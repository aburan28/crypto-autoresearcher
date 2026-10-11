"""RC-1 / Koblitz target generation (deterministic seeds)."""
from __future__ import annotations

import numpy as np


RC1 = {
    "n": 17,
    "irreducible": "t^17+t^3+1",
    "mod": (1 << 17) | (1 << 3) | 1,
    "A": 97044,
    "B": 126251,
    "group_order": 4 * 32603,
    "prime_order": 32603,
    "cofactor": 4,
}

KOBLITZ17 = {
    "n": 17,
    "irreducible": "t^17+t^3+1",
    "mod": (1 << 17) | (1 << 3) | 1,
    "A": 1,
    "B": 1,
    "group_order": 2 * 65587,
    "prime_order": 65587,
    "cofactor": 2,
}

SEED = 2026092731


def make_field():
    from gf2n import TableField

    return TableField(RC1["n"], RC1["mod"])


def make_curve(F, cell=RC1):
    from curve import Curve

    return Curve(F, cell["A"], cell["B"])


def find_generator(E, F, prime_order: int, cofactor: int, rng: np.random.Generator):
    """Find a point G of order prime_order (cofactor clearing)."""
    N = prime_order * cofactor
    for _ in range(10000):
        x = int(rng.integers(1, F.q))
        P = E.lift_x(x)
        if P is None:
            continue
        Q = E.mul(cofactor, P)
        if Q is None:
            continue
        # check order divides prime_order and Q != O
        if E.mul(prime_order, Q) is None:
            # likely order | prime_order; confirm not smaller by checking Q != O
            # and prime is prime so order is 1 or prime_order
            return Q
    raise RuntimeError("failed to find generator")


def subgroup_targets(E, F, G, n_targets: int, seed: int) -> list[dict]:
    """n_targets distinct prime-order subgroup targets from seed."""
    rng = np.random.default_rng(seed)
    prime = None
    # infer prime order from #E via trial — caller passes via cell
    out = []
    seen = set()
    while len(out) < n_targets:
        k = int(rng.integers(1, F.q))  # large enough range
        R = E.mul(k, G)
        if R is None:
            continue
        xR = int(R[0])
        if xR in seen:
            continue
        seen.add(xR)
        out.append({"idx": len(out), "k": k, "x_R": xR, "y_R": int(R[1])})
    return out


def frobenius_conjugates_x(F, xR: int, n: int = 17) -> list[int]:
    """Orbit x, x^2, x^4, ... under Frobenius."""
    orbit = []
    x = xR
    for _ in range(n):
        orbit.append(int(x))
        x = F.sqr(x)
    return orbit


def build_rc1_targets(n_targets: int = 50, seed: int = SEED) -> tuple:
    F = make_field()
    E = make_curve(F, RC1)
    rng = np.random.default_rng(seed)
    G = find_generator(E, F, RC1["prime_order"], RC1["cofactor"], rng)
    # re-seed for target draw so generator search entropy does not consume stream
    targets = subgroup_targets(E, F, G, n_targets, seed ^ 0xC0FFEE)
    return F, E, G, targets


def build_koblitz_targets(n_targets: int = 5, seed: int = SEED) -> tuple:
    F = make_field()
    E = make_curve(F, KOBLITZ17)
    rng = np.random.default_rng(seed + 17)
    G = find_generator(E, F, KOBLITZ17["prime_order"], KOBLITZ17["cofactor"], rng)
    targets = subgroup_targets(E, F, G, n_targets, seed ^ 0xA77711)
    for t in targets:
        t["conjugates_x"] = frobenius_conjugates_x(F, t["x_R"], 17)
    return F, E, G, targets
