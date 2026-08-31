# 🃏 Jester — Social Astrology Engine Backend

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-42%20Passed-brightgreen.svg)]()

**Jester** is a high-performance, social astrology backend engine built with **FastAPI**, **Swiss Ephemeris (`pyswisseph`)**, and **Supabase (PostgreSQL + Auth + RLS)**. It powers precision natal chart calculations, synastry/compatibility analysis, user connections, real-time social features, and AI-driven astrological interpretations.

---

## ✨ Features

- 🔮 **Precision Astrological Calculations**: Utilizes the C-backed Swiss Ephemeris (`pyswisseph`) library to compute high-accuracy planetary positions (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Chiron, Lilith, Nodes), house systems (Placidus, Whole Sign), and angular aspects.
- 💫 **Synastry & Compatibility Analysis**: Algorithmic compatibility engine comparing natal charts across elements, modalities, and planetary aspects to compute composite relationship scores.
- 🔒 **Supabase Auth & RLS Security**: Strict JWT verification middleware integrated with Supabase Authentication and database Row Level Security (RLS) policies for complete privacy of sensitive birth data.
- 👥 **Social & Connection System**: Connection requests, friend graphs, and privacy-aware profile sharing (Safe Public Profiles vs. Private Astrological Data).
- 💬 **Messaging & Conversations**: Real-time social messaging foundation between connected users.
- ⚡ **Daily Transits & Job Queue**: Infrastructure for calculating personal daily planetary transits and dispatching notifications.
- 🤖 **AI Astrological Interpretations**: Dynamic interpretation engine with modular LLM integration support (OpenAI GPT).
- 🧪 **Comprehensive Test Suite**: Automated unit, integration, API, and database security tests covering 42+ test cases.

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
