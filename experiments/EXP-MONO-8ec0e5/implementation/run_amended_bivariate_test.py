"""
EXP-MONO-8ec0e5 v2 -- AMENDED re-test (protocol_amendment v1_to_v2, see
experiments/EXP-MONO-8ec0e5/amendments/v1_to_v2.yaml, authoritative for this
run). RUN-MONO-8ec0e5-1 (version 1, `run_corrected_bivariate_test.py`)
resource-exhausted at 863.6s having searched only 91 of the 278 declared
primes, because `cubic_roots(A,B,p)` performs an O(p) scan of range(p) for
EVERY non-singular (A,B) pair, purely to determine Z (the number of
F_p-rational roots of f). This script changes ONLY that: how Z=3
("f splits completely") is determined for each (A,B) pair. Nothing else --
not the declared search order, not the declared range, not the qualifying
filter, not M6, not Stage 1, not Stage 2 -- is altered. See
implementation.md for the full disclosure and the SR-A1 equivalence-gate
result.

FAST SPLITTING TEST (amendment `definitions_frozen.fast_splits_completely_
test`, change A1): f(X) = X^3 + A X + B splits completely into 3 distinct
F_p-rational roots iff X^p == X (mod f(X)), computed via O(log p)
repeated-squaring polynomial exponentiation in the ring F_p[X]/(f(X)),
represented as coefficient triples (c0, c1, c2) meaning c0 + c1 X + c2 X^2,
reducing X^3 -> -A X - B (mod f) and hence X^4 -> -A X^2 - B X. Since the
caller only reaches this test after the existing non-singularity check
(4A^3 + 27B^2 != 0 mod p), which already rules out repeated roots for a
short-Weierstrass cubic, this single congruence check is sufficient -- no
separate squarefree/gcd(f,f') check is needed (amendment's own frozen
definition, and the task card's own instruction, state this explicitly).

MANDATORY, BLOCKING SR-A1 EQUIVALENCE GATE (amendment change A2): before
Stage 0 is allowed to use the fast test for the real search, it is
exhaustively cross-checked against the EXISTING, unmodified,
already-trusted `cubic_roots`-based Z-determination
(`len(cubic_roots(A,B,p)) == 3` iff fast test says "splits completely") on
EVERY non-singular (A,B) pair for ALL primes in [101, 199]. Any
disagreement is a STOP: `specification_error`, no real search is run.

ADAPTED, STRUCTURE OTHERWISE UNCHANGED, from
    experiments/EXP-MONO-8ec0e5/implementation/run_corrected_bivariate_test.py
(the version 1 script; read in full before writing this file). `qualifies`,
`h_pair_from_characters`, `count_4_torsion_bruteforce`, `_is4`,
`twist_params`, `chi_table`, `nonresidue`, `C3`, `primes_in`, `_check_D1`,
`_all_points`, `m6_sanity_check`, `stage_1`, `stage_2` are carried over
UNMODIFIED (byte-identical logic) from that script. `cubic_roots` itself is
also carried over unmodified -- it is still called, just far less often
(only as the SR-A1 equivalence-gate's own comparison oracle, and then again
in the real search only for the fraction of non-singular pairs the fast
test accepts, to obtain the actual root VALUES needed downstream).

NO NEW Q_e(T) CONSTRUCTION AND NO NEW CLASSIFIER IS WRITTEN HERE. Imports,
BY FILE PATH and read-only, the same two prior artifacts as version 1:

    experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py   as UC
        -> UC.classify_fibre, UC.resultant, UC.CLASSES
    experiments/EXP-MONO-815525/implementation/run_census.py          as RC
        -> RC.compile_sym / RC.qe_from_sym, RC.qe_from_resultant / compile_s3,
           RC.pt_add / RC.curve_order / RC.j_invariant / F_p[X] toolkit

Neither prior file is modified or copied. Both are bound by sha256 in the
output record.

FROZEN DEFINITIONS -- taken verbatim from IDEA-20260904-4f614a, notation
block and (D3), identical to version 1:

    f(X) = X^3 + A X + B ;   chi = quadratic character of F_p, chi(0) = 0
    Z    = #{x in F_p : f(x) = 0} in {0,1,3}
    tau  = #E(F_p)[2] = Z + 1
    n_+  = #{x in F_p : chi(f(x)) = +1}          <-- over ALL of F_p
    n_-  = #{x in F_p : chi(f(x)) = -1}
    h_+  = (#E(F_p)[4]   - tau) / 4
    h_-  = (#E^d(F_p)[4] - tau) / 4
    D_sum  := h_+ * n_-  +  h_- * n_+                      (D3, frozen)
    D_prod := h_+ * h_- * (n_+ + n_-)                       (named rival)

STAGE -1  (NEW) SR-A1 equivalence gate: fast test vs cubic_roots, all
          non-singular (A,B) pairs, all primes in [101,199]. BLOCKING.
STAGE 0   search for a curve with Z=3 AND h_+>=1 AND h_->=1 AND
          max(h_+,h_-)>=2 (UNCHANGED filter/range/order), using the fast
          test as PRIMARY, falling back to cubic_roots only when it accepts.
M6        pre-Stage-1 sanity check (unchanged logic from version 1).
STAGE 1   exhaustive distinct-split census (unchanged logic from version 1).
STAGE 2   compare Stage 1's observed counts against BOTH D_sum's and
          D_prod's predictions (unchanged logic from version 1).

Budget (specification.yaml / amendment, UNCHANGED): 900 s wall, 900 s CPU,
128 MiB RSS, 1 worker, no network.
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

SEED = 20260904007              # specification.yaml replication.seeds[0], unchanged
BUDGET_WALL_S = 900.0
BUDGET_RSS_BYTES = 134217728

# ---------------------------------------------------------------------------
# STAGE-0 SEARCH ORDER, DECLARED, UNCHANGED FROM version 1 / specification.yaml.
PRIME_LO, PRIME_HI = 101, 2000
H_PLUS_MIN = 1
H_MINUS_MIN = 1
H_MAX_MIN = 2   # max(h_+, h_-) >= 2, excluding exactly (h_+,h_-)=(1,1)
MAX_STRATUM = 1200000
FILTER_AUDIT_N = 250

# SR-A1 equivalence-gate range (amendment change A2, parameters_frozen):
# ALL non-singular (A,B) pairs, ALL primes in [101, 199].
EQUIV_GATE_PRIME_LO, EQUIV_GATE_PRIME_HI = 101, 199

# Internal wall-clock safety break for Stage 0 (leaves room, within the
# specification's own unchanged 900 s total budget, for the SR-A1 gate that
# runs first, plus Stage 1/2 if a curve is found, plus I/O). This is a pure
# engineering knob on how much of the ALREADY-APPROVED 900 s budget Stage 0
# may consume; it does not touch the declared range, order, or filter.
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
    """UNMODIFIED from version 1 (run_corrected_bivariate_test.py). O(p) scan
    of range(p). Still used: (a) as the SR-A1 equivalence gate's own
    comparison oracle, and (b) in the real search, ONLY for the fraction of
    non-singular pairs the fast test accepts, to obtain the actual root
    VALUES needed downstream (n_+/n_-/h_+/h_- and Q_e(T))."""
    return [x for x in range(p) if (x * x * x + A * x + B) % p == 0]


# --------------------------------------------------------- FAST SPLITTING TEST
def _poly_mul_mod_f(c, d, A, B, p):
    """Multiply two elements c=(c0,c1,c2), d=(d0,d1,d2) of F_p[X]/(f(X)),
    f(X) = X^3 + A X + B, i.e. reducing via X^3 = -A X - B (mod f), hence
    X^4 = X * X^3 = -A X^2 - B X (mod f). Ordinary degree-<3 polynomial
    multiplication followed by this reduction, all mod p."""
    c0, c1, c2 = c
    d0, d1, d2 = d
    e0 = c0 * d0
    e1 = c0 * d1 + c1 * d0
    e2 = c0 * d2 + c1 * d1 + c2 * d0
    e3 = c1 * d2 + c2 * d1
    e4 = c2 * d2
    # substitute e3*X^3 = e3*(-A X - B), e4*X^4 = e4*(-A X^2 - B X)
    r0 = (e0 - e3 * B) % p
    r1 = (e1 - e3 * A - e4 * B) % p
    r2 = (e2 - e4 * A) % p
    return (r0, r1, r2)


def _x_pow_p_mod_f(A, B, p):
    """Compute X^p mod f(X) in F_p[X]/(f(X)) by repeated squaring
    (square-and-multiply) on the binary representation of p. Returns the
    coefficient triple (c0,c1,c2)."""
    result = (1, 0, 0)   # the identity element "1"
    base = (0, 1, 0)     # the element "X"
    e = p
    while e > 0:
        if e & 1:
            result = _poly_mul_mod_f(result, base, A, B, p)
        e >>= 1
        if e:
            base = _poly_mul_mod_f(base, base, A, B, p)
    return result


def fast_splits_completely(A, B, p):
    """f(X) = X^3 + A X + B splits completely over F_p into 3 distinct
    F_p-rational roots iff X^p == X (mod f(X)), i.e. X^p mod f(X) equals the
    coefficient triple (0,1,0) exactly. Non-singularity (checked by the
    caller before this test runs) already rules out repeated roots for a
    short-Weierstrass cubic, so this single congruence check suffices --
    per the amendment's own frozen definition."""
    return _x_pow_p_mod_f(A, B, p) == (0, 1, 0)


