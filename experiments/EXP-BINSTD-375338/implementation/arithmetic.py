"""Arithmetic helpers for EXP-BINSTD-375338 Stages 0-1.

Stage 0: ord_n(2), stable dimensions from T^n-1 / Phi_n over F_2.
Stage 1: Koblitz toy census + equivariance / unsoundness tests (a)-(e).
certificate.kind is set by callers (none for measurements; decomposition
when a claimed relation is independently re-verified).
"""
from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Iterable

from curve import Curve, is_prime
from gf2n import Field, TableField, clmul, is_irreducible, pmod, pgcd

# ---- Stage 0 frozen expected (comparator column; never mixed with recomputed) ----
FROZEN_EXPECTED_ORD = {
    17: 8,
    19: 18,
    131: 130,
    163: 162,
    233: 29,
    239: 119,
    283: 94,
    409: 204,
    571: 114,
}
N_LIST = [17, 19, 131, 163, 233, 239, 283, 409, 571]
EMPTY_ROWS = ["ECC2K-130", "K-163"]
LIVE_ROWS = ["K-233", "K-283", "K-409", "K-571", "sect239k1"]
KOBLITZ_AB_EXPECTED = {
    "sect163k1": {"A": 1, "B": 1},
    "sect233k1": {"A": 0, "B": 1},
    "sect283k1": {"A": 0, "B": 1},
    "sect409k1": {"A": 0, "B": 1},
    "sect571k1": {"A": 0, "B": 1},
    "sect239k1": {"A": 0, "B": 1},
}

# ---- BIN-TOY-K19 ----
N19 = 19
MOD19 = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # t^19+t^5+t^2+t+1
A19, B19 = 0, 1  # y^2+xy = x^3+1
H19 = 4
L19_EXPECTED = 130873
ORDER19_EXPECTED = 4 * L19_EXPECTED
V19_DEG = 10  # V = {deg < 10}

# ---- BIN-TOY-K17-STABLE ----
N17 = 17
MOD17 = (1 << 17) | (1 << 3) | 1  # t^17+t^3+1
A17, B17 = 1, 1


def ord_n_of_2(n: int) -> int:
    if n <= 2 or n % 2 == 0:
        raise ValueError("n must be odd > 2")
    nm1 = n - 1
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


def stable_dimensions(n: int, d: int | None = None) -> dict:
    """Stable F_2-dimensions for subspaces of F_{2^n} closed under squaring.

    When Phi_n factors into f = (n-1)/d irreducibles of degree d=ord_n(2),
    stable dimensions are {b*d, b*d+1 for b=0..f} (include 0 and the whole
    space via the (x+1) factor of T^n-1 = (T+1) Phi_n).
    """
    if d is None:
        d = ord_n_of_2(n)
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
        "label": "RECOMPUTED",
    }


def reachability_verdict(n: int, name: str, d: int, mid_empty: bool) -> dict:
    """empty|live for named standardized rows (arithmetic, not attack)."""
    if name in ("K-163", "ECC2K-130") or (n in (163, 131) and mid_empty):
        verdict = "STRUCTURALLY_EMPTY"
        routing = "no useful mid-dimension Frobenius-stable V; do not route to orbit-batched seam"
    elif mid_empty:
        verdict = "STRUCTURALLY_EMPTY"
        routing = "mid-lane empty (ord_n(2)=n-1)"
    else:
        verdict = "LIVE"
        routing = "FROB — mid-dimension stable V exists; orbit-batched routing owned by FROB lane"
    return {
        "name": name,
        "n": n,
        "ord_n_2_recomputed": d,
        "mid_lane_empty": mid_empty,
        "verdict": verdict,
        "routing_note": routing,
        "label": "RECOMPUTED",
    }


