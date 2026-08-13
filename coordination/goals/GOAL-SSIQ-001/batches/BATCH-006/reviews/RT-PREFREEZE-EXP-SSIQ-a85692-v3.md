# RT-PREFREEZE-EXP-SSIQ-a85692-v3 — Pre-freeze Red Team review of the DRAFT
# amendment `specification_v3.yaml` (H-SSIQ-36e970), GOAL-SSIQ-001 BATCH-006

**Reviews `experiments/EXP-SSIQ-a85692/specification_v3.yaml` at `status: draft`
(this task's working-tree read; the amendment is not yet snapshot-committed by
the Coordinator, and this report changes nothing under
`experiments/EXP-SSIQ-a85692/` — including its already-frozen v2
`specification_v2.yaml` at commit `14b56525` — or any ledger record; those
remain the Coordinator's alone to touch.** `specification_v3.yaml` itself was
read in full, not sampled. Every other input named in the launching task was
read in full: `specification_v2.yaml` (327 lines, frozen `14b56525`);
`RT-BATCH-005.md` and `VAL-BATCH-005.md` (full); `RUN-SSIQ-a85692-b`'s
`raw-result.json` (`descent_metrics.per_prime` and `c_null_label.per_prime`
read directly, not via either prior review's summary); `descent_hitting_time.py`
(full, 794 lines, `ols_loglog_fit` lines 104–134 and `bootstrap_gap_ci` lines
362–384 read in full, not merely at the cited line numbers); `compute_delta_e_v2.py`
(full, 831 lines) to confirm `required_artifacts_note`'s unchanged-vs-changed
claim; and, beyond what the task named, `compute_delta_e.py` (v1,
`run_correctness_gates` lines 260–287, `run_c_bound_check` lines 514–542,
`apply_decision_rule` lines 549–581) and `specification.yaml`'s C-SEED/C-REPRO
entries (lines 400–424), to independently execute item (e)'s instruction to
check every other reused control, not merely re-cite that C-NULL-LABEL was
the one found broken. `goal.yaml`'s GD-8/GD-9 entries, `EV-SSIQ-f3ce32.yaml`,
`DEC-20260805-5f5ac6.yaml`, and `H-SSIQ-36e970.yaml` read in full.
`RT-PREFREEZE-EXP-SSIQ-a85692-v2.md` read in full as the structural template
this report follows.

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
    RT-BATCH-004, VAL/RT-BATCH-005), so this is recorded as the standing
    condition, not re-discovered.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent, per
    `ledger/goals/GOAL-SSIQ-001/goal.yaml` `runtime.runtime_note`. This review
    is not corroboration from a distinct model and does not upgrade the
    campaign's evidence tier by itself.
```

---

## Bottom line up front

Checks (b) and (e) — the two purely mechanical, zero-new-compute
verifications — both **pass cleanly**: the draft's own worked check is
independently reproduced exactly (both arms, not merely the real arm the
draft's own text quotes), and no *other* reused control besides C-NULL-LABEL
was found to have unimplemented comparison logic. Check (d) also passes: the
new gate is correctly scoped and does not reopen the already-passed Phase −1
gate.

**But two structural gaps survive into this draft that GD-9's own standing
repair exists specifically to catch, and both are subtler than GD-9 itself —
neither is a `grep`-detectable hard-coded flag; both require tracing what the
already-known data forces the new code to actually do.**

1. **[PF-1] `c_null_label_comparison_v3`'s own fit-and-bootstrap branch (the
   `>=3 primes` path) is structurally unreachable on this run's data.**
   Independently confirmed below (check (b)): *both* arms have zero of four
   primes surviving `trapped_exclusion_filter_v3` — not just the real arm the
   draft's worked check quotes. This means `c_null_label_comparison_v3`'s new
   code can *only* ever be exercised, on `RUN-SSIQ-a85692-b`'s data, down the
   `NOT-EVALUABLE` path. A correctly-implemented fit-and-bootstrap branch and
   a *stub* that always returns `NOT-EVALUABLE` without ever really trying
   produce **byte-identical output** on this run. This is a different, harder
   failure mode than GD-9's own (a hard-coded `False` that `grep` finds in two
   lines): here the branch could be fully, correctly implemented and this
   run's own artifacts would give zero runtime evidence of that fact. The
   draft does not disclose this limitation anywhere, and its own framing
   ("GD-9's fix," "wires C-NULL-LABEL's actual comparison logic") reads as a
   stronger claim than what this dispatch can actually demonstrate.
2. **[PF-2] `decision_rule_v3` requires re-invoking `apply_decision_rule`'s
   ordering, but `required_artifacts_note` never names it, and its Boolean-only
   interface has no slot for the `NOT-EVALUABLE` third state
   `invalidation_rules_v3_additions` itself requires be preserved.** Not live
   on this specific dispatch (the real-arm gate is confirmed, below, to fail
   deterministically before this interface would ever be exercised), but a
   genuine, foreseeable specification gap of exactly the kind this campaign's
   discipline (`RT-PREFREEZE-EXP-SSIQ-a85692-v2.md` PF-2) has previously rated
   blocking even when the ambiguous path was not certain to fire.

Neither finding requires redesigning the amendment's mechanism, and neither
changes checks (b)/(c)/(d)/(e)'s otherwise-clean results. Both are fixable
with text-only changes plus one cheap synthetic self-test — zero new search
cost, consistent with the amendment's own stated budget.

---

## (a) Does the spec text itself make "implement nothing, report a default" impossible?

**Partially. The text is precise about the algorithm (a materially stronger
starting point than v1's original prose, which is what let GD-9 hide for
three batches), but precision of algorithmic description is not the same
thing as runtime falsifiability, and this draft's own data makes the second
one unavailable for the one new code path it exists to add.**

What the text gets right, checked directly against what GD-9's own discovery
method needs: `required_artifacts_note` names `ols_loglog_fit` and
`bootstrap_gap_ci` as **imported unchanged, by reference** from
`descent_hitting_time.py` — not reimplemented — so a reviewer can `grep` the
new `reanalyze_v3.py` for calls to `dht.ols_loglog_fit`/`dht.bootstrap_gap_ci`
inside the null-arm branch exactly the way GD-9 was found by `grep`ping for an
assignment that never happened (`RT-BATCH-005.md` Front 2c's own
counterexample). `invalidation_rules_v3_additions` explicitly forbids
defaulting `NOT-EVALUABLE` to either `True` or `False` — a real, checkable
constraint an Executor cannot silently violate without the resulting flag
value being wrong by inspection. Both of these are genuine improvements over
v1's prose, which is exactly why GD-9 was invisible for so long: v1 never even
stated a comparison rule to check code against.

What the text does not, and structurally cannot, provide: **runtime
evidence that the `>=3`-primes branch executes correctly**, because — see
check (b) below, independently re-derived from `raw-result.json` for *both*
arms, not only the one the draft's own worked check quotes — that branch is
never entered on this run's data. GD-9 was caught because `RUN-SSIQ-a85692-b`
was "the first run in the project's history to reach this code path with real
data" (`goal.yaml` GD-9 entry, verbatim); this amendment's `c_null_label_comparison_v3`
fix has the *same* property in reverse — this re-analysis, on the only data it
is authorized to touch, is **guaranteed never to reach its own new code
path's substantive branch**, so it cannot be the run that plays GD-9's
detection role for whatever residual bugs might exist inside the
fit-and-bootstrap branch itself. A reviewer can still verify the branch by
*reading* it (which this report does, to the extent the branch exists only as
prose at draft stage — there is no code yet to read), but the campaign's own
adopted standard after GD-9 is "verified by direct code inspection... not
assumed functional because it 'ran'" (`DEC-20260805-5f5ac6` D-4) — and this
draft, as specified, will let a future reader believe `c_null_label_comparison_v3`
"ran" (a `c_null_label_report` block will exist, exactly the shape that made
GD-9's `c_null_label.ran: true` look reassuring on a shallow read) without the
branch that actually contains the fix ever having executed. See PF-1.

## (b) Independent re-derivation: which primes survive `trapped_exclusion_filter_v3`, both arms

Re-read `descent_metrics.per_prime` and `c_null_label.per_prime` directly from
`RUN-SSIQ-a85692-b/raw-result.json`, independent of the draft's own worked
check (which quotes only the real arm's four numbers):

| prime | real arm `greedy_trapped_fraction` (`descent_metrics.per_prime`) | survives (≤0.5)? | null arm `greedy_trapped_fraction` (`c_null_label.per_prime`) | survives (≤0.5)? |
|---|---|---|---|---|
| 2437 | 0.8374384236453202 | NO | 0.8078817733990148 | NO |
| 3889 | 0.7222222222222222 | NO | 0.7037037037037037 | NO |
| 5737 | 0.8200836820083682 | NO | 0.7907949790794979 | NO |
| 7333 | 0.8510638297872340 | NO | 0.8477905073649754 | NO |
| 8893 | *(not in `descent_metrics.per_prime` — excluded upstream for partial `delta_map` coverage)* | n/a | *(`c_null_label.per_prime["8893"].skipped = true`, partial coverage)* | n/a |

**Confirms, and extends, the draft's own worked check: 0 of 4 primes survive
in the real arm (exactly the draft's quoted numbers, reproduced to every
shown digit), and — independently checked here, not stated anywhere in the
draft's own worked-check text — 0 of 4 primes also survive in the null arm.**
The null arm's numbers are close to but not identical to the real arm's
(e.g. prime 3889: real 0.7222 vs. null 0.7037), consistent with the draft's
own stated rationale that trappedness is graph/topology-driven rather than
label-driven, but each arm's filter is applied to its own independently
computed number, not inherited from the other — correctly, as specified.
**Check (b) passes on arithmetic grounds** (both arms independently
reconfirmed at zero new compute), but see PF-1: this same fact is what makes
`c_null_label_comparison_v3`'s substantive branch unreachable.

One minor imprecision, found while checking both arms as the launching task
required: `pre_freeze_review.note`'s own summary states the four contributing
primes have "`trapped_fraction` in `[0.72, 0.85]`" — accurate for the real
arm (min 0.7222, max 0.8511) but not for the null arm, whose minimum
(0.7037037037037037, prime 3889) falls below the quoted 0.72 floor. Does not
change the qualitative conclusion (all values in both arms exceed the 0.5
exclusion threshold), but is worth a one-line correction given this document's
own emphasis on checked-not-trusted arithmetic. See PF-3.

## (c) Is `c_null_label_comparison_v3`'s comparison rule sound, and is it reverse-engineered?

**Soundness, in isolation: a defensible design, but with the same low-power
character `RT-BATCH-005.md` Front 2b found in C-SEARCH-BIAS, on an even
smaller resampling unit — and, per (a)/(b) above, this run cannot exercise it
to find out empirically. Reverse-engineering: largely mitigated, but the
draft's own text concedes the boundary condition that matters.**

**Rule mirrors an existing criterion, not a new bespoke one.** The rule
("null CI also excludes 0 in the positive direction = control failure")
reuses `apply_decision_rule`'s own pre-existing `DETECTED` criterion
(`compute_delta_e.py` line 572: `m_gap_ci_lo is not None and m_gap_ci_lo >
0.0`, unchanged since v1) rather than inventing a new magic threshold the way
C-SEARCH-BIAS's absolute-floor clause did. This is a materially more
principled design than C-SEARCH-BIAS's own comparability rule, and it directly
addresses `docs/inventor-protocol.md` §3's null-object-control requirement:
checking whether the *null* arm reproduces the *same* detection signature the
real arm's own pre-registered rule would call `DETECTED` is exactly the right
question to ask of a null-object control.

**Statistical power is a real, structurally unaddressed concern, one layer
below C-SEARCH-BIAS's.** `bootstrap_gap_ci` (`descent_hitting_time.py` lines
362–384, read in full) resamples the **prime-level** OLS-fit inputs with
replacement, `n = len(N_list)` at a time. At `n=4` (the real arm's own
`RUN-SSIQ-a85692-b` fit) this gives at most `4**4 = 256` distinct resample
draws; `RT-BATCH-005.md`'s Front 5 already flagged this as an "intrinsically
coarse resampling distribution" for the *real* arm's own CI. The null arm's
comparison rule as specified requires only `>= 3` primes (`ols_loglog_fit`'s
own floor) — at `n=3` the bootstrap has at most `3**3 = 27` distinct resample
draws, an even coarser distribution than the real arm's already-flagged one.
Whether a 3-point (or 4-point) null-arm CI does or does not exclude 0 is
plausibly dominated by which few prime-level points happen to be available
rather than by any genuine graph-topology-vs-delta_E-information distinction
— the exact "trivially passes or trivially fails regardless of mechanism"
shape `RT-BATCH-005.md` Front 2b found in C-SEARCH-BIAS's absolute-floor
clause, here arising from bootstrap coarseness rather than a magic-number
threshold. **This cannot be checked empirically on this run's data** (per
(a)/(b): the branch never fires), so it is recorded here as an open design
question for the next run that *does* reach it, per GD-9's own standing
repair ("verify... now that it is known to be possible, not assumed absent
elsewhere just because it was found once"). See PF-4.

**Reverse-engineering check.** The spec text states the rule was "STATED
BEFORE THIS DOCUMENT'S DRAFTER LOOKED AT RUN-SSIQ-a85692-b's null_by_prime
numbers **in any detail beyond what BATCH-005's own committed artifacts
already disclosed**" (emphasis on the draft's own hedge). `c_null_label.per_prime`
*is* one of BATCH-005's own committed artifacts — every trapped_fraction and
median value used in this review's check (b) above was already sitting in
`raw-result.json` before this draft was written, and this campaign's own
standing practice (GD-6) requires the drafter to have read the full run
package. So the literal claim "before looking at the numbers" cannot be taken
as "the drafter had zero information about what this rule would output" — the
drafter necessarily knew, or could trivially have derived, that
`trapped_exclusion_filter_v3` (drafted in the *same* document) would leave
zero survivors in both arms, i.e. that this specific comparison rule's choice
of threshold/direction was **never going to be exercised on this run's data
regardless of how it was worded**. That materially reduces (though does not
eliminate) the incentive-to-tune concern this document itself raises: there
was no live outcome on this data for a tuned rule to protect or attack. The
rule's substantive content (mirroring the pre-existing `DETECTED` criterion
rather than inventing a new number) is independent evidence against tuning.
**Net: not a violation of pre-registration discipline, but the hedge's
literal wording overstates how blind the drafter actually was, given this
campaign's own full-read requirement — a one-line correction, not a
finding that rises to blocking.**

## (d) Does the `DATA-UNAVAILABLE/BLOCKED` branch correctly avoid reopening the Phase −1 gate?

**Yes, cleanly.** `decision_rule_v3`'s text is explicit and correctly scoped:
"the Phase −1 gate itself, M-COVERAGE≥0.5 on ≥4 primes, is UNCHANGED and was
already passed in RUN-SSIQ-a85692-b — this amendment does not reopen it,"
followed by "NEW GATE, CHECKED FIRST" specific to the corrected filter. These
are genuinely different quantities in the underlying data
(`m_coverage_non_fp_fraction`, computed during the real search, vs.
`greedy_trapped_fraction`, computed during descent simulation) with no shared
code path, so there is no risk of the new gate accidentally re-evaluating the
old one. Re-checked directly: `phase_minus1_gate_pass` in `RUN-SSIQ-a85692-b`
was `True` (`n_primes_coverage_pass=5 >= 4`, all independently re-verified by
both BATCH-005 reviewers already); the new gate is a distinct, later check on
a disjoint per-prime quantity. **Given check (b)'s independent confirmation
that the new gate fires (0 < 4 real-arm survivors), `DATA-UNAVAILABLE/BLOCKED`
is the correct, mechanically forced outcome of this dispatch, and it is
distinctly labelled from every other `DATA-UNAVAILABLE/BLOCKED` instance this
campaign has recorded, per the draft's own text.**

Is this outcome "genuinely informative... not a way to avoid computing an
inconvenient number"? Yes: it is disclosed in the draft's own worked check
*before* freeze (not discovered mid-run and then rationalized), it is
consistent with `H-SSIQ-36e970`'s own stated assumption #3 ("plausible given
BATCH-005's own trapped_fraction figures"), and `goal.yaml`'s `next_action`
already frames a correctly-derived zero-survivor result as informative about
whether trapped descent is graph-size-driven rather than labelling-driven.
**One clarification worth adding to the narrowest-supported-statement
framing, not a defect**: because this outcome is essentially certain given
already-known numbers (independently reconfirmed here), this dispatch should
not be read as *testing* `H-SSIQ-36e970`'s real-arm prediction at all — it is
expected, with high confidence, to formally confirm that no clean test is
currently possible with this data under the corrected filter, which is a
narrower claim than "tests the hypothesis." The draft's own `amendment_scope`
and `H-SSIQ-36e970`'s own assumptions already say this in substance; it should
be stated as plainly in `decision_rule_v3` itself so a reader does not need to
cross-reference the hypothesis record to know it.

## (e) Any other reused control with unimplemented comparison logic?

**Checked directly against the code, per GD-9's standing repair. No new
dead-code control found among C-BOUND-CHECK, C-CONNECTIVITY, C-DEGSEQ,
C-EDGELIST, C-SEED, C-REPRO.**

- **C-CONNECTIVITY / M-DEGSEQ / C-EDGELIST** (`compute_delta_e.py` lines
  260–287, `run_correctness_gates`): each computes a real, non-trivial
  comparison (`n_built == n_formula_floor_p12`; `big.degree_sequence_check`;
  `big.independent_edgelist_check`) and returns an actual pass/fail per
  prime, consumed directly by `all_connectivity_pass = all(gates["connectivity"][p]["pass"]
  for p in PRIMES)` in `main()` (`compute_delta_e_v2.py` line 403) and fed
  into `apply_decision_rule`'s real `c_connectivity_all_pass` parameter — a
  live, gating comparison, not dead code.
- **C-BOUND-CHECK** (`compute_delta_e.py` lines 514–542, `run_c_bound_check`):
  computes `n_delta_eq_1_by_identity` per prime and explicitly, correctly
  reports itself as **non-gating** ("`spec.controls.C-BOUND-CHECK` states this
  second cross-check runs 'budget permitting' and 'does not gate the run.'")
  — `apply_decision_rule`'s signature has no parameter for it at all. This is
  disclosed, intentional non-gating status, not an omitted comparison
  masquerading as a control; VAL-BATCH-005 §"control_checks" independently
  confirmed the same reading ("ran, reported, non-gating per spec").
- **C-SEED / C-REPRO** (`specification.yaml` lines 419–424): defined as
  process-level properties (fixed seeds; deterministic replay), not as
  in-code `control_failure` flags computed by `compute_delta_e.py` at all —
  there is no `c_seed_control_failure` or `c_repro_control_failure` variable
  anywhere in either implementation file to be dead. These are verified
  *externally*, by a reviewer re-running the deterministic computation and
  checking for a bit-identical match — exactly what VAL-BATCH-005 §6 did
  (`bootstrap_gap_ci` reproduced to an exact bit match under the pinned seed).
  A GD-9-shaped defect is structurally impossible for a control with no
  internal flag to leave unassigned.

**Check (e) passes: no second GD-9-class defect found among the six named
controls.** The one substantive gap found in this review (PF-1/PF-2) is not
in these six controls but in the *new* code this amendment itself introduces.

## (f) Other issues

- **Budget realism**: 300s wall-clock for a JSON read, a filter over ≤5
  primes, two OLS fits on ≤4 points, and a 2000-resample bootstrap on ≤4
  points is generous by roughly two to three orders of magnitude (this class
  of arithmetic completes in well under a second in pure Python, consistent
  with `bootstrap_gap_ci`'s own already-measured cost:
  `descent_simulation_seconds=0.4877s` for the *full* real-arm fit-plus-boot
  in `RUN-SSIQ-a85692-b`, which additionally built graphs and ran population
  simulations this re-analysis does not). No concern.
- **`required_artifacts_note`'s diff-list precision**: precise and checkable
  for what it names (new `reanalyze_v3.py`; `ols_loglog_fit`/`bootstrap_gap_ci`
  imported by reference; `compute_delta_e_v2.py`'s search/admission/Phase −1
  code explicitly not invoked) — **but incomplete relative to what
  `decision_rule_v3` itself requires**. See PF-2: `decision_rule_v3` instructs
  reapplying "v1/v2's UNCHANGED decision rule ordering," which is
  `apply_decision_rule` (`compute_delta_e.py` lines 549–581) — this function
  is never named anywhere in `required_artifacts_note`'s diff list, neither as
  imported-unchanged nor as reimplemented. This is the same species of gap
  `RT-PREFREEZE-EXP-SSIQ-a85692-v2.md`'s own PF-1/PF-5 found in the v2 draft
  (a diff list that is accurate as far as it goes but silently omits a
  function the amendment's own logic actually needs).
- **"Zero new search" framing**: checked directly and **accurate**. Every
  input `c_null_label_comparison_v3` and `trapped_exclusion_filter_v3` need
  (`N`, `greedy_median`, `random_median`, `greedy_trapped_fraction` per prime,
  both arms) is already a scalar field in `raw-result.json`'s
  `descent_metrics.per_prime` and `c_null_label.per_prime` blocks (confirmed
  directly, check (b) above) — no graph object, adjacency list, or `delta_map`
  reconstruction is required, so `reanalyze_v3.py` genuinely need not import
  `build_isogeny_graph.py` or call `two_sided_search`. VAL-BATCH-005 §6
  already established that the real arm's own OLS/bootstrap arithmetic is
  independently reproducible from the reported medians alone, without
  re-executing the search — this amendment relies on exactly that same,
  already-validated property for the null arm. No overclaim found on this
  specific point.

---

## Findings

### PF-1 — [BLOCKING] `c_null_label_comparison_v3`'s fit-and-bootstrap branch is unreachable on this run's own data; the draft does not disclose this or require any runtime check of the branch it exists to add

Quantified from already-committed numbers, zero new compute (check (b)
above): trapped_exclusion_filter_v3 leaves 0 of 4 primes in **both** the real
arm and the null arm. `c_null_label_comparison_v3`'s only substantive new
code — the `IF (and only if) trapped_exclusion_filter_v3 leaves >=3 primes
surviving in the null arm` branch that actually fits `gamma_null_greedy`/
`gamma_null_random` and bootstraps a CI — will **not execute** on this
dispatch; the run can only ever reach the `NOT-EVALUABLE` path. A fully,
correctly implemented fit-and-bootstrap branch and a stub that unconditionally
returns `NOT-EVALUABLE` are indistinguishable in this run's `raw-result.json`,
`manifest.yaml`, and `execution_report.yaml`. This is not GD-9's own failure
mode (a `grep`-detectable hard-coded flag) — it is the harder case GD-9's
standing repair anticipates without naming: a control whose comparison logic
*could* be entirely correct, or entirely absent, or subtly wrong, with the
run's own artifacts providing no way to tell, because the branch that would
reveal the difference is never entered. The draft's own framing ("wires
C-NULL-LABEL's actual comparison logic," "GD-9's fix") reads as a stronger,
already-delivered claim than what this dispatch can support.

**Fix, concrete, zero new search cost:**
1. `required_artifacts_note` or `decision_rule_v3` must state explicitly that,
   given `trapped_exclusion_filter_v3`'s own worked check, this dispatch is
   expected to exercise only the `NOT-EVALUABLE` path of
   `c_null_label_comparison_v3`, and that the fit-and-bootstrap branch's
   correctness therefore rests on static code review (this report's check
   (a)), not on any runtime evidence this run's own artifacts can supply.
2. Add, as a required artifact, a small synthetic self-test independent of
   `RUN-SSIQ-a85692-b`'s real data — e.g. three or four constructed
   `(N, greedy_median, random_median)` triples with a hand-computable
   `gamma`/`m_gap` — demonstrating `c_null_label_comparison_v3`'s
   fit-and-bootstrap code path actually executes end-to-end and produces the
   expected numbers. This is a few lines of test code exercising the same
   `ols_loglog_fit`/`bootstrap_gap_ci` calls already imported by reference;
   it adds no measurable cost against the 300s budget and gives the next
   reviewer runtime, not merely textual, evidence that GD-9's actual fix
   works, closing exactly the gap this finding identifies.

### PF-2 — [BLOCKING] `apply_decision_rule`'s reuse is required by `decision_rule_v3` but omitted from `required_artifacts_note`, and its Boolean interface has no defined behavior for `NOT-EVALUABLE`

`decision_rule_v3` instructs, for the (on this data, unreached) `>=4-primes-survive`
branch: "apply v1/v2's UNCHANGED decision rule ordering (Phase 0 already
passed → Phase −1 gate already passed → control-failure check, now including
`c_null_label_control_failure` computed for real for the first time...)" —
this is `apply_decision_rule` (`compute_delta_e.py` lines 549–581), whose
signature takes `c_null_label_control_failure` as a plain Boolean (line 551).
Two gaps, found by reading the function signature against the spec text
directly:

1. `required_artifacts_note`'s diff list never names `apply_decision_rule`
   anywhere — not as "imported unchanged, by reference" (the treatment given
   to `ols_loglog_fit`/`bootstrap_gap_ci`), nor as new or reimplemented. A
   function the amendment's own decision logic depends on is absent from the
   one place `required_artifacts_note` promises to name every changed or
   reused function/call site.
2. `invalidation_rules_v3_additions` explicitly requires `NOT-EVALUABLE` be
   reported as a state **distinct from both `True` and `False`**, and
   forbids defaulting it to either. But `apply_decision_rule` has no
   parameter slot for a third state. The spec never states what value gets
   passed to `apply_decision_rule`'s Boolean parameter — or whether
   `apply_decision_rule` is bypassed entirely — in the (foreseeable, not
   merely hypothetical) case where the real arm clears `>=4` survivors while
   the null arm's own, independently-computed filter leaves `<3` — i.e.
   exactly the scenario `invalidation_rules_v3_additions`' own `NOT-EVALUABLE`
   rule was written to cover, colliding with an interface that cannot
   represent it.

**Not live on this specific dispatch**: check (b) above independently
confirms the real-arm gate fails deterministically (0 < 4), so
`decision_rule_v3`'s `>=4`-survivors branch — and therefore this interface
question — is never reached by `RUN-SSIQ-a85692-c`. But this is a genuine,
foreseeable specification gap of the same shape `RT-PREFREEZE-EXP-SSIQ-a85692-v2.md`
rated **BLOCKING** for `coverage_widening_note` (PF-2 in that review) even
though that branch's exercise on the actual run was not certain in advance —
this campaign's own precedent is to close such gaps in the text before
freeze, not to defer them because the current data happens not to exercise
them. **Fix**: state explicitly (i) that `apply_decision_rule` is reused by
reference and add it to `required_artifacts_note`; (ii) what happens to the
Boolean parameter, or to the decision path generally, when
`c_null_label_control_failure` is `NOT-EVALUABLE` — e.g., treat it as forcing
`UNRESOLVED-BY-THIS-TEST` (never `DETECTED`, on the same non-improvisation
principle that a missing control cannot license a positive claim), stated as
a named branch rather than left to Executor discretion.

### PF-3 — [ADVISORY, not blocking] `pre_freeze_review.note`'s own worked-check range is accurate for the real arm only

"Trapped_fraction in `[0.72, 0.85]`" (spec text, `pre_freeze_review.note`)
correctly bounds the real arm's four values (0.7222–0.8511) but not the null
arm's (0.7037–0.8478; minimum below the quoted floor) — found while
independently checking both arms per the launching task's explicit
instruction. Does not change any qualitative conclusion (all eight values
across both arms exceed 0.5). One-line correction, not a defect.

### PF-4 — [MEDIUM, forward-looking, not blocking this dispatch] `c_null_label_comparison_v3`'s statistical power at n≤4 (n=3 at its own stated floor) is unaddressed and cannot be checked on this run's data

Per check (c) above: the null-arm comparison rule's bootstrap resamples at
most `n=4` (or, at its own stated minimum, `n=3`) prime-level points with
replacement — `4**4=256` or `3**3=27` distinct resample draws respectively —
an even coarser resampling distribution than the real arm's own CI, which
`RT-BATCH-005.md` Front 5 already flagged as intrinsically coarse. Whether
this specific design is a *sound* discriminator between "genuine graph-vs-label
artifact" and "insufficient power to say anything," in the spirit of
`RT-BATCH-005.md` Front 2b's finding against C-SEARCH-BIAS, cannot be settled
empirically here — PF-1 already establishes the branch never fires on this
data. Recorded now, per GD-9's own standing repair ("verify... now that it is
known to be possible, not assumed absent elsewhere just because it was found
once"), so it is not rediscovered as a surprise the first time a future run's
data actually reaches this branch.

---

## Required controls / checks before dispatch

- Explicit spec-text disclosure that this dispatch is expected, with high
  confidence independently reconfirmed here, to exercise only
  `c_null_label_comparison_v3`'s `NOT-EVALUABLE` path, and that the
  fit-and-bootstrap branch's correctness rests on static code review only
  for this batch (PF-1).
- A synthetic, `RUN-SSIQ-a85692-b`-independent self-test demonstrating
  `c_null_label_comparison_v3`'s fit-and-bootstrap branch actually executes
  end-to-end, added to `required_artifacts` (PF-1).
- `apply_decision_rule` named explicitly in `required_artifacts_note`'s diff
  list, and a stated, mechanical rule for what happens when
  `c_null_label_control_failure` is `NOT-EVALUABLE` at the point
  `apply_decision_rule` (or its equivalent ordering) would otherwise be
  invoked (PF-2).
- One-line correction to `pre_freeze_review.note`'s trapped-fraction range to
  cover both arms accurately (PF-3, advisory).

## Counterexample or mutation

The cheapest discriminating check for PF-1 is exactly the one performed above
at zero new compute: read `descent_metrics.per_prime[p].greedy_trapped_fraction`
for `p in {2437,3889,5737,7333}` (0.8374, 0.7222, 0.8201, 0.8511) **and**
`c_null_label.per_prime[p].greedy_trapped_fraction` for the same four primes
(0.8079, 0.7037, 0.7908, 0.8478) directly from `RUN-SSIQ-a85692-b/raw-result.json`
— both sets exceed 0.5, so both arms yield zero survivors under
`trapped_exclusion_filter_v3`, well below the null arm's own stated `>=3`
minimum for `c_null_label_comparison_v3` to run at all. A version of
`reanalyze_v3.py` that hard-codes `return {"c_null_label_control_failure":
"NOT-EVALUABLE"}` without ever calling `ols_loglog_fit`/`bootstrap_gap_ci`
would pass every check this draft specifies, on this exact data, with zero
observable difference from a fully correct implementation — a direct
falsifier of "the spec text makes it impossible to leave the fix as dead code
on this dispatch," which is the launching task's own item (a). For PF-2, the
cheapest discriminating check is reading `apply_decision_rule`'s signature
(`compute_delta_e.py` line 551, `c_null_label_control_failure` typed and used
as a bare Boolean, `line 567`'s `or` clause) against
`invalidation_rules_v3_additions`' explicit three-state requirement — no
code exists yet to reconcile them, and none is named to be written.

## Baseline comparison

Not applicable in the Pollard-rho/BSGS/specialized-baseline sense — this
remains a toy-scale, gradient-existence screen with `asymptotic_claim: null`
throughout (`H-SSIQ-36e970.asymptotic_claim_note`), correctly inherited
unchanged. The relevant baseline is this campaign's own instrument- and
fix-scrutiny discipline (GD-4 through GD-9): checks (b), (d), and (e) above
show this draft's *algorithmic* description is precise and its
already-known-outcome arithmetic reproduces exactly — a materially stronger
starting point than v1's original prose ever offered GD-9's predecessor
defects. What this review adds is the layer GD-9's own standing repair
implicitly assumes but does not yet name: a control's comparison logic can be
precisely specified, statically inspectable, and *still* provide zero runtime
falsifiability if the only data authorized to exercise it structurally cannot
reach the branch that matters — a different, and in some ways harder, problem
than "the code was never written."

## Heuristic challenges

`H-SSIQ-36e970.heuristic_assumptions` correctly remains empty
(gradient-existence screen, not a heuristic-conditional complexity claim) —
attacked and held, consistent with every prior review in this lineage. No
numbered heuristic requiring a random-model justification is implicated by
any finding in this review; every finding here is a control-comparison-logic
completeness/interface gap in new re-analysis code, not a claim about the
underlying arithmetic object.

## Cost model challenges

No asymptotic-cost claim is made anywhere (`asymptotic_claim: null`,
correctly), so the per-attempt-cost × inverse-success-probability review does
not apply in the complexity-claim sense. The 300s budget is realistic and
generously oversized relative to the arithmetic actually specified (check
(f)); no resource-bookkeeping concern found, unlike v2's own pre-freeze
review (which found a live budget-formula defect, PF-1 there). The live
concern in this draft is not resource cost but **evidentiary cost**: PF-1
means the amendment spends its (trivial) compute budget on a code path that,
by the amendment's own already-known numbers, will not exercise the one
thing it exists to validate, and the draft does not price that limitation
into its own claims about what BATCH-006 will have accomplished.

## Reduction and scope challenges

No scheme from the archived source's affected-vs-safe lists appears anywhere
in this amendment or its inherited hypothesis. `H-SSIQ-36e970.scope_ceiling`
(toy, inherited) is correctly stated and not exceeded by anything in the
draft's design. No scope-inflation concern found in the amendment's content;
the concerns found here (PF-1, PF-2) are completeness/interface gaps between
what the new re-analysis code is specified to do and what this run's own
already-known data will actually let it demonstrate — not scope widening.

## Proof architecture challenges

`H-SSIQ-36e970.proof_search_map.not_applicable_reason` remains correctly
reasoned and inherited unchanged — this is a direct instrument-level
gradient-existence screen, not a proof-oriented proposal, and nothing in this
amendment converts it into one. Attacked and held, same verdict as every
prior review in this lineage.

## Narrowest supported statement

Scoped to `experiments/EXP-SSIQ-a85692/specification_v3.yaml` as read at
draft status: the amendment's algorithmic description of both
`trapped_exclusion_filter_v3` and `c_null_label_comparison_v3` is precise
enough to be checked by direct code reading once implemented (check (a)), a
materially stronger starting point than the prose that let GD-8/GD-9 hide for
three batches, and its own worked-check arithmetic independently reproduces
exactly, in both arms (check (b), extending the draft's own real-arm-only
worked check). The `DATA-UNAVAILABLE/BLOCKED` gate is correctly scoped and
does not reopen the already-passed Phase −1 gate (check (d)); no other reused
control was found to share GD-9's dead-code defect (check (e)); the "zero new
search" framing is accurate (check (f)). It should not be frozen as currently
written: (1) `trapped_exclusion_filter_v3`'s own already-known numbers make
`c_null_label_comparison_v3`'s substantive fit-and-bootstrap branch
structurally unreachable on this dispatch's data, so this run cannot supply
runtime evidence that GD-9's fix actually works, and the draft neither
discloses this limitation nor requires any independent (synthetic) runtime
check of the branch it exists to add (PF-1); (2) `decision_rule_v3` depends on
`apply_decision_rule`, which `required_artifacts_note` never names, and whose
Boolean-only interface has no defined behavior for the `NOT-EVALUABLE` state
the same document requires be preserved — not live on this specific
dispatch (the real-arm gate fails deterministically first, independently
reconfirmed here), but a genuine, foreseeable specification gap this
campaign's own precedent treats as blocking regardless (PF-2). Neither
finding requires redesigning the amendment's mechanism, which is otherwise
sound and correctly targets already-collected data at zero new search cost.

## Next concrete action

Coordinator: before moving this draft to `status: approved` / setting
`frozen_at`, require the amendment text itself (not Executor discretion at
run time, and not left implicit in `H-SSIQ-36e970`'s separate record) to
state (1) that this dispatch is expected to exercise only
`c_null_label_comparison_v3`'s `NOT-EVALUABLE` path and that a
`RUN-SSIQ-a85692-b`-independent synthetic self-test is a required artifact
demonstrating the fit-and-bootstrap branch itself executes correctly (PF-1,
blocking); (2) that `apply_decision_rule` is named in `required_artifacts_note`
and a stated, mechanical rule for its Boolean parameter (or an explicit
bypass) when `c_null_label_control_failure` is `NOT-EVALUABLE` (PF-2,
blocking). PF-3 is a one-line advisory correction and PF-4 is a
forward-looking note for whichever future run first reaches
`c_null_label_comparison_v3`'s substantive branch; neither blocks this
dispatch.

## Overall verdict

**FREEZE-WITH-FIXES.** Blocking, in priority order:

1. **[BLOCKING]** PF-1 — disclose that this dispatch cannot runtime-validate
   `c_null_label_comparison_v3`'s fit-and-bootstrap branch given
   `trapped_exclusion_filter_v3`'s own already-known numbers, and add a
   synthetic self-test that does validate it, independent of
   `RUN-SSIQ-a85692-b`'s real data.
2. **[BLOCKING]** PF-2 — name `apply_decision_rule` in `required_artifacts_note`
   and state its behavior when fed a `NOT-EVALUABLE` `c_null_label_control_failure`.

PF-3 is advisory (one-line range correction) and PF-4 is a forward-looking,
non-blocking note for a future run.

```yaml
red_team_report:
  id: RT-PREFREEZE-EXP-SSIQ-a85692-v3
  task_id: NOT SUPPLIED IN THE LAUNCHING HANDOFF; recorded as unsupplied rather than fabricated, per AGENTS.md rule 9.
  claim_under_review: >-
    experiments/EXP-SSIQ-a85692/specification_v3.yaml (status: draft,
    hypothesis_id H-SSIQ-36e970): a versioned amendment to the frozen v2
    contract (specification_v2.yaml, frozen 14b56525) that (1) implements
    trapped_exclusion_filter_v3 (GD-8's fix) and (2) implements
    c_null_label_comparison_v3 (GD-9's fix), both as a pure re-analysis of
    RUN-SSIQ-a85692-b's already-collected raw-result.json, zero new search.
  objections:
    - "OBJ-1 [PF-1, BLOCKING]: c_null_label_comparison_v3's fit-and-bootstrap branch (the >=3-null-arm-primes path, the one substantive new computation the amendment adds to fix GD-9) is structurally unreachable on RUN-SSIQ-a85692-b's own data. Independently confirmed by reading descent_metrics.per_prime and c_null_label.per_prime directly (not merely the draft's own real-arm-only worked check): all 4 primes exceed the 0.5 trapped_fraction threshold in BOTH arms (real: 0.8374/0.7222/0.8201/0.8511; null: 0.8079/0.7037/0.7908/0.8478), so trapped_exclusion_filter_v3 leaves 0 survivors in both arms -- well below the null arm's own stated >=3 minimum for c_null_label_comparison_v3 to run at all. This means a correctly-implemented fit-and-bootstrap branch and a stub that unconditionally reports NOT-EVALUABLE without ever calling ols_loglog_fit/bootstrap_gap_ci are indistinguishable in this run's own artifacts -- a harder, non-grep-detectable variant of GD-9's own failure mode. The draft neither discloses this limitation nor requires any independent runtime check of the branch it exists to add, and its framing ('wires C-NULL-LABEL's actual comparison logic') overstates what this specific dispatch can demonstrate."
    - "OBJ-2 [PF-2, BLOCKING]: decision_rule_v3 requires re-invoking apply_decision_rule's ordering (Phase 0 -> Phase -1 gate -> control-failure check including c_null_label_control_failure -> CI sign) in the (on this data, unreached) >=4-real-arm-survivors branch, but required_artifacts_note never names apply_decision_rule anywhere in its diff list, and apply_decision_rule's actual signature (compute_delta_e.py line 551) takes c_null_label_control_failure as a plain Boolean with no slot for the NOT-EVALUABLE third state invalidation_rules_v3_additions explicitly requires be preserved and never defaulted to True or False. Not live on this specific dispatch (check (b) independently confirms the real-arm gate fails deterministically, 0<4, before this interface would be reached), but a genuine, foreseeable specification gap of the same shape RT-PREFREEZE-EXP-SSIQ-a85692-v2.md rated BLOCKING for coverage_widening_note (that report's PF-2) even though that branch's exercise was likewise not certain on the data at hand."
    - "OBJ-3 [PF-3, ADVISORY]: pre_freeze_review.note's own worked-check range ('trapped_fraction in [0.72, 0.85]') is accurate for the real arm's four primes (0.7222-0.8511) but understates the null arm's minimum (0.7037 at prime 3889, below the quoted 0.72 floor) -- found while independently checking both arms per the launching task's own instruction. Does not change the qualitative conclusion (all values in both arms exceed 0.5)."
    - "OBJ-4 [PF-4, MEDIUM, forward-looking, not blocking this dispatch]: c_null_label_comparison_v3's own statistical power at n<=4 (n=3 at its own stated floor) for the bootstrap resampling unit is unaddressed and structurally cannot be checked on this run's data (PF-1 already shows the branch never fires) -- at n=3 the bootstrap has at most 3**3=27 distinct resample draws, an even coarser distribution than the real arm's own CI, which RT-BATCH-005.md Front 5 already flagged as intrinsically coarse. Recorded now per GD-9's own standing repair so it is not rediscovered as a surprise the first time a future run's data actually reaches this branch."
    - "OBJ-5 [check (c), not a defect, informational]: the comparison rule mirrors apply_decision_rule's own pre-existing DETECTED criterion (m_gap_ci_lo > 0.0) rather than inventing a new threshold, a materially more principled design than C-SEARCH-BIAS's absolute-floor clause. The pre-registration hedge's literal wording ('before looking at the numbers... beyond what BATCH-005's own committed artifacts already disclosed') concedes the drafter had access to c_null_label.per_prime's actual values via this campaign's own full-read requirement, and could trivially have known this rule would never be exercised on this data regardless of wording -- this reduces but does not fully eliminate the reverse-engineering concern the launching task raised; net assessment is not a violation, given the rule's content (reused criterion, not a new number) shows no hallmark of curve-fitting."
  required_controls:
    - "Explicit spec-text disclosure that this dispatch is expected to exercise only c_null_label_comparison_v3's NOT-EVALUABLE path, given trapped_exclusion_filter_v3's own already-known numbers (PF-1)."
    - "A synthetic, RUN-SSIQ-a85692-b-independent self-test (a required artifact) demonstrating c_null_label_comparison_v3's fit-and-bootstrap branch actually executes end-to-end and produces the expected numbers (PF-1)."
    - "apply_decision_rule named explicitly in required_artifacts_note's diff list, with a stated, mechanical rule for its Boolean c_null_label_control_failure parameter (or an explicit bypass/named branch) when the value is NOT-EVALUABLE (PF-2)."
  counterexample_or_mutation: >-
    Read descent_metrics.per_prime[p].greedy_trapped_fraction for
    p in {2437,3889,5737,7333} (0.8374, 0.7222, 0.8201, 0.8511) AND
    c_null_label.per_prime[p].greedy_trapped_fraction for the same four
    primes (0.8079, 0.7037, 0.7908, 0.8478) directly from
    RUN-SSIQ-a85692-b/raw-result.json -- both sets exceed 0.5, so both arms
    yield zero survivors under trapped_exclusion_filter_v3, below the null
    arm's own stated >=3 minimum. A reanalyze_v3.py that hard-codes
    NOT-EVALUABLE without ever calling ols_loglog_fit/bootstrap_gap_ci would
    pass every check this draft specifies, on this exact data, with zero
    observable difference from a fully correct implementation -- a direct
    falsifier of "the spec text makes it impossible to leave the fix as dead
    code on this dispatch." For PF-2, reading apply_decision_rule's signature
    (compute_delta_e.py line 551, a bare Boolean) against
    invalidation_rules_v3_additions' explicit three-state NOT-EVALUABLE
    requirement shows no code exists yet, and none is named to be written,
    to reconcile them.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/specialized-baseline sense
    (toy-scale gradient-existence screen, asymptotic_claim null throughout,
    correctly inherited). The relevant baseline is this campaign's own
    instrument- and fix-scrutiny discipline (GD-4 through GD-9): this draft's
    algorithmic description is precise and its worked-check arithmetic
    reproduces exactly in both arms, a materially stronger starting point
    than the prose that let GD-8/GD-9 hide for three batches. This review
    adds a layer GD-9's own standing repair implicitly assumes but does not
    yet name: precise, statically-inspectable comparison logic can still
    provide zero runtime falsifiability if the only authorized data cannot
    reach the branch that matters.
  heuristic_challenges:
    - "H-SSIQ-36e970.heuristic_assumptions correctly remains empty (gradient-existence screen, not a heuristic-conditional claim) -- attacked and held. Every finding here is a control-comparison-logic completeness/interface gap in new re-analysis code, not a claim about the underlying arithmetic object."
  cost_model_challenges:
    - "No asymptotic-cost claim is made (asymptotic_claim: null, correctly); the per-attempt x inverse-success-probability review does not apply in the complexity-claim sense."
    - "The 300s budget is realistic and generously oversized relative to the specified arithmetic (JSON read, filter over <=5 primes, two OLS fits and one 2000-resample bootstrap on <=4 points) -- no resource-bookkeeping defect found, unlike v2's own pre-freeze review."
    - "The live concern is evidentiary, not resource cost: PF-1 means the amendment's compute is spent on a path that, by its own already-known numbers, cannot exercise the one thing it exists to validate, and the draft does not price that limitation into its own claims about what BATCH-006 will have accomplished."
  reduction_and_scope_challenges:
    - "No scheme from the archived source's affected-vs-safe lists appears anywhere in this amendment or its inherited hypothesis; H-SSIQ-36e970.scope_ceiling (toy, inherited) correctly stated and not exceeded."
    - "PF-1/PF-2 are completeness/interface gaps between what the new re-analysis code is specified to do and what this run's own already-known data will let it demonstrate, not scope widening."
  proof_architecture_challenges:
    - "H-SSIQ-36e970.proof_search_map.not_applicable_reason correctly reasoned and inherited unchanged -- a direct instrument-level gradient-existence screen, not a proof-oriented proposal; nothing in this amendment converts it into one. Attacked and held."
  narrowest_supported_statement: >-
    Scoped to experiments/EXP-SSIQ-a85692/specification_v3.yaml as read at
    draft status: the amendment's algorithmic description of both fixes is
    precise and its worked-check arithmetic reproduces exactly, independently
    extended here to both arms (check (b)); the new gate correctly does not
    reopen the already-passed Phase -1 gate (check (d)); no other reused
    control shares GD-9's dead-code defect (check (e)); the "zero new search"
    framing is accurate (check (f)). It should NOT be frozen as currently
    written: trapped_exclusion_filter_v3's own already-known numbers make
    c_null_label_comparison_v3's substantive fit-and-bootstrap branch
    structurally unreachable on this dispatch, so this run cannot supply
    runtime evidence that GD-9's fix actually works, and the draft neither
    discloses this nor requires an independent runtime check of the branch it
    exists to add (PF-1); separately, decision_rule_v3 depends on
    apply_decision_rule, which required_artifacts_note never names, and whose
    Boolean interface has no defined behavior for the NOT-EVALUABLE state the
    same document requires be preserved (PF-2, not live on this dispatch but
    a genuine foreseeable gap). Neither requires redesigning the amendment's
    mechanism, which is otherwise sound and correctly targets already-
    collected data at zero new search cost.
  next_concrete_action: >-
    Coordinator: before status: approved / frozen_at, require the amendment
    text itself to state (1) that this dispatch is expected to exercise only
    c_null_label_comparison_v3's NOT-EVALUABLE path and add a
    RUN-SSIQ-a85692-b-independent synthetic self-test as a required artifact
    validating the fit-and-bootstrap branch (PF-1, blocking); (2) name
    apply_decision_rule in required_artifacts_note and state its behavior
    under a NOT-EVALUABLE c_null_label_control_failure (PF-2, blocking). PF-3
    is a one-line advisory correction; PF-4 is a forward-looking note for a
    future run that does reach the branch.
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v3.md
  files_written_outside_scope: []
  raw_artifacts_modified: 0
  ledger_touched: false
  record_statuses_changed: 0
  compute_performed: >-
    Arithmetic only, entirely on numbers already committed in
    experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json
    (independent re-derivation of trapped_exclusion_filter_v3's survivor set
    for BOTH the real arm and the null arm, extending the draft's own
    real-arm-only worked check) plus direct reading (not executing) of
    specification_v3.yaml, specification_v2.yaml, compute_delta_e.py,
    compute_delta_e_v2.py, and descent_hitting_time.py to trace
    trapped_exclusion_filter_v3, c_null_label_comparison_v3,
    apply_decision_rule, and every other named control (C-BOUND-CHECK,
    C-CONNECTIVITY, C-DEGSEQ, C-EDGELIST, C-SEED, C-REPRO) against the
    frozen/draft spec text. No code executed, no graph built, no search run,
    no new measurement taken.
  commits_made: 0
  commit_note: >-
    No commit made. Per AGENTS.md "Durable research commits," the
    Coordinator's ledger/snapshot archive task commits this report; it is not
    durable until that archive exists. Per write_scope, this task modified
    nothing outside
    coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/RT-PREFREEZE-EXP-SSIQ-a85692-v3.md
    -- experiments/EXP-SSIQ-a85692/ (including specification_v3.yaml itself)
    and every ledger record are untouched.
  verdict: FREEZE-WITH-FIXES
```
