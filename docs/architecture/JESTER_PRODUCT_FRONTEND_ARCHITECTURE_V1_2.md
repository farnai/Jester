# JESTER — Product & Frontend Architecture v1.2

**Date:** 2026-10-18  
**Status:** Founder-directed architecture for **local-only development**; product decisions distinguished from proposals and implementation state.  
**Source basis:** October 2026 JESTER Frontend Product Inventory, Product/Marketing Foundation, the approved JESTER brand direction, Founder feedback on Home, and Architecture v1.1. **Not a claim that all planned changes are already implemented in code.**

---

## 0. What Changed from v1.1

1. **Environment:** Only a local development instance is running. There is no deployed product or real production user base. Existing data are development/test fixtures; do not describe them as real customers. There may still be local accounts with unknown DOB; do not assume specific ages without checking.
2. **Git:** Normal local `git` changes, commits, pulls and pushes to the correctly configured JESTER repository are permitted. Preserve secrets, avoid force-pushing or rewriting history, and never commit `.env`, generated test fixtures, credentials or large unlicensed image assets.
3. **18+:** First **public** MVP will be for 18+ users (approved policy). **Server-side eligibility enforcement is a public launch gate**, not a reason to suspend local UI/UX work now. The earlier standalone 'implement 18+ eligibility' task was **not executed**; mark this feature `PLANNED / NOT YET IMPLEMENTED` pending code and server verification. A small 18+ notice may be introduced, but must not be misreported as security enforcement.
4. **Immediate Work:** Move from repeated audits and generic Dashboard redesigns to real coherent, modern React visual design. Update canonical docs; establish a concrete design system; implement and visually verify **Wave 1: Application Shell + Home**. Prepare the component patterns / contracts needed for Discover, Person and ME. Do not try to implement every subsystem in one unbounded run.
5. **No Production Migrations / Deploy:** Local database migrations may be made with informed, scoped changes and tests; no destructive reset unless explicitly needed for dev fixtures, with backup/confirmation and clear reporting. Git push is **not** the same as public production launch.

---

## 1. Product Thesis

**JESTER = People Discovery + Relationship Intelligence + Communication.** It is not a dating clone and not a horoscope portal. User journey: **ME → YOU → US → MORE PEOPLE**. Its distinctiveness is that it makes social discovery emotionally compelling, helps people communicate, and offers optional, privacy-safe explanations of its astrological interpretation.

Astrology is **secondary in visual hierarchy but central to explanation provenance**. Mathematical chart/aspect calculation is distinct from scientifically validated personality assessment; don't present derived narrative as psychological fact. An interpretation must have a valid source rule and show the appropriate "რატომ ამბობს ამას JESTER?" pathway without exposing private birth data or exact longitudes.

---

## 2. Five Main User Destinations

| Destination | Existing route | Core user question | Primary interaction |
|---|---|---|---|
| **Home** | `/` | What is worth seeing or doing now? | Open one useful insight or meaningful social action |
| **Discover** | `/discover` | Who could be interesting to meet? | Open real person profile, optionally filter |
| **Connections** | `/connections` | Who is in my circle / awaiting a response? | Manage request / open existing relationship |
| **Messages** | `/messages` | Which conversations can I continue? | Open actual conversation thread |
| **ME** | `/me` | What can others see, and what can I discover about myself? | Edit own profile / explore grounded self insight |

Contextual pages: `/people/:id`, `/compare/:id`, `/people/:id/why`, `/chat/:conversation_id`; auth and onboarding routes remain separate. Mobile navigation must not merely shrink desktop nav.

---

## 3. UX Priority Model

**Home is a curated entry point, not a component catalogue.** Clear hierarchy: one narrative hero / one main CTA, one contextual relationship or inbox module, one visually rich discovery preview. Avoid repeating the same person or the same generic paragraph in multiple sections. Use only real returned data and real evidence; handle zero-connection / sparse / empty states deliberately. Displaying a score without explaining it is not a satisfying interaction.

**Discover is photo-/interest-first.** Profile imagery, identity, city and common interests are primary. Astrology is a soft optional second layer; no full synchronous synastry calculation for all discoverable users. The feed needs server pagination and safe filtering as a separate engineering task before scale.

**Person profile** = photo gallery, public identity, bio, city, interests, human conversation context, then safe astrology and compare preview. Connection request is easy to find; accepted state enables chat / deeper Why; blocking must remain safe.

**ME** = public presentation editing (avatar/gallery, interests, bio, privacy) separated from self interpretation; don't confuse editing a profile with reading natal analysis.

**Messages** = true inbox from conversations endpoint (as supported), not an ersatz list of accepted connections.

