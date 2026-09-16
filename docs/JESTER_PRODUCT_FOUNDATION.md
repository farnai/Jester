# JESTER — Product Foundation

**Document Type:** Canonical Product Foundation & Source of Truth  
**Authority Level:** Level 2 (Directly under `AGENTS.md`)  
**Audience:** Product Designers, Engineers, Product Owners, Copywriters  
**Primary Locale:** Georgian (`ka`) First; English (`en`) Secondary  
**Status:** LOCKED PRODUCT DECISION  

---

## 1. What JESTER Is

**JESTER** is a **People Discovery and Relationship Intelligence** platform.

It is engineered to help human beings understand themselves, understand other people, and navigate the subtle dynamics of interpersonal chemistry—spanning friendships, creative collaborations, activity partnerships, intellectual dialogues, and intentional dating.

Beneath the surface, JESTER runs a deterministic astronomical calculation engine powered by Swiss Ephemeris (`pyswisseph`) and an advanced Synastry algorithm (`synastry-v1.0.0`). Above the surface, however, JESTER is completely humanized: it translates astronomical geometry into sharp, relatable, psychologically astute observations about how two people communicate, where they find friction, why they spark, and what makes them click.

```text
       ASTROLOGICAL ENGINE (Swiss Ephemeris / C-Bindings)
                              ↓
         DETERMINISTIC SIGNALS (Aspect Geometry & Orbs)
                              ↓
        RELATIONSHIP INTELLIGENCE (Semantic Contracts)
                              ↓
        JESTER VOICE LAYER (Witty, Observant, Sharp)
                              ↓
   USER EXPERIENCE (Curiosity → Understanding → Connection)
```

---

## 2. What JESTER Is NOT

To maintain absolute brand clarity and prevent falling into generic tropes, JESTER is defined by five strict negative boundaries:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        WHAT JESTER IS NOT                              │
│                                                                        │
│   ❌ NOT a Traditional Astrology App (No horoscopes, no crystal balls)  │
│   ❌ NOT a Dating-Only App (Platonic, creative, activity & romantic)    │
│   ❌ NOT an Open AI Chatbot (No conversational LLM hallucinations)      │
│   ❌ NOT a Swipe-Card Game (No binary left/right discard mechanics)     │
│   ❌ NOT a Diagnostic Assessment (No MBTI labels, no moral scores)      │
└────────────────────────────────────────────────────────────────────────┘
```

1. **NOT a Traditional Astrology or Horoscope App:**  
   Swiss Ephemeris is computational infrastructure, exactly like an encryption algorithm or a database index. Users do not need to decipher astrological natal wheels, planetary degree symbols ($\degree$), or house cusps to understand interpersonal chemistry. Primary product surfaces never show natal wheel graphics or occult jargon.
2. **NOT a Dating-Only App:**  
   Romantic connection is only one of six valid relational intents. Friendships, creative collaborations, activity partnerships, and intellectual exchanges are treated with equal first-class platform dignity.
3. **NOT an Open AI Chatbot:**  
   JESTER does not feature open-ended conversational chatbots. The AI layer acts strictly as a deterministic voice resolver and stylistic translator governed by strict semantic contracts and context safety gates.
4. **NOT a Swipe-Card Game:**  
   Binary swiping commodifies humans and reduces complex people to split-second visual judgments. JESTER uses an intentional vertical discovery feed where content, voice, and compatibility context take precedence over rapid reflex actions.
5. **NOT a Diagnostic Assessment:**  
   JESTER never assigns psychological pathology, clinical personality types (MBTI, Enneagram), or numeric virtue grades. Human attributes are treated as descriptive preferences, not diagnostic verdicts.

---

## 3. Core Philosophy & Axioms

JESTER operates on three foundational axioms:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           THE JESTER AXIOM                              │
│                                                                         │
│           "They show the match. JESTER explains the connection."        │
│                                                                         │
│       Score creates curiosity.       Interpretation creates value.      │
│                      The insight becomes the invitation.                │
└─────────────────────────────────────────────────────────────────────────┘
```

