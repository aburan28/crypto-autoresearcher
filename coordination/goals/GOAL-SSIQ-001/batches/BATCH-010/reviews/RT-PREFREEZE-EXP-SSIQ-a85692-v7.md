# RT-PREFREEZE-EXP-SSIQ-a85692-v7 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v7.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-010

**Reviews `experiments/EXP-SSIQ-a85692/specification_v7.yaml` at `status: draft`,
`pre_freeze_review.status: PENDING`, committed at `6d9f7e55` (working-tree
snapshot for this draft; not yet frozen/approved) under task
`TASK-20260806-a98805`.** Per this task's own operating rules, only a
Coordinator-committed snapshot of a *frozen* artifact is treated as durable
research evidence; this report is advisory input to the Coordinator's own
freeze decision for a pre-freeze draft, matching this lineage's established
practice (`RT-PREFREEZE-EXP-SSIQ-a85692-v6{,-round2,-round3}.md` reviewed the
v6 draft the same way before it froze). It changes nothing under
`experiments/EXP-SSIQ-a85692/` (`specification_v6.yaml` stays frozen at
`66753c92` unedited) or any ledger record.

Read in full: `AGENTS.md`, `CLAUDE.md`, `agents/red-team.md`;
`specification_v7.yaml` (196 lines); `specification_v6.yaml` in full,
including all thirteen `pfN_summary` entries and the frozen `gd12_fix_v6` /
`funnel_structure_diagnostic_v6` text; `RT-BATCH-009.md` in full; the closing
`DEC-20260806-498531.yaml` in full; `trapping_diagnostic_v5.py` (500 lines,
direct read, not trusted from either spec's prose) — confirmed
`build_graph_for_prime(p, seed)` and `load_archived_prime_data(raw_result_path,
prime)` are genuine standalone module-level functions with the signatures v7
claims (spot-checked per the task's instruction, not re-derived from scratch
given v6's own PF-2 finding is settled precedent), and that
`is_structural_local_min` is **not** separately importable (six inline lines,
`is_min = bool(delta_map[v] <= min(nbr_deltas))`, confirmed identical to v7's
disclosed duplicate formula); `build_isogeny_graph.py`'s `build_graph_bfs`
(confirms `g["vertices"]` is `sorted(visited)` — a deterministic, order-stable
list, not a set) and `degree_sequence_check`; `compute_delta_e.py`'s
`run_phase_minus1_on_confirmatory_set` (the delta_E search's own RNG/budget
mechanics, read directly to assess an interpretive confound under Q1);
`RUN-SSIQ-a85692-f/execution_report.yaml`'s ANOM-1 text directly (to confirm
which of the two numeric variants — the original "8-11"/"95/324/478/611"
slip, or RT-BATCH-009's correction "8/11/13/13"/"95/132/194/287" — v7's own
EXPECTED RESULT text uses).

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: >-
    self-reported by this Claude Code subagent session; not probe-verified
    this session (no `orchestration.adapter doctor --probe` run here).
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy
    (CLAUDE.md, "Model policy note"); this session runs `model: inherit`.
    Every credentialed backend under this environment has previously been
    found unprobeable in this campaign's prior reviews; recorded as the
    standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with every producer and every prior reviewer in this
    lineage, including RT-BATCH-009 and all three v6 pre-freeze rounds. It
    does not upgrade the campaign's evidence tier by itself.
```

---

## Bottom line up front

**This draft should NOT be frozen as written.** The core statistical design
(hold the real graph and real value multiset fixed, permute the
vertex-to-value assignment) is sound and does test what it claims to test —
this is not a re-litigation of RT-BATCH-009's already-settled control design.
But formalizing an informal 15/30-trial script into a **1000-trials/prime,
pre-registered, archived, bit-reproducible record** raises the bar on
specification precision, and at that bar two gaps are genuine, code-traceable
regressions or ambiguities that this lineage's own standard (PF-3/PF-7/PF-9)
treats as blocking:

1. **PF-1 [BLOCKING]: the REQUIRED COVERAGE ASSERTION is silently weaker than
   the check it claims to inherit unchanged, and drops a second, separately
   mandatory verification entirely.** v6/`trapping_diagnostic_v5.py` require
   *two* independent checks before trusting a rebuilt graph: (a) delta_map's
   *keys* actually match the rebuilt graph's vertex set
   (`n_matched = len([v for v in delta_map if v in vertex_set])`, compared
   against `archived_n_vertices`), and (b) a graph-rebuild verification
   (`degree_sequence_check.pass` AND rebuilt vertex count ==
   `archived_n_vertices`) — the second check exists specifically because
   PF-11 (v6, round 2) established that the coverage assertion's key-set
   match is "a second, independent vertex-set-fidelity check that a
   same-count/same-degree vertex substitution could still surface," i.e.
   neither check alone is sufficient. v7's own coverage assertion instead
   confirms only `len(delta_map) == archived_n_vertices` — a bare count
   comparison, not a key-membership match — and never mentions
   `degree_sequence_check` or an independent rebuilt-vertex-count check
   anywhere. The draft calls this "per specification_v6.yaml's own
   PF-3/PF-7/PF-13 unified per-prime failure-handling model, **inherited
   unchanged**" — true of the failure-handling *scope*, false of the check's
   own *strength*, which is narrower than what it claims to inherit.
2. **PF-2 [BLOCKING]: the "materially disagrees" anomaly branch has no
   stated failure-handling scope**, unlike the (correctly, per-prime) scoped
   coverage-assertion halt two sentences earlier. If `REAL_DEPTH0_FRACTION`
   does not equal 1.0 on some prime, the draft says only "report it
   honestly... rather than silently reconciling or improvising past it" — it
   never states whether that prime's 1000 null trials are still computed and
   archived, or whether the run halts that prime's computation at that point.
   Two compliant Executors could produce different REQUIRED ARTIFACTS from
   identical input data on this branch alone. This is exactly the
   global-vs-per-prime / unscoped-failure-branch shape that produced v6's own
   PF-3 and PF-7 (both blocking in their rounds).

Five further findings are advisory (do not block freeze, but should be
applied as text-only fixes, per this lineage's established practice for
non-blocking items):

3. **PF-3 [ADVISORY]:** the standard deviation formula (population, ÷N, vs.
   sample, ÷(N−1)) is unspecified, despite the draft being hyper-precise
   everywhere else (the Pearson-correlation and top-decile formulas in v6
   were pinned to the character).
4. **PF-4 [ADVISORY]:** `depth(v)` is applied to "every resulting local
   minimum," silently **broadening** v6's own formula, which was scoped only
   to the *basin-eligible* set (`delta_map[m] > 1`). This broadening is
   almost certainly correct — it matches what RT-BATCH-009 additionally
   checked and what `RUN-SSIQ-a85692-f`'s own (corrected) ANOM-1 figures
   report (95/132/194/287, not 86/114/176/270) — but v7 frames this as
   "using the SAME formulas specification_v6.yaml's own... already
   established," which is imprecise: the *formula* is the same, the *domain*
   is not.
5. **PF-5 [ADVISORY]:** the stated rationale for reporting
   `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` as a raw count rather than a p-value
   fraction — "invites a significance-threshold interpretation... explicitly
   declines to make" — does not achieve what it claims. Any reader can
   trivially divide by the pre-registered, fixed `N_TRIALS=1000` and recover
   the identical ratio; withholding the division removes a convenience, not
   the interpretive risk the rationale names.
6. **PF-6 [ADVISORY, forward-looking control]:** the permutation null
   correctly rules out the *pure alphabet-pigeonhole* null, but neither it
   nor v7's own framing distinguishes "genuine near-Lipschitz structure of
   the smooth-isogeny-degree pseudometric" from "an artifact of the
   delta_E-computation *procedure*" — `compute_delta_e.py`'s own search uses
   one `random.Random` instance per prime, advanced sequentially across all
   non-F_p-rational vertices in **sorted-tuple order** (not graph order),
   under a **shrinking per-vertex time budget**
   (`per_vertex_cap = min(remaining, t_prime)`). This is out of v7's own
   declared zero-new-search-cost scope to fix, but should be named now as the
   next required control before any future amendment treats "near-Lipschitz"
   as established.
7. **PF-7 [ADVISORY, minor clarity]:** the RNG-instance scoping ("a single
   `random.Random(20260806)` instance... for that prime") is defensible on a
   careful re-read as one fresh instance per prime, but is stated twice with
   slightly different phrasing and never says "fresh" or "newly constructed"
   explicitly; and the vertex list used in
   `dict(zip(vertices, shuffled))` is never pinned to a specific data
   structure in the detailed formula (only "the graph's vertex set" appears,
   earlier, in `amendment_scope`'s looser prose). Direct read of
   `build_isogeny_graph.build_graph_bfs` confirms `g["vertices"]` is a
   deterministic `sorted(...)` list (not a set, not BFS-insertion order), so
   there is no actual non-determinism risk here — but the "PRE-REGISTERED...
   bit-identical" claim would be stronger stated explicitly rather than left
   to a reader's own trace.

None of these require redesigning the control; all are fixable at zero new
search cost. But PF-1 and PF-2 change what gets computed/archived, not merely
how it is described, so — per this lineage's own calibration (a finding is
blocking exactly when it leaves the REQUIRED OUTPUT ambiguous or the
verification weaker than what it claims to inherit) — this draft needs a
revision round before freeze.

---

## (1) Is the core control design actually sound? [Q1]

**Yes, as a test of the specific dichotomy it names.** Holding the graph
topology and the exact archived delta_E value multiset fixed and
randomizing only the vertex-to-value assignment is the textbook label-
permutation / spatial-randomization null: it isolates "does the *marginal*
distribution of values plus *graph regularity* alone (few distinct values,
uniform degree) already produce near-universal depth==0 ties" from "is there
something about *which vertex* gets *which value* that matters." RT-BATCH-009
ran exactly this control informally (30 trials/prime) and it is the correct,
cheapest discriminating control for that specific question — I re-derive no
new objection to the *design* itself, and this review does not re-litigate
that settled finding.

**The confound the draft's framing misses**, however, is real and is
different from the pigeonhole question: **the control cannot distinguish
"genuine mathematical (near-Lipschitz) structure in the smooth-isogeny-degree
pseudometric" from "an artifact of how delta_E was computed."** Read
`compute_delta_e.py`'s `run_phase_minus1_on_confirmatory_set` directly
(lines 368–411): for a given prime, `delta_map` for the non-F_p-rational
vertices is filled by iterating `non_fp = [v for v in g["vertices"] if not
field.is_in_fp(v)]` — i.e. in **sorted-tuple order**, not graph-adjacency
order — using **one** `rng_search = random.Random(seeds[0]*1000003 + p)`
instance, advanced sequentially across every vertex in that loop, with a
**shrinking per-vertex time budget** (`per_vertex_cap = min(remaining,
t_prime)`, where `remaining` decreases as the search consumes wall-clock
time). A time-budget-driven or shared-RNG-driven bias in the *search
procedure* could in principle produce correlated delta_E outcomes among
vertices that are *close in sorted-tuple order*, which is a different axis
from *graph adjacency* — so this specific mechanism is not an obvious
confound for the observed *graph-edge* spatial correlation (sorted-tuple
order has no evident relationship to 2-isogeny adjacency for elliptic-curve
coordinate tuples). But the point stands generally: the permutation control
tests spatial structure against the *graph*, and confirms the pattern is not
alphabet-pigeonhole — it does **not**, and cannot by construction, test
whether that confirmed pattern reflects the underlying mathematics (a
2-isogeny edge changing reachable smooth degree by a bounded factor) versus
some property of the *search algorithm* that happens to correlate with graph
structure through a channel this review has not identified. v7's own
`OBJECTIVE_BOUNDARY` correctly declines to interpret mechanism at all, so
this is not a defect *in v7's stated scope* — but it is the cheapest
discriminating control worth naming now, before a future amendment treats
"near-Lipschitz" as more than a candidate hypothesis: **recompute delta_E for
a probe subset of vertices using fresh, per-vertex-independent RNG seeds
(removing the shared, sequentially-advancing `rng_search` instance) and check
whether the graph-edge spatial-autocorrelation signal survives.** See PF-6.

---

## (2) Are the reuse/duplication mechanics correct, and is the depth/is_structural_local_min formula consistent with v6? [Q2]

**Reuse mechanics: confirmed correct by direct spot-check**, per the task's
instruction to check rather than re-derive from scratch. `trapping_diagnostic_v5.py`
(direct read, all 500 lines): `build_graph_for_prime(p, seed)` (lines
133–148) and `load_archived_prime_data(raw_result_path, prime)` (lines
102–130) are both genuine, standalone, module-level functions, matching v7's
claimed signatures and return shapes exactly. `is_structural_local_min` is
**not** a standalone symbol — it is six inline lines inside
`run_diagnostic_for_prime` (`nbr_deltas = [...]; is_min = bool(delta_map[v]
<= min(nbr_deltas))`, lines 222–234) — confirming v7's "authorized, disclosed
duplicate, not genuinely imported" framing is accurate, and the duplicate's
own stated formula (`delta_map[v] <= min(delta_map[u] for u in
adjacency[v])`) matches the source exactly.

**depth(v)'s formula matches v6's exactly; its *domain* does not, and this is
under-disclosed (PF-4).** v6's `funnel_structure_diagnostic_v6` defines
`depth(m)` "for each **basin-eligible** local minimum m" — i.e. restricted to
`{m : is_structural_local_min(m) AND delta_map[m] > 1}`, explicitly excluding
delta_E=1 vertices (v6's own PF-1 fix, "basin-eligible local minima, defined
precisely"). v7 instead computes `depth(v)` "for every resulting local
minimum," with no `delta_map[v] > 1` restriction — a broader domain that
includes delta_E=1 (F_p-rational) local minima, which are *always*
`is_structural_local_min` by triviality (1 is the global minimum) but were
never in scope for v6's `depth` formula. Cross-checked this against
`RUN-SSIQ-a85692-f/execution_report.yaml`'s own ANOM-1 text directly: it
independently re-confirms depth==0 "even more broadly... against ALL
structural local minima (including the delta_E=1 ones excluded from the
basin-eligible set)" — so v7's broader domain is consistent with data that
already exists and with RT-BATCH-009's own additional check, and v7's stated
EXPECTED figures (95/132/194/287, matching RT-BATCH-009's corrected count,
**not** the original run's uncorrected "95/324/478/611" slip) show this is
the intended scope, correctly using the corrected numbers. The finding is
narrow: v7 should say explicitly that it broadens v6's `depth` domain from
basin-eligible-only to every structural local minimum, rather than
describing this only as "the SAME formulas... already established," so a
future reader does not assume v7's denominator equals v6's 646-basin-eligible
figure.

---

## (3) Is the permutation/RNG design deterministic and bit-reproducible? [Q3]

**No bug found in the mechanism itself.** Traced against actual Python
`random` semantics:

- `random.Random.shuffle` is Fisher–Yates via `_randbelow`, fully
  deterministic given a fixed seed and Python version; repeated `.shuffle()`
  calls on one continuously-advancing instance produce a genuinely different,
  independent-looking permutation each call (this is standard practice, not
  a known correlation risk for CPython's Mersenne Twister).
- Duplicate values in the multiset (8–13 distinct integers over 200–600
  vertices) do **not** break anything: Fisher–Yates permutes *positions*, so
  it still produces a uniformly random assignment among the distinct
  vertex-to-value mappings consistent with the fixed value-count multiset —
  exactly the null distribution the control needs, regardless of how many
  ties exist in the value alphabet.
- `list(delta_map.values())`'s iteration order is stable across the run
  (Python 3.7+ dict insertion order; `delta_map` is built once via
  `load_archived_prime_data` and never mutated), so re-shuffling it or
  re-materializing it 1000 times produces the same *starting* order each
  time before the shuffle randomizes it — no hidden order-dependence bug.
- `g["vertices"]` (confirmed by direct read of `build_isogeny_graph.build_graph_bfs`,
  line 624: `vertices = sorted(visited)`) is a deterministic, order-stable
  **list** — not a set, not raw BFS-insertion order — so `dict(zip(vertices,
  shuffled))` is reproducible across separate constructions of the graph
  given the same seed, confirming the "SAME vertex set" claim is bit-stable,
  not merely set-equal.

The residual issue is clarity, not correctness (PF-7): the spec never says
"fresh instance" explicitly (only "a single... instance... for that prime,"
twice, in slightly different phrasing), and never pins `vertices` in the
precise formula to `g["vertices"]` specifically (only the looser
`amendment_scope` prose says "the graph's vertex set"). Given `g["vertices"]`
is provably deterministic, this is advisory, not blocking.

---

## (4) Coverage assertion and per-prime failure-handling — genuinely inherited, or a new gap inside "inherited unchanged"? [Q4]

**A new gap, and a real one — this is the most consequential finding.** v6's
own `trapping_diagnostic_v5.py`-derived coverage assertion (used by every
run in this lineage, a-through-f) computes:

```python
vertex_set = set(vertices)
matched_vertices = [v for v in delta_map if v in vertex_set]
n_matched = len(matched_vertices)
coverage_assertion_pass = bool(n_matched == archived_n_vertices)
```

— i.e. it verifies delta_map's **keys actually correspond** to the rebuilt
graph's actual vertex identities, not merely that the two collections happen
to have the same *size*. v6 additionally requires a **separate**
graph-rebuild verification (`degree_sequence_check.pass` AND `n_built ==
archived_n_vertices`), justified explicitly by PF-11 (v6, round 2): "the
coverage assertion's key set functions as a second, independent
vertex-set-fidelity check that a same-count/same-degree vertex substitution
could still surface" — i.e. *both* checks are needed because either one
alone can be satisfied by a corrupted state the other would catch.

v7's own text: "REQUIRED COVERAGE ASSERTION, per-prime (never global -- per
specification_v6.yaml's own PF-3/PF-7/PF-13 unified per-prime
failure-handling model, inherited unchanged): confirm `len(delta_map) ==
archived_n_vertices`... halt with an explicit error, reported for that prime
only, on any mismatch." This is a **bare cardinality comparison**, not a
key-membership match, and there is no mention anywhere in v7 of
`degree_sequence_check` or an independent rebuilt-vertex-count verification.
"Inherited unchanged" is true of the *scope* (per-prime, non-global) but not
of the *check's own strength* — the check itself has been narrowed relative
to what it claims to inherit, without disclosure. In practice a genuine
vertex-identity mismatch would likely still surface downstream as a
`KeyError` when `adjacency[v]` is looked up against `delta_map`, so this is
unlikely to *silently* corrupt the archived result — but it removes the
informative, targeted diagnostic this lineage deliberately built (PF-9/PF-11)
in favor of a generic crash, and it does so while claiming no change
occurred. **PF-1, blocking**: either restore the two-part check (key-set
match against the rebuilt vertex set, plus `degree_sequence_check`) or state
explicitly, with a reason, why the null-permutation-control use case can rely
on the weaker check alone.

**The per-prime failure-handling model has a second gap, new to this draft
(PF-2, blocking):** the coverage-assertion halt is scoped precisely
("halt... reported for that prime only"). But the separate "materially
disagrees" branch — REAL_DEPTH0_FRACTION doesn't equal 1.0, or disagrees with
`RUN-SSIQ-a85692-f`'s archived ANOM-1 — has **no stated scope at all**: "this
is a REQUIRED, EXPLICITLY DISCLOSED anomaly... report it honestly... rather
than silently reconciling or improvising past it." This tells an Executor
*that* the anomaly must be disclosed, not *whether the 1000 null trials for
that prime are still computed and archived*, or whether the run halts that
prime's computation at the point of detecting the disagreement. Two
compliant Executors could produce materially different `RUN-SSIQ-a85692-g`
artifacts (one with a full null distribution for the anomalous prime, one
without) from the identical underlying inputs on this branch alone — which is
precisely the ambiguity this lineage's PF-3 (round 1) and PF-7 (round 2) were
raised, and treated as blocking, for. Given the *entire purpose* of this
amendment is to archive the null distribution, an Executor reading this
branch as license to halt before computing 1000 trials would defeat the
archival goal; the spec should say explicitly that `NULL_DEPTH0_FRACTIONS`
is computed and reported for a prime **regardless of** whether
REAL_DEPTH0_FRACTION matches its expected value.

---

## (5) Is NULL_EXCEEDS_OR_EQUALS_REAL_COUNT the right thing to report? [Q5]

**The metric itself is reasonable (a one-sided permutation-test count is
standard and well-defined); the stated justification for withholding the
division is weaker than claimed (PF-5, advisory).** The draft declines to
report a p-value fraction "since a claimed p-value invites a
significance-threshold interpretation this diagnostic's own
OBJECTIVE_BOUNDARY... explicitly declines to make." But `N_TRIALS = 1000` is
itself a fixed, pre-registered, disclosed constant in the same record —
nothing prevents (or meaningfully discourages) a future reader from dividing
`NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` by 1000 and treating the result exactly
as a p-value, including applying an implicit significance threshold to it.
Withholding the division removes a convenience for the reader, not the
interpretive risk the rationale names — the interpretive discipline has to
come from an explicit caveat wherever this number is *used* downstream (e.g.
in a future `EV-SSIQ-*`/`DEC-*` citing it), not from omitting an
arithmetically trivial step here. Recommend either (a) accepting this and
stating the rationale more modestly ("reported as a count for direct
legibility, not to imply a formal significance test — dividing by N_TRIALS
recovers the equivalent one-sided permutation p-value, which should not be
read against a conventional threshold without a stated pre-registered
alpha"), or (b) keeping the count-only choice but dropping the "declines a
significance-threshold interpretation" framing, which the choice does not
actually deliver.

---

## (6) Other underspecification, ambiguity, or scope-creep risk [Q6]

- **PF-3 [ADVISORY]:** standard deviation is listed among the "REQUIRED
  SUMMARY STATISTICS" with no formula specified (population, ÷N_TRIALS, vs.
  sample, ÷(N_TRIALS−1)) — a real numeric difference (~0.05% relative for
  N=1000, small but non-zero, and inconsistent with this draft's own
  insistence elsewhere — e.g. the top-decile `k = max(1, ceil(0.1 *
  n_basin_eligible))` formula in v6 — on pinning every formula exactly, not
  leaving a reader to infer the convention).
- **No scope creep found.** The amendment's own framing ("zero new search
  cost," "does not itself constitute a new claim... does not resolve the
  funnel-structure mechanism question") is accurate and matches
  `DEC-20260806-498531`'s ranked action item (1) exactly; it does not attempt
  action (2) (a new depth operationalization) or the B/X-widening
  falsification test, both explicitly and correctly deferred.
- **Budget is generously sized and correctly derived**: 4000 total
  permutation trials (1000/prime) against RT-BATCH-009's own measured
  "under 5 seconds" for 120 trials scales to roughly 3 minutes worst-case,
  comfortably inside the inherited 900s/0.3-CPU-hour budget; no new graph
  construction cost beyond the same rebuild every amendment since v5
  performs. No objection.
- **required_artifacts are complete** against AGENTS.md's artifact-policy
  list (manifest, raw-result, execution report, source-access log, command,
  environment, stdout/stderr, plus the new `permutation_null_control.json`);
  `RUN-SSIQ-a85692-g` does not collide with any existing run id (a–f exist,
  g does not).
- **No affected-vs-safe scheme, asymptotic claim, or heuristic-conditional
  complexity claim appears anywhere** — `H-SSIQ-36e970.heuristic_assumptions`
  remains correctly empty; this control is instrument-level diagnostic work,
  not a proof-oriented proposal, and `proof_search_map.not_applicable_reason`
  is correctly inherited. Attacked and held.

---

## Objections

- **OBJ-1 [PF-1, BLOCKING]:** The REQUIRED COVERAGE ASSERTION narrows v6's
  own two-part check (key-membership match against the rebuilt graph's
  vertex set, plus an independent `degree_sequence_check`/vertex-count
  verification) to a bare `len(delta_map) == archived_n_vertices` comparison,
  while describing this as "inherited unchanged" from v6's own per-prime
  model. The scope (per-prime, non-global) is correctly inherited; the
  check's own strength is not, and this discrepancy is undisclosed.
- **OBJ-2 [PF-2, BLOCKING]:** The "materially disagrees" anomaly branch
  (REAL_DEPTH0_FRACTION != 1.0 or disagrees with archived ANOM-1) states a
  disclosure obligation but no failure-handling scope — unlike the
  precisely-scoped coverage-assertion halt two sentences earlier — leaving
  ambiguous whether that prime's 1000 null trials are still computed and
  archived. Two compliant Executors could produce materially different
  required artifacts from this branch alone.
- **OBJ-3 [PF-3, ADVISORY]:** Standard deviation's formula (population vs.
  sample) is unspecified, inconsistent with this draft's own precision
  standard elsewhere.
- **OBJ-4 [PF-4, ADVISORY]:** `depth(v)`'s domain silently broadens beyond
  v6's own basin-eligible-only scope to every structural local minimum;
  correct and consistent with archived data (confirmed against
  `RUN-SSIQ-a85692-f`'s own corrected ANOM-1 figures), but described as "the
  SAME formulas... already established" without disclosing the domain
  change.
- **OBJ-5 [PF-5, ADVISORY]:** The stated rationale for reporting a raw count
  instead of a p-value fraction does not achieve its own stated goal, since
  the fixed, disclosed `N_TRIALS=1000` makes the division trivial for any
  reader.
- **OBJ-6 [PF-6, ADVISORY, forward-looking]:** The null control rules out
  pure alphabet-pigeonhole but cannot, by construction, distinguish genuine
  smooth-degree mathematical structure from a delta_E-computation-procedure
  artifact (shared, sequentially-advancing RNG plus a shrinking per-vertex
  time budget in `compute_delta_e.py`, applied in sorted-tuple rather than
  graph order) — out of this amendment's own declared scope to fix, but
  should be named now as the next required control before "near-Lipschitz"
  is treated as more than a candidate hypothesis.
- **OBJ-7 [PF-7, ADVISORY, minor]:** RNG-instance-per-prime scoping and the
  precise identity of "vertices" in the permutation formula are correct on a
  careful trace (confirmed `g["vertices"]` is a deterministic sorted list)
  but are not pinned down explicitly enough for a "PRE-REGISTERED...
  bit-identical" claim to be self-evidently true without that trace.

## Required controls

- Before freeze: restore or explicitly justify the coverage
  assertion's strength (PF-1) and state the failure-handling scope of the
  "materially disagrees" anomaly branch (PF-2) — both required so that a
  single, unambiguous Executor implementation is determined by the frozen
  text, matching this lineage's own bar for what counts as "required output"
  ambiguity.
- Before freeze (text-only, zero cost): pin the standard-deviation formula
  (PF-3), disclose the depth-domain broadening relative to v6 (PF-4), and
  either soften or drop the "declines a significance-threshold
  interpretation" claim for the raw-count metric (PF-5).
- Not required for this amendment, but should be named in the record as the
  next open control (PF-6): re-run a probe subset of the delta_E search with
  per-vertex-independent RNG seeding (removing the shared, sequentially
  advancing `rng_search` instance in `compute_delta_e.py`) and check whether
  the graph-edge spatial-autocorrelation signal persists, before crediting it
  to genuine near-Lipschitz smooth-degree structure rather than a search
  procedure artifact.

## Counterexample or mutation

**PF-1's counterexample:** a delta_map whose keys are 203 vertex tuples that
do **not** correspond 1:1 to `g["vertices"]`'s actual 203 members (e.g. one
key swapped for a distinct off-graph tuple, with the count preserved) would
pass v7's own coverage assertion (`len(delta_map) == 203`) while failing
v6's stronger key-membership check (`n_matched < 203`) — v7's own check would
not catch this before a later `KeyError` (or, in the worst case, a silently
incomplete iteration if the mismatched keys never get looked up), whereas
v6's check reports it immediately, by name, per-prime.

**PF-2's counterexample:** two Executors implementing "report [a
REAL_DEPTH0_FRACTION disagreement] honestly... rather than silently
reconciling or improvising past it" could reasonably choose (a) record the
anomaly and continue to compute+archive that prime's 1000 null trials, or
(b) record the anomaly and skip that prime's null-trial computation entirely
(treating the anomaly as invalidating further work on that prime, by analogy
with the adjacent coverage-assertion halt). Both are compliant readings of
the same sentence; the resulting `RUN-SSIQ-a85692-g/permutation_null_control.json`
would differ in content for that prime.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense (toy-scale
infrastructure and a statistical-control archival task, `asymptotic_claim:
null` throughout, correctly inherited). The relevant baseline is this
lineage's own established specification-precision discipline (PF-3/PF-7's
scope-ambiguity standard; PF-9/PF-11's two-part vertex-verification
standard) — v7 meets that discipline everywhere except the two blocking
findings above, both of which are narrowings of, or gaps beside, checks this
same lineage already built and justified in v6.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains correctly empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage.
PF-6's confound (search-procedure artifact vs. genuine near-Lipschitz
structure) is a candidate mechanical hypothesis for a *future* amendment, not
a heuristic feeding any complexity claim in this one.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly). The budget note's arithmetic (4000 total trials, ~33x
RT-BATCH-009's measured 120-trial/<5s baseline) is correct and generously
inside the inherited 900s/0.3-CPU-hour budget; no objection to the cost
model itself.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly
stated and not exceeded. `OBJECTIVE_BOUNDARY` correctly states this control
"does not itself constitute a new claim... does not resolve the
funnel-structure mechanism question" — matches `DEC-20260806-498531`'s
ranked action item (1) exactly, with actions (2) and the B/X-widening test
correctly and explicitly deferred, not silently dropped. No scope inflation.

## Proof architecture challenges

Not applicable — this remains a direct instrument-level statistical control
archival task, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited unchanged,
attacked and held every prior batch including this one).

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v7.yaml` as committed
at `6d9f7e55`, `status: draft`: the core permutation-null control design is
sound and correctly formalizes the dichotomy (coarse-alphabet pigeonhole vs.
genuine graph-spatial structure) RT-BATCH-009's informal 30-trial run and the
Coordinator's independent 15-trial reproduction already established;
`build_graph_for_prime`/`load_archived_prime_data` are confirmed genuinely
importable and `is_structural_local_min`'s disclosed-duplicate formula is
confirmed correct by direct read, consistent with v6's settled PF-2 finding.
Two blocking gaps remain: the REQUIRED COVERAGE ASSERTION is narrower than
what it claims to inherit from v6 (a bare count comparison, not a
key-membership match, and no separate graph-rebuild verification), and the
"materially disagrees" anomaly branch leaves the scope of its own
failure-handling unstated, in the same global-vs-per-prime-ambiguity shape
this lineage's PF-3/PF-7 already treated as blocking. Five further findings
are advisory text-only fixes (SD formula, depth-domain disclosure, the raw-
count rationale's overclaim, and a forward-looking control naming a
delta_E-computation-procedure confound the null cannot rule out). None
requires redesigning the control or a new experiment; all are resolvable
before the next review round at zero new search cost.

## Next concrete action

Coordinator: return this draft for one revision round applying PF-1 and PF-2
(restore or explicitly justify the coverage assertion's strength; state the
"materially disagrees" branch's failure-handling scope, explicitly requiring
that a prime's 1000 null trials are computed and archived regardless of
whether REAL_DEPTH0_FRACTION matches its expected value), plus the three
text-only advisory fixes (PF-3 SD formula; PF-4 depth-domain disclosure;
PF-5 soften or drop the significance-threshold-avoidance claim) that can be
applied in the same pass without a dedicated re-verification round, per this
lineage's own established practice. Record PF-6 (the delta_E-computation-
procedure confound) as a named, deferred control for whichever future
amendment next interprets ANOM-1's mechanism, not as a requirement of this
archival task.

