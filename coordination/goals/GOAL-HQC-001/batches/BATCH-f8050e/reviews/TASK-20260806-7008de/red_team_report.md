# Red-team report — V3 planted-correlation control arm for OPEN-6 (TASK-20260806-e1700f)

**Task** `TASK-20260806-7008de` (red team) · **Batch** `BATCH-f8050e` · **Goal**
`GOAL-HQC-001` · **Reviews** `TASK-20260806-e1700f`'s Coordinator-committed
snapshot (commit `ef4c50e7`, parent `d1311591`, `snapshot-receipt.json`
verified — all ten declared `path_sha256` values recomputed and match).
Produced 2026-08-06.

**Frozen artifacts read.** `design.md`, `planted_arm_v3.py`,
`planted_results.json`, `detection_results.json`, `detection_rate_report.md`,
`run_manifest.yaml` under
`coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/`.
I also re-read `ledger/evidence/EV-HQC-9a30d3.yaml`, my own prior report
(`TASK-20260806-ae74c4`), `DEC-20260806-cf5102`, and `stage_a.py`'s
`decode_blocks`/`wht128` (`BATCH-6fddee/TASK-20260806-64b506`) and
`measure.py` directly, independent of this task's own narration of them. I
deliberately did **not** read the Validator's report
(`TASK-20260806-cdc631`, already present on disk when I started) —
independent session, no conferring, the same discipline my V2 report used.
I modified none of the frozen artifacts. All my own verification code lives
in scratch space (`/tmp/.../scratchpad/rt_v3_bias.py`,
`rt_v3_direct.py`, `rt_v3_clustering.py`), not committed.

Both reused source files' sha256 were independently recomputed by me and
match what `planted_arm_v3.py` pins: `stage_a.py` →
`06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`;
`measure.py` → `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`.
No drift from V1/V2/V3's shared pins.

---

## VERDICT

# **ADMIT the artifacts. OPEN-6: PARTIALLY CLOSED, but by materially less than the "10.5% ≈ 8.8%, confirmed" framing suggests — I found and precisely quantified the rejection-sampling-bias mechanism the executor flagged as unresolved, and it turns out to be a complete, closed-form-arithmetic explanation of the entire gap, not a residual "somewhat closer" concern. The control-arm lineage (V1→V2→V3) has reached its ceiling; a V4 of the same shape should not be dispatched.**

---

## 1. Rejection-sampling bias: quantified, not merely bounded, and it fully explains the gap

This was the task's central question and I answer it directly, with two
independent reimplementations (not an audit of the executor's code — a
from-scratch reproduction using only the sha256-pinned `decode_blocks`/
`wht128`).

### 1.1 The mechanism

`design.md` §3.2 reports that raw, unconstrained Bernoulli(0.35) content
decodes to `F=1` ("fail") only **21.1%** of the time under the real decoder,
while the position-marking mechanism (`M_t ~ Uniform{17,18,19}` failing
positions out of 56) requires **q = 9/28 ≈ 32.14%** of positions to carry
the fail label. Rejection sampling therefore does not draw a representative
sample of "natural" content — it draws content **conditioned on a decode
label**, and then **mixes** the fail-conditional and succeed-conditional
populations at the *required* ratio (32.1%/67.9%), not the *natural* ratio
(21.1%/78.9%). If fail-labeled and succeed-labeled content have different
margin/flip characteristics — which they do, dramatically — this reweighting
alone will shift the aggregate statistics, with no other distortion needed.

### 1.2 Direct measurement of the two strata (my own script, `rt_v3_bias.py`, independent seed, T=4,000,000 unconditional Bernoulli(0.35) draws, real `decode_blocks`/`wht128`, single-position "read-one-early" perturbation with an independent fresh foreign bit)

| quantity | fail-labeled (21.1% of raw pop.) | succeed-labeled (78.9% of raw pop.) |
|---|---|---|
| mean margin | **4.27** | **12.42** |
| fraction margin ≤ 4 | 76.6% | 28.8% |
| unconditional flip rate | **20.81%** | **5.60%** |

