# AGENTS.md — Primary AI Coding Agent Instructions for Jester

## What is JESTER?

JESTER is a **People Discovery and Relationship Intelligence** engine. It is not primarily an astrology, horoscope, dating, or generic compatibility application. Astrology is its deterministic intelligence layer for helping people understand themselves, other people, and relationships.

Core product loop:

```text
ME → YOU → US → MORE PEOPLE
```

Product axioms:

- **Score creates curiosity. Interpretation creates value.**
- **The insight becomes the invitation.**

Agents must preserve these principles, but must not independently invent or redefine product strategy, user flows, scoring philosophy, relationship semantics, privacy policy, astrology methodology, monetization, or positioning. Surface unspecified product decisions to the human/product owner.

## Repository / Architecture Map

Primary backend areas live under `backend/app/`:

- `api/`: router aggregation, `/healthz`, `/v1/health`.
- `astrology/`: Swiss Ephemeris integration, Julian-day calculation, validation, natal orchestration, and aspects.
- `auth/`: Supabase JWT verification and bearer dependencies. Production uses JWKS/asymmetric JWTs; HS256 is allowed only in development/test.
- `comparisons/`: `/v1/compare` and `/v1/people/{id}/why` orchestration.
- `compatibility/`: deterministic, versioned Synastry engine, rules, models, and evidence.
- `connections/`: canonical connection lifecycle and transitions.
- `conversations/`: direct conversations and message endpoints.
- `core/`: database connection access, errors, and global handlers.
- `interpretation/`: deterministic interpretation contracts, resolver/corpus infrastructure, and orchestration. External LLM generation is not assumed to be implemented.
- `jobs/`: background-job helpers; a schema/helper does not prove a scheduled product feature exists.
- `notifications/`: notification read/list API.
- `profiles/` and `users/`: profile and current-account APIs.

Other important areas:

- `supabase/migrations/`: schema, RLS, grants, triggers, helper functions, storage, and realtime.
- `frontend/`: React/Vite web client using Supabase Auth and React Query.
- `tests/`: astrology, compatibility, backend, database-security, and interpretation tests.
- `scripts/`: demo seed, corpus generation/audit, and analysis utilities.
- `docs/`: product, architecture, API, security, database, astrology, frontend, content, and audit documentation.

Inspect the actual tree before changing a subsystem; this map is orientation, not a substitute for current source.

## Source of Truth

Use authority by question:

1. **Implementation behavior:** source code, configuration, and runtime wiring.
2. **Persistence and security:** migrations, schema, RLS policies, grants, constraints, functions, and triggers.
3. **Verified behavior:** tests and reproducible runtime behavior.
4. **Product intent:** explicitly approved product specifications, UX decisions, and owner decisions.
5. **Mathematical behavior:** frozen Synastry/astrology specifications, implementation, and relevant tests.
6. **Audits:** time-bound evidence, not permanent truth.

When sources conflict: identify the discrepancy, inspect code/schema, determine whether it is stale or intentional, preserve privacy/security, and surface unresolved product or architecture choices. Do not silently rewrite behavior merely to make documents agree. Do not let an old audit override current code.

## Before Modifying Code

Before changing a subsystem:

1. Read this file and identify the exact requested behavior.
2. Read relevant product/technical documentation.
3. Inspect source implementation and relevant frontend consumers.
4. Inspect migrations, RLS, grants, and constraints when data/security is involved.
5. Inspect relevant tests.
6. Trace the cross-layer request/data flow when applicable.
7. Identify existing contracts and invariants.
8. Make the smallest coherent change.
9. Run targeted tests, then broader tests when risk warrants them.
10. Update documentation only when a documented contract, architecture, security invariant, or supported capability changes.

Do not implement from documentation alone when source can answer the question. Do not reset, discard, or modify unrelated worktree changes.

## Scope Control

Prefer the smallest change that correctly solves the requested problem. Avoid unrelated refactors, speculative abstractions, broad renames, dependency additions without justification, accidental public API changes, and unrelated product-flow edits. If adjacent work is needed for safety, explain why and keep scope explicit.

## Security & Privacy Invariants

These are hard invariants unless an approved architecture decision explicitly changes them.

### Birth data

`public.birth_data` contains private user-owned date, time, timezone, latitude, longitude, and place information. It is owner-only. It must never become broadly readable through profiles, discovery, cards, previews, compatibility responses, client metadata, logs, tests, or accidental serialization.

### Private astrology

`public.astro_private` contains exact server-calculated longitudes, houses, and retrogrades. It remains server-controlled; do not expose it directly to clients or grant it to client roles. Clients receive only API-approved safe DTOs such as `astro_safe_profile`.

