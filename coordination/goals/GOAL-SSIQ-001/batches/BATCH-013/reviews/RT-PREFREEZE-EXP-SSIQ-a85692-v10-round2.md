# RT-PREFREEZE-EXP-SSIQ-a85692-v10-round2 — Round 2 pre-freeze Red Team
# review of the DRAFT amendment `specification_v10.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-013, task `TASK-20260806-b9d6ab`

**Reviews `experiments/EXP-SSIQ-a85692/specification_v10.yaml` at
`status: draft`, committed at `8305d9afee71469b8d88395f9610477b9e0c2e8e`
(468 lines, up from round 1's reviewed 277-line snapshot at `6edd3ce1`) — the
Coordinator's revision applying all eight round-1 findings (PF-1 through
PF-4 blocking, PF-5 through PF-8 advisory).** This is a targeted, scoped
round 2 per this task's own instructions: re-verify each of the four
blocking fixes on its own merits against the real underlying code (not
against the corrected prose alone), ask one new question PF-1's fix itself
creates, and do one fresh pass for defects the edit itself could have
introduced or left adjacent and unaudited. Round 1's own confirmed-sound
findings (seed-isolation, core budget arithmetic, self-conjugate-vertex
impossibility proof, scope discipline) are cited as still holding, not
re-derived. **No implementation file for v10 exists yet** (confirmed:
`experiments/EXP-SSIQ-a85692/implementation/` has no `*v10*` file as of
`8305d9af`) — this remains a plan audit, not an execution audit.

