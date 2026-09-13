"""
Deterministic Canonical Pair Identity and Relationship Pair Seed.
Pure core domain primitives: zero HTTP, zero DB, zero application framework imports.
"""
import uuid


def canonical_pair(u1: uuid.UUID, u2: uuid.UUID) -> tuple[uuid.UUID, uuid.UUID]:
    """
    Returns (user_low, user_high) sorted deterministically by string representation of UUID.
    Guarantees canonical_pair(A, B) == canonical_pair(B, A).
    Raises ValueError if u1 == u2.
    """
    if u1 == u2:
        raise ValueError("Cannot pair a user with themselves")
    return (u1, u2) if str(u1) < str(u2) else (u2, u1)


def canonical_pair_seed(u1: uuid.UUID, ver1: int, u2: uuid.UUID, ver2: int) -> str:
    """
    Returns the canonical, symmetric, version-aware relationship pair seed.
    Guarantees canonical_pair_seed(A, verA, B, verB) == canonical_pair_seed(B, verB, A, verA).
    Format: "{user_low}:{user_high}:{ver_low}:{ver_high}"
    """
    if str(u1) < str(u2):
        return f"{u1}:{u2}:{ver1}:{ver2}"
    else:
        return f"{u2}:{u1}:{ver2}:{ver1}"
