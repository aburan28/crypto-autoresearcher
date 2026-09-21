# BIN-EXP-003 Result — m=3 solving-degree discriminator (fixed decomposable target)

**Date:** 2026-05-31. Script: `bin_exp003_m3_fixed_target.sage`. Log: `bin_exp003_m3_fixed_target.log` (RC=0, 2/2 cells, RESULTS_JSON present). Both cells fast (<2s).

## SURVIVOR: NO · CANDIDATE: NO

## Method (fixing both BIN-EXP-002 flaws)
- **m=3** (first non-degenerate arity — m=2 linearizes at degree ≤2 and cannot show the FPPR effect).
- **Target R = P₁+P₂+P₃ with x(Pᵢ)∈V** → guaranteed decomposable, so the genuine descended S₄ system is consistent and the comparison is meaningful (`target_decomposable=True`, `real_sol_satisfies=True` in both cells).
- S₄ built by resultant of two S₃ and **VERIFIED**: 20/20 vanish on real summing 4-tuples, 18–20/20 nonzero on non-summing (`S4_GENUINE=True`, total degree 12).
- Compare actual reduced-Gröbner max degree (over `BooleanPolynomialRing`, field eqs built in) of the genuine system vs a random control with a planted solution, matched on #eqs/#vars/degree profile. Hard 150s per-cell timeout (the m=3 cell hung in EXP-001).

## Raw results (read byte-for-byte from the log)

| n | nvars | fb_size | descended degs | genuine maxdeg | genuine #sols | control maxdeg | control #sols | DISCRIMINATES | gen−ctrl | rho≈2^ |
|---|---|---|---|---|---|---|---|---|---|---|
| 7 | 6 | 3 | [1,3] | **3** | 13 | 1 | 2 | **False** | **+2** | 2.8 |
| 11 | 12 | 17 | [3] | **3** | 46 | 2 | 12 | **False** | **+1** | 4.8 |

## Finding

**The genuine binary Semaev system solves at a HIGHER (or equal) Gröbner degree than a random matched-degree control — the OPPOSITE of what a sub-rho index calculus needs.** FPPR/Petit–Quisquater require the genuine descended system to solve *below* the generic degree (their first-fall/degree-of-regularity heuristic). Here the genuine system's GB max-degree (3) exceeds the random control's (1 at n=7, 2 at n=11). The genuine system also has *more* affine solutions (13, 46) than the control (2, 12), consistent with the random control being underdetermined/less structured rather than the genuine system being "easier."

This is an instrumented, controlled toy-scale confirmation of Huang–Kosters–Yeo 2015 (the FFD↔low-D_reg link is unjustified for ECDLP systems) and the universal experimental finding (Shantz–Teske, Galbraith–Gebregiyorgis, WDSat): the genuine binary Semaev decomposition system is **not** algebraically easier than a generic system of the same shape at reachable n — so it gives no solving-degree advantage to convert into a sub-rho cost.

## Claim label

`NEGATIVE RESULT` (TOY-EVIDENCE, m=3, n∈{7,11}) → **BIN-NR-002** (this REPLACES the withdrawn m=2 BIN-NR-002): at decomposition arity m=3 with a genuine, verified S₄ and a guaranteed-decomposable target, the genuine binary Weil-descent Semaev system shows **no Gröbner solving-degree advantage** over a random matched-degree control with a planted solution — in fact it solves at a strictly *higher* degree (gen−ctrl = +2, +1). No exploitable algebraic shortcut is detectable at toy n.

## Honest scope / what this does NOT rule out (self-red-team)

1. **Toy n only (7, 11).** The Petit–Quisquater heuristic is asymptotic with *growing* m≈n^{1/3}; n∈{7,11} forces m=3 (the smallest non-trivial m) and cannot reach the regime where the claimed crossover lives (estimated n≫2000). We measured the only regime toy compute allows.
2. **The control is not a perfect null.** A random system with a planted solution matches degree/size but not the full S_m symmetry; it may be artificially easy (its low maxdeg 1–2 and few solutions suggest underdetermination). A stronger control would be a *random structured* system with the same multi-homogeneous Weil-descent shape. So "genuine is harder than this control" is robust; "genuine has no structure at all" is NOT claimed.
3. **No symmetry-breaking applied.** The genuine system's 13/46 solutions include the m!=6 permutations of the factor-base decomposition; quotienting that symmetry (Galbraith/WDSat) would change the solution count and possibly the solving degree. The degree comparison stands, but a symmetry-reduced genuine system is a cleaner future measurement.

## Next (de-prioritized — all point the same way)

- **BIN-EXP-004 (optional):** stronger structured control (random multi-homogeneous Weil-descent-shaped system) + symmetry-breaking on the genuine system, n up to compute limit. Expectation given all evidence: genuine still ≥ structured-control degree; no sub-rho signal at reachable n.
- The decisive question (does genuine D_reg grow as O(m²) at large n) is **not toy-reachable** and remains the field's central OPEN problem; our contribution is the controlled instrument + the consistent toy-scale negative, not a resolution of the asymptotic heuristic.
