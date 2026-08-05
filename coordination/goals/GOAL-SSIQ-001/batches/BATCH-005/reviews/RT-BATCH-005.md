# RT-BATCH-005 — Red Team review of RUN-SSIQ-a85692-b (EXP-SSIQ-a85692 v2,
# H-SSIQ-137200), GOAL-SSIQ-001 BATCH-005

**Reviews the Coordinator-committed snapshot at commit `06af9596`** (parent
`14b56525`), receipt
`coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/archives/TASK-20260805-8bddd0-receipt.yaml`,
covering `experiments/EXP-SSIQ-a85692/{implementation/compute_delta_e_v2.py,
runs/RUN-SSIQ-a85692-b}/` under `specification_v2.yaml` (frozen `14b56525`)
only. Nothing below is drawn from, or asserted about, any working-tree-only
state. This report changes nothing under `experiments/EXP-SSIQ-a85692/`,
`experiments/EXP-SSIQ-58b642/`, or any ledger record — those remain the
Coordinator's alone to touch. All primary artifacts named in the launching
task were read in full: `specification.yaml` (v1), `specification_v2.yaml`,
`RT-PREFREEZE-EXP-SSIQ-a85692-v2.md`, `implementation/compute_delta_e_v2.py`
and, by necessity of tracing every function it imports by reference,
`implementation/compute_delta_e.py` (v1) and
`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py` in full
— not sampled — plus every RUN-SSIQ-a85692-b artifact (`manifest.yaml`,
`raw-result.json`, `execution_report.yaml`, `source_access_log.yaml`,
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`attempt1-infra-killed.stdout.log`), the archive receipt, `goal.yaml`'s GD-4
through GD-7 entries, `EV-SSIQ-94de20.yaml`, `DEC-20260805-a4e04e.yaml`, and
`RT-BATCH-004.md` in full.

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
    unprobeable (VAL/RT-BATCH-003, RT-PREFREEZE-EXP-SSIQ-a85692[-v2],
    RT-BATCH-004), so this is recorded as the standing condition, not
    re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    is not corroboration from a distinct model and does not upgrade the
    campaign's evidence tier by itself. A Validator (TASK-20260805-10868f) is
    reviewing the same run independently and in parallel; this report was
    produced without coordinating with it and stands alone.
