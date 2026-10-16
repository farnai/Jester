"""Owner-editable profiles cannot bypass authoritative onboarding completion."""
import uuid

import psycopg
import pytest

from backend.app.config import get_settings


@pytest.mark.parametrize("operation", ["insert", "update"])
def test_authenticated_owner_cannot_set_completion_directly(operation):
    # Roll back all fixtures; never truncate or modify unrelated users.
    with psycopg.connect(get_settings().DATABASE_URL) as db:
        try:
            uid = uuid.uuid4()
            db.execute("INSERT INTO auth.users (id, email) VALUES (%s, %s)", (uid, f"boundary-{uid}@example.test"))
            if operation == "update":
                db.execute("INSERT INTO public.profiles (id, display_name) VALUES (%s, 'Boundary')", (uid,))
            db.execute("SELECT set_config('request.jwt.claim.sub', %s, true)", (str(uid),))
            db.execute("SET LOCAL ROLE authenticated")
            if operation == "update":
                # Ordinary owner edits retain their original permissions.
                db.execute("UPDATE public.profiles SET display_name = 'Edited' WHERE id = %s", (uid,))
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                if operation == "insert":
                    db.execute("INSERT INTO public.profiles (id, display_name, onboarding_completed) VALUES (%s, 'Boundary', true)", (uid,))
                else:
                    db.execute("UPDATE public.profiles SET onboarding_completed = true WHERE id = %s", (uid,))
        finally:
            db.rollback()
