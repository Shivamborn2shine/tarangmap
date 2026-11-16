from collections import defaultdict
from statistics import median
from typing import Any

from .models import Observation


def classify_wifi_rssi(rssi: int | None) -> str:
    if rssi is None:
        return "Unavailable"
    if rssi >= -55:
        return "Strong"
    if rssi >= -67:
        return "Good"
    if rssi >= -75:
        return "Fair"
    return "Weak"


def classify_wifi_quality(quality_pct: int | None) -> str:
    if quality_pct is None:
        return "Unavailable"
    if quality_pct >= 80:
        return "Strong"
    if quality_pct >= 60:
        return "Good"
    if quality_pct >= 40:
        return "Fair"
    return "Weak"


def classify_lte_rsrp(rsrp: int | None) -> str:
    if rsrp is None:
        return "Unavailable"
    if rsrp >= -85:
        return "Strong"
    if rsrp >= -98:
        return "Good"
    if rsrp >= -110:
        return "Fair"
    return "Weak"


def classify_nr_ss_rsrp(ss_rsrp: int | None) -> str:
    if ss_rsrp is None:
        return "Unavailable"
    if ss_rsrp >= -85:
        return "Strong"
    if ss_rsrp >= -98:
        return "Good"
    if ss_rsrp >= -110:
        return "Fair"
    return "Weak"


def classify_observation(obs: Observation) -> tuple[str, str]:
    """Return (signal_tier, primary_metric_label) without inventing missing values."""
    if obs.kind == "wifi" and obs.wifi:
        if obs.wifi.rssi_dbm is not None:
            return classify_wifi_rssi(obs.wifi.rssi_dbm), f"{obs.wifi.rssi_dbm} dBm Wi-Fi RSSI"
        if obs.wifi.quality_percent is not None:
            return classify_wifi_quality(obs.wifi.quality_percent), f"{obs.wifi.quality_percent}% signal quality"
        return "Unavailable", "Wi-Fi metric unavailable"

    if obs.kind == "cellular" and obs.cellular:
        if obs.technology == "nr" and obs.cellular.ss_rsrp_dbm is not None:
            return classify_nr_ss_rsrp(obs.cellular.ss_rsrp_dbm), f"{obs.cellular.ss_rsrp_dbm} dBm 5G SS-RSRP"
        if obs.cellular.rsrp_dbm is not None:
            return classify_lte_rsrp(obs.cellular.rsrp_dbm), f"{obs.cellular.rsrp_dbm} dBm LTE RSRP"
        return "Unavailable", "Cellular metric unavailable"

    if obs.kind == "active_test" and obs.active_test:
        lat = obs.active_test.latency_ms
        loss = obs.active_test.packet_loss_pct or 0.0
        if lat is None:
            return "Unavailable", "Active probe unavailable"
        if lat < 35 and loss < 1.0:
            return "Strong", f"{lat:.1f} ms latency"
        if lat < 75 and loss < 2.0:
            return "Good", f"{lat:.1f} ms latency"
        if lat < 140 and loss < 5.0:
            return "Fair", f"{lat:.1f} ms latency"
        return "Weak", f"{lat:.1f} ms latency ({loss:.1f}% loss)"

    return "Unavailable", "Unavailable"