Fail-labeled content sits almost 3x closer to the WHT decision boundary on
average and flips almost 4x more often than succeed-labeled content. This is
the entire mechanism: whichever label is over-represented relative to its
natural frequency, the aggregate statistics move toward that label's
(margin, flip-rate) profile.

**Sanity check — reconstructing the Red Team's own V2-batch baseline from
these two strata, weighted by their *natural* (measured, not assumed)
frequencies:**

| quantity | reconstructed (natural weights 21.1%/78.9%) | Red Team `EV-HQC-9a30d3` (independent 300k-sample measurement) |
|---|---|---|
| mean margin | 10.70 | 10.70 |
| fraction margin ≤ 4 | 38.88% | 38.8% |
| unconditional flip rate | 8.81% | 8.8% |

Exact agreement (my reconstruction uses a completely different 4,000,000-
sample run than the original 300,000-sample measurement, on a different
seed). This confirms both measurements are sampling the same real
distribution and that my stratification is correct.

**The actual test — reconstructing V3's rejection-sampled figures using the
*required* weights (q=9/28, 19/28) applied to the *same two strata*:**

| quantity | predicted from reweighting (q=9/28) | V3's own reported figure (`detection_results.json`, T=2,000,000) |
|---|---|---|
| mean margin | 9.80 | **9.79** |
| fraction margin ≤ 4 | 44.15% | **44.195%** |
| unconditional flip rate | 10.486% | **10.4662%** (paired) / 10.4639% (independent) |
| margin ≤ 4-conditioned flip rate | 20.145% | **20.1175%** (paired) / 20.1099% (independent) |

Every predicted figure lands within **0.02 percentage points** of V3's own
reported number — well inside sampling noise given my 4,000,000-sample
stratified estimate versus V3's 2,000,000-sample aggregate. **The entire gap
between V3's ~10.5% and the Red Team's own ~8.8% baseline is fully,
quantitatively explained by one closed-form fact — q (9/28, chosen so the
planted marginal law has a tidy 3-point support) does not equal the natural
Bernoulli(0.35) fail-decode frequency (0.211) — with no residual left to
attribute to anything else.**

### 1.3 Direct (non-reweighted) reproduction, as a second, independent check

I also built the rejection-sampling construction itself from scratch
(`rt_v3_direct.py`, T=1,000,000, independent seed, own vectorized
redraw-only-pending loop, not copied from `planted_arm_v3.py`): draw label
~ Bernoulli(q=9/28), rejection-sample content, decode with the real
`decode_blocks`, apply `shift_read_one_early` with an independent foreign
bit, record flips.

| quantity | my direct reproduction (T=1,000,000) | V3's reported figure |
|---|---|---|
| mean draws/accepted block | 2.3801 | 2.382 |
| mean margin | 9.8053 | 9.790 |
| fraction margin ≤ 4 | 44.18% | 44.195% |
| unconditional flip rate | 10.468% ± 0.031% (1 SE) | 10.4639% (independent_foreign_bit) |
| margin ≤ 4 flip rate | 20.089% ± 0.060% (1 SE) | 20.1099% (independent_foreign_bit) |

Both independent methods (reweighting-from-strata and direct
reconstruction) agree with V3's own reported figures to well within their
own sampling noise. **The construction and its reported numbers are genuine,
reproducible, and not the product of an implementation bug — but the
"rejection-sampling bias" the executor flagged as a live, unresolved
question is real, large enough to be the entire story, and now fully
explained rather than merely bounded.**

### 1.4 What this means for the interpretation, not just the number

`detection_rate_report.md` §4 and §3 present the ~10.5% figure as "directly
comparable" to the Red Team's ~8.8% baseline and frame the margin-mean
difference as a "candidate, not asserted-causal" explanation of a "~1.2x
gap." That is too cautious in one direction and slightly mis-scoped in
another:

- It is **not** a candidate explanation any more — I have shown it is a
  *complete* one, closed-form-predictable from a single already-known
  quantity (q = 9/28) and the natural label split (0.211/0.789) that
  `design.md` §3.2 itself already measured before this task's own review.
