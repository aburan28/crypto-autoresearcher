#!/usr/bin/env python3
"""
Independent checker for EXP-FROB-91ee9c / TASK-20260921-51bc02.

Deliberately does NOT import implementation.py, work/core.py, work/lattice.py,
or any SageMath module (C8 / IR-8). Implements its own finite-field, matrix
and elliptic-curve arithmetic from scratch in plain Python (stdlib ints /
fractions only), so agreement with the driver's raw output is evidence about
correctness, not self-consistency of one code path.

Checks performed, from the driver's raw work/<cell>.out.json:
  1. Independent reconstruction of the lexicographically-first monic
     irreducible g of degree n over F_q; must match the driver's
     field_modulus string's coefficient pattern.
  2. Independent point arithmetic: re-verify, for each target curve, that N
     divides #E(F_q^n) to exponent exactly 1 (via independent order counting
     for the small FROB-SPLIT-q11n5 field only, where brute-force point
     counting over F_{11^5} is affordable in pure Python; for
     FROB-EQDEG-q19n5 -- 19^5 = 2,476,099 points -- full brute-force order
     counting is disclosed as skipped for scale, per the same discipline as
     TASK-20260914-7119f2's checker.py, rather than silently omitted).
  3. Independent re-verification of every reported object-arm, C2, C3 and C4
     rational cost_ratio_neg value from the raw (U_neg, p_m) pair via the
     frozen formula (U_neg + 1 + extra)/p_m, for extra=0, using Python
     fractions only.
  4. Independent re-verification of every reported spread (max/min ratio)
     and of the object-arm consistency check's targets (I, endpoints).
  5. Independent re-verification that C3/C4 arms have U_neg identical to the
     object arm's U_neg for every matched partition (this is the defining
     structural guarantee of the C3/C4 constructions, not merely a
     convenience -- a violation would mean the matched-cardinality
     construction was not actually implemented as specified).

Usage:
    python3 checker.py <run_dir>

Writes checker-report.json into <run_dir>/work/ and prints a summary.
"""
import sys, os, json, itertools
from fractions import Fraction


def load_raw(run_dir, cell):
    with open(os.path.join(run_dir, "work", f"{cell}.out.json")) as f:
        lines = f.read().splitlines()
    return json.loads(lines[1])


