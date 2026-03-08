# Lingua: Media-Driven Language Learning

Lingua processes video/audio with official or embedded subtitles to generate:
- `simplified.srt` aligned to CEFR levels
- `previews.srt` showing upcoming context (words, phrases)
- `recaps.srt` summarizing grammar and vocabulary after scenes
- `quizzes.json` calibrated items
- `playback.mpv.conf` for MPV player overlay settings

## Prerequisites
- macOS with `ffmpeg` and `mpv` installed (Homebrew: `brew install ffmpeg mpv`)
- Python 3.10+ and Java 17+
- Maven (or add Maven Wrapper)
- Environment:
  - `GEMINI_API_KEY` for the Python AI service
  - Optional: `AI_HMAC_SECRET` for HMAC signing Java→Python calls

## Quick Start
1. Place a media file in `data/input` (e.g., `data/input/my_episode.mkv`).
2. Start services:
   - Python AI service: `PYTHONPATH=.:src uvicorn src.ai_service:app --host 0.0.0.0 --port 8001`
   - Java service: `cd java/lingua-app && mvn spring-boot:run -Dai.service.url=http://localhost:8001`
3. Process via REST:
   ```
   POST http://localhost:8080/api/process
   {
     "mediaPath": "data/input/my_episode.mkv",
     "useEmbedded": true,
     "generatePreviews": true,
     "generateRecaps": true,
     "generateQuizzes": true,
     "gapThreshold": 3.0,
     "learnerLevel": "A1"
   }
   ```
4. Outputs will appear in `data/output/`.

## Run Script
Use `./run_system.sh [optional_path]`:
- Creates venv, installs Python deps, starts FastAPI on `8001`
- Starts Spring Boot on `8080`
- Auto-detects first media file if no path given

## Configuration
- Java AI URL: `-Dai.service.url=http://localhost:8001`
- HMAC secret: `-Dai.hmac.secret=$AI_HMAC_SECRET` or env var `AI_HMAC_SECRET`
- Learner level per request: `"learnerLevel": "A1" | "A2" | ...`

## Research & Benchmarking
Lingua includes a research workflow for benchmarking CEFR-level simplification on LibriSpeech using local transcripts and audio.
- Metrics: BERTScore (semantic fidelity), Flesch–Kincaid (readability), and perplexity (fluency).
- Use the research runner to evaluate small subsets and aggregate results to JSON for analysis.

## Troubleshooting
- Maven not found: install Maven or add mvnw wrapper.
- Port conflicts: ensure `8001` (AI) and `8080` (Java) are free; update ports if needed.
- `ModuleNotFoundError: transcriber`: run with `PYTHONPATH=.:src` or start via `run_system.sh`.
- FFmpeg errors: verify `ffprobe`/`ffmpeg` are installed; check console logs for stream mapping.

## Architecture Notes
- Java orchestrates processing and I/O; Python handles AI-heavy tasks via FastAPI.
- Endpoints implemented in `src/ai_service.py`: `/simplify`, `/analyze_language`, `/generate_previews`, `/generate_recaps`, `/generate_quizzes`.
- HMAC-SHA256 signing is supported for secure inter-service requests.