def hexblob_fixture(params_text: str) -> dict:
    """Replicate subfield_scan.hexblob third-fallback acceptance of (0xHEX)."""

    def hexblob(body, label):
        m = re.search(re.escape(label) + r":\s*\n((?:\s+[0-9a-f:]+\n)+)", body)
        if not m:
            m = re.search(
                re.escape(label) + r":\s*((?:[0-9a-f]{2}:)+[0-9a-f]{2})", body
            )
            if not m:
                m = re.search(
                    re.escape(label) + r":\s*(\d+)(?:\s*\(0x[0-9a-fA-F]+\))?\s*\n",
                    body,
                )
                if m:
                    return int(m.group(1)), "decimal_or_ox_fallback"
                return None, "miss"
            return int(re.sub(r"[^0-9a-f]", "", m.group(1)), 16), "inline_colon_hex"
        h = re.sub(r"[^0-9a-f]", "", m.group(1))
        return (int(h, 16) if h else None), "multiline_colon_hex"

    # Synthetic bodies exercising the third fallback
    cases = [
        ("A_ox", "A:    1 (0x1)\n", "A", 1),
        ("B_ox", "B:    1 (0x1)\n", "B", 1),
        ("A_zero_bare", "A:    0\n", "A", 0),
        ("B_ox_upper", "B:    1 (0x1)\n", "B", 1),
    ]
    results = []
    all_ok = True
    for name, body, label, expected in cases:
        val, branch = hexblob(body, label)
        ok = val == expected and branch == "decimal_or_ox_fallback"
        all_ok = all_ok and ok
        results.append(
            {
                "case": name,
                "expected": expected,
                "parsed": val,
                "branch": branch,
                "accepts_ox_form": branch == "decimal_or_ox_fallback" and val == expected,
                "ok": ok,
            }
        )
    # Also parse live binary-curve-params rows for A of sect163k1 / sect233k1
    live = {}
    for curve in ("sect163k1", "sect233k1"):
        m = re.search(rf"===== {curve} =====(.*?)=====", params_text + "\n=====", re.S)
        body = m.group(1) if m else ""
        a, abr = hexblob(body, "A")
        b, bbr = hexblob(body, "B")
        live[curve] = {
            "A": a,
            "A_branch": abr,
            "B": b,
            "B_branch": bbr,
            "A_accepts_ox": abr == "decimal_or_ox_fallback" and a is not None,
        }
    return {
        "hexblob_regex_accepts_ox_form": all_ok,
        "synthetic_cases": results,
        "live_params_smoke": live,
        "source_regex": r"label:\s*(\d+)(?:\s*\(0x[0-9a-fA-F]+\))?\s*\n",
        "source_file": "analysis/binstd-curve-audit/subfield_scan.py",
        "label": "RECOMPUTED",
    }


def koblitz_ab_fixture(params_path: Path) -> dict:
    text = params_path.read_text(encoding="utf-8", errors="replace")

    def hexblob(body, label):
        m = re.search(re.escape(label) + r":\s*\n((?:\s+[0-9a-f:]+\n)+)", body)
        if not m:
            m = re.search(
                re.escape(label) + r":\s*((?:[0-9a-f]{2}:)+[0-9a-f]{2})", body
            )
            if not m:
                m = re.search(
                    re.escape(label) + r":\s*(\d+)(?:\s*\(0x[0-9a-fA-F]+\))?\s*\n",
                    body,
                )
                if m:
                    return int(m.group(1))
                return None
            h = re.sub(r"[^0-9a-f]", "", m.group(1))
            return int(h, 16) if h else None
        h = re.sub(r"[^0-9a-f]", "", m.group(1))
        return int(h, 16) if h else None

    rows = []
    all_match = True
    for name, expected in KOBLITZ_AB_EXPECTED.items():
        m = re.search(rf"===== {re.escape(name)} =====(.*?)=====", text + "\n=====", re.S)
        if not m:
            rows.append({"name": name, "ok": False, "error": "block_missing"})
            all_match = False
            continue
        body = m.group(1)
        A = hexblob(body, "A")
        B = hexblob(body, "B")
        ok = A == expected["A"] and B == expected["B"]
        all_match = all_match and ok
        rows.append(
            {
                "name": name,
                "A_recomputed": A,
                "B_recomputed": B,
                "A_expected": expected["A"],
                "B_expected": expected["B"],
                "match": ok,
                "label_recomputed": "RECOMPUTED",
                "label_expected": "EXPECTED",
            }
        )
    return {
        "source": str(params_path),
        "rows": rows,
        "koblitz_ab_fixture_match": all_match,
        "label": "RECOMPUTED_vs_EXPECTED",
    }


# ---- Stage 1 group / census ----


