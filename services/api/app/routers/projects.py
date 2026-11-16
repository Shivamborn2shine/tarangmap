import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..analysis import build_project_summary
from ..config import UPLOAD_DIR
from ..database import get_db
from ..models import Floorplan, Observation, Project, SurveySession
from ..schemas import FloorplanOut, ProjectCreate, ProjectOut

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    out = []
    for p in projects:
        s_count = db.query(func.count(SurveySession.id)).filter(SurveySession.project_id == p.id).scalar() or 0
        o_count = (
            db.query(func.count(Observation.id))
            .join(SurveySession, Observation.session_id == SurveySession.id)
            .filter(SurveySession.project_id == p.id)
            .scalar()
            or 0
        )
        out.append(ProjectOut(
            id=p.id,
            name=p.name,
            description=p.description,
            map_mode=p.map_mode,
            created_at=p.created_at,
            session_count=s_count,
            observation_count=o_count,
        ))
    return out


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    proj = Project(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        map_mode=payload.map_mode,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return ProjectOut(
        id=proj.id,
        name=proj.name,
        description=proj.description,
        map_mode=proj.map_mode,
        created_at=proj.created_at,
        session_count=0,
        observation_count=0,
    )


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    s_count = db.query(func.count(SurveySession.id)).filter(SurveySession.project_id == p.id).scalar() or 0
    o_count = (
        db.query(func.count(Observation.id))
        .join(SurveySession, Observation.session_id == SurveySession.id)
        .filter(SurveySession.project_id == p.id)
        .scalar()
        or 0
    )
    return ProjectOut(
        id=p.id,
        name=p.name,
        description=p.description,
        map_mode=p.map_mode,
        created_at=p.created_at,
        session_count=s_count,
        observation_count=o_count,
    )


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    db.commit()


@router.get("/{project_id}/floorplans", response_model=list[FloorplanOut])
def list_floorplans(project_id: str, db: Session = Depends(get_db)):
    fps = db.query(Floorplan).filter(Floorplan.project_id == project_id).all()
    return [
        FloorplanOut(
            id=fp.id,
            project_id=fp.project_id,
            name=fp.name,
            image_uri=fp.image_uri,
            width_px=fp.width_px,
            height_px=fp.height_px,
            scale_m_per_px=fp.scale_m_per_px,
            created_at=fp.created_at,
        )
        for fp in fps
    ]


@router.post("/{project_id}/floorplans", response_model=FloorplanOut, status_code=201)
def upload_floorplan(
    project_id: str,
    name: str = Form("Floor Plan"),
    width_px: int = Form(1000),
    height_px: int = Form(640),
    scale_m_per_px: float | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    fp_id = str(uuid.uuid4())
    ext = Path(file.filename or "floorplan.png").suffix or ".png"
    dest = UPLOAD_DIR / f"{fp_id}{ext}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    fp = Floorplan(
        id=fp_id,
        project_id=project_id,
        name=name,
        image_uri=f"/uploads/{dest.name}",
        width_px=width_px,
        height_px=height_px,
        scale_m_per_px=scale_m_per_px,
    )
    db.add(fp)
    db.commit()
    db.refresh(fp)
    return FloorplanOut(
        id=fp.id,
        project_id=fp.project_id,
        name=fp.name,
        image_uri=fp.image_uri,
        width_px=fp.width_px,
        height_px=fp.height_px,
        scale_m_per_px=fp.scale_m_per_px,
        created_at=fp.created_at,
    )


@router.get("/{project_id}/summary")
def get_project_summary(project_id: str, db: Session = Depends(get_db)):
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    obs = (
        db.query(Observation)
        .join(SurveySession, Observation.session_id == SurveySession.id)
        .filter(SurveySession.project_id == project_id)
        .all()
    )
    summary = build_project_summary(obs)
    summary["project_id"] = project_id
    summary["project_name"] = p.name
    return summary
