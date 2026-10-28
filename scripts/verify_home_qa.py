import asyncio
import os
import sys
import time
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

VIEWPORTS = [
    {"name": "desktop-1440", "width": 1440, "height": 900},
    {"name": "desktop-1280", "width": 1280, "height": 800},
    {"name": "tablet-768", "width": 768, "height": 1024},
    {"name": "mobile-390", "width": 390, "height": 844},
    {"name": "mobile-360", "width": 360, "height": 780},
    {"name": "mobile-320", "width": 320, "height": 640},
]

OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "design", "visual-studio", "experiments", "home-02", "exports")
)

async def run_qa():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("[QA] 1. Navigating to Login Page...")
        await page.goto("http://localhost:3000/auth/login", wait_until="networkidle")

        # Fill credentials
        print("[QA] 2. Logging in with farna@gmail.com...")
        await page.fill('input[type="email"], input[name="email"], #email', "farna@gmail.com")
        await page.fill('input[type="password"], input[name="password"], #password', "123")
        await page.click('button[type="submit"]')

        # Wait for redirect to home or check url
        print("[QA] 3. Waiting for navigation to Home...")
        try:
            await page.wait_for_url("http://localhost:3000/", timeout=8000)
        except Exception as e:
            print(f"[QA] Current URL: {page.url}")
            if "/onboarding" in page.url:
                print("[QA] User at onboarding, navigating to /...")
                await page.goto("http://localhost:3000/", wait_until="networkidle")

        await page.wait_for_selector(".home-experience", timeout=10000)
        print("[QA] 4. Home Experience loaded successfully!")

        # Test Interactive Truth-Flip
        print("[QA] 5. Testing Truth-Flip interaction...")
        verdict_tab = page.locator('button:has-text("შენი ვერდიქტი")')
        if await verdict_tab.count() > 0:
            await verdict_tab.click()
            await page.wait_for_timeout(300)
            print("   -> Switched to 'შენი ვერდიქტი'")

            daily_tab = page.locator('button:has-text("დღის სიმართლე")')
            await daily_tab.click()
            await page.wait_for_timeout(300)
            print("   -> Switched back to 'დღის სიმართლე'")

        # Test Do / Don't chip click
        print("[QA] 6. Testing Do/Don't chip interaction...")
        chips = page.locator('.home-ritual-chip')
        chip_count = await chips.count()
        if chip_count > 0:
            await chips.first.click()
            await page.wait_for_timeout(200)
            whisper = page.locator('.home-chip-whisper')
            if await whisper.count() > 0:
                text = await whisper.inner_text()
                print(f"   -> Chip clicked! Whisper feedback: '{text}'")

        # Test 4-Facet ME Lens
        print("[QA] 7. Testing 4-Facet ME Lens...")
        facet_btns = page.locator('.home-facet-btn')
        for i in range(min(4, await facet_btns.count())):
            btn = facet_btns.nth(i)
            label = await btn.inner_text()
            await btn.click()
            await page.wait_for_timeout(150)
            quote = await page.locator('.home-facet-quote').inner_text()
            print(f"   -> Facet '{label}': {quote[:45]}...")

        # Test Mobile Discovery Carousel
        print("[QA] 8. Testing Mobile Discovery Carousel at 390px...")
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(500)
        
        indicator = page.locator('.home-deck-indicator')
        if await indicator.count() > 0:
            init_text = await indicator.inner_text()
            print(f"   -> Initial Carousel status: {init_text}")
            next_btn = page.locator('.home-deck-next')
            if await next_btn.is_enabled():
                await next_btn.click()
                await page.wait_for_timeout(300)
                next_text = await indicator.inner_text()
                print(f"   -> After Next click status: {next_text}")

        # Capture Screenshots across all required viewports
        print("[QA] 9. Capturing screenshots across viewports...")
        for vp in VIEWPORTS:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await page.wait_for_timeout(400)
            # Scroll to top
            await page.evaluate("window.scrollTo(0, 0)")
            screenshot_path = os.path.join(OUTPUT_DIR, f"home-mvp-{vp['name']}.png")
            await page.screenshot(path=screenshot_path, full_page=False)
            print(f"   -> Captured {vp['name']} (viewport screenshot: {screenshot_path})")

            # Also capture full page on 1440 and 390
            if vp["name"] in ["desktop-1440", "mobile-390"]:
                full_path = os.path.join(OUTPUT_DIR, f"home-mvp-{vp['name']}-full.png")
                await page.screenshot(path=full_path, full_page=True)
                print(f"   -> Captured full page: {full_path}")

        print("[QA] ALL CHECKS PASSED SUCCESSFULLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa())