```

---

## Bottom line up front

Two of the five fronts this review was asked to attack hold up cleanly on
direct code inspection: **`real_execution_budget_v2` (PF-1's fix) is sound
and does exactly what it claims — no leftover `T_PRIME`, no reintroduced
per-prime sub-cap, no timing leakage from earlier phases, and the aggregate
counter's own arithmetic reproduces to the millisecond from the run's own
logged numbers.** The `required_artifacts_note` diff-list cross-check is
also accurate against the actual code, function by function.

**But the run's terminal label needs a materially narrower reading than the
receipt gives it, for two reasons the receipt does not surface, one of which
is a genuinely new, previously undisclosed defect.**

1. **`CONTROL-FAILURE-VOID` is the mechanically correct output of the frozen
   decision rule, but the specific control that fired it (C-SEARCH-BIAS) has
   a statistical-power problem that makes "comparable magnitude" here closer
   to "the test had nothing to say" than to "contamination confirmed."** At
   n=20 samples, a Pearson correlation needs |r| ≳ 0.44 to be
   distinguishable from noise; both reported correlations (0.0961, 0.0308)
   are far below that. The comparability rule's own two clauses actually
   *disagree* on this data: the ratio clause (`|corr_rand| >= 0.5 *
   |corr_true|`) says **NOT comparable** (0.0308 < 0.5×0.0961 = 0.0481 —
   the random-target correlation is roughly a third of the true-target
   one), and only the absolute-floor clause (`both < 0.1`) fires. That
   absolute floor was never itself pinned in the frozen contract text
   (`specification.yaml`/`specification_v2.yaml` say only "comparable in
   magnitude," no number) — it is an implementation-time choice made inside
   `compute_delta_e.py`, whose own comment concedes it is "reported... which
   the Coordinator/Validator can re-judge independently of this specific
   threshold." No pre-freeze review of either version ever re-judged it.
2. **NEW FINDING (not in PD-1/PD-2/PD-3, not flagged by the Coordinator's
   own `FLAGGED_FOR_INDEPENDENT_REVIEW` items, not caught by any
   pre-freeze review): C-NULL-LABEL — the *other* control the decision
   branch's own reason string cites ("C-SEARCH-BIAS, C-NULL-LABEL, or
   C-CONNECTIVITY failed") — cannot structurally ever fail.**
   `c_null_label_control_failure` is hard-coded `False` in both v1's
   `compute_delta_e.py` (lines 776–818, 874) and v2's reproduction of the
   identical inline logic (`compute_delta_e_v2.py` lines 664–701, 773). The
   block computes per-prime shuffled-label greedy/random medians but never
   fits a null M-GAP across primes, never bootstraps its CI, and never
   compares it to the real arm's CI — so no code path can ever set that
   flag `True`. For *this* run it is moot (C-SEARCH-BIAS already fires
   first), but it means the "required, not optional" null-object control
   the frozen spec relies on to catch a genuine delta_E-gradient
   masquerading as a graph-topology artifact is **dead code**, unable to
   veto a future `DETECTED` outcome under this same, reused orchestration.
3. **PD-2 (the trapped_fraction-exclusion gap) is independently confirmed
   against the actual code and is not moot merely because
   `CONTROL-FAILURE-VOID` already voids the run** — see Front 3.

None of this overturns the run's honesty or its mechanical fidelity to the
frozen v2 contract text as written; every number I re-derived matches. The
challenge is to what the terminal label licenses a reader to conclude, and
to two control-logic gaps this run is the first to make visible.

---

## FRONT 1 — Does `real_execution_budget_v2` actually do what PF-1 specifies,
## with no new defect of the same shape?

**Verdict: sound. Checked by direct code inspection, not by trusting the
manifest's prose.**

`compute_delta_e_v2.py` line 126: `T_RESERVED = 0.5 * WALL_CLOCK_BUDGET_SECONDS`
(3600.0s), and `grep`ing the entire file for `T_PRIME`, `t_prime`, `300`, or
`len(PRIMES)` in a divisor position returns nothing live — every hit is
inside a comment explaining what was *replaced*. The rewritten
`run_phase_minus1_on_confirmatory_set` (lines 212–296) takes
`aggregate_budget_seconds` as its sole budget parameter (no default that
could silently reintroduce a per-prime share), initializes
`remaining = float(aggregate_budget_seconds)` fresh on each call, and is
called exactly once for the confirmatory prefix (`T_RESERVED`) and once per
widening-extension prime (the just-returned `remaining`, threaded onward) —
`main()` lines 568–570, 610–611. No prime receives an individual sub-budget
anywhere in the file.

**Start-point / leakage check (explicitly asked for in the task):** the
counter starts at exactly `T_RESERVED = 3600.0` when
`run_phase_minus1_on_confirmatory_set` is first called — *after* Phase 0,
modular-polynomial verification, graph reuse, the two-point smoke test,
C-SEARCH-BIAS, and C-BOUND-CHECK have already run and consumed their own,
separately-measured wall-clock (≈95.4s per `budget_split_seconds`: 0.064 +
0.170 + 27.779 + 10.118 + 57.286s). None of that preamble time is deducted
from `T_RESERVED` — there is no leakage in either direction. This matches
the frozen spec's stated split ("the 0.5 factor reserves the other half...
for Phase 0, graph reuse, and descent simulation").

**Arithmetic re-derivation, zero trust in the manifest's summary:** summing
`raw-result.json.phase_minus1_real_search`'s own `wall_seconds_used` across
the five admitted primes — 284.884 + 474.842 + 817.950 + 947.691 + 1074.705
= **3600.072s** — matches `real_execution_budget_v2.aggregate_seconds_spent_confirmatory
= 3600.0714724063873` to five significant figures (the 0.001s residual is
loop/measurement overhead, immaterial). `M-COVERAGE` per prime
(194/194, 306/306, 460/460, 594/594, 554/718 = 0.77159) matches the reported
fractions exactly. **PF-1's own pre-freeze prediction — "at most ~2 of 4
admitted primes could clear `M-COVERAGE >= 0.5`" under the *unfixed* cap —
is directly falsified by this run under the *fixed* mechanism: all 5
admitted primes clear it (4 fully, 1 at 77%).** This is the single cleanest,
most fully-validated part of this run.

**One genuine, minor imprecision, not blocking:** `main()`'s log line and
`payload["c_null_label"]`'s comment both describe the usable set feeding
C-NULL-LABEL and descent-metrics as "n=5" (`[2437, 3889, 5737, 7333, 8893]`,
i.e. `usable_primes_for_fit` in the raw JSON), but 8893 is skipped inside
both loops (`len(delta_map) != len(vertices)`) because its coverage is
partial — the actual fit uses n=4. This is disclosed correctly in the
*numeric* fields (`n_primes_used: 4`, `C_NULL_LABEL_n_primes_usable: 4`) but
the *log/field naming* ("usable_primes_for_fit" including a prime that is
not, in fact, used in the fit) is misleading on a quick read. Cosmetic, not
a validity concern.

---

## FRONT 2 — Is `CONTROL-FAILURE-VOID` the correct terminal label, and does
## it mean what the receipt implies?

**The mechanical application is correct. The evidentiary reading is not
fully supported, for two independent reasons — one a design gap in the
control's own statistics, one a newly found defect in the *other* control
this branch's reason text cites.**

### 2a. `apply_decision_rule`'s ordering, re-derived independently

`compute_delta_e.py` lines 549–581 (imported unchanged into v2): the branch
order is `phase0_pass` → `phase_minus1_gate_pass` → `(c_search_bias_control_failure
or c_null_label_control_failure or not c_connectivity_all_pass)` → CI sign.
With `phase0_pass=True`, `phase_minus1_gate_pass=True`, and
`c_search_bias_control_failure=True` (from `magnitudes_comparable_flag`),
the control-failure branch fires and returns before the CI is ever
inspected — **confirmed independently against the code, matching the
manifest's own claim exactly.** The wide, positive-leaning bootstrap CI
`[-0.4077, 1.3256]` is genuinely irrelevant to this run's terminal branch;
nothing in `manifest.yaml`, `execution_report.yaml`, or the receipt spins it
as suggestive, and I found no artifact in this run overclaiming it (see
Front 5).

### 2b. C-SEARCH-BIAS's comparability test has a real power problem

`pearson_corr`/`run_c_search_bias` (`compute_delta_e.py` lines 426–507) uses
`comparable = |corr_rand| >= 0.5*max(|corr_true|, eps) OR (|corr_true| < 0.1
AND |corr_rand| < 0.1)`. Applied to this run's numbers (`corr_true =
0.09611`, `corr_rand = 0.03083`):

- Ratio clause: `0.5 * 0.09611 = 0.04805`; `0.03083 < 0.04805` → **ratio
  clause says NOT comparable** (random-target correlation is about a third
  of the true-target one).
- Absolute-floor clause: both `< 0.1` → **fires, and is the sole reason
  `magnitudes_comparable_flag = True`.**

At n=20, the standard error of a Pearson r near 0 is ≈ 1/√(n−3) ≈ 0.243,
and the conventional two-tailed significance threshold at α=0.05 is roughly
|r| > 0.44 (RT-BATCH-004 objection 4 already computed this for the same
instrument at the same sample size). **Both correlations here are far below
that threshold — both are statistically indistinguishable from zero, and
therefore also from each other, independent of whether real
search-construction-order contamination exists.** The absolute-floor clause
will fire whenever the true-target correlation itself is weak, which is the
*generic* expected outcome for this instrument at toy scale and n=20 —
making `magnitudes_comparable_flag=True` a near-certainty at this sample
size regardless of the underlying mechanism, not specific evidence that the
random-target and true-target searches are behaving the same way. This is
exactly the ambiguity RT-BATCH-004 objection 4 flagged as an open question
("this diagnostic should be re-examined... once a real M-GAP exists") —
**now that real numbers exist, the answer is: the test as specified cannot
distinguish "no detectable relationship in either arm" (weak power) from
"genuine construction-order contamination" (the thing it was built to
catch).** Nothing in this run's own reporting states this distinction; the
manifest and receipt both present `magnitudes_comparable_flag=true` as a
clean control failure without qualifying its statistical power.

**This cuts toward a possible false control-failure, not a false pass**: the
comparability rule's own ratio clause, on its own, would have called this
"not comparable" — it is only the looser, statistically uninformative
absolute floor that forces `CONTROL-FAILURE-VOID`. A reader should not treat
this as confirmed evidence that Algorithm 2's ascending-prime-order
construction is contaminating the real arm; it is equally consistent with
"the test lacked the power to tell," which is a different, and cheaper,
problem to fix (see Front 4).

### 2c. NEW FINDING — C-NULL-LABEL cannot fail; its control_failure flag is dead code

Reading `compute_delta_e.py`'s C-NULL-LABEL block (lines 772–818, reproduced
identically in `compute_delta_e_v2.py` lines 646–701) end to end: it builds
`null_by_prime[p]` (a shuffled-multiset `greedy_median`,
`greedy_trapped_fraction`, `random_median` per usable prime) and sets
`c_null_label_report = {"ran": True, "per_prime": null_by_prime}` — but
**`c_null_label_control_failure` is initialized `False` at the top of the
block and is never reassigned anywhere in either file.** There is no OLS
fit of the null medians across primes, no `m_gap_null`, no bootstrap CI on
it, and no comparison against the real arm's CI — the machinery that exists
for exactly this purpose in the *sibling* module
(`experiments/EXP-SSIQ-58b642/implementation/descent_hitting_time.py`'s own
`run_null_arm`/`m_gap_null`, lines 546–585, built for BATCH-003's
WISDE-based null arm) is present in the codebase but is not the code path
`compute_delta_e.py`'s C-NULL-LABEL uses, and no equivalent was built for
the shuffle-based control. `grep -n c_null_label_control_failure` across
both implementation files shows exactly two occurrences each: the
initialization (`= False`) and the pass-through into `apply_decision_rule`
— nothing in between ever writes to it.

**Consequence:** `outcome_scope_label_glossary`'s `CONTROL-FAILURE-VOID`
branch and its own `apply_decision_rule` reason string both name
C-NULL-LABEL as a control whose failure can void a real M-GAP — but under
the code as actually written and executed, **C-NULL-LABEL structurally
cannot ever produce that outcome.** For `RUN-SSIQ-a85692-b` this is moot in
the narrow sense that C-SEARCH-BIAS already fires the same branch first —
but it is *not* moot for the campaign: this is the first run in the
project's history to reach this code path with a real, non-empty delta_E
multiset (`phase_minus1_gate_pass=True` for the first time ever), so it is
the first opportunity anyone has had to notice that the "required, not
optional" null-object control this experiment relies on to distinguish a
genuine delta_E-gradient from a graph-topology/greedy-dynamics artifact is
inert. **A future run that clears C-SEARCH-BIAS (e.g. with a larger, more
powerful sample per Front 4) could report `DETECTED` with zero actual
protection from this specific null-object check**, despite the frozen
spec's own text asserting the opposite. This is a new, previously
undisclosed defect of the same species as GD-4 through GD-7 (a frozen/reused
element nobody stress-tested) but a different mechanism than any of them: it
is not a budget-arithmetic defect, it is a control whose comparison logic
was simply never written.

---

## FRONT 3 — PD-2 (PER-PRIME-TRAPPED-EXCLUSION never implemented):
## independently verified, and its disposition

**Confirmed against the code directly.** `compute_delta_e.py` line 846:
`usable_full = [p for p in per_prime]` — no filter of any kind on
`greedy_trapped_fraction`, despite `M-GAMMA-GREEDY`'s definition (inherited
unchanged from v1 into v2) stating "same trapped_fraction reporting and
exclusion threshold." `raw-result.json.descent_metrics.per_prime` reports,
for the four primes actually used in the fit: `2437: 0.8374`, `3889:
0.7222`, `5737: 0.8201`, `7333: 0.8511` — **all four exceed the 0.5
exclusion threshold**, confirmed against the run's own raw JSON, not merely
the executor's summary.

**Disposition: (a) and (b) both apply; (c) is rejected.**

- **(a) Warrants a new named defect.** Same species as GD-4/GD-5/GD-7 (a
  reused/frozen element nobody stress-tested), distinct mechanism (a gap
  between the frozen spec's *text* and the reused *code*'s actual behavior,
  first exercised — and therefore first material — in this run). I flag
  this, alongside Front 2c's C-NULL-LABEL dead-code finding, as warranting
  new goal-record defect entries (proposed `GD-8` for this front, `GD-9` for
  Front 2c, or the Coordinator may choose to file them as one combined entry
  since both are "reused inline orchestration silently missing logic the
  spec's own text requires" — the numbering is the Coordinator's call, not
  mine).
- **(b) Independently invalidates `gamma_greedy=0.23354` as a clean,
  spec-conformant `M-GAMMA-GREEDY` measurement, regardless of the
  `CONTROL-FAILURE-VOID` label.** `CONTROL-FAILURE-VOID` is a claim about
  search-order contamination (Front 2); it says nothing about whether the
  reported point estimate actually instantiates the frozen estimator's own
  definition. Under a *correctly* implemented exclusion filter, all four
  contributing primes would be dropped, `usable_full` would be empty, the
  `>= 4`-usable-primes floor `descent_metrics` itself requires would not be
  met, and `descent_metrics.ran` would be `False` — no `gamma_greedy`,
  `gamma_random`, or `m_gap` would exist to report at all. This is a
  *separate* invalidity from contamination: even in a hypothetical world
  where C-SEARCH-BIAS had passed cleanly, this run's own `M-GAMMA-GREEDY`
  number would still not be a valid instance of the frozen spec's estimator.
- **(c) Not moot.** `CONTROL-FAILURE-VOID` happens to make this run's
  specific numbers inert for *this run's* terminal decision, but the
  underlying code defect is not scoped to this run — it will recur
  identically in any future run that reuses this same inline orchestration,
  including one that clears C-SEARCH-BIAS. Treating PD-2 as moot here would
  let it go unfixed into a future run where it would matter for real.

---

## FRONT 4 — Given `CONTROL-FAILURE-VOID`, the cheapest, most valuable
## BATCH-006 action, ranked

Ranked by the same standard `RT-BATCH-004.md` used for BATCH-005: cheapest
first, zero-new-compute fixes before any new real search.

1. **[HIGHEST, ZERO NEW COMPUTE] Wire C-NULL-LABEL's actual comparison
   logic** (Front 2c). Fit a null M-GAP (OLS-log-log on the already-computed
   `null_by_prime` medians across primes, exactly mirroring the real arm's
   own fit), bootstrap its CI the same way `M-GAP`'s CI is bootstrapped, and
   set `c_null_label_control_failure` from a stated, pre-registered
   comparison rule (e.g., "null CI also excludes 0 in the positive
   direction" or an analogous magnitude-comparable rule to C-SEARCH-BIAS's,
   chosen and justified *before* looking at what it would output on
   already-collected data). This can be done entirely from
   `RUN-SSIQ-a85692-b`'s own already-computed `c_null_label.per_prime` data
   with **zero new search** — a pure code fix plus re-analysis of existing
   numbers. Must happen before any future run's `DETECTED` can be trusted at
   all, independent of anything else on this list.
2. **[HIGH, ZERO NEW COMPUTE FOR DIAGNOSIS] Implement
   PER-PRIME-TRAPPED-EXCLUSION** (Front 3) and re-derive what
   `descent_metrics` would report under it, using this run's own already-
   collected delta_E labels. Given all four available primes already show
   `trapped_fraction` in [0.72, 0.85], the diagnostic result is likely
   `descent_metrics.ran = False` at this graph scale — which is itself
   informative: it may indicate that the greedy descent gets trapped
   pervasively at N ≈ 200–600 regardless of delta_E-labelling quality, a
   property of graph *size*, not of the labelling instrument. If so, BATCH-
   006 cannot simply widen the confirmatory prefix (Front 1's mechanism
   already reaches larger N only by spending more of the aggregate budget on
   the *same* small-N-biased trapped-descent dynamic) — it needs either
   larger graphs (bigger primes, which under the current cumulative-budget
   design cost more and admit fewer of them) or a Coordinator decision on
   whether the trapped-exclusion threshold itself (0.5) is well-calibrated
   for toy-scale graphs before spending more compute chasing coverage.
3. **[MEDIUM] Strengthen C-SEARCH-BIAS's comparability test** (Front 2b).
   The cheapest concrete fix: increase `n_sample` (currently hard-capped at
   20 non-F_p-rational vertices at the smallest prime) to reduce the
   correlation estimate's standard error, and/or replace the fixed
   absolute/ratio threshold with a bootstrap CI directly on
   `(corr_true - corr_rand)`, analogous to the M-GAP CI machinery this same
   codebase already has — letting statistical power scale with sample size
   instead of a magic-number floor. This is the cheapest discriminating
   control for the open question Front 2b raises: whether the observed
   "comparable magnitude" is genuine contamination or an artifact of
   insufficient power.
4. **[LOWER, INFORMATIVE ONLY UNTIL #3 IS DONE] Whether the artifact — if
   real — is fixable by widening B/X, a different tie-break, or is intrinsic
   to Algorithm 2's ascending-order construction.** At n=20 this run cannot
   distinguish those cases (Front 2b): the true-target correlation is
   nominally 3× the random-target one, which is at least directionally
   *inconsistent* with "the two arms behave identically," but neither is
   individually significant. Widening B/X does not obviously address the
   mechanism PF-3's rationale names (the first-collision-in-ascending-order
   return rule, independent of how wide the smoothness bound is); a more
   direct, cheap experiment once #3 gives real power would be to change the
   tie-break/return rule (e.g., return the *minimum*-degree collision across
   the full built table rather than the first one found in ascending prime
   order) and re-run C-SEARCH-BIAS under that variant as an additional
   null-object control — this isolates whether the construction-order rule
   itself is the mechanism, rather than smoothness-bound width.

Items 1–2 require no new compute and should happen before any further
Phase -1 real search is authorized; item 3 requires modest new compute
(a larger C-SEARCH-BIAS sample, cheap relative to the 7200s budget); item 4
is downstream of 3.

---

## FRONT 5 — Other checks

- **Overclaim risk on the wide CI**: checked `manifest.yaml`,
  `execution_report.yaml`, `raw-result.json`, and the receipt. All four
  state the CI plainly (`[-0.4077, 1.3256]`) and explicitly note it is
  irrelevant to the terminal branch because the control-failure check is
  evaluated first; the executor's own `bootstrap_ci_width_note` correctly
  attributes the width to the narrow achieved N-range (203–611, a 3.0× span
  vs. the originally intended 8.9×) rather than spinning it as suggestive.
  **No artifact in this run oversells the CI.** Worth adding for context,
  not as a defect: the bootstrap itself resamples only 4 primes with
  replacement (`descent_hitting_time.py` `bootstrap_gap_ci`, `n=len(N_list)=4`),
  so even setting Front 2/3's findings aside, a 4-point bootstrap has an
  intrinsically coarse resampling distribution (at most 4⁴=256 distinct
  index draws) — the width is not solely a narrow-N-range artifact, it is
  also a small-n-bootstrap artifact. This reinforces that even a
  hypothetical clean `DETECTED` here would rest on a fragile CI.
- **Infrastructure-failure disclosure (PD-3)**: two prior attempts killed by
  an environment-imposed background-process lifetime limit (~60–65 minutes)
  before writing any output, correctly classified `infrastructure_error`,
  correctly excluded from any research conclusion (AGENTS.md rule 3), and
  the surviving partial log (`attempt1-infra-killed.stdout.log`) is
  preserved and hash-pinned in the receipt rather than discarded (rule 8).
  This is complete and compliant; no objection.
- **Diff-list cross-check accuracy**: re-verified independently by grepping
  `compute_delta_e.py` for every function name `compute_delta_e_v2.py`
  imports (`apply_truncation_fallback`, `run_phase_minus1_on_confirmatory_set`,
  `run_feasibility_smoke_test`, `verify_modular_polynomials`,
  `build_all_graphs`, `run_correctness_gates`, `run_c_search_bias`,
  `run_c_bound_check`, `apply_decision_rule`, `git_state`, and the module
  constants) — every name exists in v1's file exactly where
  `execution_report.yaml`'s diff-list claims, and the two functions claimed
  rewritten (`apply_truncation_fallback`, `run_phase_minus1_on_confirmatory_set`)
  are in fact absent from the imported-unchanged list and present, rewritten,
  in `compute_delta_e_v2.py`. **The diff-list cross-check is accurate.**

---

## Numbered objections

1. **[Front 1, not blocking, confirms the fix]** `real_execution_budget_v2`
   is verified sound by direct code inspection and independent arithmetic
   re-derivation: no leftover `T_PRIME`, no per-prime sub-cap, no timing
   leakage from earlier phases, aggregate spend (3600.072s, summed from raw
   per-prime `wall_seconds_used`) matches the reported
   `aggregate_seconds_spent_confirmatory` (3600.0714724063873s) to five
   significant figures.
2. **[Front 2b, MEDIUM]** C-SEARCH-BIAS's comparability test's own two
   clauses disagree on this run's data: the ratio clause
   (`|corr_rand| >= 0.5*|corr_true|`) says NOT comparable (0.03083 <
   0.04805); only the absolute-floor clause (`both < 0.1`) fires, and that
   floor was never pinned in the frozen contract text, was set at
   implementation time without pre-freeze scrutiny, and has essentially no
   statistical power at n=20 (|r| ≳ 0.44 needed for significance) — making
   `magnitudes_comparable_flag=true` a near-certainty whenever the
   true-target correlation itself is weak, independent of whether genuine
   search-construction-order contamination exists. `CONTROL-FAILURE-VOID`
   is the mechanically correct branch, but should not be read as confirmed
   evidence of contamination; it is at least as consistent with "the test
   lacked power to say anything."
3. **[Front 2c, HIGH, NEW FINDING]** C-NULL-LABEL's `control_failure` flag
   is dead code in both v1's `compute_delta_e.py` and v2's
   `compute_delta_e_v2.py`: it is hard-coded `False` and never derived from
   any null-M-GAP fit or comparison, despite the decision branch's own
   reason string citing C-NULL-LABEL as a possible cause of
   `CONTROL-FAILURE-VOID`. Moot for this run's terminal label (C-SEARCH-BIAS
   fires first) but not moot for the campaign: this is the first run to
   reach this code path with real data, and the gap means a future run
   clearing C-SEARCH-BIAS could report `DETECTED` with zero actual
   protection from this required null-object control. Undisclosed by the
   Executor, unflagged by the Coordinator's own review-request items, and
   unflagged by any prior review.
4. **[Front 3, HIGH]** PD-2 (PER-PRIME-TRAPPED-EXCLUSION never implemented)
   independently confirmed against `compute_delta_e.py` line 846
   (`usable_full = [p for p in per_prime]`, no filter) and against
   `raw-result.json`'s own per-prime `greedy_trapped_fraction` values (all
   four contributing primes: 0.7222–0.8511, all above the 0.5 threshold).
   Warrants a new named defect (GD-8-class) and independently invalidates
   `gamma_greedy=0.23354`/`m_gap=+0.16786` as a clean instance of the frozen
   spec's own `M-GAMMA-GREEDY` estimator, regardless of the
   `CONTROL-FAILURE-VOID` label: under a correct exclusion, zero primes
   would remain and `descent_metrics.ran` would be `False`. Not moot — this
   defect will recur in any future run reusing this same inline code.
5. **[Front 4, informational]** Given items 2–4, BATCH-006's cheapest,
   highest-value actions are two zero-new-compute code/re-analysis fixes
   (wire C-NULL-LABEL's comparison logic; implement and re-check
   PER-PRIME-TRAPPED-EXCLUSION against already-collected data) before any
   further Phase -1 real search is authorized, followed by a
   higher-power C-SEARCH-BIAS re-run (larger `n_sample` or a bootstrap-CI
   comparability rule) before drawing any conclusion about whether
   Algorithm 2's construction-order bias is real, let alone whether it is
   fixable by widening B/X.

## Required controls

- A stated, pre-registered comparison rule for C-NULL-LABEL that actually
  computes a null M-GAP (fit + bootstrap CI, mirroring the real arm) and
  sets `c_null_label_control_failure` from it, verified on already-collected
  data from this run before any new search is authorized (item 3 above).
- A re-derivation of `descent_metrics` under a correctly implemented
  PER-PRIME-TRAPPED-EXCLUSION filter, using this run's own already-collected
  delta_E labels, with the resulting outcome (likely `ran: false`) recorded
  explicitly rather than left implicit (item 4 above).
- A higher-power C-SEARCH-BIAS re-run (larger `n_sample`, and/or a
  bootstrap CI on `corr_true - corr_rand` replacing the fixed
  absolute/ratio threshold) before treating any future comparable-magnitude
  finding under this control as confirmed contamination rather than
  insufficient power.

## Counterexample or mutation

The cheapest discriminating check for Front 2c is exactly the one performed
above: `grep -n c_null_label_control_failure` across
`compute_delta_e.py`/`compute_delta_e_v2.py` returns exactly two lines per
file (initialization and pass-through) with no assignment in between —
zero new compute, zero re-measurement, a direct falsifier of "C-NULL-LABEL
functioned as a required control in this run." For Front 2b, the cheapest
discriminating check is re-applying the comparability rule's own ratio
clause in isolation to the already-reported correlations
(0.03083 < 0.5×0.09611 = 0.04805 ⇒ NOT comparable under that clause alone),
showing the absolute-floor clause is doing all the work of the control
failure on this data, with a threshold that was never pre-freeze-reviewed
and has no demonstrated power at n=20. For Front 3, the cheapest
discriminating check is re-reading `usable_full = [p for p in per_prime]`
(`compute_delta_e.py` line 846) against the spec's own text and the four
already-reported `greedy_trapped_fraction` values, all above 0.5 — zero new
compute.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this
remains a toy-scale, gradient-existence screen with `asymptotic_claim: null`
throughout, correctly inherited unchanged through H-SSIQ-9e2c71 to
H-SSIQ-137200. The relevant baseline is, again, this campaign's own
instrument- and fix-scrutiny discipline (GD-4 through GD-7): PF-1's fix
(`real_execution_budget_v2`) passes that standard cleanly on independent
re-derivation — the first genuinely validated fix in this lineage without a
further hidden layer. What this review adds is that the standard needs to
extend past budget-allocation formulas to control-comparison logic itself:
GD-7 was "the fix's own arithmetic was never stress-tested"; Front 2c here
is "the fix's own *comparison logic* was never written at all," one further
layer the same discipline had not yet reached.

## Heuristic challenges

`H-SSIQ-137200.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
numbered heuristic requiring a random-model justification is implicated by
any finding in this review; every finding here is a control-comparison-logic
or estimator-exclusion-filter defect in reused/frozen code, not a claim
about the underlying arithmetic object.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly), so the per-attempt-cost × inverse-success-probability review
does not apply in the complexity-claim sense. What does apply is ordinary
resource bookkeeping, and `real_execution_budget_v2` passes it cleanly
(Front 1): the aggregate counter is measured, not estimated, consistent
between admission and execution for the first time in this lineage, and its
own arithmetic reproduces exactly from raw per-prime numbers. The
outstanding cost-model concern is not budget arithmetic but statistical
power: C-SEARCH-BIAS's `n_sample=20` cap is a resource choice
(`budget_split_seconds.c_search_bias_seconds = 57.286s` for the whole
control) that trades cheapness for a comparability test with essentially no
power to distinguish contamination from noise at this magnitude — a real,
quantifiable cost-vs-power tradeoff the frozen contract never states.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears
anywhere in this run or its hypothesis; `H-SSIQ-137200.scope_ceiling` (toy,
inherited) is correctly stated and not exceeded by anything in this run. No
scope-inflation concern found. The concerns found here (Front 2c, Front 3)
are completeness gaps in reused control/estimator logic relative to the
frozen spec's own stated methodology, not scope widening.

