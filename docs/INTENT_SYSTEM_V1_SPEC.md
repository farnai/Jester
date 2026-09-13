# JESTER — Intent System V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

---

## 1. Product Purpose & Philosophy

JESTER is a **People Discovery and Relationship Intelligence** platform. 

To help people understand themselves, discover compatible connections, and navigate relational dynamics, the platform systematically maps foundational human domains:
> **Identity answers:** *"Who are you?"* (Name, age, cultural roots, birth parameters)  
> **Location answers:** *"Where are you based and where are you from?"* (Current residency, regional heritage)  
> **Interests answer:** *"What are you into?"* (Topics, intellectual passions, creative crafts)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, activity pace, work reality, living context)  
> **Values answer:** *"What matters to you?"* (Guiding principles, moral compass, life priorities)  
> **Social Behavior answers:** *"How do you tend to be around people?"* (Gathering scale, social battery, setting comfort)  
> **Communication answers:** *"How do you like to communicate?"* (Conversation depth, dynamic role, format, pacing)  
> **Intent answers:** *"What are you looking for on JESTER right now?"* (Current connection purpose, relational openness)

Intent describes **the user's current motivation for engaging on JESTER and the specific forms of connection they are open to experiencing**.

### Core Operating Axioms:
1. **Intent is Temporal, Not Identity:** Interests and values remain relatively stable over years. Intent fluctuates across life seasons (e.g. exploring a new city $\rightarrow$ seeking an activity partner $\rightarrow$ open to serious romance $\rightarrow$ focusing on creative collaboration). The architecture treats Intent as a fluid, editable state, never as a permanent personality label.
2. **Intent Answers Purpose, NOT Relationship Status:** Intent answers *"What are you seeking right now on JESTER?"* It strictly does **NOT** answer *"Are you single/married?"* or *"What is your marital history?"*
3. **Declared User Reality > Behavioral Inference > Astrological Interpretation:** What a user explicitly declares about their intent overrides algorithmic guesses or astrological Venus/Mars placements. If two users possess explosive synastry chemistry but User A seeks platonic friendship and User B seeks serious dating, **declared intent wins**. JESTER will never force a romantic framing on a platonic intent.
4. **People First. Signals Second. Scores Last:** Intent creates transparency and mutual safety before interaction begins. It prevents mismatched expectations, eliminates awkward misinterpretations, and turns discovery into aligned invitations.
5. **Lightweight & Non-Intrusive:** Onboarding captures a rapid 1-step or 2-tap intent choice that is 100% skippable. Zero lengthy interrogation questionnaires.

---

## 2. Conceptual Boundary & Domain Decoupling

To prevent cross-domain pollution, JESTER enforces strict architectural boundaries between Intent and adjacent subsystems:

```text
┌───────────────────┬──────────────────────────────────┬──────────────────────────────────────────────────────────┐
│ Domain            │ Core Question Answered           │ Canonical Example                                        │
├───────────────────┼──────────────────────────────────┼──────────────────────────────────────────────────────────┤
│ 1. Identity       │ Who am I?                        │ Name, gender, age, birth data, cultural roots            │
│ 2. Location       │ Where am I based / from?         │ Current City (Tbilisi), Hometown (Kvareli)               │
│ 3. Interests      │ What am I into?                  │ Photography, Cinema, Hiking, Philosophy                  │
│ 4. Lifestyle      │ How do I live my everyday life?  │ Night Owl, High Velocity, Remote Work, Pet Owner         │
│ 5. Values         │ What principles matter to me?    │ Autonomy, Honesty, Curiosity, Kindness                   │
│ 6. Social Behavior│ How am I around people?          │ Prefers one-on-one, recharges solo, observant first     │
│ 7. Communication  │ How do I communicate?            │ Deep depth, asks questions, voice notes OK, relaxed pace │
│ 8. Intent         │ What am I seeking right now?     │ Friendship, Dating, Activity partner, Collaboration      │
│ 9. Prompts        │ How do I express my voice?       │ Open-ended text prompts and personal quotes              │
└───────────────────┴──────────────────────────────────┴──────────────────────────────────────────────────────────┘
```

### Master Decoupling Table:

| Candidate Concept | Primary Domain | Decoupling Invariant & Justification |
| :--- | :--- | :--- |
| **New Friends / Social Circle** | `Intent` | Current purpose on platform; NOT social battery capacity (`Social Behavior`). |
| **Dating / Romance** | `Intent` | Relational openness; NOT marital status (`Identity`). |
| **Activity / Sports Partner** | `Intent` | Desire to find co-participants; NOT the specific sport itself (`Interests`). |
| **Creative / Project Partner** | `Intent` | Purpose of connection; NOT professional occupation (`Identity`). |
| **Single / In a Relationship** | `Identity / Status` | Legal or relational circumstance; NOT platform purpose. (JESTER is for everyone). |
| **Wants Children / Family Future**| `Values & Life Direction`| Long-term existential priority; NOT current app intent. Must remain decoupled. |
| **Looking for Deep Conversations**| `Communication` & `Intent` | Depth of talk is `Communication`; desire to connect purely for conversation is `meaningful_chat` intent. |
| **Hiking / Cinema / Tech** | `Interests` | Topical hobbies; Intent determines *why* you connect over them. |
| **Recharging in Solitude** | `Social Behavior` | Neuro-social energy recovery; NOT disinterest in connecting. |

---

## 3. Critical Question: Is JESTER a Dating App?

JESTER is **NOT** a dating app, nor is it a sterile professional networking tool. It is a **People Discovery and Relationship Intelligence Engine**.

### The Unified Discovery Model vs. Fractured Mode Switching:
- **The Competitor Failure Pattern (The "Bumble Dilemma"):** Splitting an app into hard, segregated silos ("Date Mode", "BFF Mode", "Bizz Mode") fractures user liquidity, empties discovery feeds, and creates jarring friction where users must maintain multiple parallel profiles.
- **The Generic Dating Trap (The "Tinder Dilemma"):** Assuming every interaction is inherently romantic turns platonic exploration into an awkward or unsafe experience, alienating users seeking friends, creative collaborators, or intellectual peers.
- **The JESTER Architecture (Unified Intent-Aware Discovery):**
  1. JESTER operates on a **single, unified human profile**.
  2. Intent is an explicit, first-class, **transparent attribute** attached to profiles and discovery cards.
  3. Discovery feeds adapt to intent alignment: romantic candidates are suggested to romantic seekers; platonic seekers discover platonic peers; open-minded explorers discover broad human variety.
  4. Romantic dating, platonic friendship, activity partners, and creative collaborations coexist with mutual dignity on the same platform without identity confusion.

---

## 4. Canonical Intent Taxonomy V1 (3 Categories, 7 Options)

JESTER V1 establishes a curated, focused taxonomy of **7 canonical options** organized into 3 intuitive categories:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            JESTER INTENT TAXONOMY V1                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Social & Personal Connection                                                        │
│    • friendship          New Friends             (Expanding circle, platonic bond)     │
│    • dating_open         Dating & Chemistry      (Romantic spark, open to connection)  │
│    • dating_serious      Long-Term Relationship  (Intentional dating, committed bond)  │
│    • meaningful_chat     Great Conversation      (Exchanging ideas, intellectual talk) │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Activity & Practical Collaboration                                                  │
│    • activity_partner    Activity Partner        (Sports, outdoors, events, travel)    │
│    • collaboration       Creative Collaboration  (Projects, co-creation, building)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Exploratory                                                                         │
│    • just_exploring      Just Exploring          (Curious, open-minded, seeing vibes)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Definitions & Canonical Slugs:

1. `friendship`:
   - *Definition:* Seeking meaningful, genuine friendships and expanding one's everyday social circle. Zero romantic expectations.
   - *Badge Icon:* `users`
   - *Localized Label:* New Friends / ახალი მეგობრები

2. `dating_open`:
   - *Definition:* Open to dating, mutual chemistry, and romantic exploration without rigid pre-determined timelines or heavy pressure.
   - *Badge Icon:* `sparkles`
   - *Localized Label:* Dating & Chemistry / გაცნობა & რომანტიკა

3. `dating_serious`:
   - *Definition:* Seeking intentional dating with the clear goal of building a committed, long-term partnership.
   - *Badge Icon:* `heart`
   - *Localized Label:* Long-Term Relationship / სერიოზული ურთიერთობა

