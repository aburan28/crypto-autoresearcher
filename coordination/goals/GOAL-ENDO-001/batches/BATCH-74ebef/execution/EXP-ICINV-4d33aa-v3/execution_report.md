# Execution report — EXP-ICINV-4d33aa, contract version 3

- **Handoff**: `TASK-20260810-3c448e` (coordinator → executor)
- **Goal / batch**: GOAL-ENDO-001 / BATCH-74ebef
- **Contract**: `experiments/EXP-ICINV-4d33aa/specification.yaml` (v1, approved
  2026-08-07), as amended by the approved, frozen
  `experiments/EXP-ICINV-4d33aa/amendments/v2.yaml` (changes A1–A6, still in
  force) and `experiments/EXP-ICINV-4d33aa/amendments/v3.yaml` (changes
  A7–A9, approved 2026-08-10)
- **Branch**: `claude/ecdlp-endomorphism-analysis-4m2w3z`
- **Task starting commit**: `d6ab7abfc440bddcca97fd5c60e950e557d52cc8`
  (`origin/main` at dispatch time: `2e530e6b59d2918c49517a4ac179f0e3dd5f80a2`,
  an ancestor of the starting commit — the branch was already up to date with
  `origin/main`; no merge was needed or performed)
- **Executed at**: 2026-08-10

**This report records what ran and what did not. It interprets nothing.** No
evidence record is written here, no hypothesis status is moved, and nothing is
characterised about `EV-ENDO-10109d`, `RQ-ICINV-475b5e` or `GOAL-ENDO-001`.
Those are Coordinator acts on a later ledger archive after independent review.
Per amendment v3's `confirmatory_status: exploratory_only` (STRENGTHENED
beyond version 2's own reason — see §6), any evidence record arising from
this run is pre-capped at `preliminary` regardless of outcome.

---

## 1. Emitted terminal state

```
terminal_state: OUTCOME-C
```

Emitted by the frozen decision rule (unchanged by amendment v3) from
**inside** the run (SR6, no outcome shopping), by `RUN-ICINV-849d1d`, over
three version-3 Stage-3 records plus the reused, valid version-2 Stage-1/
Stage-2 records, at the contract's own `target_count_primary = 400` and first
frozen seed `20260807`.

| field | value |
|---|---|
| `terminal_state` | `OUTCOME-C` |
| `aggregate_persistence` | `PERSISTS` |
| `majority_counts` | `PERSISTS 2, COLLAPSES 1` (`majority_shape` `2-1`) |
| `stratification_verdict` | `NEGATIVE` (`S_prime_positive` false at all three primes) |
| `invalidations` | none |
| `premise_failures` | none |

Per-prime persistence:

| prime | `F_p` (Arm B) | verdict | rows | inconclusive | `S_prime_positive` |
|---|---|---|---|---|---|
| 2003 | `0.6923076923076923` | **PERSISTS** | 13 | 0 | `False` |
| 4001 | `0.6923076923076923` | **PERSISTS** | 13 | 0 | `False` |
| 6007 | `0.38461538461538464` | **COLLAPSES** | 13 | 0 | `False` |

p = 6007 is the dissenting prime in the 2–1 majority (per the contract's
`evidence_strength_calibration_frozen`, a 2–1 majority caps any resulting
evidence record at `preliminary` and requires the dissenting prime to be
named — done here).

`OUTCOME-C` fires when the aggregate persistence verdict is `PERSISTS` and the
stratification verdict `S` is `NEGATIVE` (contract `state_4_OUTCOME_C_neither`).
Per the contract's own success criterion, `OUTCOME-C` **fully satisfies** it
and is not a lesser deliverable than any other outcome.

---

## 2. Change A8 — the Wilson-Hilferty cross-check (blocking precondition on A7)