- **"They show the match. JESTER explains the connection."**  
  Generic platforms inform users that a match occurred, leaving them with conversational paralysis. JESTER reveals *why* two people connect, what they will talk about, and where dynamic friction will arise.
- **"Score creates curiosity. Interpretation creates value."**  
  A numeric score catches attention, but substantive, witty human interpretation is what delivers lasting insight.
- **"The insight becomes the invitation."**  
  JESTER does not rely on artificial viral spam ("Invite 3 friends"). Growth occurs naturally when an insight is so funny, sharp, and accurate that a user screenshots it or sends it directly to someone:  
  *„ნახე, ჩემზე რას წერს JESTER 😂“* → *„შენც ნახე შენზე, მერე ჩვენი შედარება ვნახოთ.“*

---

## 4. Core User Journey: The Relational Loop

The product experience follows a sequential four-stage progression:

$$\mathbf{ME} \longrightarrow \mathbf{YOU} \longrightarrow \mathbf{US} \longrightarrow \mathbf{MORE\ PEOPLE}$$

1. **ME (Self-Understanding):**  
   *"What does JESTER notice about me?"*  
   The user enters foundational birth data and receives sharp, unvarnished observations about their social presence, emotional processing, communication style, and blind spots across 6 core personality placements (Sun, Moon, Ascendant, Mercury, Venus, Mars).
2. **YOU (Other-Understanding):**  
   *"What does JESTER notice about this person?"*  
   The user inspects another person's public profile, discovering their authentic voice, values, lifestyle cadence, and interests without violating privacy.
3. **US (Relationship Dynamics):**  
   *"What happens when we meet?"*  
   JESTER reveals interpersonal dynamics, communication synergy, intellectual sparks, and conversation starters between two specific people.
4. **MORE PEOPLE (Discovery):**  
   *"Who else is out there that I resonate with?"*  
   Armed with self-knowledge and relational context, the user explores an intentional discovery feed designed to inspire genuine curiosity rather than mindless consumption.

---

## 5. Product Principles

1. **Facts Before Interpretations; Interpretations Before Presentation:**  
   Astrological math and declared user truth are objective facts. Interpretation translates those facts into meaning. Presentation renders that meaning clearly. Never compromise the underlying deterministic math for visual convenience.
2. **Deterministic Intelligence:**  
   Two users with identical placements must always yield the exact same underlying astrological geometry and synastry sub-scores. No random numbers, no arbitrary drift.
3. **Intentionality Over Addiction:**  
   Every interaction should encourage thoughtful engagement and real-world connection, rejecting addictive dark patterns, infinite slot-machine swiping, and manufactured anxiety.
4. **Absolute Boundary Respect:**  
   A user’s private data belongs solely to that user. The platform never exposes private birth data, real-time locations, or private messages.

---

## 6. Role of Astrology

Astrology is JESTER’s **deterministic computational intelligence layer**, not its consumer brand.

- **Engine:** PySwissEph (`swe`) C-bindings compute high-precision celestial longitudes for 10 celestial bodies: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
- **House System:** Placidus houses and exact Ascendant are calculated when valid birth time and geographic coordinates exist.
- **Placidus Polar Contract:** Latitudes $> 66.5^\circ$ raise a Placidus polar error (HTTP 400). The system does not silently substitute an unapproved house system.
- **Timezone Precision:** Canonical IANA timezones via Python `zoneinfo` with exact Julian Day computation.
- **Unknown Birth Time is Valid:**  
  If a user does not know their birth time:
  - `birth_time` is stored as `NULL` in `public.birth_data`.
  - Ascendant and Houses remain `None`.
  - Sun, Moon, and planetary longitudes use a deterministic 12:00 UTC fallback.
  - Unknown birth time never blocks onboarding completion.
- **Invisible Delivery:**  
  Consumers receive psychological, communication, and relational insights. Astrological symbols, degree numbers, and technical jargon are completely filtered out of primary user surfaces.

---

## 7. Role of AI

JESTER uses AI strictly as a **stylistic translator and voice engine**, never as an autonomous decision-maker or open-ended chatbot.

