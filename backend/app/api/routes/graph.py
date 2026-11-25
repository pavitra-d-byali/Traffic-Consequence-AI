from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Complaint
from app.services.graph_service import build_graph
from app.services.hotspot_service import group_hotspots
from app.services.priority_service import rank_issues
router=APIRouter(prefix="/api",tags=["knowledge graph"])
def all_complaints(db): return db.query(Complaint).all()
@router.get("/graph")
def graph(db:Session=Depends(get_db)): return build_graph(all_complaints(db))
@router.get("/hotspots")
def hotspots(db:Session=Depends(get_db)): return {"hotspots":group_hotspots(all_complaints(db)),"note":"Potential groupings based on reported coordinates and related categories; not verified."}
@router.get("/priority")
def priority(db:Session=Depends(get_db)): return {"issues":rank_issues(all_complaints(db)),"note":"Prototype decision-support score, not an official traffic-risk standard."}
