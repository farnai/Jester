# JESTER — Communication System V1
## Product, UX, Data Architecture & Relationship Intelligence Specification

---

## 1. Product Purpose & Philosophy

JESTER is a **People Discovery and Relationship Intelligence** platform. 

To help people discover compatible connections and navigate relational dynamics, the platform systematically maps foundational human dimensions:
> **Interests answer:** *"What are you into?"* (Topics, intellectual passions, creative crafts)  
> **Location answers:** *"Where are you based and where are you from?"* (Current residency, regional heritage)  
> **Lifestyle answers:** *"What is your everyday life like?"* (Daily rhythm, activity pace, work environment, living reality)  
> **Values answer:** *"What matters to you?"* (Guiding principles, moral compass, and life priorities)  
> **Social Behavior answers:** *"How do you tend to be around people?"* (Gathering scale, social battery, and setting comfort)  
> **Communication answers:** *"How do you like to communicate?"* (Conversation depth, conversational role, messaging format, and pacing)

Communication describes **the mechanics, format, depth, and pacing of human conversation and digital messaging**.

### Core Operating Axioms:
1. **Describe Situations & Preferences, Don't Define Identity:** Communication answers: *"How do you prefer to converse and message?"* It strictly does **NOT** answer: *"What kind of personality are you?"*
2. **Strict Anti-Diagnostic & Anti-Labeling Invariant:** JESTER rejects communication stereotypes and pop-psychology buzzwords (*"Deep Talker"*, *"Dry Texter"*, *"Golden Retriever Communicator"*, *"Emotionally Unavailable"*, *"Bad Texter"*). Preferences are functional guidelines, not character verdicts.
3. **Zero Reply-Time Surveillance or Scorekeeping:** JESTER explicitly forbids response-latency tracking, "average reply time" clocks, read-receipt surveillance, and scorekeeping (*"They took 4 hours to reply"*). Texting speed is not a measure of human worth.
4. **The Insight Becomes the Invitation:** Communication data exists primarily to eliminate cold-start messaging anxiety and guide first conversations into engaging, natural dialogue.
5. **Declared User Reality > Behavioral Inference > Astrological Interpretation:** What a user explicitly declares about their communication comfort always overrides algorithmic inferences or astrological Mercury stereotypes.
6. **Lightweight & Skippable:** Onboarding captures a rapid 3-question *"Communication Rhythm Snapshot"* that is 100% optional and skippable. Zero rating sliders.

---

## 2. Critical Domain Separation

