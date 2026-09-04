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
                "როცა რაღაცის გაკეთება გინდა, ლოდინს ფიზიკურად ვერ იტან და მაშინვე წინ ხტები",
                "მოქმედება შენთვის ფიქრზე სწრაფად იწყება — ჯერ კარს ანგრევ და მერე კითხულობ, დაკეტილი იყო თუ არა",
                "შენს იმპულსურ პირდაპირობას „გულწრფელობას“ ეძახი და დიპლომატიას სისუსტედ თვლი",
                "სანამ სხვები გეგმავენ, შენ უკვე საქმეში ხარ ჩართული",
            ],
            [
                "სანამ სხვები რისკებს ითვლიან, შენ უკვე კედელს ეჯახები და მერე ამას „გამოცდილებას“ ეძახი.",
                "მთავარია, გზაში ვინმემ შენელება არ შემოგთავაზოს — საკუთარი შეცდომის აღიარებას ისევ წინ გადაჩეხვა გირჩევნია.",
                "გგონია, რომ სამყარო ზედმეტად ნელია, მაგრამ სინამდვილეში უბრალოდ საკუთარი მოუთმენლობის მძევალი ხარ.",
                "შენ არ ელი ნებართვას, უბრალოდ იწყებ და მერე უკვირს, სხვები რატომ დარჩნენ გაოგნებულები.",
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
                "გადაწყვეტილებებს იმდენად ნელა იღებ, რომ გარშემომყოფებს ლოდინში ნერვები წყდებათ",
                "კომფორტის ზონიდან გამოსვლას მხოლოდ მაშინ თანხმდები, თუ მეორე მხარეს უფრო რბილი დივანი გელოდება",
                "შენს სიტყვას ყოველთვის კონკრეტული წონა აქვს და ცვლილებებს პრინციპულად ეწინააღმდეგები",
            ],
            [
                "შენს გაუგონარ სიჯიუტეს „პრინციპულობას“ ეძახი — სანამ ყველა არ დანებდება, ადგილიდან არ დაიძვრები.",
                "რაც უფრო გაწვებიან და გაჩქარებენ, მით უფრო ღრმად ასობ ფესვებს მიწაში.",
                "სტაბილურობა შენთვის ფეტიშია; ერთი ჭიქის გადაადგილებამაც კი შეიძლება შენი შინაგანი სიმშვიდე დაანგრიოს.",
                "შენი მოთმინება უსაზღვრო ჩანს, მაგრამ თუ ვინმემ შენს კომფორტს გადააბიჯა, მიწისძვრა გარდაუვალია.",
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
                "ერთდროულად ხუთ პარალელურ თემაზე ლაპარაკობ და გიკვირს, სხვები რატომ იღლებიან",
                "მოსაწყენ საუბრებს ისეთი ელვისებური ირონიით ჭრი, რომ მოსაუბრე ვერც ხვდება, როგორ გააბითურე",
                "ყველაფერზე ცოტ-ცოტა იცი და ისეთი თავდაჯერებით ყვები, თითქოს ენციკლოპედია შენი დაწერილი იყოს",
                "ინფორმაციას ისეთი სისწრაფით ამუშავებ, სხვები ჩამორჩენას ვერ ასწრებენ",
            ],
            [
                "სანამ სხვები აზრს აყალიბებენ, შენ უკვე პასუხი გაქვს — და თან იმ ტონით, თითქოს მათი მოსმენა უბრალოდ ტექნიკური შეფერხება იყო.",
                "ირონია შენი სუპერძალაა, თუმცა ხშირად უბრალოდ თავდაცვის მექანიზმი, როცა რეალურ გრძნობებს გაურბიხარ.",
                "ერთ თემაზე ან ერთ ადამიანზე დიდხანს გაჩერება შენთვის პატიმრობის ტოლფასია; სიღრმეს მრავალფეროვნებაში ცვლი.",
                "შენი ყურადღების დიაპაზონი პეპლის ფრენას ჰგავს — სანამ საქმეს დაიწყებ, უკვე ახალმა იდეამ გაგიტაცა.",
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
                "ოთახში შემოსვლისთანავე გრძნობ უთქმელ განწყობებს და ყველაფერს პირად შეურაცხყოფად იღებ",
                "ახლობლებს კისერზე აზიხარ „მზრუნველის“ მანტიით და საკუთარ ახირებებს უცდომელ ინტუიციას ეძახი",
                "შენი წყენის მეხსიერება იმდენად უსაზღვროა, რომ წლების წინანდელ გადაკრულ სიტყვასაც არავის პატიობ",
                "როცა თავს დაუცველად გრძნობ, საკუთარ ნაჭუჭში ისე იმალები, თითქოს გარშემო ყველა შენს გასანადგურებლად შეთქმულებას აწყობდეს",
            ],
            [
                "ლოგიკასაც ფეხქვეშ გათელავ, ოღონდ ბოლოს მაინც თქვა: „ხომ გითხარით, წინასწარ ვიცოდი-მეთქი.“",
                "ჩუმად იბუტები და მერე ელოდები, როდის გამოიცნობს ვინმე, რატომ დაგემართა ტრაგედია.",
                "შენი „ზრუნვა“ ხშირად იმდენად მახრჩობელაა, რომ გარშემომყოფებს ჟანგბადის ძებნა უწევთ.",
                "შენი წყენა ჩუმია, მაგრამ ისეთი დამანგრეველი, რომ დამნაშავეს საკუთარი დაბადება სანანებელი გაუხდება.",
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
                "შენი შემოსვლა ოთახში შეუმჩნეველი ვერასდროს დარჩება — თუ ვინმე არ შემოგხედა, თვითონ გააკეთებ რამეს ხმამაღლა",
                "სცენა ყოველთვის შენია, მაშინაც კი, როცა უბრალოდ სხვის ისტორიას ისმენ და თემას საკუთარ თავზე გადმოიტან",
                "ვითომ უანგაროდ გასცემ, მაგრამ ვაი იმას, ვინც მადლობა ზედმეტად ჩუმად გითხრა",
                "სიამაყე შენი ხერხემალია, რომელსაც საკუთარი შეცდომის აღიარებას ცეცხლში შესვლა ურჩევნია",
            ],
            [
                "ეს გულუხვობა კი არა, პატარა პირადი თეატრია — მთავარია, მაყურებელმა ტაში არ დაიშუროს.",
                "მთავარია, შენი დამსახურება აღიარონ — უყურადღებობას ისე განიცდი, თითქოს გვირგვინი მოგპარეს.",
                "კომპლიმენტებზე ისე ნაბდდები, რომ აშკარა პირფერობაც კი ობიექტურ სიმართლედ გეჩვენება.",
                "შენი გული დიდია, მაგრამ შენი ეგო იმდენად გიგანტური, რომ ოთახში სხვებისთვის ადგილი აღარ რჩება.",
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
                "იმ დეტალს პოულობ, რომელსაც ნორმალური ადამიანი საერთოდ არ ეძებდა",
                "სხვების ქაოსის მოწესრიგებას ისე იწყებ, თითქოს ვინმემ დახმარება გთხოვა",
                "შენი სტანდარტები იმდენად ავადმყოფურად მაღალია, რომ საკუთარ თავსაც იშვიათად ინდობ",
                "სანამ სხვები იდეებზე ლაპარაკობენ, შენ უკვე ხარვეზების სრული სია გაქვს დაბეჭდილი",
            ],
            [
                "მერე სანამ ის ერთი წერტილი თავის ადგილზე არ დაჯდება, ყველას ნერვებს უშლი და ამას „სიმშვიდის შენარჩუნებას“ ეძახი.",
                "რჩევებს ისეთი ტონით არიგებ, თითქოს სამყაროს უხარვეზო მუშაობა პირადად შენს მხრებზე იდგეს.",
                "შენს შინაგან კრიტიკოსს იმდენად მკაცრი რეჟიმი აქვს, რომ საკუთარ წარმატებასაც დეფექტების ჩამონათვალით ხვდები.",
                "შენ არ გჭირდება აპლოდისმენტები, მთავარია ყველაფერი შენი პირადი ინსტრუქციის მიხედვით დალაგდეს.",
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
                "კონფლიქტს ისე გაურბიხარ, რომ მზად ხარ ყველას დაეთანხმო, ოღონდ ხმა არავინ აიმაღლოს",
                "ღიმილითა და დიპლომატიით ისე მანევრირებ, რომ საკუთარი რეალური პოზიცია სადღაც გზაში იკარგება",
                "გადაწყვეტილების მიღება გიჭირს იმიტომ, რომ ყველა ალტერნატივის ხიბლს ხედავ და არჩევანის გეშინია",
                "სილამაზე, ბალანსი და ესთეტიკა შენთვის ცხოვრების მთავარი საზომია",
            ],
            [
                "მშვიდობის შენარჩუნებას ეძახი იმას, რომ წყენას ღიმილის ქვეშ მალავ და მერე ჩუმად ელოდები, როდის მიხვდებიან.",
                "მენიუს არჩევასაც კი საერთაშორისო მოლაპარაკების მასშტაბი აქვს — შედეგად კი ყველას ნერვები ეშლება.",
                "სხვების მოსაწონად იმდენს თმობ, რომ ბოლოს საკუთარი თავიც აღარ გახსოვს.",
                "შენი მომხიბვლელობა შესანიშნავი ნიღაბია, რომლის უკანაც მუდმივი ყოყმანი და გაურკვევლობა იმალება.",
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
                "ყველა კუთხეში ტყუილს ეძებ და ამას „ფაქიზ ინტუიციას“ ეძახი",
                "ადამიანებს ისეთი მზერით აკვირდები, თითქოს მათი საიდუმლო ფაილები უკვე მაგიდაზე გედოს",
                "ზედაპირულობასა და ფასადურ საუბრებს ვერ იტან, რადგან დრამის გარეშე ცხოვრება გეუცნაურება",
                "შენი ნდობის მოპოვება გამოცდაა, სადაც გამსვლელი ქულა ბუნებაში არ არსებობს",
            ],
            [
                "ზედაპირულ საუბარს კი იმიტომ ვერ იტან, რომ იქ შენი ღრმა და ტრაგიკული ბუნების დემონსტრირება ცოტა რთულია.",
                "საკუთარ თავზე არაფერს ამბობ, სხვისგან კი სრულ სულიერ გაშიშვლებას ითხოვ და ამას „ნდობის შემოწმებას“ არქმევ.",
                "წყენას ისე სათუთად ინახავ, თითქოს საკოლექციო იარაღი იყოს, რომელსაც საჭირო მომენტში შურისძიებისთვის გამოიყენებ.",
                "შენი ინტუიცია ტყუილს მართლა გრძნობს, მაგრამ ხანდახან იქაც პოულობს შეთქმულებას, სადაც საერთოდ არაფერი ხდება.",
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
                "ტაქტის დეფიციტს „გულწრფელობას“ ეძახი და მერე გიკვირს, ხალხი რატომ გაფითრდა",
                "თავისუფლება გიყვარს ზუსტად მანამ, სანამ საქმე რუტინასა და ვალდებულებებზე მიდგება",
                "შენი ოპტიმიზმი ხანდახან იმდენად ბრმაა, რომ უფსკრულში გადახტომასაც „საინტერესო თავგადასავალს“ არქმევ",
                "ახალი იდეები და ჰორიზონტები მუდმივად გიტაცებს, თუმცა ძველების დასრულება გავიწყდება",
            ],
            [
                "სიმართლეს პირში მიახლი ყველას, მაგრამ როგორც კი ვინმე პასუხისმგებლობას მოგთხოვს, უცებ ბილეთებს ყიდულობ სხვა ქალაქში.",
                "სხვის ცხოვრებაზე ისეთი ფილოსოფიური ექსპერტივით ლაპარაკობ, თითქოს საკუთარი პრობლემები უკვე მოგვარებული გქონდეს.",
                "ერთი იდეიდან მეორეზე ისე ხტები, რომ დაწყებული საქმეების სასაფლაო უკან მოგრჩება.",
                "შენი გულწრფელობა ხშირად იმიტომაა დაუნდობელი, რომ სხვისი ემოციების გაფრთხილება ზედმეტ ძალისხმევად გეჩვენება.",
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
                "ემოციებს ისე საგულდაგულოდ მალავ, თითქოს მათი გამოხატვა სისხლის სამართლის დანაშაული იყოს",
                "შენ იცი, რომ რეალური შედეგი მხოლოდ დისციპლინას მოაქვს და მოდუნებას სისუსტედ თვლი",
                "სხვების ენთუზიაზმს ცივი რეალიზმით ისე მომენტალურად აქრობ, თითქოს ხანძარსაწინააღმდეგო სისტემა იყო",
                "საკუთარ თავს ყველაზე მძიმე ტვირთს აჰკიდებ და მერე ჩუმად ბრაზობ, სხვები რატომ არ იტანჯებიან",
            ],
            [
                "ყველაფერს აკონტროლებ და მერე წუწუნებ, რომ შენ გარეშე არავის არაფერი შეუძლია.",
                "წარმატებას მხოლოდ მაშინ აღიარებ, თუ გზაში სული არ ამოგხდა — მარტივი გამარჯვება შენთვის არ ითვლება.",
                "ემოციებს საქმეში არ ურევ, სამაგიეროდ შენს კომპანიაში ყოფნა ხანდახან დირექტორთა საბჭოს სხდომას ემსგავსება.",
                "შენი სტანდარტები მკაცრია, მაგრამ ამ სიმკაცრით უპირველესად საკუთარ თავს აწამებ.",
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
                "საკუთარ თავს „თავისუფალ მოაზროვნედ“ ასაღებ, მაგრამ მოდი ნუ გავართულებთ: უბრალოდ ვერავინ გეტყვის, რა უნდა იფიქრო",
                "ადამიანებთან ისეთი დისტანციიდან ურთიერთობ, თითქოს კოსმოსური სადგურიდან აკვირდებოდე ექსპერიმენტს",
                "ორიგინალურობა შენი აკვიატებაა — თუ ყველა მარჯვნივ წავა, შენ მარცხნივ გადაუხვევ მხოლოდ იმიტომ, რომ მასას არ დაემსგავსო",
                "საზოგადოებრივი შაბლონები და წესები შენთვის არაფერს ნიშნავს, სამაგიეროდ საკუთარ დოგმებს წმინდად იცავ",
            ],
            [
                "სამყაროს გადარჩენის იდეებსაც იმიტომ ეჭიდები, რომ საკუთარი სიჯიუტე უფრო ღირსეულად გამოიყურებოდეს.",
                "კაცობრიობა გიყვარს აბსტრაქტულად, მაგრამ კონკრეტულ ადამიანთან ხუთ წუთზე მეტხანს საუბარი უკვე გღლის.",
                "ემოციურ საუბრებს ლოგიკური ანალიზით ისე აციებ, რომ ახლობლები უბრალოდ ხელს ჩაიქნევენ.",
                "შენი ლოგიკა დროს კი არ უსწრებს, ხშირად უბრალოდ ადამიანურ სითბოსაა მოკლებული.",
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
                "რეალობა იმდენად გაწუხებს, რომ ნახევარ დროს საკუთარ ილუზიებში ატარებ და მერე გიკვირს, გადასახადები რატომ მოვიდა",
                "სხვის ტკივილს ისე ირგებ, თითქოს შენი იყოს, ოღონდ საკუთარი პრობლემების მოგვარებას თავი აარიდო",
                "მსხვერპლის როლს ისეთი ოსტატობით თამაშობ, რომ ოსკარი უკვე სახლში უნდა გედოს",
                "შენი ინტუიცია ხშირად უბრალოდ შიშებისა და სურვილების ნაზავია, რომელსაც „კოსმიურ ნიშნებს“ არქმევ",
            ],
            [
                "როცა სიტუაცია რთულდება, უბრალოდ ქრები ნისლში და მერე ამას „ენერგიის გაწმენდას“ ეძახი.",
                "საზღვრები შენთვის არ არსებობს — ან საერთოდ არ უშვებ ადამიანს, ან პირდაპირ შენს ცხოვრებას აბარებ და მერე წუწუნებ, რომ გაგაცურეს.",
                "საკუთარ დრამაში ისე კომფორტულად გრძნობ თავს, რომ ბედნიერება ხანდახან მოსაწყენად გეჩვენება.",
                "შენი შინაგანი ოკეანე იმდენად უსაზღვროა, რომ იქ რეალური პასუხისმგებლობები უკვალოდ იძირება.",
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
            [
                "გაბრაზებას ვერ მალავ — ორ წამში იფეთქებ და მერე გიკვირს, სხვები რატომ დარჩნენ შეშინებულები",
                "თუ რამე გაწუხებს, მაშინვე უნდა თქვა; ემოციების დაგროვება შენთვის უცხოა",
                "შენს ემოციურ აფეთქებებს „გულწრფელობას“ ეძახი, თუმცა სხვებისთვის ეს უბრალოდ მოულოდნელი ტაიფუნია",
            ],
            [
                "სწრაფად იფეთქებ და ხუთ წუთში ისევ მშვიდად აგრძელებ საუბარს, თითქოს არაფერი მომხდარა.",
                "მთავარია, გრძნობები არ ჩაიკეტოს, თორემ აფეთქებისას ახლოს მყოფებსაც თან გაიყოლებ.",
                "შენი ემოციური ტემპერატურა წამებში ადუღდება და გარშემო ყველაფერს წვავს.",
            ],
            ["Your emotional reactivity is immediate and completely unfiltered", "Holding grudges feels like a waste of energy when you can clear the air now"],
            ["You flare up fast and return to calm five minutes later.", "Immediate emotional truth prevents toxic build-up in your life."],
        ),
        (
            "taurus",
            [
                "სტრესს მაცივრის გაღებით ან ონლაინ-შოპინგით ებრძვი და ამას „შინაგანი ბალანსის აღდგენას“ ეძახი",
                "ნერვიულობის დროს უეცარი ცვლილებები ყველაზე მეტად გძაბავს და ჯიუტად ადგილზე შეშდები",
                "შენი შინაგანი სამყარო აუჩქარებელ, მყუდრო ტემპსა და სრულ უძრაობას მოითხოვს",
            ],
            [
                "როცა გული გტკივა, ისე ჯიუტად იკეტები, რომ შენი კომფორტის ზონიდან ტრაქტორითაც ვერავინ გამოგიყვანს.",
                "შენი ემოციური რიტმი იმდენად აუჩქარებელია, რომ განცდების მონელებას კვირებს ანდომებ.",
                "შენს სიმშვიდეს ვერაფერი შეარყევს, სანამ შენს საყვარელ სავარძელს ვინმე არ წაგართმევს.",
            ],
            ["Predictable sensory comfort is your non-negotiable emotional reset button", "Sudden emotional disruptions make you dig your heels into the ground"],
            ["You need time to metabolize stress through tactile comfort and quiet.", "Your emotional composure is an unshakeable fortress once established."],
        ),
        (
            "gemini",
            [
                "საკუთარ გრძნობებზე იმდენს ლაპარაკობ და ხუმრობ, რომ სინამდვილეში რას განიცდი, შენ თვითონაც აღარ გახსოვს",
                "ემოციური დრამის დროს იწყებ ანალიზს, თითქოს შენი პირადი ტრაგედია ვიღაც უცხოს პოდკასტის თემა იყოს",
                "საუბარი და ირონია შენი მთავარი ემოციური ვენტილატორია",
            ],
            [
                "საკუთარ განცდებსაც კი ცნობისმოყვარე მკვლევარივით აკვირდები და გრძნობებს ინტელექტუალურ გამოცანად აქცევ.",
                "თუ პრობლემაზე ხმამაღლა იხუმრე, გგონია რომ გადაჭერი, თუმცა ემოცია არსად წასულა.",
                "ერთ გრძნობაზე დიდხანს გაჩერება გღლის, ამიტომ სევდასაც კი სწრაფად იცვლი ახალი შთაბეჭდილებით.",
            ],
            ["Verbalizing your feelings is how you untangle complex emotional knots", "You analyze emotional dilemmas with lively curiosity and dry wit"],
            ["Talking through a problem dissolves the heavy emotional weight instantly.", "Humor is your primary decompression valve when life gets complicated."],
        ),
        (
            "cancer",
            [
                "უყურადღებო მზერაზეც კი შეგიძლია სამდღიანი ჩუმი ბოიკოტი გამოაცხადო და მერე ელოდო, როდის გამოიცნობენ მიზეზს",
                "როცა თავს დაუცველად გრძნობ, საკუთარ უსაფრთხო ნაჭუჭში ისე იკეტები, რომ კედლები გარედანაც ჩანს",
                "შენს გულს წვრილმანი უყურადღებობაც კი ისე ხვდება, თითქოს სამყარო დაინგრა",
            ],
            [
                "ემოციური მეხსიერება იმდენად გადატვირთული გაქვს, რომ ძველი წყენების გამო ახალ ურთიერთობებსაც წინასწარ ეჭვის თვალით უყურებ.",
                "შენს ემოციურ მეხსიერებას არაფერი ავიწყდება, განსაკუთრებით ის, რაც სხვამ შემთხვევით წამოცდა.",
                "ჩუმად იტანჯები და ამ ტანჯვით გარშემომყოფებს დანაშაულის გრძნობას უღვივებ.",
            ],
            ["Your emotional tides run profoundly deep with an encyclopedic memory", "When hurt or overwhelmed, you retreat into a heavily fortified private shell"],
            ["You require sanctuary where your tenderness is guarded, not exploited.", "Your emotional radar picks up subtle shifts in tone long before others."],
        ),
        (
            "leo",
            [
                "როცა გულს გტკენენ, შენი ტკივილი კი არ ირთვება, არამედ შელახული სიამაყე — უყურადღებობას ისე განიცდი, თითქოს ერს უღალატეს",
                "შენი წყენა ხშირად შეუმჩნევლად დარჩენილ დამსახურებას უკავშირდება",
                "როცა გიყვარს, მთელი გულითა და გრანდიოზული ჟესტებით გამოხატავ",
            ],
            [
                "სითბოს ვითომ უანგაროდ გასცემ, მაგრამ თუ საპასუხო აღფრთოვანება არ მიიღე, შიგნით ნამდვილი სამეფო დრამა იწყება.",
                "ცივი უყურადღებობა შენთვის ყველაზე მტკივნეული დარტყმაა — მტრად უფრო მარტივად მიიღებ ვინმეს, ვიდრე უინტერესო მაყურებლად.",
                "შენი სითბო დიდია, ოღონდ სანაცვლოდ მუდმივ ლოიალობასა და ტაშს ითხოვ.",
            ],
            ["Heartfelt validation and generous warmth keep your emotional engine running", "Being overlooked or dismissed wounds your pride far deeper than criticism"],
            ["When you feel seen and cherished, your emotional generosity knows no bounds.", "Cold indifference is the single thing that shuts down your warmth."],
        ),
        (
            "virgo",
            [
                "ნერვიულობის დროს იწყებ კარადების დალაგებას ან სხვების შეცდომების ჩამოთვლას და ამას „დამშვიდებას“ არქმევ",
                "ემოციებს ხშირად პრაქტიკული საზრუნავის ნიღბის ქვეშ ისე საგულდაგულოდ მალავ, რომ საკუთარ თავსაც ატყუებ",
                "საკუთარ თავს ზედმეტად მკაცრად სჯი ნებისმიერი ემოციური სისუსტისთვის",
            ],
            [
                "საკუთარ გრძნობებსაც კი ისეთი მკაცრი კრიტიკით ამოწმებ, თითქოს ემოციები საგადასახადო დეკლარაცია იყოს.",
                "შენს შინაგან კრიტიკოსს დასვენება არასდროს უწერია — სხვების დამშვიდებასაც კი ინსტრუქციების ჩამოთვლით ცდილობ.",
                "შენი მზრუნველობა სასარგებლო საქმეებში გამოიხატება, მაგრამ სითბოს ნაცვლად ხშირად შენიშვნებს არიგებ.",
            ],
            ["You manage emotional anxiety by organizing physical chaos and fixing flaws", "Internal self-criticism often masquerades as sensible problem-solving"],
            ["Constructive action is your preferred antidote to internal turbulence.", "Give your internal editor a break; perfection is not required for peace."],
        ),
        (
            "libra",
            [
                "საკუთარ წყენას ღიმილის ქვეშ მანამ მალავ, სანამ შიგნით ყველაფერი არ გადაიწვება — ოღონდ სხვებს უხერხულობა არ შეუქმნა",
                "ემოციური დისკომფორტი გეწყება მაშინვე, როგორც კი ოთახში ოდნავი დაძაბულობა ჩნდება",
                "მარტო ყოფნის პანიკური შიში გაქვს, ამიტომ ხშირად ისეთ ადამიანებს ებღაუჭები, ვის გვერდითაც შენი ადგილი არაა",
            ],
            [
                "მშვიდობის შენარჩუნება კარგია, ოღონდ საკუთარი ემოციების გაყიდვის ფასად თუ აკეთებ, ბოლოს ცარიელი რჩები.",
                "გაგება და ტაქტიანი თანადგომა გინდა, თუმცა საკუთარ რეალურ გრძნობებს იშვიათად ამბობ ხმამაღლა.",
                "კონფლიქტის შიშით ყველასთან კარგად ყოფნას ცდილობ და შედეგად საკუთარ პოზიციას კარგავ.",
            ],
            ["Harsh discord and raw confrontation drain your emotional reserves instantly", "You often swallow minor hurts just to preserve social harmony in the room"],
            ["Tactful understanding and aesthetic peace are necessary for your equilibrium.", "Keeping the peace is fine, but do not sacrifice your own needs to do it."],
        ),
        (
            "scorpio",
            [
                "მოწყვლადობის ჩვენება შენთვის სიკვდილის ტოლფასია — ამიტომ სანამ ვინმე გულს გატკენს, წინასწარ თავდასხმაზე გადადიხარ",
                "შენი ემოციები უკიდურესად ინტენსიურია, თუმცა გარეგნულად ისეთ ყინულს ინარჩუნებ, თითქოს საერთოდ არ გქონდეს გული",
                "შენს შინაგან განცდებს არავის უზიარებ, რადგან ნდობა შენთვის სახიფათო იარაღია",
            ],
            [
                "შენს შინაგან ქარიშხალს ისე მალავ ცივი მზერის უკან, რომ მოსაუბრე ვერასდროს ხვდება, რომ მის წინააღმდეგ უკვე შურისძიების გეგმა მზადდება.",
                "ტკივილს ისე ღრმად ინახავ, რომ წლების შემდეგაც შეგიძლია ზუსტად იმავე სიმძაფრით ამოხეთქო.",
                "შენი ლოიალობა აბსოლუტურია, მაგრამ თუ საზღვარი დაგირღვიეს, სამუდამო განადგურების ზონაში გადადიხარ.",
            ],
            ["Your emotional depth is fierce, all-or-nothing, and heavily guarded", "Showing vulnerability feels like handing someone a loaded weapon"],
            ["Only the tested few are ever granted access to your inner sanctuary.", "You possess an unmatched capacity to incinerate grief and emerge reborn."],
        ),
        (
            "sagittarius",
            [
                "ემოციურ სიმძიმეს იუმორით ისე მომენტალურად აფარებ თავს, რომ რეალურ განცდებთან შეხვედრას ყოველთვის ახერხებ გაექცე",
                "როგორც კი ურთიერთობაში სერიოზული ემოციური საუბარი იწყება, უცებ ჰაერი აღარ გყოფნის და გაქცევა გინდება",
                "მძიმე ემოციებში ჩაძირვა შენს თავისუფალ ბუნებას ეწინააღმდეგება და პრობლემებს ფილოსოფიური ხუმრობით შლი",
            ],
            [
                "სიცილი შენი მთავარი ფარია — სანამ იცინი, თავს იტყუებ, რომ გული არ გტკივა.",
                "მოძრაობა და ახალი შთაბეჭდილებები შენი საუკეთესო ანტიდეპრესანტია, ოღონდ საკუთარ თავს ვერსად გაექცევი.",
                "მძიმე საუბრებს ოპტიმიზმით მომენტალურად განმუხტავ, თუმცა პრობლემის არსი ხელუხლებელი რჩება.",
            ],
            ["You process emotional heaviness by zooming out to a philosophical horizon", "Feeling emotionally trapped makes you want to pack a bag and disappear"],
            ["Humor and expansive freedom are your primary healing mechanisms.", "You reframe heartaches as colorful chapters in a much larger journey."],
        ),
        (
            "capricorn",
            [
                "საკუთარ სისუსტეს ისე ებრძვი, თითქოს გრძნობების ქონა დისციპლინის ნაკლებობა და სირცხვილი იყოს",
                "დარდს საქმითა და მუშაობით იხშობ — სანამ ფეხზე დგახარ, თავს უფლებას არ აძლევ აღიარო, რომ დაიღალე",
                "შენს დარდს იშვიათად უზიარებ სხვებს, თავად პოულობ გამოსავალს და მარტოობას ეჩვევი",
            ],
            [
                "შენი თავშეკავება უდიდესი შინაგანი დისციპლინაა, მაგრამ ამ დისციპლინით ემოციებს ცოცხლად მარხავ.",
                "შენ არ გჭირდება სიბრალული, სამაგიეროდ შენი ცივი კედელი ახლობლებსაც შორს იჭერს.",
                "დრო და სტაბილურობა გჭირდება, ოღონდ სანამ ნდობას გასცემ, მეორე მხარეს უკვე იმედი გადაეწურება.",
            ],
            ["You contain emotional vulnerability behind a stoic, disciplined exterior", "Sharing personal pain feels awkward; you prefer resolving it privately"],
            ["Time, demonstrated competence, and concrete stability earn your trust.", "Your emotional loyalty runs deep beneath a reserved, unflinching surface."],
        ),
        (
            "aquarius",
            [
                "საკუთარ ემოციებსაც კი ისე უყურებ, როგორც უცნაურ ლაბორატორიულ ექსპერიმენტს — გაანალიზებ, გააციებ და თაროზე შემოდებ",
                "როცა გრძნობები ზედმეტად ინტენსიური ხდება, განმარტოება და კილომეტრიანი დისტანცია გჭირდება",
                "შენს ემოციურ სამყაროში საკუთარი ლოგიკა მოქმედებს, რომელიც სხვებისთვის ემოციურ სიცივეს ჰგავს",
            ],
            [
                "თავისუფლება და პირადი სივრცე შენი ემოციური ჰიგიენის საფუძველია, ოღონდ ამ სივრცეში ხშირად სრულიად მარტო რჩები.",
                "შენი ობიექტურობა სხვებისთვის ყინულივით ცივი ჩანს — გრძნობებს ფორმულებად შლი და მერე გიკვირს, რატომ ვერ გიგებენ.",
                "როცა ვინმე ზედმეტ სითბოს ითხოვს, უცებ ცივი დისტანციის კედელს აშენებ და მერე უკვირს, რატომ ჩამოგშორდნენ.",
            ],
            ["You observe intense emotions through an objective, intellectual telescope", "Smothering drama triggers an immediate urge for breathing room and distance"],
            ["Space is your emotional oxygen; you return when the air is clear.", "Your cool detachment is not heartlessness; it is how you keep your clarity."],
        ),
        (
            "pisces",
            [
                "სხვისი განწყობა ისე ადვილად გედება, რომ ხანდახან დეპრესიაში ხარ იმ ადამიანის გამო, ვის სახელსაც ძლივს იხსენებ",
                "რეალობიდან გაქცევა შენი საყვარელი სპორტია — როცა რამე არ მოგწონს, უბრალოდ იგონებ ალტერნატიულ სამყაროს და იქ გადადიხარ",
                "შენი გული ღიაა სამყაროს ყველა ნიუანსისთვის, რაც ხანდახან სრულ ემოციურ ქაოსს იწვევს",
            ],
            [
                "სხვისი დარდი საკუთარში ისე აგერევა, რომ მერე საკუთარ პრობლემებს ვეღარ პოულობ.",
                "მსხვერპლად ყოფნის ტკბილი სევდა ხანდახან იმდენად გითრევს, რომ რეალური გადაწყვეტილებების მიღება გავიწყდება.",
                "შენი ემპათია უსაზღვროა, ოღონდ საკუთარი საზღვრების არქონის გამო ხშირად სხვების ემოციურ ნაგავსაყრელად იქცევი.",
            ],
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
            [
                "შემოდიხარ ისე, თითქოს ოთახის კარი ფეხით შემოგეღოს — სანამ ვინმე რამეს იტყვის, ინიციატივა უკვე ხელში გიჭირავს",
                "სოციალურ ფორმალობებსა და ზედმეტ შესავლებს მომენტალურად ჭრი, თითქოს დრო ყველას ეწურებოდეს",
                "შენი პირველი შთაბეჭდილება მუდმივი მზადყოფნაა ჩხუბისთვის, მაშინაც კი, როცა უბრალოდ ყავის დასალევად მოხვედი",
            ],
            [
                "შენი პირდაპირი მზერა ისეთია, რომ ხალხი უნებურად თავდაცვის რეჟიმზე გადადის.",
                "ადამიანები შენგან დაუყოვნებლივ მოქმედებას ელიან, თუმცა ხანდახან უბრალოდ სიმშვიდე ურჩევნიათ.",
                "შემოდიხარ ხმაურით და ოთახში მყოფი ყველა ადამიანის გეგმებს თავდაყირა აყენებ.",
            ],
            ["Your physical stride into any room is bold, energetic, and immediate", "You cut past polite social preamble without wasting a second"],
            ["People look to you for immediate momentum the second you walk in.", "Your direct eye contact commands respect before you even speak."],
        ),
        (
            "taurus",
            [
                "ისეთი შთაბეჭდილება რჩება, თითქოს დედამიწის მიზიდულობის ცენტრი პირადად შენზე გადიოდეს — აუჩქარებელი, მძიმე და ურყევი",
                "აკვირდები ყველას მშვიდი, შემფასებელი მზერით და სანამ არ დარწმუნდები, რომ ადგილი უსაფრთხოა, პირს არ დააღებ",
                "შენი პოზა მყარია და ისეთ სიმშვიდეს ასხივებს, რომ გარშემომყოფებს საკუთარი აჩქარების რცხვენიათ",
            ],
            [
                "შენი თავშეკავებული მანერები პატივისცემას ბადებს, თუმცა შენი დაძვრა ადგილიდან თითქმის შეუძლებელია.",
                "შენს გვერდით ყოფნა ადამიანებს აუხსნელ უსაფრთხოებას ანიჭებს, ოღონდ სიახლეებს შენგან არავინ ელის.",
                "აუჩქარებელი ნაბიჯით მოდიხარ და ყველას აიძულებ შენს ნელ რიტმს მოერგონ.",
            ],
            ["Your initial impression is one of grounded composure and unhurried stability", "You take in the surroundings with a calm, attentive, steady gaze"],
            ["Your physical presence slows down the nervous energy of the entire room.", "You project quiet authority through calm posture and deliberate movement."],
        ),
        (
            "gemini",
            [
                "შემოსვლისთანავე სამ ადამიანს უკვე ელაპარაკები და მეოთხეს თვალით ანიშნებ — შენი ენერგია უწყვეტი სატელევიზიო გადაცემაა",
                "ისე მარტივად იწყებ ნაცნობობას, რომ ხალხს ძველი მეგობარი ჰგონიხარ, თუმცა ხუთ წუთში შეიძლება მათი სახელებიც დაგავიწყდეს",
                "შენი მზერა მუდმივად ახალ დეტალებს ეძებს და ერთ წერტილზე ორ წამსაც ვერ ჩერდება",
            ],
            [
                "შენი მსუბუქი იუმორი უხერხულობას წამებში ხსნის, თუმცა სერიოზულ თემაზე საუბარს შენთან ვერავინ ასწრებს.",
                "შენთან კომუნიკაცია ელვისებურია — სანამ სხვები თემას გაიაზრებენ, შენ უკვე მესამე ამბავზე გადახვედი.",
                "შენი ღიმილი ნებისმიერ ბარიერს ანგრევს, ოღონდ ეს მხოლოდ პირველი, ზედაპირული ფასადია.",
            ],
            ["Your expressive face and alert eyes communicate instant, lively curiosity", "You strike up engaging conversations with strangers as if you were old friends"],
            ["Playful banter dissolves social awkwardness the moment you open your mouth.", "Your animated gestures keep everyone engaged in your orbit."],
        ),
        (
            "cancer",
            [
                "ისეთი დამცავი და ფრთხილი გამომეტყველება გაქვს, თითქოს ყოველ წამს ვიღაცისგან თავდასხმას ელოდებოდე",
                "პირველი კონტაქტისას ისეთი სათნო და რბილი ჩანხარ, სანამ ვინმე შენს პირად სივრცეს არ შეეხება",
                "შენი თავაზიანი დისტანცია სინამდვილეში შინაგანი სიფრთხილე და უნდობლობაა",
            ],
            [
                "შენ არ ჩქარობ გახსნას — ჯერ ამოწმებ რამდენად უსაფრთხოა გარემო და მერე გადაწყვეტ, გაიღიმო თუ ნაჭუჭში ჩაიკეტო.",
                "ადამიანები შენში ინტუიციურად გრძნობენ სითბოს, თუმცა შენი მიუწვდომელი კედელი ხშირად აბნევთ.",
                "რბილი მზერით იყურები, მაგრამ შინაგანად ყოველ სიტყვასა და ინტონაციას მკაცრად ფილტრავ.",
            ],
            ["Your outward presentation carries a gentle, protective, approachable aura", "People instinctively sense emotional warmth beneath your polite reserve"],
            ["You observe the room carefully before lowering your guarded buffer.", "Your soft gaze provides instant, reassuring comfort to stressed people."],
        ),
        (
            "leo",
            [
                "შემოდიხარ და ოთახი ავტომატურად შენს პირად სცენად იქცევა — თუნდაც უბრალოდ მაღაზიაში პურზე იყო ჩასული",
                "შენი პოზა და მანერები იმდენად თავდაჯერებულია, რომ ხალხი ინსტინქტურად უკან იხევს, რათა შენი ბრწყინვალება არ დაჩრდილოს",
                "შენი გამორჩეული გარეგნობა შეუმჩნეველი ვერასდროს დარჩება, რადგან ყურადღების გარეშე ყოფნა შენთვის ფიზიკურად აუტანელია",
            ],
            [
                "შენ არ გჭირდება ხმამაღლა ლაპარაკი — შენი ყოფნა ოთახში ისედაც ყველაფერს ავსებს.",
                "შენი მზერა მეფური სითბოთია სავსე, სანამ ვინმე შენს ავტორიტეტს ეჭვქვეშ არ დააყენებს.",
                "სითბოს ასხივებ, მაგრამ ეს სითბო პირველ რიგში შენივე სიდიადის ხაზგასმას ემსახურება.",
            ],
            ["Your entrance naturally draws the room's gaze like light through a lens", "You radiate an open, charismatic warmth that commands effortless attention"],
            ["You don't need theatrical shouting; your posture does all the talking.", "Confidence sits upon your shoulders with effortless, natural poise."],
        ),
        (
            "virgo",
            [
                "შენი პირველი მზერა რენტგენის სკანერია — სანამ მიესალმები, უკვე შეამჩნიე სხვისი დაუთოებელი პერანგი და ჩამქრალი მზერა",
                "ისეთი თავშეკავებული და კრიტიკული იერით დგახარ, თითქოს ინსპექცია იყო და გარშემო ყველას შეფასებას უწერდე",
                "შენი გარეგნობა ყოველთვის იმდენად აკურატულია, რომ ქაოტური ადამიანები შენს დანახვაზე უხერხულობას გრძნობენ",
            ],
            [
                "შენი თავდაჭერილობა მაღალი კომპეტენციის შთაბეჭდილებას ტოვებს, თუმცა შენს მზერაში სითბოს პოვნა ცოტა რთულია.",
                "საუბრობ მშვიდად, კონკრეტულად და ისეთი ტონით, რომ სხვებს საკუთარი შეცდომების გასწორება უნდებათ.",
                "შენი მოკრძალება სინამდვილეში შენი ყველაზე მკაცრი თავდაცვითი ბარიერია.",
            ],
            ["Your demeanor is crisp, understated, observant, and immaculately neat", "Your sharp eyes take in functional details that slip past everyone else"],
            ["You project an air of quiet competence that earns instant professional respect.", "Understatement is your aesthetic signature, and it speaks volumes."],
        ),
        (
            "libra",
            [
                "შენი მომხიბვლელი ღიმილი ისეთი იდეალურია, რომ დიპლომატიურ კორპუსსაც შეშურდებოდა — ოღონდ ეს ღიმილი ხშირად უბრალოდ თავდაცვის ფარია",
                "ყველასთვის ისეთი საყვარელი და მოსაწონი ჩანხარ, რომ ხალხს ავიწყდება: შენი სიმპათია ხშირად უბრალოდ სოციალური რეფლექსია",
                "შენი გემოვნება და მანერები პირველივე წამიდან იკითხება, რადგან უგემოვნობას ფიზიკურ ტკივილად აღიქვამ",
            ],
            [
                "შენი დიპლომატია ყველაზე ხისტ ადამიანსაც კი არბილებს, თუმცა შენი ნამდვილი აზრი მაინც საიდუმლოდ რჩება.",
                "შენთან საუბარი ყველასთვის კომფორტულია, რადგან საკუთარ წყენას ღიმილის მიღმა ოსტატურად მალავ.",
                "მომხიბვლელობას ისე იყენებ, რომ უხერხულ სიტუაციებს ყოველთვის უვნებლად უვლი გვერდს.",
            ],
            ["Disarming social poise and graceful charm put everyone instantly at ease", "You navigate social etiquette with the natural grace of a seasoned diplomat"],
            ["Your aesthetic presentation is balanced, pleasing, and quietly magnetic.", "You possess the rare gift of making every conversational partner feel valued."],
        ),
        (
            "scorpio",
            [
                "ისეთი მზერით იყურები, თითქოს ყველას საიდუმლო ცოდვები იცოდე — შენს წინაშე ხალხი უნებურად დაძაბულობას გრძნობს",
                "შენი სიჩუმე იმდენად მძიმეა, რომ ოთახში ჰაერი სქელდება — ზედაპირულ საუბარს შენთან ვერავინ ბედავს",
                "შენს გარშემო ყოველთვის იგრძნობა იდუმალი, მიმზიდველი და საშიში აურა, რომელიც ცნობისმოყვარეობას აღვიძებს",
            ],
            [
                "შენ არ ხარჯავ სიტყვებს ცარიელ მისალმებებზე — შენი მზერა უკვე საკმარისი გაფრთხილებაა.",
                "შენს წინაშე თამაშის დაწყებას ყველა ერიდება, რადგან ყალბ ღიმილს პირველივე წამში შიშველი ხელებით ხსნი.",
                "შენი მაგნეტიზმი მომხიბვლელია, მაგრამ თან ისეთი მკაცრი, რომ დისტანციის დაცვას ყველა თავისით ირჩევს.",
            ],
            ["A penetrating gaze and formidable quiet intensity announce your arrival", "You project a compelling, mysterious presence that discourages shallow banter"],
            ["People hesitate to bluff around you; your eyes see through social games.", "Your silence commands more respect than the loud speeches of others."],
        ),
        (
            "sagittarius",
            [
                "შემოდიხარ ხმაურით, სიცილით და ისეთი ენერგიით, თითქოს კარები ახლახან გაგიღეს თავისუფლებისკენ",
                "შენი უშუალობა მომხიბვლელია, სანამ რამე ისეთს არ წამოაყრანტალებ, რის გამოც მთელი დარბაზი გაშეშდება",
                "შენ ოთახში შემოგაქვს თავგადასავლის სუნთქვა, თუმცა სოციალური ტაქტი ხშირად სახლში გრჩება",
            ],
            [
                "შენი ხმამაღალი სიცილი ბარიერებს წამებში ხსნის, ოღონდ სერიოზულ გარემოში ცოტა თავქარიანად გამოიყურები.",
                "შენთან ერთად ყოფნა პოზიტივთან ასოცირდება, სანამ ვინმეს მგრძნობიარე თემას შემთხვევით ფეხით არ გათელავ.",
                "თავისუფლების ისეთი წყურვილი იგრძნობა შენს სიარულში, თითქოს აქ დიდხანს გაჩერებას არც აპირებდე.",
            ],
            ["A breezy, candid entrance and expansive grin instantly dissolve pretenses", "You bring the fresh air of an open road into stuffy conference rooms"],
            ["Your unpretentious laughter makes newcomers feel like welcome companions.", "You project a buoyant, infectious optimism that lifts the entire room."],
        ),
        (
            "capricorn",
            [
                "ისეთი სერიოზული და საქმიანი სახე გაქვს, თითქოს კომპანიის გაკოტრების საქმეს იძიებდე — შენს დანახვაზე ხალხი უნებურად სწორდება",
                "შენი პირველი შთაბეჭდილება მკაცრი დისტანციაა: სანამ ადამიანი თავის ღირსებას არ დაამტკიცებს, მასთან ზედმეტ სიტყვას არ დახარჯავ",
                "შენი თავშეკავებული მანერები პატივისცემას ბადებს, თუმცა შენთან მიახლოებას გამბედაობა სჭირდება",
            ],
            [
                "შენი დისციპლინა პირველივე წამიდან იგრძნობა — შენს კომპანიაში უსაქმურად ჯდომას ყველა ერიდება.",
                "არ გჭირდება ზედმეტი დემონსტრირება; შენი ცივი თავდაჯერებულობა ყველაფერს თავის ადგილზე სვამს.",
                "შენი მზერა მკაცრია, მაგრამ სამაგიეროდ შენგან იაფფასიან დაპირებებს არავინ ელის.",
            ],
            ["Measured composure and authoritative gravity define your first impression", "You project the formidable competence of someone who runs the show"],
            ["You don't need flashy demonstrations; your steady reserve commands respect.", "People instinctively step aside and let you handle serious business."],
        ),
        (
            "aquarius",
            [
                "შენი ჩაცმულობა, მზერა ან მანერა ყოველთვის ამბობს: „მე თქვენნაირი არ ვარ“ — და ამით საშინლად ამაყობ",
                "ისეთი თავაზიანი, მაგრამ ცივი დისტანციით ურთიერთობ, რომ ადამიანი ხვდება: შენთვის ის უბრალოდ მორიგი სოციალური ფენომენია",
                "შენი მეგობრული, მაგრამ მიუკერძოებელი მზერა ინტერესს აღვიძებს, თუმცა სითბოს იქ იშვიათად იპოვიან",
            ],
            [
                "შენ არავის ჰგავხარ და ამას სპეციალურად უსვამ ხაზს, თუნდაც უბრალო დეტალებში.",
                "შენი სტილი დროს კი უსწრებს, მაგრამ ხანდახან უბრალოდ იმისთვის ხარ უცნაური, რომ ჩვეულებრივად ყოფნა გაშინებს.",
                "საუბარში ისე ერთვები, თითქოს შორიდან უყურებდე პროცესს და შინაგანად ირონიულ დასკვნებს აკეთებდე.",
            ],
            ["An unconventional, distinctly original vibe sets you apart in any crowd", "You project friendly, observant detachment with an unapologetic personal style"],
            ["Nobody mistakes you for a copy; your individuality is clear from thirty paces.", "You treat social conformity as an optional, mildly amusing spectator sport."],
        ),
        (
            "pisces",
            [
                "ისეთი მეოცნებე და რბილი მზერა გაქვს, თითქოს ამ რეალობაში მხოლოდ ნაწილობრივ იმყოფებოდე",
                "შენი აურა იმდენად დაუცველი ჩანს, რომ ხალხს შენი გადარჩენა უნდება — სანამ არ აღმოაჩენენ, რომ შენს ნისლში თავად დაიკარგნენ",
                "შენი ნაზი ხმა და მოძრაობები დამამშვიდებელ ეფექტს ახდენს, თუმცა კონკრეტულ პასუხს შენგან იშვიათად მიიღებენ",
            ],
            [
                "შენში იგრძნობა იდუმალი სიღრმე, თუმცა ხშირად ეს უბრალოდ რეალობისგან გაქცევის სურვილია.",
                "ადაპტაციას ისე ოსტატურად ახერხებ, რომ გარემოს ერწყმი და საკუთარ კონტურებს კარგავ.",
                "შენი რბილი გამოხედვა სიმპათიას იწვევს, ოღონდ პრაქტიკულ საკითხებში შენი იმედი არავის უნდა ჰქონდეს.",
            ],
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
            [
                "შენი ენერგია ისე სწრაფად იფეთქებს, რომ გარშემო ყველაფერს წვავ — სანამ საქმეს დაიწყებ, უკვე შედეგს ითხოვ და ლოდინი გაგიჟებს",
                "როცა რამე აგიტაცებს, შენი ენთუზიაზმი გადამდებია, ოღონდ სხვების დაღლას საერთოდ ვერ ამჩნევ",
                "შენს შემართებას „ლიდერობას“ ეძახი, თუმცა ხშირად ეს უბრალოდ მოთმინების სრული არარსებობა და სხვების გადათელვაა",
            ],
            [
                "პასიურობა შენთვის ფიზიკური ტკივილია; შენ მოქმედებისთვის ხარ შექმნილი, ოღონდ შედეგებზე ფიქრი გეზარება.",
                "შენი ცეცხლი ანათებს, მაგრამ თუ ფრთხილად არ იყავი, ახლობლებსაც წამში ფერფლად აქცევს.",
                "სადაც სხვები ფიქრობენ, შენ უკვე იწვი — მთავარია, ეს ენერგია უაზრო დრამაში არ გაფლანგო.",
            ],
            ["A high kinetic drive and spontaneous initiative define your core operating system", "When inspiration strikes, your enthusiasm sparks the entire environment"],
            ["Waiting around drains your battery; you are engineered for active execution.", "Your bold drive turns abstract intentions into reality at record speed."],
        ),
        (
            "earth",
            [
                "ისეთი პრაქტიკული და ურყევი ხარ, რომ ნებისმიერ სპონტანურ იდეას ცივი ბიუჯეტისა და რისკების კალკულატორით ხვდები",
                "შენ აფასებ მხოლოდ იმას, რასაც რეალური ფორმა, შედეგი და ფასი აქვს — ოცნებებს დროს არ უთმობ",
                "სტაბილურობის შენარჩუნება შენი მთავარი აკვიატებაა — სანამ ყველაფერი გეგმის მიხედვით არ მიდის, მშვიდად ვერ სუნთქავ",
            ],
            [
                "შენი მოთმინება ქაოსს სტაბილურობად აქცევს, თუმცა შენი სიჯიუტე ხანდახან ყველას ნერვებს უშლის.",
                "შენ ხარ მყარი საყრდენი, ოღონდ ცვლილებების მიმართ ისეთივე მგრძნობიარე ხარ, როგორც ბეტონის კედელი.",
                "აშენებ იმას, რაც დროს უძლებს, ოღონდ გზაში სპონტანურობისა და სიხარულის დავიწყება იცი.",
            ],
            ["Pragmatic realism and tactile grounding form the bedrock of your character", "You measure worth by enduring tangible outcomes, not fleeting novelty"],
            ["Your disciplined patience transforms messy disorder into reliable structures.", "You are the solid foundation that others instinctively rely upon."],
        ),
        (
            "air",
            [
                "იდეებზე, თეორიებსა და კონცეფციებზე საათობით შეგიძლია ილაპარაკო, ოღონდ რეალურ საქმეზე გადასვლისას უცებ ახალი თემა გაგახსენდება",
                "შენ გჭირდება ინტელექტუალური ჟანგბადი, თუმცა ემოციურ სიღრმეს ხშირად ლოგიკური ირონიით გაურბიხარ",
                "შენი აზროვნება თავისუფალია და ჩარჩოებს არ ცნობს, რაც პრაქტიკულ ცხოვრებაში ხშირად გაფანტულობას ემსგავსება",
            ],
            [
                "საკითხებს ობიექტურად უყურებ, თუმცა ადამიანურ გრძნობებს ხშირად ფორმულებამდე ამარტივებ.",
                "შენი გონებრივი სისხარტე გაძლევს საშუალებას ნებისმიერ საუბარში იბრწყინო, ოღონდ გულწრფელობას იშვიათად აჩენ.",
                "აკავშირებ იდეებსა და ადამიანებს, მაგრამ პირადად შენთან ემოციური სიახლოვის დამყარება ურთულესია.",
            ],
            ["Conceptual agility, lively communication, and social connectivity power your engine", "You require mental stimulation, fresh frameworks, and intellectual dialogue"],
            ["You connect disparate dots with effortless intellectual playfulness.", "Stagnant, unexamined ideas are the only things that truly bore you."],
        ),
        (
            "water",
            [
                "ინტუიციასა და ემოციურ განცდებს ისე ენდობი, რომ ფაქტებსა და ცივ ლოგიკას ხშირად უბრალოდ უგულებელყოფ",
                "სხვების ემოციურ ტალღებს ისე ისრუტავ, რომ მერე საკუთარ ცხოვრებას სხვისი დრამების მიხედვით ალაგებ და ამას „ემპათიას“ არქმევ",
                "შენი შინაგანი სამყარო ოკეანესავით ღრმაა, თუმცა ამ ოკეანეში ხშირად საკუთარ პასუხისმგებლობებს ძირავ",
            ],
            [
                "შენი მგრძნობელობა შენი ძალაა, ოღონდ ხშირად უბრალოდ უმიზეზო წყენებისა და დრამის წყაროდ იქცევა.",
                "შენი თანაგრძნობა უსაზღვროა, სანამ თავად არ გადაწყვეტ მსხვერპლის როლის მორგებას.",
                "გრძნობ იმას, რასაც სხვები ვერ ამჩნევენ, მაგრამ ხანდახან იქაც ხედავ ტრაგედიას, სადაც არაფერი ხდება.",
            ],
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
            [
                "ინიციატივის ხელში აღება შენი ბუნებრივი რეფლექსია — სადაც სხვები ფიქრობენ, შენ უკვე საქმეს იწყებ",
                "ლოდინი და სტაგნაცია შენთვის გაუსაძლისია; პირველი ნაბიჯის გადადგმა გიყვარს, ოღონდ ბოლომდე მიყვანა ხშირად გეზარება",
                "პირველობის წყურვილი იმდენად ძლიერია, რომ მეორე როლში ყოფნას საერთოდ პროცესიდან გასვლა გირჩევნია",
            ],
            [
                "სადაც სხვები ყოყმანობენ, შენ პროცესს იწყებ, მაგრამ რუტინულ ეტაპზე ინტერესს მომენტალურად კარგავ.",
                "შენი ლიდერული იმპულსი ბუნებრივია, ოღონდ სხვებისთვის ხშირად ზედმეტად მომთხოვნი და დომინანტური ხარ.",
                "შენ ანთებ პირველ ნაპერწკალს, ხოლო ხანძრის ჩაქრობა მერე სხვების საზრუნავი ხდება.",
            ],
            ["You are a natural instigator who launches movements and breaks deadlocks", "Standing still feels suffocating; you thrive by initiating bold new chapters"],
            ["Where others hesitate in debate, you take the first decisive step.", "Pioneering momentum is your natural habitat; you build from a blank slate."],
        ),
        (
            "fixed",
            [
                "ერთხელ არჩეულ პოზიციას ისე ეჭიდები, რომ მთელი სამყაროც რომ გადატრიალდეს, აზრს არ შეიცვლი და ამას „ერთგულებას“ დაარქმევ",
                "შენი შეუპოვრობა ლეგენდარულია, თუმცა მოქნილობის სრული დეფიციტი ხშირად დახურულ კედელთან ჯიუტად დგომას ემსგავსება",
                "ერთხელ მიღებულ გადაწყვეტილებას აღარასდროს გადახედავ, თუნდაც გარემოებები რადიკალურად შეიცვალოს",
            ],
            [
                "შენი ენერგია ხანგრძლივ მარათონზეა გათვლილი, თუმცა ახალი მიმართულების აღება შენთვის კატასტროფის ტოლფასია.",
                "შენი სტაბილურობა საიმედოა, ოღონდ კომპრომისზე წასვლა შენთვის დანებების ტოლფასია.",
                "არ ჩერდები მანამ, სანამ მიზანი არ მიიღწევა, თუნდაც ეს მიზანი უკვე დიდი ხნის წინ გამხდარიყო უაზრო.",
            ],
            ["Unwavering tenacity and loyal endurance define your operational style", "Once you commit to a course, distractions and noise bounce right off you"],
            ["You are built for the long marathon, not short, flashy sprints.", "Your steadfast consistency anchors projects and alliances through any weather."],
        ),
        (
            "mutable",
            [
                "ისე ოსტატურად ერგები ნებისმიერ ახალ რეალობას, რომ საკუთარი რეალური პოზიცია ხშირად წყლის ფორმასავით იცვლება",
                "ცვლილებების სიყვარული შენი ძალაა, მაგრამ როცა გადაწყვეტილების მიღების დრო მოდის, ისე მარტივად იცვლი მიმართულებას, რომ სხვებს საყრდენს აცლი",
                "ნებისმიერი სიტუაციიდან მშრალი გამოდიხარ, თუმცა სიმტკიცე და პრინციპულობა შენგან იშვიათი მოვლენაა",
            ],
            [
                "ტალღებზე ოსტატურად სრიალებ, თუმცა საკუთარი კურსის შენარჩუნება მუდმივად გიჭირს.",
                "შენი მოქნილობა გაძლევს საშუალებას ყველას მოერგო, ოღონდ საბოლოოდ საკუთარი თავი სად არის, აღარავინ იცის.",
                "ადაპტაციის უნარი გეხმარება, მაგრამ როცა სიმტკიცეა საჭირო, შენ უბრალოდ გვერდზე იწევი.",
            ],
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
