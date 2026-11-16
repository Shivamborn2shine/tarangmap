# TARANG Implementation Log

## 2026-11-16 — Full Hybrid Platform + Web Dashboard + Windows Collector
- Initialized monorepo (`docs/`, `packages/contracts/`, `services/api/`, `apps/web/`, `apps/windows-collector/`, `apps/android/`, `infra/`, `samples/`).
- Implemented canonical observation contract (`schema_version=1`) in `packages/contracts/observation.schema.json`.
- Built FastAPI backend (`services/api`) with SQLAlchemy 2, idempotent `/api/v1/observations/batch`, `/api/v1/projects/{id}/summary` (Rules A–E), `/api/v1/compare`, and `/api/v1/projects/{id}/export` (CSV/JSON with privacy redaction). Verified with `pytest` (3/3 passing).
- Built Windows Laptop Hybrid Collector (`apps/windows-collector`) using real `netsh wlan show interfaces` and `netsh wlan show networks mode=bssid`, SQLite offline queue, active TCP latency probe, and localhost HTTP bridge (`127.0.0.1:8765`) that serves the web dashboard and auto-opens the browser.
- Built React + TypeScript + Tailwind + Recharts web dashboard (`apps/web`) with Vercel (`vercel.json`) and Netlify (`netlify.toml`) deployment configs, Local-First Demo Mode fallback, Survey Wizard, Live Survey + Indoor Floor Plan Tap Marker, Map Explorer (Measured Points + Bounded Heatmap + List View), Analytics & Recommendations, and Session Compare & Export. Verified with `tsc -b && vite build`.
- Added Android Kotlin `RadioCapabilityProbe.kt` and `AndroidManifest.xml` with `foregroundServiceType="location"`.
