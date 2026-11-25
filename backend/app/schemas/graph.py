from pydantic import BaseModel
class GraphData(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    hotspots: list[dict]
    priority_issues: list[dict]