- **No Open Chatbot:** JESTER has no conversational AI bot. Users chat only with other authenticated human beings.
- **Deterministic Signal Pipeline:**  
  The AI / Content layer consumes structured signals generated by the Synastry engine (e.g. `aspect: Venus opposition Mars, orb: 1.2°`) and maps them to registered semantic contracts.
- **Strict Context Safety Gate (`JesterAiContextV1`):**  
  Every payload sent to an LLM must pass an automated in-memory safety gate. Any detection of blacklisted fields immediately aborts generation:
  - `messages.body` (Private messages are NEVER mined or read by AI)
  - Exact `latitude` / `longitude`
  - Exact `birth_time`
  - Biometric verification data (`selfie_bytes`)
  - Report / Block records
  - Diagnostic / clinical labels
- **Zero Hallucination of Compatibility:**  
  AI models are architecturally barred from inventing astrological positions, calculating scores, or deciding whether two people are compatible.

---

## 8. Discovery Principles

Discovery connects people through intentional, multi-dimensional resonance rather than photo-swiping.

- **Anti-Swipe Mandate:** No binary left/right swiping. Discovery is an intentional, vertical feed of rich profile cards.
- **Hierarchy of Perception:** **People first, signals second, scores last.**  
  Profiles emphasize authentic human voice (prompts, bio, values, lifestyle) before presenting compatibility metrics.
- **6/3/1 Diversity Ratio:**  
  To prevent algorithmic echo chambers, discovery candidate feeds balance three streams:
  - **60% Intent Alignment:** Candidates sharing primary or secondary relationship intents.
  - **30% Complementary Synergy:** Candidates offering dynamic balance in communication, lifestyle, or synastry.
  - **10% Serendipity:** Unexpected, intriguing candidates outside strict similarity filters.
- **Soft Geographic Relevance:**  
  Location provides a soft relevance boost (same-city candidates appear earlier), but never acts as a rigid GPS geofence. Continuous background GPS tracking is strictly prohibited.
- **Discovery Gate:**  
  To appear as a candidate in Discovery, a user must have:
  1. Completed onboarding.
  2. At least 1 clear profile photo.
  3. `is_discoverable = true`.
- **Photo Verification:**  
  Unverified users appear normally. Verified users receive a subtle verification mark (`✓ Photo Verified`). Verification proves liveness at the moment of capture; it is not a moral "Trust Score".
- **Bilateral Intent Partitioning:**  
  Candidates with mutually exclusive intents (e.g. user seeking exclusive dating vs user seeking strictly professional/creative collaboration) are automatically partitioned to prevent mismatched expectations.

---

## 9. Relationship Intents

JESTER recognizes six canonical relationship intents:

| Canonical Key | Georgian Name | Description |
| :--- | :--- | :--- |
| `new_friends` | ახალი მეგობრები | Social connection, camaraderie, shared hangouts |
| `dating` | შეხვედრები / ურთიერთობა | Intentional dating and romantic exploration |
| `creative_collab` | შემოქმედებითი კოლაბორაცია | Artistic, entrepreneurial, or project collaboration |
| `activity_partner` | აქტივობის პარტნიორი | Sports, fitness, travel, and hobby companionship |
| `deep_talks` | საუბრები / აზრების გაზიარება | Intellectual dialogue, philosophy, deep conversations |
| `open_to_possibilities` | ღია შესაძლებლობებისთვის | Fluid, organic connection without predefined boxes |

### Intent Primacy Invariant
Declared intent governs interpretation tone. If either participant declares a non-romantic intent (such as `new_friends` or `creative_collab`), the system and JESTER voice strictly prohibit romantic or sexual framing of synastry signals (e.g., Venus-Mars aspects are framed as creative drive or mutual energy, never romantic destiny).

---

## 10. Onboarding Principles

Onboarding must feel calm, respectful, human, and progressive—never like an astrological clinic or government census.

