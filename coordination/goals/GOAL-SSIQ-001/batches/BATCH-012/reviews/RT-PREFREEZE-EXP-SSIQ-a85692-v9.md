# RT-PREFREEZE-EXP-SSIQ-a85692-v9 — Round 1 pre-freeze Red Team review of
# the DRAFT amendment `specification_v9.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001
# BATCH-012, task `TASK-20260806-c88c27`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v9.yaml` at
`status: draft`, `pre_freeze_review.status: pending`, committed at `f400803d`
(a Coordinator-committed snapshot of the draft, not a frozen spec) — a
truncation-mutation control (PART A only) amending `specification_v8.yaml`
(v8, frozen `2c17b69ec52f636ce894881f9f52fd91d1bff25f`, retained unedited),
implementing the exact control `RT-BATCH-011.md`'s "Counterexample or
mutation" and "Required controls" sections named.** Per this task's operating
rules, only Coordinator-committed snapshots are treated as durable evidence;
this review is advisory pre-freeze input on a draft, not yet frozen, and
changes nothing under `experiments/EXP-SSIQ-a85692/`.

Read in full: `specification_v9.yaml` (274 lines); `specification_v8.yaml`
(687 lines, all PF-1 through PF-13 fix text and all three freeze-round
verdicts); `RT-BATCH-011.md` (full, including its "Counterexample or
mutation" section, which this amendment implements almost verbatim);
`delta_e_independent_rng_probe_v8.py` (full, 780 lines);
`compute_delta_e.py` lines 1–260 (`two_sided_search`/`build_smooth_table`);
`compute_delta_e_v2.py` lines 240–303 (`real_execution_budget_v2`'s
F_p-rational wiring and `delta_map_json_safe`); `trapping_diagnostic_v5.py`
lines 1–140 (`load_archived_prime_data`, `build_graph_for_prime`). Directly
read, not trusted from prose (all commands and outputs below are
reproducible against the committed tree): `RUN-SSIQ-a85692-h/raw-result.json`
(full top-level key list, confirmed **no** `new_delta_map` key exists
anywhere in it); `RUN-SSIQ-a85692-h/probe_delta_e_comparison.json` (full
top-level key list, confirmed `new_delta_map` exists there, is a JSON object
with `str(list(v))`-style string keys, e.g. `"[1031, 1095]"`, 203 entries);
`RUN-SSIQ-a85692-b/raw-result.json` (full top-level key list, confirmed
`phase_minus1_real_search` exists and is the schema
`trapping_diagnostic_v5.load_archived_prime_data` is hard-wired to);
`RUN-SSIQ-a85692-h/probe_delta_e_comparison.json`'s `per_vertex_records`
(194 entries, `wall_seconds` min 1.1499s / max 1.6985s, matching v9's own
cited figures exactly).

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
    itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**DO NOT FREEZE. One blocking defect, code-verified against the actual
committed run artifacts (not merely against spec prose): REQUIRED COMPARISON
2 — v9's own stated headline differentiator over v8's own review, "a SECOND,
ZERO-EXTRA-COST comparison" — as currently specified either crashes before
any artifact is written, or (if an Executor works around the crash with an
untyped comparison) silently produces a vacuous, misleadingly-clean result,
because the source file and key format the spec names do not match what the
Executor would actually need to read and parse.** Everything else in this
draft is sound: the seed-isolation argument that truncation is the sole
manipulated variable is correct (traced to the underlying determinism
mechanism, not merely asserted); the 97.0s worst-case arithmetic and the
600s/6.19x budget margin are both independently re-verified correct; PART A's
own comparison logic (unlike v8's original PART B) does not assume full
coverage and cannot reproduce PF-1/PF-9's crash shape; and the
`OBJECTIVE_BOUNDARY` scoping is clean. Three further advisory findings (two
arithmetic-citation errors in the budget-justification prose, and one
reproducibility caveat on the seed-isolation argument) do not block freeze
but should be fixed in the same pass.

1. **PF-1 [BLOCKING] — REQUIRED COMPARISON 2's named source file and key
   format do not match what actually exists in `RUN-SSIQ-a85692-h`'s
   artifacts; a literal implementation crashes or silently fabricates a
   vacuous result.** See §1 below. Directly confirmed by loading both files:
   `RUN-SSIQ-a85692-h/raw-result.json` has **no** `new_delta_map` key at any
   level (its 24 top-level keys are listed in §1); only
   `probe_delta_e_comparison.json` has it, and there its keys are JSON
   strings (`"[1031, 1095]"`), not vertex tuples. The one genuinely-imported
   function that performs the required string-to-tuple round-trip
   (`trapping_diagnostic_v5.load_archived_prime_data`) is hard-wired to a
   **different** JSON schema (`data["phase_minus1_real_search"][str(prime)]
   ["delta_map"]`, confirmed present in `RUN-SSIQ-a85692-b`'s file) that does
   not exist anywhere in `RUN-SSIQ-a85692-h`'s files (confirmed absent) —
   calling it against `RUN-SSIQ-a85692-h`'s file raises `KeyError:
   'phase_minus1_real_search'`. `required_artifacts_note` discloses no
   substitute helper for this second, structurally different parse. This is
   the identical failure shape this lineage has hit four times before
   (GD-4/7/9/10, and v8's own PF-1/PF-9): a required step described in prose
   with no corresponding, disclosed, code-verified implementation path.

2. **The truncation-isolates-the-sole-variable design reasoning is sound —
   traced to the mechanism, not merely asserted.** `derive_per_vertex_seed`
   depends only on `(base_seed, vertex)`, never on
   `per_vertex_budget_seconds` (direct read, confirmed). Given the identical
   seed, `build_smooth_table`'s only source of non-determinism
   (`find_roots_with_multiplicity`'s internal polynomial-splitting draws) and
   its heap tie-breaking (on `(degree, vertex-tuple)`, never on RNG or hash
   order) mean the sequence of table-expansion steps for a given vertex is a
   **deterministic prefix** of what a larger-budget run would compute — the
   `time.time() - t0 > time_budget_seconds` check
   (`compute_delta_e.py:156-159`) only ever truncates that prefix early,
   never alters it. This is a correct, re-derivable argument, not an
   assumption (see §2).

3. **PF-2 [ADVISORY] — two decorative "Nx smaller" figures in the budget
   justification are arithmetically wrong**, though the safety-critical
   margin they sit next to (600s budget vs. 97.0s worst case, 6.19x) is
   independently re-verified correct. See §3.

4. **PF-3 [ADVISORY] — the seed-isolation argument (finding 2 above) is sound
   in *content* but not perfectly reproducible run-to-run in exactly *which*
   vertices land on which side of the 0.5s cutoff**, since real wall-clock
   truncation depends on machine speed/load, not only the seed. Worth a
   one-sentence caveat, not a design defect.

5. **PF-4 [ADVISORY, minor] — the 0.5s per-vertex budget is a soft, not
   hard, cap**: the timeout check fires only between heap-pop iterations, so
   a single expensive `phi_ell` evaluation could in principle push one
   vertex's wall time somewhat past 0.5s. No per-call timing data exists in
   this lineage's own artifacts to bound the magnitude, but the aggregate
   600s/97.0s margin almost certainly absorbs it.

6. **PART A's own comparison design correctly avoids the full-coverage
   assumption that produced v8's PF-1/PF-9 crashes.** Unlike v8's PART B
   (which iterated all 203 vertices via `depth0_fraction`, requiring a
   coverage gate), v9's two comparisons only ever iterate vertices *actually
   resolved this run* (a subset of at most 194), checked against sources with
   guaranteed full coverage — this is a genuine, credit-worthy design
   improvement, and I found no path by which partial coverage on v9's own
   side causes a crash. PF-1 above is a different bug (wrong source file/key
   type for Comparison 2), not a coverage-assumption bug.

Given PF-1 is a real, code-verified, non-hypothetical defect in the one part
of this amendment that is genuinely novel relative to v8's own already-
reviewed pattern (Comparison 1 is a straightforward re-application of v8's
already-safe pattern; Comparison 2 is new), my verdict is **DO-NOT-FREEZE**.
The fix is textual only (no design change, no new compute), so I expect this
to be a short second round.

---

## (1) PF-1 — does REQUIRED COMPARISON 2 actually work against the real
artifacts it names? [task question: crash paths / required-artifacts
accuracy]

**No, not as currently specified — demonstrated directly against the
committed files, not inferred from prose.**

```
$ python3 -c "
import json
d = json.load(open('experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/raw-result.json'))
print(sorted(d.keys()))
print('new_delta_map' in d)"
['artifact_references', 'base_seed', 'certificate', 'comparison_against_archived_summary',
 'coverage_gate', 'experiment_id', 'finished_utc', 'git', 'graph_identity_failed_halt',
 'graph_identity_verification', 'graph_seed', 'n_trials', 'objective_boundary',
 'part_a_summary', 'part_b_outcome', 'part_b_summary', 'per_vertex_budget_seconds',
 'permutation_seed', 'platform', 'prime', 'python', 'run_id', 'scale_qualifier',
 'spec_version', 'started_utc', 'wall_clock_seconds']
False
```

`RUN-SSIQ-a85692-h/raw-result.json` has **no `new_delta_map` field at any
level** — confirmed by direct read of every top-level key. v9's text says
"load RUN-SSIQ-a85692-h's own raw-result.json **or**
probe_delta_e_comparison.json new_delta_map field," which is simply
inaccurate for the first alternative; only the second file has it:

```
$ python3 -c "
import json
d = json.load(open('experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json'))
print('new_delta_map' in d, len(d['new_delta_map']))
print(list(d['new_delta_map'].items())[:3])"
True 203
[('[1031, 1095]', 5), ('[1031, 1342]', 5), ('[1036, 1974]', 5)]
```

Its keys are `str(list(v))`-serialized JSON strings (PF-13's own write
convention, correctly applied by v8), **not** vertex tuples. v9's own
tuple-keyed resolved-vertex set cannot be compared against this dict without
first parsing every key back via `tuple(json.loads(key))` — the exact
round-trip `trapping_diagnostic_v5.load_archived_prime_data` already
implements (direct read, `trapping_diagnostic_v5.py:102-130`), but that
function is hard-wired to a **structurally different** source schema:

```python
entry = data["phase_minus1_real_search"][str(prime)]
raw_delta_map = entry["delta_map"]
```

`RUN-SSIQ-a85692-b/raw-result.json` (Comparison 1's target) genuinely has
this `phase_minus1_real_search` key (confirmed: `'phase_minus1_real_search'
in d` is `True`, with `'2437'` present among its sub-keys). `RUN-SSIQ-a85692-
h`'s files (Comparison 2's target) have **neither** `phase_minus1_real_
search` **nor** a nested `delta_map` under any such key — its `new_delta_map`
lives at the top level of `probe_delta_e_comparison.json` directly. Calling
`load_archived_prime_data` against `RUN-SSIQ-a85692-h`'s file — the most
natural reading of "reuse the same genuinely-imported function" a
good-faith Executor following this lineage's own reuse discipline would
attempt — raises `KeyError: 'phase_minus1_real_search'` immediately.

This produces one of two failure modes, both live:

- **Crash before any artifact is written.** If, per this amendment's own
  structure (mirroring v8's `main()`, which computes both comparisons
  in-memory before a single combined `raw-result.json`/
  `truncation_probe_comparison.json` write at the end), Comparison 2 is
  attempted before final artifacts are serialized, an uncaught `KeyError`
  here discards not just Comparison 2 but **also** Comparison 1's valid
  result and PART A's own core measurement (`n_resolved`, `n_timed_out`,
  `coverage_fraction`) — the actual deliverable this amendment exists to
  produce, per its own purpose statement. This reproduces the exact
  catastrophic shape of v8's PF-1/PF-9 (real compute spent, zero
  interpretable result), just at a smaller compute scale (97s, not 2910s).
- **Silent, vacuous, misleadingly-clean result.** If instead an Executor
  works around the schema mismatch by writing new, ad-hoc code that reads
  `probe_delta_e_comparison.json`'s `new_delta_map` directly and compares it
  against v9's own tuple-keyed resolved vertices **without** the
  `tuple(json.loads(key))` conversion (e.g. `if v in v8_new_delta_map` where
  `v` is a tuple and `v8_new_delta_map`'s keys are all strings), every
  membership test evaluates `False` — no exception, no crash, just
  `n_this_run_resolved > 0` with `n_value_matches_vs_v8 == 0` and
  `n_value_differs_vs_v8 == 0` (or every comparison landing in a
  "not-found" bucket, depending on exact code), for **every** vertex,
  regardless of the true relationship between this run's values and v8's.
  Given v9's own framing — "ANY value difference here is attributable
  SOLELY to the smaller search budget… a genuinely different diagnostic axis
  than Comparison 1" — a reviewer reading `n_value_differs_vs_v8 = 0`
  post-hoc, without independently re-deriving the key-parsing bug, would
  have no way to distinguish "truncation genuinely never changes the value"
  from "the comparison never matched a single key." This is a worse failure
  than a crash: it produces a plausible-looking, fully-written artifact that
  is silently wrong.

`required_artifacts_note`'s "GENUINELY IMPORTS, UNCHANGED" list names
`trapping_diagnostic_v5.load_archived_prime_data` once, for Comparison 1
(where it is correctly applicable — `RUN-SSIQ-a85692-b`'s file has the right
schema), but discloses **no** helper, imported or new, for Comparison 2's
distinct parsing need. Per this campaign's own GD-9/GD-10 discipline (a
control/wrapper's citation in prose does not establish that its comparison
logic was actually implemented against the *right* data; the same
direct-code-reading standard applies recursively to a fix's own fix), this
is exactly the class of gap that standing repair exists to catch.

**Required fix (textual only, zero new compute):**
1. Correct "raw-result.json or probe_delta_e_comparison.json" to name only
   `probe_delta_e_comparison.json` (the only file with `new_delta_map`).
2. Explicitly require the `tuple(json.loads(key))` round-trip — the
   identical convention `trapping_diagnostic_v5.load_archived_prime_data`
   already establishes — be applied to `probe_delta_e_comparison.json`'s
   `new_delta_map` field directly, disclosed as a small, new "(ii)
   AUTHORIZED, DISCLOSED DUPLICATE" parsing helper in `required_artifacts_
   note` (since `load_archived_prime_data` itself cannot be pointed at this
   file — different schema), matching this file's own established
   disclosure convention for non-importable pieces.
3. State the same collision/injectivity check `load_archived_prime_data`
   itself performs (`len(delta_map) != len(raw_delta_map)` → raise) for this
   new parse, so a future schema drift fails loudly rather than silently.

## (2) Is the seed-isolation ("sole manipulated variable") reasoning actually
sound? [task question 2]

**Yes, on direct trace of the mechanism, not merely on the design's own
prose.** `derive_per_vertex_seed(base_seed, vertex)`
(`delta_e_independent_rng_probe_v8.py:151-154`) is a pure function of
`(base_seed, vertex)` — no reference to `per_vertex_budget_seconds` anywhere
in its body or signature. Given the identical seed, `rng_v`'s draw sequence
is byte-for-byte identical between a 0.5s and a 15.0s run of the same
vertex. `build_smooth_table`'s only other source of variability is wall-clock
timing itself, checked only at the *top* of the while loop
(`compute_delta_e.py:155-159`), between `heapq.heappop` calls — never inside
a single `neighbors_ell_isogenous` evaluation. Heap ordering breaks ties on
`(degree, vertex-tuple)` comparison, a pure, deterministic function with no
dependence on Python's hash-randomization or dict-iteration order (vertices
are plain `(int, int)` tuples). So, for a fixed seed and a fixed source/
target pair, the *sequence* of `(degree, j)` pops, `phi_ell` calls, and root
discoveries up to any given point in wall-clock time is identical between
any two runs regardless of budget — a smaller budget only truncates this
identical sequence earlier. This is precisely what v9's amendment_scope
claims ("holding the per-vertex RNG stream IDENTICAL... isolates
budget-truncation as the SOLE manipulated variable"), and the claim survives
direct code trace, not just restatement.

**PF-3 caveat (advisory, not blocking):** the argument above establishes that
the *computation content* up to truncation is a deterministic prefix, but
*where* the 0.5s wall-clock cutoff actually lands (which vertex, at what
point in its table-build) depends on real machine speed/load, which is not
controlled or pinned by this amendment the way `BASE_SEED`/`GRAPH_SEED`/
`PERMUTATION_SEED` are. A re-run of this exact amendment on different
hardware could produce a different `n_resolved`/`n_timed_out` split even
with byte-identical RNG draws — worth one disclosed sentence, since v8's own
15.0s run (8x margin over the ~1.7s slowest vertex) was effectively immune to
this, and v9 is deliberately operating in the regime where it is not.

## (3) Budget correctness [task question 3]

**Independently re-verified, all core arithmetic correct; two decorative
citations are wrong.**

- `194 * 0.5 = 97.0` — correct.
- `600 / 97.0 = 6.186...` ≈ "~6.2x that worst-case bound" — correct, and this
  is the figure that actually matters for dispatch safety (a comfortable,
  not silently tight, margin).
- `2910 / 97.0 = 30.0` exactly — "roughly 30x SMALLER than v8's own
  worst-case 2910s bound" — correct, appears twice (amendment_scope and
  budget.note), both correct.
- **PF-2 [ADVISORY]:** amendment_scope's "roughly 37x smaller than v8's own
  actual measured PART A time (277.85s at 15.0s/vertex)" is wrong:
  `277.85 / 97.0 = 2.864`, not 37. budget.note's parallel claim, "6x smaller
  than v8's own actual measured wall-clock (278.5s)," is also wrong by the
  same reading: `278.5 / 97.0 = 2.87`, not 6 — though `3600 / 600 = 6.0`
  exactly, suggesting the "6x" figure was actually computed from v8's own
  **total budget** (3600s) against v9's **total budget** (600s), then
  mislabeled with v8's *actual measured* wall-clock (278.5s) instead.
  Neither error affects the safety-critical 600s-vs-97.0s margin (correctly
  stated elsewhere and independently re-verified above), so this is not
  blocking — but both are factual numeric claims in a to-be-frozen research
  record and should be corrected (either fix the arithmetic to ~2.9x, or
  drop the comparison) per this campaign's own numeric-honesty discipline.
  `total_cpu_hours: 0.2` (720s) is looser than `wall_clock_seconds_per_run:
  600`, consistent for a single-threaded process (CPU time ≈ wall time here);
  no contradiction.
- **PF-4 [ADVISORY, minor]:** the 0.5s per-vertex budget is a *soft* cap
  (timeout checked only between heap-pop iterations, `compute_delta_e.py:
  155-159`), not a hard one — a single expensive `phi_ell` call could push
  one vertex's wall time somewhat past 0.5s. No `per_vertex_records` field in
  this lineage (checked: no `phi_calls_total` or per-call timing is
  persisted) bounds the magnitude of a plausible single-call duration
  directly; it can only be inferred from v8's own aggregate 1.15-1.70s-per-
  vertex figures for a *full* multi-call table build. Given the 6.19x
  aggregate margin, this is very unlikely to threaten the 600s wall-clock
  cap even under several such overshoots, but is worth naming since it is
  the identical mechanism v8 relied on at 15.0s (where an 8x margin made it
  moot) now operating with less headroom.

## (4) Required-artifacts / import-list accuracy [task question 4]

Covered substantively in §1 (PF-1): the accuracy gap **is** the missing
disclosure of Comparison 2's real parsing requirement. Everything else in
`required_artifacts_note`'s diff list checks out on direct trace:
`compute_delta_e.two_sided_search`/`L_PRIMES`/`X_LIST_BOUND` are genuinely
importable and match the described call signature exactly (confirmed against
`compute_delta_e.py:177-210`); `trapping_diagnostic_v5.build_graph_for_prime`
and `.load_archived_prime_data` are genuinely importable (the latter correct
**only** for Comparison 1's target, per §1);
`delta_e_independent_rng_probe_v8.derive_per_vertex_seed` and
`.verify_graph_identity` are genuinely importable, and I confirmed both by
direct read: `derive_per_vertex_seed(base_seed, vertex)` matches v9's cited
formula exactly (`delta_e_independent_rng_probe_v8.py:151-154`), and
`verify_graph_identity(g, archived_n_vertices=ARCHIVED_N_VERTICES)`
(`.py:164-175`) genuinely "takes the graph and an expected count as
parameters, is not hardwired to any spec version," exactly as v9 claims.
Importing `delta_e_independent_rng_probe_v8` as a module has no observable
side effect at import time (confirmed: its only top-level executable
statements are constant assignments and function/class definitions; all
"real" work is under `if __name__ == "__main__":`, `.py:778-780`) — safe to
import for these two functions alone. `build_isogeny_graph.degree_sequence_
check` is correctly disclosed as reached only via `verify_graph_identity`'s
own internal `big` reference, not re-imported directly — correct, since
Python module-level imports are shared references, not copies.
`required_artifacts_note` correctly and explicitly excludes PART B's driver
functions and `run_phase_minus1_on_confirmatory_set`/`real_execution_budget_
v2`, consistent with the "PART A ONLY, no PART B" scope. The one gap is
exactly the one identified in §1.

## (5) Scope discipline [task question 5]

**Clean.** `OBJECTIVE_BOUNDARY` (lines 200-212) states this is "a DIAGNOSTIC
CONTROL testing the BOUNDARY CONDITION of BATCH-011's own determinism
argument... NOT a test of H-SSIQ-36e970's real-arm prediction," explicitly
does not produce a PERSISTS/WEAKENS label ("that vocabulary belongs to v8's
PART B, not run by this amendment"), and is explicitly "Scoped to p=2437
ONLY; no claim about the other three primes or any scale beyond this toy
instance." No affected/safe cryptographic scheme list appears anywhere; no
extension to lever L4 is claimed or implied. This matches the frozen v8
lineage's own established scoping discipline and I found no inflation.

## (6) Any other defect, fresh skeptical read [task question 6]

No further blocking defect found. Two smaller observations, both already
folded into PF-2/PF-3/PF-4 above, plus one positive note (finding 6 in the
bottom line): PART A's own comparison logic (both Comparison 1 and, once
PF-1 is fixed, Comparison 2) is structured around "vertices resolved in THIS
run" as the iteration domain, which — unlike v8's original PART B — cannot
reproduce the PF-1/PF-9 "blind full-coverage assumption" crash shape,
because it never assumes the *target* map (archived or v8's) has an entry
for every vertex it looks up beyond what that target's own known 100%
coverage already guarantees. This is a genuine, credit-worthy design
improvement directly responsive to RT-BATCH-011's own critique, and the
correct thing to preserve when PF-1's fix is applied — the fix should be a
parsing correction, not a change to this safe iteration-domain design.

---

## Objections

- **OBJ-1 [PF-1, BLOCKING]**: `probe_delta_e_comparison.json` new_delta_map`
  (the source REQUIRED COMPARISON 2 needs) does not exist in
  `raw-result.json` at all (confirmed by direct read of all 24 top-level
  keys) and is string-keyed (`str(list(v))`), not tuple-keyed, in the file
  where it does exist. The one genuinely-imported function that performs the
  needed string-to-tuple round-trip, `trapping_diagnostic_v5.load_archived_
  prime_data`, is hard-wired to a schema (`data["phase_minus1_real_search"]
  [str(prime)]["delta_map"]`) that exists in `RUN-SSIQ-a85692-b`'s file but
  not in `RUN-SSIQ-a85692-h`'s (confirmed absent). A literal implementation
  either crashes with `KeyError` (if it reuses `load_archived_prime_data`
  against the wrong file, plausibly before any artifact is written, risking
  the entire run's real-compute spend) or silently produces a vacuous
  all-zero comparison (if it compares un-converted string keys against
  tuple keys). `required_artifacts_note` discloses no substitute parsing
  helper for this need.
- **OBJ-2 [advisory]**: the seed-isolation ("sole manipulated variable")
  design reasoning is sound on direct mechanism trace (§2) — no objection to
  the core design — but not perfectly run-to-run reproducible in which
  vertices land on which side of the cutoff, since real wall-clock timing,
  not just the pinned seed, determines truncation point (PF-3).
- **OBJ-3 [PF-2, advisory]**: two "Nx smaller" decorative comparisons in the
  budget-justification prose are arithmetically wrong (should be ≈2.9x, not
  37x or 6x); the safety-critical 6.19x margin figure they sit beside is
  independently re-verified correct and unaffected.
- **OBJ-4 [PF-4, advisory, minor]**: the 0.5s per-vertex budget is a soft
  cap (checked only between heap-pop iterations), not a hard one; no direct
  per-call timing data in this lineage bounds worst-case single-call
  overshoot, though the aggregate 6.19x margin makes this very unlikely to
  matter.

## Required controls

- **[PF-1, BLOCKING, required before freeze, zero new compute]**: correct
  REQUIRED COMPARISON 2's source-file citation to `probe_delta_e_comparison.
  json` only, and add an explicit, disclosed `tuple(json.loads(key))`
  parsing step (with the same collision/injectivity check `load_archived_
  prime_data` itself performs) applied to that file's `new_delta_map` field,
  listed as a new small "(ii) AUTHORIZED, DISCLOSED DUPLICATE" helper in
  `required_artifacts_note`.
- **[PF-2, advisory, recommended before freeze, zero cost]**: fix or drop
  the two wrong "37x"/"6x" decorative wall-clock comparisons in the budget
  justification text.
- **[PF-3, advisory, recommended, zero cost]**: add one sentence disclosing
  that exact per-vertex resolved/timed-out counts under a 0.5s budget are
  not bit-for-bit reproducible across different hardware, unlike v8's 15.0s
  (8x-margin) run.
- **[PF-4, advisory, optional]**: note the per-vertex budget is a soft, not
  hard, cap, consistent with v8's identical mechanism at a larger margin.
- None of PF-2/PF-3/PF-4 blocks dispatch by itself; PF-1 does.

## Counterexample or mutation

**Already directly demonstrated, not hypothetical** (see §1's reproduced
commands): loading `RUN-SSIQ-a85692-h/raw-result.json` and checking for
`new_delta_map` returns `False`; loading `RUN-SSIQ-a85692-h/probe_delta_e_
comparison.json`'s `new_delta_map` shows string keys (`"[1031, 1095]"`), not
tuples; loading `RUN-SSIQ-a85692-b/raw-result.json` confirms it (and only it)
has the `phase_minus1_real_search` schema `load_archived_prime_data`
requires. The cheapest concrete demonstration that this is a live, not
merely theoretical, defect: attempt `tdv5.load_archived_prime_data(path_to_
RUN-SSIQ-a85692-h_probe_delta_e_comparison.json, 2437)` directly against the
committed file — it raises `KeyError: 'phase_minus1_real_search'`
immediately, reproducible by any reader with the committed tree.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
search-procedure diagnostic work, `H-SSIQ-36e970.asymptotic_claim: null`
throughout, correctly inherited and unchanged by this amendment. The relevant
baseline is this lineage's own code-verified-crash-path and GD-9/GD-10
required-artifacts-accuracy standard: PF-1 is exactly the shape those
standing repairs exist to catch — a required step named in prose without a
disclosed, schema-checked implementation path — applied here to a comparison
that is genuinely new relative to v8's already-reviewed pattern (Comparison
1 is a straightforward re-application of v8's own already-safe pattern and
required no new scrutiny beyond confirming it inherits the safe iteration-
domain design; Comparison 2 is the one place this amendment is not merely
reusing already-audited machinery).

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty — a
gradient-existence/search-procedure diagnostic, not a heuristic-conditional
asymptotic-complexity claim; nothing in this amendment changes that.
`asymptotic_claim: null` throughout. No numbered heuristic is implicated.

## Cost model challenges

No asymptotic-cost claim is made anywhere in this amendment. The
safety-critical budget arithmetic (`194 * 0.5 = 97.0`; `600 / 97.0 ≈ 6.19x`
margin) is independently re-verified correct (§3). Two decorative
"Nx smaller than v8" comparisons are arithmetically wrong (PF-2, §3) but do
not affect the actual margin. No `total expected cost = per-attempt cost ×
inverse success probability` computation is needed or attempted here — this
is a bounded, single-run, non-probabilistic-success diagnostic (the "success"
condition is simply completing and writing an honest report, not a
probabilistic solve), consistent with v8's own prior cost-model framing at
this scale.

## Reduction and scope challenges

No affected/safe cryptographic scheme list appears anywhere in this
amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated
and not exceeded. `OBJECTIVE_BOUNDARY` explicitly restricts this amendment's
result to "purely descriptive," explicitly excludes any PERSISTS/WEAKENS
label, `H-SSIQ-36e970`'s real-arm prediction, and lever L4, and is explicitly
scoped to p=2437 alone — verified by direct read (§5), not merely trusted
from prose. No scope inflation found.

## Proof architecture challenges

Not applicable — `H-SSIQ-36e970.proof_search_map.not_applicable_reason`
remains correctly reasoned and inherited unchanged; this is a direct
instrument-level search-procedure diagnostic, not a proof-oriented proposal.
Attacked and held, unchanged from v8's own review history.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v9.yaml` as committed
at `f400803d` (draft, status `draft`, `pre_freeze_review.status: pending`):
the core experimental design (isolate budget-truncation as the sole
manipulated variable by reusing v8's exact `BASE_SEED` and per-vertex seed
formula) is sound, re-derived from direct code trace, not merely restated
from the draft's own prose (§2); the 97.0s worst-case bound and the 600s/
6.19x total budget margin are both independently re-verified correct (§3);
`OBJECTIVE_BOUNDARY` scoping is clean (§5); PART A's comparison design
correctly avoids the full-coverage-assumption crash shape that produced v8's
PF-1/PF-9 (§6). One blocking defect is directly demonstrated, not merely
hypothesized: REQUIRED COMPARISON 2's named source file
(`raw-result.json`, which lacks `new_delta_map` entirely) and its
key-parsing requirement (a `tuple(json.loads(key))` round-trip the one
genuinely-imported candidate function, `load_archived_prime_data`, cannot
perform against `RUN-SSIQ-a85692-h`'s differently-schemaed file) are both
wrong as specified, creating a live crash-before-any-artifact-is-written path
and a live silent-vacuous-comparison path, either of which would undermine
or entirely discard this amendment's real, if small, compute spend. This
draft is **not** safe to freeze until PF-1 is fixed; PF-2/PF-3/PF-4 should be
applied in the same pass but do not independently block freeze.

## Next concrete action

Coordinator: apply PF-1's required fix (correct REQUIRED COMPARISON 2's
source-file citation to `probe_delta_e_comparison.json` only; add an
explicit, disclosed `tuple(json.loads(key))` parsing step with a collision
check, listed as a new small authorized-duplicate helper in `required_
artifacts_note`) — this is a textual-only change, zero new compute — then
apply PF-2/PF-3/PF-4 in the same pass (fix or drop the two wrong "Nx
smaller" figures; add the reproducibility caveat; note the soft per-vertex
cap), and request a second, focused pre-freeze round scoped specifically to
re-verifying PF-1's fix against the actual committed `RUN-SSIQ-a85692-h`
files (not merely against the corrected prose) before freezing and
dispatching. Given the amendment's real compute is small (97.0s worst case),
this should be a short round.

## Overall verdict

**DO-NOT-FREEZE.** One blocking finding (PF-1), directly demonstrated
against the actual committed run artifacts this amendment depends on, not
merely inferred from spec prose: REQUIRED COMPARISON 2's named source file
does not contain the field it claims, and the field's actual location uses a
key format the one genuinely-imported parsing function cannot handle for
that file's schema — creating a live crash-before-artifact-write path and a
live silent-vacuous-result path. Everything else in this draft — the core
truncation-isolation design, the budget arithmetic's safety-critical figures,
the scope discipline, and PART A's crash-safe comparison-domain design — is
sound. The fix is textual only; no design change and no new compute is
required. Expect a short second round scoped to re-verifying PF-1's fix
against the real artifact schemas.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v9
  task_id: TASK-20260806-c88c27
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v9.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: pending), committed
    at f400803d -- a single-part (PART A only) truncation-mutation control
    amending the frozen specification_v8.yaml (frozen
    2c17b69ec52f636ce894881f9f52fd91d1bff25f), implementing RT-BATCH-011's
    own named counterexample: rerun v8's per-vertex-independent-RNG delta_E
    search design at p=2437 with PER_VERTEX_BUDGET_SECONDS cut from 15.0s to
    0.5s (well below the observed ~1.15-1.70s completion range), forcing
    genuine truncation, to test whether v8's own "0/203 value differences"
    result reflects a real determinism property or a near-guaranteed
    non-informative outcome. Round 1 pre-freeze review, first round for this
    amendment.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: REQUIRED COMPARISON 2's named source file (raw-result.json) does not contain new_delta_map at all -- confirmed by direct read of all 24 top-level keys of RUN-SSIQ-a85692-h/raw-result.json, none of which is new_delta_map. The field exists only in probe_delta_e_comparison.json, string-keyed via str(list(v)) (e.g. '[1031, 1095]'), not tuple-keyed. The one genuinely-imported function that performs the needed tuple(json.loads(key)) round-trip, trapping_diagnostic_v5.load_archived_prime_data, is hard-wired to data['phase_minus1_real_search'][str(prime)]['delta_map'] -- confirmed present in RUN-SSIQ-a85692-b/raw-result.json but confirmed absent from every RUN-SSIQ-a85692-h file. Calling load_archived_prime_data against RUN-SSIQ-a85692-h's file raises KeyError: 'phase_minus1_real_search' immediately. required_artifacts_note discloses no substitute parsing helper. A literal implementation either crashes before any artifact is written (discarding the run's real compute and PART A's own core measurement along with Comparison 2) or, if worked around with an untyped comparison, silently produces a vacuous all-zero-matches result for Comparison 2 -- v9's own stated headline differentiator over v8's review -- indistinguishable in the written artifact from a genuine truncation-has-no-effect finding."
    - "OBJ-2 [advisory, not blocking]: the seed-isolation ('sole manipulated variable') reasoning is sound on direct mechanism trace -- derive_per_vertex_seed depends only on (base_seed, vertex), never on per_vertex_budget_seconds (confirmed, delta_e_independent_rng_probe_v8.py:151-154); build_smooth_table's timeout check fires only between heap-pop iterations (compute_delta_e.py:155-159), never mid-call, and heap tie-breaking is a pure function of (degree, vertex-tuple), never RNG or hash order -- so a smaller budget truncates an identical computation prefix, not a different one. Caveat (PF-3): exactly which vertices land on which side of the 0.5s cutoff depends on real wall-clock timing (machine speed/load), not only the pinned seed, so exact per-vertex resolved/timed-out counts are not bit-for-bit reproducible across hardware the way v8's 8x-margin 15.0s run effectively was."
    - "OBJ-3 [PF-2, advisory]: two decorative wall-clock comparisons in the budget-justification prose are arithmetically wrong -- amendment_scope's '37x smaller than v8's own actual measured PART A time (277.85s)' should be ~2.86x (277.85/97.0); budget.note's '6x smaller than v8's own actual measured wall-clock (278.5s)' should be ~2.87x (278.5/97.0), though 3600/600=6.0 exactly suggests the figure was actually computed from v8's total BUDGET (3600s) vs v9's total budget (600s) and mislabeled with v8's actual measured wall-clock instead. The safety-critical 600s/97.0s (~6.19x) margin these sit beside is independently re-verified correct and unaffected by either error."
    - "OBJ-4 [PF-4, advisory, minor]: the 0.5s per-vertex budget is a soft cap (checked only between heap-pop iterations, compute_delta_e.py:155-159), not a hard one -- a single expensive phi_ell evaluation could in principle push one vertex's wall time somewhat past 0.5s. No per-call timing data exists in this lineage's own artifacts (per_vertex_records carries no phi_calls_total or per-call breakdown) to bound the magnitude directly; inferred only from v8's own aggregate 1.15-1.70s full-table-build figures. The 6.19x aggregate margin makes this very unlikely to threaten the 600s wall-clock cap."
  required_controls:
    - "[PF-1, BLOCKING, required before freeze, zero new compute]: correct REQUIRED COMPARISON 2's source-file citation to probe_delta_e_comparison.json only (not raw-result.json), and add an explicit, disclosed tuple(json.loads(key)) parsing step -- with the same collision/injectivity check load_archived_prime_data itself performs -- applied to that file's new_delta_map field, listed as a new small '(ii) AUTHORIZED, DISCLOSED DUPLICATE' helper in required_artifacts_note (load_archived_prime_data itself cannot be reused for this file -- different schema)."
    - "[PF-2, advisory]: fix or drop the two wrong '37x'/'6x' decorative wall-clock comparisons in the budget justification text (correct figure ~2.9x for both)."
    - "[PF-3, advisory]: add one sentence disclosing that exact per-vertex resolved/timed-out counts under a 0.5s budget are not bit-for-bit reproducible across different hardware."
    - "[PF-4, advisory, optional]: note the per-vertex budget is a soft, not hard, cap, consistent with v8's identical mechanism at a larger margin."
  counterexample_or_mutation: >-
    Already directly demonstrated, not hypothetical: loading
    RUN-SSIQ-a85692-h/raw-result.json and checking for new_delta_map returns
    False (confirmed against all 24 top-level keys); loading
    RUN-SSIQ-a85692-h/probe_delta_e_comparison.json's new_delta_map shows
    string keys ("[1031, 1095]"), not vertex tuples; loading
    RUN-SSIQ-a85692-b/raw-result.json confirms it (and only it) has the
    phase_minus1_real_search schema trapping_diagnostic_v5.
    load_archived_prime_data requires. Directly attempting
    load_archived_prime_data against RUN-SSIQ-a85692-h's file raises
    KeyError: 'phase_minus1_real_search' immediately, reproducible by any
    reader against the committed tree.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale search-procedure diagnostic work, H-SSIQ-36e970.asymptotic_claim
    null throughout, correctly inherited and unchanged. The relevant baseline
    is this lineage's own code-verified-crash-path and GD-9/GD-10
    required-artifacts-accuracy standard: PF-1 is exactly the shape those
    standing repairs exist to catch -- a required step named in prose without
    a disclosed, schema-checked implementation path -- applied here to the
    one comparison genuinely new relative to v8's already-reviewed pattern
    (Comparison 1 is a safe, direct re-application of v8's own already-audited
    pattern; Comparison 2 is not).
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty -- a gradient-existence/search-procedure diagnostic, not a heuristic-conditional asymptotic-complexity claim; nothing in this amendment changes that. asymptotic_claim: null throughout. No numbered heuristic implicated."
  cost_model_challenges:
    - "No asymptotic-cost claim anywhere in this amendment. Safety-critical budget arithmetic independently re-verified correct: 194*0.5=97.0s worst case; 600/97.0 ~= 6.19x margin. Two decorative 'Nx smaller than v8' comparisons are arithmetically wrong (PF-2) but do not affect the actual margin. No total-expected-cost = per-attempt-cost x inverse-success-probability computation is needed -- this is a bounded, single-run, non-probabilistic-success diagnostic, consistent with v8's own cost-model framing at this scale."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "OBJECTIVE_BOUNDARY explicitly restricts this amendment's result to 'purely descriptive,' explicitly excludes any PERSISTS/WEAKENS label, H-SSIQ-36e970's real-arm prediction, and lever L4, and is explicitly scoped to p=2437 alone -- verified by direct read, not merely trusted from prose. No scope inflation found."
  proof_architecture_challenges:
    - "Not applicable -- H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged; direct instrument-level search-procedure diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v9.yaml as committed
    at f400803d (draft, pre_freeze_review.status: pending): the core
    experimental design (isolate budget-truncation as the sole manipulated
    variable by reusing v8's exact BASE_SEED and per-vertex seed formula) is
    sound, re-derived from direct code trace; the 97.0s worst-case bound and
    the 600s/6.19x total budget margin are both independently re-verified
    correct; OBJECTIVE_BOUNDARY scoping is clean; PART A's comparison design
    correctly avoids the full-coverage-assumption crash shape that produced
    v8's PF-1/PF-9. One blocking defect is directly demonstrated, not merely
    hypothesized: REQUIRED COMPARISON 2's named source file (raw-result.json,
    confirmed to lack new_delta_map entirely) and its key-parsing requirement
    (a tuple(json.loads(key)) round-trip the one genuinely-imported candidate
    function cannot perform against RUN-SSIQ-a85692-h's differently-schemaed
    file, confirmed by direct KeyError reproduction) are both wrong as
    specified, creating a live crash-before-any-artifact-is-written path and
    a live silent-vacuous-comparison path. This draft is not safe to freeze
    until PF-1 is fixed; PF-2/PF-3/PF-4 should be applied in the same pass
    but do not independently block freeze.
  next_concrete_action: >-
    Coordinator: apply PF-1's required fix (correct REQUIRED COMPARISON 2's
    source-file citation to probe_delta_e_comparison.json only; add an
    explicit, disclosed tuple(json.loads(key)) parsing step with a collision
    check, listed as a new small authorized-duplicate helper in
    required_artifacts_note) -- textual only, zero new compute -- then apply
    PF-2/PF-3/PF-4 in the same pass, and request a second, focused pre-freeze
    round scoped specifically to re-verifying PF-1's fix against the actual
    committed RUN-SSIQ-a85692-h files before freezing and dispatching. Given
    the amendment's real compute is small (97.0s worst case), this should be
    a short round.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v9.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run -- this review is a specification
    and artifact-schema trace, not an execution. Non-durable, read-only local
    Python computations run directly against the committed tree to confirm
    (a) RUN-SSIQ-a85692-h/raw-result.json's full top-level key list lacks
    new_delta_map; (b) RUN-SSIQ-a85692-h/probe_delta_e_comparison.json's
    new_delta_map exists, has 203 string-typed keys in str(list(v)) form,
    and sample values; (c) RUN-SSIQ-a85692-b/raw-result.json's top-level key
    list includes phase_minus1_real_search with a '2437' sub-key, confirming
    trapping_diagnostic_v5.load_archived_prime_data's target schema exists
    only there. No file was written or modified by these computations; no
    run artifact, specification file, or ledger record was written or
    edited. Read in full: specification_v9.yaml; specification_v8.yaml
    (all PF-1 through PF-13 text, all three freeze-round verdicts);
    RT-BATCH-011.md; delta_e_independent_rng_probe_v8.py (780 lines, full);
    compute_delta_e.py lines 1-260 (two_sided_search/build_smooth_table);
    compute_delta_e_v2.py lines 240-303 (real_execution_budget_v2's
    F_p-rational wiring, delta_map_json_safe); trapping_diagnostic_v5.py
    lines 1-140 (load_archived_prime_data, build_graph_for_prime);
    RUN-SSIQ-a85692-h's raw-result.json and probe_delta_e_comparison.json
    (full); RUN-SSIQ-a85692-b's raw-result.json (top-level schema).
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v9.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v9.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
