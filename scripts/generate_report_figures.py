from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "report_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NAVY = "#102A43"
TEAL = "#087F8C"
BLUE = "#3978CF"
GREEN = "#168A5B"
AMBER = "#D99C26"
CORAL = "#D95D54"
BG = "#F7FAFC"
CARD = "#FFFFFF"
BORDER = "#CBD5E1"
MUTED = "#486581"


def _font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf" if not bold else "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf" if not bold else "C:/Windows/Fonts/arialbd.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _box(draw: ImageDraw.ImageDraw, xy, title: str, subtitle: str, accent=TEAL):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=14, fill=CARD, outline=accent, width=3)
    draw.text((x1 + 18, y1 + 14), title, fill=NAVY, font=_font(20, True))
    draw.text((x1 + 18, y1 + 44), subtitle, fill=MUTED, font=_font(15, False))


def _arrow(draw: ImageDraw.ImageDraw, p1, p2, label: str = ""):
    draw.line([p1, p2], fill=NAVY, width=3)
    x2, y2 = p2
    draw.polygon([(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)], fill=NAVY)
    if label:
        mx, my = (p1[0] + x2) // 2, (p1[1] + y2) // 2
        draw.text((mx - 42, my - 24), label, fill=TEAL, font=_font(15, True))


def make_architecture():
    img = Image.new("RGB", (1200, 620), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 28), "Figure 3.1: TARANG Hybrid Local-First System Architecture", fill=NAVY, font=_font(26, True))

    _box(d, (50, 110, 390, 250), "Windows Laptop Hybrid App", "netsh wlan + SQLite Queue\nLocalhost Bridge (127.0.0.1:8765)", TEAL)
    _box(d, (50, 320, 390, 460), "Android Collector (Kotlin)", "WifiManager + TelephonyManager\nRoom Offline Queue + FGS", BLUE)

    _box(d, (460, 190, 780, 380), "FastAPI REST Core (v1)", "Idempotent /observations/batch\nRules Engine (Rules A-E)\nSQLAlchemy 2 + SQLite / PostGIS", NAVY)

    _box(d, (850, 110, 1150, 250), "React + TS Dashboard", "Vercel / Netlify / Localhost\nIndoor Floor Plan & Map Explorer", TEAL)
    _box(d, (850, 320, 1150, 460), "Exports & Comparisons", "Redacted CSV / JSON v1\nSession Comparison Caveats", GREEN)

    _arrow(d, (390, 180), (460, 250), "Local Sync")
    _arrow(d, (390, 390), (460, 320), "Batch JSON")
    _arrow(d, (780, 250), (850, 180), "REST JSON")
    _arrow(d, (780, 320), (850, 390), "CSV / JSON")

    d.text((50, 540), "Privacy Principle: Local-first by default; no forced cloud login; BSSID/SSID/GPS redaction supported on export.", fill=MUTED, font=_font(16))
    img.save(OUT_DIR / "fig_architecture.png")


def make_dfd():
    img = Image.new("RGB", (1200, 500), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 28), "Figure 2.1: Level 0 & Level 1 Data Flow — Radio Collection to Insights", fill=NAVY, font=_font(26, True))

    _box(d, (40, 140, 280, 300), "1. Radio Probe", "Windows netsh wlan\nAndroid Wifi/Cell\nActive TCP Probe", TEAL)
    _box(d, (340, 140, 590, 300), "2. Offline Queue", "SQLite / Room DB\nUUIDv4 Idempotency\nFreshness & Source", BLUE)
    _box(d, (650, 140, 900, 300), "3. Classifier & Rules", "Strong / Good / Fair / Weak\nRules A-E Insights\nNo Fabricated Values", AMBER)
    _box(d, (950, 140, 1160, 300), "4. Visualization", "Floor Plan & GPS Grid\nBounded Heatmap\nRedacted Exports", GREEN)

    _arrow(d, (280, 220), (340, 220))
    _arrow(d, (590, 220), (650, 220))
    _arrow(d, (900, 220), (950, 220))

    d.text((40, 390), "Honesty Rule: Windows signal quality (%) is never converted to fabricated RSSI dBm; unavailable radios report Unavailable.", fill=MUTED, font=_font(16))
    img.save(OUT_DIR / "fig_dfd.png")


