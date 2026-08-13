# RT-BATCH-013 — Red Team review of RUN-SSIQ-a85692-j (EXP-SSIQ-a85692 v10),
# GOAL-SSIQ-001 BATCH-013 (the 0.6s/0.8s/1.0s truncation sweep RT-BATCH-012
# itself named as the required follow-up)

**Reviews the Coordinator-committed snapshot at `e2102bfe` (parent `ca905c24`,
the frozen `specification_v10.yaml` after two pre-freeze review rounds),
covering `RUN-SSIQ-a85692-j`.** Per this task's operating rules, only this
Coordinator-committed snapshot is treated as durable input; the two
pre-freeze rounds' PF-1 through PF-10 findings and RT-BATCH-012's own
findings are not re-litigated. Every numeric claim below was independently
recomputed from the raw committed `truncation_sweep_comparison.json` and
`raw-result.json`, not taken from `execution_report.yaml`'s or the
Coordinator's own commit-message summaries — several local, non-durable,
read-only Python computations were run directly against the committed JSON
and against `compute_delta_e.py`, `delta_e_truncation_probe_v9.py`,
`delta_e_truncation_sweep_v10.py`, and `build_isogeny_graph.py` as committed
at `ca905c24`/`e2102bfe`. No run artifact, specification, or ledger record
was written or modified.

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

**The run executes exactly as `specification_v10.yaml` requires (PF-1
through PF-10 all independently re-verified, not merely trusted), and the
headline new finding — 62/62 differing (new, truncated) vs. (archived,
complete) triples all showing `new_value > archived_value`, never `<`, never
spuriously `==` — is not merely "mechanistically plausible": it is a
provable structural property of `two_sided_search`'s Dijkstra-correctness
plus the deterministic-per-vertex-RNG design, modulo exactly one empirically
testable premise (that a larger `time_budget_seconds` call on the same
hardware completes at least as many best-first heap-pops as a smaller one),
and I independently confirmed every observable consequence of that premise
holds with zero exceptions across all 194×3 vertex-budget cells in this
run's own raw data.** This is a genuine, well-supported positive finding.
The narrow objections below are about how it should be cited going
forward — the same posture RT-BATCH-012 took toward v9's null result — not
about whether the core directional claim is real.

1. **The comparison logic is genuinely symmetric; I traced it and also
   recomputed all 62 triples myself from the raw JSON, not the Coordinator's
   summary.** `compare_against_archived`/`compare_against_v8`
   (`delta_e_truncation_probe_v9.py:224-360`, GENUINELY IMPORTED UNCHANGED by
   v10) compute `if archived_delta_map[v] == new_delta_map[v]: matches else
   differs` — a single unconditional equality test, direction-blind, with no
   asymmetric branch, no off-by-one, no silent `>=`/`<=` substitution. I
   independently parsed `value_differs_vs_archived_triples` from
   `truncation_sweep_comparison.json` (not `execution_report.yaml`'s own
   count) at all three sweep points and got **62/62 with `new_value >
   archived_value`, 0 with `<`, 0 with `==`** — matching the Coordinator's
   claim exactly, computed independently.

2. **The mechanism is provable, not merely empirical, given one named,
   testable premise — and I tested it.** `build_smooth_table`
   (`compute_delta_e.py:144-174`) is a best-first (Dijkstra) expansion whose
   assigned degree for a vertex, upon first heap-pop, is the graph's TRUE
   minimal reachable degree regardless of exploration order — this follows
   from Dijkstra correctness on non-negative edge weights, and is
   independent of the RNG scheme, because `find_roots_with_multiplicity`
   (`build_isogeny_graph.py:340-427`) self-verifies (`if len(distinct_roots)
   != sdeg: raise`) and always returns the FULL, correct root multiset
   regardless of which random trial elements the internal splitter tried —
   this is exactly RT-BATCH-011's own determinism argument, and it is
   untouched by this run. Given a FIXED per-vertex RNG seed
   (`derive_per_vertex_seed(base_seed, vertex)`, a pure SHA-256-based
   function with no wall-clock dependency — confirmed by direct read,
   `delta_e_independent_rng_probe_v8.py:151-154`), and a FRESH
   `random.Random` per sweep-point call (confirmed:
   `delta_e_truncation_sweep_v10.py` calls
   `v9probe.run_truncation_probe_v9(g, BASE_SEED, b)` independently per
   sweep point, and `per_vertex_records`' own `seed_used` field is
   byte-identical across all three budgets for every vertex I sampled,
   e.g. vertex `[11, 381]`: `seed_used=17338134091428967313` at b=0.6, 0.8,
   AND 1.0), the sequence of heap push/pops up to any given point in the
   search is IDENTICAL regardless of the declared budget — budget only
   controls WHERE the loop halts. Therefore: table(b1) is a PREFIX (in
   finalization order) of table(b2) for b1<b2, WITH IDENTICAL degree values
   on the overlap, PROVIDED the one named premise holds (larger declared
   budget ⟹ at least as many completed iterations on that hardware). This
   premise is exactly the kind PF-3/PF-6 already flagged as not
   bit-for-bit-guaranteed across hardware/process boundaries — but I
   checked its consequences directly against this run's own raw data (not
   assumed): **the resolved vertex sets nest exactly, `s(0.6) ⊆ s(0.8) ⊆
   s(1.0)`, with zero exceptions in either direction** (|s(0.6)|=25,
   |s(0.8)|=106, |s(1.0)|=187, verified by direct set-subset computation
   against `per_vertex_records`), **and every vertex resolved at two or
   more budgets has a weakly monotonically NON-INCREASING
   `delta_e_upper_bound` as budget grows — 10 vertices changed value across
   budget pairs I checked, and ALL 10 decreased (never increased)**: e.g.
   `(2154,970)`: 4→2 (b=0.6→0.8); `(370,85)`: 9→6 (b=0.8→1.0). Given
   `common(b) = table_s(b) ∩ table_t(b)` is monotonically non-decreasing in
   `b` (as a set) with stable degree values on the overlap, `min` over a
   growing set is trivially non-increasing — this is the textbook mechanism,
   and it holds exactly, not approximately, in this run's own raw data.

3. **One further confirmation beyond what any artifact in this run states
   explicitly**: at `b=1.0`, I checked not merely that the resolved-value
   histogram's `δ=2` count (34) and `δ=3` count (70) numerically match the
   true archived population counts (34/194, 70/194) — `execution_report
   .yaml`'s own `OBS-2` correctly declines to treat that as more than a
   coincidental count match — but whether the underlying VERTEX SETS are
   IDENTICAL. They are: **the 34 vertices this run resolved to `δ=2` at
   b=1.0 are exactly the 34 vertices whose archived value is 2 (set
   equality, zero symmetric difference), and likewise for all 70 `δ=3`
   vertices.** By contrast, of the 35 vertices whose TRUE (archived) value
   is `δ=5`, only 1 resolved correctly to 5 at b=1.0 (the other 34 resolved
   to some larger, non-minimal value); of the 16 true-`δ=7` vertices, ZERO
   resolved to 7 (all 16 resolved to something larger). This is a much
   sharper, vertex-level confirmation of "shallow values converge early
   under truncation, deep values do not" than the aggregate histogram-shape
   argument alone supports, and it was not computed or stated anywhere in
   this run's own artifacts.

