# RT-PREFREEZE-EXP-SSIQ-a85692-v5 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v5.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-008

**Reviews `experiments/EXP-SSIQ-a85692/specification_v5.yaml` at `status: draft`,
`pre_freeze_review.status: PENDING`, as committed at snapshot `c445c171`
("GOAL-SSIQ-001 BATCH-008: EXP-SSIQ-a85692 v5 amendment draft (not yet
frozen)"), the last batch of this goal's 8-batch `campaign_budget`.** Per
this task's operating rules, only this Coordinator-committed snapshot is
treated as durable input; nothing below is drawn from an uncommitted
working-tree state. This report changes nothing under
`experiments/EXP-SSIQ-a85692/` (including `specification_v4.yaml`, frozen at
`0b15e854` and confirmed retained unedited) or any ledger record — those
remain the Coordinator's alone to touch.

Read in full, per the launching task: `specification_v4.yaml` (264 lines, the
frozen v4 contract, as the diff base) and `specification_v5.yaml` (188
lines) in full; `RT-BATCH-007.md` and `VAL-BATCH-007.md` in full, with
particular attention to Front 4/ANOM-1 (the N=324/n=3, N=611/n=6 cases) and
Front 6 (the ranking that justifies bundling Parts A and B);
`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py`'s
`ols_loglog_fit` (lines 104–134) and `bootstrap_gap_ci` (lines 362–384) read
directly, in full, not from any prose summary — this is the exact code the
launching task asks to be traced for the bootstrap wiring question;
`experiments/EXP-SSIQ-58b642/implementation/build_isogeny_graph.py`'s
`build_graph_bfs`, `degree_sequence_check`, `neighbors_2isogenous`,
`seed_j_invariant`, and `bfs_diameter` read directly;
`experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py`'s
`build_all_graphs` and `run_correctness_gates` (the actual code that built
the graphs underlying `RUN-SSIQ-a85692-b`'s delta_map, and the actual
C-CONNECTIVITY implementation this amendment proposes to reuse) read
directly; `experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json`
loaded and inspected programmatically (not sampled) — specifically
`phase_minus1_real_search`'s `delta_map` structure, key format, and coverage
fields for all five primes (2437, 3889, 5737, 7333, 8893);
`ledger/goals/GOAL-SSIQ-001/goal.yaml`'s GD-11 entry and `next_action`,
`ledger/evidence/EV-SSIQ-87d21a.yaml`, `ledger/decisions/DEC-20260805-6aa5c2.yaml`
in full.

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
    found unprobeable (VAL/RT-BATCH-003 through 007,
    RT-PREFREEZE-EXP-SSIQ-a85692[-v2,-v3,-v4]), so this is recorded as the
    standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This
    review shares a model family with every producer and every prior
    reviewer in this lineage; it does not upgrade the campaign's evidence
    tier by itself and does not itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**This draft should NOT be frozen as written.** Two independent, freeze-blocking
gaps, one in each part, both of the exact "looks validated, wasn't" shape
this campaign's own defect history (GD-4 through GD-11) names and repairs
recursively:

1. **PART A (PF-1, BLOCKING): the bootstrap wiring question the draft's own
   `pre_freeze_review.note` flags as unresolved is a real hollow-fix risk, not
   a hypothetical one.** Read directly: `dht.bootstrap_gap_ci`'s signature is
   `bootstrap_gap_ci(N_list, median_greedy_list, median_random_list, rng,
   n_boot=2000)` — **it has no parameter through which a caller can supply an
   alternate fit function at all**, and its body calls the module-global name
   `ols_loglog_fit` directly (`fg = ols_loglog_fit(Nb, gb)`, line 374). The
   draft's `inputs.gd11_fix_v5` text states as a plain fact that
   `bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci` (a literal alias) in the same
   sentence that admits the wiring is unresolved ("callers needing the
   hardened guard inside bootstrap resampling must pass `ols_loglog_fit_v2`
   as an explicit parameter **or** the module wires `bootstrap_gap_ci_v2` to
   call `ols_loglog_fit_v2` internally — STATE EXPLICITLY WHICH"). Given the
   actual signature, the first named option is not available without editing
   the frozen `bootstrap_gap_ci` (contradicting the amendment's own claim that
   `descent_hitting_time.py` "stays frozen and byte-for-byte untouched"). As
   literally specified, the alias is bound forever to the code path that
   calls the **original, unhardened** `ols_loglog_fit` on every resample.
   GD-11's most severe reproduced failure mode (Front 4 of `RT-BATCH-007.md`:
   a fully-degenerate resample silently producing a spurious, plausible-looking
   nonzero `gamma` rather than raising) happens **inside `bootstrap_gap_ci`'s
   resampling loop**, at exactly the small-`n` null-arm boundary this campaign
   is about to reach for the first time on real data. As specified, this
   amendment's hardening **never reaches that call site**. See PF-1.
2. **PART B (PF-4, BLOCKING): the diagnostic's central data-join step —
   matching a freshly rebuilt graph's tuple-keyed vertices against
   `delta_map`'s JSON string keys — has no stated conversion procedure, and a
   plausible mismatch fails silently, not loudly.** `delta_map`'s on-disk keys
   are `str(list(v))` (confirmed directly against
   `RUN-SSIQ-a85692-b/raw-result.json`, e.g. `"[1031, 1095]"`), a convention
   established by `compute_delta_e.py`/`compute_delta_e_v2.py`'s
   `delta_map_json_safe` construction — and **no code anywhere in this
   repository has ever reverse-parsed this format back into vertex tuples**;
   every prior consumer of `delta_map` used the in-memory,
   tuple-keyed `delta_map_raw` directly, in the same process that built the
   graph. Part B's diagnostic is the first code in this campaign's history to
   need this specific round-trip, and the spec text never states the
   conversion procedure. If an Executor's plausible-but-wrong choice (e.g.
   `str(v)` on a tuple, which yields `"(1031, 1095)"`, not `"[1031, 1095]"`)
   is used with `.get(key, <unresolved-default>)` — which the spec's own
   "handled per a stated, pre-registered rule, not silently dropped" language
   invites — **every single lookup fails identically**, and depending on what
   that pre-registered rule does, the diagnostic could complete and report a
   number without ever raising an error. This is precisely the shape of GD-9
   ("a control that structurally cannot fail") and GD-10 (a second,
   independent implementation silently bypassing the real one). See PF-4.

