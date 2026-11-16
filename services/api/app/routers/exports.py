import csv
import io
import json
from statistics import median
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..analysis import classify_observation
from ..database import get_db
from ..models import Device, Observation, Project, SurveySession

router = APIRouter(prefix="/api/v1", tags=["exports-and-compare"])


@router.get("/projects/{project_id}/export")
def export_project(
    project_id: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    redact: bool = Query(True),
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rows = (
        db.query(Observation)
        .join(SurveySession, Observation.session_id == SurveySession.id)
        .filter(SurveySession.project_id == project_id)
        .order_by(Observation.observed_at.asc())
        .all()
    )

    records = []
    for r in rows:
        tier, label = classify_observation(r)
        records.append({
            "id": r.id,
            "session_id": r.session_id,
            "kind": r.kind,
            "technology": r.technology,
            "observed_at": r.observed_at.isoformat(),
            "metric_source": r.metric_source,
            "freshness_ms": r.freshness_ms,
            "signal_tier": tier,
            "primary_metric": label,
            "location_kind": r.location_kind,
            "room_label": r.room_label,
            "x_norm": r.x_norm,
            "y_norm": r.y_norm,
            "lat": None if (redact and r.location_kind == "outdoor") else r.lat,
            "lon": None if (redact and r.location_kind == "outdoor") else r.lon,
            "gps_accuracy_m": r.gps_accuracy_m,
            "wifi_ssid": "[REDACTED]" if (redact and r.wifi and r.wifi.ssid) else (r.wifi.ssid if r.wifi else None),
            "wifi_band": r.wifi.band if r.wifi else None,
            "wifi_rssi_dbm": r.wifi.rssi_dbm if r.wifi else None,
            "wifi_quality_percent": r.wifi.quality_percent if r.wifi else None,
            "cell_operator": r.cellular.operator_name if r.cellular else None,
            "cell_tech": r.cellular.tech if r.cellular else None,
            "cell_rsrp_dbm": r.cellular.rsrp_dbm if r.cellular else None,
            "cell_ss_rsrp_dbm": r.cellular.ss_rsrp_dbm if r.cellular else None,
            "active_latency_ms": r.active_test.latency_ms if r.active_test else None,
        })

    if format == "json":
        payload = {
            "schema_version": 1,
            "project_id": project.id,
            "project_name": project.name,
            "redacted": redact,
            "count": len(records),
            "observations": records,
        }
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="tarang-{project.id[:8]}.json"'},
        )

    buf = io.StringIO()
    if records:
        writer = csv.DictWriter(buf, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    else:
        buf.write("id,session_id,kind,technology,observed_at,signal_tier,primary_metric\n")

    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="tarang-{project.id[:8]}.csv"'},
    )


@router.get("/compare")
def compare_sessions(
    session_a: str = Query(...),
    session_b: str = Query(...),
    db: Session = Depends(get_db),
):
    sa = db.query(SurveySession).filter(SurveySession.id == session_a).first()
    sb = db.query(SurveySession).filter(SurveySession.id == session_b).first()
    if not sa or not sb:
        raise HTTPException(status_code=404, detail="One or both sessions not found")

    dev_a = db.query(Device).filter(Device.id == sa.device_id).first()
    dev_b = db.query(Device).filter(Device.id == sb.device_id).first()

    obs_a = db.query(Observation).filter(Observation.session_id == sa.id).all()
    obs_b = db.query(Observation).filter(Observation.session_id == sb.id).all()

    def _stats(obs_list: list[Observation]):
        rssi = [o.wifi.rssi_dbm for o in obs_list if o.wifi and o.wifi.rssi_dbm is not None]
        qual = [o.wifi.quality_percent for o in obs_list if o.wifi and o.wifi.quality_percent is not None]
        rsrp = [
            o.cellular.ss_rsrp_dbm if o.cellular.ss_rsrp_dbm is not None else o.cellular.rsrp_dbm
            for o in obs_list
            if o.cellular and (o.cellular.ss_rsrp_dbm is not None or o.cellular.rsrp_dbm is not None)
        ]
        bands = sorted({o.wifi.band for o in obs_list if o.wifi and o.wifi.band})
        return {
            "count": len(obs_list),
            "wifi_rssi_median_dbm": round(median(rssi), 1) if rssi else None,
            "wifi_quality_median_pct": round(median(qual), 1) if qual else None,
            "cellular_rsrp_median_dbm": round(median(rsrp), 1) if rsrp else None,
            "bands": bands,
        }

    stats_a = _stats(obs_a)
    stats_b = _stats(obs_b)

    caveats = []
    if sa.device_id != sb.device_id:
        caveats.append(
            f"Different hardware used ({dev_a.model if dev_a else 'Unknown'} vs {dev_b.model if dev_b else 'Unknown'}). Antenna gain and radio calibration may differ."
        )
    if stats_a["bands"] != stats_b["bands"]:
        caveats.append(
            f"Different Wi-Fi bands observed ({', '.join(stats_a['bands']) or 'none'} vs {', '.join(stats_b['bands']) or 'none'})."
        )
    if abs(stats_a["count"] - stats_b["count"]) > max(3, int(0.3 * max(stats_a["count"], stats_b["count"], 1))):
        caveats.append(
            f"Sample count mismatch ({stats_a['count']} vs {stats_b['count']} observations)."
        )

    return {
        "session_a": {
            "id": sa.id,
            "name": sa.name,
            "device": dev_a.model if dev_a else None,
            "platform": dev_a.platform if dev_a else None,
            "started_at": sa.started_at,
            "stats": stats_a,
        },
        "session_b": {
            "id": sb.id,
            "name": sb.name,
            "device": dev_b.model if dev_b else None,
            "platform": dev_b.platform if dev_b else None,
            "started_at": sb.started_at,
            "stats": stats_b,
        },
        "caveats": caveats,
    }
