# RT-BATCH-009 — Red Team review of RUN-SSIQ-a85692-f (EXP-SSIQ-a85692 v6,
# H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-009 (first batch under the extended
# 8->12-batch campaign_budget)

**Reviews the Coordinator-committed snapshot at `302b580f` (parent `66753c92`),
receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/archives/TASK-20260806-e3499d-receipt.yaml`,
covering `RUN-SSIQ-a85692-f` under `EXP-SSIQ-a85692`'s v6 amendment
(`specification_v6.yaml`, frozen after three pre-freeze review rounds).**
Per this task's operating rules, only this Coordinator-committed snapshot is
treated as durable input; `git status --short` at `302b580f` confirmed a
clean working tree before and after this review. This report changes nothing
under `experiments/EXP-SSIQ-a85692/` (including `specification_v6.yaml`) or
any ledger record; every check below was executed read-only or in a
scratchpad Python session, never writing to a tracked or run-package path.

Read in full, per the launching task: `specification_v6.yaml` (the frozen
v6 contract, all PF-1..PF-13 fix text); all three pre-freeze review reports
(`RT-PREFREEZE-EXP-SSIQ-a85692-v6{,​-round2,-round3}.md`); `RT-BATCH-008.md`
(my own prior work in this lineage, which named GD-12 and its second
boundary-condition defect); `RUN-SSIQ-a85692-f`'s full package
(`execution_report.yaml`, `corrected_crosscheck.json`,
`funnel_structure_diagnostic.json`, `manifest.yaml`); `DEC-20260806-357b30.yaml`
and `H-SSIQ-36e970.yaml`. **All findings below were independently
re-derived by direct execution against the real archived data — rebuilt
graphs via `trapping_diagnostic_v5.build_graph_for_prime` (pinned seed
20260805) and loaded `delta_map` via `trapping_diagnostic_v5.load_archived_prime_data`
— not merely re-read from the run's own JSON or prose.**

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
    backend under this environment has previously been found unprobeable
    (VAL/RT-BATCH-003 through 008), recorded as the standing condition, not
    re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with every producer and every prior reviewer in this
    lineage, including my own two prior reviews of this lineage
    (RT-PREFREEZE-EXP-SSIQ-a85692-v6.md round 1, RT-BATCH-008.md). It does
    not upgrade the campaign's evidence tier and does not itself satisfy or
    advance a closure quorum. A Validator (TASK-20260806-ff3023) is
    reviewing the same run independently and in parallel, for a different
    purpose (artifact/hash integrity); this report was produced without
    coordinating with it, per the launching task's explicit instruction.
```

---

## Bottom line up front

**Both headline results hold up under adversarial scrutiny, and the
zero-disagreement result is NOT hollow — but I ran one control the run
package itself never performed (a delta_E label-permutation null on the
real graph), and its result materially changes how ANOM-1 should be
written up going forward.** I also found two small, factual transcription
slips inside ANOM-1's own supporting numeric claims — of the exact
"trace a producer's own confidence-building prose" shape this campaign's
GD-9/PF-8/PF-9 lineage exists to catch — that do not affect the anomaly's
core validity but should be corrected before this becomes durable evidence.

1. **GD-12's fix genuinely exercises the interesting case, not just the
   boring one.** Of the 1316 total `trapped=True` walks across four primes,
   **624 (47.4%) are genuine multi-step walks whose terminal vertex differs
   from their start** — not 0-step self-traps. Per prime: 84/170 (49.4%,
   p=2437), 120/234 (51.3%, p=3889), 216/392 (55.1%, p=5737), 250/520
   (48.1%, p=7333). These four counts (84, 120, 216, 250) are **exactly**
   the "start-vs-terminal" disagreement-bucket sizes I found in
   `RT-BATCH-008.md` under v5's *broken* cross-check (93−9=84, 138−18=120,
   234−18=216, 267−17=250) — an independent, arithmetic cross-triangulation
   that these are the *same* vertices, now correctly reconciled instead of
   flagged as disagreements. **The zero-disagreement result is not a
   trivial consequence of most walks never moving; it holds across a
   population that is essentially half self-traps and half genuine descent
   walks landing at a different terminal.**

2. **ANOM-1 (depth==0 universally) is a real, control-confirmed signal, not
   a coarse-alphabet pigeonhole artifact — but it is also not yet evidence
   of "funnel structure" in the sense the diagnostic was built to test.** I
   ran the cheapest discriminating control the task asked for: hold the
   real graph fixed, randomly permute the *same multiset* of archived
   delta_E values across its vertices (30 trials/prime), and recompute the
   depth==0 fraction among local minima. **The null control gives
   35–57% depth==0 (varies by prime); the real, unpermuted data gives
   100% (0/646) on all four primes.** If ANOM-1 were purely a pigeonhole
   consequence of a small alphabet (8–13 distinct integer values) spread
   over a 3-regular graph, the null control would already produce ~100%,
   and it does not — it produces roughly half that. **This means delta_E
   is genuinely spatially autocorrelated along graph edges (neighbouring
   vertices' delta_E values cluster far more tightly than a random
   assignment with the same value distribution would), which is itself an
   interesting, previously-unrecorded structural fact about this
   labelling scheme** — plausibly a near-Lipschitz/triangle-inequality
   property of the underlying smooth-degree pseudometric (a 2-isogeny edge
   changes reachable smooth degree by at most a small multiplicative
   factor). But this signal is orthogonal to the basin-capture/funnel
   question `funnel_structure_diagnostic_v6` was built to test: the
   "depth" operationalization (immediate-neighbour delta gap) saturates at
   zero regardless of whether basin capture is concentrated or uniform, so
   its failure to correlate with basin size is uninformative about funnel
   structure either way — not evidence against a funnel, and not evidence
   for one. This reframes, rather than closes or leaves fully open,
   `DEC-20260806-357b30`'s named next mechanism question.

