# Home Experience Specification (v1.4)

Home is the authenticated front door to self-understanding, people discovery, and existing relationships. It reflects **ME → YOU → US → MORE PEOPLE**. Public registration and onboarding gates remain separate.

## Information Hierarchy

1. **Personal welcome and photographic hero.** Georgian headline, Discover CTA, and an anchor to personal insight. Accepted-connection and incoming-request counts appear only after a successful response. Existing registration photography is decorative brand artwork, never fabricated members or activity evidence. Restrained intersecting circles and axes express connection. Mobile stacks copy and photography; tablet and desktop retain a split composition.
2. **Personal insight and conversation prompt.** A light featured card displays the returned daily observation or natal baseline, preserving provenance disclosure, full-text expansion and copy feedback. Daily/verdict tabs retain the personal lens. Optional DO / DON'T guidance is initially collapsed and remains interactive when expanded. The neighboring generic conversation prompt can be cycled and copied. Its action opens Messages when accepted connections exist, otherwise Discover; it never sends a message or creates a conversation.
3. **People discovery.** Real authorized portraits, names, city/occupation, supplied interests and verified shared-interest IDs remain central. Supported observations require `sun` or `ascendant` provenance; otherwise cards use the person's bio. Filters preserve server ordering. Desktop shows three cards per client page; tablet shows four in two columns. Below 768px, one active candidate appears in a horizontal carousel with touch, keyboard and button navigation. Photo navigation is separate from candidate navigation. Requests still require sender confirmation and recipient acceptance.
4. **Connection benefits.** Three descriptive cards link to existing Connections, Discover and Me routes. They explain relationship dynamics, shared interests and self-understanding without inventing rankings, scores or personalized recommendations.
5. **Relationships and deeper self-understanding.** The connection panel shows authorized accepted-connection metadata even when a person is absent from discovery. For an accepted person also returned by discovery, Home requests the existing relationship explanation and index, with a link to the full Why page. Otherwise it retains profile navigation or an honest empty state. Incoming requests remain actionable. Alongside it, the four-facet personal lens displays existing natal interpretation content, safe sign summaries and the profile action.
6. **Closing profile invitation.** Encourages the viewer to complete or refine their own profile, followed by the 18+ and birth-data privacy notice.

## Interaction and Presentation

- Approved warm paper surfaces, carrot orange actions with charcoal labels, and restrained rounded photo framing. No fake match percentages.
- Self-hosted Noto Sans Georgian; minimum 12px labels and line-height of at least 1.55 in Home's editorial stylesheet.
- Daily/verdict and personal-facet tabs support arrow keys, Home/End, roving focus and named panels. Keyboard focus remains visible on the carousel region and controls. Reduced-motion preferences disable transitions.
- Loading, empty, error/retry and clipboard feedback remain local to the affected section. Failed requests never fabricate zero counts, people, scores or observations.
- The five existing navigation destinations, notification utility, account menu and secure sign-out remain in AppShell. Mobile navigation retains safe-area spacing and at least 48px target height.
- Home supports horizontal candidate navigation without copying Discover's full swipe deck. Navigating between people never sends a request or rejects a person.

## Data and Authorization

| Content | Source | Boundary |
| --- | --- | --- |
| Viewer identity / avatar / bio | `GET /v1/profiles/me` | Owner data; Home body never displays raw birth data |
| Personal observation | `GET /v1/interpretations/daily-energy` (`auto`, `ka`) | Returned text; distinguish daily signals from natal fallback |
| Personal facets | `GET /v1/astrology/profile/safe-astro` and `POST /v1/interpretations/resolve-natal` | Approved safe summary only |
| Discoverable people | `GET /v1/discovery/people`; existing fallback to `GET /v1/interpretations/discovery-people` | Authenticated, server ordered, deduplicated and block-aware |
| Connections / requests | `GET /v1/connections` and existing create endpoint | Canonical pairs and explicit confirmation |
| Relationship explanation / index | `GET /v1/people/{id}/why` | Only requested for a returned discovery person with an accepted connection |
| Notifications | Existing notification API and Supabase Realtime | Shared AppShell behavior |

This redesign changes presentation and grouping, not discovery eligibility, scoring, API contracts, authentication or privacy rules. Relationship explanations depend on existing authorized data; the hero and benefit cards do not manufacture one.

## Verification

- `npm run build --prefix frontend`
- `node --experimental-strip-types --test scripts/home-model.test.mjs`
- `node scripts/home-editorial-qa.cjs` against local services. Prepare isolated accounts with `python -m scripts.prepare_social_profile_qa --wave4`; remove only those manifest-verified accounts afterward with `--cleanup`. `JESTER_BASE_URL` and `JESTER_QA_OUTPUT` select the preview and evidence directory.
- Inspect desktop (1440, 1280), tablet (768), and mobile (390, 360, 320): no horizontal overflow, readable Georgian, unobstructed closing CTA, independent failure/retry, carousel controls, copy, tabs, confirmation and real route navigation.

## Design Status

The Founder request dated 2026-11-01 explicitly authorized implementation of the supplied Contemporary Renaissance / Geometric Humanism reference. The resulting Home is `IMPLEMENTED_LOCAL`, with final Founder visual review pending. Earlier canvas synthesis remains historical design provenance under [FDR-2026-03](FOUNDER_DECISION_RECORDS.md#fdr-2026-03-visual-exploration-synthesis-kzzuf-architecture--phkqc-stage); the current request governs this implementation. pen.dev was unavailable during this task, so no updated canvas is claimed. See the [implementation and verification report](../.jester/reports/implementations/TASK-HOME-HUMANISM_report.md).
