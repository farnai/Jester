# JESTER — Prompts / Self-Expression System V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

---

## 1. Product Purpose & Philosophy

All previous JESTER data domains systematically describe structured aspects of a human being:
> **Identity answers:** *"Who are you?"* (Name, age, cultural roots, birth parameters)  
> **Location answers:** *"Where are you based and where are you from?"* (Current residency, regional heritage)  
> **Interests answer:** *"What are you into?"* (Topics, intellectual passions, creative crafts)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, activity pace, work reality, living context)  
> **Values answer:** *"What matters to you?"* (Guiding principles, moral compass, life priorities)  
> **Social Behavior answers:** *"How do you tend to be around people?"* (Gathering scale, social battery, setting comfort)  
> **Communication answers:** *"How do you like to communicate?"* (Conversation depth, dynamic role, format, pacing)  
> **Intent answers:** *"What are you looking for on JESTER right now?"* (Current connection purpose, relational openness)  
> **Prompts answer:** *"What does this person actually sound like?"* (Voice, wit, quirks, perspectives, conversation hooks)

### The Core Problem Prompts Solve:
Without open-ended self-expression, a user profile risks becoming an algorithmic database sheet consisting entirely of:
- category tags
- glassmorphic badges
- compatibility percentages
- personality labels

Prompts represent the **human layer** of JESTER.

### Governing Axioms:
1. **People First. Signals Second. Scores Last:** Self-expression makes the individual human visible before algorithmic calculations do.
2. **Prompts are Conversation Hooks, Not Essays:** A prompt exists primarily to give another person an immediate, effortless, natural reason to start a conversation.
3. **Show, Don't Just Tell:** Structured data says `Cinema` or `Night Owl`. A prompt says: *"I will rewatch 1970s Italian crime thrillers at 2 AM until my eyes hurt."*
4. **Differentiation:** Two people may possess identical interests, values, and astrological signs, yet possess completely different comedic timing, warmth, or creative eccentricity. Prompts expose that human difference.
5. **Human Authorship Over Synthetic Generation:** Prompts belong to the user's authentic voice. JESTER AI may offer polishing or brainstorming assistance upon explicit request, but must **never** manufacture or hallucinate a fake personality for the user.

---

## 2. Product Role of Prompts

Prompts in JESTER perform five high-leverage product functions:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        THE 5 ROLES OF PROMPTS                          │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Voice & Texture: Demonstrates humor, irony, warmth, or ambition     │
│ 2. Contextualization: Brings flat structured tags to life              │
│ 3. Differentiation: Reveals unique personality between similar profiles│
│ 4. Frictionless Starters: Provides obvious 1-tap conversation openers  │
│ 5. Safe AI Grounding: Provides authentic user-authored context for AI  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Voice & Texture:** Demonstrates whether a person communicates with dry wit, poetic observation, exuberant enthusiasm, or calm clarity.
2. **Contextualization:** Connects abstract preferences to concrete life stories.
3. **Differentiation:** Prevents homogenization across users sharing common tags.
4. **Frictionless Starters:** Solves the #1 dilemma of social discovery: *"What do I say first?"* Every prompt acts as an interactive conversation entry point.
5. **Safe AI Grounding:** Supplies JESTER AI with verified, user-approved self-descriptions to anchor conversation starters and relational summaries without hallucinating facts.

---

## 3. Architecture Decision: Short About/Headline + Prompts

JESTER evaluated three architectural approaches for free-form profile expression:

### Evaluated Options:
- **Option A (Full Bio + Prompts):** Forces users to stare at an intimidating blank "About Me" text box, leading to generic clichés (*"Just ask"*, *"Living life to the fullest"*), followed by repetitive prompts. Result: High user friction, poor quality.
- **Option B (Prompts Only):** Strips away any high-level anchor. Observers must piece together identity solely from disparate prompt fragments without an initial headline.
- **Option C (Short Headline/About + Curated Prompts) — SELECTED FOR V1:**
  - **Short Headline / Bio:** Max 140 characters. A rapid, orienting self-summary (e.g. *"Architect & analog film shooter based in Sololaki. Coffee fanatic."*).
  - **Prompts:** 2 to 3 structured prompt cards answering curated questions (max 250 characters each).
  - **Result:** Minimal writing pressure, clear identity orientation, and rich conversational depth.

