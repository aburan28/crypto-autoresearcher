# RT-BATCH-011 — Red Team review of RUN-SSIQ-a85692-h (EXP-SSIQ-a85692 v8),
# GOAL-SSIQ-001 BATCH-011 (PF-6's own named probe: independent per-vertex RNG,
# fixed per-vertex budget, p=2437 only)

**Reviews the Coordinator-committed snapshot at `fcd9deac` (parent `2c17b69e`,
the frozen `specification_v8.yaml` after three pre-freeze rounds), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/archives/TASK-20260806-edeb5a-receipt.yaml`,
covering `RUN-SSIQ-a85692-h`.** Per this task's operating rules, only this
Coordinator-committed snapshot is treated as durable input; the three
pre-freeze rounds' PF-1/PF-2/PF-9/PF-12/PF-13 findings are not
re-litigated. Every check below is read-only against the committed tree,
plus one local, non-durable, out-of-band computation (below) run directly
against the committed implementation files and committed archived JSON to
trace a specific numeric discrepancy — no run artifact, spec, or ledger
record was written or modified.

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
    lineage. Does not upgrade the campaign's evidence tier and does not
    itself satisfy or advance a closure quorum. A Validator is reviewing the
    same run independently and in parallel; produced without coordinating
    with it, per this task's instruction.
```

---

## Bottom line up front

**The run is executed exactly as the frozen `specification_v8.yaml`
requires — no protocol deviation, no crash, no coverage shortfall, honest
cost reporting. The mechanical `PERSISTS` label is correctly derived under
the pre-registered thresholds. But two adversarial questions posed by this
task both land: PART A's headline "0 value differences across 203 vertices"
is not the strong, RNG-independence-confirming result it appears to be — it
is close to the algorithm's *guaranteed* output given the code's own
correctness invariants, at this specific toy scale — and PART B's "stronger
than v7's archived 23.1-point margin" framing is a comparison of two
independently-drawn 1000-trial samples whose base-value orderings I have
directly traced and shown differ, which is sufficient by itself to explain
the 25.29-vs-23.1 discrepancy as ordinary Monte Carlo variation on an
extreme order statistic, not as a strengthened signal.** Both findings
narrow, rather than overturn, what this run licenses: PF-6's RNG-sharing
channel is best described as *structurally* (not merely empirically) ruled
out for p=2437 — a stronger, more defensible, but also narrower and
scale-bound claim than the "empirical signal persisted, even more strongly"
framing the raw artifacts and Coordinator's own commit message use.

1. **PART A's "0 differences" comparison has much less discriminating power
   against PF-6's RNG-sharing hypothesis than its framing suggests, because
   `two_sided_search`'s output is provably RNG-invariant whenever the search
   completes without truncation — and at p=2437's scale, it always
   completes with enormous margin.** `find_roots_with_multiplicity`
   (`build_isogeny_graph.py:340-427`) uses randomness only to pick which
   trial element the Cantor–Zassenhaus-style splitter tries internally; the
   function is *correctness-checked* before returning (`if len(distinct_roots)
   != sdeg: raise RuntimeError`, plus the earlier squarefree/gcd degree-deficit
   check) to always return the full, exact root multiset regardless of which
   random elements were tried along the way. `build_smooth_table`'s
   Dijkstra-style expansion is otherwise pure, deterministic bookkeeping (heap
   ties break on vertex-tuple comparison, not on RNG). So whenever the 15s
   per-vertex budget is not exhausted, `two_sided_search`'s
   `delta_e_upper_bound` for a given vertex is a function of `(field,
   source_j, target_j, L, X)` alone — **not** of which RNG seed drove it. I
   pulled `probe_delta_e_comparison.json`'s own `per_vertex_records` and
   confirmed empirically: max per-vertex wall time across all 194 vertices
   was **1.70s**, min **1.15s**, `n_timed_out = 0`, against a 15s budget (a
   >8x margin even at the slowest vertex) — no vertex came remotely close to
   truncation under the fresh, independent RNG regime, and PF-4 (round 1
   pre-freeze review) already established the archived shared-RNG baseline
   used only ~7.9% of its aggregate pool. Given neither run ever truncated,
   `n_value_differs = 0` was the **expected, near-certain outcome under
   either hypothesis** — "PF-6's confound is real" and "PF-6's confound does
   not exist" both predict 0 differences here, so this specific comparison
   cannot distinguish them. It remains a genuine, valuable
   *correctness/reproducibility* check (it would have caught a code bug or a
   truncation-driven divergence), just not the falsification test of PF-6's
   RNG-sharing concern its framing implies.

