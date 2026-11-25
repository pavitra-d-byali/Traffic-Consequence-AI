from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db.database import Base, get_db
from app.main import app

def test_dashboard_endpoints_and_status_validation():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = Session(engine)
    def override_db():
        yield session
    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            created = client.post("/api/complaints", json={
                "complaint_text": "Traffic signal is not working at Oak Junction",
                "location_name": "Oak Junction", "severity": "high",
            })
            assert created.status_code == 201
            complaint_id = created.json()["id"]
            assert created.json()["review_status"] == "new"
            overview = client.get("/api/dashboard/overview")
            assert overview.status_code == 200 and overview.json()["total_complaints"] == 1
            page = client.get("/api/dashboard/complaints?q=Oak&page=1&page_size=5")
            assert page.status_code == 200 and page.json()["items"][0]["id"] == complaint_id
            assert client.get("/api/complaints").status_code == 200
            assert client.get(f"/api/complaints/{complaint_id}").status_code == 200
            assert client.get(f"/api/analysis/{complaint_id}").status_code == 200
            assert client.get("/api/graph").status_code == 200
            assert client.get("/api/hotspots").status_code == 200
            assert client.get("/api/priority").status_code == 200
            changed = client.patch(f"/api/dashboard/complaints/{complaint_id}/review-status", json={"review_status": "under_review"})
            assert changed.status_code == 200 and changed.json()["review_status"] == "under_review"
            assert client.patch(f"/api/dashboard/complaints/{complaint_id}/review-status", json={"review_status": "approved"}).status_code == 422
            assert client.patch("/api/dashboard/complaints/missing/review-status", json={"review_status": "reviewed"}).status_code == 404
            assert client.get("/api/dashboard/map").json()["unmapped_count"] == 1
            assert client.get("/api/dashboard/summaries").json()["items"][0]["source_complaint_ids"] == [complaint_id]
    finally:
        app.dependency_overrides.clear()
        session.close()
        engine.dispose()
