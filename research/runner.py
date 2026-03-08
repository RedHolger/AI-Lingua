import sys
import os
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.transcriber import Transcriber
from research.data_loader import LibriSpeechLoader
from research.metrics import BenchmarkMetrics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BenchmarkRunner:
    def __init__(self, output_dir: str = "benchmark_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.loader = LibriSpeechLoader()
        self.metrics = BenchmarkMetrics()
        # Initialize Transcriber (ensure GEMINI_API_KEY is set)
        try:
            self.transcriber = Transcriber()
        except Exception as e:
            logger.error(f"Failed to initialize Transcriber. Check API Key. {e}")
            sys.exit(1)

    async def process_sample(self, sample: Dict, level: str = "A2") -> Dict:
        """
        Process a single sample:
        1. Take original text.
        2. Call Gemini to simplify it to target level.
        3. Return {original, simplified}
        """
        original_text = sample["text"]
        
        # Prepare payload for Transcriber
        # We treat the whole text as one 'line' for simplicity in this benchmark
        payload = {
            "lines": [
                {
                    "start_time": 0.0,
                    "end_time": 10.0, # Dummy time
                    "text": original_text
                }
            ]
        }

        try:
            # Call simplify_text (async)
            result = await self.transcriber.simplify_text(payload, level=level)
            
            # Extract simplified text
            simplified_lines = [l["text"] for l in result.get("lines", [])]
            simplified_text = " ".join(simplified_lines)
            
            return {
                "id": sample["id"],
                "original": original_text,
                "simplified": simplified_text,
                "level": level
            }
        except Exception as e:
            logger.error(f"Error processing sample {sample['id']}: {e}")
            return {
                "id": sample["id"],
                "original": original_text,
                "simplified": original_text,
                "error": str(e),
                "fallback": True
            }

    async def run_benchmark(self, num_samples: int = 5):
        logger.info(f"Starting benchmark with {num_samples} samples...")
        
        # 1. Load Data
        samples = self.loader.get_samples(num_samples)
        
        # 2. Process (Generate Simplified Text)
        results = []
        for s in samples:
            logger.info(f"Processing sample {s['id']}...")
            res = await self.process_sample(s, level="A2") # Benchmark for A2 level
            results.append(res)
        
        # Filter successful results
        valid_results = [r for r in results if r.get("simplified")]
        logger.info(f"Successfully processed {len(valid_results)}/{len(samples)} samples.")

        if not valid_results:
            logger.warning("No valid results to evaluate.")
            return

        original_texts = [r["original"] for r in valid_results]
        simplified_texts = [r["simplified"] for r in valid_results]

        # 3. Compute Metrics
        logger.info("Computing metrics...")
        metrics_report = self.metrics.evaluate_all(original_texts, simplified_texts)
        
        # 4. Save Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "timestamp": timestamp,
            "num_samples": len(valid_results),
            "metrics": metrics_report,
            "details": valid_results
        }
        
        report_path = self.output_dir / f"benchmark_report_{timestamp}.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Benchmark completed. Report saved to {report_path}")
        
        # Print Summary
        print("\n=== Benchmark Summary ===")
        print(f"Samples: {len(valid_results)}")
        print("Readability (Flesch-Kincaid):")
        print(f"  Original:   {metrics_report['original_readability']['fk_grade_mean']:.2f}")
        print(f"  Simplified: {metrics_report['simplified_readability']['fk_grade_mean']:.2f}")
        print("Semantic Fidelity (BERTScore):")
        print(f"  F1: {metrics_report['semantic_fidelity'].get('bert_f1_mean', 0):.4f}")
        print("Fluency (Perplexity - Lower is better):")
        print(f"  Original:   {metrics_report['original_perplexity'].get('perplexity_mean', 0):.2f}")
        print(f"  Simplified: {metrics_report['simplified_perplexity'].get('perplexity_mean', 0):.2f}")
        print("=========================")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    asyncio.run(runner.run_benchmark(num_samples=2))