### JWT/JWKS

In `ENV=production`, use only the repository-approved asymmetric JWT/JWKS path, including RS256, ES256, or EdDSA. HS256 is never a production shortcut. HS256 may be used only in development/test under the existing contract. Do not weaken verification, CORS, host restrictions, RLS, grants, or service-role boundaries for convenience.

### Canonical connections and blocking

Connection pairs are canonical unordered pairs: the same users must not create different records due to request order. Preserve the established transition API, authorization, and state machine; do not add ad-hoc direct mutations.

Blocked or hidden resources must not leak existence. Where the established contract requires it, profiles, safe astrology, compatibility, discovery, and chat must resolve as privacy-safe `404`, not an existence oracle.

## Demo / Preview Boundary

Demo, smoke-test, preview, seed, and development routes are not automatically production product behavior. Before using or changing one, determine authentication, real-data exposure, connection/privacy rules, intended environment, and production reachability.

Never use a demo fallback, hardcoded viewer, optional-auth preview, or seed identity to bypass production privacy. Do not promote preview behavior into the normal flow without explicit product/architecture approval.

## Direct Supabase / Database Access

Do not bypass backend authorization by adding arbitrary client-to-Supabase queries for protected data. Direct frontend Supabase access is acceptable only where the existing architecture explicitly permits it and RLS/grants support the intended client-owned flow. Protected business logic needs server authorization and database-level enforcement where applicable. Frontend hiding is never a security boundary.

## Database / Migration Discipline

Make database changes through ordered migrations. Before changing tables, columns, indexes, constraints, RLS, grants, database functions, or triggers, inspect related migrations and security tests. Do not casually rewrite historical migrations that may have been applied. A migration must be safe for the intended deployment model. Schema changes affecting APIs require matching contracts, consumers, tests, and docs.

## API Contract Discipline

For endpoint changes inspect request, response, and error schemas; auth/authorization; nullable fields; identifiers; pagination; status codes; frontend consumers; and tests. Do not casually rename response fields.

```text
Backend contract → API schema → frontend API client → UI state
```

Any mismatch is an integration defect. If backend returns a structured error envelope, frontend must consume that actual envelope rather than assume a different one.

## Astrology Engine Rules

Swiss Ephemeris / PySwissEph is the deterministic engine. Do not replace it with generic libraries, LLM-generated calculations, hand-written approximations, or client-side astronomy without approval.

- Use IANA timezones through Python `zoneinfo`; do not hard-code offsets or infer DST manually.
- Unknown birth time is valid. Do not invent a time. Ascendant and Houses must remain `None`; preserve the repository-defined longitude fallback.
- Preserve the established Placidus polar contract: `placidus_polar_error`, HTTP 400. Do not silently substitute another house system.
- Chiron, Lilith, Lunar Nodes, minor aspects, and house-overlay synastry must not be presented as implemented unless code/specification actually supports them.

## Signal vs Interpretation

Preserve this boundary:

```text
Birth Data → Swiss Ephemeris → deterministic signals → semantic meaning → resolver/corpus → user-facing JESTER voice
```

Do not alter deterministic math to improve wording, hard-code product voice into calculation modules, or invent astrological meaning beyond supported signals. If AI-generated language is introduced, clearly preserve the boundary between deterministic facts and generated language.

## Interpretation / Content Lifecycle

The deterministic interpretation contracts, signal mappings, resolver, and repository corpus exist. Do not label the whole interpretation layer a stub. Conversely, do not claim external LLM generation, persistent CMS/content management, automated authoring, transit-generated narrative, or production editorial lifecycle unless implemented.

Repository-backed or in-memory content is not automatically a CMS. Before implementing editable, versioned, localized, published, rollback-capable, or generated content, identify the required persistence and lifecycle architecture.

## Synastry / Compatibility Discipline

Synastry is versioned product and technical behavior. Do not casually alter scoring weights, aspect/orb rules, category semantics, normalization, aggregation, confidence rules, signal extraction, or interpretation mapping. Treat such change as engine/spec/version work, preserve stored/API compatibility, and add regression coverage. Never silently alter user scores because of an unrelated refactor.

## Product Loop and Product Decisions

Keep work aligned to `ME → YOU → US → MORE PEOPLE`:

- ME: safe self understanding, not merely raw/debug astrology.
- YOU: safe person data; never raw birth data.
- US: deterministic signals/score plus authorized interpretation; never invent meaning from score alone.
- MORE PEOPLE: authenticated, block-aware, privacy-safe discovery with approved eligibility/ranking.