Read in full: `RT-PREFREEZE-EXP-SSIQ-a85692-v10.md` (round 1, 863 lines, in
full); the CURRENT `specification_v10.yaml` (468 lines, in full, not from
diff alone); `git diff 6edd3ce1 8305d9af -- experiments/EXP-SSIQ-a85692/specification_v10.yaml`
(516 unified-diff lines) to isolate exactly what the Coordinator's revision
touched. Directly re-executed/re-read against the real code (not trusted
from round 1's own quotes or the corrected prose): `delta_e_truncation_probe_v9.py`
in full (665 lines) — `run_truncation_probe_v9` (lines 147–211),
`compare_against_archived` (224–292), `parse_v8_new_delta_map` (302–325),
`compare_against_v8` (328–386), `git_state`/`main` (394+); `build_isogeny_graph.py`
lines 54–128 (`Fp2Field` class including `frobenius`, confirmed
`graph["field"]` is a real dict key at line 628); a full-file grep of
`specification_v10.yaml` for `"three times"` and `"frobenius"` to confirm no
surviving contradiction or citation error anywhere the round-1 quotes did
not specifically cover; a full-file grep for `compare_against` (zero
matches — the basis of this round's one new blocking-adjacent finding, PF-9
below); the pre-fix `budget.note` text at `6edd3ce1` (confirmed it already
read "once, not three times" before the fix pass, so it was never part of
PF-1's contradiction and needed no edit).

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
    with the Executor, the Coordinator, round 1's own reviewer, and every
    prior reviewer in this lineage. Does not upgrade the campaign's evidence
    tier and does not itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**FREEZE-WITH-FIXES.** All four round-1 BLOCKING findings (PF-1 through
PF-4) are genuinely, fully fixed on direct re-verification against the real
code — not merely against the corrected prose. §1–§4 below re-derive each
one independently. All four round-1 ADVISORY findings (PF-5 through PF-8)
are applied accurately, with no scope creep beyond what round 1 asked for
(§5). Task item 6's specific worry — that reusing `run_truncation_probe_v9`
directly might pull in an unexpected side effect (its own graph-identity
check, its own F_p-rational wiring conflicting with v10's separately-stated
step, or a disk write) — is checked directly against the function body and
does **not** materialize: `run_truncation_probe_v9` is a pure function, no
I/O, no `verify_graph_identity` call inside it, and its internal
F_p-rational wiring is exactly what `amendment_scope` step (1) already
(correctly) attributes to it, not a duplicate (§6).

Two **new** findings, both **ADVISORY**, not blocking, calibrated against
this exact lineage's own established severity convention for the identical
defect shape (`RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md`'s own PF-9, an
omitted-from-diff-classification finding rated advisory, and this document's
own PF-5, a genuine reuse-vs-duplicate disjunction also rated advisory):

- **PF-9 [ADVISORY, NEW]**: `required_artifacts_note`'s "GENUINELY IMPORTS"
  / "Does NOT import or call" classification — the exact GD-9/GD-10
  completeness discipline PF-3 was blocking for — never mentions
  `compare_against_archived` or `compare_against_v8`, the two comparison-
  logic functions v9's own module already defines, both genuinely reusable
  unchanged (pure functions, no module-level state referenced). This is the
  identical defect *shape* as PF-3 (an incomplete function-level diff under
  a self-invoked completeness standard), left unaudited by the round-1→
  round-2 fix pass because round 1's PF-3 finding was scoped to the search
  loop only. See §7.
- **PF-10 [ADVISORY, NEW]**: step (0) — the one-time graph build/identity
  re-verify, now outside the sweep loop as PF-1's fix requires — has no
  stated failure-handling behavior. The most literal reading (PF-2's
  try/except is explicitly scoped to "steps (1) through (7)... FOR ONE
  SWEEP POINT," excluding step (0) by construction) already produces the
  correct behavior (an uncaught propagation, i.e., an infra failure per
  AGENTS rule 3, not a fabricated partial result) — but this is correct by
  omission, not by statement, and the surrounding document's heavy,
  repeated emphasis on failure-isolation-by-wrapping creates a real
  (if secondary) risk that an Executor over-generalizes the pattern to
  step (0) too, catches the failure, and then has no specified behavior for
  what to do with a caught graph-setup failure. See §8.

Neither finding risks a structurally incompatible artifact or a materially
different implementation of the mechanism under test (the shape that made
PF-1/PF-2/PF-3/PF-4 blocking); both are one-sentence, zero-new-compute
textual fixes the Coordinator can apply in the same pass without another
dedicated review round, consistent with how this lineage's own precedent
(BATCH-010 round 2) resolved the same defect shape.

---

## §1 — PF-1 (graph rebuild count): re-verified fully consistent, no
## surviving contradiction anywhere in the file [task item 1]

A full-file grep for `"three times"` (case-insensitive) returns 7 matches,
all consistent with the "ONCE" resolution:

- Line 57 and lines 228–229: quote round 1's own finding describing the
  *original* contradiction, inside `amendment_scope`'s and
  `pre_freeze_review.pf1_summary`'s own historical narration of what was
  wrong and fixed — not live requirement text.
- Line 127: *"the genuinely new analysis this amendment adds beyond a
  mechanical repeat of v9 three times, per sweep point"* — this refers to
  running the **search** three times (once per budget), a true and
  unrelated statement; it does not claim the graph is rebuilt three times.
- Line 194: *"Graph reconstruction runs EXACTLY ONCE ... per PF-1's fix
  above -- NOT three times"* — correct, explicit disclaimer.
- Line 237: *pf1_summary*'s own historical description of what was
  corrected.
- Line 460 (`budget.note`): *"generous margin for graph-rebuild overhead
  (once, not three times)"* — confirmed via `git show 6edd3ce1` that this
  exact phrase was **already present, unedited, in the round-1 draft**;
  `budget.note` was never part of the original contradiction (it already
  agreed with the "ONCE" design before the fix pass), so its survival here
  is not a residual defect, just an unrelated field the fix pass correctly
  left untouched.

`amendment_scope`'s numbered procedure now states step "(0)" (graph
rebuild/re-verify, exactly once, before the sweep loop) as structurally
distinct from the "PER SWEEP POINT" steps "(1) THROUGH (7)"; `inputs.
truncation_sweep_search_v10` opens by describing "ONE SHARED, ONCE-BUILT
GRAPH"; `required_artifacts_note` describes `verify_graph_identity` as
"called once, per PF-1's fix." All three locations round 1 named
(`amendment_scope`'s procedure list, its own budget-justification
paragraph, and `inputs`) now agree, and no fourth location contradicts them.
**PF-1's fix is genuinely, fully consistent.** No new "once" vs. "three
times" split found.

## §2 — PF-2 (failure isolation): fix is complete and unambiguously
## specified for steps (1)–(7); step (0)'s own failure mode is the one gap
## [task item 2, partly new]

`amendment_scope` now states explicitly: *"STEPS (1) THROUGH (7) ABOVE, FOR
ONE SWEEP POINT, ARE ALL INSIDE THAT SWEEP POINT'S OWN try BLOCK: if ANY
exception is raised anywhere in steps (1)-(7) for sweep point b, catch it,
record a sweep_point_error field ... and CONTINUE to the next sweep point
... Accumulate each sweep point's outcome ... INCREMENTALLY into a list as
each sweep point completes (success or failure), and make the final
combined artifact write unconditional on how many of the three sweep
points actually succeeded -- 0, 1, 2, or 3 successes must all produce a
valid, honestly-reported truncation_sweep_comparison.json."* This is an
unambiguous, implementable specification: it covers PART A (step 1–2, now
delegated to `run_truncation_probe_v9`), both required comparisons (steps
5–6), and the new histogram/conjugate-pair reporting (step 7) — exactly
round 1's required scope, not merely Comparison 2. It explicitly requires
incremental accumulation and an unconditional final write, closing the
"write-once-at-the-end" architecture round 1 flagged as concretely
dangerous. **PF-2's fix is complete for the sweep-loop body.**

**The new question this task asked (created by PF-1's own fix, not
answerable from round 1):** step (0) — the one-time graph build and
`verify_graph_identity` call — now sits entirely outside any try/except the
spec names. Is this failure mode specified?

On the most literal reading, **yes, by construction**: PF-2's own text
scopes the try/except explicitly to *"steps (1) through (7) ... FOR ONE
SWEEP POINT"* — step (0) is outside that boundary both physically (it
precedes "THEN, PER SWEEP POINT b...") and textually (the try/except
description never mentions step 0). An Executor implementing this literally
would leave step (0) unwrapped, so an exception there (e.g.
`verify_graph_identity` raising) propagates uncaught, crashing the whole
script before any sweep point begins. That is in fact the **correct**
behavior here — there is no sweep point to isolate a graph-setup failure
*from*, since none can meaningfully proceed on an unverified or
never-built graph, and v9's own precedent already establishes this
convention explicitly: `delta_e_truncation_probe_v9.py`'s own
`TruncationProbeError` docstring reads *"Raised on a genuinely
unanticipated halt condition this frozen contract does not itself specify
a recovery path for (e.g. the graph-identity re-verification failing)"* —
i.e., v9's own established convention is exactly "let it crash, no
recovery path is defined," which AGENTS rule 3 already correctly treats as
an infra failure, not negative mathematical evidence, and not something a
partial-result record should paper over.

So this is **not a defect that would cause an incorrect implementation** —
but it is a *silent* correctness property (true by exclusion, never stated
by inclusion), sitting in a document that otherwise states every
failure-isolation boundary explicitly and repeatedly. Given `amendment_
scope`'s heavy emphasis on wrapping for isolation throughout, an Executor
could plausibly (if carelessly) over-generalize the pattern and wrap step
(0) too "for consistency" — and the spec gives no guidance for what a
caught step-(0) failure should then do (record a top-level
`graph_setup_error` and still attempt the sweep loop against a
partially-built or `None` graph? Abort immediately after catching?). That
is genuinely unspecified and would matter if it happened. **PF-10
[ADVISORY, NEW]** (§8) recommends one explicit sentence closing this,
mirroring `TruncationProbeError`'s own documented rationale rather than
leaving it implicit.

## §3 — PF-3 (reuse of `run_truncation_probe_v9`): re-verified correct,
## signature and behavior match the spec's description exactly [task item 3]

Re-read `run_truncation_probe_v9(graph, base_seed, per_vertex_budget_seconds)`
directly (`delta_e_truncation_probe_v9.py:147–211`), independent of round
1's own quote. Confirmed: third parameter `per_vertex_budget_seconds` is
used directly at the function's only internal call site
(`compute_delta_e.two_sided_search(..., time_budget_seconds=
per_vertex_budget_seconds)`, line 181); the module-level
`PER_VERTEX_BUDGET_SECONDS` constant is referenced nowhere inside the
function body. The function performs, in order: (a) F_p-rational
unconditional wiring (`new_delta_map[v] = 1` for all 9 F_p-rational
vertices, lines 162–166); (b) for each of the 194 non-F_p-rational
vertices, a fresh `random.Random(seed_v)` via
`v8probe.derive_per_vertex_seed`, then `compute_delta_e.two_sided_search`
with the passed-in fixed budget; (c) returns a plain dict (`new_delta_map_
raw`, `per_vertex_records`, `n_resolved`, `n_timed_out`, `n_attempted`,
`n_non_fp_rational`, `n_fp_rational_wired_unconditionally`,
`coverage_fraction`) — no side effects, no disk I/O, no call to
`verify_graph_identity` anywhere in its body.

The current v10 spec text (`inputs.truncation_sweep_search_v10`) states:
*"the per-vertex search loop for EVERY sweep point GENUINELY IMPORTS AND
CALLS delta_e_truncation_probe_v9.run_truncation_probe_v9(graph, base_seed,
b) DIRECTLY, UNCHANGED -- no new, parallel reimplementation of the
per-vertex search loop, the F_p-rational wiring step, or the fresh-per-
vertex-RNG construction is written."* This matches the function's actual
signature and behavior exactly. `required_artifacts_note` lists
`run_truncation_probe_v9` under "GENUINELY IMPORTS, UNCHANGED" and
explicitly excludes it from the "Does NOT import or call" list (which now
correctly reads "v9's own main," not `run_truncation_probe_v9`, confirming
the pre-fix draft's opposite listing — round 1's `run_truncation_probe_v9,
main` exclusion — was itself corrected). **PF-3's fix is genuinely
correct** on direct code re-verification, not merely internally consistent
prose.

## §4 — PF-4 (`frobenius` citation): re-verified correct against the real
## `Fp2Field.frobenius` method, and consistent everywhere the old citation
## appeared [task item 4]

Re-read `Fp2Field.frobenius` directly (`build_isogeny_graph.py:119–124`):
`def frobenius(self, x): ... return (x[0] % p, (-x[1]) % p)` — an instance
method on the `Fp2Field` class, taking one element argument beyond `self`
and returning the conjugate `(a, -b)`. Confirmed `graph["field"]` is a real
dict key holding an `Fp2Field` instance (`build_isogeny_graph.py:628`,
`"field": field,`, inside the dict `build_graph_for_prime` ultimately
returns). `graph["field"].frobenius(v)` is therefore the syntactically and
semantically correct call form.

A full-file grep of `specification_v10.yaml` for `frobenius` returns 13
matches; every live (non-historical-quote) usage now reads
`graph["field"].frobenius(v)` — in `amendment_scope` (line 157/162),
`inputs` (lines 346–347/351/355), and `required_artifacts_note` (line
419) — the three locations round 1 named. The remaining matches are
round 1's own historical quotes of the disproven `"build_isogeny_graph.
frobenius"` citation, appearing inside `pf4_summary` and inline "PF-4 FIX
APPLIED" explanatory clauses that correctly frame it as the *rejected*
form, never as a live instruction. **PF-4's fix is genuinely correct and
fully consistent**, re-verified against the real method, not merely
self-consistent prose.

## §5 — PF-5 through PF-8: spot-checked, accurately worded, no new claim
## beyond round 1's request [task item 5]

- **PF-5** (`parse_v8_new_delta_map` reuse disjunction, pre-resolved
  toward genuine import): `inputs` now states *"Comparison 2 GENUINELY
  IMPORTS AND CALLS delta_e_truncation_probe_v9.parse_v8_new_delta_map(path),
  UNCHANGED -- PF-5 FIX APPLIED..."* — matches round 1's required fix
  exactly; no open disjunction remains for this function.
- **PF-6** (cross-hardware reproducibility caveat restated): `amendment_
  scope`'s new "CROSS-HARDWARE REPRODUCIBILITY CAVEAT" paragraph restates
  v9's own PF-3 finding accurately, with the same "~13-70% margin"
  qualifier round 1's own text used — no overclaiming beyond the original
  advisory ask.
- **PF-7** (statistical-power framing requirement): the new "STATISTICAL-
  POWER FRAMING REQUIRED" clause requires `n_resolved` and the
  conjugate-pair-corrected effective sample size accompany any future
  histogram-shift citation — matches round 1's required wording, applied
  to `execution_report.yaml` and "any future citation," not narrowed or
  broadened.
- **PF-8** (empty-histogram well-definedness at n_resolved=0): the value
  histogram is now explicitly specified as `EMPTY ({}) if n_resolved==0`,
  matching round 1's required fix precisely.

No PF-5–PF-8 fix introduces a claim beyond what round 1 asked for.

## §6 — Task item 6, first half: does reusing `run_truncation_probe_v9`
## pull in an unexpected side effect? [task item 6]

**No — checked directly, and the answer is clean.** As established in §3,
`run_truncation_probe_v9` is a pure function: no disk writes, no call to
`verify_graph_identity` (so no duplication or conflict with v10's own
once-only step-0 identity check), and its internal F_p-rational wiring is
exactly the behavior `amendment_scope` step (1) already (correctly)
attributes to the delegated call, not a second, redundant wiring pass
written by v10's own new code. `inputs`'s explicit disclaimer — *"no new,
parallel reimplementation of the per-vertex search loop, the F_p-rational
wiring step, or the fresh-per-vertex-RNG construction is written"* — is
accurate on direct code read, not merely asserted. The module's other
top-level functions (`compare_against_archived`, `parse_v8_new_delta_map`,
`compare_against_v8`, `git_state`, `main`) are separately defined and
untouched by `run_truncation_probe_v9`'s own call; `main` is the only
disk-writing function in v9's module, and v10's spec correctly excludes it
from reuse. No duplication or side-effect conflict found.

## §7 — Task item 6, second half / fresh pass: `compare_against_archived`
## and `compare_against_v8` are the one comparison-logic analogue of PF-3's
## defect shape left unaudited [NEW]

Re-reading the "REQUIRED COMPARISONS" text in both `amendment_scope` and
`inputs` and the full `required_artifacts_note`, a full-file grep for
`compare_against` returns **zero matches** anywhere in `specification_v10.yaml`.
The spec only names the two **data-loading** helpers as genuinely imported
— `trapping_diagnostic_v5.load_archived_prime_data` (Comparison 1's
archived-value source) and `delta_e_truncation_probe_v9.
parse_v8_new_delta_map` (Comparison 2's v8-value source) — but never
addresses the actual **comparison logic**: the matching/diffing computation
that turns `(new_delta_map, archived_delta_map, non_fp_rational_set)` into
`n_value_matches_vs_archived`, `n_value_differs_vs_archived`,
`value_differs_vs_archived_triples`, the `non_fp_rational_only`
sub-breakdown, and the `domain_note`/`isolation_note` methodological
disclosures.

I read these functions directly: `compare_against_archived(new_delta_map,
archived_delta_map, non_fp_rational_set)` (`delta_e_truncation_probe_v9.py:224–292`)
and `compare_against_v8(new_delta_map, v8_delta_map, non_fp_rational_set)`
(lines 328–386) are **both already genuinely reusable** — pure functions,
parameterized entirely by their arguments, referencing no module-level
constant (`PER_VERTEX_BUDGET_SECONDS`, `BASE_SEED`, `PRIME`) anywhere in
their bodies. This is the **identical defect shape** `required_artifacts_
note` invokes GD-9/GD-10 to prevent, and the identical shape PF-3 was rated
BLOCKING for (a claimed "EXPLICIT, CODE-VERIFIED FUNCTION-LEVEL DIFF" that
omits or misstates a directly relevant, already-reusable function) —
except here the note does not make a **false** claim about these two
functions (unlike PF-3's original false "not reusable" justification for
`run_truncation_probe_v9`); it simply never mentions them at all, in either
the "GENUINELY IMPORTS" list or the "Does NOT import or call" exclusion
list, despite that exclusion list otherwise being detailed and specific.

**Severity, calibrated against this exact lineage's own precedent, not
first-principles judgment alone:** `RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md`'s
own PF-9 found an almost identical shape (a function's provenance status
omitted from `required_artifacts_note`'s diff classification) and rated it
**ADVISORY**, not blocking, because the omission itself does not force an
Executor toward two structurally incompatible artifacts — it is a
completeness gap in documentation, not a live contradiction. This
document's own PF-5 (an open reuse-vs-duplicate disjunction for
`parse_v8_new_delta_map`) was likewise rated ADVISORY in round 1, not
blocking, even though it was a genuine, live, two-way fork facing the
Executor. Applying that same convention here: **PF-9 [ADVISORY, NEW]**.
Unlike the BATCH-010 precedent (where the omitted logic was not even a
standalone importable symbol), `compare_against_archived`/`compare_against_v8`
**are** directly, cleanly importable and reusable, so the recommended fix
is unambiguous and cheap: pre-resolve toward genuine import, exactly as
PF-5 did for `parse_v8_new_delta_map` in the very same document. One small
plumbing note for whoever applies this fix: neither function's needed
`non_fp_rational_set` argument is returned by `run_truncation_probe_v9`'s
own output dict (which returns `per_vertex_records` and `n_non_fp_rational`
but not the vertex list/set itself); it must be reconstructed once,
cheaply, either directly from `graph` (`{v for v in graph["vertices"] if
not graph["field"].is_in_fp(v)}`) or from `per_vertex_records`'s own
`"vertex"` fields — a detail the fix text should state explicitly rather
than leave for the Executor to discover.

## §8 — PF-10 [ADVISORY, NEW]: step (0)'s own failure mode should be
## stated explicitly, not left correct-by-omission

See §2 for the full derivation. Recommended fix: one sentence in
`amendment_scope`, immediately after step (0)'s description, stating
explicitly that step (0) is **not** wrapped in any try/except — if
`build_graph_for_prime` or `verify_graph_identity` raises, the exception
propagates uncaught, the run terminates with no sweep point ever attempted,
and this is an infra/setup failure under AGENTS.md rule 3 (not negative
mathematical evidence, and never to be recorded as a `sweep_point_error`
for any budget) — mirroring `TruncationProbeError`'s own documented
rationale in v9's frozen code (*"a genuinely unanticipated halt condition
this frozen contract does not itself specify a recovery path for"*). This
closes the residual risk that an Executor, pattern-matching on the
document's otherwise-pervasive wrap-everything discipline, over-generalizes
PF-2's try/except to step (0) and then has no specified behavior for a
caught graph-setup failure.

---

## Objections

- **OBJ-1 [PF-1, RESOLVED]**: re-verified, no remaining "once" vs. "three
  times" contradiction anywhere in the current file; all three locations
  round 1 named now agree, and the one additional location
  (`budget.note`) was already consistent before the fix pass and required
  no edit.
- **OBJ-2 [PF-2, RESOLVED for steps 1–7; PF-10 opens a narrower, advisory
  question for step 0]**: the sweep-point failure-isolation discipline is
  now complete and unambiguous for steps (1)–(7) — each sweep point's
  entire bundle is wrapped, results accumulate incrementally, and the
  final write is unconditional on 0/1/2/3 successes, exactly as required.
  Step (0)'s own failure mode is correct by construction (excluded from
  the try/except's stated scope) but not stated explicitly, creating a
  secondary, low-probability risk of over-generalization by an Executor
  — see PF-10.
- **OBJ-3 [PF-3, RESOLVED]**: `run_truncation_probe_v9`'s signature and
  behavior, re-read directly and independent of round 1's own quote,
  confirm the current spec's description of genuine, unchanged reuse is
  accurate; the function is a pure computation with no disk I/O and no
  internal `verify_graph_identity` call, so reusing it introduces no
  hidden side effect or conflict with v10's separately-specified,
  once-only graph build/verify step.
- **OBJ-4 [PF-4, RESOLVED]**: `graph["field"].frobenius(v)` is confirmed
  the correct call form against `Fp2Field.frobenius`'s real signature and
  the real `graph` dict's `"field"` key, and appears consistently
  everywhere the disproven `build_isogeny_graph.frobenius` citation used
  to appear; the only remaining occurrences of the old citation are
  historical quotes correctly framed as the rejected form.
- **OBJ-5 [PF-5–PF-8, RESOLVED]**: spot-checked, accurately worded, no
  scope creep beyond round 1's request.
- **OBJ-6 [PF-9, ADVISORY, NEW]**: `required_artifacts_note`'s explicit
  function-level diff — the exact completeness standard PF-3 was blocking
  for — never classifies `compare_against_archived` or `compare_against_v8`
  as either genuinely imported or an authorized duplicate, despite both
  being pure, unconditionally reusable functions already defined in v9's
  frozen module. Calibrated against this lineage's own precedent for the
  identical defect shape (BATCH-010 round 2's PF-9; this document's own
  PF-5), this is advisory, not blocking: no structurally incompatible
  artifact results either way, but leaving it open reintroduces exactly
  the duplicate-code-drift risk PF-3 was raised to eliminate.
- **OBJ-7 [PF-10, ADVISORY, NEW]**: the one-time graph build/identity-
  verify step's own failure-handling behavior is correct by omission (PF-2's
  try/except is explicitly scoped to steps 1–7 only) but never stated
  explicitly, unlike every other failure boundary in this document.

## Required controls

- **[PF-9, ADVISORY]**: add `compare_against_archived` and
  `compare_against_v8` to `required_artifacts_note`'s "GENUINELY IMPORTS,
  UNCHANGED" list (recommended — both are already genuinely reusable,
  confirmed on direct code read, removing the same duplicate-code-drift
  risk PF-3's fix removed for the search loop), and state explicitly how
  each sweep point's `non_fp_rational_set` argument is obtained (recompute
  from `graph`, or derive from `run_truncation_probe_v9`'s own
  `per_vertex_records`) since it is not returned directly by that
  function's output dict.