Given (1)-(3), my verdict is **CHALLENGE (narrow)**: no objection to
execution fidelity, PF-2/PF-10 failure-isolation implementation, budget
honesty, or `OBJECTIVE_BOUNDARY` compliance, and no objection to the core
directional mechanism, which I judge PROVEN (modulo the named, tested
premise) rather than merely plausible. The objections below are about
over-reading the raw counts/proportions as more informative than they are,
about applying this amendment's own PF-7 statistical-power discipline (which
the frozen spec already required for histogram-shift citations) to the NEW
"differs" counts too, and about precisely bounding what this finding does
and does not say about RT-BATCH-011's original PF-6 question.

---

## Front 1 — Adversarial Question 1: comparison-logic symmetry, verified not
## trusted

`compare_against_archived(new_delta_map, archived_delta_map,
non_fp_rational_set)` (`delta_e_truncation_probe_v9.py:224-267`, imported
unchanged by v10, never modified): for every vertex `v` in
`new_delta_map`'s keys, `if v not in archived_delta_map: skip (counted as
n_not_in_archived)`, `elif archived_delta_map[v] == new_delta_map[v]:
matches`, `else: differs` (recording `{"vertex": ..., "archived_value":
archived_delta_map[v], "new_value": new_delta_map[v]}` — direction-neutral
field names, no signed-difference computation anywhere). `compare_against_v8`
is byte-identical in structure against `v8_delta_map`. Neither function
contains a directional comparator (`<`, `>`, `>=`, `<=`) anywhere — the ONLY
branch is equality vs. inequality. I independently re-parsed
`value_differs_vs_archived_triples` at all three sweep points from the
committed `truncation_sweep_comparison.json` (not `execution_report.yaml`'s
own aggregate `n_value_differs` fields) and recomputed
`new_value > archived_value` / `<` / `==` counts myself: **62 `>`, 0 `<`, 0
`==`**, exactly matching the Coordinator's claim of "100% strictly
greater." Domain check: `non_fp_rational_only`'s own `n_value_differs`
sub-field is identical to the full-domain figure at every sweep point (4/4,
8/8, 50/50) — confirming all 62 differing triples are among the 194
non-F_p-rational vertices, never one of the trivially-matching 9
F_p-rational vertices, consistent with the wiring design. **No comparison-
logic artifact found; the pattern is a genuine property of the underlying
values, not a bug in how they are compared.**

## Front 2 — Adversarial Question 2: is "always ≥" provable or merely
## empirical?

**Provable, given one named premise, and the premise's testable
consequences hold with zero exceptions in this run's own data — see Bottom
line points 2-3 above for the full argument and the direct verification.**
To restate the boundary precisely, since the task asks for it explicitly:
the CODE-LEVEL guarantee (Dijkstra correctness: a vertex's first-finalized
degree is always the true minimal reachable degree, independent of RNG
order, because `find_roots_with_multiplicity` self-verifies and always
returns the complete, correct root set) is unconditional — this part is a
mathematical fact about the algorithm, not an assumption. The REMAINING
premise the "always ≥" pattern needs is purely about WALL-CLOCK MECHANICS,
not the math: that a larger declared `time_budget_seconds`, run as a
separate process call on the same machine, permits at least as many loop
iterations as a smaller one would have gotten. This is NOT something the
code enforces or could enforce (each sweep point is a fresh
`two_sided_search` call, at a different real time, subject to whatever
scheduling/thermal/GC jitter is present at that moment) — it is a physical
assumption about the test environment, the same category of assumption
PF-3/PF-6 already named for cross-run/cross-hardware comparisons here within
a single run, same hardware, same script, sequential execution. I checked
its predicted consequences directly (not merely assumed them): (a) exact
subset-nesting of the three resolved sets (25⊆106⊆187, zero exceptions);
(b) weakly-monotone-non-increasing values on every vertex resolved at
multiple budgets (10/10 changes strictly decrease, zero counter-examples).
**Given the code-level correctness argument plus this run's own
zero-exception empirical confirmation of the wall-clock premise, "a
truncated search's collision degree is never smaller than a longer or
complete search's" is as close to a proven property as this campaign's
toy-scale instrument gets — a genuinely different epistemic status than
"held across 62 samples," which is the framing this task's own question 4
offered as the weaker alternative.** No code path exists (and none was
found on direct read of `two_sided_search`/`build_smooth_table`) by which a
truncated search could discover a SMALLER collision than a longer run with
the identical seed — the heap-pop sequence up to truncation is a strict
prefix, never a reordering, of the longer run's sequence.

## Front 3 — Adversarial Question 3: sample size, proportion trend, and the
## subset-nesting check

**Subset nesting: verified directly, holds exactly** (Front 2 above) —
`s(0.6) ⊆ s(0.8) ⊆ s(1.0)` with 0 exceptions, so the three sweep points are
NOT independent samples in the usual sense; each larger budget's resolved
set is a strict superset of the smaller one's.

**Differs proportion (4/25=16.0%, 8/106=7.5%, 50/187=26.7%): I computed
this myself and it is genuinely informative, but not in the simple
monotonic-trend sense the raw numbers might suggest at a glance — it is
explained by a COMPOSITION effect, not a change in per-vertex risk.** The
dip at b=0.8 (7.5%, lower than both neighbors) is real and needs
explanation, not just noting. I traced it: at b=0.6, the tiny 25-vertex
resolved set is composed almost entirely of the two shallowest achievable
values (`δ=2`: 19, `δ=4`: 6) — the 4 that differ are presumably among the
harder `δ=4` cases. At b=0.8, the resolved set balloons to 106 and pulls in
a large, genuinely-converged block of `δ=3` vertices (49 of them, the
modal true value, found correctly at this budget) alongside the already-
converged `δ=2` block (34, exactly matching the true `δ=2` population count
even at this budget) — diluting the differs proportion even though the
raw differs count doubled. At b=1.0, resolution reaches into materially
DEEPER true values (`δ=5,6,7,8,9,10,12,16`) for the first time in volume,
and I directly confirmed (Bottom line point 3) that these deep, newly-
resolved vertices are disproportionately NOT yet converged (0/16 true-`δ=7`
vertices resolve correctly; 1/35 true-`δ=5` vertices do) — so the jump to
26.7% reflects WHICH new vertices entered the resolved set, not a rising
per-vertex probability of divergence at a fixed depth. **This is a
mechanistically coherent, favorable reading (it predicts convergence
continues as budget grows further, consistent with v8's own 15.0s/0/194
result), but it means the proportion trend by itself, cited without this
composition breakdown, could be read the wrong way (as "truncation gets
worse with more budget," when the more accurate statement is "more budget
resolves harder vertices, which — being harder — have not yet converged, a
different and much weaker claim").**

**Effective independent sample size for the DIFFERS counts specifically has
not yet been computed anywhere in this run's own artifacts, and the frozen
contract's own PF-7 discipline (required for any future histogram-shift
citation) should extend to it.** I checked whether the 62 raw differing
triples are themselves conjugate-paired, the same correction RT-BATCH-012
applied to v9's resolved set: **b=0.6: 4 raw → 1 pair + 2 singles = 3
effective units; b=0.8: 8 raw → 3 pairs + 2 singles = 5 effective units;
b=1.0: 50 raw → 24 pairs + 2 singles = 26 effective units.** Summed, 62 raw
differing triples correspond to roughly **34 effective independent
instances**, not 62 — a real, non-trivial correction (45% reduction) in
the same direction and magnitude RT-BATCH-012 found for the resolved-set
counts generally. This does not weaken the DIRECTIONAL finding (which is a
sign, not a magnitude, claim, and every single one of the 62/34 units point
the same way) but it does matter for any future claim about HOW OFTEN
truncation produces a wrong value at a given budget.

## Front 4 — Adversarial Question 4/6: relationship to RT-BATCH-011's PF-6
## boundary question

**Precise answer: this is a new, standalone finding about truncation's
effect on this search instrument, and it is ORTHOGONAL to RT-BATCH-011's
own shared-RNG-vs-independent-RNG determinism argument — it neither
narrows, extends, nor reopens that argument.** RT-BATCH-011's conclusion
(`RT-BATCH-011.md`, Bottom line points 1-2, confirmed by direct code read
here of the same `find_roots_with_multiplicity` correctness-checking logic)
was that `two_sided_search`'s output is PROVABLY RNG-invariant WHENEVER THE
SEARCH COMPLETES WITHOUT TRUNCATION — a determinism argument whose premise
is completeness, not any property of which RNG scheme (shared,
sequentially-advanced vs. independent, per-vertex-derived) drove the search.
That premise (non-truncation) is untouched by this run: `RUN-SSIQ-a85692-b`
(archived, shared-RNG) and `RUN-SSIQ-a85692-h` (v8, independent-RNG, 15.0s
budget, confirmed non-truncated by RT-BATCH-011's own per-vertex trace,
1.15-1.70s max) both complete fully, and RT-BATCH-011's own determinism
argument continues to guarantee they agree — v10's own internal-consistency
check (`execution_report.yaml`) independently confirms this again
(`comparison_1` and `comparison_2` `n_value_differs` are identical at every
sweep point, since archived and v8's own map are themselves value-identical
full searches). **What v10 adds is a DIFFERENT axis entirely: not "does the
RNG-sharing scheme matter," but "does TRUNCATION matter, regardless of RNG
scheme."** The answer, now demonstrated for the first time with a real,
mechanism-traced, non-degenerate signal (unlike v9's 0/8 null), is yes —
truncation systematically biases the result upward (toward larger, non-
minimal delta_E), by a mechanism (best-first search finds a subset of the
true collision-candidate set) that has nothing to do with which RNG
scheme produced the seed. **This is directly useful for designing any
FUTURE truncation-based probe of RT-BATCH-011's original boundary question**
(any such probe now has independent confirmation that truncation itself is
a real, directional confound that must be controlled for or reasoned about
explicitly — a genuinely new design constraint this campaign did not have
before this run), **but it does not itself answer, narrow, or reopen that
boundary question**, exactly as `OBJECTIVE_BOUNDARY` states, since even
`b=1.0` remains below the 1.14993s natural-completion floor and every
vertex in this run remains genuinely truncated.

## Front 5 — Adversarial Question 5: does the histogram breadth predict full
## convergence at larger budgets?

**Yes, consistently, and this run's own granular data (Front 3/Bottom line
point 3) supports rather than complicates that picture.** The vertex-level
identity match at `δ=2`/`δ=3` (34/34, 70/70, exact set equality) shows the
shallow-value population has ALREADY fully converged by b=1.0, well below
the natural-completion floor — meaning convergence is not a knife-edge
phenomenon that only appears at/above 1.14993s, it accrues gradually,
value-by-value, as budget grows, exactly as the best-first search order
predicts (shallow collisions are locked in earliest). The deep-value
population (`δ≥5`) is NOT yet converged at b=1.0 (0-3% correct at the
values I checked) — but this is the expected, not a surprising or
complicating, state of affairs given those vertices' collisions require
searching much further into both tables before the TRUE minimum is even
discoverable, let alone found within a still-truncated budget. v8's own
15.0s/0-differences result (30x the deepest sweep point here) is the
existing evidence that full convergence is in fact reached once budget
clears the natural floor by a wide margin; this run adds the missing
INTERMEDIATE data point showing convergence is monotesic and value-ordered,
not a discontinuous jump. **The single cheapest concrete follow-up this
predicts and that would directly test it: one more sweep point at, say,
1.1-1.2s (still near, but for some vertices now AT OR ABOVE, the 1.14993s
floor) should show `δ≥5`-value convergence beginning while `δ=2`/`δ=3`
remain exactly converged — a falsifiable, cheap next check.**

## Front 6 — Adversarial Question 8: PF-2/PF-10 implementation, verified by
## direct code read

**Both correctly implemented, confirmed by direct read of
`delta_e_truncation_sweep_v10.py` (committed at `e2102bfe`), not merely
trusted from the execution report.** Step (0) (`build_graph_for_prime` +
`verify_graph_identity`, lines 278-298) runs OUTSIDE and BEFORE any
try/except, exactly as PF-1/PF-10 require — no surrounding exception
handler anywhere between the function's start and the `for b in
SWEEP_BUDGETS:` loop. Each sweep point (lines 314-411) opens its own `try:`
at line 318, covering PART A (`run_truncation_probe_v9`), both required
comparisons, and the histogram/conjugate-pair reporting, with a bare
`except Exception as e:` (line 401) that records `sweep_point_error` and
does NOT re-raise, and `sweep_point_results.append(entry)` (line 411) runs
unconditionally after either branch — genuine incremental accumulation,
matching PF-2's fix exactly. This run's own data shows all three
`try`/`except` blocks took the success path (`sweep_point_error: null`
throughout) — the failure path is disclosed-but-unexercised on a real
failure this run, exactly as `execution_report.yaml`'s own
`executor_assessment` states, and PF-8's empty-histogram case (`n_resolved
== 0`) was similarly never exercised (`n_resolved` was 25, 106, 187, all
nonzero) — both correctly disclosed as untested code paths rather than
silently assumed correct.

## Front 7 — OBJECTIVE_BOUNDARY and scope (Adversarial Question 9)

**Clean, verified by direct field read of the committed artifacts, not
spec prose.** `grep`-checked `raw-result.json`,
`truncation_sweep_comparison.json`, and `execution_report.yaml` for
`PERSISTS`, `WEAKENS`, `H-SSIQ-36e970`, and `lever L4`/`L4`: every match is
inside an explicit disclaimer sentence (`objective_boundary` /
`objective_boundary_note` stating this does NOT test H-SSIQ-36e970's
real-arm prediction and does NOT produce a PERSISTS/WEAKENS label) — no
affirmative claim, label, or scope statement anywhere. `scale_qualifier`
correctly states "toy; N (graph size) = 203; single prime p=2437" in both
`raw-result.json` and (implicitly, via the same toy/p=2437-only framing) the
sweep artifact. `certificate.kind: none` with an explicit
docs/claims-and-verification.md-citing reason (pure measurement, no solve
claim) is present and correct. No affected/safe scheme list anywhere; no
scope inflation found.

---

## Objections

- **OBJ-1**: None on execution fidelity, PF-1 through PF-10 implementation,
  budget honesty, or `OBJECTIVE_BOUNDARY` compliance — all independently
  re-verified by direct code and artifact read (Fronts 1, 6, 7). Wall-clock
  474.15s of 1200s (39.5%), matching `raw-result.json` to full float
  precision; graph-identity re-verification passed 203/203 once, before the
  sweep loop, unwrapped, exactly as PF-1/PF-10 require.
- **OBJ-2 (comparison logic, verified not trusted)**: `compare_against_
  archived`/`compare_against_v8` are genuinely direction-blind equality
  tests (no `<`/`>`/`>=`/`<=` branch anywhere in either function); I
  independently re-parsed and recomputed all 62 differing triples from raw
  JSON and confirmed 62/62 `new_value > archived_value`, 0 `<`, 0 `==`,
  matching the Coordinator's claim exactly, computed independently rather
  than trusted.
- **OBJ-3 (mechanism: provable, and independently stress-tested)**: the
  "always ≥" pattern follows from Dijkstra correctness (a vertex's assigned
  degree, once finalized, is the true minimal degree regardless of RNG
  exploration order — `find_roots_with_multiplicity`'s self-verification
  guarantees this) plus one named, testable wall-clock-monotonicity premise.
  I checked the premise's predicted consequences directly against this
  run's own raw `per_vertex_records`: the three resolved sets nest exactly
  (`s(0.6) ⊆ s(0.8) ⊆ s(1.0)`, 0 exceptions, sizes 25/106/187), and every
  vertex resolved at 2+ budgets (10 found with a changed value) has a
  weakly monotonically non-increasing `delta_e_upper_bound` as budget
  grows (10/10 decreases, 0 increases). This is a substantially stronger
  epistemic basis than "held across 62 samples" — it is a structural
  property with zero counter-examples in every directly-checkable
  consequence this run's data affords.
- **OBJ-4 (proportion trend needs its composition explanation stated, not
  just the raw numbers)**: the differs/resolved proportion (16.0% → 7.5% →
  26.7%) is non-monotonic and, cited bare, invites a misreading ("truncation
  gets worse with more budget"). I traced the actual driver: newly-resolved
  vertices at larger budgets are disproportionately DEEPER (larger true
  `δ`), and deep vertices are disproportionately NOT yet converged at any
  budget below the natural floor (0/16 true-`δ=7` vertices, 1/35 true-`δ=5`
  vertices resolve correctly at b=1.0, vs. exact 34/34 and 70/70 identity
  matches at `δ=2`/`δ=3`) — a composition effect, not a rising per-vertex
  divergence risk. Any future citation of the proportion trend should state
  this explicitly rather than the bare percentages.
- **OBJ-5 (PF-7's own statistical-power discipline should extend to the
  differs counts, not only the resolved counts)**: the frozen contract's
  PF-7 fix requires conjugate-pair-corrected effective sample size
  alongside any future histogram-shift citation. The 62 raw differing
  triples are themselves substantially conjugate-paired (I computed: b=0.6
  → 3 effective units of 4 raw; b=0.8 → 5 of 8; b=1.0 → 26 of 50; ≈34
  effective units total, not 62) — a ~45% reduction in effective
  independent evidence for the DIRECTIONAL claim's magnitude (not its
  sign — every unit, paired or not, points the same direction), not
  computed or reported anywhere in this run's own artifacts. Should be
  applied before any future citation states a bare "62 differences" count.
- **OBJ-6 (scope precision on RT-BATCH-011/PF-6)**: this run's finding is
  orthogonal to, not a narrowing or reopening of, RT-BATCH-011's own
  shared-RNG-vs-independent-RNG determinism conclusion, which depends on
  completeness (non-truncation), not RNG scheme, and remains fully intact
  and unaffected here (archived and v8's own map continue to agree exactly,
  reconfirmed by this run's own Comparison 1/Comparison 2 identical-count
  internal check). It IS a new, standalone, useful finding about truncation
  itself (any future amendment attempting to properly test RT-BATCH-011's
  original boundary question must now account for this confound). Any
  future citation should state this distinction explicitly rather than
  imply this run bears on the RNG-sharing question.

## Required controls

- **Apply the frozen contract's own PF-7 conjugate-pair-correction
  discipline to the "differs" counts, not only the resolved counts**,
  before any `EV-*`/`DEC-*` citation states a bare "62 differences" or a
  bare proportion — report ≈34 effective independent units alongside the
  raw 62, and report the composition explanation for the non-monotonic
  proportion trend (OBJ-4/OBJ-5) rather than the bare percentages alone.
- **A follow-up sweep point at 1.1-1.2s** (straddling, and for some
  vertices now at or above, the observed 1.14993s natural-completion floor)
  to directly test Front 5's falsifiable prediction: `δ≥5`-value
  convergence should begin appearing while `δ=2`/`δ=3` remain exactly
  converged (identity match, not merely count match) — the cheapest next
  check of whether convergence is genuinely monotone-in-budget or has some
  other structure this sweep's 3 points cannot yet distinguish.
- **State explicitly, in any future citation, that this finding is
  orthogonal to RT-BATCH-011's own RNG-sharing determinism conclusion**
  (OBJ-6) — a truncation-vs-completeness finding, not an RNG-scheme
  finding, useful for future truncation-probe design but not itself
  progress on RT-BATCH-011's original boundary question.

## Counterexample or mutation

The cheapest concrete check that would have separated "the 100% directional
pattern is a genuine structural property" from "it happened to hold across
62 samples by chance": re-derive the SAME 62 triples' expected sign
independently from the algorithm's own stated correctness properties
(Dijkstra invariant + subset-table argument) BEFORE looking at the data,
then check the data against that independent prediction — which is exactly
what Front 2/OBJ-3 above did (predicted `common(b1) ⊆ common(b2)` with
stable overlap degrees, hence `best_deg(b1) ≥ best_deg(b2)`, then verified
directly against `per_vertex_records`). The prediction held with zero
exceptions on every one of the 10 checkable value changes and on the full
subset-nesting of all three resolved sets — this is the strongest form of
"held up under an adversarial, independently-derived prediction" available
at this scale, short of formally re-deriving Dijkstra correctness from
first principles (which is standard and was not separately re-proven here).
If a FUTURE sweep point at a different, larger prime or with a
non-deterministic RNG-per-call (rather than a fixed derived seed) ever
produced a vertex whose truncated value was SMALLER than a longer-budget or
complete search's value at the identical vertex, that would falsify this
mechanism and require immediate re-examination of the RNG/seed-derivation
wiring — the single cheapest discriminating control for any future reuse of
this instrument.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale, single-prime search-procedure diagnostic work,
`H-SSIQ-36e970.asymptotic_claim: null` throughout, correctly inherited and
unchanged by this run. The relevant baseline remains this campaign's own
instrument-scrutiny discipline (RT-BATCH-009 through RT-BATCH-012's "trace
it, don't trust it, bring your own control"), extended here to a genuinely
new posture: RT-BATCH-012 audited an UNDERPOWERED NULL result and found it
uninformative; this review audits a WELL-POWERED POSITIVE result and finds
it holds up under an independently-derived structural prediction, not
merely a fit to the observed data — a meaningfully different (and stronger)
form of scrutiny than either RT-BATCH-011's near-certain-null case or
RT-BATCH-012's underpowered-null case required.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty — unchanged
by this run, a search-procedure diagnostic rather than a heuristic-
conditional asymptotic claim. The one heuristic-shaped assumption worth
naming (not one of `H-SSIQ-36e970`'s own numbered items, matching
RT-BATCH-012's own convention of flagging design-level assumptions this
lineage relies on): this run's own interpretive scaffold implicitly treats
"a larger declared time_budget_seconds always permits at least as many
completed loop iterations on the same hardware" as safe to assume without
restating it as a numbered premise every time. It is currently a SAFE
assumption — I checked its consequences directly and they hold with zero
exceptions — but it is a physical/wall-clock premise, not a mathematical
one, and should be named explicitly (as PF-3/PF-6 already do for the
weaker cross-run/cross-hardware version) if this instrument is reused at a
larger scale or on more heavily loaded hardware where the margin between
sweep-point budgets could be smaller relative to scheduling jitter.

## Cost model challenges

No asymptotic-cost claim anywhere in this run. Measured wall-clock
474.14778780937195s against the 1200s/0.4 CPU-hour budget cap (39.5%
utilization), matching `raw-result.json`'s figure to full float precision
against `execution_report.yaml`'s own `OBS-4` breakdown
(b=0.6→121.33s, b=0.8→157.39s, b=1.0→195.02s, summing to 473.74s plus graph
setup ≈474.15s total). Each sweep point's wall time modestly exceeds its
own naive `194*b` bound (116.4/155.2/194.0s) by the same disclosed soft-cap
mechanism this lineage has already reported (the timeout check fires only
between heap-pop iterations, never mid-call) — correctly and
un-defensively reported, comfortably within the 1200s hard cap and the
spec's own ~2.58x worst-case margin. No objection.

## Reduction and scope challenges

No affected/safe cryptographic scheme list anywhere in this amendment;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated, not
exceeded. `raw-result.json`'s and `truncation_sweep_comparison.json`'s
`objective_boundary`/`objective_boundary_note` fields correctly restrict
this run to a purely descriptive measurement at p=2437 alone, explicitly
excluding `H-SSIQ-36e970`'s real-arm prediction, lever L4, and any
PERSISTS/WEAKENS vocabulary — verified by direct grep across all three
committed JSON/YAML artifacts, not trusted from spec prose. No scope
inflation found in this run's own artifacts. This review's own corrections
(OBJ-4, OBJ-5, OBJ-6) are evidentiary-framing/statistical-power corrections
for future citation, not scope-inflation defects in what this run itself
currently claims — it claims nothing beyond measurement, correctly.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; a direct instrument-
level search-procedure diagnostic, not a proof-oriented proposal. Attacked
and held.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-j` as committed at `e2102bfe` (parent `ca905c24`),
against `specification_v10.yaml`: the run executes exactly as the frozen
spec requires (step (0) graph rebuild/identity-verification unwrapped,
passing 203/203, before any sweep point; each of the three sweep points
independently try/except-wrapped per PF-2, all three succeeded with
`sweep_point_error: null`; PF-8's empty-histogram case correctly never
exercised, since `n_resolved` was nonzero at every budget). **What this run
licenses, narrowly**: at p=2437, for the specific 194-vertex non-F_p-
rational population under this instrument's fixed per-vertex RNG-seed
derivation, a per-vertex search budget strictly below the observed
1.14993s natural-completion floor produces a `delta_e_upper_bound` that is
NEVER SMALLER than, and is frequently strictly larger than, the value the
same seed's complete (non-truncated) search finds at the identical vertex —
a directional, structurally-grounded bias (proven modulo one wall-clock
premise, independently stress-tested with zero exceptions against this
run's own raw per-vertex data), growing in raw count (4→8→50) and in
composition-adjusted incidence as budget grows toward the floor, because
larger budgets progressively resolve DEEPER (not merely more) vertices,
which are the ones least likely to have converged yet. The `δ=2`/`δ=3`
subpopulations are shown, by direct vertex-set-identity check (not
count-coincidence), to have fully converged to their true values by b=1.0.
**What this run does NOT license**: any claim that this bears on
RT-BATCH-011's own shared-RNG-vs-independent-RNG determinism question
(OBJ-6, orthogonal — that conclusion is untouched and remains valid,
resting entirely on non-truncation, which this run never provides at any
sweep point); any claim about H-SSIQ-36e970's real-arm prediction, lever
L4, or a PERSISTS/WEAKENS label (none present, correctly); and any bare
citation of "62 differences" or the raw proportion trend without the
conjugate-pair correction (≈34 effective units) and composition
explanation this review supplies (OBJ-4/OBJ-5).

## Next concrete action

Coordinator, before drafting any `EV-SSIQ-*`/`DEC-*` record citing this
run: (1) accept `RUN-SSIQ-a85692-j`'s execution fidelity, PF-1 through
PF-10 implementation, cost/budget honesty, and `OBJECTIVE_BOUNDARY`
compliance as clean — independently re-verified here by direct code and
artifact read, not merely trusted; (2) treat the core directional finding
(truncated search never underestimates, frequently overestimates,
`delta_e_upper_bound` relative to the complete-search value at the same
vertex) as PROVEN at this toy scale, modulo the named wall-clock
monotonicity premise, whose testable consequences hold with zero
exceptions in this run's own raw data (exact subset-nesting of resolved
sets; monotone-non-increasing values on every multiply-resolved vertex) —
a materially stronger status than "held across 62 samples"; (3) any
citation of the "62 differences" or the differs-proportion trend must
include the conjugate-pair-corrected effective sample size (≈34, not 62)
and the composition explanation for the non-monotonic 16.0%/7.5%/26.7%
trend (OBJ-4/OBJ-5), not the bare numbers alone; (4) state explicitly that
this finding is orthogonal to, not a narrowing or extension of,
RT-BATCH-011's own RNG-sharing determinism conclusion (OBJ-6) — it is a
new, standalone finding about truncation itself, useful for any future
attempt to properly probe RT-BATCH-011's boundary question but not itself
that probe; (5) the single cheapest concrete follow-up this run's own data
predicts and that would extend the finding is one more sweep point at
1.1-1.2s, straddling the observed 1.14993s floor, to test whether `δ≥5`
convergence begins there while `δ=2`/`δ=3` remain exactly converged
(Front 5); (6) this remains, exactly as `OBJECTIVE_BOUNDARY` states, a
single-prime descriptive diagnostic — no extension to `H-SSIQ-36e970`,
lever L4, PERSISTS/WEAKENS vocabulary, or any other prime is licensed by
this run.

