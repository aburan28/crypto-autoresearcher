# Detection-rate report — V3 planted-correlation control arm (TASK-20260806-e1700f)

**Task** `TASK-20260806-e1700f` (executor) · **Batch** `BATCH-f8050e` ·
**Goal** `GOAL-HQC-001` · **Design** `design.md` (frozen 2026-08-06T17:45:37Z,
before either authorized run) · **Script** `planted_arm_v3.py`
(sha256 `f21ba4c369a1c4a078409d8e7525a2f82a3e82a9b211b405809818b90952ec51`) ·
**Raw data** `detection_results.json`
(sha256 `35ee2abc686dfb8100cba58f1cbc789d669c11ee53a668b9031eb8ad847c2ebd`) ·
**Authorized command**
`PYTHONDONTWRITEBYTECODE=1 python3 planted_arm_v3.py --mode detection --out-dir .`,
executed exactly once (`run_manifest.yaml`).

**This is the SEPARATE detection-rate deliverable, distinct from the main
MATCH/MISMATCH run (`planted_results.json`).** It does not report or restate
the main run's MATCH/MISMATCH result beyond a one-line cross-reference at the
end of this document.

This is an OBSERVATION report. It reports a measured rate and its
uncertainty, and an explicit numeric comparison against the Red Team's
independently measured baseline. It draws no conclusion about A17, HQC's
decoding-failure rate, any standardized parameter set, or OPEN-6's
disposition — those judgements belong to the Coordinator and the two
independent reviewers dispatched after this task
(`TASK-20260806-cdc631` validator, `TASK-20260806-7008de` red team). Claim
tier: **TOY**.

---

## 1. What was measured

The construction (`design.md` Section 3): for every block position with an
intended decode label (fail/succeed) fixed by the same exchangeable
position-marking mechanism V1/V2 used (`M_t ~ Uniform{17,18,19}`), a fresh
128-bit i.i.d. Bernoulli(0.35) candidate is drawn and decoded with the REAL
`stage_a.py` `decode_blocks`; it is accepted only if the true decode matches
the intended label, otherwise redrawn. This produces genuinely heterogeneous,
per-position, per-trial content (confirmed distinct: 10,000/10,000 sampled
accepted blocks were pairwise distinct in the main run, `planted_results.json`
`generation.ensemble_distinctness_check`), unlike V2's two fixed templates.

The perturbation (`design.md` Section 5.1, identical definition to V2's
`shift_read_one_early`): a block drops its own true last bit and gains a
foreign bit (from a neighboring position) at the front — the literal shape of
the campaign's V1 (global off-by-one) and V3 (last-block-early) defect
classes. A position **FLIPS** if its decoded label under the perturbed
content differs from its (rejection-sampling-guaranteed) unperturbed intended
label.

Two components were run, in the SAME authorized script invocation, from
independently seeded batches (`run_manifest.yaml` seeds):

- **Component A** (interior position pair, positions 9→10): the primary,
  cheapest-to-scale measurement, directly comparable in shape to the Red
  Team's own "position-generality probe" (`red_team_report.md` Section 1).
  Achieved `T = 2,000,000` trials, no truncation.
- **Component B** (full 56-position ensemble): matches the campaign's own
  named "global off-by-one" (V1) and "last-block-early" (V3) defect shapes
  exactly, using the real tiled-neighbor structure. Achieved `T = 100,000`
  trials, no truncation.

---

## 2. Headline results

