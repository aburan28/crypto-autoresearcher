# RT-PREFREEZE-EXP-SSIQ-a85692-v8-ROUND3 — Round 3 pre-freeze Red Team
# review of the DRAFT amendment `specification_v8.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-011, task `TASK-20260806-0d9ec7`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v8.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED` (round 2, DO-NOT-FREEZE
on PF-9), a working-tree draft not yet frozen.** Per this task's operating
rules, only a Coordinator-committed snapshot of a *frozen* artifact is
treated as durable research evidence; this is advisory pre-freeze input. It
changes nothing under `experiments/EXP-SSIQ-a85692/` and commits nothing.

**Mission for this round, stated explicitly per the task brief: hunt for a
THIRD independent path to the same catastrophic outcome (up to 3600s of real,
non-recoverable compute spent, PART B crashes before writing an interpretable
result), not merely confirm round 1/round 2's fixes.** Every claim below is
re-derived from direct reads of the current draft and the actual code it
imports or must reimplement, not trusted from round 1/round 2's own reports.

Read in full: `AGENTS.md`, `agents/red-team.md`,
`RT-PREFREEZE-EXP-SSIQ-a85692-v8.md` (round 1),
`RT-PREFREEZE-EXP-SSIQ-a85692-v8-round2.md` (round 2);
`specification_v8.yaml` (current, 544 lines) in full. Directly read (not
trusted from prose or from either prior round's report): `RUN-SSIQ-a85692-b/
raw-result.json`'s `phase_minus1_real_search["2437"]` entry (independently
re-extracted `n_vertices=203`, `n_non_fp_rational=194`,
`delta_map` length `== 203`, confirming `9` F_p-rational entries by direct
count, not by trusting the draft's own arithmetic);
`delta_e_permutation_null_control_v7.py` in full (`local_min_and_depth`,
`depth0_fraction`, `rebuild_and_verify`, `run_for_prime`, including the
exact `permuted_map = dict(zip(vertices, values))` construction, which round
1/round 2 did not need to trace since it is inherited via `run_for_prime`,
never imported by v8); `compute_delta_e_v2.py`'s `real_execution_budget_v2`
(`compute_delta_e_v2.py:259-261`, the F_p-rational wiring step) and its
`_json_safe_phase_minus1_row`/`delta_map_json_safe` pattern
(`compute_delta_e_v2.py:291-303`); `compute_delta_e.py`'s `two_sided_search`/
`build_smooth_table` (confirmed bounded, non-raising on ordinary timeout);
`build_isogeny_graph.py`'s `Fp2Field`, `build_graph_bfs` (vertex-set
uniqueness via Python `set`, adjacency-vertices consistency,
`find_roots_with_multiplicity`'s own rare-failure raise conditions),
`degree_sequence_check`; `trapping_diagnostic_v5.py`'s
`build_graph_for_prime` (the `time_budget_seconds=900` BFS-rebuild timeout).

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
    lineage (rounds 1 and 2). Does not upgrade the campaign's evidence tier
    and does not itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**No third blocking crash path was found. This draft can be frozen once two
small, zero-additional-compute, text-only clarifications are applied.**
PF-9's fix (round 2) is not merely "not contradicted" — I re-derived,
independently and from first principles, a positive argument for *why* it is
now sufficient, covering ground round 1/round 2 did not need to cover
(neighbour-guard consistency, and the permutation-trial loop's own,
non-literally-imported construction). I also found two new, narrow,
non-blocking gaps of the identical *class* PF-9 was about (an
implicit-but-unstated construction step) — but both are provably harmless
under the current design, not live crash risks, which is why they are
advisory rather than blocking.

1. **PF-9 [round 2, BLOCKING] — RE-VERIFIED, HOLDS, WITH A COMPLETE POSITIVE
   ARGUMENT (not merely "no counterexample found").** See §1 below for the
   full derivation. The short version: `graph["vertices"]` is provably
   duplicate-free (built from a Python `set` in `build_graph_bfs`, confirmed
   by direct read); the F_p-rational and non-F_p-rational construction loops
   are a deterministic, mutually-exclusive, jointly-exhaustive partition of
   that exact list (both loops range over `graph["vertices"]` under
   `is_in_fp`, a pure function); therefore `len(new_delta_map) ==
   len(graph["vertices"]) == 203` cannot be reached by any means other than
   "every vertex has exactly one entry" — there is no duplicate-overwrite or
   extraneous-key path that could make the count 203 while the *membership*
   is wrong. Archived data independently confirms the arithmetic underlying
   this (`n_vertices=203`, `n_non_fp_rational=194`, archived `delta_map`
   length `== 203`, all re-extracted directly from
   `RUN-SSIQ-a85692-b/raw-result.json` this round, not merely re-cited).

2. **PF-12 [NEW, ADVISORY, not blocking — same class as PF-9 but proven
   harmless].** PART B's 1000-trial permutation loop (`shuffle` + `zip` onto
   `vertices`) is, on direct trace, **not** literally covered by the "GENUINELY
   IMPORTED, UNCHANGED" language the draft uses for `depth0_fraction`/
   `summary_stats` — those two functions are the *only* things v7's
   `run_for_prime` exports that v8 imports; the shuffle/zip loop itself lives
   inside `run_for_prime`, which `required_artifacts_note` confirms is never
   imported. So this loop is new code an Executor must write for v8, not
   code reused by reference. The draft's phrase "run the IDENTICAL procedure
   specification_v7.yaml already established" therefore slightly overstates
   code-identity for this one piece. **This does not reopen a crash path**
   (see §3's positive argument: the loop is safe by a length-invariant that
   holds regardless of the exact zip/shuffle implementation, once PF-9's gate
   has passed) — but it is the same *shape* of gap PF-9 itself was: an
   important construction step described only by cross-reference to "the
   identical procedure" rather than restated as an explicit, self-sufficient
   step. Zero-cost fix: state the `base_values = list(new_delta_map.values());
   shuffle a copy; permuted_map = dict(zip(vertices, shuffled))` step
   explicitly, or (matching this file's own established convention) mark it
   as an "(ii) AUTHORIZED, DISCLOSED DUPLICATE" of `run_for_prime`'s own
   inline logic, the same label `delta_e_permutation_null_control_v7.py`'s
   own docstring already uses for its non-importable pieces.

3. **PF-13 [NEW, ADVISORY, defensive-only — no live crash under the text as
   written].** `probe_delta_e_comparison.json`'s required
   `n_value_differs` output — "the full list of (vertex, archived_value,
   new_value) triples for every differing vertex" — is the first time this
   experiment lineage has required writing per-vertex identity into a JSON
   artifact as anything other than an aggregate count. Traced directly: as
   literally specified (a **list** of triples, vertex nested as a **value**,
   never as a dict key), this is JSON-safe with zero special handling —
   Python's `json` module serializes a tuple exactly like a list when it
   appears as a value, recursively, so `[[a, b], archived_val, new_val]`
   round-trips with a plain `json.dump` call. **No crash is implied by the
   text as written.** The residual risk is purely defensive: nothing in the
   draft forecloses an Executor's natural shortcut of also dumping
   `new_delta_map` itself directly as a `{vertex: value}` dict (e.g. for
   convenience, to "just save the whole map") — which **would** raise
   `TypeError` at `json.dump` time (Python dict keys must be str/int/float/
   bool/None, never tuple), and would do so only *after* all real compute
   for the run is already spent, i.e., exactly the failure class this whole
   review is watching for. This precedent already exists and is already
   solved once in this codebase (`compute_delta_e_v2.py:291-303`'s
   `delta_map_json_safe = {str(list(k)): v for k, v in delta_map.items()}`),
   but the draft never cites it for this new output shape. Zero-cost fix:
   one sentence stating that any vertex-keyed artifact output must use the
   `str(list(v))`-keyed convention `compute_delta_e_v2.py` already
   established, and that raw tuple keys are never written directly.

---

## (1) Is `len(new_delta_map) == len(graph["vertices"]) == 203` actually a
correct and sufficient gate now? [task question 1]

**Yes — re-derived here as a complete positive argument, not merely
re-confirmed by absence of a counterexample.**

- **Vertex-set uniqueness.** `build_graph_bfs` (`build_isogeny_graph.py:583-635`,
  read directly) constructs `visited = set([seed])`, only ever adds to it via
  `visited.add(u)` guarded by `if u not in visited`, and returns
  `vertices = sorted(visited)`. A Python `set` cannot contain a duplicate
  value under `==`/`hash` (and these are plain `(int, int)` tuples, already
  confirmed hashable/collision-free by round 1's PF-7). So `graph["vertices"]`
  is, by construction, a list with **no duplicate entries** — the "could a
  duplicate key inflate the count to 203 while missing a real vertex"
  question the task asked has a structural **no** answer, not merely an
  empirical one.
- **Archived counts independently re-derived, not re-cited.** I re-extracted
  `RUN-SSIQ-a85692-b/raw-result.json`'s `phase_minus1_real_search["2437"]`
  entry directly this round:
  `n_vertices=203`, `n_non_fp_rational=194`, `n_resolved=194`,
  `m_coverage_all_vertices_fraction=1.0`, and — checked directly, not merely
  inferred — **the archived `delta_map` object itself has exactly `203`
  keys**. `203 - 194 = 9`, matching the draft's own claimed F_p-rational
  count exactly, and matching `compute_delta_e_v2.py:259-261`'s own
  construction (`for v in g["vertices"]: if field.is_in_fp(v): delta_map[v]
  = 1`), which is the exact mechanism the archived data was produced by
  (PF-2, confirmed holding). The 194+9=203 arithmetic the draft leans on is
  not an assumption; it is what actually happened in the run this amendment
  is diffing against.
- **The two construction loops are a deterministic partition, not merely
  "expected to sum to 203."** `field.is_in_fp(v)` (`Fp2Field.is_in_fp`,
  `build_isogeny_graph.py:94-95`) is a pure function of `v` with no internal
  state — `x[1] % self.p == 0`. PART A's two loops (the F_p-rational wiring
  step and the non-F_p-rational search loop) both range over the identical
  list `graph["vertices"]`, filtered by this same pure boolean. Since it is
  a boolean partition (every vertex is in exactly one of the two branches,
  never both, never neither), and since both loops only ever write keys
  drawn from `graph["vertices"]` (never a key manufactured elsewhere), the
  keyset of `new_delta_map` is, by construction, a **subset** of
  `graph["vertices"]`'s value-set, with `len(new_delta_map) ==
  len(graph["vertices"])` reachable **only** when every vertex was written
  exactly once. There is no path by which `len()` could reach 203 through
  duplicate overwrites of a smaller true-membership set, or through
  extraneous keys not in `graph["vertices"]` — both are structurally
  excluded, not merely unlikely. This directly answers the task's specific
  worry about "a duplicate key overwriting a distinct vertex."

## (2) Does `depth0_fraction` have any OTHER precondition beside `delta_map`
having all 203 keys? [task question 2]

**Yes, one — and it is also closed, by the same argument, not by a separate
one.** Direct trace of `local_min_and_depth` (`delta_e_permutation_null_
control_v7.py:133-156`): the loop is `for u in adjacency[v]: if u not in
delta_map: raise`. This is a **second**, distinct existence requirement — not
on `v` itself (which PF-9's gate covers) but on **every neighbour of every
vertex**. This is exactly the guard PF-1's own counterexample used to
demonstrate the original crash (the "neighbour guard," as opposed to the
missing guard on `delta_map[v]` itself). Round 1 and round 2 did not need to
re-examine this guard because their counterexamples both operated on `v`
itself; this round traced it explicitly because the task asked for "any
other implicit assumption."

**Why it cannot fire once PF-9's gate passes:** `adjacency` and `vertices`
come from the **same graph object**, reused (not rebuilt) between PART A and
PART B, per the draft's own explicit text ("reuse the SAME p=2437 graph...
not rebuilt twice"). `build_graph_bfs` sets `adjacency[v] = sorted(nbrs)` for
every `v` it dequeues during BFS, and every neighbour `u` it discovers is
added to the same `visited` set that becomes `vertices` — so by
construction, **every vertex appearing anywhere in any `adjacency[v]` list is
itself a member of `graph["vertices"]`** (there is no external or
lazily-discovered vertex that could appear in an adjacency list without also
appearing in the vertex list). Given `new_delta_map`'s keyset equals
`graph["vertices"]` exactly (§1), and every `u` in every `adjacency[v]` is
drawn from that same vertex list, every such `u` is automatically a key in
`new_delta_map` too. The neighbour guard therefore cannot fire once the v
itself" guard passes — not coincidentally, but because `vertices` and
`adjacency` are mutually consistent by construction of the shared graph
object. No other implicit assumption was found in `local_min_and_depth`/
`depth0_fraction`: no assumption about vertex-tuple hashability beyond what
round 1's PF-7 already verified, no assumption about `adjacency`
completeness beyond what is argued above, and no assumption about graph
identity beyond what PART A's own re-stated graph-identity check (PF-8,
round 1) already covers.

## (3) Does v8 inherit v7's own null-permutation safety property via the
identical imported function, or does its different real-data source change
anything? [task question 3]

**Neither, precisely — v8 does NOT inherit it via code identity (the loop is
not imported), but it DOES inherit the safety PROPERTY, via a structural
invariant that is independent of implementation details.** This is the one
place this round's trace goes beyond what round 1/round 2 checked, because
neither needed to: both of their counterexamples were about the *first*
`depth0_fraction` call (on the real data), before any of the 1000 trials run.
Direct trace of `run_for_prime` (`delta_e_permutation_null_control_v7.py:
301-360`, imported by v7's own CLI but **not** by v8 — only `depth0_fraction`
and `summary_stats` are, per `required_artifacts_note`, confirmed by grep of
every import in the current draft text): the loop is

```python
base_values = list(delta_map.values())
for _trial in range(n_trials):
    values = list(base_values)
    rng.shuffle(values)
    permuted_map = dict(zip(vertices, values))
    stats = depth0_fraction(permuted_map, vertices, adjacency)
```

Since `v8`'s driver must write this loop itself (it is not a "genuinely
imported, unchanged" function — the draft's "run the IDENTICAL procedure...
already established" phrasing is imprecise here; see PF-12), the question is
whether an independently-written version of this loop can reopen a crash.
**It cannot, for a reason that holds regardless of implementation choices
made for v8's version specifically:** `values` is always a permutation of
`base_values`, hence always the same length as `base_values`; `zip(vertices,
values)` produces a dict with `min(len(vertices), len(values))` entries.
Once PF-9's gate has passed, `len(base_values) == len(new_delta_map) ==
len(vertices) == 203` by definition (`base_values` is derived from
`new_delta_map.values()`), so `zip` always pairs every vertex with exactly
one value and `permuted_map` always has full coverage — for **any**
implementation that (a) derives `vertices` from the same 203-vertex graph
object PART A already built and verified, and (b) derives its per-trial value
list as a permutation of `new_delta_map`'s own values. Both conditions are
what the draft's text actually requires (reusing the same graph, "the SAME
p=2437 graph... not rebuilt twice," and "using the delta_map PART A
computed"), so the safety property transfers **not because the code is
literally the same**, but because the invariant PF-9's gate establishes
(delta_map's keyset == the graph's full vertex set, exactly) is preserved by
any length-preserving shuffle-and-zip, independent of exactly how it is
coded. This is a positive, structural argument for why "1000 more independent
chances to fail" (the task's own framing) is not actually 1000 independent
opportunities for a new crash mode: they are 1000 executions of an operation
that is safe *by construction* once the one upstream precondition (the
PF-9 gate) holds, not 1000 separately-risky operations.

## (4) Any other new defect, hunted with fresh, skeptical eyes? [task
question 4]

Two low-severity, non-blocking findings, both stated above (PF-12, PF-13) and
both of the *same class* PF-9 was (an implicit-but-unstated construction
step) — the difference from PF-9 is that both are provably harmless under
the design as it now stands, not live crash risks, which is exactly why they
are advisory rather than blocking. I also traced two structural risks that
are real in principle but are **not new to v8** and are not worth blocking on:

- `find_roots_with_multiplicity` (`build_isogeny_graph.py:340-429`) has two
  `raise` conditions (an unexplained polynomial degree-deficit, and a
  "random splitting failed to terminate... after 2000 tries" case) that are
  **shared, unmodified code**, already exercised by every prior amendment in
  this lineage (BFS graph construction and the delta_E search itself, up to
  1800-vertex graphs) with zero observed incidents in this codebase's
  history. v8's RNG-design change (independent per-vertex seeds vs. one
  shared, sequentially-advancing instance) changes *which* random draws are
  consumed but not the astronomically-low failure probability of the
  splitting routine itself, so this is not a new exposure created by this
  amendment — it is a pre-existing, already-accepted risk of the shared
  search instrument, correctly out of scope for a "does v8 introduce a new
  crash path" review.
- `trapping_diagnostic_v5.build_graph_for_prime` passes
  `time_budget_seconds=900` to `build_graph_bfs`, which raises
  `TimeoutError` if exceeded. This is the identical call every amendment
  since v5 has made (same seed, same prime), and graph construction for
  p=2437 (203 vertices) is measured at ~1-2s elsewhere in this lineage
  (cited in the draft's own budget note); not a new or live risk.

## (5) Overall: is the design now safe to execute? [task question 5]

**Yes, with the two zero-cost text clarifications above applied.** The
confidence here is not "I looked and didn't find anything" — it rests on
three positive, re-derivable arguments, each closing a distinct crash
surface `depth0_fraction`'s signature actually depends on:

1. **Membership, not just count**, is guaranteed for `v` itself:
   `len(new_delta_map) == len(graph["vertices"])` cannot be satisfied except
   by exact, one-to-one vertex coverage, because `graph["vertices"]` is
   provably duplicate-free and the two construction loops are a
   deterministic partition of that exact list (§1).
2. **Membership is also guaranteed for every neighbour** of every vertex,
   not merely the vertex itself, because `adjacency` and `vertices` are
   drawn from the same, reused (not rebuilt) graph object, so every entry
   ever appearing in an adjacency list is provably a member of the vertex
   list PF-9's gate already covers (§2) — this closes a guard PF-1/PF-9's
   own counterexamples never had to exercise, because both fired on `v`
   itself first.
3. **The 1000-trial permutation loop cannot reopen either guard**, even
   though it is new code for v8 rather than literally imported, because its
   only two operations (shuffle a copy, zip onto the same vertex list) are
   length-preserving and therefore inherit full coverage automatically from
   whatever `base_values`/`vertices` state existed when the gate passed
   (§3).

Together these cover every place `depth0_fraction`/`local_min_and_depth`
touch `delta_map`, `vertices`, or `adjacency` — there is no fourth access
pattern left unexamined in that function pair. This is the basis for
"closes the crash-risk surface" rather than merely "no third path was
noticed."

---

## Objections

- **OBJ-12 [PF-9, round 2, RE-CONFIRMED with a complete positive argument]:**
  `len(new_delta_map) == len(graph["vertices"]) == 203` is both necessary
  and sufficient to prevent every existence-related crash `depth0_fraction`/
  `local_min_and_depth` can raise, given (a) `graph["vertices"]` is provably
  duplicate-free (built from a Python `set`), (b) the two construction loops
  are a deterministic partition of that exact list under a pure function
  (`is_in_fp`), and (c) every neighbour appearing in any `adjacency[v]` is,
  by BFS construction, itself a member of `graph["vertices"]`. Independently
  re-derived counts (`n_vertices=203`, `n_non_fp_rational=194`, archived
  `delta_map` length `== 203`) confirm the arithmetic this argument rests on.
- **OBJ-13 [PF-12, NEW, ADVISORY]:** PART B's 1000-trial permutation loop
  (shuffle + zip) is new code for v8, not literally imported from v7's
  `run_for_prime` (only `depth0_fraction`/`summary_stats` are imported); the
  draft's "run the IDENTICAL procedure... already established" language
  overstates code-identity for this piece. Provably harmless (the safety
  property transfers via a length-invariant independent of implementation
  detail, §3), but should be restated as an explicit step or labelled an
  "(ii) AUTHORIZED, DISCLOSED DUPLICATE," matching this file's own existing
  convention for non-importable pieces.
- **OBJ-14 [PF-13, NEW, ADVISORY, defensive]:** The new `(vertex, archived_
  value, new_value)` triples output (`probe_delta_e_comparison.json`) is the
  first vertex-identity-bearing JSON output in this lineage; as literally
  specified (a list, vertex nested as a value) it is JSON-safe natively, but
  the draft never forecloses the natural shortcut of dumping `new_delta_map`
  directly as a `{vertex: value}` dict, which would raise `TypeError` at
  write time, after all compute is spent. `compute_delta_e_v2.py`'s own
  `str(list(v))`-keyed convention already solves this and should be cited
  explicitly.
- **OBJ-1/OBJ-2/OBJ-3/OBJ-6 [rounds 1/2] — not re-litigated this round**;
  round 2 already independently re-verified all four against primary
  sources. This round adds no new information about them.

## Required controls

- Recommended before freeze, zero cost (PF-12): state the permutation-trial
  construction (`base_values = list(new_delta_map.values())`; per trial,
  shuffle a copy and `zip` onto `vertices`) explicitly as a required step, or
  label it an authorized disclosed duplicate of `run_for_prime`'s own inline
  logic, matching `delta_e_permutation_null_control_v7.py`'s own existing
  "(ii) AUTHORIZED, DISCLOSED DUPLICATES" convention.
- Recommended before freeze, zero cost (PF-13): state explicitly that any
  vertex-keyed JSON output must use the `str(list(v))`-keyed convention
  `compute_delta_e_v2.py:291-303` already established (`delta_map_json_
  safe`), and that a raw tuple must never be written as a JSON dict key.
- Neither is required to prevent a crash under the design as currently
  specified (both are defensive/precision fixes); neither blocks dispatch by
  itself.

## Counterexample or mutation

**None constructible this round for a BLOCKING finding.** I attempted the
three most promising mutation classes the task named and traced each to a
dead end:

1. *Duplicate-key mutation*: attempted to construct an input where
   `len(new_delta_map) == 203` via a duplicate write plus a missing vertex —
   structurally impossible, since `graph["vertices"]` cannot contain a
   duplicate value (Python `set`-backed construction) and both construction
   loops only ever write keys drawn from that exact list (§1).
2. *Neighbour-guard mutation*: attempted to construct an input where
   `new_delta_map` has all 203 vertex keys but a neighbour lookup still
   fails — impossible, since `adjacency` and `vertices` share the same BFS
   provenance, so every adjacency entry is guaranteed to be a vertex-list
   member, hence a `new_delta_map` key once the gate passes (§2).
3. *Permutation-trial mutation*: attempted to construct a specific
   permutation of the value multiset that produces a partial `permuted_map`
   even though the real data passed the gate — impossible, since `shuffle`
   preserves list length and `zip` onto a same-length `vertices` list always
   yields full coverage, regardless of which permutation is drawn (§3).

Each of these was the task's own suggested attack surface; none yields a
constructible crash, unlike round 1's and round 2's counterexamples, which
were directly constructible from the draft's own stated scope.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
statistical/search-procedure control work, `asymptotic_claim: null`
throughout, unchanged from rounds 1/2. The relevant baseline is this
lineage's own code-verified-crash-path standard, applied here a full level
deeper than round 2 applied it to round 1's fix: round 2 checked whether
PF-1's gate covered the vertex subset its own counterexample named; this
round checks whether PF-9's gate covers *every* access pattern
`depth0_fraction`'s actual signature touches (`delta_map[v]`,
`delta_map[u]` for every neighbour `u`, and every downstream reconstruction
of an equal-shaped `delta_map`-like object in the 1000-trial loop), not only
the specific subset PF-9's own counterexample named.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, unchanged from rounds 1/2. No numbered heuristic is
implicated; `asymptotic_claim: null` throughout.

## Cost model challenges

No change to the round-1-verified budget arithmetic (10x/12.6x margins,
2910s worst-case search bound), independently re-spot-checked this round
against the same archived figures (`wall_seconds_used=284.88387...`,
`n_non_fp_rational=194`) and found unchanged and correct. What this round
adds to the cost-model discipline: PF-9's fix, now shown to be sufficient
by a complete positive argument rather than merely unfalsified, means the
probability-of-total-loss term round 2's own cost-model challenge flagged as
"currently undefined" is now well-defined and effectively zero under the
design as specified (not merely "not yet shown to be nonzero") — the
`total expected cost = per-attempt cost × inverse success probability`
bookkeeping this campaign requires now has a success probability
argument, not just a budget-arithmetic one. PF-12/PF-13 do not change any
cost figure; both are artifact-writing/precision concerns, not
search-cost concerns.

## Reduction and scope challenges

No scheme from any affected-vs-safe list appears anywhere in this amendment;
`H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated and not
exceeded, unchanged from rounds 1/2. `OBJECTIVE_BOUNDARY` still correctly
scopes a PERSISTS result to "THIS ONE PRIME ONLY." No scope inflation found
this round either.

## Proof architecture challenges

Not applicable — direct instrument-level statistical/search-procedure
control, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited unchanged,
attacked and held, unchanged from rounds 1/2).

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v8.yaml` as it
currently stands (draft, not yet frozen, post-round-2-revision): rounds 1
and 2's three blocking findings (PF-1, PF-2, PF-9) are correctly and
consistently fixed, and PF-9's fix is now shown — by a positive,
re-derivable structural argument covering every access pattern `depth0_
fraction`/`local_min_and_depth` actually use, not merely by the absence of a
found counterexample — to be sufficient to prevent every existence-related
crash in PART B, including the "v itself," "neighbour," and "1000-trial
permutation loop" access patterns the task specifically asked this round to
check. No third blocking crash path was found after a genuine, systematic
hunt across all three of those access patterns plus the artifact-writing
surface. Two new advisory findings (PF-12, PF-13) identify text-precision
gaps of the same shape PF-9 was, but both are provably harmless under the
design as written (not live crash risks), and both are zero-additional-cost
to fix. This draft is safe to freeze once PF-12 and PF-13 are applied.

## Next concrete action

Coordinator: apply PF-12 (state the permutation-trial shuffle/zip
construction explicitly, or label it an authorized disclosed duplicate of
`run_for_prime`'s inline logic) and PF-13 (cite `compute_delta_e_v2.py`'s
`str(list(v))`-keyed JSON convention explicitly for any vertex-keyed
artifact output) in one small text-only revision pass, then freeze and
dispatch. Neither finding requires a further red-team round: both are
provably non-blocking under the design as it now stands (§3, §(4) above),
unlike PF-1/PF-9, which were shown to be live, directly-constructible
crashes before their fixes were applied. This is the first round in this
amendment's history to end without a directly constructible path to
discarding the real-compute spend.

## Overall verdict

**FREEZE-WITH-FIXES.** No new blocking finding. Rounds 1 and 2's three
blocking findings (PF-1, PF-2, PF-9) all independently re-verified holding
this round, with PF-9 specifically re-verified via a complete positive
argument (not merely re-confirmed by absence of a counterexample) covering
every access pattern `depth0_fraction`'s actual code touches — the "v
itself" guard, the "neighbour" guard, and the 1000-trial permutation loop's
own construction, the last of which neither round 1 nor round 2 needed to
trace. Two new advisory findings (PF-12, PF-13) are zero-cost text
clarifications, both shown to be non-blocking under the design as currently
specified. Apply both in the same pass as a matter of this lineage's own
explicit-construction-step discipline, then freeze and dispatch; no further
red-team round is required before that dispatch on the crash-risk grounds
this three-round sequence has been probing.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v8-round3
  task_id: TASK-20260806-0d9ec7
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v8.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: REVIEWED, round 2
    verdict DO-NOT-FREEZE with PF-9 blocking, marked FIX APPLIED in the
    current draft text) -- round 3 dedicated hunt for a THIRD independent
    path to the same catastrophic outcome (up to 3600s of real compute
    spent, PART B crashes before writing an interpretable result), given
    round 1 found PF-1 and round 2 found PF-9 as two DIFFERENT paths to that
    identical outcome.
  objections:
    - "OBJ-12 [PF-9, round 2, RE-CONFIRMED with a complete positive argument, not merely absence of a counterexample]: len(new_delta_map) == len(graph['vertices']) == 203 is both necessary and sufficient to prevent every existence-related crash depth0_fraction/local_min_and_depth can raise. Direct trace of build_graph_bfs (build_isogeny_graph.py:583-635) confirms graph['vertices'] is provably duplicate-free (built from a Python set, sorted(visited)); the two construction loops (F_p-rational wiring, non-F_p-rational search) are a deterministic partition of that exact list under is_in_fp, a pure function with no internal state; therefore len()==203 cannot be reached except by exact one-to-one vertex coverage -- there is no duplicate-overwrite or extraneous-key path. Independently re-extracted this round (not merely re-cited from round 1/2): RUN-SSIQ-a85692-b/raw-result.json's phase_minus1_real_search['2437'] entry has n_vertices=203, n_non_fp_rational=194, and its own delta_map object has exactly 203 keys, confirming 9 F_p-rational entries directly against archived data, matching compute_delta_e_v2.py:259-261's own construction."
    - "OBJ-13 [PF-12, NEW, ADVISORY]: PART B's 1000-trial permutation loop (shuffle + zip onto vertices), traced directly in delta_e_permutation_null_control_v7.py's run_for_prime (lines 301-360), is NOT literally imported by v8 -- required_artifacts_note confirms only depth0_fraction and summary_stats are genuinely imported, never run_for_prime, which is where the shuffle/zip loop actually lives. The draft's phrasing 'run the IDENTICAL procedure specification_v7.yaml already established' therefore overstates code-identity for this one piece. Provably harmless regardless: base_values is always length len(new_delta_map); shuffle preserves length; zip(vertices, values) with both operands length 203 (once PF-9's gate has passed) always yields full coverage, for any reasonable implementation of this loop, independent of exact code choices -- the safety property transfers via a structural invariant, not via code reuse. Recommend restating the construction explicitly or labelling it an '(ii) AUTHORIZED, DISCLOSED DUPLICATE' of run_for_prime's inline logic, matching this file's own existing convention for its other non-importable pieces (is_structural_local_min/depth, the coverage assertion)."
    - "OBJ-14 [PF-13, NEW, ADVISORY, defensive-only]: probe_delta_e_comparison.json's new required n_value_differs output ('the full list of (vertex, archived_value, new_value) triples') is the first vertex-identity-bearing JSON output this lineage has required beyond an aggregate count. As literally specified (a list of triples, vertex nested as a VALUE, never a dict key), this is JSON-safe natively -- Python's json module serializes a tuple exactly like a list when it appears as a value, confirmed by direct reasoning about json.dump's encoder behaviour -- so no crash is implied by the text as written. The residual, defensive-only risk: nothing in the draft forecloses an Executor's natural shortcut of also dumping new_delta_map itself directly as a {vertex: value} dict, which WOULD raise TypeError at json.dump time (dict keys must be str/int/float/bool/None, never tuple) -- after all real compute for the run is already spent. compute_delta_e_v2.py:291-303's own delta_map_json_safe = {str(list(k)): v for k, v in delta_map.items()} pattern already solves this exact problem but is never cited by v8's text for this new output shape. Recommend one sentence citing that precedent explicitly as the required convention for any vertex-keyed artifact output."
    - "OBJ-1/OBJ-2/OBJ-3/OBJ-6 [rounds 1/2, PF-1/PF-2/PF-3/PF-6]: not re-litigated this round; round 2 already independently re-verified all four against primary sources this lineage's own discipline requires. This round adds no new information about them and defers to round 2's verification."
  required_controls:
    - "PF-12 [ADVISORY, recommended before freeze, zero cost]: state the permutation-trial construction (base_values = list(new_delta_map.values()); per trial, shuffle a copy and zip onto vertices) explicitly as a required step, or label it an authorized disclosed duplicate of run_for_prime's own inline logic."
    - "PF-13 [ADVISORY, recommended before freeze, zero cost, defensive]: state explicitly that any vertex-keyed JSON output must use the str(list(v))-keyed convention compute_delta_e_v2.py already established (delta_map_json_safe), and that a raw tuple must never be written as a JSON dict key."
    - "Neither PF-12 nor PF-13 is required to prevent a crash under the design as currently specified (both are proven non-blocking, defensive/precision fixes); neither blocks dispatch by itself, unlike PF-1/PF-2/PF-9 in prior rounds."
  counterexample_or_mutation: >-
    None constructible this round for a BLOCKING finding. Three mutation
    classes were attempted, each a dead end: (1) a duplicate-key mutation
    intended to reach len(new_delta_map)==203 while missing a real vertex --
    structurally impossible given graph["vertices"]'s set-backed
    construction and the two construction loops' deterministic partition;
    (2) a neighbour-guard mutation intended to leave an adjacency-referenced
    vertex outside new_delta_map despite full coverage -- structurally
    impossible given adjacency and vertices share the same BFS provenance;
    (3) a permutation-trial mutation intended to find a specific shuffle
    outcome that produces a partial permuted_map -- structurally impossible
    given shuffle preserves length and zip onto a same-length vertices list
    always yields full coverage. All three were the task's own suggested
    attack surfaces; none yields a constructible crash.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale statistical/search-procedure control work, asymptotic_claim
    null throughout, unchanged from rounds 1/2. The relevant baseline is
    this lineage's own code-verified-crash-path standard, applied here one
    level deeper than round 2 applied it to round 1's fix: round 2 checked
    whether PF-1's gate covered the vertex subset its own counterexample
    named; this round checks whether PF-9's gate covers every access
    pattern depth0_fraction's actual signature touches (delta_map[v],
    delta_map[u] for every neighbour u, and every downstream
    reconstruction of an equal-shaped delta_map-like object in the
    1000-trial loop), not only the specific subset PF-9's own counterexample
    named.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional complexity claim) -- attacked and held, unchanged from rounds 1/2. asymptotic_claim: null throughout."
  cost_model_challenges:
    - "No change to the round-1-verified budget arithmetic (10x/12.6x margins, 2910s worst-case search bound), independently re-spot-checked this round against the same archived figures and found unchanged and correct. This round's contribution to the cost-model discipline: PF-9's fix, now shown sufficient by a complete positive argument rather than merely unfalsified, means the probability-of-total-loss term round 2's own cost-model challenge flagged as 'currently undefined' is now well-defined and effectively zero under the design as specified -- the total-expected-cost = per-attempt-cost x inverse-success-probability bookkeeping this campaign requires now rests on a success-probability ARGUMENT, not merely a budget-arithmetic one that leaves the crash-probability term unaddressed. PF-12/PF-13 do not change any cost figure; both are artifact-writing/precision concerns, not search-cost concerns."
  reduction_and_scope_challenges:
    - "No scheme from any affected-vs-safe list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded, unchanged from rounds 1/2."
    - "OBJECTIVE_BOUNDARY still correctly scopes a PERSISTS result to THIS ONE PRIME ONLY; no scope inflation found this round either."
  proof_architecture_challenges:
    - "Not applicable -- direct instrument-level statistical/search-procedure control, not a proof-oriented proposal (H-SSIQ-36e970.proof_search_map.not_applicable_reason, inherited unchanged, attacked and held, unchanged from rounds 1/2)."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v8.yaml as it
    currently stands (draft, not yet frozen, post-round-2-revision): rounds
    1 and 2's three blocking findings (PF-1, PF-2, PF-9) are correctly and
    consistently fixed, and PF-9's fix is now shown -- by a positive,
    re-derivable structural argument covering every access pattern
    depth0_fraction/local_min_and_depth actually use, not merely by the
    absence of a found counterexample -- to be sufficient to prevent every
    existence-related crash in PART B, including the "v itself," the
    "neighbour," and the "1000-trial permutation loop" access patterns this
    round was specifically asked to check. No third blocking crash path was
    found after a genuine, systematic hunt across all three of those access
    patterns plus the artifact-writing surface. Two new advisory findings
    (PF-12, PF-13) identify text-precision gaps of the same shape PF-9 was,
    but both are provably harmless under the design as written, and both
    are zero-additional-cost to fix. This draft is safe to freeze once
    PF-12 and PF-13 are applied.
  next_concrete_action: >-
    Coordinator: apply PF-12 (state the permutation-trial shuffle/zip
    construction explicitly, or label it an authorized disclosed duplicate
    of run_for_prime's inline logic) and PF-13 (cite compute_delta_e_v2.py's
    str(list(v))-keyed JSON convention explicitly for any vertex-keyed
    artifact output) in one small text-only revision pass, then freeze and
    dispatch. Neither finding requires a further red-team round: both are
    provably non-blocking under the design as it now stands, unlike
    PF-1/PF-9, which were shown to be live, directly-constructible crashes
    before their fixes were applied. This is the first round in this
    amendment's history to end without a directly constructible path to
    discarding the real-compute spend.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8-round3.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no permutation trial executed --
    this review is a specification and implementation trace, not an
    execution. Directly read this session: specification_v8.yaml in full;
    RT-PREFREEZE-EXP-SSIQ-a85692-v8.md and -round2.md in full;
    RUN-SSIQ-a85692-b/raw-result.json's phase_minus1_real_search["2437"]
    entry (independently re-extracted n_vertices, n_non_fp_rational, and
    delta_map key count via a short Python script, not merely re-read as
    prose); delta_e_permutation_null_control_v7.py in full (local_min_and_
    depth, depth0_fraction, rebuild_and_verify, run_for_prime, including
    its exact shuffle/zip permutation-trial construction); compute_delta_e_
    v2.py's real_execution_budget_v2 (F_p-rational wiring step) and
    _json_safe_phase_minus1_row/delta_map_json_safe; compute_delta_e.py's
    two_sided_search/build_smooth_table; build_isogeny_graph.py's
    Fp2Field, build_graph_bfs (vertex-set uniqueness, adjacency-vertices
    consistency), find_roots_with_multiplicity, degree_sequence_check;
    trapping_diagnostic_v5.py's build_graph_for_prime. No file written
    outside this report; no run artifact, specification file, or ledger
    record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8-round3.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v8.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
