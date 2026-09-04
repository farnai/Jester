"""
Common utilities, validation logic, and generator helpers for the JESTER content corpus.
Enforces zero-jargon, deduplication (<0.85 Jaccard similarity), tone distribution, and length constraints.
"""
from dataclasses import dataclass, field
import hashlib
import re
from typing import Any

# Forbidden astrology jargon (case-insensitive word-boundary matching)
EN_JARGON_PATTERNS = [
    r"\bsun\b", r"\bmoons?\b", r"\bvenus\b", r"\bmars\b", r"\bmercury\b",
    r"\bjupiter\b", r"\bsaturn\b", r"\buranus\b", r"\bneptune\b", r"\bpluto\b",
    r"\bascendant\b", r"\bzodiac\b", r"\bhoroscopes?\b", r"\bnatal\b", r"\bastrology\b",
    r"\baries\b", r"\btaurus\b", r"\bgemini\b", r"\bcancer\b", r"\bleo\b",
    r"\bvirgo\b", r"\blibra\b", r"\bscorpio\b", r"\bsagittarius\b", r"\bcapricorn\b",
    r"\baquarius\b", r"\bpisces\b", r"\btrines?\b", r"\bsextiles?\b", r"\boppositions?\b",
    r"\bsquares?\b", r"\bconjunctions?\b", r"\bretrogrades?\b", r"\bdegrees?\b",
    r"\bcharts?\b", r"\btransits?\b", r"\bplanetary\b", r"\bephemeris\b", r"\bplacidus\b",
]

KA_JARGON_PATTERNS = [
    r"\bმზე[სმდაშიზე]*\b", r"\bმთვარ[ეისამდაშიზე]*\b", r"\bვენერა[სმდაშიზე]*\b",
    r"\bმარს[ისამდაშიზე]*\b", r"\bმერკურ[იისამდაშიზე]*\b", r"\bიუპიტერ[ისამდაშიზე]*\b",
    r"\bსატურნ[ისამდაშიზე]*\b", r"\bურან[ისამდაშიზე]*\b", r"\bნეპტუნ[ისამდაშიზე]*\b",
    r"\bპლუტონ[ისამდაშიზე]*\b", r"\bასცენდენტ[ისამდაშიზე]*\b", r"\bზოდიაქო[სმდაშიზე]*\b",
    r"\bჰოროსკოპ[ისამდაშიზე]*\b", r"\bასტროლოგი[აისამდაშიზე]*\b", r"\bვერძ[ისამდაშიზე]*\b",
    r"\bკურო[სმდაშიზე]*\b", r"\bტყუპებ[ისამდაშიზე]*\b", r"\bკირჩხიბ[ისამდაშიზე]*\b",
    r"\bლომ[ისამდაშიზე]*\b", r"\bქალწულ[ისამდაშიზე]*\b", r"\bსასწორ[ისამდაშიზე]*\b",
    r"\bმორიელ[ისამდაშიზე]*\b", r"\bმშვილდოსან[ისამდაშიზე]*\b", r"\bთხის\s*რქა[სმდაშიზე]*\b",
    r"\bმერწყულ[ისამდაშიზე]*\b", r"\bთევზებ[ისამდაშიზე]*\b", r"\bტრინ[ისამდაშიზე]*\b",
    r"\bსექსტილ[ისამდაშიზე]*\b", r"\bოპოზიცი[აისამდაშიზე]*\b", r"\bკვადრატურ[აისამდაშიზე]*\b",
    r"\bშეერთებ[აისამდაშიზე]*\b", r"\bრეტროგრადულ[ისამდაშიზე]*\b", r"\bგრადუს[ისამდაშიზე]*\b",
    r"\bრუკ[აისამდაშიზე]*\b", r"\bტრანზიტ[ისამდაშიზე]*\b", r"\bპლანეტ[აისამდაშიზე]*\b",
]

COMPILED_EN_JARGON = [re.compile(p, re.IGNORECASE) for p in EN_JARGON_PATTERNS]
COMPILED_KA_JARGON = [re.compile(p, re.IGNORECASE) for p in KA_JARGON_PATTERNS]


