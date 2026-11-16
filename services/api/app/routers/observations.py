from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..analysis import classify_observation
from ..database import get_db
from ..models import (
    ActiveTest,
    CellObservation,
    Observation,
    SurveySession,
    SyncBatch,
    WifiObservation,
)
from ..schemas import (
    ActiveTestPayload,
    BatchIngestRequest,
    BatchIngestResponse,
    BatchItemResult,
    CellularPayload,
    ObservationOut,
    WifiPayload,
)

router = APIRouter(prefix="/api/v1", tags=["observations"])


def _to_obs_out(obs: Observation) -> ObservationOut:
    tier, label = classify_observation(obs)
    return ObservationOut(
        schema_version=obs.schema_version,
        id=obs.id,
        session_id=obs.session_id,
        device_id=obs.device_id,
        kind=obs.kind,
        technology=obs.technology,
        observed_at=obs.observed_at,
        recorded_at=obs.recorded_at,
        received_at=obs.received_at,
        metric_source=obs.metric_source,
        freshness_ms=obs.freshness_ms,
        missing_reason=obs.missing_reason,
        location_kind=obs.location_kind,
        room_label=obs.room_label,
        x_norm=obs.x_norm,
        y_norm=obs.y_norm,
        lat=obs.lat,
        lon=obs.lon,
        gps_accuracy_m=obs.gps_accuracy_m,
        wifi=WifiPayload(
            ssid=obs.wifi.ssid,
            bssid_hash=obs.wifi.bssid_hash,
            frequency_mhz=obs.wifi.frequency_mhz,
            band=obs.wifi.band,
            channel=obs.wifi.channel,
            rssi_dbm=obs.wifi.rssi_dbm,
            quality_percent=obs.wifi.quality_percent,
            rx_mbps=obs.wifi.rx_mbps,
            tx_mbps=obs.wifi.tx_mbps,
            radio_type=obs.wifi.radio_type,
        ) if obs.wifi else None,
        cellular=CellularPayload(
            operator_name=obs.cellular.operator_name,
            tech=obs.cellular.tech,
            registered=obs.cellular.registered,
            rsrp_dbm=obs.cellular.rsrp_dbm,
            rsrq_db=obs.cellular.rsrq_db,
            sinr_db=obs.cellular.sinr_db,
            ss_rsrp_dbm=obs.cellular.ss_rsrp_dbm,
            ss_rsrq_db=obs.cellular.ss_rsrq_db,
            ss_sinr_db=obs.cellular.ss_sinr_db,
            pci=obs.cellular.pci,
            tac=obs.cellular.tac,
            band=obs.cellular.band,
        ) if obs.cellular else None,
        active_test=ActiveTestPayload(
            endpoint=obs.active_test.endpoint,
            latency_ms=obs.active_test.latency_ms,
            jitter_ms=obs.active_test.jitter_ms,
            packet_loss_pct=obs.active_test.packet_loss_pct,
            download_mbps=obs.active_test.download_mbps,
            upload_mbps=obs.active_test.upload_mbps,
            bytes_used=obs.active_test.bytes_used,
        ) if obs.active_test else None,
        signal_tier=tier,
        primary_metric_label=label,
    )


