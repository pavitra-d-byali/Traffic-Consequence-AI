from datetime import datetime, timezone
from io import BytesIO
import pandas as pd
from app.schemas.complaint import ComplaintCreate

def parse_csv(content: bytes) -> tuple[list[tuple[int, ComplaintCreate]], list[dict]]:
    try:
        frame = pd.read_csv(BytesIO(content), dtype=str, keep_default_na=False)
    except Exception as exc:
        return [], [{"row": 1, "error": f"Could not read CSV: {exc}"}]
    aliases = {"complaint_text": ["complaint_text", "text", "description"], "location_name": ["location_name", "location", "locality"],
               "latitude": ["latitude", "lat"], "longitude": ["longitude", "lon", "lng"], "timestamp": ["timestamp", "reported_date"],
               "severity": ["severity"]}
    cols = {target: next((c for c in options if c in frame.columns), None) for target, options in aliases.items()}
    if not cols["complaint_text"] or not cols["location_name"] or not cols["severity"]:
        return [], [{"row": 1, "error": "CSV requires complaint_text (or description), location_name (or locality), and severity columns"}]
    imported, issues = [], []
    for idx, row in frame.iterrows():
        n = int(idx) + 2
        try:
            raw_time = row[cols["timestamp"]] if cols["timestamp"] else ""
            if cols["timestamp"] == "reported_date" and "reported_time" in frame.columns and row.get("reported_time"):
                raw_time += " " + row["reported_time"]
            when = pd.to_datetime(raw_time, utc=True).to_pydatetime() if raw_time else datetime.now(timezone.utc)
            lat = float(row[cols["latitude"]]) if cols["latitude"] and row[cols["latitude"]].strip() else None
            lon = float(row[cols["longitude"]]) if cols["longitude"] and row[cols["longitude"]].strip() else None
            sev = row[cols["severity"]].strip().lower()
            sev = {"low": "low", "medium": "medium", "moderate": "medium", "high": "high", "critical": "critical"}.get(sev)
            if not sev: raise ValueError("severity must be low, medium, high, or critical")
            location = row[cols["location_name"]].strip()
            if "city" in frame.columns and row.get("city"):
                location = ", ".join(x for x in [location, row.get("city", "").strip(), row.get("state", "").strip()] if x)
            payload = ComplaintCreate(complaint_text=row[cols["complaint_text"]].strip(), location_name=location,
                latitude=lat, longitude=lon, timestamp=when, severity=sev, is_synthetic="synthetic" in str(row.get("source_type", "")).lower(),
                source_reference=row.get("complaint_id") or None)
            if "category" in frame.columns: pass  # source categories retained only as source data, AI categorization remains authoritative for prototype labels
            imported.append((n, payload))
        except Exception as exc:
            issues.append({"row": n, "error": str(exc)})
    return imported, issues
