# WWIT — what would it take for closure-based point-decomposition index calculus to beat rho on ECC2K-130

Zero-experiment cost-model derivation (scripted arithmetic only). Produced by `wwit_model.py` (Python 3 stdlib, deterministic, ~9 s). No repository file was read from the forbidden paths (`experiments/EXP-FROB-30006a/`, `experiments/EXP-QSP-70b731/runs/`) and no repository file was changed. Every number below is either re-derived in the script from a cited constant or marked ASSUMED with its sensitivity shown. The full script output is pasted verbatim in the last section; the sections before it are a reading guide.

## 1. Headline

**Time only.** Under the full variable count of the descended system — the direct `S_{m+1}` descent (`N_var = m l`, degree `m(m-1)`) or the chained `S_3` system (`N_var = m l + (m-2) n`, cubic) — **no cell** with `m ∈ {3,4,5,6,8,10,12,16}`, closure degree `D ∈ {3,4,5,6}`, `ω ∈ {2, 2.37, 3}`, dense or sparse (`cols² w` or `cols × nnz`) brings the total charged cost below rho `2^60.81` **with a refuting degree `D ≥ 4`**. The only rows under rho are `D = 3`, which is the cubic equations with no multiplier and refutes nothing (pilot `W_3`: 0 of 140 UNSAT instances; Semaev proves the first fall degree is 4).

**The one reading that beats rho on time** is Semaev's own unproved "block" heuristic (the closure cost scales with one `2n + l`-variable block, charged once per block, rather than with the `(m-1) n`-variable chain) **and** `ω = 2` (the dense-elimination floor) **and** `m ≥ 10`: margins +2.2 (m=10), +3.9 (m=12), +5.9 (m=16) bits; the `cols × nnz(M_D)` sparse lower bound at m=16 gives +1.5. At `ω = 2.37` the best block cell is 4.4 bits **above** rho; at `ω = 3`, 22 bits above. Remove any one of the three conjuncts and no cell beats rho.

**Time × memory.** No refuting cell beats the program's vOW convention `6 n W`. There is **no n = 131 row** in the program (`arm-b-coherent-baseline.json` records `own_curve_min_product_log2` only at n = 163, 233, 283, 409, 571), so the comparator `6 × 131 × 2^60.809 = 2^70.43` is derived here with `W = matched rho`. The best refuting cell is 26–40 bits above it; the degree-4 closure matrix alone is `2^55`–`2^80` bits per attempt.

## 2. D_max(m): the target the m = 4 / 5 pilot must hit

`c*(m)` = per-attempt budget at the optimal `l` = the pinned D3 column (rho steps; +16.1 bits in bit-ops). `D_max` = largest `D` whose single dense elimination `cols^ω`, `cols = C(N_var, ≤ D)`, fits `c*(m)`. "3(nonref)" = only the non-refuting degree fits; "none" = not even that.

| m | c*(m) rho-steps | c*(m) bit-ops | N_var chained | D_max ω=2 | D_max ω=2.37 | D_max ω=3 | ω that ties at D=4 (chained) | N_var block | D_max ω=2 (block) | ω that ties at D=4 (block) |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | −15.55 | 0.5 | 218 | none | none | none | 0.02 | 291 | none | 0.02 |
| 4 | 11.01 | 27.1 | 378 | none | none | none | 0.91 | 291 | none | 0.93 |
| 5 | 33.08 | 49.2 | 531 | 3(nonref) | none | none | 1.56 | 290 | 3(nonref) | 1.69 |
| 6 | 37.39 | 53.5 | 664 | 3(nonref) | none | none | 1.63 | 285 | 3(nonref) | 1.84 |
| 8 | 42.52 | 58.6 | 932 | 3(nonref) | none | none | 1.68 | 280 | **4** | 2.01 |
| 10 | 45.53 | 61.6 | 1201 | 3(nonref) | none | none | 1.70 | 277 | **4** | 2.10 |
| 12 | 47.49 | 63.6 | 1470 | 3(nonref) | none | none | 1.70 | 275 | **4** | 2.17 |
| 16 | 49.86 | 66.0 | 2009 | 3(nonref) | none | none | 1.68 | 273 | **4** | 2.24 |

Direct presentation: `D_min = m(m-1)` (6, 12, 20, 30, 56, …) and `D_max = none` everywhere; just writing the system costs `2^29.0 / 2^52.8 / 2^79.7 / 2^103.1` monomials at m = 3..6 against budgets of `2^0.5 / 2^27.1 / 2^49.2 / 2^53.5` bit-ops. 2LP (GTTD) budgets `2^8.71` (m=3) and `2^22.34` (m=4) widen the system to 263 / 395 variables and `D_max = none` at every ω (ω that ties at D=4: 0.90 / 1.29).

**Reading for the pilot.** At m = 4 the per-attempt budget is `2^27.1` bit-ops while `C(378, ≤4) = 2^29.7` columns: the pilot cannot even *read* the degree-4 Macaulay matrix inside the budget (ω that ties = 0.91 < 1). At m = 5 the gap at D = 4, ω = 2 is 14 bits (ω that ties = 1.56). So "D must stay ≤ D_max(m)" has no satisfiable value for m ≤ 6 at any ω ≥ 1, and D_max = 4 appears only at m ≥ 8, only under the block heuristic, only at ω ≤ 2.0–2.24.

## 3. The three most sensitive parameters (T8)

1. **ω** (elimination exponent). At D = 4 the column count is fixed by `N_var`, so per-attempt cost = `ω × log2 cols` with `log2 cols = 27.8–39.3`: each 0.1 of ω is 2.8–3.9 bits. The block cell at m=16 ties at ω = 2.375 exactly; the chained cells need ω ≤ 1.56–1.70, below the reading-the-matrix floor.
2. **D** (closure degree). One step from D = 4 to D = 5 costs 11.5 (block) to 15.8 (chained) bits at ω = 2. Conversely a refutation at D = 3 does not exist (first fall degree 4).
3. **Presentation / variable count** (block `2n + l` vs chained `m l + (m-2) n`): 7–12 bits of `log2 cols` at D = 4 for m ≥ 8, i.e. 14–24 bits at ω = 2. This is the entire difference between the "4 winning cells" and "no winning cell".

Everything else is second order: the `2^16.1` bit-ops-per-rho-step credit shifts every margin by 16.1 bits uniformly (the block m=16 cell would need a credit of only 10.2 bits to tie; the chained m=10 cell would need 27.8); ambient N = r vs 4r (+0.1 to +1.0), negation fold (+1.0), Poisson A(μ) vs cap (−0.4 to −0.6), SAT/UNSAT cost ratio 1–4.4 (+0.7 / −0.95), LA iteration constant k = 3 (0.0) flip nothing. The early-abort split buys ≤ 1 bit at the cap (p_sat ≈ 0.63) and nothing in the sub-cap regime.

## 4. Honest asymptotic reading (T9)

If D = 4 stayed bounded for all m the family is Semaev's `2^(c sqrt(n ln n))`, `c = sqrt(2/ln 2) = 1.6986`; at n = 131 the exponential part is only `2^42.9`, so the finite-n verdict is set entirely by the polynomial cofactor `cols^ω`. Time-only crossings against `2^(n/2)` (persistent):

- Semaev's own units and formula (k = n/m, attempts `m! 2^k`, `n^{4ω}` block, ω = 3): n = **302** (tables.yaml re-derivation 302; paper says n > 310). ω = 2.37: 241; ω = 2: 205.
- Fair finite-n reading (μ = 1 cap `k = (n + log2 m!)/m`, attempts `2^k`, m ≤ 16, block cost × (m−2)): ω = 3 → 231, ω = 2.37 → 177, ω = 2 → 147 without the bit-op credit; with the `2^16.1` credit 185 / 131 / **100**. The one row that puts the crossing below 131 (block ∧ ω = 2 ∧ credit) is the same reading as the four "winning" cells; at ω = 2.37 the crossing is exactly 131 (margin −4.5 vs matched rho).
- Full variable count `C((m-1) n + m k, ≤ 4)^ω`, cap rule: 310 / 238 / 197 (ω = 3 / 2.37 / 2); with the credit 266 / 193 / 151.

Time × memory against vOW `6 n W` (W = 0.886·2^(n/2)): Semaev's literal time + dense `width²` working set reproduces **518** (program: 520 dense, metric-reoptimised 518) and Semaev-sparse reproduces **460** (program: 460). Under the cap rule the T×M crossings are 442 / 379 (dense / sparse, ω = 3) and no lower than 244 under any variant; n = 131 sits below all of them.

## 5. Constants and their provenance (all re-derived or asserted in T0)

| constant | value | source |
|---|---|---|
| n, r, #E = 4r, ambient N = 2^131 | 131; log2 r = 129.000 | knowledge/findings/KN-FIND-aa2efc.md:59-66; ledger/corrections/CORR-20260928-4cb669.yaml:50-58 |
| matched rho sqrt(pi r/(4·131)) | 2^60.8090 | KN-FIND-aa2efc.md:63; CORR-4cb669:61-62 (asserted) |
| bit-ops per rho step | 2^16.1 = 2^77 / 2^60.9 | knowledge/frontiers/ecdlp/generic-rho/KR-RHO-18cc42.yaml:5,13; analysis/ecdlp2m-iteration-20261009/ctrial-harvest/fit.py:42 |
| seconds per rho step | 4/22.45e6 = 2^−22.42 | ctrial-harvest/fit.py:21; README.md:21 |
| free-oracle floors 89.25/68.58/56.40/48.44/42.85/35.61 | reproduced to ≤ 0.005 bit | KN-FIND-aa2efc.md:31-33; model identified in ledger/proposals/IDEA-20260926-4b65e3.yaml:20-27 |
| CORR fit 2n/(m+1) + 2 log2 m | residuals 0.08…0.50 | ledger/corrections/CORR-20260928-2b8f4e.yaml:71-74 (a fit, not an identification) |
| pinned D3 budgets 11.01/33.08/37.39/42.52/49.86 | reproduced to ≤ 0.005 bit | experiments/EXP-BINSTD-a222b4/specification.yaml:1207-1211 (pinned_D3_bits); CORR-4cb669:77-80 |
| μ = 1 Poisson column 11.0/32.4/36.7/42.2/49.7 (brief: 11.0/32.6/37/42/50) | reproduced to ≤ 0.36 bit | a222b4 spec:1207-1211 (record_mu1_bits); IDEA-4b65e3:41-46; H-CERTBIN-6e6287.yaml:224 |
| cap locus, A(μ), LA = k m B² (k = 1) | — | a222b4 spec:251-259, 287-291 |
| plain m = 3 budget −15.55 | reproduced | ledger/hypotheses/H-BINSTD-555991.yaml:98-99 |
| 2LP budgets 8.71 (m=3), 22.34 (m=4), m = 5 infeasible | reproduced to ≤ 0.004 bit | H-BINSTD-555991.yaml:26-27,44-46; IDEA-20261001-621974.yaml:101-131 |
| yield law μ = 2^(ml−n)/m! (Semaev eq. 11) | — | inputs/SEMAEV-2015-310/paper_fulltext.md:405-417; tables.yaml derived_checks |
| descended degree m·min(m−1,l); monomials C(ml,≤deg) = 2^29.02/52.78/79.71/103.13 at l = 29/29/28/24 | reproduced | experiments/EXP-ICPERF-783e9e/impl/arity.py:60-82; runs/RUN-ICPERF-2f36fd/checkpoint/budget_table.json (n=131 cells); ctrial-harvest/fit.py:32,41 |
| chained N_var = n(t−2) + kt, cubic | — | paper_fulltext.md:1060-1066; KN-OPEN-86e7e1.md:33-35; pilot README.md:9-10 |
| Semaev F4 cost [n(m−1)]^{4ω}, block n^{4ω} "we think", 2.376 ≤ ω ≤ 3, eqs (15)-(17), c = 1.69 | — | paper_fulltext.md:41,118,472,1067-1117 |
| W_4 columns = C(N,≤4): 988/4048/10903/31931/102091 | exact | analysis/ecdlp2m-iteration-20261009/m3-closure-pilot/aggregate.md:4,13,19,20 |
| W_4 wall 0.7 / 7.2 / 322 s at N = 18/23/30; slope 2.97 in cols | — | aggregate.md:38,13,19; README.md:22-26 |
| M_4 row weight 37.1/74.8/182.1/411.1 at N = 18/23/30/40 → w ≈ N³/156 | ASSUMED extrapolation | m3-closure-pilot/results/{n9,n11,n15,n19}-poly.jsonl basis_nnz/rows (medians) |
| W_4 rows/cols at refutation 6.3/3.4/5.2; iterations 3-5; SAT/UNSAT wall 1.7/4.4 | absorbed in ω; SAT ratio ASSUMED 2 | same results files (max_rows_seen, iterations, wall_s) |
| W_3 refutes 0/60, 0/40, 0/40 (and 0/2) | — | aggregate.md:12,18,21,37 |
| no Frobenius factor-base gain at n = 131 (only stable V has dim 130) | — | knowledge/findings/KN-FIND-b9a41d.md:108-118 |
| vOW T×Mem = 6 n W on w = M; own-curve minima 91.2591 (163) … 297.0677 (571); no n = 131 row | 163 reproduced | ledger/evidence/EV-SEMBIN-4125ec.yaml:80-87; arm-b-coherent-baseline.json vow_product_excess_per_n; c1_model.py:85,124-126 |
| coherent crossovers 520 (dense) / 460 (sparse) | reproduced 518 / 460 | EV-SEMBIN-4125ec.yaml:84-85,106-109 |
| Table 3 time-only crossing 302 | reproduced 302 | inputs/SEMAEV-2015-310/tables.yaml derived_checks.table_3_columns |

