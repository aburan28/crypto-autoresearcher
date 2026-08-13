# RT-PREFREEZE-EXP-SSIQ-a85692-v11 — Round 1 pre-freeze Red Team review of
# the DRAFT amendment `specification_v11.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001
# BATCH-014, task `TASK-20260807-43d16f`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v11.yaml` at
`status: draft`, `pre_freeze_review.status: PENDING`, `verdict: null`,
committed at `6b6703ee2` (confirmed: that commit is this file's most recent
touching commit, is an ancestor of the checked-out HEAD `6b692c2df`, and the
working tree is clean) — a two-point "floor-straddling" truncation sweep
(1.1s/1.2s) amending `specification_v10.yaml` (v10, frozen
`ca905c2482e00fef5b0bdc6902b43a77a43c8d5c`, retained unedited), implementing
item (1) of `DEC-20260806-520ca4`'s ranked resume action, itself
RT-BATCH-013's own falsifiable prediction.** Per this task's operating
rules, only Coordinator-committed snapshots are treated as durable evidence;
this review is advisory pre-freeze input on a draft and changes nothing under
`experiments/` or `ledger/`. **No implementation file for v11 exists yet**
(confirmed: no `*v11*` file under `experiments/EXP-SSIQ-a85692/implementation/`)
— this audits the plan an Executor would have to turn into code.

Read in full: `specification_v11.yaml` (329 lines); `specification_v10.yaml`
(the frozen predecessor, including every PF-1…PF-10 fix item and both freeze-
round verdicts); both BATCH-013 pre-freeze reviews (round 1 and round 2, in
full, for format and severity-calibration precedent); `RT-BATCH-013.md`;
`VAL-BATCH-013.md`; `ledger/goals/GOAL-SSIQ-001/goal.yaml` (`next_action` and
the standing per-batch obligations from BATCH-010/011/012/013);
`ledger/hypotheses/H-SSIQ-36e970.yaml`. Read directly in source, not trusted
from spec prose: `delta_e_truncation_probe_v9.py` (`run_truncation_probe_v9`
lines 147–211, `compare_against_archived` 224, `parse_v8_new_delta_map` 302,
`compare_against_v8` 328), `delta_e_truncation_sweep_v10.py`
(`value_histogram_and_conjugate_pairs` 164–219), and — the file that decides
this review — `compute_delta_e.py` lines 144–210 (`build_smooth_table`,
`two_sided_search`), plus `run_phase_minus1_on_confirmatory_set` (360–420),
the function that actually produced the archived reference map.

Directly executed against the committed tree (read-only, non-durable): the
full 194-entry `per_vertex_records` of `RUN-SSIQ-a85692-h` (min/max/median
`wall_seconds`, the below-budget counts at every candidate budget, the joint
distribution of `wall_seconds` against `delta_e_upper_bound`, the
`timed_out` count, and `comparison_against_archived`); the archived
`RUN-SSIQ-a85692-b` `raw-result.json` per-prime search record for p=2437
(`n_attempted`, `n_resolved`, `wall_seconds_used`, `sub_budget_seconds`);
the machine's core count and successive load averages.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5
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
    SESSION-independent only, NEVER model-independent. Shares a model family
    with the Coordinator who drafted v11, with the Executor, and with every
    prior reviewer in this lineage — including RT-BATCH-013, whose own
    falsifiable prediction this amendment exists to test, so the prediction
    and its adversarial review are not drawn from independent populations.
    Does not upgrade the campaign's evidence tier and does not itself satisfy
    or advance a closure quorum.
