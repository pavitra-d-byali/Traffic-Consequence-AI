import networkx as nx
from app.services.hotspot_service import group_hotspots
from app.services.priority_service import rank_issues

def build_graph(complaints):
    graph=nx.MultiDiGraph()
    for c in complaints:
        cid="complaint:"+c.id; locid="location:"+c.location_name.strip().lower(); catid="category:"+c.category
        graph.add_node(cid,id=cid,type="complaint",label=c.complaint_text[:100],synthetic=c.is_synthetic)
        graph.add_node(locid,id=locid,type="location",label=c.location_name)
        graph.add_node(catid,id=catid,type="category",label=c.category)
        graph.add_edge(cid,locid,id=f"{cid}->reported_at->{locid}",relation="reported_at")
        graph.add_edge(cid,catid,id=f"{cid}->classified_as->{catid}",relation="classified_as",source="AI-generated")
        if c.reported_cause:
            causeid="reported_cause:"+c.id
            graph.add_node(causeid,id=causeid,type="reported_cause",label=c.reported_cause,qualification="citizen-reported")
            graph.add_edge(cid,causeid,id=f"{cid}->reported_cause->{causeid}",relation="reported_cause",qualification="citizen-reported")
    nodes=[dict(v) for _,v in graph.nodes(data=True)]
    edges=[dict({"source":u,"target":v},**d) for u,v,d in graph.edges(data=True)]
    return {"nodes":nodes,"edges":edges,"hotspots":group_hotspots(complaints),"priority_issues":rank_issues(complaints)}