ASSUMED (with sensitivity): row weight w = N³/156 (only enters the sparse rows, which never win); SAT/UNSAT ratio 2 (±1 bit); rows/cols ≈ 5 at refutation and 3–5 closure iterations (absorbed into ω; the pilot's own wall-vs-cols slope is 2.97); LA memory m·2^l·l bits (within 3 bits of a222b4's 8-byte-entry form); block presentation = one `2n + l` block charged (m−2) times (Semaev's heuristic made coherent; the literal n^{4ω} without the factor is used only for the Table-3 / EV-SEMBIN reproductions).

## 6. Verbatim output of `python3 wwit_model.py`

# WWIT: closure-based point-decomposition index calculus vs rho on ECC2K-130 (zero-experiment model)

Constants: n = 131; log2 r = 129.000; ambient log2 N = 131.000 (N = 4r); rho = 2^60.8090 rho steps; 2^16.1 bit-ops per rho step; 2^-22.42 s per rho step; rho in bit-ops = 2^76.91; rho wall at the 2009 rate = 2^38.39 s = 1.14e+04 core-years.
Time x memory comparator (DERIVED HERE, no n = 131 row in the program): 6 n W = 6 x 131 x 2^60.8090 = 2^70.43 (rho-step x bit).

## T0. Reproduction of the program's numbers (asserted)

| quantity | this script | program record [cite] | |diff| | pass |
|---|---|---|---|---|
| matched rho sqrt(pi r/(4*131)) | 60.8090 | 60.8090 [KN-FIND-aa2efc.md:63] | 0.0000 | True |
| free-oracle floor m=2 (l*=43.33) | 89.2516 | 89.25 [KN-FIND-aa2efc.md:31-33] | 0.0016 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=2 | 89.33 | 89.25 | 0.08 | True |
| free-oracle floor m=3 (l*=33.00) | 68.5850 | 68.58 [KN-FIND-aa2efc.md:31-33] | 0.0050 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=3 | 68.67 | 68.58 | 0.09 | True |
| free-oracle floor m=4 (l*=26.83) | 56.4049 | 56.4 [KN-FIND-aa2efc.md:31-33] | 0.0049 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=4 | 56.40 | 56.4 | 0.00 | True |
| free-oracle floor m=5 (l*=22.76) | 48.4352 | 48.44 [KN-FIND-aa2efc.md:31-33] | 0.0048 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=5 | 48.31 | 48.44 | 0.13 | True |
| free-oracle floor m=6 (l*=19.89) | 42.8501 | 42.85 [KN-FIND-aa2efc.md:31-33] | 0.0001 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=6 | 42.60 | 42.85 | 0.25 | True |
| free-oracle floor m=8 (l*=16.12) | 35.6085 | 35.61 [KN-FIND-aa2efc.md:31-33] | 0.0015 | True |
|   CORR-2b8f4e fit 2n/(m+1)+2log2 m, m=8 | 35.11 | 35.61 | 0.50 | True |
| D3 budget m=4 (l*=29.036) | 11.010 | 11.01 [a222b4 spec:1207-1211 pinned_D3] | 0.000 | True |
|   Poisson A(mu) re-optimised, m=4 (l*=29.04) | 11.01 | 11.0 [a222b4 record_mu1]; brief 11.0 | 0.01 | True |
| D3 budget m=5 (l*=27.581) | 33.076 | 33.08 [a222b4 spec:1207-1211 pinned_D3] | 0.004 | True |
|   Poisson A(mu) re-optimised, m=5 (l*=27.82) | 32.62 | 32.4 [a222b4 record_mu1]; brief 32.6 | 0.22 | True |
| D3 budget m=6 (l*=23.415) | 37.393 | 37.39 [a222b4 spec:1207-1211 pinned_D3] | 0.003 | True |
|   Poisson A(mu) re-optimised, m=6 (l*=23.67) | 37.06 | 36.7 [a222b4 record_mu1]; brief 37.0 | 0.36 | True |
| D3 budget m=8 (l*=18.287) | 42.522 | 42.52 [a222b4 spec:1207-1211 pinned_D3] | 0.002 | True |
|   Poisson A(mu) re-optimised, m=8 (l*=18.50) | 42.25 | 42.2 [a222b4 record_mu1]; brief 42.0 | 0.05 | True |
| D3 budget m=16 (l*=10.953) | 49.856 | 49.86 [a222b4 spec:1207-1211 pinned_D3] | 0.004 | True |
|   Poisson A(mu) re-optimised, m=16 (l*=11.08) | 49.70 | 49.7 [a222b4 record_mu1]; brief 50.0 | 0.00 | True |
| plain budget m=3 (l*=29.112) | -15.552 | -15.55 [H-BINSTD-555991.yaml:98-99] | 0.002 | True |
| 2LP budget m=3 (log2 B=28.45, B'=51.77) | 8.713 | 8.71 [H-BINSTD-555991.yaml:26-27] | 0.003 | True |
| 2LP budget m=4 (log2 B=28.61, B'=37.89) | 22.336 | 22.34 [H-BINSTD-555991.yaml:26-27] | 0.004 | True |
| 2LP m=5 infeasible (B' < B/0.162) | None | infeasible [IDEA-621974:128-131] | 0 | True |
| ICPERF monomials C(87, <= 6), m=3 | 29.02 | 29.02 [budget_table.json n=131] | 0.000 | True |
| ICPERF monomials C(116, <= 12), m=4 | 52.78 | 52.78 [budget_table.json n=131] | 0.004 | True |
| ICPERF monomials C(140, <= 20), m=5 | 79.71 | 79.71 [budget_table.json n=131] | 0.000 | True |
| ICPERF monomials C(144, <= 30), m=6 | 103.13 | 103.13 [budget_table.json n=131] | 0.003 | True |
| pilot cols C(18, <= 3) | 988 | 988 [aggregate.md] | 0 | True |
| pilot cols C(18, <= 4) | 4048 | 4048 [aggregate.md] | 0 | True |
| pilot cols C(23, <= 4) | 10903 | 10903 [aggregate.md] | 0 | True |
| pilot cols C(30, <= 4) | 31931 | 31931 [aggregate.md] | 0 | True |
| pilot cols C(40, <= 4) | 102091 | 102091 [aggregate.md] | 0 | True |
| vOW 6nW n=163 (W = 0.886 2^(n/2)) | 91.2591 | 91.2591 [arm-b-coherent-baseline.json] | 0.0000 | True |
| Semaev Table-3 time-only crossing (omega=3, n^12) | 302 | 302 [tables.yaml derived_checks] | 0 | True |

ALL REPRODUCTION ASSERTIONS PASSED (floors 68.58 / 56.40 to 0.01 bit; a222b4 pinned D3 to 0.05 bit; mu-column to 0.5 bit; 2LP 8.71 / 22.34 to 0.05 bit).

## T1. Pilot-derived closure constants (m = t = 3 chained S_3, W_4 / M_4; analysis/ecdlp2m-iteration-20261009/m3-closure-pilot/results)

| N_var | cols C(N,<=4) | M_4 row weight w (nnz/row) | fit N^3/156 | W_4 rows/cols at refutation | W_4 UNSAT median wall s | W_4 SAT/UNSAT wall |
|---|---|---|---|---|---|---|
| 18 | 4048 | 37.1 | 37.4 | 6.29 | 0.7 | 1.69 |
| 23 | 10903 | 74.8 | 78.0 | 3.38 | 7.2 | 4.37 |
| 30 | 31931 | 182.1 | 173.1 | 5.18 | 321.7 | - |
| 40 | 102091 | 411.1 | 410.3 | - | - | - |

Row-weight log-log slope N=18->40: 3.01 (cubic fill; w ~ N^3/156, ASSUMED to extrapolate). W_4 wall vs cols slope N=18->30: 2.97 (i.e. wall ~ cols^2.97; supports omega near 3 for the M4RI closure as run). Implied bit-ops at N=30: wall 321.7 s = 2^30.7 rho steps = 2^46.8 bit-ops vs cols^3 = 2^44.9, cols^2 = 2^29.9.

## T2. Per-attempt budget c*(m) at the optimal l (D3 convention: one attempt per relation above the cap), and system sizes

| m | l* | l_cap=(131+log2 m!)/m | log2 LA | log2 attempts | c*(m) log2 rho steps | c*(m) log2 bit-ops | c*(m) log2 seconds | N_var direct (ml) | N_var chained (ml+(m-2)n) | N_var block (2n+l) | direct deg | p_sat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 29.11 | 44.53 | 59.81 | 75.36 | -15.55 | 0.55 | -37.97 | 87 | 218 | 291 | 6 | 0.00 |
| 4 | 29.04 | 33.90 | 60.07 | 48.48 | 11.01 | 27.11 | -11.41 | 116 | 378 | 291 | 12 | 0.00 |
| 5 | 27.58 | 27.58 | 57.48 | 27.58 | 33.08 | 49.18 | 10.66 | 138 | 531 | 290 | 20 | 0.63 |
| 6 | 23.42 | 23.42 | 49.42 | 23.42 | 37.39 | 53.49 | 14.97 | 140 | 664 | 285 | 30 | 0.63 |
| 8 | 18.29 | 18.29 | 39.57 | 18.29 | 42.52 | 58.62 | 20.10 | 146 | 932 | 280 | 56 | 0.63 |
| 10 | 15.28 | 15.28 | 33.88 | 15.28 | 45.53 | 61.63 | 23.11 | 153 | 1201 | 277 | 90 | 0.63 |
| 12 | 13.32 | 13.32 | 30.22 | 13.32 | 47.49 | 63.59 | 25.07 | 160 | 1470 | 275 | 132 | 0.63 |
| 16 | 10.95 | 10.95 | 25.91 | 10.95 | 49.86 | 65.96 | 27.44 | 175 | 2009 | 273 | 176 | 0.63 |

c*(m) in rho steps equals the pinned D3 column (CORR-4cb669 D3; a222b4). m = 3 is negative: no oracle, however cheap, ties rho there.
2LP (GTTD) budgets: m=3 2^8.71 at log2 B=28.45, B'=51.77, attempts 2^51.77; m=4 2^22.34 at log2 B=28.61, B'=37.89, attempts 2^37.89. System sizes for a 2LP attempt (chained): m=3 N_var = l + 2l' + n = 263; m=4 N_var = 2l + 2l' + 2n = 395. In bit-ops: 24.81 (m=3), 38.44 (m=4).

## T3. D_max(m, omega): largest closure degree D whose ONE dense elimination cols^omega fits c*(m) (bit-ops). Also omega_max at D = 4 and the margin at D = 4.

A cell reads 'none' when even D = 3 (the equations themselves, which refute nothing: pilot W_3 0/60, 0/40, 0/40; Semaev proves first fall degree 4) does not fit. D = 3 is structurally non-refuting, so the operative requirement is D_max >= 4.

### Presentation: chained  (N_var = m l + (m-2) n; cubic)

| pres | m | c*(m) bit-ops | N_var | D_min | D_max omega=2 | D_max omega=2.37 | D_max omega=3 | log2 cols at D=max(4,D_min) | omega_max at that D | margin at D=4, omega=2 (bits) |
|---|---|---|---|---|---|---|---|---|---|---|
| chained | 3 | 0.5 | 218 | 3 | none | none | none | 26.5 | 0.02 | -52.4 |
| chained | 4 | 27.1 | 378 | 3 | none | none | none | 29.7 | 0.91 | -32.2 |
| chained | 5 | 49.2 | 531 | 3 | 3(nonref) | none | none | 31.6 | 1.56 | -14.1 |
| chained | 6 | 53.5 | 664 | 3 | 3(nonref) | none | none | 32.9 | 1.63 | -12.3 |
| chained | 8 | 58.6 | 932 | 3 | 3(nonref) | none | none | 34.9 | 1.68 | -11.1 |
| chained | 10 | 61.6 | 1201 | 3 | 3(nonref) | none | none | 36.3 | 1.70 | -11.0 |
| chained | 12 | 63.6 | 1470 | 3 | 3(nonref) | none | none | 37.5 | 1.70 | -11.4 |
| chained | 16 | 66.0 | 2009 | 3 | 3(nonref) | none | none | 39.3 | 1.68 | -12.7 |

### Presentation: block  (N_var = 2n + l; cubic (Semaev's unproved block heuristic), cost x (m-2) blocks)

| pres | m | c*(m) bit-ops | N_var | D_min | D_max omega=2 | D_max omega=2.37 | D_max omega=3 | log2 cols at D=max(4,D_min) | omega_max at that D | margin at D=4, omega=2 (bits) |
|---|---|---|---|---|---|---|---|---|---|---|
| block | 3 | 0.5 | 291 | 3 | none | none | none | 28.1 | 0.02 | -55.7 |
| block | 4 | 27.1 | 291 | 3 | none | none | none | 28.1 | 0.93 | -30.2 |
| block | 5 | 49.2 | 290 | 3 | 3(nonref) | none | none | 28.1 | 1.69 | -8.6 |
| block | 6 | 53.5 | 285 | 3 | 3(nonref) | none | none | 28.0 | 1.84 | -4.6 |
| block | 8 | 58.6 | 280 | 3 | 4 | 3(nonref) | none | 27.9 | 2.01 | 0.2 |
| block | 10 | 61.6 | 277 | 3 | 4 | 3(nonref) | none | 27.9 | 2.10 | 2.9 |
| block | 12 | 63.6 | 275 | 3 | 4 | 3(nonref) | none | 27.8 | 2.17 | 4.6 |
| block | 16 | 66.0 | 273 | 3 | 4 | 3(nonref) | none | 27.8 | 2.24 | 6.6 |

### Presentation: direct  (N_var = m l; D must be >= m*min(m-1,l))

| pres | m | c*(m) bit-ops | N_var | D_min | D_max omega=2 | D_max omega=2.37 | D_max omega=3 | log2 cols at D=max(4,D_min) | omega_max at that D | margin at D=4, omega=2 (bits) |
|---|---|---|---|---|---|---|---|---|---|---|
| direct | 3 | 0.5 | 87 | 6 | none | none | none | 29.1 | 0.02 | -57.6 |
| direct | 4 | 27.1 | 116 | 12 | none | none | none | 52.8 | 0.51 | -78.5 |
| direct | 5 | 49.2 | 138 | 20 | none | none | none | 79.2 | 0.62 | -109.3 |
| direct | 6 | 53.5 | 140 | 30 | none | none | none | 101.9 | 0.52 | -150.4 |
| direct | 8 | 58.6 | 146 | 56 | none | none | none | 137.8 | 0.43 | -217.1 |
| direct | 10 | 61.6 | 153 | 90 | none | none | none | 152.8 | 0.40 | -243.9 |
| direct | 12 | 63.6 | 160 | 132 | none | none | none | 159.8 | 0.40 | -256.1 |
| direct | 16 | 66.0 | 175 | 176 | none | none | none | 175.3 | 0.38 | -284.5 |

### D_max under the 2LP (GTTD) budgets, chained presentation (large legs widen the system)

| m | 2LP budget bit-ops | N_var chained | D_max omega=2 | D_max omega=2.37 | D_max omega=3 | log2 cols D=4 | omega_max at D=4 |
|---|---|---|---|---|---|---|---|
| 3 | 24.8 | 263 | none | none | none | 27.6 | 0.90 |
| 4 | 38.4 | 395 | none | none | none | 29.9 | 1.29 |

## T4. Full charged cost per (presentation, m, D, omega, sparsity), l optimised for TIME. Columns: l*, N_var, log2 cols, per-attempt bit-ops, total time (rho steps), margin vs rho, peak memory (bits), T x M, margin vs 6nW = 2^70.43

### Presentation: chained

| m | D | elim | l* | N_var | log2 cols | per-attempt bit-ops | log2 attempts | T (log2 rho steps) | margin vs rho | mem bits | T x M | margin vs 6nW | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 3 | dense w=2 | 39.61 | 250 | 21.3 | 42.6 | 54.4 | 81.85 | -21.04 | 46.5 | 128.3 | -57.9 | non-refuting |
| 3 | 3 | dense w=2.37 | 41.64 | 256 | 21.4 | 50.8 | 50.3 | 85.91 | -25.10 | 48.6 | 134.5 | -64.1 | non-refuting |
| 3 | 3 | dense w=3 | 44.53 | 265 | 21.6 | 65.4 | 44.5 | 93.96 | -33.15 | 51.6 | 145.6 | -75.1 | non-refuting |
| 3 | 3 | sparse cols^2 w | 43.88 | 263 | 21.5 | 60.2 | 45.8 | 90.65 | -29.84 | 50.9 | 141.6 | -71.1 | non-refuting |
| 3 | 3 | sparse cols x nnz(M_D) | 40.47 | 252 | 21.4 | 46.0 | 52.7 | 83.56 | -22.75 | 47.4 | 130.9 | -60.5 | non-refuting |
| 3 | 4 | dense w=2 | 42.68 | 259 | 27.5 | 55.0 | 48.2 | 88.02 | -27.22 | 54.9 | 143.0 | -72.5 |  |
| 3 | 4 | dense w=2.37 | 44.53 | 265 | 27.6 | 66.1 | 44.5 | 94.63 | -33.82 | 55.2 | 149.8 | -79.4 |  |
| 3 | 4 | dense w=3 | 44.53 | 265 | 27.6 | 83.5 | 44.5 | 111.92 | -51.11 | 55.2 | 167.1 | -96.7 |  |
| 3 | 4 | sparse cols^2 w | 44.53 | 265 | 27.6 | 72.8 | 44.5 | 101.18 | -40.37 | 51.6 | 152.8 | -82.3 |  |
| 3 | 4 | sparse cols x nnz(M_D) | 44.03 | 263 | 27.6 | 60.9 | 45.5 | 90.99 | -30.19 | 51.1 | 142.1 | -71.6 |  |
| 3 | 5 | dense w=2 | 44.53 | 265 | 33.3 | 67.3 | 44.5 | 95.78 | -34.98 | 66.6 | 162.4 | -92.0 |  |
| 3 | 5 | dense w=2.37 | 44.53 | 265 | 33.3 | 79.6 | 44.5 | 108.07 | -47.26 | 66.6 | 174.7 | -104.2 |  |
| 3 | 5 | dense w=3 | 44.53 | 265 | 33.3 | 100.6 | 44.5 | 129.05 | -68.24 | 66.6 | 195.7 | -125.2 |  |
| 3 | 5 | sparse cols^2 w | 44.53 | 265 | 33.3 | 84.2 | 44.5 | 112.60 | -51.79 | 51.6 | 164.2 | -93.8 |  |
| 3 | 5 | sparse cols x nnz(M_D) | 44.53 | 265 | 33.3 | 74.0 | 44.5 | 102.43 | -41.62 | 51.6 | 154.0 | -83.6 |  |
| 3 | 6 | dense w=2 | 44.53 | 265 | 38.7 | 78.2 | 44.5 | 106.62 | -45.82 | 77.5 | 184.1 | -113.7 |  |
| 3 | 6 | dense w=2.37 | 44.53 | 265 | 38.7 | 92.5 | 44.5 | 120.96 | -60.15 | 77.5 | 198.5 | -128.0 |  |
| 3 | 6 | dense w=3 | 44.53 | 265 | 38.7 | 116.9 | 44.5 | 145.37 | -84.56 | 77.5 | 222.9 | -152.4 |  |
| 3 | 6 | sparse cols^2 w | 44.53 | 265 | 38.7 | 95.1 | 44.5 | 123.48 | -62.67 | 51.7 | 175.2 | -104.8 |  |
| 3 | 6 | sparse cols x nnz(M_D) | 44.53 | 265 | 38.7 | 85.9 | 44.5 | 114.33 | -53.52 | 51.7 | 166.1 | -95.6 |  |
| 4 | 3 | dense w=2 | 32.91 | 394 | 23.3 | 46.6 | 36.9 | 68.62 | -7.82 | 46.6 | 115.2 | -44.8 | non-refuting |
| 4 | 3 | dense w=2.37 | 33.90 | 398 | 23.3 | 56.0 | 33.9 | 73.86 | -13.05 | 46.6 | 120.5 | -50.1 | non-refuting |
| 4 | 3 | dense w=3 | 33.90 | 398 | 23.3 | 70.7 | 33.9 | 88.46 | -27.66 | 46.6 | 135.1 | -64.7 | non-refuting |
| 4 | 3 | sparse cols^2 w | 33.90 | 398 | 23.3 | 66.0 | 33.9 | 83.76 | -22.95 | 41.0 | 124.7 | -54.3 | non-refuting |
| 4 | 3 | sparse cols x nnz(M_D) | 33.71 | 397 | 23.3 | 51.1 | 34.4 | 70.43 | -9.62 | 40.8 | 111.2 | -40.8 | non-refuting |
| 4 | 4 | dense w=2 | 33.90 | 398 | 29.9 | 60.6 | 33.9 | 78.40 | -17.59 | 59.9 | 138.3 | -67.9 |  |
| 4 | 4 | dense w=2.37 | 33.90 | 398 | 29.9 | 71.7 | 33.9 | 89.48 | -28.67 | 59.9 | 149.4 | -78.9 |  |
| 4 | 4 | dense w=3 | 33.90 | 398 | 29.9 | 90.6 | 33.9 | 108.35 | -47.54 | 59.9 | 168.2 | -97.8 |  |
| 4 | 4 | sparse cols^2 w | 33.90 | 398 | 29.9 | 79.2 | 33.9 | 97.02 | -36.21 | 41.0 | 138.0 | -67.6 |  |
| 4 | 4 | sparse cols x nnz(M_D) | 33.90 | 398 | 29.9 | 66.5 | 33.9 | 84.33 | -23.52 | 41.0 | 125.3 | -54.9 |  |
| 4 | 5 | dense w=2 | 33.90 | 398 | 36.3 | 73.2 | 33.9 | 91.00 | -30.20 | 72.5 | 163.5 | -93.1 |  |
| 4 | 5 | dense w=2.37 | 33.90 | 398 | 36.3 | 86.6 | 33.9 | 104.42 | -43.61 | 72.5 | 176.9 | -106.5 |  |
| 4 | 5 | dense w=3 | 33.90 | 398 | 36.3 | 109.5 | 33.9 | 127.26 | -66.45 | 72.5 | 199.8 | -129.3 |  |
| 4 | 5 | sparse cols^2 w | 33.90 | 398 | 36.3 | 91.8 | 33.9 | 109.62 | -48.82 | 48.7 | 158.3 | -87.9 |  |
| 4 | 5 | sparse cols x nnz(M_D) | 33.90 | 398 | 36.3 | 80.5 | 33.9 | 98.27 | -37.46 | 48.7 | 147.0 | -76.5 |  |
| 4 | 6 | dense w=2 | 33.90 | 398 | 42.3 | 85.3 | 33.9 | 103.08 | -42.27 | 84.6 | 187.6 | -117.2 |  |
| 4 | 6 | dense w=2.37 | 33.90 | 398 | 42.3 | 100.9 | 33.9 | 118.72 | -57.91 | 84.6 | 203.3 | -132.9 |  |
| 4 | 6 | dense w=3 | 33.90 | 398 | 42.3 | 127.6 | 33.9 | 145.36 | -84.55 | 84.6 | 229.9 | -159.5 |  |
| 4 | 6 | sparse cols^2 w | 33.90 | 398 | 42.3 | 103.9 | 33.9 | 121.70 | -60.89 | 56.0 | 177.7 | -107.2 |  |
| 4 | 6 | sparse cols x nnz(M_D) | 33.90 | 398 | 42.3 | 93.6 | 33.9 | 111.35 | -50.54 | 56.0 | 167.3 | -96.9 |  |
| 5 | 3 | dense w=2 | 27.58 | 531 | 24.6 | 49.9 | 27.6 | 61.43 | -0.62 | 49.1 | 110.6 | -40.1 | non-refuting |
| 5 | 3 | dense w=2.37 | 27.58 | 531 | 24.6 | 58.9 | 27.6 | 70.42 | -9.61 | 49.1 | 119.6 | -49.1 | non-refuting |
| 5 | 3 | dense w=3 | 27.58 | 531 | 24.6 | 74.4 | 27.6 | 85.90 | -25.10 | 49.1 | 135.0 | -64.6 | non-refuting |
| 5 | 3 | sparse cols^2 w | 27.58 | 531 | 24.6 | 69.7 | 27.6 | 81.20 | -20.39 | 34.7 | 115.9 | -45.5 | non-refuting |
| 5 | 3 | sparse cols x nnz(M_D) | 27.58 | 531 | 24.6 | 54.2 | 27.6 | 65.67 | -4.86 | 34.7 | 100.4 | -29.9 | non-refuting |
| 5 | 4 | dense w=2 | 27.58 | 531 | 31.6 | 63.9 | 27.6 | 75.43 | -14.62 | 63.2 | 138.7 | -68.2 |  |
| 5 | 4 | dense w=2.37 | 27.58 | 531 | 31.6 | 75.6 | 27.6 | 87.12 | -26.32 | 63.2 | 150.4 | -79.9 |  |
| 5 | 4 | dense w=3 | 27.58 | 531 | 31.6 | 95.6 | 27.6 | 107.04 | -46.24 | 63.2 | 170.3 | -99.9 |  |
| 5 | 4 | sparse cols^2 w | 27.58 | 531 | 31.6 | 83.8 | 27.6 | 95.30 | -34.49 | 42.9 | 138.2 | -67.8 |  |
| 5 | 4 | sparse cols x nnz(M_D) | 27.58 | 531 | 31.6 | 70.3 | 27.6 | 81.77 | -20.96 | 42.9 | 124.7 | -54.3 |  |
| 5 | 5 | dense w=2 | 27.58 | 531 | 38.3 | 77.4 | 27.6 | 88.87 | -28.06 | 76.7 | 165.6 | -95.1 |  |
| 5 | 5 | dense w=2.37 | 27.58 | 531 | 38.3 | 91.6 | 27.6 | 103.06 | -42.25 | 76.7 | 179.7 | -109.3 |  |
| 5 | 5 | dense w=3 | 27.58 | 531 | 38.3 | 115.7 | 27.6 | 127.21 | -66.40 | 76.7 | 203.9 | -133.5 |  |
| 5 | 5 | sparse cols^2 w | 27.58 | 531 | 38.3 | 97.3 | 27.6 | 108.74 | -47.93 | 51.3 | 160.0 | -89.6 |  |
| 5 | 5 | sparse cols x nnz(M_D) | 27.58 | 531 | 38.3 | 85.1 | 27.6 | 96.54 | -35.73 | 51.3 | 147.8 | -77.4 |  |
| 5 | 6 | dense w=2 | 27.58 | 531 | 44.8 | 90.3 | 27.6 | 101.78 | -40.97 | 89.6 | 191.4 | -121.0 |  |
| 5 | 6 | dense w=2.37 | 27.58 | 531 | 44.8 | 106.9 | 27.6 | 118.36 | -57.55 | 89.6 | 208.0 | -137.5 |  |
| 5 | 6 | dense w=3 | 27.58 | 531 | 44.8 | 135.1 | 27.6 | 146.58 | -85.77 | 89.6 | 236.2 | -165.7 |  |
| 5 | 6 | sparse cols^2 w | 27.58 | 531 | 44.8 | 110.2 | 27.6 | 121.65 | -60.85 | 59.0 | 180.6 | -110.2 |  |
| 5 | 6 | sparse cols x nnz(M_D) | 27.58 | 531 | 44.8 | 99.0 | 27.6 | 110.46 | -49.65 | 59.0 | 169.4 | -99.0 |  |
| 6 | 3 | dense w=2 | 23.42 | 664 | 25.5 | 51.8 | 23.4 | 59.11 | 1.70 BEATS | 51.1 | 110.2 | -39.8 | non-refuting |
| 6 | 3 | dense w=2.37 | 23.42 | 664 | 25.5 | 61.2 | 23.4 | 68.56 | -7.75 | 51.1 | 119.6 | -49.2 | non-refuting |
| 6 | 3 | dense w=3 | 23.42 | 664 | 25.5 | 77.3 | 23.4 | 84.65 | -23.84 | 51.1 | 135.7 | -65.3 | non-refuting |
| 6 | 3 | sparse cols^2 w | 23.42 | 664 | 25.5 | 72.6 | 23.4 | 79.95 | -19.14 | 34.9 | 114.8 | -44.4 | non-refuting |
| 6 | 3 | sparse cols x nnz(M_D) | 23.42 | 664 | 25.5 | 56.4 | 23.4 | 63.76 | -2.95 | 34.9 | 98.6 | -28.2 | non-refuting |
| 6 | 4 | dense w=2 | 23.42 | 664 | 32.9 | 66.5 | 23.4 | 73.85 | -13.04 | 65.8 | 139.7 | -69.3 |  |
| 6 | 4 | dense w=2.37 | 23.42 | 664 | 32.9 | 78.7 | 23.4 | 86.03 | -25.22 | 65.8 | 151.9 | -81.4 |  |
| 6 | 4 | dense w=3 | 23.42 | 664 | 32.9 | 99.5 | 23.4 | 106.77 | -45.96 | 65.8 | 172.6 | -102.2 |  |
| 6 | 4 | sparse cols^2 w | 23.42 | 664 | 32.9 | 87.4 | 23.4 | 94.70 | -33.89 | 44.6 | 139.3 | -68.9 |  |
| 6 | 4 | sparse cols x nnz(M_D) | 23.42 | 664 | 32.9 | 73.2 | 23.4 | 80.51 | -19.70 | 44.6 | 125.1 | -54.7 |  |
| 6 | 5 | dense w=2 | 23.42 | 664 | 40.0 | 80.6 | 23.4 | 87.95 | -27.14 | 79.9 | 167.9 | -97.4 |  |
| 6 | 5 | dense w=2.37 | 23.42 | 664 | 40.0 | 95.4 | 23.4 | 102.73 | -41.92 | 79.9 | 182.7 | -112.2 |  |
| 6 | 5 | dense w=3 | 23.42 | 664 | 40.0 | 120.6 | 23.4 | 127.91 | -67.10 | 79.9 | 207.8 | -137.4 |  |
| 6 | 5 | sparse cols^2 w | 23.42 | 664 | 40.0 | 101.5 | 23.4 | 108.79 | -47.98 | 53.3 | 162.1 | -91.6 |  |
| 6 | 5 | sparse cols x nnz(M_D) | 23.42 | 664 | 40.0 | 88.6 | 23.4 | 95.94 | -35.13 | 53.3 | 149.2 | -78.8 |  |
| 6 | 6 | dense w=2 | 23.42 | 664 | 46.7 | 94.2 | 23.4 | 101.51 | -40.70 | 93.5 | 195.0 | -124.6 |  |
| 6 | 6 | dense w=2.37 | 23.42 | 664 | 46.7 | 111.5 | 23.4 | 118.81 | -58.00 | 93.5 | 212.3 | -141.9 |  |
| 6 | 6 | dense w=3 | 23.42 | 664 | 46.7 | 140.9 | 23.4 | 148.26 | -87.45 | 93.5 | 241.7 | -171.3 |  |
| 6 | 6 | sparse cols^2 w | 23.42 | 664 | 46.7 | 115.0 | 23.4 | 122.36 | -61.55 | 61.3 | 183.6 | -113.2 |  |
| 6 | 6 | sparse cols x nnz(M_D) | 23.42 | 664 | 46.7 | 103.2 | 23.4 | 110.51 | -49.70 | 61.3 | 171.8 | -101.4 |  |
| 8 | 3 | dense w=2 | 18.29 | 932 | 27.0 | 54.7 | 18.3 | 56.91 | 3.90 BEATS | 54.0 | 110.9 | -40.5 | non-refuting |
| 8 | 3 | dense w=2.37 | 18.29 | 932 | 27.0 | 64.7 | 18.3 | 66.91 | -6.10 | 54.0 | 120.9 | -50.5 | non-refuting |
| 8 | 3 | dense w=3 | 18.29 | 932 | 27.0 | 81.7 | 18.3 | 83.92 | -23.11 | 54.0 | 137.9 | -67.5 | non-refuting |
| 8 | 3 | sparse cols^2 w | 18.29 | 932 | 27.0 | 77.0 | 18.3 | 79.22 | -18.41 | 36.9 | 116.1 | -45.7 | non-refuting |
| 8 | 3 | sparse cols x nnz(M_D) | 18.29 | 932 | 27.0 | 59.9 | 18.3 | 62.05 | -1.24 | 36.9 | 99.0 | -28.5 | non-refuting |
| 8 | 4 | dense w=2 | 18.29 | 932 | 34.9 | 70.4 | 18.3 | 72.64 | -11.83 | 69.7 | 142.4 | -71.9 |  |
| 8 | 4 | dense w=2.37 | 18.29 | 932 | 34.9 | 83.3 | 18.3 | 85.54 | -24.73 | 69.7 | 155.3 | -84.9 |  |
| 8 | 4 | dense w=3 | 18.29 | 932 | 34.9 | 105.3 | 18.3 | 107.51 | -46.70 | 69.7 | 177.2 | -106.8 |  |
| 8 | 4 | sparse cols^2 w | 18.29 | 932 | 34.9 | 92.8 | 18.3 | 94.94 | -34.13 | 47.1 | 142.1 | -71.7 |  |
| 8 | 4 | sparse cols x nnz(M_D) | 18.29 | 932 | 34.9 | 77.6 | 18.3 | 79.78 | -18.97 | 47.1 | 126.9 | -56.5 |  |
| 8 | 5 | dense w=2 | 18.29 | 932 | 42.4 | 85.5 | 18.3 | 87.71 | -26.90 | 84.8 | 172.5 | -102.1 |  |
| 8 | 5 | dense w=2.37 | 18.29 | 932 | 42.4 | 101.2 | 18.3 | 103.40 | -42.59 | 84.8 | 188.2 | -117.8 |  |
| 8 | 5 | dense w=3 | 18.29 | 932 | 42.4 | 127.9 | 18.3 | 130.12 | -69.31 | 84.8 | 214.9 | -144.5 |  |
| 8 | 5 | sparse cols^2 w | 18.29 | 932 | 42.4 | 107.8 | 18.3 | 110.02 | -49.21 | 56.3 | 166.3 | -95.9 |  |
| 8 | 5 | sparse cols x nnz(M_D) | 18.29 | 932 | 42.4 | 94.0 | 18.3 | 96.18 | -35.37 | 56.3 | 152.5 | -82.0 |  |
| 8 | 6 | dense w=2 | 18.29 | 932 | 49.7 | 100.1 | 18.3 | 102.26 | -41.45 | 99.4 | 201.6 | -131.2 |  |
| 8 | 6 | dense w=2.37 | 18.29 | 932 | 49.7 | 118.5 | 18.3 | 120.64 | -59.83 | 99.4 | 220.0 | -149.6 |  |
| 8 | 6 | dense w=3 | 18.29 | 932 | 49.7 | 149.8 | 18.3 | 151.94 | -91.13 | 99.4 | 251.3 | -180.9 |  |
| 8 | 6 | sparse cols^2 w | 18.29 | 932 | 49.7 | 122.4 | 18.3 | 124.57 | -63.76 | 64.8 | 189.4 | -118.9 |  |
| 8 | 6 | sparse cols x nnz(M_D) | 18.29 | 932 | 49.7 | 109.5 | 18.3 | 111.73 | -50.93 | 64.8 | 176.5 | -106.1 |  |
| 10 | 3 | dense w=2 | 15.28 | 1201 | 28.1 | 56.9 | 15.3 | 56.09 | 4.71 BEATS | 56.2 | 112.3 | -41.9 | non-refuting |
| 10 | 3 | dense w=2.37 | 15.28 | 1201 | 28.1 | 67.3 | 15.3 | 66.49 | -5.68 | 56.2 | 122.7 | -52.3 | non-refuting |
| 10 | 3 | dense w=3 | 15.28 | 1201 | 28.1 | 85.0 | 15.3 | 84.20 | -23.39 | 56.2 | 140.4 | -70.0 | non-refuting |
| 10 | 3 | sparse cols^2 w | 15.28 | 1201 | 28.1 | 80.3 | 15.3 | 79.50 | -18.69 | 38.4 | 117.9 | -47.5 | non-refuting |
| 10 | 3 | sparse cols x nnz(M_D) | 15.28 | 1201 | 28.1 | 62.4 | 15.3 | 61.60 | -0.79 | 38.4 | 100.0 | -29.6 | non-refuting |
| 10 | 4 | dense w=2 | 15.28 | 1201 | 36.3 | 73.4 | 15.3 | 72.55 | -11.74 | 72.7 | 145.2 | -74.8 |  |
| 10 | 4 | dense w=2.37 | 15.28 | 1201 | 36.3 | 86.8 | 15.3 | 85.99 | -25.18 | 72.7 | 158.7 | -88.2 |  |
| 10 | 4 | dense w=3 | 15.28 | 1201 | 36.3 | 109.7 | 15.3 | 108.88 | -48.07 | 72.7 | 181.5 | -111.1 |  |
| 10 | 4 | sparse cols^2 w | 15.28 | 1201 | 36.3 | 96.8 | 15.3 | 95.95 | -35.14 | 49.0 | 145.0 | -74.5 |  |
| 10 | 4 | sparse cols x nnz(M_D) | 15.28 | 1201 | 36.3 | 80.9 | 15.3 | 80.06 | -19.25 | 49.0 | 129.1 | -58.6 |  |
| 10 | 5 | dense w=2 | 15.28 | 1201 | 44.2 | 89.2 | 15.3 | 88.36 | -27.55 | 88.5 | 176.8 | -106.4 |  |
| 10 | 5 | dense w=2.37 | 15.28 | 1201 | 44.2 | 105.5 | 15.3 | 104.73 | -43.92 | 88.5 | 193.2 | -122.8 |  |
| 10 | 5 | dense w=3 | 15.28 | 1201 | 44.2 | 133.4 | 15.3 | 132.59 | -71.78 | 88.5 | 221.1 | -150.6 |  |
| 10 | 5 | sparse cols^2 w | 15.28 | 1201 | 44.2 | 112.6 | 15.3 | 111.76 | -50.95 | 58.5 | 170.3 | -99.9 |  |
| 10 | 5 | sparse cols x nnz(M_D) | 15.28 | 1201 | 44.2 | 98.0 | 15.3 | 97.19 | -36.38 | 58.5 | 155.7 | -85.3 |  |
| 10 | 6 | dense w=2 | 15.28 | 1201 | 51.9 | 104.5 | 15.3 | 103.64 | -42.83 | 103.8 | 207.4 | -137.0 |  |
| 10 | 6 | dense w=2.37 | 15.28 | 1201 | 51.9 | 123.7 | 15.3 | 122.83 | -62.02 | 103.8 | 226.6 | -156.2 |  |
| 10 | 6 | dense w=3 | 15.28 | 1201 | 51.9 | 156.3 | 15.3 | 155.51 | -94.70 | 103.8 | 259.3 | -188.8 |  |
| 10 | 6 | sparse cols^2 w | 15.28 | 1201 | 51.9 | 127.9 | 15.3 | 127.04 | -66.23 | 67.4 | 194.5 | -124.0 |  |
| 10 | 6 | sparse cols x nnz(M_D) | 15.28 | 1201 | 51.9 | 114.3 | 15.3 | 113.47 | -52.66 | 67.4 | 180.9 | -110.5 |  |
| 12 | 3 | dense w=2 | 13.32 | 1470 | 29.0 | 58.7 | 13.3 | 55.89 | 4.92 BEATS | 58.0 | 113.8 | -43.4 | non-refuting |
| 12 | 3 | dense w=2.37 | 13.32 | 1470 | 29.0 | 69.4 | 13.3 | 66.61 | -5.80 | 58.0 | 124.6 | -54.1 | non-refuting |
| 12 | 3 | dense w=3 | 13.32 | 1470 | 29.0 | 87.6 | 13.3 | 84.86 | -24.06 | 58.0 | 142.8 | -72.4 | non-refuting |
| 12 | 3 | sparse cols^2 w | 13.32 | 1470 | 29.0 | 82.9 | 13.3 | 80.16 | -19.35 | 39.6 | 119.8 | -49.4 | non-refuting |
| 12 | 3 | sparse cols x nnz(M_D) | 13.32 | 1470 | 29.0 | 64.5 | 13.3 | 61.68 | -0.87 | 39.6 | 101.3 | -30.9 | non-refuting |
| 12 | 4 | dense w=2 | 13.32 | 1470 | 37.5 | 75.7 | 13.3 | 72.92 | -12.12 | 75.0 | 147.9 | -77.5 |  |
| 12 | 4 | dense w=2.37 | 13.32 | 1470 | 37.5 | 89.6 | 13.3 | 86.80 | -25.99 | 75.0 | 161.8 | -91.4 |  |
| 12 | 4 | dense w=3 | 13.32 | 1470 | 37.5 | 113.2 | 13.3 | 110.42 | -49.61 | 75.0 | 185.4 | -115.0 |  |
| 12 | 4 | sparse cols^2 w | 13.32 | 1470 | 37.5 | 100.0 | 13.3 | 97.20 | -36.39 | 50.5 | 147.7 | -77.3 |  |
| 12 | 4 | sparse cols x nnz(M_D) | 13.32 | 1470 | 37.5 | 83.5 | 13.3 | 80.72 | -19.91 | 50.5 | 131.2 | -60.8 |  |
| 12 | 5 | dense w=2 | 13.32 | 1470 | 45.7 | 92.1 | 13.3 | 89.32 | -28.51 | 91.4 | 180.7 | -110.3 |  |
| 12 | 5 | dense w=2.37 | 13.32 | 1470 | 45.7 | 109.0 | 13.3 | 106.22 | -45.42 | 91.4 | 197.6 | -127.2 |  |
| 12 | 5 | dense w=3 | 13.32 | 1470 | 45.7 | 137.8 | 13.3 | 135.01 | -74.20 | 91.4 | 226.4 | -156.0 |  |
| 12 | 5 | sparse cols^2 w | 13.32 | 1470 | 45.7 | 116.4 | 13.3 | 113.60 | -52.79 | 60.3 | 173.9 | -103.5 |  |
| 12 | 5 | sparse cols x nnz(M_D) | 13.32 | 1470 | 45.7 | 101.2 | 13.3 | 98.44 | -37.63 | 60.3 | 158.8 | -88.3 |  |
| 12 | 6 | dense w=2 | 13.32 | 1470 | 53.6 | 108.0 | 13.3 | 105.18 | -44.37 | 107.3 | 212.4 | -142.0 |  |
| 12 | 6 | dense w=2.37 | 13.32 | 1470 | 53.6 | 127.8 | 13.3 | 125.02 | -64.22 | 107.3 | 232.3 | -161.9 |  |
| 12 | 6 | dense w=3 | 13.32 | 1470 | 53.6 | 161.6 | 13.3 | 158.81 | -98.00 | 107.3 | 266.1 | -195.6 |  |
| 12 | 6 | sparse cols^2 w | 13.32 | 1470 | 53.6 | 132.2 | 13.3 | 129.46 | -68.65 | 69.5 | 199.0 | -128.5 |  |
| 12 | 6 | sparse cols x nnz(M_D) | 13.32 | 1470 | 53.6 | 118.1 | 13.3 | 115.31 | -54.50 | 69.5 | 184.8 | -114.4 |  |
| 16 | 3 | dense w=2 | 10.95 | 2009 | 30.3 | 61.4 | 11.0 | 56.22 | 4.58 BEATS | 60.7 | 116.9 | -46.5 | non-refuting |
| 16 | 3 | dense w=2.37 | 10.95 | 2009 | 30.3 | 72.6 | 11.0 | 67.45 | -6.64 | 60.7 | 128.1 | -57.7 | non-refuting |
| 16 | 3 | dense w=3 | 10.95 | 2009 | 30.3 | 91.7 | 11.0 | 86.56 | -25.75 | 60.7 | 147.2 | -76.8 | non-refuting |
| 16 | 3 | sparse cols^2 w | 10.95 | 2009 | 30.3 | 87.0 | 11.0 | 81.86 | -21.05 | 41.5 | 123.4 | -52.9 | non-refuting |
| 16 | 3 | sparse cols x nnz(M_D) | 10.95 | 2009 | 30.3 | 67.6 | 11.0 | 62.46 | -1.66 | 41.5 | 104.0 | -33.5 | non-refuting |
| 16 | 4 | dense w=2 | 10.95 | 2009 | 39.3 | 79.3 | 11.0 | 74.17 | -13.36 | 78.6 | 152.8 | -82.3 |  |
| 16 | 4 | dense w=2.37 | 10.95 | 2009 | 39.3 | 93.9 | 11.0 | 88.71 | -27.90 | 78.6 | 167.3 | -96.9 |  |
| 16 | 4 | dense w=3 | 10.95 | 2009 | 39.3 | 118.6 | 11.0 | 113.47 | -52.66 | 78.6 | 192.1 | -121.6 |  |
| 16 | 4 | sparse cols^2 w | 10.95 | 2009 | 39.3 | 104.9 | 11.0 | 99.80 | -38.99 | 52.8 | 152.6 | -82.2 |  |
| 16 | 4 | sparse cols x nnz(M_D) | 10.95 | 2009 | 39.3 | 87.6 | 11.0 | 82.41 | -21.60 | 52.8 | 135.3 | -64.8 |  |
| 16 | 5 | dense w=2 | 10.95 | 2009 | 48.0 | 96.6 | 11.0 | 91.46 | -30.65 | 95.9 | 187.4 | -116.9 |  |
| 16 | 5 | dense w=2.37 | 10.95 | 2009 | 48.0 | 114.4 | 11.0 | 109.21 | -48.40 | 95.9 | 205.1 | -134.7 |  |
| 16 | 5 | dense w=3 | 10.95 | 2009 | 48.0 | 144.6 | 11.0 | 139.42 | -78.61 | 95.9 | 235.3 | -164.9 |  |
| 16 | 5 | sparse cols^2 w | 10.95 | 2009 | 48.0 | 122.2 | 11.0 | 117.10 | -56.29 | 63.1 | 180.2 | -109.8 |  |
| 16 | 5 | sparse cols x nnz(M_D) | 10.95 | 2009 | 48.0 | 106.2 | 11.0 | 101.03 | -40.22 | 63.1 | 164.1 | -93.7 |  |
| 16 | 6 | dense w=2 | 10.95 | 2009 | 56.3 | 113.4 | 11.0 | 108.23 | -47.42 | 112.7 | 220.9 | -150.5 |  |
| 16 | 6 | dense w=2.37 | 10.95 | 2009 | 56.3 | 134.2 | 11.0 | 129.08 | -68.27 | 112.7 | 241.7 | -171.3 |  |
| 16 | 6 | dense w=3 | 10.95 | 2009 | 56.3 | 169.7 | 11.0 | 164.57 | -103.76 | 112.7 | 277.2 | -206.8 |  |
| 16 | 6 | sparse cols^2 w | 10.95 | 2009 | 56.3 | 139.0 | 11.0 | 133.86 | -73.06 | 72.7 | 206.6 | -136.2 |  |
| 16 | 6 | sparse cols x nnz(M_D) | 10.95 | 2009 | 56.3 | 123.9 | 11.0 | 118.80 | -57.99 | 72.7 | 191.5 | -121.1 |  |

### Presentation: block

| m | D | elim | l* | N_var | log2 cols | per-attempt bit-ops | log2 attempts | T (log2 rho steps) | margin vs rho | mem bits | T x M | margin vs 6nW | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 3 | dense w=2 | 40.04 | 302 | 22.1 | 44.3 | 53.5 | 82.67 | -21.86 | 46.9 | 129.6 | -59.2 | non-refuting |
| 3 | 3 | dense w=2.37 | 42.10 | 304 | 22.2 | 52.5 | 49.4 | 86.80 | -25.99 | 49.1 | 135.9 | -65.5 | non-refuting |
| 3 | 3 | dense w=3 | 44.53 | 307 | 22.2 | 67.3 | 44.5 | 95.76 | -34.95 | 51.6 | 147.4 | -76.9 | non-refuting |
| 3 | 3 | sparse cols^2 w | 44.44 | 306 | 22.2 | 62.5 | 44.7 | 91.84 | -31.03 | 51.5 | 143.3 | -72.9 | non-refuting |
| 3 | 3 | sparse cols x nnz(M_D) | 40.62 | 303 | 22.1 | 46.6 | 52.3 | 83.84 | -23.03 | 47.6 | 131.4 | -61.0 | non-refuting |
| 3 | 4 | dense w=2 | 43.17 | 305 | 28.4 | 56.9 | 47.2 | 89.00 | -28.19 | 56.8 | 145.8 | -75.4 |  |
| 3 | 4 | dense w=2.37 | 44.53 | 307 | 28.4 | 68.1 | 44.5 | 96.57 | -35.77 | 56.9 | 153.5 | -83.0 |  |
| 3 | 4 | dense w=3 | 44.53 | 307 | 28.4 | 86.0 | 44.5 | 114.47 | -53.66 | 56.9 | 171.4 | -100.9 |  |
| 3 | 4 | sparse cols^2 w | 44.53 | 307 | 28.4 | 75.1 | 44.5 | 103.52 | -42.71 | 51.6 | 155.1 | -84.7 |  |
| 3 | 4 | sparse cols x nnz(M_D) | 44.25 | 306 | 28.4 | 61.7 | 45.1 | 91.44 | -30.63 | 51.3 | 142.7 | -72.3 |  |
| 3 | 5 | dense w=2 | 44.53 | 307 | 34.4 | 69.4 | 44.5 | 97.88 | -37.07 | 68.7 | 166.6 | -96.2 |  |
| 3 | 5 | dense w=2.37 | 44.53 | 307 | 34.4 | 82.2 | 44.5 | 110.59 | -49.78 | 68.7 | 179.3 | -108.9 |  |
| 3 | 5 | dense w=3 | 44.53 | 307 | 34.4 | 103.8 | 44.5 | 132.24 | -71.43 | 68.7 | 201.0 | -130.6 |  |
| 3 | 5 | sparse cols^2 w | 44.53 | 307 | 34.4 | 86.9 | 44.5 | 115.37 | -54.56 | 51.6 | 167.0 | -96.5 |  |
| 3 | 5 | sparse cols x nnz(M_D) | 44.53 | 307 | 34.4 | 75.1 | 44.5 | 103.56 | -42.75 | 51.6 | 155.1 | -84.7 |  |
| 3 | 6 | dense w=2 | 44.53 | 307 | 40.0 | 80.8 | 44.5 | 109.19 | -48.38 | 80.1 | 189.2 | -118.8 |  |
| 3 | 6 | dense w=2.37 | 44.53 | 307 | 40.0 | 95.6 | 44.5 | 123.99 | -63.19 | 80.1 | 204.0 | -133.6 |  |
| 3 | 6 | dense w=3 | 44.53 | 307 | 40.0 | 120.8 | 44.5 | 149.21 | -88.40 | 80.1 | 229.3 | -158.8 |  |
| 3 | 6 | sparse cols^2 w | 44.53 | 307 | 40.0 | 98.3 | 44.5 | 126.68 | -65.87 | 52.0 | 178.7 | -108.3 |  |
| 3 | 6 | sparse cols x nnz(M_D) | 44.53 | 307 | 40.0 | 87.5 | 44.5 | 115.88 | -55.07 | 52.0 | 167.9 | -97.5 |  |
| 4 | 3 | dense w=2 | 32.62 | 295 | 22.0 | 45.1 | 37.7 | 68.00 | -7.19 | 44.0 | 112.0 | -41.6 | non-refuting |
| 4 | 3 | dense w=2.37 | 33.90 | 296 | 22.0 | 53.9 | 33.9 | 72.07 | -11.27 | 44.1 | 116.2 | -45.7 | non-refuting |
| 4 | 3 | dense w=3 | 33.90 | 296 | 22.0 | 67.8 | 33.9 | 85.63 | -24.82 | 44.1 | 129.7 | -59.3 | non-refuting |
| 4 | 3 | sparse cols^2 w | 33.90 | 296 | 22.0 | 63.1 | 33.9 | 80.93 | -20.12 | 41.0 | 121.9 | -51.5 | non-refuting |
| 4 | 3 | sparse cols x nnz(M_D) | 33.08 | 295 | 22.0 | 47.5 | 36.3 | 68.98 | -8.17 | 40.1 | 109.1 | -38.7 | non-refuting |
| 4 | 4 | dense w=2 | 33.90 | 296 | 28.2 | 58.2 | 33.9 | 76.01 | -15.20 | 56.5 | 132.5 | -62.1 |  |
| 4 | 4 | dense w=2.37 | 33.90 | 296 | 28.2 | 68.6 | 33.9 | 86.43 | -25.63 | 56.5 | 142.9 | -72.5 |  |
| 4 | 4 | dense w=3 | 33.90 | 296 | 28.2 | 86.4 | 33.9 | 104.23 | -43.42 | 56.5 | 160.7 | -90.3 |  |
| 4 | 4 | sparse cols^2 w | 33.90 | 296 | 28.2 | 75.5 | 33.9 | 93.33 | -32.52 | 41.0 | 134.3 | -63.9 |  |
| 4 | 4 | sparse cols x nnz(M_D) | 33.90 | 296 | 28.2 | 62.5 | 33.9 | 80.33 | -19.52 | 41.0 | 121.3 | -50.9 |  |
| 4 | 5 | dense w=2 | 33.90 | 296 | 34.1 | 69.9 | 33.9 | 87.73 | -26.92 | 68.2 | 156.0 | -85.5 |  |
| 4 | 5 | dense w=2.37 | 33.90 | 296 | 34.1 | 82.6 | 33.9 | 100.35 | -39.54 | 68.2 | 168.6 | -98.2 |  |
| 4 | 5 | dense w=3 | 33.90 | 296 | 34.1 | 104.0 | 33.9 | 121.84 | -61.03 | 68.2 | 190.1 | -119.6 |  |
| 4 | 5 | sparse cols^2 w | 33.90 | 296 | 34.1 | 87.3 | 33.9 | 105.07 | -44.26 | 44.9 | 150.0 | -79.5 |  |
| 4 | 5 | sparse cols x nnz(M_D) | 33.90 | 296 | 34.1 | 75.6 | 33.9 | 93.41 | -32.61 | 44.9 | 138.3 | -67.9 |  |
| 4 | 6 | dense w=2 | 33.90 | 296 | 39.7 | 81.1 | 33.9 | 98.94 | -38.13 | 79.4 | 178.4 | -107.9 |  |
| 4 | 6 | dense w=2.37 | 33.90 | 296 | 39.7 | 95.8 | 33.9 | 113.64 | -52.83 | 79.4 | 193.1 | -122.6 |  |
| 4 | 6 | dense w=3 | 33.90 | 296 | 39.7 | 120.9 | 33.9 | 138.66 | -77.85 | 79.4 | 218.1 | -147.7 |  |
| 4 | 6 | sparse cols^2 w | 33.90 | 296 | 39.7 | 98.5 | 33.9 | 116.28 | -55.47 | 51.7 | 168.0 | -97.6 |  |
| 4 | 6 | sparse cols x nnz(M_D) | 33.90 | 296 | 39.7 | 87.8 | 33.9 | 105.64 | -44.83 | 51.7 | 157.4 | -86.9 |  |
| 5 | 3 | dense w=2 | 27.58 | 290 | 21.9 | 46.2 | 27.6 | 58.58 | 2.23 BEATS | 43.9 | 102.5 | -32.1 | non-refuting |
| 5 | 3 | dense w=2.37 | 27.58 | 290 | 21.9 | 54.3 | 27.6 | 65.80 | -4.99 | 43.9 | 109.7 | -39.3 | non-refuting |
| 5 | 3 | dense w=3 | 27.58 | 290 | 21.9 | 68.1 | 27.6 | 79.62 | -18.81 | 43.9 | 123.5 | -53.1 | non-refuting |
| 5 | 3 | sparse cols^2 w | 27.58 | 290 | 21.9 | 63.4 | 27.6 | 74.92 | -14.11 | 34.7 | 109.6 | -39.2 | non-refuting |
| 5 | 3 | sparse cols x nnz(M_D) | 27.58 | 290 | 21.9 | 48.5 | 27.6 | 60.24 | 0.57 BEATS | 34.7 | 94.9 | -24.5 | non-refuting |
| 5 | 4 | dense w=2 | 27.58 | 290 | 28.1 | 58.5 | 27.6 | 70.01 | -9.20 | 56.2 | 126.2 | -55.8 |  |
| 5 | 4 | dense w=2.37 | 27.58 | 290 | 28.1 | 68.9 | 27.6 | 80.41 | -19.60 | 56.2 | 136.6 | -66.2 |  |
| 5 | 4 | dense w=3 | 27.58 | 290 | 28.1 | 86.6 | 27.6 | 98.12 | -37.31 | 56.2 | 154.4 | -83.9 |  |
| 5 | 4 | sparse cols^2 w | 27.58 | 290 | 28.1 | 75.8 | 27.6 | 87.25 | -26.45 | 37.3 | 124.5 | -54.1 |  |
| 5 | 4 | sparse cols x nnz(M_D) | 27.58 | 290 | 28.1 | 62.9 | 27.6 | 74.35 | -13.54 | 37.3 | 111.6 | -41.2 |  |
| 5 | 5 | dense w=2 | 27.58 | 290 | 34.0 | 70.2 | 27.6 | 81.69 | -20.88 | 67.9 | 149.6 | -79.2 |  |
| 5 | 5 | dense w=2.37 | 27.58 | 290 | 34.0 | 82.8 | 27.6 | 94.25 | -33.44 | 67.9 | 162.2 | -91.7 |  |
| 5 | 5 | dense w=3 | 27.58 | 290 | 34.0 | 104.2 | 27.6 | 115.65 | -54.84 | 67.9 | 183.6 | -113.1 |  |
| 5 | 5 | sparse cols^2 w | 27.58 | 290 | 34.0 | 87.5 | 27.6 | 98.94 | -38.13 | 44.7 | 143.7 | -73.2 |  |
| 5 | 5 | sparse cols x nnz(M_D) | 27.58 | 290 | 34.0 | 75.9 | 27.6 | 87.37 | -26.56 | 44.7 | 132.1 | -61.7 |  |
| 5 | 6 | dense w=2 | 27.58 | 290 | 39.5 | 81.4 | 27.6 | 92.83 | -32.03 | 79.1 | 171.9 | -101.5 |  |
| 5 | 6 | dense w=2.37 | 27.58 | 290 | 39.5 | 96.0 | 27.6 | 107.46 | -46.65 | 79.1 | 186.5 | -116.1 |  |
| 5 | 6 | dense w=3 | 27.58 | 290 | 39.5 | 120.9 | 27.6 | 132.36 | -71.56 | 79.1 | 211.4 | -141.0 |  |
| 5 | 6 | sparse cols^2 w | 27.58 | 290 | 39.5 | 98.6 | 27.6 | 110.08 | -49.27 | 51.5 | 161.6 | -91.2 |  |
| 5 | 6 | sparse cols x nnz(M_D) | 27.58 | 290 | 39.5 | 88.1 | 27.6 | 99.53 | -38.72 | 51.5 | 151.1 | -80.6 |  |
| 6 | 3 | dense w=2 | 23.42 | 285 | 21.9 | 46.5 | 23.4 | 53.86 | 6.95 BEATS | 43.8 | 97.6 | -27.2 | non-refuting |
| 6 | 3 | dense w=2.37 | 23.42 | 285 | 21.9 | 54.6 | 23.4 | 61.89 | -1.08 | 43.8 | 105.7 | -35.2 | non-refuting |
| 6 | 3 | dense w=3 | 23.42 | 285 | 21.9 | 68.4 | 23.4 | 75.68 | -14.87 | 43.8 | 119.5 | -49.0 | non-refuting |
| 6 | 3 | sparse cols^2 w | 23.42 | 285 | 21.9 | 63.7 | 23.4 | 70.98 | -10.17 | 30.5 | 101.5 | -31.1 | non-refuting |
| 6 | 3 | sparse cols x nnz(M_D) | 23.42 | 285 | 21.9 | 48.8 | 23.4 | 56.14 | 4.67 BEATS | 30.5 | 86.7 | -16.3 | non-refuting |
| 6 | 4 | dense w=2 | 23.42 | 285 | 28.0 | 58.8 | 23.4 | 66.09 | -5.28 | 56.1 | 122.2 | -51.7 |  |
| 6 | 4 | dense w=2.37 | 23.42 | 285 | 28.0 | 69.1 | 23.4 | 76.46 | -15.65 | 56.1 | 132.5 | -62.1 |  |
| 6 | 4 | dense w=3 | 23.42 | 285 | 28.0 | 86.8 | 23.4 | 94.12 | -33.31 | 56.1 | 150.2 | -79.8 |  |
| 6 | 4 | sparse cols^2 w | 23.42 | 285 | 28.0 | 76.0 | 23.4 | 83.27 | -22.46 | 37.2 | 120.5 | -50.0 |  |
| 6 | 4 | sparse cols x nnz(M_D) | 23.42 | 285 | 28.0 | 63.1 | 23.4 | 70.44 | -9.63 | 37.2 | 107.6 | -37.2 |  |
| 6 | 5 | dense w=2 | 23.42 | 285 | 33.9 | 70.4 | 23.4 | 77.73 | -16.92 | 67.7 | 145.4 | -75.0 |  |
| 6 | 5 | dense w=2.37 | 23.42 | 285 | 33.9 | 82.9 | 23.4 | 90.25 | -29.44 | 67.7 | 158.0 | -87.5 |  |
| 6 | 5 | dense w=3 | 23.42 | 285 | 33.9 | 104.3 | 23.4 | 111.58 | -50.77 | 67.7 | 179.3 | -108.9 |  |
| 6 | 5 | sparse cols^2 w | 23.42 | 285 | 33.9 | 87.6 | 23.4 | 94.91 | -34.10 | 44.6 | 139.5 | -69.1 |  |
| 6 | 5 | sparse cols x nnz(M_D) | 23.42 | 285 | 33.9 | 76.1 | 23.4 | 83.41 | -22.60 | 44.6 | 128.0 | -57.6 |  |
| 6 | 6 | dense w=2 | 23.42 | 285 | 39.4 | 81.5 | 23.4 | 88.83 | -28.02 | 78.8 | 167.6 | -97.2 |  |
| 6 | 6 | dense w=2.37 | 23.42 | 285 | 39.4 | 96.1 | 23.4 | 103.41 | -42.60 | 78.8 | 182.2 | -111.8 |  |
| 6 | 6 | dense w=3 | 23.42 | 285 | 39.4 | 120.9 | 23.4 | 128.24 | -67.43 | 78.8 | 207.0 | -136.6 |  |
| 6 | 6 | sparse cols^2 w | 23.42 | 285 | 39.4 | 98.7 | 23.4 | 106.02 | -45.21 | 51.4 | 157.4 | -87.0 |  |
| 6 | 6 | sparse cols x nnz(M_D) | 23.42 | 285 | 39.4 | 88.2 | 23.4 | 95.53 | -34.72 | 51.4 | 146.9 | -76.5 |  |
| 8 | 3 | dense w=2 | 18.29 | 280 | 21.8 | 46.9 | 18.3 | 49.10 | 11.71 BEATS | 43.6 | 92.7 | -22.3 | non-refuting |
| 8 | 3 | dense w=2.37 | 18.29 | 280 | 21.8 | 55.0 | 18.3 | 57.16 | 3.65 BEATS | 43.6 | 100.8 | -30.4 | non-refuting |
| 8 | 3 | dense w=3 | 18.29 | 280 | 21.8 | 68.7 | 18.3 | 70.90 | -10.09 | 43.6 | 114.5 | -44.1 | non-refuting |
| 8 | 3 | sparse cols^2 w | 18.29 | 280 | 21.8 | 64.0 | 18.3 | 66.20 | -5.39 | 28.6 | 94.8 | -24.4 | non-refuting |
| 8 | 3 | sparse cols x nnz(M_D) | 18.29 | 280 | 21.8 | 49.2 | 18.3 | 51.43 | 9.38 BEATS | 28.6 | 80.0 | -9.6 | non-refuting |
| 8 | 4 | dense w=2 | 18.29 | 280 | 27.9 | 59.1 | 18.3 | 61.34 | -0.53 | 55.9 | 117.2 | -46.8 |  |
| 8 | 4 | dense w=2.37 | 18.29 | 280 | 27.9 | 69.5 | 18.3 | 71.67 | -10.86 | 55.9 | 127.5 | -57.1 |  |
| 8 | 4 | dense w=3 | 18.29 | 280 | 27.9 | 87.1 | 18.3 | 89.26 | -28.45 | 55.9 | 145.1 | -74.7 |  |
| 8 | 4 | sparse cols^2 w | 18.29 | 280 | 27.9 | 76.3 | 18.3 | 78.44 | -17.63 | 37.1 | 115.5 | -45.1 |  |
| 8 | 4 | sparse cols x nnz(M_D) | 18.29 | 280 | 27.9 | 63.5 | 18.3 | 65.68 | -4.87 | 37.1 | 102.8 | -32.3 |  |
| 8 | 5 | dense w=2 | 18.29 | 280 | 33.7 | 70.7 | 18.3 | 72.92 | -12.11 | 67.4 | 140.4 | -69.9 |  |
| 8 | 5 | dense w=2.37 | 18.29 | 280 | 33.7 | 83.2 | 18.3 | 85.40 | -24.59 | 67.4 | 152.8 | -82.4 |  |
| 8 | 5 | dense w=3 | 18.29 | 280 | 33.7 | 104.5 | 18.3 | 106.64 | -45.83 | 67.4 | 174.1 | -103.7 |  |
| 8 | 5 | sparse cols^2 w | 18.29 | 280 | 33.7 | 87.8 | 18.3 | 90.03 | -29.22 | 44.5 | 134.5 | -64.1 |  |
| 8 | 5 | sparse cols x nnz(M_D) | 18.29 | 280 | 33.7 | 76.4 | 18.3 | 78.61 | -17.80 | 44.5 | 123.1 | -52.7 |  |
| 8 | 6 | dense w=2 | 18.29 | 280 | 39.2 | 81.8 | 18.3 | 83.97 | -23.16 | 78.5 | 162.5 | -92.0 |  |
| 8 | 6 | dense w=2.37 | 18.29 | 280 | 39.2 | 96.3 | 18.3 | 98.49 | -37.68 | 78.5 | 177.0 | -106.6 |  |
| 8 | 6 | dense w=3 | 18.29 | 280 | 39.2 | 121.0 | 18.3 | 123.22 | -62.41 | 78.5 | 201.7 | -131.3 |  |
| 8 | 6 | sparse cols^2 w | 18.29 | 280 | 39.2 | 98.9 | 18.3 | 101.08 | -40.27 | 51.2 | 152.3 | -81.9 |  |
| 8 | 6 | sparse cols x nnz(M_D) | 18.29 | 280 | 39.2 | 88.5 | 18.3 | 90.67 | -29.86 | 51.2 | 141.9 | -71.5 |  |
| 10 | 3 | dense w=2 | 15.28 | 277 | 21.8 | 47.2 | 15.3 | 46.41 | 14.40 BEATS | 43.5 | 89.9 | -19.5 | non-refuting |
| 10 | 3 | dense w=2.37 | 15.28 | 277 | 21.8 | 55.3 | 15.3 | 54.46 | 6.35 BEATS | 43.5 | 98.0 | -27.6 | non-refuting |
| 10 | 3 | dense w=3 | 15.28 | 277 | 21.8 | 69.0 | 15.3 | 68.17 | -7.36 | 43.5 | 111.7 | -41.3 | non-refuting |
| 10 | 3 | sparse cols^2 w | 15.28 | 277 | 21.8 | 64.3 | 15.3 | 63.47 | -2.66 | 28.5 | 92.0 | -21.6 | non-refuting |
| 10 | 3 | sparse cols x nnz(M_D) | 15.28 | 277 | 21.8 | 49.6 | 15.3 | 48.74 | 12.07 BEATS | 28.5 | 77.3 | -6.9 | non-refuting |
| 10 | 4 | dense w=2 | 15.28 | 277 | 27.9 | 59.4 | 15.3 | 58.62 | 2.19 BEATS | 55.7 | 114.3 | -43.9 |  |
| 10 | 4 | dense w=2.37 | 15.28 | 277 | 27.9 | 69.7 | 15.3 | 68.93 | -8.12 | 55.7 | 124.7 | -54.2 |  |
| 10 | 4 | dense w=3 | 15.28 | 277 | 27.9 | 87.3 | 15.3 | 86.48 | -25.67 | 55.7 | 142.2 | -71.8 |  |
| 10 | 4 | sparse cols^2 w | 15.28 | 277 | 27.9 | 76.5 | 15.3 | 75.68 | -14.87 | 37.0 | 112.7 | -42.3 |  |
| 10 | 4 | sparse cols x nnz(M_D) | 15.28 | 277 | 27.9 | 63.8 | 15.3 | 62.97 | -2.16 | 37.0 | 100.0 | -29.6 |  |
| 10 | 5 | dense w=2 | 15.28 | 277 | 33.6 | 71.0 | 15.3 | 70.17 | -9.36 | 67.3 | 137.5 | -67.0 |  |
| 10 | 5 | dense w=2.37 | 15.28 | 277 | 33.6 | 83.4 | 15.3 | 82.62 | -21.81 | 67.3 | 149.9 | -79.5 |  |
| 10 | 5 | dense w=3 | 15.28 | 277 | 33.6 | 104.6 | 15.3 | 103.82 | -43.01 | 67.3 | 171.1 | -100.7 |  |
| 10 | 5 | sparse cols^2 w | 15.28 | 277 | 33.6 | 88.1 | 15.3 | 87.23 | -26.42 | 44.4 | 131.6 | -61.2 |  |
| 10 | 5 | sparse cols x nnz(M_D) | 15.28 | 277 | 33.6 | 76.7 | 15.3 | 75.86 | -15.05 | 44.4 | 120.3 | -49.8 |  |
| 10 | 6 | dense w=2 | 15.28 | 277 | 39.2 | 82.0 | 15.3 | 81.19 | -20.38 | 78.3 | 159.5 | -89.1 |  |
| 10 | 6 | dense w=2.37 | 15.28 | 277 | 39.2 | 96.5 | 15.3 | 95.68 | -34.87 | 78.3 | 174.0 | -103.6 |  |
| 10 | 6 | dense w=3 | 15.28 | 277 | 39.2 | 121.2 | 15.3 | 120.34 | -59.54 | 78.3 | 198.6 | -128.2 |  |
| 10 | 6 | sparse cols^2 w | 15.28 | 277 | 39.2 | 99.1 | 15.3 | 98.25 | -37.44 | 51.1 | 149.4 | -79.0 |  |
| 10 | 6 | sparse cols x nnz(M_D) | 15.28 | 277 | 39.2 | 88.7 | 15.3 | 87.89 | -27.08 | 51.1 | 139.0 | -68.6 |  |
| 12 | 3 | dense w=2 | 13.32 | 275 | 21.7 | 47.5 | 13.3 | 44.71 | 16.10 BEATS | 43.5 | 88.2 | -17.7 | non-refuting |
| 12 | 3 | dense w=2.37 | 13.32 | 275 | 21.7 | 55.5 | 13.3 | 52.75 | 8.06 BEATS | 43.5 | 96.2 | -25.8 | non-refuting |
| 12 | 3 | dense w=3 | 13.32 | 275 | 21.7 | 69.2 | 13.3 | 66.44 | -5.63 | 43.5 | 109.9 | -39.5 | non-refuting |
| 12 | 3 | sparse cols^2 w | 13.32 | 275 | 21.7 | 64.5 | 13.3 | 61.74 | -0.93 | 28.5 | 90.2 | -19.8 | non-refuting |
| 12 | 3 | sparse cols x nnz(M_D) | 13.32 | 275 | 21.7 | 49.8 | 13.3 | 47.04 | 13.77 BEATS | 28.5 | 75.5 | -5.1 | non-refuting |
| 12 | 4 | dense w=2 | 13.32 | 275 | 27.8 | 59.7 | 13.3 | 56.90 | 3.91 BEATS | 55.6 | 112.5 | -42.1 |  |
| 12 | 4 | dense w=2.37 | 13.32 | 275 | 27.8 | 70.0 | 13.3 | 67.19 | -6.38 | 55.6 | 122.8 | -52.4 |  |
| 12 | 4 | dense w=3 | 13.32 | 275 | 27.8 | 87.5 | 13.3 | 84.72 | -23.91 | 55.6 | 140.4 | -69.9 |  |
| 12 | 4 | sparse cols^2 w | 13.32 | 275 | 27.8 | 76.7 | 13.3 | 73.93 | -13.12 | 37.0 | 110.9 | -40.5 |  |
| 12 | 4 | sparse cols x nnz(M_D) | 13.32 | 275 | 27.8 | 64.0 | 13.3 | 61.25 | -0.44 | 37.0 | 98.2 | -27.8 |  |
| 12 | 5 | dense w=2 | 13.32 | 275 | 33.6 | 71.2 | 13.3 | 68.43 | -7.62 | 67.2 | 135.6 | -65.2 |  |
| 12 | 5 | dense w=2.37 | 13.32 | 275 | 33.6 | 83.6 | 13.3 | 80.86 | -20.05 | 67.2 | 148.0 | -77.6 |  |
| 12 | 5 | dense w=3 | 13.32 | 275 | 33.6 | 104.8 | 13.3 | 102.02 | -41.22 | 67.2 | 169.2 | -98.8 |  |
| 12 | 5 | sparse cols^2 w | 13.32 | 275 | 33.6 | 88.2 | 13.3 | 85.46 | -24.65 | 44.3 | 129.8 | -59.4 |  |
| 12 | 5 | sparse cols x nnz(M_D) | 13.32 | 275 | 33.6 | 76.9 | 13.3 | 74.12 | -13.31 | 44.3 | 118.5 | -48.0 |  |
| 12 | 6 | dense w=2 | 13.32 | 275 | 39.1 | 82.2 | 13.3 | 79.43 | -18.62 | 78.2 | 157.6 | -87.2 |  |
| 12 | 6 | dense w=2.37 | 13.32 | 275 | 39.1 | 96.7 | 13.3 | 93.89 | -33.09 | 78.2 | 172.1 | -101.6 |  |
| 12 | 6 | dense w=3 | 13.32 | 275 | 39.1 | 121.3 | 13.3 | 118.52 | -57.71 | 78.2 | 196.7 | -126.3 |  |
| 12 | 6 | sparse cols^2 w | 13.32 | 275 | 39.1 | 99.2 | 13.3 | 96.46 | -35.65 | 51.1 | 147.5 | -77.1 |  |
| 12 | 6 | sparse cols x nnz(M_D) | 13.32 | 275 | 39.1 | 88.9 | 13.3 | 86.13 | -25.32 | 51.1 | 137.2 | -66.8 |  |
| 16 | 3 | dense w=2 | 10.95 | 273 | 21.7 | 47.9 | 11.0 | 42.75 | 18.06 BEATS | 43.4 | 86.1 | -15.7 | non-refuting |
| 16 | 3 | dense w=2.37 | 10.95 | 273 | 21.7 | 55.9 | 11.0 | 50.78 | 10.03 BEATS | 43.4 | 94.2 | -23.7 | non-refuting |
| 16 | 3 | dense w=3 | 10.95 | 273 | 21.7 | 69.6 | 11.0 | 64.45 | -3.64 | 43.4 | 107.8 | -37.4 | non-refuting |
| 16 | 3 | sparse cols^2 w | 10.95 | 273 | 21.7 | 64.9 | 11.0 | 59.74 | 1.06 BEATS | 28.5 | 88.2 | -17.8 | non-refuting |
| 16 | 3 | sparse cols x nnz(M_D) | 10.95 | 273 | 21.7 | 50.2 | 11.0 | 45.09 | 15.72 BEATS | 28.5 | 73.6 | -3.1 | non-refuting |
| 16 | 4 | dense w=2 | 10.95 | 273 | 27.8 | 60.1 | 11.0 | 54.92 | 5.89 BEATS | 55.5 | 110.5 | -40.0 |  |
| 16 | 4 | dense w=2.37 | 10.95 | 273 | 27.8 | 70.3 | 11.0 | 65.19 | -4.38 | 55.5 | 120.7 | -50.3 |  |
| 16 | 4 | dense w=3 | 10.95 | 273 | 27.8 | 87.8 | 11.0 | 82.69 | -21.88 | 55.5 | 138.2 | -67.8 |  |
| 16 | 4 | sparse cols^2 w | 10.95 | 273 | 27.8 | 77.1 | 11.0 | 71.91 | -11.10 | 36.9 | 108.8 | -38.4 |  |
| 16 | 4 | sparse cols x nnz(M_D) | 10.95 | 273 | 27.8 | 64.4 | 11.0 | 59.27 | 1.54 BEATS | 36.9 | 96.2 | -25.8 |  |
| 16 | 5 | dense w=2 | 10.95 | 273 | 33.5 | 71.6 | 11.0 | 66.43 | -5.62 | 67.1 | 133.5 | -63.1 |  |
| 16 | 5 | dense w=2.37 | 10.95 | 273 | 33.5 | 84.0 | 11.0 | 78.83 | -18.02 | 67.1 | 145.9 | -75.5 |  |
| 16 | 5 | dense w=3 | 10.95 | 273 | 33.5 | 105.1 | 11.0 | 99.96 | -39.15 | 67.1 | 167.0 | -96.6 |  |
| 16 | 5 | sparse cols^2 w | 10.95 | 273 | 33.5 | 88.6 | 11.0 | 83.42 | -22.61 | 44.3 | 127.7 | -57.3 |  |
| 16 | 5 | sparse cols x nnz(M_D) | 10.95 | 273 | 33.5 | 77.3 | 11.0 | 72.11 | -11.30 | 44.3 | 116.4 | -46.0 |  |
| 16 | 6 | dense w=2 | 10.95 | 273 | 39.0 | 82.5 | 11.0 | 77.40 | -16.59 | 78.0 | 155.4 | -85.0 |  |
| 16 | 6 | dense w=2.37 | 10.95 | 273 | 39.0 | 97.0 | 11.0 | 91.83 | -31.03 | 78.0 | 169.9 | -99.4 |  |
| 16 | 6 | dense w=3 | 10.95 | 273 | 39.0 | 121.6 | 11.0 | 116.42 | -55.61 | 78.0 | 194.4 | -124.0 |  |
| 16 | 6 | sparse cols^2 w | 10.95 | 273 | 39.0 | 99.5 | 11.0 | 94.39 | -33.58 | 51.0 | 145.4 | -75.0 |  |
| 16 | 6 | sparse cols x nnz(M_D) | 10.95 | 273 | 39.0 | 89.2 | 11.0 | 84.10 | -23.29 | 51.0 | 135.1 | -64.7 |  |

### Presentation: direct

(direct: only D >= m*min(m-1,l) is defined; rows at smaller D are omitted. At the optimal l the degree is m(m-1): 6, 12, 20, 30, 56, ... so D = 6 appears only at m = 3.)

| m | D | elim | l* | N_var | log2 cols | per-attempt bit-ops | log2 attempts | T (log2 rho steps) | margin vs rho | mem bits | T x M | margin vs 6nW | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 6 | dense w=2 | 44.53 | 134 | 32.8 | 66.3 | 44.5 | 94.78 | -33.97 | 65.6 | 160.3 | -89.9 |  |
| 3 | 6 | dense w=2.37 | 44.53 | 134 | 32.8 | 78.4 | 44.5 | 106.83 | -46.02 | 65.6 | 172.4 | -102.0 |  |
| 3 | 6 | dense w=3 | 44.53 | 134 | 32.8 | 99.1 | 44.5 | 127.48 | -66.67 | 65.6 | 193.0 | -122.6 |  |
| 3 | 6 | sparse cols^2 w | 44.53 | 134 | 32.8 | 80.2 | 44.5 | 108.60 | -47.79 | 51.6 | 160.2 | -89.8 |  |
| 3 | 6 | sparse cols x nnz(M_D) | 42.16 | 126 | 32.3 | 53.0 | 49.3 | 87.05 | -26.24 | 49.1 | 136.2 | -65.8 |  |

## T5a. REFUTING cells (D >= 4) under which the total charged cost drops below rho (time) or below 6nW (time x memory)

| pres | m | D | elim | l* | log2 cols | per-attempt bit-ops | T (log2 rho steps) | margin vs rho | mem bits | T x M | margin vs 6nW | per-attempt budget left (log2 rho steps) | caveat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| block | 16 | 4 | dense w=2 | 10.95 | 27.8 | 60.1 | 54.92 | 5.89 | 55.5 | 110.5 | -40.0 | 49.86 | Semaev block heuristic (closure on 2n+l vars), unproved; omega = 2 is the dense-elimination floor |
| block | 12 | 4 | dense w=2 | 13.32 | 27.8 | 59.7 | 56.90 | 3.91 | 55.6 | 112.5 | -42.1 | 47.49 | Semaev block heuristic (closure on 2n+l vars), unproved; omega = 2 is the dense-elimination floor |
| block | 10 | 4 | dense w=2 | 15.28 | 27.9 | 59.4 | 58.62 | 2.19 | 55.7 | 114.3 | -43.9 | 45.53 | Semaev block heuristic (closure on 2n+l vars), unproved; omega = 2 is the dense-elimination floor |
| block | 16 | 4 | sparse cols x nnz(M_D) | 10.95 | 27.8 | 64.4 | 59.27 | 1.54 | 36.9 | 96.2 | -25.8 | 49.86 | Semaev block heuristic (closure on 2n+l vars), unproved; omega = 2 is the dense-elimination floor |

## T5b. D = 3 rows that come in under rho (listed for completeness; NON-REFUTING: D = 3 is the cubic equations with no multiplier, pilot W_3 refuted 0 of 140 UNSAT instances, Semaev proves first fall degree 4)

| pres | m | D | elim | l* | T | margin vs rho | margin vs 6nW |
|---|---|---|---|---|---|---|---|
| block | 16 | 3 | dense w=2 | 10.95 | 42.75 | 18.06 | -15.7 |
| block | 12 | 3 | dense w=2 | 13.32 | 44.71 | 16.10 | -17.7 |
| block | 16 | 3 | sparse cols x nnz(M_D) | 10.95 | 45.09 | 15.72 | -3.1 |
| block | 10 | 3 | dense w=2 | 15.28 | 46.41 | 14.40 | -19.5 |
| block | 12 | 3 | sparse cols x nnz(M_D) | 13.32 | 47.04 | 13.77 | -5.1 |
| block | 10 | 3 | sparse cols x nnz(M_D) | 15.28 | 48.74 | 12.07 | -6.9 |
| block | 8 | 3 | dense w=2 | 18.29 | 49.10 | 11.71 | -22.3 |
| block | 16 | 3 | dense w=2.37 | 10.95 | 50.78 | 10.03 | -23.7 |
| block | 8 | 3 | sparse cols x nnz(M_D) | 18.29 | 51.43 | 9.38 | -9.6 |
| block | 12 | 3 | dense w=2.37 | 13.32 | 52.75 | 8.06 | -25.8 |
| block | 6 | 3 | dense w=2 | 23.42 | 53.86 | 6.95 | -27.2 |
| block | 10 | 3 | dense w=2.37 | 15.28 | 54.46 | 6.35 | -27.6 |
| chained | 12 | 3 | dense w=2 | 13.32 | 55.89 | 4.92 | -43.4 |
| chained | 10 | 3 | dense w=2 | 15.28 | 56.09 | 4.71 | -41.9 |
| block | 6 | 3 | sparse cols x nnz(M_D) | 23.42 | 56.14 | 4.67 | -16.3 |
| chained | 16 | 3 | dense w=2 | 10.95 | 56.22 | 4.58 | -46.5 |
| chained | 8 | 3 | dense w=2 | 18.29 | 56.91 | 3.90 | -40.5 |
| block | 8 | 3 | dense w=2.37 | 18.29 | 57.16 | 3.65 | -30.4 |
| block | 5 | 3 | dense w=2 | 27.58 | 58.58 | 2.23 | -32.1 |
| chained | 6 | 3 | dense w=2 | 23.42 | 59.11 | 1.70 | -39.8 |
| block | 16 | 3 | sparse cols^2 w | 10.95 | 59.74 | 1.06 | -17.8 |
| block | 5 | 3 | sparse cols x nnz(M_D) | 27.58 | 60.24 | 0.57 | -24.5 |

Winning cells in all: 26; D = 3 non-refuting: 22; refuting D >= 4: 4 (block heuristic: 4, full presentations: 0). Time x memory winners (any D): 0.

## T6. For D = 4 (the smallest refuting degree; pilot's flat W_4 and Semaev's Assumption 1): the omega needed to tie rho, by presentation and m, and the gap at realistic omega

| pres | m | D used | log2 cols | c*(m) bit-ops | omega needed to tie | gap omega=2 | gap omega=2.37 | gap omega=3 | gap sparse cols^2 w | gap sparse cols x nnz(M_D) |
|---|---|---|---|---|---|---|---|---|---|---|
| chained | 4 | 4 | 29.7 | 27.1 | 0.914 | -32.2 | -43.2 | -61.9 | -50.6 | -38.1 |
| chained | 5 | 4 | 31.6 | 49.2 | 1.555 | -14.1 | -25.8 | -45.7 | -33.9 | -20.4 |
| chained | 6 | 4 | 32.9 | 53.5 | 1.625 | -12.3 | -24.5 | -45.3 | -33.2 | -19.0 |
| chained | 8 | 4 | 34.9 | 58.6 | 1.681 | -11.1 | -24.0 | -46.0 | -33.4 | -18.3 |
| chained | 10 | 4 | 36.3 | 61.6 | 1.696 | -11.0 | -24.5 | -47.4 | -34.4 | -18.5 |
| chained | 12 | 4 | 37.5 | 63.6 | 1.696 | -11.4 | -25.3 | -48.9 | -35.7 | -19.2 |
| chained | 16 | 4 | 39.3 | 66.0 | 1.678 | -12.7 | -27.2 | -52.0 | -38.3 | -20.9 |
| block | 4 | 4 | 28.1 | 27.1 | 0.928 | -30.2 | -40.6 | -58.3 | -47.5 | -34.5 |
| block | 5 | 4 | 28.1 | 49.2 | 1.693 | -8.6 | -19.0 | -36.8 | -25.9 | -13.0 |
| block | 6 | 4 | 28.0 | 53.5 | 1.837 | -4.6 | -14.9 | -32.6 | -21.8 | -8.9 |
| block | 8 | 4 | 27.9 | 58.6 | 2.006 | 0.2 | -10.2 | -27.7 | -16.9 | -4.2 |
| block | 10 | 4 | 27.9 | 61.6 | 2.104 | 2.9 | -7.4 | -25.0 | -14.2 | -1.4 |
| block | 12 | 4 | 27.8 | 63.6 | 2.166 | 4.6 | -5.7 | -23.2 | -12.4 | 0.3 |
| block | 16 | 4 | 27.8 | 66.0 | 2.238 | 6.6 | -3.7 | -21.2 | -10.4 | 2.3 |
| direct | 4 | 12 | 52.8 | 27.1 | 0.513 | -78.5 | -98.0 | -131.3 | -91.8 | -46.0 |
| direct | 5 | 20 | 79.2 | 49.2 | 0.621 | -109.3 | -138.6 | -188.6 | -123.4 | -51.1 |
| direct | 6 | 30 | 101.9 | 53.5 | 0.525 | -150.4 | -188.1 | -252.4 | -164.5 | -69.6 |
| direct | 8 | 56 | 137.8 | 58.6 | 0.425 | -217.1 | -268.1 | -354.9 | -231.4 | -100.6 |
| direct | 10 | 90 | 152.8 | 61.6 | 0.403 | -243.9 | -300.4 | -396.7 | -258.4 | -112.7 |
| direct | 12 | 132 | 159.8 | 63.6 | 0.398 | -256.1 | -315.2 | -415.9 | -270.8 | -118.0 |
| direct | 16 | 176 | 175.3 | 66.0 | 0.376 | -284.5 | -349.4 | -459.8 | -299.6 | -131.4 |

(negative gap = the closure is that many bits too expensive per attempt at the l that maximises the budget; T4 re-optimises l per cell and the verdicts agree.)

## T7. Early-abort 'cheap filter + full solve' split (chained, omega = 2): filter at D_f refutes UNSAT, full solve at D_s = 4 only on the p_sat survivors

| m | D_filter | D_solve | l* | p_sat | per-attempt bit-ops | T | margin vs rho |
|---|---|---|---|---|---|---|---|
| 4 | 3 | 4 | 30.70 | 0.00 | 48.2 | 75.59 | -14.78 |
| 4 | 4 | 4 | 33.90 | 0.63 | 61.1 | 78.87 | -18.07 |
| 5 | 3 | 4 | 24.94 | 0.00 | 51.1 | 73.15 | -12.34 |
| 5 | 4 | 4 | 27.58 | 0.63 | 64.4 | 75.90 | -15.09 |
| 6 | 3 | 4 | 21.16 | 0.00 | 53.4 | 71.95 | -11.14 |
| 6 | 4 | 4 | 23.42 | 0.63 | 67.0 | 74.32 | -13.52 |
| 8 | 3 | 4 | 16.53 | 0.00 | 56.8 | 71.21 | -10.40 |
| 8 | 4 | 4 | 18.29 | 0.63 | 70.9 | 73.11 | -12.30 |
| 16 | 3 | 4 | 10.01 | 0.00 | 64.5 | 73.53 | -12.72 |
| 16 | 4 | 4 | 10.95 | 0.63 | 79.8 | 74.64 | -13.83 |

A D_f = 3 filter refutes nothing (pilot), so its row is a lower bound that no algorithm attains; with D_f = 4 the filter IS the full closure and the split saves only the SAT_RATIO factor. At the cap p_sat ~ 0.63, so early abort cannot buy more than ~1 bit there.

## T8. Sensitivity: which parameter flips the sign. Reference cell = the best refuting cell per presentation (D = 4, omega = 2, dense, l optimised for time)

| pres | m | D | margin (bits) | omega that ties (D=4) | log2 bit-ops/rho-step that ties | d margin: ambient N=r | d: negation fold | d: Poisson A(mu) | d: SAT ratio 1 / 4.4 | d: LA k=3 | d: D=5 instead of 4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chained | 10 | 4 | -11.74 | 1.696 | 27.8 | 0.22 | 1.00 | -0.50 | 0.71 / -0.95 | -0.00 | -15.8 |
| block | 16 | 4 | 5.89 | 2.375 | 10.2 | 0.13 | 1.00 | -0.43 | 0.71 / -0.95 | -0.00 | -11.5 |
| direct | 3 | 6 | -33.97 | - | 50.1 | 0.95 | 1.04 | -0.59 | 0.66 / -0.91 | -0.15 | n/a (D<D_min) |

Reading: the sign is set by (1) omega (the D = 4 column count is fixed by N_var, so cost = omega x log2 cols), (2) the degree D (one step adds ~log2(N/5) ~ 6-8 bits of columns, times omega), and (3) the presentation (block vs full N_var changes log2 cols at D = 4 by 10-12 bits at m >= 8). Convention shifts (ambient, negation fold, Poisson, SAT ratio, LA constant) move margins by at most ~3 bits and flip nothing.

## T9. Asymptotic reading (D = 4 bounded for all m; Semaev cost family), general n, compared with 2^(n/2) as Table 3 does

| k / attempts rule | closure cols | omega | bit-ops/rho-step credited (log2) | time-only crossover n (persistent, vs 2^(n/2)) | min_m total time at n=131 (log2) | m* | margin vs 2^65.5 at n=131 | margin vs matched rho 2^60.81 |
|---|---|---|---|---|---|---|---|---|
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 2.0 | 0.0 | 205 | 87.3 | 7 | -21.8 | -26.5 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 2.0 | 16.1 | 152 | 71.2 | 7 | -5.7 | -10.4 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 2.37 | 0.0 | 241 | 97.7 | 7 | -32.2 | -36.9 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 2.37 | 16.1 | 190 | 81.6 | 7 | -16.1 | -20.8 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 3.0 | 0.0 | 302 | 115.4 | 7 | -49.9 | -54.6 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | n^{4w} block | 3.0 | 16.1 | 253 | 99.3 | 7 | -33.8 | -38.5 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 2.0 | 0.0 | 245 | 96.2 | 5 | -30.7 | -35.4 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 2.0 | 16.1 | 191 | 80.1 | 5 | -14.6 | -19.3 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 2.37 | 0.0 | 290 | 107.9 | 5 | -42.4 | -47.1 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 2.37 | 16.1 | 237 | 91.8 | 5 | -26.3 | -31.0 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 3.0 | 0.0 | 367 | 127.0 | 4 | -61.5 | -66.2 |
| Semaev eq.(15) k=n/m, attempts m! 2^k | full C((m-1)n+mk,<=4) | 3.0 | 16.1 | 317 | 110.9 | 4 | -45.4 | -50.1 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 2.0 | 0.0 | 147 | 71.0 | 16 | -5.5 | -10.2 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 2.0 | 16.1 | 100 | 54.9 | 16 | 10.6 | 5.9 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 2.37 | 0.0 | 177 | 81.4 | 16 | -15.9 | -20.6 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 2.37 | 16.1 | 131 | 65.3 | 16 | 0.2 | -4.5 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 3.0 | 0.0 | 231 | 99.2 | 16 | -33.7 | -38.4 |
| cap k=(n+log2 m!)/m, attempts 2^k | n^{4w} block | 3.0 | 16.1 | 185 | 83.1 | 16 | -17.6 | -22.3 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 2.0 | 0.0 | 197 | 87.9 | 9 | -22.4 | -27.1 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 2.0 | 16.1 | 151 | 71.8 | 9 | -6.3 | -11.0 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 2.37 | 0.0 | 238 | 100.9 | 8 | -35.4 | -40.1 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 2.37 | 16.1 | 193 | 84.8 | 8 | -19.3 | -24.0 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 3.0 | 0.0 | 310 | 122.2 | 6 | -56.7 | -61.4 |
| cap k=(n+log2 m!)/m, attempts 2^k | full C((m-1)n+mk,<=4) | 3.0 | 16.1 | 266 | 106.1 | 6 | -40.6 | -45.3 |

Table-3 reproduction: literal rule, omega = 3, n^12, no unit credit -> crossover 302 (tables.yaml derived_checks: 302; the paper states n > 310). Semaev's literal k = n/m overcharges attempts by log2(m!)(1 - 1/m) bits relative to the mu = 1 cap at finite n (the cap rule is the one the WWIT cells above use, with m <= 16 and the (m-2) block multiplier on the block reading), so the cap rows are the fair finite-n reading of the same family. The full variable count moves every crossover up; crediting 2^16.1 bit-ops per rho step moves it down. The optimum m grows like sqrt(2 ln2 n / ln n) and the exponent is 1.6986 sqrt(n ln n) (eq. 17; c = sqrt(2/ln 2)); at n = 131 that is 2^42.9 before the polynomial factors -- the polynomial factors (cols^omega ~ 2^56-2^84 at omega 2-3) are what decide the finite-n verdict.

| storage reading | omega | T x M crossover n, Semaev literal (reproduction) | T x M crossover, cap rule | T x M crossover, cap rule + 2^16.1 credit | program record |
|---|---|---|---|---|---|
| dense | 3.0 | 518 | 442 | 399 | 520 (dense) / 460 (sparse) at omega=3 [EV-SEMBIN-4125ec O-1/O-3] |
| dense | 2.37 | 453 | 384 | 341 |  |
| dense | 2.0 | 415 | 350 | 307 |  |
| sparse_semaev | 3.0 | 460 | 379 | 335 | 520 (dense) / 460 (sparse) at omega=3 [EV-SEMBIN-4125ec O-1/O-3] |
| sparse_semaev | 2.37 | 396 | 322 | 277 |  |
| sparse_semaev | 2.0 | 359 | 288 | 244 |  |

The T x M reproduction uses: stage 1 = m! 2^(n/m) n^(4 omega) (Table 3), stage 2 = 2^(2n/m), relation store 2^ceil(n/m) (mk+2n) bits log-summed with the working set (cols^2 for dense, (nm)^4/24 x n^3/m for Semaev-sparse), m = argmin of the product; vOW = 6 n x 0.886 2^(n/2). EV-SEMBIN-4125ec O-2 says the exact store convention is load-bearing for a bit-exact reproduction; a 0-5 unit difference in n is that convention.

## HEADLINE

1. Under the full variable count (direct or chained S_3), NO cell (m in 3..16, D in 3..6, omega in {2, 2.37, 3}, dense or sparse) beats rho 2^60.81 on ECC2K-130 with a refuting degree D >= 4: winners = 0.
2. Under Semaev's unproved block heuristic (closure on 2n + l variables, charged once per block) with D = 4: winners = 4 cells, all at omega = 2 (the dense-elimination floor) or the cols x nnz(M_D) sparse lower bound, all at m >= 10, none at omega = 2.37 or 3: m=16 dense w=2 +5.9 bits; m=12 dense w=2 +3.9 bits; m=10 dense w=2 +2.2 bits; m=16 sparse cols x nnz(M_D) +1.5 bits. At omega = 2.37 the best block cell is within 4-5 bits of rho (T6, T9).
3. Time x memory: NO refuting cell beats 6nW = 2^70.43: winners = 0. The closure matrix alone (cols^2 bits at D = 4) is 2^55-2^80 bits per attempt; the best refuting cell is 26-40 bits above 6nW.
4. The only 'winning' cells in the full presentations are D = 3, which is the equations themselves (no multiplication) and refutes nothing (pilot W_3: 0 of 140 UNSAT instances; Semaev proves first fall degree 4).
5. D_max(m) at realistic omega (>= 2.37) is 'none' (below 4) for every m under the full presentations and under the block heuristic alike; the m = 4/5 pilot would have to show a refuting closure at D <= 3 to matter, which is impossible by the first-fall-degree theorem. At omega = 2 the block heuristic admits D = 4 at m >= 8 with margins +0.2 (m=8), +2.9 (m=10), +4.6 (m=12), +6.6 (m=16) bits per attempt (T3), and 2.2-5.9 bits in total time after l re-optimisation (T5a).
6. Asymptotically, if D = 4 stayed bounded for all m, the family is Semaev's 2^(1.6986 sqrt(n ln n)) and the finite-n verdict is set by the polynomial cofactor cols^omega. Time-only it crosses 2^(n/2) at n = 302 in Semaev's own units (omega = 3, n^12 block, k = n/m). Under the single most IC-favourable reading here (block heuristic AND omega = 2 AND 2^16.1 bit-ops per rho step credited, cap rule) the crossing is n = 100, i.e. n = 131 is ~6 bits PAST it -- that is exactly the T5a block cells; raise omega to 2.37 and the crossing moves to n = 131 (margin -4.5 at 131); use the full variable count at omega = 2 and it is n = 151. Under time x memory the crossing against 6nW is n ~ 460-520 in the program's convention (reproduced: 518 / 460) and n >= 244 under every cap-rule variant; n = 131 is below all of them.
7. What would it take, in one line: a closure that refutes UNSAT descended systems at degree 4 with an elimination that costs no more than cols^2.0 bit operations (omega = 2) AND whose cost scales with one 2n-variable block rather than with the full (m-1)n-variable chain AND m >= 10 (factor base 2^11-2^15, chain of 8-14 auxiliary field elements), AND the time x memory metric waived. Remove any one of the three conjuncts and no cell beats rho 2^60.81 on ECC2K-130.
