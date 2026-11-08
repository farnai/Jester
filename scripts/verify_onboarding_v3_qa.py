import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARTIFACT_DIR = os.environ.get("JESTER_ARTIFACT_DIR") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "artifacts_qa", "onboarding_v3")
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
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        print("[QA] Starting Playwright Onboarding V3 QA...")

        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        # Mock PUT mutations so Visual Lab testing succeeds without session
        async def mock_enrichment_mutation(route, request):
            if request.method == "PUT":
                data = request.post_data_json or {}
                await route.fulfill(status=200, json={"status": "ok", **data})
            else:
                await route.continue_()

        await page.route("**/v1/interests/me", mock_enrichment_mutation)
        await page.route("**/v1/personality-traits/me", mock_enrichment_mutation)
        await page.route("**/v1/connection-intentions/me", mock_enrichment_mutation)

        print("[QA] 1. Navigating to http://127.0.0.1:3001/visual-lab...")
        await page.goto("http://127.0.0.1:3001/visual-lab", wait_until="networkidle")

        container = page.locator(".onboarding-v3-enrichment-container")
        await container.scroll_into_view_if_needed()
        print("[QA] 2. ProfileEnrichmentModule container located in Visual Lab.")

        # =========================================================================
        # SUB-STAGE 1: INTERESTS (ONE-TAP DIRECT DISCOVERY)
        # =========================================================================
        print("\n--- Testing Sub-Stage 1: Interests ---")
        # Wait for featured pills to finish loading from API
        await page.wait_for_selector(".interests-v3-one-tap-section .interests-v3-pill", timeout=10000)

        featured_pills = container.locator(".interests-v3-one-tap-section .interests-v3-pill")
        featured_count = await featured_pills.count()
        print(f"[QA] Featured 1-tap pills count: {featured_count} (Expected 16)")
        assert featured_count == 16, f"Expected 16 featured pills, got {featured_count}"

        # Test one-tap selection: tap 1st pill
        pill_1 = featured_pills.nth(0)
        pill_1_text = (await pill_1.inner_text()).strip()
        print(f"[QA] Tapping 1st featured pill: '{pill_1_text}'...")
        await pill_1.click()
        await page.wait_for_timeout(200)

        # Assert selected class applied with single tap
        is_selected = "selected" in (await pill_1.get_attribute("class") or "")
        print(f"[QA] Pill 1 selected in 1 tap: {is_selected}")
        assert is_selected, "Pill was not selected in 1 tap!"

        # Tap 2nd pill
        pill_2 = featured_pills.nth(1)
        await pill_2.click()
        await page.wait_for_timeout(200)

        # Verify counter shows 2 / 7
        counter = container.locator(".onboarding-v3-compact-counter .onboarding-v3-counter-number")
        counter_text = (await counter.inner_text()).strip()
        print(f"[QA] Counter value: '{counter_text}' (Expected '2 / 7')")
        assert "2 / 7" in counter_text

        # Test expandable full catalog toggle
        expand_btn = container.locator(".interests-v3-btn-toggle-catalog")
        print("[QA] Clicking 'სხვა ინტერესების ნახვა' expandable catalog toggle...")
        await expand_btn.click()
        await page.wait_for_selector(".interests-v3-full-catalog-panel", timeout=5000)

        catalog_scroll = container.locator(".interests-v3-catalog-scroll")
        assert await catalog_scroll.is_visible(), "Full catalog did not expand!"
        print("[QA] Expandable catalog opened successfully.")

        # Search test
        search_input = container.locator(".interests-v3-search-box input")
        await search_input.fill("როკი")
        await page.wait_for_timeout(200)
        matched_pills = container.locator(".interests-v3-catalog-scroll .interests-v3-pill")
        print(f"[QA] Search 'როკი' results: {await matched_pills.count()} pill(s)")
        assert await matched_pills.count() >= 1

        # Advance to Stage 2: Click "შემდეგი"
        print("[QA] Submitting Stage 1 via 'შემდეგი' button...")
        next_btn = container.locator(".onboarding-v3-btn-next")
        await next_btn.click()
        await page.wait_for_timeout(400)

        # =========================================================================
        # SUB-STAGE 2: PERSONALITY DESCRIPTORS
        # =========================================================================
        print("\n--- Testing Sub-Stage 2: Personality Descriptors ---")
        await page.wait_for_selector(".personality-step-v3", timeout=5000)

        stage_header = container.locator(".personality-step-v3 .onboarding-v3-stage-header h2")
        header_text = (await stage_header.inner_text()).strip()
        print(f"[QA] Stage 2 header: '{header_text}'")
        assert "როგორ დაახასიათებ საკუთარ თავს?" in header_text

        # Verify 14 descriptors
        trait_pills = container.locator(".personality-v3-pills-grid .personality-v3-pill")
        trait_count = await trait_pills.count()
        print(f"[QA] Personality descriptors rendered: {trait_count} (Expected 14)")
        assert trait_count == 14, f"Expected 14 personality descriptors, got {trait_count}"

        # 1-tap select 2 traits
        print("[QA] Selecting 2 personality traits in 1 tap...")
        await trait_pills.nth(0).click()
        await trait_pills.nth(1).click()
        await page.wait_for_timeout(200)

        p_counter = container.locator(".personality-step-v3 .onboarding-v3-counter-number")
        print(f"[QA] Personality counter: '{(await p_counter.inner_text()).strip()}' (Expected '2 / 5')")
        assert "2 / 5" in (await p_counter.inner_text()).strip()

        # Advance to Stage 3: Click "შემდეგი"
        print("[QA] Submitting Stage 2 via 'შემდეგი' button...")
        await container.locator(".personality-step-v3 .onboarding-v3-btn-next").click()
        await page.wait_for_timeout(400)

        # =========================================================================
        # SUB-STAGE 3: CONNECTION INTENTIONS
        # =========================================================================
        print("\n--- Testing Sub-Stage 3: Connection Intentions ---")
        await page.wait_for_selector(".intentions-step-v3", timeout=5000)

        intent_header = container.locator(".intentions-step-v3 .onboarding-v3-stage-header h2")
        intent_header_text = (await intent_header.inner_text()).strip()
        print(f"[QA] Stage 3 header: '{intent_header_text}'")
        assert "რისთვის ხარ აქ?" in intent_header_text

        # Verify 6 intentions cards
        intent_cards = container.locator(".intentions-v3-cards-grid .intentions-v3-card")
        intent_count = await intent_cards.count()
        print(f"[QA] Connection intention cards rendered: {intent_count} (Expected 6)")
        assert intent_count == 6, f"Expected 6 intention cards, got {intent_count}"

        # 1-tap select 2 intentions
        print("[QA] Selecting 2 intentions in 1 tap...")
        await intent_cards.nth(0).click()
        await intent_cards.nth(1).click()
        await page.wait_for_timeout(200)

        i_counter = container.locator(".intentions-step-v3 .onboarding-v3-counter-number")
        print(f"[QA] Intentions counter: '{(await i_counter.inner_text()).strip()}' (Expected '2 / 3')")
        assert "2 / 3" in (await i_counter.inner_text()).strip()

        # =========================================================================
        # SINGLE UNIFIED SKIP ("მოგვიანებით შევავსებ") VERIFICATION
        # =========================================================================
        print("\n--- Testing Single Unified Skip ('მოგვიანებით შევავსებ') ---")
        # Ensure redundant per-step skip button is removed
        redundant_skip_btns = container.locator(".onboarding-v3-btn-skip-stage")
        assert await redundant_skip_btns.count() == 0, "Redundant per-step skip stage button should not be rendered!"
        print("[QA] Confirmed: redundant 'ამ ეტაპის გამოტოვება' button is eliminated.")

        skip_all_btn = container.locator(".intentions-step-v3 .onboarding-v3-btn-exit-all")
        assert await skip_all_btn.is_visible()
        skip_text = (await skip_all_btn.inner_text()).strip()
        print(f"[QA] Unified Skip button visible: '{skip_text}' (Expected 'მოგვიანებით შევავსებ')")
        assert "მოგვიანებით შევავსებ" in skip_text

        # =========================================================================
        # CAPTURE RESPONSIVE SCREENSHOTS
        # =========================================================================
        print("\n--- Capturing Responsive Viewports ---")
        for vp in VIEWPORTS:
            vp_context = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            vp_page = await vp_context.new_page()
            await vp_page.goto("http://127.0.0.1:3001/visual-lab", wait_until="networkidle")
            vp_container = vp_page.locator(".onboarding-v3-enrichment-container")
            await vp_container.scroll_into_view_if_needed()
            await vp_page.wait_for_timeout(300)

            screenshot_path = os.path.join(ARTIFACT_DIR, f"onboarding_v3_{vp['name']}.png")
            await vp_container.screenshot(path=screenshot_path)
            print(f"[QA] Saved screenshot for {vp['name']} ({vp['width']}x{vp['height']}): {screenshot_path}")
            await vp_context.close()

        print("\n[QA] ALL ONBOARDING V3 ACCEPTANCE CHECKS PASSED SUCCESSFULLY!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa())
