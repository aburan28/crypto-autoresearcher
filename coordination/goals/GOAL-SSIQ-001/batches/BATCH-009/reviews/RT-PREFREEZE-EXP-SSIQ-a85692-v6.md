# RT-PREFREEZE-EXP-SSIQ-a85692-v6 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v6.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-009

**Reviews `experiments/EXP-SSIQ-a85692/specification_v6.yaml` at `status: draft`,
`pre_freeze_review.status: PENDING`, as read directly from the working tree
under task `TASK-20260806-1deeb3`.** Per this task's own operating rules, only
a Coordinator-committed snapshot is treated as durable evidence; this report
does not treat the draft file itself, or anything else in the working tree,
as a research artifact — it is advisory input to the Coordinator's own freeze
decision, and changes nothing under `experiments/EXP-SSIQ-a85692/` (including
`specification_v5.yaml`, frozen `59cfaf39ea721780b4cddf3d7ac5968a70872b15`,
confirmed retained unedited) or any ledger record.

Read in full: `specification_v6.yaml` (281 lines); the frozen, unchanged
`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py`
(`greedy_descent_hitting_time`, lines 179–222, and every other function in the
file); `experiments/EXP-SSIQ-a85692/implementation/trapping_diagnostic_v5.py`
in full (500 lines, including its required-cross-check comment block and its
hand-traced p=2437/(148,37) counter-example); `experiments/EXP-SSIQ-a85692/implementation/ols_hardened.py`
in full (the established supersede-by-addition pattern this draft claims to
follow); `ledger/goals/GOAL-SSIQ-001/goal.yaml`'s GD-1 through GD-12 defect
lineage and BATCH-008's `next_action`/`resume_action`; `ledger/evidence/EV-SSIQ-334ab9.yaml`
and `ledger/decisions/DEC-20260806-357b30.yaml` in full;
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v5.md`
in full, as the exact caliber and format this review is expected to match.

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
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This
    review shares a model family with every producer and every prior
    reviewer in this lineage; it does not upgrade the campaign's evidence
    tier by itself.
```

---

## Bottom line up front

