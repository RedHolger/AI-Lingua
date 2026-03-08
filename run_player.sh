#!/bin/bash
export PYTHONPATH=.:src
export GEMINI_API_KEY=${GEMINI_API_KEY}

PYTHON_BIN=python3
if command -v python3.11 >/dev/null 2>&1; then
    PYTHON_BIN=python3.11
fi

if [ -z "$1" ]; then
    echo "Usage: ./run_player.sh <path_to_video>"
    exit 1
fi

if [ ! -d ".venv_player" ]; then
    echo "Creating virtual environment with ${PYTHON_BIN}..."
    "$PYTHON_BIN" -m venv .venv_player
    .venv_player/bin/pip install -r requirements_player.txt
fi

export LC_NUMERIC=C

echo "Starting Lingua CLI player for $1..."
.venv_player/bin/python3 src/lingua_player.py "$1"
