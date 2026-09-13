# JESTER — Lifestyle System V1
## Product, UX, Data Architecture & Behavioral Intelligence Specification

---

## 1. Product Purpose & Philosophy

JESTER is a **People Discovery and Relationship Intelligence** platform. To help people understand each other and build meaningful connections, the system must comprehend how a person actually lives their everyday life.

There is a fundamental product distinction between what a person likes and how a person lives:
> **Interests answer:** *"What are you into?"* (Topics, passions, intellectual curiosities, creative pursuits)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, physical cadence, work environment, living reality, habits)

These two dimensions are completely distinct:
- **Photography** = *Interest* (topic affinity)
- **Working Remotely** = *Lifestyle* (work reality)
- **Coffee** = *Interest* (beverage passion)
- **Night Owl** = *Lifestyle* (circadian rhythm)
- **Hiking** = *Interest* (activity preference)
- **High Physical Pace** = *Lifestyle* (overall daily velocity)
- **Dog Lover** = *Interest* (affinity for animals)
- **Dog Owner** = *Lifestyle* (daily cohabitation and responsibility)
- **Wanting Children** = *Values & Life Direction* (future family architecture)
- **Dating** = *Intent* (relational objective)

### Core Operating Axioms:
1. **Schema Now, Collection Later:** The database schema and domain model are designed broadly from day one to support rich lifestyle intelligence. However, onboarding is intentionally lightweight and non-interrogative.
2. **Progressive Onboarding + Voluntary Disclosure:** Never present a 20-question lifestyle questionnaire. Onboarding captures only a 3-question "Life Cadence Snapshot" and allows the user to skip entirely.
3. **No Moral Shaming or Health Lecturing:** Lifestyle data is descriptive, never evaluative. JESTER never judges sleep hours, substance use, or work styles.
4. **Context Over Checklists:** Public profiles must never degenerate into a sterile checkbox list of personal habits. Lifestyle is presented as fluid, human life cadence badges.

---

## 2. Lifestyle vs. Other User-Data Domains (The Master Separation Matrix)

JESTER strictly prevents domain contamination. The table below governs where ambiguous user attributes must be filed:

| Attribute / Concept | Correct Domain | Invariant & Distinction |
| :--- | :--- | :--- |
| **Photography, Cinema, Astrophotography** | `Interests` | Subject matter passion; not a daily routine. |
| **Remote / Hybrid / On-Site Work** | `Lifestyle` | Operational structure of the work day. |
| **Early Bird / Night Owl** | `Lifestyle` | Circadian rhythm and active waking hours. |
| **High Energy / Balanced / Slow Pace** | `Lifestyle` | Daily physical velocity and movement cadence. |
| **Dog Owner ("Has a dog")** | `Lifestyle` | Daily household living reality and scheduling anchor. |
| **Lover of Dogs ("Loves dogs")** | `Interests` | Emotional/topical affinity; user may not own a pet. |
| **Introvert / Extrovert / Ambivert** | `Social Behavior` | Internal battery recharge style; NOT a lifestyle habit. |
| **Prefers 1-on-1 vs Large Parties** | `Social Behavior` | Social setting preference; NOT lifestyle cadence. |
| **Fast Texter / Voice Note Enthusiast** | `Communication` | Channel and latency preference for messaging. |
| **Deep Talks vs Quick Banter** | `Communication` | Interaction depth preference. |
| **Has Children ("Parent")** | `Lifestyle / Household` | Daily living reality and time commitment. |
| **Wants Children / Family Plans** | `Values & Life Direction`| Long-term relational alignment; NOT everyday routine. |
| **Casual / Long-term Relationship** | `Intent` | What the user is seeking on JESTER right now. |
| **Spiritual / Agnostic / Secular** | `Values` | Philosophical and existential grounding. |
| **Drinking / Smoking Habits** | `Lifestyle (Sensitive)` | Personal consumption habits; strictly user-controlled. |
| **Lives Alone / Roommates / Family** | `Lifestyle (Household)` | Living structure; private/toggleable by default. |

---

## 3. Lifestyle Taxonomy V1

JESTER defines eight clear lifestyle dimensions for V1:

### 3.1 Daily Rhythm (Circadian Cadence)
Captures when the person is alert, productive, and social:
- `early_bird`: Wakes early, morning momentum, sleeps before midnight.
- `night_owl`: Thrives late at night, evening focus, nocturnal energy.
- `flexible_rhythm`: Adaptable sleep/wake schedule depending on demands.
- `structured_routine`: Highly predictable daily timetable and habits.
- `spontaneous_rhythm`: Fluid, unpredictable daily timing driven by whim.

