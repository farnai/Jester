# Home Visual Experiment 02 — JESTER Authenticated Home Reimagination

- **Status:** COMPLETED THROUGH STAGE 5 — AWAITING FOUNDER APPROVAL GATE (Stage 6)
- **Date:** 2026-10-28
- **Target Surface:** Authenticated User Home (`/` — `frontend/src/modules/home/HomePage.tsx` & `frontend/src/modules/home/HomeEditorial.tsx`)
- **Authorization Scope:** **DESIGN EXPLORATION ONLY.** Zero application source files (`frontend/`, `backend/`, `supabase/`) modified.
- **Canvas Location:** `design/visual-studio/canvas/JESTER — Visual Exploration 02.pen`
- **Exported Renders:** `design/visual-studio/experiments/home-02/exports/`
- **Audit & Capability Matrix:** `design/visual-studio/experiments/home-02/CAPABILITY_MATRIX_AND_AUDIT.md`
- **Independent Visual Critique:** `design/visual-studio/experiments/home-02/REVIEW.md`

---

## 1. Strategic Creative Thesis: The Contemporary JESTER Court

JESTER is a **People Discovery & Relationship Intelligence Platform** built around the core loop `ME → YOU → US → MORE PEOPLE` and two non-negotiable axioms (`docs/JESTER_PRODUCT_FOUNDATION.md`):
- *Score creates curiosity. Interpretation creates value.*
- *The insight becomes the invitation.*

Historically, the court Jester was the only figure intelligent, observant, and privileged enough to tell the monarch uncomfortable truths while making the room laugh. Experiment `home-02` translates that archetype into a **modern, daylight-warm digital salon** (**10/10 Playful + Social + Experimental**):
- **Emotional Sequence on Opening Home:**
  1. **Personally Addressed & Distinguished:** Greeted by name into a personal edition rather than a generic unauthenticated landing billboard.
  2. **Playfully Challenged:** Confronted with an unexpectedly accurate, dryly funny Georgian observation + **open 3 Do / 3 Don't daily ritual** (liberated from nested `<details>` accordions).
  3. **Self-Discovery (`ME`):** Progressive 1-tap access to JESTER's 10 resolved personality dimensions (`POST /v1/interpretations/resolve-natal`).
  4. **Human-First Curiosity (`YOU` & `MORE PEOPLE`):** Real human portraits framed in **vaulted salon arches** with **circular shared-interest medallions**, 6-photo gallery indicators, and JESTER's relational observations — zero swipe-to-discard gamification.
  5. **Natural Invitation & Virality (`US`):** Screenshot-ready truth cards and shuffleable conversation sparks that eliminate banal `"როგორ ხარ?"` openers.

