# JESTER — Interest System & Interest Graph V1 Specification

**Document Type:** Platform Architecture & Product Specification  
**Version:** V1.0  
**Status:** Canonical Platform Architecture  
**Scope:** Cross-cutting (User Model, Onboarding, Discovery, Recommendation, JESTER AI, Data Architecture, Analytics)

---

## 1. Core Principle

JESTER Interests are **not merely profile tags**.

The Interest System is a **shared semantic layer** connecting:

```text
User Profile
     ↓
Onboarding
     ↓
Discovery
     ↓
Recommendation
     ↓
People Grouping
     ↓
Conversation Context
     ↓
JESTER AI
```

The system strictly distinguishes between:
1. **Declared**: What a user explicitly declares about themselves.
2. **Observed / Behavioral**: What is later observed from user activity, engagement, and interaction patterns.
3. **Semantically Related**: What is structurally connected in the underlying Interest Graph.
4. **Inferred**: What JESTER may calculate as an internal recommendation signal.

### Critical Behavioral Axiom:
> **A single interest must NEVER be treated as a complete personality definition.**

*Example:*  
`Photography` ≠ *"this person is creative"*.  
Photography may contribute to a broader recommendation signal only when combined with other declared or behavioral signals.

---

## 2. Interest Taxonomy V1

JESTER maintains a structured, versioned **Interest Taxonomy V1**.

### 2.1 Top-Level Categories (18 Initial Categories)
1. **Travel & Exploring**
2. **Food & Drink**
3. **Music**
4. **Movies & TV**
5. **Books & Ideas**
6. **Creative**
7. **Culture & Arts**
8. **Sports & Fitness**
9. **Nature & Outdoors**
10. **Games**
11. **Technology**
12. **Science & Space**
13. **Astrology & Spirituality**
14. **Wellness & Mindfulness**
15. **Fashion & Style**
16. **Animals & Pets**
17. **Social & Nightlife**
18. **Learning & Life**

### 2.2 Taxonomy Scale & Exposure Rules
- **Scale:** The target for Taxonomy V1 is approximately **150–200 canonical interests** distributed across these 18 categories.
- **Extensibility:** The taxonomy is designed to be versioned and extensible (`Taxonomy V1` → `Taxonomy V2`).
- **Internal Construct:** This is an internal semantic taxonomy. **Users must NEVER be exposed to the entire taxonomy as a checklist during onboarding.**

---

## 3. Canonical Interests, Slugs & Aliases

Each interest maintains a stable, immutable canonical identity rather than being treated as arbitrary user-generated free text.

### 3.1 Conceptual Entities

#### `interest_categories`
- `id` (UUID / Integer, Primary Key)
- `name` (Text, human-readable display name, e.g., `"Movies & TV"`)
- `slug` (Text, unique identifier, e.g., `"movies-tv"`)
- `icon` (Text, icon token)
- `sort_order` (Integer)
- `status` (Enum: `'active'`, `'deprecated'`)

#### `interests`
- `id` (UUID / Integer, Primary Key)
- `category_id` (Foreign Key → `interest_categories.id`)
- `name` (Text, canonical display name, e.g., `"Cinema"`)
- `slug` (Text, unique identifier, e.g., `"cinema"`)
- `description` (Text, internal semantic definition)
- `status` (Enum: `'active'`, `'hidden'`, `'deprecated'`)

#### `interest_aliases`
- `interest_id` (Foreign Key → `interests.id`)
- `alias` (Text, alternative search term or localized synonym)

*Example Alias Mapping:*
```text
"movies"   ──┐
"films"    ──┼──► Canonical Interest: Cinema (slug: "cinema")
"cinema"   ──┘
```

Raw text strings are never used as the primary identifier of an interest.

---

## 4. Interest Relationships (The Interest Graph)

Interests are structured as an interconnected **graph**, not a flat array.

### 4.1 Schema: `interest_relations`
- `interest_id` (Foreign Key → `interests.id`)
- `related_interest_id` (Foreign Key → `interests.id`)
- `relation_type` (Enum: `'sub_genre'`, `'semantic_peer'`, `'complementary'`, `'contextual'`)
- `weight` (Numeric `[0.0, 1.0]`, connection strength)

### 4.2 Semantic Graph Examples

```text
Photography
   ├── Travel (weight: 0.85)
   ├── Art (weight: 0.80)
   ├── Design (weight: 0.75)
   ├── Nature (weight: 0.70)
   ├── Architecture (weight: 0.65)
   └── Film (weight: 0.60)

Travel
   ├── Road Trips (weight: 0.90)
   ├── Adventure (weight: 0.85)
   ├── Nature (weight: 0.80)
   ├── Food (weight: 0.75)
   └── Exploration (weight: 0.90)

Astrology
   ├── Psychology (weight: 0.80)
   ├── Spirituality (weight: 0.85)
   ├── Tarot (weight: 0.75)
   ├── Relationships (weight: 0.70)
   └── Self-discovery (weight: 0.85)
```

