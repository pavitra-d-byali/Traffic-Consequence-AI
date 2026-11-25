from collections import Counter
from datetime import datetime, timedelta, timezone
from math import ceil
from math import isfinite
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.db.models import Complaint
from app.schemas.complaint import ReviewStatus
from app.services.hotspot_service import group_hotspots
from app.services.priority_service import rank_issues

VALID_SEVERITIES = {"low": 1, "medium": 2, "high": 3, "critical": 4}

def _all(db: Session) -> list[Complaint]:
    return db.query(Complaint).all()

def _priorities(items: list[Complaint]) -> dict[str, float]:
    return {row["complaint_id"]: row["score"] for row in rank_issues(items)}

def serialize_complaint(item: Complaint, score: float) -> dict:
    timestamp = item.timestamp
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return {
        "id": item.id, "complaint_text": item.complaint_text, "location_name": item.location_name,
        "latitude": item.latitude, "longitude": item.longitude, "timestamp": timestamp.isoformat(),
        "severity": item.severity, "category": item.category, "summary": item.summary,
        "summary_status": item.summary_status, "similarity_results": item.similarity_results or [],
        "reported_cause": item.reported_cause, "is_synthetic": item.is_synthetic,
        "review_status": item.review_status or "new", "priority_score": score,
    }

def dashboard_overview(db: Session, recent_window_days: int = 7, chart_days: int = 30, priority_limit: int = 8) -> dict:
    items = _all(db)
    now = datetime.now(timezone.utc)
    recent_since = now - timedelta(days=recent_window_days)
    review_counts = Counter((item.review_status or "new") for item in items)
    category_counts = Counter(item.category for item in items)
    categories = [{"category": key, "count": category_counts[key]} for key in sorted(category_counts)]
    first_day = now.date() - timedelta(days=chart_days - 1)
    volume_counts = Counter()
    for item in items:
        stamp = item.timestamp
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        if stamp.date() >= first_day:
            volume_counts[stamp.date().isoformat()] += 1
    volume = [{"date": (first_day + timedelta(days=i)).isoformat(), "count": volume_counts[(first_day + timedelta(days=i)).isoformat()]}
              for i in range(chart_days)]
    priorities = _priorities(items)
    ranked = sorted(items, key=lambda item: priorities.get(item.id, 0), reverse=True)[:priority_limit]
    recent_count = sum(1 for item in items if (item.timestamp.replace(tzinfo=timezone.utc) if item.timestamp.tzinfo is None else item.timestamp) >= recent_since)
    return {
        "total_complaints": len(items), "recent_complaints": recent_count, "recent_window_days": recent_window_days,
        "potential_hotspots": len(group_hotspots(items)), "awaiting_review": review_counts.get("new", 0),
        "review_status_counts": {status: review_counts.get(status, 0) for status in ("new", "under_review", "reviewed")},
        "category_breakdown": categories, "volume_over_time": volume,
        "priority_issues": [serialize_complaint(item, priorities.get(item.id, 0)) for item in ranked],
    }

def search_complaints(db: Session, *, q: str | None = None, category: str | None = None,
                      severity: str | None = None, review_status: ReviewStatus | None = None,
                      sort_by: str = "newest", page: int = 1, page_size: int = 20) -> dict:
    query = db.query(Complaint)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter((Complaint.complaint_text.ilike(pattern)) | (Complaint.location_name.ilike(pattern)))
    if category:
        query = query.filter(Complaint.category == category)
    if severity:
        query = query.filter(Complaint.severity == severity)
    if review_status:
        query = query.filter(Complaint.review_status == review_status)
    filtered = query.all()
    all_items = _all(db)
    scores = _priorities(all_items)
    if sort_by == "priority":
        filtered.sort(key=lambda item: scores.get(item.id, 0), reverse=True)
    elif sort_by == "severity":
        filtered.sort(key=lambda item: (VALID_SEVERITIES.get(item.severity, 0), item.timestamp), reverse=True)
    else:
        filtered.sort(key=lambda item: item.timestamp, reverse=True)
    total = len(filtered)
    start = (page - 1) * page_size
    selected = filtered[start:start + page_size]
    return {"items": [serialize_complaint(item, scores.get(item.id, 0)) for item in selected],
            "total": total, "page": page, "page_size": page_size, "pages": ceil(total / page_size) if total else 0}

def update_review_status(db: Session, complaint_id: str, status: ReviewStatus) -> Complaint | None:
    item = db.get(Complaint, complaint_id)
    if item is None:
        return None
    item.review_status = status
    db.commit()
    db.refresh(item)
    return item

def dashboard_summaries(db: Session, *, page: int = 1, page_size: int = 20) -> dict:
    items = db.query(Complaint).order_by(Complaint.timestamp.desc()).all()
    total = len(items)
    start = (page - 1) * page_size
    selected = items[start:start + page_size]
    related_ids = {related_id for item in selected for entry in (item.similarity_results or [])
                   if (related_id := entry.get("complaint_id")) and related_id != item.id}
    related = {item.id: item for item in db.query(Complaint).filter(Complaint.id.in_(related_ids)).all()} if related_ids else {}
    result = []
    for item in selected:
        similar_ids = [entry.get("complaint_id") for entry in (item.similarity_results or []) if entry.get("complaint_id")]
        related_report_ids = [related_id for related_id in similar_ids if related_id in related]
        source_ids = [item.id]
        source_rows = [item] + [related[related_id] for related_id in related_report_ids]
        uncertain = []
        if item.latitude is None or item.longitude is None: uncertain.append("No coordinates were supplied; this report cannot be mapped.")
        if not item.reported_cause: uncertain.append("No cause was explicitly stated by the citizen.")
        if item.summary_status != "available": uncertain.append("An AI-generated summary is unavailable; use the original report.")
        if item.is_synthetic: uncertain.append("Synthetic demo record; not a real citizen report.")
        result.append({"complaint_id": item.id, "summary": item.summary, "summary_status": item.summary_status,
                       "reported_cause": item.reported_cause,
                       "ai_generated": item.summary_status == "available" and item.summary is not None,
                       "source_complaint_ids": source_ids,
                       "related_report_ids": related_report_ids,
                       "related_categories": sorted({row.category for row in source_rows}),
                       "related_locations": sorted({row.location_name for row in source_rows}),
                       "uncertain_or_missing": uncertain, "suggested_next_steps": [], "is_synthetic": item.is_synthetic})
    return {"items": result, "total": total, "page": page, "page_size": page_size, "pages": ceil(total / page_size) if total else 0}

def dashboard_map(db: Session) -> dict:
    items = _all(db)
    mapped, unmapped = [], []
    for item in items:
        valid = item.latitude is not None and item.longitude is not None and isfinite(item.latitude) and isfinite(item.longitude)
        if not valid:
            unmapped.append({"id": item.id, "location_name": item.location_name, "complaint_text": item.complaint_text,
                             "is_synthetic": item.is_synthetic})
        else:
            mapped.append({"id": item.id, "location_name": item.location_name, "complaint_text": item.complaint_text,
                           "latitude": item.latitude, "longitude": item.longitude, "category": item.category,
                           "severity": item.severity, "review_status": item.review_status or "new", "is_synthetic": item.is_synthetic})
    return {"complaints": mapped, "unmapped_count": len(unmapped), "unmapped_complaints": unmapped,
            "hotspots": group_hotspots(items), "mapped_count": len(mapped)}
