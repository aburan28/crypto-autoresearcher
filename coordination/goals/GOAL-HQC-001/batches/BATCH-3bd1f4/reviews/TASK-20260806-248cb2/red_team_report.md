# Red-team report — dilution-formula reliability checks (Check 1 / Check 2)

**Task** `TASK-20260806-248cb2` (red team) · **Batch** `BATCH-3bd1f4` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`b7f81e3e` (`TASK-20260806-9c206d`) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/{design.md,reliability_checks.py,checks_results.json,checks_report.md,run_manifest.yaml}`.
Also read `ledger/decisions/DEC-20260806-d9d395.yaml`, `ledger/evidence/EV-HQC-036d4b.yaml`
(referenced), and my own prior report
(`coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/reviews/TASK-20260806-2cec38/red_team_report.md`),
which named these two checks and produced the original single-point 13.4%
figure and the ~1.38e5 global-injection projection this batch exists to
stress-test. I re-derived every number below independently from the
committed JSON rather than trusting either the executor's or my own prior
framing.

**Bottom line up front.** Both checks were executed competently, honestly,
and inside their stated (narrow) scope: fail-closed gates are real and all
pass, the arithmetic reproduces to machine precision, and the report
correctly declines to round a mixed result into a clean verdict. But two
things change my own prior assessment materially. First, the growing,
dataset-disagreeing deviation pattern is large enough, given the formula's
near-cancellation and `1/bracket²` sensitivity, to **flip the specific
headline `DEC-20260806-d9d395` recorded** — "global injection projected
cheaper than baseline" — when the more reliable of the two datasets is used
instead of the one actually load-bearing in the committed record. Second,
"Check 2" as executed is not the check I asked for: it validates the
formula's `Δp`-scaling algebra (a bug check), not the `SE(T) ∝ 1/√T`
extrapolation my prior report's `required_controls` item 2 named — that gap
is still completely open. I ADMIT the executed artifacts as an honest
partial answer; I DO NOT ADMIT the "cheaper than baseline" headline as
established by them, and I name the specific, cheap recomputation and the
specific unaddressed check that resolve this next.

---

## 1. Does the growing-with-k pattern change confidence in the k=17 residual?

Yes, and not only in the direction the pre-registered binary framing
anticipated. Two things are true simultaneously, and they point different
ways:

- **The deviation's sign and smoothness argue it is a real, structural
  effect, not noise.** It is positive at all 34 (Dataset A) / 25 (Dataset B)
  reported `k`, grows monotonically in both datasets independently, and even
  at `k=2` — where 10,000,000 (Dataset A) trials leave essentially zero
  sampling noise — it is already `+0.42%`/`+0.36%`, not zero. A purely noisy
  quantity does not produce two independent, differently-sized samples that
  agree to within 15% of each other and never once change sign across 25-34
  points. This is evidence of genuine, growing positive block correlation,
  not an artifact of the check.
- **But growth with `k` is exactly the wrong direction for the load-bearing
  `k=17` residual's precision, given the formula's cancellation structure.**
  `Δ(log2_A_17)` is the difference of a `leading_term` and a `q_shift_term`
  that are individually ~8.5x the reported residual (`EV-HQC-036d4b`'s own
  disclosed ~88% cancellation). `T_req ∝ 1/(bracket)²`. A quantity that is
  itself the *residual of a near-cancellation*, computed from a moment ratio
  that is monotonically drifting away from its `k=16` neighbor's value as
  `k` increases, is not a quantity whose `k=17` point estimate I would call
  "stable." The check does not merely confirm 13.4% is representative — it
  shows the opposite: `k=17` sits partway up a **still-climbing curve**, so
  small differences in exactly which sample or which `k` you read off cost
  real precision, and the two-sample disagreement documented in Section 2
  below is the direct, measured consequence of that instability.

**My answer:** `k=17` is not in a "good enough, bounded, order-of-magnitude
stable" regime by the pre-registered criterion (`design.md` §1.3's own
"lower confidence" bullet — deviation growing sharply and monotonically past
`k=17` — is the one that actually obtains). The magnitude (7.6%-13.4%,
possibly more once the additional gaps in Section 4 below are accounted for)
is large enough, given `1/bracket²` scaling, to move `T_req` by a factor of
~3x between the two disclosed point estimates alone (verified in Section 3).
That is "substantial" by any reasonable reading of the pre-registered
question.

---

## 2. The dataset disagreement, investigated directly (not accepted from either report)

I recomputed both `relative_deviation(17)` figures independently from the
committed JSON (not copied from `checks_report.md`) and trace where each
dataset actually comes from, since that — not sample count alone — is what
should set the trust weighting.

- **Dataset A** (`measurement_results.json`, `T=1e7`): this is
  `TASK-20260806-cde749`'s `T_arm` — the frozen instrument's own dedicated,
  purpose-built baseline measurement, used elsewhere in that same task to
  check `q_hat_measured` against `q_hat_frozen` to `3.6e-4` relative
  precision. It is a single large committed run, not an ad hoc reuse.
- **Dataset B** (`reanalysis_results.json`, `T=10,000`): I traced this
  through `reanalysis_report.md` (lines 24, 120-147) rather than trusting
  the "T=10,000, ~660x smaller" framing at face value. The pooled true-arm
  statistic is **not** 10,000 independent draws — it is exactly **two**
  independent 5,000-trial shards (`5000` and `6000`), each contributing its
  own true-decode histogram to the pooled `mubar_k_true`. This matters
  beyond "smaller sample": with only two independent shard-level draws
  feeding a joint-order (`k=17`) combinatorial-moment ratio, whatever
  idiosyncrasy either shard's own random path carries shows up **coherently
  across the entire `k`-dependence curve derived from it**, not as
  independent per-`k` noise. That is consistent with what I actually see in
  the cross-dataset table: the A/B ratio is **not** noisy scatter around 1 —
  it is a smooth, monotonic crossover (`B<A` for `k=2..11`, `B>A` and
  growing for `k≥12`, ratio `B/A` climbing from `0.86` at `k=2` to `1.76` at
  `k=17` to `4.26` at `k=26`). A 2-shard composition effect produces exactly
  this signature; independent per-trial Poisson noise on 10,000 draws would
  not produce so smooth a crossover.

**My assessment:** Dataset A is the more reliable estimate, for two
independent reasons beyond raw count — (1) ~660x-1000x more effective trials
at `k=17` specifically, and (2) it is the dedicated frozen-instrument
measurement rather than an opportunistic 2-shard reuse whose own effective
degrees of freedom for a `k=17`-order statistic are much smaller than
`T=10,000` suggests. The disagreement factor (**1.756x**, verified by direct
recomputation, not copied) should be read as **understating** the true
uncertainty band around `13.39%`, because the check that would properly
quantify Dataset B's shard-composition variance (bootstrap or per-shard
breakdown at `k=17`) was not run by the executor and I did not have budget
to run it either (see Section 4). At minimum, the campaign should stop
treating Dataset B's `13.39%`/`0.4192` bracket as *the* number — it is the
noisier of two disclosed estimates, both of which should be carried forward,
not one silently privileged because it happens to be the value already
embedded in `reanalysis_results.json.required_T_derivation.load_bearing_k17`
before this batch ran.

---

## 3. Does this threaten the global-injection projection? — Two different comparisons, two different answers

This is the question I most needed to get right, and the answer is **not
uniform** — `DEC-20260806-d9d395` folds two structurally different claims
into one headline, and only one of them survives.

### 3a. Global vs. single-block (the *ratio* claim) — ROBUST, survives fully intact

By construction, both formulas use the identical bracket term
(`mubar_{k-1}/mubar_k − 1/q̂`, a property of the baseline true arm, not of
which block is perturbed): `Δ(log2_A_k)_single = (k/n_e)·(Δp/ln2)·bracket`,
`Δ(log2_A_k)_global = k·(Δp/ln2)·bracket`. Whatever the true value of
`bracket` is — 0.239 (Dataset A), 0.419 (Dataset B), or something else
entirely once the conditional-vs-unconditional gap in Section 4 is properly
measured — it **cancels out of the ratio**. I verified this numerically:
`T_req_single/T_req_global = 3136.0000...` to 10 significant figures using
Dataset B's bracket, and the same exact ratio holds using Dataset A's
bracket (both formulas scale by the same factor, so the ratio is invariant
by construction, not by luck). This ratio is additionally underwritten by
the *exchangeability* of the 56 blocks (same nominal marginal rate `q`,
symmetric construction) — under exchangeability, the `n_e`-fold
amplification of the global effect over the single-block effect is exact at
the level of the true (not merely modeled) partial derivative, independent
of whether the i.i.d.-blocks substitution is a good approximation to that
derivative. **So: "global injection removes the dilution penalty relative
to single-block, by a factor of exactly `n_e²`" is not weakened by this
batch's findings at all.** This is the part of the campaign's prior
conclusion that should NOT be walked back.

### 3b. Global vs. the external, fixed baseline `T_req=3.09e5` — NOT ROBUST, flips sign

This is the specific comparison `DEC-20260806-d9d395`'s `decision_label`
headlines ("global injection projected cheaper than baseline"). Unlike 3a,
this comparison is an **absolute** one against a number that does not scale
with `bracket`, so the bracket-term uncertainty is not cancelled — it goes
straight through. I recomputed `T_req_global` using each dataset's own
bracket value, holding every other constant (`T_ref=10,000`, `z_sum`,
`SE_ref`, `Δp=0.0082`) fixed at the values already committed and
cross-checked by the executor's fail-closed gates:

| bracket source | `relative_deviation(17)` | `bracket` | `T_req_global` | vs. spec's undefected `T_req=3.09e5` |
|---|---:|---:|---:|---|
| Dataset B (the value actually load-bearing in `reanalysis_results.json`) | 13.39% | 0.4192 | **1.380e5** | **0.45x — cheaper** |
| Dataset A (larger, more reliable sample, per Section 2) | 7.63% | 0.2387 | **4.257e5** | **1.38x — more expensive** |
| breakeven | 8.95% | 0.2802 | 3.09e5 | exactly baseline |

(All figures independently recomputed by me from the committed JSON; script
output cross-checked against the executor's own `total`/`T_req` values at
the shared point, matching to the reported precision.)

**The breakeven relative-deviation (8.95%) sits inside the disclosed
uncertainty band (7.63%-13.39%), closer to Dataset A's value than to Dataset
B's.** Given Section 2's finding that Dataset A is the more trustworthy of
the two, the honest current state of the evidence is: **the "cheaper than
baseline" conclusion is not established — it is one side of a coin whose
weighting favors the *other* side.** This is a materially different
statement than `DEC-20260806-d9d395`'s `decision_label`
(`single_block_dilution_confirmed_global_injection_projected_cheaper_than_baseline`)
asserts, and neither the executor's checks_report.md nor design.md performs
this specific recomputation — they report the two raw deviation numbers as
facts (correctly, per their own scope) but do not propagate them through the
`T_req_global` formula to check whether the headline survives. That
propagation is exactly what a reviewer is for, and it is the central finding
of this report.

**What this does and does not mean for the campaign.** It does *not* mean
global injection is a dead end — `T_req≈4.26e5` (Dataset A) is still cheap
in absolute terms (~130 core-seconds at the throughput figures used
elsewhere in this campaign for PS-R3, `cost_model.md`), and still vastly
cheaper than V3's `4.33e8`. What it means is that the specific comparative
claim "cheaper than the *undefected* baseline" should not be carried into a
ledger decision as established, and a pilot sized to confirm that specific
comparison should not anchor on `1.38e5` as a point target.

---

## 4. Do the two checks actually test what I asked for, or something narrower?

Not fully, on both counts — this matters for how much weight the "clean
result" should carry.

**Check 1** is correctly generalized (more `k`, two datasets) but is still,
structurally, the *same* proxy quantity as my original single 13.4% number
— the population-level marginal-moment ratio `mubar_{k-1}/mubar_k` vs.
`1/q̂` — not a direct measurement of the object my prior report's
`required_controls` item 1 actually named: `P(other 16 blocks fail |
F_{n_e-1}=1)` computed from **per-block** data (the `F_true`/`F_def` arrays
`TASK-20260806-e120e8` regenerated in-memory but did not retain). The
marginal-moment proxy is a legitimate consequence of block exchangeability
(under exchangeability the aggregate moment-sequence test and the
conditional-probability test are related, as `design.md` §1.1 correctly
derives), but it is not literally the same measurement, and it cannot
distinguish "excess correlation concentrated on the specific perturbed
block" from "excess correlation spread symmetrically across all blocks" —
a distinction that matters for whether the single-block dilution formula's
`k/n_e` term itself is exactly right. This remains open.

**Check 2**, as executed, is **not** the check I named. My prior report's
`required_controls` item 2 asked to "resample the already-collected 10,000
matched pairs at a few smaller `T` (e.g. 2,500/5,000) and confirm `SE(T) ∝
1/√T` holds within the observed range before trusting the 4-5-order-of-
magnitude extrapolation" from `T_ref=10,000` out to `T~1.4e5`-`4.3e8`. What
was actually run is a `Δp`-sweep of the *already-audited* formula, checking
that `T_req·Δp²` is constant to machine precision — this confirms the
**implementation has no bug** across `Δp`, which is useful and was done
rigorously (61 points at `k=17`, 21 points at every `k=2..26`, `cv~1e-16`
throughout), but it is an algebraic identity of the *stated* formula and
says nothing about whether the `SE(T)∝1/√T` **statistical** assumption used
to extrapolate from `T=10,000` to `T~10⁵`-`10⁸` is empirically valid at any
point in that range. I checked `run_manifest.yaml`'s two invocations and
`design.md`/`checks_report.md` directly — no resampling at smaller `T` was
performed anywhere in this batch. **This is a genuine, undisclosed scope
narrowing** that happened somewhere between my prior report naming the
check and `DEC-20260806-d9d395`/the dispatch queue's paraphrase of it
("verify the reported SE scaling... holds across a range of plausible
`Δp` values") — the word "SE-scaling" was quietly repointed from "scaling
with `T`" to "scaling with `Δp`" and nobody flagged the substitution before
it reached this batch's task card. The check that would validate the
extrapolation itself is still completely unrun, and it is cheap: it needs
no new sampling, only re-splitting the already-regenerated shard-level
matched pairs into `T=2,500`/`T=5,000` subsamples (deterministic
reproduction of `5000`/`6000` via the already-pinned `stage_a.py`
`_t_shard()`, exactly as `TASK-20260806-e120e8` already did once).

I did not attempt to run this myself: it requires invoking `stage_a.py`
against the pinned shard seeds, which is compute beyond arithmetic on
already-committed JSON and is Executor-scoped work, not something I should
do inside a review-only session with my write scope limited to this
directory. I name it as the next concrete action instead.

---

## 5. ADMIT / DO-NOT-ADMIT

**ADMIT** the artifact set (`design.md`, `reliability_checks.py`,
`checks_results.json`, `checks_report.md`, `run_manifest.yaml`) as an
honest, fail-closed, competently executed record of the two checks *as
they were actually scoped* by the time they reached this batch:

- All 11 fail-closed gates are real and independently reproducible; I
  recomputed the two headline deviation numbers (7.63%, 13.39%) and the
  `T_req_global` figure from the raw committed JSON myself and got the same
  values to the reported precision.
- The report is honest about the mixed result and does not round the
  binary pre-registered framing into a false single verdict — it explicitly
  surfaces both the "toward lower confidence" and "toward higher confidence
  in a real effect" readings and the dataset-disagreement anomaly, none of
  which was anticipated in `design.md`'s original framing.
- No campaign-level call was made, correctly, per the executor's scope.

**DO NOT ADMIT**:

- `DEC-20260806-d9d395`'s specific headline
  ("global-injection projected cheaper than baseline") as validated by this
  batch. Section 3b shows this comparison flips sign depending on which of
  the two disclosed, disagreeing datasets is used, and the more reliable
  dataset (Section 2) puts the projected `T_req_global` (~4.26e5) *above*,
  not below, the spec's own undefected `T_req=3.09e5`.
- The claim that "Check 2" validated the `SE(T)∝1/√T` extrapolation my
  prior report asked to have checked. It validated a different, narrower
  thing (the formula's `Δp`-scaling arithmetic), and the extrapolation
  validity question is unaddressed.
- Treating `1.38e5` as a trustworthy point target for sizing a pilot. It is
  one end of at least a ~3x-wide disclosed band (`1.38e5`-`4.26e5`), itself
  probably an underestimate of the true uncertainty given the 2-shard
  composition concern in Section 2.

---

## 6. My recommendation

**Do not proceed straight to scoping the global-injection pilot at ~1.38e5
as a point target.** The `n_e²`-dilution-removal *structural* argument for
preferring a global over a single-block injection (Section 3a) is sound and
untouched by anything in this batch — that direction of travel should
continue. But two cheap, still-unresolved items should come before or
alongside sizing:

1. **Re-derive `T_req_global` using Dataset A's bracket (or, better, a
   properly weighted/pooled combination of both, with a bootstrap or
   per-shard SE on Dataset B to make the weighting honest) as the primary
   input, not Dataset B's**, and use the *resulting* range (this report
   shows it already spans `1.38e5`-`4.26e5` from the two point estimates
   alone) — not a single number — to size an initial diagnostic run. Given
   the breakeven sits inside this range, a diagnostic run should be sized to
   be informative even if the true required `T` is above the spec's
   undefected `3.09e5`, not only if it is comfortably below.
2. **Run the actual `SE(T)∝1/√T` resampling check** (re-split the already-
   regenerated `5000`/`6000` shards into `T=2,500`/`T=5,000` subsamples,
   deterministic, no new sampling) before trusting any extrapolation from
   `T_ref=10,000` to a pilot scale 1-4 orders of magnitude larger. This was
   named by my prior report, was not executed by this batch under either
   check's actual scope, and is cheap.
3. Optionally, if budget allows before the pilot: the direct per-block
   conditional check (`F_true`/`F_def` split by whether block `n_e-1`
   failed) named in my prior report remains the most direct test of the
   independence approximation itself, as distinct from the marginal-moment
   proxy this batch re-measured. It requires re-invoking `stage_a.py`
   against already-pinned seeds (deterministic, no new randomness draws,
   but real compute) — Executor-scoped work, not mine to run here.

This is not a recommendation to reopen or re-litigate the single-block
(V3) closure, and it is not a claim that real-sampler global injection is
infeasible — it is a claim that the specific number and the specific
"cheaper than baseline" comparison this batch's parent decision leaned on
are not yet established to the precision a pilot-sizing decision should
rest on, and that the fix is cheap and named above, not a call for a larger
validation program.

---

## 7. Budget

Reading: the five reviewed artifacts, `DEC-20260806-d9d395.yaml`, my own
prior report, and (to trace Dataset B's actual shard composition rather than
trust the "T=10,000" framing) `reanalysis_report.md`'s per-shard
breakdown. Compute: a short Python verification script in scratch space
(no repository files touched, no new sampling) reproducing both datasets'
`k=17` bracket terms and the `T_req_global` comparison table in Section 3b
from the committed JSON values directly — a few seconds. No budget overrun;
total time well inside the 1,800-second authorization.

---

## 8. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-248cb2
  task_id: TASK-20260806-248cb2
  claim_under_review: >-
    checks_report.md (TASK-20260806-66e3c3, snapshot b7f81e3e) reports (1) a
    conditional-vs-unconditional mubar_{k-1} deviation, measured across
    k=2..35 on two independent already-committed PS-R3 datasets, that is
    always positive and grows monotonically, disagreeing at the load-bearing
    k=17 by a factor of ~1.75 between datasets (7.63% vs 13.39%), and (2) an
    SE-scaling / required-T formula sweep confirming the formula's
    Delta_p-scaling arithmetic is bug-free across six orders of magnitude and
    the full k=2..26 range -- offered as inputs to whether DEC-20260806-d9d395's
    ~1.38e5 global-injection required-T projection (versus the spec's own
    undefected T_req=3.09e5) should be trusted enough to size a pilot.
  objections:
    - "The k=17 residual is not in a stable/bounded regime: the deviation
      grows monotonically and increasingly steeply for k beyond 17 in both
      datasets, which is the pre-registered signature of LOWER confidence
      (design.md Section 1.3), not the fixed, order-of-magnitude-stable
      13.4% single number my own prior report reported at one point."
    - "The two datasets' k=17 estimates disagree by a factor of 1.756x
      (7.63% vs 13.39%), and propagating each through the SAME (already
      fail-closed-verified) required-T formula, holding every other input
      fixed, gives T_req_global = 1.380e5 (Dataset B, cheaper than the
      spec's undefected T_req=3.09e5) versus T_req_global = 4.257e5
      (Dataset A, MORE expensive than baseline) -- the breakeven bracket
      value (relative_deviation=8.95%) sits inside the disclosed
      7.63%-13.39% band, closer to Dataset A. Neither the executor's report
      nor DEC-20260806-d9d395 performs this specific recomputation; it
      directly threatens the decision's own headline label."
    - "Dataset A is the more reliable of the two -- not only ~660x-1000x
      more effective trials at k=17, but structurally the dedicated frozen
      T_arm baseline measurement, versus Dataset B's pooled statistic which
      draws on only TWO independent 5,000-trial shards (5000, 6000), not
      10,000 independent draws. The smooth, monotonic (not erratic)
      crossover between the two datasets' deviation curves (B<A for k<=11,
      B>>A and growing for k>=12) is the signature of a 2-shard composition
      effect, not per-trial sampling noise -- which argues Dataset B's
      13.39% figure (the one actually load-bearing in
      reanalysis_results.json.required_T_derivation) carries more
      uncertainty than a naive T=10,000 sqrt-scaling would suggest."
    - "'Check 2' as executed is not the check my prior report's
      required_controls item 2 named. It validates the required-T formula's
      Delta_p-scaling ARITHMETIC (an implementation-correctness check,
      confirmed bug-free to machine precision), not the SE(T) proportional
      to 1/sqrt(T) EXTRAPOLATION assumption used to project 1-4 orders of
      magnitude from T_ref=10,000 out to a pilot scale. The word
      'SE-scaling' was silently repointed from 'scaling with T' to 'scaling
      with Delta_p' somewhere between my prior report and this batch's task
      card; the originally-named resampling check (re-split the
      already-regenerated 5000/6000 shards into T=2,500/5,000 subsamples,
      no new sampling required) remains completely unrun."
    - "Check 1, while correctly generalized across k and datasets, remains
      the same population-level marginal-moment proxy as my original
      single-number finding, not the direct per-block conditional
      measurement (P(other 16 blocks fail | F_{n_e-1}=1) from F_true/F_def
      arrays) my prior report's required_controls item 1 specifically named
      and noted was available with no new sampling. That direct measurement
      is still not done."
  required_controls:
    - "Recompute T_req_global using Dataset A's bracket term (or a properly
      weighted/pooled combination of both datasets with an honest
      per-shard/bootstrap SE on Dataset B) as the primary input, not Dataset
      B's currently load-bearing 13.39% figure, before any pilot is sized
      against a specific T target."
    - "Run the actual SE(T) proportional to 1/sqrt(T) resampling check:
      re-split the already-regenerated shard-5000/shard-6000 matched pairs
      into T=2,500 and T=5,000 subsamples and confirm the paired SE scales
      as expected in the observed range, before trusting any extrapolation
      from T_ref=10,000 to a pilot scale 1-4 orders of magnitude larger.
      Deterministic reproduction of already-used seeds; no new sampling."
    - "Directly measure the conditional-vs-unconditional gap from per-block
      data (F_true/F_def arrays, re-derivable deterministically from the
      5000/6000/424242 shard seeds with no new sampling) rather than relying
      only on the population-level marginal-moment proxy Check 1 computed --
      this is the direct test of the independence approximation itself, as
      opposed to a consequence of it under exchangeability."
    - "Get a genuine uncertainty estimate on Dataset B's k=17 deviation
      (e.g. per-shard breakdown or a two-point bootstrap over its two
      constituent shards) rather than treating its point estimate as
      commensurable with Dataset A's on the strength of 'T=10,000' alone."
  counterexample_or_mutation: >-
    Held every input of the already-fail-closed-verified required-T formula
    fixed (T_ref=10000, z_sum=3.241515551, SE_ref=0.09662406112454607,
    Delta_p=0.0082, n_e=56, k=17) and substituted Dataset A's independently
    recomputed bracket term (0.238693, from relative_deviation=7.63%) for
    Dataset B's (0.419166, from relative_deviation=13.39%, the value
    actually stored in reanalysis_results.json.required_T_derivation as
    load-bearing). This single substitution moves T_req_global from
    1.380e5 (0.45x the spec's undefected T_req=3.09e5 -- "cheaper") to
    4.257e5 (1.38x the spec's undefected T_req=3.09e5 -- "more expensive"),
    flipping DEC-20260806-d9d395's own decision_label
    (single_block_dilution_confirmed_global_injection_projected_cheaper_than_baseline).
    The single-block-vs-global RATIO (exactly n_e^2=3136, verified to 10
    significant figures under both bracket values) is unaffected by this
    substitution and remains a robust, structural conclusion.
  baseline_comparison: >-
    Not an ECDLP/Pollard-rho/BSGS comparison -- HQC decoding-correlation
    instrument-validation batch. The load-bearing comparison this report
    addresses is the specification's own pre-registered undefected
    T_req=3.09e5 (PS-R3, k=m=17, cost_model.md) against the projected
    required-T for a global (V1-class) real-sampler injection at the same
    Delta_p magnitude: 1.380e5 using the dataset currently embedded as
    load-bearing in the committed record, versus 4.257e5 using the dataset
    this report argues is more reliable -- i.e. the comparison this batch's
    parent decision rests its headline on is not settled in either
    direction by the evidence assembled so far.
  heuristic_challenges:
    - "The i.i.d.-blocks substitution's error, measured here as a
      population-level moment-sequence deviation, is confirmed to be a real,
      monotonically growing, sign-stable effect (not noise) across k=2..35 --
      but its magnitude at exactly k=17, the load-bearing order, is itself
      uncertain by a factor of ~1.76x between the two available estimates,
      and that uncertainty propagates through the formula's 1/bracket^2
      sensitivity into a ~3x uncertainty on any downstream required-T
      figure. Neither design.md nor checks_report.md propagates this
      uncertainty through to the T_req_global comparison that actually
      matters for the pilot-sizing decision."
    - "The SE(T) proportional to 1/sqrt(T) extrapolation heuristic underlying
      every required-T figure in this campaign (a 1-4 order-of-magnitude
      extrapolation from T_ref=10,000) has never been empirically checked
      in-range, despite a cheap, no-new-sampling check being available and
      named twice now (my prior report's required_controls item 2, and this
      report's Section 4/required_controls)."
  cost_model_challenges:
    - "T_req_global is not a single number: propagating the two disclosed,
      disagreeing k=17 deviation estimates through the identical,
      fail-closed-verified formula yields a factor-of-3.08 spread
      (1.380e5 to 4.257e5), which straddles the specification's own
      undefected T_req=3.09e5 comparison baseline. A pilot-sizing decision
      that anchors on the lower end of this spread (1.38e5) as a point
      target, without disclosing the spread crosses the 'cheaper vs more
      expensive than baseline' boundary, understates the actual cost
      uncertainty by roughly a factor of 3."
    - "The single-block-to-global n_e^2=3136x required-T reduction is exact
      and bracket-term-independent (verified to 10 significant figures under
      both disclosed bracket values), because it follows from block
      exchangeability rather than from the accuracy of the i.i.d.-blocks
      approximation. This distinguishes it sharply from the absolute
      comparison against the external undefected baseline, which is NOT
      bracket-term-independent and is exactly the comparison that flips."
  reduction_and_scope_challenges:
    - "DEC-20260806-d9d395's decision_label conflates two structurally
      different claims -- (a) global injection removes the k/n_e dilution
      relative to single-block (robust, exact by exchangeability,
      unaffected by this batch's findings) and (b) global injection is
      cheaper than the undefected baseline (not robust, flips sign between
      the two disclosed datasets) -- into one headline. Claim (a) should be
      carried forward with full confidence; claim (b) should not be carried
      forward as established."
    - "'Check 2' as executed and as described in this batch's own dispatch
      queue ('SE-scaling in-range check... verify the reported SE scaling
      holds across a range of plausible Delta_p values') is scoped more
      narrowly than my prior report's required_controls item 2 asked
      (resampling at smaller T to validate the SE(T) proportional to
      1/sqrt(T) extrapolation). This narrowing happened silently somewhere
      between the two documents and should not be read as having closed the
      extrapolation-validity question."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    Both reliability checks were executed honestly, fail-closed, and
    reproducibly within the scope that actually reached this batch's task
    card; I independently reproduced their headline numbers from the
    committed JSON. The i.i.d.-blocks approximation error is confirmed real,
    sign-stable, and growing with k -- not a fixed 13.4% constant -- and the
    two available point estimates of its size at the load-bearing k=17
    disagree by a factor of ~1.76, with the larger, more structurally
    reliable dataset giving the SMALLER deviation (7.63%, not 13.39%). The
    single-block-to-global n_e^2 required-T reduction is exact and
    unaffected by this uncertainty, because it follows from block
    exchangeability rather than from the i.i.d. approximation's accuracy --
    that qualitative direction of travel remains sound. But the specific
    claim that a global injection is projected CHEAPER than the
    specification's own undefected T_req=3.09e5 is not established: using
    the more reliable dataset's bracket term in the identical,
    already-verified formula gives T_req_global=4.257e5, which is MORE
    expensive than baseline, not less. This is a genuinely open question,
    not a resolved one, and the two named cheap next checks (recompute with
    the more reliable/pooled bracket estimate; run the actual SE(T)
    proportional to 1/sqrt(T) resampling check that was never executed
    under either check's name) should happen before a pilot is sized
    against any single T_req number.
  next_concrete_action: >-
    Before scoping the global-injection pilot at a specific T target: (1)
    recompute T_req_global using Dataset A's bracket term (or a properly
    weighted pooling of both datasets with an honest per-shard/bootstrap SE
    on Dataset B) as the primary input rather than Dataset B's currently
    load-bearing 13.39% figure, and carry the resulting ~1.38e5-4.26e5 range
    (not a point estimate) into the pilot-sizing decision; (2) run the
    SE(T) proportional to 1/sqrt(T) resampling check named in my prior
    report and still unaddressed by this batch -- re-split the
    already-regenerated shard-5000/shard-6000 matched pairs into
    T=2,500/5,000 subsamples, no new sampling required -- before trusting
    any 1-4-order-of-magnitude extrapolation from T_ref=10,000. Both are
    cheap, Executor-scoped, no-new-(T)-sampling tasks.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/reliability_checks.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/checks_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/checks_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/tasks/TASK-20260806-66e3c3/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-3bd1f4/archives/TASK-20260806-9c206d/snapshot-receipt.json
    - ledger/decisions/DEC-20260806-d9d395.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/reviews/TASK-20260806-2cec38/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/reanalysis_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/reanalysis_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measurement_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/cost_model.md
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement:
I neither confirm the executor's framing nor re-adopt my own prior
(`TASK-20260806-2cec38`) 13.4%/1.38e5 numbers without re-scrutinizing them as
hard as I would anyone else's — Section 3b above is the direct result of
that re-scrutiny.*
