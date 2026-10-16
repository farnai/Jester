# Registration reconstruction — implementation and visual review

## Scope and baseline

Direct founder request, 2026-10-16. Actual application route: `/auth/register`.
The initial worktree already contained an edited `RegisterPage.tsx` and untracked high-resolution portrait/panorama plus five decorative SVGs. Those supplied assets were preserved. No backend, database, auth provider, routing, other screens, dependencies or lockfiles were changed. No commit or push.

Relevant sources inspected: `AGENTS.md`, the orchestrator skill/config/index, autonomous workflow, product foundation, frontend architecture/capability specifications, route guards, auth provider, registration/onboarding boundary tests, global typography and existing brand files. The external Fidelity Kit includes all approved/rejected reference images but explicitly lacks original standalone source photographs.

## Files changed

- `frontend/src/modules/auth/RegisterPage.tsx`: replaces duplicated desktop/mobile markup with one real form; preserves signup handler and auth/onboarding redirects; associates labels, adds live error/loading semantics and Georgian language; makes client mismatch errors reachable by submitting instead of silently disabling invalid forms.
- `frontend/src/modules/auth/RegistrationScene.tsx`: header, original vector logo viewports, feature copy/icons and independent scenery layers.
- `frontend/src/modules/auth/registration.css`: scoped composition, typography, geometric curves, image crop/masks, floating card and responsive layout.
- `frontend/src/assets/registration/panorama-editorial-v2.png`: newly generated separate landscape photograph, 2048×683. Original supplied photos are untouched.
- `scripts/registration-visual-qa.cjs`: six-size browser captures, geometry/control checks and comparison captures.
- `scripts/registration-functional-qa.cjs`: browser checks with intercepted auth/API responses.
- Task state and this report; screenshots, comparison HTML, reference copy and JSON evidence under `.jester/reports/verification/registration-fidelity/`.

## Composition and visual iteration

The composition uses a normal-flow grid for story/card with independent decorative photo layers. The portrait occupies a rounded photographic field with intersecting edge/bottom masks, cream curves connect it to a separate panorama, and the form floats over the scene. Mobile uses one stacked form and a repositioned hero, without duplicate controls or a device mockup. The header uses the repository vector file's original paths, viewed through two cropped SVG viewports, rather than the previous custom React symbol.

1. `before-desktop.png`: captured supplied implementation before edits.
2. `pass-1/`: real screenshots showed the card obscuring the face and the old river panorama reducing feature contrast.
3. `pass-2/`: moved portrait left, raised card, made the card opaque, reduced typography/spacing, improved masks. Face became visible; the river-dominant photograph still diverged from the reference.
4. Final: generated a brighter panoramic photograph with small figures on the left and distant city on the right. Adjusted panorama crop and desktop minimum height to keep people below the feature descriptions. Moved annotation clear of feature text. Inspected final desktop and all four full mobile captures.

Final desktop card geometry: 1440px viewport → x986/y188, 411×590; 1280px → x877/y158, 365×577. At 1280×800 the full page is 850px tall and scrolls naturally. All mobile pages scroll naturally; they are not scaled to fit one viewport. All images are separate from functional text/controls. Approved screenshot pixels are used only in QA comparisons, never in application UI.

## Verification

- `npm run build` in `frontend`: exit 0. An application-wide large-JS-chunk warning is emitted (about 1.04MB uncompressed); no bundling architecture change made in this task.
- `.venv/Scripts/python -m pytest tests/backend/test_registration_onboarding_boundary.py -q`: exit 0, **7 passed**.
- `node scripts/registration-visual-qa.cjs`: exit 0. Playwright with installed Microsoft Edge, headless Chromium. 1440×900, 1280×800, 430×932, 390×844, 360×800, 320×700. No horizontal overflow, missing images, clipped input controls or page JavaScript errors. One form at each size. Input height 44px; mobile input font 16px. See `final/geometry.json`.
- `node scripts/registration-functional-qa.cjs`: exit 0. At 1440, 390 and 320 widths: required/email/minimum-length checks, mismatched passwords, both visibility toggles, loading/disabled submit, outgoing email/password payload, generic server errors, duplicate-account recovery controls, login links, mobile menu and successful mocked signup → profile initialization → `/onboarding/birth-data`. See `functional-results.json`.
- Functional browser tests intercept responses; they do **not** prove real registration, email delivery or backend end-to-end success. No real account was created.

