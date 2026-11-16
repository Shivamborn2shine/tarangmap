import argparse
import threading
import time
import webbrowser
import uvicorn

from .probe import probe_windows_wifi


def main() -> None:
    parser = argparse.ArgumentParser(description="TARANG Windows Laptop Hybrid App & Localhost Bridge")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Localhost port (default 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    parser.add_argument("--web-url", default="", help="Optional external web dashboard URL (e.g. Vercel/Netlify URL)")
    args = parser.parse_args()

    scan = probe_windows_wifi()
    print("=" * 60)
    print("  TARANG — Mapping the Invisible (Laptop Hybrid Companion)")
    print("=" * 60)
    print(f"  Adapter : {scan.get('adapter_description') or 'Not detected'}")
    print(f"  State   : {scan.get('state')} | SSID: {scan.get('ssid') or 'N/A'}")
    print(f"  Quality : {scan.get('quality_percent')}% | RSSI: {scan.get('rssi_dbm')} dBm")
    print(f"  Local   : http://{args.host}:{args.port}")
    print("=" * 60)

    if not args.no_browser:
        target = args.web_url.rstrip("/") if args.web_url else f"http://{args.host}:{args.port}"
        if args.web_url:
            target = f"{target}?api=http://{args.host}:{args.port}"

        def _open():
            time.sleep(1.2)
            webbrowser.open(target)

        threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(
        "tarang_collector.server:hybrid_app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
