# JESTER — MARS SEMANTIC CONTRACT AUDIT (PHASE 3.8)

**Document Version:** 1.0.0  
**Date:** 2026-09-08  
**Phase:** Phase 3.8 — Mars Semantic Contract Audit & Architecture Locking  
**Status:** Audit & Architecture Design Complete  
**Final Status:** `MARS_CONTRACTS_READY_FOR_PILOT`  

---

## 1. Repository Audit Summary

A comprehensive repository audit was conducted across the backend architecture, Swiss Ephemeris calculations, persistence models, interpretation routing, and content data stores.

### Audit Checklist Findings

| Area / Query | Repository Status | Source of Truth Location |
| :--- | :---: | :--- |
| **A. Is Mars already calculated?** | **YES** | `backend/app/astrology/calculator.py` (`calculate_natal_placements`) via `swe.calc_ut(jd, swe.MARS, ...)` |
| **B. Where is Mars stored?** | **Stored in `astro_private`** | `public.astro_private.mars_longitude` (`double precision`) & `public.astro_private.retrogrades->'mars'` |
| **C. Is Mars retrograde available?** | **YES** | Calculated in `calculator.py` (`speed_lon < 0.0`) and stored in `astro_private.retrogrades` |
| **D. Is Mars exposed to safe profile?** | **NO** | Not in `SafeDerivedAstrology`, `SafeDerivedAstrologyResponse`, or `astro_safe_profile` |
| **E. Does engine.py contain Mars self-sign signals?** | **NO** | `SIGNAL_TYPE_TO_INTERPRETATION_ID` routes Sun, Moon, Rising, Mercury, and Venus, but not Mars |
| **F. Are there existing Mars semantic contracts?** | **Partial (Synastry/Transits only)** | 12 Synastry aspect contracts exist; 0 Self-interpretation Mars contracts exist |
| **G. Are there existing Mars self-content assets?** | **0** | `content_corpus.json`, `mercury_corpus.json`, `venus_corpus.json` contain 0 Mars self assets |
| **H. Minimal backend changes required later?** | **Surgical & Minimal** | Add `mars_sign` to safe models, register 12 contracts in `contracts.py`, add signal routing in `engine.py` (0 database migrations) |

---

## 2. Mars Calculation Audit

1. **Ephemeris Integration:**  
   Swiss Ephemeris integration (`pyswisseph`) calculates Mars longitude with precision in `backend/app/astrology/calculator.py`:
   ```python
   # constants.py
   PLANETS = { ... "mars": swe.MARS ... }
   
   # calculator.py
   res, _ = swe.calc_ut(jd, planet_id, DEFAULT_SWE_FLAGS)
   lon = res[0] % 360.0
   speed_lon = res[3]
   planet_positions["mars_longitude"] = round(lon, 6)
   retrogrades["mars"] = speed_lon < 0.0
   ```
2. **Deterministic Derivation:**  
   `longitude_to_sign(placements.mars_longitude)` is already executed in `natal.py` (line 128) and supplied as a weighted contributor (`weight = 2`) to `derive_primary_element_and_modality()`.
3. **Astrological Fact vs Interpretation Boundary:**  
   - **Astrological Fact:** Mars exact ecliptic longitude (e.g. `24°15' Aries`), zodiac sign (`Aries`), element (`Fire`), modality (`Cardinal`), and motion vector (`Direct/Retrograde`).
   - **Semantic Contract:** Approved boundary defining what Mars-in-sign represents in JESTER's ME layer (how energy is mobilized, effort applied, and resistance met).
   - **JESTER Expression:** User-facing Georgian copy written in 8 distinct voices.

---

## 3. Current Exposure Status & Security Boundary

- **Private Data Invariant:** `public.astro_private.mars_longitude` and exact retrograde velocity are strictly owner/server-controlled and must never be exposed directly to API clients or mobile frontends.
- **Safe Profile Invariant:** Clients receive only safe derived DTOs (`SafeDerivedAstrology`). Currently, `SafeDerivedAstrology` exposes `sun_sign`, `moon_sign`, `ascendant_sign`, `mercury_sign`, and `venus_sign`.
- **Planned Exposure:** In Phase 3.9/3.10, `mars_sign: str | None = None` will be added to `SafeDerivedAstrology` and `SafeDerivedAstrologyResponse` without database migrations, matching the pattern established for Mercury and Venus.

---

## 4. Existing Mars Signal Audit

Existing repository signals referencing Mars are strictly partitioned into Synastry and Transit domains:

1. **Synastry Aspects (`relationship.*`):**
   - `venus_conjunction_mars`, `venus_opposite_mars`, `venus_trine_mars`, `venus_square_mars` $\to$ `relationship.attraction.strong_chemistry.v1`
   - `sun_conjunction_mars`, `sun_trine_mars` $\to$ `relationship.attraction.dynamic_drive.v1`
   - `moon_mars_attraction`, `moon_trine_mars`, `moon_square_mars` $\to$ `relationship.attraction.instinctive_heat.v1`
   - `mars_mars_friction`, `mars_square_mars`, `mars_opposite_mars` $\to$ `relationship.attraction.mars_friction.v1`
   - `mercury_mars_aspect`, `mercury_square_mars` $\to$ `relationship.communication.sharp_debate.v1`
   - `mars_saturn_tension`, `mars_square_saturn` $\to$ `relationship.growth.pacing_tension.v1`
   - `mars_pluto_aspect`, `mars_square_pluto` $\to$ `relationship.growth.power_clash.v1`
