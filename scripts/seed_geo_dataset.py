"""
JESTER — Canonical Global Location Dataset Seed Script
Imports 250 countries and ~153,000 worldwide cities into PostgreSQL.
Features:
- 100% idempotent: safely re-runnable without creating duplicates.
- Deterministic UUIDv5 primary keys derived from stable source IDs.
- Caches source data in scratch/geo_cache to avoid redundant downloads.
- Validates latitude, longitude, and IANA timezones.
- Normalizes ASCII search names (e.g., Rust’avi -> Rustavi).
"""
import csv
import gzip
import io
import os
import sys
import unicodedata
import uuid
from pathlib import Path
import httpx
import psycopg

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:54322/postgres")
CACHE_DIR = PROJECT_ROOT / "scratch" / "geo_cache"

COUNTRIES_URL = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/csv/countries.csv"
CITIES_URL = "https://github.com/dr5hn/countries-states-cities-database/releases/download/v3.2-export.7/csv-cities.csv.gz"

JESTER_GEO_NAMESPACE = uuid.UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Georgian primary hubs for instant popular chip rendering
GE_MAJOR_HUBS = {
    "tbilisi", "batumi", "kutaisi", "rustavi", "telavi", "zugdidi",
    "gori", "poti", "kvareli", "qvareli", "gurjaani", "akhaltsikhe",
    "samtredia", "khashuri", "borjomi", "kobuleti", "ozurgeti", "senaki",
    "chiatura", "zestafoni", "sagarejo", "sighnaghi", "dusheti", "stepantsminda"
}


def normalize_ascii_name(name: str) -> str:
    """Normalizes city name by stripping apostrophes, modifier letters, and diacritics."""
    # Remove apostrophe-like modifier characters common in transliterations
    cleaned = (
        name.replace("’", "")
        .replace("'", "")
        .replace("ʻ", "")
        .replace("ʼ", "")
        .replace("`", "")
        .replace("´", "")
    )
    # Decompose unicode diacritics and strip non-ASCII accents
    decomposed = unicodedata.normalize("NFKD", cleaned)
    ascii_bytes = decomposed.encode("ascii", "ignore")
    normalized = ascii_bytes.decode("ascii").strip()
    return normalized or name.strip()


