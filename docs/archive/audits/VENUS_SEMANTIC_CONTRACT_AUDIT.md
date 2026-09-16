# VENUS SEMANTIC CONTRACT AUDIT (PHASE 3.5)
**Status:** VENUS_CONTRACTS_READY_FOR_PILOT  
**Date:** 2026-09-08  
**Scope:** Architectural Audit, Semantic Mission Locking, 12 Contract Specifications, Collision Prevention Matrix, and Backend Exposure Roadmap for Venus (ME Content System).  
**Document Path:** `docs/VENUS_SEMANTIC_CONTRACT_AUDIT.md`  

---

## Executive Summary

Phase 3.5 establishes the deterministic semantic ground truth for Venus in JESTER's ME Content System (`self.relation.venus_{sign}.v1`). Following the approval and delivery of Mercury Phase 3.4 (12 contracts, 96 assets, 153/153 tests passing), this audit defines the boundaries, semantic contracts, and technical wiring for Venus **prior to any copy generation**.

### The JESTER Three-Layer Decoupling Principle

```
Layer 1: ASTROLOGICAL FACT (Deterministic Calculation)
         Swiss Ephemeris (swe.VENUS longitude → zodiac sign → element + modality)
                            ↓
Layer 2: SEMANTIC INTERPRETATION (Product Ground Truth)
         Approved Semantic Contract (self.relation.venus_{sign}.v1)
         Defines WHAT the astronomical input is authorized to mean.
                            ↓
Layer 3: JESTER EXPRESSION (Stylistic Output)
         Georgian copy written in JESTER's 8 official voices across Micro & Medium depths.
         Defines HOW that meaning is humorously and sharply articulated.
```

**Cardinal Rule:** The AI generator is never permitted to invent semantic meaning or astrological interpretations during copy production.

---

## 1. Repository Audit (Phase 1 Findings)

| Question | Status | Architectural Location | Detailed Finding |
| :--- | :---: | :--- | :--- |
| **A. Is Venus already calculated?** | **YES** | `backend/app/astrology/calculator.py:124` | `swe.calc_ut(jd, swe.VENUS, flags)` calculates exact ecliptic longitude and speed. In `natal.py:127`, `venus_sign = longitude_to_sign(placements.venus_longitude)` converts longitude to zodiac sign. Also factored into `derive_primary_element_and_modality` with weight 2. |
| **B. Where is Venus stored?** | **PARTIAL** | `public.astro_private` | Exact degree is persisted in `astro_private.venus_longitude` (`DOUBLE PRECISION`). In RAM during calculation in `natal.py:127`. **NOT** currently stored in `public.astro_safe_profile` table. |
| **C. Is Venus retrograde available?** | **YES** | `astro_private.retrogrades['venus']` | `calculator.py:86` calculates `speed < 0` for all configured bodies. Flag is persisted in `retrogrades` JSONB column. |
| **D. Is Venus currently exposed to safe profile?** | **NO** | `backend/app/astrology/models.py` | Neither `SafeDerivedAstrology` nor `SafeDerivedAstrologyResponse` contains `venus_sign`. Not returned by `/astrology/profile/safe-astro` or `/astrology/people/{id}/safe-astro`. |
| **E. Is Venus represented in interpretation signals?** | **PARTIAL** | `backend/app/interpretation/engine.py` | 30+ Synastry aspect signals exist for Venus (e.g. `venus_conjunction_mars`, `sun_conjunction_venus`) mapping to `relationship.*`. Daily energy transits exist (`sun_venus_transit`, `venus_neptune_transit`). **Zero** `self.*` natal sign signals exist. |
| **F. Are there existing Venus semantic contracts?** | **NO** | `backend/app/interpretation/contracts.py` | Exactly 0 `self.relation.venus_*` contracts exist. Current self registry has 55 contracts (43 base + 12 Mercury). |
| **G. Are there existing Venus content assets?** | **NO** | `backend/app/interpretation/data/` | Exactly 0 Venus self-content assets exist in `content_corpus.json`, `mercury_corpus.json`, or `seed_data.py`. (Only 3 synastry aspect assets exist in `seed_data.py`). |
| **H. What minimal backend changes are required?** | **MINIMAL** | `models.py`, `natal.py`, `router.py`, `contracts.py`, `engine.py` | Add `venus_sign` to DTOs; register 12 contracts; wire signal mapping. **Zero database migrations or table modifications needed.** |

