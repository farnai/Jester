# JESTER — Founder Decision Records (FDR)

**Document Type:** Canonical Product & Architectural Decision Records  
**Authority Level:** Level 1.5 (Directly under `AGENTS.md` and Founder Directives)  
**Status:** ACTIVE & BINDING  
**Last Updated:** 2026-10-28  

---

## Overview

This document records binding product, strategic, UX, and architectural decisions established directly by the JESTER Founder. These records supersede older historical working papers, early exploratory prohibitions, and outdated assumptions where conflicts exist.

---

## FDR-2026-01: Photo-First Human Discovery & Touch-Native Swipe Interaction Policy

- **Date:** 2026-10-28  
- **Status:** APPROVED & BINDING  
- **Supersedes:** Early "Anti-Swipe Mandate" (`docs/JESTER_PRODUCT_FOUNDATION.md` v1.0, `docs/JESTER_DESIGN_EXPLORATION.md` §4.1)  
- **Applies to:** Social Discovery (`/discover`), Mobile UX, Product Marketing, Brand Positioning  

### 1. Context & Motivation
Early working papers in the repository contained an overreaching "Anti-Swipe Mandate" that categorically banned swipe gestures and sought to minimize profile photography in an attempt to distance JESTER from dating-app superficiality. In practice, this created an unresolvable contradiction with Wave 3's implemented mobile discovery deck (`frontend/src/modules/discover/DiscoverSwipeCard.tsx`) and artificially moralized against natural human behavior.

Visual appearance, personal aesthetic presentation, and photographic first impressions are natural, legitimate, and universal entry points into discovering other human beings. JESTER must embrace and celebrate this reality rather than suppress it.

### 2. Decision & Core Principles

1. **Photo-First Human Discovery:**  
   High-quality, candid, expressive photography serves as the primary visual gateway into discovering someone's presence, personality, and vibe.
2. **The Four-Stage Human Discovery Funnel:**  
   Discovery is structured as a progressive psychological journey:
   $$\mathbf{Visual\ Attraction} \longrightarrow \mathbf{Personal\ Curiosity} \longrightarrow \mathbf{Deeper\ Understanding} \longrightarrow \mathbf{Meaningful\ Connection}$$
   - **Stage 1: Visual Attraction:** Natural appreciation of human presence, style, and photographic aesthetic.
   - **Stage 2: Personal Curiosity:** Expressive bio statements, lifestyle cadence, values, and self-expression prompts.
   - **Stage 3: Deeper Understanding:** Deterministic Synastry signals, communication dynamics, friction points, and relational chemistry.
   - **Stage 4: Meaningful Connection:** An intentional connection invitation initiated with explicit bilateral consent.
3. **Touch-Native Mobile Discovery Deck:**  
   On mobile devices, candidates are browsed via an intuitive card deck (`DiscoverSwipeCard.tsx`):
   - **Swipe Left (or ArrowLeft / Next button):** Advances locally to the next candidate (skip/pass) without writing negative rejection telemetry to the database.
   - **Swipe Right (or ArrowRight / Connect button):** Initiates a connection request.
4. **Intentional Connection Consent Safeguard:**  
   A right-swipe **never** triggers an instant, unprompted match or single-flick connection. It opens a focused **confirmation modal/drawer**, requiring an explicit tap on "მოწვევის გაგზავნა" (Send Invitation). Escape or "ჯერ არა" (Not Now) cancels cleanly without sending data.
5. **Decoupled Gesture Architecture:**  
   Candidate navigation is completely separated from photo browsing:
   - Horizontal tapping or scrubbing within a candidate's profile steps through their photo gallery (`photos[]`) without moving the candidate card.
   - Horizontal dragging across the threshold ($>65\text{px}$) navigates candidate cards.
   - Vertical scrolling explores deep profile details, lifestyle facets, and WHY insights.
6. **Multi-Intent Dignity:**  
   JESTER is a **People Discovery & Relationship Intelligence** platform, not a dating-only app. It supports friendship, creative collaboration, activity partnerships, intellectual dialogue, and intentional romance with equal platform dignity. Celebrating photography does not make JESTER a hookup app.
7. **Absolute Separation of Appearance from Computation:**  
   JESTER never assigns numeric scores to physical attractiveness, nor does it deduce astrological or psychological compatibility from photographs. Photography is for human perception; deterministic calculations are for relational chemistry.

---

## FDR-2026-02: Photo Framing & Geometric Hierarchy

- **Date:** 2026-10-28  
- **Status:** APPROVED & BINDING  
- **Applies to:** Design Tokens, Mobile & Desktop UI Components, Visual Studio Canvas  

### 1. Context & Motivation
Explorations in Visual Studio introduced vaulted arch masks (`border-radius: 9999px 9999px 0 0`) across both avatars and large full-bleed candidate photography. On mobile screens, exaggerated arch geometry distorts natural photo crops, cuts off faces and posture, and introduces unnecessary visual kitsch.

### 2. Decision & Framing Rules

1. **Large Candidate & Lifestyle Photography:**  
   - Must use **natural photographic proportions** (e.g. 4:5 portrait or 3:4).
   - Must use **restrained, modern rounded corners** (`border-radius: 20px` to `24px` / `rounded-2xl` to `rounded-3xl`).
   - Exaggerated arch masks are strictly prohibited on full-bleed mobile candidate cards and hero photography.
2. **Small Portraits, Avatars & Cameo Badges:**  
   - Distinctive arch framing (`arch-portrait`), circular cameo rings, and subtle brand apertures are authorized and encouraged for avatars, circular shared-interest seals, and thumbnail cards.
3. **Responsive Cropping:**  
   - Images must use `object-fit: cover` with face-safe focal points to preserve human dignity across all viewport widths.

---

## FDR-2026-03: Visual Exploration Synthesis (KZzuf Architecture + phkQC Stage)

- **Date:** 2026-10-28  
- **Status:** APPROVED (Direction for Visual Studio & Future Implementation Waves)  
- **Applies to:** Authenticated Home, AppShell, Future Screen Modernization  

### 1. Context & Motivation
Visual Studio Exploration 02 produced eight distinct art-directed directions. An independent visual critique evaluated them against brand tokens, Georgian typography, spatial rhythm, and responsive viability.

### 2. Decision & Directional Selection

1. **Foundational Visual Architecture: `KZzuf` (Warm Paper Salon / Personal Court):**  
   - Selected for its warm, sophisticated editorial palette, elegant spatial hierarchy, restrained use of Carrot Orange (`#FF7A2F`), warm paper canvas (`#FAF7F2`), and mature cultural tone.
2. **Hero / Opening Stage Synthesis: `phkQC` (Theatrical Spotlight Stage with Truth-Flip & 4-Facet ME Lens):**  
   - Selected as the preferred interactive opening component for Home, introducing a playful, witty "Truth-Flip" daily hook alongside structured ME profile facets.
3. **Editorial Home Boundary:**  
   - Authenticated Home (`/`) remains a curated, vertical editorial overview (Today's Energy, ME Lens, Discovery Previews, Circle Moments).
   - Swipeable deck navigation belongs specifically to Social Discovery (`/discover`). Home does not feature binary discard swiping.

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
