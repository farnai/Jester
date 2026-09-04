"""
Forensic audit script for JESTER Georgian Content Corpus (3,894 assets).
Evaluates lexical diversity, template recurrence, tone distinction,
semantic fidelity, shareability, onboarding hooks, and Jester voice quality.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

CORPUS_PATH = Path("backend/app/interpretation/data/content_corpus.json")

BANNED_JARGON = [
    "ზოდიაქო", "ჰოროსკოპი", "ასცენდენტი", "პლანეტა", "ტრანზიტი",
    "ასპექტი", "სახლი", "ნატალური", "სინასტრია", "რუკა",
    "მზე ვერძში", "მთვარე", "მარსი", "ვენერა", "იუპიტერი", "სატურნი",
    "ურანი", "ნეპტუნი", "პლუტონი", "ოპოზიცია", "კვადრატურა", "სექსტილი", "ტრიგონი"
]

GENERIC_HOROSCOPE_CLICHES = [
    "დღეს წარმატებას", "ბედი გაგიღიმებს", "ვარსკვლავები", "გელოდებათ წარმატება",
    "დღეს შეხვდებით", "წარმატებული დღე", "მოერიდეთ კონფლიქტს", "ყველაფერი კარგად იქნება",
    "იღბალი თქვენს მხარესაა", "დღეს კარგი დღეა", "გაგიმართლებთ"
]

METAPHOR_KEYWORDS = {
    "ჭადრაკი / სტრატეგია": ["ჭადრაკ", "სვლა", "ფიგურ", "დაფა", "სტრატეგ"],
    "რადარი / სიგნალი": ["რადარ", "სიგნალ", "ტალღა", "სიხშირე", "ანტენა"],
    "სარკე / ანარეკლი": ["სარკე", "ანარეკლ"],
    "პინგ-პონგი / თამაში": ["პინგ-პონგ", "ჩოგბურთ", "ბურთი", "თამაში"],
    "ავტომობილი / მართვა": ["საჭე", "პედლ", "მუხრუჭ", "სიჩქარე", "მოძრაობ"],
    "თეატრი / სცენა": ["სცენა", "მაყურებელ", "როლი", "თეატრ", "ფარდა"],
    "ფილტრი / ნიღაბი": ["ფილტრ", "ნიღაბ", "ჯავშან", "ფარი"],
    "ნავიგაცია / რუკა / კომპასი": ["კომპას", "გზამკვლევ", "მარშრუტ", "ორიენტირ"],
    "ცეცხლი / ნაპერწკალი": ["ნაპერწკალ", "ცეცხლ", "ალი", "აფეთქებ"],
    "წყნარი ნავსაყუდელი": ["ნავსაყუდელ", "სიმყუდროვე", "ჩაი", "თავშესაფარ"],
}

ROMANTIC_MARKERS = [
    r"\bსიყვარულ", r"\bშეყვარებულ", r"\bკოცნ", r"\bრომანტიკ", r"\bვნებ(ა|ით|ის|ას|იან|ებ)?\b", r"\bსატრფო"
]

def tokenize(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s\u10D0-\u10FA-]", " ", text)
    return [w.strip() for w in clean.split() if w.strip()]

def evaluate_asset(asset: dict) -> dict:
    text = asset["text"]
    context = asset["context"]
    tone = asset["tone"]
    interp_id = asset["interpretation_id"]
    tokens = tokenize(text)
    lower_text = text.lower()

    # 1. Jargon & Horoscope Scan
    jargon_hits = [j for j in BANNED_JARGON if j in lower_text]
    horoscope_hits = [h for h in GENERIC_HOROSCOPE_CLICHES if h in lower_text]

    # 2. Romantic leakage in non-relational contexts
    romantic_leak = False
    if context in ("friendship", "self", "natal", "daily_energy"):
        if any(re.search(rm, lower_text) for rm in ROMANTIC_MARKERS) or tone == "romantic":
            romantic_leak = True

    # 3. Scoring Dimensions (0-5)
    # A. Georgian Naturalness
    nat_score = 4.6
    if len(tokens) < 5:
        nat_score -= 1.5
    elif len(tokens) > 35:
        nat_score -= 0.8
    if "არის" in tokens and tokens.count("არის") > 2:
        nat_score -= 0.5

    # B. Jester Voice & Wit
    voice_score = 4.0
    if " — " in text or " – " in text or "—" in text:
        voice_score += 0.5
    if "?" in text:
        voice_score += 0.2
    if any(k in lower_text for k in ["მაგრამ", "თუმცა", "ხოლო", "ოღონდ", "სანამ"]):
        voice_score += 0.3
    voice_score = min(5.0, voice_score)

    # C. Observational Specificity
    spec_score = 4.0
    if any(k in lower_text for k in ["როცა", "ოთახში", "საუბარში", "დროს", "წამში", "ზუსტად", "პირველივე"]):
        spec_score += 0.4
    if any(k in lower_text for k in ["ძალიან კარგი", "საინტერესო ადამიანი", "მშვენიერი"]):
        spec_score -= 1.0
    spec_score = min(5.0, max(1.0, spec_score))

    # D. Non-Generic Quality
    generic_score = 5.0
    if horoscope_hits:
        generic_score -= 3.0
    if jargon_hits:
        generic_score -= 4.0
    if any(k in lower_text for k in ["ყოველთვის წარმატებული", "ბედნიერი იქნები"]):
        generic_score -= 2.0

    # E. Tone Fit
    tone_score = 4.3
    if tone == "witty" and ("—" in text or "მაგრამ" in text or "ოღონდ" in text):
        tone_score += 0.4
    elif tone == "playful" and ("!" in text or "ხუმრობ" in lower_text or "თამაში" in lower_text or "?" in text):
        tone_score += 0.4
    elif tone == "savage" and any(k in lower_text for k in ["მეტოქე", "ილუზია", "შეცდომა", "პირდაპირ", "დაუნდობლ", "სიმართლე", "ტყუილ"]):
        tone_score += 0.5
    elif tone == "soft" and any(k in lower_text for k in ["სიმშვიდე", "სივრცე", "ჩუმად", "ნაზ", "უსიტყვოდ", "სითბო"]):
        tone_score += 0.4
    elif tone == "bold" and any(k in lower_text for k in ["პირველი", "გადაწყვეტილ", "დაუყოვნებლივ", "პირდაპირ", "სიჩქარე"]):
        tone_score += 0.4
    elif tone == "romantic" and any(k in lower_text for k in ["მიზიდულობ", "მაგნეტიზმ", "მზერა", "სიახლოვე"]):
        tone_score += 0.4
    tone_score = min(5.0, tone_score)

    # F. Context Fit
    context_score = 4.5
    if romantic_leak:
        context_score -= 3.0
    if context == "daily_energy" and ("ჩვენ" in lower_text or "ერთმანეთ" in lower_text):
        context_score -= 2.0
    if context == "friendship" and ("სიყვარულ" in lower_text or "ვნებ" in lower_text):
        context_score -= 3.0

    # G. Semantic Fidelity
    sem_score = 4.5
    if jargon_hits:
        sem_score -= 2.0

    # H. Curiosity
    curiosity_score = 4.0
    if "ხომ" in lower_text or "თითქოს" in lower_text or "მაგრამ" in lower_text or "?" in text:
        curiosity_score += 0.5
    curiosity_score = min(5.0, curiosity_score)

    # I. Memorability & Shareability
    share_score = 3.8
    if 8 <= len(tokens) <= 22 and ("—" in text or "?" in text):
        share_score += 0.7
    if tone in ("witty", "savage", "playful") and context in ("share", "discovery", "onboarding"):
        share_score += 0.3
    share_score = min(5.0, share_score)

    # Composite Overall Score
    overall = (
        nat_score * 0.15 +
        voice_score * 0.15 +
        spec_score * 0.10 +
        generic_score * 0.15 +
        tone_score * 0.10 +
        context_score * 0.10 +
        sem_score * 0.10 +
        curiosity_score * 0.05 +
        share_score * 0.10
    )

    # Classification
    if jargon_hits or horoscope_hits or romantic_leak or overall < 2.8:
        grade = "D"  # REJECT
    elif overall < 3.6:
        grade = "C"  # REWRITE
    elif overall < 4.2:
        grade = "B"  # MINOR REVISION
    else:
        grade = "A"  # KEEP

    return {
        "asset_id": asset["asset_id"],
        "interpretation_id": interp_id,
        "context": context,
        "tone": tone,
        "text": text,
        "tokens": tokens,
        "char_len": len(text),
        "word_len": len(tokens),
        "nat_score": round(nat_score, 2),
        "voice_score": round(voice_score, 2),
        "spec_score": round(spec_score, 2),
        "generic_score": round(generic_score, 2),
        "tone_score": round(tone_score, 2),
        "context_score": round(context_score, 2),
        "sem_score": round(sem_score, 2),
        "curiosity_score": round(curiosity_score, 2),
        "share_score": round(share_score, 2),
        "overall": round(overall, 2),
        "grade": grade,
        "jargon_hits": jargon_hits,
        "horoscope_hits": horoscope_hits,
        "romantic_leak": romantic_leak,
    }

def main():
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    ka_assets = [a for a in corpus if a["locale"] == "ka"]
    en_assets = [a for a in corpus if a["locale"] == "en"]

    print(f"Total Corpus: {len(corpus)}")
    print(f"Active Georgian (ka): {len(ka_assets)}")
    print(f"Future English (en): {len(en_assets)}")

    evaluations = [evaluate_asset(a) for a in ka_assets]

    # Grades breakdown
    grades = Counter(e["grade"] for e in evaluations)
    print("\n--- GRADE DISTRIBUTION ---")
    for g in ["A", "B", "C", "D"]:
        count = grades[g]
        pct = (count / len(evaluations)) * 100
        print(f"Grade {g}: {count} ({pct:.1f}%)")

    # Average scores
    dims = ["nat_score", "voice_score", "spec_score", "generic_score", "tone_score", "context_score", "sem_score", "curiosity_score", "share_score", "overall"]
    avg_scores = {d: sum(e[d] for e in evaluations) / len(evaluations) for d in dims}
    print("\n--- AVERAGE SCORES ---")
    for d, s in avg_scores.items():
        print(f"{d:18s}: {s:.2f} / 5.00")

    # Openings & Templates analysis
    openings_1 = Counter()
    openings_2 = Counter()
    openings_3 = Counter()
    bigrams = Counter()
    trigrams = Counter()

    for e in evaluations:
        toks = e["tokens"]
        if len(toks) >= 1:
            openings_1[toks[0]] += 1
        if len(toks) >= 2:
            openings_2[" ".join(toks[:2])] += 1
            for i in range(len(toks) - 1):
                bigrams[" ".join(toks[i:i+2])] += 1
        if len(toks) >= 3:
            openings_3[" ".join(toks[:3])] += 1
            for i in range(len(toks) - 2):
                trigrams[" ".join(toks[i:i+3])] += 1

    print("\n--- TOP 20 1-WORD OPENINGS ---")
    for w, c in openings_1.most_common(20):
        print(f"{w:20s}: {c} ({(c/len(evaluations))*100:.1f}%)")

    print("\n--- TOP 20 2-WORD OPENINGS ---")
    for w, c in openings_2.most_common(20):
        print(f"{w:30s}: {c} ({(c/len(evaluations))*100:.1f}%)")

    print("\n--- TOP 20 3-WORD OPENINGS ---")
    for w, c in openings_3.most_common(20):
        print(f"{w:40s}: {c}")

    print("\n--- TOP 25 RECURRING TRIGRAMS ---")
    for w, c in trigrams.most_common(25):
        print(f"{w:40s}: {c}")

    # Metaphor detection
    metaphor_counts = Counter()
    for e in evaluations:
        text = e["text"].lower()
        for cat, kw_list in METAPHOR_KEYWORDS.items():
            if any(kw in text for kw in kw_list):
                metaphor_counts[cat] += 1

    print("\n--- METAPHOR CLUSTERS ---")
    for m, c in metaphor_counts.most_common():
        print(f"{m:30s}: {c} ({(c/len(evaluations))*100:.1f}%)")

    # Tone breakdown
    tones = Counter(e["tone"] for e in evaluations)
    print("\n--- TONE BREAKDOWN ---")
    for t, c in tones.most_common():
        t_evals = [e for e in evaluations if e["tone"] == t]
        avg_ov = sum(e["overall"] for e in t_evals) / len(t_evals)
        print(f"{t:12s}: {c:4d} assets | Avg Score: {avg_ov:.2f}")

    # Context breakdown
    contexts = Counter(e["context"] for e in evaluations)
    print("\n--- CONTEXT BREAKDOWN ---")
    for ctx, c in contexts.most_common():
        c_evals = [e for e in evaluations if e["context"] == ctx]
        avg_ov = sum(e["overall"] for e in c_evals) / len(c_evals)
        print(f"{ctx:15s}: {c:4d} assets | Avg Score: {avg_ov:.2f}")

    # Policy violations check
    jargon_assets = [e for e in evaluations if e["jargon_hits"]]
    horoscope_assets = [e for e in evaluations if e["horoscope_hits"]]
    leak_assets = [e for e in evaluations if e["romantic_leak"]]

    print(f"\nJargon violations: {len(jargon_assets)}")
    print(f"Horoscope cliché violations: {len(horoscope_assets)}")
    print(f"Romantic leaks in non-relational: {len(leak_assets)}")

    d_evals = [e for e in evaluations if e["grade"] == "D"]
    print(f"\nTotal Grade D items: {len(d_evals)}")
    for d in d_evals[:10]:
        print(f"  Asset ID: {d['asset_id']}, Interp: {d['interpretation_id']}, Context: {d['context']}, Tone: {d['tone']}")
        print(f"    Text: {d['text']}")
        print(f"    Jargon: {d['jargon_hits']}, Horoscope: {d['horoscope_hits']}, Romantic leak: {d['romantic_leak']}, Overall: {d['overall']}")

    out_path = Path("scratch_audit_results.json")

    # Filter and sort lists
    sorted_evals = sorted(evaluations, key=lambda x: -x["overall"])

    top_100_overall = sorted_evals[:100]
    top_50_onboarding = [e for e in sorted_evals if e["context"] == "onboarding"][:50]
    top_100_discovery = [e for e in sorted_evals if e["context"] == "discovery"][:100]
    top_100_relationship = [e for e in sorted_evals if e["context"] == "relationship"][:100]
    top_50_friendship = [e for e in sorted_evals if e["context"] == "friendship"][:50]
    top_50_share = [e for e in sorted_evals if e["context"] == "share"][:50]

    # Rewrite candidates: Grade C or lowest overall scores or flagged items
    rewrite_candidates = sorted([e for e in evaluations if e["grade"] in ("C", "D", "B")], key=lambda x: x["overall"])[:50]

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_ka": len(ka_assets),
                "total_en": len(en_assets),
                "grades": dict(grades),
                "avg_scores": avg_scores,
                "openings_2": openings_2.most_common(50),
                "trigrams": trigrams.most_common(50),
                "metaphors": dict(metaphor_counts),
            },
            "top_100_overall": top_100_overall,
            "top_50_onboarding": top_50_onboarding,
            "top_100_discovery": top_100_discovery,
            "top_100_relationship": top_100_relationship,
            "top_50_friendship": top_50_friendship,
            "top_50_share": top_50_share,
            "top_50_rewrites": rewrite_candidates,
            "evaluations": evaluations
        }, f, ensure_ascii=False, indent=2)
    print(f"\nDetailed evaluation saved to {out_path}")

if __name__ == "__main__":
    main()
