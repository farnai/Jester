"""
Seed data builder for 43 Self / Me semantic interpretation contracts.
Covers Sun signs (identity), Moon signs (emotional processing),
Ascendants (social persona), Element dominance, and Modality dominance.
Zero astrology jargon; strictly focused on authentic human behavior and Jester punchlines.
"""
from scripts.corpus_builders.common import ContractSeedData


def get_self_contracts_data() -> list[ContractSeedData]:
    contracts: list[ContractSeedData] = []

    # =============================================================
    # 1. SUN IDENTITY CONTRACTS (12)
    # =============================================================
    sun_data = [
        (
            "aries",
            [
                "როცა რაღაცის გაკეთება გინდა, ლოდინს ფიზიკურად ვერ იტან",
                "შენი პირველი იმპულსი ყოველთვის წინ გადახტომაა, სანამ სხვები ჯერ კიდევ გეგმავენ",
                "დიპლომატიურ შემოვლებს პირდაპირი დარტყმა გირჩევნია",
                "მოქმედება შენთვის ფიქრზე სწრაფად იწყება",
            ],
            [
                "სანამ სხვები რისკებს ითვლიან, შენ უკვე ფინიშის ხაზზე დგახარ.",
                "მთავარია, გზაში ვინმემ შენელება არ შემოგთავაზოს — ეგ ყველაზე მეტად გაღიზიანებს.",
                "შენი გულწრფელობა ხანდახან კედელს ანგრევს, მაგრამ სამაგიეროდ ყალბი არასდროსაა.",
                "შენ არ ელი ნებართვას; შენ უბრალოდ იწყებ და სხვებს აიძულებ დაგეწიონ.",
            ],
            [
                "When you decide on something, waiting feels physically painful",
                "Your default instinct is to jump first and figure out the landing later",
                "Diplomatic tip-toeing is not your style; you prefer the direct route",
            ],
            [
                "While others analyze the risks, you are already crossing the finish line.",
                "The quickest way to irritate you is telling you to take it slow.",
                "You do not ask for permission; you set the pace and let others keep up.",
            ],
        ),
        (
            "taurus",
            [
                "შენს სიმშვიდეს ვერაფერი შეარყევს, თუ თავად არ გადაწყვიტე განძრევა",
                "გადაწყვეტილებებს ნელა, მაგრამ სამუდამოდ იღებ",
                "ცხოვრებისგან სიამოვნების მიღება შენთვის ხელოვნებაა და არა შემთხვევითობა",
                "შენს სიტყვას ყოველთვის კონკრეტული წონა და ფასი აქვს",
            ],
            [
                "შენი დაჩქარება შეუძლებელია; რაც უფრო გაწვებიან, მით უფრო მყარად დგახარ.",
                "შენ არ დებ ცარიელ დაპირებებს, სამაგიეროდ რასაც ამბობ, ქვაზეა ნაკვეთი.",
                "კომფორტი შენთვის ფუფუნება კი არა, აუცილებელი სამუშაო პირობაა.",
                "შენი მოთმინება უსაზღვრო ჩანს, სანამ ვინმე შენს საზღვრებს არ გადააბიჯებს.",
            ],
            [
                "Nothing can rush you unless you deliberately decide to move",
                "You make decisions at your own measured pace, but they last forever",
                "Quality and sensory comfort are non-negotiable standards for you",
            ],
            [
                "Pushing you to hurry only makes you dig your heels in deeper.",
                "Your promises are etched in stone, never thrown around carelessly.",
                "You build things designed to outlast the latest trendy noise.",
            ],
        ),
        (
            "gemini",
            [
                "შენი გონება ერთდროულად ხუთ პარალელურ თემაზე მუშაობს",
                "მოსაწყენი საუბრიდან თავის დაღწევის გენიალური ნიჭი გაქვს",
                "შენი ცნობისმოყვარეობა არასდროს ისვენებს, ყველაფერი გაინტერესებს",
                "ინფორმაციას ისეთი სისწრაფით ამუშავებ, სხვები ჩამორჩენას ვერ ასწრებენ",
            ],
            [
                "ერთ თემაზე დიდხანს გაჩერება შენთვის პატიმრობის ტოლფასია.",
                "შენ იცი ცოტ-ცოტა ყველაფერზე და საჭირო მომენტში ზუსტად იყენებ.",
                "შენი დიალოგი ყოველთვის მოულოდნელი ირონიით და გონებამახვილობით სრულდება.",
                "მთავარია, ცხოვრება ერთფეროვან რუტინაში არ ჩაიძიროს, დანარჩენს ეშველება.",
            ],
            [
                "Your brain operates on five browser tabs simultaneously",
                "You have an Olympic-level talent for escaping boring conversations",
                "Insatiable curiosity drives your every waking hour",
            ],
            [
                "Staying locked into one single topic feels like a mental cage to you.",
                "You connect unexpected concepts before others even notice the link.",
                "Routine is your kryptonite; you need mental movement to stay alive.",
            ],
        ),
        (
            "cancer",
            [
                "ოთახში შემოსვლისთანავე გრძნობ უთქმელ განწყობებსა და დაძაბულობას",
                "შენი ახლობლებისთვის ნამდვილი დამცავი ფარი ხარ",
                "ემოციური მეხსიერება იმდენად ღრმა გაქვს, წვრილმანებიც არ გავიწყდება",
                "ნდობას ადვილად არ გასცემ, მაგრამ თუ გაეცი — ბოლომდე ერთგული ხარ",
            ],
            [
                "გარეგნულად მშვიდი ჩანხარ, მაგრამ შიგნით ნამდვილი ემოციური ოკეანეა.",
                "შენი ინტუიცია არასდროს ცდება, თუნდაც ლოგიკა საპირისპიროს ამტკიცებდეს.",
                "ვინც შენს წრეში მოხვდება, ის ნამდვილ მზრუნველობას გაიგებს.",
                "შენი წყენა ჩუმია, მაგრამ ძალიან ღრმა და დიდხანს გასტანს.",
            ],
            [
                "You read the unspoken emotional subtext of a room within seconds",
                "Your protective loyalty toward your inner circle is unbreakable",
                "You keep your private world carefully guarded from casual tourists",
            ],
            [
                "You appear calm on the surface, but your inner currents run deep.",
                "Your gut feelings are rarely wrong, no matter what surface facts say.",
                "Once someone earns your trust, they gain an unshakeable guardian.",
            ],
        ),
        (
            "leo",
            [
                "შენი შემოსვლა ოთახში შეუმჩნეველი არასდროს რჩება",
                "გულუხვობა შენთვის ბუნებრივი ჟესტია და არა გათვლა",
                "შენ გიყვარს ცხოვრება დიდი მასშტაბებით და ნათელი ფერებით",
                "სიამაყე შენი ხერხემალია, რომელსაც ვერავინ მოხრის",
            ],
            [
                "სცენა შენია, მაშინაც კი, როცა უბრალოდ ჩაის სვამ სამზარეულოში.",
                "შენ არ ითხოვ ყურადღებას; ის თავისით მოგყვება, როგორც ჩრდილი.",
                "შენი გული ისეთივე დიდია, როგორც შენი ამბიციები.",
                "მთავარია, შენი დამსახურება სათანადოდ დააფასონ — უყურადღებობას ვერ იტან.",
            ],
            [
                "Your entrance into any space is fundamentally impossible to ignore",
                "Generosity is your natural reflex rather than a calculated posture",
                "You operate with an innate, unapologetic sense of creative pride",
            ],
            [
                "The room naturally centers around you even when you say nothing.",
                "You do not demand attention; it simply gravitates toward your warmth.",
                "Your loyalty and generosity are as grand as your ambitions.",
            ],
        ),
        (
            "virgo",
            [
                "შენი თვალი დეტალს ისეთ ადგილას პოულობს, სადაც სხვები ვერც კი იყურებიან",
                "ქაოსის მოწესრიგება შენთვის თერაპიის ტოლფასია",
                "საქმეს აკეთებ ჩუმად, უნაკლოდ და ზედმეტი დრამის გარეშე",
                "შენი სტანდარტები იმდენად მაღალია, რომ საკუთარ თავსაც იშვიათად ინდობ",
            ],
            [
                "შენი კრიტიკული აზროვნება სინამდვილეში სამყაროს გაუმჯობესების სურვილია.",
                "სანამ სხვები იდეებზე ლაპარაკობენ, შენ უკვე ხარვეზები გაასწორე.",
                "შენს სიჩუმეში უფრო მეტი კომპეტენციაა, ვიდრე სხვების ხმამაღალ განცხადებებში.",
                "შენ არ გჭირდება აპლოდისმენტები, უბრალოდ საქმე უნდა იყოს იდეალურად გაკეთებული.",
            ],
            [
                "Your eye catches micro-flaws that everyone else walked right past",
                "Bringing neat order out of confusing chaos is your quiet superpower",
                "You show care through practical utility rather than dramatic speeches",
            ],
            [
                "While others talk about broad visions, you quietly fix the engine.",
                "Your understated competence speaks louder than any self-promotion.",
                "You do not need applause; you need the system to function flawlessly.",
            ],
        ),
        (
            "libra",
            [
                "კონფლიქტის განმუხტვა ისე შეგიძლია, რომ ვერავინ მიხვდეს, როგორ მოხდა",
                "სილამაზე, ბალანსი და ესთეტიკა შენთვის ცხოვრების საზომია",
                "ნებისმიერ სიტუაციაში ორივე მხარის არგუმენტს თანაბრად ხედავ",
                "შენი მომხიბვლელობა ყველაზე მკაცრ დაცვასაც კი ადვილად ხსნის",
            ],
            [
                "გადაწყვეტილების მიღება გიჭირს იმიტომ, რომ ყველა ალტერნატივის ხიბლს ხედავ.",
                "შენი ღიმილი ხშირად უფრო მეტს წყვეტს, ვიდრე ყველაზე ხისტი მოლაპარაკება.",
                "შენ ქმნი გარემოს, სადაც ყველას უნდა დარჩენა და საუბარი.",
                "მთავარია, სხვების მოსაწონად საკუთარი ინტერესები არ დათმო.",
            ],
            [
                "You can defuse raw tension before anyone even realizes an argument started",
                "Aesthetic equilibrium and balance are your primary life filters",
                "You naturally see the valid kernel of truth in opposing perspectives",
            ],
            [
                "Making decisions is hard only because you see the merit in every option.",
                "Your tactful phrasing solves disputes faster than brute force ever could.",
                "You create an atmosphere where people instinctively want to linger.",
            ],
        ),
        (
            "scorpio",
            [
                "შენს მზერას ვერაფერი გამოეპარება, ადამიანებს რენტგენივით კითხულობ",
                "ზედაპირულობასა და ფასადურ საუბრებს ვერ იტან",
                "შენი ნდობის მოპოვება ურთულესია, მაგრამ დაკარგვა — წამიერი",
                "შენს სიჩუმეში უფრო მეტი ინტენსივობაა, ვიდრე სხვების ყვირილში",
            ],
            [
                "შენი საიდუმლოებები სამუდამოდ შენთან რჩება, სხვისას კი მარტივად ხსნი.",
                "შენთან ან ბოლომდე გულწრფელი უნდა იყო, ან საერთოდ არ უნდა დაიწყო საუბარი.",
                "შენ ფერფლიდან აღდგენის ნამდვილი ოსტატი ხარ.",
                "შენი ინტუიცია ტყუილს რამდენიმე კილომეტრის მანძილზე გრძნობს.",
            ],
            [
                "Your psychological radar cuts through pleasant social facades instantly",
                "Superficial small talk drains your patience within thirty seconds",
                "You possess a formidable regenerative capacity in any crisis",
            ],
            [
                "You either engage with total authenticity or you do not engage at all.",
                "Deception is detected by your instincts before logic catches up.",
                "Your loyalty is absolute, but your boundaries are heavily fortified.",
            ],
        ),
        (
            "sagittarius",
            [
                "თავისუფლება შენთვის ჰაერივით აუცილებელია, ჩარჩოებში ვერ გაჩერდები",
                "სიმართლეს ყოველთვის ისე ამბობ, როგორც არის, შეფუთვის გარეშე",
                "ახალი იდეები და ჰორიზონტები შენს ინტერესს მუდმივად აღვიძებს",
                "შენი ოპტიმიზმი ყველაზე რთულ სიტუაციაშიც კი გამოსავალს პოულობს",
            ],
            [
                "შენი გულწრფელობა ხშირად აოცებს ხალხს, მაგრამ სამაგიეროდ თამაშის გარეშეა.",
                "სანამ სხვები წესებს კითხულობენ, შენ უკვე ახალ მიმართულებას იკვლევ.",
                "შენთან ერთად ყოფნა ნიშნავს მზადყოფნას მოულოდნელი თავგადასავლებისთვის.",
                "მთავარია, ვინმემ შენი ფრთების შეკვეცა არ სცადოს — ეგ შენთვის მიუღებელია.",
            ],
            [
                "Autonomy is your non-negotiable lifeline; cages make you claustrophobic",
                "You deliver frank truth with zero decorative sugar-coating",
                "Your restless curiosity constantly chases broader intellectual horizons",
            ],
            [
                "Your candid honesty might startle people, but there is zero malice in it.",
                "You look at the grand macro picture while others get bogged in details.",
                "Routine confinement is the only thing that can truly dim your fire.",
            ],
        ),
        (
            "capricorn",
            [
                "შენ იცი, რომ რეალური შედეგი მხოლოდ დისციპლინასა და დროს მოაქვს",
                "შენი სიმშვიდე კრიზისის დროს სხვებისთვის საიმედო საყრდენია",
                "ცარიელ ლაპარაკს ყოველთვის კონკრეტული საქმე და ფაქტები გირჩევნია",
                "შენი მიზნები შორსმჭვრეტელია და მათკენ ნაბიჯ-ნაბიჯ, ურყევად მიდიხარ",
            ],
            [
                "სანამ სხვები ენთუზიაზმს კარგავენ, შენ უბრალოდ აგრძელებ მუშაობას.",
                "შენი სტანდარტები მკაცრია, მაგრამ პირველ რიგში საკუთარი თავის მიმართ.",
                "შენ აშენებ ისეთ სტრუქტურას, რომელიც ათწლეულებს გაუძლებს.",
                "ემოციებს საქმეში არ ურევ, რაც ცივი გონებით მოქმედების საშუალებას გაძლევს.",
            ],
            [
                "You understand that enduring results demand relentless discipline",
                "When everyone else panics, your quiet composure takes the wheel",
                "You measure worth by tangible execution rather than grand promises",
            ],
            [
                "While novelty-chasers burn out, you simply keep building brick by brick.",
                "Your standards are uncompromising, starting strictly with yourself.",
                "You climb mountains through patient strategy, not through lucky shortcuts.",
            ],
        ),
        (
            "aquarius",
            [
                "საზოგადოებრივი შაბლონები და გაცვეთილი წესები შენთვის არაფერს ნიშნავს",
                "აზროვნებ მომავლის კატეგორიებით, როცა სხვები ჯერ წარსულში არიან",
                "ინტელექტუალური თავისუფლება შენი ყველაზე დიდი ღირებულებაა",
                "მეგობრობასა და იდეურ თანამოაზრეობას უდიდეს მნიშვნელობას ანიჭებ",
            ],
            [
                "შენი ლოგიკა ხშირად უსწრებს დროს, ამიტომ გაგებას ხანდახან დრო სჭირდება.",
                "შენთან საუბრისას ადამიანი ხვდება, რამდენად ფართო შეიძლება იყოს აზროვნება.",
                "შენ ხარ ინდივიდუალისტი, რომელსაც გულწრფელად ადარდებს დიდი იდეები.",
                "მთავარია, არავინ შეეცადოს შენს მოქცევას ჩვეულებრივ სტანდარტებში.",
            ],
            [
                "Conventional norms and copy-paste lifestyles mean nothing to you",
                "Your thoughts operate on future frameworks while others debate the past",
                "Intellectual sovereignty is your highest personal value",
            ],
            [
                "Your unconventional angles frequently turn accepted wisdom upside down.",
                "Your emotional detachment is not coldness; it is objective perspective.",
                "You belong to your own ideas first and social expectations never.",
            ],
        ),
        (
            "pisces",
            [
                "შენი წარმოსახვა უსაზღვროა და რეალობას საკუთარი ფერებით ავსებს",
                "სხვისი ტკივილისა და განწყობის გაგება სიტყვების გარეშე შეგიძლია",
                "სამყაროს ინტუიციითა და შეგრძნებებით უფრო აღიქვამ, ვიდრე მშრალი ლოგიკით",
                "შენი ემპათია იმდენად ღრმაა, რომ ხანდახან საკუთარი საზღვრები გავიწყდება",
            ],
            [
                "შენი შინაგანი სამყარო იმდენად მდიდარია, რომ რეალობა ხანდახან ვიწრო გეჩვენება.",
                "შენ გრძნობ უხილავ ტალღებს და ადამიანების ნამდვილ ემოციურ მდგომარეობას.",
                "დროდადრო განმარტოება შენთვის ენერგიის აღდგენის ერთადერთი გზაა.",
                "შენი ინტუიცია გზას ყოველთვის გიკვალავს, თუნდაც გზამკვლევი არ გქონდეს.",
            ],
            [
                "Your imagination effortlessly dissolves the boundaries of rigid reality",
                "You absorb ambient moods and unspoken grief without trying",
                "Creative intuition guides you far more reliably than cold statistics",
            ],
            [
                "Your inner world holds more nuance than external facts could ever describe.",
                "Solitude is your necessary sanctuary for resetting your sensitive radar.",
                "Your gentleness is not fragility; it is deep emotional resilience.",
            ],
        ),
    ]

    for sign, ka_p, ka_t, en_p, en_t in sun_data:
        contracts.append(
            ContractSeedData(
                interpretation_id=f"self.identity.sun_{sign}.v1",
                context="self",
                ka_witty_premises=ka_p[:3],
                ka_witty_twists=ka_t[:3],
                ka_playful_premises=ka_p[1:],
                ka_playful_twists=ka_t[1:],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1]],
                ka_savage_twists=[ka_t[1]],
                en_witty_premises=en_p[:2],
                en_witty_twists=en_t[:2],
                en_playful_premises=en_p[1:],
                en_playful_twists=en_t[1:],
                en_soft_premises=[en_p[0]],
                en_soft_twists=[en_t[0]],
                en_bold_premises=[en_p[-1]],
                en_bold_twists=[en_t[-1]],
                en_savage_premises=[en_p[0]],
                en_savage_twists=[en_t[0]],
            )
        )

    # =============================================================
    # 2. MOON EMOTIONAL PROCESSING CONTRACTS (12)
    # =============================================================
    moon_data = [
        (
            "aries",
            ["ემოციური რეაქცია შენთან წამიერია — გაბრაზებაც და პატიებაც სწრაფად მოდის", "თუ რამე გაწუხებს, მაშინვე უნდა თქვა; ემოციების დაგროვება შენთვის უცხოა", "შენი გრძნობები ისეთივე სწრაფია, როგორც შენი ნაბიჯები"],
            ["მთავარია, გრძნობები არ ჩაიკეტოს, თორემ აფეთქება გარდაუვალია.", "სწრაფად იფეთქებ და ორ წუთში ისევ მშვიდად აგრძელებ საუბარს.", "შენი ემოციური გულწრფელობა ყველასთვის ნათელია."],
            ["Your emotional reactivity is immediate and completely unfiltered", "Holding grudges feels like a waste of energy when you can clear the air now"],
            ["You flare up fast and return to calm five minutes later.", "Immediate emotional truth prevents toxic build-up in your life."],
        ),
        (
            "taurus",
            ["ემოციური წონასწორობის აღსადგენად ფიზიკური სიმყუდროვე და სიმშვიდე გჭირდება", "ნერვიულობის დროს უეცარი ცვლილებები ყველაზე მეტად გძაბავს", "შენი შინაგანი სამყარო აუჩქარებელ, მყუდრო ტემპს მოითხოვს"],
            ["შენი ემოციური რიტმი აუჩქარებელია; შენ გჭირდება დრო ყველაფრის მოსანელებლად.", "გემრიელი საჭმელი და მშვიდი გარემო შენთვის საუკეთესო წამალია.", "შენს სიმშვიდეს ვერაფერი შეარყევს, თუ თავად არ მისცე ნება."],
            ["Predictable sensory comfort is your non-negotiable emotional reset button", "Sudden emotional disruptions make you dig your heels into the ground"],
            ["You need time to metabolize stress through tactile comfort and quiet.", "Your emotional composure is an unshakeable fortress once established."],
        ),
        (
            "gemini",
            ["ემოციების გადასამუშავებლად მათი სიტყვებად ქცევა და ხმამაღლა განხილვა გჭირდება", "როცა გული გტკივა, იწყებ ანალიზს და ცდილობ გრძნობა ლოგიკაში მოაქციო", "საუბარი და იუმორი შენი მთავარი ემოციური ვენტილატორია"],
            ["საკუთარ განცდებსაც კი ცნობისმოყვარე მკვლევარივით აკვირდები.", "თუ პრობლემაზე ხმამაღლა იხუმრე, ე.ი. მისი დაძლევა უკვე დაიწყე.", "შენი გონება ემოციებს ინტელექტუალურ გამოცანად აქცევს."],
            ["Verbalizing your feelings is how you untangle complex emotional knots", "You analyze emotional dilemmas with lively curiosity and dry wit"],
            ["Talking through a problem dissolves the heavy emotional weight instantly.", "Humor is your primary decompression valve when life gets complicated."],
        ),
        (
            "cancer",
            ["ემოციური ტალღები შენთან ღრმაა და წარსულის მოგონებებთან მჭიდროდ დაკავშირებული", "როცა თავს დაუცველად გრძნობ, საკუთარ უსაფრთხო ნაჭუჭში იკეტები", "შენს გულს წვრილმანი უყურადღებობაც კი ადვილად ხვდება"],
            ["შენ გჭირდება გარემო, სადაც შენს სინაზეს არავინ გამოიყენებს.", "შენს ემოციურ მეხსიერებას არაფერი ავიწყდება, განსაკუთრებით გულწრფელი ზრუნვა.", "საკუთარი თავშესაფარი შენი ძალების აღდგენის მთავარი ადგილია."],
            ["Your emotional tides run profoundly deep with an encyclopedic memory", "When hurt or overwhelmed, you retreat into a heavily fortified private shell"],
            ["You require sanctuary where your tenderness is guarded, not exploited.", "Your emotional radar picks up subtle shifts in tone long before others."],
        ),
        (
            "leo",
            ["ემოციურად გჭირდება გულწრფელი დაფასება და სითბოს აღიარება", "შენი წყენა ხშირად შელახულ სიამაყესა და უყურადღებობას უკავშირდება", "როცა გიყვარს, მთელი გულითა და გულუხვობით გამოხატავ"],
            ["ცივი უყურადღებობა შენთვის ყველაზე მტკივნეული დარტყმაა.", "შენს გულწრფელ აღიარებას ოქროს ფასი აქვს.", "შენი სითბო ისეთია, რომ მის გარშემო ყოფნა ყველას ახარებს."],
            ["Heartfelt validation and generous warmth keep your emotional engine running", "Being overlooked or dismissed wounds your pride far deeper than criticism"],
            ["When you feel seen and cherished, your emotional generosity knows no bounds.", "Cold indifference is the single thing that shuts down your warmth."],
        ),
        (
            "virgo",
            ["როცა ნერვიულობ, იწყებ გარემოს მოწესრიგებას და პრობლემების დალაგებას", "ემოციებს ხშირად პრაქტიკული საზრუნავის ნიღბის ქვეშ მალავ", "საკუთარ თავს ზედმეტად მკაცრად სჯი ნებისმიერი შეცდომისთვის"],
            ["საქმით დაკავება შენთვის ემოციური ქაოსის დაძლევის საუკეთესო გზაა.", "შენს შინაგან კრიტიკოსს ხანდახან დასვენება უნდა მისცე.", "შენი მზრუნველობა კონკრეტულ, სასარგებლო საქმეებში გამოიხატება."],
            ["You manage emotional anxiety by organizing physical chaos and fixing flaws", "Internal self-criticism often masquerades as sensible problem-solving"],
            ["Constructive action is your preferred antidote to internal turbulence.", "Give your internal editor a break; perfection is not required for peace."],
        ),
        (
            "libra",
            ["ემოციური დისკომფორტი გეწყება მაშინ, როცა გარშემო უხეში კონფლიქტია", "შენი შინაგანი მშვიდობა პირდაპირ კავშირშია ურთიერთობების ჰარმონიასთან", "საკუთარ წყენას ხშირად მალავ, ოღონდ გარემოში ბალანსი არ დაირღვეს"],
            ["გაგება და ტაქტიანი თანადგომა შენი ემოციური წონასწორობის გასაღებია.", "მშვიდობის შენარჩუნება კარგია, ოღონდ საკუთარი ინტერესების ფასად არა.", "ჰარმონია შენი სულის ბუნებრივი მოთხოვნილებაა."],
            ["Harsh discord and raw confrontation drain your emotional reserves instantly", "You often swallow minor hurts just to preserve social harmony in the room"],
            ["Tactful understanding and aesthetic peace are necessary for your equilibrium.", "Keeping the peace is fine, but do not sacrifice your own needs to do it."],
        ),
        (
            "scorpio",
            ["შენი ემოციები უკიდურესად ინტენსიურია, თუმცა გარეგნულად სრულ კონტროლს ინარჩუნებ", "მოწყვლადობის ჩვენება შენთვის ურთულესი და სახიფათო ნაბიჯია", "შენს შინაგან განცდებს მხოლოდ რამდენიმე რჩეულს უზიარებ"],
            ["შენს შინაგან ქარიშხალს მხოლოდ ის ხედავს, ვინც აბსოლუტური ნდობა მოიპოვა.", "ტკივილი შენში ნადგურდება და უდიდეს შინაგან ძალად გარდაიქმნება.", "შენი ლოიალობა აბსოლუტურია, სანამ საზღვრებს არ დაგირღვევენ."],
            ["Your emotional depth is fierce, all-or-nothing, and heavily guarded", "Showing vulnerability feels like handing someone a loaded weapon"],
            ["Only the tested few are ever granted access to your inner sanctuary.", "You possess an unmatched capacity to incinerate grief and emerge reborn."],
        ),
        (
            "sagittarius",
            ["ემოციურ დაძაბულობას ოპტიმიზმითა და იუმორით უმკლავდები", "როცა სიტუაცია მძიმდება, შენი ინსტინქტია სივრცის გათავისუფლება და გაქცევა", "მძიმე ემოციებში ჩაძირვა შენს თავისუფალ ბუნებას ეწინააღმდეგება"],
            ["მძიმე საუბრებს ფილოსოფიური ხედვით მომენტალურად განმუხტავ.", "მოძრაობა და ახალი შთაბეჭდილებები შენი საუკეთესო ანტიდეპრესანტია.", "სიცილი შენი მთავარი ფარია ამ ცხოვრების სირთულეების წინაშე."],
            ["You process emotional heaviness by zooming out to a philosophical horizon", "Feeling emotionally trapped makes you want to pack a bag and disappear"],
            ["Humor and expansive freedom are your primary healing mechanisms.", "You reframe heartaches as colorful chapters in a much larger journey."],
        ),
        (
            "capricorn",
            ["ემოციების ჩვენებას სისუსტედ მიიჩნევ და ცდილობ ყველაფერი შიგნით შეიკავო", "შენს დარდს იშვიათად უზიარებ სხვებს, თავად პოულობ გამოსავალს", "შენი ემოციური საიმედოობა წლობით ნაშენებ ციხესიმაგრეს ჰგავს"],
            ["დრო და კონკრეტული სტაბილურობა შენი ემოციური უსაფრთხოების მთავარი გარანტია.", "შენ არ გჭირდება სიბრალული; შენ გჭირდება შედეგი და საიმედო პარტნიორობა.", "შენი თავშეკავება უდიდესი შინაგანი დისციპლინის შედეგია."],
            ["You contain emotional vulnerability behind a stoic, disciplined exterior", "Sharing personal pain feels awkward; you prefer resolving it privately"],
            ["Time, demonstrated competence, and concrete stability earn your trust.", "Your emotional loyalty runs deep beneath a reserved, unflinching surface."],
        ),
        (
            "aquarius",
            ["ემოციებს ხშირად გონებრივი დისტანციიდან აკვირდები, თითქოს ექსპერიმენტი იყოს", "როცა გრძნობები ზედმეტად ინტენსიური ხდება, განმარტოება და ჰაერი გჭირდება", "შენს ემოციურ სამყაროში საკუთარი ლოგიკა მოქმედებს, სხვებისთვის უცნაური"],
            ["თავისუფლება და პირადი სივრცე შენი ემოციური ჰიგიენის საფუძველია.", "შენი ობიექტურობა სხვებისთვის ცივი ჩანს, მაგრამ სინამდვილეში ეს შენი ხედვაა.", "შენ გჭირდება ადამიანი, რომელიც შენს ინდივიდუალიზმს პატივს სცემს."],
            ["You observe intense emotions through an objective, intellectual telescope", "Smothering drama triggers an immediate urge for breathing room and distance"],
            ["Space is your emotional oxygen; you return when the air is clear.", "Your cool detachment is not heartlessness; it is how you keep your clarity."],
        ),
        (
            "pisces",
            ["სხვების ემოციებს ისე ისრუტავ, თითქოს საკუთარი იყოს", "შენი გული ღიაა სამყაროს ყველა ნიუანსისთვის, რაც ხანდახან გადაღლას იწვევს", "შენ გჭირდება მშვიდი თავშესაფარი, რათა სხვისი დარდი შენსაში არ აგერიოს"],
            ["მუსიკა და შემოქმედება შენი ემოციების განწმენდის საუკეთესო საშუალებაა.", "შენი ემპათია უდიდესი ნიჭია, თუ საკუთარ საზღვრებს დაიცავ.", "განმარტოება შენთვის ენერგიის აღდგენის ერთადერთი საშუალებაა."],
            ["You absorb the ambient emotional atmosphere like an intuitive sponge", "The boundary between your feelings and other people's distress is thin"],
            ["Creative seclusion is essential to cleanse your porous emotional radar.", "Your compassionate gentleness has the rare power to soothe raw wounds."],
        ),
    ]

    for sign, ka_p, ka_t, en_p, en_t in moon_data:
        contracts.append(
            ContractSeedData(
                interpretation_id=f"self.emotional.moon_{sign}.v1",
                context="self",
                ka_witty_premises=ka_p[:2],
                ka_witty_twists=ka_t[:2],
                ka_playful_premises=ka_p[1:],
                ka_playful_twists=ka_t[1:],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1]],
                ka_savage_twists=[ka_t[1]],
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

    # =============================================================
    # 3. ASCENDANT PERSONA CONTRACTS (12)
    # =============================================================
    rising_data = [
        (
            "aries",
            ["შენი შემოსვლა ოთახში ენერგიული და პირდაპირია", "სოციალურ ფორმალობებსა და ზედმეტ შესავლებს მომენტალურად ჭრი", "შენი მტკიცე ნაბიჯი მაშინვე ყურადღებას იპყრობს"],
            ["შენი თავდაჯერებული სიარული და მზერა ყურადღებას უნებურად იპყრობს.", "ადამიანები შენგან დაუყოვნებლივ მოქმედებას და ინიციატივას ელიან.", "პირდაპირი მზერა შენი სავიზიტო ბარათია."],
            ["Your physical stride into any room is bold, energetic, and immediate", "You cut past polite social preamble without wasting a second"],
            ["People look to you for immediate momentum the second you walk in.", "Your direct eye contact commands respect before you even speak."],
        ),
        (
            "taurus",
            ["შენი პირველი შთაბეჭდილება საოცარი სიმშვიდე და თავდაჯერებული სიმყარეა", "შენ არ ჩქარობ საუბრის დაწყებას, აკვირდები გარემოს მშვიდი მზერით", "შენი პოზა მყარია და სიმშვიდეს ასხივებს"],
            ["შენი ვიზუალური ესთეტიკა და თავშეკავებული მანერები პატივისცემას ბადებს.", "შენს გვერდით ყოფნა ადამიანებს აუხსნელ უსაფრთხოებას ანიჭებს.", "შენი აუჩქარებელი სიარული თავდაჯერებულობაზე მეტყველებს."],
            ["Your initial impression is one of grounded composure and unhurried stability", "You take in the surroundings with a calm, attentive, steady gaze"],
            ["Your physical presence slows down the nervous energy of the entire room.", "You project quiet authority through calm posture and deliberate movement."],
        ),
        (
            "gemini",
            ["შენი სახის გამომეტყველება ყოველთვის ცოცხალი, ცნობისმოყვარე და მოძრავია", "საუბარს ისე მარტივად იწყებ, თითქოს ყველას წლებია იცნობდე", "შენი მზერა მუდმივად ახალ დეტალებს ეძებს"],
            ["შენი მსუბუქი იუმორი პირველივე წამიდან ხსნის უხერხულობას.", "შენთან კომუნიკაცია ყოველთვის დინამიური და ხალისიანია.", "შენი ღიმილი ნებისმიერ ბარიერს წამებში ანგრევს."],
            ["Your expressive face and alert eyes communicate instant, lively curiosity", "You strike up engaging conversations with strangers as if you were old friends"],
            ["Playful banter dissolves social awkwardness the moment you open your mouth.", "Your animated gestures keep everyone engaged in your orbit."],
        ),
        (
            "cancer",
            ["შენი პირველი გამოხედვა რბილი, დამცავი და ყურადღებიანია", "ადამიანები შენში ინტუიციურად გრძნობენ სითბოს და მზრუნველობას", "შენი თავაზიანი ღიმილი სითბოთი სავსეა"],
            ["შენ არ ჩქარობ გახსნას, ჯერ ამოწმებ რამდენად უსაფრთხოა გარემო.", "შენი თავაზიანი დისტანცია სინამდვილეში შინაგანი სიფრთხილეა.", "შენთან სიახლოვეს ყველა უსაფრთხოდ გრძნობს თავს."],
            ["Your outward presentation carries a gentle, protective, approachable aura", "People instinctively sense emotional warmth beneath your polite reserve"],
            ["You observe the room carefully before lowering your guarded buffer.", "Your soft gaze provides instant, reassuring comfort to stressed people."],
        ),
        (
            "leo",
            ["შენი შემოსვლა ბუნებრივად იპყრობს დამსწრეთა მზერას", "შენი ღიმილი, პოზა და მანერები მეფურ სითბოს ასხივებს", "შენი გამორჩეული გარეგნობა შეუმჩნეველი ვერასდროს დარჩება"],
            ["შენ არ გჭირდება ხმამაღლა ლაპარაკი, რომ შენი ყოფნა იგრძნონ.", "შენი თავდაჯერებულობა ოთახში სინათლესავით შემოდის.", "შენი მზერა გულუხვობითა და თავმოყვარეობით სავსეა."],
            ["Your entrance naturally draws the room's gaze like light through a lens", "You radiate an open, charismatic warmth that commands effortless attention"],
            ["You don't need theatrical shouting; your posture does all the talking.", "Confidence sits upon your shoulders with effortless, natural poise."],
        ),
        (
            "virgo",
            ["შენი გარეგნობა და ქცევა ყოველთვის დახვეწილი, აკურატული და მოწესრიგებულია", "შენი დაკვირვებული მზერა უმცირეს შეუსაბამობასაც კი მაშინვე ამჩნევს", "შენი თავდაჭერილობა მაღალ პროფესიონალიზმზე მიუთითებს"],
            ["შენ საუბრობ მშვიდად, კონკრეტულად და ზედმეტი პათეტიკის გარეშე.", "შენი თავდაჭერილობა მაღალი კომპეტენციის შთაბეჭდილებას ტოვებს.", "შენი მოკრძალება სინამდვილეში შენი სიძლიერეა."],
            ["Your demeanor is crisp, understated, observant, and immaculately neat", "Your sharp eyes take in functional details that slip past everyone else"],
            ["You project an air of quiet competence that earns instant professional respect.", "Understatement is your aesthetic signature, and it speaks volumes."],
        ),
        (
            "libra",
            ["შენი მომხიბვლელი ღიმილი და გრაციოზული მანერები მომენტალურად განაიარაღებს ყველას", "სოციალურ ეტიკეტს ისეთი ბუნებრიობით ფლობ, თითქოს მასთან ერთად დაიბადე", "შენი გემოვნება დეტალებში პირველივე წამიდან იკითხება"],
            ["შენი ესთეტიკური გემოვნება პირველივე მზერით იკითხება.", "შენთან საუბარი ყველასთვის სასიამოვნო და კომფორტულია.", "შენი დიპლომატია ყველაზე ხისტ ადამიანსაც კი არბილებს."],
            ["Disarming social poise and graceful charm put everyone instantly at ease", "You navigate social etiquette with the natural grace of a seasoned diplomat"],
            ["Your aesthetic presentation is balanced, pleasing, and quietly magnetic.", "You possess the rare gift of making every conversational partner feel valued."],
        ),
        (
            "scorpio",
            ["შენი მზერა იმდენად გამჭოლია, რომ თითქოს ადამიანის სულში იყურები", "შენს გარშემო ყოველთვის იგრძნობა იდუმალი, მიმზიდველი და მკაცრი აურა", "შენი სიჩუმე ხშირად უფრო ხმამაღალია, ვიდრე სხვების სიტყვები"],
            ["შენ არ ხარჯავ სიტყვებს ცარიელ მისალმებებზე.", "შენი სიჩუმე უფრო მეტს ამბობს, ვიდრე სხვების მთელი გამოსვლები.", "შენს წინაშე თამაშის დაწყებას ყველა ერიდება."],
            ["A penetrating gaze and formidable quiet intensity announce your arrival", "You project a compelling, mysterious presence that discourages shallow banter"],
            ["People hesitate to bluff around you; your eyes see through social games.", "Your silence commands more respect than the loud speeches of others."],
        ),
        (
            "sagittarius",
            ["შენი ღია, მხიარული და უშუალო მანერა ყველას გულს იგებს", "შენ ოთახში შემოგაქვს თავისუფლებისა და თავგადასავლის სუნთქვა", "შენი ხმამაღალი სიცილი და იუმორი მომენტალურად ხსნის დაძაბულობას"],
            ["შენი ხმამაღალი სიცილი და გულწრფელობა წამებში ხსნის ბარიერებს.", "შენთან ერთად ყოფნა ყოველთვის პოზიტიურ ენერგიასთან ასოცირდება.", "შენი უშუალობა ადამიანებს თავისუფლების განცდას ანიჭებს."],
            ["A breezy, candid entrance and expansive grin instantly dissolve pretenses", "You bring the fresh air of an open road into stuffy conference rooms"],
            ["Your unpretentious laughter makes newcomers feel like welcome companions.", "You project a buoyant, infectious optimism that lifts the entire room."],
        ),
        (
            "capricorn",
            ["შენი სერიოზული და საქმიანი გამომეტყველება ავტორიტეტს ბუნებრივად ბადებს", "შენ ტოვებ ადამიანის შთაბეჭდილებას, რომელსაც ყველაფერი კონტროლქვეშ აქვს", "შენი თავშეკავებული მანერები პატივისცემას შთააგონებს"],
            ["შენი თავშეკავება და დისციპლინა პირველივე წამიდან იგრძნობა.", "შენს ნდობას დრო და დამსახურება სჭირდება, რაც სხვებს პატივისცემას შთააგონებს.", "შენი სიტყვა ყოველთვის მყარია და წონა აქვს."],
            ["Measured composure and authoritative gravity define your first impression", "You project the formidable competence of someone who runs the show"],
            ["You don't need flashy demonstrations; your steady reserve commands respect.", "People instinctively step aside and let you handle serious business."],
        ),
        (
            "aquarius",
            ["შენი გარეგნობა, სტილი ან საუბრის მანერა ყოველთვის გამორჩეული და ორიგინალურია", "შენ ტოვებ თავისუფალი მოაზროვნის შთაბეჭდილებას, რომელიც ჩარჩოებს არ ემორჩილება", "შენი მეგობრული, მაგრამ დამოუკიდებელი მზერა ინტერესს აღვიძებს"],
            ["შენი მეგობრული, მაგრამ ოდნავ დისტანციური დამოკიდებულება ინტერესს აღვიძებს.", "შენ არავის ჰგავხარ და ამას არც მალავ.", "შენი სტილი ყოველთვის უსწრებს დროს."],
            ["An unconventional, distinctly original vibe sets you apart in any crowd", "You project friendly, observant detachment with an unapologetic personal style"],
            ["Nobody mistakes you for a copy; your individuality is clear from thirty paces.", "You treat social conformity as an optional, mildly amusing spectator sport."],
        ),
        (
            "pisces",
            ["შენი რბილი, თითქოს მეოცნებე მზერა უცნაურ სიმშვიდეს ასხივებს", "შენ ადვილად ერგები ნებისმიერ გარემოს, როგორც წყალი ჭურჭელს", "შენი ნაზი ხმა და მანერები ადამიანებს ამშვიდებს"],
            ["შენი მოძრაობები და ხმა დამამშვიდებელ ეფექტს ახდენს გარშემომყოფებზე.", "შენში იგრძნობა იდუმალი სიღრმე, რომლის ამოხსნაც ყველას უნდა.", "შენი აურა სავსეა თანაგრძნობითა და სინაზით."],
            ["A dreamy, gentle fluidity and receptive presence put everyone at ease", "You adapt to the room's energy with chameleon-like, empathetic grace"],
            ["People feel strangely comforted in your presence without understanding why.", "Your subtle, poetic charm creates a soothing buffer against the world."],
        ),
    ]

    for sign, ka_p, ka_t, en_p, en_t in rising_data:
        contracts.append(
            ContractSeedData(
                interpretation_id=f"self.persona.rising_{sign}.v1",
                context="self",
                ka_witty_premises=ka_p[:2],
                ka_witty_twists=ka_t[:2],
                ka_playful_premises=ka_p[1:],
                ka_playful_twists=ka_t[1:],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1]],
                ka_savage_twists=[ka_t[1]],
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

    # =============================================================
    # 4. ELEMENT DOMINANCE CONTRACTS (4)
    # =============================================================
    element_data = [
        (
            "fire",
            ["შენს ხასიათში ცეცხლოვანი ენერგია და დაუყოვნებელი ინიციატივა დომინირებს", "როცა რამე აგიტაცებს, შენი ენთუზიაზმი გარშემო ყველას ედება", "შენი მოქმედება ყოველთვის სწრაფი, თამამი და გადამწყვეტია"],
            ["პასიურობა და ლოდინი შენთვის ენერგიის კარგვაა; შენ მოქმედებისთვის ხარ შექმნილი.", "შენი შემართება ყველაზე რთულ დაბრკოლებასაც კი ადვილად გადალახავს.", "შენ ანათებ იქ, სადაც სხვები ჩრდილში დგანან."],
            ["A high kinetic drive and spontaneous initiative define your core operating system", "When inspiration strikes, your enthusiasm sparks the entire environment"],
            ["Waiting around drains your battery; you are engineered for active execution.", "Your bold drive turns abstract intentions into reality at record speed."],
        ),
        (
            "earth",
            ["შენს ბუნებაში პრაქტიკული რეალიზმი და მყარი საყრდენის შექმნის სურვილი ლიდერობს", "შენ აფასებ იმას, რასაც რეალური ფორმა, შედეგი და გრძელვადიანი ფასი აქვს", "შენი მიდგომა ცხოვრებისადმი საფუძვლიანი და საიმედოა"],
            ["შენი მოთმინება და დისციპლინა ნებისმიერ ქაოსს სტაბილურ სტრუქტურად აქცევს.", "შენ ხარ ის მყარი საფუძველი, რომელზეც სხვები თავისუფლად ეყრდნობიან.", "შენ აშენებ იმას, რაც დროსა და სირთულეებს უძლებს."],
            ["Pragmatic realism and tactile grounding form the bedrock of your character", "You measure worth by enduring tangible outcomes, not fleeting novelty"],
            ["Your disciplined patience transforms messy disorder into reliable structures.", "You are the solid foundation that others instinctively rely upon."],
        ),
        (
            "air",
            ["შენს სამყაროში იდეები, ცნობისმოყვარეობა და კომუნიკაცია მთავარი მამოძრავებელია", "შენ გჭირდება ინტელექტუალური ჟანგბადი, საინტერესო დიალოგები და ახალი ხედვები", "შენი აზროვნება თავისუფალია და ჩარჩოებს არ ცნობს"],
            ["საკითხებს ყოველთვის ობიექტურად და მრავალმხრივად უყურებ.", "შენი გონებრივი სისხარტე ცხოვრებას საინტერესო მოგზაურობად აქცევს.", "შენ აკავშირებ იდეებსა და ადამიანებს ერთ მთლიანობად."],
            ["Conceptual agility, lively communication, and social connectivity power your engine", "You require mental stimulation, fresh frameworks, and intellectual dialogue"],
            ["You connect disparate dots with effortless intellectual playfulness.", "Stagnant, unexamined ideas are the only things that truly bore you."],
        ),
        (
            "water",
            ["შენს არსებაში ღრმა ემპათია, ინტუიცია და ემოციური დაკვირვება სუფევს", "შენ გრძნობ სამყაროს უხილავ დინებებს და ადამიანების დაფარულ ემოციებს", "შენი შინაგანი სამყარო ოკეანესავით ღრმა და მრავალფეროვანია"],
            ["შენი შინაგანი სიბრძნე ლოგიკაზე უფრო ღრმა და მრავლისმომცველია.", "შენი მგრძნობელობა შენი ყველაზე დიდი ძალა და მეგზურია.", "შენი თანაგრძნობა გარშემო ყველას სიმშვიდეს ანიჭებს."],
            ["Intuitive resonance, emotional depth, and acute subtext sensing guide your life", "You navigate the world by feeling emotional currents rather than dry logic"],
            ["Your sensitivity is your greatest diagnostic strength, not a weakness.", "Your empathy dissolves interpersonal walls that reason could never penetrate."],
        ),
    ]

    for elem, ka_p, ka_t, en_p, en_t in element_data:
        contracts.append(
            ContractSeedData(
                interpretation_id=f"self.element.{elem}_dominant.v1",
                context="self",
                ka_witty_premises=ka_p[:2],
                ka_witty_twists=ka_t[:2],
                ka_playful_premises=ka_p[1:],
                ka_playful_twists=ka_t[1:],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1]],
                ka_savage_twists=[ka_t[1]],
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

    # =============================================================
    # 5. MODALITY DOMINANCE CONTRACTS (3)
    # =============================================================
    modality_data = [
        (
            "cardinal",
            ["შენ ხარ ბუნებრივი ინიციატორი, რომელიც მოძრაობას იწყებს", "ლოდინი და სტაგნაცია შენთვის გაუსაძლისია; შენ პირველი ნაბიჯის გადადგმა გიყვარს", "შენი ენერგია ახალი პროექტების დასაწყებად საუკეთესოა"],
            ["სადაც სხვები ყოყმანობენ, შენ პროცესს იწყებ და სხვებს გზას უჩვენებ.", "შენი ლიდერული იმპულსი ბუნებრივია და შინაგან ცეცხლს ემყარება.", "შენ ხარ ის, ვინც პირველ ნაპერწკალს ანთებს."],
            ["You are a natural instigator who launches movements and breaks deadlocks", "Standing still feels suffocating; you thrive by initiating bold new chapters"],
            ["Where others hesitate in debate, you take the first decisive step.", "Pioneering momentum is your natural habitat; you build from a blank slate."],
        ),
        (
            "fixed",
            ["შენ ხარ საქმის ბოლომდე მიმყვანი, რომლის შეუპოვრობას საზღვარი არ აქვს", "ერთხელ არჩეულ გზას იშვიათად უხვევ; შენი ერთგულება და გამძლეობა ურყევია", "შენი ერთგულება არჩეული მიზნისადმი ურყევია"],
            ["შენი ენერგია ხანგრძლივ მარათონებზეა გათვლილი და არა მოკლე სპრინტზე.", "შენი სტაბილურობა ნებისმიერ გუნდს და ურთიერთობას ურყევ საყრდენს უქმნის.", "შენ არ ჩერდები მანამ, სანამ მიზანი არ მიიღწევა."],
            ["Unwavering tenacity and loyal endurance define your operational style", "Once you commit to a course, distractions and noise bounce right off you"],
            ["You are built for the long marathon, not short, flashy sprints.", "Your steadfast consistency anchors projects and alliances through any weather."],
        ),
        (
            "mutable",
            ["შენ ხარ ცვლილებების ოსტატი, რომელიც ნებისმიერ ახალ რეალობას წამებში ერგება", "მოქნილობა და მრავალმხრივი ხედვა შენი უდიდესი უპირატესობაა", "შენ შეგიძლია ნებისმიერი კრიზისიდან ახალი შესაძლებლობა გამოაძერწო"],
            ["შენ არ ებრძვი ტალღებს; შენ მათზე ოსტატურად სრიალებ და ახალ შესაძლებლობებს პოულობ.", "შენი ადაპტაციის უნარი ნებისმიერ კრიზისს შემოქმედებით გადაწყვეტად აქცევს.", "შენი მოქნილობა გაძლევს საშუალებას ყოველთვის მშრალი გამოხვიდე წყლიდან."],
            ["Fluid versatility and rapid adaptation make you a master of shifting terrain", "You pivot effortlessly when unexpected obstacles alter the original plan"],
            ["You do not fight the current; you surf it toward creative breakthroughs.", "Mental agility allows you to thrive inside changing conditions that baffle others."],
        ),
    ]

    for mod, ka_p, ka_t, en_p, en_t in modality_data:
        contracts.append(
            ContractSeedData(
                interpretation_id=f"self.modality.{mod}_dominant.v1",
                context="self",
                ka_witty_premises=ka_p[:2],
                ka_witty_twists=ka_t[:2],
                ka_playful_premises=ka_p[1:],
                ka_playful_twists=ka_t[1:],
                ka_soft_premises=[ka_p[0], ka_p[-1]],
                ka_soft_twists=[ka_t[0], ka_t[-1]],
                ka_bold_premises=[ka_p[0]],
                ka_bold_twists=[ka_t[0]],
                ka_savage_premises=[ka_p[1]],
                ka_savage_twists=[ka_t[1]],
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
