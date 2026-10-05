# TASK-20261002-758e51 — executor report

ZERO-RUN analysis of the archived PTM-5 exactly generic replica outputs of the
TW-FLOOR round. **Observations only.** No solver or engine code was imported or
executed (nothing under `src/crypto_autoresearcher/index_calculus` was imported
or run; the frozen `stats.py` was READ to recover the `bootstrap_slope`
algorithm and REIMPLEMENTED verbatim in `code/01_analysis.py` — never imported).
No status, hypothesis, evidence or ledger record was written or modified; every
write is under this task directory. One analysis attempt
(`code/01_analysis.py`, exit 0); the identity held at the first attempt, so the
single permitted rerun was NOT used.

Data: `coordination/review/pfdr-twfloor-20261001/reviews/TASK-20260929-575e80/attacks/out/ptm5_results.jsonl`
(8400 rows; m in {3,4,5}, bits 12..24, modes census/on, 200 per cell — verified).
Slope series: m = 4, mode = on, bits 12..24, PRIMARY stop, r > 0 on every row:
**n = 1400** (7 rungs x 200). Per-rung T: m = 4 and m = 5, on-mode, PRIMARY
stop, n = 200 per (m, rung) cell.

## 1. Field mapping (each mapping licensed by a cited archived artifact)