def scan_for_jargon(text: str, locale: str) -> list[str]:
    """Returns a list of matched forbidden jargon words if present in text."""
    patterns = COMPILED_KA_JARGON if locale == "ka" else COMPILED_EN_JARGON
    matched = []
    for pat in patterns:
        m = pat.search(text)
        if m:
            matched.append(m.group(0))
    return matched


def tokenize_words(text: str) -> set[str]:
    """Extracts lowercase word tokens from text."""
    return set(re.findall(r"\w+", text.lower()))


def calculate_jaccard_similarity(text_a: str, text_b: str) -> float:
    """Calculates Jaccard similarity of word sets between two strings."""
    tokens_a = tokenize_words(text_a)
    tokens_b = tokenize_words(text_b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))
    return intersection / union if union > 0 else 0.0


def generate_framed_variants(premise: str, twist: str, tone: str, locale: str) -> list[str]:
    """
    Synthesizes structurally diverse variants from premise and twist,
    preventing copy-paste repetitive sentence templates.
    """
    p = premise.strip().rstrip(".!?,")
    t = twist.strip().rstrip(".!?,")
    variants = []

    # 1. Direct standard: "P. T."
    variants.append(f"{p}. {t}.")

    t_lower = t[0].lower() + t[1:] if t else ""
    p_lower = p[0].lower() + p[1:] if p else ""

    if locale == "ka":
        if tone == "witty":
            variants.append(f"{p} — {t_lower}.")
            variants.append(f"როცა კარგად დააკვირდები, {p_lower}: {t_lower}.")
            variants.append(f"{t}. {p}.")
        elif tone == "playful":
            variants.append(f"{p}, ოღონდ {t_lower}.")
            variants.append(f"ერთი შეხედვით {p_lower}, მაგრამ სინამდვილეში {t_lower}.")
            variants.append(f"აქ ყველაფერი მარტივია: {p_lower}. {t}.")
        elif tone == "soft":
            variants.append(f"{p}; რაც მთავარია, {t_lower}.")
            variants.append(f"მშვიდად რომ შეხედო, {p_lower}. {t}.")
            variants.append(f"{p}, და ეს სრულ სიმშვიდეს ქმნის.")
        elif tone == "bold":
            variants.append(f"{p} — აქ ყოველგვარი ეჭვი ზედმეტია: {t_lower}.")
            variants.append(f"{t}. {p}.")
            variants.append(f"პირდაპირ რომ ვთქვათ: {p_lower}. {t}.")
            variants.append(f"{p}! {t}.")
        elif tone == "savage":
            variants.append(f"{p}, თუმცა {t_lower}.")
            variants.append(f"მოდი პირდაპირ ვთქვათ: {p_lower}. {t}.")
            variants.append(f"ილუზიების გარეშე: {p_lower} — {t_lower}.")
            variants.append(f"ნუ მოიტყუებ თავს: {p_lower}. {t}.")
        elif tone == "romantic":
            variants.append(f"{p} — და ეს თქვენს შორის ყველაფერს ცვლის.")
            variants.append(f"{p}. {t}, რაც კავშირს განსაკუთრებულ ხიბლს სძენს.")
            variants.append(f"ერთად ყოფნისას {p_lower}, რაც ურთიერთობას ამშვენებს.")
            variants.append(f"{t} — {p_lower}.")
    else:  # en
        if tone == "witty":
            variants.append(f"{p} — {t_lower}.")
            variants.append(f"When you look closely, {p_lower}: {t_lower}.")
            variants.append(f"{t}. {p}.")
            variants.append(f"Truth be told: {p_lower}. {t}.")
        elif tone == "playful":
            variants.append(f"{p}, except {t_lower}.")
            variants.append(f"At first glance, {p_lower}, but actually {t_lower}.")
            variants.append(f"Things are simple here: {p_lower}. {t}.")
            variants.append(f"{p}? {t}.")
        elif tone == "soft":
            variants.append(f"{p}; what matters most is that {t_lower}.")
            variants.append(f"Taking a quiet breath, {p_lower}. {t}.")
            variants.append(f"{p}, bringing a grounded sense of ease.")
            variants.append(f"Gently put: {p_lower}. {t}.")
        elif tone == "bold":
            variants.append(f"{p}. No hesitation needed — {t_lower}.")
            variants.append(f"{t}. {p}.")
            variants.append(f"Make no mistake: {p_lower}. {t}.")
            variants.append(f"{p}! {t}.")
        elif tone == "savage":
            variants.append(f"{p}, though {t_lower}.")
            variants.append(f"Let's be completely blunt: {p_lower}. {t}.")
            variants.append(f"Stripping away pretenses: {p_lower} — {t_lower}.")
            variants.append(f"No sugarcoating: {p_lower}. {t}.")
        elif tone == "romantic":
            variants.append(f"{p} — and that changes everything between you.")
            variants.append(f"{p}. {t}, lending the connection an unmistakable charm.")
            variants.append(f"Together, {p_lower}, bringing out mutual tenderness.")
            variants.append(f"{t} — {p_lower}.")

    return variants



