# JESTER Semantic Universe V1 Specification

**Status**: Frozen Specification / V1 Authoritative  
**Domain**: People Discovery & Relationship Intelligence  
**Author**: Jester Product & Content Architecture  
**Last Updated**: September 2026  

---

## 1. Executive Summary & Semantic Principles

JESTER is not positioned as an astrology app. Astrology serves strictly as the underlying, deterministic intelligence layer:
> **"They show the match. JESTER explains the connection."**

To maintain absolute architectural integrity, the system enforces a strict four-layer pipeline:
```text
ASTROLOGICAL TRUTH (Swiss Ephemeris / PySwissEph)
       ↓
DETERMINISTIC SIGNAL (Aspects, Longitudes, Modalities, Elements)
       ↓
SEMANTIC INTERPRETATION CONTRACT (Semantic Meaning & Domain Invariant)
       ↓
JESTER VOICE CONTENT LAYER (Witty, Playful, Observant Copy Assets)
       ↓
RESOLVED USER EXPERIENCE (Resolved Client Copy)
```

### Critical Architectural Rule: Semantic Meaning vs. Content Asset
* **Semantic Interpretation Contract**: Represents *what* the connection or trait means in human relational terms (e.g., `relationship.attraction.mars_mars_friction.v1`). It is immutable in meaning and decoupled from wording.
* **Content Asset**: Represents *how* that meaning is voiced to a user in a specific locale, context, and tone (e.g., Georgian witty onboarding copy vs. English playful discovery copy).

---

## 2. Semantic Universe Metrics

| Semantic Domain | Contract Count | Underlying Engine Subsystem | Operational Status |
| :--- | :--- | :--- | :--- |
| **Self / Me (Identity, Emotion, Persona, Elements)** | **43** | `backend/app/astrology/calculator.py` | **100% Operational** |
| **Relationship / Synastry (Chemistry, Emotion, Friction)** | **46** (45 core + 1 v2 alias) | `backend/app/compatibility/synastry.py` | **100% Operational** |
| **Friendship / Platonic (Social, Humor, Ease)** | **12** | `backend/app/astrology/aspects.py` & Synastry signals | **100% Operational** |
| **Daily Energy (Transit Archetypes)** | **12** | `backend/app/astrology/transits.py` (Architectural Contract) | **Semantic Ready / Engine Stub** |
| **TOTAL REGISTERED CONTRACTS** | **113** | — | — |

---

## 3. Domain A: Self / Me (43 Core Contracts)

The purpose of the Self/Me contracts is **not** to output generic horoscope traits ("You are an Aries, therefore you are bold"). The purpose is:
> **"Give JESTER something interesting, specific, human, and recognizable to notice about the user."**

All 43 contracts are derived strictly from deterministic natal calculations in `calculator.py`:

### 3.1 Sun Sign Identity (12 Contracts)
* **Signal Source**: Natal Sun Tropical Longitude ($0^\circ - 360^\circ \to \text{Zodiac Sign}$)
* **Contexts**: `self`, `natal`, `discovery`, `onboarding`, `share`
* **Priority**: 60

| Interpretation ID | Sign | Core Human Observation |
| :--- | :--- | :--- |
| `self.identity.sun_aries.v1` | Aries | Direct forward drive; impatience with hesitation; prefers starting over waiting. |
| `self.identity.sun_taurus.v1` | Taurus | Deliberate pacing, sensory grounding, unhurried persistence under pressure. |
| `self.identity.sun_gemini.v1` | Gemini | Rapid mental pivoting, conversational curiosity, dual perspectives. |
| `self.identity.sun_cancer.v1` | Cancer | Protective intuition, loyalty to inner circle, emotional retention. |
| `self.identity.sun_leo.v1` | Leo | Natural presence, warmth, generous dramatic flair without false modesty. |
| `self.identity.sun_virgo.v1` | Virgo | Observant discernment, practical refinement, instinctive error correction. |
| `self.identity.sun_libra.v1` | Libra | Relational equilibrium, aesthetic balance, instinctive social diplomacy. |
| `self.identity.sun_scorpio.v1` | Scorpio | Psychological penetration, silent focus, allergic to superficiality. |
| `self.identity.sun_sagittarius.v1` | Sagittarius | Philosophical restlessness, unfiltered candor, quest for expansive horizons. |
| `self.identity.sun_capricorn.v1` | Capricorn | Strategic endurance, dry realism, architectural discipline toward long goals. |
| `self.identity.sun_aquarius.v1` | Aquarius | Intellectual independence, contrarian clarity, detached objectivity. |
| `self.identity.sun_pisces.v1` | Pisces | Fluid empathy, boundary-permeable intuition, poetic inner landscape. |

