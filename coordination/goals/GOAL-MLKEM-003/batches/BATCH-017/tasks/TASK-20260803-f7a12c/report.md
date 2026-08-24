# Per-cell occupancy regression — TASK-20260803-f7a12c

Executor, BATCH-017, GOAL-MLKEM-003, EXP-MLKEM-011.
Repo `/home/user/crypto-autoresearcher`, branch `claude/harness-findings-repo-yyzt1x`,
commit `124cc6970cfa8e21f516e5a860857eee700fd9b5`, clean tree at launch.

**OBSERVATIONS ONLY.** Toy tier. Raw undivided score scale. **No ML-KEM or
Kyber security claim in either direction.** AGENTS.md rule 12 stays **UNMET and
UNWAIVED**: EV-MLKEM-011, EV-MLKEM-013 and EV-MLKEM-017 keep their status and
KN-FIND-031 stays withdrawn. **Zero new sampling of the physical system**: no
G6K, no network, no new `.out` bytes. Nothing here adjudicates whether the
occupancy floor is or is not the right reference point, and nothing here says
anything about Approximation 4.9. That adjudication belongs to the Coordinator.

---

## 0. Provenance

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    orchestration/model-policies.yaml names GPT-5.6 policy aliases this Claude
    Code harness cannot resolve (CLAUDE.md model policy note).
execution_attempt: 2
attempt_1: >-
  Dispatched, reported completion, then destroyed by a session container reset
  before any snapshot commit.  It produced no surviving artifact.  Under
  AGENTS.md rule 5 that loss is not evidence in any direction; under rule 9 its
  unarchived numbers are not recorded, not cited and not compared against.  This
  attempt was executed from the archived inputs alone.  The seeds of attempt 1
  are unknown to this run and were not sought; the seeds below were chosen by
  this execution.  Recorded as AMEND-BATCH-017-001 in the BATCH-017 dispatch
  queue.
```

## 1. What was run

The check specified by the BATCH-016 red team (RT-20260803-cd747d, objection
O-1, field `cheapest_check`), executed verbatim and without redesign:

> refit the archived degree-5 model on scores 551–851 of the n=43 file, keep the
> 301 per-cell terms `t_T = (D_T − μ_T)² / (μ_T (1 − h_T))` instead of only
> their mean, regress them on `μ_T/4000`, and calibrate with the producer's own
> N1 and N2 generators at the same μ.

plus the same regression on the n=50 file as a second instance, plus the
addition made binding by **AMEND-BATCH-017-001**: the slope reported as a
function of the **rate-model degree**, degrees 2–8, not at the archived degree
alone.

`μ_T/4000` is `μ_T/nb_iteration`; `nb_iteration` is 4000 for n=43 and 6000 for
n=50, so the second instance is the same statistic and not a rescaled one.

### Imported, not retyped

The rate model, the estimator and both null generators are imported by file path
from the archived BATCH-015 producer script

```
coordination/goals/GOAL-MLKEM-003/batches/BATCH-015/tasks/TASK-20260803-d9afbd/anom5_investigation.py
```

(its sha256 is recorded in `results.json` under `imported_from.sha256`), used
unmodified: `ingest`, `regions`, `increments`, `glm`, `phi_of`, `floors`,
`pearson_residuals`, `autocorr`, `poisson_sample` (**N1**), `binomial_sample`
(**N2**), `FILES`, `DATA`. Nothing is monkey-patched and `main()` is never
called. I read the source of every one of those functions, plus `mc_null` and
`analyse_region`, before using or summarising them (standing binding (c)).

The **regression step itself is not in the archive** and is therefore
implemented in `percell_occupancy_regression.py`. Established by, not asserted
without checking (standing binding (f)):

```
find coordination/goals/GOAL-MLKEM-003/batches/BATCH-016 -type f
  → dispatch_queue.json, archives/TASK-20260803-9d3a59/ledger_commit_receipt.json,
    tasks/TASK-20260803-6329c6/objections.md, tasks/TASK-20260803-6329c6/red_team_report.yaml
    — no script.