def build_project_summary(observations: list[Observation]) -> dict[str, Any]:
    wifi_tiers = defaultdict(int)
    cell_tiers = defaultdict(int)
    wifi_rssi_values: list[int] = []
    wifi_quality_values: list[int] = []
    lte_rsrp_values: list[int] = []
    nr_rsrp_values: list[int] = []
    room_wifi: dict[str, list[int]] = defaultdict(list)
    band_wifi: dict[str, list[int]] = defaultdict(list)
    operator_cell: dict[str, list[int]] = defaultdict(list)
    active_issues: list[Observation] = []
    uncertain_gps_count = 0

    for obs in observations:
        tier, _ = classify_observation(obs)
        if obs.location_kind == "outdoor" and obs.gps_accuracy_m is not None and obs.gps_accuracy_m > 20.0:
            uncertain_gps_count += 1

        if obs.kind == "wifi" and obs.wifi:
            wifi_tiers[tier] += 1
            if obs.wifi.rssi_dbm is not None:
                wifi_rssi_values.append(obs.wifi.rssi_dbm)
                area = obs.room_label or "Unlabeled area"
                room_wifi[area].append(obs.wifi.rssi_dbm)
                if obs.wifi.band:
                    band_wifi[obs.wifi.band].append(obs.wifi.rssi_dbm)
            if obs.wifi.quality_percent is not None:
                wifi_quality_values.append(obs.wifi.quality_percent)
        elif obs.kind == "cellular" and obs.cellular:
            cell_tiers[tier] += 1
            op = obs.cellular.operator_name or "Unknown operator"
            if obs.technology == "nr" and obs.cellular.ss_rsrp_dbm is not None:
                nr_rsrp_values.append(obs.cellular.ss_rsrp_dbm)
                operator_cell[f"{op} (5G NR)"].append(obs.cellular.ss_rsrp_dbm)
            elif obs.cellular.rsrp_dbm is not None:
                lte_rsrp_values.append(obs.cellular.rsrp_dbm)
                operator_cell[f"{op} (LTE)"].append(obs.cellular.rsrp_dbm)
        elif obs.kind == "active_test" and obs.active_test:
            if (obs.active_test.latency_ms or 0) > 100 or (obs.active_test.packet_loss_pct or 0) >= 2.0:
                active_issues.append(obs)

    weak_spots = []
    for area, values in room_wifi.items():
        med = median(values)
        tier = classify_wifi_rssi(int(round(med)))
        if tier in ("Weak", "Fair"):
            weak_spots.append({
                "area": area,
                "metric": "Wi-Fi RSSI",
                "median_value": round(med, 1),
                "unit": "dBm",
                "tier": tier,
                "sample_count": len(values),
                "confidence": "High" if len(values) >= 5 else "Moderate" if len(values) >= 3 else "Low (few samples)",
            })
    weak_spots.sort(key=lambda x: x["median_value"])

    recommendations = []

    # Rule A: Repeated weak Wi-Fi RSSI readings
    if weak_spots:
        worst = weak_spots[0]
        recommendations.append({
            "rule": "Rule A",
            "title": f"Possible coverage gap in {worst['area']}",
            "finding": f"{worst['area']} recorded {worst['tier'].lower()} Wi-Fi signal (median {worst['median_value']} dBm).",
            "evidence": f"Based on {worst['sample_count']} Wi-Fi RSSI observations in {worst['area']}.",
            "confidence": worst["confidence"],
            "suggested_test": "Try measuring a second router position or a 2.4 GHz vs 5 GHz pass in this room before relocating hardware.",
        })

    # Rule B: High latency/packet loss despite active test
    if active_issues:
        sample = active_issues[0]
        recommendations.append({
            "rule": "Rule B",
            "title": "Connectivity issue detected in active probe",
            "finding": f"Observed {sample.active_test.latency_ms:.0f} ms latency and {sample.active_test.packet_loss_pct or 0:.1f}% loss to {sample.active_test.endpoint}.",
            "evidence": f"{len(active_issues)} active probe(s) exceeded 100 ms latency or 2% packet loss.",
            "confidence": "Moderate",
            "suggested_test": "Run an active probe next to the router to isolate ISP/backhaul congestion from radio signal attenuation.",
        })

    # Rule C: Band comparison (2.4 GHz vs 5 GHz)
    if "2.4 GHz" in band_wifi and "5 GHz" in band_wifi:
        med_24 = median(band_wifi["2.4 GHz"])
        med_5 = median(band_wifi["5 GHz"])
        recommendations.append({
            "rule": "Rule C",
            "title": "2.4 GHz vs 5 GHz propagation difference",
            "finding": f"2.4 GHz median is {med_24:.1f} dBm vs 5 GHz median {med_5:.1f} dBm.",
            "evidence": f"{len(band_wifi['2.4 GHz'])} samples on 2.4 GHz and {len(band_wifi['5 GHz'])} samples on 5 GHz.",
            "confidence": "High" if min(len(band_wifi["2.4 GHz"]), len(band_wifi["5 GHz"])) >= 4 else "Moderate",
            "suggested_test": "Test throughput on 5 GHz in rooms where RSSI is above -70 dBm; use 2.4 GHz only where 5 GHz drops below -75 dBm.",
        })

    # Rule E: Operator comparison
    if len(operator_cell) >= 2:
        ops_summary = ", ".join(
            f"{k}: {median(v):.0f} dBm ({len(v)} pts)" for k, v in operator_cell.items()
        )
        recommendations.append({
            "rule": "Rule E",
            "title": "Multi-operator cellular comparison available",
            "finding": f"Observed cellular medians: {ops_summary}.",
            "evidence": "Comparing compatible RSRP/SS-RSRP readings across operators.",
            "confidence": "Moderate (verify same device/time-of-day)",
            "suggested_test": "Use the Compare view to check overlapping locations on the same hardware before switching carriers.",
        })

    if not recommendations:
        recommendations.append({
            "rule": "Baseline",
            "title": "Coverage looks healthy across surveyed points",
            "finding": "No major weak spots or high-latency probes flagged in current observations.",
            "evidence": f"{len(observations)} total observations evaluated.",
            "confidence": "High" if len(observations) >= 10 else "Low (collect more points)",
            "suggested_test": "Walk outer corners or run an active latency probe during peak evening hours to stress-test coverage.",
        })

    return {
        "total_observations": len(observations),
        "measured_areas_count": len(room_wifi),
        "typical_wifi_rssi_dbm": round(median(wifi_rssi_values), 1) if wifi_rssi_values else None,
        "typical_wifi_quality_pct": round(median(wifi_quality_values), 1) if wifi_quality_values else None,
        "typical_lte_rsrp_dbm": round(median(lte_rsrp_values), 1) if lte_rsrp_values else None,
        "typical_nr_ss_rsrp_dbm": round(median(nr_rsrp_values), 1) if nr_rsrp_values else None,
        "uncertain_gps_count": uncertain_gps_count,
        "wifi_tier_distribution": dict(wifi_tiers),
        "cellular_tier_distribution": dict(cell_tiers),
        "weak_spots": weak_spots,
        "recommendations": recommendations,
    }
