# JESTER — Social Behavior System V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

---

## 1. Product Purpose & Philosophy

JESTER is a **People Discovery and Relationship Intelligence** platform. 

To help people discover compatible connections and navigate relational dynamics, the platform systematically maps foundational human dimensions:
> **Interests answer:** *"What are you into?"* (Topics, intellectual passions, creative crafts)  
> **Location answers:** *"Where are you based and where are you from?"* (Current residency, regional heritage)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, activity pace, work environment, living reality)  
> **Values answer:** *"What matters to you?"* (Guiding principles, moral compass, and life priorities)  
> **Social Behavior answers:** *"How do you tend to be around people?"* (Interaction patterns, social battery, and setting comfort)

Social Behavior describes **how someone prefers to interact, gather, warm up, and recharge socially**.

### Core Operating Axioms:
1. **Describe Situations, Don't Define Identity:** Social Behavior answers: *"What kind of social situations and interaction patterns tend to work for you?"* It strictly does **NOT** answer: *"What kind of person are you?"*
2. **Strict Anti-Diagnostic Invariant:** JESTER does not assign psychological personality types, Myers-Briggs (MBTI) archetypes, or clinical classifications. It will never label people as *"Alpha"*, *"Beta"*, *"Loner"*, *"Social Butterfly"*, or *"Anxious Attacher"*.
3. **People First. Signals Second. Scores Last:** Social preferences serve as practical, empathetic friction-reducers and meeting-planner aids, never as exclusionary gates or clinical compatibility scores.
4. **Declared Reality > Behavioral Inference > Astrological Interpretation:** What a user directly states about their social comfort always overrides algorithmic guesses or astrological stereotypes.
5. **Progressive & Respectful Collection:** No 40-question psychometric inventory. Onboarding captures a rapid, voluntary 3-question "Social Rhythm Snapshot" that is 100% skippable.

---

## 2. Domain Boundaries: What Counts as Social Behavior?

To maintain clean data architecture and prevent cross-domain pollution, JESTER enforces strict boundaries:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         USER MODEL DOMAIN BOUNDARIES                             │
├───────────────────┬──────────────────────────────────────────────────────────────┤
│ 1. Identity       │ Who I am (Name, gender, age, birth date).                    │
│ 2. Location       │ Where I am based / where I am from (City, Country).          │
│ 3. Interests      │ What I am into (Photography, Cinema, Travel, Astrology).     │
│ 4. Lifestyle      │ How I live my everyday life (Rhythm, pace, work reality).    │
│ 5. Values         │ What principles and priorities matter to me (Autonomy, Truth).│
│ 6. Social Behavior│ How I tend to be around people (Group size, social battery). │
│ 7. Communication  │ How I communicate (Directness, banter vs depth, texting).    │
│ 8. Intent         │ What I am seeking on JESTER right now (Dating, Friends).     │
│ 9. Prompts        │ How I express myself in open-ended words.                    │
└───────────────────┴──────────────────────────────────────────────────────────────┘
```

### Master Decoupling Table:

| Candidate Concept | Primary Domain | Decoupling Invariant & Justification |
| :--- | :--- | :--- |
| **Prefers One-on-One vs Crowds** | `Social Behavior` | Preferred social gathering scale; NOT communication style. |
| **Needs Alone Time to Recharge** | `Social Behavior` | Social battery energy mechanics; NOT lifestyle cadence. |
| **Early Bird / Night Owl** | `Lifestyle` | Circadian biological rhythm; NOT social gathering preference. |
| **Remote Worker** | `Lifestyle` | Physical work reality; NOT how one behaves socially. |
| **Deep Talks vs Quick Banter** | `Communication` | Tone, depth, and medium of messaging/conversation; NOT gathering size. |
| **Fast Texter / Voice Notes** | `Communication` | Messaging channel latency and format; NOT social dynamics. |
| **Autonomy / Independence** | `Values` | Core guiding philosophical principle; NOT social group size. |
| **Adventure & Exploration** | `Values` | Life orientation toward the unknown; NOT party hosting. |
| **Hosting Dinner Parties** | `Social Behavior` | Preferred social gathering context / comfort zone. |
| **Social Cadence (Outing Frequency)**| `Lifestyle` | How many nights a week one leaves the house (operational schedule). |
| **Social Battery (Energy Dynamics)** | `Social Behavior` | How energy drains or refills during human interaction. |

---

## 3. The Introvert / Extrovert Investigation & Decision

The question of whether JESTER should collect *"Introvert / Extrovert / Ambivert"* is a foundational product decision.

### 3.1 The Flaws of Classical "Introvert / Extrovert" Labels:
1. **The Identity Trap (Boxing People In):** Labeling a user as an *"Introvert"* creates rigid self-fulfilling limitations (*"I'm an introvert, so I can't attend that"*). Labeling someone an *"Extrovert"* creates superficial stereotypes (*"Extroverts are loud, shallow, or always want attention"*).
2. **Context-Dependent Fluidity:** Human social energy is deeply contextual. An individual might be quiet and observant in a networking event of 50 strangers, yet passionately expressive for four hours in a 2-person coffee chat. A single static label erases this human nuance.
3. **Pop-Psychology Baggage:** Terms like Introvert/Extrovert trigger associations with clinical personality quizzes (Myers-Briggs / Big Five), violating JESTER’s anti-diagnostic axiom.

### 3.2 The JESTER Architectural Resolution: Functional Energy Mechanics
Rather than boxing the *person* into a psychological identity, JESTER models the **functional mechanics of their social battery**:

> **Instead of asking:** *"Are you an Introvert, Extrovert, or Ambivert?"*  
> **JESTER asks:** *"How does your social battery work?"*

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   FUNCTIONAL SOCIAL BATTERY RECHARGING                           │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 🔋 Recharges in Solitude  │ Loves people, but needs quiet downtime to refuel.   │
│ ⚡ Recharges Around People │ Draws vitality, focus, and buzz from shared presence.│
│ ⚖️ Context-Dependent       │ Fluid; depends heavily on the vibe, people, and mood.│
└──────────────────────────────────────────────────────────────────────────────────┘
```