2. **Daily Energy Transits (`daily_energy.*`):**
   - `sun_mars_transit` $\to$ `daily_energy.confidence.elevated.v1`
   - `mars_jupiter_transit` $\to$ `daily_energy.vitality.surging_drive.v1`
   - `mars_uranus_transit` $\to$ `daily_energy.restlessness.impulsive_edge.v1`
3. **Self-Interpretation Signals (`self.*`):**
   - **Currently ZERO.** Signals `mars_sign_{sign}` and `mars_{sign}` do not exist in `engine.py`.

---

## 5. Existing Content Audit

A conceptual audit of `backend/app/interpretation/data/content_corpus.json` (7,363 total assets, 825 self-interpretation assets) was performed using search patterns covering action, ambition, drive, initiative, confrontation, competition, persistence, resistance, and pace.

### Audit Findings

- **Assets with `mars` in `interpretation_id`:** **0**
- **Self assets matching action/drive/confrontation keywords:** **74 assets**
  - `self.identity` (Sun): 25 assets (focus on ego pride, leadership, conscious identity)
  - `self.persona` (Rising): 18 assets (focus on outer social entrance, first impression posture)
  - `self.modality` (Cardinal dominance): 12 assets (focus on executive push, generic initiation instinct)
  - `self.element` (Fire dominance): 10 assets (focus on temperamental combustion, enthusiastic heat)
  - `self.emotional` (Moon): 9 assets (focus on emotional boiling points, reactivity under stress)

### Classification of Matching Legacy Content

| Category | Count | Classification | Rationale & Destination |
| :--- | :---: | :---: | :--- |
| `self.identity.sun_*` | 25 | **KEEP** | Properly expresses conscious Sun ego and central purpose. Retain in Sun contracts. |
| `self.persona.rising_*` | 18 | **KEEP** | Properly expresses Ascendant social threshold and entrance demeanor. Retain in Rising contracts. |
| `self.modality.cardinal_*` | 12 | **KEEP** | Expresses abstract structural modality bias. Retain in Modality contracts. |
| `self.element.fire_*` | 10 | **KEEP** | Expresses broad elemental temperament. Retain in Element contracts. |
| `self.emotional.moon_*` | 9 | **KEEP** | Expresses subjective somatic safety and emotional threshold. Retain in Moon contracts. |

**Crucial Takeaway:** Zero legacy assets require migration or reclassification to Mars. However, the existing content clearly demonstrates the risk of semantic leakage (e.g. Rising using "door-kicking", Sun using "acting before thinking", Moon using "boiling over"). Mars must carve out a strictly distinct mechanical territory centered on **how force is directed, effort applied, and resistance navigated**.

---

## 6. Locked Mars Semantic Mission

### Core Definition

$$\mathbf{MARS} = \text{ACTION, ASSERTION, PURSUIT, DRIVE, CONFLICT STYLE}$$

Mars answers the foundational question:  
> **„როგორ მოქმედებ, როგორ მიდიხარ შენსას და რას აკეთებ წინააღმდეგობის დროს?“**  
> *(How do you take action, pursue your objectives, and respond when meeting resistance?)*

### Approved Semantic Territory
- **Initiation Style:** How movement is triggered; what breaks inertia.
- **Pursuit Strategy:** How an objective is chased; direct sprint, patient siege, or tactical maneuver.
- **Assertion:** How personal intent is projected outward into the environment.
- **Response to Resistance:** What happens when blocked; escalates force, outflanks, digs in, negotiates, or dissolves.
- **Effort & Stamina Pattern:** How energy is spent; explosive burst, relentless torque, meticulous craftsmanship, or rhythmic flow.
- **Conflict Style:** How direct challenge or friction is met.
- **Characteristic Friction / Blind Spot:** Where the sign's pursuit mechanism naturally over-rotates or becomes self-defeating.

### What Mars is NOT (De-Escalation Boundaries)
- Mars is **NOT** synonymous with anger, rage, or temper tantrums (that is Moon/emotional reactivity).
- Mars is **NOT** physical violence, criminality, or assault.
- Mars is **NOT** biological testosterone, physical fitness, or sports capability.
- Mars is **NOT** sexual behavior, erotic performance, or dating compatibility.
- Mars is **NOT** masculinity or gender stereotypes.
- Mars is **NOT** guaranteed success, conquest, or career glory.

---

## 7. Hard Ethical & Product Boundaries

Every Mars contract and future asset must obey these hard negative boundaries:

