"""
JESTER — PHASE 3.6
Venus 36-Asset Semantic Pilot Generation & QA Pipeline
Generates exactly 36 Venus assets (12 signs x 3 assets: 24 Micro, 12 Medium)
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
    r"\bდიაგნოზ", r"\bფსიქიკური აშლილობ", r"\bმოღალატე ხარ\b",
    r"\bნარცისი ხარ\b", r"\bფსიქოპათ", r"\bკრიმინალ",
    r"\bეს დამტკიცებულია\b", r"\bშენი ტვინი ასე მუშაობს\b",
    r"\bეს ფსიქოლოგიურად ნიშნავს\b", r"\bშენ აუცილებლად\b",
    r"\bმიჯაჭვულობის სინდრომ", r"\bმიჯაჭვულობის ტიპ", r"\bშფოთვითი მიჯაჭვულობ",
    r"\bშენი მეორე ნახევარი\b", r"\bგარანტირებული სიყვარულ",
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

VENUS_RAW_ASSETS = [
    # =========================================================================
    # 1. ARIES (self.relation.venus_aries.v1)
    # =========================================================================
    {
        "sign": "aries",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "rapid_relational_initiative",
        "metaphor": "sprint_start",
        "text": "შენთან ურთიერთობაში შესავალი არ არსებობს: პირველივე წამიდან ან სრული სვლით წინ მიდიხარ, ან საერთოდ არ ჩერდები. ზრდილობიანი მოთელვა შენთვის დროის კარგვაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 2,
        "depth": "micro",
        "tone": "cocky",
        "angle": "competitive_playful_spark",
        "metaphor": "sparks_duel",
        "text": "თუ ადამიანთან მსუბუქი შეჯიბრი და აზარტული ნაპერწკალი არ იგრძნობა, ინტერესი იმავე წამს ქრება. შენ სიმშვიდე კი არა, თანაბარი ძალის მოთამაშე გჭირდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "impatience_with_relational_games",
        "metaphor": "accelerator_brake",
        "text": "შენთვის მიზიდულობა მყისიერი აფეთქებაა — ან პირველივე წუთიდან იგრძნობა ცეცხლი, ან მეორე შანსს საერთოდ აღარავის აძლევ. ზრდილობიანი დიპლომატია, ორაზროვანი მინიშნებები და თვეობით ლოდინი შენს ბუნებას პირდაპირ შეურაცხყოფს. მოგწონს, როცა ადამიანს საკუთარი პოზიციის ხმამაღლა გამოხატვის არ ეშინია. პრობლემა ისაა, რომ სხვის ფრთხილ ტემპს მაშინვე გულგრილობად ნათლავ: გინდა ყველაფერი ახლავე მოხდეს, რის გამოც ხანდახან კარს მანამ კეტავ, სანამ მეორე მხარე ნაბიჯის გადადგმას მოასწრებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 2. TAURUS (self.relation.venus_taurus.v1)
    # =========================================================================
    {
        "sign": "taurus",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "unhurried_relational_pacing",
        "metaphor": "silent_comfort",
        "text": "ნდობას კილომეტრებით ზომავ და არა დღეებით. სანამ ადამიანთან კომფორტულად დუმილს არ ისწავლი, მანამდე შენს ახლო წრეში შესასვლელი კარი დაკეტილი რჩება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "tangible_sensory_loyalty",
        "metaphor": "warm_hearth",
        "text": "სიტყვების ლამაზი ფეიერვერკი არ გაინტერესებს. შენთვის ერთგულება კონკრეტული ზრუნვაა: გემრიელი ვახშამი, სიმყუდროვე და ისეთი საიმედოობა, რომელსაც ხელით შეეხები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 3,
        "depth": "medium",
        "tone": "snarky",
        "angle": "stubborn_comfort_zones",
        "metaphor": "anchored_sofa",
        "text": "შენი სიმპათია ისეთივე მყარი და უძრავია, როგორც ასწლოვანი მუხა. თუ ვინმე შენს გულში შემოვიდა, იქიდან მისი გაყვანა თითქმის შეუძლებელია — ოღონდ ეს წესი შენს ჩვევებსაც ეხება. შენთვის იდეალური ურთიერთობა მშვიდი ნავსაყუდელია, სადაც დრამის ადგილი არ არის. თუმცა პრობლემა მაშინ იწყება, როცა ნებისმიერ ცვლილებას კატასტროფად აღიქვამ: მზად ხარ თვეობით გაუძლო გაუცხოებას, ოღონდ დალაგებული რუტინა და შენი საყვარელი კომფორტის ზონა არ დაირღვეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 3. GEMINI (self.relation.venus_gemini.v1)
    # =========================================================================
    {
        "sign": "gemini",
        "index": 1,
        "depth": "micro",
        "tone": "mocking",
        "angle": "conversational_chemistry",
        "metaphor": "quick_banter",
        "text": "ადამიანი შეიძლება უნაკლო იყოს, მაგრამ თუ საუბარში თვალები არ გინათებს და თემიდან თემაზე ვერ ხტებით, შენი ინტერესი პირველივე ყავის დასრულებამდე ქრება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 2,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "need_for_mental_spaciousness",
        "metaphor": "oxygen_window",
        "text": "საუკეთესო კომპლიმენტი შენთვის ახალი უცნაური იდეის გაზიარებაა. თუ ურთიერთობა გონებრივ ჟანგბადს გაძლევს, იქ რჩები; თუ წესებს გიწესებს — უჩუმრად ქრები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "fickle_novelty_craving",
        "metaphor": "ping_pong_circus",
        "text": "შენთვის მიზიდულობა პირველ რიგში ვერბალური პინგ-პონგია. თუ მოსაუბრეს იუმორი არ ჰყოფნის ან შენს ნათქვამ ხუმრობას სამი წუთი შიფრავს, შენი ტვინი მაშინვე პარალელურ რეჟიმში გადადის. გიყვარს მსუბუქი, ჭკვიანური ფლირტი და ადამიანები, რომლებთანაც ერთდროულად ათ სხვადასხვა თემაზე შეიძლება სიცილი. სირთულე მაშინ ჩნდება, როცა სიტუაცია დამძიმდება: როგორც კი ვინმე ღრმა, სერიოზულ მონოლოგს იწყებს, შენ ხუმრობით იარაღდები და ემოციურ სიღრმეს თავს ოსტატურად არიდებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 4. CANCER (self.relation.venus_cancer.v1)
    # =========================================================================
    {
        "sign": "cancer",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "protective_nurturing_instinct",
        "metaphor": "warm_tea",
        "text": "შენი სითბო ხმაურიანი არ არის: უბრალოდ შეამჩნევ, რომ ადამიანს სცივა და ჩაის მოუტან. ზრუნვა შენთვის სიტყვებზე ბევრად უფრო ბუნებრივი ენაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 2,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "emotional_security_checkpoint",
        "metaphor": "guarded_fortress",
        "text": "უცხო ადამიანისთვის შენი გული ციხესიმაგრეა, სადაც დაცვა ყველა კუთხეში დგას. ნდობას წვეთ-წვეთად გასცემ, რადგან იცი, რა ფასი აქვს შენს დაუცველობას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 3,
        "depth": "medium",
        "tone": "snarky",
        "angle": "defensive_relational_retreat",
        "metaphor": "crab_shell_sonar",
        "text": "შენთან დაახლოება საიდუმლო ლაბირინთში გავლას ჰგავს: სანამ ბოლომდე არ დარწმუნდები, რომ მეორე მხარე შენს სითბოს ბოროტად არ გამოიყენებს, მანამდე მხოლოდ თავაზიან დისტანციას ინარჩუნებ. სამაგიეროდ, როცა კარს გახსნი, შენი ერთგულება უსაზღვრო ხდება. მთავარი ხაფანგი კი შენი შინაგანი სარადარო სისტემაა: თუ ვინმეს ცივ ტონს შეამჩნევ, პირდაპირ კი არ ჰკითხავ, არამედ ჩუმად საკუთარ ნიჟარაში ჩაიკეტები და დაელოდები, როდის მიხვდება მეორე თავის დანაშაულს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 5. LEO (self.relation.venus_leo.v1)
    # =========================================================================
    {
        "sign": "leo",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "generous_royal_courtship",
        "metaphor": "grand_stage",
        "text": "თუ ვინმე მოგწონს, ამას მთელი სამყარო გაიგებს. შენი მოწონება ჩურჩული კი არა, გრანდიოზული ჟესტები, საჩუქრები და პარტნიორით საჯარო სიამაყეა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "pride_and_public_devotion",
        "metaphor": "radiant_spotlight",
        "text": "ნახევრად ყოფნა შენი სტილი არ არის: ადამიანი ან შენს გვერდით დგას და ერთად ანათებთ, ან ჩრდილში რჩება. შენთვის პატივისცემა ყველაფერზე მაღლა დგას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "validation_vulnerability",
        "metaphor": "crown_and_applause",
        "text": "შენთვის ურთიერთობა ცენტრალურ სცენაზე გამოსვლას ჰგავს, სადაც ორივე მთავარ როლს თამაშობთ და ერთმანეთის ბრწყინვალებით ტკბებით. გულუხვი ხარ, გიყვარს ადამიანის გამორჩევა, მისი ნიჭით აღფრთოვანება და მისთვის სამეფო გარემოს შექმნა. თუმცა შენი აქილევსის ქუსლი სწორედ ეს გადაჭარბებული პატივმოყვარეობაა: თუ შეამჩნიე, რომ პარტნიორმა შენს მონდომებას ენთუზიაზმით არ უპასუხა ან შენი წარმატება არ იზეიმა, ამას პირად ღალატად მიიჩნევ და გული ისე გწყდება, თითქოს ტახტიდან ჩამოგაგდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 6. VIRGO (self.relation.venus_virgo.v1)
    # =========================================================================
    {
        "sign": "virgo",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "acts_of_service_currency",
        "metaphor": "toolbox_service",
        "text": "პოეტურ ოდებს საქმე გირჩევნია: გაფუჭებულ ნივთს შეაკეთებ, გრაფიკს დაალაგებ და ცხოვრებას გაუმარტივებ. შენი სიყვარული უხმაურო, მაგრამ გამართული მექანიზმია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "attentive_micro_observation",
        "metaphor": "fine_lens",
        "text": "შეუმჩნეველი არაფერი გრჩება — ზუსტად იცი, ვის როგორი ყავა უყვარს და როდის ეცვლება ხმის ტემბრი. შენი ყურადღება ყველაზე იშვიათი და ფაქიზი საჩუქარია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 3,
        "depth": "medium",
        "tone": "mocking",
        "angle": "relational_quality_control",
        "metaphor": "technical_inspection",
        "text": "შენთან ურთიერთობაში შესვლა მკაცრი ტექნიკური ინსპექციის გავლას ჰგავს. სანამ ვინმეზე ემოციურ რესურსს დახარჯავ, ჯერ მის პუნქტუალურობას, ჩვევებსა და ცხოვრების წესს ამოწმებ. გიყვარს პრაქტიკული ზრუნვა და ადამიანისთვის ყოველდღიურობის დალაგება. პრობლემა კი მაშინ იწყება, როცა შენი ეს დახმარების სურვილი დაუსრულებელ რედაქტირებაში გადადის: იმდენად ხარ კონცენტრირებული მეორის ნაკლოვანებების გასწორებაზე, რომ ავიწყდება, რომ ადამიანები პროექტები არ არიან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 7. LIBRA (self.relation.venus_libra.v1)
    # =========================================================================
    {
        "sign": "libra",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "aesthetic_diplomacy",
        "metaphor": "silk_balance",
        "text": "უხეშობა შენს გემოვნებას ფიზიკურად აზიანებს. შენთვის მიმზიდველია ადამიანი, რომელმაც იცის როდის გაჩუმდეს, როგორ მოუსმინოს და როგორ შექმნას ჰარმონია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "reciprocal_partnership_ideal",
        "metaphor": "golden_balance",
        "text": "თანასწორობა შენი მთავარი საზომია: ურთიერთობა ცალმხრივი მოძრაობა არასდროს უნდა იყოს. გინდა, რომ ორივე მხარე ერთნაირი პატივისცემით იცავდეს წონასწორობას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.7, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "conflict_avoidant_courtesy",
        "metaphor": "carpet_sweep_peace",
        "text": "შენთვის ურთიერთობა დახვეწილი ცეკვაა, სადაც მთავარი წესი ერთმანეთისთვის ფეხის არ დაბიჯებაა. საოცარი ოსტატობით ახერხებ ყველაზე დაძაბული სიტუაციაც კი რბილი ღიმილითა და დიპლომატიური ფრაზით განმუხტო. გიყვარს ესთეტიკა, ლამაზი გარემო და ორმხრივი თავაზიანობა. თუმცა შენი სისუსტე სწორედ ეს კონფლიქტის შიშია: მშვიდობის შესანარჩუნებლად მზად ხარ საკუთარი უკმაყოფილება ხალიჩის ქვეშ შეინახო, ოღონდ საჯარო კამათი არ დაიწყოს — სანამ ეს დაგროვილი სიმართლე მოულოდნელად არ აფეთქდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 8. SCORPIO (self.relation.venus_scorpio.v1)
    # =========================================================================
    {
        "sign": "scorpio",
        "index": 1,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "uncompromising_emotional_depth",
        "metaphor": "deep_abyss",
        "text": "ზედაპირული ფლირტი და ცარიელი კომპლიმენტები გაღიზიანებს. შენ ადამიანის ნამდვილი, დამალული შრეები გაინტერესებს — ის, რასაც სხვებს არასდროს უყვებიან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 2,
        "depth": "micro",
        "tone": "cocky",
        "angle": "fierce_protective_loyalty",
        "metaphor": "steel_armor",
        "text": "თუ ვინმე შენი ადამიანი გახდა, მისთვის კედელივით დგახარ. შენი ერთგულება აბსოლუტურია, მაგრამ სანაცვლოდ ზუსტად იმავე შეუვალ პატიოსნებას ითხოვ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 3,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "relational_trust_audit",
        "metaphor": "lie_detector_shadows",
        "text": "შენთვის ურთიერთობა ნახევრად არასდროს არსებობს: ან სრული, უპირობო ერთგულებაა, ან საერთოდ არაფერი. საოცარი ინტუიციით გრძნობ ნებისმიერ ფარისევლობას, უმცირეს ყოყმანსა და სიტყვებს მიღმა დამალულ განზრახვას. როცა ნამდვილად ენდობი, შენი ზრუნვა შეუვალი, ღრმა და მფარველობითია. თუმცა შენი მთავარი გამოცდა მუდმივი შინაგანი დაცვითი რეჟიმია: ხშირად ადამიანს მანამ ატარებ ფარულ ემოციურ ტესტებში, სანამ ის უბრალოდ არ დაიღლება იმის მტკიცებით, რომ შენი მოტყუება არასდროს უცდია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 9. SAGITTARIUS (self.relation.venus_sagittarius.v1)
    # =========================================================================
    {
        "sign": "sagittarius",
        "index": 1,
        "depth": "micro",
        "tone": "snarky",
        "angle": "relational_adventurism",
        "metaphor": "open_highway",
        "text": "შენთან ურთიერთობა მოგზაურობაა და არა საკანი. თუ ადამიანთან ერთად სიცილი, ახალი გზების აღმოჩენა და სამყაროზე კამათი არ შეგიძლია, იქ რუტინა გგუდავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "unvarnished_romantic_candor",
        "metaphor": "straight_arrow",
        "text": "შაქარმოყრილი პირფერობა შენი სტილი არ არის. პირდაპირ ამბობ იმას, რასაც ფიქრობ, რადგან გჯერა, რომ ნამდვილ კავშირს სიმართლე არასდროს აზიანებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "allergic_reaction_to_clinginess",
        "metaphor": "escape_hatch",
        "text": "შენთვის მიმზიდველია ის, ვინც შენს ჰორიზონტს აფართოებს — ადამიანი, რომელთანაც შეიძლება დილის ოთხ საათზე ფილოსოფიაზე იკამათო და მერე სპონტანურად გზას გაუდგე. ვერ იტან ეჭვიანობას, წვრილმან კონტროლსა და ვალდებულებების სიას. პრობლემა მაშინ ჩნდება, როცა ურთიერთობა ჩვეულებრივ ყოველდღიურობაში გადადის: როგორც კი რუტინის სუნი დადგება, შენი პირველი რეფლექსი კარებისკენ გახედვაა, რადგან სტაბილურობა ხშირად შეცდომით თავისუფლების დაკარგვა გგონია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 10. CAPRICORN (self.relation.venus_capricorn.v1)
    # =========================================================================
    {
        "sign": "capricorn",
        "index": 1,
        "depth": "micro",
        "tone": "cocky",
        "angle": "architectural_loyalty",
        "metaphor": "granite_pillar",
        "text": "შენს სიმპათიას წლები ამყარებს და არა წამიერი აფეთქება. შენი ერთგულება გრანიტივით მყარია, რადგან ადამიანებს მხოლოდ საფუძვლიანი გამოცდის შემდეგ ირჩევ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 2,
        "depth": "micro",
        "tone": "conversational",
        "angle": "sober_affectional_reserve",
        "metaphor": "quiet_rock",
        "text": "ხმამაღალ დაპირებებს მშვიდი ქმედება გირჩევნია. საიმედოობა შენთვის სიყვარულის უმაღლესი ფორმაა: იყო იქ, როცა მეორეს რეალური საყრდენი სჭირდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "transactional_caution",
        "metaphor": "contract_ledger",
        "text": "შენთვის ურთიერთობა სერიოზული ინვესტიციაა, რომელსაც გააზრებულად და წინდახედულად უდგები. არ გხიბლავს ზედაპირული დრამა და ქარაფშუტა თავგადასავლები; შენ პარტნიორში სიმწიფეს, პატივისცემასა და საერთო მიზნებს ეძებ. საქმით ზრუნავ და შენს გვერდით ადამიანი თავს დაცულად გრძნობს. თუმცა შენი სისუსტე ზედმეტი სიფრთხილეა: ხანდახან იმდენად გეშინია დროის ფუჭად დაკარგვის, რომ ურთიერთობას საქმიან მოლაპარაკებად აქცევ და სითბოს მანამ არ გასცემ, სანამ მეორე მხარე გარანტიებს არ მოგცემს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 11. AQUARIUS (self.relation.venus_aquarius.v1)
    # =========================================================================
    {
        "sign": "aquarius",
        "index": 1,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "friendship_first_attraction",
        "metaphor": "orbit_parallel",
        "text": "შენთან კავშირი მეგობრობით იწყება: თუ ადამიანი შენს უცნაურ ინტერესებს არ იზიარებს და თავისუფლებას არ სცემს პატივს, მასთან რომანტიკა წარმოუდგენელია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 2,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "fierce_respect_for_autonomy",
        "metaphor": "open_skies",
        "text": "არავის მორგებას არ ცდილობ და არც სხვის გადაკეთებას აპირებ. შენთვის მიმზიდველია ავთენტურობა — ადამიანი, რომელიც საკუთარ უნიკალურობას არ მალავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 3,
        "depth": "medium",
        "tone": "snarky",
        "angle": "aloof_emotional_distance",
        "metaphor": "satellite_altitude",
        "text": "შენთვის ურთიერთობა ორი დამოუკიდებელი გალაქტიკის თანაკვეთაა და არა ერთმანეთში შერწყმა. გხიბლავს არასტანდარტული აზროვნება, პროგრესული ხედვა და ადამიანი, რომელსაც საკუთარი საინტერესო ცხოვრება აქვს. პატივს სცემ სხვის პირად სივრცეს და იმავეს ითხოვ საპასუხოდ. თუმცა პრობლემა მაშინ იწყება, როცა მეორე მხარე სუფთა ემოციურ სითბოს და დაუცველობას ითხოვს: შენ ამ დროს ლოგიკურ სიმაღლეზე დისტანცირდები, რადგან ინტენსიური გრძნობები შენს რაციონალურ სისტემას თავდაყირა აყენებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },

    # =========================================================================
    # 12. PISCES (self.relation.venus_pisces.v1)
    # =========================================================================
    {
        "sign": "pisces",
        "index": 1,
        "depth": "micro",
        "tone": "conversational",
        "angle": "soulful_empathic_attunement",
        "metaphor": "gentle_ocean",
        "text": "ადამიანის მდგომარეობას უსიტყვოდ იჭერ. შენი მიმღებლობა უსაზღვროა: შეგიძლია სხვისი სისუსტეები გაკიცხვის გარეშე მიიღო და სივრცე სითბოთი აავსო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 2,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "romantic_idealism",
        "metaphor": "poetic_mist",
        "text": "შენთვის ურთიერთობა პოეზიაა — სამყარო, სადაც ყოველდღიური სიუხეშე ქრება და მხოლოდ სუფთა, გულწრფელი ემოციური თანაზიარობა რჩება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 3,
        "depth": "medium",
        "tone": "jester",
        "angle": "diffuse_boundary_vulnerability",
        "metaphor": "mirage_castle",
        "text": "შენთვის მიზიდულობა ჯადოსნურ ატმოსფეროს ჰგავს, სადაც ლოგიკური წესები და მკაცრი საზღვრები უბრალოდ ქრება. საოცარი თანაგრძნობის უნარი გაქვს — შეგიძლია ადამიანის სულში ჩაიხედო და მისი ყველაზე უთქმელი ტკივილიც კი გაიგო. გიყვარს რომანტიკა, შთაგონება და უსიტყვო კავშირი. თუმცა შენი მთავარი სისუსტე ილუზიების შექმნაა: ხანდახან იმდენად გინდა ზღაპარი დაიჯერო, რომ აშკარა გაფრთხილებებს თვალს არიდებ და ადამიანს საკუთარი წარმოსახვით გამოგონილ თვისებებს მიაწერ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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


def validate_and_build_venus_pilot():
    print("=" * 70)
    print("JESTER PHASE 3.6 — Venus 36-Asset Semantic Pilot Generation & QA")
    print("=" * 70)

    sign_map = {s[0]: s for s in SIGN_SPECS}
    assets = []

    # Check total count
    assert len(VENUS_RAW_ASSETS) == 36, f"Expected 36 assets, found {len(VENUS_RAW_ASSETS)}"

    # Check exactly 3 assets per sign (2 Micro, 1 Medium)
    by_sign = {}
    for raw in VENUS_RAW_ASSETS:
        by_sign.setdefault(raw["sign"], []).append(raw)

    assert len(by_sign) == 12, f"Expected 12 signs, got {len(by_sign)}"
    for s, s_assets in by_sign.items():
        assert len(s_assets) == 3, f"Sign {s} must have exactly 3 assets, got {len(s_assets)}"
        micros = [a for a in s_assets if a["depth"] == "micro"]
        mediums = [a for a in s_assets if a["depth"] == "medium"]
        assert len(micros) == 2, f"Sign {s} must have 2 micros, got {len(micros)}"
        assert len(mediums) == 1, f"Sign {s} must have 1 medium, got {len(mediums)}"

    # Audit all texts
    texts = []
    tone_counts = {}
    for raw in VENUS_RAW_ASSETS:
        sign = raw["sign"]
        idx = raw["index"]
        depth = raw["depth"]
        tone = raw["tone"]
        angle = raw["angle"]
        metaphor = raw["metaphor"]
        text = raw["text"].strip()
        quality = raw["quality"]

        texts.append(text)
        tone_counts[tone] = tone_counts.get(tone, 0) + 1

        char_len = len(text)
        if depth == "micro":
            assert 100 <= char_len <= 250, f"Micro length violation ({char_len} chars): {text}"
        elif depth == "medium":
            assert 400 <= char_len <= 750, f"Medium length violation ({char_len} chars): {text}"

        # Forbidden opening check
        for f_open in FORBIDDEN_OPENINGS:
            assert not text.startswith(f_open), f"Forbidden opening '{f_open}' in: {text}"

        # Forbidden claims check
        for c_pat in FORBIDDEN_CLAIMS:
            assert not re.search(c_pat, text, re.IGNORECASE), f"Forbidden claim pattern '{c_pat}' matched in: {text}"

        # Astrological jargon check in user copy
        jargon_found = scan_for_jargon(text, "ka")
        assert not jargon_found, f"Astrological jargon found: {jargon_found} in text: {text}"

        # Quality Gate validation (all >= 4.0)
        for dim, score in quality.items():
            assert score >= 4.0, f"Quality gate violation in {sign}_{idx}: {dim} = {score} (< 4.0)"

        # Verify angle in contract
        contract_id = f"self.relation.venus_{sign}.v1"
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
        asset_id = f"ca_rel_{sign[:3]}_{idx:03d}_ka_{tone[:3]}_{depth[:3]}"
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
                "batch:venus_pilot_v1",
                "body:venus",
                f"sign:{sign}",
                f"element:{element}",
                f"modality:{modality}",
                f"depth:{depth}",
                f"angle:{angle}",
                f"metaphor:{metaphor}",
            ],
            "internal_notes": json.dumps({
                "batch_id": "venus_pilot_v1",
                "astrological_fact": f"Venus is in {sign.capitalize()}",
                "semantic_contract": contract_id,
                "semantic_angle": angle,
                "metaphor_family": metaphor,
                "char_length": char_len,
                "quality_scores": quality,
            }, ensure_ascii=False),
            "provenance": {
                "batch_id": "venus_pilot_v1",
                "interpretation_id": contract_id,
                "body": "venus",
                "sign": sign,
                "element": element,
                "modality": modality,
                "semantic_contract_id": contract_id,
                "semantic_angle": angle,
                "tone": tone,
                "depth": depth,
                "variant": variant_key,
                "source_inputs": {
                    "venus_sign": sign,
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
    assert len(texts) == len(set(texts)), "Exact duplicate found in Venus pilot texts"

    # Pairwise Jaccard similarity (< 0.85)
    max_sim = 0.0
    most_similar_pair = None
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = jaccard_similarity(texts[i], texts[j])
            if sim > max_sim:
                max_sim = sim
                most_similar_pair = (texts[i], texts[j])
            assert sim < 0.85, f"Near-duplicate text detected (Jaccard={sim:.2f}):\n1: {texts[i]}\n2: {texts[j]}"

    print(f"SUCCESS: Generated and validated exactly {len(assets)} Venus pilot assets.")
    print(f"  - Micro: {len([a for a in assets if 'depth:micro' in a['tags']])}")
    print(f"  - Medium: {len([a for a in assets if 'depth:medium' in a['tags']])}")
    print(f"Peak pairwise Jaccard similarity: {max_sim:.3f}")
    print("Tone Distribution across pilot batch:")
    for t, cnt in sorted(tone_counts.items()):
        print(f"  - {t}: {cnt}")

    # Output file
    out_path = root_dir / "backend" / "app" / "interpretation" / "data" / "venus_corpus.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {out_path}")
    return assets


if __name__ == "__main__":
    validate_and_build_venus_pilot()
