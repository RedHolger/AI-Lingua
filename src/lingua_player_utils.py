
import srt
import os
import time
from typing import List, Dict, Any, Optional
from datetime import timedelta
from gtts import gTTS
import google.generativeai as genai
import json

class Scene:
    def __init__(self, index: int, start: timedelta, end: timedelta, text: str):
        self.index = index
        self.start = start
        self.end = end
        self.text = text
        self.narration_text: Optional[str] = None
        self.narration_audio_path: Optional[str] = None
        self.quiz: Optional[Dict[str, Any]] = None

def parse_srt(file_path: str) -> List[srt.Subtitle]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return list(srt.parse(f.read()))

def segment_scenes(subtitles: List[srt.Subtitle], gap_threshold_seconds: float = 3.0) -> List[Scene]:
    scenes = []
    if not subtitles:
        return scenes

    current_scene_start = subtitles[0].start
    current_scene_text = [subtitles[0].content.replace('\n', ' ')]
    last_end = subtitles[0].end

    scene_idx = 1

    for i in range(1, len(subtitles)):
        sub = subtitles[i]
        gap = (sub.start - last_end).total_seconds()
        
        if gap > gap_threshold_seconds:
            # End current scene
            scene_text = " ".join(current_scene_text)
            scenes.append(Scene(scene_idx, current_scene_start, last_end, scene_text))
            scene_idx += 1
            
            # Start new scene
            current_scene_start = sub.start
            current_scene_text = [sub.content.replace('\n', ' ')]
        else:
            current_scene_text.append(sub.content.replace('\n', ' '))
        
        last_end = sub.end

    # Add last scene
    if current_scene_text:
        scene_text = " ".join(current_scene_text)
        scenes.append(Scene(scene_idx, current_scene_start, last_end, scene_text))

    return scenes

def generate_scene_content(scenes: List[Scene], gemini_client, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for scene in scenes:
        print(f"Processing Scene {scene.index}...")
        
        # 1. Generate Narration Text
        prompt = f"""
        Analyze this video scene transcript:
        "{scene.text}"
        
        1. Write a short, engaging narration (1-2 sentences) to introduce this scene to a learner. 
           Explain the context or what is about to happen. Start with "In this scene,".
        2. Create a multiple-choice quiz question based on the scene content to test comprehension.
           Format as JSON: {{ "narration": "...", "quiz": {{ "question": "...", "options": ["A", "B", "C"], "answer": "A" }} }}
        """
        
        try:
            response = gemini_client.generate_content(prompt)
            # Clean response to get JSON
            text = response.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            data = json.loads(text)
            narration_text = data.get("narration", "Scene " + str(scene.index))
            scene.narration_text = narration_text
            scene.quiz = data.get("quiz")
            
            # 2. Generate Audio
            audio_path = os.path.join(output_dir, f"scene_{scene.index}_narration.mp3")
            if not os.path.exists(audio_path):
                tts = gTTS(text=narration_text, lang='en')
                tts.save(audio_path)
            scene.narration_audio_path = audio_path
            
        except Exception as e:
            print(f"Error processing scene {scene.index}: {e}")
            # Fallback
            scene.narration_audio_path = None
            scene.narration_text = None
            scene.quiz = None

    return scenes
