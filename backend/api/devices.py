"""Device management API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from ..database import Database, get_db

router = APIRouter(prefix="/api/devices", tags=["devices"])


@router.get("")
async def list_devices(db: Database = Depends(get_db)):
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
    devices = await db.fetchall(query)

    return {
        "code": 200,
        "data": devices
    }


@router.get("/{mac_address}")
async def get_device(mac_address: str, db: Database = Depends(get_db)):
    """Get detailed information about a specific device.

    Args:
        mac_address: Device MAC address

    Returns:
        Device details with recent recording statistics
    """
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

    return {
        "code": 200,
        "data": {
            **device,
            "statistics": stats
        }
    }


@router.get("/{mac_address}/recent")
async def get_recent_recordings(
    mac_address: str,
    limit: int = 20,
    db: Database = Depends(get_db)
):
    """Get recent recordings from a specific device.

    Args:
        mac_address: Device MAC address
        limit: Maximum number of records to return

    Returns:
        List of recent recording transcripts
    """
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
    recordings = await db.fetchall(query, (mac_address, limit))

    return {
        "code": 200,
        "data": recordings
    }
