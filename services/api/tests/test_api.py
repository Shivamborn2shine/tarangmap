from datetime import datetime, timezone
import uuid
from fastapi.testclient import TestClient

from app.main import app


def test_health_and_seeded_projects():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        projects = client.get("/api/v1/projects").json()
        assert len(projects) >= 2
        names = [p["name"] for p in projects]
        assert any("Indoor" in n for n in names)


def test_idempotent_batch_ingest():
    with TestClient(app) as client:
        dev = client.post("/api/v1/devices/register", json={
            "platform": "windows",
            "model": "Test Laptop",
            "os_version": "Windows 11",
            "capabilities": {"wifi_quality_percent": True},
        }).json()

        proj = client.post("/api/v1/projects", json={
            "name": "Pytest Idempotency Project",
            "map_mode": "indoor",
        }).json()

        sess = client.post("/api/v1/sessions", json={
            "project_id": proj["id"],
            "device_id": dev["id"],
            "name": "Test Session",
            "map_mode": "indoor",
        }).json()

        obs_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "batch_id": str(uuid.uuid4()),
            "device_id": dev["id"],
            "observations": [
                {
                    "schema_version": 1,
                    "id": obs_id,
                    "session_id": sess["id"],
                    "device_id": dev["id"],
                    "kind": "wifi",
                    "technology": "wifi",
                    "observed_at": now,
                    "recorded_at": now,
                    "metric_source": "windows_netsh_wlan",
                    "freshness_ms": 500,
                    "location_kind": "indoor",
                    "room_label": "Desk",
                    "x_norm": 0.5,
                    "y_norm": 0.5,
                    "wifi": {
                        "ssid": "TestNet",
                        "band": "2.4 GHz",
                        "channel": 6,
                        "quality_percent": 77,
                        "rssi_dbm": None,
                    },
                }
            ],
        }

        r1 = client.post("/api/v1/observations/batch", json=payload)
        assert r1.status_code == 200
        assert r1.json()["accepted"] == 1
        assert r1.json()["duplicate"] == 0

        # Re-upload identical batch -> must deduplicate
        payload["batch_id"] = str(uuid.uuid4())
        r2 = client.post("/api/v1/observations/batch", json=payload)
        assert r2.status_code == 200
        assert r2.json()["accepted"] == 0
        assert r2.json()["duplicate"] == 1

        obs_list = client.get(f"/api/v1/sessions/{sess['id']}/observations").json()
        assert len(obs_list) == 1
        assert obs_list[0]["primary_metric_label"] == "77% signal quality"


def test_summary_and_export():
    with TestClient(app) as client:
        projects = client.get("/api/v1/projects").json()
        indoor = next(p for p in projects if "Indoor" in p["name"])

        summary = client.get(f"/api/v1/projects/{indoor['id']}/summary").json()
        assert summary["total_observations"] >= 10
        assert len(summary["recommendations"]) >= 1

        csv_res = client.get(f"/api/v1/projects/{indoor['id']}/export?format=csv&redact=true")
        assert csv_res.status_code == 200
        assert "[REDACTED]" in csv_res.text

        json_res = client.get(f"/api/v1/projects/{indoor['id']}/export?format=json&redact=true")
        assert json_res.status_code == 200
        assert json_res.json()["schema_version"] == 1
