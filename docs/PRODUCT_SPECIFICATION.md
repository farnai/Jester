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

1. **ME (Understand Myself)**: User establishes their foundational identity: enters birth data (calculating deterministic natal intelligence) and optionally prioritizes 5 Primary Interests from a curated pool of ~20 candidate topics to experience their first personal taste of JESTER (*"Let's see what JESTER notices about me"*).
2. **YOU (Curiosity About Another)**: Curiosity naturally extends outward (*"What would JESTER say about my friend?"*).
3. **US (Relationship Intelligence)**: Comparing two profiles to unpack the connection (*"What does JESTER say about us?"*).
4. **MORE PEOPLE (Network & Discovery)**: Discovering new people, friends, collaborators, and relationship dynamics through shared, related, and complementary interest graphs and astrological synergy (*"Who else should I check?"*).

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

- **Backend / Data Layer (Product Capability)**: High-precision astronomical positions, house cusps, angular aspect geometries, multi-dimensional matrices, and semantic Interest Graph topology.
- **Consumer Interface (Product Experience)**: Clean, witty, human-readable JESTER observations, relationship dynamics, conversation starters, and connection insights.

---

JESTER V1 functional capabilities are composed of six major capability domains:

```text
JESTER V1
│
├── 1. Identity & Profile
├── 2. Interest System & Interest Graph
├── 3. Personal Astrology
├── 4. People & Relationships
├── 5. Communication
└── 6. JESTER Intelligence
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

# 3. Personal Profile & User Model

Every user has a social profile separate from their authentication identity.

## 3.1 Profile Information

A user maintains:

* Display name
* Profile Photo (Avatar URL)
* Bio
* Current Location (`current_city_id`, `current_country_id` — e.g. "Tbilisi, Georgia")
* Origin / Hometown (`hometown_city_id`, `hometown_country_id`, `hometown_visible` — e.g. "Kvareli, Georgia")
* Occupation
* Timezone (e.g. "Asia/Tbilisi")
* Discoverability status (`is_discoverable`)
* Declared Interests (Primary Interests, Secondary Interests, and optional Signature Interest)
* Lifestyle & Cadence (Daily rhythm, activity pace, work style, pet cohabitation, and toggleable habits)
* Values & Guiding Compass (Core Value and 3–5 guiding life principles)
* Social Rhythm & Behavior (Gathering scale preference, social battery recharge style, warm-up dynamic, and comfort zone)
* Communication Rhythm & Preferences (Conversation depth, conversational role, messaging format, and pacing)
* Intent & Relational Openness (Primary Intent, up to 2 Secondary Intents, and visibility)
* Prompts & Self-Expression (Short Headline/Bio up to 140 chars + up to 3 curated prompt answers up to 250 chars)
* Discovery Preferences (Age bounds, target genders, geographic scope, astrology depth — strictly private outbound controls)

## 3.2 Privacy & Visibility

Users must be able to control whether their profile is discoverable (`is_discoverable`).

A non-discoverable profile must not be exposed through normal person/profile access.

Blocked users must not be able to access protected profile information or safe astrology.

## 3.3 Separation of Profile Photo and Face Verification

JESTER enforces a strict conceptual and architectural boundary:
* **Profile Photo (Avatar):** An aesthetic, user-controlled element for visual social presentation and self-expression.
* **Face Verification:** An independent biometric and identity verification security capability.

These must **never** be conflated or coupled in schema, authorization, or user flow.

## 3.4 Domain Separation in the User Model

JESTER strictly isolates user dimensions. **Interests, Locations, Lifestyles, and Values must never become a dumping ground for unrelated attributes:**

| Concept | Domain | Invariant & Boundary |
| :--- | :--- | :--- |
| **Photography, Travel, Cinema, Astrology** | `Interests` | Distinct, topical affinities (*"What I'm into"*). |
| **Current City ("Based in Tbilisi")** | `Current Location` | Operational/social residency; soft discovery signal. |
| **Hometown ("From Kvareli")** | `Origin / Heritage` | Cultural root & conversational bridge; NOT current city. |
| **Birth Place ("Born in Kutaisi")** | `Astrological Calculation` | Private owner-only in `birth_data`; NOT profile location. |
| **Remote Work, Night Owl, Active Pace** | `Lifestyle` | Daily operational habits & cadence (*"How I live"*). |
| **Dog Owner ("Has a dog")** | `Lifestyle` | Daily household living reality and time commitment. |
| **Loves Dogs ("Dog lover")** | `Interests` | Topical animal passion; does not require owning a pet. |
| **Autonomy, Growth, Honesty, Curiosity** | `Values` | Guiding principles & life priorities (*"What matters to me"*). |
| **Adventure & Exploration** | `Values` | Priority of seeking the unfamiliar over comfort; not just hiking. |
| **Introvert / Extrovert / Ambivert** | `Social Behavior` | Internal battery recharge style; NOT a lifestyle habit or value. |
| **Deep conversations, Banter** | `Communication` | Interaction depth and communication preference. |
| **Has Children ("Parent")** | `Lifestyle / Household` | Daily living reality and time responsibility. |
| **Wants Children / Family Plans** | `Values & Life Direction`| Long-term relational alignment; NOT everyday routine. |
| **New Friends, Dating, Activity, Collab** | `Intent` | What the user is seeking on JESTER right now. |
| **Open-ended voice, quirks, stories** | `Prompts / Voice` | Authentic human voice, tone, and conversation hooks. |
| **Age Bounds, Target Genders, Location Scope** | `Discovery Preferences` | Outbound candidate filtering & ranking controls (*"Who I want to see"*); strictly private. |
| **Drinking / Smoking Habits** | `Lifestyle (Sensitive)` | Personal consumption habits; strictly user-controlled. |
| **Living Situation (Alone / Roommates)** | `Lifestyle (Household)` | Living structure; private/toggleable by default. |

## 3.5 Progressive Data Collection Philosophy

The platform operates on a clear guiding principle:
> **"Collect enough information to make the first experience useful, but never ask users to fully describe themselves before they can experience JESTER."**

- Onboarding remains intentionally lightweight (Birth Data + Optional Location + Optional Lifestyle Snapshot + Optional Values Selection + Optional Social Rhythm Snapshot + Optional Communication Snapshot + Optional Intent Selection + Optional Prompts + Optional 5 Primary Interests).
- The underlying schema is designed broadly from the start to support progressive enrichment over time.
- Deep behavioral affinity and nuanced relationship signals are observed downstream rather than demanded upfront.

## 3.6 Location & Origin System V1

JESTER defines a dedicated **Location & Origin System** governed by clear privacy and human-context invariants:

1. **Three Decoupled Geographic Layers:**
   - **Current Location ("Where are you based?"):** Social/physical base (e.g. Tbilisi). Displayed publicly as `📍 Tbilisi`.
   - **Origin / Hometown ("Where are you from?"):** Cultural background (e.g. Kvareli). Displayed optionally as `🏡 From Kvareli` if `hometown_visible = true`.
   - **Birth Place:** Private computational parameter in `public.birth_data` (e.g. Kutaisi) for Swiss Ephemeris natal calculations. Completely decoupled from everyday location.
2. **Strict Coordinate Privacy:** Exact coordinates (`latitude`, `longitude`), street addresses, and real-time tracking are **never** publicly exposed or serialized in public client DTOs.
3. **Canonical Resolution:** Locations reference normalized entities (`geo_cities`, `geo_countries`) with localized names (Georgian & English) rather than unstructured free-text strings.
4. **Discovery Relevance:** Location acts as a **soft relevance boost** (same-city users receive higher relevance) and generates shared-root hooks ("You're both based in Tbilisi and originally from Kvareli"), but is never an exclusionary hard filter.
5. **No Creepy Tracking:** JESTER is self-declared. No background GPS surveillance or continuous tracking is performed.

## 3.7 Lifestyle System V1

JESTER establishes a dedicated **Lifestyle System** to capture everyday cadence and operational reality:

1. **Core Purpose:** Answers *"What is your everyday life like?"* — keeping daily rhythm, activity pace, and work reality strictly distinct from interests, values, and intent.
2. **Progressive 3-Question Snapshot:** Onboarding captures only 3 high-value signals (Daily Rhythm, Activity Pace, Work Style) via 1-tap segmented controls; 100% skippable.
3. **Sensitive Habit Isolation:** Substance use (drinking, smoking), living situations, and family structure are **strictly excluded from onboarding** and are managed progressively in profile settings.
4. **Cadence Micro-Badges:** Profiles render lifestyle as elegant, glassmorphic "Cadence" chips or human sentences, never an unappealing clinical checklist of checkboxes.
5. **Zero Moralizing:** The system and JESTER AI never judge, lecture, or evaluate personal habits. All lifestyle attributes are descriptive and non-judgmental.
6. **Practical Schedule Alignment:** In Discovery and Matching, lifestyle provides soft schedule harmony (e.g., mutual night owls or complementary pacing), never hard exclusionary filters.

## 3.8 Values System V1

JESTER defines a dedicated **Values System** to model guiding principles and life priorities:

1. **Core Purpose:** Answers *"What matters to you?"* — foundational ethical compass, decision-making priorities, and personal ideals.
2. **Strict Anti-Diagnosis Invariant:** Values must **never** become a psychological assessment or personality diagnosis. JESTER will never state: *"You are 85% independent"*. Values are human declarations, not medical verdicts.
3. **18 Canonical Values V1:** Curated across 5 thematic clusters (*Personal Direction*, *Intellectual & Creative*, *Relational & Ethical*, *Life Grounding*, *Inner Spirit*).
4. **Clean Selection Model:** Users pick **3 to 5 values** that guide them most, with an optional **1 Core Value** ("True North"). No 1–10 rating sliders. 100% skippable during onboarding.
5. **Guiding Compass UI:** Rendered as refined, starred micro-badges on social profiles, never clinical bar graphs or diagnostic percentages.
6. **Relational Synergy & Complementary Balance:** In Discovery and Matching, shared values highlight natural alignment, while differing values highlight dynamic balance (e.g. *Autonomy + Loyalty: Space to breathe with a secure tether*).
7. **No Moral Superiority:** All canonical values are treated with equal dignity; zero virtue grading.

## 3.9 Social Behavior System V1

JESTER defines a dedicated **Social Behavior System** to capture interaction preferences and energy mechanics:

1. **Core Purpose:** Answers *"How do you tend to be around people?"* — describing situational gathering comfort, social battery dynamics, and warm-up pacing without defining or diagnosing identity.
2. **Strict Anti-Diagnostic & Anti-Typing Invariant:** Social behavior must **never** assign psychological personality types (MBTI, Big 5, clinical labels) or box people into rigid archetypes (*"Alpha"*, *"Loner"*, *"Social Butterfly"*).
3. **Functional Battery Instead of Introvert/Extrovert Labels:** Replaces the static *"Introvert / Extrovert"* label trap with functional energy dynamics:
   - `recharge_solo` ("Recharges in Solitude — needs quiet downtime to refuel")
   - `recharge_social` ("Recharges Around People — draws vitality from shared presence")
   - `recharge_fluid` ("Context-Dependent — depends on the connection and mood")
4. **5 Canonical Dimensions (16 Options):** Gathering Scale, Social Battery, Warm-Up Dynamic, Planning Style, Comfort Zone.
5. **Rapid 3-Question Snapshot:** Onboarding captures 3 high-impact preferences (Gathering Scale, Social Battery, Warm-Up Dynamic) via 1-tap chips; 100% skippable. Zero rating sliders.
6. **Social Rhythm Micro-Badges:** Rendered as clean, glassmorphic chips under a dedicated "Social Rhythm" profile card with granular visibility toggles.
7. **Practical Meeting Intelligence:** In Discovery and Matching, social preferences suggest optimal meeting settings (e.g. quiet corner café vs. bustling event) and prevent social friction, never acting as hard exclusionary dealbreakers.

## 3.10 Communication System V1

JESTER defines a dedicated **Communication System** to model conversation dynamics, messaging format, and pacing:

1. **Core Purpose:** Answers *"How do you like to communicate?"* — describing conversational depth, narrative roles, messaging channels, and pacing expectations without diagnosing personality.
2. **Strict Anti-Labeling Invariant:** Rejects communication buzzwords and personality classifications (*"Deep Talker"*, *"Dry Texter"*, *"Bad Texter"*, *"Golden Retriever Communicator"*). Preferences are practical situational guidelines, not character verdicts.
3. **Zero Response-Time Surveillance:** JESTER strictly forbids reply-time timers, read-receipt clocks, and latency tracking. Texting speed is never measured as compatibility. Pacing is framed as personal rhythm (`active_banter`, `unhurried_thoughtful`, `relaxed_async`).
4. **4 Canonical Dimensions (14 Options):** Conversation Depth, Conversational Role, Messaging Medium, Conversational Pacing.
5. **Rapid 3-Question Snapshot:** Onboarding captures 3 core preferences (Conversation Depth, Conversational Role, Messaging Medium) via 1-tap chips; 100% skippable. Zero rating sliders.
6. **Communication Rhythm Micro-Badges:** Displayed as elegant, glassmorphic chips under a dedicated "Communication Rhythm" profile card with granular visibility controls.
7. **First-Conversation Intelligence:** Powers "The Insight Becomes the Invitation" by tailoring icebreakers to complementary conversational dynamics (e.g. Questioner + Storyteller, or mutual Deep Seekers).
8. **Decoupling from Synastry V1:** Strictly distinct from the mathematical Mercury aspect score $S_{\text{communication}}$. Astrology models cognitive dynamic tension; Communication V1 models practical interaction habits. They enrich each other but never overwrite each other.

## 3.11 Intent System V1

JESTER defines a dedicated **Intent System** to model current platform purpose and relational openness:

1. **Core Purpose:** Answers *"What are you looking for on JESTER right now?"* — capturing temporal motivation and relational openness without diagnosing personality or probing marital status.
2. **Intent is Temporal, Not Identity:** Intent reflects current life seasons (exploring, new friends, dating, activity partners, creative collaboration), whereas interests and values remain stable over years.
3. **Unified Discovery Without Mode Fracturing:** JESTER avoids the Bumble failure pattern (splitting into isolated Date/BFF/Bizz silos) and the Tinder trap (forcing romance on every connection). Intent is an explicit, transparent tag on profiles and discovery cards.
4. **7 Canonical Options Across 3 Categories:**
   - *Social & Personal:* `friendship` (New Friends), `dating_open` (Dating & Chemistry), `dating_serious` (Long-Term Relationship), `meaningful_chat` (Great Conversation).
   - *Activity & Practical:* `activity_partner` (Shared Activities & Outdoors), `collaboration` (Creative Collaboration).
   - *Exploratory:* `just_exploring` (Curious & Open-Minded).
5. **1 Primary + Max 2 Secondary Model:** Captures real-world nuance (e.g. Primary: Long-Term Relationship, Also open to: New Friends).
6. **Bilateral Discovery Partitioning:** Strictly separates incompatible non-overlapping intents (e.g. exclusive serious dating vs. exclusive platonic friendship) to eliminate harassment and mismatched expectations.
7. **Absolute Astrological Primacy Invariant:** Declared intent strictly governs astrological interpretation. JESTER AI must never project romantic or sexual destiny onto users who declared platonic intent, regardless of high planetary synastry scores.
8. **Contextual Connection Requests:** Bridges intent into action with transparent mutual intent indicators and optional 1-tap invitation reasons (`connection_reason`).

## 3.12 Prompts / Self-Expression System V1

JESTER defines a dedicated **Prompts / Self-Expression System** to capture authentic human voice and conversation hooks:

1. **Core Purpose:** Answers *"What does this person actually sound like?"* — preventing profiles from becoming flat sheets of tags and scores by exposing individual humor, warmth, quirks, and stories.
2. **Short Headline/About + Curated Prompts:** Pairs a compact 140-character headline with up to 3 curated prompts (250 chars max each) to minimize blank-box writing anxiety while maximizing conversational richness.
3. **6 Canonical Categories (24 Prompts):** Voice & Quirks, Curiosities & Rabbit Holes, Daily Reality, Connection & Interaction, Perspectives & Worldview, Action & Collaboration.
4. **Inline Conversation Entry Points:** Every prompt card features a 1-tap `[ 💬 Reply to this ]` action that quotes the prompt directly into a connection request note, effortlessly solving the cold-start messaging problem.
5. **Human Authorship Over Synthetic Generation:** JESTER AI can provide optional, user-requested polishing or idea sparks, but is strictly prohibited from auto-generating or hallucinating answers without explicit user approval.
6. **Profile Interweaving:** Prompts are woven strategically throughout the profile layout (between photos, interests, communication badges, and safe astrology) to ensure the experience feels human and dynamic.

## 3.13 Discovery Preferences System V1

JESTER defines a dedicated **Discovery Preferences System** to govern candidate generation, eligibility, and recommendation steering:

1. **Core Purpose:** Answers *"Who and what do you want JESTER to show you?"* — providing user agency over discovery without degrading JESTER into a commodified filter marketplace.
2. **Hard vs. Soft Boundary Invariant:**
   - *Hard Filters (Strict Exclusion):* Age bounds, target genders (for romantic intents), bilateral intent compatibility, account safety standing, discoverability status, and mutual block hiding.
   - *Soft Preferences (Relevance Boosts):* Location proximity (same city/country), shared & related interests, guiding values resonance, lifestyle schedule harmony, social rhythm pairing, and astrological synastry. Candidates outside soft preferences are never excluded; they receive intelligent ranking adjustments.
3. **Anti-Marketplace Dealbreakers Policy:** Restricts hard dealbreakers strictly to Age, Gender, and Intent. Strictly bans discriminatory filtering on physical attributes, zodiac signs, income, religion, ethnicity, or private lifestyle habits.
4. **Separation of Inbound Discoverability from Outbound Preferences:** `is_discoverable` (on `public.profiles`) controls whether others can find the user; `user_discovery_preferences` controls who the user sees. A user may browse discovery feeds while their profile remains hidden.
5. **DOB & Coordinate Privacy:** Exact birth dates are never exposed (only computed integer age is serialized). Zero GPS coordinates or live tracking data are ever collected or filtered on.
6. **Three-Tier Ranking Pipeline:** Tier 1 (SQL hard gates) -> Tier 2 (Multi-signal composite scoring) -> Tier 3 (JESTER Intelligence, diversity reranking, and rotation penalty).
7. **Explainability Over Percentage Scores:** JESTER strictly forbids percentage match scores (e.g., *"87% Match"*). Discovery cards display qualitative, human explanations (*"You both love photography and are looking for friendship in Tbilisi"*).

---

# 4. Interest System & Interest Graph V1

*(Authoritative Specification: [`docs/INTEREST_SYSTEM_V1_SPEC.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/INTEREST_SYSTEM_V1_SPEC.md))*

