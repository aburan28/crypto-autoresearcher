# Validation report — EXP-ICINV-4d33aa, contract version 3

- **Validator task**: independent review of TASK-20260810-3c448e's execution
  (Executor session), scoped to EXP-ICINV-4d33aa v3 only. `harness/exp_canl.py`,
  `harness/canonical_height.py`, `harness/run_canl.py` are out of scope and were
  not reviewed or touched.
- **Snapshot reviewed**: commit `b9466e54` on
  `claude/ecdlp-endomorphism-analysis-4m2w3z` (the execution-report commit; task
  starting commit `d6ab7abfc440bddcca97fd5c60e950e557d52cc8`, confirmed on the
  branch and an ancestor of the reviewed commit). This is a Coordinator-committed
  snapshot, not a working-tree-only artifact; the only uncommitted change in the
  tree at review time was `harness/run_canl.py`, which belongs to the unrelated,
  concurrently-running EXP-CANL-96b0ad session and is disregarded.
- **Documents read**: `experiments/EXP-ICINV-4d33aa/amendments/v3.yaml`,
  `v2.yaml`, `specification.yaml`, `ledger/handoffs/TASK-20260810-3c448e.yaml`,
  `ledger/decisions/DEC-20260809-de11f9.yaml`, the execution report, and every
  raw artifact cited below.
- **Verdict: `passed_with_findings`.** Every one of the eight required
  technical checks independently reproduces from raw committed artifacts and
  none is contradicted. Two additional findings (F1, F2), found during
  independent review rather than requested by the task's numbered checklist,
  bear directly on how conservatively this run's evidence should be
  characterized and on the completeness of the execution report's deviation
  disclosure. Neither invalidates the run under the frozen contract's own
  invalidation rules, but both should be read by the Coordinator before any
  evidence record is drafted from `RUN-ICINV-849d1d`.

---

## Checks 1–8 (task-specified)

### 1. Terminal state `OUTCOME-C` re-derived from raw artifact — PASS

Read directly from `RUN-ICINV-849d1d/decision-rule-evaluation.json`:
`aggregate_persistence: PERSISTS`, `majority_counts: {PERSISTS: 2, COLLAPSES:
1}`, `majority_shape: 2-1`, `stratification_verdict: NEGATIVE`,
`invalidations: []`, `premise_failures: []`, `persistence_verdicts: {2003:
PERSISTS, 4001: PERSISTS, 6007: COLLAPSES}`.

Applying `specification.yaml`'s `frozen_decision_rule` to these inputs by hand:
`state_0_INVALID` does not fire (`invalidations` empty, 3/3 primes yield a
verdict, not fewer than two). `state_1_PREMISE_FAILED` does not fire
(`premise_failures` empty). `state_2`: majority over 3 primes with 2 PERSISTS,
1 COLLAPSES is `PERSISTS`, so `OUTCOME-A` does not fire. `state_3`: evaluated
because aggregate is `PERSISTS`; `S_prime_positive` is `False` at all three
primes, so the aggregate `S` is `NEGATIVE` and `OUTCOME-B` does not fire.
`state_4_OUTCOME_C` fires: `PERSISTS` and `S` `NEGATIVE`. This matches the
emitted `terminal_state: OUTCOME-C` exactly.

I additionally read the code that computed this (`harness/run_fullgroup.py`,
`evaluate_decision_rule_v2`/`v3`, lines ~2147–2344 and 1686–1719) and confirmed
it implements exactly this state machine over `stage1s`/`stage2s`/`stage3s`
dicts read from the run's own committed files — not a stub or a
post-hoc-selected literal. Per-prime `F_p` values were independently
recomputed by counting `persists_row: true` entries in each run's own
`persistence` block: 2003 → 9/13 = 0.6923076923076923, 4001 → 9/13 =
0.6923076923076923, 6007 → 5/13 = 0.38461538461538464 — all match the run's
own reported `F_p` to full float precision.

### 2. Change A7 CI-overlap gate, p=6007 fb=4/fb=5 — PASS

Recomputed the Wilson-Hilferty CI myself, independently, from the formula in
amendment v3.yaml change A7 (not by importing any campaign code):

