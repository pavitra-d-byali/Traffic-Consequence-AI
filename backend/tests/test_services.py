from types import SimpleNamespace
from datetime import datetime, timezone, timedelta
import pytest
from pydantic import ValidationError
from app.schemas.complaint import ComplaintCreate
from app.services.classification_service import classify
from app.services.graph_service import build_graph
from app.services.hotspot_service import group_hotspots
from app.services.priority_service import rank_issues

def report(id="1", text="Traffic congestion on road", category="congestion", lat=12.0, lon=77.0, severity="high", days=0, cause=None):
    return SimpleNamespace(id=id,complaint_text=text,category=category,location_name="Demo",latitude=lat,longitude=lon,severity=severity,timestamp=datetime.now(timezone.utc)-timedelta(days=days),reported_cause=cause,is_synthetic=True)

def test_complaint_validation_rejects_unpaired_coordinates():
    with pytest.raises(ValidationError): ComplaintCreate(complaint_text="Traffic jam on road",location_name="Here",latitude=1,severity="low")
def test_classifier_fallback_categories():
    assert classify("A large pothole is here")[0]=="road_damage"
    assert classify("Cars are parked across the street")[0]=="parking"
    assert classify("Something unusual")[0]=="other"
def test_graph_links_and_citizen_reported_cause():
    g=build_graph([report(cause="a broken signal")])
    assert {n["type"] for n in g["nodes"]}>={"complaint","location","category","reported_cause"}
    assert any(e.get("qualification")=="citizen-reported" for e in g["edges"])
def test_hotspot_groups_nearby_related_reports_only():
    assert len(group_hotspots([report("1"),report("2",lat=12.001)],radius_km=1,min_reports=2))==1
    assert group_hotspots([report("1"),report("2",lat=13)],radius_km=1,min_reports=2)==[]
def test_priority_explainable_and_ranked():
    rows=rank_issues([report("1",days=0),report("2",days=2,severity="low")])
    assert rows[0]["score"]>=rows[1]["score"]
    assert rows[0]["official_standard"] is False
