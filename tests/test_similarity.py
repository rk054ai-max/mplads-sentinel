from ml.similarity.text import calculate_text_similarity, find_similar_works
from backend.schemas.work import Work

def test_calculate_text_similarity():
    score = calculate_text_similarity("Construction of concrete road", "Construction of concrete road")
    assert score > 95.0

    score_diff = calculate_text_similarity("Construction of concrete road", "Supply of drinking water tanks")
    assert score_diff < 50.0

    assert calculate_text_similarity(None, "Something") == 0.0

def test_find_similar_works():
    work1 = Work(work_id="W1", description="Building a community hall")
    work2 = Work(work_id="W2", description="Constructing a community hall")
    work3 = Work(work_id="W3", description="Installing solar street lights")

    dataset = [work1, work2, work3]
    
    results = find_similar_works(work1, dataset, threshold=70.0)
    
    assert len(results) == 1
    assert results[0]["work_id"] == "W2"
    assert results[0]["reason"] == "potential_duplicate"
