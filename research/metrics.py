import logging
import textstat
from typing import List, Dict, Any
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GPT2Tokenizer, GPT2LMHeadModel
from bert_score import score as bertscore_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BenchmarkMetrics:
    """
    Computes metrics for benchmarking:
    1. Semantic Fidelity: BERTScore
    2. Human-likeness: Perplexity
    3. Readability: Flesch-Kincaid Grade
    """

    def __init__(self, use_gpu: bool = False):
        self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"
        self._ppl_model_id = None
        self._ppl_tokenizer = None
        self._ppl_model = None

    def compute_readability(self, texts: List[str]) -> Dict[str, float]:
        """
        Compute Flesch-Kincaid Grade Level.
        Lower score = easier to read.
        """
        scores = [textstat.flesch_kincaid_grade(t) for t in texts if t.strip()]
        return {
            "fk_grade_mean": float(np.mean(scores)) if scores else 0.0,
            "fk_grade_std": float(np.std(scores)) if scores else 0.0
        }

    def compute_bertscore(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """
        Compute BERTScore (Semantic Similarity).
        """
        try:
            # bert_score.score returns tensors for P, R, F1
            P, R, F1 = bertscore_score(predictions, references, lang="en", verbose=True, rescale_with_baseline=False)
            return {
                "bert_precision_mean": float(P.mean().item()),
                "bert_recall_mean": float(R.mean().item()),
                "bert_f1_mean": float(F1.mean().item())
            }
        except Exception as e:
            logger.error(f"Error computing BERTScore: {e}")
            return {}

    def compute_perplexity(self, texts: List[str], model_id: str = "gpt2") -> Dict[str, float]:
        """
        Compute Perplexity using a standard LM (default: gpt2).
        Lower perplexity = more natural/predictable to the model.
        """
        try:
            # filter empty texts
            valid_texts = [t for t in texts if t.strip()]
            if not valid_texts:
                return {"perplexity_mean": 0.0}

            # Lazy-load model/tokenizer
            if self._ppl_model is None or self._ppl_model_id != model_id:
                logger.info(f"Loading LM for perplexity: {model_id}")
                # Use GPT-2 family by default
                if model_id.lower().startswith("gpt2"):
                    self._ppl_tokenizer = GPT2Tokenizer.from_pretrained(model_id)
                    self._ppl_model = GPT2LMHeadModel.from_pretrained(model_id)
                else:
                    self._ppl_tokenizer = AutoTokenizer.from_pretrained(model_id)
                    self._ppl_model = AutoModelForCausalLM.from_pretrained(model_id)
                self._ppl_model.to(self.device)
                self._ppl_model.eval()
                self._ppl_model_id = model_id

            ppl_values = []
            for text in valid_texts:
                enc = self._ppl_tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                )
                input_ids = enc.input_ids.to(self.device)
                with torch.no_grad():
                    outputs = self._ppl_model(input_ids, labels=input_ids)
                    loss = outputs.loss
                    ppl = torch.exp(loss).item()
                    ppl_values.append(ppl)
            return {
                "perplexity_mean": float(np.mean(ppl_values))
            }
        except Exception as e:
            logger.error(f"Error computing Perplexity: {e}")
            return {}

    def evaluate_all(self, original_texts: List[str], simplified_texts: List[str]) -> Dict[str, Any]:
        """
        Run all metrics.
        """
        logger.info("Computing Readability...")
        orig_read = self.compute_readability(original_texts)
        simp_read = self.compute_readability(simplified_texts)

        logger.info("Computing BERTScore (Semantic Preservation)...")
        # We compare Simplified (Pred) vs Original (Ref) to check how much meaning is kept
        bert_metrics = self.compute_bertscore(predictions=simplified_texts, references=original_texts)

        logger.info("Computing Perplexity (Fluency)...")
        orig_ppl = self.compute_perplexity(original_texts)
        simp_ppl = self.compute_perplexity(simplified_texts)

        return {
            "original_readability": orig_read,
            "simplified_readability": simp_read,
            "semantic_fidelity": bert_metrics,
            "original_perplexity": orig_ppl,
            "simplified_perplexity": simp_ppl
        }
