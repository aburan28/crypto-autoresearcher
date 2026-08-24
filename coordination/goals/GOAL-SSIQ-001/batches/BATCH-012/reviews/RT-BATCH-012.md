# RT-BATCH-012 — Red Team review of RUN-SSIQ-a85692-i (EXP-SSIQ-a85692 v9),
# GOAL-SSIQ-001 BATCH-012 (the truncation-mutation control named by
# RT-BATCH-011's own "Counterexample or mutation")

**Reviews the Coordinator-committed snapshot at `1aa1c37f` (parent `d729af05`,
the frozen `specification_v9.yaml` after two pre-freeze review rounds),
covering `RUN-SSIQ-a85692-i`.** Per this task's operating rules, only this
Coordinator-committed snapshot is treated as durable input; the round-1/round-2
pre-freeze findings (PF-1 through PF-5) and RT-BATCH-011's own findings are not
re-litigated. All numeric claims below were independently recomputed from the
raw committed JSON, not taken from `execution_report.yaml`'s or the
Coordinator's own commit-message summaries; two small local, non-durable,
read-only Python computations were run directly against the committed
`truncation_probe_comparison.json`, `RUN-SSIQ-a85692-b/raw-result.json`, and
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json` — no run artifact,
specification, or ledger record was written or modified.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified this session.
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs model: inherit. Standing condition
    for this lineage, not re-discovered here.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. Shares a model family
    with the Executor, the Coordinator, and every prior reviewer in this
    lineage. Does not upgrade the campaign's evidence tier and does not itself
    satisfy or advance a closure quorum. A Validator is reviewing the same run
    independently and in parallel; produced without coordinating with it.
```

---

## Bottom line up front

**The run is executed exactly as `specification_v9.yaml` requires, and both
the Executor's `execution_report.yaml` and the Coordinator's commit message
already disclose the small-sample limitation honestly — neither asserts that
`0/8` confirms or falsifies RT-BATCH-011's boundary prediction. That
restraint is correct, because the restraint needs to be much stronger than a
generic "small sample" caveat: the 8 resolved vertices are not merely few,
they are a highly non-representative, internally correlated subsample drawn
from the extreme tail of the value distribution, and the "194/194 timed out"
headline is itself close to a foreseeable arithmetic consequence of data
already in the frozen spec's own text, not a surprising discovery about the
algorithm.** Concretely, three independent problems compound to make this
run's `0/8`/`0/17` finding almost uninformative about the question v9 was
built to answer:

1. **Raw statistical power is very weak even taking the 8 vertices at face
   value.** Exact Clopper–Pearson: observing 0 differences in 8 independent
   Bernoulli trials rules out a true per-vertex difference probability above
   only **31.2%** at 95% confidence (`1 − 0.05^(1/8) = 0.3125`), and above
   **25.0%** at 90% confidence. The 10–30% range this task named as a
   plausible "moderate true difference rate" is almost entirely *inside* the
   confidence interval this result leaves open, not excluded by it. At
   p=0.15 (a modest true difference rate), `0/8` would occur with probability
   `0.85^8 = 27.3%` — not a rare event by any convention.

2. **The 8 vertices are not 8 independent draws — they are 4 Frobenius-
   conjugate PAIRS, which halves the effective sample further.** I traced
   `build_isogeny_graph.py:119` (`frobenius(x) = (x[0], (-x[1]) % p)`, exact
   complex conjugation `(a,b) → (a, p−b)`) against the 8 resolved vertices in
   `per_vertex_records` and confirmed directly: `(59,422)`/`(59,2015)`,
   `(90,762)`/`(90,1675)`, `(490,674)`/`(490,1763)`, and
   `(756,344)`/`(756,2093)` are each an exact `p−b` conjugate pair
   (`2437−422=2015`, `2437−762=1675`, `2437−674=1763`, `2437−344=2093`).
   Since `two_sided_search`'s own target is `field.frobenius(v)`
   (`delta_e_truncation_probe_v9.py:177`), vertex `v`'s search and vertex
   `frobenius(v)`'s search are literally mirror images of the *same*
   source/target table pair with source and target roles swapped — the
   identical minimum-degree-product problem run twice under a genuinely
   symmetric construction. Recomputing the 95%-confidence power bound on the
   more defensible **4 independent pairs** rather than 8 raw records gives
   `1 − 0.05^(1/4) = 52.7%`: at this sample's actual independence structure,
   a true difference rate as high as roughly one-in-two truncated,
   conjugate-paired vertices would still be fully consistent with the
   observed `0/8`.

3. **The 8 resolved vertices are also drawn from the single most degenerate
   value in the whole distribution, not a representative sample of "hard"
   cases — and this is a mechanism-level selection effect, not luck.** I
   pulled `RUN-SSIQ-a85692-b`'s full archived `delta_map` for p=2437 (203
   entries) and its value histogram over the 194 non-F_p-rational vertices:
   `δ=2`: 34/194 (17.5%), `δ=3`: 70/194 (36.1%, the *most common* value),
   `δ=4`..`δ=8`: the remaining 46.4%. **All 8 vertices this run resolved have
   `delta_e_upper_bound == 2`** — the smallest nontrivial value the search
   space admits (the 9 F_p-rational vertices are wired to 1 unconditionally
   and are not part of this population) — **and zero resolved with `δ=3`,
   the modal value that is more than twice as common in the true
   population.** `build_smooth_table` (`compute_delta_e.py:144-174`) is a
   strict best-first, lowest-degree-first Dijkstra expansion with no
   incremental collision check (both the source and target tables are always
   built to their own full half-budget before any intersection is computed —
   confirmed directly: every one of the 8 resolved vertices' `wall_seconds`
   is 0.50–0.54s, statistically indistinguishable from the 186 *unresolved*
   vertices' 0.50–0.57s range, so "resolved" here does **not** mean "found
   fast"; it means the two independently-truncated partial tables happened
   to already contain the globally-shallowest, lowest-degree common vertex by
   the time both half-budgets expired). This is exactly the selection
   mechanism this task's Adversarial Question 2 hypothesized, but sharper
   than "easiest/fastest": the resolved sample is not biased toward vertices
   the search finishes early on (no vertex finishes early under this design),
   it is biased toward vertices whose *true answer is the smallest value the
   metric can take*, which is close to definitionally the value least likely
   to be perturbed by any truncation-driven RNG effect, since it is
   discoverable within the first few heap-pops of best-first expansion on
   both sides.

