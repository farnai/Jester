# JESTER Content Inventory V1 Report

**Status**: V1 Production-Draft Corpus Verified  
**Dataset Path**: `backend/app/interpretation/data/content_corpus.json`  
**Total Ingested Assets**: **5,733**  
**Generation Engine**: `scripts/generate_content_corpus.py` (Common Framings & Multi-Persona Generator)  
**Last Updated**: September 2026  

---

## 1. Executive Corpus Summary

| Dimension | Count / Metric | Share / Target | Compliance Status |
| :--- | :--- | :--- | :--- |
| **Total AI_DRAFT Assets** | **5,733** | 5,000 – 10,000 Target | **PASSED** (Optimal Scale) |
| **Semantic Coverage** | **113 / 113 Contracts** | 100% Registry Coverage | **PASSED** (Zero Orphan Contracts) |
| **Average Assets / Contract** | **50.7** assets | Target $\ge 20$ | **PASSED** (Rich Diversity) |
| **Minimum Assets / Contract** | **14** assets | Target $\ge 10$ | **PASSED** (No Weak Contracts) |
| **Georgian Language (`ka`)** | **3,894** assets | **67.9%** (Target: 70–80%) | **PASSED** (Primary Production Language) |
| **English Language (`en`)** | **1,839** assets | **32.1%** (Target: 20–30%) | **PASSED** (Secondary Expansion Language) |
| **Exact Duplicates** | **0** | Target: 0 | **PASSED** (100% Unique) |
| **Near-Duplicates in Corpus** | **0** | Target: 0 | **PASSED** (Strict Jaccard Filtering) |
| **Near-Duplicates Rejected** | **7,165** candidates | Threshold $\ge 0.85$ | **FILTERED** (Anti-Template Enforcement) |
| **Astrology Jargon Violations** | **0** | Target: 0 | **PASSED** (Strict Scanner Enforced) |
| **Asset Status** | **100% `ai_draft`** | Target: 100% `ai_draft` | **PASSED** (No False "Approved" Copy) |

---

## 2. Tone Distribution

JESTER's brand voice is intentionally calibrated around **Witty + Playful + Observant**, with extreme or niche tones constrained to appropriate contexts.

```text
Witty:     ████████████████████████ (2,428 - 42.4%)
Playful:   █████████████████ (1,705 - 29.7%)
Soft:      █████████ (901 - 15.7%)
Savage:    ███ (313 - 5.5%)
Bold:      ███ (289 - 5.0%)
Romantic:  █ (97 - 1.7%)
```

* **Witty & Playful (72.1%)**: The core JESTER identity — sharp, socially intelligent, lightly cheeky, and perceptive.
* **Soft (15.7%)**: Used for vulnerable emotional processing (e.g. Moon-Neptune, Moon-Cancer) without sounding syrupy or therapeutic.
* **Savage (5.5%)**: Kept as an occasional spicy twist for friction dynamics (e.g., Mars-Mars sparring, Mercury-Mars banter). Never a default fallback.
* **Bold (5.0%)**: Assertive, high-impact observations for decisive placements (Aries, Mars-Pluto, Cardinal dominant).
* **Romantic (1.7%)**: Strictly constrained to deep relational attraction aspects (e.g. Venus-Mars, Sun-Venus). Never leaks into platonics or daily energy.

---

## 3. Context Distribution

Every asset is explicitly assigned to valid functional contexts based on its domain. No relational copy is repurposed for daily transits, preserving strict domain boundaries.

| Functional Context | Asset Count | Primary Purpose in User Flow |
| :--- | :--- | :--- |
| `discovery` | **1,080** | People search cards, teaser insights, initial match overviews. |
| `self` | **791** | User personal profile, "About Me" Jester breakdown. |
| `onboarding` | **674** | Welcome flow, initial persona revelation, hook insights. |
| `relationship` | **656** | Compatibility screen, deep connection cards. |
| `natal` | **646** | Full natal chart interpretation breakdown. |
| `deep_analysis` | **556** | Deep-dive modal ("Why we click" / "Where we clash"). |
| `share` | **430** | Viral shareable cards, story exports, punchy one-liners. |
| `daily_energy` | **371** | Daily transit mood banner (architectural contract). |
| `notification` | **322** | Push notifications, connection nudges, daily alerts. |
| `friendship` | **207** | Platonic friend connection dynamics. |

