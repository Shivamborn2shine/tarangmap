from datetime import datetime, timezone
from pathlib import Path
import sys
import threading
import time
import uuid
from typing import Any, Optional

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Ensure services/api is importable so the hybrid laptop app exposes the full TARANG API
REPO_ROOT = Path(__file__).resolve().parents[3]
API_DIR = REPO_ROOT / "services" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from app.main import app as base_tarang_app  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import Device, Observation, Project, SurveySession, WifiObservation  # noqa: E402

from .probe import probe_windows_wifi, run_active_speed_test, run_active_tcp_probe, scan_nearby_networks  # noqa: E402
from .storage import OfflineQueue  # noqa: E402

QUEUE_DB = Path.home() / ".tarang" / "windows_collector_queue.db"
queue = OfflineQueue(QUEUE_DB)


class CollectorState:
    def __init__(self) -> None:
        self.recording: bool = False
        self.session_id: Optional[str] = None
        self.project_id: Optional[str] = None
        self.device_id: Optional[str] = None
        self.room_label: str = "Laptop Desk"
        self.x_norm: float = 0.5
        self.y_norm: float = 0.5
        self.cadence_sec: float = 5.0
        self.samples_recorded: int = 0
        self.last_scan: Optional[dict[str, Any]] = None
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self, project_id: str, session_id: str, device_id: str, room_label: str, x_norm: float, y_norm: float, cadence_sec: float = 5.0) -> None:
        self.stop()
        self.project_id = project_id
        self.session_id = session_id
        self.device_id = device_id
        self.room_label = room_label
        self.x_norm = x_norm
        self.y_norm = y_norm
        self.cadence_sec = max(2.0, cadence_sec)
        self.samples_recorded = 0
        self.recording = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.recording = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                scan = probe_windows_wifi()
                self.last_scan = scan
                if scan.get("available") and self.session_id and self.device_id:
                    obs_id = str(uuid.uuid4())
                    now = datetime.now(timezone.utc)
                    payload = {
                        "schema_version": 1,
                        "id": obs_id,
                        "session_id": self.session_id,
                        "device_id": self.device_id,
                        "kind": "wifi",
                        "technology": "wifi",
                        "observed_at": scan["observed_at"],
                        "recorded_at": now.isoformat(),
                        "metric_source": "windows_netsh_wlan",
                        "freshness_ms": 500,
                        "missing_reason": scan.get("missing_reason"),
                        "location_kind": "indoor",
                        "room_label": self.room_label,
                        "x_norm": self.x_norm,
                        "y_norm": self.y_norm,
                        "wifi": {
                            "ssid": scan.get("ssid"),
                            "bssid_hash": scan.get("bssid_hash"),
                            "frequency_mhz": scan.get("frequency_mhz"),
                            "band": scan.get("band"),
                            "channel": scan.get("channel"),
                            "rssi_dbm": scan.get("rssi_dbm"),
                            "quality_percent": scan.get("quality_percent"),
                            "rx_mbps": scan.get("rx_mbps"),
                            "tx_mbps": scan.get("tx_mbps"),
                            "radio_type": scan.get("radio_type"),
                        },
                    }
                    queue.enqueue(obs_id, payload, now.isoformat())
                    self._flush_queue()
                    self.samples_recorded += 1
            except Exception:
                pass
            self._stop_event.wait(self.cadence_sec)

    def _flush_queue(self) -> None:
        batch = queue.peek_batch(limit=100)
        if not batch:
            return
        db = SessionLocal()
        flushed_ids: list[str] = []
        try:
            for item in batch:
                if db.query(Observation.id).filter(Observation.id == item["id"]).first():
                    flushed_ids.append(item["id"])
                    continue
                if not db.query(SurveySession.id).filter(SurveySession.id == item["session_id"]).first():
                    continue
                obs = Observation(
                    id=item["id"],
                    schema_version=1,
                    session_id=item["session_id"],
                    device_id=item["device_id"],
                    kind=item["kind"],
                    technology=item["technology"],
                    observed_at=datetime.fromisoformat(item["observed_at"]),
                    recorded_at=datetime.fromisoformat(item["recorded_at"]),
                    received_at=datetime.now(timezone.utc),
                    metric_source=item["metric_source"],
                    freshness_ms=item["freshness_ms"],
                    missing_reason=item.get("missing_reason"),
                    location_kind=item["location_kind"],
                    room_label=item.get("room_label"),
                    x_norm=item.get("x_norm"),
                    y_norm=item.get("y_norm"),
                )
                db.add(obs)
                w = item.get("wifi") or {}
                db.add(WifiObservation(
                    observation_id=item["id"],
                    ssid=w.get("ssid"),
                    bssid_hash=w.get("bssid_hash"),
                    frequency_mhz=w.get("frequency_mhz"),
                    band=w.get("band"),
                    channel=w.get("channel"),
                    rssi_dbm=w.get("rssi_dbm"),
                    quality_percent=w.get("quality_percent"),
                    rx_mbps=w.get("rx_mbps"),
                    tx_mbps=w.get("tx_mbps"),
                    radio_type=w.get("radio_type"),
                ))
                flushed_ids.append(item["id"])
            db.commit()
            queue.remove_ids(flushed_ids)
        finally:
            db.close()