- But precisely *because* it is a complete, mechanical explanation, the two
  numbers (8.8% and 10.5%) are **not** two independent estimates of the same
  underlying quantity that happen to be close — they are estimates of two
  *different* quantities: "flip rate of a randomly-decoding Bernoulli(0.35)
  block" versus "flip rate of a Bernoulli(0.35) block conditioned to decode
  to a label drawn at the *toy* rate q=9/28 that this campaign's marking
  mechanism happens to need for its {17,18,19}-support closed form." Neither
  is closer to "what a real HQC decoding-relevant error vector's flip rate
  would be" — q=9/28 has no established connection to any real per-block
  HQC decoding-failure probability (which is astronomically smaller; this is
  the whole reason A17/OPEN-6 exists), and 0.211 is simply an artifact of
  choosing Bernoulli(0.35) as an ad hoc "realistic-noise" content proxy. Both
  are toy quantities; V3's is not an upgrade on the Red Team's, it is a
  *different, precisely related* toy quantity now under complete
  arithmetic control.

---

## 2. Confidence-interval honesty: Component A/B are correctly Wilson-sized; I checked the one place clustering could bite, and it does not

**Component A** (interior-position pair, T=2,000,000) and **Component B's
"last-block-early"** (T=100,000) each contribute exactly **one** flip
observation per independently-generated trial. There is no clustering
concern for either — a standard Wilson interval on `n` independent trials is
the right tool, and I re-derived the point estimates independently in §1.3
above at the shown precision.

**Component B's "global off-by-one" statistic is the one place a real
concern exists**, and the task explicitly asked me to check it: it pools
`56 × 100,000 = 5,600,000` "position observations" from only 100,000
independent *trials*, and each trial's 56 positions share (a) a mildly
negatively-correlated joint label structure (labels are a uniform
size-`M_t` subset of 56 positions drawn without replacement) and (b) a
ring/necklace perturbation structure (position `j`'s foreign bit is position
`j-1`'s own accepted content, so neighboring positions' flip outcomes are not
generated from disjoint randomness). Treating 5,600,000 pooled observations
as i.i.d. Bernoulli trials could, in principle, understate the true
uncertainty by a substantial factor if within-trial correlation were
material.

I tested this directly (`rt_v3_clustering.py`): built 20,000 independent
full 56-position trials from scratch (own rejection-sampling loop, own
`draw_block_fail`), applied the identical global perturbation, and compared
the **true** per-trial-cluster variance of the flip count `X_t` (0..56)
against the **naive** binomial variance `56·p̂·(1−p̂)` that an i.i.d.
assumption would predict:

```
p_hat (global flip rate, my own 20,000-trial run) = 0.105183
Var(X_t) empirical                                = 5.0389
Var(X_t) under the naive i.i.d.-position assumption = 5.2707
design effect (true/naive)                         = 0.956
SE understatement factor                           = 0.978x  (i.e. NO understatement)
```

**Result: the concern does not materialize for this construction.** The true
cluster-robust standard error is actually ~2% *smaller* than the naive
one — a small, statistically resolvable (T=20,000 gives enough precision to
distinguish 0.956 from 1.0) but practically negligible *negative*
correlation, consistent with the label-subset's mild negative correlation
dominating over any positive correlation the neighbor-chained perturbation
might induce. **The reported Wilson CI on the "global" statistic
(10.5088% [10.4834%, 10.5342%]) is honestly, even mildly conservatively,
sized — I looked for exactly the failure mode named in this task's handoff
and did not find it.** I report this as a genuine negative result, not a
manufactured one: my first script draft computed a spurious "design effect
= 2998" from a units bug (dividing `Var(X_t)` by `p(1−p)/56`, a mean-level
variance, instead of `56·p(1−p)`); the corrected computation above is what I
report, and the independently-computed SE-ratio (0.978x, matching
√0.956 ≈ 0.978) cross-checks it.

---

## 3. "Identical pipeline" claim: still holds, no drift

`decode_blocks` and `wht128` sha256 match the pinned values V1/V2/V3 all
share; I recomputed both independently. `planted_arm_v3.py`'s reuse of
`measure.comb_matrix`/`measure.log2_A_from_hists` (main run only, not
exercised by the detection-rate experiment, which is block-level and does
not call the jackknife estimator) matches the same pattern V1/V2 used, with
the same disclosed nuance (the histogram is accumulated from this task's own
per-batch generator, not literally `measure.py`'s own monolithic
`S_all`/lines 730-733 execution path) that my V1 and V2 reports already
flagged and found unproblematic. Nothing new here.

