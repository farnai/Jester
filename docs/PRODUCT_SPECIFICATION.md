# JESTER V1 — Product Capability Specification

**Document Type:** Product Capability Specification  
**Version:** V1.0  
**Purpose:** Define the functional capabilities of JESTER V1 before UI/UX and implementation decisions.

---

# 1. Product Definition & Strategic Positioning

**JESTER** is a **People Discovery and Relationship Intelligence** platform.

It uses high-precision astronomical calculations (Swiss Ephemeris) as its deterministic underlying intelligence layer, but **is not positioned as an astrology, horoscope, or dating app**. The consumer product is about **people, interpersonal curiosity, and connection dynamics**:

> **"They show the match. JESTER explains the connection."**

Traditional astrology apps ask: *"Who are you?"*  
JESTER asks: *"Why do you connect?"*

### 1.1 Core Experience Model: ME → YOU → US → MORE PEOPLE

The user experience follows a sequential psychological expansion:

```text
ME → YOU → US → MORE PEOPLE
```

1. **ME (Understand Myself)**: User enters birth data and gets their first personal taste of JESTER (*"Let's see what JESTER notices about me"*).
2. **YOU (Curiosity About Another)**: Curiosity naturally extends outward (*"What would JESTER say about my friend?"*).
3. **US (Relationship Intelligence)**: Comparing two profiles to unpack the connection (*"What does JESTER say about us?"*).
4. **MORE PEOPLE (Network & Discovery)**: Discovering new people, friends, collaborators, and relationship dynamics (*"Who else should I check?"*).

### 1.2 The "Day Vibe / Today's Energy" Experience

"Today's Energy" (Day Vibe) is the user's primary daily habit hook and their **first taste of JESTER**.

**Underlying Pipeline:**
```text
Natal Placements + Current Sky Transits
       ↓ (Deterministic Calculations)
Astrological Signals
       ↓ (Core Meaning Extraction)
Interpersonal / Psychological Meaning
       ↓ (JESTER Voice Engine)
Short Personalized Daily Insight (1–2 sentences)
```

The user never needs to understand astrological terminology. The output is:
- Extremely short (1–2 sentences)
- Immediately understandable
- Personal, sharp, playful, and slightly sarcastic
- Emotionally recognizable and shareable

### 1.3 Core Viral Mechanic: The Insight Becomes the Invitation

JESTER does not rely on artificial referral prompts (*"Invite 3 friends"*). Instead:
> **THE INSIGHT BECOMES THE INVITATION.**

When an insight is perceptive, witty, and humorous, the user naturally screenshots it or texts a friend:
> *"ნახე, ჩემზე რას წერს JESTER 😂"* → *"შენც ნახე შენზე, მერე ჩვენი შედარება ვნახოთ."*

### 1.4 Product Capability vs. Product Experience

- **Backend / Data Layer (Product Capability)**: High-precision astronomical positions, house cusps, angular aspect geometries, and multi-dimensional matrices.
- **Consumer Interface (Product Experience)**: Clean, witty, human-readable JESTER observations, relationship dynamics, conversation starters, and connection insights.

---

JESTER V1 functional capabilities are composed of five major capability domains:

```text
JESTER V1
│
├── 1. Identity & Profile
├── 2. Personal Astrology
├── 3. People & Relationships
├── 4. Communication
└── 5. JESTER Intelligence
```

---

# 2. Identity & Profile

## 2.1 Account Identity

JESTER must be able to identify an authenticated user.

### Capabilities

* Create authenticated identity through Supabase Auth.
* Maintain unique user identity.
* Retrieve current authenticated user.
* Delete account.
* Cascade-delete associated application data.

### User identity contains

* User ID
* Email
* Authentication role
* Application metadata

Authentication itself remains delegated to Supabase Auth.

---

# 3. Personal Profile

Every user has a social profile separate from their authentication identity.

## 3.1 Profile Information

A user may maintain:

* Display name
* Avatar
* Bio
* City
* Occupation
* Timezone
* Discoverability status

