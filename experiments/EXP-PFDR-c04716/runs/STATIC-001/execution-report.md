# Execution report — EXP-PFDR-c04716 / runs/STATIC-001 (zero-run static derivation)

Handoff: TASK-20260903-c7166d. Hypothesis: H-PFDR-06fd60. Source derivation:
IDEA-20260903-dcf857. Approving decision: DEC-20260903-93862f.

**ZERO-RUN STATEMENT.** Zero runs occurred. No curve was generated or sampled,
no solver was written or invoked, no Macaulay matrix was built, no seed exists.
`STATIC-001` is a zero-run package directory, not a run: it carries no
`manifest.yaml` and no run record. The only code in the package is the
derivation aid `cost_table.py` (exact integer binomials, both omega, the
real-valued balance solver), which imports only `argparse, json, math, os, sys`
and `math.comb/factorial/log2` from the standard library. **Certificate kind:
none; no run occurred.** Every number below is DERIVED (estimate), never
measured, and every bounded-slice / table number is CONDITIONAL on HEUR-001 of
H-PFDR-06fd60 ("assuming HEUR-001"); no cell is quoted below without its
(D_0, omega) tags. This report records observations and arithmetic
comparisons against the frozen preregistered prediction. It draws no
conclusion about any hypothesis, heuristic, experiment, question or goal.

## Contract check (before writing anything)

- `experiments/EXP-PFDR-c04716/specification.yaml`: `status: approved`,
  `approved_by: coordinator`, `approved_at: 2026-09-03`, approval note citing
  DEC-20260903-93862f — confirmed by reading the committed file.
- Required inputs, controls (7), metrics, preregistered prediction, budget
  (`maximum_runs: 0`, 600 s floor, 8 GB, 0.5 CPU-h), stopping rules,
  invalidation rules, required artifacts (7): all present. No
  `specification_error`.
- Repository state at execution: commit `c57429694af615f64d2e691a0df25e1b131f4875`,
  working tree clean (`git status --porcelain` empty) before this package was
  written. Read-only git only; see deviation D2.

## Stage 0 — derivation-aid script and its emitted tables

Command (from the repository root, cwd-independent; the script writes into
its own directory):

```
python3 experiments/EXP-PFDR-c04716/runs/STATIC-001/cost_table.py
```

Exit code 0; stderr empty; wall time 0.546 s as measured by the invoking
shell around the process (INFORMATIONAL ONLY — not evidence, not a run
timing; it documents that the 600 s floor of the contract was respected).
A second invocation with `--out` into the session scratchpad produced
byte-identical copies of all five emitted YAML files and identical stdout
(determinism check; the copies live outside the repository).

Environment: Linux 6.18.44-fc-v24 x86_64 (glibc 2.39); Python 3.11.15
(GCC 13.3.0); 4 cores; 15 GB RAM; no Sage; the script uses no third-party
package. PyYAML 6.0.1 was used by the executor only to strict-parse the five
emitted YAML files after the fact (all five parse); it is not imported by the
script.

Stdout of the script, verbatim:

```json
{
 "F1_null_slice_pass": true,
 "F2_direct_presentation_pass": true,
 "F3_balance_limits_pass": true,
 "small_N_tell_pass": true,
 "small_N_min_gap": {"m": 5, "D0": 4, "omega": 2.0, "log2_T_minus_rho": 9.11888845847054},
 "hand_primary_all_within_1": true,
 "hand_all_listed_within_1": false,
 "largest_discrepancy": {"log2N": 256, "m": 4, "D0": 6, "omega": 2.807,
   "log2_T": 151.5966170347727, "hand_T_log2": 150.0,
   "discrepancy_T_script_minus_hand": 1.5966170347726916,
   "hand_source": "dcf857 (D) ('about 2^150')"},
 "thresholds_256": [
  {"m": 3, "omega": 2.0,   "bracket": "below 2 (T >= rho already at D_0 = 2)", "predicted_bracket_256": null, "matches_prediction": null},
  {"m": 3, "omega": 2.807, "bracket": "below 2 (T >= rho already at D_0 = 2)", "predicted_bracket_256": null, "matches_prediction": null},
  {"m": 4, "omega": 2.0,   "bracket": "between 2 and 4", "predicted_bracket_256": "below 4", "matches_prediction": true},
  {"m": 4, "omega": 2.807, "bracket": "between 2 and 4", "predicted_bracket_256": null, "matches_prediction": null},
  {"m": 5, "omega": 2.0,   "bracket": "between 8 and 10", "predicted_bracket_256": "between 8 and 10", "matches_prediction": true},
  {"m": 5, "omega": 2.807, "bracket": "between 4 and 6", "predicted_bracket_256": "between 4 and 6", "matches_prediction": true}
 ],
 "bounded_slice_argmin_not_0_cells": [
  "(D_0 = 6, omega = 2.807) log2N=64 m=3",
  "(D_0 = 8, omega = 2.0) log2N=64 m=3",
  "(D_0 = 8, omega = 2.807) log2N=64 m=3",
  "(D_0 = 8, omega = 2.807) log2N=64 m=4"
 ],
 "cells_conditionally_below_rho": [
  "log2 N = 256, m = 5, D_0 = 4, omega = 2.0",
  "log2 N = 256, m = 5, D_0 = 4, omega = 2.807",
  "log2 N = 256, m = 5, D_0 = 6, omega = 2.0",
  "log2 N = 256, m = 5, D_0 = 8, omega = 2.0"
 ]
}
```

