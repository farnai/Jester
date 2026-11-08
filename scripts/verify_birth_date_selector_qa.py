import asyncio
import os
import sys
from playwright.async_api import async_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "artifacts_qa", "birth_date_selector")
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
        print("[QA] Starting Playwright Browser Verification...")

        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        # 1. Navigate to Visual Lab where BirthDateInput is rendered
        print("[QA] 1. Navigating to http://127.0.0.1:3001/visual-lab...")
        await page.goto("http://127.0.0.1:3001/visual-lab", wait_until="networkidle")

        # Scroll into view
        birth_fieldset = page.locator("fieldset").filter(has_text="დაბადების თარიღი")
        await birth_fieldset.first.scroll_into_view_if_needed()
        print("[QA] 2. BirthDateInput fieldset found in DOM.")

        # Verify Day select and options
        day_select = birth_fieldset.first.locator("select[name='birth_day']")
        day_options = await day_select.locator("option").all_inner_texts()
        print(f"[QA] 3. Day select has {len(day_options)} options (including placeholder).")
        assert len(day_options) >= 29, f"Expected at least 29 day options, got {len(day_options)}"

        # Verify Month select and Georgian month names
        month_select = birth_fieldset.first.locator("select[name='birth_month']")
        month_options = await month_select.locator("option").all_inner_texts()
        print(f"[QA] 4. Month select has {len(month_options)} options:")
        assert any("იანვარი" in opt for opt in month_options), "იანვარი missing from months!"
        assert any("თებერვალი" in opt for opt in month_options), "თებერვალი missing from months!"
        assert any("დეკემბერი" in opt for opt in month_options), "დეკემბერი missing from months!"

        # Verify Year input (Rapid Combobox)
        year_input = birth_fieldset.first.locator("input[placeholder='წელი']")
        print("[QA] 5. Year input combobox located.")

        # Test clicking year chevron to open rapid decade popover
        year_chevron = birth_fieldset.first.locator("button[aria-label*='წლების სიის']")
        await year_chevron.click()
        await page.wait_for_timeout(300)

        year_popover = birth_fieldset.first.locator("div[role='listbox']")
        assert await year_popover.is_visible(), "Year rapid selection popover did not open!"
        print("[QA] 6. Rapid year selection popover opened successfully.")

        # Check generational cohort chips
        gen_chips = await year_popover.locator("button").all_inner_texts()
        print(f"[QA] 7. Generational cohort chips present: {gen_chips}")
        assert "მილენიალები" in gen_chips, "მილენიალები chip missing!"
        assert "Gen Z" in gen_chips, "Gen Z chip missing!"

        # Screenshot of the open popover with generational chips
        popover_shot = os.path.join(OUTPUT_DIR, "birth_date_generational_popover.png")
        await birth_fieldset.first.screenshot(path=popover_shot)
        print(f"[QA] Generational popover screenshot saved: {popover_shot}")

        # Click მილენიალები chip (Millennials: 1981 - 1996)
        chip_millennials = year_popover.locator("button", has_text="მილენიალები")
        await chip_millennials.click()
        await page.wait_for_timeout(200)

        # Select 1995 from the list
        opt_1995 = year_popover.locator("button[role='option']", has_text="1995")
        await opt_1995.click(force=True)
        await page.wait_for_timeout(200)

        current_year_val = await year_input.input_value()
        assert current_year_val == "1995", f"Expected year 1995, got {current_year_val}"
        print(f"[QA] 8. Successfully selected year: {current_year_val}")

        # Test direct typing in Year input
        await year_input.fill("")
        await year_input.type("1998")
        await page.wait_for_timeout(200)
        assert await year_input.input_value() == "1998", "Year typing did not update input!"
        print("[QA] 9. Direct numeric typing (1998) verified.")

        # Test Day selection
        await day_select.select_option("24")
        await month_select.select_option("08")
        await page.wait_for_timeout(200)
        print("[QA] 10. Selected 24 აგვისტო 1998 -> complete valid date.")

        # Test changing month from 31-day month to February resets day without silent shift
        await day_select.select_option("31")
        await month_select.select_option("01")
        await page.wait_for_timeout(200)
        assert await day_select.input_value() == "31", "Day 31 not selected in Jan"

        # Now change to February
        await month_select.select_option("02")
        await page.wait_for_timeout(300)
        day_after_feb = await day_select.input_value()
        assert day_after_feb == "", f"Day should be reset when switching to Feb, but was '{day_after_feb}'"
        print("[QA] 11. Silent day-drift prevention verified: Day reset to empty when switching from Jan 31 to Feb.")

        # Verify alert message appears
        alert_el = birth_fieldset.first.locator("div[role='alert']")
        assert await alert_el.is_visible(), "Reset alert did not appear!"
        alert_text = await alert_el.inner_text()
        print(f"[QA] 12. Alert text verified: {alert_text}")

        # Verify across all 6 viewports and take screenshots
        print("[QA] 13. Running responsive viewport checks...")
        for vp in VIEWPORTS:
            await page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            await birth_fieldset.first.scroll_into_view_if_needed()
            await page.wait_for_timeout(300)

            # Check horizontal overflow on fieldset
            box = await birth_fieldset.first.bounding_box()
            overflow_check = await page.evaluate(
                """() => {
                    const el = document.querySelector('fieldset[id*=\"birth-date\"]');
                    if (!el) return { hasOverflow: false };
                    return {
                        scrollWidth: el.scrollWidth,
                        clientWidth: el.clientWidth,
                        hasOverflow: el.scrollWidth > el.clientWidth + 2
                    };
                }"""
            )
            assert not overflow_check.get("hasOverflow", False), (
                f"Horizontal overflow detected at {vp['name']}! "
                f"scrollWidth={overflow_check['scrollWidth']}, clientWidth={overflow_check['clientWidth']}"
            )

            screenshot_path = os.path.join(OUTPUT_DIR, f"birth_date_{vp['name']}.png")
            await birth_fieldset.first.screenshot(path=screenshot_path)
            print(f"  [OK] {vp['name']} (width {vp['width']}px): No overflow. Screenshot saved: {screenshot_path}")

        print("[QA] All Playwright browser verification checks PASSED successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_qa())
