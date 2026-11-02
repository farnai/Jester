import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARTIFACTS_DIR = os.environ.get(
    "ARTIFACTS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts"),
)

async def run_qa():
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # DESKTOP RUN (1280x800)
        # -------------------------------------------------------------
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("[QA] 1. Navigating to Login...")
        await page.goto("http://127.0.0.1:3000/auth/login", wait_until="networkidle")

        print("[QA] 2. Logging in with dev@jester.app...")
        await page.fill('#login-email, input[type="email"], input[name="email"]', "dev@jester.app")
        await page.fill('#login-password, input[type="password"], input[name="password"]', "password123")
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)

        if "/onboarding" in page.url or page.url != "http://127.0.0.1:3000/":
            await page.goto("http://127.0.0.1:3000/", wait_until="networkidle")

        await page.wait_for_selector(".jester-home-container", timeout=15000)
        await page.wait_for_selector(".home-daily-quote", timeout=15000)
        print("[QA] 3. Home page loaded successfully!")

        # Verify Tab 1 (დღის ენერგია) is active by default
        daily_tab = page.locator("#tab-daily-energy")
        assert await daily_tab.get_attribute("aria-selected") == "true", "Daily tab must be selected initially"
        daily_quote_text = await page.locator("#panel-daily-energy .home-daily-quote").inner_text()
        print(f"   -> Daily Tab Active by default: Quote: {daily_quote_text[:50]}...")

        # Verify Do & Don't is present and untouched
        dodont_items = await page.locator(".home-dodont-item").count()
        assert dodont_items == 6, f"Expected 6 Do/Don't items, found {dodont_items}"
        print(f"   -> Section 2 (Do & Don't) intact: {dodont_items} items")

        # Switch to Tab 2 (კვირის ენერგია ✦)
        print("[QA] 4. Switching to Weekly Energy Tab...")
        weekly_tab = page.locator("#tab-weekly-energy")
        await weekly_tab.click()
        await page.wait_for_timeout(1000)

        assert await weekly_tab.get_attribute("aria-selected") == "true", "Weekly tab must be selected after click"
        print("   -> Weekly Tab active!")

        # Verify Locked State
        await page.wait_for_selector(".home-weekly-locked-card", timeout=8000)
        notice_text = await page.locator(".home-notice-text").inner_text()
        print(f"   -> Locked State Notice: {notice_text}")
        assert "ვარსკვლავები" in notice_text, "Notice should mention star approval status"

        teaser_text = await page.locator(".home-weekly-teaser-quote").inner_text()
        print(f"   -> Teaser quote: {teaser_text[:60]}...")

        # Screenshot 1: Desktop Locked State
        desktop_locked_shot = os.path.join(ARTIFACTS_DIR, "weekly-energy-locked-desktop.png")
        await page.locator(".home-daily-section").screenshot(path=desktop_locked_shot)
        print(f"   -> Saved: {desktop_locked_shot}")

        # Test Unlock Flow
        print("[QA] 5. Unlocking Weekly Energy for session...")
        unlock_btn = page.locator(".home-dev-unlock-btn")
        await unlock_btn.click()
        await page.wait_for_timeout(2000)

        # Verify Unlocked State
        await page.wait_for_selector(".home-weekly-unlocked-body", timeout=8000)
        unlocked_quote = await page.locator("#panel-weekly-energy .home-daily-quote").inner_text()
        print(f"   -> Unlocked Jester Weekly Quote: {unlocked_quote}")

        points = await page.locator(".home-weekly-point-card").count()
        assert points == 3, f"Expected 3-point breakdown, found {points}"
        print(f"   -> 3-Point Weekly Breakdown verified: {points} cards (Theme, Reflection, Focus)")

        periods = await page.locator(".home-period-item").count()
        print(f"   -> Significant Periods / Peak Days detected: {periods} items")

        # Expand "რატომ?" drawer in Weekly Tab
        why_btn = page.locator("#panel-weekly-energy .home-why-toggle-btn")
        await why_btn.click()
        await page.wait_for_timeout(500)
        why_details = page.locator("#home-weekly-why-details")
        assert await why_details.is_visible(), "Technical drawer must expand"
        print("   -> Weekly Astronomical Basis Drawer expanded successfully!")

        # Screenshot 2: Desktop Unlocked State
        desktop_unlocked_shot = os.path.join(ARTIFACTS_DIR, "weekly-energy-unlocked-desktop.png")
        await page.locator(".home-daily-section").screenshot(path=desktop_unlocked_shot)
        print(f"   -> Saved: {desktop_unlocked_shot}")

        # Switch back to Tab 1 (დღის ენერგია) and verify no data loss
        print("[QA] 6. Switching back to Daily Tab...")
        await daily_tab.click()
        await page.wait_for_timeout(500)
        daily_quote_after = await page.locator("#panel-daily-energy .home-daily-quote").inner_text()
        assert daily_quote_text == daily_quote_after, "Daily quote must remain identical without refetch"
        print("   -> Daily Tab state completely preserved!")

        await context.close()

        # -------------------------------------------------------------
        # MOBILE RUN (390x844 - iPhone 14 / modern standard)
        # -------------------------------------------------------------
        print("[QA] 7. Running Mobile 390px Check...")
        m_context = await browser.new_context(viewport={"width": 390, "height": 844})
        m_page = await m_context.new_page()

        await m_page.goto("http://127.0.0.1:3000/auth/login", wait_until="networkidle")
        await m_page.fill('#login-email, input[type="email"], input[name="email"]', "dev@jester.app")
        await m_page.fill('#login-password, input[type="password"], input[name="password"]', "password123")
        await m_page.click('button[type="submit"]')
        await m_page.wait_for_timeout(3000)

        if "/onboarding" in m_page.url or m_page.url != "http://127.0.0.1:3000/":
            await m_page.goto("http://127.0.0.1:3000/", wait_until="networkidle")

        await m_page.wait_for_selector(".jester-home-container", timeout=15000)
        await m_page.wait_for_selector(".home-daily-quote", timeout=15000)

        # Switch to Weekly tab
        await m_page.locator("#tab-weekly-energy").click()
        await m_page.wait_for_timeout(1000)

        mobile_weekly_shot = os.path.join(ARTIFACTS_DIR, "weekly-energy-mobile-390.png")
        await m_page.locator(".home-daily-section").screenshot(path=mobile_weekly_shot)
        print(f"   -> Saved Mobile Screenshot: {mobile_weekly_shot}")

        # Full Home Mobile view screenshot
        mobile_full_shot = os.path.join(ARTIFACTS_DIR, "home-full-mobile-390.png")
        await m_page.screenshot(path=mobile_full_shot, full_page=True)
        print(f"   -> Saved Full Mobile Page Screenshot: {mobile_full_shot}")

        await m_context.close()
        await browser.close()
        print("[QA] ALL CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_qa())