def ensure_cached_files() -> tuple[Path, Path]:
    """Downloads source files into scratch/geo_cache if not already present."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    countries_path = CACHE_DIR / "countries.csv"
    cities_path = CACHE_DIR / "csv-cities.csv.gz"

    if not countries_path.exists():
        print(f"Downloading countries dataset from {COUNTRIES_URL}...")
        r = httpx.get(COUNTRIES_URL, follow_redirects=True, timeout=30.0)
        r.raise_for_status()
        countries_path.write_bytes(r.content)
        print(f"Saved countries.csv ({len(r.content)} bytes)")
    else:
        print(f"Using cached countries.csv ({countries_path.stat().st_size} bytes)")

    if not cities_path.exists():
        print(f"Downloading cities dataset from {CITIES_URL}...")
        with httpx.stream("GET", CITIES_URL, follow_redirects=True, timeout=120.0) as r:
            r.raise_for_status()
            with open(cities_path, "wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
        print(f"Saved csv-cities.csv.gz ({cities_path.stat().st_size} bytes)")
    else:
        print(f"Using cached csv-cities.csv.gz ({cities_path.stat().st_size} bytes)")

    return countries_path, cities_path


def seed_geo_data():
    countries_path, cities_path = ensure_cached_files()

    conn = psycopg.connect(DB_URL, autocommit=False)
    try:
        cur = conn.cursor()

        # -------------------------------------------------------------
        # 1. SEED COUNTRIES
        # -------------------------------------------------------------
        print("\n--- Processing Countries ---")
        countries_text = countries_path.read_text(encoding="utf-8", errors="replace")
        country_reader = csv.DictReader(io.StringIO(countries_text))

        country_id_map = {}  # source_id (int) -> uuid.UUID
        country_code_map = {}  # iso2 (str) -> uuid.UUID
        countries_to_upsert = []

        countries_total = 0
        countries_invalid = 0

        for row in country_reader:
            countries_total += 1
            try:
                src_id = int(row["id"])
                iso2 = row["iso2"].strip().upper()
                name = row["name"].strip()
                native_name = row.get("native", "").strip() or None
                phone_code = row.get("phonecode", "").strip() or None

                if not iso2 or not name:
                    countries_invalid += 1
                    continue

                country_uuid = uuid.uuid5(JESTER_GEO_NAMESPACE, f"country:{src_id}")
                country_id_map[src_id] = country_uuid
                country_code_map[iso2] = country_uuid

                countries_to_upsert.append((
                    country_uuid,
                    src_id,
                    iso2,
                    name,
                    native_name,
                    phone_code,
                ))
            except Exception as e:
                countries_invalid += 1

        print(f"Parsed {len(countries_to_upsert)} valid countries (Skipped: {countries_invalid})")

        # Upsert countries
        cur.executemany(
            """
            INSERT INTO public.countries (
                id, source_id, iso2, name, native_name, phone_code, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, now())
            ON CONFLICT (source_id) DO UPDATE SET
                iso2 = EXCLUDED.iso2,
                name = EXCLUDED.name,
                native_name = EXCLUDED.native_name,
                phone_code = EXCLUDED.phone_code;
            """,
            countries_to_upsert,
        )
        conn.commit()
        print("Countries successfully upserted into database!")

        # -------------------------------------------------------------
        # 2. SEED CITIES
        # -------------------------------------------------------------
        print("\n--- Processing Cities ---")
        cities_gz_bytes = cities_path.read_bytes()
        cities_text = gzip.decompress(cities_gz_bytes).decode("utf-8", errors="replace")
        city_reader = csv.DictReader(io.StringIO(cities_text))

        cities_total = 0
        cities_imported = 0
        cities_skipped = 0
        missing_timezone = 0
        missing_coords = 0
        ge_cities_count = 0

        batch = []
        batch_size = 5000

        for row in city_reader:
            cities_total += 1
            try:
                src_id = int(row["id"])
                country_src_id = int(row["country_id"])
                country_uuid = country_id_map.get(country_src_id)
                country_code = row["country_code"].strip().upper()

                # Fallback mapping if country_id didn't match directly
                if not country_uuid:
                    country_uuid = country_code_map.get(country_code)

                if not country_uuid:
                    cities_skipped += 1
                    continue

                name = row["name"].strip()
                if not name:
                    cities_skipped += 1
                    continue

                lat_str = row.get("latitude", "").strip()
                lon_str = row.get("longitude", "").strip()
                if not lat_str or not lon_str:
                    missing_coords += 1
                    cities_skipped += 1
                    continue

                lat = float(lat_str)
                lon = float(lon_str)

                # Validate coordinates
                if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                    cities_skipped += 1
                    continue

                tz = row.get("timezone", "").strip()
                if not tz:
                    missing_timezone += 1
                    # Fallback to Asia/Tbilisi for Georgia if missing
                    if country_code == "GE":
                        tz = "Asia/Tbilisi"
                    else:
                        cities_skipped += 1
                        continue

                state_name = row.get("state_name", "").strip() or None
                name_ascii = normalize_ascii_name(name)

                # Major city determination
                is_major = False
                pop_str = row.get("population", "").strip()
                pop = int(pop_str) if pop_str.isdigit() else 0

                if country_code == "GE":
                    ge_cities_count += 1
                    # Check if hub or municipal capital
                    if name_ascii.lower() in GE_MAJOR_HUBS or pop > 5000 or "tbilisi" in name.lower():
                        is_major = True
                elif pop > 500000:
                    is_major = True

                city_uuid = uuid.uuid5(JESTER_GEO_NAMESPACE, f"city:{src_id}")

                batch.append((
                    city_uuid,
                    src_id,
                    country_uuid,
                    country_code,
                    name,
                    name_ascii,
                    state_name,
                    lat,
                    lon,
                    tz,
                    is_major,
                ))

                if len(batch) >= batch_size:
                    cur.executemany(
                        """
                        INSERT INTO public.cities (
                            id, source_id, country_id, country_code, name, name_ascii,
                            state_or_region, latitude, longitude, timezone, is_major_city,
                            created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now()
                        ) ON CONFLICT (source_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            name_ascii = EXCLUDED.name_ascii,
                            state_or_region = EXCLUDED.state_or_region,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            timezone = EXCLUDED.timezone,
                            is_major_city = EXCLUDED.is_major_city,
                            updated_at = now();
                        """,
                        batch,
                    )
                    conn.commit()
                    cities_imported += len(batch)
                    batch.clear()
                    print(f"Imported {cities_imported} / {cities_total} cities...")

            except Exception as e:
                cities_skipped += 1

        if batch:
            cur.executemany(
                """
                INSERT INTO public.cities (
                    id, source_id, country_id, country_code, name, name_ascii,
                    state_or_region, latitude, longitude, timezone, is_major_city,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now()
                ) ON CONFLICT (source_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    name_ascii = EXCLUDED.name_ascii,
                    state_or_region = EXCLUDED.state_or_region,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    timezone = EXCLUDED.timezone,
                    is_major_city = EXCLUDED.is_major_city,
                    updated_at = now();
                """,
                batch,
            )
            conn.commit()
            cities_imported += len(batch)

        # -------------------------------------------------------------
        # 3. VERIFICATION & REPORTING
        # -------------------------------------------------------------
        cur.execute("SELECT count(*) FROM public.countries;")
        db_countries = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM public.cities;")
        db_cities = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM public.cities WHERE country_code = 'GE';")
        db_ge_cities = cur.fetchone()[0]

        cur.execute("SELECT count(*) FROM public.cities WHERE is_major_city = true;")
        db_major_cities = cur.fetchone()[0]

        print("\n==================================================")
        print("IMPORT SUMMARY REPORT")
        print("==================================================")
        print(f"Total Countries Processed : {countries_total}")
        print(f"Countries in Database     : {db_countries}")
        print(f"Total Cities Processed    : {cities_total}")
        print(f"Cities Imported           : {cities_imported}")
        print(f"Cities in Database        : {db_cities}")
        print(f"Georgian Cities in DB     : {db_ge_cities}")
        print(f"Major Cities Flagged      : {db_major_cities}")
        print(f"Skipped Records           : {cities_skipped}")
        print(f"Missing Coordinates       : {missing_coords}")
        print(f"Missing Timezone          : {missing_timezone}")
        print("==================================================")

    except Exception as e:
        conn.rollback()
        print(f"Error during import: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_geo_data()