Playwright was installed in an external QA tooling directory, not added as an app dependency. To reproduce, install Playwright independently, set `JESTER_PLAYWRIGHT_MODULE` to its package location, run the Vite dev server, and set `JESTER_QA_URL` if it is not on port 3001. `JESTER_QA_BROWSER` defaults to `msedge`. Run scripts from repository root. `JESTER_QA_PASS` optionally names an intermediate capture directory.

## Existing email-verification limitation

`AuthProvider.signUp` attempts `signInWithPassword` when Supabase returns no session. If confirmation is required it throws `Email not confirmed`; the registration page displays that error. There is no verification-screen transition in this implementation. The browser test reproduces this existing behavior. The provider and authentication contract remain untouched; this task cannot claim an email-verification UX that does not exist.

## Assets and copy

- `hero_woman_highres.jpg`: supplied pre-existing working-tree photo, 896×1200. Exact original provenance/licensing was not documented in the provided files. It is an alternative portrait, not the flattened reference's original photograph.
- `panorama-editorial-v2.png`: created with built-in ImageGen in this task. Prompt and provenance: `../verification/registration-fidelity/asset-provenance.md`. It is a new reconstruction, not recovered source photography.
- Feature icons: supplied working-tree SVG approximations corresponding to the Kit; not claimed to be exact original icons.
- Brand: existing `JESTER_Logo_Stacked_Outlined.svg`, original shapes/colors retained. This available vector has a muted hat/serif wordmark; the approved flattened image has a bright orange hat/bold sans wordmark. No new logo was invented.
- Fonts: existing local Noto Sans Georgian weights. There is no supplied Georgian handwritten font; annotation uses light Noto with rotation/underline as a provisional visual fallback.
- Headline follows the image/Kit: `შექმენი თავი. შექმენი სხვა. შეიგრძენი კავშირი.` The older `შეიცანი...` alternative was not substituted. Paragraphs/features retain verified existing implementation copy instead of transcribing malformed generated lettering.
- Annotation reuses the verified feature wording `შეიგრძენი უფრო ღრმა კავშირები.` The original image's handwritten sentence is not verified and is not claimed as an exact transcription.
- `როგორ მუშაობს` links to the actual feature section; login and logo link to existing routes. About/blog are non-interactive labels because no approved routes exist. URLs were requested asynchronously; no answer was available at handoff.

## Acceptance and remaining differences

| Criterion | Result |
| --- | --- |
| Real accessible form, preserved auth integration | PASS within mocked browser and existing contract-test coverage |
| Header restored and existing brand asset used | PASS; reference-brand mismatch remains |
| Independent integrated portrait/panorama and floating card | Implemented; visual review required |
| Six requested viewport captures, inspection and corrections | PASS |
| No overflow, clipped controls or broken images | PASS |
| Exact founder visual fidelity | BLOCKED by missing original photography/brand variant and remaining visual differences |

Remaining visible differences: portrait face is larger and less of the seated body is visible; the precise foliage and foreground overlap are different; desktop is more vertically compact than the reference's 1160×914 UI ratio; generated landscape/couple/city are different subjects; feature icons and some text wraps differ; mobile form spacing is more generous to keep touch targets usable; decorative handwriting and its unverified sentence are provisional. Original panorama and portrait source images are absent, so exact reproduction is not established. New imagery still needs founder acceptance.

Evidence: `../verification/registration-fidelity/comparison.html`, `desktop-comparison.png`, `mobile-comparison.png`, and all six `final/*` viewport/full-page captures.

## Final state

**VISUAL_REVIEW_REQUIRED**. **ASSET_BLOCKER** specifically for unavailable original portrait/panorama and the reference-matching logo variant. Technical checks pass; visual acceptance is not claimed. Task lifecycle is `blocked` for unresolved visual/asset acceptance, not marked completed.