### Cost model as implemented (frozen in the contract's `inputs`)

- n = m s digit variables, B = 2^s; Ncols(n', D) = sum_{i <= D} binom(n', i).
- C(k) = 2^k Ncols(n - k, D(k))^omega, k = 0..n - s.
- Null slice D(k) = ceil(((n - k) + 2m)/2); bounded slice D(k) = min(D_0, d_reg(k)).
- Enumerative leaf k = n - s additionally charged the da1428 way: 2^{n-s} 2^{m-1}
  (root-finding, 2^{m-1} roots, O(1) lookup). Curves report the argmin under
  both leaf charges.
- Balance: s = (log2 m! + m + omega log2 Ncols(n, D(0)) + log2 N)/(m + 1) with
  n = round(m s), iterated to a self-consistent fixed point (every one of the
  54 table cells converged in 3-5 iterations with no rounding cycle);
  T = 2 B^2, i.e. log2 T = 1 + 2 s; memory log2 = s; 2^m filtering charged
  inside C(0). rho: log2 T = log2 0.886 + (log2 N)/2 = 31.83 / 63.83 / 127.83.

### F1 — null slice reproduces IDEA-20260808-da1428 (CTRL-NULL-SLICE-DA1428, blocking)

PASS at all six (m, s, omega) cells. At (3, 6), (4, 8), (5, 8) and both
omega, C(k) is strictly decreasing in k over the whole range 0..n - s; the
argmin is the enumerative leaf under both leaf charges (formula and
root-finding). Emitted log2 ratios C(k+1)/C(k): range [-1.0414, -0.9293]
at omega 2 (asymptote 1 - omega = -1) and [-1.8662, -1.7078] at omega 2.807
(asymptote -1.807). The null curves at all 54 balanced table cells are also
strictly decreasing with the argmin at the leaf. Assembled total with the
enumerative oracle C = B^{m-1} 2^{m-1}: log2 T = log2 N + log2 m! + 2m
exactly (slope d log2 T / d log2 N = 1.0), e.g. m = 5: 80.91 / 144.91 /
272.91 at log2 N = 64 / 128 / 256 (exponent 1: N^1). No interior optimum.
Stopping rule 1 (interior optimum) NOT triggered.

### F2 — direct presentation reproduces da1428's B^{2 omega - 1} ratio (CTRL-DIRECT-PRESENTATION-RATIO, blocking)

