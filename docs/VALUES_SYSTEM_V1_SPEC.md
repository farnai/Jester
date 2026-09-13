# JESTER — Values System V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

---

## 1. Product Purpose & Philosophy

JESTER is a **People Discovery and Relationship Intelligence** platform. 

To help people understand themselves, discover compatible connections, and navigate relational dynamics, the platform systematically maps three foundational human dimensions:
> **Interests answer:** *"What are you into?"* (Topics, intellectual passions, creative crafts)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, activity pace, work environment, living reality)  
> **Values answer:** *"What matters to you?"* (Guiding principles, moral compass, and life priorities)

Values describe relatively stable principles, priorities, and life-direction preferences that guide decision-making, relationship boundaries, and personal fulfillment.

### Core Operating Axioms:
1. **Values Are NOT a Psychological Diagnosis:** JESTER strictly rejects turning values into clinical personality assessments. The system will **never** declare: *"You are 87% independent"* or *"Your personality is 73% ambitious"*. Values are human declarations of what matters to a person, not medical verdicts or psychological profiling.
2. **People First. Signals Second. Scores Last:** Values are deep contextual signals and conversation bridges, not clinical match scores.
3. **Schema Now, Collection Later:** The database schema and relational graph are designed broadly from day one to model values and their interactions. Onboarding, however, remains lightweight, respectful, and non-fatiguing.
4. **Zero Rating Sliders:** JESTER explicitly avoids Likert-scale rating sliders (*"Rate Honesty from 1 to 10"*). Rating sliders introduce high cognitive burden and inconsistent subjective calibration. Users simply choose 3 to 5 values that guide them most.
5. **No Moral Superiority or Virtuous Grading:** All canonical values in JESTER are treated with equal dignity and respect. The system never frames certain values as "morally superior" to others.

---

## 2. What Counts as a Value? (Domain Boundaries)

To prevent the common product failure of treating "Values" as an amorphous dumping ground, JESTER enforces strict domain boundaries:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         USER MODEL DOMAIN BOUNDARIES                             │
├───────────────────┬──────────────────────────────────────────────────────────────┤
│ 1. Identity       │ Who I am (Name, gender, age, birth date).                    │
│ 2. Location       │ Where I am based / where I am from (City, Country).          │
│ 3. Interests      │ What I am into (Photography, Cinema, Travel, Astrology).     │
│ 4. Lifestyle      │ How I live my everyday life (Rhythm, pace, work reality).    │
│ 5. Values         │ What principles and priorities matter to me (Autonomy, Honesty).│
│ 6. Social Behavior│ How my social battery functions (Introvert, Extrovert).      │
│ 7. Communication  │ How I communicate (Fast texter, deep conversation, banter).  │
│ 8. Intent         │ What I am seeking on JESTER right now (Dating, Friends).     │
│ 9. Prompts        │ How I express myself in open-ended words.                    │
└───────────────────┴──────────────────────────────────────────────────────────────┘
```

### Master Ambiguity Resolution Table:

| Concept / Candidate | Primary Domain | Decoupling Invariant & Justification |
| :--- | :--- | :--- |
| **Adventure** | `Values` | Defined as *Adventure & Exploration*: the life priority of seeking the unfamiliar over the routine. (Outdoor sports belong to `Interests`). |
| **Family** | `Values` | Prioritizing family bonds, kinship, and generational closeness above individual pursuits. (Having children is `Lifestyle / Household`). |
| **Ambition** | `Values` | Drive for mastery, impact, and excellence in one's pursuits. |
| **Stability** | `Values` | Prioritizing emotional, physical, and financial predictability and solid foundations over volatility. |
| **Autonomy / Freedom** | `Values` | Prioritizing self-reliance, sovereignty, and unconstrained decision-making. |
| **Curiosity** | `Values` | The fundamental drive to learn, question, and understand the world. (Specific subjects belong to `Interests`). |
| **Growth** | `Values` | Commitment to self-evolution, lifelong learning, and personal transformation. |
| **Playfulness / Levity** | `Values` | Prioritizing humor, laughter, and lightness through life's trials. (Everyday communication style is `Communication`). |
| **Kindness** | `Values` | Active goodwill, compassion, and generosity of spirit in human interaction. |
| **Honesty** | `Values` | Truthfulness, transparency, and ethical integrity. |
| **Creativity** | `Values` | Valuing original expression and imagination. (Specific creative crafts belong to `Interests`). |
| **Spirituality** | `Values` | Connection to the deeper mysteries, inner consciousness, and transcendence. (Astrology charts belong to `Interests` & `Astrology`). |
| **Religion** | `Identity / Culture` | Specific religious affiliation is an identity/cultural attribute; excluded from generic values taxonomy. |
| **Politics** | `Social Views` | Partisan alignment is an external belief; excluded from generic values taxonomy to prevent toxic polarization. |
| **Sustainability / Nature** | `Values` | Reverence for the living Earth and environmental stewardship. (Hiking/Camping belongs to `Interests`). |

---

## 3. Values Taxonomy V1 (18 Canonical Values)

The V1 taxonomy avoids abstract linguistic bloat. It provides a curated set of **18 Canonical Values** organized into 5 thematic clusters:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           JESTER VALUES TAXONOMY V1                              │
├──────────────────────────┬────────────────────────────┬──────────────────────────┤
│ 1. Personal Direction    │ 2. Intellectual & Creative │ 3. Relational & Ethical  │
├──────────────────────────┼────────────────────────────┼──────────────────────────┤
│ • Autonomy               │ • Curiosity                │ • Honesty                │
│ • Growth                 │ • Creativity               │ • Kindness               │
│ • Ambition               │ • Open-Mindedness          │ • Loyalty                │
│ • Stability              │ • Adventure                │ • Empathy                │
├──────────────────────────┴────────────────────────────┴──────────────────────────┤
│ 4. Life Grounding                                     │ 5. Inner Spirit          │
├───────────────────────────────────────────────────────┼──────────────────────────┤
│ • Family                 • Simplicity                 │ • Playfulness            │
│ • Community              • Authenticity               │ • Spirituality           │
└───────────────────────────────────────────────────────┴──────────────────────────┘
```

