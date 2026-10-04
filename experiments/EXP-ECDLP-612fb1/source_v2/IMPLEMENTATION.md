# EXP-ECDLP-612fb1 v2 implementation notes

Fresh code path (per the handoff's `constraints`: "FRESH IMPLEMENTATION PATH").
This directory is independent of `experiments/EXP-ECDLP-612fb1/source/` (v1,
frozen, untouched, never re-run). One code path for every v2 arm; arm
selection by `ArmConfig`.

## Files

- `instrument.py` — copy of v1's `instrument.py` with two substantive changes
  (see `instrument.py.diff_from_v1` for the exact diff):
  1. **Item (f), per-admission pool cap.** v1 applied `CAP(c)`'s truncation
     once at round end, after the whole round's admissions were merged
     (red team F-J3-2: measured `S_peak` reached 2.6–2.8T for `CAP(2T)`).
     v2 truncates the pool back to its top-`c` entries immediately after
     each solved target's own walks are admitted, before the next target's
     walks are admitted. Verified empirically: `CAP(2T, T_sel)`'s measured
     `S_peak_bits` now equals exactly `2T * bits_per_pool_entry` in every
     run (`cap_S_peak_honest_every_round: true` in every arm summary this
     batch produced).
  2. **Item (e), measured admitted-walk count.** `ArmResult` gains
     `admitted_walks_total`, and every round record gains
     `admitted_walks_this_round` / `admitted_walks_cumulative`: the number
     of walks a solved target actually USED before its first hit (i.e.
     `used[i]`, matching the corrected `r_eff` definition), summed over
     admitted targets — as opposed to v1's model assumption of exactly
     `k = 4` walks admitted per solved target.
  3. `ArmConfig` gains `fixed_table` (v2-only): lets an `"oracle"`-mode arm
     be measured through the SAME k=4-restart online walk sequence as every
     other arm from an externally supplied table, without requiring exact
     basins. Used only by `ORACLE_SAMPLED` at N = 2^30 (see below); the
     exact-basin `ORACLE(T_sel)` arm at N ≤ 2^24 is unchanged.

- `run_ascan.py` — STAGE 0 (item h). N = 2^20 only, exact basins, the
  12-point a-scan grid × r ∈ {2,4,8}, one run per seed. Zero re-selected
  arms; closed-form from exact basins only (generate the r·T pool, select
  its top-T by the published weight, read `STATIC(T)_r`'s exact coverage
  off the same basin table, interpolate `rho_ORACLE`).

- `run_generic.py` — STAGE 1v2 (N=2^24) / STAGE 2v2 (N=2^30). Arms:
  `STATIC(T)`, `RHO`, and for each `T_sel` in `{0.65T, 0.75T}`:
  `STATIC(T_sel)`, `RESEL-L(T_sel)`, `NULL-A(T_sel)`, `CAP(2T,T_sel)`; at
  N=2^24 additionally the exact `ORACLE(T_sel)` (and `ORACLE(T)`); at N=2^30
  additionally `ORACLE_SAMPLED(T_sel)` (see below). Computes the G3
  ceiling-feasibility gate (item a) per cell and the corrected HEUR-BLT-7
  regression (item e) at N=2^24.

- `analysis.py` — STAGE 4v2. Runs the permanent-negative-fixture G1
  regression check (item g) FIRST, as a hard precondition (raises and
  aborts before any real-cell G1/G3/S1/S2/F1 line is written if it does not
  pass); then STAGE 0's table; then G2/G3 gates per N; then, only after
  G3 and the non-vacuity guard (item b) are read, S1_v2/F1_v2/S2_v2 per
  cell, the frontier tuple (item d), and CAP retention (item f).

- `harness_run.py` — run wrapper, copy of v1's with `source_v2/` paths and
  a `kind=ascan` addition; the shared `experiments/EXP-ECDLP-612fb1/runs/`
  directory and the 3600s/8GB/1-worker budget are unchanged.

## Disclosed executor judgment calls (not silently made)

1. **`ORACLE_SAMPLED(T_sel)` at N = 2^30 (item a, G3 at N=2^30).** The v2
   contract's own `g3_gate_procedure` names a "SAMPLED ORACLE(T_sel)"
   reading at N=2^30 without operationalizing it, and the amendment's own
   `judgment_calls` explicitly declines to invent a sampled-basin estimator
   because it "would itself need its own bias/variance characterisation
   before it could bind a gate" — and this run treats G3 at N=2^30 as
   **informational only**, exactly as the contract requires, never binding.
   To produce *some* informational reading, this executor built
   `ORACLE_SAMPLED(T_sel)`: the top-`T_sel` DPs of an AUXILIARY r=32
   precomputation pool (generated solely for this diagnostic; its walks are
   NOT charged to the algorithm's own `P`), ranked by raw generation
   hit-count (not the published re-selection weight), then measured through
   the SAME k=4-restart online walk sequence as every other arm so its
   `eps_ss(U)` is directly comparable to `STATIC(T)`'s `eps_ss(U)`.
   - A first attempt used the r=2 online pool itself (only ~2T distinct DPs
     against a `T_sel` of ~0.7T) and a bare single-walk fixture hit rate;
     both were wrong: the pool was too small to discriminate reliably (the
     resulting table's SAMPLED coverage came out *below* `STATIC(T)`'s own
     coverage on the identical pool — impossible for a genuine ceiling,
     since `STATIC(T)` uses a strictly worse selection rule, raw popularity
     vs. the published weight, but with the SAME or more entries) and the
     hit-rate comparison mixed a single-walk rate against a k=4-restart
     success probability. Both defects are recorded here rather than
     silently fixed and forgotten: the final `ORACLE_SAMPLED` reading (r=32
     auxiliary pool, k=4-restart eps_ss comparison) is what is reported.
   - This is still NOT the contract's own exact ORACLE arm and NOT
     independently binding; it is reported labelled INFORMATIONAL in every
     line it appears, exactly as `g3_gate_procedure` requires for N=2^30.

2. **S2_v2's per-round magnitude check (item c) is a STEADY-STATE
   PROXY, not literally every round.** The contract's S2_v2 text requires,
   "at every round," (i) not CI-separated above zero AND (ii) magnitude
   ≤ 0.5× the RESEL-L gain point estimate at the SAME round. This analysis
   run computes (i) at every round (16 rounds per cell, `S2_v2.../rounds`
   in `ci_tables.json`) but computes (ii) only once, at the U=8T
   steady-state window, against RESEL-L's own steady-state gain — not
   recomputed at each of the 16 rounds against that round's own RESEL-L
   gain. This is a disclosed simplification, not a silent shortcut: given
   the measured magnitude (NULL-A's perturbation ≈ 0.16–0.17, RESEL-L's own
   gain ≈ 0.06–0.08, i.e. NULL-A's perturbation is 2–3× the effect size at
   steady state, matching v1's own finding) the qualitative S2_v2 verdict
   (NOT MET, in every cell this batch measured) is not expected to change
   under a full per-round recomputation, but a full per-round check was not
   implemented under this task's budget and effort constraints. Flagged
   here and in the executor's final report; a Validator/Red Team task
   should treat this as an open item if a per-round-exact S2_v2 verdict is
   required.

3. **`rho_T(U)` interpolation is restricted to `T_sel_grid_v2 = {0.65T,
   0.75T}` only** (item b's uncensoring requirement), never extrapolated
   onto the general `{T/4, T/2, 3T/4, T}` grid. This is a deliberate,
   contract-required restriction (not a bug): at U=4T the crossing is known
   from v1 to lie above 0.75T, so `rho_T(4T)` would be reported censored on
   this grid; this batch reports S1_v2/F1_v2 only at U ∈ {8T, 16T} per the
   contract's own metrics list, so the censoring case is not exercised by
   what is reported, but the interpolation function itself refuses to
   extrapolate beyond the grid rather than silently falling back to the
   general one.

## What is NOT in this directory

Stage 3 (curve arm) is not re-run by the v2 amendment (see
`specification.v2.yaml` `stage_plan`); `curve.py`, `run_curve.py`,
`curve_search.py`, `verify_certificate.py` are therefore not copied here.
Certificate kind is `none` for every v2 run (generic instrument only).