---

## 2. Venus Semantic Mission (Phase 2)

### Locked Conceptual Scope
**VENUS = Interpersonal Relating Instinct, Relational Aesthetic & Social Valuation**  
*(ურთიერთობისა და მიზიდულობის სტილი, ესთეტიკური და სოციალური ფასეულობები)*

Venus governs the relational bridge between the self and others. It captures how an individual naturally relates, what interpersonal tone feels instinctively attractive, how they express liking and social warmth, what relational pacing feels comfortable, and their aesthetic/value currency in connection.

### Authorized Semantic Scope
- **Attraction Currency:** What qualities, dynamics, or interpersonal atmospheres feel instinctively magnetic.
- **Affection & Warmth Expression:** How the individual signals liking, appreciation, and social interest.
- **Relational Rhythm:** Preferred tempo of intimacy (immediate, gradual, playful, structured, intense, spacious).
- **Social Value System:** What is valued in human interaction (intellectual wit, tangible stability, loyalty, elegance, shared freedom, emotional depth).
- **Relational Blind Spot / Friction Point:** Characteristic self-sabotage, over-correction, or tension in relating.

### Strict Negative Boundaries (Forbidden Claims)
Venus copy and contracts must **NEVER** claim:
- Guaranteed romantic behavior or relationship success/failure.
- Guaranteed partner compatibility, soulmate declarations, or marriage predictions.
- Clinical psychological conditions, trauma bonds, or attachment-style diagnoses (e.g. "anxious-avoidant attachment").
- Sexual behavior presented as biological or moral fact.
- Moral character evaluations ("you are disloyal", "you are narcissistic").
- Absolute fatalistic certainty ("you always fall for...", "you will never be happy with...").

---

## 3. The 12 Locked Venus Semantic Contracts (Phase 3)

The following 12 contract IDs are formally specified and locked:

```text
self.relation.venus_aries.v1
self.relation.venus_taurus.v1
self.relation.venus_gemini.v1
self.relation.venus_cancer.v1
self.relation.venus_leo.v1
self.relation.venus_virgo.v1
self.relation.venus_libra.v1
self.relation.venus_scorpio.v1
self.relation.venus_sagittarius.v1
self.relation.venus_capricorn.v1
self.relation.venus_aquarius.v1
self.relation.venus_pisces.v1
```

---

### Contract 1: `self.relation.venus_aries.v1`
- **Element:** Fire | **Modality:** Cardinal
- **Core Relational Signal:** `kinetic_attraction` (სწრაფი, პირდაპირი ინიციატივა)
- **Attraction Pattern:** Drawn to boldness, directness, playful competitive tension, and unapologetic self-assurance. Bored by hesitance, polite stalling, or passive ambiguity.
- **Expression Style:** Immediate, unfiltered warmth; teasing banter; overt invitations; taking the romantic initiative.
- **What Feels Rewarding:** High-energy momentum, spontaneous adventures, dynamic spark where mutual interest is clear.
- **Characteristic Friction / Blind Spot:** Impatience with slower courtship; interpreting a partner's caution as rejection; burning through initial novelty quickly.
- **Allowed Semantic Angles:**
  1. `rapid_relational_initiative` (მყისიერი ინიციატივა)
  2. `competitive_playful_spark` (აზარტული, თამამი ფლირტი)
  3. `impatience_with_relational_games` (დიპლომატიური თამაშების აუტანლობა)
- **Forbidden Angles:** Physical aggression, guaranteed short-lived relationships, lack of emotional capacity.

---

