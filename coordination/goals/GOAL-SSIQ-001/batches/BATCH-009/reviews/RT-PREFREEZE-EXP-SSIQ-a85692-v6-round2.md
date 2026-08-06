# RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2 — Second pre-freeze Red Team review
# of the REVISED DRAFT amendment `specification_v6.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-009

**Reviews `experiments/EXP-SSIQ-a85692/specification_v6.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED`, `pre_freeze_review
.round2_report: null` (this report), as committed at snapshot `6ae7847f`
("GOAL-SSIQ-001 BATCH-009: EXP-SSIQ-a85692 v6 draft revised after
DO-NOT-FREEZE (round 1)"), parented on `e78309b4` (the round-1-reviewed
draft).** `git status --short` on the file confirmed clean against this
commit. Per this task's operating rules, only this Coordinator-committed
snapshot is treated as durable input; this report changes nothing under
`experiments/EXP-SSIQ-a85692/` or any ledger record.

Read in full per the launching task: `AGENTS.md`, `CLAUDE.md`;
`RT-PREFREEZE-EXP-SSIQ-a85692-v6.md` (the round-1 report, DO-NOT-FREEZE,
PF-1/PF-2/PF-3 blocking, PF-4/PF-5/PF-6 advisory) in full;
`RT-PREFREEZE-EXP-SSIQ-a85692-v5-round2.md` (the format/caliber precedent,
including PF-9's "a fix that looked right in prose is not exempt from being
traced" standard) in full; the current `specification_v6.yaml` in full
(all six `pfN_summary` entries, `inputs.gd12_fix_v6`,
`inputs.funnel_structure_diagnostic_v6`, `required_artifacts_note`); the
frozen, unchanged `experiments/EXP-SSIQ-58b642/implementation
/descent_hitting_time.py` in full (`greedy_descent_hitting_time`, lines
179–222, and the walk loop's exact ordering of the trapped=True check
versus the post-step `delta_map[current]==1` check); the frozen
`experiments/EXP-SSIQ-a85692/implementation/trapping_diagnostic_v5.py` in
full (500 lines — confirmed `build_graph_for_prime` and
`load_archived_prime_data` are genuinely standalone, module-level functions;
confirmed the exhaustive cross-check's `run_diagnostic_for_prime` never
raises on `crosscheck_pass=False`, only records it); `git log`/`git status`
confirming both files are frozen with no working-tree changes.
**Programmatically queried, not sampled from prose**:
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json`'s
`descent_metrics.per_prime[p].greedy_trapped_fraction` for all four primes;
`experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-e/trapping_diagnostic.json`
and `trapped_vs_structural_crosscheck.json`; `experiments/EXP-SSIQ-58b642
/runs/RUN-SSIQ-58b642-a/raw-result.json`'s `correctness_gates
.delta1_locus_cross_check` (the F_p-rational locus sizes 9/18/18/17); and
`compute_delta_e.py`'s `descent_metrics` block (lines 820–860) to confirm
`greedy_trapped_fraction` is computed on the identical seed-20260805 rebuilt
graph and real `delta_map` that PART A/B's own reuse mechanism will
reproduce byte-for-byte.

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
    reviewer in this lineage, including the round-1 review of this same
    draft; it does not upgrade the campaign's evidence tier by itself.
```

---

## Bottom line up front

**This draft should still NOT be frozen as written.** Round 1's three
blocking findings are genuinely, correctly resolved on their own terms:
PF-1's basin-accounting fix is mathematically airtight (independently
re-derived from first principles against the frozen walk code, including
the specific scenario the launching task asked me to stress-test — a
delta_E>1 walk cannot "pass through" a delta_E=1 vertex and terminate
elsewhere, because the loop's post-step check halts the walk the instant it
reaches delta_E=1, before any subsequent candidate-emptiness test can fire);
PF-2's reuse mechanism is real (`build_graph_for_prime` and
`load_archived_prime_data` are genuinely standalone, module-level,
independently confirmed importable by direct read); and PF-3's headline
fix (crosscheck_pass as a per-prime, never-aborting boolean) is an accurate
description of what `trapping_diagnostic_v5.py` actually does, confirmed by
direct code read — its `run_diagnostic_for_prime` computes
`crosscheck_pass` and attaches a `specification_defect_note` but never
raises on disagreement anywhere in that path.

But **the revision introduces two new defects while fixing PF-3's own
ambiguity**, both found by tracing the *current* draft text against the
actual frozen code and actual archived data, not by re-reading either
report's prose — the exact discipline this task's brief and the v5-round2
precedent both demand:

1. **PF-7 [BLOCKING, NEW]: PART B's own REQUIRED ACCOUNTING ASSERTION
   reintroduces PF-3's exact global-vs-per-prime ambiguity, one level
   deeper.** It is described as "a GLOBAL, run-aborting check for that
   prime's computation" — a phrase that names two different failure-handling
   models in five words. Nothing in the draft states whether a basin-
   accounting-assertion failure for one prime destroys the diagnostic's
   entire output for all four primes, or only that one prime's.
2. **PF-8 [BLOCKING, NEW]: the "traced by hand" numeric justification for
   the corrected accounting assertion is false, confirmed by direct query
   against already-archived data.** The draft asserts, with confidence,
   that `n_trapped_false` for p=2437 equals "the F_p-rational locus size 9"
   and that `sum(len(basin[m]))` should equal 194. The real archived
   `descent_metrics.per_prime["2437"].greedy_trapped_fraction` (0.8374...,
   computed on the identical seed-20260805 rebuilt graph and real
   `delta_map` PART A/B will reuse) implies `n_trapped_false = 33`, not 9,
   and `sum(len(basin[m])) = 170`, not 194 — because `n_trapped_false`
   counts every vertex whose walk *eventually* reaches delta_E=1 (zero or
   more steps), not merely the vertices that trigger the immediate
   short-circuit. This conflates round 1's report of the *old* bug's
   overcount magnitude (which genuinely was the locus size, 9/18/18/17)
   with a prediction of the *new* scheme's `n_trapped_false` value — a
   categorically different quantity — and misattributes the resulting false
   claim to "the round-1 reviewer's own trace," which round 1's report never
   made.

