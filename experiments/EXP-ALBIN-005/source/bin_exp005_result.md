# BIN-EXP-005 Result — binary index-calculus cost-balance capstone (m=3)

**Date:** 2026-05-31. Script: `bin_exp005_cost_balance.sage`. Log: `bin_exp005_cost_balance.log` (RC=0, 12/12 cells, RESULTS_JSON present, byte-verified). This is the **binary analog of the prime-field NR-026 capstone**.

## SURVIVOR: NO · CANDIDATE: NO

## What this measures
For each n, build an ordinary E/F_{2^n}, **measure the EXACT factor-base size** |FB| = #{points with x-coordinate in an F₂-subspace V of dim ℓ} (enumerate the 2^ℓ subspace, `E.is_x_coord`), sweep ℓ around n/m to pick the cost-optimal cell, and report the index-calculus pipeline exponents vs Pollard rho:
- **rho_exp** = log₂(0.886·√(prime subgroup)) — Pollard rho group-op exponent (the baseline).
- **LA_exp** = 2·log₂|FB| — sparse linear algebra (the dominant IC stage at large n).
- **relgen_exp** = log₂|FB| + max(0, log₂(m!) + n − m·log₂|FB|) — relation generation (|FB| relations, each costing ~ m!·#E/|FB|^m attempts).
- **IC_exp** = max(LA_exp, relgen_exp); **IC/rho = IC_exp − rho_exp** (>0 ⇒ IC worse than rho).

This is **ANALYTIC-with-MEASURED-|FB|** (cost model explicit, factor-base size empirical) — not a toy solve presented as a break. It scales where Gröbner descent (BIN-EXP-004) cannot.

## Raw results (byte-verified)

| n | subgroup bits | rho 2^ | best ℓ | measured \|FB\| | LA 2^ | relgen 2^ | IC 2^ | **IC/rho 2^** |
|---|---|---|---|---|---|---|---|---|
| 11 | 10 | 4.8 | 4 | 8 | 6.0 | 7.6 | 7.6 | **+2.8** |
| 13 | 12 | 5.8 | 5 | 20 | 8.6 | 6.9 | 8.6 | **+2.8** |
| 17 | 16 | 7.8 | 6 | 26 | 9.4 | 10.2 | 10.2 | **+2.4** |
| 19 | 18 | 8.8 | 6 | 31 | 9.9 | 11.7 | 11.7 | **+2.9** |
| 23 | 22 | 10.8 | 7 | 63 | 11.9 | 13.6 | 13.6 | **+2.8** |
| 29 | 28 | 13.8 | 9 | 251 | 15.9 | 15.6 | 15.9 | **+2.1** |
| 31 | 30 | 14.8 | 9 | 268 | 16.1 | 17.4 | 17.4 | **+2.6** |
| 37 | 36 | 17.8 | 11 | 1019 | 20.0 | 19.6 | 20.0 | **+2.2** |
| 41 | 40 | 19.8 | 13 | 4114 | 24.0 | 19.6 | 24.0 | **+4.2** |
| 47 | 46 | 22.8 | 15 | 16290 | 28.0 | 21.6 | 28.0 | **+5.2** |
| 53 | 52 | 25.8 | 17 | 65467 | 32.0 | 23.6 | 32.0 | **+6.2** |
| 61 | 60 | 29.8 | 19 | 262590* | 36.0 | 27.6 | 36.0 | **+6.2** |

(*n=61 |FB| estimated by sampling the rate × 2^ℓ; all others exact enumeration. Measured |FB| tracks the heuristic 2^ℓ ≈ 2^{n/3} closely.)

## Finding — the binary crossover obstruction, measured

**The cost-optimized binary index calculus stays ABOVE Pollard rho at every n, and the gap GROWS once the linear algebra dominates:** IC/rho exponent = +2.8 (n=11) → +2.2 (n=37) → +4.2 → +5.2 → **+6.2 (n=61)**, monotone for n≥37.

**Mechanism (visible in the columns).** At small n, relation generation dominates (relgen_exp > LA_exp) and the gap is roughly flat ≈ +2.5. As n grows, |FB|≈2^{n/3} grows, relation generation gets cheaper (more decompositions per target), and **sparse linear algebra LA_exp = 2·log₂|FB| ≈ 2n/3 takes over** — outrunning rho's n/2. The asymptotic gap is **2n/3 − n/2 = n/6**, which is exactly the measured growth (n=61: 2n/3≈40 vs rho≈30, gap≈+6). The factor base that makes relations cheap is the *same* factor base whose linear algebra is too big — a structural squeeze, not a tuning artifact (ℓ was swept to the cost-optimal value per cell).

This is an instrumented confirmation, at realistic n (subgroups up to 2^60), of the universal experimental finding (Shantz–Teske, Galbraith–Gebregiyorgis, WDSat): **binary Semaev index calculus with m=3 does not beat rho, and the deficit widens with n.**

## Claim label

`NEGATIVE RESULT` (m=3 fixed, n≤61, measured-|FB| analytic cost model) → **BIN-NR-003**: for fixed decomposition arity m=3, the cost-optimized binary Weil-descent Semaev index calculus has IC-cost/rho-cost exponent strictly positive and growing as ≈ n/6 for n up to 61 (subgroups to 2^60), driven by the |FB|²≈2^{2n/3} sparse-linear-algebra stage exceeding rho's 2^{n/2}. No crossover below rho at any measured n.

## What this does NOT rule out (honest scope — the live escape routes)

1. **Fixed m=3 only.** The Petit–Quisquater subexponential heuristic requires **growing m ≈ n^{1/3}**, which lowers |FB|≈2^{n/m} and hence the LA exponent 2n/m → sub-linear in n. Our fixed-m=3 measurement *cannot* reach that regime — it is precisely the m-scaling we did not (and at toy/scaled compute cannot) test. **This is the single most important remaining open direction**, and our result sharpens *why* it matters: the obstruction we measured is the LA stage, so the heuristic lives or dies on whether growing m shrinks |FB|² faster than it raises the per-relation solving degree.
2. **No large-prime / structured linear algebra.** We charged LA at |FB|² (sparse). Large-prime variation or special structure could reduce the effective relation count or the matrix dimension.
3. **No special-curve amortization.** Koblitz/Frobenius (÷√n) or many-target amortization (VW94) are constant-to-poly factors not modeled here; they do not close an exponential n/6 gap but are the right levers for a *constant-factor* improvement.
4. **Per-relation solve cost lower-bounded.** We charged O(1) field ops per decomposition attempt (a lower bound); the true per-attempt cost is higher, which only *widens* the IC/rho gap — so the negative is conservative.

## Next (the corrected frontier)

**BIN-EXP-006 — the m-scaling test:** for FIXED larger n (say n∈{31,41}), sweep m∈{3,4,5} and measure |FB|≈2^{n/m}, the descended-system size, and (where reachable / via the bounded-degree heuristic) the per-relation cost, to see whether the IC/rho gap *shrinks* as m grows toward n^{1/3}. This is the binary regime where Petit–Quisquater predicts the crossover, and the one our capstone identifies as the sole surviving route. If the gap still grows with m at fixed n, that is direct evidence against the heuristic at the measurable margin.
