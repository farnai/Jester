import re
import uuid
import psycopg
from psycopg.rows import dict_row

from backend.app.geo.models import CanonicalCity, CanonicalCountry, CitySearchResult

# Georgian Mkhedruli script to Latin transliteration
GEORGIAN_TO_LATIN: dict[str, str] = {
    "ა": "a", "ბ": "b", "გ": "g", "დ": "d", "ე": "e", "ვ": "v", "ზ": "z",
    "თ": "t", "ი": "i", "კ": "k", "ლ": "l", "მ": "m", "ნ": "n", "ო": "o",
    "პ": "p", "ჟ": "zh", "რ": "r", "ს": "s", "ტ": "t", "უ": "u", "ფ": "p",
    "ქ": "k", "ღ": "gh", "ყ": "q", "შ": "sh", "ჩ": "ch", "ც": "ts",
    "ძ": "dz", "წ": "ts", "ჭ": "ch", "ხ": "kh", "ჯ": "j", "ჰ": "h",
}

# Common Georgian localized names for Georgian launch cities
GEORGIAN_CITY_NAMES: dict[str, str] = {
    "Tbilisi": "თბილისი",
    "Batumi": "ბათუმი",
    "Kutaisi": "ქუთაისი",
    "Rustavi": "რუსთავი",
    "Gori": "გორი",
    "Telavi": "თელავი",
    "Zugdidi": "ზუგდიდი",
    "Poti": "ფოთი",
    "Kobuleti": "ქობულეთი",
    "Khashuri": "ხაშური",
    "Gurjaani": "გურჯაანი",
    "Qvareli": "ყვარელი",
    "Akhaltsikhe": "ახალციხე",
    "Borjomi": "ბორჯომი",
    "Samtredia": "სამტრედია",
    "Senaki": "სენაკი",
    "Zestafoni": "ზესტაფონი",
    "Marneuli": "მარნეული",
    "Gardabani": "გარდაბანი",
    "Ozurgeti": "ოზურგეთი",
    "Kaspi": "კასპი",
    "Chiatura": "ჭიათურა",
    "Tskaltubo": "წყალტუბო",
    "Sagarejo": "საგარეჯო",
    "Dusheti": "დუშეთი",
    "Mtskheta": "მცხეთა",
    "Stepantsminda": "სტეფანწმინდა",
    "Signagi": "სიღნაღი",
    "Bolnisi": "ბოლნისი",
    "Akhalkalaki": "ახალქალაქი",
    "Ninotsminda": "ნინოწმინდა",
    "Dmanisi": "დმანისი",
    "Tsalka": "წალკა",
    "Kareli": "ქარელი",
    "Lagodekhi": "ლაგოდეხი",
    "Dedoplistskaro": "დედოფლისწყარო",
    "Tsalenjikha": "წალენჯიხა",
    "Chkhorotsku": "ჩხოროწყუ",
    "Martvili": "მარტვილი",
    "Khobi": "ხობი",
    "Abasha": "აბაშა",
    "Vani": "ვანი",
    "Baghdati": "ბაღდათი",
    "Kharagauli": "ხარაგაული",
    "Terjola": "თერჯოლა",
    "Tkibuli": "ტყიბული",
    "Ambrolauri": "ამბროლაური",
    "Oni": "ონი",
    "Tsageri": "ცაგერი",
    "Lentekhi": "ლენტეხი",
    "Mestia": "მესტია",
    "Chokhatauri": "ჩოხატაური",
    "Lanchkhuti": "ლანჩხუთი",
    "Keda": "ქედა",
    "Shuakhevi": "შუახევი",
    "Khulo": "ხულო",
    "Sukhumi": "სოხუმი",
    "Gagra": "გაგრა",
    "Gudauta": "გუდაუთა",
    "Ochamchire": "ოჩამჩირე",
    "Tkvarcheli": "ტყვარჩელი",
    "Gali": "გალი",
    "Tskhinvali": "ცხინვალი",
    "Java": "ჯავა",
    "Akhalgori": "ახალგორი",
    "Gudauri": "გუდაური",
    "Bakuriani": "ბაკურიანი",
    "Ureki": "ურეკი",
    "Anaklia": "ანაკლია",
    "Sairme": "საირმე",
    "Abastumani": "აბასთუმანი",
    "Surami": "სურამი",
    "Manglisi": "მანგლისი",
    "Kojori": "კოჯორი",
}

