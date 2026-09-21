# RT-BATCH-010 — Red Team review of RUN-SSIQ-a85692-g (EXP-SSIQ-a85692 v7),
# GOAL-SSIQ-001 BATCH-010 (formalizing the delta_E label-permutation null
# control into a 1000-trials/prime archived record)

**Reviews the Coordinator-committed snapshot at `4fd1425a` (parent `6bdaecb8`,
the frozen `specification_v7.yaml`), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/archives/TASK-20260806-9ad6b5-receipt.yaml`,
covering `RUN-SSIQ-a85692-g`.** Per this task's operating rules, only this
Coordinator-committed snapshot is treated as durable input. This report
changes nothing under `experiments/EXP-SSIQ-a85692/` or any ledger record;
every check below was read-only against the committed tree. Runs in parallel
with an independent Validator (TASK-20260806-08f905, artifact/hash
integrity) — no coordination with it per this task's instruction; this
report is the adversarial-interpretation pass, not a second integrity check.

Read in full: `specification_v7.yaml` (all PF-1..PF-10 fix text, both
pre-freeze rounds' verdicts, and PF-6's exact deferred-control text);
`RT-PREFREEZE-EXP-SSIQ-a85692-v7.md` and `-round2.md`; `RT-BATCH-009.md`
(the prior Red Team's informal 30-trial control); `RUN-SSIQ-a85692-g`'s full
package (`execution_report.yaml`, `manifest.yaml`,
`permutation_null_control.json`'s `objective_boundary` field directly, not
merely the spec's prose about it); `DEC-20260806-498531.yaml` (BATCH-009's
closing decision, D-2's own framing of ANOM-1); `agents/red-team.md`.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified this session.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. Every credentialed
    backend under this environment has previously been found unprobeable in
    this campaign's prior reviews, recorded as the standing condition, not
    re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Shares a model family
    with the Executor, the Coordinator, and every prior reviewer in this
    lineage, including the two v7 pre-freeze rounds and my own prior
    RT-BATCH-009 review. Does not upgrade the campaign's evidence tier and
    does not itself satisfy or advance a closure quorum. A Validator
    (TASK-20260806-08f905) is reviewing the same run independently and in
    parallel, for artifact/hash integrity; produced without coordinating
    with it, per this task's explicit instruction.
```

---

## Bottom line up front

**The formalized 1000-trial run genuinely strengthens the BATCH-009 informal
finding — the means converge tightly and the larger sample locates the
null distribution's tail more precisely than either 15- or 30-trial run
could — but this is a strengthening of confidence in the *existence* of the
signal, not of what the signal *means*, and one concrete overclaim risk
already exists in the record this batch will be cited alongside.** PF-6's
own named confound (delta_E-computation-procedure artifact vs. genuine
graph-spatial structure) is correctly and explicitly carried in
`specification_v7.yaml`'s prose and in the run's own `ANOM-1-CONTEXT`
disclaimer — but it is **not** echoed anywhere machine-readers are most
likely to check first: not in `permutation_null_control.json`'s own
`objective_boundary` field (a generic toy-scale/no-new-claim statement, no
mention of the procedure confound), not in `manifest.yaml`, not in the
Coordinator's own commit message, and not in the receipt's
`null_trial_results_reported` check. Meanwhile, the still-live
`DEC-20260806-498531` (D-2) already states, at `confidence: high`, that this
control "establishes genuine spatial autocorrelation of delta_E along graph
edges as a new, previously unrecorded structural fact" — language that, read
literally, already outruns what any permutation-only control can support,
and predates PF-6 (raised only during v7's pre-freeze review). The coming
`EV-SSIQ-*`/`DEC-*` for this batch must not simply extend D-2's wording
without now attaching PF-6's caveat explicitly.

1. **The formal result is not merely a bigger version of the same thing —
   it adds real information, in two ways.** First, precision: the 1000-trial
   means (58.2%, 37.4%, 36.3%, 45.5%) sit within 0.4–1.1 percentage points of
   both the informal 30-trial means (57.1%, 37.8%, 35.3%, 46.5%) and the
   Coordinator's own 15-trial reproduction (57.9% for p=2437, per the
   receipt) — at N=1000 the standard error of each mean is roughly
   0.15–0.2 points (population SD 3.9–6.1 points, ÷√1000), so this
   convergence is a genuine confirmation that the informal small-sample
   means were not lucky draws, not just a coincidence of larger-N asymptotic
   regression to the same number. Second, the tail: the formal run's
   observed maxima (76.9%, 54.1%, 51.3%, 59.1%) are *higher* than the
   informal 30-trial ranges' own maxima (67.9%, 52.0%, 45.2%, 51.5%) — as
   expected, since a bigger sample explores further into the distribution's
   tail — and this is the one genuinely new fact the larger trial count
   supplies: it pins down, for the first time, how close a random permutation
   can plausibly get to the real data's 100%, which the 15/30-trial runs
   were underpowered to measure. On p=2437 specifically, the null control's
   closest approach (76.9%) is only 23.1 points below the real value — the
   tightest margin of the four primes, and worth naming explicitly rather
   than folding into an undifferentiated "far below 100%" claim.