PASS for m in {3, 4, 5} and both omega. Model: k of m coordinates fixed to
factor-base values (B^k), residual r = m - k variables at degree
ceil((r (B - 1) + D_S)/2) with dense column count binom(D + r, r), leaf
k = m - 1 charged B^{m-1} 2^{m-1}; D_S = m 2^{m-1} (total degree of S_{m+1};
the ratio's B-exponent is independent of this choice — see D5). Over
B = 2^4..2^20 the argmin is k = m - 1 at every grid point from B = 16 on
(B_0 = 16 at all six (m, omega)), and the local slope
d log2(ratio_{k=m-2 / k=m-1}) / d log2 B at B = 2^20 is 3.0000 / 2.9999 /
2.9998 (m = 3/4/5) against the target 2 omega - 1 = 3 at omega 2, and
4.6139 / 4.6139 / 4.6137 against 4.614 at omega 2.807. The flip does NOT
occur in the direct presentation. Stopping rule 1 (direct fixture) NOT triggered.

### F3 — balance limits (CTRL-BALANCE-LIMITS, blocking)

PASS for m in {3, 4, 5}. C = 1: log2 T = 1 + (2/(m+1))(log2 m! + m + log2 N);
slope d log2 T / d log2 N = 0.5 / 0.4 / 0.3333 = 2/(m+1) exactly (84cdb7's
N^{2/(m+1)}); constant offsets 3.79 / 4.43 / 4.97 (84cdb7's own form without
the 2^m filter is also emitted). C = B^{m-1} 2^{m-1}: slope 1.0 exactly
(N^1); closed form and 200-step iteration agree to < 1e-6.

### Small-N tell (CTRL-SMALL-N-LOSES, blocking)

PASS: every one of the 18 bounded-slice cells at log2 N = 64 has
log2 T - log2 rho >= 9. Minimum gap 9.1189 at (m = 5, D_0 = 4, omega = 2)
[assuming HEUR-001]: log2 T = 40.94 vs rho 31.83. Next smallest: 15.39 at
(m = 4, D_0 = 4, omega = 2). Stopping rule 2 NOT triggered.

### Both-omega control (CTRL-BOTH-OMEGA)

Every table cell, curve, threshold row and concrete-cost parameter set is
emitted at omega = 2 and omega = 2.807; there is no single-omega number in
the package.

### The table (cost-table.yaml; all cells assuming HEUR-001; log2 values; estimate)

| log2 N | m | D_0 | omega | log2 T | log2 mem | rho | T - rho | hand T | script - hand | hand source |
|---|---|---|---|---|---|---|---|---|---|---|
| 256 | 5 | 4 | 2 | 108.76 | 53.88 | 127.83 | -19.06 | 108.7 | +0.06 | spec inputs |
| 256 | 5 | 4 | 2.807 | 116.60 | 57.80 | 127.83 | -11.23 | 116.6 | -0.00 | H (D) |
| 256 | 5 | 6 | 2 | 116.64 | 57.82 | 127.83 | -11.18 | 116.6 | +0.04 | spec inputs |
| 256 | 5 | 6 | 2.807 | 128.05 | 63.53 | 127.83 | +0.23 | 127.9 | +0.15 | spec inputs |
| 256 | 5 | 8 | 2 | 124.13 | 61.56 | 127.83 | -3.70 | 124.1 | +0.03 | spec inputs |
| 256 | 5 | 8 | 2.807 | 139.01 | 69.01 | 127.83 | +11.19 | 139.0 | +0.01 | H (D) |
| 256 | 4 | 4 | 2 | 128.74 | 63.87 | 127.83 | +0.91 | 128.6 | +0.14 | spec inputs |
| 256 | 4 | 4 | 2.807 | 138.04 | 68.52 | 127.83 | +10.22 | 138.0 | +0.04 | H (D) |
| 256 | 4 | 6 | 2 | 138.07 | 68.54 | 127.83 | +10.25 | 138.0 | +0.07 | dcf857 (D) |
| 256 | 4 | 6 | 2.807 | 151.60 | 75.30 | 127.83 | +23.77 | ~150 | **+1.60** | dcf857 (D) "about" |
| 256 | 4 | 8 | 2 | 146.93 | 72.97 | 127.83 | +19.11 | 146.8 | +0.13 | spec inputs |
| 256 | 4 | 8 | 2.807 | 164.59 | 81.79 | 127.83 | +36.76 | 164.4 | +0.19 | H (D) |
| 256 | 3 | 4..8 | both | 158.75 .. 202.74 | 78.9 .. 100.9 | 127.83 | +30.9 .. +74.9 | — | — | (m = 3 row: script constant log2(2 sqrt 48) = 3.79 vs hand "2^2.8") |
| 128 | 5 | 4 | 2 | 64.04 | 31.52 | 63.83 | +0.22 | 64.0 | +0.04 | spec inputs |
| 128 | 5 | 4 | 2.807 | 71.25 | 35.12 | 63.83 | +7.42 | 71.1 | +0.15 | H (D) |
| 128 | 5 | 8 | 2 | 77.79 | 38.39 | 63.83 | +13.96 | 77.7 | +0.09 | dcf857 (D) |
| 128 | 4 | 4 | 2 | 75.02 | 37.01 | 63.83 | +11.20 | 75.0 | +0.02 | dcf857 (D) |
| 64 | 5 | 4 | 2 | 40.94 | 19.97 | 31.83 | +9.12 | 40.9 | +0.04 | spec inputs |

All 54 cells (3 N x 3 m x 3 D_0 x 2 omega), with exact Ncols integers,
rounding sensitivity (n +/- 1 moves log2 T by at most +/-0.12), the C(k)
curve summary at the balanced s, and the interior-band fields, are in
`cost-table.yaml`. Memory discrepancies script - hand: all within
[-0.0004, +0.11] where a hand memory exists.

Hand-value comparison, stated exactly:
- The 8 cells listed in the contract's `inputs.hand_values_to_reproduce`
  (primary): all within 1 in log2; max |discrepancy| = 0.15 at
  (log2 N = 256, m = 5, D_0 = 6, omega = 2.807); memory 53.88 vs 53.8 at
  (256, m = 5, D_0 = 4, omega = 2).
- The additional values in H-PFDR-06fd60 statement (D): all within 1;
  max |discrepancy| = 0.19 at (256, m = 4, D_0 = 8, omega = 2.807).
- The additional values only in IDEA-20260903-dcf857 (D): all within 1 except
  (log2 N = 256, m = 4, D_0 = 6, omega = 2.807): script 151.60 vs hand
  "about 2^150", discrepancy +1.60 in log2. This exceeds 1 in log2. That
  value is not in the contract's `inputs` list nor in H-PFDR-06fd60 (D);
  it is reported as a discrepancy above 1 for that cell, and its standing
  under success-criterion item (3) is for the reviewer / Coordinator to
  decide. Tail check 1 (largest discrepancy, with its (m, D_0, omega, N)):
  (m = 4, D_0 = 6, omega = 2.807, log2 N = 256), +1.60.

### D_0 thresholds (thresholds.yaml; assuming HEUR-001; even D_0 grid 2..40)

At log2 N = 256 (tail check 2, bracketed to the nearest even value):

| m | omega | largest even D_0 with T < rho | smallest even D_0 with T >= rho | bracket | frozen prediction | comparison |
|---|---|---|---|---|---|---|
| 5 | 2 | 8 (124.1) | 10 (131.3) | between 8 and 10 | between 8 and 10 | matches |
| 5 | 2.807 | 4 (116.6) | 6 (128.1) | between 4 and 6 | between 4 and 6 | matches |
| 4 | 2 | 2 (118.6) | 4 (128.7) | between 2 and 4 | below 4 | matches (T >= rho at D_0 = 4) |
| 4 | 2.807 | 2 (123.5) | 4 (138.0) | between 2 and 4 | (none) | — |
| 3 | 2 | none | 2 (146.3) | below 2 | (none) | — |
| 3 | 2.807 | none | 2 (152.4) | below 2 | (none) | — |

At log2 N = 128: m = 5 both omega "between 2 and 4" (T = 56.5 / 60.2 at
D_0 = 2; 64.0 / 71.2 at D_0 = 4); every other (m, omega) "below 2". At
log2 N = 64: every (m, omega) "below 2". No prediction was frozen for 64 or
128 bits.

### C(k) curve structure under the bounded slice, against prediction P3

P3 (frozen): "k* = 0 with C increasing in k until n - k falls below
3.41 D_0 (omega 2) or 4.57 D_0 (omega 2.807)", stated for n = ms in the
hundreds.

Observed at the 54 balanced table cells (n from 84 to 345):
- k* = 0 (root-finding leaf charge) at 50 of 54 cells. At those cells C(k)
  is increasing over the entire guessing range: the first k with
  C(k+1)/C(k) < 1 is never reached because the residual count n - k stays at
  or above s, and s exceeds the predicted crossing D_0/(1 - 2^{-1/omega})
  (13.66 / 20.49 / 27.31 at omega 2; 18.28 / 27.42 / 36.56 at omega 2.807
  for D_0 = 4 / 6 / 8) everywhere except the one cell (64, m = 5, D_0 = 8,
  omega = 2.807), where the ratio first drops below 1 at k = 131, residual
  34 (prediction 36.56), and the argmin is still k = 0.
- k* != 0 at 4 cells, all at log2 N = 64: (m = 3, D_0 = 6, omega 2.807),
  (m = 3, D_0 = 8, omega 2), (m = 3, D_0 = 8, omega 2.807),
  (m = 4, D_0 = 8, omega 2.807). There the root-finding leaf
  2^{n-s} 2^{m-1} is below C(0): log2 leaf 82 / 76 / 94 / 117 vs
  log2 C(0) (without the 2^m factor) 89.38 / 77.60 / 116.10 / 119.28. The
  table's T for those cells is still the k = 0 value the frozen model
  specifies (80.38 / 74.48 / 93.96 / 77.92); the full-guessing balance
  (F1, N^1) at the same N gives 72.59 (m = 3) / 76.59 (m = 4). All four
  cells have T - rho >= +42.66 (m = 3) / +46.09 (m = 4) under either charge.
  Recorded as an observation against P3's "k* = 0" at these four cells; no
  interpretation.
- At the small fixture pairs (n = 18, 32, 40; outside P3's "hundreds"
  scope) the crossing is reached inside the range: residual variables at
  the first ratio drop are 11 / 18 / 25 (omega 2) and 16 / 25 / 32-34
  (omega 2.807) for D_0 = 4 / 6 / 8, i.e. 1 to 3 below the asymptotic
  formula, and the root-finding leaf is the argmin at 17 of 18 bounded
  fixture cells; k* = 0 only at (5, 8, D_0 = 4, omega 2).

### Interior band under HEUR-002 only, against prediction P5

P5 (frozen): cost 2^{k_c} binom(2(D_0 - m), D_0)^omega at
k_c = n - 2(D_0 - m). Observed:
- binom(2(D_0 - m), D_0) = 0 whenever D_0 < 2m: for m = 4 with D_0 in
  {4, 6} and for m = 5 with every D_0 in {4, 6, 8}; nonzero only for
  (m = 3, D_0 = 6): 1, (m = 3, D_0 = 8): 45, (m = 4, D_0 = 8): 1. The P5
  value is emitted as null where the binomial is zero.
- k_c lies OUTSIDE the guessing range (k_c > n - s) at all 54 table cells,
  because 2(D_0 - m) <= 10 < s at every cell; hence under HEUR-001,
  D(k) = D_0 for every k in 0..n - s at every table cell.
- At the fixture pairs k_c is in range only at (3, 6, D_0 = 6): k_c = 12,
  (3, 6, D_0 = 8): k_c = 8, (4, 8, D_0 = 8): k_c = 24; there the script's
  C(k_c) (with the full Ncols) exceeds the P5 value (top binomial only) by
  +12.0 / +9.0 / +16.0 (omega 2) and +16.8 / +12.6 / +22.5 (omega 2.807)
  in log2.
These are emitted numbers; the P5 formula as frozen is reported, not
repaired.

## Stage 1 — concrete_cost block (concrete-cost.yaml)

Filled per `templates/research-records.md`: `bound_kind: heuristic_estimate`,
`status: draft`, `id: null` (draft inside a package; no COST identifier
minted), `cost_unit: F_p field operations (log2)`, 54 parameter sets each
tagged with (D_0, omega) and the qualifier, time / memory / prior rho time
(0.886 sqrt N) / prior memory 0; 8 optimistic assumptions each flagged
[UNDER-estimates cost] (HEUR-001; bounded-solve half via a RECALLED
Huang-Kosters-Yeo pointer, not opened; omega = 2; KN-FIND-007 yield with 2^m
filtering (HEUR-003); B^2 linear algebra at unit constant; no charge for
matrix build, S_{m+1} construction (S_6 at m = 5, KN-OPEN-5b3a08 noted),
solution recognition or certificate checks; real-valued s with n = round(m s);
k* = 0 used for every cell); 2 overestimating factors; parallelism;
time-memory tradeoff (arity m as the only knob; no van Oorschot-Wiener style
interpolation to O(1) memory; the full-guessing endpoint at O(B) memory and
N^1 time); hidden-overhead disclosure (the o(1) as 2^m Ncols(ms, D_0)^omega,
per cell); affected scope (NONE unconditionally; conditionally on HEUR-001,
time only, the four cells (256, m = 5, D_0 = 4, omega 2) 108.76,
(256, m = 5, D_0 = 4, omega 2.807) 116.60, (256, m = 5, D_0 = 6, omega 2)
116.64, (256, m = 5, D_0 = 8, omega 2) 124.13, each with memory 2^53.9 to
2^61.6 against rho's O(1)); safe scope (all curves if HEUR-001 fails; the
other 50 cells listed with their T - rho; m = 3 by arithmetic; every cell on
memory); `dominated_by` and `sota_delta` restated (unconditionally +0 on every
axis; conditional deltas per cell, tagged). Machine-derived numbers only; the
prose flags were written into the script so that the block regenerates with
the numbers.

## Success-criterion checklist (1)-(5), outcomes only

1. Three fixtures pass (null slice = da1428 with full guessing and N^1;
   direct-presentation ratio; balance limits): **PASS, PASS, PASS** with the
   emitted numbers above.
2. Every bounded-slice cell at 64 bits loses to rho by at least 2^9:
   **PASS**; minimum gap 9.12 at (m = 5, D_0 = 4, omega 2).
3. Every table cell within 1 in log2 of the hand values, both omega, tagged:
   **PASS against the contract's listed hand values** (8 primary cells, max
   0.15) **and H-PFDR-06fd60 (D)** (max 0.19); **one dcf857-only approximate
   value exceeded by +1.60** at (256, m = 4, D_0 = 6, omega 2.807) — reported
   as a discrepancy above 1 for that cell; whether it falls under item (3) is
   not the executor's call. Per the contract, a discrepancy above 1 is a valid
   negative derivation result for the affected hand value, never an
   infrastructure failure.
