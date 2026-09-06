"""
EXP-MONO-8ec0e5 -- the CORRECTED re-test of EXP-MONO-98abb2's own bivariate
(h_+, h_-) joint-regime test of IDEA-20260904-4f614a's closed form (D3)
against the named multiplicative-interaction rival D_prod.

WHY THIS SCRIPT EXISTS (full story in ledger/corrections/CORR-20260904-b9f9c1.
yaml). EXP-MONO-98abb2's own Stage-0 filter (Z=3 AND h_+>=1 AND h_->=1) let
its fixed, ascending search order land on p=103, A=1, B=11, where h_+=1 AND
h_-=1 -- the UNIQUE point in the admissible domain where D_sum and D_prod are
algebraically identical (proven identity, both reviewers independently:
    D_prod - D_sum = h_-(h_+-1) n_+  +  h_+(h_--1) n_-
which is exactly zero iff h_+ = h_- = 1, and strictly positive at every other
(h_+,h_-) with h_+>=1, h_->=1, n_+,n_->0). That run was therefore VALID but
NON-DISCRIMINATING: R1_sum=R2_sum=R1_prod=R2_prod=0 could not distinguish the
two rival predictions, because both predictions were the same number.

Two independent reviewers proved the exact, necessary-and-sufficient fix:
    REQUIRE max(h_+, h_-) >= 2   (equivalently: exclude exactly (h_+,h_-)=(1,1))
This is NOT the weaker, non-tight "h_+ != h_-" fix an earlier, superseded
correction (CORR-20260904-e526e0) proposed -- that fix would needlessly
exclude perfectly good discriminating curves such as h_+=h_-=2 (where
D_prod-D_sum = 2(n_++n_-) > 0, per the identity above with h_+=h_-=2).

ADAPTED, STRUCTURE OTHERWISE UNCHANGED, from
    experiments/EXP-MONO-98abb2/implementation/run_bivariate_test.py
(read in full before writing this file). The changes from that script are:
  (1) STAGE 0's qualifying filter: Z=3 AND h_+>=1 AND h_->=1 AND
      max(h_+,h_-)>=2, instead of the bare h_+>=1 AND h_->=1 that admitted
      the coincidence point. The search order itself -- primes ascending in
      [101,2000], then A ascending, then B ascending, first hit taken -- is
      UNCHANGED and is not biased toward any previously-named (A,B) pair;
      the only lines that decide acceptance are the `hp>=1 and hm>=1 and
      max(hp,hm)>=2` tests below (fast-filter and post-brute-force
      re-check). No literal (A,B) pair from any prior review is referenced
      anywhere in this file's control flow.
  (2) NEW pre-Stage-1 sanity check (M6): immediately after a qualifying
      curve is found and BEFORE Stage 1 runs, compute D_sum and D_prod from
      the found curve's own (n_+, n_-, h_+, h_-) and explicitly verify
      D_sum != D_prod (equivalently, verify the identity's right-hand side
      h_-(h_+-1)n_+ + h_+(h_--1)n_- is nonzero). If this fails, STOP: do not
      run Stage 1 or Stage 2, and report `specification_error` -- this would
      indicate a bug in the identity's implementation, not a valid research
      outcome, since the corrected filter is PROVEN to exclude the only
      coincidence point.
  (3) Stage 1 and Stage 2 are otherwise IDENTICAL in logic to
      run_bivariate_test.py's own stage_1()/stage_2(), reusing the same two
      already-verified upstream artifacts by file path, read-only.

NO NEW Q_e(T) CONSTRUCTION AND NO NEW CLASSIFIER IS WRITTEN HERE. Imports,
BY FILE PATH and read-only, exactly the same two prior artifacts:

    experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py   as UC
        -> UC.classify_fibre, UC.resultant, UC.CLASSES
    experiments/EXP-MONO-815525/implementation/run_census.py          as RC
        -> RC.compile_sym / RC.qe_from_sym, RC.qe_from_resultant / compile_s3,
           RC.pt_add / RC.curve_order / RC.j_invariant / F_p[X] toolkit

Neither prior file is modified or copied. Both are bound by sha256 in the
output record.

FROZEN DEFINITIONS -- taken verbatim from IDEA-20260904-4f614a, notation
block and (D3):

    f(X) = X^3 + A X + B ;   chi = quadratic character of F_p, chi(0) = 0
    Z    = #{x in F_p : f(x) = 0} in {0,1,3}
    tau  = #E(F_p)[2] = Z + 1
    n_+  = #{x in F_p : chi(f(x)) = +1}          <-- over ALL of F_p
    n_-  = #{x in F_p : chi(f(x)) = -1}
    h_+  = (#E(F_p)[4]   - tau) / 4
    h_-  = (#E^d(F_p)[4] - tau) / 4
    D_sum  := h_+ * n_-  +  h_- * n_+                      (D3, frozen)
    #1^4    = C(n_+,3) + C(n_-,3) + D_sum
    #2+1+1  = 3 n_+ n_-  -  3 D_sum
    #2+2    = C(n_+ + n_-,3) - C(n_+,3) - C(n_-,3) - 3 n_+ n_- + 2 D_sum

The named multiplicative-interaction rival (same as EXP-MONO-98abb2's own,
from H-MONO-1297d7's own mechanism field):
    D_prod := h_+ * h_- * (n_+ + n_-)
with the SAME #1^4 / #2+1+1 / #2+2 combinatorial identities as (D3), but
with D_sum replaced by D_prod.

The proven identity checked by M6 (CORR-20260904-b9f9c1):
    D_prod - D_sum = h_-*(h_+-1)*n_+ + h_+*(h_--1)*n_-
which is zero iff h_+ = h_- = 1 (given n_+, n_- > 0).

STAGE 0  search for a curve with Z=3 AND h_+>=1 AND h_->=1 AND
         max(h_+,h_-)>=2 (CORRECTED filter).
M6       pre-Stage-1 sanity check: verify D_sum != D_prod algebraically on
         the found curve, by direct substitution. STOP on failure.
STAGE 1  exhaustive distinct-split census on the found curve (unchanged
         logic, only reached if M6 passes).
STAGE 2  compare Stage 1's observed counts against BOTH D_sum's and
         D_prod's own predicted #1^4, #2+1+1 (already computed in M6);
         report R1_sum, R2_sum, R1_prod, R2_prod exactly (only reached if
         M6 passes).

Budget (specification.yaml): 900 s wall, 900 s CPU, 128 MiB RSS, 1 worker,
no network.
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

SEED = 20260904007              # specification.yaml replication.seeds[0]
BUDGET_WALL_S = 900.0
BUDGET_RSS_BYTES = 134217728

# ---------------------------------------------------------------------------
# STAGE-0 SEARCH ORDER, DECLARED HERE BEFORE ANY STAGE-1 / STAGE-2 RESULT.
# Deterministic, no randomness: primes ascending in [PRIME_LO, PRIME_HI], and
# within each prime A ascending 0..p-1, then B ascending 0..p-1. The FIRST
# curve satisfying (non-singular, ordinary, Z=3, h_+>=1 AND h_->=1 AND
# max(h_+,h_-)>=2 -- the CORRECTED filter) is taken. Curves examined are
# counted exactly. The declared range is the specification's own [101, 2000].
# No literal (A,B) pair is referenced anywhere in this file's acceptance
# test.
PRIME_LO, PRIME_HI = 101, 2000
H_PLUS_MIN = 1
H_MINUS_MIN = 1
H_MAX_MIN = 2   # NEW: max(h_+, h_-) >= 2, excluding exactly (h_+,h_-)=(1,1)
# Hard cap on the Stage-1 stratum so the exhaustive census fits the 900 s
# budget. Declared before the search. C(n_+ + n_-, 3) must not exceed this;
# a qualifying curve over the cap would be reported as a budget-blocked find,
# never silently skipped.
MAX_STRATUM = 1200000
# Number of Z=3 curves on which the fast character-based h_+/h_- criterion is
# cross-checked against brute-force 4-torsion point counting before it is
# trusted as a search filter.
FILTER_AUDIT_N = 250
# Internal wall-clock safety break for Stage 0, leaving room within the
# specification's own 900 s total budget for the rest of this process
# (Stage 1/2 if a curve is found, plus I/O). EXP-MONO-98abb2's own script
# used 300 s here, tuned for that experiment's filter, which happened to
# succeed after only 10,316 (A,B) pairs. This experiment's CORRECTED,
# strictly rarer filter (max(h_+,h_-)>=2 in addition to h_+>=1 AND h_->=1)
# did not succeed within the first 300 s (see implementation.md for the
# disclosed first attempt); this constant is raised to use more of the
# approved 900 s budget, WITHOUT changing the declared search range
# [PRIME_LO, PRIME_HI], the search order, or the qualifying filter itself.
STAGE0_WALL_BREAK_S = 850.0

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
    return [x for x in range(p) if (x * x * x + A * x + B) % p == 0]


def nonresidue(p, chi):
    for d in range(2, p):
        if chi[d] == -1:
            return d
    raise RuntimeError("no non-residue mod %d" % p)


def count_4_torsion_bruteforce(p, A, B):
    """#{P in E(F_p) : 4P = O}, by literal enumeration of E(F_p) and repeated
    application of EXP-MONO-815525's own group law. O counts as one point.
    Deliberately naive: this is the definition, not an optimisation."""
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
    """h_+ and h_- from the classical 2-descent criterion, used ONLY as a fast
    search filter and cross-checked against brute force. For T = (e_i, 0),
    f'(e_i) = (e_i-e_j)(e_i-e_k); by (D1) T is halvable over F_p iff both
    factors are squares, and halvable over the twist iff both are non-squares."""
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
    """The CORRECTED Stage-0 acceptance test (CORR-20260904-b9f9c1): Z=3 is
    checked by the caller (roots already required to have length 3); this
    function checks h_+>=1 AND h_->=1 AND max(h_+,h_-)>=2, i.e. everything
    the prior filter required PLUS excluding exactly (h_+,h_-)=(1,1)."""
    return hp >= H_PLUS_MIN and hm >= H_MINUS_MIN and max(hp, hm) >= H_MAX_MIN


# ================================================================== STAGE 0
def stage_0():
    log("\n--- STAGE 0: search for a Z=3, h_+>=%d AND h_->=%d AND "
        "max(h_+,h_-)>=%d curve (CORRECTED filter) ---"
        % (H_PLUS_MIN, H_MINUS_MIN, H_MAX_MIN))
    log("declared search order: primes ascending in [%d, %d]; within a prime "
        "A ascending 0..p-1 then B ascending 0..p-1; first hit taken."
        % (PRIME_LO, PRIME_HI))
    s0 = {
        "declared_range": {"prime_lo": PRIME_LO, "prime_hi": PRIME_HI,
                           "order": "prime asc, then A asc, then B asc",
                           "h_plus_min": H_PLUS_MIN,
                           "h_minus_min": H_MINUS_MIN,
                           "h_max_min": H_MAX_MIN,
                           "filter_note": (
                               "CORRECTED per CORR-20260904-b9f9c1: excludes "
                               "exactly (h_+,h_-)=(1,1), the unique point "
                               "where D_sum=D_prod, proven necessary and "
                               "sufficient by two independent reviewers."),
                           "max_stratum_for_stage_1": MAX_STRATUM},
        "filter_audit": {"n_audited": 0, "disagreements": []},
        "primes_visited": [],
    }
    n_examined = 0          # (A,B) pairs looked at at all
    n_nonsingular = 0
    n_z3 = 0
    n_z3_hp1_hm1 = 0        # Z=3 AND h_+>=1 AND h_->=1 (prior filter), counted
                             # for disclosure only, never used to accept/reject
    audited = 0

    for p in primes_in(PRIME_LO, PRIME_HI):
        chi = chi_table(p)
        d = nonresidue(p, chi)
        s0["primes_visited"].append(p)
        for A in range(p):
            for B in range(p):
                n_examined += 1
                if (4 * pow(A, 3, p) + 27 * B * B) % p == 0:
                    continue                       # singular
                n_nonsingular += 1
                roots = cubic_roots(A, B, p)
                if len(roots) != 3:
                    continue                       # need Z = 3
                n_z3 += 1
                N = RC.curve_order(p, A, B)
                if (p + 1 - N) % p == 0:
                    continue                       # supersingular: skip
                hp, hm = h_pair_from_characters(roots, chi, p)
                if hp >= H_PLUS_MIN and hm >= H_MINUS_MIN:
                    n_z3_hp1_hm1 += 1

                if audited < FILTER_AUDIT_N:
                    audited += 1
                    Ad, Bd = twist_params(A, B, d, p)
                    e4 = count_4_torsion_bruteforce(p, A, B)
                    e4d = count_4_torsion_bruteforce(p, Ad, Bd)
                    bp, bm = (e4 - 4) // 4, (e4d - 4) // 4
                    if (bp, bm) != (hp, hm) or (e4 - 4) % 4 or (e4d - 4) % 4:
                        s0["filter_audit"]["disagreements"].append(
                            {"p": p, "A": A, "B": B, "fast": [hp, hm],
                             "bruteforce": [bp, bm],
                             "E4": e4, "Ed4": e4d})

                if not qualifies(hp, hm):
                    continue

                # ---- candidate: verify everything by direct construction ----
                Ad, Bd = twist_params(A, B, d, p)
                e4 = count_4_torsion_bruteforce(p, A, B)
                e4d = count_4_torsion_bruteforce(p, Ad, Bd)
                Nd = RC.curve_order(p, Ad, Bd)
                Z = len(roots)
                tau = Z + 1
                n_plus = sum(1 for x in range(p)
                             if chi[(x * x * x + A * x + B) % p] == 1)
                n_minus = sum(1 for x in range(p)
                              if chi[(x * x * x + A * x + B) % p] == -1)
                h_plus = (e4 - tau) // 4
                h_minus = (e4d - tau) // 4
                if not qualifies(h_plus, h_minus):
                    # brute-force disagreed with the fast filter enough to
                    # drop below the corrected threshold; do not accept,
                    # keep scanning.
                    continue
                stratum = C3(n_plus + n_minus)

                found = {
                    "p": p, "A": A, "B": B, "d_nonresidue": d,
                    "twist_A": Ad, "twist_B": Bd,
                    "j_invariant": RC.j_invariant(p, A, B),
                    "f_roots": roots, "Z": Z, "tau": tau,
                    "order_E": N, "trace_t": p + 1 - N,
                    "order_Ed_counted": Nd,
                    "order_Ed_formula_2p_plus_2_minus_NE": 2 * p + 2 - N,
                    "E4_bruteforce": e4, "Ed4_bruteforce": e4d,
                    "n_plus": n_plus, "n_minus": n_minus,
                    "h_plus": h_plus, "h_minus": h_minus,
                    "h_plus_h_minus_fast_criterion": [hp, hm],
                    "stratum_size_C3": stratum,
                    "curves_examined_before_success": n_examined,
                    "nonsingular_examined": n_nonsingular,
                    "z3_curves_examined": n_z3,
                    "z3_curves_with_prior_filter_h_plus_ge1_h_minus_ge1":
                        n_z3_hp1_hm1,
                }
                # ---- self-consistency checks on the found object ----
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
                # (D1) involution lemma, checked directly on this curve:
                # mu_T is an involution of P^1 and its F_p-fixed points exist
                # iff chi(f'(x_T)) = +1.
                ck["D1_involution_and_fixed_points"] = _check_D1(
                    p, A, B, roots, chi)

                s0["filter_audit"]["n_audited"] = audited
                s0["found_curve"] = found
                s0["outcome"] = "qualifying_curve_found"
                log("  FOUND: p=%d A=%d B=%d  Z=%d tau=%d  #E=%d #E^d=%d"
                    % (p, A, B, Z, tau, N, Nd))
                log("         #E[4]=%d #E^d[4]=%d -> h_+=%d h_-=%d"
                    % (e4, e4d, h_plus, h_minus))
                log("         n_+=%d n_-=%d  stratum C(%d,3)=%d"
                    % (n_plus, n_minus, n_plus + n_minus, stratum))
                log("         curves examined (A,B pairs): %d" % n_examined)
                log("  checks: %s" % json.dumps(ck))
                return s0

        if time.time() - T0 > STAGE0_WALL_BREAK_S:
            s0["stage0_wall_break_hit"] = True
            s0["last_prime_fully_scanned"] = p
            break

    s0["filter_audit"]["n_audited"] = audited
    if s0.get("stage0_wall_break_hit"):
        s0["outcome"] = "budget_exhausted_partial_range_search"
    else:
        s0["outcome"] = "range_exhausted_no_qualifying_curve"
    s0["curves_examined"] = n_examined
    s0["z3_curves_with_prior_filter_h_plus_ge1_h_minus_ge1_total"] = n_z3_hp1_hm1
    return s0


def _check_D1(p, A, B, roots, chi):
    """(D1): mu_T(x) = x_T + f'(x_T)/(x - x_T) is an involution of P^1, and its
    fixed points are the x-coordinates of the four Q with 2Q = T, rational iff
    chi(f'(x_T)) = +1, all carrying one common value of chi(f(.)): +1 iff
    T in 2E(F_p), -1 iff T in 2E^d(F_p). Verified by direct computation."""
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
        # fixed points solve (x - xT)^2 = f'(xT)
        fixed = [x for x in range(p) if (x - xT) * (x - xT) % p == fp % p]
        chis = sorted({chi[(x ** 3 + A * x + B) % p] for x in fixed})
        # halving check: does some Q in E(F_p) have 2Q = T?
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
    """NEW pre-Stage-1 sanity check (M6, CORR-20260904-b9f9c1 / handoff
    TASK-20260904-e063c0). Compute D_sum and D_prod from the found curve's
    own (n_+, n_-, h_+, h_-) and explicitly verify D_sum != D_prod, using the
    proven identity
        D_prod - D_sum = h_-*(h_+-1)*n_+ + h_+*(h_--1)*n_-
    which is zero iff h_+=h_-=1. Both the direct computation and the
    identity's own right-hand side are computed and cross-checked against
    each other, so a bug in either would show up as a self-inconsistency,
    not merely as a numeric coincidence.

    Returns a dict with `passed` (bool) and full diagnostic detail. If
    `passed` is False, the caller MUST stop before Stage 1/2."""
    log("\n--- M6: pre-Stage-1 sanity check (D_sum != D_prod?) ---")
    n_p, n_m = found["n_plus"], found["n_minus"]
    h_p, h_m = found["h_plus"], found["h_minus"]

    D_sum = h_p * n_m + h_m * n_p
    D_prod = h_p * h_m * (n_p + n_m)
    diff_direct = D_prod - D_sum
    # the proven identity's own right-hand side, computed independently of
    # the direct subtraction above
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
    """Exhaustive census of the distinct-split stratum, using EXP-MONO-0e6e8f's
    own classifier and EXP-MONO-815525's own Q_e construction, unmodified.
    Logic identical to EXP-MONO-98abb2's own stage_1(), including its own
    already-fixed resultant cross-check. Only reached if M6 passed."""
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
    # Cross-check the fast symmetric-base Q_e path (RC.qe_from_sym) against
    # RC's own INDEPENDENT runtime-resultant path (RC.qe_from_resultant), on
    # a sampled subset of base points. Reused unmodified from the prior
    # script's own already-fixed final version of this check.
    xcheck = {"n": 0, "mismatch": 0, "non_rational": 0, "mismatches": []}

    for t1, t2, t3 in combinations(S, 3):
        e1 = (t1 + t2 + t3) % p
        e2 = (t1 * t2 + t1 * t3 + t2 * t3) % p
        e3 = (t1 * t2 * t3) % p
        n_points += 1
        g = [(-e3) % p, e2 % p, (-e1) % p, 1]
        if UC.resultant(g, f, p) == 0:
            n_res_zero += 1          # cannot happen on this stratum; counted
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
            "Reused unmodified from EXP-MONO-98abb2's own already-fixed "
            "final stage_1(), which itself carried it forward from "
            "EXP-MONO-4e6faa/EXP-MONO-ee06e2; no dead-cross-check issue "
            "exists here to re-fix."),
    }


# ================================================================== STAGE 2
def stage_2(found, m6, s1):
    """Exact comparison: observed vs. D_sum (frozen D3) vs. D_prod (named
    multiplicative rival), reusing the predictions already computed in M6
    (pure functions of `found` alone, computed BEFORE Stage 1 ran). Only
    reached if M6 passed. Zero tolerance throughout."""
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
            "EXP-MONO-98abb2): D_prod = h_+ * h_- * (n_+ + n_-)"),
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
    out_path = os.path.join(
        REPO, "experiments", "EXP-MONO-8ec0e5", "runs",
        "RUN-MONO-8ec0e5-1", "raw-result.json")
    report = {
        "experiment_id": "EXP-MONO-8ec0e5",
        "run_id": "RUN-MONO-8ec0e5-1",
        "hypothesis_id": "H-MONO-dd666a",
        "seed": SEED,
        "randomness_sources": [
            "NONE. This run is fully deterministic: the Stage-0 search order "
            "and the Stage-1 stratum enumeration are both fixed integer "
            "orders. The specification seed 20260904007 is recorded but no "
            "random number generator is instantiated."],
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

    s0 = stage_0()
    report["stage_0"] = s0
    if s0["outcome"] == "range_exhausted_no_qualifying_curve":
        # The FULL declared range [PRIME_LO, PRIME_HI] was scanned to
        # completion without finding a qualifying curve. Reportable,
        # non-evidentiary occupancy finding per HEUR-CELL-4 / specification
        # outcomes.no_qualifying_curve_found.
        report["disposition"] = "completed_valid"
        report["outcome"] = "no_qualifying_curve_found"
        report["certificate"] = {
            "kind": "none",
            "note": "Pure measurement run; no solve or relation claimed."}
        _finish(report, out_path)
        return 0
    if s0["outcome"] == "budget_exhausted_partial_range_search":
        # The declared range [PRIME_LO, PRIME_HI] was NOT fully scanned:
        # Stage 0's internal wall-clock safety break (STAGE0_WALL_BREAK_S,
        # itself inside the specification's own 900 s total budget) was hit
        # first. This is DISTINCT from "declared range exhausted" and is
        # classified resource_exhaustion, not a negative or confirming
        # observation of any kind (AGENTS.md rule 3 / agents/executor.md
        # failure semantics). No qualifying curve was found in the PORTION
        # of the range actually searched; nothing is claimed about the
        # unsearched portion [last_prime_fully_scanned+1, PRIME_HI].
        report["disposition"] = "resource_exhaustion"
        report["failure_classification"] = "resource_exhaustion"
        report["outcome"] = (
            "BUDGET_EXHAUSTED_BEFORE_FULL_RANGE_SEARCHED: Stage 0's search "
            "reached its internal wall-clock safety break "
            "(STAGE0_WALL_BREAK_S=%.0fs, inside the specification's 900s "
            "total budget) after examining %d (A,B) pairs across primes up "
            "to and including %d, out of the full declared range [%d, %d], "
            "without finding a curve satisfying Z=3 AND h_+>=1 AND h_->=1 "
            "AND max(h_+,h_-)>=2. This is a resource_exhaustion outcome, "
            "NOT a declared-range exhaustion and NOT evidence for or "
            "against H-MONO-dd666a either way."
            % (STAGE0_WALL_BREAK_S, s0["curves_examined"],
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
        # STOP IMMEDIATELY per task card and specification stopping_rules:
        # do not run Stage 1 or Stage 2. This is a specification_error, not
        # a valid research outcome -- the corrected filter is PROVEN to
        # exclude this case, so its occurrence indicates a bug in the
        # identity's implementation or in the Stage-0 filter itself.
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
                         "executed_with_corrected_filter; "
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