**Why this works:**
- Answers the practical relational question: *"If they get quiet or want to go home after 3 hours, why is that happening?"*
- Eliminates identity judgment and moral superiority.
- Accurately captures 100% of the useful signal without the psychological baggage.

---

## 4. Social Behavior Taxonomy V1 (5 Dimensions, 16 Options)

JESTER V1 establishes a pragmatic, human taxonomy organized into **5 actionable dimensions**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          JESTER SOCIAL BEHAVIOR TAXONOMY V1                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Gathering Scale (Group Size Preference)                                             │
│    • one_on_one           Prefers One-on-One      (Intimate, focused connections)      │
│    • small_groups         Prefers Small Groups    (Tight circle of 3 to 6 people)      │
│    • lively_crowds        Thrives in Crowds       (Festivals, vibrant parties, energy) │
│    • adaptable_scale      Any Gathering Scale     (Comfortable across all crowd sizes) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Social Battery (Recharge Dynamic)                                                   │
│    • recharge_solo        Recharges in Solitude   (Needs quiet downtime after people)  │
│    • recharge_social      Recharges with People   (Draws energy from shared presence)  │
│    • recharge_fluid       Context-Dependent       (Varies by connection and mood)      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Warm-Up Dynamic (Approach to New People)                                            │
│    • initiator            Quick to Initiate       (Breaks ice easily, introduces self) │
│    • observer_first       Observant First         (Reads the room, warms up gradually) │
│    • selective_deep       Selective & Intentional (Takes time, invests deeply once in) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Social Planning (Cadence & Spontaneity)                                             │
│    • spontaneous          Spontaneous Hangouts    ("Free in 20 minutes? Let's go")     │
│    • planned_advance      Planned in Advance      (Appreciates calendar notice & plan) │
│    • flexible_flow        Goes with the Flow      (Comfortable with either mode)       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Comfort Zone (Preferred Social Setting)                                             │
│    • cozy_intimate        Cozy & Domestic         (Home dinners, tea, quiet balcony)   │
│    • out_and_about        Out in the City         (Cafés, bustling bars, cultural spots)│
│    • active_outdoor       Active & Outdoors       (Walks, parks, open nature)          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Social Behavior UX: "What Works for You Socially?"

