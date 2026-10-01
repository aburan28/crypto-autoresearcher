# EXP-ICEX-aaccfc implementation (protocol v4)

Tasks: TASK-20260929-8586f2 (implementation, protocol v3), TASK-20260929-1211f7 (repair for protocol v4, fixes FX-1 to FX-8; `repair_report_v4.yaml`) and TASK-20260929-ffd37e (v4b: re-check TASK-20260929-1344ef findings G-1 to G-4 and advisories A-1 to A-3; details and file hashes in `repair_report_v4b.yaml`, which supersedes `repair_report_v4.yaml` by reference). Protocol v4 consists of:

- `specification.yaml` (v1, DEC-20260910-56fad5);
- `amendments/AMD-20260926-ced670.yaml` (v2, DEC-20260926-6fe1a0);
- `amendments/AMD-20260929-143d11.yaml` (v3, DEC-20260929-a8d594, commit 87f67dfc06). Its sha256 is `36cad68cee9ff8da0ce86e94c2f9548f05ffd95a5bdaf32eeaeaf32c0514dac7`, recomputed from the committed file. That equals the decision's `amendment_sha256_at_decision`. The prefix `b6be15f...` quoted in the Coordinator's instruction does not match the file and is not used.
- `amendments/AMD-20260929-5a84eb.yaml` (v4, DEC-20260929-986b4c, commit 211f7ed79f). Its sha256 is `61926b8c691cfe48a00354939651314a9d5aee62432a4d671c8ec56f7ddb310d`, equal to the decision's `amendment_sha256_at_decision`.

Later amendments govern where they differ. v3 accepts the literal readings OQ-1 to OQ-14 as implemented, and adds the non-verdict figure FX-A (below). v4 answers the implementation audit TASK-20260929-e3446a: it corrects the v3 pre-data statement (F-5), keeps fixture b16-s21, pre-registers a non-verdict leave-b16-s21-out exponent fit (FX-8) and requires fixes FX-1 to FX-8 to the driver, cell runner, smoke and analysis. The seed namespace stays `EXP-ICEX-aaccfc/v2`, because neither v3 nor v4 changes a label. Stage 1 reuses the B0 backend of `EXP-SDEG-85eefd/amendments/AMD-20260926-3479cf.yaml` C-4 by reference.

No scientific run was made and no `runs/RUN-*` directory exists. Execution is
not admitted: no committed decision admits EXP-ICEX-aaccfc, and the driver
refuses every existing one (DEC-20260929-f45bf1, -a8d594 and -986b4c). The
Mac's readings at repair time also fail C-7 (repository volume about 6 GiB
free, 15-minute load above 14).

## Layout

| file | role |
| --- | --- |
| `common.py` | constants (C-2 to C-6), seed labels, fixtures, C-1 reproduction, `fb_bound` (exact integer ceil(p^(1/m))) |
| `arith.py` | instrumented F_p, affine curve and Z/q arithmetic in C-3 units (`Cost`) |
| `verify.py` | independent verifier arithmetic (copied from EXP-SDEG-85eefd; Jacobian, Cipolla) |
| `hostinfo.py` | host identity and fail-closed machine readings (copied from EXP-SDEG-85eefd, FX-2) |
| `b0.py` | interval and random-x factor bases, forward 2-sum table, B0 membership (m = 5, 6, 8), relation extraction, stage-2 scan |
| `oracle.py` | exact m-membership oracle (all signed m-multisets; uncharged) |
| `la.py` | rank tracker, structured Gaussian elimination, Lanczos over Z/q, back-substitution, dense reference |
| `pipeline.py` | cells: `primary`, `null_randfb`, `stage_cost` (m = 6, 8), `rho`; namespace guard (frozen namespace; v4b A-1 frozen fixtures only in the unit-test namespace) |
| `rho.py` | Pollard rho baseline (negation map, r = 32, fruitless cycles), C-3 units |
| `audit.py` | independent accounting checker (C-6) |
| `analysis.py` | C-5 ratio, exponent, bootstrap and verdict, verbatim; FX-A non-verdict figure (`fxa_report`, called separately); v4 FX-8 leave-b16-s21-out fit (non-verdict) |
| `cellrun.py` | one cell per fresh process; per-cell peak RSS; admission and namespace guard (v4 FX-4, bound to the live driver by v4b G-2); parent watcher (v4b G-1) |
| `driver.py` | admission (v4 FX-1), C-7 fail-closed, plan and protocol-v4 hash binding, snapshot pinning (v4 FX-6), cells, audit, analysis then FX-A, canonical run record and failure handling (v4 FX-2, FX-3; stub first, v4b G-4), inference block (v4 FX-7), cell process groups (v4b G-1), run token and driver pid (v4b G-2), committed-receipt check (v4b G-3) |
| `make_trial_plan.py` / `trial-plan-v2.json` | 6 fixtures x 5 cells = 30 cells; records protocol v4 and the sha256 of the three amendments and the v3/v4 decisions (plan sha256 `58c36b6d1444dce4f4b539f7bb0175d24d29e30af5abfd81abe7eaef14c2e983`; the file name is kept) |
| `synthetic.py` | deterministic non-frozen prime-order curves for smoke (v4 FX-5) |
| `smoke.py` | driver smoke dry-run on a synthetic fixture plus a pass/fail-only full-replay summary (v4 FX-5) |
| `tests/` | 103 tests (`test_process.py` launches real cell processes) |

