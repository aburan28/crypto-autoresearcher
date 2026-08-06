# RT-PREFREEZE-EXP-SSIQ-a85692-v8 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v8.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-011

**Reviews `experiments/EXP-SSIQ-a85692/specification_v8.yaml` at `status: draft`,
`pre_freeze_review.status: PENDING`, a working-tree draft not yet frozen,
under task `TASK-20260806-b4b3b2`.** Per this task's operating rules, only a
Coordinator-committed snapshot of a *frozen* artifact is treated as durable
research evidence; this is advisory pre-freeze input, matching this
lineage's established practice for v6/v7. It changes nothing under
`experiments/EXP-SSIQ-a85692/` and commits nothing.

**This is the first amendment since `specification_v4.yaml` that spends real
new delta_E search compute** (up to 1 CPU-hour) rather than re-analyzing
already-archived data, so this review verifies every code-path claim by
direct trace of the actual implementation files, not by trusting the
draft's own prose — including tracing which script actually produced the
archived comparison baseline, not merely which script the draft says it did.

Read in full: `AGENTS.md`, `CLAUDE.md`, `agents/red-team.md`;
`specification_v8.yaml` (266 lines); `specification_v6.yaml`/`v7.yaml`'s
PF-6 text and history; `RT-BATCH-010.md`; `RT-PREFREEZE-EXP-SSIQ-a85692-v7.md`.
Directly read (not trusted from prose): `compute_delta_e.py`
(`two_sided_search`, `build_smooth_table`, `run_phase_minus1_on_confirmatory_set`,
in full); `compute_delta_e_v2.py`'s own `run_phase_minus1_on_confirmatory_set`
(`real_execution_budget_v2`) and its module-docstring diff list against v1;
`build_isogeny_graph.py`'s `Fp2Field`/`build_graph_bfs` (vertex
representation); `delta_e_permutation_null_control_v7.py` in full
(`local_min_and_depth`, `depth0_fraction`, `rebuild_and_verify`,
`run_for_prime`); `trapping_diagnostic_v5.py`'s `load_archived_prime_data`/
`build_graph_for_prime`; `RUN-SSIQ-a85692-b/raw-result.json`'s
`phase_minus1_real_search["2437"]` entry and `RUN-SSIQ-a85692-b/manifest.yaml`
and `command.txt` directly (to establish provenance of the archived
comparison data).

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
    lineage. Does not upgrade the campaign's evidence tier and does not
    itself satisfy or advance a closure quorum.
