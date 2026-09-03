import logging
from typing import Any

from sentence_transformers import SentenceTransformer, util
import torch

from backend.schemas.work import Work

logger = logging.getLogger(__name__)

# Cache the model at the module level
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def calculate_text_similarity(description_a: str | None, description_b: str | None) -> float:
    """
    Calculates NLP similarity between two strings using sentence embeddings.
    Returns a normalized score between 0.0 and 100.0.
    """
    if not description_a or not description_b:
        return 0.0
        
    model = get_model()
    # Compute embeddings
    emb_a = model.encode(description_a, convert_to_tensor=True)
    emb_b = model.encode(description_b, convert_to_tensor=True)
    
    # Compute cosine similarity
    cosine_score = util.cos_sim(emb_a, emb_b).item()
    
    # Normalize to 0-100 (cosine sim goes from -1 to 1)
    normalized = max(0.0, cosine_score) * 100.0
    return round(normalized, 2)

def find_similar_works(work: Work, dataset: list[Work], threshold: float = 80.0) -> list[dict[str, Any]]:
    """
    Finds potentially duplicate or similar works in the dataset compared to the target work.
    Only returns works that score at or above the threshold.
    """
    if not work.description or not dataset:
        return []

    model = get_model()
    
    # Filter valid dataset targets (skip self and null descriptions)
    targets = [w for w in dataset if w.work_id != work.work_id and w.description]
    
    if not targets:
        return []

    target_descriptions = [w.description for w in targets]
    
    # Compute embeddings
    work_emb = model.encode(work.description, convert_to_tensor=True)
    targets_emb = model.encode(target_descriptions, convert_to_tensor=True)
    
    # Compute similarities against all targets
    cosine_scores = util.cos_sim(work_emb, targets_emb)[0]
    
    results = []
    for i, score_tensor in enumerate(cosine_scores):
        score = max(0.0, score_tensor.item()) * 100.0
        if score >= threshold:
            results.append({
                "work_id": targets[i].work_id,
                "score": round(score, 2),
                "reason": "potential_duplicate",
                "evidence": f"Text similarity: {round(score, 2)}/100"
            })
            
    # Sort descending by score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