## Overall verdict

**CHALLENGE (narrow).** Execution fidelity, PF-1 through PF-10
implementation, cost/budget honesty, and `OBJECTIVE_BOUNDARY` compliance
are all clean — no protocol deviation found. The headline directional
finding (truncated search values are never smaller than, and frequently
larger than, complete-search values at the same vertex) is not merely a
plausible pattern that happened to hold across 62 samples: it is a provable
structural consequence of Dijkstra correctness plus deterministic per-
vertex RNG, modulo one named wall-clock premise whose predicted
consequences I independently verified against this run's own raw data with
zero exceptions (exact subset-nesting of all three resolved sets; strictly
monotone-non-increasing values on every multiply-resolved vertex; exact
vertex-identity convergence of the `δ=2`/`δ=3` subpopulations by b=1.0).
What this review adds, ahead of any future `EV-*`/`DEC-*` citation: (a) the
proportion trend (16.0%→7.5%→26.7%) needs its composition explanation
stated, not the bare percentages, since newly-resolved deeper vertices are
disproportionately unconverged; (b) the frozen contract's own PF-7
conjugate-pair-correction discipline should extend to the "differs" counts
(≈34 effective units, not 62); (c) this finding is orthogonal to, not
progress on, RT-BATCH-011's own RNG-sharing determinism question, and any
future citation should say so explicitly. The correct status this run
supports is a genuine, mechanistically-proven, toy-scale finding about
truncation's directional bias on this specific search instrument — cite it
precisely, with the corrections above, not as a bare "62/62 differences, all
larger" headline.

