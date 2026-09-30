#!/usr/bin/env python3
"""Verification script for EXP-CANL-96b0ad amendment v2 (auxiliary-tuple
collision-free redesign [change B1, discharging CORR-20260810-308774] and the
corrected maximal-order lambda formula for Finding A [change B2, discharging
part of CORR-20260810-685434]).

NOT YET EXECUTED IN THIS SESSION. Written and filed by a Coordinator subagent
drafting session with NO Bash / code-execution tool available (see
AGENTS.md rule 9 and this file's own header note in v2.yaml change B0):
every number in this file's own docstring or in v2.yaml that is labelled
"hand-derived" below was computed by manual arithmetic during drafting,
shown with full working so a reader can check it independently, NOT by
running this script. This script exists so a session WITH Bash access (the
top-level Coordinator, or an Executor under a dispatched TASK-*) can run it
and capture v2-verification-output.txt before this amendment is relied upon
for approval or execution -- exactly the artifact this task's own
instructions ask for, disclosed as pending rather than fabricated per
AGENTS.md rule 5 ("never fabricate ... outputs"). NOTHING in this file
imports harness/exp_canl.py or harness/run_canl.py; every formula below is
reimplemented standalone from the frozen contract text and from this
amendment's own derivations, so running it is an INDEPENDENT check of the
harness code, not a restatement of it (mirroring
experiments/EXP-ICINV-4d33aa/amendments/v3-verification.py's own discipline).

This script does four things:

1.  PART 1 -- the mixed-radix (Sidon-separation) auxiliary-tuple
    construction (change B1). For every (C0, s) pair this contract's grid
    actually uses (Z-baseline arm: s = r_Z+1 in {3,5}; C1 O-arm / C2
    CM-shell arm: s = r_Z//2+1 in {2,3}, r_Z in {2,4}, C0 in
    {1,2,3,5,8}), constructs tuple A (base b_A = 2*C0+1) and tuple B (base
    b_B = 2*C0+2), verifies the separation condition
    w_i > 2*C0*sum(w_1..w_{i-1}) holds for every i (exact integer
    arithmetic), and verifies -- by an exact bounded DP over achievable
    integer sums, the SAME technique z_baseline_cell already uses for its
    own closed_form_count, reimplemented here independently -- that BOTH
    tuples achieve exactly (2*C0+1)**s distinct achievable INTEGER sums
    (i.e. are genuinely collision-free / injective, not merely
    separation-condition-compliant by assumption). Also reproduces CORR's
    own worked example's structure with the OLD weights (k=(2,1) vs (3,1))
    to confirm they do NOT achieve the naive bound (the defect this
    amendment fixes), for direct contrast.

2.  PART 2 -- for every ladder prime this contract's main ladder uses
    (101, 1009, 10007, 100003, 1000003 -- copied verbatim from
    experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/prime-verification.json,
    not re-derived), classifies every (C0, s) grid cell as
    "no_wraparound_guaranteed" ((2*C0+1)**s <= N, so the PROVABLE
    cross-tuple-agreement guarantee from Part 1 applies) or "wraparound"
    (pigeonhole guarantees mod-N collisions; no provable guarantee from this
    construction alone -- change B1's own text explains why the dual-tuple
    hard gate is downgraded to a reported comparison in this regime).

3.  PART 3 -- the corrected maximal-order lambda formula (change B2).
    Re-derives, from lambda(pi)=1 and pi's TRUE expression pi = A + f_pi*w0
    (A = (t - f_pi*D0)/2, w0 = (D0+sqrt(D0))/2 the MAXIMAL order's own basis
    element), the formula lambda(w0) = (1-A)*inverse(f_pi) mod N, and
    evaluates it at the four ALREADY-REALIZED C2-congruence curves (p, t,
    D0=-3, f_pi=f_E) copied verbatim from
    experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/c2-measurements.json
    "curves", not re-measured. Compares against (a) the currently-reported
    realized-suborder lambda value (unaffected by this amendment, computed
    the OLD way, for contrast) and (b) the NAIVE, INCORRECT substitution
    of f=1 directly into the EXISTING harness/exp_canl.py:lambda_of_w
    formula -- demonstrating concretely why that naive substitution
    (implicitly suggested as "cheap" by both the Validator and Red Team
    reports, coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-CANL-96b0ad/{validation_report.md,redteam_report.md})
    gives a DIFFERENT, WRONG answer, because it silently assumes f_pi=1
    (i.e. pi=(t+sqrt(D0))/2), which is false for these curves (f_pi in
    {8,48,14,2} respectively) -- f_pi is a fixed fact about how Frobenius
    itself embeds relative to sqrt(D0) for THIS curve, not a free parameter
    that can be swapped to 1 without changing which curve is being
    described.

4.  PART 4 -- non-vacuousness / sanity: confirms the corrected lambda(w0)
    values are nonzero mod N (matching HEUR-CANL-S1's own requirement that
    non-unit shell elements give a genuinely non-tautological reduced
    coefficient), for all four curves.
"""
import math
from fractions import Fraction