I also spot-checked `planted_results.json`/`detection_results.json`
directly (not just the two `.md` reports) and confirm every headline number
in `detection_rate_report.md` and `run_manifest.yaml` is present and
consistent in the raw JSON: `T_achieved` for Component A/B (2,000,000 /
100,000), the `paired_neighbor` unconditional Wilson record
(`k=209324, n=2000000, phat=0.104662, wilson95=[0.10424,0.10509]`), the
margin statistics (`mean=9.78997, fraction_margin_le_threshold=0.44195`),
and the main run's `cells_match=17/17`. No discrepancy between raw data,
`.md` narrative, and `run_manifest.yaml`'s execution count (2 authorized
runs, reported identically in both places) — the V1 arm's carried-forward
run-count discrepancy is not repeated here.

---

## 4. Does this actually tell the campaign much it didn't already suspect?

**Mostly confirmation, with one genuinely new and useful finding, honestly
assessed either way.**

What is genuinely new:

- A calibrated **rate with a tight CI** (10.4662% ± 0.04pp, Wilson 95%) at
  T=2,000,000, replacing V2's structurally-forced {0%, 100%}. This is real
  progress on exactly the axis both prior reviewers named as missing, and it
  is achieved with a construction (rejection sampling, verified genuinely
  heterogeneous — 10,000/10,000 distinct sampled blocks) that is a
  categorical improvement over V2's two fixed templates.
- The precise, closed-form account of *why* V3's rate differs from the Red
  Team's V2-batch rate (§1 above) — this was not previously known and is a
  useful methodological finding in its own right: it exposes a
  never-reconciled inconsistency, present since V1, between the toy
  marking-mechanism's required label frequency (q=9/28) and the "realistic
  noise" content proxy's (Bernoulli(0.35)) natural label frequency (0.211).

What is not new: once §1's decomposition is available, V3's headline
number carries almost no information beyond arithmetic recombination of
quantities the Red Team's own V2-batch 300,000-sample measurement already
established (the natural per-label margin/flip statistics) plus a quantity
already fixed by design since V1 (q). The order-of-magnitude conclusion —
"detection is possible but occurs at roughly 10%, not 100%, under content
that looks like this campcampaign's own realistic-noise proxy" — was
already the Red Team's V2-batch finding. V3 sharpens the estimate's
precision and formal calibration; it does not move the substantive
conclusion.

---

## 5. OPEN-6 disposition and the diminishing-returns reckoning (`DEC-20260806-cf5102` requires this explicitly)

**PARTIALLY CLOSED — real but smaller incremental progress than the "10.5%
≈ 8.8%, confirmed by an independent construction" framing implies, because
§1 shows the two numbers are not independent confirmations of the same
quantity; they are exactly-related toy quantities differing by one
already-known constant.**

What is now established that was not established after V2: a genuinely
heterogeneous ensemble *can* produce a calibrated detection rate (not just
{0%,100%}), and doing so does not, itself, introduce any hidden or
unaccounted-for distortion — the one distortion it does introduce
(the q-vs-0.211 label-mix effect) is now fully characterized, not merely
suspected. That is real, honest, useful progress, and I ADMIT it.

What remains untouched, unchanged since V1: the real cryptographic
`(T)`-sampler (`CTRStream`, `fixed_weight_support`, `ring_mul_sparse`/
`ring_mul_dense`) has never been run, across three generations of this
control arm. `S_t`'s support is still the toy 3-point set {17,18,19}
against PS-R3's real near-binomial spread over most of {0,...,56}. The
detection-rate experiment still measures a block-level flip rate, not the
full-arm `log2_Ahat_k` estimator's response to an injected defect end to
end. None of these are new residuals — all three were already named after
V1 and V2 and restated, honestly, in this arm's own `design.md` §7.2.

