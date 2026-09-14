"""
JESTER — Controlled Canonical Location Backfill Script
Backfills existing rows in public.birth_data and public.profiles.
Strict Rules:
- Matches birth_data using (latitude, longitude, timezone, place_label).
- Matches profiles.city only when unambiguous.
- Ambiguous cities (e.g. 'Springfield') are NEVER guessed.
- Reports exact metrics: total, mapped, unmatched, ambiguous, unchanged.
"""
import os
import sys
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")

# Common Georgian localized names to canonical city names
GE_LOCALIZED_MAP = {
    "თბილისი": "Tbilisi",
    "ბათუმი": "Batumi",
    "ქუთაისი": "Kutaisi",
    "რუსთავი": "Rust’avi",
    "თელავი": "Telavi",
    "ზუგდიდი": "Zugdidi",
    "გორი": "Gori",
    "ფოთი": "P’ot’i",
    "ყვარელი": "Qvareli",
    "გურჯაანი": "Gurjaani",
    "ახალციხე": "Akhaltsikhe",
    "სამტრედია": "Samtredia",
    "ხაშური": "Khashuri",
    "ბორჯომი": "Borjomi",
    "ქობულეთი": "Kobuleti",
    "ოზურგეთი": "Ozurgeti",
    "სენაკი": "Senak’i",
    "ჭიათურა": "Chiat’ura",
    "ზესტაფონი": "Zestap’oni",
    "საგარეჯო": "Sagarejo",
    "სიღნაღი": "Sighnaghi",
    "დუშეთი": "Dusheti",
    "სტეფანწმინდა": "Step’antsminda",
}


