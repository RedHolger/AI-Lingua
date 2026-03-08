# Research Code Analysis: Lingua System

## Executive Summary

The **Lingua** system is a research-grade language learning platform that demonstrates advanced AI integration, microservices architecture, and educational content generation. This document provides a comprehensive analysis of the codebase and instructions for running it on the TED-LIUM corpus for research purposes.

---

## System Architecture

### High-Level Overview

```
┌─────────────────┐         ┌──────────────────┐
│  Input Media    │         │  TED-LIUM Corpus │
│  (Video/Audio)  │         │  (.sph + .stm)   │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         ▼                           ▼
┌─────────────────────────────────────────┐
│      MediaService (Java)                 │
│  - Extract embedded subtitles (FFmpeg)  │
│  - Parse STM files → SRT                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      SrtUtil (Java)                      │
│  - Parse SRT files                       │
│  - Strip HTML tags                       │
│  - Format time codes                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ProcessingController (Java)             │
│  - Batch processing (100 lines/chunk)   │
│  - Scene segmentation                   │
│  - Orchestrate workflow                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      AI Service (Python FastAPI)        │
│  - Text simplification (Gemini 2.5)    │
│  - Language analysis                    │
│  - Educational content generation       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Output Files                        │
│  - simplified.srt                       │
│  - previews.srt                         │
│  - recaps.srt                           │
│  - quizzes.json                         │
└─────────────────────────────────────────┘
```

### Key Components

#### 1. **Python AI Service** (`src/ai_service.py`)
- **Technology**: FastAPI, Google Gemini 2.5 Flash
- **Endpoints**:
  - `/simplify` - CEFR-level text simplification
  - `/analyze_language` - Vocabulary/grammar extraction
  - `/generate_previews` - Scene previews
  - `/generate_recaps` - Vocabulary recaps
  - `/generate_quizzes` - Quiz generation
- **Features**:
  - HMAC-SHA256 signature verification
  - Async processing
  - Error handling with retries

#### 2. **Java Spring Boot Service** (`java/lingua-app/`)
- **Technology**: Spring Boot 3.3.3, Java 21
- **Components**:
  - `ProcessingController` - Main REST API
  - `MediaService` - FFmpeg integration
  - `SceneService` - Content segmentation
  - `EducationalService` - Educational content
  - `SrtUtil` - Subtitle utilities
- **Features**:
  - Batch processing (100 lines)
  - Path resolution (cross-platform)
  - Error resilience

#### 3. **Transcription Module** (`src/transcriber.py`)
- **Purpose**: Audio transcription using Gemini
- **Features**:
  - Base64 audio encoding
  - JSON response parsing
  - Retry logic with exponential backoff
  - Rate limiting

---

## Research Capabilities

### 1. **Text Simplification**
- **Input**: Original subtitles (human-generated)
- **Output**: Simplified subtitles at CEFR levels (A1-C2)
- **Method**: Prompt engineering with Gemini 2.5 Flash
- **Research Question**: Can LLMs maintain semantic fidelity while reducing complexity?

### 2. **Language Analysis**
- **Extracts**:
  - Vocabulary frequency
  - Grammar patterns (questions, negation, tenses)
  - Noun identification
- **Use Case**: Analyze linguistic features of educational content

### 3. **Scene Segmentation**
- **Algorithm**: Gap-based segmentation
- **Threshold**: Configurable (default 3.0 seconds)
- **Output**: Natural learning segments

### 4. **Educational Content Generation**
- **Previews**: Key words/phrases before scenes
- **Recaps**: Vocabulary/grammar summaries
- **Quizzes**: Multiple-choice questions

---

## Running on TED-LIUM Corpus

### Quick Start

1. **Download TED-LIUM v3**
   ```bash
   # Visit https://www.openslr.org/51/
   # Download and extract
   tar -xzf TEDLIUM_release-3.tgz
   ```

2. **Convert Audio Files** (if needed)
   ```bash
   # Install sox: brew install sox (macOS) or apt-get install sox (Linux)
   find tedlium/ -name "*.sph" -exec sh -c \
     'sph2pipe -f wav "$1" "${1%.sph}.wav"' _ {} \;
   ```

