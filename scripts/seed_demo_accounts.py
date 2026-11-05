"""
Safe, Idempotent Seed Script for 20 Synthetic Local Demo Accounts.
Strictly guarded to run ONLY on verified local databases (127.0.0.1 / localhost).
Creation-only: skips already existing accounts without modifying or resetting any user data.
"""
import os
import sys
import uuid
import json
import urllib.request
import urllib.error
from urllib.parse import urlparse
from pathlib import Path
import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.app.config import get_settings
from backend.app.astrology.natal import recalculate_user_astrology

DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
SUPABASE_URL = "http://127.0.0.1:54321"
SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0."
    "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
)

# Canonical Georgian Cities (verified from public.cities)
CITIES = {
    "tbilisi": {
        "id": "31ccec7f-cfa6-52d6-a1e6-8abd13257547",
        "name": "Tbilisi",
        "latitude": 41.69411,
        "longitude": 44.83368,
        "timezone": "Asia/Tbilisi",
        "place_label": "Tbilisi, Georgia",
    },
    "batumi": {
        "id": "52b6d811-8474-52ca-afe6-de22b567e531",
        "name": "Batumi",
        "latitude": 41.64228,
        "longitude": 41.63392,
        "timezone": "Asia/Tbilisi",
        "place_label": "Batumi, Georgia",
    },
    "kutaisi": {
        "id": "25362677-7103-5121-8c04-0424b9d3b5d2",
        "name": "Kutaisi",
        "latitude": 42.26791,
        "longitude": 42.69459,
        "timezone": "Asia/Tbilisi",
        "place_label": "Kutaisi, Georgia",
    },
    "zugdidi": {
        "id": "9d7f40bd-2aa5-51ee-bef4-3340aa410f37",
        "name": "Zugdidi",
        "latitude": 42.50880,
        "longitude": 41.87088,
        "timezone": "Asia/Tbilisi",
        "place_label": "Zugdidi, Georgia",
    },
    "gori": {
        "id": "fb086940-8ef9-5127-87f0-2bfac947c8ce",
        "name": "Gori",
        "latitude": 41.98422,
        "longitude": 44.11578,
        "timezone": "Asia/Tbilisi",
        "place_label": "Gori, Georgia",
    },
    "telavi": {
        "id": "c55c3b90-6a01-59e5-a319-217d57a09b21",
        "name": "Telavi",
        "latitude": 41.91978,
        "longitude": 45.47315,
        "timezone": "Asia/Tbilisi",
        "place_label": "Telavi, Georgia",
    },
    "akhaltsikhe": {
        "id": "3b218040-f08d-5dc1-9055-a2dc028ead44",
        "name": "Akhaltsikhe",
        "latitude": 41.63901,
        "longitude": 42.98262,
        "timezone": "Asia/Tbilisi",
        "place_label": "Akhaltsikhe, Georgia",
    },
    "ambrolauri": {
        "id": "33ffc15b-3c10-5a94-8667-7b3bade51ec1",
        "name": "Ambrolauri",
        "latitude": 42.52111,
        "longitude": 43.16222,
        "timezone": "Asia/Tbilisi",
        "place_label": "Ambrolauri, Georgia",
    },
    "ozurgeti": {
        "id": "7896748a-7357-56a4-8aeb-de4e1117d3e4",
        "name": "Ozurgeti",
        "latitude": 41.92442,
        "longitude": 42.00682,
        "timezone": "Asia/Tbilisi",
        "place_label": "Ozurgeti, Georgia",
    },
    "borjomi": {
        "id": "b498f17a-8e7c-5f6e-b7a6-cefc88d9c464",
        "name": "Borjomi",
        "latitude": 41.85272,
        "longitude": 43.41284,
        "timezone": "Asia/Tbilisi",
        "place_label": "Borjomi, Georgia",
    },
    "kobuleti": {
        "id": "0d770ba5-c063-5294-84ad-d16a2d3e5b8f",
        "name": "Kobuleti",
        "latitude": 41.82143,
        "longitude": 41.77921,
        "timezone": "Asia/Tbilisi",
        "place_label": "Kobuleti, Georgia",
    },
    "sighnaghi": {
        "id": "03c64de3-e526-5b7f-b8ec-675fd149a314",
        "name": "Sighnaghi",
        "latitude": 41.62046,
        "longitude": 45.92198,
        "timezone": "Asia/Tbilisi",
        "place_label": "Sighnaghi, Georgia",
    },
    "mtskheta": {
        "id": "7366fba4-7d09-5a37-bd10-554d065fa01b",
        "name": "Mtskheta",
        "latitude": 41.84514,
        "longitude": 44.71875,
        "timezone": "Asia/Tbilisi",
        "place_label": "Mtskheta, Georgia",
    },
    "samtredia": {
        "id": "403ade79-2e57-5594-b174-56ee1205ac15",
        "name": "Samtredia",
        "latitude": 42.15370,
        "longitude": 42.33517,
        "timezone": "Asia/Tbilisi",
        "place_label": "Samtredia, Georgia",
    },
}

