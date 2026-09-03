# 🃏 Jester — People Discovery & Relationship Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-74%20Passed-brightgreen.svg)]()

> **"They show the match. JESTER explains the connection."**

**Jester** is a high-performance **People Discovery and Relationship Intelligence** platform built with **FastAPI**, **Swiss Ephemeris (`pyswisseph`)**, and **Supabase (PostgreSQL + Auth + RLS)**. 

Astrology is the underlying mathematical intelligence layer, not the product identity. JESTER is designed to help humans understand why they click, clash, challenge, or complement each other across friendships, collaborations, and romance.

---

## ✨ Features

- 🔮 **Precision Astrological Engine**: Utilizes the C-backed Swiss Ephemeris (`pyswisseph`) library to compute high-accuracy planetary positions (10 core planets: Sun to Pluto), Placidus house systems, and angular cross-aspects (Conjunction, Sextile, Square, Trine, Opposition) with quadratic orb decay. *(Chiron, Lilith, and Nodes are planned future additions).*
- 💫 **Deterministic Synastry V1 Engine (`synastry-v1.0.0`)**: Comprehensive compatibility analysis across 4 sub-scores (Emotional Harmony, Communication, Attraction/Chemistry, Growth/Dynamics), normalized overall scoring ($10.0 - 98.0$), deterministic relationship signals, topics, and conversation starters.
- 🔒 **Privacy by Design & RLS Security**: Strict JWT verification middleware integrated with Supabase Authentication and database Row Level Security (RLS) policies. Raw birth data and exact astronomical placements (`astro_private`) are completely protected; other users only see safe derived profiles (`astro_safe_profile`).
- 👥 **Social & Connection System**: Canonical pair connection requests, friend graphs, and mutual block hiding (HTTP 404 Privacy-Safe Not Found).
- 💬 **Messaging & Conversations**: Real-time social messaging foundation between connected users with connection-gated authorization.
- ⚡ **Daily Transits & Day Vibe Infrastructure**: Architectural pipeline for calculating personal daily transits and translating them into sharp, witty JESTER daily insights (*transit calculation engine currently a stub*).
- 🤖 **JESTER Voice & Interpretation Pipeline**: Architectural framework translating deterministic signals into human, witty, slightly sarcastic JESTER language (*LLM integration currently a stub*).
- 🧪 **Comprehensive Test Suite**: 74 automated unit, API, synastry, and database security tests passing.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (ASGI, OpenAPI, Pydantic v2)
- **Astrology Engine**: [PySwissEph](https://pypi.org/project/pyswisseph/) (Swiss Ephemeris Python bindings)
- **Database & Auth**: [Supabase](https://supabase.com/) / PostgreSQL 15+ with Row Level Security (RLS)
- **HTTP Client & Async**: `httpx`, `asyncio`, `uvicorn`
- **Security**: `pyjwt`, `cryptography`, Pydantic Settings
- **Testing**: `pytest`, `pytest-asyncio`

---

## 📁 Repository Structure

```text
Jester/
├── backend/
│   ├── app/
│   │   ├── api/             # Main API routers & system health endpoints
│   │   ├── astrology/       # Swiss Ephemeris calculator, natal charts, transits
│   │   ├── auth/            # Supabase JWT authentication & verification middleware
│   │   ├── comparisons/     # Synastry & compatibility computation logic
│   │   ├── connections/     # User friendship & social connection routers
│   │   ├── conversations/   # Messaging & chat functionality
│   │   ├── core/            # Error handling, global exceptions, logging
│   │   ├── interpretation/ # Rule-based & AI interpretation generator
│   │   ├── jobs/            # Scheduled background jobs & transit updates
│   │   ├── notifications/   # In-app and push notification handling
│   │   ├── profiles/        # User profile & birth data endpoints
│   │   ├── users/           # User account management
│   │   ├── config.py        # Pydantic environment configuration
│   │   └── main.py          # FastAPI application factory
│   └── .env.example         # Environment template
├── supabase/
│   ├── config.toml          # Supabase CLI configuration
│   └── migrations/          # SQL database schema, RLS policies, triggers (001-020)
├── tests/
│   ├── astrology/           # Calculator & calculation validation unit tests
│   ├── backend/             # API endpoint, CORS, JWT & health tests
│   └── database/            # Database schema & security / RLS policy tests
├── .env                     # Local environment file (gitignored)
├── requirements.txt         # Python dependency list
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: `3.11+`
- **Supabase CLI** (optional for local database execution): [Install Guide](https://supabase.com/docs/guides/cli)
- **Git**

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Jester.git
   cd Jester
   ```

2. **Create and Activate Virtual Environment**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Copy `.env.example` to `.env` in the root directory:
   ```bash
   cp backend/.env.example .env
   ```
   Update `.env` values as needed:
   ```env
   ENV=development
   PROJECT_NAME="Jester API"
   VERSION="1.0.0"
   SUPABASE_URL=http://127.0.0.1:54321
   SUPABASE_ANON_KEY=your_supabase_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
   SUPABASE_JWT_SECRET=your_supabase_jwt_secret
   DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
   ```

5. **Start Supabase (Optional Local Database)**
   If running Supabase locally:
   ```bash
   supabase start
   ```

6. **Run the FastAPI Development Server**
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

---

## 📖 Interactive API Documentation

Once the server is running, explore the interactive documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Health Check Endpoints

- `GET /healthz` — System health check
- `GET /v1/health` — API v1 health check

---

## 🗄️ Database & Migrations

The database is built on Supabase PostgreSQL with 20 modular migration files (`supabase/migrations/`):

| Migration | Scope / Functionality |
|---|---|
| `001` - `003` | System extensions, custom Enums, and base `profiles` table |
| `004` - `006` | `birth_data`, `astro_private`, and secure `astro_safe_profile` views |
| `007` - `009` | `connections` (friendships), `compatibility_results`, `daily_energies` |
| `010` - `013` | Social `conversations`, `members`, `messages`, and `notifications` |
| `014` - `016` | Performance indexes, automated triggers, helper procedures |
| `017` - `020` | Database grants, Row Level Security (RLS), storage, Realtime |

To apply migrations locally using Supabase CLI:
```bash
supabase db reset
```

---

## 🧪 Running Tests

The test suite includes calculation accuracy verification, JWT auth checks, API route tests, and database security validations.

To run the complete test suite:

```bash
pytest
```

Or run specific test modules:

```bash
# Astrology calculation engine tests
pytest tests/astrology/

# Backend API & Auth tests
pytest tests/backend/

# Database security & RLS policy tests
pytest tests/database/
```

---

## 🔒 Security & Privacy

- **Birth Data Protection**: User exact birth dates, times, and locations are stored in restricted schemas (`astro_private`) and accessed exclusively through secure database functions or RLS rules.
- **JWT Authorization**: Requests to protected `/v1/` endpoints require a valid Supabase `Bearer <token>`.
- **CORS Protection**: Configurable allowed origins via Pydantic settings (`CORS_ORIGINS`).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