### Contract 2: `self.relation.venus_taurus.v1`
- **Element:** Earth | **Modality:** Fixed
- **Core Relational Signal:** `sensory_anchor` (მყარი, სენსორული ერთგულება)
- **Attraction Pattern:** Drawn to physical presence, grounded reliability, aesthetic simplicity, good taste, and unhurried calm. Repelled by chaotic drama and erratic emotional swings.
- **Expression Style:** Tangible affection, physical comfort, thoughtful comfort gifts, steady loyalty, sharing food and peaceful spaces.
- **What Feels Rewarding:** Unhurried domestic ease, predictable continuity, sensory indulgence, knowing where they stand.
- **Characteristic Friction / Blind Spot:** Relational stubbornness; measuring affection through material/sensory comfort; resisting necessary emotional evolution.
- **Allowed Semantic Angles:**
  1. `tangible_sensory_loyalty` (მატერიალური და სენსორული ზრუნვა)
  2. `unhurried_relational_pacing` (აუჩქარებელი, მდგრადი ტემპი)
  3. `stubborn_comfort_zones` (ჩვევებსა და კომფორტზე ჩაბღაუჭება)
- **Forbidden Angles:** Material greed, emotional shallowness, immobility as moral flaw.

---

### Contract 3: `self.relation.venus_gemini.v1`
- **Element:** Air | **Modality:** Mutable
- **Core Relational Signal:** `intellectual_curiosity` (ვერბალური თამაში და მენტალური მიზიდულობა)
- **Attraction Pattern:** Drawn to verbal wit, intellectual agility, conversational lightness, humor, and multifaceted curiosity. Suffocated by heavy, silent, or possessive intensity.
- **Expression Style:** Witty banter, sharing articles/ideas, playful teasing, constant communicative ping-pong, lighthearted social camaraderie.
- **What Feels Rewarding:** Engaging dialogue, mutual laughter, variety of shared experiences, feeling mentally stimulated and entertained.
- **Characteristic Friction / Blind Spot:** Intellectualizing emotions; retreating into verbal jokes when emotional depth is required; restlessness.
- **Allowed Semantic Angles:**
  1. `conversational_chemistry` (ვერბალური ნაპერწკალი და იუმორი)
  2. `need_for_mental_spaciousness` (გონებრივი სივრცის მოთხოვნილება)
  3. `fickle_novelty_craving` (მრავალფეროვნების ძიება მოწყენილობის წინააღმდეგ)
- **Forbidden Angles:** Incapacity to love, superficiality, accusations of deceit or manipulation.

---

### Contract 4: `self.relation.venus_cancer.v1`
- **Element:** Water | **Modality:** Cardinal
- **Core Relational Signal:** `protective_sanctuary` (ემოციური უსაფრთხოება და ზრუნვა)
- **Attraction Pattern:** Drawn to tenderness, emotional sincerity, intuitive consideration, loyalty, and a sense of shared belonging. Threatened by coldness, cynicism, or emotional flippancy.
- **Expression Style:** Attentive nurturing, remembering sentimental details, cooking/creating cozy sanctuaries, protective emotional shielding.
- **What Feels Rewarding:** Feeling deeply seen and emotionally safe, reciprocal devotion, quiet intimate one-on-one time.
- **Characteristic Friction / Blind Spot:** Passive-aggressive withdrawal when hurt; testing loyalty through silent retreats; expecting mind-reading.
- **Allowed Semantic Angles:**
  1. `protective_nurturing_instinct` (მზრუნველი და დამცავი სითბო)
  2. `emotional_security_checkpoint` (ნდობის ფრთხილი, ეტაპობრივი მინიჭება)
  3. `defensive_relational_retreat` (განაწყენებისას ჯავშანში ჩაკეტვა)
- **Forbidden Angles:** Co-dependency diagnosis, emotional manipulation, guaranteed clinging.

---

### Contract 5: `self.relation.venus_leo.v1`
- **Element:** Fire | **Modality:** Fixed
- **Core Relational Signal:** `celebratory_magnificence` (დიდსულოვანი, თეატრალური ერთგულება)
- **Attraction Pattern:** Drawn to radiance, charismatic confidence, generosity of spirit, aesthetic elegance, and people who stand out. Repelled by pettiness, stinginess, and lukewarm interest.
- **Expression Style:** Flamboyant generosity, public pride in the partner, warm romantic gestures, championing the partner's talents.
- **What Feels Rewarding:** Mutual admiration, being celebrated and cherished, sharing a vibrant and honorable partnership.
- **Characteristic Friction / Blind Spot:** Vulnerability to bruised pride; interpreting casual distraction as personal disrespect; needing constant theatrical reassurance.
- **Allowed Semantic Angles:**
  1. `generous_royal_courtship` (დიდსულოვანი, ფერადი რომანტიკა)
  2. `pride_and_public_devotion` (სიამაყე და პარტნიორის წარმოჩენა)
  3. `validation_vulnerability` (ყურადღების ნაკლებობაზე მტკივნეული რეაქცია)