### 3.2 Moon Sign Emotional Processing (12 Contracts)
* **Signal Source**: Natal Moon Tropical Longitude ($0^\circ - 360^\circ \to \text{Zodiac Sign}$)
* **Contexts**: `self`, `natal`, `deep_analysis`
* **Priority**: 55

| Interpretation ID | Moon Sign | Emotional Processing Style |
| :--- | :--- | :--- |
| `self.emotion.moon_aries.v1` | Aries | Instant emotional reaction, quick combustion, clean release with zero grudges. |
| `self.emotion.moon_taurus.v1` | Taurus | Rhythmic emotional digestion, need for tactile and environmental stability. |
| `self.emotion.moon_gemini.v1` | Gemini | Verbalizing feelings, intellectualizing mood shifts, talking through tensions. |
| `self.emotion.moon_cancer.v1` | Cancer | Deep emotional tide, visceral memory of tone and atmosphere, instinct to nest. |
| `self.emotion.moon_leo.v1` | Leo | Needs emotional recognition, generous with loved ones, bruised by cold indifference. |
| `self.emotion.moon_virgo.v1` | Virgo | Solves emotions like puzzles, somatic worry, manifests care through practical acts. |
| `self.emotion.moon_libra.v1` | Libra | Seeks harmony to regulate mood, weighs options endlessly, abhors raw conflict. |
| `self.emotion.moon_scorpio.v1` | Scorpio | Private intense processing, high emotional radar, long memory for betrayals. |
| `self.emotion.moon_sagittarius.v1` | Sagittarius | Emotional reframing through optimism, claustrophobia when boxed in by heavy moods. |
| `self.emotion.moon_capricorn.v1` | Capricorn | Stoic composure, self-reliant sorrow, processes pressure behind closed doors. |
| `self.emotion.moon_aquarius.v1` | Aquarius | Abstracted emotional analysis, needs mental space before admitting vulnerability. |
| `self.emotion.moon_pisces.v1` | Pisces | Absorptive empathy, porous emotional boundaries, heals through solitude or art. |

### 3.3 Ascendant Social Persona (12 Contracts)
* **Signal Source**: Exact Birth Time + Geolocation $\to$ Topocentric Ascendant Longitude.
* **Important**: When `birth_time_precision == 'unknown'`, Ascendant is `None`, and these contracts are omitted from personal resolution.
* **Contexts**: `self`, `natal`, `discovery`, `onboarding`
* **Priority**: 58

| Interpretation ID | Rising Sign | First Impression / Room Presence |
| :--- | :--- | :--- |
| `self.persona.asc_aries.v1` | Aries | Enter rooms head-first; brisk physical tempo; immediate energetic presence. |
| `self.persona.asc_taurus.v1` | Taurus | Grounded stillness; unhurried posture; calming, solid initial presence. |
| `self.persona.asc_gemini.v1` | Gemini | Animated expressions; scanning gaze; quick conversational greeting. |
| `self.persona.asc_cancer.v1` | Cancer | Gentle guarded approach; observational warmth; reads room temperature first. |
| `self.persona.asc_leo.v1` | Leo | Natural room magnetism; upright carriage; radiant, expressive greeting. |
| `self.persona.asc_virgo.v1` | Virgo | Clean precision; understated poise; quietly assesses environment and details. |
| `self.persona.asc_libra.v1` | Libra | Charming diplomacy; gracious eye contact; creates immediate aesthetic ease. |
| `self.persona.asc_scorpio.v1` | Scorpio | Laser gaze; magnetic reserve; projects quiet authority and controlled mystery. |
| `self.persona.asc_sagittarius.v1` | Sagittarius | Expansive stride; open infectious humor; enters room as if arriving at an adventure. |
| `self.persona.asc_capricorn.v1` | Capricorn | Measured composure; professional gravitas; commands respect without loudness. |
| `self.persona.asc_aquarius.v1` | Aquarius | Unconventional style; observant detachment; approachable yet distinctly original. |
| `self.persona.asc_pisces.v1` | Pisces | Soft-focus aura; gentle, chameleon-like adaptability; dreamlike presence. |

