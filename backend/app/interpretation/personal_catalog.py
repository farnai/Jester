"""
Personal Insights (Self Catalog) - 7 Layers of Astrological & Psychological Intelligence.
Provides deterministic resolution of user's natal chart into structured, paywall-ready layers.
"""
from dataclasses import dataclass
from typing import Any, Literal
import uuid
import psycopg
from psycopg.rows import dict_row

from backend.app.astrology.aspects import detect_aspect, AspectType
from backend.app.astrology.calculator import longitude_to_sign
from backend.app.interpretation.library import content_library

GEORGIAN_SIGNS = {
    "aries": "ვერძი", "taurus": "კურო", "gemini": "ტყუპები", "cancer": "კირჩხიბი",
    "leo": "ლომი", "virgo": "ქალწული", "libra": "სასწორი", "scorpio": "მორიელი",
    "sagittarius": "მშვილდოსანი", "capricorn": "თხის რქა", "aquarius": "მერწყული", "pisces": "თევზები"
}

GEORGIAN_SIGNS_LOCATIVE = {
    "aries": "ვერძში", "taurus": "კუროში", "gemini": "ტყუპებში", "cancer": "კირჩხიბში",
    "leo": "ლომში", "virgo": "ქალწულში", "libra": "სასწორში", "scorpio": "მორიელში",
    "sagittarius": "მშვილდოსანში", "capricorn": "თხის რქაში", "aquarius": "მერწყულში", "pisces": "თევზებში"
}

GEORGIAN_ELEMENTS = {
    "fire": "ცეცხლი", "earth": "მიწა", "air": "ჰაერი", "water": "წყალი"
}

GEORGIAN_MODALITIES = {
    "cardinal": "კარდინალური", "fixed": "ფიქსირებული", "mutable": "მუტაბელური"
}

GEORGIAN_ASPECT_NAMES: dict[str, str] = {
    "conjunction": "შეერთება",
    "sextile": "სექსტილი",
    "square": "კვადრატი",
    "trine": "ტრინი",
    "opposition": "ოპოზიცია"
}

GEORGIAN_BODIES: dict[str, str] = {
    "sun": "მზე", "moon": "მთვარე", "mercury": "მერკური", "venus": "ვენერა",
    "mars": "მარსი", "jupiter": "იუპიტერი", "saturn": "სატურნი",
    "uranus": "ურანი", "neptune": "ნეპტუნი", "pluto": "პლუტონი", "ascendant": "ასცენდენტი"
}


