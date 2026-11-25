import re
from functools import lru_cache
from app.core.config import settings
from app.schemas.complaint import Category

LABELS = ["congestion", "signal_issue", "parking", "road_damage", "pedestrian_safety", "accident", "other"]
RULES = {
    "signal_issue": r"\b(signal|traffic light|red light|junction light)\b",
    "parking": r"\b(park|parked|parking|double parked|no-parking)\b",
    "road_damage": r"\b(pothole|road damage|crater|broken road|uneven road)\b",
    "pedestrian_safety": r"\b(pedestrian|footpath|sidewalk|crosswalk|zebra crossing|school crossing)\b",
    "accident": r"\b(accident|collision|crash|vehicle hit|hit a)\b",
    "congestion": r"\b(traffic|congestion|queue|jam|backed up|slow moving)\b",
}
@lru_cache(maxsize=1)
def _pipeline():
    if not settings.enable_huggingface or not settings.classifier_model:
        return None
    try:
        from transformers import pipeline
        return pipeline("zero-shot-classification", model=settings.classifier_model)
    except Exception:
        return None

def classify(text: str) -> tuple[Category, str]:
    pipe = _pipeline()
    if pipe:
        try:
            label = pipe(text, candidate_labels=LABELS)["labels"][0]
            return label, "huggingface_zero_shot"
        except Exception:
            pass
    normalized = text.lower()
    for label, pattern in RULES.items():
        if re.search(pattern, normalized):
            return label, "keyword_fallback"
    return "other", "keyword_fallback"