## What is charged (C-3, C-5)

Units: F_p mult 1, inversion 10, affine point addition 13, hash probe 1, and
one LA modmul over Z/q 1. Every figure is reported as a `Cost` dict (op counts,
`units`, and a secondary `units_fieldlevel`), with process peak RSS beside it.

- **Stage 1.** Charged items:
  - factor-base construction (liftability tests and lifts);
  - the forward table, built once per fixture and factor base: n(n+1) group operations and n(n+1) probes;
  - for every attempt, including failed ones: R_j = a_j G + b_j Q by double-and-add, the full B0 scan, and one addition for relation extraction on members.
- **Stage 3.** Charged items: collector rank tracking, SGE, Lanczos (right-hand side, iterations, solution check) and back-substitution.
- **Descents.** Every attempt of all 16 descents: Q_t + r G, the B0 scan, and extraction.
- **Complete cost** = stage 1 + stage 3 + descents.
- **Not in the complete cost** (charged separately): stage 2 and the controls.
- **Also reported:** amortized cost per target, `complete / 17`.
- **Uncharged:** verification and target generation (verifier arithmetic).

## FX-A: incremental-R_j figure (AMD-20260929-143d11, descriptive, non-verdict)

`analysis.fxa_figure(result)` computes, per primary fixture:

`complete_units_rj_incremental = complete_units - 13 * sum_j (rj_ops_j - 1)`

- **rj_ops_j:** the charged group-op count of R_j = a_j G + b_j Q, including the final addition.
  - It is recomputed from the run's own labels: (a_j, b_j) from `pipeline.attempt_ab`, and Q from `pipeline.target_k`, which is checked against the receipt's Q.
  - The recomputation uses the same charged `arith.Curve`, so an incremental walk is credited 1 op per attempt.
- **Cross-check:** rj_ops_j <= pt_ops_j for every attempt. A violation raises `ProcedureDefect`.
- **Output:** the ratio of the figure to 13 x 0.886 x sqrt(q), `ratio_rj_incremental_nonverdict`. It is attached to each point beside the primary ratio.
- **Verdict isolation (actual ordering, v4 FX-7/A-4 and FX-3).** In protocol v3 `analyse` computed FX-A first, before the C-5 block (the earlier text here said "after"; that was wrong). Since v4 the driver calls `analyse(..., fxa=None)`, writes `metrics.json`, and only then calls `analysis.fxa_report` into `fxa_nonverdict.json`. An FX-A `ProcedureDefect` therefore leaves `metrics.json` untouched and marks the run `invalid` with `failure_class: procedure_defect_fxa`. The C-5 rule is unchanged.

**Which attempts are covered.**

- **Named figure: stage-1 attempts only.** These are the only attempts that build R_j = a_j G + b_j Q.
- **Supplementary figure: descents too.** Descent attempts build Q_t + r G (one scalar multiplication plus one addition), not a_j G + b_j Q. The same substitution applied to them is reported separately as `complete_units_rj_incremental_with_descents` and `ratio_rj_incremental_with_descents_nonverdict`, with the same cross-check. See OQ-15.
- **Not covered:** null and stage-cost cells, which are not in the complete cost.

## FX-8: leave-b16-s21-out sensitivity (AMD-20260929-5a84eb, descriptive, non-verdict)