## 3.2 Privacy

Users must be able to control whether their profile is discoverable.

A non-discoverable profile must not be exposed through normal person/profile access.

Blocked users must not be able to access protected profile information.

---

# 4. Birth Data & Astrological Identity

The user's astrological identity is generated from birth information.

## 4.1 Required Birth Information

JESTER supports:

* Birth date
* Birth time
* Birth time precision
* Birth timezone

Optional:

* Latitude
* Longitude
* Birth-place label

## 4.2 Birth Time Precision

The system distinguishes:

```text
EXACT
APPROXIMATE
UNKNOWN
```

Unknown birth time is a valid state.

When birth time is unknown:

* planetary positions are still calculated;
* Ascendant is unavailable;
* Houses are unavailable;
* the system must not present Ascendant/House-based information as precise.

---

# 5. Personal Astrology

JESTER V1 provides a personal astrological profile based on the natal chart.

## 5.1 Natal Planetary Placements

V1 supports:

* Sun
* Moon
* Mercury
* Venus
* Mars
* Jupiter
* Saturn
* Uranus
* Neptune
* Pluto

Each planetary placement contains a calculated longitude and corresponding zodiac sign.

## 5.2 Retrograde Status

The system determines whether each supported planet is retrograde.

## 5.3 Ascendant

When sufficiently precise birth time and valid coordinates are available:

* Ascendant is calculated;
* Ascendant zodiac sign is derived.

When birth time is unknown:

* Ascendant is unavailable.

## 5.4 Houses

JESTER V1 supports Placidus house calculation when valid birth-time and geographic information are available.

The system calculates:

* 12 house cusps.

House-based interpretation must not be generated when house calculation is unavailable.

---

# 6. Core Astrological Profile

JESTER derives simplified high-level characteristics from natal placements.

## 6.1 Sun Sign

Derived from Sun longitude.

## 6.2 Moon Sign

Derived from Moon longitude.

## 6.3 Ascendant Sign

Derived when Ascendant is available.

## 6.4 Dominant Element

The system calculates a primary element using weighted:

* Sun
* Moon
* Ascendant
* Mercury
* Venus
* Mars

Elements:

* Fire
* Earth
* Air
* Water

## 6.5 Dominant Modality

The system calculates a primary modality using the same weighted core placements.

Modalities:

* Cardinal
* Fixed
* Mutable

---

# 7. Astrological Data Boundaries

JESTER must distinguish between:

### Private astronomical data

Raw calculated information such as:

* exact planetary longitudes;
* Ascendant longitude;
* house cusps;
* retrograde state.

This data is protected server-side.

### Safe derived information

Information suitable for application-level exposure:

* Sun sign;
* Moon sign;
* Ascendant sign;
* dominant element;
* dominant modality.

This separation is part of JESTER's privacy model.

---

# 8. People

JESTER allows users to interact with other discoverable users.

## 8.1 Person Discovery

A user may access another person's public/discoverable profile.

Access must respect:

* discoverability;
* blocking;
* authorization.

## 8.2 Person Astrological Profile

When permitted, a user may access another person's safe astrological information.

This includes:

* Sun sign;
* Moon sign;
* Ascendant sign when available;
* dominant element;
* dominant modality.

Private raw astronomical coordinates must never be exposed through normal client access.

---

# 9. Connections

JESTER provides a relationship layer between users.

## 9.1 Connection Lifecycle

Supported states:

```text
pending
accepted
declined
blocked
removed
```

## 9.2 Connection Actions

Users may:

* send connection request;
* accept request;
* decline request;
* block user;
* unblock user;
* remove connection.

## 9.3 Compatibility Requirement

A compatibility comparison between two users requires an active accepted connection.

This creates an intentional relationship boundary:

```text
Person
  ↓
Connection
  ↓
Accepted relationship
  ↓
Compatibility
  ↓
Conversation
```

---

# 10. Blocking & Privacy

Blocking is a first-class product capability.

When User A blocks User B:

