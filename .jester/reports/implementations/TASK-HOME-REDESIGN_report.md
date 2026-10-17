# Implementation Report: TASK-HOME-REDESIGN

## Scope and evidence

Owner-approved strategic Home redesign, implemented on the authenticated root route. Registration, onboarding, schema, authorization and astrology/scoring engines are unchanged. No new dependencies, external analytics, seed data or credentials were added.

Read current source, relevant consumers, discovery authorization/migrations, backend discovery tests, product/marketing foundations, frontend architecture/capabilities, color system and design exploration. Marketing priorities informed hierarchy; the current approved warm orange palette takes precedence over older indigo explorations. Current on-demand daily transit code takes precedence over older statements treating all daily content as future work; scheduled delivery is still not established by that endpoint.

## Strategic findings

JESTER's value is understanding people and relationships. A number earns attention but the interpretation must repay it. The first personal observation creates recognition; an existing relationship supplies a concrete next step; discovery opens the loop again. The marketing audience hypothesis favors socially curious young adults, but this implementation does not invent targeting or change eligibility.

- First 5 seconds: personal greeting, a readable observation and a clearly separate relationship invitation. Desired feeling: recognition and curiosity, without an astrology dashboard.
- First 15 seconds: read an actual interpretation, open optional guidance, notice a familiar person or the invitation to meet someone.
- First 60 seconds: primary journey is accepted relationship exploration when available, otherwise a person's profile. Secondary journeys are self exploration, copying an insight, requests and existing conversations.
- Return motivation: new computed-day observations and real changes to people/connections. No streaks, fabricated online presence, urgency, unread events or promises of notification delivery.

These are design hypotheses, not measured retention or conversion improvements. A later approved measurement plan should assess observation-to-profile and profile-to-accepted-connection progression, with privacy-conscious event design.

## Three concepts

A — **Personal journal**: an editorial opening with one substantial thought, chapter numbers and a compact relationship margin. Strong voice and reading quality; risk of too much reading before social action.

B — **People first**: a social salon, with a large real person and surrounding profile rows; self insight becomes a short aside. Strong discovery momentum; current sparse bios/avatars and duplicated seed-like profiles weaken its emotional promise.

C — **Connection atlas**: a spatial composition linking viewer, people and relationship insights. Distinctive and tied to the product loop; sparse graph data makes it easy to imply nonexistent relationships or ranking, and mobile spatial navigation would add complexity.

| Criterion | A: journal | B: people first | C: connection atlas |
| --- | --- | --- | --- |
| Brand identity | Strong interpretation-led voice | Human, but can resemble generic social browsing | Distinctive, risks astrology visual tropes |
| Emotional impact | Personal recognition | Social curiosity | Discovery through connections |
| Usability | Clear reading and action order | Fast profile access | Requires learning graph navigation |
| Differentiation | Voice and editorial rhythm | Depends on strong profile content | Highest visual distinction |
| Real data support | Strong existing corpus | Partial profiles weaken it | Too few verified edges for a rich map |
| Technical feasibility | Existing API integrations | Existing discovery API | More layout/interaction machinery |
| Mobile | Good with disclosure | Good as a list | Spatial model is awkward |
| Scalability | Bounded sections | Needs server pagination later | Graph size and privacy complicate it |
| Marketing alignment | Interpretation creates value | More-people loop is immediate | Relationship metaphor is strong |

Selected A with B's asymmetric person/list composition and a restrained, truthful two-avatar connection motif from C. No simulated network. No identical dashboard card grid. The editorial opening is warm peach, relationship area open canvas, featured person sage, principal action carrot orange with dark text. The mark is the existing brand asset, not a replacement illustration.

## UX decisions

Personal hero and daily insight are merged. Existing connections, pending invitations and relationship dynamics share one contextual circle section. Profile browsing uses two explicit content filters and four-item pages, preserving backend alphabetical order. Large first profile means first in that list, not best match. Duplicate names are not deduplicated because distinct returned IDs are distinct people.

Primary action: explore the accepted relationship; with none, discover people. Incoming requests appear in that same context. Profile preview actions open a real person; accepted previews can open Why. All other exploration stays in existing flows. No direct message sending or request mutation was added to Home.

Removed from Home: debug navigation, email badge, arbitrary fallback scores, unsupported "top match" claims and fabricated empty-state insight text. Deferred: shared-interest matching, premium promotion, recent-activity resumption and richer recommendations because suitable contracts/data were not established.

Mobile revision after screenshot review: long insight has a five-line preview with full-text expansion; guidance is a native disclosure. This reduces initial scrolling without dropping the actual text. Tablet and desktop keep the full insight visible.

## Implementation and integrations

