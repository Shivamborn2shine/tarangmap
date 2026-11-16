from datetime import datetime, timezone
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Device, Observation, Project, SurveySession
from ..schemas import SessionCreate, SessionOut, SessionPatch

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


def _to_session_out(s: SurveySession, db: Session) -> SessionOut:
    obs_count = db.query(func.count(Observation.id)).filter(Observation.session_id == s.id).scalar() or 0
    dev = db.query(Device).filter(Device.id == s.device_id).first()
    return SessionOut(
        id=s.id,
        project_id=s.project_id,
        device_id=s.device_id,
        device_model=dev.model if dev else None,
        device_platform=dev.platform if dev else None,
        name=s.name,
        map_mode=s.map_mode,
        status=s.status,
        started_at=s.started_at,
        ended_at=s.ended_at,
        settings=json.loads(s.settings_json or "{}"),
        observation_count=obs_count,
    )


@router.get("", response_model=list[SessionOut])
def list_sessions(
    project_id: str | None = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(SurveySession)
    if project_id:
        q = q.filter(SurveySession.project_id == project_id)
    sessions = q.order_by(SurveySession.started_at.desc()).all()
    return [_to_session_out(s, db) for s in sessions]


@router.post("", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    if not db.query(Project).filter(Project.id == payload.project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
    if not db.query(Device).filter(Device.id == payload.device_id).first():
        raise HTTPException(status_code=404, detail="Device not found")

    s = SurveySession(
        id=str(uuid.uuid4()),
        project_id=payload.project_id,
        device_id=payload.device_id,
        name=payload.name,
        map_mode=payload.map_mode,
        status="recording",
        settings_json=json.dumps(payload.settings),
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return _to_session_out(s, db)


@router.patch("/{session_id}", response_model=SessionOut)
def update_session(session_id: str, payload: SessionPatch, db: Session = Depends(get_db)):
    s = db.query(SurveySession).filter(SurveySession.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if payload.status is not None:
        s.status = payload.status
        if payload.status == "finished" and s.ended_at is None:
            s.ended_at = datetime.now(timezone.utc)
    if payload.name is not None:
        s.name = payload.name
    db.commit()
    db.refresh(s)
    return _to_session_out(s, db)
