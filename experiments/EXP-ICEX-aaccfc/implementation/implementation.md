# EXP-ICEX-aaccfc implementation (protocol v3)

Task: TASK-20260929-8586f2 (implementation only). Protocol v3 consists of:

- `specification.yaml` (v1, DEC-20260910-56fad5);
- `amendments/AMD-20260926-ced670.yaml` (v2, DEC-20260926-6fe1a0);
- `amendments/AMD-20260929-143d11.yaml` (v3, DEC-20260929-a8d594, commit 87f67dfc06). Its sha256 is `36cad68cee9ff8da0ce86e94c2f9548f05ffd95a5bdaf32eeaeaf32c0514dac7`, recomputed from the committed file. That equals the decision's `amendment_sha256_at_decision`. The prefix `b6be15f...` quoted in the Coordinator's instruction does not match the file and is not used.

Later amendments govern where they differ. v3 accepts the literal readings OQ-1 to OQ-14 as implemented, and adds the non-verdict figure FX-A (below). The seed namespace stays `EXP-ICEX-aaccfc/v2`, because v3 changes no label. Stage 1 reuses the B0 backend of `EXP-SDEG-85eefd/amendments/AMD-20260926-3479cf.yaml` C-4 by reference.

No scientific run was made and no `runs/RUN-*` directory exists. Execution is
not admitted: DEC-20260929-f45bf1 carries no `execution_admission` block and
the driver refuses it. The Mac's readings at implementation time also fail
C-7 (system volume about 1.6 GiB free, 15-minute load about 22).

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
| `pipeline.py` | cells: `primary`, `null_randfb`, `stage_cost` (m = 6, 8), `rho` |
| `rho.py` | Pollard rho baseline (negation map, r = 32, fruitless cycles), C-3 units |
| `audit.py` | independent accounting checker (C-6) |
| `analysis.py` | C-5 ratio, exponent, bootstrap and verdict, verbatim; FX-A non-verdict figure |
| `cellrun.py` | one cell per fresh process (FX-4); per-cell peak RSS |
| `driver.py` | admission (FX-1), C-7 fail-closed (FX-2), plan and hash checks, cells, audit, analysis, manifest with inference fields (FX-5) |
| `make_trial_plan.py` / `trial-plan-v2.json` | 6 fixtures x 5 cells = 30 cells; records protocol v3 (sha256 `61f48e95a1854c6841d4b44ac6bbfd1a8fd67abfefa616190638bfeea7b9957b`) |
| `smoke.py` | driver smoke dry-run plus full-replay agreement summary |
| `tests/` | 58 tests |

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
- **Verdict isolation:** the figure is attached after the C-5 ratio, exponent, bootstrap and verdict are computed. The C-5 rule is unchanged.

**Which attempts are covered.**

- **Named figure: stage-1 attempts only.** These are the only attempts that build R_j = a_j G + b_j Q.
- **Supplementary figure: descents too.** Descent attempts build Q_t + r G (one scalar multiplication plus one addition), not a_j G + b_j Q. The same substitution applied to them is reported separately as `complete_units_rj_incremental_with_descents` and `ratio_rj_incremental_with_descents_nonverdict`, with the same cross-check. See OQ-15.
- **Not covered:** null and stage-cost cells, which are not in the complete cost.

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
4. the admission decision is a `coordinator_decision` with a matching id, `EXP-ICEX-aaccfc` in `target_ids`, and `execution_admission.currently_admitted: true` (FX-1);
5. the trial plan's protocol hashes match the files on disk, and the v3 amendment hash equals the DEC-20260929-a8d594 value;
6. the run directory does not already exist.

Next, C-1 fixture reproduction (Sage, byte-compare) runs; a mismatch stops the run as a procedure defect. After that:

- each of the 30 cells runs in a fresh `nice -n 10` process;
- `audit.json`, `metrics.json` (C-5), `raw-result.json` (an index of the per-cell results with sha256), `manifest.yaml` (git state, readings, implementation hashes, inference fields) and the stdout/stderr logs are written.

## Smoke (implementation check only)

`smoke.py --run-id DRYRUN-smoke-003` (protocol v3, manifest `protocol_version: 3`) ran on fixture b16-s21 only, in the namespace `smoke|EXP-ICEX-aaccfc/v2`, with 2 descents, 16 held-out points and 4 rho targets. Output is under `smoke/`. It checks identities, controls and agreement. The C-5 ratio, exponent, verdict and FX-A values were not computed or reported.

- **FX-A:** all fields were present, and the cross-check passed.
  - The named figure covered 6909 stage-1 attempts.
  - The supplementary figure also covered 1042 descent attempts.
  - The values were withheld.

The identity and control outcomes are identical to DRYRUN-smoke-002 (protocol v2), whose summary and dry-run directory are kept.

- **Fixture reproduction:** byte-identical.
- **Primary cell** (L = 3, B = 10):
  - 14 relations over 6909 attempts;
  - every attempt replayed against the exact oracle, with op counts exact;
  - all logs verified, and k recovered equals the target;
  - LA agrees with the dense reference;
  - descents 2/2 verified, and all 1042 descent attempts replayed;
  - stage 2 matches brute force on 16/16 points;
  - known false: 11 rows changed, the LA reported the system inconsistent, log verification failed, so the control passed.
- **Null:** L matches the interval factor base, and all logs verified.
- **m = 6:** L = 2; logs verified; stage 2 16/16.
- **m = 8:** L = 1; 129,563 attempts; logs verified; stage 2 16/16.
- **Rho:** 4/4 targets solved and certified.
- **Audits:** the sampled audit and the full-replay audit both accept.

An earlier smoke, DRYRUN-smoke-001, produced the same identity and control outcomes. It used a dict-per-attempt log format that made the dry-run directory 43 MB. That directory, which was never committed and is not a run record, was removed before snapshot. Its summary and logs are kept as `smoke/DRYRUN-smoke-001*`. The receipt format was then made columnar, and `raw-result.json` became an index.

Pre-data fixture property (from the trial plan, computed by verifier liftability only): at m = 8, fixtures b16-s21 and b20-s23 have L = 1. Their stage-cost cells need on the order of 10^5 and 10^6 attempts respectively. The smoke m = 8 cell took 27 s.

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
  - The Coordinator may rule which one carries the name.
- **OQ-14: memory and caps.**
  - The 8 GB limit is an in-process `ru_maxrss` guard, because macOS does not enforce RLIMIT_AS.
  - The machine caps (5,000,000 attempts per cell, 1,000,000 per descent) are machine protection. Reaching one is an infrastructure incompletion, never evidence.

## Environment

- Python 3.12.8, numpy 2.4.4, pytest 9.1.1.
- Sage: `/Users/adamburan/.local/bin/sage`, which launches `/Volumes/SSD990/cryptanalysis/sage`, with `DOT_SAGE` under `$TMPDIR`. Sage is used only for C-1 reproduction.
- The worktree is `/Volumes/SSD990/wt-amend-ic`, branch `coord/ic-leads-impl-20260928`, at HEAD `bd7a47d71cf62896cd953b4ff48a3586054997a9` when the report was written. The tree is dirty only in this directory.
