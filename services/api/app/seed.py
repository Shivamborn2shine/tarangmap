from datetime import datetime, timedelta, timezone
import hashlib
import json
import uuid
from sqlalchemy.orm import Session

from .models import (
    ActiveTest,
    CellObservation,
    Device,
    Floorplan,
    Observation,
    Project,
    SurveySession,
    WifiObservation,
)


def _bssid_hash(project_id: str, raw_bssid: str) -> str:
    return hashlib.sha256(f"{project_id}:{raw_bssid}".encode()).hexdigest()[:16]


def seed_demo_data(db: Session) -> None:
    if db.query(Project).first():
        return

    now = datetime.now(timezone.utc)

    # Devices
    android_dev = Device(
        id="11111111-1111-4111-8111-111111111101",
        platform="android",
        model="Pixel 8 (Demo)",
        os_version="Android 15",
        capabilities_json=json.dumps({
            "wifi_rssi_dbm": True,
            "wifi_frequency_mhz": True,
            "lte_rsrp_rsrq_sinr": True,
            "nr_ss_rsrp": True,
            "gps": True,
        }),
    )
    windows_dev = Device(
        id="11111111-1111-4111-8111-111111111102",
        platform="windows",
        model="ThinkPad / MediaTek Wi-Fi 6",
        os_version="Windows 11 24H2",
        capabilities_json=json.dumps({
            "wifi_quality_percent": True,
            "wifi_rssi_dbm": True,
            "wifi_band_channel": True,
            "cellular_radio": False,
        }),
    )
    db.add_all([android_dev, windows_dev])

    # Project 1: Indoor Home Survey
    p_indoor = Project(
        id="22222222-2222-4222-8222-222222222201",
        name="Shivam's Apartment — Indoor Coverage",
        description="Home Wi-Fi (2.4 GHz & 5 GHz) and LTE/5G indoor floor-plan survey",
        map_mode="indoor",
        created_at=now - timedelta(days=2),
    )
    db.add(p_indoor)

    fp = Floorplan(
        id="33333333-3333-4333-8333-333333333301",
        project_id=p_indoor.id,
        name="Main Apartment Floor Plan",
        image_uri="/samples/demo-indoor-floorplan.svg",
        width_px=1000,
        height_px=640,
        scale_m_per_px=0.015,
    )
    db.add(fp)

    s_indoor_1 = SurveySession(
        id="44444444-4444-4444-8444-444444444401",
        project_id=p_indoor.id,
        device_id=android_dev.id,
        name="Evening Walk — 5 GHz + 5G NR",
        map_mode="indoor",
        status="finished",
        started_at=now - timedelta(hours=18),
        ended_at=now - timedelta(hours=17, minutes=48),
        settings_json=json.dumps({"cadence_sec": 5, "active_probe": True}),
    )
    s_indoor_2 = SurveySession(
        id="44444444-4444-4444-8444-444444444402",
        project_id=p_indoor.id,
        device_id=windows_dev.id,
        name="Laptop Desk & Room Check — 2.4 GHz",
        map_mode="indoor",
        status="finished",
        started_at=now - timedelta(hours=4),
        ended_at=now - timedelta(hours=3, minutes=52),
        settings_json=json.dumps({"cadence_sec": 5, "collector": "windows_netsh"}),
    )
    db.add_all([s_indoor_1, s_indoor_2])

    indoor_points = [
        ("Living Room", 0.42, 0.20, -44, "5 GHz", 5180, 36, -82, "Jio 5G", "nr"),
        ("Living Room", 0.16, 0.28, -52, "5 GHz", 5180, 36, -86, "Jio 5G", "nr"),
        ("Living Room", 0.28, 0.42, -55, "5 GHz", 5180, 36, -88, "Jio 5G", "nr"),
        ("Study", 0.56, 0.22, -59, "5 GHz", 5180, 36, -91, "Jio 5G", "nr"),
        ("Study", 0.64, 0.34, -63, "5 GHz", 5180, 36, -93, "Jio 5G", "nr"),
        ("Hallway", 0.46, 0.68, -64, "5 GHz", 5180, 36, -96, "Jio 5G", "nr"),
        ("Kitchen & Dining", 0.18, 0.72, -69, "5 GHz", 5180, 36, -99, "Jio 5G", "nr"),
        ("Kitchen & Dining", 0.26, 0.84, -72, "5 GHz", 5180, 36, -101, "Jio 5G", "nr"),
        ("Master Bedroom", 0.80, 0.22, -73, "5 GHz", 5180, 36, -95, "Jio 5G", "nr"),
        ("Master Bedroom", 0.88, 0.36, -77, "5 GHz", 5180, 36, -97, "Jio 5G", "nr"),
        ("Balcony", 0.70, 0.72, -81, "5 GHz", 5180, 36, -84, "Jio 5G", "nr"),
        ("Balcony", 0.85, 0.82, -84, "5 GHz", 5180, 36, -81, "Jio 5G", "nr"),
    ]

    for idx, (room, x, y, rssi, band, freq, ch, cell_rsrp, op, tech) in enumerate(indoor_points):
        ts = now - timedelta(hours=18) + timedelta(seconds=idx * 25)
        w_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tarang-indoor-w-{idx}"))
        db.add(Observation(
            id=w_id,
            session_id=s_indoor_1.id,
            device_id=android_dev.id,
            kind="wifi",
            technology="wifi",
            observed_at=ts,
            recorded_at=ts,
            received_at=ts + timedelta(seconds=1),
            metric_source="android_wifi_manager",
            freshness_ms=1200,
            location_kind="indoor",
            room_label=room,
            x_norm=x,
            y_norm=y,
        ))
        db.add(WifiObservation(
            observation_id=w_id,
            ssid="TarangHome_5G",
            bssid_hash=_bssid_hash(p_indoor.id, "aa:bb:cc:dd:ee:01"),
            frequency_mhz=freq,
            band=band,
            channel=ch,
            rssi_dbm=rssi,
            rx_mbps=433.0 if rssi > -65 else 173.0,
            tx_mbps=390.0 if rssi > -65 else 144.0,
            radio_type="802.11ax",
        ))

        c_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tarang-indoor-c-{idx}"))
        db.add(Observation(
            id=c_id,
            session_id=s_indoor_1.id,
            device_id=android_dev.id,
            kind="cellular",
            technology=tech,
            observed_at=ts,
            recorded_at=ts,
            received_at=ts + timedelta(seconds=1),
            metric_source="android_telephony_manager",
            freshness_ms=1500,
            location_kind="indoor",
            room_label=room,
            x_norm=x,
            y_norm=y,
        ))
        db.add(CellObservation(
            observation_id=c_id,
            operator_name=op,
            tech="NR",
            registered=True,
            ss_rsrp_dbm=cell_rsrp,
            ss_rsrq_db=-10 if cell_rsrp > -95 else -13,
            ss_sinr_db=16 if cell_rsrp > -90 else 8,
            pci=214,
            tac=4102,
            band="n78 (3500 MHz)",
        ))

    # Active test showing strong signal vs latency in Balcony
    at_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "tarang-indoor-at-1"))
    db.add(Observation(
        id=at_id,
        session_id=s_indoor_1.id,
        device_id=android_dev.id,
        kind="active_test",
        technology="wifi",
        observed_at=now - timedelta(hours=17, minutes=50),
        recorded_at=now - timedelta(hours=17, minutes=50),
        received_at=now - timedelta(hours=17, minutes=50),
        metric_source="tarang_active_probe",
        freshness_ms=200,
        location_kind="indoor",
        room_label="Balcony",
        x_norm=0.85,
        y_norm=0.82,
    ))
    db.add(ActiveTest(
        observation_id=at_id,
        endpoint="1.1.1.1:443",
        latency_ms=118.4,
        jitter_ms=22.5,
        packet_loss_pct=2.5,
        bytes_used=4096,
    ))

    # Laptop 2.4 GHz session
    laptop_points = [
        ("Living Room", 0.35, 0.25, -48, 92),
        ("Study", 0.58, 0.24, -56, 81),
        ("Hallway", 0.45, 0.62, -61, 74),
        ("Master Bedroom", 0.82, 0.28, -68, 62),
        ("Balcony", 0.78, 0.74, -73, 51),
    ]
    for idx, (room, x, y, rssi, qual) in enumerate(laptop_points):
        ts = now - timedelta(hours=4) + timedelta(seconds=idx * 30)
        lw_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tarang-laptop-w-{idx}"))
        db.add(Observation(
            id=lw_id,
            session_id=s_indoor_2.id,
            device_id=windows_dev.id,
            kind="wifi",
            technology="wifi",
            observed_at=ts,
            recorded_at=ts,
            received_at=ts + timedelta(seconds=1),
            metric_source="windows_netsh_wlan",
            freshness_ms=900,
            location_kind="indoor",
            room_label=room,
            x_norm=x,
            y_norm=y,
        ))
        db.add(WifiObservation(
            observation_id=lw_id,
            ssid="TarangHome_2.4G",
            bssid_hash=_bssid_hash(p_indoor.id, "aa:bb:cc:dd:ee:02"),
            frequency_mhz=2437,
            band="2.4 GHz",
            channel=6,
            rssi_dbm=rssi,
            quality_percent=qual,
            rx_mbps=144.4,
            tx_mbps=144.4,
            radio_type="802.11n",
        ))

    # Project 2: Outdoor Campus / Neighborhood Walk
    p_outdoor = Project(
        id="22222222-2222-4222-8222-222222222202",
        name="Campus Perimeter — Outdoor LTE/5G Walk",
        description="Outdoor GPS-tagged cellular (Jio 5G vs Airtel LTE) and campus Wi-Fi walk",
        map_mode="outdoor",
        created_at=now - timedelta(days=1),
    )
    db.add(p_outdoor)

    s_outdoor = SurveySession(
        id="44444444-4444-4444-8444-444444444403",
        project_id=p_outdoor.id,
        device_id=android_dev.id,
        name="Morning Loop — North Gate to Library",
        map_mode="outdoor",
        status="finished",
        started_at=now - timedelta(hours=10),
        ended_at=now - timedelta(hours=9, minutes=35),
        settings_json=json.dumps({"cadence_sec": 5, "gps_min_accuracy_m": 20}),
    )
    db.add(s_outdoor)

    outdoor_pts = [
        (28.6139, 77.2090, 6.2, -79, "Jio", "nr"),
        (28.6143, 77.2096, 7.5, -84, "Jio", "nr"),
        (28.6148, 77.2102, 8.1, -92, "Jio", "nr"),
        (28.6152, 77.2109, 11.4, -101, "Jio", "nr"),
        (28.6157, 77.2114, 24.5, -109, "Jio", "nr"),
        (28.6153, 77.2121, 9.0, -96, "Airtel", "lte"),
        (28.6147, 77.2118, 6.8, -89, "Airtel", "lte"),
        (28.6141, 77.2110, 5.4, -83, "Airtel", "lte"),
    ]
    for idx, (lat, lon, acc, rsrp, op, tech) in enumerate(outdoor_pts):
        ts = now - timedelta(hours=10) + timedelta(seconds=idx * 45)
        oc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"tarang-outdoor-c-{idx}"))
        db.add(Observation(
            id=oc_id,
            session_id=s_outdoor.id,
            device_id=android_dev.id,
            kind="cellular",
            technology=tech,
            observed_at=ts,
            recorded_at=ts,
            received_at=ts + timedelta(seconds=1),
            metric_source="android_telephony_manager",
            freshness_ms=1100,
            location_kind="outdoor",
            lat=lat,
            lon=lon,
            gps_accuracy_m=acc,
        ))
        if tech == "nr":
            db.add(CellObservation(
                observation_id=oc_id,
                operator_name=op,
                tech="NR",
                registered=True,
                ss_rsrp_dbm=rsrp,
                ss_rsrq_db=-11,
                ss_sinr_db=14 if rsrp > -95 else 5,
                pci=108,
                tac=3021,
                band="n78",
            ))
        else:
            db.add(CellObservation(
                observation_id=oc_id,
                operator_name=op,
                tech="LTE",
                registered=True,
                rsrp_dbm=rsrp,
                rsrq_db=-9,
                sinr_db=12,
                pci=412,
                tac=3021,
                band="B3 (1800 MHz)",
            ))

    db.commit()
