"""
Seed Content Assets for JESTER Content Architecture V2.
Provides rich, multi-variant, multi-tone, multi-locale seed assets for all 30 interpretation contracts.
Zero astrology jargon, strictly verified.
"""
from datetime import datetime, timezone
from backend.app.interpretation.models import ContentAsset

SEED_CONTENT_ASSETS: list[ContentAsset] = [
    # =========================================================================
    # 1. relationship.attraction.strong_chemistry.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_chem_001_ka_witty_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთ ოთახში რომ შემოდიხართ, ჰაერი ისე მძიმდება, თითქოს ვიღაცამ კონდიციონერი გამორთო და დრამა ჩართო. ნაპერწკლები კარგია, მაგრამ ხანძარსაწინააღმდეგო სისტემა თუ არ მუშაობს, მალე ორივე ერთად დაიფერფლებით.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "attraction", "signature"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_ka_witty_b",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="თვალებით ფლირტს მორჩით — მთელმა ოთახმა გაიგო, რაც გინდათ, თქვენ კი ისევ ისე იქცევით, თითქოს შემთხვევით აღმოჩნდით ერთსა და იმავე კედელთან მიყუდებულები.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "banter", "tech_metaphor"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_ka_playful_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="playful",
        persona="jester",
        text="ნაპერწკლები ისე მარტივად ჩნდება, რომ ცეცხლმაქრი სად დევს, წინასწარ უნდა იცოდეთ. თუმცა ვიცით, რომ მაინც არ გამოიყენებთ.",
        status="ai_draft",
        version=1,
        priority=80,
        variant_key="variant_c",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "playful"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_ka_soft_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="soft",
        persona="jester",
        text="მიზიდულობა კი აშკარაა, მაგრამ ამ მუხტის ყოველდღიურობაში გადატანა ცალკე ხელოვნებაა.",
        status="ai_draft",
        version=1,
        priority=50,
        variant_key="variant_d",
        source="ai",
        author="jester_ai_v1",
        tags=["chemistry", "soft"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_ka_bold_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="bold",
        persona="jester",
        text="აქ პაუზები უხერხული არ არის — პაუზებში ელექტროენერგია გროვდება, სანამ რომელიმე თქვენგანი პირველ ნაბიჯს არ გადადგამს.",
        status="ai_draft",
        version=1,
        priority=85,
        variant_key="variant_e",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "bold"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_en_witty_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="The chemistry here doesn't require an instruction manual.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "en"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_en_playful_a",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="en",
        context="relationship",
        tone="playful",
        persona="jester",
        text="You two don't need separate Wi-Fi — the mutual signal connects instantly.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        author="lead_copywriter",
        tags=["chemistry", "playful", "en"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_friendship_witty",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="friendship",
        tone="witty",
        persona="jester",
        text="თქვენი მეგობრული დინამიკა ისეთი ცოცხალია, რომ ერთად ყოფნისას მოსაწყენი მომენტი არ არსებობს.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="friendship_witty",
        source="copywriter",
        author="lead_copywriter",
        tags=["friendship", "chemistry"],
    ),
    ContentAsset(
        asset_id="ca_rel_chem_001_archived_sample",
        interpretation_id="relationship.attraction.strong_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ეს არის დაარქივებული ძველი ტექსტი, რომელიც აღარ უნდა გამოჩნდეს.",
        status="archived",
        version=1,
        priority=200,
        archived=True,
        source="system",
        internal_notes="Archived old draft to test resolver exclusion",
    ),

    # =========================================================================
    # 2. relationship.attraction.strong_chemistry.v2
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_chem_v2_ka_witty_a",
        interpretation_id="relationship.attraction.strong_chemistry.v2",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="თვალებით ფლირტს მორჩით — მთელმა ოთახმა გაიგო, რაც გინდათ, თქვენ კი ისევ ისე იქცევით, თითქოს შემთხვევით აღმოჩნდით ერთსა და იმავე კედელთან მიყუდებულები.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["chemistry", "v2"],
    ),

    # =========================================================================
    # 3. relationship.attraction.magnetic_chemistry.v1 (Redundant/consolidated)
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_mag_chem_ka_witty_a",
        interpretation_id="relationship.attraction.magnetic_chemistry.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთმანეთს ისე ეჯახებით, როგორც ორი დამუხტული სადენი — იცით, რომ საშიშია, მაგრამ მაინც ხელს ჰკიდებთ. ლოგიკა კარიდან გადის იმ წამსვე, როგორც კი ერთმანეთის სიახლოვეს აღმოჩნდებით.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["chemistry", "magnetic"],
    ),

    # =========================================================================
    # 4. relationship.harmony.emotional_resonance.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_harm_emot_ka_witty_a",
        interpretation_id="relationship.harmony.emotional_resonance.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთმანეთის განწყობას უსიტყვოდ ხვდებით, მაგრამ ამას ხშირად იყენებთ იმისთვის, რომ საუბარს თავი აარიდოთ. ტელეპათიის იმედად ყოფნა საბოლოოდ ყოველთვის გაუგებრობით მთავრდება.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["harmony", "sun_moon"],
    ),
    ContentAsset(
        asset_id="ca_rel_harm_emot_ka_soft_a",
        interpretation_id="relationship.harmony.emotional_resonance.v1",
        locale="ka",
        context="relationship",
        tone="soft",
        persona="jester",
        text="ისეთი ემოციური სინქრონი გაქვთ, თითქოს ერთმანეთის თავში უნებართვოდ დაძრწოდეთ — ოღონდ ხანდახან ხმამაღალი ლაპარაკიც არ დაგავიწყდეთ.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        tags=["harmony", "soft"],
    ),
    ContentAsset(
        asset_id="ca_rel_harm_emot_en_witty_a",
        interpretation_id="relationship.harmony.emotional_resonance.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="Understanding each other without words is great, just remember to speak out loud occasionally.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["harmony", "en"],
    ),

    # =========================================================================
    # 5. relationship.growth.complementary_balance.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_comp_ka_witty_a",
        interpretation_id="relationship.growth.complementary_balance.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="სრულიად განსხვავებული რაკურსით უყურებთ სამყაროს. იდეალური ბალანსია ზუსტად მანამ, სანამ გადაწყვეტთ, ვინ მართავს მანქანას და ვისი პლეილისტი ჩაირთვება.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "contrast"],
    ),
    ContentAsset(
        asset_id="ca_rel_growth_comp_en_witty_a",
        interpretation_id="relationship.growth.complementary_balance.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="You view the world from totally opposite angles, which stays fascinating until you decide who drives the car.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "en"],
    ),

    # =========================================================================
    # 6. relationship.growth.dynamic_emotional_tension.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_tension_ka_witty_a",
        interpretation_id="relationship.growth.dynamic_emotional_tension.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="თქვენთან ამინდი უფრო ხშირად იცვლება, ვიდრე მთაში. დრამა ცხოვრებას კი აფერადებს, მაგრამ ყოველ საღამოს თეატრალურ წარმოდგენას ნერვები დიდხანს ვერ გაუძლებს.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "square"],
    ),

    # =========================================================================
    # 7. relationship.harmony.core_harmony.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_harm_core_ka_witty_a",
        interpretation_id="relationship.harmony.core_harmony.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ფუნდამენტურ საკითხებში იმდენად ერთნაირად ფიქრობთ, რომ კამათის დაწყებაც კი მოსაწყენად გეჩვენებათ. ფრთხილად: ზედმეტი ერთსულოვნება აზროვნებას აზარმაცებს.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["harmony", "sun_sun"],
    ),
    ContentAsset(
        asset_id="ca_rel_harm_core_ka_soft_a",
        interpretation_id="relationship.harmony.core_harmony.v1",
        locale="ka",
        context="relationship",
        tone="soft",
        persona="jester",
        text="საძირკველი იმდენად მყარია, რომ ცოტა დრამაც კი გენატრებათ — მთავარია, შიგნით ცეცხლი არ ჩაქრეს.",
        status="ai_draft",
        version=1,
        priority=60,
        variant_key="variant_b",
        source="ai",
        tags=["harmony", "soft"],
    ),

    # =========================================================================
    # 8. relationship.growth.contrasting_perspectives.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_contrast_ka_witty_a",
        interpretation_id="relationship.growth.contrasting_perspectives.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთი და იმავე ფაქტიდან ორი სრულიად საპირისპირო დასკვნა გამოგაქვთ და ორივე დარწმუნებული ხართ საკუთარ გენიალურობაში. სარკეში ყურება კარგია, ოღონდ თუ მარტო მეორის ნაკლს ამჩნევთ, სარკის გატეხვა მოგინდებათ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "opposition"],
    ),

    # =========================================================================
    # 9. relationship.growth.ego_friction.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_ego_ka_witty_a",
        interpretation_id="relationship.growth.ego_friction.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ორი ძლიერი ეგო ერთ სივრცეში — ჰაერი იმდენად მწირია, რომ ყოველი გადაწყვეტილება ტახტისთვის ბრძოლად იქცევა. გვირგვინი ერთია და ორივე ერთად ვერ დაიხურავთ; რიგრიგობით ტარება ისწავლეთ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "ego"],
    ),
    ContentAsset(
        asset_id="ca_rel_growth_ego_ka_bold_a",
        interpretation_id="relationship.growth.ego_friction.v1",
        locale="ka",
        context="relationship",
        tone="bold",
        persona="jester",
        text="ორივე საჭეს ექაჩებით და მუხრუჭს სისუსტედ თვლით. თუ ამ სიჯიუტეს გარეთ მიმართავთ, მთებს გადადგამთ; შიგნით მიმართული კი ორივეს დაგასუსტებთ.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        tags=["growth", "bold"],
    ),

    # =========================================================================
    # 10. relationship.attraction.warm_affection.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_attr_warm_ka_witty_a",
        interpretation_id="relationship.attraction.warm_affection.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ისეთი სათუთი ზრუნვით ექცევით ერთმანეთს, თითქოს ფაიფურის ჭიქები იყოთ და არა ზრდასრული ადამიანები. ეს მყუდრო იდილია სასიამოვნოა, სანამ ერთმანეთის გაღიზიანებას ზედმეტი თავაზიანობით არ დაიწყებთ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["attraction", "warmth"],
    ),

    # =========================================================================
    # 11. relationship.harmony.gentle_affinity.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_harm_gentle_ka_witty_a",
        interpretation_id="relationship.harmony.gentle_affinity.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთმანეთს ისეთი გადამეტებული სიფრთხილით ექცევით, თითქოს მყიფე მინის სათამაშოები გეჭიროთ ხელში. მზრუნველობა კარგია, მაგრამ საბავშვო ბაღის რეჟიმიდან გამოსვლაც დროა.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["harmony", "moon_venus"],
    ),

    # =========================================================================
    # 12. relationship.communication.intellectual_flow.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_comm_flow_ka_witty_a",
        interpretation_id="relationship.communication.intellectual_flow.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ისეთი სისწრაფით ცვლით აზრებსა და ირონიას, რომ გვერდით მყოფს თავი ნელთბილ სტატისტად ეჩვენება. ინტელექტუალური პინგ-პონგი ბრწყინვალეა, ოღონდ გრძნობებზე ლაპარაკის დროსაც სარკაზმს თუ არ გამორთავთ, მარტო დარჩებით.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["communication", "mercury"],
    ),
    ContentAsset(
        asset_id="ca_rel_comm_flow_ka_playful_a",
        interpretation_id="relationship.communication.intellectual_flow.v1",
        locale="ka",
        context="relationship",
        tone="playful",
        persona="jester",
        text="ნახევარ სიტყვაში გესმით ერთმანეთის ცინიზმი. ერთმანეთის აზრების დასრულება კარგია, მაგრამ ხანდახან აცადეთ მეორეს წინადადების ბოლომდე თქმა.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        tags=["communication", "playful"],
    ),
    ContentAsset(
        asset_id="ca_rel_comm_flow_en_witty_a",
        interpretation_id="relationship.communication.intellectual_flow.v1",
        locale="en",
        context="relationship",
        tone="witty",
        persona="jester",
        text="Your conversations resemble an Olympic table tennis rally — ideas move so fast onlookers get dizzy.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["communication", "en"],
    ),

    # =========================================================================
    # 13. relationship.communication.mutual_understanding.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_comm_mut_ka_witty_a",
        interpretation_id="relationship.communication.mutual_understanding.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="საერთო ენა ისე მარტივად იპოვეთ, თითქოს ერთსა და იმავე კლასში იჯექით ბოლო მერხზე და მასწავლებელს დასცინოდით. ასეთი კომფორტული დიალოგი საშიშია: იმდენად ეჩვევით ერთმანეთის გაგებას, რომ გარესამყაროსთან კონტაქტი გეზარებათ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["communication", "sun_mercury"],
    ),

    # =========================================================================
    # 14. relationship.growth.pacing_tension.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_pacing_ka_witty_a",
        interpretation_id="relationship.growth.pacing_tension.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთს უკვე ჩემოდანი აქვს ჩალაგებული, მეორე კი ჯერ კიდევ ამინდის პროგნოზს აანალიზებს. სანამ ერთი ფიქრობს, მეორე უკვე შეცდომას უშვებს — სამაგიეროდ, ბალანსი დაცულია.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "saturn"],
    ),

    # =========================================================================
    # 15. relationship.growth.dynamic_spark.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_growth_spark_ka_witty_a",
        interpretation_id="relationship.growth.dynamic_spark.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="თქვენს შორის სიმშვიდე არ არსებობს: თუ პრობლემა არ არის, ხელოვნურად შექმნით, რომ მერე აზარტით განიხილოთ. მთავარია, კამათის შემდეგ ვახშამი მეგობრულად გაიყოთ და ჩანგლები იარაღად არ გამოიყენოთ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["growth", "mars_sun"],
    ),

    # =========================================================================
    # 16. relationship.attraction.energized_collaboration.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_attr_collab_ka_witty_a",
        interpretation_id="relationship.attraction.energized_collaboration.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="როცა ერთად საქმეს იწყებთ, ენერგია ისე გემატებათ, თითქოს მთელ სამყაროს უნდა მოუგოთ შეჯიბრი. ტემპი შთამბეჭდავია, სანამ გაირკვევა, რომ საწვავი გამოგელიათ და რუკა სახლში დაგრჩათ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["attraction", "sun_mars"],
    ),

    # =========================================================================
    # 17. relationship.attraction.dynamic_drive.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_attr_drive_ka_witty_a",
        interpretation_id="relationship.attraction.dynamic_drive.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ორივეს გაზის პედალი გიყვართ და მუხრუჭს სისუსტედ თვლით. სიჩქარე კარგია, მაგრამ საჭეს თუ ორივე ერთდროულად მოქაჩავთ, ბოძთან შეხვედრა გარდაუვალია.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["attraction", "drive"],
    ),

    # =========================================================================
    # 18. relationship.stability.shared_optimism.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_stab_opt_ka_witty_a",
        interpretation_id="relationship.stability.shared_optimism.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="პრობლემებს ისეთი მსუბუქი იუმორით უყურებთ, თითქოს კრიზისი თქვენ კი არა, მეზობელს დაემართა. ოპტიმიზმი გადამდებია, მაგრამ ვარდისფერი სათვალე რეალურ ორმოებს ვერ ამოავსებს.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["stability", "jupiter"],
    ),

    # =========================================================================
    # 19. relationship.harmony.generous_affection.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_harm_gen_ka_witty_a",
        interpretation_id="relationship.harmony.generous_affection.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ერთმანეთს კომპლიმენტებითა და მხარდაჭერით ისე ავსებთ, თითქოს პირადი პიარ-სააგენტოები გქონდეთ დაქირავებული. ეს მხარდაჭერა გულწრფელია, სანამ ერთ-ერთი თქვენგანი ჩრდილში არ აღმოჩნდება.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["harmony", "venus_jupiter"],
    ),

    # =========================================================================
    # 20. relationship.attraction.intense_magnetism.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_attr_pluto_ka_witty_a",
        interpretation_id="relationship.attraction.intense_magnetism.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ისეთი მზერით უყურებთ ერთმანეთს, თითქოს პაროლი იცით, რომლითაც მეორის ფსიქიკის გატეხვა შეიძლება. ეს მიზიდულობა კი არა, ფსიქოლოგიური დეტექტივია, სადაც ორივე ეჭვმიტანილიცაა და გამომძიებელიც.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["attraction", "venus_pluto"],
    ),
    ContentAsset(
        asset_id="ca_rel_attr_pluto_ka_bold_a",
        interpretation_id="relationship.attraction.intense_magnetism.v1",
        locale="ka",
        context="relationship",
        tone="bold",
        persona="jester",
        text="აქ მზერა სიტყვებზე მეტს ამბობს. ფსიქოლოგიური ინტრიგა პირველივე შეხვედრიდან იგრძნობა — საიდუმლოებებით თამაშს შეეშვით, ორივემ ზუსტად იცით, რასაც მალავთ.",
        status="ai_draft",
        version=1,
        priority=90,
        variant_key="variant_b",
        source="copywriter",
        tags=["attraction", "bold"],
    ),

    # =========================================================================
    # 21. relationship.stability.long_term_grounding.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_stab_ground_ka_witty_a",
        interpretation_id="relationship.stability.long_term_grounding.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="დაპირებებს ისე სერიოზულად ეკიდებით, თითქოს ნოტარიუსთან იყოთ ხელმოწერილი. ციხესიმაგრე კი ააშენეთ, ოღონდ შიგნით სიცოცხლეც რომ დატოვოთ, კარგი იქნება.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["stability", "saturn_trine"],
    ),

    # =========================================================================
    # 22. relationship.notice.independent_dynamics.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_not_indep_ka_witty_a",
        interpretation_id="relationship.notice.independent_dynamics.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="პირად სივრცეს ისეთი ეჭვიანობით იცავთ, თითქოს ერთმანეთისგან თავის დაცვა გჭირდებოდეთ. თავისუფლება კარგია, მაგრამ თუ საერთო არაფერი დაგრჩათ, ურთიერთობას რატომღა არქმევთ?",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["notice", "independence"],
    ),

    # =========================================================================
    # 23. relationship.overall.exceptional_flow.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_over_exc_ka_witty_a",
        interpretation_id="relationship.overall.exceptional_flow.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ყველაფერი ისე ბუნებრივად და უხარვეზოდ ლაგდება, რომ საეჭვოცაა — ცხოვრება ასეთი მარტივი არასდროსაა. ასეთი სინერგია იშვიათია, ოღონდ ილუზიაში ნუ ჩავარდებით, რომ ეს თავისით გაგრძელდება სამუდამოდ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["overall", "high_score"],
    ),

    # =========================================================================
    # 24. relationship.overall.balanced_synergy.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_over_bal_ka_witty_a",
        interpretation_id="relationship.overall.balanced_synergy.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="გაქვთ საერთო ბაზა, მაგრამ ინდივიდუალურ სივრცესაც კბილებით იცავთ — და სწორედ ეს გინარჩუნებთ ინტერესს. ბალანსი შესანიშნავია, მთავარია, ეს დისტანცია ემოციურ სიცივეში არ გადაიზარდოს.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["overall", "balanced"],
    ),

    # =========================================================================
    # 25. relationship.overall.stimulating_friction.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_over_stim_ka_witty_a",
        interpretation_id="relationship.overall.stimulating_friction.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="თქვენი კავშირი მუდმივი პროვოკაციაა — არცერთი არ აძლევთ მეორეს მშვიდად ყოფნის უფლებას. მუდმივი გამოწვევა მატონიზირებელია, მაგრამ დასვენებაც რომ სჭირდება ადამიანს, ეგეც გაითვალისწინეთ.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["overall", "friction"],
    ),

    # =========================================================================
    # 26. relationship.overall.independent_paths.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_rel_over_indep_ka_witty_a",
        interpretation_id="relationship.overall.independent_paths.v1",
        locale="ka",
        context="relationship",
        tone="witty",
        persona="jester",
        text="ორი სრულიად დამოუკიდებელი სამყარო ხართ, რომლებიც ერთმანეთს დროდადრო გადაკვეთენ და მერე ისევ საკუთარ ტრაექტორიაზე ბრუნდებიან. თავისუფლება კარგია, ოღონდ თუ საერთო არაფერი დაგრჩათ, ურთიერთობას რატომღა არქმევთ?",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["overall", "independent"],
    ),

    # =========================================================================
    # 27. daily_energy.confidence.elevated.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_de_conf_elev_ka_witty_a",
        interpretation_id="daily_energy.confidence.elevated.v1",
        locale="ka",
        context="daily_energy",
        tone="witty",
        persona="jester",
        text="დღეს შენი თავდაჯერება ოთახში შენზე ხუთი წუთით ადრე შემოდის. გამოიყენე, ოღონდ სხვებსაც დაუტოვე ჟანგბადი.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["daily_energy", "confidence"],
    ),
    ContentAsset(
        asset_id="ca_de_conf_elev_en_witty_a",
        interpretation_id="daily_energy.confidence.elevated.v1",
        locale="en",
        context="daily_energy",
        tone="witty",
        persona="jester",
        text="Your confidence enters the room five minutes before you do today. Use it, but leave some oxygen for everyone else.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["daily_energy", "confidence", "en"],
    ),

    # =========================================================================
    # 28. daily_energy.communication.direct.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_de_comm_dir_ka_witty_a",
        interpretation_id="daily_energy.communication.direct.v1",
        locale="ka",
        context="daily_energy",
        tone="witty",
        persona="jester",
        text="სიტყვებს დღეს პირდაპირ მიზანში ისვრი. მთავარია, შემთხვევით მოკავშირე არ გაგეპაროს სამიზნეში.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["daily_energy", "communication"],
    ),

    # =========================================================================
    # 29. daily_energy.focus.scattered.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_de_focus_scat_ka_witty_a",
        interpretation_id="daily_energy.focus.scattered.v1",
        locale="ka",
        context="daily_energy",
        tone="witty",
        persona="jester",
        text="იდეები იმდენია, რომ ყურადღება იფანტება. აირჩიე ერთი და ბოლომდე მიიყვანე — დანარჩენი არსად გაიქცევა.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["daily_energy", "focus"],
    ),

    # =========================================================================
    # 30. daily_energy.creativity.exploration.v1
    # =========================================================================
    ContentAsset(
        asset_id="ca_de_creat_exp_ka_witty_a",
        interpretation_id="daily_energy.creativity.exploration.v1",
        locale="ka",
        context="daily_energy",
        tone="witty",
        persona="jester",
        text="დღეს ჩვეული მარშრუტიდან გადახვევა საუკეთესო გადაწყვეტილებაა. ახალი ხედვა მოულოდნელ ადგილას იმალება.",
        status="ai_draft",
        version=1,
        priority=100,
        variant_key="variant_a",
        source="copywriter",
        tags=["daily_energy", "creativity"],
    ),
]
