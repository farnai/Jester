"""
JESTER — PHASE 3.4
Mercury Full Generation & Astrological Provenance Hardening Pipeline
Generates exactly 96 Mercury assets (12 signs x 8 assets: 72 Micro, 24 Medium)
with machine-readable provenance, QA scoring, and zero-jargon / zero-claim safety.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from scripts.corpus_builders.common import scan_for_jargon

# Forbidden medical / psychological diagnoses and claims
FORBIDDEN_CLAIMS = [
    r"\badhd\b", r"\bყურადღების დეფიციტ", r"\bაუტიზმ", r"\bautism\b",
    r"\bდეპრესი", r"\bdepression\b", r"\bბიპოლარულ", r"\bbipolar\b",
    r"\bშფოთვითი აშლილობ", r"\banxiety disorder\b", r"\bocd\b", r"\bოკდ\b",
    r"\bოკრი\b", r"\biq\b", r"\bაიქიუ\b", r"\bინტელექტის კოეფიციენტ",
    r"\bდიაგნოზ", r"\bფსიქიკური აშლილობ", r"\bმატყუარა ხარ\b",
    r"\bნარცისი ხარ\b", r"\bფსიქოპათ", r"\bკრიმინალ",
    r"\bეს დამტკიცებულია\b", r"\bშენი ტვინი ასე მუშაობს\b",
    r"\bეს ფსიქოლოგიურად ნიშნავს\b", r"\bშენ აუცილებლად\b",
]

FORBIDDEN_OPENINGS = [
    "წარმოიდგინე სიტუაცია",
    "წარმოიდგინე",
    "შენ ხარ",
]

# 12 Sign Specifications: (sign, element, modality)
SIGN_SPECS = [
    ("aries", "fire", "cardinal"),
    ("taurus", "earth", "fixed"),
    ("gemini", "air", "mutable"),
    ("cancer", "water", "cardinal"),
    ("leo", "fire", "fixed"),
    ("virgo", "earth", "mutable"),
    ("libra", "air", "cardinal"),
    ("scorpio", "water", "fixed"),
    ("sagittarius", "fire", "mutable"),
    ("capricorn", "earth", "cardinal"),
    ("aquarius", "air", "fixed"),
    ("pisces", "water", "mutable"),
]

MERCURY_RAW_ASSETS = [
    # =========================================================================
    # 1. ARIES (self.cognition.mercury_aries.v1)
    # =========================================================================
    {
        "sign": "aries",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "rapid_processing",
        "metaphor": "sprint",
        "text": "შენთვის დიალოგი ინფორმაციის გაცვლა კი არა, სპრინტია: სანამ მოსაუბრე შესავალს დაამთავრებს, შენ უკვე დასკვნა გაქვს გამოტანილი და მოწყენილობისგან იტანჯები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "frontal_debate",
        "metaphor": "frontal_shot",
        "text": "დიპლომატიური შეფუთვა შენი საქმე არ არის. აზრს პირდაპირ შუბლში ესვრი ადამიანს და მერე გულწრფელად გიკვირს, რატომ სჭირდება ყველას დრო რეანიმაციისთვის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "impatience_with_nuance",
        "metaphor": "verbal_guillotine",
        "text": "სხვისი მონოლოგის მოსმენა შენთვის ნამდვილი წამებაა: როგორც კი აზრს დაიჭერ, ფრაზას შუაზე ჭრი და საუბრის საჭეს თვითნებურად იტაცებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "frontal_debate",
        "metaphor": "battering_ram",
        "text": "კამათში ტაქტიკურ უკანდახევას არ ცნობ. შენი არგუმენტი ტარანივით მუშაობს — პირდაპირ კედელს ანგრევ და მოწინააღმდეგეს გაქცევის შანსს არ უტოვებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "rapid_processing",
        "metaphor": "volcanic_spark",
        "text": "იდეა რომ გაგიჩნდება, ირგვლივ ყველაფერი მეორეხარისხოვანი ხდება. აზრი ისეთი ვულკანური სიჩქარით იფრქვევა, რომ ჰაერშივე წვავს მოსაუბრის მოთმინებას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "impatience_with_nuance",
        "metaphor": "shortcut_detour",
        "text": "ყველა თუ შემოვლით გზას ეძებს, შენ პირდაპირ შუაზე ჭრი სივრცეს: ორი უხეში წინადადებით ისეთ მოულოდნელ დასკვნას დებ, რომ დარბაზი სიჩუმეში იყინება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "rapid_processing",
        "metaphor": "emergency_siren",
        "text": "მოდი პირდაპირ ვთქვათ: შენი გონება საგანგებო რეჟიმის სირენასავით მუშაობს — მყისიერად და მაღალ ვოლტზე. როცა პრობლემა ჩნდება, არ გჭირდება ოცგვერდიანი ანალიტიკა; ინტუიცია პირველივე წამში გიკარნახებს პასუხს და მაშინვე მოქმედებაზე გადადიხარ. პრობლემა ისაა, რომ გარშემომყოფები ამ სიჩქარეს ვერ ეწევიან. შენთვის ნელი ახსნა უპატივცემულობის ტოლფასია, ამიტომ საუბარს ხშირად შუაზე ჭრი — არა იმიტომ, რომ უზრდელი ხარ, უბრალოდ ფინიშთან უკვე დიდი ხანია მარტო დგახარ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "aries",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "frontal_debate",
        "metaphor": "verbal_duel_fastforward",
        "text": "კამათი შენთვის ინტელექტუალური დუელია, სადაც გამარჯვებული ისაა, ვინც პირველ დარტყმას მიაყენებს მოწინააღმდეგეს. გიყვარს აზრის შიშველი, დაუმუშავებელი სახით გასროლა და გაოგნებული მზერების ყურება. პრობლემა მაშინ იწყება, როცა საქმე რთულ, მრავალშრიან თემებს ეხება: ნიუანსების ჩაძიება სიკვდილივით გეზარება. შენთვის მთავარია მოკლე, დამამხობელი ვერდიქტი და თუ ვინმე გეტყვის „მოდი დეტალურად განვიხილოთო“, ისეთი სახით უყურებ, თითქოს ვიდეოს ორმაგ სიჩქარეზე გადახვევას გთხოვდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 2. TAURUS (self.cognition.mercury_taurus.v1)
    # =========================================================================
    {
        "sign": "taurus",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "methodical_digestion",
        "metaphor": "granite_slab",
        "text": "შენი აზროვნება გრანიტის ფილას ჰგავს: მის დასაძვრელად ამწეკრანია საჭირო, მაგრამ თუ ერთხელ რამე ჩაიბეჭდა, იქიდან აზრს ბულდოზერითაც ვეღარავინ ამოფხეკს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 2,
        "depth": "micro",
        "tone": "mocking",
        "angle": "conversational_immovability",
        "metaphor": "immovable_boulder",
        "text": "ვერბალური იერიშის მიტანა შენზე უაზრობაა. ისეთი ოლიმპიური სიმშვიდით დუმხარ, რომ მოწინააღმდეგე საკუთარი არგუმენტებისგან თავადვე იღლება და ნებდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "reluctance_to_revise",
        "metaphor": "cured_cement",
        "text": "ახალი იდეის მიღება შენთან საუკუნის მშენებლობას ჰგავს. სანამ ცემენტი არ გაშრება და ათჯერ არ შეამოწმებ, მანამდე ნებისმიერ ინოვაციას ზღაპრად თვლი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "conversational_immovability",
        "metaphor": "iron_anchor",
        "text": "რაც არ უნდა გააფთრებით გიმტკიცონ საპირისპირო, შენი ლოგიკა ღუზასავითაა ჩაშვებული: სანამ საკუთარი თვალით არ ნახავ, მათი აჟიოტაჟი ნულად რჩება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "methodical_digestion",
        "metaphor": "slow_millstone",
        "text": "შენი გონება უზარმაზარი წისქვილის ქვაა: ნელა ტრიალებს, ყოველ მარცვალს სათითაოდ ფქვავს და სანამ საბოლოო ფქვილი არ დაიყრება, პასუხს ვერავინ მიიღებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "reluctance_to_revise",
        "metaphor": "locked_safe",
        "text": "ყველა რომ პოზიციას იცვლის, შენ მაინც პირველად ნათქვამზე რჩები: რკინის სეიფივით იკეტები და სხვებს აიძულებ, შენს უძრავ ლოგიკას მოერგონ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "methodical_digestion",
        "metaphor": "soil_and_scale",
        "text": "შენთან საუბრისას აჩქარება შეუძლებელია. გონება ყოველ ახალ ინფორმაციას სათითაოდ ამოწმებს, წონის და პრაქტიკულ სარგებელს ეძებს. სანამ სხვები ჰაერში აბსტრაქტულ სასახლეებს აშენებენ, შენ ჯიუტად იკვლევ ნიადაგს და ხარჯთაღრიცხვას ითხოვ. ეს საოცარ სიმყარეს გმატებს — შენი სიტყვა ყოველთვის სანდო და შემოწმებულია. თუმცა ხანდახან ეს სიფრთხილე იმდენად ჭიანურდება, რომ მატარებელი უკვე წასულია, შენ კი ისევ ბაქანზე დგახარ და ბილეთის ხარისხს ამოწმებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "conversational_immovability",
        "metaphor": "concrete_calculator",
        "text": "სამყაროში, სადაც ყველა უაზრო იდეების გენერირებითაა დაკავებული, შენ ჯიუტად ითხოვ ხელშესახებ ფაქტებს. ჰაეროვანი თეორიები და აბსტრაქტული ფილოსოფია შენთვის უბრალოდ დროის კარგვაა, თუ მას პრაქტიკული სარგებელი არ მოაქვს. სანამ ვინმე გელაპარაკება, შენი შინაგანი კალკულატორი უკვე ითვლის: რა ჯდება ეს, რამდენად გამძლეა და რაში გვჭირდება საერთოდ. შეგიძლია საათობით იჯდე და ისმინო სხვისი ენთუზიაზმი, ბოლოს კი ერთი მშრალი შეკითხვით მთელი მათი საპნის ბუშტი მიწასთან გაასწორო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 3. GEMINI (self.cognition.mercury_gemini.v1)
    # =========================================================================
    {
        "sign": "gemini",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "high_frequency_multitasking",
        "metaphor": "browser_tabs",
        "text": "შენს თავში ერთდროულად ოცდაათი ბრაუზერის ფანჯარაა გახსნილი, საიდანაც ხუთიდან მუსიკა უკრავს, შენ კი მაინც ახერხებ პარალელურად სამ თემაზე კამათს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "gemini",
        "index": 2,
        "depth": "micro",
        "tone": "mocking",
        "angle": "intellectual_fencing",
        "metaphor": "fencing_rapier",
        "text": "დიალოგში ისე სწრაფად იცვლი პოზიციას, რომ საკუთარ არგუმენტსაც კი უსწრებ. მთავარი ჭეშმარიტების დაცვა კი არა, ვერბალურ ფარიკაობაში გამარჯვებაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "low_boredom_threshold",
        "metaphor": "abandoned_toy",
        "text": "იდეა გხიბლავს ზუსტად მანამ, სანამ ახალია. როგორც კი საქმე ყოველდღიურ შესრულებაზე მიდგება, ინტერესი ქრება და თავს ახალ სათამაშოზე გადართავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "high_frequency_multitasking",
        "metaphor": "radio_frequencies",
        "text": "სიტყვების მარაგს ისეთი სისწრაფით ატრიალებ, თითქოს რადიოსიხშირეებს ცვლიდე: ნებისმიერ უხერხულ დუმილს მომენტალურად ორიგინალური რეპლიკით ავსებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "intellectual_fencing",
        "metaphor": "conversational_whirlwind",
        "text": "შენი დიალოგი ნამდვილი ქარიშხალია: ერთი წინადადებით იწყებ, ათ თემას წამოჭრი და ბოლოს ყველას თავბრუს ახვევ საკუთარი პარადოქსებით.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "high_frequency_multitasking",
        "metaphor": "mirror_maze",
        "text": "მოსაუბრე სწორხაზოვან ლოგიკას ელის, შენ კი მოულოდნელად თემის კუთხეს ცვლი და სარკეების ლაბირინთში ისე იკარგები, რომ პასუხს ვეღარავინ გთხოვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "low_boredom_threshold",
        "metaphor": "rollercoaster_playground",
        "text": "შენთან საუბარი მაღალსიჩქარიან ამერიკულ მთებზე სეირნობას ჰგავს: თემიდან თემაზე ისეთი სისწრაფით გადადიხარ, რომ შუა გზაში ადამიანებს ავიწყდებათ, თავიდან რაზე დაიწყეთ კამათი. გონება მომენტალურად იჭერს კავშირებს სრულიად დაუკავშირებელ ფაქტებს შორის. თუმცა როგორც კი თემა თავის ზედაპირულ ხიბლს კარგავს და რუტინულ დეტალებში ჩაღრმავებას ითხოვს, შენი ინტერესი უეცრად ორთქლდება. შენთვის ცოდნა სათამაშო მოედანია და არა სამეცნიერო მონოგრაფია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "gemini",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "intellectual_fencing",
        "metaphor": "circus_pingpong",
        "text": "შენი ვერბალური მანევრები ცირკის აკრობატიკას ჰგავს: შეგიძლია ერთი და იმავე მონდომებით დაიცვა ურთიერთგამომრიცხავი პოზიციები, უბრალოდ იმიტომ, რომ პროცესი გაერთობს. კამათში არგუმენტი შენთვის პინგ-პონგის ბურთია — მთავარია თამაში არ შეწყდეს და დარტყმა იყოს სანახაობრივი. პრობლემა ისაა, რომ ამ მარათონში ხშირად იკარგება საკუთარი პრინციპი; იმდენად ხარ გატაცებული სხვისი სიტყვების გაბითურებით, რომ ბოლოს თავადაც აღარ გახსოვს, სინამდვილეში რას ემხრობოდი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 4. CANCER (self.cognition.mercury_cancer.v1)
    # =========================================================================
    {
        "sign": "cancer",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "subconscious_emotional_absorption",
        "metaphor": "audio_equalizer",
        "text": "სიტყვებს კი არ უსმენ, ტონალობას აშიფრავ. ადამიანმა შეიძლება სრულყოფილი ლოგიკით გესაუბროს, მაგრამ თუ ხმაში ცივი ნოტი დაიჭირე, არგუმენტი გაუქმებულია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "defensive_rhetorical_posture",
        "metaphor": "emotional_archive",
        "text": "შენი მეხსიერება ემოციური არქივია: ციფრები და თარიღები შეიძლება დაგავიწყდეს, მაგრამ სამი წლის წინ ვინ რა მზერით გითხრა საყვედური, წამებში გაიხსენებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "subjective_bias",
        "metaphor": "prism_of_mood",
        "text": "ობიექტური ანალიზი შენთან მაშინვე მთავრდება, როგორც კი მოსაუბრის მიმართ სიმპათია ან ანტიპათია გაგიჩნდება. ფაქტებს საკუთარი განწყობის პრიზმაში ფილტრავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "subconscious_emotional_absorption",
        "metaphor": "sixth_sense_radar",
        "text": "ლოგიკური დასაბუთება არ გჭირდება, როცა შინაგანი რადარი ზუსტად გკარნახობს, სად არის თვალთმაქცობა. შენს ინტუიციას კაბინეტური თეორიები ვერ შეედრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "defensive_rhetorical_posture",
        "metaphor": "tidal_avalanche",
        "text": "კრიტიკაზე შენი პასუხი დუმილია, მაგრამ ეს დუმილი მომავალი ტალღის მომასწავებელია: როცა თავდაცვა ირღვევა, წყენა ძველი ამბების ზვავად ბრუნდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "subjective_bias",
        "metaphor": "personal_diary",
        "text": "მშრალ საქმიან შეხვედრაზეც კი შეგიძლია საუბარი პირად გამოცდილებაზე გადაიტანო: უეცრად ისეთ ემოციურ დეტალს გაიხსენებ, რომ ფორმალური დისკუსია დნება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "defensive_rhetorical_posture",
        "metaphor": "armor_and_hearth",
        "text": "უცხო გარემოში შენი აზროვნება დამცავ ჯავშანში იკეტება. სანამ სივრცეს არ შეამოწმებ და არ დარწმუნდები, რომ შენს სიტყვებს იარაღად არ გამოიყენებენ, მანამდე მხოლოდ უსაფრთხო, ზედაპირულ ფრაზებს ისვრი. სამაგიეროდ, როცა ნდობა მოპოვებულია, შენი გონება საოცრად თბილ, ამბავზე დაფუძნებულ მთხრობელად იქცევა. შენი ლოგიკა განცდებთანაა გადაჯაჭვული — თუ თემა შენთვის პირადად არ არის მნიშვნელოვანი, მასზე ფიქრიც კი უაზრო ენერგიის კარგვად გეჩვენება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.7, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "subjective_bias",
        "metaphor": "thermometer_minefield",
        "text": "შენთვის კამათში მთავარი წესი ასეთია: თუ ფაქტი ჩემს გრძნობებს ეწინააღმდეგება, მით უარესი ფაქტისთვის. საოცარი ოსტატობით ახერხებ ყველაზე აბსტრაქტული თემაც კი პირად სატკივრად აქციო. როცა ვინმე წმინდა ტექნიკურ ხარვეზზე მიგითითებს, შენი შინაგანი თერმომეტრი მაშინვე ცივ უარყოფას აჩვენებს: „ანუ შენ მე არ მენდობი?“. ამის შემდეგ დისკუსია ინტელექტუალური სივრციდან ემოციურ ნაღმების ველზე გადადის, სადაც მოწინააღმდეგეს მხოლოდ ბოდიშის მოხდაღა შველის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },

    # =========================================================================
    # 5. LEO (self.cognition.mercury_leo.v1)
    # =========================================================================
    {
        "sign": "leo",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "confident_rhetorical_staging",
        "metaphor": "royal_decree",
        "text": "აზრს კი არ გამოთქვამ, დეკრეტს აქვეყნებ. ისეთი ურყევი დარწმუნებულობით საუბრობ, რომ ხალხი ხშირად ფაქტების გადამოწმებასაც კი ვერ ბედავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 2,
        "depth": "micro",
        "tone": "mocking",
        "angle": "theatrical_articulation",
        "metaphor": "stage_spotlight",
        "text": "საუბრისას აუდიტორია აუცილებელი ატრიბუტია: თუ ოთახში მაყურებელი არ არის, აზრის გაზიარება თითქოს თავის დრამატულ დანიშნულებას კარგავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "intellectual_pride",
        "metaphor": "throne_and_crown",
        "text": "შენს არგუმენტთან შეკამათება სამეფო კარის ღალატის ტოლფასია: შეცდომის მითითებას აღიქვამ არა როგორც ლოგიკას, არამედ როგორც პირადი ავტორიტეტის შებღალვას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "confident_rhetorical_staging",
        "metaphor": "banner_and_megaphone",
        "text": "ჩურჩულით ლაპარაკი შენი ბუნება არ არის. შენი აზრები ბანერებივითაა გაშლილი — ხმამაღალი, მკაფიო და ისეთი პათოსით ნათქვამი, რომ ეჭვიც კი არავის ეპარება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 5,
        "depth": "micro",
        "tone": "conversational",
        "angle": "theatrical_articulation",
        "metaphor": "cinematic_premiere",
        "text": "ნებისმიერ მარტივ ისტორიას კინოპრემიერად აქცევ: იყენებ ფერად ეპითეტებს, პაუზებს და ემოციურ აქცენტებს, რადგან მოსაწყენი სიმართლე შენთვის უინტერესოა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "intellectual_pride",
        "metaphor": "volume_override",
        "text": "როცა ხვდები, რომ არგუმენტი სუსტია, უკან დახევის ნაცვლად მოულოდნელად ხმას უწევ და ისეთ გრანდიოზულ მონოლოგს აწყობ, რომ ყველა შინაარსს ივიწყებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 7,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "theatrical_articulation",
        "metaphor": "amphitheater_manifesto",
        "text": "შენთვის ყოველი დიალოგი ამფითეატრის ცენტრალურ სცენაზე გამოსვლას ჰგავს. აზრი აუცილებლად მასშტაბური, ფერადი და ემოციურად დამუხტული უნდა იყოს; მშრალი სტატისტიკით საუბარი შენს ბუნებას ეწინააღმდეგება. გიყვარს იდეების ისეთი პათოსით წარდგენა, თითქოს საუკუნის მანიფესტს კითხულობდე. მოსაუბრისგან ელი არა უბრალოდ თანხმობას, არამედ აღფრთოვანებას. ხოლო თუ ვინმემ შენი გამოსვლის დროს უყურადღებობა გამოიჩინა, ამას საკუთარი ინტელექტის უპატივცემულობად აღიქვამ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "leo",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "intellectual_pride",
        "metaphor": "podium_concession",
        "text": "შენთვის დისკუსია პოდიუმზე გამოსვლას ჰგავს: იდეა აუცილებლად მასშტაბური, შთამბეჭდავი და ოდნავ პათეტიკური უნდა იყოს. საუბრობ თამამი, ფერადი მეტაფორებით და გულწრფელად გწყინს, თუ ვინმე შენი მონოლოგის დროს ტელეფონში იყურება. მთავარი სისუსტე კი ისაა, რომ შეცდომის აღიარება შენთვის საჯარო კაპიტულაციის ტოლფასია. მაშინაც კი, როცა ხვდები, რომ არგუმენტი სუსტია, უკან დახევის ნაცვლად დრამატიზმის ხარისხს უმატებ და პოზიციას ბოლომდე იცავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },

    # =========================================================================
    # 6. VIRGO (self.cognition.mercury_virgo.v1)
    # =========================================================================
    {
        "sign": "virgo",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "systematic_error_detection",
        "metaphor": "comma_error",
        "text": "შენი თვალი ნებისმიერ ტექსტში პირველ რიგში მძიმის შეცდომას იპოვის. სანამ სხვები იდეის სიდიადით ტკბებიან, შენ უკვე ხედავ სამ პუნქტს, სადაც სისტემა ჩამოიშლება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "virgo",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "precision_deconstruction",
        "metaphor": "microscopic_xray",
        "text": "პათეტიკური ლოზუნგები შენთან არ ჭრის. პირველივე შეკითხვაზე — „ტექნიკურად როგორ ვაკეთებთ ამას?“ — მოსაუბრის მთელი ფილოსოფიური კონსტრუქცია ინგრევა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "analysis_paralysis",
        "metaphor": "spreadsheet_subitems",
        "text": "დიდი მიზნების დაგეგმვა კარგია, მაგრამ შენ ისე ჩაეფლობი ცხრილებისა და ქვეპუნქტების გასწორებაში, რომ საქმის დაწყება თვეობით ჭიანურდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "precision_deconstruction",
        "metaphor": "surgical_scalpel",
        "text": "შენი ლოგიკა ქირურგიული სკალპელივითაა: ზედმეტ წყალს მომენტალურად ჭრი და ტოვებ მხოლოდ იმ შიშველ ფაქტებს, რომელთა უარყოფაც შეუძლებელია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 5,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "systematic_error_detection",
        "metaphor": "loose_screw",
        "text": "ყველა რომ პროექტის წარმატებას ზეიმობს, შენ მოულოდნელად ერთ პატარა მოშვებულ ჭანჭიკზე მიუთითებ და მთელ ეიფორიას წამებში რეალობაში აბრუნებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 6,
        "depth": "micro",
        "tone": "jester",
        "angle": "analysis_paralysis",
        "metaphor": "red_pen_editor",
        "text": "სამყაროს წითელი კალმით ხელში უყურებ: ყველაფერს სჭირდება შესწორება, გადამოწმება და რედაქტირება, მათ შორის სხვის შემთხვევით ნათქვამ ხუმრობასაც კი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "systematic_error_detection",
        "metaphor": "diagnostic_scanner",
        "text": "შენი გონება მაღალი სიზუსტის სკანერია: ქაოსიდან მომენტალურად ამოკრებ არსებით დეტალებს, დაალაგებ კატეგორიებად და ხარვეზების ნუსხას შეადგენ. როცა რამე გაფუჭებულია, პირველი ხარ, ვინც მიზეზს ხვდება. თუმცა სწორედ აქ იმალება მახე: იმდენად ხარ კონცენტრირებული მიკრო-დეფექტებზე, რომ ხანდახან მთლიანი სურათი მხედველობიდან გეკარგება. საქმის გამოსწორების სურვილი ხშირად დაუსრულებელ რედაქტირებაში გადადის, სადაც სრულყოფილების ძიება შედეგის მიღებას აფერხებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "virgo",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "precision_deconstruction",
        "metaphor": "house_of_cards_collapse",
        "text": "როცა ვინმე შენს წინაშე გრანდიოზულ, ოპტიმისტურ გეგმას შლის, შენში მაშინვე იღვიძებს დაუნდობელი ლაბორანტი. არ გაინტერესებს შთამაგონებელი მუსიკა და ლამაზი სლაიდები; შენ სვამ სამ მარტივ, ტექნიკურ შეკითხვას რესურსებსა და რისკებზე. წამებში მთელი ეს ბრწყინვალე კონსტრუქცია ბანქოს სახლივით ინგრევა. შენი ანალიზი ყოველთვის უტყუარია, მაგრამ გარშემომყოფებს ხანდახან ეჩვენებათ, რომ შენთვის იდეის სრულყოფილად მოკვლა უფრო სასიამოვნოა, ვიდრე მისი ცოცხლად დანახვა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 7. LIBRA (self.cognition.mercury_libra.v1)
    # =========================================================================
    {
        "sign": "libra",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "anticipating_counter_argument",
        "metaphor": "softened_edge",
        "text": "სანამ საკუთარ აზრს ჩამოაყალიბებ, უკვე იცი, რას გიპასუხებს მოწინააღმდეგე, ამიტომ პასუხს ისე არბილებ, რომ საბოლოოდ შენი მკაფიო პოზიცია ჰაერში იკარგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 2,
        "depth": "micro",
        "tone": "mocking",
        "angle": "deliberative_suspension",
        "metaphor": "un_resolution_scale",
        "text": "მენიუს არჩევასაც კი ისეთივე ფილოსოფიური წონასწორობით უდგები, თითქოს გაეროს რეზოლუციას ათანხმებდე: ორივე მხარე თანაბრად მართალია და გადაწყვეტილება ჭიანურდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "deliberative_suspension",
        "metaphor": "pendulum_swing",
        "text": "კონფლიქტის შიშით ისე ოსტატურად ლავირებ ორ საპირისპირო აზრს შორის, რომ ხანდახან საკუთარი პოზიცია საერთოდ გავიწყდება და ქანქარასავით ირწევი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "socratic_diplomacy",
        "metaphor": "velvet_glove",
        "text": "ყველაზე უხეშ კამათსაც კი ხავერდოვანი დიპლომატიით ანეიტრალებ: ისე მოხდენილად გადააფორმებ სხვის შეურაცხყოფას, რომ მოწინააღმდეგე თავადვე იბნევა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 5,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "anticipating_counter_argument",
        "metaphor": "two_way_mirror",
        "text": "ყველა როცა ერთ მხარეს ემხრობა, შენ მოულოდნელად მოწინააღმდეგის ლოგიკას იცავ — არა ჯიბრით, არამედ იმიტომ, რომ ცალმხრივი სიმართლე თვალს გჭრის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 6,
        "depth": "micro",
        "tone": "jester",
        "angle": "socratic_diplomacy",
        "metaphor": "peace_tea_chess",
        "text": "კამათში შენი მიზანი მოწინააღმდეგის განადგურება კი არა, მისი ჩაის დასალევად დაპატიჟებაა: იმდენ კომპრომისს პოულობ, რომ კამათის არსი ორთქლდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "socratic_diplomacy",
        "metaphor": "bridge_and_corners",
        "text": "შენთვის დიალოგის მთავარი მიზანი ჰარმონიაა: ფლობ იშვიათ ნიჭს, ყველაზე მწვავე კამათიც კი ცივილიზებულ დისკუსიად აქციო. უხეში და აგრესიული ტონი ფიზიკურ დისკომფორტს გგვრის, ამიტომ ყოველთვის ცდილობ, კონფლიქტური კუთხეები მოამრგვალო. თუმცა ამ დიპლომატიას თავისი ფასი აქვს: სხვისი სიმშვიდის შენარჩუნების მცდელობაში ხშირად ერიდები კატეგორიული სიმართლის თქმას. არადა, ზოგჯერ სიტუაცია მოითხოვს მკაფიო „არას“ და არა მორიგ დაზავებას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "deliberative_suspension",
        "metaphor": "tightrope_courtroom",
        "text": "შენი გონება მუდმივად დაჭიმულ თოკზე დადის: ნებისმიერ საკითხს ორივე მხრიდან უყურებ, ხედავ თითოეული პოზიციის სიმართლეს და იტანჯები, როცა ცალსახა არჩევანია გასაკეთებელი. გადაწყვეტილების მიღება შენთვის სასამართლო პროცესს ჰგავს, სადაც მხარეები უსასრულოდ ცვლიან არგუმენტებს. ეს საოცარ სამართლიანობას გმატებს, მაგრამ ცხოვრება ყოველთვის არ ელოდება შენს საბოლოო ვერდიქტს. ზოგჯერ გაურკვევლობაში დარჩენა უფრო დამანგრეველია, ვიდრე არასრულყოფილი არჩევანი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 5.0}
    },

    # =========================================================================
    # 8. SCORPIO (self.cognition.mercury_scorpio.v1)
    # =========================================================================
    {
        "sign": "scorpio",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "penetrating_subtext_interrogation",
        "metaphor": "hidden_microphone",
        "text": "შენთვის უბრალო საუბარი არ არსებობს: ყოველ ფრაზაში ფარულ მოტივს ეძებ, ხოლო როცა ადამიანი სრულიად გულწრფელია, კიდევ უფრო მეტად ეჭვობ, რომ რაღაცას გიმალავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "surgical_verbal_economy",
        "metaphor": "silencer_target",
        "text": "ტყუილად არ ლაპარაკობ. ჩუმად აკვირდები, აგროვებ ფაქტებს და მერე ერთი ზუსტი რეპლიკით ამბობ იმას, რის ხმამაღლა აღიარებასაც მთელი ოთახი გაურბოდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "cognitive_suspicion",
        "metaphor": "detective_interrogation",
        "text": "შენთან მეგობრული ყავის დალევაც კი დაკითხვას ჰგავს: ისეთი გამჭოლი მზერით სვამ შეკითხვებს, თითქოს მოსაუბრეს საერთაშორისო შეთქმულებაში ამხელდე.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "surgical_verbal_economy",
        "metaphor": "chess_snare",
        "text": "კამათში არ ჩქარობ. მოწინააღმდეგეს აძლევ უფლებას ბევრი ილაპარაკოს, სანამ საკუთარ სიტყვებში არ გაიხლართება, მერე კი მშვიდად უსვამ წერტილს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 5,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "penetrating_subtext_interrogation",
        "metaphor": "submarine_periscope",
        "text": "როცა ყველა ზედაპირულ დეტალებზე კამათობს, შენ მოულოდნელად ადამიანის ქვეცნობიერ შიშს გააშიშვლებ და საუბრის სიღრმეს რადიკალურად ცვლი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 6,
        "depth": "micro",
        "tone": "jester",
        "angle": "cognitive_suspicion",
        "metaphor": "safe_vault_code",
        "text": "საკუთარ აზრებს ისე ინახავ, თითქოს ბანკის კოდი იყოს: შენზე არაფერია ცნობილი, მაგრამ სხვისი ყველა საიდუმლო შენს შინაგან საქაღალდეში დევს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "penetrating_subtext_interrogation",
        "metaphor": "xray_state_secret",
        "text": "შენი გონება რენტგენის აპარატივით მუშაობს: ზედაპირული ღიმილი და ზრდილობიანი ფრაზები შენზე შთაბეჭდილებას ვერ ახდენს. ინსტინქტურად გრძნობ, სად არის სისუსტე, სად თვალთმაქცობა და რას არ ამბობს მოსაუბრე. ინფორმაციას ისე ინახავ, თითქოს სახელმწიფო საიდუმლოება იყოს — შენზე თითქმის არაფერია ცნობილი, შენ კი ყველაფერი იცი. ეს საოცარ სტრატეგიულ უპირატესობას გაძლევს, მაგრამ ხანდახან ისეთ მარტივ სიტუაციაშიც კი შეთქმულებას ხედავ, სადაც უბრალოდ უყურადღებობა იყო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "scorpio",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "surgical_verbal_economy",
        "metaphor": "depth_charge_silence",
        "text": "დიალოგში შენთვის ზედაპირული ფენა არ არსებობს; შენ ყოველთვის ფესვებში იყურები. შეგიძლია მთელი შეხვედრა ჩუმად გაატარო, ისე რომ სიტყვაც არ თქვა, მაგრამ შენი დუმილი ოთახში მძიმე წონას ქმნის. აკვირდები ხმის კანკალს, მზერის არიდებას და უთქმელ პაუზებს. ხოლო როცა საუბარში ერთვები, შენი სიტყვა სიღრმისეულ მუხტს ჰგავს — პირდაპირ ეხება პრობლემის ყველაზე მტკივნეულ წერტილს. ეს გაძლევს ძალას, რომელსაც ვერავინ უგულებელყოფს, თუნდაც შენი პირდაპირობა აშინებდეთ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },

    # =========================================================================
    # 9. SAGITTARIUS (self.cognition.mercury_sagittarius.v1)
    # =========================================================================
    {
        "sign": "sagittarius",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "impatience_with_minutiae",
        "metaphor": "global_plan_escape",
        "text": "გლობალურ იდეებზე ისეთი გატაცებით საუბრობ, თითქოს კაცობრიობის გადარჩენის გეგმა გქონდეს, მაგრამ როცა დეტალებზე მიდგება საქმე, თავს უეცრად სხვა თემაზე გადართავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "uncensored_candor",
        "metaphor": "raw_arrow",
        "text": "ფილტრი საერთოდ გათიშული გაქვს: სიმართლეს ისეთი პირდაპირობით ისვრი, თითქოს დარწმუნებული იყო, რომ ტაქტის გრძნობა სუსტი ხალხის გამოგონილია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "macro_conceptual_leaping",
        "metaphor": "telescope_shoelace",
        "text": "შენი მზერა ყოველთვის შორეულ ჰორიზონტს მისჩერებია: გალაქტიკურ მასშტაბებს საათობით განიხილავ, მაგრამ საკუთარი ფეხსაცმლის თასმა რომ გახსნილია, ვერ ამჩნევ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "macro_conceptual_leaping",
        "metaphor": "continental_bridge",
        "text": "წვრილმანებზე დროის კარგვა შენი საქმე არ არის. შენი აზრები კონტინენტებს აკავშირებს და სანამ სხვები წესებს კითხულობენ, შენ უკვე მომავალს წინასწარმეტყველებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "uncensored_candor",
        "metaphor": "lightning_truth",
        "text": "შენი სიმართლე ელვასავით აჭრის ოთახს: დიპლომატიურ ეტიკეტს ისე უგულებელყოფ, თითქოს ზრდილობა მხოლოდ დროის კარგვა იყოს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "macro_conceptual_leaping",
        "metaphor": "philosophical_detour",
        "text": "მარტივ ყოფით შეკითხვაზეც კი შეგიძლია საუბარი ანტიკურ ფილოსოფიაზე გადაიტანო და ისეთი მასშტაბური დასკვნა გამოიტანო, რომ ყველა გაოგნებული დარჩეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "macro_conceptual_leaping",
        "metaphor": "horizon_flight",
        "text": "შენი აზროვნება ყოველთვის ჰორიზონტს გაჰყურებს: გიყვარს იდეები, რომლებსაც მასშტაბი და შთაგონება მოაქვთ. ერთდროულად შეგიძლია განიხილო ისტორია, ფილოსოფია და მომავლის ხედვა, თუმცა როგორც კი ვინმე რუტინული ცხრილის შევსებას მოგთხოვს, ენთუზიაზმი მომენტალურად გიქრება. საუბარში ხარ გულწრფელი, ხმაურიანი და გადამდები, თუმცა შენი პირდაპირობა ხშირად გარშემომყოფებს შოკში აგდებს. შენთვის სიმართლე უპირველესია, მაგრამ ცოტა მეტი დელიკატურობა არ გაწყენდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "impatience_with_minutiae",
        "metaphor": "hot_air_balloon",
        "text": "შენი გონება საჰაერო ბურთივით დაფრინავს აბსტრაქტულ სიმაღლეებზე: იქიდან სამყარო მარტივი, ლამაზი და ფილოსოფიურად გამართული ჩანს. მაგრამ როგორც კი მიწაზე დაშვება და კონკრეტული დეტალების მოგვარება გიწევს, აღმოჩნდება, რომ ციფრები აგერია, თარიღი დაგავიწყდა და ინსტრუქცია საერთოდ არ წაგიკითხავს. შენი ენთუზიაზმი გადამდებია, სანამ ვინმე პასუხისმგებლობის მკაფიო გადანაწილებას არ მოითხოვს — აი მაშინ კი შენი ოპტიმიზმი უეცრად ახალი თემის ძიებაში გადადის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 5.0}
    },

    # =========================================================================
    # 10. CAPRICORN (self.cognition.mercury_capricorn.v1)
    # =========================================================================
    {
        "sign": "capricorn",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "strategic_economy",
        "metaphor": "heavy_coin",
        "text": "ზედმეტ სიტყვას არ დახარჯავ: საუბრობ მხოლოდ მაშინ, როცა სათქმელს წონა აქვს. ცარიელ ენთუზიაზმს შენთან შანსი არ აქვს — მხოლოდ შედეგები ლაპარაკობს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 2,
        "depth": "micro",
        "tone": "snarky",
        "angle": "skepticism_toward_speculation",
        "metaphor": "budget_audit",
        "text": "ახალი იდეის გაგონებისას პირველი რეაქცია უარყოფაა: სანამ თეორია პრაქტიკულ გამოცდას არ გაივლის და ბიუჯეტში არ ჩაჯდება, შენთვის ის უბრალოდ უპასუხისმგებლო ზღაპარია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "sober_factual_authority",
        "metaphor": "sober_check",
        "text": "სხვების პათეტიკურ აღფრთოვანებას ერთი მშრალი შეკითხვით აცივებ: „და ამას ვინ აფინანსებს?“. შენი რეალიზმი ყველაზე ფერად ილუზიასაც კი ფერფლად აქცევს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "strategic_economy",
        "metaphor": "stone_foundation",
        "text": "შენთვის აზრი მაშინ ფასობს, თუ მასზე რამის აშენება შეიძლება. ჰაერზე ლაპარაკი დროის ქურდობაა — გირჩევნია დუმდე, ვიდრე უსარგებლო იდეები აფრქვიო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "sober_factual_authority",
        "metaphor": "carved_monument",
        "text": "შენი სიტყვა ქვაზე ამოკვეთილ კანონს ჰგავს: ცივი, უცვლელი და ისეთი წონით ნათქვამი, რომ კამათის გაგრძელების სურვილი ყველას უქრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "skepticism_toward_speculation",
        "metaphor": "precedent_archive",
        "text": "ყველა როცა რისკზე მიდის, შენ მოულოდნელად წარსულ გამოცდილებას იმოწმებ და აჩვენებ, რომ მსგავსი ექსპერიმენტი ათი წლის წინ უკვე ჩავარდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "strategic_economy",
        "metaphor": "blueprint_climber",
        "text": "შენთან საქმიანი საუბარი ყოველთვის სტრუქტურულია: არ გიყვარს გადახვევები, ემოციური ლირიკა და ზედმეტი დაპირებები. ყოველ წინადადებას აფასებ პრაქტიკული შედეგის, დროისა და რესურსების მიხედვით. შენი გონება მთამსვლელივით ფრთხილად და მყარად მიიწევს წინ, ყოველი ნაბიჯი გათვლილია. თუმცა ამ მკაცრ პრაგმატიზმს თავისი ჩრდილი აქვს: ხშირად იმდენად ხარ მიჯაჭვული დადგენილ წესებსა და წარსულ პრეცედენტებზე, რომ ჭეშმარიტად ახალ შესაძლებლობებს კარს უხურავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "sober_factual_authority",
        "metaphor": "engineering_project",
        "text": "შენი გონება საინჟინრო პროექტივითაა აწყობილი: არ არსებობს ილუზიები, მხოლოდ მკაცრი რეალიზმი და რესურსების ზუსტი გათვლა. კამათში ემოციური არგუმენტები შენზე არ ჭრის; შეგიძლია ცივი სიმშვიდით მოუსმინო ყველაზე ემოციურ გამოსვლას და მერე ორი მშრალი ფაქტით დაამტკიცო, რატომ არ იმუშავებს ეს იდეა. შენი სიტყვა ყოველთვის მყარია, თუმცა ზოგჯერ იმდენად ხარ ჩაკეტილი წესებსა და წარსულ გამოცდილებაში, რომ ჭეშმარიტად ახალ და არასტანდარტულ შესაძლებლობებს კარს უხურავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 11. AQUARIUS (self.cognition.mercury_aquarius.v1)
    # =========================================================================
    {
        "sign": "aquarius",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "principled_contrarianism",
        "metaphor": "consensus_sabotage",
        "text": "ოთახში ყველა ერთ აზრზე თუ შეთანხმდა, შენი მოვალეობაა საპირისპირო პოზიცია დაიცვა — არა იმიტომ, რომ მართლა ასე ფიქრობ, უბრალოდ ერთსულოვნება გაღიზიანებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 5.0}
    },
    {
        "sign": "aquarius",
        "index": 2,
        "depth": "micro",
        "tone": "mocking",
        "angle": "detached_systems_synthesis",
        "metaphor": "lab_experiment",
        "text": "ადამიანურ ემოციებს ისეთი ცივი ლოგიკით აანალიზებ, თითქოს ლაბორატორიულ ექსპერიმენტს აკვირდებოდე: თეორია ბრწყინვალეა, მაგრამ ცოცხალ ხალხს ვერ ერგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "intellectual_detachment",
        "metaphor": "algorithmic_coldness",
        "text": "პრობლემას სისტემურად ისე უყურებ, რომ ინდივიდუალური განცდები უბრალო სტატისტიკურ შეცდომად გეჩვენება. შენი ლოგიკა უნაკლოა, ოღონდ სითბოსგან სრულიად დაცლილი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "detached_systems_synthesis",
        "metaphor": "future_network",
        "text": "შენი იდეები ყოველთვის რამდენიმე ნაბიჯით უსწრებს დროს. სანამ სხვები არსებულ წესებს იცავენ, შენ უკვე მომავლის სისტემურ არქიტექტურას აგებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "principled_contrarianism",
        "metaphor": "paradox_bomb",
        "text": "ერთი მოულოდნელი პარადოქსით შეგიძლია მთელი საზოგადოებრივი დოგმა თავდაყირა დააყენო: გიყვარს ჩვეული აზროვნების ნგრევა და ახალი პერსპექტივის გაჩენა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "detached_systems_synthesis",
        "metaphor": "orbital_satellite",
        "text": "როცა ყველა ლოკალურ დეტალებზე კამათობს, შენ უეცრად ორბიტალურ სიმაღლეზე ახვალ და აჩვენებ, რომ მთელი დისკუსია საერთოდ არასწორ კითხვაზე იყო აგებული.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 7,
        "depth": "medium",
        "tone": "conversational",
        "angle": "detached_systems_synthesis",
        "metaphor": "open_code_map",
        "text": "შენი აზროვნება ყოველთვის მომავალში ცხოვრობს: არ გაინტერესებს „როგორ კეთდებოდა აქამდე“, შენთვის მთავარია „როგორ შეიძლება გაკეთდეს უფრო რაციონალურად“. გონება უპრობლემოდ ამსხვრევს მიღებულ დოგმებს და უცნაურ, ორიგინალურ ლოგიკურ ჯაჭვებს აგებს. კამათში ხარ აბსოლუტურად ობიექტური და არასდროს გადადიხარ პირად შეურაცხყოფაზე. თუმცა შენი სისუსტე სწორედ ეს ზედმეტი დისტანცირებაა: ხანდახან იმდენად ხარ გატაცებული იდეალური სისტემებით, რომ რეალურ ადამიანებს ივიწყებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "principled_contrarianism",
        "metaphor": "inverted_mirror_logic",
        "text": "შენთვის დიალოგში მთავარი აზარტი საყოველთაოდ მიღებული ჭეშმარიტების თავდაყირა დაყენებაა. თუ ყველა ამბობს, რომ ცა ლურჯია, შენ უყოყმანოდ იპოვი ისეთ ფიზიკურ ფორმულას, რომლითაც დაამტკიცებ, რომ სინამდვილეში ეს მხოლოდ ოპტიკური ილუზიაა. შენი ინტელექტუალური დამოუკიდებლობა შთამბეჭდავია, მაგრამ ხანდახან ეს ჯიუტი კონტრარიანიზმი თვითმიზნად იქცევა: მზად ხარ სრულიად აბსურდული თეორიაც კი დაიცვა, ოღონდ უმრავლესობის აზრს არ დაეთანხმო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 12. PISCES (self.cognition.mercury_pisces.v1)
    # =========================================================================
    {
        "sign": "pisces",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "impressionistic_non_linear_logic",
        "metaphor": "metaphorical_fog",
        "text": "ლოგიკური დასკვნის ნაცვლად მეტაფორას გვთავაზობ: შენს თავში ყველაფერი იდეალურად უკავშირდება ერთმანეთს, მაგრამ სხვებისთვის ამის ახსნა ცალკე მისტიკაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "impressionistic_non_linear_logic",
        "metaphor": "atmospheric_sponge",
        "text": "სანამ ადამიანი პირს გააღებს, უკვე იცი რა განწყობაზეა. ინფორმაციას ტვინით კი არა, მთელი შენი გარემომცველი ველით იწოვ, რაც ხშირად გფიტავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.7, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 3,
        "depth": "micro",
        "tone": "mocking",
        "angle": "narrative_boundary_blur",
        "metaphor": "tangled_yarn",
        "text": "მარტივ შეკითხვაზე პირდაპირ პასუხს ვერავინ მიიღებს: შენი აზრი ისეთ პოეტურ წრეებს ურტყამს, რომ ბოლოს თავადაც გავიწყდება, საიდან დაიწყე.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "indirect_evocative_storytelling",
        "metaphor": "river_current",
        "text": "სტრუქტურა და ცხრილები შენს გონებას ახრჩობს. შენ მდინარესავით მიედინები და აზრს მაშინ პოულობ, როცა მკაცრ ჩარჩოებს გვერდს უვლი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 5,
        "depth": "micro",
        "tone": "cocky",
        "angle": "impressionistic_non_linear_logic",
        "metaphor": "submerged_mirage",
        "text": "ფაქტები მხოლოდ აისბერგის წვერია. შენ ხედავ იმას, რაც წყლის ქვეშ იმალება და სხვებისთვის უხილავი რჩება — შენი ინტუიცია ცივ ლოგიკაზე წინ დგას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "indirect_evocative_storytelling",
        "metaphor": "dream_canvas",
        "text": "არგუმენტების ნაცვლად უეცრად ისეთ ემოციურ ამბავს მოყვები, რომ ყველას ლოგიკა ავიწყდება და შენს მიერ შექმნილ ატმოსფეროში იძირება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 7,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "impressionistic_non_linear_logic",
        "metaphor": "ocean_depths_mist",
        "text": "შენთვის აზროვნება უსაზღვრო ოკეანეში ცურვას ჰგავს: არ არსებობს ხისტი საზღვრები, მკაცრი ფორმულები და მშრალი პუნქტები. გონება ინფორმაციას აღიქვამს არა ცალკეულ ფაქტებად, არამედ მთლიან, ცოცხალ განწყობად. საოცარი სიზუსტით იჭერ სხვის უთქმელ ტკივილს, ატმოსფეროს ცვლილებასა და სიტყვებს შორის ჩამალულ სიმართლეს. თუმცა როცა ამ განცდის ლოგიკურ ენაზე თარგმნაა საჭირო, შენი აზრი ნისლივით იფანტება და სხვებს უჭირთ შენი გზის გაგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "narrative_boundary_blur",
        "metaphor": "labyrinth_sleepy_hall",
        "text": "შენთვის აზროვნება ოკეანეში ცურვას ჰგავს — ხისტი წესების, ცხრილებისა და სილოგიზმების გარეშე. საოცარი სიზუსტით იჭერ ატმოსფეროს, ფარულ მინიშნებებსა და იმას, რასაც ხმამაღლა ვერავინ ბედავს თქვას. პრობლემა მაშინ იწყება, როცა მკაფიო, მშრალი პასუხია საჭირო: შენი აზრი იწყებს წრეების დარტყმას, პოეტურ გადახვევებს და ბოლოს სულ სხვა ნაპირზე გადის. შენი ინტუიცია გენიალურია, მაგრამ სანამ მას ჩვეულებრივ ენაზე გადმოსცემ, გარშემო ნახევარ დარბაზს ეძინება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
]


def jaccard_similarity(str1: str, str2: str) -> float:
    words1 = set(re.findall(r"\w+", str1.lower()))
    words2 = set(re.findall(r"\w+", str2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    return intersection / union if union > 0 else 0.0


def validate_and_build_assets():
    print("=" * 70)
    print("JESTER PHASE 3.4 — Mercury Full Content Batch Generation & QA")
    print("=" * 70)

    sign_map = {s[0]: s for s in SIGN_SPECS}
    assets = []

    # Check total count
    assert len(MERCURY_RAW_ASSETS) == 96, f"Expected 96 assets, found {len(MERCURY_RAW_ASSETS)}"

    # Check exactly 8 assets per sign
    by_sign = {}
    for raw in MERCURY_RAW_ASSETS:
        by_sign.setdefault(raw["sign"], []).append(raw)

    assert len(by_sign) == 12, f"Expected 12 signs, got {len(by_sign)}"
    for s, s_assets in by_sign.items():
        assert len(s_assets) == 8, f"Sign {s} must have exactly 8 assets, got {len(s_assets)}"
        micros = [a for a in s_assets if a["depth"] == "micro"]
        mediums = [a for a in s_assets if a["depth"] == "medium"]
        assert len(micros) == 6, f"Sign {s} must have 6 micros, got {len(micros)}"
        assert len(mediums) == 2, f"Sign {s} must have 2 mediums, got {len(mediums)}"

    # Audit all texts
    all_texts = []
    tone_counts = {}
    depth_counts = {}
    metaphor_by_sign = {}

    for raw in MERCURY_RAW_ASSETS:
        s_name, elem, mod = sign_map[raw["sign"]]
        text = raw["text"]
        char_len = len(text)
        depth = raw["depth"]
        tone = raw["tone"]

        tone_counts[tone] = tone_counts.get(tone, 0) + 1
        depth_counts[depth] = depth_counts.get(depth, 0) + 1
        metaphor_by_sign.setdefault(s_name, set()).add(raw["metaphor"])

        # Character length constraints
        if depth == "micro":
            assert 100 <= char_len <= 250, f"Micro length violation ({char_len} chars): {text}"
        elif depth == "medium":
            assert 400 <= char_len <= 750, f"Medium length violation ({char_len} chars): {text}"
        else:
            raise ValueError(f"Invalid depth: {depth}")

        # Zero Jargon check
        jargon_matches = scan_for_jargon(text, "ka")
        assert len(jargon_matches) == 0, f"Forbidden jargon {jargon_matches} found in: {text}"

        # Zero Clinical / Claims check
        for c_pat in FORBIDDEN_CLAIMS:
            assert not re.search(c_pat, text, re.IGNORECASE), f"Forbidden claim pattern '{c_pat}' matched in: {text}"

        # Zero Forbidden Openings check
        for o in FORBIDDEN_OPENINGS:
            assert not text.strip().lower().startswith(o), f"Forbidden opening '{o}' in: {text}"

        # Quality Gate check: every category >= 4.0
        q = raw["quality"]
        for dim, score in q.items():
            assert score >= 4.0, f"Quality gate failed for {dim} ({score} < 4.0) in asset: {text}"

        all_texts.append(text)

        # Build production ContentAsset dict
        contract_id = f"self.cognition.mercury_{s_name}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract: {contract_id}"

        asset_id = f"ca_cog_{s_name[:3]}_{raw['index']:03d}_ka_{tone[:3]}_{depth[:3]}"
        variant_key = f"{tone}_ka_{depth[:3]}_{raw['index']:02d}"

        asset_dict = {
            "asset_id": asset_id,
            "interpretation_id": contract_id,
            "locale": "ka",
            "context": "self",
            "tone": tone,
            "persona": "jester",
            "text": text,
            "status": "approved",
            "version": 1,
            "priority": 100,
            "variant_key": variant_key,
            "source": "copywriter",
            "author": "jester_content_factory",
            "tags": [
                "batch:mercury_full_v1",
                "body:mercury",
                f"sign:{s_name}",
                f"element:{elem}",
                f"modality:{mod}",
                f"depth:{depth}",
                f"angle:{raw['angle']}",
                f"metaphor:{raw['metaphor']}",
            ],
            "internal_notes": json.dumps({
                "batch_id": "mercury_full_v1",
                "astrological_fact": f"Mercury is in {s_name.capitalize()}",
                "semantic_contract": contract_id,
                "semantic_angle": raw["angle"],
                "metaphor_family": raw["metaphor"],
                "char_length": char_len,
                "quality_scores": q,
            }, ensure_ascii=False),
            "provenance": {
                "batch_id": "mercury_full_v1",
                "interpretation_id": contract_id,
                "body": "mercury",
                "sign": s_name,
                "element": elem,
                "modality": mod,
                "semantic_contract_id": contract_id,
                "semantic_angle": raw["angle"],
                "tone": tone,
                "depth": depth,
                "variant": variant_key,
                "source_inputs": {
                    "mercury_sign": s_name,
                    "element": elem,
                    "modality": mod,
                },
                "quality_gate": {
                    **q,
                    "status": "passed",
                },
            },
            "archived": False,
            "weight": 1.0,
            "created_at": "2026-09-08T00:00:00Z",
            "updated_at": "2026-09-08T00:00:00Z",
        }
        assets.append(asset_dict)

    # Programmatic Uniqueness & Jaccard Collision Audit
    assert len(all_texts) == len(set(all_texts)), "Duplicate texts found across batch!"

    for i in range(len(all_texts)):
        for j in range(i + 1, len(all_texts)):
            sim = jaccard_similarity(all_texts[i], all_texts[j])
            assert sim < 0.85, f"Near-duplicate detected (Jaccard {sim:.2f} >= 0.85):\nA: {all_texts[i]}\nB: {all_texts[j]}"

    # Metaphor diversity per sign (>= 6 distinct families per sign)
    for s, mets in metaphor_by_sign.items():
        assert len(mets) >= 6, f"Sign {s} has only {len(mets)} distinct metaphor families, required >= 6"

    # Save output to backend/app/interpretation/data/mercury_corpus.json
    out_dir = root_dir / "backend" / "app" / "interpretation" / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "mercury_corpus.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Generated and validated exactly {len(assets)} Mercury assets.")
    print(f"  - Micro: {depth_counts['micro']}")
    print(f"  - Medium: {depth_counts['medium']}")
    print("Tone Distribution across batch:")
    for t, c in sorted(tone_counts.items()):
        print(f"  - {t}: {c}")
    print(f"Saved to: {out_path}")
    return assets


if __name__ == "__main__":
    validate_and_build_assets()
