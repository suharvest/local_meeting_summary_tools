"""Service for saving meeting minutes to files."""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class OutputService:
    """Service for saving meeting minutes to various formats."""

    # Language-specific translations
    TRANSLATIONS = {
        "en": {
            "meeting_minutes": "Meeting Minutes",
            "basic_info": "Basic Information",
            "table_header_item": "Item",
            "table_header_content": "Content",
            "meeting_room": "Meeting Room",
            "start_time": "Start Time",
            "end_time": "End Time",
            "duration": "Duration",
            "participants": "Participants",
            "transcript_count": "Transcript Count",
            "meeting_summary": "Meeting Summary",
            "key_points": "Key Points",
            "action_items": "Action Items",
            "meeting_records": "Meeting Records",
            "no_summary": "No summary",
            "no_key_points": "No key points",
            "no_action_items": "No action items",
            "unknown_device": "Unknown Device",
            "unknown_speaker": "Unknown",
            "people": "people",
            "items": "items",
            "generated_at": "Generated at"
        },
        "zh": {
            "meeting_minutes": "会议纪要",
            "basic_info": "基本信息",
            "table_header_item": "项目",
            "table_header_content": "内容",
            "meeting_room": "会议室",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "duration": "会议时长",
            "participants": "参会人数",
            "transcript_count": "转录条数",
            "meeting_summary": "会议摘要",
            "key_points": "关键要点",
            "action_items": "待办事项",
            "meeting_records": "会议记录",
            "no_summary": "无摘要",
            "no_key_points": "无关键要点",
            "no_action_items": "无待办事项",
            "unknown_device": "未知设备",
            "unknown_speaker": "未知",
            "people": "人",
            "items": "条",
            "generated_at": "生成时间"
        }
    }

    def __init__(self, output_dir: Optional[str] = None, language: str = "en"):
        """Initialize output service.

        Args:
            output_dir: Directory for output files. Defaults to ./output
            language: Language code (en, zh). Defaults to en
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent.parent / "output"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set language
        self.language = language if language in self.TRANSLATIONS else "en"

    def _t(self, key: str) -> str:
        """Get translation for a key.

        Args:
            key: Translation key

        Returns:
            Translated string
        """
        return self.TRANSLATIONS.get(self.language, self.TRANSLATIONS["en"]).get(key, key)

    def save_markdown(
        self,
        meeting: Dict[str, Any],
        content: Dict[str, str],
        transcripts: List[Dict[str, Any]]
    ) -> str:
        """Save meeting minutes as a Markdown file.

        Args:
            meeting: Meeting information dict
            content: Generated content dict with keys: summary, key_points, action_items
            transcripts: List of transcript records

        Returns:
            Path to the saved file
        """
        filename = f"{meeting['meeting_id']}.md"
        filepath = self.output_dir / filename

        # Format timestamps
        start_time = datetime.fromtimestamp(meeting["start_time"] / 1000)
        end_time = datetime.fromtimestamp(meeting["end_time"] / 1000)
        duration_minutes = meeting.get("duration_seconds", 0) // 60
        duration_seconds = meeting.get("duration_seconds", 0) % 60

        # Get unique speakers
        speakers = set(t.get("speaker_name", self._t("unknown_speaker")) for t in transcripts if t.get("speaker_name"))
        speaker_count = len(speakers)

        # Build markdown content
        md_content = f"""# {meeting.get('title') or self._t('meeting_minutes')}

## {self._t('basic_info')}

| {self._t('table_header_item')} | {self._t('table_header_content')} |
|------|------|
| {self._t('meeting_room')} | {meeting.get('device_name', self._t('unknown_device'))} |
| {self._t('start_time')} | {start_time.strftime('%Y-%m-%d %H:%M:%S')} |
| {self._t('end_time')} | {end_time.strftime('%Y-%m-%d %H:%M:%S')} |
| {self._t('duration')} | {duration_minutes:02d}:{duration_seconds:02d} |
| {self._t('participants')} | {speaker_count} {self._t('people')} |
| {self._t('transcript_count')} | {len(transcripts)} {self._t('items')} |

---

## {self._t('meeting_summary')}

{content.get('summary', self._t('no_summary'))}

---

## {self._t('key_points')}

{content.get('key_points', self._t('no_key_points'))}

---

## {self._t('action_items')}

{content.get('action_items', self._t('no_action_items'))}

---

## {self._t('meeting_records')}

"""
        # Add transcript records
        for t in transcripts:
            timestamp = t.get("device_time", 0)
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
            speaker = t.get("speaker_name", self._t("unknown_speaker"))
            text = t.get("text", "").strip()
            if text:
                md_content += f"**[{time_str}] {speaker}**: {text}\n\n"

        # Add generation metadata
        md_content += f"""---

*{self._t('generated_at')}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        return str(filepath)

    def get_output_path(self, meeting_id: str, format: str = "md") -> str:
        """Get the expected output file path for a meeting.

        Args:
            meeting_id: Meeting ID
            format: File format (md, json)

        Returns:
            Expected file path
        """
        return str(self.output_dir / f"{meeting_id}.{format}")

    def list_outputs(self) -> List[Dict[str, Any]]:
        """List all saved meeting minutes files.

        Returns:
            List of file info dicts
        """
        files = []
        for f in self.output_dir.glob("*.md"):
            stat = f.stat()
            files.append({
                "filename": f.name,
                "path": str(f),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return sorted(files, key=lambda x: x["modified"], reverse=True)