Given all three, my verdict is **CHALLENGE (narrow)**: no objection to
execution fidelity, cost/budget honesty, or `OBJECTIVE_BOUNDARY` compliance —
all clean, verified by direct artifact and code read. The objection is to
**how this run may be cited going forward**: even a carefully-worded citation
like "truncation did not reopen the value-difference channel, `0/8`,
consistent with the determinism argument" overstates what this specific
8-vertex, 4-pair, all-`δ=2` sample can support. The narrowest correct
statement is that **this run is inconclusive** on RT-BATCH-011's boundary
question — not confirmatory of either of RT-BATCH-011's two named outcomes —
and a genuinely powered test of the boundary condition has not yet been run.

---

## Front 1 — Adversarial Question 1: statistical power, worked precisely

Treating the 8 resolved non-F_p-rational vertices as independent Bernoulli
trials with unknown true per-vertex difference probability `p` (RT-BATCH-011's
predicted channel: budget truncation making the returned `delta_e_upper_bound`
depend on RNG-driven timing variance in which partial-table entries get built
before the 0.5s cutoff), the exact one-sided Clopper–Pearson 95% upper
confidence bound for observing 0 successes in `n` trials is
`p_upper = 1 − α^{1/n}`:

| n (unit)         | 95% upper bound on p | 90% upper bound on p |
|-------------------|----------------------|----------------------|
| 8 (raw vertices)  | 31.2%                | 25.0%                |
| 4 (conjugate pairs, Front-2 finding) | 52.7% | 40.9% |

And forward probabilities of observing `0/8` under specific hypothetical true
rates: `p=0.10 → 43.0%`, `p=0.15 → 27.3%`, `p=0.20 → 16.8%`, `p=0.30 → 5.8%`.
**None of these are improbable events.** A true difference rate anywhere in
the 10–30% range this task named as the discriminating hypothesis would
produce `0/8` a substantial fraction of the time by chance alone; the
observed result cannot distinguish "PF-6's channel is genuinely closed even
under truncation" from "PF-6's channel reopens at a real but moderate rate
that this sample was too small (and too correlated, Front 2) to catch."

## Front 2 — Adversarial Question 2: selection effect, traced concretely (not
## merely hypothesized)

Two independent, directly-demonstrated biases apply, both narrowing what
`0/8` can mean, in different ways than this task's framing anticipated:

**(a) Not a "fast/easy" bias in the timing sense the task's framing
suggested.** `two_sided_search` does not check for a collision incrementally;
each side's `build_smooth_table` always consumes its *entire* allotted
half-budget (or the remaining budget for the second call) before the
intersection is computed once, at the end. I confirmed directly from
`per_vertex_records`: the 8 resolved vertices' `wall_seconds` range
0.50172–0.54235s; the 186 unresolved vertices' range 0.50023–0.57327s.
These ranges overlap almost entirely — resolved vertices did **not**
terminate meaningfully earlier than unresolved ones. Any report or future
citation using language like "resolved quickly" or "found fast" (the
Executor's own `OBS-2` anomaly text uses "surfacing small-degree collisions
fastest," which is imprecise in this specific sense — worth a corrective note
if reused) should be corrected: nothing about this design lets a vertex exit
early.

**(b) A real, mechanism-level, and value-extreme bias.** Against the full
archived `delta_map`'s own value histogram for the 194 non-F_p-rational
vertices at p=2437 (`δ=2`: 34/194=17.5%, `δ=3`: 70/194=36.1% — the modal
value — `δ≥4`: 90/194=46.4%), **100% of this run's 8 resolved vertices have
`δ=2`, and 0% have `δ=3`, despite `δ=3` being twice as common in the true
population.** `build_smooth_table`'s strict best-first (lowest-product-degree-
first) expansion order (`compute_delta_e.py:144-174`, min-heap on `(degree,
vertex)`) means a vertex whose true minimal collision degree is the smallest
achievable value is discoverable in the fewest heap-pops on both sides
simultaneously — the one scenario where a severely truncated partial table on
*both* sides is still likely to already contain the answer. This is not
"luck": it follows from the algorithm's own design, is directly checkable
against the archived ground truth (done above), and predicts that as budget
shrinks further, the resolved subsample would skew even harder toward `δ=2`,
and as budget grows toward the natural ~1.15–1.70s completion range it would
converge back toward the true population mix. **This is a testable,
falsifiable prediction a follow-up sweep across budgets could directly
confirm** (see Next concrete action).

**(c) A second, previously-undocumented correlation: the 8 resolved vertices
are 4 exact Frobenius-conjugate pairs**, not 8 independent draws (traced in
Bottom line point 2, `frobenius(x) = (a, p−b)` confirmed against
`build_isogeny_graph.py:119`, and matched exactly against all 8 vertex
tuples). Because `two_sided_search(v, frobenius(v))` and
`two_sided_search(frobenius(v), v)` are the identical minimum-degree-product
problem with source/target swapped, a systematic (rather than purely random
per-vertex) truncation effect would be expected to move both members of a
pair together, not independently — further reducing the effective
information content of `n=8` down toward `n=4`.

Together, (a)+(b)+(c) mean this is not merely "a small sample" in the generic
sense the task's framing anticipated (and which the Executor's own honest
disclosure already flagged) — it is a **small, degenerate-value, correlated**
sample, specifically the subpopulation *least* likely to be perturbed by the
truncation mechanism under test, drawn via a traceable structural property of
the search algorithm rather than chance.

