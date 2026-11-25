import math
from app.core.config import settings

def haversine_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat, dlon = lat2-lat1, lon2-lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371 * 2 * math.asin(math.sqrt(h))

def group_hotspots(complaints, radius_km=None, min_reports=None):
    radius = radius_km if radius_km is not None else settings.hotspot_radius_km
    minimum = min_reports if min_reports is not None else settings.hotspot_min_reports
    rows = [c for c in complaints if c.latitude is not None and c.longitude is not None
            and math.isfinite(c.latitude) and math.isfinite(c.longitude)]
    groups = []
    for c in rows:
        point=(c.latitude,c.longitude)
        found=next((g for g in groups if any(haversine_km(point,(x.latitude,x.longitude)) <= radius and x.category == c.category for x in g)),None)
        if found is None: groups.append([c])
        else: found.append(c)
    result=[]
    for group in groups:
        if len(group)<minimum: continue
        result.append({"id":"hotspot:"+"|".join(sorted(c.id for c in group)), "label":"Potential hotspot", "verified":False, "radius_km":radius,
            "report_count":len(group), "categories":sorted(set(c.category for c in group)),
            "latitude":sum(c.latitude for c in group)/len(group), "longitude":sum(c.longitude for c in group)/len(group),
            "complaint_ids":sorted(c.id for c in group)})
    return result
