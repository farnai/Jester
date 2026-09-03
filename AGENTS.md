# AGENTS.md — Primary AI Coding Agent Instructions for Jester

Welcome to **Jester**. This document is the primary instruction guide for all AI coding agents (Codex, Gemini, Claude, Cursor) operating within this repository.

---

## 🃏 What is Jester?

**Jester** is a **People Discovery and Relationship Intelligence** engine. 

While built with **Python 3.11+**, **FastAPI**, **PySwissEph (Swiss Ephemeris)**, and **Supabase (PostgreSQL 15+)**, **JESTER is not positioned as an astrology app**. Astrology serves strictly as the underlying, deterministic intelligence layer. The consumer-facing product is about people, connection, and relationship dynamics:
> **"They show the match. JESTER explains the connection."**

The platform follows a strict **Privacy by Design** architecture:
- Raw birth data and exact astronomical placements are kept strictly private (`birth_data` and `astro_private`).
- Derived public astrology (Zodiac signs, primary element/modality) is separated into a safe profile view (`astro_safe_profile`).
- Security is enforced at both the FastAPI layer (JWT validation) and the PostgreSQL database layer (Row-Level Security policies and SECURITY DEFINER helpers).

---

## 🏛️ Repository Overview & Architecture Map

- **Backend Application**: `backend/app/`
  - `api/`: API router aggregation (`/v1`) & system health endpoints (`/healthz`, `/v1/health`)
  - `astrology/`: PySwissEph integration, Julian Day, planetary calculation, natal orchestration, validation, and angular aspects (`aspects.py`)
  - `auth/`: Supabase JWT verification (JWKS in production, HS256 in dev/test), bearer dependencies
  - `comparisons/`: Synastry & compatibility endpoints (`/v1/compare`, `/v1/people/{id}/why`) powered by Synastry V1
  - `compatibility/`: Deterministic Synastry V1 engine (`synastry.py`), rules, models, and orchestration (`engine.py`)
  - `connections/`: Friendship request lifecycle (pending -> accepted / declined / blocked / removed)
  - `conversations/`: Direct messaging threads & chat message endpoints
  - `core/`: Database pool (`psycopg3`), custom exception models, global exception handlers
  - `interpretation/`: [STUB] LLM / Jester voice interpretation stubs (`engine.py`, `jester.py`, `prompts.py`)
  - `jobs/`: Background job handlers (daily energy generation stub)
  - `notifications/`: User in-app notifications
  - `profiles/`: User profile management (`/v1/profiles/me`)
  - `users/`: Account details endpoint (`/v1/users/me`)
- **Database Migrations**: `supabase/migrations/` (21 SQL migrations: schema, RLS, triggers, grants)
- **Documentation**: `docs/`
  - `JESTER_STRATEGIC_MARKETING_FOUNDATION.md`: Authoritative marketing foundation, positioning, JTBD, voice, and viral loop
  - `PROJECT_CONTEXT.md`: Product vision, current stage, and philosophy
  - `ARCHITECTURE.md`: Technical architecture, request lifecycle, subsystem flows
  - `ASTROLOGY_ENGINE.md`: Detailed Swiss Ephemeris engine math, limitations, status
  - `SYNASTRY_V1_SPEC.md`: Authoritative mathematical specification for Synastry V1 (`synastry-v1.0.0`)
  - `DATABASE.md`: Complete database migration guide, data classification, schema
  - `SECURITY.md`: Auth model, RLS policies, JWT rules, data isolation invariants
  - `API.md`: Comprehensive API endpoints map, request/response models, errors
  - `TESTING.md`: Test suite documentation (74 passing tests) and test gaps
  - `AI.md`: Current state of AI/LLM stubs and prompt architecture
  - `PROJECT_STATE.md`: Subsystem status matrix and active roadmap
  - `FRONTEND_ARCHITECTURE_SPECIFICATION.md`: Frontend architecture & state machines
  - `FRONTEND_CAPABILITY_SPECIFICATION.md`: Frontend functional capabilities & UI states
- **Test Suite**: `tests/` (`astrology/`, `backend/`, `compatibility/`, `database/`) — 74 passing tests

---

## 🛑 Rule #1: Source-of-Truth Hierarchy

**DO NOT TRUST DOCUMENTATION OVER CODE.**

If documentation conflicts with the codebase, the hierarchy of truth is:

1. **Actual Source Code** (`backend/app/`)
2. **Database Migrations & Schema** (`supabase/migrations/`)
3. **Automated Test Suite** (`tests/`)
4. **Documentation Files** (`docs/*.md`, `README.md`)