### 5.1 Onboarding Snapshot (100% Skippable):
During or directly following profile creation, the user encounters a clean, single-screen **Social Rhythm Snapshot**:
- **3 Micro-Cards**:
  1. *Preferred Setting:* `[ ☕ One-on-One ]` `[ 👥 Small Groups ]` `[ 🎉 Lively Crowds ]` `[ 🌐 Adaptable ]`
  2. *Social Battery:* `[ 🔋 Recharges Solo ]` `[ ⚡ Recharges with People ]` `[ ⚖️ Context-Dependent ]`
  3. *Warm-Up Style:* `[ 🚀 Initiator ]` `[ 👀 Observant First ]` `[ 💎 Selective ]`
- **One-Tap Selection:** Single tap per question; instantly highlights and advances.
- **Zero Rating Sliders:** No 1–10 intensity scales.

```text
┌────────────────────────────────────────────────────────┐
│                   YOUR SOCIAL RHYTHM                   │
│                                                        │
│   How do you tend to be around people?                 │
│                                                        │
│   PREFERRED GATHERING                                  │
│   [ ☕ One-on-One ]  [ 👥 Small Groups ]               │
│   [ 🎉 Lively Crowds ]  [ 🌐 Adaptable ]               │
│                                                        │
│   SOCIAL BATTERY                                       │
│   [ 🔋 Recharges Solo ]  [ ⚡ Recharges Around People ] │
│   [ ⚖️ Context-Dependent ]                             │
│                                                        │
│   APPROACH TO NEW PEOPLE                               │
│   [ 🚀 Quick to Initiate ]  [ 👀 Observant First ]     │
│   [ 💎 Selective & Intentional ]                       │
│                                                        │
│   [  Skip for now  ]                     [  Continue ] │
└────────────────────────────────────────────────────────┘
```

---

## 6. Public Profile Presentation: Social Rhythm

On public profiles, social behavior renders under an elegant **"Social Rhythm"** section:

```text
┌─────────────────────────────────────────────────┐
│ Alexandre, 28                                   │
│ 📍 Based in Tbilisi · 🏡 From Kvareli           │
│                                                 │
│ SOCIAL RHYTHM                                   │
│ [ ☕ One-on-One ]  [ 🔋 Recharges Solo ]        │
│ [ 👀 Observant First ]  [ ⚡ Spontaneous ]      │
└─────────────────────────────────────────────────┘
```

### Visual & Privacy Principles:
1. **Clean Micro-Badges:** Rendered as refined, glassmorphic chips with intuitive iconography.
2. **Individual Visibility Toggles:** Users can toggle individual attributes (or the entire Social Rhythm card) visible or hidden in settings.
3. **Restraint Over Clutter:** Undeclared attributes simply do not render (no *"Social Battery: Not specified"* noise).
4. **Zero Diagnostic Grading:** Never present clinical charts, radar diagrams, or psychometric labels.

---

## 7. Relationship Intelligence: Discovery Synergy & Dynamics

In Discovery matching, Social Behavior provides **practical friction-reducers and meeting-planner intelligence**, never hard exclusionary gates:

### 7.1 Symmetric Harmony (Shared Social Comfort)
When two users share gathering preferences or battery styles:
- **Mutual One-on-One:** *"Both thrive in one-on-one settings — quiet corner cafés over chaotic rooms."*
- **Mutual Solo Rechargers:** *"Both need quiet time to refuel after socializing. Zero guilt, zero misunderstandings."*
- **Mutual Spontaneous:** *"Both thrive on last-minute plans. 'Free in twenty minutes?' will work here."*

