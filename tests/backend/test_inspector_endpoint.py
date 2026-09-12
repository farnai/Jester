"""
Tests for JESTER Content & Logic Inspector Endpoint (GET /v1/interpretations/inspector-data).
Validates that the internal QA projection compiles accurately without mutating any state.
"""
from fastapi.testclient import TestClient
import pytest

from backend.app.main import app

client = TestClient(app)


def test_inspector_endpoint_structure():
    """Validates the structure and data payload of the Content Inspector endpoint."""
    res = client.get("/v1/interpretations/inspector-data")
    assert res.status_code == 200, f"Expected 200 OK, got {res.status_code}"

    data = res.json()
    assert "summary" in data
    assert "synastry_pipeline" in data
    assert "natal_sections" in data
    assert "discovery_items" in data
    assert "connection_items" in data
    assert "chat_items" in data
    assert "daily_energy" in data
    assert "integrity" in data

    # Summary verification
    summary = data["summary"]
    assert summary["expected_frozen_assets"] == 681
    assert summary["actual_frozen_assets"] == 681
    assert summary["status"] == "OK"
    assert "555 Natal + 60 Synastry + 66 Batch 7" in summary["note"]
    assert len(summary["batches"]) == 11

    # Synastry pipeline verification
    synastry = data["synastry_pipeline"]
    assert len(synastry) == 49
    # Verify causal chain structure on first item
    first_item = synastry[0]
    assert "trigger" in first_item
    assert "aspect" in first_item
    assert "canonical_rule" in first_item
    assert "signal" in first_item
    assert "category" in first_item
    assert "contract_id" in first_item
    assert "causal_chain" in first_item
    assert len(first_item["causal_chain"]) >= 7

    # Discovery verification (12 signs)
    discovery = data["discovery_items"]
    assert len(discovery) == 12

    # Connection verification (11 invitations)
    connection = data["connection_items"]
    assert len(connection) == 11

    # Chat starters verification (43 starters)
    chat = data["chat_items"]
    assert len(chat) == 43

    # Daily Energy verification (5 layers: Archetypes, Interpretation Assets, DO, DON'T, Neutral)
    daily_energy = data["daily_energy"]
    assert len(daily_energy["archetypes"]) == 13
    assert len(daily_energy["interpretation_assets"]) == 831
    assert len(daily_energy["do_tags"]) == 39
    assert len(daily_energy["dont_tags"]) == 39
    assert daily_energy["summary"]["missing_assets_count"] == 0

    # Verify no false "არ არის ხელმისაწვდომი" and no universal max 3.0 orb
    for arch in daily_energy["archetypes"]:
        assert arch["qa_status"] == "OK"
        assert arch["narrative_ka"] != "არ არის ხელმისაწვდომი"
        assert not arch["narrative_ka"].startswith("MISSING FROZEN ASSET")
        assert len(arch["narrative_ka"]) > 10
        spec = arch["centralized_spec"]
        assert "engine_source" in spec
        assert spec["engine_source"] == "backend.app.astrology.transits"
        assert "evidence_notice" in spec
        # Check body-specific orb limits (not universal 3.0)
        for kb in spec.get("key_bodies", []):
            assert kb["max_orb"] in (0.5, 1.0, 1.5, 2.0, 2.5)

    # Neutral Baseline explicit verification
    assert "neutral_case" in daily_energy
    neutral = daily_energy["neutral_case"]
    assert neutral["detection_mode"] == "neutral_baseline"
    assert neutral["primary_transit"] is None
    assert neutral["qa_status"] == "OK"
    assert len(neutral["do_ka"]) == 3
    assert len(neutral["dont_ka"]) == 3
    assert len(neutral["do_en"]) == 3
    assert len(neutral["dont_en"]) == 3

    # Natal and Mars Semantic Firewall verification
    natal_sections = data["natal_sections"]
    assert len(natal_sections) == 9  # Sun, Moon, Ascendant, Mercury, Venus, Mars, Elements, Synthesis, Verdicts
    mars_sec = next(s for s in natal_sections if s["key"] == "mars")
    assert mars_sec["firewall_status"] == "FIREWALL_PASSED"
    assert len(mars_sec["firewall_violations"]) == 0

    # Overall integrity verification
    integrity = data["integrity"]
    assert integrity["overall_status"] == "OK"
    assert integrity["synastry_unresolved_count"] == 0