---

## 4. Prompt Taxonomy V1 (6 Categories, 24 Curated Prompts)

JESTER avoids generic dating-app prompts (*"Swipe right if..."*). Instead, prompts are calibrated to JESTER's core brand identity: **Witty, Observant, Relational, and Human**.

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            JESTER PROMPT TAXONOMY V1                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Voice, Quirks & Levity (Comedic timing, harmless idiosyncrasies)                    │
│    • unnecessary_hill    A completely unnecessary hill I will die on...                │
│    • irrational_obsession My most irrational everyday obsession...                     │
│    • useless_talent      My most useless hidden talent...                              │
│    • friends_describe    My friends would probably describe me as...                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Curiosities & Rabbit Holes (Intellectual play, deep passions)                       │
│    • talk_forever        I could talk about ___ for hours without stopping...          │
│    • recent_rabbit_hole  The rabbit hole I recently fell into...                       │
│    • question_asking     A question I never get tired of asking people...              │
│    • mind_changed        Something I completely changed my mind about...               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Daily Reality & Cadence (Everyday life, routines, quiet moments)                    │
│    • ordinary_day        A perfect ordinary day looks like...                          │
│    • leave_the_house     The easiest way to convince me to leave the house...          │
│    • sunday_routine      My ideal, unhurried Sunday...                                 │
│    • evening_winddown    My favorite way to spend an unplanned evening...              │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Connection & Interaction (Social comfort, conversation entry points)                │
│    • get_me_talking      The easiest way to get me genuinely talking...                │
│    • first_hangout       A great, low-pressure first hangout would be...               │
│    • appreciate_people   I have an instant soft spot for people who...                 │
│    • message_me_if       You should definitely message me if...                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 5. Perspectives & Worldview (Values in action, personal philosophies)                  │
│    • try_to_live_by      One simple principle I try to live by...                      │
│    • care_more_about     As time goes on, I care much more about...                    │
│    • unpopular_opinion   An unpopular opinion that I will happily defend...            │
│    • overrated_concept   Something everyone loves that I find completely overrated...  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 6. Action & Collaboration (Projects, activities, shared adventures)                    │
│    • lets_collaborate    If we were to work on a project together, it would be...      │
│    • weekend_adventure   Next adventure I want to go on...                             │
│    • teach_me            Teach me something about ___ and I'm yours...                 │
│    • favorite_local_spot A local spot in my city that never fails...                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Capacity Rules & Editorial Guardrails

1. **Capacity Limits:**
   - **Minimum Required:** 0 (Prompts are 100% optional; onboarding is never blocked).
   - **Recommended:** 2 to 3 prompts (triggers a profile completeness badge).
   - **Maximum Allowed:** 3 prompts active on a profile simultaneously.
   - *Rationale:* 3 high-impact answers provide the perfect balance of variety without overwhelming the reader.
2. **Answer Length Constraint:**
   - **Maximum Length:** 250 characters per answer.
   - *Rationale:* Enforces punchy, conversational writing. Prevents boring, unreadable essays.
3. **Headline / Bio Length Constraint:**
   - **Maximum Length:** 140 characters.
4. **No Duplicate Prompts:** A user cannot answer the same prompt template twice.

---

## 6. Prompt Selection UX & Authoring Flow

```text
┌────────────────────────────────────────────────────────┐
│                   CHOOSE A PROMPT                      │
│                                                        │
│  SUGGESTED FOR YOU (Based on your interests & style)   │
│  [ 🔍 The rabbit hole I recently fell into... ]        │
│  [ ☕ The easiest way to get me talking... ]           │
│                                                        │
│  EXPLORE BY CATEGORY                                   │
│  [ Voice & Quirks ]  [ Curiosities ]  [ Daily Reality ]│
│  [ Connection ]      [ Perspectives ] [ Adventures ]   │
│                                                        │
│  🎲 [ Surprise me with a prompt ]                      │
└────────────────────────────────────────────────────────┘
```