def get_personal_catalog(user_id: uuid.UUID, db: psycopg.Connection, locale: str = "ka") -> dict[str, Any]:
    """
    Returns the complete 7-Layer Personal Insights catalog for the authenticated user,
    deterministically resolving Swiss Ephemeris natal positions and aspects into rich Georgian copy.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT 
                b.birth_date, b.birth_time, b.birth_time_precision, b.birth_timezone, b.place_label,
                s.sun_sign, s.moon_sign, s.ascendant_sign,
                s.element_primary, s.modality_primary,
                p.sun_longitude, p.moon_longitude, p.mercury_longitude, p.venus_longitude,
                p.mars_longitude, p.jupiter_longitude, p.saturn_longitude, p.uranus_longitude,
                p.neptune_longitude, p.pluto_longitude, p.ascendant_longitude
            FROM public.birth_data b
            LEFT JOIN public.astro_safe_profile s ON s.user_id = b.user_id
            LEFT JOIN public.astro_private p ON p.user_id = b.user_id
            WHERE b.user_id = %s;
            """,
            (user_id,),
        )
        row = cur.fetchone()

    if not row or not row.get("birth_date") or not row.get("sun_sign"):
        return {
            "has_data": False,
            "data_quality": {
                "has_birth_data": False,
                "has_exact_time": False,
                "missing_fields": ["birth_date", "birth_time", "birth_city"]
            },
            "layers": []
        }

    sun = (row.get("sun_sign") or "").lower()
    moon = (row.get("moon_sign") or "").lower()
    rising = (row.get("ascendant_sign") or "").lower()
    mercury = (longitude_to_sign(row.get("mercury_longitude")) if row.get("mercury_longitude") is not None else "").lower()
    venus = (longitude_to_sign(row.get("venus_longitude")) if row.get("venus_longitude") is not None else "").lower()
    mars = (longitude_to_sign(row.get("mars_longitude")) if row.get("mars_longitude") is not None else "").lower()
    jupiter = (longitude_to_sign(row.get("jupiter_longitude")) if row.get("jupiter_longitude") is not None else "").lower()
    saturn = (longitude_to_sign(row.get("saturn_longitude")) if row.get("saturn_longitude") is not None else "").lower()
    neptune = (longitude_to_sign(row.get("neptune_longitude")) if row.get("neptune_longitude") is not None else "").lower()
    pluto = (longitude_to_sign(row.get("pluto_longitude")) if row.get("pluto_longitude") is not None else "").lower()

    elem = (row.get("element_primary") or "fire").lower()
    mod = (row.get("modality_primary") or "cardinal").lower()

    # Elemental mapping helper
    elem_map = {
        "aries": "fire", "leo": "fire", "sagittarius": "fire",
        "taurus": "earth", "virgo": "earth", "capricorn": "earth",
        "gemini": "air", "libra": "air", "aquarius": "air",
        "cancer": "water", "scorpio": "water", "pisces": "water"
    }
    sun_el = elem_map.get(sun, elem)
    moon_el = elem_map.get(moon, elem)

    precision = row.get("birth_time_precision") or "unknown"
    has_exact_time = precision in ["exact", "approximate"] and row.get("ascendant_longitude") is not None

    def resolve_text(interp_id: str) -> str:
        res = content_library.resolve(interpretation_id=interp_id, context="self", locale=locale, seed=str(user_id))
        return res.text.strip() if res else ""

    layers = []

    # ----------------------------------------------------
    # LAYER 1: ვინ ხარ სინამდვილეში (Who You Truly Are)
    # ----------------------------------------------------
    sun_text = resolve_text(f"self.identity.sun_{sun}.v1")
    moon_text = resolve_text(f"self.emotional.moon_{moon}.v1")
    rising_text = resolve_text(f"self.persona.rising_{rising}.v1") if has_exact_time and rising else ""
    synthesis_text = resolve_text(f"self.synthesis.element_dynamic.{sun_el}_{moon_el}.v1")

    layer_1_items = [
        {
            "id": "sun_identity",
            "point": "მზე",
            "sign": GEORGIAN_SIGNS.get(sun, sun),
            "label": "ცნობიერი ეგო და მოტივაცია",
            "sign_badge": f"მზე {GEORGIAN_SIGNS_LOCATIVE.get(sun, sun)}",
            "text": sun_text or f"შენი ცნობიერი ეგო და ცხოვრებისეული ამბიცია ფორმირდება {GEORGIAN_SIGNS_LOCATIVE.get(sun, sun)} ენერგიით."
        },
        {
            "id": "moon_emotional",
            "point": "მთვარე",
            "sign": GEORGIAN_SIGNS.get(moon, moon),
            "label": "ემოციური მოთხოვნილებები და შინაგანი სამყარო",
            "sign_badge": f"მთვარე {GEORGIAN_SIGNS_LOCATIVE.get(moon, moon)}",
            "text": moon_text or f"ქვეცნობიერი უსაფრთხოება და ემოციური რეაქციები ეფუძნება {GEORGIAN_SIGNS_LOCATIVE.get(moon, moon)} თვისებებს."
        }
    ]

    if has_exact_time and rising:
        layer_1_items.append({
            "id": "rising_persona",
            "point": "ასცენდენტი",
            "sign": GEORGIAN_SIGNS.get(rising, rising),
            "label": "სოციალური ნიღაბი და პირველი შთაბეჭდილება",
            "sign_badge": f"ასცენდენტი {GEORGIAN_SIGNS_LOCATIVE.get(rising, rising)}",
            "text": rising_text or f"გარე სამყაროსთან შეხებისას პირველ რიგში ვლინდება {GEORGIAN_SIGNS_LOCATIVE.get(rising, rising)} ნიღაბი."
        })
    else:
        layer_1_items.append({
            "id": "rising_missing",
            "point": "ასცენდენტი",
            "sign": "უცნობია",
            "label": "სოციალური ნიღაბი (მოითხოვს ზუსტ დროს)",
            "sign_badge": "დაბადების დრო უცნობია",
            "text": "ასცენდენტის და პირველი შთაბეჭდილების ზუსტი გამოთვლისთვის საჭიროა დაბადების საათი და წუთი. შეავსე პროფილი ზუსტი დროით."
        })

    if synthesis_text:
        layer_1_items.append({
            "id": "sun_moon_synthesis",
            "point": "სინთეზი",
            "sign": f"{GEORGIAN_ELEMENTS.get(sun_el, sun_el)} × {GEORGIAN_ELEMENTS.get(moon_el, moon_el)}",
            "label": "მზე-მთვარის შინაგანი ურთიერთქმედება",
            "sign_badge": f"{GEORGIAN_ELEMENTS.get(sun_el, sun_el)} / {GEORGIAN_ELEMENTS.get(moon_el, moon_el)}",
            "text": synthesis_text
        })

    layers.append({
        "layer_id": "layer_1",
        "number": 1,
        "title": "ვინ ხარ სინამდვილეში",
        "subtitle": "ცნობიერი ეგო, ემოციური ბირთვი და პირველი შთაბეჭდილება",
        "summary": "შენი პიროვნების ფუნდამენტური სამკუთხედი: რასაც გარეთ აჩვენებ, რას განიცდი შინაგანად და რა არის შენი შინაგანი ბრძოლა.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["მზე", "მთვარე", "ასცენდენტი", "მზე-მთვარის სინთეზი"],
        "items": layer_1_items
    })

    # ----------------------------------------------------
    # LAYER 2: როგორ აზროვნებ (How You Think)
    # ----------------------------------------------------
    merc_text = resolve_text(f"self.cognition.mercury_{mercury}.v1")
    layer_2_items = [
        {
            "id": "mercury_cognition",
            "point": "მერკური",
            "sign": GEORGIAN_SIGNS.get(mercury, mercury),
            "label": "აზროვნებისა და კომუნიკაციის სტილი",
            "sign_badge": f"მერკური {GEORGIAN_SIGNS_LOCATIVE.get(mercury, mercury)}",
            "text": merc_text or f"აზროვნებისა და ინფორმაციის გადამუშავების სტილი იმართება {GEORGIAN_SIGNS_LOCATIVE.get(mercury, mercury)} ინტელექტით."
        },
        {
            "id": "decision_making",
            "point": "გადაწყვეტილებები",
            "sign": GEORGIAN_MODALITIES.get(mod, mod),
            "label": "როგორ იღებ გადაწყვეტილებებს და კამათობ",
            "sign_badge": f"მოდალობა: {GEORGIAN_MODALITIES.get(mod, mod)}",
            "text": (
                "ინიციატორი ხარ — გადაწყვეტილებას სწრაფად იღებ და მოქმედებ, თუმცა დეტალების მოთმინება ხშირად გაკლია."
                if mod == "cardinal" else
                "ფიქსირებული პოზიცია გაქვს — სანამ საკუთარ თავს არ დაარწმუნებ, პოზიციას არ იცვლი, თუმცა შეცდომის აღიარება გიჭირს."
                if mod == "fixed" else
                "მოქნილი და ადაპტური ხარ — ყველა მხარის არგუმენტს ხედავ, თუმცა საბოლოო არჩევანის გაკეთებისას ხშირად ყოყმანობ."
            )
        }
    ]
    layers.append({
        "layer_id": "layer_2",
        "number": 2,
        "title": "როგორ აზროვნებ",
        "subtitle": "მერკური, გადაწყვეტილების მიღება და კამათის სტილი",
        "summary": "ინტელექტუალური სტილი, ლოგიკა, რამდენად სწრაფად ან ღრმად აანალიზებ და რა არის შენი სუსტი წერტილი დისკუსიაში.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["მერკური", "ლოგიკა", "გადაწყვეტილებები", "სიტყვიერი იარაღი"],
        "items": layer_2_items
    })

    # ----------------------------------------------------
    # LAYER 3: როგორ გიყვარს (How You Love)
    # ----------------------------------------------------
    venus_text = resolve_text(f"self.relation.venus_{venus}.v1")
    layer_3_items = [
        {
            "id": "venus_attraction",
            "point": "ვენერა",
            "sign": GEORGIAN_SIGNS.get(venus, venus),
            "label": "მიზიდულობის კოდი და სიყვარულის ენა",
            "sign_badge": f"ვენერა {GEORGIAN_SIGNS_LOCATIVE.get(venus, venus)}",
            "text": venus_text or f"შენს რომანტიკულ და ესთეტიკურ მიზიდულობას განსაზღვრავს {GEORGIAN_SIGNS_LOCATIVE.get(venus, venus)} ვენერა."
        },
        {
            "id": "mars_passion",
            "point": "მარსი",
            "sign": GEORGIAN_SIGNS.get(mars, mars),
            "label": "ვნება და ნადირობის ინსტინქტი",
            "sign_badge": f"მარსი {GEORGIAN_SIGNS_LOCATIVE.get(mars, mars)}",
            "text": f"როცა ადამიანი მოგწონს, შენი ვნება და ინიციატივა {GEORGIAN_SIGNS_LOCATIVE.get(mars, mars)} მარსის ენერგიით ვლინდება — არ გიყვარს გაურკვევლობა."
        },
        {
            "id": "relationship_turnoffs",
            "point": "Turn-Offs",
            "sign": GEORGIAN_SIGNS.get(venus, venus),
            "label": "რა კლავს სიმპათიას ურთიერთობაში",
            "sign_badge": "გამაღიზიანებელი ქცევები",
            "text": "ყველაზე მეტად გაღიზიანებს თავისუფლების შეზღუდვა, უმადურობა, ზედაპირული დრამა და როცა პარტნიორი საკუთარ სიტყვას არ აფასებს."
        }
    ]
    layers.append({
        "layer_id": "layer_3",
        "number": 3,
        "title": "როგორ გიყვარს",
        "subtitle": "ვენერა, მიზიდულობა, ვნება და ურთიერთობის გამაღიზიანებლები",
        "summary": "რა გხიბლავს სინამდვილეში ადამიანში, როგორ გამოხატავ სიყვარულს და რა ერთი ქცევა კლავს შენში სიმპათიას წამიერად.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["ვენერა", "მარსი", "მიზიდულობა", "Turn-Offs"],
        "items": layer_3_items
    })

    # ----------------------------------------------------
    # LAYER 4: როგორ მოქმედებ (How You Act)
    # ----------------------------------------------------
    mars_text = resolve_text(f"self.action.mars_{mars}.v1")
    layer_4_items = [
        {
            "id": "mars_action",
            "point": "მარსი",
            "sign": GEORGIAN_SIGNS.get(mars, mars),
            "label": "მოტივაცია, ენერგია და მიზნისკენ სწრაფვა",
            "sign_badge": f"მარსი {GEORGIAN_SIGNS_LOCATIVE.get(mars, mars)}",
            "text": mars_text or f"მოქმედების სტილი, ფიზიკური გამძლეობა და ბრძოლისუნარიანობა ეფუძნება {GEORGIAN_SIGNS_LOCATIVE.get(mars, mars)} მარსს."
        },
        {
            "id": "anger_style",
            "point": "ბრაზი",
            "sign": GEORGIAN_ELEMENTS.get(elem, elem),
            "label": "ბრაზის გამოხატვა და სირთულეების გადალახვა",
            "sign_badge": f"სტიქია: {GEORGIAN_ELEMENTS.get(elem, elem)}",
            "text": (
                "ფეთქებადი ხარ — ბრაზი მყისიერად ამოხეთქავს, თუმცა სწრაფადვე მშვიდდები."
                if elem == "fire" else
                "თოკავ ემოციებს — გარეგნულად სიმშვიდეს ინარჩუნებ, მაგრამ წყენას დიდი ხნით იმახსოვრებ."
                if elem == "earth" else
                "ვერბალურად იცავ თავს — სიტყვიერად არბილებ ან ირონიით პასუხობ, თუმცა შინაგანად იფიტები."
                if elem == "air" else
                "ღრმად განიცდი — წყენას საკუთარ თავში კეტავ და დისტანცირდები, სანამ არ იგრძნობ, რომ უსაფრთხოდ ხარ."
            )
        }
    ]
    layers.append({
        "layer_id": "layer_4",
        "number": 4,
        "title": "როგორ მოქმედებ",
        "subtitle": "მარსი, მოტივაცია, ბრაზის გამოხატვა და დაბრკოლებები",
        "summary": "რა გაძლევს მოტივაციას, რა ტემპით მუშაობ, როგორ გამოხატავ გაღიზიანებას და როგორ უმკლავდები წნეხს.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["მარსი", "მოტივაცია", "ბრაზი", "გამძლეობა"],
        "items": layer_4_items
    })

    # ----------------------------------------------------
    # LAYER 5: შენი ჩრდილოვანი მხარე (Your Shadow Side)
    # ----------------------------------------------------
    layer_5_items = [
        {
            "id": "saturn_fears",
            "point": "სატურნი",
            "sign": GEORGIAN_SIGNS.get(saturn, saturn) if saturn else "შეზღუდვა",
            "label": "სატურნი: შიშები, შეზღუდვები და თვითკრიტიკა",
            "sign_badge": f"სატურნი {GEORGIAN_SIGNS_LOCATIVE.get(saturn, saturn)}" if saturn else "სატურნი",
            "text": f"შენი შინაგანი კრიტიკოსი {GEORGIAN_SIGNS_LOCATIVE.get(saturn, saturn)} სატურნით ფორმირდება: ყველაზე მეტად გეშინია არაკომპეტენტურობის და კონტროლის დაკარგვის."
        },
        {
            "id": "pluto_control",
            "point": "პლუტონი",
            "sign": GEORGIAN_SIGNS.get(pluto, pluto) if pluto else "კონტროლი",
            "label": "პლუტონი: კონტროლი, ეჭვიანობა და ტრანსფორმაცია",
            "sign_badge": f"პლუტონი {GEORGIAN_SIGNS_LOCATIVE.get(pluto, pluto)}" if pluto else "პლუტონი",
            "text": "გაქვს ღრმა მოთხოვნილება, სიტუაციას სრულად ფლობდე. როცა ადამიანებს ბოლომდე არ ენდობი, ფარულ დისტანციას იცავ."
        },
        {
            "id": "neptune_escapism",
            "point": "ნეპტუნი",
            "sign": GEORGIAN_SIGNS.get(neptune, neptune) if neptune else "ილუზია",
            "label": "ნეპტუნი: გაქცევის მექანიზმები და ილუზიები",
            "sign_badge": f"ნეპტუნი {GEORGIAN_SIGNS_LOCATIVE.get(neptune, neptune)}" if neptune else "ნეპტუნი",
            "text": "როცა რეალობა მეტისმეტად უხეში ხდება, ფანტაზიებში, იზოლაციაში ან იდეალიზაციაში გაქცევა შენი თავდაცვის ინსტინქტია."
        },
        {
            "id": "self_sabotage",
            "point": "საბოტაჟი",
            "sign": "პატერნი",
            "label": "გაუცნობიერებელი თვითსაბოტაჟის ხაფანგი",
            "sign_badge": "ფსიქოლოგიური პატერნი",
            "text": "ხშირად იწყებ საქმეს ან ურთიერთობას დიდი ენთუზიაზმით, მაგრამ როგორც კი რუტინული პასუხისმგებლობა იწყება, ჰორიზონტისკენ გარბიხარ."
        }
    ]
    layers.append({
        "layer_id": "layer_5",
        "number": 5,
        "title": "შენი ჩრდილოვანი მხარე",
        "subtitle": "სატურნი, პლუტონი, ნეპტუნი და თვითსაბოტაჟის პატერნები",
        "summary": "ყველაზე ღრმა და მტკივნეული სიმართლე: რის გეშინია გაუცნობიერებლად, სად ცდილობ სხვების კონტროლს და სად აზიანებ საკუთარ თავს.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["სატურნი", "პლუტონი", "ნეპტუნი", "თვითსაბოტაჟი"],
        "items": layer_5_items
    })

    # ----------------------------------------------------
    # LAYER 6: შენი შინაგანი კონფიგურაცია (Inner Configurations)
    # ----------------------------------------------------
    aspect_candidate_pairs = [
        ("sun", row.get("sun_longitude"), "saturn", row.get("saturn_longitude")),
        ("venus", row.get("venus_longitude"), "pluto", row.get("pluto_longitude")),
        ("mars", row.get("mars_longitude"), "saturn", row.get("saturn_longitude")),
        ("moon", row.get("moon_longitude"), "mercury", row.get("mercury_longitude")),
        ("sun", row.get("sun_longitude"), "jupiter", row.get("jupiter_longitude")),
        ("mars", row.get("mars_longitude"), "jupiter", row.get("jupiter_longitude")),
    ]

    detected_aspect_items = []
    for b1, l1, b2, l2 in aspect_candidate_pairs:
        if l1 is not None and l2 is not None:
            asp = detect_aspect(b1, l1, b2, l2)
            if asp:
                b1_ka = GEORGIAN_BODIES.get(b1, b1.upper())
                b2_ka = GEORGIAN_BODIES.get(b2, b2.upper())
                asp_ka = GEORGIAN_ASPECT_NAMES.get(asp.aspect_type, asp.aspect_type)
                
                # Contextual explanation based on pair and aspect
                pair_key = frozenset([b1, b2])
                if pair_key == frozenset(["sun", "saturn"]):
                    desc = "შენი ეგო მუდმივ გამოცდას გადის პასუხისმგებლობით: ადრეული ასაკიდანვე გრძნობდი ვალდებულებას, რომ იმაზე სერიოზული ყოფილიყავი, ვიდრე იყავი."
                elif pair_key == frozenset(["venus", "pluto"]):
                    desc = "ურთიერთობებში ნახევარზომებს ვერ იტან: შენი სიყვარული ინტენსიურია, ხშირად ობსესიური, და უღალატობას სიკვდილ-სიცოცხლის ფასად მოითხოვ."
                elif pair_key == frozenset(["mars", "saturn"]):
                    desc = "გაზი და მუხრუჭი ერთდროულად: მოქმედების წყურვილი ეჯახება შინაგან თვითკრიტიკას, თუმცა ეს გაძლევს რკინის გამძლეობას, როცა მიზანს დაისახავ."
                elif pair_key == frozenset(["moon", "mercury"]):
                    desc = "გრძნობებისა და გონების მუდმივი დიალოგი: ყოველ ემოციას ლოგიკურ ახსნას უძებნი, რაც გამჭრიახობას გმატებს, თუმცა გულუბრყვილო სიმშვიდეს გაკარგვინებს."
                elif pair_key == frozenset(["sun", "jupiter"]):
                    desc = "დიდი ამბიციები და ოპტიმიზმი: სამყაროსგან ყოველთვის მეტს ელი, ვიდრე ჩვეულებრივი სტანდარტია; მთავარია, რეალობის გრძნობა არ დაკარგო."
                elif pair_key == frozenset(["mars", "jupiter"]):
                    desc = "ენერგიის ძლიერი მუხტი: რისკი გიზიდავს და თავგადასავლებში ადვილად ერთვები, თუმცა ზოგჯერ საკუთარ ძალებს გადააფასებ ხოლმე."
                else:
                    desc = f"{b1_ka}-სა და {b2_ka}-ს {asp_ka} ქმნის ძლიერ ნატალურ ბმულს შენს პირად რუკაში."

                detected_aspect_items.append({
                    "id": f"aspect_{b1}_{b2}_{asp.aspect_type}",
                    "point": f"{b1_ka} {asp_ka} {b2_ka}",
                    "sign": f"დაშორება {asp.actual_distance:.1f}°",
                    "label": f"{b1_ka}–{b2_ka}-ს {asp_ka}",
                    "sign_badge": f"{asp_ka} · ორბისი {asp.orb_diff:.1f}°",
                    "text": desc
                })

    if not detected_aspect_items:
        detected_aspect_items.append({
            "id": "aspect_clear",
            "point": "ჰარმონიული რუკა",
            "sign": "აქტიური დაძაბულობის გარეშე",
            "label": "დაძაბული ასპექტების არარსებობა",
            "sign_badge": "ჰარმონიული ბალანსი",
            "text": "შენს რუკაში მზე-სატურნის, ვენერა-პლუტონის ან მარსი-სატურნის მწვავე დაძაბული ასპექტები არ ფიქსირდება — შენი ენერგია უფრო ბუნებრივად და დაბრკოლებების გარეშე მიედინება."
        })

    layers.append({
        "layer_id": "layer_6",
        "number": 6,
        "title": "შენი შინაგანი კონფიგურაცია",
        "subtitle": "ნატალური ასპექტები და პლანეტარული შეერთებები",
        "summary": "რეალური გრადუსობრივი ასპექტები შენს დაბადების რუკაში: მზე-სატურნი, ვენერა-პლუტონი, მარსი-სატურნი და მთვარე-მერკური.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["ნატალური ასპექტები", "ორბისები", "შეერთება", "კვადრატურა"],
        "items": detected_aspect_items
    })

    # ----------------------------------------------------
    # LAYER 7: შენი პირადი სახელმძღვანელო (Your Personal Manual)
    # ----------------------------------------------------
    elem_text = resolve_text(f"self.element.{elem}_dominant.v1")
    mod_text = resolve_text(f"self.modality.{mod}_dominant.v1")
    verdict_text = resolve_text(f"self.verdict.archetype_{mod}_{elem}.v1")

    layer_7_items = [
        {
            "id": "element_dominant",
            "point": "სტიქია",
            "sign": GEORGIAN_ELEMENTS.get(elem, elem),
            "label": "წამყვანი სტიქია და ენერგიის საწვავი",
            "sign_badge": f"{GEORGIAN_ELEMENTS.get(elem, elem)} დომინანტი",
            "text": elem_text or f"შენი ენერგიის მთავარი საწვავი არის {GEORGIAN_ELEMENTS.get(elem, elem)} სტიქია."
        },
        {
            "id": "modality_dominant",
            "point": "მოდალობა",
            "sign": GEORGIAN_MODALITIES.get(mod, mod),
            "label": "ცხოვრების დინამიკა და მოქმედების ტემპი",
            "sign_badge": f"{GEORGIAN_MODALITIES.get(mod, mod)} მოდალობა",
            "text": mod_text or f"ცხოვრებისეული ტემპი ეფუძნება {GEORGIAN_MODALITIES.get(mod, mod)} რიტმს."
        },
        {
            "id": "core_verdict",
            "point": "ვერდიქტი",
            "sign": f"{GEORGIAN_MODALITIES.get(mod, mod)} {GEORGIAN_ELEMENTS.get(elem, elem)}",
            "label": "ცხოვრების მთავარი ვერდიქტი და არქეტიპი",
            "sign_badge": "მაკრო ვერდიქტი",
            "text": verdict_text or "თავისუფლებას იმდენად უფრთხილდები, რომ მის შესანარჩუნებლად ნებისმიერ სიღრმეს გაურბიხარ."
        },
        {
            "id": "user_manual",
            "point": "ინსტრუქცია",
            "sign": "User Manual",
            "label": "როგორ უნდა მოგექცნენ სხვები (ინსტრუქცია)",
            "sign_badge": "მომხმარებლის სახელმძღვანელო",
            "text": "1. არასდროს მოითხოვო მყისიერი პასუხი, როცა გაბრაზებულია. 2. აჩვენე გულწრფელობა — სიყალბეს წამებში გრძნობს. 3. მიეცი პირადი სივრცე და ნურასდროს აიძულებ რუტინას."
        }
    ]

    layers.append({
        "layer_id": "layer_7",
        "number": 7,
        "title": "შენი პირადი სახელმძღვანელო",
        "subtitle": "სტიქიები, მოდალობა, ვერდიქტი და მომხმარებლის სახელმძღვანელო",
        "summary": "სრული სინთეზი: ენერგიის საწვავი, ცხოვრების მთავარი ვერდიქტი და პრაქტიკული ინსტრუქცია სხვებისთვის — როგორ მოგექცნენ.",
        "is_locked": False,
        "star_cost": 5,
        "topics": ["სტიქია", "მოდალობა", "ვერდიქტი", "User Manual"],
        "items": layer_7_items
    })

    return {
        "has_data": True,
        "data_quality": {
            "has_birth_data": True,
            "has_exact_time": has_exact_time,
            "precision": precision,
            "missing_fields": [] if has_exact_time else ["birth_time"]
        },
        "layers": layers
    }