### 3.4 Elemental Balance (4 Contracts)
* **Signal Source**: Sum of planetary placements weighted across 4 Triplicities.
* **Contexts**: `self`, `natal`, `discovery`
* **Priority**: 50

| Interpretation ID | Dominant Element | Behavioral Synthesis |
| :--- | :--- | :--- |
| `self.element.fire_dominant.v1` | Fire | High kinetic drive, contagious initiative, low tolerance for stagnancy. |
| `self.element.earth_dominant.v1` | Earth | Tangible results over theory, rhythmic endurance, grounded pragmatism. |
| `self.element.air_dominant.v1` | Air | Conceptual velocity, social cross-pollination, living in the exchange of ideas. |
| `self.element.water_dominant.v1` | Water | Visceral contextual radar, intuitive absorption, navigating by emotional tone. |

### 3.5 Modality Dynamics (3 Contracts)
* **Signal Source**: Sum of planetary placements weighted across 3 Quadruplicities.
* **Contexts**: `self`, `natal`, `discovery`
* **Priority**: 48

| Interpretation ID | Dominant Modality | Operational Style |
| :--- | :--- | :--- |
| `self.modality.cardinal_dominant.v1` | Cardinal | The initiator: sets things into motion, prefers launching over maintenance. |
| `self.modality.fixed_dominant.v1` | Fixed | The anchor: formidable staying power, builds institutions, hates abrupt redirection. |
| `self.modality.mutable_dominant.v1` | Mutable | The adapter: flexible navigation, pivots gracefully when circumstances shift. |

---

## 4. Domain B: Relationship / Synastry (46 Contracts)

Relational contracts translate angular cross-aspects and synastry dynamics calculated by `synastry.py` and `aspects.py` into human dynamics:

### 4.1 Chemistry & Attraction Dynamics
* `relationship.attraction.strong_chemistry.v1` (Venus-Mars conjunction/trine/sextile) — Electric physical resonance.
* `relationship.attraction.strong_chemistry.v2` — Backward-compatibility alias.
* `relationship.attraction.magnetic_pull.v1` (Sun-Venus / Ascendant-Venus) — Warm mutual aesthetic charm.
* `relationship.attraction.intense_magnetism.v1` (Venus-Pluto) — Hypnotic depth, high-stakes mutual fascination.
* `relationship.attraction.warm_affection.v1` (Sun-Venus harmony) — Easy affectionate sweetness.
* `relationship.attraction.energized_collaboration.v1` (Sun-Mars trine) — Synchronized drive and joint ambition.
* `relationship.attraction.dynamic_drive.v1` (Mars-Jupiter) — Adventurous escalation and active momentum.
* `relationship.attraction.mars_mars_friction.v1` (Mars-Mars square/opposition) — Sparks and sparring; competitive chemistry.
* `relationship.attraction.venus_uranus_fascination.v1` (Venus-Uranus aspect) — Unconventional spark, zero boredom, unpredictable attraction.
* `relationship.attraction.moon_mars_attraction.v1` (Moon-Mars cross-aspect) — Visceral raw chemistry, emotional urgency.

### 4.2 Emotional Processing & Deep Resonance
* `relationship.emotional.deep_resonance.v1` (Moon-Moon trine/sextile) — Telepathic emotional comfort, shared internal rhythms.
* `relationship.emotional.moon_neptune_empathy.v1` (Moon-Neptune harmony) — Boundless empathy, romantic idealization, unspoken tenderness.
* `relationship.emotional.moon_pluto_intensity.v1` (Moon-Pluto aspect) — Uncompromising psychological bonding, raw vulnerability.
* `relationship.harmony.gentle_affinity.v1` (Moon-Sun trine) — Natural psychological balance between willpower and feeling.
* `relationship.harmony.generous_affection.v1` (Venus-Jupiter) — Lavish warmth, mutual spoiling, lighthearted generosity.