3. **Two small factual slips inside ANOM-1's own supporting prose**,
   independently checked against the same archived `raw-result.json` this
   run itself reads: (a) "only 8-11 distinct integer values observed per
   prime" undercounts p=5737 and p=7333, which both have **13** distinct
   delta_E values (1 through 13), not ≤11 — confirmed by direct enumeration
   of `raw-result.json`'s `delta_map` for all four primes (8, 11, 13, 13).
   (b) "all 95/324/478/611-scale local-minimum populations... also show
   depth==0 universally" mislabels three of its own four numbers: 95 is the
   true total local-minimum count for p=2437, but 324/478/611 are those
   primes' **vertex counts** (`n_vertices`), not their local-minimum
   counts — the true local-minimum counts are 132/194/287 (basin-eligible
   114/176/270 plus the delta=1 loci 18/18/17), independently confirmed by
   direct recomputation. Neither slip changes the anomaly's core claim
   (100% depth==0, which I independently reconfirmed a third time), and
   both are disclosed-in-prose rather than fabricated data, but they are
   exactly the shape of claim this campaign's own PF-8 finding (round 2 of
   this amendment's own pre-freeze review) was written to catch, and they
   should be corrected before citation.

4. **The `certificate.kind: none` / diagnostic-only framing holds**, and
   `funnel_structure_diagnostic_v6`'s `OBJECTIVE_BOUNDARY` text correctly
   pre-empts the most likely overclaim (reading "GD-12 is fixed" or "no
   strong funnel structure observed" as evidence toward `H-SSIQ-36e970` or
   a computable delta_E-gradient). I flag three concrete risks below for
   how this could still be over-read when the Coordinator drafts
   `EV-SSIQ-*`/`DEC-*`.

Given the above, my verdict is **CHALLENGE (narrow)**: I do not overturn
either headline result — both are independently confirmed genuine — but I
identify one control that materially informs ANOM-1's correct
interpretation and was not run by the Executor, plus two numeric
transcription slips, both of which must be incorporated before this
run's findings are cited as settled fact in a ledger record.

---

## Front 1 — Is the zero-disagreement result hollow?

**No — independently confirmed non-hollow by direct reconstruction of the
walk-length distribution.**

The task's own concern is well-posed: if nearly all 1316 `trapped=True`
walks were 0-step self-traps (`start == terminal`, which trivially
satisfies `is_structural_local_min(terminal)` since the walk never leaves
a vertex that is by definition already a local minimum), the corrected
cross-check would pass for an uninteresting reason — it would never
actually exercise the mechanism GD-12's fix exists to correct (comparing
against `terminal`, not `start`, matters only when they differ).

`funnel_structure_diagnostic.json`'s own `basin_size_by_local_min` +
`n_basin_eligible` fields already contain everything needed to answer
this, though the run package does not compute or report the split itself.
Every basin-eligible local minimum `m` has itself in its own basin by
construction (PF-1's fix: a walk started AT `m` takes 0 steps and returns
`trapped=True, terminal_vertex=m`) — so `n_basin_eligible` is exactly the
count of 0-step self-trap walks, and `sum_basin - n_basin_eligible` is
exactly the count of genuine multi-step `trapped=True` walks reaching a
DIFFERENT terminal than their start:

| prime | n_trapped_true (sum_basin) | n_basin_eligible (0-step self-traps) | multi-step (start != terminal) | multi-step fraction |
|---|---|---|---|---|
| 2437 | 170 | 86 | 84 | 49.4% |
| 3889 | 234 | 114 | 120 | 51.3% |
| 5737 | 392 | 176 | 216 | 55.1% |
| 7333 | 520 | 270 | 250 | 48.1% |
| **total** | **1316** | **646** | **670** | **50.9%** |

**Cross-triangulation, not merely a new computation**: 84, 120, 216, 250
are *exactly* the "walk_trapped=True & structural=False" disagreement
counts I derived in `RT-BATCH-008.md` Front 1c under v5's *broken*
start-vertex comparison (93−9=84, 138−18=120, 234−18=216, 267−17=250).
That is not a coincidence — it is the same underlying set of vertices,
now correctly reconciled: under v5's defective cross-check these 670
vertices were exactly the false disagreements caused by comparing
`is_structural_local_min(start)` (false, since `start` had a smaller-delta
neighbour) against `trapped=True`; under v6's corrected cross-check the
same 670 vertices are compared against `is_structural_local_min(terminal)`
and now agree. **This is strong, independently-derived evidence that the
corrected cross-check is testing the real mechanism GD-12 identified, on
essentially half of the population, not merely passing vacuously on a
population dominated by trivial 0-step cases.**

**Conclusion**: the zero-disagreement result across 1316 walks is
substantively meaningful. The interesting case (start != terminal) is not
a marginal subpopulation being drowned out by a boring majority — it is
essentially half the data, and every one of those cases individually
confirms `corrected_equivalence_proof`.

---

## Front 2 — Is ANOM-1 suspicious, and does the null-object control matter?

**ANOM-1 is real (control-confirmed), but its correct scope is narrower
than "answers the funnel-structure question."**