`analyse` adds `exponent_leave_out_b16_s21_nonverdict`: the OLS slope of log(complete units) against log q over the five primary fixtures other than b16-s21, with a 95% percentile bootstrap CI (2000 resamples, the same resampling rule as OQ-8) seeded from the new implementation label `<ns>|bootstrap|leave_out|b16-s21`. It sits beside the primary fit, carries the label "descriptive sensitivity, NOT a verdict input", and has no verdict field. The verdict, primary exponent, primary bootstrap and dominant stage are computed only from the six-point primary fit; tests check they are identical with and without the block, including a constructed case where the leave-out fit alone would satisfy the sub-rho condition.

## Stage definitions as implemented

- **Stage 1 (C-4).**
  - The attempt labels are `EXP-ICEX-aaccfc/v2|attempt|<bits>|<seed>|<j>`; a_j comes from the high 128 bits of the hash and b_j from the low 128 bits, each rejection-sampled mod q.
  - Q = kG, where k comes from `.../target|<bits>|<seed>`.
  - Each attempt runs B0 as frozen: the shared forward table plus the backward 3-sum, computed by prefix-shared point arithmetic (2/4/8 additions). The scan is full, with no early abort.
  - The first hit in scan order gives the relation. The relation is verified by independent point arithmetic; a failure is a procedure defect and stops the cell.
- **Collector.** The plain uniform collector (P1385 is deferred by the amendment).
  - It stops once the rank reaches L + 1 on the (classes, Q) system and 10 further relations have been collected.
  - All relations are rows; see OQ-3.
- **Stage 3.** The pipeline runs SGE, then Lanczos on A^T D A (D is a label-derived nonzero diagonal, retried on breakdown), then back-substitution.
  - The kernel is fixed by log G = 1.
  - Every recovered x_i is checked by x_i G = P_i, and the recovered k by k G = Q.
  - A dense Gauss-Jordan reference is compared.
- **Descents.** 16 targets per fixture. k_t comes from `.../descent|...` and r from `.../descent_r|...|<t>|<i>`.
  - Each descent retries Q_t + r G until m = 5 membership holds.
  - The recovered k_t is sum(s * x_i) - r, verified by k_t G = Q_t.
- **Stage 2.** 256 held-out points S = hG, with h from `.../heldout|...`.
  - For each S, the scan runs P1 over all 2L signed factor-base points and tests x(S - P1) < B.
  - Results are compared with brute-force pair enumeration.
  - alpha2 is the OLS slope of log(mean units) vs log L over the six primary fixtures. It is not a verdict input (C-4 note).
- **m = 6, 8 stage-cost cells.** B_m = ceil(p^(1/m)); the cells run stage 1 under the same rule, stage 2, and stage-3 LA. There are no descents (OQ-4, OQ-7).

## Controls (C-6)

- **Matched null.** A random-x factor base of the interval size is drawn without replacement from all liftable x by `.../randfb|<bits>|<seed>|<i>`.
  - It uses the same attempt stream (paired).
  - It runs stage 1 plus stage-3 LA with log verification, and reports yield and cost beside the interval factor base.
- **Known false.** The factor-base coefficient vectors are permuted across rows, while (a_j, b_j) stay with their rows.
  - The same LA runs, followed by log verification.
  - The control passes only if verification fails, and an LA failure counts as failing to verify. If the scrambled solve verifies, the cell stops as a procedure defect.
  - A test also checks the control itself: an identity "scramble" must make it report failure.
- **Baseline.** Pollard rho, 64 targets, in the same units. Reported three ways: total, walk only, and precompute only (the 32 multipliers plus the start). Each is also given against 13 x 0.886 x sqrt(q).
- **Accounting audit.** `audit.py` shares no charged code.
  - It replays 10% of stage-1 attempts, selected by `.../audit|...`. The replay recomputes group operations and probes in closed form, re-decides membership with the exact oracle, and compares exactly.
  - It recomputes every LA step's op count from the logged dimensions.
  - It replays every descent attempt.
  - It rejects receipts with omitted failed attempts, a zeroed or missing table build or factor-base construction, missing RSS, or components that do not sum.
  - When the audit rejects, the driver withholds the verdict.

## Driver

A charged run is refused unless all of these hold, checked in order:

1. the host is macOS;
2. C-7 passes fail-closed (15-minute load <= 14, system volume >= 5 GiB free, repository volume >= 20 GiB free; unreadable values refuse);
3. the run id is `RUN-*`;
4. the admission decision passes v4 FX-1: a `coordinator_decision` with a matching id; `decision` exactly `admit_execution` (v4b A-2); `EXP-ICEX-aaccfc` in `target_ids`; `execution_admission.currently_admitted: true`; not superseded or withdrawn (status `superseded`/`withdrawn` at document, decision or `execution_admission` level, a non-null `superseded_by` -- `superseded_by: null` is accepted --, or any other decision file listing it under `supersedes`); and the file tracked by git and identical to HEAD. Any DEC id may be named, because the admission decision did not exist when v4 was frozen; the manifest records this under `inputs.admission_decision_pinning`;
5. the trial plan's protocol hashes match the files on disk and the plan says protocol version 4;
6. the protocol v4 records match: the three amendments and the fixtures against their pinned sha256, and the v3 and v4 amendment hashes against `amendment_sha256_at_decision` of DEC-20260929-a8d594 and DEC-20260929-986b4c;
7. `--snapshot-receipt PATH` (v4 FX-6, required) is the dispatcher's own receipt (v4b G-3): `kind: snapshot`; a regular file (not a symlink) inside the repository at `.../archives/TASK-*/snapshot-receipt.json` whose `task_id` names that TASK directory; tracked by git, clean (`git status` empty, so neither modified nor staged-only) and byte-identical to `HEAD:<path>`. A copy elsewhere, an uncommitted or edited receipt, and a hand-written one are refused. The receipt then pins every implementation `.py`, test and trial-plan file, every pinned implementation file matches, and `git status --porcelain --untracked-files=all` of the implementation directory is empty. The receipt file itself is excluded from every comparison;
8. `--runs-dir` is `experiments/EXP-ICEX-aaccfc/runs` (v4b G-2; exit 11 otherwise) and the run directory does not already exist.

Then the run:

- Immediately after the run directory is created, before `environment.json` and the Sage probe, a stub `manifest.yaml` (`stub: true`, status `running`, driver pid, token hash) and `raw-result.json` are written (v4b G-4). If anything fails before the full record exists, the stub is rewritten as `failed_infrastructure` (failure class `exception` or `signal`, traceback under `driver.traceback`) with `raw-result.json` beside it.
- The full `manifest.yaml` then replaces the stub with status `running` before C-1 and before the first cell, and is rewritten after every cell. `inputs.driver_pid` is the driver's pid and `inputs.run_token_sha256` the sha256 of a random 256-bit per-run token (`secrets.token_hex(32)`) that exists only in the driver and in the cells' environment (v4b G-2); the token itself is never written. Its top-level `run:` block (id, experiment_id, hypothesis_id, protocol_version, status, code, environment, inputs, timing, resources, result, inference, artifacts) mirrors `EXP-SDEG-85eefd/runs/RUN-SDEG-3de103/manifest_v2.yaml`; `inputs.protocol` carries the path and sha256 of every governing record; `inputs.snapshot_verification` the FX-6 result. Driver detail (git state, cell list, C-1 result, audit outcome) sits under `driver:`.
- `command.txt`, `environment.json`, `stdout.log` and `stderr.log` are written first; `raw-result.json` (index of the cells attempted so far, with result sha256) is rewritten with every manifest write, so it exists on every path.
- C-1 fixture reproduction (Sage, byte-compare); a mismatch is a procedure defect.
- Each of the 30 cells runs in a fresh `nice -n 10` process in its own session and process group (`start_new_session`, v4b G-1). The driver passes the admission decision, repository root, run directory, run token and its own pid in the environment, records the child's pid in `cells/<cell>/process.json`, and tracks reaping explicitly: `os.wait4(pid, WNOHANG)` is polled and only a returned pid equal to the child's counts as reaped (a live child returns 0). On every path that leaves without reaping -- an exception, or SIGTERM/SIGHUP/SIGINT raised as `RunInterrupted` -- the whole group is SIGKILLed and the child reaped; stray group members are killed after every cell. A SIGKILL of the driver cannot be caught, so the cell guards itself: see below.
- Then `audit.json`, `metrics.json` (C-5; verdict withheld if the audit rejects), and after that `fxa_nonverdict.json`.
- Failure mapping (v4 FX-3): a procedure defect (cell, C-1 mismatch, or an FX-A cross-check) records `invalid`; any other exception, a failed cell of another kind (including a rho crash on a zero target, per the A-3 ruling), or SIGTERM/SIGHUP/SIGINT records `failed_infrastructure`, with the traceback in `stderr.log` and under `driver.traceback`.

