# Jester — Project Context & Vision

## 🃏 Product Concept

**Jester** is a privacy-first, social-first astrology platform designed to bring high-precision astronomical calculations together with social connections, relationship compatibility analysis (synastry), real-time messaging, and personalized AI interpretations.

Unlike traditional horoscope apps that expose raw birth data or use simplistic sun-sign astrology, Jester separates sensitive astronomical placement data from public profiles. It empowers users to explore deeper interpersonal connections based on astrological dynamics without sacrificing privacy.

---

## 🎯 Backend Purpose

The Jester backend serves as:
1. **Deterministic Astrology Calculation Engine**: Executes C-backed Swiss Ephemeris (`pyswisseph`) computations for natal planetary positions, house cusps, and transits.
2. **Privacy & Security Gateway**: Enforces strict boundaries between private birth data (`birth_data`), server-only calculations (`astro_private`), and public safe profiles (`astro_safe_profile`).
3. **Social Graph Manager**: Handles connection requests, canonical pair constraints, block relationships, and user discoverability.
4. **Compatibility & Messaging Server**: Validates active connection statuses before serving compatibility scores or allowing real-time chat.
5. **AI Interpretation Pipeline**: Serves as the structured context engine for LLM-generated insights in the signature "Jester" tone.

---

## 🏛️ Core Architectural Philosophy

1. **Privacy by Design**:
   - Exact birth parameters (date, time, lat/long) are stored in `public.birth_data` and restricted to the resource owner via database RLS (`user_id = auth.uid()`).
   - Server-calculated planetary longitudes are stored in `public.astro_private`. Client roles (`authenticated`, `anon`) have **zero** SQL permissions (`REVOKE ALL`) on `astro_private`.
   - Public components only expose high-level derived astrology (Zodiac Signs, primary element, primary modality) via `public.astro_safe_profile`.

2. **Defense in Depth**:
   - Authentication is verified in FastAPI using Supabase-issued JWTs.
   - Database operations execute via direct PostgreSQL connections with explicit Row-Level Security policies as a secondary safety barrier.
   - All helper functions use `SECURITY DEFINER` with fixed `search_path = public, pg_temp`.

3. **Canonical Relationship Ordering**:
   - Connection records enforce `user_a_id < user_b_id` via a SQL check constraint. This eliminates duplicate relationship tracking and simplifies block/friend lookup logic.

---

## 🚦 Current Development Stage & Feature Matrix

The project is currently at the **Foundation (v1.0)** stage. Core infrastructure, database schemas, security rules, basic natal chart calculation, and social graph endpoints are fully operational. Advanced compatibility math, planetary aspect calculations, daily transit engines, and LLM integrations are currently present as stubs or baseline placeholders.

### Feature Classification:

| Feature / Domain | Status | Details |
| :--- | :--- | :--- |
| **Supabase JWT Auth & Dependencies** | **IMPLEMENTED** | Asymmetric JWKS validation for production, HS256 for dev/test. |
| **Database Migrations (001-020)** | **IMPLEMENTED** | All 20 SQL migrations, tables, indexes, triggers, grants, RLS. |
| **10 Main Planets Calculation** | **IMPLEMENTED** | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto via `pyswisseph`. |
| **Placidus House Calculations** | **IMPLEMENTED** | House cusps & Ascendant calculated for valid lat/long coordinates. |
| **Safe Astro Profile Derivation** | **IMPLEMENTED** | Maps longitudes to Zodiac signs, weights primary element/modality. |
| **Social Connections Graph** | **IMPLEMENTED** | Request, accept, decline, block, unblock, remove state machine. |
| **Direct Messaging Threads** | **IMPLEMENTED** | Create thread, send/list messages (requires active connection). |
| **Notifications Infrastructure** | **IMPLEMENTED** | Notification retrieval and mark-as-read endpoints. |
| **Automated Test Suite** | **IMPLEMENTED** | 42 unit, API, and database security tests passing. |
| **Extended Planetary Bodies** | **MISSING** | Chiron, Lilith, North Node, South Node, Asteroids not calculated yet. |
| **Planetary Aspect Calculation** | **MISSING** | Angular aspects (Conjunction, Trine, Square, etc.) & orbs not implemented. |
| **Synastry Compatibility Engine** | **STUB** | Endpoints return a static hardcoded score (`82.5`) baseline. |
| **Daily Transit Engine** | **STUB** | `astrology/transits.py` is empty; daily energy job inserts static JSON. |
| **AI LLM Interpretation Engine** | **STUB** | `interpretation/` modules (`jester.py`, `prompts.py`) are empty stubs. |