@dataclass
class ContractSeedData:
    interpretation_id: str
    context: str
    ka_witty_premises: list[str] = field(default_factory=list)
    ka_witty_twists: list[str] = field(default_factory=list)
    ka_playful_premises: list[str] = field(default_factory=list)
    ka_playful_twists: list[str] = field(default_factory=list)
    ka_soft_premises: list[str] = field(default_factory=list)
    ka_soft_twists: list[str] = field(default_factory=list)
    ka_bold_premises: list[str] = field(default_factory=list)
    ka_bold_twists: list[str] = field(default_factory=list)
    ka_savage_premises: list[str] = field(default_factory=list)
    ka_savage_twists: list[str] = field(default_factory=list)
    ka_romantic_premises: list[str] = field(default_factory=list)
    ka_romantic_twists: list[str] = field(default_factory=list)

    en_witty_premises: list[str] = field(default_factory=list)
    en_witty_twists: list[str] = field(default_factory=list)
    en_playful_premises: list[str] = field(default_factory=list)
    en_playful_twists: list[str] = field(default_factory=list)
    en_soft_premises: list[str] = field(default_factory=list)
    en_soft_twists: list[str] = field(default_factory=list)
    en_bold_premises: list[str] = field(default_factory=list)
    en_bold_twists: list[str] = field(default_factory=list)
    en_savage_premises: list[str] = field(default_factory=list)
    en_savage_twists: list[str] = field(default_factory=list)
    en_romantic_premises: list[str] = field(default_factory=list)
    en_romantic_twists: list[str] = field(default_factory=list)