4. `meaningful_chat`:
   - *Definition:* Primarily looking for stimulating conversations, debating ideas, sharing perspectives, and engaging in deep banter.
   - *Badge Icon:* `message-circle`
   - *Localized Label:* Great Conversation / საინტერესო საუბრები

5. `activity_partner`:
   - *Definition:* Looking for someone to share concrete real-world activities with—hiking, sports, gym, gallery visits, concerts, or weekend trips.
   - *Badge Icon:* `compass`
   - *Localized Label:* Activity Partner / აქტივობების პარტნიორი

6. `collaboration`:
   - *Definition:* Seeking creative, intellectual, or entrepreneurial peers to brainstorm, build projects, make art, or exchange skills.
   - *Badge Icon:* `cpu`
   - *Localized Label:* Creative Collaboration / შემოქმედებითი თანამშრომლობა

7. `just_exploring`:
   - *Definition:* Curious about JESTER, open to unexpected connections, taking things as they come with zero predetermined agenda.
   - *Badge Icon:* `search`
   - *Localized Label:* Just Exploring / ჯერჯერობით ვათვალიერებ

---

## 5. Primary vs. Secondary Intent Model

Human intentions are nuanced. A person is rarely 100% monolithic in what they seek. For instance, someone's primary goal may be finding a serious partner, but they are warmly open to making great friends along the way.

To capture this without questionnaire bloat, JESTER implements the **1 Primary + Max 2 Secondary** model:

```text
┌────────────────────────────────────────────────────────┐
│                   YOUR INTENT SELECTION                │
│                                                        │
│  PRIMARY FOCUS (Choose 1)                              │
│  [ 💖 Long-Term ]  [ ✨ Dating ]  [ 👥 New Friends ]   │
│  [ 🧗 Activity ]   [ 💡 Collaboration ]                │
│  [ 💬 Great Chat ] [ 🔍 Just Exploring ]              │
│                                                        │
│  ALSO OPEN TO (Optional, pick up to 2)                 │
│  [ 👥 New Friends ]  [ 🧗 Activity ]  [ 💬 Great Chat ]│
│                                                        │
│  [ Skip for now ]                         [ Save ]     │
└────────────────────────────────────────────────────────┘
```

### Business & Selection Rules:
1. **Primary Intent (Single-Select):** Defines the user's primary compass on the platform. Governs discovery indexing and baseline card presentation.
2. **Secondary Intents (Multi-Select, 0 to 2 max):** Defines supplementary openness. Prevents artificial isolation and enables multi-channel connection bridges.
3. **Mutual Exclusivity Constraints:** A user cannot select the same option as both Primary and Secondary.
4. **`just_exploring` Rule:** If `just_exploring` is chosen as Primary, secondary options are disabled (as exploring already implies universal open-mindedness).
5. **Easy Reversibility:** Users can change their Primary and Secondary intents at any time in Profile Settings with immediate effect.

---

## 6. Temporal Architecture & Lifecycle of Intent