4. D_0 thresholds per (m, omega) at 256 bits emitted and bracket the
   predicted ranges: **PASS** — (5, 2): 8-10; (5, 2.807): 4-6; (4, 2): T >= rho
   at D_0 = 4 ("below 4"; bracket 2-4).
5. concrete_cost block filled with every optimistic assumption flagged and
   affected-vs-safe scope: **PASS** (concrete-cost.yaml).

THIS IS DESIGN INTEGRITY AND PRICING ONLY: it validates no heuristic,
supplies no ECDLP evidence, and changes no status.

## Falsification outcomes

- F1 (null slice interior optimum): NOT observed at any of the 6 fixture
  cells or 54 table-cell null curves.
- F2 (direct-presentation fixture fails): NOT observed.
- F3 (a bounded-slice cell beats rho at 64 bits): NOT observed; minimum
  gap +9.12.
- F4, F5 belong to EXP-PFDR-cbdefb and are not touched here.
- No stopping rule was triggered; no curve, solver, Macaulay matrix or run
  was ever needed.

## Deviations from the contract / handoff (all recorded, none absorbed)

- D1. The launching prompt asked for a run package in the
  `docs/evidence-and-reproducibility.md` run layout (`manifest.yaml`,
  `command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
  `raw-result.json`, a `RUN-PFDR-c04716-STATIC-001` id, `harness/runner.py
  run_wrapped` timing, `implementation.md` and `execution_report.yaml` under
  `experiments/EXP-PFDR-c04716/`). The frozen contract and handoff forbid a
  `manifest.yaml` and any run record (invalidation rule 1), fix the deliverables
  at exactly seven files, and restrict the write scope to `runs/STATIC-001/`
  (completion gate G6). The contract governs: none of those files was written
  and `run_wrapped` was not used (it would create a run record). The
  manifest-equivalent facts (commit, dirty flag, command, environment,
  informational timing, sha256s, inference block) are in this report, and the
  `execution_report` YAML required by `agents/executor.md` is embedded below
  and returned in the executor's message.
- D2. Read-only git commands (`git rev-parse HEAD`, `git status --porcelain`)
  were run to record the commit and dirty state the launching prompt required,
  although the handoff says "never run git". No git write, add, commit, push
  or branch operation occurred.
- D3. The script's stdout / stderr and the determinism re-run were captured
  in the session scratchpad outside the repository, not in the package, to
  keep the package at the seven declared files; stdout is reproduced verbatim
  above and stderr was empty.
- D4. The hand comparison includes, in addition to the contract's 8 listed
  values, the further hand values of H-PFDR-06fd60 (D) and dcf857 (D), each
  labelled by source. This is an addition for completeness (the handoff asks
  for every H (D) value); it changes no primary comparison.
- D5. Modelling choices the contract leaves open, recorded so a reviewer can
  vary them: (a) n = round(m s) in the balance (exact integer binomials need an
  integer n; sensitivity to n +/- 1 emitted per cell); (b) D_S = m 2^{m-1}
  in the direct-presentation fixture (the ratio exponent is independent of
  D_S); (c) the 2^m filtering factor is charged inside C(0) in the balance and
  omitted from the C(k) curves (k-independent, so argmin unaffected);
  (d) the leaf is emitted under both the formula charge and the da1428
  root-finding charge.

## Anomalies and unexpected observations (recorded, not interpreted)

- A1. P3's "k* = 0" does not hold at 4 of 54 table cells (all at log2 N = 64,
  listed above); at those cells the root-finding leaf is cheaper than C(0).
- A2. P5's binomial binom(2(D_0 - m), D_0) is zero at 7 of the 9 (m, D_0)
  pairs, and k_c is outside the guessing range at every table cell.
- A3. dcf857's m = 3 line quotes the constant as 2^{2.8}; the script's
  constant 2 sqrt(48) is 2^{3.79}.
- A4. 84cdb7's prose says C = B^{m-1} gives "nothing better than N^{1/2}";
  the balance as frozen in this contract gives exponent 1.0 exactly (the
  contract's own F3 expects N^1, which is what the script emits).
- A5. dcf857's title quotes the (256, m = 4, D_0 = 4, omega 2) cell as
  "2^127 versus 2^127.8"; its table and the contract's inputs say 2^128.6;
  the script gives 128.74 (T - rho = +0.91).
- A6. The one hand value exceeded by more than 1 in log2 is the
  "about 2^150" cell (A-list above, +1.60).
- A7. Shared-worktree event: the tree was clean when this session started
  (19:50 UTC, before `cost_table.py` was written at 19:50:57 UTC). At the
  final read-only `git status` (19:55 UTC) an unrelated untracked directory
  `harness/macaulay_fp/` (columns.py, koszul.py, linalg.py, poly.py,
  series.py; mtimes 19:53-19:55 UTC) had appeared, written by another agent
  in the same worktree (consistent with the F_p Macaulay port,
  TASK-20260903-ba41aa). This executor did not create, read, import or use
  it; the package depends on nothing in it. Recorded for the Coordinator's
  snapshot staging, which must stage only the seven paths of this package.
- No infrastructure event occurred.

## Sources opened

Only internal records (the handoff's `inputs` list, plus
`experiments/EXP-JPR-402649/specification.yaml`,
`ledger/handoffs/TASK-20260902-19eacf.yaml`, `agents/executor.md`,
`AGENTS.md`-bound docs). No external source was opened; Bettale-Faugere-Perret
and Huang-Kosters-Yeo remain RECALLED pointers, never presented as checked.

## Inference block

- requested_policy: executor-implementation (reasoning_effort medium), per
  TASK-20260903-c7166d.
- resolved_model_id: claude-fable-5-1 (self-reported by the runtime to the
  executor session; `AUTORESEARCH_POLICY` / `AUTORESEARCH_BACKEND` were unset,
  so no adapter resolution record exists for this session).
- model_provenance: runtime-self-reported (not adapter-verified).
- model_verified: false (no probe performed by the executor).
- reasoning_effort: medium as configured in `.claude/agents/executor.md`; not
  runtime-verifiable by the executor.
- fallback_used: false to the executor's knowledge; fallback_reason: null;
  no Bedrock; no degraded requirement known.
- independent_session: launched as a dedicated executor subagent session;
  independence from other role sessions is not verifiable by the executor.
- No model was in the loop of the derivation arithmetic itself: the numbers
  come from `cost_table.py`.

## Per-file sha256 (this report cannot contain its own hash; the snapshot receipt records it)

```
32de51a7773cc60e83f098e0650bbf1e3043cd004c7dfe434fef6f7954a12fbb  cost_table.py
017d73824da08abb94835284d04bf8e5f1ee3e4869efa2b36dbdc457a10335a7  ck-curves.yaml
d9460c0e6bd957f833cac044df1734e30a5bac307c169c9c5dcaeae375dfd15f  cost-table.yaml
3b987347cd288f3693894c867bb38e1c89ba4df8b5d4c3ac85b1c05dd8627ac5  thresholds.yaml
bb1351ffaa1ff6c048b84f5599e72923ffc048fe575b22b45108a68ec94c7554  fixtures.yaml
228fe4067d69283f8218725e267b46432e586ebc0c00c7d575a758a5e7f43d62  concrete-cost.yaml
```

## Completion gate G1-G7 (handoff)

- G1 met (three fixtures emitted with pass and numbers; none repaired).
- G2 met (18 cells at 64 bits emitted; all lose by >= 2^9; min 9.12).
- G3 met (54 cells at both omega with tags, qualifier, prior rho, memory,
  signed discrepancy where a hand value exists; the one discrepancy above 1
  reported as such).
- G4 met (thresholds per (m, omega) at each N and interior-band cells
  emitted and compared to the frozen brackets).
- G5 met (concrete-cost.yaml per template).
- G6 met (exactly seven files, all in `runs/STATIC-001/`; no manifest.yaml,
  curve parameters, sampled points or solver code; the script imports only
  the standard library) — subject to the Coordinator's own tree check.
- G7 met (this report).

## execution_report (agents/executor.md shape)

```yaml
execution_report:
  experiment_id: EXP-PFDR-c04716
  handoff_id: TASK-20260903-c7166d
  implementation_commit: c57429694af615f64d2e691a0df25e1b131f4875
  dirty_tree_before_writing: false
  zero_run_contract: true
  certificate: {kind: none, note: "no run occurred"}
  protocol_deviations:
    - "D1: run-layout files, manifest.yaml, run id, run_wrapped timing, implementation.md and execution_report.yaml requested by the launching prompt were NOT written because the frozen contract forbids a manifest/run record and fixes the package at seven files inside runs/STATIC-001/; their content is carried in execution-report.md"
    - "D2: read-only git (rev-parse, status --porcelain) run to record commit and dirty state; no git write"
    - "D3: script stdout/stderr and the determinism re-run kept in the session scratchpad outside the repository; stdout reproduced verbatim in execution-report.md"
    - "D4: hand comparison extended to H-PFDR-06fd60 (D) and dcf857 (D) values, labelled by source, beyond the contract's 8 listed values"
    - "D5: open modelling choices recorded: n = round(m s); D_S = m 2^{m-1} in the direct fixture; 2^m filter charged in the balance not the curves; leaf emitted under both charges"
  runs:
    completed: []
    invalid: []
    failed: []
    note: "maximum_runs 0; no run exists; STATIC-001 is a zero-run package directory"
  observations:
    - "F1 null slice: strictly decreasing, argmin at the enumerative leaf at all 6 fixture cells and all 54 table null curves; enumerative balance exponent 1.0 (N^1): PASS"
    - "F2 direct presentation: argmin k = m-1 from B = 16 on; slope of log2 ratio vs log2 B at B = 2^20 = 3.0000/2.9999/2.9998 (omega 2) and 4.6139/4.6139/4.6137 (omega 2.807) vs 2 omega - 1: PASS"
    - "F3 balance limits: C = 1 slope 2/(m+1) exactly; C = B^{m-1} 2^{m-1} slope 1.0 exactly: PASS"
    - "Small-N tell: all 18 cells at 64 bits lose by >= 2^9; min gap 9.1189 at (m 5, D_0 4, omega 2): PASS"
    - "Hand comparison: 8 contract-listed cells max |disc| 0.15; H (D) extras max 0.19; dcf857-only 'about 2^150' cell (256, m 4, D_0 6, omega 2.807) script 151.60, +1.60 (above 1)"
    - "Thresholds at 256 bits: (m 5, omega 2) between 8 and 10; (m 5, omega 2.807) between 4 and 6; (m 4, omega 2) between 2 and 4 i.e. T >= rho at D_0 = 4; all three match the frozen brackets; (m 4, omega 2.807) between 2 and 4; m = 3 below 2"
    - "P3: k* = 0 at 50/54 table cells; k* = leaf at 4 cells, all at 64 bits (m 3: D_0 6 omega 2.807, D_0 8 both omega; m 4: D_0 8 omega 2.807)"
    - "P5: binomial zero at 7/9 (m, D_0) pairs; k_c outside the guessing range at all 54 table cells"
    - "Cells with T < rho (time only, assuming HEUR-001, memory 2^53.9..2^61.6): (256, m 5, D_0 4, omega 2) 108.76; (256, m 5, D_0 4, omega 2.807) 116.60; (256, m 5, D_0 6, omega 2) 116.64; (256, m 5, D_0 8, omega 2) 124.13; all other 50 cells T >= rho"
  anomalies:
    - "A1 P3 fails at 4 of 54 cells (listed)"
    - "A2 P5 binomial degenerate at 7 of 9 (m, D_0); k_c out of range at all table cells"
    - "A3 m = 3 constant: hand 2^2.8 vs script 2^3.79"
    - "A4 84cdb7 prose 'nothing better than N^{1/2}' at C = B^{m-1} vs balance exponent 1.0"
    - "A5 dcf857 title '2^127' vs table 128.6 vs script 128.74 at (256, m 4, D_0 4, omega 2)"
    - "no infrastructure event"
  artifact_paths:
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/cost_table.py
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/ck-curves.yaml
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/cost-table.yaml
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/thresholds.yaml
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/fixtures.yaml
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/concrete-cost.yaml
    - experiments/EXP-PFDR-c04716/runs/STATIC-001/execution-report.md
  inference:
    requested_policy: executor-implementation
    requested_reasoning_effort: medium
    resolved_model_id: claude-fable-5-1
    model_provenance: runtime-self-reported
    model_verified: false
    fallback_used: false
    fallback_reason: null
    degraded_requirements: []
    independent_session: true
  executor_assessment:
    protocol_complete: true
    data_quality: good
    requires_rerun: false
    note: "derivation tier only; every number is an estimate conditional on HEUR-001; no hypothesis, heuristic, experiment, question or goal status is asserted"
```
