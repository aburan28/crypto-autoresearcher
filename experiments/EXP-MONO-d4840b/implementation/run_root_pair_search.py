"""
EXP-MONO-d4840b -- root-pair enumeration for a Z=3, h_+>=1, h_->=1,
max(h_+,h_-)>=2 curve. See specification.yaml (frozen, approved) and
ledger/handoffs/TASK-20260904-a6f3da.yaml for the exact declared search
order, which this file implements without modification once written.

THE KEY INSIGHT (unchanged from the task card): a short-Weierstrass cubic
f(X) = X^3 + A X + B has no X^2 term, so its three roots always sum to
zero. Every curve with Z=3 (three distinct F_p-rational roots) can
therefore be generated DIRECTLY: choose r1, r2 freely with r1 < r2 in
F_p, set r3 = -(r1+r2) mod p, and compute
    A = r1*r2 + r1*r3 + r2*r3  (mod p)
    B = -r1*r2*r3              (mod p).
This (A,B) is GUARANTEED to have exactly the roots {r1,r2,r3} -- no O(p)
per-candidate scan of range(p) is needed to determine Z, which is what
made both of EXP-MONO-8ec0e5's own attempts resource-exhaust. This is a
genuine O(p^2) total algorithm per prime (choosing (r1,r2) is O(p^2)
total; A,B computation and the fast character-based h_+/h_- test are
O(1)/O(log p) per candidate) instead of the O(p^3) (A,B)-scan approach.

ONLY STAGE 0's OWN SEARCH METHOD IS NEW. M6, Stage 1, and Stage 2 are
reused, logically UNMODIFIED, from
    experiments/EXP-MONO-8ec0e5/implementation/run_amended_bivariate_test.py
(read in full before writing this file; copied here rather than imported,
exactly as that script itself copied -- not imported -- its own logic
forward from run_corrected_bivariate_test.py). `h_pair_from_characters`,
`count_4_torsion_bruteforce`, `_is4`, `twist_params`, `chi_table`,
`nonresidue`, `C3`, `primes_in`, `_check_D1`, `_all_points`,
`m6_sanity_check`, `stage_1`, `stage_2` are carried over unmodified in
logic. `cubic_roots` is also carried over unmodified, used here only for
the FIRST-several-hundred-candidates sanity check on the root-pair
construction itself (per the task card), not as part of the real Z=3
determination (which is now unconditional-by-construction, per the
specification's own declared search order).

NO NEW Q_e(T) CONSTRUCTION AND NO NEW CLASSIFIER IS WRITTEN HERE. Imports,
BY FILE PATH and read-only, the same two prior artifacts EXP-MONO-8ec0e5
used:

    experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py   as UC
        -> UC.classify_fibre, UC.resultant, UC.CLASSES
    experiments/EXP-MONO-815525/implementation/run_census.py          as RC
        -> RC.compile_sym / RC.qe_from_sym, RC.qe_from_resultant / compile_s3,
           RC.pt_add / RC.curve_order / RC.j_invariant / F_p[X] toolkit

Neither prior file is modified or copied. Both are bound by sha256 in the
output record.

FROZEN DEFINITIONS -- taken verbatim from IDEA-20260904-4f614a, notation
block and (D3), identical to all prior scripts in this sub-thread:

    f(X) = X^3 + A X + B ;   chi = quadratic character of F_p, chi(0) = 0
    Z    = #{x in F_p : f(x) = 0} in {0,1,3}
    tau  = #E(F_p)[2] = Z + 1
    n_+  = #{x in F_p : chi(f(x)) = +1}          <-- over ALL of F_p
    n_-  = #{x in F_p : chi(f(x)) = -1}
    h_+  = (#E(F_p)[4]   - tau) / 4
    h_-  = (#E^d(F_p)[4] - tau) / 4
    D_sum  := h_+ * n_-  +  h_- * n_+                      (D3, frozen)
    D_prod := h_+ * h_- * (n_+ + n_-)                       (named rival)

STAGE 0   root-pair search (NEW): for each prime p ascending in
          [101,2000], for each unordered pair (r1,r2), r1 ascending
          0..p-1 outer, r2 ascending r1+1..p-1 inner: r3=-(r1+r2) mod p;
          skip if r3 in {r1,r2}; else A,B computed directly (O(1)); Z=3
          unconditional by construction. Take the FIRST (A,B) with
          h_+>=1, h_->=1, max(h_+,h_-)>=2.
M6        pre-Stage-1 sanity check (unchanged logic).
STAGE 1   exhaustive distinct-split census (unchanged logic).
STAGE 2   compare Stage 1's observed counts against BOTH D_sum's and
          D_prod's predictions (unchanged logic).

Budget (specification.yaml, UNCHANGED): 900 s wall, 900 s CPU, 128 MiB
RSS, 1 worker, no network.
"""

import hashlib
import json
import os
import resource
import sys
import time
from itertools import combinations

T0 = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
UC_DIR = os.path.join(REPO, "experiments", "EXP-MONO-0e6e8f", "implementation")
RC_DIR = os.path.join(REPO, "experiments", "EXP-MONO-815525", "implementation")

