#!/bin/bash

# Exit on any error
set -e

echo "Setting up English Learning System..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install system dependencies if not present
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
fi

if ! command -v mpv &> /dev/null; then
    echo "Installing MPV..."
    sudo apt-get install -y mpv
fi

# Check for .env file and Gemini API key
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "GEMINI_API_KEY=AIzaSyC4Gl8HKK91UfuecH40i9CIVS3WPqa_2ns" > .env
fi

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/{input,output,temp}

# Check if input file exists
if [ ! -f "data/input/05. Messy.flac" ]; then
    echo "Please place your audio/video file in the data/input directory"
    echo "Expected file: data/input/05. Messy.flac"
    exit 1
fi

# Run the system
echo "Running the English Learning System..."
PYTHONPATH=$PYTHONPATH:. python src/main.py "data/input/05. Messy.flac" 