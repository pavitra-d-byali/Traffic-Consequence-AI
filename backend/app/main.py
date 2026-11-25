from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import initialize_database
from app.db import models
from app.api.routes import complaints, analysis, graph, dashboard

initialize_database()
app=FastAPI(title="Traffic Consequence AI",description="Prototype citizen-report decision support. Reports and causes are unverified unless independently confirmed.",version="0.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(complaints.router); app.include_router(analysis.router); app.include_router(graph.router); app.include_router(dashboard.router)
@app.get("/api/health")
def health(): return {"status":"ok","gemini_configured":bool(settings.gemini_api_key)}
@app.post("/api/demo/seed")
async def seed_demo():
    from pathlib import Path
    from sqlalchemy.orm import Session
    from app.db.database import SessionLocal
    from app.services.csv_service import parse_csv
    from app.services.complaint_service import create_complaint
    path=Path(__file__).resolve().parents[1]/"data"/"synthetic_demo.csv"
    rows,issues=parse_csv(path.read_bytes())
    db:Session=SessionLocal()
    try:
        existing={c.source_reference for c in db.query(models.Complaint).all() if c.source_reference}
        added=0
        for _,payload in rows:
            if payload.source_reference in existing: continue
            payload.is_synthetic=True
            await create_complaint(db,payload); added+=1
        return {"inserted":added,"skipped_existing":len(rows)-added,"rejected":issues,"label":"Synthetic demo data — not real traffic reports"}
    finally: db.close()