### Definitions & Canonical Slugs:

1. **Autonomy** (`autonomy`): Valuing self-reliance, independence, and the freedom to chart one's own course.
2. **Growth** (`growth`): Committing to lifelong personal evolution, self-awareness, and expanding capabilities.
3. **Ambition** (`ambition`): Striving for excellence, meaningful impact, and achieving significant milestones.
4. **Stability** (`stability`): Valuing steady foundations, emotional reliability, and enduring security.
5. **Curiosity** (`curiosity`): An insatiable hunger to ask questions, explore ideas, and understand how things work.
6. **Creativity** (`creativity`): Valuing original imagination, aesthetic vision, and bringing new ideas into being.
7. **Open-Mindedness** (`open_mindedness`): Embracing diverse perspectives, intellectual humility, and challenging preconceptions.
8. **Adventure** (`adventure`): Embracing the thrill of the unknown, spontaneity, and stepping outside comfort zones.
9. **Honesty** (`honesty`): Valuing uncompromised truthfulness, clarity, and transparent communication.
10. **Kindness** (`kindness`): Practicing active compassion, benevolence, and warmth toward others.
11. **Loyalty** (`loyalty`): Steadfast devotion, keeping promises, and standing by the people you care about.
12. **Empathy** (`empathy`): Deeply attuning to others' emotions, listening without judgment, and understanding shared humanity.
13. **Family** (`family`): Cherishing kinship bonds, generational heritage, and dedication to loved ones.
14. **Community** (`community`): Valuing collective belonging, mutual aid, and contributing to the greater social fabric.
15. **Simplicity** (`simplicity`): Valuing uncluttered living, mindfulness, and clarity over unnecessary complexity.
16. **Authenticity** (`authenticity`): Living in strict alignment with one's true nature rather than conforming to external expectations.
17. **Playfulness** (`playfulness`): Navigating life with levity, humor, teasing warmth, and a refusal to take oneself too seriously.
18. **Spirituality** (`spirituality`): Honoring the inner life, existential wonder, and connection to something greater than oneself.

---

## 4. Value Selection UX: "What Guides You Most?"

### 4.1 Selection Rule: Choose 3 to 5 Values
- JESTER avoids overwhelming questionnaires.
- Users are presented with the curated 18-value grid.
- **Rule:** The user chooses **between 3 and 5 values**.
- The step is **100% skippable** during onboarding.

### 4.2 Optional Core Value Designation
After selecting 3–5 values, JESTER asks an optional follow-up question:
> *"If you had to pick one true north, which is it?"*
- The user may designate **1 Core Value** (`is_core = true`).
- The Core Value receives elevated prominence on the profile and in discovery cards.

```text
┌────────────────────────────────────────────────────────┐
│                   WHAT MATTERS TO YOU?                 │
│                                                        │
│   Select 3 to 5 values that guide your life.           │
│                                                        │
│   [ 🧭 Autonomy ]      [ 🌱 Growth ]       [ ⚡ Ambition ]   │
│   [ 🏛️ Stability ]     [ 🔍 Curiosity ]    [ 🎨 Creativity ] │
│   [ 🌐 Open-Minded ]   [ 🧗 Adventure ]    [ 💎 Honesty ]    │
│   [ 🤍 Kindness ]      [ 🛡️ Loyalty ]      [ 🫂 Empathy ]    │
│   [ 🏡 Family ]        [ 🤝 Community ]    [ 🌿 Simplicity ] │
│   [ 🪞 Authenticity ]  [ 🎈 Playfulness ]  [ ✨ Spirituality]│
│                                                        │
│   Selected: 4 / 5                                      │
│                                                        │
│   [  Skip for now  ]                     [  Continue ] │
└────────────────────────────────────────────────────────┘
```

