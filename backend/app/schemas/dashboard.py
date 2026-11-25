from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.complaint import Category, ReviewStatus, Severity

class ReviewStatusUpdate(BaseModel):
    review_status: ReviewStatus

class DashboardComplaint(BaseModel):
    id: str
    complaint_text: str
    location_name: str
    latitude: float | None
    longitude: float | None
    timestamp: str
    severity: Severity
    category: Category
    summary: str | None
    summary_status: str
    similarity_results: list[dict]
    reported_cause: str | None
    is_synthetic: bool
    review_status: ReviewStatus
    priority_score: float

class ComplaintPage(BaseModel):
    items: list[DashboardComplaint]
    total: int
    page: int
    page_size: int
    pages: int

class DashboardOverview(BaseModel):
    total_complaints: int
    recent_complaints: int
    recent_window_days: int
    potential_hotspots: int
    awaiting_review: int
    review_status_counts: dict[str, int]
    category_breakdown: list[dict]
    volume_over_time: list[dict]
    priority_issues: list[DashboardComplaint]

class DashboardSummary(BaseModel):
    complaint_id: str
    summary: str | None
    summary_status: str
    reported_cause: str | None
    ai_generated: bool
    source_complaint_ids: list[str]
    related_report_ids: list[str]
    related_categories: list[str]
    related_locations: list[str]
    uncertain_or_missing: list[str]
    suggested_next_steps: list[str]
    is_synthetic: bool

class DashboardSummaryPage(BaseModel):
    items: list[DashboardSummary]
    total: int
    page: int
    page_size: int
    pages: int

class ReviewStatusResponse(BaseModel):
    id: str
    review_status: ReviewStatus

class DashboardMapComplaint(BaseModel):
    id: str
    location_name: str
    complaint_text: str
    latitude: float
    longitude: float
    category: Category
    severity: Severity
    review_status: ReviewStatus
    is_synthetic: bool

class DashboardMapHotspot(BaseModel):
    id: str
    label: str
    report_count: int
    categories: list[str]
    latitude: float
    longitude: float
    complaint_ids: list[str]
    radius_km: float

class DashboardUnmappedComplaint(BaseModel):
    id: str
    location_name: str
    complaint_text: str
    is_synthetic: bool

class DashboardMap(BaseModel):
    complaints: list[DashboardMapComplaint]
    unmapped_count: int
    unmapped_complaints: list[DashboardUnmappedComplaint]
    hotspots: list[DashboardMapHotspot]
    mapped_count: int