```

---

## Bottom line up front

**This draft should NOT be frozen as written.** The statistical intent (hold
prime and graph fixed, vary only the delta_E search's RNG/budget design) is
sound in principle, and the seed-derivation formula I was specifically asked
to check is safe. But two code-verified defects would either (a) waste the
entire real-compute spend on an uncaught crash that discards the amendment's
whole headline result, or (b) mean the draft is testing against — and
justifying its budget against — the wrong archived procedure. Both are
fixable at zero additional new search cost (they are specification/wiring
fixes, not redesigns), but must be fixed before dispatch, given this run
actually burns wall-clock and CPU that cannot be recovered if the run fails
partway.

1. **PF-1 [BLOCKING, compute-loss risk].** PART A explicitly anticipates
   that its new fixed-15s-per-vertex search may leave some of the 194
   non-F_p-rational vertices at p=2437 unresolved ("REQUIRED COVERAGE
   REPORTING... `<100% coverage`... is a possible, informative outcome, not
   a failure"). PART B then feeds PART A's (possibly-partial) new delta_map
   straight into `delta_e_permutation_null_control_v7.depth0_fraction`,
   imported **unchanged**, and explicitly **not** through
   `run_for_prime`/`rebuild_and_verify` (the required_artifacts_note
   imports only `depth0_fraction` and `summary_stats`). I read
   `depth0_fraction`/`local_min_and_depth` directly: the loop is `for v in
   vertices: ... delta_map[v] <= m`, with **no existence check on
   `delta_map[v]` for v itself** — only a guard on neighbours (`if u not in
   delta_map: raise PermutationNullControlError("...never a legitimate data
   gap")`). If PART A leaves even one vertex unresolved, PART B's very
   first call — `depth0_fraction` on the REAL (unpermuted) new delta_map,
   before any of the 1000 null trials run — either raises a raw `KeyError`
   (if the unresolved vertex itself is the one being tested) or the
   imported guard's `PermutationNullControlError`, whose own message
   asserts the gap is "never legitimate" — which is false in exactly the
   scenario PART A says is expected. Either way, PART B produces **no**
   result: not the REAL_DEPTH0_FRACTION, not one of the 1000 null trials,
   and (since `base_values = list(delta_map.values())` is also short) the
   null-permutation construction (`dict(zip(vertices, shuffled))`) would
   silently truncate the same way even if the crash were caught later. This
   is not a remote edge case: see PF-5 below for why <100% coverage is a
   live possibility under this specific budget design, and it is the exact
   outcome PART A's own comparison section names as "genuinely possible"
   (`n_archived_resolved_new_was_not`). Given this amendment's entire
   purpose is PART B's PERSISTS/WEAKENS/AMBIGUOUS headline, an uncaught
   crash here means up to 3600s of real compute buys **zero** interpretable
   result. **Required fix**: PART B must state, before dispatch, exactly
   what happens when PART A's coverage is <100% — e.g. either (a) PART B is
   gated on PART A reaching full coverage, with an explicit
   `COVERAGE-SHORTFALL` outcome label distinct from
   PERSISTS/WEAKENS/AMBIGUOUS if it does not, or (b) PART B's driver
   explicitly restricts `vertices`/`adjacency` to the resolved subgraph
   with a precisely pinned procedure (and states how that changes
   comparability to v7's full-194-vertex REAL_DEPTH0_FRACTION=1.0). Either
   way this must be pre-registered text, not something an Executor
   discovers by hitting the exception after spending the budget.

2. **PF-2 [BLOCKING, mis-cited baseline].** The draft's `amendment_scope`
   and its inherited PF-6 text both describe "the ORIGINAL procedure" as
   `compute_delta_e.py`'s `run_phase_minus1_on_confirmatory_set`, quoting
   its exact line `per_vertex_cap = min(remaining, t_prime)` — this is v1's
   code, confirmed present verbatim at `compute_delta_e.py:396`. But I
   traced `RUN-SSIQ-a85692-b/manifest.yaml` and `command.txt` directly: the
   archived p=2437 delta_map this amendment diffs against was produced by
   `compute_delta_e_v2.py python3 ... --out .../RUN-SSIQ-a85692-b/raw-result.json`,
   whose **own, differently-implemented** `run_phase_minus1_on_confirmatory_set`
   (`real_execution_budget_v2`, confirmed by direct read,
   `compute_delta_e_v2.py:212-296`) uses a **single aggregate cross-prime**
   wall-clock counter (`remaining_now = remaining - elapsed_this_prime`,
   *no* `t_prime`/`min()` at all) rather than v1's fixed
   T_PRIME-per-prime cap. The two scripts share the same
   `neighbors_ell_isogenous`/`build_smooth_table`/`two_sided_search`
   (confirmed: v2 imports these unchanged from v1) and the same shared,
   sequentially-advancing `rng_search = random.Random(seeds[0]*1000003+p)`
   line — so the qualitative confound PF-6 names (shared/sequential RNG +
   shrinking per-vertex cap) is genuinely present in the data being
   compared against — but the draft never once names `compute_delta_e_v2.py`
   or its actual budget formula anywhere in its text, and its
   `required_artifacts_note` diff-list states only "Does NOT import or call
   compute_delta_e.run_phase_minus1_on_confirmatory_set... anywhere,"
   which is true but answers the wrong question: it never disclaims or
   even mentions `compute_delta_e_v2.run_phase_minus1_on_confirmatory_set`,
   the function that actually generated the exact archived p=2437 data this
   amendment diffs against. This is exactly the "explicit,
   code-verified function-level diff" failure mode this lineage's GD-9/GD-10
   standing repair exists to catch (and which even `RT-PREFREEZE-EXP-SSIQ-a85692-v7`'s
   own PF-6 discussion missed — it also cites only v1's file). **Required
   fix**: correct the amendment_scope/required_artifacts_note text to name
   `compute_delta_e_v2.py`'s `real_execution_budget_v2` mechanism as the
   actual originating procedure for `RUN-SSIQ-a85692-b`'s p=2437 data, and
   re-derive the budget-margin rationale (PF-4 below) against that
   mechanism rather than v1's.

Six further findings are advisory (do not, by themselves, block freeze, but
should be applied as text-only or small-scope fixes given real compute is at
stake):

3. **PF-3 [ADVISORY, strong — operational compute-loss risk].** This
   amendment's own budget note cites `RUN-SSIQ-a85692-b`'s execution
   history, but only for the 284.88s figure — it omits the same run's own
   documented operational precedent: `RUN-SSIQ-a85692-b`'s `manifest.yaml`
   discloses that **two of its three launch attempts were killed by an
   environment-imposed background-process lifetime limit "(empirically
   ~60-65 minutes)"** before writing any result, and only succeeded on a
   third attempt using a `setsid nohup ... disown` detachment workaround.
   This amendment's own `wall_clock_seconds_per_run: 3600` (**exactly 60
   minutes**) sits at the low edge of that same empirically-documented kill
   window, on the very same experiment lineage. The draft's
   `required_artifacts_note`/budget text says nothing about needing the
   same detachment technique. Given the expected case finishes in ~5
   minutes (284.88s-scale) this is unlikely to bite in the common case, but
   the draft's own stated worst case (2910s ≈ 48.5 minutes of search alone,
   plus overhead) sits uncomfortably close to a limit that has already
   killed two of three attempts at a similar scale in this exact
   experiment's own history. Free to fix: add an explicit instruction to
   launch this run with the same detachment pattern proactively, rather
   than risk repeating the two wasted attempts.

4. **PF-4 [ADVISORY].** Because the archived p=2437 search (under
   `compute_delta_e_v2.py`, PF-2) was the **first** prime processed against
   a fresh 3600s aggregate pool, and finished 194/194 in 284.88s (≈7.9% of
   its available slice), the "shrinking per-vertex budget" component of the
   confound almost certainly never actually bound any vertex in the
   specific archived data this amendment diffs against — no vertex was
   plausibly ever close to running out of time. The draft frames the probe
   as testing removal of "the search procedure's own shared RNG **and**
   shrinking time budget" as a bundled pair, but for this one prime's
   archived data the operative confound is almost certainly the shared,
   sequentially-advancing RNG alone. This doesn't invalidate the design
   (PF-6 itself names the confound as a package, and testing the package is
   defensible), but the draft should disclose that a PERSISTS or WEAKENS
   result here mainly speaks to the RNG-sharing mechanism, not to budget
   scarcity, since budget scarcity was not actually active in the baseline
   being compared against.