---

## 5. Public Profile Presentation: Guiding Compass

On the public profile, values appear in a dedicated, elegant section titled **"Values"** or **"Guiding Compass"**:

```text
               ┌─────────────────────────────────────────────────┐
               │           PUBLIC PROFILE PRESENTATION           │
               ├─────────────────────────────────────────────────┤
               │  Alexandre, 28                                  │
               │  📍 Based in Tbilisi · 🏡 From Kvareli          │
               │                                                 │
               │  GUIDING COMPASS                                │
               │  ⭐ Curiosity (Core)                             │
               │  [ Growth ]  [ Honesty ]  [ Autonomy ]          │
               └─────────────────────────────────────────────────┘
```

### Visual & Privacy Rules:
1. **Core Value Elevation:** If designated, the Core Value is visually anchored with a star or highlight badge.
2. **Clean Pill Layout:** Remaining values render as refined, glassmorphic chips.
3. **User-Controlled Visibility:** In profile settings, the user can toggle the entire Values section visible or hidden.
4. **No Cluttered Diagnostics:** Never display diagnostic graphs, percentages, or personality scores.

---

## 6. Values in Discovery & Relationship Intelligence

Values provide deep **philosophical resonance and relational compatibility signals**:

$$\text{Discovery Relevance} = f(\text{Human Profile}, \text{Interest Graph}, \text{Intent}, \text{Lifestyle}, \mathbf{Values}, \text{Location}, \text{Astrology Synergy})$$

### 6.1 Shared Values (Direct Resonance)
When two users share core values, JESTER surfaces this as an immediate philosophical hook:
- **Shared Curiosity & Growth:** *"Both guided by Curiosity and Growth — endless shared rabbit holes."*
- **Shared Autonomy & Honesty:** *"Both value independence and clear truth. Zero games, total respect."*

### 6.2 Complementary Values (Dynamic Balance)
When users select differing but complementary values, JESTER highlights the constructive balance with signature wit:
- **Autonomy + Loyalty:** *"One brings fierce independence, one brings steadfast loyalty. Space to breathe with a secure tether."*
- **Adventure + Stability:** *"One brings the compass, one brings the anchor. Excitement grounded in reality."*
- **Ambition + Simplicity:** *"One reaches for the stars, one cherishes the quiet moments. Grounded drive."*

### 6.3 Soft Signals, Never Exclusionary Filters in V1
- In V1, values are **never used as hard exclusionary dealbreakers**.
- Differences in values are framed as fascinating relational dynamics to understand and navigate, not automatic disqualifiers.

---

## 7. JESTER AI Context & Ethical Invariants

The JESTER AI engine receives structured values tokens:

```json
{
  "viewer": {
    "core_value": "curiosity",
    "values": ["curiosity", "growth", "autonomy", "honesty"]
  },
  "target": {
    "core_value": "loyalty",
    "values": ["loyalty", "stability", "kindness", "growth"]
  },
  "values_dynamic": {
    "shared_values": ["growth"],
    "polarity_pair": ["autonomy", "loyalty"],
    "relationship_theme": "independent_loyalty"
  }
}
```

### Critical AI Behavioral Invariants:
1. **Never Diagnose Personality:** JESTER AI must **never** tell a user: *"Because you value honesty, your personality is rigid"* or *"You are 80% an intellectual"*. Values are priorities, not psychological labels.
2. **No Moralizing or Virtuous Grading:** The AI must **never** imply that one value is "better" or "more evolved" than another (e.g., never say *"You should value family more than autonomy"*).
3. **Conversational Anchoring ("The Insight Becomes the Invitation"):** Shared values serve as natural prompts for meaningful dialogue (e.g. *"You both value authenticity above pleasing the room — small talk won't last long here"*).

---

## 8. Database Schema Specification (Architecture Blueprint)

