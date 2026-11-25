from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Complaint
from app.schemas.analysis import AnalysisSummary
router=APIRouter(prefix="/api/analysis",tags=["analysis"])
@router.get("/{complaint_id}",response_model=AnalysisSummary)
def analysis(complaint_id:str,db:Session=Depends(get_db)):
    c=db.get(Complaint,complaint_id)
    if not c: raise HTTPException(404,"Complaint not found")
    return {"complaint_id":c.id,"category":c.category,"category_source":c.category_source,"extracted_details":c.extracted_details,"summary":c.summary,"summary_status":c.summary_status,"similarity_results":c.similarity_results}
