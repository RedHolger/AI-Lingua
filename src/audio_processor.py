import ffmpeg
import os
from pathlib import Path
from typing import List, Tuple
from config.config import (
    FFMPEG_SAMPLE_RATE,
    FFMPEG_CHANNELS,
    FFMPEG_FORMAT,
    CHUNK_DURATION,
    TEMP_DIR
)

class AudioProcessor:
    def __init__(self, input_file: str):
        """Initialize the audio processor with input file path."""
        self.input_file = Path(input_file)
        self.temp_dir = TEMP_DIR
        self._validate_input()

    def _validate_input(self):
        """Validate input file exists and is a valid media file."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        valid_extensions = {'.mp4', '.mkv', '.mp3', '.wav', '.flac'}
        if self.input_file.suffix.lower() not in valid_extensions:
            raise ValueError(f"Unsupported file format: {self.input_file.suffix}")

    def process(self) -> List[Path]:
        """Process the input file and return a list of audio segments."""
        # First convert to WAV
        wav_file = self.temp_dir / f"{self.input_file.stem}.wav"
        stream = ffmpeg.input(str(self.input_file))
        stream = ffmpeg.output(
            stream,
            str(wav_file),
            acodec='pcm_s16le',
            ac=FFMPEG_CHANNELS,
            ar=FFMPEG_SAMPLE_RATE
        )
        ffmpeg.run(stream, overwrite_output=True)

        # Then segment the WAV file
        segments = []
        duration = float(ffmpeg.probe(str(wav_file))['format']['duration'])
        num_segments = int((duration + CHUNK_DURATION - 1) // CHUNK_DURATION)

        for i in range(num_segments):
            start_time = i * CHUNK_DURATION
            segment_file = self.temp_dir / f"{self.input_file.stem}_segment_{i:03d}.wav"
            
            stream = ffmpeg.input(str(wav_file), ss=start_time, t=CHUNK_DURATION)
            stream = ffmpeg.output(
                stream,
                str(segment_file),
                acodec='pcm_s16le',
                ac=FFMPEG_CHANNELS,
                ar=FFMPEG_SAMPLE_RATE
            )
            ffmpeg.run(stream, overwrite_output=True)
            segments.append(segment_file)

        return segments 