"""
Daily energy scheduled generation job.
"""
import uuid
from datetime import date
import psycopg

from backend.app.core.database import db_manager


def generate_daily_energy_for_user(user_id: uuid.UUID, energy_date: date, db: psycopg.Connection):
    """
    Generates and stores today's energy for a given user on a specific date.
    """
    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO public.daily_energies (user_id, energy_date, signals, interpretation, engine_version)
            VALUES (%s, %s, '[]'::jsonb, '{"summary": "A dynamic day for creative exploration."}'::jsonb, '1.0.0')
            ON CONFLICT (user_id, energy_date) DO UPDATE SET
                interpretation = excluded.interpretation,
                updated_at = now();
        """, (user_id, energy_date))
