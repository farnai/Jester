# Registration — focused founder-review corrections

Status: **VISUAL_REVIEW_REQUIRED**. Prepared for founder review, not approved or DONE.

## Scope

Production changes in this correction are confined to `frontend/src/modules/auth/registration.css`. Registration JSX, React components, state, signup handler, auth provider, backend, database, API contracts and mobile structure were preserved. Existing photography was reused; no image was generated or changed. QA tooling and review artifacts were updated separately. No commit or push.

## Exact corrections

- Desktop (1200px and wider) scales against the approved 1160×914 UI rather than viewport height. Normal-flow content and error messages may extend that minimum height. At 1440px, the header+scene is 1148px tall; at 1280px it is 1033px. Full-page screenshots include the separate 39px footer. The viewport captures deliberately show only the visible part of these scrollable pages.
- Portrait now uses its intrinsic aspect ratio instead of filling a wide `cover` box. At 1440px the photograph renders about 621px wide, versus 936px before. The seated torso, arms, hands and bent legs are visible. Rounded image boundaries and existing masks blend it with the cream curve. A narrow, softly masked crop of the same photo's plant-bearing right edge preserves ambient foliage beside the card.
- Card moved from x986/y188, 411×590 to x960/y241, 437×733 at 1440px. Heading, labels, explanatory text, security note, field spacing and CTA scale with the reference. Inputs are about 50px tall (previously 44px), with 17.4px text; CTA is about 65px tall (previously 54px). No form logic changes.
- Panorama layer increased from 330px to about 441px at 1440px. Bottom alignment preserves foreground rocks and the city/water panorama, with both people on the left. A top mask integrates the sky into the upper scene; no photograph is stretched.
- Desktop navigation increased from 14px to 17.4px; intro from 17px to 23.6px; feature descriptions from 14px to 17.4px. Feature width was adjusted so the second title no longer wraps unnecessarily. The approved headline is unchanged.
- Inspected the brand SVG, stacked EPS, hat EPS and brand identity board, plus supplied Kit assets. They contain the existing terracotta/serif identity; the orange/sans variant in the flattened reference remains unavailable. Existing original vector paths are retained. Correcting the hat viewport's aspect ratio removes tiny wordmark fragments previously visible underneath it.
- Mobile changes are limited to that hat viewport correction. At 390px and 320px, before/after heading, portrait, card and input rectangles are exactly equal. Mobile input font remains 16px and height 44px. No suitable Georgian handwriting font/SVG was found, so the annotation treatment and verified wording were left unchanged.

## Normalized landmark comparison

Normalize x/width against the UI width, and y/height against header+scene height, excluding presentation framing and the app footer. Reference bounds were manually read from the supplied 1160×914 UI crop; implemented DOM bounds are recorded by the browser in `final/geometry.json`. Values below are percentages at 1440px, rounded; this is a geometry comparison, not a visual score.

| Landmark | Approved reference | Corrected implementation |
| --- | --- | --- |
| UI aspect ratio | 1.269 | 1.254 |
| Logo origin x/y | ~4.8 / 2.0 | 5.0 / 2.3 |
| Navigation origin x/y | ~36.2 / 3.3 | 38.0 / 2.6 |
| Headline top y | ~13.6 | 13.6 |
| Card origin x/y | ~66.7 / 21.2 | 66.6 / 21.0 |
| Card width/height | ~30.4 / 63.1 | 30.4 / 63.9 |
| First feature top y | ~45.6 | 45.4 |
| Second feature top y | ~55.9 | 55.4 |
| Third feature top y | ~66.2 | 65.3 |
| Annotation top y | ~77.7 | 76.0 |

Photographic landmarks require visual estimates rather than DOM box claims: the visible eye is approximately x60%/y25% in the reference and x61%/y22% in the corrected image. The seated hands are around x48%/y56% versus x49%/y59%. The middle distant panorama horizon is around y87% in the reference versus y82–84% in the replacement. These remaining differences come from the different photo/pose/landscape, not screenshot viewport dimensions. The face remains unobstructed and the body/foreground are substantially more visible than before.

At 1280px the UI aspect is 1.239: normal-flow text/card spacing adds modest height rather than forcing controls smaller. At 1440px the former header+scene was 861px (aspect 1.672); it is now 1148px. Both are evaluated at the same normalized width in the before/after image.

## Screenshot inspection and iterations

The previous `final/` captures and comparison PNGs were preserved in `correction-before/` before editing. `correction-pass-1/` showed the restored body and scene depth but an abrupt photograph edge, a wrapped feature title and an overly tall card. `correction-pass-2/` corrected the image's own rounding, feature width and card spacing. Final captures refine the foliage crop and fade to remove a hard edge/stray hair detail.

The actual full desktop screenshots, mobile full-page screenshots and final comparison PNGs were opened and inspected. Comparison HTML now uses the full-page desktop capture rather than the 900px viewport image. It scales both sources uniformly to the same width, without stretching heights.

All paths below are under `.jester/reports/verification/registration-fidelity/`:

- `desktop-before-after.png`, `mobile-before-after.png`: requested before/after comparisons.
- `desktop-comparison-corrected.png`, `mobile-comparison-corrected.png`: approved versus corrected.
- `comparison.html`: all comparisons together.
- `final/1440x900.png`, `final/1440x900-full.png`.
- `final/1280x800.png`, `final/1280x800-full.png`.
- `final/390x844.png`, `final/390x844-full.png`.
- `final/320x700.png`, `final/320x700-full.png`.
- Existing tooling also captured 430×932 and 360×800.

## Verification

- `npm run build` in `frontend`: exit 0. The application-wide >500KB JS chunk warning remains.
- `.venv/Scripts/python -m pytest tests/backend/test_registration_onboarding_boundary.py -q`: exit 0, **7 passed**.
- `node scripts/registration-visual-qa.cjs`: final exit 0, all six viewport sizes. No horizontal overflow, broken images, clipped input controls or page JavaScript errors. One real form per viewport. Normalized landmarks recorded.
- `node scripts/registration-functional-qa.cjs`: exit 0 at 1440/390/320. Validation, password visibility, loading, errors, duplicate-account controls, login/mobile menu and mocked signup/profile initialization/onboarding transitions pass. This does not prove live signup/email delivery.
- Before/after JSON comparison: heading, card, portrait and input dimensions identical at 390px and 320px.
- `git diff --check`: exit 0.

An intermediate comparison export could not overwrite the original `desktop-comparison.png` because the file was locked by the environment. Exporting to the distinct `*-comparison-corrected.png` names succeeded; all original review images are preserved. This was an artifact-write issue, not a browser/app test failure.

## Remaining differences / acceptance

Desktop depth, portrait scale/body visibility, card proportions and type hierarchy are corrected and verified. Mobile behavior/geometry is preserved. Founder visual acceptance is pending. The exact portrait pose, backdrop curve, foliage, landscape horizon and figures still differ from the flattened source. Reference-matching logo and Georgian handwritten artwork are still unavailable. The same pre-existing navigation/email-verification limitations described in the first report remain unchanged. No claim of exact photographic reconstruction or final approval is made.

Task lifecycle: **review**. Final delivery status: **VISUAL_REVIEW_REQUIRED**.
