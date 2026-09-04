import json
import uuid
from datetime import date
import psycopg
from psycopg.types.json import Jsonb

from backend.app.core.database import db_manager
from backend.app.interpretation.engine import interpretation_engine


def generate_daily_energy_for_user(
    user_id: uuid.UUID,
    energy_date: date,
    db: psycopg.Connection,
    energy_type: str = "creativity",
):
    """
    Generates and stores today's energy for a given user on a specific date,
    using the decoupled JESTER interpretation content layer.
    """
    resolved = interpretation_engine.resolve_daily_energy(energy_type)
    interp_data = (
        resolved.model_dump()
        if resolved
        else {
            "id": f"daily_energy.{energy_type}.v1",
            "text": "დღეს იდეები ბევრი გაქვს. ზოგიერთი მათგანი გადარჩენასაც იმსახურებს.",
            "content_status": "ai_draft",
            "language": "ka",
        }
    )

    with db.cursor() as cur:
        cur.execute("""
            INSERT INTO public.daily_energies (user_id, energy_date, signals, interpretation, engine_version)
            VALUES (%s, %s, '[]'::jsonb, %s, '1.0.0')
            ON CONFLICT (user_id, energy_date) DO UPDATE SET
                interpretation = excluded.interpretation,
                updated_at = now();
        """, (user_id, energy_date, Jsonb(interp_data)))

