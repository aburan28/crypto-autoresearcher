"""Core arithmetic for EXP-BINSTD-38e4ad Stages 1-2.

Notation lock (HOLD-S): n = field degree; m = Semaev arity; l = window dim.
certificate.kind is never emitted here — runpack sets kind: none.
"""
from __future__ import annotations

import random
from typing import Iterable

from curve import Curve, is_prime
from gf2n import Field, TableField, clmul, pmod

# Frozen RC-1 cell
N = 17
MODULUS = (1 << 17) | (1 << 3) | 1  # t^17 + t^3 + 1
A_KOBLITZ = 1
B_KOBLITZ = 1
L_ORDER_EXPECTED = 65587
GROUP_ORDER_EXPECTED = 131174
COFACTOR_H = 2

# Phi_17 factors over F_2 (canonical bit patterns; low bit = constant term)
# Verified by independent factorisation in factor_phi_n.
F1_PHI17 = 0b100111001  # x^8 + x^5 + x^4 + x^3 + 1
F2_PHI17 = 0b111010111  # x^8 + x^7 + x^6 + x^4 + x^2 + x + 1


def poly_mul_f2(a: int, b: int) -> int:
    return clmul(a, b)


def poly_mod_f2(a: int, m: int) -> int:
    return pmod(a, m)


def poly_deg(a: int) -> int:
    return a.bit_length() - 1 if a else -1


def poly_divmod_f2(a: int, b: int) -> tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError
    q = 0
    r = a
    db = poly_deg(b)
    while r and poly_deg(r) >= db:
        shift = poly_deg(r) - db
        q ^= 1 << shift
        r ^= b << shift
    return q, r


def poly_gcd_f2(a: int, b: int) -> int:
    while b:
        a, b = b, poly_divmod_f2(a, b)[1]
    return a


def is_irreducible_f2(f: int) -> bool:
    """Rabin-style irreducibility over F_2."""
    n = poly_deg(f)
    if n <= 0:
        return False
    x = 2  # t
    cur = x
    for i in range(1, n + 1):
        cur = poly_mod_f2(poly_mul_f2(cur, cur), f)
        if i <= n // 2:
            if poly_gcd_f2(f, cur ^ x) != 1:
                return False
    return cur == x


def phi_n_poly(n: int) -> int:
    """Phi_n for prime n: (x^n + 1) / (x + 1) over F_2 (= sum_{i=0}^{n-1} x^i)."""
    return (1 << n) - 1  # 1+x+...+x^{n-1}


def factor_phi_n_over_f2(n: int) -> list[int]:
    """Factor Phi_n over F_2 into irreducibles (n prime). Exhaustive for small n."""
    phi = phi_n_poly(n)
    factors: list[int] = []
    rem = phi
    # Try all monic candidates of degree d = ord_n(2)
    d = ord_n_of_2(n)
    max_cand = 1 << (d + 1)
    for cand in range(1 << d, max_cand):  # monic degree-d: bit d set
        if not is_irreducible_f2(cand):
            continue
        while rem != 1:
            q, r = poly_divmod_f2(rem, cand)
            if r == 0:
                factors.append(cand)
                rem = q
            else:
                break
        if rem == 1:
            break
    if rem != 1:
        raise RuntimeError(f"incomplete Phi_{n} factorisation; rem={bin(rem)}")
    factors.sort()
    return factors