```sql
-- ============================================================================
-- 1. CANONICAL VALUES THEMATIC CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.values_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'personal_direction', 'relational_ethical'
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL VALUES OPTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.values_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.values_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'curiosity', 'growth', 'autonomy'
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    definition_en TEXT NOT NULL,
    definition_ka TEXT NOT NULL,
    badge_icon VARCHAR(30),                    -- 'compass', 'seedling', 'star'
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. USER VALUES JUNCTION TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    value_id UUID NOT NULL REFERENCES public.values_options(id) ON DELETE RESTRICT,
    is_core BOOLEAN NOT NULL DEFAULT false,
    sort_order INTEGER DEFAULT 1,
    source VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding', 'profile_edit')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_value UNIQUE (user_id, value_id)
);

CREATE INDEX IF NOT EXISTS idx_user_values_user ON public.user_values(user_id);
CREATE INDEX IF NOT EXISTS idx_user_values_value ON public.user_values(value_id);

-- ============================================================================
-- 4. VALUE RELATIONS GRAPH (Synergies & Polarities)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.value_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    value_a_id UUID NOT NULL REFERENCES public.values_options(id) ON DELETE CASCADE,
    value_b_id UUID NOT NULL REFERENCES public.values_options(id) ON DELETE CASCADE,
    relation_type VARCHAR(30) NOT NULL CHECK (relation_type IN ('synergy', 'complementary_balance', 'polarity')),
    dynamic_label_en VARCHAR(100) NOT NULL,    -- e.g. 'Anchor and Sail'
    dynamic_label_ka VARCHAR(100) NOT NULL,    -- e.g. 'ღუზა და იალქანი'
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_value_relation UNIQUE (value_a_id, value_b_id),
    CONSTRAINT check_no_self_value_relation CHECK (value_a_id != value_b_id)
);
```

---

## 9. API Specification & Safe DTOs

### 9.1 Safe Public Profile Serialization
Public profile and discovery card payloads include a clean, non-sensitive values list:

```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Alexandre",
  "values": [
    {
      "slug": "curiosity",
      "name": "Curiosity",
      "is_core": true,
      "badge_icon": "compass"
    },
    {
      "slug": "growth",
      "name": "Growth",
      "is_core": false,
      "badge_icon": "seedling"
    },
    {
      "slug": "autonomy",
      "name": "Autonomy",
      "is_core": false,
      "badge_icon": "shield"
    },
    {
      "slug": "honesty",
      "name": "Honesty",
      "is_core": false,
      "badge_icon": "diamond"
    }
  ]
}
```

---

## 10. Scope Boundary: V1 vs. Future Roadmap

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **18 Canonical Values V1** | ✅ | — | Curated, unambiguous foundational set |
| **Select 3 to 5 Values** | ✅ | — | Lightweight, cognitive-load-friendly |
| **Optional 1 Core Value** | ✅ | — | Surfaces user's single primary true north |
| **Shared & Complementary Hooks** | ✅ | — | Rich AI interpretations of shared/polar values |
| **Profile Values Micro-Badges** | ✅ | — | Refined visual hierarchy on social profile |
| **Hard Values Dealbreaker Filters**| ❌ | 🔮 | Requires high density; prevents artificial silos |
| **Values-Based Story Prompts** | ❌ | 🔮 | Future deep-dive content expansion |
| **Behavioral Value Inference** | ❌ | 🚫 | Privacy risk; values must remain explicitly declared |

---

## 11. Values System V1 — Final Decisions Summary

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Product Purpose** | Answers *"What matters to you?"* — guiding principles and life priorities. |
| **Anti-Diagnosis Invariant**| Strictly prohibited from acting as a psychological diagnosis or percentage personality test. |
| **Canonical Taxonomy** | 18 curated canonical values across 5 clusters (`Personal Direction`, `Intellectual`, `Relational`, `Grounding`, `Spirit`). |
| **Selection Model** | Choose 3 to 5 values. No 1–10 rating sliders. 100% skippable during onboarding. |
| **Core Value** | Optional designation of 1 Core Value ("True North") with elevated visual prominence. |
| **Profile UI Pattern** | "Guiding Compass" micro-badges with starred Core Value; clean and non-clinical. |
| **Discovery Role** | Philosophical synergy and complementary polarity observations. Soft relevance signal; no hard dealbreakers in V1. |
| **Database Model** | Normalized tables: `values_categories`, `values_options`, `user_values`, `value_relations`. |
| **API Contract** | Enriched `ProfileResponse` with clean `values: list[ValueDTO]`. Dedicated `/v1/values/*` management endpoints. |
| **AI Context** | Ingests shared values and polarities for conversational depth; strictly barred from moralizing or pseudo-diagnosing. |
| **Security Policy** | Standard RLS: users manage own values; all 18 options are public; no virtue grading or existence leaks. |
| **V1 Scope** | 18 values, 3–5 selection, 1 core value, shared/complementary resonance, AI conversational hooks. |
| **Future Scope** | Deep-dive value stories, values-based discovery filtering, advanced relationship polarities. |
