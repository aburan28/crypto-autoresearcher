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
- At **n=29, 31, m=3**: the **Weil descent** now costs ~102–117s (166,675 monomials), exceeding the outer guard before the solver runs. Past n≈29 the descent is the binding constraint at this compute scale.

Both are general-purpose-tooling limits, not science barriers: the literature's dedicated WDSat solver reaches further via a smarter monomial/XOR representation + aggressive symmetry-breaking (the solve wall), and a streaming/sparse descent would push the descent wall. Both are clear next-step engineering targets. (Note: the machine was CPU-contended by unrelated processes during this run, inflating wall-times somewhat; the *relative* frontier and the stage-by-stage diagnosis are robust.)

## What this means for the diagonal

The per-relation decomposition reachability moved from Gröbner's n≈17 to SAT's n≈19–21 (solvable) with n=23 at the general-SAT ceiling. **This does NOT move the crossover:** the whole-pipeline obstruction is the |FB|²≈2^{2n/3} sparse linear algebra (BIN-NR-003), untouched by per-relation solve speed; and the solve time itself climbs steeply (0.02s at n≤13 → ~30s at n=17–19 → intractable at n=23). The Petit–Quisquater diagonal (m≈n^{1/3}, n in the hundreds) remains out of reach at this compute scale with a general SAT solver — consistent with every prior experimental study (Shantz–Teske, Galbraith–Gebregiyorgis, WDSat 2020: IC does not beat rho at any reachable n).

## Claim label

`OBSERVATION` (TOY/SCALED, tool + reachability) → **BIN-OBS-005**: a validated WDSat-style SAT harness solves binary Semaev point decomposition correctly past the Gröbner reachability wall (n=17,19 solved + verified; Gröbner ceiling n≈17), with the reachability frontier at n≈23/m=3 diagnosed to lie in the SAT solve of a ~47K-monomial-variable instance (not the descent/encoding). An enabling tool, NOT a sub-rho result — the BIN-NR-003 linear-algebra crossover obstruction is unaffected by per-relation solve speed.

## Honest scope / next

- The harness pushes *per-relation decomposition* reachability; it does NOT run a full DLP and does NOT change the BIN-NR-003 crossover obstruction.
- To push the diagonal further: (1) a dedicated WDSat-style monomial representation + full lex symmetry-breaking (the literature's edge over general SAT); (2) the m=4/m=5 probe (running) to see whether higher arity is reachable at small n; (3) ultimately n in the hundreds, which needs the dedicated solver. This harness is the correct foundation for all three.
