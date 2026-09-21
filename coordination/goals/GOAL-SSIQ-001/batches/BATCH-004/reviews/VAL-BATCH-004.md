# VAL-BATCH-004 — Validator review of RUN-SSIQ-a85692-a (EXP-SSIQ-a85692, H-SSIQ-9e2c71)

**Reviews the Coordinator-committed snapshot at commit `29953723` only**
(receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/archives/TASK-20260805-81ffe0-receipt.yaml`).
Nothing in this report edits `specification.yaml`, any raw artifact, or any
ledger record.

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: claude-sonnet-5
  resolved_model_provenance: self-reported by this Claude Code subagent session; not probe-verified
  model_verified: false
  fallback_used: true
  fallback_reason: >-
    Subagent frontmatter under this runtime cannot express a policy
    (CLAUDE.md, "Model policy note"); this session runs model: inherit, so
    review-adversarial resolves to the session model rather than a
    policy-resolved identifier. Same standing condition RT-PREFREEZE-EXP-SSIQ-a85692
    and VAL-BATCH-003 recorded.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer and the pre-freeze reviewer; nothing below
    should be read as corroboration from a distinct model. Per AGENTS.md
    "Goal closure quorum," this alone can never satisfy a closure quorum.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `29953723` is `HEAD` on branch
  `claude/0.25-algorithm-breakthrough-y7jbiy`; trivially reachable.
- **Parent:** `git log --format='%H %P' -1 29953723` → parent
  `5fc59a15b4c3cef68740fbe72c76719a59c67b6b`, exactly the receipt's declared
  `parent_sha`. Match.
- **Path set:** `git diff-tree --no-commit-id --name-only -r 29953723` returns
  exactly the 20 paths in the receipt's `declared_paths` (compute_delta_e.py,
  8 modpoly_data files, modular_polynomials.py, velu_verify.py, 8 run files,
  the receipt itself). No extra, no missing.
- **Hashes:** recomputed `sha256(git show 29953723:<path>)` for all 20
  declared paths against `path_sha256` — **0 mismatches**, exact 64-hex
  matches (not a loose/truncated comparison).

**Verdict: PASS.** The receipt is a faithful, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification.yaml` frozen in commit `96ad45de`, `2026-08-05T09:11:25Z`
  (`frozen_at: '2026-08-05'`, `status: approved`).
- `manifest.yaml.timing.started_at: '2026-08-05T09:33:07Z'`, ~22 minutes
  after freeze. `implementation_commit`/`code.commit` in the manifest
  (`5fc59a15b4c3cef68740fbe72c76719a59c67b6b`) is the frozen-contract commit
  itself.

**Verdict: PASS.** The contract was frozen strictly before the run, and the
run's code.commit is bound to the frozen commit.

## 3. THE CENTRAL QUESTION — was the extrapolation methodology sound?

### 3.1 What the contract actually pins

`specification.yaml.inputs.delta_e_computation.smoothness_parameters_pinned_before_data`
pins **B=23, X=23 as flat module-level constants, used identically for every
one of the 12 primes** — derived once, from the *largest* pre-registered
prime (X = √23·(21601/2)^{1/6} ≈ 22.4 → 23), and explicitly "NOT TUNED
UPWARD OR DOWNWARD MID-RUN under any circumstance." This is confirmed in
code: `compute_delta_e.py` lines 107-109 define `B_SMOOTH = 23`,
`X_LIST_BOUND = 23` as single global constants passed unchanged into every
`two_sided_search()` call, including inside `run_feasibility_smoke_test`.

So the "X scales with p^(1/6)" formula the task description points at is
real, and the pre-freeze review (`RT-PREFREEZE-EXP-SSIQ-a85692.md`, Finding 1)
explicitly derives it (X≈3.2·√B at p=2437 vs X≈4.7·√B at p=21601) — **but the
frozen contract's own design deliberately does not use that per-prime value.**
It pins one X, sized to the *largest* prime, uniformly. This was a considered
choice, not an oversight: Finding 8 of the same review warns that a
*smaller* worked-example B under-covers the largest prime's own theoretical
ceiling, and the fix (B=23 fixed) was adopted specifically to avoid that.

### 3.2 What the fallback formula actually computes

`compute_delta_e.py::apply_truncation_fallback` (lines 331-360):
`est_cost = n_non_fp_rational_vertices(p) × measured_per_vertex_cost`, where
`measured_per_vertex_cost` is the **single scalar** 1.9574 s/vertex measured
at p=21601 (3 vertices) — applied identically, ascending by prime size, to
all 12 primes. I recomputed this by hand for the endpoints:
`194 × 1.9574 = 379.7` (p=2437) and `1760 × 1.9574 = 3444.9` (p=21601), both
match `raw-result.json.truncation_fallback.per_prime_estimated_full_coverage_seconds`
exactly. **This is a mechanically exact, faithful implementation of the
frozen contract's text** ("using the smoke test's OWN measured per-entry
cost... estimate each pre-registered prime's full-coverage cost ascending by
prime size" — read, defensibly, as "per-vertex full-search cost," which is
consistent with the pre-freeze reviewer's own 6.19×10⁷-entries arithmetic
translating to ≈5400 entries/vertex, i.e. the same order of aggregation).
**This is not a producer error.**