# ---------------------------------------------------------------------------
# PART 1: mixed-radix auxiliary-tuple construction
# ---------------------------------------------------------------------------

def mixed_radix_tuple(C0: int, s: int, base: int) -> list[int]:
    """s weights: target (last slot) = 1 = base**0, s-1 auxiliary slots
    (first s-1 slots, per the frozen rule's own "first s-1 slots are
    auxiliary, final slot is the target" shape) = base**1 .. base**(s-1).
    Matches harness/run_canl.py:aux_tuple's own return shape
    ([k_1..k_{s-1}, 1]) with the k_i values replaced."""
    aux = [base ** i for i in range(1, s)]
    return aux + [1]


def check_separation_condition(weights: list[int], C0: int) -> list[tuple[int, bool]]:
    """w_i > 2*C0*sum(w_1..w_{i-1}) for the weights in ASCENDING order
    (the target's weight 1 is smallest, so ascending order = reverse of the
    tuple's own [aux..., target] storage order)."""
    ordered = sorted(weights)
    results = []
    running_sum = 0
    for w in ordered:
        ok = w > 2 * C0 * running_sum
        results.append((w, ok))
        running_sum += w
    return results


def achievable_integer_sums_count(weights: list[int], C0: int) -> int:
    """Exact count of distinct integer sums sum_i w_i*c_i, c_i in [-C0,C0],
    via a bounded DP (same technique as harness/run_canl.py:z_baseline_cell's
    own achievable-sum computation, reimplemented independently here rather
    than imported)."""
    achievable = {0}
    for w in weights:
        vals = {w * c for c in range(-C0, C0 + 1)}
        achievable = {r + v for r in achievable for v in vals}
    return len(achievable)


def part1(C0_grid=(1, 2, 3, 5, 8), s_values=(2, 3, 5)):
    print("=== PART 1: mixed-radix weight construction, separation + injectivity ===")
    all_ok = True
    for C0 in C0_grid:
        for s in s_values:
            naive_bound = (2 * C0 + 1) ** s
            for label, base in (("A", 2 * C0 + 1), ("B", 2 * C0 + 2)):
                w = mixed_radix_tuple(C0, s, base)
                sep = check_separation_condition(w, C0)
                sep_ok = all(ok for _, ok in sep)
                achieved = achievable_integer_sums_count(w, C0)
                inj_ok = (achieved == naive_bound)
                all_ok = all_ok and sep_ok and inj_ok
                print(f"C0={C0:>2} s={s} tuple {label} (base={base:>3}) weights={w}  "
                      f"separation_ok={sep_ok!s:>5}  "
                      f"achievable_sums={achieved:>8} naive_bound={naive_bound:>8} "
                      f"injective={inj_ok!s:>5}")
    print(f"PART 1 all_ok = {all_ok}")

    print()
    print("--- contrast: OLD weights (frozen v1 rule, k_i=i+1 / k_i=slots+i), "
          "CORR-20260810-308774's own worked example, reproduced fresh ---")
    C0, box = 1, list(range(-1, 2))
    for label, w in (("A (k=(1,2))", [1, 2]), ("B (k=(1,3))", [1, 3])):
        sums = {c1 * w[0] + c2 * w[1] for c1 in box for c2 in box}
        print(f"  old tuple {label}: achievable sums = {sorted(sums)} "
              f"(count={len(sums)}, naive_bound=9)")
    return all_ok


# ---------------------------------------------------------------------------
# PART 2: wraparound classification against the actual main-ladder primes
# ---------------------------------------------------------------------------

# Copied verbatim from
# experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/prime-verification.json
# "main_ladder_primes" -- not re-derived, not re-verified for primality by
# this script (sympy.isprime already ran in that run and is not re-run
# here).
MAIN_LADDER_PRIMES = [101, 1009, 10007, 100003, 1000003]


def part2(C0_grid=(1, 2, 3, 5, 8), s_values=(2, 3, 5)):
    print()
    print("=== PART 2: no-wraparound classification against the real ladder ===")
    print(f"{'C0':>3} {'s':>2} {'naive_bound':>12}   " +
          "  ".join(f"N={p:>7}" for p in MAIN_LADDER_PRIMES))
    for C0 in C0_grid:
        for s in s_values:
            nb = (2 * C0 + 1) ** s
            flags = ["no_wrap" if nb <= N else "WRAP" for N in MAIN_LADDER_PRIMES]
            print(f"{C0:>3} {s:>2} {nb:>12}   " + "  ".join(f"{f:>8}" for f in flags))


# ---------------------------------------------------------------------------
# PART 3: corrected maximal-order lambda(w0) formula (Finding A / change B2)
# ---------------------------------------------------------------------------

