# RT-BATCH-008 — Red Team review of RUN-SSIQ-a85692-e (EXP-SSIQ-a85692 v5,
# H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-008 (last batch, 8-batch campaign_budget)

**Reviews the Coordinator-committed snapshot at `a686f170` (parent `59cfaf39`),
receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/archives/TASK-20260806-bac693-receipt.yaml`,
covering `RUN-SSIQ-a85692-e` under `EXP-SSIQ-a85692`'s v5 amendment
(`specification_v5.yaml`, frozen after two pre-freeze review rounds).** Per
this task's operating rules, only this Coordinator-committed snapshot is
treated as durable input; the working tree at `a686f170` was confirmed clean
(`git status --short`). This report changes nothing under
`experiments/EXP-SSIQ-a85692/` (including `specification_v5.yaml`) or any
ledger record.

Read in full, per the launching task: `specification_v5.yaml` (the frozen v5
contract); `RT-PREFREEZE-EXP-SSIQ-a85692-v5.md` and
`RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md` (both pre-freeze reviews, my own
prior work in this lineage — PF-6 originated in round 1);
`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py`'s
`greedy_descent_hitting_time`, read directly, in full;
`experiments/EXP-SSIQ-a85692/implementation/{ols_hardened.py,
gd11_regression_test.py, trapping_diagnostic_v5.py, run_batch008.py}`, the
actual executed code; the full `RUN-SSIQ-a85692-e` package including
`execution_report.yaml`'s `PD-SPEC-1` entry in full; `goal.yaml`'s `GD-11`
entry, `campaign_budget`, and `pause_conditions`; `EV-SSIQ-87d21a.yaml`;
`DEC-20260805-6aa5c2.yaml`. All independent verification below was **executed
directly** against the real committed data (`RUN-SSIQ-a85692-b/raw-result.json`,
a freshly rebuilt graph via `build_isogeny_graph.build_graph_bfs`, and the
frozen, unmodified `greedy_descent_hitting_time`/`ols_loglog_fit`/
`bootstrap_gap_ci`), not derived from any prior report's prose.

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
    (VAL/RT-BATCH-003 through 007, RT-PREFREEZE-EXP-SSIQ-a85692[-v2..v5,-v5-round2]),
    recorded as the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with every producer and every prior reviewer in this
    lineage, including my own two pre-freeze reviews of this same amendment.
    It does not upgrade the campaign's evidence tier and does not itself
    satisfy or advance a closure quorum. A Validator (TASK-20260806-3c6363)
    is reviewing the same run independently and in parallel; this report was
    produced without coordinating with it.
```

---

## Bottom line up front