Neither finding requires redesigning either part's mechanism, and both are
fixable at zero new search cost. PF-8 is non-gating on its own (the draft
hedges "the Executor's own run reports the actual figures, not this
contract's prediction"), but a confidently-stated, falsified numeric claim
left in frozen contract text is exactly the failure mode GD-12's own standing
repair exists to catch, and risks a false "something's wrong" alarm burning a
review cycle when the real run reports 33 instead of 9.

---

## (1) PF-1's fix: is the basin-accounting convention now a genuine partition?

**Yes — independently re-derived from the frozen walk code's actual control
flow, not the draft's prose, including the specific stress case the
launching task named.**

Tracing `greedy_descent_hitting_time`'s loop (lines 198–222) by induction on
`current`:

- **Invariant at loop entry:** `delta_map[current] != 1` always. Base case:
  the pre-loop check (`if delta_map[start] == 1: return trapped=False`)
  already excludes `start` with `delta_map[start]==1` from ever entering the
  loop. Inductive step: the ONLY way `current` is reassigned inside the loop
  is via `current = nxt; steps += 1`, immediately followed by
  `if delta_map[current] == 1: return trapped=False` — so any vertex with
  delta 1 reached by a step returns **before** the loop's next top-of-loop
  candidate check ever runs. The loop can therefore never be entered with
  `delta_map[current] == 1`.
- **Consequence for the trapped=True check:** `candidates = [v for v in nbrs
  if delta_map[v] < cur_delta]` and its emptiness test always run on a
  `current` with `delta_map[current] > 1` (by the invariant above). So
  `trapped=True` can **only** fire at a vertex with `delta_map > 1` — exactly
  the draft's "basin-eligible" condition. There is no code path by which a
  `trapped=True` return can have `terminal_vertex` at a delta_E=1 vertex.
- **The specific scenario the launching task asked me to check** — "a walk
  started at a non-local-minimum vertex passes THROUGH a delta_E=1 vertex
  before terminating elsewhere" — **does not exist as a code path.** The
  moment `current` becomes a delta_E=1 vertex (via a step), the function
  returns immediately with `trapped=False`; it never re-enters the loop to
  evaluate that vertex's own candidate set, so there is no way for a walk to
  visit a delta_E=1 vertex and then continue past it to a different
  terminus. Every walk that ever reaches delta_E=1 halts there, with
  `trapped=False`, unconditionally.
- **Self-basin membership**, re-derived directly (not merely re-reading the
  draft's own argument): for `m` with `is_structural_local_min(m)` and
  `delta_map[m] > 1`, starting at `m`: the pre-loop check doesn't fire
  (`delta_map[m] != 1`); `prev is None` so `nbrs` is the full, unfiltered
  neighbour set on the first iteration; `candidates` is empty by definition
  of `m` being a structural local minimum; the function returns
  `trapped=True`, `steps=0`, with `current` (hence `terminal_vertex`)
  unchanged at `m`. So every basin-eligible `m` is unconditionally a member
  of its own basin, `basin_size(m) >= 1` always — **confirmed**, not merely
  asserted.

**Partition check, confirmed exhaustive and non-overlapping:** every vertex,
as a start, is either (a) `trapped=True`, in which case its terminal vertex
is unconditionally basin-eligible (by the invariant above) and it
contributes to exactly one basin's multiset, or (b) `trapped=False`, in
which case it is counted in `n_trapped_false` and contributes to no basin.
These are mutually exclusive and jointly exhaustive by construction of the
function's own return branches (there is no third outcome). **PF-1's fix is
CONFIRMED HOLDING** — the required accounting assertion is now a genuine,
non-vacuous partition check that will pass on real data, unconditionally, as
a mathematical fact independent of what the specific numeric values turn
out to be (see PF-8 below for where the draft's own illustration of those
values goes wrong).

## (2) PF-2's fix: are the two "genuinely imported" functions actually what the draft claims?

**Yes, directly confirmed by reading all 500 lines of
`trapping_diagnostic_v5.py`.**

- `build_graph_for_prime(p, seed)` (lines 133–148): a standalone,
  module-level `def`, no closure over any enclosing function's local state,
  calling only `big.seed_j_invariant`, `big.verify_seed_supersingular`,
  `big.build_graph_bfs` (all imported, unchanged) and raising
  `TrappingDiagnosticError` on a failed supersingularity check. Returns
  `(g, seed_info)` exactly as the draft states. **Genuinely importable,
  confirmed.**
- `load_archived_prime_data(raw_result_path, prime)` (lines 102–130):
  likewise a standalone, module-level `def`. Returns a dict with keys
  `delta_map` (already key-converted via `tuple(json.loads(key_str))`),
  `archived_n_vertices`, `archived_n_resolved`,
  `archived_greedy_trapped_fraction` — matching the draft's description
  ("returns delta_map with PF-4's key round-trip already applied, plus
  archived_n_vertices/archived_n_resolved") exactly, including the
  round-trip collision guard (raises `TrappingDiagnosticError` if the key
  conversion is not injective). **Genuinely importable, confirmed.**
- `is_structural_local_min`, the coverage assertion, and the graph-rebuild
  verification: re-confirmed **not** separately importable — they remain six
  inline lines (formula at line 234: `is_min = bool(delta_map[v] <=
  min(nbr_deltas))`) and ~15 lines respectively, inside
  `run_diagnostic_for_prime`, with no standalone entry point. The draft's
  "AUTHORIZED, DISCLOSED DUPLICATE" instruction is the correct and only
  available path, and its stated formula matches the real inline formula
  exactly (`delta_map[v] <= min(delta_map[u] for u in adjacency[v])`
  vs. the real `delta_map[v] <= min(nbr_deltas)` where `nbr_deltas =
  [delta_map[u] for u in adjacency[v]]` — identical).
- **One minor, non-blocking completeness gap:** the real inline formula's
  six lines also include a PF-7 "RAISE LOUDLY" guard on a missing-neighbour
  `delta_map` entry (lines 224–232). The draft's stated duplicate formula
  (a bare `<=`/`min` expression) does not explicitly restate this guard as
  part of what gets duplicated, even though the required coverage assertion
  (also duplicated, per the same paragraph) makes the guard's trigger
  condition structurally unreachable either way — the same reasoning
  `trapping_diagnostic_v5.py`'s own PF-7 comment already gives ("this
  batch's data has full coverage... never a legitimate data gap"). Not
  blocking; worth one clause for completeness (advisory, **PF-10**).

**PF-2's fix is CONFIRMED HOLDING.** An Executor following this instruction
has an unambiguous, fully-specified path with no undisclosed reimplementation
and no undisclosed edit to a file declared unchanged.

## (3) PF-3's fix: does the per-prime `crosscheck_pass` model actually match the code, and does a new internal contradiction appear?

### The headline claim: CONFIRMED HOLDING against the real code

Read `run_diagnostic_for_prime` end to end (lines 161–441) specifically
looking for any `raise` triggered by `crosscheck_pass == False`. There is
none: the loop at lines 311–322 computes `walk_trapped`/`structural` per
vertex and appends to `disagreements`; `crosscheck_pass = bool(len
(disagreements) == 0)` is computed and attached to `crosscheck_result`
along with a `specification_defect_note`, and the function simply returns
`result` — no exception path exists for a disagreement anywhere in this
function. `main()` (lines 452–496) writes both output files and prints a
summary line regardless of `crosscheck_pass`'s value, for all four primes.
Directly confirmed against `RUN-SSIQ-a85692-e`'s own archived
`trapped_vs_structural_crosscheck.json`: `crosscheck_pass: False` for **all
four** primes (93/203, 138/324, 234/478, 267/611 disagreements), and the run
completed and archived normally — it did not abort. **The draft's claim that
`trapping_diagnostic_v5.py` "did NOT literally implement" a halt, despite its
own frozen spec text saying it would, is accurate**, and PART A's
`crosscheck_pass` design (a per-prime boolean, never aborting) is a
faithful, working precedent, not a hopeful description.

### PF-7 [BLOCKING, NEW]: PART B's own accounting assertion reintroduces the exact ambiguity PF-3 was meant to close

Quoting the draft's `funnel_structure_diagnostic_v6` item 2 verbatim:

> "...halt with an explicit error on any mismatch -- this is now a
> **GLOBAL, run-aborting check for that prime's computation** (distinct
> from PART A's per-prime crosscheck_pass, which never aborts)..."

This is internally self-contradictory in the same way round 1's PF-3 was:
"GLOBAL" and "for that prime's computation" name two different scopes.
PART A's own use of the identical phrase ("this specific assertion is a
global, run-aborting check -- a violation here means the walk was not run
on every vertex exactly once, **a bug independent of any prime-specific
data question**") is unambiguous there because its own justification
explicitly rules out per-prime scoping. PART B's sentence gives no such
disambiguating justification and instead appends language ("for that
prime's computation") that reads as scoping it *to* one prime — the exact
opposite of PART A's own definition of "global" two paragraphs earlier in
the same document.

This is not a stylistic nit: PART B's own precondition model (crosscheck_pass
gates only that prime's PART B block, "while proceeding normally for every
other prime") **requires** some form of per-prime isolation in the
implementation (at minimum, the crosscheck_pass-gated skip must not itself
crash the whole process). Whether that same isolation also catches a basin-
accounting-assertion failure (making it, despite the "GLOBAL" label,
effectively per-prime too) or whether the accounting assertion is
deliberately left outside that isolation (so it genuinely aborts the whole
run, including primes not yet processed, and discards any already-computed
results for primes that DID pass) is never stated. This is structurally the
same failure-handling underspecification GD-6 already burned this campaign
on, and the same species of defect PF-3 was raised to close — now relocated
one level deeper, inside PART B's own fix text, rather than resolved.

In practice this assertion should never fire (PF-1's fix makes it a genuine
tautological partition, confirmed in (1) above), so the ambiguity is
currently "unlikely to matter" — but that is exactly the reasoning this
campaign's own GD-4/GD-12 precedent has already shown it cannot rely on, and
the identical reasoning round 1 used to justify blocking the original PF-3.

**Required fix:** state explicitly whether the basin-accounting assertion's
halt aborts (a) only that prime's PART B computation (with the other three
primes' results still computed and written to the output artifacts), or
(b) the entire `RUN-SSIQ-a85692-f` process before any output is written —
and, if (a), state that the per-prime isolation already required for
`crosscheck_pass` gating is the same mechanism that catches this assertion
too, so a reader does not have to infer it.

## (4) PF-4, PF-5, PF-6's fixes: confirmed applied, plus one new numeric-fidelity defect (PF-8)

### PF-4: CONFIRMED APPLIED, no gap found

The "at least 3 independent inputs" requirement in `gd12_fix_v6` now
explicitly requires collective coverage of all three of
`greedy_descent_hitting_time_v2`'s return branches (immediate delta_E==1,
trapped=True, trapped=False-via-steps), names the (148,37)/p=2437 case for
the trapped=True branch, and requires `execution_report.yaml` to state which
branch each input exercises. Matches round 1's required fix exactly; no new
gap found.

### PF-5: CONFIRMED APPLIED, no gap found

"provably NON-NEGATIVE, not 'positive'" replaces the self-contradictory
original wording; the accompanying explanation (depth==0 is legitimate for a
tied neighbour, which the non-backtracking walk's tie-break rule can still
enter and terminate at) is independently confirmed correct: the walk's
`candidates = [v for v in nbrs if delta_map[v] < cur_delta]` uses **strict**
`<`, so a neighbour tied at the exact minimum delta is correctly excluded
from `candidates` (matching `is_structural_local_min`'s `<=` convention) —
depth 0 is a real, reachable, non-error case. No new gap found.

### PF-6: CONFIRMED APPLIED, verified against real archived data as the task directed

`k = max(1, ceil(0.1 * n_basin_eligible))` is now explicit and deterministic.
Checked against the actual basin-eligible counts these four primes will
produce (`n_structural_local_min` from `RUN-SSIQ-a85692-e`'s archived
`trapping_diagnostic.json`, minus the archived F_p-rational locus size from
`RUN-SSIQ-58b642-a`'s `correctness_gates.delta1_locus_cross_check`):

| prime | n_structural_local_min | F_p-rational locus | n_basin_eligible | k = max(1, ceil(0.1·n)) |
|---|---|---|---|---|
| 2437 | 95 | 9 | 86 | 9 |
| 3889 | 132 | 18 | 114 | 12 |
| 5737 | 194 | 18 | 176 | 18 |
| 7333 | 287 | 17 | 270 | 27 |

All four are well-defined, strictly positive integers with no boundary
behaviour (`n_basin_eligible` is never 0 or small enough for `max(1, ...)`
to matter on this batch's actual data). **No issue found for the primes
actually in scope.** One purely theoretical, non-blocking edge case
(`n_basin_eligible == 0`, not exercised by any of the four primes) is noted
as advisory only, **PF-11**: the top-decile fraction's denominator
(`n_trapped_true`) would also be forced to 0 in that hypothetical case,
making "the fraction those k=1 minima capture" divide-by-zero over a
non-existent minimum — worth one defensive clause if this diagnostic is ever
reused on a prime with a near-empty basin-eligible set, but not reachable
here.

### PF-8 [BLOCKING, NEW]: the accounting assertion's own "traced by hand" numeric justification is false

The draft's `funnel_structure_diagnostic_v6` item 2 states:

> "...so this assertion is a genuine partition check, not vacuous, and **per
> the round-1 reviewer's own trace SHOULD now hold exactly** (traced by hand
> for p=2437: 203 total vertices, **n_trapped_false expected == the
> F_p-rational locus size 9** per BATCH-005's archived data, so
> **sum(len(basin[m])) is expected == 194** -- the Executor's own run
> reports the actual figures, not this contract's prediction)."

Two things are wrong here, both directly checkable against already-archived
data:

1. **Round 1's report never made this trace.** Round 1's report cites
   "9/18/18/17 per prime" exactly once, in a completely different context:
   as the size of the *old*, broken accounting scheme's overcount (each
   delta_E=1 vertex was double-counted by exactly one, so the total overcount
   equalled the locus size). It never claims, and never traced, that the
   *corrected* scheme's `n_trapped_false` should equal that same number.
   Attributing this specific (and false) claim to "the round-1 reviewer's
   own trace" is a fabricated citation to a prior review's authority.
2. **The number itself is false, confirmed by direct query.** `n_trapped_false`
   counts every vertex whose walk *ever* reaches a delta_E=1 vertex — either
   immediately (the F_p-rational start, the only case the old bug's overcount
   was about) or after one or more descent steps (a delta>1 start whose walk
   descends all the way to delta_E=1). Directly queried
   `RUN-SSIQ-a85692-b/raw-result.json`'s `descent_metrics.per_prime["2437"]
   .greedy_trapped_fraction = 0.8374384236453202` — computed by
   `dht.run_population(..., "greedy", ...)` on the same seed-20260805
   rebuilt graph and the same real `delta_map` that PART A/B's reuse
   mechanism will load, i.e. the exact quantity PART A's cross-check will
   reproduce byte-for-byte once `greedy_descent_hitting_time_v2` exists.
   `(1 - 0.8374384236453202) * 203 = 33.0` exactly (an exact integer, not a
   rounding artefact) — **not 9.** Consequently `sum(len(basin[m])) =
   203 - 33 = 170`, **not 194.** The same computation for the other three
   primes gives `n_trapped_false = 90, 86, 91` against the draft's implied
   `18, 18, 17` — every one wrong by a large factor (5x, 4.8x, 5.4x).

**Consequence, scoped honestly:** this does **not** affect the correctness of
the accounting *mechanism* — PF-1's fix (see (1) above) makes the assertion
hold as a genuine partition regardless of the specific numbers involved, and
the draft's own hedge ("the Executor's own run reports the actual figures,
not this contract's prediction") means no code path treats "194" or "9" as a
required value to halt on. This is not a PF-1-style correctness defect. But
it is a confidently-stated, falsified numerical claim, embedded as fact
inside the very paragraph meant to build confidence that the corrected
assertion "SHOULD now hold exactly," in frozen contract text — exactly the
shape of unconditional claim GD-12's own standing repair exists to prevent,
independent of whether it happens to gate a check. Left as written, it risks
a false "something is wrong" alarm during `RUN-SSIQ-a85692-f`'s own review,
when the real run reports 33/90/86/91 against a written expectation of
9/18/18/17 — a mismatch a future reviewer would have to re-derive from
scratch (as this review just did) to determine is not, in fact, a defect.

**Required fix:** either (a) replace the specific numbers with the correct
ones (33/170 for p=2437, and the corresponding correct pairs for the other
three primes, computed the same way), explicitly sourced from
`descent_metrics.per_prime[p].greedy_trapped_fraction` rather than the
F_p-rational locus size, or (b) remove the illustrative numeric prediction
entirely and state only that the assertion holds by construction as a
genuine partition (proved in (1) above), without predicting specific values
that were never actually traced. Either is a zero-new-search, text-only fix.

---

## Findings summary

| ID | Status this round | Location | One-line |
|---|---|---|---|
| PF-1 | **CONFIRMED HOLDING** | PART B basin definition | Basin-eligible = {m : local_min(m) AND delta(m)>1} is a genuine, exhaustive, non-overlapping partition — independently re-derived, including the "passes through delta_E=1" stress case, which is not a reachable code path |
| PF-2 | **CONFIRMED HOLDING** | PART B reuse split | Both named import targets are genuinely standalone, module-level, confirmed by direct read; duplication targets are correctly identified as the only available path |
| PF-3 | **CONFIRMED HOLDING (headline), NEW GAP FOUND (PF-7)** | PART A crosscheck_pass | The per-prime, never-aborting model matches the real code exactly — but PART B's OWN accounting assertion reintroduces the identical global-vs-per-prime ambiguity PF-3 was raised to resolve |
| PF-4 | CONFIRMED APPLIED | PART A regression test | Branch coverage now required explicitly; no gap |
| PF-5 | CONFIRMED APPLIED | PART B depth() wording | "non-negative" replaces the self-contradiction; depth==0/tied-neighbour case independently reconfirmed correct |
| PF-6 | CONFIRMED APPLIED | PART B top-decile | Deterministic rounding formula checked against real archived basin-eligible counts (86/114/176/270) for all four primes — well-defined throughout |
| PF-7 | **BLOCKING, NEW** | PART B accounting assertion halt model | "GLOBAL, run-aborting check for that prime's computation" is self-contradictory; whether one prime's failure destroys all four primes' output or only that prime's is unstated |
| PF-8 | **BLOCKING, NEW** | PART B accounting assertion justification | The "traced by hand" n_trapped_false==9/sum==194 claim for p=2437 is false (real value: 33/170, confirmed by direct query); misattributed to round 1's own trace, which never made this claim |
| PF-9 (round 1's PF-4) | not applicable this round | — | Renumbered; round 1's advisory items PF-4/PF-5/PF-6 are addressed above under their original numbers per this draft's own `pfN_summary` labelling |
| PF-10 | ADVISORY | PART B is_structural_local_min duplicate | The stated duplicate formula doesn't explicitly restate the PF-7 loud-raise-on-missing-neighbour guard, though it is structurally unreachable either way given the required coverage assertion |
| PF-11 | ADVISORY | PART B top-decile, theoretical edge case | `n_basin_eligible == 0` (not reachable by these four primes) would divide by zero in the top-decile fraction; not exercised by real data |

---

## Required controls / checks before dispatch

- **PF-7 [BLOCKING]:** state explicitly whether the basin-accounting
  assertion's halt is scoped to that one prime's computation (with other
  primes' results preserved and written) or aborts the entire run before any
  output is produced, and state whether the same per-prime isolation
  `crosscheck_pass` gating requires is the mechanism that provides this
  scoping.
- **PF-8 [BLOCKING]:** correct or remove the "traced by hand" numeric
  illustration (n_trapped_false==9, sum==194 for p=2437) — replace with the
  correct values (33/170), sourced from `descent_metrics.per_prime[p]
  .greedy_trapped_fraction`, or remove the specific prediction and rely on
  the construction proof alone. Correct the misattribution to "the round-1
  reviewer's own trace."
- **PF-10/PF-11 [ADVISORY]:** text-only additions, non-blocking.

## Counterexample or mutation

**PF-7's counterexample:** consider an Executor implementation that wraps
each prime's PART B block in a per-prime `try/except TrappingDiagnosticError:
continue` (required for `crosscheck_pass` gating to make sense) but does
**not** exempt the basin-accounting assertion from that same catch — under
this reading, "GLOBAL" is simply wrong, and a hypothetical accounting
failure for prime P would skip only P, exactly like `crosscheck_pass`.
Now consider an equally literal Executor who reads "GLOBAL, run-aborting"
at face value and deliberately raises the accounting assertion's exception
*outside* any per-prime catch (e.g., by computing it in a final aggregation
step after all four primes' basins are built) — under this reading, one
prime's accounting failure discards the diagnostic's entire output for all
four primes, even primes whose own accounting independently passed. Both
implementations are literal, defensible readings of the same sentence, and
they produce materially different artifacts on a hypothetical failure —
directly falsifying "the failure-handling model is now unambiguous."

**PF-8's counterexample, executed directly against archived data:**
`RUN-SSIQ-a85692-b/raw-result.json`'s
`descent_metrics.per_prime["2437"]["greedy_trapped_fraction"] ==
0.8374384236453202`. `(1 - 0.8374384236453202) * 203 == 33.0` exactly.
`RUN-SSIQ-58b642-a/raw-result.json`'s `correctness_gates
.delta1_locus_cross_check["2437"]["n_built_fp_rational"] == 9`. `33 != 9` —
a direct falsifier of "n_trapped_false expected == the F_p-rational locus
size 9," computed from data both already archived and available to the
draft's own author without running anything new.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
(toy-scale infrastructure and a graph-structural diagnostic,
`asymptotic_claim: null` throughout, correctly inherited). The relevant
baseline remains this campaign's own instrument- and spec-scrutiny
discipline (GD-4 through GD-12, and v5's own PF-9 precedent): PF-7 shows
that a resolved ambiguity can be reintroduced, in the same document, at a
different location, by the very act of writing the explanatory text for an
unrelated fix; PF-8 shows that "trace it, don't trust it" must apply to a
Coordinator's own confidence-building illustration inside a fix, not only to
the fix's operative logic — exactly the shape of finding v5's round 2
(PF-9) already established for this lineage, now recurring in a sibling
amendment.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains empty (gradient-existence
screen, not a heuristic-conditional complexity claim) — attacked and held,
consistent with every prior review in this lineage. No finding here
implicates a numbered heuristic; PF-7 and PF-8 are failure-handling and
numeric-fidelity precision gaps in diagnostic contract text, not claims
about the underlying ECDLP-adjacent problem.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly, inherited); the per-attempt-cost × inverse-success-probability
review does not apply. The `900s`/`0.3` CPU-hour budget is unchanged and
remains realistic; PF-7's fix (a failure-handling clarification) and PF-8's
fix (a numeric correction) have zero cost impact — neither requires new
computation. The live concern remains evidentiary: PF-7's ambiguity, if it
resolves the wrong way, could silently discard three valid primes' worth of
already-computed results on one prime's anomaly (a real evidentiary cost,
not merely a stylistic one); PF-8's false prediction, if left uncorrected,
risks one wasted review cycle re-deriving that a large numeric mismatch
between the contract's own prediction and the real run's output is not
actually a defect.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis; `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) correctly stated and not exceeded. No scope-inflation
found. `funnel_structure_diagnostic_v6`'s `OBJECTIVE_BOUNDARY` correctly
restates PART B as a diagnostic, not a claim; no decision rule reads PART
B's output. This amendment still correctly implements exactly the two
resume actions `DEC-20260806-357b30`'s `next_actions`/`resume_action`
named, on the same four primes, at zero new search cost — unaffected by
PF-7/PF-8, both of which are purely inside PART B's own diagnostic text.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` (inherited unchanged)
remains correctly reasoned — a direct instrument-level gradient-existence
screen and a graph-structural diagnostic, not a proof-oriented proposal.
Attacked and held, same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v6.yaml` as committed
at `6ae7847f`, `status: draft`: round 1's three blocking findings are
genuinely resolved on their own stated terms, confirmed by independent
re-derivation against the frozen code and archived data rather than by
re-reading either report's prose. **PF-1's basin-eligible-partition fix is
mathematically airtight**, including against the specific "walk passes
through a delta_E=1 vertex" stress case this task named — that scenario is
not a reachable code path, because the walk halts the instant it reaches
delta_E=1. **PF-2's reuse split is real** — both cited import targets are
genuinely standalone, module-level functions, confirmed by direct read of
all 500 lines of `trapping_diagnostic_v5.py`. **PF-3's headline fix
accurately describes the real code's actual behaviour** — `crosscheck_pass`
never aborts, matching `RUN-SSIQ-a85692-e`'s own archived, completed
execution on all four primes despite disagreements on all four. **But the
fix for PF-3 reintroduces PF-3's own defect shape one level deeper**: PART
B's REQUIRED ACCOUNTING ASSERTION is described with a self-contradictory
"GLOBAL... for that prime's computation" failure-handling phrase, leaving
unstated whether one prime's hypothetical accounting failure destroys all
four primes' output or only one (PF-7, blocking). **And the accounting
assertion's own "traced by hand" numeric illustration is false**,
confirmed by direct query against already-archived
`descent_metrics.per_prime` data: the real `n_trapped_false` for p=2437 is
33, not the claimed 9, and `sum(len(basin[m]))` is 170, not 194 — a
confidently-stated, falsified claim misattributed to round 1's own trace,
which round 1 never made (PF-8, blocking, though non-gating: it does not
affect the accounting mechanism's own correctness, only a piece of
illustrative prose). PF-4, PF-5, PF-6 are confirmed correctly applied, with
PF-6 specifically re-verified against the real basin-eligible counts these
four primes will actually produce (86/114/176/270), as the launching task
directed. Two further advisory items (PF-10, PF-11) round out this pass.
None of PF-7/PF-8/PF-10/PF-11 requires redesigning either part's mechanism;
all are fixable at zero new search cost.

## Next concrete action

Coordinator: before `status: approved` / setting `frozen_at`, require the
amendment text to (1) resolve PF-7 by stating explicitly whether the basin-
accounting assertion's halt is per-prime (scoped, other primes' results
preserved) or global (aborts the whole run before any output is produced),
and whether it shares the same per-prime isolation mechanism
`crosscheck_pass` gating requires; (2) resolve PF-8 by correcting the
n_trapped_false==9/sum==194 illustration to the correct values (33/170 for
p=2437, computed the same way for the other three primes) or removing the
specific numeric prediction in favour of the construction proof alone, and
correcting the misattribution to round 1's trace; (3) apply PF-10/PF-11 as
text-only additions. Re-verify PF-7 and PF-8's specific fixes once added,
before freeze, per this campaign's own standing GD-12/PF-9 practice: any
mathematical, accounting, or failure-handling claim in contract prose gets a
concrete, executed trace before it is trusted, applied here uniformly
(including to this review's own PF-8, whose counterexample above is a
genuine, direct query against real archived JSON, not an assertion).

## Overall verdict

**DO-NOT-FREEZE.** Blocking, in priority order:

1. **[BLOCKING, NEW]** PF-7 — PART B's own REQUIRED ACCOUNTING ASSERTION is
   described with a self-contradictory "GLOBAL... for that prime's
   computation" failure-handling phrase, reintroducing the identical
   global-vs-per-prime ambiguity PF-3 was raised, and correctly fixed
   elsewhere in this same draft, to resolve.
2. **[BLOCKING, NEW]** PF-8 — the accounting assertion's own "traced by
   hand" numeric justification (n_trapped_false==9, sum==194 for p=2437) is
   false, confirmed by direct query against already-archived data (real
   value: 33/170); non-gating on the assertion's own correctness, but a
   confidently-stated, falsified claim in frozen contract text,
   misattributed to a trace round 1's report never made.

Round 1's three original blocking findings (PF-1, PF-2, PF-3's headline
per-prime model) are all **CONFIRMED HOLDING**, independently re-derived
against the frozen code and archived data in this pass, not merely
re-read. PF-4, PF-5, PF-6 are **CONFIRMED APPLIED**, with PF-6 specifically
re-verified against real basin-eligible counts as directed. PF-10 and PF-11
are advisory and do not block this dispatch on their own.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2
  task_id: TASK-20260806-088952
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v6.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at snapshot 6ae7847f, parented on
    e78309b4 (the round-1-reviewed draft) -- a revision applying all six
    findings (PF-1, PF-2, PF-3, PF-4, PF-5, PF-6) of
    RT-PREFREEZE-EXP-SSIQ-a85692-v6.md's DO-NOT-FREEZE verdict: PART B's
    basin-accounting convention is redefined via "basin-eligible local
    minima" = {m : is_structural_local_min(m) AND delta_map[m] > 1}; the
    reuse mechanism for build_graph_for_prime/load_archived_prime_data is
    stated as genuine imports with is_structural_local_min/coverage/
    graph-rebuild-verification as disclosed duplicates; the crosscheck's
    halt model is stated as a per-prime, never-aborting crosscheck_pass
    boolean.
  objections:
    - "PF-7 [BLOCKING, NEW]: PART B's own REQUIRED ACCOUNTING ASSERTION (funnel_structure_diagnostic_v6, item 2) is described as 'a GLOBAL, run-aborting check for that prime's computation' -- a self-contradictory phrase naming two different failure-handling scopes in five words. PART A's own use of 'global, run-aborting' two paragraphs earlier is unambiguous only because its own justification ('a bug independent of any prime-specific data question') explicitly rules out per-prime scoping; PART B's parallel assertion gives no such disambiguation and instead appends 'for that prime's computation', which reads as scoping it TO one prime -- the opposite of PART A's own definition of 'global'. PART B's own precondition model (crosscheck_pass gates only that prime's block, 'while proceeding normally for every other prime') requires SOME per-prime isolation in the implementation; whether that same isolation also catches a basin-accounting-assertion failure (making it, despite the 'GLOBAL' label, effectively per-prime), or whether the assertion is deliberately left outside that isolation (so it genuinely destroys all four primes' output on one prime's anomaly) is never stated. This is the identical failure-handling underspecification shape PF-3 was raised to close (and PF-3's own headline fix correctly closes elsewhere in this same draft), now reintroduced one level deeper, inside the very fix text meant to resolve it."
    - "PF-8 [BLOCKING, NEW]: the REQUIRED ACCOUNTING ASSERTION's own explanatory text states, with confidence, 'per the round-1 reviewer's own trace SHOULD now hold exactly (traced by hand for p=2437: 203 total vertices, n_trapped_false expected == the F_p-rational locus size 9 ... so sum(len(basin[m])) is expected == 194)'. This is false on two counts, both directly checkable against already-archived data: (1) round 1's report never made this trace -- it cites '9/18/18/17 per prime' exactly once, as the OLD broken scheme's overcount magnitude (each delta_E=1 vertex double-counted by exactly one), never as a prediction of the corrected scheme's n_trapped_false value, a categorically different quantity; the attribution is fabricated. (2) The number itself is false: n_trapped_false counts every vertex whose walk EVER reaches delta_E=1 (zero or more steps), not merely the F_p-rational vertices that trigger the immediate short-circuit. Directly queried RUN-SSIQ-a85692-b/raw-result.json's descent_metrics.per_prime['2437'].greedy_trapped_fraction == 0.8374384236453202 (computed on the identical seed-20260805 rebuilt graph and real delta_map PART A/B's reuse mechanism will reproduce byte-for-byte): (1 - 0.8374384236453202) * 203 == 33.0 exactly, not 9 -- a factor of ~3.7x off. sum(len(basin[m])) is therefore 170, not 194. The same computation for the other three primes gives n_trapped_false = 90, 86, 91 against the draft's implied 18, 18, 17 -- every prime wrong, by factors of 4.8x-5.4x. Non-gating on the assertion's own correctness (PF-1's fix makes the assertion hold as a genuine partition regardless of the specific values, and the draft itself hedges 'the Executor's own run reports the actual figures, not this contract's prediction'), but a confidently-stated, falsified numerical claim left in frozen contract text is exactly the failure mode GD-12's own standing repair exists to catch, and risks a false 'something is wrong' alarm burning a review cycle when the real run reports 33/90/86/91 against a written expectation of 9/18/18/17."
    - "PF-1 [round 1's finding, CONFIRMED HOLDING]: independently re-derived, not merely re-read -- greedy_descent_hitting_time's loop invariant (delta_map[current] != 1 always holds at loop entry, by induction: the pre-loop check excludes start, and any step reaching delta=1 returns trapped=False immediately, before the next loop iteration's candidate check can run) proves trapped=True can only fire at a vertex with delta>1, exactly PART A's basin-eligible condition, with no code path for a walk to 'pass through' delta_E=1 and terminate elsewhere. Every basin-eligible m has itself in its own basin by construction (0-step self-trap, full unfiltered neighbour set on the first iteration since prev is None). The accounting assertion is a genuine, exhaustive, non-overlapping partition."
    - "PF-2 [round 1's finding, CONFIRMED HOLDING]: build_graph_for_prime and load_archived_prime_data independently confirmed standalone, module-level functions by direct read of all 500 lines of trapping_diagnostic_v5.py, with signatures/return values matching the draft's description exactly. is_structural_local_min/coverage/graph-rebuild-verification independently reconfirmed NOT separately importable, so the draft's disclosed-duplication path is the only available one, correctly identified. One minor, non-blocking gap (PF-10): the stated duplicate formula for is_structural_local_min does not explicitly restate the PF-7 loud-raise-on-missing-neighbour guard from the real inline code, though it remains structurally unreachable either way given the required coverage assertion."
    - "PF-3 [round 1's finding, headline CONFIRMED HOLDING]: independently confirmed by direct read of run_diagnostic_for_prime (all 500 lines) that crosscheck_pass is computed and recorded but never gates a raise anywhere in that function; main() writes both output artifacts and prints a summary for all four primes regardless of crosscheck_pass. Directly cross-checked against RUN-SSIQ-a85692-e's own archived trapped_vs_structural_crosscheck.json: crosscheck_pass=False for all four primes (93/203, 138/324, 234/478, 267/611 disagreements), and the run completed and archived normally rather than aborting -- the draft's claim about the real code's actual behaviour is accurate. See PF-7 above for where this fix's OWN new text reintroduces the resolved ambiguity elsewhere."
    - "PF-4/PF-5/PF-6 [round 1's advisory findings, CONFIRMED APPLIED]: branch-coverage requirement for the 3-input regression test is explicit; depth(m)'s 'non-negative' wording resolves the prior self-contradiction and is independently reconfirmed correct (candidates uses strict <, matching is_structural_local_min's <=, so a tied neighbour correctly yields depth==0, a real reachable case); the top-decile k=max(1,ceil(0.1*n_basin_eligible)) formula is explicit and, checked directly against the real basin-eligible counts these four primes will produce (86/114/176/270, derived from RUN-SSIQ-a85692-e's archived n_structural_local_min minus RUN-SSIQ-58b642-a's archived F_p-rational locus sizes), well-defined throughout with no boundary case triggered. PF-11 (advisory): the formula's theoretical n_basin_eligible==0 edge case would divide by zero, but is not reachable by any of the four primes actually in scope."
  required_controls:
    - "PF-7: state explicitly whether the basin-accounting assertion's halt is scoped to only that prime's PART B computation (other primes' results preserved and written) or aborts the entire run before any output is produced, and whether it shares the per-prime isolation mechanism crosscheck_pass gating already requires -- BLOCKING."
    - "PF-8: correct the n_trapped_false==9/sum==194 illustration for p=2437 to the correct values (33/170), sourced from descent_metrics.per_prime[p].greedy_trapped_fraction rather than the F_p-rational locus size, or remove the specific numeric prediction and rely on the construction proof alone; correct the misattribution to round 1's own trace, which never made this claim -- BLOCKING, zero new search cost, correct values derivable from already-archived data."
    - "PF-10/PF-11: text-only additions, non-blocking."
  counterexample_or_mutation: >-
    PF-7: two equally literal Executor readings of the same sentence produce
    materially different artifacts on a hypothetical accounting-assertion
    failure -- one (per-prime try/except also catches the accounting
    assertion) preserves the other three primes' results; the other
    ('GLOBAL' read literally, assertion computed outside any per-prime
    catch) discards all four primes' output on one prime's anomaly. Neither
    reading is ruled out by the current text.
    PF-8: RUN-SSIQ-a85692-b/raw-result.json's
    descent_metrics.per_prime["2437"]["greedy_trapped_fraction"] ==
    0.8374384236453202, computed on the same seed-20260805 rebuilt graph and
    real delta_map PART A/B's reuse mechanism will reproduce.
    (1 - 0.8374384236453202) * 203 == 33.0 exactly.
    RUN-SSIQ-58b642-a/raw-result.json's correctness_gates
    .delta1_locus_cross_check["2437"]["n_built_fp_rational"] == 9. 33 != 9,
    directly falsifying "n_trapped_false expected == the F_p-rational locus
    size 9" using only already-archived data, no new computation.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline remains this
    campaign's own instrument- and spec-scrutiny discipline (GD-4 through
    GD-12, and specification_v5.yaml's own round-2 PF-9 precedent): PF-7
    shows a resolved ambiguity can be reintroduced, in the same document, by
    the act of writing an unrelated fix's own explanatory text; PF-8 shows
    "trace it, don't trust it" must apply to a Coordinator's own
    confidence-building illustration inside a fix, not only to the fix's
    operative logic -- the same finding shape v5's round 2 established for
    this lineage, now recurring in a sibling amendment.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; PF-7/PF-8 are failure-handling and numeric-fidelity precision gaps in diagnostic contract text."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is unchanged and remains realistic; PF-7's fix (a failure-handling clarification) and PF-8's fix (a numeric correction) have zero cost impact."
    - "The live concern is evidentiary: PF-7's ambiguity, if resolved the wrong way, could silently discard three valid primes' worth of already-computed results on one prime's anomaly; PF-8's false prediction, left uncorrected, risks a wasted review cycle re-deriving that a large mismatch between the contract's own prediction and the real run's output is not actually a defect."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded. No scope-inflation found."
    - "funnel_structure_diagnostic_v6's OBJECTIVE_BOUNDARY correctly restates PART B as a diagnostic, not a claim, consistent with the rest of the draft -- no decision rule reads PART B's output."
    - "This amendment still correctly implements exactly the two resume actions DEC-20260806-357b30's next_actions/resume_action named, on the same four primes, at zero new search cost -- reconfirmed here, unaffected by PF-7/PF-8, both purely inside PART B's own diagnostic text."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen and a graph-structural diagnostic, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v6.yaml as committed
    at 6ae7847f, status: draft: round 1's three blocking findings are all
    genuinely resolved on their own stated terms, independently re-derived
    against the frozen code and archived data. PF-1's basin-eligible
    partition is mathematically airtight, including against the "walk
    passes through delta_E=1" stress case (not a reachable code path). PF-2's
    reuse split is real, both import targets confirmed genuinely standalone.
    PF-3's headline per-prime crosscheck_pass model accurately describes the
    real code's actual, archived, non-aborting behaviour. But PART B's own
    new fix text introduces two new blocking defects: its REQUIRED
    ACCOUNTING ASSERTION's failure-handling model is self-contradictory
    ("GLOBAL... for that prime's computation"), reintroducing PF-3's own
    resolved ambiguity one level deeper (PF-7); and its "traced by hand"
    numeric justification (n_trapped_false==9/sum==194 for p=2437) is false,
    confirmed by direct query against already-archived data (real value:
    33/170), misattributed to a trace round 1's report never made (PF-8,
    non-gating on the assertion's own correctness but a falsified claim in
    frozen contract text). PF-4/PF-5/PF-6 are confirmed correctly applied,
    with PF-6 specifically re-verified against the real basin-eligible
    counts these four primes will produce. PF-10/PF-11 are advisory. None
    require redesign; all fixable at zero new search cost.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text to (1) resolve PF-7 by stating explicitly whether the basin-
    accounting assertion's halt is per-prime (scoped) or global (aborts the
    whole run), and whether it shares crosscheck_pass's own per-prime
    isolation; (2) resolve PF-8 by correcting the numeric illustration to
    33/170 (p=2437) and the corresponding correct pairs for the other three
    primes, or removing the specific prediction in favour of the
    construction proof alone, and correcting the misattribution to round 1's
    trace; (3) apply PF-10/PF-11 as text-only additions. Re-verify PF-7 and
    PF-8's specific fixes once added, before freeze, per this campaign's own
    standing GD-12/PF-9 practice: any mathematical, accounting, or
    failure-handling claim in contract prose gets a concrete, executed trace
    before it is trusted, applied here uniformly including to this review's
    own PF-8 (a direct query against real archived JSON, not an assertion).
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Hand-traced greedy_descent_hitting_time's loop invariant by induction
    (delta_map[current] != 1 at every loop entry) directly against
    descent_hitting_time.py's actual control flow, establishing that
    trapped=True can only fire at delta>1 vertices and that a walk cannot
    "pass through" a delta_E=1 vertex and terminate elsewhere. Read all 500
    lines of trapping_diagnostic_v5.py to confirm build_graph_for_prime and
    load_archived_prime_data are standalone module-level functions and that
    run_diagnostic_for_prime never raises on crosscheck_pass=False.
    Programmatically queried RUN-SSIQ-a85692-b/raw-result.json's
    descent_metrics.per_prime[p].greedy_trapped_fraction for all four
    primes, RUN-SSIQ-a85692-e's trapping_diagnostic.json and
    trapped_vs_structural_crosscheck.json, and RUN-SSIQ-58b642-a
    /raw-result.json's correctness_gates.delta1_locus_cross_check, computing
    n_trapped_false = (1 - greedy_trapped_fraction) * n_vertices exactly for
    all four primes (33, 90, 86, 91) and confirming these differ from the
    draft's implied 9/18/18/17. Read compute_delta_e.py's descent_metrics
    block to confirm greedy_trapped_fraction is computed on the identical
    seed-20260805 rebuilt graph PART A/B's own reuse mechanism will
    reproduce. Computed k = max(1, ceil(0.1 * n_basin_eligible)) for all
    four primes against real archived basin-eligible counts (86/114/176/270).
    git log/git status confirmed both code files frozen with no
    working-tree changes and confirmed specification_v6.yaml's current
    committed state (6ae7847f) and clean working tree. No graph built, no
    delta_E search run, no file written outside this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-009/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml itself),
    the round-1 report, and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