### 3.2 Activity Pace (Physical Velocity)
Captures everyday physical movement and restlessness:
- `high_velocity`: Constant motion, workouts, restless energy (*"Always on the go"*).
- `balanced_pace`: Regular movement combined with intentional quiet time.
- `relaxed_pace`: Calm, slow, unhurried (*"Thrives in low-pressure calm"*).

### 3.3 Work Style (Professional Cadence)
Captures the operational reality of the user's livelihood:
- `remote`: Work from home / digital nomad; high schedule autonomy.
- `hybrid`: Split between office and home base.
- `on_site`: Physical office, clinic, studio, or facility presence.
- `freelance_contract`: Project-based, variable rhythms.
- `entrepreneur_founder`: Immersive, non-traditional hours.
- `student`: Academic schedule with seasonal exam peaks.
- `shift_based`: Rotating or non-standard day/night shifts.

### 3.4 Social Cadence (Everyday Outing Frequency)
*Distinction: Captures lifestyle outing frequency, leaving internal social personality to Social Behavior.*
- `frequently_social`: Out several nights a week; seeks dynamic environments.
- `moderately_social`: 1–2 social outings weekly; balances home and events.
- `home_focused`: Prefers spending evenings at home with occasional outings.

### 3.5 Pets & Household Animals
Captures physical pet cohabitation (distinct from animal interests):
- `has_dog`: Lives with a canine companion (daily walking schedule).
- `has_cat`: Lives with feline companion.
- `has_multiple_pets`: Lives with multiple animals.
- `has_other_pets`: Birds, reptiles, fish, etc.
- `pet_free`: Does not live with animals (may still love them).

### 3.6 Living Situation (Sensitive Household Context)
*Classification: Private by default; user-controlled toggle.*
- `lives_alone`: Independent household.
- `lives_with_roommates`: Shared flat or co-living space.
- `lives_with_family`: Multigenerational or family household.
- `lives_with_partner`: Domestic cohabitation.

### 3.7 Sensitive Substances: Drinking & Smoking
*Classification: Optional, private or public toggle; strictly non-judgmental.*
- **Drinking:**
  - `never`: Does not drink alcohol (includes sober lifestyle).
  - `socially`: Drinks occasionally in social settings.
  - `regularly`: Enjoys wine/cocktails with meals or weekends.
- **Smoking:**
  - `never`: Non-smoker.
  - `socially`: Occasional social smoker.
  - `regularly`: Daily smoker / vaper.
  - `trying_to_quit`: Active cessation process.

---

## 4. Onboarding UX: The 3-Question "Life Cadence Snapshot"

To respect the user's time and avoid questionnaire fatigue, onboarding isolates **only the 3 highest-value lifestyle signals**:

```text
┌────────────────────────────────────────────────────────┐
│                   YOUR LIFE CADENCE                    │
│                                                        │
│   A few quick signals about how you move through life. │
│                                                        │
│   YOUR DAILY RHYTHM                                    │
│   [ 🌅 Early Bird ]  [ 🌙 Night Owl ]  [ ⚖️ Flexible ] │
│                                                        │
│   YOUR EVERYDAY PACE                                   │
│   [ ⚡ Always Moving ] [ 🌿 Balanced ] [ ☕ Relaxed ]  │
│                                                        │
│   YOUR WORK REALITY                                    │
│   [ 💻 Remote ]   [ 🔄 Hybrid ]   [ 🏢 On-Site ]       │
│   [ 🎓 Student ]  [ 🚀 Entrepreneur ]                  │
│                                                        │
│   [  Skip for now  ]                     [  Continue ] │
└────────────────────────────────────────────────────────┘
```

### Why These Three Signals Were Chosen for Onboarding:
1. **Rhythm:** Immediately surfaces late-night vs. morning conversational compatibility.
2. **Pace:** Prevents burnout mismatches between hyper-active and deeply calm individuals.
3. **Work Reality:** Signals daytime availability, remote coffee-work synergy, and geographic flexibility.

### Sensitive Items Excluded from Onboarding:
- **Drinking, Smoking, Living Situation, and Children are STRICTLY EXCLUDED from onboarding.** 
- They can be added progressively later in profile settings.

---

## 5. Public Profile Presentation: Cadence Pills, Not Checklists

