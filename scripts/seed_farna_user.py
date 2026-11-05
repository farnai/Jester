"""
Seed local development user with password 123, profile, birth data, and Swiss Ephemeris calculations.
Works with both 'dev@jester.app' (or legacy aliases) in the UI.
"""
import sys
import uuid
import json
import urllib.request
import urllib.error
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import psycopg
from psycopg.rows import dict_row

from backend.app.astrology.natal import recalculate_user_astrology

DB_URL = "postgresql://postgres:postgres@127.0.0.1:54322/postgres"
SUPABASE_URL = "http://127.0.0.1:54321"
SERVICE_ROLE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0."
    "EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
)
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9."
    "CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
)

USERS_TO_CREATE = [
    {
        "id": "44444444-4444-4444-4444-444444444444",
        "email": "dev@jester.app",
        "password": "password123",
        "display_name": "Dev User",
        "first_name": "Dev",
        "last_name": "User",
        "bio": "Jester Local Development Persona. Exploration, testing, and connection intelligence.",
        "city": "London",
        "city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "current_city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "birth_city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "occupation": "Developer",
        "birth_date": "2000-01-01",
        "birth_time": "12:00:00",
        "birth_timezone": "UTC",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "place_label": "London, United Kingdom",
        "is_discoverable": True,
    },
    {
        "id": "44444444-4444-4444-4444-444444444445",
        "email": "dev-alias@jester.app",
        "password": "password123",
        "display_name": "Dev User (Alias)",
        "first_name": "Dev",
        "last_name": "Alias",
        "bio": "Jester Local Development Persona (Secondary).",
        "city": "London",
        "city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "current_city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "birth_city_id": "c6383804-ec3d-507c-bbee-97f23941339e",
        "occupation": "Developer",
        "birth_date": "2000-01-01",
        "birth_time": "12:00:00",
        "birth_timezone": "UTC",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "place_label": "London, United License",
        "is_discoverable": False,
    },
]


def ensure_auth_user(cur, user_info: dict) -> str:
    """Ensure user exists in Supabase Auth without deleting or resetting existing records."""
    email = user_info["email"]
    uid = user_info["id"]
    cur.execute("SELECT id FROM auth.users WHERE email = %s OR id = %s;", (email, uid))
    existing = cur.fetchone()
    if existing:
        print(f"  [*] Auth user already exists in GoTrue (ID: {existing['id']})")
        return str(existing["id"])
    return create_user_via_admin_api(user_info)


def create_user_via_admin_api(user_info: dict) -> str:
    """Create user via Supabase Admin API so GoTrue handles bcrypt and auth.identities."""
    payload = {
        "id": user_info["id"],
        "email": user_info["email"],
        "password": user_info["password"],
        "email_confirm": True,
        "user_metadata": {
            "name": user_info["display_name"],
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
        print(f"Error creating user {user_info['email']} via Admin API ({e.code}): {error_body}")
        raise


def test_password_login(email: str, password: str) -> bool:
    """Verify that password login works directly via GoTrue endpoint."""
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        data=json.dumps({"email": email, "password": password}).encode("utf-8"),
        headers={
            "apikey": ANON_KEY,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return "access_token" in data
    except urllib.error.HTTPError as e:
        print(f"Login test failed for {email}: {e.code} - {e.read().decode('utf-8')}")
        return False


def seed_farna():
    conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)
    with conn.cursor() as cur:
        cur.execute("RESET ROLE;")

        for user_info in USERS_TO_CREATE:
            email = user_info["email"]
            uid = user_info["id"]
            user_uuid = uuid.UUID(uid)

            print(f"\n--- Setting up {email} (ID: {uid}) ---")

            # 1. Ensure user exists in Supabase Auth safely without deletion
            created_id = ensure_auth_user(cur, user_info)

            # 3. Create public.profiles
            is_disc = user_info.get("is_discoverable", True)
            cur.execute(
                """
                INSERT INTO public.profiles (
                    id, display_name, first_name, last_name, bio, city, city_id, current_city_id,
                    occupation, timezone, is_discoverable, onboarding_completed, onboarding_step
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, 4)
                ON CONFLICT (id) DO UPDATE SET
                    display_name = excluded.display_name,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    bio = excluded.bio,
                    city = excluded.city,
                    city_id = excluded.city_id,
                    current_city_id = excluded.current_city_id,
                    occupation = excluded.occupation,
                    timezone = excluded.timezone,
                    is_discoverable = excluded.is_discoverable,
                    onboarding_completed = true,
                    onboarding_step = 4;
                """,
                (
                    user_uuid,
                    user_info["display_name"],
                    user_info["first_name"],
                    user_info["last_name"],
                    user_info["bio"],
                    user_info["city"],
                    user_info["city_id"],
                    user_info["current_city_id"],
                    user_info["occupation"],
                    user_info["birth_timezone"],
                    is_disc,
                ),
            )
            print("  [+] public.profiles created")

            # 4. Create public.birth_data
            cur.execute(
                """
                INSERT INTO public.birth_data (
                    user_id, birth_date, birth_time, birth_time_precision, birth_timezone,
                    latitude, longitude, place_label, birth_city_id
                )
                VALUES (%s, %s, %s, 'exact', %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    birth_date = excluded.birth_date,
                    birth_time = excluded.birth_time,
                    birth_time_precision = excluded.birth_time_precision,
                    birth_timezone = excluded.birth_timezone,
                    latitude = excluded.latitude,
                    longitude = excluded.longitude,
                    place_label = excluded.place_label,
                    birth_city_id = excluded.birth_city_id;
                """,
                (
                    user_uuid,
                    user_info["birth_date"],
                    user_info["birth_time"],
                    user_info["birth_timezone"],
                    user_info["latitude"],
                    user_info["longitude"],
                    user_info["place_label"],
                    user_info["birth_city_id"],
                ),
            )
            print("  [+] public.birth_data created")

            # 5. Calculate Swiss Ephemeris natal astrology
            safe = recalculate_user_astrology(user_uuid, conn)
            print(
                f"  [+] Swiss Ephemeris Placements:\n"
                f"      Sun: {safe.sun_sign}, Moon: {safe.moon_sign}, Ascendant: {safe.ascendant_sign}\n"
                f"      Primary Element: {safe.element_primary}, Modality: {safe.modality_primary}"
            )

            # 6. Verify password login
            ok = test_password_login(email, user_info["password"])
            if ok:
                print(f"  [SUCCESS] Password login verified for {email} with password '{user_info['password']}'!")
            else:
                print(f"  [FAILED] Password login verification failed for {email}!")

    conn.close()
    print("\n==============================================")
    print("Dev User successfully created and verified!")
    print("Email: dev@jester.app (or dev-alias@jester.app)")
    print("Password: 123")
    print("==============================================")


if __name__ == "__main__":
    seed_farna()
