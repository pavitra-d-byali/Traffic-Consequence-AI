from functools import lru_cache
from app.core.config import settings

@lru_cache(maxsize=1)
def _model():
    if not settings.enable_sentence_transformers:
        return None
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except Exception:
        return None

def find_similar(text: str, candidates: list[dict], limit: int = 3) -> list[dict]:
    model = _model()
    matches = []
    if model and candidates:
        try:
            from sentence_transformers import util
            vectors = model.encode([text] + [c["text"] for c in candidates], convert_to_tensor=True)
            scores = util.cos_sim(vectors[0], vectors[1:])[0]
            matches = [{"complaint_id": candidates[i]["id"], "score": float(scores[i])} for i in range(len(candidates)) if float(scores[i]) >= .55]
            return sorted(matches, key=lambda x: x["score"], reverse=True)[:limit]
        except Exception:
            pass
    # Documented lexical Jaccard fallback; it is a rough duplicate hint, not semantic similarity.
    tokens = set(text.lower().split())
    for c in candidates:
        other = set(c["text"].lower().split())
        score = len(tokens & other) / max(1, len(tokens | other))
        if score >= .18:
            matches.append({"complaint_id": c["id"], "score": round(score, 3), "method": "token_jaccard_fallback"})
    return sorted(matches, key=lambda x: x["score"], reverse=True)[:limit]
