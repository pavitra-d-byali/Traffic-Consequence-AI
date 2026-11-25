from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.complaint import Category, ReviewStatus, Severity
from app.schemas.dashboard import (ComplaintPage, DashboardMap, DashboardOverview,
                                   DashboardSummaryPage, ReviewStatusResponse, ReviewStatusUpdate)
from app.services.dashboard_service import dashboard_map, dashboard_overview, dashboard_summaries, search_complaints, update_review_status

router = APIRouter(prefix="/api/dashboard", tags=["authority dashboard"])

@router.get("/overview", response_model=DashboardOverview)
def overview(recent_window_days: int = Query(7, ge=1, le=90), chart_days: int = Query(30, ge=7, le=90),
             priority_limit: int = Query(8, ge=1, le=50), db: Session = Depends(get_db)):
    return dashboard_overview(db, recent_window_days, chart_days, priority_limit)

@router.get("/complaints", response_model=ComplaintPage)
def complaints(q: str | None = Query(None, max_length=200), category: Category | None = None,
               severity: Severity | None = None, review_status: ReviewStatus | None = None,
               sort_by: Literal["newest", "severity", "priority"] = "newest",
               page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
               db: Session = Depends(get_db)):
    return search_complaints(db, q=q, category=category, severity=severity, review_status=review_status,
                             sort_by=sort_by, page=page, page_size=page_size)

@router.patch("/complaints/{complaint_id}/review-status", response_model=ReviewStatusResponse)
def set_review_status(complaint_id: str, payload: ReviewStatusUpdate, db: Session = Depends(get_db)):
    item = update_review_status(db, complaint_id, payload.review_status)
    if item is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"id": item.id, "review_status": item.review_status}

@router.get("/summaries", response_model=DashboardSummaryPage)
def summaries(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return dashboard_summaries(db, page=page, page_size=page_size)

@router.get("/map", response_model=DashboardMap)
def map_data(db: Session = Depends(get_db)):
    return dashboard_map(db)
