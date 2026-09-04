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
            variants.append(f"{p}. შეხედე მეორე მხრიდან: {t_lower}.")
            variants.append(f"{t}. თანაც {p_lower}.")
            variants.append(f"როცა ფიქრობ, რომ {p_lower}, აღმოჩნდება: {t_lower}.")
            variants.append(f"{p}. შედეგი? {t}.")
            variants.append(f"{p}, რაც საბოლოოდ ასე სრულდება: {t_lower}.")
            variants.append(f"წარმოიდგინე სიტუაცია: {p_lower}. ახლა დაამატე ეს: {t_lower}.")
            variants.append(f"{p}. ირონია იმაშია, რომ {t_lower}.")
            variants.append(f"{t}. არადა თავიდან {p_lower}.")
            variants.append(f"{p}... და მერე უკვირთ, რატომ {t_lower}.")
            variants.append(f"ჯერ {p_lower}, მერე კი ირკვევა, რომ {t_lower}.")
            variants.append(f"{p}. მოკლედ რომ ვთქვათ: {t_lower}.")
            variants.append(f"{p} — თუმცა მეორე მხარეს {t_lower}.")
            variants.append(f"{t} — და ამას წინ უძღვის: {p_lower}.")
        elif tone == "playful":
            variants.append(f"{p}, ოღონდ {t_lower}.")
            variants.append(f"{p}! თან გაითვალისწინე: {t_lower}.")
            variants.append(f"როგორც ჩანს, {p_lower}. თუმცა მოიცადე — {t_lower}.")
            variants.append(f"{p}. წესი ნომერი ერთი: {t_lower}.")
            variants.append(f"{t}. და ამას მოჰყვება: {p_lower}.")
            variants.append(f"გარედან თითქოს {p_lower}, შიგნით კი {t_lower}.")
            variants.append(f"{p}? პასუხი მარტივია: {t_lower}.")
            variants.append(f"არ იდარდო: {p_lower}. მთავარი სირთულე ისაა, რომ {t_lower}.")
            variants.append(f"{p} — და სანამ ამას გაიაზრებ, {t_lower}.")
            variants.append(f"{p}! ოღონდ მცირე დეტალით: {t_lower}.")
            variants.append(f"{t} — აი ასე მარტივად, როცა {p_lower}.")
        elif tone == "soft":
            variants.append(f"{p}. ამ დროს ყველაზე მეტად საჭიროა: {t_lower}.")
            variants.append(f"მშვიდი დაკვირვებით: {p_lower}. რაც მთავარია, {t_lower}.")
            variants.append(f"{p}; ეს ბუნებრივი პროცესია, რადგან {t_lower}.")
            variants.append(f"{t}. თანდათანობით ირკვევა: {p_lower}.")
            variants.append(f"{p}. მთავარია, დროულად დაინახო: {t_lower}.")
            variants.append(f"{p} — სიჩქარის გარეშე: {t_lower}.")
            variants.append(f"თუ კარგად დაფიქრდები, {p_lower}. თუმცა {t_lower}.")
            variants.append(f"{t} — სიმშვიდის შენარჩუნებით, როცა {p_lower}.")
        elif tone == "bold":
            variants.append(f"{p}! აქ ეჭვიც არავის ეპარება: {t_lower}.")
            variants.append(f"ფაქტი ერთია: {p_lower}. და ამას ვერაფერი შეცვლის: {t_lower}.")
            variants.append(f"{p}. პირდაპირ და დაუფარავად — {t_lower}.")
            variants.append(f"{t}! იმიტომ, რომ {p_lower}.")
            variants.append(f"{p}; დათმობაზე წასვლას არავინ აპირებს: {t_lower}.")
            variants.append(f"თამამად შეიძლება ითქვას: {p_lower}. თანაც {t_lower}.")
            variants.append(f"{p} — არავითარი კომპრომისი: {t_lower}.")
            variants.append(f"{t}! ზუსტად იქ, სადაც {p_lower}.")
        elif tone == "savage":
            variants.append(f"{p}. ნუ მოიტყუებ თავს: {t_lower}.")
            variants.append(f"{p}. ამ ყველაფერს ერთი უსიამოვნო სახელი აქვს: {t_lower}.")
            variants.append(f"{t}. სანამ ამას მიხვდები, მანამდე {p_lower}.")
            variants.append(f"{p}, თუმცა ყველამ მშვენივრად იცის: {t_lower}.")
            variants.append(f"შენი თავდაცვა მარტივია: {p_lower}. უხერხული სიმართლე კი ისაა, რომ {t_lower}.")
            variants.append(f"{p}. კომიკურია, მაგრამ {t_lower}.")
            variants.append(f"{p} — ილუზიების გარეშე: {t_lower}.")
            variants.append(f"{t} — და ამას ვერანაირი თავის მართლება ვერ უშველის, როცა {p_lower}.")
        elif tone == "romantic":
            variants.append(f"{p} — სწორედ ეს ქმნის განსაკუთრებულ მიზიდულობას: {t_lower}.")
            variants.append(f"{p}. ამ ორს შორის ყველაფერი იცვლება, რადგან {t_lower}.")
            variants.append(f"{t}. სიახლოვე იწყება იქ, სადაც {p_lower}.")
            variants.append(f"ერთმანეთის გვერდით {p_lower}, ოღონდ {t_lower}.")
            variants.append(f"{p}. და ეს კავშირი ცოცხლდება მაშინ, როცა {t_lower}.")
            variants.append(f"{t} — განსაკუთრებული ქიმია იგრძნობა, რადგან {p_lower}.")
    else:  # en
        if tone == "witty":
            variants.append(f"{p} — {t_lower}.")
            variants.append(f"Looking from another angle: {p_lower}, yet {t_lower}.")
            variants.append(f"{t}. Meanwhile, {p_lower}.")
            variants.append(f"When you assume {p_lower}, it turns out {t_lower}.")
            variants.append(f"{p}. The real irony? {t}.")
            variants.append(f"{p}, which inevitably leads to: {t_lower}.")
            variants.append(f"{t} — right after {p_lower}.")
        elif tone == "playful":
            variants.append(f"{p}, except {t_lower}.")
            variants.append(f"Keep in mind: {p_lower}, while {t_lower}.")
            variants.append(f"{p}. Rule number one: {t_lower}.")
            variants.append(f"{t}. And immediately following that: {p_lower}.")
            variants.append(f"On the outside, {p_lower}, but on the inside: {t_lower}.")
            variants.append(f"{p}? Well: {t_lower}.")
        elif tone == "soft":
            variants.append(f"{p}; what matters most is that {t_lower}.")
            variants.append(f"With quiet clarity, {p_lower}. In the end, {t_lower}.")
            variants.append(f"{p}. Give it space: {t_lower}.")
            variants.append(f"{t}. Gradually, {p_lower}.")
        elif tone == "bold":
            variants.append(f"{p}. No hesitation needed — {t_lower}.")
            variants.append(f"The baseline reality: {p_lower}. Unapologetically, {t_lower}.")
            variants.append(f"{t}! Because {p_lower}.")
            variants.append(f"{p}; zero compromises: {t_lower}.")
        elif tone == "savage":
            variants.append(f"{p}, though {t_lower}.")
            variants.append(f"Drop the pretenses: {p_lower}. The reality is {t_lower}.")
            variants.append(f"{t}. Before you realize it: {p_lower}.")
            variants.append(f"{p} — and no amount of rationalization changes that {t_lower}.")
        elif tone == "romantic":
            variants.append(f"{p} — and that changes everything: {t_lower}.")
            variants.append(f"{p}. The spark ignites when {t_lower}.")
            variants.append(f"Side by side, {p_lower}, bringing out {t_lower}.")
            variants.append(f"{t} — the pull between them is undeniable when {p_lower}.")

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