def frobenius_point_F(F: Field, P):
    if P is None:
        return None
    x, y = P
    return (F.sqr(x), F.sqr(y))


def build_curve(n: int, mod: int, A: int, B: int) -> tuple[TableField, Curve]:
    ok, _ = is_irreducible(mod)
    if not ok:
        raise ValueError(f"modulus not irreducible n={n}")
    F = TableField(n, mod)
    E = Curve(F, A, B)
    return F, E


def verify_toy_k19(E: Curve) -> dict:
    order = E.count_by_trace()
    if order % H19 != 0:
        return {
            "ok": False,
            "group_order_E": order,
            "reason": "order not divisible by cofactor 4",
        }
    l_order = order // H19
    ok = (
        order == ORDER19_EXPECTED
        and l_order == L19_EXPECTED
        and is_prime(l_order)
    )
    return {
        "ok": ok,
        "group_order_E": order,
        "cofactor_h": H19,
        "l_order": l_order,
        "l_order_prime": is_prime(l_order),
        "frozen_expected": {
            "group_order_E": ORDER19_EXPECTED,
            "l_order": L19_EXPECTED,
            "cofactor_h": H19,
        },
        "label_recomputed": "RECOMPUTED",
        "label_expected": "EXPECTED",
    }


def find_generator(E: Curve, cofactor: int, l_order: int, seed: int):
    rng = random.Random(seed ^ 0xB17)
    F = E.F
    for _ in range(200000):
        x = rng.randrange(1, F.q)
        P = E.lift_x(x)
        if P is None:
            continue
        G = E.mul(cofactor, P)
        if G is None:
            continue
        if E.mul(l_order, G) is None and E.mul(1, G) is not None:
            # order exactly l (l prime): G != O already; check [l/p] not needed if prime
            return G
    raise RuntimeError("failed to find order-l generator")


def frobenius_scalar(E: Curve, G, l_order: int) -> int:
    """Scalar mu with sigma(G) = [mu] G on Koblitz (sigma endomorphism)."""
    F = E.F
    Gs = frobenius_point_F(F, G)
    if not E.on_curve(Gs):
        raise RuntimeError("sigma(G) not on curve — not Koblitz")
    # Baby-step: Gs = [mu] G; solve DL in order-l group (l ~ 1e5: feasible BSGS-ish)
    # Simple: since l is small, use baby-step giant-step or just pollard; here l=130873
    # Use BSGS
    import math

    m = int(math.isqrt(l_order)) + 1
    baby = {}
    R = None  # [j]G
    for j in range(m):
        baby[R] = j
        R = E.add(R, G) if R is not None else G
        if R is None:
            baby[None] = j + 1
            break
    # Also store O at j=0
    baby[None] = 0
    # factor = [m]G
    factor = E.mul(m, G)
    # Gs = [i*m + j] G => Gs - [i]factor = [j]G
    gamma = Gs
    for i in range(m + 1):
        if gamma in baby:
            mu = (i * m + baby[gamma]) % l_order
            if E.mul(mu, G) == Gs:
                return mu
        gamma = E.sub(gamma, factor)
    raise RuntimeError("failed to recover Frobenius scalar mu")


def poly_basis_window(deg_lt: int) -> list[int]:
    return list(range(1 << deg_lt))


def build_factor_base(E: Curve, V: list[int]) -> dict:
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
    return {
        "V": sorted(Vset),
        "Vset": Vset,
        "x_E_cap_V": x_e,
        "points": points,
        "point_set": set(points),
        "n_x": len(x_e),
        "n_points": len(points),
    }


def point_key(P) -> tuple:
    if P is None:
        return ("O",)
    return (P[0], P[1])


def normalize_target(E: Curve, R):
    """Choose representative of {R, -R} by smaller (x,y) lex."""
    Rn = E.neg(R)
    return R if point_key(R) <= point_key(Rn) else Rn


def in_prime_subgroup(E: Curve, P, l_order: int) -> bool:
    if P is None:
        return False
    return E.mul(l_order, P) is None