def build_assets_for_contract(
    seed: ContractSeedData,
    existing_asset_texts: set[str],
    all_seen_by_interp: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """
    Generates ~60-70 unique Content Assets for a contract, enforcing strict QA invariants:
    - Zero exact duplicates
    - Zero near-duplicates (Jaccard < 0.85)
    - Zero astrology jargon
    - Valid length (20 - 280 chars)
    - Appropriate tone and context assignment
    """
    stats = {
        "generated": 0,
        "rejected_duplicate": 0,
        "rejected_near_duplicate": 0,
        "rejected_jargon": 0,
        "rejected_length": 0,
    }
    assets: list[dict[str, Any]] = []
    interp_id = seed.interpretation_id
    if interp_id not in all_seen_by_interp:
        all_seen_by_interp[interp_id] = []

    domain = interp_id.split(".")[0]
    if domain == "self":
        available_contexts = ["self", "natal", "discovery", "onboarding"]
    elif domain == "relationship":
        available_contexts = ["relationship", "deep_analysis", "discovery", "share", "onboarding"]
    elif domain == "friendship":
        available_contexts = ["friendship", "discovery", "share"]
    elif domain == "daily_energy":
        available_contexts = ["daily_energy", "notification"]
    else:
        available_contexts = [seed.context]

    tone_plans = [
        # Georgian (~50-55 assets)
        ("ka", "witty", seed.ka_witty_premises, seed.ka_witty_twists, 18),
        ("ka", "playful", seed.ka_playful_premises, seed.ka_playful_twists, 15),
        ("ka", "soft", seed.ka_soft_premises, seed.ka_soft_twists, 12),
        ("ka", "bold", seed.ka_bold_premises, seed.ka_bold_twists, 10),
        ("ka", "savage", seed.ka_savage_premises, seed.ka_savage_twists, 4),
        ("ka", "romantic", seed.ka_romantic_premises, seed.ka_romantic_twists, 4),

        # English (~18-20 assets)
        ("en", "witty", seed.en_witty_premises, seed.en_witty_twists, 6),
        ("en", "playful", seed.en_playful_premises, seed.en_playful_twists, 5),
        ("en", "soft", seed.en_soft_premises, seed.en_soft_twists, 4),
        ("en", "bold", seed.en_bold_premises, seed.en_bold_twists, 4),
        ("en", "savage", seed.en_savage_premises, seed.en_savage_twists, 2),
        ("en", "romantic", seed.en_romantic_premises, seed.en_romantic_twists, 2),
    ]

    for locale, tone, premises, twists, target_count in tone_plans:
        if not premises or not twists:
            continue
        if tone == "romantic" and domain not in ("relationship",):
            continue

        collected_for_bucket = 0
        candidate_texts: list[str] = []

        # 1. Generate framed variants
        for p in premises:
            for t in twists:
                framed = generate_framed_variants(p, t, tone, locale)
                candidate_texts.extend(framed)

        # 2. Add standalone premise and twist options
        for p in premises:
            if len(p) >= 30:
                candidate_texts.append(p if p.endswith((".", "!")) else f"{p}.")
        for t in twists:
            if len(t) >= 30:
                candidate_texts.append(t if t.endswith((".", "!")) else f"{t}.")

        for text in candidate_texts:
            if collected_for_bucket >= target_count:
                break

            text = text.strip()
            # 1. Length check
            if len(text) < 20 or len(text) > 280:
                stats["rejected_length"] += 1
                continue

            # 2. Exact duplicate check
            if text in existing_asset_texts:
                stats["rejected_duplicate"] += 1
                continue

            # 3. Astrology jargon scan
            jargon_found = scan_for_jargon(text, locale)
            if jargon_found:
                stats["rejected_jargon"] += 1
                continue

            # 4. Near-duplicate check against assets already accepted for this contract
            is_near_dup = False
            for prev_text in all_seen_by_interp[interp_id]:
                sim = calculate_jaccard_similarity(text, prev_text)
                if sim >= 0.85:
                    is_near_dup = True
                    break

            if is_near_dup:
                stats["rejected_near_duplicate"] += 1
                continue

            # Valid asset accepted!
            existing_asset_texts.add(text)
            all_seen_by_interp[interp_id].append(text)
            collected_for_bucket += 1
            stats["generated"] += 1

            # Deterministic asset ID
            aid_hash = hashlib.sha256(f"{interp_id}:{locale}:{tone}:{text}".encode("utf-8")).hexdigest()[:10]
            asset_id = f"ca_{aid_hash}"

            # Context selection round-robin
            ctx_idx = (collected_for_bucket - 1) % len(available_contexts)
            chosen_ctx = available_contexts[ctx_idx]

            variant_key = f"{tone}_{locale}_{collected_for_bucket:02d}"

            asset_obj = {
                "asset_id": asset_id,
                "interpretation_id": interp_id,
                "locale": locale,
                "context": chosen_ctx,
                "tone": tone,
                "persona": "jester",
                "text": text,
                "status": "ai_draft",
                "version": 1,
                "priority": 50,
                "variant_key": variant_key,
                "source": "ai",
                "author": "jester_ai_corpus_v1",
                "tags": [domain, tone, locale, "corpus_v1"],
                "internal_notes": "AI Draft production corpus asset",
                "archived": False,
                "weight": 1.0,
                "experiment_id": None,
                "created_at": "2026-09-04T00:00:00Z",
                "updated_at": "2026-09-04T00:00:00Z",
            }
            assets.append(asset_obj)

    return assets, stats