**On the ceiling question `DEC-20260806-cf5102` requires be confronted
directly: yes, this control-arm lineage has reached its ceiling, and this
batch's own result is itself the sharpest evidence for that conclusion.**
V3's headline "new" measurement — built with materially more machinery than
V2 (rejection sampling, redraw-until-match, a two-variant foreign-bit
design, margin instrumentation) and using 6.7x the Red Team's original
sample size — turns out, on inspection, to be **fully decomposable into
information the V2-batch Red Team review had already produced**, plus one
already-fixed design constant. That is close to a textbook diminishing-
returns signature: each control-arm generation since V1 has closed one
narrowly-scoped methodological gap (V1→V2: real decoder; V2→V3: a
calibrated rate instead of {0,100%}), while the actual object of concern —
whether a subtle bug in the *real* generation path explains PS-R3's
anti-correlation signal — has not moved at all, because no generation of
this lineage has ever executed that real path. A V4 that further refines
the toy content model (e.g., matching q to 0.211, or widening the marking
mechanism's support toward PS-R3's real near-binomial spread) would likely
repeat this pattern: technically real progress on a narrowly-scoped
methodological question, arithmetically recoverable from what is already
known, and still silent on the actual sampler. **I recommend against
dispatching a V4 of this shape.** The next control that would add genuine
new information is the one all three generations' own honest disclosures
have named and none has attempted: inject the V1/V3-class boundary/index-
shift defect directly into the real `CTRStream`/`fixed_weight_support`/ring-
arithmetic pipeline (even at reduced, toy-budget scale) and measure whether
it propagates to a `log2_Ahat_k`-level or `qhat`-level deviation there — a
qualitatively different experiment from anything in the V1–V3 lineage, not
a fourth iteration of the same toy content-model apparatus.

---

## 6. Baseline and cost-model notes (`agents/red-team.md` contract)

**Baseline comparison.** Not a Pollard-rho/BSGS-class claim; toy-tier HQC
decoder-statistic instrument check. Closest analogue remains `CTRL-POSHOM`'s
own measured real-crypto-data marginal shifts under V1/V2/V3-class defects
(−0.0243%, −0.0566%, +0.0015%, per my V1 report), still two to three orders
of magnitude smaller than any of this lineage's own toy-arm shifts —
reinforcing, again, that none of V1/V2/V3's own internal sensitivity figures
transfer to the real pipeline's actual noise floor.

**Cost-model / heuristic challenges.** Not applicable in the exponent-first
Wesolowski-profile sense.

**Budget.** Authorized 1,800 wall-clock seconds. My three verification
scripts measured wall-clock: `rt_v3_bias.py` 97.4s, `rt_v3_direct.py` 21.9s,
`rt_v3_clustering.py` 28.4s — **≈147.7 seconds of compute, ≈8% of the
1,800-second budget. No overrun.** No result was trimmed or subsampled to
fit budget; T's (4,000,000 / 1,000,000 / 20,000 trials respectively) were
chosen for statistical adequacy, not budget pressure, and there was ample
remaining budget to go larger had it been needed.

---

## 7. Cheapest next concrete action

Do not dispatch a V4 of the same shape (fixed template → heterogeneous
rejection-sampled ensemble → [next refinement of the same toy content
model]). Dispatch, instead, a defect-injection experiment against the real
`(T)`-sampler path (`CTRStream`/`fixed_weight_support`/ring arithmetic) at
whatever reduced toy scale the budget allows: inject the same boundary/
index-shift perturbation this lineage has used throughout (V1 global,
V3 last-block-early) directly into that real generation path, and measure
whether it propagates to a detectable deviation in `qhat`/`log2_Ahat_k`
computed the same way PS-R3's real pipeline computes it. This is the
control every generation of this lineage has correctly and consistently
named as still-missing; it is the one this batch's own result shows the
toy-content-model lineage can no longer substitute for.

---

## 8. Scope

TOY. Nothing here is a statement about HQC, A17, A5, any decoding-failure
rate, or any standardized parameter set. I hold no authority to change
research status and changed none. All committed artifacts under
`TASK-20260806-e1700f` were read only, not modified; my verification scripts
live in this session's scratch space
(`/tmp/.../scratchpad/rt_v3_bias.py`, `rt_v3_direct.py`,
`rt_v3_clustering.py`) and are not part of the durable research record — the
numeric results transcribed in §§1-2 are what carries the finding forward.