`chi2_wilson_hilferty_bounds(df, z)` was added to
`harness/exp_icinv_fullgroup.py` as a thin alias of the module's pre-existing
`wilson_hilferty_band` (itself the same three-line closed-form reimplementation
of `harness/exp_icinv.py:binomial_null_verdict` lines 428–433, already
continuously cross-checked against every real measured cell in this
experiment via `nullb`'s `AssertionError` guard). `wilson_hilferty_crosscheck`
implements change A8's own mandatory, artifact-producing self-check: it
constructs synthetic per-curve rate data at each probed `df` and **empirically
bisects** for the exact statistic at which the **committed**
`exp_icinv.binomial_null_verdict`'s own verdict flips between
`under-dispersed`/`invariant`/`over-dispersed` — that boundary *is* the
committed function's own `(lo, hi)` by construction of its own
`if/elif` classification, so the comparison is a genuine two-implementation
cross-check rather than a restatement of the same formula against itself (the
committed function does not return `(lo, hi)` programmatically at all — only a
verdict string and a `detail` string rounded to 2 decimal places, far coarser
than the required tolerance, which is why parsing was not used).

Run **once per run** (identically in each of the four version-3 runs), before
any gate result was interpreted:

| `df` | `n_curves` | local `hi` | committed-measured `hi` | rel. err. `hi` | `lo` reachable | local `lo` | committed-measured `lo` | rel. err. `lo` | within 1e-9 |
|---:|---:|---|---|---|---|---|---|---|---|
| 1 | 2 | 4.928019916282493 | 4.928019916282493 | 1.80e-16 | **No** (analytic `lo` < 0) | −0.0031233456 | — | — | **True** |
| 5 | 6 | 12.821881652935673 | 12.821881652935676 | 2.77e-16 | Yes | 0.7976493210012301 | 0.7976493210012301 | 0.0 | **True** |
| 20 | 21 | 34.171886921470524 | 34.17188692147053 | 2.08e-16 | Yes | 9.574760431067203 | 9.574760431067203 | 0.0 | **True** |
| 69 | 70 | 93.85997077186359 | 93.85997077186362 | 3.03e-16 | Yes | 47.91662236377866 | 47.91662236377866 | 0.0 | **True** |
| 138 | 139 | 172.41567380040422 | 172.4156738004043 | 4.95e-16 | Yes | 107.3670239198993 | 107.36702391989932 | 2.65e-16 | **True** |
| 139 | 140 | 173.53359597056 | 173.53359597056001 | 1.64e-16 | Yes | 108.24914565926782 | 108.24914565926782 | 0.0 | **True** |

`all_within_tolerance: true` at every probed `df`, in every run (full detail:
`wilson-hilferty-crosscheck.json` in each of `RUN-ICINV-476e12`,
`RUN-ICINV-ff0806`, `RUN-ICINV-4bf6c8`, `RUN-ICINV-849d1d`, and the failed
`RUN-ICINV-476e12-failed`). Every measured relative error is at or below
float64 precision (~1e-16), roughly nine orders of magnitude inside the
required 1e-9 relative tolerance.

**Note on which `df` values this run actually used.** The primary class sizes
measured were `n_curves = 104` (p=2003, df=103), `138` (p=4001, df=137), `140`
(p=6007, df=139). Only df=139 exactly matches a probed value. The amendment
names `{1, 5, 20, 69, 138, 139}` as a *minimum* probe set covering the
campaign's stratum floors and both class sizes already in use elsewhere in
this contract, not a claim that every df actually used here would be probed
exactly. Because `chi2_wilson_hilferty_bounds` is one closed-form expression
evaluated per `df` (not a per-df lookup table or an interpolation), verifying
it against the committed function at six representative points spanning 1 to
139 certifies the *formula*, which is what change A8 requires; it does not
additionally certify df=103 or df=137 as distinct facts. This is reported
plainly rather than left implicit.

---

## 3. Change A9 — data provenance

### 3a. p = 4001 and p = 6007: reuse without redraw

Both primes' Stage-3 measurements were read from their own committed
version-2 run records **without redrawing samples**, per amendment v3's own
argument that Arm A0 is deterministic given the frozen seed (20260807) and a
genuine re-draw would reproduce the identical numbers.

| prime | source run | `cell-aggregates.json` exists? | method used |
|---|---|---|---|
| 4001 | `RUN-ICINV-40622f` | Yes (its SR3 gate passed under version 2) | read directly |
| 6007 | `RUN-ICINV-c670c2` | **No** (its SR3 gate failed under version 2, before Arm B's cells were aggregated) | **reconstructed** from `per-curve-measurements.json` |

The reconstruction path (`reconstruct_rows_from_columnar` +
`harness.run_fullgroup.cells_for`) was validated before being relied on: it
was run against `RUN-ICINV-40622f`, whose per-curve table can be independently
checked against its own already-committed `cell-aggregates.json`, and
reproduced all 351 of that run's cells' pooled variance ratios exactly
(0 mismatches at 1e-9 absolute tolerance). This validation is not itself a
run artifact; it is recorded here as the check performed before the identical
code path was used, unvalidated, on p=6007's data (which has no ground-truth
`cell-aggregates.json` to check against, precisely because its gate had
failed and its Arm B cells had never been aggregated under version 2).

Every run's `change-a9-provenance.json` names the exact source run id, path,
and sha256 of every file read (`raw-result.json` and
`per-curve-measurements.json`), and lists which fields were read unchanged
from the source versus recomputed in this run (`cells`,
`baseline_reproduction`, `persistence`, `tail_checks`) — the same discipline
amendment v2 change A4 requires of `baseline-provenance.json`.

### 3b. p = 2003: the mandatory audit, performed and declared

Stage 3 at p=2003 was never executed under version 2 (SR3 halted the
per-prime execution order `[4001, 6007, 2003]` at p=6007, before p=2003 was
reached) or under version 1 (version 1's own p=2003 primary-class run,
`RUN-ICINV-fg-primary-p2003`, predates the SR3 baseline-reproduction control
entirely and never evaluated it).

**Audit method**: for every candidate directory named in amendment v3's own
text (the version-1-looking `RUN-ICINV-fg-stage1-p2003` /
`RUN-ICINV-fg-nullr*-p2003` family) *and* for the short-id directories this
driver's own dependency map proposes to read (`RUN-ICINV-65bc20`,
`RUN-ICINV-84bd66`), each manifest's `run.handoff_id`, `run.code.commit`, and
`run.status` were read, and `git log --diff-filter=A` was independently run
on each manifest's own path to find the commit that first added it — exactly
as the amendment text proposed, done as code (`audit_p2003_stage12_provenance`
in `harness/run_fullgroup.py`) rather than asserted by hand.