* B cannot access A's protected profile;
* B cannot access A's safe astrology;
* compatibility access is suppressed;
* messaging access is suppressed;
* the relationship becomes blocked;
* unblocking does not automatically restore the previous accepted relationship.

Privacy-safe behavior should avoid revealing whether a protected resource exists.

---

# 11. Compatibility / Synastry

Compatibility is a core JESTER capability.

The purpose of compatibility is not merely to output a numerical score.

The system must ultimately answer:

> **Why do these two people work, clash, attract, challenge, or complement each other?**

The compatibility system consists of:

```text
Person A
   +
Person B
   ↓
Natal Data
   ↓
Synastry Analysis
   ↓
Compatibility Dimensions
   ↓
Overall Score
   ↓
Signals
   ↓
Topics
   ↓
Conversation Starters
```

---

# 12. Synastry Inputs

Compatibility analysis should use the natal data of both users.

The V1 engine should be capable of evaluating:

### Core planets

* Sun
* Moon
* Mercury
* Venus
* Mars
* Jupiter
* Saturn
* Uranus
* Neptune
* Pluto

### Additional contextual factors

* Ascendant when available;
* dominant element;
* dominant modality.

---

# 13. Planetary Cross-Aspects

V1 compatibility analysis should identify significant angular relationships between Person A and Person B.

Initial supported aspect types:

```text
0°    Conjunction
60°   Sextile
90°   Square
120°  Trine
180°  Opposition
```

The engine must calculate angular distance between planetary placements and determine whether the relationship falls within the applicable orb.

---

# 14. Orb & Aspect Strength

Not every aspect has equal significance.

The engine must evaluate:

* exact angular distance;
* maximum allowed orb;
* deviation from exact aspect;
* aspect strength.

Closer aspects should generally produce stronger signals than weaker/out-of-orb relationships.

Orb rules must be deterministic and versioned.

---

# 15. Planet-Pair Importance

Different planetary interactions represent different relationship domains.

V1 should therefore use weighted planet-pair importance.

Examples of conceptual domains:

```text
Sun       → identity / self-expression
Moon      → emotional connection
Mercury   → communication / thinking
Venus     → affection / attraction / values
Mars      → drive / chemistry / conflict
Jupiter   → growth / optimism
Saturn    → structure / responsibility
Uranus    → independence / disruption
Neptune   → idealization / imagination
Pluto     → intensity / transformation
```

These meanings are inputs into the scoring and signal-generation model, not merely descriptive labels.

---

# 16. Element Compatibility

V1 evaluates elemental interaction between the two users.

Elements:

```text
Fire
Earth
Air
Water
```

The system evaluates whether dominant elements create:

* complementary interaction;
* neutral interaction;
* challenging interaction.

Element compatibility contributes to the broader compatibility model.

---

# 17. Modality Compatibility

V1 evaluates modality interaction.

Modalities:

```text
Cardinal
Fixed
Mutable
```

The system evaluates the relationship between the users' dominant modalities.

Modality interaction contributes to compatibility interpretation.

---

# 18. Compatibility Dimensions

The overall compatibility result should not be represented by a single number alone.

V1 should produce four internal dimensions.

The exact final naming and weighting must be frozen in the Synastry V1 mathematical specification, but the model should cover relationship-relevant areas such as:

1. Emotional Harmony
2. Communication
3. Attraction / Chemistry
4. Growth / Long-Term Dynamics

These dimensions contribute to the overall compatibility score.

---

# 19. Overall Compatibility Score

The system produces a normalized:

```text
10.0 – 98.0
```

compatibility score.

### Core Strategic Principle:
> **SCORE CREATES CURIOSITY. INTERPRETATION CREATES VALUE.**

A score (e.g. `87%`) acts as the initial spark that makes the user ask: *"Why?"*  
The actual value and retention come from the multi-dimensional breakdown, dynamic tension points, and conversation starters.

The score is:

* **100% deterministic**;
* **reproducible**;
* **derived from the underlying astronomical cross-chart aspects**;
* **versioned (`synastry-v1.0.0`)**;
* **independent of presentation language**.

