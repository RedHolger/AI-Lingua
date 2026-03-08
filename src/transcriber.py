import google.generativeai as genai
from pathlib import Path
from typing import Dict, List
import json
import base64
from config.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_RETRIES, TIMEOUT, RATE_LIMIT_DELAY
from time import sleep

class Transcriber:
    def __init__(self):
        """Initialize the Gemini API client."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def _create_transcription_prompt(self) -> str:
        """Create the prompt for song transcription."""
        return """
        Please transcribe this audio segment and provide the output in the following JSON format:
        {
            "lines": [
                {
                    "start_time": float,  // Start time in seconds
                    "end_time": float,    // End time in seconds
                    "text": string        // The transcribed text
                }
            ]
        }
        Only return the JSON object, no other text.
        """

    def _create_simplification_prompt(self, transcription: Dict, level: str = "A1") -> str:
        """Create the prompt for text simplification."""
        lines = [line["text"] for line in transcription["lines"]]
        text = "\n".join(lines)
        
        return f"""
        Please simplify the following text to make it suitable for a language learner at CEFR level {level}.
        Keep the meaning but use simpler vocabulary and grammar appropriate for {level}.
        
        Text to simplify:
        {text}
        
        Return the simplified version in the same JSON format:
        {{
            "lines": [
                {{
                    "start_time": float,  // Use the same timestamps as the original
                    "end_time": float,
                    "text": string        // The simplified text
                }}
            ]
        }}
        Only return the JSON object, no other text.
        """

    async def transcribe_segment(self, audio_file: Path) -> Dict:
        """Transcribe an audio segment using Gemini."""
        retries = MAX_RETRIES
        while retries > 0:
            try:
                with open(audio_file, 'rb') as f:
                    audio_data = f.read()
                
                # Convert audio data to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                response = self.model.generate_content(
                    [
                        {"text": self._create_transcription_prompt()},
                        {"inline_data": {
                            "mime_type": "audio/wav",
                            "data": audio_base64
                        }}
                    ],
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "top_k": 40
                    }
                )
                
                # Extract JSON from response
                try:
                    # First try to parse the response text directly
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from the text
                    text = response.text.strip()
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = text[start:end]
                        return json.loads(json_str)
                    raise ValueError("No valid JSON found in response")
                    
            except Exception as e:
                print(f"Attempt {MAX_RETRIES - retries + 1} failed: {e}")
                retries -= 1
                if retries > 0:
                    # Check if it's a rate limit error and wait longer
                    if "429" in str(e) or "quota" in str(e).lower():
                        print(f"Rate limit hit, waiting {RATE_LIMIT_DELAY * 2} seconds...")
                        sleep(RATE_LIMIT_DELAY * 2)
                    else:
                        sleep(TIMEOUT / MAX_RETRIES)
                else:
                    raise RuntimeError(f"Failed to transcribe after {MAX_RETRIES} attempts: {e}")

    async def simplify_text(self, transcription: Dict, level: str = "A1") -> Dict:
        """Simplify the transcribed text using Gemini."""
        retries = MAX_RETRIES
        while retries > 0:
            try:
                response = self.model.generate_content(
                    [{"text": self._create_simplification_prompt(transcription, level=level)}],
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.8,
                        "top_k": 40
                    }
                )
                
                # Extract JSON from response
                try:
                    # First try to parse the response text directly
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    # If that fails, try to extract JSON from the text
                    text = response.text.strip()
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = text[start:end]
                        return json.loads(json_str)
                    raise ValueError("No valid JSON found in response")
                    
            except Exception as e:
                print(f"Attempt {MAX_RETRIES - retries + 1} failed: {e}")
                retries -= 1
                if retries > 0:
                    # Check if it's a rate limit error and wait longer
                    if "429" in str(e) or "quota" in str(e).lower():
                        print(f"Rate limit hit, waiting {RATE_LIMIT_DELAY * 2} seconds...")
                        sleep(RATE_LIMIT_DELAY * 2)
                    else:
                        sleep(TIMEOUT / MAX_RETRIES)
                else:
                    raise RuntimeError(f"Failed to simplify after {MAX_RETRIES} attempts: {e}")

    async def process_segments(self, segments: List[Path]) -> tuple[Dict, Dict]:
        """Process multiple audio segments and combine the results."""
        all_transcriptions = {"lines": []}
        all_simplifications = {"lines": []}
        
        for i, segment in enumerate(segments):
            print(f"Processing segment {i+1}/{len(segments)}: {segment.name}")
            
            # Add delay between API calls to respect rate limits
            if i > 0:
                print(f"Waiting {RATE_LIMIT_DELAY} seconds between API calls...")
                sleep(RATE_LIMIT_DELAY)
            
            trans_result = await self.transcribe_segment(segment)
            simp_result = await self.simplify_text(trans_result)
            
            all_transcriptions["lines"].extend(trans_result["lines"])
            all_simplifications["lines"].extend(simp_result["lines"])
        
        return all_transcriptions, all_simplifications

    def adjust_segment_timing(self, segments_data, audio_duration):
        """Adjust segment timing to better match audio duration."""
        total_segments = len(segments_data["lines"])
        if total_segments == 0:
            return segments_data

        # Calculate time per segment
        time_per_segment = audio_duration / total_segments

        adjusted_lines = []
        for i, line in enumerate(segments_data["lines"]):
            start_time = i * time_per_segment
            end_time = min((i + 1) * time_per_segment, audio_duration)

            adjusted_lines.append({
                "start_time": start_time,
                "end_time": end_time,
                "text": line["text"]
            })

        return {"lines": adjusted_lines} 
