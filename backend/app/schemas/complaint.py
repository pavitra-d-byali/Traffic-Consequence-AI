from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Severity = Literal["low", "medium", "high", "critical"]
Category = Literal["congestion", "signal_issue", "parking", "road_damage", "pedestrian_safety", "accident", "other"]
ReviewStatus = Literal["new", "under_review", "reviewed"]

class ComplaintCreate(BaseModel):
    complaint_text: str = Field(min_length=5, max_length=5000)
    location_name: str = Field(min_length=2, max_length=300)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    severity: Severity
    is_synthetic: bool = False
    source_reference: str | None = None
    @model_validator(mode="after")
    def coordinates_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        return self

class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    complaint_text: str
    location_name: str
    latitude: float | None
    longitude: float | None
    timestamp: datetime
    severity: Severity
    category: Category
    category_source: str
    extracted_details: dict
    summary: str | None
    summary_status: str
    similarity_results: list
    reported_cause: str | None
    is_synthetic: bool
    source_reference: str | None
    review_status: ReviewStatus = "new"

class ImportIssue(BaseModel):
    row: int
    error: str

class ImportResult(BaseModel):
    imported: int
    rejected: int
    issues: list[ImportIssue]
    complaints: list[ComplaintRead]
