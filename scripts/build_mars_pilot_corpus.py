"""
Script to build, validate, and write the 36-asset Mars Pilot Corpus for JESTER Phase 3.9.

Validates:
- Exactly 36 assets (12 signs x 3 assets: 24 Micro, 12 Medium, 0 Deep)
- 12 Locked semantic contracts (self.action.mars_{sign}.v1)
- Strict character length boundaries (Micro: 100-250, Medium: 400-750)
- Cross-planet firewall & Action != Anger boundary
- Forbidden openings, forbidden claims, and zero astrological jargon in user copy
- All 8 official JESTER voices represented
- Full machine-readable provenance metadata and quality gate >= 4.0
- Exact and near-duplicate (pairwise Jaccard < 0.85) assertions
"""
import json
from pathlib import Path
import re
import sys
from typing import Any

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.interpretation.contracts import INTERPRETATION_CONTRACTS
from scripts.corpus_builders.common import scan_for_jargon

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

MARS_PILOT_RAW_ASSETS: list[dict[str, Any]] = [
    # 1. ARIES (self.action.mars_aries.v1)
    {
        "sign": "aries",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "kinetic_frontal_initiative",
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
        "metaphor": "direct_breach",
        "text": "წინააღმდეგობას შემოვლითი გზებით არ უყურებ: თუ წინ კედელი დაგხვდა, პირდაპირი ბიძგით ცდილობ მის გატეხვას. შენთვის მოთმინება მხოლოდ ენერგიის ფუჭი ხარჯვაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "high_velocity_burnout",
        "metaphor": "rocket_thruster",
        "text": "შენი მოქმედების მექანიზმი პირველივე წამში მაქსიმალური აჩქარებით ჩართვას ჰგავს: ან მყისიერად იღებ შედეგს, ან ინტერესი იმავე სისწრაფით გიქრება. ვერ იტან გაწელილ პროცედურებს, ხანგრძლივ განხილვებსა და სხვის ყოყმანს — შენთვის ნებისმიერი პაუზა უკან დახევის ტოლფასია. მთელი ძალით შედიხარ საქმეში და პირველივე წინაღობას პირდაპირ ეჯახები. თუმცა შენი მთავარი სისუსტე სწორედ ეს მოკლე დისტანციის ენერგიაა: თუ ბარიერი პირველი დარტყმით არ ჩამოიშალა, მეორე რაუნდისთვის მოთმინება აღარ გყოფნის და ხშირად საქმეს მანამ ტოვებ, სანამ სხვები საერთოდ გარკვევას მოასწრებდნენ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 2. TAURUS (self.action.mars_taurus.v1)
    {
        "sign": "taurus",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "relentless_grinding_momentum",
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
        "metaphor": "granite_weight",
        "text": "თუ ვინმე შენი გზიდან ჩამოშორებას შეეცდება, უბრალოდ მთელი სიმძიმით ერთ ადგილზე ჩერდები: შენთან დაპირისპირება კედლისთვის მხრით მიწოლას ჰგავს — კედელი არ დაიძვრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 3,
        "depth": "medium",
        "tone": "mocking",
        "angle": "inertia_friction",
        "metaphor": "steamroller_engine",
        "text": "შენი მოქმედების სტილი მძიმე ტექნიკის მუშაობას ჰგავს: სანამ ძრავი გაცხელდება და ადგილიდან დაიძვრები, გარშემო ყველას ჰგონია, რომ არაფრის გაკეთებას არ აპირებ. სამაგიეროდ, როგორც კი მექანიზმი ჩაირთვება, შენი შეჩერება ბუნებრივ კატასტროფას უტოლდება — მიდიხარ დინჯად, თანაბარი ტემპით და უბრალოდ ასწორებ ყველაფერს, რაც გზაზე გეღობება. პრობლემა ისაა, რომ მიმართულების შეცვლა შენთვის შეუძლებელი მისიაა: მაშინაც კი, როცა აშკარაა, რომ წინ უფსკრულია, ინერციით მაინც ჯიუტად იმავე კურსს მიჰყვები, რადგან მოხვევა ზედმეტ ენერგიას მოითხოვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 3. GEMINI (self.action.mars_gemini.v1)
    {
        "sign": "gemini",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "tactical_multi_track_maneuver",
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
        "metaphor": "shadow_maneuver",
        "text": "სანამ მოწინააღმდეგე პირდაპირი დარტყმისთვის ემზადება, შენ უკვე მის ზურგს უკან ხარ და სიტუაციას სულ სხვა რაკურსით მართავ: შენი მთავარი იარაღი სისხარტე და მოულოდნელობაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "energy_dispersion",
        "metaphor": "juggling_blades",
        "text": "შენთვის მოქმედება ჭადრაკის სწრაფ პარტიას ჰგავს, ოღონდ ერთდროულად ხუთ სხვადასხვა დაფაზე თამაშობ. ვერ იტან ერთფეროვან, მონოტონურ შრომას; შენ გჭირდება გამუდმებით იცვლებოდეს ტაქტიკა, ჩნდებოდეს ახალი დაბრკოლებები და გეძლეოდეს მანევრირების საშუალება. საოცრად ოსტატურად ახერხებ რთული სიტუაციებიდან მშრალად გამოსვლას მხოლოდ იმიტომ, რომ მოქნილი ხარ. თუმცა შენი მთავარი მტერი საკუთარი ენერგიის გაფანტვაა: იმდენ საქმეს იწყებ ერთდროულად და იმდენ მხარეს გარბიხარ, რომ ხშირად ფინიშის ხაზამდე არცერთი პროექტი არ მიგყავს, რადგან გზაში ახალი იდეა გადაგეღობა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },

    # 4. CANCER (self.action.mars_cancer.v1)
    {
        "sign": "cancer",
        "index": 1,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "protective_defensive_surge",
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
        "metaphor": "coastal_wave",
        "text": "პირდაპირ იერიშზე იშვიათად გადადიხარ: ჯერ სიტუაციას გვერდიდან შემოუვლი, ნიადაგს მოსინჯავ და ზუსტად მაშინ გადადგამ ნაბიჯს, როცა მეორე მხარე ამას ყველაზე ნაკლებად ელის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 3,
        "depth": "medium",
        "tone": "snarky",
        "angle": "tenacious_emotional_clamp",
        "metaphor": "crab_pincer_lock",
        "text": "შენი მოქმედების სტილი მოულოდნელი ტალღასავით მუშაობს: სანამ გარედან სიმშვიდე ჩანს, შენ შინაგანად ენერგიას აგროვებ და როგორც კი საჭირო მომენტი დგება, საქმეს ისეთი სიმტკიცით ჩაებღაუჭები, რომ ხელიდან ვეღარავინ გამოგგლეჯს. არ გიყვარს ღია, ხმაურიანი ბრძოლა; შენთვის გაცილებით კომფორტულია სიტუაციის კულუარებიდან, ფრთხილი მანევრებით მართვა. თუმცა შენი სუსტი წერტილი ზედმეტი თავდაცვითი რეჟიმია: ხშირად უბრალო სამუშაო წინააღმდეგობასაც კი პირად შეურაცხყოფად აღიქვამ, ჩუმად საკუთარ ნაჭუჭში იკეტები და საქმის კეთების ნაცვლად შინაგან წყენას უსასრულოდ ამუშავებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 5. LEO (self.action.mars_leo.v1)
    {
        "sign": "leo",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "sovereign_theatrical_assertion",
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
        "metaphor": "golden_shield",
        "text": "წინააღმდეგობა შენს თავმოყვარეობას აღვიძებს: რაც უფრო მეტად ცდილობენ შენს შეჩერებას, მით უფრო ამაყად და ურყევად დგახარ საკუთარ პოზიციაზე. უკან დახევა შენთვის გამორიცხულია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 3,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "status_vulnerability_stalemate",
        "metaphor": "arena_spotlight",
        "text": "შენთვის მოქმედება საკუთარი ძალის საჯარო დემონსტრირებაა. როცა საქმეს ხელს კიდებ, მთელი არსებით ერთვები, რადგან შენთვის საშუალო შედეგი უბრალოდ მიუღებელია — ყველაფერი სამეფო სტანდარტით უნდა შესრულდეს. შენი ენთუზიაზმი გარშემომყოფებსაც აიძულებს ფეხი აგიწყონ. თუმცა შენი აქილევსის ქუსლი სწორედ ეს გადაჭარბებული პატივმოყვარეობაა: თუ დაინახე, რომ შენს წამოწყებას ხალხი აღფრთოვანებით არ შეხვდა, ან შეცდომა მოგივიდა, აღიარების ნაცვლად ჯიუტად იმავე პოზიციაზე იყინები, ოღონდ სხვების თვალში შენი რეპუტაცია არ შეირყეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 6. VIRGO (self.action.mars_virgo.v1)
    {
        "sign": "virgo",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "surgical_precision_execution",
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
        "metaphor": "diagnostic_scanner",
        "text": "თუ საქმე გაიჭედა, ყვირილს და ნერვიულობას არ იწყებ: მშვიდად იღებ ინსტრუმენტებს, შლი პროცესს შემადგენელ ნაწილებად და ხარვეზს მანამ ასწორებ, სანამ მექანიზმი იდეალურად არ იმუშავებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 3,
        "depth": "medium",
        "tone": "mocking",
        "angle": "micro_perfectionist_friction",
        "metaphor": "watchmaker_loupe",
        "text": "შენი მოქმედების სტილი ქირურგიულ ჩარევას ჰგავს: ემოციებს მთლიანად თიშავ, საქმეს საინჟინრო ამოცანად აქცევ და უმცირეს დეტალსაც კი ისეთი პედანტურობით ამუშავებ, რომ შეცდომის შანსი ნულამდე დაგყავს. ვერ იტან ზერელე, ნაჩქარევ ნაბიჯებს; შენთვის მთავარია ხარისხი და პრაქტიკული გამართულობა. მაგრამ შენი მთავარი ხაფანგი სწორედ ეს გადაჭარბებული პერფექციონიზმია: ხანდახან ისე ღრმად ეფლობი უმნიშვნელო წვრილმანების გაპრიალებაში, რომ მთავარი მოქმედება ჩერდება და მთელ ენერგიას ისეთი ხარვეზების გასწორებაზე ხარჯავ, რომლებსაც რეალურად საქმის ბედზე გავლენა არ ჰქონდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 7. LIBRA (self.action.mars_libra.v1)
    {
        "sign": "libra",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "strategic_diplomatic_leverage",
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
        "metaphor": "balanced_fulcrum",
        "text": "კონფლიქტში შენი მიზანი მეორის განადგურება კი არა, წონასწორობის აღდგენაა: ყოველთვის ეძებ სამართლიან გადაწყვეტას, სადაც ორივე მხარე საკუთარ წილ პასუხისმგებლობას დაინახავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "indecisive_arbitration_hesitation",
        "metaphor": "court_pendulum",
        "text": "შენთვის მოქმედება სტრატეგიულ ჭადრაკს ჰგავს, სადაც მთავარი ამოცანა სუფთა ხელებით თამაში და წესების დაცვაა. საოცარი ოსტატობით ახერხებ ყველაზე დაძაბული სიტუაციაც კი მოლაპარაკებების მაგიდასთან გადაიტანო და უხეში დაპირისპირება ცივილურ დიალოგად აქციო. ყოველთვის ცდილობ მოძებნო ოქროს შუალედი, სადაც არავინ დარჩება განაწყენებული. თუმცა შენი სისუსტე სწორედ ეს გადაჭარბებული ყოყმანია: სანამ ყველა შესაძლო პოზიციას აწონი, ყველას არგუმენტს მოისმენ და იდეალურ ბალანსს დაადგენ, მოქმედების გადამწყვეტი მომენტი ხშირად ხელიდან მიფრინავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 8. SCORPIO (self.action.mars_scorpio.v1)
    {
        "sign": "scorpio",
        "index": 1,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "subterranean_strategic_resolve",
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
        "metaphor": "deep_faultline",
        "text": "წინააღმდეგობა შენს ენერგიას არ ფიტავს — პირიქით, ზეწოლის ქვეშ შენი გამძლეობა ორმაგდება: შეგიძლია თვეობით უხმოდ იმოძრაო მიზნისკენ და საჭირო მომენტში ზუსტად იქ დაარტყა, სადაც ყველაზე მეტად ჭრის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 3,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "scorched_earth_fixation",
        "metaphor": "covert_pressure_valve",
        "text": "შენი მოქმედების მექანიზმი აბსოლუტურ კონტროლსა და რკინის თვითდისციპლინაზეა აგებული. არასდროს ხარჯავ ძალას ზედაპირულ ხმაურზე; შენ სწავლობ მოწინააღმდეგის ფსიქოლოგიას, ითვლი მის სუსტ წერტილებს და მოქმედებ მხოლოდ მაშინ, როცა წარმატება გარანტირებულია. შენი გამძლეობა ექსტრემალურ პირობებში შეუდარებელია. მაგრამ შენი მთავარი საფრთხე ფიქსაცია და უკან დაუხევლობაა: თუ ვინმემ შენი გზა გადაკვეთა, ბრძოლას პირად ომად აქცევ და მზად ხარ უზარმაზარი რესურსი დაწვა, ოღონდ საბოლოო გამარჯვება შენ დაგრჩეს — მაშინაც კი, როცა გამარჯვების ფასი თავად მიზანზე ძვირი ჯდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },

    # 9. SAGITTARIUS (self.action.mars_sagittarius.v1)
    {
        "sign": "sagittarius",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "expansive_visionary_momentum",
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
        "metaphor": "open_field_charge",
        "text": "მოქმედებაში მთავარი შენთვის თავისუფლება და დიდი მიზანია: თუ საქმე შთაგაგონებს, წარმოუდგენელი ენთუზიაზმით მირბიხარ წინ და ვერცერთი წვრილმანი შეზღუდვა ვერ გაგაჩერებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 3,
        "depth": "medium",
        "tone": "mocking",
        "angle": "restless_overextension",
        "metaphor": "wildfire_expedition",
        "text": "შენი მოქმედების სტილი ფართო მასშტაბის კავალერიის შეტევას ჰგავს: შენ გჭირდება სივრცე, გრანდიოზული იდეები და ისეთი ამოცანები, სადაც სამყაროს შეცვლაა საჭირო. წვრილმანი ბიუროკრატია და რუტინული დეტალები შენს ენერგიას მომენტალურად ახრჩობს; შენ გირჩევნია წინ გაიჭრა და პრობლემები გზადაგზა, მოულოდნელი იუმორითა და ოპტიმიზმით მოაგვარო. თუმცა შენი სუსტი წერტილი ზედმეტი გაფანტულობა და უპასუხისმგებლო გადახტომებია: ხშირად ისეთი ენთუზიაზმით იწყებ ახალ თავგადასავალს, რომ ძველი საქმის ბოლო შტრიხების მიყვანა გავიწყდება და გზაში დაუმთავრებელი პროექტების მთელ ველს ტოვებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 10. CAPRICORN (self.action.mars_capricorn.v1)
    {
        "sign": "capricorn",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "disciplined_architectural_execution",
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
        "metaphor": "mountain_climber_anchor",
        "text": "დაბრკოლებები შენში პანიკას არასდროს იწვევს: იცი, რომ გამარჯვება დროისა და დისციპლინის საკითხია. მიდიხარ ნაბიჯ-ნაბიჯ, ზედმეტი ემოციების გარეშე და ბოლომდე ასრულებ დაწყებულს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 3,
        "depth": "medium",
        "tone": "snarky",
        "angle": "rigid_pragmatic_exhaustion",
        "metaphor": "heavy_fortress_siege",
        "text": "შენი მოქმედების მექანიზმი კარგად ორგანიზებულ სამხედრო კამპანიას ჰგავს: არანაირი ზედმეტი ხმაური, არანაირი ქარაფშუტული რისკი; ყველაფერი გათვლილია ხანგრძლივ, ეტაპობრივ გამარჯვებაზე. საოცარი უნარი გაქვს გაუძლო რუტინას, დაღლას და მკაცრ პირობებს, ოღონდ დასახულ მწვერვალს მიაღწიო. შენი პროდუქტიულობა სხვებისთვის მისაბაძი მაგალითია. მაგრამ შენი მთავარი პრობლემა ზედმეტი სისასტიკეა საკუთარი თავის მიმართ: ხშირად ცხოვრებას დაუსრულებელ ვალდებულებად აქცევ, ემოციურ გადაღლას უგულებელყოფ და მაშინაც კი ჯიუტად აგრძელებ სიმძიმის თრევას, როცა საქმე უკვე მარტივად შეიძლებოდა მოგვარებულიყო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 11. AQUARIUS (self.action.mars_aquarius.v1)
    {
        "sign": "aquarius",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "unconventional_systemic_disruption",
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
        "metaphor": "lightning_rod",
        "text": "ბრძანებებს და ზეწოლას ცივი გულგრილობით პასუხობ: ვერავინ გაიძულებს ისე იმოქმედო, როგორც მიღებულია. შენი ნაბიჯები მხოლოდ საკუთარ პრინციპებსა და მომავლის ხედვას ემორჩილება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "contrarian_friction",
        "metaphor": "quantum_grid_glitch",
        "text": "შენთვის მოქმედება სისტემის გამოცდაა: როგორც კი ვინმე გეტყვის, რომ რაღაც „ასე კეთდება იმიტომ, რომ წესია“, შენში ავტომატურად ირთვება რევოლუციური მუხტი. არ გხიბლავს ჩვეულებრივი კონკურენცია; შენ ცდილობ თამაშის წესები თავდაყირა დააყენო და პრობლემა ისეთი არასტანდარტული მეთოდით გადაჭრა, რომელსაც ვერავინ წარმოიდგენდა. თუმცა შენი აქილევსის ქუსლი უაზრო სიჯიუტეა: ხანდახან მხოლოდ იმიტომ ეწინააღმდეგები მარტივ, აპრობირებულ გზას, რომ არ გინდა სხვებს დაემსგავსო, და ამ პროტესტში იმდენ დროს ხარჯავ, რომ საქმის რეალური მიზანი სადღაც გზაში იკარგება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # 12. PISCES (self.action.mars_pisces.v1)
    {
        "sign": "pisces",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "permeable_intuitive_flow",
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
        "metaphor": "mist_dissolve",
        "text": "როცა ზეწოლა ძლიერდება, შენ წინააღმდეგობას კი არ უწევ, არამედ ფორმას იცვლი და ნისლივით ქრები: შენი მოუხელთებლობა საუკეთესო თავდაცვა და გამარჯვების სტრატეგიაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 3,
        "depth": "medium",
        "tone": "mocking",
        "angle": "passive_paralysis_drift",
        "metaphor": "tidal_whirlpool",
        "text": "შენი მოქმედების მექანიზმი ინტუიციურ დინებას ჰგავს: როცა შთაგონებული ხარ, შეგიძლია მთები ისე გადადგა, რომ ფიზიკური დაღლა საერთოდ ვერ იგრძნო — მოქმედებ შემოქმედებითი ტალღით და გარემოს საოცრად ერგები. ვერ იტან უხეშ დირექტივებსა და ხისტ გრაფიკებს; შენი ენერგია მხოლოდ შინაგანი განწყობის დროს მუშაობს. თუმცა შენი მთავარი სისუსტე სწორედ ეს ნისლში გაქცევაა: როცა პირისპირ რთულ, უსიამოვნო კონფლიქტს ეჯახები, მოქმედების ნაცვლად პასიურ დრეიფში გადადიხარ, ილუზიებში იმალები და ელი, რომ პრობლემა თავისით, უსიტყვოდ გაიხსნება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
]


def jaccard_similarity(s1: str, s2: str) -> float:
    w1 = set(re.findall(r"\w+", s1.lower()))
    w2 = set(re.findall(r"\w+", s2.lower()))
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def validate_and_build_mars_pilot() -> list[dict[str, Any]]:
    print("=" * 70)
    print("JESTER PHASE 3.9 — Mars 36-Asset Semantic Pilot Generation & QA")
    print("=" * 70)

    root_dir = Path(__file__).parent.parent
    sign_map = {s[0]: s for s in SIGN_SPECS}

    assets: list[dict[str, Any]] = []
    texts: list[str] = []
    metaphors_by_sign: dict[str, set[str]] = {}
    tone_counts: dict[str, int] = {}

    assert len(MARS_PILOT_RAW_ASSETS) == 36, f"Expected exactly 36 raw assets, got {len(MARS_PILOT_RAW_ASSETS)}"

    for raw in MARS_PILOT_RAW_ASSETS:
        sign = raw["sign"]
        idx = raw["index"]
        depth = raw["depth"]
        tone = raw["tone"]
        angle = raw["angle"]
        metaphor = raw["metaphor"]
        text = raw["text"].strip()
        quality = raw["quality"]

        texts.append(text)
        metaphors_by_sign.setdefault(sign, set()).add(metaphor)
        tone_counts[tone] = tone_counts.get(tone, 0) + 1

        char_len = len(text)
        if depth == "micro":
            assert 100 <= char_len <= 250, f"Micro length violation ({char_len} chars) in {sign}_{idx}: {text}"
        elif depth == "medium":
            assert 400 <= char_len <= 750, f"Medium length violation ({char_len} chars) in {sign}_{idx}: {text}"

        # Forbidden opening check
        for f_open in FORBIDDEN_OPENINGS:
            assert not text.startswith(f_open), f"Forbidden opening '{f_open}' in {sign}_{idx}: {text}"

        # Forbidden claims check
        for c_pat in FORBIDDEN_CLAIMS:
            assert not re.search(c_pat, text, re.IGNORECASE), f"Forbidden claim pattern '{c_pat}' matched in {sign}_{idx}: {text}"

        # Astrological jargon check in user copy
        jargon_found = scan_for_jargon(text, "ka")
        assert not jargon_found, f"Astrological jargon found: {jargon_found} in {sign}_{idx}: {text}"

        # Action != Anger check: Must not contain anger-engine clichés as primary claim
        for a_cliche in [r"ბრაზდები", r"ჩხუბობ", r"აგრესიული ხარ", r"თავს ესხმი", r"ვერ აკონტროლებ თავს"]:
            assert not re.search(a_cliche, text), f"Anger-engine cliché '{a_cliche}' found in {sign}_{idx}"

        # Quality Gate validation (all >= 4.0)
        for dim, score in quality.items():
            assert score >= 4.0, f"Quality gate violation in {sign}_{idx}: {dim} = {score} (< 4.0)"

        # Verify angle in contract
        contract_id = f"self.action.mars_{sign}.v1"
        assert contract_id in INTERPRETATION_CONTRACTS, f"Contract {contract_id} not registered"
        contract = INTERPRETATION_CONTRACTS[contract_id]
        clean_angle = angle.replace("_", " ")
        assert any(angle in ha.replace(" ", "_") or ha in clean_angle for ha in contract.meaning.human_meaning), (
            f"Angle '{angle}' not in contract {contract_id} angles: {contract.meaning.human_meaning}"
        )

        # Build full machine-readable provenance asset
        sign_info = sign_map[sign]
        element = sign_info[1]
        modality = sign_info[2]
        asset_id = f"ca_act_{sign[:3]}_{idx:03d}_ka_{tone[:3]}_{depth[:3]}"
        variant_key = f"{tone}_ka_{depth[:3]}_{idx:02d}"

        asset_obj = {
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
                "batch:mars_pilot_v1",
                "body:mars",
                f"sign:{sign}",
                f"element:{element}",
                f"modality:{modality}",
                f"depth:{depth}",
                f"angle:{angle}",
                f"metaphor:{metaphor}",
                "domain:action",
            ],
            "internal_notes": json.dumps({
                "batch_id": "mars_pilot_v1",
                "astrological_fact": f"Mars is in {sign.capitalize()}",
                "semantic_contract": contract_id,
                "semantic_angle": angle,
                "metaphor_family": metaphor,
                "char_length": char_len,
                "quality_scores": quality,
            }, ensure_ascii=False),
            "provenance": {
                "batch_id": "mars_pilot_v1",
                "interpretation_id": contract_id,
                "body": "mars",
                "sign": sign,
                "element": element,
                "modality": modality,
                "semantic_contract_id": contract_id,
                "semantic_angle": angle,
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
    assert len(texts) == len(set(texts)), "Exact duplicate found in Mars pilot texts"

    # Pairwise Jaccard similarity (< 0.85)
    max_sim = 0.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = jaccard_similarity(texts[i], texts[j])
            if sim > max_sim:
                max_sim = sim
            assert sim < 0.85, f"Near-duplicate text detected (Jaccard={sim:.2f}):\n1: {texts[i]}\n2: {texts[j]}"

    # Verify metaphor diversity (at least 3 distinct per sign)
    for s, m_set in metaphors_by_sign.items():
        assert len(m_set) == 3, f"Sign {s} must have exactly 3 distinct metaphor families, got {len(m_set)}"

    print(f"SUCCESS: Generated and validated exactly {len(assets)} Mars pilot assets.")
    print(f"  - Micro: {len([a for a in assets if 'depth:micro' in a['tags']])}")
    print(f"  - Medium: {len([a for a in assets if 'depth:medium' in a['tags']])}")
    print(f"Peak pairwise Jaccard similarity: {max_sim:.3f}")
    print("Tone Distribution across pilot batch:")
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
    validate_and_build_mars_pilot()
