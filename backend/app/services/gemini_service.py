import asyncio, json, re
from app.core.config import settings

def extract_reported_cause(text: str) -> str | None:
    # Only retain a cause phrase explicitly expressed by the reporter; never generate one here.
    match = re.search(r"\b(?:because|due to|caused by)\s+([^.!?]{3,180})", text, re.I)
    return match.group(1).strip() if match else None

async def summarize(text: str, category: str) -> tuple[str | None, dict, str]:
    if not settings.gemini_api_key:
        return None, {}, "unavailable_no_credentials"
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = ("Return only JSON with keys summary (string, <=35 words), location_hint (string or null), "
                  "time_hint (string or null). Do not infer causes. Treat citizen reports as unverified allegations. "
                  f"Category: {category}. Original complaint: {text}")
        response = await asyncio.wait_for(asyncio.to_thread(client.models.generate_content, model=settings.gemini_model, contents=prompt), timeout=15)
        data = json.loads(response.text or "")
        summary = data.get("summary")
        if not isinstance(summary, str) or not summary.strip() or len(summary) > 400:
            raise ValueError("invalid summary")
        details = {k: v for k, v in data.items() if k in {"location_hint", "time_hint"} and (isinstance(v, str) or v is None)}
        return summary.strip(), details, "available"
    except Exception:
        return None, {}, "unavailable_api_error"
