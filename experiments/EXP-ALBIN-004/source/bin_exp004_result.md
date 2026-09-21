# BIN-EXP-004 Result — larger-n binary Semaev IC reachability (m=3 Gröbner descent)

**Date:** 2026-05-31. Script: `bin_exp004_larger_n.sage`. Log: `bin_exp004_larger_n.log`. Per-cell 240s hard timeout.

## SURVIVOR: NO · CANDIDATE: NO · purpose: establish the Gröbner-descent reachability ceiling

## Raw results (byte-verified from the log)

| n | nvars | \|FB\| | descended deg | genuine solving degree | consistent | real_sol_satisfies | GB secs | status |
|---|---|---|---|---|---|---|---|---|
| 11 | 12 | 8 | 6 | **2** | True | True | 0.95 | OK |
| 13 | 12 | 7 | 6 | **2** | True | True | 1.46 | OK |
| 17 | 18 | 26 | 6 | — | — | — | — | **TIMEOUT(240s)** |
| 19 | 18 | 31 | 6 | — | — | — | — | **TIMEOUT(240s)** |

(n=23,29,31,37 not reached — killed after the n=17/19 timeouts established the ceiling.)

## Findings

1. **Genuine solving degree stayed BOUNDED (=2) at the reachable cells (n=11,13).** This is the FPPR-favorable direction: the genuine descended S₄ system, despite total degree 6, solves at Gröbner degree 2 — its real factor-base solution is recovered (`real_sol_satisfies=True`). At face value this is *consistent with* (not proof of) the bounded-first-fall heuristic at small n.
2. **Plain Gröbner descent is UNREACHABLE past n≈17** under a 240s cap (degree-6 descended system in ≈n binary variables → Macaulay blowup). This is exactly why the literature (WDSat/SAT, symmetry-breaking) abandons direct Gröbner for binary IC. So the per-relation *solve degree* is NOT the quantity we can scale — but it is also NOT the quantity that decides crossover.

## Why this is not the decisive measurement (→ BIN-EXP-005)

A bounded per-relation solving degree does **not** imply IC beats rho: the index-calculus pipeline cost is dominated by **relation count × per-relation cost + sparse linear algebra ≈ |FB|²**, and |FB|≈2^{n/3} forces LA≈2^{2n/3}, which must be compared to rho's 2^{n/2}. That balance is curve-only (no Gröbner) and scales to realistic n — measured in BIN-EXP-005 (the capstone).

## Claim label

`OBSERVATION` (TOY-EVIDENCE, n∈{11,13}): genuine binary descended S₄ solving degree is bounded (=2) where reachable, with verified real-solution recovery; plain Gröbner descent is compute-unreachable past n≈17. No NR filed here — this is a reachability/scoping result feeding the BIN-EXP-005 capstone.