**This draft should NOT be frozen as written.** The central mathematical claim
of PART A (GD-12's fix) is genuinely correct — I traced it by hand against the
actual frozen `descent_hitting_time.py` code, not the draft's prose, and it
holds unconditionally, including through the fallback multi-edge branch and
the first-step (`prev is None`) case. That is a real, hard-won result and
should not be understated. But **PART B contains a new mathematical error of
exactly GD-12's own shape** — an unconditional claim about "empty basin"
behavior that is false for one specific, non-empty subset of vertices — and
two further blocking gaps in reuse-mechanics and failure-handling
specification:

1. **PART B (PF-1, BLOCKING, most severe): item 3's "empty basin → basin_size
   == 1, its own start" convention is FALSE for every delta_E = 1 structural
   local minimum, and would make the REQUIRED ACCOUNTING ASSERTION fail on
   every prime, every run, as literally specified.** `is_structural_local_min(v)`
   (`trapping_diagnostic_v5.py` line 234: `delta_map[v] <= min(nbr_deltas)`)
   trivially flags **every** delta_E = 1 vertex as a structural local
   minimum — the draft's own text says as much for the immediate-branch case
   ("1 is the global minimum ... trivially satisfies is_structural_local_min").
   But `greedy_descent_hitting_time_v2`'s own top-level short-circuit
   (`if delta_map[start] == 1: return trapped=False`, inherited unchanged
   from the frozen function, line 195–197) fires **before** the walk ever
   reaches the loop that would otherwise trap a genuine local minimum at
   itself in 0 steps. So delta_E = 1 local minima can **never** receive a
   `trapped=True` walk from any start vertex, including — unlike every other
   structural local minimum — their own. Their true basin size under PART A's
   corrected, trapped=True-only cross-check is exactly 0, not the ">= 1 via
   self" item 3 asserts for "every" local minimum. A literal implementation of
   item 3 force-reports `basin_size == 1` for these vertices while
   simultaneously counting the same vertex in `n_trapped_false` (their own
   walk IS trapped=False) — a double count that inflates
   `sum(len(basin[m])) + n_trapped_false` above `n_vertices` by exactly the
   F_p-rational locus size for every prime (a nonzero, already-known quantity:
   9/18/18/17 per BATCH-008's own disagreement data). See PF-1.
2. **PART B (PF-2, BLOCKING): the "REUSED, not reimplemented" instruction for
   `is_structural_local_min` names something that is not actually importable.**
   `trapping_diagnostic_v5.py` has no standalone `is_structural_local_min`
   function — the computation is six inline lines inside `run_diagnostic_for_prime`,
   and the per-vertex result (`local_min_flags`, the only place "the set of
   structural local minima" is ever materialized) is a purely local variable,
   never included in the function's own returned `result` dict (only the
   aggregate `n_structural_local_min`/`fraction_structural_local_min` survive
   to the caller). See PF-2.
3. **(PF-3, BLOCKING): PART A's "halt with an explicit error ... on ANY
   disagreement" and PART B's "if it does not pass for a given prime, PART B
   must not run for that prime and must report why" describe two different,
   irreconcilable failure-handling models** (a global, run-aborting raise vs.
   a per-prime catch-and-continue), and the draft never states which applies.
   See PF-3.

Two advisory items (PF-4, PF-5, PF-6) round out the review; none is blocking
on its own. All findings are fixable at zero new search cost, consistent with
the amendment's own budget, and none requires redesigning either part's
mechanism.

---

## PART A — is the core mathematical claim (Q1) actually correct?

**Yes, unconditionally, traced directly against the frozen code — this is the
one place this review can confirm the draft did what GD-12's own standing
repair demands.** Reading `greedy_descent_hitting_time` line by line
(`descent_hitting_time.py:179–222`):

- **First step (`prev is None`):** `nbrs = [v for v in adjacency[current] if v != prev]` with `prev = None` filters nothing (every tuple `!= None`), so `nbrs` is the **full** neighbour list on the very first iteration — there is no exclusion to worry about here at all.
- **Later steps:** by the walk's own construction, whenever `current` was reached from `prev` by an accepted descent step, `delta_map[current] < delta_map[prev]` **strictly** (the step was only taken because `current` was in `candidates = [v for v in nbrs if delta_map[v] < cur_delta]` at the moment `prev` was `current`). So `prev` itself can never satisfy `delta_map[prev] < delta_map[current]` — it is never a viable candidate, whether or not it is present in `nbrs`.
- **The fallback branch** (`if not nbrs: nbrs = list(adjacency[current])`, which reintroduces `prev`) therefore changes nothing about whether `candidates` is empty, for the same reason: `prev` was already disqualified by strict inequality, filtered or not.
- So `candidates == []` (the `trapped=True` condition) is **exactly** equivalent to "no member of the FULL neighbour set `adjacency[current]` has strictly smaller delta than `current`" — which is precisely `is_structural_local_min`'s own `delta_map[v] <= min(nbr_deltas)` test (`trapping_diagnostic_v5.py:234`), computed over the same full `adjacency[v]`.

This holds for every `trapped=True` return point, including the 0-step case
reached directly from `start` (first step, full neighbour set, no filtering
needed) and the case reached after one or more accepted steps (fallback
branch neutralized by the strict-inequality argument above). **Attacked and
held.** This is the correct execution of GD-12's own standing repair ("a
concrete, executed trace ... before that claim is written into frozen
contract text as fact") — the draft's `corrected_equivalence_proof` is not
merely plausible prose this time; it is verifiable and verified.

## PART A — terminal_vertex well-definedness and bit-identical superset (Q2)

**Yes, in all three return branches**, each of which naturally captures
`current` at exactly the point of return: the immediate `delta_E==1` branch
returns before entering the loop (`current` still equals `start`, unmoved);
the `trapped=True` branch returns inside the loop with `current` already set
to the last accepted vertex; the `trapped=False`-via-steps branch returns
immediately after `current = nxt` on the step that reaches `delta_E==1`. A
faithful line-for-line superset (add one field at each return statement,
change nothing else) will be bit-identical on every other field by
construction, and the draft's required "at least 3 independent inputs"
correctly pins one concrete, already-hand-traced case: p=2437, start=(148,37)
→ terminal=(1617,1793), matching `trapping_diagnostic_v5.py`'s own comment
exactly (re-verified directly against that file's lines 265–274, not merely
cited from the draft's prose).

**One gap (PF-4, advisory):** the "at least 3 independent inputs" requirement
does not explicitly require that the chosen inputs collectively exercise all
three return branches (immediate `delta_E==1`, `trapped=True`, `trapped=False`-via-steps).
Only the `trapped=True` (148,37) case is pinned by name. A bug isolated to,
say, the immediate branch's `terminal_vertex` capture (trivial, but still
code) could pass an under-specified 3-input test that happens to hit
`trapped=True` three times.

## PART A — is the delta_E=1 exclusion the right fix, and is it complete? (Q3)

**For PART A's own cross-check: yes, correctly scoped, no under- or
over-coverage.** Every `trapped=False` walk — whether the immediate 0-step
case or a multi-step descent — terminates at a vertex with `delta_map[terminal]==1`,
the global minimum, which trivially satisfies `is_structural_local_min` by
the `<=` definition regardless of neighbours. Excluding **all**
`trapped=False` results (not just the 0-step immediate case) from the
equivalence claim is therefore exactly right, and the draft's actual required
cross-check code (partition by the `trapped` flag alone, check only
`trapped=True`) implements this correctly even though the surrounding prose
in `amendment_scope` illustrates the point using only the immediate-branch
example. This prose imprecision is cosmetic — the operative instruction is
unambiguous — but see PF-1 below for where the same fact (every delta_E=1
vertex is a trivial structural local minimum with no route to a `trapped=True`
walk, ever, including from itself) was **not** correctly carried through into
PART B.

## PART B — required-reuse mechanics (Q4)

**Two separate, both-blocking problems**, distinct from each other:

### PF-1 [BLOCKING] — item 3's basin-accounting convention is false for delta_E=1 local minima; the REQUIRED ACCOUNTING ASSERTION fails deterministically

See the trace above (Q1) and the bottom-line summary. Concretely: for a
genuine `delta_E > 1` structural local minimum `m`, starting a walk **at**
`m` skips the immediate check (`delta_map[m] != 1`), enters the loop with the
full, unfiltered neighbour set (`prev is None`), finds `candidates == []`
(by definition of `m` being a local min), and returns `trapped=True` in 0
steps with `terminal_vertex == m` — so `m` is always a member of its own
basin, exactly as item 3 assumes. But for a `delta_E == 1` vertex `m'`
(which is *also*, trivially, a structural local minimum by the same `<=`
definition), starting a walk at `m'` hits the **unconditional** top-level
check `if delta_map[start] == 1: return trapped=False` — the loop is never
entered at all, so `m'` can **never** be its own `trapped=True` basin member,
and by the same short-circuit no other vertex's walk can pass through `m'`
and still be `trapped=True` there either (reaching `delta_E==1` at any point
converts the walk to `trapped=False` immediately). `m'`'s true basin size
under PART A's corrected accounting is exactly **0**, always, for every
prime.

Item 3 as written ("a local minimum with an EMPTY basin ... is reported with
basin_size == 1, its own start, never as 0 or omitted") does not carve out
this case, and applied literally to `m'` it **double-counts** the same
vertex: once as `m'`'s forced self-basin-of-1, and again inside
`n_trapped_false` (since `m'`'s own walk genuinely is `trapped=False`). The
REQUIRED ACCOUNTING ASSERTION (`sum(len(basin[m]) for all m) + n_trapped_false
== n_vertices`) is therefore guaranteed to **fail by exactly the F_p-rational
locus size** for every one of the four primes (already known and nonzero —
9, 18, 18, 17 per prime, from BATCH-008's own `delta1_locus_cross_check`
data), on any implementation that follows item 3's literal instruction. As
specified, PART B would halt with an explicit error on **every** execution,
never producing the diagnostic it exists to run — the same "required check
that cannot pass, or cannot fail meaningfully" shape as GD-9's dead control,
one layer further in, and squarely GD-12's own "unconditional claim never
checked against a concrete trace," this time inside the very amendment meant
to repair GD-12.

**Required fix:** state explicitly, and trace, that delta_E=1 structural
local minima are excluded from the basin/depth/correlation analysis
entirely (they are not reachable trapping destinations under
`greedy_descent_hitting_time_v2` by construction), OR define their
`basin_size` as 0 (not the item-3 "self" convention), and adjust the
REQUIRED ACCOUNTING ASSERTION's stated formula and expected total
accordingly, before freeze.

### PF-2 [BLOCKING] — "REUSED, not reimplemented" names a non-existent importable unit

`trapping_diagnostic_v5.py` has no `def is_structural_local_min(...)`
anywhere in the file (confirmed by direct read of all 500 lines). The
computation is six inline lines inside `run_diagnostic_for_prime`
(lines 210–239: `nbr_deltas = [delta_map[u] for u in adjacency[v]]; is_min =
bool(delta_map[v] <= min(nbr_deltas))`), and its per-vertex result
(`local_min_flags`) is a local variable that **never appears in the function's
own returned `result` dict** — only the aggregate `structural_local_minimum:
{n_vertices, n_structural_local_min, fraction_structural_local_min}` survives
to any caller. So "the set of structural local minima v5's
trapping_diagnostic_v5.py already computes (REUSED UNCHANGED via import, not
recomputed)" — the exact set PART B's basin construction needs to iterate
over — is not obtainable by import in any form. An Executor following the
letter of the instruction has no path that is not either (a) a fresh,
duplicate six-line reimplementation (contradicting "not reimplemented"), or
(b) an edit to `trapping_diagnostic_v5.py` to also return `local_min_flags`
(forbidden by the draft's own "UNCHANGED, NOT MODIFIED" list). This is the
same species of gap GD-9 and GD-10 both named ("reused" library code whose
actual reuse boundary was never checked to exist), now against a *name* the
draft itself introduced (`is_structural_local_min`) as if it were an existing
symbol.

**Required fix:** either (i) explicitly authorize the minimal, disclosed
duplication of the six-line formula in the new module, named identically
(`is_structural_local_min(v, delta_map, adjacency)`), as a stated,
acknowledged exception rather than left to "an equivalent refactor... state
which and why," or (ii) name the exact new symbol `trapping_diagnostic_v5.py`
would need to additionally return (a change that itself needs disclosing,
since the file is elsewhere declared unchanged).

### PF-3 [BLOCKING] — PART A's halt model and PART B's per-prime precondition language contradict each other

PART A's required corrected cross-check says: "halt with an explicit error,
not a silently-reported disagreement count, on ANY disagreement." This
campaign's own precedent for that exact phrase (`trapping_diagnostic_v5.py`'s
PF-7 fix, "RAISE LOUDLY", which raises `TrappingDiagnosticError` — an
uncaught exception that aborts the entire process, not a per-item skip) reads
as a **global**, run-aborting halt: one disagreement, on one prime, ends the
run before any other prime's PART A cross-check or any PART B computation
ever executes. But PART B's own precondition text reads as a **per-prime**
model: "if PART A's corrected cross-check does not pass for a given prime,
PART B MUST NOT run for that prime and must report why, rather than computing
a basin analysis..." — which presupposes the run continues far enough to
produce a report naming the reason, for that one prime, while (implicitly)
still processing the others. The draft never reconciles these two readings.
Given this campaign's own GD-6 precedent (an unspecified failure-handling
branch produced a mislabeled, unforeseen outcome category, discovered only at
run time), this ambiguity should be resolved explicitly before freeze, not
left for an Executor to resolve silently one way or the other under time
pressure — even though PART A's proof (Q1 above, now independently traced by
this review) makes an actual disagreement unlikely in practice, "unlikely in
practice" is exactly the reasoning GD-4/GD-12 have already shown this
campaign cannot rely on.

**Required fix:** state explicitly whether the corrected cross-check's
per-vertex comparison is computed and its pass/fail recorded **per prime**
(a boolean field, gating only that prime's PART B block, with all four
primes' PART A cross-checks and PART B computations otherwise independent),
or whether any single disagreement anywhere aborts the whole
`RUN-SSIQ-a85692-f` run (in which case PART B's "for that prime" language
should be corrected to reflect that PART B never runs for *any* prime once
one disagreement occurs anywhere).

## PART B — accounting assertions (Q5)

PART A's `n_trapped_true + n_trapped_false == n_vertices` is a legitimate but
weak sanity check: it is close to tautological given the walk always returns
exactly one of `trapped=True`/`trapped=False` per vertex processed exactly
once, but it is not fully vacuous (it would catch an accidental duplicate
iteration, a dict-key collision, or a silently skipped vertex). PART B's
accounting assertion (`sum(len(basin[m])) + n_trapped_false == n_vertices`)
is, by contrast, genuinely informative **in intent** — but is, per PF-1
above, currently guaranteed to fail as specified, which defeats its purpose
entirely rather than merely weakening it.

## Other underspecification (Q6)

### PF-5 [ADVISORY] — internally inconsistent wording for `depth(m)`

"well-defined and positive for every genuine local minimum ... depth==0 is a
legitimate, reportable value, not an error" is self-contradictory word
choice ("positive" normally excludes 0). The underlying formula
(`min(delta_map[u] for u in adjacency[m]) - delta_map[m]`) is correct and
provably non-negative given `is_structural_local_min`'s own `<=` definition
— this is a wording nit, not a computational defect. Recommend "non-negative"
in place of "positive."

### PF-6 [ADVISORY] — top-decile rounding convention unstated

"the fraction of all trapped=True walks captured by the 10% of local minima
with the largest basins" does not state a rounding rule when
`n_local_min` (post-PF-1-fix, excluding delta_E=1 vertices) is not a multiple
of 10. The tie-break rule for the boundary is given, but not how many local
minima constitute "10%" when that is not an integer. Low stakes (a citation
precision issue, not a computation the decision rule depends on), but cheap
to fix now.

---

## Findings summary

| ID | Severity | Location | One-line |
|---|---|---|---|
| PF-1 | BLOCKING | PART B item 3 / accounting assertion | delta_E=1 local minima's basin size is asserted >=1 via self, but is provably always 0 — assertion fails on every prime as specified |
| PF-2 | BLOCKING | PART B reuse instruction | `is_structural_local_min` is not an importable symbol in trapping_diagnostic_v5.py; only an aggregate, not per-vertex flags, survives to its return value |
| PF-3 | BLOCKING | PART A/B failure-handling | "halt on any disagreement" (global) vs. "must not run for that prime" (per-prime) are unreconciled |
| PF-4 | ADVISORY | PART A regression requirement | 3-input equivalence test doesn't require coverage of all 3 return branches |
| PF-5 | ADVISORY | PART B depth() prose | "well-defined and positive" contradicts the immediately following "depth==0 is legitimate" |
| PF-6 | ADVISORY | PART B top-decile | rounding convention for non-multiple-of-10 `n_local_min` unstated |

---

## Required controls / checks before dispatch

- PF-1: state explicitly that delta_E=1 structural local minima are excluded
  from the basin set (or defined with `basin_size == 0`), and correct the
  REQUIRED ACCOUNTING ASSERTION's formula/expected total to match — trace by
  hand against at least one prime's known F_p-rational locus size before
  freeze (BLOCKING).
- PF-2: name the exact reuse mechanism for `is_structural_local_min` /
  "the set of structural local minima" — an explicitly authorized, disclosed
  duplication of the six-line formula, or a named new return field from a
  disclosed change to a file otherwise declared unchanged (BLOCKING).
- PF-3: state explicitly whether PART A's halt-on-disagreement is per-prime
  (recorded boolean, gating only that prime's PART B) or global (aborts the
  whole run), and correct PART B's "for that prime" language to match
  (BLOCKING).
- PF-4/PF-5/PF-6: text-only additions, non-blocking.

## Counterexample or mutation

**PF-1's counterexample, hand-traced against the actual frozen function:**
take any prime's F_p-rational vertex `m'` (e.g. any of the 9 such vertices
for p=2437, all independently confirmed `delta_map[m']==1` in BATCH-005's
archived data). `greedy_descent_hitting_time_v2(adjacency, m', delta_map,
diameter_sentinel)` hits the top-level `if delta_map[start]==1: return
{"trapped": False, "terminal_vertex": m', ...}` before the loop — and by the
same rule, **no other vertex's walk can ever be `trapped=True` at `m'`
either**, since reaching `delta_E==1` at any point converts the walk to
`trapped=False`. `m'`'s true basin (restricted to `trapped=True` walks, as
PART A's corrected cross-check requires) is the empty set, size 0 — directly
falsifying item 3's "no OTHER vertex's walk terminates there, only its own
trivial 1-vertex basin from itself as a start" for this entire vertex class.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
infrastructure (PART A, `asymptotic_claim` null) and a graph-structural
diagnostic (PART B), correctly inherited scope. The relevant baseline is this
campaign's own instrument- and spec-scrutiny discipline (GD-4 through GD-12):
PF-1 is, in a new location, the *exact* failure shape GD-12 itself is — an
unconditional mathematical claim about walk/local-minimum correspondence,
written into contract text without a concrete trace, false for a specific,
non-empty, already-known vertex subset. This review clears the bar GD-12's
own standing repair sets by performing that trace here, before freeze, rather
than after a failed run.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains empty (gradient-existence
screen, not a heuristic-conditional complexity claim) — attacked and held,
consistent with every prior review in this lineage. No finding here
implicates a numbered heuristic; every blocking finding is a
mathematical/reuse/failure-handling precision gap in a diagnostic script, not
in a probabilistic claim about the underlying ECDLP-adjacent problem.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly, inherited); the per-attempt-cost × inverse-success-probability
review does not apply. The `900s`/`0.3` CPU-hour budget is realistic and
generously sized relative to `EXP-SSIQ-58b642`'s own measured graph-build
figures plus O(N) arithmetic on already-committed `delta_map` data for four
primes ≤611 vertices; none of PF-1 through PF-6's required fixes materially
change this (they are all specification-text and accounting-formula
corrections, not new computation). The live concern is evidentiary, not
resource: as specified, PF-1 would make PART B halt with an error on every
execution rather than silently returning a wrong number — a "fails loudly"
outcome, in this campaign's own preferred direction, but still a defect worth
catching before the run rather than after.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis. `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) is not exceeded. `funnel_structure_diagnostic_v6`'s own
`OBJECTIVE_BOUNDARY` restates PART B as a diagnostic, not a claim, correctly
and consistently with the rest of the draft — no decision rule reads PART B's
output. No scope-inflation found. This amendment correctly implements exactly
the two resume actions `DEC-20260806-357b30`'s `next_actions`/`resume_action`
named, on the same four primes, at zero new search cost.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` (inherited unchanged)
remains correctly reasoned — a direct instrument-level gradient-existence
screen and a graph-structural diagnostic, not a proof-oriented proposal.
Attacked and held, same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v6.yaml` as read in the
working tree, `status: draft`: **PART A's central mathematical claim is
correct**, independently traced by this review directly against the frozen,
unchanged `greedy_descent_hitting_time` — for every `trapped=True` walk, the
terminal vertex is unconditionally a genuine structural local minimum over
its full neighbour set, including through the first-step and multi-edge
fallback edge cases, and the exclusion of all `trapped=False` walks from the
corrected cross-check is exactly right, not under- or over-covering. **PART B
introduces a new defect of the same shape as the one this whole amendment
exists to fix**: its basin-accounting convention (item 3) is false for every
delta_E=1 structural local minimum, guaranteeing its own REQUIRED ACCOUNTING
ASSERTION fails on every prime as specified (PF-1, blocking); its "reused,
not reimplemented" instruction names a computation
(`is_structural_local_min`) that is not actually importable from
`trapping_diagnostic_v5.py`, only obtainable as a duplicate or via an
undisclosed change to a file declared unchanged (PF-2, blocking); and the
draft leaves an unreconciled contradiction between a global, run-aborting
halt model (PART A's own wording) and a per-prime continue-and-report model
(PART B's own wording) for the identical failure event (PF-3, blocking).
Three advisory items (PF-4, PF-5, PF-6) round out the review. None of these
findings requires redesigning either part's mechanism, and all are fixable at
zero new search cost, consistent with this amendment's own budget.

## Next concrete action

Coordinator: before `status: approved` / setting `frozen_at`, require the
amendment text to (1) resolve PF-1 by explicitly excluding delta_E=1
structural local minima from the basin/depth/correlation analysis (or
defining their basin_size as 0) and correcting the REQUIRED ACCOUNTING
ASSERTION accordingly, traced by hand against at least one prime's known
F_p-rational locus size; (2) resolve PF-2 by naming the exact, disclosed
mechanism for obtaining per-vertex `is_structural_local_min` values/"the set
of structural local minima" (an authorized scoped duplication, or a named new
return field with the corresponding disclosed change to the "unchanged" file
list); (3) resolve PF-3 by stating explicitly whether the corrected
cross-check's halt is per-prime or global, and correcting PART B's "for that
prime" language to match; (4) apply PF-4/PF-5/PF-6 as text-only additions.
Re-verify PF-1, PF-2, and PF-3's specific traces once the fixes are added,
before freeze, per this campaign's own standing GD-12 repair: any
mathematical equivalence or accounting claim in review or contract prose gets
a concrete, executed trace before it is trusted, applied here uniformly
(including to this review's own PF-1, whose counterexample above is a
genuine hand-trace against the real frozen code, not an assertion).

## Overall verdict

**DO-NOT-FREEZE.** Blocking, in priority order:

1. **[BLOCKING]** PF-1 — PART B's basin-accounting convention for
   delta_E=1 structural local minima is mathematically false and would make
   the REQUIRED ACCOUNTING ASSERTION fail on every prime as specified,
   defeating the diagnostic's own purpose.
2. **[BLOCKING]** PF-2 — the "REUSED, not reimplemented" instruction for
   `is_structural_local_min` names a computation with no actual importable
   form in `trapping_diagnostic_v5.py`.
3. **[BLOCKING]** PF-3 — PART A's global halt-on-disagreement wording and
   PART B's per-prime continue-and-report wording describe the same failure
   event two incompatible ways.

PF-4, PF-5, PF-6 are advisory and do not block this dispatch on their own.
PART A's own central mathematical claim (the reason this amendment exists)
is independently confirmed correct by this review's own hand trace and
should be preserved unchanged through any revision that addresses PF-1–PF-3.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v6
  task_id: TASK-20260806-1deeb3
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v6.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), read directly from the working tree: PART A
    fixes GD-12 by superseding (never editing) dht.greedy_descent_hitting_time
    with greedy_descent_hitting_time_v2, which exposes the walk's terminal
    vertex, and corrects the trapped-vs-structural cross-check to compare
    trapped=True walks against is_structural_local_min(terminal), excluding
    trapped=False (delta_E=1 success) walks entirely; PART B is a new,
    PART-A-dependent funnel-structure/basin-size diagnostic over the same
    four primes (2437, 3889, 5737, 7333).
  objections:
    - "PF-1 [BLOCKING]: PART B item 3's convention that an empty basin is always reported with basin_size==1 ('its own start') is mathematically false for every delta_E=1 structural local minimum. is_structural_local_min trivially flags all delta_E=1 vertices True (delta=1 is the global minimum), but greedy_descent_hitting_time_v2's own inherited top-level short-circuit (if delta_map[start]==1: return trapped=False) means a delta_E=1 local minimum can never receive a trapped=True walk from ANY vertex, including itself -- unlike every delta_E>1 local minimum, whose 0-step self-walk IS trapped=True (full neighbour set on the first step, prev is None, candidates empty by definition of being a local min). A literal implementation of item 3 double-counts these vertices (forced basin_size=1, plus counted again in n_trapped_false), making the REQUIRED ACCOUNTING ASSERTION (sum(len(basin[m])) + n_trapped_false == n_vertices) fail by exactly the F_p-rational locus size (9/18/18/17 per prime, already known from BATCH-008 data) on every prime, every run, as specified -- the diagnostic could never complete as written."
    - "PF-2 [BLOCKING]: the 'REUSED, not reimplemented' instruction for is_structural_local_min / 'the set of structural local minima' names a symbol that does not exist as an importable unit in trapping_diagnostic_v5.py (confirmed by reading all 500 lines directly). The computation is six inline lines inside run_diagnostic_for_prime, and its per-vertex output (local_min_flags) is a local variable never included in that function's own returned dict -- only the aggregate n_structural_local_min/fraction_structural_local_min survive. An Executor following the letter of the instruction has no path that is not either an undisclosed reimplementation or an undisclosed edit to a file the draft elsewhere declares unchanged -- the same reuse-mechanics gap GD-9 and GD-10 both named."
    - "PF-3 [BLOCKING]: PART A's 'halt with an explicit error ... on ANY disagreement' (this campaign's own PF-7/'RAISE LOUDLY' precedent reads this as a global, run-aborting exception) and PART B's 'if it does not pass for a given prime, PART B must not run for that prime and must report why' (which presupposes per-prime continuation) describe the same failure event under two incompatible failure-handling models, and the draft never states which applies -- the same shape of underspecified failure-handling branch GD-6 already burned this campaign on once."
    - "PF-4 [ADVISORY]: the REQUIRED EQUIVALENCE REGRESSION's 'at least 3 independent inputs' does not explicitly require coverage of all three of greedy_descent_hitting_time_v2's return branches (immediate delta_E==1, trapped=True, trapped=False-via-steps) -- only the trapped=True (148,37) case is pinned by name."
    - "PF-5 [ADVISORY]: depth(m) is described as 'well-defined and positive for every genuine local minimum' immediately followed by 'depth==0 is a legitimate, reportable value, not an error' -- internally contradictory word choice ('positive' normally excludes 0); the formula itself is correct and provably non-negative."
    - "PF-6 [ADVISORY]: the top-decile concentration's rounding convention when n_local_min is not a multiple of 10 is unstated (the tie-break rule for the boundary IS stated, but not how many local minima constitute '10%' in that case)."
  required_controls:
    - "PF-1: state explicitly that delta_E=1 structural local minima are excluded from the basin/depth/correlation analysis (or that their basin_size is defined as 0, not the item-3 self-convention), and correct the REQUIRED ACCOUNTING ASSERTION's formula/expected total to match, traced by hand against at least one prime's known F_p-rational locus size before freeze -- BLOCKING."
    - "PF-2: name the exact, disclosed reuse mechanism for is_structural_local_min / the set of structural local minima -- an explicitly authorized scoped duplication of the six-line formula, or a named new return field via a disclosed change to a file otherwise declared unchanged -- BLOCKING."
    - "PF-3: state explicitly whether the corrected cross-check's halt-on-disagreement is per-prime (a recorded boolean gating only that prime's PART B) or global (aborts the whole run before any prime's PART B executes), and correct PART B's 'for that prime' language to match -- BLOCKING."
    - "PF-4/PF-5/PF-6: text-only additions, non-blocking."
  counterexample_or_mutation: >-
    PF-1: take any F_p-rational vertex m' for a given prime (e.g. one of the 9
    such vertices for p=2437, all with delta_map[m']==1 in BATCH-005's
    archived data). greedy_descent_hitting_time_v2(adjacency, m', delta_map,
    diameter_sentinel) hits the top-level "if delta_map[start]==1: return
    trapped=False" before the loop -- so m''s own self-walk is NOT trapped=True,
    contradicting item 3's "its own trivial 1-vertex basin from itself as a
    start." By the same top-level short-circuit, no OTHER vertex's walk can be
    trapped=True at m' either (any walk reaching delta_E==1 becomes
    trapped=False at that instant), so m''s true basin under the corrected,
    trapped=True-only cross-check is the empty set, size 0 -- directly
    falsifying item 3's "no OTHER vertex's walk terminates there, only its own
    trivial 1-vertex basin" for this entire, already-known-nonzero vertex
    class.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline is this
    campaign's own instrument- and spec-scrutiny discipline (GD-4 through
    GD-12): PF-1 is, in a new location, the exact failure shape GD-12 itself
    is -- an unconditional mathematical claim about walk/local-minimum
    correspondence, written into contract text without a concrete trace,
    false for a specific, non-empty, already-known vertex subset -- caught
    here, before freeze, by performing that trace directly against the frozen
    code rather than trusting the draft's own prose. PART A's own central
    claim, by contrast, is independently confirmed correct by the same
    tracing discipline applied in the other direction.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; every blocking finding is a mathematical/reuse/failure-handling precision gap in diagnostic code."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is realistic and generously sized; none of PF-1 through PF-6's required fixes materially change this (all are specification-text and accounting-formula corrections, not new computation)."
    - "The live concern is evidentiary, not resource: as specified, PF-1 would make PART B halt with an explicit error on every execution rather than silently returning a wrong number -- a loud rather than silent failure, in this campaign's preferred direction, but still worth catching before the run rather than after."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded. No scope-inflation found."
    - "funnel_structure_diagnostic_v6's OBJECTIVE_BOUNDARY correctly restates PART B as a diagnostic, not a claim, consistent with the rest of the draft -- no decision rule reads PART B's output."
    - "This amendment correctly implements exactly the two resume actions DEC-20260806-357b30's next_actions/resume_action named, on the same four primes, at zero new search cost -- independently reconfirmed here."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen and a graph-structural diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v6.yaml as read in
    the working tree, status: draft: PART A's central mathematical claim
    (trapped=True implies is_structural_local_min(terminal_vertex),
    unconditionally) is CORRECT, independently traced by this review directly
    against the frozen, unchanged greedy_descent_hitting_time, including the
    first-step and multi-edge fallback edge cases -- GD-12's own standing
    repair correctly applied this time. PART B introduces a new defect of the
    identical shape: its basin-accounting convention is false for every
    delta_E=1 structural local minimum, guaranteeing its own required
    accounting assertion fails on every prime as specified (PF-1, blocking);
    its reuse instruction names a non-importable symbol (PF-2, blocking); and
    it leaves an unreconciled contradiction between a global and a per-prime
    failure-handling model for the identical event (PF-3, blocking). Three
    advisory items (PF-4, PF-5, PF-6) round out the review. None require
    redesigning either part's mechanism; all are fixable at zero new search
    cost.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text to (1) resolve PF-1 by excluding delta_E=1 structural local minima
    from the basin analysis (or defining their basin_size as 0) and
    correcting the accounting assertion accordingly; (2) resolve PF-2 by
    naming the exact, disclosed mechanism for obtaining per-vertex
    is_structural_local_min values; (3) resolve PF-3 by stating explicitly
    whether the corrected cross-check's halt is per-prime or global; (4)
    apply PF-4/PF-5/PF-6 as text-only additions. Re-verify PF-1 through PF-3's
    specific traces once fixed, before freeze, per this campaign's own
    standing GD-12 repair.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Hand-traced greedy_descent_hitting_time's control flow line by line
    against descent_hitting_time.py (all branches: immediate delta_E==1,
    first-step prev-is-None, trapped=True general step, multi-edge fallback,
    trapped=False-via-steps) and cross-checked each against
    trapping_diagnostic_v5.py's is_structural_local_min inline formula (line
    234). Traced the delta_E=1-vertex self-walk case explicitly (the PF-1
    counterexample) against the same frozen short-circuit. Read
    trapping_diagnostic_v5.py in full (500 lines) to confirm no standalone
    is_structural_local_min function or per-vertex-flag-returning entry point
    exists. Read ols_hardened.py in full to confirm the supersede-by-addition
    pattern this draft claims to follow. No graph built, no delta_E search
    run, no file written outside this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml itself)
    and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