## 4.1 Core Principle: Shared Semantic Layer

Interests in JESTER are not decorative tags. They constitute a shared semantic layer connecting Profile, Onboarding, Discovery, Recommendation, People Grouping, Conversation Context, and JESTER AI.

The platform distinguishes:
1. **Declared Interests:** What a user explicitly chooses.
2. **Behavioral Affinity:** What is observed from downstream activity and engagement.
3. **Semantically Related Interests:** Connections modeled within the Interest Graph.
4. **Inferred Signals:** Algorithmic recommendation inputs.

> **A single interest must NEVER be treated as a complete personality definition.**  
> *(e.g., Photography ≠ "creative person". It contributes to recommendation only in combination with other signals).*

## 4.2 Structured Interest Taxonomy V1

The taxonomy encompasses **18 top-level categories** targeting **150–200 canonical interests**:
1. Travel & Exploring | 2. Food & Drink | 3. Music | 4. Movies & TV | 5. Books & Ideas | 6. Creative
7. Culture & Arts | 8. Sports & Fitness | 9. Nature & Outdoors | 10. Games | 11. Technology | 12. Science & Space
13. Astrology & Spirituality | 14. Wellness & Mindfulness | 15. Fashion & Style | 16. Animals & Pets | 17. Social & Nightlife | 18. Learning & Life