**Audit result**:

| candidate | declared `handoff_id` | is genuinely version-2 (`TASK-20260809-caa93e`, `completed_valid`)? |
|---|---|---|
| `RUN-ICINV-fg-stage1-p2003` | `TASK-20260807-3414fc` (version 1) | **No** |
| `RUN-ICINV-fg-nullr-p2003` | `TASK-20260807-3414fc` (version 1) | **No** |
| `RUN-ICINV-fg-nullr-v2-p2003` | `TASK-20260807-3414fc` (version 1) | **No** |
| `RUN-ICINV-fg-nullr-v3-p2003` | `TASK-20260807-3414fc` (version 1) | **No** |
| `RUN-ICINV-65bc20` (stage 1) | `TASK-20260809-caa93e` (version 2) | **Yes** |
| `RUN-ICINV-84bd66` (stage 2) | `TASK-20260809-caa93e` (version 2) | **Yes** |

Every one of the four candidates the amendment flagged by name (all
`nullr*`/`stage1` "v2"/"v3"-suffixed directories) is confirmed, not assumed,
to be a **version-1** artifact — the suffixes in their names ("nullr-v2",
"nullr-v3") are re-run tags *within* version 1's own iterative execution, not
contract-version markers. This matches the suspicion the amendment itself
raised but explicitly declined to resolve.

Separately, and **not named in the amendment's own candidate list**, a valid
version-2 Stage 1 record (`RUN-ICINV-65bc20`) and Stage 2 record
(`RUN-ICINV-84bd66`) for p=2003 **do exist**, minted under the same
short-id scheme as the other version-2 runs, under handoff
`TASK-20260809-caa93e`. This driver's own `V3_STAGE12_SOURCE` dependency map
was built to point at these before the audit function was run against it;
the audit function's role was to *confirm* that choice against the manifests
themselves rather than assume it.

**What this means for Stage 3, stated explicitly**: regardless of the Stage
1/2 audit outcome, Stage 3 (the primary-class Arm A0/A1/B density sweep) had
**no valid record at p=2003 under any version**, so a fresh Stage 3
measurement was required by change A9 and was run (`RUN-ICINV-4bf6c8`),
reading `RUN-ICINV-65bc20` and `RUN-ICINV-84bd66` as its Stage-1/Stage-2
dependencies (SR1/SR2), under the unchanged sampler and class-selection
rules. Full audit detail: `change-a9-p2003-audit.json` in `RUN-ICINV-4bf6c8`
and `RUN-ICINV-849d1d`.

