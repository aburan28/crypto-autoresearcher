# VAL-BATCH-006 — Validator review of RUN-SSIQ-a85692-c (EXP-SSIQ-a85692 v3, H-SSIQ-36e970)

**Reviews the Coordinator-committed snapshot at commit `cc786884` only**
(receipt `coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/archives/TASK-20260805-2d8575-receipt.yaml`,
parent `7f40426b`). Nothing in this report edits `specification_v3.yaml`, any
raw artifact, `descent_hitting_time.py`, `compute_delta_e.py`, or any ledger
record. Every input named in the launching task was read in full, not
sampled: `specification_v2.yaml` (327 lines) and `specification_v3.yaml` (363
lines, the frozen contract this run implements) in full;
`RT-PREFREEZE-EXP-SSIQ-a85692-v3.md` in full; `reanalyze_v3.py` (573 lines)
read directly, not the manifest's prose description; the complete
`RUN-SSIQ-a85692-c` package (`manifest.yaml`, `raw-result.json`,
`execution_report.yaml`, `source_access_log.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `synthetic_self_test.json`);
the snapshot receipt including `coordinator_precommit_checks`;
`descent_hitting_time.py` (794 lines, `ols_loglog_fit` lines 104–134 and
`bootstrap_gap_ci` lines 362–384 read in full) and `compute_delta_e.py`
(`apply_decision_rule` lines 549–581) read directly to check the two
by-reference imports; `goal.yaml`'s GD-8/GD-9 entries, `EV-SSIQ-f3ce32.yaml`,
`DEC-20260805-5f5ac6.yaml` in full; and, for template conformance,
`VAL-BATCH-005.md`. `H-SSIQ-36e970.yaml` was also read in full to check the
overclaim question against the hypothesis record itself.

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
    policy-resolved identifier. Same standing condition every review in this
    lineage has recorded (VAL/RT-BATCH-003 through VAL-BATCH-005,
    RT-PREFREEZE-EXP-SSIQ-a85692-v2/v3).
  independent_session: true
  independence_kind: session
  independence_cap: >-
    SESSION-independent only, never model-independent. This review shares a
    model family with the producer, the pre-freeze reviewer, and every prior
    reviewer in this lineage; nothing below is corroboration from a distinct
    model. Per AGENTS.md "Goal closure quorum," this alone can never satisfy
    a closure quorum, and this record does not itself close GOAL-SSIQ-001 or
    change H-SSIQ-36e970's status.
```

---

## 1. Receipt verification (content-first, per AGENTS.md)

- **Commit reachability:** `git merge-base --is-ancestor cc786884 HEAD`
  confirms `cc786884` is an ancestor of `HEAD`. Reachable.
- **Parent:** `git log --format='%H %P' -1 cc786884` → parent
  `7f40426b041044b9074f8bf208971786bde83801`, exactly the receipt's declared
  `parent_sha`. Match.
- **Path set:** `git diff-tree --no-commit-id --name-only -r cc786884` lists
  exactly 11 changed files: the 10 declared artifacts plus the receipt
  itself. No extra file, nothing missing.
- **Hashes:** recomputed `sha256(git show cc786884:<path>)` independently for
  all 10 declared paths and compared against `path_sha256` — **0
  mismatches**, all 10 exact 64-hex matches:

  | path | match |
  |---|---|
  | implementation/reanalyze_v3.py | MATCH |
  | runs/RUN-SSIQ-a85692-c/manifest.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-c/raw-result.json | MATCH |
  | runs/RUN-SSIQ-a85692-c/execution_report.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-c/source_access_log.yaml | MATCH |
  | runs/RUN-SSIQ-a85692-c/command.txt | MATCH |
  | runs/RUN-SSIQ-a85692-c/environment.json | MATCH |
  | runs/RUN-SSIQ-a85692-c/stdout.log | MATCH |
  | runs/RUN-SSIQ-a85692-c/stderr.log | MATCH |
  | runs/RUN-SSIQ-a85692-c/synthetic_self_test.json | MATCH |

- **v1/v2 artifacts untouched:** `git diff --stat 7f40426b cc786884 --
  experiments/EXP-SSIQ-a85692/specification.yaml
  experiments/EXP-SSIQ-a85692/specification_v2.yaml
  experiments/EXP-SSIQ-a85692/implementation/compute_delta_e.py
  experiments/EXP-SSIQ-a85692/implementation/compute_delta_e_v2.py
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-a
  experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b` returns **empty** — no
  changes to any of them between the freeze commit and this snapshot.

**Verdict: PASS.** The receipt is a faithful, content-verified record of the
exact bytes reviewed below.

## 2. Contract-freeze verification

- `specification_v3.yaml` frozen in commit `7f40426b` ("EXP-SSIQ-a85692 v3
  FROZEN (all four pre-freeze findings resolved)"); `git show
  7f40426b:experiments/EXP-SSIQ-a85692/specification_v3.yaml` diffed against
  the current working-tree copy — **byte-identical**, no post-freeze edits.
- `manifest.yaml.code.commit = 7f40426b041044b9074f8bf208971786bde83801`
  equals the snapshot's own `parent_sha` exactly: the run executed against
  the precise commit that froze `specification_v3.yaml`, with no intervening
  commit between freeze and execution.

**Verdict: PASS.**

## 3. Independent re-derivation: `trapped_exclusion_filter_v3` on RUN-b's own raw data

Read `RUN-SSIQ-a85692-b/raw-result.json`'s `descent_metrics.per_prime` (real
arm) and `c_null_label.per_prime` (null arm) directly — not via the
pre-freeze review's own table, not via `reanalyze_v3.py`'s own output — and
applied the `<=0.5` threshold by hand:

| prime | real arm `greedy_trapped_fraction` | survives? | null arm `greedy_trapped_fraction` | survives? |
|---|---|---|---|---|
| 2437 | 0.8374384236453202 | NO | 0.8078817733990148 | NO |
| 3889 | 0.7222222222222222 | NO | 0.7037037037037037 | NO |
| 5737 | 0.8200836820083682 | NO | 0.7907949790794979 | NO |
| 7333 | 0.8510638297872340 | NO | 0.8477905073649754 | NO |
| 8893 | not present (partial coverage, excluded upstream) | n/a | `skipped=true` | n/a |

Zero of four primes survive in **either** arm, reproduced to every shown
digit against both `raw-result.json.trapped_exclusion_filter_v3` (this run's
own output) and the pre-freeze review's independent table. This is the
single number that determines every downstream branch in this run.

**Verdict: PASS.**

## 4. THE CENTRAL QUESTION — does the synthetic self-test independently check out?

This is the item the receipt's `coordinator_precommit_checks` flags as
`synthetic_self_test_disclosure: FLAGGED_FOR_INDEPENDENT_REVIEW`, and the
single most important check per the launching task.

### 4.1 Analytic re-derivation, from first principles, not from the code's own output

`ols_loglog_fit` (`descent_hitting_time.py` lines 104–134, transcribed
directly) computes `gamma = sxy/sxx` where `sxy = sum((x-xbar)*(y-ybar))`,
`sxx = sum((x-xbar)^2)`, over `x = log(N)`, `y = log(median)`. For an exact
power law `y = N^gamma` (i.e. `c=1`, so `log(c)=0`): `ys = gamma * xs`
exactly, so `ybar = gamma*xbar`, and
`sxy = sum((x-xbar)*gamma*(x-xbar)) = gamma*sxx`, giving `gamma_fit =
gamma` **exactly** (up to floating-point rounding of `N**gamma` and
`math.log`, which is on the order of `1e-15`–`1e-16` relative error, far
under the self-test's own `1e-9` tolerance). `r_squared = 1 - rss/tss`
should be `1.0` to floating precision since every residual is ~0. This is a
hand-derivation from the transcribed formula, independent of running any
code.

I independently confirmed the synthetic construction matches this
prediction: `N_list = [100, 1000, 10000, 100000]`, `greedy_medians =
N**0.3`, `random_medians = N**0.8` (`c=1.0` in both cases, zero noise).
Expected: `gamma_greedy=0.3`, `gamma_random=0.8`, `m_gap=0.5`, `r_squared=1.0`
for both fits.

**Recomputed values in `synthetic_self_test.json`:** `gamma_null_greedy =
0.29999999999999993` (diff from 0.3: `~7e-17`), `gamma_null_random = 0.8`
(exact), `m_gap_null = 0.5000000000000001` (diff from 0.5: `~1e-16`),
`r_squared_greedy = r_squared_random = 1.0`. **All match the hand-derived
analytic prediction to far better than the stated `1e-9` tolerance** — this
is not merely "the code says it passed," it is arithmetic I re-derived
independently from the transcribed `ols_loglog_fit` formula and the stated
construction.

### 4.2 Bootstrap CI degeneracy — also analytically checkable, also confirmed

`bootstrap_gap_ci` (lines 362–384) resamples primes with replacement and
refits `ols_loglog_fit` on each resample, skipping any resample where
`sxx==0` (all resampled `N` identical). Because §4.1 shows `ols_loglog_fit`
recovers `gamma` **exactly** for *any* subset of `>=2` distinct N values on
a noiseless exact power law, every valid bootstrap resample must return
`m_gap = 0.5` exactly (to floating precision) — the CI is analytically
predicted to degenerate to a point at `0.5`. **Recomputed CI: `[0.4999999999999998,
0.5000000000000004]`**, width `~6e-16` — floating-point noise, not
statistical spread, exactly as hand-derived. `n_boot_valid_draws=1968` of
2000 (32 degenerate all-same-index draws correctly skipped by the `except
ValueError` clause) — consistent with `4**4=256` distinct ordered draws out
of which `4` are the degenerate all-same-index draws per resampling
structure; the reported skip count is plausible and does not indicate any
selection artifact (skipped draws are excluded from the CI, not
zero-filled).

### 4.3 Independence of the synthetic inputs from RUN-b's real numbers

Checked directly, not merely asserted: RUN-b's real four contributing
primes have `N = [203, 324, 478, 611]` (per `descent_metrics.per_prime`,
confirmed in §3's own read of the same file) and small-integer medians
(`greedy_median` in the single-digit-to-low-teens range, `random_median` in
the 20s–30s range, per BATCH-005's own already-verified numbers). The
synthetic self-test's `N_list = [100, 1000, 10000, 100000]` and
`greedy_medians`/`random_medians` in the `3.98`–`31.6` and `39.8`–`10000`
ranges share **no value** with RUN-b's real N or median figures at any
digit of precision, and are constructed by a closed-form power-law formula
stated in the code, not copied from any file. `source_access_log.yaml` and
`raw-result.json` both state explicitly that the synthetic data is "NOT
sourced from RUN-SSIQ-a85692-b, RUN-SSIQ-a85692-a, or any prior run's
raw-result.json" — confirmed true by direct comparison, not merely by
trusting the stated claim.

**Verdict on the central question: PASS.** The synthetic self-test's
expected/analytic values are independently correct (re-derived by hand from
`ols_loglog_fit`'s transcribed formula, not from the code's own output), the
code correctly implements `dht.ols_loglog_fit`/`dht.bootstrap_gap_ci` calls
producing the analytically-predicted numbers to far better than the stated
tolerance, and the synthetic inputs are genuinely independent of
RUN-SSIQ-a85692-b's real N/median values — not incidentally matching them.

## 5. `c_null_label_control_failure` reported as the literal NOT-EVALUABLE state

`raw-result.json.c_null_label_comparison_v3.c_null_label_control_failure =
"NOT-EVALUABLE"` — a JSON **string**, not the JSON booleans `true`/`false`.
Confirmed directly in the raw file, not via the manifest's summary. Traced
`c_null_label_comparison_v3()` (`reanalyze_v3.py` lines 141–216): the `if
len(null_survivors) < min_primes:` branch returns the literal string
`"NOT-EVALUABLE"` and returns **before** any `dht.ols_loglog_fit` or
`dht.bootstrap_gap_ci` call — confirmed by reading the control flow directly,
not by trusting `evaluable=false`. Since `null_survivors=0 < 3`, this branch
is the one that fires on this run's actual data.

**Verdict: PASS.** Reported as the explicit third state, never defaulted to
`True` or `False`, and the fit-and-bootstrap branch's non-execution on real
data is independently confirmed by direct control-flow tracing.

## 6. `apply_decision_rule` correctly NOT invoked — traced directly, not inferred from the flag

Read `main()` (`reanalyze_v3.py` lines 376–512) directly. The controlling
branch is:

```python
if len(real_survivors) < REAL_ARM_MIN_PRIMES:
    decision = {"branch": "DATA-UNAVAILABLE-BLOCKED", ...}
    # apply_decision_rule is NOT invoked in this branch
else:
    ... v1c.apply_decision_rule(...) ...
```

`real_survivors = filter_result["real_arm"]["survivors"]`, an empty list per
§3 (`n_survivors=0`), so `len(real_survivors) = 0 < REAL_ARM_MIN_PRIMES (4)`
is `True` — the `if` branch fires, and the `else` branch containing the
`v1c.apply_decision_rule(...)` call is **never entered** on this run's
control flow, confirmed by reading the branch condition against the
independently-recomputed survivor count from §3, not by trusting
`apply_decision_rule_invoked=false` in the output. There is no placeholder
value passed anywhere: the `if` branch constructs `decision` directly from a
literal dict, with no call to `apply_decision_rule` of any kind, correct or
placeholder. `raw-result.json` records `apply_decision_rule_invoked: false`,
`apply_decision_rule_result: null`, consistent with the traced code.

**Verdict: PASS.** The new gate genuinely short-circuits before
`apply_decision_rule`'s call site; there is no disguised invocation with a
placeholder argument.

As a secondary check (not exercised on this run's data, but worth
confirming the code is not merely absent): the `not_evaluable_decision_rule_v3`
bypass logic **is** present and correctly written inside the `else` branch
(`if c_null_label_control_failure == "NOT-EVALUABLE": decision =
{"branch": "UNRESOLVED-BY-THIS-TEST", ...}` — never `DETECTED` — bypassing
`apply_decision_rule` entirely in that sub-case too), matching PF-2's fix
exactly. This branch is not reached on `RUN-SSIQ-a85692-c`'s actual data
(disclosed correctly as PD-3 in `execution_report.yaml`), so this is a
static-code-reading confirmation only, not a runtime one — the same
evidentiary-shape caveat that applies to `c_null_label_comparison_v3`'s
fit-and-bootstrap branch (§4) applies here too, and `execution_report.yaml`
discloses this explicitly (item (4) of `required_artifacts_note_diff_cross_check`).

## 7. DATA-UNAVAILABLE-BLOCKED does not reopen the Phase −1 gate

Read `main()` directly: `phase_minus1_gate_pass_already = True` and
`phase0_pass_already = True` are hardcoded literals, commented "UNCHANGED
from RUN-SSIQ-a85692-b; not reopened here" — there is no recomputation of
`M-COVERAGE` anywhere in `reanalyze_v3.py` (confirmed by `grep`: no
occurrence of `m_coverage` or `M-COVERAGE` as a computed quantity in this
file, only in the decision-reason prose string explaining why the two gates
are distinct). The new gate operates on `real_survivors`, itself derived
from `greedy_trapped_fraction` (`descent_metrics.per_prime`), a disjoint
field from the Phase −1 gate's `m_coverage_non_fp_fraction`
(`phase_minus1_real_search`), independently confirmed disjoint in
BATCH-005's own review. `RUN-SSIQ-a85692-b`'s Phase −1 gate pass
(`n_primes_coverage_pass=5>=4`) is not read, recomputed, or referenced by
value anywhere in `reanalyze_v3.py` — it is simply asserted true by the two
hardcoded literals, exactly matching `decision_rule_v3`'s own text ("the
Phase −1 gate itself... is UNCHANGED and was already passed... this
amendment does not reopen it").

**Verdict: PASS.** Genuinely disjoint checks on disjoint data, confirmed by
direct code reading rather than by trusting the decision-reason prose.

## 8. Diff-list cross-check against `required_artifacts_note`

Read `reanalyze_v3.py` directly against `specification_v3.yaml`'s
`required_artifacts_note` diff list (not the module's own docstring
paraphrase of it, and not `execution_report.yaml`'s own claimed
cross-check, which I re-derived independently):

- **NEW: `reanalyze_v3.py`, reads `RUN-SSIQ-a85692-b/raw-result.json`,
  implements `trapped_exclusion_filter_v3`/`c_null_label_comparison_v3`.**
  Confirmed: `main()` opens `args.run_b` with plain `json.load`; `grep`
  confirms the only subscripts of `run_b` used anywhere are
  `["descent_metrics"]["per_prime"]`, `["c_null_label"]["per_prime"]`, plus
  `["c_search_bias"]["magnitudes_comparable_flag"]` and
  `["correctness_gates"]["connectivity"]` inside the dead
  `>=4`-survivors branch. Both named functions exist as top-level,
  independently callable functions.
- **NEW, REQUIRED: synthetic self-test, independent of RUN-b's real
  data.** Confirmed §4 above.
- **IMPORTED UNCHANGED, BY REFERENCE: `ols_loglog_fit`/`bootstrap_gap_ci`
  from `descent_hitting_time.py`.** Confirmed: `import descent_hitting_time
  as dht`; `grep` for `def ols_loglog_fit` and `def bootstrap_gap_ci` inside
  `reanalyze_v3.py` returns **zero matches** — neither function is
  redefined or shadowed anywhere in this file, so every call is genuinely
  the imported, unmodified function object.
- **IMPORTED UNCHANGED, BY REFERENCE: `apply_decision_rule` from
  `compute_delta_e.py` (v1).** Confirmed: `import compute_delta_e as v1c`;
  `grep` for `def apply_decision_rule` inside `reanalyze_v3.py` returns zero
  matches. The call site `v1c.apply_decision_rule(...)` exists in the code
  at the location `decision_rule_v3` specifies, with the correct five
  named + two keyword arguments matching `compute_delta_e.py` line 549's
  signature exactly (`phase0_pass`, `phase_minus1_gate_pass`,
  `c_search_bias_control_failure`, `c_null_label_control_failure`,
  `c_connectivity_all_pass`, `m_gap_ci_lo`, `m_gap_ci_hi`) — confirmed by
  reading both signatures side by side, not merely trusting that the call
  "looks right."
- **UNCHANGED, NOT INVOKED AT ALL: `compute_delta_e_v2.py`'s search,
  smoke-test, admission, Phase −1 code.** `grep -nE
  "two_sided_search|build_smooth_table|run_phase_minus1|apply_truncation_fallback|
  run_c_search_bias|verify_modular_polynomials|build_all_graphs|
  run_correctness_gates|build_isogeny_graph|compute_delta_e_v2"
  reanalyze_v3.py` returns matches **only inside the module docstring's own
  prose** (lines 11–14, 37, listing what is *not* invoked) — zero
  occurrences as actual code (import statements or call expressions).
  `compute_delta_e_v2.py` itself is never imported. Additionally confirmed
  that importing `v1c`/`dht` does not itself trigger a search: both
  `compute_delta_e.py` and `descent_hitting_time.py` guard their `main()`
  behind `if __name__ == "__main__":`, so the module-level `import`
  statements execute no search code as a side effect.

**Verdict: PASS.** The diff-list cross-check holds against the actual code,
function for function, independently re-verified rather than accepted from
`execution_report.yaml`'s own claimed cross-check (item (4) of that
document's own cross-check — the disclosure that `apply_decision_rule`'s
call site exists but is unexercised on this data — is itself confirmed
accurate by my own trace in §6).

## 9. Overclaim / premature-closure check

- The experiment title ("fixing GD-8/GD-9") and hypothesis statement could,
  read carelessly, suggest GD-9's fix is validated end-to-end on real data.
  Checked directly: `manifest.yaml.validity_reason` states explicitly "This
  IS the only runtime evidence this batch supplies that
  c_null_label_comparison_v3's fit-and-bootstrap branch works correctly, per
  evidentiary_limitation_disclosure_v3" and separately "did NOT execute on
  this run's real data" — the distinction between "fixed in the code sense"
  (confirmed, §6/§8) and "validated against real data" (explicitly NOT
  claimed; only validated via the independent synthetic self-test, §4) is
  stated plainly in the run's own primary artifact, not buried or
  contradicted elsewhere. `execution_report.yaml`'s
  `executor_assessment.note` reinforces this: "No conclusion is drawn here
  about whether H-SSIQ-36e970's or H-SSIQ-137200's real-arm prediction is
  supported or refuted."
- `H-SSIQ-36e970.yaml` (read in full) correctly inherits `asymptotic_claim:
  null`, `heuristic_assumptions: []`, and `scope_ceiling.claim_tier: toy`
  unchanged; `status: proposed`, correctly not advanced by this run (only
  the Coordinator changes hypothesis status).
- `H-SSIQ-36e970`'s real-arm prediction (`gamma_greedy < gamma_random`)
  remains untested by this run: `decision.branch = DATA-UNAVAILABLE-BLOCKED`
  fires before any real gamma is computed on the real arm's surviving set
  (`descent_metrics_v3.ran = false`). No sentence anywhere in the reviewed
  package asserts H-SSIQ-36e970's prediction is supported, refuted,
  detected, or falsified.
- The receipt's own commit message states the flagged items are "Recorded
  VERBATIM AND NOT ENDORSED" — an honest framing this review's independent
  checks (§3–§8) now upgrade from "not endorsed" to "independently
  confirmed," not merely "plausible."

**Verdict: PASS**, with one **condition** carried forward (see Overall
verdict below): any future evidence or decision record citing this batch's
"GD-9 fixed" outcome must preserve the run's own distinction between
code-level correctness (confirmed by direct reading, §6/§8, and by the
synthetic self-test, §4) and real-data runtime validation (not established
by this batch; `c_null_label_comparison_v3`'s fit-and-bootstrap branch and
`not_evaluable_decision_rule_v3`'s bypass logic both remain unexercised on
any real dataset as of this batch).

## 10. Null-object-control framing (docs/inventor-protocol.md §3)

No statistical signal (correlation, bias, gamma estimate) is reported from
real data anywhere in this run — the new gate fires before any such
quantity would be computed, so the "does the quantity decay as the
destroying parameter increases" check does not apply to this run's own
real-data output. The synthetic self-test's own
`synthetic_c_null_label_control_failure=True` is a stated, expected property
of the constructed example (`m_gap_expected=0.5>0`, CI degenerates at
0.5>0), not a claim about any null object drawn from real data, and the
artifacts do not present it as such. C-NULL-LABEL itself — the null-object
control this entire amendment exists to make functional — remains
`NOT-EVALUABLE` on this dispatch's real data (§5); this is disclosed as a
limitation, not silently treated as a passing control. No artifact tell
found; nothing to flag here beyond what §4/§5/§9 already establish.

## 11. Infrastructure / budget sanity

Total measured wall-clock `0.0353s` against a `300s` budget, `ulimit -v
1048576` (1 GiB) never approached, single invocation, no infrastructure
failures, no prior attempts — consistent with the pre-freeze review's own
estimate that the budget was "generous by roughly two to three orders of
magnitude." No anomalies recorded (`execution_report.yaml.anomalies: []`),
independently consistent with `stdout.log`'s five printed lines matching
`raw-result.json` exactly and `stderr.log` being empty.

**Verdict: PASS.**

---

## Findings

- **F-1 [confirmed, not blocking, standing limitation].** This batch
  provides **zero runtime evidence on real data** that
  `c_null_label_comparison_v3`'s fit-and-bootstrap branch or
  `not_evaluable_decision_rule_v3`'s bypass logic work correctly — both
  remain code-verified only (§4, §6, §8) plus, for the fit-and-bootstrap
  branch specifically, synthetic-data-verified (§4). This is the exact,
  correctly disclosed limitation `evidentiary_limitation_disclosure_v3`
  predicted before this run executed and that this review independently
  confirms held. **What resolves it:** a future real-data run whose
  underlying descent data leaves `>=3` null-arm survivors (or `>=4`
  real-arm survivors with `<3` null-arm survivors, for the bypass branch
  specifically) — not something this batch's own data can supply, since
  `trapped_exclusion_filter_v3`'s threshold is pinned and correctly not
  loosened to force a different outcome.
- **F-2 [informational, non-blocking].** The synthetic self-test's own
  "control_failure=True" outcome (§10) is a designed property of the
  constructed example and is stated as such; a careless future citation
  could mistake this for evidence about real-data behavior. Not a defect in
  this batch's own artifacts, which state the distinction correctly, but
  worth naming so a downstream reader does not conflate the two.

## Overall verdict: **ADMIT-WITH-CONDITIONS**

The receipt is a genuine, content-verified, snapshot-committed record of a
run executed exactly as its frozen v3 contract specifies. Every
independently checkable claim in this package was re-derived from raw data,
from the transcribed source of the imported functions, or from direct
control-flow tracing — not accepted from the manifest's prose, the
Executor's own diff-list cross-check, or the pre-freeze review's own
numbers — and every one reproduced exactly or to far better than its stated
tolerance: the 10 declared path hashes (§1), the contract-freeze binding
(§2), the zero-survivor arithmetic in both arms (§3), the synthetic
self-test's analytic values (§4, hand-derived from `ols_loglog_fit`'s
formula, not merely re-run), the literal `NOT-EVALUABLE` string and its
control-flow origin (§5), `apply_decision_rule`'s genuine non-invocation
with no placeholder substitution (§6), the disjointness of the new gate from
the already-passed Phase −1 gate (§7), and the diff-list's function-level
accuracy (§8). No overclaim was found in the run's own artifacts (§9): the
distinction between "fixed in the code sense" and "validated against real
data" is stated plainly and repeatedly in `manifest.yaml` and
`execution_report.yaml` themselves.

It is admitted **with the condition** that any future ledger evidence or
decision record citing this batch's outcome as "GD-9 fixed" or
"C-NULL-LABEL wired" must carry F-1 explicitly: this batch's real-data
re-analysis supplies **no runtime evidence** that
`c_null_label_comparison_v3`'s substantive comparison logic, or
`not_evaluable_decision_rule_v3`'s bypass rule, work correctly on real,
non-degenerate data — only that they are correctly coded (confirmed by
direct reading) and correctly execute on a hand-constructed synthetic
example with a known analytic answer (confirmed by independent
re-derivation). This is not a weaker admission than BATCH-005's own
ADMIT-WITH-CONDITIONS pattern; it is the same discipline applied one layer
deeper, exactly as GD-9's standing repair requires.

This report establishes that `RUN-SSIQ-a85692-c` is admissible evidence of
exactly what it measured: `trapped_exclusion_filter_v3` correctly leaves
zero survivors in both arms of `RUN-SSIQ-a85692-b`'s already-collected data,
`decision_rule_v3`'s new gate correctly and mechanically derives
`DATA-UNAVAILABLE-BLOCKED` from that fact without reopening the Phase −1
gate, and the new `c_null_label_comparison_v3` code is correctly implemented
(by direct reading) and correctly executes end-to-end on independent
synthetic data with an analytically verified answer. It establishes nothing
about whether a delta_E-gradient exists, and nothing about H-SSIQ-36e970's
or H-SSIQ-137200's real-arm prediction beyond what
`DATA-UNAVAILABLE-BLOCKED` itself asserts — no data currently exists, under
the corrected trapped-vertex filter, on which that prediction could even be
tested.

```yaml
validation_report:
  id: VAL-BATCH-006
  task_id: TASK-20260805-47be12
  run_ids: [RUN-SSIQ-a85692-c]
  reviewed_commit: cc786884a485d85224cf44bf9e4aaf85be606e0c
  reviewed_commit_parent: 7f40426b041044b9074f8bf208971786bde83801
  artifact_checks:
    - {check: path_sha256_recompute, scope: "all 10 declared paths", result: PASS, mismatches: 0}
    - {check: commit_reachable_from_HEAD, result: PASS}
    - {check: commit_parent_matches_declared, result: PASS}
    - {check: commit_changed_exactly_declared_paths, result: PASS, detail: "11 changed files = 10 declared artifacts + receipt itself"}
    - {check: v1_v2_artifacts_untouched, result: PASS, detail: "git diff --stat 7f40426b cc786884 against every v1/v2 path returns empty"}
    - {check: contract_frozen_before_run, frozen_commit: 7f40426b, run_code_commit: 7f40426b, result: PASS, detail: "manifest.yaml.code.commit equals the freeze commit exactly, no intervening commit"}
    - {check: specification_v3_unmodified_since_freeze, result: PASS, detail: "git show 7f40426b:specification_v3.yaml is byte-identical to the working-tree copy"}
    - {check: required_artifacts_present, result: PASS, detail: "all 10 declared artifacts exist and parse"}
  metric_recomputations:
    - {metric: trapped_exclusion_filter_v3_real_arm_survivors, reported: 0, recomputed_from_RUN_b_raw_data: 0, method: "hand-applied threshold<=0.5 to descent_metrics.per_prime[p].greedy_trapped_fraction for p in {2437,3889,5737,7333}", result: MATCH}
    - {metric: trapped_exclusion_filter_v3_null_arm_survivors, reported: 0, recomputed_from_RUN_b_raw_data: 0, method: "hand-applied threshold<=0.5 to c_null_label.per_prime[p].greedy_trapped_fraction for the same four primes", result: MATCH}
    - {metric: synthetic_gamma_null_greedy, reported: 0.29999999999999993, expected_analytic: 0.3, method: "hand-derivation of ols_loglog_fit's gamma=sxy/sxx formula for an exact power law with c=1, showing gamma_fit=gamma_true exactly up to float rounding", result: MATCH, tolerance: "diff ~7e-17, well under stated 1e-9"}
    - {metric: synthetic_gamma_null_random, reported: 0.8, expected_analytic: 0.8, result: "EXACT MATCH"}
    - {metric: synthetic_m_gap_null, reported: 0.5000000000000001, expected_analytic: 0.5, result: MATCH, tolerance: "diff ~1e-16"}
    - {metric: synthetic_bootstrap_ci_degeneracy, reported: [0.4999999999999998, 0.5000000000000004], expected_analytic: "degenerate point at 0.5 (any bootstrap resample with >=2 distinct N reproduces gamma exactly on a noiseless power law)", method: "hand-derivation from ols_loglog_fit's exactness on any valid resample, independent of running the code", result: MATCH, ci_width: "~6e-16, floating-point noise not statistical spread"}
    - {metric: synthetic_r_squared, reported: [1.0, 1.0], expected_analytic: 1.0, result: "EXACT MATCH"}
  control_checks:
    - {control: trapped_exclusion_filter_v3, result: "CONFIRMED ZERO SURVIVORS BOTH ARMS", detail: "independently re-derived from RUN-SSIQ-a85692-b's own raw-result.json, not from this run's or the pre-freeze review's own numbers"}
    - {control: c_null_label_comparison_v3, result: "NOT-EVALUABLE, literal string, confirmed by direct control-flow trace", detail: "if len(null_survivors) < min_primes branch returns before any dht.* call; confirmed by reading the code, not by trusting evaluable=false"}
    - {control: apply_decision_rule_non_invocation, result: "CONFIRMED GENUINE, NO PLACEHOLDER", detail: "traced main()'s if/else directly: the DATA-UNAVAILABLE-BLOCKED branch constructs decision from a literal dict with zero call to apply_decision_rule of any kind"}
    - {control: not_evaluable_decision_rule_v3_bypass_logic, result: "CODE-VERIFIED, NOT RUNTIME-EXERCISED", detail: "present and correctly written (reports UNRESOLVED-BY-THIS-TEST, never DETECTED, bypassing apply_decision_rule) but never reached by this run's own data (real_survivors=0<4 fires the outer gate first) -- disclosed in execution_report.yaml, independently confirmed"}
    - {control: phase_minus1_gate_not_reopened, result: PASS, detail: "phase_minus1_gate_pass_already and phase0_pass_already are hardcoded True literals; no recomputation of m_coverage_non_fp_fraction anywhere in reanalyze_v3.py, confirmed by grep"}
    - {control: diff_list_function_level_cross_check, result: PASS, detail: "ols_loglog_fit/bootstrap_gap_ci/apply_decision_rule confirmed imported and never redefined (grep for def <name> inside reanalyze_v3.py returns zero matches for all three); compute_delta_e_v2.py and its search functions confirmed absent from all import/call sites, present only in docstring prose"}
    - {control: synthetic_self_test_independence_from_real_data, result: PASS, detail: "N_list and medians share no value with RUN-SSIQ-a85692-b's real N=[203,324,478,611] or its real median figures at any digit"}
  heuristic_validation_checks: []
  cost_model_checks:
    - {check: budget_realism, result: PASS, detail: "measured wall-clock 0.0353s against 300s budget, consistent with pre-freeze review's own two-to-three-orders-of-magnitude estimate"}
  proof_architecture_checks: []
  findings:
    - {id: F-1, severity: confirmed-standing-limitation-not-blocking, summary: "This batch supplies zero runtime evidence on real, non-degenerate data that c_null_label_comparison_v3's fit-and-bootstrap branch or not_evaluable_decision_rule_v3's bypass logic work correctly -- both are code-verified (and, for the fit-and-bootstrap branch, synthetic-data-verified) only, exactly as evidentiary_limitation_disclosure_v3 predicted and this review independently confirms held", resolution: "a future real-data run whose descent data leaves >=3 null-arm survivors (or the >=4-real/<3-null split for the bypass branch) would supply this; not producible from this batch's own pinned data without loosening the threshold, which is correctly not done"}
    - {id: F-2, severity: informational, summary: "The synthetic self-test's own control_failure=True outcome is a designed property of the constructed example (m_gap_expected=0.5>0); correctly stated as such in the artifacts, but a careless future citation could mistake it for evidence about real-data behavior", resolution: "no action required beyond this note; the run's own artifacts already state the distinction correctly"}
  verdict: passed
  overall_admissibility: ADMIT-WITH-CONDITIONS
  limitations:
    - "Session-only independence: this review shares a model family with the producer, the pre-freeze reviewer, and every prior reviewer in this lineage; it is not model-independent corroboration and does not satisfy or advance a closure quorum."
    - "This report makes no claim about whether a delta_E-gradient exists, about lever L4's status, or about H-SSIQ-36e970's or H-SSIQ-137200's real-arm prediction -- DATA-UNAVAILABLE-BLOCKED means no data currently exists, under the corrected trapped-vertex filter, on which that prediction could be tested."
    - "Any future citation of this batch's 'GD-9 fixed' outcome must carry F-1: real-data runtime validation of c_null_label_comparison_v3's substantive branch remains absent; only code-level correctness and independent synthetic-data correctness are established."
    - "Toy scale throughout, inherited unchanged from H-SSIQ-36e970.scope_ceiling: at most the 5 primes RUN-SSIQ-a85692-b already admitted, N in [203, 718] before any filtering (narrower, [203,611], for the 4 primes actually contributing pre-filter). Nothing transfers to cryptographic scale."
  artifact_paths:
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-006/reviews/VAL-BATCH-006.md
```
