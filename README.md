# 🃏 JESTER — People Discovery & Relationship Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2%2B-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.2%2B-646CFF.svg)](https://vite.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![Tests](https://img.shields.io/badge/Tests-193%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **"Score creates curiosity. Interpretation creates value. The insight becomes the invitation."**

**JESTER** is a high-performance **People Discovery and Relationship Intelligence** platform. It is not a generic horoscope, dating, or astrology app. Astrology serves strictly as JESTER's deterministic intelligence layer to help people understand themselves, each other, and their interpersonal dynamics across romance, friendships, and creative collaborations.

Core Product Loop:
$$\mathbf{ME} \longrightarrow \mathbf{YOU} \longrightarrow \mathbf{US} \longrightarrow \mathbf{MORE\ PEOPLE}$$

---

## ✨ System Capabilities & Architecture

### 1. Deterministic Astrological Intelligence Layer
- **Swiss Ephemeris (`pyswisseph`) Integration:** Deterministic calculation of celestial longitudes (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto) and Placidus houses.
- **6 Core Personality Placements:** Full semantic modeling for **Sun** (`self.identity`), **Moon** (`self.emotional`), **Ascendant** (`self.persona`), **Mercury** (`self.cognition`), **Venus** (`self.relation`), and **Mars** (`self.action`).
- **Precision Timezone Handling:** IANA timezones via Python `zoneinfo` with exact Julian Day computation. Unknown birth time is supported cleanly (Ascendant/Houses remain `None`).

### 2. Synastry V1 Compatibility Engine (`synastry-v1.0.0`)
- **Multi-Dimensional Relationship Scoring:** Deterministic synastry normalized into an overall score ($10.0 - 98.0$) across 4 distinct dimensions:
  - Emotional Harmony
  - Communication & Intellectual Flow
  - Attraction & Chemistry
  - Long-Term Growth & Dynamics
- **Deterministic Signal Extraction:** Quadratic orb decay for major cross-aspects (Conjunction, Trine, Sextile, Square, Opposition) with harmonic category classifications (`harmony`, `attraction`, `communication`, `growth`, `stability`, `notice`).
- **Deep Analysis:** Structured evidence trace, conversation starters, and discussion topics.

### 3. Interpretation Architecture V2 & Georgian Content Layer
- **Contract-Based Interpretation:** Decoupled semantic contracts (`InterpretationContract`) resolved deterministically from calculated signals.
- **Approved Georgian Copywriter Corpus:** Handcrafted, witty, slightly sarcastic JESTER voice in Georgian (`locale: "ka"`), with support for multi-asset authoring and editorial provenance (`copywriter` vs `ai_draft`).
- **Multi-Context Resolution:** Context-aware interpretations across `self` (natal profile), `relationship` (romantic synastry), `friendship`, and `daily_energy`.
- **Transitional Daily Energy (Day Vibe):** Daily energetic archetype mapping (e.g. Aries $\to$ `confidence`, Scorpio $\to$ `introspection`) with approved Georgian copy (*dynamic transit engine planned for Phase 5*).

### 4. Privacy by Design & Security Invariants
- **Birth Data Isolation:** User birth dates, times, coordinates, and places are stored exclusively in owner-only `public.birth_data` protected by PostgreSQL Row Level Security (RLS). They are never exposed to other users, cards, or discovery previews.
- **Private Astrology Protection:** Exact astronomical degrees and houses reside in server-only `public.astro_private`. Other users and client applications only ever receive sanitized, safe DTOs (`astro_safe_profile`).
- **Canonical Connection States:** Canonical unordered pair logic for connections, friend requests, and mutual block hiding (HTTP 404 Privacy-Safe Not Found).

### 5. Frontend Client & Visual Foundation Lab
- **Client Stack:** React 19, Vite 8, TypeScript, TanStack React Query, React Router v7.
- **Forensic Backend $\to$ Frontend Inspector (`/__debug/backend-audit`):** Comprehensive developer lab inspecting the live end-to-end pipeline:
  $$\text{PostgreSQL} \longrightarrow \text{Swiss Ephemeris} \longrightarrow \text{Safe Astro API} \longrightarrow \text{React Query Cache} \longrightarrow \text{Georgian Content UI}$$
  Includes live deterministic A/B state switching (London Aries vs Tbilisi Scorpio), full un-truncated Georgian texts for all 6 planets, and pipeline verification matrices.
