# Protocol: volcano-level panel at m = 3 on the n = 16 Koblitz class (pre-registered)

Frozen 2026-10-11 before any cell ran. Residual lead R1 of `README.md`.

**Question.** With the production S₄ Gröbner solver (m = 3, where the
decomposition step is non-trivial: hundreds of reductions per call), does the
per-prime volcano position (v₃(f_E), v₃₁(f_E)) of a curve in the n = 16,
f = 3·31 Koblitz class predict per-call solver cost, first-fall degree or
relation yield?

**Instrument.** `crypto/examples/koblitz_level_panel.rs` (a variant of the
presentation sweep): full-group probes, fixed budget of 12 probes per curve,
monomial subspace V = ⟨1, z, …, z⁵⟩ (l = 6; a random V is about 8× costlier
per call at m = 3 and is out of budget), node budget 2·10⁶ reductions per
decomposition, transported logarithm BSGS-checked. Three worker threads.

**Curves (13).** Crater a₆ = 1; all four curves of stratum (v₃, v₃₁) = (1, 0)
(a₆ = 34988, 34989, 36766, 36767); four seeded-random curves of stratum (0, 1)
(a₆ = 31049, 40902, 45805, 63030); four of stratum (1, 1) (a₆ = 1710, 5390,
45335, 61880). Selection seed 20261011, from `per_ell_levels.json`.

**Metrics per curve** (algebraic ones are deterministic given the probe
stream): reductions per call, first-fall and D* histograms when enabled,
unknown-probe count (budget exhaustion), relations per probe, Gröbner wall
per call (timing is secondary: cells run interleaved across strata in a
seeded random order, three at a time).

**Pre-registered expectations.** (1) Reductions per call and first-fall
degree identical across strata within the per-curve spread (Boundary C′
makes the leading forms a₆-free for every m). (2) Relations per probe follow
|F|³ scaling; no stratum effect once |F| is accounted for. (3) The crater is
not slower than any floor stratum. A stratum effect at permutation p < 0.01 on
an algebraic metric would be a finding to re-derive, not to report.

**Analysis.** Curve-level means; between-stratum permutation test (20,000
draws, labels permuted across curves) on each metric; crater z against the
pooled floor; incremental R² of strata beyond |F| for the relation rate.

**Budget and stop rule.** About 300 s per call at m = 3 (pilot
2026-10-03): 13 × 12 = 156 calls ≈ 13 core-hours ≈ 4.5 wall-hours. Cells
append to the checkpoint file as they finish; if the session ends first,
the partial rows are analysed as such and the missing cells are listed.
No cell is dropped for being slow; an exhausted node budget is recorded as
`unknown_probes`, never as a refutation.

**Amendment 2026-10-12, recorded before the panel ran.** A one-call smoke on
the crater (`experiments/levelpanel_smoke/`, 1 probe, l = 6, m = 3) took
430 s and 948 reductions. The container was restarted once during the
session, which killed the first launch before any cell finished, so the
budget is reduced from 12 to **6 probes per curve** (a cell then lands in
about 45 minutes; 13 cells on 3 threads ≈ 3 wall-hours). The algebraic
metrics (reductions per call, infeasible branches, refutations) are per
call and unaffected; the relation-rate estimate gets half the probes and is
reported with its Poisson interval. Nothing else changes.