### 4.3 Communication & Intellectual Synergy
* `relationship.communication.intellectual_flow.v1` (Mercury-Mercury trine) — Rapid ping-pong dialogue, effortless mutual understanding.
* `relationship.communication.mutual_understanding.v1` (Sun-Mercury conjunction/trine) — Speaking the same conceptual dialect.
* `relationship.communication.mercury_moon_connection.v1` (Mercury-Moon aspect) — Translating gut feelings into crystal clear words.
* `relationship.communication.mercury_mars_banter.v1` (Mercury-Mars aspect) — Sharp wit, lightning-fast banter, debating as foreplay.
* `relationship.communication.mercury_saturn_precision.v1` (Mercury-Saturn aspect) — Serious deliberation, structured agreements, candid realism.

### 4.4 Friction, Power & Growth Tensions
* `relationship.growth.contrasting_perspectives.v1` (Sun-Sun square/opposition) — Different lenses on life; productive counterweight.
* `relationship.growth.ego_friction.v1` (Sun-Mars square) — Two drivers in one cockpit; learning when to yield.
* `relationship.growth.pacing_tension.v1` (Mars-Saturn aspect) — Gas pedal vs. brake pedal; finding rhythmic calibration.
* `relationship.growth.dynamic_spark.v1` (Venus-Mars square) — Friction that prevents complacency; exciting tension.
* `relationship.growth.mars_pluto_power.v1` (Mars-Pluto aspect) — Intense willpower showdown; learning shared sovereignty.
* `relationship.growth.venus_saturn_caution.v1` (Venus-Saturn aspect) — Guarded affection, slow-earned trust, fear of vulnerability.
* `relationship.growth.sun_saturn_testing.v1` (Sun-Saturn aspect) — Demanding accountability, reality testing, building true endurance.

### 4.5 Long-Term Grounding, Shared Visions & Independence
* `relationship.stability.long_term_grounding.v1` (Sun-Saturn trine) — Rock-solid reliability, mutual commitments kept.
* `relationship.stability.shared_optimism.v1` (Sun-Jupiter trine) — Expansive shared vision, mutual elevation, generous leeway.
* `relationship.stability.jupiter_saturn_balance.v1` (Jupiter-Saturn cross-aspect) — The visionary meets the builder; grounded expansion.
* `relationship.notice.independent_dynamics.v1` (Uranus prominent aspects) — Mutual respect for personal autonomy and freedom.
* `relationship.notice.sun_neptune_idealism.v1` (Sun-Neptune aspect) — Seeing the poetic highest self in one another.
* `relationship.notice.moon_uranus_surprise.v1` (Moon-Uranus aspect) — Unexpected emotional revelations, spontaneous resets.

### 4.6 Overall Synastry Balance Tiers
* `relationship.overall.exceptional_flow.v1` (Overall score $\ge 85$) — Rare effortless harmony across major life vectors.
* `relationship.overall.balanced_synergy.v1` (Overall score $70-84$) — Healthy equilibrium of comfort and stimulating contrast.
* `relationship.overall.stimulating_friction.v1` (Overall score $55-69$) — Dynamic growth engine fueled by difference.
* `relationship.overall.independent_paths.v1` (Overall score $< 55$) — Divergent operating models requiring conscious bridge-building.

---

## 5. Domain C: Friendship / Platonic (12 Dedicated Contracts)

Friendship contracts re-frame underlying astrological signals for platonic peer relationships. A friend pairing does not seek romance; it seeks banter, loyalty, social rhythm, and mutual respect.

| Interpretation ID | Underlying Signal | Platonic Framing |
| :--- | :--- | :--- |
| `friendship.chemistry.social_spark.v1` | Sun-Mars / Mars-Jupiter | High energy peer fun, spontaneous schemes, immediate camaraderie. |
| `friendship.communication.conversational_ease.v1` | Mercury-Mercury trine | Seamless dialogue, 3-hour conversations about everything and nothing. |
| `friendship.humor.shared_banter.v1` | Mercury-Mars / Mercury-Uranus | Savage inside jokes, deadpan comedic timing, ruthless banter. |
| `friendship.rhythm.effortless_pacing.v1` | Sun-Sun harmonious | Picking up right where you left off after six months of silence. |
| `friendship.support.mutual_loyalty.v1` | Sun-Saturn / Moon-Saturn trine | The 3 AM emergency call; dependable loyalty that doesn't waver. |
| `friendship.trust.unspoken_understanding.v1` | Moon-Moon harmony | Reading each other's glances in awkward social settings without a word. |
| `friendship.independence.low_maintenance.v1` | Uranus-Sun aspects | Zero guilt trips, complete freedom, low-maintenance connection. |
| `friendship.social.group_catalyst.v1` | Jupiter-Ascendant / Sun-Jupiter | The life of the group; elevates gatherings into unforgettable nights. |
| `friendship.intellect.stimulating_debates.v1` | Mercury-Jupiter / Mercury-Pluto | Passionate philosophical arguments that end in hearty laughter over drinks. |
| `friendship.comfort.safe_haven.v1` | Moon-Venus / Moon-Neptune | Decompressing in silence, safe from social performance pressure. |
| `friendship.friction.playful_sparring.v1` | Mars-Mars square / Sun-Mars | Competitive gaming/sports rivals who sharpen each other's edge. |
| `friendship.balance.complementary_allies.v1` | Modality/Element balance | The strategist and the executor; perfectly paired operational partners. |