| symbol | replica field | licensed by |
|---|---|---|
| S_3 | `stop["S"]` (= `table_s3 + search_s3`, table included) | `attacks/ptm5_engine.py` `snapshot()`; `attacks/07_ptm5_analysis.py` uses `p["S"]` |
| r_frozen | `stop["r_frozen"]` (= `relations + sum(rows_fed)`, on mode; the lemma's step-(ii) pair count) | `ptm5_engine.py` `snapshot()`; `attacks/f3-lemma-map.yaml` symbol_map `r` |
| r_rank | `stop["rank"]` (the solver rank; the lemma's step-(iii) independent-relation count) | `ptm5_engine.py` `snapshot()`/`Elim.rank`; `f3-lemma-map.yaml` symbol_map `r` |
| N, B | `row["N"]`, `row["B"]` | `07_ptm5_analysis.py` `ratios()` |
| stop | `row["primary"]` (first row determining k; the engine-stop analogue) | `ptm5_engine.py` `run_instance()` docstring; `07_ptm5_analysis.py` and `09b_ptm5_agg_by_rung.py` both read `primary` |
| ratio | `S / (0.5 * sqrt(r * N))` | `07_ptm5_analysis.py` `ratios()` |
| x, groups | `log2(N)`, the rung (`bits`) | `calibration/f7.py` `series()` (`r["log2N"]`, `k[1]`) |

Verified before the attempt (`out/00_field_check.json`): all 1400 m = 4 (and
1400 m = 5) on-mode rows carry a PRIMARY stop with `rank >= 1` and
`r_frozen >= 1` (none excluded); N and B are constant per rung (one rung prime
per bits, `rung_prime(bits)` deterministic), which licenses the exact
per-stratum-sum form of the stratified bootstrap (self-check in
`slopes.json.linear_form_selfcheck`, absdiff 1.2e-16).

## 2. (a) Slopes — replica vs engine (EV-PFDR-d90ccd OBS-8 restated)

Method: OLS of log2(quantity) vs log2 N; interval = the frozen `stats.py`
`bootstrap_slope` convention (stratified by rung, one draw per member with
replacement, percentile endpoints by the `stats.py` index arithmetic),
reps = 20000, level = 0.95, seed = 0 — reimplemented verbatim
(`random.Random(0)`); calibration per `calibration/f7.py` + `f7_supp.py`
(gauss / t3 / empirical / within_rung_empirical / rung_sd_gauss; beta0 in
{0, slope}; 1000 series; inner interval reps 2000 seed 0; kappa_95 =
zs[ceil(0.95 n)-1]); calibrated interval = [slope - k(slope - lo),
slope + k(hi - slope)] with the worst kappa over the quantity's 10
configurations.

| quantity | replica slope | replica nominal 95% | replica calibrated | engine (OBS-8) |
|---|---|---|---|---|
| ratio_rank | **-0.019426** | [-0.022505, -0.016275] | **[-0.022747, -0.016027]** (kappa 1.0786) | -0.01491, calibrated [-0.0242, -0.0053] |
| ratio_frozen | **-0.038062** | [-0.041568, -0.034597] | **[-0.041782, -0.034385]** (kappa 1.0610) | -0.03384 (nominal [-0.04169, -0.02558]) |

- Both replica calibrated intervals exclude 0. MC-2 (200 seeds x 2000 reps):
  0/200 flips of "excludes 0" for both quantities; endpoint MC s.d. <= 1.1e-04.
  MC-5 coverage at the replica's design: 0.928-0.957 at nominal 95% over the 20
  configurations (the replica's 200-per-rung design needs far less widening
  than the engine's five-per-rung design, whose worst ratio_rank kappa over 34
  configurations was 1.349).
- Vectorized cross-check of the same semantics (numpy PCG64, seed 758510):
  interval endpoints agree with the verbatim fits to <= 4.2e-05
  (`slopes.json.vectorized_crosscheck_20000`) — validates the vectorized
  machinery used for MC-2 / MC-5.
- Levels under r_rank: replica series min/max **[1.374, 5.232]** over 1400
  instances (ratio_frozen [0.704, 2.720]); the engine's series level was
  2.10-3.63 over its 55 instances. The replica's 1400-instance series spans
  wider extremes than the engine's 55-instance series; recorded as an
  observation only (no per-instance predicate is adopted, AMD C-4).

## 3. (b) Per-rung aggregate T (AMD-20261002-2bc8cf C-1..C-4)

T = (sum_i w_i S_i^2)/(sum_i w_i r_i N_i/4), w_i = 1/(N_i B_i), per (m, rung),
on-mode, PRIMARY stop, both r conventions. **Premise audit (C-1):** the replica
is exactly generic BY CONSTRUCTION (base logs uniform distinct nonzero
+-classes; x-key equality = +-equality; the floor's premise holds EXACTLY —
`ptm5_engine.py` module docstring); no per-arm audit applies (no arms).
**C-3:** both conventions reported. **C-4:** no per-instance predicate
adopted. Point values reconcile with the round's descriptive
`09b_ptm5_agg_by_rung.json` to <= 1.6e-14 (exact same formula and rows).

99% interval: the round's curve bootstrap at the engine's five-per-rung design
— five instances per rung per replicate (the replica's 200-per-cell rows
playing the curve role), 20000 replicates, `np.default_rng(0)` per cell,
`np.quantile` 0.005/0.995 (`09_agg_by_rung.py`'s convention).

| m | conv | T by rung 12..24 bits | 99% interval range over rungs |
|---|---|---|---|
| 4 | frozen | 2.2315, 1.9421, 1.7715, 1.5024, 1.4077, 1.3935, **1.2953** | lowest hi99 **1.6013** (b24); lo99 dips below 1 at b20-b24 (0.9820, 0.9926, 0.9619) — intervals straddle 1 |
| 4 | rank | 8.8642 -> 6.0992 | all intervals far above 1 |
| 5 | frozen | 3.1718 -> 1.9914 | lowest hi99 2.7606 (b24) |
| 5 | rank | 12.4608 -> 8.1513 | all far above 1 |

**No rung's 99% interval excludes 1 from below on any cell**
(`per_rung_T.json.flags_excluding_1_from_below` = []); nothing is TW-BREAK-shaped
and nothing routes to the Coordinator on that channel. The m = 4 frozen path
(2.23 -> 1.30 over 12..24 bits) follows the engine's own path (2.507 at 12 bits
-> 1.115 at 30 bits, EV-PFDR-d90ccd cross_joint_reading) toward 1 from above.

Coverage (the round's MC-5 structure, `04_f6_aggregate.py`: 1000 synthetic
designs per cell, inner interval 20000 reps, inner seeds 10_000+design /
20_000+design): **NULL-B** (r* ~ Poisson(4 S^2/N) per instance, S fixed — the
L2 pair budget attained exactly in expectation, T_true = 1): coverage of the
true T = **1.000** and false-flag rate (hi99 < 1) = **0.000** on every cell.
**NULL-G** (u* ~ Gamma(rank+1, 1/kappa_hat), r = rank fixed, per-cell
kappa_hat = sum(rank+1)/sum(4 S^2/N)): coverage **1.000** on every cell. The
five-per-rung interval is conservative (over-covers) at this design — the
5-instance T sampling distribution is much wider than the null's cell-level
variability; the round's engine pooled-cell coverage (0.946-0.984 at nominal
99%) was a different, tighter design (five curves per rung pooled over rungs).

## 4. (c) The identity's decomposition

slope(log2 ratio_rank) = slope(log2 ratio_frozen) + 0.5*(slope(log2 r_frozen/B)
- slope(log2 r_rank/B)), on the same 1400 rows:

| component | replica | engine (f7.stdout / EV-PFDR-d90ccd) | replica - engine |
|---|---|---|---|
| slope log2 ratio_rank | -0.019426 | -0.014907 | -0.004520 |
| slope log2 ratio_frozen | -0.038062 | -0.033838 | -0.004224 |
| slope log2 r_frozen/B | +0.038628 [+0.030900, +0.046512] | +0.040822 | -0.002194 |
| slope log2 r_rank/B | +0.001357 [+0.000232, +0.002557] | +0.002959 | -0.001601 |
| slope log2 (r_frozen/r_rank) | +0.037271 [+0.029779, +0.045000] | +0.037863 | -0.000592 |
| 0.5 x multiplicity contribution | +0.018636 | +0.018932 | -0.000296 |

**Identity residual: 3.47e-18** (tolerance 1e-09; the alternative form
slope(log2 ratio_frozen) + 0.5*slope(log2 r_frozen/r_rank) gives the same
residual; the component difference check is exactly 0.0). The identity HOLDS
— exact arithmetic per instance, as the engine's own decomposition also
re-verifies from the archived values (-0.03383844969209488 + 0.5*(0.04082209815404258
- 0.0029586587579856403) = -0.014906729994066413 vs F7's -0.014906729994066411,
residual 1.7e-18). No defect; the single permitted rerun was not used.

The decomposition reproduces on the replica: the r_rank decline is the r_frozen
ratio's decline plus half the multiplicity growth, with every component within
0.0022 of the engine's recorded values.

## 5. (d) The pre-registered reading (DEC-20261002-bed082, fixed before data)

**Branch (i) fired, by condition A**: the replica's r_rank slope's own
calibrated interval [-0.022747, -0.016027] lies INSIDE the engine's calibrated
interval [-0.0242, -0.0053] (the nominal 95% interval [-0.022505, -0.016275]
also lies inside). Conditions (ii) (interval containing 0) and (iii) (steeper
than the engine's beyond both intervals) did not fire. Stated plainly for the
Coordinator: the replica's point slope (-0.019426) is steeper than the
engine's point (-0.01491), and the engine's point lies 0.0029 above the
replica's calibrated upper end — but the rule's branch (i) condition A is
met, and the rule's reading is therefore its pre-registered sentence:

> "F7's r_rank decline reproduces on the exactly generic replica"; the decline
> is the generic floor-attainment path, and OQ-F7 narrows toward
> 'T flattens at >= 1'.

This is the rule's own sentence fired by its own condition, not this
executor's interpretation; the Coordinator reads it under NA-2. (Honesty note:
this outcome is the Coordinator's pre-registered expectation, which
DEC-20261002-bed082 recorded as NOT independent.)

**Per-rung T:** no rung's 99% interval excludes 1 from below at m = 4 or m = 5
under either convention — no TW-BREAK-shaped flag; the per-rung table stands as
observations.

**Identity:** exact arithmetic, residual 3.47e-18 within tolerance — no defect,
no rerun.

Scope discipline (TW-SCOPE): toy scale, 12..24 bits, synthetic Z_N replica;
no deployed-curve claim, no universal impossibility, no exponent below rho.

## 6. Defects, deviations, unrecoverable conventions (recorded, not silently dropped)

1. **Card sign discrepancy (r_rank/|F|).** The card's COMPUTE (c) lists
   "r_rank/|F| -0.002959". The archive records POSITIVE: f7.stdout
   `r_rank_over_F` slope +0.0029586587579856403, and EV-PFDR-d90ccd F7 reads
   "+0.0030". The identity arithmetic requires + (with -0.002959 the engine's
   decomposition would give -0.011948, not F7's -0.014907). The archive was
   followed; the card's minus sign is recorded as a card-text defect, not
   resolved silently.
2. **The round's NULL-P coverage null is not recoverable for the replica
   rows.** `04_f6_aggregate.py`'s NULL-P draws r* from the exact compound
   Poisson with the instance's own per-class H1 means (mu_TT, mu_TB, mu_SS —
   engine row fields). The replica rows carry no per-class H1 means; only the
   SS first moment is recoverable (`07_ptm5_analysis.py` first_moment_SS:
   (enc_recorded - ss_dup)(enc_recorded - ss_dup - 1)/N), and the total pair
   count's H1 mean needs the table's per-key group structure, which the rows
   do not carry. Adaptation used and labelled: **NULL-B** (r* ~ Poisson(4 S^2/N),
   the L2 pair budget with X = 2S, floor attained exactly in expectation,
   T_true = 1) — the decision-relevant null for the flag rule. NULL-G is the
   round's shape with a per-cell kappa_hat (the round estimated kappa per
   (m, mode) cell pooled over rungs; my cells are per rung, so the per-cell
   estimate is the per-rung analogue — recorded).
