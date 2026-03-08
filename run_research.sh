#!/bin/bash
export PYTHONPATH=.:src
export GEMINI_API_KEY=${GEMINI_API_KEY}

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Warning: GEMINI_API_KEY is not set. Please export it or edit this script."
    exit 1
fi

if [ ! -d ".venv_research" ]; then
    echo "Creating research virtual environment..."
    python3 -m venv .venv_research
fi

# Always ensure dependencies are installed/updated
echo "Installing/Updating dependencies..."
.venv_research/bin/pip install -r research/requirements.txt

# Configure NLTK to use a local directory
export NLTK_DATA=$(pwd)/.nltk_data
mkdir -p $NLTK_DATA
echo "NLTK_DATA set to $NLTK_DATA"

echo "Running benchmark..."
.venv_research/bin/python3 research/runner.py
