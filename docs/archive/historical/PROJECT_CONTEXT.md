# Jester — Project Context & Vision

## 🃏 Product Concept & Strategic Positioning

**Jester** is a **People Discovery and Relationship Intelligence** platform.

While powered by a high-precision, C-backed Swiss Ephemeris (`pyswisseph`) astronomical calculation engine, **Jester is not positioned as an astrology app or horoscope tool**. Astrology serves strictly as the underlying, deterministic intelligence layer. 

The consumer-facing product is about **people, connection, curiosity, and relationship dynamics**:
> **"They show the match. JESTER explains the connection."**

Traditional astrology apps ask: *"Who are you?"*  
Jester asks: *"Why do you connect?"*

### Core Product Experience Model:
```text
ME → YOU → US → MORE PEOPLE
```
1. **Understand Myself**: *"Let's see what Jester notices about me."*
2. **See What Jester Notices About Another**: *"What would Jester say about my friend?"*
3. **Understand What Connects Us**: *"What does Jester say about us?"*
4. **Discover Other People**: *"Who else should I check?"*

### Core Viral Axiom:
> **THE INSIGHT BECOMES THE INVITATION.**  
Users receive personal, witty, slightly sarcastic observations that are sharp enough that they naturally want to show someone else (*"Look what Jester wrote about me 😂"* → *"Join and see what it says about you"* → Compare).

---

## 🎯 Backend Purpose

The Jester backend serves as:
1. **Deterministic Astronomical & Synastry Engine**: Executes C-backed Swiss Ephemeris computations for natal positions, house cusps, and cross-chart angular aspects via Synastry V1 (`synastry-v1.0.0`).
2. **Privacy & Security Gateway**: Enforces strict boundaries between private birth data (`birth_data`), server-only calculations (`astro_private`), and public safe profiles (`astro_safe_profile`).
3. **Social Graph Manager**: Handles connection requests, canonical pair constraints (`user_a < user_b`), block relationships, and user discoverability.
4. **Compatibility & Messaging Server**: Validates active connection statuses before serving compatibility scores or allowing real-time chat.
5. **AI Interpretation Pipeline**: Provides structured signals for LLM-generated insights in the signature "Jester" voice.

---

## 🏛️ Core Architectural Philosophy

1. **Privacy by Design**:
   - Exact birth parameters (date, time, lat/long) are stored in `public.birth_data` and restricted to the resource owner via database RLS (`user_id = auth.uid()`).
   - Server-calculated planetary longitudes are stored in `public.astro_private`. Client roles (`authenticated`, `anon`) have **zero** SQL permissions (`REVOKE ALL`) on `astro_private`.
   - Public components only expose high-level derived astrology (Zodiac Signs, primary element, primary modality) via `public.astro_safe_profile`.

2. **Defense in Depth**:
   - Authentication is verified in FastAPI using Supabase-issued JWTs (asymmetric JWKS enforced in production).
   - Database operations execute via direct PostgreSQL connections with explicit Row-Level Security policies as a secondary safety barrier.
   - All helper functions use `SECURITY DEFINER` with fixed `search_path = public, pg_temp`.

3. **Canonical Relationship Ordering**:
   - Connection records enforce `user_a_id < user_b_id` via a SQL check constraint. This eliminates duplicate relationship tracking and simplifies block/friend lookup logic.

4. **Astrology → JESTER Content Pipeline**:
   ```text
   ASTROLOGICAL DATA → SIGNAL / ASPECT → MEANING → RELATIONSHIP / PERSONAL INTERPRETATION → JESTER VOICE → USER-FACING INSIGHT
   ```
   JESTER does not invent astrological meaning. The calculation provides the underlying signal; JESTER translates that signal into human-readable, witty language.

---

## 🚦 Current Development Stage & Feature Matrix

The project is currently at the **Foundation (v1.0)** stage. Core infrastructure, database schemas, security rules, natal chart calculation, angular aspects, Synastry V1 compatibility engine, and social graph endpoints are fully operational and verified with **74 automated tests**. Daily transit engines and LLM voice generation are currently present as architectural stubs.

### Feature Classification:

| Feature / Domain | Status | Details |
| :--- | :--- | :--- |
| **Supabase JWT Auth & Dependencies** | **IMPLEMENTED** | Asymmetric JWKS validation for production, HS256 for dev/test. |
| **Database Migrations (001-021)** | **IMPLEMENTED** | All 21 SQL migrations, tables, indexes, triggers, grants, RLS. |
| **10 Main Planets Calculation** | **IMPLEMENTED** | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto via `pyswisseph`. |
| **Placidus House Calculations** | **IMPLEMENTED** | House cusps & Ascendant calculated for valid lat/long coordinates. |
| **Planetary Aspect Calculation** | **IMPLEMENTED** | Conjunction, Sextile, Square, Trine, Opposition with quadratic decay in `astrology/aspects.py`. |
| **Safe Astro Profile Derivation** | **IMPLEMENTED** | Maps longitudes to Zodiac signs, weights primary element/modality. |
| **Synastry Compatibility Engine (V1)** | **IMPLEMENTED** | 100% deterministic engine (`synastry-v1.0.0`): 4 sub-scores, overall score ($10-98$), signals, topics, starters. |
| **Social Connections Graph** | **IMPLEMENTED** | Request, accept, decline, block, unblock, remove state machine with canonical pairs. |
| **Direct Messaging Threads** | **IMPLEMENTED** | Create thread, send/list messages (requires active accepted connection). |
| **Notifications Infrastructure** | **IMPLEMENTED** | Notification retrieval and mark-as-read endpoints. |
| **Automated Test Suite** | **IMPLEMENTED** | 74 unit, API, synastry, and database security tests passing. |
| **Extended Planetary Bodies** | **MISSING** | Chiron, Lilith, North Node, South Node, Asteroids not calculated yet. |
| **Daily Transit Engine** | **STUB** | `astrology/transits.py` is empty stub; daily energy job inserts static JSON. |
| **AI LLM Interpretation Engine** | **STUB** | `interpretation/` modules (`jester.py`, `prompts.py`, `engine.py`) are empty stubs. |

