import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "artifacts_qa", "interests_v2")
)

VIEWPORTS = [
    {"name": "desktop-1440", "width": 1440, "height": 900},
    {"name": "desktop-1280", "width": 1280, "height": 800},
    {"name": "tablet-768", "width": 768, "height": 1024},
    {"name": "mobile-390", "width": 390, "height": 844},
    {"name": "mobile-360", "width": 360, "height": 780},
    {"name": "mobile-320", "width": 320, "height": 640},
]

async def run_qa():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print("[QA] Starting Playwright Interests V2 QA...")

        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        print("[QA] 1. Navigating to http://127.0.0.1:3001/visual-lab...")
        await page.goto("http://127.0.0.1:3001/visual-lab", wait_until="networkidle")

        form = page.locator("form.interests-step-v2")
        await form.scroll_into_view_if_needed()
        print("[QA] 2. InterestsStep form located in DOM.")

        # Wait for catalog to load
        await page.wait_for_selector(".interests-v2-pills", timeout=10000)

        # 3. Verify category tabs
        cat_btns = form.locator(".interests-v2-cat-btn")
        cat_count = await cat_btns.count()
        print(f"[QA] 3. Category tabs found: {cat_count} (Expected 10: 'ყველა' + 9 categories)")
        assert cat_count == 10, f"Expected 10 category tabs, found {cat_count}"

        # 4. Verify total interest pills when 'all' is active
        all_pills = form.locator(".interests-v2-pill")
        total_pills = await all_pills.count()
        print(f"[QA] 4. Total interest pills rendered: {total_pills} (Expected 79)")
        assert total_pills == 79, f"Expected 79 interest pills, found {total_pills}"

        # 5. Verify category filtering
        print("[QA] 5. Testing Category Filter: 'მუსიკა და სცენა'...")
        music_tab = form.locator(".interests-v2-cat-btn").filter(has_text="მუსიკა და სცენა")
        await music_tab.click()
        await page.wait_for_timeout(200)
        filtered_count = await form.locator(".interests-v2-pill").count()
        print(f"       -> Filtered count for 'მუსიკა და სცენა': {filtered_count} (Expected 9)")
        assert filtered_count == 9, f"Expected 9 music pills, got {filtered_count}"

        # Return to 'all'
        await form.locator(".interests-v2-cat-btn").filter(has_text="ყველა").click()
        await page.wait_for_timeout(200)
        assert await form.locator(".interests-v2-pill").count() == 79

        # 6. Verify Search
        search_input = form.locator(".interests-v2-search-box input")
        print("[QA] 6. Testing Search Functionality:")

        # Search Georgian: "როკი"
        await search_input.fill("როკი")
        await page.wait_for_timeout(200)
        rock_count = await form.locator(".interests-v2-pill").count()
        print(f"       -> Georgian search 'როკი': {rock_count} item(s)")
        assert rock_count >= 1

        # Search English: "anime"
        await search_input.fill("anime")
        await page.wait_for_timeout(200)
        anime_count = await form.locator(".interests-v2-pill").count()
        print(f"       -> English search 'anime': {anime_count} item(s)")
        assert anime_count >= 1

        # Search Alias: "მელომანი"
        await search_input.fill("მელომანი")
        await page.wait_for_timeout(200)
        alias_count = await form.locator(".interests-v2-pill").count()
        print(f"       -> Alias search 'მელომანი': {alias_count} item(s)")
        assert alias_count == 1

        # Search Empty State
        await search_input.fill("xyz999_non_existent")
        await page.wait_for_timeout(200)
        assert await form.locator(".interests-v2-empty-state").is_visible()
        print("       -> Empty state displayed properly for non-matching queries.")

        # Clear search
        await form.locator(".interests-v2-btn-reset-search").click()
        await page.wait_for_timeout(200)
        assert await form.locator(".interests-v2-pill").count() == 79
        print("       -> Search reset successful.")

        # 7. Selection constraints & Tray test
        print("[QA] 7. Testing 3–7 Selection Constraints & Tray:")
        submit_btn = form.locator(".interests-v2-btn-submit")

        # Initial state: 0 selected
        assert not await submit_btn.is_disabled(), "Submit should be enabled for 0 (treated as skip)"

        # Select 1st pill
        pills = form.locator(".interests-v2-pill")
        await pills.nth(0).click()
        await page.wait_for_timeout(150)
        assert await submit_btn.is_disabled(), "Submit MUST be disabled when 1 interest is selected!"
        print("       -> 1 selected: Submit correctly disabled (needs min 3).")

        # Select 2nd pill
        await pills.nth(1).click()
        await page.wait_for_timeout(150)
        assert await submit_btn.is_disabled(), "Submit MUST be disabled when 2 interests are selected!"
        print("       -> 2 selected: Submit correctly disabled (needs min 3).")

        # Select 3rd pill
        await pills.nth(2).click()
        await page.wait_for_timeout(150)
        assert not await submit_btn.is_disabled(), "Submit MUST be enabled when 3 interests are selected!"
        print("       -> 3 selected: Submit enabled (ready).")

        # Select up to 7 pills
        for i in range(3, 7):
            await pills.nth(i).click()
            await page.wait_for_timeout(100)

        counter_pill = form.locator(".interests-v2-counter-pill")
        counter_text = await counter_pill.inner_text()
        print(f"       -> 7 selected: Counter badge displays '{counter_text}'")
        assert "7 / 7" in counter_text

        # Verify 8th pill is disabled
        eighth_pill = pills.nth(7)
        assert await eighth_pill.is_disabled(), "Unselected pills MUST be disabled at 7 items!"
        print("       -> Max 7 enforced: unselected pills properly disabled.")

        # Verify tray chips
        tray_chips = form.locator(".interests-v2-tray-chip")
        assert await tray_chips.count() == 7
        print("       -> Tray displays exactly 7 chips.")

        # Remove 1 item via tray '✕' button
        await tray_chips.first.locator(".interests-v2-tray-chip-remove").click()
        await page.wait_for_timeout(150)
        assert "6 / 7" in await counter_pill.inner_text()
        assert not await eighth_pill.is_disabled(), "Pills re-enabled after deselecting below 7."
        print("       -> One-click tray removal verified: count reduced to 6/7, pills re-enabled.")

        # Re-add to 7 for visual capture
        await eighth_pill.click()
        await page.wait_for_timeout(150)

        # 8. Responsive Viewport Captures
        print("[QA] 8. Running Responsive Viewport QA across 6 viewports...")
        for vp in VIEWPORTS:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await page.wait_for_timeout(300)
            await form.scroll_into_view_if_needed()

            # Check horizontal overflow
            scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
            client_width = await page.evaluate("() => document.documentElement.clientWidth")
            assert scroll_width <= client_width + 1, f"Horizontal overflow detected at {vp['name']}! {scroll_width} > {client_width}"

            screenshot_path = os.path.join(OUTPUT_DIR, f"interests_v2_{vp['name']}.png")
            await form.screenshot(path=screenshot_path)
            print(f"  [OK] {vp['name']} (width {vp['width']}px): Screenshot saved.")

        await browser.close()
        print("[QA] All Interests System V2 Playwright checks PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(run_qa())