---

## 4. The Visual Language to Implement

**Direction:** **Warm Modern Editorial + Human Social Discovery** (approved direction for first implementation wave). Modern, bold but not childish, sophisticated but not corporate sterile. Light backgrounds, carrot orange as a focused accent, secondary sage/peach, excellent Georgian typography, confident headlines, photographs of authentic adult people, meaningful asymmetry, clean navigation, deliberate white space rather than huge empty regions.

**Tokens (match actual project tokens or consolidate safely):**
- Primary CTA: `#FF7A2F`
- Hover state: `#E9681F`
- Warm canvas: `#FAF7F2`
- White surface: `#FFFFFF`
- Ink text: `#222630`
- Secondary text: `#6A716F`
- Sage accent: `#95A686`, sage wash: `#E8EFE2`
- Peach accent: `#F5DDD1`
- Borders: `#E6E0D7`

Check contrast especially orange CTA with small white text. Noto Sans Georgian/Noto Sans for real interface text; don't use rasterized Georgian text from image generation. Reuse original JESTER logo asset. Avoid a zoo of borders, badges, card stacks and fake decorative icons.

**Layout:** fluid modern desktop (max-width around 1200–1320px depending on measured content), substantive page width, visually balanced hero, useful content above fold, mobile-first breakpoints. Verify browser widths 320, 375/390, 768, 1280, 1440; test full-page and viewport. No arbitrary overflow hiding.

**Image policy:** use genuine authored or lawfully sourced photo assets with documented provenance and right of use. Show **adult** people in diverse genuine social settings (friends, interests, neighborhood/city, groups), not stereotype romance-only stock. Photos must have clear purpose, object position, responsive crops, alt text and performance sizes. Never ship flattened image mockups as HTML substitutes or tiny upscaled crop images. If generation unavailable, use branded gradients/shape/avatars rather than pretend an image exists. During dev distinguish project-generated decorative imagery from actual user-uploaded photos.

**Component design:** bespoke layout primitives and a small functional UI library; not one generic `Card` component for every object. Build `HomeHero`, `InsightFeature`, `RelationshipMoment`, `DiscoveryPreview`, `PersonCard`, `InterestChips`, `EvidenceDisclosure`, `MediaGallery`, etc. only as justified. Explicit loading/empty/error, keyboard/focus, tap target states.

---

## 5. Existing Functionality vs. Planned Work Separation

According to the October read-only inventory (requires source inspection prior to modifications):
- **Implemented / Reusable:** Auth/onboarding (locally verified earlier), basic profile and self insights, Sun/Moon safe DTO, deterministic compatibility + corpus, connections, real-time chat, interests schema and own-interest endpoints, existing design tokens, TanStack Query, routes, smoke/visual/debug surfaces.
- **Partial:** Home information hierarchy, Discover feed/filters/pagination, actual Messages inbox integration, user-friendly profile edit, reusable social visuals.
- **Missing / Planned:** Multi-photo gallery (currently single avatar), gallery reorder/delete flows, common-interest output for other person, reports/moderation, monetization accounts/ledger/entitlements/quotas, public-MVP 18+ server-enforced eligibility as newly approved requirement.
- **Unknown / Verify:** Exact coverage and privacy safety of `evidence_trace`, Synastry dimension count (inventory says 5; older spec differs), ability to update and display interests on Person, current `welcome` routing, debug-route production guards, actual registry of original logo/image assets.

A status saying `IMPLEMENTED` is not a substitute for browser/DB verification. Do not relabel planned work as complete.

---

## 6. Media, Interests, Explainability — Target Contracts

**Photos:** Up to 6 per user is a **proposed working design default**, subject to load/storage assessment; one primary; order/edit/delete; image transforms, EXIF/GPS removal, file size validation, storage authorization, abuse reports and moderation. The old single `avatar_url` must remain compatible during transition. Avoid asserting one public Storage bucket can revoke access immediately after sharing.

**Interests:** Existing tables and endpoints can be reused. Show own selected tags and shared interest intersections where accurately calculable; if absent, omit counts, do not fabricate. User should edit tags after onboarding.

**Explainability:** Calculation → structured signals → rule/corpus provenance → displayed narrative → privacy-filtered explanation DTO. A sentence may derive from multiple aspects, never fake a singular Mars–Venus aspect. Public preview, self, accepted connection have different authorization. Optional sheet/dialog / accordion based on UX context. Unknown birth time means no invented rising/houses.

---

## 7. Discovery Performance Contract

