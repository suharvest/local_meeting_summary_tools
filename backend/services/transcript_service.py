"""Service for querying and formatting transcript records."""
from datetime import datetime
from typing import List, Dict, Any

from ..database import Database


class TranscriptService:
    """Service for transcript record operations."""

    def __init__(self, db: Database):
        self.db = db

    async def get_transcripts(
        self,
        mac_address: str,
        start_time: int,
        end_time: int
    ) -> List[Dict[str, Any]]:
        """Get transcript records for a device within a time range.

        Args:
            mac_address: Device MAC address
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds

        Returns:
            List of transcript records ordered by device_time
        """
        query = """
            SELECT
                id,
                speaker_id,
                speaker_name,
                text,
                device_time,
                session_id
            FROM recordings
            WHERE mac_address = %s
              AND device_time >= %s
              AND device_time <= %s
            ORDER BY device_time ASC
        """
        return await self.db.fetchall(query, (mac_address, start_time, end_time))

    def format_transcript(self, transcripts: List[Dict[str, Any]]) -> str:
        """Format transcript records into a readable dialog format.

        Args:
            transcripts: List of transcript records

        Returns:
            Formatted transcript string for LLM input
        """
        if not transcripts:
            return "无转录记录"

        formatted_lines = []
        prev_speaker = None
        merged_text = []

        for record in transcripts:
            speaker = record.get("speaker_name", "未知")
            text = record.get("text", "").strip()
            timestamp = record.get("device_time", 0)

            if not text:
                continue

            # Merge consecutive messages from the same speaker
            if speaker == prev_speaker:
                merged_text.append(text)
            else:
                # Output previous speaker's merged content
                if prev_speaker and merged_text:
                    formatted_lines.append(f"{prev_speaker}: {' '.join(merged_text)}")

                prev_speaker = speaker
                merged_text = [text]

        # Don't forget the last speaker
        if prev_speaker and merged_text:
            formatted_lines.append(f"{prev_speaker}: {' '.join(merged_text)}")

        return "\n\n".join(formatted_lines)

    def format_transcript_with_time(self, transcripts: List[Dict[str, Any]]) -> str:
        """Format transcript records with timestamps.

        Args:
            transcripts: List of transcript records

        Returns:
            Formatted transcript string with timestamps
        """
        if not transcripts:
            return "无转录记录"

        formatted_lines = []

        for record in transcripts:
            speaker = record.get("speaker_name", "未知")
            text = record.get("text", "").strip()
            timestamp = record.get("device_time", 0)

            if not text:
                continue

            # Convert millisecond timestamp to time string
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
            formatted_lines.append(f"[{time_str}] {speaker}: {text}")

        return "\n".join(formatted_lines)

    async def get_speakers(
        self,
        mac_address: str,
        start_time: int,
        end_time: int
    ) -> List[str]:
        """Get unique speaker names from transcripts.

        Args:
            mac_address: Device MAC address
            start_time: Start timestamp in milliseconds
            end_time: End timestamp in milliseconds

        Returns:
            List of unique speaker names
        """
        query = """
            SELECT DISTINCT speaker_name
            FROM recordings
            WHERE mac_address = %s
              AND device_time >= %s
              AND device_time <= %s
              AND speaker_name IS NOT NULL
              AND speaker_name != ''
            ORDER BY speaker_name
        """
        results = await self.db.fetchall(query, (mac_address, start_time, end_time))
        return [r["speaker_name"] for r in results]
