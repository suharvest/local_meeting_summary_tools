"""Meeting management API endpoints."""
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..database import Database, get_db
from ..llm.factory import LLMFactory, get_llm_factory
from ..services.transcript_service import TranscriptService
from ..services.prompt_service import PromptService, SUPPORTED_LANGUAGES
from ..services.output_service import OutputService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/meetings", tags=["meetings"])
limiter = Limiter(key_func=get_remote_address)

# In-memory storage for active meetings
active_meetings: Dict[str, Dict[str, Any]] = {}

# Meeting cleanup configuration
MEETING_TTL_MS = 3600000  # 1 hour TTL for completed meetings


def cleanup_old_meetings():
    """Clean up completed meetings older than TTL to prevent memory leaks."""
    now = int(time.time() * 1000)
    to_remove = [
        mid for mid, m in active_meetings.items()
        if m.get("status") == "completed" and now - m.get("end_time", 0) > MEETING_TTL_MS
    ]
    for mid in to_remove:
        del active_meetings[mid]
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old meetings")


class StartMeetingRequest(BaseModel):
    """Request body for starting a meeting."""
    mac_address: str
    title: Optional[str] = None


class EndMeetingRequest(BaseModel):
    """Request body for ending a meeting."""
    meeting_id: str
    llm_provider: Optional[str] = None
    language: Optional[str] = "en"  # Language for meeting minutes (zh, en)


@router.post("/start")
@limiter.limit("30/minute")
async def start_meeting(
    request: Request,
    body: StartMeetingRequest,
    db: Database = Depends(get_db)
):
    """Start a new meeting session.

    Creates a meeting record with start time and device information.

    Args:
        body: Meeting start parameters

    Returns:
        Meeting information including meeting_id
    """
    # Clean up old meetings periodically
    cleanup_old_meetings()

    # Generate unique meeting ID
    meeting_id = f"mtg_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    start_time = int(time.time() * 1000)

    # Get device information with error handling
    try:
        device = await db.fetchone(
            "SELECT name FROM devices WHERE mac_address = %s",
            (body.mac_address,)
        )
        device_name = device["name"] if device and device["name"] else body.mac_address
    except Exception as e:
        logger.error(f"Database error while fetching device: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    meeting = {
        "meeting_id": meeting_id,
        "mac_address": body.mac_address,
        "device_name": device_name,
        "title": body.title,
        "start_time": start_time,
        "status": "in_progress"
    }

    active_meetings[meeting_id] = meeting
    logger.info(f"Meeting started: {meeting_id} for device {body.mac_address}")

    return {
        "code": 200,
        "data": meeting
    }


@router.post("/end")
@limiter.limit("30/minute")
async def end_meeting(
    request: Request,
    body: EndMeetingRequest,
    db: Database = Depends(get_db)
):
    """End an active meeting session.

    Records end time and prepares for meeting minutes generation.

    Args:
        body: Meeting end parameters

    Returns:
        Meeting information with stream URL for SSE
    """
    if body.meeting_id not in active_meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = active_meetings[body.meeting_id]
    end_time = int(time.time() * 1000)

    # Count transcript records with error handling
    try:
        count_result = await db.fetchone(
            """
            SELECT COUNT(*) as count FROM recordings
            WHERE mac_address = %s
              AND device_time >= %s
              AND device_time <= %s
            """,
            (meeting["mac_address"], meeting["start_time"], end_time)
        )
    except Exception as e:
        logger.error(f"Database error while counting transcripts: {e}")
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")

    meeting.update({
        "end_time": end_time,
        "duration_seconds": (end_time - meeting["start_time"]) // 1000,
        "transcript_count": count_result["count"] if count_result else 0,
        "status": "generating",
        "llm_provider": body.llm_provider,
        "language": body.language or "en"
    })

    logger.info(f"Meeting ended: {body.meeting_id}, transcripts: {meeting['transcript_count']}")

    return {
        "code": 200,
        "data": {
            **meeting,
            "stream_url": f"/api/meetings/{body.meeting_id}/stream"
        }
    }


@router.get("/{meeting_id}")
@limiter.limit("60/minute")
async def get_meeting(request: Request, meeting_id: str):
    """Get meeting information by ID.

    Args:
        meeting_id: Meeting ID

    Returns:
        Meeting details
    """
    if meeting_id not in active_meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return {
        "code": 200,
        "data": active_meetings[meeting_id]
    }