- **Forbidden Angles:** Narcissism, ego vanity as character flaw, superficial arrogance.

---

### Contract 6: `self.relation.venus_virgo.v1`
- **Element:** Earth | **Modality:** Mutable
- **Core Relational Signal:** `devoted_craftsmanship` (პრაქტიკული ზრუნვა და ყურადღება დეტალებზე)
- **Attraction Pattern:** Drawn to competence, thoughtful consideration, quiet intelligence, cleanliness, and grounded humility. Repelled by sloppy posturing, chaos, and empty grandiose promises.
- **Expression Style:** Acts of service, solving logistical hassles, noticing personal nuances, quietly improving the partner's daily life.
- **What Feels Rewarding:** Functional harmony, mutual respect, practical reliability, understated genuine appreciation without dramatic excess.
- **Characteristic Friction / Blind Spot:** Relational over-editing; expressing love through constructive critique; difficulty relaxing into imperfect romance.
- **Allowed Semantic Angles:**
  1. `acts_of_service_currency` (სიყვარული საქმით და პრაქტიკული ზრუნვით)
  2. `attentive_micro_observation` (უმცირესი დეტალებისა და საჭიროებების შემჩნევა)
  3. `relational_quality_control` (ზედმეტი კრიტიკულობა და ხარვეზების გასწორების სურვილი)
- **Forbidden Angles:** Nagging stereotype, coldness, incapacity for passion.

---

### Contract 7: `self.relation.venus_libra.v1`
- **Element:** Air | **Modality:** Cardinal
- **Core Relational Signal:** `harmonious_equilibrium` (ესთეტიკური ჰარმონია და ეგალიტარული პარტნიორობა)
- **Attraction Pattern:** Drawn to grace, aesthetic refinement, diplomatic tact, charming reciprocity, and mutual consideration. Repelled by vulgarity, blunt aggression, and relational one-sidedness.
- **Expression Style:** Thoughtful compliments, setting a romantic atmosphere, smoothing over interpersonal friction, balancing mutual desires.
- **What Feels Rewarding:** Shared beauty, elegant collaboration, peaceful social interaction, feeling like an equal and admired partner.
- **Characteristic Friction / Blind Spot:** Chronic conflict avoidance; prioritizing pleasant surfaces over uncomfortable truths; indecision under relationship strain.
- **Allowed Semantic Angles:**
  1. `aesthetic_diplomacy` (ესთეტიკური დახვეწილობა და თავაზიანობა)
  2. `reciprocal_partnership_ideal` (სრული თანასწორობისა და ბალანსის ძიება)
  3. `conflict_avoidant_courtesy` (კონფლიქტისთვის თავის არიდება ზედაპირული სიმშვიდით)
- **Forbidden Angles:** Phony insincerity, weakness, incapacity to take a stand.

---

### Contract 8: `self.relation.venus_scorpio.v1`
- **Element:** Water | **Modality:** Fixed
- **Core Relational Signal:** `transformative_depth` (შეუვალი ერთგულება და ღრმა ემოციური ინტენსივობა)
- **Attraction Pattern:** Drawn to psychological truth, mystery, intense authenticity, resilience, and magnetic focus. Repelled by superficial flirtation, casual disloyalty, and lukewarm commitment.
- **Expression Style:** Laser-focused devotion, protective emotional shielding, absolute loyalty, sharing vulnerabilities only in strict confidence.
- **What Feels Rewarding:** All-or-nothing emotional intimacy, unbreakable trust, feeling deeply bound at a soulful level.
- **Characteristic Friction / Blind Spot:** Hyper-vigilance regarding betrayal; testing the partner's loyalty; holding onto subtle emotional wounds.
- **Allowed Semantic Angles:**
  1. `uncompromising_emotional_depth` (ზედაპირულობის ზიზღი და მაქსიმალური ინტენსივობა)
  2. `fierce_protective_loyalty` (ურყევი, ფოლადისებრი ერთგულება)
  3. `relational_trust_audit` (პარტნიორის შემოწმება ფარულ მოტივებზე)