# --------------------------------------------------------------- F_q[x]/(g)
class FQN:
    def __init__(self, q, n, g_coeffs):
        self.q = q
        self.n = n
        self.g = g_coeffs[:]

    def reduce(self, coeffs):
        c = coeffs[:]
        q, n, g = self.q, self.n, self.g
        while len(c) > n:
            deg = len(c) - 1
            if c[deg] % q != 0:
                factor = c[deg] % q
                for i in range(n + 1):
                    c[deg - n + i] = (c[deg - n + i] - factor * g[i]) % q
            c.pop()
        c = c + [0] * (n - len(c))
        return [x % q for x in c]

    def mul(self, a, b):
        prod = [0] * (self.n * 2)
        for i, ai in enumerate(a):
            if ai == 0:
                continue
            for j, bj in enumerate(b):
                if bj == 0:
                    continue
                prod[i + j] = (prod[i + j] + ai * bj) % self.q
        return self.reduce(prod)

    def add(self, a, b):
        return [(x + y) % self.q for x, y in zip(a, b)]

    def sub(self, a, b):
        return [(x - y) % self.q for x, y in zip(a, b)]

    def neg(self, a):
        return [(-x) % self.q for x in a]

    def zero(self):
        return [0] * self.n

    def one(self):
        v = [0] * self.n
        v[0] = 1
        return v

    def is_zero(self, a):
        return all(x == 0 for x in a)

    def eq(self, a, b):
        return a == b

    def power(self, a, e):
        result = self.one()
        base = a[:]
        while e > 0:
            if e & 1:
                result = self.mul(result, base)
            base = self.mul(base, base)
            e >>= 1
        return result

    def inv(self, a):
        if self.is_zero(a):
            raise ZeroDivisionError("inverse of zero")
        order = self.q ** self.n - 2
        return self.power(a, order)

    def sqrt(self, a):
        Qsize = self.q ** self.n
        if Qsize % 4 == 3:
            cand = self.power(a, (Qsize + 1) // 4)
            if self.eq(self.mul(cand, cand), a):
                return cand
            return None
        raise NotImplementedError("general Tonelli-Shanks not needed for these fields")


def is_irreducible_bruteforce(q, coeffs):
    n = len(coeffs) - 1

    def trim(p):
        p = p[:]
        while len(p) > 1 and p[-1] == 0:
            p.pop()
        return p

    def polymod(A, B):
        A = trim(A); B = trim(B)
        binv = pow(B[-1], -1, q)
        while len(A) >= len(B) and not all(c == 0 for c in A):
            A = trim(A)
            if len(A) < len(B):
                break
            shift = len(A) - len(B)
            coef = (A[-1] * binv) % q
            for i, bc in enumerate(B):
                A[shift + i] = (A[shift + i] - coef * bc) % q
            A = trim(A)
        return trim(A)

    for d in range(1, n // 2 + 1):
        for lower in itertools.product(range(q), repeat=d):
            cand = list(lower) + [1]
            if len(cand) == 1:
                continue
            r = polymod(coeffs, cand)
            if r == [0]:
                return False
    return True


def find_first_irreducible_coeffs(q, n):
    for lower in itertools.product(range(q), repeat=n):
        coeffs = list(lower) + [1]
        if is_irreducible_bruteforce(q, coeffs):
            return coeffs
    raise RuntimeError("none found")


def coeffs_to_poly_str(coeffs):
    """coeffs: constant-first, length n+1, monic. Render like Sage's default
    str(poly) for cross-check against the driver's recorded field_modulus,
    e.g. [1,0,0,0,2,1] (q=11,n=5) -> 'x^5 + 2*x^4 + 1'."""
    n = len(coeffs) - 1
    terms = []
    for deg in range(n, -1, -1):
        c = coeffs[deg]
        if c == 0:
            continue
        if deg == 0:
            terms.append(f"{c}")
        elif deg == 1:
            terms.append(f"x" if c == 1 else f"{c}*x")
        else:
            terms.append(f"x^{deg}" if c == 1 else f"{c}*x^{deg}")
    return " + ".join(terms)


# ------------------------------------------------------------ EC arithmetic
class EC:
    def __init__(self, field, A, B):
        self.F = field
        self.A = A
        self.B = B

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if F.eq(F.add(y1, y2), F.zero()):
                return None
            num = F.add(self._scal(3, F.mul(x1, x1)), self.A)
            den = self._scal(2, y1)
            lam = F.mul(num, F.inv(den))
        else:
            num = F.sub(y2, y1)
            den = F.sub(x2, x1)
            lam = F.mul(num, F.inv(den))
        x3 = F.sub(F.sub(F.mul(lam, lam), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)

    def _scal(self, c, a):
        return [(c * x) % self.F.q for x in a]

    def scalar_mul(self, k, P):
        result = None
        addend = P
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result


def is_probable_prime(n):
    if n < 2:
        return False
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            return n == p
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in [2, 3, 5, 7, 11, 13, 17]:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def vec_to_enc(v, q):
    s = 0
    for c in reversed(v):
        s = s * q + c
    return s


def cost_ratio_check(U_pair, p_pair, extra):
    Un, Ud = U_pair
    pn, pd = p_pair
    if pn == 0:
        return None
    return Fraction(Un, Ud) + 1 + extra, Fraction(pn, pd)


def cost_ratio_exact(U_pair, p_pair, extra=0):
    val, pfrac = cost_ratio_check(U_pair, p_pair, extra)
    return val / pfrac


CONSISTENCY_TARGETS = {
    "FROB-SPLIT-q11n5": {"I": Fraction(2055, 451), "m1": Fraction(206733, 41), "m2": Fraction(5533, 5)},
    "FROB-EQDEG-q19n5": {"I": Fraction(6152, 861), "m1": Fraction(12097908, 205), "m2": Fraction(82593, 10)},
}

CELLS = [
    ("FROB-SPLIT-q11n5", 11, 5, 1, 2, 10061),
    ("FROB-EQDEG-q19n5", 19, 5, 1, 1, 117991),
]


def check_cell(run_dir, cell, q, n, A, B, N, report):
    data = load_raw(run_dir, cell)
    entry = {"cell": cell}

    # 1. independent field modulus reconstruction
    g_coeffs = find_first_irreducible_coeffs(q, n)
    g_str_independent = coeffs_to_poly_str(g_coeffs)
    entry["independent_field_modulus"] = g_str_independent
    entry["driver_field_modulus"] = data["field_modulus"]
    entry["field_modulus_matches"] = (g_str_independent == data["field_modulus"])

    # 2. re-verify every reported cost_ratio_neg (extra=0) in object/C2/C3/C4
    #    arms from raw (U_neg, p_m) using our own Fraction arithmetic.
    mismatches = []
    checked = 0

    def check_partition_list(label, parts):
        nonlocal checked
        for r in parts:
            if r.get("status") != "ok":
                continue
            reported = Fraction(*r["cost_ratio_neg"]["0"]["value"])
            recomputed = cost_ratio_exact(r["U_neg"], r["p_m"], extra=0)
            checked += 1
            if reported != recomputed:
                mismatches.append({"arm": label, "partition": r["partition_blocks"],
                                    "reported": str(reported), "recomputed": str(recomputed)})

    check_partition_list("object", data["object_arm_partitions"])
    check_partition_list("C2", data["C2_arm_partitions"])
    for seed, parts in data["C3_arm_by_seed"].items():
        check_partition_list(f"C3_seed{seed}", parts)
    for seed, parts in data["C4"]["partitions_by_seed"].items():
        check_partition_list(f"C4_seed{seed}", parts)

    entry["cost_ratio_reverifications_checked"] = checked
    entry["cost_ratio_mismatches"] = mismatches
    entry["cost_ratio_all_match"] = (len(mismatches) == 0)

    # 3. re-verify U_neg identical between object arm and C3/C4 for every
    #    matched (ok) partition -- the defining structural guarantee of C3/C4.
    obj_by_dims = {tuple(r["slot_dims"]): r for r in data["object_arm_partitions"] if r["status"] == "ok"}
    uneg_mismatches = []
    for seed, parts in data["C3_arm_by_seed"].items():
        for r in parts:
            if r["status"] != "ok":
                continue
            key = tuple(r["slot_dims"])
            obj_r = obj_by_dims.get(key)
            if obj_r is None or obj_r["U_neg"] != r["U_neg"]:
                uneg_mismatches.append({"arm": f"C3_seed{seed}", "slot_dims": r["slot_dims"],
                                         "object_U_neg": obj_r["U_neg"] if obj_r else None,
                                         "arm_U_neg": r["U_neg"]})
    for seed, parts in data["C4"]["partitions_by_seed"].items():
        for r in parts:
            if r["status"] != "ok":
                continue
            key = tuple(r["slot_dims"])
            obj_r = obj_by_dims.get(key)
            if obj_r is None or obj_r["U_neg"] != r["U_neg"]:
                uneg_mismatches.append({"arm": f"C4_seed{seed}", "slot_dims": r["slot_dims"],
                                         "object_U_neg": obj_r["U_neg"] if obj_r else None,
                                         "arm_U_neg": r["U_neg"]})
    entry["C3_C4_U_neg_matched_cardinality_mismatches"] = uneg_mismatches
    entry["C3_C4_U_neg_matched_cardinality_ok"] = (len(uneg_mismatches) == 0)

    # 4. re-verify object-arm spread/I and the consistency-check targets
    ok = [r for r in data["object_arm_partitions"] if r["status"] == "ok"]
    m1 = [r for r in ok if r["slot_count_m"] == 1][0]
    coarsest = cost_ratio_exact(m1["U_neg"], m1["p_m"])
    vals = [(r, cost_ratio_exact(r["U_neg"], r["p_m"])) for r in ok]
    argmax_r, argmax_v = max(vals, key=lambda t: t[1])
    argmin_r, argmin_v = min(vals, key=lambda t: t[1])
    I_independent = coarsest / argmin_v
    spread_independent = argmax_v / argmin_v
    target = CONSISTENCY_TARGETS[cell]
    entry["independent_I"] = str(I_independent)
    entry["independent_spread"] = str(spread_independent)
    entry["independent_m1_ratio"] = str(coarsest)
    entry["independent_m2_argmin_ratio"] = str(argmin_v)
    entry["target_I"] = str(target["I"])
    entry["target_m1"] = str(target["m1"])
    entry["target_m2"] = str(target["m2"])
    entry["consistency_check_independent"] = (
        I_independent == target["I"] and coarsest == target["m1"] and argmin_v == target["m2"]
    )
    entry["driver_reported_consistency_check"] = data["object_arm_consistency_check"]["all_match"]
    entry["consistency_checks_agree"] = (
        entry["consistency_check_independent"] == entry["driver_reported_consistency_check"]
    )

    # 5. re-verify every reported spread_summary (object, C2, C3-by-seed,
    #    C4-by-seed) via independent max/min over the same raw (U_neg,p_m).
    def spread_of(parts):
        okp = [r for r in parts if r.get("status") == "ok"]
        if not okp:
            return None
        vals = [cost_ratio_exact(r["U_neg"], r["p_m"]) for r in okp]
        return max(vals) / min(vals)

    spread_checks = {}
    spread_checks["object"] = str(spread_of(data["object_arm_partitions"]))
    spread_checks["C2"] = str(spread_of(data["C2_arm_partitions"]))
    for seed, parts in data["C3_arm_by_seed"].items():
        spread_checks[f"C3_seed{seed}"] = str(spread_of(parts))
    for seed, parts in data["C4"]["partitions_by_seed"].items():
        spread_checks[f"C4_seed{seed}"] = str(spread_of(parts))
    entry["independent_spreads"] = spread_checks

    obj_spread = Fraction(*data["object_arm_summary"]["spread"])
    strictly_smaller = {}
    strictly_smaller["C2"] = spread_of(data["C2_arm_partitions"]) < obj_spread
    for seed, parts in data["C3_arm_by_seed"].items():
        strictly_smaller[f"C3_seed{seed}"] = spread_of(parts) < obj_spread
    for seed, parts in data["C4"]["partitions_by_seed"].items():
        strictly_smaller[f"C4_seed{seed}"] = spread_of(parts) < obj_spread
    entry["independent_strictly_smaller_than_object_verdicts"] = strictly_smaller

    # 6. curve eligibility spot check: N divides recomputed order exactly once.
    entry["curve_recomputed_order"] = data["curve_recomputed"]["order"]
    entry["N_target"] = N
    order = data["curve_recomputed"]["order"]
    exp = 0
    tmp = order
    while tmp % N == 0:
        exp += 1
        tmp //= N
    entry["N_divides_order_exponent"] = exp
    entry["N_divides_order_exactly_once"] = (exp == 1)

    report["cells"].append(entry)
    return data


def independent_object_search_small_field(report):
    """Full independent brute-force order verification for the smaller field
    FROB-SPLIT-q11n5 (11^5 = 161051 field elements, affordable in pure
    Python): recompute #E(F_{11^5}) for A=1,B=2 by point counting via
    Euler-criterion (quadratic residue test), independent of Sage's
    EllipticCurve.order()."""
    q, n, A, B = 11, 5, 1, 2
    g_coeffs = find_first_irreducible_coeffs(q, n)
    F = FQN(q, n, g_coeffs)
    Aelt = [A] + [0] * (n - 1)
    Belt = [B] + [0] * (n - 1)
    Qsize = q ** n
    half = (Qsize - 1) // 2
    count = 1  # point at infinity
    zero = F.zero()
    for xvec in itertools.product(range(q), repeat=n):
        xelt = list(xvec)
        rhs = F.add(F.add(F.power(xelt, 3), F.mul(Aelt, xelt)), Belt)
        if F.is_zero(rhs):
            count += 1
            continue
        euler = F.power(rhs, half)
        if euler == F.one():
            count += 2
        # else: non-residue, 0 points
    return count


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    report = {"cells": [], "independent_full_order_count": {}}

    for cell, q, n, A, B, N in CELLS:
        check_cell(run_dir, cell, q, n, A, B, N, report)

    # Independent brute-force #E(F_q^n) for the small field only (large field
    # 19^5 = 2,476,099 disclosed as skipped for scale, matching the
    # TASK-20260914-7119f2 checker's disclosed-skip discipline).
    count = independent_object_search_small_field(report)
    report["independent_full_order_count"]["FROB-SPLIT-q11n5_A1_B2"] = {
        "independent_count": count,
        "driver_recomputed_order": None,  # filled below
        "status": "computed",
    }
    data0 = load_raw(run_dir, "FROB-SPLIT-q11n5")
    report["independent_full_order_count"]["FROB-SPLIT-q11n5_A1_B2"]["driver_recomputed_order"] = \
        data0["curve_recomputed"]["order"]
    report["independent_full_order_count"]["FROB-SPLIT-q11n5_A1_B2"]["matches"] = (
        count == data0["curve_recomputed"]["order"]
    )
    report["independent_full_order_count"]["FROB-EQDEG-q19n5_A1_B1"] = {
        "status": "skipped_too_large_for_pure_python_full_reenumeration_this_session",
        "field_size": 19 ** 5,
    }

    outpath = os.path.join(run_dir, "work", "checker-report.json")
    with open(outpath, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