sys.path.insert(0, UC_DIR)
sys.path.insert(0, RC_DIR)
import run_uncond_census as UC   # noqa: E402  EXP-MONO-0e6e8f, unmodified
import run_census as RC         # noqa: E402  EXP-MONO-815525, unmodified

CLASSES = UC.CLASSES            # ["1^4", "2+2", "2+1+1", "4", "3+1"]

SEED = 20260904010              # specification.yaml replication.seeds[0]
BUDGET_WALL_S = 900.0
BUDGET_RSS_BYTES = 134217728

# ---------------------------------------------------------------------------
# STAGE-0 SEARCH ORDER, DECLARED in specification.yaml `NEW_declared_search_order`.
PRIME_LO, PRIME_HI = 101, 2000
H_PLUS_MIN = 1
H_MINUS_MIN = 1
H_MAX_MIN = 2   # max(h_+, h_-) >= 2, excluding exactly (h_+,h_-)=(1,1)
MAX_STRATUM = 1200000
FILTER_AUDIT_N = 250          # h_pair fast-vs-bruteforce cross-check budget
CONSTRUCTION_AUDIT_N = 500    # root-pair -> (A,B) correctness self-check budget

# Internal wall-clock safety break for Stage 0 (pure engineering knob on how
# much of the already-approved 900s budget Stage 0 may consume; does not
# touch the declared range, order, or filter). The O(p^2) algorithm is
# expected to finish the full declared range comfortably inside this.
STAGE0_WALL_BREAK_S = 860.0

log = UC.log


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def C3(n):
    return n * (n - 1) * (n - 2) // 6 if n >= 3 else 0


