"""
Focused Unit Tests for backend.app.core.canonical
Validates:
A. Symmetry: canonical_pair(A, B) == canonical_pair(B, A)
B. Determinism: identical inputs yield identical outputs
C. Seed symmetry: canonical_pair_seed(A, vA, B, vB) == canonical_pair_seed(B, vB, A, vA)
D. Known-value regression: exact format "{user_low}:{user_high}:{ver_low}:{ver_high}"
E. Different pair separation: different UUIDs produce distinct canonical pairs and seeds
F. Version sensitivity: version updates alter the seed string deterministically
G. Self-pair behavior: canonical_pair(A, A) raises ValueError
H. Application wrapper: connections.router.get_canonical_pair raises JesterAPIException(invalid_pair)
"""
import uuid
import pytest

from backend.app.core.canonical import canonical_pair, canonical_pair_seed
from backend.app.connections.router import get_canonical_pair, get_canonical_pair_seed
from backend.app.core.errors import JesterAPIException


def test_canonical_pair_symmetry():
    u1 = uuid.UUID("a0000000-0000-0000-0000-000000000001")
    u2 = uuid.UUID("b0000000-0000-0000-0000-000000000002")

    pair_1 = canonical_pair(u1, u2)
    pair_2 = canonical_pair(u2, u1)

    assert pair_1 == (u1, u2)
    assert pair_2 == (u1, u2)
    assert pair_1 == pair_2


def test_canonical_pair_determinism():
    u1 = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
    u2 = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

    assert canonical_pair(u1, u2) == canonical_pair(u1, u2)


def test_canonical_pair_seed_symmetry():
    u1 = uuid.UUID("a0000000-0000-0000-0000-000000000001")
    u2 = uuid.UUID("b0000000-0000-0000-0000-000000000002")
    v1 = 3
    v2 = 5

    seed_1 = canonical_pair_seed(u1, v1, u2, v2)
    seed_2 = canonical_pair_seed(u2, v2, u1, v1)

    assert seed_1 == seed_2
    assert seed_1 == "a0000000-0000-0000-0000-000000000001:b0000000-0000-0000-0000-000000000002:3:5"


def test_canonical_pair_seed_known_value_regression():
    u_low = uuid.UUID("11111111-1111-1111-1111-111111111111")
    u_high = uuid.UUID("99999999-9999-9999-9999-999999999999")
    ver_low = 1
    ver_high = 2

    # Forward order
    seed_fwd = canonical_pair_seed(u_low, ver_low, u_high, ver_high)
    assert seed_fwd == "11111111-1111-1111-1111-111111111111:99999999-9999-9999-9999-999999999999:1:2"

    # Reverse order
    seed_rev = canonical_pair_seed(u_high, ver_high, u_low, ver_low)
    assert seed_rev == "11111111-1111-1111-1111-111111111111:99999999-9999-9999-9999-999999999999:1:2"
    assert seed_fwd == seed_rev


def test_canonical_pair_separation():
    u1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
    u2 = uuid.UUID("22222222-2222-2222-2222-222222222222")
    u3 = uuid.UUID("33333333-3333-3333-3333-333333333333")

    pair_12 = canonical_pair(u1, u2)
    pair_13 = canonical_pair(u1, u3)
    pair_23 = canonical_pair(u2, u3)

    assert pair_12 != pair_13
    assert pair_12 != pair_23
    assert pair_13 != pair_23

    seed_12 = canonical_pair_seed(u1, 1, u2, 1)
    seed_13 = canonical_pair_seed(u1, 1, u3, 1)
    assert seed_12 != seed_13


def test_canonical_pair_seed_version_sensitivity():
    u1 = uuid.UUID("11111111-1111-1111-1111-111111111111")
    u2 = uuid.UUID("22222222-2222-2222-2222-222222222222")

    seed_v1 = canonical_pair_seed(u1, 1, u2, 1)
    seed_v2_a = canonical_pair_seed(u1, 2, u2, 1)
    seed_v2_b = canonical_pair_seed(u1, 1, u2, 2)

    assert seed_v1 != seed_v2_a
    assert seed_v1 != seed_v2_b
    assert seed_v2_a != seed_v2_b


def test_canonical_pair_self_rejection():
    u1 = uuid.UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(ValueError, match="Cannot pair a user with themselves"):
        canonical_pair(u1, u1)


def test_connections_router_wrapper_preserves_jester_api_exception():
    u1 = uuid.UUID("11111111-1111-1111-1111-111111111111")

    with pytest.raises(JesterAPIException) as exc_info:
        get_canonical_pair(u1, u1)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == "invalid_pair"
    assert exc_info.value.message == "Cannot connect with yourself"


def test_connections_router_alias_identity():
    assert get_canonical_pair_seed is canonical_pair_seed