The score is calculated by the production-ready Synastry V1 Engine (`backend/app/compatibility/synastry.py`), replacing the former hardcoded baseline (`82.5`).


---

# 20. Compatibility Signals

Compatibility analysis should extract meaningful relationship signals.

Examples of signal concepts:

* independence;
* emotional ease;
* strong attraction;
* communication flow;
* different perspectives;
* curiosity;
* intensity;
* stability;
* growth;
* friction;
* complementary strengths.

Signals should be generated from actual astrological relationships rather than static arrays.

Each signal should have a strength level such as:

```text
low
medium
high
```

---

# 21. Compatibility Topics

The system should derive topics that are likely to create productive interaction between two people.

Examples:

* travel;
* books;
* creative work;
* ideas;
* ambition;
* relationships;
* learning;
* lifestyle;
* adventure.

Topics must ultimately be generated from compatibility signals rather than permanently hardcoded for every pair.

---

# 22. Conversation Starters

Compatibility can generate conversation starters based on detected relationship patterns.

Examples of output concepts:

* questions about travel;
* questions about interests;
* questions about ideas;
* questions about experiences;
* questions related to shared strengths.

Conversation starters are a downstream interpretation of compatibility data.

They must not affect the numerical compatibility score.

---

# 23. Compatibility Result Persistence

Compatibility results should be cacheable.

A result is associated with:

* canonical user pair;
* birth-data version of User A;
* birth-data version of User B;
* engine version;
* calculation timestamp;
* compatibility output.

If either user's birth data changes:

```text
Birth Data Version Changes
        ↓
Cached Compatibility Becomes Stale
        ↓
Recalculate
        ↓
Store New Result
```

---

# 24. Daily Astrology

JESTER V1 includes a daily astrological capability.

The purpose is to provide personalized daily information derived from the user's astrological context.

The current static implementation is only a placeholder.

A production V1 implementation should eventually derive daily information from actual astronomical/transit calculations.

Daily output should be associated with:

* user;
* date;
* engine version;
* generated content/data.

---

# 25. JESTER Intelligence

JESTER includes an AI interpretation layer.

The AI layer is responsible for translating structured astrological information into natural-language JESTER interpretations.

Architecture:

```text
Astrological Data
       ↓
Structured Signals
       ↓
Interpretation Context
       ↓
JESTER AI
       ↓
Natural Language
```

The AI should interpret data.

It should not replace the deterministic calculation engine.

---

# 26. Deterministic vs AI Responsibilities

This boundary is fundamental.

### Deterministic engine

Responsible for:

* astronomical calculations;
* planetary positions;
* signs;
* houses;
* aspects;
* orbs;
* scoring;
* compatibility dimensions;
* signal extraction;
* data validity.

### AI layer

Responsible for:

* explanation;
* narrative;
* contextualization;
* conversational language;
* JESTER personality;
* natural-language interpretation.

The AI must not invent underlying astronomical facts.

---

# 27. Messaging

JESTER supports direct communication between connected users.

## Capabilities

* create/retrieve direct conversation;
* send message;
* retrieve messages;
* persist messages;
* receive realtime message updates.

Messaging requires an active accepted connection.

---

# 28. Notifications

JESTER supports application-level notifications.

Initial notification categories:

* connection request;
* connection accepted;
* daily energy;
* system.

Users can:

* list notifications;
* mark notifications as read.

Database realtime notification infrastructure exists.

Native mobile push delivery is outside the current backend capability.

---

# 29. Realtime

JESTER supports realtime updates for:

* messages;
* notifications.

Realtime infrastructure is provided through Supabase Realtime.

---

# 30. Capability Boundaries for V1

The following are explicitly **not part of the current implemented capability set** and must not be treated as already available:

### Astrology (Missing / Deferred)

* Chiron;
* Lilith;
* North Node;
* South Node;
* Ceres;
* Pallas;
* Juno;
* Vesta;
* Part of Fortune;
* Arabic Parts;
* Alternative house system fallbacks (Equal, Whole Sign).