```
df = n_curves - 1;  stat = df*ratio
lo = df*(1 - 2/(9df) - 1.96*sqrt(2/(9df)))**3
hi = df*(1 - 2/(9df) + 1.96*sqrt(2/(9df)))**3
CI = [stat/hi, stat/lo]
```

At `n_curves=140` (from `RUN-ICINV-ff0806/baseline-reproduction.json`):

| fb | ratio (raw) | my CI | run's `r_true_95pct_ci` | overlaps [1.3,3.6]? |
|---:|---|---|---|---|
| 4 | 1.2315292605941532 | `[0.9864520254143091, 1.5813756882794519]` | identical | True (both) |
| 5 | 1.1125313273888915 | `[0.891134962323324, 1.4285734410673028]` | identical | True (both) |
| 6 | 1.4518421211510657 | `[1.1629221057243266, 1.864273880509101]` | identical | True (both, no regression) |

My independently computed CIs match the run's reported `r_true_95pct_ci` to
every displayed digit. `gate_passed: True` for `RUN-ICINV-ff0806` is correct
given these inputs and the frozen `[1.3, 3.6]` band, which I confirmed is
untouched (`checks.every_row_in_band_1_3_to_3_6_gate_definition` names the
[1.3, 3.6] literal, not a re-derived one).

### 3. Change A8 cross-check — PASS

Read `wilson-hilferty-crosscheck.json` in `RUN-ICINV-849d1d` and
`RUN-ICINV-476e12`: byte-identical across both runs, `all_within_tolerance:
true` at every probed df, every `relative_error_*` at or below ~1e-15–1e-16,
nine orders of magnitude inside the required 1e-9.