### 7.2 Complementary Balance (Dynamic Interplay)
When two users possess differing but complementary social dynamics:
- **Initiator + Observant:** *"One easily breaks the ice, one reads the room. Natural conversational rhythm without pressure."*
- **Recharge Solo + Recharge Social:** *"One brings energy from the room, one anchors in quiet downtime. Space to breathe with shared warmth."*
- **One-on-One + Small Groups:** *"Close enough to find easy common ground, flexible enough to expand the circle."*

### 7.3 Friction Prevention (Meeting Intelligence)
JESTER AI uses social behavior to suggest **ideal first interaction settings**:
- Avoids suggesting loud, crowded venues to two people who prefer one-on-one quiet spaces.
- Suggests clear planning notice when connecting with someone who selects `planned_advance`.

---

## 8. JESTER AI Context & Ethical Invariants

When the JESTER AI engine receives social behavior context tokens:

```json
{
  "viewer": {
    "group_preference": "one_on_one",
    "social_battery": "recharge_solo",
    "warmup_style": "observer_first",
    "planning_style": "spontaneous"
  },
  "target": {
    "group_preference": "one_on_one",
    "social_battery": "recharge_solo",
    "warmup_style": "initiator",
    "planning_style": "planned_advance"
  },
  "social_dynamics": {
    "gathering_harmony": "exact_match_one_on_one",
    "battery_synergy": "mutual_solo_recharge",
    "warmup_interplay": "initiator_and_observer",
    "ideal_meeting_type": "quiet_tea_or_walk"
  }
}
```

### Operational Invariants:
1. **Never Label or Psychologically Pigeonhole:** JESTER AI must **never** call a user *"antisocial"*, *"introverted recluse"*, *"attention-seeking extrovert"*, or *"socially awkward"*.
2. **Equal Dignity Across All Social Rhythms:** Needing alone time to recharge is treated with identical respect as drawing energy from a crowd. JESTER never treats extroversion as "better" or introversion as a "flaw to overcome."
3. **Constructive Meeting Advice ("The Insight Becomes the Invitation"):** Context is used to craft thoughtful, low-pressure invitations (e.g. *"Since you both prefer low-key one-on-one spots, skip the noisy bar and grab tea"*).

---

## 9. Database Schema Specification (Architecture Blueprint)

```sql
-- ============================================================================
-- 1. CANONICAL SOCIAL BEHAVIOR CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.social_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'gathering_scale', 'social_battery', 'warmup_style', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL SOCIAL BEHAVIOR OPTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.social_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.social_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'one_on_one', 'recharge_solo', 'initiator', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    definition_en TEXT NOT NULL,
    definition_ka TEXT NOT NULL,
    badge_icon VARCHAR(30),                    -- 'coffee', 'battery-charging', 'rocket', etc.
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. USER SOCIAL PREFERENCES TABLE (Normalized Profile Extension)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_social_preferences (
    user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    group_preference VARCHAR(40),              -- e.g. 'one_on_one', 'small_groups', 'lively_crowds', 'adaptable_scale'
    social_battery VARCHAR(40),                -- e.g. 'recharge_solo', 'recharge_social', 'recharge_fluid'
    warmup_style VARCHAR(40),                  -- e.g. 'initiator', 'observer_first', 'selective_deep'
    planning_style VARCHAR(40),                -- e.g. 'spontaneous', 'planned_advance', 'flexible_flow'
    comfort_zone VARCHAR(40),                  -- e.g. 'cozy_intimate', 'out_and_about', 'active_outdoor'
    visibility_flags JSONB NOT NULL DEFAULT '{
        "group_preference": true,
        "social_battery": true,
        "warmup_style": true,
        "planning_style": true,
        "comfort_zone": true
    }',
    source VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding_snapshot', 'profile_edit', 'inferred')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. SOCIAL RELATIONS GRAPH (Synergies & Dynamic Interplay)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.social_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    option_a_id UUID NOT NULL REFERENCES public.social_options(id) ON DELETE CASCADE,
    option_b_id UUID NOT NULL REFERENCES public.social_options(id) ON DELETE CASCADE,
    relation_type VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_harmony', 'complementary_balance', 'pacing_difference')),
    dynamic_label_en VARCHAR(120) NOT NULL,    -- e.g. 'Mutual Quiet Refueling', 'Initiator and Observer'
    dynamic_label_ka VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_social_relation UNIQUE (option_a_id, option_b_id),
    CONSTRAINT check_no_self_social_relation CHECK (option_a_id != option_b_id)
);
```