```

---

## Bottom line up front

**DO-NOT-FREEZE.** The amendment inherits v10's hard-won procedural
discipline correctly and pre-applies it (PF-2, PF-7, PF-8, PF-9, PF-10 are
all carried into the draft without needing a review round to rediscover
them — genuinely good work, and I confirmed each by direct read). The
budget arithmetic is correct. The cited functions all exist with the cited
signatures. But **the choice of `b = 1.2s` is wrong on the amendment's own
terms, and I can show that from already-archived data at zero new compute**:

1. **PF-11 [BLOCKING] — the experiment's headline question is already
   answered NO, with certainty, before it runs.** `RUN-SSIQ-a85692-h` ran
   every one of the 194 vertices to natural completion (`per_vertex_budget_seconds:
   15.0`, `n_resolved: 194`, **zero** `timed_out`). Of those 194 natural
   completion times, exactly **2** are below 1.2s — and **both have
   `delta_e_upper_bound = 2`**. The fastest vertex with `delta_E >= 5`
   takes **1.392s**, 16% above the largest sweep budget. So the question in
   the amendment's own title — "does `delta_E>=5` convergence begin
   appearing [in the naturally-completed subset] as budget crosses the
   1.14993s floor?" — is determined in advance: **no**, and no possible
   outcome of this run can be evidence about it. See §1.
2. **PF-12 [BLOCKING] — `timed_out` does *not* have the semantics v11's
   sharper prediction assumes, because the budget is split in half
   internally.** `two_sided_search` gives the **source** table
   `time_budget_seconds / 2.0` and the target table the remainder, and sets
   `timed_out = to_s or to_t`. Natural completion at budget `b` therefore
   requires `t_source <= b/2`, **not** `t_total <= b`. At `b=1.2` the
   source-side cap is **0.6s** against a median total natural time of
   1.44s. `RUN-SSIQ-a85692-h` records only the *total* `wall_seconds`, so
   the archive contains **no** evidence for v11's premise at all — the spec
   compares the budget against the wrong quantity. See §2.
3. **PF-13 [BLOCKING] — the "genuinely new" falsifiable prediction is
   already confirmed at n=194 in archived data, and v11 proposes to re-test
   it at n<=2 for ~450s of new search.** `RUN-SSIQ-a85692-h`'s own
   `comparison_against_archived` reads `n_value_matches: 203`,
   `n_value_differs: 0`, `non_fp_rational_only: {n_both_resolved: 194,
   n_value_differs: 0}` — i.e. 194 naturally-completed vertices, zero
   truncated, exact agreement with `RUN-SSIQ-a85692-b`'s archived map on
   every one. v11's prediction ("every naturally-completed vertex's value
   MUST equal the archived value exactly") is *that* result, restricted to
   at most 2 vertices. See §3.
4. **PF-14 [BLOCKING] — no machine-load precondition, and the failure mode
   is silent.** This machine has 14 cores and 1-minute load averages I
   measured at **20.56 / 21.22 / 21.24** (the Coordinator separately
   measured 19.45 and 24.15). At ~1.5x oversubscription every wall-clock
   figure inflates, and the b=1.2 arm's entire margin above the floor is
   ~50ms (~4%). PF-8's own well-definedness discipline then makes a
   load-destroyed run report `n_naturally_completed: 0` and
   `naturally_completed_histogram: {}` — **well-formed, honest-looking, and
   indistinguishable from a mathematical finding**. That is the artifact
   tell this program's own inventor protocol §3 warns about, in reverse: a
   quantity that reads as a null when the null was manufactured by the
   execution environment. The existing CROSS-HARDWARE REPRODUCIBILITY
   CAVEAT does not cover it — it addresses *different hardware*, not
   *contention on the same hardware*, and it is a narrative caveat with no
   gate, no measurement, and no abort path. See §4.

Two further findings (PF-15, PF-16) are **ADVISORY**: the standing
per-batch obligations from BATCH-010/012/013 are not carried into this
amendment's text at all (§5), and the `n_timed_out` / `n_still_truncated`
counting conventions are distinct quantities the draft does not distinguish
(§6).

The cheapest complete repair is small and stays inside budget: **move the
upper sweep point from 1.2s into the 1.35–1.45s band, pre-register the
predicted natural-completion count from `RUN-SSIQ-a85692-h`'s own archived
timings, and gate the run on a measured floor calibration on the actual
execution machine.** §7 gives the numbers.

---

## §1 — PF-11: `b=1.2s` cannot observe what the amendment says it exists to
## observe [check area A, and the design question underneath it]

I recomputed the empirical CDF of natural completion times from
`RUN-SSIQ-a85692-h`'s own 194 `per_vertex_records` (that run used
`per_vertex_budget_seconds: 15.0`, resolved 194/194, and recorded **zero**
`timed_out` — so every record is a genuine, unbudgeted natural completion,
which is exactly why its min is the campaign's cited floor):

| budget b | # vertices with natural `wall_seconds` < b | value histogram of that subset |
|---|---|---|
| 1.1 | 0 | `{}` |
| **1.2** | **2** | **`{2: 2}`** |
| 1.3 | 7 | `{2: 4, 3: 3}` |
| **1.4** | **45** | `{2: 19, 3: 19, 4: 3, 6: 1, 7: 1, 8: 2}` |
| **1.45** | **115** | `{2: 28, 3: 43, 4: 8, 5: 20, 6: 4, 7: 6, 8: 6}` |
| 1.5 | 186 | `{2: 33, 3: 65, 4: 10, 5: 41, 6: 9, 7: 16, 8: 12}` |
| 1.7 | 194 (all) | `{2: 34, 3: 70, 4: 10, 5: 42, 6: 10, 7: 16, 8: 12}` |

And the per-value time ranges (min / median / max natural `wall_seconds`):

| delta_E | n | min | median | max |
|---|---|---|---|---|
| 2 | 34 | **1.150** | 1.388 | 1.507 |
| 3 | 70 | 1.257 | 1.436 | 1.699 |
| 4 | 10 | 1.369 | 1.422 | 1.470 |
| 5 | 42 | 1.406 | 1.451 | 1.514 |
| 6 | 10 | **1.394** | 1.458 | 1.522 |
| 7 | 16 | 1.396 | 1.458 | 1.498 |
| 8 | 12 | 1.392 | 1.452 | 1.494 |

**The minimum natural completion time over all vertices with
`delta_E >= 5` is 1.392s.** No such vertex can complete naturally at
`b = 1.2s` — the margin is not marginal, it is 16%, and it is a *floor over
78 vertices*, not a single fast outlier. So the naturally-completed
histogram at b=1.2 is, at best, `{2: 2}`; at b=1.1 it is `{}` by the
amendment's own (correct) construction. The amendment's title question and
its stated core purpose ("to directly observe whether `delta_E>=5` values
appear there **for the first time in this lineage**") are decided before
any compute is spent.

This is not a power complaint in the generic sense the campaign has
previously (correctly) resisted. It is the sharper thing: **the pre-
registered measurement is a constant function of the budget in this range**,
and the constant is already in the archive. Worse, the 2 admissible vertices
are the two fastest in the entire population, which is precisely the
value-extremity selection bias BATCH-012's own standing obligation exists to
prevent — the fastest tail is the *shallowest* tail (`delta_E=2`), so the
one thing the naturally-completed subset at b=1.2 is guaranteed to show is
the artifact BATCH-012 already characterized, re-presented as a new
observation.

The standing obligation is explicit in `goal.yaml`'s own `next_action`: *"a
truncation budget must be sized strictly between the shortest and longest
natural completion times in the relevant population, not merely well below
the shortest."* `b=1.2` satisfies that obligation only in the letter — it
sits at roughly the **1st percentile** of the population (2/194), which is
"barely above the shortest," the mirror image of the failure mode the
obligation names. RT-BATCH-013 proposed "1.1–1.2s" in good faith from the
floor figure alone; the archived per-vertex distribution, which that review
did not tabulate against `delta_e_upper_bound`, shows the proposal needs
correcting rather than executing. **A reviewer's own prediction is a claim
and carries the same burden as any other; this is me discharging that
burden against RT-BATCH-013.**

**Required fix (PF-11):** move the upper sweep point into the informative
band. `SWEEP_BUDGETS = [1.1, 1.4]` or `[1.2, 1.45]` are both defensible and
both stay in budget (§7). At 1.4 the naturally-completed subset is ~45
vertices including 4 with `delta_E >= 5`; at 1.45 it is ~115 including 30
with `delta_E >= 5` — a genuine, non-degenerate test of exactly the
monotone-in-budget-across-the-value-range question `DEC-20260806-520ca4`
item (1) asks. Retain 1.1 as the guaranteed-truncated control arm (it is
sound, see §4).

## §2 — PF-12: what `timed_out` actually means, read in the code [check
## area B — the check the task specifically asked me to make]

`run_truncation_probe_v9` does not compute `timed_out` itself. It copies it
(`delta_e_truncation_probe_v9.py:186`, `timed_out = bool(r["timed_out"])`)
from `compute_delta_e.two_sided_search`, and records it per vertex in
`per_vertex_records` alongside `resolved`, `delta_e_upper_bound`,
`seed_used`, `wall_seconds`. So the **shape** v11 assumes is real: a
per-vertex boolean is returned, unchanged, with no new instrumentation
needed. That part of v11 checks out, and I confirm it.

The **semantics** do not. `two_sided_search` (`compute_delta_e.py:177–210`):

```python
half_budget = None if time_budget_seconds is None else time_budget_seconds / 2.0
table_s, calls_s, to_s = build_smooth_table(field, source_j, rng, q, L, X, half_budget, t0)
t_mid = time.time()
remaining = None if time_budget_seconds is None else max(0.0, time_budget_seconds - (t_mid - t0))
table_t, calls_t, to_t = build_smooth_table(field, target_j, rng, q, L, X, remaining, t_mid)
...
"timed_out": bool(to_s or to_t),
```

and `build_smooth_table` sets `timed_out = True` on the elapsed check at the
top of its heap loop, breaking out with a partial table; otherwise it exits
when the heap is exhausted under the `X = 23` degree cap.

Three consequences, none of which the draft states:

1. **The source table is capped at `b/2`, not `b`.** `timed_out is False`
   requires `t_source <= b/2` **and** `t_source + t_target <= b`. At
   `b = 1.2` that is a 0.6s cap on the source-side expansion. The archived
   `per_vertex_records` record only the *total* `wall_seconds`; the
   source/target split is never persisted anywhere in this lineage. So the
   claim "at b=1.2s, some fast-completing vertices are now expected to
   complete NATURALLY" has **no archival support whatsoever** — not weak
   support, none. If the split is roughly even, the 1.14993s vertex needs
   `t_source ≈ 0.575s` against a 0.6s cap: a coin flip. The realistic
   pre-run expectation for `n_naturally_completed` at b=1.2 is **0 to 2**,
   with 0 entirely plausible even on an idle machine.
2. **"Naturally completed" means "both Dijkstra expansions exhausted their
   heaps under the fixed `(L, X=23, B=23)` class"** — it does *not* mean
   "the true minimal isogeny degree." `two_sided_search`'s own docstring is
   explicit that this is an upper-bound search over a restricted smooth
   class. v11's phrasing — *"per EV-SSIQ-48d274's own derivation the
   returned value IS the confirmed true minimum, not merely a valid upper
   bound"* — needs the qualifier "within the frozen `(L, X)` search class"
   or it overstates what the instrument establishes. This is a wording
   defect with real downstream citation risk, not a nit: the sharper
   prediction is about *reproducing the archived reference value*, not
   about a mathematical minimum.
3. **The prediction is well-founded on the exactness side, and I verified
   why — but the draft asserts it rather than deriving it.** A completed
   table is RNG-independent (the root sets are mathematically determined;
   randomness only affects root-finding, not the finished table), which is
   what actually licenses "naturally completed ⟹ same value regardless of
   seed." And the archived reference is itself un-truncated: I read
   `run_phase_minus1_on_confirmatory_set` and the RUN-b record for p=2437 —
   194/194 attempted and resolved from a `t_prime = 300s` pool using
   284.88s, so every vertex's `per_vertex_cap = min(remaining, t_prime)` was
   **≥ ~15s**, an order of magnitude above the 1.70s maximum natural time.
   Good news for the prediction; but the draft never states this, and its
   consequence for the failure branch is stated *wrongly*: the draft says a
   nonzero mismatch would mean *either* EV-SSIQ-48d274's derivation is
   overturned *or* `timed_out` doesn't mean what is assumed. That is a false
   dichotomy — the third and, a priori, most likely explanation is
   **archived-side truncation or an `(L, X)`-class artifact**, with
   `new_value < archived_value` as its signature. The direction of any
   mismatch is diagnostic and must be reported.

**Required fix (PF-12):** state the `b/2` source-side cap explicitly in
`amendment_scope`, and either (a) require the Executor to record the
per-side split (a two-line change: `two_sided_search` already computes
`t_mid`; if the Executor is not permitted to touch frozen code, record it in
the calibration step of PF-14 instead), or (b) replace the "b=1.2s exceeds
the floor" premise with the honest statement that the effective natural-
completion condition is `max(2*t_source, t_total) <= b` and is **not
predictable from any archived record**. Qualify "confirmed true minimum"
with the `(L, X)` class. Replace the false dichotomy with a three-way
branch that reports mismatch direction.

## §3 — PF-13: the new cross-check is strictly weaker than evidence already
## in the archive

`RUN-SSIQ-a85692-h`'s own `comparison_against_archived`, read directly from
`probe_delta_e_comparison.json`:

```
n_both_resolved: 203, n_value_matches: 203, n_value_differs: 0,
value_differs_triples: [],
non_fp_rational_only: {n_both_resolved: 194, n_value_matches: 194, n_value_differs: 0}
```

with `per_vertex_budget_seconds: 15.0` and **zero** `timed_out` across all
194 records. In this lineage's own language: 194 naturally-completed
vertices, 194/194 exact agreement with the archived map, zero exceptions.

v11's REQUIRED NATURAL-COMPLETION CROSS-CHECK asks exactly this question —
"does every naturally-completed vertex's value equal the archived value
exactly?" — and, at `b ∈ {1.1, 1.2}`, would answer it on **0 to 2**
vertices, at a cost of ~450s of new search. `n_naturally_completed_NOT_matching_archived
= 0` out of 0 or 2 is not a confirmation of anything; the identical
statement is already available at n=194.

I want to be precise about what this does and does not condemn. It does
**not** condemn the cross-check as a mechanism — partitioning by `timed_out`
and testing equality on the naturally-completed side is a good, cheap idea,
and at `b = 1.45` (n≈115, spanning every value class) it would be a genuine
strengthening: it would test equality *in the mixed regime*, where some
vertices in the same run are truncated and others are not, which
`RUN-SSIQ-a85692-h` (uniformly untruncated) cannot test. That is the design
worth freezing. It condemns the cross-check **at the chosen budgets**, where
it degenerates to a re-derivation of an archived result on a 1%-of-population
extremity-selected subsample.

**Required fix (PF-13):** the amendment must disclose `RUN-SSIQ-a85692-h`'s
existing 194/194 exact-match result as the prior state of evidence for this
exact prediction, and state explicitly what the new cross-check adds beyond
it (the mixed-regime test), which requires PF-11's budget change to be
non-empty. Any future citation must not present a `k/k` match at k<=2 as
independent confirmation of a proposition already confirmed at n=194.

## §4 — PF-14: machine load, the silent null, and what should have happened
## to the reported quantity [check area A]

**Re-verified independently.** `sysctl -n hw.ncpu` = **14**. Successive
`uptime` calls in this session: load averages **20.56 / 21.22 / 21.24**
(1/5/15-min). The Coordinator separately observed 19.45 and 24.15. That is
sustained ~1.4x–1.7x oversubscription from concurrent agent worktrees in
this same repository, and the 5- and 15-minute averages show it is not a
transient spike.

The mechanism is direct: `build_smooth_table`'s stopping test is
`time.time() - t0 > time_budget_seconds` — **wall clock**, not CPU time. A
single-threaded expansion that needs 0.6s of CPU on an idle machine needs
~0.9s of wall clock at 1.5x oversubscription. Every natural completion time
in §1's table inflates by roughly that factor while the budget stays fixed.
At `b = 1.2` with a floor of 1.14993s and a source-side cap of 0.6s (§2),
`n_naturally_completed = 0` is the *expected* outcome under current load,
not a tail risk.

**And the run would report that null in perfectly well-formed shape.** v11
pre-applies PF-8's discipline: the naturally-completed histogram is
explicitly `{}` at zero, `n_naturally_completed` is reported alongside every
figure per PF-7. All correct, all honest — and jointly they produce an
artifact in which "the environment was too loaded for any vertex to finish"
is typographically identical to "no vertex finishes naturally at this
budget," which a future reader could reasonably misread as "delta_E>=5
convergence does not begin at the floor." AGENTS rule 3 is unambiguous that
a timeout is never mathematical counterevidence; the draft's own
instrumentation gives a future reader no way to apply that rule, because
nothing in the artifact records whether the timeouts were budget-driven or
contention-driven.

**Is the existing caveat sufficient? No.** The CROSS-HARDWARE
REPRODUCIBILITY CAVEAT addresses a *different machine* producing a
*different set* of naturally-completing vertices, and even asserts that
"the qualitative existence of SOME naturally-completing vertices at b=1.2s
... is robust to modest cross-run timing variation." Given §1 (2/194
candidates, both marginal) and §2 (an unmeasured 0.6s source-side cap),
that sentence is **not supported** and should be withdrawn regardless of
which other fixes are adopted. Contention on the *same* machine is a
distinct, currently-active, and much larger perturbation, and a narrative
caveat is not a control.

**What should the reported quantity do?** `n_naturally_completed` should be
a *monotonically increasing, quantitatively predictable* function of `b`,
and the naturally-completed histogram should converge to
`RUN-SSIQ-a85692-h`'s full histogram `{2:34, 3:70, 4:10, 5:42, 6:10, 7:16,
8:12}` as `b` rises through 1.7s. That gives a free, sharp, pre-registrable
prediction curve from archived data — and a discriminating control: if
measured `n_naturally_completed` falls far below the archived-timing
prediction, the deficit is an execution-environment artifact, not a
mathematical result.

**Required fix (PF-14), four checkable parts:**

1. **Pre-registered prediction.** From `RUN-SSIQ-a85692-h`'s archived
   `wall_seconds`, pre-register in the frozen spec the predicted
   `n_naturally_completed` at each chosen `b` (0 at 1.1; 2 at 1.2; 45 at
   1.4; 115 at 1.45 — the counts in §1), stated as an **upper bound**,
   since the `b/2` source cap of §2 can only reduce it.
2. **Floor calibration on the actual execution machine, before the sweep.**
   Call `run_truncation_probe_v9(graph, BASE_SEED, 15.0)` on a **fixed,
   pre-registered 8-vertex subsample** — the 8 vertices with the smallest
   archived `wall_seconds` in `RUN-SSIQ-a85692-h` (named by coordinate in
   the frozen spec, so it cannot be chosen after the fact) — and record each
   measured natural time. Worst-case cost ~120s at the 15s cap; realistic
   cost ~10–20s. This directly re-measures the floor under whatever load
   the machine is actually carrying.
3. **Abort/defer gate, pre-registered.** If the calibrated floor
   (min measured natural time on that subsample) **exceeds the largest
   sweep budget**, the run is **DEFERRED** — no
   `truncation_sweep_comparison.json` claiming a natural-completion result
   is written, and the outcome is recorded as an infra/environment
   condition under AGENTS rule 3, never as evidence about delta_E
   convergence. If the calibrated floor exceeds the archived 1.14993s by
   more than a pre-registered factor (I suggest 1.15x), the truncated-side
   sweep may still proceed but the natural-completion cross-check's result
   must be labelled `load_confounded: true` in the artifact itself.
4. **Load recorded in the manifest, not just in prose.** Record
   `hw.ncpu` and the 1/5/15-minute load averages in `environment.json`
   **at run start and at run end**, and require `execution_report.yaml` to
   state them next to `n_naturally_completed`. This is the null-object
   discipline applied to the execution environment: without it, the
   measurement has no control against the hypothesis "the machine did it."

**The counter-consideration, honestly weighed: the b=1.1s arm is robust.**
Load can only *increase* wall times, and 1.1s is below the idle-machine
floor of 1.14993s (0 of 194 archived records below it). Contention pushes
completion times further above the budget, so "every vertex is truncated at
b=1.1" is monotone-safe under load — it can fail only if the execution
machine is *faster* than the one that produced `RUN-SSIQ-a85692-h`, which
is the ordinary cross-hardware caveat, not the load mechanism. Keep the
1.1s arm; it is the one part of this instrument that load cannot corrupt.
(It is also, on its own, a modest increment over v10's 1.0s point — its
value is as a control, not as a new observation, and the spec should say
so.)

## §5 — PF-15 [ADVISORY]: the standing per-batch obligations are not carried
## into the amendment's text [check area C]

A full-file grep of `specification_v11.yaml` for `extremity`, `selection`,
`BATCH-012`, `strength_note`, and `propagat` returns **zero matches**. What
the goal record's `next_action` requires of "any future amendment":

- **BATCH-012 (EV-SSIQ-c3df82, 13th knowledge candidate)**: any resolved
  subsample from a time-budget-truncated randomized search must be checked
  for value-extremity selection bias and Frobenius-conjugate-pair
  correlation before being cited as informative about the full population.
  **Partially carried**: `value_histogram_and_conjugate_pairs` is required
  per sweep point over the *resolved* set. **Not carried**: no such check is
  required for the genuinely new **naturally-completed** subset, which is
  the most extremity-selected subsample this lineage has ever cited (the
  literal fastest tail — see §1). This is the single most load-bearing
  omission in the group.
- **BATCH-010 (EV-SSIQ-a64d92 O-3)**: caveats/confounds must propagate into
  every artifact a future reader might consult first. **Not carried**: the
  CROSS-HARDWARE caveat lives in `amendment_scope` prose only; nothing
  requires it (or PF-14's load figures) to appear in
  `truncation_sweep_comparison.json` itself, which is precisely the artifact
  a future reader consults first.
- **BATCH-013 (EV-SSIQ-48d274, 14th knowledge candidate)**: the evidence-
  strength distinction between a first-principles-derived, zero-exception-
  confirmed, independently-reproduced finding and a merely-observed pattern
  must be stated explicitly in any future evidence record's `strength_note`.
  **Not carried**: no `strength_note` requirement anywhere. Given §3, this
  matters concretely — a `2/2` match must not inherit the derivation-tier
  language v10 earned at 194/194.
- **BATCH-011 (EV-SSIQ-69ba8b, 12th)**: an amendment auditing an instrument
  against a hypothesis must first check whether the instrument's own
  correctness invariants make the planned comparison capable of
  discriminating the hypothesis at all. **Not carried, and this is the
  obligation whose discharge would have caught PF-11 and PF-12 at drafting
  time.** §1 and §2 are exactly that check, performed late.

**Required fix (PF-15):** carry all four explicitly, with the BATCH-012
check extended by name to the naturally-completed subset, the BATCH-010
propagation requirement naming `truncation_sweep_comparison.json` and
`execution_report.yaml` as the artifacts that must carry the caveats
in-band, and a required `strength_note` clause pre-committing that the
cross-check's evidence tier scales with `n_naturally_completed`.

## §6 — PF-16 [ADVISORY]: three different "timed out" counts

`run_truncation_probe_v9` returns `n_timed_out` counted over **all 194
attempted** vertices. v11 additionally requires `n_still_truncated`, counted
over **resolved** vertices only, and asserts `n_naturally_completed +
n_still_truncated == n_resolved` (correct, and correctly required to be
checked rather than assumed). But a third population exists and is never
named: vertices that are `resolved=False` — and among those, `timed_out`
may be either True (budget ran out) or False (both tables completed and no
collision exists inside the `(L, X)` class). So `n_timed_out >=
n_still_truncated` in general, with the gap being unresolved-and-timed-out
vertices, and `n_timed_out` is **not** a superset statistic anyone should
compare directly against `n_still_truncated`.

**Required fix (PF-16):** define all three counts explicitly in the frozen
spec (`n_timed_out` over attempted; `n_still_truncated` over resolved;
`n_unresolved_and_not_timed_out` — the genuinely interesting residual, which
would indicate a vertex whose full `(L, X)`-class search found no collision
at all), and require the identity
`n_timed_out = n_still_truncated + n_unresolved_and_timed_out` be reported.

## §7 — Budget arithmetic, and what the right bound is [check area D]

**`194 * 2.3 = 446.2s` is arithmetically correct** (`1.1 + 1.2 = 2.3`), and
`1000 / 446.2 = 2.24x`, as stated. `total_cpu_hours: 0.33` against
`wall_clock_seconds_per_run: 1000` is consistent (`1000/3600 = 0.278`),
matching this lineage's generous-rounding precedent.

**It is not the right bound, for two reasons the draft should absorb:**

1. **Overshoot.** The budget check sits at the *top* of `build_smooth_table`'s
   heap loop, so a vertex can overshoot its slice by one pop's work (up to
   9 modular-polynomial root-findings). RT-BATCH-013 measured this on the
   real v10 run: `b=0.6 → 121.33s` against a 116.4s bound (**+4.2%**),
   `b=0.8 → 157.39s` (+1.4%), `b=1.0 → 195.02s` (+0.5%). Small, but nonzero,
   and it grows under contention.
2. **Load.** At the measured ~1.5x oversubscription, the *wall-clock* figure
   the 1000s cap governs is not the search-time figure. Truncated vertices
   are budget-bounded (a truncated vertex takes ~`b` wall seconds regardless
   of load — load makes it do *less work*, not take more time), so the
   headline bound is fairly load-robust; but the graph build (~1–2s idle),
   the JSON I/O, and the overshoot term all inflate. Realistic worst case
   under current load: ~470–500s, still comfortably inside 1000s.

**Under PF-11's recommended fix the budget still holds**, which is the point
of recommending it: `[1.1, 1.4]` → `194 * 2.5 = 485s`; `[1.2, 1.45]` →
`194 * 2.65 = 514.1s`; adding PF-14's ~120s worst-case calibration →
~605–635s worst case, still within the existing 1000s / 0.33 CPU-hour
budget with ~1.6x margin. **No budget increase is required to fix this
amendment.** If the Coordinator prefers a wider margin, raising
`wall_clock_seconds_per_run` to 1200 (v10's own value) costs nothing.

## §8 — What is sound, verified directly, and should not be re-litigated

Stated plainly so the fix pass does not disturb it:

- **Every cited function exists with the cited signature.**
  `run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds)`
  (line 147, pure, no disk I/O, no internal `verify_graph_identity`, fresh
  `random.Random` per vertex, F_p-rational wiring before the loop, returns
  per-vertex `resolved`/`delta_e_upper_bound`/`wall_seconds`/`timed_out`);
  `parse_v8_new_delta_map(path)` (302); `compare_against_archived(new,
  archived, non_fp_rational_set)` (224); `compare_against_v8(new, v8,
  non_fp_rational_set)` (328). All re-read this session.
- **`delta_e_truncation_sweep_v10.value_histogram_and_conjugate_pairs(resolved_non_fp_set,
  new_delta_map, field)` (164–219) is genuinely reusable**: pure, no
  module-level state, no I/O, PF-8's `n_resolved == 0` case explicitly
  handled, self-conjugate and odd-`n_paired` anomalies loudly reported
  rather than assumed away. v11's "first reuse of a v10-defined function"
  claim is accurate. One plumbing note the draft *does* leave implicit and
  should state (it is the same note PF-9 attached to the comparison
  functions in v10 round 2): `resolved_non_fp_set` is not returned by
  `run_truncation_probe_v9`'s output dict and must be reconstructed from
  `per_vertex_records` (`resolved is True`) or from `graph`.
- **v10's procedural fixes are pre-applied without a review round**: PF-2
  per-sweep-point exception isolation over the whole bundle with incremental
  accumulation and an unconditional final write; PF-7 power framing; PF-8
  empty-histogram well-definedness; PF-9-style explicit function-level diff
  including `compare_against_*`; PF-10 step-(0) uncaught-propagation
  discipline stated explicitly. Each verified against the draft text. This
  is exactly the behavior the two prior rounds were trying to induce.
- **Seed isolation holds.** `BASE_SEED = 20260811` unchanged;
  `derive_per_vertex_seed(base_seed, v)` is a pure function of
  `(base_seed, vertex)`; budget remains the sole manipulated variable.
- **Scope discipline is clean.** `OBJECTIVE_BOUNDARY` correctly excludes
  H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label, and
  lever L4, is scoped to p=2437 only, and correctly declines to answer
  RT-BATCH-011's original truncation-boundary question, citing
  `DEC-20260806-520ca4` D-3's confound constraint. No affected/safe scheme
  list anywhere. No scope inflation found.

---

## Objections

- **OBJ-1 [PF-11, BLOCKING]**: at `b = 1.2s` the naturally-completed subset
  is, from `RUN-SSIQ-a85692-h`'s own archived natural completion times,
  **2 of 194 vertices, both with `delta_E = 2`**; the fastest vertex with
  `delta_E >= 5` takes **1.392s**. The amendment's own headline question
  ("does `delta_E>=5` convergence begin appearing there?") is therefore
  answered NO with certainty before the run, and the run cannot produce
  evidence about it. The 2 admissible vertices are the extreme fastest tail
  — the exact value-extremity selection bias BATCH-012's standing obligation
  names. `b = 1.2` sits at ~the 1st percentile of the natural completion
  distribution, satisfying "strictly between shortest and longest" only in
  the letter.
- **OBJ-2 [PF-12, BLOCKING]**: `timed_out` is `to_s or to_t` from
  `two_sided_search`, which caps the **source** table at
  `time_budget_seconds / 2.0` and the target at the remainder. Natural
  completion at `b` requires `t_source <= b/2`, not `t_total <= b`. At
  `b=1.2` that is a 0.6s source-side cap against a median total natural time
  of 1.44s. `RUN-SSIQ-a85692-h` records only totals, so the archive contains
  no support for the "some vertices complete naturally at 1.2s" premise.
  Separately, `timed_out is False` establishes exactness only **within the
  frozen `(L, X=23, B=23)` search class**, not "the true minimum" as the
  draft states, and the draft's failure branch is a false dichotomy that
  omits the a priori most likely third explanation (archived-side or
  class-boundary artifact, signature `new_value < archived_value`).
- **OBJ-3 [PF-13, BLOCKING]**: the "genuinely new" falsifiable prediction is
  already confirmed at n=194 with zero exceptions in archived data —
  `RUN-SSIQ-a85692-h` ran at `per_vertex_budget_seconds: 15.0` with **zero**
  `timed_out` and `comparison_against_archived.non_fp_rational_only:
  {n_both_resolved: 194, n_value_differs: 0}`. v11 proposes to re-test it at
  n<=2 for ~450s of new search, without disclosing the prior evidence state.
  The mechanism is good; at these budgets it degenerates.
- **OBJ-4 [PF-14, BLOCKING]**: no machine-load precondition, measurement,
  gate, or calibration, on a machine I measured at 14 cores and load
  averages 20.56/21.22/21.24 (~1.5x oversubscription), against a b=1.2 arm
  whose entire margin above the floor is ~50ms (~4%) — and whose real
  constraint is a 0.6s source-side cap (OBJ-2). Under load,
  `n_naturally_completed = 0` is the expected outcome, and PF-8's own
  well-definedness discipline renders it as a well-formed `{}` histogram
  indistinguishable from a mathematical finding, in violation of the spirit
  of AGENTS rule 3 (a timeout is never mathematical counterevidence). The
  existing CROSS-HARDWARE caveat covers a different mechanism, has no gate,
  and contains an unsupported assurance ("the qualitative existence of SOME
  naturally-completing vertices at b=1.2s ... is robust") that should be
  withdrawn.
- **OBJ-5 [PF-15, advisory]**: zero matches in the full spec text for
  `extremity`, `selection`, `BATCH-012`, `strength_note`, `propagat` — the
  standing obligations from BATCH-010 (caveat propagation into first-consulted
  artifacts), BATCH-012 (value-extremity/conjugate-pair check, here needed
  specifically for the naturally-completed subset), BATCH-011 (check the
  instrument's own invariants make the comparison discriminating at all —
  the obligation whose discharge would have caught OBJ-1 and OBJ-2 at
  drafting time), and BATCH-013 (evidence-strength distinction in a
  `strength_note`) are not carried into this amendment's text.
- **OBJ-6 [PF-16, advisory]**: `n_timed_out` (over all attempted),
  `n_still_truncated` (over resolved), and the unnamed third population
  (unresolved, whether timed out or not — including the genuinely
  interesting `resolved=False, timed_out=False` case of a complete
  `(L,X)`-class search that found no collision) are conflatable as drafted;
  only the resolved-side identity is required.

## Required controls

- **[PF-11, BLOCKING]**: replace `SWEEP_BUDGETS = [1.1, 1.2]` with a list
  whose upper point lands in the informative band — `[1.1, 1.4]` (n_natural
  ≈ 45, first `delta_E >= 5` appearances: 4) or `[1.2, 1.45]` (n_natural
  ≈ 115, of which 30 have `delta_E >= 5`) — retaining a sub-floor point as
  the guaranteed-truncated control. Justify the choice against the archived
  per-value time table in §1, not against the floor alone. Both options stay
  inside the existing 1000s budget (§7).
- **[PF-12, BLOCKING]**: state the `time_budget_seconds / 2.0` source-side
  cap explicitly; restate the natural-completion condition as
  `max(2*t_source, t_total) <= b`; either require the per-side split to be
  recorded (PF-14's calibration step is the cheapest place) or withdraw the
  claim that archived totals predict natural completion. Qualify "confirmed
  true minimum" with "within the frozen `(L, X=23, B=23)` search class."
  Replace the two-way failure dichotomy with a three-way branch that reports
  mismatch **direction** and names archived-side/class-boundary artifact as
  the third explanation.
- **[PF-13, BLOCKING]**: disclose `RUN-SSIQ-a85692-h`'s existing 194/194
  exact-match, zero-timed_out result as the prior evidence state for this
  exact prediction, and state what the new cross-check adds beyond it (the
  mixed-regime test, which only exists once PF-11's fix makes the
  naturally-completed subset non-degenerate). Pre-commit that no `k/k` match
  at small `k` is cited as independent confirmation.
- **[PF-14, BLOCKING]**: four parts — (a) pre-register the predicted
  `n_naturally_completed` at each budget from `RUN-SSIQ-a85692-h`'s archived
  timings, as an upper bound; (b) require a pre-sweep floor calibration on
  the actual execution machine, over a **fixed, coordinate-named 8-vertex
  subsample** (the 8 fastest archived vertices) at the 15.0s reference
  budget, ~120s worst case; (c) pre-register an abort/defer gate — if the
  calibrated floor exceeds the largest sweep budget, DEFER the run as an
  infra condition under AGENTS rule 3 with no natural-completion result
  written, and if the calibrated floor exceeds 1.15x the archived 1.14993s,
  proceed but stamp `load_confounded: true` into the artifact; (d) record
  `hw.ncpu` and 1/5/15-minute load averages in `environment.json` at run
  start and end, and require `execution_report.yaml` to print them adjacent
  to `n_naturally_completed`. Withdraw the unsupported "robust to modest
  cross-run timing variation" assurance from the CROSS-HARDWARE caveat.
- **[PF-15, advisory]**: carry the four standing obligations explicitly,
  with BATCH-012's extremity/conjugate-pair check extended **by name** to
  the naturally-completed subset, BATCH-010's propagation requirement naming
  `truncation_sweep_comparison.json` and `execution_report.yaml` as the
  artifacts that must carry the caveats in-band, and a required
  `strength_note` clause scaling the claimed evidence tier to
  `n_naturally_completed`.
- **[PF-16, advisory]**: define `n_timed_out`, `n_still_truncated`, and
  `n_unresolved_and_not_timed_out` explicitly and require the full identity
  be reported.
- Also advisory, no PF number needed: state explicitly how
  `resolved_non_fp_set` is derived for `value_histogram_and_conjugate_pairs`
  (from `per_vertex_records`' `resolved is True`, or from `graph`), the same
  plumbing note PF-9 attached to the comparison functions in v10 round 2.
- PF-15 and PF-16 do not block freeze independently; PF-11 through PF-14 do,
  collectively and individually — each is demonstrated against archived data
  or against the real frozen code, not hypothesized.

## Counterexample or mutation

**The cheapest discriminating control is free and already computed.**
Before spending any new search time, tabulate `RUN-SSIQ-a85692-h`'s 194
archived natural `wall_seconds` against their `delta_e_upper_bound` values
(§1's two tables). This *is* the counterexample: it shows the fastest
`delta_E >= 5` vertex at 1.392s, which falsifies the premise that `b=1.2s`
can observe `delta_E >= 5` natural convergence. Any Coordinator or reviewer
can reproduce it in ten lines of Python against a committed artifact.

**The cheapest discriminating control for the load confound** is PF-14(b):
re-run the 8 fastest vertices at the reference 15.0s budget on the actual
execution machine and compare the measured floor against 1.14993s. If the
measured floor is ≥ 1.2s, the b=1.2 arm's natural-completion cross-check is
guaranteed empty for environmental reasons and the run must not report that
emptiness as a result. Cost: ~10–20s realistic, ~120s worst case.

**The null-object control for the cross-check itself**, once budgets are
fixed: the measured `n_naturally_completed(b)` must track the archived
prediction curve (0 / 2 / 45 / 115 at 1.1 / 1.2 / 1.4 / 1.45, as upper
bounds given §2's source-side cap). A measured count far below the archived
prediction is an execution-environment artifact and must be reported as
such, not as a property of delta_E convergence. A quantity that stays flat
when the archived timings say it should climb steeply through 1.4–1.5s is
the artifact tell, and this spec should pre-commit to reading it that way.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
unchanged from BATCH-013: toy-scale, single-prime search-procedure
diagnostic work, `H-SSIQ-36e970.asymptotic_claim: null` throughout,
`heuristic_assumptions` empty, correctly inherited. The operative baseline
is **the archived evidence this amendment must beat to be worth running**:
`RUN-SSIQ-a85692-h` already establishes, at n=194 with zero exceptions and
zero timeouts, exactly the equality the new cross-check predicts (§3). An
amendment whose novel measurement is strictly dominated by an existing
artifact on every axis — sample size, value coverage, selection bias — has
not cleared its own baseline. PF-11's budget fix is what makes it clear it:
at `b ≈ 1.45` the cross-check tests equality in the **mixed** regime (some
vertices truncated, some not, in one run), which `RUN-SSIQ-a85692-h`
structurally cannot test.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty;
`asymptotic_claim: null`; no numbered heuristic is implicated. The one
implicit modelling assumption this amendment *does* introduce — "a vertex
whose total natural completion time is below `b` will complete naturally at
budget `b`" — is not a heuristic in the exponent-first sense but is
nonetheless **false as stated**, for the structural reason in §2 (the `b/2`
source-side cap). It should be stated and corrected rather than left
implicit.

## Cost model challenges

`194 * (1.1 + 1.2) = 446.2s` is arithmetically correct, and `1000/446.2 =
2.24x` as stated. Two corrections to what that bound covers: (i) the budget
check is at the top of `build_smooth_table`'s loop, so per-vertex overshoot
by up to one heap-pop is possible — measured at +4.2% / +1.4% / +0.5% on
v10's real run at b=0.6/0.8/1.0 (RT-BATCH-013); (ii) under the measured
~1.5x oversubscription the truncated-vertex term is roughly load-invariant
(a truncated vertex consumes ~`b` wall seconds and simply does less work),
but graph build, I/O, and overshoot inflate; realistic worst case ~470–500s.
Under PF-11's recommended budgets plus PF-14's calibration the worst case
rises to ~605–635s, still inside the existing 1000s / 0.33 CPU-hour budget
with ~1.6x margin — **no budget increase is required to fix this
amendment**, though restoring v10's 1200s cap would cost nothing. No
`total expected cost = per-attempt cost × inverse success probability`
computation applies: bounded, single-run, non-probabilistic-success
diagnostic.

## Reduction and scope challenges

No affected/safe cryptographic scheme list anywhere;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated and not
exceeded. `OBJECTIVE_BOUNDARY` correctly excludes the real-arm prediction,
any PERSISTS/WEAKENS label, and lever L4, is scoped to p=2437 alone, and
correctly declines to answer RT-BATCH-011's original truncation-boundary
question per `DEC-20260806-520ca4` D-3. No scope inflation found. The one
scope risk is **downstream, not in this text**: a `n_naturally_completed: 0`
outcome (§4) invites a future reader to convert an environmental null into a
statement about delta_E convergence, which PF-14's gate and PF-15's caveat
propagation exist to prevent. And per the closure-scrutiny rule: were this
run's null later cited as evidence that "convergence to `delta_E >= 5` does
not begin at the floor," that would be a closure claim resting on a
measurement that was structurally incapable of observing the phenomenon —
a fatigue report about the instrument, not a statement about the object.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; a direct instrument-level
search-procedure diagnostic, not a proof-oriented proposal. Attacked and
held, unchanged from v8/v9/v10 review history.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v11.yaml` as committed
at `6b6703ee2` (draft, `pre_freeze_review.status: PENDING`, no
implementation file yet written): the amendment's procedural architecture is
sound and pre-applies every one of v10's ten hard-won fixes without needing a
review round to rediscover them; the seed-isolation argument holds; the
cited functions all exist with the cited signatures and `timed_out` is
genuinely returned per-vertex in the shape v11 assumes; the budget
arithmetic is correct; the scope boundary is clean; and the `b = 1.1s`
guaranteed-truncated control arm is robust to the machine-load confound.
It is **not** safe to freeze: the choice of `b = 1.2s` as the "above the
floor" arm is refuted by the archived data the amendment itself cites
(2/194 vertices, both `delta_E = 2`; fastest `delta_E >= 5` vertex at
1.392s, PF-11); `timed_out`'s real semantics impose an unmeasured `b/2`
source-side cap that removes what little archival support that arm had and
qualify "true minimum" to the frozen `(L, X)` class (PF-12); the
cross-check's falsifiable prediction is already confirmed at n=194 with zero
exceptions in `RUN-SSIQ-a85692-h` and would be re-tested here at n<=2
(PF-13); and on a machine measured at 14 cores under load averages
20.56/21.22/21.24 the expected outcome is a well-formed, silent,
environment-manufactured `n_naturally_completed: 0` with no gate,
calibration, or recorded load to distinguish it from a finding (PF-14). All
four fixes are cheap: three are textual and one is a ~120s-worst-case
calibration step, and the corrected design fits inside the existing budget
with ~1.6x margin. The underlying *mechanism* — partitioning by `timed_out`
and testing exact equality on the naturally-completed side — is a good idea
that becomes genuinely informative, and genuinely new relative to
`RUN-SSIQ-a85692-h`, at a budget in the 1.35–1.45s band.