## Cell guard (v4 FX-4, v4b G-1, G-2, A-1)

`cellrun.run_task` refuses (status `refused`, exit 3, no computation) any namespace that is neither `EXP-ICEX-aaccfc/v2` nor starts with `smoke|`. The frozen namespace is accepted only when all of these hold (v4b G-2):

- the environment names the decision, repository root, run directory, run token and driver pid;
- the run directory is `experiments/EXP-ICEX-aaccfc/runs/RUN-*`;
- the decision still passes `driver.check_decision`;
- the manifest is the full record (not the stub), status `running`, `id` equal to the directory name, for that decision and namespace, with `code.commit` equal to the repository HEAD;
- `inputs.run_token_sha256` equals the sha256 of the token in the environment;
- `inputs.driver_pid` equals the environment's driver pid, which is this process's live parent (`os.getppid()`) and whose command line runs this implementation directory's `driver.py` (psutil, with a `ps` fallback).

A hand-written manifest cannot carry the hash of a token it never saw, nor name a live `driver.py` parent. As an extra layer, `pipeline.run_*` raise `NamespaceRefused` for the frozen namespace unless `cellrun` has set `pipeline.FROZEN_ADMITTED` after its guard accepted.

Orphan protection (v4b G-1): when `ICEX_AACCFC_DRIVER_PID` is set, the cell refuses at once (exit 9, nothing written) if that pid is not its parent; otherwise a daemon thread polls `os.getppid()` every 0.2 s and calls `os._exit(9)` as soon as the process is re-parented. The result file is written to `result.json.tmp` and renamed into place only after a final parent check, so an orphan leaves no `result.json`.

Fixtures (FX-5, v4b A-1): an inline fixture is accepted only in a smoke namespace and never if it matches a frozen fixture, and a smoke-namespace task may not name a fixture by bits/seed at all, so `cellrun` (which always persists its result) never evaluates a frozen fixture in the smoke namespace. `pipeline._ns_guard` additionally refuses a frozen fixture in any smoke namespace except the prefix `smoke|EXP-ICEX-aaccfc/v2|tests`. That prefix is the one exempt path: the in-process unit tests (`tests/conftest.py` `smoke_primary`, `test_charging`, `test_controls`, `test_fxa`) call `pipeline` directly and persist nothing. Those modules carry `PYTEST_DONT_REWRITE` (v4b A-3), so a failing assertion reports no compared value, and their assert messages are fixed strings.

## Smoke (implementation check only)

**Protocol v4 smoke (FX-5).** `smoke.py` now runs the driver's smoke dry run on a synthetic, non-frozen prime-order curve from `synthetic.py` (13-bit field; the frozen fixtures are 16- and 20-bit, and `common.is_frozen_fixture` is checked by the driver, `cellrun` and `smoke.py`), in the namespace `smoke|EXP-ICEX-aaccfc/v2`, with 2 descents, 16 held-out points and 4 rho targets. Output goes to `smoke/v4/`. The summary holds pass/fail fields only; `smoke.assert_no_cost_fields` refuses any key naming units, cost, ratio, exponent, verdict, attempts, time or memory. No C-5 analysis runs in smoke.

- `DRYRUN-smoke-v4-001` and `DRYRUN-smoke-v4-002` are two driver dry runs of the same command. Both reached `smoke_completed`. The first two summary attempts failed inside `smoke.py` because its own key guard rejected two of its key names (`fxa_nonverdict_written`, and cell ids such as `stage_cost_m6` used as keys). The summary was then changed to a list, and both existing directories were summarised with `smoke.py --summarize-only`; neither run was repeated.
- Outcome in both: fixture reproduction byte-identical; every cell `ok` in the smoke namespace; sampled and full-replay audits accept; primary logs verified, k recovered, LA agrees with the dense reference, both descents verified, stage-2 scan agrees with brute force, known-false control passed (scrambled solve failed to verify); null factor base matches the interval size; stage-cost m = 6 and m = 8 logs verified with stage 2 agreeing; rho targets all solved and certified; `fxa_nonverdict.json` written after the audit.