1. **No Fatalistic Certainty:** Forbidden phrases include `"შენ ყოველთვის"`, `"შენ აუცილებლად"`, `"შენ ვერასდროს"`.
2. **No Violence or Criminality:** Zero framing of Mars as dangerous, violent, law-breaking, or abusive.
3. **No Psychiatric or Clinical Labels:** Zero diagnostic terms (`ADHD`, `OCD`, `bipolar`, `intermittent explosive disorder`, `antisocial`, `narcissist`).
4. **No Moralization of Action:**
   - "Direct / fast" is NOT inherently virtuous.
   - "Indirect / slow" is NOT inherently cowardly or defective.
   - "Competitive" is NOT inherently hostile.
   - Describe **mechanisms of exertion**, never moral character.
5. **No Event or Outcome Predictions:** No claims that a user will win battles, get fired, succeed in business, or suffer physical injury.

---

## 8. Cross-Planet Firewall

| Planet | Core Domain | Boundary Question & Test | Violation Risk if Crossed |
| :--- | :--- | :--- | :--- |
| **SUN** | Core Identity / Ego Will | *Does this text describe who the person is at their core?* | Conflating acting style with primary life purpose. |
| **MOON** | Emotional Safety / Defense | *Does this text describe how they feel when threatened?* | Reducing Mars to emotional reactivity, fear, or crying/screaming. |
| **MERCURY** | Cognition / Debate Style | *Does this text describe how they think or communicate?* | Confusing mental reasoning/speech with physical/tactical mobilization. |
| **VENUS** | Relating / Attraction / Taste | *Does this text describe what they like or appreciate?* | Confusing desire/attraction with pursuit/assertion. |
| **MARS** | **Action / Assertion / Pursuit** | ***Does this text describe how effort is deployed to overcome a barrier?*** | **Proper Mars Territory.** |

### Specific Critical Disambiguations
- **Mars vs Mercury:** "How you formulate an argument" is Mercury. "What you physically DO when challenged or blocked" is Mars.
- **Mars vs Venus:** "What attracts you and what atmosphere you enjoy" is Venus. "How you actively pursue what you want" is Mars.
- **Mars vs Moon:** "What you feel somatically when safe or wounded" is Moon. "How you deploy force when confronted with an obstacle" is Mars.
- **Mars vs Sun:** "Your sense of self-worth and leadership identity" is Sun. "Your tactical exertion and mechanics of follow-through" is Mars.

---