---

## 4. Change A7 — the CI-overlap SR3 sub-check, old vs new at every row

`baseline_reproduction_v3` (added to `harness/run_fullgroup.py`, alongside —
not overwriting — `baseline_reproduction_v2`) replaces **only** the
`every_row_in_band_1_3_to_3_6` sub-check's contribution to
`checks["every_row_in_band_1_3_to_3_6"]` with the CI-overlap test. The old
literal field is kept, reported, and explicitly labelled non-gating; the new
`ci_overlaps_band_1_3_to_3_6` field (with its own `r_true_95pct_ci` pair) is
what the gate actually reads. `monotonic_decay_is_false` and
`operating_row_within_tolerance` are untouched, copied verbatim from the same
computation `baseline_reproduction_v2` performs. The band `[1.3, 3.6]` itself
is not moved, widened, or re-estimated anywhere.

### p = 4001 (`RUN-ICINV-476e12`) — gate applies, `gate_passed: True`

All 13 rows pass **both** the literal check and the CI-overlap check (no
regression; every row that passed under version 2 still passes).

### p = 6007 (`RUN-ICINV-ff0806`) — gate applies, `gate_passed: True`

This is the prime that motivated the redesign (DEC-20260809-de11f9,
RUN-ICINV-99f722). Under the CI-overlap gate:

| fb | ratio | literal `in_band` | `r_true_95pct_ci` | CI overlaps `[1.3,3.6]` |
|---:|---|:---:|---|:---:|
| 4 | 1.2315292605941532 | **False** | `[0.9864520254143091, 1.5813756882794519]` | **True** |
| 5 | 1.1125313273888915 | **False** | `[0.891134962323324, 1.4285734410673028]` | **True** |
| 6 | 1.4518421211510657 | True | `[1.1629221057243266, 1.864273880509101]` | True |
| 7–22 (10 rows) | (all pass) | True | — | True |

