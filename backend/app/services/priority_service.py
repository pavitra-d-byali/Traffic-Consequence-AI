from collections import Counter
from datetime import datetime, timezone

def rank_issues(complaints):
    if not complaints: return []
    sev={"low":1,"medium":2,"high":3,"critical":4}
    counts=Counter(c.category for c in complaints)
    now=datetime.now(timezone.utc)
    rows=[]
    for c in complaints:
        dt=c.timestamp if c.timestamp.tzinfo else c.timestamp.replace(tzinfo=timezone.utc)
        recency=2 ** (-max(0,(now-dt).total_seconds()/86400)/30)
        severity=sev.get(c.severity,1)/4
        frequency=min(counts[c.category]/10,1)
        recurrence=min(sum(1 for x in complaints if x.category==c.category and x.id!=c.id)/5,1)
        score=100*(.35*severity+.25*frequency+.25*recurrence+.15*recency)
        rows.append({"complaint_id":c.id,"category":c.category,"score":round(score,1),"formula":"35% normalized severity + 25% category frequency + 25% recurrence + 15% 30-day half-life recency","official_standard":False})
    return sorted(rows,key=lambda x:x["score"],reverse=True)
