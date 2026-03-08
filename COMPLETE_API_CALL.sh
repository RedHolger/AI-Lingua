#!/bin/bash
# Complete API call for Crayon Shin-chan media file
# Make sure services are running on ports 8001 (Python) and 8080 (Java)

# Configuration
API_URL="http://localhost:8080/api/process"
MEDIA_FILE="data/input/[BuriBuri] Crayon Shin-chan - 0001 [DVD][19B1AC2B].mkv"

# Full processing with all features
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"mediaPath\": \"$MEDIA_FILE\",
    \"useEmbedded\": true,
    \"generatePreviews\": true,
    \"generateRecaps\": true,
    \"generateQuizzes\": true,
    \"gapThreshold\": 3.0,
    \"learnerLevel\": \"A1\"
  }" \
  --max-time 1200 \
  -w "\n\nHTTP Status: %{http_code}\nTime: %{time_total}s\n" \
  | python3 -m json.tool

