"""
JESTER — PHASE 3.10
Mars Full Generation & Astrological Provenance Hardening Pipeline
Generates exactly 96 Mars assets (12 signs x 8 assets: 72 Micro, 24 Medium, 0 Deep)
with machine-readable provenance, QA scoring, Action != Anger firewall, and zero-jargon / zero-claim safety.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any

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
    r"\bდიაგნოზ", r"\bფსიქიკური აშლილობ", r"\bმოღალატე ხარ\b",
    r"\bნარცისი ხარ\b", r"\bფსიქოპათ", r"\bკრიმინალ",
    r"\bეს დამტკიცებულია\b", r"\bშენი ტვინი ასე მუშაობს\b",
    r"\bეს ფსიქოლოგიურად ნიშნავს\b", r"\bშენ აუცილებლად\b",
    r"\bმიჯაჭვულობის სინდრომ", r"\bმიჯაჭვულობის ტიპ", r"\bშფოთვითი მიჯაჭვულობ",
    r"\bშენი მეორე ნახევარი\b", r"\bგარანტირებული სიყვარულ",
    r"\bფიზიკური ძალადობ", r"\bცემა\b", r"\bსისხლი\b",
    r"\bტესტოსტერონ", r"\bსექსუალური ტემპერამენტ",
]

FORBIDDEN_OPENINGS = [
    "წარმოიდგინე სიტუაცია",
    "წარმოიდგინე",
    "შენ ხარ",
    "შენი სიყვარულის ენაა",
    "შენი იდეალური პარტნიორია",
]

ANGER_CLICHES = [
    r"ბრაზდები",
    r"ჩხუბობ",
    r"აგრესიული ხარ",
    r"თავს ესხმი",
    r"ვერ აკონტროლებ თავს",
]

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

MARS_FULL_RAW_ASSETS: list[dict[str, Any]] = [
    # =========================================================================
    # 1. ARIES (self.action.mars_aries.v1)
    # =========================================================================
    {
        "sign": "aries",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "kinetic_frontal_initiative",
        "action_angle": "initiation",
        "metaphor": "sprint_ignition",
        "text": "შენთვის მოქმედების დაწყებას შესავალი არ სჭირდება: როგორც კი მიზანს დაინახავ, პირველივე წამიდან სრული სვლით მიიწევ წინ. სანამ სხვა გეგმას წერს, შენ უკვე მოქმედებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "combative_impatience",
        "action_angle": "resistance",
        "metaphor": "direct_breach",
        "text": "წინააღმდეგობას შემოვლითი გზებით არ უყურებ: თუ წინ კედელი დაგხვდა, პირდაპირი ბიძგით ცდილობ მის გატეხვას. შენთვის მოთმინება მხოლოდ ენერგიის ფუჭი ხარჯვაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "kinetic_frontal_initiative",
        "action_angle": "activation",
        "metaphor": "kinetic_spark",
        "text": "როგორც კი იდეა თავში გაგიელვებს, ადგილზე ვეღარ ჩერდები: შენთვის ფიქრი და ნაბიჯის გადადგმა ერთი და იგივე პროცესია. ყოყმანი შენს ენერგიას მომენტალურად კლავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 4,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "combative_impatience",
        "action_angle": "pursuit",
        "metaphor": "fast_arrow",
        "text": "მიზნისკენ ისეთი სისწრაფით მიქრიხარ, რომ გზაში დეტალების შემჩნევას ვერც ასწრებ: მთავარია პირველი მიხვიდე, ხოლო რა დარჩა უკან გადათელილი, მაგას მერე გაარკვევ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 5,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "kinetic_frontal_initiative",
        "action_angle": "execution",
        "metaphor": "hammer_strike",
        "text": "სანამ სხვები გადაწყვეტილების მიღების წესებს განიხილავენ, შენ უკვე კარს ამტვრევ და საქმეს აკეთებ: შენი ლოგიკა მარტივია — რაც უფრო სწრაფად იმოქმედებ, ნაკლები კითხვა გაჩნდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "combative_impatience",
        "action_angle": "tactical_adaptation",
        "metaphor": "rapid_rebound",
        "text": "თუ პირველმა იერიშმა შედეგი არ მოიტანა, ტაქტიკის ანალიზს კი არ იწყებ, არამედ წამში ახალ სამიზნეს პოულობ: შენთვის წარუმატებლობა მხოლოდ მიმართულების შეცვლის საბაბია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "high_velocity_burnout",
        "action_angle": "persistence_momentum",
        "metaphor": "rocket_thruster",
        "text": "შენი მოქმედების მექანიზმი პირველივე წამში მაქსიმალური აჩქარებით ჩართვას ჰგავს: ან მყისიერად იღებ შედეგს, ან ინტერესი იმავე სისწრაფით გიქრება. ვერ იტან გაწელილ პროცედურებს, ხანგრძლივ განხილვებსა და სხვის ყოყმანს — შენთვის ნებისმიერი პაუზა უკან დახევის ტოლფასია. მთელი ძალით შედიხარ საქმეში და პირველივე წინაღობას პირდაპირ ეჯახები. თუმცა შენი მთავარი სისუსტე სწორედ ეს მოკლე დისტანციის ენერგიაა: თუ ბარიერი პირველი დარტყმით არ ჩამოიშალა, მეორე რაუნდისთვის მოთმინება აღარ გყოფნის და ხშირად საქმეს მანამ ტოვებ, სანამ სხვები საერთოდ გარკვევას მოასწრებდნენ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 8,
        "depth": "medium",
        "tone": "conversational",
        "angle": "high_velocity_burnout",
        "action_angle": "blind_spot",
        "metaphor": "short_circuit_fuse",
        "text": "რეალურად რომ დავაკვირდეთ, შენი მოქმედების სტილი ელვისებურ აფეთქებას ჰგავს: როცა რაღაცის მიღწევა გინდა, მთელ ძალას ერთ წერტილში უყრი თავს და ისეთი სისწრაფით იჭრები წინ, რომ წინააღმდეგობას წამებში ანგრევ. შენთან საქმის გაჭიანურება და ცივი ლოდინი გამორიცხულია — მოქმედებ ახლა, დაუყოვნებლივ და უკომპრომისოდ. თუმცა შენი მთავარი პრობლემა ისაა, რომ გრძელვადიანი ალყისთვის რესურსი არ გაქვს: თუ პირველმა შეტევამ მყისიერი შედეგი არ მოიტანა, მოთმინება წამებში გეწურება და საქმეს მანამ ტოვებ, სანამ სხვები საერთოდ ჩაერთვებოდნენ. ვერ იტან მონოტონურ პროცესს, სადაც ყოველდღიური რუტინით უნდა აშენო შედეგი; შენ გამარჯვება პირველივე რაუნდში გჭირდება, თორემ ინტერესი იმავე წამს ქრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 2. TAURUS (self.action.mars_taurus.v1)
    # =========================================================================
    {
        "sign": "taurus",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "relentless_grinding_momentum",
        "action_angle": "initiation",
        "metaphor": "heavy_tractor",
        "text": "საქმის დაწყებას დრო სჭირდება, მაგრამ როგორც კი დაძრავ, შენს შეჩერებას ვეღარავინ მოახერხებს. შენი ძალა აჩქარებაში კი არა, მძიმე და შეუჩერებელ სვლაშია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 2,
        "depth": "micro",
        "tone": "snarky",
        "angle": "immovable_resistance_torque",
        "action_angle": "resistance",
        "metaphor": "granite_weight",
        "text": "თუ ვინმე შენი გზიდან ჩამოშორებას შეეცდება, უბრალოდ მთელი სიმძიმით ერთ ადგილზე ჩერდები: შენთან დაპირისპირება კედლისთვის მხრით მიწოლას ჰგავს — კედელი არ დაიძვრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 3,
        "depth": "micro",
        "tone": "jester",
        "angle": "relentless_grinding_momentum",
        "action_angle": "activation",
        "metaphor": "hydraulic_press",
        "text": "შენი დაძვრა თუ მოხდა, წინაღობას შანსი არ რჩება: არ ყვირი და არ ჩქარობ, უბრალოდ ჰიდრავლიკური წნეხივით თანაბრად აწვები და საქმე ზუსტად ისე სრულდება, როგორც შენ გადაწყვიტე.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 4,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "immovable_resistance_torque",
        "action_angle": "pursuit",
        "metaphor": "deep_furrow",
        "text": "სანამ სხვები მოკლე გზებს ეძებენ, შენ მიწაში ღრმა კვალს ავლებ და ნელა მიიწევ წინ: შენი მიზნის მიტოვება ბუნების კანონებს ეწინააღმდეგება — ერთხელ დაწყებულს ბოლომდე გაიყვან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "relentless_grinding_momentum",
        "action_angle": "execution",
        "metaphor": "anchor_hold",
        "text": "შენთვის მოქმედება მიწაში ჩარჭობილ ღუზას ჰგავს: რაც უფრო მეტად ცდილობენ შენს დაჩქარებას, მით უფრო მყარად დგახარ ერთ წერტილში და მშვიდად ელი, სანამ მოწინააღმდეგე დაიღლება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 6,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "immovable_resistance_torque",
        "action_angle": "tactical_adaptation",
        "metaphor": "slow_grind",
        "text": "თუ გზა გადაგეკეტა, უკან არ იხევ და არც შემოვლით გარბიხარ: იწყებ ნელ, შეუჩერებელ ხეხვას მანამ, სანამ ბარიერი თავისით არ გაიცვითება და შენს მძიმე ნაბიჯს გზას არ დაუთმობს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 7,
        "depth": "medium",
        "tone": "mocking",
        "angle": "inertia_friction",
        "action_angle": "persistence_momentum",
        "metaphor": "steamroller_engine",
        "text": "შენი მოქმედების სტილი მძიმე ტექნიკის მუშაობას ჰგავს: სანამ ძრავი გაცხელდება და ადგილიდან დაიძვრები, გარშემო ყველას ჰგონია, რომ არაფრის გაკეთებას არ აპირებ. სამაგიეროდ, როგორც კი მექანიზმი ჩაირთვება, შენი შეჩერება ბუნებრივ კატასტროფას უტოლდება — მიდიხარ დინჯად, თანაბარი ტემპით და უბრალოდ ასწორებ ყველაფერს, რაც გზაზე გეღობება. პრობლემა ისაა, რომ მიმართულების შეცვლა შენთვის შეუძლებელი მისიაა: მაშინაც კი, როცა აშკარაა, რომ წინ უფსკრულია, ინერციით მაინც ჯიუტად იმავე კურსს მიჰყვები, რადგან მოხვევა ზედმეტ ენერგიას მოითხოვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 8,
        "depth": "medium",
        "tone": "cocky",
        "angle": "inertia_friction",
        "action_angle": "blind_spot",
        "metaphor": "tectonic_mass",
        "text": "ჩემს შეჩერებას ვინც შეეცდება, თავად აღმოჩნდება გზიდან გადაგდებული: შენი მოქმედების მექანიზმი ტექტონიკური ფილის მოძრაობას ჰგავს — სანამ დაიძვრები, დრო გადის, მაგრამ თუ დაიძარი, შენი შეჩერება შეუძლებელია. საქმეს უდგები ისეთი მძიმე და გათვლილი ენერგიით, რომ ნებისმიერი ზედაპირული დაბრკოლება შენს წონას თავისით ემორჩილება. არ გჭირდება ზედმეტი ჟესტები; შენი მთავარი კოზირი ურყევი სიმტკიცე და შეუჩერებელი სვლაა. თუმცა პრობლემა ისაა, რომ როცა სიტუაცია მკვეთრ მანევრს და მოქნილობას მოითხოვს, შენ უბრალოდ იყინები: გირჩევნია კედელს წლობით ურტყა თავი და იმავე კურსს მიაწვე, ვიდრე ერთი ნაბიჯით გადაუხვიო გვერდზე, რადგან ტაქტიკის შეცვლა შენთვის საკუთარი პრინციპების ღალატის ტოლფასია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 3. GEMINI (self.action.mars_gemini.v1)
    # =========================================================================
    {
        "sign": "gemini",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "tactical_multi_track_maneuver",
        "action_angle": "initiation",
        "metaphor": "fencing_parry",
        "text": "ბარიერს შუბლით არასდროს ეჯახები: როცა წინ დაბრკოლება ჩნდება, მომენტალურად სამ ახალ შემოვლით გზას პოულობ და საქმეს ისე აგვარებ, რომ ზედმეტ ძალას არ ხარჯავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 2,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "evasive_flanking_strategy",
        "action_angle": "resistance",
        "metaphor": "shadow_maneuver",
        "text": "სანამ მოწინააღმდეგე პირდაპირი დარტყმისთვის ემზადება, შენ უკვე მის ზურგს უკან ხარ და სიტუაციას სულ სხვა რაკურსით მართავ: შენი მთავარი იარაღი სისხარტე და მოულოდნელობაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "tactical_multi_track_maneuver",
        "action_angle": "activation",
        "metaphor": "quick_switch",
        "text": "შენთვის მოქმედების დაწყება ჩამრთველის წამიერ გადაწევას ჰგავს: ერთი გეგმით არასდროს შემოიფარგლები, ჯიბეში ყოველთვის გაქვს სათადარიგო სვლა, რომელსაც საჭიროებისთანავე ჩართავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "evasive_flanking_strategy",
        "action_angle": "pursuit",
        "metaphor": "dual_track",
        "text": "სანამ სხვები ერთ მიზანზე იყინებიან, შენ ერთდროულად ორ სხვადასხვა მიმართულებით გარბიხარ: თუ ერთი ჩიხში შევიდა, მეორეს გამოიყენებ ისე, რომ დროის დაკარგვას საერთოდ ვერ იგრძნობ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 5,
        "depth": "micro",
        "tone": "mocking",
        "angle": "tactical_multi_track_maneuver",
        "action_angle": "execution",
        "metaphor": "mirror_trick",
        "text": "მოწინააღმდეგეს ყურადღებას ერთი ხელის მოძრაობით უფანტავ, სანამ მეორე ხელით უკვე შედეგი გამოგაქვს: შენი მოქმედება ილუზიონისტის ტრიუკია, სადაც მთავარი დარტყმა შეუმჩნეველი რჩება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 6,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "evasive_flanking_strategy",
        "action_angle": "tactical_adaptation",
        "metaphor": "decoy_pivot",
        "text": "როგორც კი წინაღობას ხედავ, ფორმას წამში იცვლი და სულ სხვა კარიდან შედიხარ: შენთვის ჩიხი არ არსებობს, არსებობს მხოლოდ ახალი, მოულოდნელი მანევრის აუცილებლობა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "energy_dispersion",
        "action_angle": "persistence_momentum",
        "metaphor": "juggling_blades",
        "text": "შენთვის მოქმედება ჭადრაკის სწრაფ პარტიას ჰგავს, ოღონდ ერთდროულად ხუთ სხვადასხვა დაფაზე თამაშობ. ვერ იტან ერთფეროვან, მონოტონურ შრომას; შენ გჭირდება გამუდმებით იცვლებოდეს ტაქტიკა, ჩნდებოდეს ახალი დაბრკოლებები და გეძლეოდეს მანევრირების საშუალება. საოცრად ოსტატურად ახერხებ რთული სიტუაციებიდან მშრალად გამოსვლას მხოლოდ იმიტომ, რომ მოქნილი ხარ. თუმცა შენი მთავარი მტერი საკუთარი ენერგიის გაფანტვაა: იმდენ საქმეს იწყებ ერთდროულად და იმდენ მხარეს გარბიხარ, რომ ხშირად ფინიშის ხაზამდე არცერთი პროექტი არ მიგყავს, რადგან გზაში ახალი იდეა გადაგეღობა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 8,
        "depth": "medium",
        "tone": "conversational",
        "angle": "energy_dispersion",
        "action_angle": "blind_spot",
        "metaphor": "mosaic_puzzle",
        "text": "რეალურად რომ შევხედოთ, შენი მოქმედების მექანიზმი საოცრად მოქნილი და სწრაფია: როცა წინ დაბრკოლება ჩნდება, შუბლით კი არ ეჯახები, არამედ წამში ხუთ ალტერნატიულ გზას იგონებ და სიტუაციას ისე უვლი გვერდს, რომ დაძაბულობას საერთოდ არ ტოვებ. შეგიძლია ერთდროულად ათ საქმეს მოკიდო ხელი და ყველგან შექმნა მოძრაობის ილუზია. პრობლემა ისაა, რომ შენი ყურადღების რესურსი ზედმეტად სწრაფად იფანტება: როგორც კი საქმე რუტინულ, მონოტონურ ფაზაში გადადის და მანევრირების ადგილი აღარ რჩება, ინტერესი მომენტალურად გიქრება. იწყებ ბრწყინვალედ, იგონებ უამრავ სვლას, მაგრამ ფინიშის ხაზამდე მისვლა გეზარება, რადგან ჰორიზონტზე უკვე ახალი, ბევრად უფრო სახალისო თამაში გამოჩნდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 4. CANCER (self.action.mars_cancer.v1)
    # =========================================================================
    {
        "sign": "cancer",
        "index": 1,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "protective_defensive_surge",
        "action_angle": "initiation",
        "metaphor": "fortress_guard",
        "text": "შენი ძალა მაშინ იღვიძებს, როცა შენს სივრცეს ან ახლობლებს საფრთხე ემუქრება: ასეთ დროს მშვიდი დამკვირვებლიდან შეუვალ, დაუნდობელ მფარველად იქცევი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "indirect_sideways_advance",
        "action_angle": "resistance",
        "metaphor": "coastal_wave",
        "text": "პირდაპირ იერიშზე იშვიათად გადადიხარ: ჯერ სიტუაციას გვერდიდან შემოუვლი, ნიადაგს მოსინჯავ და ზუსტად მაშინ გადადგამ ნაბიჯს, როცა მეორე მხარე ამას ყველაზე ნაკლებად ელის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 3,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "protective_defensive_surge",
        "action_angle": "activation",
        "metaphor": "protective_moat",
        "text": "მოქმედებას მაშინ იწყებ, როცა შენს ტერიტორიაზე უცხო ნაბიჯის ხმა გაისმის: არ ელოდები დარტყმას, მომენტალურად თხრი დამცავ ზოლს და სიტუაციას სრულიად შენს წესებს უმორჩილებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "indirect_sideways_advance",
        "action_angle": "pursuit",
        "metaphor": "defensive_shield",
        "text": "მიზნისკენ პირდაპირ არ გარბიხარ — მოძრაობ ფრთხილად, საიმედო თავშესაფრიდან თავშესაფრამდე: მაგრამ თუ რამე ჩაიფიქრე, იმას ისეთი სიმტკიცით იცავ, რომ უკან დახევას არავითარ შემთხვევაში არ აპირებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 5,
        "depth": "micro",
        "tone": "jester",
        "angle": "protective_defensive_surge",
        "action_angle": "execution",
        "metaphor": "shell_armor",
        "text": "შენი გადაწყვეტილების აღსრულება მყარი ჯავშნის მორგებას ჰგავს: სანამ ყველა დარწმუნებულია, რომ გაჩერდი, შენ ჩუმად, შიგნიდან ამაგრებ პოზიციას და საქმეს ბოლომდე წყვეტ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "indirect_sideways_advance",
        "action_angle": "tactical_adaptation",
        "metaphor": "current_undertow",
        "text": "როცა ხედავ, რომ პირისპირ ბრძოლა უშედეგოა, უკან კი არ იხევ, არამედ წყალქვეშა დინებასავით იწყებ მოქმედებას: მეორე მხარეს ნიადაგს ფეხქვეშ შეუმჩნევლად აცლი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 7,
        "depth": "medium",
        "tone": "snarky",
        "angle": "tenacious_emotional_clamp",
        "action_angle": "persistence_momentum",
        "metaphor": "crab_pincer_lock",
        "text": "შენი მოქმედების სტილი მოულოდნელი ტალღასავით მუშაობს: სანამ გარედან სიმშვიდე ჩანს, შენ შინაგანად ენერგიას აგროვებ და როგორც კი საჭირო მომენტი დგება, საქმეს ისეთი სიმტკიცით ჩაებღაუჭები, რომ ხელიდან ვეღარავინ გამოგგლეჯს. არ გიყვარს ღია, ხმაურიანი ბრძოლა; შენთვის გაცილებით კომფორტულია სიტუაციის კულუარებიდან, ფრთხილი მანევრებით მართვა. თუმცა შენი სუსტი წერტილი ზედმეტი თავდაცვითი რეჟიმია: ხშირად უბრალო სამუშაო წინააღმდეგობასაც კი პირად შეურაცხყოფად აღიქვამ, ჩუმად საკუთარ ნაჭუჭში იკეტები და საქმის კეთების ნაცვლად შინაგან წყენას უსასრულოდ ამუშავებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 8,
        "depth": "medium",
        "tone": "cocky",
        "angle": "tenacious_emotional_clamp",
        "action_angle": "blind_spot",
        "metaphor": "citadel_bastion",
        "text": "ჩემს ტერიტორიაზე შემოჭრას ვინც შეეცდება, ძალიან სწრაფად მიხვდება, რომ შეცდომა დაუშვა: შენი მოქმედების მექანიზმი მიუდგომელ ციტადელს ჰგავს, რომელიც ერთი შეხედვით მშვიდია, მაგრამ საჭიროებისას მომენტალურად იკეტება და უმძლავრეს კონტრშეტევას ანხორციელებს. საოცრად ზუსტად გრძნობ, როდის უნდა გააკეთო მანევრი და როდის უნდა გაიყინო. თუმცა შენი სისუსტე სწორედ ეს გადაჭარბებული ჩაკეტვაა: ხშირად ობიექტურ, საქმიან დაბრკოლებასაც კი პირად შეურაცხყოფად აღიქვამ, იწყებ ჩრდილში დამალვას და მოქმედების ნაცვლად შინაგან წყენაზე იჭედები. გირჩევნია კვირები დაკარგო თავდაცვით დუმილში, ვიდრე პირდაპირ გახვიდე და პრობლემა ღიად, საქმიანად მოაგვარო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 5. LEO (self.action.mars_leo.v1)
    # =========================================================================
    {
        "sign": "leo",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "sovereign_theatrical_assertion",
        "action_angle": "initiation",
        "metaphor": "royal_banner",
        "text": "თუ რამეს აკეთებ, ისე უნდა გააკეთო, რომ ყველამ დაინახოს: შენი მოქმედება ყოველთვის მასშტაბური, თამამი და ღირსებით სავსეა. ჩრდილში წვრილმანი საქმეები არ გხიბლავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "pride_driven_perseverance",
        "action_angle": "resistance",
        "metaphor": "golden_shield",
        "text": "წინააღმდეგობა შენს თავმოყვარეობას აღვიძებს: რაც უფრო მეტად ცდილობენ შენს შეჩერებას, მით უფრო ამაყად და ურყევად დგახარ საკუთარ პოზიციაზე. უკან დახევა შენთვის გამორიცხულია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 3,
        "depth": "micro",
        "tone": "conversational",
        "angle": "sovereign_theatrical_assertion",
        "action_angle": "activation",
        "metaphor": "lion_herald",
        "text": "შენთვის მოქმედების დაწყება ყოველთვის მოვლენაა: არ შეგიძლია საქმეს ჩუმად, კუთხეში მიუდგე. თუ რამეს იწყებ, მთელი ენერგიით აცხადებ ამას და სხვებსაც პროცესში ითრევ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 4,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "pride_driven_perseverance",
        "action_angle": "pursuit",
        "metaphor": "high_pedestal",
        "text": "სანამ სხვები პატარა მიზნებზე კამათობენ, შენ პირდაპირ ყველაზე მაღალ საფეხურს ირჩევ და იქით მიემართები: შენი მოქმედება ყოველთვის მაქსიმალურ მასშტაბს მოითხოვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 5,
        "depth": "micro",
        "tone": "snarky",
        "angle": "sovereign_theatrical_assertion",
        "action_angle": "execution",
        "metaphor": "crown_seal",
        "text": "საქმის დასრულებას ისე აღნიშნავ, თითქოს იმპერია დაიპყარი: შენი ხელმოწერა ნებისმიერ შედეგზე იმდენად მკაფიოა, რომ ავტორის ვინაობაზე კითხვა არავის უჩნდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "pride_driven_perseverance",
        "action_angle": "tactical_adaptation",
        "metaphor": "sovereign_stride",
        "text": "თუ გეგმა ჩაიშალა, შეცდომას კი არ აღიარებ, არამედ წარუმატებლობასაც ისეთი სამეფო თავდაჯერებით გადააბიჯებ, თითქოს ეს თავიდანვე შენი სტრატეგიის ნაწილი იყო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 7,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "status_vulnerability_stalemate",
        "action_angle": "persistence_momentum",
        "metaphor": "arena_spotlight",
        "text": "შენთვის მოქმედება საკუთარი ძალის საჯარო დემონსტრირებაა. როცა საქმეს ხელს კიდებ, მთელი არსებით ერთვები, რადგან შენთვის საშუალო შედეგი უბრალოდ მიუღებელია — ყველაფერი სამეფო სტანდარტით უნდა შესრულდეს. შენი ენთუზიაზმი გარშემომყოფებსაც აიძულებს ფეხი აგიწყონ. თუმცა შენი აქილევსის ქუსლი სწორედ ეს გადაჭარბებული პატივმოყვარეობაა: თუ დაინახე, რომ შენს წამოწყებას ხალხი აღფრთოვანებით არ შეხვდა, ან შეცდომა მოგივიდა, აღიარების ნაცვლად ჯიუტად იმავე პოზიციაზე იყინები, ოღონდ სხვების თვალში შენი რეპუტაცია არ შეირყეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "status_vulnerability_stalemate",
        "action_angle": "blind_spot",
        "metaphor": "solar_flair",
        "text": "მოდი ვაღიაროთ: შენთვის მოქმედება თეატრალური წარმოდგენაა, სადაც მთავარ როლს ყოველთვის შენ ასრულებ. საოცარი ენერგიით შეგიძლია ხალხის გაძღოლა და ყველაზე უიმედო პროექტისაც კი გრანდიოზულ გამარჯვებად ქცევა, რადგან შენი ენთუზიაზმი გადამდებია. მაგრამ საქმე მაშინ რთულდება, როცა ჩრდილში, რუტინული შავი სამუშაოა შესასრულებელი: თუ მაყურებელი არ გყავს და ტაშს არავინ გიკრავს, მოტივაცია წამებში გიქრება. შენი მთავარი ხაფანგი სიამაყეა — როცა ხედავ, რომ შენი მიდგომა არ მუშაობს, ტაქტიკის შეცვლის ნაცვლად ჯიუტად იგივე პოზაში დგახარ, ოღონდ ვინმემ არ იფიქროს, რომ შეცდი, და ამ დემონსტრაციულ სიჯიუტეში მთელ რეალურ შედეგს ანიავებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 6. VIRGO (self.action.mars_virgo.v1)
    # =========================================================================
    {
        "sign": "virgo",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "surgical_precision_execution",
        "action_angle": "initiation",
        "metaphor": "scalpel_calibration",
        "text": "შენთვის მოქმედება ქაოსური ენერგიის ფრქვევა კი არა, ზუსტი გათვლაა: ჯერ დეტალებს შეისწავლი, სუსტ წერტილებს იპოვი და მერე ერთი მიზანმიმართული მოძრაობით წყვეტ საკითხს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 2,
        "depth": "micro",
        "tone": "snarky",
        "angle": "systematic_defect_correction",
        "action_angle": "resistance",
        "metaphor": "diagnostic_scanner",
        "text": "თუ საქმე გაიჭედა, ყვირილს და ნერვიულობას არ იწყებ: მშვიდად იღებ ინსტრუმენტებს, შლი პროცესს შემადგენელ ნაწილებად და ხარვეზს მანამ ასწორებ, სანამ მექანიზმი იდეალურად არ იმუშავებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 3,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "surgical_precision_execution",
        "action_angle": "activation",
        "metaphor": "micro_filter",
        "text": "მოქმედებას არა დიდი ხმაურით, არამედ უმცირესი დეტალის გასუფთავებით იწყებ: როცა ზედმეტ ხმაურს ჩამოაცილებ, პროცესი ისე შეუფერხებლად მიდის, თითქოს თავისით მოგვარდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "systematic_defect_correction",
        "action_angle": "pursuit",
        "metaphor": "blueprint_grid",
        "text": "მიზნისკენ წინასწარ დახაზული სქემით მიდიხარ: არანაირი ინტუიცია და ქაოსური ნახტომები, ყოველი ნაბიჯი ზუსტად იმდენ მილიმეტრს ფარავს, რამდენიც სისტემის გამართვისთვისაა საჭირო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 5,
        "depth": "micro",
        "tone": "cocky",
        "angle": "surgical_precision_execution",
        "action_angle": "execution",
        "metaphor": "precision_laser",
        "text": "პრობლემასთან მიდგომა ლაზერული ჭრით გირჩევნია: სანამ სხვები უროთი ურტყამენ კედელს, შენ ერთ კონკრეტულ ჭანჭიკს უჭერ და მთელი მექანიზმი უხმოდ მუშაობს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 6,
        "depth": "micro",
        "tone": "jester",
        "angle": "systematic_defect_correction",
        "action_angle": "tactical_adaptation",
        "metaphor": "surgical_tweezer",
        "text": "თუ სისტემაში ხარვეზი გაიპარა, პანიკას კი არ იწყებ, არამედ პინცეტით აცლი პრობლემურ დეტალს და პროცესს ისეთი სიზუსტით აგრძელებ, თითქოს არაფერი მომხდარა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 7,
        "depth": "medium",
        "tone": "mocking",
        "angle": "micro_perfectionist_friction",
        "action_angle": "persistence_momentum",
        "metaphor": "watchmaker_loupe",
        "text": "შენი მოქმედების სტილი ქირურგიულ ჩარევას ჰგავს: ემოციებს მთლიანად თიშავ, საქმეს საინჟინრო ამოცანად აქცევ და უმცირეს დეტალსაც კი ისეთი პედანტურობით ამუშავებ, რომ შეცდომის შანსი ნულამდე დაგყავს. ვერ იტან ზერელე, ნაჩქარევ ნაბიჯებს; შენთვის მთავარია ხარისხი და პრაქტიკული გამართულობა. მაგრამ შენი მთავარი ხაფანგი სწორედ ეს გადაჭარბებული პერფექციონიზმია: ხანდახან ისე ღრმად ეფლობი უმნიშვნელო წვრილმანების გაპრიალებაში, რომ მთავარი მოქმედება ჩერდება და მთელ ენერგიას ისეთი ხარვეზების გასწორებაზე ხარჯავ, რომლებსაც რეალურად საქმის ბედზე გავლენა არ ჰქონდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "micro_perfectionist_friction",
        "action_angle": "blind_spot",
        "metaphor": "laboratory_centrifuge",
        "text": "ყოველი შეცდომა შენთვის კატასტროფაა, ამიტომ სანამ შედეგს გამოაჩენ, მას უმაღლესი სიმკაცრით ამოწმებ: შენი მოქმედების მექანიზმი საიდუმლო ლაბორატორიას ჰგავს, სადაც ყოველი ნაბიჯი გათვლილია და შემთხვევითობას ადგილი არ აქვს. სხვების ქაოსურ მცდელობებს მშვიდი დაკვირვებით უყურებ, რადგან იცი, რომ საბოლოოდ პრობლემას მაინც შენი სისტემური მიდგომა გადაჭრის. თუმცა შენი მთავარი დრამა სწორედ ეს მიკროსკოპული ჩაღრმავებაა: ხშირად ისე იკარგები წვრილმანი დეტალების გაპრიალებაში, რომ მთლიანი პროექტის ჩაბარების ვადას აცდენ. საქმე უკვე იდეალურია, მაგრამ შენ მაინც პოულობ ერთ შეუმჩნეველ ნაკლს და მის გასწორებაში მთელ ძვირფას დროს ხარჯავ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 7. LIBRA (self.action.mars_libra.v1)
    # =========================================================================
    {
        "sign": "libra",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "strategic_diplomatic_leverage",
        "action_angle": "initiation",
        "metaphor": "velvet_glove",
        "text": "უხეში ძალით ზეწოლა შენი სტილი არ არის: სასურველ შედეგს ისეთი დახვეწილი დიპლომატიით და მოკავშირეების შეკრებით აღწევ, რომ მეორე მხარე ვერც ხვდება, როგორ დათმო პოზიცია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "calibrated_reciprocal_pressure",
        "action_angle": "resistance",
        "metaphor": "balanced_fulcrum",
        "text": "კონფლიქტში შენი მიზანი მეორის განადგურება კი არა, წონასწორობის აღდგენაა: ყოველთვის ეძებ სამართლიან გადაწყვეტას, სადაც ორივე მხარე საკუთარ წილ პასუხისმგებლობას დაინახავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "strategic_diplomatic_leverage",
        "action_angle": "activation",
        "metaphor": "diplomatic_pact",
        "text": "მოქმედებას მარტო არასდროს იწყებ: ჯერ მოკავშირეებს შემოიკრებ, პოზიციებს შეათანხმებ და საქმეს ისე გააკეთებ, რომ პასუხისმგებლობა ყველაზე თანაბრად გადანაწილდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 4,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "calibrated_reciprocal_pressure",
        "action_angle": "pursuit",
        "metaphor": "strategic_bridge",
        "text": "მიზნისკენ პირდაპირი იერიშით კი არა, ხიდების მშენებლობით მიდიხარ: შენი სვლა ყოველთვის ისეა გათვლილი, რომ მეორე მხარეს უკან დასახევი გზა ღირსეულად შეუნარჩუნდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 5,
        "depth": "micro",
        "tone": "cocky",
        "angle": "strategic_diplomatic_leverage",
        "action_angle": "execution",
        "metaphor": "golden_scales",
        "text": "შენი გადაწყვეტილება საიუველირო სასწორივით ზუსტია: უხეში ზეწოლის გარეშე, მხოლოდ სწორი ბერკეტის შერჩევით აღწევ იმას, რასაც სხვები ხმაურიანი ბრძოლით ვერ ახერხებენ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 6,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "calibrated_reciprocal_pressure",
        "action_angle": "tactical_adaptation",
        "metaphor": "chess_gambit",
        "text": "თუ სიტუაცია ჩიხში შევიდა, შეტაკებას არ იწყებ: მშვიდად სწირავ მეორეხარისხოვან პოზიციას, მოწინააღმდეგეს ყურადღებას უდუნებ და მთავარ მიზანს მაინც შენს სასარგებლოდ წყვეტ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "indecisive_arbitration_hesitation",
        "action_angle": "persistence_momentum",
        "metaphor": "court_pendulum",
        "text": "შენთვის მოქმედება სტრატეგიულ ჭადრაკს ჰგავს, სადაც მთავარი ამოცანა სუფთა ხელებით თამაში და წესების დაცვაა. საოცარი ოსტატობით ახერხებ ყველაზე დაძაბული სიტუაციაც კი მოლაპარაკებების მაგიდასთან გადაიტანო და უხეში დაპირისპირება ცივილურ დიალოგად აქციო. ყოველთვის ცდილობ მოძებნო ოქროს შუალედი, სადაც არავინ დარჩება განაწყენებული. თუმცა შენი სისუსტე სწორედ ეს გადაჭარბებული ყოყმანია: სანამ ყველა შესაძლო პოზიციას აწონი, ყველას არგუმენტს მოისმენ და იდეალურ ბალანსს დაადგენ, მოქმედების გადამწყვეტი მომენტი ხშირად ხელიდან მიფრინავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 8,
        "depth": "medium",
        "tone": "mocking",
        "angle": "indecisive_arbitration_hesitation",
        "action_angle": "blind_spot",
        "metaphor": "marble_colonnade",
        "text": "შენი მოქმედების სტილი უსასრულო დიპლომატიურ მიღებას ჰგავს, სადაც თითოეული ნაბიჯი იმდენად ზრდილობიანია, რომ რეალური საქმე საერთოდ აღარ კეთდება. საოცარი ოსტატობით ახერხებ ინტერესთა კონფლიქტის განმუხტვას და ისეთი გარემოს შექმნას, სადაც ადამიანები შენს ნებას ისე ასრულებენ, რომ ჰგონიათ, ეს მათი საკუთარი გადაწყვეტილება იყო. მაგრამ შენი სასაცილო ხაფანგი გაუთავებელი შეთანხმებების ძიებაა: როცა სიტუაცია ითხოვს მკვეთრ, მყისიერ ნაბიჯს ვიღაცის უკმაყოფილების ფასად, შენ იყინები. იწყებ უსასრულო კონსულტაციებს, წონი ყველა მხარის არგუმენტს და მანამ ელოდები იდეალურ კომპრომისს, სანამ მოქმედების მომენტი შეუქცევადად არ დაიკარგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 8. SCORPIO (self.action.mars_scorpio.v1)
    # =========================================================================
    {
        "sign": "scorpio",
        "index": 1,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "subterranean_strategic_resolve",
        "action_angle": "initiation",
        "metaphor": "silent_submarine",
        "text": "შენს განზრახვას წინასწარ ვერავინ გაიგებს: მოქმედებ ჩუმად, სიღრმიდან და ისეთი კონცენტრაციით, რომ როცა შენი ნაბიჯი გამოჩნდება, საქმე უკვე გადაწყვეტილია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 2,
        "depth": "micro",
        "tone": "cocky",
        "angle": "unrelenting_psychological_stamina",
        "action_angle": "resistance",
        "metaphor": "deep_faultline",
        "text": "წინააღმდეგობა შენს ენერგიას არ ფიტავს — პირიქით, ზეწოლის ქვეშ შენი გამძლეობა ორმაგდება: შეგიძლია თვეობით უხმოდ იმოძრაო მიზნისკენ და საჭირო მომენტში ზუსტად იქ დაარტყა, სადაც ყველაზე მეტად ჭრის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 3,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "subterranean_strategic_resolve",
        "action_angle": "activation",
        "metaphor": "sonar_pulse",
        "text": "მოქმედებას არა ხმაურით, არამედ სიტუაციის უხმო სკანირებით იწყებ: როგორც კი სუსტ წერტილს დააფიქსირებ, მთელი ენერგიით ერთ კონკრეტულ წერტილზე ახდენ კონცენტრაციას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 4,
        "depth": "micro",
        "tone": "conversational",
        "angle": "unrelenting_psychological_stamina",
        "action_angle": "pursuit",
        "metaphor": "stealth_stalk",
        "text": "მიზანს თვალს არასდროს აშორებ, მაგრამ არც წინასწარ აცხადებ შენს ნაბიჯებს: მოძრაობ ჩრდილში, ინარჩუნებ დისტანციას და ზუსტად მაშინ ჩნდები, როცა საქმე უკვე გარდაუვალია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 5,
        "depth": "micro",
        "tone": "jester",
        "angle": "subterranean_strategic_resolve",
        "action_angle": "execution",
        "metaphor": "pressure_vault",
        "text": "შენი გადაწყვეტილების აღსრულება მაღალი წნევის კამერას ჰგავს: გარეთ არაფერი ჟონავს, მაგრამ შიგნით ისეთი ძალა გროვდება, რომ შედეგის შეჩერებას ვეღარავინ შეძლებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "unrelenting_psychological_stamina",
        "action_angle": "tactical_adaptation",
        "metaphor": "underground_root",
        "text": "თუ ზედაპირზე გზა ჩაიკეტა, მიწისქვეშა ფესვებივით იწყებ განშტოებას: შენთან ბრძოლა ფუჭია — იქ ამოყოფ თავს, სადაც მოწინააღმდეგეს ყველაზე მყარი საყრდენი ეგულებოდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 7,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "scorched_earth_fixation",
        "action_angle": "persistence_momentum",
        "metaphor": "covert_pressure_valve",
        "text": "შენი მოქმედების მექანიზმი აბსოლუტურ კონტროლსა და რკინის თვითდისციპლინაზეა აგებული. არასდროს ხარჯავ ძალას ზედაპირულ ხმაურზე; შენ სწავლობ მოწინააღმდეგის ფსიქოლოგიას, ითვლი მის სუსტ წერტილებს და მოქმედებ მხოლოდ მაშინ, როცა წარმატება გარანტირებულია. შენი გამძლეობა ექსტრემალურ პირობებში შეუდარებელია. მაგრამ შენი მთავარი საფრთხე ფიქსაცია და უკან დაუხევლობაა: თუ ვინმემ შენი გზა გადაკვეთა, ბრძოლას პირად ომად აქცევ და მზად ხარ უზარმაზარი რესურსი დაწვა, ოღონდ საბოლოო გამარჯვება შენ დაგრჩეს — მაშინაც კი, როცა გამარჯვების ფასი თავად მიზანზე ძვირი ჯდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 8,
        "depth": "medium",
        "tone": "snarky",
        "angle": "scorched_earth_fixation",
        "action_angle": "blind_spot",
        "metaphor": "obsidian_forge",
        "text": "მოდი ვაღიაროთ: შენი მოქმედების მექანიზმი წყალქვეშა ნაღმს ჰგავს — სანამ ზედაპირზე სიჩუმეა, შენ სიღრმეში ისეთ სტრატეგიულ კონცენტრაციას ინარჩუნებ, რომ როცა შენი ნაბიჯი გამოჩნდება, წინააღმდეგობას აზრი აღარ აქვს. საოცარი ფსიქოლოგიური გამძლეობა გაქვს და შეგიძლია თვეობით ელოდო ზუსტ მომენტს. მაგრამ შენი მთავარი ხაფანგი ავადმყოფური ფიქსაციაა: თუ საქმე შენს პრინციპებს შეეხო, ამოცანას სამკვდრო-სასიცოცხლო ომად აქცევ. მზად ხარ მთელი საკუთარი რესურსი დაწვა, გადაყარო დრო და ენერგია, ოღონდ მეორე მხარე სრულად დანებდეს. საბოლოოდ იგებ, მაგრამ გამარჯვების ფასი ხშირად იმდენად დიდია, რომ მიღწეული შედეგი თავად გაყენებს ზარალს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 9. SAGITTARIUS (self.action.mars_sagittarius.v1)
    # =========================================================================
    {
        "sign": "sagittarius",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "expansive_visionary_momentum",
        "action_angle": "initiation",
        "metaphor": "arrow_flight",
        "text": "დაბრკოლებებს ზემოდან გადაახტები: თუ წინ კედელი აღიმართა, დროს მის ნგრევაზე კი არ ხარჯავ, არამედ ისარს პირდაპირ ჰორიზონტს მიღმა ისვრი და ახალ სივრცეს იპყრობ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "uninhibited_candid_pursuit",
        "action_angle": "resistance",
        "metaphor": "open_field_charge",
        "text": "მოქმედებაში მთავარი შენთვის თავისუფლება და დიდი მიზანია: თუ საქმე შთაგაგონებს, წარმოუდგენელი ენთუზიაზმით მირბიხარ წინ და ვერცერთი წვრილმანი შეზღუდვა ვერ გაგაჩერებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "expansive_visionary_momentum",
        "action_angle": "activation",
        "metaphor": "compass_heading",
        "text": "მოქმედებას წვრილმანი გეგმების გარეშე იწყებ: საკმარისია კომპასმა მიმართულება გიჩვენოს და მთელი სვლით მიიწევ წინ. დეტალებს გზადაგზა, მოძრაობაშივე გაარკვევ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 4,
        "depth": "micro",
        "tone": "snarky",
        "angle": "uninhibited_candid_pursuit",
        "action_angle": "pursuit",
        "metaphor": "open_horizon",
        "text": "მიზნისკენ სვლა შენთვის ახალი სივრცის დაპყრობაა: ვერ იტან შეზღუდვებს და ვიწრო ჩარჩოებს — რაც უფრო დიდია მასშტაბი, მით უფრო თავისუფლად და თამამად მოქმედებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 5,
        "depth": "micro",
        "tone": "jester",
        "angle": "expansive_visionary_momentum",
        "action_angle": "execution",
        "metaphor": "long_leap",
        "text": "დაბრკოლებასთან მიახლოებისას არ ჩერდები — პირდაპირ დიდ ნახტომს აკეთებ: თუ გადახტი, ხომ მშვენიერი, ხოლო თუ ვერა, ფრენის პროცესი მაინც სანახაობრივი გამოვა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 6,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "uninhibited_candid_pursuit",
        "action_angle": "tactical_adaptation",
        "metaphor": "wandering_caravan",
        "text": "თუ ერთი გზა ჩაიკეტა, ტრაგედიას არ ქმნი: მომენტალურად ცვლი მარშრუტს და ახალი თავგადასავლისკენ მიემართები — შენთვის მთავარია მოძრაობა არასდროს შეწყდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 7,
        "depth": "medium",
        "tone": "mocking",
        "angle": "restless_overextension",
        "action_angle": "persistence_momentum",
        "metaphor": "wildfire_expedition",
        "text": "შენი მოქმედების სტილი ფართო მასშტაბის კავალერიის შეტევას ჰგავს: შენ გჭირდება სივრცე, გრანდიოზული იდეები და ისეთი ამოცანები, სადაც სამყაროს შეცვლაა საჭირო. წვრილმანი ბიუროკრატია და რუტინული დეტალები შენს ენერგიას მომენტალურად ახრჩობს; შენ გირჩევნია წინ გაიჭრა და პრობლემები გზადაგზა, მოულოდნელი იუმორითა და ოპტიმიზმით მოაგვარო. თუმცა შენი სუსტი წერტილი ზედმეტი გაფანტულობა და უპასუხისმგებლო გადახტომებია: ხშირად ისეთი ენთუზიაზმით იწყებ ახალ თავგადასავალს, რომ ძველი საქმის ბოლო შტრიხების მიყვანა გავიწყდება და გზაში დაუმთავრებელი პროექტების მთელ ველს ტოვებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 8,
        "depth": "medium",
        "tone": "unfiltered",
        "angle": "restless_overextension",
        "action_angle": "blind_spot",
        "metaphor": "galleon_voyage",
        "text": "მოდი პირდაპირ ვთქვათ, როგორ მოქმედებ: შენი მექანიზმი ოკეანეში გაჭრილ დიდ გალეონს ჰგავს, რომელსაც მხოლოდ ზურგის ქარი და გრანდიოზული მიზნები ამოძრავებს. საოცარი სისწრაფით შეგიძლია ხალხის დარაზმვა, ახალი ჰორიზონტების გახსნა და რთული პროექტების ერთი დიდი ნახტომით დაძვრა. შენთვის მოქმედება შთაგონებაა და არა რუტინა. მაგრამ შენი სისუსტე სწორედ ეს მოუსვენარი გაფანტულობაა: როგორც კი საქმე ფინიშის ხაზს უახლოვდება და იწყება წვრილმანი, უინტერესო დეტალების დალაგება, შენ უკვე სხვა კონტინენტისკენ გაქვს გეზი აღებული. ტოვებ დაწყებულ საქმეებს ნახევარ გზაზე მხოლოდ იმიტომ, რომ ახალი იდეა უფრო კაშკაშა ჩანდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 10. CAPRICORN (self.action.mars_capricorn.v1)
    # =========================================================================
    {
        "sign": "capricorn",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "disciplined_architectural_execution",
        "action_angle": "initiation",
        "metaphor": "granite_foundation",
        "text": "მოქმედებას ცივი გათვლით იწყებ: სანამ პირველ ნაბიჯს გადადგამ, უკვე მთელი გეგმა გაქვს გაწერილი. შენი მიზანდასახულობა ქვაზე აშენებული კედელივით მყარი და ურყევია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "authoritative_siege_persistence",
        "action_angle": "resistance",
        "metaphor": "mountain_climber_anchor",
        "text": "დაბრკოლებები შენში პანიკას არასდროს იწვევს: იცი, რომ გამარჯვება დროისა და დისციპლინის საკითხია. მიდიხარ ნაბიჯ-ნაბიჯ, ზედმეტი ემოციების გარეშე და ბოლომდე ასრულებ დაწყებულს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 3,
        "depth": "micro",
        "tone": "conversational",
        "angle": "disciplined_architectural_execution",
        "action_angle": "activation",
        "metaphor": "iron_beam",
        "text": "მოქმედებას რკინის კონსტრუქციასავით აწყობ: სანამ საქმეს დაიწყებ, დარწმუნებული უნდა იყო საყრდენის სიმყარეში. შენი ენერგია ფუჭ ემოციებზე არასდროს იხარჯება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 4,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "authoritative_siege_persistence",
        "action_angle": "pursuit",
        "metaphor": "steep_ridge",
        "text": "ციცაბო მწვერვალის დანახვა შენს ნაბიჯს მხოლოდ ამძაფრებს: რაც უფრო რთულია გზა, მით უფრო უდრეკი ხდება შენი ნება. შენთვის წარმატება დათმენილი დროის საზღაურია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 5,
        "depth": "micro",
        "tone": "jester",
        "angle": "disciplined_architectural_execution",
        "action_angle": "execution",
        "metaphor": "stone_quarry",
        "text": "საქმეს ისე ამუშავებ, თითქოს ქვის კარიერში ბლოკებს თლიდე: ყოველი დარტყმა ზუსტი, მძიმე და აუცილებელია. შენთან იოლი გამოსავლის ძიებას აზრი არ აქვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "authoritative_siege_persistence",
        "action_angle": "tactical_adaptation",
        "metaphor": "winter_march",
        "text": "თუ გარემო პირობები გაუარესდა, ტემპს კი არ ანელებ, არამედ ზამთრის ლაშქრობასავით ყინავ ემოციებს და იგივე ნაბიჯით მიდიხარ ბოლომდე, სანამ სხვები იყინებიან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 7,
        "depth": "medium",
        "tone": "snarky",
        "angle": "rigid_pragmatic_exhaustion",
        "action_angle": "persistence_momentum",
        "metaphor": "heavy_fortress_siege",
        "text": "შენი მოქმედების მექანიზმი კარგად ორგანიზებულ სამხედრო კამპანიას ჰგავს: არანაირი ზედმეტი ხმაური, არანაირი ქარაფშუტული რისკი; ყველაფერი გათვლილია ხანგრძლივ, ეტაპობრივ გამარჯვებაზე. საოცარი უნარი გაქვს გაუძლო რუტინას, დაღლას და მკაცრ პირობებს, ოღონდ დასახულ მწვერვალს მიაღწიო. შენი პროდუქტიულობა სხვებისთვის მისაბაძი მაგალითია. მაგრამ შენი მთავარი პრობლემა ზედმეტი სისასტიკეა საკუთარი თავის მიმართ: ხშირად ცხოვრებას დაუსრულებელ ვალდებულებად აქცევ, ემოციურ გადაღლას უგულებელყოფ და მაშინაც კი ჯიუტად აგრძელებ სიმძიმის თრევას, როცა საქმე უკვე მარტივად შეიძლებოდა მოგვარებულიყო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 8,
        "depth": "medium",
        "tone": "unexpected",
        "angle": "rigid_pragmatic_exhaustion",
        "action_angle": "blind_spot",
        "metaphor": "clockwork_monolith",
        "text": "ვერავინ წარმოიდგენდა, რომ ასეთი ცივი დისციპლინით შესაძლებელი იყო ნებისმიერი კედლის გარღვევა: შენი მოქმედების მექანიზმი გიგანტური საათის მექანიზმს ჰგავს, რომელიც წამიერი გადახრის გარეშე, თანაბარი რიტმით მიიწევს მიზნისკენ. არ გაინტერესებს იოლი გზები და მყისიერი აპლოდისმენტები; შენ აშენებ შედეგს, რომელიც ათწლეულებს გაუძლებს. თუმცა შენი მთავარი მოულოდნელი სისუსტე საკუთარი თავის ულმობელი ექსპლუატაციაა: ხშირად ისე ეჩვევი მუდმივ დაძაბულობასა და მძიმე ტვირთის ზიდვას, რომ მაშინაც კი უარს ამბობ მარტივ გადაწყვეტაზე, როცა საქმე უკვე მოგვარებულია. გგონია, რომ თუ საქმეში უზარმაზარი ტანჯვა არ ჩააქციე, შედეგი ნამდვილი არ არის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 11. AQUARIUS (self.action.mars_aquarius.v1)
    # =========================================================================
    {
        "sign": "aquarius",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "unconventional_systemic_disruption",
        "action_angle": "initiation",
        "metaphor": "circuit_breaker",
        "text": "როცა ყველა ერთ გზას მიჰყვება, შენ ზუსტად საპირისპირო მიმართულებით იწყებ მოქმედებას: შენი ძალა სტანდარტული წესების დამსხვრევაში და სრულიად ახალი ლოგიკის შექმნაშია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 2,
        "depth": "micro",
        "tone": "snarky",
        "angle": "stubborn_ideological_autonomy",
        "action_angle": "resistance",
        "metaphor": "lightning_rod",
        "text": "ბრძანებებს და ზეწოლას ცივი გულგრილობით პასუხობ: ვერავინ გაიძულებს ისე იმოქმედო, როგორც მიღებულია. შენი ნაბიჯები მხოლოდ საკუთარ პრინციპებსა და მომავლის ხედვას ემორჩილება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "unconventional_systemic_disruption",
        "action_angle": "activation",
        "metaphor": "voltage_spike",
        "text": "მოქმედებას მაშინ იწყებ, როცა ძველი მეთოდები ჩიხში შედის: ერთი მოულოდნელი იმპულსით მთელ სისტემას გადატვირთავ და საქმეს ისეთი ლოგიკით აგვარებ, რომელსაც ვერავინ მიხვდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 4,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "stubborn_ideological_autonomy",
        "action_angle": "pursuit",
        "metaphor": "off_grid_beacon",
        "text": "მიზნისკენ სვლა შენთვის საერთო ტრასიდან გადახვევაა: მიდიხარ საკუთარი სიგნალით, დამოუკიდებლად და არაფრის დიდებით არ დაემორჩილები სხვის მიერ დაწესებულ სიჩქარეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 5,
        "depth": "micro",
        "tone": "mocking",
        "angle": "unconventional_systemic_disruption",
        "action_angle": "execution",
        "metaphor": "code_refactor",
        "text": "საქმეს ისე უდგები, როგორც გაჭედილ ალგორითმს: შლი არსებულ წესებს, თავიდან აწყობ ლოგიკას და შედეგს ისეთი მეთოდით დებ, რომელიც სტანდარტულ ჩარჩოებში არ ჯდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 6,
        "depth": "micro",
        "tone": "conversational",
        "angle": "stubborn_ideological_autonomy",
        "action_angle": "tactical_adaptation",
        "metaphor": "paradigm_shift",
        "text": "თუ გზა გადაგიკეტეს, ბრძოლას კი არ იწყებ, არამედ წესებს უცვლი მთელ თამაშს: მოწინააღმდეგეს თავისივე ლოგიკის უაზრობას აჩვენებ და საქმეს გვერდიდან წყვეტ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "contrarian_friction",
        "action_angle": "persistence_momentum",
        "metaphor": "quantum_grid_glitch",
        "text": "შენთვის მოქმედება სისტემის გამოცდაა: როგორც კი ვინმე გეტყვის, რომ რაღაც „ასე კეთდება იმიტომ, რომ წესია“, შენში ავტომატურად ირთვება რევოლუციური მუხტი. არ გხიბლავს ჩვეულებრივი კონკურენცია; შენ ცდილობ თამაშის წესები თავდაყირა დააყენო და პრობლემა ისეთი არასტანდარტული მეთოდით გადაჭრა, რომელსაც ვერავინ წარმოიდგენდა. თუმცა შენი აქილევსის ქუსლი უაზრო სიჯიუტეა: ხანდახან მხოლოდ იმიტომ ეწინააღმდეგები მარტივ, აპრობირებულ გზას, რომ არ გინდა სხვებს დაემსგავსო, და ამ პროტესტში იმდენ დროს ხარჯავ, რომ საქმის რეალური მიზანი სადღაც გზაში იკარგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 8,
        "depth": "medium",
        "tone": "unfiltered",
        "angle": "contrarian_friction",
        "action_angle": "blind_spot",
        "metaphor": "electric_current_network",
        "text": "მოდი პირდაპირ გითხრა, როგორ მუშაობს შენი გონება: შენი მოქმედების მექანიზმი ელექტრულ ქსელს ჰგავს, რომელიც ყოველთვის ყველაზე არასტანდარტულ, მოულოდნელ ტრაექტორიას ირჩევს. როგორც კი დაინახავ, რომ რაღაც მოძველებული წესებით მუშაობს, მომენტალურად გიჩნდება სურვილი სისტემა თავდაყირა დააყენო და ახალი მოდელი შექმნა. შენი იდეები ხშირად დროს უსწრებს და საოცრად ეფექტურია. მაგრამ შენი რეალური სისუსტე პრინციპული სიჯიუტეა: ხანდახან მხოლოდ იმიტომ ამბობ უარს მარტივ და აპრობირებულ გზაზე, რომ ის ყველასთვის გასაგებია. გირჩევნია ველოსიპედი თავიდან გამოიგონო და კვირები დაკარგო, ვიდრე სხვისი გაკვალული ბილიკით გაიარო, რადგან კონფორმიზმი შენთვის ყველაზე დიდი მარცხია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 12. PISCES (self.action.mars_pisces.v1)
    # =========================================================================
    {
        "sign": "pisces",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "permeable_intuitive_flow",
        "action_angle": "initiation",
        "metaphor": "flowing_river",
        "text": "დაბრკოლებას პირდაპირ არ ეჯახები: წყალივით პოულობ უმცირეს ნაპრალს, შეუმჩნევლად გაედინები და მიზანს ისე აღწევ, რომ გზაში არანაირ ხმაურს არ ტოვებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 2,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "indirect_elusive_adaptation",
        "action_angle": "resistance",
        "metaphor": "mist_dissolve",
        "text": "როცა ზეწოლა ძლიერდება, შენ წინააღმდეგობას კი არ უწევ, არამედ ფორმას იცვლი და ნისლივით ქრები: შენი მოუხელთებლობა საუკეთესო თავდაცვა და გამარჯვების სტრატეგიაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "permeable_intuitive_flow",
        "action_angle": "activation",
        "metaphor": "silent_current",
        "text": "მოქმედებას მაშინ ვიწყებ, როცა გარემო თავად იძლევა ნიშანს: არ მჭირდება წინასწარი გეგმები, ინტუიციურ დინებას მივყვები და მიზანთან ზუსტად საჭირო დროს აღმოვჩნდები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 4,
        "depth": "micro",
        "tone": "snarky",
        "angle": "indirect_elusive_adaptation",
        "action_angle": "pursuit",
        "metaphor": "ocean_depth",
        "text": "მიზნისკენ ისე ცურავ, რომ ზედაპირზე ტალღაც კი არ ჩნდება: სანამ სხვები ერთმანეთს ეჯიბრებიან, შენ სიღრმიდან პოულობ გასასვლელს და საქმეს მშვიდად აგვარებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 5,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "permeable_intuitive_flow",
        "action_angle": "execution",
        "metaphor": "permeable_sponge",
        "text": "საქმესთან შეხებისას წინააღმდეგობას არ უწევ გარემოს — უბრალოდ იწოვ სიტუაციას, არბილებ კონფლიქტს და საქმეს ისე ასრულებ, თითქოს ბარიერი საერთოდ არ ყოფილა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 6,
        "depth": "micro",
        "tone": "jester",
        "angle": "indirect_elusive_adaptation",
        "action_angle": "tactical_adaptation",
        "metaphor": "drift_current",
        "text": "თუ წინ კედელი დაგხვდა, მასთან შეჯახებას არ დაიწყებ: მშვიდად დაელოდები, როდის აიწევს წყლის დონე და მას ზემოდან, სრულიად უხმაუროდ გადაუვლი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 7,
        "depth": "medium",
        "tone": "mocking",
        "angle": "passive_paralysis_drift",
        "action_angle": "persistence_momentum",
        "metaphor": "tidal_whirlpool",
        "text": "შენი მოქმედების მექანიზმი ინტუიციურ დინებას ჰგავს: როცა შთაგონებული ხარ, შეგიძლია მთები ისე გადადგა, რომ ფიზიკური დაღლა საერთოდ ვერ იგრძნო — მოქმედებ შემოქმედებითი ტალღით და გარემოს საოცრად ერგები. ვერ იტან უხეშ დირექტივებსა და ხისტ გრაფიკებს; შენი ენერგია მხოლოდ შინაგანი განწყობის დროს მუშაობს. თუმცა შენი მთავარი სისუსტე სწორედ ეს ნისლში გაქცევაა: როცა პირისპირ რთულ, უსიამოვნო კონფლიქტს ეჯახები, მოქმედების ნაცვლად პასიურ დრეიფში გადადიხარ, ილუზიებში იმალები და ელი, რომ პრობლემა თავისით, უსიტყვოდ გაიხსნება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 8,
        "depth": "medium",
        "tone": "unexpected",
        "angle": "passive_paralysis_drift",
        "action_angle": "blind_spot",
        "metaphor": "subterranean_aquifer",
        "text": "ვერასდროს გაიგებ, საიდან გაჩნდება შენი მოქმედების ტალღა: შენი მექანიზმი მიწისქვეშა მდინარეს ჰგავს, რომელიც უხილავად მოძრაობს და ყველაზე გაუვალ კლდეებშიც კი პოულობს გზას. არ გჭირდება პირდაპირი კონფრონტაცია; შენი ძალა გარემოსთან სრულ შერწყმასა და მოუხელთებლობაშია. თუმცა შენი მოულოდნელი სისუსტე გაურკვევლობაში გაქრობაა: როგორც კი საქმე მკაფიო, ხისტ პასუხისმგებლობას და კონკრეტულ ვადებს მოითხოვს, შენ უბრალოდ ნისლში ითქვიფები. მოქმედების ნაცვლად პასიურ დრეიფში გადადიხარ და ელი, რომ პრობლემა თავისით გაიწოვება, რაც ხშირად რეალური შედეგის დაკარგვით მთავრდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
]


def jaccard_similarity(s1: str, s2: str) -> float:
    w1 = set(re.findall(r"\w+", s1.lower()))
    w2 = set(re.findall(r"\w+", s2.lower()))
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def validate_and_build_mars_full() -> list[dict[str, Any]]:
    print("=" * 70)
    print("VALIDATING AND BUILDING FULL MARS CORPUS (96 ASSETS)")
    print("=" * 70)

    # 1. Exact Count Assertions
    assert len(MARS_FULL_RAW_ASSETS) == 96, f"Expected 96 raw assets, found {len(MARS_FULL_RAW_ASSETS)}"

    sign_map = {s[0]: s for s in SIGN_SPECS}
    assets = []
    texts = []
    tone_counts: dict[str, int] = {}
    metaphors_by_sign: dict[str, set[str]] = {s: set() for s in sign_map}
    depth_counts: dict[str, int] = {"micro": 0, "medium": 0, "deep": 0}

    for item in MARS_FULL_RAW_ASSETS:
        sign = item["sign"]
        idx = item["index"]
        depth = item["depth"]
        tone = item["tone"]
        angle = item["angle"]
        action_angle = item["action_angle"]
        metaphor = item["metaphor"]
        text = item["text"].strip()
        quality = item["quality"]

        # Track depth
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

        # Track tone
        tone_counts[tone] = tone_counts.get(tone, 0) + 1

        # Track metaphor
        assert metaphor not in metaphors_by_sign[sign], f"Duplicate metaphor '{metaphor}' in sign {sign}"
        metaphors_by_sign[sign].add(metaphor)

        # Track texts for dup checks
        texts.append(text)

        # Length validation
        char_len = len(text)
        if depth == "micro":
            assert 100 <= char_len <= 250, f"Micro length violation ({char_len} chars) in {sign}_{idx}: '{text}'"
        elif depth == "medium":
            assert 400 <= char_len <= 750, f"Medium length violation ({char_len} chars) in {sign}_{idx}: '{text}'"
        else:
            raise ValueError(f"Invalid depth: {depth}")

        # Forbidden claims
        for pat in FORBIDDEN_CLAIMS:
            assert not re.search(pat, text, re.IGNORECASE), f"Forbidden claim pattern '{pat}' in {sign}_{idx}"

        # Forbidden openings
        for fo in FORBIDDEN_OPENINGS:
            assert not text.startswith(fo), f"Forbidden opening '{fo}' in {sign}_{idx}"

        # Action != Anger Clichés
        for ac in ANGER_CLICHES:
            assert not re.search(ac, text), f"Anger cliché '{ac}' in {sign}_{idx}: '{text}'"

        # No Astrological Jargon in copy
        jargon = scan_for_jargon(text, "ka")
        assert not jargon, f"Astrological jargon {jargon} in {sign}_{idx}: '{text}'"

        # Semantic angle must match contract
        contract_id = f"self.action.mars_{sign}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Missing contract {contract_id}"
        contract = INTERPRETATION_CONTRACTS[contract_id]
        clean_angle = angle.replace("_", " ")
        assert any(angle in ha.replace(" ", "_") or ha in clean_angle for ha in contract.meaning.human_meaning), (
            f"Angle '{angle}' not in contract {contract_id} meaning"
        )

        # Quality Gate validation (all >= 4.0)
        for dim, sc in quality.items():
            assert sc >= 4.0, f"Quality score {dim} = {sc} < 4.0 in {sign}_{idx}"

        element, modality = sign_map[sign][1], sign_map[sign][2]
        variant_key = f"{sign}_action_v{idx:02d}"
        asset_id = f"astrology.{contract_id}.{variant_key}"

        asset_obj = {
            "asset_id": asset_id,
            "interpretation_id": contract_id,
            "variant_key": variant_key,
            "tone": tone,
            "text": text,
            "tags": [
                "body:mars",
                f"sign:{sign}",
                f"element:{element}",
                f"modality:{modality}",
                f"tone:{tone}",
                f"depth:{depth}",
                f"angle:{angle}",
                f"action_angle:{action_angle}",
                f"metaphor:{metaphor}",
                "domain:action",
            ],
            "internal_notes": json.dumps({
                "batch_id": "mars_full_v1",
                "astrological_fact": f"Mars is in {sign.capitalize()}",
                "semantic_contract": contract_id,
                "semantic_angle": angle,
                "action_angle": action_angle,
                "metaphor_family": metaphor,
                "char_length": char_len,
                "quality_scores": quality,
            }, ensure_ascii=False),
            "provenance": {
                "batch_id": "mars_full_v1",
                "interpretation_id": contract_id,
                "body": "mars",
                "sign": sign,
                "element": element,
                "modality": modality,
                "semantic_contract_id": contract_id,
                "semantic_angle": angle,
                "action_angle": action_angle,
                "metaphor_family": metaphor,
                "tone": tone,
                "depth": depth,
                "variant": variant_key,
                "source_inputs": {
                    "mars_sign": sign,
                    "element": element,
                    "modality": modality,
                },
                "quality_gate": {
                    **quality,
                    "status": "passed",
                },
            },
            "archived": False,
            "weight": 1.0,
            "created_at": "2026-09-08T00:00:00Z",
            "updated_at": "2026-09-08T00:00:00Z",
        }
        assets.append(asset_obj)

    # Check for exact duplicates
    assert len(texts) == len(set(texts)), "Exact duplicate found in Mars full texts"

    # Pairwise Jaccard similarity (< 0.85)
    max_sim = 0.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = jaccard_similarity(texts[i], texts[j])
            if sim > max_sim:
                max_sim = sim
            assert sim < 0.85, f"Near-duplicate text detected (Jaccard={sim:.2f}):\n1: {texts[i]}\n2: {texts[j]}"

    # Verify metaphor diversity (at least 8 distinct per sign)
    for s, m_set in metaphors_by_sign.items():
        assert len(m_set) == 8, f"Sign {s} must have exactly 8 distinct metaphor families, got {len(m_set)}"

    # Tone counts assertion: exactly 12 per voice!
    for t, cnt in tone_counts.items():
        assert cnt == 12, f"Voice '{t}' must have exactly 12 assets, got {cnt}"

    print(f"SUCCESS: Generated and validated exactly {len(assets)} Mars full assets.")
    print(f"  - Micro: {depth_counts['micro']}")
    print(f"  - Medium: {depth_counts['medium']}")
    print(f"  - Deep: {depth_counts['deep']}")
    print(f"Peak pairwise Jaccard similarity: {max_sim:.3f}")
    print("Tone Distribution across full batch (target: exactly 12 each):")
    for t, cnt in sorted(tone_counts.items()):
        print(f"  - {t}: {cnt}")

    # Output file
    out_path = root_dir / "backend" / "app" / "interpretation" / "data" / "mars_corpus.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {out_path}")
    return assets


if __name__ == "__main__":
    validate_and_build_mars_full()