### 4.3 Downstream Graph Utility
The graph structure powers:
- Related-interest discovery
- Multi-dimensional recommendation
- Contextual user grouping
- Semantic matching in Discovery
- Dynamic conversation starters

---

## 5. Domain Separation in the User Model

JESTER maintains strict domain boundaries in the User Model. **Interests must never become a dumping ground for other user dimensions.**

| Concept | Correct User Model Domain | NOT an Ordinary Interest |
| :--- | :--- | :--- |
| **Photography, Hiking, Cinema** | `Interests` | ✅ Ordinary Interest |
| **Want children / Have children** | `Lifestyle / Family Plans` | ❌ Not an Interest |
| **Long-term relationship / Friendship** | `Relationship Intent` | ❌ Not an Interest |
| **Introvert / Extrovert** | `Social Energy / Personality Signal` | ❌ Not an Interest |
| **Ambition / Humor / Honesty** | `Values & Traits` | ❌ Not an Interest |
| **Deep conversations / Fast texting** | `Communication Preferences` | ❌ Not an Interest |

Preserving this separation guarantees data integrity, prevents muddy recommendation signals, and keeps JESTER's intelligence engine clean.

---

## 6. Astrology: Dual-Layer Architecture

Astrology operates across two completely separate platform layers:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. INTEREST LAYER (Declared Preference)                    │
│    User chooses: "Astrology", "Birth charts", "Synastry"    │
│    Meaning: "I am interested in discussing astrology."      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. SYSTEM DATA LAYER (Deterministic Engine)                 │
│    User enters: birth date, birth time, place coordinates   │
│    System computes: Swiss Ephemeris natal chart & Synastry  │
│    Meaning: Deterministic interpersonal intelligence.       │
└─────────────────────────────────────────────────────────────┘
```

### Essential Privacy & Product Invariants:
1. **Having natal chart data does NOT mean the user is interested in astrology.** (A user may want JESTER's relational insights without any interest in astrological theory).
2. **Selecting astrology as an interest does NOT grant permission to inject raw cosmic jargon into every feature.** JESTER always maintains its witty, human-first voice.
3. The two concepts must remain decoupled across all models and APIs.

---

## 7. Onboarding Interest Rules

To prevent low-quality "select everything" behavior and cognitive overload, onboarding enforces a strict prioritization mechanism:

### 7.1 The Rules
1. **Optional Selection:** The user may **skip** interest selection entirely during onboarding.
2. **Exact Gating:** If the user chooses to select interests during onboarding, they **MUST select exactly 5 Primary Interests**.
3. **Candidate Pool:** The user is presented with a curated candidate pool of approximately **20 candidate interests** (not the full 200-item taxonomy).
4. **Action Gating:** The "Continue" button is disabled until the counter reaches **5 / 5** (or until the user taps "Skip").

### 7.2 Representative 20-Item Onboarding Pool
```text
[ Travel ]       [ Coffee ]      [ Music ]        [ Photography ]
[ Movies ]       [ Books ]       [ Astrology ]    [ Food ]
[ Hiking ]       [ Art ]         [ Fitness ]      [ Dogs ]
[ Technology ]   [ Gaming ]      [ Fashion ]      [ Nature ]
[ Theatre ]      [ Writing ]     [ Psychology ]   [ Concerts ]
```

*Personalization Constraint:* The 20-item pool may be lightly contextualized based on prior steps, but it must remain lightweight and never attempt to box the user into a predetermined type.

---

## 8. Primary vs. Secondary Interests

JESTER explicitly separates interest prioritization into two distinct tiers:

### 8.1 Primary Interests
- **Definition:** The 5 interests explicitly chosen and prioritized by the user during onboarding.
- **Meaning:** *"These are the things that feel most like me."*
- **Role:** Primary identity anchor; prominent visual hierarchy on profile; dominant discovery match weights.

### 8.2 Secondary Interests
- **Definition:** Additional interests added later via profile editing.
- **Meaning:** *"These are other things I am into."*
- **Role:** Broader contextual discovery; secondary profile display.

### 8.3 Conceptual Entity: `user_interests`
- `user_id` (UUID, Foreign Key → `profiles.id`)
- `interest_id` (Foreign Key → `interests.id`)
- `type` (Enum: `'primary'`, `'secondary'`)
- `is_signature` (Boolean, default: `false`)
- `source` (Enum: `'declared'`, `'profile_edit'`, `'prompt'`)
- `visibility` (Enum: `'public'`, `'connections_only'`, `'hidden'`)
- `created_at` (Timestamptz)
- `updated_at` (Timestamptz)

---

## 9. Signature Interest

Following the selection of 5 Primary Interests, JESTER may optionally present an optional single-choice prompt:

> *"Which one could you talk about forever?"*

### Rules & Impact
- **Non-Mandatory:** Must be skippable to avoid onboarding friction.
- **Data Marker:** Sets `is_signature = true` on the chosen interest (maximum 1 per user).
- **Product Value:**
  - Distinctive profile badge / highlight.
  - High-priority hook for JESTER conversation starters.
  - Contextual anchor in Discovery cards.

---

## 10. Interest Intensity Policy

JESTER explicitly prohibits multi-point intensity rating during onboarding:
- **NO** *"Love / Like / Obsessed"* sliders.
- **NO** 1-to-5 star ratings per interest.

*Rationale:* Adding rating scales creates friction, increases drop-off, and yields unreliable self-assessments. Interest depth is enriched progressively through profile engagement, JESTER interactions, and behavioral signals.

---

## 11. Interest Source & Multi-Tier Affinity

The system tracks the provenance and confidence of interest data across multiple layers:

### 11.1 Provenance Sources
- `declared`: Explicitly picked by the user in UI.
- `prompt`: Stated in answer to a specific JESTER prompt.
- `conversation`: Surfaced organically in chat/topics.
- `behavioral`: Inferred from browsing, reading, or topic engagement.
- `inferred`: Derived from semantic graph neighborhood analysis.

### 11.2 Conceptual Entity: `user_interest_affinity`
- `user_id` (UUID, Foreign Key → `profiles.id`)
- `interest_id` (Foreign Key → `interests.id`)
- `score` (Numeric `[0.0, 1.0]`, affinity intensity)
- `confidence` (Numeric `[0.0, 1.0]`, algorithmic certainty)
- `source` (Enum: `'declared'`, `'prompt'`, `'conversation'`, `'behavioral'`, `'inferred'`)
- `updated_at` (Timestamptz)

### 11.3 Overwrite Invariant
> **Behavioral affinity scores must NEVER overwrite or mutate explicit user declarations.**  
If a user declared Photography, `declared: true` remains fixed. If behavioral data indicates an affinity score of `0.85`, it is tracked in `user_interest_affinity` alongside the declared state.

---

## 12. Declared Interests vs. Behavioral Affinity

These two layers serve fundamentally different platform needs:

1. **Declared Interests (Presentation Layer):**
   - User-controlled, public-facing, identity self-expression.
   - Displayed on the user profile and shared connection cards.
2. **Behavioral Affinity (Internal Intelligence Layer):**
   - Internal signals used strictly for recommendation, feed ranking, and candidate discovery.
   - **Non-Judgment Rule:** JESTER does not label or judge users based on behavioral affinity (e.g. never tell a user *"You are a visual storyteller"* unless intentionally packaged as a delightful JESTER insight experience).

---

## 13. Discovery Matching Dimensions

Interest matching in Discovery operates across three distinct relationship tiers rather than flat string comparison:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. SHARED                                                   │
│    Both users explicitly share the same canonical interest. │
│    UI Voice: "You both love photography."                   │
├─────────────────────────────────────────────────────────────┤
│ 2. RELATED                                                  │
│    Users have different but graph-connected interests.      │
│    (e.g., User A: Photography, User B: Travel)              │
│    UI Voice: "You both love exploring — just differently."  │
├─────────────────────────────────────────────────────────────┤
│ 3. COMPLEMENTARY                                            │
│    Different interests + compatible energy or social style. │
│    UI Voice: "Different interests. Similar energy."         │
└─────────────────────────────────────────────────────────────┘
```

