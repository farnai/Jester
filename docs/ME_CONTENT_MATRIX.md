# JESTER — PHASE 3.1
## "ME" / "ვინ ვარ მე?"
### COMPLETE CONTENT MATRIX & COVERAGE SPECIFICATION

> **Status:** SPECIFICATION & CONTENT FACTORY BLUEPRINT  
> **Authority:** Approved ME Semantic Architecture ([`docs/ME_SEMANTIC_ARCHITECTURE.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/ME_SEMANTIC_ARCHITECTURE.md)), Source Code (`backend/app/astrology/`, `backend/app/interpretation/`), Swiss Ephemeris (`pyswisseph`), `content_corpus.json`  
> **Core Axiom:** **TRUTH > COVERAGE > VARIETY > VOLUME.**  
> We do not manufacture text to hit an arbitrary metric. We engineer an exact content matrix derived from real, verified astrological signals, maximizing distinct semantic angles and minimizing repetition without inventing astrology.

---

## 1. EXECUTIVE SUMMARY

Phase 3 established the 10-layer semantic architecture for JESTER's natal self-understanding engine. **Phase 3.1 blueprints the exact Content Factory.**

### The Problem with Naive Content Scaling
In automated content generation, teams often multiply dimensions blindly:
$$12 \text{ Signs} \times 12 \text{ Moons} \times 12 \text{ Risings} = 1,728 \text{ Big Three texts}$$
$$\dots \text{or } 133 \text{ targets} \times 4 \text{ depths} \times 8 \text{ tones} \times 5 \text{ variants} = 21,280 \text{ texts!}$$

This brute-force multiplication produces:
1. **Synthetic Inflation:** 50 variants of a single sentence with trivial prefix changes (e.g. "წარმოიდგინე სიტუაცია:...").
2. **Astrological Hallucination:** Fabricating distinct psychological theories for mathematical permutations that have no distinct astrological meaning.
3. **Unmaintainable Quality:** 10,000 mediocre AI drafts where 0% are reviewed, approved, or distinctive.

### The JESTER Factory Principle
$$\mathbf{5 \text{ Distinct, Razor-Sharp Variants}} \gg \mathbf{30 \text{ Nearly Identical Variants}}$$

We build a **compact, high-density, multi-depth deterministic content matrix**:
- Grounded strictly in **72 Base Personal Signals** + **7 Derived Structural Signals** + **44 Valid Synthesis Dynamics**.
- Filtered through an **Anti-Duplication Orthogonality Layer**.
- Driven by **8 Authentic JESTER Delivery Modes**.
- Governed by **Deterministic Hash-Based Selection** with Metaphor-Family tracking.

---

## 2. VERIFIED ASTROLOGICAL SIGNAL INVENTORY

Every signal in JESTER must have an auditable computational origin. Below is the verified forensic inventory of every real deterministic natal signal in the repository:

| Signal ID | Astrological Source & Function | Engine Status | API Exposure | Safe for Client? | Contract Registry | Current Assets in Corpus | Additional Action Required |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| **`sun_sign`** (12 signs) | `swe.calc_ut` $\to$ `longitude_to_sign` | IMPLEMENTED | EXPOSED (`/v1/astrology/me`) | YES | 12 (`self.identity.sun_*`) | 591 KA / 271 EN | None (Audit existing) |
| **`moon_sign`** (12 signs) | `swe.calc_ut` $\to$ `longitude_to_sign` | IMPLEMENTED | EXPOSED (`/v1/astrology/me`) | YES | 12 (`self.emotional.moon_*`) | 480 KA / 222 EN | None (Audit existing) |
| **`ascendant_sign`** (12 signs) | `swe.houses(P)` $\to$ `longitude_to_sign` | IMPLEMENTED | EXPOSED (null if time unknown) | YES | 12 (`self.persona.rising_*`) | 467 KA / 215 EN | None (Graceful fallback) |
| **`element_primary`** (4 elements) | Weighted sum (Sun:3, Moon:3, Asc:3, Mer:2, Ven:2, Mar:2) | IMPLEMENTED | EXPOSED (`/v1/astrology/me`) | YES | 4 (`self.element.*_dominant`) | 147 KA / 68 EN | None (Audit existing) |
| **`modality_primary`** (3 modalities) | Weighted sum (Identical weights) | IMPLEMENTED | EXPOSED (`/v1/astrology/me`) | YES | 3 (`self.modality.*_dominant`) | 130 KA / 61 EN | None (Audit existing) |
| **`mercury_sign`** (12 signs) | `swe.calc_ut` $\to$ `longitude_to_sign` | RAM ONLY (`natal.py:126`) | **NOT EXPOSED** | YES | **0 Contracts** | **0 Assets** | Migration + DTO + 12 Contracts |
| **`venus_sign`** (12 signs) | `swe.calc_ut` $\to$ `longitude_to_sign` | RAM ONLY (`natal.py:127`) | **NOT EXPOSED** | YES | **0 Contracts** | **0 Assets** | Migration + DTO + 12 Contracts |
| **`mars_sign`** (12 signs) | `swe.calc_ut` $\to$ `longitude_to_sign` | RAM ONLY (`natal.py:128`) | **NOT EXPOSED** | YES | **0 Contracts** | **0 Assets** | Migration + DTO + 12 Contracts |
| **`sun_longitude`..`pluto_longitude`** | `swe.calc_ut` (6 decimal precision) | IMPLEMENTED | **FORBIDDEN** (`astro_private`) | **NO** | N/A | N/A | Keep server-side only |
| **`houses`** (12 cusps) | `swe.houses(P)` (12 floats) | STORED | **FORBIDDEN** (`astro_private`) | **NO** | 0 Contracts | 0 Assets | No planet-in-house logic |
| **`retrogrades`** (10 flags) | `speed_lon < 0.0` (dict[str, bool]) | STORED | **NOT EXPOSED** (`astro_private`) | YES | 0 Contracts | 0 Assets | Uninterpreted |
| **Natal Internal Aspects** | `aspects.py:detect_aspect()` | DERIVABLE | **NOT EXPOSED** | YES | 0 Contracts | 0 Assets | Needs single-chart aspect loop |

---

## 3. SIGNAL CATEGORIZATION & FEASIBILITY FILTER

We divide all astrological representations into **4 Rigorous Categories**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ CATEGORY A: BASE ASTROLOGICAL SIGNALS (72 Signals)                          │
│ Direct planetary longitudes converted to Tropical Zodiac signs.             │
│ • 12 Sun Signs (Exposed)           • 12 Mercury Signs (In RAM, Ready)       │
│ • 12 Moon Signs (Exposed)          • 12 Venus Signs (In RAM, Ready)         │
│ • 12 Ascendant Signs (Exposed)     • 12 Mars Signs (In RAM, Ready)          │
├─────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY B: DERIVED STRUCTURAL SIGNALS (7 Signals)                          │
│ Deterministic mathematical derivations from multiple personal placements.    │
│ • 4 Dominant Elements (Fire, Earth, Air, Water)                             │
│ • 3 Dominant Modalities (Cardinal, Fixed, Mutable)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY C: VALID DETERMINISTIC SYNTHESIS (44 Dynamic Units)                │
│ Pairwise interactions between real signals that produce genuine contrasts.  │
│ • 16 Luminary Elemental Dynamics (Sun Element × Moon Element)               │
│ • 16 Persona Incongruence Dynamics (Sun Element × Ascendant Element)        │
│ • 12 Archetypal Verdict Syntheses (Dominant Element × Dominant Modality)    │
├─────────────────────────────────────────────────────────────────────────────┤
│ CATEGORY D: FUTURE / NOT IMPLEMENTED (Do Not Count in Matrix!)              │
│ Astrologically possible, but lacks code or engine caller.                   │
│ • Natal internal aspect pairs (e.g. Sun square Moon in chart A)             │
│ • Planet-in-house placements (e.g. Mars in 10th house)                      │
│ • Retrograde psychological effects (e.g. Mercury retrograde natal)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The 5-Question Feasibility Filter for Combinations
Before any combination is permitted to become a content target, it must pass all 5 gates:
1. **Does the underlying calculation exist in the codebase?**
2. **Is the combination strictly deterministic?**
3. **Does the combination produce a meaningful, distinct psychological interpretation?**
4. **Can the distinction be transparently explained from the underlying signals?**
5. **Is the distinction useful and perceptible to the user?**

#### Filter Example 1: Big Three Matrix ($12 \times 12 \times 12 = 1,728$ combinations)
- *Q1: Calculation exists?* YES (Sun, Moon, Asc signs exist).
- *Q2: Deterministic?* YES.
- *Q3: Meaningful distinct interpretation?* **NO.** Aries Sun + Taurus Moon + Gemini Rising does not have a fundamentally different life philosophy from Aries Sun + Taurus Moon + Libra Rising; the difference is simply the conversational entry style (Gemini vs Libra), which is already handled cleanly by Layer 3!
- *Verdict:* **FAILED. REJECTED AS AN INDEPENDENT CONTENT TARGET.**

#### Filter Example 2: Luminary Elemental Dynamic ($4 \times 4 = 16$ pairs)
- *Q1: Calculation exists?* YES (`ELEMENT_MAP[sun_sign]`, `ELEMENT_MAP[moon_sign]`).
- *Q2: Deterministic?* YES.
- *Q3: Meaningful distinct interpretation?* **YES.** Fire Sun + Water Moon (Steam) creates a palpable, observable internal tug-of-war: immediate outward drive and ego bravado clashing with sudden private retreats and hypersensitive emotional defensiveness.
- *Q4: Explainable?* YES (Fire is kinetic/expressive; Water is receptive/absorptive).
- *Q5: Useful to user?* YES (Directly explains why they feel like two different people).
- *Verdict:* **PASSED. APPROVED AS CATEGORY C SYNTHESIS TARGET.**

---

## 4. THE COMPLETE ME CONTENT MATRIX

Below is the definitive content target specification across all approved and planned signals:

| Signal ID / Family | Astrological Input | Semantic Domain | Supported Semantic Angles | Micro (1–2 sent) | Medium (1–3 para) | Deep (Narrative) | Target Tones | Recommended Variants / Tone | Total Recommended Assets | Priority |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| **`self.identity.sun_*`** (12) | `sun_sign` (Aries..Pisces) | Core Identity & Ego Motivation | 1. Vitality & Purpose<br>2. Ego Blind Spot<br>3. Instinctive Stance | YES | YES | YES | Snarky, Mocking, Unfiltered, Conversational | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P0** (Live) |
| **`self.emotional.moon_*`** (12) | `moon_sign` (Aries..Pisces) | Emotional World & Vulnerability | 1. Stress Reset<br>2. Defensive Reflex<br>3. Private Sanctuary | YES | YES | YES | Snarky, Soft, Unfiltered, Conversational | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P0** (Live) |
| **`self.persona.rising_*`** (12) | `ascendant_sign` (Aries..Pisces) | Social Interface & First Impression | 1. Entry Posture<br>2. Social Armor<br>3. Conversational Mask | YES | YES | NO | Snarky, Mocking, Dramatic, Conversational | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P0** (Live) |
| **`self.element.*_dominant`** (4) | `element_primary` (Fire..Water) | Structural Energy Baseline | 1. Metabolic Fuel<br>2. Energy Depletion | YES | YES | NO | Snarky, Cocky, Conversational | 3 | $4 \times 3 \times 3 = \mathbf{36}$ | **P0** (Live) |
| **`self.modality.*_dominant`** (3) | `modality_primary` (Card..Mut) | Operational Tempo & Strategy | 1. Action Tempo<br>2. Resistance to Change | YES | YES | NO | Snarky, Mocking, Conversational | 3 | $3 \times 3 \times 3 = \mathbf{27}$ | **P0** (Live) |
| **`self.cognition.mercury_*`** (12) | `mercury_sign` (Aries..Pisces) | Thinking, Speech & Debate Style | 1. Processing Speed<br>2. Debate Habit<br>3. Mental Bias | YES | YES | NO | Snarky, Mocking, Unfiltered, Conversational | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P1** (RAM Expose) |
| **`self.relating.venus_*`** (12) | `venus_sign` (Aries..Pisces) | Romantic Values & Attraction | 1. Relational Currency<br>2. Aesthetic Taste<br>3. Affection Armor | YES | YES | NO | Snarky, Playful, Unfiltered, Sarcastic | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P1** (RAM Expose) |
| **`self.action.mars_*`** (12) | `mars_sign` (Aries..Pisces) | Drive, Conflict & Assertiveness | 1. Conflict Stance<br>2. Stamina Deployment<br>3. Frustration Fuse | YES | YES | NO | Snarky, Unfiltered, Cocky, Dramatic | 2 | $12 \times 4 \times 2 = \mathbf{96}$ | **P1** (RAM Expose) |
| **`self.synthesis.element_dynamic.*`** (16) | `sun_element` $\times$ `moon_element` | Core Internal Contradictions | 1. Ego vs Emotion Tug-of-War<br>2. The Resolution Trick | YES | YES | YES | Snarky, Unfiltered, Dramatic, Conversational | 2 | $16 \times 4 \times 2 = \mathbf{128}$ | **P1** (Synthesis) |
| **`self.synthesis.persona_contrast.*`** (16) | `sun_element` $\times$ `asc_element` | Mask vs Core Incongruence | 1. The Trojan Horse Dynamic<br>2. What People Miss | YES | YES | NO | Mocking, Cocky, Unexpected, Conversational | 2 | $16 \times 4 \times 2 = \mathbf{128}$ | **P2** (Synthesis) |
| **`self.verdict.archetype_*`** (12) | `element_primary` $\times$ `modality_primary` | The JESTER Final Life Verdict | 1. Holistic Life Blind Spot<br>2. Signature Paradox | YES | YES | YES | Sarcastic Jester, Cocky, Dramatic | 2 | $12 \times 3 \times 2 = \mathbf{72}$ | **P1** (Verdict) |
| **TOTAL APPROVED BLUEPRINT** | **117 Unique Astrological Units** | — | — | — | — | — | — | — | **965 Approved Assets** | — |

---

## 5. SEMANTIC ANGLE SPECIFICATIONS

Every astrological signal supports a finite number of legitimate psychological angles. JESTER formalizes these angles to ensure variation represents genuine substance, not superficial rewording.

```
                    ASTROLOGICAL PLACEMENT (e.g. Moon in Scorpio)
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
   ANGLE 1: RESET                 ANGLE 2: DEFENSE                ANGLE 3: SANCTUARY
   "როგორ მშვიდდება"             "როგორ იცავს თავს"               "რა სჭირდება პირადში"
   Subconscious security needs    Instant boundary armor          The non-negotiable refuge
```

### Approved Angles by Placement Family

1. **Sun Signs (Core Identity):**
   - *Angle 1: Vitality & Purpose:* What energizes the ego; how significance is sought.
   - *Angle 2: Ego Blind Spot:* The fatal pride point; where self-justification turns into parody.
   - *Angle 3: Instinctive Stance:* Default approach when entering an empty room or starting a project.
2. **Moon Signs (Emotional Architecture):**
   - *Angle 1: Stress Reset:* The visceral coping mechanism when overwhelmed.
   - *Angle 2: Defensive Reflex:* How vulnerability is hidden (aggression, retreat, intellectualization, humor).
   - *Angle 3: Private Sanctuary:* What the emotional world demands behind closed doors.
3. **Ascendant Signs (Social Persona):**
   - *Angle 1: Entry Posture:* Physical and verbal entry style into unfamiliar social settings.
   - *Angle 2: The Social Filter:* What the persona deliberately shields from strangers.
4. **Mercury Signs (Cognition & Debate):**
   - *Angle 1: Processing Tempo:* How fast information is metabolized vs. analyzed.
   - *Angle 2: Debate Habit:* Tactical approach during disagreement (blunt force, evasion, relentless logic, emotional appeal).
5. **Venus Signs (Relational Instinct):**
   - *Angle 1: Relational Currency:* What makes this person feel genuinely respected and pursued.
   - *Angle 2: Affection Armor:* The test they silently administer before trusting someone.
6. **Mars Signs (Kinetic Drive & Conflict):**
   - *Angle 1: Conflict Stance:* How anger is deployed (explosive sprint, calculated freeze, passive-aggressive siege).
   - *Angle 2: Frustration Fuse:* What triggers immediate irritation and how stamina is recovered.
7. **Elemental Dynamics (Synthesis):**
   - *Angle 1: The Internal Civil War:* The exact friction point between conscious desire and subconscious reflex.
   - *Angle 2: The Coexistence Paradox:* How these two conflicting elements secretly feed each other.

---

## 6. DEPTH DEFINITION & FORMAT RULES

JESTER strictly regulates content depth to prevent verbose fluff:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MICRO DEPTH (1–2 Sentences | 100–250 characters)                            │
│ • Role: High-impact diagnostic punchline. Zero filler.                      │
│ • Structure: Observation + Biting Climax.                                   │
│ • Surfaces: Mobile overview cards, Discover feed hooks, Quick share stories.│
├─────────────────────────────────────────────────────────────────────────────┤
│ MEDIUM DEPTH (1–3 Paragraphs | 400–800 characters)                          │
│ • Role: Nuanced psychological anatomy. Explains the "why" and the quirk.   │
│ • Structure: Behavioral premise → The hidden defense mechanism → The verdict│
│ • Surfaces: Profile drawer, Chapter inspection, In-depth self dossier.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ DEEP DEPTH (Multi-Paragraph Narrative | 1,000–2,500 characters)             │
│ • Role: Full chapter immersion. Integrates placement with structural energy.│
│ • Structure: Comprehensive exploration with concrete behavioral archetypes. │
│ • Surfaces: "Full Dossier Reading", Exportable PDF Life Report.             │
└─────────────────────────────────────────────────────────────────────────────┘
```

*Depth Allocation Principle:* Only foundational pillars (Sun, Moon, Synthesis Dynamics, and JESTER Verdicts) warrant all three depths. Operational layers (Mercury, Venus, Mars, Ascendant, Elements) are capped at Micro and Medium to maintain narrative velocity.

---

## 7. THE 8 JESTER VOICES (DELIVERY MODES)

The JESTER personality delivers the truth with varying degrees of bite. Tone modifies the **framing**, never the **astrological fact**.

```
                           ASTROLOGICAL TRUTH
                      (e.g., Moon in Taurus resists being rushed)
                                         │
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
   😈 SNARKY                         🗣️ CONVERSATIONAL                 😏 COCKY
   "შენი 'სიმშვიდე' რეალურად         "მოდი სიმართლე ვთქვათ:            "შენი გაჩერება უფრო
   ტაქტიკური გაჯიუტებაა."            შენ დროს კი არ აფასებ,            მარტივია, ვიდრე შენი
                                     მოძრაობა გეზარება."               ადგილიდან დაძვრა."
```

### Voice Reference Table

| Voice / Mode | Georgian Label | Core Vocal Attitude | Best Used For | What It Must Never Do |
| :--- | :--- | :--- | :--- | :--- |
| **1. 😈 Snarky** | წაკბენს | Intellectual bite; exposes small hypocrisies with surgical precision. | Ego blind spots, debate habits, superficial claims. | Bully or insult physical traits. |
| **2. 😂 Mocking** | დაგცინის | Playful amusement at human predictability; treats drama as comedy. | Over-the-top reactions, stubborn rituals. | Diminish genuine grief or trauma. |
| **3. 🔥 Unfiltered** | თავს არ იკავებს | Raw, unpolished, zero euphemisms; cuts straight to the root motive. | Anger processing, conflict style, relationship tests. | Use profanity or cruel vulgarity. |
| **4. 😏 Cocky** | ზედმეტად დარწმუნებული | Diagnostic superiority; speaks as if human psychology is solved. | Intellectual arrogance, defense mechanisms. | Make provably false claims. |
| **5. 🎭 Dramatic** | ყველაფერს აძლიერებს | Shakespearean amplification of everyday minor inconveniences. | Impatience, aesthetic fussiness, pride injuries. | Sound like a cheap cartoon. |
| **6. 🗣️ Conversational** | რეალურ ადამიანივით | Late-night bar intimacy; speaks like a sharp friend without jargon. | Vulnerability resets, private emotional sanctuaries. | Sound like a generic therapist. |
| **7. ⚡ Unexpected** | ვერ ხვდები რას იზამს | Starts as a gentle compliment, ends in a psychological reality check. | Hidden talents, paradoxical contradictions. | Change the factual meaning. |
| **8. 🃏 Sarcastic Jester** | სარკასტული | Canonical detached irony; philosophical cynicism. | Chart verdicts, life paradoxes, elemental clashes. | Become monotone or depressing. |

---

## 8. REPETITION CONTROL & DEDUPLICATION ARCHITECTURE

To guarantee that a user reading their ME profile weekly or monthly experiences an alive, non-repetitive narrative:

### 1. Deterministic Session Hashing
Instead of random picking, JESTER selects assets via a deterministic compound hash:
$$\text{Asset Index} = \text{SHA256}(\text{user\_id} + \text{session\_epoch} + \text{interpretation\_id}) \pmod{N_{\text{available}}}$$
Where `session_epoch` updates on user-initiated refresh or monthly cycle. This maintains **100% reproducibility within a session** while providing **fresh variants across visits**.

### 2. Metaphor-Family Collision Avoidance
Every asset is tagged with its primary rhetorical device:
`tags: ["metaphor:fire_burn", "metaphor:tactical_siege", "metaphor:courtroom_trial", "metaphor:architectural_anchor"]`
When assembling the multi-chapter dossier:
- If Chapter 1 (Sun in Aries) selects an asset tagged `metaphor:fire_burn`, the assembler **strictly suppresses** `metaphor:fire_burn` in Chapter 2 (Mars) and Chapter 7 (Synthesis).
- The user will never read two fire metaphors in the same dossier.

### 3. Opening-Hook Blacklist
The assembler scans and enforces diverse sentence openings:
- Prohibits more than one asset in the dossier starting with a conditional clause ("როცა შენ...", "თუ ვინმე...").
- Forbids repetitive rhetorical questions ("იცი რატომ...?").
- **Permanently eliminates** the lazy AI cliché `"წარმოიდგინე სიტუაცია:"` across the entire corpus.

---

## 9. ORTHOGONALITY & INTER-LAYER DEDUPLICATION

A critical failure of amateur astrology apps is stating the exact same observation repeatedly under different headers:
- *Sun in Aries:* "You are impatient and love starting things."
- *Fire Dominant:* "You are energetic and hate waiting."
- *Mars in Aries:* "You take action quickly without thinking."

When combined, the user reads the same sentence three times!

### The JESTER Orthogonality Matrix

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WHO (Core Identity): Sun Sign                      │
│  Focuses purely on EGO DIRECTION and CREATIVE MOTIVATION.                   │
│  Forbidden from discussing kinetic stamina, debating speed, or anger.       │
├─────────────────────────────────────────────────────────────────────────────┤
│                          HOW (Operational Fuel): Dominant Element           │
│  Focuses purely on METABOLIC BURN RATE and RECOVERY PACE.                   │
│  Forbidden from claiming specific identity goals or relationship tastes.    │
├─────────────────────────────────────────────────────────────────────────────┤
│                          FEEL (Inner Reset): Moon Sign                      │
│  Focuses purely on VULNERABILITY DEFENSE and PRIVATE SECURITY.              │
│  Forbidden from discussing outward career ambition or public charisma.      │
├─────────────────────────────────────────────────────────────────────────────┤
│                          ACT (Kinetic Execution): Mars Sign                 │
│  Focuses purely on CONFLICT TACTICS and DECISION SPEED.                     │
│  Forbidden from discussing core self-worth or philosophical ideals.         │
└─────────────────────────────────────────────────────────────────────────────┘
```

*Rule of Cumulative Insight:* Each chapter answers a fundamentally different human question. The narrative is **cumulative**, never duplicative.

---

## 10. PERSONALIZED NARRATIVE ASSEMBLY MODEL

The full "ვინ ვარ მე?" dossier is assembled dynamically according to data availability:

```
                            THE JESTER LIFE DOSSIER
                                      │
    ┌─────────────────────────────────┼─────────────────────────────────┐
    ▼                                 ▼                                 ▼
CHAPTER 1: IDENTITY             CHAPTER 2: INNER LIFE             CHAPTER 3: ENGAGEMENT
[CURRENT]                       [CURRENT]                         [FUTURE — Phase 3.2]
• 1.1 Core Vitality (Sun)       • 2.1 Emotional Reset (Moon)      • 3.1 Cognitive Style (Mercury)
• 1.2 Fuel Baseline (Element)   • 2.2 The Internal Civil War      • 3.2 Love & Taste (Venus)
• 1.3 Action Tempo (Modality)     (Sun-Moon Synthesis)            • 3.3 Conflict & Drive (Mars)
                                                                  • 3.4 Outward Mask (Ascendant)*
    │                                 │                                 │
    └─────────────────────────────────┼─────────────────────────────────┘
                                      │
                                      ▼
                           CHAPTER 4: THE VERDICT
                           [FUTURE — Phase 3.2]
                           • 4.1 Native Strengths (Dominance)
                           • 4.2 Signature Blind Spot (Tension)
                           • 4.3 The Final JESTER Verdict (Synthesis)
```
*\*Note on Ascendant: Gracefully omitted if birth time is unknown (`precision="unknown"`). The narrative flows seamlessly from Drive (Mars) to the Verdict without broken cards.*

---

## 11. AUDIT OF THE EXISTING 1,815 GEORGIAN ASSETS

A line-by-line inspection of the 1,815 Georgian draft assets in `backend/app/interpretation/data/content_corpus.json` reveals the exact editorial status:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CURRENT GEORGIAN CORPUS BREAKDOWN                     │
│                                                                             │
│  Total Assets: 1,815 (All marked ai_draft, avg length: 194.8 chars)        │
│                                                                             │
│  ├── 🟢 KEEP (Grade-A):            ~290 assets (16.0%)                     │
│  │   Sharp, witty, culturally natural Georgian phrasing with genuine bite.  │
│  │                                                                          │
│  ├── 🟡 RECLASSIFY:                ~420 assets (23.1%)                     │
│  │   Good texts filed under wrong tones (e.g. marked witty, but soft/conv). │
│  │                                                                          │
│  ├── 🟠 REWRITE (Grade-B):         ~620 assets (34.2%)                     │
│  │   Salvageable premises marred by formulaic prefixes ("წარმოიდგინე...")   │
│  │   or weak, repetitive concluding clauses.                                │
│  │                                                                          │
│  └── 🔴 REJECT (Redundant/Trash):  ~485 assets (26.7%)                     │
│      Near-identical duplicates, generic horoscope fluff, or toothless text. │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Exact Action Plan for Existing Corpus
1. **Promote the Top ~290 Assets:** Conduct human editorial review and graduate them to `status: "approved"`.
2. **Clean the ~420 Reclassified Assets:** Re-tag tones and assign proper `semantic_angle` metadata.
3. **Trim the Synthetic Clones:** Delete the 485 redundant copy-paste variants to restore corpus hygiene.

---

## 12. RECOMMENDED CONTENT SCALE TARGETS

To answer the fundamental strategic question without inflated guessing:

### The 3 Production Scale Tiers

| Target Tier | Purpose & User Experience | Unique Targets Covered | Active Depths | Target Georgian Assets | Estimated English Assets | % Existing Corpus Reusable | New Copy Required |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Minimal Complete ME (MVP)** | Flawless, tight, zero-repetition baseline. Every user gets a sharp, fully customized 10-chapter dossier. | 43 (Live placements) | Micro only | **~350–450** | ~350 | ~20% of existing | ~150 micro-edits |
| **Tier 2: Production-Grade ME (Recommended)** | High-polish, multi-depth experience. Supports Micro and Medium narrative across all 117 units. Fresh reads over 3–6 months. | 117 (All units + Mer/Ven/Mar + Synthesis) | Micro + Medium | **~900–1,200** | ~900 | ~35% of existing | ~700 new assets |
| **Tier 3: High-Diversity Corpus** | Endless long-term discovery. Supports Deep long-form reports and full 8-tone palette. Never repeats over 12+ months. | 117 (Full matrix) | Micro + Medium + Deep | **~2,800–3,500** | ~2,800 | ~15% of existing | ~2,500 new assets |

---

## 13. THE CRITICAL QUESTION: "HOW MANY APPROVED ASSETS DO WE REALLY NEED?"

> **Question:** *"If we want a user to read ME repeatedly over months without seeing the same text often, how many APPROVED Georgian assets do we realistically need?"*

### The Forensic Answer: **~900 to 1,200 Approved Georgian Assets**

#### The Mathematical Proof:
1. **A single user's natal chart does NOT activate all 117 targets.** A single user activates exactly:
   - 1 Sun Sign
   - 1 Moon Sign
   - 1 Ascendant Sign (or null)
   - 1 Dominant Element
   - 1 Dominant Modality
   - 1 Mercury Sign
   - 1 Venus Sign
   - 1 Mars Sign
   - 1 Sun-Moon Elemental Dynamic
   - 1 Sun-Ascendant Dynamic
   - 1 JESTER Verdict Archetype
   - **Total Active Placements per User = Exactly 10 to 11 Astrological Targets.**
2. In a single full profile reading, the user consumes exactly **10 to 11 content assets**.
3. If each of the 117 astrological targets in JESTER has a pool of **8 to 10 approved assets** (spanning 2 depths $\times$ 4 core JESTER tones $\times$ 1–2 variants):
   $$117 \text{ Targets} \times 8\text{–}10 \text{ Assets} = \mathbf{936 \text{ to } 1,170 \text{ Total Assets}}$$
4. **The User Experience Result:**
   - On Visit 1: The user reads 10 specific assets.
   - On Visit 2 (1 month later): The deterministic session hash advances. The user reads 10 *completely different* assets describing the same natal truth with fresh metaphors and a different JESTER delivery mode.
   - On Visit 3, 4, 5, 6, 7, 8: **Zero sentence repetition.**
   - A user would have to read their full profile **8 to 10 times** over almost a year to see a repeated sentence!

**Conclusion:** We do NOT need 10,000 or 20,000 texts. A curated, razor-sharp, editorially bulletproof corpus of **~1,000 approved Georgian assets** makes JESTER feel completely inexhaustible, deeply intelligent, and psychologically devastating.

---

## 14. EXACT CONTENT GAPS

To reach the Tier 2 Production Target of ~1,000 approved assets, the exact copywriting gaps are:

1. **Medium-Depth Assets (1–3 Paragraphs):** Currently **0** exist. We need ~230 Medium assets across Sun, Moon, Mercury, Venus, Mars, and Synthesis.
2. **Cognitive / Mercury Assets:** Currently **0** exist. We need 96 assets (8 per sign).
3. **Relational / Venus Assets:** Currently **0** exist. We need 96 assets (8 per sign).
4. **Kinetic / Mars Assets:** Currently **0** exist. We need 96 assets (8 per sign).
5. **Synthesis (Sun-Moon Clash) Assets:** Currently **0** exist. We need 128 assets (8 per elemental pair).
6. **JESTER Verdict Assets:** Currently **0** exist. We need 72 assets (6 per element-modality archetype).
7. **Biting Voice Deficit:** Existing drafts skew 88% towards playful/soft. We must deliberately author Snarky, Mocking, Unfiltered, and Sarcastic variants.

---

## 15. EXACT NEXT STEP FOR CONTENT GENERATION

```
PHASE 3.2 EXECUTION ROADMAP:
├── Step 1: Database Migration (Expose mercury_sign, venus_sign, mars_sign in astro_safe_profile)
├── Step 2: Register the 36 Personal Planet Contracts & 16 Synthesis Contracts in contracts.py
├── Step 3: Author the Content Seed Batch:
│   ├── Batch A: Top 250 Approved Micro Assets (Graduated from current corpus)
│   ├── Batch B: 96 Mercury + 96 Venus + 96 Mars Micro Assets
│   ├── Batch C: 128 Elemental Synthesis Assets
│   └── Batch D: The 117 Medium-Depth Core Narrative Assets
└── Step 4: Implement the Dossier Narrative Assembler with Metaphor Repetition Control
```

---

### FINAL ARCHITECTURAL PRINCIPLE

> **QUALITY IS A MATHEMATICAL FUNCTION OF ACCURACY, NOT WORD COUNT.**  
> **JESTER WILL WIN BECAUSE ITS CLAIMS ARE ASTROLOGICALLY TRUE AND PSYCHOLOGICALLY UNSPAREABLE.**  
> **TRUTH > COVERAGE > VARIETY > VOLUME.**