## Next concrete action

Coordinator: in one pass, (1) change `SWEEP_BUDGETS` to `[1.1, 1.4]` or
`[1.2, 1.45]`, justified against §1's archived per-value completion-time
table rather than against the floor alone; (2) state the `b/2` source-side
cap and requalify "true minimum" to the frozen `(L, X=23, B=23)` class,
replacing the two-way mismatch dichotomy with a three-way branch reporting
mismatch direction; (3) disclose `RUN-SSIQ-a85692-h`'s existing 194/194
zero-exception exact-match result as the prior evidence state and state what
the mixed-regime cross-check adds beyond it; (4) add the PF-14 load package
— pre-registered `n_naturally_completed` predictions from archived timings,
a coordinate-named 8-vertex 15.0s floor calibration before the sweep, a
pre-registered defer/`load_confounded` gate, and start/end load averages in
`environment.json` — and withdraw the unsupported robustness sentence from
the CROSS-HARDWARE caveat; (5) apply PF-15 and PF-16 in the same pass. Then
request one short, focused round-2 pre-freeze review scoped to (a) the new
budget's predicted natural-completion counts being correctly transcribed
from archived data, and (b) the defer gate being stated as a hard
precondition rather than a caveat — before dispatching the ~500–635s of
real compute.

## Overall verdict

