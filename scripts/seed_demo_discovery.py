"""
Seeds realistic discovery users and the default demo user with real birth data
and calculates exact Swiss Ephemeris placements for smoke-testing the UX/content flow.
"""
import uuid
import psycopg
from psycopg.rows import dict_row

from backend.app.astrology.natal import recalculate_user_astrology

DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"

DEMO_USER_ID = uuid.UUID("26098ac8-f8f0-4cd3-9bbb-78dc8467ba07")

USERS_DATA = [
    {
        "id": DEMO_USER_ID,
        "email": "demo_user@jester.app",
        "display_name": "ალექსანდრე",
        "bio": "ტექნოლოგიები, ციფრული პროდუქტები და ადამიანური კავშირები.",
        "city": "თბილისი",
        "occupation": "Product Lead",
        "birth_date": "1996-04-12",
        "birth_time": "14:30:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333301"),
        "email": "elene@jester.app",
        "display_name": "ელენე",
        "bio": "დიზაინერი და ვიზუალური მკვლევარი. მიყვარს სიცხადე და დეტალები.",
        "city": "თბილისი",
        "occupation": "UX/UI Designer",
        "birth_date": "1997-11-08",
        "birth_time": "10:15:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333302"),
        "email": "nikoloz@jester.app",
        "display_name": "ნიკოლოზ",
        "bio": "სტრატეგია, ურბანული მოგზაურობა და სპონტანური გადაწყვეტილებები.",
        "city": "ბათუმი",
        "occupation": "Creative Director",
        "birth_date": "1994-08-22",
        "birth_time": "18:45:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.6416,
        "longitude": 41.6359,
        "place_label": "ბათუმი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333303"),
        "email": "ana@jester.app",
        "display_name": "ანა",
        "bio": "არქიტექტურა, მინიმალისტური სივრცეები და ღამის საუბრები.",
        "city": "ქუთაისი",
        "occupation": "Architect",
        "birth_date": "1998-02-14",
        "birth_time": "08:30:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 42.2679,
        "longitude": 42.6946,
        "place_label": "ქუთაისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333304"),
        "email": "davit@jester.app",
        "display_name": "დავით",
        "bio": "ალგორითმები, მუსიკა და რთული პრობლემების მარტივი ამოხსნა.",
        "city": "თბილისი",
        "occupation": "Software Engineer",
        "birth_date": "1993-05-30",
        "birth_time": "22:10:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333305"),
        "email": "mariam@jester.app",
        "display_name": "მარიამ",
        "bio": "ბრენდის სტრატეგია და ამბების თხრობა. პირდაპირი და კონცენტრირებული.",
        "city": "თელავი",
        "occupation": "Brand Strategist",
        "birth_date": "1999-09-18",
        "birth_time": "12:00:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.9198,
        "longitude": 45.4732,
        "place_label": "თელავი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333306"),
        "email": "giorgi@jester.app",
        "display_name": "გიორგი",
        "bio": "დოკუმენტური კინო, ფოტოგრაფია და ადამიანებზე დაკვირვება.",
        "city": "ბათუმი",
        "occupation": "Art Director",
        "birth_date": "1995-07-04",
        "birth_time": "16:20:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.6416,
        "longitude": 41.6359,
        "place_label": "ბათუმი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333307"),
        "email": "nino@jester.app",
        "display_name": "ნინო",
        "bio": "ვიზუალური ხელოვნება, პორტრეტები და ურბანული არქიტექტურა.",
        "city": "თბილისი",
        "occupation": "Photographer",
        "birth_date": "1997-03-24",
        "birth_time": "09:20:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333308"),
        "email": "luka@jester.app",
        "display_name": "ლუკა",
        "bio": "ხმის დიზაინი, ანალოგური სინთეზატორები და ღამის ექსპერიმენტები.",
        "city": "თბილისი",
        "occupation": "Music Producer",
        "birth_date": "1996-10-15",
        "birth_time": "15:45:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
    {
        "id": uuid.UUID("33333333-3333-3333-3333-333333333309"),
        "email": "salome@jester.app",
        "display_name": "სალომე",
        "bio": "საგამოძიებო ჟურნალისტიკა, ფაქტები და დოკუმენტური ისტორიები.",
        "city": "თბილისი",
        "occupation": "Journalist",
        "birth_date": "1995-01-18",
        "birth_time": "07:30:00",
        "birth_timezone": "Asia/Tbilisi",
        "latitude": 41.7151,
        "longitude": 44.8271,
        "place_label": "თბილისი",
    },
]

def seed():
    conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)
    with conn.cursor() as cur:
        cur.execute("RESET ROLE;")
        print("Seeding demo users...")
        for u in USERS_DATA:
            uid = u["id"]
            # 1. auth.users
            cur.execute(
                """
                INSERT INTO auth.users (id, email, raw_user_meta_data, role, aud)
                VALUES (%s, %s, %s, 'authenticated', 'authenticated')
                ON CONFLICT (id) DO UPDATE SET email = excluded.email;
                """,
                (uid, u["email"], '{"name": "%s"}' % u["display_name"]),
            )

            # 2. public.profiles
            cur.execute(
                """
                INSERT INTO public.profiles (id, display_name, bio, city, occupation, is_discoverable)
                VALUES (%s, %s, %s, %s, %s, true)
                ON CONFLICT (id) DO UPDATE SET
                    display_name = excluded.display_name,
                    bio = excluded.bio,
                    city = excluded.city,
                    occupation = excluded.occupation,
                    is_discoverable = true;
                """,
                (uid, u["display_name"], u["bio"], u["city"], u["occupation"]),
            )

            # 3. public.birth_data
            cur.execute(
                """
                INSERT INTO public.birth_data (
                    user_id, birth_date, birth_time, birth_time_precision, birth_timezone, latitude, longitude, place_label
                )
                VALUES (%s, %s, %s, 'exact', %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    birth_date = excluded.birth_date,
                    birth_time = excluded.birth_time,
                    birth_timezone = excluded.birth_timezone,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    place_label = excluded.place_label;
                """,
                (uid, u["birth_date"], u["birth_time"], u["birth_timezone"], u["latitude"], u["longitude"], u["place_label"]),
            )

            # 4. Calculate Swiss Ephemeris natal astrology and derive safe profile
            safe = recalculate_user_astrology(uid, conn)
            print(f"  [+] {u['display_name']} -> Sun: {safe.sun_sign}, Moon: {safe.moon_sign}, Asc: {safe.ascendant_sign}, Element: {safe.element_primary}")

    conn.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