---

## 14. Internal Interest Clusters

JESTER utilizes internal **Interest Clusters** as algorithmic grouping constructs.

### 14.1 Cluster Nature
- Clusters are **internal recommendation constructs**, NOT user personality badges or permanent psychological classifications.
- Assigning a cluster requires **multiple converging signals**, never a single interest.
  - *Example:* `Travel` alone does NOT make someone an *"Adventurer"*.
  - An `Explorer` signal requires: `Travel` + `Road trips` + `Outdoors` + behavioral exploration evidence.

### 14.2 Representative Taxonomy Clusters
- *Explorers*
- *Creatives*
- *Thinkers*
- *Social Butterflies*
- *Homebodies*
- *Culture Lovers*
- *Food People*
- *Nature People*
- *Tech People*
- *Wellness People*
- *Curious Minds*

---

## 15. Cross-Category Semantic Clusters

To capture the nuance of modern human connection, the recommendation engine models cross-category combinations:

| Cross-Category Cluster | Contributing Signals | Relational Dynamic |
| :--- | :--- | :--- |
| **Coffee & Conversations** | Coffee + Books + 1-on-1 social preference + Deep conversation preference | Intimate intellectual connection |
| **Let's Just Go Somewhere** | Travel + Road trips + Spontaneity + Adventure | Kinetic, exploratory momentum |
| **Creative Chaos** | Photography + Music + Design + Spontaneity | Expressive, aesthetic synergy |
| **Quiet but Interesting** | Books + Movies + Lower social energy + Deep conversations | Calibrated, low-drain curiosity |
| **Always Doing Something** | Sports + Travel + High social activity | High-energy dynamic partnership |

