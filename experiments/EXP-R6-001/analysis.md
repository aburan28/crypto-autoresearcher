# EXP-R6-001 analysis — arbitrary explicit factor-base membership solve (R6)

**Runs of record:** `RUN-EXP-R6-001-a` (probe, valid w/ censoring), `-b` (F=12 full cell, valid),
`-c` (F=14 cell, valid), `-d` (F=16 random arm, valid partial), `-e` (F=16 interval arm, valid partial),
`-e2`/`-e3` (F=14/F=16 support-matched nulls, valid), `-f` (rho ladder 2^20..2^30, valid),
`-g` (F=101 l~2^20 design-point attempt, censored), `-h` (m=4 F=6 spot attempt, censored).
Script: `R6_run.sage`; analyzer: `R6_analyze.py` (-> `analysis.json`). Sage 10.9, macOS arm64.
Every recovered decomposition was verified against its target; every rho recovery was exact (k == k_true).

## 1. What was measured (and what was censored)

The frozen spec's ladder is `l = 2^20..2^30` with `|F| = l^{1/3}` (F = 101..1016 for m=3).
The probe (RUN-a) found the m=3 solve wall **between F=18 (gb 28.0 s) and F=20 (gb > 460 s,
censored at the 600 s cap)**. Per the stopping rules, the measured cells were placed at the
largest feasible sizes `F = 12, 14, 16` (cell subgroup orders `q in [F^3, 1.15 F^3]`, i.e.
`l ~ 2^10.7..2^12.2`, birthday balance `|F|^3 ~ q` preserved per cell), and all spec-scale
cells were censored per protocol (section 5). This is a **reduced-scope** execution of the
frozen protocol: deviations listed in section 6.

## 2. Measured cells (m=3; total cost = build + GB + root-extraction, per target)

| cell (arm) | n (empty) | q~ | GB median s | total mean s | total mean, group-op-equiv | d_reg med (max) | vdim med (max) |
|---|---|---|---|---|---|---|---|
| F=12 random    | 24 (5) | 1811 | 1.41 | 5.43 | 1.07e6 | 2 (8) | 6 (57) |
| F=12 interval  | 24 (7) | 1823 | 1.45 | 6.73 | 1.32e6 | 2 (8) | 4.5 (45) |
| F=14 random    | 24 (4) | 2861 | 4.15 | 13.97 | 2.74e6 | 2 (4) | 6 (21) |
| F=14 interval  | 18 (7) | 2797 | 4.17 | 8.58 | 1.69e6 | 2 (4) | 4.5 (24) |
| F=16 random    | 12 (4) | 4397 | 8.66 | 36.88 | 7.25e6 | 2 (10) | 4.5 (61) |
| F=16 interval  | 8 (2) | 4703 | 11.75 | 64.57 | 1.27e7 | 2.5 (4) | 9 (18) |

(group-op-equivalents via measured unit 5.09e-6 s/group-op, RUN-b; total means include
singular-`variety()` fallback extractions on 20/110 targets — see unexpected observations.
`empty` = no decomposition exists for that random target; its solve cost still counts.)

**Total-cost exponent (primary metric):** per-target log-log fit over all 110 m=3 solves:
**alpha = 2.074, bootstrap 90% CI (1.565, 2.621)** (2000 resamples within cells, `analysis.json`).
Cell-mean fit: alpha = 2.217 (6 cell-arms). GB-only (solve without extraction): alpha = 2.144,
CI90 (2.086, 2.209). fglm-extraction-only totals: alpha = 2.071 (n=82). **Every variant's CI
lies entirely above 0.5.**

## 3. Controls (all four mandatory)

**(1) Pollard rho on the same instances + spec-scale ladder.** 56 in-cell recoveries (F=12..16,
same curves/targets) + 96 ladder measurements at l = 2^20/2^24/2^28/2^30 (3 curves x 8 targets
each), all exact. Fitted rho exponent **0.4988, CI90 (0.4813, 0.5161)** — sits at l^0.5 as the
control must. Measured constant 1.356 mean / 1.306 median vs 1.2533 theory (H040/T24 anchor,
plain-walk convention). **Cost ratio, solve/rho on matched instances: total 2.0e4..1.5e5x,
GB-only 5.1e3..2.7e4x** (per-cell table in `analysis.json`). The solve arm loses to rho at every
measured scale by 4-5 orders of magnitude.

**(2) Matched random curves (control 2).** Implemented as independent random curves in the same
l-window (exact same-l matching is infeasible by rejection at these l within budget — deviation,
section 6). Curve-mean GB spread within each cell-arm: max/min ratio **1.04..1.25** across all
six cells — cost is curve-generic.

**(3) Same-order isogenous curve (control 3).** Explicit rational isogenies found for every
control3 curve (degrees 3,5,7,11,13; order equality verified). Mean GB: F=12 1.38 s vs 1.43 s
main; F=14 4.25 s vs 4.16 s; F=16 10.37 s vs ~9.9 s — **identical within noise**.

**(4) Support-matched random null (control 4).** 4 nulls per cell (identical monomial support,
randomized coefficients; T11-style): GB 1.80 s (F=12), 5.91 s (F=14), 14.49 s (F=16) vs real
1.43 / 4.16 / ~9.9 s — **nulls cost ~1.3-1.5x the real systems with the same ~F^6-7 scaling**;
no curve-structure shortcut is visible in either direction. (All nulls had empty varieties,
as expected for random systems; the GB cost is the comparison.)

## 4. No-win signature and secondaries

