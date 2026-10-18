# Home Experience Specification (v1.2)

Home is the authenticated front door to self-understanding, people discovery, and existing relationships. It reflects the product thesis: **ME → YOU → US → MORE PEOPLE**.

## Information Hierarchy & Visual Composition

1. **Editorial Primary Hero (ME / US Contextual):**
   - A confident, wide-viewport editorial composition anchored to the user's authentic identity.
   - Displays one genuine personal observation (`daily.data?.interpretation?.text`) or profile insight.
   - Clear distinction between computed daily transits (`real_transit`) and natal profile baseline (`fallback_sun_sign`).
   - One primary action CTA and an accessible, grounded "რატომ ამბობს ამას JESTER?" disclosure explaining signal provenance without exposing raw birth data.
   - Quick one-tap copy action for the insight with user feedback.
   - Optional DO / DON'T guidance tags when returned by the API.

2. **Contextual Social Moment (Circle / Relationship):**
   - If user has an accepted connection (`accepted.length > 0`): Shows a genuine relationship moment between the viewer and one connected person (`API.compatibility.why`), with communication/synastry interpretation, grounded compatibility index note ("საინტერესო ნაწილი — ახსნაა"), and direct CTA to `/people/:id/why`.
   - If incoming connection requests are pending: Displays a clear action banner to review requests.
   - If user has no connections: Provides an honest, thoughtful first-connection path without fabricated mock data.

3. **Discovery Preview (2–3 Distinct Real People):**
   - Displays 2–3 distinct, deduplicated profiles from the database (`GET /v1/interpretations/discovery-people`).
   - Shows real names, avatars/photos, cities, occupations, and genuine observations (if `presence_sign_source` is `sun` or `ascendant`) or authentic user bio.
   - Dedicated "ყველა ადამიანი" CTA leading to the full `/discover` experience.
   - Never repeats the same candidate or duplicate generic paragraphs.

4. **Closing Editorial Action:**
   - A warm, purposeful invitation to complete/refine the user's own profile and bio.

5. **Shared AppShell Navigation:**
   - 5 canonical destinations: **მთავარი** (`/`), **აღმოაჩინე** (`/discover`), **კავშირები** (`/connections`), **საუბრები** (`/messages`), **ჩემი პროფილი** (`/me`).
   - Clean notifications utility with live unread counter (`/notifications`).
   - User account dropdown with profile links and secure sign-out.
   - Mobile-first bottom navigation with 48px touch targets and clear active states.

## Data and Authorization

| Content | Source Endpoint | Boundary & Privacy Rule |
| --- | --- | --- |
| Viewer identity / avatar / bio | `GET /v1/profiles/me` | Owner data; no email or raw birth data displayed |
| Personal observation | `GET /v1/interpretations/daily-energy` (`auto`, `ka`) | Display returned text; label fallback truthfully |
| Discoverable people | `GET /v1/interpretations/discovery-people` | Authenticated; deduplicated; blocked users filtered |
| Connections & pending requests | `GET /v1/connections` | Canonical pairs (`user_a_id < user_b_id`) |
| Relationship why / index | `GET /v1/people/{id}/why` | Only requested for returned person with accepted connection |
| Notifications | `GET /v1/notifications` + Supabase Realtime | Live unread counter badge |

## Verification Requirements

- Build: `npm run build --prefix frontend` must succeed without errors.
- Automated tests: `node --experimental-strip-types --test scripts/home-model.test.mjs` must pass all tests.
- Visual verification: Render and inspect desktop (1440×900, 1280×800), tablet (768), and mobile (390×844, 320×700).
