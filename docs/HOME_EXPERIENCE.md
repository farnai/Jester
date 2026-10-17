# Home experience

Home is an authenticated entry into self understanding, people discovery and existing relationships. Product intent remains in [Product Foundation](JESTER_PRODUCT_FOUNDATION.md) and [Marketing Foundation](JESTER_STRATEGIC_MARKETING_FOUNDATION.md). This document describes the implemented presentation, not new scoring or discovery policy.

## Hierarchy and actions

1. Personal observation: existing daily interpretation, with explicit distinction between computed-day and sun-sign fallback responses. Optional guidance and provenance are disclosures. Mobile long text expands on request. Copy copies the supplied observation locally; it never sends a message.
2. Existing circle: accepted connection interpretation and index, or a contextual discovery entry when there are no connections. Incoming/outgoing requests link to the established connection tabs. The primary orange action explores an accepted relationship, otherwise discovers people.
3. People: an observation-first filter and an all-profiles filter, four profiles per page. Preserve server order (currently alphabetical), label it explicitly, and never claim a recommendation ranking. The first visual feature is the first eligible item, not a highest-ranked candidate.
4. Self profile: a contextual prompt when bio is absent, or a general profile-edit entry.

The Home navigation exposes Home, Discover, Messages, Me, Notifications and an account menu. Other routes retain their existing shell. Home does not expose developer navigation.

## Data and authorization

| Content | Existing source | Presentation boundary |
| --- | --- | --- |
| Viewer name/avatar/bio/timezone | `GET /v1/profiles/me` | Owner data; no email or birth details displayed |
| Personal observation | `GET /v1/interpretations/daily-energy` (`auto`, `ka`) | Render returned text and guidance; label fallback as profile observation |
| People | `GET /v1/interpretations/discovery-people` | Authenticated response only; never pass a substitute viewer |
| Circle and requests | `GET /v1/connections` | Canonical pairs and existing statuses |
| Relationship interpretation/index | `GET /v1/people/{id}/why` | Only requested for a returned discovery person with an accepted connection; backend remains authoritative |
| Notifications | Existing AppShell list and realtime subscription | Existing behavior unchanged |

No new persistence, direct Supabase business queries, ranking, score calculation, messaging mutation or entitlement is introduced. Home shows no discovery score: the current endpoint can supply fallback scores. Candidate hooks are shown only when `presence_sign_source` is `sun` or `ascendant`; default Aries hooks are suppressed. With no supported hook, use a real bio or an honest partial-data message.

Blocked pairs are filtered defensively in Home, in addition to server filtering. Deep links appear only for accepted pairs. Errors never reuse stale relationship text. If the accepted person is absent from discovery, show the connection count and management route rather than probing a profile.

## Lifecycle and states

Each API section has independent loading, empty and retryable error handling. Broken avatars fall back to initials. No fake observation or percentage fills an empty state. Personal fallback content is explicitly distinguished from a computed daily observation.

React Query reuses established profile, connection and discovery keys. Daily cache keys include viewer and local calendar date; the mounted page checks the date once per minute and cleans up that timer. Relationship results refetch on mount. Existing auth identity-change cache clearing remains in place. API errors are handled per section; authorization remains server-owned.

This does not implement a daily scheduler, push pipeline, personalized recommendation algorithm or public share link. The API currently returns the whole discovery list; four-item pagination bounds rendering, not network payload or backend work. Server cursor pagination needs a separate contract.

## Responsive and accessibility

Desktop uses a reading column beside a narrower relationship column, then a featured profile beside a list. Tablet preserves two columns and uses bottom navigation. Mobile stacks sections, shortens the initial long observation with an explicit expansion control, and retains full content on demand. Typography and colors use the approved existing tokens and Noto Sans Georgian. Focus rings, native details disclosures, named landmarks, state announcements and 44px controls support keyboard/touch use. Skeleton animation stops under reduced motion. There is no fixed page height.

## Verification

Build: `npm run build --prefix frontend`.
Regression checks: `node --experimental-strip-types --test scripts/home-model.test.mjs`.
The test file uses existing React/TypeScript dependencies to render real components with isolated API/auth boundaries; no fixture or preview route is bundled into Home. Live browser checks are described in the task implementation report.