### Authoring Steps:
1. **Browse or Tap Suggested:** User browses by category or taps a contextually suggested prompt template.
2. **Interactive Answer Card:** Shows prompt title, active text field, live character counter (`0/250`), and an optional `"Spark with AI"` button.
3. **Instant Preview:** Shows exactly how the finished chip will appear on the public profile.
4. **Reorder via Drag-and-Drop:** In profile edit mode, users can drag cards to set priority order (`sort_order: 1, 2, 3`).

---

## 7. AI-Assisted Self-Expression Guardrails

JESTER AI can serve as a supportive copy editor, but must **never** replace authentic human agency.

### Supported AI Actions (Triggered ONLY by User):
1. **Polish & Tighten:** User writes rough thoughts $\rightarrow$ AI suggests 2 punchier or warmer variations while preserving the user's exact meaning.
2. **Spark Ideas:** User chooses a prompt $\rightarrow$ AI shows 3 thematic directions based on declared interests (e.g. for Cinema: *"Mention your favorite obscure film or a movie that made you question everything"*).
3. **Voice Calibrations:** Allows user to toggle suggestions between `Witty`, `Warm`, and `Concise`.

### Critical Invariants:
- **Zero Hallucination:** JESTER AI must **never** auto-generate and publish an answer without the user's explicit request, review, and approval.
- **Attribution & Ownership:** Once edited and approved by the user, prompt text is stored as pure user-authored declared content (`source = 'user'`).
- **No Astrology Attribution:** The AI must never insert astrological clichés (*"As an Aries, I..."*) into prompt suggestions.

---

## 8. Multi-Domain Context Integration

Prompts serve as the expressive amplifier for structured signals:

1. **Prompts × Interests:**
   - Structured: `Photography` + `Cinema`
   - Prompt: *"I could talk about the cinematography in 1990s films forever."*
2. **Prompts × Values:**
   - Structured: `Curiosity (Core)`
   - Prompt: *"A question I never get tired of asking: What's a belief you held for ten years that you recently discarded?"*
3. **Prompts × Social Behavior:**
   - Structured: `One-on-One` + `Observant First`
   - Prompt: *"The easiest way to get me talking: Skip the group chat and ask me about my most irrational obsession over quiet coffee."*
4. **Prompts × Communication:**
   - Structured: `Deep & Meaningful` + `Question Asker`
   - Prompt: *"I have an instant soft spot for people who ask questions they genuinely don't know the answer to."*
5. **Prompts × Intent:**
   - Structured: `activity_partner`
   - Prompt: *"The easiest way to convince me to leave the house: Propose an impromptu hike outside the city with zero agenda."*

---

## 9. Public Profile Visual Hierarchy

To prevent the profile from feeling like a wall of data tags, Prompts are strategically interwoven with structured attributes:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. Visual Anchor: Primary Photo, Name, Age, Verification    │
│ 2. Location & Origin: 📍 Tbilisi · 🏡 From Kvareli          │
│ 3. Looking For: [ 👥 New Friends (Main) ] [ 🧗 Activity ]   │
│ 4. Headline / Bio: "Architect & analog shooter in Sololaki" │
├─────────────────────────────────────────────────────────────┤
│ 5. PROMPT #1 (Primary Voice Hook)                           │
│    "A completely unnecessary hill I will die on..."         │
│    "Filter coffee is objectively better than espresso if    │
│     you actually care about tasting origin notes."          │
│    [ 💬 Reply to this ]                                     │
├─────────────────────────────────────────────────────────────┤
│ 6. Primary Interests: [ Photography ⭐ ] [ Cinema ] [ Hiking ]│
├─────────────────────────────────────────────────────────────┤
│ 7. PROMPT #2 (Curiosity / Story)                            │
│    "The rabbit hole I recently fell into..."                │
│    "Brutalist architecture in the South Caucasus and why    │
│     concrete buildings feel like frozen music."             │
│    [ 💬 Reply to this ]                                     │
├─────────────────────────────────────────────────────────────┤
│ 8. Communication & Social Rhythm: Micro-Badges              │
│    [ 🌊 Deep & Meaningful ] [ 🔋 Recharges Solo ]           │
├─────────────────────────────────────────────────────────────┤
│ 9. PROMPT #3 (Connection / Invitation Hook)                 │
│    "A great low-pressure first hangout would be..."         │
│    "Grabbing sourdough pastries and walking through Vera    │
│     until we run out of things to debate."                  │
│    [ 💬 Reply to this ]                                     │
├─────────────────────────────────────────────────────────────┤
│ 10. Values & Lifestyle Cadence: Guiding Compass Badges      │
│ 11. Safe Astrological Placements: Sun, Moon, Ascendant      │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. Prompts as Interactive Conversation Entry Points