All confidence intervals are Wilson score 95% intervals on a binomial
proportion; a normal-approximation ±3 jackknife-style SE band (this
campaign's own 3-SE convention) is also reported. Full counts and both
interval types are in `detection_results.json`.

### 2.1 Component A — interior position (9 → 10), `T = 2,000,000`

| variant | condition | flips / n | rate | Wilson 95% CI | ±3 SE band |
|---|---|---|---|---|---|
| paired_neighbor (foreign bit = position 9's own accepted last bit, same trial) | unconditional | 209,324 / 2,000,000 | **10.4662%** | [10.4239%, 10.5087%] | [10.4013%, 10.5311%] |
| paired_neighbor | margin ≤ 4 | 177,819 / 883,900 | **20.1175%** | [20.0341%, 20.2012%] | [19.9896%, 20.2455%] |
| independent_foreign_bit (foreign bit = fresh, unconditioned Bernoulli(0.35) draw) | unconditional | 209,278 / 2,000,000 | **10.4639%** | [10.4216%, 10.5064%] | [10.3990%, 10.5288%] |
| independent_foreign_bit | margin ≤ 4 | 177,751 / 883,900 | **20.1099%** | [20.0264%, 20.1935%] | [19.9820%, 20.2378%] |

The two foreign-bit variants (`paired_neighbor` — the ensemble-faithful
choice — vs. `independent_foreign_bit` — replicating the Red Team's own
stated "random foreign bit" methodology as closely as this arm's record of
it allows) agree with each other to within 0.002-0.008 percentage points,
far inside either variant's own CI. Whatever difference this methodological
choice could in principle make, it was not detectable at `T = 2,000,000`.

### 2.2 Component B — full 56-position ensemble, `T = 100,000`

| variant | condition | flips / n | rate | Wilson 95% CI | ±3 SE band |
|---|---|---|---|---|---|
| global off-by-one (all 56 positions, circular) | unconditional | 588,492 / 5,600,000 position-observations | **10.5088%** | [10.4834%, 10.5342%] | [10.4699%, 10.5477%] |
| last-block-early (position 55 only) | unconditional | 10,685 / 100,000 trials | **10.685%** | [10.4950%, 10.8798%] | [10.3919%, 10.9781%] |

The `global` and `last-block-early` rates (10.51%, 10.69%) and both Component
A unconditional rates (10.46%, 10.46%) are mutually consistent — all four
independent measurements, from three different generation batches and two
different perturbation shapes, cluster in a **10.5-10.7%** band.

---

## 3. Explicit numeric comparison against the Red Team's baseline (`EV-HQC-9a30d3`)

The Red Team (`TASK-20260806-ae74c4`, `red_team_report.md` Section 2)
independently measured, on 300,000 UNCONDITIONED i.i.d. Bernoulli(0.35)
128-bit blocks (no rejection sampling — every drawn block was used,
regardless of what it decoded to), the natural single-position
"read-one-early" flip rate:

```
unconditional:        ~8.8%
margin (<=4) conditioned: ~19.6%
```

| comparison | this arm (Component A, paired_neighbor) | Red Team baseline | absolute difference | this arm's rate ÷ baseline | distance in this arm's own SE |
|---|---|---|---|---|---|
| unconditional | 10.4662% [10.42%, 10.51%] | 8.8% | +1.67 pp | 1.19x | ≈77 SE (this arm's `se_normal_approx=0.000216`) |
| margin ≤ 4 conditioned | 20.1175% [20.03%, 20.20%] | 19.6% | +0.52 pp | 1.03x | ≈12.2 SE (this arm's `se_normal_approx=0.000426`) |

Both figures are **many SE away from the Red Team's point estimate at this
arm's own achieved sample size** (a direct consequence of `T = 2,000,000`
giving a very narrow CI, not evidence of a large practical difference) — the
practically-scaled comparison is the "absolute difference" / "rate ÷
baseline" columns, not the SE-distance column. On that practically-scaled
reading:

- The **unconditional** rate (~10.5%) is measurably, consistently higher
  than the Red Team's 8.8% baseline across all four independent measurements
  in this report (10.46-10.69%), by roughly 1.2x.
- The **margin-conditioned** rate (~20.1%) is close to the Red Team's 19.6%
  baseline, within about 3% relative difference — much closer than the
  unconditional figures are.
- **Neither figure is remotely close to V2's demonstrated 100%.** Both this
  arm's rate and the Red Team's baseline are roughly an order of magnitude
  below V2's two-fixed-template result, consistent with the Red Team's own
  finding that V2's 100% was an artifact of hand-searching for a worst-case
  pair (`red_team_report.md` Section 2).

---

## 4. The rejection-sampling margin distribution, measured directly (bearing on possible rejection-sampling bias)

This arm's TARGET-position (position 10) accepted content's WHT margin
(`top1 - top2` of `|wht128(...)|`, computed via `stage_a.py`'s `wht128`
directly, `design.md` Section 5.2 step 3), measured over all `T = 2,000,000`
Component A trials:

| statistic | this arm (rejection-sampled, label-conditioned) | Red Team `EV-HQC-9a30d3` (unconditioned Bernoulli(0.35)) |
|---|---|---|
| min | 0 | 0 |
| median | 8.0 | 8.0 |
| mean | 9.790 | 10.70 |
| max | 68 | 60 |
| fraction margin ≤ 4 | 44.195% | 38.8% |

This arm's accepted-content margin distribution has a **modestly smaller
mean** (9.79 vs. 10.70) and a **modestly larger fraction near the decision
boundary** (44.2% vs. 38.8% at margin ≤ 4) than the Red Team's unconditioned
population. This is directionally consistent with — and offered here as a
candidate, not asserted, explanation for — this arm's somewhat higher
UNCONDITIONAL flip rate (10.5% vs. 8.8%): conditioning accepted content on
"true decode matches the intended label" (this arm's rejection-sampling
criterion) appears to shift the accepted population slightly closer to the
WHT decision boundary than an unconditioned Bernoulli(0.35) draw, on average.
This arm does **not** establish causality here, only reports the two
measured margin distributions side by side; whether this fully explains the
~1.2x unconditional-rate gap, and whether it constitutes a should-be-corrected
bias or simply reflects what a genuinely label-matching population looks
like, is left to `TASK-20260806-7008de` (this batch's Red Team dispatch,
charged specifically with probing rejection-sampling bias) and
`TASK-20260806-cdc631` (Validator).

Notably, once content is ALSO conditioned on margin (the margin-conditioned
row of Section 3), the residual gap between this arm's rate (20.1%) and the
Red Team's (19.6%) shrinks to ~3% relative — much smaller than the
unconditional gap (~19% relative) — consistent with (though not proof of) the
margin-distribution difference being the dominant driver of the unconditional
gap.

---

## 5. What this experiment does NOT establish (design.md Section 5.4/7, restated)

- This is a **block-level flip-rate** measurement, not a measurement of the
  full-arm `log2_Ahat_k` estimator's response to an injected defect. A high
  or low block-level flip rate is suggestive but distinct from what the
  campaign's estimator would show if a defect were injected into a full run
  and re-measured end-to-end (the kind of experiment the Red Team ran
  against V1's and V2's own fixed-template constructions).
- The real cryptographic `(T)`-sampler (`CTRStream`, `fixed_weight_support`,
  ring arithmetic) is still never run. This arm constructs planted content
  via rejection sampling from an i.i.d. Bernoulli(0.35) PROXY distribution,
  verified only against the decode label — not by sampling a genuine
  fixed-weight-support-derived `(T)`-distributed error vector end-to-end.
- The rejection-sampling-bias question (Section 4 above) is instrumented,
  not resolved, by this report.
- This report makes no claim about which of the `paired_neighbor` /
  `independent_foreign_bit` foreign-bit conventions is "more correct" —
  both are reported because the difference between them was named, in
  advance (`design.md` Section 5.2), as a disclosed methodological choice
  worth checking; in this run they agreed to within noise.

---

## 6. Cross-reference to the main run (not restated in detail here)

The SEPARATE main run (`planted_results.json`, this task's other authorized
invocation) reports 17/17 cells (k=2..18) MATCH the closed-form planted
`log2_A_k(k)` within the campaign's 3-jackknife-SE band, at `T = 500,000`,
using the SAME rejection-sampling construction (unperturbed). That is a
different statistic (the full-arm estimator against the UN-perturbed
construction) from this report's (block-level flip rate under an INJECTED
perturbation), and the two are not combined into a single number anywhere in
this task's artifacts, per `design.md` Section 0's binding requirement to
keep the two deliverables distinct.

---

## 7. Execution count and validity

Both components ran in the single `--mode detection` authorized invocation
(`run_manifest.yaml` `execution_count`), executed exactly once. Neither
component was wall-clock-truncated. `detection_results.json` `validity.status
= valid_measurement` for both components. Core-seconds spent: 274.7 of an
800-core-second allocation (this task's own split of the 1800-core-second
total budget, `design.md` Section 6); wall-clock: 274.4s of a
1500-second allocation. Full budget accounting, seeds, and fail-closed-check
firing status (none fired) are in `run_manifest.yaml`.

---

## 8. Scope

TOY. Nothing here is a statement about HQC, A17, A5, any decoding-failure
rate, or any standardized parameter set. I hold no authority to change
research status and changed none. This report presents observations
(measured rates, confidence intervals, and numeric comparisons) only;
whether this arm's measured detection rate, taken together with the main
run's MATCH/MISMATCH result and the rejection-sampling margin-distribution
finding (Section 4), closes, partially closes, or leaves open OPEN-6 is a
judgement for the Coordinator and the two independent reviewers dispatched
after this task.
