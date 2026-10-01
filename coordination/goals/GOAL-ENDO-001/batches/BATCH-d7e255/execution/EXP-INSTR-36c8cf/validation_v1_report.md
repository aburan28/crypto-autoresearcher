# Validation V1 — EXP-INSTR-36c8cf amendment v2 (HEUR-INSTR-4 vs. competing heavy-tail explanation)

Independent `review-adversarial` session. Did not originate EXP-INSTR-36c8cf, amendment v1, amendment v2,
or DEC-20260810-5aeeaa. Task: re-derive, from `RUN-INSTR-36c8cf-phaseA-v2-57ca9a`'s own raw per-seed
variance ratios, a verdict on whether the observed rung-to-rung instability is ordinary sampling noise
(HEUR-INSTR-4) or a right-skewed / heavy-tailed per-row sampling distribution (the competing explanation
named in amendment v2). This report is validation **V1** named in
`validation_required_before_approval`. It does not approve, reject, or otherwise change the status of
amendment v2, does not touch the run, and changes no ledger record.

## Snapshot verified

- Amendment v2: `experiments/EXP-INSTR-36c8cf/amendments/v2.yaml`, committed at `60060084` (ancestor of
  current HEAD `2b9af4d6`), working tree byte-identical to that commit.
- Decision: `ledger/decisions/DEC-20260810-5aeeaa.yaml`, same commit, same identity check.
- Run: `experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/`, committed at `77cd4285`
  (also an ancestor of HEAD), working tree byte-identical (`git diff 77cd4285 -- <run dir>` empty). This
  is the Coordinator-committed snapshot named by `DEC-20260810-5aeeaa.snapshot_commit_holding_the_run`;
  no working-tree-only artifact was substituted.
- `raw-result.json`'s `raw.sr3v3_families.4001.rungs` is structurally equal (`==`) to
  `sr3v3-reference-sampling.json`'s `families.4001.rungs` — raw/summary agreement holds, so every number
  below is grounded in the same per-seed values both files carry.

## Artifact / manifest checks

- All 20 contract-required artifacts present in the run directory, plus 3 declared extras
  (`conflict-1.json`, `inference-provenance.json`, `load-observations.json`), matching DEC-20260810-5aeeaa's
  own count.
- `manifest.yaml`: `code.commit = cbbdd003d9169ec07a31f1c1f569fd08a77bcdca`, `dirty: false`,
  `all_pinned: true` (13 source files, each sha256-pinned; 4 are `status: untracked` but still hash-pinned,
  consistent with the contract's own note that pinning — not git-cleanliness — identifies the code for a
  dirty/new-file run). `status: completed_valid`.
- Seeds: rung 1 = the 12 contract seeds (including `11235813`); rung 2 adds exactly `20260821..20260832`
  (12 new, verified from the raw per-seed keys, nested inside rung 1); rung 3 adds exactly
  `20260833..20260856` (24 new, nested inside rung 2) → 12/24/48 exactly as amendment v1 change G3 E2
  declares. Confirmed directly from the per-seed key sets in `sr3v3-reference-sampling.json`, not from any
  summary count.
- Environment: `macOS-26.6-arm64`, Python 3.13.1, vs. the historical reference run's Linux x86_64 /
  Python 3.11.15 (`reference_run_reproduction.note`); this is disclosed in-run and gated only on the
  variance-ratio statistic bit-exactly at the shared-sum-set path (not on cross-platform bit-exactness of
  the re-measurement), which is the correct scope per the contract.
- Resources: wall 128.234 s, CPU 116.057 s, peak RSS 72.45 MB — all inside budget
  (14400 s / 24 CPU-h / 8 GB / 20 runs); `budget_events: []`.
- `z` computed at run time (`2.8905115606917384` from `NormalDist().inv_cdf(519/520)`), not transcribed —
  consistent with the A4 no-transcription rule.

## Metric recomputation (independent, from raw per-seed ratios only)

All of the following were computed directly from `per_seed_ratios` in `sr3v3-reference-sampling.json`
(cross-checked against the byte-identical copy in `raw-result.json`), **not** copied from
`sr3v3-interval-stability.json` or the amendment's own summary text, and then compared:

- **Half-widths**: recomputed `z * sample_stdev(per_seed_ratios)` for all 13 rows × 3 rungs and it equals
  the reported `half_width`/`interval_low`/`interval_high` to <1e-9 in every one of the 39 cells.
- **Rung-to-rung relative changes**: recomputed `|hw_now - hw_prev| / hw_prev` for all 13 rows at both
  transitions from the independently-derived half-widths above; matches
  `sr3v3-interval-stability.json`'s `relative_change` to <1e-9 in every cell, and the derived
  `within_rule` flags reproduce the reported counts exactly: **1 of 13 rows within rule at rung 2 (24
  seeds)**, **5 of 13 at rung 3 (48 seeds)** — the same figures cited in the amendment and in
  DEC-20260810-5aeeaa.

## The two headline numbers in `competing_explanation_not_excluded`, recomputed independently

Recomputed directly from `per_seed_ratios` at rung 3 (48 seeds), comparing each seed's value against that
row's own `mean ± z·sd` interval, self-referentially (the extreme is part of the same seed set that fits
the interval, exactly as the amendment frames it):

| row (fb) | n | mean | sd | interval | extreme seed | extreme value | side |
|---|---|---|---|---|---|---|---|
| 11 | 48 | 2.6301 | 0.2184 | [1.9988, 3.2614] | 20260852 | **3.335763** (rounds to 3.3358) | **above**, upper endpoint 3.261373 (3.2614) |
| 22 | 48 | 3.1610 | 0.4675 | [1.8098, 4.5123] | 20260830 | **4.823059** (rounds to 4.8231) | **above**, upper endpoint 4.512253 (4.5123) |

Both figures the amendment cites are confirmed exactly from raw data. A full sweep of all 13 rows at rung
3 finds **no other exceedances in either direction** — total is exactly 2, both upper, none lower,
matching the amendment's claim.

**Claim 1 — count consistency.** Expected count under the Gaussian rule is `13 × 48 / 260 = 2.4`.
Recomputed exactly (both `13*48/260` and the equivalent `Binomial(624, 1/260)` mean). `P(X=2 |
Binomial(624, 1/260)) = 0.2617`, `P(X≤2) = 0.57` (Poisson(2.4) gives the same to 4 places). **The
amendment's claim that the count is consistent and proves nothing is correct** — 2 observed against 2.4
expected sits inside the bulk of the distribution by any reasonable measure.

**Claim 2 — one-sided-pattern probability.** Under a symmetric null, each exceedance is upper or lower
with probability 1/2 independently, so `P(both upper) = 0.5 × 0.5 = 0.25` exactly. **Confirmed exactly as
claimed.** (Note for the record: this is the probability of the *specific* observed pattern "both upper,"
not `P(same side, either direction) = 0.5`; the amendment's arithmetic is for the pattern actually observed
and is internally consistent, but a reader should not conflate the two framings.)

**A qualifier not in the amendment's text, found on independent inspection**: the two rung-3 exceedances
are not two independent pieces of evidence about row 22 specifically — row 22's rung-3 exceedance (seed
20260830, value 4.823059) is the **same seed** that already exceeded row 22's own rung-2 interval
(rung 2: mean 3.1582, sd 0.4968, upper endpoint 4.5941 < 4.823059). Because the ladder is nested, this is
one recurring draw appearing in two overlapping seed sets, not two independent confirmations. It does mean
the same extreme value persisted rather than being diluted as more seeds were added at that row, which is
mildly more consistent with a real tail value than with an isolated fluke — but it should be counted as one
observation, not amplified into two.

## Skewness and tail weight, all 13 rows, all 3 rungs (independently computed, not in either source file)

Per-row biased Fisher-Pearson skewness `g1` and excess kurtosis `g2` at n=12/24/48:

- Rung 3 (48 seeds): **8 of 13 rows positive-skew, 5 negative** (rows 4,5,7,8,9,11,15,22 positive; 6,10,12,13,18
  negative). Individually, only row 22 clears roughly 2×SE(skew) (`g1=1.045`, SE≈`sqrt(6/48)=0.354`,
  z≈3.0) — every other row's per-row skew is within noise for n=48 (SE too large to resolve skew of this
  magnitude at 13 separate rows without correction for multiple comparisons).