2. **`NULL_EXCEEDS_OR_EQUALS_REAL_COUNT == 0` on all four primes (0/4000
   total) is a genuinely strong statement, correctly reported, but its
   strength should be read off the max-vs-100% gap, not the bare zero.**
   The zero count by itself only says "no permutation trial reached the real
   value in this specific sample of 1000"; a null count of exactly 0 out of
   1000 is compatible with a one-sided permutation p-value anywhere from 0
   up to roughly 1/1001 (the granularity floor at this N), and cannot by
   itself distinguish "structurally impossible" from "possible but very
   rare." What actually carries the evidentiary weight is the *margin*:
   every prime's observed maximum sits 20.9–48.7 percentage points below
   100% (p=7333: 59.1%→40.9pt gap; p=3889: 54.1%→45.9pt gap; p=5737:
   51.3%→48.7pt gap; p=2437: 76.9%→23.1pt gap), each roughly 3–4 population
   standard deviations above that prime's own null mean (e.g. p=2437's
   76.9% max is (76.9−58.2)/6.14 ≈ 3.05 SD above its own mean) — a
   magnitude consistent with, not surprising relative to, ordinary extreme-value
   statistics for n=1000 draws from a well-behaved bounded distribution, which
   is itself informative: it suggests the null distribution's tail is not
   obviously heavy enough to make a near-miss at higher N plausible, though
   this is a plausibility read from four single per-prime samples, not a
   proven tail bound. `specification_v7.yaml`'s own PF-5 fix correctly
   pre-empts reading `0/1000` as a formal significance result against a
   pre-registered alpha (none stated) — this review adds only that the
   *headline* of the coming citation should foreground the margin, not the
   bare zero, since "zero out of a thousand" reads more dramatically in
   isolation than the actual (still comfortable, but not enormous on
   p=2437) gap it represents.