### Non-Negotiable Visual & Privacy Guardrails Enforced
1. **Verified Token Discipline (`frontend/src/ui/tokens/colors.ts`, `docs/design/JESTER_COLOR_DESIGN_SYSTEM_V1.md`):**
   - Daylight canvas `#FAF7F2`, pure card `#FFFFFF`, warm alt `#F3EEE6`, elevated chrome `#FFFDFA`, Peach insight tint `#FBEEE7` / `#F5DDD1`, Sage ritual `#E8EFE2` / `#4B6242`, theatrical inverse spotlight `#222630`.
   - **Strict Contrast Invariant:** Every `#FF7A2F` Carrot Orange surface uses **`#222630` Deep Charcoal text/icons (`5.82:1` WCAG AA)** — including notification badges (fixing the current app's `2.60:1` white-on-orange badge defect). `#FFFFFF` text is used **only** on `#222630` (`15.1:1`) or `#9E4215` (`6.47:1`).
2. **Georgian-First Typography (`frontend/src/ui/tokens/typography.ts`):**
   - `Noto Sans Georgian`, `line-height >= 1.55` across all headings/body, `font-size >= 12px` floor (eliminating the `9px–11px` violations in current `homeEditorial.css`), bold weight hierarchy (`800`/`700`/`600`), zero `uppercase` transforms, zero missing Unicode arrow glyphs.
3. **Privacy, Safety & Zero Prohibited Tropes:**
   - `18+` adult notice preserved; zero exposure of `public.birth_data` or `public.astro_private`; zero astrological jargon (`გრადუსი`, `სახლი`, `ტრანზიტი`, `რეტროგრადი`), crowns, medieval parchment, carnival bells, clown masks, or occult zodiac wheels. All exploration portraits are explicitly labeled synthetic concept assets.

---

## 2. Georgian Brand Voice & Witty Truth Tone System (8 Contexts)

> **Core Voice Principle:** *„ის, ვინც გეუბნება სიმართლეს, რასაც სხვები ვერ გიბედავენ — და თან გაღიმებს.“*
> Sharp observational irony (`docs/AI.md`) aimed at universal human contradictions — **never** mockery (`დაცინვა`), **never** punching down, and **zero sarcasm** during privacy, safety, or emotional friction moments.

| # | Product Context | Wit Dial | Georgian Tone Rule | Representative In-Design Georgian Copy |
| :--- | :--- | :---: | :--- | :--- |
| **1** | **Daily Observations & 3 Do / 3 Don't** | `9/10` | Punchy 2-sentence recognition + crisp 2-word action cues (`daily_energy_tags.json`). | *„დღეს ზუსტად ხედავ, სად მთავრდება სხვისი დრამა და სად იწყება შენი საქმე. გამოიყენე ეს სიმშვიდე, სანამ ვინმემ ისევ თავის ქაოსში ჩაგითრია.“* |
| **2** | **Personalized `ME` Insights** | `8/10` | Exposes the gap between outward composure (`self.persona`) and inner wiring (`self.cognition` / `self.emotional`). | *„კამათში ხმას არ უწევ — უბრალოდ ერთ ისეთ ზუსტ კითხვას სვამ, რომ მეორე მხარე თვითონ ხვდება წინააღმდეგობას.“* |
| **3** | **Self-Discovery & Profile Prompts** | `7/10` | Warmly provocative dare against lazy blank profiles; invites real human specificity. | *„ცარიელი პროფილი იდუმალება არ არის — უბრალოდ სიზარმაცეა. დაწერე ორი ნამდვილი წინადადება შენზე.“* |
| **4** | **Connection Recommendations (`YOU`/`US`)** | `8/10` | Celebrates concrete shared interests (`common_interest_ids`) and dynamic contrast without cheesy % hype. | *„ელენე მშვიდად აკვირდება გარემოს, მაგრამ იუმორი ისეთი მშრალი და ზუსტი აქვს, მოუმზადებელს დაგიჭერს.“* |
| **5** | **Social Interactions & Starters** | `8/10` | Kills small-talk awkwardness; turns insights into effortless 1-tap invitations. | *„დაივიწყე „როგორ ხარ?“ — ჰკითხე: რა არის ის უცნაური წვრილმანი, რაც ადამიანში პირველივე ხუთ წუთში გაწონებს თავს?“* |
| **6** | **Empty States (`0` Connections / Unknown Time)** | `6/10` | Reassuring, dryly observant, zero fake accounts, zero user guilt. | *„შენი წრე ჯერ თავისუფალია — და ეს ბევრად სჯობს შემთხვევითი ხალხით სავსე სიას.“* |
| **7** | **Errors, Retry & Validation** | `4/10` | Light self-aware humility directed only at the system, followed immediately by clear recovery. | *„დღის დაკვირვებამ გზაში ცოტა დაიგვიანა. სანამ განვაახლებთ, ადამიანების დათვალიერება ჩვეულებრივად მუშაობს.“* |
| **8** | **Sensitive, Privacy & Safety Moments** | **`0/10`** | **100% calm, dignified, transparent.** Zero irony on blocking, declines, friction, or birth-data privacy. | *„დაბადების თარიღი, საათი და კოორდინატები მხოლოდ შენ გეკუთვნის და სხვებისთვის არასდროს ჩანს.“* |

---

## 3. Bespoke JESTER Graphic Language (`Motifs 1–5`)

Built as pure scalable vector components on the `.pen` canvas (`Home 02 — Brand Motifs, Voice & Reusable System Sheet`, node `qWsWT`):
1. **Motif 1 — Contemporary Court Arch & Seal (`თაღი და ბეჭედი`):** Vaulted portrait mask (`cornerRadius: [R_top, R_top, 20, 20]`) paired with an unclipped bottom-right circular medallion (`3px` `#FFFFFF` halo ring) displaying shared-interest counts (`3+`, `2+`) while keeping the facial triangle (`18%–82% X, 15%–72% Y`) 100% unobstructed.
2. **Motif 2 — Three-Perspective Spark (`სამი ხედვის ნაპერწკალი`, component `Icif9`):** Asymmetric 3-ray convergence (*Curiosity, Understanding, Empathy*) + suspended `#FF7A2F` truth orb (`viewBox: [0,0,24,24]`), replacing generic AI stars (`✦`) across navigation and JESTER provenance headers.
3. **Motif 3 — Witty Truth Bracket (`სიმართლის ჩარჩო`):** `45°` chamfered architectural corner brackets (`cornerRadius: [6, 28, 6, 28]`) exclusively framing JESTER's voice, never user-written bios or chat messages.
4. **Motif 4 — Dual Ritual Tokens for 3 Do / 3 Don't (`SAoJJ` & `QvQw5`):** Non-clinical shape + color + glyph differentiation: upright Sage arch with forward compass lancet (`გაბედე`, `#4B6242` on `#E8EFE2`) vs chamfered Terracotta threshold barrier (`მოერიდე`, `#9E4215` on `#FFE7D7`) — zero punitive red `✕` error icons.
5. **Motif 5 — Relational Resonance Thread (`კავშირის ძაფი`, component `DEinx`):** Counter-poised `ME` and `YOU` perspective arcs sweeping around a central `#FF7A2F` `US` spark diamond — zero romantic hearts or occult aspect lines.

---

## 4. Three Genuinely Divergent Home Concepts (14-Attribute Specifications)

### Direction A — „პირადი კარი“ (*The Personal Court*)
1. **Creative Thesis:** Authenticated Home as an intimate morning/evening audience in a contemporary salon where JESTER greets you by name, delivers today's unvarnished truth alongside an open **3 Do / 3 Don't Salon Pact Ledger**, offers a progressive `ME` blind-spot mirror, and opens arched gallery doors to 3 curated people and your active `US` circle.
2. **Primary Emotional Effect:** Addressed & distinguished → playfully challenged → self-curious → socially intrigued → ready to share.
3. **Main User Journey:** `Salon Greeting` → `Ceremonial Daily Truth + 1-Tap Pact Stamp` → `Progressive ME Blind-Spot Strip` → `3 Arch-Cropped Human Introductions (MORE PEOPLE)` → `Twin-Arch US Relationship Dynamic`.
4. **Proposed Home IA:** (1) Personal Edition Greeting + Pending/Circle Pills; (2) Asymmetric `ME` Truth Card + Open 2-Column `3 Do / 3 Don't` Ledger; (3) `ME` Self-Mirror Strip (`resolve-natal`); (4) 3-Up Arch Candidate Floor (`DiscoveryDeckPerson`) + Sticky `US` Inner Circle Card; (5) `18+` & Privacy Footer.
5. **Daily Insight & 3 Do / 3 Don't Treatment:** Zero accordions — all 6 tags from `GET /v1/interpretations/daily-energy` sit open in a structured Sage/Terracotta Salon Ledger where tapping a `Do` chip stamps it as your chosen daily move.
6. **People Discovery Treatment:** 3 curated arch-cropped portraits (`photos[0..5]` count badge + `46px` `#FF7A2F` shared-interest seal + `#FFE7D7` shared interest pills + JESTER `hook_observation`).
7. **Brand Voice Examples:** *„საღამო მშვიდობისა, ნინო.“* · *„დღეს ზუსტად ხედავ, სად მთავრდება სხვისი დრამა და სად იწყება შენი საქმე.“*
8. **Visual Identity Approach:** Warm `#FAF7F2` salon paper, `#FBEEE7` chamfered Truth Frame, `#FFFFFF` structured Ledger, `#F3EEE6` `US` alcove with `Motif 5A` Resonance Bridge.
9. **Desktop `1440px` Composition (`KZzuf`):** `1280px` container: Top Edition Bar → `736px / 520px` equal-height (`336px`) Hero Truth + Ledger split → Full-width `ME` Self-Mirror strip → `820px` equal-height (`513px`) 3-Arch Candidate Row → `736px / 520px` equal-height (`613px`) `US` Dynamic + Salon Invitation Floor.
10. **Mobile `390px` Composition (`J9hQRx`):** Top Bar + Personal Greeting (`48px` request pill) + Ceremonial Truth & `48px` Share CTA + Open 2-Column `3 Do / 3 Don't` Ledger (`52px` tactile chips with `SAoJJ`/`QvQw5` tokens) + `Mobile Progressive ME Self-Mirror Card` (`48px` `/me` CTA) + Full-Width Arch Candidate Cards (`1/5 ფოტო` cues, occupation/city, `✦` shared interests, `48px` CTAs) + `US` Active Pair Dynamic.
11. **Interaction & Motion Ideas:** `180ms` gentle curtain rise on load; tactile `scale(0.98)` Pact Stamp check; tap-left/right inline photo stepping (`prefers-reduced-motion` switches to opacity-only).
12. **Reusable Components:** `SalonTruthFrame`, `DailyPactLedger`, `ArchCandidateCard`, `TwinArchUsCard`.
13. **Capability Dependencies:** **100% `EXISTING` + `DERIVABLE`** (`profiles/me`, `daily-energy`, `safe-astro` + `resolve-natal`, `discovery/people`, `connections`, `people/{id}/why`). Zero `PROPOSED` backend blockers.
14. **Strengths, Weaknesses & UX Risks:** *Strengths:* Highest editorial dignity, immediate daily ritual utility, zero backend wait. *Weakness:* `ME`-first vertical priority means full people cards sit lower on mobile than Direction B. *Risk Mitigation:* Punchy `#FF7A2F` CTAs and sharpened dryly observant Georgian copy (*„სხვის ქაოსში მშვიდი მსაჯული“*) prevent museum stiffness.

---

### Direction B — „ცოცხალი პორტრეტები“ (*Human-First Living Gallery*)
1. **Creative Thesis:** Real human beings become the immediate above-the-fold centerpiece while JESTER whispers beside you as a sharp gallery curator — pairing a 4-second **Morning Espresso Daily Vibe Strip** with rich, vertically scrollable **Multi-Photo Arch Portrait Stories**.
2. **Primary Emotional Effect:** Instant social warmth & human presence → quick smile at morning vibe → multi-photo curiosity & shared-interest discovery → natural connection impulse.
3. **Main User Journey:** `Morning Espresso Daily Strip + 6 Ritual Tags` → `Active Circle Ribbon (US)` → `Living Portrait Story #1 (Above Mobile Fold!)` → `Interleaved ME Self-Mirror` → `Living Portrait Story #2 (with explicit PROPOSED Prompt exploration)`.
4. **Proposed Home IA:** Desktop `400px` Sticky Personal Curator Rail (`ME` Daily Vibe + `US` Circle Ribbon + `ME` Mirror) paired with an `840px` Curated Daily Portrait Stream (`დღის 2 რჩეული პორტრეტი` + `ყველა ადამიანი (12)` link to `/discover`); Mobile compact top ticker + `48px` Circle strip + full above-the-fold Living Portrait Card #1.
5. **Daily Insight & 3 Do / 3 Don't Treatment:** Compressed into a fast-scanning `#FBEEE7` Morning Espresso card with equal-height (`66px`) inline **3 `Do`** (`#E8EFE2`) and **3 `Don't`** (`#FFFFFF`) summary strips and a `48×48px` quick-share button so repeat visitors absorb all 6 daily cues in seconds.
6. **People Discovery Treatment:** Anti-swipe vertical story spreads combining tall vaulted arch portraits (`1/5` & `1/4 ფოტო` tap-steppers + unclipped `#FF7A2F` circular shared-interest seals), `✦`-prefixed `#FFE7D7` `common_interest_ids`, JESTER `hook_observation`, `EXISTING` `bio`, AND a clearly badged **`PROPOSED` Prompt Q&A module** (`კონცეპტუალური მოდული · PROPOSED`).
7. **Brand Voice Examples:** *„დღეს შენი თავდაჯერება ოთახში შენზე ხუთი წუთით ადრე შემოდის — მთავარია, სხვებსაც დაუტოვო სკამი.“*
8. **Visual Identity Approach:** Sunlit gallery `#FAF7F2` canvas, generous `#FFFFFF` portrait spreads (`28px` radius), standardized `#FF7A2F` + `#222630` circular seals, `#E8EFE2` interleaved self-mirror cards.
9. **Desktop `1440px` Composition (`z5IEM`):** Asymmetric 2-column magazine layout (`400px` left rail + `40px` gutter + `840px` right curated horizontal story spreads with `48px` route link to `/discover`).
10. **Mobile `390px` Composition (`EESTW`):** Compact Morning Espresso ticker + `48px` Circle strip positions Candidate #1 (`mLk3z`) so its arch portrait, shared interests, JESTER hook, and `48px` `გაიცანი ახლოს` CTA finish at **`~694px`** (`74px` clear above the `76px` sticky bottom dock inside a `390×844` viewport!), followed by the interleaved `ME` card (`48px` `/me` CTA) and Sandro's spread.
11. **Interaction & Motion Ideas:** Tap-right/left 6-photo crossfade (`150ms`, zero horizontal swipe-to-reject!); subtle one-time medallion entrance pulse; bottom half-sheet preview when tapping a connected friend in the Circle strip.
12. **Reusable Components:** `MorningEspressoTicker`, `CircleStoryRibbon`, `LivingPortraitSpread`, `SelfMirrorInterlude`.
13. **Capability Dependencies:** Core stream is **100% `EXISTING` + `DERIVABLE`** (`GET /v1/discovery/people` provides `photos[]`, `interests[]`, `common_interest_ids[]`, `same_city`, `hook_observation`, `bio`); Candidate #2 explicitly illustrates how `PROPOSED` `user_prompts` slots in later while degrading cleanly to `bio` today.
14. **Strengths, Weaknesses & UX Risks:** *Strengths:* Strongest above-the-fold human warmth and discovery engagement on mobile. *Weakness:* Daily `ME` truth is more compact/ancillary than in A or C. *Risk Mitigation:* Capping Home to 2–3 curated daily portraits with a clear `ყველა ადამიანი (12)` link preserves sharp separation from `/discover`.

---

### Direction C — „ჯესტერის სცენა“ (*The Living Jester Stage — 10/10 Experimental*)
1. **Creative Thesis:** JESTER as a living, interactive product personality: a jewel-like **Theatrical Dialogue Stage** (`#222630` spotlight card on Desktop; warm `#FFF6F0` framed stage with `#222630` marquee pill on Mobile to preserve daylight balance) paired with a live **Truth-Flip switcher**, tactile **6-chip Do/Don't apron**, interactive **4-Facet `ME` Self-Discovery Lens**, **Motley Asymmetric Social Collage**, and **Conversation Spark Shuffler**.
2. **Primary Emotional Effect:** Immediate surprise & theatrical distinction → grinned recognition on flipping daily truth vs permanent verdict → active self-exploration across 4 facets → playful curiosity across a living collage of people and sparks.
3. **Main User Journey:** `Theatrical Dialogue Stage (Daily Truth ⇄ ME Verdict + 6 Tactile Chips + Story Share)` → `4-Facet ME Lens (ხასიათი · ემოცია · საუბარი · მიზიდულობა)` → `Motley Social Collage (Featured Arch + US Dual-Arch + Secondary Arches + Spark Shuffler)`.
4. **Proposed Home IA:** (1) Top Stage & Self-Lens Band (Equal-height `468px` Spotlight Stage + `#FFFFFF` 4-Facet `ME` Selector); (2) Bottom Asymmetric Motley Social Collage (Equal-height `569px` columns: Tall Featured Candidate Arch + `US` `#E8EFE2` Dual-Arch Chemistry Tile stacked over 2 Mini Arches + `#FBEEE7` Shuffleable Conversation Spark Launcher for `accepted` circle chats); (3) `18+` Footer.
5. **Daily Insight & 3 Do / 3 Don't Treatment:** All 6 `do_ka`/`dont_ka` tags appear directly on the stage apron as interactive Sage (`#E8EFE2`/`#4B6242`) and Terracotta (`#FFE7D7`/`#9E4215`) chips (`>= 44px` Desktop, `>= 52px` Mobile); tapping one marks it with an explicit `✓` checkmark + `#FF7A2F` (`#222630` text) and updates JESTER's live whisper (*„ჩანიშნულია. თუ მაინც შეგეშალა, ჩვენ არავის ვეტყვით.“*).
6. **People Discovery Treatment:** Desktop **Motley Patchwork Collage** (`Featured Arch` + `US Twin Arches` + `2 Staggered Secondary Arches`) and Mobile **Full-Width (`358px`) Editorial Story Cards** (`1/5` & `1/4 ფოტო` cues, `#FF7A2F` seals, `✦` shared-interest pills, JESTER observations, `48px` CTAs).
7. **Brand Voice Examples:** *„დღეს ყველას რჩევას ურიგებ — და ყველაზე სასაცილო ისაა, რომ მართალი ხარ. უბრალოდ ყველას ჯერ არ უკითხავს.“*
8. **Visual Identity Approach:** Strictly disciplined **Warm Paper `#FAF7F2` Canvas** paired with a contained `#222630` desktop stage card (and warm `#FFF6F0` + `#222630` marquee stage on mobile) plus `#FF7A2F` / `#E8EFE2` / `#FBEEE7` Motley accents.
9. **Desktop `1440px` Composition (`phkQC`):** Top band `760px` Spotlight Stage + `496px` 4-Facet `ME` Lens (`468px` equal height); Bottom band `420px` Featured Arch + `472px` (`US` Dual-Arch + 2 Mini Arches) + `340px` Spark Shuffler (`569px` equal height).
10. **Mobile `390px` Composition (`kxBNd`):** Warm `#FFF6F0` framed stage (`48px` Truth-Flip pill, `52px–54px` checkable `3 Do / 3 Don't` chips, whisper confirmation, `48px` Share CTA) + `2×2` `48px` **4-Facet `ME` Selector** (intact `მიზიდულობა`) + 2 full-width (`358px`) rich human story cards + `US` Dual-Arch tile (`48px` CTA) + Spark Shuffler (`48px` `სხვა კითხვა` + `accepted`-only chat CTA).
11. **Interaction & Motion Ideas:** `220ms` card-flip/crossfade between `დღის სიმართლე` and `შენი ვერდიქტი`; `180ms` sliding pill across the 4 `ME` facets; `150ms` deck-shuffle on `სხვა კითხვა` (`0ms`/opacity-only under `prefers-reduced-motion`).
12. **Reusable Components:** `JesterSpotlightStage`, `NatalFacetLens`, `DualArchChemistryTile`, `SparkShufflerCard`.
13. **Capability Dependencies:** **100% `EXISTING` + `DERIVABLE`!** Unlocks `daily-energy` (quote + 6 tags), `resolve-natal` (5 of 10 `ME` dimensions interactively on Home!), `discovery/people` (`DiscoveryDeckPerson`), and `people/{id}/why` (`conversation_starters[]` for `accepted` connections) with zero new backend tables required.
14. **Strengths, Weaknesses & UX Risks:** *Strengths:* Most unmistakably original `10/10` JESTER identity, deepest interactive self-discovery (`ME`), and highest organic screenshot-sharing potential. *Weakness:* Highest interactive density of the three concepts. *Risk Mitigation:* Warm `#FFF6F0` mobile stage + `2×2` `48px` facet buttons keep mobile breathable and light-first.

---

## 5. Complete `.pen` Canvas Artifact Inventory (Post-Stage-5 Verified)

Saved in `design/visual-studio/canvas/JESTER — Visual Exploration 02.pen` (preserving prior frames `muxVY`, `XufCt`, `K075v`, `bi8Au` untouched at `y: -180..3492`):

| Node ID | Frame / Component Name | Kind | Final Dimensions | Canvas `(x, y)` | Exported `2x` PNG |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `O9jVt0` | `Component / Jester Brand Logo` | Reusable Component | `158 × 28` | `(900, 3820)` | *(Instanced)* |
| `PCzv0` | `Component / Desktop AppShell Nav` | Reusable Component | `1440 × 76` | `(1620, 3800)` | *(Instanced)* |
| `MQrOa` | `Component / Mobile AppShell Top Bar` | Reusable Component | `390 × 60` | `(3120, 3800)` | *(Instanced)* |
| `B3aESw` | `Component / Mobile 5-Tab Bottom Dock` | Reusable Component | `390 × 76` | `(3120, 3880)` | *(Instanced)* |
| `Icif9` | `Component / Motif 2 Three-Perspective Spark` | Reusable Component | `24 × 24` | `(900, 3995)` | *(Instanced)* |
| `SAoJJ` | `Component / Motif 4A Do Ritual Token` | Reusable Component | `28 × 28` | `(940, 3995)` | *(Instanced)* |
| `QvQw5` | `Component / Motif 4B Dont Ritual Token` | Reusable Component | `28 × 28` | `(984, 3995)` | *(Instanced)* |
| `DEinx` | `Component / Motif 5A Resonance Bridge` | Reusable Component | `120 × 32` | `(1028, 3995)` | *(Instanced)* |
| `PpRBE` | `Home 02 — Synthetic Editorial Portrait Bank (Concept Exploration Only)` | Asset Frame | `424 × 182` | `(1120, 3800)` | — |
| `qWsWT` | `Home 02 — Brand Motifs, Voice & Reusable System Sheet` | System Sheet | `1440 × 792` | `(900, 4050)` | `exports/qWsWT.png` |
| `KZzuf` | `Home 02 · Direction A: Personal Court — Desktop 1440` | Concept Screen | `1440 × 1474` | `(900, 5002)` | `exports/KZzuf.png` |
| `J9hQRx` | `Home 02 · Direction A: Personal Court — Mobile 390` | Concept Screen | `390 × 2199` | `(2420, 5002)` | `exports/J9hQRx.png` |
| `z5IEM` | `Home 02 · Direction B: Human Discovery — Desktop 1440` | Concept Screen | `1440 × 1247` | `(900, 7361)` | `exports/z5IEM.png` |
| `EESTW` | `Home 02 · Direction B: Human Discovery — Mobile 390` | Concept Screen | `390 × 1512` | `(2420, 7361)` | `exports/EESTW.png` |
| `phkQC` | `Home 02 · Direction C: Living Jester — Desktop 1440` | Concept Screen | `1440 × 1379` | `(900, 9033)` | `exports/phkQC.png` |
| `kxBNd` | `Home 02 · Direction C: Living Jester — Mobile 390` | Concept Screen | `390 × 2485` | `(2420, 9033)` | `exports/kxBNd.png` |
| `A3wQ2` | `Home 02 — Representative Interaction, Missing-Data & Honest System States` | States Sheet | `1440 × 766` | `(900, 11678)` | `exports/A3wQ2.png` |

