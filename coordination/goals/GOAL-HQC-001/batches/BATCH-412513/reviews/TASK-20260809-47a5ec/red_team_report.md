# Red-team report — matched-pair reconstruction and extension (TASK-20260809-a79e4f)

**Task** `TASK-20260809-47a5ec` (red team) · **Batch** `BATCH-412513` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`6a7a9dd53b3e2c9641a91dbd0f1c187566868ca8` (task `TASK-20260809-a87710`) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/{design.md,matched_pair.py,matched_pair_results.json,matched_pair_report.md,run_manifest.yaml,stdout.log,stderr.log}`.
Also read `ledger/decisions/DEC-20260809-46e85c.yaml` (the pre-registered
branch rule), `ledger/goals/GOAL-HQC-001.yaml`'s `next_action`,
`ledger/evidence/EV-HQC-dd85c1.yaml`, my own prior standing objection
(`coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md`),
and — to check claims that rest on code, not just on reported numbers —
`stage_a.py` (`_t_shard`, `CTRStream`, `decode_blocks`, `hist_of`,
`batch_hists`, `evaluable_k`) and `matched_pair.py`'s own jackknife
implementation directly, sha256-pinned, read-only. This is an independent
session; I did not continue the producing agent's session and have not read
the concurrent Validator's report before writing this one.

I confirm the pre-registered rule fired exactly as frozen, with no post-hoc
reframing. I do **not** contest that outcome. But I contest the report's
implicit single-cause framing of *why* the exponent check tripped, and I
name a concrete, free, missing empirical control that the design's own
"zero new entropy" claim should have carried and did not.

---

## 1. Was the pre-registered decision rule honoured exactly as frozen?

Yes, on every mechanically-checkable point I could verify against
`DEC-20260809-46e85c`'s literal text.

- **Branch D (invalid/infrastructure):** stage 1's determinism gate
  reproduced `pilot_results.json`'s committed `S_histogram` arrays for the
  original configuration (shard 5000 defected, shard 6000 undefected)
  bit-identically (`matched_pair_results.json.stage_1.determinism_gate.status
  == "PASS"`); D2/D3 are 0 on all 8 arms across both stages; no arm
  truncated. Branch D correctly does not fire.
- **Branch E (sign anomaly):** DEC's definition requires the two stage-1
  shards to disagree in sign **with each individually significant at
  `|z|>=1.96`**. Measured: shard 5000 diff=+0.1018, z=0.814; shard 6000
  diff=+0.0108, z=0.072 — same sign, neither individually significant.
  Branch E correctly does not fire. (I re-derived both `z` values from the
  reported `diff`/`se_paired` pairs myself rather than taking the report's
  arithmetic on faith.)
- **The exponent check, evaluated next, per DEC's own ordering** ("fit the
  matched-pair jackknife SE against trial count... IF IT FALLS OUTSIDE THAT
  BAND, that supersedes branches A/B/C"): I independently refit
  `alpha` from the three reported `(T, SE_paired@k=17)` points —
  `(5000, 0.137502), (10000, 0.096781), (20000, 0.017905)` — via
  `numpy.polyfit(log T, log SE, 1)` and reproduce **alpha = 1.4700**
  (my own recomputation: 1.46996) against the report's 1.4704932987763473,
  a difference attributable only to floating-point/rounding, not to a
  different construction. This is genuinely outside `[0.4, 0.6]`, and DEC's
  text genuinely says this supersedes A/B/C. **The executor's framing on
  this point is correct, not a convenient misreading.**
- **What supersession actually blocked, made concrete:** absent the
  supersession, this batch's own numbers satisfy Branch B's literal
  condition at k=17: `|z| = 0.619 < 1.96` and
  `|diff| + 1.96*SE = 0.01108 + 1.96*0.01791 = 0.04618 < 0.19`. Un-superseded,
  this would have read as a clean, *tight* scoped null — considerably
  tighter than the campaign's own pre-run target of excluding down to
  ~0.135–0.19. **The pre-registered exponent check is doing real,
  consequential work here, and correctly withholds a conclusion that would
  otherwise look decisive.** I credit the design for catching this rather
  than treating the supersession as a formality.
- No branch was structurally unreachable by this design (contra the
  standing concern the handoff asked me to check): the exponent check has
  now actually fired on real, valid (non-infrastructure, non-anomalous)
  data — the first time in this campaign any of this decision rule's
  non-default branches has fired on anything other than a null D/E check.

**Verdict on Q1/Q2:** the rule was applied exactly as frozen; no branch was
reinterpreted, and the supersession clause is exactly what DEC's text says
it is, not an executor-invented escape hatch.

## 2. Does the fired cell mean what the branch narrative says — or does the report under-diagnose it?

This is where I have a substantive, evidence-based objection, though not
one that changes which branch fired.

DEC's rationale (and the executor's report, section 7) treats the
alpha=1.47 result as a single finding: "substantial deviation from
`1/sqrt(T)` scaling over these three points," implying the derivation's
scaling *assumption* is what broke. **I recomputed the local exponent
between each consecutive pair of points and this is not what the data
shows:**

| step | T | ratio SE(T2)/SE(T1) | local exponent |
|---|---|---|---|
| 5,000 → 10,000 (same shards 5000/6000, pooled) | ×2 | 0.7039 | **0.5067** |
| 10,000 → 20,000 (fresh shards 8001/8002 introduced) | ×2 | 0.1850 | **2.4344** |

The first doubling — using the pilot's own already-committed shards,
exactly the zero-new-entropy step this batch exists to validate — is
almost exactly consistent with `1/sqrt(T)` (local exponent 0.507 against a
target of 0.5). **100% of the deviation driving `alpha=1.47` is
concentrated in the single transition to the fresh shards 8001/8002.** A
three-point OLS fit across a step-function anomaly reports an "average"
exponent that describes neither regime. This matters for what gets written
into the KN-TECH entry the ledger archive is obligated to file: "the
`1/sqrt(T)` modeling assumption is refuted" is a coarser and more alarming
diagnosis than what was actually measured, which is "the estimator behaves
as expected within a fixed shard pool and collapses on a specific pair of
fresh shards." Those imply different next actions — the first says "the
derivation is unsound in general"; the second says "trial-count and
shard-identity are confounded in this 3-point design and need to be
separated."

**A second, corroborating fact the report doesn't surface:** the
"~0.140 expected" pre-run figure that stage 1's 0.0968 is compared against
(design.md §2, DEC's rationale) was extrapolated from the Red Team's
*external, single-shard* Probe 2 (shard 424242, SE=0.1982 at T=5,000,
`BATCH-2ecaa1/reviews/TASK-20260806-92aecb`), not from this task's own
data. This task's own two shards' individually-measured SEs at the *same*
T=5,000 are 0.1251 (shard 5000) and 0.1499 (shard 6000) — already 24-37%
below the Red Team's probe, using the identical jackknife construction. Once
the pooled figure is checked against the *correct*, within-task baseline
(mean 0.137502, exactly the value the report itself uses as the T=5,000
point in its own exponent fit) rather than the external one, the "surprise"
at T=10,000 evaporates: 0.137502/√2 = 0.09724, essentially identical to the
measured 0.096781. **The genuinely anomalous number is not stage 1's pooled
SE (0.0968) — it is stage 2's (0.0179).** The report's §7 anomaly note
conflates these two by presenting both as instances of "deviation from
1/sqrt(T)," when only one of them actually is one.

**Required control, cheap, for the next scaling-characterization task DEC
already calls for:** re-run the *same* trial-count sweep **holding shard
identity fixed** (e.g., shards 5000/6000 or 8001/8002 alone, at
T ∈ {5,000, 10,000, 20,000, 40,000} via new, disjoint trial ranges on the
same shard) so that a genuine T-scaling exponent can be estimated without
shard identity as a confound. As currently designed, the 3-point fit cannot
distinguish "the SE-vs-T law is wrong" from "the estimator's true variance
is highly shard-dependent and two more shards were drawn from a
long/heavy-tailed region of that dependence."

## 3. Is "zero new entropy" verified, or only argued?

I checked this against `stage_a.py` directly rather than taking the design
document's claim on faith. `_t_shard`'s only randomness source is
`CTRStream(sha_key(ps_id, "T", shard, MASTER_SEED), ...)`, re-instantiated
**per trial** and keyed only by `(ps_id, shard, MASTER_SEED, local trial
index, vector tag)` — with no dependency on `decode_blocks`, on `n_trials`,
on batch size, or on call history (including the discarded 300-trial
warmup, which reuses local indices 0..299 and is thrown away). This makes
the code-level claim **correct**: two separate `_t_shard` calls on the same
shard, with different `decode_blocks` installed, do generate bit-identical
`bits` arrays per trial index. I found no bug in this mechanism.

But the handoff's own must_attack item is still live: **the CROSSED arms
have no empirical (only code-level) verification.** The only runtime check
against a committed reference is the determinism gate, and it covers *only*
the two GATE arms (shard 5000 defected, shard 6000 undefected) against
`pilot_results.json`. The two CROSSED arms (shard 5000 undefected, shard
6000 defected) — half of every reconstructed pair — are validated by
argument about `CTRStream`'s key derivation, never by a runtime assertion.

**A free, decisive, and currently-missing control:** `decode_blocks`
reshapes `bits` to `(B, n_e, n_2)` and computes `F`/`W` **per block
independently** (§`wht128` operates per-row on the reshaped `(-1,128)`
array; no cross-block mixing anywhere in the function). The V3 defect only
overwrites the *last* block's window
(`bits_defected[:, lo:hi] = bits[:, lo-1:hi-1]`, `lo=(n_e-1)*n_2`). It
follows structurally that `F[:, 0:n_e-1]` must be bit-identical between the
defected and undefected decode of the *same* trial on the *same* shard.
`matched_pair.py` never checks this — it retains only `S = F.sum(axis=1)`
per trial (`matched_pair_results.json.stage_1.per_trial_S`), which is a
lossy projection that cannot distinguish "genuinely paired, only the last
block ever differs" from "something perturbed more than the last block but
happened to preserve the row sum." Comparing `F[:, :n_e-1]` element-wise
between the GATE and CROSSED arm of each shard costs nothing beyond an
array `.all()` call already available from data the script already
computes, and is the actual, decisive empirical test of "zero new entropy"
for the crossed arms that the code-level argument alone does not supply. I
recommend this as the specific, named, cheapest control for the next task
in this line.

## 4. Is pooling two shards into one estimator call legitimate for a nonlinear statistic?

Not verified either way in this artifact set — flagged as an open
methodological question, not a finding of bias. `log2_A_from_hists` is a
nonlinear function of histogram counts (log-ratio of a combinatorial
moment to `q^k`); the pooling rule concatenates raw histograms
(`H_pooled = H_5000 + H_6000`, `B_pooled = concat(B_5000, B_6000)`) rather
than combining the two shards' own point estimates by inverse-variance
weighting. For two shards with materially different point estimates —
stage 1's own shards disagree by roughly 10x at k=17 (+0.1018 vs +0.0108,
though both are within ~1 SE of each other and of zero, so this specific
gap is not itself distinguishable from noise) — a Jensen-type discrepancy
between "pool-then-estimate" and "estimate-then-average" is plausible in
principle for this class of estimator and is not tested here. **Required
control:** report both the concatenated-histogram pooled estimate (as
currently done) and an inverse-variance-weighted average of the two shards'
own point estimates side by side; a material difference between the two
would mean the pooling convention itself needs to be pre-registered and
justified rather than assumed.

## 5. Reproducing or refuting the 2.78x unpaired/paired SE ratio at k=17

Neither cleanly, and the honest characterization is scale-dependent, which
I recommend the ledger archive record precisely rather than forcing into
DEC's binary "consistent"/"materially inconsistent" release condition.

| source | shard(s) | T | ratio (unpaired/paired) |
|---|---|---|---|
| Red Team Probe 2 (`BATCH-2ecaa1`) | 424242 | 5,000 | 2.78x |
| this task, shard 5000 | 5000 | 5,000 | 2.90x |
| this task, shard 6000 | 6000 | 5,000 | 3.22x |
| this task, stage 1 pooled | 5000+6000 | 10,000 | 3.15x |
| this task, shard 8001 | 8001 | 10,000 | 16.40x |
| this task, shard 8002 | 8002 | 10,000 | 9.81x |
| this task, stage 2 pooled | 8001+8002 | 20,000 | 15.51x |

At near-identical scale and on shards drawn from the same generative
process as the original probe, the ratio **replicates reasonably well**
(2.78x vs. 2.90-3.22x, a 4-16% relative gap — plausible sampling variation
for a ratio-of-jackknife-SDs statistic built from only 200 pseudo-values).
At the fresh, larger-T shards it does **not** replicate — it is 3.5x-5.9x
too large, tracking the same anomaly as §2. **This is neither a clean
replication nor a clean refutation; it is evidence the ratio is not a
scale-invariant design constant**, which is itself the more informative
finding and should be filed as such rather than collapsed into either of
DEC's two pre-declared knowledge-promotion bins.

## 6. Stage 2's trial count (T2=20,000): formula and disclosure

I recomputed the substitution independently:
`T2_raw = 10000 * (0.09678123828590589 * 2.80 / 0.20)^2 = 18358.55`,
round → 18,359, `clamp(18359, 20000, 60000) = 20000`. This matches the
report exactly and the formula was applied correctly. One point the report
states but does not emphasize: the raw computed value (18,359) missed the
pre-registered floor by only ~8.2% — a close call, not a wide margin — so
whether the floor bound at all was sensitive to the precision of stage 1's
own (already-anomalously-tight) SE estimate. More consequential and
**not stated anywhere in the report**: design.md's own stated expectation
("at T2 of order 3.9e4 the SE is expected around 0.069") was calibrated to
the *old*, larger baseline SE (0.1982); the realized T2 (20,000, the floor)
ended up roughly half that anticipated size, yet still achieved an SE
(0.0179) roughly 4x *tighter* than what even the larger, anticipated T2 was
expected to produce. That a *smaller-than-planned* sample size
overshot precision expectations calibrated to a *larger* sample size is
itself a restatement of the §2 anomaly, and is exactly the pattern that
should make a reader distrust the floor-driven "genuinely tight null"
reading even before the alpha-supersession clause is invoked.

## 7. Standing objection: has this pipeline ever produced a fired detection?

**No, and the report does not claim otherwise.** Branch A requires
`|z| >= 1.96`; stage 2's z at k=17 is 0.619. My BATCH-2ecaa1 objection ("in
six [now seven] batches this detection chain has never once produced a
fired cell from a known-present real-sampler defect") is **not retired** by
this batch. This is stated plainly per the handoff's requirement, not as a
rhetorical flourish: whatever else this batch established about the
matched-pair design's mechanics, it has not yet demonstrated the pipeline
can ring on a defect it is known to contain.

## 8. Scope

This is a toy-scale, PS-R3-only, single-defect-class (V3),
single-injection-point measurement. I make no claim here about HQC's
IND-CCA security, its decoding-failure rate, assumption A17/A5, or any
standardized parameter set, and I did not find any such claim latent in the
executor's artifacts — `matched_pair_report.md` and `run_manifest.yaml`
both state the scope boundary correctly and repeatedly. Pollard-rho/BSGS
baseline comparison is not applicable to this HQC decode-path instrument
task; the relevant baseline is the campaign's own between-shard design
(whose power deficit this line of work exists to correct) and the
unauthorized full `T_req≈3.09e5` run, neither of which this batch's cost
(28.1 measured wall-seconds against an 1,800 s budget) comes close to
requiring a revised comparison against.

---

```yaml
red_team_report:
  id: RT-20260809-47a5ec
  task_id: TASK-20260809-47a5ec
  claim_under_review: >-
    matched_pair_report.md (TASK-20260809-a79e4f, snapshot
    6a7a9dd53b3e2c9641a91dbd0f1c187566868ca8) reports a fitted SE-vs-trial-count
    exponent alpha=1.470 at k=m=17, outside the pre-registered [0.4,0.6]
    consistency band, and states this "supersedes branches A/B/C" of
    DEC-20260809-46e85c's pre-registered decision rule per that decision's own
    text, without itself applying the rule or drawing further conclusions.
  objections:
    - "The report and DEC's rationale frame alpha=1.47 as a single,
      undifferentiated 'deviation from 1/sqrt(T) scaling over these three
      points.' Independently recomputing the LOCAL exponent between each
      consecutive pair shows this is wrong as a diagnosis, though not as a
      mechanical trigger: the 5,000->10,000 step (same shards 5000/6000,
      pooled) gives local exponent 0.507, essentially exact 1/sqrt(T)
      consistency; the 10,000->20,000 step (switching to fresh shards
      8001/8002) gives local exponent 2.434. 100% of the anomaly is
      concentrated in the shard-switch step. A 3-point OLS fit across this
      step-function reports an average that describes neither regime, and
      risks the KN-TECH entry recording 'the 1/sqrt(T) assumption is
      refuted' when the more precise and better-supported statement is
      'trial count and shard identity are confounded in this design, and
      the collapse is localized to two specific fresh shards.'"
    - "The '~0.140 expected' figure that stage 1's pooled SE (0.0968) is
      compared against in design.md/DEC's rationale was extrapolated from
      an EXTERNAL, single-shard probe (Red Team Probe 2, shard 424242, SE
      0.1982 at T=5,000), not from this task's own shards. This task's own
      two shards individually measure SE=0.1251 and 0.1499 at the same
      T=5,000 -- already 24-37% below the external probe under an identical
      jackknife construction. Using the correct within-task baseline, stage
      1's pooled SE (0.0968) is almost exactly what 1/sqrt(T) predicts
      (0.137502/sqrt(2)=0.0972). The report's section 7 anomaly note
      presents stage 1's SE and stage 2's SE as two instances of the same
      phenomenon; only stage 2's is actually anomalous."
    - "The determinism/'zero new entropy' claim is verified only by
      code-level argument (CTRStream is keyed per-trial by shard+index,
      independent of decode_blocks or call history -- confirmed correct by
      direct inspection of stage_a.py) and by the determinism gate, which
      covers ONLY the two GATE arms against pilot_results.json. The two
      CROSSED arms -- half of every reconstructed pair -- have no runtime,
      empirical check against any reference, exactly as the handoff's own
      must_attack item warned. A free, decisive, structural check
      (F[:, 0:n_e-1] must be bit-identical between the defected and
      undefected decode of a given trial, since decode_blocks operates
      per-block independently and V3 only touches the last block) was never
      run, despite costing nothing beyond data the script already computes."
    - "Pooling two shards by concatenating raw histograms
      (H_pooled = H_5000 + H_6000) rather than by inverse-variance-weighting
      the two shards' own point estimates is unjustified for a nonlinear
      estimator (log2_A_from_hists) and untested for bias; not shown to
      matter here, but not ruled out either."
    - "matched_pair_report.md does not state that stage 2's realized T2
      (20,000, the pre-registered floor) is roughly half of design.md's own
      stated pre-run anticipation (~3.9e4), yet achieved an SE about 4x
      tighter than what even that larger anticipated T2 was expected to
      produce -- a restatement of the same anomaly as the exponent finding,
      omitted from the report's own framing of what the floor-bound
      outcome means."
  required_controls:
    - "Empirical (not code-argument-only) verification of zero-new-entropy
      pairing: assert F[:, 0:n_e-1] bit-identical between the GATE and
      CROSSED arm of each stage-1 shard, and between the two decode variants
      of each stage-2 shard. Free given data already computed."
    - "A within-shard trial-count sweep (same shard identity, T stepped
      across at least 3-4 values via disjoint trial ranges) to separate
      genuine T-scaling from shard-to-shard heterogeneity, which the current
      3-point fit cannot do because every point uses a different shard set."
    - "Report both pooling conventions (concatenated-histogram vs.
      inverse-variance-weighted point-estimate average) side by side for the
      pooled cells, to check whether the nonlinear estimator's pooling
      choice materially affects the point estimate or SE."
    - "Report, per k, the count/fraction of the 200 (or pooled 400)
      leave-one-batch-out jackknife replicates that are non-finite (NaN) at
      each stage, given jack_se's use of np.nanmean/np.nansum combined with
      a fixed normalizer b=vals.shape[0] rather than the count of finite
      replicates -- a latent bias risk at high k (where evaluable_k's own
      30-trial-per-arm floor means individual batches can be sparse) that is
      currently invisible in the aggregated output."
  counterexample_or_mutation: >-
    Cheapest discriminating experiment: re-run stage 2's exact protocol on
    shards 5000/6000 themselves at T=20,000 (new, disjoint trial ranges from
    the ones already used, still zero-new-entropy relative to nothing
    committed at that T, i.e. genuinely new sampling on already-familiar
    shards) instead of on fresh shards 8001/8002. If the resulting paired SE
    at k=17 tracks 1/sqrt(T) from the existing 5,000/10,000 points (i.e.
    lands near 0.068-0.070), the anomaly is a property of shards 8001/8002
    specifically, not of trial count in general, and the KN-TECH lesson
    should say so. If it instead collapses the same way stage 2 did, the
    1/sqrt(T) refutation is real and general, not shard-specific -- and the
    scaling-characterization task DEC's next_actions already calls for
    should be designed around this exact comparison as its first step.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense (this is an HQC
    decode-path instrument measurement, not an ECDLP claim). The relevant
    specialized baseline is the campaign's own between-shard design, whose
    documented 2.8x-10.6x power deficit (BATCH-2ecaa1 red-team report) this
    whole line of work exists to correct, and the unauthorized full
    T_req~3.09e5-trial run, which this batch's 28.1 measured wall-seconds
    (well inside its 1,800 s / 400 core-second authorization) does not
    approach and does not license.
  heuristic_challenges: []
  cost_model_challenges:
    - "Budget and spend are honestly reported and measured, not modeled
      (28.517 core-seconds / 28.099 wall-seconds against 400/1,800
      authorized, both stages). No objection to the cost accounting itself."
    - "design.md's own pre-run anticipation that T2 would land 'of order
      3.9e4' (based on the OLD external SE baseline) versus the realized
      T2=20,000 (the floor) is a roughly 2x miss in the sizing rule's own
      prior expectation. Not a budget problem (both are cheap), but worth
      recording as a second, independent signal that the pre-run SE model
      used to write design.md was already miscalibrated against this task's
      own shards before stage 1 ran."
  reduction_and_scope_challenges:
    - "Claim tier correctly stays TOY throughout both matched_pair_report.md
      and run_manifest.yaml; PS-R3-only, V3-only, decode_blocks-only scope
      is stated repeatedly and accurately. I found no HQC-security,
      decoding-failure-rate, A17/A5, or standardized-parameter-set claim
      latent anywhere in the executor's artifacts."
    - "H-HQC-18d1b4 is correctly left untouched by this batch's own
      artifacts (the executor does not apply DEC's decision rule, as
      instructed); any movement of that hypothesis is the ledger archive
      task's responsibility, not this task's, and is outside what I am
      reviewing here."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    DEC-20260809-46e85c's pre-registered decision rule was applied exactly
    as frozen: branches D and E correctly did not fire, the fitted exponent
    (alpha=1.4700, independently reproduced) correctly falls outside
    [0.4,0.6] and correctly supersedes branches A/B/C per DEC's own text,
    and the executor correctly reported this without applying the rule
    itself. No branch was reinterpreted or made unreachable by construction.
    However, the anomaly the exponent captures is NOT a uniform deviation
    from 1/sqrt(T) scaling across all three measured points: the
    5,000->10,000 step (same shards, pooled) is consistent with 1/sqrt(T)
    to within measurement noise (local exponent 0.507); the entire anomaly
    is concentrated in the 10,000->20,000 step, which simultaneously
    introduces two new shards -- a confound the current 3-point,
    different-shards-per-point design cannot resolve. The 2.78x
    unpaired/paired SE ratio replicates acceptably (2.9-3.2x) at matched
    scale/shard-similarity to the original probe and does not replicate
    (9.8-16.4x) at the fresh, larger-T shards, which is itself evidence
    the ratio is not a stable design constant, not a clean confirmation or
    refutation of the original figure. The "zero new entropy" pairing claim
    is correct by code-level analysis of stage_a.py's CTRStream but remains
    empirically unverified for the crossed arms specifically, via a free
    check the script does not run. Branch A has still never fired in this
    campaign; my standing objection from BATCH-2ecaa1 is not retired.
  next_concrete_action: >-
    Before writing the KN-TECH entry DEC-20260809-46e85c's knowledge_promotion
    release condition requires: run the counterexample above (a T=20,000
    matched-pair extension on shards 5000/6000 themselves, new trial ranges,
    rather than fresh shards) to determine whether the alpha=1.47 anomaly is
    shard-specific or a general property of this design, and add the free
    F[:, 0:n_e-1] bit-identity check between decode variants of the same
    trial as a standing invariant in this task family going forward. File
    the KN-TECH entry as neither "replicates cleanly" nor "materially
    inconsistent" but as the more precise finding actually supported: the
    unpaired/paired SE ratio and the SE-vs-T scaling both hold within a
    fixed shard pool and both break down on shard extension, which is a
    genuinely different and more useful lesson than either of DEC's two
    pre-declared bins captures.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/stdout.log
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/stderr.log
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/archives/TASK-20260809-a87710/snapshot-receipt.json
    - ledger/decisions/DEC-20260809-46e85c.yaml
    - ledger/goals/GOAL-HQC-001.yaml
    - ledger/evidence/EV-HQC-dd85c1.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_results.json
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement,
formed by re-deriving the reported arithmetic (the exponent fit, the SE
ratios, the branch conditions) from the committed numbers and by reading
`stage_a.py`'s own PRNG/decode code directly rather than accepting the
design document's characterization of it on faith.*