**PD-SPEC-1's diagnosis is independently CONFIRMED CORRECT as far as it
goes — but it is INCOMPLETE.** The Executor correctly identified that the
frozen spec's required cross-check compares the walk's `trapped` flag against
`is_structural_local_min(START)` when the underlying mathematical argument
(PF-6, which I wrote in round 1 of this amendment's own pre-freeze review)
actually proves the equivalence for the walk's **TERMINAL** vertex, a
different vertex whenever `start` is not itself a local minimum. I
independently reconfirmed this with my own hand-traced counter-example, using
a **different vertex and a different prime** than the Executor's own
`(148,37)`/2437 example (`(58,996)`/3889, full trace below) — the Executor's
diagnosis holds.

**But my own independent decomposition of the disagreement counts finds a
SECOND, distinct source the Executor's write-up never identifies or
separates out**: for every one of the 9/18/18/17 F_p-rational (`delta_E=1`)
vertices per prime, `greedy_descent_hitting_time` returns `trapped: False` **by
an explicit, separate design choice** (delta=1 is defined as "success," never
"trapped," and the function short-circuits before entering its loop) — but
`is_structural_local_min` flags every delta=1 vertex `True` **trivially** (it
is definitionally the global minimum value). This mismatch is present
**even when start == terminal** (0 steps), so it is not an instance of the
start-vs-terminal bug at all — it is a second, independent boundary-condition
defect in the same claimed equivalence. I confirmed by direct count that
these two sources exactly and exhaustively partition every disagreement on
all four primes (84+9=93, 120+18=138, 216+18=234, 250+17=267 — exact). This
matters operationally: the Executor's own suggested fix ("expose the walk's
terminal vertex and compare against that instead") is **not sufficient by
itself** — applied naively to *all* walks (including the 15–28% per prime
that succeed by reaching delta=1), it would newly misclassify every
successful walk's delta=1 terminal as a "disagreement" too, since
`trapped=False` there while `is_structural_local_min(terminal)=True`
trivially. A correct fix must restrict the equivalence check to `trapped:
True` walks only, and treat the delta=1/success case as outside the claim
entirely.

**This is genuinely a NEW category of defect**, not a restatement of GD-6,
GD-9/GD-10, or GD-11: it is an unconditional mathematical claim, asserted with
high confidence in a red-team review's own prose ("provably exact... for
every vertex, unconditionally," "conclusively a bug... never a mechanism
finding") and transcribed into frozen contract text as fact, where the
abstract argument was correct but its concretization into an executable
per-vertex check silently substituted the wrong quantifier target — and where
neither of two pre-freeze review rounds caught it with a concrete trace,
despite round 2's own governing discipline that round ("trace it, don't trust
it") applying correctly to an adjacent finding (PF-9) but not to this one. I
recommend the Coordinator name this GD-12 (next in `goal.yaml`'s sequence)
under a new "review-claim-not-traced" category.

**PART A is unaffected and its own contrast is genuine, not a test-construction
artifact** — independently re-executed. **The structural local-minimum
fractions (0.41–0.47) are independently confirmed valid and correctly
computed**, including an independent bit-identical reproduction of the
archived `greedy_trapped_fraction` for prime 2437, which is strong evidence
the graph rebuild reproduces the *exact* original adjacency, not merely a
same-size/same-degree graph.

Given campaign_budget is now exhausted (8/8 batches) and no completion
criterion is met, I recommend `closed_at_budget` (not `paused`, and not a
request for extension), with the corrected cross-check as the concretely
named resume action.

---

## Front 1 — Independent re-verification of PD-SPEC-1 from first principles

### 1a. The code, traced directly

`greedy_descent_hitting_time` (`descent_hitting_time.py` lines 179–222):

```python
if delta_map[start] == 1:
    return {"hitting_time": 0, "trapped": False, ...}      # short-circuit
while True:
    nbrs = [v for v in adjacency[current] if v != prev]
    if not nbrs: nbrs = list(adjacency[current])
    candidates = [v for v in nbrs if delta_map[v] < cur_delta]
    if not candidates:
        return {..., "trapped": True, ...}                 # halts HERE, at `current`
    ...
    current = nxt                                            # descends
    if delta_map[current] == 1:
        return {..., "trapped": False, ...}                 # reaches delta=1: "success"
```

`trapped: True` is returned when the loop variable `current` — which may have
moved several steps away from `start` — has no smaller-delta neighbour.
`current` at the point of return is the walk's **terminal vertex**, which
equals `start` only when `start` is itself already a local minimum (0-step
case). The frozen spec's cross-check (`specification_v5.yaml` line 279)
compares this flag against `is_structural_local_min(start)` — a fact I
confirmed by direct `grep`: the exact string `is_structural_local_min(start)`
appears **only** in `specification_v5.yaml`, in neither pre-freeze review
report. This is a real code fact, not an interpretation.

### 1b. My own counter-example — different vertex, different prime

I rebuilt prime 3889's graph independently (`build_isogeny_graph.build_graph_bfs`,
seed 20260805, matching the pinned convention) and picked a vertex from the
crosscheck's own disagreement list with `delta_E != 1` (excluding the
Executor's `(148,37)`/2437 example):

```
picked vertex (58, 996), delta=11
  at (58, 996) delta=11, neighbour deltas [4, 3, 3], candidates=[(650,3544),(1831,2247),(2330,514)]
  (tie-break) -> (2330, 514), delta=3
  at (2330, 514) delta=3, neighbour deltas [11, 9, 3], candidates=[]  -> TRAPPED

walk result: {'trapped': True, 'steps': 1, ...}
terminal vertex (2330, 514): is_structural_local_min = True   (3 <= min([11,9,3])=3)
start vertex   (58, 996):   is_structural_local_min = False   (has neighbour delta=3 < 11)
```

This independently reproduces the Executor's mechanism exactly, on a
different vertex and a different prime: the walk descends one non-trivial
step before getting trapped, so `trapped(start)=True` but
`is_structural_local_min(start)=False`, while `is_structural_local_min(terminal)=True`
— confirming PF-6's underlying mathematical argument is correct **for the
terminal vertex** and confirming the spec's operational comparison target
(`start`) is wrong. **PD-SPEC-1's core diagnosis: CONFIRMED, independently,
by direct execution.**

### 1c. A second, independent source PD-SPEC-1 does not separate out

I decomposed all four primes' disagreement lists by direct query
(`trapped_vs_structural_crosscheck.json` cross-referenced against
`delta_map`):

| prime | n_disagreements | walk_trapped=True & structural=False (start-vs-terminal) | walk_trapped=False & structural=True (delta=1 boundary) | delta=1 (F_p-rational) vertex count |
|---|---|---|---|---|
| 2437 | 93 | 84 | 9 | 9 |
| 3889 | 138 | 120 | 18 | 18 |
| 5737 | 234 | 216 | 18 | 18 |
| 7333 | 267 | 250 | 17 | 17 |

The second bucket is **exactly** the set of F_p-rational vertices (which
resolve `delta_E=1` by identity, per `compute_delta_e.py`), confirmed by
direct trace:

```
delta=1 vertex picked: (332, 0), p=3889
walk result (start==terminal, 0 steps): {'trapped': False, 'steps': 0, ...}
neighbour deltas: [1, 4, 4]; is_structural_local_min((332,0)) = True   (1 <= min([1,4,4])=1)
```

This is **not** an instance of the start-vs-terminal issue — start and
terminal are the same vertex here (0 steps taken). It is a **separate**
definitional mismatch: `greedy_descent_hitting_time` treats reaching
`delta_E=1` as a distinct "success" outcome, deliberately never labelled
`trapped`, regardless of whether that vertex is also (trivially) a
graph-structural local minimum under `is_structural_local_min`'s own `<=`
definition. PF-6's "unconditional... for every vertex" framing is false at
this boundary independent of the terminal-vertex question. **Consequence for
the required fix**: simply exposing and comparing against the walk's
terminal vertex is not sufficient. Applied to *all* walks (not just
`trapped: True` ones), it would newly misclassify **every successful walk**
(15–28% of vertices per prime, since `1 - greedy_trapped_fraction` = 0.163 /
0.278 / 0.180 / 0.149) as a disagreement, since their delta=1 terminal is
`trapped=False` but trivially `is_structural_local_min=True`. A correct fix
restricts the equivalence claim to `trapped: True` walks only (verify their
now-exposed terminal is a genuine structural local minimum) and drops the
`trapped: False` (success) case from the comparison entirely, since no
local-minimality claim is being made about it.

---

## Front 2 — Is this a new defect, or does it belong to an existing category?

**Genuinely new — not GD-6, not GD-9/GD-10, not GD-11.**

- **Not GD-9/GD-10** (a validation artifact that structurally cannot fail, or
  a fix that never calls the function it validates). Here the check *did*
  call the real, unmodified `greedy_descent_hitting_time` and *did* fail
  loudly and reproducibly — the instrument worked exactly as built. The
  defect is upstream of the instrument, in what the frozen contract told the
  instrument to compare.
- **Not GD-6** (something already knowable was not re-checked before
  freeze) in the narrow sense — this is not a stale fact that changed; it is
  a proof whose conclusion was never traced against a concrete multi-step
  example at any point in its lineage.
- **Not GD-11** (a numerical-robustness defect in floating-point arithmetic
  in shared library code). This is not a numerics issue at all;
  `greedy_descent_hitting_time` behaves exactly as documented and intended.

**What it actually is**: I wrote PF-6 in round 1 of this amendment's own
pre-freeze review. Re-reading my own round-1 text now against the actual
frozen spec: round 1's mathematical argument — "the predecessor's delta is
always strictly greater... so it can never be excluded from a smaller-delta
candidate set" — is **correct**, and remains correct today (my own
independent trace above re-confirms it, for the terminal vertex). But round
1's prose is genuinely **ambiguous about which vertex "w" denotes**: it never
disambiguates "the vertex the walk eventually halts at" from "the vertex the
walk starts from," and its own required-fix language ("run the cross-check
against every vertex with a resolved `delta_E` value") reads naturally as
"iterate the check over every **starting** vertex" — the same iteration
`run_population` already uses. Directly `grep`-confirmed: the literal phrase
`is_structural_local_min(start)` appears in **neither** pre-freeze review
report — it is the Coordinator's own concretization of round 1's abstract
argument into the frozen operational text, and that concretization silently
equated "w" with "start." Round 2 then reviewed this exact frozen text and
wrote "the exact walk-trapped/structural-local-minimum equivalence argument
in round 1's (g) is unchanged and still correct... CONFIRMED APPLIED AND
ADEQUATE" — without ever re-tracing a concrete multi-step example against the
now-concrete `is_structural_local_min(start)` comparison. This is the same
review, in the same document, that *did* apply exactly this discipline to an
adjacent finding: PF-9 was caught precisely because round 2 queried the real
`raw-result.json` fields directly rather than trusting round 1's prose. PF-6
got no equivalent treatment.

