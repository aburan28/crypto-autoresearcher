#!/usr/bin/env python3
"""Exact Rolle-pruned Weil-polynomial census for EXP-BINSTD-842864.

Integer/rational Sturm box test with square-free handling; Rolle DFS as in
the numerical census search order, without importing weil_census.py.
Sympy is used only for independent hit re-verification and optional sampling.

certificate.kind for all runs: none (structural census).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import resource
import sys
import time
from fractions import Fraction
from math import comb, factorial, gcd, lcm
from typing import Any

Q = 2
BOX = 2 * math.sqrt(Q)
# Rational brackets around 2*sqrt(2) (same as exact_targets.py)
INSIDE_N, INSIDE_D = 28284271, 10000000
OUTSIDE_N, OUTSIDE_D = 28284272, 10000000
INSIDE = Fraction(INSIDE_N, INSIDE_D)
OUTSIDE = Fraction(OUTSIDE_N, OUTSIDE_D)

LMFDB_UNFILTERED = {1: 5, 2: 35, 3: 215, 4: 1645, 5: 14325, 6: 164937}

# ---------------------------------------------------------------------------
# Polynomial helpers over Q (Fraction coefficients)
# ---------------------------------------------------------------------------


def _trim(c: list[Fraction]) -> list[Fraction]:
    i = 0
    while i < len(c) - 1 and c[i] == 0:
        i += 1
    return c[i:]


def _deriv(c: list[Fraction]) -> list[Fraction]:
    c = _trim(c)
    n = len(c) - 1
    if n <= 0:
        return [Fraction(0)]
    return _trim([c[i] * (n - i) for i in range(n)])


def _divmod_q(a: list[Fraction], b: list[Fraction]) -> tuple[list[Fraction], list[Fraction]]:
    a = _trim([Fraction(x) for x in a])
    b = _trim([Fraction(x) for x in b])
    if b == [Fraction(0)]:
        raise ZeroDivisionError
    q: list[Fraction] = [Fraction(0)]
    r = a[:]
    db = len(b) - 1
    while True:
        r = _trim(r)
        if r == [Fraction(0)] or len(r) - 1 < db:
            break
        term_c = r[0] / b[0]
        shift = len(r) - 1 - db
        term = [term_c] + [Fraction(0)] * shift
        n = max(len(q), len(term))
        q = [Fraction(0)] * (n - len(q)) + q
        term_pad = [Fraction(0)] * (n - len(term)) + term
        q = [x + y for x, y in zip(q, term_pad)]
        prod = [Fraction(0)] * (len(b) + len(term) - 1)
        for i, x in enumerate(b):
            for j, y in enumerate(term):
                prod[i + j] += x * y
        n = max(len(r), len(prod))
        r = [Fraction(0)] * (n - len(r)) + r
        prod = [Fraction(0)] * (n - len(prod)) + prod
        r = [x - y for x, y in zip(r, prod)]
    return _trim(q), _trim(r)


def _gcd_q(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    a = _trim([Fraction(x) for x in a])
    b = _trim([Fraction(x) for x in b])
    while b != [Fraction(0)]:
        _, r = _divmod_q(a, b)
        a, b = b, r
    if a != [Fraction(0)] and a[0] != 0:
        a = [x / a[0] for x in a]
    return a


def _exact_div_q(a: list[Fraction], b: list[Fraction]) -> list[Fraction]:
    q, r = _divmod_q(a, b)
    if _trim(r) != [Fraction(0)]:
        raise ValueError("not divisible")
    return q


def _to_int_coeffs(c: list[Fraction]) -> list[int]:
    c = _trim([Fraction(x) for x in c])
    if c == [Fraction(0)]:
        return [0]
    dens = [x.denominator for x in c]
    L = 1
    for d in dens:
        L = lcm(L, d)
    out = [int(x * L) for x in c]
    g = 0
    for x in out:
        g = gcd(g, abs(x))
    out = [x // g for x in out]
    if out[0] < 0:
        out = [-x for x in out]
    return out


def _sturm_seq(c: list[Fraction]) -> list[list[Fraction]]:
    f0 = _trim([Fraction(x) for x in c])
    f1 = _deriv(f0)
    seq = [f0]
    if f1 == [Fraction(0)]:
        return seq
    seq.append(f1)
    while True:
        _, rem = _divmod_q(seq[-2], seq[-1])
        rem = _trim([-x for x in rem])
        if rem == [Fraction(0)]:
            break
        seq.append(rem)
        if len(rem) <= 1:
            break
    return seq


def _eval(c: list[Fraction], x: Fraction) -> Fraction:
    v = Fraction(0)
    for a in c:
        v = v * x + a
    return v


def _sign(v: Fraction) -> int:
    if v == 0:
        return 0
    return 1 if v > 0 else -1


def _sign_at_inf(c: list[Fraction], plus: bool = True) -> int:
    c = _trim(c)
    if c == [Fraction(0)]:
        return 0
    s = _sign(c[0])
    deg = len(c) - 1
    if plus:
        return s
    return s if deg % 2 == 0 else -s


def _variations(signs: list[int]) -> int:
    f = [s for s in signs if s != 0]
    return sum(1 for i in range(len(f) - 1) if f[i] != f[i + 1])


def _count_roots(c: list[Fraction], lo: Fraction | None = None, hi: Fraction | None = None) -> int:
    seq = _sturm_seq(c)

    def sigma(point: Any) -> int:
        signs = []
        for f in seq:
            if point == "+inf":
                signs.append(_sign_at_inf(f, True))
            elif point == "-inf":
                signs.append(_sign_at_inf(f, False))
            else:
                signs.append(_sign(_eval(f, point)))
        return _variations(signs)

    if lo is None:
        return sigma("-inf") - sigma("+inf")
    return sigma(lo) - sigma(hi)


def _strip_boundary(coeffs: list[int]) -> list[int]:
    f = [Fraction(x) for x in coeffs]
    boundary = [Fraction(1), Fraction(0), Fraction(-4 * Q)]
    while len(_trim(f)) - 1 >= 2:
        q, r = _divmod_q(f, boundary)
        if _trim(r) == [Fraction(0)]:
            f = q
        else:
            break
    return _to_int_coeffs(f)


def _squarefree_part(coeffs: list[int]) -> list[int]:
    f = [Fraction(x) for x in coeffs]
    g = _gcd_q(f, _deriv(f))
    if len(_trim(g)) <= 1:
        return _to_int_coeffs(f)
    return _to_int_coeffs(_exact_div_q(f, g))


def _root_in_closed_box_deg1(c0: int, c1: int) -> tuple[bool, bool]:
    """c0 x + c1 = 0 => x = -c1/c0. Ambiguous if in (INSIDE, OUTSIDE] gap."""
    if c0 == 0:
        return False, False
    x = Fraction(-c1, c0)
    ax = abs(x)
    if ax <= INSIDE:
        return True, False
    if ax <= OUTSIDE:
        return True, True  # outside-bracket accepts; flag ambiguous
    return False, False


def _root_in_closed_box_deg2(c0: int, c1: int, c2: int) -> tuple[bool, bool]:
    """Both roots real and in closed box (Sturm on the quadratic)."""
    if c0 == 0:
        return _root_in_closed_box_deg1(c1, c2)
    disc = c1 * c1 - 4 * c0 * c2
    if disc < 0:
        return False, False
    if disc == 0:
        # double root at -c1/(2 c0)
        return _root_in_closed_box_deg1(2 * c0, c1)
    sfq = [Fraction(c0), Fraction(c1), Fraction(c2)]
    if _count_roots(sfq) != 2:
        return False, False
    inside = _count_roots(sfq, -INSIDE, INSIDE)
    outside = _count_roots(sfq, -OUTSIDE, OUTSIDE)
    if inside != outside:
        return outside == 2, True
    return inside == 2, False


def exact_real_rooted_in_box(coeffs: list[int]) -> tuple[bool, bool]:
    """Return (verdict, ambiguous_near_boundary).

    All roots real and in the closed interval [-2 sqrt q, 2 sqrt q].
    Multiple roots allowed (square-free part checked). Boundary roots
    +-2 sqrt q are accepted by stripping x^2 - 4q.
    """
    f = _strip_boundary(coeffs)
    if len(f) - 1 <= 0:
        return True, False
    sf = _squarefree_part(f)
    d = len(sf) - 1
    if d <= 0:
        return True, False
    if d == 1:
        return _root_in_closed_box_deg1(sf[0], sf[1])
    if d == 2:
        return _root_in_closed_box_deg2(sf[0], sf[1], sf[2])
    sfq = [Fraction(x) for x in sf]
    if _count_roots(sfq) != d:
        return False, False
    inside = _count_roots(sfq, -INSIDE, INSIDE)
    outside = _count_roots(sfq, -OUTSIDE, OUTSIDE)
    if inside != outside:
        return outside == d, True
    return inside == d, False


# ---------------------------------------------------------------------------
# Sympy independent re-verification (not used in hot path)
# ---------------------------------------------------------------------------


def sympy_exact_real_rooted_in_box(coeffs: list[int]) -> tuple[bool, bool]:
    import sympy as sp

    X = sp.Symbol("x")
    boundary = sp.Poly(X**2 - 4 * Q, X)
    inside = sp.Rational(INSIDE_N, INSIDE_D)
    outside = sp.Rational(OUTSIDE_N, OUTSIDE_D)
    poly = sp.Poly([sp.Integer(c) for c in coeffs], X)
    while poly.degree() >= 2:
        quotient, remainder = sp.div(poly, boundary, X)
        if remainder == 0:
            poly = sp.Poly(quotient, X)
        else:
            break
    if poly.degree() <= 0:
        return True, False
    _content, factors = poly.sqf_list()
    ambiguous = False
    for fac, _mult in factors:
        fac = sp.Poly(fac, X)
        deg = fac.degree()
        if deg <= 0:
            continue
        if fac.count_roots() != deg:
            return False, False
        inn = fac.count_roots(-inside, inside)
        out = fac.count_roots(-outside, outside)
        if inn != out:
            ambiguous = True
            if out != deg:
                return False, True
        elif inn != deg:
            return False, False
    return True, ambiguous


# ---------------------------------------------------------------------------
# Arithmetic: ceilings, multiples, place counts
# ---------------------------------------------------------------------------


def a_g_sequence(max_g: int) -> list[int]:
    """a_g from (3+2√2)^g + (3-2√2)^g = 2 a_g; recurrence u_g = 6 u_{g-1} - u_{g-2}."""
    # u_0 = 2, u_1 = 6; a_g = u_g / 2
    out = []
    u_prev2, u_prev1 = 2, 6
    for g in range(1, max_g + 1):
        if g == 1:
            u = 6
        else:
            u = 6 * u_prev1 - u_prev2
            u_prev2, u_prev1 = u_prev1, u
        out.append(u // 2)
    return out


def weil_ceiling(g: int) -> int:
    return 2 * a_g_sequence(g)[g - 1] - 1


def multiples_below_ceiling(g: int, modulus: int) -> list[int]:
    ceiling = weil_ceiling(g)
    return list(range(modulus, ceiling + 1, modulus))


def moebius(n: int) -> int:
    if n == 1:
        return 1
    factors = 0
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            x //= p
            if x % p == 0:
                return 0
            factors += 1
        p += 1 if p == 2 else 2
    if x > 1:
        factors += 1
    return -1 if factors % 2 else 1


def frobenius_charpoly_from_h(h: list[int], q: int = Q) -> list[int]:
    """P(T) = sum_{k=0}^g a_k T^k (T^2 + q)^{g-k}, monic degree 2g."""
    g = len(h) - 1
    P = [0] * (2 * g + 1)
    for k, a_k in enumerate(h):
        # (T^2 + q)^{g-k}
        m = g - k
        binom_row = [1]
        # coeffs of (T^2 + q)^m = sum_{j=0}^m C(m,j) q^{m-j} T^{2j}
        for j in range(m + 1):
            coef = comb(m, j) * (q ** (m - j))
            # multiply by a_k T^k => degree k + 2j
            deg = k + 2 * j
            P[deg] += a_k * coef
    # P stored low-degree-first above; convert to high-first monic
    # Actually we filled P[deg] with deg from 0..2g; reverse for [leading..]
    P_high = list(reversed(P))
    return P_high


def power_sums_from_charpoly(P_high: list[int], max_r: int) -> list[int]:
    """Newton sums p_r = sum alpha_i^r for monic P = T^n + c1 T^{n-1}+...+cn."""
    n = len(P_high) - 1
    # P_high = [1, c1, ..., cn]
    c = P_high  # c[0]=1
    p = [0] * (max_r + 1)
    for r in range(1, max_r + 1):
        s = 0
        for j in range(1, min(r, n) + 1):
            s -= c[j] * (p[r - j] if r - j > 0 else n if r - j == 0 and False else (n if j == r else p[r - j]))
        # Standard Newton:
        # For r <= n: p_r + c1 p_{r-1} + ... + c_{r-1} p_1 + r c_r = 0
        # For r > n: p_r + c1 p_{r-1} + ... + c_n p_{r-n} = 0
        if r <= n:
            s = 0
            for j in range(1, r):
                s += c[j] * p[r - j]
            s += r * c[r]
            p[r] = -s
        else:
            s = 0
            for j in range(1, n + 1):
                s += c[j] * p[r - j]
            p[r] = -s
    return p


def virtual_curve_and_place_counts(h: list[int], q: int = Q) -> dict[str, Any]:
    """Compute N_r and a_r for r=1..g. Does NOT claim Jacobian sufficiency."""
    g = len(h) - 1
    P = frobenius_charpoly_from_h(h, q)
    psums = power_sums_from_charpoly(P, g)
    N = {r: q**r + 1 - psums[r] for r in range(1, g + 1)}
    a: dict[int, Any] = {}
    for r in range(1, g + 1):
        s = sum(moebius(r // d) * N[d] for d in range(1, r + 1) if r % d == 0)
        if s % r != 0:
            a[r] = {
                "value_numerator": s,
                "div_r": r,
                "integral": False,
                "note": "non-integral place count",
            }
        else:
            a[r] = {"value": s // r, "nonnegative": (s // r) >= 0}
    return {
        "P": P,
        "N_r": {str(r): N[r] for r in range(1, g + 1)},
        "a_r": {str(r): a[r] for r in range(1, g + 1)},
        "all_a_r_nonnegative": all(a[r].get("nonnegative") is True for r in range(1, g + 1)),
        "jacobian_sufficiency_claimed": False,
        "note": "a_r>=0 is necessary not sufficient for being a Jacobian; undecided only",
    }


# ---------------------------------------------------------------------------
# Rolle-pruned enumerator
# ---------------------------------------------------------------------------


def coefficient_bounds(g: int) -> list[float]:
    return [comb(g, k) * (BOX**k) for k in range(g + 1)]


def census(
    g: int,
    modulus: int | None = None,
    filtered_only: bool = False,
    collect_all_classes: bool = False,
    progress_every: int = 100000,
    wall_limit_s: float | None = None,
    checkpoint_path: str | None = None,
    max_ambiguous_stored: int = 100,
) -> dict[str, Any]:
    """Enumerate integer real Weil polynomials of degree g over F_2.

    If modulus is set and filtered_only, only last-coefficient values with
    h(3) ≡ 0 (mod modulus) are tested. Unfiltered class count still requires
    filtered_only=False.
    """
    bounds = coefficient_bounds(g)
    found_classes: list[dict[str, Any]] = []
    class_count = 0
    hits: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    ambiguous_count = 0
    survivors = [0] * (g + 1)
    exact_tests = 0
    t0 = time.time()
    timed_out = False

    def maybe_timeout() -> bool:
        nonlocal timed_out
        if wall_limit_s is not None and (time.time() - t0) > wall_limit_s:
            timed_out = True
            return True
        return False

    def write_checkpoint() -> None:
        if not checkpoint_path:
            return
        ck = {
            "dimension": g,
            "exact_tests_performed": exact_tests,
            "classes_found": class_count,
            "hit_count": len(hits),
            "hits": hits,
            "ambiguous_count": ambiguous_count,
            "survivors_per_level": survivors,
            "wall_s": time.time() - t0,
            "timed_out": timed_out,
            "partial": True,
        }
        tmp = checkpoint_path + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(ck, fh)
        os.replace(tmp, checkpoint_path)

    def recurse(k: int, chosen: list[int]) -> None:
        nonlocal exact_tests, class_count, ambiguous_count
        if timed_out or maybe_timeout():
            return
        limit = int(bounds[k]) + 1
        if k == g and modulus is not None and filtered_only:
            # Pin a_g by congruence: h(3) ≡ 0 (mod modulus)
            partial_sum = sum(c * (Q + 1) ** (g - i) for i, c in enumerate(chosen))
            target_mod = (-partial_sum) % modulus
            candidates = []
            a = target_mod
            while a <= limit:
                candidates.append(a)
                a += modulus
            a = target_mod - modulus
            while a >= -limit:
                candidates.append(a)
                a -= modulus
            a_range = candidates
        else:
            a_range = range(-limit, limit + 1)

        for a_k in a_range:
            if timed_out:
                return
            partial = chosen + [a_k]
            derivative = [
                partial[i] * factorial(g - i) // factorial(k - i) for i in range(k + 1)
            ]
            exact_tests += 1
            if progress_every and exact_tests % progress_every == 0:
                print(
                    f"  g={g} k={k} tests={exact_tests} survivors={survivors} "
                    f"classes={class_count} hits={len(hits)} amb={ambiguous_count} "
                    f"wall={time.time()-t0:.1f}s",
                    flush=True,
                )
                write_checkpoint()
            verdict, is_amb = exact_real_rooted_in_box(derivative)
            if is_amb:
                ambiguous_count += 1
                if len(ambiguous) < max_ambiguous_stored:
                    ambiguous.append(
                        {"level": k, "partial": list(partial), "derivative": derivative}
                    )
            if not verdict:
                continue
            survivors[k] += 1
            if k == g:
                points = sum(c * (Q + 1) ** (g - i) for i, c in enumerate(partial))
                if points > 0:
                    class_count += 1
                    row = {"points": points, "h": list(partial)}
                    if collect_all_classes:
                        found_classes.append(row)
                    if modulus is not None and points % modulus == 0:
                        hits.append(row)
            else:
                recurse(k + 1, partial)

    recurse(1, [1])

    wall = time.time() - t0
    result = {
        "dimension": g,
        "modulus": modulus,
        "filtered_only": filtered_only,
        "classes_found": class_count,
        "classes_known_lmfdb": LMFDB_UNFILTERED.get(g),
        "unfiltered_matches_lmfdb": (
            class_count == LMFDB_UNFILTERED[g] if g in LMFDB_UNFILTERED and not filtered_only else None
        ),
        "hits": hits,
        "hit_count": len(hits),
        "ambiguous_near_boundary": ambiguous,
        "ambiguous_count": ambiguous_count,
        "ambiguous_stored": len(ambiguous),
        "survivors_per_level": survivors,
        "exact_tests_performed": exact_tests,
        "wall_s": wall,
        "timed_out": timed_out,
        "termination_reason": "timeout" if timed_out else "completed",
        "classes": found_classes if collect_all_classes else None,
        "partial": False,
    }
    if checkpoint_path:
        with open(checkpoint_path, "w") as fh:
            json.dump({**result, "checkpoint_final": True}, fh)
    return result


def enrich_hit(hit: dict[str, Any]) -> dict[str, Any]:
    h = hit["h"]
    places = virtual_curve_and_place_counts(h)
    out = dict(hit)
    out.update(places)
    # Independent sympy re-verify
    sym_v, sym_amb = sympy_exact_real_rooted_in_box(h)
    int_v, int_amb = exact_real_rooted_in_box(h)
    out["sympy_agreement"] = sym_v == int_v and sym_amb == int_amb and sym_v
    out["sympy_verdict"] = sym_v
    out["sympy_ambiguous"] = sym_amb
    out["integer_sturm_verdict"] = int_v
    out["integer_sturm_ambiguous"] = int_amb
    return out


def sample_pruned_dual_box(
    g: int, sample_size: int = 10000, seed: int = 0
) -> dict[str, Any]:
    """Compare integer Sturm vs sympy on random coefficient vectors in the box."""
    rng = random.Random(seed)
    bounds = coefficient_bounds(g)
    agreements = 0
    disagreements: list[Any] = []
    for _ in range(sample_size):
        coeffs = [1]
        for k in range(1, g + 1):
            lim = int(bounds[k]) + 1
            coeffs.append(rng.randint(-lim, lim))
        a = exact_real_rooted_in_box(coeffs)
        b = sympy_exact_real_rooted_in_box(coeffs)
        if a == b:
            agreements += 1
        else:
            if len(disagreements) < 20:
                disagreements.append({"h": coeffs, "integer_sturm": a, "sympy": b})
    return {
        "dimension": g,
        "sample_size": sample_size,
        "seed": seed,
        "agreements": agreements,
        "disagreements": len(disagreements),
        "disagreement_examples": disagreements,
        "all_agree": len(disagreements) == 0 and agreements == sample_size,
    }


# ---------------------------------------------------------------------------
# Baseline g<=4 via same enumerator (and optional exact_targets.py compare)
# ---------------------------------------------------------------------------


def baseline_g4(modulus: int = 131) -> dict[str, Any]:
    rows = []
    for g in range(1, 5):
        # Filtered census (modulus pin at last level for speed at g=4 still OK unfiltered)
        unf = census(g, modulus=None, filtered_only=False, collect_all_classes=False, progress_every=200000)
        filt = census(g, modulus=modulus, filtered_only=True, collect_all_classes=False, progress_every=200000)
        rows.append(
            {
                "dimension": g,
                "unfiltered_class_count": unf["classes_found"],
                "expected_unfiltered": LMFDB_UNFILTERED[g],
                "unfiltered_match": unf["classes_found"] == LMFDB_UNFILTERED[g],
                "filtered_hit_count": filt["hit_count"],
                "filtered_hits": filt["hits"],
                "ambiguous_count_unfiltered": unf["ambiguous_count"],
                "ambiguous_count_filtered": filt["ambiguous_count"],
                "survivors_unfiltered": unf["survivors_per_level"],
                "exact_tests_unfiltered": unf["exact_tests_performed"],
                "exact_tests_filtered": filt["exact_tests_performed"],
                "wall_s_unfiltered": unf["wall_s"],
                "wall_s_filtered": filt["wall_s"],
            }
        )
    return {
        "modulus": modulus,
        "expected_unfiltered": [5, 35, 215, 1645],
        "expected_filtered_hits": 0,
        "expected_scanned_note": "Rolle DFS test counts differ from exact_targets.py head-product scanned counts",
        "exact_targets_json_scanned": {3: 104, 4: 234220},
        "rows": rows,
        "all_unfiltered_match": all(r["unfiltered_match"] for r in rows),
        "all_filtered_zero": all(r["filtered_hit_count"] == 0 for r in rows),
        "all_ambiguous_zero": all(
            r["ambiguous_count_unfiltered"] == 0 and r["ambiguous_count_filtered"] == 0 for r in rows
        ),
    }


def peak_rss_bytes() -> int:
    # Linux: ru_maxrss is kilobytes
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["ceilings", "baseline", "census", "sample", "controls"], required=True)
    ap.add_argument("--dims", type=int, nargs="+", default=[5, 6])
    ap.add_argument("--modulus", type=int, default=131)
    ap.add_argument("--filtered-only", action="store_true")
    ap.add_argument("--json", type=str, default=None)
    ap.add_argument("--wall-limit", type=float, default=None)
    ap.add_argument("--sample-size", type=int, default=10000)
    ap.add_argument("--progress-every", type=int, default=100000)
    ap.add_argument("--checkpoint", type=str, default=None)
    args = ap.parse_args()

    # Self-tests
    assert exact_real_rooted_in_box([1, 0])[0]
    assert not exact_real_rooted_in_box([1, 0, -100])[0]
    assert exact_real_rooted_in_box([1, 0, -4 * Q])[0]
    assert exact_real_rooted_in_box([1, -4, 4])[0]  # (x-2)^2 multiple root

    if args.mode == "ceilings":
        ag = a_g_sequence(6)
        report = {
            "a_g": {str(g): ag[g - 1] for g in range(1, 7)},
            "ceilings": {str(g): 2 * ag[g - 1] - 1 for g in range(1, 7)},
            "multiples_of_131": {
                str(g): multiples_below_ceiling(g, 131) for g in range(1, 7)
            },
            "multiple_counts": {
                str(g): len(multiples_below_ceiling(g, 131)) for g in range(1, 7)
            },
            "expected_ceilings_g5_g6": [6725, 39201],
            "expected_counts_g5_g6": [51, 299],
            "match_g5": len(multiples_below_ceiling(5, 131)) == 51 and weil_ceiling(5) == 6725,
            "match_g6": len(multiples_below_ceiling(6, 131)) == 299 and weil_ceiling(6) == 39201,
        }
    elif args.mode == "baseline":
        report = baseline_g4(args.modulus)
    elif args.mode == "census":
        searches = []
        for g in args.dims:
            print(
                f"=== census g={g} filtered_only={args.filtered_only} modulus={args.modulus} ===",
                flush=True,
            )
            ck = args.checkpoint
            if ck is None and args.json:
                ck = args.json + f".g{g}.checkpoint.json"
            row = census(
                g,
                modulus=args.modulus,
                filtered_only=args.filtered_only,
                collect_all_classes=False,
                progress_every=args.progress_every,
                wall_limit_s=args.wall_limit,
                checkpoint_path=ck,
            )
            # Write pre-enrich snapshot so a sympy failure cannot erase the census.
            if args.json:
                pre = {
                    "base_field": Q,
                    "modulus": args.modulus,
                    "filtered_only": args.filtered_only,
                    "searches": [row],
                    "peak_rss_bytes": peak_rss_bytes(),
                    "pre_enrich": True,
                }
                pre_path = args.json + ".pre_enrich.json"
                with open(pre_path, "w") as fh:
                    json.dump(pre, fh)
                print(f"wrote pre-enrich snapshot {pre_path}", flush=True)
            enriched_hits = []
            for h in row["hits"]:
                try:
                    enriched_hits.append(enrich_hit(h))
                except Exception as exc:  # noqa: BLE001 — record and continue
                    bad = dict(h)
                    bad["enrich_error"] = repr(exc)
                    bad["sympy_agreement"] = False
                    enriched_hits.append(bad)
            row["hits"] = enriched_hits
            searches.append(row)
            print(
                f"g={g}: classes={row['classes_found']} hits={row['hit_count']} "
                f"amb={row['ambiguous_count']} tests={row['exact_tests_performed']} "
                f"wall={row['wall_s']:.2f}s timed_out={row['timed_out']}",
                flush=True,
            )
        report = {
            "base_field": Q,
            "modulus": args.modulus,
            "filtered_only": args.filtered_only,
            "searches": searches,
            "peak_rss_bytes": peak_rss_bytes(),
        }
    elif args.mode == "sample":
        report = {
            "samples": [sample_pruned_dual_box(g, args.sample_size) for g in args.dims],
            "peak_rss_bytes": peak_rss_bytes(),
        }
    elif args.mode == "controls":
        # Stage 2 nearby-object controls
        results = {}
        # modulus 5 at g=1 must find 5-point class
        c5 = census(1, modulus=5, filtered_only=True, collect_all_classes=True)
        results["mod5_g1"] = {
            "hit_count": c5["hit_count"],
            "hits": c5["hits"],
            "must_find_5_point_class": any(h["points"] == 5 for h in c5["hits"]),
            "classes_found_unfiltered_check": census(1, modulus=None)["classes_found"],
        }
        # modulus 1 returns all classes (every integer ≡ 0 mod 1)
        for g in [1, 2, 3]:
            unf = census(g, modulus=None)
            mod1 = census(g, modulus=1, filtered_only=True)
            results[f"mod1_g{g}"] = {
                "unfiltered": unf["classes_found"],
                "mod1_hits": mod1["hit_count"],
                "hits_equal_unfiltered": unf["classes_found"] == mod1["hit_count"],
            }
        # toy moduli ladder at g<=3
        toy = [17, 19, 23, 29, 31, 37, 41]
        ladder = {}
        for n in toy:
            ladder[str(n)] = {}
            for g in [1, 2, 3]:
                row = census(g, modulus=n, filtered_only=True, collect_all_classes=False)
                ladder[str(n)][f"g{g}"] = {
                    "hit_count": row["hit_count"],
                    "hits": row["hits"],
                    "ambiguous_count": row["ambiguous_count"],
                    "wall_s": row["wall_s"],
                }
        # Hand-derived expectations from IDEA-20260926-80209d
        results["toy_ladder"] = ladder
        results["hand_derived_expectations"] = {
            "elliptic_g1_any_ladder_prime": "empty (no prime >=7 in {1..5})",
            "surface_g2_present_only_at_19": True,
            "surface_class_at_19": {"h": [1, 3, 1], "points": 19},
        }
        # Check surface row
        g2_present = {n: ladder[str(n)]["g2"]["hit_count"] > 0 for n in toy}
        results["surface_presence"] = g2_present
        results["surface_only_19"] = g2_present.get(19) and not any(
            g2_present[n] for n in toy if n != 19
        )
        results["peak_rss_bytes"] = peak_rss_bytes()
        report = results
    else:
        raise SystemExit("unknown mode")

    text = json.dumps(report, indent=2)
    if args.json:
        os.makedirs(os.path.dirname(args.json) or ".", exist_ok=True)
        with open(args.json, "w") as fh:
            fh.write(text)
        print(f"wrote {args.json}", flush=True)
    else:
        print(text)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        import traceback

        traceback.print_exc()
        # Best-effort crash breadcrumb next to --json if present
        try:
            argv = sys.argv
            if "--json" in argv:
                jpath = argv[argv.index("--json") + 1]
                crumb = {
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                    "termination_reason": "implementation_error",
                }
                with open(jpath + ".crash.json", "w") as fh:
                    json.dump(crumb, fh, indent=2)
                print(f"wrote crash breadcrumb {jpath}.crash.json", flush=True)
        except Exception:
            pass
        raise