- Rung 2 (24 seeds): row 22 shows a markedly strong signal in isolation — `g1=1.769` (z≈3.8 against
  SE≈0.5) and **excess kurtosis `g2=3.64`** (z≈3.6 against SE≈1.0) — clearly non-Gaussian at that one row,
  at that one rung, driven substantially by the single seed 20260830.
- **Pooled, standardized residuals across all 13 rows** (each row's per-seed ratios standardized by its own
  mean/sd, then pooled — a higher-power omnibus check not present in either source file): pooled skewness
  rises with sample size in a way consistent with a real (small) population-level effect rather than pure
  noise — `g1=0.002 (z=0.01)` at rung 1 (n=156 pooled), `g1=0.148 (z=1.07)` at rung 2 (n=312), `g1=0.175
  (z=1.79)` at rung 3 (n=624). **This trend is directionally consistent with mild right skew and does not
  reach conventional significance (z<2) at any rung.** Pooled excess kurtosis stays near zero throughout
  (z=-1.57, 0.61, 0.26) — no pooled evidence of fat tails beyond skew.

**Structural context independent of this run's specific numbers**: `harness/exp_icinv.py:412`
(`binomial_null_verdict`) defines the characterized "variance ratio" as `obs_variance / null_variance`
with the code's own comment `(n-1)*ratio ~ chi2_{n-1}` under the null. A statistic of this family is
asymptotically Gaussian only as degrees of freedom grow; at finite df it carries an intrinsic positive
skew (population skewness of `chi2_df/df` is `sqrt(8/df)`). This is a genuine, data-independent reason to
expect *some* right skew in a variance-ratio statistic's sampling distribution, and it is consistent with
the majority-positive-skew count and the rising pooled-skew trend above. It is **not**, by itself, a
demonstration that the skew is large enough at this statistic's actual (seed-resampling-induced, not
curve-count-induced) degrees of freedom to invalidate the Gaussian tail rule at 259/260 coverage — the two
things are different sampling axes (seed resampling vs. curve count) and the structural argument only
establishes plausibility, not magnitude.

## Rung-to-rung half-width changes vs. the 1/(2·sqrt(n_prev)) noise model