## Overall verdict

**DO-NOT-FREEZE.** Two blocking findings survive: PF-1 (the REQUIRED
COVERAGE ASSERTION is narrower than the check it claims to inherit unchanged
from v6, and drops v6's separate graph-rebuild verification without
disclosure or justification) and PF-2 (the REAL_DEPTH0_FRACTION-disagreement
anomaly branch has no stated failure-handling scope, leaving the required
output ambiguous in the same shape this lineage's own PF-3/PF-7 already
treated as blocking). Five advisory findings (PF-3 through PF-7) should be
applied in the same revision pass. The core control design itself (Q1) is
sound and not in question; this is a specification-precision gate, not a
design-validity objection — consistent with this lineage's own repeated
pattern (v6 needed three rounds for defects of exactly this shape before
reaching FREEZE-WITH-FIXES).

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v7
  task_id: TASK-20260806-a98805
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v7.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at 6d9f7e55, pre_freeze_review.status:
    PENDING -- formalizes the delta_E label-permutation null control
    (RT-BATCH-009's informal 30-trial run, the Coordinator's independent
    15-trial reproduction) into a 1000-trials/prime, pre-registered, archived
    run record (RUN-SSIQ-a85692-g), per DEC-20260806-498531's ranked action
    item (1).
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: The REQUIRED COVERAGE ASSERTION (len(delta_map) == archived_n_vertices) is a bare cardinality comparison, narrower than v6's own two-part check (key-membership match of delta_map against the rebuilt graph's actual vertex set, PLUS a separate degree_sequence_check/vertex-count graph-rebuild verification, justified explicitly by v6's own PF-11: 'a second, independent vertex-set-fidelity check that a same-count/same-degree vertex substitution could still surface'). v7 describes this as 'inherited unchanged' from v6's per-prime failure-handling model -- true of the scope, false of the check's own strength, and the graph-rebuild verification is dropped without mention. Directly confirmed by reading trapping_diagnostic_v5.py's own coverage_assertion_pass computation (n_matched = len([v for v in delta_map if v in vertex_set])) against v7's stated formula."
    - "OBJ-2 [PF-2, BLOCKING]: The 'materially disagrees' anomaly branch (REAL_DEPTH0_FRACTION != 1.0, or disagreeing with RUN-SSIQ-a85692-f's archived ANOM-1) states only a disclosure obligation ('report it honestly... rather than silently reconciling or improvising past it') with no stated failure-handling SCOPE, unlike the precisely-scoped coverage-assertion halt two sentences earlier ('halt... reported for that prime only'). Two compliant Executors could produce materially different RUN-SSIQ-a85692-g artifacts (one still computing and archiving that prime's 1000 null trials, one halting that prime's computation on detecting the anomaly) from the same text -- the same global-vs-per-prime/unscoped-failure-branch shape this lineage's PF-3 (v6 round 1) and PF-7 (v6 round 2) were both raised, and treated as blocking, for."
    - "OBJ-3 [PF-3, ADVISORY]: Standard deviation is listed among the REQUIRED SUMMARY STATISTICS with no formula specified (population /N_TRIALS vs. sample /(N_TRIALS-1)) -- inconsistent with this draft's own (and v6's) established practice of pinning every formula exactly (e.g. the top-decile k = max(1, ceil(0.1*n_basin_eligible)) formula)."
    - "OBJ-4 [PF-4, ADVISORY]: depth(v) is computed for 'every resulting local minimum,' silently broadening v6's own formula, which was scoped only to the basin-eligible set (delta_map[m] > 1, v6's own PF-1 fix). The broadening is correct and consistent with RUN-SSIQ-a85692-f's own corrected ANOM-1 figures (95/132/194/287, independently confirmed by direct read of execution_report.yaml, not the original run's uncorrected '95/324/478/611' slip that RT-BATCH-009 caught) and with RT-BATCH-009's own additional check -- but v7 frames this only as 'using the SAME formulas specification_v6.yaml's own... already established,' without disclosing that the DOMAIN, not just the formula, differs from v6."
    - "OBJ-5 [PF-5, ADVISORY]: The rationale for reporting NULL_EXCEEDS_OR_EQUALS_REAL_COUNT as a raw count rather than a p-value fraction ('invites a significance-threshold interpretation... explicitly declines to make') does not achieve its stated goal: N_TRIALS=1000 is itself fixed and disclosed in the same pre-registered record, so any reader can trivially recover the identical ratio by dividing. Withholding the division removes a convenience, not the interpretive risk the rationale names."
    - "OBJ-6 [PF-6, ADVISORY, forward-looking]: The permutation null correctly rules out pure alphabet-pigeonhole (confirmed sound design, Q1) but cannot, by construction, distinguish genuine near-Lipschitz smooth-isogeny-degree structure from an artifact of the delta_E-computation PROCEDURE. Directly read compute_delta_e.py's run_phase_minus1_on_confirmatory_set: one random.Random(seeds[0]*1000003+p) instance is advanced sequentially across all non-F_p-rational vertices in SORTED-TUPLE order (not graph order), under a shrinking per-vertex time budget (per_vertex_cap = min(remaining, t_prime)). Out of v7's own declared zero-new-search-cost scope to fix, but should be named now as the next required control (recompute delta_E for a probe subset with per-vertex-independent fresh RNG seeding and check whether the graph-edge spatial correlation persists) before any future amendment credits the pattern to genuine mathematical structure."
    - "OBJ-7 [PF-7, ADVISORY, minor]: RNG-instance-per-prime scoping and the precise identity of 'vertices' in the permutation formula are correct on careful trace (confirmed g['vertices'] is a deterministic sorted(...) list via direct read of build_isogeny_graph.build_graph_bfs, not a set or BFS-insertion order) but are not pinned down explicitly enough in the formula text itself for the 'PRE-REGISTERED... bit-identical' claim to be self-evidently true without that trace."
  required_controls:
    - "PF-1 [BLOCKING]: restore v6's two-part coverage/graph-rebuild verification (key-membership match against the rebuilt vertex set, plus degree_sequence_check + rebuilt-vertex-count match), or state explicitly, with a reason, why the weaker single-count check suffices for this specific control's use case."
    - "PF-2 [BLOCKING]: state the failure-handling scope of the REAL_DEPTH0_FRACTION-disagreement anomaly branch explicitly -- specifically, whether that prime's 1000 null trials are still computed and archived (required, given the amendment's own archival purpose) or whether the anomaly halts further computation for that prime."
    - "PF-3/PF-4/PF-5 [ADVISORY]: pin the standard-deviation formula; disclose the depth-domain broadening relative to v6; soften or drop the significance-threshold-avoidance rationale for the raw-count metric. All three are text-only, zero new search cost, and can be applied in the same revision pass as PF-1/PF-2 without a dedicated re-verification round, per this lineage's own established practice for advisory-only findings."
    - "PF-6 [not required for this amendment; record as the next open control]: a probe re-run of the delta_E search with per-vertex-independent RNG seeding, to test whether the graph-edge spatial-autocorrelation signal is procedure-driven or reflects genuine near-Lipschitz smooth-degree structure, before a future amendment credits the latter."
  counterexample_or_mutation: >-
    PF-1: a delta_map whose 203 keys do not correspond 1:1 to g["vertices"]'s
    actual 203 members (e.g. one key swapped for an off-graph tuple, count
    preserved) passes v7's own coverage assertion (len(delta_map) == 203)
    while failing v6's stronger key-membership check (n_matched < 203) --
    v7's own check would not catch this before a later KeyError, whereas
    v6's reports it immediately, by name, per-prime.
    PF-2: two compliant Executors reading "report it honestly... rather than
    silently reconciling or improvising past it" could reasonably choose (a)
    continue computing and archiving that prime's 1000 null trials after
    recording the anomaly, or (b) halt that prime's computation on detecting
    it, by analogy with the adjacent coverage-assertion halt -- both are
    compliant readings of the same sentence, producing different archived
    artifacts for that prime.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure, asymptotic_claim null throughout, correctly
    inherited). The relevant baseline is this lineage's own established
    specification-precision discipline (PF-3/PF-7's scope-ambiguity
    standard; PF-9/PF-11's two-part vertex-verification standard) -- v7
    meets that discipline everywhere except the two blocking findings above,
    both narrowings of or gaps beside checks this same lineage already built
    and justified in v6.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. PF-6's search-procedure-artifact-vs-genuine-structure confound is a candidate mechanical hypothesis for a future amendment, not a heuristic feeding any complexity claim in this one."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere (asymptotic_claim: null, correctly). The budget note's arithmetic (4000 total trials, ~33x RT-BATCH-009's measured 120-trial/<5s baseline) is correct and generously inside the inherited 900s/0.3-CPU-hour budget; no objection to the cost model itself."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "OBJECTIVE_BOUNDARY correctly states this control does not itself constitute a new claim and does not resolve the funnel-structure mechanism question, matching DEC-20260806-498531's ranked action item (1) exactly, with actions (2) and the B/X-widening test correctly and explicitly deferred rather than silently dropped. No scope inflation found."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level statistical control archival task, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v7.yaml as committed
    at 6d9f7e55, status: draft: the core permutation-null control design is
    sound and correctly formalizes the coarse-alphabet-pigeonhole-vs-genuine-
    spatial-structure dichotomy RT-BATCH-009's informal run already
    established; the named reuse functions are confirmed genuinely
    importable and is_structural_local_min's disclosed-duplicate formula is
    confirmed correct by direct read. Two blocking gaps remain: the REQUIRED
    COVERAGE ASSERTION is narrower than what it claims to inherit from v6
    (a bare count comparison, not a key-membership match, with v6's separate
    graph-rebuild verification dropped and undisclosed), and the "materially
    disagrees" anomaly branch leaves its own failure-handling scope
    unstated, in the same shape this lineage's PF-3/PF-7 already treated as
    blocking. Five further findings are advisory, text-only fixes. None
    requires redesigning the control or running new search; all are
    resolvable in one revision pass at zero new search cost.
  next_concrete_action: >-
    Coordinator: return this draft for one revision round applying PF-1 and
    PF-2 (restore or explicitly justify the coverage assertion's strength;
    state the "materially disagrees" branch's failure-handling scope,
    explicitly requiring that a prime's 1000 null trials are computed and
    archived regardless of whether REAL_DEPTH0_FRACTION matches its expected
    value), plus PF-3/PF-4/PF-5 as text-only additions in the same pass, per
    this lineage's own established practice for advisory-only findings not
    requiring a dedicated re-verification round. Record PF-6 as a named,
    deferred control for whichever future amendment next interprets ANOM-1's
    mechanism.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v7.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no permutation trial executed --
    this review is a specification trace, not an execution. Directly read
    (not sampled from prose): trapping_diagnostic_v5.py in full (500 lines),
    confirming build_graph_for_prime/load_archived_prime_data are genuine
    standalone module-level functions and is_structural_local_min is an
    inline six-line formula, not importable; build_isogeny_graph.py's
    build_graph_bfs (confirming g["vertices"] is a deterministic sorted list)
    and degree_sequence_check; compute_delta_e.py's
    run_phase_minus1_on_confirmatory_set (confirming the shared,
    sequentially-advancing per-prime RNG and shrinking per-vertex time
    budget underlying PF-6's confound); RUN-SSIQ-a85692-f/execution_report.yaml's
    ANOM-1 text directly (confirming v7's stated EXPECTED figures use
    RT-BATCH-009's corrected 95/132/194/287, not the original run's
    uncorrected 95/324/478/611 slip); specification_v6.yaml in full,
    including its coverage assertion and graph-rebuild verification text and
    all thirteen pfN_summary entries; DEC-20260806-498531.yaml and
    RT-BATCH-009.md in full. No file written outside this report; no run
    artifact, specification file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v7.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml and
    specification_v7.yaml themselves) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