# Major international hubs mapped from Georgian script
GEORGIAN_FOREIGN_CITIES: dict[str, str] = {
    "ნიუ იორკი": "new york",
    "ნიუ-იორკი": "new york",
    "ლონდონი": "london",
    "პარიზი": "paris",
    "ბერლინი": "berlin",
    "რომი": "rome",
    "ტოკიო": "tokyo",
    "მადრიდი": "madrid",
    "კიევი": "kyiv",
    "ვენა": "vienna",
    "ათენი": "athens",
    "ვარშავა": "warsaw",
    "პრაღა": "prague",
    "ლისაბონი": "lisbon",
    "ამსტერდამი": "amsterdam",
    "ბრიუსელი": "brussels",
    "სტოკჰოლმი": "stockholm",
    "ოსლო": "oslo",
    "ჰელსინკი": "helsinki",
    "კოპენჰაგენი": "copenhagen",
    "დუბლინი": "dublin",
}

POPULAR_GE_HUBS: list[str] = [
    "Tbilisi",
    "Batumi",
    "Kutaisi",
    "Rustavi",
    "Gori",
    "Telavi",
    "Zugdidi",
    "Poti",
    "Kobuleti",
    "Khashuri",
]


def transliterate_georgian(text: str) -> str:
    """
    Transliterates Georgian text to Latin ASCII representation.
    """
    res = []
    for char in text.lower():
        res.append(GEORGIAN_TO_LATIN.get(char, char))
    return "".join(res)


def _format_display_name(name: str, state_or_region: str | None, country_name: str) -> str:
    if state_or_region and state_or_region.lower() != name.lower():
        return f"{name}, {state_or_region}, {country_name}"
    return f"{name}, {country_name}"


def _get_search_result_display_name(name_ascii: str, name: str, country_code: str) -> str:
    """
    Produces primary display name with Georgian script for Georgian cities.
    e.g. 'თბილისი / Tbilisi' or 'Gurjaani'
    """
    if country_code == "GE":
        ka = GEORGIAN_CITY_NAMES.get(name_ascii) or GEORGIAN_CITY_NAMES.get(name)
        if ka:
            return f"{ka} / {name_ascii}"
    return name_ascii or name