- **d_reg flat + time exponential — the smooth-subgroup no-win signature recurs:** d_reg
  median = 2.0 at every cell (outliers to 10 only on high-vdim targets) while cost scales ~l^2.1.
- Decomposition yield: 67/110 random targets had >=1 verified decomposition (vdim 0..61;
  relation counts per target in raw.json). vdim distribution is consistent with
  ~16|F|^3/q ordered-sign decompositions per target.
- Relation build cost (membership polynomial construction): 0.002..0.008 s/target
  (charged into relation_cost); negligible next to the GB — the bookkeeping leak is not
  present: even GB-only cost exceeds rho by 3-4 orders of magnitude.
- d_ff: not instrumented (the EXP-DREG-001 instrument targets the boolean system family;
  sizes do not overlap) — deviation recorded; d_reg via GB max degree reported instead.

## 5. Censoring table (infrastructure state, not evidence — AGENTS rule 5)

| cell | outcome |
|---|---|
| m=3 F=20 (l~2^13) | GB censored: >460 s unfinished at the 600 s cap (RUN-a, killed) |
| m=3 F=24 | not attempted (ladder stopped after censored scale) |
| m=3 F=101, l~2^20 (spec design point) | build 0.0083 s; GB censored at 240 s (RUN-g) |
| m=3 spec scales l = 2^24..2^30 | censored (design points F=256..1016 unreachable; not attempted) |
| m=4 F=6 (l~2^10.5) spot arm | first GB censored at 300 s, zero solves (RUN-h); m=4 F=8 dev smoke >200 s |
| m=4 spec points (F=32 @ 2^20, F=64 @ 2^24, ...) | censored (not attempted) |

## 6. Deviations from the frozen specification (all recorded here and in the EV)

1. **Scales reduced:** spec ladder l=2^20..2^30 unreachable within the 600 s/invocation and
   3000 s total budget; measured cells at l ~ 2^10.7..2^12.2 (F=12,14,16), |F|=l^{1/3}
   preserved per cell. Spec-scale solve cells censored (section 5); rho control at the spec
   scales measured in full (RUN-f).
2. **Replication reduced at F=14/F=16:** F=14 interval arm 18/24 targets; F=16 random 12/24,
   interval 8/18 (soft-deadline skips, enumerated in each run's raw.json notes). F=12 complete.
3. **Control 2** implemented as l-window-matched independent random curves, not exact same-l.
4. **Control 3** via explicit small-degree rational isogenies (all found, degrees <= 13).
5. **m=4 spot arm:** attempted at F=6 (and F=8 in dev smoke); fully censored within budget.
6. **d_ff** not instrumented (instrument/system mismatch); d_reg (GB max degree) reported.
7. **Extraction path:** FGLM + back-substitution primary; Singular `variety()` fallback on
   20/110 solves (method recorded per target; fallback times inflate F=16 total means).
8. **Machine shared** with another experiment agent during parts of the session (wall-time
   noise; op-count metrics — rho ops, d_reg, vdim — unaffected).
9. RUN-d stderr printed "done" lines for deadline-skipped phases (0 records); raw.json counts
   and skip notes are authoritative; logging fixed for later runs and noted in its manifest.

## 7. Gate arithmetic (numbers, per the frozen criteria — verdict belongs to the Coordinator)

- Success criterion needs: alpha CI entirely below 0.5 on >=4 ladder points AND below every
  control. Measured: **3 F-values** (< 4), alpha = 2.074 CI90 (1.565, 2.621) — **CI entirely
  above 0.5**; cost **above** the rho control by 2.0e4..1.5e5x at every measured scale.
- Falsification conditions: (i) "alpha CI overlaps 0.5 or sits above the rho control" —
  CI (1.565, 2.621) sits entirely above 0.5 and above rho's measured 0.4988 (0.4813, 0.5161);
  (ii) "the no-win signature (degree flat, time exponential) recurs" — d_reg median 2.0 flat
  across all cells, cost ~ l^2.1; (iii) "solve-only gain erased by full accounting" — no gain
  even solve-only (GB-only alpha 2.144, CI (2.086, 2.209); GB-only/rho 5.1e3..2.7e4x).
- Prediction 2 (d_reg lower than the support-matched null): real d_reg median 2 vs null
  systems all unit-ideal (d_reg 0, empty) — nulls solved *harder*, not easier; no d_reg
  separation in the predicted direction (null GB costs are 1.3-1.5x real, same scaling).

## 8. Unexpected observations (AGENTS rule 8)

1. Sharp solve wall: m=3 F=18 gb 28.0 s vs F=20 > 460 s unfinished (>=16x for 1.11x size).
2. m=4 (6-variable) systems are dramatically harder than m=3 at matched l: even F=6 censored,
   while m=3 F=12 costs ~1.4 s.
3. d_reg outliers up to 10 on high-vdim targets; median stays 2.
4. Null systems cost *more* than the real membership systems at every cell (~1.3-1.5x).
5. vdim (relation count) spans 0..61 at fixed F — target-to-target variance is large.

## 9. Scope statement (AGENTS rules 6-7)

Toy scale only (l <= 2^12.2 measured; spec scales censored, not extrapolated). These numbers
say: over the tested instances, parameters, solver (Singular degrevlex GB), and budget, the
arbitrary explicit-membership m=3 total cost scales ~ l^2.1 (CI entirely above 0.5), tracks
the support-matched null, and loses to Pollard rho by 4-5 orders of magnitude at every
measured scale, with the no-win signature present. Nothing here bounds alternative
implementations (non-GB solvers), larger-l behavior directly (censored), or non-membership
formulations.