def run_backfill():
    conn = psycopg.connect(DB_URL, autocommit=False, row_factory=dict_row)
    try:
        cur = conn.cursor()

        # -------------------------------------------------------------
        # 1. BACKFILL BIRTH DATA
        # -------------------------------------------------------------
        print("\n--- Auditing & Backfilling public.birth_data ---")
        cur.execute(
            """
            SELECT user_id, place_label, latitude, longitude, birth_timezone, birth_city_id
            FROM public.birth_data;
            """
        )
        bd_rows = cur.fetchall()

        bd_total = len(bd_rows)
        bd_mapped = 0
        bd_unmatched = 0
        bd_ambiguous = 0
        bd_unchanged = 0

        for r in bd_rows:
            uid = r["user_id"]
            if r["birth_city_id"] is not None:
                bd_unchanged += 1
                continue

            lat = r["latitude"]
            lon = r["longitude"]
            tz = r["birth_timezone"]
            label = r["place_label"] or ""

            # Check if Georgian localized name in label
            normalized_label_city = None
            for ge_name, en_name in GE_LOCALIZED_MAP.items():
                if ge_name in label:
                    normalized_label_city = en_name
                    break

            # Search by coordinates and timezone first
            matched_cities = []
            if lat is not None and lon is not None and tz:
                # Coordinate proximity check (within ~25km = ~0.25 degrees) and matching timezone
                cur.execute(
                    """
                    SELECT id, name, name_ascii, country_code, latitude, longitude, timezone
                    FROM public.cities
                    WHERE timezone = %s
                      AND abs(latitude - %s) < 0.25
                      AND abs(longitude - %s) < 0.25;
                    """,
                    (tz, lat, lon),
                )
                matched_cities = cur.fetchall()

            if len(matched_cities) == 1:
                # Unambiguous coordinate & timezone match
                best_city = matched_cities[0]
                cur.execute(
                    "UPDATE public.birth_data SET birth_city_id = %s WHERE user_id = %s;",
                    (best_city["id"], uid),
                )
                bd_mapped += 1
                print(f"  [Mapped birth_data] User {uid}: '{label}' -> {best_city['name']} ({best_city['country_code']})")
            elif len(matched_cities) > 1:
                # Disambiguate with label if possible
                label_matches = [
                    c for c in matched_cities
                    if (c["name"].lower() in label.lower() or
                        c["name_ascii"].lower() in label.lower() or
                        (normalized_label_city and c["name"].lower() == normalized_label_city.lower()))
                ]
                if len(label_matches) == 1:
                    best_city = label_matches[0]
                    cur.execute(
                        "UPDATE public.birth_data SET birth_city_id = %s WHERE user_id = %s;",
                        (best_city["id"], uid),
                    )
                    bd_mapped += 1
                    print(f"  [Mapped birth_data (Disambiguated)] User {uid}: '{label}' -> {best_city['name']} ({best_city['country_code']})")
                else:
                    bd_ambiguous += 1
                    print(f"  [Ambiguous birth_data] User {uid}: '{label}' matched {len(matched_cities)} cities with similar coordinates. Skipped.")
            else:
                # Try exact name match if coordinates didn't match
                if normalized_label_city:
                    cur.execute("SELECT id, name, country_code FROM public.cities WHERE country_code = 'GE' AND name = %s;", (normalized_label_city,))
                    name_matches = cur.fetchall()
                    if len(name_matches) == 1:
                        cur.execute("UPDATE public.birth_data SET birth_city_id = %s WHERE user_id = %s;", (name_matches[0]["id"], uid))
                        bd_mapped += 1
                        print(f"  [Mapped birth_data by name] User {uid}: '{label}' -> {name_matches[0]['name']}")
                    else:
                        bd_unmatched += 1
                        print(f"  [Unmatched birth_data] User {uid}: '{label}' could not be resolved.")
                else:
                    bd_unmatched += 1
                    print(f"  [Unmatched birth_data] User {uid}: '{label}' could not be resolved.")

        # -------------------------------------------------------------
        # 2. BACKFILL PROFILES
        # -------------------------------------------------------------
        print("\n--- Auditing & Backfilling public.profiles ---")
        cur.execute(
            """
            SELECT id, display_name, city, city_id
            FROM public.profiles;
            """
        )
        p_rows = cur.fetchall()

        p_total = len(p_rows)
        p_mapped = 0
        p_unmatched = 0
        p_ambiguous = 0
        p_unchanged = 0

        for r in p_rows:
            uid = r["id"]
            if r["city_id"] is not None:
                p_unchanged += 1
                continue

            city_text = (r["city"] or "").strip()
            if not city_text:
                p_unchanged += 1
                continue

            # Check localized Georgian map
            mapped_en_name = GE_LOCALIZED_MAP.get(city_text)
            lookup_name = mapped_en_name or city_text

            # Search in public.cities
            cur.execute(
                """
                SELECT id, name, name_ascii, country_code, state_or_region
                FROM public.cities
                WHERE name ILIKE %s OR name_ascii ILIKE %s;
                """,
                (lookup_name, lookup_name),
            )
            candidates = cur.fetchall()

            if len(candidates) == 1:
                # Exactly 1 city worldwide matches
                best_city = candidates[0]
                cur.execute(
                    "UPDATE public.profiles SET city_id = %s, city = %s WHERE id = %s;",
                    (best_city["id"], best_city["name"], uid),
                )
                p_mapped += 1
                print(f"  [Mapped profile] User {uid}: '{city_text}' -> {best_city['name']} ({best_city['country_code']})")
            elif len(candidates) > 1:
                # If mapped from Georgian dictionary, prefer Georgian country_code = 'GE'
                ge_cand = [c for c in candidates if c["country_code"] == "GE"]
                if mapped_en_name and len(ge_cand) == 1:
                    best_city = ge_cand[0]
                    cur.execute(
                        "UPDATE public.profiles SET city_id = %s, city = %s WHERE id = %s;",
                        (best_city["id"], best_city["name"], uid),
                    )
                    p_mapped += 1
                    print(f"  [Mapped profile (GE specific)] User {uid}: '{city_text}' -> {best_city['name']} (GE)")
                else:
                    p_ambiguous += 1
                    print(f"  [Ambiguous profile] User {uid}: '{city_text}' matches {len(candidates)} cities worldwide (e.g. {candidates[0]['name']}, {candidates[0]['country_code']}). NOT guessing.")
            else:
                p_unmatched += 1
                print(f"  [Unmatched profile] User {uid}: '{city_text}' not found in canonical dataset.")

        conn.commit()

        print("\n==================================================")
        print("BACKFILL SUMMARY REPORT")
        print("==================================================")
        print(f"Birth Data Total      : {bd_total}")
        print(f"  - Successfully Mapped: {bd_mapped}")
        print(f"  - Ambiguous (Skipped): {bd_ambiguous}")
        print(f"  - Unmatched          : {bd_unmatched}")
        print(f"  - Unchanged          : {bd_unchanged}")
        print("--------------------------------------------------")
        print(f"Profiles Total        : {p_total}")
        print(f"  - Successfully Mapped: {p_mapped}")
        print(f"  - Ambiguous (Skipped): {p_ambiguous}")
        print(f"  - Unmatched          : {p_unmatched}")
        print(f"  - Unchanged          : {p_unchanged}")
        print("==================================================")

    except Exception as e:
        conn.rollback()
        print(f"Error during backfill: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_backfill()
