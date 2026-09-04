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
                "თქვენს შორის მიზიდულობა პირველივე წამიდან იგრძნობა და ზედმეტ ახსნას არ საჭიროებს",
                "ოთახში ერთად ყოფნისას ჰაერში აუხსნელი მაგნიტური დაძაბულობა ჩნდება",
                "ერთმანეთის მზერა ისე გიჭერთ, რომ გარშემო ხმაური ქრება",
                "თქვენი ქიმია იმდენად სპონტანურია, რომ გეგმებს აზრს უკარგავს",
            ],
            [
                "ნაპერწკლები ისე მარტივად ჩნდება, რომ ცეცხლმაქრი სად დევს, წინასწარ უნდა იცოდეთ.",
                "მიზიდულობა აშკარაა, თუმცა სიტყვები აქ მხოლოდ ფონია.",
                "მთავარია, ამ მუხტმა ყოველდღიური რუტინა არ დაგავიწყოთ.",
                "თქვენ ორს შორის ტემპერატურა ყოველთვის რამდენიმე გრადუსით მაღალია.",
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
                "თქვენს შორის მიზიდულობა პირველივე წამიდან იგრძნობა და ზედმეტ ახსნას არ საჭიროებს",
                "ოთახში ერთად ყოფნისას ჰაერში აუხსნელი მაგნიტური დაძაბულობა ჩნდება",
            ],
            [
                "ნაპერწკლები ისე მარტივად ჩნდება, რომ ცეცხლმაქრი სად დევს, წინასწარ უნდა იცოდეთ.",
                "მიზიდულობა აშკარაა, თუმცა სიტყვები აქ მხოლოდ ფონია.",
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
                "თქვენი მიზიდულობა მოულოდნელი და ელვისებურია",
                "ერთმანეთს ისე იზიდავთ, როგორც საპირისპირო პოლუსები",
                "თქვენს შეხვედრას ყოველთვის ახლავს გარკვეული თავბრუდამხვევი აზარტი",
            ],
            [
                "ლოგიკა აქ უძლურია; საქმე ინსტინქტურ მიზიდულობას ეხება.",
                "ერთად ყოფნისას სიმშვიდეს ნამდვილად ვერ იპოვით, სამაგიეროდ მოსაწყენი არასდროს იქნება.",
                "ეს ის კავშირია, სადაც ნაპერწკალი წამში გიგანტურ ცეცხლად იქცევა.",
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
                "თქვენს ურთიერთობაში ბუნებრივი სინაზე და ესთეტიკური სითბო იგრძნობა",
                "ერთმანეთის კომპანიაში ყოფნა მყუდრო შემოდგომის საღამოს ჰგავს",
                "თქვენს შორის მოწონება მარტივი, გულწრფელი და სასიამოვნოა",
            ],
            [
                "ეს ის სითბოა, ცივ დღეს ცხელი ჩაი რომ მოგიტანონ და შეგაფარონ.",
                "ერთმანეთის გალამაზება და გახარება თქვენთვის ბუნებრივი ჟესტია.",
                "თქვენი სიახლოვე სიმშვიდითა და ბუნებრივი მომხიბვლელობით სუნთქავს.",
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
                "როცა ერთად რაღაცის შექმნას იწყებთ, თქვენი ენერგია ორმაგდება",
                "თქვენი თანამშრომლობა სპორტულ აზარტსა და შემოქმედებით მუხტს აერთიანებს",
                "იდეიდან მოქმედებამდე მანძილი თქვენ ორს შორის მინიმალურია",
            ],
            [
                "ერთობლივი პროექტები თქვენთან ქარიშხალივით სწრაფად და შედეგიანად მიდის.",
                "თქვენ არ ზიხართ და ელით; თქვენ ერთად ქმნით საკუთარ ტალღას.",
                "მოტივაცია თქვენთან გადამდებია და სხვებსაც მოქმედებისკენ უბიძგებს.",
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
                "თქვენ ორს ერთად მოქმედება გიყვართ და უსაქმოდ ჯდომას ვერ იტანთ",
                "თქვენი შეხვედრა ყოველთვის ახალი ინიციატივებისა და გეგმების დასაწყისია",
                "თქვენ შორის მუხტი პირდაპირ მოქმედებასა და სიჩქარეზეა ორიენტირებული",
            ],
            [
                "თქვენთან საქმე ყოველთვის ჩქარ ტემპში წყდება; ლოდინი თქვენთვის უცხოა.",
                "მთავარია, გზაში ერთმანეთს არ გადააჯირითოთ — ენერგია ორივეს თავზე საყრელად გაქვთ.",
                "თქვენი დინამიკა ცეცხლოვანია და მუდმივ მოძრაობაში იმყოფება.",
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
                "თქვენს შორის მიზიდულობა იმდენად ღრმაა, რომ ფსიქოლოგიურ დონემდე აღწევს",
                "ზედაპირული ფლირტი აქ არ იმუშავებს; თქვენ ერთმანეთის სიღრმეებს ეხებით",
                "ერთმანეთის მზერაში რაღაც საბედისწერო და გარდაუვალი იკითხება",
            ],
            [
                "ეს ის მიზიდულობაა, რომელიც ადამიანს ძირფესვიანად ცვლის და აფხიზლებს.",
                "თქვენს შორის საიდუმლოებები დიდხანს ვერ გაძლებს; ინტუიცია ყველაფერს ხსნის.",
                "ინტენსივობა აქ მაღალია, ამიტომ ემოციური უსაფრთხოება განსაკუთრებულ ფასს იძენს.",
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
                "თქვენს შორის ნაპერწკალი ხშირად კონკურენციიდან და ჯიბრიდან იბადება",
                "ორი ძლიერი ნებისყოფა ერთ სივრცეში მუდმივად ამოწმებს ერთმანეთის გამძლეობას",
                "თქვენი მიზიდულობა ცეცხლოვანია, თუმცა ხანდახან ბრძოლის ველს ემსგავსება",
            ],
            [
                "სანამ კამათობთ, მიზიდულობა იზრდება; მთავარია, გამარჯვებული ვახშამზე პატიჟებდეს.",
                "თქვენთან მოსაწყენი სიმშვიდე არასდროს იქნება, ენერგია ყოველთვის პიკზეა.",
                "ეს ის შემთხვევაა, როცა წინააღმდეგობა ურთიერთობას უფრო მადისაღმძვრელს ხდის.",
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
                "თქვენი მიზიდულობა წესებსა და ჩვეულებრივ ლოგიკას საერთოდ არ ემორჩილება",
                "ერთმანეთში გაოცებთ ის უცნაურობები, რასაც სხვები ვერც კი ამჩნევენ",
                "თქვენს შორის კავშირი მოულოდნელ სიურპრიზებსა და ელექტროულ იმპულსებს ეფუძნება",
            ],
            [
                "ვერავინ იწინასწარმეტყველებს, რა მოხდება ხვალ; სწორედ ეს გიზიდავთ ყველაზე მეტად.",
                "ერთფეროვნება ამ ურთიერთობაში პირველივე წამს კვდება.",
                "თქვენ არღვევთ სტანდარტებს და ამით საოცარ თავისუფლებას პოულობთ.",
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
                "თქვენი ემოციური და ფიზიკური რეაქცია ერთმანეთზე წამიერია",
                "გრძნობები აქ სწრაფად იფეთქებს და პირდაპირ ქმედებაში გადადის",
                "ერთმანეთის სიახლოვეში პულსი გიჩქარდებათ და სიფრთხილე გავიწყდებათ",
            ],
            [
                "ინსტინქტი აქ გონებას უსწრებს; თქვენ შორის მუხტი ძალზე პირველყოფილია.",
                "ემოციური ტემპერატურა ხშირად იცვლება, სამაგიეროდ ყოველთვის ცოცხალია.",
                "თქვენთან საუბარიც კი ხშირად ფარულ ვნებასა და აზარტს შეიცავს.",
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
                "თქვენს რომანტიკულ გემოვნებაში საოცარი თანხვედრა და ელეგანტურობაა",
                "ერთმანეთის კომპლიმენტებით ავსება და ლამაზი მომენტების შექმნა გსიამოვნებთ",
                "თქვენი მიზიდულობა დახვეწილ დეტალებსა და საერთო ესთეტიკაზე დგას",
            ],
            [
                "თქვენ ერთად ყოფნისას სამყარო უფრო ჰარმონიული და გემოვნებიანი ჩანს.",
                "სოციალურ გარემოში თქვენი წყვილი ბუნებრივ აღფრთოვანებას იწვევს.",
                "თქვენ იცით, როგორ აქციოთ უბრალო შეხვედრაც კი დღესასწაულად.",
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
                "ერთმანეთის ვიზუალური ხიბლი და მანერები პირველივე მზერით გატყვევებთ",
                "თქვენს შორის მიზიდულობა იმდენად ცხადია, რომ გარშემომყოფებიც კი ამჩნევენ",
                "ერთად დგომისას თითქოს ორივეს მომხიბვლელობა ორმაგდება",
            ],
            [
                "თქვენ იზიდავთ ერთმანეთს ისეთი ბუნებრიობით, რომ წინააღმდეგობა უაზროა.",
                "ეს ის კავშირია, სადაც გარეგნული მიმზიდველობა შინაგან სიმპათიას ერწყმის.",
                "ერთმანეთისთვის საუკეთესო სარკე ხართ, რომელიც მხოლოდ მშვენიერებას ირეკლავს.",
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
                "თქვენს შორის კონტაქტი პირდაპირი, გაბედული და უყოყმანოა",
                "ერთმანეთს მოქმედებისკენ და თამამი ნაბიჯებისკენ ბუნებრივად უბიძგებთ",
                "თქვენს შეხვედრას თან ახლავს ენერგიული მუხტი, რომელიც გაჩერების საშუალებას არ გაძლევთ",
            ],
            [
                "თქვენთან საქმე ყოველთვის თამამ გადაწყვეტილებებს მოითხოვს.",
                "თქვენ არ გეშინიათ გარისკვის, როცა ერთად ხართ.",
                "ეს არის დინამიკა, სადაც თითოეული ნაბიჯი ახალ თავგადასავალს იწყებს.",
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
                "ერთმანეთის განწყობასა და ემოციურ მდგომარეობას უსიტყვოდ გრძნობთ",
                "თქვენს შორის არის იშვიათი გაგება, სადაც თავის გამართლება არ გჭირდებათ",
                "ერთად ყოფნისას შინაგანი სიმშვიდე და უსაფრთხოების განცდა ჩნდება",
            ],
            [
                "უსიტყვოდ გაგება კარგია, ოღონდ ხანდახან ხმამაღლა ლაპარაკიც არ დაგავიწყდეთ.",
                "თქვენი ემოციური ტალღები ერთმანეთს საოცარი ბუნებრიობით ერწყმის.",
                "აქ მიღება ბუნებრივია, რაც დღევანდელ სამყაროში იშვიათი ფუფუნებაა.",
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
                "ცხოვრების მთავარ საკითხებში ერთ ტალღაზე ხართ და ერთნაირად ფიქრობთ",
                "თქვენი ფასეულობები და მიზნები ისე ემთხვევა, თითქოს ერთი გეგმა გქონდეთ",
                "ერთად ყოფნა ძალდატანების გარეშე მიმდინარეობს, როგორც ბუნებრივი დინება",
            ],
            [
                "თითქოს ერთი და იგივე წესების წიგნი გაქვთ წაკითხული ბავშვობაში.",
                "ძირითად პრინციპებზე კამათი არ გჭირდებათ; საძირკველი უკვე მყარია.",
                "ეს ის ჰარმონიაა, რომელიც წლებს უძლებს და დროთა განმავლობაში მხოლოდ ძლიერდება.",
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
                "ერთმანეთის განწყობას წამებში ამჩნევთ და მზრუნველობას არ იშურებთ",
                "თქვენს ურთიერთობაში სიმყუდროვე და ნაზი მზრუნველობა სუფევს",
                "ერთმანეთის დამშვიდება ისე შეგიძლიათ, როგორც არავის სხვას",
            ],
            [
                "მთავარია, სხვისი დარდი საკუთარ პასუხისმგებლობად არ აქციოთ.",
                "თქვენი სიახლოვე საუკეთესო თავშესაფარია გადაღლილი დღის შემდეგ.",
                "სინაზე თქვენთან სისუსტე კი არა, უდიდესი გამაერთიანებელი ძალაა.",
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
                "ერთმანეთის გახარება გსიამოვნებთ და კომპლიმენტებსაც არ იშურებთ",
                "თქვენს შორის არის გულუხვი მხარდაჭერა, სადაც შური და მეტოქეობა გამორიცხულია",
                "ერთად ყოფნისას ცხოვრება უფრო ნათელი და შესაძლებლობებით სავსე ჩანს",
            ],
            [
                "ასეთ გარემოში ადამიანური ზრდა და განვითარება საოცრად მარტივია.",
                "თქვენი ურთიერთობა სავსეა ოპტიმიზმით, სიცილითა და გულწრფელი სითბოთი.",
                "თქვენ აფართოებთ ერთმანეთის სამყაროს და კარგ განწყობას უშურველად გასცემთ.",
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
                "თქვენი ემოციური რიტმები იმდენად სინქრონულია, რომ სიტყვები მეორეხარისხოვანი ხდება",
                "ერთმანეთის ტკივილსა და სიხარულს ისე განიცდით, თითქოს საკუთარი იყოს",
                "თქვენს შორის არის უსაფრთხო სივრცე, სადაც ნებისმიერი ემოციის გამოხატვა მოსულა",
            ],
            [
                "ეს არის იშვიათი ემოციური თანხვედრა, რომელიც სრულ თავისუფლებას გაძლევთ.",
                "თქვენ არ გჭირდებათ თავის მოჩვენება; აქ ნამდვილი სახით ყოფნა დაფასებულია.",
                "ეს ის კავშირია, რომელიც ყველაზე მძიმე ქარიშხალსაც კი მშვიდად გადაიტანს.",
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
                "თქვენს შორის არის პოეტური და ინტუიციური კავშირი, რომელიც ლოგიკას სცდება",
                "ერთმანეთის უთქმელ გრძნობებს ისე აღიქვამთ, როგორც წყალი ირეკლავს სინათლეს",
                "თქვენს ურთიერთობაში არის საოცარი სინაზე და მიმტევებლობა",
            ],
            [
                "მთავარია, ილუზიებში არ დაიკარგოთ და რეალობასთან კავშირი შეინარჩუნოთ.",
                "ეს ის სიახლოვეა, რომელიც სულს ამშვიდებს და შინაგან ჰარმონიას ანიჭებს.",
                "თქვენ გრძნობთ ერთმანეთს მანძილზეც კი, თითქოს უხილავი ძაფით იყოთ შეკრულნი.",
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
                "თქვენი სიახლოვე იმდენად ღრმაა, რომ შიშველ ემოციურ სიმართლეს ეხება",
                "ერთმანეთს ეხმარებით შინაგანი კომპლექსებისა და შიშების დაძლევაში",
                "თქვენს შორის ნდობა ადვილად არ მოდის, მაგრამ მოპოვების შემდეგ ურყევია",
            ],
            [
                "ეს კავშირი ორივეს გაიძულებთ გაიზარდოთ და ძველი შეზღუდვები მოიშოროთ.",
                "თქვენ არ გეშინიათ რთული თემების; პირიქით, სწორედ იქ პოულობთ ნამდვილ არსს.",
                "ეს არის ძლიერი ფსიქოლოგიური ალიანსი, რომელსაც ვერაფერი გატეხავს.",
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
                "სრულიად განსხვავებული კუთხიდან უყურებთ სამყაროს და ეს საინტერესოა",
                "თქვენი განსხვავებები ერთმანეთის ნაკლოვანებებს ბუნებრივად ავსებს",
                "ერთად ყოფნისას ხედავთ იმას, რაც მარტო ყოფნისას გამოგეპარებოდათ",
            ],
            [
                "საინტერესოა მანამ, სანამ გადაწყვეტთ, ვინ მართავს მანქანას.",
                "კონტრასტი თქვენი საუკეთესო მასწავლებელია, თუ ერთმანეთის მოსმენას შეძლებთ.",
                "თქვენ ორი სხვადასხვა პოლუსი ხართ, რომლებიც ერთ მთლიანობას ქმნიან.",
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
                "ემოციური ტემპერატურა თქვენთან ხშირად და მოულოდნელად იცვლება",
                "განცდების გამოხატვის განსხვავებული სტილი ხანდახან გაუგებრობას ქმნის",
                "თქვენი ურთიერთობა დინამიურია და მუდმივ ყურადღებას მოითხოვს",
            ],
            [
                "მოსაწყენად ნამდვილად არ გეცლებათ, მთავარია დრამა კომედიაში არ აგერიოთ.",
                "თუ ისწავლით ერთმანეთის რიტმის პატივისცემას, ეს დაძაბულობა შემოქმედებად იქცევა.",
                "ეს ის შემთხვევაა, როცა განსხვავებული ხასიათები ერთმანეთს აფხიზლებს.",
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
                "ორივე სარკის სხვადასხვა მხარეს დგახართ და მსგავსებას ხედავთ, მაგრამ კუთხე მაინც განსხვავებულია",
                "თქვენი დისკუსიები ხშირად ფილოსოფიურ დაპირისპირებად იქცევა ხოლმე",
                "ერთმანეთის სისუსტეებს ისე მკაფიოდ ამჩნევთ, როგორც საკუთარ ხელისგულს",
            ],
            [
                "კამათი აქ ინტელექტუალური თამაშია, თუ პირადი ამბიციები განზე დარჩება.",
                "თქვენ აიძულებთ ერთმანეთს საკუთარ შეხედულებებს ახლებურად შეხედოთ.",
                "ეს არის პარტნიორობა, სადაც ყოველთვის არის რაღაც ახალი სასწავლი.",
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
                "ორ ლიდერს ერთ ოთახში ხანდახან სივრცე და ყურადღება არ ჰყოფნის",
                "თქვენი ნებისყოფა იმდენად ძლიერია, რომ დათმობაზე წასვლა თავმოყვარეობის საკითხი ხდება",
                "ყოველთვის ცდილობთ დაამტკიცოთ, ვისი გზა უფრო სწორი და ეფექტურია",
            ],
            [
                "კომპრომისი აქ სისუსტე კი არა, სტრატეგიული გამარჯვებაა.",
                "თუ ძალებს გააერთიანებთ და არა ერთმანეთის წინააღმდეგ მიმართავთ, მთებს გადადგამთ.",
                "მთავარია, გვირგვინი რიგრიგობით მოირგოთ ხოლმე.",
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
                "ერთს აჩქარება და სწრაფი შედეგი უნდა, მეორეს — ყველაფრის დაფიქრება და გადამოწმება",
                "ტემპების შეუთავსებლობა ხანდახან მოთმინების დაკარგვის მიზეზი ხდება",
                "თქვენი ხედვა დროსთან მიმართებაში საგრძნობლად განსხვავებულია",
            ],
            [
                "თუ ტემპზე შეთანხმდებით, თქვენი ნაბიჯები დაუძლეველი გახდება.",
                "სიჩქარე და სიფრთხილე ერთად იდეალური ფორმულაა, თუ ერთმანეთს არ ებრძვით.",
                "მოთმინება აქ ის უნარია, რომლის სწავლაც ორივეს მოგიწევთ.",
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
                "ყოველთვის მოიძებნება თემა, რაზეც კამათი აზარტში და სპორტულ ინტერესში გადავა",
                "თქვენი საუბრები ხშირად ნაპერწკლებს ყრის და ენერგიას აღვიძებს",
                "თქვენ არ აძლევთ ერთმანეთს მოდუნებისა და ჩვეულებრივ რუტინაში ჩარჩენის უფლებას",
            ],
            [
                "მთავარია, კამათის შემდეგ ვახშამი მეგობრულად გაიყოთ.",
                "ეს ნაპერწკალი ურთიერთობას მუდმივად ცოცხალს და აქტიურს ტოვებს.",
                "თქვენი დიალოგი ყოველთვის გამოწვევაა, რომელსაც სიამოვნებით იღებთ.",
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
                "სტრესის დროს ერთი სიჩუმეში იკეტება, მეორეს კი დაუყოვნებლივი განხილვა სჭირდება",
                "ემოციური გადატვირთვის მეთოდები თქვენ ორს სრულიად განსხვავებული გაქვთ",
                "ხანდახან გგონიათ, რომ სხვადასხვა ემოციურ ენაზე ლაპარაკობთ",
            ],
            [
                "ერთმანეთის ენის სწავლა აქ ყველაზე დიდი და საინტერესო გამოწვევაა.",
                "სივრცის მიცემა არ ნიშნავს გულგრილობას; ეს უბრალოდ პატივისცემაა.",
                "განსხვავებული ემოციური რიტმი გაიძულებთ უფრო ყურადღებიანი გახდეთ.",
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
                "როცა საქმე პრინციპებს ეხება, არცერთი თქვენგანი უკან დახევას არ აპირებს",
                "თქვენს შორის არის ძალთა დაპირისპირება, სადაც კონტროლის დათმობა ჭირს",
                "ეს არის ნებისყოფის ნამდვილი გამოცდა ორი უკომპრომისო ადამიანისთვის",
            ],
            [
                "გამარჯვებული აქ არ იქნება; ან ორივე იმარჯვებს პარტნიორობით, ან ორივე აგებს.",
                "თუ ამ ენერგიას საერთო მიზნისკენ მიმართავთ, ნებისმიერ დაბრკოლებას გაანადგურებთ.",
                "საზღვრების პატივისცემა აქ გადარჩენის მთავარი პირობაა.",
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
                "თქვენს კავშირში ილუზიებს ადგილი არ აქვს; რეალობა თავისი წესებით შემოდის",
                "ერთმანეთის მიმართ პასუხისმგებლობა და სიფრთხილე ხშირად აჭარბებს სპონტანურობას",
                "ემოციების გამოხატვა აქ დროითა და საქმით დასტურდება და არა ლამაზი სიტყვებით",
            ],
            [
                "ეს ის კავშირია, სადაც ფასეულობა წლობით იზრდება, თუნდაც დასაწყისი ცივი ჩანდეს.",
                "რომანტიკა აქ საიმედოობაშია და არა ცარიელ ჟესტებში.",
                "სიმწიფე და მოთმინება თქვენს ურთიერთობას ურყევ ციხესიმაგრედ აქცევს.",
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
                "ერთი თქვენგანი გაზის პედალს აწვება, მეორე კი მუხრუჭს ამოწმებს",
                "მოქმედების დაწყებამდე წინააღმდეგობის გადალახვა თქვენთვის ჩვეულებრივი ამბავია",
                "ერთმანეთის იდეებს მკაცრად ფილტრავთ, სანამ რეალიზაციაზე გადახვალთ",
            ],
            [
                "ეს ფილტრი საუკეთესო შედეგს იძლევა: მხოლოდ ნამდვილად გამძლე გეგმები ცოცხლობს.",
                "ნუ აღიქვამთ სიფრთხილეს მტრობად; ეს უბრალოდ ხარისხის კონტროლია.",
                "თქვენ აბალანსებთ ერთმანეთის რისკებს და შედეგი ყოველთვის მყარია.",
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
                "ერთად ყოფნისას თქვენი მიზნები გრანდიოზული ხდება და ჩარჩოებს სცდება",
                "ერთმანეთს უბიძგებთ უფრო ფართოდ იფიქროთ და წვრილმანებს არ დასჯერდეთ",
                "თქვენი ენთუზიაზმი ხშირად რეალობის საზღვრებს აფართოებს",
            ],
            [
                "მთავარია, გეგმების მასშტაბში კონკრეტული ნაბიჯები არ დაგავიწყდეთ.",
                "ოპტიმიზმი თქვენთან გადამდებია და ახალ შესაძლებლობებს იზიდავს.",
                "თქვენ ერთად იზრდებით და სამყაროს საკუთარი წესებით იპყრობთ.",
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
                "თქვენი დიალოგი პინგ-პონგის ფინალს ჰგავს — აზრები ელვის სისწრაფით იცვლება",
                "საერთო იუმორი და ირონია თქვენი საუბრის მთავარი სანელებელია",
                "თქვენთან სიჩუმეც კი აზრიანია, მაგრამ ლაპარაკი — ნამდვილი სიამოვნება",
            ],
            [
                "აზრები ისე სწრაფად იცვლება, რომ მაყურებელს თავბრუ დაეხვევა.",
                "თქვენ არ გჭირდებათ გრძელი შესავლები; ნახევარ სიტყვაში გესმით ერთმანეთის.",
                "ინტელექტუალური თავსებადობა აქ უმაღლეს დონეზეა.",
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
                "აზრების გაზიარება აქ ძალდატანების გარეშე ხდება, ყოველგვარი დაძაბულობის გარეშე",
                "ერთმანეთის მოსმენა და გაგება თქვენთვის ბუნებრივი მოცემულობაა",
                "რთულ საკითხებზეც კი მშვიდად და კონსტრუქციულად მსჯელობთ",
            ],
            [
                "თითქოს საერთო შიდა ლექსიკონი გაქვთ, სადაც გაუგებრობები იშვიათია.",
                "თქვენთან საუბარი ამშვიდებს და გადაწყვეტილების მიღებას ამარტივებს.",
                "ურთიერთპატივისცემა დიალოგში თქვენი მთავარი საყრდენია.",
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
                "ერთმანეთის საუბარში არა მხოლოდ სიტყვებს, არამედ მათ მიღმა არსებულ ემოციასაც იჭერთ",
                "თქვენ იცით, როდის უნდა შეაჩეროთ საუბარი და უბრალოდ მოუსმინოთ",
                "თქვენი დიალოგი ტაქტიანია და ერთმანეთის გრძნობებს სათუთად უფრთხილდება",
            ],
            [
                "ეს ის იშვიათი კომუნიკაციაა, სადაც ადამიანი თავს ნამდვილად გაგებულად გრძნობს.",
                "თქვენ ეხმარებით ერთმანეთს ემოციების მკაფიო სიტყვებად ჩამოყალიბებაში.",
                "ტაქტი და სითბო თქვენს საუბარს განსაკუთრებულ ფასს სძენს.",
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
                "თქვენი საუბრები ხშირად ინტელექტუალურ დუელს ემსგავსება, სადაც არგუმენტები ხმლებს ჰგავს",
                "აზრების პირდაპირი და ხისტი შეჯახება თქვენს გონებას აღვიძებს",
                "ერთმანეთს არ ინდობთ ლოგიკურ შეცდომებში, რაც დიალოგს აზარტულს ხდის",
            ],
            [
                "მთავარია, დებატები პირად შეურაცხყოფაში არ გადავიდეს; აზარტი ისედაც დიდია.",
                "მოსაწყენი დიალოგები თქვენთან გამორიცხულია; ტემპი ყოველთვის მაღალია.",
                "თქვენ ამახვილებთ ერთმანეთის აზროვნებას ისე, როგორც არავინ სხვა.",
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
                "თქვენი საუბრები პრაქტიკულ შედეგებზე, ფაქტებსა და რეალობაზეა ორიენტირებული",
                "ცარიელ იდეებს ყოველთვის კონკრეტული ანალიზი და გეგმა გირჩევნიათ",
                "საკითხებს უდგებით სერიოზულად, აუჩქარებლად და საფუძვლიანად",
            ],
            [
                "თქვენთან მიღებული გადაწყვეტილებები ყოველთვის მყარი და დაცულია.",
                "ხანდახან მეტი სიმსუბუქეც არ გაწყენდათ, თუმცა საიმედოობა გარანტირებულია.",
                "თქვენ აშენებთ საუბარს ისე, როგორც არქიტექტორი აშენებს ხიდს.",
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
                "თქვენი თემები ყოველთვის უცნაური, არასტანდარტული და მოულოდნელია",
                "ჩვეულებრივ ამბებსაც კი ისეთი რაკურსით უყურებთ, რომ სიცილი გარანტირებულია",
                "ერთმანეთის ყველაზე გიჟურ იდეებსაც კი სრული სერიოზულობით განიხილავთ",
            ],
            [
                "თქვენთან საუბარი სტერეოტიპების მსხვრევის საუკეთესო მაგალითია.",
                "ორიგინალურობა თქვენი საერთო ენაა, რომელსაც სხვები ხშირად ვერ იგებენ.",
                "თქვენთან ერთად ყოფნისას გონება ახალ განზომილებაში გადადის.",
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
                "ერთად ყოფნისას პრობლემები პატარავდება, ხოლო გეგმები გრანდიოზული ხდება",
                "თქვენს ურთიერთობაში არის გადამდები ოპტიმიზმი და ერთმანეთის უპირობო რწმენა",
                "იუმორი და გულუხვობა ნებისმიერ დაძაბულობას მარტივად ხსნის",
            ],
            [
                "თქვენი ერთობლივი ენერგია იზიდავს იღბალს და ახალ კარებს აღებს.",
                "ცხოვრება თქვენთან ერთად მხიარული და იმედით სავსე მოგზაურობაა.",
                "თქვენ აძლევთ ერთმანეთს ფრთებს, რათა უფრო მაღლა იფრინოთ.",
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
                "ეს ის კავშირია, სადაც დაპირება ცარიელი სიტყვა არასდროს არის",
                "თქვენი საიმედოობა და ერთმანეთისადმი ერთგულება წლებს უძლებს",
                "პასუხისმგებლობა და ურთიერთპატივისცემა აქ საძირკველშივე დევს",
            ],
            [
                "საიმედოობა დღეს იშვიათი ფუფუნებაა, თქვენ კი მას ბუნებრივად ფლობთ.",
                "თქვენ აშენებთ ისეთ კავშირს, რომელსაც დრო მხოლოდ სიმტკიცეს მატებს.",
                "ეს არის ნამდვილი ზურგი და საყრდენი ნებისმიერ ცხოვრებისეულ სიტუაციაში.",
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
                "ერთმანეთის შეცდომებს მარტივად პატიობთ და გულში წყენას არ იტოვებთ",
                "თქვენს სივრცეში სითბო, სიმშვიდე და გულწრფელი კეთილგანწყობა სუფევს",
                "ერთმანეთის გახარება უბრალო, ყოველდღიურ წვრილმანებში გსიამოვნებთ",
            ],
            [
                "ეს არის ემოციური სიუხვე, სადაც არავინ ითვლის ვინ მეტი გასცა.",
                "თქვენთან დასვენება და ენერგიის აღდგენა საოცრად მარტივია.",
                "სიკეთე თქვენს ურთიერთობაში მთავარი კანონია.",
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
                "თქვენი პარტნიორობა მყარ, გამოცდილ პრინციპებზე დგას და ილუზიებს არ ეფუძნება",
                "ერთმანეთის ზურგს უმაგრებთ ისე, რომ ზედმეტი სიტყვები საჭირო არ არის",
                "თქვენ ერთად ქმნით ცხოვრების ისეთ სტრუქტურას, რომელიც ნებისმიერ კრიზისს გაუძლებს",
            ],
            [
                "ეს არის ქვაზე ნაშენი კავშირი, რომელსაც ქარიშხალი ვერაფერს დააკლებს.",
                "თქვენ არ გჭირდებათ ხმაურიანი დეკლარაციები; თქვენი საქმეები თავად ლაპარაკობს.",
                "საიმედოობა თქვენი ყველაზე ძლიერი იარაღია.",
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
                "ერთმანეთის პირად სივრცესა და ავტონომიას ბუნებრივად უფრთხილდებით",
                "თქვენ არ ზღუდავთ ერთმანეთის თავისუფლებას და არ ცდილობთ მეორის შეცვლას",
                "თქვენი ურთიერთობა შეგნებულ არჩევანზე დგას და არა ერთმანეთზე მიჯაჭვულობაზე",
            ],
            [
                "თავისუფლება აქ კავშირს კი არ ასუსტებს, არამედ აძლიერებს.",
                "თქვენ ორი დამოუკიდებელი სამყარო ხართ, რომლებმაც ერთად ყოფნა აირჩიეს.",
                "სიმწიფე სწორედ იმაშია, რომ არ დაკარგოთ საკუთარი თავი ურთიერთობაში.",
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
                "თქვენს შორის არის იშვიათი ჰარმონია და ორგანული თანხვედრა ყველა დონეზე",
                "თითქოს ერთი და იმავე ტალღაზე მაუწყებლობთ, ყოველგვარი ხარვეზების გარეშე",
                "თქვენი კავშირი მსუბუქად და ძალდაუტანებლად ვითარდება",
            ],
            [
                "ასეთი სინერგია იშვიათად გვხვდება; გაუფრთხილდით და ისიამოვნეთ.",
                "თქვენ ავსებთ ერთმანეთს ისე, თითქოს ყოველთვის ერთად უნდა ყოფილიყავით.",
                "აქ ყველაფერი თავისთავად ლაგდება, ზედმეტი დრამის გარეშე.",
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
                "თქვენს შორის არის ჯანსაღი ბალანსი მსგავსებასა და საინტერესო განსხვავებებს შორის",
                "თქვენ არ ერწყმით ერთმანეთს ბოლომდე, სამაგიეროდ ინარჩუნებთ საკუთარ ხიბლს",
                "თქვენი დინამიკა სტაბილურია და ამავდროულად ცოცხალი",
            ],
            [
                "ზუსტად ეს ბალანსი ტოვებს ურთიერთობას ცოცხალს და მიმზიდველს წლების მანძილზე.",
                "თქვენ გაქვთ საერთო საფუძველი და ამავე დროს სივრცე ინდივიდუალიზმისთვის.",
                "ეს არის ჰარმონია, რომელიც არასდროს ხდება მოსაწყენი.",
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
                "თქვენს კავშირში ენერგია კონტრასტებიდან და მუდმივი გამოწვევიდან იბადება",
                "ერთმანეთს არ აძლევთ მოდუნების საშუალებას; აქ ყოველთვის რაღაც ხდება",
                "თქვენი განსხვავებები ზრდის მთავარი კატალიზატორია",
            ],
            [
                "მოსაწყენი არასდროს იქნება, თუ ერთმანეთის მოსმენას და პატივისცემას ისწავლით.",
                "ეს ურთიერთობა გაიძულებთ მუდმივად ფორმაში იყოთ და განვითარდეთ.",
                "კონტრასტი აქ სიძლიერეა, თუ მას სწორად გამოიყენებთ.",
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
                "თქვენ ხართ ორი სრულიად დამოუკიდებელი სამყარო საკუთარი ტრაექტორიით",
                "საერთო ენის პოვნა შეგნებულ ძალისხმევასა და მოთმინებას მოითხოვს",
                "ავტონომია აქ უფრო დიდია, ვიდრე ემოციური მიჯაჭვულობა",
            ],
            [
                "შეუძლებელი არაფერია, თუ ორივეს ნამდვილად გინდათ ხიდების აშენება.",
                "თქვენი კავშირი შეგნებულ არჩევანზე დგას და არა ავტომატურ მიზიდულობაზე.",
                "ერთმანეთის განსხვავებულობის პატივისცემა აქ მთავარი გასაღებია.",
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