def lambda_of_w_OLD_UNMODIFIED(D_E: int, t: int, f: int, N: int) -> int:
    """harness/exp_canl.py:lambda_of_w, copied verbatim (not imported), for
    side-by-side comparison. UNCHANGED by this amendment; this is the
    formula the EXISTING code applies to the realized (possibly
    non-maximal) suborder."""
    if N % 2 == 0:
        raise ValueError("requires odd N")
    if math.gcd(f, N) != 1:
        raise ValueError(f"requires gcd(f={f}, N={N}) == 1")
    inv2 = pow(2, -1, N)
    return (D_E + 2 - t) % N * inv2 % N


def lambda_of_w0_maximal_order(D0: int, t: int, f_pi: int, N: int) -> int:
    """NEW formula (change B2), derived in v2.yaml change B2's own text:
    pi = A + f_pi*w0 where w0 = (D0+sqrt(D0))/2 is the MAXIMAL order's own
    basis element and A = (t - f_pi*D0)/2 (an integer -- pi is an algebraic
    integer expressed in O_K's own Z-basis {1,w0}). lambda(pi)=1 (fixed
    convention, unchanged) gives A + f_pi*lambda(w0) = 1 mod N, i.e.
    lambda(w0) = (1-A)*inverse(f_pi) mod N. Requires gcd(f_pi, N)=1 (the
    SAME precondition the old formula already required, now stated in terms
    of f_pi specifically since f_pi and the order's OWN conductor f_O=1 are
    no longer assumed equal)."""
    if N % 2 == 0:
        raise ValueError("requires odd N")
    if math.gcd(f_pi, N) != 1:
        raise ValueError(f"requires gcd(f_pi={f_pi}, N={N}) == 1")
    A_num = t - f_pi * D0
    if A_num % 2 != 0:
        raise ValueError(f"(t - f_pi*D0) = {A_num} is not even; pi is not "
                          f"integral in the assumed basis -- STOP, do not "
                          f"silently round (AGENTS.md rule 5)")
    A = A_num // 2
    inv_fpi = pow(f_pi, -1, N)
    return (1 - A) % N * inv_fpi % N


# Copied verbatim from
# experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/c2-measurements.json
# "curves" -- not re-measured, not re-derived; D0=-3 for all four (j=0
# congruence ladder). f_pi here is exactly what that file reports as
# "f_E" (Z[pi]'s own conductor, computed by
# harness/isogeny_class.py:frobenius_discriminant + fundamental_discriminant,
# UNCHANGED by this amendment).
C2_CURVES = {
    1009:    {"t": 62,   "D_E_realized": -192,  "f_pi": 8},
    10009:   {"t": 182,  "D_E_realized": -6912, "f_pi": 48},
    100003:  {"t": 632,  "D_E_realized": -588,  "f_pi": 14},
    1000003: {"t": 2000, "D_E_realized": -12,   "f_pi": 2},
}
D0 = -3


def part3():
    print()
    print("=== PART 3: corrected maximal-order lambda(w0) vs. the realized-suborder "
          "value vs. the NAIVE (incorrect) f=1 substitution ===")
    print(f"{'p':>8} {'t':>6} {'f_pi':>5}   {'lambda(w_realized)':>20}   "
          f"{'lambda(w0)_CORRECTED':>22}   {'lambda(w0)_NAIVE_f=1':>22}   agree(corrected,naive)")
    for p, c in C2_CURVES.items():
        t, D_E_r, f_pi = c["t"], c["D_E_realized"], c["f_pi"]
        lam_realized = lambda_of_w_OLD_UNMODIFIED(D_E_r, t, f_pi, p)
        lam_corrected = lambda_of_w0_maximal_order(D0, t, f_pi, p)
        # the naive, INCORRECT substitution both prior reviews suggested as
        # "cheap": call the OLD formula with D_E:=D0, f:=1 directly.
        lam_naive = lambda_of_w_OLD_UNMODIFIED(D0, t, 1, p)
        agree = (lam_corrected == lam_naive)
        print(f"{p:>8} {t:>6} {f_pi:>5}   {lam_realized:>20} "
              f"  {lam_corrected:>22}   {lam_naive:>22}   {agree}")
    print("(agree=False at any row demonstrates the naive f=1 substitution is "
          "mathematically WRONG -- it silently assumes pi=(t+sqrt(D0))/2, "
          "false whenever f_pi != 1, i.e. at every one of these four curves.)")


# ---------------------------------------------------------------------------
# PART 4: nonzero-ness sanity (HEUR-CANL-S1's own non-tautology requirement)
# ---------------------------------------------------------------------------

def part4():
    print()
    print("=== PART 4: corrected lambda(w0) is nonzero mod N at every realized curve ===")
    all_nonzero = True
    for p, c in C2_CURVES.items():
        lam = lambda_of_w0_maximal_order(D0, c["t"], c["f_pi"], p)
        nz = (lam % p != 0)
        all_nonzero = all_nonzero and nz
        print(f"  p={p}: lambda(w0)={lam}  nonzero={nz}")
    print(f"PART 4 all_nonzero = {all_nonzero}")


if __name__ == "__main__":
    part1()
    part2()
    part3()
    part4()