*UX Constraint:* The full taxonomy is strictly internal. Users are **never** presented with the entire taxonomy as an onboarding checklist.

## 4.3 Canonical Identity & Aliases

Interests have immutable canonical records rather than arbitrary free-text strings:
* `interest_categories` (id, name, slug, icon, sort_order, status)
* `interests` (id, category_id, name, slug, description, status)
* `interest_aliases` (interest_id, alias) — maps synonyms (e.g. `"movies"`, `"films"`, `"cinema"`) to a single canonical entity.

## 4.4 The Interest Graph (`interest_relations`)

Interests form a weighted graph with relationships (`sub_genre`, `semantic_peer`, `complementary`, `contextual`) and weights `[0.0, 1.0]`:
* *Photography* → Travel, Art, Design, Nature, Architecture, Film.
* *Travel* → Road Trips, Adventure, Nature, Food, Exploration.
* *Astrology* → Psychology, Spirituality, Tarot, Relationships, Self-discovery.

## 4.5 Dual-Layer Astrology Model

Astrology operates across two strictly independent platform layers:
1. **Interest Layer:** User selects *"Astrology"*, *"Birth charts"*, *"Synastry"* (means: *"I like discussing astrology"*).
2. **System Data Layer:** Birth date, time, and coordinates calculated deterministically via Swiss Ephemeris.