- **[PF-10, ADVISORY]**: add one sentence to `amendment_scope` immediately
  after step (0) stating explicitly that step (0) is not wrapped in any
  try/except, that an exception there propagates uncaught and terminates
  the run before any sweep point is attempted, and that this is an infra
  failure under AGENTS.md rule 3 (never recorded as a `sweep_point_error`),
  mirroring `TruncationProbeError`'s own documented rationale in v9.
- Neither control blocks freeze; both are textual, zero new compute, and
  can be applied in the same pass without a further dedicated review
  round, consistent with how this lineage's own BATCH-010 round 2
  resolved the identical defect shape (PF-9 there) under a
  FREEZE-WITH-FIXES verdict.

## Counterexample or mutation

Carried forward from round 1, still the correct discriminating check once
an implementation exists (not yet possible — no implementation file):
inject a deliberate fault into the b=0.8 sweep point's histogram/
conjugate-pair code after b=0.6 completes successfully, and confirm the
written `truncation_sweep_comparison.json` still contains b=0.6's full
result plus a recorded `sweep_point_error` for b=0.8, never silently
discarding b=0.6. This round adds one further, cheap discriminating check
once code exists: force `verify_graph_identity` to raise during step (0)
and confirm the run terminates with no `truncation_sweep_comparison.json`
written at all (not a zero-sweep-point "success" record) — the concrete
test of PF-10's recommended behavior.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
unchanged from round 1: toy-scale, single-prime search-procedure
diagnostic work, `H-SSIQ-36e970.asymptotic_claim: null` throughout. The
relevant baseline remains this lineage's own code-verified-crash-path and
GD-9/GD-10 required-artifacts-accuracy standard; PF-9 here is precisely
that standard applied to the two functions PF-3's own fix pass did not
reach, and PF-10 is that same "trace it, don't trust it" discipline
applied to the one failure boundary PF-1's fix newly created (moving graph
setup outside the sweep loop) rather than one round 1 could have asked
about (round 1 reviewed a draft where graph setup was still, incorrectly,
inside the loop).