*Rule*: Whenever implementation changes or a conflict is discovered, **the documentation must be updated immediately to reflect reality.**

---

## 📋 Before Modifying Code

Agents MUST follow this checklist before making changes:

1. Read this `AGENTS.md`.
2. Identify the relevant subsystem (e.g. `astrology`, `auth`, `connections`, `compatibility`).
3. Read the corresponding documentation file under `docs/` (e.g. `docs/ASTROLOGY_ENGINE.md`, `docs/SYNASTRY_V1_SPEC.md`, `docs/SECURITY.md`).
4. Inspect the actual source implementation file(s).
5. Inspect related test files in `tests/`.
6. Inspect relevant database migrations in `supabase/migrations/` if database, schema, or security behavior is involved.
7. Make the **smallest appropriate change** required to accomplish the task.
8. Run the test suite: `python -m pytest`.
9. Update `docs/` if architecture, API contracts, or project state changed.

---

## 🔒 Security & Privacy Invariants

These security invariants must **NEVER** be violated:

1. **Birth Data Privacy**: Raw birth date, exact birth time, latitude, and longitude in `public.birth_data` are strictly **owner-only**. RLS policy `birth_data_select_own` restricts read access to `auth.uid()`.
2. **Astro Private Isolation**: `public.astro_private` contains exact server-calculated planet longitudes and houses. It has `REVOKE ALL` for `authenticated` and `anon` roles. Client applications must NEVER be granted access to `astro_private`.
3. **Production JWT Security**: In `ENV=production`, only asymmetric JWT algorithms (`RS256`, `ES256`, `EdDSA`) via Supabase JWKS are allowed. Symmetric `HS256` is strictly prohibited in production.
4. **Canonical Pair Constraint**: User connection pairs are stored as `(user_a_id, user_b_id)` where `user_a_id < user_b_id`. Connections can never be updated directly by authenticated clients (`REVOKE UPDATE`). State changes MUST use `/v1/connections/{id}/transition`.
5. **Mutual Block Hiding**: If User A blocks User B (or vice versa), mutual discovery of profiles, safe astrology, compatibility results, and chat messages MUST return 404 Privacy-Safe Not Found.

---

## 🔮 Astrology & Content Pipeline Rules

1. **Deterministic Calculations**: Astronomical math must rely strictly on `pyswisseph` and standard IANA timezone handling via `zoneinfo.ZoneInfo`.
2. **Unknown Birth Time Handling**: When birth time is unknown (`birth_time_precision = 'unknown'`), Ascendant and Houses MUST be set to `None`. Planetary longitudes are calculated for 12:00 UTC mean noon.
3. **Polar Region Error Handling**: Placidus house calculations fail mathematically at latitudes $> 66.5^\circ$. These cases must raise `placidus_polar_error` (HTTP 400).
4. **Separation of Signal and Voice**:
   ```text
   ASTROLOGICAL DATA → SIGNAL / ASPECT → MEANING → RELATIONSHIP / PERSONAL INTERPRETATION → JESTER VOICE → USER-FACING INSIGHT
   ```
   JESTER does not invent astrological meaning; calculation provides the signal, and JESTER translates it into human-readable voice.
5. **Do Not Claim Features That Do Not Exist**:
   - Chiron, Lilith, and Lunar Nodes are NOT calculated in `calculator.py`.
   - Daily Transits (`transits.py`) is an empty stub.
   - AI / LLM interpretation pipeline (`interpretation/`) contains empty stubs.
   - Synastry V1 (`compatibility/synastry.py`) and Aspect calculations (`astrology/aspects.py`) ARE implemented and verified with 74 tests.

---

## 🎯 Product & Strategic Invariants

1. **Category**: People Discovery + Relationship Intelligence (not a horoscope or dating app).
2. **Core Growth Model**: `ME → YOU → US → MORE PEOPLE`.
3. **Viral Axiom**: **The insight becomes the invitation**.
4. **Comparison Axiom**: **Score creates curiosity. Interpretation creates value.**

---

## 📝 Documentation Maintenance Rule

**Documentation is part of the architecture.**

Whenever a significant implementation change occurs:
- Update `docs/PROJECT_STATE.md` subsystem status.
- Update `docs/API.md` if API contracts, paths, or schemas changed.
- Update `docs/SECURITY.md` if security models or RLS policies changed.
- Update `docs/ARCHITECTURE.md` if subsystem boundaries or dependencies changed.
- Update `docs/TESTING.md` if new test suites or testing strategies were added.

Documentation must **never** claim a feature is implemented when it is only a stub or placeholder.

