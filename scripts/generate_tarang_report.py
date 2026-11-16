from pathlib import Path
import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "docs" / "report_figures"
OUT_PATH = ROOT / "docs" / "TARANG_Project_Report_Shivam_Kumar_40p.docx"

NAVY = RGBColor(0x10, 0x2A, 0x43)
TEAL = RGBColor(0x08, 0x7F, 0x8C)
MUTED = RGBColor(0x48, 0x65, 0x81)


def read_snippet(rel_path: str, start: int, end: int) -> str:
    p = ROOT / rel_path
    lines = p.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[start - 1 : end])


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
    r.font.size = Pt(8.2)
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
    p.paragraph_format.line_spacing = 1.22
    for r in p.runs:
        r.font.size = Pt(11)
    return p


def add_bullet(doc: docx.Document, text: str):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
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
        doc.add_paragraph()


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
    r.font.size = Pt(22)
    r.font.color.rgb = NAVY

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("TARANG — Mapping the Invisible")
    r2.bold = True
    r2.font.size = Pt(24)
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
        "institution for the award of any degree or diploma. All architectural diagrams, source code "
        "excerpts, automated test metrics, and live application screenshots documented in this report "
        "were generated directly from the implemented TARANG repository."
    )
    doc.add_paragraph("\nCandidate Signature: ________________________\nName: Shivam Kumar (Roll No. 2105130)")
    doc.add_page_break()

    # ---------------- ACKNOWLEDGEMENT ----------------
    add_heading(doc, "ACKNOWLEDGEMENT", level=1)
    add_body(
        doc,
        "I express my sincere gratitude to my project guide, Mr. Mukesh Singh, for his continuous "
        "mentorship, technical feedback, and encouragement throughout the design and implementation "
        "of TARANG. His emphasis on honest telemetry, reproducible engineering, and cybersecurity "
        "rigor shaped every layer of this platform."
    )
    add_body(
        doc,
        "I also thank the faculty and laboratory staff of the Department of Computer Science and "
        "Engineering, Graphic Era Deemed to be University, for providing the academic environment "
        "and resources required to complete this hybrid networking and cybersecurity-aware project."
    )
    doc.add_page_break()

    # ---------------- ABSTRACT ----------------
    add_heading(doc, "ABSTRACT", level=1)
    add_body(
        doc,
        "Modern wireless connectivity is routinely judged by coarse operating-system signal bars, "
        "which obscure spatial dead zones, wall attenuation, 2.4 GHz vs 5 GHz propagation differences, "
        "and the critical distinction between local Wi-Fi PHY link rate and actual ISP internet throughput. "
        "TARANG (Telecommunication Analysis, Radio Assessment & Network Geomapping) is a local-first, "
        "privacy-respecting Wi-Fi and cellular network surveying platform built as a hybrid system "
        "spanning a Windows laptop collector, an Android Kotlin radio probe, a FastAPI REST backend, "
        "and a responsive React + TypeScript web dashboard deployable on Vercel and Netlify."
    )
    add_body(
        doc,
        "Unlike cloud-locked survey tools that require user accounts or upload sensitive SSIDs, "
        "BSSIDs, and home floor plans to third-party servers, TARANG operates offline-first with "
        "SQLite/Room queues, UUIDv4 idempotent batch ingestion, honest radio-specific metric "
        "classification (never fabricating RSSI dBm from Windows signal quality percentages or "
        "forging indoor GPS precision), and a deterministic rules-based engine (Rules A–E) that "
        "translates raw RF observations into verifiable optimization tests."
    )
    doc.add_page_break()

    # ---------------- TABLE OF CONTENTS, FIGURES, TABLES ----------------
    add_heading(doc, "TABLE OF CONTENTS", level=1)
    for item in [
        "Chapter 1: Introduction (Overview, Motivation, Problem Statement, Objectives, Scope, Requirements)",
        "Chapter 2: System Analysis and Requirements (Existing vs Proposed, Functional, CyberSecurity, DFD)",
        "Chapter 3: System Design and Architecture (Hybrid Architecture, Database ER Schema, Module Matrix)",
        "Chapter 4: Core Methods, Algorithms and Source Code Working (10 Core Modules + Full Code Chunks)",
        "Chapter 5: REST API Specification (Endpoint Matrix & Canonical JSON v1 Contracts)",
        "Chapter 6: Input and Output Design (Sequence Diagram, Synthetic Live Previews, Real Laptop Screenshots)",
        "Chapter 7: Implementation, Testing, CyberSecurity and Maintenance (Pytest, Charts, STRIDE Matrix)",
        "Chapter 8: Summary, Learning Outcomes and Future Scope",
        "References",
        "Appendices A–D: Radio Thresholds, Additional Source Excerpts, Deployment Guide, Checklist",
    ]:
        add_bullet(doc, item)

    add_heading(doc, "LIST OF FIGURES", level=2)
    for fig_lbl in [
        "Figure 2.1: Level 0 & Level 1 Data Flow — Radio Collection to Insights",
        "Figure 3.1: TARANG Hybrid Local-First System Architecture",
        "Figure 3.2: Canonical Relational & Geospatial Database Schema (v1)",
        "Figure 4.1: Rules-Based Optimization Engine (Rules A–E)",
        "Figure 6.0: End-to-End Sequence — Windows Hybrid Survey & Speed Test",
        "Figure 6.1: Synthetic Privacy-Safe Indoor Wi-Fi Coverage Floor Plan Preview",
        "Figure 6.2: Synthetic Privacy-Safe Outdoor Campus 5G/LTE Walk Survey Preview",
        "Figure 6.3–6.7: Real Working Laptop Application Screenshots (http://127.0.0.1:8765)",
        "Figure 7.1: Seeded Apartment Indoor Wi-Fi RSSI by Room",
        "Figure 7.2: 2.4 GHz (Windows Laptop) vs 5 GHz (Android) Propagation by Room",
        "Figure 7.3: Automated Verification & Build Checks (100% Passing)",
    ]:
        add_bullet(doc, fig_lbl)
    doc.add_page_break()

    # ---------------- CHAPTER 1 ----------------
    add_heading(doc, "CHAPTER 1: INTRODUCTION", level=1)
    add_heading(doc, "1.1 Overview", level=2)
    add_body(
        doc,
        "TARANG (Telecommunication Analysis, Radio Assessment & Network Geomapping) is a "
        "local-first Wi-Fi and cellular network surveying platform. A user can walk through a "
        "home, office, campus building, or outdoor neighborhood using a Windows laptop or Android "
        "handset, collect real radio measurements, attach them to indoor floor-plan coordinates or "
        "outdoor GPS fixes, visualize coverage honestly, compare sessions, and receive grounded "
        "optimization suggestions."
    )
    add_heading(doc, "1.2 Background and Motivation", level=2)
    add_body(
        doc,
        "Standard operating-system signal bars compress complex RF behavior into three or four "
        "ambiguous icons. Users frequently confuse strong Wi-Fi signal with fast internet speed, "
        "or assume a 144.4 Mbps Wi-Fi PHY link rate means their ISP connection is 144 Mbps when "
        "their actual internet plan delivers ~30 Mbps. Furthermore, Windows WLAN drivers report "
        "signal quality as a percentage (%) and may or may not expose raw RSSI (dBm), whereas "
        "Android handsets expose Wi-Fi RSSI along with LTE RSRP/RSRQ and 5G NR SS-RSRP/SS-SINR "
        "subject to OS scan throttling and permissions."
    )
    add_body(
        doc,
        "TARANG was motivated by the need for an approachable, zero-clutter surveying platform that "
        "presents plain-language summaries ('Strong', 'Good', 'Fair', 'Weak', 'Unavailable') first "
        "while keeping raw engineering metrics, freshness timestamps, and source provenance one tap away."
    )
    add_heading(doc, "1.3 Problem Statement", level=2)
    add_body(
        doc,
        "To design and implement a privacy-respecting, offline-resilient hybrid network surveying "
        "platform that: (1) captures real Wi-Fi telemetry on Windows laptops via a localhost bridge "
        "and cellular/Wi-Fi telemetry on Android, (2) prevents fabricated readings or duplicate "
        "observations during offline sync, (3) distinguishes radio signal strength from internet "
        "throughput, and (4) provides an accessible React dashboard deployable on Vercel and Netlify."
    )
    add_heading(doc, "1.4 Objectives", level=2)
    for obj in [
        "Develop a FastAPI monolith backend with canonical schema_version=1 contracts and idempotent UUIDv4 batch ingestion.",
        "Build a Windows Laptop Hybrid App (apps/windows-collector) that parses live netsh wlan telemetry, buffers to SQLite, serves the web UI on http://127.0.0.1:8765, and auto-opens the browser.",
        "Create a responsive React + TypeScript + Tailwind + Recharts web dashboard (apps/web) deployable on Vercel and Netlify with automatic localhost collector detection and Local-First Demo Mode fallback.",
        "Implement an Android Kotlin RadioCapabilityProbe for permission-aware Wi-Fi RSSI and LTE/5G NR measurements.",
        "Enforce cybersecurity and privacy controls including project-salted BSSID hashing, redacted CSV/JSON exports, and STRIDE threat mitigations.",
    ]:
        add_bullet(doc, obj)

    add_heading(doc, "1.5 Scope and Limitations", level=2)
    add_body(
        doc,
        "In scope: Wi-Fi RSSI/quality/band/channel collection, LTE/5G NR RSRP/RSRQ/SINR collection "
        "on supported Android hardware, manual indoor floor-plan marking with Undo, outdoor GPS "
        "collection with accuracy halos, opt-in active TCP latency and internet speed tests, "
        "rules-based diagnostics, and redacted exports. Out of scope: software 'signal boosting', "
        "forged indoor GPS precision, and iOS third-party cellular radio diagnostics."
    )

    add_heading(doc, "1.6 Software and Hardware Requirements", level=2)
    add_table(
        doc,
        ["Component", "Specification"],
        [
            ["Backend & Collector", "Python 3.12+, FastAPI, Uvicorn, SQLAlchemy 2, Pydantic v2, HTTPX, Pytest"],
            ["Database", "SQLite (local-first default) / PostgreSQL 16 + PostGIS 3.4 (Docker Compose)"],
            ["Web Frontend", "React 18, TypeScript 5, Vite 5, Tailwind CSS, Recharts, Lucide Icons"],
            ["Windows Hardware", "Windows 10/11 laptop with WLAN adapter (verified on MediaTek MT7921 Wi-Fi 6)"],
            ["Android Target", "Android 10+ (API 29+) with Fine Location & Phone State permissions"],
            ["Cloud Hosting", "Vercel (vercel.json) and Netlify (netlify.toml) for static SPA hosting"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 2 ----------------
    add_heading(doc, "CHAPTER 2: SYSTEM ANALYSIS AND REQUIREMENTS", level=1)
    add_heading(doc, "2.1 Existing vs Proposed System", level=2)
    add_table(
        doc,
        ["Dimension", "Existing Commercial Tools", "TARANG (Proposed Hybrid System)"],
        [
            ["Account & Cloud Lock-in", "Mandatory account creation; cloud upload", "Local-first; zero login required for MVP"],
            ["Data Honesty", "Converts Windows % to fake dBm; hides stale scans", "Stores raw units, freshness_ms, metric_source, missing_reason"],
            ["Indoor Location", "Pretends GPS works accurately indoors", "Manual tap-to-mark floor plan with room labels & Undo"],
            ["Throughput vs Signal", "Blurs PHY link rate with ISP speed", "Separates Wi-Fi PHY Link Rate from opt-in Active Speed Test"],
            ["Accessibility", "Relies on color-only heatmaps", "Pairs color with text badges, units, and accessible List View"],
        ],
    )

    add_heading(doc, "2.2 Functional Requirements", level=2)
    add_table(
        doc,
        ["ID", "Requirement", "Implementation Module"],
        [
            ["FR-01", "Create indoor/outdoor survey projects & upload floor plans", "services/api/app/routers/projects.py"],
            ["FR-02", "Register device hardware capabilities & random UUID", "services/api/app/routers/devices.py"],
            ["FR-03", "Start, pause, resume, and finish survey sessions", "services/api/app/routers/sessions.py"],
            ["FR-04", "Idempotent batch ingest up to 500 observations", "services/api/app/routers/observations.py"],
            ["FR-05", "Live Windows WLAN scan, SQLite queue & active speed test", "apps/windows-collector/tarang_collector/"],
            ["FR-06", "Rules-based insights (Rules A–E) & session comparison", "services/api/app/analysis.py & exports.py"],
        ],
    )

    add_heading(doc, "2.3 Non-Functional and CyberSecurity Requirements", level=2)
    for req in [
        "Loopback Isolation: Windows collector binds to 127.0.0.1:8765 by default to prevent unauthorized LAN probing.",
        "Privacy by Default: BSSIDs are hashed with project-specific salts; exports support redact=true to mask SSIDs and outdoor GPS coordinates.",
        "Accessibility (WCAG AA): Touch targets >= 44px (48px on sticky mobile controls), tabular numerals, and non-color-only status badges.",
        "Offline Resilience: Local SQLite/Room queues survive process restarts and deduplicate on retry.",
    ]:
        add_bullet(doc, req)

    add_heading(doc, "2.4 Data Flow Diagrams", level=2)
    add_figure(doc, FIG_DIR / "fig_dfd.png", "Figure 2.1: Level 0 & Level 1 Data Flow — Radio Collection to Insights.")
    doc.add_page_break()

    # ---------------- CHAPTER 3 ----------------
    add_heading(doc, "CHAPTER 3: SYSTEM DESIGN AND ARCHITECTURE", level=1)
    add_heading(doc, "3.1 Hybrid Monolith & Laptop Bridge Architecture", level=2)
    add_body(
        doc,
        "TARANG employs a hybrid monolith architecture. On a Windows laptop, `tarang_collector` "
        "imports the FastAPI backend (`services/api/app/main.py`), mounts live Windows hardware "
        "routes under `/api/v1/windows/*`, serves the compiled React production bundle (`apps/web/dist`), "
        "and launches the user's browser to `http://127.0.0.1:8765`. Simultaneously, the exact same "
        "React codebase can be deployed statically to Vercel or Netlify and will automatically connect "
        "to the local laptop collector if running, or operate in Local-First Demo Mode."
    )
    add_figure(doc, FIG_DIR / "fig_architecture.png", "Figure 3.1: TARANG Hybrid Local-First System Architecture.")

    add_heading(doc, "3.2 Canonical Database Schema & ER Design", level=2)
    add_body(
        doc,
        "All observations conform to `schema_version=1` (`packages/contracts/observation.schema.json`). "
        "A base `observations` table stores common timestamps (`observed_at`, `recorded_at`, `received_at`), "
        "`freshness_ms`, `metric_source`, `missing_reason`, and location (`indoor` normalized `[0,1]` "
        "coordinates or `outdoor` WGS84 `lat`/`lon` + `gps_accuracy_m`), while technology-specific "
        "metrics live in `wifi_observations`, `cell_observations`, and `active_tests`."
    )
    add_figure(doc, FIG_DIR / "fig_er_schema.png", "Figure 3.2: Canonical Relational & Geospatial Database Schema (v1).")

    add_heading(doc, "3.3 SQLAlchemy ORM Models (services/api/app/models.py)", level=2)
    add_code_block(
        doc,
        "Excerpt 3.1: services/api/app/models.py — Core Observation & WifiObservation Models",
        read_snippet("services/api/app/models.py", 75, 130),
    )

    add_heading(doc, "3.4 Package & Module Responsibility Matrix", level=2)
    add_table(
        doc,
        ["Module Path", "Responsibility"],
        [
            ["services/api/app/main.py", "FastAPI lifespan, DB table creation, demo seeding, CORS, static mounts"],
            ["services/api/app/analysis.py", "Radio-specific tier rules & Rules A–E recommendation engine"],
            ["services/api/app/routers/observations.py", "Idempotent /observations/batch ingest & query endpoints"],
            ["services/api/app/routers/exports.py", "Redacted CSV/JSON export & session comparison with caveats"],
            ["apps/windows-collector/tarang_collector/probe.py", "netsh wlan interface/network parser, TCP probe, active speed test"],
            ["apps/windows-collector/tarang_collector/storage.py", "Resilient SQLite offline queue (enqueue, peek_batch, remove_ids)"],
            ["apps/windows-collector/tarang_collector/server.py", "Hybrid localhost FastAPI server + background sampling thread"],
            ["apps/web/src/api.ts", "Auto-detects localhost collector (no-store) or Demo Mode fallback"],
            ["apps/web/src/components/LiveSurveyView.tsx", "Glanceable hero card, floor-plan tap marker, latency & speed test"],
            ["apps/android/.../RadioCapabilityProbe.kt", "Permission-aware Android WifiManager & TelephonyManager probe"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 4 ----------------
    add_heading(doc, "CHAPTER 4: CORE METHODS, ALGORITHMS AND SOURCE CODE WORKING", level=1)

    add_heading(doc, "4.1 Windows WLAN Probe & Honest Metric Extraction (probe.py)", level=2)
    add_body(
        doc,
        "The `probe_windows_wifi()` function invokes `netsh wlan show interfaces` as a subprocess "
        "without spawning a visible console window (`CREATE_NO_WINDOW`). It parses key-value pairs "
        "for SSID, hashed BSSID, band, channel, radio type, link rates, signal quality %, and RSSI "
        "(only when explicitly exposed by the WLAN driver, never fabricated from %)."
    )
    add_code_block(
        doc,
        "Excerpt 4.1: apps/windows-collector/tarang_collector/probe.py — probe_windows_wifi()",
        read_snippet("apps/windows-collector/tarang_collector/probe.py", 51, 125),
    )

    add_heading(doc, "4.2 Active TCP Latency & Opt-In Internet Speed Test (probe.py)", level=2)
    add_body(
        doc,
        "To separate local Wi-Fi PHY link rate (e.g., 144.4 Mbps) from end-to-end ISP throughput, "
        "`run_active_tcp_probe()` measures TCP handshake latency/jitter to `1.1.1.1:443`, while "
        "`run_active_speed_test()` performs an opt-in streamed download/upload benchmark against "
        "`speed.cloudflare.com` and reports actual Download and Upload Mbps."
    )
    add_code_block(
        doc,
        "Excerpt 4.2: apps/windows-collector/tarang_collector/probe.py — run_active_speed_test()",
        read_snippet("apps/windows-collector/tarang_collector/probe.py", 185, 229),
    )

    add_heading(doc, "4.3 SQLite Offline Queue & Collector Loop (storage.py & server.py)", level=2)
    add_body(
        doc,
        "`OfflineQueue` persists each captured observation to `~/.tarang/windows_collector_queue.db` "
        "before attempting database flush, ensuring zero observation loss if the app closes mid-survey."
    )
    add_code_block(
        doc,
        "Excerpt 4.3: apps/windows-collector/tarang_collector/storage.py — OfflineQueue",
        read_snippet("apps/windows-collector/tarang_collector/storage.py", 1, 56),
    )
    add_code_block(
        doc,
        "Excerpt 4.4: apps/windows-collector/tarang_collector/server.py — Background Collector Loop",
        read_snippet("apps/windows-collector/tarang_collector/server.py", 64, 122),
    )

    add_heading(doc, "4.4 Radio-Specific Signal Tier Classification (analysis.py)", level=2)
    add_body(
        doc,
        "Each radio technology uses its own calibrated thresholds rather than a single universal dBm scale."
    )
    add_code_block(
        doc,
        "Excerpt 4.5: services/api/app/analysis.py — Tier Classification Rules",
        read_snippet("services/api/app/analysis.py", 1, 78),
    )

    add_heading(doc, "4.5 Rules-Based Optimization Engine (analysis.py)", level=2)
    add_figure(doc, FIG_DIR / "fig_rules_pipeline.png", "Figure 4.1: Rules-Based Optimization Engine (Rules A–E).")
    add_code_block(
        doc,
        "Excerpt 4.6: services/api/app/analysis.py — Rules A, B, C, E Insights Generator",
        read_snippet("services/api/app/analysis.py", 125, 195),
    )

    add_heading(doc, "4.6 Idempotent Batch Ingestion (observations.py)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.7: services/api/app/routers/observations.py — Deduplication on Retry",
        read_snippet("services/api/app/routers/observations.py", 75, 130),
    )

    add_heading(doc, "4.7 Session Comparison & Redacted Export (exports.py)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.8: services/api/app/routers/exports.py — Session Comparison Caveats",
        read_snippet("services/api/app/routers/exports.py", 100, 155),
    )

    add_heading(doc, "4.8 Hybrid Frontend Auto-Detection & Live Polling (api.ts)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.9: apps/web/src/api.ts — detectBackend() Hybrid Discovery",
        read_snippet("apps/web/src/api.ts", 23, 62),
    )

    add_heading(doc, "4.9 Android Permission-Aware RadioCapabilityProbe (Kotlin)", level=2)
    add_code_block(
        doc,
        "Excerpt 4.10: apps/android/.../RadioCapabilityProbe.kt — Safe Telephony & Wi-Fi Capture",
        read_snippet("apps/android/app/src/main/java/com/tarang/collector/RadioCapabilityProbe.kt", 33, 95),
    )
    doc.add_page_break()

    # ---------------- CHAPTER 5 ----------------
    add_heading(doc, "CHAPTER 5: REST API SPECIFICATION", level=1)
    add_table(
        doc,
        ["Method & Endpoint", "Function", "Auth / Scope"],
        [
            ["GET /health", "API and database readiness check", "Local / Public"],
            ["GET, POST /api/v1/projects", "Browse or create survey projects", "Local"],
            ["POST /api/v1/projects/{id}/floorplans", "Upload floor-plan image & dimensions", "Local"],
            ["POST /api/v1/devices/register", "Register device capabilities & UUID", "Local"],
            ["GET, POST, PATCH /api/v1/sessions", "Manage survey session lifecycle", "Local"],
            ["POST /api/v1/observations/batch", "Idempotent batch ingest (<= 500 items)", "Local"],
            ["GET /api/v1/projects/{id}/summary", "Distributions, weak spots & Rules A–E", "Local"],
            ["GET /api/v1/projects/{id}/export", "CSV/JSON export with redact=true", "Local"],
            ["GET /api/v1/compare", "Compare two sessions with caveats", "Local"],
            ["GET /api/v1/windows/live-scan", "Live Windows netsh wlan telemetry", "Loopback 8765"],
            ["POST /api/v1/windows/speed-test", "Opt-in active download/upload Mbps test", "Loopback 8765"],
        ],
    )
    add_code_block(
        doc,
        "Example 5.1: Canonical Observation Batch Response (POST /api/v1/observations/batch)",
        """
{
  "batch_id": "9f1c2e40-8b3d-4c1a-9a12-112233445566",
  "accepted": 1,
  "duplicate": 0,
  "rejected": 0,
  "items": [{ "id": "a1b2c3d4-...", "status": "accepted", "reason": null }]
}
""",
    )
    add_code_block(
        doc,
        "Example 5.2: Live Windows WLAN Scan Response (GET /api/v1/windows/live-scan)",
        """
{
  "interface": {
    "available": true,
    "adapter_description": "MediaTek MT7921 Wi-Fi 6 802.11ax PCIe Adapter",
    "state": "connected",
    "ssid": "Airtel_suna_6489",
    "band": "2.4 GHz",
    "channel": 6,
    "quality_percent": 77,
    "rssi_dbm": -61,
    "metric_source": "windows_netsh_wlan"
  }
}
""",
    )
    doc.add_page_break()

    # ---------------- CHAPTER 6 ----------------
    add_heading(doc, "CHAPTER 6: INPUT AND OUTPUT DESIGN WITH GENERATED LIVE PREVIEWS & SCREENSHOTS", level=1)
    add_heading(doc, "6.1 End-to-End Hybrid Survey Sequence", level=2)
    add_figure(doc, FIG_DIR / "fig_sequence.png", "Figure 6.0: End-to-End Sequence — Windows Hybrid Survey & Speed Test.")

    add_heading(doc, "6.2 Generated Synthetic Privacy-Safe Live Preview Demonstrations", level=2)
    add_body(
        doc,
        "To demonstrate indoor and outdoor coverage visualization without exposing private home "
        "photographs or personal coordinates, the following synthetic preview scenes were generated "
        "using TARANG's visual palette (#F7FAFC, #102A43, #087F8C, #168A5B, #D99C26, #D95D54)."
    )
    add_figure(
        doc,
        FIG_DIR / "preview_indoor_wifi.jpg",
        "Figure 6.1: Synthetic Privacy-Safe Indoor Wi-Fi Coverage Floor Plan Preview.",
        width_in=5.6,
    )
    add_figure(
        doc,
        FIG_DIR / "preview_outdoor_cellular.jpg",
        "Figure 6.2: Synthetic Privacy-Safe Outdoor Campus 5G/LTE Walk Survey Preview.",
        width_in=5.6,
    )
    doc.add_page_break()

    add_heading(doc, "6.3 Live Working Application Screenshots (Captured from Laptop at 127.0.0.1:8765)", level=2)
    add_body(
        doc,
        "The screenshots below were captured directly from the live TARANG Hybrid Application "
        "running on http://127.0.0.1:8765 on Windows 11 with the MediaTek MT7921 Wi-Fi 6 adapter."
    )
    add_figure(doc, FIG_DIR / "ss_01_overview.png", "Figure 6.3: Live Overview Dashboard & Windows Laptop Collector Card (127.0.0.1:8765).", width_in=5.9)
    add_figure(doc, FIG_DIR / "ss_02_live_survey.png", "Figure 6.4: Live Survey View — Real-Time Windows WLAN Reading, Speed Test & Floor Plan Marker.", width_in=5.9)
    add_figure(doc, FIG_DIR / "ss_03_map_explorer.png", "Figure 6.5: Map Explorer — Measured Points, Legend, and Point Inspector.", width_in=5.9)
    add_figure(doc, FIG_DIR / "ss_04_insights.png", "Figure 6.6: Insights & Analytics — Signal Distributions & Rules-Based Recommendations.", width_in=5.9)
    add_figure(doc, FIG_DIR / "ss_05_compare_export.png", "Figure 6.7: Compare & Export — Session Comparison Caveats & Redacted CSV/JSON Export.", width_in=5.9)

    add_heading(doc, "6.4 Responsive Viewport & Interaction Budget Specification", level=2)
    add_table(
        doc,
        ["Viewport Width", "Layout Mode", "Key Ergonomic & Accessibility Behavior"],
        [
            ["320–599 px (Mobile)", "Single column, bottom nav, sticky action bar", "48px thumb-zone Start/Pause/Finish controls; stacked cards"],
            ["600–899 px (Tablet)", "Two-column selective grids", "Map primary; point inspector in clean stacked panel"],
            ["900–1279 px (Laptop)", "Side rail + main map + inspector", "Balanced Recharts distribution & RSSI sequence charts"],
            [">= 1280 px (Desktop)", "Persistent slim sidebar + expansive map", "Full analyst controls with persistent unit-labeled legend"],
        ],
    )
    doc.add_page_break()

    # ---------------- CHAPTER 7 ----------------
    add_heading(doc, "CHAPTER 7: IMPLEMENTATION, TESTING, CYBERSECURITY AND MAINTENANCE", level=1)
    add_heading(doc, "7.1 Automated Verification Results", level=2)
    add_table(
        doc,
        ["Test Case / Verification Check", "Scope", "Result"],
        [
            ["test_health_and_seeded_projects", "FastAPI /health & seeded demo projects", "PASSED"],
            ["test_idempotent_batch_ingest", "Duplicate UUID batch deduplication", "PASSED"],
            ["test_summary_and_export", "Rules A–E summary & redacted CSV/JSON export", "PASSED"],
            ["tsc -b && vite build", "TypeScript strict check & Vite production bundle", "PASSED"],
            ["Windows Hybrid Probe", "Live netsh wlan & FastAPI localhost bridge (8765)", "PASSED"],
        ],
    )
    add_figure(doc, FIG_DIR / "fig_signal_chart.png", "Figure 7.1: Seeded Apartment Indoor Wi-Fi RSSI by Room.")
    add_figure(doc, FIG_DIR / "fig_band_comparison.png", "Figure 7.2: 2.4 GHz (Windows Laptop) vs 5 GHz (Android) Propagation by Room.")
    add_figure(doc, FIG_DIR / "fig_test_breakdown.png", "Figure 7.3: Automated Verification & Build Checks (100% Passing).")

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

    add_heading(doc, "7.3 Maintenance Checklist", level=2)
    for m in [
        "Restart START_TARANG_LAPTOP.bat after updating Python modules in apps/windows-collector or services/api.",
        "Run `cd apps/web && npm run build` before committing frontend updates so localhost port 8765 serves the latest bundle.",
        "Keep `~/.tarang/windows_collector_queue.db` and `services/api/tarang.db` out of version control (enforced by .gitignore).",
    ]:
        add_bullet(doc, m)
    doc.add_page_break()

    # ---------------- CHAPTER 8 ----------------
    add_heading(doc, "CHAPTER 8: SUMMARY, LEARNING OUTCOMES AND FUTURE SCOPE", level=1)
    add_heading(doc, "8.1 Summary", level=2)
    add_body(
        doc,
        "TARANG delivers a complete, local-first hybrid network surveying platform that bridges "
        "Windows laptop WLAN hardware, Android cellular/Wi-Fi probing, a FastAPI REST backend, and "
        "a Vercel/Netlify-ready React web dashboard while upholding strict metric honesty and "
        "privacy-by-default engineering."
    )
    add_heading(doc, "8.2 Learning Outcomes", level=2)
    for lo in [
        "Designed and implemented an idempotent FastAPI + SQLAlchemy 2 REST API with schema_version=1 contracts.",
        "Built a Windows localhost hybrid collector parsing live netsh wlan telemetry without fabricating RSSI dBm.",
        "Distinguished local Wi-Fi PHY link rate from actual ISP internet throughput via opt-in active speed testing.",
        "Applied STRIDE cybersecurity threat modeling and privacy redaction to geospatial network surveys.",
    ]:
        add_bullet(doc, lo)
    add_heading(doc, "8.3 Future Scope", level=2)
    for f in [
        "Complete Android Jetpack Compose APK release with Room background foreground-service sync.",
        "Automated PDF coverage report generation and multi-device LAN project collaboration.",
        "Dockerized PostgreSQL + PostGIS spatial indexing for campus-scale outdoor surveys.",
    ]:
        add_bullet(doc, f)

    # ---------------- REFERENCES ----------------
    add_heading(doc, "REFERENCES", level=1)
    for ref in [
        "1. FastAPI Framework Documentation — https://fastapi.tiangolo.com/",
        "2. React & Vite Documentation — https://react.dev/ and https://vite.dev/",
        "3. Microsoft netsh wlan Command Reference — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-wlan",
        "4. Android WifiManager & TelephonyManager — https://developer.android.com/develop/connectivity/wifi/wifi-scan",
        "5. PostGIS Spatial Database — https://postgis.net/documentation/",
        "6. TARANG GitHub Repository — https://github.com/Shivamborn2shine/tarangmap",
    ]:
        add_body(doc, ref)

    # ---------------- APPENDICES ----------------
    add_heading(doc, "APPENDIX A: RADIO SIGNAL THRESHOLDS REFERENCE", level=1)
    add_table(
        doc,
        ["Tier", "Wi-Fi RSSI (dBm)", "Windows Quality (%)", "LTE RSRP / 5G SS-RSRP (dBm)"],
        [
            ["Strong", ">= -55 dBm", ">= 80%", ">= -85 dBm"],
            ["Good", "-56 to -67 dBm", "60% to 79%", "-86 to -98 dBm"],
            ["Fair", "-68 to -75 dBm", "40% to 59%", "-99 to -110 dBm"],
            ["Weak", "< -75 dBm", "< 40%", "< -110 dBm"],
            ["Unavailable", "null (missing_reason)", "null (missing_reason)", "null (missing_reason)"],
        ],
    )

    add_heading(doc, "APPENDIX B: ADDITIONAL SOURCE EXCERPTS", level=1)
    add_code_block(
        doc,
        "Excerpt B.1: services/api/app/schemas.py — Canonical ObservationIn Contract",
        read_snippet("services/api/app/schemas.py", 96, 145),
    )
    add_code_block(
        doc,
        "Excerpt B.2: apps/web/src/components/LiveSurveyView.tsx — Floor Plan Normalized Tap Marker",
        read_snippet("apps/web/src/components/LiveSurveyView.tsx", 125, 165),
    )
    add_code_block(
        doc,
        "Excerpt B.3: apps/web/src/components/MapExplorerView.tsx — Bounded Heatmap & Point Inspector",
        read_snippet("apps/web/src/components/MapExplorerView.tsx", 145, 200),
    )
    add_code_block(
        doc,
        "Excerpt B.4: services/api/app/main.py — FastAPI Lifespan & Static Mounts",
        read_snippet("services/api/app/main.py", 1, 52),
    )
    add_code_block(
        doc,
        "Excerpt B.5: apps/windows-collector/tarang_collector/server.py — Hybrid App & Capabilities",
        read_snippet("apps/windows-collector/tarang_collector/server.py", 170, 235),
    )
    doc.add_page_break()

    add_heading(doc, "APPENDIX C: DEPLOYMENT & LAUNCHER GUIDE", level=1)
    add_body(
        doc,
        "1. Laptop Hybrid Mode: Double-click START_TARANG_LAPTOP.bat to start the local collector "
        "and web dashboard on http://127.0.0.1:8765.\n"
        "2. Cloud Web Deployment: Connect https://github.com/Shivamborn2shine/tarangmap to Vercel "
        "or Netlify; root vercel.json and netlify.toml build apps/web automatically.\n"
        "3. Backend Tests: Run `cd services/api && python -m pytest -v`."
    )

    add_heading(doc, "APPENDIX D: SUBMISSION & VERIFICATION CHECKLIST", level=1)
    for chk in [
        "[x] Candidate details (Shivam Kumar, 2105130, BCA CyberSecurity 2024–2027, Graphic Era Deemed to be University) verified.",
        "[x] All 3 pytest tests, TypeScript build, and live Windows WLAN probe verified passing.",
        "[x] Real working screenshots captured from http://127.0.0.1:8765 and synthetic privacy-safe previews generated.",
        "[x] Source code pushed to https://github.com/Shivamborn2shine/tarangmap (main branch).",
        "[ ] Print/export to PDF and obtain Project Guide (Mr. Mukesh Singh) signature.",
    ]:
        add_body(doc, chk)

    doc.save(str(OUT_PATH))
    print("Saved expanded report to:", OUT_PATH)


if __name__ == "__main__":
    build_report()