Intent is the most dynamic profile attribute in JESTER.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      INTENT STATE & LIFECYCLE                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Current Declared Intent (`public.user_intents`)                     │
│    • Active, public, discoverable                                      │
│    • Directly editable by user at any time                             │
│    • Evaluated in real-time by Discovery and AI starter engines        │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Intent Transition Audit Log (`public.user_intent_history`)          │
│    • Internal append-only transition log                               │
│    • Records: `user_id`, `previous_primary`, `new_primary`, timestamp  │
│    • STRICT INVARIANT: 100% Private (REVOKED from all client roles)    │
│    • Never exposed on public profile or discovery cards                │
│    • Never used to embarrass or judge users (e.g. "Changed intent 3x") │
└────────────────────────────────────────────────────────────────────────┘
```

### Lifecycle Invariants:
- **No Expiration Anxiety:** Intent does not arbitrarily expire after 7 days (avoiding nagging notifications).
- **Graceful Refresh Prompts:** After 90 days of unchanged intent, JESTER may show a gentle, non-blocking profile banner: *"Still looking for the same things? Update your intent anytime."*
- **Instant Discovery Updates:** Updating intent instantly recalculates discovery filtering and invalidates cached discovery candidate sets.

---

## 7. Onboarding UX: The Lightweight Intent Choice

Onboarding must be lightning fast, pressure-free, and respectful.

### The Single-Card Onboarding Step:
- **Positioning:** Positioned as the final step of the core profile flow (after Birth Data, Location, and optional Snapshots).
- **Core Prompt:** *"What brings you to JESTER right now?"*
- **Interface:** Interactive micro-chips displayed in a clean grid.
- **One-Tap Primary Selection:** Tapping any chip immediately marks it as Primary.
- **Optional Secondaries:** A small secondary row unlocks: *"Also open to (optional, up to 2)"*.
- **Prominent Skip Button:** A clear `"Skip for now"` button permits immediate onboarding completion.
- **Default on Skip:** If skipped, the user's intent defaults to `just_exploring` with `source = 'skipped'`, ensuring the user is not excluded from discovery.

---

## 8. "Just Exploring" & Graceful Default Behavior

Allowing users to declare `just_exploring` is critical for product trust:
- **Reduces Onboarding Friction:** New users who are hesitant to commit to "Dating" or "Friends" can enter without performance anxiety.
- **Discovery Behavior:** Users marked `just_exploring` appear in discovery feeds across all general categories, flagged with a discreet `[ 🔍 Exploring ]` chip.
- **Connection Safety:** When a user with `just_exploring` connects with someone seeking `dating_serious`, JESTER AI gently prompts clear communication: *"Alexandre is just exploring right now — keep things natural and see where the vibe leads."*

---

## 9. Dating Intent Isolation & Decoupling from Family Planning

Dating intent carries unique emotional weight and requires strict boundary enforcement:

### 1. `dating_open` vs. `dating_serious`:
- Clearly separates casual romantic exploration (`dating_open`) from committed partnership search (`dating_serious`), preventing the #1 source of dating app resentment.

### 2. Strict Decoupling from Family Planning / Children:
- Questions such as *"Do you want children?"* or *"Family plans"* **MUST NOT** be merged into Intent V1.
- Family planning is an existential, lifelong orientation belonging properly to **Values & Life Direction** (`public.user_values`).
- Intent V1 remains strictly focused on current platform purpose.

### 3. Strict Decoupling from Relationship Status:
- JESTER does not ask: *"Are you single?"*
- Intent represents what you are open to on the platform. A user seeking friendship or co-founders has no obligation to declare their private relationship status.

---

## 10. Discovery Relevance & Intent Compatibility Filter Rules

Intent plays a decisive role in Discovery. Unlike subtle lifestyle habits or social battery, mismatched relationship intents can lead to harassment, disappointment, or wasted time.

### 10.1 Intent Compatibility Matrix:

| Viewer Intent | Target: `dating_serious` | Target: `dating_open` | Target: `friendship` | Target: `activity_partner` | Target: `collaboration` | Target: `just_exploring` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`dating_serious`** | 🟢 **Symmetric Match** | 🟡 **Aligned (Soft)** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🟡 **Compatible** |
| **`dating_open`** | 🟡 **Aligned (Soft)** | 🟢 **Symmetric Match** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🟡 **Compatible** |
| **`friendship`** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🟢 **Symmetric Match** | 🟢 **Symmetric Match** | 🟡 **Compatible** | 🟢 **Compatible** |
| **`activity_partner`** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🟢 **Symmetric Match** | 🟢 **Symmetric Match** | 🟢 **Compatible** | 🟢 **Compatible** |
| **`collaboration`** | 🔴 **Partitioned** | 🔴 **Partitioned** | 🟡 **Compatible** | 🟢 **Compatible** | 🟢 **Symmetric Match** | 🟢 **Compatible** |
| **`just_exploring`** | 🟡 **Compatible** | 🟡 **Compatible** | 🟢 **Compatible** | 🟢 **Compatible** | 🟢 **Compatible** | 🟢 **Universal Match**|

*Note on Secondary Intents:* If Viewer A has Primary `dating_serious` but Secondary `friendship`, they are **NOT** partitioned from Target B (`friendship`); they are matched under the shared `friendship` bridge!

### 10.2 Mathematical Intent Filtering Rule:
Two users $A$ and $B$ are eligible for mutual Discovery presentation if:
$$\Big(\text{Intents}(A) \cap \text{Intents}(B) \neq \emptyset\Big) \quad \lor \quad \Big(\text{'just\_exploring'} \in \text{Intents}(A) \cup \text{Intents}(B)\Big)$$

If $\text{Intents}(A) \cap \text{Intents}(B) = \emptyset$, the pair is safely partitioned. This single mathematical invariant eliminates platonic/romantic harassment.

---

## 11. Intent × Astrology: The Absolute Primacy Invariant

Astrological synastry is deterministic intelligence; it is **NOT** a psychic prediction of user intent.

### The Invariant:
> **Declared User Intent strictly governs how Astrological Synergy is interpreted and presented.**

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        INTENT × ASTROLOGY BOUNDARY                     │
├────────────────────────────────────────────────────────────────────────┤
│ Scenario: Venus-Mars Conjunction (High Relational Chemistry)           │
│                                                                        │
│ IF Both Users Declare Dating Intent:                                   │
│   → JESTER AI: "Strong natural chemistry and magnetic attraction.      │
│     Conversation flows with effortless spark."                         │
│                                                                        │
│ IF Either User Declares Platonic Friendship / Collaboration:          │
│   → JESTER AI: "Vibrant creative energy and shared drive. You inspire  │
│     each other to take action and build exciting projects."            │
│                                                                        │
│ RULE: Synastry NEVER overrides declared intent. JESTER AI must NEVER   │
│ project romantic or sexual destiny onto a platonic connection.        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 12. Multi-Domain Relational Intelligence

Intent serves as the **operational anchor** that binds all prior JESTER systems into coherent, actionable invitations:

$$\text{Actionable Invitation} = \text{Intent} \times (\text{Interests} + \text{Lifestyle} + \text{Values} + \text{Social} + \text{Communication})$$

### Concrete Multi-Domain Synthesis Examples:

1. **Intent (`activity_partner`) + Interests (`Hiking`) + Lifestyle (`Early Bird`):**
   - *JESTER Insight:* *"You're both looking for activity partners, love hiking, and wake up early. Saturday morning trails are an easy match."*
2. **Intent (`meaningful_chat`) + Values (`Curiosity`) + Communication (`Deep & Meaningful`):**
   - *JESTER Insight:* *"Both here for great conversation and deep ideas. Skip the shallow small talk — you already have plenty to unpack."*
3. **Intent (`collaboration`) + Interests (`Photography`, `Cinema`) + Social (`One-on-One`):**
   - *JESTER Insight:* *"Both looking to collaborate on visual projects, preferring low-key one-on-one sessions over big groups. Grab coffee and trade notes."*

---

## 13. Public Profile Presentation: "Looking For" Micro-Badges

On public profiles, Intent is displayed prominently near the top of the profile (just below Location) to ensure immediate clarity:

```text
┌─────────────────────────────────────────────────┐
│ Alexandre, 28                                   │
│ 📍 Based in Tbilisi · 🏡 From Kvareli           │
│                                                 │
│ LOOKING FOR                                     │
│ [ 👥 New Friends (Main) ]  [ 🧗 Activity Partner ]
│                                                 │
│ ABOUT                                           │
│ "Architect by day, mountain trail runner by     │
│ weekend. Always down for good coffee and debate"│
└─────────────────────────────────────────────────┘
```

### Presentation Rules:
1. **Prominent Visual Anchor:** Displayed as elegant, elevated glassmorphic chips with distinct icons (`users`, `compass`, `heart`).
2. **Clear Primary Designation:** The primary intent is subtly starred or marked with `(Main)` to communicate true focus.
3. **Visibility Toggles:** Users can toggle Intent visibility (`public`, `connections_only`, `hidden`). When hidden, it does not display on the profile but still informs discovery filtering.
4. **Natural Sentence Fallback:** Clients can optionally render a human sentence: *"Alexandre is here for new friends and shared activities."*

---

## 14. Connection Request Context & "Why Connect?"

To fulfill JESTER's axiom **"The insight becomes the invitation"**, the connection flow bridges user intent with explicit context:

```text
┌────────────────────────────────────────────────────────┐
│                   SEND CONNECTION REQUEST              │
│                                                        │
│  To: Alexandre                                         │
│  You're both open to: [ 👥 New Friends ]               │
│                                                        │
│  ADD A QUICK CONTEXT (Optional)                        │
│  [ ☕ Grab coffee ]  [ 💬 Great conversation ]         │
│  [ 🧗 Shared activity ]  [ 🎨 Creative project ]       │
│                                                        │
│  [  Send Request  ]                                    │
└────────────────────────────────────────────────────────┘
```

### Protocol:
1. **Transparent Shared Intent:** The connection modal automatically displays mutual overlapping intents (e.g. *"You're both open to shared activities"*).
2. **Optional "Why Connect?" Tag:** Senders can tap an optional 1-tap tag (`connection_reason`) stored on the connection record.
3. **Recipient Experience:** The recipient receives the invitation with clear context: *"Alexandre wants to connect — you both love Photography and are looking for activity partners."* Zero creepy ambiguity.

---

## 15. Database Architecture Blueprint (DDL & Indexes)

The Intent System defines 5 normalized tables maintaining strict schema consistency with prior domains:

```sql
-- ============================================================================
-- 1. CANONICAL INTENT CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.intent_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'social_connection', 'dating_romance', 'activity_practical', 'exploratory'
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL INTENT OPTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.intent_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.intent_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'friendship', 'dating_open', 'dating_serious', 'meaningful_chat', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    definition_en TEXT NOT NULL,
    definition_ka TEXT NOT NULL,
    badge_icon VARCHAR(30),                    -- 'users', 'sparkles', 'heart', 'message-circle', 'compass', 'cpu', 'search'
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. USER INTENTS (Active Declared Intent State)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_intents (
    user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    primary_intent VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE RESTRICT,
    secondary_intents JSONB NOT NULL DEFAULT '[]'::jsonb,  -- Array of max 2 slugs
    visibility VARCHAR(20) NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'connections_only', 'hidden')),
    source VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding', 'profile_edit', 'skipped')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. INTENT RELATIONS GRAPH (Compatibility & Alignment Matrix)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.intent_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_a_slug VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE CASCADE,
    intent_b_slug VARCHAR(60) NOT NULL REFERENCES public.intent_options(slug) ON DELETE CASCADE,
    relation_type VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_match', 'aligned_soft', 'partitioned', 'universal')),
    alignment_label_en VARCHAR(120) NOT NULL,
    alignment_label_ka VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_intent_relation UNIQUE (intent_a_slug, intent_b_slug),
    CONSTRAINT check_no_self_intent_relation CHECK (intent_a_slug != intent_b_slug)
);

