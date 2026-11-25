from pydantic import BaseModel
class AnalysisSummary(BaseModel):
    complaint_id: str
    category: str
    category_source: str
    extracted_details: dict
    summary: str | None
    summary_status: str
    similarity_results: list