2. **This sharpens, rather than weakens, the correct conclusion about PF-6's
   RNG-sharing channel — but changes its epistemic basis.** Because
   `two_sided_search`'s output is provably RNG-invariant given
   non-truncation, and non-truncation is independently confirmed on both
   sides (PF-4's archived-side disclosure; my own per-vertex trace on the
   probe side), PF-6's RNG-sharing channel for p=2437 is best stated as
   **structurally closed by a determinism argument**, not as "empirically
   tested and found not to matter." That is a *stronger* claim in one sense
   (it does not depend on this one draw's luck) and a *narrower* one in
   another (it is a scale-bound argument: it holds only as long as the
   search stays far from its time budget, which need not remain true at
   larger primes or crypto scale, where PF-6's mechanism becomes live again
   and this specific style of probe would regain real discriminating power).

3. **The reported "stronger margin" (25.29pp vs. v7's archived 23.1pp) is a
   traced artifact of differing base-value insertion order across two
   independently-drawn 1000-trial permutation samples, not a strengthened
   signal — concretely demonstrated, not merely suspected.** Both
   `delta_e_permutation_null_control_v7.run_for_prime`
   (lines 344-360, feeding v7's archived null) and
   `delta_e_independent_rng_probe_v8.run_probe_permutation_null_control_v8`
   (lines 344-360, feeding this run's fresh null) construct
   `base_values = list(delta_map.values())`, then for each of 1000 trials
   call `rng.shuffle(values)` (a single `random.Random(PERMUTATION_SEED)`
   instance, `PERMUTATION_SEED = 20260806` in **both**) and
   `dict(zip(vertices, values))`. Python's `Random.shuffle` (Fisher–Yates)
   performs an index-permutation that depends **only on list length and RNG
   state**, never on element values — so if `base_values`' *insertion
   order* differs between the two runs, the two "same-seed" 1000-trial
   samples are two genuinely different (though still individually valid)
   draws, not a re-derivation of the same sequence. I loaded
   `RUN-SSIQ-a85692-b`'s archived `delta_map` for p=2437 (via
   `trapping_diagnostic_v5.load_archived_prime_data`, the same function both
   v7 and v8 use) and directly rebuilt the graph via
   `trapping_diagnostic_v5.build_graph_for_prime(2437, 20260805)` (the same
   call both runs make): **the archived delta_map's key insertion order
   does not equal the natural sorted-vertex order, and does not equal the
   fp-rational-then-non-fp-rational split order that
   `compute_delta_e_v2.py`'s own documented single-pass construction
   (lines 258-278) and `delta_e_independent_rng_probe_v8.py`'s PF-9
   construction step (lines 192-220) both produce when run fresh against the
   identical, verifiably-identical graph.** (`g["vertices"] = sorted(visited)`
   is canonical per `build_isogeny_graph.build_graph_bfs` line 624, so this
   is not an artifact of BFS traversal order.) I did not fully trace *why*
   the archived JSON's key order departs from what a fresh reconstruction of
   the documented construction produces (a plausible candidate is some
   reprocessing between the in-memory `delta_map` and the archived
   `delta_map_json_safe`/JSON round-trip in `RUN-SSIQ-a85692-b`'s own
   pipeline, not examined further here) — but the *existence* of the
   mismatch is directly demonstrated, and by the shuffle-determinism
   argument above it is sufficient on its own to explain the 25.29-vs-23.1pp
   gap without invoking any change in signal strength. Consistent with this:
   the two null distributions' **medians are numerically identical**
   (`0.5844155844155844` in both — expected, since a fixed, coarse ~1000-value
   distribution has many repeated achievable fractions near its center) while
   the **extreme order statistics (max, min) differ noticeably** (0.7692 vs.
   0.7471; 0.3836 vs. 0.3571) — exactly the noise pattern expected from two
   independent finite samples of the same generating process, where the
   sample maximum of 1000 draws is far noisier than the sample median.

4. **PART A's own comparison (`compare_against_archived`) is unaffected by
   the ordering issue** — it looks up `archived_delta_map[v]` and
   `new_delta_map[v]` by vertex-tuple key, not by list position, so its
   `n_value_differs = 0` finding is a valid, order-independent statement
   (just a weakly-discriminating one, per point 1). The ordering issue is
   specific to PART B's shuffle-based null construction.

5. **Scope, budget, and cost reporting all check out and none of the
   pre-registered thresholds or `OBJECTIVE_BOUNDARY` text were exceeded.**
   `raw-result.json`'s `objective_boundary` and `part_b_summary
   .objective_boundary` both correctly restrict a `PERSISTS` result to
   p=2437 alone, explicitly excluding the other three primes,
   `H-SSIQ-36e970`, and lever L4 — matching the frozen spec's own
   `OBJECTIVE_BOUNDARY` text verbatim. `manifest.yaml`'s
   `timing.wall_seconds: 278.49618768692017` matches `raw-result.json`'s
   `wall_clock_seconds` exactly, and the `~7.7%`/`~7.74%` budget-utilization
   figures in `manifest.yaml`'s `validity_reason` and `timing_note` are
   consistent with `278.496 / 3600`. No embellishment found.

Given the above, my verdict is **CHALLENGE (narrow)**: the run's execution
fidelity, coverage gate, budget honesty, and objective-boundary scoping are
all clean and correctly reported — but the evidentiary *weight* the raw
artifacts and Coordinator's commit message implicitly assign to this run
(an empirical RNG-sharing test that "persisted, even more strongly than
archived") overstates what the mechanism and the null construction actually
support. The correct, narrower, and in one respect *more rigorous*
statement is: PF-6's RNG-sharing channel is closed for p=2437 by a
determinism argument about `two_sided_search`'s own correctness invariant
(not by this comparison's empirical power), and the reported margin
increase is sampling noise from a base-value ordering difference between two
independently-drawn null samples, not a strengthened signal.

---

## Front 1 — Adversarial Question 1: does the zero-diff comparison actually
## discriminate PF-6's confound, or is it near-guaranteed at this scale?

**Near-guaranteed, for the reasons in bottom-line point 1.** Read directly:
`experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py:340`
(`two_sided_search`) calls `build_smooth_table` twice, which calls
`neighbors_ell_isogenous` → `find_roots_with_multiplicity`
(`experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py:340-427`).
That function's only use of `rng` is inside `_split_squarefree`, an internal
polynomial-splitting routine, and the function raises before returning if
the split result's degree does not exactly match the polynomial's
squarefree-part degree — i.e., it is *designed and verified* to be
RNG-invariant in its output content, with RNG affecting only its internal
computational path. Combined with `build_smooth_table`'s deterministic
Dijkstra/best-first bookkeeping (heap comparisons break ties on vertex
identity, not RNG draws), `two_sided_search`'s reported
`delta_e_upper_bound` for a given vertex cannot differ across RNG seeds
*unless* the 15s (or, archived-side, aggregate-pool-derived) time budget is
exhausted mid-search, truncating the smooth table before it reaches its
natural (bound-`X=23`) fixed point. I confirmed directly from
`probe_delta_e_comparison.json`'s `per_vertex_records` that no vertex in
this run came within 8x of its budget (max 1.70s of 15.0s), and PF-4 already
established the archived run used only ~7.9% of a much larger aggregate
pool. **Neither run ever exercised the one channel through which RNG choice
could have changed the algorithm's output.** This does not mean PART A was
worthless — it is a real, useful correctness/reproducibility check (a code
bug or an unexpected truncation would have shown up as `n_value_differs >
0`) — but it means the reported "0 out of 203" is not informative about
*which* of PF-6's two hypotheses is true; both predict the same observed
result here.

## Front 2 — Adversarial Question 2: is the margin difference (25.29pp vs.
## 23.1pp) itself suspicious, expected, or noise — traced concretely?

**Traced concretely to a base-value ordering difference between two
independently-drawn 1000-trial permutation samples — a mundane, demonstrated
source, not evidence of anything about PF-6's confound.** See bottom-line
point 3 for the full trace. The short version: `PERMUTATION_SEED = 20260806`
being identical in both runs does **not** imply identical null samples,
because `random.Random.shuffle` is a length-and-seed-determined index
permutation applied to whatever order `base_values = list(delta_map.values())`
happens to be in — and I directly confirmed the archived delta_map's key
order (loaded by `trapping_diagnostic_v5.load_archived_prime_data`, feeding
v7's null) does not match the order a fresh reconstruction of the documented
delta_map-construction logic produces against the identical, verifiably-
identical rebuilt graph (feeding v8's null). The two null runs are therefore
two genuine, independent 1000-trial Monte Carlo draws from (very plausibly)
the same underlying generating process, not a literal replay. This is
consistent with the observed pattern: identical median (a central, low-noise
statistic on a coarse near-1000-point empirical distribution), differing max
and min (high-noise extreme order statistics for N=1000). **The "stronger
than archived" framing in `manifest.yaml`'s `validity_reason` and the
Coordinator's own commit message, while not literally false as arithmetic
(25.29 > 23.1), should not be read as the signal getting stronger — it is
ordinary between-sample variance on an already-comfortable margin.** I did
not fully identify why the archived JSON's key order departs from the
documented single-pass construction (candidate: some reprocessing step in
`RUN-SSIQ-a85692-b`'s own pipeline between the in-memory dict and its
JSON-serialized form, not examined further here); that gap does not weaken
the finding, since the mismatch itself is what matters and is directly
demonstrated by direct comparison, independent of its cause.

## Front 3 — Adversarial Question 3: does a PERSISTS result on p=2437 alone
## test PF-6's RNG-sharing half with real power?

**With empirical power, no (Front 1); with a structural/correctness
argument, yes, and I judge this the more defensible way to state the
result.** Given `two_sided_search`'s RNG-invariance-when-not-truncated is a
property of the code's own design (not an assumption), and non-truncation
is independently confirmed on both the archived side (PF-4) and this run's
side (my own per-vertex trace, Front 1), it follows *deductively*, not just
empirically, that RNG-sharing could not have altered a single delta_E value
for p=2437 under either search regime. That is a genuinely stronger
conclusion than "we ran it once and it matched" — but it is bound to this
scale: at a prime large enough that `two_sided_search` starts timing out
some vertices (plausible as primes grow, since table-build cost scales with
field arithmetic cost and the smooth-degree table's branching factor), the
determinism argument stops applying and PF-6's RNG-sharing channel becomes
live and genuinely testable again, at which point this style of probe would
regain real discriminating power. This should be stated explicitly if/when
BATCH-012 or a later amendment considers widening to the other three primes
(3889, 5737, 7333) or toward crypto scale — the same "zero differences"
outcome should be *expected*, not treated as reassuring, unless per-vertex
wall-time data is checked for near-timeout cases first.

## Front 4 — Adversarial Question 4: would `n_value_differs` stay at 0 under
## yet another independent seed?

**Yes, with high confidence, grounded in the Front 1/3 determinism argument
rather than left as an open unknown.** Given `BASE_SEED = 20260811` is
arbitrary relative to the mechanism (the RNG only selects internal
polynomial-splitting trial elements, never affecting the returned root set
when the search completes), and this run's own measured timing (max 1.70s
against a 15s budget) shows enormous headroom regardless of which specific
seed is used, a re-run under a different `BASE_SEED` should, with very high
probability, reproduce `n_value_differs = 0` again — not because the RNG
"got lucky" this time, but because the search-completion margin at p=2437's
scale is wide enough that no plausible seed pushes any vertex near
truncation. This is a testable prediction (a genuine, cheap next control:
one more probe run at a different `BASE_SEED`, expected outcome `0/203`
again), not merely an assertion — see Required controls / Next concrete
action.

## Front 5 — objective-boundary scoping and cost honesty (Adversarial
## Questions 7-8)

Both check out cleanly. `raw-result.json`'s `objective_boundary` and
`part_b_summary.objective_boundary` explicitly restrict a `PERSISTS` finding
to p=2437 alone, explicitly disclaim any extension to the other three
primes, `H-SSIQ-36e970`, or lever L4, and explicitly restate the diagnostic-
control (not-a-claim) framing — matching the frozen spec's own
`OBJECTIVE_BOUNDARY` text. `manifest.yaml`'s `timing.wall_seconds:
278.49618768692017` matches `raw-result.json`'s `wall_clock_seconds` to
full float precision, and the reported ~7.7% budget utilization
(278.496/3600) is arithmetically correct and not rounded favorably.

---

## Objections

- **OBJ-1**: None on execution fidelity. `execution_report.yaml`'s own
  required-artifacts diff-list cross-check is accurate against
  `specification_v8.yaml`'s text (spot-checked); the two-part graph-identity
  re-verification, the strengthened `len(new_delta_map)==203` gate (PF-9),
  the fixed 15s per-vertex budget, the fresh per-vertex RNG derivation, and
  the F_p-rational unconditional wiring step are all implemented exactly as
  frozen. No objection to `RUN-SSIQ-a85692-h`'s own reported raw numbers.
- **OBJ-2**: PART A's `n_value_differs = 0` finding, while correctly
  computed, has much less power to discriminate PF-6's RNG-sharing
  hypothesis than its framing implies — `two_sided_search`'s output is
  provably RNG-invariant whenever the search completes without truncation
  (code-traced: `find_roots_with_multiplicity`'s internal correctness check
  guarantees the full, exact root set regardless of internal random
  choices), and I confirmed via `per_vertex_records` that no vertex in this
  run came within 8x of its 15s budget. Both "PF-6's confound is real" and
  "PF-6's confound does not exist" predict `0/203` here; this comparison
  cannot distinguish them empirically.
- **OBJ-3**: PART B's "margin stronger than v7's archived 23.1pp" framing
  (`manifest.yaml validity_reason`, Coordinator's commit message) is a
  comparison of two independently-drawn 1000-trial permutation samples whose
  base-value insertion orders I directly confirmed differ (archived order,
  loaded via `trapping_diagnostic_v5.load_archived_prime_data`, does not
  match the order a fresh reconstruction of the documented
  fp-then-non-fp-rational split construction produces against the identical
  rebuilt graph). Given `random.Random.shuffle`'s index-permutation depends
  only on length and RNG state, this ordering difference alone is sufficient
  to explain the 25.29-vs-23.1pp gap as between-sample Monte Carlo variance
  on an extreme order statistic (consistent with the two distributions'
  identical medians but differing extrema), not a strengthened signal.
- **OBJ-4**: The correct, more defensible statement of what this run
  establishes is a *structural* (determinism-argument) closure of PF-6's
  RNG-sharing channel for p=2437 — not an *empirical* test that happened to
  find no difference. This is a stronger claim in one sense (independent of
  this draw's luck) but explicitly scale-bound (the determinism argument
  requires non-truncated search, verified true here but not guaranteed at
  larger primes or crypto scale), and this scale-boundedness should be
  stated in any evidence record citing this run, not left implicit.

## Required controls

- **One additional probe run at a different `BASE_SEED`** (cheap: this run
  took 278.5s of a 3600s budget) to test the Front 4 prediction directly:
  expected outcome `n_value_differs = 0` again, for the reason given in
  Front 1/4, not because of luck. A second `0/203` result would directly
  corroborate the determinism argument; any non-zero result would falsify it
  and would itself be the single most informative outcome this lineage could
  produce, since it would mean truncation or a code-path I have not
  identified is live even at this toy scale.
- **Before citing the 25.29pp margin against v7's 23.1pp margin as
  "stronger": either (a) re-run PART B's null construction using the
  archived run's own delta_map insertion order explicitly matched (so the
  two null samples are literal replays of the same shuffle sequence, making
  the comparison apples-to-apples), or (b) drop the cross-run margin
  comparison entirely and report only that this run's own fresh margin
  (25.29pp) clears the pre-registered 13.1pp `PERSISTS` threshold — which it
  does, comfortably, on its own terms, without needing the (order-confounded)
  comparison to v7's archived figure.**
- Per-vertex wall-time data (already collected in `per_vertex_records`)
  should be checked for near-timeout cases as a standard gate in any future
  widening of this probe to the other three primes or larger primes,
  precisely because the determinism argument in Front 1/3 stops holding once
  truncation becomes plausible — at that point this probe design would
  finally test what PF-6 actually named.

## Counterexample or mutation

The cheapest concrete mutation that would separate "PART A's 0-diff result
is informative" from "PART A's 0-diff result is near-guaranteed regardless":
artificially shrink `PER_VERTEX_BUDGET_SECONDS` in a probe run (e.g. to
0.5s, well below the observed ~1.15-1.70s completion range) so that some
vertices genuinely truncate under the fresh-RNG regime. If `n_value_differs`
stays near 0 even under forced truncation, that would be a genuinely
surprising, informative result about the algorithm's robustness. If it rises
sharply, that confirms the determinism argument's boundary condition
precisely: RNG choice only matters once truncation is live, exactly as
Front 1/3 predict. This is a strictly cheaper and more targeted control than
re-running at full budget with a new seed (Front 4's control), and directly
targets the mechanism rather than merely repeating the same
near-certain-outcome test.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
statistical-control/search-procedure diagnostic work,
`H-SSIQ-36e970.asymptotic_claim: null` throughout, correctly inherited and
unchanged by this run. The relevant baseline is this campaign's own
instrument-scrutiny discipline (`RT-BATCH-009`/`RT-BATCH-010`'s "trace it,
don't trust it, bring your own control"): this review extends that standard
from statistical-null-control auditing to auditing the *search primitive
itself* — asking not just "was the permutation-null control run correctly"
(yes) but "does the underlying randomized algorithm's own correctness
invariants make the planned comparison capable of discriminating the stated
hypothesis at all" (only partially, and for a traceable, scale-bound
reason).

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty — this is a
gradient-existence screen and search-procedure diagnostic, not a
heuristic-conditional asymptotic-complexity claim, and nothing in this run
changes that. No numbered heuristic is implicated. The one heuristic-shaped
object worth naming explicitly, though it is not one of `H-SSIQ-36e970`'s
own numbered assumptions: the frozen spec's own implicit expectation that
"this amendment's real value multiset should be nearly identical to v7's if
PART A's comparison finds few value differences" (spec text,
`probe_permutation_null_control_v8` block) is correct about the *value*
multiset but silently assumed order-comparability of the two null draws,
which this review shows does not hold — worth a corrective note if this
spec's prose is reused as a template for a future amendment.

## Cost model challenges

No asymptotic-cost claim is made anywhere in this run. Measured wall-clock
278.49618768692017s against a 3600s/1.0-CPU-hour budget (`manifest.yaml`
timing block), matching `raw-result.json`'s figure to full float precision;
~7.7% budget utilization, honestly reported, not rounded favorably. PF-3's
required proactive detached launch was applied and the run finished
naturally with no killed attempt, consistent with `command.txt`. No
objection to the cost/budget bookkeeping.

## Reduction and scope challenges

No affected/safe cryptographic scheme list appears anywhere in this
amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) is correctly
stated and not exceeded. `raw-result.json`'s and the frozen spec's own
`OBJECTIVE_BOUNDARY` correctly restrict a `PERSISTS` result to p=2437 alone,
explicitly excluding the other three primes, `H-SSIQ-36e970`'s real-arm
prediction, and lever L4 — verified by direct read, not merely trusted from
the spec's prose. No scope inflation found in this run's own artifacts. The
one correction this review recommends (Front 3/OBJ-4: state the RNG-sharing
closure as a scale-bound determinism argument, not an unconditional
empirical finding) is a framing/evidentiary-weight correction, not a
scope-inflation defect in what was actually tested or claimed.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; this is a direct
instrument-level search-procedure diagnostic, not a proof-oriented proposal.
Attacked and held.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-h` as committed at `fcd9deac` (parent `2c17b69e`),
against `specification_v8.yaml`: the run executes exactly as the frozen spec
requires (graph-identity re-verification passes; PART A resolves 194/194
non-F_p-rational vertices with 0 timeouts, max per-vertex wall time 1.70s
against a 15s budget; the PF-9 gate `len(new_delta_map)==203` passes; PART A's
key-matched comparison against `RUN-SSIQ-a85692-b`'s archived delta_map
finds `n_value_differs=0`; PART B's `REAL_DEPTH0_FRACTION=1.0` on 95/95
structural local minima, exactly matching v7's archived figure; a freshly
and correctly drawn 1000-trial permutation null with `null_max=0.7471`,
comfortably clearing the pre-registered `PERSISTS` thresholds with its own
25.29pp margin; mechanical outcome `PERSISTS`, correctly derived). **What
this run licenses, narrowly stated**: for p=2437 specifically, PF-6's
RNG-sharing channel is closed — not primarily because this one empirical
comparison happened to find zero differences (a near-guaranteed outcome
given `two_sided_search`'s own correctness-verified, RNG-invariant-when-
non-truncated output, independently confirmed non-truncated on both the
archived and probe sides), but because that determinism argument rules the
channel out deductively at this scale. The reported "stronger than
archived" margin (25.29pp vs. 23.1pp) is not evidence of a strengthened
signal; it is a directly-traced artifact of differing base-value insertion
order between two independently-drawn 1000-trial null samples under the
Fisher-Yates shuffle construction, and should not be cited as such. This
result licenses restoring `DEC-20260806-498531` D-2's "genuine structural
fact" language for p=2437 alone (per the frozen spec's own
`OBJECTIVE_BOUNDARY`, correctly stated in the artifacts), with the added,
narrower caveat that this closure is scale-bound and would need
re-examination — via per-vertex timeout data, not assumed — before being
extended to the other three primes, larger primes, or any crypto-scale
claim.

## Next concrete action

Coordinator, before drafting the `EV-SSIQ-*`/`DEC-*` record for this batch:
(1) accept `RUN-SSIQ-a85692-h`'s execution fidelity as clean — no protocol
deviation, coverage-gate pass verified directly, cost/budget honestly
reported; (2) state PF-6's RNG-sharing closure for p=2437 as a
*determinism-argument* closure (Front 1/3), not purely an empirical one, and
flag it as scale-bound (does not automatically transfer to the other three
primes or larger primes without checking per-vertex timeout margins first);
(3) do not cite the 25.29pp-vs-23.1pp margin comparison as "stronger
signal" — either drop the cross-run comparison or re-run PART B with the
archived delta_map's own key order explicitly reproduced for a genuine
apples-to-apples replay (Required controls); (4) if a further probe is
budgeted, prioritize the cheap truncation-mutation control (Counterexample
or mutation) over a same-budget different-seed rerun, since it targets the
Front 1/3 mechanism directly rather than repeating a near-certain-outcome
test; (5) this remains, exactly as `OBJECTIVE_BOUNDARY` states, a single-prime
diagnostic control — no extension to `H-SSIQ-36e970`, lever L4, or the other
three primes is licensed by this run.

## Overall verdict

**CHALLENGE (narrow).** The run itself is executed cleanly and exactly as
the frozen spec requires; no protocol deviation, execution defect, coverage
shortfall, or cost-reporting discrepancy was found. The mechanical
`PERSISTS` label is correctly derived under the pre-registered thresholds.
What this review adds, and what the Coordinator should incorporate before
this record is cited further: (a) PART A's "0 differences" result is much
closer to a guaranteed outcome of the algorithm's own correctness invariants
at this toy scale than to a genuine empirical discrimination of PF-6's
RNG-sharing hypothesis — traced to `find_roots_with_multiplicity`'s
correctness-checked, RNG-invariant-when-non-truncated design, and confirmed
non-truncated on both sides via per-vertex timing data; (b) the "stronger
margin than v7's archived result" framing is a directly-traced artifact of
differing base-value insertion order between two independent 1000-trial null
draws under the shared Fisher-Yates+seed construction, not a strengthened
signal — demonstrated by direct comparison of the archived and freshly
reconstructed delta_map key orders against the identical rebuilt graph. The
narrower, more defensible statement this run supports is a *structural*,
scale-bound closure of PF-6's RNG-sharing channel for p=2437, not the
"empirical signal persisted, even more strongly" reading the raw artifacts
and commit message currently invite.

```yaml
red_team_report:
  id: RT-BATCH-011
  task_id: TASK-20260806-359283
  claim_under_review: >-
    Coordinator-committed snapshot fcd9deac (parent 2c17b69e, the frozen
    specification_v8.yaml after three pre-freeze review rounds), receipt
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/archives/TASK-20260806-edeb5a-receipt.yaml,
    covering RUN-SSIQ-a85692-h: a probe re-search of delta_E for p=2437
    using per-vertex-independent, freshly-seeded RNG under a fixed
    (never-shrinking) per-vertex time budget, testing PF-6's confound
    (search-procedure RNG-sharing vs. genuine mathematical structure) named
    in DEC-20260806-7839b5. Reports PF-1/PF-9 coverage gate pass (203/203),
    PART A comparison against the archived shared-RNG search finding
    n_value_differs=0 across all 203 vertices (194/194 non-F_p-rational
    search-only), and PART B REAL_DEPTH0_FRACTION=1.0 (95/95 structural
    local minima, matching v7's archived figure exactly) against a fresh
    1000-trial permutation null (null_max=0.7471), margin=25.29 percentage
    points, mechanical outcome PERSISTS -- reported by the Coordinator's own
    commit message as "stronger" than v7's own archived 23.1-point margin
    for the same prime.
  objections:
    - "OBJ-1: None on execution fidelity. execution_report.yaml's own required-artifacts diff-list cross-check is accurate against specification_v8.yaml's text -- the two-part graph-identity re-verification, the strengthened len(new_delta_map)==203 gate (PF-9), the fixed 15s per-vertex budget, the fresh per-vertex RNG derivation, and the F_p-rational unconditional wiring step are all implemented exactly as frozen. No objection to RUN-SSIQ-a85692-h's own reported raw numbers."
    - "OBJ-2: PART A's n_value_differs=0 finding, while correctly computed, has much less power to discriminate PF-6's RNG-sharing hypothesis than its framing implies. two_sided_search's output (compute_delta_e.py:177-210) is provably RNG-invariant whenever the search completes without truncation: find_roots_with_multiplicity (build_isogeny_graph.py:340-427) uses rng only inside an internal Cantor-Zassenhaus-style splitter, and the function raises RuntimeError before returning if the returned root count does not exactly match the polynomial's squarefree-part degree -- i.e. it is designed and correctness-checked to return the full, exact root multiset regardless of which random elements were tried internally. I confirmed directly from probe_delta_e_comparison.json's per_vertex_records that no vertex in this run came within 8x of its 15s budget (max wall_seconds=1.6985s, min=1.1499s, n_timed_out=0), and PF-4 (round-1 pre-freeze review) already established the archived shared-RNG baseline used only ~7.9% of a much larger aggregate pool. Both 'PF-6's confound is real' and 'PF-6's confound does not exist' predict n_value_differs=0 given non-truncation on both sides -- this comparison cannot empirically distinguish them, though it remains a valid correctness/reproducibility check."
    - "OBJ-3: PART B's 'margin stronger than v7's archived 23.1pp' framing (manifest.yaml validity_reason; the Coordinator's own commit message) compares two independently-drawn 1000-trial permutation samples whose base-value insertion orders I directly confirmed differ. I loaded RUN-SSIQ-a85692-b's archived delta_map for p=2437 (via trapping_diagnostic_v5.load_archived_prime_data, the same function both v7's null control and this run's key-matched comparison use) and separately rebuilt the graph via trapping_diagnostic_v5.build_graph_for_prime(2437, 20260805): the archived delta_map's key insertion order matches neither the natural sorted-vertex order (g['vertices'] = sorted(visited), build_isogeny_graph.py:624) nor the fp-rational-then-non-fp-rational split order that both compute_delta_e_v2.py's documented single-pass construction (lines 258-278) and delta_e_independent_rng_probe_v8.py's PF-9 construction step (lines 192-220) produce when freshly run against the identical, set-verified-identical rebuilt graph. Because random.Random.shuffle performs an index permutation determined only by list length and RNG state (never element values), this base_values ordering mismatch alone is sufficient to make the two 'same-PERMUTATION_SEED=20260806' 1000-trial null samples genuinely independent draws rather than a literal replay -- consistent with the observed pattern (identical medians, 0.5844155844155844 in both; differing max/min, 0.7692 vs 0.7471 and 0.3836 vs 0.3571, the noisier extreme order statistics). I did not fully trace why the archived JSON's key order departs from the documented construction (a candidate not examined further: some reprocessing step in RUN-SSIQ-a85692-b's own pipeline between the in-memory delta_map and its JSON-serialized form); the mismatch's existence, not its cause, is what carries the finding."
    - "OBJ-4: The correct, more defensible statement of what this run establishes is a STRUCTURAL (determinism-argument) closure of PF-6's RNG-sharing channel for p=2437, not an EMPIRICAL test that happened to find zero differences -- stronger in that it does not depend on this draw's luck, but explicitly scale-bound (the determinism argument requires non-truncated search, independently verified true here via per-vertex timing but not guaranteed at larger primes or crypto scale, where PF-6's mechanism becomes live again). This scale-boundedness should be stated explicitly in any evidence record citing this run, not left implicit in a threshold-based PERSISTS label."
  required_controls:
    - "One additional probe run at a different BASE_SEED (cheap: this run used 278.5s of a 3600s budget) to test whether n_value_differs stays at 0 -- expected per the determinism argument (Front 1/3), not a coincidence of this specific draw; a non-zero result would be the single most informative outcome this lineage could produce, since it would mean truncation or an unidentified code path is live even at toy scale."
    - "Before citing the 25.29pp-vs-23.1pp margin comparison as evidence of anything: either (a) re-run PART B's null construction with the archived delta_map's own key insertion order explicitly reproduced (a genuine apples-to-apples replay of the same shuffle sequence), or (b) drop the cross-run margin comparison and report only that this run's own fresh margin (25.29pp) independently clears the pre-registered 13.1pp PERSISTS threshold on its own terms."
    - "Per-vertex wall-time data (already collected in per_vertex_records for this run) should be checked for near-timeout cases as a standard gate before any future widening of this probe design to the other three primes or larger primes -- the determinism argument in Front 1/3 stops holding once truncation becomes plausible, at which point this probe design would finally test what PF-6 actually named."
  counterexample_or_mutation: >-
    The cheapest concrete mutation that would separate "PART A's 0-diff
    result is informative" from "PART A's 0-diff result is near-guaranteed
    regardless": artificially shrink PER_VERTEX_BUDGET_SECONDS in a probe
    run (e.g. to 0.5s, well below the observed ~1.15-1.70s completion range)
    so that some vertices genuinely truncate under the fresh-RNG regime. If
    n_value_differs stays near 0 even under forced truncation, that is a
    genuinely surprising, informative result about the algorithm's
    robustness that this review's determinism argument would not predict. If
    it rises sharply, that confirms the determinism argument's boundary
    condition precisely: RNG choice only matters once truncation is live.
    This targets the mechanism directly and is strictly cheaper than a
    same-budget different-seed rerun.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale search-procedure diagnostic work, H-SSIQ-36e970.asymptotic_claim
    null throughout, correctly inherited and unchanged by this run. The
    relevant baseline is this campaign's own instrument-scrutiny discipline
    (RT-BATCH-009/RT-BATCH-010's "trace it, don't trust it, bring your own
    control"), extended here from auditing the statistical-null-control
    procedure to auditing the underlying randomized search primitive's own
    correctness invariants -- asking whether the planned comparison could,
    even in principle, discriminate the stated hypothesis at this scale.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty -- a gradient-existence screen and search-procedure diagnostic, not a heuristic-conditional asymptotic claim; nothing in this run changes that. The one heuristic-shaped assumption worth naming, though not one of H-SSIQ-36e970's own numbered items: the frozen spec's prose ('this amendment's real value multiset should be nearly identical to v7's if PART A's comparison finds few value differences') is correct about the VALUE multiset but silently assumes order-comparability of the two null draws, which this review shows does not hold -- worth a corrective note if reused as a template."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere in this run. Measured wall-clock 278.49618768692017s against a 3600s/1.0-CPU-hour budget (manifest.yaml timing block), matching raw-result.json's figure to full float precision; ~7.7% budget utilization, honestly reported, not rounded favorably. PF-3's required proactive detached launch was applied and the run finished naturally with no killed attempt. No objection to the cost/budget bookkeeping."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "raw-result.json's and the frozen spec's own OBJECTIVE_BOUNDARY correctly restrict a PERSISTS result to p=2437 alone, explicitly excluding the other three primes, H-SSIQ-36e970's real-arm prediction, and lever L4 -- verified by direct read of raw-result.json's part_b_summary.objective_boundary field, not merely trusted from the spec's prose. No scope inflation found. The one correction this review recommends (Front 3/OBJ-4) is a framing/evidentiary-weight correction, not a scope-inflation defect in what was actually tested or claimed."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-h as committed at fcd9deac (parent 2c17b69e),
    against specification_v8.yaml: the run executes exactly as the frozen
    spec requires (graph-identity re-verification passes; PART A resolves
    194/194 non-F_p-rational vertices with zero timeouts, max per-vertex
    wall time 1.70s against a 15s budget; the PF-9 gate
    len(new_delta_map)==203 passes; PART A's key-matched comparison against
    RUN-SSIQ-a85692-b's archived delta_map finds n_value_differs=0; PART B's
    REAL_DEPTH0_FRACTION=1.0 on 95/95 structural local minima, exactly
    matching v7's archived figure; a freshly and correctly drawn 1000-trial
    permutation null with null_max=0.7471, comfortably clearing the
    pre-registered PERSISTS thresholds via its own 25.29pp margin;
    mechanical outcome PERSISTS, correctly derived). What this run licenses,
    narrowly: for p=2437 specifically, PF-6's RNG-sharing channel is closed
    -- not primarily because this one empirical comparison found zero
    differences (near-guaranteed given two_sided_search's correctness-
    verified, RNG-invariant-when-non-truncated output, independently
    confirmed non-truncated on both the archived and probe sides via
    per-vertex timing data), but because that determinism argument rules the
    channel out deductively at this scale. The reported "stronger than
    archived" margin (25.29pp vs 23.1pp) is not evidence of a strengthened
    signal; it is a directly-traced artifact of differing base-value
    insertion order between two independently-drawn 1000-trial null samples
    under the shared Fisher-Yates-shuffle construction, and should not be
    cited as such. This licenses restoring DEC-20260806-498531 D-2's
    "genuine structural fact" language for p=2437 alone (per the frozen
    spec's own OBJECTIVE_BOUNDARY, correctly stated in the artifacts), with
    the added, narrower caveat that this closure is scale-bound and needs
    re-examination -- via per-vertex timeout data, not assumption -- before
    extension to the other three primes, larger primes, or any crypto-scale
    claim.
  next_concrete_action: >-
    Coordinator, before drafting the EV-SSIQ-*/DEC-* record for this batch:
    (1) accept RUN-SSIQ-a85692-h's execution fidelity as clean -- no
    protocol deviation, coverage-gate pass verified directly, cost/budget
    honestly reported; (2) state PF-6's RNG-sharing closure for p=2437 as a
    determinism-argument closure (Front 1/3), not purely an empirical one,
    and flag it as scale-bound, not automatically transferable to the other
    three primes or larger primes without checking per-vertex timeout
    margins first; (3) do not cite the 25.29pp-vs-23.1pp margin comparison
    as a "stronger signal" -- either drop the cross-run comparison or
    re-run PART B with the archived delta_map's own key order explicitly
    reproduced for a genuine apples-to-apples replay (Required controls);
    (4) if a further probe is budgeted, prioritize the cheap
    truncation-mutation control (Counterexample or mutation) over a
    same-budget different-seed rerun, since it targets the Front 1/3
    mechanism directly rather than repeating a near-certain-outcome test;
    (5) this remains, exactly as OBJECTIVE_BOUNDARY states, a single-prime
    diagnostic control -- no extension to H-SSIQ-36e970, lever L4, or the
    other three primes is licensed by this run.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-BATCH-011.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph rebuilt for the purpose of altering any artifact; two
    non-durable, read-only local Python computations were run directly
    against the committed implementation files
    (experiments/EXP-SSIQ-a85692/implementation/trapping_diagnostic_v5.py,
    build_isogeny_graph.py) and the committed archived JSON
    (experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json) to
    (a) confirm no per-vertex search in RUN-SSIQ-a85692-h came close to its
    15s time budget (read directly from
    probe_delta_e_comparison.json's per_vertex_records, no computation
    needed beyond max/min), and (b) trace the base-value insertion-order
    mismatch underlying OBJ-3/Front 2, by rebuilding the p=2437 graph via
    trapping_diagnostic_v5.build_graph_for_prime(2437, 20260805) (identical
    call every amendment in this lineage since v5 makes) and comparing the
    archived delta_map's key order against the natural sorted-vertex order
    and the fp-then-non-fp split order the documented construction produces.
    Neither computation modified any file; no run artifact, specification
    file, or ledger record was written or edited. Read in full:
    specification_v8.yaml (all PF-1 through PF-13 fix text and all three
    round verdicts); RT-PREFREEZE-EXP-SSIQ-a85692-v8.md and its round2/round3
    reports' bottom-line sections; RUN-SSIQ-a85692-h's full package
    (raw-result.json, manifest.yaml, execution_report.yaml,
    probe_delta_e_comparison.json, probe_permutation_null_control.json,
    stdout.log, command.txt); RUN-SSIQ-a85692-g's permutation_null_control.json
    (v7's archived p=2437 null, for the Front 2 comparison);
    RUN-SSIQ-a85692-b's raw-result.json (the archived delta_map and
    manifest/command.txt provenance); compute_delta_e.py, compute_delta_e_v2.py,
    delta_e_permutation_null_control_v7.py,
    delta_e_independent_rng_probe_v8.py, trapping_diagnostic_v5.py, and
    build_isogeny_graph.py (the specific functions cited throughout this
    report, read directly, not taken from spec prose or prior reports'
    descriptions).
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-BATCH-011.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v8.yaml and
    every run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