Prompts eliminate cold-start paralysis through direct contextual interaction:

### The "Reply to Prompt" Flow:
1. When viewing a profile, every prompt card features a subtle `[ 💬 Reply to this ]` action button.
2. Tapping it opens a lightweight message composer that automatically quotes the prompt:
   ```text
   ┌────────────────────────────────────────────────────────┐
   │ REASON TO CONNECT                                      │
   │ Alexandre: "Filter coffee is objectively better than   │
   │ espresso if you actually care about origin notes."     │
   │                                                        │
   │ Your message:                                          │
   │ "Bold claim. Are we talking Ethiopian naturals or are  │
   │ you defending washed Kenyans?"                         │
   │                                                        │
   │ [ Send Connection Request ]                            │
   └────────────────────────────────────────────────────────┘
   ```
3. When the recipient receives the request, the notification highlights the exact prompt reference, transforming a generic *"Alex wants to connect"* into an immediate, engaging conversation starter.

---

## 11. Moderation & Trust & Safety Guardrails

Because prompts are public user-authored text, they are protected by automated moderation:

### 1. Pre-Publication Automated Guardrails:
- **Sanitization:** Strict HTML/script tag stripping; prevents Cross-Site Scripting (XSS).
- **PII Guardrail:** Regex detection blocks unprompted phone numbers, email addresses, and external payment handles to protect users from off-platform scams and stalking.
- **Safety Lexicon Filter:** Blocks hate speech, explicit sexual solicitation, violent threats, and illegal substance sales.

### 2. Moderation States:
- `published`: Passed automated checks; immediately visible.
- `flagged_review`: Triggered borderline keyword; temporarily held for internal queue review.
- `rejected`: Violated community safety policy; user receives non-punitive inline guidance to rephrase.

### 3. Light-Touch Enforcement:
- JESTER explicitly permits irony, dry humor, quirky opinions, and cultural slang. Harmless sarcasm (*"I hate waking up early"*) is never flagged as toxic or negative.

---

## 12. Database Architecture Blueprint (DDL & Indexes)

Three normalized tables maintaining strict schema consistency with previous JESTER domains:

```sql
-- ============================================================================
-- 1. CANONICAL PROMPT CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.prompt_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'voice_quirks', 'curiosity_ideas', 'daily_reality', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL PROMPT TEMPLATES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.prompt_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'unnecessary_hill', 'talk_forever', 'ordinary_day', etc.
    question_en TEXT NOT NULL,
    question_ka TEXT NOT NULL,
    placeholder_en VARCHAR(120),
    placeholder_ka VARCHAR(120),
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. USER PROMPTS (Active Declared User Answers)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    prompt_template_id UUID NOT NULL REFERENCES public.prompt_templates(id) ON DELETE RESTRICT,
    answer VARCHAR(250) NOT NULL,
    sort_order INTEGER NOT NULL CHECK (sort_order BETWEEN 1 AND 3),
    visibility VARCHAR(20) NOT NULL DEFAULT 'public' CHECK (visibility IN ('public', 'connections_only', 'hidden')),
    moderation_status VARCHAR(20) NOT NULL DEFAULT 'published' CHECK (moderation_status IN ('published', 'flagged_review', 'rejected')),
    source VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('declared', 'ai_assisted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_prompt_template UNIQUE (user_id, prompt_template_id),
    CONSTRAINT uq_user_prompt_order UNIQUE (user_id, sort_order)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_user_prompts_user ON public.user_prompts(user_id, sort_order);
CREATE INDEX IF NOT EXISTS idx_user_prompts_status ON public.user_prompts(moderation_status);
```

