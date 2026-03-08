
import sys
import os
import time
import subprocess
from typing import List, Optional
from lingua_player_utils import parse_srt, segment_scenes, generate_scene_content, Scene
from gemini_client import GeminiClient

class LinguaPlayer:
    def __init__(self, video_path: str):
        self.video_path = video_path
        self.scenes: List[Scene] = []
        self.current_scene_idx = -1
        self.last_scene_idx = -1
        
    def load_content(self):
        # 1. Determine Paths
        base_path = os.path.splitext(self.video_path)[0]
        # Check for simplified subs first (as primary or secondary)
        simpl_path = base_path + ".simplified.srt"
        # Check for original subs
        orig_path = base_path + ".srt"
        if not os.path.exists(orig_path):
             embedded_srt = base_path + ".embedded.srt"
             if os.path.exists(embedded_srt):
                 orig_path = embedded_srt
        
        if not os.path.exists(orig_path):
            print(f"Original subtitles not found at {orig_path}. Cannot analyze scenes.")
            return

        print("Loading subtitles and segmenting scenes...")
        subs = parse_srt(orig_path)
        self.scenes = segment_scenes(subs)
        print(f"Found {len(self.scenes)} scenes.")

        # 2. Generate AI Content (Narrations/Quizzes)
        output_dir = os.path.join(os.path.dirname(self.video_path), "lingua_content")
        
        # Check if content already exists to skip generation (simple check)
        # In a real app, we'd load JSON. Here we just check if audio exists for first scene
        first_audio = os.path.join(output_dir, "scene_1_narration.mp3")
        if not os.path.exists(first_audio):
            print("Generating AI content (Narrations & Quizzes)... This may take a while.")
            try:
                gemini = GeminiClient()
                self.scenes = generate_scene_content(self.scenes, gemini, output_dir)
            except Exception as e:
                print(f"AI Generation failed: {e}. Proceeding without narrations.")
        else:
            print("Found existing AI content. Loading...")
            # Ideally load from JSON, but for now we assume file naming convention matches
            for scene in self.scenes:
                audio_path = os.path.join(output_dir, f"scene_{scene.index}_narration.mp3")
                if os.path.exists(audio_path):
                    scene.narration_audio_path = audio_path

        # 3. Start Playback via external mpv
        print(f"Playing: {self.video_path}")
        mpv_cmd = ["mpv", self.video_path]

        # Load subtitles
        if os.path.exists(orig_path):
            mpv_cmd.append(f"--sub-file={orig_path}")
        if os.path.exists(simpl_path):
            mpv_cmd.append(f"--sub-file={simpl_path}")

        # Launch mpv as a separate process (opens its own window on macOS)
        try:
            proc = subprocess.Popen(mpv_cmd)
            proc.wait()
        except FileNotFoundError:
            print("Error: 'mpv' executable not found. Install via Homebrew: brew install mpv")
        except Exception as e:
            print(f"Error launching mpv: {e}")

    def run(self):
        try:
            # For now, all playback is handled by the external mpv process in load_content
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lingua_player.py <video_path>")
        sys.exit(1)
    
    player = LinguaPlayer(sys.argv[1])
    player.load_content()
    player.run()