---

## 10. API Specification & Safe DTOs

### 10.1 Safe Public Profile Serialization
Public profile payloads serialize social preferences filtered strictly through the user's `visibility_flags`:

```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Alexandre",
  "social_behavior": {
    "group_preference": "one_on_one",
    "social_battery": "recharge_solo",
    "warmup_style": "observer_first",
    "planning_style": "spontaneous",
    "comfort_zone": "cozy_intimate"
  }
}
```

### 10.2 Planned Endpoints (53 to 58):
- `GET /v1/social-behavior/options` — List canonical categories and localized options.
- `GET /v1/social-behavior/onboarding-snapshot` — Fetch the 3 onboarding questions with chips.
- `POST /v1/social-behavior/onboarding` — Submit onboarding snapshot (optional/skippable).
- `GET /v1/social-behavior/me` — Retrieve own declared social preferences and visibility flags.
- `PATCH /v1/social-behavior/me` — Update social preferences and visibility flags.
- `GET /v1/social-behavior/people/{target_user_id}` — Get discoverable target's public social preferences.

---

## 11. Scope Boundary: V1 vs. Future Roadmap

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **5 Dimensions / 16 Options** | ✅ | — | Curated, actionable, non-clinical taxonomy |
| **Functional Social Battery** | ✅ | — | Solves Introvert/Extrovert without boxing people in |
| **3-Question Onboarding Snapshot**| ✅ | — | Fast, single-tap, 100% skippable |
| **Social Rhythm Profile Badges** | ✅ | — | Micro-badges under dedicated profile section |
| **Meeting Setting Recommendations**| ✅ | — | AI suggests low-friction venues based on comfort zones |
| **Hard Social Dealbreaker Filters**| ❌ | 🔮 | Premature; social behavior is fluid and contextual |
| **Social Calendar Integration** | ❌ | 🔮 | Deep integration deferred to future sync features |
| **Automated Behavioral Profiling** | ❌ | 🚫 | Privacy & ethical violation; preferences must remain declared |

---

## 12. Final Architecture Decisions Table

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Product Purpose** | Answers *"How do you tend to be around people?"* — gathering scale, battery mechanics, warm-up style. |
| **Introvert / Extrovert Decision** | Replaced rigid identity labels with **functional social battery mechanics** (`recharge_solo`, `recharge_social`, `recharge_fluid`). |
| **Anti-Diagnostic Invariant**| Strictly forbidden from assigning personality types, MBTI codes, or psychometric labels. |
| **Canonical Taxonomy** | 5 dimensions, 16 options: Gathering Scale, Social Battery, Warm-Up Dynamic, Planning Style, Comfort Zone. |
| **Onboarding UX** | 3-question rapid snapshot card. Single-tap chips. Zero sliders. 100% skippable. |
| **Profile UI Pattern** | "Social Rhythm" micro-badges with granular per-attribute privacy toggles. |
| **Discovery Role** | Practical friction reduction and ideal meeting setting suggestions. Soft signal; no hard dealbreakers. |
| **Database Model** | Normalized tables: `social_categories`, `social_options`, `user_social_preferences`, `social_relations`. |
| **API Contract** | Enriched `ProfileResponse` with `social_behavior: SocialBehaviorDTO`. Dedicated `/v1/social-behavior/*` endpoints. |
| **AI Context** | Contextual friction reduction and meeting advice; strictly barred from personality labeling or shaming. |
| **Security Policy** | Standard RLS: users manage own preferences; all options public; hidden fields suppressed from client and AI. |
| **V1 Scope** | 16 options, 3-question snapshot, social rhythm badges, battery awareness, meeting recommendations. |
| **Future Scope** | Event RSVP dynamics, advanced hangout scheduling, group conversation synergy. |
