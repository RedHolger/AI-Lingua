
import os
import google.generativeai as genai
from typing import List, Dict, Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_scene(self, subtitles: str) -> str:
        prompt = f"""
        Analyze the following subtitles from a video scene.
        Identify the main characters, the context, and what happens.
        Write a short narration (2-3 sentences) to introduce the scene to a viewer before it starts.
        Focus on setting the scene and explaining the situation.
        
        Subtitles:
        {subtitles}
        
        Narration:
        """
        return self.generate_content(prompt)
