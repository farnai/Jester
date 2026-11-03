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
        context = await browser.new_context(viewport={"width": 1280, "height": 850})
        page = await context.new_page()

        print("[QA] 1. Logging in with dev@jester.app...")
        await page.goto("http://127.0.0.1:3000/auth/login", wait_until="networkidle")
        await page.fill('#login-email, input[type="email"], input[name="email"]', "dev@jester.app")
        await page.fill('#login-password, input[type="password"], input[name="password"]', "password123")
        await page.click('button[type="submit"]')
        await page.wait_for_timeout(3000)

        if page.url != "http://127.0.0.1:3000/":
            await page.goto("http://127.0.0.1:3000/", wait_until="networkidle")

        await page.wait_for_selector(".home-navigation", timeout=15000)
        await page.wait_for_selector(".home-stars-pill", timeout=15000)
        print("[QA] 2. Home page loaded! Checking Stars balance pill...")

        pill_text = await page.locator(".home-stars-pill").inner_text()
        print(f"   -> Stars Pill text: '{pill_text}'")

        # 3. Click Stars Pill to open Wallet Modal
        print("[QA] 3. Clicking Stars Pill to open Wallet Modal...")
        await page.click(".home-stars-pill")
        await page.wait_for_selector(".wallet-modal-card", timeout=5000)
        wallet_title = await page.locator("#wallet-modal-title").inner_text()
        wallet_hero_balance = await page.locator(".wallet-hero-number").inner_text()
        print(f"   -> Wallet Modal Opened: '{wallet_title}', Balance Hero: {wallet_hero_balance} Stars")

        modal_path = os.path.join(ARTIFACTS_DIR, "wallet-modal-desktop.png")
        await page.screenshot(path=modal_path)
        print(f"   -> Saved: {modal_path}")

        # Close Modal using Escape key
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(800)

        # 4. Switch to Weekly Energy Tab
        print("[QA] 4. Switching to Weekly Energy Tab...")
        await page.click("#tab-weekly-energy")
        await page.wait_for_timeout(1000)

        # Check if weekly energy is unlocked or needs unlock
        is_locked = await page.locator(".home-weekly-locked-card").count() > 0
        if is_locked:
            print("[QA] 5. Weekly Energy is locked. Clicking 'განბლოკვა (5 ✦ ვარსკვლავი)'...")
            await page.click(".home-weekly-locked-actions button.home-btn-primary")
            await page.wait_for_timeout(2500)
            print("   -> Unlock action completed!")

        await page.wait_for_selector(".home-weekly-unlocked-body", timeout=10000)
        weekly_quote = await page.locator(".home-weekly-unlocked-body .home-daily-quote").inner_text()
        print(f"   -> Weekly Energy Unlocked! Quote: '{weekly_quote[:60]}...'")

        weekly_path = os.path.join(ARTIFACTS_DIR, "weekly-energy-unlocked-live.png")
        await page.screenshot(path=weekly_path)
        print(f"   -> Saved: {weekly_path}")

        # 5. Expand Personal Insights (Section 4)
        print("[QA] 6. Expanding Personal Insights (Section 4)...")
        await page.click("#home-insights-accordion-toggle")
        await page.wait_for_selector(".home-insights-accordion", timeout=5000)

        # Find layer 2
        layer2_toggle = page.locator("#layer-header-layer_2")
        await layer2_toggle.scroll_into_view_if_needed()
        await layer2_toggle.click()
        await page.wait_for_timeout(1000)

        # Check if layer 2 is locked
        layer2_locked = await page.locator("#layer-panel-layer_2 .home-layer-locked-box").count() > 0
        if layer2_locked:
            print("[QA] 7. Layer 2 is locked. Clicking 'შრის განბლოკვა (5 ✦)'...")
            await page.click("#layer-panel-layer_2 .home-layer-unlock-btn")
            await page.wait_for_timeout(2500)
            print("   -> Layer 2 unlock completed!")

        # Verify layer 2 items are revealed
        await page.wait_for_selector("#layer-panel-layer_2 .home-layer-items-grid", timeout=10000)
        item_count = await page.locator("#layer-panel-layer_2 .home-layer-item-card").count()
        first_item_text = await page.locator("#layer-panel-layer_2 .home-item-text").first.inner_text()
        print(f"   -> Layer 2 Unlocked! {item_count} items revealed. First item preview: '{first_item_text[:50]}...'")

        insights_path = os.path.join(ARTIFACTS_DIR, "personal-layer-unlocked-live.png")
        await page.screenshot(path=insights_path)
        print(f"   -> Saved: {insights_path}")

        # 6. Re-open Wallet Modal to check updated balance and ledger
        print("[QA] 8. Re-opening Wallet Modal to check updated ledger...")
        await page.locator(".home-stars-pill").scroll_into_view_if_needed()
        await page.click(".home-stars-pill")
        await page.wait_for_selector(".wallet-modal-card", timeout=5000)

        updated_balance = await page.locator(".wallet-hero-number").inner_text()
        tx_count = await page.locator(".wallet-tx-item").count()
        print(f"   -> Updated Balance: {updated_balance} Stars, Transactions in ledger: {tx_count}")

        ledger_path = os.path.join(ARTIFACTS_DIR, "wallet-modal-after-unlocks.png")
        await page.screenshot(path=ledger_path)
        print(f"   -> Saved: {ledger_path}")

        print("\n[QA] ALL VERIFICATIONS PASSED SUCCESSFULLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa())