JESTER rejects the clinical "dating app checklist" UI where profiles display 10 checked boxes.

```text
               ┌─────────────────────────────────────────────────┐
               │           PUBLIC PROFILE PRESENTATION           │
               ├─────────────────────────────────────────────────┤
               │  Alexandre, 28                                  │
               │  📍 Based in Tbilisi · 🏡 From Kvareli          │
               │                                                 │
               │  CADENCE                                        │
               │  [ 🌙 Night Owl ] [ ⚡ High Pace ] [ 💻 Remote ]│
               │  [ 🐕 Has a Dog ]                               │
               │                                                 │
               │  HABITS (If enabled by user)                    │
               │  [ 🍷 Social Drinker ] [ 🚭 Non-Smoker ]        │
               └─────────────────────────────────────────────────┘
```

### Visual Architecture Rules:
1. **Cadence Micro-Badges:** Lifestyle signals appear as compact, elegant chips under a clean "Cadence" header.
2. **Integrated Human Sentence Option:** For compact discovery cards, lifestyle merges into an organic natural language line:  
   *“Night owl working remotely with high-energy pace.”*
3. **Granular Privacy Toggles:** The user can toggle visibility on any lifestyle attribute independently.
4. **No Empty State Clutter:** Undeclared attributes simply do not render; no placeholder blanks like *"Drinking: Not specified"*.

---

## 6. Lifestyle in Discovery & Relationship Intelligence

Lifestyle acts as an everyday **operational alignment and synergy signal**:

$$\text{Discovery Relevance} = f(\text{Human Profile}, \text{Interest Graph}, \text{Intent}, \mathbf{Lifestyle}, \text{Location}, \text{Astrology Synergy})$$

### 6.1 Rhythm Synergy vs. Dynamic Contrast
- **Shared Nocturnal Cadence:** Two night owls receive a playful discovery hook:  
  *“You're both nocturnal creatures — expect late-night conversations.”*
- **Complementary Contrast:** An early bird and a night owl are framed with warmth:  
  *“Different rhythms: one owns the sunrise, one owns the night.”*

### 6.2 Activity Pace Compatibility
- Two high-velocity users receive mutual activity highlights (*"High-pace synergy for spontaneous outings"*).
- A high-pace user and a relaxed user are highlighted as grounding influences (*"Dynamic energy meets calming presence"*).

### 6.3 Soft Signals, Never Dealbreaker Walls in V1
- In V1, lifestyle attributes are **soft recommendation boosts and conversational context**, not rigid exclusionary filters.
- A user will not be hidden from discovery simply because one works hybrid and the other works remote.

---

## 7. JESTER AI Context & Ethical Invariants

The JESTER AI interpretation layer receives sanitized lifestyle tokens:

```json
{
  "viewer": {
    "rhythm": "night_owl",
    "activity_pace": "high_velocity",
    "work_style": "remote",
    "pets": ["has_dog"],
    "drinking": "socially"
  },
  "target": {
    "rhythm": "night_owl",
    "activity_pace": "balanced_pace",
    "work_style": "remote",
    "pets": ["has_cat"],
    "drinking": "never"
  },
  "lifestyle_alignment": {
    "rhythm_match": "shared_nocturnal",
    "pace_balance": "complementary",
    "work_synergy": "both_remote",
    "pet_dynamic": "dog_and_cat"
  }
}
```

### Critical AI Behavioral Invariants:
1. **Zero Moralizing or Health Lecturing:** JESTER AI must **never** judge a user’s lifestyle choices, sleep schedule, smoking habits, or alcohol consumption (e.g. never generate *"You should sleep earlier"* or *"Drinking is unhealthy"*).
2. **Contextual Sparks, Not Judgments:** Lifestyle is used to explain real-life scheduling harmony (e.g. *"Since you're both working remotely with flexible hours, afternoon coffee breaks actually work"*).
3. **Respect for Sensitive Habit Suppression:** If a user has marked drinking, smoking, or living situation as private, those tokens are **completely omitted from AI prompt context**.

---

## 8. Database Schema Specification (Architecture Blueprint)