-- ============================================================================
-- 5. USER INTENT HISTORY (Private Transition Audit Log - SERVICE ONLY)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_intent_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    previous_primary VARCHAR(60),
    new_primary VARCHAR(60) NOT NULL,
    previous_secondaries JSONB,
    new_secondaries JSONB,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_user_intents_primary ON public.user_intents(primary_intent);
CREATE INDEX IF NOT EXISTS idx_user_intents_visibility ON public.user_intents(visibility);
CREATE INDEX IF NOT EXISTS idx_user_intent_history_user ON public.user_intent_history(user_id, changed_at DESC);
```

---

## 16. API Specification & Safe DTOs (Endpoints 65–70)

### 16.1 Safe Public Profile Extension (`IntentDTO`):
```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Alexandre",
  "intent": {
    "primary": {
      "slug": "friendship",
      "name": "New Friends",
      "icon": "users"
    },
    "secondaries": [
      {
        "slug": "activity_partner",
        "name": "Activity Partner",
        "icon": "compass"
      }
    ],
    "visibility": "public"
  }
}
```

### 16.2 Planned Endpoints:
1. `GET /v1/intents/options` — List canonical intent categories and localized options.
2. `GET /v1/intents/onboarding` — Retrieve the onboarding intent selection card metadata.
3. `POST /v1/intents/onboarding` — Submit initial primary & secondary intents (100% skippable).
4. `GET /v1/intents/me` — Retrieve own declared intent and visibility settings.
5. `PATCH /v1/intents/me` — Update primary intent, secondary intents, and visibility.
6. `GET /v1/intents/people/{target_user_id}` — Get discoverable target's public intent (respecting block rules and visibility flags).

---

## 17. Security, Privacy, Analytics & Scope

### 17.1 Security & Privacy Invariants:
1. **Audit Log Isolation:** `public.user_intent_history` is strictly **SERVICE-ONLY**. Client database roles (`authenticated`, `anon`, `public`) have zero permissions (`REVOKE ALL`). Past intentions must never be leaked or weaponized.
2. **Respect for Hidden State:** When `visibility = 'hidden'`, intent is omitted from public profile responses and target AI prompts, but remains active internally for bilateral discovery partitioning.
3. **Zero Inferred Intent:** Intent is strictly declared by the user. Recommendation algorithms, astrological calculators, and chat parsers are permanently prohibited from automatically guessing, overriding, or mutating user intent.

### 17.2 Non-Surveillance Analytics:
- `intent_onboarding_viewed` — Reached intent step in onboarding.
- `intent_onboarding_completed` — User declared intent.
- `intent_onboarding_skipped` — User skipped intent.
- `intent_updated` — User changed intent in profile settings.
- `connection_reason_selected` — User selected an optional connection reason tag.
- *Strict Invariant:* No tracking of chat text or message sentiment is permitted for intent analytics.

### 17.3 V1 vs. Future Roadmap:

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **7 Canonical Options / 3 Categories** | ✅ | — | Focused, dignified, non-confusing taxonomy |
| **1 Primary + Max 2 Secondary Model** | ✅ | — | Honest human nuance without form fatigue |
| **Bilateral Discovery Partitioning** | ✅ | — | Eliminates platonic/romantic harassment |
| **Profile "Looking For" Micro-Badges** | ✅ | — | Clear, glassmorphic chips with privacy toggles |
| **Optional "Why Connect?" Reason** | ✅ | — | Contextual invitations without pressure |
| **Astrology Primacy Invariant** | ✅ | — | Declared user reality strictly overrides astro |
| **Travel Mode / Temporary Location Intent** | ❌ | 🔮 | Future geo-roaming capability |
| **Event-Specific Intent Micro-Badges** | ❌ | 🔮 | Future festival/conference integration |
| **Intent Transition Machine Learning** | ❌ | 🔮 | Deferred until large-scale longitudinal data |

---

## 18. Final Architecture Decisions Table

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Core Product Purpose** | Answers *"What are you looking for on JESTER right now?"* — temporal purpose, not personality or marital status. |
| **App Identity (Dating vs Social)**| JESTER is a unified **People Discovery and Relationship Intelligence Engine**. No fractured mode switching. Single profile with transparent intent tags. |
| **Taxonomy Structure** | 7 canonical options across 3 categories: Social/Personal (`friendship`, `dating_open`, `dating_serious`, `meaningful_chat`), Activity (`activity_partner`, `collaboration`), and Exploratory (`just_exploring`). |
| **Selection Model** | 1 Primary Focus (Single-Select) + up to 2 Secondary Openness (Multi-Select). |
| **Temporal Nature** | Editable at any time. Current state is public; history is private append-only audit log. |
| **Onboarding UX** | 1-card rapid choice, 100% skippable. Defaults to `just_exploring` if skipped. |
| **Dating Boundary** | Clear separation between `dating_open` and `dating_serious`. Children/family planning decoupled to Values. |
| **Discovery Logic** | Hard bilateral partitioning for mutually incompatible intents (e.g. strict dating vs strict friends); soft relevance for aligned intents. |
| **Astrology Boundary** | Declared user intent strictly overrides astrological synastry. Astrological energy is framed within the declared intent boundary. |
| **Connection Flow** | Displays mutual shared intent context; optional 1-tap `connection_reason` tag ("Why connect?"). |
| **Database Blueprint** | 5 normalized tables: `intent_categories`, `intent_options`, `user_intents`, `intent_relations`, `user_intent_history`. |
| **API Blueprint** | Enriched `ProfileResponse` with `intent: IntentDTO|None` and dedicated endpoints 65–70 under `/v1/intents/*`. |
| **Privacy Policy** | History revoked from client roles; hidden intents stripped from public DTOs; zero algorithmic inference from chat bodies. |
