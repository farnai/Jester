import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VIEWPORTS = [
    {"name": "mobile-360", "width": 360, "height": 780},
    {"name": "mobile-390", "width": 390, "height": 844},
    {"name": "tablet-768", "width": 768, "height": 1024},
    {"name": "desktop-1280", "width": 1280, "height": 800},
    {"name": "desktop-1440", "width": 1440, "height": 900},
]

ARTIFACTS_DIR = os.environ.get(
    "ARTIFACTS_DIR",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "artifacts")),
)

async def run_qa():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("[QA] 1. Navigating to Login...")
        await page.goto("http://localhost:3000/auth/login", wait_until="networkidle")

        print("[QA] 2. Logging in with dev@jester.app...")
        await page.fill('input[type="email"], input[name="email"], #email', "dev@jester.app")
        await page.fill('input[type="password"], input[name="password"], #password', "password123")
        await page.click('button[type="submit"]')

        print("[QA] 3. Waiting for navigation to Home...")
        try:
            await page.wait_for_url("http://localhost:3000/", timeout=8000)
        except Exception:
            if "/onboarding" in page.url:
                print("[QA] Redirecting to Home from onboarding...")
                await page.goto("http://localhost:3000/", wait_until="networkidle")

        # Wait for the home layout
        await page.wait_for_selector(".jester-home-container", timeout=12000)
        print("[QA] 4. Rebuilt Home Page container loaded successfully!")

        # Verify Section 1: Daily Energy
        print("[QA] 5. Verifying Section 1: Daily Energy...")
        daily_sec = page.locator(".home-daily-section")
        assert await daily_sec.count() > 0, "Daily energy section missing!"
        quote_text = await page.locator(".home-daily-quote").inner_text()
        print(f"   -> Daily quote: {quote_text[:60]}...")
        
        # Test expandable "რატომ?" drawer
        why_btn = page.locator(".home-why-toggle-btn")
        await why_btn.click()
        await page.wait_for_selector("#home-why-details", state="visible")
        why_text = await page.locator("#home-why-details").inner_text()
        print(f"   -> 'რატომ?' drawer expanded: {why_text[:80]}...")

        # Verify Section 2: Do & Don't
        print("[QA] 6. Verifying Section 2: Do & Don't...")
        dodont_sec = page.locator(".home-dodont-section")
        assert await dodont_sec.count() > 0, "Do & Don't section missing!"
        do_items = await page.locator(".home-do-item").all_inner_texts()
        dont_items = await page.locator(".home-dont-item").all_inner_texts()
        print(f"   -> DO items count: {len(do_items)} -> {do_items}")
        print(f"   -> DONT items count: {len(dont_items)} -> {dont_items}")

        # Verify Section 3: Personal Insights (7 layers)
        print("[QA] 7. Verifying Section 3: Personal Insights (7 Layers)...")
        insights_sec = page.locator(".home-insights-section")
        assert await insights_sec.count() > 0, "Personal Insights section missing!"
        layer_cards = page.locator(".home-layer-card")
        layer_count = await layer_cards.count()
        print(f"   -> Layers rendered count: {layer_count}")
        assert layer_count == 7, f"Expected 7 layers, got {layer_count}"

        # Test toggling layer 2
        layer_2_toggle = page.locator("#layer-header-layer_2_cognition")
        if await layer_2_toggle.count() > 0:
            await layer_2_toggle.click()
            await page.wait_for_selector("#layer-panel-layer_2_cognition", state="visible")
            print("   -> Toggled and expanded Layer 2 (როგორ აზროვნებ)")

        # Verify Section 4: New People (18+)
        print("[QA] 8. Verifying Section 4: New People...")
        people_sec = page.locator(".home-people-section")
        assert await people_sec.count() > 0, "New People section missing!"
        person_cards = page.locator(".home-person-card")
        people_count = await person_cards.count()
        print(f"   -> New people cards count: {people_count}")
        assert people_count > 0, "Expected at least 1 person card!"
        first_person_name = await page.locator(".home-person-name").first.inner_text()
        print(f"   -> First person: {first_person_name}")

        # Verify responsive snapshots and zero horizontal overflow
        print("[QA] 9. Checking responsive viewports & capturing screenshots...")
        for vp in VIEWPORTS:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await page.wait_for_timeout(400)

            # Check horizontal overflow
            scroll_width = await page.evaluate("document.documentElement.scrollWidth")
            client_width = await page.evaluate("document.documentElement.clientWidth")
            overflow = scroll_width > client_width
            print(f"   - Viewport {vp['name']} ({vp['width']}x{vp['height']}): scrollWidth={scroll_width}, clientWidth={client_width}, overflow={overflow}")
            assert not overflow, f"Horizontal overflow detected on viewport {vp['name']}!"

            # Take full page screenshot
            full_path = os.path.join(ARTIFACTS_DIR, f"rebuilt-home-final-{vp['name']}-full.png")
            await page.screenshot(path=full_path, full_page=True)
            print(f"     Captured: {full_path}")

        print("[QA] 10. All checks PASSED successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa())