**Earlier smoke outputs (protocol v2/v3; immutable, excluded from every analysis by AMD-20260929-5a84eb F-5).** `smoke/DRYRUN-smoke-001*`, `smoke/DRYRUN-smoke-002*`, `smoke/DRYRUN-smoke-003*` and `smoke/driver_dryrun/` ran on frozen fixture b16-s21 at its frozen m and B in the smoke namespace. They are kept unchanged. This file previously quoted attempt counts from them; those figures are removed from this version because the attempt count approximately determines stage-1 cost (the earlier text remains in the v3 snapshot, commit d6da4cd606). Their identity and control outcomes matched the v4 smoke above.

Pre-data fixture property (from the trial plan, computed by verifier liftability only): at m = 8, fixtures b16-s21 and b20-s23 have L = 1. Their stage-cost cells need on the order of 10^5 and 10^6 attempts respectively.

## Open questions

Each question below gives the literal reading this implementation uses. A different reading needs a Coordinator amendment.

- **OQ-1: point-addition unit.**
  - Reading: every affine group operation with two finite operands (addition, doubling, or P + (-P) = O) costs 13 units flat, and its internal field operations are not charged again.
  - A field-level figure, in which doubling comes to 14, is reported as `units_fieldlevel`.
- **OQ-2: LA inversion.** C-3 prices only the LA modmul. Reading: an inversion over Z/q costs 10 units, by analogy with F_p inversion.
- **OQ-3: "rank |F| - 1".**
  - F contains both signs, so |F| = 2L, but log(-P) = -log P. The literal target 2L - 1 exceeds the column count L + 2 whenever L > 3, so it cannot be reached.
  - Reading: the columns are the L x-classes plus G and Q, with target rank ncols - 1 = L + 1 and 10 excess rows. The kernel is one-dimensional and fixed by log G = 1.
  - "The relation containing Q" is read as the Q column, which every relation has because b_j is uniform.
- **OQ-4: B0 at m = 6 and 8.** B0 is frozen for m = 5 only. Reading: the same forward 2-sum table, and a backward (m - 2)-sum by the same prefix-shared recursion.
- **OQ-5: stage-2 test cost and fit.**
  - Each test "x(S - P1) < B" costs 1 unit (the probe unit).
  - S - P1 = O is not a hit.
  - alpha2 uses the mean over the 256 points.
  - The fit uses only the six primary fixtures, whose L values are 3, 5, 6, 7, 11 and 5.
- **OQ-6: rho details.**
  - The collision-store lookup costs 1 probe per step.
  - The primary rho figure includes precompute.
  - The walk labels are not fixed by the protocol.
- **OQ-7: "stage-cost-only" at m = 6 and 8.**
  - Reading: stage 1 to the same rank rule (same attempt stream), stage 2 at B_m, and stage-3 LA with log verification.
  - There are no descents, and these cells are not C-5 verdict inputs.
- **OQ-8: C-5 statistics.**
  - The bootstrap resamples the 6 fixture points with replacement, redraws resamples in which all log q values are equal, and reports a percentile CI.
  - The dominant stage pools units over the 20-bit fixtures.
  - The ratio uses the frozen reference 13 x 0.886 x sqrt(q), not the measured rho.
- **OQ-9: host.** C-7 is stated for the Mac, so the driver refuses non-macOS hosts. A pod run would need an amendment, as EXP-SDEG-85eefd's AMD-20260928-7ce387 was.
- **OQ-10: labels outside the protocol.**
  - a_j and b_j come from one hash, split into high and low 128-bit halves.
  - Labels the protocol does not fix: `descent_r`, `rho`, `rho_walk`, `scramble`, `lanczos`, `audit` and `bootstrap`.
- **OQ-11: B0 scan and relation choice.** B0 runs a full scan, with no early abort, per its frozen definition. The units spent up to the first hit are recorded per member. The first hit gives the relation.
- **OQ-12: null design.** The null uses the same attempt stream as the primary. It includes stage-3 LA but no descents. Its construction cost includes the liftability tests of all draws.
- **OQ-13: cost of computing R_j.** R_j is computed from scratch by double-and-add (literal C-4). This is a large share of per-attempt cost. An incremental walk would be a protocol change. Resolved by v3: the charged figure keeps the literal reading, and FX-A reports the incremental figure as non-verdict.
- **OQ-15 (new): FX-A and descents.**
  - Descent attempts build Q_t + r G, not a_j G + b_j Q.
  - Reading: the named `complete_units_rj_incremental` covers stage-1 attempts only.
  - A supplementary with-descents figure is reported beside it. Both are non-verdict.
  - Ruled by v4 (AMD-20260929-5a84eb, OQ-15 ruling): accepted as implemented; both non-verdict.