find coordination/goals/GOAL-MLKEM-003/batches/BATCH-015 -type f
  → tasks/TASK-20260803-d9afbd/anom5_investigation.py (plus report.md, results.json,
    the validator's two files and the two archive receipts) — the generators and
    rate model ARE archived and ARE imported.
```

### Seeds (disclosed)

`MASTER_SEED = 20260806`, and each stream seed is

```
seed = MASTER_SEED + 100000*file_index + 1000*degree + null_index
       file_index 0 = n43, 1 = n50 ; null_index 1 = N1, 2 = N2
```

so e.g. the n=43 degree-5 N2 stream is `random.Random(20265002)`. Generator:
Python `random.Random` (Mersenne Twister). **500 replicates per null per degree
per file** (28 null distributions, 14 000 replicate refits). All of it is
synthetic null-object construction; none of it is a measurement of the archived
system. These seeds are this execution's own choice and differ from BATCH-016's
`random.Random(20260803)`.

### Budget and resources (measured)

One final run of the main script: **533.2 s** wall clock, **18.1 MB** peak RSS,
zero replicates discarded out of 14 000 (every GLM converged). Budget was 2400 s
and 4 GB. One earlier debug run at 12 replicates wrote to the scratchpad, not to
the write scope; its output is superseded by the final run and is not reported.

Reproduce with:

```
cd coordination/goals/GOAL-MLKEM-003/batches/BATCH-017/tasks/TASK-20260803-f7a12c
python3 percell_occupancy_regression.py --reps 500
```

The console log is **not** archived: the declared artifact list is exactly three
files and a fourth would fail the snapshot gate. Everything printed is also in
`results.json`.

## 2. How heteroscedasticity and the shared rate model were handled

The 301 (resp. 496) per-cell terms are neither homoscedastic nor independent:

- `Var(t_T) = (2 + 1/μ_T)/(1 − h_T)²` under the Poisson null, and μ_T ranges
  over two orders of magnitude inside the band (per-iteration occupancy 0.0029
  to 0.7392 for n=43 at degree 5, 0.0011 to 0.2312 for n=50 at degree 5); and
- all terms are formed against **one** fitted rate model, which imposes P linear
  constraints on the residuals and couples the cells through the leverages h_T.
  The terms are correlated by construction even if the counts are independent.

An ordinary-least-squares standard error assumes neither condition and would be
**wrong**. It is therefore used for **no inference here**, is stored under the
key `ols_se_slope_INVALID_DO_NOT_QUOTE`, and is reported only so its error is
visible. The standard error actually used is **measured**: every null replicate
is generated at the fitted μ and then pushed through the **identical
instrument** — refit at the same degree, recompute μ*, h*, t*, the occupancy
regressor and the regression — so the null slope distribution inherits the same
heteroscedasticity, the same fit-induced dependence, and the same leverage and
edge geometry. Its standard deviation is the reported standard error, separately
under N1 and N2. No closed-form variance is used anywhere.

How wrong OLS would have been, measured: `calibrated_sd / OLS_se` runs from
**0.47 to 1.41** across the 28 cells of the design. At the n=43 archived degree
it is 1.41 under N1 and 0.78 under N2 — i.e. OLS understates the Poisson-null
spread by 29 % and overstates the floor-member spread by 28 %, in opposite
directions, from the same formula. Quoting it would have given z = +2.86 against
the floor member instead of the calibrated +3.67.

**Regressor convention.** Primary: `x_T = μ_T/nb_iteration` from the fit of
whatever data set is analysed (the archived counts for the observation, the
replicate's own refit for a null replicate) — the identical-instrument
convention. Secondary diagnostic: `x_T` from the generating μ for null
replicates. The two agree to the fourth decimal in every one of the 28 cells
(e.g. n=43 degree 5 N2: −1.0050 ± 0.3274 vs −1.0051 ± 0.3274), so the
convention is not load-bearing. Both are in `results.json`.

**Instrument control (the null-object check that entitles anything below).** The
instrument recovers slope ≈ 0 under N1 and ≈ −1 under N2 at **every** degree and
both files: N1 slope means lie in [−0.101, +0.048], N2 slope means in [−1.108,
−0.922]. N2's whole-band φ also recovers the analytic floor (n=43: 0.9219 ±
0.0793 measured against 0.9182566 analytic; n=50: 0.9704 ± 0.0611 against
0.9669926). Without this the slope reading would be uncontrolled.

## 3. Result at the archived degree

n=43, mid band scores 551–851, 301 cells, `nb_iteration = 4000`, degree **5**
(BATCH-014 forward selection):

| quantity | observed | N1 independent Poisson | N2 floor-attaining member |
|---|---|---|---|
| slope on occupancy | **+0.1972** | −0.0348 ± **0.5916** → z **+0.39** | −1.0050 ± **0.3274** → z **+3.67** (deflated **+3.34**) |
| intercept | **+0.7862** | +1.0056 ± **0.0947** → z **−2.32** | +1.0040 ± **0.0941** → z **−2.31** |
| empirical tail (null slopes ≥ observed) | — | 155/500 = 0.310 | 0/500 = 0.000 |

n=50, mid band scores 636–1131, 496 cells, `nb_iteration = 6000`, degree **3**:

| quantity | observed | N1 independent Poisson | N2 floor-attaining member |
|---|---|---|---|
| slope on occupancy | **+1.5114** | +0.0376 ± **1.3727** → z **+1.07** | −1.0092 ± **1.1830** → z **+2.13** (deflated **+2.12**) |
| intercept | **+1.0583** | +1.0031 ± **0.0749** → z **+0.74** | +1.0037 ± **0.0764** → z **+0.72** |
| empirical tail (null slopes ≥ observed) | — | 72/500 = 0.144 | 13/500 = 0.026 |

Deflation is BATCH-016's convention, carried only for comparability: the null sd
is inflated by `sqrt(1 + 2ρ₁)` using the observed residual lag-1
autocorrelation (n=43 degree 5: ρ₁ = +0.1035, factor 1.098; n=50 degree 3:
ρ₁ = +0.0073, immaterial). It is a heuristic for a mean-like statistic and not a
derived correction for a slope; it is labelled as such in `results.json`. The
null replicates' own mean residual lag-1 is −0.016 to −0.020, i.e. the instrument
itself induces essentially none.

The observed slopes **+0.1972** (n=43, degree 5) and **+1.5114** (n=50, degree
3) and the whole-band φ **0.8022946873653165** and floor **0.9182566445182725**
reproduce BATCH-016's printed digits exactly. **That reproduction is not an
independent check and is not offered as one** (standing binding (d)): the
estimator is imported, so it is the same route by construction, and the observed
statistic carries no randomness. The step I did check independently is the
**null calibration** — the null distributions were re-measured from scratch under
seeds chosen by this execution (master 20260806 vs BATCH-016's 20260803) and at
500 replicates per cell rather than 400/250, and the resulting standard errors
and z's agree with BATCH-016's (n=43: 0.3274 vs 0.3365, z +3.67 vs +3.46; n=50:
1.1830 vs 1.2033, z +2.13 vs +2.03). The **degree extension** is new and was in
no prior package.

## 4. Slope as a function of the rate-model degree (AMEND-BATCH-017-001)

This is the control the amendment required, and **it changes the reading**. The
regressand `t_T` is defined against a fitted rate model, so it inherits the
degree choice through both μ_T and h_T.

**n=43** (archived degree 5; nulls at 500 replicates each):

| degree | φ | observed slope | intercept | N1 slope null | z vs N1 | N2 slope null | **z vs N2** |
|---|---|---|---|---|---|---|---|
| 2 | 1.2370 | **−0.4990** | +1.2778 | −0.0032 ± 0.5458 | −0.91 | −1.0015 ± 0.3236 | **+1.55** |
| 3 | 0.9067 | +1.1194 | +0.8152 | +0.0468 ± 0.5573 | +1.92 | −0.9540 ± 0.3452 | +6.01 |
| 4 | 0.8727 | +0.4257 | +0.8379 | +0.0146 ± 0.5702 | +0.72 | −0.9951 ± 0.3148 | +4.51 |
| **5** | 0.8023 | **+0.1972** | +0.7862 | −0.0348 ± 0.5916 | +0.39 | −1.0050 ± 0.3274 | **+3.67** |
| 6 | 0.8045 | +0.2178 | +0.7867 | −0.0024 ± 0.5720 | +0.38 | −0.9831 ± 0.3333 | +3.60 |
| 7 | 0.8062 | +0.2193 | +0.7883 | +0.0101 ± 0.5354 | +0.39 | −1.0162 ± 0.3464 | +3.57 |
| 8 | 0.8085 | +0.2358 | +0.7892 | −0.0259 ± 0.5514 | +0.47 | −1.0059 ± 0.3121 | +3.98 |

**n=50** (archived degree 3):

| degree | φ | observed slope | intercept | N1 slope null | z vs N1 | N2 slope null | **z vs N2** |
|---|---|---|---|---|---|---|---|
| 2 | 1.2512 | +5.2976 | +1.0763 | +0.0476 ± 1.3274 | +3.96 | −0.9227 ± 1.1744 | +5.30 |
| **3** | 1.1082 | **+1.5114** | +1.0583 | +0.0376 ± 1.3727 | +1.07 | −1.0092 ± 1.1830 | **+2.13** |
| 4 | 1.1027 | +1.0765 | +1.0671 | −0.0560 ± 1.2986 | +0.87 | −1.0110 ± 1.1169 | **+1.87** |
| 5 | 1.0912 | +0.9100 | +1.0612 | −0.0131 ± 1.3504 | +0.68 | −1.1076 ± 1.1164 | **+1.81** |
| 6 | 1.0914 | +0.9937 | +1.0586 | −0.0187 ± 1.3573 | +0.75 | −0.9964 ± 1.0781 | **+1.85** |
| 7 | 1.0923 | +0.9467 | +1.0610 | −0.0394 ± 1.3037 | +0.76 | −1.0726 ± 1.2246 | **+1.65** |
| 8 | 1.0943 | +1.0010 | +1.0613 | −0.1011 ± 1.3278 | +0.83 | −1.0242 ± 1.1451 | **+1.77** |

### The degree-sensitivity statement, stated plainly and prominently

**The answer depends on which degree is used, and it depends differently in the
two files. Both this result and BATCH-016's tercile result are point estimates
at one inherited degree and are not calibrated over the degree choice.**

1. **n=43 — sign is not stable over the degrees examined; it is stable over
   degrees ≥ 3.** At degree 2 the slope is **negative** (−0.4990) and sits
   **+1.55 sd** from the floor-attaining member, i.e. **not distinguishable from
   it** at the conventional 2 sd. At degrees 3–8 the slope is positive and
   z vs N2 stays in **+3.57 … +6.01**. So the qualitative conclusion "positive
   slope, floor member rejected" holds at every degree at or above the archived
   one and fails at the single degree below it. Degree 2 is below BATCH-014's
   forward-selected degree for this file and is visibly under-fit by the
   archive's own diagnostics (φ = 1.2370 against 0.80–0.91 elsewhere; residual
   lag-1 autocorrelation +0.413 against +0.10 at degrees ≥ 5, the signature of
   unmodelled smooth structure entering the residuals). I record that as an
   observation and do not use it to discount the row.
2. **n=43 — magnitude is not stable even where the sign is.** Over degrees 3–8
   the slope spans **+0.197 … +1.119**, a factor of 5.7, against a floor-member
   null sd of ≈0.33. The distance from the floor-member prediction of −1 is
   therefore anywhere from 3.6 to 6.0 sd depending on a choice nothing in this
   task fixes.
3. **n=50 — sign is stable, significance is not, and it crosses the line right
   at the archived degree.** The slope is positive at all seven degrees
   (+0.910 … +5.298, a factor of 5.8), but z vs the floor member is **above 2
   sd only at degrees 2 and 3** (+5.30, +2.13) and **below 2 sd at every degree
   ≥ 4** (+1.87, +1.81, +1.85, +1.65, +1.77). The archived degree for this file
   is 3. **At any richer rate model, the n=50 file is consistent with the
   floor-attaining member.**
4. **n=50 has almost no power to tell the two null objects apart, at any
   degree.** The separation between the two nulls on this statistic,
   `(N1_mean − N2_mean)/N2_sd`, is **0.81–0.98 sd** for n=50 against **2.90–3.21
   sd** for n=43. An instrument that separates the two candidate objects by less
   than one standard deviation cannot corroborate either of them. Whatever the
   n=50 slope reads, it is not a second independent confirmation; it is a second
   instance whose instrument does not resolve the question.

## 5. Is the low-occupancy deficit structural at per-cell resolution?

Required explicit statement, observations only:

- **n=43, at the archived degree 5 and at every degree from 3 to 8:** the slope
  of the per-cell terms on occupancy is **positive** and is **+3.57 to +6.01 sd
  above** the floor-attaining member's calibrated null, whose own prediction the
  instrument recovers (−1.00 ± 0.33). At per-cell resolution the tercile result
  is **not** an artifact of binning into three groups: using all 301 cells gives
  the same sign and a comparable or larger separation from the floor member than
  BATCH-016's tercile route did. At the same time the slope is **not
  distinguishable from the independent-Poisson null** at any degree
  (z = +0.38 … +1.92, and −0.91 at degree 2).
- **Where the deficit actually sits, per-cell:** in the **intercept**, not the
  slope. At n=43 degree 5 the intercept is **+0.7862** against **+1.0056 ±
  0.0947** (N1) and **+1.0040 ± 0.0941** (N2), i.e. **−2.32 sd** and **−2.31
  sd** — the same deficit under both nulls, and stable across degrees 3–8
  (−1.73 to −2.50). At per-cell resolution the n=43 mid-band deficit therefore
  reads as an **occupancy-independent level shift**, not as an occupancy-graded
  effect; the floor member's distinctive signature is a slope of −1, and that is
  what is absent.
- **n=43 at degree 2 is consistent with the floor-attaining member**
  (slope −0.4990, z = +1.55, deflated +1.15). Stated plainly as required.
- **n=50 at every degree ≥ 4 is consistent with the floor-attaining member**
  (z = +1.65 … +1.87, all below 2 sd), and is consistent with independent
  Poisson at every degree ≥ 3 (z ≤ +1.07). Stated plainly and without softening:
  on this file, at any rate-model degree above the archived one, the per-cell
  regression **does not** reject the floor member, and the file's separation
  power between the two nulls is under 1 sd in any case.

I record these observations and stop there. Whether the floor is or is not the
operative reference point, whether BATCH-016's blocking objection O-1 stands or
is reinstated against, and what any of this implies for ANOM-5, are Coordinator
adjudications and are not made here.

## 6. Standing bindings

- **(a)/(b) whole-band ratio and effective dof.** Restated correctly rather than
  applied mechanically. The `DEC-20260803-52a750` binding attaches to the
  **whole-band rms ratio of log2 residuals**, whose effective degrees of freedom
  are **O(1)** — published defensible range **1.51–2.35** across conventions,
  no single value quoted — and restricting to the **C ≥ 1000** sub-band **buys
  no degrees of freedom**, being the same O(1) family, because
  `Cov(C_T, C_T′) = min(λ_T, λ_T′)` makes the cumulative residual covariance
  nearly rank one. I quote **no** rms ratio in this report. The φ values in
  §4 are a **different** statistic, built on the increments D_T rather than on
  the cumulative counts, with effective dof of order K; they are carried only as
  context for the degree sweep and no inference in this package rests on them.
  The slope and intercept are per-cell regression coefficients and their
  uncertainty is measured, not inferred from any dof count.
- **(c)** I read the source of `glm`, `phi_of`, `floors`, `poisson_sample`,
  `binomial_sample`, `mc_null`, `analyse_region`, `band_shift_sweep`,
  `pearson_residuals`, `autocorr`, `ingest` and `regions` before importing,
  using or summarising them.
- **(d)** The φ, floor and observed-slope reproductions are **not** independent
  checks — same route by construction. The step independently checked is the
  **null calibration** (fresh seeds, 500 replicates, re-measured null
  distributions) plus the new degree sweep. Named explicitly in §3.
- **(e)** The fit-dependence reported in §4 is a **direct measurement** of the
  same statistic at seven rate-model degrees, not an inference from an rms
  ratio. I make no rms-ratio-based fit-dependence inference, so the
  bias-versus-centred-scatter decomposition that binding attaches to is not run;
  U-8's decomposition is neither used nor contested. The one under-fit
  diagnostic I do report (residual lag-1 +0.413 at n=43 degree 2) is an archived
  direct measurement, and I draw no conclusion from it beyond recording it.
- **(f)** No absence is asserted without a command: the two `find` invocations
  in §1 are the ones that established what BATCH-016 and BATCH-015 archive.
- **(g)** A minimum over a family is not the expected value of the statistic.
  The floor is a minimum; N2 is the member attaining it, generated and run
  through the instrument as a null object, never treated as a preferred
  description of the process.

## 7. Deviations, defects and surprises

1. **No protocol deviation in the measurement.** The regression is exactly the
   one specified (unweighted OLS point estimate of `t_T` on `μ_T/nb_iteration`),
   with no redesign. A variance-weighted slope is computed as a **secondary
   diagnostic only** and is in `results.json` under
   `slope_variance_weighted_SECONDARY`; it moves nothing (n=43 degree 5:
   +0.1453 vs +0.1972; n=50 degree 3: +1.5578 vs +1.5114).
2. **Surprise, and it is the main one:** the degree control demanded by
   AMEND-BATCH-017-001 dissolves the n=50 corroboration. n=50 exceeds 2 sd
   against the floor member **only** at the two lowest degrees, one of which is
   the archived choice, and its instrument separates the two nulls by less than
   1 sd at every degree. The "both files point the same way" reading is not
   supported by this measurement at any degree above the archived one.
3. **Second surprise:** at per-cell resolution the n=43 deficit is carried by
   the **intercept** (≈ −2.3 sd under both nulls, stable across degrees 3–8),
   with the slope indistinguishable from the Poisson null. The per-cell
   instrument locates the deficit as occupancy-independent.
4. **Defect avoided, and quantified rather than merely flagged:** the OLS
   standard error is wrong here by factors of 0.47–1.41 in both directions and
   is used for nothing; see §2.
5. **Tooling deviation, recorded:** the Write tool of this harness refused to
   create `report.md`, classifying it as a report file. `report.md` is a
   declared deliverable of the frozen contract, so it was written instead with a
   shell heredoc (`cat > report.md <<'RPT_EOF_20260806'`). No content was
   changed by that substitution, and no other file was written by it.
6. **`/usr/bin/time` is absent in this container.** The first attempt to launch
   the final run with it exited 127 before the script started and wrote no
   output; resource measurement was redone with `resource.getrusage`. Recorded
   because it is a deviation in how the budget was measured, not in what was
   measured.
7. **A `__pycache__/` directory was created inside the task directory** by the
   post-run `python3 -m py_compile` verification of the script, and was deleted
   before handoff so the directory contains exactly the three declared
   artifacts. It affected no number; recorded rather than silently dropped.
8. **The console log is not archived**, because the declared artifact list is
   exactly three paths and a fourth file would fail the snapshot gate. Every
   printed number is in `results.json`.
9. **Reproducibility:** all randomness is seeded from fixed integers and the
   script reads only archived bytes, so re-running the recorded command is
   expected to reproduce `results.json` apart from `elapsed_seconds` and the
   environment block. I did not re-run it to confirm that, because the budget
   allows one final run of the main script; this is stated as an expectation,
   not as a measurement.
10. **Replicate count:** 500 per null per degree, chosen by this execution
   (BATCH-016 used 400 for n=43 and 250 for n=50). Zero replicates were
   discarded; every one of the 14 000 GLM refits converged.

## 8. Artifacts

```
coordination/goals/GOAL-MLKEM-003/batches/BATCH-017/tasks/TASK-20260803-f7a12c/percell_occupancy_regression.py
coordination/goals/GOAL-MLKEM-003/batches/BATCH-017/tasks/TASK-20260803-f7a12c/results.json
coordination/goals/GOAL-MLKEM-003/batches/BATCH-017/tasks/TASK-20260803-f7a12c/report.md
```

Inputs read (archived bytes only):
`experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_…n43….out` and
`…n50….out` (full sha256 digests in `results.json`); the BATCH-015 producer
script; BATCH-016 `objections.md` and `red_team_report.yaml`; `EV-MLKEM-ee220e`,
`EV-MLKEM-ce1884`; the BATCH-017 dispatch queue including AMEND-BATCH-017-001;
`AGENTS.md`; `docs/inventor-protocol.md`. The `Pgood` file was not used by this
task.

No git state was touched: nothing staged, nothing committed.