## 9. The 12 Approved Mars Semantic Contracts

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                         12 LOCKED MARS CONTRACTS                               │
├────────────────────────────────┬────────────────────────┬──────────────────────┤
│ Contract ID                    │ Core Type              │ Primary Mechanism    │
├────────────────────────────────┼────────────────────────┼──────────────────────┤
│ self.action.mars_aries.v1      │ kinetic_frontal        │ Frontal Sprint       │
│ self.action.mars_taurus.v1     │ relentless_inertia     │ Heavy Torque         │
│ self.action.mars_gemini.v1     │ tactical_maneuver      │ Flanking Agility     │
│ self.action.mars_cancer.v1     │ protective_surge       │ Defensive Clamp      │
│ self.action.mars_leo.v1        │ sovereign_assertion    │ Theatrical Resolve   │
│ self.action.mars_virgo.v1      │ surgical_precision     │ Technical Remedy     │
│ self.action.mars_libra.v1      │ strategic_diplomacy    │ Calibrated Leverage  │
│ self.action.mars_scorpio.v1    │ subterranean_resolve   │ Covert Leverage      │
│ self.action.mars_sagittarius.v1│ expansive_momentum     │ Visionary Gallop     │
│ self.action.mars_capricorn.v1  │ architectural_siege    │ Disciplined Climb    │
│ self.action.mars_aquarius.v1   │ systemic_disruption    │ Contrarian Shock     │
│ self.action.mars_pisces.v1     │ permeable_flow         │ Indirect Dissolution │
└────────────────────────────────┴────────────────────────┴──────────────────────┘
```

### Detailed Contract Specifications

#### 1. `self.action.mars_aries.v1`
- **Sign / Element / Modality:** Aries | Fire | Cardinal
- **Core Mechanism:** Direct kinetic acceleration; instantaneous front-line exertion.
- **Initiation Style:** Spontaneous ignition; begins before full assessment or planning.
- **Pursuit Strategy:** Frontal sprint; high velocity; short-range explosion.
- **Response to Resistance:** Direct impact; accelerates force to breach the obstacle head-on.
- **Effort Pattern:** High-output explosive spike followed by rapid exhaustion if not immediately resolved.
- **Confrontation:** Direct, open, unvarnished clash; immediate confrontation to clear the air.
- **Friction / Blind Spot:** Burning out on the opening charge; impatience with preparation; escalating conflict unnecessarily.
- **Allowed Angles:** `kinetic_frontal_initiative`, `combative_impatience`, `high_velocity_burnout`
- **Forbidden Angles:** Physical violence, tactical calculation, deliberate hesitation, passive retreat.

#### 2. `self.action.mars_taurus.v1`
- **Sign / Element / Modality:** Taurus | Earth | Fixed
- **Core Mechanism:** Heavy physical momentum; high-torque endurance that is slow to start but immovable once underway.
- **Initiation Style:** Deliberate and cautious; requires tangible stakes or material incentive to break inertia.
- **Pursuit Strategy:** Unhurried, methodical, step-by-step progress; grinding stamina.
- **Response to Resistance:** Immovable entrenchment; leans mass against the barrier until the obstacle breaks.
- **Effort Pattern:** Flat, consistent, tireless output; exceptional endurance for repetitive tasks.
- **Confrontation:** Stubborn passive resistance; immovable silence; blunt retaliatory force if pushed beyond threshold.
- **Friction / Blind Spot:** Extreme inertia; refusal to pivot when a strategy fails; stubborn obstinacy.
- **Allowed Angles:** `relentless_grinding_momentum`, `immovable_resistance_torque`, `inertia_friction`
- **Forbidden Angles:** Sudden erratic changes, rapid sprinting, verbal parrying, agility maneuvers.

#### 3. `self.action.mars_gemini.v1`
- **Sign / Element / Modality:** Gemini | Air | Mutable
- **Core Mechanism:** Tactical agility and multi-directional flanking; maneuverability over raw force.
- **Initiation Style:** Sparked by curiosity, intellectual restlessness, novelty, or an intriguing loophole.
- **Pursuit Strategy:** Zig-zagging; simultaneous parallel tracks; rapidly pivoting approach.
- **Response to Resistance:** Circumvents the barrier; finds loopholes; changes the field of engagement.
- **Effort Pattern:** Variable, scattered bursts driven by mental stimulation; low tolerance for tedious physical repetition.
- **Confrontation:** Verbal parrying, reframing terms, tactical deflection, clever evasion.
- **Friction / Blind Spot:** Dispersion of effort across too many tracks; dropping pursuit midway; superficial execution.
- **Allowed Angles:** `tactical_multi_track_maneuver`, `evasive_flanking_strategy`, `energy_dispersion`
- **Forbidden Angles:** Brute physical intimidation, heavy immovable persistence, emotional withdrawal.

#### 4. `self.action.mars_cancer.v1`
- **Sign / Element / Modality:** Cancer | Water | Cardinal
- **Core Mechanism:** Protective, visceral mobilization; defensive surge driven by emotional loyalty.
- **Initiation Style:** Activated by perceived threat to safety, family, sanctuary, or vulnerable allies.
- **Pursuit Strategy:** Diagonal, indirect advance (sideways approach); circles target while securing perimeter.
- **Response to Resistance:** Shell retreat followed by tenacious, unbreakable clamping grip.
- **Effort Pattern:** Fluctuating tidal energy; ferocious and tireless when protecting; cautious when exposed.
- **Confrontation:** Protective armor, indirect grievances, emotional counter-strike, tenacious tenacity.
- **Friction / Blind Spot:** Taking practical obstacles personally; acting through passive resentment; defensive overreaction.
- **Allowed Angles:** `protective_defensive_surge`, `indirect_sideways_advance`, `tenacious_emotional_clamp`
- **Forbidden Angles:** Detached logical debate, reckless frontal gambling, indifferent aggression.

#### 5. `self.action.mars_leo.v1`
- **Sign / Element / Modality:** Leo | Fire | Fixed
- **Core Mechanism:** Theatrical, dignified assertion; pursuit driven by pride, honor, and sovereign conviction.
- **Initiation Style:** Mobilizes when personal stature, creative vision, or leadership honor is challenged.
- **Pursuit Strategy:** Bold, visible, grand execution; demands to be witnessed, recognized, and respected.
- **Response to Resistance:** Inflates dignity and resolve; refuses to appear small, petty, or defeated.
- **Effort Pattern:** Sustained high-voltage output sustained by recognition, loyalty, and self-belief.
- **Confrontation:** Direct, theatrical, magnanimous; stands firm in the spotlight; scorns underhanded tactics.
- **Friction / Blind Spot:** Inability to back down due to pride; doubling down on flawed actions to avoid losing face.
- **Allowed Angles:** `sovereign_theatrical_assertion`, `pride_driven_perseverance`, `status_vulnerability_stalemate`
- **Forbidden Angles:** Covert sabotage, petty bureaucratic squabbling, self-effacing retreat.

#### 6. `self.action.mars_virgo.v1`
- **Sign / Element / Modality:** Virgo | Earth | Mutable
- **Core Mechanism:** Surgical precision and methodical troubleshooting; effort channeled through technique.
- **Initiation Style:** Activated by an inefficiency, an error, a broken system, or a technical problem.
- **Pursuit Strategy:** Systematic, step-by-step optimization; micro-adjusting execution to eliminate friction.
- **Response to Resistance:** Deconstructs the obstacle into component parts; fixes the mechanism until it runs smoothly.
- **Effort Pattern:** Economical, measured, disciplined craftsmanship; zero wasted motion.
- **Confrontation:** Factual critique, procedural auditing, exposing inconsistencies and procedural flaws.
- **Friction / Blind Spot:** Analysis paralysis; exhausting energy on micro-details; losing sight of the overall objective.
- **Allowed Angles:** `surgical_precision_execution`, `systematic_defect_correction`, `micro_perfectionist_friction`
- **Forbidden Angles:** Grandiose theatrical gestures, chaotic aggression, blind physical charges.

#### 7. `self.action.mars_libra.v1`
- **Sign / Element / Modality:** Libra | Air | Cardinal
- **Core Mechanism:** Strategic mediation and diplomatic balancing; tactical leverage through coalition and etiquette.
- **Initiation Style:** Mobilizes when imbalance, unfairness, or discord threatens relational equilibrium.
- **Pursuit Strategy:** Velvet-glove pressure; reciprocal negotiation; strategically building consensus.
- **Response to Resistance:** Negotiates, seeks counter-leverage, mediates, disarms through polite diplomacy.
- **Effort Pattern:** Oscillating, calibration-heavy; expends significant energy testing reactions before acting.
- **Confrontation:** Civilized arbitration; polite framing; avoids uncouth shouting; uses strategic politeness as a shield.
- **Friction / Blind Spot:** Excessive hesitation weighing counter-arguments; passive-aggressive evasion of direct friction.
- **Allowed Angles:** `strategic_diplomatic_leverage`, `calibrated_reciprocal_pressure`, `indecisive_arbitration_hesitation`
- **Forbidden Angles:** Vulgar confrontation, unilateral bull-dozing, solitary brute exertion.

#### 8. `self.action.mars_scorpio.v1`
- **Sign / Element / Modality:** Scorpio | Water | Fixed
- **Core Mechanism:** Subterranean strategic resolve; covert focus and relentless psychological stamina.
- **Initiation Style:** Silent, deliberate, unhurried; waits for the exact leverage point before moving.
- **Pursuit Strategy:** Covert, unshakeable tunnel vision; zero outward broadcast of intent or tactics.
- **Response to Resistance:** Absorbs pressure without cracking; outwaits the barrier; applies lethal precision to weak points.
- **Effort Pattern:** Deep reservoir of volcanic stamina; sustained undercover intensity over long periods.
- **Confrontation:** Cold, controlled, surgical; zero theatrical fluff; devastatingly direct when cornered.
- **Friction / Blind Spot:** Scorched-earth retribution; obsessive fixation on control; inability to disengage from toxic battles.
- **Allowed Angles:** `subterranean_strategic_resolve`, `unrelenting_psychological_stamina`, `scorched_earth_fixation`
- **Forbidden Angles:** Impulsive surface bravado, noisy superficial posturing, naive transparency.

#### 9. `self.action.mars_sagittarius.v1`
- **Sign / Element / Modality:** Sagittarius | Fire | Mutable
- **Core Mechanism:** Expansive visionary momentum; pursuit propelled by ideals, freedom, and broad horizons.
- **Initiation Style:** Sparked by a big idea, a righteous cause, a distant goal, or an open frontier.
- **Pursuit Strategy:** High-spirited gallop; wide strides; loose reins; broad-brush forward movement.
- **Response to Resistance:** Leaps over obstacles; laughs off resistance; changes trajectory toward open terrain.
- **Effort Pattern:** High, buoyant enthusiasm; rapidly suffocated by micromanagement or repetitive drill.
- **Confrontation:** Blunt candid broadsides; righteous philosophical defense; refusing to take petty rules seriously.
- **Friction / Blind Spot:** Overextension; leaving tasks half-finished; clumsy tactical blunders from ignoring fine print.
- **Allowed Angles:** `expansive_visionary_momentum`, `uninhibited_candid_pursuit`, `restless_overextension`
- **Forbidden Angles:** Meticulous micro-management, covert manipulation, passive emotional entrenchment.

#### 10. `self.action.mars_capricorn.v1`
- **Sign / Element / Modality:** Capricorn | Earth | Cardinal
- **Core Mechanism:** Architectural siege discipline; structured, methodical climb to long-term dominance.
- **Initiation Style:** Cold, calculated assessment; begins only with an operational blueprint and clear outcome.
- **Pursuit Strategy:** Relentless uphill progression; building infrastructure and securing foothold before next step.
- **Response to Resistance:** Professional siege warfare; out-plans, out-lasts, and out-disciplines the obstacle.
- **Effort Pattern:** High-efficiency, iron stamina; energy output increases as stakes and altitude rise.
- **Confrontation:** Authoritative, dry, ruthlessly practical; enforces hierarchy and consequences without emotion.
- **Friction / Blind Spot:** Rigid workaholism; emotional austerity; treating human dynamics as joyless military campaigns.
- **Allowed Angles:** `disciplined_architectural_execution`, `authoritative_siege_persistence`, `rigid_pragmatic_exhaustion`
- **Forbidden Angles:** Spontaneous gambling, chaotic emotional outbursts, quitting under fatigue.

#### 11. `self.action.mars_aquarius.v1`
- **Sign / Element / Modality:** Aquarius | Air | Fixed
- **Core Mechanism:** Systemic disruption and ideological autonomy; non-conformist, counter-intuitive action.
- **Initiation Style:** Triggered by arbitrary authority, outdated rules, or an innovative breakthrough opportunity.
- **Pursuit Strategy:** Unconventional, erratic yet stubborn; attacks problems from unexpected systemic angles.
- **Response to Resistance:** Cool detachment; circumvents traditional channels; rewrites the rules of engagement.
- **Effort Pattern:** Electric, intermittent voltage; sudden bursts of hyper-focus mixed with aloof contemplation.
- **Confrontation:** Impassive, objective defiance; intellectual rebellion; refuses to engage on opponent's terms.
- **Friction / Blind Spot:** Contrarianism for its own sake; stubborn dogmatism; alienating allies through cold detachment.
- **Allowed Angles:** `unconventional_systemic_disruption`, `stubborn_ideological_autonomy`, `contrarian_friction`
- **Forbidden Angles:** Blind obedience to tradition, emotional drama, heavy physical drudgery.

#### 12. `self.action.mars_pisces.v1`
- **Sign / Element / Modality:** Pisces | Water | Mutable
- **Core Mechanism:** Permeable intuitive flow; indirect dissolution of barriers through non-linear movement.
- **Initiation Style:** Sparked by inspiration, empathy, imaginative urge, or subtle atmospheric currents.
- **Pursuit Strategy:** Water-like path of least resistance; flowing around obstacles; shifting form.
- **Response to Resistance:** Dissolves, yields outwardly while steadily eroding the obstacle from underneath.
- **Effort Pattern:** Tidal and wave-like; immense stamina when inspired, evaporating into inertia when forced.
- **Confrontation:** Evasive retreat; disarming aggression through non-resistance; subtle, indirect influence.
- **Friction / Blind Spot:** Passive paralysis; escapism when confronted directly; drifting without tangible anchor.
- **Allowed Angles:** `permeable_intuitive_flow`, `indirect_elusive_adaptation`, `passive_paralysis_drift`
- **Forbidden Angles:** Ruthless corporate ambition, heavy rigid control, direct blunt aggression.

---

## 10. Sign Differentiation Matrix

| Sign | What Sparks Action? | How Does it Start? | How Does it Pursue? | What Does it Do When Blocked? | Where Does it Self-Sabotage? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Aries** | Immediate challenge | Instant sprint | Frontal impact | Accelerates force to breach | Opening burnout / impatience |
| **Taurus** | Tangible stakes / comfort | Deliberate lag | Relentless heavy torque | Leans mass until barrier yields | Immovable inertia / stubbornness |
| **Gemini** | Curiosity / novelty | Multi-track spark | Agility & tactical parrying | Circumvents via loopholes | Effort dispersion / dropped tasks |
| **Cancer** | Threat to sanctuary / loved ones | Sideways approach | Protective diagonal advance | Clamps down with tenacious shell | Personalizing / passive grudge |
| **Leo** | Honor / stature / spotlight | Theatrical announcement | Sovereign, bold execution | Inflates dignity & resolve | Pride stalemate / fear of losing face |
| **Virgo** | Technical defect / inefficiency | Diagnostic check | Meticulous troubleshooting | Deconstructs into pieces & fixes | Micro-perfectionist paralysis |
| **Libra** | Imbalance / injustice | Calibrated check | Strategic negotiation & charm | Mediates & seeks coalition | Indecisive arbitration lag |
| **Scorpio** | Hidden truth / high stakes | Silent calculation | Covert, relentless tracking | Absorbs pressure & strikes weak point | Scorched-earth obsession |
| **Sagittarius** | Grand idea / frontier | Wide gallop | Uninhibited visionary stride | Leaps over or jokes past it | Overextension / ignoring details |
| **Capricorn** | Long-term career / structural goal | Cold blueprint | Systematic uphill siege | Out-plans & out-disciplines | Joyless exhaustion / rigidity |
| **Aquarius** | Arbitrary rule / systemic flaw | Contrarian angle | Disruption & rule-breaking | Detaches & rewrites system | Contrarianism for its own sake |
| **Pisces** | Poetic urge / empathy | Intuitive drift | Fluid permeable current | Yields outwardly, erodes underneath | Passive paralysis / escapism |

---

## 11. Cross-Planet Collision Matrix

| Sign | Primary Mars Mechanism | Secondary Possible Collision | Boundary Rule to Enforce |
| :--- | :--- | :--- | :--- |
| **Aries** | Kinetic frontal sprint | Sun in Aries (identity/ego) | Focus on **burst exertion & obstacle impact**, not leadership ego or self-importance. |
| **Taurus** | Heavy grinding torque | Moon in Taurus (somatic calm) | Focus on **unmovable work stamina**, not emotional comfort food or peaceful sleep. |
| **Gemini** | Tactical flanking agility | Mercury in Gemini (verbal logic) | Focus on **tactical action & multitasking execution**, not intellectual curiosity or conversation. |
| **Cancer** | Protective defensive clamp | Moon in Cancer (emotional security) | Focus on **visceral defensive action & fight-back**, not tears, nostalgia, or inner vulnerability. |
| **Leo** | Sovereign theatrical assertion | Sun in Leo (core vitality/pride) | Focus on **bold physical exertion & pride in battle**, not general charisma or need for applause. |
| **Virgo** | Surgical precision execution | Mercury in Virgo (analytical mind) | Focus on **physical craftsmanship & correcting flaws in action**, not mental calculation or speech. |
| **Libra** | Strategic diplomatic leverage | Venus in Libra (aesthetic harmony) | Focus on **calibrated leverage & tactical mediation under pressure**, not fashion, flirting, or sweet romance. |
| **Scorpio** | Subterranean strategic resolve | Moon in Scorpio (emotional depth) | Focus on **relentless stamina & covert execution**, not emotional trauma, paranoia, or intimate bonding. |
| **Sagittarius** | Expansive visionary momentum | Jupiter / Sun in Sag (philosophy) | Focus on **physical gallop & unvarnished blunt action**, not academic theories, lectures, or optimism. |
| **Capricorn** | Architectural siege persistence | Saturn / Sun in Cap (duty/reputation) | Focus on **deliberate physical uphill climb & siege tactics**, not societal status, ancestry, or public career title. |
| **Aquarius** | Unconventional systemic disruption | Uranus / Mercury in Aqua (intellect) | Focus on **tactical defiance & contrarian action**, not abstract social theories or technological gadgets. |
| **Pisces** | Permeable intuitive flow | Moon/Neptune in Pisces (escapism) | Focus on **non-linear fluid action & indirect erosion**, not fantasy dreaming, crying, or spiritual mysticism. |

---

## 12. Forbidden-Claim Matrix

The following table establishes explicit validation rules that automated tests will enforce during Mars content generation:

| Forbidden Category | Forbidden Patterns / Concepts | Allowed Framing |
| :--- | :--- | :--- |
| **Physical Violence / Assault** | `ფიზიკური ძალადობა`, `ცემა`, `ჩხუბი`, `იარაღი`, `კრიმინალი`, `სისხლი` | `კონფლიქტის სტილი`, `დაპირისპირება`, `პირდაპირობა`, `ინიციატივა` |
| **Clinical / Psychiatric Labels** | `ADHD`, `OCD`, `იმპულსური აშლილობა`, `ფსიქოპათი`, `აგრესორი`, `ნარცისი` | `მოუთმენლობა`, `სწრაფი ტემპი`, `დეტალებზე კონცენტრაცია`, `დაჟინებულობა` |
| **Fatalistic Guarantees** | `შენ აუცილებლად გაიმარჯვებ`, `ყოველთვის მარცხდები`, `გარანტირებული წარმატება` | `შენი ბუნებრივი სტრატეგიაა`, `როცა წინააღმდეგობას ხვდები`, `ხშირად ირჩევ` |
| **Gender / Biology Stereotypes** | `მამაკაცური ენერგია`, `ტესტოსტერონი`, `ნამდვილი კაცი`, `სუსტი სქესი` | `ენერგიის მობილიზება`, `მოქმედების მექანიზმი`, `ძალისხმევის განაწილება` |
| **Sexual Behavior Claims** | `სექსუალური ტემპერამენტი`, `საწოლში`, `ლიბიდო`, `ვნება` | `მიზნის დევნა`, `აზარტი`, `ინიციატივის გამოჩენა` |
| **Generic Moral Judgments** | `ცუდი ხასიათი`, `სუსტი ადამიანი`, `ბოროტი განზრახვა`, `იდეალური მებრძოლი` | `სტრატეგიის სუსტი წერტილი`, `ენერგიის გადაწვა`, `ტაქტიკური უპირატესობა` |

---

## 13. JESTER Compatibility Analysis

The 12 Mars contracts provide fertile, multi-dimensional semantic foundations capable of naturally supporting all 8 official JESTER voices:

| Voice | How Voice Expresses Mars Contracts | Tone Example / Vehicle |
| :--- | :--- | :--- |
| **Snarky** | Dryly points out how the user's action strategy backfires or exhausts them. | *Exposing Aries charging into an already unlocked door or Virgo fixing a pencil while the building burns.* |
| **Mocking** | Teases the user's exaggerated habits when blocked or challenged. | *Mocking Taurus trying to out-sit a glacier or Libra holding a peace conference during an ambush.* |
| **Unfiltered** | Delivers raw, blunt truth about their confrontation style and pace. | *Bluntly telling Sagittarius that running away isn't a strategy or Scorpio that their secret plan is obvious.* |
| **Cocky** | Celebrates their formidable stamina, precision, or tactical cleverness. | *Boasting of Capricorn's unbreakable siege persistence or Gemini's uncatchable footwork.* |
| **Dramatic** | Frames their action mechanism as an epic, high-stakes battle. | *Elevating Leo's sovereign stand in the arena or Cancer's fierce fortress counter-attack.* |
| **Conversational** | Speaks peer-to-peer about how they actually handle friction and deadlines. | *Casual, realistic talk about how Taurus gets stuck or how Aquarius acts on principle.* |
| **Unexpected** | Delivers an unconventional analogy or surprising twist on how effort is spent. | *Comparing Pisces' evasive action to mist slipping through bars or Virgo's anger to a red pen correction.* |
| **Jester** | Surfaces the fundamental paradox of their action pattern with playful irony. | *The paradox of fighting so hard to avoid fighting (Libra) or working so hard to break a rule that didn't matter (Aquarius).* |

---

## 14. Minimal Backend Implementation Plan

To support Mars when moving to Phase 3.9 (Pilot) and Phase 3.10 (Full Generation), the following minimal backend changes are pre-planned:

1. **`backend/app/astrology/models.py`:**
   - Add `mars_sign: str | None = None` to `SafeDerivedAstrology`.
   - Add `mars_sign: str | None = None` to `SafeDerivedAstrologyResponse`.
2. **`backend/app/astrology/natal.py`:**
   - In `recalculate_user_astrology`, pass `mars_sign=mars_sign` into the constructed `SafeDerivedAstrology` instance.
3. **`backend/app/astrology/router.py`:**
   - In `recalculate_own_astrology` and `get_my_safe_astrology`, pass `mars_sign=result.mars_sign` into `SafeDerivedAstrologyResponse`.
4. **`backend/app/interpretation/contracts.py`:**
   - Register the 12 `self.action.mars_{sign}.v1` contracts under Section 5D (`SELF / ME — ACTION & ASSERTION`).
5. **`backend/app/interpretation/engine.py`:**
   - In the signal mapping loop over `SIGNS`:
     ```python
     SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mars_sign_{_s}"] = f"self.action.mars_{_s}.v1"
     SIGNAL_TYPE_TO_INTERPRETATION_ID[f"mars_{_s}"] = f"self.action.mars_{_s}.v1"
     ```
6. **Zero Database Migrations:**
   - No migration needed. Follows the exact non-breaking pattern established in Mercury and Venus.
7. **Zero Private Exposure:**
   - Private planetary degrees, house positions, and raw retrograde speeds remain strictly isolated in `astro_private`.

---

## 15. Testing & Verification Strategy

Future test suite (`tests/interpretation/test_mars_content.py`) will mirror the rigorous verification standards of Mercury and Venus:
1. **Contract Registration & Routing:** Assert all 12 `self.action.mars_{sign}.v1` contracts are registered in `INTERPRETATION_CONTRACTS` and mapped in `SIGNAL_TYPE_TO_INTERPRETATION_ID`.
2. **Safe Exposure:** Assert `mars_sign` is present on `SafeDerivedAstrology` and `SafeDerivedAstrologyResponse` without leaking degrees, houses, or retrograde flags.
3. **Forbidden Claims & Jargon Scan:** Assert 0 occurrences of astrological jargon (`მარსი`, `მზე`, etc.), 0 clinical diagnoses, 0 violence terms, and 0 fatalistic certainty claims.
4. **Length Boundaries:** Micro assets strictly $100 \le \text{length} \le 250$ chars; Medium assets strictly $400 \le \text{length} \le 750$ chars.
5. **Full Quality Gate:** Automated scoring across all 5 dimensions $\ge 4.0$ for every single asset.
6. **Zero Regressions:** Full repository test suite must remain 100% green (170+ tests).

---

## 16. Risks & Unresolved Questions

1. **Risk of Conflating Mars with Anger / Temper:**
   - *Mitigation:* Explicitly locked in contracts: Mars represents **action, exertion, pursuit, and resistance response**, NOT emotional tantrums (which belong to Moon).
2. **Risk of Redundant Overlap with Sun in Fire Signs:**
   - *Mitigation:* Enforced firewall: Sun in Aries/Leo/Sagittarius represents conscious identity, life purpose, and ego expression. Mars represents tactical execution, sprint vs stamina mechanics, and how friction is breached.
3. **Risk of Overlap between Mars in Gemini/Virgo and Mercury:**
   - *Mitigation:* Enforced firewall: Mercury is information processing, cognitive framing, and debate articulation. Mars in Gemini/Virgo is physical/tactical agility, multi-tracking tasks, and diagnostic mechanical troubleshooting.
4. **Product Decision on Mars Exposure Timing:**
   - *Clarification:* Mars backend exposure will be applied surgically in Phase 3.9 when the pilot assets are ready to be ingested.

---

## 17. Readiness Assessment

| Criterion | Evaluation | Status |
| :--- | :--- | :---: |
| **Astrological Grounding** | Swiss Ephemeris calculation verified; Element & Modality integration mapped. | **VERIFIED** |
| **Semantic Mission Clarity** | Strictly defined as Action, Assertion, Pursuit, Drive, and Conflict Style. | **LOCKED** |
| **Cross-Planet Firewall** | Clear boundaries separating Mars from Sun, Moon, Mercury, and Venus. | **LOCKED** |
| **Sign Differentiation** | 12 distinct action mechanisms established; zero superficial adjective swapping. | **VERIFIED** |
| **Safety & Boundary Rules** | Forbidden claims, violence prohibition, and non-moralizing language defined. | **LOCKED** |
| **JESTER Voice Compatibility** | All 8 voices naturally supported with specific framing vehicles. | **VERIFIED** |
| **Repository Discipline** | Zero database migrations; zero raw data leakage; surgical plan defined. | **VERIFIED** |

---

## Final Status

# MARS_CONTRACTS_READY_FOR_PILOT

The 12 Mars semantic contracts are fully defined, bounded, differentiated, and ready to guide the upcoming 36-asset pilot generation.