```sql
-- ============================================================================
-- 1. CANONICAL LIFESTYLE CATEGORIES & OPTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.lifestyle_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'daily_rhythm', 'work_style', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.lifestyle_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.lifestyle_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'night_owl', 'early_bird', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    badge_icon VARCHAR(30),                    -- 'moon', 'sun', 'laptop'
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. USER LIFESTYLE TABLE (Normalized Profile Extension)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_lifestyle (
    user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    daily_rhythm VARCHAR(40),                  -- references lifestyle_options.slug
    activity_pace VARCHAR(40),                 -- references lifestyle_options.slug
    work_style VARCHAR(40),                    -- references lifestyle_options.slug
    social_cadence VARCHAR(40),                -- references lifestyle_options.slug
    pet_status VARCHAR(40),                    -- 'has_dog', 'has_cat', 'no_pets', etc.
    living_situation VARCHAR(40),              -- 'alone', 'roommates', 'family', etc.
    drinking_habit VARCHAR(40),                -- 'never', 'socially', 'regularly'
    smoking_habit VARCHAR(40),                 -- 'never', 'socially', 'regularly'
    visibility_flags JSONB NOT NULL DEFAULT '{
        "daily_rhythm": true,
        "activity_pace": true,
        "work_style": true,
        "social_cadence": true,
        "pet_status": true,
        "living_situation": false,
        "drinking": true,
        "smoking": true
    }',
    source VARCHAR(30) NOT NULL DEFAULT 'declared',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_lifestyle_rhythm ON public.user_lifestyle(daily_rhythm);
CREATE INDEX IF NOT EXISTS idx_user_lifestyle_work ON public.user_lifestyle(work_style);
```

---

## 9. API Specification & Safe DTOs

### 9.1 Safe Public Profile Serialization
Public profiles serialize a sanitized, user-controlled lifestyle block:

```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Alexandre",
  "lifestyle": {
    "daily_rhythm": { "slug": "night_owl", "label": "Night Owl", "icon": "moon" },
    "activity_pace": { "slug": "high_velocity", "label": "Always Moving", "icon": "zap" },
    "work_style": { "slug": "remote", "label": "Remote", "icon": "laptop" },
    "pet_status": { "slug": "has_dog", "label": "Has a Dog", "icon": "dog" },
    "drinking": { "slug": "socially", "label": "Socially", "icon": "wine" },
    "smoking": { "slug": "never", "label": "Non-Smoker", "icon": "slash" }
  }
}
```
*Note: If `visibility_flags.living_situation` is false (default), `"living_situation"` is omitted from the public response.*

---

## 10. Scope Boundary: V1 vs. Future Roadmap

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **3-Question Cadence Onboarding** | ✅ | — | Quick, low-friction signal capture |
| **Rhythm, Pace, Work Style, Pets** | ✅ | — | Essential daily life context |
| **Granular Visibility Flags** | ✅ | — | Privacy protection for sensitive habits |
| **Soft Discovery Alignment Boost** | ✅ | — | Practical meeting & schedule synergy |
| **AI Schedule Harmony Starters** | ✅ | — | Witty observations about daily rhythms |
| **Hard Lifestyle Dealbreaker Filters** | ❌ | 🔮 | Requires larger user pool to prevent empty feeds |
| **Behavioral Lifestyle Inference** | ❌ | 🔮 | Inferring bedtime from message timestamps |
| **Calendar / Availability Integration**| ❌ | 🔮 | High complexity; deferred to Post-V1 |
| **Dietary Lifestyle (Vegan, Keto, etc.)**| ❌ | 🔮 | Can be handled via Interest Graph in V1 |

---

## 11. Lifestyle System V1 — Final Decisions Summary

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Product Role** | Answers *"What is your everyday life like?"* — decoupled from Interests, Values, and Intent. |
| **Onboarding Strategy** | 3-question quick snapshot (Rhythm, Pace, Work style). 100% skippable. |
| **Sensitive Attributes** | Living situation, drinking, smoking strictly excluded from onboarding; available in profile edit. |
| **Privacy & Visibility**| Granular per-attribute visibility toggles via `visibility_flags` JSONB. Living situation private by default. |
| **Public Profile UI** | Elegant Cadence micro-badges; never a laundry list of checkboxes. |
| **Discovery Role** | Soft relevance boost and conversational observations (e.g. mutual night owls). No hard filters in V1. |
| **Database Model** | Dedicated normalized table `public.user_lifestyle` referencing canonical `lifestyle_options`. |
| **AI Context** | Ingests rhythm and cadence for conversational warmth; strictly prohibited from moralizing or lecturing. |
| **Security Policy** | Standard RLS: users manage own lifestyle row; private attributes suppressed from public DTOs. |
| **Future Scope** | Hard lifestyle dealbreaker filters, calendar integration, behavioral inference. |