3. **Convert STM to SRT**
   ```bash
   python scripts/stm_to_srt.py \
     tedlium/test/stm/talk1.stm \
     data/input/talk1.srt
   ```

4. **Start Services**
   ```bash
   # Terminal 1: Python AI service
   source venv/bin/activate
   PYTHONPATH=.:src uvicorn src.ai_service:app --port 8001
   
   # Terminal 2: Java service
   cd java/lingua-app
   mvn spring-boot:run -Dai.service.url=http://localhost:8001
   ```

5. **Process Single Talk**
   ```bash
   curl -X POST http://localhost:8080/api/process \
     -H "Content-Type: application/json" \
     -d '{
       "officialSrt": "data/input/talk1.srt",
       "useEmbedded": false,
       "generatePreviews": true,
       "generateRecaps": true,
       "learnerLevel": "A1"
     }'
   ```

6. **Batch Process Entire Corpus**
   ```bash
   # Edit scripts/process_tedlium_batch.py to set TEDLIUM_ROOT
   python scripts/process_tedlium_batch.py
   ```

### Expected Processing Time

- **Single talk** (5-10 minutes): ~2-5 minutes
- **100 talks**: ~3-8 hours (depending on API rate limits)
- **Full corpus** (2,351 talks): ~2-3 days

---

## Research Metrics

### Semantic Fidelity
- **BERTScore**: Compare simplified vs. original using BERT embeddings
- **Target**: >0.85 F1 score

### Readability
- **Flesch-Kincaid Grade Level**: Measure complexity reduction
- **Target**: 2-3 grade levels reduction

### Human-likeness
- **Perplexity**: Using GPT-2 to measure naturalness
- **Target**: Perplexity < 50 (lower = more natural)

### Implementation
See `TED_LIUM_GUIDE.md` for detailed evaluation scripts.

---

## Code Quality & Research Readiness

### Strengths
✅ **Modular Architecture**: Easy to extend and modify  
✅ **Error Handling**: Graceful degradation  
✅ **Batch Processing**: Handles large datasets  
✅ **Documentation**: Well-structured code  
✅ **Research Integration**: Designed for benchmarking  

### Areas for Research Enhancement
1. **Evaluation Metrics**: Add BERTScore, Perplexity scripts
2. **Statistical Analysis**: Add significance testing
3. **Visualization**: Generate comparison plots
4. **Reproducibility**: Add seed setting, version pinning

---

## Key Files for Research

| File | Purpose |
|------|---------|
| `src/ai_service.py` | AI endpoints (simplification, analysis) |
| `src/transcriber.py` | Audio transcription logic |
| `java/.../ProcessingController.java` | Main processing orchestration |
| `java/.../SrtUtil.java` | Subtitle parsing/formatting |
| `scripts/stm_to_srt.py` | TED-LIUM format conversion |
| `scripts/process_tedlium_batch.py` | Batch processing script |

---

## Research Workflow

```
1. Data Preparation
   ├── Download TED-LIUM
   ├── Convert .sph → .wav
   └── Convert .stm → .srt

2. Processing
   ├── Start services
   ├── Run batch processing
   └── Collect outputs

3. Evaluation
   ├── Compute BERTScore
   ├── Measure readability
   ├── Calculate perplexity
   └── Statistical analysis

4. Analysis
   ├── Compare metrics
   ├── Identify patterns
   ├── Generate visualizations
   └── Write research paper
```

---

## Next Steps

1. **Read**: `TED_LIUM_GUIDE.md` for detailed instructions
2. **Run**: Single talk test to verify setup
3. **Scale**: Process full corpus with batch script
4. **Evaluate**: Run evaluation metrics
5. **Analyze**: Compare results, write findings

---

## Contact & Support

For issues or questions:
- Check logs: `data/output/` and service terminals
- Review error messages in batch summary
- Verify API keys and service connectivity

---

**Last Updated**: December 2025  
**System Version**: Lingua v1.0  
**Research Status**: Ready for TED-LIUM benchmarking