## Proof architecture challenges

`proof_search_map.not_applicable_reason` remains correctly reasoned and
inherited unchanged — this is a direct instrument-level gradient-existence
screen, not a proof-oriented proposal, and nothing in this run converts it
into one. Attacked and held, same verdict as every prior review in this
lineage.

## Narrowest supported statement

Scoped to `RUN-SSIQ-a85692-b` as committed at snapshot `06af9596`:
`real_execution_budget_v2` is independently verified sound (Front 1) and the
`CONTROL-FAILURE-VOID` terminal label is a mechanically correct application
of the frozen decision rule (Front 2a) — this run's honesty and fidelity to
the v2 contract's text is not in question. But the label should not be read
as confirmed evidence of search-construction-order contamination: the
C-SEARCH-BIAS test that produced it has demonstrably weak statistical power
at this sample size and an internally inconsistent comparability rule on
this exact data (Front 2b), and the campaign's *other* required control
(C-NULL-LABEL) is newly found to be structurally incapable of ever failing
in the current code (Front 2c) — a gap this run is the first to expose and
which must be fixed before any future `DETECTED` under this experiment can
be trusted. Separately, PD-2's trapped-fraction-exclusion gap (independently
confirmed, Front 3) means `gamma_greedy=0.23354`/`m_gap=+0.16786` are not a
clean instance of the frozen spec's own `M-GAMMA-GREEDY` estimator even
setting contamination aside. H-SSIQ-137200's real-arm prediction remains
genuinely untested by this run: not because the instrument failed (it
worked, for the first time end-to-end), but because the run's own control
battery has two now-documented gaps that leave the question open rather than
answered in either direction.

