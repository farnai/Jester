"""
Seed data builder for 12 Friendship / Platonic semantic interpretation contracts.
Zero astrology jargon; strictly focused on platonic chemistry, banter,
shared humor, low-maintenance loyalty, safe haven dynamics, and Jester twists.
"""
from scripts.corpus_builders.common import ContractSeedData


def get_friendship_contracts_data() -> list[ContractSeedData]:
    contracts: list[ContractSeedData] = []

    friendship_defs = [
        (
            "friendship.chemistry.instant_rapport.v1",
            [
                "თქვენს მეგობრობაში პირველივე შეხვედრიდან ისეთი სიმსუბუქე გაჩნდა, თითქოს სკოლის მერხიდან იცნობდეთ ერთმანეთს",
                "უცნაური უხერხულობის ფაზა თქვენს ურთიერთობას საერთოდ არ ჰქონია",
                "ერთად ყოფნა ისეთივე ბუნებრივია, როგორც ძველი კომფორტული ტანსაცმლის ჩაცმა",
            ],
            [
                "პირველივე დღიდან გასაგები იყო, რომ თქვენ ორს ერთად ბევრი საერთო ისტორია გელოდათ.",
                "არანაირი ფორმალობა და თავის მოჩვენება; აქ პირდაპირ საქმეზე გადახვედით.",
                "ეს ის მეგობრობაა, რომელიც წამებში იბადება და წლობით ძლებს.",
            ],
            [
                "Zero awkward warm-up phase was needed; you clicked from the first five minutes",
                "Being around each other felt immediately familiar and completely unforced",
            ],
            [
                "You skipped polite formalities and went straight to laughing like lifelong conspirators.",
                "Natural rapport made you feel like old friends before you even learned each other's full names.",
            ],
        ),
        (
            "friendship.communication.effortless_banter.v1",
            [
                "თქვენი საუბარი ისეთი სისწრაფითა და სიმსუბუქით მიდის, რომ საათები წუთებივით გარბის",
                "ერთმანეთის ხუმრობებს ჰაერშივე იჭერთ და მაშინვე ახალ რეპლიკას ამატებთ",
                "თემების ნაკლებობა თქვენთან უბრალოდ არ არსებობს; ყველაფერზე შეგიძლიათ საათობით ლაპარაკი",
            ],
            [
                "მაყურებლისთვის თქვენი დიალოგი მზა კომედიური სერიალის სცენარს ჰგავს.",
                "სანამ სხვები თემას ეძებენ, თქვენ უკვე მეხუთე პარალელურ ამბავს განიხილავთ.",
                "ეს ის ურთიერთობაა, სადაც სიცილი საუკეთესო თერაპიაა.",
            ],
            [
                "Your banter moves with frictionless ping-pong speed and sharp punchlines",
                "Running out of things to discuss is an impossibility whenever you two get together",
            ],
            [
                "An eavesdropper would swear you two had rehearsed your comedy bits for years.",
                "You leap from mundane observations to absurd theories without breaking stride.",
            ],
        ),
        (
            "friendship.communication.shared_absurdity.v1",
            [
                "სამყაროს აბსურდულობაზე ზუსტად ერთნაირად გეცინებათ და ერთსა და იმავე დეტალებს ამჩნევთ",
                "თქვენი შიდა ხუმრობები იმდენად სპეციფიკურია, რომ სხვებისთვის მათი ახსნა შეუძლებელია",
                "სერიოზულ სიტუაციებშიც კი საკმარისია ერთმანეთს თვალი შეავლოთ, რომ სიცილი ძლივს შეიკავოთ",
            ],
            [
                "ერთი გამოხედვაც კმარა იმისთვის, რომ ორივემ ზუსტად იცოდეთ, რა გაიფიქრა მეორემ.",
                "თქვენი იუმორის გრძნობა სარკისებურია და ეს უდიდესი იღბალია.",
                "მთავარია, მნიშვნელოვან შეხვედრებზე ერთმანეთის გვერდით არ დასხდეთ.",
            ],
            [
                "You laugh at the exact same absurdities that completely elude everyone else",
                "Your collection of hyper-specific inside jokes requires an encrypted dictionary",
            ],
            [
                "A single shared glance across a serious room is enough to trigger suppressed laughter.",
                "Never sit next to each other at formal events; your composure will not survive.",
            ],
        ),
        (
            "friendship.harmony.synchronous_pace.v1",
            [
                "თქვენი სოციალური ენერგია და რიტმი საოცრად ემთხვევა ერთმანეთს",
                "არცერთი არ აჩქარებს მეორეს და არც დავიწყებულად გრძნობს თავს",
                "ერთად გასეირნებაც და უბრალოდ ჩუმად ყოფნაც თანაბრად კომფორტულია",
            ],
            [
                "არავინ ითხოვს ზედმეტ ყურადღებას; თქვენი ტემპი სრულ სინქრონშია.",
                "თქვენ იცით, როდის არის დრო აქტიურობის და როდის — მშვიდად განტვირთვის.",
                "ეს ის იშვიათი ბალანსია, სადაც ერთად ყოფნა არასდროს ღლის.",
            ],
            [
                "Your social batteries recharge and deplete on nearly identical schedules",
                "Neither person feels rushed to keep up or abandoned in slow motion",
            ],
            [
                "Hanging out feels entirely pressure-free; zero performance anxiety exists here.",
                "You can comfortably share silence without anyone feeling awkward.",
            ],
        ),
        (
            "friendship.stability.unconditional_cushion.v1",
            [
                "როცა ცხოვრებაში რაღაც აირევა, იცი, ვის უნდა დაურეკო ყოველგვარი ყოყმანის გარეშე",
                "თქვენს შორის არის მყარი თანადგომა, რომელიც მორალის კითხვასა და შეფასებებს გამორიცხავს",
                "ერთმანეთის ზურგს ისე უმაგრებთ, რომ მტკიცებულებები არ გჭირდებათ",
            ],
            [
                "აქ არავინ გეტყვის 'ხომ გეუბნებოდი'; აქ უბრალოდ მოვლენ და პრობლემას ერთად მოაგვარებთ.",
                "ნამდვილი მეგობრობა სწორედ ასეთ უპირობო საყრდენში გამოიხატება.",
                "ეს ის ზურგია, რომლის იმედიც ნებისმიერ დროს შეგიძლიათ გქონდეთ.",
            ],
            [
                "When life gets chaotic, this is the first number called without a second thought",
                "Support arrives here without patronizing lectures or I-told-you-so commentary",
            ],
            [
                "Zero judgment, zero preachy speeches; just immediate practical backup.",
                "Having a safety net this sturdy makes taking risks in life much easier.",
            ],
        ),
        (
            "friendship.stability.quiet_loyalty.v1",
            [
                "თვეებიც რომ არ გქონდეთ კონტაქტი, შეხვედრისას ზუსტად იქიდან აგრძელებთ, სადაც გაჩერდით",
                "ეს არის დაბალი მოთხოვნილებების, მაგრამ უმაღლესი სანდოობის მეგობრობა",
                "თქვენ არ გჭირდებათ ყოველდღიური გადამოწმება იმის დასამტკიცებლად, რომ მეგობრები ხართ",
            ],
            [
                "დრო და მანძილი ამ კავშირს ვერაფერს აკლებს; საფუძველი უკვე მყარია.",
                "აქ არ არის პრეტენზიები 'რატომ არ მირეკავდი'; არის მხოლოდ გულწრფელი სიხარული ნახვისას.",
                "ეს ის მეგობრობაა, რომელიც მთელი ცხოვრება ჩუმად და საიმედოდ მიგყვება.",
            ],
            [
                "Months can pass in silence, yet you pick up mid-sentence without missing a beat",
                "This is low-maintenance, high-fidelity loyalty that never demands proof of life",
            ],
            [
                "Zero guilt trips about unanswered texts; just instant, warm continuity upon reunion.",
                "Time and geographic distance make zero dent in the bedrock of this trust.",
            ],
        ),
        (
            "friendship.notice.autonomous_bond.v1",
            [
                "ერთმანეთის პირად ცხოვრებას, დროსა და არჩევანს სრული თავისუფლებით ეკიდებით",
                "თქვენს მეგობრობაში არ არის მესაკუთრეობა და ეჭვიანობა სხვა წრეების მიმართ",
                "თქვენ ორი დამოუკიდებელი ადამიანი ხართ, რომელთა გზებიც სასიამოვნოდ იკვეთება",
            ],
            [
                "თავისუფლება აქ მეგობრობას კიდევ უფრო ღირებულს და გულწრფელს ხდის.",
                "თითოეულს გაქვთ საკუთარი სამყარო, რაც შეხვედრებს ყოველთვის საინტერესოს ტოვებს.",
                "ეს არის ზრდასრული ადამიანების მეგობრობა ყოველგვარი ზედმეტი დრამის გარეშე.",
            ],
            [
                "Neither person displays possessiveness regarding outside social circles",
                "Total autonomy keeps the connection healthy, mature, and drama-free",
            ],
            [
                "You celebrate each other's independent trajectories with zero territorial insecurity.",
                "Two sovereign lives intersecting by genuine enjoyment rather than obligation.",
            ],
        ),
        (
            "friendship.social.crew_catalyst.v1",
            [
                "როცა ერთად ჩნდებით კომპანიაში, საერთო განწყობა მომენტალურად იწევს მაღლა",
                "თქვენი ერთობლივი ენერგია ნებისმიერ შეკრებას ცოცხალ თავგადასავლად აქცევს",
                "თქვენ არამხოლოდ ერთმანეთს ავსებთ, არამედ გარშემომყოფებსაც აერთიანებთ",
            ],
            [
                "თქვენ ორნი ნებისმიერი წვეულების ან შეხვედრის მთავარი კატალიზატორი ხართ.",
                "სადაც თქვენ ხართ, იქ მოსაწყენი საუბრები წამებში ქრება.",
                "თქვენი დუეტი გუნდურ ენერგიას ორმაგად აძლიერებს.",
            ],
            [
                "Whenever you two show up together, the collective energy in the room leaps up",
                "You function as an organic social catalyst that turns standard gatherings into adventures",
            ],
            [
                "You do not just entertain each other; you light up the whole table effortlessly.",
                "Your shared chemistry turns any standard Friday night into an unforgettable story.",
            ],
        ),
        (
            "friendship.communication.intellectual_sparring.v1",
            [
                "ერთმანეთს უზიარებთ საინტერესო წიგნებს, იდეებსა და პროვოკაციულ მოსაზრებებს",
                "თქვენი დისკუსიები ნამდვილი გონებრივი ვარჯიშია, სადაც აზროვნება იხვეწება",
                "თქვენ არ ერიდებით განსხვავებულ პოზიციებზე კამათს, რადგან პროცესი თავად გაინტერესებთ",
            ],
            [
                "კამათი აქ მეგობრობას კი არ აზიანებს, არამედ ურთიერთპატივისცემას ზრდის.",
                "თქვენ ერთად იზრდებით ინტელექტუალურად და ერთმანეთს ახალ ჰორიზონტებს უხსნით.",
                "ეს ის მეგობრობაა, სადაც ყოველი საუბრის შემდეგ ახალი იდეებით ბრუნდები შინ.",
            ],
            [
                "Brainstorming together feels like an exhilarating intellectual sparring session",
                "You test provocative theses against each other with zero bruised egos",
            ],
            [
                "Fierce debate strengthens the bond rather than threatening it.",
                "You walk away from every discussion with three new books to read and a sharper perspective.",
            ],
        ),
        (
            "friendship.harmony.judgment_free_refuge.v1",
            [
                "ეს არის ადგილი, სადაც შეგიძლია იყო სრულიად არასრულყოფილი და შენი სისუსტეები არ დამალო",
                "ერთმანეთთან არ გჭირდებათ წარმატებული ნიღბის ტარება; აქ რეალური სახეებია დაფასებული",
                "თქვენი საუბრები სავსეა გულწრფელობით, რომელიც დღეს იშვიათად მოიპოვება",
            ],
            [
                "აქ ყველაზე უცნაური ფიქრების გაზიარებაც კი სრულიად უსაფრთხოა.",
                "ეს თავშესაფარია, სადაც გარე სამყაროს შეფასებები კარს მიღმა რჩება.",
                "მეგობრობა, სადაც სრულიად საკუთარი თავი ხარ, უდიდესი საჩუქარია.",
            ],
            [
                "This connection offers an unfiltered safe haven where all masks come off",
                "You do not need to perform success or conceal awkward flaws around each other",
            ],
            [
                "Sharing embarrassing mistakes is met with compassionate laughter and zero judgment.",
                "A rare emotional refuge where being fully human is not just tolerated, but celebrated.",
            ],
        ),
        (
            "friendship.growth.playful_rivalry.v1",
            [
                "თქვენს შორის მუდმივად არის მეგობრული შეჯიბრი, რომელიც ორივეს განვითარებას აიძულებს",
                "ერთმანეთის წარმატება გაძლევთ მოტივაციას, რომ თავადაც უფრო მაღლა ახვიდეთ",
                "იუმორისტული წაკბენა და გამოწვევები თქვენი მეგობრობის მთავარი ძრავია",
            ],
            [
                "ეს მეტოქეობა შურით კი არა, უდიდესი პატივისცემითა და სიყვარულით არის სავსე.",
                "თქვენ არ აძლევთ ერთმანეთს ზარმაცობის უფლებას; მუდმივად წინ უბიძგებთ.",
                "როცა ერთი იმარჯვებს, მეორე პირველი ულოცავს და შემდეგ თავად იწყებს ვარჯიშს.",
            ],
            [
                "A playful competitive streak continuously pushes both of you to level up",
                "Roasting each other with love keeps your feet firmly planted on the ground",
            ],
            [
                "Rivalry here is rooted in deep admiration rather than petty insecurity.",
                "You never let each other settle for mediocre output; you set the bar high together.",
            ],
        ),
        (
            "friendship.growth.opposite_strengths.v1",
            [
                "რაშიც ერთი სუსტია, იქ მეორე ბრწყინავს — თქვენ იდეალურად ფარავთ ერთმანეთის ბრმა ზონებს",
                "ერთის პრაქტიკული რეალიზმი და მეორის გიჟური იდეები ერთად საოცარ ტანდემს ქმნის",
                "თქვენი განსხვავებული ხასიათები პრობლემების გადაჭრას ორჯერ უფრო ეფექტურს ხდის",
            ],
            [
                "ერთად თქვენ გაცილებით ძლიერი გუნდი ხართ, ვიდრე ცალ-ცალკე.",
                "თქვენ სწავლობთ იმ თვისებებს, რომლებიც თავად გაკლიათ, და ეს შესანიშნავია.",
                "ეს ის პარტნიორობაა, სადაც განსხვავება სისუსტე კი არა, მთავარი უპირატესობაა.",
            ],
            [
                "Where one hesitates, the other executes; you cover each other's blind spots with precision",
                "One provides visionary spark while the other anchors pragmatic logistics",
            ],
            [
                "As a combined unit, you navigate life far more effectively than either could alone.",
                "Complementary differences turn a good friendship into an indestructible team.",
            ],
        ),
    ]

    for interp_id, ka_p, ka_t, en_p, en_t in friendship_defs:
        contracts.append(
            ContractSeedData(
                interpretation_id=interp_id,
                context="friendship",
                ka_witty_premises=ka_p,
                ka_witty_twists=ka_t,
                ka_playful_premises=ka_p[1:] + [ka_p[0]],
                ka_playful_twists=ka_t[1:] + [ka_t[0]],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1] if len(ka_p) > 1 else ka_p[0]],
                ka_savage_twists=[ka_t[0]],
                en_witty_premises=en_p,
                en_witty_twists=en_t,
                en_playful_premises=en_p[::-1],
                en_playful_twists=en_t[::-1],
                en_soft_premises=[en_p[0]],
                en_soft_twists=[en_t[0]],
                en_bold_premises=[en_p[-1]],
                en_bold_twists=[en_t[-1]],
                en_savage_premises=[en_p[0]],
                en_savage_twists=[en_t[0]],
            )
        )

    return contracts