*Invariants:* Having natal data does not imply interest in astrology. Selecting astrology interest does not authorize the system to inject celestial jargon into ordinary human features.

## 4.6 Onboarding Interest Rules

1. **Optional Selection:** The user may skip interest selection entirely during onboarding.
2. **Exact Gating (5 / 5):** If entering interest selection, the user **must select exactly 5 Primary Interests** from a curated candidate pool of approximately **20 interests**.
3. **Continue Action:** Disabled until 5 items are chosen (or skipped).
4. **No Intensity Ratings:** Never ask users to rate interests (Love/Like) during onboarding.

## 4.7 Primary vs. Secondary Interests

* **Primary Interests:** The 5 prioritized onboarding selections (*"These are the things that feel most like me"*). Prominent profile visual hierarchy.
* **Secondary Interests:** Additional interests added later via profile editing (*"These are other things I'm into"*).
* Represented in `user_interests` (`primary` vs `secondary`).

## 4.8 Signature Interest

Following the 5 Primary selections, JESTER may optionally present a single skippable prompt:
> *"Which one could you talk about forever?"*

Marks one interest as `is_signature = true` for profile badge display and high-priority conversation starter generation.

## 4.9 Declared Interests vs. Behavioral Affinity

Tracked via `user_interest_affinity` (score, confidence, source: `declared`, `prompt`, `conversation`, `behavioral`, `inferred`).
* **Non-Overwrite Invariant:** Behavioral affinity scores never overwrite explicit user declarations.
* **Non-Judgment Invariant:** Behavioral affinity is an internal recommendation signal, never used to publicly label or judge the user.