- **OQ-16 (v4): decision values accepted as an admission.** Resolved by the v4b instruction (A-2): only `admit_execution` admits; every other value refuses.
- **OQ-17 (new, v4): superseding decisions that are not committed.** FX-1 names "a later committed decision". Reading (fail-closed): any decision file present in `ledger/decisions/` whose `supersedes` names the admission decision refuses, committed or not.
- **OQ-18 (new, v4): tests still exercise frozen fixture b16-s21.** The pre-existing unit tests (`conftest.smoke_primary`, `test_charging`, `test_controls`, `test_fxa`) run pipeline code on frozen fixtures in the `smoke|...|tests` namespace. Nothing is committed or printed, and assertions are structural, but the process does evaluate cost on a frozen fixture at frozen (m, B). v4b narrows this to the documented exempt path (A-1: only the `smoke|EXP-ICEX-aaccfc/v2|tests` prefix, in process, persisting nothing) and hides values on failure (A-3). Moving these tests to `synthetic.py` would still need their fixture-specific assertions rewritten; the Coordinator may rule.
- **OQ-19 (new, v4): what the snapshot pins.** FX-6 reading: every `*.py` and `tests/*.py` and `trial-plan*.json` in the implementation directory must be pinned; other pinned implementation files (docs, smoke outputs) are hash-checked if the receipt lists them; governing records outside the directory (specification, amendments, decisions, fixtures) are bound by the protocol-v4 check instead. Sage is an external executable, recorded but not pinned.
- **OQ-20 (new, v4b): a SIGKILLed driver leaves `status: running`.** Nothing can write after an uncatchable SIGKILL, so the manifest stays `running` while the orphaned cell exits unwritten (G-1). Reading: a `running` manifest whose `inputs.driver_pid` is no longer a live `driver.py` is a dead run and is to be read as `failed_infrastructure` (the cell guard already refuses it). No reconciler rewrites it, because run records are immutable; a Coordinator record would state it.
- **OQ-21 (new, v4b): HEAD must not move during a run.** The G-2 guard requires `code.commit` to equal the repository HEAD at every cell launch. A commit in the run worktree during a run (for example by another session) refuses the next cell, which ends the run as `failed_infrastructure`. Reading: intended, fail-closed; the run needs a worktree nobody commits to.
- **OQ-22 (new, v4b): orphan exit latency.** The watcher polls every 0.2 s; the final parent check before the rename leaves a window of microseconds. Measured in `test_process.py` under load: the orphan is gone well inside the test's 3 s bound. Reading: this meets "within about 1 s".
- **OQ-23 (new, v4b): receipt path form.** G-3 reading: the receipt path must match `(.+/)?archives/TASK-<8 digits>-<3 to 6 hex>/snapshot-receipt.json`, and `task_id` must equal that TASK directory; the goal and batch prefix is not fixed. The legacy three-digit TASK form is accepted.
- **OQ-14: memory and caps.**
  - The 8 GB limit is an in-process `ru_maxrss` guard, because macOS does not enforce RLIMIT_AS.
  - The machine caps (5,000,000 attempts per cell, 1,000,000 per descent) are machine protection. Reaching one is an infrastructure incompletion, never evidence.

## Environment

- Python 3.12.8, numpy 2.4.4, pytest 9.1.1.
- Sage: `/Users/adamburan/.local/bin/sage`, which launches `/Volumes/SSD990/cryptanalysis/sage`, with `DOT_SAGE` under `$TMPDIR`. Sage is used only for C-1 reproduction.
- The worktree is `/Volumes/SSD990/wt-amend-ic`, branch `coord/ic-leads-impl-20260928`. At the v4 repair HEAD was `37e2e7d72e19a5390883db8ab81634579da5abf8`; at the v4b repair it was `eecc610b3c` (v4 snapshot TASK-20260929-8428ad, commit 9698f4a36a). The tree is dirty only in this directory (plus untracked task directories of other sessions). An untracked, git-ignored `__pycache__/` in this directory predates the v4b edits; it is neither pinned nor counted as dirty.
