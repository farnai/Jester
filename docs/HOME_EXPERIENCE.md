# Home Experience Specification (v1.3)

Home is the authenticated front door to self-understanding, people discovery, and existing relationships. It reflects the product thesis: **ME → YOU → US → MORE PEOPLE**.

## Information Hierarchy & Visual Composition

1. **Editorial Hero and Quick Actions:**
   - Georgian headline, authenticated greeting and Discover CTA alongside organic portrait composition. Existing accepted-connection and incoming-request counts appear only after a successful connections response; loading/error is never presented as zero.
   - Existing registration photography is decorative brand artwork, never a fabricated member or proof of user activity.
   - Four shortcuts: personal insight anchor, Discover, Connections and Messages.
   - Mobile retains a compact two-column hero and the existing bottom navigation.

2. **Personal Insight (ME):**
   - Displays one genuine personal observation (`daily.data?.interpretation?.text`) or profile insight.
   - Clear distinction between computed daily transits (`real_transit`) and natal profile baseline (`fallback_sun_sign`).
   - One primary action CTA and an accessible, grounded "რატომ ამბობს ამას JESTER?" disclosure explaining signal provenance without exposing raw birth data.
   - Primary full-text action remains visible. Copy, optional guidance and provenance are grouped in an expandable details area, with copy feedback preserved.
   - Optional DO / DON'T guidance inside an expandable disclosure when returned by the API.

3. **Active Connections (Circle / Relationship):**
   - Up to three accepted connections, using authorized `other_display_name` and `other_avatar_url` metadata even when absent from the discovery response. No fabricated online/activity indicators.
   - When an accepted person also exists in authorized discovery: an expandable relationship moment (`API.compatibility.why`), with interpretation, grounded compatibility index note ("საინტერესო ნაწილი — ახსნაა"), and direct CTA to `/people/:id/why`.
   - If incoming connection requests are pending: Displays a clear action banner to review requests.
   - If user has no connections: Provides an honest, thoughtful first-connection path without fabricated mock data.

4. **Discovery Preview (Up to Four Distinct Real People):**
   - Four portrait cards per client page from `GET /v1/interpretations/discovery-people`, with preserved server ordering, observation/all filters and pagination. Two columns on smaller screens.
   - Shows real names, avatars/photos, cities, occupations, and genuine observations (if `presence_sign_source` is `sun` or `ascendant`) or authentic user bio.
   - Dedicated "ყველა ადამიანი" CTA leading to the full `/discover` experience.
   - Never repeats the same candidate or duplicate generic paragraphs.

5. **Conversation Invitation and Closing Action:**
   - Orange invitation with a clearly generic conversation question; links to Messages only when an accepted connection exists, otherwise Discover. Does not create a chat or send a message.
   - A warm, purposeful invitation to complete/refine the user's own profile and bio.

6. **Shared AppShell Navigation (unchanged):**
   - 5 canonical destinations: **მთავარი** (`/`), **აღმოაჩინე** (`/discover`), **კავშირები** (`/connections`), **საუბრები** (`/messages`), **ჩემი პროფილი** (`/me`).
   - Clean notifications utility with live unread counter (`/notifications`).
   - User account dropdown with profile links and secure sign-out.
   - Home bottom navigation uses 48px touch targets including 360px, an opaque surface and safe-area spacing. Other routes retain their existing navigation styling.

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
- Browser integration: `node scripts/home-editorial-qa.cjs`, with temporary local accounts prepared using `python -m scripts.prepare_social_profile_qa --wave4`; remove only those manifest-verified accounts afterward with `--cleanup`.
- Visual verification: Render and inspect desktop (1440, 1280), tablet (768), and mobile (390, 360), checking overflow, action targets, actual authorized connection data, navigation and independent error/retry.