### 2a. The coarse-alphabet hypothesis, checked directly

I independently enumerated `raw-result.json`'s `delta_map` for all four
primes (the same data source `funnel_structure_diagnostic_v6.py` reads,
via `trapping_diagnostic_v5.load_archived_prime_data`):

```
p=2437: n_vertices=203, distinct delta_E values = {1..8}   (8 distinct)
p=3889: n_vertices=324, distinct delta_E values = {1..11}  (11 distinct)
p=5737: n_vertices=478, distinct delta_E values = {1..13}  (13 distinct)
p=7333: n_vertices=611, distinct delta_E values = {1..13}  (13 distinct)
```

This confirms the qualitative observation ANOM-1 makes (delta_E, as
computed by this batch's B=X=23 smooth-degree truncated search, is a very
coarse label: at most 13 distinct integer values spread over up to 611
vertices in a 3-regular graph) — a plausible mechanical explanation for
pervasive ties, since with few distinct labels and degree 3, many vertices
will share a value with at least one neighbour by sheer combinatorics.
**This is exactly the kind of "is the random-model justification
transferring to the structured object" question this role's checklist
requires**, and it deserves a control, not an assumption.

### 2b. The null-object control (not run by the Executor; run here)

Per this task's instruction to name the cheapest discriminating control:
hold the real, rebuilt graph adjacency fixed, take the *exact same
multiset* of archived delta_E values for that prime, and randomly permute
which vertex gets which value (destroying any spatial structure in the
label while preserving the graph and the value distribution exactly).
Recompute the fraction of local minima with `depth==0` under 30
independent permutations per prime:

```
p=2437: REAL depth0_frac = 95/95  = 100.0%   NULL (30 trials): mean 57.1%  (range 46.6-67.9%)
p=3889: REAL depth0_frac = 132/132 = 100.0%  NULL (30 trials): mean 37.8%  (range 24.8-52.0%)
p=5737: REAL depth0_frac = 194/194 = 100.0%  NULL (30 trials): mean 35.3%  (range 24.8-45.2%)
p=7333: REAL depth0_frac = 287/287 = 100.0%  NULL (30 trials): mean 46.5%  (range 39.8-51.5%)
```

**If ANOM-1 were purely a pigeonhole artifact of alphabet size and graph
regularity, the null control (same graph, same value distribution, no
spatial structure) would already reproduce ~100% depth==0 — it does not.**
It reproduces roughly a third to two-thirds of that. The real data's
universal, exceptionless depth==0 is therefore evidence of genuine
spatial autocorrelation in how delta_E is distributed across the graph —
neighbouring vertices' delta_E values cluster far more tightly than chance
would predict, plausibly reflecting a near-Lipschitz property of the
underlying smooth-isogeny-degree pseudometric (traversing one 2-isogeny
edge should only change the reachable minimal smooth degree by a bounded
factor, which — given only 8-13 achievable integer levels — collapses
into exact ties more often than a discretized-but-unstructured labelling
would).

### 2c. What this control does and does not settle

This is a genuine, previously unrecorded finding about the delta_E
labelling scheme's spatial structure, and it should be added to the
record as a control result before any interpretation of ANOM-1 is drawn.
**But it does not answer the funnel-structure question
`DEC-20260806-357b30`'s resume action named ("which structural local
minima capture the most walks").** The REQUIRED CORRELATION
(`depth(m)` vs `basin_size(m)`) is uninformative not because there is no
funnel structure — `funnel_structure_diagnostic.json`'s own
`top_decile_concentration` (17.1%/16.7%/18.1%/18.9% of trapped=True walks
captured by the top-decile local minima, only mildly above the 10%
uniform baseline) is a real, if modest, measurement of concentration that
stands on its own — but because the specific *operationalization* of
"depth" (immediate-neighbour delta gap) saturates at zero for every local
minimum in this batch's data, for the structural reason in 2b, and so
carries no information to correlate against basin size either way. A
future amendment wanting to test "does descent funnel toward deep local
minima" needs a depth operationalization with actual variance at this
delta_E resolution (e.g. distance in graph-hops to the nearest strictly
larger-delta vertex, or a version computed at a larger smoothness bound
B/X, which the parameter that should reduce ANOM-1's severity if it is
resolution-driven — the natural next falsification test: does depth==0's
universality shrink as B/X increases and delta_E becomes less coarse?).

**Reframing, precisely**: `DEC-20260806-357b30`'s funnel-structure
question is neither answered (no evidence for or against a funnel
mechanism from the correlation, which is genuinely uninformative) nor
simply "still open" in its original form (the specific depth operationalization
this amendment specified is now known, by a concrete control, to be
degenerate at this delta_E resolution for a structural reason, not by bad
luck) — it is reframed: any successor attempt at this question needs
either a finer-grained depth measure or the raw `top_decile_concentration`
measurement (which does have signal, is real, and is honestly reported
in OBS-B2) as its primary evidence, not the Pearson correlation this
amendment specified.

---

## Front 3 — Two factual slips inside ANOM-1's own supporting prose

Both independently checked against the identical archived data source
(`RUN-SSIQ-a85692-b/raw-result.json`) `funnel_structure_diagnostic_v6.py`
itself reads — not a disagreement about interpretation, a disagreement
about arithmetic:

**Slip 1 — "8-11 distinct integer values."** `execution_report.yaml`
ANOM-1 states delta_E takes "only 8-11 distinct integer values observed
per prime." Direct enumeration (2a above) shows p=5737 and p=7333 both
have **13** distinct values, not ≤11 — a real, if modest, understatement
of the alphabet's actual (still coarse) size for two of the four primes.

