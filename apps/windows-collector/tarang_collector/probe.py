from datetime import datetime, timezone
import hashlib
import platform
import re
import socket
import subprocess
import time
from typing import Any


def _run_netsh(args: list[str]) -> str:
    try:
        res = subprocess.run(
            ["netsh", "wlan", *args],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return res.stdout or ""
    except Exception:
        return ""


def _parse_kv_lines(output: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            parsed[k.strip().lower()] = v.strip()
    return parsed


def _band_to_freq(band_str: str | None, channel: int | None) -> int | None:
    if channel is None:
        return None
    if band_str and "5" in band_str:
        return 5000 + channel * 5
    if band_str and "6" in band_str:
        return 5950 + channel * 5
    if 1 <= channel <= 13:
        return 2407 + channel * 5
    if channel == 14:
        return 2484
    if channel >= 32:
        return 5000 + channel * 5
    return None


def probe_windows_wifi() -> dict[str, Any]:
    """Read real Windows WLAN interface state via netsh. Never fabricates RSSI from %."""
    now = datetime.now(timezone.utc)
    raw = _run_netsh(["show", "interfaces"])
    kv = _parse_kv_lines(raw)

    if not kv or "state" not in kv:
        return {
            "available": False,
            "observed_at": now.isoformat(),
            "adapter_name": None,
            "adapter_description": None,
            "state": "unavailable",
            "missing_reason": "No Windows WLAN interface found or WLAN AutoConfig service stopped",
            "os_version": f"Windows {platform.release()} ({platform.version()})",
        }

    state = kv.get("state", "disconnected").lower()
    quality_match = re.search(r"(\d+)\s*%", kv.get("signal", ""))
    quality_pct = int(quality_match.group(1)) if quality_match else None

    rssi_raw = kv.get("rssi")
    rssi_dbm = None
    if rssi_raw:
        m = re.search(r"(-?\d+)", rssi_raw)
        if m:
            rssi_dbm = int(m.group(1))

    channel = int(kv["channel"]) if kv.get("channel", "").isdigit() else None
    band = kv.get("band")
    freq_mhz = _band_to_freq(band, channel)

    rx_mbps = None
    tx_mbps = None
    for key, target in [("receive rate (mbps)", "rx"), ("transmit rate (mbps)", "tx")]:
        if key in kv:
            try:
                val = float(kv[key])
                if target == "rx":
                    rx_mbps = val
                else:
                    tx_mbps = val
            except ValueError:
                pass

    bssid_raw = kv.get("ap bssid") or kv.get("bssid")
    bssid_hash = (
        hashlib.sha256(bssid_raw.encode()).hexdigest()[:16] if bssid_raw else None
    )

    return {
        "available": True,
        "observed_at": now.isoformat(),
        "os_version": f"Windows {platform.release()} ({platform.version()})",
        "adapter_name": kv.get("name"),
        "adapter_description": kv.get("description"),
        "state": state,
        "ssid": kv.get("ssid") if state == "connected" else None,
        "bssid_hash": bssid_hash,
        "band": band,
        "channel": channel,
        "frequency_mhz": freq_mhz,
        "radio_type": kv.get("radio type"),
        "authentication": kv.get("authentication"),
        "quality_percent": quality_pct,
        "rssi_dbm": rssi_dbm,
        "rssi_supported": rssi_dbm is not None,
        "rx_mbps": rx_mbps,
        "tx_mbps": tx_mbps,
        "metric_source": "windows_netsh_wlan",
        "missing_reason": None if rssi_dbm is not None else "Driver exposes signal quality % only (no direct RSSI dBm)",
    }


def scan_nearby_networks() -> list[dict[str, Any]]:
    raw = _run_netsh(["show", "networks", "mode=bssid"])
    networks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("SSID ") and ":" in s:
            if current:
                networks.append(current)
            ssid_val = s.split(":", 1)[1].strip()
            current = {"ssid": ssid_val or "(Hidden)", "bssids": []}
        elif current and s.startswith("Network type") and ":" in s:
            current["network_type"] = s.split(":", 1)[1].strip()
        elif current and s.startswith("Authentication") and ":" in s:
            current["authentication"] = s.split(":", 1)[1].strip()
        elif current and s.startswith("BSSID ") and ":" in s:
            bssid = s.split(":", 1)[1].strip()
            current["bssids"].append({"bssid_hash": hashlib.sha256(bssid.encode()).hexdigest()[:12]})
        elif current and s.startswith("Signal") and ":" in s and current["bssids"]:
            m = re.search(r"(\d+)\s*%", s.split(":", 1)[1])
            if m:
                current["bssids"][-1]["quality_percent"] = int(m.group(1))
        elif current and s.startswith("Channel") and ":" in s and current["bssids"]:
            ch = s.split(":", 1)[1].strip()
            if ch.isdigit():
                current["bssids"][-1]["channel"] = int(ch)
    if current:
        networks.append(current)
    return networks


def run_active_tcp_probe(host: str = "1.1.1.1", port: int = 443, samples: int = 4) -> dict[str, Any]:
    latencies: list[float] = []
    failures = 0
    for _ in range(samples):
        t0 = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=2.0):
                dt = (time.perf_counter() - t0) * 1000.0
                latencies.append(dt)
        except OSError:
            failures += 1
        time.sleep(0.08)

    if not latencies:
        return {
            "endpoint": f"{host}:{port}",
            "latency_ms": None,
            "jitter_ms": None,
            "packet_loss_pct": 100.0,
            "bytes_used": 0,
        }

    avg_lat = sum(latencies) / len(latencies)
    jitter = (
        sum(abs(latencies[i] - latencies[i - 1]) for i in range(1, len(latencies))) / max(len(latencies) - 1, 1)
    )
    loss_pct = (failures / samples) * 100.0
    return {
        "endpoint": f"{host}:{port}",
        "latency_ms": round(avg_lat, 2),
        "jitter_ms": round(jitter, 2),
        "packet_loss_pct": round(loss_pct, 1),
        "bytes_used": len(latencies) * 128,
    }


def run_active_speed_test(download_bytes: int = 5_000_000, upload_bytes: int = 1_500_000) -> dict[str, Any]:
    """Opt-in active internet throughput test (distinct from local Wi-Fi PHY link rate)."""
    import httpx

    dl_mbps = None
    ul_mbps = None
    bytes_used = 0
    endpoint = "speed.cloudflare.com"

    try:
        with httpx.Client(timeout=12.0, follow_redirects=True) as client:
            t0 = time.perf_counter()
            dl_total = 0
            with client.stream("GET", f"https://{endpoint}/__down?bytes={download_bytes}") as resp:
                resp.raise_for_status()
                for chunk in resp.iter_bytes(chunk_size=65536):
                    dl_total += len(chunk)
            dl_sec = max(time.perf_counter() - t0, 0.001)
            dl_mbps = round((dl_total * 8) / (dl_sec * 1_000_000), 2)
            bytes_used += dl_total

            payload = b"0" * upload_bytes
            t1 = time.perf_counter()
            ul_resp = client.post(f"https://{endpoint}/__up", content=payload)
            ul_resp.raise_for_status()
            ul_sec = max(time.perf_counter() - t1, 0.001)
            ul_mbps = round((upload_bytes * 8) / (ul_sec * 1_000_000), 2)
            bytes_used += upload_bytes
    except Exception as exc:
        return {
            "endpoint": endpoint,
            "download_mbps": dl_mbps,
            "upload_mbps": ul_mbps,
            "bytes_used": bytes_used,
            "error": str(exc),
        }

    return {
        "endpoint": endpoint,
        "download_mbps": dl_mbps,
        "upload_mbps": ul_mbps,
        "bytes_used": bytes_used,
        "error": None,
    }
