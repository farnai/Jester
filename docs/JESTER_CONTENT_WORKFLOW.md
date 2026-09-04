# JESTER V1 — Content & Copywriter Editorial Workflow

## Operational Guide: From AI Launch Drafts to Copywriter Excellence

---

## 🃏 1. Editorial Vision & Mission

In JESTER, copy is **the voice of the product**.
Astrology calculates deterministic relational physics; JESTER's voice explains what that means in sharp, observant, human prose.
> *"They show the match. JESTER explains the connection."*

The platform employs a phased content lifecycle designed to scale from launch to hundreds of thousands of active users without ever touching core astrology calculations:

```text
PHASE 1: Automated Launch Generation (AI Drafts)
      ↓ (Jargon-screened, contract-compliant baseline)
PHASE 2: Professional Copywriter Review & Tone Expansion
      ↓ (Bespoke Georgian & English copy, brand personality)
PHASE 3: Editorial Approval & Immediate Production Precedence
      ↓ (Approved assets instantly override AI drafts)
PHASE 4: Experimentation, A/B Testing & Seasonal Iteration
      ↓ (Variant keys, weights, continuous performance tuning)
```

---

## 🔄 2. The Four-Phase Content Lifecycle

### Phase 1 — Pre-Launch: Batch AI Generation
1. **Input Payload**: The batch generator consumes:
   - Interpretation Contract (ID, context, category, human meaning themes).
   - Voice Directives (tone, sarcasm, warmth, directness, sentence cap).
   - Locale (`ka`, `en`).
2. **Execution**: Generates 5–10 candidate assets per interpretation per tone.
3. **Automated Quality Gate**:
   - Programmatic astrology jargon scan (`assert_no_jargon`).
   - Sentence count limit validation ($\le 2$ sentences).
   - Length and character boundary checks.
4. **Initial State**: Assets are inserted with `status="ai_draft"` and `source="ai"`.

### Phase 2 — Copywriter Review & Refinement
Professional Georgian copywriters inspect semantic meaning and author high-craft prose:
1. Copywriters query the editorial catalog via `GET /v1/content/inventory` and `GET /v1/interpretations/{id}/assets`.
2. Copywriters craft variants across multiple tones:
   - **Witty**: Clever observation, modern cadence, subtle irony.
   - **Playful**: Light, entertaining social dynamic.
   - **Soft**: Emotionally supportive, validating, gentle.
   - **Bold**: High confidence, punchy, direct.
   - **Savage**: Sharp observational wit (never cruel).
   - **Romantic**: Genuine chemistry without cliché horoscope fluff.
3. Assets are submitted with `status="review"` or directly approved.

### Phase 3 — Production Approval & Promotion
When a copywriter approves an asset:
- The endpoint `POST /v1/content/assets/{asset_id}/approve` transitions `status="approved"`.
- The resolver's status hierarchy immediately promotes the approved asset above all `ai_draft` records.
- **Astrology calculations, scores, synastry matrices, and database tables remain 100% untouched.**

### Phase 4 — Experimentation & Seasonal Iteration
- Copywriters author experimental variants tagged with `experiment_id` and `variant_key="variant_b"`.
- Controlled A/B testing evaluates user engagement, share rates, and connection interactions.
- Winning variants are promoted to `status="winner"`.

---

## 🛠️ 3. Operational API Guide for Copywriters

All mutation operations require a JWT with role `copywriter`, `admin`, or `service_role`.

### 3.1 Audit Current Inventory
```bash
curl -X GET "https://api.jester.app/v1/content/inventory" \
     -H "Authorization: Bearer <COPYWRITER_JWT>"
```
Returns a list of all 30 interpretation contracts, showing total assets, approved assets, available tones, and locales.

### 3.2 View Assets for an Interpretation Contract
```bash
curl -X GET "https://api.jester.app/v1/interpretations/relationship.attraction.strong_chemistry.v1/assets" \
     -H "Authorization: Bearer <COPYWRITER_JWT>"
```

### 3.3 Create a New Copywriter Asset
```bash
curl -X POST "https://api.jester.app/v1/interpretations/relationship.attraction.strong_chemistry.v1/assets" \
     -H "Authorization: Bearer <COPYWRITER_JWT>" \
     -H "Content-Type: application/json" \
     -d '{
       "locale": "ka",
       "context": "relationship",
       "tone": "playful",
       "persona": "jester",
       "text": "თქვენ ორს ცალკე Wi-Fi არ გჭირდებათ — სიგნალი ისედაც პირველივე წამიდან იჭერს.",
       "status": "approved",
       "priority": 120,
       "variant_key": "variant_playful_1",
       "tags": ["chemistry", "wifi_metaphor"],
       "internal_notes": "Signature brand copy for launch campaign."
     }'
```
Response: `201 Created` with the newly assigned stable `asset_id`.

### 3.4 Update an Existing Asset
```bash
curl -X PATCH "https://api.jester.app/v1/content/assets/ca_rel_chem_001_ka_witty_a" \
     -H "Authorization: Bearer <COPYWRITER_JWT>" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "აქ მიზიდულობას ზედმეტი ახსნა ნამდვილად არ სჭირდება.",
       "tone": "witty",
       "priority": 150
     }'
```

### 3.5 Approve an Asset
```bash
curl -X POST "https://api.jester.app/v1/content/assets/ca_rel_chem_001_ka_witty_a/approve" \
     -H "Authorization: Bearer <COPYWRITER_JWT>"
```

### 3.6 Archive a Retired Asset
```bash
curl -X POST "https://api.jester.app/v1/content/assets/ca_rel_chem_001_ka_witty_old/archive" \
     -H "Authorization: Bearer <COPYWRITER_JWT>"
```
Archived assets are permanently suppressed from resolver selection.

---

## ✍️ 4. Editorial Guidelines & Quality Checklists

Every copywriter asset must satisfy the following strict editorial standards:

### ✅ Epistemic Modesty & Safety Checklist
- [ ] **No Absolute Predictions**: Never write *"You will marry each other"* or *"This will fall apart."*
- [ ] **No Mind Reading**: Never claim certainty about what the other person thinks or secretly feels.
- [ ] **No Accusations**: Never accuse either party of malicious intent, infidelity, or toxic traits.
- [ ] **No Medical / Diagnostic Terms**: Do not use clinical psychology jargon (*narcissist, bipolar, trauma bond*).
- [ ] **Dynamic Focus**: Frame every insight as a relational dynamic or energetic contrast, not a static destiny.

### 🚫 Forbidden Astrology Jargon (Programmatically Enforced)
Neither English nor Georgian assets may contain any of the following terms:

| English Forbidden Terms | Georgian Forbidden Terms |
| :--- | :--- |
| `synastry`, `transit`, `orb` | `სინასტრია`, `ტრანზიტი`, `ორბი` |
| `conjunction`, `trine`, `sextile` | `შეერთება`, `ტრინი`, `სექსტილი` |
| `opposition`, `square`, `aspect` | `ოპოზიცია`, `კვადრატი`, `ასპექტი` |
| `ascendant`, `midheaven`, `house` | `ასცენდენტი`, `მედიუმ ცელი`, `სახლი` |

### 📏 Brevity & Punch Rules
1. **Sentence Limit**: Maximum 2 sentences per insight.
2. **Punchline Placement**: Deliver the core insight or humorous twist in the second sentence.
3. **Punctuation**: Clean Georgian typography (em dash `—`, quotation marks `„ “` or modern standard quotes).
4. **Emoji Policy**: Avoid emoji spam. Use emojis sparingly only if designated for share cards.
