# Implementation note — RUN-SEMBIN-251fd3

## Code

`experiments/EXP-SEMBIN-db9bc3/code/`:

| module | origin | status in attempt 2 |
|---|---|---|
| `binary_field.py` | attempt 1 | kept unchanged; primitive polynomial verified by full cycle; Tr(1) = n mod 2 and Hasse bound checked in self-test |
| `arm_c_coset.py` | attempt 1 | kept unchanged; bounds A/B, searched-coset reading, exact enumeration and null |
| `semaev_repro.py` | attempt 1 | kept; ONE docstring corrected (`degenerate_slice`: ceiled rows also agree exactly; the slack is a separate reported number) |
| `nagao_cost.py` | attempt 1 | kept unchanged; T1–T5, vOW Pareto minimum via `semaev_repro`, crossover, unit disclosure |
| `arm_i_independent_memory.py` | attempt 1 | kept unchanged; imports nothing from the directory; docstring records it was written before ARM N |
| `selftest.py` | attempt 2 | 56 hand-checked assertions; two literals of MINE were wrong on first run (a docstring-derived expectation and −log2(1−1/e) at the 5th decimal) and were corrected; the code under test did not change |
| `run_experiment.py` | attempt 2 | driver; arms in contract order; each artifact written on completion; provisional manifest first, final manifest last |

## Conventions (all declared in code before the arms ran)

- Sign: ARM N margin = Nagao − vOW (positive = Nagao worse). ARM R reproduces
  COST-SEMBIN-8d123b in ITS sign (baseline − Semaev). Both stated wherever used.
- vOW: T = W(1/M + 1/w), Mem = 3n·max(w, M), W = 0.886·2^{n/2}. Product minimum
  6nW; equal-rate minimum √(6nW); time-only at total work W (no interior
  minimum exists — declared).
- m = max(2, ⌈n/C_0⌉); N = n(m−1) (frozen quantity); exact shifted count
  m·C_0 + (m−2)n reported beside it.
- T1: loose d_F·log2 N or exact log2 C(N+d_F, d_F). T2 = (ω−1)·T1 so T1+T2 =
  ω·log2(monomials) (Lemma 2). T3 = log2(m·2^{C_0}+1). T4 = −log2(1−e^{−λ}),
  log2 λ = (m·C_0−n) − Δ with Δ the ARM C Jensen deficit. T5 = log2 C(N+d_F, d_F)
  field elements (frozen width), and 2× that as the dense-square reading.
  T6 = ω·T3 (index-calculus linear algebra) log-added to time.
- Tolerances: 1e-3 bits vs targets printed to ≥ 4 decimals; 5e-3 vs 2 decimals;
  5e-2 vs 1 decimal; integers exact.

## Measured vs modeled

Measured: ARM C exact enumeration (x-image sizes, empty-coset counts, null
counts). Modeled: everything else.

## Deviations

See `task-report.md` §9. Summary: two driver executions in attempt 2 (labels
only, exec-1 retained, zero numeric differences); manifest artifacts block
re-hashed once after the two markdown reports were written; HEAD moved under the
run because the Coordinator committed on the shared branch.

## Resources

Wall 5.6 s per driver execution; peak RSS 120 MB (cap 2 GB); 1 run of 1 permitted.