3. **PF-6's confound is correctly named as deferred in the frozen spec and
   correctly left unaddressed by this run's own results — but it is
   inconsistently propagated across this batch's own artifact stack, which
   is itself a concrete overclaim risk.** `specification_v7.yaml`'s
   `OBJECTIVE_BOUNDARY` states PF-6 in full (the control "by construction
   CANNOT distinguish genuine near-Lipschitz smooth-isogeny-degree structure
   from an artifact of the delta_E-computation PROCEDURE," naming
   `compute_delta_e.py`'s shared, sequentially-advancing per-prime RNG under
   a shrinking per-vertex time budget in sorted-tuple order). The run's own
   `execution_report.yaml` `ANOM-1-CONTEXT` observation correctly declines
   to draw a mechanism conclusion ("draws no conclusion... about WHY the
   real depth==0 degeneracy is universal"). But I checked
   `permutation_null_control.json`'s own `objective_boundary` field
   directly (the field most likely to be read or grepped by a future
   citation, since it lives inside the archived result, not the spec
   prose) and it is a **generic** boundary statement — "does not itself
   constitute a new claim... does not resolve the funnel-structure mechanism
   question... Scale: toy... no result transfers to cryptographic scale" —
   with **no mention of PF-6 or the procedure-vs-structure confound at all**.
   Neither `manifest.yaml`, the Executor's `validity_reason`, nor the
   Coordinator's commit message or receipt cross-checks mention PF-6 either.
   A future reader who consults only the archived JSON result (rather than
   the full frozen spec text) would have no way to learn that this control
   cannot rule out a search-procedure artifact.

4. **This is not a hypothetical risk — the current standing decision record
   already uses language PF-6 should qualify.** `DEC-20260806-498531`
   (BATCH-009's close) states, at `confidence: high`: ANOM-1 "establishes
   genuine spatial autocorrelation of delta_E along graph edges as a new,
   previously unrecorded structural fact about this labelling scheme." That
   decision predates PF-6 (first raised in this batch's own v7 pre-freeze
   review), so it is not itself a defect in that record — but the coming
   `EV-SSIQ-*`/`DEC-*` covering this batch cites and extends that lineage,
   and must not repeat "genuine... structural fact" without now attaching
   PF-6's caveat explicitly: what the 1000-trial control adds is confidence
   that the pattern is not a coarse-alphabet pigeonhole artifact, not
   confidence that it reflects the underlying mathematics rather than the
   delta_E search's own RNG/budget mechanics.

Given the above, my verdict is **CHALLENGE (narrow)**: the run itself is
executed exactly as the frozen spec requires (confirmed by cross-reading
`execution_report.yaml`'s own diff-list cross-check against the spec's
`required_artifacts_note`, C-REPRO self-report, and the two-part coverage
check), and the 1000-trial formalization is a genuine, non-trivial
strengthening of BATCH-009's informal finding — but the record has one live
overclaim risk (D-2's language) that predates this batch and one structural
gap (PF-6 absent from the machine-readable result artifact) that this
batch's own archival purpose should have closed and did not.

---

## Front 1 — Does 1000 trials meaningfully strengthen the informal 15/30-trial result?

**Yes, on precision and on tail characterization; no, on mechanism — exactly
as the frozen spec's own framing anticipates, and this review confirms both
halves.**

| prime | informal (30 trials) mean | Coordinator's 15-trial mean | formal (1000 trials) mean | formal SD | formal max | gap to 100% |
|---|---|---|---|---|---|---|
| 2437 | 57.1% | 57.9% | 58.2% | 6.14 | 76.9% | 23.1 pt |
| 3889 | 37.8% | — | 37.4% | 5.87 | 54.1% | 45.9 pt |
| 5737 | 35.3% | — | 36.3% | 4.84 | 51.3% | 48.7 pt |
| 7333 | 46.5% | — | 45.5% | 3.92 | 59.1% | 40.9 pt |

The convergence of means to within ~1 point across three independently-run
samples of very different sizes (15, 30, 1000) is meaningful evidence
against a lucky small-sample draw — at N=1000 the standard error of the
mean is roughly a third to a tenth of the SD itself, so this is a
well-estimated population mean, not a noisy point estimate any more. The
tail information (max 76.9%/54.1%/51.3%/59.1%, all *higher* than the
30-trial run's own observed maxima) is the one genuinely new fact: a bigger
sample necessarily samples further into the tail, and this run is the first
to establish, with reasonable confidence, roughly how close a random
permutation of this exact value multiset can plausibly get to the real
data's 100% — informative precisely because it was the thing the 15/30-trial
runs could not measure. What the larger N does **not** do — and the spec is
honest about this — is add anything to the question of mechanism (PF-6);
`ANOM-1-CONTEXT`'s own text is correct that this run's "sole relevant new
contribution is the archived null distribution itself."

## Front 2 — Is `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT == 0` as strong as it sounds?

**Strong, but the strength is in the margin, not the bare zero — see Front 1
table above.** p=2437's 23.1-point gap (the tightest of the four) is
still comfortable, but is meaningfully weaker than p=5737's 48.7-point gap,
and a citation that reports "0/1000 on every prime" without also reporting
the per-prime margin risks reading as uniformly overwhelming evidence when
one prime's margin is roughly half the others'. This is a legibility point
for the coming record, not an objection to the run's own reporting (which
states the exact max/min/SD per prime, correctly, in `OBS-3`).

## Front 3 — Does this batch address, rule in, or rule out PF-6's confound?

**Correctly does none of the three, per its own stated scope — but the
run's own machine-readable artifact (`permutation_null_control.json`) fails
to carry PF-6's specific caveat forward, unlike the frozen spec text and
the execution report's prose.** See bottom-line points 3–4 above. This is
the single concrete, actionable finding of this review: before archiving
this batch's evidence record, the Coordinator should either (a) add PF-6's
specific text (not merely a generic toy-scale boundary) to
`permutation_null_control.json`'s own `objective_boundary` field in a
follow-up disclosure, or (b) ensure the `EV-SSIQ-*` record for this batch
states PF-6 explicitly enough that a reader consulting only the evidence
record (not the full spec text) still learns of the confound. Absent
either, the archived JSON result — the artifact most likely to be quoted or
re-parsed by a future amendment — is silent on the one caveat this entire
batch exists to *not* resolve.

## Front 4 — Scope/overclaim risk for the coming `EV-SSIQ-*`/`DEC-*`

Named concretely, before drafting:

1. **D-2 language reuse risk (see bottom-line point 4).** `DEC-20260806-498531`'s
   "genuine spatial autocorrelation... as a new... structural fact"
   (confidence: high) predates PF-6. The coming decision record must not
   restate this language for the formalized 1000-trial result without
   attaching PF-6's caveat — "control-confirmed against the alphabet-pigeonhole
   null; not yet distinguished from a delta_E-search-procedure artifact" is
   the accurate compound claim, not "genuine structural fact" alone.
2. **`0/4000` should not be cited as a bare number.** Per Front 2, the
   coming record should report per-prime margins (or at minimum flag
   p=2437 as the tightest case), not an undifferentiated "zero out of four
   thousand trials" headline.
3. **This remains orthogonal to `H-SSIQ-36e970`.** Unchanged from
   `RT-BATCH-009`'s Front 4 finding, restated because the risk of
   conflation grows, not shrinks, as this control becomes a "properly
   archived, pre-registered, 1000-trial record" — its formal weight makes it
   *more* likely to be miscited as bearing on the directional-gradient
   question than the informal version was, not less.
4. **The funnel-structure mechanism question (`DEC-20260806-498531` next_action
   item (2)) remains untouched.** This batch explicitly declines (correctly)
   to attempt a new depth operationalization or the B/X-widening test; the
   coming record must not read "the null control is now formally archived"
   as any progress toward that separate, still-open question.

---

## Objections

- **OBJ-1**: None on execution fidelity. `execution_report.yaml`'s own
  `required_artifacts_note_diff_cross_check` is thorough and, spot-checked
  against `specification_v7.yaml`'s text, accurate — the two-part coverage
  assertion, the broadened depth domain (PF-4), the single-per-prime RNG
  instance (PF-7), and the unconditional null-trial computation regardless
  of anomaly (PF-2) are all implemented as specified. No objection to
  `RUN-SSIQ-a85692-g`'s own reported numbers.
- **OBJ-2**: The 1000-trial result is a genuine strengthening of BATCH-009's
  informal finding on precision (tight mean convergence, SEM ~0.15-0.2pt)
  and on tail characterization (new, higher observed maxima than either
  informal run), but adds nothing on mechanism — correctly disclosed by the
  run itself (`ANOM-1-CONTEXT`), and this should be stated with equal
  explicitness in the coming `EV-SSIQ-*` record, not merely inherited from
  the spec's own framing.
- **OBJ-3**: `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT == 0` on every prime is
  correctly reported but should be cited alongside its per-prime margin
  (23.1–48.7 percentage points below 100%, weakest on p=2437), not as an
  undifferentiated "0/4000" headline, to avoid reading a variable-strength
  result as uniformly overwhelming.
- **OBJ-4**: PF-6's confound (delta_E-computation-procedure artifact vs.
  genuine graph-spatial structure) is correctly stated in
  `specification_v7.yaml`'s `OBJECTIVE_BOUNDARY` and correctly left
  unaddressed by this run's own results (per its own `ANOM-1-CONTEXT`), but
  is **not** propagated into `permutation_null_control.json`'s own
  `objective_boundary` field (a generic toy-scale statement only), nor into
  `manifest.yaml`, the receipt, or the Coordinator's commit message. A
  reader consulting only the archived JSON result would not learn of this
  confound. This should be fixed (either in the archived artifact or
  explicitly in the coming `EV-SSIQ-*` text) before the record is cited
  further.
- **OBJ-5**: `DEC-20260806-498531` D-2's existing language ("genuine spatial
  autocorrelation... as a new... structural fact," confidence: high)
  predates PF-6 and should not be extended unqualified to cover this
  batch's formalized result. The coming decision record needs to append
  PF-6's caveat explicitly, not merely cite D-2 by reference.

## Required controls

- PF-6's own named next step (a probe re-run of the delta_E search with
  per-vertex-independent, freshly-seeded RNG, checking whether the
  graph-edge spatial-autocorrelation signal persists) remains the correct,
  cheapest discriminating control for the procedure-vs-structure question —
  unchanged from the v7 pre-freeze review's own finding, restated here as
  still the right next step, not required by this archival amendment.
- Before this batch's `EV-SSIQ-*`/`DEC-*` is drafted: propagate PF-6's
  specific text (not a generic toy-scale boundary) into whatever artifact a
  future citation is most likely to consult first — either
  `permutation_null_control.json`'s own `objective_boundary` field (via a
  disclosed correction, since the run itself is immutable) or the evidence
  record's own limitations block, explicitly, not by reference to a spec
  paragraph a reader may not open.