## Front 3 — Adversarial Question 3: what does "194/194 timed out" say on its
## own?

Two things, one honesty-framing correction and one genuine confirmation:

**(a) "Far more severe than anticipated" is a fair description of the
deviation from the spec's own *prose* prediction ("some or most vertices"),
but the underlying arithmetic fact was largely foreseeable from data already
cited in the frozen spec's own budget-justification text, not a new
discovery about the algorithm.** `RUN-SSIQ-a85692-h`'s own committed
`per_vertex_records` (read directly) show a **minimum** full, non-truncated
two-sided completion time of **1.14993s** across all 194 vertices — already
more than double the v9 amendment's entire 0.5s per-vertex budget, before any
split between source-half and target-half is considered. Given
`two_sided_search` never checks the other side's table before both halves
individually exhaust their allotted time, and every single vertex needed at
least 1.15s to complete both halves naturally, near-total timeout
(`n_timed_out ≈ 194/194`) was close to the only arithmetically plausible
outcome, not a genuine surprise the algorithm's behavior revealed. This
tempers, without contradicting, the Coordinator's disclosed characterization
— the deviation from the spec's own *text* ("some or most") is real and
correctly disclosed, but should not be read as evidence the algorithm behaved
unpredictably; it is evidence the pre-freeze review's own "some or most"
expectation did not fully draw out the implication of the completion-time
data it had already cited.

**(b) One genuine, useful confirmation: `resolved` and `timed_out` are not
mutually exclusive by design** (`two_sided_search`, `compute_delta_e.py:194,
208`: `resolved = len(common) > 0` computed after both possibly-truncated
tables are built; `timed_out = bool(to_s or to_t)`), and this run's own data
is the first real-world evidence that this is not merely a theoretical
possibility — 8/194 vertices are simultaneously `resolved=True` and
`timed_out=True`. This validates that the boundary-condition design (a vertex
can produce a genuine, non-vacuous measured answer *from a truncated search*)
is mechanically sound and was genuinely exercised, which is the one part of
v9's premise this run does confirm cleanly.

## Front 4 — Adversarial Question 4: was the intended comparison actually
## exercised?

**No, not in the way the design intended, and this is the sharpest finding of
this review.** The amendment's stated purpose (`amendment_scope`,
`isolation_note` in `delta_e_truncation_probe_v9.py:377-385`) is to test
whether "a resolved-at-0.5s vertex's value differs from ITS OWN
identical-RNG, larger-budget counterpart" — i.e., whether a search that
resolves *despite* truncation nonetheless converges to a *different* answer
than the same seed given full budget. Front 2(b) shows this question was
essentially never put to the test: the only vertices that resolved at 0.5s
are exactly the ones whose answer (`δ=2`, the globally smallest achievable
value) is locked in within the first few best-first heap-pops on both sides —
almost by construction, values this shallow are discoverable at *any*
non-trivial budget, truncated or not, which is precisely why they would be
expected to agree with the full-budget answer regardless of whether RNG-
driven timing variance is a live effect. The 186 vertices whose true answer
requires deeper exploration — the cases where a genuinely different partial
table (shaped by timing-variance-driven differences in how far the best-first
expansion got before cutoff) could plausibly diverge from the full-budget
answer — are exactly the vertices that produced **no data at all** under this
budget. The "197 vertices reused identical RNG, different budget" design is
real and correctly isolates budget as the sole manipulated variable
(confirmed: `BASE_SEED`, `derive_per_vertex_seed` are verbatim identical to
v8, `git diff --stat HEAD` shows zero changes to any prior implementation
file) — but the budget cut turned out so severe that it mostly just prevented
resolution rather than probing the resolved-but-truncated-vs-complete
divergence question it was built to answer.

## Front 5 — OBJECTIVE_BOUNDARY, honesty, and PF-5 (Adversarial Questions 7–8)

**OBJECTIVE_BOUNDARY: clean.** `raw-result.json`'s `objective_boundary` field
verbatim states this is a "DESCRIPTIVE DIAGNOSTIC CONTROL, not a claim,"
explicitly disclaims a PERSISTS/WEAKENS label, `H-SSIQ-36e970`'s real-arm
prediction, and cryptographic-scale transfer. Confirmed: neither
`raw-result.json` nor `truncation_probe_comparison.json` contains an
`outcome` field of PERSISTS/WEAKENS vocabulary anywhere, and `execution_report
.yaml`'s `OBS-3`/`OBS-4`/`ANOM-2`/`executor_assessment` all explicitly
disclaim drawing a conclusion "about which of RT-BATCH-011's two named
outcomes this measurement supports," deferring to the Coordinator and
reviewers. No lever L4 or H-SSIQ-36e970 claim anywhere. Clean.

**Honesty on the small-sample limitation: already disclosed, correctly, by
both the Executor and the Coordinator.** `execution_report.yaml`'s `ANOM-2`
explicitly states "this comparison's own statistical power is
correspondingly small — disclosed explicitly rather than left implicit," and
the Coordinator's own commit message states the small sample "materially
limits what this run alone can support statistically." Neither overclaims.
This review's contribution is to make that limitation **quantitative and
mechanistic** (Fronts 1–2) rather than leave it at "small sample, be
careful," ahead of any future citation of this run in an `EV-*`/`DEC-*`
record — no such record exists yet (checked: no `ledger/` file references
`RUN-SSIQ-a85692-i`).