- **Social Surfaces:** Discovery cards, Person profiles, Why compatibility breakdowns, Us comparison views, Connections, and direct Messaging.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+, ASGI, Pydantic v2) |
| **Astrology Engine** | [PySwissEph](https://pypi.org/project/pyswisseph/) (Swiss Ephemeris C-bindings) |
| **Database & Auth** | [Supabase](https://supabase.com/) / PostgreSQL 15+ with Row Level Security (RLS) |
| **Frontend Web Client** | [React 19](https://react.dev/), [Vite 8](https://vite.dev/), [TypeScript](https://www.typescriptlang.org/) |
| **Data Fetching & Cache**| [@tanstack/react-query v5](https://tanstack.com/query/latest) |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` (193 automated tests) |

---

## 📁 Repository Structure

```text
Jester/
├── backend/
│   ├── app/
│   │   ├── api/             # Aggregated API router & system health checks (/healthz, /v1/health)
│   │   ├── astrology/       # Swiss Ephemeris calculator, natal placements, developer debug router
│   │   ├── auth/            # Supabase JWT/JWKS verification & bearer dependencies
│   │   ├── comparisons/     # /v1/compare and /v1/people/{id}/why orchestration
│   │   ├── compatibility/   # Versioned Synastry V1 engine, models, and scoring logic
│   │   ├── connections/     # Canonical connection state machine & transitions
│   │   ├── conversations/   # Realtime conversations and message endpoints
│   │   ├── core/            # Database pooling, error handlers, and global exceptions
│   │   ├── interpretation/  # Content Architecture V2, resolver, contracts, and Georgian corpus
│   │   ├── jobs/            # Background jobs & daily energy worker stubs
│   │   ├── notifications/   # In-app notification endpoints
│   │   ├── profiles/        # User profiles & discoverability endpoints
│   │   ├── users/           # Authenticated user account API
│   │   ├── config.py        # Pydantic Settings & environment validation
│   │   └── main.py          # FastAPI application factory
│   └── .env.example         # Backend environment template
├── frontend/
│   ├── src/
│   │   ├── core/            # API client, typed DTOs, Supabase client, auth context
│   │   ├── modules/         # Feature modules (home, discover, people, compatibility, me, auth)
│   │   ├── navigation/      # React Router routing table & ProtectedRoute guards
│   │   ├── shared/          # Universal UI design system (Card, Button, Badge, Skeleton)
│   │   └── ui/              # Developer tools (BackendAuditDebugPage, VisualLab)
│   ├── package.json         # Frontend dependencies & scripts
│   └── vite.config.ts       # Vite configuration
├── supabase/
│   ├── config.toml          # Supabase CLI configuration
│   └── migrations/          # 20 ordered SQL migrations (schema, RLS, triggers, functions)
├── tests/
│   ├── astrology/           # Swiss Ephemeris validation, aspects, and calculation tests
│   ├── backend/             # API routes, CORS, JWT auth, self-healing, and preview tests
│   ├── compatibility/       # Synastry V1 engine, scoring formulas, and topics tests
│   ├── database/            # Database security, RLS enforcement, and isolation tests
│   └── interpretation/      # Content V2, contracts, and Mars/Mercury/Venus corpus tests
├── docs/                    # Architecture, API specs, database docs, and semantic audits
├── requirements.txt         # Python backend dependencies
└── README.md                # Project documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python:** `3.11+`
- **Node.js:** `18+` or `20+` (npm / npx)
- **Supabase CLI:** (Optional for local PostgreSQL execution) [Install Guide](https://supabase.com/docs/guides/cli)

---

### 2. Backend Setup

1. **Create and Activate Virtual Environment:**
   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   ```bash
   cp backend/.env.example .env
   ```
   Ensure `.env` contains your Supabase URL, anon key, and database connection string:
   ```env
   ENV=development
   PROJECT_NAME="Jester API"
   VERSION="1.0.0"
   SUPABASE_URL=http://127.0.0.1:54321
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
   ```

4. **Start the FastAPI Backend:**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
   The backend API will be available at:
   - **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Check:** [http://localhost:8000/healthz](http://localhost:8000/healthz)

---

### 3. Frontend Setup

1. **Navigate to the frontend directory & install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Vite Development Server:**
   ```bash
   npm run dev
   ```
   The web application will be live at:
   - **Main Client:** [http://localhost:5173/](http://localhost:5173/)
   - **Forensic Data & Content Inspector:** [http://localhost:5173/debug/backend-audit](http://localhost:5173/debug/backend-audit)
   - **Visual Foundation Lab:** [http://localhost:5173/visual-lab](http://localhost:5173/visual-lab)

---

## 🧪 Testing & Verification

### Run the Backend Test Suite (193 Tests)
```powershell
.venv\Scripts\python.exe -m pytest tests
```
Runs the complete suite covering:
- Mathematical accuracy of Swiss Ephemeris and coordinate conversions
- Synastry V1 calculations and orb decay formulas
- Content V2 resolution, multi-context fallback, and contract matching
- JWT verification, RLS policies, and owner birth data security

### Verify Frontend TypeScript & Production Bundle
```bash
cd frontend
npm run build
```
Executes `tsc` type checking and `vite build` to guarantee zero compile-time errors.

---

## 🔒 Security & Privacy Invariants

- **Zero Raw Data Exposure:** `public.birth_data` contains private, user-owned birth parameters. It is never exposed in profile views, compatibility payloads, or public discovery.
- **Server-Controlled Astrology:** `public.astro_private` exact degrees and houses are accessed exclusively by server calculation logic. Clients only receive the safe `SafeDerivedAstrologyResponse`.
- **Production JWT Verification:** Production mode strictly enforces asymmetric JWT/JWKS verification. HS256 is restricted to development/test fixtures.
- **Comprehensive Policy:** For full architectural details, role privilege matrices, existence oracle elimination, and vulnerability disclosure, see [**SECURITY.md**](SECURITY.md).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