collector_state = CollectorState()
win_router = APIRouter(prefix="/api/v1/windows", tags=["windows-collector"])


class StartCollectorReq(BaseModel):
    project_id: Optional[str] = None
    session_name: str = "Laptop Live Wi-Fi Survey"
    room_label: str = "Laptop Desk"
    x_norm: float = 0.5
    y_norm: float = 0.5
    cadence_sec: float = 5.0


class UpdateMarkerReq(BaseModel):
    room_label: str
    x_norm: float
    y_norm: float


@win_router.get("/capabilities")
def windows_capabilities():
    scan = probe_windows_wifi()
    return {
        "platform": "windows",
        "collector_mode": "hybrid_localhost",
        "adapter_available": scan.get("available", False),
        "adapter_name": scan.get("adapter_name"),
        "adapter_description": scan.get("adapter_description"),
        "os_version": scan.get("os_version"),
        "capabilities": {
            "wifi_quality_percent": True,
            "wifi_rssi_dbm": scan.get("rssi_supported", False),
            "wifi_band_channel": True,
            "active_tcp_probe": True,
            "cellular_radio": False,
            "gps": False,
        },
        "notes": "Windows exposes driver-relative signal quality (%). RSSI dBm is recorded only when directly exposed by the WLAN driver.",
    }


@win_router.get("/live-scan")
def windows_live_scan(include_nearby: bool = False):
    scan = probe_windows_wifi()
    collector_state.last_scan = scan
    nearby = scan_nearby_networks() if include_nearby else []
    return {
        "interface": scan,
        "nearby_networks": nearby,
    }


@win_router.post("/active-probe")
def windows_active_probe(host: str = "1.1.1.1", port: int = 443):
    return run_active_tcp_probe(host=host, port=port)


@win_router.post("/speed-test")
def windows_speed_test():
    return run_active_speed_test()


@win_router.get("/collector/status")
def windows_collector_status():
    return {
        "status": "Recording" if collector_state.recording else "Connected",
        "recording": collector_state.recording,
        "project_id": collector_state.project_id,
        "session_id": collector_state.session_id,
        "room_label": collector_state.room_label,
        "x_norm": collector_state.x_norm,
        "y_norm": collector_state.y_norm,
        "samples_recorded": collector_state.samples_recorded,
        "pending_queue_count": queue.pending_count(),
        "last_scan": collector_state.last_scan,
    }


@win_router.post("/collector/start")
def windows_collector_start(req: StartCollectorReq):
    scan = probe_windows_wifi()
    if not scan.get("available"):
        raise HTTPException(status_code=400, detail="No Windows WLAN adapter detected")

    db = SessionLocal()
    try:
        proj_id = req.project_id
        if not proj_id:
            proj = db.query(Project).first()
            if not proj:
                proj = Project(id=str(uuid.uuid4()), name="Laptop Wi-Fi Survey", map_mode="indoor")
                db.add(proj)
                db.commit()
            proj_id = proj.id

        dev_id = "11111111-1111-4111-8111-111111111102"
        dev = db.query(Device).filter(Device.id == dev_id).first()
        if not dev:
            dev = Device(
                id=dev_id,
                platform="windows",
                model=scan.get("adapter_description") or "Windows Laptop",
                os_version=scan.get("os_version") or "Windows",
                capabilities_json="{}",
            )
            db.add(dev)
            db.commit()

        sess = SurveySession(
            id=str(uuid.uuid4()),
            project_id=proj_id,
            device_id=dev_id,
            name=req.session_name,
            map_mode="indoor",
            status="recording",
        )
        db.add(sess)
        db.commit()
        session_id = sess.id
    finally:
        db.close()

    collector_state.start(
        project_id=proj_id,
        session_id=session_id,
        device_id=dev_id,
        room_label=req.room_label,
        x_norm=req.x_norm,
        y_norm=req.y_norm,
        cadence_sec=req.cadence_sec,
    )
    return windows_collector_status()


@win_router.post("/collector/marker")
def windows_collector_marker(req: UpdateMarkerReq):
    collector_state.room_label = req.room_label
    collector_state.x_norm = max(0.0, min(1.0, req.x_norm))
    collector_state.y_norm = max(0.0, min(1.0, req.y_norm))
    return windows_collector_status()


@win_router.post("/collector/stop")
def windows_collector_stop():
    sess_id = collector_state.session_id
    collector_state.stop()
    if sess_id:
        db = SessionLocal()
        try:
            sess = db.query(SurveySession).filter(SurveySession.id == sess_id).first()
            if sess:
                sess.status = "finished"
                sess.ended_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()
    return windows_collector_status()


def create_hybrid_app() -> FastAPI:
    base_tarang_app.include_router(win_router)

    web_dist = REPO_ROOT / "apps" / "web" / "dist"
    if web_dist.exists():
        assets_dir = web_dist / "assets"
        if assets_dir.exists():
            base_tarang_app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="web-assets")

        @base_tarang_app.get("/{full_path:path}")
        def serve_spa(full_path: str):
            candidate = web_dist / full_path
            if full_path and candidate.is_file():
                return FileResponse(str(candidate))
            return FileResponse(str(web_dist / "index.html"))

    return base_tarang_app


hybrid_app = create_hybrid_app()