---

## 9. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-7008de
  task_id: TASK-20260806-7008de
  claim_under_review: >-
    The V3 planted-correlation control arm (TASK-20260806-e1700f, snapshot
    ef4c50e7) replaces V2's two fixed templates with a genuinely
    heterogeneous, rejection-sampled per-position/per-trial content ensemble
    and reports a calibrated boundary-shift detection rate of ~10.47%
    (Component A, T=2,000,000, unconditional), ~1.19x the Red Team's own
    independently-measured ~8.8% natural-content baseline (EV-HQC-9a30d3),
    with the executor explicitly flagging its accepted-content margin shift
    (mean 9.79 vs. 10.70) as a candidate, unresolved rejection-sampling-bias
    concern for this review to probe.
  objections:
    - "The rejection-sampling bias the executor flagged as a live, unresolved
      concern is real and turns out to be a COMPLETE explanation of the
      ~1.2x gap, not a partial one: stratifying a fresh 4,000,000-sample
      unconditional Bernoulli(0.35) population by decoded label
      (fail-labeled: mean margin 4.27, flip rate 20.81%; succeed-labeled:
      mean margin 12.42, flip rate 5.60%) and reweighting by the required
      label mix (q=9/28~=0.3214 fail) instead of the natural mix (0.211
      fail) reproduces V3's reported mean margin (9.80 predicted vs. 9.79
      reported), fraction margin<=4 (44.15% vs. 44.195%), unconditional flip
      rate (10.486% vs. 10.4662%), and margin-conditioned flip rate (20.145%
      vs. 20.1175%) all to within 0.02-0.03 percentage points."
    - "Because the bias is fully explained by one already-known constant (q,
      fixed since V1's marking-mechanism design) applied to strata the Red
      Team's own V2-batch measurement could in principle already have
      produced, V3's ~10.5% figure and the Red Team's ~8.8% figure are NOT
      two independent confirmations of the same underlying quantity -- they
      are estimates of two DIFFERENT, precisely related toy quantities.
      Neither is closer to 'what a real HQC decoding-relevant error vector's
      flip rate would be'; q=9/28 has no established connection to any real
      per-block HQC decoding-failure probability."
    - "detection_rate_report.md's framing of the ~1.2x gap as a 'candidate,
      not asserted-causal' explanation understates how completely resolved
      this question now is, and its 'directly comparable' framing of the two
      rates slightly overstates how much independent information the second
      measurement carries once the reweighting relationship is known."
    - "The control-arm lineage (V1->V2->V3) has reached its ceiling: this
      batch's own headline result is itself the sharpest evidence for that,
      since it is fully decomposable into information the prior batch's Red
      Team review already produced, and none of the three named residuals
      (real (T)-sampler never run, narrow 3-point S_t support vs. PS-R3's
      near-binomial spread, block-level flip rate vs. full estimator
      response) has moved across three generations."
  required_controls:
    - "Do not dispatch a V4 of the same shape (further-refined toy content
      model / marking mechanism). The next control that adds genuine new
      information is defect injection directly into the real (T)-sampler
      path (CTRStream/fixed_weight_support/ring arithmetic), even at reduced
      toy scale, measuring propagation to a real qhat/log2_Ahat_k deviation
      -- named consistently by every prior review of this lineage and not
      yet attempted."
  counterexample_or_mutation: >-
    Two independent reimplementations (own seeds, own vectorized rejection-
    sampling loop, not copied from planted_arm_v3.py), both against the
    sha256-pinned real decode_blocks/wht128: (1) a stratify-and-reweight
    reconstruction from a fresh 4,000,000-sample unconditional Bernoulli(0.35)
    population, predicting V3's reported margin/flip-rate figures to within
    0.02-0.03 percentage points; (2) a direct T=1,000,000 rejection-sampling
    reproduction (label ~ Bernoulli(q=9/28), redraw until decode matches),
    reproducing V3's figures to within 1 SE. Also directly tested (T=20,000
    independent full-56-position trials, own construction) whether
    Component B's "global" 5,600,000-pooled-position-observation Wilson CI
    understates uncertainty from within-trial clustering: measured design
    effect = 0.956 (Var(X_t) empirical 5.04 vs. naive-independence 5.27),
    i.e. no understatement -- the reported CI is honestly, mildly
    conservatively, sized.
  baseline_comparison: >-
    Not an ECDLP asymptotic claim. Closest analogue: CTRL-POSHOM's own
    measured real-crypto-data marginal shifts under V1/V2/V3-class defects
    (-0.0243%, -0.0566%, +0.0015%), two to three orders of magnitude smaller
    than any of this lineage's own toy-arm sensitivity figures (V2's ~+1.98%
    q-shift, V3's ~10.5% block-level flip rate) -- reinforcing that none of
    this lineage's internal sensitivity figures transfer to the real
    pipeline's actual noise floor.
  heuristic_challenges: []
  cost_model_challenges:
    - "Component A/last-block-early Wilson CIs are correctly sized (one
      observation per independent trial, no clustering). Component B's
      'global' statistic pools 5,600,000 position-observations from only
      100,000 independent trials with a theoretically plausible within-trial
      correlation structure (negatively-correlated labels from a fixed-M_t
      subset draw; a ring-chained perturbation); directly measured via an
      independent 20,000-trial reconstruction and found NOT to understate
      uncertainty (design effect 0.956, SE ratio 0.978x) -- a checked, not
      assumed, negative result."
  reduction_and_scope_challenges:
    - "decode_blocks/wht128/measure.py sha256 independently reverified,
      matching V1/V2/V3's shared pins exactly; no drift."
    - "planted_results.json/detection_results.json raw JSON spot-checked
      directly against detection_rate_report.md and run_manifest.yaml;
      T_achieved, Wilson records, margin statistics, and cells_match=17/17
      all consistent -- V1's carried-forward run-count discrepancy is not
      repeated."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The V3 arm's artifacts are honest, reproducible (independently confirmed
    by two from-scratch reimplementations), and budget-compliant (ADMIT).
    Its rejection-sampling-bias concern, which the executor correctly
    flagged as live and unresolved, is real and I have now fully resolved
    it: the ~1.19x gap between V3's ~10.5% and the Red Team's ~8.8%
    natural-content baseline is completely explained by the mismatch between
    the toy marking mechanism's required label frequency (q=9/28, fixed
    since V1) and the natural Bernoulli(0.35) decode-label frequency
    (0.211), with no residual left over. This means V3's headline
    measurement, while genuinely a calibrated rate (real progress over V2's
    forced {0%,100%}), is largely arithmetically recoverable from
    information the V2-batch Red Team review already established, not an
    independent confirmation of it. OPEN-6 is PARTIALLY CLOSED by this arm,
    incrementally beyond V2 (a genuine calibrated-rate methodology now
    exists and is shown not to introduce any UNEXPLAINED distortion), but
    the marginal information gained is smaller than the framing suggests,
    and the control-arm lineage of this shape has reached its ceiling: no
    generation has exercised the real (T)-sampler, and this generation's own
    result demonstrates that further refinement of the toy content model
    yields diminishing, largely-predictable returns rather than new
    information about the real pipeline.
  next_concrete_action: >-
    Do not dispatch a V4 planted-arm control of the same shape. Dispatch a
    defect-injection experiment against the real CTRStream/
    fixed_weight_support/ring-arithmetic (T)-sampler path, even at reduced
    toy budget, measuring whether the same V1/V3-class boundary/index-shift
    perturbation propagates to a detectable qhat/log2_Ahat_k-level deviation
    when computed the same way PS-R3's real pipeline computes it -- the
    control every generation of this lineage has named as missing and none
    has attempted.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/planted_arm_v3.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/planted_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/detection_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/detection_rate_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/tasks/TASK-20260806-e1700f/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/archives/TASK-20260806-c2b509/snapshot-receipt.json
    - ledger/evidence/EV-HQC-9a30d3.yaml
    - ledger/decisions/DEC-20260806-cf5102.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/reviews/TASK-20260806-ae74c4/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none.*