- Report per-prime margins (max-null-vs-100% gap) alongside the `0/4000`
  headline in the coming record, per Front 2/OBJ-3.

## Counterexample or mutation

The cheapest discriminating control for PF-6 remains unchanged from the
pre-freeze review: recompute delta_E for a probe subset of vertices using
fresh, per-vertex-independent RNG seeds (removing `compute_delta_e.py`'s
shared, sequentially-advancing `rng_search` instance and its shrinking
per-vertex time budget), then re-run this exact permutation-null procedure
against the probe's delta_map. If the graph-edge spatial autocorrelation
signal (real ≈100% depth==0 vs. null ≈35-58%) persists under
per-vertex-independent search RNG, PF-6's confound is ruled out and D-2's
"genuine structural fact" language becomes fully supported; if it weakens
substantially, the current signal is at least partly a search-procedure
artifact. Neither this run nor any prior run in this lineage has performed
this control — it remains open, exactly as PF-6 states.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale statistical-control archival work, `asymptotic_claim: null`
throughout (correctly inherited, unchanged from every prior batch). The
relevant baseline is this campaign's own instrument- and claim-scrutiny
discipline: this review extends RT-BATCH-009's own "trace it, don't trust
it, bring your own control" standard by checking not only the reported
numbers but which artifact PF-6's caveat is (and is not) actually carried
into — the same "a producer's own confidence-building prose is not
automatically load-bearing where a reader will actually look" discipline
this lineage's GD-9/PF-8/PF-9 lineage established.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
finding here implicates a numbered heuristic; this remains a statistical
control archival task with `asymptotic_claim: null`.

