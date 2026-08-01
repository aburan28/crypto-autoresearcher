# BIN-EXP-006 Result — the m-scaling test (the surviving escape route)

**Date:** 2026-05-31. Script: `bin_exp006_m_scaling.sage`. Log: `bin_exp006_m_scaling.log` (RC=0, 10/10 cells, RESULTS_JSON byte-verified).

## SURVIVOR: NO · CANDIDATE: NO

## What this tests
BIN-NR-003 (capstone) identified the |FB|²≈2^{2n/3} sparse-linear-algebra stage as the obstruction for fixed m=3. The Petit–Quisquater subexponential heuristic escapes it by **growing m** (≈n^{1/3}), which shrinks |FB|≈2^{n/m} and the LA exponent 2n/m. This experiment asks the directly-measurable version: **at FIXED n, does increasing m shrink the IC/rho gap (toward a crossover) or does the per-relation solving cost rise faster?** For n∈{31,41}, m∈{2,…,6}, we measure EXACT |FB| (enumerated) and bracket the per-relation solve cost two ways (FPPR-optimistic bounded degree vs a degree-2^{m-1} semiregular proxy).

## Raw results (byte-verified)

| n | m | \|FB\| | LA 2^ (=2log₂\|FB\|) | per-rel solve 2^ (opt) | IC_opt/rho 2^ | IC_sr/rho 2^ |
|---|---|---|---|---|---|---|
| 31 | 2 | 32900 | 30.0 | 21.2 | **+23.4** | +23.4 |
| 31 | 3 | 504 | 17.9 | 34.9 | **+35.7** | +35.7 |
| 31 | 4 | 135 | 14.2 | 51.4 | **+50.9** | +54.8 |
| 31 | 5 | 37 | 10.4 | 60.9 | **+63.2** | +66.5 |
| 31 | 6 | 18 | 8.3 | 64.3 | **+69.1** | +4.8 † |
| 41 | 2 | 527539 | 38.0 | 22.8 | **+25.9** | +25.9 |
| 41 | 3 | 8196 | 26.0 | 39.8 | **+37.5** | +37.5 |
| 41 | 4 | 508 | 18.0 | 57.2 | **+56.0** | +60.9 |
| 41 | 5 | 132 | 14.1 | 73.7 | **+73.6** | +84.9 |
| 41 | 6 | 66 | 12.1 | 88.3 | **+88.8** | +72.6 † |

## Finding

**At fixed n, increasing m makes the IC/rho gap WORSE, not better.** The LA exponent does fall with m exactly as Petit–Quisquater would want (n=31: 2^30 → 2^8), confirming the |FB|²-relief mechanism is real. **But the per-relation Gröbner-solve cost rises faster** (2^21 → 2^64), because the descended system's degree scales with the Semaev per-variable degree 2^{m-1}, and it dominates the pipeline. Net: the gap grows monotonically with m at both n. So the *fixed-n* m-sweep does not approach a crossover — the linear-algebra relief from a smaller factor base is overwhelmed by the harder polynomial solve. This is the precise trade-off at the heart of the FPPR/Petit–Quisquater balance, measured.

## Honest caveats (self-red-team — do NOT overclaim)

1. **Per-relation solve cost is MODELED, not measured.** It is a `binomial(nvars, D)^ω` proxy with D from either an FPPR-optimistic bound (m(m−1)/2+1) or a 2^{m-1} semiregular proxy — **not** a measured Gröbner degree (BIN-EXP-004 showed the real solve is unreachable past n≈17). The *direction* (rises steeply with m, dominates) is robust and theory-consistent; the exact exponents are model-dependent and should not be quoted as measured complexities.
2. **† artifact at m=6.** The `Dsr` proxy hits D≥nvars there, where `log₂binomial(nvars,D)=0` collapses the solve cost to 2^0 → the spurious "+4.8"/"+72.6" dips. These are **cost-model artifacts, NOT crossovers**, and are excluded from the conclusion. (The IC_opt column, which caps D at nvars more gracefully, shows no such dip.)
3. **This does NOT contradict Petit–Quisquater.** They scale m **with growing n** (m≈n^{1/3}, so the per-relation degree ≈n^{2/3} grows sub-linearly while |FB| shrinks); we swept m at FIXED n (where m=6 already forces an enormous relative degree). Our result says: *at the n we can reach, no fixed-n choice of m crosses below rho, and the optimum is small m* — it does NOT measure the n→∞, m≈n^{1/3} diagonal, which remains the genuine open question and is not reachable here.

## Claim label

`NEGATIVE RESULT` (TOY/SCALED-EVIDENCE, n∈{31,41}, modeled per-relation solve) → **BIN-NR-004**: at fixed n∈{31,41}, sweeping the decomposition arity m∈{2,…,6} does not shrink the binary IC/rho cost gap — the gap grows monotonically with m, because the per-relation polynomial-solve cost (degree ~2^{m-1}) rises faster than the sparse-linear-algebra cost (2^{2n/m}) falls. The cost-optimal arity is small (m=2–3), consistent with BIN-NR-003. Caveat: per-relation solve cost is a modeled proxy, not a measured Gröbner degree.

## What remains OPEN (unchanged, sharpened)

The Petit–Quisquater **n→∞ diagonal m≈n^{1/3}** is the sole surviving route and is **not reachable** at scaled compute — it requires either a proof that the descended first-fall/D_reg stays ≈ the bounded value as both n and m grow (Huang–Kosters–Yeo 2015 give evidence against), or measurements at n in the hundreds (only feasible via WDSat/SAT + symmetry-breaking, the literature's tools). Our contribution: a measured-|FB|, explicit-cost-model map showing (i) fixed-m gap grows ~n/6 (BIN-NR-003) and (ii) fixed-n gap grows with m (BIN-NR-004) — i.e. both axis-parallel directions move *away* from a crossover, leaving only the diagonal, which is exactly where the unresolved heuristic lives.
