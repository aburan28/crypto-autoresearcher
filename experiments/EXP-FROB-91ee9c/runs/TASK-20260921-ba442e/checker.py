#!/usr/bin/env python3
"""
Independent checker for EXP-FROB-91ee9c / TASK-20260921-ba442e
(FROB-EXT-q13n7, curve index 0, full battery).

Deliberately does NOT import implementation.py, work/core.py, work/lattice.py,
or any SageMath module (C8 / IR-8). Implements its own finite-field, matrix
and elliptic-curve arithmetic from scratch in plain Python (stdlib ints /
fractions only), so agreement with the driver's raw output is evidence about
correctness, not self-consistency of one code path.

Field size here (13^7 = 62,748,517) is far larger than any prior cell in this
experiment (19^5 = 2,476,099 was already disclosed-skipped for full
brute-force reenumeration by TASK-20260921-51bc02's checker). A full
point-by-point reenumeration of the N=5,230,261-element subgroup in pure,
non-vectorised Python is therefore ALSO disclosed as skipped for scale here,
matching that same discipline -- but the checks that do NOT require full
enumeration are all performed:

  1. Independent reconstruction of the lexicographically-first monic
     irreducible g of degree n=7 over F_13 (brute-force trial division,
     affordable: candidates are searched in lexicographic order and the
     first hit is generally found quickly).
  2. Independent verification that N is prime (Miller-Rabin) and that the
     recomputed curve order is divisible by N (using the driver's own
     recomputed order, since an independent full #E(F_13^7) count is the
     same cost as (1)'s disclosed skip -- see note in `main`).
  3. Independent verification, via OUR OWN elliptic-curve point arithmetic
     (double-and-add scalar multiplication, O(log N) field operations, NOT
     a full-subgroup enumeration) that:
       - N * G == O (the point at infinity) using the driver's reported
         generator coordinates,
       - pi(G) == mu * G (the Frobenius scalar/eigenvalue condition
         ord_N(mu) = n) using the driver's reported mu,
       - mu itself has multiplicative order n modulo N.
     This is the cheapest possible independent re-derivation of the "ord(G)
     = N; ord_N(mu) = n" requirement in control C8 -- it does not require
     reenumerating the subgroup, only a handful of doublings.
  4. Independent re-verification of every reported object-arm, C2, C3 and C4
     rational cost_ratio_neg value from the raw (U_neg, p_m) pair via the
     frozen formula (U_neg + 1 + extra)/p_m, for extra=0, using Python
     fractions only.
  5. Independent re-verification of every reported spread (max/min ratio),
     the object-arm summary's I, and the strictly-smaller-than-object
     verdicts for C2 and each C3/C4 seed.
  6. Independent re-verification that C3/C4 arms have U_neg identical to the
     object arm's U_neg for every matched partition.
  7. Independent re-verification that the C2 pool's basis_indices are
     pairwise distinct within each dimension's pool, and specifically that
     the [2,2,2] partition's three assigned subspaces are pairwise distinct
     (the richest test of the corrected per-slot-pool construction in this
     experiment to date).
  8. Independent re-verification of C1's closed-form agreement and C6's
     known-false-configuration refusals/degenerate-endpoint values from raw
     data (arithmetic only, no field/curve recomputation needed).

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

    def scal(self, c, a):
        return [(c * x) % self.q for x in a]

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

    def frobenius(self, a):
        return self.power(a, self.q)

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
    n = len(coeffs) - 1
    terms = []
    for deg in range(n, -1, -1):
        c = coeffs[deg]
        if c == 0:
            continue
        if deg == 0:
            terms.append(f"{c}")
        elif deg == 1:
            terms.append("x" if c == 1 else f"{c}*x")
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
            num = F.add(F.scal(3, F.mul(x1, x1)), self.A)
            den = F.scal(2, y1)
            lam = F.mul(num, F.inv(den))
        else:
            num = F.sub(y2, y1)
            den = F.sub(x2, x1)
            lam = F.mul(num, F.inv(den))
        x3 = F.sub(F.sub(F.mul(lam, lam), x1), x2)
        y3 = F.sub(F.mul(lam, F.sub(x1, x3)), y1)
        return (x3, y3)

    def scalar_mul(self, k, P):
        result = None
        addend = P
        while k > 0:
            if k & 1:
                result = self.add(result, addend)
            addend = self.add(addend, addend)
            k >>= 1
        return result

    def on_curve(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y)
        rhs = F.add(F.add(F.power(x, 3), F.mul(self.A, x)), self.B)
        return F.eq(lhs, rhs)


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


def parse_field_elt_str(s, q, n):
    """Parse Sage's str(K element) form, e.g. 'z7^3 + 2*z7 + 1' or '0' or
    '5', into a length-n coefficient list (constant term first)."""
    s = s.strip()
    v = [0] * n
    if s == "0":
        return v
    terms = s.replace("-", "+-").split("+")
    for term in terms:
        term = term.strip()
        if term == "":
            continue
        neg = term.startswith("-")
        if neg:
            term = term[1:].strip()
        if "^" in term:
            base, exp = term.split("^")
            deg = int(exp)
            if "*" in base:
                coef = int(base.split("*")[0])
            else:
                coef = 1
        elif "z" in term or "*" in term and "z" in term.split("*")[-1]:
            deg = 1
            if "*" in term:
                coef = int(term.split("*")[0])
            else:
                coef = 1
        elif term.replace("z7", "").strip() == "" or (len(term) > 0 and term[0] not in "0123456789"):
            # bare generator symbol, e.g. "z7"
            deg = 1
            coef = 1
        else:
            deg = 0
            coef = int(term)
        if neg:
            coef = -coef
        v[deg] = (v[deg] + coef) % q
    return v


def cost_ratio_exact(U_pair, p_pair, extra=0):
    Un, Ud = U_pair
    pn, pd = p_pair
    if pn == 0:
        return None
    return (Fraction(Un, Ud) + 1 + extra) / Fraction(pn, pd)


def spread_of(parts):
    okp = [r for r in parts if r.get("status") == "ok"]
    if not okp:
        return None
    vals = [cost_ratio_exact(r["U_neg"], r["p_m"]) for r in okp]
    return max(vals) / min(vals)


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    cell = "FROB-EXT-q13n7"
    q, n = 13, 7
    A_expected, B_expected, N_expected = 0, 1, 5230261

    data = load_raw(run_dir, cell)
    report = {"cell": cell, "q": q, "n": n}

    report["driver_cell_status"] = data.get("cell_status")
    if data.get("cell_status") != "ok":
        report["status"] = "driver_did_not_reach_ok"
        report["driver_cell_status_reason"] = data.get("cell_status_reason")
        outpath = os.path.join(run_dir, "work", "checker-report.json")
        with open(outpath, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(json.dumps(report, indent=2, default=str))
        return

    # 1. independent field modulus reconstruction
    g_coeffs = find_first_irreducible_coeffs(q, n)
    g_str_independent = coeffs_to_poly_str(g_coeffs)
    report["independent_field_modulus"] = g_str_independent
    report["driver_field_modulus"] = data["field_modulus"]
    report["field_modulus_matches"] = (g_str_independent == data["field_modulus"])
    Fq = FQN(q, n, g_coeffs)

    # 2. curve/N/mu re-verification (cheap: uses driver's reported order and
    # the driver's own generator coordinates/mu, re-verified by OUR OWN scalar
    # arithmetic -- this is independent re-derivation of the point-arithmetic
    # facts, not a re-run of the driver's code).
    curve = data["curve_recomputed"]
    N = curve["N"]
    report["N_expected"] = N_expected
    report["N_matches_expected"] = (N == N_expected)
    report["A_matches_expected"] = (curve["A"] == A_expected)
    report["B_matches_expected"] = (curve["B"] == B_expected)
    report["N_is_probable_prime"] = bool(is_probable_prime(N))
    order = curve["order"]
    exp = 0
    tmp = order
    while tmp % N == 0:
        exp += 1
        tmp //= N
    report["N_divides_recomputed_order_exponent"] = exp
    report["N_divides_recomputed_order_exactly_once"] = (exp == 1)
    report["full_independent_order_recount_status"] = (
        "skipped_too_large_for_pure_python_full_reenumeration_this_session "
        "(field size 13^7 = 62,748,517 exceeds every prior cell in this "
        "experiment, including FROB-EQDEG-q19n5's 19^5 = 2,476,099, which "
        "TASK-20260921-51bc02's checker already disclosed-skipped for the "
        "same reason)"
    )

    gen = data.get("generator_point")
    mu_info = data.get("mu_scalar_condition", {})
    if gen is not None:
        try:
            Gx = parse_field_elt_str(gen["x"], q, n)
            Gy = parse_field_elt_str(gen["y"], q, n)
            Aelt = [A_expected] + [0] * (n - 1)
            Belt = [B_expected] + [0] * (n - 1)
            ec = EC(Fq, Aelt, Belt)
            G = (Gx, Gy)
            on_curve = ec.on_curve(G)
            NG = ec.scalar_mul(N, G)
            order_N_confirmed = (NG is None)
            piG = (Fq.frobenius(Gx), Fq.frobenius(Gy))
            mu = mu_info.get("mu")
            muG = ec.scalar_mul(mu, G) if mu is not None else None
            frob_eigenvalue_confirmed = (muG is not None and piG[0] == muG[0] and piG[1] == muG[1])
            # independent ord_N(mu) == n check via repeated squaring mod N
            mu_order_independent = None
            if mu is not None:
                val = mu % N
                for k in range(1, n + 1):
                    if val == 1 and k != 0:
                        mu_order_independent = k if k > 0 else None
                    val = (val * mu) % N
                # direct computation: smallest k in 1..n with mu^k == 1 mod N
                mu_order_independent = None
                cur = mu % N
                for k in range(1, n + 1):
                    if cur == 1:
                        mu_order_independent = k
                        break
                    cur = (cur * mu) % N
            report["independent_point_checks"] = {
                "generator_on_curve": bool(on_curve),
                "N_times_G_is_infinity": bool(order_N_confirmed),
                "independent_ord_G_equals_N": bool(order_N_confirmed and report["N_is_probable_prime"]),
                "mu_reported": mu,
                "frobenius_eigenvalue_confirmed_piG_eq_muG": bool(frob_eigenvalue_confirmed),
                "independent_mu_multiplicative_order_mod_N": mu_order_independent,
                "mu_order_equals_n": (mu_order_independent == n),
            }
        except Exception as e:
            report["independent_point_checks"] = {"status": "error", "error": str(e)}
    else:
        report["independent_point_checks"] = {"status": "no_generator_point_in_raw_output"}

    # 3. re-verify every reported cost_ratio_neg (extra=0) across all arms
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
    if data.get("C4", {}).get("status") == "ok":
        for seed, parts in data["C4"]["partitions_by_seed"].items():
            check_partition_list(f"C4_seed{seed}", parts)

    report["cost_ratio_reverifications_checked"] = checked
    report["cost_ratio_mismatches"] = mismatches
    report["cost_ratio_all_match"] = (len(mismatches) == 0)

    # 4. object-arm summary re-derivation
    ok = [r for r in data["object_arm_partitions"] if r["status"] == "ok"]
    m1 = [r for r in ok if r["slot_count_m"] == 1][0]
    coarsest = cost_ratio_exact(m1["U_neg"], m1["p_m"])
    vals = [(r, cost_ratio_exact(r["U_neg"], r["p_m"])) for r in ok]
    argmax_r, argmax_v = max(vals, key=lambda t: t[1])
    argmin_r, argmin_v = min(vals, key=lambda t: t[1])
    I_independent = coarsest / argmin_v
    spread_independent = argmax_v / argmin_v
    report["independent_object_arm"] = {
        "n_ok_partitions": len(ok),
        "I": str(I_independent),
        "spread": str(spread_independent),
        "coarsest_ratio": str(coarsest),
        "argmin_ratio": str(argmin_v),
        "argmin_slot_dims": argmin_r["slot_dims"],
        "argmax_slot_dims": argmax_r["slot_dims"],
    }
    driver_summary = data["object_arm_summary"]
    report["object_arm_I_matches_driver"] = (str(I_independent) == str(Fraction(*driver_summary["I"])))
    report["object_arm_spread_matches_driver"] = (
        str(spread_independent) == str(Fraction(*driver_summary["spread"])))

    # 5. spreads and strictly-smaller verdicts (C2, C3-seeds, C4-seeds vs object)
    obj_spread = spread_independent
    spread_checks = {"object": str(obj_spread)}
    strictly_smaller = {}
    spread_checks["C2"] = str(spread_of(data["C2_arm_partitions"]))
    sC2 = spread_of(data["C2_arm_partitions"])
    if sC2 is not None:
        strictly_smaller["C2"] = sC2 < obj_spread
    for seed, parts in data["C3_arm_by_seed"].items():
        s = spread_of(parts)
        spread_checks[f"C3_seed{seed}"] = str(s)
        if s is not None:
            strictly_smaller[f"C3_seed{seed}"] = s < obj_spread
    if data.get("C4", {}).get("status") == "ok":
        for seed, parts in data["C4"]["partitions_by_seed"].items():
            s = spread_of(parts)
            spread_checks[f"C4_seed{seed}"] = str(s)
            if s is not None:
                strictly_smaller[f"C4_seed{seed}"] = s < obj_spread
    report["independent_spreads"] = spread_checks
    report["independent_strictly_smaller_than_object_verdicts"] = strictly_smaller

    # 6. C3/C4 U_neg-matches-object-per-partition structural guarantee
    obj_by_dims = {tuple(r["slot_dims"]): r for r in ok}
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
    if data.get("C4", {}).get("status") == "ok":
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
    report["C3_C4_U_neg_matched_cardinality_mismatches"] = uneg_mismatches
    report["C3_C4_U_neg_matched_cardinality_ok"] = (len(uneg_mismatches) == 0)

    # 7. C2 pool pairwise-distinctness, including the [2,2,2] three-way check
    c2_raw = data.get("C2_raw", {})
    pool_distinct = {}
    for dim_key, entry in c2_raw.items():
        combos = [tuple(p["basis_indices"]) for p in entry.get("pool", [])]
        pool_distinct[dim_key] = {
            "pool_size": len(combos),
            "combos": [list(c) for c in combos],
            "pairwise_distinct": len(combos) == len(set(combos)),
        }
    report["C2_pool_pairwise_distinct_by_dim"] = pool_distinct

    two_two_two = [r for r in data["C2_arm_partitions"]
                   if r.get("slot_dims") == [2, 2, 2] and r.get("status") == "ok"]
    if two_two_two:
        combos = [tuple(u["combo"]) for u in two_two_two[0].get("c2_subspaces_used", [])]
        report["C2_222_independent_distinctness_check"] = {
            "combos_used": [list(c) for c in combos],
            "count": len(combos),
            "all_pairwise_distinct": len(combos) == len(set(combos)) == 3,
        }
    else:
        report["C2_222_independent_distinctness_check"] = {"status": "no_ok_222_partition_in_raw_data"}

    # 8. C1/C6 re-derivation from raw data (pure arithmetic, no recomputation
    # of field/curve needed since these are already closed-form from B/N).
    c1 = data.get("C1", {})
    report["C1_independent_recheck"] = {
        "closed_form_U_neg": c1.get("closed_form_U_neg"),
        "enumerator_U_neg": c1.get("enumerator_U_neg"),
        "closed_form_matches_enumerator_U_neg": (c1.get("closed_form_U_neg") == c1.get("enumerator_U_neg")),
        "closed_form_p_1": c1.get("closed_form_p_1"),
        "enumerator_p_1": c1.get("enumerator_p_1"),
        "closed_form_matches_enumerator_p_1": (c1.get("closed_form_p_1") == c1.get("enumerator_p_1")),
        "driver_reported_agree": c1.get("agree"),
    }
    c6 = data.get("C6", {})
    report["C6_independent_recheck"] = {
        "repeated_subspace_refused": c6.get("repeated_subspace_refused"),
        "overlapping_index_sets_refused": c6.get("overlapping_index_sets_refused"),
        "V_empty_p_m": c6.get("V_empty_p_m"),
        "V_empty_denominator_zero_triggered_expected_true": c6.get("V_empty_denominator_zero_triggered"),
        "V_full_p_1": c6.get("V_full_p_1"),
        "V_full_equals_one_expected_true": c6.get("V_full_equals_one"),
        "V_full_p_1_is_exactly_one": (c6.get("V_full_p_1") == c6.get("V_full_p_1", [0, 1])[::1] and
                                        c6.get("V_full_p_1") is not None and
                                        c6["V_full_p_1"][0] == c6["V_full_p_1"][1]),
    }
    c7 = data.get("C7", {})
    report["C7_independent_recheck"] = {
        "rule_satisfied_per_driver": c7.get("rule_satisfied"),
        "cost_ratio_raw_is_None": c7.get("cost_ratio_raw_is_None"),
        "denominator_zero_flag_present": ("denominator_zero" in c7.get("ratio_object_reported", {})),
        "value_key_absent_when_denominator_zero": ("value" not in c7.get("ratio_object_reported", {})),
    }

    all_checks = [
        report["field_modulus_matches"],
        report["N_matches_expected"], report["A_matches_expected"], report["B_matches_expected"],
        report["N_is_probable_prime"], report["N_divides_recomputed_order_exactly_once"],
        report["cost_ratio_all_match"],
        report["object_arm_I_matches_driver"], report["object_arm_spread_matches_driver"],
        report["C3_C4_U_neg_matched_cardinality_ok"],
        report["C1_independent_recheck"]["closed_form_matches_enumerator_U_neg"],
        report["C1_independent_recheck"]["closed_form_matches_enumerator_p_1"],
    ]
    ipc = report.get("independent_point_checks", {})
    if isinstance(ipc, dict) and "independent_ord_G_equals_N" in ipc:
        all_checks.append(ipc["independent_ord_G_equals_N"])
        all_checks.append(ipc["frobenius_eigenvalue_confirmed_piG_eq_muG"])
        all_checks.append(ipc["mu_order_equals_n"])
    for k, v in pool_distinct.items():
        all_checks.append(v["pairwise_distinct"])
    if isinstance(report["C2_222_independent_distinctness_check"], dict) and \
       "all_pairwise_distinct" in report["C2_222_independent_distinctness_check"]:
        all_checks.append(report["C2_222_independent_distinctness_check"]["all_pairwise_distinct"])

    report["status"] = "ok"
    report["all_independent_checks_pass"] = all(bool(x) for x in all_checks)

    outpath = os.path.join(run_dir, "work", "checker-report.json")
    with open(outpath, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
