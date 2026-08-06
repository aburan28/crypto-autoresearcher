# Red-team report — pilot real-sampler defect injection (TASK-20260806-77a574)

**Task** `TASK-20260806-92aecb` (red team) · **Batch** `BATCH-2ecaa1` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`17d5fb54` (`TASK-20260806-1281e1`, parent `edaf49466e0c...`, verified against
the snapshot receipt's `path_sha256` map) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/{design.md,pilot_injection.py,pilot_results.json,pilot_report.md,run_manifest.yaml,stdout.log,stderr.log}`.
Also read `ledger/decisions/DEC-20260806-1ac8fa.yaml` (the binding stopping
rule), the prior batch's own red-team report
(`BATCH-a5c525/reviews/TASK-20260806-e13ecc/red_team_report.md`, which I
wrote, read here as the artifact whose narrow recommendation this pilot
claims to implement, not as license to re-adopt it uncritically), and — to
independently probe the injection mechanism per this task's constraint 2 —
`stage_a.py` and `measure.py` directly, sha256-pinned, read-only, exactly as
the executor's own convention requires.

**I do not confirm the executor's framing on the strength of the reported
numbers alone.** I independently re-implemented the exact V3 transform
against the real, unmodified `decode_blocks` on fresh, previously-unused
PRNG shards, and the result changes the shape of the verdict: the injection
mechanism is sound and its local effect is large and unambiguous — more
convincingly than the pilot's own artifacts show — but the reported "clean
null" at the joint-moment level is close to a foregone conclusion of the
comparison method chosen, not evidence that the propagated effect is small.
Details below.

---

## 0. Independent reproduction: what I actually ran

Budget used: two short Python scripts (~20 wall-seconds of compute total,
well inside the 1,800-second authorization), both loading `stage_a.py`
(sha256 `06a0a618...681405`, matching the pinned value in every artifact
under review) and `measure.py` (sha256 `a4fd1ecb...f5dc8`) **read-only**,
identically to `pilot_injection.py`'s own `load_module()` pattern, and
consuming **fresh** PRNG shards (`424242`) disjoint from every shard used
anywhere in this campaign's committed record (Stage-A `0-3`/`900`,
cost-model `999`, `measure.py` `1000-1007`, this pilot's own `5000`/`6000`/
`4900`/`4901`) — so this is a genuinely independent measurement, not a
re-read of the pilot's own numbers.

**Probe 1 — does the injection actually fire, and does it matter, on the
SAME trials (matched pairs)?** For 5,000 freshly-generated PS-R3 trials, I
decoded each trial's bit array twice: once through the real, unmodified
`decode_blocks` (the true bits), and once after applying the *exact* V3
transform from `design.md` §3 / `pilot_injection.py`'s
`make_defected_decode_blocks` (`bits_defected[:, lo:hi] = bits[:, lo-1:hi-1]`)
to the SAME underlying random draws, then decoding that.

```
last-block F flip rate (matched pairs, SAME draws): 533/5000 = 0.1066
other-block F changes (should be 0): 0
marginal P(F_{n_e-1}=1) true=0.3198 defected=0.3280 diff=0.0082
matched-pair flip-rate SE (binomial): 0.00436  =>  z ~ 24.4
```

**Probe 2 — how much statistical power did the pilot's between-shard
comparison design leave on the table?** Using the same matched trials, I
computed `log2_Ahat_k` for both the true and defected decode of the SAME
5,000 instances (via `measure.py`'s own `comb_matrix`/`log2_A_from_hists`,
`stage_a.py`'s own `hist_of`/`batch_hists`, identically to the pilot's own
estimator call), then compared two ways of forming the defected-minus-true
difference and its SE: (a) treating the two arms as **independent** (as the
pilot's own between-shard design effectively does — quadrature-sum of two
separately-jackknifed SEs), and (b) a **matched-pair jackknife on the
per-batch difference itself**, which is available for free because both
arms here share the same underlying randomness.

```
k=17: point_true=-0.9360  point_def=-0.7438  diff=+0.1922
k=17: SE unpaired (independent-arm quadrature) = 0.5514   z=0.349
k=17: SE paired   (matched-pair jackknife)      = 0.1982   z=0.970
k=17: power ratio (unpaired SE / paired SE)     = 2.78x
k=2:  power ratio                                ~10.6x
k=24: power ratio                                ~1.63x
```

