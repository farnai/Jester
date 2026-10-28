# JESTER — Founder Decision Records (FDR)

**Document Type:** Founder decision provenance and canonical-document index\
**Governance:** Product intent under [AGENTS.md — Source of Truth](../AGENTS.md#source-of-truth); no additional authority tier\
**Status:** ACTIVE; approval scope is recorded per decision\
**Last Updated:** 2026-10-28  

---

## Overview

This document records Founder decisions and their scope. Under `AGENTS.md`, approved owner decisions inform product intent; code, migrations and tests establish implementation, persistence/security and verified behavior respectively. This register does not override those authorities or create a competing specification. Conflicts follow the `AGENTS.md` Conflict Protocol.

Canonical ownership remains with [Product Foundation](JESTER_PRODUCT_FOUNDATION.md), [Home Experience](HOME_EXPERIENCE.md), [Discovery Wave 3](DISCOVERY_WAVE3.md), [Design Exploration](JESTER_DESIGN_EXPLORATION.md) and [Architecture v1.2](architecture/JESTER_PRODUCT_FRONTEND_ARCHITECTURE_V1_2.md). Entries below summarize decisions and point to those owners; runtime details belong in source and the relevant capability document.

Approval terms follow [Architecture v1.2 approval criteria](architecture/JESTER_PRODUCT_FRONTEND_ARCHITECTURE_V1_2.md#12-approval--completion-criteria). `INTERACTION_POLICY_APPROVED`, `IMPLEMENTED_LOCAL` and `VISUAL_REVIEW_PENDING` can coexist. `FOUNDER_VISUAL_APPROVED` requires explicit approval of the specific rendered implementation; neither implementation nor direction selection supplies that evidence.

---

## FDR-2026-01: Photo-First Human Discovery & Touch-Native Swipe Interaction Policy

- **Date:** 2026-10-28  
- **Status:** INTERACTION_POLICY_APPROVED; Wave 3 IMPLEMENTED_LOCAL; VISUAL_REVIEW_PENDING\
- **Supersedes:** Early "Anti-Swipe Mandate" (`docs/JESTER_PRODUCT_FOUNDATION.md` v1.0, `docs/JESTER_DESIGN_EXPLORATION.md` §4.1)  
- **Applies to:** Home previews (`/`), Social Discovery (`/discover`), Mobile UX, Product Marketing, Brand Positioning\

### 1. Context & Motivation
Earlier documents restricted swipe gestures more broadly than the Founder direction intended. Photo-forward, swipeable discovery is approved as an interaction principle. This does not approve the visual quality of the current Wave 3 implementation.

Photography is a major, legitimate discovery signal. Users and relationship intents may prioritize shared interests, self-expression, conversation or other information; visual attraction is not a mandatory first step.

### 2. Decision & Core Principles

1. **Photo-First Human Discovery:**  
   High-quality, candid, expressive photography serves as the primary visual gateway into discovering someone's presence, personality, and vibe.
2. **An Illustrative Discovery Journey:**\
   One possible journey, not a required sequence for every user or intent:
   $$\mathbf{Visual\ Attraction} \longrightarrow \mathbf{Personal\ Curiosity} \longrightarrow \mathbf{Deeper\ Understanding} \longrightarrow \mathbf{Meaningful\ Connection}$$
   - **Stage 1: Visual Attraction:** Natural appreciation of human presence, style, and photographic aesthetic.
   - **Stage 2: Personal Curiosity:** Expressive bio statements, lifestyle cadence, values, and self-expression prompts.
   - **Stage 3: Deeper Understanding:** Declared human context and optional astrological interpretations. Deterministic calculations do not establish scientifically validated psychological conclusions.
   - **Stage 4: Meaningful Connection:** The sender explicitly confirms an invitation; the recipient separately accepts or declines.
3. **Touch-Native Mobile Discovery Deck:**  
   On mobile devices, candidates are browsed via an intuitive card deck (`DiscoverSwipeCard.tsx`):
   - **Swipe Left (or ArrowLeft / Next button):** Advances locally to the next candidate (skip/pass) without writing negative rejection telemetry to the database.
   - **Swipe Right (or ArrowRight / Connect button):** Opens connection confirmation; only Send submits the request.
4. **Intentional Connection Consent Safeguard:**  
   A right-swipe **never** triggers an instant, unprompted match or single-flick connection. It opens a focused **confirmation modal/drawer**, requiring an explicit tap on "მოწვევის გაგზავნა" (Send Invitation). Escape or "ჯერ არა" (Not Now) cancels cleanly without sending data.
5. **Decoupled Gesture Architecture:**  
   Candidate navigation is completely separated from photo browsing:
   - Photo taps and dedicated buttons step through the gallery without changing candidates. Dragging is candidate navigation, not an implemented photo-scrubbing gesture.
   - Wave 3 drag thresholds and keyboard behavior are implementation details in `DiscoverSwipeCard.tsx` and [Discovery Wave 3](DISCOVERY_WAVE3.md).
   - Full individual profiles may remain vertically scrollable; details and WHY access follow existing authorization and available data.
   - Home may show a horizontal, touch-friendly profile carousel on mobile. Discover uses the full candidate Swipe Deck; Home need not reproduce all Discover interactions. Avoid vertical stacking of multiple candidate cards on mobile. Vertical scrolling of the overall Home page remains compatible with this rule.
6. **Multi-Intent Dignity:**  
   JESTER is a **People Discovery & Relationship Intelligence** platform spanning friendship, creative collaboration, activity partnerships, intellectual dialogue and intentional romance.
7. **Absolute Separation of Appearance from Computation:**  
   JESTER never assigns numeric scores to physical attractiveness or derives compatibility from photographs. Photography informs human perception; Synastry scores summarize astrological rules, not scientifically validated psychological compatibility.

---

## FDR-2026-02: Photo Framing & Geometric Hierarchy

- **Date:** 2026-10-28  
- **Status:** APPROVED & BINDING  
- **Applies to:** Design Tokens, Mobile & Desktop UI Components, Visual Studio Canvas  

### 1. Context & Motivation
Explorations used arch masks for both small portraits and large photographs. Exaggerated arches can constrain natural crops and obscure faces or posture, especially on mobile.

### 2. Decision & Framing Rules

1. **Large Candidate & Lifestyle Photography:**  
   - Normally use **natural photographic proportions** with **restrained corner radii**. Ratios such as 4:5 or 3:4 are examples, not an exclusive list.
   - Avoid exaggerated arch shapes, especially on mobile. This is a visual preference to evaluate against the actual crop and composition, not an absolute ban on all large-photo arches or a new fixed-radius token rule.
2. **Small Portraits, Avatars & Cameo Badges:**  
   - Distinctive arch framing (`arch-portrait`), circular cameo rings, and subtle brand apertures are authorized and encouraged for avatars, circular shared-interest seals, and thumbnail cards.
3. **Responsive Cropping:**  
   - Images must use `object-fit: cover` with face-safe focal points to preserve human dignity across all viewport widths.

---

## FDR-2026-03: Visual Exploration Synthesis (KZzuf Architecture + phkQC Stage)

- **Date:** 2026-10-28  
- **Status:** DESIGN_DIRECTION_SELECTED; synthesized implementation VISUAL_REVIEW_PENDING\
- **Applies to:** Authenticated Home, AppShell, Future Screen Modernization  

### 1. Context & Motivation
Visual Studio Exploration 02 produced eight distinct art-directed directions. An independent visual critique evaluated them against brand tokens, Georgian typography, spatial rhythm, and responsive viability.

### 2. Decision & Directional Selection

1. **Foundational Visual Architecture: `KZzuf` (Warm Paper Salon / Personal Court):**  
   - Selected for its warm, sophisticated editorial palette, elegant spatial hierarchy, restrained use of Carrot Orange (`#FF7A2F`), warm paper canvas (`#FAF7F2`), and mature cultural tone.
2. **Hero / Opening Stage Synthesis: `phkQC` (Theatrical Spotlight Stage with Truth-Flip & 4-Facet ME Lens):**  
   - Selected as the preferred interactive opening component for Home, introducing a playful, witty "Truth-Flip" daily hook alongside structured ME profile facets.
3. **Editorial Home Boundary:**  
   - Authenticated Home (`/`) remains a curated editorial overview. Its mobile people preview may use a horizontal, touch-friendly carousel; it need not duplicate Discover's full deck interactions.
   - Avoid vertical stacks of multiple mobile candidate cards. Full individual profiles may scroll vertically.
   - `KZzuf` + `phkQC` is the selected direction, not final approval of existing Home code or a future synthesized implementation. Neither has evidence here for `FOUNDER_VISUAL_APPROVED`.

---

## FDR-2026-04: Commercial Architecture & Feature Classification Boundaries

- **Date:** 2026-10-28  
- **Status:** APPROVED & BINDING  
- **Applies to:** Monetization Strategy, Product Roadmap, Engineering Backlog  

### 1. Approved Commercial Architecture
1. **Free Social Core:**  
   Profile creation, daily energy reading, browsing people, interest tags, reciprocal connections, and unmetered human-to-human messaging remain **100% free**.
2. **Jester Plus (Subscription):**  
   Recurring subscription for advanced multi-person group synastry, deep-dive conflict navigation, transit notifications, and premium relationship guides.
3. **On-Demand Credits:**  
   Unit-metered credits reserved exclusively for costly generative AI synthesis and external LLM voice expansion.

### 2. Feature Classification Boundaries

| Feature | Classification | Technical / Repository Reality |
| :--- | :--- | :--- |
| **Free Core Social & Messaging** | **APPROVED / CORE** | Implemented in backend & frontend (Wave 1–4). |
| **Jester Plus & Credits Model** | **APPROVED ARCHITECTURE** | Architectural specification approved; pricing/payment ledger not yet built. |
| **JESTER Stars** | **CONCEPTUAL PROPOSAL (`PROPOSED`)** | Exploratory micro-currency idea; 0% schema, 0% backend, 0% frontend. Not approved for implementation. |
| **Paid Backtrack / Rewind** | **CONCEPTUAL PROPOSAL (`PROPOSED`)** | Exploratory paid deck feature; 0% schema or backend. Discovery does not permanently reject candidates in Wave 3. |
| **Personalized Discovery Ranking** | **SPECIFIED / NOT IMPLEMENTED** | Documented in `DISCOVERY_PREFERENCES_SYSTEM_V1_SPEC.md`; Wave 3 uses UUID cursor pagination. |
| **Server-Enforced 18+ Gate** | **APPROVED POLICY / LAUNCH GATE** | Binding public policy; server-side database constraint & verification gate deferred to Wave 5 release gates. |
