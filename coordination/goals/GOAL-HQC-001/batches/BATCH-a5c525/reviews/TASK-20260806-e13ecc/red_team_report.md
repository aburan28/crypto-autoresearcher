# Red-team report — real-sampler cost model (TASK-20260806-77443e)

**Task** `TASK-20260806-e13ecc` (red team) · **Batch** `BATCH-a5c525` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`e784c8ba` (`TASK-20260806-f238a2`, parent-checked against the dispatch
queue's requirement that this commit precede review) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/{cost_model.md,benchmark.py,benchmark_results.json,run_manifest.yaml}`.
Also read `ledger/evidence/EV-HQC-163374.yaml`, `ledger/decisions/DEC-20260806-0995d5.yaml`,
`ledger/goals/GOAL-HQC-001.yaml` (full `batch_checkpoints` and
`pause_conditions`), and
`coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/reviews/TASK-20260806-7008de/red_team_report.md`
(my own prior V3 review, read here strictly as an artifact under review, not
as license to repeat its recommendation without a fresh assessment — the
task card is explicit that a prior recommendation in principle is not a
substitute for a fresh judgement of timing/budget now).

I independently recomputed the Wilson-CI sizing table (§4.1 of
`cost_model.md`) and the derived cost-table arithmetic (§5.a/§5.b) from the
raw `benchmark_results.json` throughput figures. All recomputed values match
the reported ones to the stated precision (e.g. `n ≈ z²p(1-p)/w²` at
p=0.201, w=0.005 gives 24,678.3, matching "24,678"; T_req=3.09e5 at 788/2227/2168
t/cs gives 392.1/138.8/142.5 core-seconds, matching "139-392"). **I found no
arithmetic errors anywhere in the cost model.** My objections below are about
what quantities were plugged into correct arithmetic, not about the
arithmetic itself.

---

## VERDICT

**ADMIT the cost model as an artifact** — its arithmetic is correct, its
self-disclosed anomaly (§2.1) is real and honestly reported rather than
smoothed over, its budget/scope observance is clean, and it does not
overclaim (it explicitly declines to fabricate HQC-3/HQC-5's true deployed
parameters and labels PS-R1/R3/R5 as order-matched proxies, not the real
thing). **But its headline "139-392 core-seconds, cheap" framing is
optimistic in a way that matters for the decision it is meant to support,**
for the reasons in §1-§3 below. **My independent recommendation is
PARTIAL-GO, narrower and more conditional than the executor's own
PARTIAL-GO** — bounded by a pre-committed stopping rule, not open-ended
follow-on iteration. I take PAUSE seriously (§4) and do not think it is
clearly wrong, but on balance I do not recommend it *yet*, for reasons
stated below.

---

## 1. Benchmark methodology: the "cheap" figure rests on the *favorable* side of an unresolved, unexplained 2.6-2.8x internal discrepancy

The cost model's own §2.1 discloses that `stages_summed` (788 t/cs at PS-R3,
this task's own separately-timed calls to the real functions) and
`full_pipeline_via_real_t_shard` (2,227 t/cs, calling `stage_a.py`'s own
`_t_shard()` worker directly on the *same* functions, doing *strictly more*
work per trial) disagree by 2.8x, and the disagreement is not resolved — the
executor offers a "plausible, not confirmed" cold-start/warm-up explanation
and stops there. This is the single most consequential unresolved fact in
the artifact, and I want to be precise about what it does and does not
undermine.

**What it does not undermine:** the executor's choice to report a *range*
rather than pick one figure is the right instinct, and using the pessimistic
bound for the "does it even fit" floor check is correctly conservative.

**What it does undermine:** cost_model.md §2.1 explicitly elects to use "the
converged ~2,100-2,230 band, anchored on the actual production-scale T=1e7
measurement, as the primary planning figure, since it is empirically
better-supported... than this task's own single small-N anomaly." That is a
judgement call, not a neutral fact, and it resolves an *unexplained*
discrepancy in the direction that makes the headline number look best. The
"convergence" argument has real force for the *undefected* full-pipeline
throughput specifically (EV-HQC-b71230's T=1e7 production run independently
achieved 2,168 t/cs, a genuinely separate, larger-scale, out-of-process
measurement, not just another instance of this benchmark's own possibly
order-biased loop) — I recompute this convergence as real and it is the
strongest single piece of evidence in the whole cost model. But that
convergence evidence is about the **unmodified, undefected** generation
path. It says nothing about whether a **defect-injected** version of the
same code — with an added conditional branch inside the hot per-trial loop
at exactly one of the four named injection points (§3) — would preserve the
same throughput, since no defect-injected run has ever been timed. A
one-line conditional is unlikely to move throughput by 2.8x on its own, but
the point is narrower: the cost model has not established that its favorable
bound, rather than its unfavorable bound, is the right one to plan against
for the *actual next experiment*, only for a *different, already-run*
experiment (PS-R3 undefected, T=1e7).

**Required control, cheap and concrete:** before committing budget to the
real experiment, re-run this same calibration benchmark with (a) the stage
order randomized/rotated across parameter sets (not always
stage1→stage2→bitpack→stage3→`_t_shard` within each set) and (b)
`decode_blocks` warmed once before *any* stage timing begins, to determine
whether the 2.8x gap is genuinely a cold-start artifact or a real cost the
production run's own 8-shard/4-core structure happens to amortize away in a
way a single small defect-injection run would not. This is minutes of
compute, not a budget risk, and it directly de-confounds the one number the
whole affordability argument leans hardest on.

**On the "3,500 trials, is that enough" question specifically:** for a
*timing* estimate (not a *rate* estimate), the concern is not sampling
noise — more trials would not resolve the 2.6-2.8x gap, since it is
structural/systematic (an ordering or warm-state effect), not statistical
noise that averages out. The trial count is adequate for what it can measure
and inadequate for what it cannot: it cannot by itself tell the two bounds
apart. I do not read the small trial count as the primary source of
optimism here; the primary source is the *choice of which bound to plan
against* given an unresolved discrepancy the trial count cannot fix.

---

## 2. The detection-rate assumption underlying every T_req figure in §4.1 does not transfer to the real sampler, and the cost model already half-admits this without fully pricing it

This is my most serious objection, and it goes to the heart of what "cheap"
means here.

`cost_model.md` §4.1 derives its Wilson-CI sizing table from the "8.8%-20.1%
detection-rate range V1-V3 established," per the dispatch queue's own
instruction. But V1-V3's detection rate is a **block-level flip rate under
Bernoulli(0.35) planted content, filtered by a toy 3-point marking mechanism
{17,18,19} out of 56 positions**, measured by the *V3-batch red team's own
report* (which I wrote and which is itself under review here) to be a
**mixture-dependent artifact of a design constant (q=9/28 vs the natural
0.211)**, not a portable "natural detection rate" — this is not my
interpretation now, it is the finding both the Validator and I independently
established and the Coordinator adopted verbatim in `DEC-20260806-0995d5`.
Carrying an already-debunked "portable rate" concept forward into a *new*
domain (the real sampler) compounds the error rather than avoiding it: the
8.8-20% figures were shown to be an artifact of *that* content model's
label-mixture choice, not a property of boundary-shift defects in general.

The real `(T)`-sampler's support draws (`fixed_weight_support`, Floyd's
algorithm over `range(n-w, n)`, `n_e=56`, `omega≈45-51` at PS-R3) produce
genuinely near-uniform weight-`w` index subsets — nothing like the toy
3-point marking mechanism's deliberately boundary-adjacent construction. A
single-index shift (e.g. injection point 2, `range(n-w-1, n-1)`) changes at
most one or two of ~45-51 drawn indices per instance; whether that
perturbation propagates all the way to a detectable `log2_Ahat_k`-level
moment shift is an empirical question about the *real* decoder's margin
distribution over *real* near-binomial supports, which no V1-V3 arm ever
measured (V1-V3 never ran `fixed_weight_support` at all) and which
`cost_model.md` §4.2 explicitly, honestly admits it cannot supply: *"the T
actually needed to detect an injected defect's effect at the estimator
level depends on that defect's effect size on `log2_Ahat_k`, which is
unmeasured and unmeasurable without running the injection."*