Independently reproduced one probed point (df=69) myself, from scratch, using
`harness/exp_icinv_fullgroup.py:chi2_wilson_hilferty_bounds` for the local
value and my own bisection against the **committed**
`harness/exp_icinv.py:binomial_null_verdict`'s verdict-classification boundary
(not copy-pasted from `wilson_hilferty_crosscheck`'s own bisection code):
local `(lo, hi) = (47.91662236377866, 93.85997077186359)`; the committed
function's own classification boundary, located by my independent bisection,
sits at `93.85997077186362` (relative difference `3.03e-16`) — matching the
run's own reported `committed_function_measured_hi` for df=69 exactly. The
cross-check is genuine, not circular: it compares against
`binomial_null_verdict`'s own `if/elif` classification behavior, which does
not import or otherwise depend on `wilson_hilferty_band`.

### 4. Change A9 data provenance — PASS

**p=2003 audit (contract-version classification).** Checked every candidate
manifest's `run.handoff_id` myself:

| candidate | `handoff_id` in manifest | matches execution report's claim |
|---|---|---|
| `RUN-ICINV-fg-stage1-p2003` | `TASK-20260807-3414fc` (v1) | yes |
| `RUN-ICINV-fg-nullr-p2003` | `TASK-20260807-3414fc` (v1) | yes |
| `RUN-ICINV-fg-nullr-v2-p2003` | `TASK-20260807-3414fc` (v1) | yes |
| `RUN-ICINV-fg-nullr-v3-p2003` | `TASK-20260807-3414fc` (v1) | yes |
| `RUN-ICINV-65bc20` | `TASK-20260809-caa93e` (v2) | yes |
| `RUN-ICINV-84bd66` | `TASK-20260809-caa93e` (v2) | yes |

Cross-checked with `git log --diff-filter=A` on each manifest path (independent
of the manifest's own self-reported fields): `RUN-ICINV-fg-stage1-p2003` was
first added by commit `f6697e97` (2026-08-07, version-1 window);
`RUN-ICINV-65bc20` and `RUN-ICINV-84bd66` were first added by `d7aa5701` and
`627f7ca5` respectively (2026-08-09) — the exact two commit hashes amendment
v3.yaml names as "version 2's Stage 1/2 commits". The audit table in the
execution report is correct.

**p=4001/p=6007 reuse-without-redraw.** Read
`change-a9-provenance.json` in `RUN-ICINV-476e12` and `RUN-ICINV-ff0806`: both
name a `source_run_id`, `source_per_curve_measurements_path`, and
`source_raw_result_path` with `sha256` values. I independently recomputed
`sha256sum` on the four named source files (`RUN-ICINV-40622f/cell-aggregates.json`,
`RUN-ICINV-40622f/per-curve-measurements.json`, `RUN-ICINV-40622f/raw-result.json`,
`RUN-ICINV-c670c2/per-curve-measurements.json`, `RUN-ICINV-c670c2/raw-result.json`)
and every one matches the declared hash exactly (bit-for-bit). `RUN-ICINV-40622f`
and `RUN-ICINV-c670c2` themselves carry `handoff_id: TASK-20260809-caa93e`
(version 2), consistent with the claim that they are version-2's own Stage-3
records.

### 5. `harness/exp_icinv.py` edit prohibition — PASS

`git diff d6ab7abf HEAD -- harness/exp_icinv.py` is empty. `git log --follow`
on the file shows no commit after `d6ab7abf` (the task's own starting commit).
`git hash-object harness/exp_icinv.py` = `883d554...` matches the sha256 pinned
in every version-3 run's `manifest.yaml` (`byte_identical: true`,
`status: clean`, in every one of the four completed and one failed run).

### 6. SR6 (no outcome shopping) — PASS

Commit chronology: `654dc626` ("implement changes A7/A8/A9", 15:24:32) precedes
`e91366a3` ("Stage 3 runs", 15:26:41) precedes `72af0034` ("aggregate decidev3
run, terminal_state OUTCOME-C", 15:26:56) precedes `b9466e54` (execution
report, 15:30:04). The decision logic existed in committed code before any
version-3 run executed. `decision-rule-evaluation.json` is produced by
`evaluate_decision_rule_v3`/`v2`, called from inside `main_v3`, and is a run
artifact, not a human-authored file — I confirmed this by reading the calling
code (§1 above), not merely trusting the filename.

### 7. `check_run_source_provenance.py --strict --since-commit d6ab7abf...` — PASS

Ran it myself:

```
5 pinned, 0 unpinned, 0 unreadable, of 5 run manifest(s) in scope
  of the pinned, 2 also ran from a fully clean tree
exit code: 0
```

Matches the execution report's §7 table and quoted output exactly, including
the "2 also ran from a fully clean tree" detail (the other 3 ran with an
overall-dirty tree — expected, given the concurrent unrelated
`harness/run_canl.py` edits from the other session — but every individually
executed source file is still pinned and `status: clean` per-file).

### 8. Budget and scope — PASS

Summed `wall_seconds` across the five manifests (2.197569 + 1.981584 +
7.315392 + 56.548344 + 0.42566) = 68.47 s ≈ the reported "~68.5 s". Summed
`cpu_seconds` = 72.36 s ≈ 0.0201 CPU-hours ≈ the reported "~72.4 s
(≈0.020 CPU-hours)". Peak `peak_rss_bytes` across all five = 256,483,328 bytes
(≈245 MB), well under the 4 GB cap. 5 runs used of 30 budgeted. `claim_tier:
toy`, `sota_delta: 0` match `specification.yaml`'s own `scale_relevance` block
verbatim; nothing in the execution report overstates scope.

---

## Findings from independent review (not on the task's numbered checklist)

### F1 (major) — The "closest to blind" framing for p=2003 is not supportable; the entire 2–1 majority rests on previously-known numbers, not three fresh primes

Amendment v3.yaml's `confirmatory_status_note` states: *"A confirmatory test of
H-ICINV-6c7920 under this design needs a prime this amendment's own drafting
never touched -- p=2003 is the closest this experiment has to that."* The
execution report treats `RUN-ICINV-4bf6c8` as a **fresh** Stage-3 measurement
at p=2003 (§3b: *"Stage 3... had no valid record at p=2003 under any version,
so a fresh Stage 3 measurement was required... and was run"*), and never
revisits the "closest to blind" characterization.

I independently compared `RUN-ICINV-4bf6c8/raw-result.json`'s persistence
block against the pre-existing, already-committed version-1 run
`RUN-ICINV-fg-primary-p2003/raw-result.json` (same class: trace=36,
order=1968, n_curves=104; same `frozen_parameters`, including seed 20260807
and T=400). All 13 rows of `VR_pooled` at `seed=20260807|T=400` are
**bit-for-bit identical** between the two runs:

```
fb=4:  0.9554704490630147 == 0.9554704490630147
fb=5:  1.1090666156013722 == 1.1090666156013722
...    (all 13 rows identical)
fb=22: 1.3558162685151962 == 1.3558162685151962
```

`F_p` (0.6923076923076923), `per_prime_binary` (PERSISTS), and
`S_prime_positive` (False, `S_row_fraction` 0.07692307692307693) are also
identical between the two runs. `RUN-ICINV-fg-primary-p2003` was executed
**2026-08-07T17:44** (per its own manifest `timing.started_at`) — the same day
version 1 was dispatched, and roughly two days before amendment v3 was even
filed (2026-08-09) and three days before it was approved and executed
(2026-08-10).

This is not merely something I inferred by diffing files: amendment
**v2.yaml's own `confirmatory_status_note`** (filed 2026-08-07, referenced by
v3.yaml's own `refs:` list) states outright: *"The version-1 execution has
already exposed this Coordinator to two primes' worth of persistence
statistics (F_p = 0.6923 at p = 2003 and p = 4001, PERSISTS at both...)."*
The campaign's own prior written record already discloses that the p=2003
persistence result was known before v2 was drafted — two amendments and three
days before v3's "closest to blind" language was written. v3.yaml does not
mention or reconcile this prior disclosure when making its "closest to blind"
claim, and the execution report does not either.

The procedural distinction the execution report draws — that no *contract-admissible*
Stage-3 record existed at p=2003 under any version, so a new run was required
by A9 — is correct and was executed properly; I am not disputing that the run
itself was procedurally compliant. What is not supportable is the **epistemic**
claim that this makes p=2003 a genuinely new, informative measurement.
Amendment v3's own A9 rationale for reusing p=4001/p=6007 without redraw is
that the sampler is deterministic given seed 20260807, so "a genuine re-draw
... would reproduce the SAME ... numbers exactly." That argument applies with
identical force to p=2003: the "fresh" run reproduces, to the bit, numbers
that were already sitting in the repository and already known to the
Coordinator's own prior amendment. **All three primes' persistence and
stratification verdicts that feed `OUTCOME-C`** — not just p=4001 and p=6007,
which the execution report already flags as reused — **were determined and,
per the campaign's own record, substantially already known before amendment
v3 was drafted.** There is no prime in this 2–1 majority that represents a
genuinely blind measurement taken after the gate redesign was fixed.

**Consequence for evidence strength.** `preliminary` (per
`confirmatory_status: exploratory_only`) is the right direction but, on this
finding, understates how non-blind this run is. The execution report's own
framing suggests the *only* source of non-blindness is (a) the A7 gate having
been engineered around the two rows that motivated it, and (b) reusing
p=4001/p=6007's measurements. F1 shows a third, undisclosed source: p=2003's
own numbers were also already available. Any evidence record drawn from
`RUN-ICINV-849d1d` should state plainly that **zero** of the three primes in
the reported majority represent a fresh, blind test under the redesigned
protocol, not just the two the execution report names, and the "closest to
blind" language should not be repeated without this qualification.

### F2 (moderate) — Every version-3 run's manifest self-misidentifies as contract version 2 / handoff TASK-20260809-caa93e; undisclosed

`harness/run_fullgroup.py` defines `HANDOFF_ID_V3 = "TASK-20260810-3c448e"`
(line 139) but this constant is **never referenced anywhere else in the
file** — it is dead code. The shared manifest-writing function
`write_run_package` (used by both the v2 and v3 code paths) hard-codes the
module-level `HANDOFF_ID` (`= "TASK-20260809-caa93e"`, version 2's dispatch)
and `CONTRACT_VERSION`/`AMENDMENT_PATH` (version 2's values) into
`manifest.yaml`'s `run.handoff_id`, `run.contract_version`,
`run.protocol_amendment`, and `run.inference.handoff_id` fields, regardless of
which contract version actually produced the run.

Confirmed directly in every version-3 run's committed `manifest.yaml`,
including the aggregate decide run:

```
RUN-ICINV-476e12/manifest.yaml:  handoff_id: TASK-20260809-caa93e
                                  contract_version: 2
                                  protocol_amendment: .../amendments/v2.yaml
RUN-ICINV-849d1d/manifest.yaml:  handoff_id: TASK-20260809-caa93e
                                  contract_version: 2
                                  protocol_amendment: .../amendments/v2.yaml
```

(identical for `RUN-ICINV-ff0806`, `RUN-ICINV-4bf6c8`, and the failed
`RUN-ICINV-476e12-failed`). Only `manifest.yaml`'s `run.stage` field
(`3v3`/`decidev3`) and the separate JSON artifact
`decision-rule-evaluation.json` (whose `contract_version`/`protocol_amendment`
fields **are** correctly patched to `3`/`v3.yaml` by
`evaluate_decision_rule_v3`, lines 1701–1702) reveal that these are version-3
runs. `code.commit` is unaffected (captured live from git state, not from the
stale constant), so the p=2003 provenance audit in §3b of the execution
report — which cross-references `code.commit` against `git log
--diff-filter=A` rather than trusting `handoff_id` — is not undermined by
this defect, and neither is check #7's `check_run_source_provenance.py`
result (scoped by commit range, not by manifest `handoff_id`).

This is a genuine, real defect (not a fabrication and not a scoring error) and
it is **not mentioned** in the execution report's "Deviations" section, which
lists only D-v3-1 (the `_print_sweep` KeyError) and D-v3-2 (the amendment's
candidate list omitting the short-id p=2003 records). It should have been:
this campaign places unusual emphasis on exactly this kind of
self-identifying provenance (A6's hash-pinning requirement, A9's own audit
methodology, which is built around reading `manifest.run.handoff_id` to
classify a run's contract version). A future auditor who trusts
`manifest.run.contract_version`/`handoff_id` at face value — as change A9's
own stated audit method does for the p=2003 Stage-1/2 candidates — would
misclassify these five version-3 runs as version-2 artifacts. Recommend a
scoped follow-up fix (wire `HANDOFF_ID_V3`/`CONTRACT_VERSION_V3`/
`AMENDMENT_PATH_V3` through `write_run_package`, or an explicit version
parameter) before any further runs are dispatched under this driver, and a
note in any Coordinator record citing these five runs that their
`manifest.yaml` self-identification fields are wrong and `code.commit` /
`decision-rule-evaluation.json` are the fields to trust instead.

### Answers to the task's explicit review questions

- **Is `preliminary` the correct cap?** Directionally yes, but see F1: the
  stated reasons for the cap (A7 engineered around known numbers; p=4001/6007
  reused) are real but incomplete. The full picture is that no prime in the
  2–1 majority is a blind measurement under the redesigned protocol. This
  argues for the Coordinator to record, alongside `preliminary`, an explicit
  statement that the run's confirmatory value is zero-primes, not
  one-prime-partial, and that a genuinely confirmatory test still requires
  primes touched by neither version 1, 2, nor 3.
- **Is the 2–1 majority (p=6007 dissenting) reported honestly?** Yes on its
  own numeric terms — it is stated plainly in the first table of §1 of the
  execution report, not buried, and the dissenting prime is named as the
  contract's own `evidence_strength_calibration_frozen` requires. F1 does not
  contest this disclosure; it contests a separate claim (blindness) made
  elsewhere in the same documents.
- **Are D-v3-1/D-v3-2 complete, or is there an unmentioned deviation?**
  D-v3-1 and D-v3-2 are both independently verified as described (§ above:
  D-v3-1's `KeyError` traceback and `failed_infrastructure` status confirmed
  from `RUN-ICINV-476e12-failed`'s own `stderr.log`/`manifest.yaml`; D-v3-2
  confirmed via the manifest `handoff_id` audit in check #4). F2 is a real,
  additional, unmentioned deviation.

---

## Artifact paths cited

- `experiments/EXP-ICINV-4d33aa/amendments/v3.yaml`,
  `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml`,
  `experiments/EXP-ICINV-4d33aa/specification.yaml`
- `ledger/handoffs/TASK-20260810-3c448e.yaml`,
  `ledger/decisions/DEC-20260809-de11f9.yaml`
- `coordination/goals/GOAL-ENDO-001/batches/BATCH-74ebef/execution/EXP-ICINV-4d33aa-v3/execution_report.md`
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-849d1d/` (decision-rule-evaluation.json,
  manifest.yaml, wilson-hilferty-crosscheck.json)
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-476e12/` and
  `RUN-ICINV-476e12-failed/` (manifest.yaml, stderr.log, stdout.log,
  baseline-reproduction.json, wilson-hilferty-crosscheck.json,
  change-a9-provenance.json, raw-result.json, coverage-certificates.json)
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-ff0806/` (baseline-reproduction.json,
  change-a9-provenance.json, raw-result.json, coverage-certificates.json,
  wilson-hilferty-crosscheck.json)
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-4bf6c8/` (raw-result.json,
  baseline-reproduction.json, change-a9-p2003-audit.json,
  coverage-certificates.json)
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-fg-primary-p2003/` (raw-result.json,
  manifest.yaml) — the pre-existing version-1 record central to Finding F1
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-fg-stage1-p2003/`,
  `RUN-ICINV-fg-nullr-p2003/`, `RUN-ICINV-fg-nullr-v2-p2003/`,
  `RUN-ICINV-fg-nullr-v3-p2003/`, `RUN-ICINV-65bc20/`, `RUN-ICINV-84bd66/`
  (manifest.yaml, for the A9 p=2003 audit cross-check)
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-40622f/`,
  `RUN-ICINV-c670c2/` (cell-aggregates.json, per-curve-measurements.json,
  raw-result.json — sha256-recomputed against `change-a9-provenance.json`)
- `harness/exp_icinv.py` (hash-verified unmodified), `harness/exp_icinv_fullgroup.py`
  (`chi2_wilson_hilferty_bounds`, `wilson_hilferty_band`, `wilson_hilferty_crosscheck`,
  `r_true_95pct_ci` read and partially re-executed), `harness/run_fullgroup.py`
  (`evaluate_decision_rule_v2`/`v3`, `write_run_package`, `HANDOFF_ID`/`HANDOFF_ID_V3`/
  `CONTRACT_VERSION`/`CONTRACT_VERSION_V3` read)
- `tools/check_run_source_provenance.py` (executed directly)
- git commits `d6ab7abf` (task start), `654dc626`, `e91366a3`, `72af0034`,
  `b9466e54` (reviewed snapshot); `f6697e97`, `d7aa5701`, `627f7ca5`,
  `9591caac` (cross-referenced for the A9 p=2003 audit and F1's timeline)

## Limitations of this review

- I did not independently re-derive the tail-checks (`tail-checks.json`),
  the variance-decomposition identity check's numeric result beyond confirming
  `identity_all_hold: True`/`dropped_or_short_cells: []` from each stage-3
  run's raw result, or the NULL-R matched-null / planted-signal (Arm C)
  numbers beyond reading them as reported. These are cited from the run's own
  artifacts, not independently recomputed by this Validator.
- I did not verify `stratified_stats`/`persistence_and_stratification`'s S1/S2/S3
  arithmetic cell-by-cell; I verified only the aggregate `S_prime_positive`/`F_p`
  values by direct row-counting against the frozen thresholds, and confirmed
  the decision-rule code correctly consumes those aggregates.
- This report makes no claim about H-ICINV-6c7920, EV-ENDO-10109d,
  RQ-ICINV-475b5e, or GOAL-ENDO-001. Toy scale throughout (p ≤ 6007),
  `claim_tier: toy`, `sota_delta: 0`. Nothing here supports or rejects an
  ECDLP cost claim in either direction.
- No hypothesis or goal status is changed by this report. That is reserved
  for the Coordinator, on a separate ledger archive, after this and the
  companion Red Team/independent review return.