**DO-NOT-FREEZE.** Four blocking findings, all demonstrated against
already-committed artifacts or the real frozen code rather than
hypothesized: the upper sweep budget cannot observe the phenomenon the
amendment exists to observe (PF-11, from `RUN-SSIQ-a85692-h`'s own archived
per-vertex completion times); `timed_out`'s real semantics impose a `b/2`
source-side cap that the spec's floor comparison ignores and the archive
cannot resolve (PF-12, from `compute_delta_e.two_sided_search`); the
"genuinely new" prediction is already confirmed at n=194 and would be
re-tested at n<=2 (PF-13); and the execution environment is currently loaded
to ~1.5x oversubscription with no precondition, calibration, gate, or
recorded measurement to keep a manufactured null from reading as a finding
(PF-14). Two advisory findings (PF-15 standing-obligation carry-forward,
PF-16 counting conventions) should be applied in the same pass. The
amendment's procedural discipline is the best this lineage has produced
pre-review — v10's ten fixes are all carried without prompting — and the
cross-check mechanism is worth keeping; it is the budget choice, inherited
in good faith from RT-BATCH-013's own prediction, that must change, and
correcting it costs no additional compute budget.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v11
  task_id: TASK-20260807-43d16f
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v11.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: PENDING,
    verdict: null), committed at 6b6703ee2 (ancestor of HEAD 6b692c2df,
    clean tree) -- a two-point "floor-straddling" truncation sweep
    (SWEEP_BUDGETS = [1.1, 1.2] seconds) amending the frozen
    specification_v10.yaml (ca905c2482e00fef5b0bdc6902b43a77a43c8d5c),
    implementing item (1) of DEC-20260806-520ca4's ranked resume action
    (RT-BATCH-013's own falsifiable prediction): test whether delta_E>=5
    convergence begins appearing as the per-vertex budget crosses the
    observed 1.14993s natural-completion floor while delta_E=2/3 remain
    exactly converged, via a genuinely new natural-completion cross-check
    partitioning each sweep point's resolved vertices by their own
    timed_out flag. No implementation file exists yet as of the reviewed
    commit -- this audits the plan, not executing code. Round 1 pre-freeze
    review, first round for this amendment.
  objections:
    - "OBJ-1 [PF-11, BLOCKING]: at b=1.2s the naturally-completed subset is, per RUN-SSIQ-a85692-h's own archived per_vertex_records (per_vertex_budget_seconds 15.0, n_resolved 194, ZERO timed_out -- so every record is a genuine unbudgeted natural completion), exactly 2 of 194 vertices, and BOTH have delta_e_upper_bound = 2. The minimum natural completion time over all 78 vertices with delta_E >= 5 is 1.392s, 16% above the largest sweep budget. The amendment's own headline question -- does delta_E>=5 convergence begin appearing in the naturally-completed subset at b=1.2s -- is therefore answered NO with certainty before any compute is spent, and no outcome of the run can be evidence about it. The 2 admissible vertices are the extreme fastest (hence shallowest) tail, exactly the value-extremity selection bias BATCH-012's standing obligation exists to prevent; b=1.2 sits at ~the 1st percentile of the natural-completion distribution, satisfying 'sized strictly between the shortest and longest natural completion times' only in the letter. Archived counts below candidate budgets: 1.1 -> 0; 1.2 -> 2 ({2:2}); 1.3 -> 7 ({2:4,3:3}); 1.4 -> 45 ({2:19,3:19,4:3,6:1,7:1,8:2}); 1.45 -> 115 ({2:28,3:43,4:8,5:20,6:4,7:6,8:6}); 1.5 -> 186; 1.7 -> 194."
    - "OBJ-2 [PF-12, BLOCKING]: timed_out does not have the semantics v11's sharper prediction assumes. run_truncation_probe_v9 copies it verbatim from compute_delta_e.two_sided_search (delta_e_truncation_probe_v9.py:186), which sets timed_out = bool(to_s or to_t) after giving the SOURCE table half_budget = time_budget_seconds / 2.0 and the target table only the remainder (compute_delta_e.py:185-192). Natural completion at budget b therefore requires t_source <= b/2 AND t_total <= b -- at b=1.2 a 0.6s source-side cap against a median total natural time of 1.44s. RUN-SSIQ-a85692-h persists only total wall_seconds, never the per-side split, so the archive contains NO support for the premise that some vertices complete naturally at b=1.2s; the realistic pre-run expectation is 0 to 2 even on an idle machine. Separately, timed_out=False establishes exactness only within the frozen (L, X=23, B=23) smooth-degree search class (two_sided_search's own docstring is explicit that this is an upper-bound search), not 'the confirmed true minimum' as amendment_scope states; and the draft's failure branch is a false dichotomy (either EV-SSIQ-48d274 is overturned or timed_out means something else) that omits the a priori most likely third explanation, an archived-side or class-boundary artifact, whose signature is new_value < archived_value. On the exactness side the prediction is in fact well-founded and I verified why -- a completed table is RNG-independent, and RUN-SSIQ-a85692-b's archived p=2437 map gave every vertex a per_vertex_cap >= ~15s (194/194 attempted and resolved from a 300s t_prime pool using 284.88s), an order of magnitude above the 1.70s maximum natural time -- but the draft asserts this rather than deriving it."
    - "OBJ-3 [PF-13, BLOCKING]: the 'genuinely new' falsifiable prediction is already confirmed at n=194 with zero exceptions in archived data. RUN-SSIQ-a85692-h's comparison_against_archived reads n_both_resolved 203, n_value_matches 203, n_value_differs 0, value_differs_triples [], non_fp_rational_only {n_both_resolved 194, n_value_matches 194, n_value_differs 0}, at per_vertex_budget_seconds 15.0 with zero timed_out -- i.e. 194 naturally-completed vertices, 194/194 exact agreement with RUN-SSIQ-a85692-b's archived map. v11 proposes to re-test that same proposition on 0-2 vertices for ~450s of new search, without disclosing the prior evidence state. The cross-check MECHANISM is good and would be genuinely new at b ~ 1.45, where it would test equality in the MIXED regime (some vertices truncated and some not within one run), which the uniformly-untruncated RUN-SSIQ-a85692-h structurally cannot test."
    - "OBJ-4 [PF-14, BLOCKING]: no machine-load precondition, calibration, gate, or recorded measurement. Independently re-verified this session: sysctl -n hw.ncpu = 14; successive uptime 1/5/15-minute load averages 20.56 / 21.22 / 21.24 (Coordinator separately observed 19.45 and 24.15) -- sustained ~1.4x-1.7x oversubscription, not a transient spike, from concurrent agent worktrees in this repository. build_smooth_table's stopping test is wall-clock (time.time() - t0 > time_budget_seconds), not CPU time, so every natural completion time inflates ~proportionally while the budget stays fixed; against a ~50ms (~4%) nominal margin and a 0.6s unmeasured source-side cap (OBJ-2), n_naturally_completed = 0 is the EXPECTED outcome under current load. v11's own (correct) PF-8 discipline then renders that as a well-formed empty histogram {} alongside n_naturally_completed 0 -- honest-looking, schema-valid, and indistinguishable from a mathematical finding that delta_E>=5 convergence does not begin at the floor, contrary to AGENTS rule 3. The existing CROSS-HARDWARE REPRODUCIBILITY CAVEAT does not cover this: it addresses a different machine producing a different naturally-completing SET, not contention on the same machine; it is narrative with no gate, no measurement and no abort path; and it contains an assurance ('the qualitative existence of SOME naturally-completing vertices at b=1.2s ... is robust to modest cross-run timing variation') that OBJ-1 and OBJ-2 show is unsupported and that should be withdrawn regardless of which other fixes are adopted. The b=1.1s arm, by contrast, IS robust: load can only increase wall times, so 'every vertex truncated below the floor' is monotone-safe under contention."
    - "OBJ-5 [PF-15, advisory]: a full-file grep of specification_v11.yaml for 'extremity', 'selection', 'BATCH-012', 'strength_note' and 'propagat' returns zero matches. The goal record's next_action standing obligations are not carried: BATCH-012's value-extremity/conjugate-pair check is carried only for the resolved set (via value_histogram_and_conjugate_pairs) and NOT for the genuinely new naturally-completed subset, which is the most extremity-selected subsample this lineage has ever proposed to cite; BATCH-010's caveat-propagation obligation is unmet (the CROSS-HARDWARE caveat lives in amendment_scope prose only, with nothing requiring it or the load figures to appear in truncation_sweep_comparison.json, the artifact a future reader consults first); BATCH-013's evidence-strength distinction has no strength_note requirement anywhere, so a 2/2 match could inherit derivation-tier language v10 earned at 194/194; and BATCH-011's obligation to first check whether the instrument's own invariants make the planned comparison discriminating at all is exactly the check whose discharge would have caught OBJ-1 and OBJ-2 at drafting time."
    - "OBJ-6 [PF-16, advisory]: three distinct counting populations are conflatable as drafted. run_truncation_probe_v9 returns n_timed_out counted over all 194 ATTEMPTED vertices; v11's n_still_truncated is counted over RESOLVED vertices only; and a third population is never named -- resolved=False vertices, among which timed_out may be True (budget exhausted) or False (both tables completed with no collision inside the (L,X) class, a genuinely interesting outcome). So n_timed_out >= n_still_truncated in general and the two must not be compared directly. Only the resolved-side identity (n_naturally_completed + n_still_truncated == n_resolved, correctly required to be checked rather than assumed) is specified."
  required_controls:
    - "[PF-11, BLOCKING]: replace SWEEP_BUDGETS = [1.1, 1.2] with an upper point in the informative band -- [1.1, 1.4] (predicted n_naturally_completed ~45, including 4 vertices with delta_E >= 5) or [1.2, 1.45] (~115, including 30 with delta_E >= 5) -- retaining a sub-floor point as the guaranteed-truncated control arm, and justify the choice against the archived per-value completion-time table, not against the floor minimum alone. Both options stay inside the existing 1000s budget."
    - "[PF-12, BLOCKING]: state the time_budget_seconds/2.0 source-side cap explicitly; restate the natural-completion condition as max(2*t_source, t_total) <= b; either require the per-side split to be recorded (cheapest in PF-14's calibration step) or withdraw the claim that archived total times predict natural completion. Qualify 'confirmed true minimum' with 'within the frozen (L, X=23, B=23) search class'. Replace the two-way mismatch dichotomy with a three-way branch reporting mismatch DIRECTION and naming archived-side/class-boundary artifact (new_value < archived_value) as the third explanation. State, rather than assume, the two facts that actually license the prediction: completed tables are RNG-independent, and RUN-SSIQ-a85692-b gave every p=2437 vertex a >= ~15s cap."
    - "[PF-13, BLOCKING]: disclose RUN-SSIQ-a85692-h's existing 194/194 zero-exception, zero-timed_out exact-match result as the prior evidence state for this exact prediction, and state explicitly what the new cross-check adds beyond it (the mixed-regime test, which only becomes non-degenerate once PF-11's budget fix is applied). Pre-commit that no k/k match at small k is cited as independent confirmation of a proposition already confirmed at n=194."
    - "[PF-14, BLOCKING]: (a) pre-register, in the frozen spec, the predicted n_naturally_completed at each chosen budget derived from RUN-SSIQ-a85692-h's archived wall_seconds, stated as an UPPER bound since the b/2 source cap can only reduce it; (b) require a pre-sweep floor calibration on the actual execution machine -- run_truncation_probe_v9(graph, BASE_SEED, 15.0) over a FIXED, coordinate-named 8-vertex subsample (the 8 fastest archived vertices), ~120s worst case, ~10-20s realistic -- recording each measured natural time; (c) pre-register an abort/defer gate: if the calibrated floor exceeds the largest sweep budget, DEFER the run as an infra/environment condition under AGENTS rule 3 with no natural-completion result written at all, and if the calibrated floor exceeds 1.15x the archived 1.14993s, proceed but stamp load_confounded: true into truncation_sweep_comparison.json itself; (d) record hw.ncpu and 1/5/15-minute load averages in environment.json at run start AND end, and require execution_report.yaml to print them adjacent to n_naturally_completed. Withdraw the unsupported 'robust to modest cross-run timing variation' assurance from the CROSS-HARDWARE caveat."
    - "[PF-15, advisory]: carry the four standing per-batch obligations explicitly -- BATCH-012's extremity/conjugate-pair check extended BY NAME to the naturally-completed subset; BATCH-010's caveat propagation naming truncation_sweep_comparison.json and execution_report.yaml as the artifacts that must carry the caveats in-band; BATCH-013's evidence-strength distinction as a required strength_note clause scaling the claimed tier to n_naturally_completed; BATCH-011's instrument-invariant discriminating-power precheck."
    - "[PF-16, advisory]: define n_timed_out (over attempted), n_still_truncated (over resolved) and n_unresolved_and_not_timed_out explicitly, and require the full identity be reported rather than only the resolved-side one."
    - "[advisory, no PF number]: state how resolved_non_fp_set is derived for value_histogram_and_conjugate_pairs (from per_vertex_records where resolved is True, or from graph), since run_truncation_probe_v9's output dict does not return it -- the same plumbing note PF-9 attached to the comparison functions in v10 round 2."
    - "PF-15 and PF-16 do not block freeze independently; PF-11 through PF-14 do, individually and collectively -- each is demonstrated against a committed artifact or the real frozen code, not hypothesized."
  counterexample_or_mutation: >-
    The cheapest discriminating control is free and already computed:
    tabulate RUN-SSIQ-a85692-h's 194 archived natural wall_seconds against
    their delta_e_upper_bound values. That tabulation IS the counterexample
    -- it puts the fastest delta_E >= 5 vertex at 1.392s, falsifying the
    premise that b=1.2s can observe delta_E >= 5 natural convergence, and
    is reproducible in ten lines of Python against a committed artifact.
    For the load confound, the cheapest control is PF-14(b): re-run the 8
    fastest vertices at the 15.0s reference budget on the actual execution
    machine and compare the measured floor against 1.14993s; if the
    measured floor is >= the largest sweep budget, the natural-completion
    cross-check is guaranteed empty for environmental reasons and that
    emptiness must not be written as a result (~10-20s realistic cost).
    Once budgets are fixed, the standing null-object control is that
    measured n_naturally_completed(b) must track the archived prediction
    curve (0 / 2 / 45 / 115 at b = 1.1 / 1.2 / 1.4 / 1.45, as upper
    bounds); a measured count far below the archived prediction is an
    execution-environment artifact, and a count that stays flat where the
    archived timings say it should climb steeply through 1.4-1.5s is the
    artifact tell this spec should pre-commit to reading as such.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale, single-prime search-procedure diagnostic work,
    H-SSIQ-36e970.asymptotic_claim null and heuristic_assumptions empty
    throughout, correctly inherited and unchanged. The operative baseline
    is the archived evidence this amendment must beat to be worth running:
    RUN-SSIQ-a85692-h already establishes, at n=194 with zero exceptions
    and zero timeouts, exactly the equality the new cross-check predicts.
    As drafted, the novel measurement is dominated by an existing artifact
    on every axis -- sample size (2 vs 194), value coverage ({2} vs all
    seven values), and selection bias (extreme fastest tail vs full
    population) -- so it has not cleared its own baseline. PF-11's budget
    fix is precisely what clears it: at b ~ 1.45 the cross-check tests
    equality in the MIXED truncated/naturally-completed regime, which
    RUN-SSIQ-a85692-h structurally cannot test.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty; asymptotic_claim null throughout; no numbered heuristic is implicated by this amendment."
    - "The one implicit modelling assumption this amendment newly introduces -- 'a vertex whose total natural completion time is below b will complete naturally at budget b' -- is not a heuristic in the exponent-first sense, but it is FALSE as stated, because two_sided_search caps the source-side expansion at b/2 independently of the total. It must be stated and corrected rather than left implicit."
  cost_model_challenges:
    - "194 * (1.1 + 1.2) = 446.2s is arithmetically correct, and 1000/446.2 = 2.24x as stated; total_cpu_hours 0.33 against wall_clock_seconds_per_run 1000 (1000/3600 = 0.278) matches this lineage's generous-rounding precedent."
    - "It is not the whole bound: the budget check sits at the TOP of build_smooth_table's heap loop, so a vertex can overshoot its slice by one pop's work (up to 9 modular-polynomial root-findings). Measured on v10's real run (RT-BATCH-013): b=0.6 -> 121.33s vs a 116.4s bound (+4.2%), b=0.8 -> 157.39s (+1.4%), b=1.0 -> 195.02s (+0.5%)."
    - "Under the measured ~1.5x oversubscription the truncated-vertex term is roughly load-invariant (a truncated vertex consumes ~b wall seconds and simply completes less work), but graph build, JSON I/O and the overshoot term inflate; realistic worst case ~470-500s. Under PF-11's recommended budgets plus PF-14's calibration the worst case rises to ~605-635s ([1.1,1.4] -> 485s; [1.2,1.45] -> 514.1s; plus ~120s calibration), still inside the existing 1000s / 0.33 CPU-hour budget with ~1.6x margin. NO budget increase is required to fix this amendment, though restoring v10's own 1200s cap would cost nothing."
    - "No total-expected-cost = per-attempt-cost x inverse-success-probability computation applies: bounded, single-run, non-probabilistic-success diagnostic, consistent with v8/v9/v10 framing."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list anywhere; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "OBJECTIVE_BOUNDARY correctly excludes H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label and lever L4, is scoped to p=2437 alone, and correctly declines to answer RT-BATCH-011's original truncation-boundary question per DEC-20260806-520ca4 D-3. No scope inflation found in the text as drafted."
    - "The scope risk is downstream: an n_naturally_completed = 0 outcome invites a future reader to convert an environmental null into a statement about delta_E convergence. Were this run's null later cited as evidence that convergence to delta_E >= 5 does not begin at the floor, that would be a closure claim resting on a measurement structurally incapable of observing the phenomenon -- a fatigue report about the instrument, not a statement about the object. PF-14's gate and PF-15's caveat propagation exist to prevent exactly that."
  proof_architecture_challenges:
    - "Not applicable -- H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged; a direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held, unchanged from v8/v9/v10 review history."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v11.yaml as
    committed at 6b6703ee2 (draft, pre_freeze_review.status PENDING, no
    implementation file yet written): the amendment's procedural
    architecture is sound and pre-applies every one of v10's ten fixes
    without needing a review round to rediscover them; the seed-isolation
    argument holds (BASE_SEED 20260811 unchanged, derive_per_vertex_seed
    pure in (base_seed, vertex), budget the sole manipulated variable);
    every cited function exists with the cited signature and timed_out is
    genuinely returned per-vertex in the shape v11 assumes;
    value_histogram_and_conjugate_pairs is genuinely pure and reusable; the
    budget arithmetic is correct; the scope boundary is clean; and the
    b=1.1s guaranteed-truncated control arm is robust to the machine-load
    confound. It is NOT safe to freeze: the b=1.2s "above the floor" arm is
    refuted by the archived data the amendment itself cites (2 of 194
    vertices below 1.2s, both delta_E=2; fastest delta_E>=5 vertex at
    1.392s -- PF-11); timed_out's real semantics impose an unmeasured b/2
    source-side cap that removes what little archival support that arm had,
    and qualify "true minimum" to the frozen (L, X=23, B=23) class
    (PF-12); the cross-check's falsifiable prediction is already confirmed
    at n=194 with zero exceptions in RUN-SSIQ-a85692-h and would be
    re-tested here at n<=2 (PF-13); and on a machine measured at 14 cores
    under 1/5/15-minute load averages 20.56/21.22/21.24, the expected
    outcome is a well-formed, silent, environment-manufactured
    n_naturally_completed = 0 with no gate, calibration, or recorded load
    to distinguish it from a finding (PF-14). All four fixes are cheap --
    three textual, one a ~120s-worst-case calibration -- and the corrected
    design fits the existing 1000s budget with ~1.6x margin. The underlying
    mechanism (partition by timed_out, test exact equality on the
    naturally-completed side) is a good idea that becomes genuinely
    informative, and genuinely new relative to RUN-SSIQ-a85692-h, at a
    budget in the 1.35-1.45s band.
  next_concrete_action: >-
    Coordinator: in one pass, (1) change SWEEP_BUDGETS to [1.1, 1.4] or
    [1.2, 1.45], justified against the archived per-value completion-time
    table rather than the floor minimum alone; (2) state the b/2
    source-side cap, requalify "true minimum" to the frozen (L, X=23,
    B=23) class, and replace the two-way mismatch dichotomy with a
    three-way branch reporting mismatch direction; (3) disclose
    RUN-SSIQ-a85692-h's existing 194/194 zero-exception exact-match result
    as the prior evidence state and state what the mixed-regime cross-check
    adds beyond it; (4) add the PF-14 load package (pre-registered
    n_naturally_completed predictions from archived timings; a
    coordinate-named 8-vertex 15.0s floor calibration before the sweep; a
    pre-registered defer / load_confounded gate; start-and-end load
    averages and hw.ncpu in environment.json) and withdraw the unsupported
    robustness sentence from the CROSS-HARDWARE caveat; (5) apply PF-15 and
    PF-16 in the same pass. Then request one short, focused round-2
    pre-freeze review scoped to (a) the new budget's predicted
    natural-completion counts being correctly transcribed from archived
    data and (b) the defer gate being stated as a hard precondition rather
    than a caveat -- before dispatching the ~500-635s of real compute.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no code executed from this
    lineage's implementation modules -- this review is a specification and
    real-code/real-artifact trace against a draft with no implementation
    file yet, not an execution. Non-durable, read-only computations run
    directly against the committed tree: (a) recomputed min/max/median
    wall_seconds over all 194 per_vertex_records in
    RUN-SSIQ-a85692-h/probe_delta_e_comparison.json (min 1.149932861328125,
    max 1.6985499858856201, median 1.4400434494018555), confirming the
    Coordinator's handed-over figures, and confirmed that run's
    per_vertex_budget_seconds = 15.0 with n_resolved = 194 and ZERO
    timed_out; (b) computed the count and delta_E histogram of records
    below each candidate budget (1.1 -> 0; 1.2 -> 2, both delta_E=2; 1.3 ->
    7; 1.4 -> 45; 1.45 -> 115; 1.5 -> 186; 1.7 -> 194) and the per-value
    min/median/max completion times (minimum over delta_E>=5 vertices =
    1.392s) -- the basis of PF-11; (c) read that run's
    comparison_against_archived (n_value_matches 203, n_value_differs 0;
    non_fp_rational_only 194/194) -- the basis of PF-13; (d) read
    RUN-SSIQ-a85692-b/raw-result.json's phase_minus1_real_search record for
    p=2437 (n_attempted 194, n_resolved 194, wall_seconds_used 284.88s
    against a 300s t_prime pool) and run_phase_minus1_on_confirmatory_set's
    per_vertex_cap logic, establishing that every archived vertex received a
    >= ~15s cap; (e) read compute_delta_e.two_sided_search and
    build_smooth_table line by line to establish the b/2 source-side cap and
    the heap-exhaustion stopping condition -- the basis of PF-12; (f) read
    run_truncation_probe_v9, parse_v8_new_delta_map, compare_against_archived,
    compare_against_v8 and value_histogram_and_conjugate_pairs directly to
    confirm existence, signatures and purity; (g) full-file greps of
    specification_v11.yaml for extremity/selection/BATCH-012/strength_note/
    propagat/derivation/conjugate -- the basis of PF-15; (h) measured
    sysctl -n hw.ncpu = 14 and successive uptime load averages
    20.56/21.22/21.24 -- the basis of PF-14; (i) git checks confirming
    6b6703ee2 is the spec's touching commit, an ancestor of HEAD, with a
    clean working tree. No file was written or edited by any of these
    computations other than this report itself.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task wrote
    only coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v10.yaml,
    specification_v11.yaml and every run package) and every ledger record
    are untouched.
  verdict: DO-NOT-FREEZE
```