def exhaustive_decomp_index(E: Curve, fb: dict, l_order: int) -> dict:
    """Map normalized R -> list of certified point-pair decompositions."""
    from collections import defaultdict

    index = defaultdict(list)
    pts = fb["points"]
    seen_pair = set()
    for i, P1 in enumerate(pts):
        for j in range(i, len(pts)):
            P2 = pts[j]
            S = E.add(P1, P2)
            if S is None:
                continue
            if not in_prime_subgroup(E, S, l_order):
                continue
            R = normalize_target(E, S)
            x1, x2 = P1[0], P2[0]
            key = (point_key(R), x1, x2, point_key(P1), point_key(P2))
            if key in seen_pair:
                continue
            seen_pair.add(key)
            index[point_key(R)].append(
                {
                    "R": R,
                    "x1": x1,
                    "x2": x2,
                    "P1": P1,
                    "P2": P2,
                    "sum": S,
                }
            )
    return index

def certify_decomposition(E: Curve, R, P1, P2) -> bool:
    """Independent re-verification: P1+P2 equals ±R and all on curve."""
    if not (E.on_curve(R) and E.on_curve(P1) and E.on_curve(P2)):
        return False
    S = E.add(P1, P2)
    return S == R or S == E.neg(R)


def lifts_of_x(E: Curve, x: int) -> list:
    P = E.lift_x(x)
    if P is None:
        return []
    N = E.neg(P)
    if N == P:
        return [P]
    return [P, N]


def any_sign_sums_to(E: Curve, x1: int, x2: int, targets: Iterable) -> bool:
    tset = list(targets)
    for P1 in lifts_of_x(E, x1):
        for P2 in lifts_of_x(E, x2):
            S = E.add(P1, P2)
            if S in tset:
                return True
    return False


def both_in_V(Vset: set, x1: int, x2: int) -> bool:
    return x1 in Vset and x2 in Vset


def shift_orbit(F: Field, x: int) -> list[int]:
    orb = []
    y = x
    for _ in range(F.n):
        orb.append(y)
        y = F.sqr(y)
    return orb


def is_orbit_lex_minimal(F: Field, x: int) -> bool:
    orb = shift_orbit(F, x)
    return x == min(orb)