Three further findings are not individually blocking but should be applied
alongside PF-1/PF-4 before freeze: PF-5 (C-CONNECTIVITY as actually
implemented is a vertex-**count** check, not an edge-structure check, and the
draft's own framing of "byte-identical vertex/edge structure" cannot
actually be verified by anything this amendment reuses); PF-6 (the
walk-trapped/structural-local-minimum "gap" the draft's own pre-freeze note
(f) asks about is **provably zero** for the frozen, unchanged
`greedy_descent_hitting_time` — a fact derivable directly from the function's
own documented invariant, not an open empirical question — which changes
what the required cross-check should actually be **for**, and argues for
running it on every vertex, not a sample); and two advisory items (PF-7,
PF-8) on untested branches and claim-scope hygiene.

None of these findings require redesigning either part's mechanism. All are
fixable at zero new search cost, consistent with the amendment's own budget.

---

## PART A

### (a) Is `ols_loglog_fit_v2` precise enough that an Executor could not introduce other silent behavioral changes?

**Yes, for the standalone function itself.** The spec text is explicit and
checkable by direct line diff: "BYTE-IDENTICAL to `dht.ols_loglog_fit` except
[the guard line]." The replacement condition, `max(xs) == min(xs)`, is a pure
function of `xs` (computed at line 113 of the original, before `sxx`/`xbar`),
so its placement relative to the rest of the (unchanged) body is functionally
inert — it can sit anywhere between computing `xs` and computing `gamma =
sxy/sxx` without changing behavior, and a pre-freeze/post-hoc line diff can
verify "every other line byte-identical" mechanically. **No issue here.**

One residual, minor, non-blocking maintenance-debt note: because
`descent_hitting_time.py` must stay byte-for-byte untouched, `ols_hardened.py`
necessarily achieves this "byte-identical except the guard" property by
**copying** the function body, not by composition (e.g. a shared private
core the two functions both delegate to). A future numerical fix to
`dht.ols_loglog_fit` (a real possibility, given this campaign's own
`instrument_calibration` history) will not automatically propagate to
`ols_loglog_fit_v2` — the two will silently diverge unless a future amendment
re-applies the fix by hand to both. This is exactly the texture of
duplicate-logic risk GD-10 named, one layer removed (a duplicate of a
*correct* implementation rather than of a *buggy* one, so lower severity) —
recorded so it is not forgotten, not blocking this freeze.

### (b) Is `max(xs) == min(xs)` the right replacement, confirmed against RT-BATCH-007.md's own cases?

**Yes, independently re-executed, not merely re-derived.** Direct computation:

```
N=324, n=3: sxx=2.3665827156630354e-30 (old guard: does NOT fire) ; max(xs)==min(xs): True (new guard: FIRES)
N=611, n=6: sxx=4.733165431326071e-30  (old guard: does NOT fire) ; max(xs)==min(xs): True (new guard: FIRES)
```

Both of `RT-BATCH-007.md`'s own named anomaly cases are correctly caught by
the proposed replacement, and (cross-checked against `EV-SSIQ-87d21a.yaml`
O-4) the four already-archived real N values (203, 324, 478, 611 at n=4) all
correctly raise under **both** the old and new guard, so the replacement
changes nothing about currently-archived behavior. **Confirmed correct.**

### (c) THE BOOTSTRAP WIRING QUESTION — traced directly against the actual code, BLOCKING