**Could this have been caught at pre-freeze?** Yes, cheaply. My own trace
above took under a minute against real data; an even smaller hand-worked
example makes it self-evident: a 3-vertex path A(delta=5)–B(delta=3)–C(delta=2),
C a genuine dead end. The walk from A takes two strict-descent steps and
halts at C; `is_structural_local_min(A)=False` but `trapped=True`. Neither
pre-freeze round constructed any concrete example at all for PF-6 — round 1
argued from the docstring alone, and round 2 explicitly deferred to round 1
without re-deriving.

**Recommend naming a new defect (GD-12, next in `goal.yaml`'s sequence),
category: "an unconditional mathematical claim asserted with high confidence
in review prose, transcribed into frozen contract text as fact, whose
concretization into an executable check silently mis-targeted the quantifier
— never checked against a concrete trace by either pre-freeze review round,
despite the same round applying that exact discipline to an adjacent
finding."** Standing repair candidate: any pre-freeze finding that asserts an
equivalence, invariant, or "provably exact" claim as the *justification* for
a required check must be accompanied by (or immediately followed by) a
concrete, executed trace of at least one non-trivial instance before the
claim is written into frozen contract text as unconditional — the same
"trace it, don't trust it" standard this campaign's own GD-9/PF-9 lineage
already applies to Executor and Coordinator artifacts, extended explicitly to
a reviewer's own mathematical assertions.

---

## Front 3 — Does this affect PART A's validity, or is it fully contained to PART B?

**Fully contained to PART B, confirmed independently, not merely asserted.**
`ols_hardened.py` and `gd11_regression_test.py` touch none of
`trapping_diagnostic_v5.py`'s code or data; the receipt's own
`v1_v4_and_prior_runs_untouched` precommit check and the Executor's
`required_artifacts_note_diff_cross_check` both confirm disjointness, and I
independently re-executed PART A's own required regression tests from
scratch (not merely re-read the JSON):

```
N324_n3  (median_greedy=[10,20,30], median_random=[15,45,90]):
  v2:       lo=None hi=None n_valid=0
  original: lo=-0.5 hi=0.5  n_valid=2000  sample_gaps=[-0.5,-0.5,-0.5]
N611_n6  (median_greedy=[24]*6, median_random=[36]*6):
  v2:       lo=None hi=None n_valid=0
  original: lo=0.5  hi=0.5  n_valid=2000  sample_gaps=[0.5,0.5,0.5]
```

These are bit-identical to the archived `bootstrap_gap_ci_v2_regression_test.json`.
I also traced *why* the original produces exactly `-0.5`/`0.5` rather than an
arbitrary or undefined value (front 6 below) to rule out a rigged or
coincidentally-convenient test construction. **PART A's contrast is genuine.**

---

## Front 4 — Are the structural local-minimum fractions (0.41–0.47) still valid?

**Yes, independently confirmed, and the crosscheck's failure has no bearing
on them.** I independently recomputed, from scratch, for prime 2437 (using
the same rebuilt graph and the same real `delta_map`):

```
independently recomputed n_structural_local_min = 95 (fraction 0.467980) -- MATCHES trapping_diagnostic.json exactly
independently recomputed greedy trapped_fraction  = 0.8374384236453202     -- MATCHES the RUN-SSIQ-a85692-b archived value bit-for-bit
```

The bit-identical reproduction of the *archived* `greedy_trapped_fraction`
(not merely a fraction of the right approximate size) is strong evidence the
graph rebuild reproduces the **exact original adjacency**, not merely a
same-count/same-degree graph — independently addressing the residual risk
PF-5/PF-11 flagged in pre-freeze review. `is_structural_local_min`'s own
computation (`delta_map[v] <= min(neighbour deltas)`) is a direct, correctly
implemented translation of its stated definition — confirmed by hand for
several vertices above, in addition to the aggregate match. **The crosscheck
tests a different, additional claim** (that the walk's flag agrees with a
particular vertex's local-min status) and its failure is a comparison-target
bug, not a defect in how the fractions themselves are computed. The
0.41–0.47 structural local-minimum fractions and their contrast against the
72–85% `greedy_trapped_fraction` (documented, correctly per PF-8, as a
different, non-corroborating statistic reflecting many-to-one funnelling)
remain valid, informative diagnostic numbers.

---

## Front 5 — Lever L4, BATCH-009, and how this goal should close out

`goal.yaml`'s `campaign_budget.maximum_batches: 8`, `current_batch_id:
BATCH-008` — **this is the last batch inside the declared hard budget.**
`pause_conditions` include "the eight-batch campaign budget is exhausted
without an admissible next lever or next mechanism" and "a definitive
infrastructure... blocker prevents the next approved task." Neither of the
other two conditions (all levers closed; user-requested pause) applies.

**Recommendation: `closed_at_budget`, not `paused`, and not a request for
extension.** Reasoning:

1. The 8-batch budget is a declared hard limit, not a soft one this batch's
   findings give cause to override. GD-12 (the newly found spec defect) is a
   well-scoped, zero-new-search-cost text/design fix (restrict the corrected
   cross-check to `trapped: True` walks against an exposed terminal vertex,
   excluding the delta=1/success case) — exactly the shape of "concrete
   resume action" a budget-exhausted closure is supposed to carry (AGENTS.md
   rule 9), not evidence of an emergency requiring the Coordinator to bypass
   the checkpoint.
2. Lever L4 remains genuinely OPEN, not closed by a committed ceiling
   argument and not advanced to a falsifiable hypothesis with a costed,
   sub-1/3 mechanism — none of `goal.yaml`'s completion criteria are met.
   `closed_at_budget` (not `completed`, not a silent downgrade to
   understate progress) is the accurate terminal status per this
   repository's own convention (`GOAL-MLKEM-001`, `GOAL-P13-001`,
   `GOAL-AES-002/003` all use exactly this pattern for a hard-budget stop
   with an open lever).
3. This batch (like BATCH-002 through BATCH-007) again surfaced a
   validation-instrument/specification defect rather than new evidence about
   the mechanism (pervasive greedy trapping) itself. Per the inventor
   protocol, a run of screened-and-rejected/defect-laden batches is a
   fatigue report about the search's own process, not a finding that L4 is
   exhausted — I am not recommending L4's retirement, and `goal.yaml`
   already explicitly records L4 as "NOT RETIRED."

**Ranked resume action for a future extension/re-approval of this goal:**

1. **[Highest value]** Correct GD-12: supersede (not edit)
   `greedy_descent_hitting_time` with a version that exposes the walk's
   terminal vertex (same "supersede by addition" discipline `ols_hardened.py`
   already established for GD-11), and rewrite the cross-check to (a) restrict
   the equivalence claim to `trapped: True` walks, comparing against
   `is_structural_local_min(terminal)`, and (b) explicitly state the delta=1/
   success case is outside the claim (no comparison made). Re-run against
   the same four primes' already-archived `delta_map` — zero new search
   cost, no new graph build required beyond what this run already did.
2. **[Second]** The structural local-minimum fractions (now independently
   validated) show <50% of vertices are genuine local minima while 72–85% of
   greedy walks end up trapped somewhere — a real, now-quantified funnelling
   signal. `execution_report.yaml`'s own `OBS-B3` already flags a natural
   follow-up (in-degree/funnel-structure analysis: which local minima capture
   the most walks) as "a separate analysis, not requested" — this is the
   most promising specific next question for L4 once GD-12 is fixed,
   because it is the first candidate mechanism this campaign has that could
   explain *why* trapping is pervasive rather than merely re-confirming that
   it is.
3. **[Deferred, correctly]** Widening to larger N stays deferred until (1)
   and (2) give an evidence-based reason to expect different behaviour —
   unchanged from `goal.yaml`'s own standing deferral.

---

## Front 6 — Other checks: diff-list, PART A contrast, overclaim risk

**Diff-list cross-check**: independently spot-checked, holds. `ols_hardened.py`
defines exactly `ols_loglog_fit_v2` and `bootstrap_gap_ci_v2`
(`__all__` confirms), the latter calling `ols_loglog_fit_v2` (not
`dht.ols_loglog_fit`) at both call sites, confirmed by direct read — no alias
form present. `trapping_diagnostic_v5.py` imports `build_isogeny_graph`/
`descent_hitting_time` unchanged, by reference; no local fork exists.

**PART A's contrast is not a construction artifact.** I traced *why* the
original (unhardened) guard on `N_list=[324,324,324]` produces exactly
`gamma=-0.5` rather than an arbitrary/undefined value: `xs = [log(324)]*3`
are bit-identical floats, but `xbar = sum(xs)/3` rounds to one ULP away from
`xs[0]` (`5.780743515792328` vs `5.780743515792329`), giving a tiny but
non-zero `sxx = 2.3665...e-30`; `sxy` picks up a correspondingly tiny,
non-zero value from `ybar`'s own rounding, and the ratio is deterministically
`-0.5` for this specific input in IEEE-754 double precision. This is a
genuine, reproducible floating-point property (confirmed independently four
times now across this lineage: round-1 pre-freeze, round-2 pre-freeze, the
Executor's own run, and this review), not a cherry-picked "nice number."

**Overclaim risks for future citation**:

1. A future record could read "PART B's required cross-check FAILED on all
   four primes" as meaning the diagnostic's own headline measurement (the
   structural local-minimum fractions) is unreliable. Front 4 above shows
   this is false — the fractions are independently validated; only a
   *secondary* consistency check (against a mis-specified comparison target)
   failed. Any successor record citing this batch's fractions should say so
   explicitly.
2. `specification_v5.yaml`'s own frozen text still asserts the false
   "conclusively a bug... never a mechanism finding" claim as unconditional
   fact. This run and this review both correctly declined to endorse that
   framing, but the frozen contract text itself remains uncorrected until a
   Coordinator amendment supersedes it — a future producer skimming the
   spec rather than the run package could still be misled.
3. The Executor's classification ("specification_error, not a coding bug,
   not a negative research finding") is substantially correct and I concur,
   but it understates the category: this is not an ordinary
   ambiguous-phrasing spec error of the PF-4/PF-9 shape — it is a case where
   a **reviewer's own proof**, asserted with high confidence, was
   transcribed into a frozen contract without ever being traced. Naming it
   distinctly (GD-12) matters so the standing repair targets review
   discipline specifically, not only executor/coordinator transcription.

---

## Objections

- **OBJ-1**: The frozen spec's PF-6 cross-check compares
  `is_structural_local_min(start)` against `trapped`, but the underlying
  proof (correctly) establishes the equivalence for the walk's *terminal*
  vertex only — independently reconfirmed via a fresh hand-trace on a
  different vertex/prime (`(58,996)`, p=3889). Confirmed, matches PD-SPEC-1.
- **OBJ-2 [NOT raised by the Executor]**: A second, independent source
  contributes exactly 9/18/18/17 of the 93/138/234/267 disagreements per
  prime — every F_p-rational (`delta_E=1`) vertex, where `start==terminal`
  (0 steps) yet `trapped=False` (by the function's explicit "delta=1 =
  success" design) while `is_structural_local_min=True` (trivially). This is
  not an instance of the start-vs-terminal bug and must be handled
  separately in any corrected cross-check; naively "fixing" only the
  terminal-vertex issue would newly misclassify every *successful* walk
  (15–28% of vertices per prime) as a disagreement too.
- **OBJ-3**: PF-6's mathematical argument (which I authored in round 1 of
  this amendment's pre-freeze review) is correct in the abstract but was
  never checked against a concrete, multi-step trace by either pre-freeze
  round before being transcribed into frozen contract text as unconditional
  fact — a genuinely new defect category, not GD-6/GD-9/GD-10/GD-11.
- **OBJ-4**: `specification_v5.yaml`'s frozen text remains uncorrected;
  citing it directly (rather than the run package + this review) risks
  propagating the false "conclusively a bug" claim forward.

## Required controls

- A superseding version of `greedy_descent_hitting_time` (by addition, not
  edit, per this campaign's own `ols_hardened.py` precedent) must expose the
  walk's terminal vertex before any corrected cross-check can run.
- The corrected cross-check must restrict the equivalence claim to
  `trapped: True` walks only, comparing `is_structural_local_min(terminal)`;
  it must explicitly exclude `trapped: False` (delta=1/success) outcomes
  from the claim rather than silently including them.
- Any future pre-freeze finding asserting an unconditional equivalence,
  invariant, or "provably exact" claim as the justification for a required
  check must be accompanied by an executed, concrete (not merely
  hand-argued) trace of at least one non-trivial instance before being
  written into frozen contract text — the standing repair I recommend
  attaching to GD-12.

## Counterexample or mutation

Two independently executed counter-examples, both against the real,
unmodified functions and real archived `delta_map` data, both on different
vertices/primes than the Executor's own example:

**Start-vs-terminal (p=3889, vertex `(58,996)`):** `greedy_descent_hitting_time`
returns `trapped=True, steps=1`, terminal `(2330,514)` with neighbour deltas
`[11,9,3]` (`is_structural_local_min(terminal)=True`, confirming PF-6's real
claim); but `is_structural_local_min((58,996))=False` (neighbour deltas
`[4,3,3]`, has a strictly smaller neighbour) — falsifies "trapped(start) <=>
is_structural_local_min(start), unconditionally."

**Delta=1 boundary (p=3889, vertex `(332,0)`):** `greedy_descent_hitting_time`
returns `trapped=False, steps=0` (start==terminal, short-circuited); but
`is_structural_local_min((332,0))=True` trivially (neighbour deltas
`[1,4,4]`, delta=1 is the global minimum) — falsifies the same claim by a
second, independent mechanism, orthogonal to the start-vs-terminal issue.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
infrastructure work and a graph-structural diagnostic, `asymptotic_claim:
null` throughout (correctly inherited). The relevant baseline remains this
campaign's own instrument- and fix-scrutiny discipline (GD-4 through GD-11,
PF-9's "trace a prior review's own prose"): OBJ-2/OBJ-3 extend that
discipline one further step — to a reviewer's own mathematical argument,
asserted with high confidence and never concretely traced before being
frozen into contract text, surviving a second review round whose own stated
method ("trace it, don't trust it") was applied correctly to an adjacent
finding (PF-9) but not to this one.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
finding here implicates a numbered heuristic.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly). Budget: measured 3.09s against a 900s/0.3 CPU-hour budget,
roughly two orders of magnitude under — confirmed via `manifest.yaml`, no
concern. GD-12's fix (a superseding function plus a corrected cross-check
re-run on already-archived `delta_map` data) is zero new search cost, no
new graph build beyond what this batch already performed.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly
stated and not exceeded. `objective_boundary`'s scoping of Part B as a
diagnostic, not a claim, is correctly stated and not contradicted by
anything in the run package or this review — GD-12's finding does not
convert Part B into a claim, and does not itself constitute evidence for or
against a computable delta_E-gradient.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level
gradient-existence screen, not a proof-oriented proposal. Attacked and held,
same verdict as every prior review in this lineage. Separately: GD-12 itself
is a proof-architecture failure one level up — an unconditional equivalence
claim asserted in review prose without the "boundary and strictness"
discipline (`docs/inventor-protocol.md` section 8, attack 3) ever being
applied to it by checking a concrete boundary case (the delta=1 vertex) or a
concrete multi-step case (a walk of length >0) before freeze.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-e` as committed at `a686f170`, against
`specification_v5.yaml` frozen at `59cfaf39`: PART A's fix and its two
required regression tests are genuinely correct and independently
re-confirmed by direct re-execution (not merely re-read), producing a real,
non-artifactual contrast against the frozen, unmodified originals. PART B's
graph rebuild, coverage assertion, and structural local-minimum fractions
(0.41–0.47 per prime) are independently confirmed correct, including a
bit-identical reproduction of the archived `greedy_trapped_fraction` for one
prime that supports exact-adjacency-reproduction, not merely
same-size/same-degree. PART B's required exhaustive cross-check genuinely
fails on all four primes for the reason the Executor's `PD-SPEC-1` disclosure
names (a start-vs-terminal comparison-target error in the frozen contract's
own operational text, not a coding bug) — independently reconfirmed via a
fresh counter-example on a different vertex and prime — **and for a second,
independent reason PD-SPEC-1 does not identify**: every F_p-rational
(delta=1) vertex disagrees for a distinct boundary-condition reason
unrelated to the start-vs-terminal issue, which any future fix must handle
separately. This is a genuinely new defect category (recommend GD-12), not a
restatement of GD-6/GD-9/GD-10/GD-11, and it does not affect PART A or the
structural local-minimum fractions' validity. Given campaign_budget is now
exhausted at 8/8 batches with no completion criterion met and L4 still
genuinely open, `closed_at_budget` with the corrected cross-check as the
named resume action is the accurate, honest terminal status for this batch —
not `paused` understating a met criterion (none was met) and not a request
to bypass the declared hard budget.

## Next concrete action

Coordinator: (1) name GD-12 in `goal.yaml` per Front 2's category, with the
standing repair attached (any pre-freeze finding's unconditional equivalence
claim requires an executed concrete trace before being written into frozen
contract text); (2) move `GOAL-SSIQ-001` to `closed_at_budget` (campaign_budget
exhausted, no completion criterion met, L4 explicitly not retired), recording
this batch's ranked resume action (Front 5) as the successor/revisit
condition required by AGENTS.md rule 9; (3) if/when this goal is
re-approved or extended, the first task should supersede
`greedy_descent_hitting_time` to expose the terminal vertex and re-run a
corrected cross-check (restricted to `trapped: True` walks, excluding the
delta=1/success case) against the same four primes' already-archived
`delta_map` — zero new search cost; (4) supersede or annotate
`specification_v5.yaml`'s own PF-6 text so a future reader of the frozen
contract (not just the run package) does not inherit the false
"conclusively a bug... unconditionally" claim.

## Overall verdict

**CHALLENGE (upheld and extended).** PD-SPEC-1's diagnosis is independently
confirmed correct as far as it goes, via a fresh counter-example on
different data than the Executor used — but it is incomplete: a second,
independent boundary-condition source of disagreement (the delta=1/success
convention) is identified here for the first time, with the operational
consequence that the Executor's own suggested fix path is insufficient
without also excluding that case. This is recommended as a new defect
(GD-12), distinct from GD-6/GD-9/GD-10/GD-11. PART A and the structural
local-minimum fractions are independently confirmed valid and unaffected.
Given this is the last batch inside GOAL-SSIQ-001's declared 8-batch
campaign_budget, `closed_at_budget` — not `paused`, and not a request to
bypass the budget — is the accurate terminal status, with the corrected
cross-check as the concrete, zero-new-search-cost resume action.

```yaml
red_team_report:
  id: RT-BATCH-008
  task_id: TASK-20260806-bf15ab
  claim_under_review: >-
    Coordinator-committed snapshot a686f170 (parent 59cfaf39), receipt
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/archives/TASK-20260806-bac693-receipt.yaml,
    covering RUN-SSIQ-a85692-e under EXP-SSIQ-a85692's v5 amendment
    (specification_v5.yaml, frozen after two pre-freeze review rounds): PART A
    (GD-11's fix, ols_hardened.py) reported passing; PART B (the
    trapping-mechanism diagnostic) reported its own frozen-contract-required
    exhaustive cross-check FAILED on all four primes (93-267 disagreements),
    which the Executor (PD-SPEC-1) diagnosed as a defect in the contract's
    own text (comparing the walk's "trapped" flag against the START vertex,
    not the TERMINAL vertex) rather than a bug in its own code.
  objections:
    - "OBJ-1: The frozen spec's PF-6 cross-check compares is_structural_local_min(start) against trapped, but the underlying proof (PF-6, which I authored in round 1 of this amendment's own pre-freeze review) correctly establishes the equivalence for the walk's TERMINAL vertex only. Independently reconfirmed by direct execution on a DIFFERENT vertex and prime than the Executor's own example: p=3889, vertex (58,996), delta=11, neighbour deltas [4,3,3] (not itself a local min); walk descends one step (tie-broken) to (2330,514), delta=3, neighbour deltas [11,9,3] (genuine local min, trapped=True there). trapped(start)=True but is_structural_local_min(start)=False; is_structural_local_min(terminal)=True. PD-SPEC-1's core diagnosis CONFIRMED."
    - "OBJ-2 [NOT raised by the Executor's PD-SPEC-1]: A second, independent source of disagreement, decomposed by direct query of trapped_vs_structural_crosscheck.json against delta_map: exactly 9/18/18/17 of the 93/138/234/267 disagreements per prime are F_p-rational (delta_E=1) vertices, where start==terminal (0 steps, function short-circuits) yet trapped=False (the function's explicit design: reaching delta=1 is 'success,' never 'trapped') while is_structural_local_min=True trivially (delta=1 is the global minimum value by definition). This is NOT an instance of the start-vs-terminal bug -- it is a distinct boundary-condition defect in the same claimed equivalence. Verified exactly: 84+9=93 (2437), 120+18=138 (3889), 216+18=234 (5737), 250+17=267 (7333) -- the two sources exhaustively and exactly partition every disagreement on all four primes. Operational consequence: naively fixing only the start-vs-terminal issue (exposing and comparing against the terminal vertex for ALL walks) would newly misclassify every SUCCESSFUL walk (15-28% of vertices per prime, since 1-greedy_trapped_fraction = 0.163/0.278/0.180/0.149) as a disagreement too, since their delta=1 terminal is trapped=False but trivially is_structural_local_min=True. A correct fix must restrict the equivalence check to trapped:True walks only and exclude the delta=1/success case from the claim entirely."
    - "OBJ-3: PF-6's mathematical argument is correct in the abstract (re-confirmed above) but was never checked against a concrete, multi-step, hand- or code-traced example by either pre-freeze review round before being transcribed into frozen contract text as unconditional fact ('provably exact... for every vertex, unconditionally'). Direct grep confirms the literal phrase is_structural_local_min(start) appears in NEITHER pre-freeze review report -- it is the Coordinator's own concretization of round 1's ambiguous abstract argument ('the walk halts at w') into the frozen operational text, which silently equated w with the loop's start vertex (the same iteration variable run_population already uses). Round 2 reviewed this exact frozen text and wrote 'CONFIRMED APPLIED AND ADEQUATE... still correct' without re-tracing a concrete multi-step example -- the SAME review round that DID apply exactly this 'trace it, don't trust it' discipline to an adjacent finding (PF-9, by directly querying real archived data). This is a genuinely new defect category, distinct from GD-6 (re-read failure), GD-9/GD-10 (validation artifact that doesn't call/exercise the right function -- here the check DID call the real function and DID fail loudly and correctly), and GD-11 (floating-point numerical robustness -- unrelated mechanism). Recommend naming GD-12: 'an unconditional mathematical claim asserted with high confidence in review prose, transcribed into frozen contract text as fact, whose concretization into an executable check silently mis-targeted the quantifier -- never checked against a concrete trace by either pre-freeze review round.'"
    - "OBJ-4: specification_v5.yaml's frozen text remains uncorrected and still asserts the false 'conclusively a bug in this amendment's own code... never a mechanism finding' claim as unconditional fact. A future producer reading the frozen spec directly (rather than the run package + this review) could be misled into re-deriving or trusting the same false framing."
  required_controls:
    - "A superseding version of greedy_descent_hitting_time (by addition, not edit, per this campaign's own ols_hardened.py precedent for GD-11) must expose the walk's terminal vertex before any corrected cross-check can run."
    - "The corrected cross-check must restrict the equivalence claim to trapped:True walks only, comparing is_structural_local_min(terminal); it must explicitly exclude trapped:False (delta=1/success) outcomes from the claim rather than silently including them, per OBJ-2's finding."
    - "Any future pre-freeze finding asserting an unconditional equivalence, invariant, or 'provably exact' claim as the justification for a required check must be accompanied by an executed, concrete trace of at least one non-trivial instance (and, per OBJ-2, at least one boundary-condition instance) before being written into frozen contract text -- the standing repair recommended for GD-12."
  counterexample_or_mutation: >-
    Start-vs-terminal (p=3889, vertex (58,996), independently executed, not
    from any prior report): greedy_descent_hitting_time returns trapped=True,
    steps=1, walk's actual terminal (2330,514) has neighbour deltas [11,9,3]
    (is_structural_local_min(terminal)=True, confirming PF-6's real claim);
    but is_structural_local_min((58,996))=False (neighbour deltas [4,3,3], a
    strictly smaller neighbour exists) -- falsifies "trapped(start) <=>
    is_structural_local_min(start), unconditionally."
    Delta=1 boundary (p=3889, vertex (332,0), independently executed):
    greedy_descent_hitting_time returns trapped=False, steps=0 (start ==
    terminal, short-circuited by the function's own delta=1 special case);
    but is_structural_local_min((332,0))=True trivially (neighbour deltas
    [1,4,4], delta=1 is the global minimum) -- falsifies the same
    "unconditional" claim by a SECOND, independent mechanism, orthogonal to
    the start-vs-terminal issue and not identified by the Executor's
    PD-SPEC-1.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline is this
    campaign's own instrument- and fix-scrutiny discipline (GD-4 through
    GD-11, PF-9's "trace a prior review's own prose, don't trust it"): OBJ-2/
    OBJ-3 extend that discipline one further step, to a reviewer's own
    mathematical argument (mine, in round 1 of this amendment's pre-freeze
    lineage), asserted with high confidence and never concretely traced
    before being frozen into contract text, surviving a second review round
    whose own stated method was applied correctly to an adjacent finding
    (PF-9) but not to this one.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere (asymptotic_claim: null, correctly). Measured wall-clock 3.09s against a 900s/0.3-CPU-hour budget, roughly two orders of magnitude under -- confirmed via manifest.yaml."
    - "GD-12's recommended fix (a superseding terminal-vertex-exposing function plus a corrected, correctly-scoped cross-check re-run on already-archived delta_map data for the same four primes) is zero new search cost and requires no new graph build beyond what this batch already performed."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "objective_boundary's scoping of Part B as a diagnostic, not a claim, is correctly stated and not contradicted by anything in the run package or this review -- GD-12's finding does not convert Part B into a claim and does not itself constitute evidence for or against a computable delta_E-gradient."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
    - "GD-12 itself is a proof-architecture failure one level up (docs/inventor-protocol.md section 8, boundary-and-strictness attack): an unconditional equivalence claim asserted in review prose without ever being checked against a concrete boundary case (the delta=1 vertex, OBJ-2) or a concrete multi-step case (a walk of length >0, OBJ-1) before freeze."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-e as committed at a686f170, against
    specification_v5.yaml frozen at 59cfaf39: PART A's fix and both required
    regression tests are genuinely correct and independently re-confirmed by
    direct re-execution, producing a real, non-artifactual contrast against
    the frozen originals (Front 3, Front 6). PART B's graph rebuild, coverage
    assertion, and structural local-minimum fractions (0.41-0.47 per prime)
    are independently confirmed correct, including a bit-identical
    reproduction of the archived greedy_trapped_fraction for prime 2437
    (Front 4). PART B's required exhaustive cross-check genuinely fails on
    all four primes for the reason PD-SPEC-1 names (a start-vs-terminal
    comparison-target error in the frozen contract's own text) --
    independently reconfirmed on different data -- AND for a second,
    independent reason PD-SPEC-1 does not identify (OBJ-2): every
    F_p-rational vertex disagrees for a distinct boundary-condition reason.
    This is recommended as a new defect (GD-12), distinct from
    GD-6/GD-9/GD-10/GD-11, and does not affect PART A or the structural
    local-minimum fractions' validity. Campaign_budget is exhausted (8/8
    batches) with no completion criterion met and L4 explicitly not retired;
    closed_at_budget with the corrected cross-check as the named,
    zero-new-search-cost resume action is the accurate terminal status --
    not paused understating a met criterion (none was met), and not grounds
    to bypass the declared hard budget.
  next_concrete_action: >-
    Coordinator: (1) name GD-12 per Front 2/OBJ-3's category, with the
    standing repair attached (any pre-freeze finding's unconditional
    equivalence claim requires an executed concrete trace, including a
    boundary-condition instance, before being written into frozen contract
    text); (2) move GOAL-SSIQ-001 to closed_at_budget (campaign_budget
    exhausted, no completion criterion met, L4 explicitly not retired),
    recording Front 5's ranked resume action as the successor/revisit
    condition required by AGENTS.md rule 9; (3) on re-approval/extension,
    first task supersedes greedy_descent_hitting_time to expose the terminal
    vertex and re-runs a corrected cross-check (restricted to trapped:True
    walks, excluding the delta=1/success case per OBJ-2) against the same
    four primes' already-archived delta_map -- zero new search cost; (4)
    supersede or annotate specification_v5.yaml's own PF-6 text so a future
    reader of the frozen contract does not inherit the false "conclusively a
    bug... unconditionally" claim.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-BATCH-008.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Executed directly (not merely traced): rebuilt the 2-isogeny graphs for
    primes 2437 and 3889 from scratch via build_isogeny_graph.build_graph_bfs
    (seed 20260805, matching the pinned convention) and loaded
    RUN-SSIQ-a85692-b/raw-result.json's real delta_map for both primes.
    Called the frozen, unmodified greedy_descent_hitting_time directly on
    two vertices not used in the Executor's own counter-example ((58,996)/
    3889 and (332,0)/3889), tracing both by hand and by direct execution,
    confirming the walk's terminal vertex and its neighbour deltas against
    is_structural_local_min computed independently from delta_map + rebuilt
    adjacency. Cross-referenced trapped_vs_structural_crosscheck.json's full
    disagreement lists against delta_map for all four primes, decomposing
    every disagreement into two exhaustive, exactly-partitioning buckets (OBJ-1
    vs OBJ-2 mechanisms) and confirming the F_p-rational-vertex-count bucket
    matches the delta=1 count exactly on all four primes. Independently
    re-executed both of PART A's required regression-test cases from
    scratch (not read from JSON), reproducing gamma=-0.5/0.5 for the
    original guard and None/None (0 valid draws) for the hardened guard,
    bit-identical to the archived bootstrap_gap_ci_v2_regression_test.json,
    and additionally traced the floating-point mechanism producing exactly
    -0.5 (xbar's 1-ULP deviation from a repeated identical float) to rule out
    a rigged test construction. Independently recomputed
    n_structural_local_min (95/203=0.467980, prime 2437) and the population-
    wide greedy_trapped_fraction (0.8374384236453202) from the rebuilt graph
    and real delta_map, both bit-identical to the archived/reported values.
    Directly grepped both pre-freeze review reports and specification_v5.yaml
    for the literal string "is_structural_local_min(start)" to establish it
    appears only in the frozen spec, not in either review's own prose. No
    file written outside this report; no run artifact, specification file,
    or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-BATCH-008.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v5.yaml and every
    run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
