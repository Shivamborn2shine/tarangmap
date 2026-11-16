from pathlib import Path
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "report_figures"
OUT_PATH = ROOT / "docs" / "TARANG_Project_Report_Shivam_Kumar.docx"

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


def add_code_block(doc: docx.Document, caption: str, code: str):
    cp = doc.add_paragraph()
    cr = cp.add_run(caption)
    cr.bold = True
    cr.font.size = Pt(9.5)
    cr.font.color.rgb = TEAL

    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = "Table Grid"
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, "F0F4F8")
    p = cell.paragraphs[0]
    r = p.add_run(code.strip())
    r.font.name = "Consolas"
    r.font.size = Pt(8.5)
    r.font.color.rgb = NAVY
    doc.add_paragraph()


def add_heading(doc: docx.Document, text: str, level: int = 1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = NAVY if level == 1 else TEAL
    return p


def add_body(doc: docx.Document, text: str):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    for r in p.runs:
        r.font.size = Pt(11)
    return p


def add_bullet(doc: docx.Document, text: str):
    p = doc.add_paragraph(text, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(10.5)
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
        cr.font.size = Pt(9.5)
        cr.font.color.rgb = MUTED


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r1 = p.add_run("TARANG — Project Report (Shivam Kumar, 2105130)   |   Page ")
    r1.font.size = Pt(8.5)
    r1.font.color.rgb = MUTED
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    p._p.append(fld)


def build_report():
    doc = docx.Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11.0)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1.25)
    add_page_number_footer(sec)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)

    # ---------------- TITLE PAGE ----------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("PROJECT REPORT")
    r.bold = True
    r.font.size = Pt(20)
    r.font.color.rgb = NAVY

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("TARANG — Mapping the Invisible")
    r2.bold = True
    r2.font.size = Pt(22)
    r2.font.color.rgb = TEAL

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run(
        "Telecommunication Analysis, Radio Assessment & Network Geomapping:\n"
        "A Local-First Hybrid Wi-Fi and Cellular Network Surveying Platform"
    )
    r3.font.size = Pt(13)
    r3.font.color.rgb = MUTED

    doc.add_paragraph()
    p_deg = doc.add_paragraph()
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_deg.add_run(
        "Submitted in partial fulfillment of the requirements for the degree of\n"
        "Bachelor of Computer Applications (BCA) in CyberSecurity"
    ).italic = True

    doc.add_paragraph()
    add_table(
        doc,
        ["Field", "Candidate & Academic Details"],
        [
            ["Candidate Name", "Shivam Kumar"],
            ["Registration / Roll Number", "2105130"],
            ["Programme / Batch", "BCA CyberSecurity, 2024–2027"],
            ["Department", "Department of Computer Science and Engineering"],
            ["Institution / Place", "Graphic Era Deemed to be University, Dehradun"],
            ["Project Guide", "Mr. Mukesh Singh"],
            ["Academic Year & Submission", "2024–2027 | November 2026"],
            ["Source Repository", "https://github.com/Shivamborn2shine/tarangmap"],
        ],
    )
    doc.add_page_break()

    # ---------------- CANDIDATE DECLARATION ----------------
    add_heading(doc, "CANDIDATE DECLARATION", level=1)
    add_body(
        doc,
        "I hereby declare that the project report entitled \"TARANG — Mapping the Invisible: "
        "A Local-First Hybrid Wi-Fi and Cellular Network Surveying Platform\" submitted to the "
        "Department of Computer Science and Engineering, Graphic Era Deemed to be University, "
        "in partial fulfillment of the requirements for the award of the degree of Bachelor of "
        "Computer Applications (BCA) in CyberSecurity (Batch 2024–2027), is a record of original "
        "work carried out by me (Shivam Kumar, Roll No. 2105130) under the supervision and guidance "
        "of Mr. Mukesh Singh."
    )
    add_body(
        doc,
        "The matter embodied in this report has not been submitted to any other university or "
        "institution for the award of any degree or diploma."
    )
    doc.add_paragraph("\nCandidate Signature: ________________________\nName: Shivam Kumar (Roll No. 2105130)")
    doc.add_page_break()

    # ---------------- ACKNOWLEDGEMENT ----------------
    add_heading(doc, "ACKNOWLEDGEMENT", level=1)
    add_body(
        doc,
        "I express my sincere gratitude to my project guide, Mr. Mukesh Singh, for his continuous "
        "mentorship, technical feedback, and encouragement throughout the design and implementation "
        "of TARANG. I also thank the faculty of the Department of Computer Science and Engineering, "
        "Graphic Era Deemed to be University, for providing the academic environment and resources "
        "to complete this hybrid networking and cybersecurity-aware surveying platform."
    )
    doc.add_page_break()

    # ---------------- ABSTRACT ----------------
    add_heading(doc, "ABSTRACT", level=1)
    add_body(
        doc,
        "Modern wireless connectivity is often judged only by coarse operating-system signal bars, "
        "which hide spatial dead zones, band propagation differences (2.4 GHz vs 5 GHz), and the "
        "distinction between local Wi-Fi radio link rate and actual internet throughput. TARANG "
        "(Telecommunication Analysis, Radio Assessment & Network Geomapping) is a local-first, "
        "privacy-respecting Wi-Fi and cellular network surveying platform built as a hybrid system "
        "spanning a Windows laptop collector, an Android Kotlin radio probe, a FastAPI REST backend, "
        "and a responsive React + TypeScript web dashboard deployable on Vercel and Netlify."
    )
    add_body(
        doc,
        "Unlike cloud-locked survey tools, TARANG operates offline-first with SQLite/Room queues, "
        "idempotent UUIDv4 batch ingestion, honest radio-specific metric reporting (never fabricating "
        "RSSI dBm from Windows signal quality percentages or indoor GPS precision), and a rules-based "
        "analysis engine that translates raw RF observations into actionable diagnostic tests."
    )
    doc.add_page_break()

    # ---------------- TABLE OF CONTENTS / FIGURES / TABLES ----------------
    add_heading(doc, "TABLE OF CONTENTS", level=1)
    toc_items = [
        "1. Chapter 1: Introduction",
        "2. Chapter 2: System Analysis and Requirements",
        "3. Chapter 3: System Design and Architecture",
        "4. Chapter 4: Core Methods, Algorithms and Source Code Working",
        "5. Chapter 5: REST API Specification",
        "6. Chapter 6: Input and Output Design",
        "7. Chapter 7: Implementation, Testing, CyberSecurity and Maintenance",
        "8. Chapter 8: Summary, Learning Outcomes and Future Scope",
        "References",
        "Appendix A–D: Command Reference, Source Excerpts, Deployment & Verification Checklist",
    ]
    for item in toc_items:
        add_bullet(doc, item)
    doc.add_page_break()

    # ---------------- CHAPTER 1 ----------------
    add_heading(doc, "CHAPTER 1: INTRODUCTION", level=1)
    add_heading(doc, "1.1 Overview", level=2)
    add_body(
        doc,
        "TARANG (Telecommunication Analysis, Radio Assessment & Network Geomapping) enables "
        "homeowners, students, researchers, and network technicians to walk through an indoor "
        "building or outdoor perimeter, record real Wi-Fi and cellular radio observations, anchor "
        "them to floor-plan or GPS coordinates, and generate grounded coverage insights."
    )
    add_heading(doc, "1.2 Background and Motivation", level=2)
    add_body(
        doc,
        "Standard device indicators conflate radio signal strength, signal quality, local PHY link "
        "rate, and ISP internet throughput. Furthermore, many commercial survey tools require paid "
        "cloud accounts or transmit sensitive SSIDs, BSSIDs, and floor plans to third-party servers. "
        "TARANG solves this with a local-first architecture that keeps raw network data private by default."
    )
    add_heading(doc, "1.3 Problem Statement", level=2)
    add_body(
        doc,
        "To design and implement a hybrid cross-platform network surveying system that accurately "
        "collects supported Wi-Fi and cellular metrics across Windows laptops and Android devices, "
        "prevents fabricated telemetry or duplicate uploads, and presents calm, accessible coverage "
        "maps and optimization tests via a deployable web dashboard."
    )
    add_heading(doc, "1.4 Objectives", level=2)
    for obj in [
        "Build a FastAPI monolith backend with canonical schema_version=1 contracts and idempotent batch ingest.",
        "Build a Windows Laptop Hybrid Collector reading real WLAN adapter telemetry via netsh wlan and serving a localhost bridge on 127.0.0.1:8765.",
        "Develop a responsive React + TypeScript dashboard deployable on Vercel and Netlify with seamless Local-First Demo Mode fallback.",
        "Implement an Android Kotlin RadioCapabilityProbe for permission-aware Wi-Fi RSSI and LTE/5G NR RSRP/RSRQ/SINR collection.",
        "Enforce cybersecurity and privacy controls including BSSID hashing, export redaction, and STRIDE threat mitigations.",
    ]:
        add_bullet(doc, obj)

    add_heading(doc, "1.5 Software and Hardware Requirements", level=2)
    add_table(
        doc,
        ["Component", "Specification"],
        [
            ["Backend & Collector", "Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2, Pydantic v2, SQLite / PostgreSQL+PostGIS"],
            ["Web Frontend", "React 18, TypeScript 5, Vite 5, Tailwind CSS, Recharts, Lucide Icons"],
            ["Windows Hardware", "Windows 10/11 laptop with WLAN adapter (tested on MediaTek MT7921 Wi-Fi 6)"],
            ["Android Target", "Android 10+ (API 29+) with Location & Phone permissions for WifiManager / TelephonyManager"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 2 ----------------
    add_heading(doc, "CHAPTER 2: SYSTEM ANALYSIS AND REQUIREMENTS", level=1)
    add_heading(doc, "2.1 Existing vs Proposed System", level=2)
    add_table(
        doc,
        ["Criterion", "Existing Signal Tools", "TARANG (Proposed Hybrid System)"],
        [
            ["Privacy & Storage", "Cloud-first, requires login, uploads SSIDs/BSSIDs", "Local-first SQLite/Room; optional LAN sync; redacted exports"],
            ["Metric Honesty", "Converts Windows % to fake dBm; mixes LTE & 5G scales", "Preserves raw units, freshness_ms, and missing_reason"],
            ["Indoor Positioning", "Relies on inaccurate indoor GPS", "Manual floor-plan tap marker with room labels & Undo"],
            ["Throughput Clarity", "Confuses Wi-Fi PHY rate with internet speed", "Separates PHY Link Rate from opt-in Active Speed Test"],
        ],
    )
    add_heading(doc, "2.2 Functional & CyberSecurity Requirements", level=2)
    add_body(
        doc,
        "Functional requirements cover project/session lifecycle, idempotent 500-item batch ingestion, "
        "indoor floor-plan mapping, outdoor GPS accuracy flagging, rules-based insights (Rules A–E), "
        "and CSV/JSON exports. Non-functional and cybersecurity requirements mandate loopback-only "
        "binding by default, project-salted SHA-256 BSSID hashing, zero IMEI/phone-number collection, "
        "and WCAG AA accessible UI badges pairing color with text and units."
    )
    add_figure(doc, FIG_DIR / "fig_dfd.png", "Figure 2.1: Level 0 & Level 1 Data Flow — Radio Collection to Insights.")
    doc.add_page_break()

    # ---------------- CHAPTER 3 ----------------
    add_heading(doc, "CHAPTER 3: SYSTEM DESIGN AND ARCHITECTURE", level=1)
    add_heading(doc, "3.1 Hybrid Monolith & Laptop Bridge Architecture", level=2)
    add_body(
        doc,
        "TARANG uses a clean monorepo separating apps/windows-collector, apps/web, apps/android, "
        "services/api, packages/contracts, and infra. On a Windows laptop, the hybrid collector "
        "mounts the FastAPI v1 API alongside live hardware endpoints (/api/v1/windows/*) on "
        "http://127.0.0.1:8765, serves the compiled React SPA, and auto-opens the browser."
    )
    add_figure(doc, FIG_DIR / "fig_architecture.png", "Figure 3.1: TARANG Hybrid Local-First System Architecture.")

    add_heading(doc, "3.2 Package & Module Responsibility Matrix", level=2)
    add_table(
        doc,
        ["Module Path", "Responsibility"],
        [
            ["services/api/app/main.py", "FastAPI app lifespan, CORS, router mounting, static uploads/samples"],
            ["services/api/app/analysis.py", "Radio-specific tier classification and Rules A–E optimization engine"],
            ["apps/windows-collector/tarang_collector/probe.py", "Real netsh wlan parser, nearby BSSID scanner, TCP latency & speed test"],
            ["apps/windows-collector/tarang_collector/server.py", "Hybrid localhost server (port 8765) + background SQLite queue worker"],
            ["apps/web/src/api.ts", "Auto-detects localhost collector or falls back to Local-First Demo Mode"],
            ["apps/android/.../RadioCapabilityProbe.kt", "Permission-aware Android WifiManager & TelephonyManager snapshot probe"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 4 ----------------
    add_heading(doc, "CHAPTER 4: CORE METHODS, ALGORITHMS AND SOURCE CODE WORKING", level=1)
    add_heading(doc, "4.1 Windows WLAN Probe & Honest Metric Extraction (probe.py)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.1: apps/windows-collector/tarang_collector/probe.py — Honest netsh wlan parsing",
        """
quality_match = re.search(r"(\\d+)\\s*%", kv.get("signal", ""))
quality_pct = int(quality_match.group(1)) if quality_match else None

rssi_raw = kv.get("rssi")
rssi_dbm = None
if rssi_raw:
    m = re.search(r"(-?\\d+)", rssi_raw)
    if m:
        rssi_dbm = int(m.group(1))
""",
    )
    add_heading(doc, "4.2 Radio-Specific Signal Tier Classification (analysis.py)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.2: services/api/app/analysis.py — Separate Wi-Fi, LTE, and 5G NR Rules",
        """
def classify_wifi_rssi(rssi: int | None) -> str:
    if rssi is None: return "Unavailable"
    if rssi >= -55: return "Strong"
    if rssi >= -67: return "Good"
    if rssi >= -75: return "Fair"
    return "Weak"
""",
    )
    add_heading(doc, "4.3 Idempotent Batch Ingestion (observations.py)", level=2)
    add_body(
        doc,
        "To guarantee zero data loss during offline retries, POST /api/v1/observations/batch checks "
        "each observation UUID before insertion, returning per-item status (accepted, duplicate, or "
        "rejected) and recording a SyncBatch audit row."
    )
    doc.add_page_break()

    # ---------------- CHAPTER 5 ----------------
    add_heading(doc, "CHAPTER 5: REST API SPECIFICATION", level=1)
    add_table(
        doc,
        ["Method & Endpoint", "Purpose"],
        [
            ["GET /health", "API and database readiness check (schema_version=1)"],
            ["GET, POST /api/v1/projects", "List or create indoor/outdoor survey projects"],
            ["POST /api/v1/projects/{id}/floorplans", "Upload floor-plan image with pixel dimensions"],
            ["POST /api/v1/observations/batch", "Idempotent batch ingest (up to 500 observations)"],
            ["GET /api/v1/projects/{id}/summary", "Signal distributions, weak spots, and Rules A–E insights"],
            ["GET /api/v1/projects/{id}/export", "CSV or JSON export with optional SSID/GPS redaction"],
            ["GET /api/v1/windows/live-scan", "Live Windows WLAN adapter reading via localhost bridge"],
            ["POST /api/v1/windows/speed-test", "Opt-in active internet download/upload Mbps test"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 6 ----------------
    add_heading(doc, "CHAPTER 6: INPUT AND OUTPUT DESIGN", level=1)
    add_body(
        doc,
        "The React + TypeScript web interface follows a calm technical aesthetic (#F7FAFC background, "
        "#102A43 deep navy text, #087F8C teal primary actions) with 44–48px touch targets, bottom "
        "navigation on mobile, and a persistent sidebar on desktop. Key screens include the 3-step "
        "Survey Wizard, Live Survey with tap-to-mark floor plan, Map Explorer (Measured Points, "
        "Bounded Heatmap, and Accessible List View), Insights, and Session Compare & Export."
    )
    doc.add_page_break()

    # ---------------- CHAPTER 7 ----------------
    add_heading(doc, "CHAPTER 7: IMPLEMENTATION, TESTING, CYBERSECURITY AND MAINTENANCE", level=1)
    add_heading(doc, "7.1 Automated Verification Results", level=2)
    add_table(
        doc,
        ["Test Case / Build Check", "Scope", "Result"],
        [
            ["test_health_and_seeded_projects", "FastAPI /health & seeded demo projects", "PASSED"],
            ["test_idempotent_batch_ingest", "Duplicate UUID batch deduplication", "PASSED"],
            ["test_summary_and_export", "Rules A–E summary & redacted CSV/JSON export", "PASSED"],
            ["tsc -b && vite build", "TypeScript strict check & Vite production bundle", "PASSED"],
            ["Windows Hybrid Probe", "Live netsh wlan & FastAPI localhost bridge (8765)", "PASSED"],
        ],
    )
    add_figure(doc, FIG_DIR / "fig_signal_chart.png", "Figure 7.1: Seeded Apartment Indoor Wi-Fi RSSI by Room.")

    add_heading(doc, "7.2 CyberSecurity Threat & Control Matrix (STRIDE)", level=2)
    add_table(
        doc,
        ["STRIDE Category", "Potential Threat", "Implemented Control in TARANG"],
        [
            ["Spoofing", "Unauthorized client forging device telemetry", "Device capability registration & random UUIDv4 identifiers"],
            ["Tampering", "Duplicate or corrupted offline sync batches", "Pydantic v2 schema validation & UUID idempotency check"],
            ["Repudiation", "Disputed survey timestamps or locations", "Immutable observed_at, recorded_at, received_at & metric_source"],
            ["Info Disclosure", "Leaking home SSIDs, BSSIDs, or GPS coordinates", "Project-salted BSSID hash; redact=true default on CSV/JSON export"],
            ["Denial of Service", "Oversized batch uploads or runaway speed tests", "500-item batch cap; opt-in speed test with explicit timeout"],
            ["Elevation of Privilege", "Unintended remote access to laptop collector", "Loopback-only binding (127.0.0.1:8765) by default"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 8 ----------------
    add_heading(doc, "CHAPTER 8: SUMMARY, LEARNING OUTCOMES AND FUTURE SCOPE", level=1)
    add_heading(doc, "8.1 Summary & Learning Outcomes", level=2)
    add_body(
        doc,
        "TARANG demonstrates how local-first engineering, honest radio telemetry, and accessible "
        "visualization can demystify Wi-Fi and cellular connectivity. Key learning outcomes include "
        "designing idempotent REST APIs, parsing Windows WLAN driver outputs without fabricating dBm "
        "values, building responsive React/Recharts dashboards deployable on Vercel/Netlify, and "
        "applying STRIDE privacy controls to geospatial network data."
    )
    add_heading(doc, "8.2 Future Scope", level=2)
    for f in [
        "Full Android Jetpack Compose APK release with Room background foreground-service sync.",
        "PDF report generation and multi-device LAN project collaboration.",
        "Dockerized PostgreSQL + PostGIS spatial indexing for campus-scale outdoor surveys.",
    ]:
        add_bullet(doc, f)

    # ---------------- REFERENCES ----------------
    add_heading(doc, "REFERENCES", level=1)
    refs = [
        "1. FastAPI Framework Documentation — https://fastapi.tiangolo.com/",
        "2. React & Vite Documentation — https://react.dev/ and https://vite.dev/",
        "3. Microsoft netsh wlan Command Reference — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan",
        "4. Android WifiManager & TelephonyManager — https://developer.android.com/develop/connectivity/wifi/wifi-scan",
        "5. PostGIS Spatial Database — https://postgis.net/documentation/",
        "6. TARANG GitHub Repository — https://github.com/Shivamborn2shine/tarangmap",
    ]
    for ref in refs:
        add_body(doc, ref)

    # ---------------- APPENDICES ----------------
    add_heading(doc, "APPENDIX A: DEPLOYMENT & LAUNCHER GUIDE", level=1)
    add_body(
        doc,
        "1. Laptop Hybrid Mode: Double-click START_TARANG_LAPTOP.bat to start the local collector "
        "and web dashboard on http://127.0.0.1:8765.\n"
        "2. Cloud Web Deployment: Connect https://github.com/Shivamborn2shine/tarangmap to Vercel "
        "or Netlify; root vercel.json and netlify.toml build apps/web automatically.\n"
        "3. Backend Tests: Run `cd services/api && python -m pytest -v`."
    )

    add_heading(doc, "APPENDIX B: SUBMISSION & VERIFICATION CHECKLIST", level=1)
    for chk in [
        "[x] Candidate details (Shivam Kumar, 2105130, BCA CyberSecurity 2024–2027, Graphic Era Deemed to be University) verified.",
        "[x] All 3 pytest tests, TypeScript build, and live Windows WLAN probe verified passing.",
        "[x] Source code pushed to https://github.com/Shivamborn2shine/tarangmap (main branch).",
        "[ ] Print/export to PDF and obtain Project Guide (Mr. Mukesh Singh) signature.",
    ]:
        add_body(doc, chk)

    doc.save(str(OUT_PATH))
    print("Saved report to:", OUT_PATH)


if __name__ == "__main__":
    build_report()