Per the launching task's specific instruction, I read `bootstrap_gap_ci`
directly (not the draft's prose):

```python
def bootstrap_gap_ci(N_list, median_greedy_list, median_random_list, rng,
                      n_boot=2000):
    ...
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        Nb = [N_list[i] for i in idx]
        gb = [median_greedy_list[i] for i in idx]
        rb = [median_random_list[i] for i in idx]
        try:
            fg = ols_loglog_fit(Nb, gb)
            fr = ols_loglog_fit(Nb, rb)
        except ValueError:
            continue
        gaps.append(fr["gamma"] - fg["gamma"])
```

**There is no parameter of any kind through which a caller can substitute a
different fit function.** `ols_loglog_fit` is called by its bare module-global
name, twice, inside the resampling loop. This is a hard fact about the
frozen, unchanged code, not an interpretation.

The draft's own `inputs.gd11_fix_v5` text states, as a plain declarative
fact, "`bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci` (an alias, not a
reimplementation)" — and in the very next clause admits this doesn't actually
resolve the question ("callers needing the hardened guard inside bootstrap
resampling must pass `ols_loglog_fit_v2` as an explicit parameter **or** the
module wires `bootstrap_gap_ci_v2` to call `ols_loglog_fit_v2` internally —
STATE EXPLICITLY WHICH, as a required, code-verified diff-list item, not left
ambiguous"). This is internally inconsistent: it asserts a concrete binding
(`= dht.bootstrap_gap_ci`) while simultaneously flagging that binding as an
open question. Given the actual signature traced above, **the first named
resolution path is not achievable at all** without editing the frozen
`bootstrap_gap_ci` — which the amendment's own `amendment_scope` forbids
("`descent_hitting_time.py` stays frozen and byte-for-byte untouched...PART A
supersedes by addition, never by edit"). So as the spec is literally written
(`bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci`), the only concrete binding
actually stated, `bootstrap_gap_ci_v2` **is** `dht.bootstrap_gap_ci`, calling
the original, unhardened `ols_loglog_fit` on every resample, forever, with no
mechanism for any caller — however "hardened-guard-aware" — to change that
through the exported symbol this amendment actually names.

**Why this is a hollow fix, not merely an ambiguity.** GD-11's own most
serious confirmed manifestation (`RT-BATCH-007.md` Front 4) is a spurious
nonzero `gamma` entering `bootstrap_gap_ci`'s `gaps` list from *inside* the
resampling loop — not from a standalone call to `ols_loglog_fit`. The
amendment's own `next_action` framing (`goal.yaml` GD-11 entry, `EV-SSIQ-87d21a.yaml`)
names the risk explicitly: "the next real dispatch that reaches the null
arm's fit-and-bootstrap branch at a small survivor count including prime
3889 is at genuine, non-hypothetical risk." **That exact call path — a
bootstrap resample calling the fit function — is precisely the one this
amendment, as specified, does not protect.** A future caller that switches to
`ols_hardened.bootstrap_gap_ci_v2` believing it gets GD-11's protection gets
none: it is byte-identical to the vulnerable original.

**This gap is invisible to the amendment's own required validation.**
`required_artifacts` names `gd11_regression_test.json`, and `inputs.gd11_fix_v5`
requires only that the regression test call `ols_loglog_fit_v2` directly on
the two named (N, n) cases and confirm it raises `ValueError`. Nothing in the
required validation calls `bootstrap_gap_ci_v2` at all, so even the
literal, as-written hollow binding (`= dht.bootstrap_gap_ci`) would **pass**
every required check cleanly — the required test cannot detect the failure
mode it exists to prevent, the same structural blind spot `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md`
found in `mutation_precondition_v4`'s first draft (PF-1 there) and
`RT-BATCH-006.md` found in v3's self-test (GD-10).

**This is BLOCKING (PF-1).** See Findings below for the required fix.

### (d) Does this amendment retroactively alter any already-archived gamma/CI value?

**No, confirmed.** `required_artifacts_note`'s "NOT RE-RUN" list is accurate:
nothing in `inputs.gd11_fix_v5` reads or recomputes any prior run's
`descent_metrics`, and the new module is additive (a new file,
`ols_hardened.py`), never an edit to `descent_hitting_time.py`. This is
consistent with `EV-SSIQ-87d21a.yaml` O-4's own finding that no
currently-archived number is contaminated by GD-11. **Confirmed, no issue.**

---

## PART B

### (e) Is the structural local-minimum diagnostic well-defined against `delta_map`'s real schema?

Directly inspected `RUN-SSIQ-a85692-b/raw-result.json`'s
`phase_minus1_real_search` for all five primes:

| prime | n_vertices | delta_map entries | coverage_all_vertices | used by v5? |
|---|---|---|---|---|
| 2437 | 203 | 203 | 1.0 | yes |
| 3889 | 324 | 324 | 1.0 | yes |
| 5737 | 478 | 478 | 1.0 | yes |
| 7333 | 611 | 611 | 1.0 | yes |
| 8893 | 741 | 577 | 0.779 | no (correctly excluded) |

For all four primes v5 actually uses, `delta_map` has **exactly one entry per
vertex**, including F_p-rational vertices (verified directly: e.g.
`delta_map["[1037, 0]"] == 1` for prime 2437, and all F_p-rational entries
checked have value `1`). **The "vertex with an unresolved neighbour" branch
the spec requires handling is therefore dead code against this batch's own
real data — it can never execute for any of the four primes used, since
`m_coverage_all_vertices_fraction == 1.0` for all four.** This is not an
error, but it means the "stated, pre-registered rule" the spec requires for
that branch is **specified but untestable by this run**, the same texture as
`RT-BATCH-007.md` OBJ-3/F-5's finding about CHECK 3's untested-branch scope —
see PF-7. Separately, the spec's parenthetical groups "vertices with an
unresolved neighbour" together with "F_p-rational with delta=1 by identity"
as if both need the same handling; they don't — F_p-rational vertices are
always resolved (trivially, `delta=1`), never unresolved. Minor imprecision,
not itself a computational error.

**The load-bearing, unaddressed part of (e) is the key-format bridge, and it
is a real gap — see PF-4 above and in Findings below.** `delta_map`'s on-disk
keys are `str(list(v))` (`"[1031, 1095]"`), a JSON-serialization convention
introduced by `compute_delta_e.py`'s `delta_map_json_safe = {str(list(k)): v
for k, v in delta_map.items()}` (confirmed by direct source read, both
`compute_delta_e.py` line 416 and `compute_delta_e_v2.py` line 292). **No
code in this repository has ever reverse-parsed this format**: every prior
consumer used `delta_map_raw` (tuple-keyed, in-memory, built in the same
process as the graph) directly — `run_population(g["adjacency"], vertices,
delta_map, ...)` at lines 803/805/838/840 of `compute_delta_e.py` all take
the raw, tuple-keyed dict, never the JSON-safe one. Part B's diagnostic is
the **first** code in this campaign to need `graph["vertices"]` (tuples, from
a freshly-built `build_graph_bfs`) and `delta_map` (JSON string keys, from an
archived file) to agree on a common key representation, and the spec states
no conversion procedure. See PF-4.

### (f) Does rebuilding the graph reproduce byte-identical structure, and is the stated verification sufficient?

**No — the "C-CONNECTIVITY's own floor(p/12) anchor" the spec names as its
verification is a vertex-COUNT check only, confirmed by direct code
reading, and cannot detect an edge-structure divergence.** Read
`compute_delta_e.py`'s `run_correctness_gates` directly:

```python
n_built = len(g["vertices"])
n_formula = p // 12  # p = 1 (mod 12): epsilon = 0 exactly
connectivity[p] = {"n_built": n_built, "n_formula_floor_p12": n_formula,
                    "pass": bool(n_built == n_formula)}
```

This compares two **integers**. It says nothing about which specific
vertices are adjacent to which. Two different graphs with the same vertex
count (e.g. one with a root-finding bug that swaps which of two
degree-matching curves ends up adjacent to a third) would pass this check
identically — directly answering the launching task's own question (f):
**yes, this can happen, and the stated check cannot catch it.**
`degree_sequence_check` (M-DEGSEQ, checks every vertex has degree exactly 3)
and `independent_edgelist_check` (C-EDGELIST, an independently-computed
spot-check of one sampled prime's edges) are the checks in this codebase
that actually probe edge structure — the draft's `pre_freeze_review.note`
(e) names only the count-check as reused, neither of the other two.

There is a deeper problem with the "byte-identical to what was already
validated" framing itself, independent of which check is reused: **the
original run never persisted the graph's adjacency structure.**
`RUN-SSIQ-a85692-b/raw-result.json` records `delta_map`, vertex counts, and
coverage fractions — not `adjacency`. There is literally no archived edge
data for Part B's rebuild to diff against. What Part B can actually verify is
**correctness of this build** (re-run M-DEGSEQ; cross-check `n_vertices`
against the exact, already-archived per-prime count — 2437→203, 3889→324,
5737→478, 7333→611 — a stronger, more specific, already-available check than
the generic `floor(p/12)` formula), not bit-identity to a specific prior
run's internal state, which cannot be checked by anything available.
Separately, direct reading of `build_isogeny_graph.py` confirms the graph is
a **deterministic mathematical object given `p`**: `seed_j_invariant(p)`
takes no seed/rng argument at all (Deuring reduction is a pure function of
`p`), and while `neighbors_2isogenous` uses an `rng` internally for root
extraction, `adjacency[v] = sorted(nbrs)` is a deterministic sort of whatever
roots are found, so a *correct* root-finder returns the same adjacency
regardless of the specific `rng` path taken. This reinforces the same
conclusion from a different angle: the right verification target for Part B
is "this rebuild is a correct 2-isogeny graph" (M-DEGSEQ + the specific
archived vertex count), not "this rebuild bit-matches an unrecorded prior
build." See PF-5.

### (g) Walk-trapped vs. structural local minimum — is there an actual gap, and does the draft's cross-check design address it?

**There is no gap. This is provable directly from the frozen, unchanged
`greedy_descent_hitting_time` code, not merely an empirical question a
sample-based cross-check can bound.** Read the function directly
(`descent_hitting_time.py` lines 179–222):

```python
while True:
    nbrs = [v for v in adjacency[current] if v != prev]
    if not nbrs:
        nbrs = list(adjacency[current])
    cur_delta = delta_map[current]
    candidates = [v for v in nbrs if delta_map[v] < cur_delta]
    if not candidates:
        return {..., "trapped": True, ...}
```

The function's own docstring states the invariant that makes the predecessor
exclusion irrelevant to `trapped`: "this exclusion can NEVER remove a
genuine strictly-smaller candidate in a strict-descent walk, since the
predecessor's delta is always STRICTLY GREATER than the current vertex's
delta by construction of the walk's own history." That is exactly the
argument: `candidates` requires `delta_map[v] < cur_delta`; `prev` can never
satisfy this (its delta is always strictly greater, by the walk's own
invariant), so excluding `prev` from `nbrs` changes nothing about whether
`candidates` is empty, whether or not the degenerate multi-edge fallback
(`if not nbrs: nbrs = list(adjacency[current])`) fires. **Therefore: "the
walk is trapped at vertex w" (regardless of the path taken to reach w, and
regardless of ties) is exactly equivalent to "w is a structural local
minimum" (`delta_map[w] <= min(delta_map[u] for u in adjacency[w])`) — a code
identity, not a statistical tendency.**

This changes what the draft's own required cross-check is actually testing.
Since the mathematical equivalence is exact, any observed disagreement
between Part B's `is_structural_local_min` and a re-run of
`greedy_descent_hitting_time` on the same `delta_map` can only be an
**implementation bug in Part B's own new code** (a strict-vs-non-strict
comparator mismatch, or — concretely — the key-format bug named in PF-4) —
never a discovery about the mechanism. Given that, running the cross-check on
"a sample of vertices," as specified, is the wrong design for its actual
purpose: a localized bug (e.g. one that only mis-handles the F_p-rational
`[j, 0]` keys, or one that silently drops a fraction of vertices to the
"unresolved" branch because of a key mismatch) could easily be invisible in a
small sample and present in the untested majority — precisely the concern
the launching task's item (g) raises. Since `greedy_descent_hitting_time` is
O(diameter) per start vertex and every graph here has ≤620 vertices, running
it against **every** vertex with a resolved `delta_E` value costs
negligibly more than a sample and is a much stronger regression test. See
PF-6.

### (h) Is Part B's own claim-scoping consistent with the rest of the draft?

**Broadly yes, but one adjacent-statistic risk is worth naming explicitly.**
`objective_boundary`'s language ("a DIAGNOSTIC, not a claim... does not test
H-SSIQ-36e970's real-arm prediction... does not itself constitute evidence
for or against a computable delta_E-gradient") is correctly stated and not
contradicted anywhere else in the draft — no decision rule references Part
B's output, and `required_artifacts` correctly keeps its output
(`trapping_diagnostic.json`) separate from anything H-SSIQ-36e970's own
decision machinery reads.

One thing worth flagging for a successor record, not blocking this freeze:
the "fraction of vertices that are structural local minima" Part B reports
is a **genuinely different statistic** from the already-archived
`greedy_trapped_fraction` (per PF-6's equivalence, "trapped from *start*
vertex v" means "v's own deterministic descent terminates at *some* local
minimum," which can be a many-to-one funneling onto a small set of actual
local-minimum vertices — so the raw fraction of vertices that *are* local
minima is generally smaller than, and conceptually distinct from, the
walk-outcome-weighted `trapped_fraction`). They are easy to conflate in a
later citation ("X% structural local minima" read as corroborating or
replicating the already-reported `trapped_fraction`), which would overstate
Part B's evidentiary weight in exactly the direction `objective_boundary`
disclaims. Recommend the successor record state the two are different
quantities, not interchangeable. Advisory (PF-8).

---

## Findings

### PF-1 — [BLOCKING] PART A: the bootstrap-CI wiring is unspecified, and as literally written binds `bootstrap_gap_ci_v2` to the unhardened original — a hollow fix of the same shape as GD-9/GD-10

See (c) above for the full trace. `dht.bootstrap_gap_ci` has no parameter for
injecting an alternate fit function and calls `ols_loglog_fit` by its bare
module-global name inside the resampling loop. The draft's own text both
asserts `bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci` (a literal alias to the
unhardened function) and simultaneously flags that binding as an open
question the amendment must resolve before freeze. As written, the only
concrete binding stated makes the amendment's hardening unreachable from any
bootstrap resample — precisely the call path where GD-11's most serious
confirmed failure mode (a spurious nonzero `gamma` silently entering
`bootstrap_gap_ci`'s output) actually occurs, and precisely the path the next
real null-arm dispatch is exposed on. The amendment's own required validation
(`gd11_regression_test.json`) never calls `bootstrap_gap_ci_v2` and so cannot
detect this gap.

**Required fix, one of:**
1. Add a `fit_function` parameter to a **genuinely new**
   `bootstrap_gap_ci_v2` in `ols_hardened.py` (not an alias — a distinct
   function, necessarily duplicating the resampling loop, since
   `descent_hitting_time.py` cannot be edited) that defaults to and threads
   `ols_loglog_fit_v2` through both fit calls (`fg`, `fr`); state this
   explicitly, not as an open "or," and require the pre-freeze reviewer to
   trace by hand (or the required regression test to demonstrate, executed)
   that a resample matching the N=324/n=3 or N=611/n=6 case, invoked through
   `bootstrap_gap_ci_v2`, actually raises/discards rather than silently
   contributing a spurious gap value.
2. Alternatively, if the Coordinator judges editing `bootstrap_gap_ci` itself
   (adding an optional `fit_function=ols_loglog_fit` parameter, default value
   preserving all existing callers' behavior byte-for-byte) is preferable to
   a duplicate loop, that requires revising `amendment_scope`'s current claim
   that `descent_hitting_time.py` "stays frozen and byte-for-byte untouched"
   — an explicit, disclosed exception, not a silent one — and the required
   validation must then exercise the new default-preserving parameter
   against at least one pre-existing archived call site to confirm no
   existing behavior changed.

Either way, `required_artifacts` must add a check that calls
`bootstrap_gap_ci_v2` (not only the standalone `ols_loglog_fit_v2`) on data
reproducing the N=324/n=3 or N=611/n=6 anomaly and confirms the resample is
correctly discarded rather than silently included.

### PF-4 — [BLOCKING] PART B: the delta_map key-format bridge between the archived JSON and the freshly-rebuilt graph is unspecified, and a plausible mismatch fails silently

See (e)/PF-4 discussion above. `delta_map`'s on-disk keys are `str(list(v))`
(`"[1031, 1095]"`); no code anywhere in this repository has ever reverse-parsed
this format, since every prior consumer used the tuple-keyed `delta_map_raw`
in-process. Part B's diagnostic is the first code needing this round-trip,
and the spec states no conversion procedure. A plausible wrong choice (e.g.
`str(v)` on a tuple, `"(1031, 1095)"` instead of `"[1031, 1095]"`) makes
every lookup fail identically; combined with the spec's own instruction to
handle "vertices with an unresolved neighbour... per a stated, pre-registered
rule, not silently dropped," a systematic key mismatch could complete without
crashing and report a diagnostic built on zero real matches.

**Required fix:** state the exact key-conversion procedure in the spec text
(e.g. `tuple(json.loads(key))` to go from archived key to vertex tuple, or
`str(list(v))` to go from a rebuilt vertex to the archived key — pick one
direction and name it as a diff-list-precision item per this campaign's
standing GD-9/GD-10 discipline). Additionally require a coverage assertion,
executed before any statistic is computed: the number of `delta_map` keys
successfully matched against the rebuilt graph's vertex set must equal the
already-archived `n_resolved`/`n_vertices` count for that prime (2437: 203,
3889: 324, 5737: 478, 7333: 611) — a free, already-available number sitting
in the exact file this diagnostic reads — and the run must halt with an
explicit error, not a silent partial result, if it does not match.

### PF-5 — [BLOCKING, folds into the required fix above] PART B: "C-CONNECTIVITY's floor(p/12) anchor" is a vertex-count check only and cannot verify edge structure; no archived adjacency exists to diff against anyway

See (f) above. `run_correctness_gates`'s C-CONNECTIVITY compares two
integers (`n_built == p // 12`); it is blind to which specific vertices are
adjacent. M-DEGSEQ and C-EDGELIST are the checks that probe edge structure in
this codebase, and the draft names neither as reused. Separately, no prior
run persisted `adjacency`, so "byte-identical to what was already validated"
cannot be checked by anything, reused or not — the achievable and correct
target is **correctness of this rebuild**, not bit-identity to an unrecorded
prior state.

**Required fix:** state explicitly that `degree_sequence_check` (M-DEGSEQ) is
re-run on all four rebuilt graphs (cheap, already-available function, zero
new code), and that each prime's `n_vertices` is cross-checked against the
**specific already-archived count** for that prime in
`RUN-SSIQ-a85692-b/raw-result.json` (2437→203, 3889→324, 5737→478, 7333→611),
not only the generic `floor(p/12)` formula. Reframe the "byte-identical"
language to "independently verified correct by M-DEGSEQ and the archived
per-prime vertex count," which is both accurate and achievable.

### PF-6 — [ADVISORY, but changes the required cross-check's design] PART B: the walk-trapped/structural-local-minimum gap is provably zero, not an open empirical question — run the cross-check on every vertex, not a sample

See (g) above. The frozen `greedy_descent_hitting_time`'s own documented
invariant (a strict-descent walk's predecessor always has strictly greater
delta, so it can never be excluded from a *smaller-delta* candidate set by
the non-backtracking rule) makes "trapped at w" exactly equivalent to "w is a
structural local minimum," for every vertex, unconditionally. Any observed
disagreement in the required cross-check is therefore conclusively a bug in
Part B's own new `is_structural_local_min` (most likely the key-format issue
named in PF-4), never a mechanism finding. Given the equivalence is exact and
the per-vertex cost is negligible for graphs of this size (≤620 vertices),
run the cross-check against every vertex with a resolved `delta_E` value, not
"a sample" — a sample risks missing a bug localized to a vertex subset (e.g.
F_p-rational vertices specifically), exactly the concern the launching task's
item (g) raises. Not blocking on its own, but should be applied alongside
PF-4's fix, since it is the cheapest available test of PF-4's fix actually
working.