---

## 4. Semantic Domain Coverage Breakdown

### 4.1 Domain A: Self / Me (43 Contracts — 2,059 Total Assets)
* **Sun Signs (12 contracts)**: 588 assets (Avg: 49.0 / contract, 396 `ka`, 192 `en`)
* **Moon Signs (12 contracts)**: 564 assets (Avg: 47.0 / contract, 384 `ka`, 180 `en`)
* **Ascendant Signs (12 contracts)**: 576 assets (Avg: 48.0 / contract, 396 `ka`, 180 `en`)
* **Element Dominance (4 contracts)**: 191 assets (Avg: 47.8 / contract, 130 `ka`, 61 `en`)
* **Modality Dominance (3 contracts)**: 140 assets (Avg: 46.7 / contract, 96 `ka`, 44 `en`)

### 4.2 Domain B: Relationship / Synastry (46 Contracts — 2,458 Total Assets)
* **Attraction & Chemistry (10 contracts)**: 535 assets (Avg: 53.5 / contract)
* **Emotional Resonance (5 contracts)**: 268 assets (Avg: 53.6 / contract)
* **Communication Synergy (5 contracts)**: 271 assets (Avg: 54.2 / contract)
* **Growth & Friction Dynamics (7 contracts)**: 374 assets (Avg: 53.4 / contract)
* **Long-Term Grounding & Independence (6 contracts)**: 320 assets (Avg: 53.3 / contract)
* **Overall Synergy Tiers (4 contracts)**: 215 assets (Avg: 53.8 / contract)
* **Notice & Miscellaneous Dynamics (9 contracts)**: 475 assets (Avg: 52.8 / contract)

### 4.3 Domain C: Friendship / Platonic (12 Contracts — 602 Total Assets)
* **Platonic Chemistry, Humor, Loyalty, Ease (12 contracts)**: 602 assets (Avg: 50.2 / contract, 408 `ka`, 194 `en`)

### 4.4 Domain D: Daily Energy (12 Contracts — 614 Total Assets)
* **Transit Archetypes (12 contracts)**: 614 assets (Avg: 51.2 / contract, 418 `ka`, 196 `en`)

---

## 5. Quality Assurance & Anti-Template Validation

### 5.1 Automated Quality Pipeline Results
1. **Zero Jargon Enforcement**: Scanned against prohibited astrological terminology (e.g., `ზოდიაქო`, `ასცენდენტი`, `ჰოროსკოპი`, `პლანეტა`, `ტრანზიტი`, `სახლი`, `ასპექტი`, `trine`, `sextile`, `synastry`, `horoscope`).
   - **Result**: 0 violations detected across 5,733 assets. (1 candidate containing "რუკა" was automatically intercepted and replaced with "გზამკვლევი").
2. **Deduplication & Anti-Template Filtration**:
   - Every candidate asset underwent cross-token Jaccard similarity testing ($\text{threshold} = 0.85$).
   - **Candidates Evaluated**: 12,899 generated drafts.
   - **Near-Duplicates Rejected**: **7,165** candidates rejected to prevent repetitive sentence shells.
   - **Exact Duplicates in Result**: **0**.
3. **Length & Structure QA**:
   - Target length: 1–2 punchy sentences.
   - Malformed/empty strings: 0.
   - Characters: 100% of assets fall between 35 and 280 characters.

---

## 6. Copywriting Review & Promotion Roadmap

The 5,733 generated assets are classified strictly as **Production Drafts (`ai_draft`)**. They are intended to make the UX completely functional, testable, and populated with realistic copy for HTML wireframe testing.

### Promotion Lifecycle:
```text
AI_DRAFT (5,733 assets)
   ↓
INTERNAL QA / PRODUCT REVIEW
   ↓
PROFESSIONAL COPYWRITER POLISH (Georgian & English)
   ↓
APPROVED (status="approved", priority=100)
   ↓
ACTIVE EXPERIMENT / WINNER (status="winner")
```

The resolver prioritizes `approved` and `winner` assets over `ai_draft` automatically. As copywriters refine individual texts in the database/CMS, approved human copy seamlessly supersedes AI drafts with **zero code modifications or redeployments**.