These two rows' CIs match, to the displayed precision, the numbers amendment
v3's own filing-time verification script (`v3-verification.py` /
`v3-verification-output.txt`) computed before this run existed
(fb=4: `[0.986452, 1.581376]`; fb=5: `[0.891135, 1.428573]`). `checks`:
`every_row_in_band_1_3_to_3_6: true` (gating, CI-based),
`rows_outside_band_literal_non_gating: [4, 5]` (reported, not gating),
`monotonic_decay_is_false: true`, `operating_row_within_tolerance: true`
(operating row fb=9, VR `1.5787641552269556` against the record-read
reference `1.5787641552269556`, delta `0.0` — Arm A0 is a bit-exact
reproduction of the same measured cell. Against the contract's own
*prose*-stated reference `1.591`, reported separately and never gating, the
delta is `-0.012235844773044402`, matching DEC-20260809-de11f9's own number).
**`gate_passed: True`** — under version 2's literal check this prime's gate
had failed (`RUN-ICINV-c670c2`, `RUN-ICINV-99f722`).

### p = 2003 (`RUN-ICINV-4bf6c8`) — gate does not apply (no committed reference)

Five of thirteen rows fail the literal check (fb ∈ {6, 11, 12, 13, 15, 22} —
six, not five; see table below) while all thirteen pass the CI-overlap check.
Since `gate_applies_at_this_prime: False` here (p=2003 has no committed
EV-ENDO-10109d density sweep to compare against), neither check gates
anything at this prime regardless — this is reported for completeness, not
because it affects the terminal state.

| fb | ratio | literal `in_band` | CI overlaps |
|---:|---|:---:|:---:|
| 4 | 1.5120 | True | True |
| 5 | 1.3503 | True | True |
| 6 | 1.2963 | **False** | True |
| 7 | 2.2028 | True | True |
| 8 | 2.5864 | True | True |
| 9 | 2.6346 | True | True |
| 10 | 3.5332 | True | True |
| 11 | 3.8498 | **False** | True |
| 12 | 3.8894 | **False** | True |
| 13 | 4.3710 | **False** | True |
| 15 | 3.6979 | **False** | True |
| 18 | 3.0139 | True | True |
| 22 | 1.2524 | **False** | True |

(Full row tables for every prime, including `mean_density_3V_over_order`,
`mean_rate`, `verdict`, and every field above: `baseline-reproduction.json`
in each stage-3 run directory.)

---

## 5. What ran, what did not, and every deviation

### Runs produced

| run id | p | role | contract version | status | notes |
|---|---|---|---|---|---|
| `RUN-ICINV-476e12-failed` | 4001 | primary | 3 | `failed_infrastructure` | see deviation below; superseded by `RUN-ICINV-476e12` |
| `RUN-ICINV-476e12` | 4001 | primary | 3 | `completed_valid` | reuse (A9), gate passed, F_p PERSISTS |
| `RUN-ICINV-ff0806` | 6007 | primary | 3 | `completed_valid` | reuse (A9), gate passed, F_p COLLAPSES |
| `RUN-ICINV-4bf6c8` | 2003 | primary | 3 | `completed_valid` | fresh Stage 3 (A9), no gate, F_p PERSISTS |
| `RUN-ICINV-849d1d` | — | decide | 3 | `completed_valid` | aggregate: terminal_state OUTCOME-C |

Stage 1 and Stage 2 were **not re-run** at any prime: amendment v3 changes
A7/A8/A9 touch only Stage 3's baseline-reproduction sub-check and its data
provenance, and valid version-2 Stage 1/2 records exist at all three primes
(`RUN-ICINV-65bc20`/`fda7fe`/`d1cbec` for stage 1,
`RUN-ICINV-84bd66`/`910053`/`9f38cf` for stage 2), confirmed by the change-A9
audit at p=2003 (§3b) and already established as valid, clean-tree, A6-pinned
version-2 records by DEC-20260809-de11f9 at p=4001/p=6007.

No curve was dropped, at any prime, in any arm. No timeout or memory-cap
event occurred (see §7 for budget accounting).

### Deviations

**D-v3-1 (implementation defect, self-caught before any gate result was
relied on).** `_print_sweep` (shared by version 2 and version 3's console
summary) reads `checks["rows_outside_band"]`; `baseline_reproduction_v3`'s
`checks` dict originally used only the more precisely named
`rows_outside_band_literal_non_gating` / `rows_outside_band_ci_gating`, so the
first attempt at the p=4001 run (`--stage 3v3 --p 4001`) crashed with a
`KeyError` **after** the actual gate computation had already succeeded and
printed (`BASELINE GATE: passed=True`), inside the final console-summary
call. Per the driver's own `except Exception` handler this was correctly
classified `failed_infrastructure` (never negative evidence, AGENTS.md rule
5) and written immutably as `RUN-ICINV-476e12-failed`; the clean run id
`RUN-ICINV-476e12` itself had not yet been used (the exception handler
appends `-failed` to a **freshly computed** run id, so the collision-free id
was still available). The fix (adding a `rows_outside_band` alias key to
`baseline_reproduction_v3`'s `checks` dict, matching what that key meant for
gating purposes under version 2) is a formatting/reporting-path fix only —
`baseline_reproduction_v3`'s gate logic itself, which had already run
successfully inside the failed process before the crash, was not touched.
`RUN-ICINV-476e12-failed` is retained, unedited, marked
`failed_infrastructure`, per AGENTS.md rule 4 (run records are immutable;
corrections supersede, never overwrite).

**D-v3-2 (reported, not a defect).** The amendment's own candidate list for
the p=2003 audit (§3b) named only the version-1-looking directories and
correctly flagged them as suspect; it did not mention that valid version-2
Stage 1/2 records for p=2003 exist under a *different* naming convention
(the short-id scheme). This driver's dependency map
(`V3_STAGE12_SOURCE`) already pointed at the correct records before the audit
function was written against it; the audit function's role was to confirm
that choice, which it did. Recorded so a reviewer does not read the
amendment's silence on this point as evidence the correct records were
missed.

**No other deviation from the frozen contract, amendment v2, or amendment v3
occurred.** In particular: `harness/exp_icinv.py` was not edited (checked by
`fg.committed_file_digest()` at the start of every run — `byte_identical:
true` in every one); `exp_icinv.permutation_null` (NULL-C) was not used
(checked by `fg.self_audit_no_null_c()` — `call_sites_total: 0` in every
run); no sum set was recomputed per arm; no reference value was transcribed
into source (every one is read from its committed record at run time and
bound by `source_sha256` — see `change-a9-provenance.json` and
`baseline-provenance.json` in each run).

---

## 6. Scope and honesty (verbatim from the handoff, restated as run)

Toy scale throughout (`p ≤ 10007`). `claim_tier: toy`, `sota_delta: 0`. No run
of this contract can support or reject an ECDLP cost claim. Any resulting
evidence record is pre-capped at `preliminary` per amendment v3's
`confirmatory_status: exploratory_only`, **strengthened beyond version 2's
own reason**: the redesign's numeric effect on the two rows that motivated it
(p=6007, fb=4 and fb=5) was computed and disclosed in the amendment's own
filing text *before* this run existed, so a version-3 run at p=4001 or p=6007
cannot be blind in the sense a pre-registration requires. `OUTCOME-C` — the
over-dispersion persists (2–1 majority) and does not stratify by r
(`S: NEGATIVE`) — fully satisfies the contract's success criterion and is
reported with the same clarity as any other outcome, per the handoff's
explicit instruction. This report does not characterise what `OUTCOME-C`
means for `H-ICINV-6c7920`, `EV-ENDO-10109d`, `RQ-ICINV-475b5e`, or
`GOAL-ENDO-001` — those are Coordinator acts on a later ledger archive.

---

## 7. Budget and provenance check

| | this task (version 3) | budget |
|---|---|---|
| runs (including the one `failed_infrastructure`) | 5 | 30 max |
| wall clock, summed | ~68.5 s | 14400 s per run |
| CPU, summed | ~72.4 s (≈0.020 CPU-hours) | 12 CPU-hours |
| peak memory | well under 4 GB (no `RLIMIT_AS` trip in any run) | 4 GB |

`python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-4d33aa
--strict --since-commit d6ab7abfc440bddcca97fd5c60e950e557d52cc8`:

```
5 pinned, 0 unpinned, 0 unreadable, of 5 run manifest(s) in scope
  of the pinned, 2 also ran from a fully clean tree
exit code: 0
```

All five run manifests produced by this task (the four `completed_valid`
plus the one `failed_infrastructure`) are pinned; the check passes `--strict`.
This is scoped to this task's own commits, exactly as DEC-20260809-de11f9
scoped version 2's own check — the version-1 and version-2 runs predate this
task and are not re-scored by it.

---

## 8. Artifact index

- `harness/exp_icinv_fullgroup.py` — added `CONTRACT_VERSION_V3`,
  `AMENDMENT_PATH_V3`, `chi2_wilson_hilferty_bounds`, `r_true_95pct_ci`,
  `wilson_hilferty_crosscheck` (change A7/A8). `harness/exp_icinv.py` not
  touched.
- `harness/run_fullgroup.py` — added `baseline_reproduction_v3`,
  `evaluate_decision_rule_v3`, `reconstruct_rows_from_columnar`,
  `load_stage3_cells_v3`, `audit_p2003_stage12_provenance`,
  `assemble_stage3_v3_reused`, `run_id_for_v3`, `_sweep_artifacts_v3`,
  `main_v3`, and the `--stage 3v3|decidev3` CLI entry points. Version-2
  functions (`baseline_reproduction_v2`, `evaluate_decision_rule_v2`, the
  `"1"|"2"|"3"|"decide"` dispatch in `main`) are unmodified.
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-476e12-failed/` — retained,
  immutable, `failed_infrastructure` (D-v3-1).
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-476e12/` — p=4001 Stage 3, v3.
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-ff0806/` — p=6007 Stage 3, v3.
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-4bf6c8/` — p=2003 Stage 3, v3
  (fresh measurement).
- `experiments/EXP-ICINV-4d33aa/runs/RUN-ICINV-849d1d/` — aggregate decide,
  v3. `terminal_state: OUTCOME-C`.

Each of the four `completed_valid`/`failed_infrastructure` run directories
carries the contract's full required-artifact set
(`manifest.yaml`, `command.txt`, `environment.json`, `stdout.log`,
`stderr.log`, `raw-result.json`, `coverage-certificates.json`,
`per-curve-measurements.json`, `decision-rule-evaluation.json`,
`baseline-reproduction.json`, `tail-checks.json`) plus
`wilson-hilferty-crosscheck.json` (change A8, every run) and, where
applicable, `change-a9-provenance.json` (p=4001/p=6007 reuse runs) or
`change-a9-p2003-audit.json` (p=2003 and the decide run).
