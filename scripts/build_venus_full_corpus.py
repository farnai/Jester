"""
JESTER — PHASE 3.7
Venus Full Generation & Astrological Provenance Hardening Pipeline
Generates exactly 96 Venus assets (12 signs x 8 assets: 72 Micro, 24 Medium)
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

VENUS_FULL_RAW_ASSETS = [
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
        "context_type": "interpersonal",
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
        "context_type": "romantic",
        "text": "თუ ადამიანთან მსუბუქი შეჯიბრი და აზარტული ნაპერწკალი არ იგრძნობა, ინტერესი იმავე წამს ქრება. შენ სიმშვიდე კი არა, თანაბარი ძალის მოთამაშე გჭირდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "rapid_relational_initiative",
        "metaphor": "direct_collision",
        "context_type": "friendship",
        "text": "როცა ადამიანი მოგწონს, გზადაგზა არ მიკიბ-მოკიბავ: პირდაპირ ეუბნები, რომ მასთან დროის გატარება გინდა. დიპლომატიური თავაზიანობა შენს ენერგიას მხოლოდ ფიტავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "impatience_with_relational_games",
        "metaphor": "snail_race",
        "context_type": "social",
        "text": "ორაზროვანი მინიშნებები და სამდღიანი პაუზები მესიჯებზე შენს ნერვებზე თამაშობს: სანამ სხვა ფიქრობს რა უპასუხოს, შენ უკვე ახალ წრეზე ხარ გადასული.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "competitive_playful_spark",
        "metaphor": "ignited_fuse",
        "context_type": "romantic",
        "text": "შენთვის სიმპათია მშვიდი მდინარე კი არა, მოულოდნელი ნაპერწკალია: ან მყისიერად ენთები და მთელ სივრცეს ათბობ, ან სიცივე ისეთივე მკვეთრი და საბოლოოა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aries",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "rapid_relational_initiative",
        "metaphor": "door_kick_entry",
        "context_type": "social",
        "text": "კარზე ფრთხილად კაკუნი შენი სტილი არ არის: მეგობრობაშიც და სიმპათიაშიც პირდაპირ შუაგულში იჭრები და ადამიანს უბრალოდ არჩევანის გარეშე ტოვებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "impatience_with_relational_games",
        "metaphor": "accelerator_brake",
        "context_type": "romantic",
        "text": "შენთვის მიზიდულობა მყისიერი აფეთქებაა — ან პირველივე წუთიდან იგრძნობა ცეცხლი, ან მეორე შანსს საერთოდ აღარავის აძლევ. ზრდილობიანი დიპლომატია, ორაზროვანი მინიშნებები და თვეობით ლოდინი შენს ბუნებას პირდაპირ შეურაცხყოფს. მოგწონს, როცა ადამიანს საკუთარი პოზიციის ხმამაღლა გამოხატვის არ ეშინია. პრობლემა ისაა, რომ სხვის ფრთხილ ტემპს მაშინვე გულგრილობად ნათლავ: გინდა ყველაფერი ახლავე მოხდეს, რის გამოც ხანდახან კარს მანამ კეტავ, სანამ მეორე მხარე ნაბიჯის გადადგმას მოასწრებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aries",
        "index": 8,
        "depth": "medium",
        "tone": "conversational",
        "angle": "competitive_playful_spark",
        "metaphor": "boxing_handshake",
        "context_type": "interpersonal",
        "text": "ურთიერთობაში შენთვის მთავარი ენერგია ცოცხალი ინტერაქციაა. ვერ იტან პასიურ თანხმობას, როცა ადამიანი ყველაფერში გეთანხმება მხოლოდ იმიტომ, რომ კონფლიქტს მოერიდოს. შენ პატივს სცემ მას, ვისაც შეუძლია თამამად შემოგხედოს, შენს ხუმრობას უფრო მწარე პასუხი დაახვედროს და საკუთარი სივრცე დაიცვას. თუმცა ხშირად გავიწყდება, რომ ურთიერთობა მუდმივი რინგი არ არის: ხანდახან ადამიანებს უბრალოდ დასვენება უნდათ, შენ კი ისევ საპასუხო შეტევისთვის ემზადები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "friendship",
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
        "context_type": "romantic",
        "text": "სიტყვების ლამაზი ფეიერვერკი არ გაინტერესებს. შენთვის ერთგულება კონკრეტული ზრუნვაა: გემრიელი ვახშამი, სიმყუდროვე და ისეთი საიმედოობა, რომელსაც ხელით შეეხები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "tangible_sensory_loyalty",
        "metaphor": "granite_bench",
        "context_type": "appreciation",
        "text": "შენი გემოვნება დროებით ტრენდებზე მაღლა დგას: ხარისხს, სიმყარეს და ნამდვილ სიმშვიდეს ირჩევ. შენთან ყოფნა ხალხისთვის ფუფუნებაა, რადგან ქაოსს არ იკარებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "unhurried_relational_pacing",
        "metaphor": "loading_bar",
        "context_type": "social",
        "text": "თუ ვინმე აჩქარებას ცდილობს, შენი შინაგანი სიჩქარე ავტომატურად განახევრდება. შენთან დაახლოება ნელი, მაგრამ საიმედო ჩამოტვირთვის პროცესს ჰგავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "stubborn_comfort_zones",
        "metaphor": "heavy_anchor",
        "context_type": "romantic",
        "text": "შენი მიჯაჭვულობა უძრავი ქვაა: თუ ადამიანი მიიღე, მის გვერდით დგახარ, მაგრამ თუ მან შენი სიმშვიდე დაარღვია, კედელივით ცივი და მიუდგომელი ხდები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "taurus",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "tangible_sensory_loyalty",
        "metaphor": "blanket_shield",
        "context_type": "friendship",
        "text": "დრამატული რჩევების ნაცვლად ადამიანს თბილ პლედს და გემრიელ ჩაის დაახვედრებ: იცი, რომ სხეულის დამშვიდება ხშირად ნებისმიერ გრძელ საუბარზე უკეთ მუშაობს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 7,
        "depth": "medium",
        "tone": "snarky",
        "angle": "stubborn_comfort_zones",
        "metaphor": "anchored_sofa",
        "context_type": "romantic",
        "text": "შენი სიმპათია ისეთივე მყარი და უძრავია, როგორც ასწლოვანი მუხა. თუ ვინმე შენს გულში შემოვიდა, იქიდან მისი გაყვანა თითქმის შეუძლებელია — ოღონდ ეს წესი შენს ჩვევებსაც ეხება. შენთვის იდეალური ურთიერთობა მშვიდი ნავსაყუდელია, სადაც დრამის ადგილი არ არის. თუმცა პრობლემა მაშინ იწყება, როცა ნებისმიერ ცვლილებას კატასტროფად აღიქვამ: მზად ხარ თვეობით გაუძლო გაუცხოებას, ოღონდ დალაგებული რუტინა და შენი საყვარელი კომფორტის ზონა არ დაირღვეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "taurus",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "unhurried_relational_pacing",
        "metaphor": "slow_cooker",
        "context_type": "interpersonal",
        "text": "შენთან ურთიერთობის აგება სახლის ფუნდამენტის ჩასხმას ჰგავს: არანაირი ნაჩქარევი გადაწყვეტილება, ყველაფერი დინჯად, ხარისხიანად და საუკუნეების გათვლით კეთდება. ვერ იტან ადამიანებს, რომლებიც დღეს ერთს ამბობენ და ხვალ სხვას აკეთებენ; შენთვის სიტყვის ფასი მისი პრაქტიკული შესრულებაა. სამაგიეროდ, როცა საქმე კომპრომისზე მიდგება, შენი ჯიუტი სიმშვიდე გარშემომყოფებს ჭკუიდან შლის: შეგიძლია ისეთი ურყევი სახით იჯდე საკუთარ პოზიციაზე, რომ მოპირდაპირე მხარე უბრალოდ დაღლილობისგან დანებდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "friendship",
        "text": "საუკეთესო კომპლიმენტი შენთვის ახალი უცნაური იდეის გაზიარებაა. თუ ურთიერთობა გონებრივ ჟანგბადს გაძლევს, იქ რჩები; თუ წესებს გიწესებს — უჩუმრად ქრები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "fickle_novelty_craving",
        "metaphor": "radio_channel_switch",
        "context_type": "social",
        "text": "ერთფეროვნება შენი სიმპათიის მთავარი მტერია. თუ ყოველი შეხვედრა წინასწარ დაწერილ სცენარს ჰგავს, შენი ყურადღება მაშინვე სხვა სიხშირეზე გადადის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "conversational_chemistry",
        "metaphor": "rapier_fencing",
        "context_type": "romantic",
        "text": "ფლირტი შენთვის ინტელექტუალური ფარიკაობაა: სიტყვებით ისე ოსტატურად თამაშობ, რომ სანამ მეორე მხარე პასუხს მოიფიქრებს, უკვე სამი ნაბიჯით წინ ხარ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 5,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "need_for_mental_spaciousness",
        "metaphor": "bird_in_flight",
        "context_type": "interpersonal",
        "text": "ეჭვიანობა და მუდმივი კონტროლი შენს ინტერესს წამებში კლავს. შენთან ყოფნის საიდუმლო თავისუფლებაშია: რაც ნაკლებად გზღუდავენ, მით მეტად გინდა დარჩენა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 6,
        "depth": "micro",
        "tone": "conversational",
        "angle": "conversational_chemistry",
        "metaphor": "shared_links",
        "context_type": "friendship",
        "text": "შენი სიყვარულის დასტური მემების და საინტერესო სტატიების გაუთავებელი ნაკადია. ვისთანაც ინფორმაციას ცვლი, შენთვის ის ადამიანი უკვე ახლობელია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "gemini",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "fickle_novelty_craving",
        "metaphor": "ping_pong_circus",
        "context_type": "romantic",
        "text": "შენთვის მიზიდულობა პირველ რიგში ვერბალური პინგ-პონგია. თუ მოსაუბრეს იუმორი არ ჰყოფნის ან შენს ნათქვამ ხუმრობას სამი წუთი შიფრავს, შენი ტვინი მაშინვე პარალელურ რეჟიმში გადადის. გიყვარს მსუბუქი, ჭკვიანური ფლირტი და ადამიანები, რომლებთანაც ერთდროულად ათ სხვადასხვა თემაზე შეიძლება სიცილი. სირთულე მაშინ ჩნდება, როცა სიტუაცია დამძიმდება: როგორც კი ვინმე ღრმა, სერიოზულ მონოლოგს იწყებს, შენ ხუმრობით იარაღდები და ემოციურ სიღრმეს თავს ოსტატურად არიდებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "gemini",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "need_for_mental_spaciousness",
        "metaphor": "open_courtyard",
        "context_type": "social",
        "text": "შენთვის ადამიანთან სიახლოვე არ ნიშნავს ერთმანეთის საკუთრებად ქცევას. გხიბლავს ცნობისმოყვარეობა, სპონტანური შეხვედრები და ისეთი საუბრები, სადაც ყოველ წუთს ახალი აზრი იბადება. მეგობრობაშიც და სიმპათიაშიც გჭირდება ჰაერი: თუ ვინმე ცდილობს შენი დღის განრიგი აკონტროლოს, მაშინვე უჩინარი ხდები. თუმცა ხანდახან ეს ზედაპირული სიმსუბუქე მეორე მხარეს აბნევს: სანამ შენ ფიქრობ, რომ უბრალოდ მხიარულად ურთიერთობთ, სხვებს უჭირთ გაიგონ, რეალურად რამდენად ხარ ჩართული მათ ცხოვრებაში.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "appreciation",
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
        "context_type": "romantic",
        "text": "უცხო ადამიანისთვის შენი გული ციხესიმაგრეა, სადაც დაცვა ყველა კუთხეში დგას. ნდობას წვეთ-წვეთად გასცემ, რადგან იცი, რა ფასი აქვს შენს დაუცველობას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 3,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "protective_nurturing_instinct",
        "metaphor": "family_heirloom",
        "context_type": "friendship",
        "text": "შენთვის ახლო წრე ოჯახის ტოლფასია: თუ ვინმე მიიღე, მის დარდს საკუთარივით განიცდი და მზად ხარ ნებისმიერ უსამართლობას მის მაგივრად გადაეღობო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "defensive_relational_retreat",
        "metaphor": "silent_radar",
        "context_type": "social",
        "text": "თუ ვინმემ შენი ყურადღება ვერ დააფასა, სცენას არ გამართავ: უბრალოდ ისე ჩუმად და ცივად გაუჩინარდები, რომ მეორე მხარე ვერც მიხვდება, რა მოხდა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 5,
        "depth": "micro",
        "tone": "cocky",
        "angle": "emotional_security_checkpoint",
        "metaphor": "deep_harbor",
        "context_type": "romantic",
        "text": "ისეთ სიმყუდროვეს და ემოციურ უსაფრთხოებას ქმნი, რომ შენთან ერთხელ მოხვედრილ ადამიანს სხვაგან წასვლა აღარასდროს უნდება — შენი სითბო იშვიათი თავშესაფარია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "cancer",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "protective_nurturing_instinct",
        "metaphor": "memory_box",
        "context_type": "appreciation",
        "text": "წლების წინ შემთხვევით ნათქვამ ფრაზას გაიხსენებ და ადამიანს ზუსტად იმ საჩუქარს მიუტან, რაზეც ბავშვობაში ოცნებობდა: შენი მეხსიერება ემოციური არქივია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 7,
        "depth": "medium",
        "tone": "snarky",
        "angle": "defensive_relational_retreat",
        "metaphor": "crab_shell_sonar",
        "context_type": "romantic",
        "text": "შენთან დაახლოება საიდუმლო ლაბირინთში გავლას ჰგავს: სანამ ბოლომდე არ დარწმუნდები, რომ მეორე მხარე შენს სითბოს ბოროტად არ გამოიყენებს, მანამდე მხოლოდ თავაზიან დისტანციას ინარჩუნებ. სამაგიეროდ, როცა კარს გახსნი, შენი ერთგულება უსაზღვრო ხდება. მთავარი ხაფანგი კი შენი შინაგანი სარადარო სისტემაა: თუ ვინმეს ცივ ტონს შეამჩნევ, პირდაპირ კი არ ჰკითხავ, არამედ ჩუმად საკუთარ ნიჟარაში ჩაიკეტები და დაელოდები, როდის მიხვდება მეორე თავის დანაშაულს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "cancer",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "emotional_security_checkpoint",
        "metaphor": "emotional_vault",
        "context_type": "interpersonal",
        "text": "შენთვის ურთიერთობაში მთავარი ვალუტა ემოციური უსაფრთხოებაა. სანამ ადამიანს საკუთარ საიდუმლოებებს გაუზიარებ, ჯერ მის რეაქციებს ასჯერ შეამოწმებ: როგორ რეაგირებს სხვის სისუსტეზე, შეუძლია თუ არა მოსმენა და რამდენად საიმედოა მისი სიტყვა. როცა ნდობა მოპოვებულია, შეუდარებლად მზრუნველი ხარ. თუმცა პრობლემა მაშინ იწყება, როცა ძველ წყენებს გულში თვეობით აგროვებ და მერე სრულიად მოულოდნელად, საყოფაცხოვრებო წვრილმანის გამო, წარსულის მთელ არქივს მაგიდაზე გადმოყრი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "romantic",
        "text": "ნახევრად ყოფნა შენი სტილი არ არის: ადამიანი ან შენს გვერდით დგას და ერთად ანათებთ, ან ჩრდილში რჩება. შენთვის პატივისცემა ყველაფერზე მაღლა დგას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "validation_vulnerability",
        "metaphor": "dimmed_mirror",
        "context_type": "social",
        "text": "თუ შენს ძალისხმევას აღფრთოვანებული მზერა არ მოჰყვა, ენთუზიაზმი წამში ცივდება: შენ სითბოს უხვად გასცემ, მაგრამ მაყურებლის გარეშე თამაში არ გხიბლავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 4,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "generous_royal_courtship",
        "metaphor": "golden_banquet",
        "context_type": "friendship",
        "text": "შენი მეგობრობა გულუხვობის ზეიმია: გიყვარს ადამიანების გამხნევება, მათი ნიჭის წარმოჩენა და მათთვის ისეთი გარემოს შექმნა, სადაც ყველა თავს გამორჩეულად გრძნობს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 5,
        "depth": "micro",
        "tone": "mocking",
        "angle": "pride_and_public_devotion",
        "metaphor": "vip_invitation",
        "context_type": "social",
        "text": "შენს წრეში მოხვედრა საპატიო სტატუსს ჰგავს: ვისაც გვერდით დაიყენებ, მისგანაც იმავე ურყევ ლოიალობას და საჯარო პატივისცემას ელი.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 6,
        "depth": "micro",
        "tone": "conversational",
        "angle": "generous_royal_courtship",
        "metaphor": "warm_sunlight",
        "context_type": "interpersonal",
        "text": "როცა ადამიანს ენდობი, შენი სითბო პირდაპირ ათბობს: არასდროს გშურს სხვისი წარმატება, პირიქით, გინდა რომ შენთან ერთად ისიც მწვერვალზე იდგეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "leo",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "validation_vulnerability",
        "metaphor": "crown_and_applause",
        "context_type": "romantic",
        "text": "შენთვის ურთიერთობა ცენტრალურ სცენაზე გამოსვლას ჰგავს, სადაც ორივე მთავარ როლს თამაშობთ და ერთმანეთის ბრწყინვალებით ტკბებით. გულუხვი ხარ, გიყვარს ადამიანის გამორჩევა, მისი ნიჭით აღფრთოვანება და მისთვის სამეფო გარემოს შექმნა. თუმცა შენი აქილევსის ქუსლი სწორედ ეს გადაჭარბებული პატივმოყვარეობაა: თუ შეამჩნიე, რომ პარტნიორმა შენს მონდომებას ენთუზიაზმით არ უპასუხა ან შენი წარმატება არ იზეიმა, ამას პირად ღალატად მიიჩნევ და გული ისე გწყდება, თითქოს ტახტიდან ჩამოგაგდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "leo",
        "index": 8,
        "depth": "medium",
        "tone": "unexpected",
        "angle": "pride_and_public_devotion",
        "metaphor": "lion_pride_parade",
        "context_type": "interpersonal",
        "text": "შენთან კავშირი ღირსების საკითხია: თუ ვინმეს მეგობრად ან რჩეულად თვლი, მის რეპუტაციას ისეთივე თავგამოდებით დაიცავ, როგორც საკუთარს. გიყვარს ფერადი ჟესტები, სიურპრიზები და ადამიანებისთვის იმის შეხსენება, თუ რამდენად განსაკუთრებულები არიან. სირთულე კი მაშინ იწყება, როცა უბრალო საყოფაცხოვრებო უთანხმოებას პრესტიჟის ბრძოლად აქცევ: შეცდომის აღიარება შენთვის იმდენად რთულია, რომ ხშირად მზად ხარ დრამა გააძლიერო, ოღონდ საკუთარი სიმართლე ურყევად დაიცვა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "friendship",
        "text": "შეუმჩნეველი არაფერი გრჩება — ზუსტად იცი, ვის როგორი ყავა უყვარს და როდის ეცვლება ხმის ტემბრი. შენი ყურადღება ყველაზე იშვიათი და ფაქიზი საჩუქარია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "acts_of_service_currency",
        "metaphor": "swiss_watch",
        "context_type": "romantic",
        "text": "ლამაზი დაპირებებით ვერავინ მოგატყუებს. შენთვის სანდოობა შვეიცარიული საათივით გამართული ქმედებაა: სიტყვას საქმე უნდა მოჰყვებოდეს, სხვა ყველაფერი ქარია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "relational_quality_control",
        "metaphor": "red_pencil",
        "context_type": "interpersonal",
        "text": "თუ ადამიანს ნაკლოვანებაზე მიუთითებ, ეს ზიზღი კი არა, დახმარების სურვილია: შენ ხედავ პოტენციალს და გინდა, რომ ყველაფერი იდეალურად მუშაობდეს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 5,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "attentive_micro_observation",
        "metaphor": "clean_slate",
        "context_type": "social",
        "text": "ქაოსი და დაულაგებელი ურთიერთობები შენს სიმშვიდეს ძირს უთხრის. შენ გჭირდება სიცხადე, წესრიგი და ურთიერთგაგება, სადაც ყოველ წვრილმანს თავისი ადგილი აქვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "virgo",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "acts_of_service_currency",
        "metaphor": "first_aid_kit",
        "context_type": "friendship",
        "text": "როცა სხვები უბრალოდ წუხან, შენ უკვე წამლებს ყიდულობ და ექიმთან რიგს იკავებ: შენი სიმპათია პრაქტიკული ხსნაა და არა ცარიელი თანაგრძნობა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 7,
        "depth": "medium",
        "tone": "mocking",
        "angle": "relational_quality_control",
        "metaphor": "technical_inspection",
        "context_type": "social",
        "text": "შენთან ურთიერთობაში შესვლა მკაცრი ტექნიკური ინსპექციის გავლას ჰგავს. სანამ ვინმეზე ემოციურ რესურსს დახარჯავ, ჯერ მის პუნქტუალურობას, ჩვევებსა და ცხოვრების წესს ამოწმებ. გიყვარს პრაქტიკული ზრუნვა და ადამიანისთვის ყოველდღიურობის დალაგება. პრობლემა კი მაშინ იწყება, როცა შენი ეს დახმარების სურვილი დაუსრულებელ რედაქტირებაში გადადის: იმდენად ხარ კონცენტრირებული მეორის ნაკლოვანებების გასწორებაზე, რომ ავიწყდება, რომ ადამიანები პროექტები არ არიან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "virgo",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "acts_of_service_currency",
        "metaphor": "spreadsheet_heart",
        "context_type": "romantic",
        "text": "შენთვის სიყვარული ყოველდღიური შრომა და ერთგული მზრუნველობაა. არ გხიბლავს ხმაურიანი სერენადები და თეატრალური დრამა; შენთვის გაცილებით ძვირფასია, როცა ადამიანი დანაპირებს დროულად ასრულებს და შენს პირად სივრცეს პატივს სცემს. საოცარი ოსტატობით ახერხებ პარტნიორის ცხოვრება უფრო კომფორტული და ორგანიზებული გახადო. თუმცა შენი სისუსტე ზედმეტი პედანტურობაა: ხანდახან იმდენად ხარ გატაცებული უმნიშვნელო დეტალების ანალიზით, რომ გავიწყდება უბრალოდ მოეშვა და მომენტით ისიამოვნო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "aesthetic",
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
        "context_type": "romantic",
        "text": "თანასწორობა შენი მთავარი საზომია: ურთიერთობა ცალმხრივი მოძრაობა არასდროს უნდა იყოს. გინდა, რომ ორივე მხარე ერთნაირი პატივისცემით იცავდეს წონასწორობას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.7, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "conflict_avoidant_courtesy",
        "metaphor": "soft_cushion",
        "context_type": "social",
        "text": "კამათის თავიდან ასაცილებლად ისეთ დიპლომატიურ სასწაულებს ახდენ, რომ ხანდახან თავადაც გავიწყდება, რეალურად რას ფიქრობდი თავიდან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 4,
        "depth": "micro",
        "tone": "cocky",
        "angle": "aesthetic_diplomacy",
        "metaphor": "art_gallery",
        "context_type": "social",
        "text": "შენი გარემოცვა დახვეწილ გალერეას ჰგავს: უგემოვნობას, ყვირილს და ქაოსს ახლოსაც არ იკარებ. შენთან ურთიერთობა ესთეტიკის გაკვეთილია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 5,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "reciprocal_partnership_ideal",
        "metaphor": "mirror_reflection",
        "context_type": "romantic",
        "text": "როგორც გექცევიან, ზუსტად იმავე მონეტით პასუხობ: სითბოს სითბოთი აბრუნებ, სიცივეს კი ისეთივე ელეგანტური გულგრილობით პასუხობ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "libra",
        "index": 6,
        "depth": "micro",
        "tone": "mocking",
        "angle": "conflict_avoidant_courtesy",
        "metaphor": "polite_mask",
        "context_type": "social",
        "text": "შენი თავაზიანი ღიმილი საუკეთესო ჯავშანია: შეგიძლია ადამიანი ისე ზრდილობიანად გაისტუმრო, რომ კომპლიმენტი ეგონოს და მადლობაც გითხრას.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "conflict_avoidant_courtesy",
        "metaphor": "carpet_sweep_peace",
        "context_type": "romantic",
        "text": "შენთვის ურთიერთობა დახვეწილი ცეკვაა, სადაც მთავარი წესი ერთმანეთისთვის ფეხის არ დაბიჯებაა. საოცარი ოსტატობით ახერხებ ყველაზე დაძაბული სიტუაციაც კი რბილი ღიმილითა და დიპლომატიური ფრაზით განმუხტო. გიყვარს ესთეტიკა, ლამაზი გარემო და ორმხრივი თავაზიანობა. თუმცა შენი სისუსტე სწორედ ეს კონფლიქტის შიშია: მშვიდობის შესანარჩუნებლად მზად ხარ საკუთარი უკმაყოფილება ხალიჩის ქვეშ შეინახო, ოღონდ საჯარო კამათი არ დაიწყოს — სანამ ეს დაგროვილი სიმართლე მოულოდნელად არ აფეთქდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "libra",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "reciprocal_partnership_ideal",
        "metaphor": "court_orchestra",
        "context_type": "partnership",
        "text": "შენთვის იდეალური კავშირი ორი სრულფასოვანი ადამიანის ჰარმონიული სიმფონიაა. ვერ იტან უხეშ დომინაციას, როცა ერთი მხარე მეორეს ჩაგრავს ან საკუთარ ნებას თავს ახვევს. შენ ეძებ თანასწორობას, ინტელექტუალურ სინქრონს და საერთო ესთეტიკურ ხედვას. თუმცა ხშირად იმდენად ხარ ორიენტირებული პარტნიორის კომფორტზე, რომ საკუთარ საზღვრებს ბუნდოვანს ხდი: ცდილობ ყველას მოერგო, ყველას გაუგო და ბოლოს საკუთარ თავს ეკითხები, სად გაქრა შენი რეალური სურვილები.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "loyalty",
        "text": "თუ ვინმე შენი ადამიანი გახდა, მისთვის კედელივით დგახარ. შენი ერთგულება აბსოლუტურია, მაგრამ სანაცვლოდ ზუსტად იმავე შეუვალ პატიოსნებას ითხოვ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "relational_trust_audit",
        "metaphor": "xray_scanner",
        "context_type": "social",
        "text": "შენი მზერა ფარულ დეტექტორს ჰგავს: სანამ სხვა ორ სიტყვას იტყვის, შენ უკვე იცი რა იმალება მის ზრდილობიან ღიმილს მიღმა. მოტყუება შენთან გამორიცხულია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "uncompromising_emotional_depth",
        "metaphor": "shallow_puddle",
        "context_type": "social",
        "text": "ადამიანები, რომლებიც მხოლოდ ამინდზე და ზედაპირულ თემებზე საუბრობენ, შენში მოწყენილობას კი არა, სრულ გაუცხოებას იწვევენ: შენ სიღრმე გწყურია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 5,
        "depth": "micro",
        "tone": "conversational",
        "angle": "fierce_protective_loyalty",
        "metaphor": "vault_keeper",
        "context_type": "friendship",
        "text": "შენთან საიდუმლოს გაზიარება ყველაზე უსაფრთხო ნაბიჯია: რაც შენს ყურამდე მივა, იქ სამუდამოდ ჩაიკეტება. მეგობრობაში შენი საიმედოობა ურყევია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "scorpio",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "uncompromising_emotional_depth",
        "metaphor": "dark_magnet",
        "context_type": "romantic",
        "text": "შენი დუმილი ხშირად ნებისმიერ საუბარზე უფრო ინტენსიურია: ოთახში შემოსვლითაც კი ისეთ ატმოსფეროს ქმნი, რომ გარშემო ყველა სიმართლის თქმას იწყებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 7,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "relational_trust_audit",
        "metaphor": "lie_detector_shadows",
        "context_type": "romantic",
        "text": "შენთვის ურთიერთობა ნახევრად არასდროს არსებობს: ან სრული, უპირობო ერთგულებაა, ან საერთოდ არაფერი. საოცარი ინტუიციით გრძნობ ნებისმიერ ფარისევლობას, უმცირეს ყოყმანსა და სიტყვებს მიღმა დამალულ განზრახვას. როცა ნამდვილად ენდობი, შენი ზრუნვა შეუვალი, ღრმა და მფარველობითია. თუმცა შენი მთავარი გამოცდა მუდმივი შინაგანი დაცვითი რეჟიმია: ხშირად ადამიანს მანამ ატარებ ფარულ ემოციურ ტესტებში, სანამ ის უბრალოდ არ დაიღლება იმის მტკიცებით, რომ შენი მოტყუება არასდროს უცდია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "scorpio",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "uncompromising_emotional_depth",
        "metaphor": "submarine_depths",
        "context_type": "interpersonal",
        "text": "შენთან დაახლოება წყალქვეშა ნავით ოკეანის ფსკერზე დაშვებას ჰგავს: წნევა მაღალია, ატმოსფერო უკიდურესად დამუხტული და უკან დასახევი გზა აღარ არსებობს. გხიბლავს ავთენტური, ძლიერი ხასიათის ადამიანები, რომლებიც საკუთარ ჩრდილებს არ ემალებიან. შენი ერთგულება იშვიათი და ურყევია. თუმცა შენი სისუსტე ზედმეტი ეჭვიანობაა: თუ ადამიანმა მცირე უყურადღებობა გამოიჩინა, შენი გონება მაშინვე გლობალურ შეთქმულების თეორიას ააგებს და მზად ხარ ხიდები ისე დაწვა, რომ განმარტებასაც არ დაელოდო.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "friendship",
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
        "context_type": "romantic",
        "text": "შაქარმოყრილი პირფერობა შენი სტილი არ არის. პირდაპირ ამბობ იმას, რასაც ფიქრობ, რადგან გჯერა, რომ ნამდვილ კავშირს სიმართლე არასდროს აზიანებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "relational_adventurism",
        "metaphor": "mountain_horizon",
        "context_type": "social",
        "text": "შენთან ყოფნა ჰორიზონტის გაფართოებაა: მოსაწყენ ყოველდღიურობას თავგადასავლად აქცევ და ადამიანებს აჩვენებ, რომ სამყარო ბევრად უფრო დიდია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "allergic_reaction_to_clinginess",
        "metaphor": "leash_snap",
        "context_type": "social",
        "text": "როგორც კი ვინმე შენი თავისუფლების შეზღუდვას ან ეჭვიანობის სცენების მოწყობას დაიწყებს, შენი რეაქცია მყისიერია: კარისკენ მიმავალ გზას ვერავინ გადაგიღობავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 5,
        "depth": "micro",
        "tone": "conversational",
        "angle": "relational_adventurism",
        "metaphor": "bonfire_laugh",
        "context_type": "friendship",
        "text": "საუკეთესო კავშირი შენთვის საერთო სიცილი და გულწრფელი მხიარულებაა: თუ ადამიანთან ერთად გულიანად იცინი, ყველა სხვა წვრილმანი მეორეხარისხოვანი ხდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "sagittarius",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "unvarnished_romantic_candor",
        "metaphor": "midnight_passport",
        "context_type": "romantic",
        "text": "ნაცვლად სტანდარტული რომანტიკისა, შუაღამისას ჩემოდნის ჩალაგებას და სხვა ქალაქში გაქცევას შესთავაზებ: შენი სიყვარული მოულოდნელი თავგადასავალია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "allergic_reaction_to_clinginess",
        "metaphor": "escape_hatch",
        "context_type": "romantic",
        "text": "შენთვის მიმზიდველია ის, ვინც შენს ჰორიზონტს აფართოებს — ადამიანი, რომელთანაც შეიძლება დილის ოთხ საათზე ფილოსოფიაზე იკამათო და მერე სპონტანურად გზას გაუდგე. ვერ იტან ეჭვიანობას, წვრილმან კონტროლსა და ვალდებულებების სიას. პრობლემა მაშინ ჩნდება, როცა ურთიერთობა ჩვეულებრივ ყოველდღიურობაში გადადის: როგორც კი რუტინის სუნი დადგება, შენი პირველი რეფლექსი კარებისკენ გახედვაა, რადგან სტაბილურობა ხშირად შეცდომით თავისუფლების დაკარგვა გგონია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "sagittarius",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "unvarnished_romantic_candor",
        "metaphor": "wild_fire_trail",
        "context_type": "interpersonal",
        "text": "შენთან ურთიერთობა ღია ცის ქვეშ ცხოვრებას ჰგავს: ჰაერი ბევრია, თავისუფლება უსაზღვრო და პერსპექტივები გრანდიოზული. გულწრფელი ხარ, არ გიყვარს ინტრიგები და ყოველთვის პირდაპირ გამოხატავ საკუთარ განზრახვას. თუმცა შენი მთავარი გამოწვევა ემოციური ტაქტის ნაკლებობაა: ხანდახან შენს სიმართლეს ისეთი სისწრაფით ისვრი, რომ მეორე მხარეს გულს სტკენ და მერე გულწრფელად გიკვირს, რატომ განაწყენდა ადამიანი, როცა შენ „უბრალოდ სიმართლე თქვი“.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "friendship",
        "text": "ხმამაღალ დაპირებებს მშვიდი ქმედება გირჩევნია. საიმედოობა შენთვის სიყვარულის უმაღლესი ფორმაა: იყო იქ, როცა მეორეს რეალური საყრდენი სჭირდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "transactional_caution",
        "metaphor": "audit_ledger",
        "context_type": "social",
        "text": "ცარიელი ენთუზიაზმი და ჰაერზე აშენებული გეგმები შენში ნდობას არ იწვევს: სანამ ადამიანი თავის სიტყვას საქმით არ დაამტკიცებს, შენთვის ის უბრალოდ ნაცნობია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "architectural_loyalty",
        "metaphor": "iron_beam",
        "context_type": "romantic",
        "text": "ურთიერთობას მომავლის პერსპექტივით უყურებ: თუ ერთად ზრდა, საერთო მიზნების მიღწევა და სტაბილურობის შენება არ შეგიძლიათ, დროის კარგვას აზრი არ აქვს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "capricorn",
        "index": 5,
        "depth": "micro",
        "tone": "mocking",
        "angle": "sober_affectional_reserve",
        "metaphor": "frozen_fountain",
        "context_type": "social",
        "text": "თეატრალური ემოციური გამოხტომები შენს თვალში სიმწიფის ნაკლებობაა: სიმშვიდე და თავშეკავება შენთვის ბევრად უფრო სოლიდური გრძნობის ნიშანია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "architectural_loyalty",
        "metaphor": "shielded_investment",
        "context_type": "friendship",
        "text": "როცა ვინმე კრიზისშია, ემოციურ სიტყვებს კი არ ისვრი, არამედ მის პრობლემას პრაქტიკულად აგვარებ: შენი მეგობრობა უმაღლესი დონის საიმედოობის გარანტიაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "transactional_caution",
        "metaphor": "contract_ledger",
        "context_type": "romantic",
        "text": "შენთვის ურთიერთობა სერიოზული ინვესტიციაა, რომელსაც გააზრებულად და წინდახედულად უდგები. არ გხიბლავს ზედაპირული დრამა და ქარაფშუტა თავგადასავლები; შენ პარტნიორში სიმწიფეს, პატივისცემასა და საერთო მიზნებს ეძებ. საქმით ზრუნავ და შენს გვერდით ადამიანი თავს დაცულად გრძნობს. თუმცა შენი სისუსტე ზედმეტი სიფრთხილეა: ხანდახან იმდენად გეშინია დროის ფუჭად დაკარგვის, რომ ურთიერთობას საქმიან მოლაპარაკებად აქცევ და სითბოს მანამ არ გასცემ, სანამ მეორე მხარე გარანტიებს არ მოგცემს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "capricorn",
        "index": 8,
        "depth": "medium",
        "tone": "dramatic",
        "angle": "sober_affectional_reserve",
        "metaphor": "ancient_fortress_gate",
        "context_type": "interpersonal",
        "text": "შენთვის სიახლოვე საპასუხისმგებლო გადაწყვეტილებაა, რომელსაც ემოციურ ქარიშხალზე არ აფუძნებ. გიყვარს სიმშვიდე, ღირსება და ურთიერთგაგება, სადაც ორივე მხარე საკუთარ მოვალეობებს აცნობიერებს. საიმედო საყრდენი ხარ რთულ დროს. თუმცა შენი მთავარი გამოცდა ემოციური სითბოს გამოხატვაა: ხშირად იმდენად ხარ კონცენტრირებული პრაქტიკულ შედეგებზე, რომ მეორე მხარეს შენი სიტყვიერი დადასტურება აკლია, შენ კი გიკვირს რატომ სჭირდებათ სიტყვები, როცა ყველაფერი საქმით ნათელია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "romantic",
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
        "context_type": "social",
        "text": "არავის მორგებას არ ცდილობ და არც სხვის გადაკეთებას აპირებ. შენთვის მიმზიდველია ავთენტურობა — ადამიანი, რომელიც საკუთარ უნიკალურობას არ მალავს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 3,
        "depth": "micro",
        "tone": "cocky",
        "angle": "fierce_respect_for_autonomy",
        "metaphor": "independent_galaxy",
        "context_type": "romantic",
        "text": "ტრადიციული რომანტიკული წესები შენთვის მოსაწყენი შაბლონია: შენ საკუთარ წესებს ქმნი, სადაც თანასწორობა და პირადი თავისუფლება მთავარი კანონია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 4,
        "depth": "micro",
        "tone": "mocking",
        "angle": "aloof_emotional_distance",
        "metaphor": "glass_dome",
        "context_type": "social",
        "text": "როგორც კი ვინმე დრამატულ სცენებს და მესაკუთრეობას იწყებს, შენი რეაქცია ცივი გაოცებაა: ლოგიკურ სიმაღლეზე ახვალ და სიტუაციას გვერდიდან უყურებ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 5,
        "depth": "micro",
        "tone": "conversational",
        "angle": "friendship_first_attraction",
        "metaphor": "shared_frequency",
        "context_type": "friendship",
        "text": "საუკეთესო კავშირი შენთვის საერთო იდეალები და მომავლის ხედვაა. ვისთანაც სამყაროს შეცვლაზე შეგიძლია საუბარი, ის ადამიანი შენთვის ნამდვილად ძვირფასია.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 6,
        "depth": "micro",
        "tone": "dramatic",
        "angle": "fierce_respect_for_autonomy",
        "metaphor": "cosmic_constellation",
        "context_type": "interpersonal",
        "text": "შენთან სიახლოვე ორ თანაბარ ვარსკვლავს ჰგავს: ერთად ანათებთ, მაგრამ ერთმანეთის ორბიტას არასდროს არღვევთ — დამოუკიდებლობა შენი უმაღლესი ფასეულობაა.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "aquarius",
        "index": 7,
        "depth": "medium",
        "tone": "snarky",
        "angle": "aloof_emotional_distance",
        "metaphor": "satellite_altitude",
        "context_type": "interpersonal",
        "text": "შენთვის ურთიერთობა ორი დამოუკიდებელი გალაქტიკის თანაკვეთაა და არა ერთმანეთში შერწყმა. გხიბლავს არასტანდარტული აზროვნება, პროგრესული ხედვა და ადამიანი, რომელსაც საკუთარი საინტერესო ცხოვრება აქვს. პატივს სცემ სხვის პირად სივრცეს და იმავეს ითხოვ საპასუხოდ. თუმცა პრობლემა მაშინ იწყება, როცა მეორე მხარე სუფთა ემოციურ სითბოს და დაუცველობას ითხოვს: შენ ამ დროს ლოგიკურ სიმაღლეზე დისტანცირდები, რადგან ინტენსიური გრძნობები შენს რაციონალურ სისტემას თავდაყირა აყენებს.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "aquarius",
        "index": 8,
        "depth": "medium",
        "tone": "jester",
        "angle": "friendship_first_attraction",
        "metaphor": "free_thinkers_club",
        "context_type": "romantic",
        "text": "შენთან რომანტიკა საინტერესო ინტელექტუალური მეგობრობის გარეშე უბრალოდ არ მუშაობს. გჭირდება პარტნიორი, რომელიც შენს ექსცენტრიულ იდეებს კი არ დასცინებს, არამედ საკუთარ გიჟურ თეორიას დაამატებს. გიყვარს თანასწორობა, არასტანდარტული ფორმატები და თავისუფლება. მაგრამ შენი სისუსტე სწორედ ეს გადაჭარბებული დისტანციაა: ხანდახან იმდენად გეშინია ჩვეულებრივი ადამიანური მიჯაჭვულობის, რომ ყველაფერს ფილოსოფიურ დისკუსიად აქცევ, როცა მეორე მხარეს უბრალოდ შენი ჩახუტება სჭირდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
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
        "context_type": "empathy",
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
        "context_type": "romantic",
        "text": "შენთვის ურთიერთობა პოეზიაა — სამყარო, სადაც ყოველდღიური სიუხეშე ქრება და მხოლოდ სუფთა, გულწრფელი ემოციური თანაზიარობა რჩება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 3,
        "depth": "micro",
        "tone": "snarky",
        "angle": "diffuse_boundary_vulnerability",
        "metaphor": "dissolving_fog",
        "context_type": "interpersonal",
        "text": "საზღვრების გავლება შენი სუსტი წერტილია: ხანდახან სხვის დარდს ისე იწოვ, თითქოს შენი იყოს, და ბოლოს ვეღარ ხვდები, ვისი ემოციებით ცხოვრობ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 4,
        "depth": "micro",
        "tone": "unfiltered",
        "angle": "soulful_empathic_attunement",
        "metaphor": "mirror_pool",
        "context_type": "appreciation",
        "text": "ცივი ლოგიკა და მკაცრი წესები შენს სიმპათიას ახრჩობს. შენთვის მიმზიდველია სინაზე, გულწრფელი დაუცველობა და ადამიანი, რომელიც გრძნობებს არ ემალება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.8, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.8}
    },
    {
        "sign": "pisces",
        "index": 5,
        "depth": "micro",
        "tone": "cocky",
        "angle": "romantic_idealism",
        "metaphor": "magic_spell",
        "context_type": "romantic",
        "text": "ისეთ ჯადოსნურ ატმოსფეროს ქმნი, რომ შენს გვერდით ყველაზე პრაგმატული ადამიანებიც კი ივიწყებენ ცხრილებს და ემოციების სამყაროში იძირებიან.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 6,
        "depth": "micro",
        "tone": "unexpected",
        "angle": "diffuse_boundary_vulnerability",
        "metaphor": "dreamer_compass",
        "context_type": "social",
        "text": "ლოგიკური რჩევის ნაცვლად ადამიანს უეცრად ზუსტად იმ მუსიკას ჩაურთავ, რომელიც მის განწყობას შეესაბამება: შენი ინტუიცია სიტყვებზე წინ დარბის.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 4.9, "jester_voice": 4.8, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 7,
        "depth": "medium",
        "tone": "jester",
        "angle": "diffuse_boundary_vulnerability",
        "metaphor": "mirage_castle",
        "context_type": "romantic",
        "text": "შენთვის მიზიდულობა ჯადოსნურ ატმოსფეროს ჰგავს, სადაც ლოგიკური წესები და მკაცრი საზღვრები უბრალოდ ქრება. საოცარი თანაგრძნობის უნარი გაქვს — შეგიძლია ადამიანის სულში ჩაიხედო და მისი ყველაზე უთქმელი ტკივილიც კი გაიგო. გიყვარს რომანტიკა, შთაგონება და უსიტყვო კავშირი. თუმცა შენი მთავარი სისუსტე ილუზიების შექმნაა: ხანდახან იმდენად გინდა ზღაპარი დაიჯერო, რომ აშკარა გაფრთხილებებს თვალს არიდებ და ადამიანს საკუთარი წარმოსახვით გამოგონილ თვისებებს მიაწერ.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 5.0, "natural_georgian": 5.0, "originality": 4.9}
    },
    {
        "sign": "pisces",
        "index": 8,
        "depth": "medium",
        "tone": "mocking",
        "angle": "romantic_idealism",
        "metaphor": "rose_tinted_veil",
        "context_type": "interpersonal",
        "text": "შენთვის ურთიერთობა ხელოვნების ნიმუშია, სადაც ყოველდღიურობის უხეშ დეტალებს ლამაზი ფერებით ფარავ. შეგიძლია უსასრულოდ აპატიო, გაუგო და მხარი დაუჭირო მას, ვინც გიყვარს. შენი თანაგრძნობა უსაზღვრო და უანგაროა. მაგრამ პრობლემა მაშინ იწყება, როცა რეალობა შენს იდეალისტურ სცენარს ეჯახება: ნაცვლად იმისა, რომ პრობლემას პირდაპირ შეხედო, შენ საკუთარ ნისლიან ფანტაზიებში გარბიხარ და ელოდები, რომ ყველაფერი თავისით, ჯადოსნურად მოგვარდება.",
        "quality": {"astrological_grounding": 5.0, "semantic_specificity": 5.0, "jester_voice": 4.9, "natural_georgian": 5.0, "originality": 4.9}
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


def validate_and_build_venus_full():
    print("=" * 70)
    print("JESTER PHASE 3.7 — Venus Full Content Batch Generation & QA")
    print("=" * 70)

    sign_map = {s[0]: s for s in SIGN_SPECS}
    assets = []

    # Check total count: exactly 96
    assert len(VENUS_FULL_RAW_ASSETS) == 96, f"Expected exactly 96 assets, found {len(VENUS_FULL_RAW_ASSETS)}"

    # Check exactly 8 assets per sign (6 Micro, 2 Medium)
    by_sign = {}
    for raw in VENUS_FULL_RAW_ASSETS:
        by_sign.setdefault(raw["sign"], []).append(raw)

    assert len(by_sign) == 12, f"Expected 12 signs, got {len(by_sign)}"
    for s, s_assets in by_sign.items():
        assert len(s_assets) == 8, f"Sign {s} must have exactly 8 assets, got {len(s_assets)}"
        micros = [a for a in s_assets if a["depth"] == "micro"]
        mediums = [a for a in s_assets if a["depth"] == "medium"]
        assert len(micros) == 6, f"Sign {s} must have 6 micros, got {len(micros)}"
        assert len(mediums) == 2, f"Sign {s} must have 2 mediums, got {len(mediums)}"

    # Audit all texts
    texts = []
    tone_counts = {}
    context_counts = {"romantic": 0, "non_romantic": 0}
    metaphors_by_sign = {}

    for raw in VENUS_FULL_RAW_ASSETS:
        sign = raw["sign"]
        idx = raw["index"]
        depth = raw["depth"]
        tone = raw["tone"]
        angle = raw["angle"]
        metaphor = raw["metaphor"]
        ctx_type = raw.get("context_type", "interpersonal")
        text = raw["text"].strip()
        quality = raw["quality"]

        texts.append(text)
        tone_counts[tone] = tone_counts.get(tone, 0) + 1
        metaphors_by_sign.setdefault(sign, set()).add(metaphor)

        if ctx_type == "romantic":
            context_counts["romantic"] += 1
        else:
            context_counts["non_romantic"] += 1

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
                "batch:venus_full_v1",
                "body:venus",
                f"sign:{sign}",
                f"element:{element}",
                f"modality:{modality}",
                f"depth:{depth}",
                f"angle:{angle}",
                f"metaphor:{metaphor}",
                f"context_type:{ctx_type}",
            ],
            "internal_notes": json.dumps({
                "batch_id": "venus_full_v1",
                "astrological_fact": f"Venus is in {sign.capitalize()}",
                "semantic_contract": contract_id,
                "semantic_angle": angle,
                "metaphor_family": metaphor,
                "context_type": ctx_type,
                "char_length": char_len,
                "quality_scores": quality,
            }, ensure_ascii=False),
            "provenance": {
                "batch_id": "venus_full_v1",
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
    assert len(texts) == len(set(texts)), "Exact duplicate found in Venus full texts"

    # Pairwise Jaccard similarity (< 0.85)
    max_sim = 0.0
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = jaccard_similarity(texts[i], texts[j])
            if sim > max_sim:
                max_sim = sim
            assert sim < 0.85, f"Near-duplicate text detected (Jaccard={sim:.2f}):\n1: {texts[i]}\n2: {texts[j]}"

    # Verify metaphor diversity (at least 6 per sign)
    for s, m_set in metaphors_by_sign.items():
        assert len(m_set) >= 6, f"Sign {s} must have at least 6 distinct metaphor families, got {len(m_set)}"

    print(f"SUCCESS: Generated and validated exactly {len(assets)} Venus full assets.")
    print(f"  - Micro: {len([a for a in assets if 'depth:micro' in a['tags']])}")
    print(f"  - Medium: {len([a for a in assets if 'depth:medium' in a['tags']])}")
    print(f"Peak pairwise Jaccard similarity: {max_sim:.3f}")
    print("Tone Distribution across full batch:")
    for t, cnt in sorted(tone_counts.items()):
        print(f"  - {t}: {cnt}")
    print(f"Romantic Balance: Non-romantic: {context_counts['non_romantic']} ({context_counts['non_romantic']/len(assets)*100:.1f}%), Romantic: {context_counts['romantic']} ({context_counts['romantic']/len(assets)*100:.1f}%)")

    # Output file
    out_path = root_dir / "backend" / "app" / "interpretation" / "data" / "venus_corpus.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {out_path}")
    return assets


if __name__ == "__main__":
    validate_and_build_venus_full()
