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
    draw.text((x1 + 18, y1 + 16), title, fill=NAVY, font=_font(22, True))
    draw.text((x1 + 18, y1 + 48), subtitle, fill=MUTED, font=_font(16, False))


def _arrow(draw: ImageDraw.ImageDraw, p1, p2, label: str = ""):
    draw.line([p1, p2], fill=NAVY, width=3)
    x2, y2 = p2
    draw.polygon([(x2, y2), (x2 - 10, y2 - 6), (x2 - 10, y2 + 6)], fill=NAVY)
    if label:
        mx, my = (p1[0] + x2) // 2, (p1[1] + y2) // 2
        draw.text((mx - 40, my - 24), label, fill=TEAL, font=_font(15, True))


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
        # Map -90..-40 to bar height
        h = max(30, int((100 + rssi) * 5.2))
        d.rounded_rectangle([x, base_y - h, x + 120, base_y], radius=8, fill=col)
        d.text((x + 22, base_y - h - 28), f"{rssi} dBm", fill=NAVY, font=_font(17, True))
        d.text((x + 12, base_y + 12), name, fill=NAVY, font=_font(16, False))
        x += 180

    d.line([(60, base_y), (1140, base_y)], fill=NAVY, width=2)
    img.save(OUT_DIR / "fig_signal_chart.png")


if __name__ == "__main__":
    make_architecture()
    make_dfd()
    make_signal_chart()
    print("Generated figures in", OUT_DIR)
