import pysrt
from pathlib import Path
from datetime import timedelta
from typing import Dict, List

class SubtitleGenerator:
    def __init__(self, output_dir: Path):
        """Initialize the subtitle generator with output directory."""
        self.output_dir = output_dir

    def _create_timestamp(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format."""
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = int(td.total_seconds() % 60)
        milliseconds = int((td.total_seconds() * 1000) % 1000)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def generate_subtitles(self, data: Dict, output_file: str) -> Path:
        """Generate SRT subtitle file from transcription/simplification data."""
        subs = pysrt.SubRipFile()
        
        for i, line in enumerate(data["lines"], 1):
            start_time = self._create_timestamp(line["start_time"])
            end_time = self._create_timestamp(line["end_time"])
            text = line["text"]
            
            sub = pysrt.SubRipItem(
                index=i,
                start=pysrt.SubRipTime.from_string(start_time),
                end=pysrt.SubRipTime.from_string(end_time),
                text=text
            )
            subs.append(sub)
        
        output_path = self.output_dir / output_file
        subs.save(str(output_path), encoding='utf-8')
        return output_path 