## 4.10 Discovery Matching & Semantic Clusters

Discovery matching supports three relational tiers:
* **Shared:** Same canonical interest (*"You both love photography"*).
* **Related:** Semantically connected interests (*"You both love exploring — just differently"*).
* **Complementary:** Different interests with compatible social/communication energy (*"Different interests. Similar energy"*).

Internal **Interest Clusters** (*Explorers*, *Creatives*, *Thinkers*, etc.) and **Cross-Category Semantic Clusters** (*Coffee & Conversations*, *Let's Just Go Somewhere*, *Creative Chaos*, *Quiet but Interesting*) group multi-signal patterns without creating permanent personality labels.

## 4.11 Conversation Value vs. Discovery Value

* **Conversation Value:** Likelihood of sparking engaging dialogue (e.g. Photography, Coffee). Drives conversation starters and profile prompts.
* **Discovery Value:** Distinctiveness for partner recommendation (e.g. Niche philosophy). Parameterized separately in graph weights.

## 4.12 Telemetry & Learning Loop

Telemetry tracks selection, skips, search, profile discovery views, and conversation triggers to systematically iterate the taxonomy from `Taxonomy V1` to `Taxonomy V2`.

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

## 8.3 Person Interest Profile & Discovery Matching

When viewing another discoverable person's profile, the viewer accesses their public declared interests:
* **Primary Interests**: Prominently displayed (the 5 core identity anchors).
* **Signature Interest**: Elevated with a distinctive badge (*"Which one could you talk about forever?"*).
* **Secondary Interests**: Grouped separately or progressively disclosed.

Discovery matching between two discoverable users evaluates three relational tiers:
1. **Shared**: Explicit mutual canonical interest (e.g., both love Photography).
2. **Related**: Graph-connected semantic neighbors (e.g., Photography and Travel).
3. **Complementary**: Different declared interests paired with compatible social energy or communication preferences.

*Multi-Signal Invariant:* Recommendation and discovery candidate grouping utilize internal multi-signal **Interest Clusters** (*Explorers*, *Creatives*, *Thinkers*, etc.) and **Cross-Category Semantic Clusters** rather than flat single-tag comparisons.

## 8.4 Person Location Profile & Discovery Relevance

When viewing another discoverable person's profile or discovery card:
* **Current Location:** Displayed prominently as `📍 Tbilisi` (or `📍 Berlin, Germany` if international).
* **Hometown / Origin:** Displayed as `🏡 From Kvareli` if the user has enabled `hometown_visible = true`. Hidden if disabled.
* **Discovery Relevance Boost:** Candidates residing in the same current city receive an organic soft relevance boost to facilitate real-world meeting potential.
* **Shared Origin Hooks:** Candidates sharing a hometown root or regional heritage surface contextual observations (e.g. *"You're both in Tbilisi and originally from Kvareli"*).
* **Privacy Boundary:** Exact geographic coordinates (`latitude`, `longitude`) are strictly internal and never serialized on discovery cards or profiles.

## 8.5 Person Lifestyle Profile & Cadence Alignment

When viewing another discoverable person's profile or discovery card:
* **Cadence Presentation:** Displayed as elegant, non-clinical micro-badges (`🌙 Night Owl`, `⚡ High Pace`, `💻 Remote`, `🐕 Has a Dog`).
* **Schedule Synergy:** Highlights shared operational realities (e.g., mutual night owls or remote work flexibility) to spark practical meeting ideas.
* **Habit Privacy:** Sensitive habits (drinking, smoking, living situation) render only if explicitly set to public by the user.
* **Soft Alignment:** Lifestyle compatibility serves as contextual conversational sparks, never as hard exclusionary filters.

## 8.6 Person Values Profile & Philosophical Alignment

When viewing another discoverable person's profile or discovery card:
* **Guiding Compass Presentation:** Displayed as refined micro-badges, elevating the user's Core Value (`⭐ Curiosity (Core)`) alongside guiding principles (`[ Growth ]`, `[ Honesty ]`, `[ Autonomy ]`).
* **Shared Resonance:** Highlights natural philosophical alignment when users share core values.
* **Complementary Polarity:** Surfaces constructive balances (e.g. *Autonomy + Loyalty*, *Adventure + Stability*) with signature JESTER wit and warmth.
* **Zero Psychological Diagnosis:** Never presents diagnostic scores, virtue rankings, or personality percentages.

## 8.7 Person Social Behavior Profile & Social Dynamics in Discovery

When viewing another discoverable person's profile or discovery card:
* **Social Rhythm Presentation:** Displayed as compact, glassmorphic chips under "Social Rhythm" (`[ ☕ One-on-One ]`, `[ 🔋 Recharges Solo ]`, `[ 👀 Observant First ]`, `[ ⚡ Spontaneous ]`).
* **Symmetric Harmony:** Surfaces shared social comfort (e.g. mutual one-on-one preference or mutual solo rechargers: *"Both need quiet downtime after socializing — zero pressure, zero guilt"*).
* **Complementary Interplay:** Highlights dynamic balance (e.g. initiator + observer: *"One breaks the ice, one reads the room — natural conversational flow"*).
* **Meeting Intelligence:** JESTER AI suggests ideal low-pressure first hangout contexts based on mutual comfort zones.
* **Granular Privacy:** Individual attributes render only if not toggled hidden by the user.

## 8.8 Person Communication Profile & First-Conversation Intelligence

When viewing another discoverable person's profile or discovery card:
* **Communication Rhythm Presentation:** Rendered as glassmorphic chips under "Communication Rhythm" (`[ 🌊 Deep & Meaningful ]`, `[ 💡 Exchanges Ideas ]`, `[ 🎙️ Voice Notes OK ]`, `[ ⏳ Unhurried Pace ]`).
* **Symmetric Depth:** Highlights shared conversational depth (e.g. *"Both skip the shallow small talk — conversations here get real quickly"*).
* **Complementary Dynamics:** Identifies natural flow (e.g. Question-Asker + Storyteller: *"One draws stories out, one loves narrating vivid experiences"*).
* **Channel & Pacing Comfort:** Informs conversational initiation (e.g. *"Voice notes are welcome here"* or *"Prefers an unhurried, thoughtful rhythm"*).
* **Zero Scorekeeping:** Never presents reply-time latency, read-receipt timers, or communication scores.

## 8.9 Person Intent Profile & Discovery Partitioning

When viewing another discoverable person's profile or discovery card:
* **Looking For Presentation:** Displayed prominently near top of profile (`[ 👥 New Friends (Main) ]`, `[ 🧗 Activity Partner ]`, `[ 🔍 Just Exploring ]`).
* **Symmetric Match:** Users sharing identical primary intent receive a direct relevance boost (e.g. *"Both here for new friends and social circle"*).
* **Aligned Openness:** Users with overlapping secondary openness surface bridge invitations (e.g. *"Alexandre is primarily dating, but both are open to outdoor activities"*).
* **Bilateral Discovery Partitioning:** Eliminates romantic/platonic mismatched feeds: users seeking exclusively serious dating are never presented to users seeking exclusively platonic friendship or collaboration unless a secondary bridge or `just_exploring` exists.
* **Astrological Framing Guardrail:** Astrological synastry is strictly framed within declared intent boundaries; JESTER AI never suggests romantic destiny to platonic seekers.

## 8.10 Person Prompts Profile & Conversational Hooks

When viewing another discoverable person's profile:
* **Interwoven Profile Presence:** Prompts appear interwoven between photo, interests, lifestyle, and astrology cards rather than isolated at the bottom.
* **Inline Connection Hooks:** Every prompt card includes an interactive `[ 💬 Reply to this ]` action that quotes the prompt directly into a connection request note.
* **Voice & Texture Discovery:** Prompts expose unique humor, quirks, and conversational tone, turning passive reading into active engagement.
* **Automated Safety Protection:** All public prompt answers pass automated PII detection, hate-speech filtering, and XSS sanitization prior to publication.

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

## 9.4 Connection Context & Optional Invitation Reason

To fulfill the axiom *"The insight becomes the invitation"*, connection requests bridge declared intent:
* **Mutual Shared Intent:** The request modal surfaces shared intent alignment (e.g. *"You're both open to shared activities"*).
* **Optional Context Reason (`connection_reason`):** Senders may attach an optional 1-tap invitation tag (`coffee_meet`, `great_chat`, `shared_activity`, `creative_project`, `mutual_vibe`).
* **Transparent Reception:** Recipients see the context immediately, eliminating cold-start hesitation and ambiguity.

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

The system derives topics likely to foster engaging, productive interaction between two people.

In JESTER V1, topics are synthesized from two complementary inputs:
1. **Deterministic Synastry Signals**: Astrological aspect geometries (e.g. Mercury-Jupiter dynamic fueling expansive philosophical curiosity).
2. **Interest Graph Shared & Related Nodes**: Topics reflecting explicit mutual interests (Shared) or bridge topics (Related) parameterized by high Conversation Value.

Examples: travel, cinema, philosophy, books, creative work, technology, adventure, local culinary culture.

---

# 22. Conversation Starters

JESTER generates witty, situational conversation starters to eliminate cold-start messaging friction.

Starters synthesize:
1. **Astrological Dynamic Tension**: Interpersonal dynamics derived from Synastry aspects.
2. **Interest Graph Anchors**: Leveraging the users' declared Primary Interests, Signature Interest, and mutual graph neighbors with high **Conversation Value** (e.g. Photography, Coffee).
3. **Communication Role & Depth Pairing**: Tailoring starters to the users' declared conversational roles (e.g. Questioner + Storyteller generates a narrative question prompt; mutual Deep Seekers skip small talk).
4. **Intent & Purpose Framing**: Framing conversation starters to match mutual declared intent (e.g. suggesting outdoor trail outings for mutual `activity_partner` seekers, intellectual debates for `meaningful_chat`, or romantic chemistry for mutual `dating` seekers).

Conversation starters are a downstream interpretation layer. They must never retroactively modify the deterministic numerical compatibility score.

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

The AI layer is responsible for translating structured astrological information and Interest Graph semantic context into natural-language JESTER interpretations.

Architecture:

```text
Astrological Data + Interest Graph Context
       ↓
Structured Signals & Shared Semantic Anchors
       ↓
Interpretation Context
       ↓
JESTER AI
       ↓
Natural Language
```

The AI interprets data; it does not replace the deterministic calculation engine or alter the interest graph topology.

### AI Context Invariants:
1. **Never Stereotype from a Single Interest**: JESTER AI must **never** treat a single interest as a complete personality definition (e.g. `Photography` ≠ "creative soul").
2. **Behavioral Affinity is Non-Judgmental**: Internal behavioral affinity scores are recommendation inputs; they must **never** be used by JESTER AI to publicly label, judge, or pigeonhole the user.
3. **Conversational Anchoring**: Declared Primary Interests and Signature Interests serve as conversational icebreakers, not psychological verdicts.
4. **Location & Origin Warmth Without Creepiness**: JESTER AI uses Current City and Hometown as natural conversational bridges (e.g. shared roots, regional context), never as deterministic stereotypes or stalkerish proximity remarks. Raw coordinates and device sensor logs are strictly barred from AI prompts.
5. **Lifestyle Context Without Moralizing**: JESTER AI uses daily rhythm, activity pace, and work reality for empathetic schedule harmony (e.g. nocturnal camaraderie, remote coffee work), never for moralizing, health lectures, or judgment on personal habits. Private habits (drinking, smoking, living situation) are strictly omitted from prompt context if hidden.
6. **Values Context Without Diagnostic Grading**: JESTER AI uses shared values and polarities for philosophical depth and conversational warmth, never for psychological diagnoses, virtue grading, or moral superiority claims. All canonical values are treated with equal dignity.
7. **Social Behavior Context Without Box-Labelling**: JESTER AI uses gathering scale, social battery, and warm-up dynamics to suggest comfortable first meeting venues and empathetic pacing, strictly never calling a user "antisocial", "introverted recluse", "attention-seeking", or assigning MBTI/pop-psychology personality types.
8. **Communication Context Without Response-Time Surveillance**: JESTER AI uses declared conversation depth, role pairing, and messaging format to craft natural starters and set healthy expectations, strictly never tracking or commenting on reply latency, scorekeeping response times, or diagnosing communication flaws ("dry texter"). Message bodies are never parsed for psychological profiling.
9. **Intent Primacy & Anti-Romantic Assumption Invariant**: JESTER AI must strictly respect declared intent boundaries. Astrological chemistry (e.g. Venus-Mars aspects) must **never** be interpreted as romantic destiny or sexual pursuit if either participant has declared platonic friendship or collaboration intent. Declared user intent strictly governs astrological framing.
10. **Prompt Context Without Psychological Stereotyping**: JESTER AI treats published prompt answers as authentic self-expression and contextual conversation anchors, **never as clinical psychological proof or moral diagnostic verdicts** (e.g. humorous exaggeration in a prompt is never converted into an antisocial diagnosis).

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
* canonical interest taxonomy and graph relationships;
* data validity.

### AI layer

Responsible for:

* explanation;
* narrative;
* contextualization;
* conversational language;
* JESTER personality;
* natural-language interpretation.

The AI must not invent underlying astronomical facts or override canonical interest mappings.

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
2. Profile & User Model domain separation
3. Birth data & atomic onboarding
4. Interest System & Interest Graph V1 (Taxonomy, 5/5 Primary onboarding, graph relations)
5. Natal astrology (Swiss Ephemeris)
6. People & Discovery matching (Shared, Related, Complementary)
7. Connections
8. Real Synastry (Synastry V1 engine)
9. Compatibility score & 4 dimensions
10. Compatibility signals
11. Direct messaging

## Tier 2 — Core Enhancement

12. Compatibility topics (Synastry + Interest Graph Conversation Value)
13. Conversation starters (Relational tension + Interest anchors)
14. Daily astrology
15. JESTER AI interpretation (with non-stereotyping interest context)
16. Notifications
17. Realtime interaction

## Tier 3 — Expansion

18. Extended celestial bodies
19. Advanced astrological points
20. Group conversations
21. Push notifications
22. Advanced daily transits

---

# 32. V1 Functional Relationship

The central JESTER loop is:

```text
CREATE SELF (Birth Data + Optional 5 Primary Interests)
    ↓
UNDERSTAND SELF (Personal Astrology & Safe Profile)
    ↓
DISCOVER PEOPLE (Interest Graph Matching + Safe Astrology)
    ↓
CONNECT
    ↓
COMPARE (Deterministic Synastry V1)
    ↓
UNDERSTAND THE RELATIONSHIP
    ↓
START A CONVERSATION (Interest Anchors + Synastry Dynamics)
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