## Next concrete action

Coordinator: before authorizing further BATCH-006 real search, require (1)
a code fix wiring C-NULL-LABEL's actual null-M-GAP comparison logic
(Front 2c), applied and checked against this run's own already-collected
`c_null_label.per_prime` data at zero new compute; (2) a re-derivation of
`descent_metrics` under a correctly implemented
PER-PRIME-TRAPPED-EXCLUSION filter (Front 3/PD-2) against this run's own
already-collected delta_E labels, also zero new compute; (3) a decision on
whether to record these as new goal-record defects (candidate GD-8/GD-9,
numbering at the Coordinator's discretion) in the same lineage as
GD-4–GD-7; (4) only after (1)–(2), a higher-power C-SEARCH-BIAS re-run
(larger `n_sample` or a bootstrap-CI comparability rule, Front 2b/Front 4
item 3) before any future run's comparable-magnitude finding is read as
confirmed contamination. None of this requires abandoning lever L4 or this
experiment's mechanism, which — modulo these control-logic gaps — is
otherwise sound and, for the first time in this campaign, produced a real,
end-to-end computed M-GAP.

## Overall verdict

**CHALLENGE.**

Not a challenge to `real_execution_budget_v2` (verified sound) or to the
Executor's honesty, completeness, or mechanical fidelity to the frozen v2
contract — all are confirmed by independent re-derivation. The challenge is
to the evidentiary weight the receipt implicitly grants
`CONTROL-FAILURE-VOID`: the control that produced it has demonstrably weak
power on this exact data and an internally inconsistent comparability rule
that was never pre-freeze-scrutinized, and the campaign's other required
null-object control is newly found to be dead code, unable to have caught
anything even had C-SEARCH-BIAS passed. This run is honestly reported and
represents genuine, hard-won progress (the first real, end-to-end M-GAP in
this campaign's history), but its terminal label should be read as "the
control battery could not clear this run for a clean read, for reasons that
are at least partly a test-design gap rather than confirmed contamination,"
not as "search-construction-order bias confirmed real." Two zero-new-compute
fixes (Front 2c, Front 3) should close before any further real search.

```yaml
red_team_report:
  id: RT-BATCH-005
  task_id: TASK-20260805-f60ff9
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b (snapshot commit
    06af9596, parent 14b56525; receipt TASK-20260805-8bddd0-receipt.yaml):
    the first run in this campaign where the Phase -1 gate passed and a real
    M-GAP was computed on real, in-session-computed delta_E labels
    (gamma_greedy=0.23354, gamma_random=0.40140, m_gap=+0.16786, bootstrap
    95% CI [-0.4077, 1.3256], n_primes_used=4), with terminal branch
    CONTROL-FAILURE-VOID because C-SEARCH-BIAS's random-target correlation
    (0.03083) was flagged comparable in magnitude to the true-target
    correlation (0.09611) under the run's own comparability rule.
  objections:
    - "OBJ-1 [Front 1, CONFIRMS THE FIX]: real_execution_budget_v2 (PF-1's fix) is verified sound by direct code inspection and independent arithmetic re-derivation -- no leftover T_PRIME, no reintroduced per-prime sub-cap, no timing leakage from earlier phases; aggregate spend re-summed from raw per-prime wall_seconds_used (3600.072s) matches the reported aggregate_seconds_spent_confirmatory (3600.0714724063873s) to five significant figures, and PF-1's own pre-freeze prediction (at most ~2 of 4 primes would clear coverage under the unfixed cap) is directly falsified by this run under the fixed mechanism (5 of 5 admitted primes clear it)."
    - "OBJ-2 [Front 2b, MEDIUM]: C-SEARCH-BIAS's comparability rule's own two clauses disagree on this data -- the ratio clause (|corr_rand| >= 0.5*|corr_true|) says NOT comparable (0.03083 < 0.04805); only the absolute-floor clause (both < 0.1) fires, and that numeric floor was never pinned in the frozen contract text, was set at implementation time without pre-freeze scrutiny, and has essentially no statistical power at n=20 (|r| >~ 0.44 needed for significance) -- making magnitudes_comparable_flag=true a near-certainty whenever the true-target correlation itself is weak, independent of whether genuine search-construction-order contamination exists. CONTROL-FAILURE-VOID is the mechanically correct branch but should not be read as confirmed contamination."
    - "OBJ-3 [Front 2c, HIGH, NEW FINDING]: C-NULL-LABEL's control_failure flag is dead code in both v1's compute_delta_e.py and v2's compute_delta_e_v2.py -- hard-coded False, never derived from any null-M-GAP fit or comparison, despite the decision branch's own reason string citing C-NULL-LABEL as a possible cause of CONTROL-FAILURE-VOID. Moot for this run's terminal label (C-SEARCH-BIAS fires first) but not moot for the campaign: this is the first run to reach this code path with real data, and the gap means a future run clearing C-SEARCH-BIAS could report DETECTED with zero actual protection from this required null-object control. Undisclosed by the Executor, unflagged by the Coordinator's own review-request items, and unflagged by any prior review."
    - "OBJ-4 [Front 3, HIGH]: PD-2 (PER-PRIME-TRAPPED-EXCLUSION never implemented) independently confirmed against compute_delta_e.py line 846 (usable_full = [p for p in per_prime], no filter) and against raw-result.json's own per-prime greedy_trapped_fraction values (all four contributing primes: 0.7222-0.8511, all above the 0.5 threshold). Warrants a new named defect (GD-8-class) and independently invalidates gamma_greedy=0.23354/m_gap=+0.16786 as a clean instance of the frozen spec's own M-GAMMA-GREEDY estimator, regardless of the CONTROL-FAILURE-VOID label: under a correct exclusion, zero primes would remain and descent_metrics.ran would be False. Not moot -- this defect will recur in any future run reusing this same inline code."
    - "OBJ-5 [Front 5, minor, not blocking]: usable_primes_for_fit / log lines describe the C-NULL-LABEL/descent-metrics usable set as n=5 (including 8893) though 8893 is skipped inside both loops for partial coverage and the actual fit uses n=4 -- correctly reflected in the numeric fields (n_primes_used=4) but the field/log naming is misleading on a quick read. Cosmetic."
  required_controls:
    - "A stated, pre-registered comparison rule for C-NULL-LABEL that actually fits a null M-GAP (OLS-log-log + bootstrap CI, mirroring the real arm) and sets c_null_label_control_failure from it, verified on this run's own already-collected c_null_label.per_prime data before any new search is authorized."
    - "A re-derivation of descent_metrics under a correctly implemented PER-PRIME-TRAPPED-EXCLUSION filter, using this run's own already-collected delta_E labels, with the resulting outcome (likely ran: false) recorded explicitly."
    - "A higher-power C-SEARCH-BIAS re-run (larger n_sample and/or a bootstrap CI on corr_true - corr_rand replacing the fixed absolute/ratio threshold) before any future comparable-magnitude finding under this control is read as confirmed contamination rather than insufficient power."
  counterexample_or_mutation: >-
    grep -n c_null_label_control_failure across compute_delta_e.py and
    compute_delta_e_v2.py returns exactly two lines per file (initialization
    to False, pass-through into apply_decision_rule) with no assignment in
    between -- zero new compute, a direct falsifier of "C-NULL-LABEL
    functioned as a required control in this run." Separately, re-applying
    C-SEARCH-BIAS's comparability rule's ratio clause alone to the reported
    correlations (0.03083 < 0.5*0.09611 = 0.04805) shows it says NOT
    comparable, isolating that the absolute-floor clause alone drives
    CONTROL-FAILURE-VOID on this data. Separately, re-reading
    usable_full = [p for p in per_prime] (compute_delta_e.py line 846)
    against the four already-reported greedy_trapped_fraction values
    (all > 0.5) confirms PD-2 with zero new compute.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-7):
    real_execution_budget_v2 passes that standard cleanly on independent
    re-derivation -- the first fix in this lineage validated without a
    further hidden layer at the budget-arithmetic level. This review extends
    the same discipline one layer further, into control-comparison logic
    itself: GD-7 was "the fix's own arithmetic was never stress-tested";
    Front 2c here is "the fix's own comparison logic was never written at
    all."
  heuristic_challenges:
    - "H-SSIQ-137200.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. Every finding in this review is a control-comparison-logic or estimator-exclusion-filter defect in reused/frozen code, not a claim about the underlying arithmetic object."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply in the complexity-claim sense."
    - "real_execution_budget_v2 passes ordinary resource bookkeeping cleanly (measured, not estimated; consistent between admission and execution; arithmetic reproduces exactly from raw numbers, Front 1)."
    - "The outstanding cost-model concern is statistical power, not budget arithmetic: C-SEARCH-BIAS's n_sample=20 cap (57.286s of the 7200s budget) trades cheapness for a comparability test with essentially no power to distinguish contamination from noise at this magnitude -- a real cost-vs-power tradeoff the frozen contract never states."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this run or its hypothesis; H-SSIQ-137200.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "The concerns found here (Front 2c, Front 3) are completeness gaps in reused control/estimator logic relative to the frozen spec's own stated methodology, not scope widening."
  proof_architecture_challenges:
    - "proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal; nothing in this run converts it into one. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to RUN-SSIQ-a85692-b at snapshot 06af9596: real_execution_budget_v2
    is independently verified sound and CONTROL-FAILURE-VOID is a
    mechanically correct application of the frozen decision rule. But the
    label should not be read as confirmed evidence of search-construction
    -order contamination: C-SEARCH-BIAS's comparability test has demonstrably
    weak power at n=20 and an internally inconsistent result on this exact
    data (its own ratio clause says NOT comparable), and C-NULL-LABEL -- the
    campaign's other required control, cited in the same decision branch's
    reason text -- is newly found to be structurally incapable of ever
    failing in the current code, a gap this run is the first to expose.
    Separately, PD-2's independently-confirmed trapped-fraction-exclusion gap
    means gamma_greedy=0.23354/m_gap=+0.16786 are not a clean instance of the
    frozen spec's own M-GAMMA-GREEDY estimator even setting contamination
    aside. H-SSIQ-137200's real-arm prediction remains genuinely untested:
    the instrument worked end-to-end for the first time, but the run's own
    control battery has two now-documented gaps that leave the question open
    rather than answered in either direction.
  next_concrete_action: >-
    Coordinator: before authorizing further BATCH-006 real search, require
    (1) a code fix wiring C-NULL-LABEL's actual null-M-GAP comparison logic,
    checked against this run's own already-collected c_null_label.per_prime
    data at zero new compute; (2) a re-derivation of descent_metrics under a
    correctly implemented PER-PRIME-TRAPPED-EXCLUSION filter against this
    run's own already-collected delta_E labels, also zero new compute; (3) a
    decision on recording these as new goal-record defects (candidate
    GD-8/GD-9) in the GD-4-GD-7 lineage; (4) only after (1)-(2), a
    higher-power C-SEARCH-BIAS re-run before any future comparable-magnitude
    finding is read as confirmed contamination.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/reviews/RT-BATCH-005.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic and code-inspection only, entirely on numbers already
    committed in experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json
    (summation of per-prime wall_seconds_used against the reported aggregate
    counter; re-application of the C-SEARCH-BIAS comparability rule's ratio
    clause in isolation to already-reported correlations) plus direct
    reading (not executing) of compute_delta_e_v2.py, compute_delta_e.py, and
    descent_hitting_time.py to trace real_execution_budget_v2, the
    C-SEARCH-BIAS comparability rule, the C-NULL-LABEL control_failure
    assignment, and the PER-PRIME-TRAPPED-EXCLUSION filter against the frozen
    spec's text. No code executed, no graph built, no search run, no new
    measurement taken.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/reviews/RT-BATCH-005.md
    -- experiments/EXP-SSIQ-a85692/, experiments/EXP-SSIQ-58b642/, and every
    ledger record are untouched.
  verdict: CHALLENGE
```
