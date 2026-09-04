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
                "გადაწყვეტილებებს ისეთი სისწრაფით იღებ, თითქოს შედეგებზე პასუხისმგებლობა სხვას ეკისრებოდეს",
                "სარკეში საკუთარ თავსაც კი ცოტა ზემოდან უყურებ და სხვების ყოყმანი გაღიზიანებს",
            ],
            [
                "გამოიყენე ეს მუხტი, ოღონდ სხვებსაც დაუტოვე ცოტა ჟანგბადი.",
                "გგონია, რომ შეუცდომელი ხარ, მაგრამ უბრალოდ დღეს საკუთარი შეცდომების შემჩნევა არ გინდა.",
                "დღეს ყველა კითხვაზე პასუხი გაქვს, ოღონდ მთავარია, ვინმემ არ გადაამოწმოს.",
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
                "სიტყვებს დღეს პირდაპირ მიზანში ისვრი და დიპლომატიას დროის კარგვად თვლი",
                "სხვების გაურკვეველი ლაპარაკი იმდენად გაღიზიანებს, რომ წინადადების დასრულებას არავის აცდი",
                "შენი აზრი დღეს იმდენად დაუნდობლად ნათელია, რომ მისი დამალვა ფიზიკურად შეუძლებელია",
            ],
            [
                "მთავარია, შემთხვევით მოკავშირე არ გაგეპაროს სამიზნეში — სიმართლე კარგია, მაგრამ მარტო დარჩენა ცოტა მოსაწყენი.",
                "სხვების გრძნობების დაზოგვაზე დღეს საერთოდ არ ფიქრობ და მერე გიკვირს, რატომ გაჩუმდა ოთახი.",
                "შენი „გულწრფელობა“ დღეს უფრო ლაზერულ ჭრას ჰგავს, ვიდრე მეგობრულ დიალოგს.",
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
                "იდეები იმდენია, რომ ათივე საქმეს ერთდროულად იწყებ და ათივეს ხვალისთვის გადადებ",
                "შენი ყურადღება ერთდროულად ოც სხვადასხვა ბრაუზერის ჩანართშია გაფანტული",
                "ახალი გეგმა თავში ყოველ ხუთ წუთში ერთხელ გებადება, სანამ წინა საქმე ნახევარზეა მიტოვებული",
            ],
            [
                "დღეს ენერგია იმდენ წვრილმანზე იფანტება, რომ საღამოს დაღლილი ხარ, თუმცა რეალურად არაფერი გაგიკეთებია.",
                "მთავარია, ახალი პროექტის დაწყების ეიფორიამ ძველი ვალდებულებები სულ არ დაგავიწყოს.",
                "შენი გონება დღეს ფოიერვერკს ჰგავს — ლამაზად ანათებს, მაგრამ საქმის კეთებას ხელს უშლის.",
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
                "ჩვეული მარშრუტიდან გადახვევა დღეს საუკეთესო გადაწყვეტილებაა, რადგან რუტინა გგუდავს",
                "ისეთ ექსპერიმენტებში ერთვები, რომ ნორმალური ადამიანები გაოცებული გიყურებენ",
                "შენი წარმოსახვა მაქსიმალურ სიმძლავრეზე მუშაობს და ყველაფერში უჩვეულო კუთხეს ეძებს",
            ],
            [
                "ახალ ხედვას პოულობ, ოღონდ ექსპერიმენტებში ისე ნუ გადავარდები, რომ რეალობაში დაბრუნების გზა დაგავიწყდეს.",
                "ორიგინალურობა კარგია, მაგრამ ხანდახან ბორბლის თავიდან გამოგონება უბრალოდ ენერგიის კარგვაა.",
                "შენი შემოქმედებითი მუხტი დღეს ყველას აბნევს — რასაც აკეთებ, გენიალურობასა და უაზრობას შორის ბალანსირებს.",
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
                "დღეს აჩქარება მხოლოდ შეცდომებს მოგიტანს — ჯერ სხვებს აცადე შეცდომის დაშვება",
                "ემოციური ხმაური უკან იხევს და სიტუაციას ისე უყურებ, როგორც ცივ საჭადრაკო დაფას",
                "შენი სიმშვიდე დღეს იმდენად შორსმჭვრეტელია, რომ სხვების პანიკა უბრალოდ გეცინება",
            ],
            [
                "ნუ იჩქარებ; დღეს მოთმინება შენი ყველაზე მომგებიანი სტრატეგიაა — შენი გამარჯვება ისედაც გარდაუვალია.",
                "სანამ სხვები ენერგიას ცარიელ ყვირილში ხარჯავენ, შენ წყნარად ელოდები შენს მომენტს.",
                "შენი სტრატეგიული სიცივე დღეს ისეთია, რომ შენთან კამათის გაგრძელება ყველას ეზარება.",
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
                "ფიზიკური მუხტი იმდენად მაღალია, რომ ერთ ადგილზე ჯდომა ფიზიკურ ტკივილს გაყენებს",
                "დღეს გაქვს ისეთი ენერგია, თითქოს მთელი ქალაქის პრობლემების მოგვარება ერთ დღეში შეგეძლოს",
                "დაბრკოლებებს ისე ეჯახები, თითქოს გზაზე მუყაოს ყუთები იდგეს",
            ],
            [
                "მიმართე ეს ძალა კონკრეტული მიზნისკენ, თორემ უბრალოდ საკუთარ თავსაც გადაღლი და გარშემომყოფებსაც.",
                "შენი შემართება შთამბეჭდავია, მაგრამ სიჩქარეში შეიძლება ისეთი რამე გატეხო, რისი შეკეთებაც მერე ძვირი დაჯდება.",
                "ენერგია გადმოდის ნაპირებიდან, ოღონდ სხვებსაც მიეცი უფლება შენსავით არ იჩქარონ.",
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
                "დღეს შენი სოციალური ბატარეა იმდენად დაბალ ნიშნულზეა, რომ უბრალო მისალმებაც კი ძალისხმევას მოითხოვს",
                "გარე სამყაროს ხმაური გაღიზიანებს და ადამიანების დანახვაზე კარის გადაკეტვა გინდება",
                "საკუთარ თავთან მარტო დარჩენა ერთადერთი რამაა, რაც დღეს ნორმალურ მდგომარეობას შეგინარჩუნებს",
            ],
            [
                "ნუ აიძულებ თავს სოციალური ენთუზიაზმის თამაშს — დღეს უბრალოდ დაიმალე და ჟანგბადი მოიკრიბე.",
                "თუ დღეს ვინმე ზედმეტ კომუნიკაციას მოგთხოვს, შეიძლება ისეთი პასუხი გაგეპაროს, რომ წლები ინანო.",
                "საკუთარი თავშესაფარი დღეს შენი ერთადერთი გადარჩენაა; სამყარო შენ გარეშეც მშვენივრად გაძლებს რამდენიმე საათს.",
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
                "ჩვეული განრიგი დღეს გაუსაძლისად გეჩვენება და რაღაცის თავდაყირა დაყენების ცდუნება გაწუხებს",
                "ისეთი მოუსვენრობა გიპყრობს, რომ უბრალოდ მშვიდად ჯდომა შენთვის შეუძლებელი მისიაა",
                "უეცარი და დაუფიქრებელი გადაწყვეტილების მიღების სურვილი ჰაერში ელექტროენერგიასავით ტრიალებს",
            ],
            [
                "სანამ ძველ ხიდებს გადაწვავ, დაფიქრდი: ეს ნამდვილი ცვლილების სურვილია თუ უბრალოდ მოწყენილობა.",
                "მოულოდნელად მიღებული გადაწყვეტილება დღეს შეიძლება ხვალ სანანებელი გაგიხდეს.",
                "მოუსვენრობა გიბიძგებს რისკისკენ, ოღონდ შედეგების გასწორება მერე ორმაგად დაგეზარება.",
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
                "დღეს შენი მომხიბვლელობა ისე მუშაობს, რომ ნებისმიერი კარის გაღება მარტივი ღიმილით შეგიძლია",
                "ადამიანებთან საერთო ენას ისე პოულობ, თითქოს მათი საიდუმლო სურვილები წინასწარ იცოდე",
                "შენი სოციალური მაგნეტიზმი პიკზეა და ყველას უნდა შენს კომპანიაში დარჩენა",
            ],
            [
                "გამოიყენე ეს მომენტი, ოღონდ საკუთარი მომხიბვლელობის ილუზიაში ნუ ჩაიძირები — ხალხს შენი ხიბლი მოსწონს და არა შენი ახირებები.",
                "შენი ღიმილი დღეს ყველაზე ხისტ ოპონენტსაც განაიარაღებს, ოღონდ დაპირებებს ზედმეტად ნუ გაანიავებ.",
                "ადამიანები შენს გარშემო ტრიალებენ, მთავარია ამ ყურადღებამ თავბრუ არ დაგახვიოს.",
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
                "დღეს ემოციებსა და ოცნებებს გვერდზე დებ და მხოლოდ იმას აკეთებ, რაც კონკრეტულ შედეგს დებს",
                "დაგროვილი საქმეების სია დღეს შენს წინაშე ისე დევს, როგორც საომარი გეგმა",
                "შენ არ ელი იდეალურ განწყობას; უბრალოდ ჯდები და ასრულებ იმას, რასაც სხვები გაურბიან",
            ],
            [
                "დღეს შენი შრომისმოყვარეობა მანქანის მუშაობას ჰგავს — ეფექტურია, თუმცა სითბოსგან სრულიად დაცლილი.",
                "საღამოს საქმეები კი იქნება დასრულებული, მაგრამ მოდუნებას მაინც ვერ შეძლებ, რადგან ახალი სია უკვე მზად გაქვს.",
                "დისციპლინა დღეს შენი იარაღია, ოღონდ საკუთარ თავს ზედამხედველივით ნუ ექცევი.",
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
                "ზედაპირული თემები დღეს ინტერესს სრულად კარგავს და შინაგან გადაფასებაში იძირები",
                "გრძნობ, რომ რაღაც ძველი ილუზია ინგრევა და სიმართლისთვის თვალებში შეხედვის დრო მოვიდა",
                "სხვისი აზრი დღეს საერთოდ აღარ გადარდებს; შენ შენს პირად საზღვრებს ამოწმებ",
            ],
            [
                "საკუთარ თავთან გულწრფელობა მტკივნეულია, მაგრამ სამაგიეროდ ყალბი როლების თამაშს ერთხელ და სამუდამოდ წყვეტ.",
                "გადაყარე ის, რაც აღარ მუშაობს — ნუ ინახავ ძველ წყენებს, თითქოს ძვირფასი რელიქვია იყოს.",
                "დღეს სიმართლე უხერხულია, თუმცა ამ სიმართლის გარეშე წინ ვეღარ წახვალ.",
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
                "ახალი იდეა მოულოდნელად გებადება და ძველ გეგმებს წამში უაზროდ აქცევს",
                "ძველი მეთოდებით მუშაობა დღეს იმდენად გღლის, რომ მზად ხარ ყველაზე გიჟური ალტერნატივა მოსინჯო",
                "შენი გონება დღეს გაურბის შაბლონებს და მოულოდნელ კავშირებს პოულობს",
            ],
            [
                "გამოსცადე ახალი მიდგომა, ოღონდ ნუ გაგიკვირდება, თუ გარშემომყოფები თავიდან შეშფოთებით შემოგხედავენ.",
                "ცნობისმოყვარეობა კარგია, მაგრამ ყოველ ნახევარ საათში მიმართულების შეცვლა საქმეს ვერ დაასრულებს.",
                "დღეს ექსპერიმენტების დღეა — მთავარია, ლაბორატორია შემთხვევით არ ააფეთქო.",
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