**PF-5 failure-isolation: genuinely implemented and genuinely exercised on
its success path, verified by direct code read, not by trusting
`comparison_2_error: null`.** I read `delta_e_truncation_probe_v9.py:519-538`
directly: PART A's result and Comparison 1 are captured into local variables
(`part_a_result`, `comparison_1`) before Comparison 2's `try:` block begins
(lines 476-511 precede 519); the `try:` wraps both `parse_v8_new_delta_map`
and `compare_against_v8` under a bare `except Exception as e`, which sets
`comparison_2_error` and does not re-raise. I independently confirmed
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`'s top-level `new_delta_map`
field exists (203 string-keyed entries, e.g. `"[1031, 1095]": 5`) and that
`parse_v8_new_delta_map`'s `tuple(json.loads(key_str))` round-trip against
those 203 real keys produces 203 distinct tuples with no collision (matching
`ANOM-NONE-COMPARISON-2-FAILURE`'s own claim). `comparison_2_error: null`
therefore genuinely means "the code path was reached, ran, and succeeded" —
not "the field was never wired up." The one thing this run's data cannot
confirm is whether the `except` branch itself, if triggered, would correctly
preserve PART A's and Comparison 1's results in the written artifact (the
architecture makes this look correct on inspection — `comparison_payload` is
built incrementally with `if part_a_result is not None:` / `if comparison_1
is not None:` guards independent of the Comparison-2 try/except, so a
Comparison-2 exception cannot discard already-computed PART A results — but
this remains disclosed-but-unexercised on an actual failure this run, exactly
as `ANOM-NONE-COMPARISON-2-FAILURE` states).

---

## Objections

- **OBJ-1**: None on execution fidelity, budget honesty, or
  `OBJECTIVE_BOUNDARY` compliance. Graph-identity re-verification passed
  (203/203, degree-sequence check clean); `BASE_SEED`/`derive_per_vertex_seed`
  confirmed byte-identical to v8 by direct code read; total wall-clock
  101.46s of 600s (16.9%), consistent across `raw-result.json`, `manifest
  .yaml`, and `execution_report.yaml` to full float precision.
- **OBJ-2 (Front 1)**: `0/8` (equivalently `0/17` including the trivially-
  matching F_p-rational vertices) has weak statistical power against
  RT-BATCH-011's own named hypothesis. Exact 95% Clopper–Pearson bound rules
  out only a true per-vertex difference rate above 31.2% (8 raw vertices) or
  52.7% (4 independent conjugate pairs, OBJ-3). The 10–30% range this task
  named as a plausible moderate signal is not excluded.
- **OBJ-3 (Front 2c)**: The 8 resolved vertices are 4 exact Frobenius-
  conjugate pairs (`(a,b)`/`(a,p−b)`, directly verified against
  `build_isogeny_graph.py:119`'s `frobenius` implementation and all 8 vertex
  tuples in `per_vertex_records`), not 8 independent trials — this run's own
  design (`target = field.frobenius(v)`) makes each pair a mirrored instance
  of the same source/target problem, further reducing effective sample size.
- **OBJ-4 (Front 2b)**: The resolved sample is drawn overwhelmingly from the
  extreme tail of the value distribution (100% at `δ=2`, the smallest
  nontrivial achievable value, vs. 17.5% of the true archived population;
  0% at `δ=3`, the modal true value at 36.1%) — a directly-demonstrated,
  mechanism-level selection effect (best-first, lowest-degree-first table
  expansion) rather than a chance artifact of "the fastest 8 to finish"
  (`wall_seconds` for resolved vs. unresolved vertices overlap almost
  entirely, 0.50–0.54s vs. 0.50–0.57s — nothing here terminates early).
- **OBJ-5 (Front 4)**: Because of OBJ-4, this run's core design intent — does
  a resolved-but-truncated search find a *different* answer than the same
  seed given full budget — was essentially never tested. The vertices that
  could show such a divergence (larger-δ, deeper-search cases) are precisely
  the 186 that produced no data at all.
- **OBJ-6 (Front 3a, advisory, framing only)**: "Far more severe than the
  frozen contract anticipated" (Coordinator's commit message,
  `execution_report.yaml`'s `ANOM-1`) is a fair description of the gap from
  the spec's own prose ("some or most vertices"), but the underlying fact —
  near-total timeout — was close to arithmetically inevitable given
  `RUN-SSIQ-a85692-h`'s own committed minimum full-completion time
  (1.14993s, more than double the 0.5s budget) already cited in the frozen
  spec's own budget-justification text. This does not change what the run
  supports; it is a note for how future amendments should read their own
  completion-time citations before setting an "expected" truncation
  fraction.
- **OBJ-7 (minor, precision)**: `execution_report.yaml`'s `OBS-2` attributes
  the resolved sample to `two_sided_search`'s design "surfacing small-degree
  collisions fastest." Per Front 2a, "fastest" is not supported by the wall-
  clock data (resolved and unresolved vertices consume statistically
  indistinguishable wall time); the correct mechanism is fewest-heap-pops-
  to-discover, not early wall-clock termination. Worth a corrective note if
  this framing is reused in a future spec or evidence record.

## Required controls

- **A follow-up truncation-mutation run at an intermediate per-vertex budget,
  strictly between 0.5s and the observed 1.14993s minimum full-completion
  time** — e.g. 0.8s or 0.9s. This stays below every observed full-completion
  time (so genuine truncation is preserved on most/all vertices, avoiding
  RT-BATCH-011's original problem of never truncating) while being large
  enough to plausibly pull in vertices with `δ≥3` and break the current
  `δ=2`-only degeneracy, directly testing Front 2(b)'s prediction that the
  resolved-value mix should shift toward the true population distribution as
  budget grows. This is the single most informative and cheapest next
  action, and is explicitly what this task's own final question asked for.
- **A budget sweep (0.6s, 0.8s, 1.0s), not a single point**, would let the
  Coordinator observe `n_resolved` and the resolved-value distribution as a
  genuine dose-response curve against budget, rather than one more single
  small-N sample at a different fixed point.
- **Before any future citation treats the conjugate-pair vertices as
  independent evidence**, either report `n_value_differs` per-pair
  (deduplicating conjugate partners) alongside the raw per-vertex count, or
  explicitly disclose the pairing and its effect on effective sample size —
  matching this run's own `non_fp_rational_only` sub-breakdown convention of
  never hiding a domain choice that changes what a count means.

## Counterexample or mutation

The cheapest concrete mutation that would separate "the `δ=2`-only resolved
sample is representative of what a larger truncation budget would show" from
"it is a degenerate artifact of best-first search order": rerun this
amendment's identical procedure at `PER_VERTEX_BUDGET_SECONDS = 0.8` (or any
value strictly between 0.5 and 1.14993). If the resolved-value distribution
at that budget remains dominated by `δ=2` far out of proportion to its 17.5%
population share, that would be a genuinely surprising result Front 2(b)'s
mechanism does not predict (worth investigating further — e.g., some
structural property of these 4 vertex-pairs beyond generic best-first order).
If it shifts toward the true population mix (more `δ=3`, `δ=4`, etc.
entering the resolved set as budget grows), that confirms the mechanism this
review traces and licenses treating a sufficiently-generous-but-still-
truncating budget as the correct instrument for RT-BATCH-011's boundary
question — which 0.5s, this run's own budget, was too severe to be.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale, single-prime search-procedure diagnostic work,
`H-SSIQ-36e970.asymptotic_claim: null` throughout, correctly inherited and
unchanged by this run. The relevant baseline is this campaign's own
instrument-scrutiny discipline (`RT-BATCH-009`/`RT-BATCH-010`/`RT-BATCH-011`'s
"trace it, don't trust it, bring your own control"), extended here from
auditing whether a comparison can discriminate a hypothesis at all
(RT-BATCH-011's contribution) to auditing whether an underpowered positive
instance of that comparison (this run) is being asked to bear more
evidentiary weight than its own sample size and internal correlation
structure can support — a distinct failure mode from RT-BATCH-011's
(near-certain null vs. genuinely-uninformative-small-null).

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty — unchanged by
this run, a search-procedure diagnostic rather than a heuristic-conditional
asymptotic claim. The one heuristic-shaped assumption worth naming, though
not one of `H-SSIQ-36e970`'s own numbered items: the frozen spec's own text
implicitly treats "the search resolves a vertex" and "the resolved value is
representative of what fuller search would find at that vertex" as
correlated in the helpful direction (i.e. that a resolved-under-truncation
answer is informative about truncation's general effect). Front 2(b) shows
this is backwards for this specific budget: resolution under 0.5s is
correlated with the *smallest, least truncation-sensitive* answers, not a
representative cross-section. Worth flagging explicitly if this design is
reused as a template.

## Cost model challenges

No asymptotic-cost claim anywhere in this run. Measured wall-clock
101.4591281414032s against a 600s/0.2 CPU-hour budget, matching
`raw-result.json`'s figure to full float precision across `manifest.yaml`,
`execution_report.yaml`, and `raw-result.json`; 16.9% budget utilization,
honestly reported. `execution_report.yaml`'s disclosed ~4.2% overshoot of the
97.0s worst-case *sub*-bound (101.03s measured PART A time) against the
soft-cap mechanism (PF-4) is correctly and un-defensively reported, and
remains comfortably within the 600s hard cap and the spec's own ~6.19x
margin. No objection.

## Reduction and scope challenges

No affected/safe cryptographic scheme list anywhere in this amendment;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated, not
exceeded. `raw-result.json`'s `objective_boundary` correctly restricts this
run to a purely descriptive measurement at p=2437 alone, explicitly excluding
`H-SSIQ-36e970`'s real-arm prediction, lever L4, and any PERSISTS/WEAKENS
vocabulary — verified by direct field read, not trusted from spec prose. No
scope inflation found in this run's own artifacts. This review's own
corrections (Fronts 1, 2, 4) are evidentiary-weight and statistical-power
corrections for future citation, not scope-inflation defects in what this
run itself claims — it currently claims nothing beyond measurement, correctly.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; a direct instrument-level
search-procedure diagnostic, not a proof-oriented proposal. Attacked and
held.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-i` as committed at `1aa1c37f` (parent `d729af05`),
against `specification_v9.yaml`: the run executes exactly as the frozen spec
requires (graph-identity re-verification passes 203/203; PART A ran on all
194 non-F_p-rational vertices under the fixed 0.5s budget with byte-identical
RNG seeds to v8; `n_resolved=8`, `n_timed_out=194/194` — every vertex hit the
cutoff on at least one table-build half, which `resolved`/`timed_out` are not
mutually exclusive by design and this run is the first to demonstrate this
concretely; `coverage_fraction=0.0412`; both REQUIRED COMPARISONS found
`n_value_differs=0` over the 17 vertices resolved (8 non-F_p-rational + 9
trivially-wired F_p-rational); `comparison_2_error: null` genuinely reflects
a successfully-executed, not merely dormant, code path, confirmed by direct
trace of `parse_v8_new_delta_map` against the real 203-key source file).
**What this run licenses, narrowly stated**: this is a genuine, honestly-
reported measurement that severe truncation (0.5s per vertex, ~2.3–3.4x below
observed natural completion) leaves 194/194 non-F_p-rational vertices with at
least one truncated table-build half, of which 8 nonetheless resolve a
collision, all at the smallest achievable value (`δ=2`) and forming 4 exact
Frobenius-conjugate pairs, all 8 matching both the archived and v8's own
values. **What this run does NOT license**: any statement that truncation
"does not reopen" or "confirms the boundary of" RT-BATCH-011's RNG-sharing
determinism argument — the observed `0/8` is statistically consistent (at
95% confidence) with a true divergence rate as high as 31% (raw count) to
53% (accounting for conjugate-pair correlation), and the specific 8 vertices
that did resolve are, by a directly-traced mechanism of the search algorithm
itself, exactly the subpopulation *least* likely to be sensitive to the
truncation effect under test. The correct status of RT-BATCH-011's boundary
question after this run is **still open / inconclusive**, not narrowed
toward either of RT-BATCH-011's two named outcomes — a materially different
status than "the determinism argument's boundary condition was tested and
held," which would be an overclaim this specific 8-vertex, 4-pair, all-δ=2
sample cannot support.

