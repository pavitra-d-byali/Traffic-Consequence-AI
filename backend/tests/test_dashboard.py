from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db.database import Base
from app.db.models import Complaint
from app.services.dashboard_service import dashboard_overview, dashboard_summaries, search_complaints, update_review_status

def make_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return Session(engine)

def complaint(id, *, text="Traffic is backed up", location="Main Road", category="congestion",
              severity="medium", days_ago=0, status="new", lat=None, lon=None):
    return Complaint(id=id, complaint_text=text, location_name=location, latitude=lat, longitude=lon,
                     timestamp=datetime.now(timezone.utc)-timedelta(days=days_ago), severity=severity,
                     category=category, category_source="keyword_fallback", extracted_details={}, summary=None,
                     summary_status="unavailable_no_credentials", similarity_results=[], reported_cause=None,
                     is_synthetic=False, review_status=status)

def test_dashboard_metrics_are_aggregated_from_rows():
    db = make_session()
    db.add_all([complaint("a"), complaint("b", category="parking", days_ago=12, status="reviewed")])
    db.commit()
    result = dashboard_overview(db, recent_window_days=7, chart_days=30)
    assert result["total_complaints"] == 2
    assert result["recent_complaints"] == 1
    assert result["awaiting_review"] == 1
    assert result["review_status_counts"]["reviewed"] == 1
    assert {row["category"] for row in result["category_breakdown"]} == {"congestion", "parking"}
    assert len(result["volume_over_time"]) == 30
    db.close()

def test_dashboard_search_filter_and_pagination():
    db = make_session()
    db.add_all([complaint("a", text="Signal is broken", location="Oak St", category="signal_issue", severity="high"),
                complaint("b", text="Cars block lane", location="Pine St", category="parking", status="under_review"),
                complaint("c", text="Queue by junction", location="Oak St", category="congestion", severity="critical")])
    db.commit()
    first = search_complaints(db, q="oak", page=1, page_size=1)
    second = search_complaints(db, q="oak", page=2, page_size=1)
    filtered = search_complaints(db, review_status="under_review", severity="high")
    assert first["total"] == 2 and first["items"][0]["id"] != second["items"][0]["id"]
    assert first["pages"] == 2
    assert filtered["items"] == [] and filtered["total"] == 0
    db.close()

def test_priority_sort_and_review_status_update_persist():
    db = make_session()
    db.add_all([complaint("low", severity="low"), complaint("high", severity="critical")])
    db.commit()
    page = search_complaints(db, sort_by="priority")
    assert page["items"][0]["id"] == "high"
    changed = update_review_status(db, "low", "under_review")
    assert changed and changed.review_status == "under_review"
    assert db.get(Complaint, "low").review_status == "under_review"
    assert update_review_status(db, "missing", "reviewed") is None
    db.close()

def test_empty_dashboard_results_are_safe():
    db = make_session()
    overview = dashboard_overview(db)
    page = search_complaints(db, q="not found")
    assert overview["total_complaints"] == 0
    assert overview["potential_hotspots"] == 0
    assert overview["priority_issues"] == []
    assert page["items"] == [] and page["pages"] == 0
    db.close()

def test_summary_sources_are_distinct_from_similarity_hints():
    db = make_session()
    source = complaint("source", text="Original citizen report")
    related = complaint("related", text="Similar nearby report", category="parking")
    source.summary = "AI condensed the original report."
    source.summary_status = "available"
    source.similarity_results = [{"complaint_id": "related", "score": .7}]
    db.add_all([source, related])
    db.commit()
    row = next(item for item in dashboard_summaries(db)["items"] if item["complaint_id"] == "source")
    assert row["source_complaint_ids"] == ["source"]
    assert row["related_report_ids"] == ["related"]
    assert row["related_categories"] == ["congestion", "parking"]
    db.close()
