"""
Seed data builder for 12 Daily Energy transit archetype semantic interpretation contracts.
Prepared for future transit calculation engine.
Zero astrology jargon; strictly focused on personal daily focus, drive,
mental articulation, social bandwidth, and Jester observations.
"""
from scripts.corpus_builders.common import ContractSeedData


def get_daily_energy_contracts_data() -> list[ContractSeedData]:
    contracts: list[ContractSeedData] = []

    daily_defs = [
        (
            "daily_energy.confidence.elevated.v1",
            [
                "დღეს შენი თავდაჯერება ოთახში შენზე ხუთი წუთით ადრე შემოდის",
                "გადაწყვეტილებების მიღება დღეს საოცრად მარტივია და ყოყმანი სადღაც გაქრა",
                "დღეს გაქვს ისეთი ენერგია, რომელიც სხვებსაც მოქმედებისკენ უბიძგებს",
            ],
            [
                "გამოიყენე ეს მუხტი, ოღონდ სხვებსაც დაუტოვე ცოტა ჟანგბადი.",
                "დღეს რთულ საქმეებს თამამად შეეჭიდე; გამბედაობა შენს მხარესაა.",
                "მთავარია, საკუთარ შესაძლებლობებში ეჭვი წამითაც არ შეიტანო.",
            ],
            [
                "Your self-assurance walks into the room five minutes before you do today",
                "Decisiveness comes with zero second-guessing; you know exactly what move to make",
            ],
            [
                "Ride this wave of assertiveness, but leave a little oxygen for everyone else.",
                "Tackle the intimidating conversation today; courage is on your side.",
            ],
        ),
        (
            "daily_energy.communication.direct.v1",
            [
                "სიტყვებს დღეს პირდაპირ მიზანში ისვრი და ზედმეტ დიპლომატიას ვერ იტან",
                "გაურკვეველი და ბუნდოვანი საუბრები დღეს ყველაზე მეტად გაღიზიანებს",
                "შენი აზრი დღეს იმდენად ნათელია, რომ მისი დამალვა შეუძლებელია",
            ],
            [
                "მთავარია, შემთხვევით მოკავშირე არ გაგეპაროს სამიზნეში.",
                "სიმართლის თქმა კარგია, მაგრამ ტაქტის შენარჩუნება დღეს განსაკუთრებით გამოგადგება.",
                "მოკლე და მკაფიო დიალოგები დღეს საუკეთესო შედეგს მოგიტანს.",
            ],
            [
                "You are cutting straight through pleasantries to the bare bones of truth today",
                "Ambiguous waffle and beating around the bush will grate on your nerves instantly",
            ],
            [
                "Aim carefully so an innocent bystander does not catch friendly fire.",
                "Clarity is your superpower today; keep communications short, sharp, and constructive.",
            ],
        ),
        (
            "daily_energy.focus.scattered.v1",
            [
                "იდეები იმდენია, რომ ყურადღება ერთდროულად ათ სხვადასხვა მიმართულებით იფანტება",
                "ახალი გეგმების დაწყება გინდა, თუმცა ძველები ჯერ ბოლომდე არ დაგიხურავს",
                "დღეს შენი გონება ცნობისმოყვარეობის პიკზეა, მაგრამ კონცენტრაცია ჭირს",
            ],
            [
                "აირჩიე ერთი მთავარი საქმე და ბოლომდე მიიყვანე — დანარჩენი არსად გაიქცევა.",
                "არ სცადო ყველაფრის ერთდროულად კეთება; პრიორიტეტები შენი გადარჩენის გზაა.",
                "ჩაიწერე იდეები და მხოლოდ ერთზე ფოკუსირდი, თორემ დღე გაფრინდება.",
            ],
            [
                "Your mind is juggling a dozen brilliant concepts simultaneously today",
                "Inspiration is everywhere, but executing a single task to completion requires discipline",
            ],
            [
                "Pick one primary target and lock in; the other ideas will wait patiently in your notes.",
                "Resist the urge to start three new projects before finishing breakfast.",
            ],
        ),
        (
            "daily_energy.creativity.exploration.v1",
            [
                "დღეს ჩვეული მარშრუტიდან გადახვევა საუკეთესო გადაწყვეტილებაა",
                "შენი წარმოსახვა მუშაობს მაქსიმალურ სიმძლავრეზე და ახალ ფორმებს ეძებს",
                "ესთეტიკური შთაგონება დღეს ყველაზე მოულოდნელ ადგილებში იმალება",
            ],
            [
                "ახალი ხედვა ყოველდღიური რუტინის დარღვევის შემდეგ გამოჩნდება.",
                "მიეცი საკუთარ თავს ექსპერიმენტების ჩატარების უფლება.",
                "დღეს შემოქმედებითი ინტუიცია მშრალ გათვლებზე გაცილებით ძლიერია.",
            ],
            [
                "Deviating from your customary routine is the sharpest decision you can make today",
                "Aesthetic receptivity is heightened; fresh perspectives hide in plain sight",
            ],
            [
                "Give your curiosity free rein to test unconventional approaches.",
                "Inspiration arrives through intuition rather than rigid spreadsheets today.",
            ],
        ),
        (
            "daily_energy.clarity.strategic_patience.v1",
            [
                "დღეს შენი აზროვნება მშვიდი, ფხიზელი და შორსმჭვრეტელია",
                "ემოციური ხმაური უკან იხევს და მხოლოდ კონკრეტული ლოგიკა რჩება",
                "გეგმების შედგენა და სისტემური დალაგება დღეს საოცრად მარტივად გამოგდის",
            ],
            [
                "გამოიყენე ეს სიფხიზლე რთული სტრატეგიული საკითხების მოსაგვარებლად.",
                "ნუ იჩქარებ; დღეს მოთმინება შენი ყველაზე მომგებიანი სტრატეგიაა.",
                "შენ ხედავ მთლიან სურათს და დეტალებში აღარ იკარგები.",
            ],
            [
                "Sober mental clarity replaces emotional static today",
                "Long-term strategic planning feels effortless and grounded in reality",
            ],
            [
                "Leverage this deliberate calm to untangle complicated operational bottlenecks.",
                "Patience is your highest-yield investment today; build for durability.",
            ],
        ),
        (
            "daily_energy.vitality.surging_drive.v1",
            [
                "დღეს გაქვს იმდენი ენერგია, რომ მთელი კვირის საქმის მოსწრება შეგიძლია",
                "ფიზიკური მუხტი მაღალია და უსაქმოდ ყოფნა გაღიზიანებს",
                "დაბრკოლებები დღეს შენთვის მხოლოდ დამატებითი აზარტის წყაროა",
            ],
            [
                "მიმართე ეს ძალა კონკრეტული მიზნისკენ, რათა ენერგია ტყუილად არ დაიფანტოს.",
                "შენი შემართება დღეს ნებისმიერ წინააღმდეგობას გაარღვევს.",
                "დღეს შენი დღეა — იმოქმედე თამამად და თავდაჯერებულად.",
            ],
            [
                "A surge of physical stamina and ambitious drive has you ready to tackle the mountain",
                "Sitting still feels nearly impossible when your engine is running this hot",
            ],
            [
                "Channel this kinetic momentum toward a major bottleneck and clear it for good.",
                "Obstacles look like minor speed bumps today; put your foot on the gas.",
            ],
        ),
        (
            "daily_energy.receptivity.emotional_pause.v1",
            [
                "დღეს შენი სოციალური ბატარეა ჩვეულებრივზე უფრო სწრაფად იცლება",
                "გარე სამყაროს ხმაურისგან თავის დაღწევა და განმარტოება საუკეთესო არჩევანია",
                "შენ გჭირდება სიჩუმე და საკუთარ ფიქრებთან მარტო დარჩენა",
            ],
            [
                "ნუ დააძალებ თავს ზედმეტ აქტიურობას; დღეს ძალების აღდგენის დროა.",
                "მშვიდი საღამო და კარგი წიგნი დღეს საუკეთესო თერაპია იქნება.",
                "საკუთარ რიტმს პატივი ეცი — ენერგია ხვალ გაორმაგებული დაბრუნდება.",
            ],
            [
                "Your social bandwidth is running on low battery today, and that is completely fine",
                "Stepping back from ambient external noise is a necessary preservation move",
            ],
            [
                "Do not guilt yourself into performing social enthusiasm; take the quiet evening.",
                "Recharge in peace so you can re-enter the arena with restored reserves tomorrow.",
            ],
        ),
        (
            "daily_energy.restlessness.impulsive_edge.v1",
            [
                "ჩვეული განრიგი დღეს გაუსაძლისად გეჩვენება და რაღაც ახლის ცდა გინდა",
                "უეცარი გადაწყვეტილებების მიღების ცდუნება დღეს განსაკუთრებით დიდია",
                "მოულოდნელი ცვლილებების სურვილი შენს სიმშვიდეს არღვევს",
            ],
            [
                "სანამ ყველაფერს თავდაყირა დააყენებ, სამამდე დაითვალე.",
                "შეცვალე წვრილმანები, მაგრამ ფუნდამენტურ გადაწყვეტილებებში სიფრთხილე გამოიჩინე.",
                "ეს მოუსვენრობა სინამდვილეში შენი შემოქმედებითი ენერგიის გამოღვიძებაა.",
            ],
            [
                "Routine tasks feel suffocating today; you crave a sharp, unpredictable pivot",
                "The temptation to make sudden, spontaneous moves is buzzing right under the surface",
            ],
            [
                "Count to three before blowing up working systems on a whim.",
                "Disrupt your habits in playful ways without setting fire to necessary commitments.",
            ],
        ),
        (
            "daily_energy.social.magnetic_charm.v1",
            [
                "დღეს ადამიანებთან საერთო ენის გამონახვა საოცრად ბუნებრივად გამოგდის",
                "შენი ღიმილი და თავაზიანობა ნებისმიერ დაძაბულ სიტუაციას მარტივად ხსნის",
                "მოლაპარაკებები და მნიშვნელოვანი შეხვედრები დღეს შენს სასარგებლოდ გადაწყდება",
            ],
            [
                "გამოიყენე ეს ხიბლი საჭირო კონტაქტების დასამყარებლად.",
                "დღეს ადამიანები შენს მიმართ განსაკუთრებულ კეთილგანწყობას იჩენენ.",
                "შენი სოციალური მაგნეტიზმი დღეს პიკზეა — გაუღიმე სამყაროს.",
            ],
            [
                "Connecting with others feels exceptionally natural, warm, and rewarding today",
                "Your social presence disarms skepticism and invites immediate goodwill",
            ],
            [
                "Schedule the important collaborative meeting today; the room is ready to listen.",
                "Effortless charm clears negotiation hurdles that usually take days to resolve.",
            ],
        ),
        (
            "daily_energy.discipline.grounded_execution.v1",
            [
                "დღეს შენი მთავარი მოკავშირე დისციპლინა, წესრიგი და კონკრეტული საქმეა",
                "დაგროვილი დავალებების ჩამოწერა და მათი სათითაოდ შესრულება კმაყოფილებას მოგანიჭებს",
                "შენ არ ელი იდეალურ მომენტს; შენ უბრალოდ ჯდები და აკეთებ",
            ],
            [
                "ეს ის დღეა, როცა შენი შრომისმოყვარეობა თვალსაჩინო შედეგს მოიტანს.",
                "დეტალებზე კონცენტრაცია დღეს შეცდომებისგან სრულად დაგიცავს.",
                "საღამოს საკუთარი თავით ნამდვილად ამაყი დარჩები.",
            ],
            [
                "Methodical discipline and quiet execution are your greatest strengths today",
                "Clearing overdue administrative backlogs provides immense satisfaction",
            ],
            [
                "You do not wait for ideal inspiration; you simply sit down and get the job done.",
                "By evening, the checklist will be cleared and your mind will feel completely free.",
            ],
        ),
        (
            "daily_energy.introspection.deep_reset.v1",
            [
                "დღეს შინაგანი გადაფასების და ზედმეტი ტვირთის მოშორების დღეა",
                "ზედაპირული საქმეები ინტერესს კარგავს; შენ არსებით საკითხებზე ფიქრობ",
                "შენ გრძნობ, რომ რაღაც ძველი ეტაპი სრულდება და ახლის დასაწყისია",
            ],
            [
                "გაუშვი ის, რაც აღარ გემსახურება — ადგილი გაუთავისუფლე ახალ ენერგიას.",
                "ეს შინაგანი სიჩუმე შენი მომავალი გამარჯვებების საძირკველია.",
                "იყავი გულწრფელი საკუთარ თავთან; პასუხები უკვე შენშია.",
            ],
            [
                "A quiet urge to declutter mental baggage and re-evaluate priorities emerges today",
                "Superficial chatter loses all appeal as you gravitate toward foundational questions",
            ],
            [
                "Shed outdated habits that no longer serve your growth; create room for the new.",
                "Honest self-reflection today lays the foundation for your next major chapter.",
            ],
        ),
        (
            "daily_energy.curiosity.spontaneous_pivot.v1",
            [
                "ახალი იდეა მოულოდნელად გებადება და მთელ დღეს ახალ მიმართულებას აძლევს",
                "დღეს შენი ინტუიცია ახალი ხელსაწყოებისა და მეთოდების გამოცდას გკარნახობს",
                "გონება მზად არის დაარღვიოს ძველი სქემები და ახლებურად იფიქროს",
            ],
            [
                "ენდე ამ იმპულსს — ხანდახან ყველაზე უცნაური ექსპერიმენტი საუკეთესო შედეგს იძლევა.",
                "გამოსცადე ახალი მიდგომა საქმეში; შედეგი სასიამოვნოდ გაგაოცებს.",
                "ცნობისმოყვარეობა დღეს შენი საუკეთესო მეგზურია.",
            ],
            [
                "An unexpected insight arrives out of nowhere, sparking an exciting pivot",
                "Your instincts urge you to test fresh workflows and challenge stale formulas",
            ],
            [
                "Follow the curiosity breadcrumbs; unconventional experiments pay off handsomely today.",
                "Break out of rigid thinking and let a clever idea take the wheel.",
            ],
        ),
    ]

    for interp_id, ka_p, ka_t, en_p, en_t in daily_defs:
        contracts.append(
            ContractSeedData(
                interpretation_id=interp_id,
                context="daily_energy",
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
