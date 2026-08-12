# RT-BATCH-006 — Red Team review of RUN-SSIQ-a85692-c (EXP-SSIQ-a85692 v3,
# H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-006

**Reviews the Coordinator-committed snapshot at commit `cc786884`** (parent
`7f40426b`), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/archives/TASK-20260805-2d8575-receipt.yaml`,
covering `RUN-SSIQ-a85692-c` under `specification_v3.yaml`'s amendment
(frozen `7f40426b`) only. Nothing below is drawn from, or asserted about, any
working-tree-only state. This report changes nothing under
`experiments/EXP-SSIQ-a85692/` or any ledger record — those remain the
Coordinator's alone to touch. Read in full: `specification_v2.yaml`,
`specification_v3.yaml`, `RT-PREFREEZE-EXP-SSIQ-a85692-v3.md`,
`implementation/reanalyze_v3.py`, the complete `RUN-SSIQ-a85692-c` package
(`manifest.yaml`, `raw-result.json`, `execution_report.yaml`,
`synthetic_self_test.json`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`), the archive receipt,
`goal.yaml`'s GD-8/GD-9 entries and `next_action`, `EV-SSIQ-f3ce32.yaml`,
`DEC-20260805-5f5ac6.yaml`, `H-SSIQ-36e970.yaml`, and `RT-BATCH-005.md`
(including its Front 4 ranking this batch implements) in full. Independently
re-derived (not merely re-cited): the trapped-fraction survivor arithmetic
for both arms against `RUN-SSIQ-a85692-b/raw-result.json` directly, and the
data-schema question of whether `c_null_label.per_prime` carries its own `N`
field (it does not — checked directly against the raw JSON, see Objection 1).

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
    Subagent frontmatter under this runtime cannot express a policy (CLAUDE.md,
    "Model policy note"); this session runs `model: inherit`. Every
    credentialed backend under this environment has previously been found
    unprobeable (VAL/RT-BATCH-003/004/005, RT-PREFREEZE-EXP-SSIQ-a85692[-v2,-v3]),
    so this is recorded as the standing condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    is not corroboration from a distinct model and does not upgrade the
    campaign's evidence tier by itself. A Validator (TASK-20260805-47be12) is
    reviewing the same run independently and in parallel; this report was
    produced without coordinating with it and stands alone.