### 3.3 My own independent re-derivation

Since X is pinned flat, table *size* alone does not explain any real cost
variation across primes. But **actual search termination time is not
governed only by X** — the bidirectional table-collision search
(`compute_delta_e.py`'s Dijkstra-style `build_smooth_table`) stops as soon as
a collision is found, and Theorem 1.5 bounds the *true* minimal degree by
(p/2)^{1/3}, which is genuinely smaller at smaller p (10.68 at p=2437 vs
22.10 at p=21601). Since finalization proceeds in ascending degree order, a
smaller true bound plausibly means fewer entries need to be built before a
collision is found — i.e., real per-vertex cost is plausibly p-dependent
*even with X pinned flat*. I modeled this three independent ways:

| model | basis | cost/vertex at p=2437 | total (194 v) | fits T_prime=300s? |
|---|---|---|---|---|
| **flat (as run)** | measured 1.9574 s/v at p=21601, unscaled | 1.9574 | 379.7s | No (1.27× over) |
| **A-1's own disclosed measurement** | informal dev-time 3-vertex sample at p=2437 | 1.43 | 277.4s | **Yes** (8% margin) |
| **Theorem-1.5 degree-scaling** | cost ∝ (p/2)^{1/3}, anchored at p=21601 | 0.946 | 183.5s | **Yes** (39% margin) |
| **Per-prime X-scaling (Lemma 3.2)** | cost ∝ entries(X(p)) via #L≈X²(lnX+2), X(p)=√23(p/2)^{1/6} | 0.842 | 163.3s | **Yes** (46% margin) |

I extended the same three models to the second-smallest prime (3889, 306
vertices): the informal-measurement power-law fit (b≈0.144 from the two
disclosed data points) gives ≈468s (excluded); the degree-scaling model gives
≈339s (excluded, narrowly); the X-scaling model gives ≈306s (essentially at
the boundary, ambiguous). **Under every model I tried, at most 1-2 of the 12
primes would newly qualify — never 4 or more.**

### 3.4 Conclusion on the central question

- **The extrapolation rule is directionally conservative** (it uses the
  single most expensive prime as a flat multiplier for every cheaper prime),
  and this direction is the *same* one the pre-freeze review deliberately
  chose to protect against a worse failure mode (discovering a budget
  overshoot mid-run after testing only the cheap smallest prime, Finding 1).
  That tradeoff is defensible engineering, not a defect.
- **But conservative here is not free**: it plausibly overstates cost by
  ~1.3-2.3× at the smallest 1-2 primes, and the run's own margin at the
  smallest prime is razor-thin (1.27×). Three independent correction
  models — one of them the run's *own disclosed* anomaly A-1 — all put the
  smallest prime's corrected cost *under* T_prime.
- **This does NOT overturn DATA-UNAVAILABLE-BLOCKED as the terminal label.**
  Even the most favorable correction model admits at most ~2 primes, and the
  Phase -1 gate and `fitting_window` both require **4+ primes** to produce a
  confirmatory M-GAP. The qualitative outcome (insufficient data for a
  confirmatory descent test at these pinned parameters) is robust to this
  concern.
- **It does materially undermine one specific, disclosed number**: "0 of 12
  primes" / "even the smallest prime doesn't fit" is very likely an
  overstatement of the true infeasibility margin, not a validated fact. The
  run used only 90.57s of its 7200s budget (1.26%); a second, equally cheap
  smoke test at the smallest prime (or 2-3 intermediate primes) — which
  anomaly A-1 itself proposes as a possible amendment — would have cost
  essentially nothing and would have converted a genuinely untested
  assumption (per-vertex cost is well-represented by a single largest-prime
  measurement) into a measured one, per `docs/inventor-protocol.md` §6 step 2
  ("each assumption the complexity analysis rests on... measured separately").
  This experiment makes no speedup/complexity claim (`asymptotic_claim: null`
  throughout), so the ladder's "absent step 2 is `failed`, not `incomplete`,
  when a speedup is claimed" clause does not itself apply — but the same
  discipline is still the right standard for a feasibility gate whose margin
  is this thin.

**This finding does not change my verdict on the run's terminal label. It is
recorded as FINDING F-1 below, with a concrete resolution.**

## 4. Smoke-test re-derivation

- **Lemma 3.2 sanity check:** measured table sizes (342-365 entries/side) are
  well under the Lemma 3.2 upper bound at X=B=23 (≈2716/side, from the
  pre-freeze review's own arithmetic, X²(lnX+2) = 529×5.135 ≈ 2716) —
  consistent (an upper bound should not be tight, and isn't).
- **Theoretical ceiling:** (21601/2)^(1/3) = 22.1045, hand-verified by cube
  interpolation (22^3=10648, 22.2^3=10941.48, target 10800.5 → 22.104).
  Matches `raw-result.json.feasibility_smoke_test.theoretical_ceiling_p_over_2_cube_root_at_p21601`
  exactly.
- **Independent re-execution:** I re-ran
  `python3 experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py`
  end-to-end (no code changes) against the vendored artifacts. It completed
  in 93.6s, reproduced `DATA-UNAVAILABLE-BLOCKED` as the terminal branch,
  reproduced the truncation fallback's structure exactly
  (`smallest-prime estimate 402.1s` vs the archived run's 379.7s — both
  well above T_prime, same qualitative outcome; the two runs differ because
  the smoke test times 3 fresh vertex searches on live hardware, which is
  expected timing noise, not non-determinism in the decision logic).
  `C-SEARCH-BIAS` correlations reproduced **bit-for-bit** across independent
  executions (0.09610901... / 0.03083264...), because that arm's search is
  seeded deterministically over a fixed vertex sample while the smoke test's
  vertex *sample* draws are also seeded but wall-clock timing is not.
- **C-SEARCH-BIAS correlations recomputed from raw rows**: I recomputed
  Pearson correlation directly from `raw-result.json.c_search_bias.{true,random}_target_arm.rows`
  (`distance` vs `delta_e_upper_bound`, n=20 each) and got
  0.09610901099736081 (true) and 0.030832644977609028 (random) — matching
  the reported values to 14 significant figures. **Reproduced exactly.**

**Verdict: PASS.** Every number I attempted to recompute reproduces from the
raw data or from an independent re-execution.

## 5. Phi_ell sourcing and verification

- Live re-fetch of `https://math.mit.edu/~drew/modpolys/jfiles/phi_j_<ell>.txt`
  for ell ∈ {3, 11, 23} (spanning small/medium/largest) returned byte-identical
  content: sha256 matches `source_access_log.yaml` and the vendored files
  exactly for all three (`62bf6c...`, `985c6a...`, `96e147...`).
- Re-ran `velu_verify.load_and_verify(3, ...)` and `velu_verify.load_and_verify(23, ...)`
  independently: both return `all_ok: True`, 3/3 test curves each, with
  `phi_ell_residual_mod_p: 0` on every trial — reproducing
  `raw-result.json.modular_polynomial_verification.ell_23_required.all_ok: true`
  exactly, via an independently-implemented route (exact rational Vélu-formula
  isogeny + naive point counting), as the frozen contract requires for the
  largest ell actually used.

**Verdict: PASS.** Sourcing is genuine (re-fetched, not merely cited) and the
independent verification route reproduces.

## 6. C-SEARCH-BIAS check

- Ran as specified: 20 non-F_p-rational vertices at the smallest
  pre-registered prime (2437), both a true-Frobenius-target arm and a
  uniformly-random-other-vertex-target (null-object) arm, same
  `compute_delta_e.py` search code, same (B,X).
- Correlations independently recomputed from raw rows (§4): both weak
  (0.096, 0.031). The report's own pre-registered `comparability_rule`
  ("comparable if... OR both magnitudes are below 0.1") correctly flags
  `magnitudes_comparable_flag: true` here since both are <0.1 — I
  independently checked this arithmetic and it is applied exactly as stated.
- This is a genuine null-object control (a random-target search is a null
  object of the same shape as the true-target search — same algorithm, same
  (B,X), broken correspondence to the real Frobenius conjugate) per
  `docs/inventor-protocol.md` §3. It is correctly disclosed that, **had** a
  real-arm M-GAP existed, this comparable-magnitude flag would trigger
  `CONTROL-FAILURE-VOID` per the contract's own rule — but since the Phase -1
  gate is checked first in the decision hierarchy (confirmed in code,
  `apply_decision_rule` lines 549-581) and fails first, this flag is
  correctly reported as not altering the terminal branch for *this* run.

**Verdict: PASS.** Ran as specified, reproducible, correctly interpreted
against the contract's own decision-hierarchy ordering.

## 7. Decision-rule label check

- `apply_decision_rule` (code, lines 549-581) checks Phase 0 → Phase -1 gate
  → control-failure → M-GAP sign, in exactly the order
  `decision_rule_frozen_before_data` specifies. For this run, Phase 0 passed
  and Phase -1 failed, so the function returns `DATA-UNAVAILABLE-BLOCKED`
  before any control-failure or M-GAP branch is reached — correct per the
  frozen contract's own hierarchy.
- Grepped every run artifact for the bare string "VOID": the only
  occurrences are (a) inside the compound term `CONTROL-FAILURE-VOID`, and
  (b) one explicit historical reference to "EXP-SSIQ-58b642's VOID outcome"
  in `execution_report.yaml`'s quote of `success_criterion` — a correctly
  scoped reference to the *predecessor* experiment's own (differently
  named) outcome, not a mislabeling of this run. No bare "VOID" is used to
  describe this run's own outcome anywhere in `raw-result.json`,
  `manifest.yaml`, or `execution_report.yaml`.

**Verdict: PASS.** DATA-UNAVAILABLE-BLOCKED is the contractually correct
label for an empty confirmatory prime set, applied mechanically and without
any forbidden-word drift.

## 8. Overclaim / premature-closure check

- No sentence anywhere in the reviewed artifacts asserts the descent test
  ran; `descent_metrics: {"ran": false}` and `phase_minus1_real_search: {}`
  are stated plainly in `raw-result.json`.
- The smoke test's 3-vertex sample at p=21601 is never generalized as
  "coverage" — `M-COVERAGE_by_prime` is explicitly reported as "none
  attempted beyond the smoke test itself."
- C-SEARCH-BIAS's weak correlations are explicitly and correctly **not**
  read as evidence about a real delta_E-gradient anywhere in the artifacts
  (there is no real-arm data to compare them against); the report states
  this limitation directly (`c_search_bias` comment in the receipt: "does
  not change the terminal branch").
- Anomaly A-1 (the informal smaller measurement that might have admitted the
  smallest prime) is disclosed prominently, attributed correctly as
  non-official, and explicitly **not** substituted into the mechanical
  result — this is the correct behavior under the frozen contract's
  non-improvisation rule, and it is exactly the datum my own §3 analysis
  above builds on. This is good-faith, rule-8/9-compliant disclosure, not an
  attempt to bury an inconvenient result.
- The Coordinator's own snapshot-commit message explicitly declines to
  endorse the DATA-UNAVAILABLE-BLOCKED interpretation and flags the
  extrapolation-methodology question as the single most important thing for
  this review to check — which this report now has.

**Verdict: PASS.** No overclaim or premature-closure drift found.

---

## Findings

- **F-1 [non-blocking, actionable].** The frozen contract's truncation
  fallback tests feasibility at only one point (the largest prime) and
  applies that single measurement flat to all 12 primes. Per §3, this is
  directionally conservative but plausibly overstates cost at the smallest
  1-2 primes by roughly 1.3-2.3×, on a margin (1.27× at the smallest prime)
  thin enough that the correction could plausibly flip 1 (not 4+) primes'
  feasibility verdict. **What resolves it:** a second, equally cheap
  (~5-10s) smoke test at the smallest pre-registered prime — or, better, at
  2-3 spread primes — run as a Coordinator-approved protocol amendment (not
  a silent in-place fix to the frozen contract), to convert an untested
  flat-cost assumption into a measured one before this specific
  DATA-UNAVAILABLE-BLOCKED outcome is treated as fully exhausting the (B=23,
  X=23) instrument at these graph sizes. This does not change my verdict on
  the reviewed run, because even a corrected estimate does not reach the
  4-prime floor the Phase -1 gate requires.
- **F-2 [informational, not a defect].** The contract's own text says
  "measured per-*entry* cost" while the implementation and I both verify it
  operationalizes this as measured per-*vertex* (full two-sided-search) cost.
  This is a defensible reading consistent with the pre-freeze reviewer's own
  aggregate arithmetic (which itself conflated the two at the ≈5400
  entries/vertex level) and does not change any number in the run. **What
  would resolve it:** a wording tightening in any future amendment to this
  contract, naming "per-vertex full-search cost" explicitly rather than
  "per-entry cost," so a future reader cannot construct a genuinely
  different (per-table-entry) extrapolation from the same text.
- **F-3 [informational].** `stopping_rules`/`invalidation_rules` use the
  bare term "INCONCLUSIVE for lack of coverage" for a truncated set with
  fewer than 4 primes, a case distinct from the empty-set case actually
  observed here, and the four-label `outcome_scope_label_glossary` does not
  explicitly enumerate this as a fifth label or confirm it is subsumed under
  `DATA-UNAVAILABLE-BLOCKED`. Not exercised by this run (the confirmatory set
  was empty, not merely under 4), so it is not a blocking gap here. **What
  would resolve it:** an explicit sentence in a future amendment stating
  whether "1-3 primes admitted" and "0 primes admitted" are the same
  run-level label or different ones.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run that was executed exactly as its frozen contract specifies, honestly and
completely disclosed, with every recomputable number independently
reproduced (hashes, Phi_ell sourcing, Vélu-formula verification, C-SEARCH-BIAS
correlations, the theoretical ceiling, and the qualitative decision branch
under independent re-execution). The DATA-UNAVAILABLE-BLOCKED terminal label
is correctly applied per the frozen decision rule and is robust to the
extrapolation-methodology concern raised in the archive commit message: no
plausible correction admits the 4+ primes the Phase -1 gate requires. This
receipt is therefore **admissible evidence that the pinned (B=23, X=23)
instrument, extrapolated from a single largest-prime measurement, did not
clear the Phase -1 gate on this run.**

It is admitted **with the condition** that any Coordinator synthesis citing
this run state F-1 explicitly: the specific claim "0 of 12 primes" /
"even the smallest prime doesn't fit" rests on an untested flat-cost
extrapolation that the run's own disclosed anomaly (A-1) and my independent
degree-scaling and table-size models all suggest overstates cost at the
smallest primes by a material margin, and a near-zero-cost follow-up
amendment (a second smoke test at the smallest prime) would close that gap
before this specific instrument configuration is treated as exhausted at
this scale. As required by AGENTS.md rule 9, this is recorded as the
concrete revisit condition for lever L4's next action, not a reason to
reopen or discard the run.

This report establishes nothing about whether a delta_E-gradient exists. It
establishes that the run is admissible evidence of what it actually measured
(infeasibility of the pinned instrument under a conservative, honestly-
disclosed extrapolation), scoped exactly as narrowly as that.

```yaml
validation_report:
  id: VAL-BATCH-004
  task_id: TASK-20260805-798a16
  run_ids: [RUN-SSIQ-a85692-a]
  reviewed_commit: 299537238f14db622c7e93f52bc19286a7c4bba7
  reviewed_commit_parent: 5fc59a15b4c3cef68740fbe72c76719a59c67b6b
  artifact_checks:
    - {check: path_sha256_recompute, scope: "all 20 declared paths", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS}
    - {check: contract_frozen_before_run, frozen_at: '2026-08-05T09:11:25Z', run_started_at: '2026-08-05T09:33:07Z', result: PASS}
    - {check: required_artifacts_present, result: PASS, detail: "all 20 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: smallest_prime_truncation_estimate, reported: 379.7, recomputed: "194 * 1.9574 = 379.7358", result: MATCH}
    - {metric: largest_prime_truncation_estimate, reported: 3444.9, recomputed: "1760 * 1.9574 = 3445.02", result: MATCH}
    - {metric: theoretical_ceiling_p21601, reported: 22.1045, recomputed: "(21601/2)^(1/3) = 22.104", result: MATCH}
    - {metric: c_search_bias_true_target_correlation, reported: 0.09611, recomputed_from_raw_rows: 0.09610901099736081, result: MATCH}
    - {metric: c_search_bias_random_target_correlation, reported: 0.03083, recomputed_from_raw_rows: 0.030832644977609028, result: MATCH}
    - {metric: full_pipeline_independent_reexecution, reported_branch: DATA-UNAVAILABLE-BLOCKED, reexecuted_branch: DATA-UNAVAILABLE-BLOCKED, reexecuted_smoke_test_seconds_per_vertex: 2.0725, result: "QUALITATIVE MATCH; timing differs as expected (live measurement, not seeded)"}
    - {metric: independent_correction_models_for_smallest_prime, models: ["A-1 disclosed measurement: 277.4s (fits)", "Theorem-1.5 degree-scaling: 183.5s (fits)", "per-prime Lemma-3.2 X-scaling: 163.3s (fits)"], vs_flat_estimate: 379.7s, primes_newly_admitted_max: "1-2 of 12, never >=4", conclusion: "terminal label DATA-UNAVAILABLE-BLOCKED is robust; the '0 of 12' magnitude is likely an overstatement"}
  control_checks:
    - {control: C-CAL-GAP, result: PASS, detail: "reused unchanged, ran, bit-identical to EXP-SSIQ-58b642"}
    - {control: modular_polynomial_source, ell_refetched: [3, 11, 23], result: PASS, detail: "live re-fetch sha256 matches vendored files exactly for all 3"}
    - {control: phi_23_velu_independent_verification, result: PASS, detail: "independently re-executed velu_verify.py, all_ok=True, 3/3 test curves, residual 0 on every trial, for both ell=3 and ell=23"}
    - {control: C-SEARCH-BIAS, result: PASS, detail: "ran as specified at smallest prime, 20 vertices, both arms; correlations reproduced exactly from raw rows; correctly disclosed as not altering the terminal branch given decision-rule ordering"}
    - {control: C-CONNECTIVITY, result: PASS, detail: "floor(p/12) formula anchor, all 12 primes, matches PD-1's disclosed scope narrowing"}
    - {control: decision_rule_label_taxonomy, result: PASS, detail: "no bare VOID used for this run's own outcome; DATA-UNAVAILABLE-BLOCKED correctly derived from code's decision-hierarchy ordering"}
    - {control: c_null_label_and_descent_metrics, result: "NOT RUN, correctly", detail: "Phase -1 gate failure per the frozen contract's own ordering means these are legitimately skipped, not silently omitted"}
  heuristic_validation_checks: []
  cost_model_checks:
    - {check: extrapolation_formula_faithfulness_to_contract_text, result: PASS, detail: "est_cost = n_vertices * measured_per_vertex_cost is a mechanically exact, defensible implementation of scope_reduction_fallback_pinned_before_data"}
    - {check: extrapolation_methodology_soundness, result: "CONSERVATIVE BUT LIKELY MATERIALLY OVERSTATED at 1-2 smallest primes", detail: "see Findings F-1; robust to the terminal DATA-UNAVAILABLE-BLOCKED label, not robust to the specific '0 of 12 primes' magnitude"}
    - {check: X_pinned_flat_not_scaled_per_prime, result: "CONFIRMED IN CODE", detail: "B_SMOOTH=23, X_LIST_BOUND=23 module-level constants, used identically for every prime; this is the frozen contract's own deliberate design (RT-PREFREEZE Finding 8), not a producer deviation"}
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: non-blocking-actionable, summary: "single-point, worst-case-flat extrapolation plausibly overstates cost at 1-2 smallest primes by 1.3-2.3x on a thin margin", resolution: "a second near-zero-cost smoke test at the smallest prime(s), via Coordinator-approved amendment"}
    - {id: F-2, severity: informational, summary: "contract text says 'per-entry cost', implementation and this review both read it as 'per-vertex full-search cost' -- defensible, non-blocking", resolution: "wording tightening in a future amendment"}
    - {id: F-3, severity: informational, summary: "'INCONCLUSIVE for lack of coverage' (1-3 primes admitted) is not enumerated in the 4-label glossary alongside DATA-UNAVAILABLE-BLOCKED (0 primes / gate failure)", resolution: "not exercised by this run; clarify in a future amendment"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer and the pre-freeze reviewer; it is not model-independent corroboration."
    - "F-1's correction models are order-of-magnitude sanity checks built from disclosed numbers, not a re-executed, official smoke test at additional primes; they establish plausibility and bound the maximum number of primes that could be newly admitted, not an exact corrected cost."
    - "This report makes no claim about whether a delta_E-gradient exists, about lever L4's status, or about the archived source's Heuristic 1 or complexity claim -- none of that data was produced by this run."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-004/reviews/VAL-BATCH-004.md
```