```yaml
red_team_report:
  id: RT-BATCH-013
  task_id: TASK-20260806-d4379a
  claim_under_review: >-
    Coordinator-committed snapshot e2102bfe (parent ca905c24, the frozen
    specification_v10.yaml after two pre-freeze review rounds), covering
    RUN-SSIQ-a85692-j: a three-point per-vertex-budget sweep (0.6s/0.8s/1.0s,
    all strictly below the observed 1.14993s natural-completion floor) of
    the delta_E search at p=2437, testing RT-BATCH-012's own falsifiable
    prediction about whether the resolved-value distribution shifts toward
    the true population mix as budget grows. Reports coverage growing
    12.9%->54.6%->96.4%, unpaired-conjugate fraction falling 12.0%->3.8%->
    0.5%, and -- the batch's most significant unanticipated result --
    n_value_differs_vs_archived nonzero and growing (4, 8, 50 at
    0.6s/0.8s/1.0s), with the Coordinator's own precommit check finding all
    62 differing triples across the sweep have new_value strictly greater
    than archived_value, characterized as consistent with a mechanistic
    explanation (truncated search returns a valid but non-minimal upper
    bound, never smaller than a full-budget search's value).
  objections:
    - "OBJ-1: None on execution fidelity, PF-1 through PF-10 implementation, budget honesty, or OBJECTIVE_BOUNDARY compliance -- independently re-verified by direct code and artifact read. Wall-clock 474.14778780937195s of 1200s (39.5%), matching raw-result.json to full float precision; graph-identity re-verification passed 203/203 once, before the sweep loop, unwrapped, exactly as PF-1/PF-10 require."
    - "OBJ-2 (comparison logic, verified not trusted): compare_against_archived/compare_against_v8 (delta_e_truncation_probe_v9.py:224-360, genuinely imported unchanged) are direction-blind equality tests -- no <, >, >=, or <= branch appears anywhere in either function. I independently re-parsed value_differs_vs_archived_triples from the raw truncation_sweep_comparison.json (not execution_report.yaml's own counts) at all three sweep points and recomputed the sign myself: 62/62 new_value > archived_value, 0 with <, 0 with ==, matching the Coordinator's claim exactly, computed independently."
    - "OBJ-3 (mechanism: provable, and independently stress-tested against raw data, not merely observed): the always-greater-or-equal pattern follows from Dijkstra correctness (a vertex's finalized degree is the true minimal reachable degree regardless of RNG exploration order, since find_roots_with_multiplicity self-verifies and always returns the complete, correct root multiset -- build_isogeny_graph.py:340-427) plus one named, testable wall-clock-monotonicity premise (a larger declared time_budget_seconds permits at least as many completed loop iterations on the same hardware). I checked this premise's predicted consequences directly against this run's own raw per_vertex_records: the three resolved sets nest exactly (s(0.6) subset-of s(0.8) subset-of s(1.0), 0 exceptions, sizes 25/106/187), and every vertex resolved at 2+ budgets with a changed value (10 found) has a weakly monotonically non-increasing delta_e_upper_bound as budget grows (10/10 decreases, 0 increases; e.g. (2154,970): 4->2 at b=0.6->0.8, (370,85): 9->6 at b=0.8->1.0). A substantially stronger epistemic basis than 'held across 62 samples' -- a structural property with zero counter-examples in every directly-checkable consequence this run's own data affords."
    - "OBJ-4 (proportion trend needs its composition explanation stated, not just the raw numbers): the differs/resolved proportion (4/25=16.0%, 8/106=7.5%, 50/187=26.7%) is non-monotonic and, cited bare, invites a misreading. I traced the driver directly: newly-resolved vertices at larger budgets are disproportionately DEEPER (larger true delta), and deep vertices are disproportionately not yet converged at any budget below the natural floor -- I verified by direct vertex-set-identity check (not count coincidence) that at b=1.0 the 34 delta=2-resolved vertices and 70 delta=3-resolved vertices are EXACTLY the true archived population's own delta=2/delta=3 vertex sets (zero symmetric difference), while only 1/35 true-delta=5 vertices and 0/16 true-delta=7 vertices resolve to their correct value at b=1.0 (all others resolve to a larger, non-minimal value). This is a composition effect, not a rising per-vertex divergence risk; any future citation of the proportion trend should state this explicitly rather than the bare percentages."
    - "OBJ-5 (PF-7's own statistical-power discipline should extend to the differs counts, not only the resolved counts): the frozen contract's PF-7 fix requires conjugate-pair-corrected effective sample size alongside any future histogram-shift citation, applied so far only to resolved-vertex counts. I computed the same correction for the 62 raw differing triples: b=0.6 -> 3 effective units of 4 raw (1 pair + 2 singles); b=0.8 -> 5 of 8 (3 pairs + 2 singles); b=1.0 -> 26 of 50 (24 pairs + 2 singles); approximately 34 effective independent units total, not 62 -- a ~45% reduction in effective independent evidence for the finding's MAGNITUDE (not its sign, since every unit points the same direction). Not computed or reported anywhere in this run's own artifacts; should be applied before any future citation states a bare '62 differences' count."
    - "OBJ-6 (scope precision on RT-BATCH-011/PF-6): this run's finding is orthogonal to, not a narrowing or reopening of, RT-BATCH-011's own shared-RNG-vs-independent-RNG determinism conclusion, which depends on search completeness (non-truncation), not on which RNG scheme was used, and remains fully intact and unaffected here -- reconfirmed by this run's own internal consistency check that archived (shared-RNG, complete) and v8 (independent-RNG, complete) continue to agree exactly at every sweep point's Comparison 1/Comparison 2. This IS a new, standalone, useful finding about truncation itself (relevant to any future amendment attempting to properly test RT-BATCH-011's original boundary question, since it establishes a real confound such a probe must now account for), but it does not itself narrow or answer that boundary question, exactly as OBJECTIVE_BOUNDARY states. Any future citation should state this distinction explicitly."
  required_controls:
    - "Apply the frozen contract's own PF-7 conjugate-pair-correction discipline to the differs counts, not only the resolved counts, before any EV-*/DEC-* citation states a bare 62-differences count or bare proportion -- report ~34 effective independent units alongside the raw 62, and report the composition explanation for the non-monotonic 16.0%/7.5%/26.7% proportion trend (OBJ-4/OBJ-5) rather than the bare percentages alone."
    - "A follow-up sweep point at 1.1-1.2s per-vertex budget (straddling, and for some vertices now at or above, the observed 1.14993s natural-completion floor) to directly test whether delta>=5-value convergence begins appearing there while delta=2/delta=3 remain exactly converged (identity match, not merely count match) -- the cheapest next check of whether convergence is genuinely monotone-in-budget across the full value range or has some other structure this sweep's 3 points cannot yet distinguish."
    - "State explicitly, in any future citation, that this finding is orthogonal to RT-BATCH-011's own RNG-sharing determinism conclusion (OBJ-6) -- a truncation-vs-completeness finding, not an RNG-scheme finding, useful for future truncation-probe design but not itself progress on RT-BATCH-011's original boundary question."
  counterexample_or_mutation: >-
    The cheapest concrete check that would have separated 'the 100%
    directional pattern is a genuine structural property' from 'it happened
    to hold across 62 samples by chance': re-derive the expected sign
    independently from the algorithm's own stated correctness properties
    (Dijkstra invariant + subset-table argument: common(b1) subset-of
    common(b2) for b1<b2 with stable overlap degrees, hence best_deg(b1) >=
    best_deg(b2)) BEFORE looking at the data, then check the data against
    that independent prediction -- done in OBJ-3 above. The prediction held
    with zero exceptions on all 10 checkable value changes and on the full
    subset-nesting of all three resolved sets. If a future sweep point at a
    different prime, or with a non-deterministic RNG-per-call rather than a
    fixed derived seed, ever produced a vertex whose truncated value was
    SMALLER than a longer-budget or complete search's value at the
    identical vertex, that would falsify this mechanism and require
    immediate re-examination of the RNG/seed-derivation wiring -- the
    single cheapest discriminating control for any future reuse of this
    instrument.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale, single-prime search-procedure diagnostic work,
    H-SSIQ-36e970.asymptotic_claim null throughout, correctly inherited and
    unchanged. The relevant baseline remains this campaign's own
    instrument-scrutiny discipline (RT-BATCH-009 through RT-BATCH-012's
    "trace it, don't trust it, bring your own control"), extended here to a
    genuinely new posture: RT-BATCH-012 audited an underpowered NULL result
    and found it uninformative; this review audits a well-powered POSITIVE
    result and finds it holds up under an independently-derived structural
    prediction, not merely a fit to the observed data -- a meaningfully
    different and stronger form of scrutiny than either RT-BATCH-011's
    near-certain-null case or RT-BATCH-012's underpowered-null case
    required.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty -- unchanged by this run, a search-procedure diagnostic rather than a heuristic-conditional asymptotic claim. The one heuristic-shaped assumption worth naming, not one of H-SSIQ-36e970's own numbered items: this run's interpretive scaffold implicitly treats 'a larger declared time_budget_seconds always permits at least as many completed loop iterations on the same hardware' as safe without restating it as a numbered premise. Currently safe -- I checked its consequences directly and they hold with zero exceptions -- but it is a physical/wall-clock premise, not a mathematical one, and should be named explicitly (as PF-3/PF-6 already do for the weaker cross-run/cross-hardware version) if this instrument is reused at larger scale or on more heavily loaded hardware where sweep-point budget margins could be smaller relative to scheduling jitter."
  cost_model_challenges:
    - "No asymptotic-cost claim anywhere in this run. Measured wall-clock 474.14778780937195s against the 1200s/0.4 CPU-hour budget cap (39.5% utilization), matching raw-result.json to full float precision against execution_report.yaml's own OBS-4 per-sweep-point breakdown (121.33s/157.39s/195.02s). Each sweep point modestly exceeds its own naive 194*b bound by the same disclosed soft-cap mechanism this lineage has already reported (timeout check fires only between heap-pop iterations, never mid-call) -- correctly and un-defensively reported, comfortably within the 1200s hard cap and the spec's own ~2.58x worst-case margin. No objection."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated, not exceeded."
    - "raw-result.json's and truncation_sweep_comparison.json's objective_boundary/objective_boundary_note fields correctly restrict this run to a purely descriptive measurement at p=2437 alone, explicitly excluding H-SSIQ-36e970's real-arm prediction, lever L4, and any PERSISTS/WEAKENS vocabulary -- verified by direct grep across all three committed JSON/YAML artifacts, not trusted from spec prose. No scope inflation found; this review's own corrections (OBJ-4/OBJ-5/OBJ-6) are evidentiary-framing corrections for future citation, not scope-inflation defects in what this run itself currently claims."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-j as committed at e2102bfe (parent ca905c24),
    against specification_v10.yaml: the run executes exactly as the frozen
    spec requires (step (0) unwrapped, passing 203/203; three sweep points
    each independently try/except-wrapped per PF-2, all succeeded,
    sweep_point_error null throughout; PF-8's empty-histogram case correctly
    never exercised, all budgets had nonzero n_resolved). What this run
    licenses, narrowly: at p=2437, for the 194-vertex non-F_p-rational
    population under this instrument's fixed per-vertex RNG-seed derivation,
    a per-vertex search budget strictly below the observed 1.14993s
    natural-completion floor produces a delta_e_upper_bound that is NEVER
    SMALLER than, and is frequently strictly larger than, the value the
    identical seed's complete (non-truncated) search finds at the same
    vertex -- a directional bias PROVEN modulo one named wall-clock
    monotonicity premise, independently stress-tested with zero exceptions
    against this run's own raw per-vertex data (exact subset-nesting of all
    three resolved sets; strictly monotone-non-increasing values on every
    multiply-resolved vertex; exact vertex-set-identity convergence of the
    delta=2/delta=3 subpopulations by b=1.0). What this run does NOT
    license: any claim that this bears on RT-BATCH-011's own shared-RNG-vs-
    independent-RNG determinism question (orthogonal -- that conclusion
    rests entirely on non-truncation, which this run never provides at any
    sweep point, and remains untouched); any claim about H-SSIQ-36e970's
    real-arm prediction, lever L4, or a PERSISTS/WEAKENS label (none
    present); and any bare citation of "62 differences" or the raw
    proportion trend without the conjugate-pair correction (~34 effective
    units) and composition explanation this review supplies.
  next_concrete_action: >-
    Coordinator, before drafting any EV-SSIQ-*/DEC-* record citing this
    run: (1) accept RUN-SSIQ-a85692-j's execution fidelity, PF-1 through
    PF-10 implementation, cost/budget honesty, and OBJECTIVE_BOUNDARY
    compliance as clean; (2) treat the core directional finding as PROVEN
    at this toy scale, modulo the named wall-clock monotonicity premise,
    whose testable consequences hold with zero exceptions in this run's own
    raw data -- a materially stronger status than "held across 62 samples";
    (3) any citation of the "62 differences" or the differs-proportion
    trend must include the conjugate-pair-corrected effective sample size
    (~34, not 62) and the composition explanation for the non-monotonic
    16.0%/7.5%/26.7% trend, not the bare numbers alone; (4) state explicitly
    that this finding is orthogonal to, not a narrowing or extension of,
    RT-BATCH-011's own RNG-sharing determinism conclusion -- a new,
    standalone finding about truncation itself, useful for future
    truncation-probe design but not itself progress on RT-BATCH-011's
    boundary question; (5) the single cheapest concrete follow-up this
    run's own data predicts is one more sweep point at 1.1-1.2s, straddling
    the observed 1.14993s floor, to test whether delta>=5 convergence
    begins there while delta=2/delta=3 remain exactly converged; (6) this
    remains, exactly as OBJECTIVE_BOUNDARY states, a single-prime
    descriptive diagnostic -- no extension to H-SSIQ-36e970, lever L4,
    PERSISTS/WEAKENS vocabulary, or any other prime is licensed by this run.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-BATCH-013.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph rebuilt, no artifact altered. Several non-durable, read-only
    local Python computations were run directly against the committed
    truncation_sweep_comparison.json and raw-result.json: (a) parsed all 62
    value_differs_vs_archived_triples across the three sweep points and
    independently recomputed the sign of new_value minus archived_value for
    each (62 >, 0 <, 0 ==); (b) extracted per_vertex_records for all three
    sweep points, computed the resolved-vertex-set subset relations
    (s(0.6) subset-of s(0.8) subset-of s(1.0), verified exact), and found
    every vertex resolved at 2+ budgets with a changed delta_e_upper_bound
    value (10 found, all strictly decreasing as budget grows, 0 increases);
    (c) reconstructed, for the b=1.0 sweep point, the archived (true) value
    for every one of the 187 resolved vertices (via the value_differs
    triples' own archived_value field for non-matching vertices, and the
    new_value itself for matching ones) and checked vertex-set identity
    (not merely count identity) between the delta=2-resolved set and the
    true delta=2 population, and likewise for delta=3, delta=5, and
    delta=7 (found: delta=2 and delta=3 are exact identity matches;
    delta=5 is 1/35 correct; delta=7 is 0/16 correct); (d) computed the
    Frobenius-conjugate-pair structure of the 62 differing triples
    themselves (not merely the resolved sets) at each sweep point, using
    frobenius(x)=(a, p-b) with p=2437, finding ~34 effective independent
    units across the 62 raw triples; (e) grepped raw-result.json,
    truncation_sweep_comparison.json, and execution_report.yaml for
    PERSISTS, WEAKENS, H-SSIQ-36e970, and "lever L4" to confirm every match
    is inside an explicit disclaimer, never an affirmative claim. No file
    was written or edited by any of these computations. Read in full:
    specification_v10.yaml (all PF-1 through PF-10 fix text and both round
    verdicts); RT-BATCH-012.md and RT-BATCH-011.md in full; RUN-SSIQ-a85692-j's
    full package (raw-result.json, execution_report.yaml,
    truncation_sweep_comparison.json, command.txt); delta_e_truncation_sweep_v10.py
    (the full new implementation file, read directly, not taken from spec
    prose or the execution report's own description); delta_e_truncation_probe_v9.py's
    compare_against_archived, compare_against_v8, run_truncation_probe_v9
    (read directly, confirmed genuinely imported and unchanged);
    compute_delta_e.py's build_smooth_table and two_sided_search;
    build_isogeny_graph.py's frobenius and find_roots_with_multiplicity;
    delta_e_independent_rng_probe_v8.py's derive_per_vertex_seed and
    verify_graph_identity; trapping_diagnostic_v5.py's load_archived_prime_data
    and build_graph_for_prime.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-BATCH-013.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v10.yaml and
    every run package) and every ledger record are untouched.
  verdict: CHALLENGE
```