---

## 13. API Specification & Safe DTOs (Endpoints 71–77)

### 13.1 Safe Profile Serialization (`UserPromptDTO`):
```json
{
  "id": "8b3e8c42-2345-6789-01ab-cdef01234567",
  "prompt_template_id": "9c4f9d53-3456-7890-12bc-def012345678",
  "slug": "unnecessary_hill",
  "question": "A completely unnecessary hill I will die on...",
  "answer": "Filter coffee is objectively better than espresso if you actually care about origin notes.",
  "sort_order": 1,
  "visibility": "public"
}
```

### 13.2 Planned Endpoints:
1. `GET /v1/prompts/categories` — List prompt categories.
2. `GET /v1/prompts/templates` — List curated prompt templates (filterable by `category_slug`).
3. `GET /v1/prompts/suggestions` — Contextual prompt suggestions based on user interests and intent.
4. `GET /v1/prompts/me` — Retrieve own declared prompts and moderation states.
5. `POST /v1/prompts` — Create a prompt answer (validates max 3 limit, 250 chars max).
6. `PATCH /v1/prompts/{prompt_id}` — Edit an existing prompt answer or update sort order.
7. `DELETE /v1/prompts/{prompt_id}` — Delete a prompt answer.
8. `POST /v1/prompts/ai-assist` — Request AI polishing, tone adjustment, or idea sparks for a draft.
9. `GET /v1/prompts/people/{target_user_id}` — View discoverable target's public prompts (respecting block rules).

---

## 14. Security, Privacy, Analytics & Scope

### 14.1 Security & Privacy Invariants:
1. **Sanitization:** Strict HTML sanitization on all incoming prompt answers.
2. **AI Semantic Boundary:** JESTER AI must treat prompt answers as self-expression and humor, **never as clinical psychological diagnosis**. (e.g. A prompt saying *"I hate everyone before my morning coffee"* must never result in an AI verdict declaring the user *"antisocial"*).
3. **Block Isolation:** Blocked users receive `404 PrivacySafeNotFoundException` and cannot view prompts or submit prompt replies.

### 14.2 Non-Surveillance Analytics:
- `prompt_library_opened`
- `prompt_template_selected`
- `prompt_created`
- `prompt_updated`
- `prompt_deleted`
- `prompt_replied_to`
- `prompt_connection_initiated`
- `ai_prompt_assist_requested`
- `ai_prompt_assist_accepted`

---

## 15. Final Architecture Decisions Table

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Core Product Role** | Answers *"What does this person actually sound like?"* — human voice, wit, and conversation hooks. |
| **Profile Structure** | Short Headline / Bio (140 chars) + up to 3 Curated Prompts (250 chars max each). |
| **Taxonomy Structure** | 6 categories, 24 curated prompts calibrated to JESTER brand voice (witty, observant, relational). |
| **Capacity Limits** | Min 0 (100% optional), Recommended 2–3, Max 3 active prompts. |
| **Conversation Entry** | Inline `[ 💬 Reply to this ]` on every prompt card; quotes prompt in connection request note. |
| **AI Assistance** | Optional, user-initiated copy polishing or idea sparks. Strict zero-unprompted-hallucination invariant. |
| **Profile Layout** | Woven throughout profile (between photo, interests, lifestyle, and astrology) to prevent tag clutter. |
| **Astrology Boundary** | Astrology must NEVER write or dictate prompt answers. Human voice remains independent. |
| **Database Blueprint** | 3 normalized tables: `prompt_categories`, `prompt_templates`, `user_prompts`. |
| **API Blueprint** | Dedicated `/v1/prompts/*` endpoints (71–77) and `prompts: list[UserPromptDTO]` in `ProfileResponse`. |
| **Moderation Policy** | Pre-publication PII & hate-speech regex filter; non-punitive guidance; permits harmless irony. |
