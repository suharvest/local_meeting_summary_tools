"""Service for saving meeting minutes to files."""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class OutputService:
    """Service for saving meeting minutes to various formats."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize output service.

        Args:
            output_dir: Directory for output files. Defaults to ./output
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent.parent / "output"

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        speakers = set(t.get("speaker_name", "未知") for t in transcripts if t.get("speaker_name"))
        speaker_count = len(speakers)

        # Build markdown content
        md_content = f"""# {meeting.get('title') or '会议纪要'}

## 基本信息

| 项目 | 内容 |
|------|------|
| 会议室 | {meeting.get('device_name', '未知设备')} |
| 开始时间 | {start_time.strftime('%Y-%m-%d %H:%M:%S')} |
| 结束时间 | {end_time.strftime('%Y-%m-%d %H:%M:%S')} |
| 会议时长 | {duration_minutes:02d}:{duration_seconds:02d} |
| 参会人数 | {speaker_count} 人 |
| 转录条数 | {len(transcripts)} 条 |

---

## 会议摘要

{content.get('summary', '无摘要')}

---

## 关键要点

{content.get('key_points', '无关键要点')}

---

## 待办事项

{content.get('action_items', '无待办事项')}

---

## 会议记录

"""
        # Add transcript records
        for t in transcripts:
            timestamp = t.get("device_time", 0)
            time_str = datetime.fromtimestamp(timestamp / 1000).strftime("%H:%M:%S")
            speaker = t.get("speaker_name", "未知")
            text = t.get("text", "").strip()
            if text:
                md_content += f"**[{time_str}] {speaker}**: {text}\n\n"

        # Add generation metadata
        md_content += f"""---

*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
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