*(Note: 10 core planets Sun..Pluto, Placidus houses, Ascendant, and angular aspects Conjunction, Sextile, Square, Trine, Opposition ARE implemented).*

### Compatibility / Synastry Status
* **IMPLEMENTED**: Real deterministic Synastry V1 engine (`synastry-v1.0.0`) in `backend/app/compatibility/synastry.py` with 4-dimensional scoring, quadratic orb decay, planet-pair weighting, element/modality matrices, signals, topics, and starters.


### AI

* OpenAI API integration;
* JESTER interpretation engine;
* prompt pipeline;
* AI-generated astrological explanations.

### Daily

* actual transit calculations;
* personalized transit engine;
* dynamic daily interpretation.

### Communication

* message pagination;
* group conversations;
* native push notifications.

---

# 31. V1 Capability Priority

Capabilities are grouped by importance to the core JESTER value proposition.

## Tier 1 — Core

These define the essential JESTER experience:

1. User identity
2. Profile
3. Birth data
4. Natal astrology
5. People
6. Connections
7. Real Synastry
8. Compatibility score
9. Compatibility signals
10. Direct messaging

## Tier 2 — Core Enhancement

11. Compatibility topics
12. Conversation starters
13. Daily astrology
14. JESTER AI interpretation
15. Notifications
16. Realtime interaction

## Tier 3 — Expansion

17. Extended celestial bodies
18. Advanced astrological points
19. Group conversations
20. Push notifications
21. Advanced daily transits

---

# 32. V1 Functional Relationship

The central JESTER loop is:

```text
CREATE SELF
    ↓
UNDERSTAND SELF
    ↓
DISCOVER PEOPLE
    ↓
CONNECT
    ↓
COMPARE
    ↓
UNDERSTAND THE RELATIONSHIP
    ↓
START A CONVERSATION
    ↓
BUILD THE RELATIONSHIP
```

This loop represents the primary functional architecture of JESTER V1.

---

# 33. Product Principle

JESTER should not treat astrology as a static profile-card system.

The fundamental product unit is:

```text
Person × Person × Astrological Relationship
```

Therefore, the deepest capability of JESTER is not simply:

> "What are you?"

but:

> "What happens when you and another person interact?"

The natal chart establishes the individual foundation.

Synastry explains the relationship.

JESTER AI translates that relationship into understandable human language.

Social and messaging capabilities turn that understanding into interaction.

---

# 34. Current Implementation Status

The backend infrastructure and mathematical foundations for the core capability model are in place.

Current state:

```text
Authentication       ██████████  Implemented
Profiles             ██████████  Implemented
Natal Astrology      ██████████  Implemented
Aspect Engine        ██████████  Implemented
Synastry V1          ██████████  Implemented
Social Graph         ██████████  Implemented
Messaging            ██████████  Implemented
Notifications        █████████░  Implemented
Daily Transits       ██░░░░░░░░  Stub
JESTER AI Voice      █░░░░░░░░░  Stub
```

The mathematical specification for Synastry was completed and implemented as **Synastry V1 (`synastry-v1.0.0`)**, documented authoritatively in [`docs/SYNASTRY_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/SYNASTRY_V1_SPEC.md) and verified by 74 automated tests.

---

# 35. Next Technical Milestones

With Synastry V1 fully operational, the remaining development milestones are:

1. **Daily Transit & Day Vibe Engine**: Implement `backend/app/astrology/transits.py` to calculate real-time transit aspects against user natal placements and generate short, witty daily observations.
2. **JESTER Voice & Interpretation Pipeline**: Connect the structured signal output from Synastry V1 and Daily Transits to OpenAI API via `backend/app/interpretation/jester.py` using validated prompt templates.
3. **Frontend Consumer Transformation**: Translate the raw astronomical data exposure in the web app into the witty, human-first JESTER experience (`ME → YOU → US → MORE PEOPLE`).

