"""
EXP-MONO-ee06e2 -- linear-vs-quadratic discrimination of IDEA-20260904-4f614a's
exact closed form's D-term, on a curve with h_- >= 2 (genuinely beyond the
h_-=1 minimal value EXP-MONO-4e6faa tested, which could not discriminate a
linear D-term dependence on h_- from any rival f(h_-) agreeing at h_-=1).

ADAPTED, STRUCTURE UNCHANGED, from
    experiments/EXP-MONO-4e6faa/implementation/run_h_minus_stress.py
(read in full before writing this file). The only changes from that script
are:
  (1) Stage 0's qualifying filter: h_- >= 2 instead of h_- > 0. The search
      order itself (primes ascending in [101,2000], then A ascending, then
      B ascending, first hit taken) is UNCHANGED and is not biased toward
      any previously-named (A,B) pair.
  (2) Stage 2 additionally computes a named quadratic rival prediction,
      D_quad = h_+ * n_- + (h_-)**2 * n_+, alongside the frozen linear D3
      formula D_lin = h_+ * n_- + h_- * n_+, and reports all four residuals
      (R1_lin, R2_lin, R1_quad, R2_quad) against Stage 1's own exhaustive
      census, exactly, before either prediction is read against the other.

NO NEW Q_e(T) CONSTRUCTION AND NO NEW CLASSIFIER IS WRITTEN HERE. This script
imports, BY FILE PATH and read-only, exactly the same two prior artifacts
EXP-MONO-4e6faa's own script used:

    experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py   as UC
        -> UC.classify_fibre   the already-verified five-class label
        -> UC.resultant        the already-verified Res(g,f) guard
        -> UC.CLASSES          the five-class list
    experiments/EXP-MONO-815525/implementation/run_census.py          as RC
        (pulled in transitively by UC)
        -> RC.compile_sym / RC.qe_from_sym     symmetric-base Q_e(T)
        -> RC.qe_from_resultant / compile_s3   independent Q_e(T) path
        -> RC.pt_add / RC.curve_order / RC.factor_pattern / F_p[X] toolkit

Neither prior file is modified or copied. Both are bound by sha256 in the
output record.

FROZEN DEFINITIONS -- taken verbatim from IDEA-20260904-4f614a, notation block
and (D3):

    f(X) = X^3 + A X + B ;   chi = quadratic character of F_p, chi(0) = 0
    Z    = #{x in F_p : f(x) = 0} in {0,1,3}
    tau  = #E(F_p)[2] = Z + 1
    n_+  = #{x in F_p : chi(f(x)) = +1}          <-- over ALL of F_p
    n_-  = #{x in F_p : chi(f(x)) = -1}
    h_+  = (#E(F_p)[4]   - tau) / 4
    h_-  = (#E^d(F_p)[4] - tau) / 4
    D_lin  := h_+ * n_-  +  h_- * n_+                      (D3, frozen)
    #1^4    = C(n_+,3) + C(n_-,3) + D_lin
    #2+1+1  = 3 n_+ n_-  -  3 D_lin
    #2+2    = C(n_+ + n_-,3) - C(n_+,3) - C(n_-,3) - 3 n_+ n_- + 2 D_lin

The named quadratic rival, from H-MONO-fa4cb9's own mechanism field:
    D_quad := h_+ * n_-  +  (h_-)**2 * n_+
with the SAME #1^4 / #2+1+1 / #2+2 combinatorial identities as (D3), but with
D_lin replaced by D_quad.

The stratum is (D3)'s own: the C(n_+ + n_-, 3) monic cubics g(X) = X^3 - e1 X^2
+ e2 X - e3 that split into three DISTINCT F_p-rational roots, NONE of them a
root of f. It is enumerated as unordered triples of distinct elements of
S := F_p \\ Z(f), which is exactly that set and has size n_+ + n_- = p - Z.

STAGE 0  search for a curve with Z = 3 AND h_- >= 2 (CHANGED from h_- > 0).
STAGE 1  exhaustive distinct-split census on the found curve (unchanged logic).
STAGE 2  BEFORE reading Stage 1's output, compute D_lin and D_quad and both
         predictions; then compare against Stage 1's observed counts and
         report all four residuals R1_lin, R2_lin, R1_quad, R2_quad exactly.

Budget (specification.yaml): 900 s wall, 900 s CPU, 128 MiB RSS, 1 worker,
no network.

NOTE ON THE DEAD CROSS-CHECK FIX: EXP-MONO-4e6faa's own FINAL archived script
(the one this file is adapted from) already fixed a dead `xcheck` block that
existed in an earlier, interrupted draft of that script. That fix is
REUSED HERE UNMODIFIED (the resultant cross-check in stage_1 below is the
already-corrected version). No secondary fix is needed or attempted in this
file.
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

SEED = 20260904005              # specification.yaml replication.seeds[0]
BUDGET_WALL_S = 900.0
BUDGET_RSS_BYTES = 134217728

# ---------------------------------------------------------------------------
# STAGE-0 SEARCH ORDER, DECLARED HERE BEFORE ANY STAGE-1 / STAGE-2 RESULT.
# Deterministic, no randomness: primes ascending in [PRIME_LO, PRIME_HI], and
# within each prime A ascending 0..p-1, then B ascending 0..p-1. The FIRST
# curve satisfying (non-singular, ordinary, Z = 3, h_- >= 2) is taken --
# CHANGED from EXP-MONO-4e6faa's own h_- > 0 filter. Curves examined are
# counted exactly. The declared range is the specification's own [101, 2000].
PRIME_LO, PRIME_HI = 101, 2000
H_MINUS_MIN = 2   # <-- the one Stage-0 filter change from EXP-MONO-4e6faa
# Hard cap on the Stage-1 stratum so the exhaustive census fits the 900 s
# budget. Declared before the search. C(n_+ + n_-, 3) must not exceed this;
# a qualifying curve over the cap would be reported as a budget-blocked find,
# never silently skipped.
MAX_STRATUM = 1200000
# Number of Z=3 curves on which the fast character-based h_+/h_- criterion is
# cross-checked against brute-force 4-torsion point counting before it is
# trusted as a search filter.
FILTER_AUDIT_N = 250

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


# ================================================================== STAGE 0
def stage_0():
    log("\n--- STAGE 0: search for a Z=3, h_->=%d curve ---" % H_MINUS_MIN)
    log("declared search order: primes ascending in [%d, %d]; within a prime "
        "A ascending 0..p-1 then B ascending 0..p-1; first hit taken."
        % (PRIME_LO, PRIME_HI))
    s0 = {
        "declared_range": {"prime_lo": PRIME_LO, "prime_hi": PRIME_HI,
                           "order": "prime asc, then A asc, then B asc",
                           "h_minus_min": H_MINUS_MIN,
                           "max_stratum_for_stage_1": MAX_STRATUM},
        "filter_audit": {"n_audited": 0, "disagreements": []},
        "primes_visited": [],
    }
    n_examined = 0          # (A,B) pairs looked at at all
    n_nonsingular = 0
    n_z3 = 0
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

                if hm < H_MINUS_MIN:
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
                if h_minus < H_MINUS_MIN:
                    # brute-force disagreed with the fast filter enough to
                    # drop below threshold; do not accept, keep scanning.
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
                ck["h_minus_at_least_threshold"] = (h_minus >= H_MINUS_MIN)
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

        if time.time() - T0 > 300:
            break

    s0["filter_audit"]["n_audited"] = audited
    s0["outcome"] = "range_exhausted_no_qualifying_curve"
    s0["curves_examined"] = n_examined
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


# ================================================================== STAGE 1
def stage_1(found):
    """Exhaustive census of the distinct-split stratum, using EXP-MONO-0e6e8f's
    own classifier and EXP-MONO-815525's own Q_e construction, unmodified.
    Logic identical to EXP-MONO-4e6faa's own stage_1(), including its own
    already-fixed resultant cross-check."""
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
    # a sampled subset of base points. Reused unmodified from EXP-MONO-4e6faa's
    # own already-fixed final version of this check (see that experiment's
    # implementation.md for the full derivation of why this wiring is a
    # genuine independent elimination path on this stratum, not a tautology).
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
            "Reused unmodified from EXP-MONO-4e6faa's own already-fixed "
            "final stage_1(); no dead-cross-check issue exists here to "
            "re-fix. See run_h_minus_stress.py's provenance / "
            "implementation.md for the original fix and its rationale."),
    }


# ================================================================== STAGE 2
def stage_2(found, s1):
    """Exact three-way comparison: observed vs. D_lin (frozen D3) vs. D_quad
    (named quadratic rival). Computed BEFORE reading s1's own counts in the
    sense that both predictions are pure functions of `found` alone -- s1 is
    passed in only to read off the already-computed `observed` counts for
    the final residual subtraction, never to select or adjust a prediction.
    Zero tolerance throughout."""
    log("\n--- STAGE 2: exact three-way comparison (linear vs. quadratic) ---")
    n_p, n_m = found["n_plus"], found["n_minus"]
    h_p, h_m = found["h_plus"], found["h_minus"]

    # D_lin: the frozen, unmodified D3 formula (IDEA-20260904-4f614a).
    D_lin = h_p * n_m + h_m * n_p
    # D_quad: the named quadratic rival (H-MONO-fa4cb9's own mechanism field).
    D_quad = h_p * n_m + (h_m ** 2) * n_p

    def predicted(D):
        return {
            "1^4": C3(n_p) + C3(n_m) + D,
            "2+1+1": 3 * n_p * n_m - 3 * D,
            "2+2": C3(n_p + n_m) - C3(n_p) - C3(n_m) - 3 * n_p * n_m + 2 * D,
        }

    predicted_lin = predicted(D_lin)
    predicted_quad = predicted(D_quad)

    obs = s1["counts"]
    R1_lin = obs["1^4"] - predicted_lin["1^4"]
    R2_lin = obs["2+1+1"] - predicted_lin["2+1+1"]
    R3_lin = obs["2+2"] - predicted_lin["2+2"]
    R1_quad = obs["1^4"] - predicted_quad["1^4"]
    R2_quad = obs["2+1+1"] - predicted_quad["2+1+1"]
    R3_quad = obs["2+2"] - predicted_quad["2+2"]

    out = {
        "frozen_prediction_source": "IDEA-20260904-4f614a (D3), unmodified",
        "rival_prediction_source": (
            "H-MONO-fa4cb9's own mechanism field: D_quad = h_+*n_- + "
            "(h_-)**2 * n_+"),
        "n_plus": n_p, "n_minus": n_m, "h_plus": h_p, "h_minus": h_m,
        "D_lin": D_lin,
        "D_lin_terms": {"h_plus*n_minus": h_p * n_m,
                        "h_minus*n_plus": h_m * n_p},
        "D_quad": D_quad,
        "D_quad_terms": {"h_plus*n_minus": h_p * n_m,
                         "h_minus_squared*n_plus": (h_m ** 2) * n_p},
        "predicted_lin": predicted_lin,
        "predicted_quad": predicted_quad,
        "observed": obs,
        "R1_lin_1^4": R1_lin,
        "R2_lin_2+1+1": R2_lin,
        "R3_lin_2+2_bonus": R3_lin,
        "R1_quad_1^4": R1_quad,
        "R2_quad_2+1+1": R2_quad,
        "R3_quad_2+2_bonus": R3_quad,
        "R1_lin_is_zero": R1_lin == 0,
        "R2_lin_is_zero": R2_lin == 0,
        "R1_quad_is_zero": R1_quad == 0,
        "R2_quad_is_zero": R2_quad == 0,
        "class_4_count": obs["4"], "class_3+1_count": obs["3+1"],
        "closed_form_implies_4_and_3+1_are_zero_on_this_stratum": True,
    }
    log("  D_lin  = h_+*n_- + h_-*n_+       = %d*%d + %d*%d       = %d"
        % (h_p, n_m, h_m, n_p, D_lin))
    log("  D_quad = h_+*n_- + (h_-)^2*n_+   = %d*%d + %d*%d      = %d"
        % (h_p, n_m, h_m ** 2, n_p, D_quad))
    for k in ("1^4", "2+1+1", "2+2"):
        log("  %-7s observed %d   lin-pred %d (resid %d)   "
            "quad-pred %d (resid %d)"
            % (k, obs[k], predicted_lin[k], obs[k] - predicted_lin[k],
               predicted_quad[k], obs[k] - predicted_quad[k]))
    log("  R1_lin=%d R2_lin=%d   R1_quad=%d R2_quad=%d"
        % (R1_lin, R2_lin, R1_quad, R2_quad))
    return out


# ====================================================================== MAIN
def main():
    out_path = os.path.join(
        REPO, "experiments", "EXP-MONO-ee06e2", "runs",
        "RUN-MONO-ee06e2-1", "raw-result.json")
    report = {
        "experiment_id": "EXP-MONO-ee06e2",
        "run_id": "RUN-MONO-ee06e2-1",
        "hypothesis_id": "H-MONO-fa4cb9",
        "seed": SEED,
        "randomness_sources": [
            "NONE. This run is fully deterministic: the Stage-0 search order "
            "and the Stage-1 stratum enumeration are both fixed integer "
            "orders. The specification seed 20260904005 is recorded but no "
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
    if s0["outcome"] != "qualifying_curve_found":
        report["disposition"] = "completed_valid"
        report["outcome"] = "no_qualifying_curve_found"
        _finish(report, out_path)
        return 0

    found = s0["found_curve"]
    if not found["checks"]["stratum_within_budget_cap"]:
        report["disposition"] = "completed_valid"
        report["outcome"] = "qualifying_curve_found_but_stratum_over_budget"
        _finish(report, out_path)
        return 0

    s1 = stage_1(found)
    report["stage_1"] = s1
    report["stage_2"] = stage_2(found, s1)
    report["certificate"] = {
        "kind": "none",
        "note": ("Pure measurement run. No discrete-log solve and no "
                 "factor-base relation is claimed. The construction is "
                 "EXP-MONO-0e6e8f's own already-independently-verified one, "
                 "reused unmodified and bound by sha256 above.")}
    report["disposition"] = "completed_valid"
    report["outcome"] = ("linear_vs_quadratic_comparison_executed; "
                         "R1_lin=%d R2_lin=%d R1_quad=%d R2_quad=%d"
                         % (report["stage_2"]["R1_lin_1^4"],
                            report["stage_2"]["R2_lin_2+1+1"],
                            report["stage_2"]["R1_quad_1^4"],
                            report["stage_2"]["R2_quad_2+1+1"]))
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