def get_city_by_id(city_id: uuid.UUID, db: psycopg.Connection) -> CanonicalCity | None:
    """
    Retrieves canonical city record by UUID including joined country information.
    Returns None if the city does not exist.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT c.id, c.source_id, c.country_id, c.country_code,
                   co.name as country_name, c.name, c.name_ascii,
                   c.state_or_region, c.latitude, c.longitude, c.timezone,
                   c.is_major_city
            FROM public.cities c
            JOIN public.countries co ON co.id = c.country_id
            WHERE c.id = %s;
            """,
            (city_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        display_name = _format_display_name(
            name=row["name"],
            state_or_region=row["state_or_region"],
            country_name=row["country_name"],
        )

        return CanonicalCity(
            id=row["id"],
            source_id=row["source_id"],
            country_id=row["country_id"],
            country_code=row["country_code"],
            country_name=row["country_name"],
            name=row["name"],
            name_ascii=row["name_ascii"],
            state_or_region=row["state_or_region"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            timezone=row["timezone"],
            is_major_city=row["is_major_city"],
            display_name=display_name,
        )


def get_country_by_id(country_id: uuid.UUID, db: psycopg.Connection) -> CanonicalCountry | None:
    """
    Retrieves canonical country record by UUID.
    Returns None if the country does not exist.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, source_id, iso2, name, native_name, phone_code
            FROM public.countries
            WHERE id = %s;
            """,
            (country_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return CanonicalCountry(**row)


def list_countries(db: psycopg.Connection) -> list[CanonicalCountry]:
    """
    Returns all canonical countries ordered alphabetically.
    """
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT id, source_id, iso2, name, native_name, phone_code
            FROM public.countries
            ORDER BY name ASC;
            """
        )
        rows = cur.fetchall()
        return [CanonicalCountry(**r) for r in rows]


def get_popular_cities(limit: int, db: psycopg.Connection) -> list[CitySearchResult]:
    """
    Returns the curated popular cities list for empty search state.
    For the Georgian launch, prioritizes the top 10 Georgian hubs in exact order.
    """
    capped_limit = min(max(1, limit), 20)
    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT c.id as city_id, c.name, c.name_ascii, co.name as country_name,
                   c.country_code, c.state_or_region as region
            FROM public.cities c
            JOIN public.countries co ON co.id = c.country_id
            WHERE c.country_code = 'GE' AND c.name_ascii = ANY(%s)
            ORDER BY CASE c.name_ascii
                WHEN 'Tbilisi' THEN 1
                WHEN 'Batumi' THEN 2
                WHEN 'Kutaisi' THEN 3
                WHEN 'Rustavi' THEN 4
                WHEN 'Gori' THEN 5
                WHEN 'Telavi' THEN 6
                WHEN 'Zugdidi' THEN 7
                WHEN 'Poti' THEN 8
                WHEN 'Kobuleti' THEN 9
                WHEN 'Khashuri' THEN 10
                ELSE 20 END
            LIMIT %s;
            """,
            (POPULAR_GE_HUBS, capped_limit),
        )
        rows = cur.fetchall()
        return [
            CitySearchResult(
                city_id=r["city_id"],
                name=r["name_ascii"] or r["name"],
                display_name=_get_search_result_display_name(r["name_ascii"], r["name"], r["country_code"]),
                country_name=r["country_name"],
                country_code=r["country_code"],
                region=r["region"],
            )
            for r in rows
        ]


def search_cities(query: str, limit: int, db: psycopg.Connection) -> list[CitySearchResult]:
    """
    Searches canonical cities with high-performance PostgreSQL indexed search and ranking.
    Prioritizes:
    1. Exact city-name match
    2. Prefix match
    3. Transliterated/ASCII match (including Georgian Mkhedruli)
    4. Partial substring match
    5. Georgian launch priority & Major city flags
    """
    clean_q = re.sub(r"\s+", " ", query.strip())
    if len(clean_q) < 2:
        return []

    capped_limit = min(max(1, limit), 20)
    q_lower = clean_q.lower()

    # Collect search variants
    exact_terms = {q_lower}
    
    # Check known foreign city mappings in Georgian (e.g. 'ნიუ იორკი' -> 'new york')
    if q_lower in GEORGIAN_FOREIGN_CITIES:
        exact_terms.add(GEORGIAN_FOREIGN_CITIES[q_lower])

    # Transliterate Georgian script
    translit_q = transliterate_georgian(clean_q)
    if translit_q != q_lower:
        exact_terms.add(translit_q)
        # Strip Georgian nominative suffix '-i' for foreign cities (e.g. 'londoni' -> 'london')
        if translit_q.endswith("i") and len(translit_q) > 3:
            exact_terms.add(translit_q[:-1])
        # Handle 'q' vs 'k' in Georgian transliteration (e.g. 'qvareli' vs 'kvareli')
        if "q" in translit_q:
            exact_terms.add(translit_q.replace("q", "k"))
        if "k" in translit_q:
            exact_terms.add(translit_q.replace("k", "q"))

    prefix_terms = [f"{term}%" for term in exact_terms]
    contains_terms = [f"%{term}%" for term in exact_terms]
    exact_list = list(exact_terms)

    with db.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT c.id as city_id, c.name, c.name_ascii, co.name as country_name,
                   c.country_code, c.state_or_region as region,
                   (
                       CASE
                           WHEN lower(c.name_ascii) = ANY(%s) OR lower(c.name) = ANY(%s) THEN 100
                           WHEN lower(c.name_ascii) LIKE ANY(%s) OR lower(c.name) LIKE ANY(%s) THEN 75
                           ELSE 40
                       END
                       + CASE WHEN c.country_code = 'GE' THEN 15 ELSE 0 END
                       + CASE WHEN c.is_major_city THEN 10 ELSE 0 END
                   ) AS match_rank
            FROM public.cities c
            JOIN public.countries co ON co.id = c.country_id
            WHERE c.name_ascii ILIKE ANY(%s)
               OR c.name ILIKE ANY(%s)
            ORDER BY match_rank DESC,
                     CASE WHEN c.country_code = 'GE' THEN 0 ELSE 1 END ASC,
                     c.is_major_city DESC,
                     c.name_ascii ASC
            LIMIT %s;
            """,
            (exact_list, exact_list, prefix_terms, prefix_terms, contains_terms, contains_terms, capped_limit),
        )
        rows = cur.fetchall()

        return [
            CitySearchResult(
                city_id=r["city_id"],
                name=r["name_ascii"] or r["name"],
                display_name=_get_search_result_display_name(r["name_ascii"], r["name"], r["country_code"]),
                country_name=r["country_name"],
                country_code=r["country_code"],
                region=r["region"],
            )
            for r in rows
        ]