# 20 Diverse Synthetic Demo Users Specification
DEMO_USERS_SPEC = [
    {
        "email": "demo01@jester.test",
        "first_name": "გიორგი",
        "last_name": "ასათიანი",
        "occupation": "არქიტექტორი",
        "bio": "არქიტექტურა, ურბანული დიზაინი და დილის ესპრესო.",
        "birth_date": "1996-03-22",
        "birth_time": "08:30:00",
        "birth_city": "tbilisi",
        "current_city": "tbilisi",
        "interest_slugs": ["art", "coffee", "travel", "photography"],
    },
    {
        "email": "demo02@jester.test",
        "first_name": "ნინო",
        "last_name": "ჩხეიძე",
        "occupation": "კინოკრიტიკოსი",
        "bio": "წიგნები, კინო და მშვიდი საღამოები ქალაქის ხედით.",
        "birth_date": "1998-07-14",
        "birth_time": "14:15:00",
        "birth_city": "kutaisi",
        "current_city": "tbilisi",
        "interest_slugs": ["books", "cinema", "writing", "coffee"],
    },
    {
        "email": "demo03@jester.test",
        "first_name": "დავით",
        "last_name": "კვარაცხელია",
        "occupation": "პროგრამისტი",
        "bio": "ტექნოლოგიები, მთები და კარგი საუბრები ცხოვრებაზე.",
        "birth_date": "1991-11-08",
        "birth_time": "21:40:00",
        "birth_city": "zugdidi",
        "current_city": "batumi",
        "interest_slugs": ["technology", "hiking", "nature", "philosophy"],
    },
    {
        "email": "demo04@jester.test",
        "first_name": "მარიამ",
        "last_name": "ჯაფარიძე",
        "occupation": "ფოტოგრაფი",
        "bio": "ზღვა, ფოტოგრაფია და თანამედროვე ხელოვნება.",
        "birth_date": "2002-05-19",
        "birth_time": "11:00:00",
        "birth_city": "batumi",
        "current_city": "batumi",
        "interest_slugs": ["photography", "art", "nature", "travel"],
    },
    {
        "email": "demo05@jester.test",
        "first_name": "ლუკა",
        "last_name": "ბერიძე",
        "occupation": "მუსიკალური პროდიუსერი",
        "bio": "მუსიკა, ვინილის ფირფიტები და საფეხმავლო მარშრუტები.",
        "birth_date": "1988-09-27",
        "birth_time": "06:45:00",
        "birth_city": "gori",
        "current_city": "tbilisi",
        "interest_slugs": ["music", "concerts", "hiking", "coffee"],
    },
    {
        "email": "demo06@jester.test",
        "first_name": "სალომე",
        "last_name": "მაისურაძე",
        "occupation": "კულინარიული ბლოგერი",
        "bio": "მოგზაურობა, კულინარიული ექსპერიმენტები და ასტროლოგია.",
        "birth_date": "1995-12-10",
        "birth_time": "17:20:00",
        "birth_city": "telavi",
        "current_city": "tbilisi",
        "interest_slugs": ["travel", "food", "astrology", "nature"],
    },
    {
        "email": "demo07@jester.test",
        "first_name": "ნიკოლოზ",
        "last_name": "დოლიძე",
        "occupation": "ისტორიკოსი",
        "bio": "ისტორია, თეატრი და კლასიკური ლიტერატურა.",
        "birth_date": "1980-04-03",
        "birth_time": "13:10:00",
        "birth_city": "ozurgeti",
        "current_city": "batumi",
        "interest_slugs": ["theatre", "books", "philosophy", "art"],
    },
    {
        "email": "demo08@jester.test",
        "first_name": "ანა",
        "last_name": "შენგელია",
        "occupation": "UI/UX დიზაინერი",
        "bio": "დიჯიტალ დიზაინი, ელექტრონული მუსიკა და კატები.",
        "birth_date": "2005-02-17",
        "birth_time": "09:50:00",
        "birth_city": "tbilisi",
        "current_city": "tbilisi",
        "interest_slugs": ["technology", "music", "pets", "art"],
    },
    {
        "email": "demo09@jester.test",
        "first_name": "ირაკლი",
        "last_name": "გელოვანი",
        "occupation": "მთამსვლელი & გიდი",
        "bio": "მთამსვლელობა, ღვინის კულტურა და გულწრფელი ადამიანები.",
        "birth_date": "1975-08-25",
        "birth_time": "19:30:00",
        "birth_city": "ambrolauri",
        "current_city": "kutaisi",
        "interest_slugs": ["nature", "hiking", "food", "philosophy"],
    },
    {
        "email": "demo10@jester.test",
        "first_name": "თამარ",
        "last_name": "ნემსაძე",
        "occupation": "იოგას ინსტრუქტორი",
        "bio": "იოგა, ჯანსაღი ცხოვრების წესი და ფსიქოლოგია.",
        "birth_date": "1993-06-30",
        "birth_time": "04:15:00",
        "birth_city": "akhaltsikhe",
        "current_city": "tbilisi",
        "interest_slugs": ["fitness", "philosophy", "books", "coffee"],
    },
    {
        "email": "demo11@jester.test",
        "first_name": "ალექსანდრე",
        "last_name": "თოფურია",
        "occupation": "3D ანიმატორი",
        "bio": "ვიდეო თამაშები, ანიმაცია და ღამის ქალაქი.",
        "birth_date": "1999-10-12",
        "birth_time": "23:00:00",
        "birth_city": "kobuleti",
        "current_city": "batumi",
        "interest_slugs": ["gaming", "technology", "cinema", "music"],
    },
    {
        "email": "demo12@jester.test",
        "first_name": "ქეთევან",
        "last_name": "ცინცაძე",
        "occupation": "სტილისტი",
        "bio": "მოდა, ესთეტიკა და მოგზაურობა მსოფლიოს გარშემო.",
        "birth_date": "1984-01-28",
        "birth_time": "15:40:00",
        "birth_city": "kobuleti",
        "current_city": "batumi",
        "interest_slugs": ["fashion", "travel", "photography", "art"],
    },
    {
        "email": "demo13@jester.test",
        "first_name": "ბექა",
        "last_name": "მიქაძე",
        "occupation": "ფინანსური ანალიტიკოსი",
        "bio": "ფინანსები, სტარტაპები და დილის სირბილი.",
        "birth_date": "2003-09-05",
        "birth_time": "07:25:00",
        "birth_city": "samtredia",
        "current_city": "kutaisi",
        "interest_slugs": ["fitness", "technology", "coffee", "books"],
    },
    {
        "email": "demo14@jester.test",
        "first_name": "თინათინ",
        "last_name": "ლომიძე",
        "occupation": "ეკოლოგი",
        "bio": "ბუნება, ეკოლოგია და სამაგიდო თამაშები მეგობრებთან.",
        "birth_date": "1997-11-23",
        "birth_time": "12:15:00",
        "birth_city": "borjomi",
        "current_city": "tbilisi",
        "interest_slugs": ["nature", "hiking", "gaming", "pets"],
    },
    {
        "email": "demo15@jester.test",
        "first_name": "ლევან",
        "last_name": "გოგოლაძე",
        "occupation": "მათემატიკოსი",
        "bio": "ჭადრაკი, კლასიკური მუსიკა და ძველი თბილისის ისტორიები.",
        "birth_date": "1970-07-07",
        "birth_time": "18:50:00",
        "birth_city": "gori",
        "current_city": "tbilisi",
        "interest_slugs": ["philosophy", "books", "music", "art"],
    },
    {
        "email": "demo16@jester.test",
        "first_name": "ელენე",
        "last_name": "კაპანაძე",
        "occupation": "სომელიე",
        "bio": "ღვინის ტურიზმი, იტალიური სამზარეულო და ცოცხალი მუსიკა.",
        "birth_date": "2001-04-18",
        "birth_time": "10:35:00",
        "birth_city": "sighnaghi",
        "current_city": "tbilisi",
        "interest_slugs": ["food", "travel", "concerts", "music"],
    },
    {
        "email": "demo17@jester.test",
        "first_name": "ვაჟა",
        "last_name": "წიკლაური",
        "occupation": "ასტროფოტოგრაფი",
        "bio": "მთები, კემპინგი და ასტროფოტოგრაფია.",
        "birth_date": "1986-02-09",
        "birth_time": "16:00:00",
        "birth_city": "mtskheta",
        "current_city": "tbilisi",
        "interest_slugs": ["hiking", "nature", "photography", "astrology"],
    },
    {
        "email": "demo18@jester.test",
        "first_name": "ანა-მარია",
        "last_name": "ხუციშვილი",
        "occupation": "კერამიკოსი",
        "bio": "კერამიკა, მებაღეობა და მშვიდი ცხოვრების რიტმი.",
        "birth_date": "1994-08-30",
        "birth_time": "20:10:00",
        "birth_city": "telavi",
        "current_city": "telavi",
        "interest_slugs": ["art", "nature", "coffee", "books"],
    },
    {
        "email": "demo19@jester.test",
        "first_name": "სანდრო",
        "last_name": "გამყრელიძე",
        "occupation": "სპორტსმენი",
        "bio": "სნოუბორდი, ექსტრემალური სპორტი და კონცერტები.",
        "birth_date": "2004-12-03",
        "birth_time": "05:40:00",
        "birth_city": "kutaisi",
        "current_city": "tbilisi",
        "interest_slugs": ["fitness", "concerts", "music", "travel"],
    },
    {
        "email": "demo20@jester.test",
        "first_name": "მზია",
        "last_name": "დუმბაძე",
        "occupation": "მწერალი",
        "bio": "ბათუმის ბულვარი, ზღვის ხმაური და კარგი ლიტერატურა.",
        "birth_date": "1968-10-25",
        "birth_time": "11:45:00",
        "birth_city": "batumi",
        "current_city": "batumi",
        "interest_slugs": ["books", "philosophy", "cinema", "nature"],
    },
]


