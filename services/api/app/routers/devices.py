import json
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Device
from ..schemas import DeviceOut, DeviceRegister

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.get("", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).order_by(Device.created_at.desc()).all()
    return [
        DeviceOut(
            id=d.id,
            platform=d.platform,
            model=d.model,
            os_version=d.os_version,
            capabilities=json.loads(d.capabilities_json or "{}"),
            created_at=d.created_at,
        )
        for d in devices
    ]


@router.post("/register", response_model=DeviceOut, status_code=201)
def register_device(payload: DeviceRegister, db: Session = Depends(get_db)):
    dev_id = payload.id or str(uuid.uuid4())
    existing = db.query(Device).filter(Device.id == dev_id).first()
    if existing:
        existing.model = payload.model
        existing.os_version = payload.os_version
        existing.capabilities_json = json.dumps(payload.capabilities)
        db.commit()
        db.refresh(existing)
        d = existing
    else:
        d = Device(
            id=dev_id,
            platform=payload.platform,
            model=payload.model,
            os_version=payload.os_version,
            capabilities_json=json.dumps(payload.capabilities),
        )
        db.add(d)
        db.commit()
        db.refresh(d)
    return DeviceOut(
        id=d.id,
        platform=d.platform,
        model=d.model,
        os_version=d.os_version,
        capabilities=json.loads(d.capabilities_json or "{}"),
        created_at=d.created_at,
    )
