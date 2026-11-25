from sqlalchemy.orm import Session
from app.db.models import Complaint
from app.schemas.complaint import ComplaintCreate
from app.services.classification_service import classify
from app.services.gemini_service import extract_reported_cause, summarize
from app.services.similarity_service import find_similar

async def create_complaint(db: Session, payload: ComplaintCreate) -> Complaint:
    category, source = classify(payload.complaint_text)
    candidates = [{"id": c.id, "text": c.complaint_text} for c in db.query(Complaint).all()]
    similar = find_similar(payload.complaint_text, candidates)
    summary, details, status = await summarize(payload.complaint_text, category)
    cause = extract_reported_cause(payload.complaint_text)
    obj = Complaint(**payload.model_dump(), category=category, category_source=source,
                    extracted_details={"gemini": details, "reported_cause_basis": "citizen-reported" if cause else None},
                    summary=summary, summary_status=status, similarity_results=similar, reported_cause=cause)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_complaint(db: Session, complaint_id: str):
    return db.get(Complaint, complaint_id)

def list_complaints(db: Session, limit: int = 100, offset: int = 0):
    return db.query(Complaint).order_by(Complaint.timestamp.desc()).offset(offset).limit(limit).all()