Full scripts and output are reproducible from the sha256-pinned imports
alone; I did not modify, and my probe never wrote to, `stage_a.py` or
`measure.py`.

**What this establishes, stated precisely:**

1. **The injected defect has a large, unambiguous, trivially-significant
   local effect** (z ≈ 24 on a matched-pairs binomial test, 10.7% of trials
   flip block `n_e-1`'s decode outcome) — this is a *much* stronger,
   independent confirmation that the injection genuinely fires and matters
   than anything in the pilot's own artifacts, which never measure the
   injection's effect against a matched baseline at all.
2. **A matched-pair (same-random-draws) design is available essentially for
   free** — it costs no additional PRNG draws, reuses the identical `bits`
   array, and needs one extra `decode_blocks` call per batch — and would
   have given the pilot's own comparison **2.8x to 10x** tighter standard
   errors at the same trial count, depending on `k`.
3. **The pilot's actual design does not use this.** `design.md` §1 calls the
   second arm a "paired... control arm," but it is not matched pairs: it
   draws **disjoint PRNG shards** (`5000` defected, `6000` undefected) and
   compares the two arms' independently-jackknifed estimates by summing
   their SEs in quadrature — the *less* powerful of the two designs
   available, at the *same* trial-count cost as the more powerful one.

---

## 1. Was the injection point/defect choice a shortcut, or representative?

`design.md` §2 justifies V3/`decode_blocks` on stringency grounds (narrowest
of four points, my own prior-batch recommendation), and I do not dispute
that rationale on its own terms — it is a real, correctly-applied argument,
not a fig leaf. But the task instruction asks specifically whether an
*easiest-to-implement* motive is also present and unacknowledged, and reading
`stage_a.py`'s `_t_shard` (lines 496-543) answers this directly: `decode_blocks`
is called **once per batch of up to 64 trials**, on a full `(B, N)` array,
as a single free function resolved by module-global lookup — trivially
wrappable by reassigning `sa.decode_blocks` to a thin array-preprocessing
closure, exactly as `pilot_injection.py` does. The other three named points
(`CTRStream.below()`, `fixed_weight_support`'s Floyd range, `ring_mul_sparse`)
are called **per-index, inside nested per-trial loops** (lines 499-511) —
injecting into any of them would require either patching a class method
used recursively inside a hot loop, or intercepting a per-call integer
argument deep inside `fixed_weight_support`'s Floyd's-algorithm body, which
is a structurally different and more invasive kind of patch than "reassign
one module-level function name."

**This is not raised to accuse the executor of picking the easy point under
cover of stringency — the stringency argument is independently valid and I
endorse it.** It is raised because "mechanically sound" has now been
demonstrated for **exactly one of the four named points**, and that one
happens to be the technically easiest to wrap externally without touching
internals. Nothing in this pilot tells the campaign whether a thin-wrapper
injection is even *possible* for the other three without editing function
bodies — which `design.md` §5 itself would classify as "needs structural
redesign" (its criterion 1) if discovered. The mechanical-soundness claim
should be read as scoped to `decode_blocks`'s injection point specifically,
not to "real-sampler defect injection" as a general capability.

**On defect-class coverage:** V1 (global shift, touching every block) was
explicitly and honestly not tested — stated as a scope boundary, not
smuggled. I agree this is a defensible, disclosed choice for a single pilot
covering "one defect class." But combined with §2 below, its absence has a
specific consequence: V1 would have been the **positive control** this
pipeline still lacks (see §2).

---

## 2. Is the clean null informative, or an artifact of underpowering? (Answered empirically, not just argued)

This is the central finding of this review, quantified in §0 above.

**Claim under scrutiny:** `pilot_report.md` §4 reports the paired
defected-minus-undefected difference at `k=m=17` as `z = -0.466`, calls it
"a clean null... exactly the primary outcome design.md §4 pre-registered as
most likely," and the campaign's stopping rule (`DEC-20260806-1ac8fa`)
treats "a measurable signal or a clean null" as equally sufficient for
"succeeds cleanly" → scale to the full run.

**What the reported quantity should have done, stated in advance:** if the
injected defect genuinely propagates to the joint-moment statistic at a
magnitude the campaign could ever hope to detect, the *right* test to run
first is the most powerful comparison available at pilot scale — matched
pairs, not independent shards — specifically because Section 0's probe shows
the underlying per-trial effect is not small (10.7% local flip rate, not
the vague "measurable but likely small fraction" `design.md` §4 predicted
without a number). A null on the **less powerful** of two equal-cost designs
does not distinguish "the effect doesn't propagate" from "the test chosen
couldn't have seen it either way."

**Concretely:** my own matched-pair reproduction at T=5,000 (a *fresh*,
independent shard, not the pilot's own shards, so not directly comparable
number-for-number) still does not clear significance at k=17 (z≈0.97) —
so I am not claiming the null is wrong, or that a "measurable signal" was
actually there and missed. I am establishing that **the pilot's own
between-shard design could not have told the difference between "the
propagated effect is genuinely near zero" and "the propagated effect is on
the order of the matched-pair point estimate (~0.19-0.21 in log2_A_17
units, which both my probe and the pilot's own diff essentially agree on)
but this T and this design cannot resolve it."** Both a zero effect and a
~0.2-unit effect are consistent with what was observed. That is the
definition of an inconclusive result, not a confirmed clean null, and it is
inconclusive **specifically because of a design choice, not because of an
intrinsic power ceiling** — the ~free matched-pair alternative would have
materially narrowed that ambiguity at the *same* trial count.

**Is this expected given prior campaign findings?** Yes, and the pilot's own
design document half-acknowledges why (dilution: only `k/n_e ≈ 0.30` of `k=17` subsets
touch the perturbed block) — but `design.md` never converts that intuition
into a number, and the SE achieved (0.44, unpaired) is roughly what a naive
power calculation from the specification's own `T_req=3.09e5` sizing
(itself derived for a *different* target quantity, per the prior batch's
red-team objection, un-retracted here) would predict at T=5,000. So: **not
surprising, and not informative about mechanical soundness OR about
detectability** — it is close to the expected outcome of an under-designed
comparison at this scale, regardless of ground truth.

**The missing positive control.** Per `docs/inventor-protocol.md`'s
controls-before-belief standard (usually invoked to distrust a signal
without a null-object control), the same logic runs in reverse here: **a
null is not trustworthy without a positive control showing the same
pipeline, at the same scale, can detect a *known-present*, less-diluted
effect.** No batch in this campaign — not V1/V2/V3 (never ran the real
sampler at all), not this pilot — has ever produced a *fired* joint-moment
cell from a genuine real-sampler injection. The detection pipeline
(`decode_blocks`-level injection → `log2_Ahat_k` joint estimator) has zero
track record of catching anything it was pointed at. A null from an
instrument that has never once demonstrated it can ring is weaker evidence
than a null from one that has.

---

## 3. Injection mechanism: independently probed, not merely read

Task constraint: check whether the monkey-patch is genuinely exercised on
every trial, and whether "0 injection-invariant violations" is trivially
true.

**Genuinely exercised, confirmed by reading + reproduction.** `_t_shard`
(line 543) resolves `decode_blocks` as a **module-global name lookup at
call time**, inside a `while t < n_trials` loop that calls it once per batch
(`BATCH=64`) for the *entire* duration of one `_t_shard` invocation.
`pilot_injection.py` reassigns `sa.decode_blocks` once, before calling
`sa._t_shard(...)` for the defected arm, and restores it immediately after
— so every one of the ~79 batches inside that one call sees the patched
function, with no fork/spawn ambiguity (the executor's choice of
single-process execution, explicitly justified in `run_manifest.yaml`, is
correct and necessary here — multiprocessing would have broken the
monkey-patch's propagation to worker processes, a real risk the executor
correctly avoided rather than merely disclosed). I confirm this by direct
reading of `_t_shard`'s source, and independently by my own §0 reproduction,
which performed the identical patch-and-call sequence and observed the
expected large behavioral difference — the strongest possible evidence the
patch is live, stronger than an `id()`-equality check alone could ever be.

**The injection invariant is real but largely tautological, and this
matters for how much weight "0 violations" should carry.** The invariant
(`design.md` §3) checks that the perturbed array `b`, which was constructed
two lines earlier by `b[:, lo:hi] = bits[:, lo-1:hi-1]`, in fact satisfies
`b[:, lo+1:hi] == bits[:, lo:hi-1]` and `b[:, lo] == bits[:, lo-1]`. This is
checking that a NumPy slice assignment did what a NumPy slice assignment
deterministically does — it would only fail on an implementation bug in the
`lo`/`hi` arithmetic itself (which the deliberate-mismatch dry run correctly
demonstrates it *can* catch). It does **not** independently verify that
`decode_blocks` was actually called with the perturbed array `b` rather
than the original `bits` — that fact is visible only by reading the
adjacent source line (`return original_decode_blocks(b, n_e, n_2, dup)`),
not by any runtime check. This is a fair, narrow version of the "trivially
true" concern the task asked me to check: the invariant is a legitimate
arithmetic-correctness check, correctly exercised, but "0 violations" should
not be read as proof the defect had any downstream effect — only my §0
reproduction (or an equivalent independent behavioral comparison) supplies
that.

---

## 4. Were design.md's pre-registered criteria strict enough to be falsifiable?

Reasonably strict **for what they scope**: the "needs structural redesign"
list (§5, five conditions) names concrete, checkable failure modes (defect
requires editing decoder internals; invariant fails to abort under a
deliberate break; D2/D3 fire on the defected arm; `NaN` at `k=m` on a
full-T arm; any uncaught exception) and none of them is trivially
unsatisfiable or trivially always-true — I do not find the "almost anything
short of a crash passes" pattern the task asked me to check for. The
`sha256`-mismatch and injection-invariant dry runs are genuine, executed
inline, and demonstrably capable of failing (I re-read both `SystemExit`
paths and they are real aborts, not soft warnings).

**What the criteria are silent on, and why that silence matters here:**
nowhere in §5's seven "mechanically sound" conditions or five
"needs-redesign" conditions is there any criterion referencing **statistical
power, minimum detectable effect size, or the adequacy of the comparison
design** — "mechanically sound" is scoped entirely to code-level
correctness (crashes, invariants, identity, finiteness), which is a
legitimate and honestly-labeled scope. The gap is not in `design.md`'s own
honesty — it says exactly what it checks — but in `DEC-20260806-1ac8fa`'s
stopping rule, which reads "a measurable signal or a clean null... without
requiring structural redesign" as sufficient grounds to scale to the full
run. That phrasing silently imports "clean null" (a code-mechanical
category) as if it settles the (statistical, and per §2 above,
demonstrably underpowered) question of whether this comparison design can
tell the campaign what it needs to know before spending the full budget.

---

## 5. ADMIT / DO-NOT-ADMIT verdict

**ADMIT** the artifacts as an honest, reproducible record of what was
actually done. Specifically:

- Every reported number I attempted to reproduce independently (the
  injection mechanism, its firing on every batch, the qualitative shape of
  its local effect) reproduced correctly against the sha256-pinned source.
- `design.md` genuinely predates data generation in every way I can check
  (git history/provenance chain, internal cross-references, and the honest
  "no confident directional prediction" framing in §4, which is not the
  kind of thing a retrofitted document tends to include).
- No cherry-picking: the report discloses both arms' large individual
  deviations from 0 (`z=-3.84` defected, `z=-2.57` undefected at k=17)
  *before* explaining why the paired difference, not either arm alone, is
  the isolating quantity — this is presented honestly rather than
  suppressed in favor of the more favorable-looking difference number.
- Scope discipline is clean: budget usage is a small fraction of
  authorization on every dimension, no file outside the task's write scope
  was touched, and the claim tier is held at toy throughout.
- **What ADMIT does not mean:** it does not mean the "clean null, as
  predicted" framing should be read as informative about whether the
  injected defect propagates to the joint-moment statistic, nor that the
  comparison design chosen was the strongest one available at the same
  cost. An honest artifact can still under-power the exact question the
  stopping rule needs answered — which is what §0-§2 establish.

---

## 6. My independent judgement: GENUINELY AMBIGUOUS / INCONCLUSIVE

I separate two questions the stopping rule conflates:

**(a) Is the real-sampler injection mechanism mechanically sound?** **YES —
more strongly than the pilot's own artifacts establish.** My independent
matched-pair reproduction (z≈24 on the local flip rate) is stronger,
harder-to-fake evidence of correct, consequential injection than the
pilot's own `id()`-identity and tautological-invariant checks. I do not
recommend a structural redesign of the injection wrapper itself; none is
needed for `decode_blocks`'s injection point.

**(b) Does this pilot supply what the stopping rule needs — evidence that
the current design (between-shard comparison, T scaled per the executor's
undefected-estimator-derived T_req) will produce a decisive result at full
scale, rather than a second uninformative null bought at ~150-400
core-seconds?** **NO — this is where I judge the pilot inconclusive**, for
reasons quantified in §0 and §2: the comparison method used is
demonstrably (2.8x-10x, depending on k) less powerful than a
same-cost alternative, no power calculation was performed against the
defect's own measured local effect size (which is not small — 10.7%, not
the vague "likely small" `design.md` guessed), and no positive control has
ever shown this exact detection pipeline can produce a fired cell from a
real, known-present injected defect.

**This is not "needs structural redesign" (that would trigger PAUSE on
grounds the injection mechanism doesn't work — it does) and it is not
"mechanically sound, scale up" (that would accept the stopping rule's
conflation of code-level cleanliness with statistical adequacy, which §0-§2
show is unwarranted here).** It is a case for one more bounded, cheap pilot
addendum before committing the full run:

1. **Re-run the SAME defect at the SAME injection point using a matched-pair
   (same-random-draws) comparison** instead of independent shards — free in
   additional PRNG draws, needs one extra `decode_blocks` call per batch,
   and (per §0) buys 2.8x-10x tighter SEs at the same trial count.
2. **Compute an actual required-T for detecting an effect of the
   observed local magnitude** (10.7% flip rate on the perturbed block, not
   the specification's `T_req` sized for the undefected estimator's own
   precision target — a different question, per the prior batch's
   still-unretracted red-team objection) before committing to
   `T ≈ 3.09e5` as the right scale for the *next* run.
3. **Run one positive-control pilot** — the same mechanism, at the broader
   V1-class injection point (or any less-diluted point), at the same
   pilot-scale trial count — to establish, for the first time in this
   campaign, that the real-sampler-to-joint-moment detection pipeline can
   produce a fired/significant cell from a genuinely present defect. Absent
   this, a null from the narrowest point is uncalibrated: there is no
   evidence in six batches that this pipeline can ever say "yes" to
   anything.

Each of these is order-of-magnitude cheaper than the pilot already run
(reuses already-generated bits, or reuses the same trial count at a
different injection point) and would convert "genuinely ambiguous" into a
real answer before the campaign spends the full `T_req`-scale budget on a
design I have shown leaves several-fold power on the table for free.

---

## 7. Budget

Reading: full pilot artifact set, the binding decision record, the prior
batch's red-team report, and the two reused source files. Compute: two
independent Python reproductions against the sha256-pinned `stage_a.py`/
`measure.py`, fresh PRNG shard `424242`, ~20 wall-seconds total, no
multiprocessing, no write access to either reused file. **No budget
overrun** — total wall-clock for this review is a small fraction of the
1,800-second authorization.

---

## 8. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-92aecb
  task_id: TASK-20260806-92aecb
  claim_under_review: >-
    pilot_report.md (TASK-20260806-77a574, snapshot 17d5fb54) claims the
    real-sampler V3/decode_blocks defect injection is mechanically SOUND
    against every pre-registered criterion, and reports a "clean null" on
    the paired defected-minus-undefected comparison at k=m=17
    (diff=-0.207, SE=0.444, z=-0.466), offered as the pilot's factual input
    to DEC-20260806-1ac8fa's binding stopping rule for whether the campaign
    scales to the full T_req~3.09e5 run.
  objections:
    - "The comparison design (disjoint PRNG shards, 5000 defected vs 6000
      undefected, SEs combined in quadrature) is demonstrably less powerful
      than a same-cost matched-pair (same-random-draws) alternative: my own
      reproduction shows a 2.8x (k=17) to ~10.6x (k=2) tighter SE from
      matched pairing at the identical trial count, using the identical
      sha256-pinned decode_blocks and the identical V3 transform."
    - "The reported clean null is consistent with BOTH a genuinely near-zero
      propagated effect AND a real effect of the magnitude both this
      review's and the pilot's own point estimates suggest (~0.19-0.21 in
      log2_A_17 units) -- the between-shard design used cannot distinguish
      these at T=5,000, so 'clean null, as predicted' should not be read as
      informative about propagation, only about the SE floor of the method
      chosen."
    - "design.md's per-trial effect-size language ('a MEASURABLE but likely
      SMALL fraction... should flip') is not quantified anywhere in the
      pre-registration; my independent matched-pair measurement puts the
      actual local flip rate at 10.7% (533/5000), which is not obviously
      'small' and was never checked against a numeric threshold before the
      run."
    - "The injection-invariant check (design.md Section 3) that reports '0
      violations' is largely tautological: it verifies that a NumPy slice
      assignment produced the array shape it was constructed to produce, not
      that decode_blocks was actually called on the perturbed array with any
      downstream consequence -- that fact is established only by reading the
      adjacent source line, or by an independent behavioral reproduction
      such as this review's Section 0, not by the invariant itself."
    - "No batch in this six-batch campaign, including this pilot, has ever
      produced a POSITIVE (fired/significant) result from a real-sampler
      injection through the full detection pipeline (decode_blocks-level
      defect -> log2_Ahat_k joint estimator). A null from a pipeline with no
      track record of ever detecting anything it was pointed at is weaker
      evidence than a null from one with a demonstrated positive control."
    - "Mechanical soundness has been demonstrated for exactly one of the
      four named injection points (decode_blocks), which is also, by
      reading _t_shard, the structurally easiest of the four to wrap
      externally (one function call per batch vs. per-index calls nested
      inside per-trial loops for the other three) -- this does not
      contradict design.md's stringency rationale, but the resulting
      mechanical-soundness claim should be scoped to this one point, not to
      real-sampler injection generally."
  required_controls:
    - "Re-run the identical defect/injection point using a matched-pair
      (same-random-draws) comparison instead of independent PRNG shards --
      reuses already-generated bits, costs one extra decode_blocks call per
      batch, and (per this review's Section 0) buys 2.8x-10x tighter SEs at
      the same trial count, essentially for free."
    - "Compute an actual required-T for detecting an effect of the observed
      local magnitude (10.7% block-level flip rate), rather than reusing
      the specification's T_req, which is sized for the undefected
      estimator's own precision target -- a different quantity, per the
      still-unretracted objection in TASK-20260806-e13ecc Section 2."
    - "Run one positive-control pilot at a less-diluted injection point
      (e.g. V1's global shift) at the same pilot trial count, to establish
      for the first time that this detection pipeline can produce a fired
      cell from a genuinely present real-sampler defect."
  counterexample_or_mutation: >-
    Independently reproduced the exact V3 transform against the real,
    sha256-pinned decode_blocks on a fresh PRNG shard (424242, disjoint from
    every shard used anywhere in this campaign's record) using a MATCHED-PAIR
    design (same underlying random draws, decoded once true and once
    defected). Found a large, trivially significant local effect (10.7%
    block-level flip rate, z~24) that the pilot's own between-shard design
    is not powered to resolve at the joint-moment level -- and showed the
    matched-pair alternative would have given 2.8x-10.6x tighter SEs at the
    identical trial count, using only the compute already implicit in the
    trials the pilot generated.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/ECDLP sense -- this is an
    instrument-validation pilot for an HQC decoding-correlation estimator,
    not an asymptotic-complexity claim. The relevant comparison is
    within-design: the between-shard comparison the pilot used against the
    matched-pair comparison this review demonstrates was available at equal
    cost, and against the campaign's own six-batch record of never having
    produced a positive detection through this pipeline.
  heuristic_challenges:
    - "design.md Section 4's expectation of 'a measurable but likely small
      fraction' of flips is qualitative and unquantified in the
      pre-registration; this review supplies the missing number (10.7%) and
      finds it larger than the pre-registered language's framing implies,
      though still diluted enough by k/n_e that the joint-moment test
      remains ambiguous at this trial count."
    - "The stopping rule (DEC-20260806-1ac8fa) treats 'a measurable signal
      or a clean null... without requiring structural redesign' as a single
      sufficient condition for scaling up. This conflates a code-mechanical
      category (no redesign needed) with a statistical-adequacy question
      (was the comparison powered to tell null from small-but-real apart) --
      the two do not coincide here, per Sections 0 and 2 above."
  cost_model_challenges:
    - "Scaling to the full T_req=3.09e5 run using the executor's original,
      undefected-estimator-derived sizing (rather than a required-T
      recomputed from the injected defect's own now-measured local effect
      size) risks spending the full 139-392 core-second budget on a second
      inconclusive result, for the same underpowering reason identified in
      Section 2 -- a cheap matched-pair power check should precede that
      commitment, not follow it."
    - "The throughput comparison itself (2,097.6 t/cs defected vs 2,105.6
      t/cs undefected, ~3% below the cost model's optimistic band) is not
      disputed; my objections are entirely about statistical detectability,
      not about the throughput measurement, which I did not attempt to
      independently re-benchmark (outside this review's scope; the
      Validator's task card covers re-benchmarking)."
  reduction_and_scope_challenges:
    - "Mechanical soundness is validly established for exactly one of the
      four named injection points and should not be read, in the next
      Coordinator decision, as generalizing to CTRStream.below(),
      fixed_weight_support's Floyd range, or ring_mul_sparse -- those three
      are called per-index inside nested per-trial loops (stage_a.py lines
      499-511), a structurally different and more invasive injection
      surface than decode_blocks's single per-batch call."
    - "V1 (global shift) remains untested in the real sampler, as disclosed.
      Its absence is not an overclaim, but it is also the most natural
      candidate for the positive-control run named above, since it touches
      every block rather than one out of 56."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The real-sampler injection mechanism at the decode_blocks/V3 point is
    genuinely mechanically sound -- independently reproduced here with
    stronger evidence (a large, unambiguous matched-pair effect) than the
    pilot's own artifacts supply. But the pilot's reported "clean null" at
    the joint-moment level is not informative about whether the injected
    defect propagates to a detectable degree at larger T, because the
    between-shard comparison design used is demonstrably (2.8x-10.6x,
    depending on k) less powerful than a same-cost matched-pair alternative,
    and no power calculation was ever performed against the defect's own
    measured effect size. ADMIT the artifacts as honest and reproducible;
    DO NOT read "mechanically sound" as settling whether this design is
    ready to license the full T_req-scale commitment. My independent
    judgement is GENUINELY AMBIGUOUS / INCONCLUSIVE on the go/no-go question
    specifically (not on the injection mechanism, which I affirm), pending
    the three named, cheap, pilot-scale additions.
  next_concrete_action: >-
    Before committing to the full T_req-scale run: (1) re-run the identical
    V3/decode_blocks injection using a matched-pair (same-random-draws)
    comparison instead of independent shards -- free in additional PRNG
    draws, ~3-10x tighter SEs at the same trial count; (2) recompute the
    required T for detecting an effect of the injection's own measured local
    magnitude (10.7% block-level flip rate), rather than reusing the
    specification's undefected-estimator T_req; (3) run one positive-control
    pilot at a less-diluted injection point (e.g. V1's global shift) to
    establish, for the first time in this campaign, that the real-sampler
    detection pipeline can produce a fired cell from a genuinely present
    defect. All three are affordable within a few hundred core-seconds,
    reusing this pilot's own machinery.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_injection.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/archives/TASK-20260806-1281e1/snapshot-receipt.json
    - ledger/decisions/DEC-20260806-1ac8fa.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-a5c525/reviews/TASK-20260806-e13ecc/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement:
I neither confirm the executor's framing nor re-adopt my own prior
(BATCH-a5c525) recommendation without fresh, independently-reproduced
evidence, which this review supplies via Section 0's original computation
against the sha256-pinned source, not merely by reading the pilot's own
reported numbers.*