```

---

## Bottom line up front

GD-8's fix is clean and independently verified: `trapped_exclusion_filter_v3`
is implemented exactly as specified, its worked-check arithmetic reproduces
to full float precision, and `decision_rule_v3`'s new gate fires exactly as
predicted. **GD-9's fix is a different story.** The synthetic self-test that
`specification_v3.yaml` requires as the *only* runtime evidence for
`c_null_label_comparison_v3`'s fit-and-bootstrap branch — required
specifically because the pre-freeze review proved that branch is
structurally unreachable on this run's real data — **does not call
`c_null_label_comparison_v3` at all.** `run_synthetic_self_test_v3` invokes
`dht.ols_loglog_fit`/`dht.bootstrap_gap_ci` directly and reimplements the
comparison rule inline (`reanalyze_v3.py` lines 242–272), bypassing the one
function this whole exercise exists to validate. `ols_loglog_fit` and
`bootstrap_gap_ci` already had independent runtime evidence of correctness
from `RUN-SSIQ-a85692-b`'s own real-arm fit (`EV-SSIQ-f3ce32` O-1/O-2, both
reviewers re-derived it by hand). The self-test therefore re-confirms
functions the campaign already knew worked, and supplies **zero** direct
runtime coverage of `c_null_label_comparison_v3`'s own wiring — the
cross-dict indexing (`N` pulled from `real_per_prime`, medians pulled from
`null_per_prime`, keyed by a third list, `null_survivors`), the `min_primes`
gate, and the `NOT-EVALUABLE`-vs-boolean branching that is the actual new
code GD-9's fix adds. This is not a hypothetical gap: the same species of
failure the pre-freeze review (PF-1) already flagged for the *real-data*
path — "a correct implementation and a stub... are indistinguishable" —
recurs, undetected, inside the fix built specifically to close that gap.
Every artifact in this run's package (`raw-result.json`, `manifest.yaml`,
`execution_report.yaml` OBS-4, the archive receipt) states or implies that
the self-test is runtime evidence "that `c_null_label_comparison_v3`'s
fit-and-bootstrap branch works correctly." **That claim is not supported by
what the test actually exercises**, and should not be carried into any
successor record without this correction.

GD-8 and GD-9's core fixes are otherwise sound, the run executed honestly,
DATA-UNAVAILABLE-BLOCKED is the mechanically correct and pre-disclosed
outcome, and the process overhead of running this batch — while its
substantive outcome was foreseeable at pre-freeze — was not wasted: it
surfaced this new gap, which a lighter-weight Coordinator-only calculation
would not have.

---

## Front 1 — Does the synthetic self-test actually prove what it claims?

**No, not for the function it exists to validate.** Read directly
(`experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py`):

- `c_null_label_comparison_v3` is defined at lines 141–216 and has **exactly
  one call site in the entire file**, at line 415, inside `main()`'s
  real-data path (confirmed by `grep -n c_null_label_comparison_v3`: every
  other occurrence is a docstring, a log line, or a JSON key name — never a
  second invocation).
- `run_synthetic_self_test_v3` (lines 223–356), called from `main()` at line
  400, **never calls `c_null_label_comparison_v3`**. It calls
  `dht.ols_loglog_fit`/`dht.bootstrap_gap_ci` directly on hand-constructed
  lists (lines 242, 243, 248–249), then computes
  `synthetic_control_failure = bool(lo is not None and lo > 0.0)` (line 272)
  — a **second, independent, hand-written copy** of the comparison rule
  `c_null_label_comparison_v3` line 193 already implements, not a call to
  it.
- Consequently the self-test exercises: (a) `ols_loglog_fit`/
  `bootstrap_gap_ci`, which already had independent runtime evidence of
  correctness from `RUN-SSIQ-a85692-b`'s own real-arm gamma fit
  (`EV-SSIQ-f3ce32` O-1/O-2 — both BATCH-005 reviewers independently
  re-derived the aggregate-counter arithmetic and the CI machinery by hand);
  and (b) a hand-copied restatement of one comparison expression. It does
  **not** exercise: the `len(null_survivors) < min_primes` gate (line 160),
  the `real_per_prime[p]["N"]` / `null_per_prime[p]["greedy_median"]`
  cross-dict indexing (lines 181–183), the `sorted(null_survivors)`
  ordering step, or any of `c_null_label_comparison_v3`'s own control flow.

This is not an abstract concern. I independently checked whether the
cross-dict indexing choice (`N` from `real_per_prime`, medians from
`null_per_prime`) is even *structurally forced* by the data, and confirmed
directly against `RUN-SSIQ-a85692-b/raw-result.json`:
`descent_metrics.per_prime["2437"]` carries keys `[N, greedy_median,
greedy_trapped_fraction, is_extension_prime, random_median]`;
`c_null_label.per_prime["2437"]` carries only `[greedy_median,
greedy_trapped_fraction, random_median]` — **no `N` field**. So pulling `N`
from the real arm is the *only* correct wiring for this data schema, which
makes it exactly the kind of implementation detail a synthetic self-test
should independently confirm (e.g., by constructing synthetic
`null_per_prime` dicts that likewise omit `N`, to force the function to use
the real-arm source) rather than the kind that is safe to leave unverified.
**A version of `c_null_label_comparison_v3` that swapped which dict `N` or
the medians came from, or that had an off-by-one in `min_primes`, or that
failed to `sorted()` before zipping the three lists, would pass this
self-test unchanged** — the self-test's own inputs never flow through that
function.

The self-test's discriminating power against a *subtly wrong*
implementation of the thing it is named for is therefore low, not high. Its
discriminating power against `ols_loglog_fit`/`bootstrap_gap_ci` themselves
being broken is real but redundant with prior evidence. The "exact power
law, zero noise" construction (Objection raised in the launching task) is a
separate, smaller concern layered on top: because every point lies exactly
on the fitted line, the bootstrap CI degenerates to a point
(width ≈ 6e-16), which is a clean, unambiguous check for the arithmetic it
does exercise — but that arithmetic is not the code under review.

**This is a new, previously undisclosed defect of the same species as GD-8/
GD-9 themselves: a required control (here, a required *validation artifact*)
that "ran" and produced a passing report block, without its comparison logic
ever touching the function it was built to validate.** It differs from GD-9
in mechanism (GD-9 was a hard-coded flag findable by `grep`; this is a test
that calls the right *library* but the wrong *wrapper*) but is the identical
failure mode this campaign's own standing repair (GD-9,
`standing_repair_adopted`) exists to catch: "a control's failure_consequence
being named... does not establish that the control's comparison logic was
ever implemented... verify by direct code reading." That discipline was
applied to `c_null_label_comparison_v3` itself at pre-freeze (PF-1) but not,
apparently, to the self-test built to satisfy PF-1's own requirement.

## Front 2 — Was running this batch, given the pre-freeze-certain outcome, a good use of process?

**Both directions, then a verdict.**

*For running it:* The DATA-UNAVAILABLE-BLOCKED outcome on real data was
correctly predicted at pre-freeze with high confidence, but "correctly
predicted" is not the same as "already established as an archived,
independently-verified fact" — the campaign's own standing discipline
(GD-6, GD-8, GD-9 themselves) is precisely that a prediction must still be
checked against the actual code and actual run artifacts before being
trusted, because GD-8 and GD-9 were both cases where a plausible-sounding
prior belief ("the filter is applied," "the control can fail") turned out
false only once someone read the code and data directly. Skipping the
Executor/Validator/Red-Team cycle here would have meant taking
`specification_v3.yaml`'s own worked check on faith, which is exactly the
posture that let GD-8/GD-9 survive three prior batches. The cycle also cost
essentially nothing: measured wall-clock 0.035s against a 300s budget, and
it is what *this Front 1 finding* itself was surfaced by — a lighter-weight
Coordinator-only calculation would have reproduced the arithmetic but would
not, on the pattern of this campaign's own history, have caught a bug in a
newly-written 130-line implementation file without an independent read.

*Against running it as a full three-role cycle:* The pre-freeze review had
already performed the one calculation that mattered (both arms, zero
survivors) at zero cost, before any code existed. Dispatching a full
Executor run, then an independent Validator and Red Team pass, to confirm an
outcome the campaign's own prior document called "essentially certain" is
a heavier process than the marginal uncertainty warranted, if the *only*
goal were confirming the DATA-UNAVAILABLE-BLOCKED arithmetic. That
arithmetic could have been re-verified by the Coordinator alone (as the
pre-freeze reviewer already did) without minting a new run id, execution
report, and independent-review pair.

**Verdict: justified, but not primarily for the reason the run package
claims.** The batch's value is concentrated in two things neither of which
required predicting the real-arm outcome in advance: (1) independently
confirming, against the *actual implemented code* rather than the draft
prose, that `trapped_exclusion_filter_v3` does what it says (a genuine,
non-trivial check — code and prose diverge often enough in this campaign's
own history, GD-8/GD-9/GD-6, that this is not a formality); and (2) this
review's own Front 1 finding, which would not exist without an independent
read of the actually-executed `reanalyze_v3.py`. The self-test's claimed
value — "the ONLY runtime evidence... that GD-9's fix actually works" — is
real for the reused library functions but overstated for
`c_null_label_comparison_v3` itself, per Front 1. Net: the cycle was worth
running, but its output should be read as "GD-8 fixed and validated; GD-9's
wrapper fixed in code and consistent with the spec's description, but not
yet runtime-validated by any test in this campaign" — a narrower claim than
what the artifacts currently state.

## Front 3 — What does the campaign actually know now, and is it correctly scoped?

- **(a) GD-8 is fixed in code, confirmed by direct reading and by
  independent re-derivation of the arithmetic.** `trapped_exclusion_filter_v3`
  (`reanalyze_v3.py` lines 79–134) applies the 0.5 threshold independently to
  each arm's own `greedy_trapped_fraction`, matches the spec's worked check
  to full float precision (re-verified directly against
  `RUN-SSIQ-a85692-b/raw-result.json`: real arm 0.8374/0.7222/0.8201/0.8511,
  null arm 0.8079/0.7037/0.7908/0.8478, all > 0.5), and `decision_rule_v3`'s
  new gate correctly does not reopen the already-passed Phase −1 gate. This
  is solid.
- **(b) GD-9 is fixed in code but validated ONLY on synthetic data — and,
  per Front 1, even that synthetic validation does not reach the function
  itself.** The correct, narrower statement any successor record must carry:
  *`c_null_label_comparison_v3`'s algorithmic description matches the spec
  and its `NOT-EVALUABLE` path is confirmed correct on real data (0 < 3
  survivors, correctly reported, never defaulted); its fit-and-bootstrap
  branch has not been runtime-validated by any test executed in this
  campaign to date* — not "GD-9 is fixed" unqualified, and not "the
  synthetic self-test validates the branch," both of which overstate what
  Front 1 shows was actually exercised.
- **(c) Universal trapping across both arms is a real, if weakly-powered,
  observation about lever L4 itself, and it is already substantively
  surfaced but not statistically caveated.** All 8 values (4 primes × 2
  arms) exceed 0.5, and the null arm's numbers track the real arm's closely
  (e.g. prime 3889: 0.7222 vs 0.7037) — independently re-checked here. This
  is consistent with, and is the kind of evidence that would support,
  H-SSIQ-36e970's own mechanism-section framing that trapping may be a
  property of graph topology/greedy-descent dynamics at this N, not of
  delta_E-label quality — a genuine (if informal) null-object observation in
  the spirit of `docs/inventor-protocol.md` §3: the null arm reproduces
  qualitatively similar behavior to the real arm under a broken
  label↔vertex correspondence. But I checked whether trapped_fraction trends
  with N across the only four data points available (N=203→0.837,
  N=324→0.722, N=478→0.820, N=611→0.851) and found **no monotonic trend** —
  it dips at N=324 and rises again, not a decay curve. At n=4 this is far
  too small a sample to conclude trapping is N-invariant, but it is also not
  supportive of "trapping decreases with N" as an assumption for planning
  BATCH-007's next step. This specific non-monotonicity, and the n=4 sample
  size, should be stated explicitly in any evidence record that cites the
  universal-trapping observation as informative about L4 — it currently is
  not.

## Front 4 — Cheapest, most valuable BATCH-007 action, ranked

Ranked by the same standard `RT-BATCH-004.md`/`RT-BATCH-005.md` used:
cheapest and zero-new-compute first.

1. **[HIGHEST, ZERO NEW COMPUTE] Close Front 1's gap: build a synthetic
   self-test that actually calls `c_null_label_comparison_v3`.** Construct
   synthetic `real_per_prime`/`null_per_prime` dicts shaped exactly like the
   real data schema (real arm carries `N`; null arm does not), a
   `null_survivors` list, and exercise the function itself through *both*
   its branches: the `< min_primes` `NOT-EVALUABLE` path (already covered by
   real data, but not by synthetic data — worth confirming independently)
   and the `>= min_primes` fit-and-bootstrap path, with a hand-computable
   expected `m_gap_null`. This is a few more lines against already-imported
   functions, zero new search cost, and is what PF-1's own requirement
   actually needed — this batch built a test that satisfies PF-1's letter
   without its substance. Must happen before any future run's
   `c_null_label_control_failure` (true, false, or `NOT-EVALUABLE`) is cited
   as validated machinery.
2. **[HIGH, ZERO NEW COMPUTE] Investigate the mechanism behind pervasive
   trapping**, using already-collected graph/vertex/degree-sequence data
   from `RUN-SSIQ-a85692-b` (no new delta_E search, no new graph
   construction): is trapping concentrated on specific low-degree vertices,
   correlated with a graph-structural property independent of N, or an
   artifact of the greedy tie-break rule itself? Front 3(c)'s finding that
   trapped_fraction does *not* monotonically decrease across the four
   already-tested N values (203–611) argues for doing this diagnostic
   *before* spending real search budget on larger N under an unexamined
   assumption that bigger graphs trap less.
3. **[MEDIUM, COSTED, CONDITIONAL] Widen to larger primes/N only if (2)
   gives a specific reason to expect different behavior at larger N.**
   Costed against `real_execution_budget_v2`'s aggregate-counter mechanism
   (already validated working, `EV-SSIQ-f3ce32` O-1/O-2); premature before
   (2), per Front 3(c)'s non-monotonicity finding — spending new search
   budget on an untested assumption repeats the shape of exactly the kind of
   uncosted-precompute decision this campaign's own discipline (GD-4)
   exists to prevent.
4. **[NOT YET — do not close L4] Do not retire lever L4 as exhausted.**
   Zero survivors at N in [203, 611] across 4–5 primes is a coverage gap at
   toy scale, not a named obstruction with an argument (`docs/
   inventor-protocol.md` §4's closure standard); `goal.yaml` itself still
   ranks L4 highest-priority and open. A closure here would be exactly the
   kind of "count of screened-and-rejected... a fatigue report about the
   search" the protocol warns against, not a statement about the problem.
   Revisit condition: items 1–2 completed, and either (2) identifies a
   fixable mechanism or (3) is run at larger N with a specific hypothesis
   about why trapping should differ.

## Front 5 — Other checks

- **`compute_delta_e_v2.py`'s search code never invoked: accurate.**
  Confirmed by direct grep of `reanalyze_v3.py`: the string
  `compute_delta_e_v2` never appears in the file, and the only imports are
  `compute_delta_e` (v1, for `apply_decision_rule`/`SEEDS`) and
  `descent_hitting_time` (for `ols_loglog_fit`/`bootstrap_gap_ci`). No
  search, smoke-test, admission, or Phase −1 machinery is reachable from
  this file. The diff-list's claim on this point holds.
- **`apply_decision_rule`'s non-invocation: correctly disclosed, no silent
  invocation found.** `grep -n apply_decision_rule` on `reanalyze_v3.py`
  shows exactly one call site (line 502), inside the `>= 4`-real-arm-
  survivors `else` branch of `main()`'s gate check — the branch this run's
  actual data (0 survivors) never enters. `apply_decision_rule_invoked` is
  correctly recorded as `false` in `raw-result.json`, and
  `execution_report.yaml` discloses this explicitly rather than glossing it
  as "used." No discrepancy found.
- **Overclaim audit on the synthetic-only-validated fix plus the
  expected-and-realized null result:** the single, load-bearing overclaim
  is Front 1's — `execution_report.yaml` OBS-4 states the self-test "is the
  ONLY runtime evidence this batch supplies that `c_null_label_comparison_v3`'s
  fit-and-bootstrap branch works correctly" and `manifest.yaml`'s
  `validity_reason` repeats this near-verbatim; both should be read with
  Front 1's correction attached. Everything else in the run package is
  scoped honestly: `decision.reason`, `descent_metrics_v3.ran: false`, and
  the certificate block (`kind: none`) make no claim beyond what the data
  supports, and the Coordinator's own precommit checks
  (`synthetic_self_test_disclosure`, `diff_list_cross_check`) correctly
  flagged both areas `FLAGGED_FOR_INDEPENDENT_REVIEW` rather than silently
  endorsing them — good practice that this review's Front 1 finding
  directly answers.

---

## Objections

1. **[Front 1, HIGH, NEW FINDING] `run_synthetic_self_test_v3` never calls
   `c_null_label_comparison_v3` — it calls the underlying, already-validated
   `dht.ols_loglog_fit`/`dht.bootstrap_gap_ci` directly and reimplements the
   comparison rule inline, bypassing the actual GD-9 fix entirely.**
   Confirmed by direct reading of `reanalyze_v3.py`: `c_null_label_comparison_v3`
   (lines 141–216) has exactly one call site (line 415, the unreached
   real-data path); `run_synthetic_self_test_v3` (lines 223–356) independently
   calls `dht.ols_loglog_fit`/`dht.bootstrap_gap_ci` (lines 242–243,
   248–249) and recomputes `synthetic_control_failure` with a hand-written
   copy of the comparison expression (line 272), never invoking
   `c_null_label_comparison_v3`. A version of `c_null_label_comparison_v3`
   with a bug in its cross-dict indexing (independently confirmed load-bearing:
   `c_null_label.per_prime` has no `N` field, checked directly against
   `RUN-SSIQ-a85692-b/raw-result.json`), its `min_primes` gate, or its
   `sorted()`/zip ordering would pass this self-test unchanged. This
   contradicts the claim, repeated in `raw-result.json`,
   `execution_report.yaml` OBS-4, and `manifest.yaml`'s `validity_reason`,
   that the self-test is runtime evidence the fit-and-bootstrap branch
   "works correctly" — it is runtime evidence that `ols_loglog_fit`/
   `bootstrap_gap_ci` (already independently validated, `EV-SSIQ-f3ce32`
   O-1/O-2) still work, and that a hand-copied restatement of one comparison
   rule behaves as expected. It is not evidence about the wrapper function
   GD-9's fix actually adds.
2. **[Front 3(c), MEDIUM] The universal-trapping observation is genuinely
   informative about lever L4's mechanism but is stated without its
   sample-size and non-monotonicity caveats.** At n=4 primes, trapped_fraction
   does not trend monotonically with N (203→0.837, 324→0.722, 478→0.820,
   611→0.851, independently re-derived here) — this argues against assuming
   "bigger N traps less" when planning any widening, and should be stated
   explicitly in the evidence record rather than left implicit in
   `H-SSIQ-36e970`'s general mechanism-section framing.
3. **[Front 2, informational, not blocking] The batch's own framing of "this
   establishes GD-9's fix works" is broader than what Front 1 shows the
   batch actually established.** The process overhead was justified overall
   (see Front 2), but the marginal value delivered by the self-test
   specifically is smaller than claimed, and the successor record should say
   so rather than repeat the run package's framing.

## Required controls

- A second synthetic self-test that calls `c_null_label_comparison_v3`
  itself (not `dht.ols_loglog_fit`/`bootstrap_gap_ci` directly), through
  synthetic `real_per_prime`/`null_per_prime` dict inputs matching the real
  data schema (null arm carries no `N` field), exercising both the
  `NOT-EVALUABLE` and fit-and-bootstrap branches through the actual function
  call — required before any future run's `c_null_label_control_failure`
  output is cited as validated (Objection 1).
- An explicit statement of the n=4, non-monotonic trapped_fraction-vs-N
  finding wherever the universal-trapping observation is cited as informative
  about lever L4, so it is not read as stronger evidence than four points
  support (Objection 2).
- A correction to `execution_report.yaml` OBS-4 / `manifest.yaml`
  `validity_reason`'s framing of what the synthetic self-test validates, in
  any successor record that cites this batch (Objection 1).

## Counterexample or mutation

The cheapest discriminating check for Objection 1 is exactly the one
performed above at zero new compute: `grep -n "c_null_label_comparison_v3("
experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py` returns exactly
two lines — the `def` (line 141) and the one call site inside `main()`'s
unreached real-data branch (line 415) — confirming
`run_synthetic_self_test_v3` never calls it. A mutation that makes this
concrete: replace `c_null_label_comparison_v3`'s line 182
(`greedy_medians = [null_per_prime[p]["greedy_median"] for p in ordered]`)
with `real_per_prime[p]["greedy_median"]` (a plausible copy-paste bug, since
`real_per_prime` is already in scope and both dicts share the same key
shape for this field) — every check in `synthetic_self_test.json` still
reports `PASS`, because the self-test never constructs `real_per_prime`/
`null_per_prime` dicts or calls the mutated function at all. This is a
direct falsifier of "the self-test would catch a bug in the fix it exists to
validate."

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — toy-scale
gradient-existence screen, `asymptotic_claim: null` throughout, correctly
inherited and not questioned by anything in this batch. The relevant
baseline is this campaign's own instrument- and fix-scrutiny discipline
(GD-4 through GD-9): this batch cleanly clears that bar for GD-8 (direct
code reading confirms the fix and its arithmetic) and clears the *letter* of
GD-9's own standing repair (a required synthetic self-test was built and
executed) but not its *substance* — the test that discipline requires exists,
runs, and reports PASS, without ever calling the function under review. This
is the identical failure mode GD-9 itself named ("a control can execute,
populate a report, and never actually compute the comparison its own
failure_consequence promises"), now recurring one layer up, inside the
artifact built specifically to prevent it.

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim).
No numbered heuristic requiring a random-model justification is implicated
by any finding in this review.

## Cost model challenges

No asymptotic-cost claim is made (`asymptotic_claim: null`, correctly); the
per-attempt × inverse-success-probability review does not apply. The 300s
budget was generously oversized (measured 0.035s) — no resource-bookkeeping
defect. The live concern is again evidentiary, not resource cost: the batch
spent (trivial) compute on a self-test that, by its own construction, cannot
exercise the code path it is required to validate.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears
anywhere in this amendment or its inherited hypothesis. `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) is correctly stated and not exceeded. No scope-inflation
found. Front 4's recommendation to keep lever L4 open, not close it, is
itself a scope-discipline point: the current evidence (zero survivors at toy
scale, n=4) does not rise to a named obstruction and must not be read as
closing L4.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — a direct instrument-level gradient-existence
screen, not a proof-oriented proposal. Attacked and held, same verdict as
every prior review in this lineage.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-c` as committed at `cc786884`: `trapped_exclusion_filter_v3`
(GD-8's fix) is correctly implemented and independently confirmed against
both real and null arm data to full float precision; `decision_rule_v3`'s new
gate correctly fires DATA-UNAVAILABLE-BLOCKED without reopening the
already-passed Phase −1 gate; `apply_decision_rule`'s non-invocation and
`compute_delta_e_v2.py`'s non-invocation are both accurately disclosed with
no discrepancy found. `c_null_label_comparison_v3` (GD-9's fix) is
implemented in code consistent with the spec's description and correctly
returns `NOT-EVALUABLE` on this run's real data, never defaulted — **but the
required synthetic self-test does not call this function**, so its
fit-and-bootstrap branch has **no direct runtime validation from this batch
or any prior one**; the self-test's actual, demonstrated content is that
`ols_loglog_fit`/`bootstrap_gap_ci` (already independently validated) still
work, plus a hand-written restatement of one comparison expression. Any
successor record must state GD-9's status as "fixed in code, consistent
with spec, `NOT-EVALUABLE` path confirmed on real data; fit-and-bootstrap
branch not yet runtime-validated by any executed test" — not "GD-9's fix
works" or "validated by the synthetic self-test" without qualification. The
universal-trapping observation (0/4 primes survive in both arms) is a
genuine, disclosed, informative result about lever L4, but the four
available data points show no monotonic trend with N and this should be
stated wherever the observation is cited.

## Next concrete action

Coordinator: before citing this batch's GD-9 fix as validated in any
successor evidence or decision record, require a second synthetic self-test
that calls `c_null_label_comparison_v3` itself (not the underlying
`dht.*` functions directly), through synthetic `real_per_prime`/
`null_per_prime` dict inputs shaped like the real data schema, exercising
both its `NOT-EVALUABLE` and fit-and-bootstrap branches — zero new search
cost, per this campaign's own standing practice. Independently of that fix,
open BATCH-007 with Front 4's ranked plan: (1) the corrected self-test
above; (2) a zero-new-compute mechanism investigation of why greedy descent
traps pervasively in both arms at N in [203, 611], using already-collected
graph/vertex data; (3) only then, and only if (2) gives a specific reason to
expect different behavior, widen to larger N/primes, costed against the
already-validated aggregate-budget mechanism; do not retire lever L4 as
exhausted at this toy scale.

## Overall verdict

**CHALLENGE.** The run executed honestly, GD-8's fix is sound and
independently confirmed, and DATA-UNAVAILABLE-BLOCKED is the mechanically
correct, pre-disclosed terminal label. But the batch's own required
mechanism for validating GD-9's fix — the synthetic self-test — does not
call the function it exists to validate, so GD-9's fit-and-bootstrap branch
remains, in substance though not in the run package's stated framing, in the
same unvalidated state PF-1 originally found it in. This is not a repeat of
GD-9 itself (no hard-coded flag), and it does not overturn
DATA-UNAVAILABLE-BLOCKED as this run's correct terminal label, but it means
"GD-9's fix works" is not yet a supported claim and must not be carried
forward as one.

```yaml
red_team_report:
  id: RT-BATCH-006
  task_id: TASK-20260805-176dab
  claim_under_review: >-
    RUN-SSIQ-a85692-c (experiments/EXP-SSIQ-a85692, specification_v3.yaml,
    hypothesis H-SSIQ-36e970): a pure re-analysis of RUN-SSIQ-a85692-b's
    already-collected data implementing trapped_exclusion_filter_v3 (GD-8's
    fix) and c_null_label_comparison_v3 (GD-9's fix), with a required
    synthetic self-test as the only runtime evidence for GD-9's substantive
    new branch, terminating in DATA-UNAVAILABLE-BLOCKED.
  objections:
    - "OBJ-1 [Front 1, HIGH, NEW FINDING]: run_synthetic_self_test_v3 (reanalyze_v3.py lines 223-356) never calls c_null_label_comparison_v3 (lines 141-216, one call site at line 415, in the unreached real-data branch). The self-test invokes dht.ols_loglog_fit/dht.bootstrap_gap_ci directly on hand-constructed lists and reimplements the comparison rule inline (line 272: synthetic_control_failure = bool(lo is not None and lo > 0.0)) rather than calling the function under review. ols_loglog_fit/bootstrap_gap_ci already had independent runtime evidence of correctness from RUN-SSIQ-a85692-b's own real-arm fit (EV-SSIQ-f3ce32 O-1/O-2). A version of c_null_label_comparison_v3 with a bug in its cross-dict indexing (independently confirmed load-bearing: c_null_label.per_prime carries no N field, checked directly against raw-result.json), its min_primes gate, or its sort/zip ordering would pass this self-test unchanged, since the self-test never constructs real_per_prime/null_per_prime dicts or calls that function. This contradicts raw-result.json, execution_report.yaml OBS-4, and manifest.yaml's validity_reason, all of which state or imply the self-test is runtime evidence the fit-and-bootstrap branch 'works correctly.'"
    - "OBJ-2 [Front 3(c), MEDIUM]: the universal-trapping observation (0/4 primes survive trapped_exclusion_filter_v3 in both real and null arms) is genuinely informative about lever L4's mechanism, but the four available data points show NO monotonic trend of trapped_fraction with N (N=203->0.837, N=324->0.722, N=478->0.820, N=611->0.851, independently re-derived here) -- this argues against assuming 'bigger N traps less' when planning a widening, and is not currently stated as a caveat anywhere the observation is cited."
    - "OBJ-3 [Front 2, informational, not blocking]: the run package's framing overstates what was established -- 'GD-9's fix works, validated by the synthetic self-test' is broader than OBJ-1 shows was actually demonstrated. The process overhead of running the full batch was net justified (it surfaced OBJ-1, which a lighter Coordinator-only arithmetic check would not have), but the self-test's specific marginal contribution is smaller than the artifacts claim."
  required_controls:
    - "A second synthetic self-test that calls c_null_label_comparison_v3 itself (not dht.ols_loglog_fit/bootstrap_gap_ci directly), via synthetic real_per_prime/null_per_prime dict inputs matching the real data schema (null arm carries no N field), exercising both the NOT-EVALUABLE and fit-and-bootstrap branches through the actual function call -- required before any future run's c_null_label_control_failure output is cited as validated (OBJ-1)."
    - "Explicit statement of the n=4, non-monotonic trapped_fraction-vs-N finding wherever the universal-trapping observation is cited as informative about lever L4 (OBJ-2)."
    - "Correction to execution_report.yaml OBS-4 / manifest.yaml validity_reason's framing of what the synthetic self-test validates, in any successor record citing this batch (OBJ-1/OBJ-3)."
  counterexample_or_mutation: >-
    grep -n "c_null_label_comparison_v3(" experiments/EXP-SSIQ-a85692/implementation/reanalyze_v3.py
    returns exactly two lines: the def (line 141) and the one call site
    inside main()'s unreached real-data branch (line 415) -- confirming
    run_synthetic_self_test_v3 never calls it. Concrete mutation: replace
    c_null_label_comparison_v3's line 182
    (greedy_medians = [null_per_prime[p]["greedy_median"] for p in ordered])
    with real_per_prime[p]["greedy_median"] (a plausible copy-paste bug,
    since real_per_prime is already in scope with the same key shape for
    this field) -- every check in synthetic_self_test.json still reports
    PASS, because the self-test never constructs real_per_prime/null_per_prime
    dicts or invokes the mutated function at all. Direct falsifier of "the
    self-test would catch a bug in the fix it exists to validate."
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-9): this batch
    clears that bar for GD-8 cleanly, and clears the LETTER of GD-9's own
    standing repair (a required synthetic self-test exists and runs) but not
    its SUBSTANCE -- the test never calls the function under review. This is
    the identical failure mode GD-9 itself named ("a control can execute,
    populate a report, and never actually compute the comparison its own
    failure_consequence promises"), recurring one layer up, inside the
    artifact built specifically to prevent it.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. No finding here implicates a numbered heuristic."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply."
    - "The 300s budget was generously oversized (measured wall-clock 0.035s) -- no resource-bookkeeping defect."
    - "The live concern is evidentiary, not resource cost: compute was spent on a self-test that, by construction, cannot exercise the code path (c_null_label_comparison_v3's own wiring) it is required to validate."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "Front 4's recommendation to keep lever L4 OPEN (not closed) is a scope-discipline point: zero survivors at n=4 toy-scale primes is a coverage gap, not a named obstruction under docs/inventor-protocol.md section 4's closure standard, and must not be read as closing L4."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-c as committed at cc786884: trapped_exclusion_filter_v3
    (GD-8's fix) is correctly implemented and independently confirmed to
    full float precision against both arms; decision_rule_v3's new gate
    correctly fires DATA-UNAVAILABLE-BLOCKED without reopening the Phase -1
    gate; apply_decision_rule's and compute_delta_e_v2.py's non-invocation
    are accurately disclosed with no discrepancy found. c_null_label_comparison_v3
    (GD-9's fix) is implemented in code consistent with the spec and
    correctly returns NOT-EVALUABLE on real data, never defaulted -- but the
    required synthetic self-test does not call this function, so its
    fit-and-bootstrap branch has NO direct runtime validation from this
    batch or any prior one; the self-test's demonstrated content is that
    ols_loglog_fit/bootstrap_gap_ci (already validated) still work, plus a
    hand-written restatement of one comparison expression. Any successor
    record must state GD-9's status as "fixed in code, consistent with
    spec, NOT-EVALUABLE path confirmed on real data; fit-and-bootstrap
    branch not yet runtime-validated" -- not "GD-9's fix works" or
    "validated by the synthetic self-test" unqualified. The universal-trapping
    observation is genuine and informative but the four available points
    show no monotonic trend with N; this caveat is currently missing
    wherever the observation is cited.
  next_concrete_action: >-
    Coordinator: before citing this batch's GD-9 fix as validated in any
    successor evidence or decision record, require a second synthetic
    self-test that calls c_null_label_comparison_v3 itself through synthetic
    real_per_prime/null_per_prime dict inputs shaped like the real schema,
    exercising both its NOT-EVALUABLE and fit-and-bootstrap branches --
    zero new search cost. Open BATCH-007 with Front 4's ranked plan: (1)
    the corrected self-test; (2) a zero-new-compute mechanism investigation
    of pervasive trapping using already-collected graph/vertex data; (3)
    only then, conditional on (2)'s findings, widen to larger N/primes,
    costed against the already-validated aggregate-budget mechanism; do not
    retire lever L4 as exhausted at this toy scale.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/RT-BATCH-006.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic only: independent re-derivation of trapped_exclusion_filter_v3's
    survivor set for both arms from RUN-SSIQ-a85692-b/raw-result.json;
    direct schema check of descent_metrics.per_prime vs c_null_label.per_prime
    field sets (python3, read-only); independent re-check of trapped_fraction
    vs N monotonicity across the four contributing primes. Plus direct
    reading (not executing) of reanalyze_v3.py, specification_v2.yaml,
    specification_v3.yaml, RT-PREFREEZE-EXP-SSIQ-a85692-v3.md, the full
    RUN-SSIQ-a85692-c package, the archive receipt, goal.yaml, EV-SSIQ-f3ce32.yaml,
    DEC-20260805-5f5ac6.yaml, H-SSIQ-36e970.yaml, and RT-BATCH-005.md in
    full. No code executed, no graph built, no search run, no new
    measurement taken beyond read-only arithmetic on already-committed
    numbers.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is
    not durable until that archive exists. Per write_scope, this task
    modified nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/RT-BATCH-006.md
    -- experiments/EXP-SSIQ-a85692/ and every ledger record are untouched.
  verdict: CHALLENGE
```