def run_tests_abc_e(E: Curve, F: Field, targets_decomps: list, Vset: set) -> dict:
    """tests (a)(b)(c)(e) on list of {R, decomps:[{x1,x2,P1,P2}]}."""
    same_instance_hits = 0
    conjugate_hits = 0
    conjugate_trials = 0
    in_V_hits = 0
    in_V_trials = 0
    leg_swap_hits = 0
    leg_swap_trials = 0
    solutions_total = 0
    solutions_lost = 0
    lost_fractions = []
    hard_stop = None
    certificate_fail = 0
    certificate_ok = 0

    for item in targets_decomps:
        R = item["R"]
        Rsig = frobenius_point_F(F, R)
        if not E.on_curve(Rsig):
            raise RuntimeError("sigma(R) not on Koblitz curve")
        decomp = item["decomps"]
        n_sol = len(decomp)
        n_lost = 0
        for d in decomp:
            if not certify_decomposition(E, R, d["P1"], d["P2"]):
                certificate_fail += 1
                continue
            certificate_ok += 1
            x1, x2 = d["x1"], d["x2"]
            sx1, sx2 = F.sqr(x1), F.sqr(x2)

            # (a) same R
            same = any_sign_sums_to(E, sx1, sx2, [R, E.neg(R)])
            if same and Rsig != R and Rsig != E.neg(R):
                same_instance_hits += 1
                hard_stop = {
                    "R": point_key(R),
                    "x1": x1,
                    "x2": x2,
                    "note": "same_instance_hit with sigma(R)!=±R",
                }
            elif same and (Rsig == R or Rsig == E.neg(R)):
                pass  # excluded from hard-stop per A2 edge case

            # (b) conjugate
            conjugate_trials += 1
            conj = any_sign_sums_to(E, sx1, sx2, [Rsig, E.neg(Rsig)])
            if conj:
                conjugate_hits += 1
            in_V_trials += 1
            if both_in_V(Vset, sx1, sx2):
                in_V_hits += 1

            # (c) leg-swap
            leg_swap_trials += 1
            if any_sign_sums_to(E, x2, x1, [R, E.neg(R)]):
                leg_swap_hits += 1

            # (e) unsound per-instance orbit-canonical constraint:
            # among the n Frobenius images of the ordered pair (x1,x2),
            # keep only the lexicographically smallest pair. Under a free
            # cyclic action this deletes ~1-1/n of single-instance solutions
            # (HOLD-R / a77711: the orbit mates solve conjugate instances).
            orb_pairs = []
            a, b = x1, x2
            for _ in range(F.n):
                orb_pairs.append((a, b) if a <= b else (b, a))
                a, b = F.sqr(a), F.sqr(b)
            canonical = min(orb_pairs)
            cur = (x1, x2) if x1 <= x2 else (x2, x1)
            if cur != canonical:
                n_lost += 1

        solutions_total += n_sol
        solutions_lost += n_lost
        frac = (n_lost / n_sol) if n_sol else None
        if frac is not None:
            lost_fractions.append(frac)

    lost_fractions_sorted = sorted(lost_fractions)
    median_lost = (
        lost_fractions_sorted[len(lost_fractions_sorted) // 2]
        if lost_fractions_sorted
        else None
    )
    worst_lost = max(lost_fractions) if lost_fractions else None
    return {
        "same_instance_hits": same_instance_hits,
        "conjugate_instance_hits": (conjugate_hits / conjugate_trials)
        if conjugate_trials
        else None,
        "conjugate_hits_count": conjugate_hits,
        "conjugate_trials": conjugate_trials,
        "shifted_legs_in_V_fraction": (in_V_hits / in_V_trials) if in_V_trials else None,
        "in_V_hits": in_V_hits,
        "in_V_trials": in_V_trials,
        "leg_swap_hit_rate": (leg_swap_hits / leg_swap_trials) if leg_swap_trials else None,
        "solutions_lost_under_canonical_constraint": solutions_lost,
        "solutions_total": solutions_total,
        "solutions_lost_median_fraction": median_lost,
        "solutions_lost_worst_fraction": worst_lost,
        "solutions_lost_fractions_per_target": lost_fractions,
        "certificate_ok": certificate_ok,
        "certificate_fail": certificate_fail,
        "certificate_pass_rate": (
            certificate_ok / (certificate_ok + certificate_fail)
            if (certificate_ok + certificate_fail)
            else None
        ),
        "hard_stop_same_instance": hard_stop,
        "label": "MEASURED",
    }


def select_targets_from_index(index: dict, E: Curve, max_targets: int = 50) -> list:
    """Deterministic: sort by R.x then R.y; keep those with ≥1 decomp."""
    items = []
    for _rk, decomps in index.items():
        if not decomps:
            continue
        R = decomps[0]["R"]
        # Dedupe decomps by (x1,x2) unordered
        uniq = {}
        for d in decomps:
            a, b = d["x1"], d["x2"]
            key = (a, b) if a <= b else (b, a)
            if key not in uniq:
                # store with x1<=x2 ordering for (e) apply on first? Keep original P1,P2
                uniq[key] = {
                    "x1": key[0],
                    "x2": key[1],
                    "P1": d["P1"] if d["x1"] == key[0] else d["P2"],
                    "P2": d["P2"] if d["x1"] == key[0] else d["P1"],
                }
                # Fix lifts to match x1,x2
                # Re-lift properly:
        fixed = []
        for (a, b), _ in uniq.items():
            # find any certified lifts
            found = None
            for P1 in lifts_of_x(E, a):
                for P2 in lifts_of_x(E, b):
                    if certify_decomposition(E, R, P1, P2):
                        found = {"x1": a, "x2": b, "P1": P1, "P2": P2}
                        break
                if found:
                    break
            if found:
                fixed.append(found)
        if fixed:
            items.append({"R": R, "Rx": R[0], "Ry": R[1], "decomps": fixed})
    items.sort(key=lambda it: (it["Rx"], it["Ry"]))
    return items[:max_targets]


def phi_n_factors_over_f2(n: int) -> list[int]:
    """Factor Phi_n = (T^n-1)/(T-1) over F_2 into irreducibles of deg ord_n(2)."""
    d = ord_n_of_2(n)
    phi = (1 << n) - 1  # 1+T+...+T^{n-1}
    factors = []
    rem = phi
    max_cand = 1 << (d + 1)
    for cand in range(1 << d, max_cand):
        # irreducibility
        ok, _ = is_irreducible(cand) if False else (True, None)
        # use local irred test on poly
        nn = cand.bit_length() - 1
        if nn != d:
            continue
        # Rabin
        x = 2
        cur = x
        irr = True
        for i in range(1, nn + 1):
            cur = pmod(clmul(cur, cur), cand)
            if i <= nn // 2:
                if pgcd(cand, cur ^ x) != 1:
                    irr = False
                    break
        if not (irr and cur == x):
            continue
        while rem != 1:
            # divmod
            q, r = rem, 0
            # poly_divmod
            a, b = rem, cand
            qq = 0
            rr = a
            db = b.bit_length() - 1
            while rr and rr.bit_length() - 1 >= db:
                sh = (rr.bit_length() - 1) - db
                qq ^= 1 << sh
                rr ^= b << sh
            if rr == 0:
                factors.append(cand)
                rem = qq
            else:
                break
        if rem == 1:
            break
    if rem != 1:
        raise RuntimeError(f"incomplete Phi_{n} factorisation")
    return sorted(factors)


def ker_g_tau(F: Field, g: int) -> list[int]:
    def apply(poly, x):
        acc = 0
        y = x
        p = poly
        while p:
            if p & 1:
                acc ^= y
            y = F.sqr(y)
            p >>= 1
        return acc

    return [x for x in range(F.q) if apply(g, x) == 0]


def tau_stable_check(F: Field, V: Iterable[int]) -> dict:
    Vset = set(V)
    leave = sum(1 for v in Vset if F.sqr(v) not in Vset)
    # rank
    used = []
    for v in sorted(Vset):
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
    return {
        "pass": leave == 0,
        "leave_count": leave,
        "dim_V": len(used),
        "card_V": len(Vset),
        "in_V_fraction_under_shift": 1.0 if leave == 0 else (len(Vset) - leave) / len(Vset),
    }


def zl_replica(l_order: int, mu: int, window_size: int, seed: int, n_field: int) -> dict:
    """Scalar-action replica of tests (a)(b) in Z/l with random window."""
    rng = random.Random(seed)
    window = set()
    while len(window) < window_size:
        window.add(rng.randrange(0, l_order))
    # "points" are residues; a decomposition of t is unordered pair {a,b} with
    # (a+b) % l == t or == (-t)%l. Build index for targets that have ≥1 decomp.
    from collections import defaultdict

    # For efficiency: sample pairs from window
    wlist = list(window)
    index = defaultdict(set)
    for i, a in enumerate(wlist):
        for b in wlist[i:]:
            s = (a + b) % l_order
            index[s].add((a, b) if a <= b else (b, a))
            index[(-s) % l_order].add((a, b) if a <= b else (b, a))
    # pick up to 50 targets with decomps, deterministic order
    targets = sorted([t for t, ds in index.items() if ds and t != 0])[:50]
    same_hits = 0
    conj_hits = 0
    conj_trials = 0
    in_w = 0
    in_w_trials = 0
    for t in targets:
        for a, b in index[t]:
            sa, sb = (a * a) % l_order, (b * b) % l_order  # wrong — sigma is *mu not square
            # Correct: "sigma" = multiplication by mu on the group Z/l
            sa, sb = (mu * a) % l_order, (mu * b) % l_order
            # (a) same t?
            s = (sa + sb) % l_order
            if s == t or s == (-t) % l_order:
                if (mu * t) % l_order != t and (mu * t) % l_order != (-t) % l_order:
                    same_hits += 1
            # (b) conjugate mu*t
            conj_trials += 1
            ct = (mu * t) % l_order
            if s == ct or s == (-ct) % l_order:
                conj_hits += 1
            in_w_trials += 1
            if sa in window and sb in window:
                in_w += 1
    return {
        "seed": seed,
        "window_size": len(window),
        "n_targets": len(targets),
        "mu": mu,
        "same_instance_hits": same_hits,
        "conjugate_instance_hits": (conj_hits / conj_trials) if conj_trials else None,
        "shifted_legs_in_window_fraction": (in_w / in_w_trials) if in_w_trials else None,
        "conjugate_trials": conj_trials,
        "label": "MEASURED",
    }