To prevent cross-domain contamination, JESTER enforces strict boundaries between Communication and adjacent subsystems:

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
│ 8. Intent         │ What am I seeking right now?     │ Long-term relationship, close friends, collaborators     │
│ 9. Prompts        │ How do I express my voice?       │ Open-ended text prompts and personal quotes              │
└───────────────────┴──────────────────────────────────┴──────────────────────────────────────────────────────────┘
```

### Master Decoupling Table:

| Candidate Concept | Primary Domain | Decoupling Invariant & Justification |
| :--- | :--- | :--- |
| **Deep Talks vs Light Banter** | `Communication` | Interaction depth preference; NOT social group size. |
| **Asks Questions vs Shares Stories**| `Communication` | Conversational role and narrative flow; NOT communication ability. |
| **Voice Notes vs Texting vs Calls** | `Communication` | Preferred messaging channel/format; NOT lifestyle routine. |
| **Prefers One-on-One vs Crowds** | `Social Behavior` | Social gathering scale and physical environment; NOT conversational depth. |
| **Social Battery (Recharging Solo)**| `Social Behavior` | Energy mechanics during/after human contact; NOT messaging tone. |
| **Honesty & Radical Truth** | `Values` | Ethical guiding principle; NOT everyday conversational phrasing. |
| **Curiosity** | `Values` & `Interests`| In `Values`, drive to explore ideas; in `Communication`, the question-driven role (`question_curious`). |
| **Playfulness / Levity** | `Values` & `Communication`| In `Values`, existential lightness; in `Communication`, witty banter preference. |
| **Looking for Meaningful Chat** | `Intent` | Short-term purpose on JESTER; NOT long-term conversational habit. |
| **Early Bird / Night Owl** | `Lifestyle` | Biological circadian rhythm; NOT messaging latency. |

---

## 3. Dimensional Analysis & The 9-Question Litmus Test

Every candidate dimension for Communication System V1 was evaluated against the 9-question architecture litmus test:
1. *Does it materially improve discovery?*
2. *Does it improve first conversation?*
3. *Does it improve JESTER AI recommendations?*
4. *Does it improve real-world connection?*
5. *Can users understand it immediately?*
6. *Is it worth asking during onboarding?*
7. *Is it better learned behaviorally later?*
8. *Is it potentially sensitive or socially judgmental?*
9. *Does it overlap with another JESTER domain?*

### Evaluation Results:

| Candidate Dimension | Litmus Test Evaluation | V1 Decision |
| :--- | :--- | :---: |
| **A. Conversation Depth** | Essential for setting expectations (small talk vs. existential substance). Immensely improves starter generation. Immediately clear. | ✅ **IN V1 (Core)** |
| **B. Conversational Role** | Identifies narrative flow (Question-asker, Storyteller, Idea-exchanger). Powers complementary matching. | ✅ **IN V1 (Core)** |
| **C. Messaging Medium** | Solves major real-world friction (Text vs. Voice Notes vs. Calls). High practical utility. | ✅ **IN V1 (Core)** |
| **D. Pacing & Rhythm** | Helpful for managing reply expectations (Active bursts vs. unhurried async). Must be framed without reply-time metrics. | ✅ **IN V1 (Profile & Snapshot)** |
| **E. Response Latency Metrics** | "Average reply time: 2 hours". Highly toxic, induces surveillance anxiety, punishes busy users. | 🚫 **STRICTLY EXCLUDED** |
| **F. Tone / Mood Archetypes** | Highly subjective ("Warm", "Serious", "Witty"). Prone to inconsistent self-reporting. Better expressed via Prompts. | 🔮 **DEFERRED** |
| **G. Message Sentiment Snooping** | Parsing private chat text to diagnose personality. Severe privacy violation; destroys trust. | 🚫 **PERMANENTLY BANNED** |

---

## 4. Communication Taxonomy V1 (4 Dimensions, 14 Canonical Options)

JESTER V1 establishes a pragmatic, non-judgmental taxonomy of **14 canonical options** organized into 4 actionable dimensions:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                         JESTER COMMUNICATION TAXONOMY V1                               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Conversation Depth (What conversational depth feels most natural?)                  │
│    • casual_light         Light & Casual          (Breezy, fun, everyday observations) │
│    • balanced_depth       Balanced Flow           (Easy everyday chat that can go deep)│
│    • deep_meaningful      Deep & Meaningful       (Big ideas, philosophy, substance)   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Conversational Role (What is your natural conversational dynamic?)                  │
│    • question_curious     Curious / Asks Questions(Enjoys drawing others out, inquiring)│
│    • story_expressive     Storyteller             (Narrates experiences, vivid context)│
│    • idea_conceptual      Idea Exchanger          (Debates, brainstorming, mental play)│
│    • adaptable_flow       Goes with the Flow      (Responsive, matches partner's style)│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Messaging Medium (How do you prefer to exchange messages?)                          │
│    • mostly_text          Mostly Text             (Clean, concise, async written word) │
│    • voice_notes_welcome  Voice Notes Welcome     (Appreciates vocal tone and nuance)  │
│    • calls_welcome        Calls over Endless Text (Prefers quick chats over text marathons)│
│    • flexible_medium      A Bit of Everything     (Comfortable across any medium)      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Conversational Pacing (What is your messaging rhythm?)                              │
│    • active_banter        Active Bursts           (Fast ping-pong when online)         │
│    • unhurried_thoughtful Unhurried & Thoughtful  (Takes time, writes with substance)  │
│    • relaxed_async        Relaxed & No Pressure   (Casual async pace, zero rush)       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Definitions & Canonical Slugs:

1. **Conversation Depth**:
   - `casual_light`: Enjoys keeping interaction playful, humorous, and light-hearted without heavy emotional weight.
   - `balanced_depth`: Naturally bridges everyday humor and casual banter with meaningful, thoughtful discussions.
   - `deep_meaningful`: Craves substantial dialogue, existential curiosities, and authentic vulnerability from early on.

2. **Conversational Role**:
   - `question_curious`: An active listener who loves asking thoughtful questions and uncovering how the other person thinks.
   - `story_expressive`: Communicates through vivid narratives, relatable personal anecdotes, and expressive context.
   - `idea_conceptual`: Energized by debating theories, exchanging creative concepts, and exploring abstract ideas.
   - `adaptable_flow`: Highly intuitive and fluid; comfortably matches the conversational temperature of the room.

3. **Messaging Medium**:
   - `mostly_text`: Prefers traditional text messaging; values brevity, reading at one's own pace, and low disruption.
   - `voice_notes_welcome`: Enjoys listening to and sending voice memos; values the warmth, nuance, and inflections of speech.
   - `calls_welcome`: Prefers a 10-minute real-time call over 3 days of disjointed texting.
   - `flexible_medium`: Seamlessly switches between text, voice, and spontaneous calls depending on the context.

4. **Conversational Pacing**:
   - `active_banter`: Enjoys real-time conversational tennis—rapid replies back-and-forth when both are present.
   - `unhurried_thoughtful`: Takes several hours or a day to formulate a genuine, substantive reply; values depth over speed.
   - `relaxed_async`: Views messaging as an open, ongoing letter exchange with zero expectation of immediate reply.

---

## 5. Communication UX: The "Communication Rhythm" Snapshot

### 5.1 Onboarding Snapshot (100% Skippable):
During or following profile setup, the user encounters a single-card **Communication Rhythm Snapshot**:
- **3 Core Questions**:
  1. *Conversation Depth:* `[ 🎈 Light & Casual ]` `[ ⚖️ Balanced Flow ]` `[ 🌊 Deep & Meaningful ]`
  2. *Conversational Style:* `[ 🔍 Asks Questions ]` `[ 📖 Shares Stories ]` `[ 💡 Exchanges Ideas ]` `[ 🌊 Goes with the Flow ]`
  3. *Preferred Format:* `[ 💬 Mostly Text ]` `[ 🎙️ Voice Notes OK ]` `[ 📞 Calls Welcome ]` `[ 🔄 Mixed ]`
- **One-Tap Selection:** Single tap per question; instantly highlights and advances.
- **Pacing Question:** Available during onboarding or accessible anytime in Profile Settings.
- **Zero Sliders:** No 1–10 rating scales.

```text
┌────────────────────────────────────────────────────────┐
│                YOUR COMMUNICATION RHYTHM               │
│                                                        │
│   How do you like to converse and message?             │
│                                                        │
│   CONVERSATION DEPTH                                   │
│   [ 🎈 Light & Casual ]  [ ⚖️ Balanced Flow ]          │
│   [ 🌊 Deep & Meaningful ]                             │
│                                                        │
│   CONVERSATIONAL DYNAMIC                               │
│   [ 🔍 Asks Questions ]  [ 📖 Shares Stories ]         │
│   [ 💡 Exchanges Ideas ]  [ 🌊 Goes with the Flow ]    │
│                                                        │
│   PREFERRED FORMAT                                     │
│   [ 💬 Mostly Text ]  [ 🎙️ Voice Notes OK ]            │
│   [ 📞 Calls Welcome ]  [ 🔄 A Bit of Everything ]     │
│                                                        │
│   [  Skip for now  ]                     [  Continue ] │
└────────────────────────────────────────────────────────┘
```

---

## 6. Public Profile Presentation: Communication Rhythm

On public profiles, communication preferences render under an elegant **"Communication Rhythm"** section:

```text
┌─────────────────────────────────────────────────┐
│ Alexandre, 28                                   │
│ 📍 Based in Tbilisi · 🏡 From Kvareli           │
│                                                 │
│ COMMUNICATION RHYTHM                            │
│ [ 🌊 Deep & Meaningful ]  [ 💡 Exchanges Ideas ]│
│ [ 🎙️ Voice Notes OK ]    [ ⏳ Unhurried Pace ]  │
└─────────────────────────────────────────────────┘
```

### Visual & Privacy Principles:
1. **Clean Glassmorphic Micro-Badges:** Rendered as refined, understated chips with clear iconography.
2. **Granular Privacy Controls:** Users can independently toggle any attribute (or the entire card) visible or hidden in settings via `visibility_flags`.
3. **Undeclared Restraint:** Undeclared attributes simply do not render (no *"Preferred Format: Not specified"* clutter).
4. **Zero Diagnostic Grading:** Never display communication scores, "chattiness" radar graphs, or speed metrics.

---

## 7. Relationship Intelligence & Discovery Dynamics

In Discovery matching, Communication preferences provide **conversational friction reduction and chemistry bridges**, never acting as numerical compatibility gates:

### 7.1 Symmetric Harmony (Shared Conversational Frequency)
- **Mutual Deep & Meaningful:** *"Both skip the shallow small talk — conversations here get real quickly."*
- **Mutual Voice Notes:** *"Both welcome voice memos — feel free to talk it out rather than type essays."*
- **Mutual Unhurried Pacing:** *"Both prefer an unhurried rhythm — zero texting anxiety, zero pressure."*

### 7.2 Complementary Balance (Dynamic Conversation Interplay)
- **Question-Asker + Storyteller:** *"One naturally draws stories out, one loves narrating vivid experiences. Effortless conversational tennis."*
- **Idea-Exchanger + Question-Asker:** *"One brings bold concepts to the table, one probes with deep questions. Intellectual fire."*
- **Active Bursts + Relaxed Async:** *"Different messaging paces — set an easy rhythm early and avoid overthinking latency."*

### 7.3 Clear Distinction from Synastry V1 $S_{\text{communication}}$
- **Synastry V1 $S_{\text{communication}}$:** A deterministic mathematical aspect score ($0.0 - 100.0$) derived from Mercury-Mercury, Sun-Mercury, and Moon-Mercury astrological angular geometries.
- **Communication System V1:** Self-declared human preferences and messaging habits.
- **Invariant:** Synastry calculates the *underlying cognitive tension*; Communication V1 provides the *practical operational manual*. They enrich each other but **never overwrite each other**.

---

## 8. First-Conversation Intelligence ("The Insight Becomes the Invitation")

Communication data provides high-leverage context for generating cold-start conversation starters and chat guidance:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        FIRST-CONVERSATION INTELLIGENCE ENGINE                          │
├────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│ User A Dynamic             │ User B Dynamic              │ Generated JESTER Guidance   │
├────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ `question_curious`         │ `story_expressive`          │ "Ask them about the story   │
│ (Inquisitive listener)     │ (Loves telling stories)     │ behind their latest trip."  │
├────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ `deep_meaningful`          │ `deep_meaningful`           │ "Skip the 'how was your     │
│ (Seeks substance)          │ (Seeks substance)           │ day' small talk — dive into │
│                            │                             │ the ideas you both care for"│
├────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ `voice_notes_welcome`      │ `voice_notes_welcome`       │ "Voice notes are welcome    │
│ (Enjoys audio nuance)      │ (Enjoys audio nuance)       │ here — voice tone will build│
│                            │                             │ connection twice as fast."  │
├────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ `casual_light`             │ `deep_meaningful`           │ "Start with playful humor;  │
│ (Humor & ease)             │ (Substantive)               │ let the deeper substance    │
│                            │                             │ emerge naturally over time."│
└────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

---

## 9. JESTER AI Context & Ethical Invariants

When the JESTER AI engine receives communication context tokens:

```json
{
  "viewer": {
    "conversation_depth": "deep_meaningful",
    "conversation_role": "idea_conceptual",
    "messaging_medium": "voice_notes_welcome",
    "response_pace": "unhurried_thoughtful"
  },
  "target": {
    "conversation_depth": "deep_meaningful",
    "conversation_role": "question_curious",
    "messaging_medium": "mostly_text",
    "response_pace": "relaxed_async"
  },
  "communication_dynamics": {
    "depth_resonance": "mutual_deep",
    "role_interplay": "conceptual_and_curious",
    "medium_awareness": "target_prefers_text",
    "pacing_harmony": "both_unhurried"
  }
}
```

### Critical Operational Invariants:
1. **Never Label or Psychologically Stereotype:** JESTER AI must **never** call a user *"dry texter"*, *"ghosting risk"*, *"high maintenance"*, or *"bad communicator"*. All communication styles are treated with equal dignity.
2. **Medium Respect:** If User B prefers `mostly_text`, JESTER AI must not advise User A to barrage them with 5-minute voice notes.
3. **Pacing Reassurance:** JESTER AI actively reassures users when connected with an `unhurried_thoughtful` communicator (*"Alexandre takes his time to craft meaningful replies — don't mistake unhurried pacing for a lack of interest"*).
4. **Strict Message Privacy:** JESTER AI is **never** provided with actual user-to-user chat message bodies or sentiment logs for personality profiling.

---

## 10. Declared vs. Behavioral Communication Architecture

JESTER strictly separates what a user declares from downstream behavioral observations:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Declared Preferences (User-Controlled & Profile Visible)            │
│    • Stored in `public.user_communication_preferences`                 │
│    • Explicit, editable, governed by user visibility toggles           │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Behavioral Signals (Internal Recommendations Only)                  │
│    • Message count milestones (e.g. 5+ messages exchanged)             │
│    • Active connection status                                          │
│    • Stored in service-role internal logs                              │
│    • NEVER overwrites declared preferences                             │
│    • NEVER exposed as public user labels or "scores"                   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. JESTER AI Interpretation Layer                                      │
│    • Translates declared preferences into warm conversational guidance │
│    • Respects declared user intent above all else                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Database Schema Specification (Architecture Blueprint)

```sql
-- ============================================================================
-- 1. CANONICAL COMMUNICATION CATEGORIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.communication_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'conversation_depth', 'conversation_role', 'messaging_medium', 'response_pace'
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 2. CANONICAL COMMUNICATION OPTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.communication_options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES public.communication_categories(id) ON DELETE CASCADE,
    slug VARCHAR(60) NOT NULL UNIQUE,          -- 'deep_meaningful', 'question_curious', 'voice_notes_welcome', etc.
    name_en VARCHAR(100) NOT NULL,
    name_ka VARCHAR(100) NOT NULL,
    definition_en TEXT NOT NULL,
    definition_ka TEXT NOT NULL,
    badge_icon VARCHAR(30),                    -- 'waves', 'help-circle', 'mic', 'clock', etc.
    sort_order INTEGER DEFAULT 100,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 3. USER COMMUNICATION PREFERENCES TABLE (Normalized Profile Extension)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_communication_preferences (
    user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    conversation_depth VARCHAR(40),            -- e.g. 'casual_light', 'balanced_depth', 'deep_meaningful'
    conversation_role VARCHAR(40),             -- e.g. 'question_curious', 'story_expressive', 'idea_conceptual', 'adaptable_flow'
    messaging_medium VARCHAR(40),              -- e.g. 'mostly_text', 'voice_notes_welcome', 'calls_welcome', 'flexible_medium'
    response_pace VARCHAR(40),                 -- e.g. 'active_banter', 'unhurried_thoughtful', 'relaxed_async'
    visibility_flags JSONB NOT NULL DEFAULT '{
        "conversation_depth": true,
        "conversation_role": true,
        "messaging_medium": true,
        "response_pace": true
    }',
    source VARCHAR(30) NOT NULL DEFAULT 'declared' CHECK (source IN ('onboarding_snapshot', 'profile_edit', 'inferred')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- 4. COMMUNICATION RELATIONS GRAPH (Synergies & Dynamic Interplay)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.communication_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    option_a_id UUID NOT NULL REFERENCES public.communication_options(id) ON DELETE CASCADE,
    option_b_id UUID NOT NULL REFERENCES public.communication_options(id) ON DELETE CASCADE,
    relation_type VARCHAR(30) NOT NULL CHECK (relation_type IN ('symmetric_harmony', 'complementary_balance', 'pacing_awareness')),
    dynamic_label_en VARCHAR(120) NOT NULL,    -- e.g. 'Questioner and Storyteller', 'Mutual Deep Substance'
    dynamic_label_ka VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_communication_relation UNIQUE (option_a_id, option_b_id),
    CONSTRAINT check_no_self_communication_relation CHECK (option_a_id != option_b_id)
);
```

---

## 12. API Specification & Safe DTOs

### 12.1 Safe Public Profile Serialization
Public profile payloads serialize communication preferences filtered strictly through `visibility_flags`:

```json
{
  "id": "7a3e8b42-1234-4567-89ab-cdef01234567",
  "display_name": "Alexandre",
  "communication": {
    "conversation_depth": "deep_meaningful",
    "conversation_role": "idea_conceptual",
    "messaging_medium": "voice_notes_welcome",
    "response_pace": "unhurried_thoughtful"
  }
}
```

### 12.2 Planned Endpoints (59 to 64):
- `GET /v1/communication/options` — List canonical categories and localized options.
- `GET /v1/communication/onboarding-snapshot` — Fetch the 3 onboarding questions with interactive chips.
- `POST /v1/communication/onboarding` — Submit onboarding snapshot (optional/skippable).
- `GET /v1/communication/me` — Retrieve own declared communication preferences and visibility flags.
- `PATCH /v1/communication/me` — Update communication preferences and visibility flags.
- `GET /v1/communication/people/{target_user_id}` — Get discoverable target's public communication preferences.

---

## 13. Privacy & Security Invariants

1. **Owner-Controlled Visibility:** All communication preferences are governed by per-attribute visibility flags. When toggled private, they are stripped from public responses and omitted from AI prompts.
2. **Zero Message Body Mining:** JESTER strictly prohibits parsing or training AI on the plaintext bodies of user-to-user direct messages for communication profiling.
3. **No Latency Shaming:** Latency metrics, response-time scores, and read-receipt timers are excluded from schema, API, and UI.
4. **Non-Diagnostic Security Invariant:** System prompts and client contracts explicitly forbid generating personality typologies or virtue rankings based on communication style.

---

## 14. Non-Surveillance Analytics

To measure feature adoption without compromising user privacy:
- `communication_onboarding_viewed` — User reached the onboarding step.
- `communication_onboarding_completed` — User submitted communication preferences.
- `communication_onboarding_skipped` — User tapped skip.
- `communication_preference_updated` — User changed preferences in profile settings.
- `communication_starter_used` — User tapped a conversation starter generated with communication context.
- *Strict Invariant:* No raw message content or user keystroke timings are ever logged for analytics.

---

## 15. User Experience States

1. **Not Started:** New user in onboarding; step displayed with quick single-tap chips and prominent "Skip for now".
2. **Skipped:** User tapped skip; no rows created in `user_communication_preferences`; profile card does not render.
3. **Partially Completed:** User selected depth and format, skipped role; undeclared fields remain `NULL` and are omitted from profile badges.
4. **Completed:** All preferences declared; rendered as refined glassmorphic chips under "Communication Rhythm".
5. **Edited Later:** Updated via Profile Settings at any time with instant cache invalidation.
6. **Hidden:** User toggled visibility to false; badges vanish from public profile; suppressed from external AI prompts.
7. **Public:** Visible to authenticated, discoverable, and unblocked users.
8. **Blocked:** Handled by canonical privacy-safe 404; zero existence or preference leakage.

---

## 16. Scope Boundary: V1 vs. Future Roadmap

| Capability | In V1 | Deferred to Future | Rationale |
| :--- | :---: | :---: | :--- |
| **4 Dimensions / 14 Options** | ✅ | — | Curated, actionable, non-judgmental taxonomy |
| **3-Question Onboarding Snapshot**| ✅ | — | Rapid, single-tap, 100% skippable |
| **First-Conversation Intelligence**| ✅ | — | Context-aware icebreakers and meeting advice |
| **Communication Profile Badges** | ✅ | — | Clean micro-badges under dedicated profile section |
| **Exclusion of Response Timers** | ✅ | — | Protects mental health; prevents reply-anxiety |
| **Message Body Content Profiling** | 🚫 | 🚫 | Permanent privacy boundary violation |
| **Adaptive Communication Learning**| ❌ | 🔮 | Requires significant messaging volume |
| **Voice Note Transcription / Preview**| ❌ | 🔮 | Future chat infrastructure feature |

---

## 17. Final Architecture Decisions Table

| Area | V1 Architecture Decision |
| :--- | :--- |
| **Product Purpose** | Answers *"How do you like to communicate?"* — depth, conversational role, format, and pacing. |
| **Anti-Typing Invariant** | Strictly rejects personality labels ("Deep Talker", "Dry Texter", "Golden Retriever"). |
| **Response-Time Philosophy** | Replaced toxic reply timers with **conversational pacing preferences** (`active_banter`, `unhurried_thoughtful`, `relaxed_async`). |
| **Canonical Taxonomy** | 4 dimensions, 14 options: Conversation Depth, Conversational Role, Messaging Medium, Conversational Pacing. |
| **Onboarding UX** | 3-question rapid snapshot card. Single-tap chips. Zero sliders. 100% skippable. |
| **Profile UI Pattern** | "Communication Rhythm" micro-badges with granular per-attribute privacy toggles. |
| **Discovery & First Chat** | Powers "The Insight Becomes the Invitation" with role-aware starter generation (e.g. Questioner + Storyteller). |
| **Synastry Distinction** | Strictly decoupled from Synastry V1 $S_{\text{communication}}$ (astrological aspects). They complement, never overwrite. |
| **Database Model** | Normalized tables: `communication_categories`, `communication_options`, `user_communication_preferences`, `communication_relations`. |
| **API Contract** | Enriched `ProfileResponse` with `communication: CommunicationDTO|None`. Dedicated `/v1/communication/*` endpoints. |
| **AI Context** | Contextual starter crafting and pacing reassurance; strictly barred from personality labeling or message snooping. |
| **Security Policy** | Standard RLS: users manage own preferences; all options public; hidden fields suppressed from client and AI. |
| **V1 Scope** | 14 options, 3-question snapshot, communication badges, role synergy, AI icebreaker guidance. |
| **Future Scope** | Voice note messaging enhancements, adaptive conversation pacing, multi-user chat dynamics. |