@router.get("/{meeting_id}/stream")
@limiter.limit("10/minute")
async def stream_meeting_minutes(
    request: Request,
    meeting_id: str,
    db: Database = Depends(get_db),
    llm_factory: LLMFactory = Depends(get_llm_factory)
):
    """Stream meeting minutes generation via Server-Sent Events.

    Generates meeting summary, key points, and action items using LLM
    and streams the output in real-time.

    Args:
        meeting_id: Meeting ID

    Returns:
        SSE stream of meeting minutes content
    """
    if meeting_id not in active_meetings:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting = active_meetings[meeting_id]

    async def generate():
        """Generator function for SSE events."""
        try:
            # Send start event
            yield f"event: start\ndata: {json.dumps({'meeting_id': meeting_id, 'status': 'loading'})}\n\n"

            # Initialize services with language
            language = meeting.get("language", "en")
            transcript_service = TranscriptService(db, language=language)
            prompt_service = PromptService(language=language)
            output_service = OutputService(language=language)

            # Get transcripts with extended time range (add 60 seconds buffer)
            extended_end_time = meeting["end_time"] + 60000  # Add 60 seconds

            transcripts = await transcript_service.get_transcripts(
                meeting["mac_address"],
                meeting["start_time"],
                extended_end_time
            )

            # If no transcripts in meeting time range, try to get recent transcripts
            if not transcripts:
                logger.info("No transcripts in meeting range, fetching recent data")
                # Get transcripts from last 5 minutes as fallback
                fallback_start = meeting["end_time"] - 300000  # 5 minutes before end
                transcripts = await transcript_service.get_transcripts(
                    meeting["mac_address"],
                    fallback_start,
                    extended_end_time
                )

            if not transcripts:
                error_messages = {
                    "en": "No transcript records found. Please ensure the device is uploading data.",
                    "zh": "无转录记录，请确保设备正在上传数据"
                }
                error_msg = error_messages.get(language, error_messages["en"])
                yield f"event: error\ndata: {json.dumps({'error': error_msg, 'code': 400})}\n\n"
                return

            logger.info(f"Found {len(transcripts)} transcripts for meeting {meeting_id}")

            # Send transcripts event
            yield f"event: transcripts\ndata: {json.dumps({'count': len(transcripts)})}\n\n"

            # Format transcript for LLM
            formatted_transcript = transcript_service.format_transcript(transcripts)

            # Get LLM provider
            provider_name = meeting.get("llm_provider")
            provider = llm_factory.get_provider(provider_name)
            actual_model = provider.get_model_name()
            actual_provider = provider_name or llm_factory.default_provider

            # Send model info event
            yield f"event: model_info\ndata: {json.dumps({'provider': actual_provider, 'model': actual_model, 'language': language})}\n\n"

            # Language instruction to append to system prompts
            language_instructions = {
                "zh": "请用中文回答。",
                "en": "Please respond in English."
            }
            language_instruction = language_instructions.get(language, language_instructions["en"])

            # Define generation stages with language-specific titles
            stage_titles = {
                "zh": {"summary": "会议摘要", "key_points": "关键要点", "action_items": "待办事项"},
                "en": {"summary": "Meeting Summary", "key_points": "Key Points", "action_items": "Action Items"}
            }
            titles = stage_titles.get(language, stage_titles["en"])

            stages = [
                ("summary", "meeting_summary.txt", titles["summary"]),
                ("key_points", "key_points.txt", titles["key_points"]),
                ("action_items", "action_items.txt", titles["action_items"]),
            ]

            full_content = {}

            for stage_name, prompt_file, stage_title in stages:
                # Send stage start event
                yield f"event: stage_start\ndata: {json.dumps({'stage': stage_name, 'title': stage_title})}\n\n"

                # Load system prompt and append language instruction
                base_prompt = prompt_service.load_prompt(prompt_file)
                system_prompt = f"{base_prompt}\n\n{language_instruction}"

                # Stream generate content
                full_text = ""
                async for chunk in provider.stream_generate(
                    prompt=formatted_transcript,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=2048
                ):
                    full_text += chunk
                    yield f"event: content\ndata: {json.dumps({'stage': stage_name, 'content': chunk})}\n\n"
                    await asyncio.sleep(0.01)  # Control streaming rate

                full_content[stage_name] = full_text

                # Send stage complete event
                yield f"event: stage_complete\ndata: {json.dumps({'stage': stage_name, 'full_content': full_text})}\n\n"

            # Save meeting minutes to file
            output_path = output_service.save_markdown(meeting, full_content, transcripts)

            # Update meeting status
            meeting["status"] = "completed"
            meeting["file_path"] = output_path
            meeting["content"] = full_content

            # Send complete event
            yield f"event: complete\ndata: {json.dumps({'meeting_id': meeting_id, 'file_path': output_path, 'status': 'completed'})}\n\n"

        except Exception as e:
            logger.error(f"Error generating meeting minutes for {meeting_id}: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': 'Internal server error', 'code': 500})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.get("")
@limiter.limit("60/minute")
async def list_meetings(request: Request):
    """List all active meetings.

    Returns:
        List of active meeting information
    """
    # Clean up old meetings before listing
    cleanup_old_meetings()

    meetings = list(active_meetings.values())
    return {
        "code": 200,
        "data": sorted(meetings, key=lambda x: x.get("start_time", 0), reverse=True)
    }


@router.get("/config/languages")
@limiter.limit("60/minute")
async def get_supported_languages(request: Request):
    """Get list of supported languages for meeting minutes.

    Returns:
        List of supported language codes and names
    """
    languages = [
        {"code": code, "name": name}
        for code, name in SUPPORTED_LANGUAGES.items()
    ]
    return {
        "code": 200,
        "data": languages
    }
