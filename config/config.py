import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
TEMP_DIR = PROJECT_ROOT / "data" / "temp"

# Create directories if they don't exist
for directory in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"  # Updated to use the latest stable model

# FFmpeg Configuration
FFMPEG_SAMPLE_RATE = 44100
FFMPEG_CHANNELS = 1
FFMPEG_FORMAT = "wav"

# MPV Configuration
MPV_CONFIG = {
    "sub-auto": "fuzzy",
    "sub-font-size": "45",
    "sub-pos": "95",
    "secondary-sub-pos": "5",
    "loop-file": "inf"
}

# Transcription Configuration
CHUNK_DURATION = 30  # seconds - increased to reduce number of API calls
MAX_RETRIES = 3
TIMEOUT = 60
RATE_LIMIT_DELAY = 3  # seconds between API calls to respect rate limits
 