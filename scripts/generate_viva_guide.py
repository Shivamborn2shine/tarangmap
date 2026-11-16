from pathlib import Path
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "report_figures"
OUT_PATH = ROOT / "docs" / "TARANG_Viva_Guide_Shivam_Kumar.docx"

NAVY = RGBColor(0x10, 0x2A, 0x43)
TEAL = RGBColor(0x08, 0x7F, 0x8C)
MUTED = RGBColor(0x48, 0x65, 0x81)


def set_cell_bg(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def add_table(doc: docx.Document, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        set_cell_bg(cell, "102A43")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row in enumerate(rows):
        bg = "F7FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            set_cell_bg(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(9.5)
    doc.add_paragraph()


def add_heading(doc: docx.Document, text: str, level: int = 1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = NAVY if level == 1 else TEAL
    return p


def add_body(doc: docx.Document, text: str):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.18
    for r in p.runs:
        r.font.size = Pt(10.5)
    return p


def add_bullet(doc: docx.Document, text: str):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    for r in p.runs:
        r.font.size = Pt(10)
    return p


def add_figure(doc: docx.Document, img_path: Path, caption: str, width_in: float = 5.8):
    if img_path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(img_path), width=Inches(width_in))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cp.add_run(caption)
        cr.italic = True
        cr.font.size = Pt(9)
        cr.font.color.rgb = MUTED


def add_code_ref_box(doc: docx.Document, refs: list[str]):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, "E6F6F7")
    p = cell.paragraphs[0]
    rh = p.add_run("Where to Show in Source Code:\n")
    rh.bold = True
    rh.font.size = Pt(9.5)
    rh.font.color.rgb = TEAL
    for ref in refs:
        rb = p.add_run(f"• {ref}\n")
        rb.font.name = "Consolas"
        rb.font.size = Pt(8.8)
        rb.font.color.rgb = NAVY
    doc.add_paragraph()


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r1 = p.add_run("TARANG Viva & Code Walkthrough Guide (Shivam Kumar, 2105130)   |   Page ")
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = MUTED
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    p._p.append(fld)


def build_viva_guide():
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11.0)
    sec.top_margin = Inches(0.85)
    sec.bottom_margin = Inches(0.85)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)
    add_page_number_footer(sec)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    # ---------------- PAGE 1: TECH STACK & OVERVIEW ----------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("TARANG — VIVA & CODE WALKTHROUGH GUIDE")
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = NAVY

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(
        "Shivam Kumar (Roll No. 2105130)  |  BCA CyberSecurity (2024–2027)  |  Guide: Mr. Mukesh Singh\n"
        "Graphic Era (Deemed to be University), Dehradun"
    )
    r2.font.size = Pt(10)
    r2.font.color.rgb = MUTED

    add_heading(doc, "Complete Project Tech Stack", level=1)
    add_table(
        doc,
        ["Layer", "Technologies Used", "Role in TARANG"],
        [
            ["Web Frontend", "React 18, TypeScript 5, Vite 5, Tailwind CSS, Recharts, Lucide Icons", "Responsive dashboard, floor-plan tap marker, charts, CSV/JSON export"],
            ["Windows Hybrid App", "Python 3.12, netsh wlan CLI, SQLite3, FastAPI, Uvicorn", "Reads live laptop Wi-Fi, buffers offline, serves localhost:8765 & auto-opens browser"],
            ["Backend API", "FastAPI, Pydantic v2, SQLAlchemy 2, HTTPX, Pytest", "REST API v1, idempotent batch ingest, Rules A–E insights, redacted exports"],
            ["Database", "SQLite (local-first default) / PostgreSQL 16 + PostGIS 3.4", "Stores projects, floorplans, sessions, observations, and sync batches"],
            ["Android Collector", "Kotlin, Android WifiManager, TelephonyManager, Foreground Service", "Permission-aware Wi-Fi RSSI and LTE/5G NR RSRP/RSRQ/SINR capture"],
            ["Deployment & CI", "Vercel (vercel.json), Netlify (netlify.toml), Docker Compose, GitHub", "Static SPA hosting + hybrid localhost connection + containerized DB/API"],
        ],
    )
    add_figure(doc, FIG_DIR / "fig_architecture.png", "System Architecture: How Laptop App, Android, Backend, and Web Connect.", width_in=5.9)
    doc.add_page_break()

    # ---------------- Q1 ----------------
    add_heading(doc, "Q1. How does your laptop read real Wi-Fi signal instead of fake numbers?", level=1)
    add_body(
        doc,
        "Simple Answer: My Windows collector runs the built-in Windows `netsh wlan show interfaces` "
        "command in the background, parses the real adapter fields (SSID, band, channel, PHY link rate, "
        "Signal %, and RSSI dBm), hashes the router BSSID with SHA-256 for privacy, and NEVER converts "
        "Signal % into a fake dBm if the driver does not expose RSSI."
    )
    add_code_ref_box(doc, [
        "apps/windows-collector/tarang_collector/probe.py : probe_windows_wifi() (Lines 50–125)",
        "apps/windows-collector/tarang_collector/server.py : /api/v1/windows/live-scan (Lines 204–214)",
    ])

    # ---------------- Q2 ----------------
    add_heading(doc, "Q2. How does the Hybrid Web + Laptop App work (localhost & Vercel/Netlify)?", level=1)
    add_body(
        doc,
        "Simple Answer: On startup, the React web app runs `detectBackend()` which checks `http://127.0.0.1:8765/health`. "
        "If the laptop collector is running (`START_TARANG_LAPTOP.bat`), it connects live to your laptop's Wi-Fi adapter. "
        "If deployed standalone on Vercel or Netlify without the laptop app running, it falls back seamlessly to Local-First Demo Mode."
    )
    add_code_ref_box(doc, [
        "apps/web/src/api.ts : detectBackend() (Lines 26–62)",
        "apps/windows-collector/tarang_collector/server.py : create_hybrid_app() (Lines 323–339)",
    ])
    doc.add_page_break()

    # ---------------- Q3 ----------------
    add_heading(doc, "Q3. Why is PHY Link Rate (144.4 Mbps) different from Speedtest (29.84 Mbps)?", level=1)
    add_body(
        doc,
        "Simple Answer: 144.4 Mbps from `netsh wlan` is only the local radio link speed between your laptop and router. "
        "Your actual internet speed (29.84 Mbps) depends on your ISP plan and backhaul. To measure real internet performance, "
        "TARANG includes two opt-in active probes: a TCP latency probe to 1.1.1.1:443 and a timed download/upload Speed Test."
    )
    add_figure(doc, FIG_DIR / "fig_phy_vs_isp.png", "Visual Explanation: Local Wi-Fi PHY Link Rate vs End-to-End ISP Speed.", width_in=5.8)
    add_code_ref_box(doc, [
        "apps/windows-collector/tarang_collector/probe.py : run_active_tcp_probe() (Lines 155–188)",
        "apps/windows-collector/tarang_collector/probe.py : run_active_speed_test() (Lines 191–233)",
    ])
    doc.add_page_break()

    # ---------------- Q4 ----------------
    add_heading(doc, "Q4. How do you prevent data loss offline or duplicate rows on retry?", level=1)
    add_body(
        doc,
        "Simple Answer: Every observation is assigned a unique UUIDv4 on the client. On Windows, `OfflineQueue` saves it "
        "to a local SQLite database (`~/.tarang/windows_collector_queue.db`) before syncing. On the server, `ingest_batch()` "
        "checks if that UUID already exists — if it does, it marks it `'duplicate'` and skips inserting it again."
    )
    add_figure(doc, FIG_DIR / "fig_idempotent_sync.png", "Visual Flow: Offline SQLite Queue & Idempotent UUIDv4 Batch Sync.", width_in=5.8)
    add_code_ref_box(doc, [
        "apps/windows-collector/tarang_collector/storage.py : OfflineQueue (Lines 7–56)",
        "apps/windows-collector/tarang_collector/server.py : CollectorState (Lines 31–122)",
        "services/api/app/routers/observations.py : ingest_batch() (Lines 91–130)",
    ])
    doc.add_page_break()

    # ---------------- Q5 ----------------
    add_heading(doc, "Q5. How does Indoor Floor-Plan Mapping work without fake indoor GPS?", level=1)
    add_body(
        doc,
        "Simple Answer: GPS is inaccurate indoors, so the user selects a room name and taps their location on the floor plan. "
        "`handleFloorplanClick()` converts pixel coordinates into normalized `[0, 1]` coordinates (`x_norm`, `y_norm`) so pins "
        "stay accurately positioned across mobile, tablet, and desktop screens."
    )
    add_figure(doc, FIG_DIR / "fig_ux_wireflow.png", "Visual Flow: 2-Tap Survey Start, Live Floor-Plan Marking, and Map Explorer.", width_in=5.8)
    add_code_ref_box(doc, [
        "apps/web/src/components/LiveSurveyView.tsx : handleFloorplanClick() (Lines 146–152)",
        "apps/web/src/api.ts : getWindowsLiveScan() with cache: 'no-store' (Lines 143–149)",
    ])
    doc.add_page_break()

    # ---------------- Q6 ----------------
    add_heading(doc, "Q6. How are signals classified and how are recommendations generated?", level=1)
    add_body(
        doc,
        "Simple Answer: TARANG never mixes Wi-Fi RSSI, Windows Quality %, LTE RSRP, and 5G NR SS-RSRP into one scale. "
        "`classify_observation()` applies technology-specific thresholds, and `build_project_summary()` runs deterministic "
        "Rules A–E to generate Finding -> Evidence -> Confidence -> Suggested Next Test cards."
    )
    add_figure(doc, FIG_DIR / "fig_signal_tiers_scale.png", "Radio-Specific Signal Tier Thresholds.", width_in=5.6)
    add_figure(doc, FIG_DIR / "fig_rules_pipeline.png", "Rules-Based Optimization Engine (Rules A–E).", width_in=5.6)
    add_code_ref_box(doc, [
        "services/api/app/analysis.py : classify_observation() (Lines 56–85)",
        "services/api/app/analysis.py : build_project_summary() (Lines 88–195)",
    ])
    doc.add_page_break()

    # ---------------- Q7 ----------------
    add_heading(doc, "Q7. What CyberSecurity & Privacy protections are built in?", level=1)
    add_body(
        doc,
        "Simple Answer: (1) Loopback-only binding (`127.0.0.1:8765`) by default, (2) SHA-256 hashing of router BSSIDs, "
        "(3) `redact=true` on CSV/JSON exports to mask SSIDs and precise outdoor GPS, and (4) runtime permission checks on Android."
    )
    add_figure(doc, FIG_DIR / "fig_privacy_pipeline.png", "Privacy-by-Default Telemetry Redaction & BSSID Hashing Pipeline.", width_in=5.8)
    add_code_ref_box(doc, [
        "services/api/app/routers/exports.py : export_project() & compare_sessions() (Lines 17–60, 97–155)",
        "apps/android/app/src/main/java/com/tarang/collector/RadioCapabilityProbe.kt : capture() (Lines 35–60)",
    ])

    add_heading(doc, "2-Minute Live Demo Script for Your Teacher", level=2)
    for step in [
        "1. Double-click START_TARANG_LAPTOP.bat -> opens http://127.0.0.1:8765 automatically.",
        "2. Overview Tab: Show the live MediaTek MT7921 adapter reading and signal tier badge.",
        "3. Survey Tab: Show live RSSI/% updating, tap a room on the floor plan, and click Speed Test (~6.5 MB) to contrast ISP Mbps vs PHY Link Rate.",
        "4. Map Explorer Tab: Toggle Estimated Heatmap and List View, and click a dot to show the Point Inspector.",
        "5. Compare & Export Tab: Show hardware/band comparison caveats and download a redacted CSV/JSON file.",
    ]:
        add_bullet(doc, step)

    doc.save(str(OUT_PATH))
    print("Saved Viva Guide to:", OUT_PATH)


if __name__ == "__main__":
    build_viva_guide()
