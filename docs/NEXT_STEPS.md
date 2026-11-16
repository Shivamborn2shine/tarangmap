# Next Steps

1. Deploy `apps/web` to **Vercel** or **Netlify** (root `vercel.json` and `netlify.toml` are pre-configured).
2. Run `START_TARANG_LAPTOP.bat` on Windows to launch the Laptop Hybrid Collector on `http://127.0.0.1:8765` (or build `TARANG-Laptop.exe` via `apps/windows-collector/build_exe.ps1`).
3. Open the Android Studio project in `apps/android` to build and test the on-device APK for LTE/5G + Wi-Fi collection.
4. For multi-user LAN/Docker PostgreSQL+PostGIS deployment, run `docker compose -f infra/docker-compose.yml up`.
