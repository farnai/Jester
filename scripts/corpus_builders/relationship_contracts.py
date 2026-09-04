"""
Seed data builder for 45 Relationship / Synastry semantic interpretation contracts.
Zero astrology jargon; strictly focused on interpersonal connection dynamics,
romantic friction, conversational flow, emotional resonance, and Jester twists.
"""
from scripts.corpus_builders.common import ContractSeedData


def get_relationship_contracts_data() -> list[ContractSeedData]:
    contracts: list[ContractSeedData] = []

    rel_defs = [
        # 1. Attraction Dynamics
        (
            "relationship.attraction.strong_chemistry.v1",
            "relationship",
            [
                "ერთ ოთახში რომ შემოდიხართ, ჰაერი ისე მძიმდება, თითქოს ვიღაცამ კონდიციონერი გამორთო და დრამა ჩართო",
                "თქვენს შორის იმდენად დაუფარავი მუხტია, რომ თავაზიანი საუბრის მცდელობა პირველივე წამს სასაცილოდ გამოიყურება",
                "ორივემ ზუსტად იცით, რა ხდება, მაგრამ ისე იქცევით, თითქოს შემთხვევით აღმოჩნდით ერთსა და იმავე კედელთან მიყუდებულები",
                "თვალებით ფლირტს ისე აშკარად ეწევით, რომ მთელ ოთახს უხერხულობისგან ყურები უწითლდება",
            ],
            [
                "ნაპერწკლები კარგია, მაგრამ ხანძარსაწინააღმდეგო სისტემა თუ არ მუშაობს, მალე ორივე ერთად დაიფერფლებით.",
                "თვალებით ფლირტს მორჩით — მთელმა ოთახმა გაიგო, რაც გინდათ, თქვენ კი ისევ თავს იკატუნებთ.",
                "ქიმია იდეალურია, სანამ საქმე იმაზე მიდგება, ვინ ვის დაურეკავს პირველი.",
                "ტემპერატურა მაღალია, თუმცა ამ მუხტის ყოველდღიურობაში გადატანა ცალკე ხელოვნებაა.",
            ],
            [
                "The kinetic attraction between you two is unmistakable from the first conversation",
                "There is a spontaneous magnetic current whenever you share the same room",
                "Your mutual chemistry bypasses polite formality with effortless speed",
            ],
            [
                "The spark is so immediate you might want to know where the fire extinguisher is.",
                "You two operate on a frequency where words are merely background music.",
                "The tension between you is alive, electric, and completely unscripted.",
            ],
        ),
        (
            "relationship.attraction.strong_chemistry.v2",
            "relationship",
            [
                "ერთ ოთახში რომ შემოდიხართ, ჰაერი ისე მძიმდება, თითქოს ვიღაცამ კონდიციონერი გამორთო და დრამა ჩართო",
                "თქვენს შორის იმდენად დაუფარავი მუხტია, რომ თავაზიანი საუბრის მცდელობა პირველივე წამს სასაცილოდ გამოიყურება",
            ],
            [
                "ნაპერწკლები კარგია, მაგრამ ხანძარსაწინააღმდეგო სისტემა თუ არ მუშაობს, მალე ორივე ერთად დაიფერფლებით.",
                "თვალებით ფლირტს მორჩით — მთელმა ოთახმა გაიგო, რაც გინდათ, თქვენ კი ისევ თავს იკატუნებთ.",
            ],
            [
                "The kinetic attraction between you two is unmistakable from the start",
            ],
            [
                "You two operate on a frequency where words are merely background music.",
            ],
        ),
        (
            "relationship.attraction.magnetic_chemistry.v1",
            "relationship",
            [
                "ერთმანეთს ისე ეჯახებით, როგორც ორი დამუხტული სადენი — იცით, რომ საშიშია, მაგრამ მაინც ხელს ჰკიდებთ",
                "თქვენი მიზიდულობა ყველა ლოგიკურ წესს აუქმებს და მერე ორივეს უკვირს, რატომ დაკარგეთ კონტროლი",
                "თავბრუდამხვევი აზარტი გაქვთ, თუმცა შედეგებზე ფიქრი ორივეს გეზარებათ",
            ],
            [
                "ლოგიკა კარიდან გადის იმ წამსვე, როგორც კი ერთმანეთის სიახლოვეს აღმოჩნდებით.",
                "ეს ის კავშირია, სადაც მშვიდობას არავინ ეძებს — მთავარია, აფეთქება ლამაზი გამოვიდეს.",
                "ერთად ყოფნისას მოსაწყენი არასდროს იქნება, სამაგიეროდ ნერვული სისტემა მუდმივ გამოცდას გადის.",
            ],
            [
                "Your mutual attraction strikes like lightning and ignores common sense",
                "You pull each other into orbit with an intoxicating, unpredictable intensity",
            ],
            [
                "Logic takes a back seat whenever you two end up in the same room.",
                "It is thrilling, kinetic, and completely resistant to safe predictions.",
            ],
        ),
        (
            "relationship.attraction.warm_affection.v1",
            "relationship",
            [
                "ისეთი სათუთი ზრუნვით ექცევით ერთმანეთს, თითქოს ფაიფურის ჭიქები იყოთ და არა ზრდასრული ადამიანები",
                "ერთად ყოფნისას ზედმეტად მშვიდად გრძნობთ თავს, რაც ცოტა საეჭვოცაა",
                "სითბოს ისე უშურველად გასცემთ, თითქოს კონკურსი იყოს საუკეთესო პარტნიორის წოდებაზე",
            ],
            [
                "ეს მყუდრო იდილია სასიამოვნოა, სანამ ერთმანეთის გაღიზიანებას ზედმეტი თავაზიანობით არ დაიწყებთ.",
                "ჩაი და პლედი კარგია, მაგრამ ხანდახან რეალურ პრობლემებზე ლაპარაკიც მოგიწევთ.",
                "სინაზე მშვენიერია, ოღონდ ვნებასაც დაუტოვეთ ცოტა ადგილი.",
            ],
            [
                "A gentle warmth and aesthetic sweetness define the way you interact",
                "Being around each other feels like stepping into a comfortably lit room",
            ],
            [
                "Your mutual affection is cozy, effortless, and genuinely soothing.",
                "You bring out an instinctive gentleness in one another.",
            ],
        ),
        (
            "relationship.attraction.energized_collaboration.v1",
            "relationship",
            [
                "როცა ერთად საქმეს იწყებთ, ენერგია ისე გემატებათ, თითქოს მთელ სამყაროს უნდა მოუგოთ შეჯიბრი",
                "იდეიდან მოქმედებამდე ნახევარი წამია, ოღონდ არცერთს არ გახსოვთ, გეგმა საერთოდ გქონდათ თუ არა",
                "თქვენი თანამშრომლობა სპორტულ აზარტს უფრო ჰგავს, ვიდრე მშვიდ პარტნიორობას",
            ],
            [
                "ტემპი შთამბეჭდავია, სანამ გაირკვევა, რომ საწვავი გამოგელიათ და რუკა სახლში დაგრჩათ.",
                "მთავარია, გზაში ერთმანეთს არ გადააჯირითოთ მხოლოდ იმიტომ, რომ მეორეზე სწრაფი აღმოჩნდეთ.",
                "ერთად მთებს გადადგამთ, ოღონდ მერე იმ მთების უკან დაბრუნება არ მოგინდეთ.",
            ],
            [
                "When you two combine forces, your collective energy multiplies exponentially",
                "You tackle ambitious challenges with creative adrenaline and teamwork",
            ],
            [
                "From initial idea to active execution, the distance between you is near zero.",
                "You push each other toward peak performance without heavy friction.",
            ],
        ),
        (
            "relationship.attraction.dynamic_drive.v1",
            "relationship",
            [
                "ორივეს გაზის პედალი გიყვართ და მუხრუჭს სისუსტედ თვლით",
                "ერთად დგომისას ისეთი მოუსვენრობა გიპყრობთ, თითქოს ადგილზე გაჩერება კანონით ისჯებოდეს",
                "თქვენი შეხვედრა ყოველთვის ახალი ქაოსისა და გეგმების დასაწყისია",
            ],
            [
                "სიჩქარე კარგია, მაგრამ საჭეს თუ ორივე ერთდროულად მოქაჩავთ, ბოძთან შეხვედრა გარდაუვალია.",
                "მოქმედება რომ გიყვართ, გასაგებია, ოღონდ დანიშნულების ადგილი წინასწარ რომ შეგეთანხმებინათ, უკეთესი იქნებოდა.",
                "ენერგია თავზე საყრელი გაქვთ, მთავარია, ერთმანეთის ნერვებზე არ დახარჯოთ.",
            ],
            [
                "You share a high-octane drive that refuses to sit still or overthink",
                "Being together feels like stepping on the gas pedal with zero hesitation",
            ],
            [
                "You resolve situations at breakneck speed because waiting bores you both.",
                "Just make sure you do not compete for the steering wheel while driving fast.",
            ],
        ),
        (
            "relationship.attraction.intense_magnetism.v1",
            "relationship",
            [
                "ისეთი მზერით უყურებთ ერთმანეთს, თითქოს პაროლი იცით, რომლითაც მეორის ფსიქიკის გატეხვა შეიძლება",
                "ზედაპირულ თემებზე საუბარს არც კი ცდილობთ — პირდაპირ იქ ურტყამთ, სადაც ყველაზე მეტად მტკივა ან იზიდავს",
                "თქვენს შორის ჰაერი იმდენად დაძაბულია, რომ ნებისმიერი უბრალო ფრაზა ორაზროვნად ჟღერს",
            ],
            [
                "ეს მიზიდულობა კი არა, ფსიქოლოგიური დეტექტივია, სადაც ორივე ეჭვმიტანილიცაა და გამომძიებელიც.",
                "საიდუმლოებებით თამაშს შეეშვით: ორივემ ზუსტად იცით, რასაც მალავთ.",
                "ინტენსივობა პიკზეა, ამიტომ ემოციური ჩაფხუტი არცერთს არ გაწყენდათ.",
            ],
            [
                "The pull between you is psychologically profound and impossible to fake",
                "Casual encounters are out of the question; you cut straight to the core",
            ],
            [
                "This connection has a transformative gravity that leaves neither of you unchanged.",
                "You see right through each other's masks from the very first minute.",
            ],
        ),
        (
            "relationship.attraction.mars_friction.v1",
            "relationship",
            [
                "თქვენი ფლირტი უფრო საჩვენებელ ჩხუბს ჰგავს, სადაც არცერთი არ აპირებს პირველი დანებდეს",
                "კამათის გარეშე ერთმანეთის მიმართ ინტერესს კარგავთ — დაძაბულობა თქვენი მთავარი საწვავია",
                "ორი ძლიერი ნებისყოფა ერთ ოთახში მუდმივად ამოწმებს, ვინ უფრო მალე აფეთქდება",
            ],
            [
                "სანამ ერთმანეთს ეგოს უსწორებთ, მიზიდულობა იზრდება; ოღონდ ბოლოს არ დაგავიწყდეთ, რაზე დაიწყეთ ჩხუბი.",
                "ეს ის შემთხვევაა, როცა წინააღმდეგობა ერთადერთი მიზეზია, რის გამოც ჯერ კიდევ ერთად ხართ.",
                "მთავარია, გამარჯვებულმა დამარცხებულს ყავა მაინც უყიდოს.",
            ],
            [
                "A feisty competitive edge electrifies the chemistry between you two",
                "Two headstrong temperaments constantly test each other's boundaries",
            ],
            [
                "The friction is what fuels the attraction; keeping the peace is secondary.",
                "Every conversation feels like a high-stakes sparring match with romantic undertones.",
            ],
        ),
        (
            "relationship.attraction.electric_fascination.v1",
            "relationship",
            [
                "ერთმანეთის უცნაურობები ისე გაინტერესებთ, თითქოს უცხოპლანეტელი გყავდეთ ლაბორატორიაში",
                "თქვენს შორის პროგნოზირებადი არაფერია — ყოველი დიალოგი მოულოდნელ მოსახვევში გადის",
                "ნორმალური ადამიანების წესები თქვენთან არ მუშაობს და ეს ორივეს სასაცილოდ გეჩვენებათ",
            ],
            [
                "არაპროგნოზირებადობა ამაღელვებელია, სანამ საქმე ელემენტარულ პუნქტუალურობამდე არ მივა.",
                "წესების დარღვევა გიხარიათ, მაგრამ ქაოსში ცხოვრება ადრე თუ გვიან ნერვებს დაგაწყვეტთ.",
                "ერთფეროვნება აქ არ არსებობს, სამაგიეროდ სიმშვიდეც სამუდამოდ დაკარგულია.",
            ],
            [
                "Your dynamic defies standard scripts; the fascination is spontaneous and wild",
                "You find each other's eccentricities endlessly captivating",
            ],
            [
                "Predictability is impossible here, which is precisely why you cannot look away.",
                "You break conventional rules together and love every second of it.",
            ],
        ),
        (
            "relationship.attraction.instinctive_heat.v1",
            "relationship",
            [
                "ტვინი ჯერ კიდევ სიტუაციის გაანალიზებას ცდილობს, როცა სხეული უკვე მოქმედებაზეა გადასული",
                "თქვენი რეაქციები ერთმანეთზე იმდენად იმპულსურია, რომ დიპლომატიას შანსი არ აქვს",
                "ერთმანეთის სიახლოვეში პულსი გიჩქარდებათ და საღი აზრი სადღაც ქრება",
            ],
            [
                "ინსტინქტი კარგია, ოღონდ მერე შედეგების ახსნა რომ მოგიწევთ, ეგეც გაითვალისწინეთ.",
                "ტემპერატურა წამში ადის პიკზე, მაგრამ გაციებაც ისეთივე სწრაფი იცის.",
                "ეს ის მუხტია, რომელიც თავდაპირველად თავბრუს გახვევთ, მერე კი თავის ტკივილს გიტოვებთ.",
            ],
            [
                "Gut-level chemistry and emotional responsiveness ignite in an instant",
                "Your physical and emotional reflexes toward each other are intensely immediate",
            ],
            [
                "Instinct moves faster than etiquette between you two.",
                "The atmosphere heats up before either of you has time to think twice.",
            ],
        ),
        (
            "relationship.attraction.aesthetic_harmony.v1",
            "relationship",
            [
                "ერთად ისე პოზირებთ, თითქოს მოდის ჟურნალის ყდისთვის გქონდეთ კასტინგი გავლილი",
                "ერთმანეთს კომპლიმენტებით ავსებთ და გემოვნებაზე ისე თანხმდებით, რომ მესამე პირს გული ერევა",
                "თქვენი მიზიდულობა დახვეწილ დეტალებსა და ვიზუალურ პერფექციონიზმზე დგას",
            ],
            [
                "ფასადი ბრწყინვალეა, ოღონდ ინტერიერშიც რომ შეიხედოთ და ნამდვილი პრობლემები ნახოთ, ცუდი არ იქნება.",
                "ესთეტიკა ურთიერთობას ვერ გადაარჩენს, თუ შიგნით რეალური შინაარსი არ დევს.",
                "სოციალურ ქსელებში იდეალურად გამოიყურებით; მთავარია, რეალობაშიც ასე იყოს.",
            ],
            [
                "You share an instinctive aesthetic harmony and refined romantic taste",
                "Creating graceful, beautiful experiences together comes naturally",
            ],
            [
                "You make each other feel effortlessly appreciated and admired.",
                "Your connection is styled with organic elegance and mutual charm.",
            ],
        ),
        (
            "relationship.attraction.magnetic_presence.v1",
            "relationship",
            [
                "ერთად ოთახში რომ დგახართ, ყურადღების ცენტრში ყოფნა ისე გსიამოვნებთ, რომ სხვები აღარც გახსოვთ",
                "ერთმანეთის მომხიბვლელობას სარკესავით ირეკლავთ და საკუთარი თავით ტკბებით",
                "თქვენს შორის მიზიდულობა იმდენად თეატრალურია, რომ მაყურებლის გარეშე თითქოს აზრს კარგავს",
            ],
            [
                "ეს მიზიდულობაა თუ უბრალოდ ორი ნარცისის წარმატებული კოლაბორაცია?",
                "გარშემომყოფები კი გიყურებენ, მაგრამ მთავარია, ერთმანეთში მარტო საკუთარი ანარეკლი არ გიყვარდეთ.",
                "მშვენიერება კარგია, მაგრამ როცა შუქი ჩაქრება, რა რჩება?",
            ],
            [
                "Visual appeal and outward charm create an instant mutual fascination",
                "You find each other's physical presence and social poise deeply captivating",
            ],
            [
                "The visual rapport is obvious to everyone standing in the same room.",
                "You mirror each other's appeal with effortless social flair.",
            ],
        ),
        (
            "relationship.attraction.bold_momentum.v1",
            "relationship",
            [
                "არცერთი არ უყურებთ ნიშნებს — პირდაპირ წინ გარბიხართ და შედეგებზე მერე ფიქრობთ",
                "თქვენი ურთიერთობა ისე ვითარდება, თითქოს ვიღაცამ აჩქარების ღილაკს დააჭირა და გაეჭედა",
                "ერთმანეთს ისეთ რისკებზე უბიძგებთ, რაზეც მარტო ყოფნისას არც კი გაიფიქრებდით",
            ],
            [
                "გაბედული ნაბიჯები კარგია, სანამ კედელს არ შეეჯახებით მთელი სისწრაფით.",
                "სანამ გადაწყვეტთ, რომ ყველაფერი შეგიძლიათ, გაარკვიეთ, საით მირბიხართ.",
                "მოქმედება გიყვართ, თუმცა შედეგებზე პასუხისმგებლობის აღება ცალკე საკითხია.",
            ],
            [
                "A bold kinetic momentum propels your dynamic forward without hesitation",
                "You inspire assertive, fearless moves in each other from day one",
            ],
            [
                "Hesitation evaporates whenever you decide to tackle something together.",
                "Your mutual energy is decisive, active, and thoroughly engaging.",
            ],
        ),

        # 2. Harmony Dynamics
        (
            "relationship.harmony.emotional_resonance.v1",
            "relationship",
            [
                "ერთმანეთის განწყობას უსიტყვოდ ხვდებით, მაგრამ ამას ხშირად იყენებთ იმისთვის, რომ საუბარს თავი აარიდოთ",
                "ისეთი ემოციური სინქრონი გაქვთ, თითქოს ერთმანეთის თავში უნებართვოდ დაძრწოდეთ",
                "ერთად ყოფნისას სიჩუმეც კი იმდენად კომფორტულია, რომ რეალური პრობლემების თქმა გეზარებათ",
            ],
            [
                "უსიტყვოდ გაგება მოსახერხებელია, მაგრამ ტელეპათიის იმედად ყოფნა საბოლოოდ ყოველთვის გაუგებრობით მთავრდება.",
                "ემოციების გაზიარება კარგია, სანამ ერთმანეთის დეპრესიას პირად პასუხისმგებლობად არ აქცევთ.",
                "ერთ ტალღაზე ყოფნა კარგია, ოღონდ ხანდახან ხმამაღალი ლაპარაკიც არ დაგავიწყდეთ.",
            ],
            [
                "You tune into each other's internal emotional weather without needing subtitles",
                "A profound instinctive acceptance makes being together feel like coming home",
            ],
            [
                "Silent understanding is wonderful, just remember to speak out loud once in a while.",
                "Your emotional wavelengths sync up with remarkable organic ease.",
            ],
        ),
        (
            "relationship.harmony.core_harmony.v1",
            "relationship",
            [
                "ფუნდამენტურ საკითხებში იმდენად ერთნაირად ფიქრობთ, რომ კამათის დაწყებაც კი მოსაწყენად გეჩვენებათ",
                "თითქოს ერთი და იგივე სცენარით გაიზარდეთ — იმდენად ემთხვევა თქვენი შეხედულებები",
                "ერთად ყოფნა ისე ძალდაუტანებლად მიდის, რომ ხანდახან ცოტა დრამაც კი გენატრებათ",
            ],
            [
                "ასეთი თანხვედრა კომფორტულია, ოღონდ ფრთხილად: ზედმეტი ერთსულოვნება აზროვნებას აზარმაცებს.",
                "ყველაფერში შეთანხმება იდეალურია, სანამ რომელიმე თქვენგანი განსხვავებული აზრის გამოთქმას არ გაბედავს.",
                "საძირკველი მყარია, მთავარია, შიგნით ცეცხლი არ ჩაქრეს.",
            ],
            [
                "Your foundational worldviews and moral compasses align naturally",
                "Core decisions feel easy because your guiding values match effortlessly",
            ],
            [
                "It feels as though you both read the exact same rulebook growing up.",
                "You do not need to negotiate the basics; your foundation is already solid.",
            ],
        ),
        (
            "relationship.harmony.gentle_affinity.v1",
            "relationship",
            [
                "ერთმანეთს ისეთი გადამეტებული სიფრთხილით ექცევით, თითქოს მყიფე მინის სათამაშოები გეჭიროთ ხელში",
                "ნებისმიერ უხეშ სიტყვას ისე არიდებთ თავს, რომ ხანდახან სიმართლეც კი იკარგება",
                "ერთმანეთის დამშვიდება ისე კარგად იცით, რომ რეალური კონფლიქტის დანახვაც აღარ გინდათ",
            ],
            [
                "მზრუნველობა კარგია, მაგრამ საბავშვო ბაღის რეჟიმიდან გამოსვლაც დროა.",
                "ზედმეტი სინაზე კონფლიქტს კი არ აქრობს, უბრალოდ ხალიჩის ქვეშ მალავს.",
                "მთავარია, სხვისი დარდი საკუთარ საშინაო დავალებად არ გაიხადოთ.",
            ],
            [
                "Tender emotional appreciation and cozy soothing define your shared rhythm",
                "You instinctively soften the hard edges of each other's difficult days",
            ],
            [
                "Just make sure you do not adopt each other's burdens as personal homework.",
                "Your gentle presence serves as the ultimate decompression chamber.",
            ],
        ),
        (
            "relationship.harmony.generous_affection.v1",
            "relationship",
            [
                "ერთმანეთს კომპლიმენტებითა და მხარდაჭერით ისე ავსებთ, თითქოს პირადი პიარ-სააგენტოები გქონდეთ დაქირავებული",
                "გულუხვობა ორივეს გიყვართ, ოღონდ მთავარია, აუდიტორიამ დაინახოს, რა კარგი ადამიანები ხართ",
                "ერთად ყოფნისას სამყარო იმდენად ვარდისფერი ჩანს, რომ რეალობის დანახვა ჭირს",
            ],
            [
                "ეს მხარდაჭერა გულწრფელია, სანამ ერთ-ერთი თქვენგანი ჩრდილში არ აღმოჩნდება.",
                "ტაშის დაკვრას რომ მორჩებით, რეალურ ცხოვრებაში დაბრუნებაც მოგიწევთ.",
                "გულუხვობა კარგია, მაგრამ საზღვრები აქაც აუცილებელია.",
            ],
            [
                "You celebrate each other's milestones with genuine warmth and zero jealousy",
                "Generous appreciation flows freely without score-keeping or petty rivalries",
            ],
            [
                "In an atmosphere this encouraging, personal growth happens on autopilot.",
                "You consistently bring out the brightest, most generous versions of each other.",
            ],
        ),
        (
            "relationship.harmony.deep_empathy.v1",
            "relationship",
            [
                "ერთმანეთის ტკივილს ისე განიცდით, თითქოს საკუთარი პრობლემები ცოტა გქონდეთ",
                "უსაფრთხო სივრცე შექმენით, სადაც ორივეს შეგიძლიათ დაუსრულებლად იწუწუნოთ და ამას „სიღრმე“ დაარქვათ",
                "ერთმანეთის სისუსტეებს ისე უფრთხილდებით, რომ ზრდის მოტივაცია გეკარგებათ",
            ],
            [
                "ემპათია მშვენიერია, ოღონდ ერთმანეთის ფსიქოთერაპევტებად ნუ გადაიქცევით — ამისთვის პროფესიონალები არსებობენ.",
                "სხვისი ცრემლების ყლაპვას რომ მორჩებით, გაიხსენეთ, საკუთარი ცხოვრებაც რომ გაქვთ მისახედი.",
                "აქ მიღება სრულია, თუმცა კომფორტის ზონაში ჩარჩენის რისკიც მაღალია.",
            ],
            [
                "Your emotional processing styles sync up with rare, telepathic ease",
                "You hold safe space for each other's vulnerabilities without any judgment",
            ],
            [
                "Here, pretenses fall away instantly; you meet each other at the deepest level.",
                "This emotional haven easily weathers external stress and uncertainty.",
            ],
        ),
        (
            "relationship.harmony.intuitive_communion.v1",
            "relationship",
            [
                "ისეთი მისტიკური გამომეტყველებით უყურებთ ერთმანეთს, თითქოს სამყაროს საიდუმლო გაიგეთ და ჩვეულებრივი ადამიანები აღარ გაინტერესებთ",
                "ერთმანეთის უთქმელ აზრებს კითხულობთ, მაგრამ როცა რამე მარტივი უნდა შეათანხმოთ, უცებ ენა გებმით",
                "თქვენს შორის არის პოეტური კავშირი, რომელსაც მიწაზე დაშვება უჭირს",
            ],
            [
                "პოეტური კავშირი კარგია, მაგრამ ქირის გადახდის დროს ინტუიცია ნაკლებად ეფექტურია.",
                "ღრუბლებში ფრენას შეეშვით — რეალობასთან შეჯახება მტკივნეული იქნება.",
                "გრძნობები სიღრმისეულია, მაგრამ სიტყვების თქმაც დროდადრო აუცილებელია.",
            ],
            [
                "An intuitive, gentle communion allows you to communicate beneath surface words",
                "Forgiveness and sensitive understanding soften every potential rough edge",
            ],
            [
                "Just remember to stay grounded in reality so you do not wander off into daydreams.",
                "You sense each other's moods across distance as if connected by an invisible thread.",
            ],
        ),
        (
            "relationship.harmony.transformative_depth.v1",
            "relationship",
            [
                "თქვენი ურთიერთობა ისეთია, რომ ყოველი დიალოგი ეგზისტენციალურ კრიზისში ან ფსიქოლოგიურ კათარზისში გადადის",
                "მსუბუქად ყოფნა არ შეგიძლიათ — აუცილებლად უნდა ამოქექოთ ერთმანეთის ყველაზე ბნელი კუთხეები",
                "ნდობის მოსაპოვებლად ერთმანეთს ისეთ გამოცდებს უწყობთ, თითქოს საიდუმლო სამსახურში იღებდეთ",
            ],
            [
                "ტრანსფორმაცია კარგია, მაგრამ ხანდახან ადამიანებს უბრალოდ პიცის შეჭმა და სისულელეებზე სიცილი უნდათ.",
                "საკუთარ თავზე მუშაობით რომ დაიღლებით, გაიხსენეთ, რომ ეს ურთიერთობაა და არა რეაბილიტაციის კურსი.",
                "სიღრმე მშვენიერია, ოღონდ ზედაპირზე ამოსვლაც არ დაგავიწყდეთ ჟანგბადის ჩასასუნთქად.",
            ],
            [
                "Your bond bypasses polite illusions to explore unfiltered emotional truth",
                "You catalyze deep personal reinvention simply by being honest together",
            ],
            [
                "Trust takes serious investment here, but once granted, it is absolute.",
                "You fearlessly discuss the hard topics that others spend years avoiding.",
            ],
        ),

        # 3. Growth & Tension Dynamics
        (
            "relationship.growth.complementary_balance.v1",
            "relationship",
            [
                "იმდენად განსხვავებული რაკურსით უყურებთ სამყაროს, რომ საოცრებაა, ერთ ენაზე როგორ ლაპარაკობთ",
                "ერთმანეთის ნაკლოვანებებს ავსებთ, თუმცა ამას ხშირად ერთმანეთის ჭკუის სწავლებისთვის იყენებთ",
                "ერთად ყოფნისას ხედავთ იმას, რაც მარტო ყოფნისას გამოგეპარებოდათ, თუმცა ამის აღიარება გეძნელებათ",
            ],
            [
                "იდეალური ბალანსია ზუსტად მანამ, სანამ გადაწყვეტთ, ვინ მართავს მანქანას და ვისი პლეილისტი ჩაირთვება.",
                "კონტრასტი გიზიდავთ, მაგრამ ყოველდღიურობაში სწორედ ეს განსხვავებები დაგაწყვეტთ ნერვებს.",
                "სხვადასხვა პოლუსი ხართ; მთავარია, ერთმანეთის განადგურება არ სცადოთ.",
            ],
            [
                "You view the horizon from opposite vantage points that complement each other",
                "Where one of you hesitates, the other instinctively provides balance",
            ],
            [
                "Fascinating dynamic, right up until you have to decide who drives the car.",
                "Your creative contrasts keep complacency from ever settling in.",
            ],
        ),
        (
            "relationship.growth.dynamic_emotional_tension.v1",
            "relationship",
            [
                "თქვენთან ამინდი უფრო ხშირად იცვლება, ვიდრე მთაში — ხან სიყვარულის მორცხვი მზეა, ხან მეხთატეხა",
                "გრძნობების გამოხატვის განსხვავებული სტილი გაქვთ და მუდმივად გგონიათ, რომ მეორე არასწორად რეაგირებს",
                "თქვენი ურთიერთობა მუდმივ მზადყოფნას მოითხოვს, თითქოს სახანძრო რაზმში მუშაობდეთ",
            ],
            [
                "დრამა ცხოვრებას აფერადებს, მაგრამ ყოველ საღამოს თეატრალურ წარმოდგენას ნერვები დიდხანს ვერ გაუძლებს.",
                "სანამ გაარკვევთ, ვინ უფრო განაწყენებულია, მიზეზი უკვე ორივეს დაგავიწყდებათ.",
                "მოსაწყენად ნამდვილად არ გეცლებათ, მთავარია, კომედია ტრაგედიაში არ გადაიზარდოს.",
            ],
            [
                "Your emotional processing styles clash in ways that demand constant adjustment",
                "Navigating divergent sensitivities requires active calibration from both sides",
            ],
            [
                "Boredom is impossible; just make sure you do not mistake comedy for tragedy.",
                "The creative friction prevents stagnation, provided neither takes it too personally.",
            ],
        ),
        (
            "relationship.growth.contrasting_perspectives.v1",
            "relationship",
            [
                "ერთი და იმავე ფაქტიდან ორი სრულიად საპირისპირო დასკვნა გამოგაქვთ და ორივე დარწმუნებული ხართ საკუთარ გენიალურობაში",
                "თქვენი დისკუსიები პარლამენტის სხდომას ჰგავს — ბევრი ხმაური, ნულოვანი კომპრომისი",
                "ერთმანეთის სისუსტეებს ისე მკაფიოდ ხედავთ, რომ ცდუნებას ვერ უძლებთ, იქვე არ წამოაძახოთ",
            ],
            [
                "სარკეში ყურება კარგია, ოღონდ თუ მარტო მეორის ნაკლს ამჩნევთ, სარკის გატეხვა მოგინდებათ.",
                "ინტელექტუალური დებატები მანამაა სახალისო, სანამ პირადი თავმოყვარეობა არ ჩაერთვება.",
                "სხვისი შეცდომების გამოსწორებას რომ მორჩებით, საკუთარ თავზეც დაფიქრდით.",
            ],
            [
                "You stand on opposite sides of the same mirror, seeing shared themes from inverse angles",
                "Your debates push both of you out of comfortable intellectual echo chambers",
            ],
            [
                "Disagreements turn into stimulating masterclasses as long as egos stay checked.",
                "You mirror each other's blind spots with startling, constructive clarity.",
            ],
        ),
        (
            "relationship.growth.ego_friction.v1",
            "relationship",
            [
                "ორი ძლიერი ეგო ერთ სივრცეში — ჰაერი იმდენად მწირია, რომ ყოველი გადაწყვეტილება ტახტისთვის ბრძოლად იქცევა",
                "არცერთს არ გინდათ აღიაროთ, რომ მეორე მართალი იყო, თუნდაც ფაქტები სახეში გეცემოდეთ",
                "დათმობაზე წასვლა თქვენთვის კაპიტულაციას ნიშნავს, ამიტომ კედელს ჯიუტად აწვებით",
            ],
            [
                "გვირგვინი ერთია და ორივე ერთად ვერ დაიხურავთ; რიგრიგობით ტარება ისწავლეთ, თორემ ორივეს ჩამოგცვივდებათ.",
                "კომპრომისი კაპიტულაცია არ არის, თუმცა თქვენთვის ეს ომის წაგების ტოლფასია.",
                "თუ ამ სიჯიუტეს გარეთ მიმართავთ, მთებს გადადგამთ; შიგნით მიმართული კი ორივეს დაგასუსტებთ.",
            ],
            [
                "Two dominant wills in the same room occasionally find the oxygen running thin",
                "Neither of you enjoys backing down when personal authority is challenged",
            ],
            [
                "Compromise is not surrender here; it is a tactical victory for the alliance.",
                "If you point that collective firepower outward, you become unstoppable.",
            ],
        ),
        (
            "relationship.growth.pacing_tension.v1",
            "relationship",
            [
                "ერთს უკვე ჩემოდანი აქვს ჩალაგებული, მეორე კი ჯერ კიდევ ამინდის პროგნოზს აანალიზებს",
                "ტემპების სხვაობა გაგიჟებთ: ერთი მეორეს მუხრუჭს ეძახის, მეორე პირველს — თვითმკვლელ მძღოლს",
                "დროსთან მიმართებაში იმდენად განსხვავებული ხედვა გაქვთ, რომ შეხვედრის დათქმაც კი თავის ტკივილია",
            ],
            [
                "სიჩქარე და სიფრთხილე იდეალური კომბინაციაა, თუ გზაში ერთმანეთი არ დახოცეთ.",
                "სანამ ერთი ფიქრობს, მეორე უკვე შეცდომას უშვებს — სამაგიეროდ, ბალანსი დაცულია.",
                "მოთმინება აქ ის უნარია, რომლის სწავლაც ორივეს მოგიწევთ, თუნდაც კბილების ღრჭიალით.",
            ],
            [
                "One wants to accelerate immediately while the other insists on checking every bolt",
                "Friction over timing tests whether impatience or caution wins the day",
            ],
            [
                "Once you calibrate your cadence, speed and structure become an unbeatable combo.",
                "Patience is the primary skill this connection demands from both of you.",
            ],
        ),
        (
            "relationship.growth.dynamic_spark.v1",
            "relationship",
            [
                "თქვენს შორის სიმშვიდე არ არსებობს: თუ პრობლემა არ არის, ხელოვნურად შექმნით, რომ მერე აზარტით განიხილოთ",
                "ერთმანეთის ღილაკებზე დაჭერა თქვენი საყვარელი სპორტია",
                "ჩვეულებრივ რუტინას ვერ იტანთ, ამიტომ ყოველდღიურობას პატარა დრამებით აზავებთ",
            ],
            [
                "ნაპერწკალი კარგია, მაგრამ ხანძარი რომ გაჩნდება, დამნაშავეს ნუღარ ეძებთ.",
                "მთავარია, კამათის შემდეგ ვახშამი მეგობრულად გაიყოთ და ჩანგლები იარაღად არ გამოიყენოთ.",
                "ეს ნაპერწკალი ურთიერთობას ცოცხალს ტოვებს, ოღონდ ემოციურ ენერგიასაც გვარიანად წოვს.",
            ],
            [
                "There is always a provocative topic ready to spark an energetic debate between you",
                "You challenge each other to stay mentally agile and refuse comfortable apathy",
            ],
            [
                "The dynamic spark keeps the connection alive, provided dinner is shared after.",
                "You push each other's buttons, but mostly because the reaction is entertaining.",
            ],
        ),
        (
            "relationship.growth.emotional_divergence.v1",
            "relationship",
            [
                "კრიზისის დროს ერთი კუთხეში ჯდება და დუმს, მეორე კი კედლებს ანგრევს, რომ საუბარი დაიწყოს",
                "სტრესთან გამკლავების ისეთი რადიკალური მეთოდები გაქვთ, თითქოს სხვადასხვა ბიოლოგიური სახეობა იყოთ",
                "ხშირად გგონიათ, რომ მეორე სპეციალურად იქცევა ისე, რომ თქვენ გაგაღიზიანოთ",
            ],
            [
                "სიჩუმე ყოველთვის უარყოფას არ ნიშნავს, ხოლო ხმამაღალი საუბარი — თავდასხმას. თარგმანი ისწავლეთ.",
                "სანამ ერთმანეთს ემოციურ ყრუ-მუნჯობას აბრალებთ, დაფიქრდით, იქნებ უბრალოდ ჟანგბადი გჭირდებათ.",
                "განსხვავებული რიტმი გაიძულებთ უფრო ყურადღებიანი გახდეთ, თუნდაც ეს დისკომფორტს გიქმნიდეთ.",
            ],
            [
                "Under pressure, one withdraws into silence while the other wants to talk it out now",
                "Your coping languages diverge, requiring conscious translation rather than panic",
            ],
            [
                "Giving each other breathing room is not detachment; it is essential respect.",
                "Learning each other's emotional dialect turns potential rift into deep maturity.",
            ],
        ),
        (
            "relationship.growth.power_clash.v1",
            "relationship",
            [
                "როცა საქმე პრინციპებს ეხება, ორივე მზად ხართ გემი ჩაძიროთ, ოღონდ საჭე ხელიდან არ გაუშვათ",
                "კონტროლის დათმობა თქვენთვის ფიზიკურ ტკივილთან ასოცირდება",
                "ეს არის ნებისყოფის დაუნდობელი ტესტი, სადაც კომპრომისს სისუსტედ აღიქვამთ",
            ],
            [
                "ამ ომში გამარჯვებული არ იქნება — ან ერთად ააშენებთ იმპერიას, ან ერთმანეთის ნანგრევებზე იცეკვებთ.",
                "საზღვრების დაცვა კარგია, მაგრამ თუ საზღვარზე ეკლიან მავთულს გააბამთ, ურთიერთობა ციხედ გადაიქცევა.",
                "ძალაუფლების გაყოფა რომ ისწავლოთ, ბევრად ნაკლები ენერგია დაგეხარჯებოდათ.",
            ],
            [
                "When fundamental principles clash, neither of you yields an inch voluntarily",
                "Unbending willpower on both sides creates a high-stakes test of mutual respect",
            ],
            [
                "There is no solo winner here; you either succeed as co-architects or exhaust each other.",
                "Redirect that fierce stubbornness outward and you can move actual mountains.",
            ],
        ),
        (
            "relationship.growth.sobering_realism.v1",
            "relationship",
            [
                "რომანტიკულ ზღაპრებს აქ ადგილი არ აქვს — თქვენი ურთიერთობა უფრო ბიზნეს-ხელშეკრულებას ჰგავს მკაცრი პირობებით",
                "ემოციებს ისეთი სიფრთხილით გასცემთ, თითქოს ბანკის კრედიტს ამტკიცებდეთ",
                "სპონტანურობა აქ წესების დარღვევად ითვლება და ორივე ცდილობთ ყველაფერი წინასწარ გათვალოთ",
            ],
            [
                "საიმედოობა ფასდაუდებელია, მაგრამ ხანდახან ექსელ-ის ცხრილიდან თავის ამოყოფაც აუცილებელია.",
                "ზედმეტი პრაგმატიზმით რომ არ გაიყინოთ, ცოტა სისულელეების ჩადენაც სცადეთ ხოლმე.",
                "სიმწიფე კარგია, თუმცა ბავშვური სიხარულიც სჭირდება ურთიერთობას.",
            ],
            [
                "Fantasies find no quarter here; reality demands measurable accountability",
                "Emotional trust is earned through patient consistency rather than grand rhetoric",
            ],
            [
                "The value of this bond compounds over years, even if the opening feels reserved.",
                "Mature dependability is far rarer and more romantic than hollow theatrics.",
            ],
        ),
        (
            "relationship.growth.strategic_resistance.v1",
            "relationship",
            [
                "ერთი ახალ იდეას ისვრის, მეორე კი მაშინვე ათ მიზეზს პოულობს, რატომ ჩავარდება ეს გეგმა",
                "ყოველი ინიციატივა ისეთ მკაცრ აუდიტს გადის, რომ სპონტანურობა ჩანასახშივე კვდება",
                "ერთმანეთის იდეებს ისე ფილტრავთ, თითქოს სახელმწიფო საიდუმლოებას ამუშავებდეთ",
            ],
            [
                "ეს ხარისხის კონტროლია თუ უბრალოდ სხვისი ენთუზიაზმის ჩახშობის ხელოვნება?",
                "გეგმები კი გამოვა უნაკლო, ოღონდ მათი განხორციელების ხალისი აღარავის შერჩება.",
                "სიფრთხილე კარგია, მაგრამ ხანდახან გარისკვაც ამართლებს.",
            ],
            [
                "One hits the accelerator while the other reflexively tests the emergency brakes",
                "Rigorous stress-testing precedes every significant joint decision",
            ],
            [
                "This friction filters out bad ideas: only durable, well-built plans survive.",
                "Do not mistake careful skepticism for sabotage; it is simply quality control.",
            ],
        ),
        (
            "relationship.growth.limitless_ambition.v1",
            "relationship",
            [
                "ერთად ყოფნისას თქვენი ეგო და გეგმები ისეთ მასშტაბებს აღწევს, რომ დედამიწა პატარა გეჩვენებათ",
                "ერთმანეთს გრანდიოზული იდეებით კვებავთ, მაგრამ დეტალებზე პასუხისმგებლობის აღება არცერთს არ გინდათ",
                "თქვენი ენთუზიაზმი ხშირად რეალობის საზღვრებს სცდება და ილუზიებში გადადის",
            ],
            [
                "სამყაროს დაპყრობა კარგია, ოღონდ კომუნალურების გადახდაც რომ არ დაგავიწყდეთ, უკეთესი იქნება.",
                "ამბიციები უსაზღვრო გაქვთ, მთავარია, რეალობასთან კავშირი სულ არ დაკარგოთ.",
                "დიდი გეგმები პატარა ნაბიჯებით იწყება; პირდაპირ კოსმოსში გაფრენას ნუ ელით.",
            ],
            [
                "Being together inflates your mutual ambitions until standard goals look tiny",
                "You challenge each other to think bolder and refuse timid compromises",
            ],
            [
                "Just ensure that between grand visions, someone remembers to pay the electric bill.",
                "Your collective optimism expands boundaries and draws extraordinary luck.",
            ],
        ),

        # 4. Communication Dynamics
        (
            "relationship.communication.intellectual_flow.v1",
            "relationship",
            [
                "ისეთი სისწრაფით ცვლით აზრებსა და ირონიას, რომ გვერდით მყოფს თავი ნელთბილ სტატისტად ეჩვენება",
                "ნახევარ სიტყვაში გესმით ერთმანეთის ცინიზმი და ეს ორივეს უდიდეს სიამოვნებას განიჭებთ",
                "სიჩუმეშიც კი იგრძნობა, როგორ მუშაობს ორივეს ტვინი ახალი პასუხის მოსაფიქრებლად",
            ],
            [
                "ინტელექტუალური პინგ-პონგი ბრწყინვალეა, ოღონდ გრძნობებზე ლაპარაკის დროსაც სარკაზმს თუ არ გამორთავთ, მარტო დარჩებით.",
                "ერთმანეთის აზრების დასრულება კარგია, მაგრამ ხანდახან აცადეთ მეორეს წინადადების ბოლომდე თქმა.",
                "აზრები სწრაფად იცვლება, მთავარია, არსი არ დაგეკარგოთ გზაში.",
            ],
            [
                "Conversations between you resemble a championship ping-pong rally",
                "Mental agility and matching wit make small talk delightfully obsolete",
            ],
            [
                "Ideas bounce back and forth so fast an outsider would get whiplash watching.",
                "You share shorthand references and laugh at jokes before they are finished.",
            ],
        ),
        (
            "relationship.communication.mutual_understanding.v1",
            "relationship",
            [
                "საერთო ენა ისე მარტივად იპოვეთ, თითქოს ერთსა და იმავე კლასში იჯექით ბოლო მერხზე და მასწავლებელს დასცინოდით",
                "რთულ თემებზეც კი მშვიდად მსჯელობთ, რაც დღევანდელ სამყაროში თითქმის არაბუნებრივია",
                "აზრების გაზიარებისას არ გჭირდებათ თავის დაცვა, რაც იშვიათი კომფორტია",
            ],
            [
                "ასეთი კომფორტული დიალოგი საშიშია: იმდენად ეჩვევით ერთმანეთის გაგებას, რომ გარესამყაროსთან კონტაქტი გეზარებათ.",
                "გაგება კარგია, ოღონდ საკუთარი აზრის დათმობას ნუ დაიწყებთ უბრალოდ მშვიდობის შესანარჩუნებლად.",
                "შინაგანი ლექსიკონი გაქვთ, თუმცა გარედან მოსულ სიახლეებსაც ნუ ჩაკეტავთ.",
            ],
            [
                "Articulating complex thoughts feels smooth, safe, and deeply validated",
                "You listen with genuine presence instead of just waiting for your turn to speak",
            ],
            [
                "It feels as though you share a shared private dictionary of nuance.",
                "Collaborative problem-solving happens naturally without defensive posture.",
            ],
        ),
        (
            "relationship.communication.intuitive_listening.v1",
            "relationship",
            [
                "ერთმანეთის საუბარში სიტყვებზე მეტად პაუზებსა და ინტონაციას უსმენთ, რაც ხანდახან ზედმეტ პარანოიას ჰგავს",
                "ზუსტად იცით, როდის უნდა გაჩუმდეთ, მაგრამ ამ სიჩუმეში ხშირად უთქმელი პრეტენზიები გროვდება",
                "ერთმანეთის გრძნობებს ისე უფრთხილდებით, რომ პირდაპირ სიმართლის თქმა გიჭირთ",
            ],
            [
                "ტაქტი და ემპათია დასაფასებელია, ოღონდ პირდაპირობაც რომ ჩართოთ ხოლმე, ცხოვრება გამარტივდება.",
                "ინტონაციების გაშიფვრას შეეშვით და პირდაპირ ჰკითხეთ, რა ხდება.",
                "მოსმენა კარგია, მაგრამ საკუთარი ხმის გაგონებაც აუცილებელია.",
            ],
            [
                "You catch the unspoken feelings vibrating beneath the surface of conversation",
                "Tactful attentiveness ensures neither of you feels dismissed or unheard",
            ],
            [
                "You excel at translating tangled emotions into clear, reassuring clarity.",
                "Listening becomes an act of care rather than a verbal transaction.",
            ],
        ),
        (
            "relationship.communication.sharp_debate.v1",
            "relationship",
            [
                "თქვენი საუბარი ინტელექტუალური ჩხუბია წესების გარეშე — ლოგიკურ შეცდომას არცერთი არ პატიობთ მეორეს",
                "კამათი თქვენთვის წინასწარი შეთანხმებაა იმაზე, რომ არცერთი არ დანებდებით",
                "აზრების ხისტი შეჯახება ორივეს გონებას აღვიძებს, თუმცა ნერვებსაც გვარიანად ცვეთს",
            ],
            [
                "დებატებში გამარჯვება ურთიერთობის გადარჩენას არ ნიშნავს — ეგოს თუ არ მოთოკავთ, მარტო საკუთარ სიმართლესთან დარჩებით.",
                "არგუმენტებით მეორის განადგურება სპორტი კი არა, ურთიერთობის ნელი მკვლელობაა.",
                "მთავარია, დისკუსიის შემდეგ ისევ შეგეძლოთ ერთად ჩაის დალევა.",
            ],
            [
                "Discussions quickly morph into high-speed intellectual fencing matches",
                "You challenge weak logic without mercy, keeping each other on mental toes",
            ],
            [
                "Just keep egos padded so fierce debate does not turn into personal combat.",
                "Mental sharpness is guaranteed; dull conversation cannot survive here.",
            ],
        ),
        (
            "relationship.communication.grounded_deliberation.v1",
            "relationship",
            [
                "თქვენი საუბრები პრაქტიკულ შედეგებზე, ფაქტებსა და რეალობაზეა ორიენტირებული — ილუზიებს შანსი არ აქვს",
                "ცარიელ იდეებს მაშინვე ურტყამთ პრაქტიკულ ლოგიკას და სპონტანურობას ადგილზევე ახრჩობთ",
                "საკითხებს უდგებით ისეთი სერიოზულობით, თითქოს სახელმწიფო ბიუჯეტს ანაწილებდეთ",
            ],
            [
                "საიმედოობა გარანტირებულია, მაგრამ ცოტა იუმორი და სისულელე საუბარს ნამდვილად არ აწყენდა.",
                "მშრალი ლოგიკით ურთიერთობას ვერ გააცოცხლებთ; ემოციებსაც მიეცით სივრცე.",
                "არქიტექტურული სიზუსტით აშენებული დიალოგი კარგია, ოღონდ შიგნით სითბოც უნდა იყოს.",
            ],
            [
                "Conversations center around tangible execution, sober facts, and realistic timelines",
                "You filter grandiose theories through rigorous practical scrutiny",
            ],
            [
                "A touch of levity never hurts, but your structural reliability is airtight.",
                "You construct decisions the way master engineers build suspension bridges.",
            ],
        ),
        (
            "relationship.communication.unconventional_spark.v1",
            "relationship",
            [
                "თქვენი თემები იმდენად უცნაური და არასტანდარტულია, რომ ნებისმიერი მესამე პირი გიჟებად ჩაგთვლით",
                "ჩვეულებრივ ამბებსაც კი ისეთი აბსურდული რაკურსით უყურებთ, რომ სიცილი გარანტირებულია",
                "ყველაზე გიჟურ თეორიებსაც კი სრული სერიოზულობით განიხილავთ და ამით ერთობrecordით",
            ],
            [
                "სტერეოტიპების მსხვრევა სახალისოა, მაგრამ ყოველდღიურ საკითხებზე შეთანხმებაც რომ შეგეძლოთ, ურიგო არ იქნებოდა.",
                "ორიგინალურობა კარგია, თუმცა პრაქტიკული რეალობა ხანდახან ყურადღებას ითხოვს.",
                "სხვები ვერ გიგებენ და არც გაინტერესებთ; მთავარია, ერთმანეთი გართობთ.",
            ],
            [
                "Your conversations bypass typical banalities for quirky, brilliant brainstorms",
                "You explore bizarre hypotheticals with deadpan seriousness and high amusement",
            ],
            [
                "Conventional small talk dies a quick death whenever you two get talking.",
                "Originality is your shared mother tongue, and it keeps you endlessly fascinated.",
            ],
        ),

        # 5. Stability & Notice Dynamics
        (
            "relationship.stability.shared_optimism.v1",
            "relationship",
            [
                "პრობლემებს ისეთი მსუბუქი იუმორით უყურებთ, თითქოს კრიზისი თქვენ კი არა, მეზობელს დაემართა",
                "ერთად ისეთი თავდაჯერებულები ხართ, რომ რეალურ საფრთხეებსაც კი სასაცილოდ იგდებთ",
                "თქვენი ოპტიმიზმი გადამდებია, ოღონდ ხანდახან რეალურ პასუხისმგებლობას გაქცევთ",
            ],
            [
                "ოპტიმიზმი გადამდებია, მაგრამ ვარდისფერი სათვალე რეალურ ორმოებს ვერ ამოავსებს.",
                "სიცილით ყველაფრის გადაფარვა არ გამოვა; ხანდახან პრობლემას თვალი უნდა გაუსწოროთ.",
                "გეგმები გრანდიოზულია, მთავარია, რეალიზაციაზეც არ თქვათ უარი.",
            ],
            [
                "Shared humor and infectious optimism make difficulties shrink in your presence",
                "You expand each other's confidence and laugh off transient bad luck",
            ],
            [
                "Your shared aura acts as an open invitation for serendipity and fresh luck.",
                "Being together makes life feel expansive, generous, and thoroughly promising.",
            ],
        ),
        (
            "relationship.stability.long_term_grounding.v1",
            "relationship",
            [
                "დაპირებებს ისე სერიოზულად ეკიდებით, თითქოს ნოტარიუსთან იყოთ ხელმოწერილი",
                "თქვენს კავშირში სპონტანურობა მინიმალურია, სამაგიეროდ საიმედოობა — ასპროცენტიანი",
                "პასუხისმგებლობა თქვენი მთავარი ღირებულებაა, რაც ურთიერთობას ურყევ ციხესიმაგრედ აქცევს",
            ],
            [
                "ციხესიმაგრე კი ააშენეთ, ოღონდ შიგნით სიცოცხლეც რომ დატოვოთ, კარგი იქნება.",
                "ერთგულება ფასდაუდებელია, მაგრამ რუტინამ არ უნდა მოგკლათ.",
                "საიმედოობა იშვიათია, მთავარია, ურთიერთობა მოვალეობების ჩამონათვალად არ იქცეს.",
            ],
            [
                "Promises are solid commitments here rather than convenient conversational filler",
                "Enduring reliability and mutual accountability anchor the bond across time",
            ],
            [
                "Genuine dependability is a rare luxury today; you two embody it effortlessly.",
                "You construct a fortress of trust that only grows sturdier with each passing year.",
            ],
        ),
        (
            "relationship.stability.generous_comfort.v1",
            "relationship",
            [
                "შეცდომებს ისე მარტივად პატიობთ ერთმანეთს, თითქოს არაფერი მომხდარა — და მერე უკვირთ, რატომ მეორდება იგივე",
                "თქვენს სივრცეში იმდენად მყუდრო კომფორტია, რომ აქტიური ზრდის სურვილი ქრება",
                "ერთმანეთის გახარება წვრილმანებში გსიამოვნებთ, რაც საყვარელი და ცოტა მოსაწყენიცაა",
            ],
            [
                "ეს ემოციური სიუხვე კარგია, ოღონდ საზღვრების დაწესებაც აუცილებელია, რომ ვინმემ თავზე არ დაგაჯდეთ.",
                "კომფორტი სასიამოვნოა, მაგრამ უმოძრაობა ურთიერთობის დაბერებას იწვევს.",
                "პატიება კარგია, მაგრამ დასკვნების გამოტანაც არ დაგავიწყდეთ.",
            ],
            [
                "Forgiveness and emotional generosity erase grievances before they fester",
                "Your shared space is defined by generous comfort and easygoing domestic peace",
            ],
            [
                "Emotional abundance means neither of you ever keeps score of who gave more.",
                "Recharging together feels restorative, natural, and refreshingly uncomplicated.",
            ],
        ),
        (
            "relationship.stability.architectural_anchor.v1",
            "relationship",
            [
                "თქვენი პარტნიორობა ბეტონზეა ნაშენი — არანაირი ილუზია, მხოლოდ მკაცრი პრინციპები",
                "ერთმანეთის ზურგს უმაგრებთ უსიტყვოდ, მაგრამ ემოციურ სითბოს ძუნწად იმეტებთ",
                "ისეთ სტრუქტურას ქმნით, რომელიც ნებისმიერ კრიზისს გაუძლებს, თუმცა ცოტა მკაცრია",
            ],
            [
                "ქვაზე ნაშენი კავშირი კარგია, ოღონდ ცივი კედლები ცოტა გაათბეთ კიდეც.",
                "საქმეები ლაპარაკობს, გასაგებია, მაგრამ თბილი სიტყვაც რომ თქვათ ხანდახან, არ დაგაზარალებთ.",
                "საიმედოობა უმაღლესია, თუმცა სიმსუბუქეც სჭირდება ცხოვრებას.",
            ],
            [
                "Your partnership is constructed on rock-solid principles free of wishful thinking",
                "You guard each other's flanks with unspoken, unwavering fidelity",
            ],
            [
                "This alliance is built on bedrock; storms simply bounce off the exterior.",
                "You do not require dramatic declarations; your actions do all the heavy lifting.",
            ],
        ),
        (
            "relationship.notice.independent_dynamics.v1",
            "relationship",
            [
                "პირად სივრცეს ისეთი ეჭვიანობით იცავთ, თითქოს ერთმანეთისგან თავის დაცვა გჭირდებოდეთ",
                "ავტონომია იმდენად დიდია, რომ ხანდახან ერთმანეთის ცხოვრებაში სტუმრებივით ხართ",
                "თავისუფლება ორივესთვის უპირველესია, ამიტომ ვალდებულებებს შორიდან უყურებთ",
            ],
            [
                "თავისუფლება კარგია, მაგრამ თუ საერთო არაფერი დაგრჩათ, ურთიერთობას რატომღა არქმევთ?",
                "დამოუკიდებლობა არ ნიშნავს იმას, რომ მეორის არსებობა მხოლოდ მაშინ გაგახსენდეთ, როცა მოსახერხებელია.",
                "ორ დამოუკიდებელ სამყაროს შორის ხიდიც უნდა არსებობდეს, მარტო დისტანცია საკმარისი არაა.",
            ],
            [
                "You fiercely respect each other's sovereignty without insecurity or clinginess",
                "The bond thrives on deliberate choice rather than co-dependent attachment",
            ],
            [
                "Freedom does not dilute this connection; it provides the air it needs to breathe.",
                "Two sovereign worlds meeting by conscious choice rather than needy compulsion.",
            ],
        ),

        # 6. Macro Synergy Contracts
        (
            "relationship.overall.exceptional_flow.v1",
            "relationship",
            [
                "ყველაფერი ისე ბუნებრივად და უხარვეზოდ ლაგდება, რომ საეჭვოცაა — ცხოვრება ასეთი მარტივი არასდროსაა",
                "თითქოს ერთი და იმავე ტალღაზე ხართ მომართულები და ხარვეზები საერთოდ არ გაქვთ",
                "თქვენი კავშირი მსუბუქად ვითარდება, რაც ხანდახან ცოტა დრამის სურვილსაც კი აჩენს",
            ],
            [
                "ასეთი სინერგია იშვიათია, ოღონდ ილუზიაში ნუ ჩავარდებით, რომ ეს თავისით გაგრძელდება სამუდამოდ.",
                "როცა ყველაფერი ზედმეტად იდეალურია, პირველივე პატარა გაუგებრობამ იცის დიდი შოკი.",
                "ისიამოვნეთ სიმსუბუქით, მაგრამ ფხიზლად ყოფნაც არ დაგავიწყდეთ.",
            ],
            [
                "Rare, organic alignment runs across multiple dimensions of your connection",
                "You broadcast on the exact same frequency with virtually zero static",
            ],
            [
                "Cadences this smooth are uncommon; savor the ease and keep communicating.",
                "Everything clicks into place without the exhausting uphill push.",
            ],
        ),
        (
            "relationship.overall.balanced_synergy.v1",
            "relationship",
            [
                "გაქვთ საერთო ბაზა, მაგრამ ინდივიდუალურ სივრცესაც კბილებით იცავთ — და სწორედ ეს გინარჩუნებთ ინტერესს",
                "არც ზედმეტად ერწყმით ერთმანეთს და არც ერთმანეთს შორდებით",
                "თქვენი დინამიკა სტაბილურია, თუმცა შიდა დაძაბულობაც ზომიერად ახლავს",
            ],
            [
                "ბალანსი შესანიშნავია, მთავარია, ეს დისტანცია ემოციურ სიცივეში არ გადაიზარდოს.",
                "ოქროს შუალედის დაცვა კარგია, ოღონდ ვნებასაც დაუტოვეთ ადგილი.",
                "ეს ის ჰარმონიაა, რომელიც არ გაგაგიჟებთ, სამაგიეროდ არც მოგბეზრდებათ.",
            ],
            [
                "A resilient balance between shared rhythm and stimulating contrasts anchors you",
                "You share common ground while maintaining distinct individual flavors",
            ],
            [
                "This equilibrium keeps the spark alive without burning the house down.",
                "You have found the sweet spot between predictable comfort and fun novelty.",
            ],
        ),
        (
            "relationship.overall.stimulating_friction.v1",
            "relationship",
            [
                "თქვენი კავშირი მუდმივი პროვოკაციაა — არცერთი არ აძლევთ მეორეს მშვიდად ყოფნის უფლებას",
                "ენერგია კონტრასტებიდან მოდის და ერთფეროვნებას პირველივე წუთს კლავს",
                "მუდმივი გამოწვევა თქვენი ურთიერთობის მთავარი საწვავია",
            ],
            [
                "მუდმივი გამოწვევა მატონიზირებელია, მაგრამ დასვენებაც რომ სჭირდება ადამიანს, ეგეც გაითვალისწინეთ.",
                "კონტრასტი კარგია, სანამ ეს დაპირისპირება დამღლელ ჩვევად არ გადაიქცევა.",
                "მოსაწყენი არასდროს იქნება, თუ ომის ნაცვლად თამაშს აირჩევთ.",
            ],
            [
                "Energy is catalyzed by sharp contrasts and continuous dynamic challenges",
                "You refuse to let each other slide into dull routines or comfortable ruts",
            ],
            [
                "Boring will never be a problem here, provided active listening remains a habit.",
                "Dynamic friction keeps the relationship evolving instead of fossilizing.",
            ],
        ),
        (
            "relationship.overall.independent_paths.v1",
            "relationship",
            [
                "ორი სრულიად დამოუკიდებელი სამყარო ხართ, რომლებიც ერთმანეთს დროდადრო გადაკვეთენ და მერე ისევ საკუთარ ტრაექტორიაზე ბრუნდებიან",
                "მიჯაჭვულობა თქვენთვის უცხოა — ავტონომია ყველაფერზე მაღლა დგას",
                "საერთო ენის პოვნა შეგნებულ ძალისხმევას მოითხოვს, თორემ ისე მარტივად დაიშლებით",
            ],
            [
                "თავისუფლება კარგია, ოღონდ თუ საერთო არაფერი დაგრჩათ, ურთიერთობას რატომღა არქმევთ?",
                "დამოუკიდებლობა არ ნიშნავს იმას, რომ მეორის არსებობა მხოლოდ მაშინ გაგახსენდეთ, როცა მოსახერხებელია.",
                "თუ ხიდის აშენება ორივეს გინდათ, საკუთარი ეგოს შეზღუდვაც მოგიწევთ.",
            ],
            [
                "Two sovereign trajectories meeting by deliberate choice rather than gravitational pull",
                "Building enduring bridges requires conscious intent and patient curiosity",
            ],
            [
                "Nothing is impossible here, but the connection requires conscious cultivation.",
                "You operate as sovereign allies rather than merged identities.",
            ],
        ),
    ]

    for item in rel_defs:
        interp_id, ctx, ka_p, ka_t, en_p, en_t = item
        # Split into tone categories
        w_ka_p = ka_p[:2]
        w_ka_t = ka_t[:2]
        p_ka_p = ka_p[1:]
        p_ka_t = ka_t[1:]
        s_ka_p = [ka_p[0]]
        s_ka_t = [ka_t[1] if len(ka_t) > 1 else ka_t[0]]
        b_ka_p = [ka_p[-1]]
        b_ka_t = [ka_t[-1]]
        sav_ka_p = [ka_p[0]]
        sav_ka_t = [ka_t[0]]
        rom_ka_p = [ka_p[0]] if "attraction" in interp_id or "harmony" in interp_id else []
        rom_ka_t = [ka_t[0]] if "attraction" in interp_id or "harmony" in interp_id else []

        w_en_p = en_p[:2]
        w_en_t = en_t[:2]
        p_en_p = en_p[1:]
        p_en_t = en_t[1:]
        s_en_p = [en_p[0]]
        s_en_t = [en_t[1] if len(en_t) > 1 else en_t[0]]
        b_en_p = [en_p[-1]]
        b_en_t = [en_t[-1]]
        sav_en_p = [en_p[0]]
        sav_en_t = [en_t[0]]
        rom_en_p = [en_p[0]] if "attraction" in interp_id or "harmony" in interp_id else []
        rom_en_t = [en_t[0]] if "attraction" in interp_id or "harmony" in interp_id else []

        contracts.append(
            ContractSeedData(
                interpretation_id=interp_id,
                context=ctx,
                ka_witty_premises=ka_p,
                ka_witty_twists=ka_t,
                ka_playful_premises=p_ka_p,
                ka_playful_twists=p_ka_t,
                ka_soft_premises=s_ka_p,
                ka_soft_twists=s_ka_t,
                ka_bold_premises=b_ka_p,
                ka_bold_twists=b_ka_t,
                ka_savage_premises=sav_ka_p,
                ka_savage_twists=sav_ka_t,
                ka_romantic_premises=rom_ka_p,
                ka_romantic_twists=rom_ka_t,
                en_witty_premises=en_p,
                en_witty_twists=en_t,
                en_playful_premises=p_en_p,
                en_playful_twists=p_en_t,
                en_soft_premises=s_en_p,
                en_soft_twists=s_en_t,
                en_bold_premises=b_en_p,
                en_bold_twists=b_en_t,
                en_savage_premises=sav_en_p,
                en_savage_twists=sav_en_t,
                en_romantic_premises=rom_en_p,
                en_romantic_twists=rom_en_t,
            )
        )

    return contracts