First DB-filter candidate rows (exclude self, blocked, not discoverable, underage once policy shipped), indexed stable server pagination, lightweight enrichment (photo, bio, interest tags, shared counts) for just current page. Compute compatibility **on profile open / explicit preview**, or valid cache. Do not run full synastry on all candidates each request. Filtering by city + interests first; detailed affinity scoring deferred.

**Implemented Wave 3:** [Bounded discovery and social profiles](../DISCOVERY_WAVE3.md) documents the owner-authorized swipe deck: left = local Next; right = explicit connection confirmation, with keyboard/buttons and a browsable list. It adds no Likes, Matches or permanent rejection. Canonical connection transitions remain authoritative. Card media is bounded to current/next; Person Profile places connection controls before progressive astrology disclosure. Visual status remains `FOUNDER_REVIEW_REQUIRED`.

---

## 8. Free, Plus & Credits — Commercial Architecture

**Business decision:** Retain **free core social loop** (profile, photos, browsing, interests, basic connections and human-to-human messages), reserve recurring advanced interpretive/AI value for **Jester Plus**, and on-demand costly generation for **Credits**. Detailed price, included allotments, refunds and chosen payment provider are **not yet approved**. Do not add a fake paywall or create payment forms in first design wave.

Plan later server-owned feature catalogue/entitlements, metering, idempotent transaction ledger, payment webhooks and cost monitoring. Use quotas before enabling expensive external AI requests. Unlike human messaging, AI chat incurs model cost; they must not share one quota. Closed/local beta may collect no payments while contracts are designed now; no premature promise of unlimited generative AI.

---

## 9. 18+ Public-Launch Gate (Approved Policy, Implementation Deferred)

This is a binding **public product policy**, not a claim that controls currently exist. Server verifies declared private DOB, enforces at completion and protected social APIs, returns fail-closed for missing/invalid, and excludes underage accounts from discoverable results; frontend appropriately explains eligibility. Existing development accounts are test fixtures and may be migrated after non-destructive inspection. No production users exist according to Founder. Birthday boundary and leap day tests required. Self-reported DOB ≠ independently verified age. Before public launch add report/flag UX, image moderation workflow, accessible account deletion, and dev/debug route isolation.

**Priority:** Document and enforce as a release gate. Do not derail current local design work to implement this as a standalone first task. If a user-facing adult-only notice is trivial and accurate, it can be added, but do not mark backend eligibility as DONE until tested.

---

## 10. Execution Sequence

| Wave | Action | Definition of Done |
|---|---|---|
| **1 — NOW** | Update canonical docs; create coherent Visual System; implement AppShell + **Home** as a real modern, human-centered React experience | Screenshots at desktop/mobile + actual API data, responsive and keyboard QA; Home meaningful first-user state; tests/build pass; no fake data |
| **2** | ME / Person: public profile editor, interest display/edit, photo gallery (backend+storage+RLS) | End-to-end local upload/reorder/delete; safe person browse + real interests |
| **3** | Discover: DB pagination, filters, efficient profile cards | Test with pagination boundary and blocked/sparse cases; no N×Synastry |
| **4** | Connections, real inbox, explanation UI | Real 2-account social loop, authorized Why and conversational starter |
| **5** | Public launch gates | 18+ server policy, report/moderation, deletion, rate limits, secrets/privacy, debug isolation, SMTP, metrics |
| **6** | Paid offerings | Pricing/unit economics, entitlements, ledger, payment processor + recurring Plus, optional Credits |

**Wave 1 explicit scope:** Refine Home modules and shared navigation; prepare styles/components for Discover/Person/ME without claiming gallery/filters are implemented. Move on in small verified slices rather than a giant simultaneous redesign.

---

## 11. Git & Local Environment Rules

The Founder authorizes Git work. Inspect status/diff; create scoped commits and push to the confirmed JESTER remote if configured and safe. No `reset --hard`, no force-push, no leaked secrets, no destructive DB reset. Current local Supabase users are dev fixtures, but don't delete them casually; test state migrations in local only. Never claim deployed/public-ready merely because pushed to GitHub.

---

## 12. Approval & Completion Criteria

Statuses:
- `DESIGN_DIRECTION_SELECTED`
- `IMPLEMENTED_LOCAL`
- `FUNCTIONALLY_VERIFIED`
- `VISUALLY_REVIEWED`
- `FOUNDER_APPROVED`
- `PUBLIC_READY`

Wave 1 ends at **IMPLEMENTED_LOCAL + FUNCTIONALLY_VERIFIED** with screenshots for Founder review; do not self-issue Founder approval. 18+ public rule remains **PLANNED / PUBLIC LAUNCH BLOCKER** until full implementation/verification. No payment, photo-gallery or ranking functionality to be declared done because visually mocked.