def nonresidue(p, chi):
    for d in range(2, p):
        if chi[d] == -1:
            return d
    raise RuntimeError("no non-residue mod %d" % p)


def count_4_torsion_bruteforce(p, A, B):
    """UNMODIFIED from version 1. #{P in E(F_p) : 4P = O}, by literal
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
    """UNMODIFIED from version 1. h_+ and h_- from the classical 2-descent
    criterion, used ONLY as a fast search filter and cross-checked against
    brute force."""
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
    """UNMODIFIED from version 1 (the CORRECTED Stage-0 acceptance test,
    CORR-20260904-b9f9c1): Z=3 is checked by the caller separately; this
    function checks h_+>=1 AND h_->=1 AND max(h_+,h_-)>=2."""
    return hp >= H_PLUS_MIN and hm >= H_MINUS_MIN and max(hp, hm) >= H_MAX_MIN


# ============================================================ STAGE -1 (SR-A1)
def sr_a1_equivalence_gate():
    """MANDATORY, BLOCKING (amendment change A2). Exhaustively cross-checks
    `fast_splits_completely(A,B,p)` against `len(cubic_roots(A,B,p))==3` on
    EVERY non-singular (A,B) pair, for ALL primes in [101,199]. Returns a
    dict with `passed` (bool), `n_pairs_checked`, and (if any) the exact
    counterexamples. Does NOT proceed to the real search if it fails."""
    log("\n--- STAGE -1 (SR-A1): MANDATORY equivalence gate, fast test vs "
        "cubic_roots, primes in [%d,%d], all non-singular (A,B) pairs ---"
        % (EQUIV_GATE_PRIME_LO, EQUIV_GATE_PRIME_HI))
    t_start = time.time()
    n_checked = 0
    n_nonsingular = 0
    n_agree_split = 0       # both say "splits completely"
    n_agree_not_split = 0   # both say "does not split completely"
    disagreements = []
    primes_checked = []

    for p in primes_in(EQUIV_GATE_PRIME_LO, EQUIV_GATE_PRIME_HI):
        primes_checked.append(p)
        for A in range(p):
            for B in range(p):
                if (4 * pow(A, 3, p) + 27 * B * B) % p == 0:
                    continue                       # singular, excluded
                n_nonsingular += 1
                n_checked += 1
                fast = fast_splits_completely(A, B, p)
                slow = (len(cubic_roots(A, B, p)) == 3)
                if fast == slow:
                    if fast:
                        n_agree_split += 1
                    else:
                        n_agree_not_split += 1
                else:
                    disagreements.append(
                        {"p": p, "A": A, "B": B, "fast_says_splits": fast,
                         "cubic_roots_says_splits": slow})
                    if len(disagreements) >= 50:
                        # cap the disclosed list; n_checked/pass-fail below
                        # still reflect the FULL exhaustive scan, not just
                        # the disclosed sample of counterexamples.
                        pass

    wall = time.time() - t_start
    passed = (len(disagreements) == 0)
    out = {
        "primes_checked": primes_checked,
        "n_primes_checked": len(primes_checked),
        "declared_range": [EQUIV_GATE_PRIME_LO, EQUIV_GATE_PRIME_HI],
        "n_nonsingular_pairs_checked": n_nonsingular,
        "n_pairs_checked": n_checked,
        "n_agree_splits_completely": n_agree_split,
        "n_agree_does_not_split": n_agree_not_split,
        "n_disagreements": len(disagreements),
        "disagreements": disagreements,
        "passed": passed,
        "wall_seconds": round(wall, 3),
        "note": (
            "EXHAUSTIVE over every non-singular (A,B) pair for every prime "
            "in the declared gate range -- not a sample. PASS means the "
            "fast O(log p) splitting test agreed with the existing, "
            "unmodified O(p) cubic_roots-based Z-determination on every "
            "single one of these pairs."),
    }
    log("  primes checked: %d   non-singular pairs checked: %d"
        % (len(primes_checked), n_nonsingular))
    log("  agree(splits): %d   agree(not split): %d   disagreements: %d"
        % (n_agree_split, n_agree_not_split, len(disagreements)))
    log("  SR-A1 gate wall time: %.3fs" % wall)
    log("  SR-A1 gate %s" % ("PASSED" if passed else "FAILED"))
    return out


# ================================================================== STAGE 0
def stage_0():
    log("\n--- STAGE 0: search for a Z=3, h_+>=%d AND h_->=%d AND "
        "max(h_+,h_-)>=%d curve (UNCHANGED filter), using the FAST "
        "splitting test as the PRIMARY Z-determination method ---"
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
                               "UNCHANGED from version 1 / "
                               "CORR-20260904-b9f9c1: excludes exactly "
                               "(h_+,h_-)=(1,1). Only the Z-determination "
                               "method changed (amendment v1_to_v2, "
                               "change A1)."),
                           "max_stratum_for_stage_1": MAX_STRATUM},
        "filter_audit": {"n_audited": 0, "disagreements": []},
        "primes_visited": [],
    }
    n_examined = 0          # (A,B) pairs looked at at all
    n_nonsingular = 0
    n_fast_says_split = 0   # fast test said "splits completely"
    n_z3 = 0                # confirmed Z=3 (fast test accepted, cubic_roots agreed)
    n_z3_hp1_hm1 = 0        # Z=3 AND h_+>=1 AND h_->=1 (prior filter), disclosure only
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

                # ---- PRIMARY Z-determination: fast splitting test, O(log p) ----
                if not fast_splits_completely(A, B, p):
                    continue                       # need Z = 3 (splits completely)
                n_fast_says_split += 1

                # ---- fallback: cubic_roots(A,B,p), UNMODIFIED, only when the
                # fast test accepted, to obtain the actual root VALUES ----
                roots = cubic_roots(A, B, p)
                if len(roots) != 3:
                    # Would contradict the SR-A1 gate's own exhaustive result
                    # on [101,199]; outside that range this is a live
                    # correctness check, not assumed. Recorded, not silently
                    # skipped.
                    s0["filter_audit"]["disagreements"].append(
                        {"p": p, "A": A, "B": B,
                         "context": "real_search_fast_vs_cubic_roots",
                         "fast_says_splits": True,
                         "cubic_roots_root_count": len(roots)})
                    continue
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
                             "E4": e4, "Ed4": e4d,
                             "context": "h_pair_filter_audit"})

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
                    "fast_test_said_split_count": n_fast_says_split,
                    "z3_curves_examined": n_z3,
                    "z3_curves_with_prior_filter_h_plus_ge1_h_minus_ge1":
                        n_z3_hp1_hm1,
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
    s0["nonsingular_examined_total"] = n_nonsingular
    s0["fast_test_said_split_total"] = n_fast_says_split
    s0["z3_curves_with_prior_filter_h_plus_ge1_h_minus_ge1_total"] = n_z3_hp1_hm1
    return s0


def _check_D1(p, A, B, roots, chi):
    """UNMODIFIED from version 1. (D1): mu_T(x) = x_T + f'(x_T)/(x - x_T) is
    an involution of P^1, and its fixed points are the x-coordinates of the
    four Q with 2Q = T, rational iff chi(f'(x_T)) = +1."""
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
    """UNMODIFIED from version 1. Computes D_sum and D_prod from the found
    curve's own (n_+, n_-, h_+, h_-) and explicitly verifies D_sum != D_prod,
    using the proven identity
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
    """UNMODIFIED from version 1. Exhaustive census of the distinct-split
    stratum, using EXP-MONO-0e6e8f's own classifier and EXP-MONO-815525's
    own Q_e construction, unmodified. Only reached if M6 passed."""
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
            "Reused unmodified from EXP-MONO-98abb2's own already-fixed "
            "final stage_1(), which itself carried it forward from "
            "EXP-MONO-4e6faa/EXP-MONO-ee06e2; no dead-cross-check issue "
            "exists here to re-fix."),
    }


# ================================================================== STAGE 2
def stage_2(found, m6, s1):
    """UNMODIFIED from version 1. Exact comparison: observed vs. D_sum
    (frozen D3) vs. D_prod (named multiplicative rival), reusing the
    predictions already computed in M6. Only reached if M6 passed. Zero
    tolerance throughout."""
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
            "EXP-MONO-98abb2 / version 1): D_prod = h_+ * h_- * (n_+ + n_-)"),
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
        "RUN-MONO-8ec0e5-2", "raw-result.json")
    report = {
        "experiment_id": "EXP-MONO-8ec0e5",
        "run_id": "RUN-MONO-8ec0e5-2",
        "hypothesis_id": "H-MONO-dd666a",
        "amendment": "v1_to_v2",
        "seed": SEED,
        "randomness_sources": [
            "NONE. This run is fully deterministic: the SR-A1 gate order, "
            "the Stage-0 search order, and the Stage-1 stratum enumeration "
            "are all fixed integer orders. The specification seed "
            "20260904007 is recorded but no random number generator is "
            "instantiated."],
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

    # ---- STAGE -1: MANDATORY, BLOCKING SR-A1 equivalence gate ----
    gate = sr_a1_equivalence_gate()
    report["sr_a1_equivalence_gate"] = gate
    if not gate["passed"]:
        report["disposition"] = "invalid_measurement"
        report["failure_classification"] = "specification_error"
        report["outcome"] = (
            "SR_A1_EQUIVALENCE_GATE_FAILED: the fast splitting test "
            "disagreed with the existing, unmodified cubic_roots-based "
            "Z-determination on %d of %d non-singular (A,B) pairs checked "
            "across primes in [%d,%d]. Per the amendment's own "
            "frozen_decision_rule.if_sr_a1_gate_fails, the real search is "
            "NOT run. See sr_a1_equivalence_gate.disagreements for the "
            "exact counterexample(s)."
            % (gate["n_disagreements"], gate["n_pairs_checked"],
               EQUIV_GATE_PRIME_LO, EQUIV_GATE_PRIME_HI))
        report["certificate"] = {
            "kind": "none",
            "note": "Run halted at the SR-A1 gate; no search performed, "
                     "nothing to certify."}
        _finish(report, out_path)
        return 0

    # ---- STAGE 0: the real search, gate passed ----
    s0 = stage_0()
    report["stage_0"] = s0
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
            "BUDGET_EXHAUSTED_BEFORE_FULL_RANGE_SEARCHED: Stage 0's search "
            "(using the fast splitting test, verified equivalent by the "
            "SR-A1 gate above) reached its internal wall-clock safety "
            "break (STAGE0_WALL_BREAK_S=%.0fs, inside the specification's "
            "900s total budget) after examining %d (A,B) pairs across "
            "primes up to and including %d, out of the full declared range "
            "[%d, %d], without finding a curve satisfying Z=3 AND h_+>=1 "
            "AND h_->=1 AND max(h_+,h_-)>=2. This is a resource_exhaustion "
            "outcome, NOT a declared-range exhaustion and NOT evidence for "
            "or against H-MONO-dd666a either way."
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
                         "executed_with_fast_splitting_test; "
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
