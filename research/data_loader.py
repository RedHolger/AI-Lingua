import logging
import os
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LibriSpeechLoader:
    """
    Loader for LibriSpeech corpus from a local path.
    Expects the standard LibriSpeech structure with *.trans.txt files:
      <dir>/<speaker>/<chapter>/<speaker>-<chapter>.trans.txt
    Each line: "<utt_id> <TRANSCRIPT...>"
    Audio files are <utt_id>.flac in the same directory.
    """
    def __init__(self, root: str | None = None):
        # Allow override via env; fallback to provided path
        self.root = Path(root or os.environ.get(
            "LIBRISPEECH_ROOT",
            "/Users/manuvashistha/Downloads/TED/speech-corpus-dl/data/cache/LibriSpeech"
        )).expanduser()
        if not self.root.exists():
            logger.warning(f"LibriSpeech root not found: {self.root}")

    def get_samples(self, num_samples: int = 10) -> List[Dict]:
        samples: List[Dict] = []
        count = 0

        if not self.root.exists():
            logger.error(f"LibriSpeech path does not exist: {self.root}")
            return samples

        trans_files = list(self.root.glob("**/*.trans.txt"))
        if not trans_files:
            logger.error(f"No .trans.txt files found under {self.root}")
            return samples

        for tf in sorted(trans_files):
            try:
                with open(tf, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split(maxsplit=1)
                        if len(parts) != 2:
                            continue
                        utt_id, text = parts
                        audio_path = tf.parent / f"{utt_id}.flac"
                        samples.append({
                            "id": utt_id,
                            "text": text,
                            "audio": {"path": str(audio_path)} if audio_path.exists() else None,
                            "speaker_id": utt_id.split("-")[0]
                        })
                        count += 1
                        if count >= num_samples:
                            return samples
            except Exception as e:
                logger.error(f"Failed reading {tf}: {e}")
                continue

        return samples

if __name__ == "__main__":
    # Test the loader
    loader = TedLiumLoader(streaming=True)
    samples = loader.get_samples(2)
    for s in samples:
        print(f"ID: {s['id']}")
        print(f"Text: {s['text'][:100]}...")
