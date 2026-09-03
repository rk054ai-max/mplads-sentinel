from decimal import Decimal
from ml.similarity.duplicate import detect_potential_duplicates
from backend.schemas.work import Work

def test_detect_potential_duplicates():
    work1 = Work(
        work_id="W1", 
        description="Construction of 5km concrete road",
        latitude=28.6139,
        longitude=77.2090,
        sanctioned_amount=Decimal("1000000")
    )
    work2 = Work(
        work_id="W2", 
        description="Construction of 5km concrete road", # Identical description
        latitude=28.6145, # Very close geographically
        longitude=77.2095,
        sanctioned_amount=Decimal("1020000") # Very close amount
    )
    work3 = Work(
        work_id="W3", 
        description="Installation of water coolers in school",
        latitude=12.9716,
        longitude=77.5946,
        sanctioned_amount=Decimal("50000")
    )
    
    dataset = [work1, work2, work3]
    
    result = detect_potential_duplicates(work1, dataset, text_threshold=0.88)
    
    assert result["duplicate_score"] > 88.0
    assert len(result["matches"]) == 1
    
    match = result["matches"][0]
    assert match["work_id"] == "W2"
    assert match["reason"] == "potential_duplicate"
    assert match["distance_m"] < 1000.0
    assert match["similarity"] >= 0.88
    
    assert any("text similarity" in ev for ev in result["evidence"])
    assert any("proximity" in ev for ev in result["evidence"])
    assert any("sanctioned amounts" in ev for ev in result["evidence"])

def test_detect_no_duplicates():
    work1 = Work(work_id="W1", description="Building a bridge")
    work2 = Work(work_id="W2", description="Buying computers for school")
    
    result = detect_potential_duplicates(work1, [work1, work2], text_threshold=0.88)
    assert result["duplicate_score"] == 0.0
    assert len(result["matches"]) == 0
