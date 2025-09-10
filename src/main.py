import argparse
from pathlib import Path
from typing import Optional
import subprocess
from tqdm import tqdm
import asyncio

from config.config import INPUT_DIR, OUTPUT_DIR, MPV_CONFIG
from audio_processor import AudioProcessor
from transcriber import Transcriber
from subtitle_generator import SubtitleGenerator

def create_mpv_config(config_path: Path):
    """Create MPV configuration file."""
    config_content = "\n".join(f"{k}={v}" for k, v in MPV_CONFIG.items())
    config_path.write_text(config_content)

def play_with_mpv(video_path: Path, original_srt: Path, simplified_srt: Path, mpv_config: Optional[Path] = None):
    """Play the video with MPV and subtitles."""
    cmd = ["mpv"]
    
    if mpv_config and mpv_config.exists():
        cmd.extend(["--config-file", str(mpv_config)])
    
    cmd.extend([
        str(video_path),
        f"--sub-file={original_srt}",
        f"--secondary-sub-file={simplified_srt}"
    ])
    
    subprocess.run(cmd)

async def process_video(input_path: Path, play: bool = True):
    """Process a video file to generate subtitles."""
    print(f"Processing: {input_path}")
    
    # Extract and segment audio
    print("Extracting and segmenting audio...")
    processor = AudioProcessor(str(input_path))
    segments = processor.process()
    
    # Transcribe and simplify
    print("Transcribing and simplifying lyrics...")
    transcriber = Transcriber()
    transcription, simplification = await transcriber.process_segments(segments)
    
    # Generate subtitle files
    print("Generating subtitles...")
    subtitle_gen = SubtitleGenerator(OUTPUT_DIR)
    original_srt = subtitle_gen.generate_subtitles(transcription, input_path.stem + ".original.srt")
    simplified_srt = subtitle_gen.generate_subtitles(simplification, input_path.stem + ".simplified.srt")
    
    # Play the video if requested
    if play:
        config_path = OUTPUT_DIR / "mpv.conf"
        create_mpv_config(config_path)
        play_with_mpv(input_path, original_srt, simplified_srt, config_path)

async def main():
    parser = argparse.ArgumentParser(description="Process video/audio files for language learning")
    parser.add_argument("input", type=str, help="Input video/audio file")
    parser.add_argument("--no-play", action="store_true", help="Don't play the video after processing")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        input_path = INPUT_DIR / args.input
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {args.input}")
    
    await process_video(input_path, not args.no_play)

if __name__ == "__main__":
    asyncio.run(main()) 