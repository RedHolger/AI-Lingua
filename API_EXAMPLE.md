# Complete API Examples for Lingua

## Processing Media File: Crayon Shin-chan

### File Path
The media file should be in the `data/input/` directory. Based on your system, use one of these paths:

**Option 1: Relative path (recommended)**
```
data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv
```

**Option 2: Absolute path**
```
/Users/manuvashistha/Documents/Lingua/data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv
```

---

## Complete API Call Examples

### 1. Basic Request (Extract Embedded Subtitles)

```bash
curl -X POST http://localhost:8080/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "mediaPath": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
    "useEmbedded": true,
    "generatePreviews": false,
    "generateRecaps": false,
    "generateQuizzes": false,
    "gapThreshold": 3.0,
    "learnerLevel": "A1"
  }'
```

### 2. Full Processing (All Features Enabled)

```bash
curl -X POST http://localhost:8080/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "mediaPath": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
    "useEmbedded": true,
    "generatePreviews": true,
    "generateRecaps": true,
    "generateQuizzes": true,
    "gapThreshold": 3.0,
    "learnerLevel": "A1"
  }'
```

### 3. Using External SRT File (If you have a separate subtitle file)

```bash
curl -X POST http://localhost:8080/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "mediaPath": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
    "useEmbedded": false,
    "officialSrt": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].srt",
    "generatePreviews": true,
    "generateRecaps": true,
    "generateQuizzes": true,
    "gapThreshold": 3.0,
    "learnerLevel": "A1"
  }'
```

### 4. Advanced Configuration (Different CEFR Level)

```bash
curl -X POST http://localhost:8080/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "mediaPath": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
    "useEmbedded": true,
    "generatePreviews": true,
    "generateRecaps": true,
    "generateQuizzes": false,
    "gapThreshold": 5.0,
    "learnerLevel": "B1"
  }'
```

---

## API Parameters Explained

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mediaPath` | string | Yes | - | Path to media file (relative to project root or absolute) |
| `useEmbedded` | boolean | No | false | Extract subtitles from embedded streams in media file |
| `officialSrt` | string | No | null | Path to external SRT file (alternative to embedded) |
| `generatePreviews` | boolean | No | false | Generate scene previews with key words/phrases |
| `generateRecaps` | boolean | No | false | Generate vocabulary/grammar recaps |
| `generateQuizzes` | boolean | No | false | Generate quiz questions |
| `gapThreshold` | number | No | 3.0 | Seconds of silence to consider as scene break |
| `learnerLevel` | string | No | "A1" | CEFR level: A1, A2, B1, B2, C1, C2 |

---

## Response Format

### Success Response

```json
{
  "originalSrt": "/Users/manuvashistha/Documents/Lingua/data/output/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv.embedded.srt",
  "simplifiedSrt": "/Users/manuvashistha/Documents/Lingua/data/output/simplified.srt",
  "previewsSrt": "/Users/manuvashistha/Documents/Lingua/data/output/previews.srt",
  "recapsSrt": "/Users/manuvashistha/Documents/Lingua/data/output/recaps.srt",
  "quizzesJson": "/Users/manuvashistha/Documents/Lingua/data/output/quizzes.json",
  "mpvConf": "/Users/manuvashistha/Documents/Lingua/data/output/playback.mpv.conf"
}
```

### Error Response

```json
{
  "timestamp": "2025-12-16T17:21:09.753+00:00",
  "status": 500,
  "error": "Internal Server Error",
  "path": "/api/process"
}
```

---

## Python Example

```python
import requests
import json

url = "http://localhost:8080/api/process"
payload = {
    "mediaPath": "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
    "useEmbedded": True,
    "generatePreviews": True,
    "generateRecaps": True,
    "generateQuizzes": True,
    "gapThreshold": 3.0,
    "learnerLevel": "A1"
}

response = requests.post(url, json=payload, timeout=600)
result = response.json()

if response.status_code == 200:
    print("Success!")
    print(f"Simplified SRT: {result['simplifiedSrt']}")
    print(f"Previews SRT: {result.get('previewsSrt', 'N/A')}")
    print(f"Recaps SRT: {result.get('recapsSrt', 'N/A')}")
else:
    print(f"Error: {result}")
```

---

## JavaScript/Node.js Example

```javascript
const axios = require('axios');

const payload = {
  mediaPath: "data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv",
  useEmbedded: true,
  generatePreviews: true,
  generateRecaps: true,
  generateQuizzes: true,
  gapThreshold: 3.0,
  learnerLevel: "A1"
};

axios.post('http://localhost:8080/api/process', payload, {
  timeout: 600000  // 10 minutes
})
  .then(response => {
    console.log('Success!', response.data);
  })
  .catch(error => {
    console.error('Error:', error.response?.data || error.message);
  });
```

---

## Important Notes

1. **File Path**: Use relative paths from project root (e.g., `data/input/file.mkv`) or absolute paths
2. **Timeout**: Processing can take 2-10 minutes for large files, set appropriate timeout
3. **Services**: Ensure both Python (port 8001) and Java (port 8080) services are running
4. **API Key**: Make sure `GEMINI_API_KEY` is set in `.env` file
5. **File Location**: Media file must exist in the specified path

---

## Quick Test Command

```bash
# Test if services are running
curl http://localhost:8080/actuator/health 2>/dev/null || echo "Java service not running"
curl http://localhost:8001/docs 2>/dev/null && echo "Python service running" || echo "Python service not running"
```

---

## Troubleshooting

### Error: "No official subtitles available"
- **Solution**: Ensure `useEmbedded: true` and media file has embedded subtitles, OR provide `officialSrt` path

### Error: "File not found"
- **Solution**: Check file path is correct (relative to project root or absolute)
- Verify file exists: `ls -lh data/input/[BuriBuri]*.mkv`

### Error: Timeout
- **Solution**: Increase timeout value, or process in smaller chunks
- Large files (1000+ subtitle entries) may take 5-10 minutes

### Error: "AI service HTTP 500"
- **Solution**: Check Python service logs, verify GEMINI_API_KEY is set correctly