## Cost model challenges

No asymptotic-cost claim is made anywhere. Measured wall-clock 4.114s
against a 900s/0.3-CPU-hour budget (`manifest.yaml` timing block), roughly
two orders of magnitude under, confirmed. The 1000-trials/prime scale
(4000 total trials) is correctly derived from RT-BATCH-009's own measured
120-trial/<5s baseline (spec's own `budget.note`); no objection to the cost
model.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears
anywhere in this amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited)
correctly stated and not exceeded. `specification_v7.yaml`'s
`OBJECTIVE_BOUNDARY` correctly states this control "does not itself
constitute a new claim... does not resolve the funnel-structure mechanism
question" — matching `DEC-20260806-498531`'s ranked action item (1)
exactly. The one gap (Front 3/4, OBJ-4/OBJ-5) is not scope inflation within
this run's own artifacts, which stay carefully bounded — it is a
propagation gap between the frozen spec's correct scoping and the archived
result artifact's own (generic) boundary text, plus a live risk that the
prior batch's decision language gets extended without qualification.

## Proof architecture challenges

Not applicable — this remains a direct instrument-level statistical control
archival task, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited
unchanged, attacked and held every prior batch including this one).

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-g` as committed at `4fd1425a`, against
`specification_v7.yaml` frozen at `6bdaecb8`: the run executes exactly as
the frozen spec requires (two-part coverage/graph-rebuild verification
passes on all four primes; `REAL_DEPTH0_FRACTION` = 1.0 on all four primes,
exactly reproducing `RUN-SSIQ-a85692-f`'s ANOM-1 figures; all 4000
permutation trials computed and archived with zero undefined trials;
`NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` = 0/1000 on every prime;
C-REPRO self-reported bit-identical). This formalizes, and materially
strengthens on precision and tail-characterization grounds, BATCH-009's
informal 15/30-trial finding that the real data's universal depth==0
degeneracy is not reproduced by a label-permutation null holding graph and
value-multiset fixed — the formal means converge to within ~1 point of both
informal runs, and the formal run's own observed maxima (76.9% on p=2437,
the tightest case, down to 51.3% on p=5737) newly establish how close a
random permutation can plausibly approach 100%, which the informal runs
were underpowered to measure. This strengthening is about confidence in the
*existence* of the signal, not its *cause*: PF-6's named, deferred confound
(delta_E-computation-procedure artifact vs. genuine near-Lipschitz
graph-spatial structure) remains entirely untested by this batch, correctly
per its own declared zero-new-search-cost scope, and is correctly disclosed
in the frozen spec's prose and the run's own `ANOM-1-CONTEXT` observation —
but is absent from `permutation_null_control.json`'s own `objective_boundary`
field and every other machine-readable artifact in this run's package,
which is a propagation gap that should be closed before this record is
cited further, particularly since `DEC-20260806-498531`'s own
high-confidence "genuine... structural fact" language (predating PF-6)
is the lineage this batch's coming decision record will extend.

## Next concrete action

Coordinator: (1) accept the run's own execution fidelity as clean — no
protocol deviation found, C-REPRO self-reported and consistent with the
frozen spec's every PF-1 through PF-10 fix; (2) when drafting
`EV-SSIQ-*`/`DEC-*` for this batch, explicitly attach PF-6's caveat to any
restatement of ANOM-1's "genuine structural fact" language inherited from
`DEC-20260806-498531` D-2, rather than silently carrying that
high-confidence phrasing forward unqualified; (3) report per-prime margins
(23.1–48.7 percentage-point gaps between each prime's observed null maximum
and the real 100%) alongside the `0/4000` headline, flagging p=2437 as the
tightest case, not an undifferentiated zero; (4) propagate PF-6's specific
text into `permutation_null_control.json`'s own `objective_boundary` field
(via a disclosed correction, since the run itself is immutable) or state it
explicitly enough in the evidence record's own limitations block that a
reader who never opens the frozen spec still learns of the confound; (5)
treat PF-6's own named next control (a probe delta_E re-search with
per-vertex-independent RNG) as the correct next step toward resolving
mechanism, unchanged and still open, not attempted by this batch.

## Overall verdict

**CHALLENGE (narrow).** The run itself is executed cleanly and exactly as
the frozen spec requires; no protocol deviation, execution defect, or
numeric discrepancy was found. The 1000-trial formalization is a genuine,
non-trivial strengthening of BATCH-009's informal finding — tight mean
convergence across three independently-sized samples, plus new tail
information the smaller samples could not supply — not merely a bigger
version of the same result. What this review adds, and what the Coordinator
should not proceed past without incorporating: (a) PF-6's confound is
correctly deferred in the frozen spec's prose but is not propagated into
the run's own machine-readable result artifact, a gap that should be closed
before citation; (b) the standing `DEC-20260806-498531` D-2 language
("genuine... structural fact," confidence: high) predates PF-6 and must not
be extended to this batch's formalized result without PF-6's caveat
attached explicitly; (c) the `0/4000` headline should be cited with its
per-prime margins, not as an undifferentiated zero, since p=2437's margin
(23.1 points) is meaningfully tighter than the other three primes'.

```yaml
red_team_report:
  id: RT-BATCH-010
  task_id: TASK-20260806-497010
  claim_under_review: >-
    Coordinator-committed snapshot 4fd1425a (parent 6bdaecb8, the frozen
    specification_v7.yaml), receipt
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/archives/TASK-20260806-9ad6b5-receipt.yaml,
    covering RUN-SSIQ-a85692-g: formalizes BATCH-009's informal delta_E
    label-permutation null control (30 trials/prime, Red Team; 15
    trials/prime, Coordinator) into a pre-registered, 1000-trials/prime,
    bit-reproducible archived record. Reports the two-part
    coverage/graph-rebuild verification passing on all four primes;
    REAL_DEPTH0_FRACTION = 1.0 on all four primes (95/95, 132/132, 194/194,
    287/287); all 4000 permutation trials completed with
    NULL_EXCEEDS_OR_EQUALS_REAL_COUNT = 0 on every prime; null means 0.582
    (p=2437), 0.374 (p=3889), 0.363 (p=5737), 0.455 (p=7333).
  objections:
    - "OBJ-1: None on execution fidelity. execution_report.yaml's own required_artifacts_note_diff_cross_check is thorough and, spot-checked against specification_v7.yaml's text, accurate -- the two-part coverage assertion (PF-1/PF-8/PF-9), the broadened depth domain (PF-4), the single-per-prime RNG instance (PF-7), and the unconditional null-trial computation regardless of anomaly (PF-2) are all implemented as the frozen spec requires. No objection to RUN-SSIQ-a85692-g's own reported numbers."
    - "OBJ-2: The 1000-trial result is a genuine strengthening of BATCH-009's informal finding on precision (formal means 58.2%/37.4%/36.3%/45.5% converge to within 0.4-1.1 points of both the 30-trial informal means 57.1%/37.8%/35.3%/46.5% and the Coordinator's own 15-trial reproduction 57.9% for p=2437; SEM at N=1000 is ~0.15-0.2 points against population SDs of 3.9-6.1 points) and on tail characterization (new, higher observed maxima -- 76.9%/54.1%/51.3%/59.1% -- than either informal run reached), but adds nothing on mechanism, correctly disclosed by the run itself (ANOM-1-CONTEXT explicitly draws no conclusion about WHY the degeneracy is universal). This dual character (strengthens existence-of-signal confidence, does not touch cause) should be stated with equal explicitness in the coming EV-SSIQ-* record."
    - "OBJ-3: NULL_EXCEEDS_OR_EQUALS_REAL_COUNT == 0 on every prime (0/4000 total) is correctly reported but should be cited alongside its per-prime margin -- the gap between each prime's observed null maximum and the real 100% is 23.1 points (p=2437, the tightest case), 45.9 points (p=3889), 48.7 points (p=5737), and 40.9 points (p=7333) -- not as an undifferentiated '0/4000' headline, since a bare zero out of a thousand is compatible with a one-sided permutation p-value anywhere from 0 up to roughly 1/1001 at this trial count, and the actual evidentiary weight is carried by the margin (roughly 3-4 population SDs above each prime's own null mean), which varies meaningfully across primes."
    - "OBJ-4: PF-6's confound (delta_E-computation-procedure artifact -- compute_delta_e.py's shared, sequentially-advancing per-prime RNG under a shrinking per-vertex time budget in sorted-tuple order -- vs. genuine graph-spatial structure) is correctly stated in specification_v7.yaml's OBJECTIVE_BOUNDARY and correctly left unaddressed by this run's own results (per its own ANOM-1-CONTEXT observation), but is NOT propagated into permutation_null_control.json's own objective_boundary field, which I read directly and found to be a generic toy-scale/no-new-claim statement with no mention of PF-6 or the procedure-vs-structure confound at all. Nor is it mentioned in manifest.yaml, the receipt's null_trial_results_reported check, or the Coordinator's commit message. A reader consulting only the archived JSON result artifact -- the artifact most likely to be quoted or re-parsed by a future amendment -- would have no way to learn of this confound."
    - "OBJ-5: DEC-20260806-498531's own D-2 rationale (confidence: high) already states ANOM-1 'establishes genuine spatial autocorrelation of delta_E along graph edges as a new, previously unrecorded structural fact about this labelling scheme.' That decision predates PF-6 (first raised only during this batch's own v7 pre-freeze review), so it is not itself a defect in that prior record -- but the coming EV-SSIQ-*/DEC-* for this batch extends that lineage and must not restate 'genuine... structural fact' unqualified for the newly-formalized 1000-trial result without PF-6's caveat attached explicitly."
  required_controls:
    - "PF-6's own named next step (a probe re-run of the delta_E search with per-vertex-independent, freshly-seeded RNG -- removing compute_delta_e.py's shared, sequentially-advancing rng_search instance -- checking whether the graph-edge spatial-autocorrelation signal persists) remains the correct, cheapest discriminating control for the procedure-vs-structure question, unchanged from the v7 pre-freeze review's own finding. Not required by this archival amendment; still the correct next step before crediting the signal to genuine mathematics."
    - "Before this batch's EV-SSIQ-*/DEC-* is drafted: propagate PF-6's specific text into whatever artifact a future citation is most likely to consult first -- either permutation_null_control.json's own objective_boundary field (via a disclosed correction, since the run itself is immutable) or the evidence record's own limitations block, explicitly, not solely by reference to a spec paragraph a reader may not open."
    - "Report per-prime margins (max-null-vs-100% gap: 23.1/45.9/48.7/40.9 percentage points) alongside the 0/4000 headline in the coming record, per OBJ-3."
  counterexample_or_mutation: >-
    The cheapest discriminating control for PF-6, unchanged from the
    pre-freeze review: recompute delta_E for a probe subset of vertices
    using fresh, per-vertex-independent RNG seeds (removing
    compute_delta_e.py's shared, sequentially-advancing rng_search instance
    and its shrinking per-vertex time budget), then re-run this exact
    permutation-null procedure against the probe's delta_map. If the
    graph-edge spatial-autocorrelation signal (real ~100% depth==0 vs. null
    ~35-58%) persists under per-vertex-independent search RNG, PF-6's
    confound is ruled out and D-2's "genuine structural fact" language
    becomes fully supported; if it weakens substantially, the current
    signal is at least partly a search-procedure artifact. Neither this run
    nor any prior run in this lineage has performed this control -- it
    remains open, exactly as PF-6 states.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale statistical-control archival work, asymptotic_claim null
    throughout, correctly inherited. The relevant baseline is this
    campaign's own instrument- and claim-scrutiny discipline: this review
    extends RT-BATCH-009's own "trace it, don't trust it, bring your own
    control" standard by checking which specific artifact PF-6's caveat is,
    and is not, actually carried into -- the same "a producer's own
    confidence-building prose is not automatically load-bearing where a
    reader will actually look" discipline this lineage's GD-9/PF-8/PF-9
    lineage established.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; asymptotic_claim: null throughout."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere. Measured wall-clock 4.114s against a 900s/0.3-CPU-hour budget (manifest.yaml timing block), roughly two orders of magnitude under, confirmed. The 1000-trials/prime scale (4000 total trials) is correctly derived from RT-BATCH-009's own measured 120-trial/<5s baseline; no objection to the cost model."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "specification_v7.yaml's OBJECTIVE_BOUNDARY correctly states this control does not itself constitute a new claim and does not resolve the funnel-structure mechanism question, matching DEC-20260806-498531's ranked action item (1) exactly. The gap found (OBJ-4/OBJ-5) is not scope inflation within this run's own artifacts, which stay carefully bounded -- it is a propagation gap between the frozen spec's correct scoping and the archived result artifact's own generic boundary text, plus a live risk that the prior batch's decision language gets extended without qualification."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level statistical control archival task, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-g as committed at 4fd1425a, against
    specification_v7.yaml frozen at 6bdaecb8: the run executes exactly as
    the frozen spec requires (two-part coverage/graph-rebuild verification
    passes on all four primes; REAL_DEPTH0_FRACTION = 1.0 on all four
    primes, exactly reproducing RUN-SSIQ-a85692-f's ANOM-1 figures; all
    4000 permutation trials computed and archived with zero undefined
    trials; NULL_EXCEEDS_OR_EQUALS_REAL_COUNT = 0/1000 on every prime;
    C-REPRO self-reported bit-identical). This formalizes, and materially
    strengthens on precision and tail-characterization grounds, BATCH-009's
    informal 15/30-trial finding -- formal means converge to within ~1
    point of both informal runs, and newly-observed maxima (76.9% on
    p=2437, the tightest case, down to 51.3% on p=5737) establish how close
    a random permutation can plausibly approach 100%, information the
    informal runs were underpowered to supply. This strengthening is about
    confidence in the signal's EXISTENCE, not its CAUSE: PF-6's named,
    deferred confound (delta_E-computation-procedure artifact vs. genuine
    near-Lipschitz graph-spatial structure) remains entirely untested,
    correctly per this amendment's own declared zero-new-search-cost scope,
    and is correctly disclosed in the frozen spec's prose and the run's own
    ANOM-1-CONTEXT observation -- but is absent from
    permutation_null_control.json's own objective_boundary field and every
    other machine-readable artifact in this run's package, a propagation
    gap that should be closed before this record is cited further,
    particularly since DEC-20260806-498531's own high-confidence
    "genuine... structural fact" language (predating PF-6) is the lineage
    this batch's coming decision record will extend.
  next_concrete_action: >-
    Coordinator: (1) accept the run's own execution fidelity as clean -- no
    protocol deviation found, C-REPRO self-reported and consistent with the
    frozen spec's every PF-1 through PF-10 fix; (2) when drafting
    EV-SSIQ-*/DEC-* for this batch, explicitly attach PF-6's caveat to any
    restatement of ANOM-1's "genuine structural fact" language inherited
    from DEC-20260806-498531 D-2, rather than silently carrying that
    high-confidence phrasing forward unqualified; (3) report per-prime
    margins (23.1-48.7 percentage-point gaps between each prime's observed
    null maximum and the real 100%) alongside the 0/4000 headline, flagging
    p=2437 as the tightest case, not an undifferentiated zero; (4)
    propagate PF-6's specific text into permutation_null_control.json's own
    objective_boundary field (via a disclosed correction, since the run
    itself is immutable) or state it explicitly enough in the evidence
    record's own limitations block that a reader who never opens the frozen
    spec still learns of the confound; (5) treat PF-6's own named next
    control (a probe delta_E re-search with per-vertex-independent RNG) as
    the correct next step toward resolving mechanism, unchanged and still
    open, not attempted by this batch.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-BATCH-010.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph rebuilt, no permutation trial re-executed -- this review is a
    direct read and cross-check of the committed artifacts (not a
    from-scratch statistical re-derivation, unlike RT-BATCH-009's informal
    control run). Read specification_v7.yaml in full including all PF-1
    through PF-10 fix text and both pre-freeze review reports;
    RUN-SSIQ-a85692-g/execution_report.yaml, manifest.yaml, and
    permutation_null_control.json's own objective_boundary field directly
    (via a scratchpad Python json.load, not merely via the spec's own prose
    describing it); DEC-20260806-498531.yaml in full; RT-BATCH-009.md in
    full for the informal 30-trial comparison figures. Computed the
    per-prime null-maximum-to-real-100%-gap arithmetic (23.1/45.9/48.7/40.9
    percentage points) and the approximate SD-multiple of each prime's
    observed maximum above its own null mean directly from the archived
    manifest.yaml result.metrics block, by hand, not from any prior
    report's prose. No file written outside this report; no run artifact,
    specification file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-BATCH-010.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v7.yaml and
    every run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
