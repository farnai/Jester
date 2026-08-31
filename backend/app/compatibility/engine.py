"""
Deterministic compatibility calculation engine service.
Calculates score, dimensions, structured signals, topics, starters, and evidence trace
from private astrology placements.
"""
from typing import Any
import uuid

from backend.app.compatibility.models import CompatibilityScore
from backend.app.compatibility.synastry import NatalInputPayload, SynastryEngine, SynastryResult


class CompatibilityEngine:
    def __init__(self) -> None:
        self._engine = SynastryEngine()

    def calculate_from_payloads(
        self,
        person_a: NatalInputPayload,
        person_b: NatalInputPayload,
    ) -> SynastryResult:
        return self._engine.calculate(person_a, person_b)

    def calculate(
        self,
        person_a_id: uuid.UUID,
        person_a_version: int,
        person_a_precision: str,
        person_a_placements: dict[str, Any],
        person_b_id: uuid.UUID,
        person_b_version: int,
        person_b_precision: str,
        person_b_placements: dict[str, Any],
    ) -> SynastryResult:
        # Extract 10 planets
        planets_a = {
            p: float(person_a_placements[f"{p}_longitude"])
            for p in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
            if person_a_placements.get(f"{p}_longitude") is not None
        }
        planets_b = {
            p: float(person_b_placements[f"{p}_longitude"])
            for p in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
            if person_b_placements.get(f"{p}_longitude") is not None
        }

        asc_a = person_a_placements.get("ascendant_longitude")
        if asc_a is not None:
            asc_a = float(asc_a)
        asc_b = person_b_placements.get("ascendant_longitude")
        if asc_b is not None:
            asc_b = float(asc_b)

        payload_a = NatalInputPayload(
            user_id=person_a_id,
            birth_data_version=person_a_version,
            birth_time_precision=person_a_precision,  # type: ignore
            planet_longitudes=planets_a,
            ascendant_longitude=asc_a,
            retrogrades=person_a_placements.get("retrogrades") or {},
        )
        payload_b = NatalInputPayload(
            user_id=person_b_id,
            birth_data_version=person_b_version,
            birth_time_precision=person_b_precision,  # type: ignore
            planet_longitudes=planets_b,
            ascendant_longitude=asc_b,
            retrogrades=person_b_placements.get("retrogrades") or {},
        )

        return self._engine.calculate(payload_a, payload_b)