def make_er_schema():
    img = Image.new("RGB", (1200, 660), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 3.2: Canonical Relational & Geospatial Database Schema (v1)", fill=NAVY, font=_font(25, True))

    _box(d, (40, 90, 330, 220), "projects", "PK id, name, map_mode\ncreated_at", NAVY)
    _box(d, (40, 270, 330, 400), "floorplans", "PK id, FK project_id\nimage_uri, width_px, height_px", TEAL)
    _box(d, (420, 90, 740, 220), "sessions", "PK id, FK project_id, device_id\nstatus, started_at, ended_at", BLUE)
    _box(d, (830, 90, 1150, 220), "devices", "PK id, platform, model\nos_version, capabilities_json", NAVY)
    _box(d, (420, 280, 740, 450), "observations", "PK id (UUID), FK session_id\nkind, technology, freshness_ms\nlocation_kind, x_norm, y_norm, lat, lon", TEAL)
    _box(d, (40, 490, 360, 620), "wifi_observations", "PK/FK observation_id, ssid\nbssid_hash, band, rssi_dbm, quality_%", GREEN)
    _box(d, (420, 490, 740, 620), "cell_observations", "PK/FK observation_id, operator\ntech, rsrp_dbm, ss_rsrp_dbm, sinr_db", AMBER)
    _box(d, (800, 490, 1150, 620), "active_tests & sync_batches", "endpoint, latency_ms, jitter_ms\nbatch_id, accepted/duplicate counts", CORAL)

    d.line([(330, 155), (420, 155)], fill=NAVY, width=3)
    d.line([(185, 220), (185, 270)], fill=NAVY, width=3)
    d.line([(740, 155), (830, 155)], fill=NAVY, width=3)
    d.line([(580, 220), (580, 280)], fill=NAVY, width=3)
    d.line([(480, 450), (200, 490)], fill=NAVY, width=2)
    d.line([(580, 450), (580, 490)], fill=NAVY, width=2)
    d.line([(680, 450), (960, 490)], fill=NAVY, width=2)

    img.save(OUT_DIR / "fig_er_schema.png")


def make_sequence():
    img = Image.new("RGB", (1200, 600), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 6.0: End-to-End Sequence — Windows Hybrid Survey & Speed Test", fill=NAVY, font=_font(25, True))

    actors = [("User / Browser", 130), ("React UI (8765)", 420), ("Hybrid Server", 730), ("netsh / SQLite", 1040)]
    for name, cx in actors:
        d.rounded_rectangle([cx - 105, 80, cx + 105, 130], radius=10, fill=CARD, outline=NAVY, width=2)
        d.text((cx - 80, 95), name, fill=NAVY, font=_font(18, True))
        d.line([(cx, 130), (cx, 550)], fill=BORDER, width=2)

    steps = [
        (170, 130, 420, "1. Click 'Start Survey' & Tap Room", TEAL),
        (235, 420, 730, "2. POST /api/v1/windows/collector/start", BLUE),
        (300, 730, 1040, "3. Poll netsh wlan show interfaces (5s)", NAVY),
        (365, 1040, 730, "4. Enqueue & Flush to SQLite DB (UUIDv4)", GREEN),
        (430, 420, 730, "5. GET /live-scan (no-store) & POST /speed-test", AMBER),
        (495, 730, 130, "6. Render Live RSSI/Quality + Floor Plan Pin", TEAL),
    ]
    for y, x1, x2, lbl, col in steps:
        d.line([(x1, y), (x2, y)], fill=col, width=3)
        dir_sign = 1 if x2 > x1 else -1
        d.polygon([(x2, y), (x2 - 10 * dir_sign, y - 6), (x2 - 10 * dir_sign, y + 6)], fill=col)
        d.text((min(x1, x2) + 25, y - 24), lbl, fill=NAVY, font=_font(16, True))

    img.save(OUT_DIR / "fig_sequence.png")


def make_rules_pipeline():
    img = Image.new("RGB", (1200, 480), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 4.1: Rules-Based Optimization Engine (Rules A–E)", fill=NAVY, font=_font(25, True))

    rules = [
        ("Rule A: Coverage Gap", "Median Wi-Fi < -68 dBm\nin an area -> Flag Weak Spot", CORAL, 50),
        ("Rule B: Backhaul vs RF", "Latency > 100ms or Loss >= 2%\n-> Isolate ISP vs Wi-Fi", AMBER, 330),
        ("Rule C: Band Comparison", "2.4 GHz vs 5 GHz medians\n-> Recommend band per room", BLUE, 610),
        ("Rule E: Operator Diff", "Jio 5G vs Airtel LTE\n-> Warn on hardware caveats", GREEN, 890),
    ]
    for title, sub, col, x in rules:
        _box(d, (x, 120, x + 260, 320), title, sub, col)

    d.text((50, 390), "Output Format: Every recommendation strictly reports Finding -> Evidence -> Confidence -> Suggested Next Test.", fill=MUTED, font=_font(17, True))
    img.save(OUT_DIR / "fig_rules_pipeline.png")


def make_signal_chart():
    img = Image.new("RGB", (1200, 520), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 28), "Figure 7.1: Seeded Apartment Indoor Wi-Fi RSSI by Room (5 GHz vs 2.4 GHz)", fill=NAVY, font=_font(24, True))

    rooms = [
        ("Living Room", -48, GREEN),
        ("Study", -61, BLUE),
        ("Hallway", -64, BLUE),
        ("Kitchen", -70, AMBER),
        ("Master Bed", -75, AMBER),
        ("Balcony", -82, CORAL),
    ]
    base_y = 430
    x = 90
    for name, rssi, col in rooms:
        h = max(30, int((100 + rssi) * 5.2))
        d.rounded_rectangle([x, base_y - h, x + 120, base_y], radius=8, fill=col)
        d.text((x + 22, base_y - h - 28), f"{rssi} dBm", fill=NAVY, font=_font(17, True))
        d.text((x + 12, base_y + 12), name, fill=NAVY, font=_font(16, False))
        x += 180

    d.line([(60, base_y), (1140, base_y)], fill=NAVY, width=2)
    img.save(OUT_DIR / "fig_signal_chart.png")


def make_band_comparison():
    img = Image.new("RGB", (1200, 500), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 7.2: 2.4 GHz (Windows Laptop) vs 5 GHz (Android) Propagation by Room", fill=NAVY, font=_font(24, True))

    rooms = [
        ("Living Room", -48, -44),
        ("Study", -56, -61),
        ("Hallway", -61, -64),
        ("Master Bed", -68, -75),
        ("Balcony", -73, -82),
    ]
    base_y = 410
    x = 95
    for name, r24, r5 in rooms:
        h24 = max(30, int((100 + r24) * 4.8))
        h5 = max(30, int((100 + r5) * 4.8))
        d.rounded_rectangle([x, base_y - h24, x + 55, base_y], radius=6, fill=TEAL)
        d.rounded_rectangle([x + 65, base_y - h5, x + 120, base_y], radius=6, fill=BLUE)
        d.text((x + 2, base_y - h24 - 24), f"{r24}", fill=TEAL, font=_font(15, True))
        d.text((x + 67, base_y - h5 - 24), f"{r5}", fill=BLUE, font=_font(15, True))
        d.text((x + 8, base_y + 12), name, fill=NAVY, font=_font(16, False))
        x += 210

    d.line([(60, base_y), (1140, base_y)], fill=NAVY, width=2)
    d.text((80, 455), "Teal = 2.4 GHz (better wall penetration)   |   Blue = 5 GHz (higher peak throughput, steeper attenuation)", fill=MUTED, font=_font(16, True))
    img.save(OUT_DIR / "fig_band_comparison.png")


def make_test_breakdown():
    img = Image.new("RGB", (1200, 460), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 7.3: Automated Verification & Build Checks (100% Passing)", fill=NAVY, font=_font(24, True))

    checks = [
        ("Pytest API Suite (3/3)", 100, GREEN, 110),
        ("TypeScript & Vite Build", 100, TEAL, 190),
        ("Windows netsh Probe", 100, BLUE, 270),
        ("Hybrid Bridge (127.0.0.1:8765)", 100, GREEN, 350),
    ]
    for label, pct, col, y in checks:
        d.text((50, y + 8), label, fill=NAVY, font=_font(18, True))
        d.rounded_rectangle([420, y, 1080, y + 40], radius=10, fill="#E2E8F0")
        d.rounded_rectangle([420, y, 1080, y + 40], radius=10, fill=col)
        d.text((1095, y + 8), f"{pct}%", fill=NAVY, font=_font(18, True))

    img.save(OUT_DIR / "fig_test_breakdown.png")


def make_phy_vs_isp():
    img = Image.new("RGB", (1200, 500), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 4.2: Why Wi-Fi PHY Link Rate (144.4 Mbps) != Internet Speed (29.84 Mbps)", fill=NAVY, font=_font(23, True))

    _box(d, (50, 130, 340, 290), "Laptop (MT7921)", "Wi-Fi 802.11n 2.4 GHz\nRSSI: -61 dBm | Qual: 77%", TEAL)
    _box(d, (460, 130, 740, 290), "Home Wi-Fi Router", "Local Radio Link:\n144.4 Mbps PHY Rate", BLUE)
    _box(d, (860, 130, 1150, 290), "ISP / Internet", "Actual Speedtest:\n29.84 Mbps (Plan/Backhaul)", GREEN)

    _arrow(d, (340, 210), (460, 210), "144.4 Mbps")
    _arrow(d, (740, 210), (860, 210), "29.84 Mbps")

    d.rounded_rectangle([50, 350, 1150, 440], radius=12, fill="#EAF2FC", outline=BLUE, width=2)
    d.text((75, 378), "Key Insight: netsh wlan reports local Router <-> Laptop PHY link rate. TARANG's opt-in Speed Test measures end-to-end ISP throughput.", fill=NAVY, font=_font(16, True))
    img.save(OUT_DIR / "fig_phy_vs_isp.png")


def make_idempotent_sync():
    img = Image.new("RGB", (1200, 500), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 4.3: Offline SQLite Queue & Idempotent Batch Sync Flow", fill=NAVY, font=_font(24, True))

    _box(d, (40, 130, 290, 290), "1. Capture + UUIDv4", "Assign unique obs_id\nSave to SQLite Queue", TEAL)
    _box(d, (350, 130, 620, 290), "2. POST /batch", "Send <= 500 items\nNetwork drop? Retry safe", BLUE)
    _box(d, (680, 90, 930, 210), "New obs_id -> Insert", "status: 'accepted'\nRemove from queue", GREEN)
    _box(d, (680, 240, 930, 360), "Existing obs_id -> Skip", "status: 'duplicate'\nZero DB duplicates", AMBER)
    _box(d, (980, 165, 1170, 295), "3. Synced", "Queue = 0\nAudit in sync_batches", NAVY)

    _arrow(d, (290, 210), (350, 210))
    _arrow(d, (620, 190), (680, 150))
    _arrow(d, (620, 230), (680, 300))
    _arrow(d, (930, 150), (980, 210))
    _arrow(d, (930, 300), (980, 250))

    img.save(OUT_DIR / "fig_idempotent_sync.png")


def make_signal_tiers_scale():
    img = Image.new("RGB", (1200, 520), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 4.4: Radio-Specific Signal Tier Scales (Never Mixed)", fill=NAVY, font=_font(24, True))

    rows = [
        ("Wi-Fi RSSI (dBm)", [">= -55", "-56 to -67", "-68 to -75", "< -75"], 110),
        ("Windows Quality (%)", [">= 80%", "60% - 79%", "40% - 59%", "< 40%"], 210),
        ("LTE RSRP (dBm)", [">= -85", "-86 to -98", "-99 to -110", "< -110"], 310),
        ("5G NR SS-RSRP (dBm)", [">= -85", "-86 to -98", "-99 to -110", "< -110"], 410),
    ]
    colors = [GREEN, BLUE, AMBER, CORAL]
    tiers = ["Strong", "Good", "Fair", "Weak"]

    for label, vals, y in rows:
        d.text((40, y + 18), label, fill=NAVY, font=_font(17, True))
        x = 310
        for val, col, tier in zip(vals, colors, tiers):
            d.rounded_rectangle([x, y, x + 195, y + 60], radius=10, fill=col)
            d.text((x + 16, y + 10), tier, fill="#FFFFFF", font=_font(16, True))
            d.text((x + 16, y + 34), val, fill="#FFFFFF", font=_font(15, False))
            x += 210

    img.save(OUT_DIR / "fig_signal_tiers_scale.png")


def make_stride_diagram():
    img = Image.new("RGB", (1200, 540), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 7.4: STRIDE CyberSecurity Threat Model & TARANG Defense Layers", fill=NAVY, font=_font(24, True))

    items = [
        ("S — Spoofing", "Random UUIDv4 device IDs\nCapability registration", TEAL, 50, 100),
        ("T — Tampering", "Pydantic v2 validation\nIdempotent UUID dedup", BLUE, 425, 100),
        ("R — Repudiation", "observed_at / recorded_at\nmetric_source audit", NAVY, 800, 100),
        ("I — Info Disclosure", "Project-salted BSSID hash\nredact=true CSV/JSON", GREEN, 50, 300),
        ("D — Denial of Service", "500-item batch limit\nOpt-in timed speed test", AMBER, 425, 300),
        ("E — Elevation", "Loopback 127.0.0.1:8765\nNo root / no sniffing", CORAL, 800, 300),
    ]
    for title, sub, col, x, y in items:
        _box(d, (x, y, x + 340, y + 150), title, sub, col)

    img.save(OUT_DIR / "fig_stride_matrix.png")


def make_ux_wireflow():
    img = Image.new("RGB", (1200, 480), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 6.8: Comfort-First UX Wireflow (<= 2 Taps to Start Survey)", fill=NAVY, font=_font(24, True))

    _box(d, (40, 130, 290, 300), "1. Overview Home", "Big 'Start Survey' CTA\nLaptop Collector Card", TEAL)
    _box(d, (330, 130, 580, 300), "2. 3-Step Wizard", "Indoor / Outdoor\nWi-Fi / Cell / Room", BLUE)
    _box(d, (620, 130, 880, 300), "3. Live Survey", "Hero Signal + Freshness\nTap Floor Plan + Undo", GREEN)
    _box(d, (920, 130, 1160, 300), "4. Map & Insights", "Measured Points / List\nRules A-E + Export", NAVY)

    _arrow(d, (290, 215), (330, 215))
    _arrow(d, (580, 215), (620, 215))
    _arrow(d, (880, 215), (920, 215))

    d.text((40, 370), "Ergonomics: 48px sticky thumb-zone controls on mobile; tabular numerals; color never communicates signal alone.", fill=MUTED, font=_font(16, True))
    img.save(OUT_DIR / "fig_ux_wireflow.png")


def make_privacy_pipeline():
    img = Image.new("RGB", (1200, 480), BG)
    d = ImageDraw.Draw(img)
    d.text((40, 24), "Figure 7.5: Privacy-by-Default Telemetry Redaction & BSSID Hashing Pipeline", fill=NAVY, font=_font(24, True))

    _box(d, (40, 130, 350, 300), "Raw Radio Capture", "SSID: Airtel_suna_6489\nBSSID: b4:86:18:...\nGPS: 28.6139, 77.2090", CORAL)
    _box(d, (430, 130, 760, 300), "Local Privacy Transform", "SHA-256(project_id + BSSID)\nNo IMEI / No Phone #\nLoopback-only storage", TEAL)
    _box(d, (840, 130, 1160, 300), "Redacted Export (CSV/JSON)", "SSID: [REDACTED]\nbssid_hash: 1dc71802...\nGPS: null (when redact=true)", GREEN)

    _arrow(d, (350, 215), (430, 215))
    _arrow(d, (760, 215), (840, 215))

    d.text((40, 370), "Result: Researchers can share signal-quality datasets publicly without exposing home Wi-Fi names or exact coordinates.", fill=MUTED, font=_font(16, True))
    img.save(OUT_DIR / "fig_privacy_pipeline.png")


if __name__ == "__main__":
    make_architecture()
    make_dfd()
    make_er_schema()
    make_sequence()
    make_rules_pipeline()
    make_signal_chart()
    make_band_comparison()
    make_test_breakdown()
    make_phy_vs_isp()
    make_idempotent_sync()
    make_signal_tiers_scale()
    make_stride_diagram()
    make_ux_wireflow()
    make_privacy_pipeline()
    print("Generated all 14 technical diagrams in", OUT_DIR)