## Heuristic challenges

Unchanged from round 1 — `H-SSIQ-36e970.heuristic_assumptions` remains
empty, `asymptotic_claim: null` throughout; no numbered heuristic
implicated by this amendment or by this round's two new findings.

## Cost model challenges

Unchanged from round 1 — budget arithmetic (`194*2.4=465.6s` worst case,
`1200/465.6≈2.58x` margin) re-confirmed still correct and untouched by the
fix pass. Neither PF-9 nor PF-10 has any cost implication: PF-9 concerns
which existing function computes an already-planned comparison, not
whether it runs or how long it takes; PF-10 concerns documentation of an
already-correct control-flow default, not new compute.

## Reduction and scope challenges

Unchanged from round 1 — no affected/safe cryptographic scheme list
anywhere; `OBJECTIVE_BOUNDARY` (re-read, unedited by the fix pass except
for the "three times" grep sweep already covered in §1) still correctly
excludes `H-SSIQ-36e970`'s real-arm prediction, any PERSISTS/WEAKENS
label, and lever L4, scoped to p=2437 only. No scope inflation found in
this round's fresh pass.

## Proof architecture challenges

Not applicable — unchanged from round 1;
`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v10.yaml` as
committed at `8305d9afee71469b8d88395f9610477b9e0c2e8e` (draft, no
implementation file yet written): all four round-1 BLOCKING defects
(PF-1 through PF-4) are genuinely, fully corrected — re-verified against
the real underlying code (`delta_e_truncation_probe_v9.py`,
`build_isogeny_graph.py`), not merely against the corrected prose's own
internal consistency — and all four round-1 ADVISORY fixes (PF-5 through
PF-8) are applied accurately with no scope creep. Task item 6's specific
concern (reusing `run_truncation_probe_v9` pulling in an unexpected side
effect) is checked directly and does not materialize. Two new findings
from this round's targeted new-question (PF-10, step-0 failure handling)
and fresh pass (PF-9, comparison-logic reuse omission) are real but
narrow: both are documentation-completeness gaps of a defect shape this
lineage's own precedent (this document's PF-5; BATCH-010 round 2's PF-9)
treats as advisory, not blocking, because neither creates a live risk of
two good-faith Executors producing structurally incompatible artifacts —
the graph-rebuild-count, failure-isolation-scope, false-reuse-justification,
and non-existent-import defects that made PF-1 through PF-4 blocking. This
amendment's underlying experimental design (three intermediate budgets,
correctly bounded below the natural-completion floor, correctly isolating
budget as the sole manipulated variable, correctly and honestly bounded on
cost) remains sound and unchanged since round 1.

