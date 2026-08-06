# RT-PREFREEZE-EXP-SSIQ-a85692-v11 — Red Team pre-freeze review (round 1) of
# `specification_v11.yaml` (DRAFT, status: draft, NOT YET FROZEN)

**Reviews the Coordinator-committed snapshot at `6b6703ee`** (clean working
tree; `experiments/EXP-SSIQ-a85692/specification_v11.yaml` as committed by
"GOAL-SSIQ-001 BATCH-014: EXP-SSIQ-a85692 v11 amendment draft (not yet
frozen)"). No code was run and no search compute was spent producing this
review — every finding below is a direct read of the committed draft text
against the real, already-committed implementation files it cites:
`delta_e_truncation_sweep_v10.py`, `delta_e_truncation_probe_v9.py`,
`delta_e_independent_rng_probe_v8.py`, `trapping_diagnostic_v5.py`,
`compute_delta_e.py`, `compute_delta_e_v2.py` (all read in full), plus
`RUN-SSIQ-a85692-b/raw-result.json`, `EV-SSIQ-48d274.yaml`, and
`RT-BATCH-013.md`.

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
    with the Executor/Coordinator drafting this amendment.
```

---

## Verdict: **FREEZE-WITH-FIXES**

Execution mechanics (imports, failure isolation, budget arithmetic, graph
rebuild-once discipline) check out cleanly against the real code. The draft's
genuinely new contribution — the natural-completion cross-check — is
mechanistically sound in what it reads (`timed_out` means what the draft
says it means), but its **falsifiable prediction leans on an unstated,
unverified second premise about a different run**, and its own function-level
diff is **incomplete on one genuinely new piece of required output** in a way
that a good-faith Executor could resolve two structurally different ways —
on a code path this run is **certain** to exercise (`b=1.1s`), not a remote
edge case. None of this is fundamentally broken; all three items below are
fixable by adding explicit text, not by redesigning the amendment.

---

## What I checked and found correct (no objection)

1. **`timed_out` means exactly what the draft assumes, verified against the
   actual search primitive, not just the wrapper.** Read
   `compute_delta_e.py:144-174` (`build_smooth_table`) and `:177-210`
   (`two_sided_search`) directly. `build_smooth_table`'s `timed_out` is set
   `True` only if the wall-clock check trips **before** its own heap empties;
   if the heap empties first (every smooth-degree-≤23 codomain reachable via
   `L_PRIMES` from that starting point has been enumerated), `timed_out`
   stays `False` — a genuine, budget-independent, algorithm-internal
   completion signal, not "always True whenever a fixed-duration loop runs."
   `two_sided_search`'s own `timed_out` is `bool(to_s or to_t)`: **both**
   the source-table and target-table expansions must have exhausted their
   own heaps for the combined call to report `timed_out=False`. So
   `run_truncation_probe_v9`'s per-vertex `timed_out` field (read, unchanged,
   by the new cross-check — no new instrumentation, as claimed) does mean
   "this run's search reached its own confirmed-exhaustive stopping
   condition before the declared budget elapsed," exactly as the draft's
   prose states. This part of Adversarial Question 1 clears.
2. **`value_histogram_and_conjugate_pairs` is genuinely pure and genuinely
   reusable**, verified directly against `delta_e_truncation_sweep_v10.py:164-219`.
   Signature `(resolved_non_fp_set, new_delta_map, field)`; body references
   only its own parameters plus `field.frobenius(v)` — no read of any
   module-level constant (`SWEEP_BUDGETS`, `PRIME`, `GRAPH_SEED`,
   `BASE_SEED`). v11's claim that this is the first reuse of a v10-defined
   function in the lineage, and that it is safe to reuse unchanged, is
   correct.
3. **Every cited import exists with the exact name and call signature
   claimed.** Checked against the real files, not the draft's own prose:
   `delta_e_truncation_probe_v9.run_truncation_probe_v9(graph, base_seed,
   per_vertex_budget_seconds)`, `.parse_v8_new_delta_map(path)`,
   `.compare_against_archived(new_delta_map, archived_delta_map,
   non_fp_rational_set)`, `.compare_against_v8(...)` (same signature);
   `trapping_diagnostic_v5.build_graph_for_prime(p, seed)`,
   `.load_archived_prime_data(raw_result_path, prime)`;
   `delta_e_independent_rng_probe_v8.verify_graph_identity(g,
   archived_n_vertices)`; `delta_e_truncation_sweep_v10.
   value_histogram_and_conjugate_pairs(...)`, `.vertex_json_safe(v)`,
   `.delta_map_json_safe(delta_map)`. No PF-4-style nonexistent citation
   found.
4. **Budget arithmetic is correct.** `194*(1.1+1.2) = 446.2`; `194*1.2 =
   232.8`; v10's own comparable bound `194*(0.6+0.8+1.0) = 465.6`;
   `1000/446.2 ≈ 2.241` (stated "~2.24x", correct). `1.1 < 1.14993` (the
   observed floor minimum) and `1.14993 < 1.2 < 1.70` (the observed range
   maximum) — both correctly support "b=1.1 guarantees full truncation,
   b=1.2 genuinely straddles."
5. **Failure isolation is complete, including the new code.** Step (0)
   (graph build + `verify_graph_identity`) is specified to run exactly once,
   unwrapped, before the sweep loop — matches v9/v10's PF-1/PF-10 precedent.
   Each sweep point's steps (1) through (8) — explicitly including step (8),
   the new natural-completion cross-check — are specified as all inside that
   sweep point's own `try` block, matching PF-2's discipline extended
   correctly to the new code. No narrower-than-the-bundle scoping found
   (clears the PF-2-style check).
6. **No graph-rebuild-count or scope self-contradiction found** (the PF-1
   class of defect): "GRAPH REBUILD/RE-VERIFY HAPPENS EXACTLY ONCE" is
   stated once and never contradicted elsewhere in the draft.
7. `total_cpu_hours: 0.33` against `wall_clock_seconds_per_run: 1000`
   initially looked like a stale copy from v10 (`1200s`/`0.4` CPU-hr) —
   checked and it is **not** clearly wrong: v9 (`600s`/`0.2`hr) and v10
   (`1200s`/`0.4`hr) both fit a `wall_clock*1.2/3600` buffer convention,
   which `1000*1.2/3600 = 0.333…` also fits. v8 (`3600s`/`1.0`hr) doesn't
   fit that same pattern, and no document states the intended relationship
   explicitly, so this is unresolved but **not a contradiction that can
   cause an execution-time problem either way** (0.33 CPU-hr is a looser,
   not tighter, cap than the binding 1000s wall-clock limit). Not required
   as a blocking fix; worth a one-line clarifying convention statement in a
   future amendment, not this one.

---

## Required fixes

### FIX-1 (Adversarial Questions 1–2, most important): the falsifiable
prediction depends on an unstated, unverified second premise about a
**different run**, not just on what `timed_out` means in this one

The draft's own justification is: `timed_out=False` ⟹ "per EV-SSIQ-48d274's
own derivation the returned value IS the confirmed true minimum" ⟹ therefore
it must equal `RUN-SSIQ-a85692-b`'s archived value exactly. The first
implication is correct (see "checked and found correct" #1 above) — but it
only establishes that **this run's** search, for that vertex, found the true
minimum within the algorithm's own smooth-degree domain (`L_PRIMES`, `X=23`).
It says nothing about whether `RUN-SSIQ-a85692-b`'s archived value for the
**same** vertex is *also* that domain-minimum, rather than itself a
non-exhaustive upper bound. `EV-SSIQ-48d274`'s actual derivation (RT-BATCH-013,
Front 2/OBJ-3) is a **same-seed, growing-budget** monotonicity argument
("table(b1) is a prefix of table(b2)") — it does not, by itself, license
treating a value produced under a **completely different RNG scheme** as
ground truth.

I checked whether this second premise is even verifiable, and it is not,
directly — I read `compute_delta_e_v2.py:212-296`
(`run_phase_minus1_on_confirmatory_set`, the actual code that produced
`RUN-SSIQ-a85692-b`, confirmed via `WALL_CLOCK_BUDGET_SECONDS`/`T_RESERVED`
naming and cross-checked against the archived run's own field names —
`aggregate_seconds_available_at_prime_start`,
`stopped_before_start_aggregate_exhausted` — which only exist in the *v2*
function, not the *v1* `compute_delta_e.py` version I initially misread
this against) in full: **it never records a per-vertex `timed_out` flag
anywhere**, only the resolved `delta_map` values themselves. So there is no
way to directly confirm, from the archived artifact, that every one of
`RUN-SSIQ-a85692-b`'s 194 non-F_p-rational values at p=2437 came from a
non-truncated search.

I then checked the **circumstantial** case, from the real archived data
(`RUN-SSIQ-a85692-b/raw-result.json`, `phase_minus1_real_search["2437"]`):
`aggregate_seconds_available_at_prime_start = 3600.0`,
`wall_seconds_used = 284.88387155532837`, `n_resolved = 194 = n_non_fp_rational`
(`m_coverage_non_fp_fraction = 1.0`). Average ≈1.47s/vertex, consistent with
the lineage's own observed 1.15–1.70s natural-completion range. Because
`run_phase_minus1_on_confirmatory_set`'s per-vertex `time_budget_seconds`
argument (`remaining_now`) starts near 3600s and shrinks only by *actually
elapsed* time, and total elapsed time across all 194 vertices was 284.88s
(≪3600s throughout), it is highly implausible that any individual vertex's
own search hit its budget cap before its heap emptied. So the premise
appears **true** for this specific prime and run — but **this argument
appears nowhere in this lineage's documents** (not in v9/v10/v11's specs,
not in `EV-SSIQ-48d274`, not in `RT-BATCH-013`), despite being load-bearing
for every "archived == true value" framing this campaign has already used
(e.g. `RT-BATCH-013` O-4's "the TRUE archived population's own 34
delta_E=2 vertices").

**Required fix:** name this as an explicit, numbered premise in v11's spec
text (matching this lineage's own convention for physical/wall-clock
premises — PF-3/PF-6, and O-3's "one named, testable premise"), citing the
supporting arithmetic above; and broaden the interpretive guidance for a
nonzero `n_naturally_completed_NOT_matching_archived` to name a **third**
possible cause alongside the two the draft currently offers ("overturning
EV-SSIQ-48d274's own derivation" or "`timed_out` doesn't mean what this
amendment assumes") — namely, that `RUN-SSIQ-a85692-b`'s own archived value
for that specific vertex was itself a non-exhaustive upper bound, which
would neither overturn EV-SSIQ-48d274 nor reveal a misunderstanding of
`timed_out`. As currently written, a reviewer encountering that (unlikely
but not impossible) outcome would be pointed at only two explanations,
missing the more mundane one.

### FIX-2 (Adversarial Questions 3/8, real ambiguity, will be exercised):
`required_artifacts_note` under-declares how many times
`value_histogram_and_conjugate_pairs` is called

`amendment_scope` item (7) requires the **existing** histogram/conjugate-pair
report over the full `resolved_non_fp_set`, via
`value_histogram_and_conjugate_pairs` — this is what `required_artifacts_note`
describes as "called once per sweep point." But `amendment_scope` item (8)
(the new cross-check) **separately** requires "the delta_E VALUE HISTOGRAM
restricted to the naturally-completed subset alone" — a second, distinct
value→count dict over a *different* vertex set. The draft never states
whether the Executor should (a) call the same genuinely-imported
`value_histogram_and_conjugate_pairs` a **second** time, on the
naturally-completed-only subset (in which case `required_artifacts_note`'s
own "(called once per sweep point)" is literally wrong — it should say "up
to twice"), or (b) hand-write new code duplicating a slice of that
function's own histogram-building loop — which is nowhere declared as an
authorized duplicate the way `vertex_json_safe`/`delta_map_json_safe` are.
This is exactly the completeness gap PF-9 was written to catch in v10's own
draft, applied one lineage-generation further in: `required_artifacts_note`
claims a complete function-level diff but is silent on which of two
structurally incompatible resolutions applies to a piece of output the spec
itself requires.

This is not a remote edge case: at `b=1.1s`, `n_naturally_completed` is
**guaranteed to be 0** by design (1.1 < 1.14993, the observed floor), so
this exact code path — "compute the naturally-completed-restricted
histogram at `n_naturally_completed==0`" — will be exercised with certainty
on every execution of this spec, not merely hypothetically.

**Required fix:** state explicitly that `value_histogram_and_conjugate_pairs`
is reused a second time per sweep point (once on the full
`resolved_non_fp_set` per item 7, once on the naturally-completed subset per
item 8), and correct `required_artifacts_note`'s parenthetical accordingly —
or, if new code is actually intended, declare it explicitly as an
authorized, disclosed duplicate the way the JSON-safety helpers are.

### FIX-3 (Adversarial Question 7, minor but should be pinned before
freeze): the internal-consistency check's failure mode is unspecified

"`assert n_naturally_completed + n_still_truncated == n_resolved` ... this
amendment REQUIRES the Executor to check and report the outcome of, not
silently assume holds" is ambiguous between (a) a literal Python `assert`
statement — which, were it ever to fail, would raise, be caught by the
enclosing per-sweep-point `try`/`except` (per item 6's own failure-isolation
discipline), and **discard that sweep point's otherwise-valid Comparison
1/Comparison 2/histogram results along with it** — and (b) an explicit
boolean field computed and reported alongside the other counts without
raising, which is the pattern `value_histogram_and_conjugate_pairs` itself
already established for its own internal-consistency check (the "n_paired
is odd" anomaly is reported as a string, never raised). Since the partition
is definitionally exhaustive (every vertex is `timed_out` `True` or `False`,
mutually exclusive) and nothing in the described logic could actually
violate it short of a code bug, the practical stakes are low — but per this
lineage's own convention (report anomalies, don't let an internal-consistency
check destroy an otherwise-successful sweep point's real results), the spec
should say so explicitly rather than leave "assert" open to its literal,
crash-and-lose-the-sweep-point reading.

---

## Adversarial-question-by-question summary (per the task's 8 items)

1. **What `timed_out` actually tracks** — verified against
   `compute_delta_e.py`'s `build_smooth_table`/`two_sided_search`, not just
   the `run_truncation_probe_v9` wrapper: a genuine, budget-independent,
   algorithm-internal exhaustive-completion flag. The draft's characterization
   is accurate. **No objection to this part.**
2. **Is the falsifiable prediction well-founded** — no, not as stated: it
   needs a second, unstated premise about `RUN-SSIQ-a85692-b`'s own
   completeness, which is unverifiable from that run's own artifact (no
   per-vertex `timed_out` was ever recorded there) and, while I found strong
   circumstantial support for it in the real archived data, that support
   appears nowhere in this lineage's own text. **FIX-1.**
3. **Budget/two-point-list arithmetic** — checked, correct throughout
   (`446.2s`, `232.8s`, `~2.24x`, floor/range placement of `1.1`/`1.2`). **No
   objection.**
4. **Self-contradictions (PF-1 class)** — none found; graph-rebuild-once and
   isolation-scope language is consistent throughout.
5. **Nonexistent-import citations (PF-4 class)** — none found; every cited
   function exists with the exact name/signature claimed.
6. **Failure-isolation completeness (PF-2 class)** — clean; the new
   cross-check (step 8) is explicitly inside the same per-sweep-point `try`
   block as steps (1)-(7).
7. **Genuinely new, two-way-resolvable edge case** — found, and it is
   certain to be exercised (`b=1.1s` guarantees `n_naturally_completed==0`):
   the histogram-reuse ambiguity (**FIX-2**) and the assert-vs-report
   ambiguity (**FIX-3**), not the zero-count arithmetic itself (which is
   safe either way, since `value_histogram_and_conjugate_pairs` already
   handles an empty input set without crashing).
8. **`required_artifacts_note` function-level-diff completeness (PF-9
   class)** — one real gap found (**FIX-2**); otherwise complete and
   accurate against the real code.

---

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
single-prime search-instrument diagnostic, `H-SSIQ-36e970.asymptotic_claim`
untouched. The relevant comparison is this lineage's own pre-freeze
discipline (PF-1 through PF-10 in v10's two rounds); this round finds three
fixable gaps of the same general classes those rounds found (an unstated
physical premise, an incomplete function-diff, an underspecified failure
mode), none of them blocking.

## Narrowest supported statement

The draft's mechanics — imports, failure isolation, graph-rebuild-once
discipline, and search-cost budget arithmetic — are sound and verified
against the real committed code, not merely trusted from the draft's own
prose. The draft's one genuinely new idea (the natural-completion
cross-check) reads a real, correctly-understood `timed_out` signal with no
new instrumentation, and its own "EMPTY {} at zero" discipline is real and
already established in the reused function — but its **exact-equality**
prediction currently overstates what has been established, by implicitly
treating `RUN-SSIQ-a85692-b`'s archived value as ground truth without stating
or citing why. This is fixable with additional disclosure text, not a
redesign, and does not block a freeze once fixed.

## Next concrete action

Coordinator: apply FIX-1 through FIX-3 as text amendments to
`specification_v11.yaml` (no code exists yet, so this is pure spec-text
editing), then route back through a second pre-freeze round only if any fix
changes the amendment's actual execution behavior (FIX-2/FIX-3 might, if
resolved toward "write new code" or "use a raising assert"; FIX-1 is
documentation-only and would not require a second round by itself). Until
then, `pre_freeze_review.status` stays `PENDING` and `frozen_at` stays
`null`.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v11
  task_id: TASK-20260806-c8a398
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v11.yaml (draft, status: draft,
    committed at 6b6703ee, not yet frozen): a two-point floor-straddling
    truncation sweep (b in [1.1, 1.2] seconds/vertex at p=2437) amending
    specification_v10.yaml (frozen ca905c2482e00fef5b0bdc6902b43a77a43c8d5c),
    whose core new contribution is a REQUIRED NATURAL-COMPLETION CROSS-CHECK
    partitioning each sweep point's resolved vertices by their own timed_out
    flag and predicting that every naturally-completed (timed_out=False)
    vertex's value exactly equals RUN-SSIQ-a85692-b's archived value.
  objections:
    - "FIX-1: the falsifiable prediction (naturally-completed value == archived value, exactly) rests on an unstated, unverified second premise -- that RUN-SSIQ-a85692-b's own archived value for the same vertex is itself a non-truncated, domain-exhaustive result, not merely that this run's own search reached its own confirmed stopping condition. RUN-SSIQ-a85692-b was executed via compute_delta_e_v2.py's run_phase_minus1_on_confirmatory_set (read in full), which never records a per-vertex timed_out flag, so this premise is unverifiable directly from the archived artifact. I derived strong circumstantial support for it from RUN-SSIQ-a85692-b/raw-result.json (aggregate_seconds_available_at_prime_start=3600.0 vs wall_seconds_used=284.88s across 194 vertices, average ~1.47s/vertex, consistent with the observed 1.15-1.70s natural-completion range, meaning no individual vertex's own per-vertex time budget plausibly ran out) -- but this argument appears nowhere in v9/v10/v11's specs, EV-SSIQ-48d274, or RT-BATCH-013, despite being load-bearing for every prior 'archived == true value' framing this campaign has used."
    - "FIX-2: required_artifacts_note states delta_e_truncation_sweep_v10.value_histogram_and_conjugate_pairs is 'called once per sweep point,' but amendment_scope's item (8) separately requires a delta_E value histogram restricted to the naturally-completed subset alone -- a second, distinct histogram from item (7)'s full-resolved-set histogram. The draft never states whether this reuses the same imported function a second time (making the 'called once' note wrong) or requires new, undeclared duplicate code -- a genuine, two-way-incompatible ambiguity, and this code path is certain to execute (b=1.1s guarantees n_naturally_completed==0 by design), not a remote edge case."
    - "FIX-3: the internal-consistency check 'assert n_naturally_completed + n_still_truncated == n_resolved ... report the outcome, not silently assume holds' is ambiguous between a literal Python assert (which, on failure, would be caught by the enclosing per-sweep-point try/except and discard that sweep point's otherwise-valid Comparison 1/2/histogram results) and a non-crashing explicit boolean report -- the pattern value_histogram_and_conjugate_pairs itself already established for its own internal-consistency anomaly. Low practical stakes (the partition is definitionally exhaustive) but should be pinned to match lineage convention."
  required_controls:
    - "Add an explicit, numbered premise to specification_v11.yaml stating that RUN-SSIQ-a85692-b's archived delta_map values for p=2437 are themselves domain-exhaustive (non-truncated), citing the aggregate-budget-vs-wall-seconds-used arithmetic from RUN-SSIQ-a85692-b/raw-result.json, and broaden the interpretive guidance for a nonzero n_naturally_completed_NOT_matching_archived to name this as a third possible explanation alongside the two the draft currently offers."
    - "Clarify in required_artifacts_note and amendment_scope whether value_histogram_and_conjugate_pairs is called a second time (on the naturally-completed subset) or whether new duplicate code is authorized for that specific histogram, and correct the '(called once per sweep point)' note accordingly."
    - "Specify that the n_naturally_completed + n_still_truncated == n_resolved internal-consistency check is reported as an explicit non-raising boolean field, not a raising assert, matching value_histogram_and_conjugate_pairs's own anomaly-reporting precedent."
  counterexample_or_mutation: >-
    The cheapest concrete check that exposes FIX-1: recompute, from
    RUN-SSIQ-a85692-b/raw-result.json's own phase_minus1_real_search["2437"]
    fields (aggregate_seconds_available_at_prime_start=3600.0,
    wall_seconds_used=284.88s, n_resolved=194/194), whether the per-vertex
    time_budget_seconds available to that run's own two_sided_search calls
    ever plausibly approached exhaustion for any vertex -- done above, and it
    did not, which is why FIX-1 is a documentation gap rather than a false
    prediction, but the gap is real and should be closed with an explicit,
    numbered premise before freeze rather than left implicit.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense --
    toy-scale, single-prime search-instrument diagnostic pre-freeze review;
    H-SSIQ-36e970.asymptotic_claim untouched throughout. The relevant
    baseline is this lineage's own pre-freeze discipline (PF-1 through PF-10,
    two rounds on v10's own draft); this round finds three fixable gaps of
    comparable classes (unstated physical premise, incomplete function-diff,
    underspecified failure mode), none blocking.
  heuristic_challenges:
    - "The draft's own physical/wall-clock-style premise this review adds (FIX-1) is not one of H-SSIQ-36e970's numbered heuristic_assumptions -- correctly, since this remains a search-instrument diagnostic, not a heuristic-conditional asymptotic claim -- but it is exactly the class of premise this lineage's own convention (PF-3/PF-6, O-3's 'one named, testable premise') requires to be named explicitly, and it currently is not."
  cost_model_challenges:
    - "Budget arithmetic verified correct: 194*(1.1+1.2)=446.2s worst case, 194*1.2=232.8s at the largest single sweep point, 1000s/446.2s ~= 2.24x margin, all matching the draft's own stated figures. total_cpu_hours=0.33 against wall_clock_seconds_per_run=1000 does not obviously follow a stated conversion rule, but is not inconsistent with the binding 1000s wall-clock cap either way (a looser, not tighter, bound) -- noted, not required as a blocking fix."
  reduction_and_scope_challenges:
    - "No affected/safe cryptographic scheme list anywhere in this draft; OBJECTIVE_BOUNDARY correctly scopes this to a single-prime (p=2437) descriptive diagnostic control, explicitly excluding H-SSIQ-36e970's real-arm prediction, lever L4, and any PERSISTS/WEAKENS vocabulary -- no scope inflation found."
  proof_architecture_challenges:
    - "Not applicable -- a search-instrument diagnostic amendment, not a proof-oriented proposal; inherited not_applicable_reason unchanged and correctly reasoned."
  narrowest_supported_statement: >-
    specification_v11.yaml's mechanics (imports, per-sweep-point failure
    isolation including the new cross-check, graph-rebuild-once discipline,
    and search-cost budget arithmetic) are sound and verified directly
    against the real committed implementation files, not merely trusted from
    the draft's own prose. The natural-completion cross-check correctly reads
    an already-well-understood timed_out signal with no new instrumentation.
    Its exact-equality falsifiable prediction, however, currently overstates
    what has been established, by implicitly treating a different run's
    (RUN-SSIQ-a85692-b's) archived value as confirmed ground truth without
    stating or citing why -- fixable with additional disclosure text, not a
    redesign. Two further gaps (histogram-reuse ambiguity, assert-vs-report
    ambiguity) affect a code path (b=1.1s, n_naturally_completed==0) this
    amendment is certain to exercise on every execution, not a remote edge
    case.
  next_concrete_action: >-
    Coordinator: apply FIX-1 through FIX-3 as text amendments to
    specification_v11.yaml (no implementation code exists yet). Route back
    through a second pre-freeze round only if resolving FIX-2 or FIX-3
    changes actual execution behavior (e.g. toward new duplicate code or a
    raising assert); FIX-1 is documentation-only. pre_freeze_review.status
    stays PENDING and frozen_at stays null until these are applied and this
    round's findings are addressed.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No code executed, no search compute spent, no artifact modified. Several
    non-durable, read-only computations were performed directly against
    already-committed JSON (RUN-SSIQ-a85692-b/raw-result.json's
    phase_minus1_real_search["2437"] fields) to check FIX-1's circumstantial
    support; no file was written by any of these. Read in full:
    specification_v11.yaml (draft); specification_v10.yaml,
    specification_v9.yaml, specification_v8.yaml (budget blocks only, for the
    total_cpu_hours check); delta_e_truncation_sweep_v10.py;
    delta_e_truncation_probe_v9.py; delta_e_independent_rng_probe_v8.py;
    trapping_diagnostic_v5.py; compute_delta_e.py; compute_delta_e_v2.py
    (lines 200-300, run_phase_minus1_on_confirmatory_set); EV-SSIQ-48d274.yaml;
    RT-BATCH-013.md; AGENTS.md; agents/red-team.md;
    docs/inventor-protocol.md.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task wrote only
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-014/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v11.md
    -- specification_v11.yaml and every other artifact are untouched.
  verdict: FREEZE-WITH-FIXES
```
