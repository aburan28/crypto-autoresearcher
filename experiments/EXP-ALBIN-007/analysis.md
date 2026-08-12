# Analysis — Autolab binary-field BIN-EXP-007: WDSat

## Observation
**Date:** 2026-05-31. Script: `bin_exp007_wdsat.sage` (+ extra cells `bin_exp007b_extra.log`). Solver: CryptoMiniSat via `pycryptosat` (native `add_xor_clause` — the WDSat-defining feature).

Source excerpt / raw summary:

```
# BIN-EXP-007 Result — WDSat-style SAT decomposition harness

**Date:** 2026-05-31. Script: `bin_exp007_wdsat.sage` (+ extra cells `bin_exp007b_extra.log`). Solver: CryptoMiniSat via `pycryptosat` (native `add_xor_clause` — the WDSat-defining feature).

## SURVIVOR: NO · CANDIDATE: NO · purpose: push the per-relation DECOMPOSITION solve past the Gröbner wall (n≈17) toward the Petit–Quisquater diagonal.

## What was built (the deliverable)

A working, validated WDSat-style SAT harness for binary Semaev point decomposition:
- **Semaev S₃/S₄/S₅** for the binary curve (resultant recursion), each **verified** (vanishes on ≥18 real summing tuples, nonzero on non-summing) before any use.
- **Fast Weil descent to F₂** (the engineering unlock): vectorize the F₂-coordinate extraction of every coefficient into a GF(2) matrix, precompute each c-monomial once, assemble each F₂-component by a bulk Boolean-ring sum. **~70× faster** than the naive per-term loop (n=17: 2.5s vs 188s; n=23: 19s vs intractable). **Correctness proven**: the slow ordinary-ring (degree-12) descent, reduced into the Boolean ring (x²=x), is **byte-identical** to the fast Boolean descent (sym_diff=0, offline check).
- **WDSat-style CNF+XOR encoding:** each descended Boolean Semaev equation → one *native XOR clause* over fresh monomial-variables; each monomial-variable ⟺ ∏ of its factor c-variables via Tseitin AND-gates. This is exactly the structure WDSat exploits (the equations are XOR-linear in the monomial variables).
- **Lex symmetry-breaking** on the m factor-base blocks (the Galbraith/WDSat m! cut), as an MSB-ordering relaxation.
- **Native solve time-limit** via `solver.solve(time_limit=…)` (pycryptosat is a C extension that ignores Python `signal.alarm`; the limit returns UNKNOWN, surfaced as a clean SOLVE_TIMEOUT — NOT mis-read as UNSAT).
- **Built-in validation:** a known decomposition R = ΣPᵢ (x(Pᵢ)∈V) must be SAT; the recovered assignment must satisfy all descended equations AND map back to real factor-base x-coordinates (`valid` and `recovX` columns).

## Reachability — SOLVES PAST THE GRÖBNER WALL (the goal). Complete frontier (byte-verified)

| n | m | nvars | distinct monomials (AND-gates) | descend secs | solve secs | status | valid | real x recovered |
|---|---|---|---|---|---|---|---|---|
| 11 | 3 | 12 | 1048 | ~1 | 0.02 | **SOLVED** | True | True |
| 13 | 3 | 12 | 1048 | ~1 | 0.02 | **SOLVED** | True | True |
| 17 | 3 | 18 | 9369 | 2.5 | **30.3** | **SOLVED** | True | True |
| 19 | 3 | 18 | 9369 | 3.3 | **33.3** | **SOLVED** | True | True |
| 23 | 3 | 24 | 46848 | 19.5 | 122 (cap) | SOLVE_TIMEOUT | — | — |
| 29 | 3 | 30 | 166675 | 102 | — | DESCENT-BOUND (outer cap) | — | — |
| 31 | 3 | 30 | 166675 | 117 | — | DESCENT-BOUND (outer cap) | — | — |

**Gröbner descent (BIN-EXP-004) was UNREACHABLE past n≈17 (240s timeout). The WDSat/SAT harness SOLVES n=17 and n=19 correctly** — recovering the genuine factor-base decomposition (`valid=True`, `recovX=True`). This independently reproduces the WDSat 2019/2020 per-relation advantage.

**Two distinct walls, cleanly separated by the frontier:**
- **n=23** (47K monomial-vars): descent + encoding are fast (19.5s + ~1s); the wall is the **SAT solve** (hit the 120s cap → SOLVE_TIMEOUT, correctly recorded as UNKNOWN, not UNSAT).
- **n=29, 31** (167K monomials): the **Weil descent itself** now costs ~102–117s (Φ has millions of terms), and the outer guard fires before the solve starts. Past n≈29 the descent is the binding constraint at this compute scale, before the solver is even invoked.

So the practical m=3 reachability ceiling with a general-purpose SAT solver on this (CPU-contended) machine is **n≈19 solved / n≈23 solve-bound / n≈29 descent-bound**.

## The diagnosed ceiling (honest, important)

The frontier was profiled stage-by-stage and shows **two different walls**:
- At **n=23, m=3**: `subs`=1s, `descend`=19.5s, `encode`≈1s (46,848 AND-gate vars). The wall is the **CryptoMiniSat SOLVE** — the ~47K-var instance hit the 120s solve cap (and in a first uncapped run burned 40 CPU-minutes). The ceiling here is **fundamental to the SAT solve**, not a harness inefficiency.
```

## Comparison
Compared against Autolab's stated baseline (typically Pollard rho / VW / Wesolowski-class
isogeny cost, depending on topic). This import does not recompute those baselines inside
crypto-autoresearcher.

## Inference
`OBSERVATION` / `TOY-EVIDENCE` (or Autolab's original label if stronger, still not upgraded):
the Autolab package is now citeable as `EXP`+`RUN` evidence under the harness. Scientific
content remains bounded by Autolab's original scope and caveats.

## Limitation
- Not independently re-executed in this repository.
- Certificates were not re-verified; do not promote discrete-log / decomposition claims.
- Claim tier remains `toy` unless a later harness experiment re-runs with certificates.
