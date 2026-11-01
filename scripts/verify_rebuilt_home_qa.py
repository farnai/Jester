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

        print("[QA] 3. Waiting for navigation away from login...")
        await page.wait_for_timeout(3000)
        print(f"   -> URL after submit: {page.url}")
        if "/auth/login" in page.url:
            # Check if there is an error message on the page
            err_el = page.locator("[role='alert'], .auth-error, .login-error")
            if await err_el.count() > 0:
                print(f"   -> Login error message on page: {await err_el.first.inner_text()}")
            await page.wait_for_timeout(2000)

        if "/onboarding" in page.url or page.url != "http://localhost:3000/":
            print("[QA] Redirecting to Home...")
            await page.goto("http://localhost:3000/", wait_until="networkidle")

        # Wait for the home layout and data to settle
        await page.wait_for_selector(".jester-home-container", timeout=15000)
        await page.wait_for_selector(".home-daily-quote", timeout=15000)
        print("[QA] 4. Rebuilt Home Page container and daily quote loaded successfully!")

        # Verify Unified Section Containers (All 4 sections have .home-card)
        print("[QA] 4.1. Verifying Unified Section Containers...")
        card_selectors = [
            ".home-daily-section .home-daily-card.home-card",
            ".home-dodont-section .home-dodont-card.home-card",
            ".home-insights-section .home-insights-card.home-card",
            ".home-people-section .home-people-card.home-card",
        ]
        for sel in card_selectors:
            count = await page.locator(sel).count()
            print(f"   -> Container check: '{sel}' count = {count}")
            assert count == 1, f"Missing unified .home-card container for {sel}"

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

        # Verify Section 3: Personal Insights (Nested Accordion)
        print("[QA] 7. Verifying Section 3: Personal Insights (Nested Accordion)...")
        insights_sec = page.locator(".home-insights-section")
        assert await insights_sec.count() > 0, "Personal Insights section missing!"

        # A) Check Initial State: Collapsed by default
        parent_toggle = page.locator("#home-insights-accordion-toggle")
        assert await parent_toggle.count() > 0, "Parent accordion toggle button missing!"
        initial_expanded = await parent_toggle.get_attribute("aria-expanded")
        print(f"   -> Parent initial aria-expanded: {initial_expanded}")
        assert initial_expanded == "false", "Parent accordion must be collapsed by default!"

        # Verify visible elements when collapsed
        title_text = await page.locator("#home-insights-heading").inner_text()
        subtitle_text = await page.locator(".home-insights-card .home-section-subtitle").inner_text()
        print(f"   -> Title: {title_text}, Subtitle: {subtitle_text}")
        assert "გაიცანი საკუთარი თავი" in title_text
        assert "შენი პიროვნების 7 ასტროლოგიური შრე" in subtitle_text

        # 7 inner layers should be hidden initially
        initial_layer_count = await page.locator(".home-layer-card").count()
        print(f"   -> Layers rendered before opening parent: {initial_layer_count}")
        assert initial_layer_count == 0, f"Expected 0 layers rendered while collapsed, got {initial_layer_count}"

        # B) Expand Parent Accordion
        print("   -> Clicking parent accordion to expand...")
        await parent_toggle.click()
        await page.wait_for_selector("#home-insights-body", state="visible")
        after_open_expanded = await parent_toggle.get_attribute("aria-expanded")
        assert after_open_expanded == "true", "Parent accordion aria-expanded must be true after click!"

        layer_cards = page.locator(".home-layer-card")
        layer_count = await layer_cards.count()
        print(f"   -> Layers rendered count after opening parent: {layer_count}")
        assert layer_count == 7, f"Expected 7 layers, got {layer_count}"

        star_pill_count = await page.locator(".home-star-pill").count()
        assert star_pill_count == 0, f"Expected 0 star price badges, found {star_pill_count}"
        print("   -> Verified: No monetization price badges shown (layers are open and free)")

        # C) Test toggling inner layer 2
        layer_2_toggle = page.locator("#layer-header-layer_2_cognition")
        if await layer_2_toggle.count() > 0:
            await layer_2_toggle.click()
            await page.wait_for_selector("#layer-panel-layer_2_cognition", state="visible")
            print("   -> Toggled and expanded Layer 2 (როგორ აზროვნებ) independently")

        # D) Test collapsing Parent Accordion again
        print("   -> Clicking parent accordion to collapse again...")
        await parent_toggle.click()
        await page.wait_for_timeout(300)
        collapsed_expanded = await parent_toggle.get_attribute("aria-expanded")
        assert collapsed_expanded == "false", "Parent accordion aria-expanded must be false after collapse!"
        after_collapse_count = await page.locator(".home-layer-card").count()
        assert after_collapse_count == 0, f"Expected 0 layers visible after collapse, got {after_collapse_count}"
        print("   -> Verified: Collapsing parent hides all 7 layers!")

        # E) Re-open parent accordion for Sharing & screenshot verification
        await parent_toggle.click()
        await page.wait_for_selector("#home-insights-body", state="visible")

        # F) Verify Individual Card Sharing (Modal & Canvas)
        print("[QA] 7.1. Verifying Individual Card Sharing Modal...")
        first_layer_toggle = page.locator(".home-layer-toggle").first
        await first_layer_toggle.click()
        await page.wait_for_timeout(300)
        share_btn = page.locator(".home-card-share-btn").first
        assert await share_btn.count() > 0, "Share card button missing on layer items!"
        await share_btn.click()
        await page.wait_for_selector(".home-modal-overlay", state="visible")
        modal_title = await page.locator("#share-modal-title").inner_text()
        print(f"   -> Share Modal Opened: {modal_title}")
        assert "ბარათის გაზიარება" in modal_title
        
        # Check preview branding and quote
        preview_logo = await page.locator(".home-share-preview-logo").inner_text()
        assert "J E S T E R" in preview_logo
        quote_present = await page.locator(".home-share-preview-quote").count() > 0
        assert quote_present, "Share card preview quote missing!"
        
        # Close modal
        close_btn = page.locator(".home-modal-close-btn")
        await close_btn.click()
        await page.wait_for_selector(".home-modal-overlay", state="hidden")
        print("   -> Share Modal closed successfully.")

        # Verify Section 4: New People (18+)
        print("[QA] 8. Verifying Section 4: New People (Photo-first, info-second)...")
        people_sec = page.locator(".home-people-section")
        assert await people_sec.count() > 0, "New People section missing!"
        person_cards = page.locator(".home-person-card")
        people_count = await person_cards.count()
        print(f"   -> New people cards count: {people_count}")
        assert people_count > 0, "Expected at least 1 person card!"

        # Check Short Card Elements
        first_card = person_cards.first
        photo_count = await first_card.locator(".home-person-photo-wrap").count()
        assert photo_count == 1, "Photo wrap missing on New People card!"
        new_badge_count = await first_card.locator(".home-person-badge-new").count()
        assert new_badge_count == 1, "New / ახალი badge missing on card!"
        
        first_person_name = await first_card.locator(".home-person-name").inner_text()
        print(f"   -> First person short name: {first_person_name}")
        # Verify surname is abbreviated (ends with . or single word)
        if " " in first_person_name:
            assert first_person_name.strip().endswith("."), f"Surname must be abbreviated to initial with dot: {first_person_name}"

        # Check interest tags <= 2
        interest_count = await first_card.locator(".home-person-interest-tag").count()
        assert interest_count <= 2, f"Expected at most 2 interest tags, got {interest_count}"

        # Check Portrait Proportions and Fallbacks on Cards
        cards_with_photo = 0
        cards_with_fallback = 0

        for idx in range(min(people_count, 6)):
            card = person_cards.nth(idx)
            wrap = card.locator(".home-person-photo-wrap")
            bbox = await wrap.bounding_box()
            if bbox:
                ratio = bbox["height"] / bbox["width"]
                print(f"   -> Card #{idx + 1} wrap dimensions: {bbox['width']:.1f}x{bbox['height']:.1f} (ratio: {ratio:.2f})")
                assert 1.25 <= ratio <= 1.45, f"Card #{idx + 1} expected 3:4 ratio (~1.33), got {ratio:.2f}"

            img_el = card.locator(".home-person-photo")
            if await img_el.count() > 0:
                cards_with_photo += 1
                obj_fit = await img_el.evaluate("el => getComputedStyle(el).objectFit")
                obj_pos = await img_el.evaluate("el => getComputedStyle(el).objectPosition")
                print(f"   -> Card #{idx + 1} Photo styling: object-fit={obj_fit}, object-position={obj_pos}")
                assert obj_fit == "cover", f"Expected object-fit cover, got {obj_fit}"
            else:
                fallback_el = card.locator(".home-person-photo-fallback")
                if await fallback_el.count() > 0:
                    cards_with_fallback += 1
                    initial_text = await card.locator(".home-person-initial").inner_text()
                    print(f"   -> Card #{idx + 1} Fallback avatar verified (Initial: {initial_text}, same 3:4 portrait wrap)")

        print(f"   -> Verified {cards_with_photo} photo cards and {cards_with_fallback} fallback cards all preserve 3:4 portrait geometry!")

        # Check Portrait Proportions and Fallbacks on Cards
        cards_with_photo = 0
        cards_with_fallback = 0

        for idx in range(min(people_count, 6)):
            card = person_cards.nth(idx)
            wrap = card.locator(".home-person-photo-wrap")
            bbox = await wrap.bounding_box()
            if bbox:
                ratio = bbox["height"] / bbox["width"]
                print(f"   -> Card #{idx + 1} wrap dimensions: {bbox['width']:.1f}x{bbox['height']:.1f} (ratio: {ratio:.2f})")
                assert 1.25 <= ratio <= 1.45, f"Card #{idx + 1} expected 3:4 ratio (~1.33), got {ratio:.2f}"

            img_el = card.locator(".home-person-photo")
            if await img_el.count() > 0:
                cards_with_photo += 1
                obj_fit = await img_el.evaluate("el => getComputedStyle(el).objectFit")
                obj_pos = await img_el.evaluate("el => getComputedStyle(el).objectPosition")
                print(f"   -> Card #{idx + 1} Photo styling: object-fit={obj_fit}, object-position={obj_pos}")
                assert obj_fit == "cover", f"Expected object-fit cover, got {obj_fit}"
            else:
                fallback_el = card.locator(".home-person-photo-fallback")
                if await fallback_el.count() > 0:
                    cards_with_fallback += 1
                    initial_text = await card.locator(".home-person-initial").inner_text()
                    print(f"   -> Card #{idx + 1} Fallback avatar verified (Initial: {initial_text}, same 3:4 portrait wrap)")

        print(f"   -> Verified {cards_with_photo} photo cards and {cards_with_fallback} fallback cards all preserve 3:4 portrait geometry!")

        # 9. Verify Detailed Person Profile Navigation
        print("[QA] 8.1. Navigating to Detailed Person Profile...")
        await first_card.locator("a.home-person-link").click()
        await page.wait_for_selector(".person-profile-container", timeout=10000)
        print("   -> Person Profile page loaded successfully!")

        # Verify Thematic Sections on Person Profile
        hero_name = await page.locator(".person-display-name").inner_text()
        print(f"   -> Profile hero name: {hero_name}")
        assert len(hero_name) > 0, "Person display name missing in profile hero!"

        # Verify Identity badges (Zodiac, City, Work)
        badges_count = await page.locator(".person-pill").count()
        print(f"   -> Identity pills count: {badges_count}")
        assert badges_count > 0, "Expected at least 1 identity pill (zodiac/city/work)!"

        # Verify Photos & Gallery
        main_photo = page.locator(".person-main-photo-stage")
        assert await main_photo.count() == 1, "Main photo stage missing on Person Profile!"

        # Verify Compatibility Section
        compat_sec = page.locator(".person-compatibility-card")
        if await compat_sec.count() > 0:
            print("   -> Compatibility section rendered with safe First Sight preview")

        # Verify Astrological Context Section
        astro_sec = page.locator(".person-astrology-card")
        if await astro_sec.count() > 0:
            astro_items_count = await page.locator(".person-astro-item").count()
            print(f"   -> Astrological context items count: {astro_items_count}")
        else:
            print("   -> Astrological context section clean (safe fallback when target person has no safe astro record)")

        # Verify PRIVACY INVARIANT: No 7 personal layers on other's profile!
        profile_layer_cards = await page.locator(".home-layer-card").count()
        assert profile_layer_cards == 0, f"VIOLATION: Personal Insights 7 layers found on public profile! ({profile_layer_cards})"
        print("   -> Verified Privacy Invariant: 7 Personal Insights layers are 100% private to account owner!")

        # Return to Home
        back_btn = page.locator(".person-back-link")
        if await back_btn.count() > 0:
            await back_btn.click()
            await page.wait_for_timeout(500)
        if "/people/" in page.url or "/discover" in page.url:
            await page.goto("http://localhost:3000/", wait_until="networkidle")
        await page.wait_for_selector(".jester-home-container", timeout=10000)
        print("   -> Returned to Home page.")

        # Capture specific New People Section on Desktop (1280px)
        await page.set_viewport_size({"width": 1280, "height": 800})
        await page.wait_for_timeout(300)
        desktop_section = page.locator(".home-people-section")
        desktop_section_path = os.path.join(ARTIFACTS_DIR, "rebuilt-home-new-people-desktop-1280.png")
        await desktop_section.screenshot(path=desktop_section_path)
        print(f"   -> Captured Desktop New People section: {desktop_section_path}")

        # Capture specific New People Section on Mobile (390px)
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(300)
        mobile_section = page.locator(".home-people-section")
        mobile_section_path = os.path.join(ARTIFACTS_DIR, "rebuilt-home-new-people-mobile-390.png")
        await mobile_section.screenshot(path=mobile_section_path)
        print(f"   -> Captured Mobile New People section: {mobile_section_path}")

        # Verify responsive snapshots and zero horizontal overflow across all required viewports
        print("[QA] 9. Checking responsive viewports & capturing full screenshots...")
        for vp in VIEWPORTS:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await page.wait_for_timeout(400)

            # Check card dimensions in this viewport
            first_c = page.locator(".home-person-card").first
            c_bbox = await first_c.bounding_box()
            if c_bbox:
                print(f"   - Viewport {vp['name']} card size: {c_bbox['width']:.1f}w x {c_bbox['height']:.1f}h")

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

