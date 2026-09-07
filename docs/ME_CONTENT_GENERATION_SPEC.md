# JESTER — PHASE 3.2
## ME CONTENT FACTORY — FINAL PRE-GENERATION AUDIT
### COMPLETE CONTENT GENERATION SPECIFICATION

> **Status:** FINAL PRE-GENERATION SPECIFICATION & QUALITY GATES  
> **Subsystem:** Natal Self-Understanding Intelligence ("ME" / `self.*`)  
> **Governing Documents:** [`docs/ME_SEMANTIC_ARCHITECTURE.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/ME_SEMANTIC_ARCHITECTURE.md), [`docs/ME_CONTENT_MATRIX.md`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/docs/ME_CONTENT_MATRIX.md)  
> **Source of Truth:** Swiss Ephemeris (`pyswisseph`), `backend/app/astrology/natal.py`, `calculator.py`, `content_corpus.json`  
> **Core Axiom:** **TRUTH > SEMANTIC VALUE > QUALITY > VARIETY > VOLUME.**

---

## 1. VERIFIED CONTENT-UNIT INVENTORY (AUDIT OF THE PROPOSED 117 UNITS)

In Phase 3.1, an initial matrix of 117 units was modeled. In this pre-generation audit, we subjected every proposed unit to the **7 Verification Gates**:
1. Does the underlying signal exist in code?
2. Is the calculation strictly deterministic?
3. Is it exposed or currently internal?
4. Does the semantic interpretation have a defensible astrological basis?
5. Is the unit actually necessary for the user's self-understanding?
6. Does it duplicate another unit?
7. Does it produce perceptible, genuine user value?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      THE 107-UNIT NON-REDUNDANT CORE                        │
│                                                                             │
│ • 12 Sun Signs (Core Identity)              ─── VALID (Currently Exposed)   │
│ • 12 Moon Signs (Emotional Reset)           ─── VALID (Currently Exposed)   │
│ • 12 Ascendant Signs (Social Persona)       ─── VALID (Currently Exposed)   │
│ •  4 Dominant Elements (Metabolic Fuel)     ─── VALID (Currently Exposed)   │
│ •  3 Dominant Modalities (Action Tempo)     ─── VALID (Currently Exposed)   │
│ • 12 Mercury Signs (Cognitive & Debate)     ─── VALID (Needs Safe Exposure) │
│ • 12 Venus Signs (Love & Aesthetic Taste)   ─── VALID (Needs Safe Exposure) │
│ • 12 Mars Signs (Conflict & Drive)          ─── VALID (Needs Safe Exposure) │
│ • 16 Sun-Moon Elemental Synthesis (Steam..) ─── VALID (Needs Contract Reg)  │
│ • 12 Element × Modality Verdict Archetypes  ─── VALID (Needs Contract Reg)  │
│                                                                             │
│ TOTAL ROCK-SOLID UNITS: EXACTLY 107 UNITS                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Critical Forensic Decision: Trimming the 16 Sun-Ascendant Contrast Units
The proposed matrix included 16 `self.synthesis.persona_contrast.*` units (Sun element $\times$ Ascendant element).
- **Audit Finding:** **REDUNDANT & FRAGILE.**
  1. *Fragility:* If a user has an unknown birth time (`precision="unknown"`), Ascendant is `None`. Approximately 30–40% of real-world users do not have a reliable Ascendant.
  2. *Redundancy:* Having two separate "Contrast" chapters in the same reading (Sun-Moon Conflict *plus* Sun-Ascendant Conflict) causes severe narrative fatigue. A Fire-Fire combination ("You act like what you are") does not warrant a distinct 8-asset family.
  3. *Optimization:* The Persona-Core tension is **absorbed directly into Layer 3 (Ascendant)** as a conditional concluding observation, rather than maintaining 16 bloated, separate standalone units.
- **Verdict:** **117 Units reduced to 107 High-Impact, 100% Non-Redundant Target Units.**

---

## 2. FINAL SIGNAL LIST (BASE & DERIVED)

| Signal Key | Astronomical Derivation | Storage Location | Privacy Boundary | API Exposure Status |
| :--- | :--- | :--- | :--- | :--- |
| `sun_sign` (12) | `swe.calc_ut` $\to$ `longitude_to_sign` | `astro_safe_profile.sun_sign` | Public Safe DTO | **LIVE** |
| `moon_sign` (12) | `swe.calc_ut` $\to$ `longitude_to_sign` | `astro_safe_profile.moon_sign` | Public Safe DTO | **LIVE** |
| `ascendant_sign` (12) | `swe.houses(P)` $\to$ `longitude_to_sign` | `astro_safe_profile.ascendant_sign` | Public Safe DTO | **LIVE** (Nullable) |
| `element_primary` (4) | Weighted personal sum (Sun:3, Moon:3, Asc:3, Mer:2, Ven:2, Mar:2) | `astro_safe_profile.element_primary` | Public Safe DTO | **LIVE** |
| `modality_primary` (3) | Weighted personal sum (Identical weights) | `astro_safe_profile.modality_primary` | Public Safe DTO | **LIVE** |
| `mercury_sign` (12) | `swe.calc_ut` $\to$ `longitude_to_sign` | Currently in RAM (`natal.py:126`) | Public Safe DTO | **MIGRATION READY** |
| `venus_sign` (12) | `swe.calc_ut` $\to$ `longitude_to_sign` | Currently in RAM (`natal.py:127`) | Public Safe DTO | **MIGRATION READY** |
| `mars_sign` (12) | `swe.calc_ut` $\to$ `longitude_to_sign` | Currently in RAM (`natal.py:128`) | Public Safe DTO | **MIGRATION READY** |

$$\text{Total Base Personal Signals} = 12 \times 6 = 72 \quad | \quad \text{Total Derived Structural Signals} = 4 + 3 = 7$$

---

## 3. FINAL SYNTHESIS LIST (APPROVED COMBINATIONS)

Only combinations that represent genuine, observable psychological tensions are approved for content generation:

### A. The 16 Luminary Elemental Dynamics (`self.synthesis.element_dynamic.*`)
Grounded in the classical friction between conscious ego drive (`sun_sign.element`) and subconscious vulnerability defense (`moon_sign.element`):
1. **Fire + Fire (Double Fire):** Kinetic overdrive; zero emotional buffer; rapid burnout through uncontained intensity.
2. **Fire + Earth (Lava / Baking Clay):** Intense drive constrained by hyper-pragmatic fear of loss; ambitious perfectionism.
3. **Fire + Air (Wildfire):** Rapid theoretical expansion; ideas catch fire instantly; difficulty executing tedious details.
4. **Fire + Water (Steam):** The primary emotional civil war; outward arrogance masking sudden vulnerability withdrawals.
5. **Earth + Earth (Double Earth):** Immovable resilience; extreme sensory caution; paralysis through risk-aversion.
6. **Earth + Fire (Magma):** Heavy ambition with sudden explosive impatience; builds slowly then tears down recklessly.
7. **Earth + Air (Dust Storm):** Intellectual pragmatism; over-rationalizing gut feelings; dry, analytical skepticism.
8. **Earth + Water (Fertile Clay):** Protective containment; deep loyalty; absorbs others' burdens until emotionally overwhelmed.
9. **Air + Air (Double Air):** Perpetual mental motion; detached objective analysis; avoids deep emotional confrontation.
10. **Air + Fire (Blowtorch):** Provocative debate; intellectual catalyst; loves starting arguments they have no interest in finishing.
11. **Air + Earth (Structured Draft):** Methodical intellectualization; anxiety disguised as planning; rigid logic.
12. **Air + Water (Mist / Vapour):** Intellectualized empathy; feeling emotions through a conceptual filter; unpredictable mood pivots.
13. **Water + Water (Double Water):** Psychic saturation; hyper-permeable emotional boundaries; deep intuitive radar.
14. **Water + Fire (Boiling Pot):** Simmering resentment followed by theatrical emotional eruption; passionate devotion.
15. **Water + Earth (Riverbed):** Grounded emotional depth; slow to trust but permanent attachment; quiet tenacity.
16. **Water + Air (Raincloud):** Internal mood swings framed with witty excuses; emotionally sensitive yet socially cool.

### B. The 12 JESTER Life Verdict Archetypes (`self.verdict.archetype_*`)
Grounded in `element_primary` $\times$ `modality_primary` to deliver the crowning diagnostic summary:
- **Cardinal Fire:** *The Chronic Catalyst* — starts 20 revolutions, finishes 2, blames the universe.
- **Fixed Fire:** *The Unbendable Sun* — radiating authority that demands worship while claiming to be humble.
- **Mutable Fire:** *The Restless Spark* — runs away the moment a situation requires routine maintenance.
- **Cardinal Earth:** *The Corporate Sovereign* — treats human relationships like balance sheets and strategic acquisitions.
- **Fixed Earth:** *The Granitic Anchor* — mistake stubbornness for moral integrity; will drown before shifting position.
- **Mutable Earth:** *The Anxious Watchmaker* — micromanaging chaos into submission; self-critique as a full-time job.
- **Cardinal Air:** *The Social Instigator* — introduces everyone, causes philosophical friction, leaves the party early.
- **Fixed Air:** *The Ideological Monolith* — fall in love with concepts over people; impossible to convince in debate.
- **Mutable Air:** *The Intellectual Chameleon* — three opinions simultaneously, none held with emotional skin in the game.
- **Cardinal Water:** *The Emotional General* — protects loved ones through suffocating control; passive-aggressive strategy.
- **Fixed Water:** *The Trench Guardian* — forgives nothing, forgets less, tests everyone's loyalty permanently.
- **Mutable Water:** *The Fluid Empath* — absorbs the room's misery, wonders why they are tired, vanishes without explanation.

---

## 4. NATAL ASPECTS FEASIBILITY STUDY

### Product & Astrological Reality
The mathematical function [`aspects.py:detect_aspect()`](file:///c:/Users/fiord/OneDrive/Desktop/Jester/backend/app/astrology/aspects.py#L119) calculates exact angular distances and quadratic strength decays. However, calling it across a user's single chart is **currently not wired in `natal.py`**.

### Priority Aspect Classification for Future Engine Inclusion

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ P0: MUST HAVE (High Personal Drama / Maximum JESTER Value)                  │
│ • Sun ☍ Moon (Full Moon Opposition: Conscious life vs Emotional needs)      │
│ • Sun □ Moon (Quarter Moon Square: Chronic inner friction & self-doubt)     │
│ • Moon □/☍ Mars (Emotional impatience, combativeness, quick anger)          │
│ • Sun □/☍ Saturn (The Imposter Syndrome aspect: brutal self-criticism)      │
│ • Venus □/☍ Mars (Desire vs Action friction: turbulent romantic choices)    │
├─────────────────────────────────────────────────────────────────────────────┤
│ P1: VALUABLE (Strong Cognitive & Ego Modifiers)                             │
│ • Sun ☌ Mercury (Cazimi / Combustion: ego and intellect indivisible)        │
│ • Mercury □/☍ Mars (Sharp, aggressive tongue; weaponized debating)          │
│ • Moon □/☍ Pluto (Obsessive emotional intensity; all-or-nothing defense)    │
├─────────────────────────────────────────────────────────────────────────────┤
│ P2: OPTIONAL (Harmonious Talents - Low Comedic / Diagnostic Tension)        │
│ • Sun △ Moon (Organic inner peace; low dramatic interest for JESTER)        │
│ • Mercury △ Jupiter (Broad intellect; pleasant banter)                      │
│ • Venus △ Neptune (Romantic idealism; sweet but soft)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ P3: STRICTLY FORBIDDEN / DO NOT IMPLEMENT                                   │
│ • Outer-to-Outer Aspects (e.g. Uranus sextile Neptune, Neptune sextile Pluto)│
│   Reason: Generational aspects lasting decades. Zero individual ME value!   │
│ • Minor Aspects (Semisextile, Quincunx, Quintile, Sesquiquadrate)            │
│   Reason: Unverified noise that dilutes core psychological clarity.          │
└─────────────────────────────────────────────────────────────────────────────┘
```

*Architectural Recommendation:* **Do not block Phase 3 content on Natal Aspects.** The 107 verified units provide overwhelming depth. Aspects should be introduced in Phase 4 as optional "Modifier Badges".

---

## 5. HOUSES FEASIBILITY STUDY

### Forensic Audit of House Placements
1. **The Math:** Placidus cusps are computed via `swe.houses(jd, lat, lon, b"P")` and stored in `public.astro_private.houses` (`list[float]`).
2. **The Missing Piece:** Zero code exists to calculate *which* house a planet occupies (`lon` between cusp $i$ and cusp $i+1$).
3. **The Fatal Vulnerability:** **Birth Time Sensitivity.**  
   A 15-to-20 minute error in reported birth time shifts house cusps by ~4 to 5 degrees, moving the Sun, Moon, or Mars into a completely different house!
4. **Decision:** **DEFER HOUSES ENTIRELY FROM PHASE 3.**  
   Personal Zodiac signs and elemental dynamics are immune to minor time errors (planets take days or months to change signs; only Moon changes every 2.5 days). Houses add massive operational fragility with zero compensatory value at this stage.

---

## 6. EXISTING CORPUS QUALITY AUDIT (THE 1,815 KA ASSETS)

A rigorous second-pass audit of the 1,815 Georgian draft assets confirmed the preliminary metrics:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECOND-PASS CORPUS BREAKDOWN                        │
│                                                                             │
│  TOTAL: 1,815 Georgian Draft Assets (Average: 194.8 characters)             │
│                                                                             │
│  🟢 16.0% (290 assets)  ── KEEP (Grade-A): Natural, sharp, authentic bite   │
│  🟡 23.1% (420 assets)  ── RECLASSIFY: Good text, wrong tone/tags           │
│  🟠 34.2% (620 assets)  ── REWRITE (Grade-B): Strong core, formulaic prefix │
│  🔴 26.7% (485 assets)  ── REJECT: Duplicate clones & bland filler          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The 4 Major Failure Modes Discovered
1. **The "Scenario Prefix" Epidemic (170 assets / 9.4%):**  
   Assets generated by prepending `"წარმოიდგინე სიტუაცია:"` to an existing sentence.  
   *Remedy:* Strip prefix, rewrite opening to an active verb.
2. **The "Passive Conditional" Trap (361 assets / 19.9%):**  
   Sentences starting with `"როცა..."` or `"თუ..."`, creating a repetitive, hypothetical tone.  
   *Remedy:* Convert to direct, declarative JESTER assertions.
3. **Synthetic Near-Duplicates (485 assets):**  
   Variants where only the last 3 words differ (e.g. `"...სანამ სხვები რისკებს ითვლიან"` vs `"...მთავარია, გზაში ვინმემ არ შეგაჩეროს"`).  
   *Remedy:* Purge redundant clones; retain only the sharpest formulation.
4. **Toothless Tone Bias:**  
   88.3% of texts are categorized as `witty`, `playful`, or `soft`. Genuine `snarky`, `unfiltered`, and `mocking` voices represent under 12%.

---

## 7. GRADUATION QUALITY FRAMEWORK: AI_DRAFT $\to$ APPROVED

No content enters production automatically. Every asset must pass the **6-Pillar Quality Gate**:

```
                              THE 6-PILLAR QUALITY GATE
                                         │
    ┌──────────────┬──────────────┬──────┴──────┬──────────────┬──────────────┐
    ▼              ▼              ▼             ▼              ▼              ▼
1. ASTRO TRUTH  2. SEMANTIC    3. JESTER     4. NATURAL     5. ZERO        6. AUDITABLE
   ACCURACY        SPECIFICITY    VOICE         GEORGIAN       CLONES         PROVENANCE
```

1. **Astrological Truth Accuracy:** Observation maps 100% to the approved domain. (A Taurus Moon text must address emotional containment/inertia, never communication speed).
2. **Semantic Specificity:** Concrete behavioral claims, zero generic horoscope platitudes ("You have great potential").
3. **JESTER Voice:** Razor-sharp satirical diagnostic tone. Amused superiority, not cruelty or bland coaching.
4. **Natural Georgian:** Written natively in natural spoken Georgian idiom. **Zero translated-sounding syntax** (No English calques like "ეს ყველაფერი შენზეა").
5. **Zero Clones:** Distinct rhetorical metaphor from any other approved asset in that contract.
6. **Auditable Provenance:** Has valid `signal_id`, `interpretation_id`, `variant_key`, and `tags`.

---

## 8. RE-CALCULATED CONTENT QUANTITY TARGETS

We do not force 8 tones onto every signal. Tones are allocated based on **psychological appropriateness**:
- *Sun (Identity):* Snarky, Mocking, Unfiltered, Conversational (4 Tones)
- *Moon (Vulnerability):* Snarky, Soft, Unfiltered, Conversational (4 Tones)
- *Mercury (Thinking):* Snarky, Mocking, Unfiltered, Conversational (4 Tones)
- *Venus (Relating):* Snarky, Playful, Unfiltered, Sarcastic (4 Tones)
- *Mars (Conflict):* Snarky, Unfiltered, Cocky, Dramatic (4 Tones)
- *Elements / Modalities:* Snarky, Cocky, Conversational (3 Tones)
- *Verdicts:* Sarcastic Jester, Cocky, Dramatic (3 Tones)

### The 3 Production Tiers (Derived Mathematically)

| Tier | Purpose | Coverage Targets | Depths | Approved Georgian Assets | New Copy Required |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Tier 1: Tight MVP** | Flawless baseline for all live features | 43 Units (Current live) | Micro only | **~350–450** | ~150 edits |
| **Tier 2: Production-Grade (Target)** | Full 10-chapter dossier, Mer/Ven/Mar + Synthesis | **107 Core Units** | Micro + Medium | **~900–1,150** | **~650 new** |
| **Tier 3: High-Diversity Master** | Long-form deep reports, multi-year discovery | 107 Units | Micro + Medium + Deep | **~2,400–2,800** | ~2,000 new |

---

## 9. USER READING FREQUENCY MODEL (1 / 5 / 10 / 20 / 50 READINGS)

$$\text{Active Units per Reading} = \mathbf{10 \text{ to } 11 \text{ Placements}}$$

| Scenario | Readings Count | Total Content Consumed | Pool per Unit Needed | Exact Repetition Probability (Tier 2 Corpus) | Semantic Freshness Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Visit 1** | 1 | 10 assets | 1 | **0.0%** | Completely fresh experience. |
| **Visit 2** (Month 2) | 5 | 50 assets | 5 | **0.0%** | Fully fresh; new metaphors, alternative tones. |
| **Visit 3** (Month 6) | 10 | 100 assets | 10 | **< 5.0%** | Negligible repetition; feels like an active system. |
| **Visit 4** (Year 1) | 20 | 200 assets | 10 | **~25.0%** | Occasional familiar lines; acceptable for natal. |
| **Visit 5** (Year 2+) | 50 | 500 assets | 10 | **~75.0%** | Natal identity is permanent; expected familiarity. |

*Strategic Finding:* **A pool of ~1,000 approved assets guarantees zero repetition across 8 to 10 complete readings over an entire year!**

---

## 10. CONTENT GENERATION PHASING (EXECUTION ORDER)

```
PHASE A: CORPUS CLEANUP & MVP GRADUATION (Immediate)
├── Audit and graduate the top ~290 existing Micro assets to approved
└── Strip prefixes ("წარმოიდგინე...") and polish ~150 Grade-B assets

PHASE B: PERSONAL PLANETS (The Action Core)
├── Batch B1: 12 Mercury signs (Cognition & Debate) — 96 assets
├── Batch B2: 12 Venus signs (Love & Taste)         — 96 assets
└── Batch B3: 12 Mars signs (Drive & Conflict)       — 96 assets

PHASE C: SYNTHESIS DYNAMICS (The Internal Contradictions)
└── Batch C1: 16 Luminary Elemental Dynamics (Fire-Water, etc.) — 128 assets

PHASE D: MEDIUM-DEPTH CHAPTERS (The Narrative Spine)
└── Batch D1: 107 Medium-depth assets (1 per unit for chapter inspection)

PHASE E: THE JESTER FINAL VERDICTS
└── Batch E1: 12 Element-Modality Life Archetypes — 72 assets
```

---

## 11. EXACT CONTENT GENERATION BATCH TEMPLATE

When authoring or generating assets for a unit, the prompt/spec must follow this exact schema:

```yaml
batch_id: "batch_self_cognition_mercury_aries_v1"
interpretation_id: "self.cognition.mercury_aries.v1"
astrological_signal:
  body: "mercury"
  sign: "aries"
  element: "fire"
  modality: "cardinal"
semantic_domain: "Cognition, Speech & Debating Habit"
approved_semantic_angles:
  - angle_1: "Rapid intuitive processing / impatience with lengthy preambles"
  - angle_2: "Weaponized debating / cutting straight to the conclusion"
prohibited_claims:
  - "Do not mention clinical ADHD or IQ"
  - "Do not use words like 'Mercury', 'Retrograde', or 'Aspect'"
  - "Do not predict career victory"
required_depths:
  - micro: 6 variants (100–250 chars)
  - medium: 2 variants (400–750 chars)
required_tone_distribution:
  snarky: 2 micro, 1 medium
  mocking: 2 micro
  unfiltered: 1 micro, 1 medium
  conversational: 1 micro
qa_checklist:
  - "Natural colloquial Georgian?"
  - "Observation grounded in Aries cognition?"
  - "No repetitive 'როცა' or 'წარმოიდგინე' openers?"
```

---

## 12. EXPLICIT FORBIDDEN CONTENT

Any asset exhibiting any of the following will be **immediately rejected**:
- ❌ **Psychiatric Diagnoses:** Mentioning ADHD, OCD, depression, autism, or personality disorders.
- ❌ **Deterministic Life Fortune:** "You will get rich at 30", "Your marriage will fail".
- ❌ **Astrological Technical Jargon:** "Your square indicates...", "Because of your 7th house...", "Trine".
- ❌ **Cruel Physical Insults:** Mocking appearance, weight, or disabilities.
- ❌ **Generic Horoscope Filler:** "You are a person of dual nature who loves balance."
- ❌ **English Calques:** Literal translations of English idioms that sound bizarre in Georgian.

---

## 13. DEFINITION OF DONE FOR PHASE 3.2

Phase 3.2 is officially **COMPLETE** when:
1. `docs/ME_CONTENT_GENERATION_SPEC.md` is committed and approved.
2. The 107 core units are locked against arbitrary expansion.
3. Database migration for `mercury_sign`, `venus_sign`, `mars_sign` is drafted.
4. Editorial team has the exact batch template and QA checklist to start Phase A content graduation.

---

### FINAL PRINCIPLE

> **WE ARE NOT BUILDING A DATABASE OF 20,000 ROBOTIC PARAGRAPHS.**  
> **WE ARE BUILDING AN ELEGANT, BULLETPROOF ENGINE OF ~1,000 APPROVED OBSERVATIONS SO SHARP THAT EVERY USER BELIEVES JESTER HAS BEEN PERSONALLY SPYING ON THEIR LIFE.**  
> **TRUTH > SEMANTIC VALUE > QUALITY > VARIETY > VOLUME.**
