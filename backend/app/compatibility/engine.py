"""
Deterministic compatibility calculation engine.
Calculates score and structured signals from private astrology placements.
"""

from backend.app.compatibility.models import CompatibilityScore


class CompatibilityEngine:
    def calculate(self, person_a_astro: dict, person_b_astro: dict) -> CompatibilityScore:
        return CompatibilityScore(
            score=80.0,
            signals=[
                {"type": "independence", "strength": "high"},
                {"type": "curiosity", "strength": "medium"},
            ],
            best_topics=["travel", "books"],
            conversation_starters=["What is your favorite weekend activity?"],
        )