---

## 16. Profile Presentation & Visual Hierarchy

The user profile must avoid becoming a cluttered "tag cloud":

1. **Hierarchy:** Primary Interests are given prominent visual weight. Secondary Interests are grouped separately or revealed progressively.
2. **Signature Badge:** If a Signature Interest exists, it receives distinctive UI elevation.
3. **Conversational Focus:** Every interest should help an observer answer:
   > *"What could I talk to this person about?"*  
   rather than communicate: *"This person checked a box."*

---

## 17. Conversation Value vs. 18. Discovery Value

The system explicitly distinguishes between an interest's conversational utility and its discovery utility:

```text
┌─────────────────────────────────────────────────────────────┐
│ CONVERSATION VALUE                                          │
│ How easily does this interest generate an engaging chat?    │
│ • Photography: High conversation value                      │
│ • Coffee: High local meetup / conversation value            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ DISCOVERY / RECOMMENDATION VALUE                            │
│ How predictive or distinctive is this interest for matching?│
│ • Common interest (e.g. "Music"): High broad compatibility  │
│ • Niche interest (e.g. "Obscure Philosophy"): High match    │
│   affinity, but narrower general conversation appeal.       │
└─────────────────────────────────────────────────────────────┘
```

These values are parameterized separately in the graph weights to prevent generic interests from dominating Discovery while allowing high-conversation topics to lead icebreakers.

---

## 19. Progressive Onboarding Philosophy

JESTER adheres strictly to this design principle:
> **"Collect enough information to make the first experience useful, but never ask users to fully describe themselves before they can experience JESTER."**

- Lightweight onboarding: Birth Data + Optional 5 Primary Interests.
- Broad underlying schema designed for progressive enrichment over time.
- Deep behavioral affinity is observed and calculated downstream.

---

## 20. Analytics & Telemetry Learning Loop

The Interest Graph is measured and iterated systematically from V1 launch:

### 20.1 Core Telemetry Events
- `interest_selection_started`
- `interest_selected` (interest_id, source)
- `interest_deselected` (interest_id)
- `interest_selection_skipped`
- `primary_interest_completed` (count: 5)
- `signature_interest_selected` (interest_id)
- `secondary_interest_added` (interest_id)
- `secondary_interest_removed` (interest_id)
- `interest_search_used` (query)
- `interest_category_opened` (category_id)
- `discover_profile_viewed` (target_user_id, shared_interest_count)
- `discover_profile_dismissed` (target_user_id)
- `connection_created` (source: shared_interest | astrology | direct)
- `conversation_started` (topic_source: interest | synastry)

### 20.2 Taxonomy Lifecycle: Build → Measure → Learn
Telemetry directly informs taxonomy expansion, weight calibration, and alias mapping from `Taxonomy V1` to `Taxonomy V2`.

---

## 21. UX Constraint: Simple for User, Rich for System

- The user sees a clean, focused, 5-choice selection from ~20 candidates during onboarding.
- The system captures a multi-layered graph node connected to 200+ canonical interests, semantic weights, and cross-category clusters.
- **Rule:** The full taxonomy must never be dumped onto the client as a giant checklist.

---

## 22. Platform Consistency Checklist

All platform documentation must align with these 12 immutable principles:

1. [x] **Interest selection is optional.**
2. [x] **If selected during onboarding, exactly 5 Primary Interests are chosen.**
3. [x] **The onboarding candidate pool contains approximately 20 interests.**
4. [x] **Secondary Interests can be added later via profile.**
5. [x] **One optional Signature Interest may be selected.**
6. [x] **Declared interests and behavioral affinity are strictly separated.**
7. [x] **Astrology Interest and Astrology Birth Data are separate layers.**
8. [x] **Interests are separated from lifestyle, intent, traits, and communication preferences.**
9. [x] **Interest relationships form an interconnected graph with weighted edges.**
10. [x] **Interest clusters are internal recommendation constructs, not fixed personality labels.**
11. [x] **Profile Photo (aesthetic self-expression) and Face Verification (identity security) are separate concepts.**
12. [x] **User data is collected progressively over time.**