- **Forbidden Angles:** Paranoia diagnosis, toxic possession, dangerous/abusive behavior claims.

---

### Contract 9: `self.relation.venus_sagittarius.v1`
- **Element:** Fire | **Modality:** Mutable
- **Core Relational Signal:** `expansive_camaraderie` (ფილოსოფიური თავისუფლება და საერთო თავგადასავალი)
- **Attraction Pattern:** Drawn to intellectual exploration, infectious humor, cultural curiosity, unvarnished honesty, and wide horizons. Repelled by possessive jealousy, domestic rigidity, and narrow predictability.
- **Expression Style:** Inviting the partner into new experiences, expansive optimism, generous shared laughter, uplifting companionship.
- **What Feels Rewarding:** Freedom within connection, philosophical debates, spontaneous travel or discovery, laughing together.
- **Characteristic Friction / Blind Spot:** Commitment claustrophobia; blunt candor delivered without emotional tact; fleeing when daily domestic routine sets in.
- **Allowed Semantic Angles:**
  1. `relational_adventurism` (სიყვარული როგორც საერთო მოგზაურობა და ჰორიზონტის გაფართოება)
  2. `unvarnished_romantic_candor` (პირდაპირი, ხანდახან უტაქტო გულწრფელობა)
  3. `allergic_reaction_to_clinginess` (შეზღუდვებისა და ეჭვიანობის აუტანლობა)
- **Forbidden Angles:** Incapacity for commitment, infidelity, emotional heartlessness.

---

### Contract 10: `self.relation.venus_capricorn.v1`
- **Element:** Earth | **Modality:** Cardinal
- **Core Relational Signal:** `structural_devotion` (გრძელვადიანი საიმედოობა და პატივისცემა)
- **Attraction Pattern:** Drawn to maturity, quiet competence, integrity, mutual respect, ambition, and emotional resilience. Repelled by flakey inconsistency, loud emotional drama, and superficial hype.
- **Expression Style:** Concrete reliability, investing time and resources into the partnership's future, dignified support, protecting the other's reputation.
- **What Feels Rewarding:** Building enduring foundations, knowing the partner is a dependable ally, mutual respect through actions rather than words.
- **Characteristic Friction / Blind Spot:** Emotional austerity; treating relationships like long-term strategic contracts; withholding affection until "earned".
- **Allowed Semantic Angles:**
  1. `architectural_loyalty` (გრძელვადიანი, მყარი კავშირის მშენებლობა)
  2. `sober_affectional_reserve` (ემოციური თავშეკავება და საქმით გამოხატული სითბო)
  3. `transactional_caution` (ურთიერთობის შეფასება რესურსებითა და საიმედოობით)
- **Forbidden Angles:** Gold-digging, cold heart, loveless utilitarianism.

---

### Contract 11: `self.relation.venus_aquarius.v1`
- **Element:** Air | **Modality:** Fixed
- **Core Relational Signal:** `unconventional_solidarity` (მეგობრობაზე დაფუძნებული, თავისუფალი კავშირი)
- **Attraction Pattern:** Drawn to individuality, intellectual eccentricity, progressive ideals, authentic weirdness, and egalitarian respect. Repelled by traditional codependency, suffocating expectations, and emotional possessiveness.
- **Expression Style:** Total acceptance of the other's quirks, intellectual camaraderie, giving generous breathing room, defending the partner's autonomy.
- **What Feels Rewarding:** Friendship first, stimulating conceptual discussions, feeling chosen without feeling constrained.
- **Characteristic Friction / Blind Spot:** Emotional detachment; intellectualizing raw intimate feelings; aloofness when confronted with high-intensity emotional demands.
- **Allowed Semantic Angles:**
  1. `friendship_first_attraction` (ინტელექტუალური მეგობრობა როგორც მიზიდულობის საფუძველი)
  2. `fierce_respect_for_autonomy` (პარტნიორის დამოუკიდებლობისა და უნიკალურობის დაცვა)
  3. `aloof_emotional_distance` (ზედმეტ დრამაზე გონებრივი დისტანცირებით პასუხი)