def primes_in(lo, hi):
    sieve = bytearray([1]) * (hi + 1)
    sieve[0:2] = b"\0\0"
    for i in range(2, int(hi ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(lo, hi + 1) if sieve[i]]


# ------------------------------------------------------------------ curve data
def chi_table(p):
    """chi[v] = Legendre symbol of v mod p, chi[0] = 0."""
    t = [-1] * p
    t[0] = 0
    for x in range(1, (p + 1) // 2):
        t[x * x % p] = 1
    return t


def cubic_roots(A, B, p):
    """UNMODIFIED from EXP-MONO-8ec0e5. O(p) scan of range(p). Used here
    ONLY as the CONSTRUCTION_AUDIT_N correctness self-check on the new
    root-pair -> (A,B) construction, not as part of the real search."""
    return [x for x in range(p) if (x * x * x + A * x + B) % p == 0]


def nonresidue(p, chi):
    for d in range(2, p):
        if chi[d] == -1:
            return d
    raise RuntimeError("no non-residue mod %d" % p)


def count_4_torsion_bruteforce(p, A, B):
    """UNMODIFIED from EXP-MONO-8ec0e5. #{P in E(F_p) : 4P = O}, by literal
    enumeration of E(F_p) and repeated application of EXP-MONO-815525's own
    group law. O counts as one point. Deliberately naive: this is the
    definition, not an optimisation."""
    n = 1                                   # the point at infinity
    for x in range(p):
        v = (x * x * x + A * x + B) % p
        if v == 0:
            n += 1 if _is4(p, A, (x, 0)) else 0
            continue
        if pow(v, (p - 1) // 2, p) != 1:
            continue
        y = None
        for c in range(1, p):
            if c * c % p == v:
                y = c
                break
        for P in ((x, y), (x, (-y) % p)):
            if _is4(p, A, P):
                n += 1
    return n


def _is4(p, A, P):
    Q = RC.pt_add(p, A, P, P)               # 2P
    if Q is None:
        return True
    return RC.pt_add(p, A, Q, Q) is None    # 4P


def twist_params(A, B, d, p):
    """E^d : y^2 = x^3 + A d^2 x + B d^3 (IDEA notation block / handoff)."""
    return (A * d * d % p, B * d * d * d % p)


def h_pair_from_characters(roots, chi, p):
    """UNMODIFIED from EXP-MONO-8ec0e5. h_+ and h_- from the classical
    2-descent criterion, used ONLY as a fast search filter and
    cross-checked against brute force."""
    hp = hm = 0
    for i in range(3):
        j, k = [q for q in range(3) if q != i]
        a, b = chi[(roots[i] - roots[j]) % p], chi[(roots[i] - roots[k]) % p]
        if a == 1 and b == 1:
            hp += 1
        elif a == -1 and b == -1:
            hm += 1
    return hp, hm


def qualifies(hp, hm):
    """UNMODIFIED (CORR-20260904-b9f9c1): h_+>=1 AND h_->=1 AND
    max(h_+,h_-)>=2."""
    return hp >= H_PLUS_MIN and hm >= H_MINUS_MIN and max(hp, hm) >= H_MAX_MIN


# ================================================================== STAGE 0
def stage_0():
    log("\n--- STAGE 0 (NEW ALGORITHM): root-pair enumeration for a Z=3, "
        "h_+>=%d AND h_->=%d AND max(h_+,h_-)>=%d curve ---"
        % (H_PLUS_MIN, H_MINUS_MIN, H_MAX_MIN))
    log("declared search order: primes ascending in [%d, %d]; within a "
        "prime, r1 ascending 0..p-1 (outer), r2 ascending r1+1..p-1 "
        "(inner); r3 = -(r1+r2) mod p forced; skip if r3 in {r1,r2}; "
        "first hit taken." % (PRIME_LO, PRIME_HI))
    s0 = {
        "declared_range": {
            "prime_lo": PRIME_LO, "prime_hi": PRIME_HI,
            "order": "prime asc, then r1 asc, then r2 asc (r1<r2)",
            "h_plus_min": H_PLUS_MIN, "h_minus_min": H_MINUS_MIN,
            "h_max_min": H_MAX_MIN,
            "filter_note": (
                "UNCHANGED qualifying filter from EXP-MONO-8ec0e5 / "
                "CORR-20260904-b9f9c1: excludes exactly (h_+,h_-)=(1,1). "
                "Z=3 is now UNCONDITIONAL by construction (root-pair "
                "parameterization), not a filtered property."),
            "max_stratum_for_stage_1": MAX_STRATUM,
        },
        "construction_audit": {"n_audited": 0, "failures": []},
        "filter_audit": {"n_audited": 0, "disagreements": []},
        "per_prime": [],
        "primes_visited": [],
    }

    n_pairs_examined_total = 0    # (r1,r2) pairs looked at, all primes
    n_degenerate_total = 0        # r3 in {r1,r2}, skipped
    n_candidates_total = 0        # genuine 3-distinct-root candidates
    construction_audited = 0
    filter_audited = 0

    for p in primes_in(PRIME_LO, PRIME_HI):
        chi = chi_table(p)
        d = nonresidue(p, chi)
        s0["primes_visited"].append(p)
        pairs_this_prime = 0
        degenerate_this_prime = 0
        candidates_this_prime = 0

        for r1 in range(p):
            for r2 in range(r1 + 1, p):
                n_pairs_examined_total += 1
                pairs_this_prime += 1

                r3 = (-(r1 + r2)) % p
                if r3 == r1 or r3 == r2:
                    n_degenerate_total += 1
                    degenerate_this_prime += 1
                    continue

                roots = [r1, r2, r3]
                A = (r1 * r2 + r1 * r3 + r2 * r3) % p
                B = (-(r1 * r2 * r3)) % p
                n_candidates_total += 1
                candidates_this_prime += 1

                # ---- CONSTRUCTION_AUDIT_N: verify f(x)=x^3+Ax+B has
                # roots {r1,r2,r3} by direct substitution, and via the
                # independent cubic_roots() scan. Own correctness check,
                # not part of the declared search logic. ----
                if construction_audited < CONSTRUCTION_AUDIT_N:
                    construction_audited += 1
                    ok_subst = all(
                        (r ** 3 + A * r + B) % p == 0 for r in roots)
                    slow_roots = sorted(cubic_roots(A, B, p))
                    ok_slow = (slow_roots == sorted(roots))
                    if not (ok_subst and ok_slow):
                        s0["construction_audit"]["failures"].append(
                            {"p": p, "r1": r1, "r2": r2, "r3": r3,
                             "A": A, "B": B,
                             "direct_substitution_ok": ok_subst,
                             "cubic_roots_matches": ok_slow,
                             "cubic_roots_result": slow_roots})

                # non-singularity: guaranteed by construction (r1,r2,r3
                # distinct), verify anyway.
                nonsingular = (4 * pow(A, 3, p) + 27 * B * B) % p != 0
                if not nonsingular:
                    # Would contradict the construction; recorded, not
                    # silently skipped.
                    s0["construction_audit"]["failures"].append(
                        {"p": p, "r1": r1, "r2": r2, "r3": r3, "A": A,
                         "B": B, "unexpected_singular": True})
                    continue

                N = RC.curve_order(p, A, B)
                if (p + 1 - N) % p == 0:
                    continue                       # supersingular: skip

                hp, hm = h_pair_from_characters(roots, chi, p)

                if filter_audited < FILTER_AUDIT_N:
                    filter_audited += 1
                    Ad, Bd = twist_params(A, B, d, p)
                    e4 = count_4_torsion_bruteforce(p, A, B)
                    e4d = count_4_torsion_bruteforce(p, Ad, Bd)
                    bp, bm = (e4 - 4) // 4, (e4d - 4) // 4
                    if (bp, bm) != (hp, hm) or (e4 - 4) % 4 or (e4d - 4) % 4:
                        s0["filter_audit"]["disagreements"].append(
                            {"p": p, "A": A, "B": B, "fast": [hp, hm],
                             "bruteforce": [bp, bm],
                             "E4": e4, "Ed4": e4d,
                             "context": "h_pair_filter_audit"})

                if not qualifies(hp, hm):
                    continue

                # ---- candidate: verify everything by direct construction ----
                Ad, Bd = twist_params(A, B, d, p)
                e4 = count_4_torsion_bruteforce(p, A, B)
                e4d = count_4_torsion_bruteforce(p, Ad, Bd)
                Nd = RC.curve_order(p, Ad, Bd)
                Z = 3
                tau = Z + 1
                n_plus = sum(1 for x in range(p)
                             if chi[(x * x * x + A * x + B) % p] == 1)
                n_minus = sum(1 for x in range(p)
                              if chi[(x * x * x + A * x + B) % p] == -1)
                h_plus = (e4 - tau) // 4
                h_minus = (e4d - tau) // 4
                if not qualifies(h_plus, h_minus):
                    continue

                stratum = C3(n_plus + n_minus)

                s0["per_prime"].append({
                    "p": p, "pairs_examined": pairs_this_prime,
                    "degenerate": degenerate_this_prime,
                    "candidates": candidates_this_prime,
                    "found_here": True})

                found = {
                    "p": p, "A": A, "B": B, "d_nonresidue": d,
                    "twist_A": Ad, "twist_B": Bd,
                    "j_invariant": RC.j_invariant(p, A, B),
                    "f_roots": roots, "root_pair_r1_r2": [r1, r2],
                    "Z": Z, "tau": tau,
                    "order_E": N, "trace_t": p + 1 - N,
                    "order_Ed_counted": Nd,
                    "order_Ed_formula_2p_plus_2_minus_NE": 2 * p + 2 - N,
                    "E4_bruteforce": e4, "Ed4_bruteforce": e4d,
                    "n_plus": n_plus, "n_minus": n_minus,
                    "h_plus": h_plus, "h_minus": h_minus,
                    "h_plus_h_minus_fast_criterion": [hp, hm],
                    "stratum_size_C3": stratum,
                    "root_pairs_examined_before_success": n_pairs_examined_total,
                    "degenerate_pairs_skipped_total": n_degenerate_total,
                    "candidates_examined_total": n_candidates_total,
                }
                ck = found["checks"] = {}
                ck["twist_order_matches_2p+2-N"] = (Nd == 2 * p + 2 - N)
                ck["tau_equals_Z_plus_1"] = (tau == Z + 1)
                ck["E4_minus_tau_divisible_by_4"] = ((e4 - tau) % 4 == 0)
                ck["Ed4_minus_tau_divisible_by_4"] = ((e4d - tau) % 4 == 0)
                ck["n_plus_plus_n_minus_equals_p_minus_Z"] = (
                    n_plus + n_minus == p - Z)
                ck["n_plus_minus_n_minus_equals_minus_t"] = (
                    n_plus - n_minus == -(p + 1 - N))
                ck["fast_criterion_agrees_with_bruteforce"] = (
                    [hp, hm] == [h_plus, h_minus])
                ck["h_plus_at_least_threshold"] = (h_plus >= H_PLUS_MIN)
                ck["h_minus_at_least_threshold"] = (h_minus >= H_MINUS_MIN)
                ck["max_h_plus_h_minus_at_least_2"] = (
                    max(h_plus, h_minus) >= H_MAX_MIN)
                ck["not_the_excluded_coincidence_point"] = (
                    not (h_plus == 1 and h_minus == 1))
                ck["four_divides_order_E"] = (N % 4 == 0)
                ck["n_plus_even_internal_parity_check_step5"] = (
                    n_plus % 2 == 0)
                ck["stratum_within_budget_cap"] = (stratum <= MAX_STRATUM)
                ck["D1_involution_and_fixed_points"] = _check_D1(
                    p, A, B, roots, chi)

                s0["construction_audit"]["n_audited"] = construction_audited
                s0["filter_audit"]["n_audited"] = filter_audited
                s0["found_curve"] = found
                s0["outcome"] = "qualifying_curve_found"
                log("  FOUND: p=%d r1=%d r2=%d r3=%d -> A=%d B=%d"
                    % (p, r1, r2, r3, A, B))
                log("         Z=%d tau=%d  #E=%d #E^d=%d"
                    % (Z, tau, N, Nd))
                log("         #E[4]=%d #E^d[4]=%d -> h_+=%d h_-=%d"
                    % (e4, e4d, h_plus, h_minus))
                log("         n_+=%d n_-=%d  stratum C(%d,3)=%d"
                    % (n_plus, n_minus, n_plus + n_minus, stratum))
                log("         root pairs examined: %d" % n_pairs_examined_total)
                log("  checks: %s" % json.dumps(ck))
                return s0

        s0["per_prime"].append({
            "p": p, "pairs_examined": pairs_this_prime,
            "degenerate": degenerate_this_prime,
            "candidates": candidates_this_prime,
            "found_here": False})

        if time.time() - T0 > STAGE0_WALL_BREAK_S:
            s0["stage0_wall_break_hit"] = True
            s0["last_prime_fully_scanned"] = p
            break

    s0["construction_audit"]["n_audited"] = construction_audited
    s0["filter_audit"]["n_audited"] = filter_audited
    if s0.get("stage0_wall_break_hit"):
        s0["outcome"] = "budget_exhausted_partial_range_search"
    else:
        s0["outcome"] = "range_exhausted_no_qualifying_curve"
    s0["root_pairs_examined_total"] = n_pairs_examined_total
    s0["degenerate_pairs_skipped_total"] = n_degenerate_total
    s0["candidates_examined_total"] = n_candidates_total
    return s0


def _check_D1(p, A, B, roots, chi):
    """UNMODIFIED from EXP-MONO-8ec0e5. (D1): mu_T(x) = x_T + f'(x_T)/(x -
    x_T) is an involution of P^1, and its fixed points are the
    x-coordinates of the four Q with 2Q = T, rational iff
    chi(f'(x_T)) = +1."""
    out = []
    for xT in roots:
        fp = 1
        for r in roots:
            if r != xT:
                fp = fp * (xT - r) % p
        involutive = all(
            (xT + fp * pow((xT + fp * pow((x - xT) % p, -1, p) - xT) % p,
                           -1, p)) % p == x % p
            for x in range(p) if x != xT and
            (xT + fp * pow((x - xT) % p, -1, p)) % p != xT)
        fixed = [x for x in range(p) if (x - xT) * (x - xT) % p == fp % p]
        chis = sorted({chi[(x ** 3 + A * x + B) % p] for x in fixed})
        halvable_rationally = any(
            RC.pt_add(p, A, Q, Q) == (xT, 0)
            for Q in _all_points(p, A, B))
        out.append({
            "x_T": xT, "f_prime_x_T": fp % p, "chi_f_prime": chi[fp % p],
            "mu_T_is_involution": involutive,
            "n_rational_fixed_points": len(fixed),
            "fixed_points_rational_iff_chi_plus1":
                (len(fixed) == 2) == (chi[fp % p] == 1),
            "common_chi_f_on_fixed_points": chis,
            "T_in_2E_Fp": halvable_rationally,
            "chi_plus1_on_fixed_iff_T_in_2E":
                (chis == [1]) == halvable_rationally if fixed else None,
        })
    return out


def _all_points(p, A, B):
    for x in range(p):
        v = (x * x * x + A * x + B) % p
        if v == 0:
            yield (x, 0)
        elif pow(v, (p - 1) // 2, p) == 1:
            for c in range(1, p):
                if c * c % p == v:
                    yield (x, c)
                    yield (x, (-c) % p)
                    break


# ============================================================ M6 SANITY CHECK
def m6_sanity_check(found):
    """UNMODIFIED from EXP-MONO-8ec0e5. Computes D_sum and D_prod from the
    found curve's own (n_+, n_-, h_+, h_-) and explicitly verifies
    D_sum != D_prod, using the proven identity
        D_prod - D_sum = h_-*(h_+-1)*n_+ + h_+*(h_--1)*n_-
    which is zero iff h_+=h_-=1."""
    log("\n--- M6: pre-Stage-1 sanity check (D_sum != D_prod?) ---")
    n_p, n_m = found["n_plus"], found["n_minus"]
    h_p, h_m = found["h_plus"], found["h_minus"]

    D_sum = h_p * n_m + h_m * n_p
    D_prod = h_p * h_m * (n_p + n_m)
    diff_direct = D_prod - D_sum
    identity_rhs = h_m * (h_p - 1) * n_p + h_p * (h_m - 1) * n_m

    def predicted(D):
        return {
            "1^4": C3(n_p) + C3(n_m) + D,
            "2+1+1": 3 * n_p * n_m - 3 * D,
            "2+2": C3(n_p + n_m) - C3(n_p) - C3(n_m) - 3 * n_p * n_m + 2 * D,
        }

    predicted_sum = predicted(D_sum)
    predicted_prod = predicted(D_prod)

    identity_self_consistent = (diff_direct == identity_rhs)
    passed = (D_sum != D_prod) and identity_self_consistent

    out = {
        "n_plus": n_p, "n_minus": n_m, "h_plus": h_p, "h_minus": h_m,
        "D_sum": D_sum,
        "D_sum_terms": {"h_plus*n_minus": h_p * n_m,
                        "h_minus*n_plus": h_m * n_p},
        "D_prod": D_prod,
        "D_prod_terms": {"h_plus*h_minus*(n_plus+n_minus)": D_prod},
        "D_prod_minus_D_sum_direct": diff_direct,
        "identity_rhs_h_minus_(h_plus-1)_n_plus_plus_h_plus_(h_minus-1)_n_minus":
            identity_rhs,
        "identity_self_consistent": identity_self_consistent,
        "D_sum_not_equal_D_prod": (D_sum != D_prod),
        "excluded_coincidence_point_h_plus_eq_h_minus_eq_1":
            (h_p == 1 and h_m == 1),
        "predicted_sum": predicted_sum,
        "predicted_prod": predicted_prod,
        "passed": passed,
        "note": (
            "PASS means D_sum != D_prod was confirmed algebraically on this "
            "specific found curve BEFORE Stage 1 runs, per CORR-20260904-"
            "b9f9c1's proven identity and the corrected Stage-0 filter. FAIL "
            "means the corrected filter did not exclude the coincidence "
            "point despite the proof -- a bug in the identity's "
            "implementation or in Stage 0's filter, not a valid research "
            "outcome; Stage 1/2 must not run."),
    }
    log("  D_sum  = h_+*n_- + h_-*n_+   = %d*%d + %d*%d = %d"
        % (h_p, n_m, h_m, n_p, D_sum))
    log("  D_prod = h_+*h_-*(n_++n_-)   = %d*%d*(%d+%d) = %d"
        % (h_p, h_m, n_p, n_m, D_prod))
    log("  D_prod - D_sum (direct)     = %d" % diff_direct)
    log("  identity RHS h_-(h_+-1)n_+ + h_+(h_--1)n_- = %d" % identity_rhs)
    log("  identity self-consistent: %s   D_sum != D_prod: %s"
        % (identity_self_consistent, D_sum != D_prod))
    log("  M6 %s" % ("PASSED" if passed else "FAILED"))
    return out


# ================================================================== STAGE 1
def stage_1(found):
    """UNMODIFIED from EXP-MONO-8ec0e5. Exhaustive census of the
    distinct-split stratum, using EXP-MONO-0e6e8f's own classifier and
    EXP-MONO-815525's own Q_e construction, unmodified. Only reached if
    M6 passed."""
    p, A, B = found["p"], found["A"], found["B"]
    log("\n--- STAGE 1: exhaustive distinct-split census, p=%d A=%d B=%d ---"
        % (p, A, B))
    symtab = RC.compile_sym(p, A, B)
    s3tab = RC.compile_s3(p, A, B)
    f = RC.pnorm([B, A, 0, 1], p)
    S = [x for x in range(p) if (x ** 3 + A * x + B) % p != 0]
    assert len(S) == p - found["Z"]

    counts = {c: 0 for c in CLASSES}
    ramified = {c: 0 for c in CLASSES}
    affine_counts = {}
    deg_counts = {}
    n_points = 0
    n_zero_qe = 0
    n_res_zero = 0
    examples = {c: [] for c in CLASSES}
    xcheck = {"n": 0, "mismatch": 0, "non_rational": 0, "mismatches": []}

    for t1, t2, t3 in combinations(S, 3):
        e1 = (t1 + t2 + t3) % p
        e2 = (t1 * t2 + t1 * t3 + t2 * t3) % p
        e3 = (t1 * t2 * t3) % p
        n_points += 1
        g = [(-e3) % p, e2 % p, (-e1) % p, 1]
        if UC.resultant(g, f, p) == 0:
            n_res_zero += 1
            continue
        qe = RC.qe_from_sym(symtab, p, e1, e2, e3)
        cl = UC.classify_fibre(qe, p)
        if cl is None:
            n_zero_qe += 1
            continue
        k = cl["class"]
        counts[k] += 1
        if not cl["squarefree"]:
            ramified[k] += 1
        affine_counts[cl["affine_pattern"]] = \
            affine_counts.get(cl["affine_pattern"], 0) + 1
        deg_counts[cl["degree_in_T"]] = deg_counts.get(cl["degree_in_T"], 0) + 1
        if len(examples[k]) < 20:
            examples[k].append({"roots": [t1, t2, t3], "e": [e1, e2, e3],
                                "Qe": qe, "class": k,
                                "squarefree": cl["squarefree"]})
        if n_points % 5000 == 1 and xcheck["n"] < 400:
            xcheck["n"] += 1
            F = RC.F3(p, e1, e2, e3)
            X1, X2, X3 = (t1, 0, 0), (t2, 0, 0), (t3, 0, 0)
            alt = RC.qe_from_resultant(s3tab, F, X1, X2, X3)
            alt_fp = RC.to_fp(alt, p)
            if alt_fp is None:
                xcheck["non_rational"] += 1
                xcheck["mismatches"].append(
                    {"e": [e1, e2, e3], "reason": "resultant_not_Fp_rational"})
            elif RC.pnorm(alt_fp, p) != qe:
                xcheck["mismatch"] += 1
                xcheck["mismatches"].append(
                    {"e": [e1, e2, e3], "fast": qe,
                     "resultant": RC.pnorm(alt_fp, p)})

    log("  base points: %d   classified: %d" % (n_points, sum(counts.values())))
    for c in CLASSES:
        log("    %-7s %d" % (c, counts[c]))
    log("  resultant cross-check: %d sampled, %d mismatch, %d non-rational"
        % (xcheck["n"], xcheck["mismatch"], xcheck["non_rational"]))
    return {
        "p": p, "A": A, "B": B,
        "stratum": "distinct-split: unordered triples of distinct roots in "
                   "F_p \\ Z(f); |S| = n_+ + n_- = p - Z",
        "stratum_size_enumerated": n_points,
        "stratum_size_C3_predicted": C3(len(S)),
        "counts": counts,
        "total_classified": sum(counts.values()),
        "ramified_by_class": ramified,
        "n_resultant_zero": n_res_zero,
        "n_zero_qe": n_zero_qe,
        "affine_pattern_counts": affine_counts,
        "degree_in_T_counts": {str(k): v for k, v in deg_counts.items()},
        "examples": examples,
        "resultant_crosscheck": xcheck,
        "resultant_crosscheck_note": (
            "Reused unmodified from EXP-MONO-8ec0e5's own final stage_1(), "
            "which itself carried it forward from EXP-MONO-98abb2 / "
            "EXP-MONO-4e6faa/EXP-MONO-ee06e2; no dead-cross-check issue "
            "exists here to re-fix."),
    }


# ================================================================== STAGE 2
def stage_2(found, m6, s1):
    """UNMODIFIED from EXP-MONO-8ec0e5. Exact comparison: observed vs.
    D_sum (frozen D3) vs. D_prod (named multiplicative rival), reusing
    the predictions already computed in M6. Only reached if M6 passed.
    Zero tolerance throughout."""
    log("\n--- STAGE 2: exact comparison vs. both predictions (M6 already "
        "computed both) ---")
    obs = s1["counts"]
    predicted_sum = m6["predicted_sum"]
    predicted_prod = m6["predicted_prod"]

    R1_sum = obs["1^4"] - predicted_sum["1^4"]
    R2_sum = obs["2+1+1"] - predicted_sum["2+1+1"]
    R3_sum = obs["2+2"] - predicted_sum["2+2"]
    R1_prod = obs["1^4"] - predicted_prod["1^4"]
    R2_prod = obs["2+1+1"] - predicted_prod["2+1+1"]
    R3_prod = obs["2+2"] - predicted_prod["2+2"]

    out = {
        "frozen_prediction_source": (
            "IDEA-20260904-4f614a (D3), unmodified; formula verified "
            "against that record's own text ('D := h_+ * n_- + h_- * "
            "n_+ .') before writing this script."),
        "rival_prediction_source": (
            "H-MONO-1297d7's own mechanism field (same named rival as "
            "all prior scripts in this sub-thread): "
            "D_prod = h_+ * h_- * (n_+ + n_-)"),
        "n_plus": found["n_plus"], "n_minus": found["n_minus"],
        "h_plus": found["h_plus"], "h_minus": found["h_minus"],
        "D_sum": m6["D_sum"], "D_prod": m6["D_prod"],
        "predicted_sum": predicted_sum,
        "predicted_prod": predicted_prod,
        "observed": obs,
        "R1_sum_1^4": R1_sum,
        "R2_sum_2+1+1": R2_sum,
        "R3_sum_2+2_bonus": R3_sum,
        "R1_prod_1^4": R1_prod,
        "R2_prod_2+1+1": R2_prod,
        "R3_prod_2+2_bonus": R3_prod,
        "R1_sum_is_zero": R1_sum == 0,
        "R2_sum_is_zero": R2_sum == 0,
        "R1_prod_is_zero": R1_prod == 0,
        "R2_prod_is_zero": R2_prod == 0,
        "class_4_count": obs["4"], "class_3+1_count": obs["3+1"],
        "closed_form_implies_4_and_3+1_are_zero_on_this_stratum": True,
    }
    for k, r1, r2 in (("1^4", "R1_sum_1^4", "R1_prod_1^4"),
                      ("2+1+1", "R2_sum_2+1+1", "R2_prod_2+1+1"),
                      ("2+2", "R3_sum_2+2_bonus", "R3_prod_2+2_bonus")):
        log("  %-7s observed %d   sum-pred %d (resid %d)   "
            "prod-pred %d (resid %d)"
            % (k, obs[k], predicted_sum[k], out[r1], predicted_prod[k],
               out[r2]))
    log("  R1_sum=%d R2_sum=%d   R1_prod=%d R2_prod=%d"
        % (R1_sum, R2_sum, R1_prod, R2_prod))
    return out


# ====================================================================== MAIN
def main():
    if len(sys.argv) < 2:
        print("usage: run_root_pair_search.py <out_raw_result_json>",
              file=sys.stderr)
        return 2
    out_path = os.path.abspath(sys.argv[1])

    report = {
        "experiment_id": "EXP-MONO-d4840b",
        "run_id": "RUN-MONO-d4840b-1",
        "hypothesis_id": "H-MONO-dd666a",
        "seed": SEED,
        "randomness_sources": [
            "NONE. This run is fully deterministic: the Stage-0 root-pair "
            "search order and the Stage-1 stratum enumeration are both "
            "fixed integer orders. The specification seed 20260904010 is "
            "recorded but no random number generator is instantiated."],
        "reused_artifacts_sha256": {
            "EXP-MONO-0e6e8f/implementation/run_uncond_census.py":
                sha256(os.path.join(UC_DIR, "run_uncond_census.py")),
            "EXP-MONO-815525/implementation/run_census.py":
                sha256(os.path.join(RC_DIR, "run_census.py")),
            "EXP-MONO-815525/implementation/s4_symmetric_coeffs.json":
                sha256(os.path.join(RC_DIR, "s4_symmetric_coeffs.json")),
            "EXP-MONO-815525/implementation/s3_monomials.json":
                sha256(os.path.join(RC_DIR, "s3_monomials.json")),
            "EXP-MONO-815525/implementation/s4_monomials.json":
                sha256(os.path.join(RC_DIR, "s4_monomials.json")),
        },
        "python_version": sys.version.split()[0],
    }

    # ---- STAGE 0: the new O(p^2) root-pair search ----
    s0 = stage_0()
    report["stage_0"] = s0

    if s0["construction_audit"]["failures"]:
        report["disposition"] = "invalid_measurement"
        report["failure_classification"] = "specification_error"
        report["outcome"] = (
            "CONSTRUCTION_AUDIT_FAILED: the root-pair -> (A,B) construction "
            "did not produce the claimed roots {r1,r2,r3} (or disagreed "
            "with an independent cubic_roots() scan) on at least one of "
            "the first %d candidates audited. See "
            "stage_0.construction_audit.failures for the exact "
            "counterexample(s). Per this experiment's own algorithmic "
            "premise, this would be a correctness bug in the new "
            "construction, not a valid research outcome." % CONSTRUCTION_AUDIT_N)
        report["certificate"] = {
            "kind": "none",
            "note": "Run halted at the construction audit; nothing to "
                     "certify."}
        _finish(report, out_path)
        return 0

    if s0["outcome"] == "range_exhausted_no_qualifying_curve":
        report["disposition"] = "completed_valid"
        report["outcome"] = "no_qualifying_curve_found"
        report["certificate"] = {
            "kind": "none",
            "note": "Pure measurement run; no solve or relation claimed."}
        _finish(report, out_path)
        return 0
    if s0["outcome"] == "budget_exhausted_partial_range_search":
        report["disposition"] = "resource_exhaustion"
        report["failure_classification"] = "resource_exhaustion"
        report["outcome"] = (
            "BUDGET_EXHAUSTED_BEFORE_FULL_RANGE_SEARCHED: Stage 0's "
            "root-pair search reached its internal wall-clock safety break "
            "(STAGE0_WALL_BREAK_S=%.0fs, inside the specification's 900s "
            "total budget) after examining %d root pairs (%d degenerate, "
            "%d genuine candidates) across primes up to and including %d, "
            "out of the full declared range [%d, %d], without finding a "
            "curve satisfying Z=3 AND h_+>=1 AND h_->=1 AND "
            "max(h_+,h_-)>=2. This is a resource_exhaustion outcome, NOT a "
            "declared-range exhaustion and NOT evidence for or against "
            "H-MONO-dd666a either way."
            % (STAGE0_WALL_BREAK_S, s0["root_pairs_examined_total"],
               s0["degenerate_pairs_skipped_total"],
               s0["candidates_examined_total"],
               s0["last_prime_fully_scanned"], PRIME_LO, PRIME_HI))
        report["certificate"] = {
            "kind": "none",
            "note": "Pure measurement run; no solve or relation claimed."}
        _finish(report, out_path)
        return 0

    found = s0["found_curve"]
    if not found["checks"]["stratum_within_budget_cap"]:
        report["disposition"] = "completed_valid"
        report["outcome"] = "qualifying_curve_found_but_stratum_over_budget"
        report["certificate"] = {
            "kind": "none",
            "note": "Pure measurement run; no solve or relation claimed."}
        _finish(report, out_path)
        return 0

    m6 = m6_sanity_check(found)
    report["m6_sanity_check"] = m6
    if not m6["passed"]:
        report["disposition"] = "invalid_measurement"
        report["failure_classification"] = "specification_error"
        report["outcome"] = (
            "M6_SANITY_CHECK_FAILED: D_sum == D_prod on the found curve "
            "despite the corrected max(h_+,h_-)>=2 filter, which is PROVEN "
            "(CORR-20260904-b9f9c1) to exclude the only such point. This "
            "indicates a bug in the identity's implementation, in the "
            "Stage-0 filter, or in the found curve's own h_+/h_- "
            "computation -- not a valid research outcome. Stage 1 and "
            "Stage 2 were NOT run, per the specification's stopping rules "
            "and the task card's explicit instruction.")
        report["certificate"] = {
            "kind": "none",
            "note": "Run halted at M6; no census performed, nothing to "
                     "certify."}
        _finish(report, out_path)
        return 0

    s1 = stage_1(found)
    report["stage_1"] = s1
    report["stage_2"] = stage_2(found, m6, s1)
    report["certificate"] = {
        "kind": "none",
        "note": ("Pure measurement run. No discrete-log solve and no "
                 "factor-base relation is claimed. The construction is "
                 "EXP-MONO-0e6e8f's own already-independently-verified one, "
                 "reused unmodified and bound by sha256 above.")}
    report["disposition"] = "completed_valid"
    report["outcome"] = ("bivariate_additive_vs_multiplicative_comparison_"
                         "executed_with_root_pair_search; "
                         "R1_sum=%d R2_sum=%d R1_prod=%d R2_prod=%d"
                         % (report["stage_2"]["R1_sum_1^4"],
                            report["stage_2"]["R2_sum_2+1+1"],
                            report["stage_2"]["R1_prod_1^4"],
                            report["stage_2"]["R2_prod_2+1+1"]))
    _finish(report, out_path)
    return 0


def _finish(report, out_path):
    ru = resource.getrusage(resource.RUSAGE_SELF)
    report["wall_seconds"] = round(time.time() - T0, 1)
    report["cpu_seconds"] = round(ru.ru_utime + ru.ru_stime, 1)
    report["peak_rss_bytes"] = int(ru.ru_maxrss)
    report["budget"] = {"maximum_wall_seconds": BUDGET_WALL_S,
                        "maximum_peak_rss_bytes": BUDGET_RSS_BYTES,
                        "wall_within_budget":
                            report["wall_seconds"] <= BUDGET_WALL_S,
                        "rss_within_budget":
                            report["peak_rss_bytes"] <= BUDGET_RSS_BYTES}
    log("\nwall %.1fs  cpu %.1fs  peak RSS %d bytes"
        % (report["wall_seconds"], report["cpu_seconds"],
           report["peak_rss_bytes"]))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(report, open(out_path, "w"), indent=1)
    log("wrote %s" % out_path)


if __name__ == "__main__":
    sys.exit(main())