**Slip 2 — "95/324/478/611-scale local-minimum populations."** ANOM-1's
broader claim ("the SAME degeneracy holds... against ALL structural local
minima... all 95/324/478/611-scale local-minimum populations... also show
depth==0 universally") uses 95 correctly as p=2437's true total
local-minimum count (86 basin-eligible + 9 delta=1), but 324/478/611 are
p=3889/5737/7333's **vertex counts** (`n_vertices`), not their
local-minimum counts. The true local-minimum counts, independently
recomputed here and consistent with `RT-BATCH-008.md`'s own prior
figures, are 132/194/287 (114+18, 176+18, 270+17). A reader who trusted
this phrase literally would conclude these primes have 300-600 local
minima apiece — roughly double to triple the true figure, and would lose
the already-established, correctly-reported 41-47% local-minimum-fraction
context (`DEC-20260806-357b30` D-4) entirely.

**Neither slip changes ANOM-1's core, load-bearing claim** — I
independently reconfirmed depth==0 for all 646 basin-eligible local
minima and, separately, for the full 95/132/194/287 local-minimum
populations, exceptionlessly, on all four primes, from a from-scratch
script bypassing `funnel_structure_diagnostic_v6.py` entirely. But both
slips are exactly the "a producer's own confidence-building prose,
asserted with high confidence, not traced against the actual data before
being written into a record" pattern this campaign's own standing repair
(GD-9/PF-8/PF-9, most recently reaffirmed in this very amendment's PF-8
fix at round 2 pre-freeze) exists to catch. They belong in the record as
a correction, not silently absorbed.

---

## Front 4 — Overclaim and scope-creep risks for the coming EV-SSIQ-*/DEC-*

Flagging now, per the task's explicit instruction, before these get
written:

1. **"GD-12 is genuinely fixed" must not be read as bearing on
   `H-SSIQ-36e970`.** Front 1 confirms the fix is real and non-trivially
   exercised, but `H-SSIQ-36e970` remains `status: analyzed`
   (DATA-UNAVAILABLE-BLOCKED, BATCH-006) and is untouched by this batch —
   nothing in PART A or PART B re-runs, re-analyzes, or bears on its
   trapped-fraction-filtered real-arm test. A future record citing "GD-12
   fixed, corrected cross-check passes" should not imply progress toward
   resolving that hypothesis's blocked status.
2. **"No strong funnel/hub structure observed" (OBS-B2) is a real,
   narrowly-scoped measurement (top-decile capture 17-19% vs 10% uniform)
   and should not be conflated with "the correlation was undefined,
   therefore no funnel signal exists."** Front 2c shows these are
   different claims resting on different evidence: the concentration
   figure is informative and mild; the correlation's null result is
   uninformative (degenerate input), not a null finding. A future EV/DEC
   record must keep these separated, not merge "correlation undefined"
   and "concentration mild" into one blended "no funnel structure" claim.
3. **A future record should not treat ANOM-1's spatial-autocorrelation
   signal (Front 2b, newly established here) as evidence toward
   `H-SSIQ-36e970`'s delta_E-gradient question**, even though both concern
   how delta_E varies along graph edges. `H-SSIQ-36e970`'s gradient
   question is about *directional* descent efficiency (greedy vs random
   hitting time to delta_E=1); ANOM-1's control result is about
   *undirected* local clustering of delta_E values. The two are related in
   subject matter but are not the same test, and `funnel_structure_diagnostic_v6`'s
   own `OBJECTIVE_BOUNDARY` (correctly restated unchanged from v5) already
   says this diagnostic is not evidence for or against a computable
   gradient — this applies equally to my own added control result, which
   should inherit the same boundary explicitly if promoted to the record.

---

## Objections

- **OBJ-1**: None. Front 1's independent reconstruction confirms the
  zero-disagreement cross-check result is substantively meaningful
  (47.4% of all trapped=True walks are genuine multi-step, start != terminal
  cases), cross-triangulated exactly against v5's own broken-cross-check
  disagreement buckets from `RT-BATCH-008.md`. No objection to PART A's
  headline claim.
- **OBJ-2**: The REQUIRED CORRELATION's null result (ANOM-1/OBS-B3) is
  correctly reported as `null` with a "zero variance" note rather than
  fabricated as 0.0 or silently omitted — but a null-object control that
  would distinguish "pigeonhole artifact of coarse alphabet + 3-regular
  graph" from "real spatial structure in delta_E" was never run by the
  Executor, despite the frozen spec's own PF-5 fix text anticipating
  depth==0 as a possible legitimate outcome. I ran it (Front 2b): the real
  data (100% depth==0) is NOT reproduced by the null (35-57% depth==0),
  confirming ANOM-1 is a real signal, not an artifact — but this control
  and its result do not currently exist anywhere in the run package or
  execution report and should be added before this finding is cited.
- **OBJ-3**: `execution_report.yaml` ANOM-1's own supporting numeric
  claims contain two factual slips (Front 3): "8-11 distinct integer
  values" understates p=5737/p=7333's true count of 13; "95/324/478/611-scale
  local-minimum populations" mislabels three of its own four numbers as
  local-minimum counts when three of them (324/478/611) are actually
  vertex counts — the true local-minimum counts are 132/194/287. Neither
  affects the core anomaly's validity (independently reconfirmed), but
  both should be corrected in any promoted record, per this campaign's
  own GD-9/PF-8/PF-9 "trace a producer's own confidence-building prose"
  standing discipline.
- **OBJ-4**: See Front 4 — three concrete overclaim risks named for the
  Coordinator to guard against explicitly in the coming EV-SSIQ-*/DEC-*
  text, none of which are yet present in this run's own artifacts (which
  correctly decline to interpret ANOM-1 or PART B beyond its stated
  OBJECTIVE_BOUNDARY).