- **Forbidden Angles:** Inability to feel love, robot/alien dehumanization, chronic detachment as pathology.

---

### Contract 12: `self.relation.venus_pisces.v1`
- **Element:** Water | **Modality:** Mutable
- **Core Relational Signal:** `permeable_resonance` (პოეტური თანაგრძნობა და ინტუიციური მიმღებლობა)
- **Attraction Pattern:** Drawn to soulfulness, gentle vulnerability, artistic depth, emotional softness, and unspoken resonance. Repelled by callous cynicism, rigid transactional attitudes, and harsh criticism.
- **Expression Style:** Gentle emotional attunement, creative/poetic expression, forgiving devotion, non-judgmental listening.
- **What Feels Rewarding:** Transcendent emotional connection, dissolving boundaries in quiet harmony, feeling emotionally and spiritually understood.
- **Characteristic Friction / Blind Spot:** Boundary erosion; romanticizing red flags or projecting idealized fantasies; emotional escapism when practical conflict arises.
- **Allowed Semantic Angles:**
  1. `soulful_empathic_attunement` (პარტნიორის განცდების უსიტყვოდ შეგრძნება)
  2. `romantic_idealism` (პოეტური და იდეალისტური შეხედულება სიყვარულზე)
  3. `diffuse_boundary_vulnerability` (საზღვრების წაშლა და რეალობისგან გაქცევა)
- **Forbidden Angles:** Victim complex, psychic claims, chronic martyr syndrome.

---

## 4. Astrological Semantic Discipline (Phase 4 & 5)

To prevent signs from collapsing into generic formulas, Venus uses element and modality as structural dimensions while preserving sign-specific uniqueness:

| Element | Relational Energy | Cardinal (Initiates) | Fixed (Sustains) | Mutable (Adapts) |
| :--- | :--- | :--- | :--- | :--- |
| **Fire** | Direct, Expressive, Enthusiastic | **Aries:** Launches romantic momentum directly; sparks immediate excitement. | **Leo:** Radiates generous, theatrical pride; celebrates the bond grandly. | **Sagittarius:** Expands horizons; relates through humor and philosophical adventure. |
| **Earth** | Tangible, Steady, Sensory | **Capricorn:** Builds structural stability; invests in enduring alliances. | **Taurus:** Grounds connection in sensory comfort, loyalty, and peace. | **Virgo:** Refines everyday harmony; expresses love through devoted service. |
| **Air** | Mental, Conversational, Curious | **Libra:** Curates social grace and egalitarian balance between two people. | **Aquarius:** Defends intellectual autonomy and unconditional individuality. | **Gemini:** Weaves conversational ping-pong and agile curiosity. |
| **Water** | Intimate, Receptive, Atmosphere-Sensitive | **Cancer:** Establishes a protective sanctuary and emotional belonging. | **Scorpio:** Plunges into transformative depth and fierce exclusivity. | **Pisces:** Dissolves rigid boundaries in empathic, poetic resonance. |

---

## 5. Repetition & Semantic Collision Audit (Phase 8)

Venus must never collide with Sun, Moon, Mercury, or Mars. The following boundary matrix is frozen:

```
┌──────────────┬──────────────────────────────────────────────┬──────────────────────────────────────────────┐
│ Planet       │ Core Semantic Domain                         │ Boundary vs Venus                            │
├──────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ SUN          │ Identity, Central Ego, Vitality              │ Sun = Who I am; Venus = What I appreciate.   │
│ MOON         │ Inner Emotional Security, Vulnerability      │ Moon = How I cope; Venus = How I relate.     │
│ MERCURY      │ Cognition, Argumentation, Information        │ Mercury = How I think; Venus = How I charm.  │
│ VENUS        │ Relating Instinct, Attraction, Social Values │ Venus = How I connect, admire, and value.    │
│ MARS         │ Assertion, Drive, Friction, Pursuit          │ Mars = How I fight; Venus = What attracts me.│
└──────────────┴──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

### Specific Collision Hotspots & Resolution Rules

1. **Venus in Cancer vs Moon in Cancer:**
   - *Moon in Cancer:* How the individual retreats when emotionally wounded, needs physical home security, and processes private somatic moods.
   - *Venus in Cancer:* How the individual builds a hospitable relational bridge, expresses warmth through caretaking, and tests interpersonal safety before opening.
2. **Venus in Gemini vs Mercury in Gemini:**
   - *Mercury in Gemini:* Mental speed, information ingestion, multi-tasking, structured debate agility.
   - *Venus in Gemini:* Conversational flirtation, witty social rapport, seeking variety in partners, finding quick humor attractive.
3. **Venus in Aries vs Mars in Aries:**
   - *Mars in Aries:* Aggressive drive, physical confrontation, pushing through obstacles, anger response.
   - *Venus in Aries:* Relational spark, direct romantic approach, falling for courage and audacity, impatience with polite dating stalling.
4. **Venus in Libra vs Sun in Libra:**
   - *Sun in Libra:* Core identity defined by fairness, indecisiveness as life philosophy, seeking universal balance.
   - *Venus in Libra:* Relational aesthetics, courtship elegance, social courtesy, specific attraction to graceful partners.

---

## 6. JESTER Tone Compatibility (Phase 6)

The 12 semantic contracts are written analytically to support all 8 official JESTER voices during future corpus generation:

| Official JESTER Tone | Tone Focus in Venus Copy | Example Framing Style |
| :--- | :--- | :--- |
| **Snarky (წაკბენს)** | Pokes at romantic blind spots and courtship hypocrisies. | "შენთვის სიყვარული მშვიდი ნავსაყუდელია მანამ, სანამ ვინმე დივანზე შენს ადგილს არ დაიკავებს." |
| **Mocking (დაგცინის)** | Teases courtship dramatics and relationship rituals. | "სანამ სხვები თვალებით ეფლირტავებიან, შენ უკვე პარტნიორის ბიუჯეტის აუდიტს ატარებ." |
| **Unfiltered (თავს არ იკავებს)** | Cuts through romantic delusions with raw honesty. | "თუ ნაპერწკალი პირველ სამ წამში არ გაჩნდა, მეორე შანსს კი არა, გამარჯობასაც აღარ ეტყვი." |
| **Cocky (ზედმეტად თავდაჯერებულია)** | Exaggerates relational standards and aesthetic discernment. | "შენს გემოვნებასთან შედარებით სხვების არჩევანი უბრალოდ კომპრომისია." |
| **Dramatic (ყველაფერს აძლიერებს)** | Elevates romantic dynamics to Shakespearean stakes. | "შენთან ურთიერთობა ან საუკუნის რომანია, ან ტრაგიკული დუმილი — შუალედი ბუნებამ არ მოგცა." |
| **Conversational (ადამიანივით გელაპარაკება)** | Warm, grounded, perceptive observation of how they connect. | "შენთვის მთავარია ადამიანი უსიტყვოდ გრძნობდეს, როდის გჭირდება მარტო ყოფნა." |
| **Unexpected (მოულოდნელი)** | Flips a romantic cliché into an absurd, sharp observation. | "ყველა ელის, რომ გულს გადაუშლი, შენ კი უცებ საერთო ინვესტიციების გეგმას უხსნი." |
| **Jester (სარკასტული)** | Self-deprecating, razor-sharp irony about relationship patterns. | "იდეალური პარტნიორი გინდა, ოღონდ ისეთი, რომელიც ზუსტად შენს წესებს დაიცავს და თან თავისუფალი იქნება." |

---

## 7. Forbidden-Claim Matrix (Phase 7 & 8)

Automated QA regex and lint filters for Venus batch generation:

```python
FORBIDDEN_VENUS_CLAIMS = [
    # Clinical diagnoses
    r"\badhd\b", r"\bაუტიზმ", r"\bდეპრესი", r"\bბიპოლარულ",
    r"\bმიჯაჭვულობის სინდრომ", r"\bმიჯაჭვულობის ტიპ", r"\bშფოთვითი მიჯაჭვულობ",
    r"\bგარიყვის შიში", r"\bოკდ\b", r"\bტრავმული კავშირ",
    
    # Absolute fatalistic / fortune-telling claims
    r"\bშენ აუცილებლად დაქორწინდები\b", r"\bშენი მეორე ნახევარი\b",
    r"\bეს ქორწინება\b", r"\bგარანტირებული სიყვარულ", r"\bსაბედისწერო სიყვარულ",
    r"\bეს დამტკიცებულია\b", r"\bშენ ყოველთვის ირჩევ\b",
    
    # Moral / Character judgments
    r"\bმოღალატე ხარ\b", r"\bარ შეგიძლია სიყვარული\b", r"\bცივი ხარ\b",
    r"\bნარცისი ხარ\b", r"\bტოქსიკური ხარ\b",
    
    # User-facing technical astrology jargon
    r"\bვენერა\b", r"\bრეტროგრად\b", r"\bტრინი\b", r"\bსექსტილ\b",
    r"\bკვადრატ\b", r"\bოპოზიცი\b", r"\bსახლი\b", r"\bეფემერიდ\b"
]
```

---

## 8. Backend Exposure & Implementation Roadmap (Phase 9)

### Planned Backend Touchpoints (Phase 3.6 / Generation Prep)

1. **`backend/app/astrology/models.py`**:
   ```python
   # Add to SafeDerivedAstrology and SafeDerivedAstrologyResponse:
   venus_sign: str | None = None
   ```
2. **`backend/app/astrology/natal.py`**:
   ```python
   # Already calculated on line 127:
   venus_sign = longitude_to_sign(placements.venus_longitude)
   # Pass into constructor:
   SafeDerivedAstrology(..., venus_sign=venus_sign)
   ```
3. **`backend/app/astrology/router.py`**:
   ```python
   # Pass venus_sign in recalculate and safe profile responses
   ```
4. **`backend/app/interpretation/contracts.py`**:
   ```python
   # Append 12 contracts under category="self", subtopic="relation":
   "self.relation.venus_aries.v1": InterpretationContract(...)
   ...
   ```
5. **`backend/app/interpretation/engine.py`**:
   ```python
   # Map signals:
   "venus_sign_{sign}": "self.relation.venus_{sign}.v1",
   "venus_{sign}": "self.relation.venus_{sign}.v1",
   ```
6. **`backend/app/interpretation/library.py`**:
   ```python
   # Add "venus_corpus.json" to _load_corpus_fixture()
   ```

**Zero database migrations are needed.** Consistent with Phase 3.4, `astro_safe_profile` table remains untouched, and derived safe fields are populated at API runtime.

---

## 9. Proposed Test Strategy

Prior to Phase 3.6 pilot generation, a dedicated test suite `tests/interpretation/test_venus_contracts.py` will verify:
1. All 12 contracts present in `INTERPRETATION_CONTRACTS`.
2. Signal routing resolves `venus_sign_{sign}` and `venus_{sign}` to `self.relation.venus_{sign}.v1`.
3. All contracts possess $\ge 3$ distinct semantic angles.
4. `SafeDerivedAstrology` and `SafeDerivedAstrologyResponse` expose `venus_sign` while strictly hiding `venus_longitude`, `retrogrades`, and houses.
5. All 153 existing tests continue to pass green.

---

## 10. Unresolved Questions & Risks

1. **Category Subtopic Naming:**
   - Current contracts use `self.cognition` for Mercury.
   - Proposed for Venus: `self.relation` (or `self.relating`).
   - *Recommendation:* Lock `self.relation.venus_{sign}.v1` as standardized in Phase 3.5.
2. **Batch Volume in Phase 3.6:**
   - Pilot Batch: 12 signs × 3 assets = 36 assets (Pilot Gate).
   - Full Batch: 12 signs × 8 assets = 96 assets (72 Micro, 24 Medium).
   - Follows the identical proven pipeline of Mercury Phase 3.3 $\to$ 3.4.

---

## 11. Final Verdict

# VENUS_CONTRACTS_READY_FOR_PILOT
