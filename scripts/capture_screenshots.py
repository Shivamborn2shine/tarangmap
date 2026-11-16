from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "report_figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://127.0.0.1:8765", wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT_DIR / "ss_01_overview.png"), full_page=False)

        # Click Survey tab
        page.get_by_role("button", name="Survey", exact=True).click()
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT_DIR / "ss_02_live_survey.png"), full_page=False)

        # Click Map Explorer tab
        page.get_by_role("button", name="Map Explorer").click()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT_DIR / "ss_03_map_explorer.png"), full_page=False)

        # Click Insights tab
        page.get_by_role("button", name="Insights").click()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT_DIR / "ss_04_insights.png"), full_page=False)

        # Click Compare & Export tab
        page.get_by_role("button", name="Compare & Export").click()
        page.wait_for_timeout(1000)
        page.screenshot(path=str(OUT_DIR / "ss_05_compare_export.png"), full_page=False)

        browser.close()
        print("Captured 5 live screenshots in", OUT_DIR)


if __name__ == "__main__":
    capture()