Do not treat UUID lookup, smoke-test lists, hardcoded IDs, or preview endpoints as production Discover. Do not invent discovery ranking, compatibility visibility, score calibration, daily-energy commitment, content persistence, or other unresolved product policy.

## Conversations, Notifications, and Daily Energy

For chat work inspect creation, listing, participant authorization, connection requirements, message permissions, realtime, unread state, notifications, and starter-to-chat handoff. `/chat/:conversation_id` alone does not prove a complete messaging product.

Notification contracts must agree across database, backend, realtime events, frontend DTOs, and UI. Verify event producers separately from tables/read endpoints.

Time-based features require more than schemas/helpers: date/time, transit calculation, deterministic signals, interpretation, persistence, scheduler/worker, delivery, and user experience. Do not claim a production Daily Energy system or invent transit/scheduler behavior without approved specification.

## Secrets / Configuration

Never commit or log API keys, JWT secrets, private keys, service-role keys, database passwords, tokens, or production credentials. Use established environment configuration. Development defaults and demo credentials must not become production behavior.

## Testing and Runtime Verification

Run tests proportionate to risk: targeted tests first; broader/full tests for shared infrastructure, auth, privacy/security, migrations, public contracts, cross-layer work, multiple product surfaces, or release readiness. A targeted passing test is not proof of complete behavior.

When practical, verify runtime request/auth/response/error/persistence/authorization. Frontend work must consider loading, success, empty, error, auth, authorization, responsive behavior, navigation, cache/realtime invalidation, subscription lifecycle, and logout cache reset. Do not leave debug bars, hardcoded IDs, smoke controls, developer routes, or placeholder copy in production surfaces unless explicitly intended.

## Documentation Map

Use docs as a routing system, not as equally authoritative copies of reality:

- Product/UX: approved product and frontend specifications.
- Backend/API: `ARCHITECTURE.md`, `API.md`, source routes/models.
- Astrology/Synastry: `ASTROLOGY_ENGINE.md`, `SYNASTRY_V1_SPEC.md`, engine/tests.
- Database/security: `DATABASE.md`, `SECURITY.md`, migrations.
- Interpretation: `AI.md`, interpretation/content documents, source.
- Audits: `docs/audits/` and other audit reports as evidence snapshots.

Documentation should describe durable contracts. Update it when public behavior, privacy, architecture, schema, capability, or mathematical behavior changes; avoid mutable test counts and unsupported “complete” or “production-ready” claims.

## Preflight Checklist

```text
[ ] I understand the requested behavior.
[ ] I found the governing product/technical contract.
[ ] I inspected the implementation and relevant consumers.
[ ] I inspected applicable schema, RLS, and security rules.
[ ] I checked relevant tests.
[ ] I know the applicable privacy boundary.
[ ] I know whether this is production or demo/preview behavior.
[ ] I am not inventing a missing product decision.
[ ] I am not changing unrelated work.
[ ] I know how the change will be verified.
```

## Completion Checklist

```text
[ ] Implementation matches the intended contract.
[ ] Security/privacy invariants remain intact.
[ ] API contracts remain consistent.
[ ] Relevant tests pass; broader tests ran when warranted.
[ ] No secrets, demo bypasses, or stale hardcoded IDs were introduced.
[ ] Documentation changed if a durable contract changed.
[ ] The result was actually verified.
```

## What Agents Must NOT Claim

Do not claim a capability exists merely because a table, route, helper, schema, fixture, placeholder, or demo exists. A Daily Energy table is not a transit product; a chat route is not a complete messaging product; a resolver is not an external LLM system; a notification table is not event production; a UUID endpoint is not production Discover; and a unit test is not end-to-end proof.

Use precise terms: implemented, partially implemented, infrastructure exists, endpoint exists, frontend scaffold exists, not integrated, not productionized, or not implemented. Use “complete” only after relevant end-to-end verification.

## Conflict Protocol

When instructions/evidence conflict: inspect current source and schema, read relevant approved docs, determine staleness, preserve security/privacy, surface conflicts that change product or architecture, and resolve only objectively established implementation conflicts. Record decisions that create durable architectural knowledge.

## Final Principle

JESTER is a real product, not a collection of demos. Protect product clarity, user privacy, deterministic astrology, correct relationship semantics, stable contracts, small reversible changes, verified behavior, facts/interpretation/presentation separation, and the rule against invented product decisions.

> Inspect the real system. Preserve the contract. Make the smallest correct change. Verify it. Ask before inventing.