## Next concrete action

Coordinator, before drafting any `EV-SSIQ-*`/`DEC-*` record citing this run:
(1) accept `RUN-SSIQ-a85692-i`'s execution fidelity, cost/budget honesty, and
`OBJECTIVE_BOUNDARY` compliance as clean — no protocol deviation, no coverage
defect, PF-5 confirmed genuinely implemented and genuinely exercised on its
success path by direct code trace; (2) record this run's status as
**inconclusive**, not confirmatory, regarding RT-BATCH-011's own boundary
prediction — cite the exact power bounds above (31.2% raw / 52.7% pair-
corrected 95% CI) rather than a qualitative "small sample" caveat; (3) do not
cite `n_value_differs=0` as evidence the determinism argument extends into
the truncated regime — the resolved subsample is a mechanism-traced,
extreme-value, internally-correlated selection, not a representative probe
of the 186 vertices the boundary question actually concerns; (4) **the
single most informative and cheapest next action is a follow-up truncation-
mutation run at an intermediate per-vertex budget strictly between 0.5s and
the observed 1.14993s natural-completion floor** (e.g. 0.8s or 0.9s, or a
0.6/0.8/1.0s sweep) — high enough to plausibly pull non-`δ=2` vertices into
the resolved set and test Front 2(b)'s prediction directly, while staying
below every observed natural-completion time so genuine truncation is
preserved and RT-BATCH-011's original "never truncates" problem does not
recur; (5) this remains, exactly as `OBJECTIVE_BOUNDARY` states, a
single-prime descriptive diagnostic — no extension to `H-SSIQ-36e970`, lever
L4, PERSISTS/WEAKENS vocabulary, or any other prime is licensed by this run.

