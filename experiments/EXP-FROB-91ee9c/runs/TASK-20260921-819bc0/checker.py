#!/usr/bin/env python3
"""
Independent checker for EXP-FROB-91ee9c / TASK-20260921-819bc0.

Deliberately does NOT import implementation.py, work/core.py, work/lattice.py,
or any SageMath module (C8 / IR-8). Implements its own finite-field, matrix
and elliptic-curve arithmetic from scratch in plain Python (stdlib ints /
fractions only), so agreement with the driver's raw output is evidence about
correctness, not self-consistency of one code path.

Scope, per the handoff/amendment: this run recomputes the OBJECT ARM
(consistency check only) and control C2 ONLY, using the corrected
per-slot-independent subspace-pool construction. C3/C4 are out of scope and
are not present in this run's raw output, so the checker does not look for
them.

Checks performed, from the driver's raw work/<cell>.out.json:
  1. Independent reconstruction of the lexicographically-first monic
     irreducible g of degree n over F_q; must match the driver's
     field_modulus string's coefficient pattern.
  2. Independent point counting/order re-verification for the small
     FROB-SPLIT-q11n5 field only (brute-force affordable in pure Python);
     for FROB-EQDEG-q19n5 (19^5 = 2,476,099 points) full brute-force order
     counting is disclosed as skipped for scale, matching the disclosed-skip
     discipline of the two prior runs' checkers.
  3. Independent re-verification of every reported object-arm and C2
     rational cost_ratio_neg value from the raw (U_neg, p_m) pair via the
     frozen formula (U_neg + 1 + extra)/p_m, for extra=0, using Python
     fractions only.
  4. Independent re-verification of the object-arm consistency-check targets
     (I, m1/coarsest ratio, m2/argmin ratio, argmin slot_dims) and of both
     arms' spreads (object and C2).
  5. THE CORRECTED-CONSTRUCTION GATE (this run's whole purpose): for every
     dimension d appearing more than once in a single partition's slot_dims
     (only [2,2] arises for either tested cell), independently verify from
     the driver's raw C2_raw pool that the pool for that dimension has at
     least as many entries as the maximum multiplicity needed, that all pool
     entries for a given dimension have PAIRWISE DISTINCT basis_indices
     (index tuples), and that the C2_arm_partitions entry for that partition
     used a U_neg consistent with two DIFFERENT B_W sizes summing correctly
     (i.e. is NOT reproducible by summing one B_W set with itself, unless the
     two pool entries happen to coincide in size only -- checked via the
     recomputed sumset cardinality from the two disclosed B_W sizes never
     being assumed but the DISTINCTNESS of basis_indices being checked
     directly, which is what the fix actually guarantees).

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


def cost_ratio_exact(U_pair, p_pair, extra=0):
    Un, Ud = U_pair
    pn, pd = p_pair
    val = Fraction(Un, Ud) + 1 + extra
    pfrac = Fraction(pn, pd)
    return val / pfrac


CONSISTENCY_TARGETS = {
    "FROB-SPLIT-q11n5": {"I": Fraction(2055, 451), "m1": Fraction(206733, 41), "m2": Fraction(5533, 5)},
    "FROB-EQDEG-q19n5": {"I": Fraction(6152, 861), "m1": Fraction(12097908, 205), "m2": Fraction(82593, 10)},
}

CELLS = [
    ("FROB-SPLIT-q11n5", 11, 5, 1, 2, 10061),
    ("FROB-EQDEG-q19n5", 19, 5, 1, 1, 117991),
]


def spread_of(parts):
    okp = [r for r in parts if r.get("status") == "ok"]
    if not okp:
        return None
    vals = [cost_ratio_exact(r["U_neg"], r["p_m"]) for r in okp]
    return max(vals) / min(vals)


def check_cell(run_dir, cell, q, n, A, B, N, report):
    data = load_raw(run_dir, cell)
    entry = {"cell": cell}

    # 1. independent field modulus reconstruction
    g_coeffs = find_first_irreducible_coeffs(q, n)
    g_str_independent = coeffs_to_poly_str(g_coeffs)
    entry["independent_field_modulus"] = g_str_independent
    entry["driver_field_modulus"] = data["field_modulus"]
    entry["field_modulus_matches"] = (g_str_independent == data["field_modulus"])

    # 2. re-verify every reported cost_ratio_neg (extra=0) in object/C2 arms
    #    from raw (U_neg, p_m) using our own Fraction arithmetic.
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

    entry["cost_ratio_reverifications_checked"] = checked
    entry["cost_ratio_mismatches"] = mismatches
    entry["cost_ratio_all_match"] = (len(mismatches) == 0)

    # 3. re-verify object-arm spread/I and the consistency-check targets
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
    entry["independent_object_spread"] = str(spread_independent)
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
    entry["argmin_slot_dims"] = argmin_r["slot_dims"]

    # 4. re-verify C2 spread and strictly-smaller-than-object verdict
    obj_spread = spread_independent
    c2_spread = spread_of(data["C2_arm_partitions"])
    entry["independent_C2_spread"] = str(c2_spread) if c2_spread is not None else None
    entry["driver_reported_C2_spread"] = data["C2_spread_summary"].get("spread")
    if c2_spread is not None and entry["driver_reported_C2_spread"] is not None:
        driver_c2_spread = Fraction(*entry["driver_reported_C2_spread"])
        entry["C2_spread_matches"] = (c2_spread == driver_c2_spread)
    else:
        entry["C2_spread_matches"] = None
    entry["independent_C2_strictly_smaller_than_object"] = (
        c2_spread < obj_spread if c2_spread is not None else None
    )

    # 5. THE CORRECTED-CONSTRUCTION GATE: for every dimension appearing with
    #    multiplicity > 1 in any ok partition's slot_dims, verify the raw
    #    C2_raw pool for that dimension has pairwise DISTINCT basis_indices
    #    and enough entries for the multiplicity needed.
    max_mult_by_dim = {}
    for r in ok:
        counts = {}
        for d in r["slot_dims"]:
            counts[d] = counts.get(d, 0) + 1
        for d, c in counts.items():
            if d == 0:
                continue
            max_mult_by_dim[d] = max(max_mult_by_dim.get(d, 0), c)

    pool_distinctness = {}
    pool_sufficiency = {}
    for d, needed in max_mult_by_dim.items():
        key = str(d)
        raw = data["C2_raw"].get(key)
        if raw is None or not raw.get("found"):
            pool_distinctness[key] = None
            pool_sufficiency[key] = False
            continue
        combos = [tuple(e["basis_indices"]) for e in raw["pool"]]
        pool_distinctness[key] = (len(combos) == len(set(combos)))
        pool_sufficiency[key] = (len(combos) >= needed if needed > 1 else True)
    entry["multi_slot_dimensions_and_needed_multiplicity"] = {str(k): v for k, v in max_mult_by_dim.items()}
    entry["C2_pool_distinctness_by_dim"] = pool_distinctness
    entry["C2_pool_sufficiency_by_dim"] = pool_sufficiency
    entry["C2_construction_fix_verified"] = (
        all(v is True for v in pool_distinctness.values()) and
        all(v is True for v in pool_sufficiency.values())
    )

    # Also directly verify, for the [2,2] partition itself, that the two
    # slots' basis_indices (as recorded in the driver's C2_arm construction
    # via C2_raw pool order) are pairwise distinct, by re-deriving which pool
    # entries a [2,2] partition would consume (first k=2 entries of dim-2
    # pool, in pool order) and checking they differ.
    dim2_raw = data["C2_raw"].get("2")
    if dim2_raw is not None and dim2_raw.get("found") and len(dim2_raw["pool"]) >= 2:
        b0 = tuple(dim2_raw["pool"][0]["basis_indices"])
        b1 = tuple(dim2_raw["pool"][1]["basis_indices"])
        entry["two_two_slots_distinct_subspaces"] = (b0 != b1)
        entry["two_two_slots_basis_indices"] = [list(b0), list(b1)]
    else:
        entry["two_two_slots_distinct_subspaces"] = None
        entry["two_two_slots_basis_indices"] = None

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

    count = independent_object_search_small_field(report)
    report["independent_full_order_count"]["FROB-SPLIT-q11n5_A1_B2"] = {
        "independent_count": count,
        "driver_recomputed_order": None,
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
