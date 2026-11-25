from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.complaint import ComplaintCreate, ComplaintRead, ImportResult, ImportIssue
from app.services.complaint_service import create_complaint, get_complaint, list_complaints
from app.services.csv_service import parse_csv

router=APIRouter(prefix="/api/complaints",tags=["complaints"])
@router.post("",response_model=ComplaintRead,status_code=201)
async def create(payload:ComplaintCreate,db:Session=Depends(get_db)): return await create_complaint(db,payload)
@router.get("",response_model=list[ComplaintRead])
def listing(limit:int=100,offset:int=0,db:Session=Depends(get_db)): return list_complaints(db,min(max(limit,1),500),max(offset,0))
@router.get("/{complaint_id}",response_model=ComplaintRead)
def retrieve(complaint_id:str,db:Session=Depends(get_db)):
    item=get_complaint(db,complaint_id)
    if not item: raise HTTPException(404,"Complaint not found")
    return item
@router.post("/import",response_model=ImportResult)
async def import_csv(file:UploadFile=File(...),db:Session=Depends(get_db)):
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Upload a .csv file")
    rows,issues=parse_csv(await file.read())
    imported=[]
    for row_num,payload in rows:
        try: imported.append(await create_complaint(db,payload))
        except Exception as exc: issues.append({"row":row_num,"error":str(exc)})
    return {"imported":len(imported),"rejected":len(issues),"issues":issues,"complaints":imported}
