#!/bin/bash

set -e

echo "Setting up English Learning System..."

# -----------------------
# CONFIG
# -----------------------
AI_PORT=8001
JAVA_PORT=8080

# -----------------------
# Python environment
# -----------------------
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

# -----------------------
# System dependencies
# -----------------------
if ! command -v ffmpeg &>/dev/null; then
  echo "FFmpeg not found. macOS: brew install ffmpeg"
fi

if ! command -v mpv &>/dev/null; then
  echo "MPV not found. macOS: brew install mpv"
fi

# -----------------------
# Environment variables
# -----------------------
if [ ! -f ".env" ]; then
  echo "Creating .env file..."
  echo "GEMINI_API_KEY=your_api_key_here" >.env
fi

# -----------------------
# Data directories
# -----------------------
echo "Creating data directories..."
mkdir -p data/{input,output,temp}

# -----------------------
# Input file resolution
# -----------------------
INPUT_FILE="$1"
if [ -z "$INPUT_FILE" ]; then
  INPUT_FILE=$(ls -1 data/input/*.{mp4,mkv,mp3,wav,flac} 2>/dev/null | head -n 1)
fi

if [ -z "$INPUT_FILE" ] || [ ! -f "$INPUT_FILE" ]; then
  echo "No input media found."
  echo "Place a file in data/input or pass a path as argument."
  exit 1
fi

# -----------------------
# Start FastAPI safely
# -----------------------
if lsof -i :$AI_PORT &>/dev/null; then
  echo "FastAPI already running on port $AI_PORT"
else
  echo "Starting AI service (FastAPI) on port $AI_PORT..."
  PYTHONPATH=.:src uvicorn src.ai_service:app \
    --host 0.0.0.0 \
    --port $AI_PORT \
    --log-level info &
fi

# -----------------------
# Start Spring Boot
# -----------------------
echo "Starting Java Spring Boot service on port $JAVA_PORT..."
cd java/lingua-app
mvn -q -DskipTests spring-boot:run
