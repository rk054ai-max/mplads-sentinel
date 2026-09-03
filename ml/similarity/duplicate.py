import logging
from typing import Any
from decimal import Decimal

from sentence_transformers import SentenceTransformer, util
import torch
from geopy.distance import geodesic

from backend.schemas.work import Work

logger = logging.getLogger(__name__)

_model = None
# Simple in-memory cache for embeddings: description -> embedding tensor
_embedding_cache = {}

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_embedding(description: str):
    if description in _embedding_cache:
        return _embedding_cache[description]
    
    model = get_model()
    emb = model.encode(description, convert_to_tensor=True)
    _embedding_cache[description] = emb
    return emb

def detect_potential_duplicates(
    work: Work, 
    dataset: list[Work], 
    text_threshold: float = 0.88
) -> dict[str, Any]:
    """
    Detects potential duplicate candidates by combining text similarity,
    location proximity, and cost similarity.
    """
    if not work.description or not dataset:
        return {"duplicate_score": 0.0, "matches": [], "evidence": []}
        
    model = get_model()
    work_emb = get_embedding(work.description)
    
    matches = []
    max_duplicate_score = 0.0
    global_evidence = []
    
    # Optional location
    has_location = work.latitude is not None and work.longitude is not None
    target_coords = (work.latitude, work.longitude) if has_location else None
    
    for candidate in dataset:
        if candidate.work_id == work.work_id or not candidate.description:
            continue
            
        cand_emb = get_embedding(candidate.description)
        # Compute cosine similarity
        text_sim = util.cos_sim(work_emb, cand_emb).item()
        
        if text_sim < text_threshold:
            continue
            
        match_evidence = [f"High text similarity ({round(text_sim, 2)})"]
        combined_score = text_sim * 100.0  # base score 0-100
        distance_m = None
        
        # Location proximity
        if has_location and candidate.latitude is not None and candidate.longitude is not None:
            cand_coords = (candidate.latitude, candidate.longitude)
            distance_m = geodesic(target_coords, cand_coords).meters
            
            if distance_m <= 1000: # Within 1km boosts score
                combined_score = min(100.0, combined_score + 5.0)
                match_evidence.append(f"Close geographic proximity ({round(distance_m, 1)}m)")
        
        # Cost similarity
        if work.sanctioned_amount and candidate.sanctioned_amount:
            # If amounts are within 5% of each other
            diff = abs(work.sanctioned_amount - candidate.sanctioned_amount)
            if diff <= work.sanctioned_amount * Decimal("0.05"):
                combined_score = min(100.0, combined_score + 5.0)
                match_evidence.append("Highly similar sanctioned amounts")
                
        matches.append({
            "work_id": candidate.work_id,
            "similarity": round(text_sim, 2),
            "distance_m": round(distance_m, 1) if distance_m is not None else None,
            "reason": "potential_duplicate"
        })
        
        if combined_score > max_duplicate_score:
            max_duplicate_score = combined_score
            global_evidence = match_evidence
            
    # Sort matches by similarity descending
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    
    return {
        "duplicate_score": round(max_duplicate_score, 2),
        "matches": matches,
        "evidence": global_evidence
    }