## Next concrete action

Coordinator: apply PF-9 and PF-10 in one further textual pass (add
`compare_against_archived`/`compare_against_v8` to `required_artifacts_
note`'s genuine-import list with an explicit note on deriving
`non_fp_rational_set`; add one sentence to `amendment_scope` step (0)
stating its failure mode explicitly) — zero new compute, no further
dedicated red-team round required given both fixes are unambiguous,
textual, and match already-established patterns in this exact document
(PF-3's and PF-5's own resolutions) — then freeze and dispatch. Once an
implementation exists, run both discriminating checks named above
(the b=0.8 injected-fault test carried forward from round 1, and the new
step-0 injected-fault test from PF-10) before treating the real 465.6s
worst-case compute as validated infrastructure, not merely validated
prose.

## Overall verdict

**FREEZE-WITH-FIXES.** All four round-1 blocking findings are genuinely
resolved on direct re-verification against the real code, not merely
against self-consistent corrected prose. Two new advisory findings (PF-9:
`compare_against_archived`/`compare_against_v8` omitted from the
GD-9/GD-10 function-level diff PF-3's fix was meant to make complete;
PF-10: step (0)'s own failure mode is correct by omission but not stated
explicitly) should be applied in the same textual pass, with zero new
compute and no further dedicated review round required, consistent with
this lineage's own precedent for the identical defect shape.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v10-round2
  task_id: TASK-20260806-b9d6ab
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v10.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at
    8305d9afee71469b8d88395f9610477b9e0c2e8e -- the Coordinator's revision
    applying all eight round-1 pre-freeze findings (PF-1 through PF-4
    blocking: graph-rebuild-count self-contradiction, incomplete
    failure-isolation scope, a false code-verified reuse justification,
    and a non-existent module-level import citation; PF-5 through PF-8
    advisory) to the three-point intermediate-budget truncation sweep
    (0.6s/0.8s/1.0s) amending the frozen specification_v9.yaml. No
    implementation file exists yet as of the reviewed commit. Round 2
    (targeted, scoped) pre-freeze review, following round 1's
    DO-NOT-FREEZE verdict at 6edd3ce1.
  objections:
    - "OBJ-1 [PF-1, RESOLVED]: re-verified via full-file grep for 'three times' -- all 7 matches are either historical quotes of the original defect (correctly framed as rejected), the unrelated 'search runs three times' statement, or explicit 'NOT three times' disclaimers; the graph-rebuild-once design is now stated consistently in amendment_scope's step (0), inputs' opening sentence, and required_artifacts_note; budget.note already agreed with 'once' before the fix pass (confirmed via git show 6edd3ce1) and required no edit."
    - "OBJ-2 [PF-2, RESOLVED for steps 1-7]: amendment_scope now explicitly states steps (1)-(7) are each inside that sweep point's own try block, results accumulate incrementally, and the final artifact write is unconditional on 0/1/2/3 successes -- complete and unambiguous for an Executor. Step (0), the one-time graph build/verify, is correctly excluded from this scope by construction (matching v9's own TruncationProbeError precedent of 'no specified recovery path'), but this exclusion is never stated explicitly -- see PF-10."
    - "OBJ-3 [PF-3, RESOLVED]: run_truncation_probe_v9 re-read directly (delta_e_truncation_probe_v9.py:147-211), independent of round 1's own quote -- confirmed a pure function, third parameter used directly at its one internal call site, no reference to the module-level constant, no disk I/O, no internal verify_graph_identity call. The current spec's description of genuine, unchanged reuse matches this exactly."
    - "OBJ-4 [PF-4, RESOLVED]: graph[\"field\"].frobenius(v) re-verified correct against Fp2Field.frobenius's real signature (build_isogeny_graph.py:119-124, returns (x[0]%p, (-x[1])%p)) and the real graph dict's 'field' key (line 628); appears consistently in all three locations round 1 named, with all remaining 'build_isogeny_graph.frobenius' occurrences correctly framed as historical quotes of the rejected form."
    - "OBJ-5 [PF-5 through PF-8, RESOLVED]: spot-checked against round 1's exact required wording; all four applied accurately with no scope creep."
    - "OBJ-6 [PF-9, ADVISORY, NEW]: required_artifacts_note's explicit function-level diff -- the same GD-9/GD-10 completeness standard PF-3 was blocking for -- never classifies compare_against_archived or compare_against_v8 (delta_e_truncation_probe_v9.py:224-292, 328-386) as either genuinely imported or an authorized duplicate, despite both being pure, unconditionally reusable functions with no module-level state referenced. A full-file grep for 'compare_against' returns zero matches in specification_v10.yaml. Calibrated against this lineage's own precedent for the identical defect shape (RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md's own PF-9; this document's own PF-5), this is advisory, not blocking, since no structurally incompatible artifact results either way -- but leaving it open reintroduces the exact duplicate-code-drift risk PF-3's fix was meant to close."
    - "OBJ-7 [PF-10, ADVISORY, NEW]: step (0)'s own failure-handling behavior is correct by omission (PF-2's try/except is explicitly scoped to steps 1-7 only, so step 0 naturally propagates any exception uncaught, an infra failure per AGENTS rule 3) but is never stated explicitly, unlike every other failure boundary in this document -- a real, if secondary, risk that an Executor over-generalizes the pervasive wrap-everything pattern to step 0 and then has no specified behavior for a caught graph-setup failure."
  required_controls:
    - "[PF-9, ADVISORY]: add compare_against_archived and compare_against_v8 to required_artifacts_note's 'GENUINELY IMPORTS, UNCHANGED' list (both confirmed already reusable unchanged), and state explicitly how each sweep point's non_fp_rational_set argument is derived, since run_truncation_probe_v9's own output dict does not return it directly."
    - "[PF-10, ADVISORY]: add one sentence to amendment_scope immediately after step (0) stating explicitly that step (0) is not wrapped in any try/except, an exception there propagates uncaught and terminates the run before any sweep point is attempted, and this is an infra failure under AGENTS.md rule 3, never recorded as a sweep_point_error -- mirroring TruncationProbeError's own documented rationale in v9's frozen code."
    - "Neither PF-9 nor PF-10 blocks freeze; both are textual, zero new compute, and can be applied in the same pass without a further dedicated review round, consistent with how BATCH-010 round 2 resolved the identical defect shape under a FREEZE-WITH-FIXES verdict."
  counterexample_or_mutation: >-
    Carried forward from round 1 (not yet executable -- no implementation
    file exists): once implemented, inject a deliberate fault into the
    b=0.8 sweep point's histogram/conjugate-pair code after b=0.6 completes
    successfully, and confirm truncation_sweep_comparison.json still
    contains b=0.6's full result plus a recorded sweep_point_error for
    b=0.8. This round adds one further cheap check specific to PF-10: force
    verify_graph_identity to raise during step (0) and confirm the run
    terminates with no truncation_sweep_comparison.json written at all (an
    infra failure, not a fabricated zero-sweep-point "success" record).
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    unchanged from round 1, toy-scale single-prime search-procedure
    diagnostic work, H-SSIQ-36e970.asymptotic_claim null throughout. The
    relevant baseline remains this lineage's own code-verified-crash-path
    and GD-9/GD-10 required-artifacts-accuracy standard; PF-9 is that exact
    standard applied to the two comparison-logic functions PF-3's own fix
    pass did not reach, and PF-10 is the same discipline applied to the one
    failure boundary PF-1's fix newly created by moving graph setup outside
    the sweep loop.
  heuristic_challenges:
    - "Unchanged from round 1: H-SSIQ-36e970.heuristic_assumptions remains empty, asymptotic_claim null throughout; no numbered heuristic implicated by this amendment or by this round's two new findings."
  cost_model_challenges:
    - "Unchanged from round 1: budget arithmetic (194*2.4=465.6s worst case, 1200/465.6~=2.58x margin) re-confirmed correct and untouched by the fix pass. Neither PF-9 nor PF-10 has any cost implication -- PF-9 concerns which existing function computes an already-planned comparison, PF-10 concerns documentation of an already-correct control-flow default."
  reduction_and_scope_challenges:
    - "Unchanged from round 1: no affected/safe cryptographic scheme list anywhere; OBJECTIVE_BOUNDARY still correctly excludes H-SSIQ-36e970's real-arm prediction, any PERSISTS/WEAKENS label, and lever L4, scoped to p=2437 only. No scope inflation found in this round's fresh pass."
  proof_architecture_challenges:
    - "Not applicable, unchanged from round 1 -- H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v10.yaml as
    committed at 8305d9afee71469b8d88395f9610477b9e0c2e8e (draft, no
    implementation file yet written): all four round-1 BLOCKING defects
    (PF-1 through PF-4) are genuinely, fully corrected, re-verified against
    the real underlying code rather than the corrected prose's own internal
    consistency; all four round-1 ADVISORY fixes (PF-5 through PF-8) are
    applied accurately with no scope creep; task item 6's specific
    side-effect concern about reusing run_truncation_probe_v9 does not
    materialize on direct check. Two new findings (PF-9: comparison-logic
    reuse status omitted from required_artifacts_note's own completeness
    standard; PF-10: step (0)'s failure mode correct by omission but not
    stated explicitly) are real but narrow, of a defect shape this
    lineage's own precedent treats as advisory rather than blocking, since
    neither risks two good-faith Executors producing structurally
    incompatible artifacts. The underlying experimental design (three
    intermediate budgets, correctly bounded, correctly isolating budget as
    the sole manipulated variable, correctly and honestly bounded on cost)
    remains sound and unchanged since round 1.
  next_concrete_action: >-
    Coordinator: apply PF-9 and PF-10 in one further textual pass (add
    compare_against_archived/compare_against_v8 to required_artifacts_
    note's genuine-import list with an explicit non_fp_rational_set
    derivation note; add one sentence to amendment_scope step (0) stating
    its failure mode explicitly) -- zero new compute, no further dedicated
    red-team round required -- then freeze and dispatch. Once an
    implementation exists, run both discriminating checks named above (the
    b=0.8 injected-fault test carried forward from round 1, and the new
    step-0 injected-fault test from PF-10) before treating the real 465.6s
    worst-case compute as validated infrastructure.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v10-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no code executed from this
    lineage's implementation modules -- this review is a specification and
    real-code trace against a draft with no implementation file yet, not an
    execution. Non-durable, read-only local computations run directly
    against the committed tree: (a) full-file grep of specification_v10.yaml
    for 'three times' (7 matches, all consistent with the ONCE resolution)
    and 'frobenius' (13 matches, all consistent with graph["field"].
    frobenius(v)); (b) full-file grep for 'compare_against' (zero matches,
    the basis of PF-9); (c) git diff 6edd3ce1 8305d9af -- experiments/
    EXP-SSIQ-a85692/specification_v10.yaml (516 unified-diff lines) to
    isolate exactly what the fix pass touched; (d) git show 6edd3ce1:...
    to confirm budget.note's 'once, not three times' phrase predates the
    fix pass and was never part of PF-1's contradiction; (e) direct re-read
    of run_truncation_probe_v9, compare_against_archived,
    parse_v8_new_delta_map, compare_against_v8, and Fp2Field.frobenius in
    their real source files, independent of round 1's own quotes, to
    confirm signatures/behavior match the current spec's descriptions. No
    file was written or edited by any of these computations other than this
    report itself.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task wrote
    only coordination/goals/GOAL-SSIQ-001/batches/BATCH-013/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v10-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v10.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
