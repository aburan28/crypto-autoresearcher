# RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2 — Second pre-freeze Red Team review
# of the REVISED DRAFT amendment `specification_v7.yaml` (H-SSIQ-36e970),
# GOAL-SSIQ-001 BATCH-010

**Reviews `experiments/EXP-SSIQ-a85692/specification_v7.yaml` at
`status: draft`, `pre_freeze_review.status: REVIEWED`,
`pre_freeze_review.findings_applied: [PF-1, PF-2, PF-3, PF-4, PF-5, PF-6,
PF-7]`, as committed at snapshot `cebbc300` ("GOAL-SSIQ-001 BATCH-010:
EXP-SSIQ-a85692 v7 draft revised after DO-NOT-FREEZE (round 1)"), parented on
`6d9f7e55` (the round-1-reviewed draft). `git status --short` on the file
confirmed a clean working tree against this commit.** Per this task's own
operating rules, only this Coordinator-committed snapshot is treated as
durable input; this report is advisory input to the Coordinator's own freeze
decision and changes nothing under `experiments/EXP-SSIQ-a85692/` (including
`specification_v6.yaml`, still frozen unedited at `66753c92`) or any ledger
record.

Read in full per the launching task: `AGENTS.md`, `CLAUDE.md`,
`agents/red-team.md`; `RT-PREFREEZE-EXP-SSIQ-a85692-v7.md` (round 1,
DO-NOT-FREEZE, PF-1/PF-2 blocking, PF-3 through PF-7 advisory) in full;
`RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2.md` and
`RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3.md` (the sibling lineage's own
round-2/round-3 caliber precedent, including PF-7/PF-8/PF-12/PF-13's "a fix
that looks right in prose is not exempt from being traced" and "same
mechanism, asserted not pinned down" standards) in full; the current
`specification_v7.yaml` in full (all seven `pfN_summary` entries, the entire
`inputs.delta_e_permutation_null_control_v7` block, `required_artifacts_note`);
`specification_v6.yaml` in full, specifically re-read for exactly what its
PF-3/PF-7/PF-13 findings did and did not cover (the crosscheck_pass boolean
and the basin-accounting assertion; **not**, on direct re-check, the coverage
assertion or graph-rebuild verification, which v6's own `gd12_fix_v6` REUSE
MECHANISM paragraph describes only as an "authorized, disclosed duplication,"
with no explicit per-prime/global scope statement attached anywhere in that
paragraph or elsewhere in v6); `trapping_diagnostic_v5.py` in full (500
lines, direct read, not trusted from either draft's prose) — specifically
`run_diagnostic_for_prime`'s own `coverage_assertion_pass` /
`graph_rebuild_independently_verified_correct` computation (lines 181–208)
compared formula-by-formula against v7's own stated (a)/(b) formulas, and
`run_all`'s loop (lines 444–449) checked directly for the presence or
absence of a `try`/`except` around each prime's call to
`run_diagnostic_for_prime` (confirmed: **none exists** — a raised
`TrappingDiagnosticError` for any one prime propagates out of `run_all`
uncaught).

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
    lineage, including the round-1 review of this same draft and every round
    of the sibling v6 lineage. It does not upgrade the campaign's evidence
    tier by itself.
```

---

## Bottom line up front

**Round 1's two blocking findings are both genuinely, correctly resolved on
their own terms.** PF-1's coverage assertion is now, independently re-traced
formula-by-formula against `trapping_diagnostic_v5.py`'s own
`coverage_assertion_pass`/`graph_rebuild_independently_verified_correct`
computation (not merely re-read from the draft's own prose), an **exact**
match: `vertex_set = set(g["vertices"])`, `n_matched = len([v for v in
delta_map if v in vertex_set])`, `degree_sequence_check(g).pass AND
len(g["vertices"]) == archived_n_vertices` reproduce the real code's
`n_matched == archived_n_vertices` and `degseq_pass and vertex_count_match`
checks exactly, including the archived-vertex-count figures
(2437: 203, 3889: 324, 5737: 478, 7333: 611), independently confirmed against
`ARCHIVED_N_VERTICES` in the source file. PF-2's anomaly branch is now
unambiguous: "this DOES NOT HALT OR SKIP that prime's NULL_DEPTH0_FRACTIONS
computation... REGARDLESS of whether REAL_DEPTH0_FRACTION matches its
expected value" states the required behavior directly, with no residual
two-reading risk of the shape v6's own round-2 PF-7 found in a
superficially similar-looking fix. **No blocking defect survives this
round.**

But three new, genuine, code-traceable advisory gaps surface from reading
this round's own new text with the same skepticism that found v6's own
PF-7/PF-8/PF-12/PF-13 as byproducts of prior rounds' fix text — none leaves
the REQUIRED OUTPUT ambiguous, so none is blocking, but all three are the
same species of defect ("a confidently-stated claim in fix text that does
not survive a direct trace") this lineage has repeatedly treated as worth
fixing before freeze:

1. **PF-8 [ADVISORY, NEW]: the coverage assertion's "never global... per
   specification_v6.yaml's own PF-3/PF-7/PF-13 unified per-prime
   failure-handling model, inherited unchanged" attribution is false on
   direct re-check of v6's own text, and describes the reused code's actual
   behavior backwards.** v6's PF-3/PF-7/PF-13 unification applies only to
   the `crosscheck_pass` boolean and the basin-accounting-partition
   assertion — v6 never states a per-prime/global scope for the coverage
   assertion or graph-rebuild verification anywhere. Worse: the actual
   reused code (`trapping_diagnostic_v5.py`'s `run_all`, confirmed by direct
   read) has **no** `try`/`except` around each prime's
   `run_diagnostic_for_prime` call, so a coverage-assertion failure for one
   prime, in that file's own real behavior, propagates and aborts
   **every** prime's processing — the opposite of "never global." This does
   not leave the required OUTPUT ambiguous, since v7's own operative
   sentence two clauses later ("Halt with an explicit error, reported for
   that prime only, if EITHER (a) or (b) fails") states the actual required
   behavior for THIS amendment's own new script directly and unambiguously
   — the defect is confined to the justifying citation, exactly PF-12's
   shape in the sibling v6 lineage (an unverified "inherited"/"same
   mechanism" claim, non-blocking because the behavior itself stands without
   it).
2. **PF-9 [ADVISORY, NEW]: `required_artifacts_note`'s own GD-9/GD-10
   explicit function-level code diff omits the coverage
   assertion/graph-rebuild verification from its list of AUTHORIZED,
   DISCLOSED DUPLICATES**, even though part (a) (the `vertex_set`/`n_matched`
   key-membership logic) is, exactly like `is_structural_local_min`, **not**
   a standalone importable symbol in `trapping_diagnostic_v5.py` (confirmed
   inline at lines 186–190, inside `run_diagnostic_for_prime`) and must
   therefore also be re-implemented, not imported, in the new script.
   `required_artifacts_note` explicitly names `is_structural_local_min` and
   `depth(v)` as disclosed duplicates but is silent on the coverage
   assertion's own duplication status — a real, if narrow, gap in the exact
   discipline GD-9/GD-10 exists to enforce, and the shape of gap v6's own
   PF-2 was raised for (a reuse instruction naming or implying import where
   none is possible).
3. **PF-10 [ADVISORY, NEW]: PF-3's population-vs-sample standard-deviation
   choice is now correctly and precisely FORMULATED, but its stated
   JUSTIFICATION does not hold up.** "The 1000 trials constitute the full
   population of interest for this pre-registered run, not a sample
   estimating a larger population" is in tension with the rest of this same
   amendment's own design: `N_TRIALS` is explicitly "chosen for statistical
   stability" (the language of Monte Carlo *estimation*, not of enumerating
   a closed population), and `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` is
   explicitly a one-sided permutation-test statistic, whose entire
   interpretive purpose is to treat the 1000 realized values as a *sample*
   from the (203!-to-611!-sized, for-all-practical-purposes-unenumerable)
   space of vertex-value permutations, in order to estimate how surprising
   the real value is relative to that much larger reference distribution.
   Under that framing — the amendment's own — sample SD (÷(N−1)), not
   population SD (÷N), is the standard convention for estimating the
   dispersion of an underlying distribution from a Monte Carlo sample drawn
   from it. The **arithmetic** difference is negligible (~0.05% relative at
   N=1000, as round 1's report already noted) and either convention is
   defensible in different framings, so this is not blocking — but the
   *specific rationale* given ("the full population of interest," not a
   sample) does not survive being checked against what the rest of this same
   paragraph does with the resulting number.

None of PF-8/PF-9/PF-10 requires redesigning the control, and all are
fixable at zero new search cost with a sentence or two each — the same
"advisory, non-blocking, text-only" category PF-3 through PF-7 already
occupy in this draft's own lineage, and PF-10/PF-11/PF-12/PF-13 occupy in the
sibling v6 lineage.

---

## (1) PF-1's fix: is the coverage assertion actually a faithful restoration, verified by direct code trace?

**Yes — confirmed, formula-by-formula, by directly reading
`trapping_diagnostic_v5.py`'s own `run_diagnostic_for_prime` (lines 161–208),
not by trusting v7's own prose or round 1's report that the fix would work.**

The real code:

```python
# ---- 4. GRAPH-REBUILD VERIFICATION (PF-5/PF-11) ---------------------
degseq = big.degree_sequence_check(g)
vertex_count_match = bool(n_built == archived_n_vertices)
degseq_pass = bool(degseq["pass"])

# ---- 2/3. key-format bridge + REQUIRED COVERAGE ASSERTION (PF-4/PF-9)
vertex_set = set(vertices)
matched_vertices = [v for v in delta_map if v in vertex_set]
n_matched = len(matched_vertices)
coverage_assertion_pass = bool(n_matched == archived_n_vertices)

if not coverage_assertion_pass:
    raise TrappingDiagnosticError(...)

if not (degseq_pass and vertex_count_match):
    raise TrappingDiagnosticError(...)
```

(where `vertices = g["vertices"]`, so `vertex_set = set(g["vertices"])`, and
`n_built = len(vertices) = len(g["vertices"])`).

v7's stated formula: "(a) coverage assertion: `vertex_set =
set(g["vertices"])`; `n_matched = len([v for v in delta_map if v in
vertex_set])`; confirm `n_matched == archived_n_vertices`... (b)
graph-rebuild verification: `degree_sequence_check(g).pass AND
len(g["vertices"]) == archived_n_vertices`... Halt with an explicit error,
reported for that prime only, if EITHER (a) or (b) fails."

Line-by-line: `vertex_set = set(g["vertices"])` **matches**
`vertex_set = set(vertices)` exactly (identical value, `vertices` is bound to
`g["vertices"]`). `n_matched = len([v for v in delta_map if v in
vertex_set])` **matches** `n_matched = len(matched_vertices)` where
`matched_vertices = [v for v in delta_map if v in vertex_set]` — identical
list comprehension, merely inlined. `degree_sequence_check(g).pass AND
len(g["vertices"]) == archived_n_vertices` **matches** `degseq_pass and
vertex_count_match` exactly (`degseq_pass = bool(degseq["pass"])`,
`vertex_count_match = bool(n_built == archived_n_vertices)`,
`n_built = len(vertices)`). "Halt... if EITHER (a) or (b) fails" **matches**
the real code's two independent `raise` statements (one per check, evaluated
in sequence, each independently sufficient to halt). The archived-vertex-count
figures v7 cites (2437: 203, 3889: 324, 5737: 478, 7333: 611) are an exact
match to `ARCHIVED_N_VERTICES = {2437: 203, 3889: 324, 5737: 478, 7333: 611}`
(line 89), independently re-confirmed by direct read, not copied from either
draft's own citation of it.

**PF-1's own counterexample from round 1 (a delta_map with a swapped, same-
count, off-graph key) is now correctly caught**: the restored key-membership
match (`n_matched = len([v for v in delta_map if v in vertex_set])`) would
correctly register `n_matched < archived_n_vertices` for that scenario,
exactly as v6's own check does, unlike the bare `len(delta_map)` count round
1 found and blocked on. **PF-1 CONFIRMED HOLDING**, verified by direct trace,
not by trusting the draft's own "RESTORED, IDENTICAL TO v6's OWN TWO-PART
CHECK" framing.

### PF-8 [ADVISORY, NEW]: the "never global... inherited unchanged" citation does not survive being checked against either v6's own text or the reused code's own actual behavior

v7's coverage-assertion clause is introduced as: "REQUIRED COVERAGE
ASSERTION AND GRAPH-REBUILD VERIFICATION, per-prime (never global -- per
specification_v6.yaml's own PF-3/PF-7/PF-13 unified per-prime
failure-handling model, inherited unchanged)."

Two things are wrong here, both directly checkable:

1. **v6's PF-3/PF-7/PF-13 never addressed the coverage assertion's own
   scope.** Re-reading v6's `gd12_fix_v6.pf3_summary` and its own operative
   FAILURE-HANDLING MODEL text: PF-3 fixed the `crosscheck_pass` boolean's
   scope (the `trapped=True`-vs-`is_structural_local_min(terminal)`
   comparison). PF-7 (round 2) and PF-13 (round 3) fixed the *basin-
   accounting-assertion*'s scope (`sum(basin) + n_trapped_false ==
   n_vertices`). v6's own REUSE MECHANISM paragraph — the one place v6
   discusses the coverage assertion and graph-rebuild verification at all —
   describes them only as "AUTHORIZED, DISCLOSED DUPLICATIONS" of
   `trapping_diagnostic_v5.py`'s inline logic, with **no** per-prime/global
   scope statement attached anywhere in that paragraph or elsewhere in v6.
   There is nothing in v6 for v7's citation to be "inherited unchanged"
   from.
2. **The reused code's own actual behavior is the opposite of "never
   global."** Directly read `trapping_diagnostic_v5.py`'s `run_all`
   (lines 444–449):
   ```python
   def run_all(raw_result_path=RUN_B_RAW_RESULT_RELPATH, seed=SEED,
               primes=PRIMES_B):
       per_prime = {}
       for p in primes:
           per_prime[p] = run_diagnostic_for_prime(p, raw_result_path, seed)
       return per_prime
   ```
   There is no `try`/`except` anywhere in this loop. A `TrappingDiagnosticError`
   raised by the coverage assertion or graph-rebuild verification for **one**
   prime propagates uncaught out of `run_all`, aborting the computation for
   **every** prime, including ones already successfully processed and ones
   not yet reached — i.e., in this file's own real, executed behavior, the
   coverage assertion is effectively **global**, not per-prime.

This does **not** leave v7's own REQUIRED OUTPUT ambiguous: the very next
sentence in the same clause states the actual requirement for *this*
amendment's own new script directly — "Halt with an explicit error, reported
for that prime only, if EITHER (a) or (b) fails" — which is a self-sufficient
instruction an Executor can implement without resolving the citation's
accuracy. This is exactly PF-12's shape in the sibling v6 lineage: a
"same mechanism"/"inherited" justification asserted in fix text, not
verified, non-blocking specifically because the required behavior stands on
its own without it. Unlike v6's own PF-12, this one is also a mischaracterization
of what the *cited* prior finding actually established, not merely an
unverified implementation-necessity claim about a mechanism — worth
correcting so a future reader does not conclude v6 already resolved this
exact question (it did not), and does not conclude the reused code already
behaves the desired way (it does not).

## (2) PF-2's fix: is the anomaly branch's failure-handling scope actually unambiguous now?

**Yes — re-read against the exact two-reading risk this task named (the
shape of v6's own round-2 PF-7 finding), and no equivalent risk survives.**

v6's PF-7 was blocking specifically because "GLOBAL, run-aborting check for
that prime's computation" named two incompatible scopes in five words — a
genuine internal self-contradiction that an Executor could resolve either
way. v7's PF-2 fix contains no analogous self-contradiction: "this DOES NOT
HALT OR SKIP that prime's NULL_DEPTH0_FRACTIONS computation -- the 1000 null
trials are computed and archived for that prime REGARDLESS of whether
REAL_DEPTH0_FRACTION matches its expected value" is a single, unconditional,
one-directional instruction with no competing clause anywhere in the same
paragraph or elsewhere in the document. Round 1's own counterexample (two
compliant Executors choosing to continue vs. halt on the same sentence) is
directly foreclosed: there is now exactly one compliant reading. "Instead,
this is a REQUIRED, EXPLICITLY DISCLOSED anomaly... reported ALONGSIDE that
prime's full, complete summary statistics" reinforces, rather than
qualifies, the "always compute" instruction — "alongside" cannot be read as
"instead of."

**One minor, sub-advisory clarity note, not elevated to its own finding**:
"materially disagrees" (for the ANOM-1 comparison) has no stated numeric
tolerance. Given `REAL_DEPTH0_FRACTION` is an exact ratio of integer counts
against an EXPECTED value of exactly 1.0 (100%, matching ANOM-1's own exact
95/95, 132/132, 194/194, 287/287 figures), any deviation at all would be
unambiguously material in practice (there is no floating-point rounding
boundary to fall on either side of), so this does not rise to a
counterexample-bearing gap the way "materially disagrees" language might in
a genuinely continuous-valued comparison. Noted for completeness, not
required before freeze.

**PF-2 CONFIRMED HOLDING.** No residual two-reading risk found.

## (3) PF-3 through PF-7: confirmed applied, with PF-3's own stated rationale re-examined as directed

### PF-4, PF-5, PF-6, PF-7: CONFIRMED APPLIED, no new gap

- **PF-4** (depth-domain broadening disclosure): the domain-broadening
  disclosure is explicit and precise — "unlike v6's own depth(m), which was
  scoped ONLY to the basin-eligible set (`delta_map[m] > 1`, v6's own PF-1
  fix), THIS amendment's `depth(v)` and `is_structural_local_min(v)` are
  evaluated over EVERY structural local minimum, WITHOUT the
  `delta_map[v] > 1` restriction." Matches round 1's required fix exactly;
  independently re-confirmed the `is_structural_local_min` formula itself
  (`delta_map[v] <= min(delta_map[u] for u in adjacency[v])`) is identical
  to the source's inline formula (`delta_map[v] <= min(nbr_deltas)`,
  `nbr_deltas = [delta_map[u] for u in adjacency[v]]`) by direct read of
  `trapping_diagnostic_v5.py` line 234. No gap.
- **PF-5** (raw-count rationale): now states "dividing by N_TRIALS recovers
  the equivalent one-sided permutation p-value, which should NOT be read
  against a conventional significance threshold without a stated,
  pre-registered alpha (none is stated or implied here)" — matches round 1's
  recommended option (a) exactly (accept the trivial-division fact, soften
  to a caveat about threshold interpretation rather than claiming the
  division itself is prevented). No gap.
- **PF-6** (forward-looking deferred control): recorded verbatim in
  `OBJECTIVE_BOUNDARY` with an explicit "Explicitly out of THIS amendment's
  own zero-new-search-cost scope" boundary — matches round 1's advisory
  recommendation, correctly scoped as deferred rather than silently dropped
  or silently required. No gap.
- **PF-7** (RNG-instance/vertex-identity pinning): "a SINGLE,
  FRESHLY-CONSTRUCTED `random.Random(20260806)` instance, constructed once
  per prime, advanced sequentially across all 1000 trials for that prime via
  repeated `.shuffle()` calls on the SAME instance, never re-seeded or
  reconstructed mid-prime" and "vertex set" pinned explicitly to
  `g["vertices"]` ("confirmed a deterministic `sorted(...)` list, not a set
  or BFS-insertion order, by `trapping_diagnostic_v5.build_graph_for_prime`'s
  own return value"). Matches round 1's advisory recommendation; the
  "freshly-constructed... once per prime" language it asked for is present
  verbatim. No gap.

### PF-3: formula CONFIRMED CORRECT and correctly distinguished from the sample formula; the stated JUSTIFICATION does not hold up (PF-10, new)

The formula itself is now unambiguous and correctly distinguishes the two
conventions: "POPULATION standard deviation (divide the sum of squared
deviations from the mean by N_TRIALS, NOT N_TRIALS - 1)" — this is a
correct, precise statement of the population-vs-sample distinction (the only
two conventions in ordinary use), leaving no ambiguity about which formula an
Executor must implement. This closes round 1's PF-3 finding on its own
narrow terms (the formula WAS previously unspecified; it is now pinned to
one specific, named convention).

**But the task's own direction — check whether "the 1000 trials constitute
the full population of interest" actually holds up — does not survive
scrutiny against the rest of this same paragraph's own design.** Three
pieces of the amendment's own text are in tension with a "closed population"
framing:

1. `N_TRIALS = 1000` is explicitly justified earlier in `amendment_scope` as
   "a round, generously-sized number... chosen for statistical stability" —
   "statistical stability" is language for a Monte Carlo *estimate*
   converging as more draws are taken, which presupposes an underlying
   distribution larger than, and independent of, any particular finite
   sample size chosen for it. A genuinely closed population does not have a
   "stability" property as a function of how many of its members you decide
   to include.
2. `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` is explicitly framed, in the very
   same paragraph, as "a one-sided permutation-test count" — the entire
   interpretive machinery of a permutation test treats the realized trials
   as a random sample from the (here, `203!`-to-`611!`-sized, practically
   unenumerable) space of all possible vertex-value permutations, used to
   *estimate* how extreme the real value is relative to that much larger
   reference distribution. That is a sampling framing, not a closed-population
   framing, by construction of the statistic itself.
3. The population-vs-sample SD choice is *usually* consequential precisely
   when the analyst intends the reported SD to *say something about* a
   larger space the sample was drawn from (which is exactly what a
   permutation-test null distribution's SD is used for by any reader who
   wants to gauge, e.g., an approximate z-score) — the standard convention
   in that specific use case (Monte Carlo estimation of a null distribution)
   is the sample formula, an unbiased estimator of the underlying
   distribution's variance, not the population formula.

The **arithmetic** consequence is negligible — round 1's own report already
noted the two formulas differ by ~0.05% relative at N=1000, and this
amendment reports the SD purely as one of several REQUIRED SUMMARY
STATISTICS with no downstream decision rule reading it (`OBJECTIVE_BOUNDARY`
correctly states this control "does not itself constitute a new claim... does
not gate any decision rule"), so this is not blocking. But the specific
*reason given* — "the 1000 trials constitute the full population of interest
for this pre-registered run, not a sample estimating a larger population" —
is not a coherent description of what the rest of the same paragraph does
with that number. Either convention (population or sample) is defensible on
its own terms; what is not defensible is asserting the "closed population"
framing while, two sentences later, computing a one-sided permutation-test
statistic that only makes sense under the opposite framing.

---

## (4) New defects from this round's revision, and interaction among the three per-prime failure-handling branches

Re-read the entire draft with the same skepticism that surfaced PF-8/PF-9/
PF-10 above, specifically for the two things this task named: (a) whether
the newly-restored two-part coverage check interacts correctly with the rest
of the per-prime failure-handling model, and (b) whether a degenerate outcome
during the 1000 permutation trials themselves is left unaddressed.

**(a) Interaction among the three per-prime branches: no operational conflict
found, ordering is sound.** The three branches — (i) coverage
assertion/graph-rebuild verification (item 2), (ii) the REAL_DEPTH0_FRACTION
"materially disagrees" anomaly (item 3's FAILURE-HANDLING SCOPE), and (iii)
whatever could happen inside the 1000 permutation trials themselves (item 4)
— are strictly sequential and non-overlapping in scope by construction of
the document's own item ordering: (i) must pass before delta_map/graph are
trusted at all (a hard per-prime halt, confirmed above); only if (i) passes
does (ii)'s REAL_DEPTH0_FRACTION even get computed (so a coverage-assertion
failure and a "materially disagrees" anomaly can never both apply to the
same prime in the same run — they are mutually exclusive failure points in
the pipeline, not competing branches over the same condition); and (iii)'s
1000 trials are unconditionally required once (i) has passed, regardless of
(ii)'s outcome, per PF-2's fix. No contradiction, no double-halt, no
undefined precedence between these three found.

**(b) Degenerate permutation trials: no unaddressed scenario found.**
Checked specifically for (1) a trial producing zero local minima (which
would make `REAL_DEPTH0_FRACTION`'s per-trial analogue a division by zero):
impossible by construction — since the permutation only reassigns the
existing delta_E value MULTISET across the SAME vertex set, the vertex(es)
holding the multiset's global minimum value are unconditionally structural
local minima under `is_structural_local_min`'s own `<=`-against-all-neighbours
definition (no neighbour can have a strictly smaller value than the
multiset's own minimum), so `n_local_min >= 1` in every one of the 1000
trials, on every prime, with no possible zero-denominator case. (2) A
permuted delta_map failing the coverage/adjacency lookups the way a
corrupted vertex identity would: impossible by construction — the
permutation reassigns values onto the SAME, already-verified vertex key set
(`dict(zip(g["vertices"], shuffled))`), so no KeyError-class failure mode
from the coverage assertion's own concern (mismatched vertex identities) can
arise inside a trial; that class of failure is fully retired by the earlier,
one-time coverage assertion (i) and cannot recur per-trial. No degenerate
in-trial scenario was found unaddressed.

**(c) PF-9 [ADVISORY, NEW]: `required_artifacts_note`'s explicit code diff
omits the coverage assertion's own duplication status.** Quoting the
relevant clause in full: "`is_structural_local_min` and `depth(v)` are
AUTHORIZED, DISCLOSED DUPLICATES of `specification_v6.yaml`'s own formulas
(which are themselves disclosed duplicates of `trapping_diagnostic_v5.py`'s
inline logic) -- this amendment does NOT import `funnel_structure_diagnostic_v6.py`
or `descent_walk_hardened.py`... and `build_isogeny_graph` functions as
needed (IMPORTED UNCHANGED, by reference)." This correctly classifies
`is_structural_local_min`/`depth(v)` as duplicates and `degree_sequence_check`
(one half of the graph-rebuild verification) as a genuine import. It never
classifies the coverage assertion's own `vertex_set`/`n_matched` logic (item
2(a)) at all — and, exactly like `is_structural_local_min`, that logic is
**not** a standalone importable symbol in `trapping_diagnostic_v5.py`
(confirmed inline at lines 186–190, inside `run_diagnostic_for_prime`, by
direct read) — it must be re-implemented as a disclosed duplicate in the new
script, the same as `is_structural_local_min` is. `required_artifacts_note`
is the document's own designated, GD-9/GD-10-mandated location for this
exact classification, and it is silent on this one component. This does not
create an operational gap for the Executor (item 2's own body already gives
the exact formula to implement, so an Executor has everything needed to
write correct code) — but it is a real, checkable incompleteness in the
explicit function-level diff this campaign's own standing repair exists to
require, the same species of omission (a reuse/duplication classification
left unstated for one component while stated for a structurally identical
sibling component) PF-2 was originally raised for in the v6 lineage.

No other new defect was found. `required_artifacts`, `budget`, and the
`amendment_scope` preamble are unchanged since round 1 and remain internally
consistent with the corrected text above.

---

## (5) Whole-draft coherence pass after one round of seven compounded patches

Specifically checked, per this task's own direction, whether round 1's seven
findings — applied together in a single revision pass, unlike v6's lineage
which spread its findings across three separate rounds — compose cleanly or
show a side-effect defect visible only when read together.

**No contradiction or redundancy found among the seven applied fixes
themselves.** Each `pfN_summary` (lines 89–130) was cross-read against its
corresponding operative clause in `inputs.delta_e_permutation_null_control_v7`
and found to match in substance (PF-1's summary correctly describes the
two-part restoration verified in section (1) above; PF-2's summary correctly
describes the unconditional-computation fix verified in section (2); PF-3
through PF-7's summaries correctly describe their own applied text, verified
in section (3)). Unlike v6's own PF-13 (two structurally analogous
accounting assertions assigned different, unreconciled severities, visible
only because they were fixed in different rounds), v7 has only one
accounting-style check in this amendment (the coverage assertion/graph-rebuild
verification) — there is no sibling assertion in this document for its scope
to drift out of alignment with, so PF-13's specific failure shape does not
recur here. PF-8/PF-9/PF-10 above are new findings, but none is a
contradiction *between* two of round 1's seven fixes; each is a defect
*within* a single fix's own justifying prose (PF-8, PF-10) or a completeness
gap in a section round 1's fixes did not touch (PF-9, in
`required_artifacts_note`, which none of PF-1 through PF-7 modified).

The document remains verbose (seven `PF-N FIX APPLIED` inline annotations
inside one already-dense paragraph, echoing round 1's own summary text
closely) but legible and traceable end-to-end on a full re-read; no reader
would need to reconcile two competing statements of the same requirement
anywhere in the current text.

---

## Findings summary

| ID | Status this round | Location | One-line |
|---|---|---|---|
| PF-1 | **CONFIRMED HOLDING** | Coverage assertion / graph-rebuild verification | Restored two-part check verified formula-by-formula against `trapping_diagnostic_v5.py`'s own `coverage_assertion_pass`/`graph_rebuild_independently_verified_correct` code, an exact match, not merely re-read from prose |
| PF-2 | **CONFIRMED HOLDING** | REAL_DEPTH0_FRACTION anomaly branch | Unconditional "computed and archived... REGARDLESS" language leaves no residual two-reading risk of the shape v6's own round-2 PF-7 found |
| PF-3 | Formula CONFIRMED CORRECT; **NEW GAP FOUND (PF-10)** | SD formula | Population/sample distinction now precisely formulated and correctly pinned to population, but the stated justification ("full population of interest") is in tension with the amendment's own Monte-Carlo/permutation-test framing |
| PF-4 | CONFIRMED APPLIED | depth-domain disclosure | Explicit, precise, matches round 1's requirement |
| PF-5 | CONFIRMED APPLIED | raw-count rationale | Softened as recommended (option a) |
| PF-6 | CONFIRMED APPLIED | deferred control | Recorded, correctly scoped as deferred |
| PF-7 | CONFIRMED APPLIED | RNG/vertex pinning | "freshly-constructed... once per prime" and `g["vertices"]` pinning both present verbatim |
| PF-8 | **ADVISORY, NEW** | Coverage assertion FAILURE-HANDLING SCOPE citation | "inherited unchanged" from v6's PF-3/PF-7/PF-13 is false (those findings never addressed the coverage assertion) and mischaracterizes the reused code's own actual (effectively global) behavior; non-blocking since the required behavior is independently, unambiguously stated in the same clause |
| PF-9 | **ADVISORY, NEW** | `required_artifacts_note` code diff | Coverage assertion's `vertex_set`/`n_matched` logic, not importable, is omitted from the explicit disclosed-duplicate classification given to `is_structural_local_min`/`depth(v)` |
| PF-10 | **ADVISORY, NEW** | SD formula's stated rationale | "Full population of interest" does not survive being checked against the same paragraph's own "statistical stability" and "one-sided permutation-test" framing; arithmetic difference negligible |

---

## Required controls / checks before dispatch

- PF-1, PF-2, PF-4, PF-5, PF-6, PF-7: no further action required; all
  CONFIRMED HOLDING/APPLIED this round, independently re-traced against the
  actual code and the actual draft text, not merely re-read from either
  report's prose.
- **PF-8 [ADVISORY]:** correct or remove the "per specification_v6.yaml's own
  PF-3/PF-7/PF-13 unified per-prime failure-handling model, inherited
  unchanged" citation for the coverage assertion — either state that this
  amendment establishes its own per-prime scope for this check (not
  inherited from v6, which never addressed it), or drop the citation and
  keep only the operative "Halt... reported for that prime only" sentence,
  which is already sufficient on its own.
- **PF-9 [ADVISORY]:** add the coverage assertion (item 2(a)) to
  `required_artifacts_note`'s explicit disclosed-duplicate list, alongside
  `is_structural_local_min` and `depth(v)`, since it is likewise not a
  standalone importable symbol in `trapping_diagnostic_v5.py`.
- **PF-10 [ADVISORY]:** either restate PF-3's rationale to match the
  amendment's own Monte-Carlo/permutation-test framing (e.g., "reported as
  population SD by convention, describing the exact archived 1000-value
  dataset itself; a reader using this SD to approximate the null
  distribution's own dispersion should note the sample formula would differ
  by ~0.05% at this N and is the more standard convention for that specific
  inferential use"), or switch to the sample formula if the intent is
  genuinely inferential. Either is a zero-new-search, text-only fix; the
  numeric difference is immaterial either way.
- Neither PF-8, PF-9, nor PF-10 requires a third full review round before
  freeze; all three are text-only, zero-search-cost additions, consistent
  with this lineage's own established practice (v6's own PF-10/PF-11/
  PF-12/PF-13, and this draft's own PF-3 through PF-7) for advisory-only
  findings applied without a dedicated re-verification round.

## Counterexample or mutation

**PF-8's counterexample, executed directly against the actual code:** an
Executor's new script that reuses `trapping_diagnostic_v5.py`'s own
`run_all`-style bare loop (no per-prime `try`/`except`) for the coverage
assertion, reasonably believing v7's own citation that this scope is
"inherited unchanged" from v6, would produce a script whose coverage
assertion is, in fact, global — directly violating v7's own "reported for
that prime only" requirement two sentences later. Nothing in v6 would have
told that Executor otherwise (confirmed: v6's own text never states a scope
for this specific check), and the actual reused file's own `run_all`
(confirmed by direct read, lines 444–449, no `try`/`except`) would reinforce
rather than correct the mistaken belief.

**PF-10's counterexample, illustrative not a falsifier of the reported
number:** a future reader using `NULL_DEPTH0_FRACTIONS`'s standard deviation
to compute an approximate z-score for `REAL_DEPTH0_FRACTION` relative to the
null distribution (a natural, foreseeable use of exactly this statistic,
given `NULL_EXCEEDS_OR_EQUALS_REAL_COUNT` is reported alongside it for the
same comparative purpose) would, under standard statistical convention for
that specific inferential use, reach for the sample formula — the population
formula this draft mandates differs from it by a factor of
`sqrt(1000/999) ≈ 1.0005`, immaterial in magnitude but not in which
convention the amendment's own stated rationale claims to be using.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense (toy-scale
infrastructure and a statistical-control archival task, `asymptotic_claim:
null` throughout, correctly inherited, unchanged since round 1). The
relevant baseline remains this campaign's own instrument- and
spec-scrutiny discipline (v6's own PF-7/PF-8/PF-12/PF-13: "trace a fix's own
confidence-building or justifying prose, not only its operative
requirement"). Applied here, that discipline confirms PF-1 and PF-2's fixes
hold their own operative requirements exactly (formula-traced, not
prose-trusted), while finding the same class of defect this lineage's
sibling amendment repeatedly produced in its own fix text — a citation or
rationale that does not survive being checked, alongside (unlike the
sibling's PF-7/PF-8) an operative requirement that, in both new findings
here, remains correctly and independently stated regardless of the flawed
citation or rationale next to it. This round converges faster than v6's own
three-round lineage (no blocking defect survives a single revision round
here, versus two), which is consistent with round 1's own narrower scope (a
single-part control, not a two-part PART A/PART B amendment) rather than
evidence of a lower review bar.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` remains correctly empty (a
gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage and
its v6 sibling. No finding here implicates a numbered heuristic; PF-8/PF-9/
PF-10 are citation-accuracy, disclosure-completeness, and statistical-
rationale-coherence gaps in diagnostic contract text, not claims about the
underlying ECDLP-adjacent problem.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly, unchanged since round 1); the per-attempt-cost ×
inverse-success-probability review does not apply. The `900s`/`0.3`
CPU-hour budget is unchanged from round 1 and remains realistic
(re-confirmed: no new computation of any kind is introduced by any of PF-1
through PF-10). PF-8/PF-9/PF-10 are all text-only, zero-cost. The one live
evidentiary concern this round closes is PF-1/PF-2's own operational
correctness (both now confirmed holding by direct trace, not merely by
prose); PF-8/PF-9/PF-10 carry no run-time or evidentiary risk, only
documentation-clarity risk for a future reader tracing the same citations
this review traced.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment; `H-SSIQ-36e970.scope_ceiling` (toy, inherited) correctly
stated and not exceeded, unchanged since round 1. `OBJECTIVE_BOUNDARY`
correctly states this control "does not itself constitute a new claim...
does not resolve the funnel-structure mechanism question" — still matches
`DEC-20260806-498531`'s ranked action item (1) exactly, with actions (2) and
the B/X-widening test still correctly and explicitly deferred, not silently
dropped. No scope inflation found this round.

## Proof architecture challenges

Not applicable — this remains a direct instrument-level statistical control
archival task, not a proof-oriented proposal
(`H-SSIQ-36e970.proof_search_map.not_applicable_reason`, inherited unchanged,
attacked and held every prior batch including this one).

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v7.yaml` as committed
at `cebbc300`, `status: draft`: round 1's two blocking findings (PF-1, PF-2)
are both genuinely resolved on their own stated terms, independently
re-verified by direct formula-by-formula trace against
`trapping_diagnostic_v5.py`'s own code (not by trusting the draft's own
prose or round 1's report that the fix would work). PF-1's restored coverage
assertion and graph-rebuild verification are an exact match to the source
file's own `coverage_assertion_pass`/`graph_rebuild_independently_verified_correct`
logic. PF-2's anomaly branch states its required behavior unconditionally,
with no residual two-reading risk of the shape v6's own round-2 PF-7 found.
PF-4 through PF-7 are confirmed correctly applied against round 1's own
required-fix text. **No blocking defect survives this round.** Three new
advisory findings round out this pass: PF-8 (the coverage assertion's
"inherited unchanged from v6" citation is false and describes the reused
code's own real behavior backwards, non-blocking since the operative
requirement is independently and unambiguously stated in the same clause),
PF-9 (`required_artifacts_note`'s explicit code diff omits the coverage
assertion's own non-importable, must-duplicate status, unlike its sibling
`is_structural_local_min`), and PF-10 (PF-3's SD formula is now correctly
and precisely specified, but its stated "closed population" rationale is in
tension with the same paragraph's own Monte-Carlo/permutation-test framing,
with a negligible arithmetic consequence). None requires redesigning the
control or a further review round; all three are resolvable in the same
revision pass, at zero new search cost, per this lineage's own established
practice for advisory-only findings (v6's own PF-10 through PF-13; this
draft's own PF-3 through PF-7).

## Next concrete action

Coordinator: this draft may proceed to `status: approved` / `frozen_at` once
PF-8, PF-9, and PF-10 are applied as text-only additions (correct or drop the
coverage assertion's "inherited unchanged from v6" citation; add the
coverage assertion to `required_artifacts_note`'s disclosed-duplicate list;
restate or reconcile PF-3's SD rationale with the amendment's own
permutation-test framing) — consistent with this lineage's own established
practice of applying advisory-only findings without a dedicated
re-verification round (v6's own PF-10 through PF-13 were applied this way;
this draft's own PF-3 through PF-7 were applied and confirmed this way in
this very round). If the Coordinator prefers a third pass to re-confirm
PF-8/PF-9/PF-10's specific text, that is available but not, on this review's
own findings, required before freeze.

## Overall verdict

**FREEZE-WITH-FIXES.** No blocking item remains. Required before
`status: approved` / `frozen_at`:

1. **[ADVISORY]** PF-8 — correct or remove the coverage assertion's "per
   specification_v6.yaml's own PF-3/PF-7/PF-13 unified per-prime
   failure-handling model, inherited unchanged" citation, which is false on
   direct re-check of v6's own text and describes the reused code's real
   behavior (no `try`/`except` in `run_all`) backwards; the operative
   requirement itself ("halt... reported for that prime only") is already
   correct and unambiguous and needs no change.
2. **[ADVISORY]** PF-9 — add the coverage assertion's own (not importable,
   must-duplicate) status to `required_artifacts_note`'s explicit
   function-level code diff, alongside `is_structural_local_min` and
   `depth(v)`.
3. **[ADVISORY]** PF-10 — reconcile PF-3's "full population of interest"
   rationale with the same paragraph's own "statistical stability" and
   "one-sided permutation-test" framing, or switch to the sample SD formula;
   the numeric consequence is negligible either way.

PF-1 and PF-2 (round 1's blocking findings) are both **CONFIRMED HOLDING**,
independently re-derived by direct formula-by-formula code trace in this
round, not trusted from either the draft's own prose or round 1's report
that the fix would work. PF-4 through PF-7 are **CONFIRMED APPLIED**.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2
  task_id: TASK-20260806-62839b
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v7.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970), committed at snapshot cebbc300, parented on
    6d9f7e55 (the round-1-reviewed draft) -- a revision applying round 1's
    two blocking findings (PF-1: the coverage assertion had been silently
    narrowed to a bare cardinality comparison; PF-2: the REAL_DEPTH0_FRACTION
    anomaly branch stated a disclosure obligation with no failure-handling
    scope) plus five advisory findings (PF-3 through PF-7: SD formula,
    depth-domain disclosure, raw-count rationale, a deferred control,
    RNG/vertex-identity pinning), all in a single revision pass.
  objections:
    - "PF-8 [ADVISORY, NEW]: The restored coverage assertion's introductory clause -- 'per-prime (never global -- per specification_v6.yaml's own PF-3/PF-7/PF-13 unified per-prime failure-handling model, inherited unchanged)' -- is false on direct re-check of specification_v6.yaml's own text: v6's PF-3 fixed crosscheck_pass's scope and PF-7/PF-13 fixed the basin-accounting-assertion's scope; v6 never states a per-prime/global scope for the coverage assertion or graph-rebuild verification anywhere, describing them only as 'authorized, disclosed duplications' with no attached scope statement. Worse, the reused code's own actual behavior is the opposite of 'never global': trapping_diagnostic_v5.py's run_all (lines 444-449, directly read) has no try/except around each prime's run_diagnostic_for_prime call, so a coverage-assertion TrappingDiagnosticError for one prime propagates uncaught and aborts every prime's processing in that file's own real, executed behavior. Non-blocking: v7's own next sentence ('Halt with an explicit error, reported for that prime only, if EITHER (a) or (b) fails') states the actual required behavior for this amendment's own new script directly and self-sufficiently, independent of the flawed citation -- the same shape as v6's own round-3 PF-12 finding (an unverified 'same mechanism'/'inherited' justification, non-blocking because the required behavior stands without it)."
    - "PF-9 [ADVISORY, NEW]: required_artifacts_note's explicit, GD-9/GD-10-mandated function-level code diff names is_structural_local_min and depth(v) as AUTHORIZED, DISCLOSED DUPLICATES (correctly, since neither is importable) but never classifies the coverage assertion's own vertex_set/n_matched logic (item 2(a)) at all, despite that logic likewise being inline-only, not a standalone importable symbol in trapping_diagnostic_v5.py (confirmed at lines 186-190 by direct read, inside run_diagnostic_for_prime). Does not create an operational gap (item 2's own body already states the exact formula to implement), but is a real, checkable incompleteness in the explicit code-diff this campaign's own standing repair (GD-9/GD-10) exists to require, for a component structurally identical in reuse status to a sibling component (is_structural_local_min) the same note DOES correctly classify."
    - "PF-10 [ADVISORY, NEW]: PF-3's SD formula is now correctly and precisely specified (population, divide by N_TRIALS, correctly distinguished from the sample /(N_TRIALS-1) formula) -- but its stated justification, 'the 1000 trials constitute the full population of interest for this pre-registered run, not a sample estimating a larger population,' is in tension with the rest of the same paragraph's own design: N_TRIALS is explicitly 'chosen for statistical stability' (Monte Carlo estimation language, presupposing convergence toward an underlying distribution larger than any one finite sample), and NULL_EXCEEDS_OR_EQUALS_REAL_COUNT is explicitly framed as 'a one-sided permutation-test count,' whose entire interpretive machinery treats the 1000 trials as a sample from the (203!-to-611!-sized, practically unenumerable) space of all vertex-value permutations. Under that framing -- the amendment's own -- sample SD, not population SD, is the standard convention for estimating an underlying distribution's dispersion from a Monte Carlo sample. The arithmetic consequence is negligible (~0.05% relative at N=1000, as round 1's report already noted) and either convention is defensible on its own terms, so this is not blocking, but the specific stated rationale does not survive being checked against what the same paragraph does with the resulting number two sentences later."
    - "PF-1 [round 1's finding, CONFIRMED HOLDING]: independently re-traced formula-by-formula against trapping_diagnostic_v5.py's own coverage_assertion_pass/graph_rebuild_independently_verified_correct computation (lines 181-208, direct read), not merely re-read from either draft's prose. vertex_set = set(g[\"vertices\"]); n_matched = len([v for v in delta_map if v in vertex_set]); confirm n_matched == archived_n_vertices EXACTLY matches the real code's vertex_set = set(vertices); matched_vertices = [v for v in delta_map if v in vertex_set]; n_matched = len(matched_vertices); coverage_assertion_pass = bool(n_matched == archived_n_vertices). degree_sequence_check(g).pass AND len(g[\"vertices\"]) == archived_n_vertices EXACTLY matches degseq_pass and vertex_count_match. Archived-vertex-count figures (2437: 203, 3889: 324, 5737: 478, 7333: 611) independently re-confirmed against ARCHIVED_N_VERTICES (line 89) by direct read, not copied from either draft's own citation."
    - "PF-2 [round 1's finding, CONFIRMED HOLDING]: re-read against the exact two-reading risk this task named (v6's own round-2 PF-7 shape). 'this DOES NOT HALT OR SKIP that prime's NULL_DEPTH0_FRACTIONS computation -- the 1000 null trials are computed and archived for that prime REGARDLESS of whether REAL_DEPTH0_FRACTION matches its expected value' is a single, unconditional, one-directional instruction with no competing clause anywhere in the document -- no equivalent of v6's own 'GLOBAL... for that prime's computation' self-contradiction found. Round 1's own two-Executor counterexample is directly foreclosed."
    - "PF-4/PF-5/PF-6/PF-7 [round 1's advisory findings, CONFIRMED APPLIED]: depth-domain broadening disclosed explicitly and precisely (matches round 1's required fix); raw-count rationale softened per round 1's recommended option (a); the deferred control is recorded and correctly scoped as out of this amendment's own zero-new-search-cost boundary; RNG-instance ('freshly-constructed... once per prime') and vertex-identity (g[\"vertices\"], confirmed a deterministic sorted list) are both pinned explicitly, matching round 1's advisory recommendation verbatim."
  required_controls:
    - "PF-8 [ADVISORY]: correct or remove the coverage assertion's false 'inherited unchanged from v6's PF-3/PF-7/PF-13' citation; the operative 'halt... reported for that prime only' requirement is already correct and needs no change."
    - "PF-9 [ADVISORY]: add the coverage assertion's own non-importable, must-duplicate status to required_artifacts_note's explicit code diff, alongside is_structural_local_min and depth(v)."
    - "PF-10 [ADVISORY]: reconcile PF-3's 'full population of interest' rationale with the same paragraph's own Monte-Carlo/permutation-test framing (N_TRIALS chosen 'for statistical stability'; NULL_EXCEEDS_OR_EQUALS_REAL_COUNT framed as a permutation-test statistic), or switch to the sample SD formula. Numeric consequence negligible either way (~0.05% relative at N=1000)."
    - "None of PF-8/PF-9/PF-10 requires a third review round; all are text-only, zero-search-cost additions, per this lineage's own established practice for advisory-only findings applied without a dedicated re-verification round."
  counterexample_or_mutation: >-
    PF-8: an Executor implementing the coverage assertion by reusing
    trapping_diagnostic_v5.py's own run_all-style bare loop (no per-prime
    try/except), reasonably relying on v7's own citation that this scope is
    "inherited unchanged" from v6, would produce a script whose coverage
    assertion is, in fact, global -- directly violating v7's own "reported
    for that prime only" requirement two sentences later. Nothing in v6
    would correct this belief (confirmed: v6's own text never states a scope
    for this specific check), and trapping_diagnostic_v5.py's own run_all
    (confirmed by direct read, no try/except) would reinforce rather than
    correct it.
    PF-10 (illustrative, not a falsifier of the reported value): a future
    reader computing an approximate z-score for REAL_DEPTH0_FRACTION against
    NULL_DEPTH0_FRACTIONS's own SD (a natural use, given
    NULL_EXCEEDS_OR_EQUALS_REAL_COUNT is reported alongside for the same
    comparative purpose) would, under standard convention for that specific
    inferential use, reach for the sample formula -- differing from the
    mandated population formula by a factor of sqrt(1000/999) ~= 1.0005,
    immaterial in magnitude but not in which convention the stated rationale
    claims to use.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale infrastructure, asymptotic_claim null throughout, correctly
    inherited, unchanged since round 1). The relevant baseline remains this
    campaign's own instrument- and spec-scrutiny discipline established by
    the sibling v6 lineage (PF-7/PF-8/PF-12/PF-13: trace a fix's own
    confidence-building or justifying prose, not only its operative
    requirement). Applied here: PF-1 and PF-2's operative requirements both
    hold exactly under direct formula-level trace; PF-8 and PF-10 are the
    same class of defect the sibling lineage repeatedly produced in its own
    fix text (a citation or rationale that does not survive being checked),
    but in both cases here the operative requirement next to the flawed
    citation/rationale remains independently correct and unambiguous, unlike
    v6's own PF-7 (where the operative requirement itself was
    self-contradictory).
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held, consistent with every prior review in this lineage and its v6 sibling. No finding here implicates a numbered heuristic."
  cost_model_challenges:
    - "No asymptotic-cost claim is made anywhere (asymptotic_claim: null, correctly, unchanged since round 1); the per-attempt x inverse-success-probability review does not apply."
    - "The 900s/0.3 CPU-hour budget is unchanged and remains realistic; no new computation is introduced by PF-1 through PF-10. PF-8/PF-9/PF-10 are all text-only, zero-cost."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded, unchanged since round 1."
    - "OBJECTIVE_BOUNDARY correctly states this control does not itself constitute a new claim and does not resolve the funnel-structure mechanism question, matching DEC-20260806-498531's ranked action item (1) exactly, with actions (2) and the B/X-widening test correctly and explicitly deferred rather than silently dropped. No scope inflation found this round."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason remains correctly reasoned and inherited unchanged -- a direct instrument-level statistical control archival task, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v7.yaml as committed
    at cebbc300, status: draft: round 1's two blocking findings (PF-1, PF-2)
    are both genuinely resolved on their own stated terms, independently
    re-verified by direct formula-by-formula trace against
    trapping_diagnostic_v5.py's own code, not by trusting the draft's own
    prose or round 1's report that the fix would work. PF-1's restored
    coverage assertion and graph-rebuild verification are an exact match to
    the source file's own logic. PF-2's anomaly branch states its required
    behavior unconditionally, with no residual two-reading risk of the shape
    v6's own round-2 PF-7 found. PF-4 through PF-7 are confirmed correctly
    applied. No blocking defect survives this round. Three new advisory
    findings (PF-8: a false "inherited from v6" citation, non-blocking since
    the operative requirement stands on its own; PF-9: required_artifacts_note's
    code diff omits the coverage assertion's own must-duplicate status; PF-10:
    PF-3's SD rationale is in tension with the amendment's own permutation-test
    framing, negligible numeric consequence) round out this pass. None
    requires redesigning the control or running new search; all are
    resolvable in one revision pass at zero new search cost.
  next_concrete_action: >-
    Coordinator: this draft may proceed to status: approved / frozen_at once
    PF-8, PF-9, and PF-10 are applied as text-only additions (correct or
    drop the coverage assertion's false "inherited unchanged from v6"
    citation; add the coverage assertion to required_artifacts_note's
    disclosed-duplicate list; reconcile or drop PF-3's "closed population"
    rationale) -- consistent with this lineage's own established practice of
    applying advisory-only findings without a dedicated re-verification
    round. A third pass to re-confirm PF-8/PF-9/PF-10's specific text is
    available at the Coordinator's discretion but is not, on this review's
    own findings, required before freeze.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    No graph built, no delta_E search run, no permutation trial executed --
    this review is a specification trace, not an execution. Directly read
    (not sampled from prose): trapping_diagnostic_v5.py in full (500 lines),
    specifically run_diagnostic_for_prime's coverage_assertion_pass /
    graph_rebuild_independently_verified_correct computation (lines 161-208)
    compared formula-by-formula against v7's own stated (a)/(b) text, and
    run_all's loop (lines 444-449) checked directly for the presence or
    absence of a try/except around each prime's run_diagnostic_for_prime
    call (confirmed: none exists). specification_v6.yaml in full, re-read
    specifically to confirm what PF-3/PF-7/PF-13 did and did not establish
    (crosscheck_pass and the basin-accounting assertion; not the coverage
    assertion). specification_v7.yaml in full (326 lines), all seven
    pfN_summary entries cross-read against their corresponding operative
    clauses. RT-PREFREEZE-EXP-SSIQ-a85692-v7.md (round 1) and
    RT-PREFREEZE-EXP-SSIQ-a85692-v6-round2.md /
    RT-PREFREEZE-EXP-SSIQ-a85692-v6-round3.md (sibling lineage precedent) in
    full. git log/git status confirmed specification_v7.yaml's current
    committed state (cebbc300, parented on 6d9f7e55) and clean working tree.
    No file written outside this report; no run artifact, specification
    file, or ledger record edited.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-010/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v7-round2.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v6.yaml and
    specification_v7.yaml themselves), the round-1 report, and every ledger
    record are untouched.
  verdict: FREEZE-WITH-FIXES
```
