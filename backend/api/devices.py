"""Device management API endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..database import Database, get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/devices", tags=["devices"])
limiter = Limiter(key_func=get_remote_address)


@router.get("")
@limiter.limit("60/minute")
async def list_devices(request: Request, db: Database = Depends(get_db)):
    """Get list of all devices with recording counts.

    Returns:
        List of device information including display name and recording count
    """
    query = """
        SELECT
            d.mac_address,
            d.name,
            IFNULL(NULLIF(d.name, ''), d.mac_address) as display_name,
            d.ip_address,
            d.version,
            COUNT(r.id) as recording_count
        FROM devices d
        LEFT JOIN recordings r ON d.mac_address = r.mac_address
        GROUP BY d.mac_address, d.name, d.ip_address, d.version
        ORDER BY recording_count DESC
    """
    try:
        devices = await db.fetchall(query)
    except Exception as e:
        logger.error(f"Database error while listing devices: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    return {
        "code": 200,
        "data": devices
    }


@router.get("/{mac_address}")
@limiter.limit("60/minute")
async def get_device(request: Request, mac_address: str, db: Database = Depends(get_db)):
    """Get detailed information about a specific device.

    Args:
        mac_address: Device MAC address

    Returns:
        Device details with recent recording statistics
    """
    try:
        # Get device info
        device_query = """
            SELECT
                d.mac_address,
                d.name,
                IFNULL(NULLIF(d.name, ''), d.mac_address) as display_name,
                d.ip_address,
                d.version,
                d.created_at,
                d.updated_at
            FROM devices d
            WHERE d.mac_address = %s
        """
        device = await db.fetchone(device_query, (mac_address,))

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        # Get recording statistics
        stats_query = """
            SELECT
                COUNT(*) as total_recordings,
                COUNT(DISTINCT DATE(FROM_UNIXTIME(device_time/1000))) as recording_days,
                MIN(device_time) as first_recording,
                MAX(device_time) as last_recording
            FROM recordings
            WHERE mac_address = %s
        """
        stats = await db.fetchone(stats_query, (mac_address,))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error while fetching device {mac_address}: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    return {
        "code": 200,
        "data": {
            **device,
            "statistics": stats
        }
    }


@router.get("/{mac_address}/recent")
@limiter.limit("60/minute")
async def get_recent_recordings(
    request: Request,
    mac_address: str,
    limit: int = 20,
    db: Database = Depends(get_db)
):
    """Get recent recordings from a specific device.

    Args:
        mac_address: Device MAC address
        limit: Maximum number of records to return (max 100)

    Returns:
        List of recent recording transcripts
    """
    # Enforce maximum limit to prevent resource exhaustion
    limit = min(max(1, limit), 100)

    query = """
        SELECT
            id,
            speaker_name,
            text,
            device_time,
            session_id
        FROM recordings
        WHERE mac_address = %s
        ORDER BY device_time DESC
        LIMIT %s
    """
    try:
        recordings = await db.fetchall(query, (mac_address, limit))
    except Exception as e:
        logger.error(f"Database error while fetching recordings for {mac_address}: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    return {
        "code": 200,
        "data": recordings
    }