- **Sequential 8-Step Blueprint:**
  1. **Basic Identity:** Real First Name + Last Name. Derives public `display_name` as `"First L."` (e.g., `"დავით გ."`). Last name is never shown publicly.
  2. **Birth Date:** Day, Month, Year. Enforces strict **18+ platform boundary**.
  3. **Birth Time:** 24-hour time selector with prominent **"ზუსტი დრო არ ვიცი" (Unknown Time)** toggle.
  4. **Birth Place:** Global city autocomplete search (canonical `cities` table) resolving coordinates and IANA timezone for natal calculations.
  5. **Where You Live:** Current residential city (social discovery base; decoupled from birth place).
  6. **Interests:** Selection from canonical interest graph (minimum 3 if selecting, up to 7; fully skippable).
  7. **Profile Photo:** Primary avatar upload (skippable during onboarding; required later to enter Discovery).
  8. **Finish:** Natal calculation presentation and the user's first personalized JESTER insight.
- **Deterministic Resume:**  
  `onboarding_step` is persisted to the database. Users can abandon the flow at any step and resume later exactly where they left off. Back navigation preserves all entered data without reset.

---

## 11. Authentication Boundary

JESTER strictly isolates authentication credentials from personal identity:

```text
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│       1. AUTHENTICATION              │       │         2. ONBOARDING                │
│    Route: /auth/register             │  ───► │    Route: /onboarding                │
│    • Email                           │       │    • Real Name & Display Name        │
│    • Password                        │       │    • Private Birth Data              │
│    • Confirm Password                │       │    • City, Interests, Photo          │
└──────────────────────────────────────┘       └──────────────────────────────────────┘
```

- **Credentials-Only Registration:**  
  `/auth/register` accepts only `email`, `password`, and `confirm_password`. First name, last name, birth data, and location are never requested on the registration form.
- **Supabase Auth Authority:**  
  Supabase Auth is the identity and session provider. FastAPI validates asymmetric JWKS tokens in production.
- **Abandonment Safety:**  
  If a user abandons registration before completing Onboarding Step 1, zero personal identity or birth data exists in application tables.

---

## 12. Privacy & Security Invariants

These invariants are immutable architectural rules:

1. **Birth Data Isolation:**  
   `public.birth_data` contains private date, time, timezone, latitude, longitude, and place data. It is restricted to the resource owner via database RLS (`user_id = auth.uid()`). It is never exposed in profile views, discovery cards, or API responses to other users.
2. **Server-Only Astrology:**  
   `public.astro_private` stores exact calculated longitudes, houses, and retrogrades. Client roles (`authenticated`, `anon`) have `REVOKE ALL` SQL permissions on this table. Clients receive only safe derived DTOs (`astro_safe_profile`).
3. **Canonical Connection Pairs:**  
   All connection and relationship records enforce `user_a_id < user_b_id` via a database check constraint, preventing duplicate or order-dependent states.
4. **Block Privacy:**  
   Blocked entities return privacy-safe HTTP 404 (Not Found) across all endpoints (profiles, safe astrology, compatibility, chat). The system never leaks an existence oracle.
5. **Anti-Surveillance Messaging:**  
   Private direct messaging between connected users contains zero read-receipt latency clocks, zero typing speed telemetry, and zero sentiment mining.
6. **Strict 18+ Platform Boundary:**  
   Users under 18 years of age are strictly barred from registration and onboarding.

---

## 13. Georgian-First Requirement

JESTER is built and deployed **Georgian-first (`locale: "ka"`)**. English (`en`) is secondary.

- **Native Voice:** JESTER’s signature witty, observant, and teasing copy is authored natively in Georgian, reflecting contemporary urban vernacular and cultural cadence. It is not a literal machine translation from English.
- **Script Nuances:** Mkhedruli script has no native uppercase/lowercase distinction. Visual hierarchy relies on font weight contrast (700/800 Bold) and generous vertical line spacing (minimum line-height 1.5–1.6) rather than capital-letter transformations.
- **Horizontal Expansion:** Georgian words are on average 20% to 35% longer than English equivalents. UI containers, buttons, and navigation elements must support generous horizontal breathing room.