Recomputed the corrected nested-ladder noise scale independently (`1/(2·sqrt(12))=0.1443` at 12→24,
`1/(2·sqrt(24))=0.1021` at 24→48 — matches DEC-20260810-5aeeaa's derivation) and compared it against the
**full distribution** of the 13 rows' relative changes, not just the reported worst row:

| transition | predicted scale | observed mean \|Δ\| (13 rows) | half-normal-predicted mean | observed sd | half-normal-predicted sd |
|---|---|---|---|---|---|
| 12→24 | 0.1443 | **0.1625** (+41% vs. predicted mean) | 0.1152 | 0.0910 | 0.0870 |
| 24→48 | 0.1021 | **0.0788** (−3% vs. predicted mean) | 0.0814 | 0.0554 | 0.0615 |

**This is the most important disconfirming-of-B signal found in this validation.** If the per-row sampling
distribution carried a persistent heavy tail or skew large enough to matter, the excess-over-predicted
noise should show up at *both* transitions, roughly proportionally — a structural property of the data
generating process does not go away as n doubles again. Instead, the aggregate (mean-of-13) relative
change is elevated at the first transition (12→24) but is at or slightly *below* the Gaussian-noise
prediction at the second (24→48), where 11 of 13 rows changed by less than the model's own predicted mean.
Only two rows exceed 1× the predicted scale at 24→48 (row 7 at 2.31×, row 8 at 1.19×) and neither is one of
the two rows flagged for tail exceedances. **The instability at 24→48 that drove F4 is concentrated in a
handful of individual rows crossing the fixed 5% threshold, not in a systematic across-the-board excess
over the noise model at that transition** — which is closer to what ordinary noise plus a hard 5%
cutoff on 13 rows produces than to what a persistent heavy tail would produce.

## Item 4 — is fb=22's largest sd / worst rung-1→2 change structural or expected-under-noise?

- Across the 13 rows at rung 3, row-level mean and row-level sd are positively correlated
  (`Pearson r = 0.658`), which is the structurally expected relationship for a chi-square/variance-ratio
  family statistic (variance of such a statistic scales with its own location under this kind of
  construction) — **not** unique to row 22. Row 18 has an even higher mean (3.43 vs. row 22's 3.16) but a
  much smaller sd (0.336 vs. 0.467) and no exceedance, so the location–scale correlation alone does not
  fully explain row 22's behavior; row 22 remains a mild residual outlier after accounting for it, but not
  a dramatic one.
- Row 22's rung1→2 sd growth (0.3566→0.4968, **+39.3%**) is the largest of the 13 rows by a real margin
  (next is row 15 at +27.0%; most rows are in −20%…+15%). At n=12, the relative standard error of a sample
  sd is on the order of `sqrt(1/(2·11))≈21%`, so a +39% jump for the single largest-of-13 draw is a
  roughly "worst-of-13" outcome under pure sampling noise — comparable in character to the 2.7-SD /
  2.3-SD worst-row figures DEC-20260810-5aeeaa already computed for the half-width changes themselves, and
  not obviously incompatible with chance at that scale (p≈0.08–0.24 by the decision's own max-of-13
  calculation, floors under positive row correlation).
- **Verdict on item 4**: mixed and not decisive either way. Row 22 is genuinely the row with the largest
  variance and the worst instability, which is exactly what "the row with the largest true variance"
  would look like whether the mechanism is ordinary noise (large true variance → large sampling noise in
  the sd estimate) or a genuine heavier/skewed tail localized to that row (plausible given its own rung-2
  skew/kurtosis signal above, which is a real signal on its own terms even if not conclusive about the
  whole gate).

## Overall mechanism verdict

**Inconclusive, on the data available from this one run.** This independent recomputation reproduces
every number the amendment and DEC-20260810-5aeeaa cite, exactly, and does not find grounds to override
either. Specifically:

- The two headline observations in `competing_explanation_not_excluded` (exceedance count, one-sided
  pattern) are, as the amendment itself says, individually unremarkable under the Gaussian rule — confirmed
  by independent recomputation of both probabilities.
- A higher-power pooled-skewness check across all 13 rows (not present in either source artifact) shows a
  directionally consistent, rising-with-n trend toward mild right skew, which is structurally plausible
  given what the characterized statistic actually is (a variance-ratio / chi-square-type quantity, which
  is intrinsically right-skewed at finite degrees of freedom) — but the trend does not reach conventional
  significance at any tested rung (max z≈1.8 at rung 3).
- The rung-to-rung half-width change analysis, extended here to the full 13-row distribution rather than
  only the worst row, argues mildly **against** a persistent heavy tail: the aggregate excess over the
  Gaussian-noise prediction appears at the 12→24 transition but is largely absent at 24→48, where a
  structural, non-vanishing tail effect would be expected to persist.
- Row 22 (the row driving both flagged exceedances) shows a real, isolated non-Gaussian signal at rung 2
  (kurtosis and skewness both several SE from zero), but this is one row out of thirteen and its rung-3
  exceedance is the same recurring seed as its rung-2 exceedance, not independent replication.

**This validation does not return the heavy-tail/skew explanation as established**, so amendment v2's own
stated consequence ("IF IT RETURNS THE HEAVY-TAIL EXPLANATION, THIS AMENDMENT MUST BE WITHDRAWN") is not
triggered by this report. **Nor does this validation clear HEUR-INSTR-4 as confirmed** — the pooled-skew
trend and the row-22-specific non-Gaussian signal are real enough that a Coordinator reading this should
not treat the mechanism question as settled in either direction. The single most informative unresolved
fact is the pooled-skew z-trend (0.01 → 1.07 → 1.79): if it continues to climb through rungs 4–8 at
anything like this rate, HEUR-INSTR-4's own falsification condition in the amendment ("the ratio reported
by E9 D1 stays materially above 1 as n grows") would likely fire before rung 8; if it plateaus or reverses,
that is evidence for HEUR-INSTR-4. **E9's D2 diagnostic (per-row skewness and split-sided exceedance
counts at every rung) is exactly what is needed to track this, and this report's pooled-across-rows
extension of it is offered as a recommended addition if E9 is ever revised** — it is not a change to any
frozen contract, only an observation for whoever next reviews rung-4+ data.

## Limitations

- Single unreplicated run, one prime (p=4001), one geometry, 13 rows, seed rungs 12/24/48 only. Nothing
  here transfers to p=6007 or to rungs 4–8, which do not exist yet.
- All significance/consistency checks above use the same Gaussian/chi-square asymptotic machinery being
  questioned; there is no model-free ground truth available from a single run to definitively settle
  Explanation A vs. B. The pooled-skew check assumes a common standardized shape across the 13 rows, which
  is itself only approximately supported (8:5 sign split, not uniform).
- This report addresses only validation V1 (the mechanism question). It says nothing about validation V2
  (the red-team freeze-question pass), which is a separate, required precondition for approval and is not
  in this session's scope.
- No claim of any kind is made here about H-ICINV-6c7920, EV-ENDO-10109d, endomorphism structure, or any
  curve/class/isogeny/prime, in either direction, at any scale. This report characterizes a diagnostic
  statistic's sampling behavior only.

## Terminal verdict

```yaml
validation_report:
  id: VAL-20260811-v1instr36c8cf
  task_id: V1 (experiments/EXP-INSTR-36c8cf/amendments/v2.yaml validation_required_before_approval)
  run_ids:
    - RUN-INSTR-36c8cf-phaseA-v2-57ca9a
  artifact_checks:
    - "20 contract-required artifacts + 3 declared extras present; manifest source_provenance all_pinned true, dirty false"
    - "snapshot commit 77cd4285 (run) and 60060084 (amendment v2 / DEC) both ancestors of current HEAD; working tree byte-identical to both — no working-tree-only artifact used"
    - "raw-result.json raw.sr3v3_families.4001 structurally equal to sr3v3-reference-sampling.json families.4001 — raw/summary agreement confirmed"
    - "seed nesting confirmed from raw per-seed keys: rung1=12 contract seeds, rung2 adds 20260821-20260832, rung3 adds 20260833-20260856"
  metric_recomputations:
    - "half-width = z*sd recomputed from raw per_seed_ratios for all 13 rows x 3 rungs: matches reported half_width/interval_low/interval_high to <1e-9 in all 39 cells"
    - "rung-to-rung relative_change recomputed independently for all 13 rows x 2 transitions: matches sr3v3-interval-stability.json to <1e-9 in all 26 cells; within_rule flags and row counts (1/13 at rung2, 5/13 at rung3) reproduce exactly"
    - "fb=11 rung3 max per-seed ratio 3.335763 vs interval_high 3.261373, and fb=22 rung3 max 4.823059 vs interval_high 4.512253, both independently confirmed from raw per-seed data"
    - "exceedance sweep of all 13 rows at rung3 confirms exactly 2 exceedances, both upper, none lower -- no other row exceeds"
  control_checks:
    - "C-SEED-STABILITY (interval width vs seed count): recomputed, reproduces reported F4 firing and row-failure counts exactly"
    - "C-SELF-CONSISTENCY: correctly not_evaluated per SR4 (no interval accepted); no widening or gating performed, confirmed from sr3v3-self-consistency.json"
  heuristic_validation_checks:
    - "count consistency claim (2 observed vs 2.4 expected under Gaussian rule, 13*48/260): recomputed exactly; P(X=2|Binomial(624,1/260))=0.2617, P(X<=2)=0.57 -- confirmed unremarkable as claimed"
    - "one-sided pattern claim (P(both upper)=0.25 under symmetry): recomputed exactly as 0.5*0.5=0.25 -- confirmed correct arithmetic; noted this is P(specific pattern), not P(same side)=0.5"
    - "pooled (13-row, standardized-residual) skewness check across rungs 1/2/3: g1=0.002 (z=0.01), 0.148 (z=1.07), 0.175 (z=1.79) -- rising trend consistent with mild right skew, does not reach conventional significance at any rung"
    - "per-row skew/kurtosis at rung3: 8/13 rows positive skew, 5/13 negative; only row fb=22 individually significant (z~3 at rung3, z~3.6-3.8 at rung2 including excess kurtosis 3.64)"
    - "rung-to-rung half-width change vs 1/(2*sqrt(n_prev)) noise model, full 13-row distribution: observed mean exceeds predicted by +41% at 12->24 but is -3% (at or below) predicted at 24->48 -- no persistent cross-transition excess, argues mildly against a structural heavy tail"
    - "structural note: harness/exp_icinv.py binomial_null_verdict defines the characterized statistic as a chi-square-type ratio ((n-1)*ratio ~ chi2_{n-1} per source comment), which is intrinsically right-skewed at finite df -- a data-independent reason B is plausible in principle, not a measurement that it applies at the relevant scale here"
    - "item4 (fb=22 largest sd / worst change): row-level mean-sd correlation r=0.658 across 13 rows is structurally expected for this statistic family; row22 remains a mild residual outlier after accounting for it but its +39% rung1->2 sd growth is consistent with a worst-of-13 draw under pure sampling noise (p~0.08-0.24 per DEC-20260810-5aeeaa's own max-of-13 arithmetic)"
  cost_model_checks: []
  proof_architecture_checks: []
  mechanism_verdict: inconclusive
  mechanism_verdict_detail: >-
    Neither HEUR-INSTR-4 (ordinary sampling noise) nor the competing heavy-tail/skew explanation is
    established by this run's data. The amendment's own two headline numbers (exceedance count and
    one-sided pattern) are confirmed exactly and are, as the amendment says, individually unremarkable.
    An independent higher-power pooled-skew check across all 13 rows finds a directionally consistent
    but not-yet-significant rising trend toward right skew (z 0.01 -> 1.07 -> 1.79 across rungs 1/2/3),
    structurally plausible given the characterized statistic is a chi-square-type ratio. A full-distribution
    (not worst-row-only) check of rung-to-rung half-width changes against the predicted noise scale finds
    excess variability at the 12->24 transition but not at 24->48, which argues mildly against a persistent
    heavy tail. This validation does NOT return the heavy-tail explanation as confirmed, so amendment v2's
    own stated withdrawal trigger is not activated by this report; it also does not clear HEUR-INSTR-4.
    The pooled-skew z-trend across future rungs (if the amendment is ever approved and executed) is the
    single most informative quantity to track next.
  verdict: passed
  verdict_note: >-
    "passed" describes the ADMISSIBILITY of RUN-INSTR-36c8cf-phaseA-v2-57ca9a as a receipt (artifacts
    complete, hashes pinned, seeds nested and verified, environment and resources recorded within budget,
    every cited metric independently recomputed from raw per-seed data and reproduced exactly) and the
    completeness of the V1 recomputation task itself (all raw data needed was present and was used; no
    missing measurement was substituted). It does NOT mean HEUR-INSTR-4 is validated, does NOT mean the
    competing explanation is excluded, and per AGENTS.md / agents/validator.md does NOT authorize
    amendment approval, promotion, or any curve-side or ECDLB claim. See mechanism_verdict above for the
    substantive question V1 was asked to answer, which is INCONCLUSIVE.
  limitations:
    - "single unreplicated run, one prime (p=4001), seed rungs 12/24/48 only; nothing here transfers to p=6007 or to rungs 4-8"
    - "all consistency checks use Gaussian/chi-square asymptotic machinery; no model-free ground truth is available from one run to definitively settle Explanation A vs B"
    - "pooled-skew check assumes a common standardized shape across the 13 rows, only approximately supported (8:5 sign split at rung3)"
    - "this report addresses V1 only; V2 (red-team freeze-question pass) is a separate required precondition not in this session's scope"
    - "no claim of any kind about H-ICINV-6c7920, EV-ENDO-10109d, endomorphism structure, or any curve/class/isogeny/prime, in either direction, at any scale"
  artifact_paths:
    - experiments/EXP-INSTR-36c8cf/amendments/v2.yaml
    - experiments/EXP-INSTR-36c8cf/amendments/v1.yaml
    - experiments/EXP-INSTR-36c8cf/specification.yaml
    - ledger/decisions/DEC-20260810-5aeeaa.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/manifest.yaml
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/raw-result.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-reference-sampling.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-interval-stability.json
    - experiments/EXP-INSTR-36c8cf/runs/RUN-INSTR-36c8cf-phaseA-v2-57ca9a/sr3v3-self-consistency.json
    - harness/exp_icinv.py
```