@router.post("/observations/batch", response_model=BatchIngestResponse)
def ingest_batch(payload: BatchIngestRequest, db: Session = Depends(get_db)):
    items: list[BatchItemResult] = []
    accepted = 0
    duplicate = 0
    rejected = 0
    now = datetime.now(timezone.utc)

    valid_sessions = {s.id for s in db.query(SurveySession.id).all()}

    for item in payload.observations:
        if db.query(Observation.id).filter(Observation.id == item.id).first():
            duplicate += 1
            items.append(BatchItemResult(id=item.id, status="duplicate", reason="Already ingested"))
            continue

        if item.session_id not in valid_sessions:
            rejected += 1
            items.append(BatchItemResult(id=item.id, status="rejected", reason="Unknown session_id"))
            continue

        obs = Observation(
            id=item.id,
            schema_version=item.schema_version,
            session_id=item.session_id,
            device_id=item.device_id,
            kind=item.kind,
            technology=item.technology,
            observed_at=item.observed_at,
            recorded_at=item.recorded_at,
            received_at=now,
            metric_source=item.metric_source,
            freshness_ms=item.freshness_ms,
            missing_reason=item.missing_reason,
            location_kind=item.location_kind,
            room_label=item.room_label,
            x_norm=item.x_norm,
            y_norm=item.y_norm,
            lat=item.lat,
            lon=item.lon,
            gps_accuracy_m=item.gps_accuracy_m,
        )
        db.add(obs)

        if item.kind == "wifi" and item.wifi:
            db.add(WifiObservation(
                observation_id=item.id,
                ssid=item.wifi.ssid,
                bssid_hash=item.wifi.bssid_hash,
                frequency_mhz=item.wifi.frequency_mhz,
                band=item.wifi.band,
                channel=item.wifi.channel,
                rssi_dbm=item.wifi.rssi_dbm,
                quality_percent=item.wifi.quality_percent,
                rx_mbps=item.wifi.rx_mbps,
                tx_mbps=item.wifi.tx_mbps,
                radio_type=item.wifi.radio_type,
            ))
        elif item.kind == "cellular" and item.cellular:
            db.add(CellObservation(
                observation_id=item.id,
                operator_name=item.cellular.operator_name,
                tech=item.cellular.tech,
                registered=item.cellular.registered,
                rsrp_dbm=item.cellular.rsrp_dbm,
                rsrq_db=item.cellular.rsrq_db,
                sinr_db=item.cellular.sinr_db,
                ss_rsrp_dbm=item.cellular.ss_rsrp_dbm,
                ss_rsrq_db=item.cellular.ss_rsrq_db,
                ss_sinr_db=item.cellular.ss_sinr_db,
                pci=item.cellular.pci,
                tac=item.cellular.tac,
                band=item.cellular.band,
            ))
        elif item.kind == "active_test" and item.active_test:
            db.add(ActiveTest(
                observation_id=item.id,
                endpoint=item.active_test.endpoint,
                latency_ms=item.active_test.latency_ms,
                jitter_ms=item.active_test.jitter_ms,
                packet_loss_pct=item.active_test.packet_loss_pct,
                download_mbps=item.active_test.download_mbps,
                upload_mbps=item.active_test.upload_mbps,
                bytes_used=item.active_test.bytes_used,
            ))

        accepted += 1
        items.append(BatchItemResult(id=item.id, status="accepted"))

    if not db.query(SyncBatch.id).filter(SyncBatch.id == payload.batch_id).first():
        db.add(SyncBatch(
            id=payload.batch_id,
            device_id=payload.device_id,
            received_at=now,
            accepted_count=accepted,
            duplicate_count=duplicate,
            rejected_count=rejected,
        ))

    db.commit()
    return BatchIngestResponse(
        batch_id=payload.batch_id,
        accepted=accepted,
        duplicate=duplicate,
        rejected=rejected,
        items=items,
    )


@router.get("/sessions/{session_id}/observations", response_model=list[ObservationOut])
def get_session_observations(
    session_id: str,
    kind: str | None = Query(None),
    limit: int = Query(500, le=2000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    if not db.query(SurveySession.id).filter(SurveySession.id == session_id).first():
        raise HTTPException(status_code=404, detail="Session not found")
    q = db.query(Observation).filter(Observation.session_id == session_id)
    if kind:
        q = q.filter(Observation.kind == kind)
    rows = q.order_by(Observation.observed_at.asc()).offset(offset).limit(limit).all()
    return [_to_obs_out(r) for r in rows]


@router.get("/projects/{project_id}/observations", response_model=list[ObservationOut])
def get_project_observations(
    project_id: str,
    kind: str | None = Query(None),
    session_id: str | None = Query(None),
    limit: int = Query(1000, le=5000),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Observation)
        .join(SurveySession, Observation.session_id == SurveySession.id)
        .filter(SurveySession.project_id == project_id)
    )
    if kind:
        q = q.filter(Observation.kind == kind)
    if session_id:
        q = q.filter(Observation.session_id == session_id)
    rows = q.order_by(Observation.observed_at.asc()).limit(limit).all()
    return [_to_obs_out(r) for r in rows]