## Overall verdict

**CHALLENGE (narrow).** Execution fidelity, cost/budget honesty, and
`OBJECTIVE_BOUNDARY` compliance are all clean — no protocol deviation
found, and both the Executor's own report and the Coordinator's commit
message already, correctly, decline to draw a conclusion from this run about
RT-BATCH-011's boundary question. What this review adds, ahead of any future
`EV-*`/`DEC-*` citation: the `0/8` (`0/17`) null result is not merely
small-sample — it is drawn from a mechanism-traced, extreme-tail, internally
correlated (4 conjugate pairs, not 8 independent trials) subpopulation that
is close to definitionally immune to the truncation effect under test, and
its exact statistical power (95% CI up to 31–53% true divergence rate,
depending on independence assumption) leaves the 10–30% "moderate signal"
range this task named essentially untested. The correct status this run
supports is **inconclusive**, and the correct next step is a follow-up at an
intermediate budget (0.8–1.0s) designed to actually pull non-degenerate
values into the resolved set, not a same-budget rerun or a conclusion drawn
from this run alone.

```yaml
red_team_report:
  id: RT-BATCH-012
  task_id: TASK-20260806-30d8d3
  claim_under_review: >-
    Coordinator-committed snapshot 1aa1c37f (parent d729af05, the frozen
    specification_v9.yaml after two pre-freeze review rounds), covering
    RUN-SSIQ-a85692-i: a truncation-mutation control re-running v8's
    per-vertex-independent-RNG delta_E probe at p=2437 with per-vertex budget
    cut to 0.5s (well below the observed 1.15-1.70s natural completion
    range), testing whether n_value_differs rises once genuine truncation is
    forced, per RT-BATCH-011's own named counterexample/mutation. Reports
    graph-identity re-verification pass (203/203), PART A n_resolved=8/194,
    n_timed_out=194/194, coverage_fraction=0.0412, and both REQUIRED
    COMPARISONS (against the archived shared-RNG baseline and against v8's
    own identical-RNG 15.0s-budget probe) finding n_value_differs=0 over the
    17 vertices resolved this run (8 non-F_p-rational + 9 trivially-wired
    F_p-rational), comparison_2_error null. No PERSISTS/WEAKENS label
    produced; OBJECTIVE_BOUNDARY explicitly restricts this to a descriptive
    diagnostic at p=2437, not a test of H-SSIQ-36e970's real-arm prediction.
  objections:
    - "OBJ-1: None on execution fidelity, budget honesty, or OBJECTIVE_BOUNDARY compliance. Graph-identity re-verification passed 203/203; BASE_SEED/derive_per_vertex_seed confirmed byte-identical to v8 by direct code read (git diff --stat HEAD shows zero changes to any prior implementation file); total wall-clock 101.4591281414032s against 600s (16.9%), consistent to full float precision across raw-result.json, manifest.yaml, and execution_report.yaml."
    - "OBJ-2 (statistical power): 0/8 (equivalently 0/17 including the 9 trivially-matching F_p-rational vertices) has weak power against RT-BATCH-011's own named hypothesis. Exact Clopper-Pearson 95% upper bound on the true per-vertex difference probability given 0/8 is 1-0.05^(1/8)=31.2%; the 10-30% range this task named as a plausible moderate signal is almost entirely inside this interval, not excluded by it. At a true rate of 15%, 0/8 occurs with probability 0.85^8=27.3%, not a rare event."
    - "OBJ-3 (correlated sample): the 8 resolved vertices are 4 exact Frobenius-conjugate pairs, not 8 independent trials. I confirmed build_isogeny_graph.py:119's frobenius(x)=(x[0], (-x[1])%p) against all 8 resolved vertex tuples in per_vertex_records: (59,422)/(59,2015), (90,762)/(90,1675), (490,674)/(490,1763), (756,344)/(756,2093) are each an exact (a,b)/(a,p-b) pair (2437-422=2015, 2437-762=1675, 2437-674=1763, 2437-344=2093). Since two_sided_search's target is field.frobenius(v), each pair runs the identical minimum-degree-product problem with source/target swapped. Recomputing the 95% CI on 4 independent pairs gives 1-0.05^(1/4)=52.7%: a true divergence rate as high as roughly one-in-two truncated vertices remains fully consistent with the observed 0/8 at this sample's actual independence structure."
    - "OBJ-4 (value-extreme selection effect, mechanism-traced not hypothesized): I pulled RUN-SSIQ-a85692-b's full archived delta_map for p=2437 and computed its value histogram over the 194 non-F_p-rational vertices: delta=2 is 34/194 (17.5%), delta=3 is 70/194 (36.1%, the MODAL value), delta>=4 is 90/194 (46.4%). All 8 vertices this run resolved have delta_e_upper_bound==2 (the smallest nontrivial achievable value); zero resolved with delta=3 despite it being twice as common in the true population. build_smooth_table (compute_delta_e.py:144-174) is a strict best-first, lowest-degree-first Dijkstra expansion with no incremental collision check -- both source and target tables always consume their FULL allotted half-budget before the single end-of-search intersection check, confirmed directly: resolved vertices' wall_seconds (0.50172-0.54235s) statistically overlap unresolved vertices' wall_seconds (0.50023-0.57327s) almost entirely, so resolution here does NOT mean the search terminated early. This is a directly-demonstrated, mechanism-level bias toward the value least likely to be perturbed by any truncation-driven RNG-timing effect (discoverable within the first few heap-pops on both sides), not a chance artifact."
    - "OBJ-5 (design intent not exercised): because of OBJ-4, this run's own stated purpose (does a resolved-but-truncated search find a DIFFERENT value than the same seed at full budget) was essentially never tested -- the 8 vertices that resolved are exactly the ones whose answer is locked in almost immediately regardless of budget size, while the 186 vertices whose true answer requires deeper search (where a genuine truncation-vs-completion divergence could plausibly appear) produced no data at all."
    - "OBJ-6 (framing, advisory): 'far more severe than anticipated' (Coordinator's commit message; execution_report.yaml ANOM-1) is fair against the spec's own prose ('some or most vertices'), but the underlying near-total-timeout fact was close to arithmetically foreseeable: RUN-SSIQ-a85692-h's own committed per_vertex_records (read directly) show a MINIMUM full two-sided completion time of 1.14993s across all 194 vertices -- more than double the entire 0.5s v9 budget -- already cited in the frozen spec's own budget-justification text. Does not change what the run supports; a calibration note for future amendments."
    - "OBJ-7 (minor, precision): execution_report.yaml's OBS-2 attributes the resolved sample to two_sided_search 'surfacing small-degree collisions fastest.' Per the wall_seconds data above, 'fastest' is not supported (resolved and unresolved vertices consume statistically indistinguishable wall time); the correct mechanism is fewest-heap-pops-to-discover, not early wall-clock termination."
  required_controls:
    - "A follow-up truncation-mutation run at an intermediate per-vertex budget strictly between 0.5s and the observed 1.14993s natural-completion floor (e.g. 0.8s or 0.9s) -- high enough to plausibly pull delta>=3 vertices into the resolved set and test the Front-2(b) mechanism directly, while staying below every observed completion time so genuine truncation is preserved (avoiding RT-BATCH-011's original never-truncates problem). This is the single cheapest, most informative next action."
    - "A budget sweep (0.6s, 0.8s, 1.0s) rather than one more single fixed point, to observe n_resolved and the resolved-value distribution as a dose-response curve against budget."
    - "Before any future citation treats the 8 resolved vertices as 8 independent data points: either report n_value_differs deduplicated by conjugate pair, or explicitly disclose the pairing and its effect on effective sample size, matching this run's own non_fp_rational_only sub-breakdown convention of never hiding a domain choice that changes what a count means."
  counterexample_or_mutation: >-
    Rerun this amendment's identical procedure at PER_VERTEX_BUDGET_SECONDS =
    0.8 (or any value strictly between 0.5 and 1.14993, the observed natural-
    completion floor). If the resolved-value distribution at that budget
    remains dominated by delta=2 far out of proportion to its 17.5%
    population share, that would be a genuinely surprising result the
    best-first-search mechanism traced in OBJ-4 does not predict, worth
    investigating further. If it shifts toward the true population mix (more
    delta=3, delta=4 entering the resolved set as budget grows), that
    confirms the traced mechanism and licenses a sufficiently-generous-but-
    still-truncating budget as the correct instrument for RT-BATCH-011's
    boundary question, which this run's 0.5s budget was too severe to
    provide.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale, single-prime search-procedure diagnostic work,
    H-SSIQ-36e970.asymptotic_claim null throughout, correctly inherited and
    unchanged. The relevant baseline is this campaign's own instrument-
    scrutiny discipline (RT-BATCH-009/RT-BATCH-010/RT-BATCH-011's "trace it,
    don't trust it, bring your own control"), extended here from auditing
    whether a comparison can discriminate a hypothesis at all (RT-BATCH-011's
    contribution) to auditing whether an underpowered positive instance of
    that comparison is being asked to bear more evidentiary weight than its
    own sample size and internal correlation structure can support.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty -- unchanged by this run, a search-procedure diagnostic rather than a heuristic-conditional asymptotic claim. The one heuristic-shaped assumption worth naming, not one of H-SSIQ-36e970's own numbered items: the frozen spec implicitly treats 'the search resolves a vertex under truncation' and 'the resolved value is representative of what fuller search would show generally' as correlated in the helpful direction. OBJ-4 shows this is backwards for this budget: resolution is correlated with the smallest, least truncation-sensitive answers, not a representative cross-section. Worth flagging if this design is reused as a template."
  cost_model_challenges:
    - "No asymptotic-cost claim anywhere in this run. Measured wall-clock 101.4591281414032s against a 600s/0.2 CPU-hour budget, matching raw-result.json's figure to full float precision across manifest.yaml and execution_report.yaml; 16.9% budget utilization, honestly reported. The disclosed ~4.2% overshoot of the 97.0s worst-case sub-bound (101.03s measured PART A time, attributed to the PF-4 soft-cap mechanism) is correctly and un-defensively reported and stays comfortably within the 600s hard cap and the spec's own ~6.19x margin. No objection."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated, not exceeded."
    - "raw-result.json's objective_boundary correctly restricts this run to a purely descriptive measurement at p=2437 alone, explicitly excluding H-SSIQ-36e970's real-arm prediction, lever L4, and any PERSISTS/WEAKENS vocabulary -- verified by direct field read. No scope inflation found in this run's own artifacts; this review's corrections are evidentiary-weight/statistical-power corrections for future citation, not scope-inflation defects in what this run itself currently claims."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-i as committed at 1aa1c37f (parent d729af05),
    against specification_v9.yaml: the run executes exactly as the frozen
    spec requires (graph-identity re-verification passes 203/203; PART A ran
    on all 194 non-F_p-rational vertices under the fixed 0.5s budget with
    byte-identical RNG seeds to v8; n_resolved=8, n_timed_out=194/194 --
    every vertex hit the cutoff on at least one table-build half, resolved
    and timed_out being genuinely non-exclusive by design, demonstrated
    concretely here for the first time; coverage_fraction=0.0412; both
    REQUIRED COMPARISONS found n_value_differs=0 over the 17 vertices
    resolved (8 non-F_p-rational + 9 trivially-wired F_p-rational);
    comparison_2_error null genuinely reflects a successfully-executed code
    path, confirmed by direct trace of parse_v8_new_delta_map against the
    real 203-key source file). What this run licenses, narrowly: a genuine,
    honestly-reported measurement that severe truncation leaves 194/194
    non-F_p-rational vertices with at least one truncated table-build half,
    of which 8 (forming 4 exact Frobenius-conjugate pairs, all at the
    smallest achievable value delta=2) nonetheless resolve a collision,
    all 8 matching both the archived and v8's own values. What this run does
    NOT license: any statement that truncation "does not reopen" or
    "confirms the boundary of" RT-BATCH-011's RNG-sharing determinism
    argument -- the observed 0/8 is statistically consistent (95% CI) with a
    true divergence rate as high as 31% (raw count) to 53% (conjugate-pair-
    corrected), and the 8 vertices that did resolve are, by a directly-traced
    mechanism of the search algorithm itself, the subpopulation least likely
    to be sensitive to the truncation effect under test. The correct status
    after this run is still open/inconclusive on RT-BATCH-011's boundary
    question, not narrowed toward either of its two named outcomes.
  next_concrete_action: >-
    Coordinator, before drafting any EV-SSIQ-*/DEC-* record citing this run:
    (1) accept RUN-SSIQ-a85692-i's execution fidelity, cost/budget honesty,
    and OBJECTIVE_BOUNDARY compliance as clean; (2) record this run's status
    as inconclusive, not confirmatory, regarding RT-BATCH-011's own boundary
    prediction, citing the exact power bounds (31.2% raw / 52.7% pair-
    corrected 95% CI) rather than a qualitative small-sample caveat; (3) do
    not cite n_value_differs=0 as evidence the determinism argument extends
    into the truncated regime -- the resolved subsample is a mechanism-
    traced, extreme-value, internally-correlated selection, not a
    representative probe of the 186 vertices the boundary question actually
    concerns; (4) the single most informative and cheapest next action is a
    follow-up truncation-mutation run at an intermediate per-vertex budget
    strictly between 0.5s and the observed 1.14993s natural-completion floor
    (e.g. 0.8s or 0.9s, or a 0.6/0.8/1.0s sweep) -- high enough to plausibly
    pull non-delta=2 vertices into the resolved set while staying below
    every observed natural-completion time so genuine truncation is
    preserved; (5) this remains, exactly as OBJECTIVE_BOUNDARY states, a
    single-prime descriptive diagnostic -- no extension to H-SSIQ-36e970,
    lever L4, PERSISTS/WEAKENS vocabulary, or any other prime is licensed.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-BATCH-012.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph rebuilt, no artifact altered. Three non-durable, read-only local
    Python computations were run directly against the committed
    truncation_probe_comparison.json, RUN-SSIQ-a85692-b/raw-result.json, and
    RUN-SSIQ-a85692-h/probe_delta_e_comparison.json: (a) extracted and
    tabulated all 8 resolved and 186 unresolved per_vertex_records'
    wall_seconds and delta_e_upper_bound values (Front 2a/4); (b) loaded
    RUN-SSIQ-a85692-b's full archived delta_map for p=2437 and computed its
    value histogram over the 194 non-F_p-rational vertices, comparing against
    the resolved sample's all-delta=2 composition (Front 2b/OBJ-4); (c)
    checked all 8 resolved vertex tuples against build_isogeny_graph.py's
    frobenius(x)=(a,p-b) definition and confirmed all 8 form 4 exact
    conjugate pairs (Front 2c/OBJ-3); (d) parsed RUN-SSIQ-a85692-h's real
    203-key new_delta_map field to confirm parse_v8_new_delta_map's
    collision-free round-trip independent of trusting the run's own
    comparison_2_error:null claim (Front 5). No file was written or edited by
    any of these computations. Read in full: specification_v9.yaml (all
    PF-1 through PF-5 fix text and both round verdicts); RT-BATCH-011.md;
    RUN-SSIQ-a85692-i's full package (raw-result.json, manifest.yaml,
    execution_report.yaml, truncation_probe_comparison.json, command.txt);
    delta_e_truncation_probe_v9.py (the full new implementation file, read
    directly, not taken from spec prose or the execution report's own
    description); compute_delta_e.py's two_sided_search and
    build_smooth_table (lines 144-211); build_isogeny_graph.py's frobenius
    (lines 119-124); RUN-SSIQ-a85692-b's raw-result.json (archived delta_map)
    and RUN-SSIQ-a85692-h's probe_delta_e_comparison.json (v8's new_delta_map
    and per_vertex_records).
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-BATCH-012.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v9.yaml and
    every run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
