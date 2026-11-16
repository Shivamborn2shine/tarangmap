# TARANG — Mapping the Invisible

**T**elecommunication **A**nalysis, **R**adio **A**ssessment & **N**etwork **G**eomapping

TARANG is a local-first Wi-Fi and cellular network surveying platform with a **Windows Laptop Hybrid Collector** (`http://127.0.0.1:8765`), **FastAPI backend**, **React + TypeScript web dashboard** (ready for Vercel & Netlify), and **Android Kotlin probe**.

## Architecture

- `apps/web`: React + Vite + Tailwind + Recharts dashboard (`vercel.json` & `netlify.toml` ready). Works standalone in Local-First Demo Mode or connects automatically to the Laptop Hybrid Collector on `http://127.0.0.1:8765`.
- `apps/windows-collector`: Windows laptop hybrid app (`netsh wlan` live Wi-Fi probe, SQLite offline queue, active TCP latency probe, localhost HTTP bridge on port `8765`, and auto-browser launcher).
- `services/api`: FastAPI + SQLAlchemy 2 REST API (`schema_version=1`, idempotent batch ingest, rules-based insights, session comparison, CSV/JSON export).
- `apps/android`: Android Kotlin `RadioCapabilityProbe` & `AndroidManifest.xml` for permission-aware Wi-Fi and LTE/5G collection.
- `packages/contracts`: Canonical JSON Schema (`observation.schema.json`).
- `infra`: Docker Compose for PostgreSQL + PostGIS + FastAPI.

## Quick Start

### 1. Run the Windows Laptop Hybrid App (Recommended on Laptop)
Double-click `START_TARANG_LAPTOP.bat` or run:
```powershell
$env:PYTHONPATH="apps/windows-collector;services/api"
python -m tarang_collector --port 8765
```
This probes your Windows Wi-Fi adapter, starts the local API + web dashboard on `http://127.0.0.1:8765`, and opens your browser automatically.

### 2. Deploy Web Dashboard to Vercel or Netlify
Root `vercel.json` and `netlify.toml` are already configured to build `apps/web` (`apps/web/dist`). Just import this repository into Vercel or Netlify and deploy.

### 3. Run Backend Tests
```powershell
cd services/api
python -m pytest -v
```