---

## 6. Domain D: Daily Energy / Transits (12 Contracts)

> [!IMPORTANT]
> **Separation of Architectural Contract from Calculation Engine**:
> `backend/app/astrology/transits.py` is currently an uncalculated stub. The 12 Daily Energy contracts are registered to define the product semantics for future transit calculation. In V1, they resolve deterministically based on transit state flags and mock seeds for UX testing, with zero false claims of live astronomical calculations.

| Interpretation ID | Transit Archetype | Psychological Focus |
| :--- | :--- | :--- |
| `daily_energy.confidence.elevated.v1` | Sun-Mars transit | Assertive drive, room-taking confidence, high initiative. |
| `daily_energy.confidence.steady.v1` | Sun-Saturn trine transit | Grounded resilience, quiet self-assurance, practical momentum. |
| `daily_energy.communication.direct.v1` | Mercury-Mars transit | Razor-sharp messaging, zero fluff, direct negotiations. |
| `daily_energy.communication.reflective.v1` | Mercury-Neptune transit | Intuitive processing, listening between the lines, quiet reading. |
| `daily_energy.focus.scattered.v1` | Mercury-Uranus transit | Idea tsunami, restless attention, brilliant nonlinear insights. |
| `daily_energy.focus.laser_sharp.v1` | Mercury-Saturn transit | Flawless task execution, deep work focus, structural pruning. |
| `daily_energy.creativity.exploration.v1` | Venus-Uranus transit | Breaking routine aesthetics, divergent artistic experimentation. |
| `daily_energy.creativity.grounded.v1` | Venus-Saturn transit | Turning inspiration into tangible form; craftsmanship. |
| `daily_energy.social.magnetic.v1` | Venus-Jupiter transit | Natural charm, effortless social warmth, open doors. |
| `daily_energy.social.selective.v1` | Moon-Saturn transit | Social battery conservation, selective company, introverted recharge. |
| `daily_energy.resilience.fortified.v1` | Mars-Pluto transit | Unstoppable endurance, cutting through obstacles, fierce resolve. |
| `daily_energy.rest.contemplative.v1` | Moon-Neptune transit | Dreamy introspection, slowing down, subconscious integration. |

---

## 7. Unsupported Astrological Categories & Known Limitations

In accordance with **AGENTS.md Rule #1 (Source of Truth)** and strict astrology transparency:

### 7.1 Unsupported Astronomical Placements
The following points are **NOT** calculated by `calculator.py` and must never be referenced in semantic contracts:
1. **Chiron / Asteroids**: No Ceres, Pallas, Juno, Vesta, or Chiron calculations exist.
2. **Lunar Nodes (True/Mean Rahu & Ketu)**: Not present in the ephemeris pipeline.
3. **Lilith (Black Moon / Dark Moon)**: Not calculated.
4. **Arabic Parts / Lots (e.g. Lot of Fortune)**: Not supported.
5. **Secondary Progressions & Solar Arc Directions**: Not implemented.

### 7.2 Known Mathematical & Operational Boundaries
1. **Polar Region Error Handling**: At latitudes $> 66.5^\circ$, Placidus house cusp math fails and raises `placidus_polar_error` (HTTP 400).
2. **Unknown Birth Time Precision**: When `birth_time_precision == 'unknown'`, Ascendant and Houses are set to `None`. Calculations default to 12:00 UTC mean noon. Personal resolution gracefully falls back to 4-dimension profiles (Sun, Moon, Element, Modality).
3. **Daily Transits**: Live transit calculation in `transits.py` remains a stub.