- `frontend/src/modules/home/HomePage.tsx`: orchestrates real queries and contextual sections.
- `HomeElements.tsx`: SVG icons, avatar fallback, skeleton and feedback states.
- `HomeNavigation.tsx`: scoped Home navigation, notifications entry, account menu and mobile navigation.
- `homeModel.ts`: supported-hook filtering, canonical pair checks, date/guidance helpers.
- `home.css`: scoped responsive editorial layout with approved CSS tokens.
- `frontend/src/shared/AppShell.tsx`: selects Home chrome only on root; auth and notification wiring preserved.
- `scripts/home-model.test.mjs`: model and rendered state regression tests.
- `docs/HOME_EXPERIENCE.md`: durable presentation/data boundaries.

APIs: profiles/me, interpretations/daily-energy, interpretations/discovery-people, connections, people/{id}/why, and existing notification list/subscription. Four Home queries run independently; one additional canonical Why query is enabled only for an accepted person already returned by discovery. No per-profile request fan-out. Avatar loading is lazy with reserved geometry. Date timer has cleanup; no new realtime subscription. The existing identity-change cache reset is retained.

## Real data and gaps

Runtime snapshot during this task: 24 accessible profiles, 5 with supported sun/ascendant observations, 1 accepted connection and 3 outgoing requests. These are local verification observations, not durable global counts. Real names, avatars, available city/bio, interpretation text, guidance, connection state and accepted index were used. No user identifiers or credentials are stored in this report.

Many profiles have missing bio/avatar/occupation, repeated names, and repeated sign-based corpus hooks. One broken avatar exercised initials fallback. Existing interpretation copy includes sharper language than the warm brand brief; editorial corpus review is advisable, and this design does not rewrite engine content.

Backend discovery has fallback score/demo-viewer paths. Home does not supply a demo identity, does not show discovery scores and suppresses fallback-sign hooks, but the backend paths remain a separate API-hardening concern. Eligibility/ranking redesign, cursor pagination and recommendation provenance need their own approved contracts. No new shared-interest inference or simulated user activity is introduced.

## Verification

- `npm run build --prefix frontend`: PASS (TypeScript + Vite). Existing application bundle remains over the 500 kB advisory threshold; no dependency was added.
- `node --experimental-strip-types --test scripts/home-model.test.mjs`: PASS. Covers canonical blocked pairs/order, unsupported hook suppression, optional guidance, date rollover/fallback, rendered loading/error/empty states, daily fallback provenance and pending/blocked privacy presentation. Node reports experimental type-stripping notice.
- Browser: signed-in Home loaded real content; initial skeletons observed. Copy confirmed success; disclosure opened with Enter. Both people filters and next page worked. Real profile opened; accepted Why page displayed the matching index and interpretation. Mobile expansion/collapse, guidance and account menu worked. 375/768/1440 layouts inspected with screenshots and DOM horizontal-overflow measurements.
- Negative states: actual component markup rendered with isolated test inputs for failures/empty/pending/blocked. No live API fault injection or database mutation performed. These tests do not prove server authorization; existing backend contracts remain authoritative.
- No project lint script exists. No destructive backend discovery fixture was run against the available real database. Auth/onboarding code was not changed; existing authenticated flow verified, not every login provider or new-account onboarding path.

## Remaining limitations

No production deployment or remote push performed for this Home task. Other pages retain their old visual shell. Existing notification realtime semantics are unchanged. Full-list discovery loading needs server pagination for larger datasets. No full cross-account/block-transition end-to-end security audit, screen-reader suite or measured retention/performance study is claimed. The UI and relevant state checks are implemented; broader product maturity is not implied.

Task is handed to review after local implementation and verification, following the control-plane lifecycle.

### Final verification notes

- The additional outgoing-request, messages and notifications navigation checks passed. The existing Messages page still shows an inbox backend-dependency notice and accepted-contact entry points; navigation success is not a claim of a complete inbox.
- All three measured viewports had document width equal to viewport width. Desktop visible links had accessible names; the mobile avatar link was explicitly named after review.
- Small muted text on peach/sage initially fell below 4.5:1; changed those tinted-surface labels to approved dark orange/sage ink tokens. Canvas muted text measures approximately 4.67:1. Primary button uses dark text.
- `git diff --check`: PASS. Portability/credential scan found no developer paths or credentials in added artifacts; substring matches were repository-relative module paths and a concept-table heading.
- Acceptance criteria: PASS for hierarchy/accepted relationship action, three-concept analysis, real data with explicit states, responsive sizes, and preservation of existing routing/privacy gates. Scope limitations above remain explicit.
- Screenshots captured outside the repository: `jester-home-desktop.jpg`, `jester-home-tablet.jpg`, `jester-home-mobile.jpg`; they are review artifacts and are not committed user data.

Continuation check (2026-10-18): final build and all seven regression tests passed again. Live session restoration returned to Home and the API supplied the next day's observation. Header now prefers that returned content date so it agrees with the observation when client/profile calendar boundaries differ. Final desktop/mobile captures were saved as temporary review artifacts.