3. **Slope bootstrap strata vs per-rung T draws.** The archived
   `bootstrap_slope` convention stratifies by rung and resamples every stratum
   at its own size — 200 per rung on the replica's rows (there is no prior
   bit-identical run on these rows; seeds declared). The per-rung T intervals
   use the card's five-instances-per-rung MC-5 curve-role discipline. Both are
   recorded with their citations; neither was silently substituted.
4. **Coverage 1.000 (conservative).** Both nulls give coverage 1.000 at
   nominal 99% on every cell: at the five-per-rung design the interval is much
   wider than the null's cell-level variability. Recorded as an observation
   about the procedure at this design (the round's 0.946-0.984 was the engine's
   pooled-cell design).
5. **Dispatch-note HEAD vs execution HEAD.** The dispatch note said HEAD
   3f51ede083; at execution HEAD was 35d8d2c7b5 (one later `bus: publish
   records` commit; the card/decision commit 3f51ede083 is present beneath it;
   working tree clean apart from this task directory). Recorded in the
   receipt.
6. **Machine condition.** /Volumes/SSD990 had ~35 MB free at session start; a
   zsh here-document failed on temp-file creation before computing anything
   (recorded in the receipt as an infrastructure note; nothing was computed by
   it). All outputs are small (total ~150 KB); no command failed during the
   analysis.

## 7. Deliverables

- `code/00_field_check.py`, `code/01_analysis.py` (deterministic; seeds
  declared in the docstring and the receipt)
- `out/slopes.json` (replica r_rank and r_frozen slopes with bootstrap and
  calibrated intervals, MC-2, MC-5, engine F7 values restated from
  EV-PFDR-d90ccd OBS-8, decision-rule branch evaluation)
- `out/per_rung_T.json` (both conventions, m = 4 and m = 5, premise audit,
  99% intervals at 20000 replicates, coverage, flags = [])
- `out/identity_decomposition.json` (components, residual 3.47e-18, engine
  comparison, card sign note)
- `out/00_field_check.{json,stdout,stderr}`, `out/01_analysis.{stdout,stderr}`
- `report.md` (this file), `receipt.yaml`