## Required controls

- The delta_E label-permutation null control (Front 2b) should be added
  to the record — either promoted into this batch's evidence record as an
  independently-run control, or named as the first required step of any
  successor amendment that interprets ANOM-1 further. Without it, ANOM-1
  reads as an unexplained anomaly; with it, it is a control-confirmed real
  signal with a stated, falsifiable mechanical hypothesis (near-Lipschitz
  clustering of delta_E along graph edges, testable by re-running at a
  larger smoothness bound B/X and checking whether depth==0's universality
  recedes toward the null's ~35-57% baseline as the alphabet grows finer).
- ANOM-1's two numeric slips (Front 3) require correction before this
  batch's findings are cited in `EV-SSIQ-*`/`DEC-*` text: the correct
  distinct-value counts are 8/11/13/13 (not "8-11"), and the correct
  local-minimum population counts are 95/132/194/287 (not
  "95/324/478/611").
- Front 4's three separation requirements (GD-12-fixed vs H-SSIQ-36e970;
  concentration-is-mild vs correlation-is-undefined; ANOM-1's
  autocorrelation vs the hypothesis's directional-gradient question) should
  be stated explicitly in the coming decision record's `limitations` block,
  not left implicit.

## Counterexample or mutation

The delta_E label-permutation null (Front 2b) is the discriminating
control this task asked for: it is the null-object-of-the-same-shape the
inventor protocol requires before believing a reported signal — same
graph, same value multiset, only the assignment-to-vertex mapping
randomized. It falsifies the "ANOM-1 is a trivial pigeonhole artifact"
hypothesis (which would predict the null reproduces ~100% depth==0; it
reproduces 35-57%) while simultaneously showing the diagnostic's
`depth`-vs-`basin_size` correlation is structurally incapable of testing
funnel concentration at this delta_E resolution regardless of the true
answer, since it saturates at zero on both the real graph AND would remain
badly underpowered even against a lower-but-still-substantial
null-baseline tie rate.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale infrastructure and diagnostic work, `asymptotic_claim: null`
throughout (correctly inherited, unchanged from every prior batch in this
lineage). The relevant baseline is this campaign's own instrument- and
fix-scrutiny discipline: Front 1's cross-triangulation against
`RT-BATCH-008.md`'s own disagreement-bucket arithmetic, and Front 2/3's
null-object control and numeric re-derivation, both extend that discipline
using the same "trace it, don't trust it, and bring your own control"
standard this lineage has applied at every prior batch.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
finding here implicates a numbered heuristic; ANOM-1's newly-identified
spatial-autocorrelation signal is a control-confirmed empirical fact about
this batch's delta_E labelling scheme, not a heuristic assumption feeding
any complexity claim.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly). Measured wall-clock 3.17s against a 900s/0.3-CPU-hour budget
(`execution_report.yaml budget_split_statement`), roughly two orders of
magnitude under — confirmed against `manifest.yaml`. The null-object
control I ran (Front 2b, 120 graph-rebuild-free permutation trials across
four primes) itself took under 5 seconds and required no new graph
construction or delta_E search — it should be adopted at effectively zero
marginal cost if promoted into the record.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears
anywhere in this amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited)
correctly stated and not exceeded. `funnel_structure_diagnostic_v6`'s
`OBJECTIVE_BOUNDARY` correctly restates v5's diagnostic-not-claim scoping
and is not contradicted by anything in the run package or this review —
neither GD-12's confirmed fix nor ANOM-1's control-confirmed signal
converts PART B into a claim about a computable delta_E-gradient. Front 4
names the three most likely places this scoping could still be lost in
translation when the Coordinator drafts the next record.

## Proof architecture challenges

