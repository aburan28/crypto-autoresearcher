# VAL-BATCH-005 — Validator review of RUN-SSIQ-a85692-b (EXP-SSIQ-a85692 v2, H-SSIQ-137200)

**Reviews the Coordinator-committed snapshot at commit `06af9596` only**
(receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/archives/TASK-20260805-8bddd0-receipt.yaml`,
parent `14b56525`). Nothing in this report edits `specification_v2.yaml`, any
raw artifact, `descent_hitting_time.py`, or any ledger record. Every input
named in the launching task was read in full, not sampled, per this
campaign's GD-6 standing practice: `specification.yaml` (v1, 614 lines) and
`specification_v2.yaml` (v2, 327 lines) in full; `RT-PREFREEZE-EXP-SSIQ-a85692-v2.md`
in full; `compute_delta_e_v2.py` (831 lines) read directly, not the
manifest's prose description; the complete RUN-SSIQ-a85692-b package
(manifest, raw-result.json, execution_report, source_access_log, command.txt,
environment.json, stdout.log, stderr.log, attempt1-infra-killed.stdout.log);
the snapshot receipt including `coordinator_precommit_checks`;
`descent_hitting_time.py` (794 lines, from `EXP-SSIQ-58b642/implementation/`);
`goal.yaml`'s GD-7 entry, `EV-SSIQ-94de20.yaml`, `DEC-20260805-a4e04e.yaml`;
and, for template conformance, `VAL-BATCH-004.md`.

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
    policy-resolved identifier. Same standing condition RT-PREFREEZE-EXP-SSIQ-a85692-v2,
    VAL-BATCH-004, and VAL-BATCH-003 recorded.
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer, the pre-freeze reviewer, and every prior
    reviewer in this lineage; nothing below is corroboration from a distinct
    model. Per AGENTS.md "Goal closure quorum," this alone can never satisfy
    a closure quorum, and this record does not itself close GOAL-SSIQ-001 or
    change H-SSIQ-137200's status.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `06af9596` is `HEAD` on branch
  `claude/0.25-algorithm-breakthrough-y7jbiy` (`git log --oneline -3` shows it
  first, with `14b56525` as its direct parent). Reachable.
- **Parent:** `git log --format='%H %P' -1 06af9596` → parent
  `14b56525ea9584cb0d7fd20f2dc4de5af82d2215`, exactly the receipt's declared
  `parent_sha`. Match.
- **Path set:** `git show --stat 06af9596` lists exactly 11 changed files:
  the 10 declared artifacts plus the receipt itself. No extra file, nothing
  missing.
- **Hashes:** recomputed `sha256(git show 06af9596:<path>)` independently for
  all 10 declared paths (via `git show <commit>:<path> | sha256sum`) and
  compared against `path_sha256` — **0 mismatches**, all 10 exact 64-hex
  matches:

  | path | match |
  |---|---|
  | implementation/compute_delta_e_v2.py | MATCH |
  | runs/RUN-SSIQ-a85692-b/manifest.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-b/raw-result.json | MATCH |
  | runs/RUN-SSIQ-a85692-b/execution_report.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-b/source_access_log.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-b/command.txt | MATCH |
  | runs/RUN-SSIQ-a85692-b/environment.json | MATCH |
  | runs/RUN-SSIQ-a85692-b/stdout.log | MATCH |
  | runs/RUN-SSIQ-a85692-b/stderr.log | MATCH |
  | runs/RUN-SSIQ-a85692-b/attempt1-infra-killed.stdout.log | MATCH |

- **v1 artifacts untouched:** confirmed no v1 path (`compute_delta_e.py`,
  `modular_polynomials.py`, `velu_verify.py`, `modpoly_data/*.txt`,
  `specification.yaml`, `runs/RUN-SSIQ-a85692-a/*`) appears in the changed-path
  set. `compute_delta_e_v2.py` imports these by reference (`sys.path.insert` +
  `import compute_delta_e as v1c`), never copies them.

**Verdict: PASS.** The receipt is a faithful, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v2.yaml` frozen in commit `14b56525` (`frozen_at:
  '2026-08-05'`, `status: approved`); confirmed by diffing the committed blob
  against the working-tree copy (`git show 14b56525:...specification_v2.yaml`
  vs current file) — **byte-identical**, confirming no post-freeze edits.
- `manifest.yaml.code.commit = 14b56525ea9584cb0d7fd20f2dc4de5af82d2215`
  equals the snapshot's own `parent_sha` exactly: the run executed against
  the precise commit that froze `specification_v2.yaml`, with no intervening
  commit between freeze (`2026-08-05T10:16:41Z`) and the run's first
  (killed) launch (`2026-08-05T10:30:34Z`, ~14 minutes later) or its
  successful third attempt (`2026-08-05T12:38:41Z`).

**Verdict: PASS.**

## 3. THE CENTRAL QUESTION — did `real_execution_budget_v2` actually work as designed?

This is the single most important check per the launching task and per the
receipt's own `gd7_fix_verification_flag`. I traced the code directly
(`compute_delta_e_v2.py::run_phase_minus1_on_confirmatory_set`, lines
212–296) rather than trusting the manifest's narrative, and then
cross-checked the traced logic against the run's own recorded per-prime
timing data.

### 3.1 What the code actually does

`run_phase_minus1_on_confirmatory_set(graphs, primes_ascending, seeds,
aggregate_budget_seconds)` initializes **one** `remaining` counter at
`aggregate_budget_seconds` (= `T_RESERVED = 3600.0`, line 126). For each
prime in ascending order it calls `time.time()` once (`t0`) before that
prime's per-vertex loop and re-checks `remaining_now = remaining -
(time.time() - t0)` **before every vertex**, breaking the inner loop the
moment `remaining_now <= 0`. After the prime's loop ends (by exhaustion or by
budget), `remaining -= prime_wall_seconds` (the ACTUAL measured wall time for
that prime), and the loop moves to the next prime carrying the same
decremented `remaining`. There is **no `T_PRIME` constant, no division by
`len(PRIMES)`, and no per-prime cap of any kind** anywhere in this function —
confirmed by reading every line, not just the docstring's claim.

This is a structurally different design from v1's `run_phase_minus1_on_confirmatory_set`
(PF-1's finding: `T_PRIME = 0.5*7200/12 = 300s` applied identically to every
admitted prime, independent of how many primes are in the confirmatory set).

### 3.2 Independent falsification of "per-prime cap disguised as aggregate"

The launching task specifically asked me to rule out a per-prime cap that
merely *looks* aggregate. I pulled `phase_minus1_real_search`'s per-prime
`wall_seconds_used` and `aggregate_seconds_available_at_prime_start` directly
from `raw-result.json` (not the manifest's summary):

| prime | `aggregate_seconds_available_at_prime_start` | `wall_seconds_used` | `n_resolved`/`n_non_fp` | M-COVERAGE |
|---|---|---|---|---|
| 2437 | 3600.00 | 284.88 | 194/194 | 1.0000 |
| 3889 | 3315.12 | 474.84 | 306/306 | 1.0000 |
| 5737 | 2840.27 | 817.95 | 460/460 | 1.0000 |
| 7333 | 2022.32 | 947.69 | 594/594 | 1.0000 |
| 8893 | 1074.63 | 1074.70 | 554/718 | 0.7716 |

Two facts jointly and independently falsify a disguised-per-prime-cap
reading: (1) `wall_seconds_used` varies by **3.8×** across the first four
primes (284.9s to 947.7s) — a fixed per-prime cap, whether 300s (v1's
defective constant) or any other constant, cannot produce this; each prime
ran to its own natural completion. (2) `aggregate_seconds_available_at_prime_start`
for prime *i* equals `aggregate_seconds_available_at_prime_start[i-1] -
wall_seconds_used[i-1]` **exactly**, to the fifth decimal
(3600.00 − 284.88 = 3315.12; 3315.12 − 474.84 = 2840.28 ≈ 2840.27; etc.) —
this is the signature of a single running counter threaded across calls, not
independent per-prime allocations. Only the fifth prime (8893) was actually
truncated, when the shared counter reached 1074.63s remaining and the prime's
own vertex-by-vertex loop consumed all of it (`wall_seconds_used=1074.70`,
slightly *exceeding* the pre-vertex-start `remaining` snapshot by 0.07s — this
is exactly the code's documented granularity: the exhaustion check happens
**before** each vertex's search call, not after, so the vertex in progress
when the budget crosses zero is allowed to finish, per
`two_sided_search(..., time_budget_seconds=remaining_now)`'s own internal
budget argument. This is expected behavior, not a bug).

Summed: `284.88 + 474.84 + 817.95 + 947.69 + 1074.70 = 3600.07`, matching
`real_execution_budget_v2.aggregate_seconds_spent_confirmatory =
3600.0714724063873` in `raw-result.json` to the shown digits — **recomputed
independently, not copied**. `aggregate_seconds_remaining_after_confirmatory
= 0.0` follows (`max(0.0, remaining)`, matching the code's floor at line
296).

**Conclusion: `real_execution_budget_v2` behaved exactly as PF-1's fix
specifies — a genuine single aggregate, measured wall-clock counter with no
per-prime cap. This is not consistent with a disguised per-prime cap under
any interpretation of the recorded numbers.**

### 3.3 Off-by-source-of-time-measurement check

The launching task specifically raised the risk that the aggregate clock
might not correctly account for time spent on Phase 0 / smoke tests /
C-SEARCH-BIAS before Phase −1 starts. Checked directly: `T_RESERVED = 0.5 *
WALL_CLOCK_BUDGET_SECONDS` (line 126) is passed as `aggregate_budget_seconds`
to `run_phase_minus1_on_confirmatory_set` as a **fixed 3600.0s**, not adjusted
by any elapsed-time-so-far term — `main()` never subtracts Phase 0 /
modular-polynomial-verification / graph-reuse / two-point-smoke-test /
C-SEARCH-BIAS / C-BOUND-CHECK time from it. This is a **deliberate design
choice stated explicitly in the frozen v2 spec text**
(`scope_reduction_fallback_v2`: "Reserve the SAME half-budget for Phase −1 as
v1... the 0.5 split rationale... is unchanged and not itself in question"),
not a silently-introduced bug — I checked the spec text before concluding
this. Recomputing the pre-Phase−1 budget split from `raw-result.json`
(`phase0_c_cal_gap_seconds=0.064` + `modular_polynomial_verification_seconds=0.170`
+ `graph_reuse_seconds=27.779` + `feasibility_smoke_test_two_point_seconds=10.118`
+ `c_search_bias_seconds=57.286` = **95.42s**, plus an untimed
C-BOUND-CHECK gap of roughly 1.7s not itemized in `budget_split_seconds` — a
minor, non-blocking incompleteness in the budget accounting, noted below as
Finding F-1) shows the pre-Phase−1 preamble consumed only ~97s against the
**other** reserved half (also nominally 3600s), so no aggregate-clock
double-counting or under-counting occurred, and total measured wall time
(3698.5s) stayed well inside the 7200s budget (51.4%) with wide margin. **No
off-by-source-of-time-measurement defect found.** I flag, as a forward-looking
observation and not a defect in this run, that this fixed-reservation design
(rather than "reserved-minus-elapsed") could in principle allow a future
amendment with a much more expensive preamble (e.g. wider smoothness
parameters) to overrun the nominal 7200s total; this run's own numbers do not
exercise that risk (preamble ≈97s ≪ 3600s reserved for it), so it is recorded
as a latent design characteristic for a future pre-freeze review to watch,
not a finding against this run.

**Verdict on the central question: PASS.** `real_execution_budget_v2` is
independently confirmed, from the run's own recorded per-prime timing data
(not from the manifest's prose), to implement a genuine aggregate,
measured-not-estimated wall-clock counter with zero per-prime cap, exactly as
PF-1's fix specifies, and it is directly responsible for this run clearing
the Phase −1 gate for the first time in this campaign.

## 4. Admission arithmetic (`scope_reduction_fallback_v2`) — independent re-derivation

Recomputed the two-point linear interpolation and the cumulative-prefix
admission entirely from this run's own raw measurements
(`c_min=1.4221388498942058` at p=2437, `c_max=1.9500084718068440` at
p=21601, and `non_fp_rational_counts_by_prime`), independent of the
manifest's stated result:

```
cost_per_vertex(p) = c_min + (c_max - c_min) * (p - p_min) / (p_max - p_min)
est(p) = n_non_fp(p) * cost_per_vertex(p)
```

| # | prime | est (recomputed) | cumulative (recomputed) | fits ≤3600s |
|---|---|---|---|---|
| 1 | 2437 | 275.89 | 275.89 | yes |
| 2 | 3889 | 447.41 | 723.31 | yes |
| 3 | 5737 | 696.00 | 1419.30 | yes |
| 4 | 7333 | 924.86 | 2344.16 | yes |
| 5 | 8893 | 1148.78 | **3492.94** | yes |
| 6 | 10657 | 1424.35 | 4917.29 | **no** |

Recomputed `confirmatory_prime_set = [2437, 3889, 5737, 7333, 8893]`,
`cumulative_estimated_seconds_admitted = 3492.9393263419524` — **matches
`raw-result.json.truncation_fallback_v2` to every shown digit**, independently
reproduced from raw measurements with a from-scratch Python re-implementation
of the formula, not by trusting the manifest or re-reading the log line.

**Verdict: PASS.**

## 5. C-SEARCH-BIAS bit-identical reproduction — re-derived, not trusted

The receipt's second flagged item asks whether the bit-identical claim
against RUN-SSIQ-a85692-a is genuine. I did **not** take "same seeds, same
graph" on faith:

- Recomputed Pearson correlation directly from `raw-result.json.c_search_bias.{true,random}_target_arm.rows`
  (`distance` vs `delta_e_upper_bound`, n=20 each) using an independent
  from-scratch implementation of the Pearson formula: got
  `0.09610901099736084` (true) and `0.030832644977609028` (random) — **exact
  match** to the reported values, both recomputed from raw per-vertex rows.
- Loaded `RUN-SSIQ-a85692-a/raw-result.json` directly and compared its
  `c_search_bias.true_target_arm.rows` and `.random_target_arm.rows` lists
  against RUN-b's element-by-element in Python (`==` on the full row lists,
  not just the summary correlation scalar): **both lists compare
  identical**, vertex-for-vertex, target-for-target, degree-for-degree. This
  is the strongest available check that RUN-b's C-SEARCH-BIAS truly executed
  the identical code against the identical graph, not merely that the two
  summary correlations happen to agree.
- Independently verified `magnitudes_comparable_flag=True` against the
  code's own pre-registered `comparability_rule`
  (`|corr_random| >= 0.5*max(|corr_true|,eps)` OR both `<0.1`): `0.0961 <
  0.1` and `0.0308 < 0.1` both hold, so the "both below 0.1" branch fires
  correctly.

**Verdict: PASS**, both flagged items in the receipt (`gd7_fix_verification_flag`
and `c_search_bias_control_failure_consistency`) resolve to CONFIRMED, not
merely "plausible."

## 6. Descent metrics — recomputed from reported per-prime medians

`raw-result.json` does not retain raw per-vertex hitting-time arrays (only
aggregated per-prime medians and trapped fractions), so a full
vertex-level re-derivation would require re-executing the ~3600s real search
— outside this review's practical budget, and disclosed as a limitation
below. What **is** independently checkable from committed numbers, and what I
checked:

- Re-ran `ols_loglog_fit`'s exact formula (transcribed from
  `descent_hitting_time.py` lines 104–134, not reimplemented from memory) on
  the four usable primes' reported `(N, greedy_median)` and `(N,
  random_median)` pairs (`N=[203,324,478,611]`, greedy medians `[10,11,12,13]`,
  random medians `[22,20,24,36]`): recomputed `gamma_greedy =
  0.23353930498277403`, `gamma_random = 0.4013966802748042`, `m_gap =
  0.16785737529203015` — **exact match**, all 17 significant figures, to
  `raw-result.json.descent_metrics`.
- Re-ran `bootstrap_gap_ci`'s exact resampling procedure (`random.Random(20260805)`,
  2000 bootstrap draws, transcribed directly from `descent_hitting_time.py`
  lines 362–384, including its `sxx==0` degenerate-resample skip) on the same
  four data points: recomputed `lo=-0.4077113485550079`,
  `hi=1.325623864261203` — **exact bit match** to `raw-result.json`'s
  `m_gap_ci_lo`/`m_gap_ci_hi`. Python's `random.Random` with a fixed seed and
  the same call sequence is deterministic, so this is a genuine, not
  coincidental, reproduction.

**Verdict: PASS**, for the downstream arithmetic (OLS fit and bootstrap CI
from the reported medians). **Limitation, disclosed rather than
elided**: the medians themselves (and thus the entire descent-metrics
output) are not independently re-derivable from this review's available
artifacts without re-executing the real delta_E search and the descent
simulators, which would cost real compute comparable to the original run
(~3600s+); this review did not re-execute that search. This validation
therefore establishes that the reported downstream statistics are computed
**correctly from** the reported medians, not that the medians themselves are
correct — that rests on the correctness of `two_sided_search` /
`greedy_descent_hitting_time` / `random_walk_hitting_time`, which is reused,
unmodified code previously exercised (not independently re-derived from raw
per-vertex data) in this and prior batches.

## 7. PD-2 (PER-PRIME-TRAPPED-EXCLUSION gap) — verified directly against `descent_hitting_time.py`

Read `descent_hitting_time.py` in full to check the executor's disclosed
claim independently, not merely to confirm it appears in the execution
report.

- `population_median_with_sentinel` (lines 137–154) computes and *returns*
  `trapped_fraction` alongside the median. `run_population` (lines 254–289)
  propagates it into its result dict. **Nowhere in this 794-line file** is
  there any conditional logic that excludes a prime, or filters a
  population, based on `trapped_fraction > 0.5`, or any threshold at all —
  confirmed by reading every function in the module, and by `grep`ping the
  file for `trapped_fraction` (2 occurrences, both report-only assignments,
  no comparison operator applied to the value anywhere).
- Cross-checked `compute_delta_e_v2.py`'s own descent-metrics orchestration
  (lines 703–761, the inline logic PD-2 says reproduces v1's gap unmodified):
  confirmed the `for p in usable_primes` loop appends every prime with full
  coverage to `per_prime` unconditionally — no `if
  per_prime[p]["greedy_trapped_fraction"] <= 0.5` guard anywhere before the
  OLS fit is computed on `usable_full`.
- `grep`ped the entire `EXP-SSIQ-a85692/` tree for `PER-PRIME-TRAPPED-EXCLUSION`
  and for `trapped_fraction.*0.5`: the label and the 0.5 threshold appear
  **only** in `specification.yaml`'s prose (the definition and the
  invalidation rule text), never as an implemented comparison in any `.py`
  file. This directly confirms PD-2's claim: the filter is specified in the
  frozen contract's text but was never coded, in either v1's original
  `compute_delta_e.py` or its unmodified reuse here.
- Confirmed the reported trapped fractions for the four usable primes
  directly from `raw-result.json.descent_metrics.per_prime` (2437: 0.8374,
  3889: 0.7222, 5737: 0.8201, 7333: 0.8511) — **all four exceed 0.5**, so
  PD-2 is correctly characterized as material to this specific run's
  reported numbers, not a hypothetical concern.
- **Impact on the terminal decision, independently re-verified**: read
  `apply_decision_rule` (`compute_delta_e.py` lines 549–581, imported
  unchanged) directly. Its branch order is `phase0_pass` →
  `phase_minus1_gate_pass` → `(c_search_bias_control_failure or
  c_null_label_control_failure or not c_connectivity_all_pass)` → CI sign.
  The control-failure branch (`return {"branch": "CONTROL-FAILURE-VOID", ...}`)
  is reached and returned **before** the function ever inspects `m_gap_ci_lo`
  — it does not require `m_gap_ci_lo` to be non-`None`. Since
  `c_search_bias_control_failure=True` independent of trapped_fraction (§5
  above), the terminal branch is CONTROL-FAILURE-VOID regardless of whether
  PER-PRIME-TRAPPED-EXCLUSION is applied or not. I confirmed this by tracing
  the code path directly rather than accepting the executor's own stated
  simulation.

**Verdict: PD-2 CONFIRMED, both as a genuine gap in the reused code and as
immaterial to this run's terminal decision label.** It IS material to the
specific `gamma_greedy=0.23354` / `m_gap=+0.16786` numbers, exactly as
disclosed: under a correctly-implemented filter, zero of the four usable
primes would remain for the greedy-arm fit (all four exceed the 0.5
threshold), so `descent_metrics.ran` would be `false` and no `gamma_greedy`/
`m_gap`/CI would exist at all. Any Coordinator synthesis or future citation
of this run's specific M-GAP numbers must carry this caveat; the
CONTROL-FAILURE-VOID label itself does not depend on it.

## 8. Diff-list cross-check against `required_artifacts_note`

Read `compute_delta_e_v2.py` directly against `specification_v2.yaml`'s
`required_artifacts_note` diff list (not the module's own docstring
paraphrase of it):

- `apply_truncation_fallback` (lines 167–203): rewritten, cumulative-prefix
  logic, matching `scope_reduction_fallback_v2`. **CONFIRMED CHANGED.**
- `run_phase_minus1_on_confirmatory_set` (lines 212–296): rewritten, single
  aggregate counter, no per-prime cap, matching `real_execution_budget_v2`.
  **CONFIRMED CHANGED**, and independently exercised in §3 above.
- `estimate_per_prime_cost_v2` (lines 134–159): new, separate helper
  function, not folded into `apply_truncation_fallback`, matching
  `per_prime_cost_estimate_v2`'s PF-5 requirement. **CONFIRMED NEW.**
- `run_feasibility_smoke_test`, `verify_modular_polynomials`,
  `build_all_graphs`, `run_correctness_gates`, `run_c_search_bias`,
  `run_c_bound_check`, `apply_decision_rule`, `git_state`,
  `two_sided_search`, and the module constants: all imported directly as
  `v1c.<name>` (lines 105–113), never redefined in this file. **CONFIRMED
  UNCHANGED, reused by reference** — a Python `import` binding, which is a
  materially stronger reuse guarantee than a textual "unchanged" claim
  (there is no way for the imported name to diverge from v1's own execution
  without editing v1's file, which the receipt's `v1_artifacts_untouched`
  check already confirmed did not happen).
- The one disclosed physical-form deviation (PD-1: new file vs. in-place
  edit) is exactly what the launching task's own instruction required
  ("copy or branch... do not edit v1's frozen file in place"), consistent
  with `command.txt`'s own record of that instruction, and does not change
  the logical diff.

**Verdict: PASS.** The diff-list cross-check holds against the actual code,
function for function.

## 9. Decision-rule application check

- `apply_decision_rule` (traced in §7) evaluates, in order: `phase0_pass`
  (True) → `phase_minus1_gate_pass` (True, confirmed: `n_primes_coverage_pass=5
  >= 4` from `raw-result.json`, independently recomputed from the five
  per-prime `m_coverage_non_fp_fraction` values, all ≥0.5) → control-failure
  check (`c_search_bias_control_failure=True` fires) → returns
  `CONTROL-FAILURE-VOID`. This is exactly the frozen ordering: Phase −1 gate
  → Phase 0 (already passed) → C-SEARCH-BIAS/comparability →
  CONTROL-FAILURE-VOID.
- Grepped every RUN-SSIQ-a85692-b artifact for the bare string `"VOID"`:
  every occurrence is inside the compound term `CONTROL-FAILURE-VOID`, or in
  quoted historical references to EXP-SSIQ-58b642's differently-named VOID
  outcome or v1's DATA-UNAVAILABLE-BLOCKED text. **No bare "VOID" used to
  describe this run's own outcome anywhere.**
- `manifest.yaml.run.validity = "completed_valid_control_failure_void"` and
  `raw-result.json.decision.branch = "CONTROL-FAILURE-VOID"` are consistent
  with each other and with the four-label glossary
  (`outcome_scope_label_glossary`, inherited unchanged from v1).

**Verdict: PASS.** No bare-VOID misuse; decision rule applied mechanically
and correctly.

## 10. Overclaim / premature-closure check

- `manifest.yaml.validity_reason` and `execution_report.yaml.observations.decision_rule_application`
  both state explicitly that the terminal branch is CONTROL-FAILURE-VOID
  "regardless of the CI including a wide positive range" — the wide,
  positive-leaning CI (`[-0.4077, 1.3256]`) is never presented as suggestive
  evidence for a delta_E-gradient anywhere in the reviewed artifacts. This is
  the correct treatment: a control failure means the *signal itself* — not
  just its sign — is contaminated and uninterpretable, and the artifacts do
  not soften this.
- The receipt's own `decision_branch_recorded` check states the outcome
  "VERBATIM AND NOT ENDORSED," and PD-2's caveat is stated plainly rather
  than smoothed over ("should NOT be read as a clean, spec-conformant
  M-GAMMA-GREEDY measurement... a reader treating them as the spec's own
  M-GAMMA-GREEDY without this caveat would be misled").
- `executor_assessment.data_quality: limited` (not "good") is an honest
  self-downgrade, correctly citing both PD-2 and the narrow achieved N-range
  (203–611, a 3.0× span vs. the originally intended 8.9× span) as the
  reasons, consistent with `RT-BATCH-004.md` objection 2 and
  `DEC-20260805-a4e04e` D-5's advance warning that the cheapest-admissible
  prefix would concentrate on small primes.
- No sentence anywhere asserts H-SSIQ-137200's prediction is supported,
  refuted, detected, or falsified. `objective_boundary` is restated
  correctly (toy scale, no crypto-scale transfer, no complexity claim).

**Verdict: PASS.** No overclaim found; the CONTROL-FAILURE-VOID label's force
is preserved, not softened, anywhere in the reviewed package.

## 11. Infrastructure-failure disclosure (PD-3)

`attempt1-infra-killed.stdout.log` is preserved and hash-pinned (§1); its
content (58 lines, ending mid-Phase −1 with no `raw-result.json` write, no
stderr) is consistent with the execution report's narrative of a clean
external kill, not a code crash. Per AGENTS.md rule 3, correctly classified
`infrastructure_error` and correctly excluded from any research-evidence
role; no partial numeric result from either killed attempt appears anywhere
in the reported numbers (verified: neither killed attempt's log shows a
completed Phase −1 prime).

**Verdict: PASS.**

---

## Findings

- **F-1 [informational, non-blocking].** `budget_split_seconds` itemizes
  Phase 0, modular-polynomial verification, graph reuse, the two-point smoke
  test, C-SEARCH-BIAS, the Phase −1 confirmatory search, C-NULL-LABEL, and
  descent simulation, but omits a line item for C-BOUND-CHECK's own runtime.
  Summing the itemized entries (3696.81s) against the reported
  `total_wall_seconds` (3698.50s) leaves ~1.7s unaccounted for — almost
  certainly C-BOUND-CHECK plus miscellaneous overhead (argument parsing,
  `git_state()`'s subprocess call, JSON serialization), not a missing
  compute-time disclosure of any consequence (<0.05% of total wall time).
  **What would resolve it:** a `c_bound_check_seconds` key in a future
  amendment's budget_split, purely for completeness against
  `spec.budget.delta_e_search_sub_budget_note`'s "If the split is not stated,
  that is an underspecification" clause. Does not affect any reported metric.
- **F-2 [informational, forward-looking, non-blocking].** `real_execution_budget_v2`'s
  `T_RESERVED` is a fixed 3600s reservation, not reduced by time already
  spent in the pre-Phase−1 preamble (Phase 0 / modpoly verification / graph
  reuse / smoke tests / C-SEARCH-BIAS / C-BOUND-CHECK). This is explicit,
  disclosed, intentional design in the frozen v2 spec text ("not itself in
  question"), and in THIS run the preamble (~97s) was negligible against the
  3600s reserved for it, so no total-budget-overrun risk materialized
  (3698.5s / 7200s = 51.4%). Flagged only as a latent characteristic for a
  future amendment to watch if the preamble ever grows materially (e.g.
  wider smoothness parameters raising smoke-test or C-SEARCH-BIAS cost);
  **not a defect in this run**, and not blocking.
- **F-3 [confirmed, material to reported numbers, not to the terminal
  label].** PD-2 (PER-PRIME-TRAPPED-EXCLUSION never implemented in the
  reused descent-metrics code) is independently confirmed against
  `descent_hitting_time.py` and `compute_delta_e_v2.py`'s own inline
  orchestration (§7). It is material: under a correctly implemented filter,
  zero of the four usable primes survive (all four have
  `greedy_trapped_fraction > 0.5`), so `gamma_greedy=0.23354`,
  `gamma_random=0.40140`, `m_gap=+0.16786`, and the bootstrap CI would not
  exist as reported. It does NOT change this run's terminal decision
  (CONTROL-FAILURE-VOID fires via C-SEARCH-BIAS regardless, independently
  re-traced through `apply_decision_rule` in §7/§9). **What resolves it:** a
  Coordinator-approved, separately pre-freeze-reviewed amendment implementing
  the filter in a new function (per the reuse discipline — not a silent patch
  to reused code), and a re-run of descent metrics under it. Any citation of
  this run's specific gamma/M-GAP numbers, in a ledger synthesis or
  elsewhere, must carry this caveat.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run executed exactly as its frozen v2 contract specifies, honestly and
completely disclosed, including two infrastructure failures that consumed
real compute without producing evidence (correctly excluded per AGENTS.md
rule 3) and a self-disclosed gap in reused code (PD-2) that this review
independently confirmed against the actual code rather than accepting on
trust. Every recomputable number in this package was independently
re-derived from raw data or from a from-scratch reimplementation of the
governing formula — the admission arithmetic, the aggregate-counter's
genuinely-aggregate (not disguised-per-prime) behavior, the C-SEARCH-BIAS
correlations (recomputed from raw rows AND cross-checked row-for-row against
RUN-a's own raw data), the OLS gamma fits, and the bootstrap CI — and every
one reproduced exactly. `real_execution_budget_v2` is confirmed, from the
run's own timing data, to have worked precisely as PF-1's fix specifies: this
is the central finding this review exists to make, and it holds. The decision
rule was applied mechanically and correctly, in the frozen ordering, with no
bare-`VOID` misuse, and the CONTROL-FAILURE-VOID label's force is preserved
throughout the package — nowhere is the wide, positive-leaning CI presented
as suggestive despite the control failure.

It is admitted **with the condition** that any Coordinator synthesis or
future citation of this run's specific `gamma_greedy` / `gamma_random` /
`m_gap` numbers (as opposed to the CONTROL-FAILURE-VOID terminal label
itself, which does not depend on this) states F-3/PD-2's caveat explicitly:
these numbers are computed without the PER-PRIME-TRAPPED-EXCLUSION filter the
frozen spec's own M-GAMMA-GREEDY definition names, and under that filter none
of the four contributing primes would remain in the greedy-arm fit.

This report establishes that RUN-SSIQ-a85692-b is admissible evidence of
exactly what it measured: a Phase −1 gate pass under the corrected
cumulative-budget/aggregate-counter design, and a CONTROL-FAILURE-VOID
terminal outcome because C-SEARCH-BIAS's random-target correlation remains
comparable in magnitude to the true-target correlation. It establishes
nothing about whether a delta_E-gradient exists, and nothing about
H-SSIQ-137200's status beyond what CONTROL-FAILURE-VOID itself asserts (the
signal, as measured by this instrument's search-construction order, is
contaminated and uninterpretable in either direction at these parameters).

```yaml
validation_report:
  id: VAL-BATCH-005
  task_id: TASK-20260805-10868f
  run_ids: [RUN-SSIQ-a85692-b]
  reviewed_commit: 06af9596d623b1d61c6daf6e14ed898ef00c213d
  reviewed_commit_parent: 14b56525ea9584cb0d7fd20f2dc4de5af82d2215
  artifact_checks:
    - {check: path_sha256_recompute, scope: "all 10 declared paths", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "11 changed files = 10 declared artifacts + receipt itself"}
    - {check: v1_artifacts_untouched, result: PASS, detail: "no v1 path appears in the changed-path set; v1 code imported by reference (sys.path insertion), never copied"}
    - {check: contract_frozen_before_run, frozen_at: '2026-08-05T10:16:41Z', run_first_launch: '2026-08-05T10:30:34Z', run_successful_attempt_started: '2026-08-05T12:38:41Z', result: PASS}
    - {check: specification_v2_unmodified_since_freeze, result: PASS, detail: "git show 14b56525:specification_v2.yaml is byte-identical to the working-tree copy"}
    - {check: required_artifacts_present, result: PASS, detail: "all 10 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: aggregate_counter_genuine_vs_disguised_per_prime_cap, method: "independently summed wall_seconds_used across 5 confirmatory primes and cross-checked aggregate_seconds_available_at_prime_start's monotone decrement", reported_aggregate_spent: 3600.0714724063873, recomputed: "284.884+474.842+817.950+947.691+1074.705 = 3600.072", result: MATCH, additional_check: "per-prime wall_seconds_used varies 3.8x (284.9s-947.7s), directly falsifying a fixed per-prime-cap reading"}
    - {metric: cumulative_admission_arithmetic, reported_confirmatory_set: [2437, 3889, 5737, 7333, 8893], reported_cumulative: 3492.9393263419524, recomputed_from_scratch: "identical set, cumulative=3492.9393263419524", result: MATCH}
    - {metric: c_search_bias_true_target_correlation, reported: 0.09610901099736084, recomputed_from_raw_rows: 0.09610901099736084, result: MATCH}
    - {metric: c_search_bias_random_target_correlation, reported: 0.030832644977609028, recomputed_from_raw_rows: 0.030832644977609028, result: MATCH}
    - {metric: c_search_bias_bit_identical_to_RUN_a, method: "element-wise list comparison of true_target_arm.rows and random_target_arm.rows between RUN-a and RUN-b raw-result.json", result: MATCH, detail: "both row lists identical, not merely the summary correlations"}
    - {metric: gamma_greedy, reported: 0.23353930498277403, recomputed_via_ols_loglog_fit_from_reported_medians: 0.23353930498277403, result: MATCH}
    - {metric: gamma_random, reported: 0.4013966802748042, recomputed_via_ols_loglog_fit_from_reported_medians: 0.4013966802748042, result: MATCH}
    - {metric: m_gap, reported: 0.16785737529203015, recomputed: 0.16785737529203015, result: MATCH}
    - {metric: m_gap_bootstrap_ci, reported: [-0.4077113485550079, 1.325623864261203], recomputed_via_seeded_bootstrap_2000_draws: [-0.4077113485550079, 1.325623864261203], result: "EXACT BIT MATCH"}
  control_checks:
    - {control: C-CAL-GAP, result: PASS, detail: "reused unchanged, ran, overall_pass=true"}
    - {control: modular_polynomial_verification_ell23, result: PASS, detail: "independent Velu-formula route, all_ok=true, 3/3 test curves, residual 0"}
    - {control: C-CONNECTIVITY_M-DEGSEQ_C-EDGELIST, result: PASS, detail: "all 12 primes, floor(p/12) anchor"}
    - {control: real_execution_budget_v2_aggregate_counter, result: "CONFIRMED WORKING AS DESIGNED", detail: "independently re-derived from per-prime wall_seconds_used and aggregate_seconds_available_at_prime_start; genuinely aggregate, not a disguised per-prime cap; see report section 3"}
    - {control: C-SEARCH-BIAS, result: FAILED, detail: "magnitudes_comparable_flag=true (both correlations <0.1); independently re-derived from raw rows and cross-checked row-for-row bit-identical against RUN-SSIQ-a85692-a"}
    - {control: C-NULL-LABEL, result: "RAN, n_primes_usable=4", detail: "8893 correctly excluded for partial (non-full) coverage per the inherited len(delta_map)!=len(vertices) skip rule"}
    - {control: C-BOUND-CHECK, result: "ran, reported, non-gating per spec"}
    - {control: decision_rule_label_taxonomy, result: PASS, detail: "no bare VOID used for this run's own outcome; CONTROL-FAILURE-VOID correctly derived via the frozen branch ordering (phase0 -> phase_minus1_gate -> control_failure -> CI), independently traced through apply_decision_rule's code"}
  heuristic_validation_checks: []
  cost_model_checks:
    - {check: budget_split_completeness, result: "MINOR GAP (F-1)", detail: "C-BOUND-CHECK's own runtime is not itemized in budget_split_seconds; ~1.7s of 3698.5s total unaccounted, <0.05%, non-blocking"}
    - {check: aggregate_reservation_vs_elapsed_preamble_time, result: "BY DESIGN, NOT A BUG (F-2)", detail: "T_RESERVED=3600s is a fixed reservation per the frozen spec text, not reduced by pre-Phase-1 elapsed time; preamble (~97s) was negligible against it in this run, so no overrun risk materialized (total 3698.5s/7200s=51.4%); flagged as a latent characteristic for a future amendment with a materially larger preamble to watch"}
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: informational, summary: "C-BOUND-CHECK's runtime is not itemized in budget_split_seconds (~1.7s unaccounted of 3698.5s total)", resolution: "add a c_bound_check_seconds key in a future amendment"}
    - {id: F-2, severity: informational-forward-looking, summary: "T_RESERVED's fixed (not elapsed-adjusted) reservation is intentional per frozen spec text and did not cause an overrun in this run, but is a latent risk if a future amendment's preamble grows materially", resolution: "watch in a future pre-freeze review if smoothness parameters or preamble cost increase"}
    - {id: F-3, severity: confirmed-material-to-reported-numbers-not-to-terminal-label, summary: "PD-2 (PER-PRIME-TRAPPED-EXCLUSION never implemented in reused descent-metrics code) independently confirmed against descent_hitting_time.py and compute_delta_e_v2.py; material to gamma_greedy/gamma_random/m_gap (all 4 contributing primes have trapped_fraction>0.5, so a correct filter would leave zero primes and descent_metrics.ran=false); does NOT change the terminal CONTROL-FAILURE-VOID label, independently re-traced through apply_decision_rule", resolution: "Coordinator-approved, separately pre-freeze-reviewed amendment implementing the filter; any citation of this run's specific gamma/M-GAP numbers must carry this caveat"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, the pre-freeze reviewer, and every prior reviewer in this lineage; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "Descent-metrics medians (greedy_median, random_median per prime) are not independently re-derivable from this review's available artifacts without re-executing the real ~3600s delta_E search and descent simulators, which this review did not do; this review confirms the downstream OLS/bootstrap arithmetic is computed correctly FROM the reported medians, not that the medians themselves are correct from first principles."
    - "This report makes no claim about whether a delta_E-gradient exists, about lever L4's status, or about the archived source's Heuristic 1 or complexity claim -- none of that data is licensed by a CONTROL-FAILURE-VOID outcome."
    - "Toy scale throughout: p up to 8893 in the fitted window (15 bits max across all 12 pre-registered primes), graphs 203-611 vertices in the achieved fitting window, B=X=23. Nothing transfers to cryptographic scale."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-005/reviews/VAL-BATCH-005.md
```