5. **PF-5 [ADVISORY, connects to PF-1].** The new probe's **fixed** 15s
   per-vertex cap is, in the plausible-worst-case sense, *tighter* than
   what the archived run effectively had available for early vertices of a
   first-processed prime (up to the full, only-slowly-shrinking ~3600s
   aggregate pool). If any vertex under the new independent-RNG draws needs
   more than 15s (plausible — this is the same "RNG-design-driven
   variance" the draft itself invokes to justify a 10x margin over the
   *average*), the new procedure could produce **lower** coverage than the
   100%-covered archived baseline purely because its worst-case ceiling is
   smaller, not because of anything diagnostic about PF-6. If PF-1's fix
   allows PART B to proceed on a partial new delta_map, the WEAKENS branch
   text should distinguish "REAL_DEPTH0_FRACTION dropped because of a
   coverage shortfall under a tighter cap" from "REAL_DEPTH0_FRACTION
   dropped with full coverage" — these are different findings about
   different things.

6. **PF-6 [ADVISORY].** The `+/-10` percentage-point margin-tolerance band
   is pre-registered (satisfying the process requirement) but its *width*
   is not derived from any measured or distributional argument — no
   estimate of how much the 23.1pp archived margin itself would vary under
   a different permutation seed or a slightly different real-value
   multiset is given, and 10pp is ~43% of the 23.1pp anchor it is applied
   to (the tightest of the four primes per `RT-BATCH-010`'s own table).
   Separately, the three-way PERSISTS/WEAKENS/AMBIGUOUS partition has a gap
   at one edge: a result with REAL_DEPTH0_FRACTION >= 0.95 but a margin
   **wider** than 23.1+10=33.1pp (i.e., an even *stronger* signal than
   archived) satisfies neither PERSISTS's `+/-10pp` band nor WEAKENS's
   "materially lower," and falls to AMBIGUOUS by the letter of the rule,
   though intuitively that outcome supports (or strengthens) PERSISTS. This
   is a narrow, probably-unlikely case, but the pre-registration is
   silent on it, and the task's own instruction to check for a hidden
   researcher-degree-of-freedom is best answered by naming this edge now,
   before the result is known.

7. **PF-7 [VERIFIED SAFE — question 2, no defect found].** Traced
   `build_isogeny_graph.py`'s `Fp2Field`/`build_graph_bfs` directly: every
   graph vertex is already a plain 2-tuple of Python `int`s, `(a, b)` with
   `a, b` `in [0, p)`. `tuple(int(c) for c in vertex)` on such a tuple is a
   harmless identity coercion, not a silent-failure risk. Distinct vertices
   have distinct `(a, b)` pairs, so `"%r" % (tuple(...),)` produces distinct
   strings per vertex, and SHA-256 truncated to 8 bytes (64 bits) is
   astronomically collision-safe for 194 vertices (birthday bound
   ≈194²/2⁶⁵). `BASE_SEED = 20260811` is confirmed distinct from every
   other pinned seed role in this lineage (`SEEDS = [20260805, 11, 977]`,
   `PERMUTATION_SEED = 20260806`). No fix needed; recorded here so this
   check does not need re-deriving in a future round.

8. **PF-8 [ADVISORY].** PART A never explicitly states that it re-runs the
   two-part graph-identity check (`degree_sequence_check` +
   rebuilt-vertex-count match against `archived_n_vertices`) that
   `delta_e_permutation_null_control_v7.rebuild_and_verify` established as
   required — it relies implicitly on `build_graph_for_prime`'s seed
   determinism. Low risk (the seed is pinned and this construction is
   reused unchanged from every prior amendment since v5), but inconsistent
   with this lineage's own "state every verification explicitly" discipline
   that produced v6/v7's own PF-1 fixes.

---

## (1) Is the core experimental design actually sound as a test of PF-6? [Q1]

**Yes in intent, with two qualifications now on the record (PF-2, PF-4).**
`two_sided_search`'s own signature (`field, source_j, target_j, rng, q, L, X,
time_budget_seconds`) confirms it is a pure function of its parameters — no
internal RNG construction, no hidden global state — so holding `field`,
`source_j`, `target_j` (= `field.frobenius(v)`), `q`, `L`, `X` fixed and
varying only `rng`/`time_budget_seconds` genuinely isolates those two axes
within `two_sided_search`/`build_smooth_table` themselves; I found no other
parameter the draft leaves uncontrolled inside those two functions. The
confound with real teeth is not inside `two_sided_search` but in what the
draft calls "the ORIGINAL procedure": as PF-2 establishes, that is actually
`compute_delta_e_v2.py`'s `real_execution_budget_v2`, not v1's function the
draft names — and as PF-4 establishes, for this specific archived prime the
budget-shrinking half of the confound was very likely never actually
binding, so this probe's discriminating power is concentrated in the
RNG-sharing half. None of this breaks the design; it means the citation
needs correcting and the interpretation needs one added caveat.

## (2) Is the per-vertex seed-derivation formula well-specified and
collision-free? [Q2]

**Yes — see PF-7 above.** Verified safe by direct trace against the actual
vertex representation.

## (3) Is the budget actually justified? [Q3]

**The arithmetic is correct; the citation underlying it is wrong (PF-2), and
one operational risk is undisclosed (PF-3).** Independently recomputed:
`284.88387155532837 / 194 = 1.469...`s/vertex (matches the draft's "~1.47"),
`15 / 1.469 ≈ 10.2×` (matches "~10x"), `194 * 15 = 2910`s worst case (< 3600s
cap, ~690s margin including graph-rebuild/permutation-control overhead —
this bound is correctly derived and does hold), `3600 / 284.88 ≈ 12.6×`
(matches the note's "~12.6x"). So the run **cannot** exhaust its own 3600s
overall cap purely from the vertex-search loop as specified (194 vertices ×
15s fixed, no early exit, is bounded by construction at 2910s). The
undisclosed risk is external, not arithmetic: PF-3's ~60-65-minute
background-process kill window, empirically measured on this exact
experiment lineage at a very similar scale.

## (4) Are the PERSISTS/WEAKENS/AMBIGUOUS thresholds well-chosen? [Q4]

**Pre-registered and mostly reasonable; two soft spots, PF-6 above.** The
0.95 floor correctly classifies a hypothetical 0.97 as PERSISTS-eligible on
its own (0.97 ≥ 0.95), so the specific concern in the task prompt about 0.97
being force-labeled AMBIGUOUS does not materialize under the rule as
literally written — that clause is fine. The genuine gaps are the
undefended width of the ±10pp band and the AMBIGUOUS-by-default treatment of
an unexpectedly *stronger* margin, both named in PF-6.

## (5) Do PART A/PART B have the same failure-handling precision this
lineage's v6/v7 needed multiple rounds to reach? [Q5]

**No — this is the single biggest regression, and it is worse than v6/v7's
own instances of this defect class because it is not merely ambiguous prose
but a traced, executable crash path (PF-1).** v6/v7's blocking findings
(PF-1/PF-2 in `RT-PREFREEZE-EXP-SSIQ-a85692-v7`) were genuine gaps but left
an Executor with two *plausible readings* of ambiguous text. Here, PART A
explicitly anticipates an outcome (partial coverage) that PART B's actual,
traced code path cannot survive without crashing, and the draft's own
`required_artifacts_note` confirms PART B deliberately imports only the two
low-level functions (`depth0_fraction`, `summary_stats`) and not the
higher-level `rebuild_and_verify`/`run_for_prime` wrapper that would have
caught this. This is exactly the "unscoped anomaly branch" shape the task
asked about, now instantiated as an actual crash risk rather than a reading
ambiguity.

## (6) Other underspecification or risk of wasting real compute [Q6]

Covered above: PF-3 (background-process kill window precedent), PF-5
(tighter worst-case per-vertex ceiling than the archived baseline
effectively had), PF-8 (implicit rather than explicit graph-identity
re-verification in PART A).

---

## Objections

- **OBJ-1 [PF-1, BLOCKING]:** PART B feeds PART A's own possibly-partial new
  delta_map directly into `delta_e_permutation_null_control_v7.depth0_fraction`
  (imported unchanged, bypassing `rebuild_and_verify`'s coverage gate),
  whose `local_min_and_depth` has no existence guard on `delta_map[v]` for
  v itself. Any unresolved vertex under PART A's fixed-15s search crashes
  PART B's very first call (the REAL, unpermuted `depth0_fraction`), before
  any of the 1000 null trials run, discarding the amendment's entire
  headline result and the compute spent producing it.
- **OBJ-2 [PF-2, BLOCKING]:** The draft's "ORIGINAL procedure" text (and its
  inherited PF-6 text) names `compute_delta_e.py`'s
  `run_phase_minus1_on_confirmatory_set` and its literal
  `per_vertex_cap = min(remaining, t_prime)` formula, but
  `RUN-SSIQ-a85692-b/manifest.yaml`/`command.txt` confirm the archived
  p=2437 data was actually produced by `compute_delta_e_v2.py`'s different
  `real_execution_budget_v2` (a single aggregate cross-prime counter, no
  `t_prime`). The two functions share the same shared/sequential RNG
  pattern (so PF-6's underlying concern is not invalidated), but the
  specific code artifact cited is the wrong one, violating this lineage's
  own GD-9/GD-10 explicit-function-level-diff standard.
- **OBJ-3 [PF-3, ADVISORY, strong]:** The 3600s budget sits at the low edge
  of an empirically-documented ~60-65-minute background-process kill window
  that already killed two of three launch attempts of the exact run
  (`RUN-SSIQ-a85692-b`) this amendment compares against; the draft does not
  instruct the Executor to use the detachment workaround proactively.
- **OBJ-4 [PF-4, ADVISORY]:** For the specific archived p=2437 data, the
  budget-shrinking half of PF-6's named confound was very likely never
  actually binding (100% coverage used only ~7.9% of an up-to-3600s
  aggregate pool); the probe's discriminating power is concentrated in the
  RNG-sharing half, and the draft should say so.
- **OBJ-5 [PF-5, ADVISORY]:** The new fixed 15s cap is plausibly tighter,
  in the worst case, than what the archived run's shrinking-but-generous
  aggregate budget provided for early vertices — a coverage-driven WEAKENS
  would not carry the same interpretation as a full-coverage WEAKENS.
- **OBJ-6 [PF-6, ADVISORY]:** The ±10pp band's width has no stated
  statistical basis and is ~43% of the 23.1pp anchor it bounds; the
  three-way outcome partition has an undefined edge (fraction ≥0.95, margin
  wider than the ±10pp band) that falls to AMBIGUOUS by default though it
  intuitively supports PERSISTS.
- **OBJ-7 [PF-7, VERIFIED SAFE]:** No defect found in the seed-derivation
  formula by direct trace of vertex representation, seed distinctness, and
  hash-truncation collision risk.
- **OBJ-8 [PF-8, ADVISORY]:** PART A does not explicitly state it re-runs
  `rebuild_and_verify`'s graph-identity checks before searching.

## Required controls

- Before freeze: PF-1 must be resolved — state exactly what PART B does
  when PART A's new delta_map is not full coverage (gate-and-label
  distinctly, or explicitly restrict the domain with a pinned procedure).
- Before freeze: PF-2 must be corrected — name `compute_delta_e_v2.py`'s
  `real_execution_budget_v2` as the actual originating procedure for the
  archived comparison data, and re-derive the budget-margin rationale
  against it.
- Strongly recommended before dispatch (PF-3): instruct the Executor to
  launch via the same detached execution pattern (`setsid`/`nohup`/`disown`)
  `RUN-SSIQ-a85692-b` needed, given this run's budget sits at the edge of
  the same empirically-documented kill window.
- Text-only, zero cost (PF-4/PF-5/PF-6/PF-8): disclose that the archived
  baseline's budget-scarcity component was very likely non-binding for
  p=2437; note that a coverage-driven WEAKENS differs from a
  full-coverage WEAKENS; justify or narrow the ±10pp band and close the
  AMBIGUOUS-by-default edge case; state explicitly that PART A re-runs the
  graph-identity check.

## Counterexample or mutation

**PF-1's counterexample, concretely constructible:** suppose PART A's
independent-RNG search resolves 193 of 194 non-F_p-rational vertices at
p=2437 within their fixed 15s budgets (a single unlucky RNG draw exceeding
15s is entirely plausible given the draft's own "RNG-design-driven
variance" justification for a 10x margin). PART B's driver calls
`depth0_fraction(new_delta_map, g["vertices"], g["adjacency"])` — since
`new_delta_map` is missing the one unresolved vertex, the loop `for v in
vertices` reaches that vertex and evaluates `delta_map[v] <= m`, raising an
uncaught `KeyError` (the vertex itself, not a neighbour, so
`local_min_and_depth`'s only guard — on neighbours — does not fire). PART B
terminates with no REAL_DEPTH0_FRACTION and none of 1000 null trials
computed; `probe_permutation_null_control.json` cannot be written as
specified. This is directly constructible from the draft's own stated
design (fixed 15s cap, no PART B coverage gate) and does not require an
adversarial or contrived input.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this
remains toy-scale statistical-control work with `asymptotic_claim: null`.
The relevant baseline is this lineage's own established specification
discipline (v6/v7's PF-1/PF-2/PF-3/PF-7 unscoped-branch standard) and, new
to this review, an actual runtime/code trace of what the imported function
does when its precondition is violated — a stronger check than v6/v7's
reviews performed, made necessary because this amendment is the first to
spend real compute the campaign cannot get back if the run fails partway.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held. No numbered heuristic is implicated; `asymptotic_claim:
null` throughout, unchanged.

## Cost model challenges

The headline budget arithmetic (10x per-vertex margin, 2910s worst-case
search bound, 12.6x total margin over the archived measurement) is
independently re-derived here and confirmed correct (Q3 above). What is not
correct is the citation underlying it (PF-2: the "original" figure being
compared against is real and accurately transcribed — `wall_seconds_used =
284.88387155532837`, `n_non_fp_rational = 194`, both confirmed directly
against `RUN-SSIQ-a85692-b/raw-result.json` — but the *procedure* that
produced it is mis-attributed), and the arithmetic does not account for the
documented ~60-65-minute infrastructure kill window this exact run history
already hit twice (PF-3) — an infrastructure risk, not a mathematical cost
error, but a real risk to the compute actually being spent.

## Reduction and scope challenges

No scheme from any affected-vs-safe list appears anywhere in this
amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly stated
and not exceeded. `OBJECTIVE_BOUNDARY` correctly scopes a PERSISTS result to
"THIS ONE PRIME ONLY," not extending to the other three primes or to
`H-SSIQ-36e970`/lever L4 — no scope inflation found.

## Proof architecture challenges

Not applicable — direct instrument-level statistical/search-procedure
control, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited
unchanged, attacked and held).

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v8.yaml` as a draft,
not yet frozen: the intended experimental design (hold prime/graph fixed,
vary only the delta_E search's RNG-sharing and budget-shape) is a sound and
appropriately narrow test of PF-6's named confound, and the per-vertex
seed-derivation formula is verified safe by direct code trace (PF-7). Two
blocking, code-verified defects prevent freezing as written: PART B's
imported `depth0_fraction` call has no defined behavior, and in fact
crashes on direct trace, when fed the partial-coverage new delta_map PART A
explicitly anticipates as a possible outcome (PF-1) — a defect that would
discard the entire real-compute spend and the amendment's whole headline
result, not merely produce an ambiguous record; and the draft's own
characterization of "the ORIGINAL procedure" it is testing against and
sizing its budget relative to names the wrong script — `compute_delta_e.py`
rather than the `compute_delta_e_v2.py` that actually produced
`RUN-SSIQ-a85692-b`'s archived p=2437 data (PF-2), a citation error this
lineage's own GD-9/GD-10 standard treats as blocking. Neither defect
requires redesigning the underlying control; both are specification/wiring
fixes at zero additional search cost. Five further findings (PF-3 through
PF-6, PF-8) are advisory but, given real compute is at stake, should be
applied in the same revision pass, particularly PF-3 (an empirically
documented infrastructure risk specific to this exact experiment's own
history at a very similar budget scale).

## Next concrete action

Coordinator: return this draft for one revision round applying PF-1
(state PART B's exact behavior under partial PART A coverage, with a
distinct outcome label if it gates rather than proceeds) and PF-2 (correct
the cited "ORIGINAL procedure" to `compute_delta_e_v2.py`'s
`real_execution_budget_v2` and re-derive the budget-margin note against
it), plus PF-3 (add the detachment-launch instruction given the documented
~60-65-minute kill-window precedent on this exact experiment) and the
remaining text-only advisories (PF-4/PF-5/PF-6/PF-8) in the same pass. Do
not dispatch the Executor until PF-1 in particular is resolved: as
specified, there is a directly constructible input (any single unresolved
vertex under the new fixed-budget search) that spends up to the full 3600s
real-compute budget and returns no interpretable PART B result.

## Overall verdict

**DO-NOT-FREEZE.** Two blocking findings: PF-1 (PART B has no defined,
crash-free behavior under a PART-A outcome the draft itself calls possible
and informative — verified by direct trace of `depth0_fraction`'s missing
existence guard on `delta_map[v]`) and PF-2 (the draft names the wrong
script as "the ORIGINAL procedure" it tests against and sizes its budget
relative to — verified by direct trace of `RUN-SSIQ-a85692-b`'s own
`manifest.yaml`/`command.txt` against both `compute_delta_e.py` and
`compute_delta_e_v2.py`). Given this is the first amendment since v4 to
spend real, non-recoverable compute, PF-1 in particular should be treated
as dispatch-blocking rather than merely record-quality-blocking: as
written, the draft has a directly constructible path to spending its full
budget for zero interpretable result. Six further findings, including one
strong operational-risk advisory (PF-3, an empirically documented
infrastructure kill-window precedent from this exact experiment's own prior
run at a similar budget scale), should be applied in the same revision
pass.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v8
  task_id: TASK-20260806-b4b3b2
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v8.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970, pre_freeze_review.status: PENDING) --
    proposes re-searching delta_E for p=2437 (RUN-SSIQ-a85692-h) using a
    fresh, per-vertex-independent RNG and a fixed (non-shrinking)
    per-vertex time budget, comparing the resulting delta_map against
    RUN-SSIQ-a85692-b's archived one, and re-running the label-permutation
    null control on the new data, as the falsification test PF-6
    (specification_v7.yaml) named. This is the first amendment since
    specification_v4.yaml requiring genuinely new delta_E search compute
    (up to 1 CPU-hour), not zero-new-search-cost re-analysis.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: PART B feeds PART A's own possibly-partial new delta_map directly into delta_e_permutation_null_control_v7.depth0_fraction (imported unchanged, bypassing rebuild_and_verify's coverage gate -- confirmed by required_artifacts_note importing only depth0_fraction and summary_stats, never rebuild_and_verify/run_for_prime). Direct read of local_min_and_depth confirms no existence guard on delta_map[v] for v itself (only a guard on neighbours, whose own message asserts the gap is 'never legitimate' -- false in this design's own anticipated scenario). Any unresolved vertex under PART A's fixed-15s search crashes PART B's very first call (the REAL, unpermuted depth0_fraction), before any of the 1000 null trials run, discarding the amendment's entire headline result and the compute spent producing it."
    - "OBJ-2 [PF-2, BLOCKING]: The draft's 'ORIGINAL procedure' text (and its inherited PF-6 text from specification_v7.yaml) names compute_delta_e.py's run_phase_minus1_on_confirmatory_set and its literal per_vertex_cap = min(remaining, t_prime) formula (confirmed present verbatim at compute_delta_e.py:396). But RUN-SSIQ-a85692-b/manifest.yaml and command.txt, read directly, confirm the archived p=2437 data was actually produced by compute_delta_e_v2.py's real_execution_budget_v2 (compute_delta_e_v2.py:212-296), a materially different mechanism (single aggregate cross-prime wall-clock counter, remaining_now = remaining - elapsed_this_prime, no t_prime variable at all). Both scripts share the same neighbors_ell_isogenous/build_smooth_table/two_sided_search (v2 imports these unchanged from v1, confirmed) and the same rng_search = random.Random(seeds[0]*1000003+p) line, so PF-6's underlying concern is not invalidated -- but the draft never names compute_delta_e_v2.py anywhere, violating this lineage's own GD-9/GD-10 explicit-function-level-diff standard, and even RT-PREFREEZE-EXP-SSIQ-a85692-v7's own PF-6 discussion made the same mis-citation."
    - "OBJ-3 [PF-3, ADVISORY, strong]: RUN-SSIQ-a85692-b/manifest.yaml discloses that two of its three launch attempts were killed by an environment-imposed background-process lifetime limit '(empirically ~60-65 minutes)' before writing any result. This amendment's own wall_clock_seconds_per_run: 3600 (exactly 60 minutes) sits at the low edge of that same empirically-documented kill window on the same experiment lineage; the draft does not instruct the Executor to use the setsid/nohup/disown detachment workaround proactively."
    - "OBJ-4 [PF-4, ADVISORY]: Because the archived p=2437 search (compute_delta_e_v2.py, PF-2) was the first prime processed against a fresh 3600s aggregate pool and finished 194/194 in 284.88s (~7.9% of its available slice), the budget-shrinking half of PF-6's confound was very likely never actually binding for this specific archived data; the probe's discriminating power is concentrated in the RNG-sharing half, which the draft's framing does not disclose."
    - "OBJ-5 [PF-5, ADVISORY]: The new fixed 15s per-vertex cap is plausibly tighter, in the worst case, than what the archived run's shrinking-but-generous aggregate budget (up to ~3600s for a first-processed prime) provided for early vertices -- a coverage-driven WEAKENS outcome would not carry the same interpretation as a full-coverage WEAKENS, and the draft does not distinguish the two."
    - "OBJ-6 [PF-6, ADVISORY]: The +/-10 percentage-point margin-tolerance band has no stated statistical basis (no estimate of the archived margin's own variability under a different seed) and is ~43% of the 23.1pp anchor it bounds, the tightest of the four primes per RT-BATCH-010's own table. The three-way PERSISTS/WEAKENS/AMBIGUOUS partition also has an undefined edge: REAL_DEPTH0_FRACTION >= 0.95 with a margin wider than 23.1+10=33.1pp satisfies neither PERSISTS's band nor WEAKENS's 'materially lower,' falling to AMBIGUOUS by default though it intuitively supports (or strengthens) PERSISTS."
    - "OBJ-7 [PF-7, VERIFIED SAFE]: The per-vertex seed-derivation formula was traced directly against build_isogeny_graph.py's Fp2Field/build_graph_bfs: every graph vertex is already a plain (int, int) tuple, so tuple(int(c) for c in vertex) is a harmless identity coercion, not a failure risk. Distinct vertices produce distinct repr strings, and SHA-256 truncated to 64 bits is astronomically collision-safe for 194 vertices. BASE_SEED=20260811 is confirmed distinct from SEEDS=[20260805, 11, 977] and PERMUTATION_SEED=20260806. No defect found."
    - "OBJ-8 [PF-8, ADVISORY]: PART A never explicitly states that it re-runs the two-part graph-identity check (degree_sequence_check plus rebuilt-vertex-count match against archived_n_vertices) that delta_e_permutation_null_control_v7.rebuild_and_verify established as required before trusting a rebuilt graph -- it relies implicitly on build_graph_for_prime's seed determinism, inconsistent with this lineage's own explicit-verification discipline."
  required_controls:
    - "PF-1 [BLOCKING]: state PART B's exact behavior when PART A's new delta_map has <100% coverage -- either gate PART B on full coverage with a distinct COVERAGE-SHORTFALL outcome label, or explicitly restrict vertices/adjacency to the resolved subgraph via a precisely pinned procedure, stating how that changes comparability to v7's full-194-vertex REAL_DEPTH0_FRACTION=1.0 baseline."
    - "PF-2 [BLOCKING]: correct the 'ORIGINAL procedure' citation to name compute_delta_e_v2.py's real_execution_budget_v2 as the actual mechanism that produced RUN-SSIQ-a85692-b's archived p=2437 data, and re-derive the budget-margin rationale (the ~10x/~12.6x figures) against that mechanism rather than v1's per_vertex_cap=min(remaining,t_prime)."
    - "PF-3 [ADVISORY, strongly recommended before dispatch]: instruct the Executor to launch this run via the same detached execution pattern (setsid/nohup/disown) RUN-SSIQ-a85692-b needed after two failed attempts, given this run's 3600s budget sits at the edge of the same empirically-documented ~60-65-minute background-process kill window."
    - "PF-4/PF-5/PF-6/PF-8 [ADVISORY, text-only, zero cost]: disclose that the archived baseline's budget-scarcity component was very likely non-binding for p=2437; distinguish a coverage-driven WEAKENS from a full-coverage WEAKENS in the interpretation text; justify or narrow the +/-10pp band and close the AMBIGUOUS-by-default edge case for a stronger-than-archived margin; state explicitly that PART A re-runs the graph-identity check before searching."
  counterexample_or_mutation: >-
    PF-1's counterexample is directly constructible from the draft's own
    stated design, not an adversarial input: suppose PART A's
    independent-RNG search resolves 193 of 194 non-F_p-rational vertices at
    p=2437 within their fixed 15s budgets (one unlucky RNG draw exceeding
    15s is plausible given the draft's own justification for a 10x margin
    over the AVERAGE, not the worst case). PART B's driver calls
    depth0_fraction(new_delta_map, g["vertices"], g["adjacency"]); the loop
    for v in vertices reaches the unresolved vertex and evaluates
    delta_map[v] <= m, raising an uncaught KeyError (the vertex itself, not
    a neighbour, so local_min_and_depth's only guard does not fire). PART B
    terminates with no REAL_DEPTH0_FRACTION and none of 1000 null trials
    computed.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale statistical/search-procedure control work, asymptotic_claim
    null throughout, correctly inherited. The relevant baseline is this
    lineage's own established specification-precision discipline (v6/v7's
    PF-1/PF-2/PF-3/PF-7 unscoped-failure-branch standard), extended here by
    an actual runtime/code trace of what the imported function does when
    its precondition is violated, made necessary because this is the first
    amendment in the lineage to spend real, non-recoverable compute.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional complexity claim) -- attacked and held. asymptotic_claim: null throughout, unchanged."
  cost_model_challenges:
    - "The headline budget arithmetic is independently re-derived and confirmed correct: 284.88387155532837s / 194 vertices = 1.469s/vertex average (matches the draft's ~1.47s); 15s / 1.469s ~= 10.2x margin (matches ~10x); 194 vertices * 15s = 2910s worst-case search bound, < 3600s cap with ~690s margin for overhead (matches the draft's own 2910s figure and its implicit claim the cap cannot be exhausted by the vertex loop alone); 3600s / 284.88s ~= 12.6x total margin (matches the note). All figures independently confirmed against RUN-SSIQ-a85692-b/raw-result.json's phase_minus1_real_search['2437'] entry directly. What is not correct is the citation underlying it (PF-2: the numeric figure is accurately transcribed but the procedure that produced it is mis-attributed), and the arithmetic does not account for the documented ~60-65-minute infrastructure kill window this exact run history already hit twice (PF-3) -- an infrastructure risk to the compute being spent, not a mathematical cost-model error."
  reduction_and_scope_challenges:
    - "No scheme from any affected-vs-safe list appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "OBJECTIVE_BOUNDARY correctly scopes a PERSISTS result to THIS ONE PRIME ONLY, not extending to the other three primes or to H-SSIQ-36e970/lever L4 -- no scope inflation found."
  proof_architecture_challenges:
    - "Not applicable -- direct instrument-level statistical/search-procedure control, not a proof-oriented proposal (H-SSIQ-36e970.proof_search_map.not_applicable_reason, inherited unchanged, attacked and held)."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v8.yaml as a draft,
    not yet frozen: the intended experimental design (hold prime/graph
    fixed, vary only the delta_E search's RNG-sharing and budget-shape) is
    a sound and appropriately narrow test of PF-6's named confound, and the
    per-vertex seed-derivation formula is verified safe by direct code
    trace. Two blocking, code-verified defects prevent freezing as written:
    PART B's imported depth0_fraction call has no defined behavior, and in
    fact crashes on direct trace, when fed the partial-coverage new
    delta_map PART A explicitly anticipates as a possible outcome -- a
    defect that would discard the entire real-compute spend and the
    amendment's whole headline result; and the draft's own
    characterization of "the ORIGINAL procedure" it tests against and sizes
    its budget relative to names the wrong script (compute_delta_e.py
    rather than compute_delta_e_v2.py, which actually produced
    RUN-SSIQ-a85692-b's archived p=2437 data). Neither defect requires
    redesigning the underlying control; both are specification/wiring
    fixes at zero additional search cost. Five further findings are
    advisory but should be applied in the same revision pass given real
    compute is at stake, particularly the empirically documented
    infrastructure kill-window risk from this exact experiment's own prior
    run history.
  next_concrete_action: >-
    Coordinator: return this draft for one revision round applying PF-1
    (state PART B's exact behavior under partial PART A coverage, with a
    distinct outcome label if it gates rather than proceeds) and PF-2
    (correct the cited "ORIGINAL procedure" to compute_delta_e_v2.py's
    real_execution_budget_v2 and re-derive the budget-margin note against
    it), plus PF-3 (add the detachment-launch instruction) and the
    remaining text-only advisories (PF-4/PF-5/PF-6/PF-8) in the same pass.
    Do not dispatch the Executor until PF-1 is resolved: as specified,
    there is a directly constructible input (any single unresolved vertex
    under the new fixed-budget search) that spends up to the full 3600s
    real-compute budget and returns no interpretable PART B result.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no permutation trial executed --
    this review is a specification and implementation trace, not an
    execution. Directly read: specification_v8.yaml in full;
    specification_v6.yaml/v7.yaml's PF-6 text and history;
    RT-BATCH-010.md and RT-PREFREEZE-EXP-SSIQ-a85692-v7.md in full;
    compute_delta_e.py in full (two_sided_search, build_smooth_table,
    run_phase_minus1_on_confirmatory_set); compute_delta_e_v2.py's own
    run_phase_minus1_on_confirmatory_set and module-docstring diff list;
    build_isogeny_graph.py's Fp2Field/build_graph_bfs;
    delta_e_permutation_null_control_v7.py in full (local_min_and_depth,
    depth0_fraction, rebuild_and_verify, run_for_prime);
    trapping_diagnostic_v5.py's load_archived_prime_data/
    build_graph_for_prime; RUN-SSIQ-a85692-b/raw-result.json's
    phase_minus1_real_search entries for all five admitted primes, and
    RUN-SSIQ-a85692-b/manifest.yaml and command.txt in full. Independently
    recomputed the budget arithmetic (1.47s/vertex average, 10.2x margin,
    2910s worst case, 12.6x total margin) by hand against the archived
    JSON, not from the draft's own prose. No file written outside this
    report; no run artifact, specification file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-011/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v8.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v8.yaml and
    every prior run package) and every ledger record are untouched.
  verdict: DO-NOT-FREEZE
```