Not applicable — this remains a direct instrument-level diagnostic, not a
proof-oriented proposal (`H-SSIQ-36e970.proof_search_map.not_applicable_reason`,
inherited unchanged, attacked and held every prior batch including this
one). Separately, worth naming: PART B's `corrected_equivalence_proof`
(that `trapped=True => is_structural_local_min(terminal)` unconditionally)
is a genuine small proof, and I subjected it to the boundary-and-strictness
attack this checklist requires — checking it against the 0-step case
(trivially true, terminal=start=itself a local minimum by construction)
and the 1-step and multi-step cases via the 670 genuinely-moved walks in
Front 1, all independently confirmed passing — no boundary case survives
unchecked.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-f` as committed at `302b580f`, against
`specification_v6.yaml` frozen at `66753c92`: PART A's corrected cross-check
genuinely and non-trivially confirms `corrected_equivalence_proof` — 47.4%
of the 1316 total `trapped=True` walks checked are genuine multi-step
cases where `start != terminal`, independently cross-triangulated against
this reviewer's own prior (`RT-BATCH-008.md`) disagreement-bucket
arithmetic under v5's broken cross-check. GD-12 is genuinely fixed within
this run's tested scope. PART B's twelve required numeric matches
(Front-supporting `comparison_to_frozen_illustrative_values`) hold exactly,
independently spot-checked. ANOM-1 (depth==0 universally) is confirmed a
real signal — not a pigeonhole artifact of coarse delta_E alphabet size
and 3-regular graph structure — by an independently-run label-permutation
null control not present in the run package (real: 100% depth==0 on all
four primes; null: 35-57% mean across 30 trials/prime), but this signal is
orthogonal to, and does not resolve, the funnel/basin-capture mechanism
question `DEC-20260806-357b30` named as the next step; that question is
reframed (the specified depth operationalization is structurally
uninformative at this delta_E resolution), not answered or fully closed.
Two small factual slips in ANOM-1's own supporting prose (an understated
distinct-value-count range and a mislabeled local-minimum-population list)
should be corrected before citation, though neither affects the anomaly's
core validity. `certificate.kind: none` and the diagnostic-only framing
correctly hold throughout; three concrete overclaim risks for the coming
`EV-SSIQ-*`/`DEC-*` records are named in Front 4 and should be guarded
against explicitly in that text's `limitations` block.

## Next concrete action

Coordinator: (1) accept PART A/GD-12 as genuinely, non-trivially fixed
per Front 1 — no further action needed on this front; (2) add the
delta_E label-permutation null control (Front 2b) to the durable record,
either as an appended finding on this batch or as the first required step
of any successor amendment that further interprets ANOM-1, together with
the falsifiable mechanical hypothesis it supports (near-Lipschitz spatial
clustering of delta_E along graph edges, testable by re-running at a
larger smoothness bound B/X); (3) correct ANOM-1's two numeric slips
(Front 3: 8/11/13/13 distinct values, not "8-11"; 95/132/194/287
local-minimum populations, not "95/324/478/611") before this batch's
findings are cited in `EV-SSIQ-*`/`DEC-*` text; (4) when drafting that
record, explicitly separate GD-12-fixed from any implication about
`H-SSIQ-36e970`'s status, and separate the mild-but-real top-decile
concentration measurement from the uninformative (not "negative")
correlation result, per Front 4's three named risks; (5) treat the
funnel-structure mechanism question as reframed, not closed — a future
amendment attempting it should use a depth operationalization with
demonstrated non-degenerate variance at whatever delta_E resolution it
runs at, verified by the same null-permutation control before relying on
it.

## Overall verdict

**CHALLENGE (narrow).** Both of this batch's headline results are
independently confirmed genuine on adversarial re-derivation: GD-12's
corrected cross-check is not a hollow pass on a population dominated by
trivial self-traps (47.4% of trapped=True walks are genuine multi-step
cases, cross-triangulated exactly against this reviewer's own prior
disagreement-bucket counts), and ANOM-1's depth==0 universality is a real,
control-confirmed signal rather than a pigeonhole artifact of coarse
delta_E resolution. What this review adds, and what the Coordinator should
not proceed past without incorporating: (a) a null-object control the run
package never ran, whose result changes ANOM-1 from "unexplained anomaly"
to "control-confirmed real signal that is nonetheless orthogonal to the
funnel-structure question it was meant to help answer"; (b) two small,
independently-verified numeric slips inside ANOM-1's own supporting prose;
and (c) three concrete overclaim risks named before, not after, the
Coordinator drafts `EV-SSIQ-*`/`DEC-*`.

```yaml
red_team_report:
  id: RT-BATCH-009
  task_id: TASK-20260806-bb916b
  claim_under_review: >-
    Coordinator-committed snapshot 302b580f (parent 66753c92), receipt
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/archives/TASK-20260806-e3499d-receipt.yaml,
    covering RUN-SSIQ-a85692-f under EXP-SSIQ-a85692's v6 amendment
    (specification_v6.yaml, frozen after three pre-freeze review rounds):
    PART A (gd12_fix_v6) reported the corrected trapped-vs-structural
    cross-check PASSES on all four primes with ZERO disagreements (1316/1316
    trapped=True walks), fixing GD-12; PART B (funnel_structure_diagnostic_v6)
    reported all twelve of the frozen spec's own stated expected numeric
    values match exactly, plus one genuine, disclosed anomaly (ANOM-1):
    depth(m)==0 for every basin-eligible structural local minimum on every
    prime (646/646), making the REQUIRED CORRELATION mathematically
    undefined.
  objections:
    - "OBJ-1: None -- Front 1's independent reconstruction of the walk-length distribution (via basin_size_by_local_min and n_basin_eligible, cross-referenced against RT-BATCH-008.md's own v5 disagreement-bucket counts) confirms the zero-disagreement cross-check result is substantively meaningful: 670/1316 (47.4%) of all trapped=True walks are genuine multi-step, start!=terminal cases (84/170, 120/234, 216/392, 250/520 per prime), not 0-step self-traps. These four counts (84,120,216,250) are exactly the start-vs-terminal disagreement-bucket sizes I independently derived under v5's broken cross-check in RT-BATCH-008.md -- an independent arithmetic cross-triangulation, not a new coincidence. No objection to PART A's headline claim."
    - "OBJ-2: The REQUIRED CORRELATION's null result (ANOM-1/OBS-B3) is correctly reported as null rather than fabricated, but the run never ran a null-object control to distinguish 'ANOM-1 is a pigeonhole artifact of coarse delta_E alphabet size (8-13 distinct integer values) plus 3-regular graph structure' from 'ANOM-1 reflects real spatial autocorrelation in how delta_E is distributed across the graph.' I ran this control (30 trials/prime: hold the real graph and the real delta_E value multiset fixed, randomly permute which vertex gets which value, recompute depth==0 fraction among local minima). Real data: 100% depth==0 on all four primes (646/646). Null control: mean 35.3%-57.1% depth==0 across the four primes (range 24.8%-67.9% across trials). The null does NOT reproduce the real result, confirming ANOM-1 is a real, control-confirmed signal, not a pigeonhole artifact -- but this control and its result exist nowhere in the run package or execution_report.yaml and should be added before ANOM-1 is cited further. Separately, this real signal is orthogonal to, and does not resolve, the basin-capture/funnel-structure question funnel_structure_diagnostic_v6 was built to test: the depth operationalization (immediate-neighbour delta gap) saturates at zero for a structural reason independent of whether basin capture is concentrated, so its null correlation is uninformative about funnel structure either way, not evidence against one."
    - "OBJ-3: execution_report.yaml ANOM-1's own supporting numeric claims contain two factual slips, independently checked against the same archived raw-result.json this run's own code reads. (a) 'only 8-11 distinct integer values observed per prime' understates p=5737 and p=7333, which both have 13 distinct delta_E values (1 through 13), not <=11 -- direct enumeration gives 8/11/13/13 across the four primes. (b) 'all 95/324/478/611-scale local-minimum populations... also show depth==0 universally' mislabels three of its own four numbers: 95 is correctly p=2437's true total local-minimum count, but 324/478/611 are p=3889/5737/7333's VERTEX counts (n_vertices), not their local-minimum counts -- the true local-minimum counts, independently recomputed and consistent with RT-BATCH-008.md's own prior figures, are 132/194/287 (114+18, 176+18, 270+17). Neither slip affects the anomaly's core validity, which I independently reconfirmed a third time (100% depth==0 on both the 646 basin-eligible and the full 95/132/194/287 local-minimum populations, from a from-scratch script bypassing funnel_structure_diagnostic_v6.py entirely), but both are exactly the 'trace a producer's own confidence-building prose before it becomes a record' pattern this campaign's GD-9/PF-8/PF-9 standing discipline exists to catch, most recently reaffirmed by this very amendment's own PF-8 fix at round 2 pre-freeze."
    - "OBJ-4: Three concrete overclaim risks for the coming EV-SSIQ-*/DEC-* records, none present in this run's own artifacts (which correctly decline to interpret beyond OBJECTIVE_BOUNDARY): (i) 'GD-12 is genuinely fixed' must not be read as bearing on H-SSIQ-36e970, which remains status:analyzed/DATA-UNAVAILABLE-BLOCKED and untouched by this batch; (ii) OBS-B2's mild-but-real top-decile concentration (17-19% vs 10% uniform baseline) must not be conflated with the correlation's undefined result into a single blended 'no funnel structure' claim -- they are different claims resting on different evidence; (iii) ANOM-1's newly control-confirmed spatial-autocorrelation signal (undirected local clustering of delta_E) must not be read as evidence toward H-SSIQ-36e970's directional-gradient question (greedy vs random hitting-time efficiency) -- related subject matter, not the same test, and OBJECTIVE_BOUNDARY's existing scoping should be explicitly extended to cover this new control result if it is promoted into the record."
  required_controls:
    - "The delta_E label-permutation null control (Front 2b, OBJ-2) must be added to the durable record -- either appended to this batch's evidence or named as the first required step of any successor amendment interpreting ANOM-1 further -- together with the falsifiable mechanical hypothesis it supports (near-Lipschitz spatial clustering of delta_E along graph edges), testable by re-running at a larger smoothness bound B/X and checking whether depth==0's universality recedes toward the null's ~35-57% baseline as the delta_E alphabet grows finer."
    - "ANOM-1's two numeric slips (OBJ-3) require correction before citation in EV-SSIQ-*/DEC-* text: correct distinct-delta_E-value counts are 8/11/13/13 (not '8-11'); correct local-minimum population counts are 95/132/194/287 (not '95/324/478/611')."
    - "Front 4's three separation requirements (OBJ-4) should be stated explicitly in the coming decision record's limitations block, not left implicit: GD-12-fixed vs H-SSIQ-36e970 status; mild-concentration vs undefined-correlation; ANOM-1's undirected autocorrelation vs the hypothesis's directional-gradient question."
  counterexample_or_mutation: >-
    The delta_E label-permutation null (30 trials/prime, real graph +
    real value multiset, randomized vertex assignment) falsifies the
    "ANOM-1 is a trivial pigeonhole artifact of coarse alphabet size plus
    3-regular graph structure" hypothesis: that hypothesis predicts the
    null control should already reproduce ~100% depth==0, but it produces
    only 35.3%-57.1% (mean across primes), independently executed against
    the real rebuilt graphs and archived delta_map, not from any prior
    report's prose.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline is this
    campaign's own instrument- and fix-scrutiny discipline: Front 1's
    cross-triangulation against RT-BATCH-008.md's own disagreement-bucket
    arithmetic, and Front 2/3's null-object control and independent
    numeric re-derivation, both extend that discipline using the same
    "trace it, don't trust it, and bring your own control" standard this
    lineage has applied at every prior batch.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. ANOM-1's newly control-confirmed spatial-autocorrelation signal is a control-confirmed empirical fact about this batch's delta_E labelling scheme, not a heuristic assumption feeding any complexity claim."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere (asymptotic_claim: null, correctly). Measured wall-clock 3.17s against a 900s/0.3-CPU-hour budget, roughly two orders of magnitude under -- confirmed via manifest.yaml."
    - "The null-object control I ran (120 permutation trials across four primes, no new graph construction or delta_E search) took under 5 seconds and would add effectively zero marginal cost if promoted into the durable record."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "funnel_structure_diagnostic_v6's OBJECTIVE_BOUNDARY correctly restates v5's diagnostic-not-claim scoping and is not contradicted by anything in the run package or this review -- neither GD-12's confirmed fix nor ANOM-1's control-confirmed signal converts PART B into a claim about a computable delta_E-gradient. Front 4/OBJ-4 names the three most likely places this scoping could still be lost when the Coordinator drafts the next record."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level diagnostic, not a proof-oriented proposal. Attacked and held."
    - "corrected_equivalence_proof (trapped=True => is_structural_local_min(terminal), unconditionally) was subjected to the boundary-and-strictness attack: checked against the 0-step case (terminal=start=itself a local minimum by construction, trivially holds) and against the 670 genuinely multi-step cases in Front 1/OBJ-1 (all independently confirmed passing, none excepted). No boundary case survives unchecked."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-f as committed at 302b580f, against
    specification_v6.yaml frozen at 66753c92: PART A's corrected
    cross-check genuinely and non-trivially confirms corrected_equivalence_proof
    -- 47.4% of the 1316 total trapped=True walks checked are genuine
    multi-step cases where start != terminal, independently
    cross-triangulated against this reviewer's own prior disagreement-bucket
    arithmetic from RT-BATCH-008.md. GD-12 is genuinely fixed within this
    run's tested scope. PART B's twelve required numeric matches hold
    exactly, independently spot-checked. ANOM-1 (depth==0 universally) is
    confirmed a real signal -- not a pigeonhole artifact -- by an
    independently-run label-permutation null control not present in the
    run package (real: 100% depth==0 on all four primes; null: 35-57%
    mean across 30 trials/prime), but this signal is orthogonal to, and
    does not resolve, the funnel/basin-capture mechanism question
    DEC-20260806-357b30 named as the next step; that question is
    reframed, not answered or fully closed. Two small factual slips in
    ANOM-1's own supporting prose (understated distinct-value-count range;
    mislabeled local-minimum-population list) should be corrected before
    citation, though neither affects the anomaly's core validity.
    certificate.kind: none and the diagnostic-only framing correctly hold
    throughout; three concrete overclaim risks for the coming
    EV-SSIQ-*/DEC-* records are named and should be guarded against
    explicitly in that text's limitations block.
  next_concrete_action: >-
    Coordinator: (1) accept PART A/GD-12 as genuinely, non-trivially
    fixed per Front 1/OBJ-1 -- no further action needed on this front;
    (2) add the delta_E label-permutation null control (Front 2b/OBJ-2)
    to the durable record, together with its falsifiable mechanical
    hypothesis (near-Lipschitz spatial clustering of delta_E along graph
    edges, testable via a larger smoothness bound B/X); (3) correct
    ANOM-1's two numeric slips (Front 3/OBJ-3: 8/11/13/13 distinct values,
    not "8-11"; 95/132/194/287 local-minimum populations, not
    "95/324/478/611") before citation in EV-SSIQ-*/DEC-* text; (4) when
    drafting that record, explicitly separate GD-12-fixed from any
    implication about H-SSIQ-36e970's status, and separate the
    mild-but-real top-decile concentration from the uninformative
    correlation result, per Front 4/OBJ-4's three named risks; (5) treat
    the funnel-structure mechanism question as reframed, not closed -- a
    future amendment attempting it should use a depth operationalization
    with demonstrated non-degenerate variance at whatever delta_E
    resolution it runs at, verified by the same null-permutation control
    before relying on it.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-BATCH-009.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Executed directly (not merely traced): rebuilt the 2-isogeny graphs
    for all four primes (2437, 3889, 5737, 7333) from scratch via
    trapping_diagnostic_v5.build_graph_for_prime (pinned seed 20260805,
    matching the pinned convention) and loaded RUN-SSIQ-a85692-b/raw-result.json's
    real delta_map for all four primes via trapping_diagnostic_v5.load_archived_prime_data.
    Reconstructed the walk-length (0-step vs multi-step) distribution for
    all 1316 trapped=True walks from funnel_structure_diagnostic.json's
    own basin_size_by_local_min/n_basin_eligible fields and
    cross-referenced the resulting multi-step counts (84/120/216/250)
    against this reviewer's own independently-derived v5 disagreement-bucket
    counts in RT-BATCH-008.md. Independently enumerated raw-result.json's
    delta_map for all four primes to obtain exact distinct-value counts
    (8/11/13/13) and cross-checked against ANOM-1's stated "8-11" range.
    Independently recomputed full local-minimum populations (95/132/194/287)
    from the same rebuilt graphs and delta_map, cross-checked against
    ANOM-1's "95/324/478/611" phrase. Ran a from-scratch, standalone
    delta_E label-permutation null control (30 trials per prime, seeded
    random.Random(42)): for each trial, shuffled the real delta_map's
    values across the real graph's vertex set, recomputed
    is_structural_local_min and depth(m) via the same formulas
    trapping_diagnostic_v5.py/funnel_structure_diagnostic_v6.py use, and
    recorded the fraction of resulting local minima with depth==0,
    comparing against the real (unpermuted) data's 100% depth==0 result
    on all four primes. All code executed in a scratchpad Python session
    importing trapping_diagnostic_v5 and build_isogeny_graph unchanged;
    no file written outside this report; no run artifact, specification
    file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-BATCH-009.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml and
    every run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