### PF-7 — [ADVISORY] PART B: the "unresolved neighbour" handling branch is untestable against this batch's own real data

Directly confirmed: all four primes v5 uses (2437, 3889, 5737, 7333) have
`m_coverage_all_vertices_fraction == 1.0` — `delta_map` has an entry for
every vertex, so the "vertex with an unresolved neighbour" branch can never
execute this batch. The spec should say so explicitly (the branch's
correctness is specified, and should stay specified precisely — the safest
choice is to raise loudly if it is ever reached unexpectedly, since an
unexpected unresolved neighbour against this specific data would itself
signal a stale read or wrong prime), rather than implying the handling is
exercised. Same texture as `RT-BATCH-007.md` OBJ-3/F-5's untested-branch
caveat for CHECK 3.

### PF-8 — [ADVISORY] PART B: name explicitly that "fraction of structural local minima" and the archived "greedy trapped_fraction" are different statistics

See (h) above. Both are legitimate, but a future citation could conflate
them as corroborating measurements of the same thing; per PF-6's
equivalence, they are related but generally numerically different
quantities (many-to-one funneling inflates `trapped_fraction` relative to
the raw local-minimum density). State this explicitly in the successor
record reporting Part B's numbers.

---

## Required controls / checks before dispatch

- PF-1: `ols_hardened.py` must state, unambiguously, exactly how
  `bootstrap_gap_ci_v2` threads `ols_loglog_fit_v2` into its resampling loop
  (a genuinely new function, or a disclosed, scoped edit to the frozen
  `bootstrap_gap_ci`'s default-preserving signature), and
  `gd11_regression_test.json` must include a check that calls
  `bootstrap_gap_ci_v2` (not only `ols_loglog_fit_v2` standalone) against
  data reproducing the N=324/n=3 or N=611/n=6 anomaly and confirms the
  degenerate resample is discarded, not silently included (BLOCKING).
- PF-4: state the exact `delta_map` key ⇄ vertex-tuple conversion procedure
  as a diff-list-precision item, and require a hard-fail coverage assertion
  (matched-key count == the archived `n_resolved`/`n_vertices` for that
  prime) before any diagnostic statistic is computed (BLOCKING).
- PF-5: re-run `degree_sequence_check` (M-DEGSEQ) on all four rebuilt graphs
  and cross-check each prime's `n_vertices` against the specific
  already-archived count for that prime, not only the generic `floor(p/12)`
  formula; reframe "byte-identical vertex/edge structure" language
  accordingly (folds into PF-4's fix, BLOCKING as a pair).
- PF-6: run the structural-vs-walk cross-check against every vertex with a
  resolved `delta_E`, not a sample (advisory but recommended alongside the
  PF-4 fix, since it is the cheapest test of that fix).
- PF-7/PF-8: text-only additions, non-blocking.

## Counterexample or mutation

**PF-1's counterexample, executed directly against the actual, unchanged
`bootstrap_gap_ci`:** its signature `bootstrap_gap_ci(N_list,
median_greedy_list, median_random_list, rng, n_boot=2000)` contains no
fit-function parameter, and its body calls the bare name `ols_loglog_fit`
twice inside the resampling loop (confirmed by direct source read, lines
362–384). A hypothetical `bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci` (the
literal binding the draft's own text states) is therefore bit-identical to
the vulnerable original for every input, including the N=324/n=3 and
N=611/n=6 cases this same amendment's Part A is supposed to fix — a direct
falsifier of "PART A protects any future bootstrap CI computation" for the
specific, and most consequential, call path GD-11 names.

**PF-4's counterexample:** `delta_map["[1031, 1095]"] == 5` (confirmed
directly against the archived file) but `str((1031, 1095)) ==
"(1031, 1095)"` — a plausible, unstated wrong choice of key format
(`str(v)` on a tuple rather than `str(list(v))`) causes
`delta_map.get(str(v))` to return `None`/miss for every vertex, silently,
with no crash, in a run whose own `required_artifacts_note` claims "no new
delta_E search of any kind" and would show nothing anomalous in its budget
or timing.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense —
toy-scale gradient-existence infrastructure (Part A) and a graph-structural
diagnostic (Part B), `asymptotic_claim: null` throughout, correctly
inherited. The relevant baseline is this campaign's own instrument- and
fix-scrutiny discipline (GD-4 through GD-11): PF-1 and PF-4 are both, in
different code, the *exact* recurring failure shape this campaign's own
standing repairs (GD-9's "verify the control's comparison logic was ever
implemented," GD-10's "verify the fix actually calls the function it
validates," applied recursively) exist to catch — a fix/diagnostic that
*names* the vulnerable function correctly but never reaches the call site
that matters. This review clears that bar for both parts by tracing the
actual code (`bootstrap_gap_ci`'s real signature; `delta_map`'s real,
never-before-reverse-parsed JSON key format), not by trusting either part's
own prose description of itself.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (gradient-existence
screen, not a heuristic-conditional complexity claim) — attacked and held,
consistent with every prior review in this lineage. No finding here
implicates a numbered heuristic; every finding is a control/instrument-fidelity
gap (Part A: a numerical-guard wiring gap; Part B: a data-join precision gap
and a verification-scope gap).

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly); the per-attempt-cost × inverse-success-probability review does
not apply. The `900s`/`0.3` CPU-hour budget is realistic and generously
sized relative to EXP-SSIQ-58b642's own measured graph-build figures
(12–120s total) plus arithmetic on ≤620-vertex `delta_map` data for four
primes — no resource-bookkeeping concern, and none of PF-1/PF-4/PF-5/PF-6's
fixes materially change this (a `bootstrap_gap_ci_v2` regression check on
synthetic data, an M-DEGSEQ re-run on already-built graphs, and a full- rather
than sampled-vertex cross-check are all negligible relative to the stated
budget). The live concern is, again, evidentiary rather than resource cost:
PF-1 means a future real null-arm dispatch could silently include a spurious
bootstrap point-estimate with no budget/timing signal indicating a problem —
identical in shape to `RT-BATCH-007.md`'s own cost-model-challenge finding
about GD-11 itself, now shown to survive this amendment's own fix as
specified.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis. `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) is correctly stated and not exceeded. No scope-inflation
found. `objective_boundary`'s scoping of Part B as a diagnostic, not a claim,
is correctly stated and not contradicted elsewhere in the draft (PF-8's note
is about a future citation risk, not about anything in this draft
overclaiming). This amendment correctly bundles exactly the two actions
`DEC-20260805-6aa5c2`'s `next_action` named, on disjoint data and code paths
(confirmed directly: Part A touches only `descent_hitting_time.py`'s callers;
Part B touches only graph/`delta_map` data; neither references the other),
matching `RT-BATCH-007.md` Front 6's own ranking and bundling rationale.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level
gradient-existence screen, not a proof-oriented proposal. Attacked and held,
same verdict as every prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v5.yaml` as committed
at `c445c171`, `status: draft`: PART A's standalone guard replacement
(`max(xs) == min(xs)`) is correct and independently re-verified against both
of `RT-BATCH-007.md`'s own named anomaly cases (N=324/n=3, N=611/n=6) — but
the amendment's own text leaves the bootstrap-CI wiring question it names as
open genuinely unresolved, and the one concrete binding it does state
(`bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci`) is, by direct trace of the
actual unchanged `bootstrap_gap_ci` signature, a hollow fix that never
reaches the resampling call path where GD-11's most serious manifestation
occurs (PF-1, blocking). PART B's structural local-minimum diagnostic is
well-motivated and its data (`delta_map`, full coverage for all four primes
used) supports it, but its central data-join step — matching a freshly
rebuilt graph's tuple-keyed vertices against `delta_map`'s never-before-reverse-parsed
JSON string keys — has no stated conversion procedure and a plausible
mismatch fails silently (PF-4, blocking), and its stated graph-rebuild
verification (`floor(p/12)` vertex-count anchor alone) cannot detect an
edge-structure divergence and has no archived adjacency to diff against
regardless (PF-5, blocking, folds into PF-4's fix). The walk-trapped/structural-local-minimum
"gap" the draft's own pre-freeze note worries about is provably zero for the
frozen code as written — not an open empirical question — which means the
required cross-check should run against every vertex, not a sample, since
any disagreement it finds is conclusively an implementation bug (PF-6,
advisory but recommended). Two further advisory items (PF-7: the
unresolved-neighbour branch is untestable against this batch's actual data;
PF-8: the diagnostic's headline statistic is a different quantity from the
already-archived `trapped_fraction` and should not be read as corroborating
it) round out the review. None of these findings require redesigning either
part's mechanism, and all are fixable at zero new search cost.

## Next concrete action

Coordinator: before `status: approved` / setting `frozen_at`, require the
amendment text to (1) resolve PF-1 by naming, unambiguously, how
`bootstrap_gap_ci_v2` threads `ols_loglog_fit_v2` into its resampling loop
(a genuinely new function, since `bootstrap_gap_ci` has no injectable
fit-function parameter and the frozen module cannot be edited under the
amendment's own stated scope) and add a `bootstrap_gap_ci_v2`-level
regression check reproducing N=324/n=3 or N=611/n=6 to
`gd11_regression_test.json`; (2) resolve PF-4/PF-5 by stating the exact
`delta_map` key ⇄ vertex-tuple conversion procedure, requiring a hard-fail
coverage assertion against each prime's already-archived `n_resolved`/`n_vertices`
count, and re-running M-DEGSEQ (not only the `floor(p/12)` count check) on
each rebuilt graph; (3) apply PF-6 by running the structural-vs-walk
cross-check against every vertex with a resolved `delta_E`, not a sample;
(4) apply PF-7/PF-8 as text-only additions. Re-verify PF-1 and PF-4's
specific traces once the fixes are added, before freeze, per this campaign's
standing practice of tracing the fix, not merely trusting that text was
added (the exact discipline `RT-PREFREEZE-EXP-SSIQ-a85692-v4.md`'s own PF-1
required and `VAL-BATCH-007.md` §2 supplied independently). None of the four
requires new search or touches any already-archived run's data.

## Overall verdict

**DO-NOT-FREEZE.** Blocking, in priority order:

1. **[BLOCKING]** PF-1 — Part A's bootstrap-CI wiring is unresolved in the
   draft's own text, and the one concrete binding it states
   (`bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci`) is, by direct trace of the
   actual code, a hollow fix that never reaches the resampling call path
   GD-11's most serious manifestation occurs on.
2. **[BLOCKING]** PF-4 — Part B's `delta_map` key ⇄ rebuilt-graph-vertex
   join has no stated conversion procedure, no precedent anywhere in this
   codebase, and a plausible mismatch fails silently rather than loudly.
3. **[BLOCKING, pairs with PF-4's fix]** PF-5 — the stated graph-rebuild
   verification (`floor(p/12)` vertex-count anchor alone) cannot detect an
   edge-structure divergence and has no archived adjacency to check against
   regardless; M-DEGSEQ and the specific archived per-prime vertex count
   must be added.

PF-6, PF-7, PF-8 are advisory and do not block this dispatch on their own,
but PF-6 should be applied alongside PF-4's fix since it is the cheapest
available test that PF-4's fix actually works.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v5
  task_id: NOT SUPPLIED IN THE LAUNCHING HANDOFF; recorded as unsupplied rather than fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v5.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at snapshot c445c171: a bundled,
    two-part amendment to the frozen v4 contract (specification_v4.yaml,
    frozen 0b15e854) -- PART A hardens dht.ols_loglog_fit's degeneracy guard
    (GD-11's fix) via a new module ols_hardened.py (ols_loglog_fit_v2,
    max(xs)==min(xs) replacing sxx==0.0); PART B is a new
    trapping-mechanism diagnostic (deferred since BATCH-006) computing a
    graph-structural local-minimum property from already-committed
    delta_map data and freshly-rebuilt 2-isogeny graphs for four primes
    (2437, 3889, 5737, 7333).
  objections:
    - "PF-1 [BLOCKING]: dht.bootstrap_gap_ci (descent_hitting_time.py lines 362-384) has NO parameter through which a caller can substitute an alternate fit function, and calls the bare module-global name ols_loglog_fit twice inside its resampling loop. The draft's own inputs.gd11_fix_v5 text asserts bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci (a literal alias to the UNHARDENED original) in the same breath as admitting the wiring is an open question ('STATE EXPLICITLY WHICH, not left ambiguous'). Given the actual signature, the alternative it names ('pass ols_loglog_fit_v2 as an explicit parameter') is not achievable without editing the frozen bootstrap_gap_ci, which amendment_scope forbids. As literally written, the amendment's hardening never reaches the resampling call path where GD-11's most serious confirmed failure mode (a spurious nonzero gamma silently entering bootstrap_gap_ci's output, RT-BATCH-007.md Front 4) actually occurs -- exactly the exposure the next real null-arm dispatch faces. The required gd11_regression_test.json never calls bootstrap_gap_ci_v2 and so cannot detect this gap. Same shape as GD-9 (a control that structurally cannot fail) and GD-10 (a fix that never calls the function it claims to protect)."
    - "PF-4 [BLOCKING]: delta_map's on-disk keys are str(list(v)) (e.g. '[1031, 1095]', confirmed directly against RUN-SSIQ-a85692-b/raw-result.json and against compute_delta_e.py's delta_map_json_safe construction). No code anywhere in this repository has ever reverse-parsed this format back into vertex tuples -- every prior consumer used the tuple-keyed delta_map_raw in-process. Part B's diagnostic is the first code needing this round-trip, and the spec states no conversion procedure. A plausible wrong choice (str(v) on a tuple, '(1031, 1095)', instead of str(list(v)), '[1031, 1095]') makes every lookup fail identically; combined with the spec's own 'handled per a stated, pre-registered rule, not silently dropped' language for unresolved vertices, a systematic key mismatch could complete without crashing and report a diagnostic built on zero real matches."
    - "PF-5 [BLOCKING, pairs with PF-4]: run_correctness_gates's C-CONNECTIVITY (compute_delta_e.py), the check the draft names as reused for Part B's graph-rebuild verification, compares only n_built == p//12 -- two integers, blind to edge structure. Two graphs with identical vertex count but different adjacency would pass identically, directly confirming the launching task's own concern. Separately, no prior run persisted the graph's adjacency structure at all, so 'byte-identical to what was already validated' cannot be checked against anything, reused or not -- M-DEGSEQ (degree_sequence_check, cheap, already available) plus a cross-check against the specific already-archived per-prime vertex count (2437:203, 3889:324, 5737:478, 7333:611) is the correct, achievable substitute."
    - "PF-6 [ADVISORY, changes required-check design]: greedy_descent_hitting_time's own documented invariant (a strict-descent walk's predecessor always has strictly greater delta, so the non-backtracking exclusion can never remove a genuine smaller-delta candidate) makes 'trapped at w' EXACTLY equivalent to 'w is a structural local minimum', for every vertex, unconditionally -- a code identity, not an open empirical question the draft's sample-based cross-check needs to bound. Any disagreement the cross-check finds is therefore conclusively a bug in Part B's own new code (most likely PF-4's key-format issue). Recommend running the cross-check against every vertex (negligible extra cost for graphs <=620 vertices), not a sample, since a sample risks missing a bug localized to a vertex subset."
    - "PF-7 [ADVISORY]: all four primes v5 uses have m_coverage_all_vertices_fraction == 1.0 in RUN-SSIQ-a85692-b -- the 'vertex with an unresolved neighbour' handling branch the spec requires can never execute against this batch's real data, so its correctness is specified but untestable here; the successor record should say so."
    - "PF-8 [ADVISORY]: Part B's headline 'fraction of vertices that are structural local minima' is a different statistic from the already-archived greedy trapped_fraction (per PF-6's equivalence, trapped_fraction counts walks that terminate at ANY local minimum, a many-to-one funnel, not the raw density of local-minimum vertices) -- should not be read as corroborating or replicating it in a future citation."
  required_controls:
    - "PF-1: ols_hardened.py must state unambiguously how bootstrap_gap_ci_v2 threads ols_loglog_fit_v2 into its resampling loop (a genuinely new function, since bootstrap_gap_ci has no injectable fit-function parameter), and gd11_regression_test.json must add a check calling bootstrap_gap_ci_v2 (not only ols_loglog_fit_v2 standalone) against data reproducing N=324/n=3 or N=611/n=6 and confirm the degenerate resample is discarded, not silently included -- BLOCKING."
    - "PF-4/PF-5: state the exact delta_map key <-> vertex-tuple conversion procedure as a diff-list-precision item; require a hard-fail coverage assertion (matched-key count == the archived n_resolved/n_vertices for that prime) before any statistic is computed; re-run degree_sequence_check (M-DEGSEQ) on all four rebuilt graphs and cross-check each prime's n_vertices against its specific already-archived count, not only the generic floor(p/12) formula -- BLOCKING."
    - "PF-6: run the structural-local-minimum-vs-walk-trapped cross-check against every vertex with a resolved delta_E, not a sample -- advisory, recommended alongside the PF-4 fix as the cheapest available test that the fix works."
  counterexample_or_mutation: >-
    PF-1: bootstrap_gap_ci's actual signature (N_list, median_greedy_list,
    median_random_list, rng, n_boot=2000) has no fit-function parameter and
    calls the bare name ols_loglog_fit twice inside its resampling loop
    (descent_hitting_time.py lines 362-384, confirmed by direct read); a
    literal bootstrap_gap_ci_v2 = dht.bootstrap_gap_ci -- the one concrete
    binding the draft's text states -- is bit-identical to the vulnerable
    original for every input, including N=324/n=3 and N=611/n=6, a direct
    falsifier of "PART A protects any future bootstrap CI computation" for
    the exact call path GD-11 names as the live risk.
    PF-4: delta_map["[1031, 1095]"] == 5 (confirmed against the archived
    file) but str((1031, 1095)) == "(1031, 1095)" -- a plausible, unstated
    wrong key-format choice causes delta_map.get(str(v)) to miss on every
    vertex, silently, with no crash and nothing anomalous in budget/timing,
    in a run whose own required_artifacts_note claims "no new delta_E
    search of any kind."
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure and diagnostic work, asymptotic_claim null
    throughout, correctly inherited). The relevant baseline is this
    campaign's own instrument- and fix-scrutiny discipline (GD-4 through
    GD-11): PF-1 and PF-4 are both the exact recurring failure shape this
    campaign's standing repairs exist to catch -- a fix/diagnostic that
    names the vulnerable function or data source correctly but never
    reaches the call site or key format that actually matters -- confirmed
    here by tracing the actual code (bootstrap_gap_ci's real signature,
    delta_map's real, never-before-reverse-parsed JSON key format) rather
    than trusting either part's own prose description of itself.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic; every finding is a control/instrument-fidelity gap."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is realistic and generously sized relative to EXP-SSIQ-58b642's own measured graph-build figures (12-120s) plus arithmetic on <=620-vertex delta_map data for four primes; none of the required fixes (a bootstrap_gap_ci_v2 regression check, an M-DEGSEQ re-run, a full- rather than sampled-vertex cross-check) materially change this."
    - "The live concern remains evidentiary: PF-1 means a future real null-arm dispatch could silently include a spurious bootstrap point-estimate with no budget/timing signal indicating a problem -- identical in shape to RT-BATCH-007.md's own cost-model finding about GD-11, now shown to survive this amendment's own fix as specified."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded. No scope-inflation found."
    - "objective_boundary's scoping of Part B as a diagnostic, not a claim, is correctly stated and not contradicted elsewhere in the draft (PF-8 is a future-citation risk, not an overclaim in this draft itself)."
    - "This amendment correctly bundles exactly the two actions DEC-20260805-6aa5c2's next_action named, on disjoint data and code paths, matching RT-BATCH-007.md Front 6's own ranking and bundling rationale -- independently reconfirmed here."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v5.yaml as committed
    at c445c171, status: draft: PART A's standalone guard replacement
    (max(xs)==min(xs)) is correct, independently re-verified against both of
    RT-BATCH-007.md's own named anomaly cases (N=324/n=3, N=611/n=6) -- but
    the amendment leaves its own flagged bootstrap-CI wiring question
    unresolved, and its one concrete stated binding is a hollow fix that
    never reaches the resampling call path GD-11's most serious
    manifestation occurs on (PF-1, blocking). PART B's structural
    local-minimum diagnostic is well-motivated and its data (delta_map, full
    coverage for all four primes used) supports it, but its central
    data-join step has no stated key-conversion procedure and a plausible
    mismatch fails silently (PF-4, blocking), and its stated verification
    (a vertex-count-only check) cannot detect an edge-structure divergence
    and has no archived adjacency to diff against regardless (PF-5,
    blocking). The walk-trapped/structural-local-minimum "gap" the draft's
    own pre-freeze note treats as open is provably zero given the frozen
    code's own documented invariant, which argues for a full- rather than
    sampled-vertex cross-check (PF-6, advisory). Two further advisory items
    (PF-7, PF-8) round out the review. None require redesigning either
    part's mechanism; all are fixable at zero new search cost.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text to (1) resolve PF-1 by naming unambiguously how bootstrap_gap_ci_v2
    threads ols_loglog_fit_v2 into its resampling loop and add a
    bootstrap_gap_ci_v2-level regression check to gd11_regression_test.json;
    (2) resolve PF-4/PF-5 by stating the exact delta_map key<->vertex-tuple
    conversion procedure, a hard-fail coverage assertion against each
    prime's archived n_resolved/n_vertices, and an M-DEGSEQ re-run on each
    rebuilt graph; (3) apply PF-6 (full-vertex, not sampled, cross-check);
    (4) apply PF-7/PF-8 as text-only additions. Re-verify PF-1 and PF-4's
    specific traces once fixed, before freeze, per this campaign's standing
    practice of tracing the fix rather than trusting that text was added.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v5.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Executed directly (not merely traced): recomputed sxx and
    max(xs)==min(xs) for N=324/n=3, N=611/n=6, N=500/n=3, and N in
    {203,324,478,611}/n=4 from first principles (independent of any prior
    review's reported numbers) to confirm PF-1(b)'s guard-replacement
    correctness. Loaded RUN-SSIQ-a85692-b/raw-result.json programmatically
    and inspected phase_minus1_real_search's delta_map structure, key
    format, and coverage fields for all five primes (2437, 3889, 5737,
    7333, 8893) directly, not from any prose description. Direct source
    reads (not summaries) of dht.bootstrap_gap_ci/ols_loglog_fit,
    build_isogeny_graph.py's build_graph_bfs/degree_sequence_check/
    neighbors_2isogenous/seed_j_invariant, and compute_delta_e.py's
    build_all_graphs/run_correctness_gates/delta_map_json_safe
    construction, cross-referenced against grep across the implementation
    tree to confirm no prior code reverse-parses delta_map's JSON string
    keys. No graph built, no delta_E search run, no file written outside
    this report.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-008/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v5.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v5.yaml itself)
    and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