def verify_local_environment():
    settings = get_settings()
    if settings.is_production:
        raise RuntimeError("CRITICAL SAFETY CHECK: Refusing to seed demo users in production!")
    parsed = urlparse(settings.DATABASE_URL or DB_URL)
    host = (parsed.hostname or "").lower()
    if host not in ["127.0.0.1", "localhost", "::1"]:
        raise RuntimeError(f"CRITICAL SAFETY CHECK: Host '{host}' is not a local test environment!")
    print(f"[ENV OK] Verified safe local database: {host}:{parsed.port or 5432}")


def create_user_via_admin_api(email: str, display_name: str, password: str) -> str:
    """Create user via Supabase Admin API without overwriting or deleting."""
    payload = {
        "email": email,
        "password": password,
        "email_confirm": True,
        "user_metadata": {
            "name": display_name,
        },
    }

    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["id"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"Error creating user {email} via Admin API ({e.code}): {error_body}")
        raise


def run_seed():
    verify_local_environment()

    # Password for local synthetic demo accounts (from env or safe local default)
    demo_password = os.getenv("JESTER_DEMO_PASSWORD", "LocalDemoPass2026!")

    conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)
    with conn.cursor() as cur:
        # Pre-load interests map
        cur.execute("SELECT id, slug FROM public.interests;")
        interest_slug_to_id = {row["slug"]: row["id"] for row in cur.fetchall()}

    created_count = 0
    skipped_count = 0

    print("=" * 70)
    print("JESTER SYNTHETIC DEMO SEEDING: 20 NEW ACCOUNTS")
    print("=" * 70)

    for spec in DEMO_USERS_SPEC:
        email = spec["email"]
        fn = spec["first_name"]
        ln = spec["last_name"]
        display_name = f"{fn} {ln[0]}."

        b_city = CITIES[spec["birth_city"]]
        c_city = CITIES[spec["current_city"]]

        with conn.cursor() as cur:
            # 1. Check if auth user already exists by email
            cur.execute("SELECT id FROM auth.users WHERE email = %s;", (email,))
            existing_auth = cur.fetchone()

            if existing_auth:
                print(f"[EXISTS - SKIPPED] {email} (ID: {existing_auth['id']})")
                skipped_count += 1
                continue

            # 2. Register user via Supabase Auth Admin API
            uid_str = create_user_via_admin_api(email, display_name, demo_password)
            user_uuid = uuid.UUID(uid_str)

            # 3. Insert public.profiles (Creation only, ON CONFLICT DO NOTHING)
            cur.execute(
                """
                INSERT INTO public.profiles (
                    id, display_name, first_name, last_name, bio,
                    city, city_id, current_city_id, occupation,
                    timezone, is_discoverable, onboarding_completed, onboarding_step
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, true, 4)
                ON CONFLICT (id) DO NOTHING;
                """,
                (
                    user_uuid,
                    display_name,
                    fn,
                    ln,
                    spec["bio"],
                    c_city["name"],
                    c_city["id"],
                    c_city["id"],
                    spec["occupation"],
                    c_city["timezone"],
                ),
            )

            # 4. Insert public.birth_data (Creation only, ON CONFLICT DO NOTHING)
            cur.execute(
                """
                INSERT INTO public.birth_data (
                    user_id, birth_date, birth_time, birth_time_precision,
                    birth_timezone, latitude, longitude, place_label, birth_city_id
                )
                VALUES (%s, %s, %s, 'exact', %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING;
                """,
                (
                    user_uuid,
                    spec["birth_date"],
                    spec["birth_time"],
                    b_city["timezone"],
                    b_city["latitude"],
                    b_city["longitude"],
                    b_city["place_label"],
                    b_city["id"],
                ),
            )

            # 5. Insert user_interests
            for slug in spec["interest_slugs"]:
                interest_id = interest_slug_to_id.get(slug)
                if interest_id:
                    cur.execute(
                        """
                        INSERT INTO public.user_interests (user_id, interest_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING;
                        """,
                        (user_uuid, interest_id),
                    )

            # 6. Calculate deterministic Swiss Ephemeris natal astrology
            safe = recalculate_user_astrology(user_uuid, conn)

            created_count += 1
            print(
                f"[CREATED] {email} -> {display_name} | Sun: {safe.sun_sign}, Moon: {safe.moon_sign}, Asc: {safe.ascendant_sign}"
            )

    conn.close()

    print("=" * 70)
    print(f"SEED SUMMARY: {created_count} newly created, {skipped_count} skipped.")
    print("=" * 70)


if __name__ == "__main__":
    run_seed()

