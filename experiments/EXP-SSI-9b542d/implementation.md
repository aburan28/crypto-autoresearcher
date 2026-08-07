# Implementation Notes: EXP-SSI-9b542d

## Overview

`crossover.py` implements the Wesolowski crossover locus `p*(w)` experiment as
specified in `specification.yaml`. It is a zero-compute cost-model experiment
that applies the corrected vOW time-memory formula (MC_P13_CORRECTED) to
committed numbers from the paper and prior validated measurements.

## Architecture

Single-file Python 3 script using only standard library modules:
`math, json, os, sys, time, hashlib, statistics, platform, importlib, re, ast`

### Execution Flow

1. **Step 0 — Environment**: Records Python version, platform, module availability
   (find_spec for forbidden modules), and asserts no forbidden import.

2. **Step 1 — Input Loading**: Reads and verifies T1 (cost_measurements.json,
   8 rows), T2 (paper_fulltext.md lines 234-238, parsed with regex), and
   cross-checks against PAPER_PAIRS/OVERHEAD_C from cost_model.py (read as text
   via ast.literal_eval, NOT imported). SHA-256 hashes of all input files recorded.

3. **Step 2 — Fit Parameters**: Computes per-entry law coefficients (a1..a4)
   from T1 data and verifies against frozen reference values.

4. **Step 3 — BOUNDARY-CONDITION-GATE (Fix 3)**:
   - BCG-2 FIRST (negative control): Evaluates superseded formula at w=M,
     verifies residual = 0.5*L_mem(P) at all 5 committed P rows × 4 laws.
   - BCG-1: Evaluates corrected formula at w=M, verifies residual < 1e-9.
   - Gate blocks all subsequent computation on failure.

5. **Step 4 — REPRODUCTION GATE (RG-1..RG-5)**: Recovers EV-SSI-59f7a2's
   committed bracket at P=256, unbounded memory.

6. **Step 5 — XCHK-1**: Independent expression path cross-check (direct
   summation of literals vs general evaluator).

7. **Step 6 — Monotonicity (MONO-1..5)**: Slope checks, kink location, data
   properties, convention difference.

8. **Step 7 — Main Grid**: 4480 cells (4 laws × 2 S × 4 A × 5 c × 2 MC × 14 w).
   Each cell performs a 513-point bracket scan on P ∈ [256, 768] followed by
   bisection of sign changes.

9. **Step 8 — Null Object**: Same code path with N0 (E=0) and N1 (E=9.8).
   Computes margin-surface displacements.

10. **Step 9 — Sensitivity**: L5 extrapolation, log2_k_DG sweep, adversarial
    corner, SANITY-1 model coherence audit.

11. **Step 10-13 — Scope, Convention Signs, Bands, Tail Checks**.

12. **Step 14 — XCHK-2**: Optional numpy cross-check (records NOT_RUN if absent).

13. **Step 15 — L5 grid**: 1120 sensitivity cells.

### Key Design Decisions

- **MC_P13_CORRECTED formula**: `T_A(P,w) = T_full(P) + 0.5*max(0, L_mem(P) - log2_w)`.
  The square root of a memory RATIO (M/w), not of raw count w.
  Satisfies T_A(P, M) = T_full(P) exactly by construction.

- **Interpolation**: T2 columns use piecewise-linear interpolation between
  committed rows. No extrapolation outside [256, 768].

- **Same code path for nulls**: The `solve_crossover` function is called with
  the same interface for main laws, null laws, and L5.

- **Deterministic**: No randomness. Seed 0 recorded for form only.

## Protocol Deviations

None. All requirements in the specification followed as written.

## Known Limitations (carried, not introduced)

- T1 fit window [9, 40] extrapolated 6.4x-19.2x to [256, 768] — stamped on every cell.
- Per-entry costs based on primes_used ∈ {[2,3], [2,3,5]}, not operating ℓ at NIST scale.
- MONO-3 FAIL is a finding about the model: p*(w) is non-monotone because
  L_mem(P) itself grows with P, creating a feedback between the locus and
  its penalty term. This is not a code defect.