That admission is exactly right, and it is exactly why the headline
affordability number should not be read as settled. §4.2's fallback — using
the specification's own frozen `T_req=3.09e5` for the *undefected*
estimator's own precision target as "the best available order-of-magnitude
anchor" — answers a different question ("how much T to resolve the natural
estimator to its own stated SE") than the one that actually matters ("how
much T to reliably distinguish a defect-injected run from an undefected
one"). Those coincide only if the defect's effect size on `log2_Ahat_k` is
comparable to or larger than the estimator's own natural SE at that T — a
condition established for **none** of the four injection points, and least
plausible for the narrowest one (§3 point 4, the last-block-window defect —
literally the V3-class defect that needed the most machinery and still only
showed a 10-20% *block-level* rate, far short of certain propagation).

**What the reported quantity should have done, and the control that's
missing:** if the injected defect is expected to move `log2_Ahat_k` by a
detectable amount, that should show up as a dose-response — a larger
perturbation (e.g. injection point 1, the broadest-scope `CTRStream.below`
shift affecting every draw) should move the statistic by more, and a
narrower one (point 4) by less, roughly tracking how many of the ~45-96
per-instance draws each variant touches. No such prediction or ordering is
given. The cheapest discriminating control is not a bigger benchmark — it is
a **tiny pilot injection run** (a few hundred to a few thousand trials, well
inside this task's own unused budget headroom) at the *narrowest* injection
point, checked for **any** measurable moment shift before committing to the
"139-392 core-seconds is enough" framing for the full T_req-scale run. If
the narrowest defect variant's effect size turns out to be small relative to
the natural estimator SE at T=3.09e5 (plausible, given V3's own ~10-20%
block-level ceiling), the true required T could be one to three orders of
magnitude higher than 3.09e5 — pushing cost from ~139-392 core-seconds to
somewhere between ~14,000 and ~400,000 core-seconds, which would consume a
large fraction to all of the campaign's remaining budget on a single
parameter set and defect variant. This is not a hypothetical concern
invented for this report — it is the same "manifestation rate is far below
what a hand-searched worst-case construction suggests" pattern the V2-batch
Red Team already found once, at the exact same layer of this same
experiment lineage (natural ~8.8% vs V1's forced 100%).

---

## 3. The central question: does "cheap in one clean run" survive this campaign's own track record of required rework?

The dispatch queue asks this directly and I answer it directly: **no, not
at face value, and the gap matters.**

Every one of the four batches this campaign has run under the removed cap
disclosed at least one thing requiring correction before its result could
stand as reported:

- **BATCH-4b8ad3 (V1):** not merely "a defect requiring a fix" but a
  **structural blind spot** discovered *after* a clean run and two ADMIT
  verdicts — the arm was mathematically incapable of detecting the defect
  class it targeted, for any T, discovered only by the Red Team's own
  mutation testing. The repair was not a patch to V1; it was an entirely new
  design (V2), a full new executor task, a full new review cycle. Measured
  by executor core-seconds alone, V2 cost 434.3 vs V1's 72.0 — a ~6x
  escalation, and that ratio does not even count the doubled review/archive
  overhead of running the whole batch cycle twice.
- **BATCH-558f5b (V2):** no disqualifying defect, but a binding correction
  (the "genuine non-zero chance of flipping" language had to be rescoped by
  the Red Team from a measured rate to a deterministic property of one
  hand-searched template pair) and a Validator-flagged gap (raw histogram
  not archived).
- **BATCH-f8050e (V3):** no disqualifying defect, but the Coordinator's own
  framing of the headline result ("closely tracking," "confirming") was
  found by *both* independent reviewers, unprompted, to be an over-read
  requiring correction in the ledger record itself — the third consecutive
  batch in which review corrected a Coordinator framing, per that batch's
  own `process_finding`.
- **This very task (TASK-20260806-77443e):** discloses its own unresolved
  2.6-2.8x internal measurement discrepancy (§1 above) — a defect in the
  cost-model artifact's own methodology, caught by the executor itself
  before I had to find it, but still an unresolved anomaly in the newest
  artifact in the chain.

Four for four. This is not a fatigue-report tally I am using to declare the
lane dead (per `docs/inventor-protocol.md` §4, that would be exactly the
wrong move) — it is a base rate for **this specific kind of task**
(instrument-trust work against `stage_a.py`'s pipeline), and the real-sampler
injection experiment is drawn from the same population: it is mechanically
more complex than any of V1-V3 (touches four candidate injection sites in
code none of V1-V3 ever exercised, in a sampler whose actual near-binomial
support distribution is unvalidated against the toy content models used so
far), which argues the base rate for "needs at least one round of
correction" should not be assumed *lower* than 4/4 going in.

**Pricing this in:** if I take the historical pattern at face value and
assume a comparable probability of needing either (a) a correction-and-rerun
of the same shape (cheap, ~1.2-2x the headline cost, per V2/V3's pattern) or
(b) a full structural redesign (expensive, ~6x-plus the headline cost *and*
a doubled review cycle, per V1→V2's pattern), the true expected cost of
reaching an *admissible* result is not 139-392 core-seconds. A rough
weighting — say, credit the campaign's own improving trend (V1's structural
failure was the outlier; V2 and V3 needed only in-place corrections, not
redesigns) with, at minimum, a 1.5-2x realistic multiplier for ordinary
correction-and-rerun, and hold in reserve the possibility of a V1-style full
redesign if §2's detection-rate transfer problem manifests as "the chosen
injection point shows no measurable signal at the planned T" — puts a
defensible **true expected cost band at roughly 300-800 core-seconds for the
optimistic case, and, if §2's power problem bites and requires an
order-of-magnitude-larger T, potentially several thousand to tens of
thousands of core-seconds** for a fully admissible, reviewed result. The
lower end remains comfortably affordable against the ~4,978-second headroom
this task's own §6 derives. The upper end is not, and the cost model does
not name this scenario as a real possibility with a real number attached —
it names the *mechanism* (§4.2's honest admission) but does not carry it
through to a "if this happens, here is what it costs" line in the cost
table. **That is the single addition I would require before treating this
cost model as decision-ready: a stated cost figure for the scenario where
the pilot-scale detection check in §2 comes back negative or ambiguous, not
just for the scenario where it works cleanly.**

I also flag, without treating it as decisive on its own, that the campaign's
own §6 running-budget total is a **lower bound with an admitted gap**
(validator-session compute is not itemized in any of the three most recent
`batch_checkpoints` entries, and general Coordinator/session overhead is not
tracked against the 10,800-second total at all) — so "~4,978 seconds
remaining" should itself be read as optimistic, not exact, independent of
anything about the real-sampler experiment specifically.

---

## 4. Should the campaign PAUSE instead? A serious case exists; I do not think it is dispositive, but it should not be waved off

The task requires I weigh this seriously rather than default to GO because a
cheap number was reported. I did, and here is the honest accounting.

**The case for PAUSE, stated at full strength:** `GOAL-HQC-001.pause_conditions`
includes *"the decisive computation exceeds the declared campaign budget
after cheaper falsification gates are exhausted."* This cost model's own
§5.b **re-confirms, independently, the campaign's prior BATCH-003
structural-infeasibility finding**: the actual decisive computation — HQC-1's
own real DFR at its own real load-bearing order (`k=m=16`, true `q`) — costs
on the order of `2-3e39` core-seconds, infeasible by roughly 38-39 orders of
magnitude, no matter how favorably the throughput bound is read. That is not
new information, but it is a *third* independent reconfirmation
(BATCH-003, then implicitly every subsequent reduced-parameter batch, now
explicitly again here) that the direct decisive computation this goal's
`completion_criteria` ultimately points toward can never be run. Six
consecutive batches under the removed cap have now been spent almost
entirely on certifying a *single already-collected* reduced-parameter
measurement (PS-R3 / EV-HQC-b71230) against a sampler-defect concern, and
**not one of them has touched the two other completion-criterion items**
(the extrapolation to standardized parameters on numbered heuristics, and
the memory-charged ISD baseline) — both are explicitly, repeatedly deferred
"until OPEN-6 closes," and OPEN-6 has not closed after three full batches of
trying. If the real-sampler experiment *also* comes back ambiguous (a live
possibility per §2), the campaign would be entering its fourth consecutive
"instrument-trust" batch, still with zero progress on the actual completion
criteria, and each of those batches has independently found something to
correct (§3). That is a legitimate diminishing-returns pattern, not a
strawman, and `docs/inventor-protocol.md`'s closure standard cuts both ways:
if premature closure of a promising lane is a failure mode, so is premature,
uncosted continuation of an instrument-validation sub-line whose own
reviewers have twice now (BATCH-f8050e, and implicitly this batch) said has
reached a ceiling in its current form.

**The case against PAUSE, stated at full strength:** OPEN-6 is not a
tangential concern — it is a **load-bearing precondition** for treating
PS-R3's own -244.1-to-32.4-SD anti-correlation result as informative at all;
without it, the campaign's single most substantive measurement to date
cannot be told apart from a sampler artifact, which means pausing now would
leave the campaign's best result in permanent limbo rather than resolved
either way. The specific next step (§3 of `cost_model.md`) is unusually
well-scoped compared to prior HQC-goal next actions: four named injection
points, each confirmed by reading to be a small, local, single-line change,
in code whose self-integrity gate already passes cleanly. And the pause
condition's own text — "after cheaper falsification gates are exhausted" —
has a live cheaper gate still available: the pilot-scale detection check I
name in §2, which costs a few hundred core-seconds and would itself supply
the missing power/effect-size information the current cost model lacks,
before any large commitment is made.

**My own weighing:** I do not think the campaign has yet reached the point
where PAUSE is clearly the more defensible move, because a cheap,
bounded, informative test remains available and untried, and OPEN-6 is
genuinely load-bearing rather than a rabbit hole. But I do not think GO on
the cost model's own terms (fund the full 139-392-core-second run and
proceed to standardized-parameter extrapolation next) is defensible either,
given §2's unpriced power gap and §3's track record. The defensible middle
is a **tightly bounded, single pre-committed pilot**, not an open invitation
to keep iterating on this sub-line indefinitely — see my recommendation
below, which ties continuation to a stopping rule specifically so that a
fourth ambiguous result forces the PAUSE question back onto the table rather
than inviting a fifth.

---

## 5. ADMIT / DO-NOT-ADMIT verdict on the cost model artifact

**ADMIT.** Specifically:

- Arithmetic: correct throughout (independently reverified, §above).
- Scope discipline: clean — no defect injected, `measure.py`/`stage_a.py`/the
  specification untouched, budget (600 core-seconds / 1,800 wall-seconds / 1
  run) respected with wide margin (5.69 core-seconds used).
- Honesty: the 2.6-2.8x discrepancy is self-disclosed in detail rather than
  hidden or silently resolved in the model's favor without comment; the
  standardized-parameter gap (PS-R1/R3/R5 are order-matched proxies, not
  HQC-3/HQC-5's true deployed dup values) is disclosed rather than
  papered over; §4.2 explicitly names what it cannot supply (defect-specific
  power) rather than presenting `T_req=3.09e5` as if it already accounted
  for that.
- What ADMIT does **not** mean: it does not mean the headline "cheap"
  framing should be adopted uncritically for the go/no-go decision. An
  honest artifact can still under-price a real risk it has itself disclosed
  but not fully carried through to a costed scenario (§2-§3 above are that
  gap).

---

## 6. My independent GO / NO-GO / PARTIAL-GO recommendation

**PARTIAL-GO, narrower than the executor's, with a pre-committed stopping
rule.**

1. Fund a **single pilot injection run** at PS-R3, using the **narrowest**
   of the four named injection points (§3 point 4, the last-block-window
   defect — deliberately the hardest case, not the easiest, since a
   detectable signal there is the strongest evidence the approach will
   generalize, and a null result there is the cheapest way to learn that a
   much larger T is needed before committing more budget). Size it first at
   a few hundred to low-thousand trials specifically to check for **any**
   measurable `log2_Ahat_k` moment shift (the control named in §2), not yet
   at the full `T_req=3.09e5` scale.
2. Only if that pilot shows a measurable, non-noise deviation, proceed to
   the full `T_req`-scale run (139-392 core-seconds pessimistic-optimistic,
   per this cost model) **plus a paired undefected control at the same T**
   (not reusing `EV-HQC-b71230`'s T=1e7 dataset for the comparison without
   an explicit justification for why a T-mismatched control is valid, which
   `cost_model.md` §5.a correctly flags as an open design choice, not a
   settled one).
3. **Pre-commit now, in the dispatch decision, to a stopping rule:** if this
   round (pilot + full run) does not produce a clean, admissible result —
   i.e., if it needs a structural redesign of the injection mechanism rather
   than an in-place correction, mirroring V1→V2's pattern — the Coordinator
   should not fund a second full redesign-and-rerun cycle on this sub-line
   without first revisiting PAUSE against `GOAL-HQC-001.pause_conditions`
   explicitly, rather than defaulting to a fifth iteration the way the
   control-arm lineage was allowed to reach a fourth.
4. **Explicitly NOT recommended:** anything beyond PS-R3 scope this round
   (the standardized-parameter table in §5.b, PS-A k≥3, PS-R1 at its own
   k=m=16) — this matches the executor's own recommendation and I concur on
   that boundary specifically.

This differs from the executor's PARTIAL-GO in two concrete ways: it
inserts a cheap pilot-scale detection check *before* committing to the
T_req-scale run (the executor's recommendation goes straight to funding the
T_req-scale run on the strength of the undefected estimator's own precision
target, which §2 shows is the wrong quantity to plan against), and it ties
any further iteration to an explicit, pre-declared stopping rule rather than
leaving the next round's scope to be decided after the fact — which is
exactly the pattern that let the control-arm lineage run three full
generations before its own reviewers said "ceiling."

---

## 7. Budget

This review required reading the full cost model, benchmark script, raw
JSON, run manifest, both ledger records, the full goal record (all
`batch_checkpoints` and `pause_conditions`), and my own prior V3 report, plus
one independent arithmetic re-derivation (Wilson-CI sizing and the cost
table, via a short Python script, sub-second compute). No code from
`stage_a.py` or `measure.py` was executed, modified, or imported by me; I
performed no benchmark re-run (that is `TASK-20260806-069687`'s explicit
job, not mine — my task card asks for optimism analysis and a go/no-go
judgement, not a re-benchmark). **No budget overrun.** Actual work stayed
well inside the 1,200-second wall-clock authorization; the only compute I
executed was the sub-second arithmetic check reported in the preamble.

---

## 8. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-e13ecc
  task_id: TASK-20260806-e13ecc
  claim_under_review: >-
    cost_model.md (TASK-20260806-77443e, snapshot e784c8ba) claims a
    PS-R3-scale real-sampler defect-injection experiment reaching the
    specification's own T_req=3.09e5 costs only 139-392 core-seconds
    (pessimistic-optimistic bound), comfortably inside the smallest
    requested budget tranche and small relative to the campaign's estimated
    ~4,978 core/wall-seconds of remaining budget, and recommends PARTIAL-GO
    scoped to PS-R3 only.
  objections:
    - "The '139-392 core-seconds, cheap' figure plans against the favorable
      side of an unresolved, unexplained 2.6-2.8x internal throughput
      discrepancy (stages_summed vs full_pipeline_via_real_t_shard) that the
      executor discloses but does not resolve; the convergence argument used
      to justify the favorable bound is genuinely strong for the UNMODIFIED,
      UNDEFECTED path (independently corroborated by EV-HQC-b71230's T=1e7
      production run at 2,168 t/cs) but has not been established for a
      defect-injected variant, which has never been timed."
    - "The Wilson-CI detection-rate sizing (T=24,700 at the adopted ±0.5pp
      precision target) is built on the 8.8-20.1% V1-V3 block-level flip
      rate, which the V3-batch red-team review (this same reviewer, prior
      task) already showed is a mixture-dependent artifact of a toy
      marking-mechanism design constant (q=9/28), not a portable natural
      rate -- carrying it forward as an anchor for a DIFFERENT domain (the
      real near-uniform-weight-subset sampler) compounds rather than avoids
      that already-identified error."
    - "cost_model.md section 4.2 honestly admits the T actually needed to
      detect an INJECTED defect's effect on log2_Ahat_k is unmeasured and
      unmeasurable without running the injection, then falls back to the
      spec's own T_req (sized for the undefected estimator's own precision,
      a different quantity) as 'the best available anchor' without pricing
      the scenario where that anchor is wrong -- no cost figure is given for
      the case where the pilot-scale check comes back null or ambiguous,
      which is plausible given the narrowest injection point (last-block
      window) is exactly the V3-class defect that needed the most machinery
      to detect even at the block level."
    - "The campaign's own track record is 4-for-4: every batch since the
      cap was removed (V1, V2, V3, and this cost-model task itself) disclosed
      at least one required correction, one of which (V1 to V2) was a full
      structural redesign costing roughly 6x the original executor spend
      plus a doubled review cycle. The cost model treats '139-392
      core-seconds' as the answer to 'is this affordable' without pricing a
      comparable probability of needing an equivalent redesign cycle here."
    - "The ~4,978-second remaining-budget estimate (cost_model.md section 6)
      is an admitted lower bound: validator-session compute is not itemized
      in any of the three most recent batch_checkpoints entries, and general
      Coordinator/session overhead is untracked against the 10,800-second
      total entirely."
  required_controls:
    - "Re-run the calibration benchmark with stage order randomized per
      parameter set and decode_blocks pre-warmed before ANY stage timing, to
      determine whether the 2.6-2.8x stages_summed-vs-t_shard gap is a
      cold-start artifact (as hypothesized) or a real cost a single
      defect-injection run would actually pay. Cheap (minutes), and directly
      de-confounds the one figure the affordability argument leans on most."
    - "Before committing to the full T_req=3.09e5 run, execute a small pilot
      injection (a few hundred to low-thousand trials) at the NARROWEST
      named injection point (last-block-window shift) specifically checking
      for ANY measurable log2_Ahat_k moment shift -- the missing
      dose-response/effect-size control that would let the campaign know,
      cheaply, whether 3.09e5 is remotely the right order of magnitude for
      T_req at the estimator level, rather than assuming it is because it is
      the only frozen number available."
    - "State a cost figure, not just a mechanism, for the scenario where the
      pilot check in the prior bullet is null or ambiguous -- e.g. what T,
      and what core-second cost, would be needed if the true detectable
      effect size requires one or two orders of magnitude more trials than
      T_req."
  counterexample_or_mutation: >-
    Independently recomputed the Wilson-CI sizing table and the derived
    cost-table arithmetic from raw benchmark_results.json throughput figures
    via a short Python script; all figures match to stated precision (e.g.
    n=24,678.3 at p=0.201/w=0.005 vs reported "24,678"; T_req cost
    138.8-392.1 core-seconds at 2227/788 t/cs vs reported "139-392"). No
    arithmetic error found -- the objections above are about which
    quantities were plugged into correct arithmetic, not about the
    arithmetic itself.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/ECDLP sense -- this is a
    feasibility cost model for an HQC decoding-instrument validation
    experiment, not an asymptotic-complexity claim. The relevant "baseline"
    is the campaign's own prior three control-arm generations (V1/V2/V3),
    against which this task's proposed real-sampler injection is compared
    throughout section 3 above on cost, track record, and information
    yield rather than on algorithmic complexity.
  heuristic_challenges:
    - "The implicit heuristic 'a boundary-index-shift defect's block-level
      detection rate under toy planted content (8.8-20.1%) is a usable proxy
      for its manifestation rate under the real near-uniform-weight-subset
      sampler' is neither numbered nor justified by any random-model
      argument connecting the two domains -- it is adopted by default because
      it is the only number the campaign has, not because a case is made for
      transfer. This is exactly the kind of implicit, unnumbered assumption
      docs/target-result-profile.md's heuristic-inventory discipline would
      flag if this were an asymptotic claim; it is flagged here even though
      this is a toy-tier feasibility model, because the affordability
      conclusion depends on it."
  cost_model_challenges:
    - "Total expected cost is not priced as per-attempt cost times inverse
      success probability here: the model reports per-attempt cost
      (139-392 core-seconds for one clean pilot/run) without folding in the
      campaign's own empirically-observed ~100% rate (4/4 recent batches) of
      needing at least one correction cycle, nor the smaller but real
      probability (illustrated by V1-to-V2) of needing a full redesign
      costing several times the headline figure plus a doubled review cycle."
    - "The favorable throughput bound (2,227 t/cs) used as the 'primary
      planning figure' is corroborated for the undefected path by an
      independent T=1e7 production run, but no equivalent corroboration
      exists for a defect-injected variant of the same code -- the cost
      model treats this as settled by analogy rather than flagging it as an
      open, cheaply-testable gap."
    - "dominated_by / Pareto-frontier fields are not applicable to this
      artifact (it is a feasibility cost model, not a competing mechanism
      against a baseline algorithm) -- noted rather than left silently
      unaddressed, per the requirement to check every unchecked null."
  reduction_and_scope_challenges:
    - "The four named injection points (CTRStream.below, fixed_weight_support
      range, ring_mul_sparse accumulation, decode_blocks reshape) are
      confirmed by reading to be small, local changes -- I did not find this
      claim overstated. But the cost model treats all four as
      interchangeable for T_req-sizing purposes when they plausibly have
      very different expected effect sizes on log2_Ahat_k (point 1, global
      CTRStream shift, touches every draw; point 4, last-block-window,
      touches one block only) -- the affected-injection-point scope should
      not be flattened to one T_req figure without naming which point that
      figure is actually sized for."
    - "PS-R1/PS-R3/PS-R5 are correctly and explicitly labeled as
      order-matched proxies (dup=1), not HQC-3/HQC-5's true deployed
      parameters -- this scope limitation is honestly stated, not inflated,
      and I confirm it rather than object to it."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The cost model's arithmetic is correct and its methodology honestly
    discloses its own central weakness (the 2.6-2.8x throughput gap and the
    missing defect-specific power calculation), which I ADMIT as an
    artifact. But its headline affordability conclusion (139-392
    core-seconds, comfortably cheap) is optimistic because it (a) resolves
    an unexplained internal discrepancy in its own favor for a scenario
    (defect-injected timing) it has not actually corroborated, and (b)
    anchors its required-T calculation to a detection-rate figure already
    shown, by this same reviewer's prior report, to be a mixture-dependent
    toy artifact rather than a portable rate, without establishing that
    figure transfers to the real sampler's structurally different support
    distribution. A single clean PS-R3-scale run, if the first attempt
    succeeds without needing redesign, is genuinely affordable against the
    campaign's remaining budget; a realistic accounting for this campaign's
    own 4-for-4 track record of needing at least one correction cycle, and
    for the live possibility that the chosen injection point shows no
    measurable signal at the planned T, pushes the TRUE expected cost of an
    admissible result into a wide band whose upper end is not comfortably
    affordable and is not priced anywhere in the artifact. The campaign has
    not yet reached a point where PAUSE is clearly the better call --
    OPEN-6 remains genuinely load-bearing and a cheap discriminating pilot
    remains untried -- but continuing without a pre-committed stopping rule
    would repeat the exact pattern (open-ended iteration past the point
    reviewers themselves called a ceiling) that ended the control-arm
    sub-line three batches ago.
  next_concrete_action: >-
    Dispatch a bounded pilot injection at the narrowest named defect class
    (last-block-window shift) at small scale (hundreds to low-thousands of
    trials) checking specifically for a measurable log2_Ahat_k moment shift,
    BEFORE committing to the full T_req=3.09e5 run -- and have the
    Coordinator record, in the same decision that authorizes this, an
    explicit stopping rule: if this round needs a structural redesign rather
    than an in-place correction, the next step is a PAUSE review against
    GOAL-HQC-001's declared pause_conditions, not an automatic V2-style
    rebuild.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/cost_model.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/benchmark.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/benchmark_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/tasks/TASK-20260806-77443e/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/archives/TASK-20260806-f238a2/snapshot-receipt.json
    - ledger/evidence/EV-HQC-163374.yaml
    - ledger/decisions/DEC-20260806-0995d5.yaml
    - ledger/goals/GOAL-HQC-001.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-f8050e/reviews/TASK-20260806-7008de/red_team_report.md
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement,
not a confirmation of the executor's framing, and not a re-adoption of my
own prior (V3-batch) recommendation without fresh scrutiny of timing and
budget as they stand today.*