def ord_n_of_2(n: int) -> int:
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be odd > 2")
    nm1 = n - 1
    # least d | (n-1) with 2^d ≡ 1 mod n
    divisors = []
    for i in range(1, int(nm1**0.5) + 1):
        if nm1 % i == 0:
            divisors.append(i)
            if i != nm1 // i:
                divisors.append(nm1 // i)
    for d in sorted(divisors):
        if pow(2, d, n) == 1:
            return d
    raise ValueError(f"ord_{n}(2) not found")


def verify_ord_n_2(n: int, d: int) -> bool:
    if d <= 0 or pow(2, d, n) != 1:
        return False
    # prime factors of d
    x = d
    primes = []
    p = 2
    while p * p <= x:
        if x % p == 0:
            primes.append(p)
            while x % p == 0:
                x //= p
        p = 3 if p == 2 else p + 2
    if x > 1:
        primes.append(x)
    for p in primes:
        if pow(2, d // p, n) == 1:
            return False
    return True


def stable_dimensions(n: int, d: int) -> dict:
    f = (n - 1) // d
    dims = []
    for b in range(f + 1):
        dims.append(b * d)
        dims.append(b * d + 1)
    dims = sorted(set(dims))
    mid = [x for x in dims if x not in (0, 1, n - 1, n)]
    return {
        "ord_n_2": d,
        "phi_factor_count": f,
        "phi_factor_degree": d,
        "stable_dimensions": dims,
        "mid_dimensions": mid,
        "mid_lane_empty": len(mid) == 0,
    }


def apply_poly_frobenius(F: Field, poly: int, x: int) -> int:
    """Evaluate poly(tau) at x where tau = squaring: sum p_i x^{2^i}."""
    acc = 0
    y = x
    p = poly
    while p:
        if p & 1:
            acc ^= y
        y = F.sqr(y)
        p >>= 1
    return acc


def ker_g_tau(F: Field, g: int) -> list[int]:
    """All field elements in ker g(tau)."""
    return [x for x in range(F.q) if apply_poly_frobenius(F, g, x) == 0]


def tau_stability_check(F: Field, V: Iterable[int]) -> dict:
    Vset = set(V)
    basis = []
    # Extract an F2-basis by greedy bit independence on the vector space
    # represented as integers (standard basis of F_{2^n}).
    # For stability we only need: for every v in V, v^2 in V.
    leave = []
    for v in sorted(Vset):
        sq = F.sqr(v)
        if sq not in Vset:
            leave.append({"v": v, "v_sq": sq})
    # Also check a spanning set: take linearly independent elements
    span = []
    for v in sorted(Vset):
        # gaussian on bit vectors
        x = v
        for b in span:
            # reduce
            # find pivot
            pass
        # simpler: just verify full set closed under squaring (exact for finite V)
        pass
    closed = len(leave) == 0
    dim = None
    # compute dim via gaussian elimination over F2
    mat = sorted(Vset)
    rank = 0
    used = []
    for v in mat:
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        # lowest set bit as pivot
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        rank += 1
    return {
        "pass": closed,
        "leave_count": len(leave),
        "leave_examples": leave[:5],
        "dim_V": rank,
        "card_V": len(Vset),
        "expected_card": 1 << rank if closed else None,
    }


def frobenius_point(P):
    """Coordinate-wise squaring (x,y) -> (x^2, y^2). Not necessarily on E."""
    if P is None:
        return None
    x, y = P
    # squaring in char 2 is linear: x^2 is bit-interleave; use field sqr via int
    # We need the field — caller should use curve.F.sqr
    raise NotImplementedError("use frobenius_point_F")


def frobenius_point_F(F: Field, P):
    if P is None:
        return None
    x, y = P
    return (F.sqr(x), F.sqr(y))


def build_koblitz_curve() -> tuple[TableField, Curve]:
    F = TableField(N, MODULUS)
    E = Curve(F, A_KOBLITZ, B_KOBLITZ)
    return F, E


def verify_group_order(E: Curve) -> dict:
    order = E.count_by_trace()
    l_order = order // COFACTOR_H
    return {
        "group_order_E": order,
        "cofactor_h": COFACTOR_H,
        "l_order": l_order,
        "l_order_prime": is_prime(l_order),
        "matches_frozen": order == GROUP_ORDER_EXPECTED and l_order == L_ORDER_EXPECTED,
        "frozen_expected": {
            "group_order_E": GROUP_ORDER_EXPECTED,
            "l_order": L_ORDER_EXPECTED,
            "cofactor_h": COFACTOR_H,
        },
    }


def find_generator(E: Curve, l_order: int, seed: int):
    """Find a point G of order l_order (prime-order subgroup generator)."""
    rng = random.Random(seed ^ 0x4731)
    F = E.F
    for _ in range(100000):
        x = rng.randrange(1, F.q)
        P = E.lift_x(x)
        if P is None:
            continue
        G = E.mul(COFACTOR_H, P)
        if G is None:
            continue
        if E.mul(l_order, G) is None:
            return G
    raise RuntimeError("failed to find order-l generator")


def random_targets(E: Curve, G, l_order: int, n_targets: int, seed: int) -> list:
    rng = random.Random(seed)
    out = []
    for _ in range(n_targets):
        k = rng.randrange(1, l_order)
        out.append(E.mul(k, G))
    return out


def build_factor_base(E: Curve, V: list[int]) -> dict:
    """Points with x in V ∩ x(E), both signs. Index by point tuple."""
    F = E.F
    Vset = set(V)
    points = []
    x_e = []
    for x in sorted(Vset):
        P = E.lift_x(x)
        if P is None:
            continue
        x_e.append(x)
        points.append(P)
        N = E.neg(P)
        if N != P:
            points.append(N)
    point_set = set(points)
    return {
        "V": sorted(Vset),
        "x_E_cap_V": x_e,
        "points": points,
        "point_set": point_set,
        "n_x": len(x_e),
        "n_points": len(points),
    }


def solution_set_S(E: Curve, R, fb: dict) -> set:
    """Unordered pairs {x1,x2} (as frozenset) with some lifts summing to ±R.

    For x1==x2 use frozenset with one element plus a tag via tuple (x,x).
    Represent as sorted tuple (min,max) always.
    """
    if R is None:
        return set()
    Rneg = E.neg(R)
    targets = (R, Rneg)
    S = set()
    pts = fb["points"]
    pset = fb["point_set"]
    for P1 in pts:
        for T in targets:
            Q = E.sub(T, P1)
            if Q in pset:
                x1, x2 = P1[0], Q[0]
                S.add((x1, x2) if x1 <= x2 else (x2, x1))
    return S


def square_tuple(F: Field, pair: tuple[int, int]) -> tuple[int, int]:
    a, b = F.sqr(pair[0]), F.sqr(pair[1])
    return (a, b) if a <= b else (b, a)


def census_metrics(E: Curve, targets: list, fb: dict) -> dict:
    """Compute closure_fraction, conjugate_overlap, equivariance_agreement."""
    F = E.F
    n_total = len(targets)
    n_sigma_pm = 0
    n_eligible = 0
    n_empty = 0
    n_closed = 0  # nonempty + square(S)subseteq S
    n_overlap = 0
    n_sq_tuples = 0
    n_sq_in_Ssigma = 0
    n_sq_in_S = 0
    a2_alarms = []

    # Cache S(R) and S(sigma(R))
    for idx, R in enumerate(targets):
        Rsig = frobenius_point_F(F, R)
        # sigma(R) must be on E for Koblitz; track
        on_e = E.on_curve(Rsig)
        if on_e and (Rsig == R or Rsig == E.neg(R)):
            n_sigma_pm += 1
            continue
        n_eligible += 1
        S_R = solution_set_S(E, R, fb)
        S_sig = solution_set_S(E, Rsig, fb) if on_e else set()
        if not S_R:
            n_empty += 1
        closed = bool(S_R) and all(square_tuple(F, t) in S_R for t in S_R)
        if closed:
            n_closed += 1
            a2_alarms.append({"target_index": idx, "kind": "closure", "label": "MEASURED"})
        overlap = bool(S_R & S_sig)
        if overlap:
            n_overlap += 1
            a2_alarms.append({"target_index": idx, "kind": "overlap", "label": "MEASURED"})
        for t in S_R:
            st = square_tuple(F, t)
            n_sq_tuples += 1
            if st in S_R:
                n_sq_in_S += 1
            if st in S_sig:
                n_sq_in_Ssigma += 1

    closure_fraction = (n_closed / n_eligible) if n_eligible else None
    # conjugate_overlap: COUNT of eligible R with nonempty intersection (spec unit: count)
    conjugate_overlap = n_overlap
    equivariance_agreement = (
        (n_sq_in_Ssigma / n_sq_tuples) if n_sq_tuples else None
    )
    return {
        "n_targets_drawn": n_total,
        "n_targets_sigma_pm_R": n_sigma_pm,
        "n_targets_eligible": n_eligible,
        "n_targets_empty_S": n_empty,
        "n_targets_closed_nonempty": n_closed,
        "closure_fraction": closure_fraction,
        "conjugate_overlap": conjugate_overlap,
        "equivariance_agreement": equivariance_agreement,
        "n_squared_tuples": n_sq_tuples,
        "n_squared_in_S_R": n_sq_in_S,
        "n_squared_in_S_sigma": n_sq_in_Ssigma,
        "a2_alarms": a2_alarms,
        "A2_alarm": len(a2_alarms) > 0,
        "label": "MEASURED",
    }


def leave_V_fraction(F: Field, V: list[int]) -> dict:
    Vset = set(V)
    leave = sum(1 for v in Vset if F.sqr(v) not in Vset)
    return {
        "card_V": len(Vset),
        "leave_count": leave,
        "leave_Vprime_fraction": leave / len(Vset) if Vset else None,
        "label": "MEASURED",
    }


def random_subspace(F: Field, dim: int, seed: int, forbid_stable: list[set[int]] | None = None) -> list[int]:
    """Random dim-dimensional F2-subspace of F_{2^n} as list of elements."""
    rng = random.Random(seed)
    n = F.n
    for _attempt in range(1000):
        # random full-rank n x dim generator matrix columns
        cols = []
        while len(cols) < dim:
            v = rng.randrange(1, 1 << n)
            # reduce against existing
            x = v
            for p, piv in cols:
                if x & (1 << p):
                    x ^= piv
            if x == 0:
                continue
            p = (x & -x).bit_length() - 1
            cols.append((p, x))
        # enumerate subspace
        elems = []
        for mask in range(1 << dim):
            acc = 0
            for i, (_p, piv) in enumerate(cols):
                if mask & (1 << i):
                    acc ^= piv
            elems.append(acc)
        S = set(elems)
        if forbid_stable:
            if any(S == fs for fs in forbid_stable):
                continue
        # require not tau-stable
        if all(F.sqr(v) in S for v in S):
            continue
        return sorted(S)
    raise RuntimeError("failed to sample non-stable random subspace")


def h2_counts(E: Curve, V: list[int], n: int) -> dict:
    """Direct vs per-orbit |x(E) ∩ V|."""
    F = E.F
    Vset = set(V)
    x_cap = [x for x in sorted(Vset) if E.is_x_coord(x)]
    direct = len(x_cap)
    # orbits under squaring
    seen = set()
    orbit_rep_count = 0
    orbit_details = []
    for x in x_cap:
        if x in seen:
            continue
        orb = []
        y = x
        for _ in range(n + 1):
            if y in seen:
                break
            seen.add(y)
            orb.append(y)
            y = F.sqr(y)
            if y == x:
                break
        # only count x that stay in x_cap (they should if V stable and endomorphism)
        orb_in = [z for z in orb if z in set(x_cap)]
        orbit_rep_count += len(orb_in)  # contribute full orbit size via one rep * |orb|
        # Better: one representative contributes |orb ∩ x_cap|
        # For agreement: sum over orbit reps of |orb| should equal direct
        orbit_details.append({"rep": x, "orbit_size": len(orb), "orbit_in_xcap": len(orb_in)})
    # Correct per-orbit method: pick one rep per orbit; sum orbit sizes
    seen2 = set()
    per_orbit_sum = 0
    n_orbits = 0
    fixed_points = []
    for x in x_cap:
        if x in seen2:
            continue
        orb = []
        y = x
        for _ in range(n + 2):
            orb.append(y)
            y = F.sqr(y)
            if y == x:
                break
        for z in orb:
            seen2.add(z)
        # all orb elements should be in x_cap if endomorphism preserves E
        per_orbit_sum += len(orb)
        n_orbits += 1
        if len(orb) == 1:
            fixed_points.append(x)
    return {
        "direct_count": direct,
        "per_orbit_sum": per_orbit_sum,
        "n_orbits": n_orbits,
        "fixed_points_in_xcap": fixed_points,
        "h2_count_agreement": direct == per_orbit_sum,
        "label": "MEASURED",
    }


def select_V_f1(F: Field) -> tuple[int, list[int], dict]:
    """Build V = ker f1(tau); verify factorisation matches frozen patterns."""
    factors = factor_phi_n_over_f2(N)
    factors_sorted = sorted(factors)
    expected = sorted([F1_PHI17, F2_PHI17])
    fact_ok = factors_sorted == expected
    g = F1_PHI17  # choose f1
    V = ker_g_tau(F, g)
    stab = tau_stability_check(F, V)
    return g, V, {
        "phi17_factors_computed": [bin(f) for f in factors_sorted],
        "phi17_factors_frozen": [bin(f) for f in expected],
        "factorisation_matches_frozen": fact_ok,
        "chosen_g": bin(g),
        "chosen_label": "f1",
        "tau_stability": stab,
    }
