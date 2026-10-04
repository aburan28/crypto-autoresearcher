# TASK-20260924-94cc33: red-team review of the gapattr draft's difference from childend (zero-run)

Card: `ledger/handoffs/TASK-20260924-94cc33.yaml` (governs). Goal GOAL-GFPN-380702, question RQ-GFPN-c01af8,
experiment EXP-GFPN-05ff43, batch BATCH-e409ca. Archival task TASK-20260924-93f3ca. Repository HEAD read:
`237d95568f376fd31093efc7a3362ba6625b9e5f`. Companion: `review-report.yaml` (the machine-readable report; same
content).

**Observations only.** This report makes no approval recommendation and says nothing about D, the quotient,
H-GFPN-9a29be or HEUR-GFPN-DFLAT. Nothing in it is evidence about them.

**Object.** The DRAFT AMD-EXP-GFPN-05ff43-20260924-gapattr
(`experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml`, sha256
`919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7`; status draft at line 164, approved_by null
at 165, approval_decision null at 166). Its difference from childend (RH-1..RH-8, lines 242-443; RGL-6 and RGL-7,
457-476; the incorporated readings, 483-531) was read together with failclosed, readbackclose, readbackfull and
readbackcover.

**Zero runs.** No run package; no msolve, valgrind, callgrind_annotate, gp, Sage or builder child; no import of
any module of `implementation*/`, `tools/` or `harness/`; no import of a third-party module read under AJ-1; no
perf_event_open; no fork of a process running scanned code. Python ran with `-B` and `PYTHONDONTWRITEBYTECODE=1`.

## 0. Verdicts

| joint | verdict | one line |
|---|---|---|
| AJ-0 known-answer control | **holds** | the unchanged method flagged every object of CRG-4 (a)-(e), at record and package level |
| AJ-1 no fail-open (RH-1, RH-4) | **breaks** | CX-1: a lost launch record at an SE-3 / HR-3 re-solved tag is covered by another record of the same tag; PASS while definition (i) holds |
| AJ-2 no planned-basis refusal (RH-1) | **holds** | 683 of 683 listed files attributed; every normal outcome of every launch kind attributed |
| AJ-3 definitional scope (RH-2) | **holds** | every cap-mismatch outcome FAILs by 68-70 under every rule set; no RKR-4 (b) PASS / PASS_ZL row changed |
| AJ-4 development harness (RH-3) | **holds** | spec "out" substitution sound; comparator and fixtures read no environment, path or label; no computation differs |
| AJ-5 reads, reach, readers | **holds** | RFR-4 confirmed in this report's words; carried findings stand; readers listed |
| AJ-6 value classes, neutrality | **holds** | RH-1 reads are post-completion and read-only; RH-4 records only; classes as listed (OB-4) |

FAIL-OPEN counterexamples: **one family, CX-1** (lost-record class; definitions (i) and, on the launch-record
reading, (ii); NOT the foreign-process class, definition (iv)). It is reachable only under the lost-record premise
(a launch record absent without RL-1 (d) firing); no ordinary-operation path and no documented interpreter or
operating-system behaviour that supplies that premise was found. Planned-basis refusals: **none**. Fail-closed
findings: **FC-1..FC-7** (section 10.3), never a bar.

## 1. Integrity (CRG-2), applied first

Every check passed before any joint and again at report-writing time.

**(a) The draft.** On disk `919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7`. The
addendum_sha256 of the TASK-20260924-27ea14 receipt, as given by the dispatching session in the task message (the
card's blindness block allows this), is the same value. The receipt
`coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-27ea14/ledger-receipt.json` was **not opened**. Status
fields: `status: draft` (164), `approved_by: null` (165), `approval_decision: null` (166). PASS.

**(b) The bound drafts.**

| file | expected = on disk |
|---|---|
| `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml` | `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b` |
| `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml` | `1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c` |
| `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml` | `f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c` |
| `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml` | `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1` |
| `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml` | `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e` |

**(c) Archived reviews and censuses.** `integrity.py` (appendix) read only the `path_sha256` field of the snapshot
receipts of TASK-20260924-0c2fdc, 7e8a5d, 71d070, ddfb69 and a01341 (under
`coordination/goals/GOAL-GFPN-380702/archives/`) and compared every entry with the bytes on disk: ALL_OK True
(`integrity.out`, reproduced in the appendix). The card's expected values also match directly.

| file | receipt | sha256 |
|---|---|---|
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml` | 0c2fdc | `b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f` |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md` | 0c2fdc | `0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8` |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml` | 7e8a5d | `139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4` |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md` | 7e8a5d | `97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json` | 71d070 | `9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md` | 71d070 | `ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py` | 71d070 | `00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json` | ddfb69 | `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md` | ddfb69 | `5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py` | ddfb69 | `ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py` | a01341 | `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json` | a01341 | `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4` |
| `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md` | a01341 | `2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3` |

**(d) Frozen trees, plans and gate packages.**

```text
git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' \
    'experiments/EXP-GFPN-05ff43/trial-plan-*.json' experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a \
    experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a \
    experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956
```

printed nothing and exited 0, with the two globs quoted and, separately, shell-expanded. `git cat-file -t` of the
base printed `commit`; `git merge-base --is-ancestor dd103455380238ec2f20d17414de687acdcc822a HEAD` exited 0.
`git status --porcelain --untracked-files=all -- experiments/EXP-GFPN-05ff43
coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33` printed nothing before the deliverables were
written. PASS.

Released frozen inputs, hashed for the record: `k4a_anchor_system.py`
`3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b`; `square_analogue_n3.json`
`22550c2f4ede32a41d7b8134f2c72c04121d20065eacd6604640b0ef0e8a81ba`; `square_analogue_n4.json`
`e3bc6d120a52a898fd84e47efe54f727f20e2013c906522cd41a73303ae595a2`.

## 2. Method (one method, unchanged, for AJ-0..AJ-3)

The final evaluator `rt_eval.py` (sha256 `662e57565e314186a334173d0c4188acd7162bb21f9bce6196e69b2645ba893e`; its
output `rt_eval.out` `1c88d680bff71dbcc94039890726928b433bc6e9841df1e821a32900898e1290` and `rt_eval.json`
`cea33e7189aaa172db1d19ecadd084a4bcbfe606ebc2d4631571f3748b02a7ba`; all three reproduced or summarized in the
appendix) imports only json, os, re, itertools and sys. It reads two scratch files and nothing of the repository
as code.

- **Layer 1 (files).** Every file under child/, solver/, health/, comparator/, pari/ is attributed to launch records
  under RG4 = childend RG-4 (b) as worded (childend 423-437), RH1 = gapattr RH-1 (i)-(vi) as worded (246-280) with
  the same non-launch list, and RH1w = RH1 with (v) weakened as CRG-4 (e) words it. No attribution and not on the
  non-launch list = RECORDER GAP.
- **Layer 2 (packages).** RK = readbackclose RK-1, RK-3 as worded; RF = failclosed as worded; RG = childend; RH =
  gapattr (RG with RH-1, RH-2 (a)/(b), RH-4); RHw = RH with (v) weakened. The frozen checker items
  v2_check_run.py 66-67 and 68-70 are evaluated. Manifest variants: Mr (r3 base: requested cap from the raw
  envelope, r3_run_wrapper.py 550, None when the wrapper wrote raw) and Mc (requested cap recorded independently).
  k = number of other class-B launches.
- **Definitions** (failclosed 604-621) on truth facts: FAIL-OPEN iff PASS or PASS_ZL while (i)-(v); (ii) under two
  readings of "recorded pair" (LR: in a launch record; ANY: in any RB-2 source); (iv) LITERALLY: a record written in
  a process other than the installing one that no rule detects. PLANNED-BASIS REFUSAL iff a driver-logic outcome
  that a dependant's frozen logic acts on (or RFR-2 enumerates), designed (no constructed record loss), FAILs.
- **Listings (CRG-9).** Launch sets of the four archived r3 gate packages are RECONSTRUCTED by the frozen naming:
  `child/<tag>.spec.json` gives a child-job record (argv `[<python>, -B, implementation-v2/v2_child.py,
  <rd>/child/<tag>.spec.json]`, stdout/stderr `child/<tag>.stdout/.stderr`; v2_driver.py 92-102);
  `solver/<tag>.ms.log` or `health/<tag>.ms.log` gives an msolve record (argv `-f <dir>/<tag>.ms -o
  <dir>/<tag>.ms.out`; v2_driver.py 161-166, a1_health.py 141-147); `solver/<tag>.callgrind.stdout` gives a
  callgrind record (argv `valgrind --tool=callgrind --callgrind-out-file=<dir>/<tag>.callgrind.out msolve ... -f
  <tag>.ms -o <tag>.cg.ms.out`; v2_solver.py 515-518, v2_driver.py 208-209); `comparator/stdout.log` gives the
  comparator record (argv `[<comparator python>, k4a_anchor_system.py, <rd>/comparator]`; v2_driver.py 647-651);
  `pari/<tag>.gp.stdout` gives a gp record (a1_pari.py 91-96). child_end exec for a child job whose `.meta.json` or
  `.npz` exists and for every other reconstructed launch. Spec "out" values from the archived spec files. Paths
  compared absolutely under each package's recorded GFPN_RUN_DIR, which equals its current path for all four
  (command.txt). Listings by `listing.py` with O_NOATIME; every directory's lstat unchanged before and after.
  A listing check is a reading of r3 artifacts under r4 rule text, never a result about a package's verdict.
- **Versions kept.** rt_eval.v1.py (never run), rt_eval.v2.py (one run, TypeError, output rt_eval.v2.run1.out),
  rt_eval.v3.py (one run, superseded: record-removed constructions were tagged planned-basis refusals; outputs
  rt_eval.v3.out, rt_eval.v3.json), rt_eval.py (final). All reproduced verbatim in the appendix.

## 3. AJ-0: known-answer control (holds)

The method, unchanged, flagged every CRG-4 object.

**(a) readbackclose RK-1 / RK-3 as worded.**

| object | record level | package level |
|---|---|---|
| P-16 (raise at v2_solver.py 181) | RK: child_created **false** for a created child, definition (iii) (RF: undetermined) | RK k=1 Mc **PASS, FAIL-OPEN (ii-ANY), (ii-LR), (iii), (v)**; k=1 Mr FAIL by 68-70 (requested cap None); k=0 FAIL by 66-67. RF FAIL everywhere |
| P-F2 after P-14a | RK: child_created **false** for a created child, (iii) (RF: true) | RK k=1 Mc **PASS, FAIL-OPEN (ii-ANY), (ii-LR), (iii), (v)**; other variants FAIL. RF FAIL |
| W-1 (wrapper writes raw, r3_run_wrapper.py 491-505) | no launch record | RK **PASS_ZL** (Mr and Mc), **FAIL-OPEN (v)**. RF FAIL |

**(b) failclosed as worded, FO-1** (variants C and B; foreign-file write failed and interrupted; escaped exit 1 and
-2: eight objects). Record level: RF child_created true, class C or B, the foreign-process record detected by
NOTHING; RG and RH child_end undetermined. Package level: RF variant C **PASS with k=1, FAIL-OPEN (iv)** (k=0 FAILs
by 66-67: a class-C child has no pair); variant B **PASS with k=0 and k=1, FAIL-OPEN (iv)**. RG and RH FAIL in every
variant.

**(c) childend as worded, PB-2 and PB-3.**

- PB-2 (cells m = 4, raw_grid child's meta): records grid_raw_t0 child, msolve raw_t0, callgrind raw_t0, all class
  B, exec. RG **FAIL, PLANNED-BASIS REFUSAL** (basis X-09/X-10 aggregates, v2_driver.py 1259-1267, a1_driver.py
  301-310), gap `child/grid_raw_t0.meta.json`. RF PASS, RH PASS.
- PB-3 (cells m = 5, one SE-3 re-solve): records S5_t0, S5_t1 attempt 1 (SSF), attempt 2, class B, exec. RG
  **FAIL, PLANNED-BASIS REFUSAL** (basis X-08 m = 4 `_condition_met`, v2_driver.py 1110-1127; X-09/X-10), gaps
  `solver/S5_t1.ms.err.ssf-attempt1`, `.ms.log.ssf-attempt1`, `.ms.out.ssf-attempt1`. RF PASS, RH PASS.

**(d) Listing check under childend RG-4 (b) as worded** (launch sets reconstructed). Full per-file table in the "Listing tables" section below.

| package | files in the five dirs | reconstructed records | unattributed .meta.json | unattributed .npz | other |
|---|---|---|---|---|---|
| RUN-GFPN-f6a21a | 284 | 88 (childjob 16, msolve 36, callgrind 36) | **16** | 4 | 0 |
| RUN-GFPN-902222 | 284 | 88 (childjob 16, msolve 36, callgrind 36) | **16** | 4 | 0 |
| RUN-GFPN-f5412a | 32 | 7 (childjob 1, msolve 5, comparator 1) | **1** | 1 | 0 |
| RUN-GFPN-bfe956 | 83 | 19 (childjob 11, msolve 8) | **11** | 7 | 0 |

The 16, 16, 1 and 11 match the readback census (md 431-434). The unattributed files, each listed:

- RUN-GFPN-f6a21a and RUN-GFPN-902222 (the same 20 each): `child/fixture_S3.meta.json`, `child/fixture_S3.npz`,
  `child/fixture_S3_rescaled.meta.json`, `child/fixture_S3_rescaled.npz`, `child/fixture_torsion_S3_norm.meta.json`,
  `child/fixture_torsion_S3_norm.npz`, `child/fixture_torsion_S3_rq.meta.json`, `child/fixture_torsion_S3_rq.npz`,
  `child/fx_fresh1_raw_u.meta.json`, `child/fx_fresh1_raw_x.meta.json`, `child/fx_fresh2_raw_u.meta.json`,
  `child/fx_fresh2_raw_x.meta.json`, `child/fx_planted0_raw_u.meta.json`, `child/fx_planted0_raw_x.meta.json`,
  `child/fx_planted1_raw_u.meta.json`, `child/fx_planted1_raw_x.meta.json`, `child/fx_reg0_raw_u.meta.json`,
  `child/fx_reg0_raw_x.meta.json`, `child/fx_reg1_raw_u.meta.json`, `child/fx_reg1_raw_x.meta.json`.
- RUN-GFPN-f5412a: `child/anchor_S4.meta.json`, `child/anchor_S4.npz`.
- RUN-GFPN-bfe956: `child/ctl_S3.meta.json`, `child/ctl_S3.npz`, `child/ctl_S3_rescaled.meta.json`,
  `child/ctl_S3_rescaled.npz`, `child/ctl_identity_n3.meta.json`, `child/ctl_identity_n3.npz`,
  `child/ctl_identity_n5_m3.meta.json`, `child/ctl_identity_n5_m3.npz`, `child/ctl_identity_n5_m4.meta.json`,
  `child/ctl_identity_n5_m4.npz`, `child/ctl_raw_n5_m3.meta.json`, `child/ctl_raw_n5_m4.meta.json`,
  `child/ctl_raw_planted.meta.json`, `child/ctl_raw_random.meta.json`, `child/ctl_torsion_S3_norm.meta.json`,
  `child/ctl_torsion_S3_norm.npz`, `child/ctl_torsion_S3_rq.meta.json`, `child/ctl_torsion_S3_rq.npz`.

**(e) gapattr with RH-1 (v) weakened vs as worded.**

- File level, RUN-GFPN-bfe956 with the reconstructed record childjob:ctl_S3 removed: RH1w 0 unattributed; RH1 as
  worded 5 recorder gaps (`child/ctl_S3.meta.json`, `.npz`, `.spec.json`, `.stderr`, `.stdout`). Table in the "Listing tables" section below.
- KA-e1 (controls, G4 shape, ctl_S3 record removed, build ok): RHw **PASS, FAIL-OPEN (i), (ii-LR)** (the meta file
  carries its pair, so (ii-ANY) does not hold); RH FAIL with the five gaps.
- KA-e2 (cells m = 4, raw_grid child crashed after exec, partial .npz, record removed): RHw **PASS, FAIL-OPEN (i),
  (ii-ANY), (ii-LR)**; RH FAIL (gaps `child/grid_raw_t0.npz`, `.spec.json`, `.stderr`, `.stdout`).

What would change the verdict: any CRG-4 object not flagged. None was missed.

## 4. AJ-1: attribution and callback, no fail-open (breaks)

Reading: failclosed RFR-1 (definitions (i)-(v); (iv) literally) on RH-1, RH-4 and their interaction with RG-1,
RF-0..RF-3, RL-1 and RL-3.

Files and lines read: gapattr 242-355, 379-415, 457-476, 483-531; childend 250-336 (RG-1), 337-372 (RG-2), 416-437
(RG-4); failclosed 280-418, 604-621, 652-663; readbackfull 209-252, 269-285; r3_resolve.py 224-238, 248-319,
373-390, 397-409; r3_common.py 88-90; v2_driver.py 92-107, 118-147, 158-214, 645-676; v2_solver.py 149-308,
512-552; a1_health.py 140-152, 223-253; a1_pari.py 86-124; r3_entry_v2.py 55-84; r3_entry_a1.py 88-115; review
TASK-20260924-1ecb7d yaml and md in full (X1, X6b, X10 at 268-331).

### 4.1 Worked attack (1): a lost record per clause

- **Renamed attempt file matched to another record: BREAKS (CX-1, section 10.1).** Every attempt of one SE-3 /
  HR-3 event launches with the same argv, stdout_path and stderr_path (v2_driver.py 161-166; a1_health.py
  141-147); the unrenamed files are the last attempt's. Remove any ONE of n >= 2 records: n-1 >= k records remain
  for every renamed attempt k <= n-1, so (vi) attributes every renamed file (to the wrong attempt when an earlier
  record is the absent one) and (i) / (ii) attribute the final files. No gap, PASS. Evaluated: LR-1, LR-2, LR-3,
  LR-5 and all 11 single removals among 2, 3 and 6 attempts: RH PASS, FAIL-OPEN (i), (ii-LR). Two removals of three
  (LR-4): gap, FAIL. Under childend the renamed files are gaps in every case (RG FAIL).
- **Renamed file matched to another tag: holds.** (vi) needs records whose stdout_path is exactly
  `<dir>/<tag>.ms.log` for the file's own tag and directory.
- **Two spec files naming the same out: holds.** (v) needs the record's LAST argv element to be
  `<dir>/<tag>.spec.json` and "out" = `<dir>/<tag>` of that tag. Every child-job call site derives a distinct tag in
  one package (v2_driver.py 317, 348, 548, 671, 768, 782, 801, 805, 816, 961, 1161; a1_driver.py 146); the four
  listings repeat no child tag. A lost child-job record leaves its five files as gaps (LR-8, KA-e1, KA-e2: FAIL).
- **Spec rewritten after its launch:** no frozen or r3 path does so (written once at v2_driver.py 98-99, before
  run_child at 101). Anything else is RGL-7 (gapattr 470-476): visible after the fact, not prevented. Declared limit.
- **Callgrind argv naming a path another launch writes: holds.** It names `<tag>.ms`, `<tag>.cg.ms.out` and the
  callgrind out file, not the msolve launch's `.ms.out`, `.ms.log`, `.ms.err`; with the msolve record absent those
  are gaps (LR-6: FAIL).
- **Directory named by one argv but written by two launches: holds** for the frozen launch set: only comparator/ is
  named (v2_driver.py 647-651) and only the comparator writes there; comparator record absent gives gaps (LR-7:
  FAIL). See OB-1.

### 4.2 Worked attack (2): definition (iv) read literally

Reading used: (iv) holds when a record is written in a process other than the installing one (the r4 entry process
in which the recorder is installed) and no rule detects it (neither flagged nor attributed to a writer the rules
name).

| writer (process) | records / files | known to the rules | treatment | (iv) holds? |
|---|---|---|---|---|
| r4 run wrapper (entry's parent) | manifest, command.txt, fallback raw-result.json (r3_run_wrapper.py 491-505), post-completion listing (RL-3) | yes: RF-0 (b), RL-4, RL-6; r3 base 423-570 | raw_result_writer "wrapper" FAILs (RF-2 (vi), RF-3 (a)); requested cap (Mr, 550) | no |
| installing process (entry, frozen driver, resolve layer, recorder) | launch, attempt, pass-through records; solver-events.json; raw-result.json via finish; spec files; .ms inputs; health inputs; gp script; pari-stack.json | yes | read | n/a |
| fork child before exec (v2_solver.py 182-208) | report on the pipe (read at 214-227); opens stdout/stderr (188-189); if it ESCAPES: recorder-foreign-<pid>.json (RF-1 (b)) and pari-stack.json from the entry's finally (r3_entry_v2.py 75-77; r3_entry_a1.py 106-108) | yes: RF-1 (b), RG-1 | FO-1 (write ok, failed, interrupted; exit 1 or -2): child_end undetermined, FAIL. X1, X10, X6b: frozen_pre_exec_exit or exec, PASS, IF supplying code existed (none found) | only on hypothetical X1, X10, X6b |
| build or raw-grid child job after exec (v2_child.py) | `.stdout`, `.stderr` (i); `<out>.npz`, `<out>.meta.json` (v) | yes | attributed; meta read as RB-2 (b) source | no |
| comparator (k4a_anchor_system.py) | `stdout.log`, `stderr.log` (i); four `.ms` and `k4a_results.json` (iv) (k4a 279-281, 318) | yes | attributed; read by the driver (v2_driver.py 653-669) | no (OB-1: any other writer there would be attributed too; grandchildren are RFL-1, NOT A BAR) |
| msolve | `.ms.log`, `.ms.err` (i); `.ms.out` (ii) | yes | attributed | no |
| valgrind (and msolve under it) | `.callgrind.stdout`, `.stderr` (i); `.callgrind.out` (iii), removed at v2_solver.py 549 except 521-524; `.cg.ms.out` (ii), removed at v2_driver.py 211 | yes | attributed | no |
| callgrind_annotate (v2_solver.py 533), gp --version-short (a1_pari.py 121) | nothing in the package (output captured); not through run_child; reaped before return | no launch record | none needed | no record written |
| gp (a1_pari.py 91-96) | `.gp.stdout`, `.gp.stderr` (i); `.gp` script driver-written (ii), non-launch list | yes | attributed; stdout read at a1_pari.py 101 | no |

### 4.3 Worked attack (3): RH-4

| case | RG | RH | class |
|---|---|---|---|
| H4-a signal-raised exception caught by the callback's own try | PASS | child_end undetermined, **FAIL** | fail-closed (FC-5) |
| H4-b exception of the callback's own code, caught | PASS | undetermined, **FAIL** | fail-closed (FC-5) |
| H4-c pending signal at the callback's entry, before its try | undetermined, FAIL | undetermined, **FAIL** | fail-closed |
| H4-d exception escaping another after-fork callback or the epilogue | PASS | PASS, **no definition holds** | not fail-open (OB-2) |

RH-4 opens no route to a favourable child_end.

### 4.4 Worked attack (4): RG-1 residuals X1, X6b, X10

- **Repository** (`scan.py`: ast over every .py of the three trees, guard refused 0 imports and 0 launches;
  `scan.out` in the appendix). os._exit(97/98/99) only in the frozen child branch (v2_solver.py 196, 201, 208);
  sys.exit(96) / (0) only in the exec'd v2_child.py (60, 69, 81); every other sys.exit is a script entry point's
  `sys.exit(main())` or a fixed 0, 1 or 2 outside the driver's unwinding path; SystemExit raises carry string codes
  (v2_common.py 100; a1_driver.py 52, 224, 233) or lie in development or plan-writing scripts; the r3 entries catch
  and RE-RAISE (r3_entry_v2.py 69-79; r3_entry_a1.py 100-110); exec only at v2_solver.py 204-205; subprocess.run
  only in wrapper, checker and development code and in v2_common.sh (57-61), a1_pari.py 121, v2_solver.py 533,
  none on the driver's unwinding path (v2_driver.py has no broad handler and no finally); no hook registration in
  the three trees. The r4 code does not exist; RH-5 (a), (b) check it at stage time.
- **Third-party text read** (never imported) under `/usr/local/lib/python3.11/dist-packages`: cypari2 2.2.0 (23
  text files), cysignals 1.12.5 (8), python-flint 0.9.0 (60 .py/.pyi), numpy 2.4.6 (142 non-test .py). No os._exit,
  sys.exit, exit(, abort(, exec*, posix_spawn, fork, register_at_fork, atexit, os.system, subprocess, os.kill or
  raise_signal call, except `flint/test/__main__.py` 164 (a test runner the entries do not import). Compiled `.so`
  modules and PyYAML were NOT read.
- **Result:** no supplying code found; X1, X10, X6b remain hypothetical; RGL-6 (gapattr 459-469) declares the
  remainder. Not a counterexample.

### 4.5 Worked attack (5): classification

CX-1: FAIL-OPEN (a break). FO-1 under gapattr, H4-a, H4-b, H4-c, LR-4, LR-6, LR-7, LR-8: fail-closed. H4-d: neither.
X1, X10, X6b: unsupplied hypotheticals.

What would change the verdict: a rule making the launch-record count of a re-solved tag a checked quantity (CX-1's
mutation); a reading that the lost-record premise lies outside RFR-1's search (it names "any path or outcome it can
construct from ... this lineage's rules", and CRG-4 (e) and RH-6 (i) (19), (22) use the premise). Supplying code
for X1, X10 or X6b would add a foreign-process-class break.

## 5. AJ-2: attribution, no planned-basis refusal (holds)

Reading: failclosed RFR-2 on RH-1. Files and lines: gapattr 243-287; v2_driver.py 92-214, 645-676, 1130-1236,
1248-1326; v2_child.py in full; v2_solver.py 512-552; a1_health.py 140-253; a1_pari.py 86-124; a1_driver.py
56-215; r3_resolve.py 224-238, 310; numpy/lib/_npyio_impl.py 756-800 (text); the four listings; the 44 spec "out"
values; the four GFPN_RUN_DIR lines.

**(1) Listing check under RH-1 as worded** (launch sets reconstructed; full per-file table in the "Listing tables" section below):

| package | files | (i) | (ii) | (iv) | (v) | unattributed |
|---|---|---|---|---|---|---|
| RUN-GFPN-f6a21a | 284 | 176 | 88 | 0 | 20 | **0** |
| RUN-GFPN-902222 | 284 | 176 | 88 | 0 | 20 | **0** |
| RUN-GFPN-f5412a | 32 | 14 | 11 | 5 | 2 | **0** |
| RUN-GFPN-bfe956 | 83 | 38 | 27 | 0 | 18 | **0** |

(first applying clause counted; every applying clause listed per file in the table).

**(2) Normal outcomes the gate never produced** (from the frozen code; evaluator N-1..N-13, file-by-file in the
appendix's `rt_eval.out`):

| id | outcome | attribution | RH verdict (RG) |
|---|---|---|---|
| N-1 | cells m = 5 measured | `.ms` (ii), `.ms.log`/`.ms.err` (i), `.ms.out` (ii) | PASS (PASS) |
| N-2 | cells m = 5 not_measured (timeout, memory; no .ms.out) | as N-1 | PASS (PASS) |
| N-3 | cells m = 4, raw_grid measured, callgrind ok | meta (v) (.npz removed, v2_driver.py 144) | PASS (refusal) |
| N-4 | raw_grid child crashed after exec (partial .npz, 137-139) | .npz (v) | PASS (PASS) |
| N-5 | SE-3 re-solve at S-1, 2 attempts | renamed files (vi) k=1 | PASS (refusal) |
| N-6 | controls_a1: HR-3 re-solve at S-2, gp, health, builds, solves | health inputs and health-<p>.json non-launch; gp script (ii); renamed health files (vi) | PASS (refusal) |
| N-7 | failing callgrind child (out file left, v2_solver.py 521-524) | `.callgrind.out` (iii) | PASS (refusal) |
| N-8 | timed-out callgrind child (no out file; .cg.ms.out removed at v2_driver.py 211) | as N-3 | PASS (refusal) |
| N-9 | cached builds (out under the cache dir, v2_driver.py 96) | spec (ii), stdout/stderr (i) | PASS (PASS) |
| N-10 | fixture4 uncached builds and solves | (v) | PASS (refusal) |
| N-11 | child-job refusal paths: refused meta (v2_child.py 68/80), refused before fork (class A), ERR setrlimit (class C) | (v), (ii), (i) | PASS (refusal) |
| N-12 | anchor-identity: comparator, uncached build, gb_only solves | (i), (iv), (v), (ii) | PASS (refusal) |
| N-13 | Z-C5 (no launch) | none needed | PASS_ZL (PASS_ZL) |

**(3) Where it may break**, checked: valgrind side files (`.callgrind.out` (iii), `.cg.ms.out` (ii)); a valgrind core
file would land in the child's cwd, the repository root (r3_run_wrapper.py 477; no call site passes cwd,
v2_solver.py 186-187), outside the five directories (B-8, recalled); msolve auxiliary files: none among 683 listed
files at the gate invocations (B-9); gp and health side files (N-6); HR-3 health re-solve files (N-6); child-job
refusal paths (N-11); np.savez writes the named file directly (B-6, read).

No planned basis outcome is refused. Fail-closed found here: FC-3. What would change the verdict: a normal-path file
of a planned basis outcome that no clause names, or a check run at a root other than the recorded one (FC-3).

## 6. AJ-3: definitional scope (holds)

Reading: failclosed RFR-2 on RH-2 with childend RG-2. Files and lines: gapattr 288-318; childend 337-372; failclosed
280-308, 355-371, 664-672; readbackclose-census.md 472-494 (table 476-492); v2_check_run.py 62-73; v2_solver.py
177-308 (193, 197-201, 226-232); v2_driver.py 989-1003, 1006-1013, 1110-1127, 1248-1326.

| package kind | outcome with an unequal pair | RF | RG | RH |
|---|---|---|---|---|
| cells m = 5 | every launch P-8 / every launch P-9 / one P-9 plus one measured | FAIL (68-70), planned-basis refusal (X-08, X-09/X-10) | same | FAIL (68-70), cap-mismatch stop |
| cells m = 4 | same three | FAIL, refusal (X-09/X-10) | same | FAIL, cap-mismatch stop |
| build | same three | FAIL, refusal (X-07 `_load_build`, v2_driver.py 989-1003, 1068-1075) | same | FAIL, cap-mismatch stop |
| controls (gate) | one P-9 build child | FAIL, refusal (row 478) | same | FAIL, cap-mismatch stop |

The frozen dependants read the raw outcome (`_load_build`, `_prior_cells`, `_condition_met`, aggregate), but no frozen
rule reads the cap read-back, and every protocol version FAILs these outcomes by 68-70. RH-2 changes no verdict: its
class is read only by the RF-3 (b) stop record and the planned-basis scope (RH-7, 428-429).

RKR-4 (b) rows that are PASS or PASS_ZL (md 476-492):

| row | kind | RF | RG | RH |
|---|---|---|---|---|
| 478 | G1..G4 completed_valid (fixture shape) | PASS | FAIL (refusal) | PASS |
| 480 | controls_a1 image | PASS | FAIL (refusal) | PASS |
| 481 | fixture4 launched | PASS | FAIL (refusal) | PASS |
| 482 | Z-F4 | PASS_ZL | PASS_ZL | PASS_ZL |
| 483 | build (cached) | PASS | PASS | PASS |
| 485 | cells m = 5 measured (and with one SE-3 re-solve) | PASS (PASS) | PASS (FAIL, refusal) | PASS (PASS) |
| 486 | Z-C5, both run_status variants | PASS_ZL | PASS_ZL | PASS_ZL |
| 488 | cells m = 4 (and with a failed callgrind child) | PASS | FAIL (refusal) | PASS |
| 489 | aggregate v2 | PASS | PASS | PASS |
| 490 | contingency | as the kind replaced | as replaced | as replaced |
| 491 | W-1 | not a planned basis outcome (failclosed 671-672); FAIL | FAIL | FAIL |

No row changed by RG-2 and RH-2 together relative to RF. Observations OB-3, OB-4. What would change the verdict: a
frozen rule acting on a package with an unequal pair before 68-70 stops it, or a PASS / PASS_ZL row that FAILs under
RH by design.

## 7. AJ-4: development harness (holds)

Reading: failclosed RFR-3 on RH-3 with childend RG-3. Files and lines: gapattr 319-342; childend 373-415; failclosed
419-483; v2_driver.py 92-107, 118-147, 645-676, 752-931; a1_driver.py 56-215; v2_common.py 36-42, 97-101; the 44
archived specs; `k4a_anchor_system.py` and both fixture JSON files in full; r3_run_wrapper.py 433-442, 464, 544-551;
r3_check_run.py 250-257, 324-334; r3_dv12.py 116-121; r3_dv7.py 290-318.

- **RH-3 (a).** Spec keys: job, field, curve, kind, m, beta_override, cap_bytes, out, and sample_seed + to_cache
  (build_poly) or x_R + nodes (raw_grid) (v2_driver.py 94-96, 120-121, 134-135; the 44 archived specs). Only "out"
  carries a path; it equals `<GFPN_RUN_DIR>/child/<tag>` for all 44 archived specs (to_cache false). Substituted,
  a development "out" equals the plan path; every other key is label-free and path-free. Applies to controls (11
  uncached specs), anchor-identity (1) and controls-a1 (its a1_driver.py 146 builds).
- **Comparator and fixtures.** `k4a_anchor_system.py` reads no environment variable, run directory or label: its
  only input is `OUT = sys.argv[1]` (56); it writes four `.ms` files and `k4a_results.json` there (279-281, 318);
  seeds are fixed strings keyed by task text and p. The fixture JSON files are data only. The sub-item the previous
  review left inconclusive is closed.
- **RG-3 (a)-(d) with RH-3 (b)**, on the r3 base: the ladder read at r3_run_wrapper.py 464 and recorded at 546;
  git_tree_state and the phase-A receipt reads at 437-441; r3_check_run.py 255-256 tests only the presence of the
  archive task's commit; r3_dv12.py 119 writes "dev-synthetic-not-a-commit" (RH-3 (b) withdraws that citation
  correctly); the r3_dv7.py 301-314 tracer is not carried; the three expected items are r3_check_run.py 329-330,
  331-332, 333-334.
- **No computation difference** in seeds, streams, targets, substituted argv, cap, watchdogs or thread count.

Fail-closed found here: FC-4. What would change the verdict: a frozen read of the label or of a redirected value
that changes a computed value.

## 8. AJ-5: reads, reach and readers (holds)

**RFR-4, confirmed in this report's words.** X-13 (a1_check_run.py 79-84) takes the id named by the plan's
`gate.addendum_blocking_package` (RUN-GFPN-2c4862 in trial-plan-v2-a1-r3.json), opens
`<EXP_DIR>/runs/<id>/raw-result.json` and requires `run_status == "completed_valid"` and `gate_pass is True`. X-02
(r3_run_wrapper.py 190-196, reached at 288-289 for the a1-r3 plan when `controls_a1_gate_required`) takes the same id
from the same field, opens `RUNS/<id>/raw-result.json` through `_raw` (97-104) and applies the same two tests. The
roots agree in production (a1_common.py 44 and r3_common.py 31 are `EXP_DIR/runs`; r3_run_wrapper.py 68 `RUNS =
R.RUNS_DIR`, redirected only in development checks). A missing file fails both (X-13 reads `{}`; X-02 refuses "has
not run"); an unparseable file fails both (X-13's json.load raises and the checker exits non-zero; X-02 reads
`run_status "unparseable"` and refuses). **The values X-13 reads are the fields X-02 reads.**

**RLR-2 / RKR-2 carried findings stand**, with no change since `dd103455380238ec2f20d17414de687acdcc822a` (the CRG-2
(d) diff is empty). Re-derived by scan.py: run_child defined once (v2_solver.py 149; `_run_child_locked` 177); every
production reference is a Load of the module attribute or module global (v2_driver.py 101, 166, 650; v2_solver.py 517;
a1_health.py 147; a1_pari.py 96; v2_solver.py 171 for `_run_child_locked`); zero `from v2_solver import`; the only
other references are development code (r3_devchecks.py 190; r3_devchecks_more.py 80). dis of v2_solver.py (text
compiled in the scan process, sha256 `0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d`): line 181 is
CALL os.fork then STORE_FAST pid.

**RFR-6 readers.**

| value | readers | change to what they compute |
|---|---|---|
| RH-1 attribution | r4 RL-3 gap computation (post-completion, epsilon) -> RF-3 (a), RF-3 (b) stop record; DV-18 RH-6 (i) (18)-(22) | none to frozen or r3 readers (there are none) |
| renamed_files as RH-1 (vi) reads them | written at r3_resolve.py 310 (224-238); r3 solver-events checks and sweeps (r3_check_run.py 189-224) | none; RH-1 reads read-only |
| spec files as RH-1 (v) reads them | the exec'd v2_child.py; byte and key sweeps (a1_check_run.py 51-58; r3_check_run.py 189-224) | none |
| RH-4 mark | RG-1 (c) -> RF-0 (c), RF-3 (a), RF-3 (b) | none to frozen readers |
| RH-2 class | RF-3 (b) stop record and the planned-basis scope only | none |
| raw_result_writer | RF-0 (b), RF-2 (vi), RF-3 (a), planned-basis scope (RH-2 (b) re-reads the scope sentence only) | none |
| recorder-foreign file | RF-1 (b) writes; RF-2 (viii), RF-3 (a), RL-3 listing | sweeps see one more file in a FAIL package |
| `undetermined` | RF-0 (c), RF-3 (a), RG-1 (c)/(d), RH-4 | key sweeps read keys, not this value |

REG-1, the key and byte sweeps and the frozen checkers: unchanged in what they compute.

## 9. AJ-6: value classes and neutrality (holds)

- RH-1's reads are post-completion and read-only (RH-7, 419-422): they cannot change any value the frozen parent or
  the resolve layer records, or the order of any frozen step.
- RH-4 records only, inside the RG-1 callback (class gamma, 423-427); absent an exception it changes no value and no
  order. With one, the callback consumes it: OB-5 (report-only stderr difference), FC-5 (cost).
- RH-7: RH-1 attribution epsilon, RH-4 mark gamma, exactly one each; the RH-2 class receives no class letter
  (428-429) while the last bullet (430-431) requires DV-11 to list it "with exactly one class" (OB-4).

## 10. Counterexamples, refusals, fail-closed findings, observations, behaviours

### 10.1 CX-1 (AJ-1): FAIL-OPEN

- **Definitions met:** (i); (ii) on the launch-record reading of "recorded pair" (not on the any-RB-2-source reading).
- **Class:** lost launch record at a re-solved tag. NOT the foreign-process class (definition (iv)).
- **Reachability:** not through ordinary operation and not through documented interpreter or operating-system
  behaviour, as far as found. It needs a launch record absent without RL-1 (d) firing (readbackfull 244-249: a
  recording failure is an SE-2 (4) consistency violation), or solver-events.json altered after the launch (RGL-7,
  gapattr 470-476: visible after the fact, not prevented). It is the premise that CRG-4 (e), the card's AJ-1 worked
  attack (1), RH-1's own WHY sentence (gapattr 284-287) and RH-6 (i) (19), (22) (394-407) use.

| step | file and lines | event |
|---|---|---|
| 1 | r3_resolve.py 373-390; readbackfull 212-243 (RL-1 (a)-(c)); childend 420-422 (RG-4 (a)) | A cells m = 5 package runs under the r4 entry with SE-3 installed and the RL-1 recorder in place of v2_solver.run_child. The driver calls SE-3 solve for tag S5_t1 (not gb_only), entering `_bounded` (389 -> 248). |
| 2 | r3_resolve.py 262-263; v2_driver.py 161-166 | Attempt 1: the frozen solve writes `solver/S5_t1.ms` (162), launches msolve with `-f solver/S5_t1.ms -o solver/S5_t1.ms.out` (165), stdout `solver/S5_t1.ms.log`, stderr `solver/S5_t1.ms.err` (166). The recorder appends L1 (class B: created, pair read, equal to the cap; failclosed 381-383). |
| 3 | r3_resolve.py 267-279, 297-310; r3_common.py 88-90; r3_resolve.py 224-238 | SSF signature: event created (277-279); k = 1 < K + 1 = 6; the three files renamed to `S5_t1.ms.out.ssf-attempt1`, `.ms.log.ssf-attempt1`, `.ms.err.ssf-attempt1`, listed by their renamed names under `renamed_files["attempt1"]` (235, 310). |
| 4 | r3_resolve.py 258-263, 295-296, 313; v2_driver.py 161-166 | Attempt 2 (after spacing, 260-261) rewrites `S5_t1.ms` and launches msolve with the SAME argv, stdout_path, stderr_path; the recorder appends L2 (class B). No SSF: loop ends; accepted_attempt 2. |
| 5 | readbackfull 223-227, 244-249; gapattr 470-476 | THE PREMISE: L2 absent from launch_records, L1 present, no consistency violation recorded. |
| 6 | gapattr 250-251, 264-274 | RH-1: `S5_t1.ms.log`, `.ms.err` (attempt 2's) to L1 by (i); `S5_t1.ms.out`, `S5_t1.ms` to L1 by (ii); the three `.ssf-attempt1` files to L1 by (vi) (event entry present; >= 1 record with stdout_path `solver/S5_t1.ms.log`; L1 first). No recorder gap. |
| 7 | failclosed 376-395 (RF-3 (a)); v2_check_run.py 66-70 | Every launch record present is class B; no gap, no recorder-foreign file, no undetermined; raw_result_writer driver; the frozen items pass (attempt 2's pair is in its RB-1 attempt record and raw, equal to the cap). **PASS** (Mr and Mc). |
| 8 | failclosed 608-614 | The pair the parent read for attempt 2's child (227 executed) is in no launch record: **(i)**. That child executed argv with no pair in a launch record: **(ii)** (launch-record reading). PASS while (i) holds: **FAIL-OPEN**. |

Variants: LR-2 (attempt 1's record absent: its renamed files go by (vi) to L2, the wrong attempt; PASS); LR-3 (three
attempts, attempt 2's record absent: its renamed files go by (vi) k=2 to attempt 3's record; PASS); LR-5 (HR-3 at
S-2, a1_health.py 140-147 via r3_resolve.py 397-409, health/, final record absent; PASS); every single removal among
2, 3 and 6 attempts (11 cases): PASS. Two removals of three (LR-4): FAIL. Under childend RG-4 (b): FAIL in every case
(and PB-3 on the designed path).

**Cheapest mutation.** For every tag with an SE-3 or HR-3 event, require the number of launch records whose
stdout_path is `<dir>/<tag>.ms.log` to EQUAL the event's attempt count (`len(event["attempts"])`, r3_resolve.py 270,
277), a mismatch being a recorder gap; attribute the unrenamed final files of such a tag only to the accepted
attempt's record (`accepted_attempt`, 313). Equivalently: a file named by more than one launch record is attributed
only when those records are exactly one event's attempts.

**Cheapest discriminating control.** RH-6 (i) (19) third case as worded ("one launch record of the tag removed yields
a recorder gap and FAIL") on a scratch copy with one stand-in SSF attempt: RH-1 as worded gives no gap and PASS (LR-1,
LR-2), the mutated rule gives a gap and FAIL.

**What it is not.** Not an ordinary-operation route found; not a foreign-process route; not a statement about any
archived package; not evidence about D.

### 10.2 Planned-basis refusals

None found under AJ-2, AJ-3 or any other joint. The childend refusals (PB-2, PB-3, N-3..N-8, N-10..N-12, RKR-4 (b)
rows 478, 480, 481, 485, 488) do not occur under gapattr.

### 10.3 Fail-closed findings (never a bar)

| id | joint | finding | cost |
|---|---|---|---|
| FC-1 | AJ-1 | RH-6 (i) (19) third case and (20) (gapattr 397-400) cannot be met by RH-1 as worded (CX-1: no gap, PASS); DV-18 STOPs there by construction | an r4 stage stop for a Coordinator decision; it is also the check that would expose CX-1 |
| FC-2 | AJ-1 | RH-6 (i) (22) expects `.npz` among the gaps (404-407); a raw_grid child's `.npz` is removed at v2_driver.py 144 (evaluator RH6_22_raw_grid: four gaps, no .npz) | a DV-18 stop if (22) uses a raw_grid child job |
| FC-3 | AJ-2 | RH-1 compares recorded absolute paths; a package checked at another root has every launch file unattributed (REL-1: 8 gaps, FAIL) | a refused admission if run from another root; a Coordinator decision (the evaluator's planned-basis tag on REL-1 is mechanical, DV-10) |
| FC-4 | AJ-4 | development packages record dev-run-directory paths in fields no accepted-label list names: raw["build"]["npz"] (v2_driver.py 129; 671-673), `_slim` argv in raw child records (128, 150-154; comparator 652, 655), a1_pari.py 97 ("script", "command"), a1_health.py 148-149 ("input.path", "command"); no computed value differs | a DV-18 stop if read as "any other frozen read of the label" (failclosed 478-481) |
| FC-5 | AJ-1 / AJ-6 | RH-4 consumes a Python-level signal exception raised in the callback body (FAIL, H4-a/b) and the interrupt does not stop the driver; one pending at entry gives undetermined (H4-c) | a spurious FAIL and the driver's continued run time; a Coordinator decision |
| FC-6 | AJ-1 (carried) | a host without RGL-1's counter behaviour, or a child killed before exec, gives undetermined (childend RGL-1; review 1ecb7d FC-B, FC-C) | a FAIL or a stage stop (RH-5 (d)) |
| FC-7 | AJ-1 | lost-record constructions outside CX-1 FAIL: LR-4, LR-6, LR-7, LR-8, KA-e1, KA-e2 | none beyond a FAIL |

### 10.4 Observations

- **OB-1 (AJ-1).** RH-1 (iv) attributes by the directory an argv names (255-256), while RH-1's WHY sentence says "No
  clause attributes a file by its directory alone" (284-285). A file under comparator/ written by a process the
  rules do not know is attributed to the comparator record (evaluator IV-1: PASS). Carried unchanged from childend
  RG-4 (b); the known writers there are the comparator and possibly its grandchildren (RFL-1, NOT A BAR, failclosed
  661). No other writer found.
- **OB-2 (AJ-1).** RH-4's "the frozen parent may continue where it would otherwise have raised at v2_solver.py 181"
  (353-355) assumes an after-fork callback exception would propagate from os.fork; by recalled CPython behaviour
  (B-2) it goes to the unraisable hook and os.fork returns. H4-d gets no mark and needs none.
- **OB-3 (AJ-3).** A P-9 launch is recorded "crashed"; the m = 4 rule's stated basis (stopping rule 3: timeout / OOM
  / crash, as review TASK-20260924-1ecb7d quotes it) would act on a crash; 68-70 FAILs the package first. RH-2 (d)'s
  condition on "no launch of the class released a capped workload under a recorded cap equal to the requested cap"
  is met by pure P-8 / P-9 packages, not by mixtures at the outcome level; RH-2 (a) classes mixtures by the failing
  item, which they meet.
- **OB-4 (AJ-3 / AJ-6).** RH-7 gives the RH-2 class no class letter but requires DV-11 to list it with exactly one
  class; childend RG-8 left RG-2 the same way.
- **OB-5 (AJ-6).** Without RH-4's catch an escaping callback exception would be printed to the driver's stderr by the
  unraisable hook (B-2); with it, nothing is printed: a report-only difference in a FAIL package.
- **OB-6 (AJ-3).** A GFPN_V2_CAP_BYTES environment variable would change the driver's cap without the gp cap
  (pre-existing frozen behaviour; not ordinary operation; not part of the difference).

### 10.5 Interpreter, library and operating-system behaviours relied on

| id | behaviour | provenance | verdict dependence |
|---|---|---|---|
| B-1 | a Python-level signal handler runs at a bytecode boundary, so its exception can surface in the callback's body, entry or epilogue | recalled | H4-a..H4-d only; not CX-1 |
| B-2 | an exception escaping an after-fork parent callback goes to the unraisable hook; os.fork returns | recalled | H4-d, OB-2, OB-5; if it propagated instead: RF-1 undetermined, FAIL; no verdict changes |
| B-3 | stdlib modules register at-fork callbacks | recalled | only that "another callback" exists (H4-d) |
| B-4 | SystemExit(n) exits with n after unwinding; os._exit at once; uncaught KeyboardInterrupt ends by SIGINT | recalled | X1 (hypothetical), FO-1 statuses 1 and -2 |
| B-5 | O_NOATIME prevents atime updates for owner or root | used; every directory's lstat equal before and after | CRG-1 compliance only |
| B-6 | np.savez writes the zip directly to the named file | read: numpy 2.4.6 `numpy/lib/_npyio_impl.py` 756-800, sha256 `557dbdca775fdf05ab660f6694c5d25194634426ddb2a22a7e1706828dc83b82` | AJ-2 (no auxiliary child/ file) |
| B-7 | zipfile writes to the file object given | recalled | supports B-6 |
| B-8 | valgrind writes vgcore.<pid> in the child's cwd on a client crash | recalled | AJ-2 statement (cwd = repository root); a file in solver/ would be a gap and FAIL, not a refusal by design |
| B-9 | msolve (-v 2 -t 1 -f IN -o OUT, -P 1 or -g 1) writes only OUT, stdout, stderr | NOT read or run; observed: no other msolve file among 683 listed files at the gate invocations (p = 4111 and 16777291 fixtures, anchor-identity, controls); transfer to cells and a1 invocations assumed | AJ-2 for msolve outputs |
| B-10 | cysignals sig_on / sig_off turn a signal into a Python exception | read as text: cysignals 1.12.5 `macros.h` 1-40, sha256 `9263a434e966ee6318f7a2bba11f0e77f18c798e9eea721cc8d29424fc9fff30`; compiled parts unread | the RGL-6 residual only |
| B-11 | RH-1 compares recorded path strings with listed paths | rule text (gapattr 246-274) | FC-3 |
| B-12 | GIT_OPTIONAL_LOCKS=0 stops git status refreshing the index | recalled (git documentation) | compliance of post-compaction git children (DV-8) |
| B-13 | audit hooks see import and process-launch events | recalled; exercised by scan.py's self-test and counts | guard evidence only |

## 11. Final checks on the written files

Run on both files after they were assembled, and re-run after the last edit (commands in section 13.4):

- `yaml.safe_load` of `review-report.yaml`: parses (14 top-level keys).
- CRG-7 name self-check (`selfcheck.py`, word list read at run time from `<scratch>/rt_94cc33/words.txt`, sha256
  `c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268`, 16 words). Every scratch script, output and
  generated part reproduced here: 0 hits. First run on the assembled files: 3 hits in each file, namely the name of
  the repository-root project-instructions file (1 per file), the path of the session-configuration directory the
  dispatching session forbade reading (1 per file), and the inference block's prohibition flag (1 per file, the one
  permitted exception). The first two were reworded. Re-run after the last edit: 1 hit per file, the permitted
  prohibition flag only.
- CRG-8: each of the eight identifiers the card forbids as this task's own id occurs 0 times in the two files (grep).
- The literal scratch path occurs 0 times in either file.
- `GIT_OPTIONAL_LOCKS=0 git status --porcelain --untracked-files=all` on the write scope and on
  `experiments/EXP-GFPN-05ff43`: only the two deliverables, untracked; nothing under `experiments/`.
- The sha256 of each deliverable cannot be written into itself; it is stated in the return to the dispatching
  session.

## 12. Red-team report block (agents/red-team.md)

- **id / task_id:** TASK-20260924-94cc33 (no RT id minted).
- **claim_under_review:** gapattr's difference from childend opens no fail-open route and refuses no planned basis
  outcome by design (definitions 604-621, (iv) literally), keeps the development harness feasible on the r3 base, and
  leaves the RFR-4 reads and the carried findings standing.
- **objections:** CX-1 (FAIL-OPEN, lost-record class); FC-1 (RH-6 (i) (19) / (20) cannot pass as worded); OB-1
  ((iv) attributes by directory despite the WHY sentence); FC-4 (dev path fields outside the accepted lists).
- **required_controls:** CX-1's discriminating control (RH-6 (i) (19) / (20) third case, worded vs mutated RH-1);
  FC-2 (use an uncached build child job for (22)); FC-3 (attribute at the recorded root or relative to
  GFPN_RUN_DIR).
- **counterexample_or_mutation:** CX-1; mutation: launch-record count per re-solved tag must equal the event's attempt
  count, unrenamed final files only to the accepted attempt's record.
- **baseline_comparison:** against childend as worded: childend refuses planned basis outcomes by design (PB-2, PB-3;
  16/16/1/11 meta and 4/4/1/7 npz unattributed) and has no CX-1 route; gapattr removes every refusal found (0 gaps over
  683 files) and adds CX-1. Against failclosed: FO-1 was FAIL-OPEN (iv) there, fail-closed here. Pollard rho, BSGS and
  specialized ECDLP baselines do not apply to a protocol review that measures nothing.
- **heuristic_challenges:** B-9 is an untested transfer; B-1..B-3 are recalled and carry no verdict.
- **cost_model_challenges:** FC-1..FC-6 each cost a stop or a spurious FAIL and a Coordinator decision; none costs a
  result.
- **reduction_and_scope_challenges:** the listing check is a reading of r3 artifacts under r4 rule text with
  reconstructed launch sets; X1, X10, X6b stay unshown-absent for compiled extensions, PyYAML and interpreter shutdown
  (RGL-6).
- **proof_architecture_challenges:** RH-1's WHY sentence states a property whose stated exception ("unless another
  record's own positive source names exactly that file") is exactly CX-1 at re-solved tags.
- **narrowest_supported_statement:** on static reading of the frozen code, the r3 base, the drafts and the listings of
  four archived r3 gate packages: under gapattr as worded a package can receive PASS while one launch record of a tag
  re-solved by SE-3 or HR-3 is absent (FAIL-OPEN, (i) and (ii) on the launch-record reading), under a lost-record
  premise for which no ordinary path was found; no planned-basis refusal was found; every file of the four packages'
  five directories is attributed by RH-1; the RFR-4 reads are confirmed; seven fail-closed findings are listed.
  Nothing here concerns D.
- **next_concrete_action:** a check step: evaluate the CX-1 mutation with this report's evaluator objects LR-1..LR-5
  and the RH6_19 loop, with RH-6 (i) (19) / (20) as the discriminating control. No approval is recommended or implied.
- **artifact_paths:** `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.yaml`,
  `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33/review-report.md`.

## 13. Review attestation

- **task_id** TASK-20260924-94cc33; **role** red-team; **joints_owned** AJ-0..AJ-6; **verdicts** AJ-0 holds, AJ-1
  breaks, AJ-2 holds, AJ-3 holds, AJ-4 holds, AJ-5 holds, AJ-6 holds.
- **read_sibling_reports:** none. The archived reviews TASK-20260924-f5631b and TASK-20260924-1ecb7d were read in full
  as inputs; there are no sibling reports in this round.
- **Launched nothing, imported nothing scanned:** no run package or solver-class child; scan.py compiled
  v2_solver.py's TEXT for dis and ran under an audit hook refusing the 256 scanned module names and every launch (0
  and 0 attempts); cypari2, cysignals, flint and numpy were read as text, never imported; PyYAML (not read under AJ-1)
  was imported only to parse the YAML deliverable.

### 13.1 Blindness

**blind_from, not opened:** `ledger/decisions/DEC-20260924-61b22c.yaml`, `ledger/corrections/CORR-20260924-3c831f.yaml`,
`ledger/handoffs/TASK-20260924-c9218d.yaml`, `ledger/handoffs/TASK-20260924-27ea14.yaml`,
`ledger/goals/GOAL-GFPN-380702/goal.yaml`, `ledger/decisions/DEC-20260924-844896.yaml`,
`ledger/corrections/CORR-20260924-862f7d.yaml`, `ledger/handoffs/TASK-20260924-64c8fe.yaml`,
`ledger/handoffs/TASK-20260924-5816cd.yaml`, `knowledge/techniques/KN-TECH-79d6b9.md`,
`ledger/decisions/DEC-20260924-8fa3d4.yaml`, `ledger/corrections/CORR-20260924-7fcbd2.yaml`,
`ledger/handoffs/TASK-20260924-7e9d3e.yaml`, `ledger/handoffs/TASK-20260924-eb2540.yaml`.

**Withheld by the dispatching session, not opened:** `ledger/handoffs/TASK-20260924-93f3ca.yaml`;
`coordination/goals/GOAL-GFPN-380702/batches/`; `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-27ea14/`
(its receipt not opened; the one field was given by the dispatching session);
`coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-5816cd/` and `.../TASK-20260924-eb2540/`;
`coordination/bus/`; `coordination/events/`; every directory under `coordination/goals/*/reviews/` other than
`reviews/TASK-20260924-f5631b/`, `reviews/TASK-20260924-1ecb7d/`, the three released files and this write scope; git
commit messages; pull requests; the web (no search, no fetch).

**Disclosures.**

1. KNOWN IN ADVANCE AND ACCEPTED BY THE CARD: the draft summarizes and cites DEC-20260924-61b22c (header and findings
   carried, lines 1-240; RH-2 (d) 313-318; RH-5 (d) 376-377; 523-531), cites CORR-20260924-3c831f (239-240, 342, 355)
   and DEC-20260924-844896 (524-525). Read as part of the draft; no blind file opened.
2. The archived reviews, the censuses and CORR-20260924-b3cd63 cite earlier decisions and corrections; read as inputs.
3. As retained through the context compaction (DV-1), no repository-wide search was run; every search named files or
   directories outside the withheld set. scan.py listed file NAMES under `tools/` and `harness/` for its guard and
   read no file there.
4. No withheld path was opened by accident.

### 13.2 Paths read

In full: `ledger/handoffs/TASK-20260924-94cc33.yaml`; `agents/red-team.md`; `AGENTS.md`; the gapattr, childend,
failclosed and readbackfull drafts; the four archived review files of TASK-20260924-f5631b and TASK-20260924-1ecb7d;
`implementation-v2/` v2_solver.py, v2_driver.py, v2_child.py, v2_common.py, v2_check_run.py;
`implementation-v2-a1/` a1_check_run.py, a1_driver.py, a1_health.py, a1_pari.py; `implementation-v2-r3/` r3_resolve.py,
r3_run_wrapper.py, r3_entry_v2.py, r3_entry_a1.py, r3_check_run.py; the three released frozen files;
`ledger/corrections/CORR-20260924-b3cd63.yaml`.

In part: readbackclose draft (1-669); readbackcover draft (150-379; whole file hashed); readback-census.md (420-460);
readbackclose-census.md (326-500, 552-700); the other six census files (hashed only); v2_lift.py (200-241);
v2_run_wrapper.py (grep hits 176, 182); a1_run_wrapper.py (grep hits 297, 303); a1_common.py (grep hit 44);
r3_common.py (18-35, 88-100, 104-135); r3_dv7.py (290-318); r3_dv12.py (105-125); r3_reg1.py, r3_devchecks.py,
r3_devchecks_more.py (grep and scan hits); every .py of the three implementation trees (source text parsed by
scan.py); the four trial plans (parsed as JSON: packages, kinds, requires, args, gate); the five snapshot receipts
(path_sha256 field); `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-f1fb0e/` (listed only); the four
gate packages (listings with O_NOATIME; the bytes of 44 spec files and four command.txt files with O_NOATIME,
retaining only spec keys, job, to_cache, out and the GFPN_RUN_DIR line); CORR-20260924-217903 and
CORR-20260924-80009d (lines 1-40); the repository-root project-instructions file (provided to the session as
project instructions; its name is not written here under CRG-7).

Card inputs not read: DEC-20260924-a789e1, DEC-20260924-650068, DEC-20260924-1ce186, DEC-20260924-15a77a (line counts
only); `implementation-v2-r3.md`; the amendments other than the six named.

Outside the repository: `<scratch>/rt_94cc33/` (section 13.3); under `/usr/local/lib/python3.11/dist-packages/`:
`cypari2/` (23 text files by grep; `pari_instance.pyx` sha256
`c1086ca7981c2542a4d175ceb796ff34eb8c471d46190e6f6149b602c28ff83d`; version from `cypari2-2.2.0.dist-info`),
`cysignals/` (8 text files by grep; `macros.h` 1-40; `cysignals-1.12.5.dist-info`), `flint/` (60 .py/.pyi by grep;
`python_flint-0.9.0.dist-info`), `numpy/` (142 non-test .py by grep; `lib/_npyio_impl.py` 756-800;
`numpy-2.4.6.dist-info`), and the names (not bytes) of the compiled `.so` files; one directory under `/root/.local`
(listed once before the compaction, DV-6); system libraries and the interpreter `/usr/local/bin/python3` (3.11.15).
Nothing under the session-configuration directory the dispatching session forbade reading was read.

### 13.3 Scratch files (`<scratch>/rt_94cc33/`, transient, outside the repository)

| file | sha256 | purpose |
|---|---|---|
| words.txt | `c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268` | word list placed by the dispatching session; read at run time by selfcheck.py only |
| integrity.py | `12af6f427041b27ddcdd62c18e154e7a9b7775f0542d234c366c0efaf8795330` | CRG-2 (c) |
| integrity.out | `beefb79963a06053f4c28785afce7ad226e2d2f9a996a29b100d4b1cfcdd8476` | its output |
| listing.py | `2c19faa2a5a877df500dfa47bc81ed60350ed2735baadf11b354ba352599309c` | O_NOATIME listing |
| listing.json | `6942f67518b6effd9dfaaf21a16e08734cdb3241ba1221e61ab4741d5c60274e` | its output |
| specout.py | `1b6662cdb7ad10bd4ca0641d11518ee26e6bf1fbc496f7386c3ac7c8d9ca05cb` | spec out values, GFPN_RUN_DIR lines |
| specout.json | `700d61d3158f797b948ddeda344fe57bd10396046236844af06d2f87054e9b58` | its output |
| scan.py | `7a194f5d49a47f160dcea9cdc464fbc23956feb7d3bc2b5e4968c223ab8d83c9` | ast / dis scan under a guard |
| scan.out | `cde64163b4067793bdd6ce3264592302320b0ac77e5184389e1f33e73d6603fd` | its output |
| rt_eval.v1.py | `fc7dff05472260fecf8a1fa4f6995e8463fcf7e9a92310c71f8aed5ec171f40a` | evaluator v1, never run |
| rt_eval.v2.py | `daab8b7626c768fa0938dff6f1f1ae6bd995523942599f1c366b33bf449fe9b3` | evaluator v2 |
| rt_eval.v2.run1.out | `aa68348d532d6847219dd67774338b221e593695d3ec1feb1fa7a4a7d63fb2ea` | its failed run (TypeError) |
| rt_eval.v3.py | `1f60cdc492e74a280e791bf04c8ab719cd9d2b8ef185251c1151ee17ee8f4dc3` | evaluator v3 |
| rt_eval.v3.out | `4306a8ab201d39ff257499f3e4e512684b1dbee0909a916bdf9d1f409ec31631` | its output |
| rt_eval.v3.json | `fdaa826255e335a2f2565f01afc87d91670a7456a8a44db55e6f415013626c96` | its output |
| rt_eval.py | `662e57565e314186a334173d0c4188acd7162bb21f9bce6196e69b2645ba893e` | final evaluator |
| rt_eval.out | `1c88d680bff71dbcc94039890726928b433bc6e9841df1e821a32900898e1290` | its output |
| rt_eval.json | `cea33e7189aaa172db1d19ecadd084a4bcbfe606ebc2d4631571f3748b02a7ba` | its output |
| selfcheck.py | `434c5a252bacd7c5603c37266db9c9bdb875a687338d09bbcc206eef02c100b8` | CRG-7 self-check |
| tables.py | `7c731da6d2e440eb0660439d7a95032287ca7a65d6a148f85fcc9d6d710653f0` | listing-table parts |
| tables.yaml.part | `35a75dc52d3763258e004e173110fbb066d77a6dca8b23acf226f81620f4df8b` | appended to the YAML |
| tables.md.part | `12f92c2fe954f5c6106e2141b0bac12f2e19be7aa9a02bd697857ce59a1d1f5c` | appended here ("Listing tables" section) |
| appendix.py | `c59102ca35a20b7ef84330120b32f25a643b450ceecad94bef5647340644df8c` | writes the appendix part |
| appendix.md.part | `3f25b7edf3aa3dae1551ce11fc264c1b6f89d3d8031dbda037ea023c4f3d0c69` | appended here (appendix) |

### 13.4 Commands (argv)

Before the context compaction, as retained (DV-1): `python3 -B integrity.py | tee integrity.out`;
`PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B listing.py listing.json`; `PYTHONDONTWRITEBYTECODE=1 timeout 120
python3 -B specout.py listing.json specout.json`; `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan.py
/home/user/crypto-autoresearcher > scan.out`; `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rt_eval.py >
rt_eval.out` (once per run of v2, v3 and the final version; DV-2); `git diff --stat dd1034... -- <CRG-2 (d)
pathspecs, quoted and shell-expanded>`; `git status --porcelain -- experiments/EXP-GFPN-05ff43
coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33`; `git rev-parse HEAD`; `git cat-file -t dd1034...`;
`git merge-base --is-ancestor dd1034... HEAD`; `sha256sum <CRG-2 files>`; read-only reads of the input files (cat,
sed -n, awk, grep, wc, ls, sha256sum), exact argv not retained; one `python3 -S` invocation and one directory listing
under `/root/.local`, exact argv and output not retained (DV-5, DV-6).

After the compaction, exact (cwd the repository unless stated; `<scratch>` abbreviates the scratch directory):

```text
ls -la; sha256sum *                                                               (cwd <scratch>/rt_94cc33)
test -e /home/user/crypto-autoresearcher/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33  (exit 1)
sed -n 1,200p / 200,420p / 420,640p / 640,900p / 900,1141p rt_eval.out           (cwd <scratch>/rt_94cc33)
sed/cat -n/awk numbering of experiments/EXP-GFPN-05ff43/amendments/v2_addendum_gapattr.yaml lines 236-445
awk 'NR>=444 && NR<=540' v2_addendum_gapattr.yaml; wc -l v2_addendum_gapattr.yaml
awk 'NR>=600 && NR<=708' v2_addendum_failclosed.yaml
wc -l ledger/handoffs/TASK-20260924-94cc33.yaml; awk numbering of it, lines 1-200 and 200-496
PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<print keys of rt_eval.json>'  (twice; cwd <scratch>/rt_94cc33)
grep -n '^def \|^# ---\|^class \|^[A-Z_]* = ' rt_eval.py; sed -n 1,37p, 56,246p, 38,55p, 578,680p rt_eval.py
awk 'NR>=220 && NR<=320' implementation-v2-r3/r3_resolve.py
grep -n '^K\b\|^K =\|RENAME_SUFFIX\|SPACING_S =' r3_common.py r3_resolve.py; grep -n 'stdout_path\|launch_records' r3_*.py
awk 'NR>=205 && NR<=306' v2_addendum_readbackfull.yaml
grep -n -i 'attempt record\|number of launch\|count of launch\|each attempt\|one launch record per\|every attempt' <five amendments>
grep -n 'RF-[0-8]_\|RF-[0-8]:' v2_addendum_failclosed.yaml; grep -n 'RG-[0-9]_\|RGL-[0-9]' v2_addendum_childend.yaml
awk 'NR>=372 && NR<=418' v2_addendum_failclosed.yaml; awk 'NR>=416 && NR<=437' v2_addendum_childend.yaml
grep -n 'subprocess\|os\.system\|Popen\|open(\|os\.environ\|sys\.argv\|import \|msolve\|write' k4a_anchor_system.py; wc -l; sha256sum
wc -l <CORR-20260924-b3cd63, -217903, -80009d; DEC-20260924-a789e1, -650068, -1ce186, -15a77a>
read of CORR-20260924-b3cd63.yaml; sed -n 1,40p CORR-20260924-217903.yaml; sed -n 1,40p CORR-20260924-80009d.yaml
awk 'NR>=118 && NR<=160' and 'NR>=645 && NR<=676' implementation-v2/v2_driver.py
awk 'NR>=419 && NR<=483' v2_addendum_failclosed.yaml; awk 'NR>=373 && NR<=415' v2_addendum_childend.yaml
PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<summarize specout.json>'; awk 'NR>=88 && NR<=108' v2_driver.py
ls experiments/EXP-GFPN-05ff43/dev-evidence; awk 'NR>=472 && NR<=494' readbackclose-census.md
awk 'NR>=280 && NR<=371' v2_addendum_failclosed.yaml
awk 'NR>=505 && NR<=556' v2_solver.py; awk 'NR>=195 && NR<=214' v2_driver.py
grep -n 'chdir\|cwd' implementation-v2/*.py implementation-v2-a1/*.py implementation-v2-r3/*.py
grep -n 'build_poly(\|raw_grid(\|child_job(' v2_driver.py a1_driver.py implementation-v2-r3/*.py
awk 'NR>=158 && NR<=194' v2_driver.py; awk 'NR>=366 && NR<=410' r3_resolve.py
grep -n 'run_child\|\.ms\.log\|def run_system\|def run(' a1_health.py; grep -n '<labels>' <scratch>/rt_94cc33/rt_eval.py
cat scan.out                                                                      (cwd <scratch>/rt_94cc33)
awk 'NR>=52 && NR<=64' v2_common.py; awk 'NR>=86 && NR<=124' a1_pari.py; awk 140-152 and 245-253 a1_health.py
awk 'NR>=223 && NR<=246' a1_health.py; grep -n 'reinvoke_on_fail\|H.run(\|a1_health.run\|health.run(' a1/*.py r3/*.py
awk 'NR>=55 && NR<=84' r3_entry_v2.py; awk 'NR>=88 && NR<=115' r3_entry_a1.py
grep -n '\bsh(\|C\.sh\|AC\.sh\|other_solver_processes\|gp_version()' <v2, a1 .py; r3_entry_v2, r3_entry_a1, r3_resolve, r3_common>
grep -n 'except\|finally\|def main\|def finish\|environment(\|C\.env' v2_driver.py; grep -n 'def environment\|def msolve_version\|^def ' v2_common.py
awk 'NR>=74 && NR<=86' a1_check_run.py; awk 186-198 and 284-292 r3_run_wrapper.py
grep -n '2c4862\|RUNS_DIR\|^RUNS\b\|^RUNS =' a1_check_run.py a1_common.py r3_run_wrapper.py r3_common.py
grep -n 'def _raw' -A 10 r3_run_wrapper.py; PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<print gate.addendum_blocking_package of trial-plan-v2-a1-r3.json>'
awk 433-442, 464, 544-551 r3_run_wrapper.py; awk 250-257, 322-335 r3_check_run.py; awk 116-121 r3_dv12.py
grep -n 'red_team_report' -A 40 agents/red-team.md
ls -d cypari2* cysignals* flint* python_flint* numpy*; find <pkg> -type f (text types) | wc -l      (cwd /usr/local/lib/python3.11/dist-packages)
find cypari2 cysignals flint -type f (text types) -print0 | xargs -0 grep -n -E '<exit|abort|exec|spawn|fork|at-fork|atexit|system|subprocess|kill|raise_signal>'
find cypari2 cysignals -type f (text types) | sort; find cypari2 cysignals flint -name '*.so' | sort; sha256sum cypari2/pari_instance.pyx cysignals/macros.h numpy/lib/_npyio_impl.py
find numpy -name '*.py' (excluding tests, f2py, testing, _pyinstaller, typing, distutils) | wc -l; the same | xargs grep -n -E '<same pattern set>'
PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B selfcheck.py <scratch scripts and outputs; later the parts; finally the deliverables>
PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables.py; PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<yaml.safe_load(tables.yaml.part)>'
grep -c '````' <scratch scripts and outputs>; PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B appendix.py; wc -c <parts>; sha256sum <new scratch files>
GIT_OPTIONAL_LOCKS=0 git rev-parse HEAD
GIT_OPTIONAL_LOCKS=0 git cat-file -t dd103455380238ec2f20d17414de687acdcc822a
GIT_OPTIONAL_LOCKS=0 git merge-base --is-ancestor dd103455380238ec2f20d17414de687acdcc822a HEAD
GIT_OPTIONAL_LOCKS=0 git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json' experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f6a21a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-902222 experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-f5412a experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956
GIT_OPTIONAL_LOCKS=0 git diff --stat <the same, globs shell-expanded>
GIT_OPTIONAL_LOCKS=0 git status --porcelain --untracked-files=all -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33
sha256sum <six amendments, four review files, nine census files, three released files>; awk 'NR>=160 && NR<=168' v2_addendum_gapattr.yaml; cat <scratch>/rt_94cc33/integrity.out
test -e <write scope> (exit 1); mkdir -p coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-94cc33; ls -la of it
writes of the two deliverables; printf '<comment header>' >> review-report.yaml; cat <scratch>/rt_94cc33/tables.yaml.part >> review-report.yaml
PYTHONDONTWRITEBYTECODE=1 python3 -B -c '<yaml.safe_load(review-report.yaml)>'  (before and after the append)
sed -i 's/Full per-file table in section 14\./.../; s/Table in section 14\./.../; s/full per-file table in section 14):/.../; s/appended here (section 14)/.../' review-report.md   (four reference rewrites)
cat <scratch>/rt_94cc33/tables.md.part <scratch>/rt_94cc33/appendix.md.part >> review-report.md
edits of both files with the file-edit tool (DV-12 text; this command list; section 11 results)
final checks (section 11): yaml.safe_load; selfcheck.py on both files; grep -c of the eight CRG-8 identifiers; sha256sum; GIT_OPTIONAL_LOCKS=0 git status --porcelain --untracked-files=all on the write scope and experiments/EXP-GFPN-05ff43
```

### 13.5 Inference

```yaml
requested_policy: review-adversarial
agent_binding: red-team, at the policy's default reasoning effort, as the dispatching session arranged
resolved_model_id: null        # none supplied by the dispatching session; none invented
model_verified: false
fallback_used: false
bedrock_used: false
```

### 13.6 Deviations

- **DV-1.** The working context was compacted once. The earlier transcript lies under a path the dispatching session
  forbids reading and was not consulted. Pre-compaction paths and commands are compiled from the retained summary;
  exact argv of individual pre-compaction read-only shell reads were not retained and are listed by form. Every
  post-compaction command is listed exactly. Every cited line was re-read after the compaction or is in a scratch
  output reproduced verbatim.
- **DV-2.** Four evaluator versions (v1 never run; v2 one run, TypeError; v3 one run, superseded; final). Every
  superseded version and output is kept under a version-suffixed name; no output was overwritten, as retained. The
  argv of superseded runs is known only in the listed form; the commands that gave the files their suffixed names were
  not retained.
- **DV-3.** The CRG-2 (a) value came from the dispatching session's message; the receipt was not opened.
- **DV-4.** Listings and spec / command.txt reads used O_NOATIME; every directory's lstat was unchanged.
- **DV-5.** One `python3 -S` invocation before the compaction, while locating the third-party source text; exact argv
  and output not retained. No other claim is made about it.
- **DV-6.** One directory listing under `/root/.local` before the compaction, outside the three permitted classes of
  outside reads, while locating installed third-party modules; exact argv and output not retained.
- **DV-7.** specout.py read the full bytes of the 44 spec files and four command.txt files (O_NOATIME), retaining only
  the spec keys, job, to_cache, out and the GFPN_RUN_DIR line.
- **DV-8.** Whether the pre-compaction git status set GIT_OPTIONAL_LOCKS=0 was not retained; without it git status may
  refresh the index's stat cache (an optional-lock write to `.git/index`; no tracked content, ref or object changes).
  Every post-compaction git child set it.
- **DV-9.** Card inputs not read: DEC-20260924-a789e1, -650068, -1ce186, -15a77a (line counts only),
  `implementation-v2-r3.md`, the other amendments; CORR-20260924-217903 and -80009d lines 1-40 only. No verdict relies
  on them.
- **DV-10.** The evaluator tags any FAIL of a designed planned package as a planned-basis refusal; REL-1 (FC-3)
  carries that tag; this report classifies it fail-closed (production checks run at the recorded root).
- **DV-11.** The listing tables and the appendix were generated by scratch scripts (tables.py, appendix.py) and
  appended to hand-written bodies. After appending, one phrase of the appended tables text in this md was corrected
  ("the rule is stated in section 3" to "section 2", where the Method section actually states it), so this md's
  "Listing tables" section differs from `tables.md.part` in that one character; every table row is unchanged.
- **DV-12.** The write-scope directory was created (`mkdir -p`); it holds only the two deliverables. One in-place
  edit of this md by `sed -i` (replacing four "section 14" references) wrote sed's transient temporary file in the
  same directory and renamed it over the md; no other file remains there.

## Listing tables (every file of the five directories of the four archived r3 gate packages)

Launch sets are RECONSTRUCTED (CRG-9); the rule is stated in section 2 and in the YAML `listing_tables.reconstruction_rule`. Each cell names the clause and the reconstructed record that attributes the file, every clause that applies, in record order. `NONE (recorder gap)` means no clause attributes it and it is not on the non-launch list. These are readings of r3 artifacts under r4 rule text, never results about any package's verdict and never evidence about D.

### RUN-GFPN-f6a21a: 284 files in the five directories, 88 reconstructed launch records

- childend RG-4 (b) as worded: first-clause counts NONE (gap) 20, argv exact 88, stdout/stderr 176; unattributed 20.
- gapattr RH-1 as worded: first-clause counts (i) 176, (ii) 88, (v) 20; unattributed 0.

| # | file | childend RG-4 (b) as worded | gapattr RH-1 as worded |
|---|---|---|---|
| 1 | `child/fixture_S3.meta.json` | NONE (recorder gap) | (v) childjob:fixture_S3 |
| 2 | `child/fixture_S3.npz` | NONE (recorder gap) | (v) childjob:fixture_S3 |
| 3 | `child/fixture_S3.spec.json` | argv exact childjob:fixture_S3 | (ii) childjob:fixture_S3 |
| 4 | `child/fixture_S3.stderr` | stdout/stderr childjob:fixture_S3 | (i) childjob:fixture_S3 |
| 5 | `child/fixture_S3.stdout` | stdout/stderr childjob:fixture_S3 | (i) childjob:fixture_S3 |
| 6 | `child/fixture_S3_rescaled.meta.json` | NONE (recorder gap) | (v) childjob:fixture_S3_rescaled |
| 7 | `child/fixture_S3_rescaled.npz` | NONE (recorder gap) | (v) childjob:fixture_S3_rescaled |
| 8 | `child/fixture_S3_rescaled.spec.json` | argv exact childjob:fixture_S3_rescaled | (ii) childjob:fixture_S3_rescaled |
| 9 | `child/fixture_S3_rescaled.stderr` | stdout/stderr childjob:fixture_S3_rescaled | (i) childjob:fixture_S3_rescaled |
| 10 | `child/fixture_S3_rescaled.stdout` | stdout/stderr childjob:fixture_S3_rescaled | (i) childjob:fixture_S3_rescaled |
| 11 | `child/fixture_torsion_S3_norm.meta.json` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_norm |
| 12 | `child/fixture_torsion_S3_norm.npz` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_norm |
| 13 | `child/fixture_torsion_S3_norm.spec.json` | argv exact childjob:fixture_torsion_S3_norm | (ii) childjob:fixture_torsion_S3_norm |
| 14 | `child/fixture_torsion_S3_norm.stderr` | stdout/stderr childjob:fixture_torsion_S3_norm | (i) childjob:fixture_torsion_S3_norm |
| 15 | `child/fixture_torsion_S3_norm.stdout` | stdout/stderr childjob:fixture_torsion_S3_norm | (i) childjob:fixture_torsion_S3_norm |
| 16 | `child/fixture_torsion_S3_rq.meta.json` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_rq |
| 17 | `child/fixture_torsion_S3_rq.npz` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_rq |
| 18 | `child/fixture_torsion_S3_rq.spec.json` | argv exact childjob:fixture_torsion_S3_rq | (ii) childjob:fixture_torsion_S3_rq |
| 19 | `child/fixture_torsion_S3_rq.stderr` | stdout/stderr childjob:fixture_torsion_S3_rq | (i) childjob:fixture_torsion_S3_rq |
| 20 | `child/fixture_torsion_S3_rq.stdout` | stdout/stderr childjob:fixture_torsion_S3_rq | (i) childjob:fixture_torsion_S3_rq |
| 21 | `child/fx_fresh1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh1_raw_u |
| 22 | `child/fx_fresh1_raw_u.spec.json` | argv exact childjob:fx_fresh1_raw_u | (ii) childjob:fx_fresh1_raw_u |
| 23 | `child/fx_fresh1_raw_u.stderr` | stdout/stderr childjob:fx_fresh1_raw_u | (i) childjob:fx_fresh1_raw_u |
| 24 | `child/fx_fresh1_raw_u.stdout` | stdout/stderr childjob:fx_fresh1_raw_u | (i) childjob:fx_fresh1_raw_u |
| 25 | `child/fx_fresh1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh1_raw_x |
| 26 | `child/fx_fresh1_raw_x.spec.json` | argv exact childjob:fx_fresh1_raw_x | (ii) childjob:fx_fresh1_raw_x |
| 27 | `child/fx_fresh1_raw_x.stderr` | stdout/stderr childjob:fx_fresh1_raw_x | (i) childjob:fx_fresh1_raw_x |
| 28 | `child/fx_fresh1_raw_x.stdout` | stdout/stderr childjob:fx_fresh1_raw_x | (i) childjob:fx_fresh1_raw_x |
| 29 | `child/fx_fresh2_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh2_raw_u |
| 30 | `child/fx_fresh2_raw_u.spec.json` | argv exact childjob:fx_fresh2_raw_u | (ii) childjob:fx_fresh2_raw_u |
| 31 | `child/fx_fresh2_raw_u.stderr` | stdout/stderr childjob:fx_fresh2_raw_u | (i) childjob:fx_fresh2_raw_u |
| 32 | `child/fx_fresh2_raw_u.stdout` | stdout/stderr childjob:fx_fresh2_raw_u | (i) childjob:fx_fresh2_raw_u |
| 33 | `child/fx_fresh2_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh2_raw_x |
| 34 | `child/fx_fresh2_raw_x.spec.json` | argv exact childjob:fx_fresh2_raw_x | (ii) childjob:fx_fresh2_raw_x |
| 35 | `child/fx_fresh2_raw_x.stderr` | stdout/stderr childjob:fx_fresh2_raw_x | (i) childjob:fx_fresh2_raw_x |
| 36 | `child/fx_fresh2_raw_x.stdout` | stdout/stderr childjob:fx_fresh2_raw_x | (i) childjob:fx_fresh2_raw_x |
| 37 | `child/fx_planted0_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted0_raw_u |
| 38 | `child/fx_planted0_raw_u.spec.json` | argv exact childjob:fx_planted0_raw_u | (ii) childjob:fx_planted0_raw_u |
| 39 | `child/fx_planted0_raw_u.stderr` | stdout/stderr childjob:fx_planted0_raw_u | (i) childjob:fx_planted0_raw_u |
| 40 | `child/fx_planted0_raw_u.stdout` | stdout/stderr childjob:fx_planted0_raw_u | (i) childjob:fx_planted0_raw_u |
| 41 | `child/fx_planted0_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted0_raw_x |
| 42 | `child/fx_planted0_raw_x.spec.json` | argv exact childjob:fx_planted0_raw_x | (ii) childjob:fx_planted0_raw_x |
| 43 | `child/fx_planted0_raw_x.stderr` | stdout/stderr childjob:fx_planted0_raw_x | (i) childjob:fx_planted0_raw_x |
| 44 | `child/fx_planted0_raw_x.stdout` | stdout/stderr childjob:fx_planted0_raw_x | (i) childjob:fx_planted0_raw_x |
| 45 | `child/fx_planted1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted1_raw_u |
| 46 | `child/fx_planted1_raw_u.spec.json` | argv exact childjob:fx_planted1_raw_u | (ii) childjob:fx_planted1_raw_u |
| 47 | `child/fx_planted1_raw_u.stderr` | stdout/stderr childjob:fx_planted1_raw_u | (i) childjob:fx_planted1_raw_u |
| 48 | `child/fx_planted1_raw_u.stdout` | stdout/stderr childjob:fx_planted1_raw_u | (i) childjob:fx_planted1_raw_u |
| 49 | `child/fx_planted1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted1_raw_x |
| 50 | `child/fx_planted1_raw_x.spec.json` | argv exact childjob:fx_planted1_raw_x | (ii) childjob:fx_planted1_raw_x |
| 51 | `child/fx_planted1_raw_x.stderr` | stdout/stderr childjob:fx_planted1_raw_x | (i) childjob:fx_planted1_raw_x |
| 52 | `child/fx_planted1_raw_x.stdout` | stdout/stderr childjob:fx_planted1_raw_x | (i) childjob:fx_planted1_raw_x |
| 53 | `child/fx_reg0_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg0_raw_u |
| 54 | `child/fx_reg0_raw_u.spec.json` | argv exact childjob:fx_reg0_raw_u | (ii) childjob:fx_reg0_raw_u |
| 55 | `child/fx_reg0_raw_u.stderr` | stdout/stderr childjob:fx_reg0_raw_u | (i) childjob:fx_reg0_raw_u |
| 56 | `child/fx_reg0_raw_u.stdout` | stdout/stderr childjob:fx_reg0_raw_u | (i) childjob:fx_reg0_raw_u |
| 57 | `child/fx_reg0_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg0_raw_x |
| 58 | `child/fx_reg0_raw_x.spec.json` | argv exact childjob:fx_reg0_raw_x | (ii) childjob:fx_reg0_raw_x |
| 59 | `child/fx_reg0_raw_x.stderr` | stdout/stderr childjob:fx_reg0_raw_x | (i) childjob:fx_reg0_raw_x |
| 60 | `child/fx_reg0_raw_x.stdout` | stdout/stderr childjob:fx_reg0_raw_x | (i) childjob:fx_reg0_raw_x |
| 61 | `child/fx_reg1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg1_raw_u |
| 62 | `child/fx_reg1_raw_u.spec.json` | argv exact childjob:fx_reg1_raw_u | (ii) childjob:fx_reg1_raw_u |
| 63 | `child/fx_reg1_raw_u.stderr` | stdout/stderr childjob:fx_reg1_raw_u | (i) childjob:fx_reg1_raw_u |
| 64 | `child/fx_reg1_raw_u.stdout` | stdout/stderr childjob:fx_reg1_raw_u | (i) childjob:fx_reg1_raw_u |
| 65 | `child/fx_reg1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg1_raw_x |
| 66 | `child/fx_reg1_raw_x.spec.json` | argv exact childjob:fx_reg1_raw_x | (ii) childjob:fx_reg1_raw_x |
| 67 | `child/fx_reg1_raw_x.stderr` | stdout/stderr childjob:fx_reg1_raw_x | (i) childjob:fx_reg1_raw_x |
| 68 | `child/fx_reg1_raw_x.stdout` | stdout/stderr childjob:fx_reg1_raw_x | (i) childjob:fx_reg1_raw_x |
| 69 | `solver/fx_fresh1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_S3 | (i) callgrind:fx_fresh1_S3 |
| 70 | `solver/fx_fresh1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_S3 | (i) callgrind:fx_fresh1_S3 |
| 71 | `solver/fx_fresh1_S3.ms` | argv exact callgrind:fx_fresh1_S3; argv exact msolve:solver/fx_fresh1_S3 | (ii) callgrind:fx_fresh1_S3; (ii) msolve:solver/fx_fresh1_S3 |
| 72 | `solver/fx_fresh1_S3.ms.err` | stdout/stderr msolve:solver/fx_fresh1_S3 | (i) msolve:solver/fx_fresh1_S3 |
| 73 | `solver/fx_fresh1_S3.ms.log` | stdout/stderr msolve:solver/fx_fresh1_S3 | (i) msolve:solver/fx_fresh1_S3 |
| 74 | `solver/fx_fresh1_S3.ms.out` | argv exact msolve:solver/fx_fresh1_S3 | (ii) msolve:solver/fx_fresh1_S3 |
| 75 | `solver/fx_fresh1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_S3_rescaled | (i) callgrind:fx_fresh1_S3_rescaled |
| 76 | `solver/fx_fresh1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_S3_rescaled | (i) callgrind:fx_fresh1_S3_rescaled |
| 77 | `solver/fx_fresh1_S3_rescaled.ms` | argv exact callgrind:fx_fresh1_S3_rescaled; argv exact msolve:solver/fx_fresh1_S3_rescaled | (ii) callgrind:fx_fresh1_S3_rescaled; (ii) msolve:solver/fx_fresh1_S3_rescaled |
| 78 | `solver/fx_fresh1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_fresh1_S3_rescaled | (i) msolve:solver/fx_fresh1_S3_rescaled |
| 79 | `solver/fx_fresh1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_fresh1_S3_rescaled | (i) msolve:solver/fx_fresh1_S3_rescaled |
| 80 | `solver/fx_fresh1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_fresh1_S3_rescaled | (ii) msolve:solver/fx_fresh1_S3_rescaled |
| 81 | `solver/fx_fresh1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_raw_u | (i) callgrind:fx_fresh1_raw_u |
| 82 | `solver/fx_fresh1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_raw_u | (i) callgrind:fx_fresh1_raw_u |
| 83 | `solver/fx_fresh1_raw_u.ms` | argv exact callgrind:fx_fresh1_raw_u; argv exact msolve:solver/fx_fresh1_raw_u | (ii) callgrind:fx_fresh1_raw_u; (ii) msolve:solver/fx_fresh1_raw_u |
| 84 | `solver/fx_fresh1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_fresh1_raw_u | (i) msolve:solver/fx_fresh1_raw_u |
| 85 | `solver/fx_fresh1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_fresh1_raw_u | (i) msolve:solver/fx_fresh1_raw_u |
| 86 | `solver/fx_fresh1_raw_u.ms.out` | argv exact msolve:solver/fx_fresh1_raw_u | (ii) msolve:solver/fx_fresh1_raw_u |
| 87 | `solver/fx_fresh1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_raw_x | (i) callgrind:fx_fresh1_raw_x |
| 88 | `solver/fx_fresh1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_raw_x | (i) callgrind:fx_fresh1_raw_x |
| 89 | `solver/fx_fresh1_raw_x.ms` | argv exact callgrind:fx_fresh1_raw_x; argv exact msolve:solver/fx_fresh1_raw_x | (ii) callgrind:fx_fresh1_raw_x; (ii) msolve:solver/fx_fresh1_raw_x |
| 90 | `solver/fx_fresh1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_fresh1_raw_x | (i) msolve:solver/fx_fresh1_raw_x |
| 91 | `solver/fx_fresh1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_fresh1_raw_x | (i) msolve:solver/fx_fresh1_raw_x |
| 92 | `solver/fx_fresh1_raw_x.ms.out` | argv exact msolve:solver/fx_fresh1_raw_x | (ii) msolve:solver/fx_fresh1_raw_x |
| 93 | `solver/fx_fresh1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_torsion_S3_norm | (i) callgrind:fx_fresh1_torsion_S3_norm |
| 94 | `solver/fx_fresh1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_torsion_S3_norm | (i) callgrind:fx_fresh1_torsion_S3_norm |
| 95 | `solver/fx_fresh1_torsion_S3_norm.ms` | argv exact callgrind:fx_fresh1_torsion_S3_norm; argv exact msolve:solver/fx_fresh1_torsion_S3_norm | (ii) callgrind:fx_fresh1_torsion_S3_norm; (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| 96 | `solver/fx_fresh1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_norm | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| 97 | `solver/fx_fresh1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_norm | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| 98 | `solver/fx_fresh1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_fresh1_torsion_S3_norm | (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| 99 | `solver/fx_fresh1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_torsion_S3_rq | (i) callgrind:fx_fresh1_torsion_S3_rq |
| 100 | `solver/fx_fresh1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_torsion_S3_rq | (i) callgrind:fx_fresh1_torsion_S3_rq |
| 101 | `solver/fx_fresh1_torsion_S3_rq.ms` | argv exact callgrind:fx_fresh1_torsion_S3_rq; argv exact msolve:solver/fx_fresh1_torsion_S3_rq | (ii) callgrind:fx_fresh1_torsion_S3_rq; (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| 102 | `solver/fx_fresh1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_rq | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| 103 | `solver/fx_fresh1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_rq | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| 104 | `solver/fx_fresh1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_fresh1_torsion_S3_rq | (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| 105 | `solver/fx_fresh2_S3.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_S3 | (i) callgrind:fx_fresh2_S3 |
| 106 | `solver/fx_fresh2_S3.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_S3 | (i) callgrind:fx_fresh2_S3 |
| 107 | `solver/fx_fresh2_S3.ms` | argv exact callgrind:fx_fresh2_S3; argv exact msolve:solver/fx_fresh2_S3 | (ii) callgrind:fx_fresh2_S3; (ii) msolve:solver/fx_fresh2_S3 |
| 108 | `solver/fx_fresh2_S3.ms.err` | stdout/stderr msolve:solver/fx_fresh2_S3 | (i) msolve:solver/fx_fresh2_S3 |
| 109 | `solver/fx_fresh2_S3.ms.log` | stdout/stderr msolve:solver/fx_fresh2_S3 | (i) msolve:solver/fx_fresh2_S3 |
| 110 | `solver/fx_fresh2_S3.ms.out` | argv exact msolve:solver/fx_fresh2_S3 | (ii) msolve:solver/fx_fresh2_S3 |
| 111 | `solver/fx_fresh2_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_S3_rescaled | (i) callgrind:fx_fresh2_S3_rescaled |
| 112 | `solver/fx_fresh2_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_S3_rescaled | (i) callgrind:fx_fresh2_S3_rescaled |
| 113 | `solver/fx_fresh2_S3_rescaled.ms` | argv exact callgrind:fx_fresh2_S3_rescaled; argv exact msolve:solver/fx_fresh2_S3_rescaled | (ii) callgrind:fx_fresh2_S3_rescaled; (ii) msolve:solver/fx_fresh2_S3_rescaled |
| 114 | `solver/fx_fresh2_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_fresh2_S3_rescaled | (i) msolve:solver/fx_fresh2_S3_rescaled |
| 115 | `solver/fx_fresh2_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_fresh2_S3_rescaled | (i) msolve:solver/fx_fresh2_S3_rescaled |
| 116 | `solver/fx_fresh2_S3_rescaled.ms.out` | argv exact msolve:solver/fx_fresh2_S3_rescaled | (ii) msolve:solver/fx_fresh2_S3_rescaled |
| 117 | `solver/fx_fresh2_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_raw_u | (i) callgrind:fx_fresh2_raw_u |
| 118 | `solver/fx_fresh2_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_raw_u | (i) callgrind:fx_fresh2_raw_u |
| 119 | `solver/fx_fresh2_raw_u.ms` | argv exact callgrind:fx_fresh2_raw_u; argv exact msolve:solver/fx_fresh2_raw_u | (ii) callgrind:fx_fresh2_raw_u; (ii) msolve:solver/fx_fresh2_raw_u |
| 120 | `solver/fx_fresh2_raw_u.ms.err` | stdout/stderr msolve:solver/fx_fresh2_raw_u | (i) msolve:solver/fx_fresh2_raw_u |
| 121 | `solver/fx_fresh2_raw_u.ms.log` | stdout/stderr msolve:solver/fx_fresh2_raw_u | (i) msolve:solver/fx_fresh2_raw_u |
| 122 | `solver/fx_fresh2_raw_u.ms.out` | argv exact msolve:solver/fx_fresh2_raw_u | (ii) msolve:solver/fx_fresh2_raw_u |
| 123 | `solver/fx_fresh2_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_raw_x | (i) callgrind:fx_fresh2_raw_x |
| 124 | `solver/fx_fresh2_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_raw_x | (i) callgrind:fx_fresh2_raw_x |
| 125 | `solver/fx_fresh2_raw_x.ms` | argv exact callgrind:fx_fresh2_raw_x; argv exact msolve:solver/fx_fresh2_raw_x | (ii) callgrind:fx_fresh2_raw_x; (ii) msolve:solver/fx_fresh2_raw_x |
| 126 | `solver/fx_fresh2_raw_x.ms.err` | stdout/stderr msolve:solver/fx_fresh2_raw_x | (i) msolve:solver/fx_fresh2_raw_x |
| 127 | `solver/fx_fresh2_raw_x.ms.log` | stdout/stderr msolve:solver/fx_fresh2_raw_x | (i) msolve:solver/fx_fresh2_raw_x |
| 128 | `solver/fx_fresh2_raw_x.ms.out` | argv exact msolve:solver/fx_fresh2_raw_x | (ii) msolve:solver/fx_fresh2_raw_x |
| 129 | `solver/fx_fresh2_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_torsion_S3_norm | (i) callgrind:fx_fresh2_torsion_S3_norm |
| 130 | `solver/fx_fresh2_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_torsion_S3_norm | (i) callgrind:fx_fresh2_torsion_S3_norm |
| 131 | `solver/fx_fresh2_torsion_S3_norm.ms` | argv exact callgrind:fx_fresh2_torsion_S3_norm; argv exact msolve:solver/fx_fresh2_torsion_S3_norm | (ii) callgrind:fx_fresh2_torsion_S3_norm; (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| 132 | `solver/fx_fresh2_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_norm | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| 133 | `solver/fx_fresh2_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_norm | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| 134 | `solver/fx_fresh2_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_fresh2_torsion_S3_norm | (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| 135 | `solver/fx_fresh2_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_torsion_S3_rq | (i) callgrind:fx_fresh2_torsion_S3_rq |
| 136 | `solver/fx_fresh2_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_torsion_S3_rq | (i) callgrind:fx_fresh2_torsion_S3_rq |
| 137 | `solver/fx_fresh2_torsion_S3_rq.ms` | argv exact callgrind:fx_fresh2_torsion_S3_rq; argv exact msolve:solver/fx_fresh2_torsion_S3_rq | (ii) callgrind:fx_fresh2_torsion_S3_rq; (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| 138 | `solver/fx_fresh2_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_rq | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| 139 | `solver/fx_fresh2_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_rq | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| 140 | `solver/fx_fresh2_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_fresh2_torsion_S3_rq | (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| 141 | `solver/fx_planted0_S3.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_S3 | (i) callgrind:fx_planted0_S3 |
| 142 | `solver/fx_planted0_S3.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_S3 | (i) callgrind:fx_planted0_S3 |
| 143 | `solver/fx_planted0_S3.ms` | argv exact callgrind:fx_planted0_S3; argv exact msolve:solver/fx_planted0_S3 | (ii) callgrind:fx_planted0_S3; (ii) msolve:solver/fx_planted0_S3 |
| 144 | `solver/fx_planted0_S3.ms.err` | stdout/stderr msolve:solver/fx_planted0_S3 | (i) msolve:solver/fx_planted0_S3 |
| 145 | `solver/fx_planted0_S3.ms.log` | stdout/stderr msolve:solver/fx_planted0_S3 | (i) msolve:solver/fx_planted0_S3 |
| 146 | `solver/fx_planted0_S3.ms.out` | argv exact msolve:solver/fx_planted0_S3 | (ii) msolve:solver/fx_planted0_S3 |
| 147 | `solver/fx_planted0_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_S3_rescaled | (i) callgrind:fx_planted0_S3_rescaled |
| 148 | `solver/fx_planted0_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_S3_rescaled | (i) callgrind:fx_planted0_S3_rescaled |
| 149 | `solver/fx_planted0_S3_rescaled.ms` | argv exact callgrind:fx_planted0_S3_rescaled; argv exact msolve:solver/fx_planted0_S3_rescaled | (ii) callgrind:fx_planted0_S3_rescaled; (ii) msolve:solver/fx_planted0_S3_rescaled |
| 150 | `solver/fx_planted0_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_planted0_S3_rescaled | (i) msolve:solver/fx_planted0_S3_rescaled |
| 151 | `solver/fx_planted0_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_planted0_S3_rescaled | (i) msolve:solver/fx_planted0_S3_rescaled |
| 152 | `solver/fx_planted0_S3_rescaled.ms.out` | argv exact msolve:solver/fx_planted0_S3_rescaled | (ii) msolve:solver/fx_planted0_S3_rescaled |
| 153 | `solver/fx_planted0_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_raw_u | (i) callgrind:fx_planted0_raw_u |
| 154 | `solver/fx_planted0_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_raw_u | (i) callgrind:fx_planted0_raw_u |
| 155 | `solver/fx_planted0_raw_u.ms` | argv exact callgrind:fx_planted0_raw_u; argv exact msolve:solver/fx_planted0_raw_u | (ii) callgrind:fx_planted0_raw_u; (ii) msolve:solver/fx_planted0_raw_u |
| 156 | `solver/fx_planted0_raw_u.ms.err` | stdout/stderr msolve:solver/fx_planted0_raw_u | (i) msolve:solver/fx_planted0_raw_u |
| 157 | `solver/fx_planted0_raw_u.ms.log` | stdout/stderr msolve:solver/fx_planted0_raw_u | (i) msolve:solver/fx_planted0_raw_u |
| 158 | `solver/fx_planted0_raw_u.ms.out` | argv exact msolve:solver/fx_planted0_raw_u | (ii) msolve:solver/fx_planted0_raw_u |
| 159 | `solver/fx_planted0_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_raw_x | (i) callgrind:fx_planted0_raw_x |
| 160 | `solver/fx_planted0_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_raw_x | (i) callgrind:fx_planted0_raw_x |
| 161 | `solver/fx_planted0_raw_x.ms` | argv exact callgrind:fx_planted0_raw_x; argv exact msolve:solver/fx_planted0_raw_x | (ii) callgrind:fx_planted0_raw_x; (ii) msolve:solver/fx_planted0_raw_x |
| 162 | `solver/fx_planted0_raw_x.ms.err` | stdout/stderr msolve:solver/fx_planted0_raw_x | (i) msolve:solver/fx_planted0_raw_x |
| 163 | `solver/fx_planted0_raw_x.ms.log` | stdout/stderr msolve:solver/fx_planted0_raw_x | (i) msolve:solver/fx_planted0_raw_x |
| 164 | `solver/fx_planted0_raw_x.ms.out` | argv exact msolve:solver/fx_planted0_raw_x | (ii) msolve:solver/fx_planted0_raw_x |
| 165 | `solver/fx_planted0_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_torsion_S3_norm | (i) callgrind:fx_planted0_torsion_S3_norm |
| 166 | `solver/fx_planted0_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_torsion_S3_norm | (i) callgrind:fx_planted0_torsion_S3_norm |
| 167 | `solver/fx_planted0_torsion_S3_norm.ms` | argv exact callgrind:fx_planted0_torsion_S3_norm; argv exact msolve:solver/fx_planted0_torsion_S3_norm | (ii) callgrind:fx_planted0_torsion_S3_norm; (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| 168 | `solver/fx_planted0_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_norm | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| 169 | `solver/fx_planted0_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_norm | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| 170 | `solver/fx_planted0_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_planted0_torsion_S3_norm | (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| 171 | `solver/fx_planted0_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_torsion_S3_rq | (i) callgrind:fx_planted0_torsion_S3_rq |
| 172 | `solver/fx_planted0_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_torsion_S3_rq | (i) callgrind:fx_planted0_torsion_S3_rq |
| 173 | `solver/fx_planted0_torsion_S3_rq.ms` | argv exact callgrind:fx_planted0_torsion_S3_rq; argv exact msolve:solver/fx_planted0_torsion_S3_rq | (ii) callgrind:fx_planted0_torsion_S3_rq; (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| 174 | `solver/fx_planted0_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_rq | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| 175 | `solver/fx_planted0_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_rq | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| 176 | `solver/fx_planted0_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_planted0_torsion_S3_rq | (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| 177 | `solver/fx_planted1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_S3 | (i) callgrind:fx_planted1_S3 |
| 178 | `solver/fx_planted1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_S3 | (i) callgrind:fx_planted1_S3 |
| 179 | `solver/fx_planted1_S3.ms` | argv exact callgrind:fx_planted1_S3; argv exact msolve:solver/fx_planted1_S3 | (ii) callgrind:fx_planted1_S3; (ii) msolve:solver/fx_planted1_S3 |
| 180 | `solver/fx_planted1_S3.ms.err` | stdout/stderr msolve:solver/fx_planted1_S3 | (i) msolve:solver/fx_planted1_S3 |
| 181 | `solver/fx_planted1_S3.ms.log` | stdout/stderr msolve:solver/fx_planted1_S3 | (i) msolve:solver/fx_planted1_S3 |
| 182 | `solver/fx_planted1_S3.ms.out` | argv exact msolve:solver/fx_planted1_S3 | (ii) msolve:solver/fx_planted1_S3 |
| 183 | `solver/fx_planted1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_S3_rescaled | (i) callgrind:fx_planted1_S3_rescaled |
| 184 | `solver/fx_planted1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_S3_rescaled | (i) callgrind:fx_planted1_S3_rescaled |
| 185 | `solver/fx_planted1_S3_rescaled.ms` | argv exact callgrind:fx_planted1_S3_rescaled; argv exact msolve:solver/fx_planted1_S3_rescaled | (ii) callgrind:fx_planted1_S3_rescaled; (ii) msolve:solver/fx_planted1_S3_rescaled |
| 186 | `solver/fx_planted1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_planted1_S3_rescaled | (i) msolve:solver/fx_planted1_S3_rescaled |
| 187 | `solver/fx_planted1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_planted1_S3_rescaled | (i) msolve:solver/fx_planted1_S3_rescaled |
| 188 | `solver/fx_planted1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_planted1_S3_rescaled | (ii) msolve:solver/fx_planted1_S3_rescaled |
| 189 | `solver/fx_planted1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_raw_u | (i) callgrind:fx_planted1_raw_u |
| 190 | `solver/fx_planted1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_raw_u | (i) callgrind:fx_planted1_raw_u |
| 191 | `solver/fx_planted1_raw_u.ms` | argv exact callgrind:fx_planted1_raw_u; argv exact msolve:solver/fx_planted1_raw_u | (ii) callgrind:fx_planted1_raw_u; (ii) msolve:solver/fx_planted1_raw_u |
| 192 | `solver/fx_planted1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_planted1_raw_u | (i) msolve:solver/fx_planted1_raw_u |
| 193 | `solver/fx_planted1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_planted1_raw_u | (i) msolve:solver/fx_planted1_raw_u |
| 194 | `solver/fx_planted1_raw_u.ms.out` | argv exact msolve:solver/fx_planted1_raw_u | (ii) msolve:solver/fx_planted1_raw_u |
| 195 | `solver/fx_planted1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_raw_x | (i) callgrind:fx_planted1_raw_x |
| 196 | `solver/fx_planted1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_raw_x | (i) callgrind:fx_planted1_raw_x |
| 197 | `solver/fx_planted1_raw_x.ms` | argv exact callgrind:fx_planted1_raw_x; argv exact msolve:solver/fx_planted1_raw_x | (ii) callgrind:fx_planted1_raw_x; (ii) msolve:solver/fx_planted1_raw_x |
| 198 | `solver/fx_planted1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_planted1_raw_x | (i) msolve:solver/fx_planted1_raw_x |
| 199 | `solver/fx_planted1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_planted1_raw_x | (i) msolve:solver/fx_planted1_raw_x |
| 200 | `solver/fx_planted1_raw_x.ms.out` | argv exact msolve:solver/fx_planted1_raw_x | (ii) msolve:solver/fx_planted1_raw_x |
| 201 | `solver/fx_planted1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_torsion_S3_norm | (i) callgrind:fx_planted1_torsion_S3_norm |
| 202 | `solver/fx_planted1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_torsion_S3_norm | (i) callgrind:fx_planted1_torsion_S3_norm |
| 203 | `solver/fx_planted1_torsion_S3_norm.ms` | argv exact callgrind:fx_planted1_torsion_S3_norm; argv exact msolve:solver/fx_planted1_torsion_S3_norm | (ii) callgrind:fx_planted1_torsion_S3_norm; (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| 204 | `solver/fx_planted1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_norm | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| 205 | `solver/fx_planted1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_norm | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| 206 | `solver/fx_planted1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_planted1_torsion_S3_norm | (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| 207 | `solver/fx_planted1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_torsion_S3_rq | (i) callgrind:fx_planted1_torsion_S3_rq |
| 208 | `solver/fx_planted1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_torsion_S3_rq | (i) callgrind:fx_planted1_torsion_S3_rq |
| 209 | `solver/fx_planted1_torsion_S3_rq.ms` | argv exact callgrind:fx_planted1_torsion_S3_rq; argv exact msolve:solver/fx_planted1_torsion_S3_rq | (ii) callgrind:fx_planted1_torsion_S3_rq; (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| 210 | `solver/fx_planted1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_rq | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| 211 | `solver/fx_planted1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_rq | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| 212 | `solver/fx_planted1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_planted1_torsion_S3_rq | (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| 213 | `solver/fx_reg0_S3.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_S3 | (i) callgrind:fx_reg0_S3 |
| 214 | `solver/fx_reg0_S3.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_S3 | (i) callgrind:fx_reg0_S3 |
| 215 | `solver/fx_reg0_S3.ms` | argv exact callgrind:fx_reg0_S3; argv exact msolve:solver/fx_reg0_S3 | (ii) callgrind:fx_reg0_S3; (ii) msolve:solver/fx_reg0_S3 |
| 216 | `solver/fx_reg0_S3.ms.err` | stdout/stderr msolve:solver/fx_reg0_S3 | (i) msolve:solver/fx_reg0_S3 |
| 217 | `solver/fx_reg0_S3.ms.log` | stdout/stderr msolve:solver/fx_reg0_S3 | (i) msolve:solver/fx_reg0_S3 |
| 218 | `solver/fx_reg0_S3.ms.out` | argv exact msolve:solver/fx_reg0_S3 | (ii) msolve:solver/fx_reg0_S3 |
| 219 | `solver/fx_reg0_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_S3_rescaled | (i) callgrind:fx_reg0_S3_rescaled |
| 220 | `solver/fx_reg0_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_S3_rescaled | (i) callgrind:fx_reg0_S3_rescaled |
| 221 | `solver/fx_reg0_S3_rescaled.ms` | argv exact callgrind:fx_reg0_S3_rescaled; argv exact msolve:solver/fx_reg0_S3_rescaled | (ii) callgrind:fx_reg0_S3_rescaled; (ii) msolve:solver/fx_reg0_S3_rescaled |
| 222 | `solver/fx_reg0_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_reg0_S3_rescaled | (i) msolve:solver/fx_reg0_S3_rescaled |
| 223 | `solver/fx_reg0_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_reg0_S3_rescaled | (i) msolve:solver/fx_reg0_S3_rescaled |
| 224 | `solver/fx_reg0_S3_rescaled.ms.out` | argv exact msolve:solver/fx_reg0_S3_rescaled | (ii) msolve:solver/fx_reg0_S3_rescaled |
| 225 | `solver/fx_reg0_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_raw_u | (i) callgrind:fx_reg0_raw_u |
| 226 | `solver/fx_reg0_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_raw_u | (i) callgrind:fx_reg0_raw_u |
| 227 | `solver/fx_reg0_raw_u.ms` | argv exact callgrind:fx_reg0_raw_u; argv exact msolve:solver/fx_reg0_raw_u | (ii) callgrind:fx_reg0_raw_u; (ii) msolve:solver/fx_reg0_raw_u |
| 228 | `solver/fx_reg0_raw_u.ms.err` | stdout/stderr msolve:solver/fx_reg0_raw_u | (i) msolve:solver/fx_reg0_raw_u |
| 229 | `solver/fx_reg0_raw_u.ms.log` | stdout/stderr msolve:solver/fx_reg0_raw_u | (i) msolve:solver/fx_reg0_raw_u |
| 230 | `solver/fx_reg0_raw_u.ms.out` | argv exact msolve:solver/fx_reg0_raw_u | (ii) msolve:solver/fx_reg0_raw_u |
| 231 | `solver/fx_reg0_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_raw_x | (i) callgrind:fx_reg0_raw_x |
| 232 | `solver/fx_reg0_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_raw_x | (i) callgrind:fx_reg0_raw_x |
| 233 | `solver/fx_reg0_raw_x.ms` | argv exact callgrind:fx_reg0_raw_x; argv exact msolve:solver/fx_reg0_raw_x | (ii) callgrind:fx_reg0_raw_x; (ii) msolve:solver/fx_reg0_raw_x |
| 234 | `solver/fx_reg0_raw_x.ms.err` | stdout/stderr msolve:solver/fx_reg0_raw_x | (i) msolve:solver/fx_reg0_raw_x |
| 235 | `solver/fx_reg0_raw_x.ms.log` | stdout/stderr msolve:solver/fx_reg0_raw_x | (i) msolve:solver/fx_reg0_raw_x |
| 236 | `solver/fx_reg0_raw_x.ms.out` | argv exact msolve:solver/fx_reg0_raw_x | (ii) msolve:solver/fx_reg0_raw_x |
| 237 | `solver/fx_reg0_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_torsion_S3_norm | (i) callgrind:fx_reg0_torsion_S3_norm |
| 238 | `solver/fx_reg0_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_torsion_S3_norm | (i) callgrind:fx_reg0_torsion_S3_norm |
| 239 | `solver/fx_reg0_torsion_S3_norm.ms` | argv exact callgrind:fx_reg0_torsion_S3_norm; argv exact msolve:solver/fx_reg0_torsion_S3_norm | (ii) callgrind:fx_reg0_torsion_S3_norm; (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| 240 | `solver/fx_reg0_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_norm | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| 241 | `solver/fx_reg0_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_norm | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| 242 | `solver/fx_reg0_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_reg0_torsion_S3_norm | (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| 243 | `solver/fx_reg0_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_torsion_S3_rq | (i) callgrind:fx_reg0_torsion_S3_rq |
| 244 | `solver/fx_reg0_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_torsion_S3_rq | (i) callgrind:fx_reg0_torsion_S3_rq |
| 245 | `solver/fx_reg0_torsion_S3_rq.ms` | argv exact callgrind:fx_reg0_torsion_S3_rq; argv exact msolve:solver/fx_reg0_torsion_S3_rq | (ii) callgrind:fx_reg0_torsion_S3_rq; (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| 246 | `solver/fx_reg0_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_rq | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| 247 | `solver/fx_reg0_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_rq | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| 248 | `solver/fx_reg0_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_reg0_torsion_S3_rq | (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| 249 | `solver/fx_reg1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_S3 | (i) callgrind:fx_reg1_S3 |
| 250 | `solver/fx_reg1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_S3 | (i) callgrind:fx_reg1_S3 |
| 251 | `solver/fx_reg1_S3.ms` | argv exact callgrind:fx_reg1_S3; argv exact msolve:solver/fx_reg1_S3 | (ii) callgrind:fx_reg1_S3; (ii) msolve:solver/fx_reg1_S3 |
| 252 | `solver/fx_reg1_S3.ms.err` | stdout/stderr msolve:solver/fx_reg1_S3 | (i) msolve:solver/fx_reg1_S3 |
| 253 | `solver/fx_reg1_S3.ms.log` | stdout/stderr msolve:solver/fx_reg1_S3 | (i) msolve:solver/fx_reg1_S3 |
| 254 | `solver/fx_reg1_S3.ms.out` | argv exact msolve:solver/fx_reg1_S3 | (ii) msolve:solver/fx_reg1_S3 |
| 255 | `solver/fx_reg1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_S3_rescaled | (i) callgrind:fx_reg1_S3_rescaled |
| 256 | `solver/fx_reg1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_S3_rescaled | (i) callgrind:fx_reg1_S3_rescaled |
| 257 | `solver/fx_reg1_S3_rescaled.ms` | argv exact callgrind:fx_reg1_S3_rescaled; argv exact msolve:solver/fx_reg1_S3_rescaled | (ii) callgrind:fx_reg1_S3_rescaled; (ii) msolve:solver/fx_reg1_S3_rescaled |
| 258 | `solver/fx_reg1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_reg1_S3_rescaled | (i) msolve:solver/fx_reg1_S3_rescaled |
| 259 | `solver/fx_reg1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_reg1_S3_rescaled | (i) msolve:solver/fx_reg1_S3_rescaled |
| 260 | `solver/fx_reg1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_reg1_S3_rescaled | (ii) msolve:solver/fx_reg1_S3_rescaled |
| 261 | `solver/fx_reg1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_raw_u | (i) callgrind:fx_reg1_raw_u |
| 262 | `solver/fx_reg1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_raw_u | (i) callgrind:fx_reg1_raw_u |
| 263 | `solver/fx_reg1_raw_u.ms` | argv exact callgrind:fx_reg1_raw_u; argv exact msolve:solver/fx_reg1_raw_u | (ii) callgrind:fx_reg1_raw_u; (ii) msolve:solver/fx_reg1_raw_u |
| 264 | `solver/fx_reg1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_reg1_raw_u | (i) msolve:solver/fx_reg1_raw_u |
| 265 | `solver/fx_reg1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_reg1_raw_u | (i) msolve:solver/fx_reg1_raw_u |
| 266 | `solver/fx_reg1_raw_u.ms.out` | argv exact msolve:solver/fx_reg1_raw_u | (ii) msolve:solver/fx_reg1_raw_u |
| 267 | `solver/fx_reg1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_raw_x | (i) callgrind:fx_reg1_raw_x |
| 268 | `solver/fx_reg1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_raw_x | (i) callgrind:fx_reg1_raw_x |
| 269 | `solver/fx_reg1_raw_x.ms` | argv exact callgrind:fx_reg1_raw_x; argv exact msolve:solver/fx_reg1_raw_x | (ii) callgrind:fx_reg1_raw_x; (ii) msolve:solver/fx_reg1_raw_x |
| 270 | `solver/fx_reg1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_reg1_raw_x | (i) msolve:solver/fx_reg1_raw_x |
| 271 | `solver/fx_reg1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_reg1_raw_x | (i) msolve:solver/fx_reg1_raw_x |
| 272 | `solver/fx_reg1_raw_x.ms.out` | argv exact msolve:solver/fx_reg1_raw_x | (ii) msolve:solver/fx_reg1_raw_x |
| 273 | `solver/fx_reg1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_torsion_S3_norm | (i) callgrind:fx_reg1_torsion_S3_norm |
| 274 | `solver/fx_reg1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_torsion_S3_norm | (i) callgrind:fx_reg1_torsion_S3_norm |
| 275 | `solver/fx_reg1_torsion_S3_norm.ms` | argv exact callgrind:fx_reg1_torsion_S3_norm; argv exact msolve:solver/fx_reg1_torsion_S3_norm | (ii) callgrind:fx_reg1_torsion_S3_norm; (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| 276 | `solver/fx_reg1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_norm | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| 277 | `solver/fx_reg1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_norm | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| 278 | `solver/fx_reg1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_reg1_torsion_S3_norm | (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| 279 | `solver/fx_reg1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_torsion_S3_rq | (i) callgrind:fx_reg1_torsion_S3_rq |
| 280 | `solver/fx_reg1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_torsion_S3_rq | (i) callgrind:fx_reg1_torsion_S3_rq |
| 281 | `solver/fx_reg1_torsion_S3_rq.ms` | argv exact callgrind:fx_reg1_torsion_S3_rq; argv exact msolve:solver/fx_reg1_torsion_S3_rq | (ii) callgrind:fx_reg1_torsion_S3_rq; (ii) msolve:solver/fx_reg1_torsion_S3_rq |
| 282 | `solver/fx_reg1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_rq | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| 283 | `solver/fx_reg1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_rq | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| 284 | `solver/fx_reg1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_reg1_torsion_S3_rq | (ii) msolve:solver/fx_reg1_torsion_S3_rq |

Files outside the five directories (53; outside the attribution rules' scope): `certificates/decomposition_S3_rescaled_tfresh1_r0.json`, `certificates/decomposition_S3_rescaled_tfresh1_r1.json`, `certificates/decomposition_S3_rescaled_tfresh1_r2.json`, `certificates/decomposition_S3_rescaled_tfresh1_r3.json`, `certificates/decomposition_S3_rescaled_tplanted0_r0.json`, `certificates/decomposition_S3_rescaled_tplanted0_r1.json`, `certificates/decomposition_S3_rescaled_tplanted0_r2.json`, `certificates/decomposition_S3_rescaled_tplanted0_r3.json`, `certificates/decomposition_S3_rescaled_tplanted0_r4.json`, `certificates/decomposition_S3_rescaled_tplanted0_r5.json`, `certificates/decomposition_S3_rescaled_tplanted0_r6.json`, `certificates/decomposition_S3_rescaled_tplanted0_r7.json`, `certificates/decomposition_S3_rescaled_tplanted1_r0.json`, `certificates/decomposition_S3_rescaled_tplanted1_r1.json`, `certificates/decomposition_S3_rescaled_tplanted1_r2.json`, `certificates/decomposition_S3_rescaled_tplanted1_r3.json`, `certificates/decomposition_S3_tfresh1_r0.json`, `certificates/decomposition_raw_u_tfresh1_r0.json`, `certificates/decomposition_raw_u_tfresh1_r1.json`, `certificates/decomposition_raw_u_tfresh1_r2.json`, `certificates/decomposition_raw_u_tfresh1_r3.json`, `certificates/decomposition_raw_u_tplanted0_r0.json`, `certificates/decomposition_raw_u_tplanted0_r1.json`, `certificates/decomposition_raw_u_tplanted0_r2.json`, `certificates/decomposition_raw_u_tplanted0_r3.json`, `certificates/decomposition_raw_u_tplanted0_r4.json`, `certificates/decomposition_raw_u_tplanted0_r5.json`, `certificates/decomposition_raw_u_tplanted0_r6.json`, `certificates/decomposition_raw_u_tplanted0_r7.json`, `certificates/decomposition_raw_u_tplanted1_r0.json`, `certificates/decomposition_raw_u_tplanted1_r1.json`, `certificates/decomposition_raw_u_tplanted1_r2.json`, `certificates/decomposition_raw_u_tplanted1_r3.json`, `certificates/decomposition_raw_x_tfresh1_r0.json`, `certificates/decomposition_torsion_S3_rq_tfresh1_r0.json`, `certificates/decomposition_torsion_S3_rq_tplanted0_r0.json`, `certificates/decomposition_torsion_S3_rq_tplanted0_r1.json`, `certificates/decomposition_torsion_S3_rq_tplanted1_r0.json`, `command.txt`, `cost-band-p64.yaml`, `environment.json`, `heur-dflat.yaml`, `ladder-table.yaml`, `manifest.yaml`, `pari-stack.json`, `polynomials/fixture_S3.npz`, `polynomials/fixture_S3_rescaled.npz`, `polynomials/fixture_torsion_S3_norm.npz`, `polynomials/fixture_torsion_S3_rq.npz`, `raw-result.json`, `solver-events.json`, `stderr.log`, `stdout.log`

### RUN-GFPN-902222: 284 files in the five directories, 88 reconstructed launch records

- childend RG-4 (b) as worded: first-clause counts NONE (gap) 20, argv exact 88, stdout/stderr 176; unattributed 20.
- gapattr RH-1 as worded: first-clause counts (i) 176, (ii) 88, (v) 20; unattributed 0.

| # | file | childend RG-4 (b) as worded | gapattr RH-1 as worded |
|---|---|---|---|
| 1 | `child/fixture_S3.meta.json` | NONE (recorder gap) | (v) childjob:fixture_S3 |
| 2 | `child/fixture_S3.npz` | NONE (recorder gap) | (v) childjob:fixture_S3 |
| 3 | `child/fixture_S3.spec.json` | argv exact childjob:fixture_S3 | (ii) childjob:fixture_S3 |
| 4 | `child/fixture_S3.stderr` | stdout/stderr childjob:fixture_S3 | (i) childjob:fixture_S3 |
| 5 | `child/fixture_S3.stdout` | stdout/stderr childjob:fixture_S3 | (i) childjob:fixture_S3 |
| 6 | `child/fixture_S3_rescaled.meta.json` | NONE (recorder gap) | (v) childjob:fixture_S3_rescaled |
| 7 | `child/fixture_S3_rescaled.npz` | NONE (recorder gap) | (v) childjob:fixture_S3_rescaled |
| 8 | `child/fixture_S3_rescaled.spec.json` | argv exact childjob:fixture_S3_rescaled | (ii) childjob:fixture_S3_rescaled |
| 9 | `child/fixture_S3_rescaled.stderr` | stdout/stderr childjob:fixture_S3_rescaled | (i) childjob:fixture_S3_rescaled |
| 10 | `child/fixture_S3_rescaled.stdout` | stdout/stderr childjob:fixture_S3_rescaled | (i) childjob:fixture_S3_rescaled |
| 11 | `child/fixture_torsion_S3_norm.meta.json` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_norm |
| 12 | `child/fixture_torsion_S3_norm.npz` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_norm |
| 13 | `child/fixture_torsion_S3_norm.spec.json` | argv exact childjob:fixture_torsion_S3_norm | (ii) childjob:fixture_torsion_S3_norm |
| 14 | `child/fixture_torsion_S3_norm.stderr` | stdout/stderr childjob:fixture_torsion_S3_norm | (i) childjob:fixture_torsion_S3_norm |
| 15 | `child/fixture_torsion_S3_norm.stdout` | stdout/stderr childjob:fixture_torsion_S3_norm | (i) childjob:fixture_torsion_S3_norm |
| 16 | `child/fixture_torsion_S3_rq.meta.json` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_rq |
| 17 | `child/fixture_torsion_S3_rq.npz` | NONE (recorder gap) | (v) childjob:fixture_torsion_S3_rq |
| 18 | `child/fixture_torsion_S3_rq.spec.json` | argv exact childjob:fixture_torsion_S3_rq | (ii) childjob:fixture_torsion_S3_rq |
| 19 | `child/fixture_torsion_S3_rq.stderr` | stdout/stderr childjob:fixture_torsion_S3_rq | (i) childjob:fixture_torsion_S3_rq |
| 20 | `child/fixture_torsion_S3_rq.stdout` | stdout/stderr childjob:fixture_torsion_S3_rq | (i) childjob:fixture_torsion_S3_rq |
| 21 | `child/fx_fresh1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh1_raw_u |
| 22 | `child/fx_fresh1_raw_u.spec.json` | argv exact childjob:fx_fresh1_raw_u | (ii) childjob:fx_fresh1_raw_u |
| 23 | `child/fx_fresh1_raw_u.stderr` | stdout/stderr childjob:fx_fresh1_raw_u | (i) childjob:fx_fresh1_raw_u |
| 24 | `child/fx_fresh1_raw_u.stdout` | stdout/stderr childjob:fx_fresh1_raw_u | (i) childjob:fx_fresh1_raw_u |
| 25 | `child/fx_fresh1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh1_raw_x |
| 26 | `child/fx_fresh1_raw_x.spec.json` | argv exact childjob:fx_fresh1_raw_x | (ii) childjob:fx_fresh1_raw_x |
| 27 | `child/fx_fresh1_raw_x.stderr` | stdout/stderr childjob:fx_fresh1_raw_x | (i) childjob:fx_fresh1_raw_x |
| 28 | `child/fx_fresh1_raw_x.stdout` | stdout/stderr childjob:fx_fresh1_raw_x | (i) childjob:fx_fresh1_raw_x |
| 29 | `child/fx_fresh2_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh2_raw_u |
| 30 | `child/fx_fresh2_raw_u.spec.json` | argv exact childjob:fx_fresh2_raw_u | (ii) childjob:fx_fresh2_raw_u |
| 31 | `child/fx_fresh2_raw_u.stderr` | stdout/stderr childjob:fx_fresh2_raw_u | (i) childjob:fx_fresh2_raw_u |
| 32 | `child/fx_fresh2_raw_u.stdout` | stdout/stderr childjob:fx_fresh2_raw_u | (i) childjob:fx_fresh2_raw_u |
| 33 | `child/fx_fresh2_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_fresh2_raw_x |
| 34 | `child/fx_fresh2_raw_x.spec.json` | argv exact childjob:fx_fresh2_raw_x | (ii) childjob:fx_fresh2_raw_x |
| 35 | `child/fx_fresh2_raw_x.stderr` | stdout/stderr childjob:fx_fresh2_raw_x | (i) childjob:fx_fresh2_raw_x |
| 36 | `child/fx_fresh2_raw_x.stdout` | stdout/stderr childjob:fx_fresh2_raw_x | (i) childjob:fx_fresh2_raw_x |
| 37 | `child/fx_planted0_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted0_raw_u |
| 38 | `child/fx_planted0_raw_u.spec.json` | argv exact childjob:fx_planted0_raw_u | (ii) childjob:fx_planted0_raw_u |
| 39 | `child/fx_planted0_raw_u.stderr` | stdout/stderr childjob:fx_planted0_raw_u | (i) childjob:fx_planted0_raw_u |
| 40 | `child/fx_planted0_raw_u.stdout` | stdout/stderr childjob:fx_planted0_raw_u | (i) childjob:fx_planted0_raw_u |
| 41 | `child/fx_planted0_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted0_raw_x |
| 42 | `child/fx_planted0_raw_x.spec.json` | argv exact childjob:fx_planted0_raw_x | (ii) childjob:fx_planted0_raw_x |
| 43 | `child/fx_planted0_raw_x.stderr` | stdout/stderr childjob:fx_planted0_raw_x | (i) childjob:fx_planted0_raw_x |
| 44 | `child/fx_planted0_raw_x.stdout` | stdout/stderr childjob:fx_planted0_raw_x | (i) childjob:fx_planted0_raw_x |
| 45 | `child/fx_planted1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted1_raw_u |
| 46 | `child/fx_planted1_raw_u.spec.json` | argv exact childjob:fx_planted1_raw_u | (ii) childjob:fx_planted1_raw_u |
| 47 | `child/fx_planted1_raw_u.stderr` | stdout/stderr childjob:fx_planted1_raw_u | (i) childjob:fx_planted1_raw_u |
| 48 | `child/fx_planted1_raw_u.stdout` | stdout/stderr childjob:fx_planted1_raw_u | (i) childjob:fx_planted1_raw_u |
| 49 | `child/fx_planted1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_planted1_raw_x |
| 50 | `child/fx_planted1_raw_x.spec.json` | argv exact childjob:fx_planted1_raw_x | (ii) childjob:fx_planted1_raw_x |
| 51 | `child/fx_planted1_raw_x.stderr` | stdout/stderr childjob:fx_planted1_raw_x | (i) childjob:fx_planted1_raw_x |
| 52 | `child/fx_planted1_raw_x.stdout` | stdout/stderr childjob:fx_planted1_raw_x | (i) childjob:fx_planted1_raw_x |
| 53 | `child/fx_reg0_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg0_raw_u |
| 54 | `child/fx_reg0_raw_u.spec.json` | argv exact childjob:fx_reg0_raw_u | (ii) childjob:fx_reg0_raw_u |
| 55 | `child/fx_reg0_raw_u.stderr` | stdout/stderr childjob:fx_reg0_raw_u | (i) childjob:fx_reg0_raw_u |
| 56 | `child/fx_reg0_raw_u.stdout` | stdout/stderr childjob:fx_reg0_raw_u | (i) childjob:fx_reg0_raw_u |
| 57 | `child/fx_reg0_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg0_raw_x |
| 58 | `child/fx_reg0_raw_x.spec.json` | argv exact childjob:fx_reg0_raw_x | (ii) childjob:fx_reg0_raw_x |
| 59 | `child/fx_reg0_raw_x.stderr` | stdout/stderr childjob:fx_reg0_raw_x | (i) childjob:fx_reg0_raw_x |
| 60 | `child/fx_reg0_raw_x.stdout` | stdout/stderr childjob:fx_reg0_raw_x | (i) childjob:fx_reg0_raw_x |
| 61 | `child/fx_reg1_raw_u.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg1_raw_u |
| 62 | `child/fx_reg1_raw_u.spec.json` | argv exact childjob:fx_reg1_raw_u | (ii) childjob:fx_reg1_raw_u |
| 63 | `child/fx_reg1_raw_u.stderr` | stdout/stderr childjob:fx_reg1_raw_u | (i) childjob:fx_reg1_raw_u |
| 64 | `child/fx_reg1_raw_u.stdout` | stdout/stderr childjob:fx_reg1_raw_u | (i) childjob:fx_reg1_raw_u |
| 65 | `child/fx_reg1_raw_x.meta.json` | NONE (recorder gap) | (v) childjob:fx_reg1_raw_x |
| 66 | `child/fx_reg1_raw_x.spec.json` | argv exact childjob:fx_reg1_raw_x | (ii) childjob:fx_reg1_raw_x |
| 67 | `child/fx_reg1_raw_x.stderr` | stdout/stderr childjob:fx_reg1_raw_x | (i) childjob:fx_reg1_raw_x |
| 68 | `child/fx_reg1_raw_x.stdout` | stdout/stderr childjob:fx_reg1_raw_x | (i) childjob:fx_reg1_raw_x |
| 69 | `solver/fx_fresh1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_S3 | (i) callgrind:fx_fresh1_S3 |
| 70 | `solver/fx_fresh1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_S3 | (i) callgrind:fx_fresh1_S3 |
| 71 | `solver/fx_fresh1_S3.ms` | argv exact callgrind:fx_fresh1_S3; argv exact msolve:solver/fx_fresh1_S3 | (ii) callgrind:fx_fresh1_S3; (ii) msolve:solver/fx_fresh1_S3 |
| 72 | `solver/fx_fresh1_S3.ms.err` | stdout/stderr msolve:solver/fx_fresh1_S3 | (i) msolve:solver/fx_fresh1_S3 |
| 73 | `solver/fx_fresh1_S3.ms.log` | stdout/stderr msolve:solver/fx_fresh1_S3 | (i) msolve:solver/fx_fresh1_S3 |
| 74 | `solver/fx_fresh1_S3.ms.out` | argv exact msolve:solver/fx_fresh1_S3 | (ii) msolve:solver/fx_fresh1_S3 |
| 75 | `solver/fx_fresh1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_S3_rescaled | (i) callgrind:fx_fresh1_S3_rescaled |
| 76 | `solver/fx_fresh1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_S3_rescaled | (i) callgrind:fx_fresh1_S3_rescaled |
| 77 | `solver/fx_fresh1_S3_rescaled.ms` | argv exact callgrind:fx_fresh1_S3_rescaled; argv exact msolve:solver/fx_fresh1_S3_rescaled | (ii) callgrind:fx_fresh1_S3_rescaled; (ii) msolve:solver/fx_fresh1_S3_rescaled |
| 78 | `solver/fx_fresh1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_fresh1_S3_rescaled | (i) msolve:solver/fx_fresh1_S3_rescaled |
| 79 | `solver/fx_fresh1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_fresh1_S3_rescaled | (i) msolve:solver/fx_fresh1_S3_rescaled |
| 80 | `solver/fx_fresh1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_fresh1_S3_rescaled | (ii) msolve:solver/fx_fresh1_S3_rescaled |
| 81 | `solver/fx_fresh1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_raw_u | (i) callgrind:fx_fresh1_raw_u |
| 82 | `solver/fx_fresh1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_raw_u | (i) callgrind:fx_fresh1_raw_u |
| 83 | `solver/fx_fresh1_raw_u.ms` | argv exact callgrind:fx_fresh1_raw_u; argv exact msolve:solver/fx_fresh1_raw_u | (ii) callgrind:fx_fresh1_raw_u; (ii) msolve:solver/fx_fresh1_raw_u |
| 84 | `solver/fx_fresh1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_fresh1_raw_u | (i) msolve:solver/fx_fresh1_raw_u |
| 85 | `solver/fx_fresh1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_fresh1_raw_u | (i) msolve:solver/fx_fresh1_raw_u |
| 86 | `solver/fx_fresh1_raw_u.ms.out` | argv exact msolve:solver/fx_fresh1_raw_u | (ii) msolve:solver/fx_fresh1_raw_u |
| 87 | `solver/fx_fresh1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_raw_x | (i) callgrind:fx_fresh1_raw_x |
| 88 | `solver/fx_fresh1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_raw_x | (i) callgrind:fx_fresh1_raw_x |
| 89 | `solver/fx_fresh1_raw_x.ms` | argv exact callgrind:fx_fresh1_raw_x; argv exact msolve:solver/fx_fresh1_raw_x | (ii) callgrind:fx_fresh1_raw_x; (ii) msolve:solver/fx_fresh1_raw_x |
| 90 | `solver/fx_fresh1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_fresh1_raw_x | (i) msolve:solver/fx_fresh1_raw_x |
| 91 | `solver/fx_fresh1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_fresh1_raw_x | (i) msolve:solver/fx_fresh1_raw_x |
| 92 | `solver/fx_fresh1_raw_x.ms.out` | argv exact msolve:solver/fx_fresh1_raw_x | (ii) msolve:solver/fx_fresh1_raw_x |
| 93 | `solver/fx_fresh1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_torsion_S3_norm | (i) callgrind:fx_fresh1_torsion_S3_norm |
| 94 | `solver/fx_fresh1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_torsion_S3_norm | (i) callgrind:fx_fresh1_torsion_S3_norm |
| 95 | `solver/fx_fresh1_torsion_S3_norm.ms` | argv exact callgrind:fx_fresh1_torsion_S3_norm; argv exact msolve:solver/fx_fresh1_torsion_S3_norm | (ii) callgrind:fx_fresh1_torsion_S3_norm; (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| 96 | `solver/fx_fresh1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_norm | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| 97 | `solver/fx_fresh1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_norm | (i) msolve:solver/fx_fresh1_torsion_S3_norm |
| 98 | `solver/fx_fresh1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_fresh1_torsion_S3_norm | (ii) msolve:solver/fx_fresh1_torsion_S3_norm |
| 99 | `solver/fx_fresh1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_fresh1_torsion_S3_rq | (i) callgrind:fx_fresh1_torsion_S3_rq |
| 100 | `solver/fx_fresh1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_fresh1_torsion_S3_rq | (i) callgrind:fx_fresh1_torsion_S3_rq |
| 101 | `solver/fx_fresh1_torsion_S3_rq.ms` | argv exact callgrind:fx_fresh1_torsion_S3_rq; argv exact msolve:solver/fx_fresh1_torsion_S3_rq | (ii) callgrind:fx_fresh1_torsion_S3_rq; (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| 102 | `solver/fx_fresh1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_rq | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| 103 | `solver/fx_fresh1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_fresh1_torsion_S3_rq | (i) msolve:solver/fx_fresh1_torsion_S3_rq |
| 104 | `solver/fx_fresh1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_fresh1_torsion_S3_rq | (ii) msolve:solver/fx_fresh1_torsion_S3_rq |
| 105 | `solver/fx_fresh2_S3.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_S3 | (i) callgrind:fx_fresh2_S3 |
| 106 | `solver/fx_fresh2_S3.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_S3 | (i) callgrind:fx_fresh2_S3 |
| 107 | `solver/fx_fresh2_S3.ms` | argv exact callgrind:fx_fresh2_S3; argv exact msolve:solver/fx_fresh2_S3 | (ii) callgrind:fx_fresh2_S3; (ii) msolve:solver/fx_fresh2_S3 |
| 108 | `solver/fx_fresh2_S3.ms.err` | stdout/stderr msolve:solver/fx_fresh2_S3 | (i) msolve:solver/fx_fresh2_S3 |
| 109 | `solver/fx_fresh2_S3.ms.log` | stdout/stderr msolve:solver/fx_fresh2_S3 | (i) msolve:solver/fx_fresh2_S3 |
| 110 | `solver/fx_fresh2_S3.ms.out` | argv exact msolve:solver/fx_fresh2_S3 | (ii) msolve:solver/fx_fresh2_S3 |
| 111 | `solver/fx_fresh2_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_S3_rescaled | (i) callgrind:fx_fresh2_S3_rescaled |
| 112 | `solver/fx_fresh2_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_S3_rescaled | (i) callgrind:fx_fresh2_S3_rescaled |
| 113 | `solver/fx_fresh2_S3_rescaled.ms` | argv exact callgrind:fx_fresh2_S3_rescaled; argv exact msolve:solver/fx_fresh2_S3_rescaled | (ii) callgrind:fx_fresh2_S3_rescaled; (ii) msolve:solver/fx_fresh2_S3_rescaled |
| 114 | `solver/fx_fresh2_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_fresh2_S3_rescaled | (i) msolve:solver/fx_fresh2_S3_rescaled |
| 115 | `solver/fx_fresh2_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_fresh2_S3_rescaled | (i) msolve:solver/fx_fresh2_S3_rescaled |
| 116 | `solver/fx_fresh2_S3_rescaled.ms.out` | argv exact msolve:solver/fx_fresh2_S3_rescaled | (ii) msolve:solver/fx_fresh2_S3_rescaled |
| 117 | `solver/fx_fresh2_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_raw_u | (i) callgrind:fx_fresh2_raw_u |
| 118 | `solver/fx_fresh2_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_raw_u | (i) callgrind:fx_fresh2_raw_u |
| 119 | `solver/fx_fresh2_raw_u.ms` | argv exact callgrind:fx_fresh2_raw_u; argv exact msolve:solver/fx_fresh2_raw_u | (ii) callgrind:fx_fresh2_raw_u; (ii) msolve:solver/fx_fresh2_raw_u |
| 120 | `solver/fx_fresh2_raw_u.ms.err` | stdout/stderr msolve:solver/fx_fresh2_raw_u | (i) msolve:solver/fx_fresh2_raw_u |
| 121 | `solver/fx_fresh2_raw_u.ms.log` | stdout/stderr msolve:solver/fx_fresh2_raw_u | (i) msolve:solver/fx_fresh2_raw_u |
| 122 | `solver/fx_fresh2_raw_u.ms.out` | argv exact msolve:solver/fx_fresh2_raw_u | (ii) msolve:solver/fx_fresh2_raw_u |
| 123 | `solver/fx_fresh2_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_raw_x | (i) callgrind:fx_fresh2_raw_x |
| 124 | `solver/fx_fresh2_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_raw_x | (i) callgrind:fx_fresh2_raw_x |
| 125 | `solver/fx_fresh2_raw_x.ms` | argv exact callgrind:fx_fresh2_raw_x; argv exact msolve:solver/fx_fresh2_raw_x | (ii) callgrind:fx_fresh2_raw_x; (ii) msolve:solver/fx_fresh2_raw_x |
| 126 | `solver/fx_fresh2_raw_x.ms.err` | stdout/stderr msolve:solver/fx_fresh2_raw_x | (i) msolve:solver/fx_fresh2_raw_x |
| 127 | `solver/fx_fresh2_raw_x.ms.log` | stdout/stderr msolve:solver/fx_fresh2_raw_x | (i) msolve:solver/fx_fresh2_raw_x |
| 128 | `solver/fx_fresh2_raw_x.ms.out` | argv exact msolve:solver/fx_fresh2_raw_x | (ii) msolve:solver/fx_fresh2_raw_x |
| 129 | `solver/fx_fresh2_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_torsion_S3_norm | (i) callgrind:fx_fresh2_torsion_S3_norm |
| 130 | `solver/fx_fresh2_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_torsion_S3_norm | (i) callgrind:fx_fresh2_torsion_S3_norm |
| 131 | `solver/fx_fresh2_torsion_S3_norm.ms` | argv exact callgrind:fx_fresh2_torsion_S3_norm; argv exact msolve:solver/fx_fresh2_torsion_S3_norm | (ii) callgrind:fx_fresh2_torsion_S3_norm; (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| 132 | `solver/fx_fresh2_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_norm | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| 133 | `solver/fx_fresh2_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_norm | (i) msolve:solver/fx_fresh2_torsion_S3_norm |
| 134 | `solver/fx_fresh2_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_fresh2_torsion_S3_norm | (ii) msolve:solver/fx_fresh2_torsion_S3_norm |
| 135 | `solver/fx_fresh2_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_fresh2_torsion_S3_rq | (i) callgrind:fx_fresh2_torsion_S3_rq |
| 136 | `solver/fx_fresh2_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_fresh2_torsion_S3_rq | (i) callgrind:fx_fresh2_torsion_S3_rq |
| 137 | `solver/fx_fresh2_torsion_S3_rq.ms` | argv exact callgrind:fx_fresh2_torsion_S3_rq; argv exact msolve:solver/fx_fresh2_torsion_S3_rq | (ii) callgrind:fx_fresh2_torsion_S3_rq; (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| 138 | `solver/fx_fresh2_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_rq | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| 139 | `solver/fx_fresh2_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_fresh2_torsion_S3_rq | (i) msolve:solver/fx_fresh2_torsion_S3_rq |
| 140 | `solver/fx_fresh2_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_fresh2_torsion_S3_rq | (ii) msolve:solver/fx_fresh2_torsion_S3_rq |
| 141 | `solver/fx_planted0_S3.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_S3 | (i) callgrind:fx_planted0_S3 |
| 142 | `solver/fx_planted0_S3.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_S3 | (i) callgrind:fx_planted0_S3 |
| 143 | `solver/fx_planted0_S3.ms` | argv exact callgrind:fx_planted0_S3; argv exact msolve:solver/fx_planted0_S3 | (ii) callgrind:fx_planted0_S3; (ii) msolve:solver/fx_planted0_S3 |
| 144 | `solver/fx_planted0_S3.ms.err` | stdout/stderr msolve:solver/fx_planted0_S3 | (i) msolve:solver/fx_planted0_S3 |
| 145 | `solver/fx_planted0_S3.ms.log` | stdout/stderr msolve:solver/fx_planted0_S3 | (i) msolve:solver/fx_planted0_S3 |
| 146 | `solver/fx_planted0_S3.ms.out` | argv exact msolve:solver/fx_planted0_S3 | (ii) msolve:solver/fx_planted0_S3 |
| 147 | `solver/fx_planted0_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_S3_rescaled | (i) callgrind:fx_planted0_S3_rescaled |
| 148 | `solver/fx_planted0_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_S3_rescaled | (i) callgrind:fx_planted0_S3_rescaled |
| 149 | `solver/fx_planted0_S3_rescaled.ms` | argv exact callgrind:fx_planted0_S3_rescaled; argv exact msolve:solver/fx_planted0_S3_rescaled | (ii) callgrind:fx_planted0_S3_rescaled; (ii) msolve:solver/fx_planted0_S3_rescaled |
| 150 | `solver/fx_planted0_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_planted0_S3_rescaled | (i) msolve:solver/fx_planted0_S3_rescaled |
| 151 | `solver/fx_planted0_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_planted0_S3_rescaled | (i) msolve:solver/fx_planted0_S3_rescaled |
| 152 | `solver/fx_planted0_S3_rescaled.ms.out` | argv exact msolve:solver/fx_planted0_S3_rescaled | (ii) msolve:solver/fx_planted0_S3_rescaled |
| 153 | `solver/fx_planted0_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_raw_u | (i) callgrind:fx_planted0_raw_u |
| 154 | `solver/fx_planted0_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_raw_u | (i) callgrind:fx_planted0_raw_u |
| 155 | `solver/fx_planted0_raw_u.ms` | argv exact callgrind:fx_planted0_raw_u; argv exact msolve:solver/fx_planted0_raw_u | (ii) callgrind:fx_planted0_raw_u; (ii) msolve:solver/fx_planted0_raw_u |
| 156 | `solver/fx_planted0_raw_u.ms.err` | stdout/stderr msolve:solver/fx_planted0_raw_u | (i) msolve:solver/fx_planted0_raw_u |
| 157 | `solver/fx_planted0_raw_u.ms.log` | stdout/stderr msolve:solver/fx_planted0_raw_u | (i) msolve:solver/fx_planted0_raw_u |
| 158 | `solver/fx_planted0_raw_u.ms.out` | argv exact msolve:solver/fx_planted0_raw_u | (ii) msolve:solver/fx_planted0_raw_u |
| 159 | `solver/fx_planted0_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_raw_x | (i) callgrind:fx_planted0_raw_x |
| 160 | `solver/fx_planted0_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_raw_x | (i) callgrind:fx_planted0_raw_x |
| 161 | `solver/fx_planted0_raw_x.ms` | argv exact callgrind:fx_planted0_raw_x; argv exact msolve:solver/fx_planted0_raw_x | (ii) callgrind:fx_planted0_raw_x; (ii) msolve:solver/fx_planted0_raw_x |
| 162 | `solver/fx_planted0_raw_x.ms.err` | stdout/stderr msolve:solver/fx_planted0_raw_x | (i) msolve:solver/fx_planted0_raw_x |
| 163 | `solver/fx_planted0_raw_x.ms.log` | stdout/stderr msolve:solver/fx_planted0_raw_x | (i) msolve:solver/fx_planted0_raw_x |
| 164 | `solver/fx_planted0_raw_x.ms.out` | argv exact msolve:solver/fx_planted0_raw_x | (ii) msolve:solver/fx_planted0_raw_x |
| 165 | `solver/fx_planted0_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_torsion_S3_norm | (i) callgrind:fx_planted0_torsion_S3_norm |
| 166 | `solver/fx_planted0_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_torsion_S3_norm | (i) callgrind:fx_planted0_torsion_S3_norm |
| 167 | `solver/fx_planted0_torsion_S3_norm.ms` | argv exact callgrind:fx_planted0_torsion_S3_norm; argv exact msolve:solver/fx_planted0_torsion_S3_norm | (ii) callgrind:fx_planted0_torsion_S3_norm; (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| 168 | `solver/fx_planted0_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_norm | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| 169 | `solver/fx_planted0_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_norm | (i) msolve:solver/fx_planted0_torsion_S3_norm |
| 170 | `solver/fx_planted0_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_planted0_torsion_S3_norm | (ii) msolve:solver/fx_planted0_torsion_S3_norm |
| 171 | `solver/fx_planted0_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_planted0_torsion_S3_rq | (i) callgrind:fx_planted0_torsion_S3_rq |
| 172 | `solver/fx_planted0_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_planted0_torsion_S3_rq | (i) callgrind:fx_planted0_torsion_S3_rq |
| 173 | `solver/fx_planted0_torsion_S3_rq.ms` | argv exact callgrind:fx_planted0_torsion_S3_rq; argv exact msolve:solver/fx_planted0_torsion_S3_rq | (ii) callgrind:fx_planted0_torsion_S3_rq; (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| 174 | `solver/fx_planted0_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_rq | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| 175 | `solver/fx_planted0_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_planted0_torsion_S3_rq | (i) msolve:solver/fx_planted0_torsion_S3_rq |
| 176 | `solver/fx_planted0_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_planted0_torsion_S3_rq | (ii) msolve:solver/fx_planted0_torsion_S3_rq |
| 177 | `solver/fx_planted1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_S3 | (i) callgrind:fx_planted1_S3 |
| 178 | `solver/fx_planted1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_S3 | (i) callgrind:fx_planted1_S3 |
| 179 | `solver/fx_planted1_S3.ms` | argv exact callgrind:fx_planted1_S3; argv exact msolve:solver/fx_planted1_S3 | (ii) callgrind:fx_planted1_S3; (ii) msolve:solver/fx_planted1_S3 |
| 180 | `solver/fx_planted1_S3.ms.err` | stdout/stderr msolve:solver/fx_planted1_S3 | (i) msolve:solver/fx_planted1_S3 |
| 181 | `solver/fx_planted1_S3.ms.log` | stdout/stderr msolve:solver/fx_planted1_S3 | (i) msolve:solver/fx_planted1_S3 |
| 182 | `solver/fx_planted1_S3.ms.out` | argv exact msolve:solver/fx_planted1_S3 | (ii) msolve:solver/fx_planted1_S3 |
| 183 | `solver/fx_planted1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_S3_rescaled | (i) callgrind:fx_planted1_S3_rescaled |
| 184 | `solver/fx_planted1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_S3_rescaled | (i) callgrind:fx_planted1_S3_rescaled |
| 185 | `solver/fx_planted1_S3_rescaled.ms` | argv exact callgrind:fx_planted1_S3_rescaled; argv exact msolve:solver/fx_planted1_S3_rescaled | (ii) callgrind:fx_planted1_S3_rescaled; (ii) msolve:solver/fx_planted1_S3_rescaled |
| 186 | `solver/fx_planted1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_planted1_S3_rescaled | (i) msolve:solver/fx_planted1_S3_rescaled |
| 187 | `solver/fx_planted1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_planted1_S3_rescaled | (i) msolve:solver/fx_planted1_S3_rescaled |
| 188 | `solver/fx_planted1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_planted1_S3_rescaled | (ii) msolve:solver/fx_planted1_S3_rescaled |
| 189 | `solver/fx_planted1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_raw_u | (i) callgrind:fx_planted1_raw_u |
| 190 | `solver/fx_planted1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_raw_u | (i) callgrind:fx_planted1_raw_u |
| 191 | `solver/fx_planted1_raw_u.ms` | argv exact callgrind:fx_planted1_raw_u; argv exact msolve:solver/fx_planted1_raw_u | (ii) callgrind:fx_planted1_raw_u; (ii) msolve:solver/fx_planted1_raw_u |
| 192 | `solver/fx_planted1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_planted1_raw_u | (i) msolve:solver/fx_planted1_raw_u |
| 193 | `solver/fx_planted1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_planted1_raw_u | (i) msolve:solver/fx_planted1_raw_u |
| 194 | `solver/fx_planted1_raw_u.ms.out` | argv exact msolve:solver/fx_planted1_raw_u | (ii) msolve:solver/fx_planted1_raw_u |
| 195 | `solver/fx_planted1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_raw_x | (i) callgrind:fx_planted1_raw_x |
| 196 | `solver/fx_planted1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_raw_x | (i) callgrind:fx_planted1_raw_x |
| 197 | `solver/fx_planted1_raw_x.ms` | argv exact callgrind:fx_planted1_raw_x; argv exact msolve:solver/fx_planted1_raw_x | (ii) callgrind:fx_planted1_raw_x; (ii) msolve:solver/fx_planted1_raw_x |
| 198 | `solver/fx_planted1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_planted1_raw_x | (i) msolve:solver/fx_planted1_raw_x |
| 199 | `solver/fx_planted1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_planted1_raw_x | (i) msolve:solver/fx_planted1_raw_x |
| 200 | `solver/fx_planted1_raw_x.ms.out` | argv exact msolve:solver/fx_planted1_raw_x | (ii) msolve:solver/fx_planted1_raw_x |
| 201 | `solver/fx_planted1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_torsion_S3_norm | (i) callgrind:fx_planted1_torsion_S3_norm |
| 202 | `solver/fx_planted1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_torsion_S3_norm | (i) callgrind:fx_planted1_torsion_S3_norm |
| 203 | `solver/fx_planted1_torsion_S3_norm.ms` | argv exact callgrind:fx_planted1_torsion_S3_norm; argv exact msolve:solver/fx_planted1_torsion_S3_norm | (ii) callgrind:fx_planted1_torsion_S3_norm; (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| 204 | `solver/fx_planted1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_norm | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| 205 | `solver/fx_planted1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_norm | (i) msolve:solver/fx_planted1_torsion_S3_norm |
| 206 | `solver/fx_planted1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_planted1_torsion_S3_norm | (ii) msolve:solver/fx_planted1_torsion_S3_norm |
| 207 | `solver/fx_planted1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_planted1_torsion_S3_rq | (i) callgrind:fx_planted1_torsion_S3_rq |
| 208 | `solver/fx_planted1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_planted1_torsion_S3_rq | (i) callgrind:fx_planted1_torsion_S3_rq |
| 209 | `solver/fx_planted1_torsion_S3_rq.ms` | argv exact callgrind:fx_planted1_torsion_S3_rq; argv exact msolve:solver/fx_planted1_torsion_S3_rq | (ii) callgrind:fx_planted1_torsion_S3_rq; (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| 210 | `solver/fx_planted1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_rq | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| 211 | `solver/fx_planted1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_planted1_torsion_S3_rq | (i) msolve:solver/fx_planted1_torsion_S3_rq |
| 212 | `solver/fx_planted1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_planted1_torsion_S3_rq | (ii) msolve:solver/fx_planted1_torsion_S3_rq |
| 213 | `solver/fx_reg0_S3.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_S3 | (i) callgrind:fx_reg0_S3 |
| 214 | `solver/fx_reg0_S3.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_S3 | (i) callgrind:fx_reg0_S3 |
| 215 | `solver/fx_reg0_S3.ms` | argv exact callgrind:fx_reg0_S3; argv exact msolve:solver/fx_reg0_S3 | (ii) callgrind:fx_reg0_S3; (ii) msolve:solver/fx_reg0_S3 |
| 216 | `solver/fx_reg0_S3.ms.err` | stdout/stderr msolve:solver/fx_reg0_S3 | (i) msolve:solver/fx_reg0_S3 |
| 217 | `solver/fx_reg0_S3.ms.log` | stdout/stderr msolve:solver/fx_reg0_S3 | (i) msolve:solver/fx_reg0_S3 |
| 218 | `solver/fx_reg0_S3.ms.out` | argv exact msolve:solver/fx_reg0_S3 | (ii) msolve:solver/fx_reg0_S3 |
| 219 | `solver/fx_reg0_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_S3_rescaled | (i) callgrind:fx_reg0_S3_rescaled |
| 220 | `solver/fx_reg0_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_S3_rescaled | (i) callgrind:fx_reg0_S3_rescaled |
| 221 | `solver/fx_reg0_S3_rescaled.ms` | argv exact callgrind:fx_reg0_S3_rescaled; argv exact msolve:solver/fx_reg0_S3_rescaled | (ii) callgrind:fx_reg0_S3_rescaled; (ii) msolve:solver/fx_reg0_S3_rescaled |
| 222 | `solver/fx_reg0_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_reg0_S3_rescaled | (i) msolve:solver/fx_reg0_S3_rescaled |
| 223 | `solver/fx_reg0_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_reg0_S3_rescaled | (i) msolve:solver/fx_reg0_S3_rescaled |
| 224 | `solver/fx_reg0_S3_rescaled.ms.out` | argv exact msolve:solver/fx_reg0_S3_rescaled | (ii) msolve:solver/fx_reg0_S3_rescaled |
| 225 | `solver/fx_reg0_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_raw_u | (i) callgrind:fx_reg0_raw_u |
| 226 | `solver/fx_reg0_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_raw_u | (i) callgrind:fx_reg0_raw_u |
| 227 | `solver/fx_reg0_raw_u.ms` | argv exact callgrind:fx_reg0_raw_u; argv exact msolve:solver/fx_reg0_raw_u | (ii) callgrind:fx_reg0_raw_u; (ii) msolve:solver/fx_reg0_raw_u |
| 228 | `solver/fx_reg0_raw_u.ms.err` | stdout/stderr msolve:solver/fx_reg0_raw_u | (i) msolve:solver/fx_reg0_raw_u |
| 229 | `solver/fx_reg0_raw_u.ms.log` | stdout/stderr msolve:solver/fx_reg0_raw_u | (i) msolve:solver/fx_reg0_raw_u |
| 230 | `solver/fx_reg0_raw_u.ms.out` | argv exact msolve:solver/fx_reg0_raw_u | (ii) msolve:solver/fx_reg0_raw_u |
| 231 | `solver/fx_reg0_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_raw_x | (i) callgrind:fx_reg0_raw_x |
| 232 | `solver/fx_reg0_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_raw_x | (i) callgrind:fx_reg0_raw_x |
| 233 | `solver/fx_reg0_raw_x.ms` | argv exact callgrind:fx_reg0_raw_x; argv exact msolve:solver/fx_reg0_raw_x | (ii) callgrind:fx_reg0_raw_x; (ii) msolve:solver/fx_reg0_raw_x |
| 234 | `solver/fx_reg0_raw_x.ms.err` | stdout/stderr msolve:solver/fx_reg0_raw_x | (i) msolve:solver/fx_reg0_raw_x |
| 235 | `solver/fx_reg0_raw_x.ms.log` | stdout/stderr msolve:solver/fx_reg0_raw_x | (i) msolve:solver/fx_reg0_raw_x |
| 236 | `solver/fx_reg0_raw_x.ms.out` | argv exact msolve:solver/fx_reg0_raw_x | (ii) msolve:solver/fx_reg0_raw_x |
| 237 | `solver/fx_reg0_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_torsion_S3_norm | (i) callgrind:fx_reg0_torsion_S3_norm |
| 238 | `solver/fx_reg0_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_torsion_S3_norm | (i) callgrind:fx_reg0_torsion_S3_norm |
| 239 | `solver/fx_reg0_torsion_S3_norm.ms` | argv exact callgrind:fx_reg0_torsion_S3_norm; argv exact msolve:solver/fx_reg0_torsion_S3_norm | (ii) callgrind:fx_reg0_torsion_S3_norm; (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| 240 | `solver/fx_reg0_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_norm | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| 241 | `solver/fx_reg0_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_norm | (i) msolve:solver/fx_reg0_torsion_S3_norm |
| 242 | `solver/fx_reg0_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_reg0_torsion_S3_norm | (ii) msolve:solver/fx_reg0_torsion_S3_norm |
| 243 | `solver/fx_reg0_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_reg0_torsion_S3_rq | (i) callgrind:fx_reg0_torsion_S3_rq |
| 244 | `solver/fx_reg0_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_reg0_torsion_S3_rq | (i) callgrind:fx_reg0_torsion_S3_rq |
| 245 | `solver/fx_reg0_torsion_S3_rq.ms` | argv exact callgrind:fx_reg0_torsion_S3_rq; argv exact msolve:solver/fx_reg0_torsion_S3_rq | (ii) callgrind:fx_reg0_torsion_S3_rq; (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| 246 | `solver/fx_reg0_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_rq | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| 247 | `solver/fx_reg0_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_reg0_torsion_S3_rq | (i) msolve:solver/fx_reg0_torsion_S3_rq |
| 248 | `solver/fx_reg0_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_reg0_torsion_S3_rq | (ii) msolve:solver/fx_reg0_torsion_S3_rq |
| 249 | `solver/fx_reg1_S3.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_S3 | (i) callgrind:fx_reg1_S3 |
| 250 | `solver/fx_reg1_S3.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_S3 | (i) callgrind:fx_reg1_S3 |
| 251 | `solver/fx_reg1_S3.ms` | argv exact callgrind:fx_reg1_S3; argv exact msolve:solver/fx_reg1_S3 | (ii) callgrind:fx_reg1_S3; (ii) msolve:solver/fx_reg1_S3 |
| 252 | `solver/fx_reg1_S3.ms.err` | stdout/stderr msolve:solver/fx_reg1_S3 | (i) msolve:solver/fx_reg1_S3 |
| 253 | `solver/fx_reg1_S3.ms.log` | stdout/stderr msolve:solver/fx_reg1_S3 | (i) msolve:solver/fx_reg1_S3 |
| 254 | `solver/fx_reg1_S3.ms.out` | argv exact msolve:solver/fx_reg1_S3 | (ii) msolve:solver/fx_reg1_S3 |
| 255 | `solver/fx_reg1_S3_rescaled.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_S3_rescaled | (i) callgrind:fx_reg1_S3_rescaled |
| 256 | `solver/fx_reg1_S3_rescaled.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_S3_rescaled | (i) callgrind:fx_reg1_S3_rescaled |
| 257 | `solver/fx_reg1_S3_rescaled.ms` | argv exact callgrind:fx_reg1_S3_rescaled; argv exact msolve:solver/fx_reg1_S3_rescaled | (ii) callgrind:fx_reg1_S3_rescaled; (ii) msolve:solver/fx_reg1_S3_rescaled |
| 258 | `solver/fx_reg1_S3_rescaled.ms.err` | stdout/stderr msolve:solver/fx_reg1_S3_rescaled | (i) msolve:solver/fx_reg1_S3_rescaled |
| 259 | `solver/fx_reg1_S3_rescaled.ms.log` | stdout/stderr msolve:solver/fx_reg1_S3_rescaled | (i) msolve:solver/fx_reg1_S3_rescaled |
| 260 | `solver/fx_reg1_S3_rescaled.ms.out` | argv exact msolve:solver/fx_reg1_S3_rescaled | (ii) msolve:solver/fx_reg1_S3_rescaled |
| 261 | `solver/fx_reg1_raw_u.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_raw_u | (i) callgrind:fx_reg1_raw_u |
| 262 | `solver/fx_reg1_raw_u.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_raw_u | (i) callgrind:fx_reg1_raw_u |
| 263 | `solver/fx_reg1_raw_u.ms` | argv exact callgrind:fx_reg1_raw_u; argv exact msolve:solver/fx_reg1_raw_u | (ii) callgrind:fx_reg1_raw_u; (ii) msolve:solver/fx_reg1_raw_u |
| 264 | `solver/fx_reg1_raw_u.ms.err` | stdout/stderr msolve:solver/fx_reg1_raw_u | (i) msolve:solver/fx_reg1_raw_u |
| 265 | `solver/fx_reg1_raw_u.ms.log` | stdout/stderr msolve:solver/fx_reg1_raw_u | (i) msolve:solver/fx_reg1_raw_u |
| 266 | `solver/fx_reg1_raw_u.ms.out` | argv exact msolve:solver/fx_reg1_raw_u | (ii) msolve:solver/fx_reg1_raw_u |
| 267 | `solver/fx_reg1_raw_x.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_raw_x | (i) callgrind:fx_reg1_raw_x |
| 268 | `solver/fx_reg1_raw_x.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_raw_x | (i) callgrind:fx_reg1_raw_x |
| 269 | `solver/fx_reg1_raw_x.ms` | argv exact callgrind:fx_reg1_raw_x; argv exact msolve:solver/fx_reg1_raw_x | (ii) callgrind:fx_reg1_raw_x; (ii) msolve:solver/fx_reg1_raw_x |
| 270 | `solver/fx_reg1_raw_x.ms.err` | stdout/stderr msolve:solver/fx_reg1_raw_x | (i) msolve:solver/fx_reg1_raw_x |
| 271 | `solver/fx_reg1_raw_x.ms.log` | stdout/stderr msolve:solver/fx_reg1_raw_x | (i) msolve:solver/fx_reg1_raw_x |
| 272 | `solver/fx_reg1_raw_x.ms.out` | argv exact msolve:solver/fx_reg1_raw_x | (ii) msolve:solver/fx_reg1_raw_x |
| 273 | `solver/fx_reg1_torsion_S3_norm.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_torsion_S3_norm | (i) callgrind:fx_reg1_torsion_S3_norm |
| 274 | `solver/fx_reg1_torsion_S3_norm.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_torsion_S3_norm | (i) callgrind:fx_reg1_torsion_S3_norm |
| 275 | `solver/fx_reg1_torsion_S3_norm.ms` | argv exact callgrind:fx_reg1_torsion_S3_norm; argv exact msolve:solver/fx_reg1_torsion_S3_norm | (ii) callgrind:fx_reg1_torsion_S3_norm; (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| 276 | `solver/fx_reg1_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_norm | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| 277 | `solver/fx_reg1_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_norm | (i) msolve:solver/fx_reg1_torsion_S3_norm |
| 278 | `solver/fx_reg1_torsion_S3_norm.ms.out` | argv exact msolve:solver/fx_reg1_torsion_S3_norm | (ii) msolve:solver/fx_reg1_torsion_S3_norm |
| 279 | `solver/fx_reg1_torsion_S3_rq.callgrind.stderr` | stdout/stderr callgrind:fx_reg1_torsion_S3_rq | (i) callgrind:fx_reg1_torsion_S3_rq |
| 280 | `solver/fx_reg1_torsion_S3_rq.callgrind.stdout` | stdout/stderr callgrind:fx_reg1_torsion_S3_rq | (i) callgrind:fx_reg1_torsion_S3_rq |
| 281 | `solver/fx_reg1_torsion_S3_rq.ms` | argv exact callgrind:fx_reg1_torsion_S3_rq; argv exact msolve:solver/fx_reg1_torsion_S3_rq | (ii) callgrind:fx_reg1_torsion_S3_rq; (ii) msolve:solver/fx_reg1_torsion_S3_rq |
| 282 | `solver/fx_reg1_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_rq | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| 283 | `solver/fx_reg1_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/fx_reg1_torsion_S3_rq | (i) msolve:solver/fx_reg1_torsion_S3_rq |
| 284 | `solver/fx_reg1_torsion_S3_rq.ms.out` | argv exact msolve:solver/fx_reg1_torsion_S3_rq | (ii) msolve:solver/fx_reg1_torsion_S3_rq |

Files outside the five directories (35; outside the attribution rules' scope): `certificates/decomposition_S3_rescaled_tplanted0_r0.json`, `certificates/decomposition_S3_rescaled_tplanted0_r1.json`, `certificates/decomposition_S3_rescaled_tplanted0_r2.json`, `certificates/decomposition_S3_rescaled_tplanted0_r3.json`, `certificates/decomposition_S3_rescaled_tplanted1_r0.json`, `certificates/decomposition_S3_rescaled_tplanted1_r1.json`, `certificates/decomposition_S3_rescaled_tplanted1_r2.json`, `certificates/decomposition_S3_rescaled_tplanted1_r3.json`, `certificates/decomposition_S3_tfresh1_r0.json`, `certificates/decomposition_raw_u_tplanted0_r0.json`, `certificates/decomposition_raw_u_tplanted0_r1.json`, `certificates/decomposition_raw_u_tplanted0_r2.json`, `certificates/decomposition_raw_u_tplanted0_r3.json`, `certificates/decomposition_raw_u_tplanted1_r0.json`, `certificates/decomposition_raw_u_tplanted1_r1.json`, `certificates/decomposition_raw_u_tplanted1_r2.json`, `certificates/decomposition_raw_u_tplanted1_r3.json`, `certificates/decomposition_raw_x_tfresh1_r0.json`, `certificates/decomposition_torsion_S3_rq_tplanted0_r0.json`, `certificates/decomposition_torsion_S3_rq_tplanted1_r0.json`, `command.txt`, `cost-band-p64.yaml`, `environment.json`, `heur-dflat.yaml`, `ladder-table.yaml`, `manifest.yaml`, `pari-stack.json`, `polynomials/fixture_S3.npz`, `polynomials/fixture_S3_rescaled.npz`, `polynomials/fixture_torsion_S3_norm.npz`, `polynomials/fixture_torsion_S3_rq.npz`, `raw-result.json`, `solver-events.json`, `stderr.log`, `stdout.log`

### RUN-GFPN-f5412a: 32 files in the five directories, 7 reconstructed launch records

- childend RG-4 (b) as worded: first-clause counts NONE (gap) 2, argv directory 5, argv exact 11, stdout/stderr 14; unattributed 2.
- gapattr RH-1 as worded: first-clause counts (i) 14, (ii) 11, (iv) 5, (v) 2; unattributed 0.

| # | file | childend RG-4 (b) as worded | gapattr RH-1 as worded |
|---|---|---|---|
| 1 | `child/anchor_S4.meta.json` | NONE (recorder gap) | (v) childjob:anchor_S4 |
| 2 | `child/anchor_S4.npz` | NONE (recorder gap) | (v) childjob:anchor_S4 |
| 3 | `child/anchor_S4.spec.json` | argv exact childjob:anchor_S4 | (ii) childjob:anchor_S4 |
| 4 | `child/anchor_S4.stderr` | stdout/stderr childjob:anchor_S4 | (i) childjob:anchor_S4 |
| 5 | `child/anchor_S4.stdout` | stdout/stderr childjob:anchor_S4 | (i) childjob:anchor_S4 |
| 6 | `comparator/anchor17_planted.ms` | argv directory comparator | (iv) comparator |
| 7 | `comparator/anchor17_random.ms` | argv directory comparator | (iv) comparator |
| 8 | `comparator/anchor25_planted.ms` | argv directory comparator | (iv) comparator |
| 9 | `comparator/anchor25_random.ms` | argv directory comparator | (iv) comparator |
| 10 | `comparator/k4a_results.json` | argv directory comparator | (iv) comparator |
| 11 | `comparator/stderr.log` | stdout/stderr comparator; argv directory comparator | (i) comparator; (iv) comparator |
| 12 | `comparator/stdout.log` | stdout/stderr comparator; argv directory comparator | (i) comparator; (iv) comparator |
| 13 | `solver/anchor_comparator_random.ms` | argv exact msolve:solver/anchor_comparator_random | (ii) msolve:solver/anchor_comparator_random |
| 14 | `solver/anchor_comparator_random.ms.err` | stdout/stderr msolve:solver/anchor_comparator_random | (i) msolve:solver/anchor_comparator_random |
| 15 | `solver/anchor_comparator_random.ms.log` | stdout/stderr msolve:solver/anchor_comparator_random | (i) msolve:solver/anchor_comparator_random |
| 16 | `solver/anchor_comparator_random.ms.out` | argv exact msolve:solver/anchor_comparator_random | (ii) msolve:solver/anchor_comparator_random |
| 17 | `solver/anchor_comparator_system.ms` | argv exact msolve:solver/anchor_comparator_system | (ii) msolve:solver/anchor_comparator_system |
| 18 | `solver/anchor_comparator_system.ms.err` | stdout/stderr msolve:solver/anchor_comparator_system | (i) msolve:solver/anchor_comparator_system |
| 19 | `solver/anchor_comparator_system.ms.log` | stdout/stderr msolve:solver/anchor_comparator_system | (i) msolve:solver/anchor_comparator_system |
| 20 | `solver/anchor_comparator_system.ms.out` | argv exact msolve:solver/anchor_comparator_system | (ii) msolve:solver/anchor_comparator_system |
| 21 | `solver/anchor_v2_t0.ms` | argv exact msolve:solver/anchor_v2_t0 | (ii) msolve:solver/anchor_v2_t0 |
| 22 | `solver/anchor_v2_t0.ms.err` | stdout/stderr msolve:solver/anchor_v2_t0 | (i) msolve:solver/anchor_v2_t0 |
| 23 | `solver/anchor_v2_t0.ms.log` | stdout/stderr msolve:solver/anchor_v2_t0 | (i) msolve:solver/anchor_v2_t0 |
| 24 | `solver/anchor_v2_t0.ms.out` | argv exact msolve:solver/anchor_v2_t0 | (ii) msolve:solver/anchor_v2_t0 |
| 25 | `solver/anchor_v2_t1.ms` | argv exact msolve:solver/anchor_v2_t1 | (ii) msolve:solver/anchor_v2_t1 |
| 26 | `solver/anchor_v2_t1.ms.err` | stdout/stderr msolve:solver/anchor_v2_t1 | (i) msolve:solver/anchor_v2_t1 |
| 27 | `solver/anchor_v2_t1.ms.log` | stdout/stderr msolve:solver/anchor_v2_t1 | (i) msolve:solver/anchor_v2_t1 |
| 28 | `solver/anchor_v2_t1.ms.out` | argv exact msolve:solver/anchor_v2_t1 | (ii) msolve:solver/anchor_v2_t1 |
| 29 | `solver/anchor_v2_t2.ms` | argv exact msolve:solver/anchor_v2_t2 | (ii) msolve:solver/anchor_v2_t2 |
| 30 | `solver/anchor_v2_t2.ms.err` | stdout/stderr msolve:solver/anchor_v2_t2 | (i) msolve:solver/anchor_v2_t2 |
| 31 | `solver/anchor_v2_t2.ms.log` | stdout/stderr msolve:solver/anchor_v2_t2 | (i) msolve:solver/anchor_v2_t2 |
| 32 | `solver/anchor_v2_t2.ms.out` | argv exact msolve:solver/anchor_v2_t2 | (ii) msolve:solver/anchor_v2_t2 |

Files outside the five directories (11; outside the attribution rules' scope): `command.txt`, `cost-band-p64.yaml`, `environment.json`, `heur-dflat.yaml`, `ladder-table.yaml`, `manifest.yaml`, `pari-stack.json`, `raw-result.json`, `solver-events.json`, `stderr.log`, `stdout.log`

### RUN-GFPN-bfe956: 83 files in the five directories, 19 reconstructed launch records

- childend RG-4 (b) as worded: first-clause counts NONE (gap) 18, argv exact 27, stdout/stderr 38; unattributed 18.
- gapattr RH-1 as worded: first-clause counts (i) 38, (ii) 27, (v) 18; unattributed 0.

| # | file | childend RG-4 (b) as worded | gapattr RH-1 as worded |
|---|---|---|---|
| 1 | `child/ctl_S3.meta.json` | NONE (recorder gap) | (v) childjob:ctl_S3 |
| 2 | `child/ctl_S3.npz` | NONE (recorder gap) | (v) childjob:ctl_S3 |
| 3 | `child/ctl_S3.spec.json` | argv exact childjob:ctl_S3 | (ii) childjob:ctl_S3 |
| 4 | `child/ctl_S3.stderr` | stdout/stderr childjob:ctl_S3 | (i) childjob:ctl_S3 |
| 5 | `child/ctl_S3.stdout` | stdout/stderr childjob:ctl_S3 | (i) childjob:ctl_S3 |
| 6 | `child/ctl_S3_rescaled.meta.json` | NONE (recorder gap) | (v) childjob:ctl_S3_rescaled |
| 7 | `child/ctl_S3_rescaled.npz` | NONE (recorder gap) | (v) childjob:ctl_S3_rescaled |
| 8 | `child/ctl_S3_rescaled.spec.json` | argv exact childjob:ctl_S3_rescaled | (ii) childjob:ctl_S3_rescaled |
| 9 | `child/ctl_S3_rescaled.stderr` | stdout/stderr childjob:ctl_S3_rescaled | (i) childjob:ctl_S3_rescaled |
| 10 | `child/ctl_S3_rescaled.stdout` | stdout/stderr childjob:ctl_S3_rescaled | (i) childjob:ctl_S3_rescaled |
| 11 | `child/ctl_identity_n3.meta.json` | NONE (recorder gap) | (v) childjob:ctl_identity_n3 |
| 12 | `child/ctl_identity_n3.npz` | NONE (recorder gap) | (v) childjob:ctl_identity_n3 |
| 13 | `child/ctl_identity_n3.spec.json` | argv exact childjob:ctl_identity_n3 | (ii) childjob:ctl_identity_n3 |
| 14 | `child/ctl_identity_n3.stderr` | stdout/stderr childjob:ctl_identity_n3 | (i) childjob:ctl_identity_n3 |
| 15 | `child/ctl_identity_n3.stdout` | stdout/stderr childjob:ctl_identity_n3 | (i) childjob:ctl_identity_n3 |
| 16 | `child/ctl_identity_n5_m3.meta.json` | NONE (recorder gap) | (v) childjob:ctl_identity_n5_m3 |
| 17 | `child/ctl_identity_n5_m3.npz` | NONE (recorder gap) | (v) childjob:ctl_identity_n5_m3 |
| 18 | `child/ctl_identity_n5_m3.spec.json` | argv exact childjob:ctl_identity_n5_m3 | (ii) childjob:ctl_identity_n5_m3 |
| 19 | `child/ctl_identity_n5_m3.stderr` | stdout/stderr childjob:ctl_identity_n5_m3 | (i) childjob:ctl_identity_n5_m3 |
| 20 | `child/ctl_identity_n5_m3.stdout` | stdout/stderr childjob:ctl_identity_n5_m3 | (i) childjob:ctl_identity_n5_m3 |
| 21 | `child/ctl_identity_n5_m4.meta.json` | NONE (recorder gap) | (v) childjob:ctl_identity_n5_m4 |
| 22 | `child/ctl_identity_n5_m4.npz` | NONE (recorder gap) | (v) childjob:ctl_identity_n5_m4 |
| 23 | `child/ctl_identity_n5_m4.spec.json` | argv exact childjob:ctl_identity_n5_m4 | (ii) childjob:ctl_identity_n5_m4 |
| 24 | `child/ctl_identity_n5_m4.stderr` | stdout/stderr childjob:ctl_identity_n5_m4 | (i) childjob:ctl_identity_n5_m4 |
| 25 | `child/ctl_identity_n5_m4.stdout` | stdout/stderr childjob:ctl_identity_n5_m4 | (i) childjob:ctl_identity_n5_m4 |
| 26 | `child/ctl_raw_n5_m3.meta.json` | NONE (recorder gap) | (v) childjob:ctl_raw_n5_m3 |
| 27 | `child/ctl_raw_n5_m3.spec.json` | argv exact childjob:ctl_raw_n5_m3 | (ii) childjob:ctl_raw_n5_m3 |
| 28 | `child/ctl_raw_n5_m3.stderr` | stdout/stderr childjob:ctl_raw_n5_m3 | (i) childjob:ctl_raw_n5_m3 |
| 29 | `child/ctl_raw_n5_m3.stdout` | stdout/stderr childjob:ctl_raw_n5_m3 | (i) childjob:ctl_raw_n5_m3 |
| 30 | `child/ctl_raw_n5_m4.meta.json` | NONE (recorder gap) | (v) childjob:ctl_raw_n5_m4 |
| 31 | `child/ctl_raw_n5_m4.spec.json` | argv exact childjob:ctl_raw_n5_m4 | (ii) childjob:ctl_raw_n5_m4 |
| 32 | `child/ctl_raw_n5_m4.stderr` | stdout/stderr childjob:ctl_raw_n5_m4 | (i) childjob:ctl_raw_n5_m4 |
| 33 | `child/ctl_raw_n5_m4.stdout` | stdout/stderr childjob:ctl_raw_n5_m4 | (i) childjob:ctl_raw_n5_m4 |
| 34 | `child/ctl_raw_planted.meta.json` | NONE (recorder gap) | (v) childjob:ctl_raw_planted |
| 35 | `child/ctl_raw_planted.spec.json` | argv exact childjob:ctl_raw_planted | (ii) childjob:ctl_raw_planted |
| 36 | `child/ctl_raw_planted.stderr` | stdout/stderr childjob:ctl_raw_planted | (i) childjob:ctl_raw_planted |
| 37 | `child/ctl_raw_planted.stdout` | stdout/stderr childjob:ctl_raw_planted | (i) childjob:ctl_raw_planted |
| 38 | `child/ctl_raw_random.meta.json` | NONE (recorder gap) | (v) childjob:ctl_raw_random |
| 39 | `child/ctl_raw_random.spec.json` | argv exact childjob:ctl_raw_random | (ii) childjob:ctl_raw_random |
| 40 | `child/ctl_raw_random.stderr` | stdout/stderr childjob:ctl_raw_random | (i) childjob:ctl_raw_random |
| 41 | `child/ctl_raw_random.stdout` | stdout/stderr childjob:ctl_raw_random | (i) childjob:ctl_raw_random |
| 42 | `child/ctl_torsion_S3_norm.meta.json` | NONE (recorder gap) | (v) childjob:ctl_torsion_S3_norm |
| 43 | `child/ctl_torsion_S3_norm.npz` | NONE (recorder gap) | (v) childjob:ctl_torsion_S3_norm |
| 44 | `child/ctl_torsion_S3_norm.spec.json` | argv exact childjob:ctl_torsion_S3_norm | (ii) childjob:ctl_torsion_S3_norm |
| 45 | `child/ctl_torsion_S3_norm.stderr` | stdout/stderr childjob:ctl_torsion_S3_norm | (i) childjob:ctl_torsion_S3_norm |
| 46 | `child/ctl_torsion_S3_norm.stdout` | stdout/stderr childjob:ctl_torsion_S3_norm | (i) childjob:ctl_torsion_S3_norm |
| 47 | `child/ctl_torsion_S3_rq.meta.json` | NONE (recorder gap) | (v) childjob:ctl_torsion_S3_rq |
| 48 | `child/ctl_torsion_S3_rq.npz` | NONE (recorder gap) | (v) childjob:ctl_torsion_S3_rq |
| 49 | `child/ctl_torsion_S3_rq.spec.json` | argv exact childjob:ctl_torsion_S3_rq | (ii) childjob:ctl_torsion_S3_rq |
| 50 | `child/ctl_torsion_S3_rq.stderr` | stdout/stderr childjob:ctl_torsion_S3_rq | (i) childjob:ctl_torsion_S3_rq |
| 51 | `child/ctl_torsion_S3_rq.stdout` | stdout/stderr childjob:ctl_torsion_S3_rq | (i) childjob:ctl_torsion_S3_rq |
| 52 | `solver/ctl_identity_planted.ms` | argv exact msolve:solver/ctl_identity_planted | (ii) msolve:solver/ctl_identity_planted |
| 53 | `solver/ctl_identity_planted.ms.err` | stdout/stderr msolve:solver/ctl_identity_planted | (i) msolve:solver/ctl_identity_planted |
| 54 | `solver/ctl_identity_planted.ms.log` | stdout/stderr msolve:solver/ctl_identity_planted | (i) msolve:solver/ctl_identity_planted |
| 55 | `solver/ctl_identity_planted.ms.out` | argv exact msolve:solver/ctl_identity_planted | (ii) msolve:solver/ctl_identity_planted |
| 56 | `solver/ctl_identity_random.ms` | argv exact msolve:solver/ctl_identity_random | (ii) msolve:solver/ctl_identity_random |
| 57 | `solver/ctl_identity_random.ms.err` | stdout/stderr msolve:solver/ctl_identity_random | (i) msolve:solver/ctl_identity_random |
| 58 | `solver/ctl_identity_random.ms.log` | stdout/stderr msolve:solver/ctl_identity_random | (i) msolve:solver/ctl_identity_random |
| 59 | `solver/ctl_identity_random.ms.out` | argv exact msolve:solver/ctl_identity_random | (ii) msolve:solver/ctl_identity_random |
| 60 | `solver/ctl_planted_S3.ms` | argv exact msolve:solver/ctl_planted_S3 | (ii) msolve:solver/ctl_planted_S3 |
| 61 | `solver/ctl_planted_S3.ms.err` | stdout/stderr msolve:solver/ctl_planted_S3 | (i) msolve:solver/ctl_planted_S3 |
| 62 | `solver/ctl_planted_S3.ms.log` | stdout/stderr msolve:solver/ctl_planted_S3 | (i) msolve:solver/ctl_planted_S3 |
| 63 | `solver/ctl_planted_S3.ms.out` | argv exact msolve:solver/ctl_planted_S3 | (ii) msolve:solver/ctl_planted_S3 |
| 64 | `solver/ctl_planted_S3_rescaled.ms` | argv exact msolve:solver/ctl_planted_S3_rescaled | (ii) msolve:solver/ctl_planted_S3_rescaled |
| 65 | `solver/ctl_planted_S3_rescaled.ms.err` | stdout/stderr msolve:solver/ctl_planted_S3_rescaled | (i) msolve:solver/ctl_planted_S3_rescaled |
| 66 | `solver/ctl_planted_S3_rescaled.ms.log` | stdout/stderr msolve:solver/ctl_planted_S3_rescaled | (i) msolve:solver/ctl_planted_S3_rescaled |
| 67 | `solver/ctl_planted_S3_rescaled.ms.out` | argv exact msolve:solver/ctl_planted_S3_rescaled | (ii) msolve:solver/ctl_planted_S3_rescaled |
| 68 | `solver/ctl_planted_torsion_S3_norm.ms` | argv exact msolve:solver/ctl_planted_torsion_S3_norm | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| 69 | `solver/ctl_planted_torsion_S3_norm.ms.err` | stdout/stderr msolve:solver/ctl_planted_torsion_S3_norm | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| 70 | `solver/ctl_planted_torsion_S3_norm.ms.log` | stdout/stderr msolve:solver/ctl_planted_torsion_S3_norm | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| 71 | `solver/ctl_planted_torsion_S3_norm.ms.out` | argv exact msolve:solver/ctl_planted_torsion_S3_norm | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| 72 | `solver/ctl_planted_torsion_S3_rq.ms` | argv exact msolve:solver/ctl_planted_torsion_S3_rq | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| 73 | `solver/ctl_planted_torsion_S3_rq.ms.err` | stdout/stderr msolve:solver/ctl_planted_torsion_S3_rq | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| 74 | `solver/ctl_planted_torsion_S3_rq.ms.log` | stdout/stderr msolve:solver/ctl_planted_torsion_S3_rq | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| 75 | `solver/ctl_planted_torsion_S3_rq.ms.out` | argv exact msolve:solver/ctl_planted_torsion_S3_rq | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| 76 | `solver/ctl_rawx_planted.ms` | argv exact msolve:solver/ctl_rawx_planted | (ii) msolve:solver/ctl_rawx_planted |
| 77 | `solver/ctl_rawx_planted.ms.err` | stdout/stderr msolve:solver/ctl_rawx_planted | (i) msolve:solver/ctl_rawx_planted |
| 78 | `solver/ctl_rawx_planted.ms.log` | stdout/stderr msolve:solver/ctl_rawx_planted | (i) msolve:solver/ctl_rawx_planted |
| 79 | `solver/ctl_rawx_planted.ms.out` | argv exact msolve:solver/ctl_rawx_planted | (ii) msolve:solver/ctl_rawx_planted |
| 80 | `solver/ctl_rawx_random.ms` | argv exact msolve:solver/ctl_rawx_random | (ii) msolve:solver/ctl_rawx_random |
| 81 | `solver/ctl_rawx_random.ms.err` | stdout/stderr msolve:solver/ctl_rawx_random | (i) msolve:solver/ctl_rawx_random |
| 82 | `solver/ctl_rawx_random.ms.log` | stdout/stderr msolve:solver/ctl_rawx_random | (i) msolve:solver/ctl_rawx_random |
| 83 | `solver/ctl_rawx_random.ms.out` | argv exact msolve:solver/ctl_rawx_random | (ii) msolve:solver/ctl_rawx_random |

Files outside the five directories (18; outside the attribution rules' scope): `certificates/decomposition_S3_rescaled_tctl_planted_r0.json`, `certificates/decomposition_S3_rescaled_tctl_planted_r1.json`, `certificates/decomposition_S3_rescaled_tctl_planted_r2.json`, `certificates/decomposition_S3_rescaled_tctl_planted_r3.json`, `certificates/decomposition_S3_tctl_planted_r0.json`, `certificates/decomposition_torsion_S3_norm_tctl_planted_r0.json`, `certificates/decomposition_torsion_S3_rq_tctl_planted_r0.json`, `command.txt`, `cost-band-p64.yaml`, `environment.json`, `heur-dflat.yaml`, `ladder-table.yaml`, `manifest.yaml`, `pari-stack.json`, `raw-result.json`, `solver-events.json`, `stderr.log`, `stdout.log`

### RUN-GFPN-bfe956 with the reconstructed record childjob:ctl_S3 removed (AJ-0 (e0))

- RH-1 with (v) weakened: first-clause counts (i) 36, (ii) 26, (v) weakened 21; unattributed 0.
- RH-1 as worded: first-clause counts (i) 36, (ii) 26, (v) 16, NONE (gap) 5; unattributed 5: `child/ctl_S3.meta.json`, `child/ctl_S3.npz`, `child/ctl_S3.spec.json`, `child/ctl_S3.stderr`, `child/ctl_S3.stdout`.

| # | file | RH-1, (v) weakened | RH-1 as worded |
|---|---|---|---|
| 1 | `child/ctl_S3.meta.json` | (v) weakened <some launch record> | NONE (recorder gap) |
| 2 | `child/ctl_S3.npz` | (v) weakened <some launch record> | NONE (recorder gap) |
| 3 | `child/ctl_S3.spec.json` | (v) weakened <some launch record> | NONE (recorder gap) |
| 4 | `child/ctl_S3.stderr` | (v) weakened <some launch record> | NONE (recorder gap) |
| 5 | `child/ctl_S3.stdout` | (v) weakened <some launch record> | NONE (recorder gap) |
| 6 | `child/ctl_S3_rescaled.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_S3_rescaled |
| 7 | `child/ctl_S3_rescaled.npz` | (v) weakened <some launch record> | (v) childjob:ctl_S3_rescaled |
| 8 | `child/ctl_S3_rescaled.spec.json` | (ii) childjob:ctl_S3_rescaled; (v) weakened <some launch record> | (ii) childjob:ctl_S3_rescaled |
| 9 | `child/ctl_S3_rescaled.stderr` | (i) childjob:ctl_S3_rescaled; (v) weakened <some launch record> | (i) childjob:ctl_S3_rescaled |
| 10 | `child/ctl_S3_rescaled.stdout` | (i) childjob:ctl_S3_rescaled; (v) weakened <some launch record> | (i) childjob:ctl_S3_rescaled |
| 11 | `child/ctl_identity_n3.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n3 |
| 12 | `child/ctl_identity_n3.npz` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n3 |
| 13 | `child/ctl_identity_n3.spec.json` | (ii) childjob:ctl_identity_n3; (v) weakened <some launch record> | (ii) childjob:ctl_identity_n3 |
| 14 | `child/ctl_identity_n3.stderr` | (i) childjob:ctl_identity_n3; (v) weakened <some launch record> | (i) childjob:ctl_identity_n3 |
| 15 | `child/ctl_identity_n3.stdout` | (i) childjob:ctl_identity_n3; (v) weakened <some launch record> | (i) childjob:ctl_identity_n3 |
| 16 | `child/ctl_identity_n5_m3.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n5_m3 |
| 17 | `child/ctl_identity_n5_m3.npz` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n5_m3 |
| 18 | `child/ctl_identity_n5_m3.spec.json` | (ii) childjob:ctl_identity_n5_m3; (v) weakened <some launch record> | (ii) childjob:ctl_identity_n5_m3 |
| 19 | `child/ctl_identity_n5_m3.stderr` | (i) childjob:ctl_identity_n5_m3; (v) weakened <some launch record> | (i) childjob:ctl_identity_n5_m3 |
| 20 | `child/ctl_identity_n5_m3.stdout` | (i) childjob:ctl_identity_n5_m3; (v) weakened <some launch record> | (i) childjob:ctl_identity_n5_m3 |
| 21 | `child/ctl_identity_n5_m4.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n5_m4 |
| 22 | `child/ctl_identity_n5_m4.npz` | (v) weakened <some launch record> | (v) childjob:ctl_identity_n5_m4 |
| 23 | `child/ctl_identity_n5_m4.spec.json` | (ii) childjob:ctl_identity_n5_m4; (v) weakened <some launch record> | (ii) childjob:ctl_identity_n5_m4 |
| 24 | `child/ctl_identity_n5_m4.stderr` | (i) childjob:ctl_identity_n5_m4; (v) weakened <some launch record> | (i) childjob:ctl_identity_n5_m4 |
| 25 | `child/ctl_identity_n5_m4.stdout` | (i) childjob:ctl_identity_n5_m4; (v) weakened <some launch record> | (i) childjob:ctl_identity_n5_m4 |
| 26 | `child/ctl_raw_n5_m3.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_raw_n5_m3 |
| 27 | `child/ctl_raw_n5_m3.spec.json` | (ii) childjob:ctl_raw_n5_m3; (v) weakened <some launch record> | (ii) childjob:ctl_raw_n5_m3 |
| 28 | `child/ctl_raw_n5_m3.stderr` | (i) childjob:ctl_raw_n5_m3; (v) weakened <some launch record> | (i) childjob:ctl_raw_n5_m3 |
| 29 | `child/ctl_raw_n5_m3.stdout` | (i) childjob:ctl_raw_n5_m3; (v) weakened <some launch record> | (i) childjob:ctl_raw_n5_m3 |
| 30 | `child/ctl_raw_n5_m4.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_raw_n5_m4 |
| 31 | `child/ctl_raw_n5_m4.spec.json` | (ii) childjob:ctl_raw_n5_m4; (v) weakened <some launch record> | (ii) childjob:ctl_raw_n5_m4 |
| 32 | `child/ctl_raw_n5_m4.stderr` | (i) childjob:ctl_raw_n5_m4; (v) weakened <some launch record> | (i) childjob:ctl_raw_n5_m4 |
| 33 | `child/ctl_raw_n5_m4.stdout` | (i) childjob:ctl_raw_n5_m4; (v) weakened <some launch record> | (i) childjob:ctl_raw_n5_m4 |
| 34 | `child/ctl_raw_planted.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_raw_planted |
| 35 | `child/ctl_raw_planted.spec.json` | (ii) childjob:ctl_raw_planted; (v) weakened <some launch record> | (ii) childjob:ctl_raw_planted |
| 36 | `child/ctl_raw_planted.stderr` | (i) childjob:ctl_raw_planted; (v) weakened <some launch record> | (i) childjob:ctl_raw_planted |
| 37 | `child/ctl_raw_planted.stdout` | (i) childjob:ctl_raw_planted; (v) weakened <some launch record> | (i) childjob:ctl_raw_planted |
| 38 | `child/ctl_raw_random.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_raw_random |
| 39 | `child/ctl_raw_random.spec.json` | (ii) childjob:ctl_raw_random; (v) weakened <some launch record> | (ii) childjob:ctl_raw_random |
| 40 | `child/ctl_raw_random.stderr` | (i) childjob:ctl_raw_random; (v) weakened <some launch record> | (i) childjob:ctl_raw_random |
| 41 | `child/ctl_raw_random.stdout` | (i) childjob:ctl_raw_random; (v) weakened <some launch record> | (i) childjob:ctl_raw_random |
| 42 | `child/ctl_torsion_S3_norm.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_torsion_S3_norm |
| 43 | `child/ctl_torsion_S3_norm.npz` | (v) weakened <some launch record> | (v) childjob:ctl_torsion_S3_norm |
| 44 | `child/ctl_torsion_S3_norm.spec.json` | (ii) childjob:ctl_torsion_S3_norm; (v) weakened <some launch record> | (ii) childjob:ctl_torsion_S3_norm |
| 45 | `child/ctl_torsion_S3_norm.stderr` | (i) childjob:ctl_torsion_S3_norm; (v) weakened <some launch record> | (i) childjob:ctl_torsion_S3_norm |
| 46 | `child/ctl_torsion_S3_norm.stdout` | (i) childjob:ctl_torsion_S3_norm; (v) weakened <some launch record> | (i) childjob:ctl_torsion_S3_norm |
| 47 | `child/ctl_torsion_S3_rq.meta.json` | (v) weakened <some launch record> | (v) childjob:ctl_torsion_S3_rq |
| 48 | `child/ctl_torsion_S3_rq.npz` | (v) weakened <some launch record> | (v) childjob:ctl_torsion_S3_rq |
| 49 | `child/ctl_torsion_S3_rq.spec.json` | (ii) childjob:ctl_torsion_S3_rq; (v) weakened <some launch record> | (ii) childjob:ctl_torsion_S3_rq |
| 50 | `child/ctl_torsion_S3_rq.stderr` | (i) childjob:ctl_torsion_S3_rq; (v) weakened <some launch record> | (i) childjob:ctl_torsion_S3_rq |
| 51 | `child/ctl_torsion_S3_rq.stdout` | (i) childjob:ctl_torsion_S3_rq; (v) weakened <some launch record> | (i) childjob:ctl_torsion_S3_rq |
| 52 | `solver/ctl_identity_planted.ms` | (ii) msolve:solver/ctl_identity_planted | (ii) msolve:solver/ctl_identity_planted |
| 53 | `solver/ctl_identity_planted.ms.err` | (i) msolve:solver/ctl_identity_planted | (i) msolve:solver/ctl_identity_planted |
| 54 | `solver/ctl_identity_planted.ms.log` | (i) msolve:solver/ctl_identity_planted | (i) msolve:solver/ctl_identity_planted |
| 55 | `solver/ctl_identity_planted.ms.out` | (ii) msolve:solver/ctl_identity_planted | (ii) msolve:solver/ctl_identity_planted |
| 56 | `solver/ctl_identity_random.ms` | (ii) msolve:solver/ctl_identity_random | (ii) msolve:solver/ctl_identity_random |
| 57 | `solver/ctl_identity_random.ms.err` | (i) msolve:solver/ctl_identity_random | (i) msolve:solver/ctl_identity_random |
| 58 | `solver/ctl_identity_random.ms.log` | (i) msolve:solver/ctl_identity_random | (i) msolve:solver/ctl_identity_random |
| 59 | `solver/ctl_identity_random.ms.out` | (ii) msolve:solver/ctl_identity_random | (ii) msolve:solver/ctl_identity_random |
| 60 | `solver/ctl_planted_S3.ms` | (ii) msolve:solver/ctl_planted_S3 | (ii) msolve:solver/ctl_planted_S3 |
| 61 | `solver/ctl_planted_S3.ms.err` | (i) msolve:solver/ctl_planted_S3 | (i) msolve:solver/ctl_planted_S3 |
| 62 | `solver/ctl_planted_S3.ms.log` | (i) msolve:solver/ctl_planted_S3 | (i) msolve:solver/ctl_planted_S3 |
| 63 | `solver/ctl_planted_S3.ms.out` | (ii) msolve:solver/ctl_planted_S3 | (ii) msolve:solver/ctl_planted_S3 |
| 64 | `solver/ctl_planted_S3_rescaled.ms` | (ii) msolve:solver/ctl_planted_S3_rescaled | (ii) msolve:solver/ctl_planted_S3_rescaled |
| 65 | `solver/ctl_planted_S3_rescaled.ms.err` | (i) msolve:solver/ctl_planted_S3_rescaled | (i) msolve:solver/ctl_planted_S3_rescaled |
| 66 | `solver/ctl_planted_S3_rescaled.ms.log` | (i) msolve:solver/ctl_planted_S3_rescaled | (i) msolve:solver/ctl_planted_S3_rescaled |
| 67 | `solver/ctl_planted_S3_rescaled.ms.out` | (ii) msolve:solver/ctl_planted_S3_rescaled | (ii) msolve:solver/ctl_planted_S3_rescaled |
| 68 | `solver/ctl_planted_torsion_S3_norm.ms` | (ii) msolve:solver/ctl_planted_torsion_S3_norm | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| 69 | `solver/ctl_planted_torsion_S3_norm.ms.err` | (i) msolve:solver/ctl_planted_torsion_S3_norm | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| 70 | `solver/ctl_planted_torsion_S3_norm.ms.log` | (i) msolve:solver/ctl_planted_torsion_S3_norm | (i) msolve:solver/ctl_planted_torsion_S3_norm |
| 71 | `solver/ctl_planted_torsion_S3_norm.ms.out` | (ii) msolve:solver/ctl_planted_torsion_S3_norm | (ii) msolve:solver/ctl_planted_torsion_S3_norm |
| 72 | `solver/ctl_planted_torsion_S3_rq.ms` | (ii) msolve:solver/ctl_planted_torsion_S3_rq | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| 73 | `solver/ctl_planted_torsion_S3_rq.ms.err` | (i) msolve:solver/ctl_planted_torsion_S3_rq | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| 74 | `solver/ctl_planted_torsion_S3_rq.ms.log` | (i) msolve:solver/ctl_planted_torsion_S3_rq | (i) msolve:solver/ctl_planted_torsion_S3_rq |
| 75 | `solver/ctl_planted_torsion_S3_rq.ms.out` | (ii) msolve:solver/ctl_planted_torsion_S3_rq | (ii) msolve:solver/ctl_planted_torsion_S3_rq |
| 76 | `solver/ctl_rawx_planted.ms` | (ii) msolve:solver/ctl_rawx_planted | (ii) msolve:solver/ctl_rawx_planted |
| 77 | `solver/ctl_rawx_planted.ms.err` | (i) msolve:solver/ctl_rawx_planted | (i) msolve:solver/ctl_rawx_planted |
| 78 | `solver/ctl_rawx_planted.ms.log` | (i) msolve:solver/ctl_rawx_planted | (i) msolve:solver/ctl_rawx_planted |
| 79 | `solver/ctl_rawx_planted.ms.out` | (ii) msolve:solver/ctl_rawx_planted | (ii) msolve:solver/ctl_rawx_planted |
| 80 | `solver/ctl_rawx_random.ms` | (ii) msolve:solver/ctl_rawx_random | (ii) msolve:solver/ctl_rawx_random |
| 81 | `solver/ctl_rawx_random.ms.err` | (i) msolve:solver/ctl_rawx_random | (i) msolve:solver/ctl_rawx_random |
| 82 | `solver/ctl_rawx_random.ms.log` | (i) msolve:solver/ctl_rawx_random | (i) msolve:solver/ctl_rawx_random |
| 83 | `solver/ctl_rawx_random.ms.out` | (ii) msolve:solver/ctl_rawx_random | (ii) msolve:solver/ctl_rawx_random |

## Appendix: computation scripts and outputs, verbatim

Every file below is in the reviewer's transient scratch directory `<scratch>/rt_94cc33/` (outside the repository; the literal scratch path is not written into this report). Each is reproduced byte for byte between the fences; the sha256 is of the file's bytes. No listed word required masking (the self-check found 0 hits in every file reproduced).

### `integrity.py`

- sha256: `12af6f427041b27ddcdd62c18e154e7a9b7775f0542d234c366c0efaf8795330`
- bytes: 1850; lines: 63
- argv: `python3 -B integrity.py | tee integrity.out   (cwd <scratch>/rt_94cc33)`
- role: CRG-2 (c): compares the path_sha256 field of five archive receipts with on-disk bytes. Output: integrity.out.

````text
#!/usr/bin/env python3
# CRG-2 (c): compare receipt path_sha256 entries against on-disk bytes.
# Reads only the path_sha256 field of each named receipt (JSON). Imports nothing
# from the repository.
import hashlib
import json
import os
import sys

REPO = "/home/user/crypto-autoresearcher"
ARCH = "coordination/goals/GOAL-GFPN-380702/archives"
RECEIPTS = [
    "TASK-20260924-0c2fdc/snapshot-receipt.json",
    "TASK-20260924-7e8a5d/snapshot-receipt.json",
    "TASK-20260924-71d070/snapshot-receipt.json",
    "TASK-20260924-ddfb69/snapshot-receipt.json",
    "TASK-20260924-a01341/snapshot-receipt.json",
]


def find_path_sha(obj):
    """Return the first dict found under a key named path_sha256."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "path_sha256" and isinstance(v, dict):
                return v
        for v in obj.values():
            r = find_path_sha(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_path_sha(v)
            if r is not None:
                return r
    return None


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


allok = True
for r in RECEIPTS:
    rp = os.path.join(REPO, ARCH, r)
    with open(rp, "rb") as f:
        data = json.loads(f.read())
    ps = find_path_sha(data)
    print("RECEIPT", r)
    if ps is None:
        print("  NO path_sha256 FIELD")
        allok = False
        continue
    for path, want in sorted(ps.items()):
        full = os.path.join(REPO, path)
        got = sha(full) if os.path.isfile(full) else "MISSING"
        ok = got == want
        allok &= ok
        print("  %s %s\n    receipt %s\n    disk    %s" % ("OK " if ok else "BAD", path, want, got))
print("ALL_OK", allok)
````

### `listing.py`

- sha256: `2c19faa2a5a877df500dfa47bc81ed60350ed2735baadf11b354ba352599309c`
- bytes: 2541; lines: 67
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B listing.py listing.json   (cwd <scratch>/rt_94cc33)`
- role: O_NOATIME directory listing of the four archived r3 gate packages; lstat of every directory before and after. Output: listing.json.

````text
#!/usr/bin/env python3
# Listing of the four archived r3 gate packages (CRG-4 (d), AJ-2 (1)).
# Reads DIRECTORY ENTRIES and lstat metadata only; opens every directory with
# O_RDONLY | O_DIRECTORY | O_NOATIME so that no access time is updated; reads no
# file content. Imports nothing from the repository. Writes one JSON listing to
# argv[2] (scratch, outside the repository).
import json
import os
import stat
import sys

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
FLAGS = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOATIME", 0)


def snap(path):
    st = os.lstat(path)
    return {"atime_ns": st.st_atime_ns, "mtime_ns": st.st_mtime_ns, "ctime_ns": st.st_ctime_ns}


def walk(root, rel=""):
    out, dirs = [], []
    p = os.path.join(root, rel) if rel else root
    before = snap(p)
    fd = os.open(p, FLAGS)
    try:
        with os.scandir(fd) as it:
            ents = sorted(it, key=lambda e: e.name)
            for e in ents:
                st = e.stat(follow_symlinks=False)
                r = os.path.join(rel, e.name) if rel else e.name
                if stat.S_ISDIR(st.st_mode):
                    dirs.append(r)
                    out.append({"path": r + "/", "type": "dir"})
                else:
                    t = "file" if stat.S_ISREG(st.st_mode) else ("symlink" if stat.S_ISLNK(st.st_mode) else "other")
                    out.append({"path": r, "type": t, "size": st.st_size})
    finally:
        os.close(fd)
    after = snap(p)
    changed = [p] if before != after else []
    for d in dirs:
        o2, c2 = walk(root, d)
        out += o2
        changed += c2
    return out, changed


res = {"o_noatime_flag_used": bool(getattr(os, "O_NOATIME", 0)), "packages": {}}
for pk in PKGS:
    root = os.path.join(RUNS, pk)
    ls, changed = walk(root)
    res["packages"][pk] = {"entries": ls, "dirs_with_metadata_change_during_listing": changed}
with open(sys.argv[1], "w") as fh:
    json.dump(res, fh, indent=1)
for pk in PKGS:
    e = res["packages"][pk]["entries"]
    nf = sum(1 for x in e if x["type"] == "file")
    top = {}
    for x in e:
        if x["type"] != "file":
            continue
        d = x["path"].split("/")[0] if "/" in x["path"] else "."
        top[d] = top.get(d, 0) + 1
    print(pk, "files", nf, "by top dir", top, "metadata changes", res["packages"][pk]["dirs_with_metadata_change_during_listing"])
print("O_NOATIME used:", res["o_noatime_flag_used"])
````

### `specout.py`

- sha256: `1b6662cdb7ad10bd4ca0641d11518ee26e6bf1fbc496f7386c3ac7c8d9ca05cb`
- bytes: 2188; lines: 52
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B specout.py listing.json specout.json   (cwd <scratch>/rt_94cc33)`
- role: O_NOATIME read of every child/*.spec.json 'out' value and the '# GFPN_RUN_DIR=' line of command.txt. Output: specout.json.

````text
#!/usr/bin/env python3
# Reads, with O_NOATIME, (1) the "out" value and the key names of every
# child/*.spec.json of the four archived r3 gate packages (RH-1 (v) reads exactly
# this field), and (2) the "# GFPN_RUN_DIR=" line of each package's command.txt
# (the run directory the frozen driver used, r3_run_wrapper.py 469-471).
# Imports nothing from the repository; writes JSON to argv[2] in scratch.
import json
import os
import sys

RUNS = "/home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs"
PKGS = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
NOA = getattr(os, "O_NOATIME", 0)
listing = json.load(open(sys.argv[1]))


def read_noatime(path):
    fd = os.open(path, os.O_RDONLY | NOA)
    try:
        chunks = []
        while True:
            b = os.read(fd, 1 << 20)
            if not b:
                break
            chunks.append(b)
        return b"".join(chunks)
    finally:
        os.close(fd)


out = {}
for pk in PKGS:
    rd = os.path.join(RUNS, pk)
    ent = listing["packages"][pk]["entries"]
    specs = sorted(x["path"] for x in ent if x["type"] == "file" and x["path"].startswith("child/") and x["path"].endswith(".spec.json"))
    cmd = read_noatime(os.path.join(rd, "command.txt")).decode("utf-8", "replace").splitlines()
    rdl = [l for l in cmd if l.startswith("# GFPN_RUN_DIR=")]
    rec = {"command_txt_GFPN_RUN_DIR_line": rdl, "specs": {}}
    for s in specs:
        try:
            d = json.loads(read_noatime(os.path.join(rd, s)))
            rec["specs"][s] = {"parses": True, "out": d.get("out"), "out_is_str": isinstance(d.get("out"), str),
                               "keys": sorted(d.keys()), "job": d.get("job"), "to_cache": d.get("to_cache")}
        except Exception as e:  # noqa: BLE001
            rec["specs"][s] = {"parses": False, "error": repr(e)}
    out[pk] = rec
with open(sys.argv[2], "w") as fh:
    json.dump(out, fh, indent=1)
for pk, rec in out.items():
    print("==", pk, rec["command_txt_GFPN_RUN_DIR_line"])
    for s, v in rec["specs"].items():
        print("  ", s, "parses", v.get("parses"), "job", v.get("job"), "to_cache", v.get("to_cache"), "out", v.get("out"))
````

### `scan.py`

- sha256: `7a194f5d49a47f160dcea9cdc464fbc23956feb7d3bc2b5e4968c223ab8d83c9`
- bytes: 6690; lines: 131
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B scan.py /home/user/crypto-autoresearcher > scan.out   (cwd <scratch>/rt_94cc33)`
- role: ast / dis static scan of the three implementation trees' source text, under an audit-hook guard refusing imports of scanned modules and every process launch. Output: scan.out.

````text
#!/usr/bin/env python3
"""TASK-20260924-94cc33 static scan (scratch; zero runs). Reads SOURCE TEXT of the three implementation trees and
parses it with ast / compiles v2_solver's text for dis in this process. Never imports, execs or evals a scanned
module. An audit hook refuses (and counts) any import whose top-level name is a .py stem of the scanned trees,
tools/ or harness/, and every process-launch event. Writes nothing; prints to stdout.
usage: python3 -B scan.py <repo-root>"""
import ast
import dis
import hashlib
import os
import sys

REPO = os.path.abspath(sys.argv[1])
EXP = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43")
TREES = ["implementation-v2", "implementation-v2-a1", "implementation-v2-r3"]

# ---------------------------------------------------------------- guard: names only (os.walk lists names)
stems = set()
for base in [os.path.join(EXP, t) for t in os.listdir(EXP) if t.startswith("implementation")] + \
        [os.path.join(REPO, "tools"), os.path.join(REPO, "harness")]:
    if os.path.isdir(base):
        for _dp, _dn, fn in os.walk(base):
            for f in fn:
                if f.endswith(".py"):
                    stems.add(f[:-3])
collide = sorted(s for s in stems if s in sys.stdlib_module_names or s in sys.modules)
REFUSE = stems - set(collide)
LAUNCH = ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty",
          "pty.spawn")
COUNT = {"import": 0, "launch": 0}
TEST = [True]


def hook(event, args):
    if event == "import" and args and str(args[0]).split(".")[0] in REFUSE:
        if not TEST[0]:
            COUNT["import"] += 1
        raise ImportError("guard: import of scanned module refused")
    if event in LAUNCH:
        if not TEST[0]:
            COUNT["launch"] += 1
        raise RuntimeError("guard: process launch refused")


sys.addaudithook(hook)
st = []
for ev, a in (("import", ("v2_solver", None, None, None, None)), ("os.fork", ())):
    try:
        sys.audit(ev, *a)
        st.append((ev, "NOT refused"))
    except (ImportError, RuntimeError):
        st.append((ev, "refused"))
TEST[0] = False
print("== guard: %d refused names, sha256(sorted) %s; stdlib/loaded collisions %s; self-test %s"
      % (len(REFUSE), hashlib.sha256("\n".join(sorted(REFUSE)).encode()).hexdigest(), collide, st))


def dotted(n):
    if isinstance(n, ast.Name):
        return n.id
    if isinstance(n, ast.Attribute):
        d = dotted(n.value)
        return d + "." + n.attr if d else n.attr
    return None


FILES = []
for t in TREES:
    for f in sorted(os.listdir(os.path.join(EXP, t))):
        if f.endswith(".py"):
            FILES.append(os.path.join(EXP, t, f))

EXITS = {"os._exit", "sys.exit", "exit", "quit", "os.abort", "os.kill", "os.killpg", "signal.raise_signal"}
EXECS = ("os.exec", "os.posix_spawn", "os.spawn", "subprocess.", "multiprocessing.", "pty.")
EXEC_EXACT = {"os.system", "os.popen", "os.fork", "os.forkpty", "os.fexecve"}
HOOKS = {"os.register_at_fork", "signal.signal", "signal.setitimer", "signal.alarm", "atexit.register",
         "faulthandler.enable", "faulthandler.register", "sys.settrace", "sys.setprofile", "sys.addaudithook",
         "threading.Thread", "threading.Timer", "_thread.start_new_thread", "sys.excepthook"}
sec = {k: [] for k in ("exit_calls", "systemexit_raises", "exec_fork_spawn", "hooks", "broad_handlers",
                       "run_child_refs", "from_v2_solver_import", "defs")}
for p in FILES:
    rel = os.path.relpath(p, REPO)
    src = open(p, encoding="utf-8").read()
    tree = ast.parse(src, filename=p)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            fn = dotted(n.func)
            if fn in EXITS:
                arg = ast.unparse(n.args[0])[:60] if n.args else ""
                sec["exit_calls"].append("%s:%d %s(%s)" % (rel, n.lineno, fn, arg))
            if fn and (fn in EXEC_EXACT or fn.startswith(EXECS)):
                sec["exec_fork_spawn"].append("%s:%d %s" % (rel, n.lineno, fn))
            if fn in HOOKS:
                sec["hooks"].append("%s:%d %s" % (rel, n.lineno, fn))
        if isinstance(n, ast.Raise) and n.exc is not None:
            nm = dotted(n.exc.func) if isinstance(n.exc, ast.Call) else dotted(n.exc)
            if nm and nm.endswith("SystemExit"):
                arg = ast.unparse(n.exc.args[0])[:50] if isinstance(n.exc, ast.Call) and n.exc.args else "(none)"
                sec["systemexit_raises"].append("%s:%d SystemExit(%s)" % (rel, n.lineno, arg))
        if isinstance(n, ast.ExceptHandler):
            tn = "bare" if n.type is None else ast.unparse(n.type)
            if n.type is None or any(x in tn for x in ("BaseException", "SystemExit", "KeyboardInterrupt")):
                reraise = any(isinstance(b, ast.Raise) for b in ast.walk(n))
                sec["broad_handlers"].append("%s:%d except %s (raise inside: %s)" % (rel, n.lineno, tn, reraise))
        if isinstance(n, (ast.Name, ast.Attribute)):
            nm = n.id if isinstance(n, ast.Name) else n.attr
            if nm in ("run_child", "_run_child_locked"):
                ctx = type(n.ctx).__name__
                sec["run_child_refs"].append("%s:%d %s [%s]" % (rel, n.lineno, ast.unparse(n)[:40], ctx))
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "v2_solver":
            sec["from_v2_solver_import"].append("%s:%d from %s import %s" % (rel, n.lineno, n.module,
                                                                            [a.name for a in n.names]))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in ("run_child", "_run_child_locked"):
            sec["defs"].append("%s:%d def %s" % (rel, n.lineno, n.name))
for k, v in sec.items():
    print("\n== (%s) %d" % (k, len(v)))
    for x in v:
        print("  " + x)

# ---------------------------------------------------------------- dis: where os.fork's result is stored (181)
vp = os.path.join(EXP, "implementation-v2", "v2_solver.py")
vsrc = open(vp, encoding="utf-8").read()
code = compile(vsrc, vp, "exec")
fn = [c for c in code.co_consts if hasattr(c, "co_name") and c.co_name == "_run_child_locked"][0]
print("\n== (dis) v2_solver.py sha256 %s, compiled from text with %s; _run_child_locked first line %d; lines 178-183:"
      % (hashlib.sha256(vsrc.encode()).hexdigest(), sys.version.split()[0], fn.co_firstlineno))
for ins in dis.get_instructions(fn):
    ln = ins.positions.lineno if ins.positions else None
    if ln is not None and 178 <= ln <= 183:
        print("  %d %-22s %s" % (ln, ins.opname, ins.argrepr))
print("\n== guard attempt counts: import %d, launch %d" % (COUNT["import"], COUNT["launch"]))
````

### `rt_eval.v1.py`

- sha256: `fc7dff05472260fecf8a1fa4f6995e8463fcf7e9a92310c71f8aed5ec171f40a`
- bytes: 49399; lines: 835
- argv: `NEVER RUN`
- role: First evaluator version. Superseded before any run: writers were stored as space-joined strings although launch ids contain spaces.

````text
#!/usr/bin/env python3
"""TASK-20260924-94cc33 rule evaluator (scratch; zero runs). One method for AJ-0..AJ-3, unchanged across objects.

It imports only json, os, re and itertools. It reads two scratch files written earlier by this review
(listing.json: the directory listings of the four archived r3 gate packages; specout.json: the "out" value of
each child/*.spec.json). It imports no module of any scanned tree and no third-party module.

LAYER 1 (file level) - attribution of every file under child/, solver/, health/, comparator/, pari/ to launch
records, under three encodings of the attribution text:
  RG4   childend RG-4 (b) AS WORDED: stdout_path / stderr_path; a path the argv names exactly; a file under a
        directory the argv names and no other record's argv names; the non-launch list.
  RH1   gapattr RH-1 (i)-(vi) AS WORDED, with the same non-launch list.
  RH1w  RH1 with clause (v) WEAKENED to "every file under child/ is attributed to some launch record" (CRG-4 (e)).
A file with no attribution and not on the non-launch list is a RECORDER GAP.

LAYER 2 (package level) - verdicts under the rule texts, encoded as functions:
  RK   readbackclose RK-1 (a)/(b) and RK-3 (b) AS WORDED (RL-3 gaps gate nothing).
  RF   failclosed AS WORDED: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 gap = a file of the RL-3 globs whose
       writing launch (truth) has no launch record.
  RG   childend: RF with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b) (layer 1 RG4; a gap makes the verdict FAIL).
  RH   gapattr: RG with RH-1 (layer 1 RH1), RH-2 (a)/(b) and RH-4.
  RHw  RH with RH-1 (v) weakened (layer 1 RH1w).
Each package is read under two manifest variants of the requested cap (v2_check_run.py 64):
  Mr = r3 base (r3_run_wrapper.py 550: raw-result.json envelope; None when the wrapper wrote raw-result.json);
  Mc = an r4 wrapper recording the requested cap independently of raw-result.json.
Definitions (failclosed 604-621), evaluated on TRUTH facts: FAIL-OPEN iff the verdict is PASS or PASS_ZL while one
of (i)..(v) holds. (ii) is evaluated under two readings of "recorded pair": LR = in a launch record; ANY = in any
RB-2 source (launch record, the launch's own child/*.meta.json, its RB-1 attempt record, driver-written raw).
PLANNED-BASIS REFUSAL iff the outcome is a planned basis outcome (driver-logic outcome as the rule set reads
RF-0 (b), acted on by a dependant's frozen logic or listed in RFR-2's enumeration) AND designed AND FAIL.
"""
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "<sys.executable>"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE_SET = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}          # RG-1 (c)
RENAMED = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
OUT = {}


def P(*a):
    print(*a)


# ============================================================================ LAYER 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 inputs / 251 report)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93 script)"
    return None


def attribute(rd, rels, dirs, records, specs, events, rule):
    """rels: paths relative to rd (files in the five directories); dirs: absolute directory paths present;
    records: dicts id, order, argv, stdout, stderr, child_end; specs: {absolute spec path: dict or None};
    events: dicts dir, tag, renamed_files. Returns {rel: [(record id, clause)]}."""
    names = {}
    for r in records:
        for a in set(r["argv"]):
            names[a] = names.get(a, 0) + 1
    res = {}
    for rel in rels:
        p = rd + "/" + rel
        hits = []
        for r in records:
            if p == r["stdout"] or p == r["stderr"]:
                hits.append((r["id"], "(i)" if rule != "RG4" else "stdout/stderr"))
            if p in r["argv"]:
                hits.append((r["id"], "(ii)" if rule != "RG4" else "argv exact"))
            if rule in ("RH1", "RH1w"):
                for a in r["argv"]:
                    if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                        hits.append((r["id"], "(iii)"))
            for a in r["argv"]:
                if a in dirs and p.startswith(a.rstrip("/") + "/") and names.get(a, 0) == 1:
                    hits.append((r["id"], "(iv)" if rule != "RG4" else "argv directory"))
            if rule == "RH1" and r.get("child_end") == "exec" and r["argv"]:
                m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
                if m:
                    sp = specs.get(r["argv"][-1])
                    o = rd + "/child/" + m.group("tag")
                    if isinstance(sp, dict) and isinstance(sp.get("out"), str) and sp["out"] == o and p in (o + ".npz", o + ".meta.json"):
                        hits.append((r["id"], "(v)"))
        if rule == "RH1w" and rel.startswith("child/") and records:
            hits.append(("<some launch record>", "(v) weakened"))
        if rule == "RH1":
            d, _, name = rel.partition("/")
            m = RENAMED.fullmatch(name)
            if m and d in ("solver", "health"):
                tag, k = m.group("tag"), int(m.group("k"))
                ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
                same = sorted((r for r in records if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["order"])
                if ev and len(same) >= k:
                    hits.append((same[k - 1]["id"], "(vi) k=%d" % k))
        if not hits and nonlaunch(rel):
            hits.append(("-", nonlaunch(rel)))
        res[rel] = hits
    return res


# ============================================================================ LAYER 2: launches, files, packages
def L(lid, site, tag, **kw):
    d = dict(lid=lid, site=site, tag=tag, created=True, p227=True, exec_=True, report="OK", rc=0, pair=CP,
             raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False, foreign_write=None,
             recorded=True, callback="normal", fired=None, new_pids=None, opened=None, t_en=None, value=None,
             order=0, outcome="ok", job=None, cached=False, dirn=None, gb=False, cg_out_left=False,
             partial_npz=False, in_attempt_record=False, in_raw=False, retained=True, files_override=None)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["opened"] is None:
        d["opened"] = d["created"]
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if d["dirn"] is None:
        d["dirn"] = {"childjob": "child", "msolve": "solver", "callgrind": "solver", "comparator": "comparator",
                     "health": "health", "gp": "pari"}[site]
    return d


def launch_paths(l, rd):
    """argv, stdout_path, stderr_path exactly as the frozen call sites build them."""
    t, dn = l["tag"], rd + "/" + l["dirn"]
    s = l["site"]
    if s == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if s in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"]
                + (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if s == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2",
                 "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if s == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if s == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(s)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch (relative paths, truth writer)."""
    if l["files_override"] is not None:
        return list(l["files_override"])
    t, dn, s, me = l["tag"], l["dirn"], l["site"], l["lid"]
    f = []
    opened = l["created"] and l["report"] is not None       # the fork child opened stdout/stderr (188-189)
    if s == "childjob":
        f.append((dn + "/" + t + ".spec.json", "driver (v2_driver 98-99)"))
        if opened:
            f += [(dn + "/" + t + ".stdout", me), (dn + "/" + t + ".stderr", me)]
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f += [(dn + "/" + t + ".npz", me + " (v2_child 38)"), (dn + "/" + t + ".meta.json", me + " (v2_child 41)")]
                else:
                    f += [(dn + "/" + t + ".meta.json", me + " (v2_child 104; .npz removed v2_driver 144)")]
            elif l["outcome"] == "refused_meta":
                f += [(dn + "/" + t + ".meta.json", me + " (v2_child 68/80)")]
            elif l["partial_npz"]:
                f += [(dn + "/" + t + ".npz", me + " (partial, v2_child 38/100)")]
    elif s in ("msolve", "health"):
        if l["retained"]:
            f.append((dn + "/" + t + ".ms", "driver (v2_driver 162 / a1_health 143)"))
        if opened:
            f += [(dn + "/" + t + ".ms.log", me), (dn + "/" + t + ".ms.err", me)]
        if l["exec_"] and l["outcome"] in ("ok", "ssf"):
            f.append((dn + "/" + t + ".ms.out", me))
    elif s == "callgrind":
        if opened:
            f += [(dn + "/" + t + ".callgrind.stdout", me), (dn + "/" + t + ".callgrind.stderr", me)]
        if l["cg_out_left"]:
            f.append((dn + "/" + t + ".callgrind.out", me + " (left by v2_solver 521-524)"))
    elif s == "comparator":
        if opened:
            f += [(dn + "/stdout.log", me), (dn + "/stderr.log", me)]
        if l["exec_"] and l["outcome"] == "ok":
            f += [(dn + "/" + x, me + " (k4a 279-281, 318)") for x in ("anchor25_random.ms", "anchor25_planted.ms",
                                                                      "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json")]
    elif s == "gp":
        f.append((dn + "/" + t + ".gp", "driver (a1_pari 91-93)"))
        if opened:
            f += [(dn + "/" + t + ".gp.stdout", me), (dn + "/" + t + ".gp.stderr", me)]
    return f


def resolve(kind, launches, raw="driver", gate=False, basis=None, row=None, designed=True, rd=None, resolves=(),
            raw_pairs=True, recording_failure=False, extra_files=()):
    """Build a package. resolves: (site_dir, tag, [launch ids in attempt order]) SE-3 / HR-3 re-solves: every
    attempt but the last has its .ms.out/.ms.log/.ms.err renamed to <name>.ssf-attempt<k> (r3_resolve 224-238)
    and listed under renamed_files["attempt<k>"] of the event (310)."""
    rd = rd or RUNS + "/RUN-X"
    files, events = {}, []
    for i, l in enumerate(launches):
        l["order"] = i
        for rel, w in files_of(l):
            files[rel] = w
    for dn, tag, ids in resolves:
        ev = {"dir": dn, "tag": tag, "renamed_files": {}}
        for k, lid in enumerate(ids[:-1], start=1):
            rn = {}
            for ext in (".ms.out", ".ms.log", ".ms.err"):
                src = dn + "/" + tag + ext
                if src in files:
                    w = files.pop(src)
                    files[src + ".ssf-attempt%d" % k] = lid + " (renamed, r3_resolve 234)"
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"renamed": True}
                else:
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"absent": True}
            ev["renamed_files"]["attempt%d" % k] = rn
            # the next attempt rewrites the unrenamed names
            nxt = next(x for x in launches if x["lid"] == ids[k])
            for rel, w in files_of(nxt):
                files[rel] = w
        events.append(ev)
    for rel, w in extra_files:
        files[rel] = w
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, designed=designed, rd=rd,
                files=files, events=events, raw_pairs=raw_pairs, recording_failure=recording_failure)


# ---------------------------------------------------------------- recorded values
def rk1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def rf1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return l["pair"]


def child_end(l, rs):
    if rs in ("RH", "RHw") and l["callback"] == "caught":
        return "undetermined"
    cc = rf1(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["opened"] and l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE_SET:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):
    cc = rk1(l) if rs == "RK" else rf1(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


# ---------------------------------------------------------------- package-level rules
def records_for_layer1(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = launch_paths(l, pkg["rd"])
        out.append({"id": l["lid"], "order": l["order"], "argv": argv, "stdout": so, "stderr": se,
                    "child_end": child_end(l, rs) if rs in ("RG", "RH", "RHw") else None})
    return out


def specs_of(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["site"] == "childjob":
            path = pkg["rd"] + "/child/" + l["tag"] + ".spec.json"
            if ("child/" + l["tag"] + ".spec.json") in pkg["files"]:
                sp[path] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"], "to_cache": l["cached"]}
    return sp


def dirs_of(pkg):
    return {pkg["rd"] + "/" + d for d in FIVE}


def gaps(pkg, rs):
    rels = sorted(pkg["files"])
    if rs == "RK":
        return []
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob_hit = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            writer = w.split(" ")[0]
            if glob_hit and writer not in ("driver", "-") and writer not in recorded:
                g.append(rel)
        return sorted(g)
    rule = {"RG": "RG4", "RH": "RH1", "RHw": "RH1w"}[rs]
    att = attribute(pkg["rd"], rels, dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    return sorted(r for r, h in att.items() if not h)


def pairs_collected(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(rec_pair(l))                                       # RL-3 (d)
        if l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"]:
            ps.append(l["pair"])                                         # RB-2 (b): the child's own getrlimit
        if l["in_attempt_record"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (c)
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (a)
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = pairs_collected(pkg)
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    five = bool(pkg["files"])
    r4ok = not pkg["recording_failure"]
    zl_kinds = ("cells_m5", "fixture4")
    if rs == "RK":
        if not items and r4ok:
            return "PASS"
        if not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(rf1(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs in ("RG", "RH", "RHw"):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    g = gaps(pkg, rs)
    if (not items and r4ok and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign
            and not g and not undet):
        return "PASS"
    if (not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok and rw == "driver"
            and pkg["kind"] in zl_kinds and not foreign):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    files = pkg["files"]
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (rk1(l) if rs == "RK" else rf1(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and l["pair"] == CP and (
                l["in_attempt_record"] or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in files and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            detected = (rs != "RK" and l["foreign_write"] == "ok") or (rs in ("RG", "RH", "RHw") and rec and child_end(l, rs) == "undetermined")
            if not detected:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs in ("RG", "RH", "RHw") and infra_stop(pkg):
        return False
    if rs in ("RH", "RHw") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (removed)"
    cc = rk1(l) if rs == "RK" else rf1(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs in ("RG", "RH", "RHw"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii) created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs in ("RG", "RH", "RHw") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant foreign-process record; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def evaluate(label, pkg, rule_sets=("RF", "RG", "RH"), ks=(0,), variants=("Mr", "Mc"), extra_b=None, key=None):
    P("\n### " + label)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-24s] %-3s %s" % (l["lid"][:24], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = pkg
            if k:
                other = [L("otherB%d" % j, "msolve", "otherB_t%d" % j, in_raw=True) for j in range(k)]
                q = resolve(pkg["kind"], [dict(x) for x in pkg["launches"]] + other, raw=pkg["raw"], gate=pkg["gate"],
                            basis=pkg["basis"], row=pkg["row"], designed=pkg["designed"], rd=pkg["rd"],
                            resolves=[(e["dir"], e["tag"], None) for e in []], raw_pairs=pkg["raw_pairs"],
                            recording_failure=pkg["recording_failure"])
                q["files"].update({r: w for r, w in pkg["files"].items()})
                q["events"] = pkg["events"]
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row " + str(q["row"]))))
            if rs in ("RG", "RH", "RHw") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RHw") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-18s defs %-24s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var),
                         "definitions": dfs, "fail_open": fo, "planned_basis_refusal": pb, "gaps": g})
    OUT[key or label] = rows
    return rows


# ============================================================================ helpers for objects
def ms(lid, tag, **kw):
    return L(lid, "msolve", tag, in_raw=True, **kw)


def cj(lid, tag, job="build", **kw):
    return L(lid, "childjob", tag, job=job, in_raw=True, **kw)


def cg(lid, tag, **kw):
    return L(lid, "callgrind", tag, in_raw=True, **kw)


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)"
BASIS_M4 = "X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003, 1068-1075)"


# ============================================================================ AJ-0 KNOWN-ANSWER CONTROL
P("=" * 110 + "\nAJ-0 KNOWN-ANSWER CONTROL (CRG-4 (a)-(e))")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK), RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False)
evaluate("KA-a1 P-16 (v2_solver 181 CALL then STORE_FAST pid; raise leaves the driver: raw wrapper-written)",
         resolve("cells_m5", [p16], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a1")
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False)
evaluate("KA-a2 P-F2 after P-14a (release raises in run_child's finally over a raise at 214)",
         resolve("cells_m5", [pf2], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a2")
evaluate("KA-a3 W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper 491-505)",
         resolve("cells_m5", [], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), key="KA-a3")

P("\n--- (b) failclosed AS WORDED (RF): FO-1, foreign-file write failed / interrupted")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (var_lab, wr, rc), "S5_t0", report=rep, rc=rc, pair=pr, p227=p227, exec_=False,
                    escaped=True, foreign_write=wr, outcome="refused_to_start" if var_lab == "C" else "crashed")
            evaluate("KA-b FO-1 variant %s, foreign write %s, escaped exit %d" % (var_lab, wr, rc),
                     resolve("cells_m5", [fo], basis=BASIS_M5, designed=False), ("RF", "RG", "RH"), ks=(0, 1),
                     key="KA-b-%s-%s-%d" % (var_lab, wr, rc))

P("\n--- (c) childend AS WORDED (RG): PB-2 and PB-3 (RF and RH for contrast)")
pb2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve raw_t0", "raw_t0"),
                           cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488)
evaluate("KA-c1 PB-2 cells m = 4, raw_grid child leaves child/grid_raw_t0.meta.json (v2_driver 1161 -> 133-147)", pb2, key="KA-c1")
a1 = ms("S5_t1 attempt 1 (SSF)", "S5_t1", outcome="ssf", in_attempt_record=True)
a2 = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
pb3 = resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1, a2], basis=BASIS_M5, row=485, resolves=[("solver", "S5_t1", [a1["lid"], a2["lid"]])])
evaluate("KA-c2 PB-3 cells m = 5 with one SE-3 re-solve at S-1 (r3_resolve 224-238, 310)", pb3, key="KA-c2")

# ---------------------------------------------------------------- (d) and AJ-2 (1): the listing check
listing = json.load(open(os.path.join(SCR, "listing.json")))
specout = json.load(open(os.path.join(SCR, "specout.json")))


def reconstruct(pk):
    """CRG-9 reconstruction by the frozen code's naming: child/<tag>.spec.json -> child job; solver/<tag>.ms.log ->
    msolve; solver/<tag>.callgrind.stdout -> callgrind; comparator/stdout.log -> comparator; health/<tag>.ms.log ->
    health msolve; pari/<tag>.gp.stdout -> gp. child_end "exec" is reconstructed for a child job whose <out>.meta.json
    or <out>.npz exists (only v2_child writes them, after exec) and for every launch whose output file exists."""
    rd = RUNS + "/" + pk
    ents = listing["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    dirs = {rd + "/" + e["path"].rstrip("/") for e in ents if e["type"] == "dir"}
    recs, order = [], 0
    specs = {}
    for rel, v in specout[pk]["specs"].items():
        specs[rd + "/" + rel] = {"out": v.get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = argv = so = se = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid = "childjob:" + t
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out", "<-P|-g>", "1"]
            so, se, ce, lid = rd + "/" + d + "/" + name, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v",
                    "2", "-t", "1", "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se, ce, lid = rd + "/solver/" + name, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t
        elif rel == "comparator/stdout.log":
            argv, so, se, ce, lid = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se, ce, lid = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/pari/" + name, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t
        if lid:
            recs.append({"id": lid, "order": order, "argv": argv, "stdout": so, "stderr": se, "child_end": ce})
            order += 1
    return rd, rels, dirs, recs, specs


def listing_check(rule, pkgs, drop=None, label=""):
    P("\n--- listing check under %s %s" % (rule, label))
    res = {}
    for pk in pkgs:
        rd, rels, dirs, recs, specs = reconstruct(pk)
        if drop:
            recs = [r for r in recs if r["id"] != drop]
        att = attribute(rd, rels, dirs, recs, specs, [], rule)
        g = [r for r in rels if not att[r]]
        by_clause = {}
        for r, h in att.items():
            for (_i, c) in (h[:1] if h else [("-", "NONE (gap)")]):
                by_clause[c] = by_clause.get(c, 0) + 1
        per_rec = {}
        for r, h in att.items():
            for (i, c) in h:
                per_rec.setdefault(i, []).append(c)
        meta_g = [x for x in g if x.endswith(".meta.json")]
        P("  %s: %d files in the five directories, %d reconstructed launch records (%s); files by first clause %s"
          % (pk, len(rels), len(recs), dict(sorted({k: sum(1 for r in recs if r["id"].startswith(k)) for k in ("childjob", "msolve", "callgrind", "comparator", "gp")}.items())),
             dict(sorted(by_clause.items()))))
        P("    unattributed: %d (child/*.meta.json %d; child/*.npz %d; other %d)" % (len(g), len(meta_g), sum(1 for x in g if x.endswith(".npz")),
                                                                                  len(g) - len(meta_g) - sum(1 for x in g if x.endswith(".npz"))))
        for x in g:
            P("      GAP " + x)
        res[pk] = {"n_files": len(rels), "n_records": len(recs), "gaps": g, "first_clause_counts": by_clause,
                   "attribution": {r: att[r] for r in rels}}
    OUT["listing_%s%s" % (rule, "_drop_" + drop if drop else "")] = res
    return res


GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
P("\n--- (d) LISTING CHECK under childend RG-4 (b) AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RG4", GATE, label="(childend)")

P("\n--- (e) gapattr with RH-1 (v) WEAKENED vs AS WORDED, one child-job launch record removed")
P("  (e0) file level on RUN-GFPN-bfe956 with the record of childjob:ctl_S3 removed:")
listing_check("RH1w", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(weakened)")
listing_check("RH1", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(worded)")
e1 = resolve("controls", [cj("ctl_identity_n3", "ctl_identity_n3", in_raw=False), cj("ctl_raw_random", "ctl_raw_random", job="grid", in_raw=False),
                          cj("ctl_S3", "ctl_S3", in_raw=False, recorded=False), ms("ctl_planted_S3", "ctl_planted_S3", in_raw=False)],
             gate=True, row=478, raw_pairs=False, rd=RUNS + "/RUN-G4-copy")
evaluate("KA-e1 controls (G4 shape, raw carries no pair), child-job record of ctl_S3 REMOVED (build ok: meta carries its pair)",
         e1, ("RH", "RHw"), key="KA-e1")
e2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid", outcome="crashed", partial_npz=True, recorded=False, in_raw=False),
                          ms("msolve S4_t0", "S4_t0"), cj("grid_raw_t1 child", "grid_raw_t1", job="grid"), ms("msolve raw_t1", "raw_t1")],
             basis=BASIS_M4, row=488)
evaluate("KA-e2 cells m = 4, raw_grid child of target 0 crashed after exec (partial .npz, no meta), its record REMOVED",
         e2, ("RH", "RHw"), key="KA-e2")

# ============================================================================ AJ-1 under gapattr
P("\n" + "=" * 110 + "\nAJ-1 FAIL-OPEN SEARCH UNDER GAPATTR (RH), RG for contrast")
P("\n--- (1) lost launch records whose files another record's positive source names")


def resolved_cell(drop=None, n=2, site="msolve", dn="solver", tag="S5_t1", kind="cells_m5", extra=()):
    atts = [L("%s attempt %d" % (tag, k), site, tag, outcome="ssf" if k < n else "ok", in_attempt_record=True, in_raw=(k == n),
              recorded=(drop is None or k not in drop)) for k in range(1, n + 1)]
    lau = [ms("S5_t0", "S5_t0")] + list(extra) + atts
    return resolve(kind, lau, basis=BASIS_M5 if kind == "cells_m5" else "X-02 / X-13 (controls_a1 image)", row=485 if kind == "cells_m5" else 480,
                   gate=kind == "controls_a1", resolves=[(dn, tag, [a["lid"] for a in atts])])


evaluate("LR-0 SE-3 re-solve at S-1 (2 attempts), every launch record present", resolved_cell(), ("RG", "RH"), key="LR-0")
evaluate("LR-1 SE-3 re-solve at S-1 (2 attempts), the FINAL attempt's launch record REMOVED", resolved_cell(drop={2}), ("RG", "RH"), key="LR-1")
evaluate("LR-2 SE-3 re-solve at S-1 (2 attempts), attempt 1's launch record REMOVED", resolved_cell(drop={1}), ("RG", "RH"), key="LR-2")
evaluate("LR-3 SE-3 re-solve at S-1 (3 attempts), attempt 2's launch record REMOVED", resolved_cell(drop={2}, n=3), ("RG", "RH"), key="LR-3")
evaluate("LR-4 SE-3 re-solve at S-1 (3 attempts), attempts 2 and 3 REMOVED", resolved_cell(drop={2, 3}, n=3), ("RG", "RH"), key="LR-4")
evaluate("LR-5 HR-3 re-solve at S-2 in controls_a1 (2 attempts), the final attempt's record REMOVED",
         resolved_cell(drop={2}, site="health", dn="health", tag="health_p1073741831_d222", kind="controls_a1",
                       extra=[L("gp", "gp", "controls_a1_pari"), L("health d444", "health", "health_p1073741831_d444")]),
         ("RG", "RH"), key="LR-5")
cgp = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve S4_t0 (callgrind tag)", "S4_t0", recorded=False),
                           cg("callgrind S4_t0", "S4_t0")], basis=BASIS_M4, row=488)
evaluate("LR-6 callgrind tag: the msolve record REMOVED, the callgrind record names <tag>.ms", cgp, ("RH",), key="LR-6")
cmp_ = resolve("anchor", [L("comparator", "comparator", "comparator", recorded=False), cj("anchor_S4", "anchor_S4"),
                          ms("anchor_comparator_random", "anchor_comparator_random", gb=True)], gate=True, row=478)
evaluate("LR-7 anchor-identity: the comparator record REMOVED", cmp_, ("RH",), key="LR-7")
bld = resolve("controls", [cj("ctl_S3", "ctl_S3", recorded=False), cj("ctl_raw_random", "ctl_raw_random", job="grid"), ms("ctl_planted_S3", "ctl_planted_S3")],
              gate=True, row=478)
evaluate("LR-8 a build child-job record REMOVED (the RH-6 (i) (22) shape)", bld, ("RH",), key="LR-8")

P("\n--- (2)-(3) FO-1 and RH-4 under gapattr")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("ok", "failed", "interrupted"):
        fo = ms("FO-1 %s %s" % (var_lab, wr), "S5_t0", report=rep, rc=1, pair=pr, p227=p227, exec_=False, escaped=True, foreign_write=wr,
                outcome="refused_to_start" if var_lab == "C" else "crashed")
        evaluate("FO-1 variant %s, foreign write %s" % (var_lab, wr), resolve("cells_m5", [fo], basis=BASIS_M5, designed=False),
                 ("RH",), ks=(1,), key="AJ1-FO1-%s-%s" % (var_lab, wr))
for lab, cb in (("H4-a a signal-raised exception caught by the callback's own try (RH-4 marks)", "caught"),
                ("H4-b an exception of the callback's own code, caught (RH-4 marks)", "caught"),
                ("H4-c a pending signal surfacing at the callback's entry, before its try: escapes, body not run", "escaped_before_body"),
                ("H4-d an exception escaping another after_in_parent callback, or the callback's epilogue after its body", "escaped_after_body")):
    evaluate(lab, resolve("cells_m5", [ms("msolve", "S5_t0", callback=cb)], basis=BASIS_M5, designed=False), ("RG", "RH"), ks=(1,), key=lab[:4])

P("\n--- (4) RG-1 residuals, HYPOTHETICAL supplying code (none found in the repository scan or the third-party text read)")
evaluate("X1 escaped child exits 99 by an unwinding-path SystemExit, variant C (empty report)",
         resolve("cells_m5", [ms("X1", "S5_t0", report="", rc=99, pair=None, p227=False, exec_=False, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X1")
evaluate("X10 escaped child itself execs, variant B",
         resolve("cells_m5", [ms("X10", "S5_t0", report="OK", rc=0, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X10")
evaluate("X6b counter on a second live child that execs while the real child escaped (variant B)",
         resolve("cells_m5", [ms("X6b", "S5_t0", report="OK", rc=1, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X6b")

P("\n--- census paths under gapattr (RH), each in a cells m = 5 package with one other class (B) launch")
census = [
    ("P-1..P-4 refused before fork (153-169)", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start")),
    ("P-6 ERR setrlimit 97", dict(report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-7 empty report 99", dict(report="", rc=99, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-8 soft != cap (98; return 232)", dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")),
    ("P-9 hard-only mismatch (98)", dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")),
    ("P-10..P-13 exec; ok / crashed / memory / timeout", dict()),
    ("exec raised after OK (99)", dict(report="OK", rc=99, exec_=False, outcome="crashed")),
    ("P-5a raise before fork", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, raised="MemoryError", tb=[(152, False)], rec_key=False)),
    ("P-16 raise at 181", dict(raised="KeyboardInterrupt", p227=False, exec_=False, report=None, rc=None, pair=None, tb=[(181, False)], rec_key=False)),
    ("P-14c raise after 227", dict(raised="KeyboardInterrupt", tb=[(244, True)], rec_key=True)),
]
for lab, kw in census:
    raw = "wrapper" if kw.get("raised") else "driver"
    evaluate("census " + lab, resolve("cells_m5", [ms("path", "S5_t0", **kw)], raw=raw, basis=BASIS_M5, designed=kw.get("raised") is None),
             ("RH",), ks=(1,), variants=("Mc",), key="census " + lab)

# ============================================================================ AJ-2 normal outcomes under gapattr
P("\n" + "=" * 110 + "\nAJ-2 NORMAL OUTCOMES OF EVERY LAUNCH KIND UNDER GAPATTR (RH): files written and their attribution")


def show_attr(label, pkg, rs="RH"):
    rule = {"RG": "RG4", "RH": "RH1"}[rs]
    att = attribute(pkg["rd"], sorted(pkg["files"]), dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    P("\n### " + label)
    for rel in sorted(att):
        h = att[rel]
        P("  %-52s writer %-44s -> %s" % (rel, pkg["files"][rel][:44], "; ".join("%s %s" % (c, i) for i, c in h) if h else "GAP"))
    OUT.setdefault("AJ2_attr", {})[label] = {r: att[r] for r in att}
    return evaluate(label + " [verdict]", pkg, ("RG", "RH"), variants=("Mr",), key="AJ2 " + label)


show_attr("N-1 cells m = 5 measured (S5 t0 retained, t1 not retained)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), ms("S5_t1", "S5_t1", retained=False)], basis=BASIS_M5, row=485))
show_attr("N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out)", resolve(
    "cells_m5", [ms("S5_t0 timeout", "S5_t0", rc=-9, outcome="timeout"), ms("S5_t1 memory", "S5_t1", rc=-11, outcome="memory_exhausted")], basis=BASIS_M5, row=485))
show_attr("N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488))
show_attr("N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="crashed", rc=1, partial_npz=True), cj("grid_raw_t1", "grid_raw_t1", job="grid"),
                 ms("raw_t1", "raw_t1")], basis=BASIS_M4, row=488))
a1_ = ms("S5_t1 attempt 1", "S5_t1", outcome="ssf", in_attempt_record=True)
a2_ = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
show_attr("N-5 SE-3 re-solve at S-1 (2 attempts)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1_, a2_], basis=BASIS_M5, row=485,
                                                         resolves=[("solver", "S5_t1", [a1_["lid"], a2_["lid"]])]))
h1 = L("health d222 attempt 1", "health", "health_p1073741831_d222", outcome="ssf", in_attempt_record=True)
h2 = L("health d222 attempt 2", "health", "health_p1073741831_d222", in_attempt_record=True)
show_attr("N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves", resolve(
    "controls_a1", [L("gp", "gp", "controls_a1_pari"), h1, h2, L("health d444", "health", "health_p1073741831_d444"),
                    cj("ctl_a1_torsion_S3_rq", "ctl_a1_torsion_S3_rq"), ms("ctl_a1_planted_torsion_S3_rq", "ctl_a1_planted_torsion_S3_rq")],
    gate=True, row=480, resolves=[("health", "health_p1073741831_d222", [h1["lid"], h2["lid"]])],
    extra_files=[("health/health-1073741831.json", "driver (a1_health 251)")]))
show_attr("N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)],
    basis=BASIS_M4, row=488))
show_attr("N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=-9, outcome="timeout")],
    basis=BASIS_M4, row=488))
show_attr("N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962)", resolve(
    "build", [cj("build_4111_S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True), cj("build_4111_S4", "build_4111_ecgfp5_shaped_S4_m4", cached=True)],
    basis=BASIS_BUILD, row=483))
show_attr("N-10 fixture4: uncached builds and solves", resolve(
    "fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481))
show_attr("N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C)", resolve(
    "cells_m4", [cj("grid_raw_t0 refused meta", "grid_raw_t0", job="grid", outcome="refused_meta"),
                 cj("grid_raw_t1 refused before fork", "grid_raw_t1", job="grid", created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start"),
                 cj("grid_raw_t2 ERR", "grid_raw_t2", job="grid", report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start"),
                 ms("raw_t3", "raw_t3")], basis=BASIS_M4, row=488))
show_attr("N-12 anchor-identity: comparator, uncached build, gb_only solves", resolve(
    "anchor", [L("comparator", "comparator", "comparator"), cj("anchor_S4", "anchor_S4"), ms("anchor_v2_t0", "anchor_v2_t0", gb=True),
               ms("anchor_comparator_system", "anchor_comparator_system", gb=True)], gate=True, row=478))
show_attr("N-13 Z-C5 (no launch; directories only)", resolve("cells_m5", [], basis=BASIS_M5, row=486))

P("\n--- AJ-2 (1) LISTING CHECK under gapattr RH-1 AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RH1", GATE, label="(gapattr)")

# ============================================================================ AJ-3 cap-mismatch outcomes and RKR-4 (b) rows
P("\n" + "=" * 110 + "\nAJ-3 CAP-MISMATCH OUTCOMES (RH-2) AND THE RKR-4 (b) PASS / PASS_ZL ROWS: RF vs RG vs RH")
p8 = dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")
p9 = dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")
for kind, basis in (("cells_m5", BASIS_M5), ("cells_m4", BASIS_M4), ("build", BASIS_BUILD)):
    evaluate("CM %s: every launch P-8" % kind, resolve(kind, [ms("P-8 a", "t0", **p8), ms("P-8 b", "t1", **p8)], basis=basis), variants=("Mr",), key="CM %s P8" % kind)
    evaluate("CM %s: every launch P-9" % kind, resolve(kind, [ms("P-9 a", "t0", **p9), ms("P-9 b", "t1", **p9)], basis=basis), variants=("Mr",), key="CM %s P9" % kind)
    evaluate("CM %s: mixture, one P-9 launch and one measured launch (pair = cap, exec)" % kind,
             resolve(kind, [ms("P-9", "t0", **p9), ms("measured", "t1")], basis=basis), variants=("Mr",), key="CM %s mix" % kind)
evaluate("CM controls (gate): one P-9 build child", resolve("controls", [cj("P-9 build", "ctl_S3", **p9), ms("ok", "ctl_planted_S3")], gate=True, row=478),
         variants=("Mr",), key="CM controls")
rows = [
    ("478 G1..G4 completed_valid (fixture shape: uncached builds, raw grids, solves, callgrind)", resolve(
        "fixture", [cj("fixture_S3", "fixture_S3"), cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid"), ms("fx_reg0_raw_x", "fx_reg0_raw_x"),
                    cg("cg fx_reg0_raw_x", "fx_reg0_raw_x"), ms("fx_reg0_S3", "fx_reg0_S3"), cg("cg fx_reg0_S3", "fx_reg0_S3")], gate=True, row=478)),
    ("480 controls_a1 image", resolve("controls_a1", [L("gp", "gp", "controls_a1_pari"), L("health", "health", "health_p1073741831_d222"),
                                                      cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")], gate=True, row=480,
                                      extra_files=[("health/health-1073741831.json", "driver (a1_health 251)")])),
    ("481 fixture4 launched", resolve("fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481)),
    ("482 Z-F4 (zero call)", resolve("fixture4", [], row=482)),
    ("483 build (cached)", resolve("build", [cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True)], basis=BASIS_BUILD, row=483)),
    ("485 cells m = 5 measured", resolve("cells_m5", [ms("S5_t0", "S5_t0")], basis=BASIS_M5, row=485)),
    ("485 cells m = 5 measured, one SE-3 re-solve", pb3),
    ("486 Z-C5", resolve("cells_m5", [], basis=BASIS_M5, row=486)),
    ("488 cells m = 4", pb2),
    ("488 cells m = 4, callgrind child failed", resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"),
                                                                     cg("cg raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)], basis=BASIS_M4, row=488)),
    ("489 aggregate v2", resolve("aggregate", [], basis="X-10 aggregate_a1", row=489)),
]
for lab, pkg in rows:
    evaluate("RKR-4 (b) row " + lab, pkg, ("RF", "RG", "RH"), variants=("Mr",), key="row " + lab)

with open(os.path.join(SCR, "rt_eval.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rt_eval.json with %d keys" % len(OUT))
````

### `rt_eval.v2.py`

- sha256: `daab8b7626c768fa0938dff6f1f1ae6bd995523942599f1c366b33bf449fe9b3`
- bytes: 49454; lines: 835
- argv: `ran once; the argv form retained is PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rt_eval.py > rt_eval.out (cwd <scratch>/rt_94cc33), the file then being the current rt_eval.py; its output is kept as rt_eval.v2.run1.out`
- role: Second version. The run failed with TypeError (L() got multiple values for keyword argument 'in_raw'); no JSON was written.

````text
#!/usr/bin/env python3
"""TASK-20260924-94cc33 rule evaluator (scratch; zero runs). One method for AJ-0..AJ-3, unchanged across objects.

It imports only json, os, re and itertools. It reads two scratch files written earlier by this review
(listing.json: the directory listings of the four archived r3 gate packages; specout.json: the "out" value of
each child/*.spec.json). It imports no module of any scanned tree and no third-party module.

LAYER 1 (file level) - attribution of every file under child/, solver/, health/, comparator/, pari/ to launch
records, under three encodings of the attribution text:
  RG4   childend RG-4 (b) AS WORDED: stdout_path / stderr_path; a path the argv names exactly; a file under a
        directory the argv names and no other record's argv names; the non-launch list.
  RH1   gapattr RH-1 (i)-(vi) AS WORDED, with the same non-launch list.
  RH1w  RH1 with clause (v) WEAKENED to "every file under child/ is attributed to some launch record" (CRG-4 (e)).
A file with no attribution and not on the non-launch list is a RECORDER GAP.

LAYER 2 (package level) - verdicts under the rule texts, encoded as functions:
  RK   readbackclose RK-1 (a)/(b) and RK-3 (b) AS WORDED (RL-3 gaps gate nothing).
  RF   failclosed AS WORDED: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 gap = a file of the RL-3 globs whose
       writing launch (truth) has no launch record.
  RG   childend: RF with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b) (layer 1 RG4; a gap makes the verdict FAIL).
  RH   gapattr: RG with RH-1 (layer 1 RH1), RH-2 (a)/(b) and RH-4.
  RHw  RH with RH-1 (v) weakened (layer 1 RH1w).
Each package is read under two manifest variants of the requested cap (v2_check_run.py 64):
  Mr = r3 base (r3_run_wrapper.py 550: raw-result.json envelope; None when the wrapper wrote raw-result.json);
  Mc = an r4 wrapper recording the requested cap independently of raw-result.json.
Definitions (failclosed 604-621), evaluated on TRUTH facts: FAIL-OPEN iff the verdict is PASS or PASS_ZL while one
of (i)..(v) holds. (ii) is evaluated under two readings of "recorded pair": LR = in a launch record; ANY = in any
RB-2 source (launch record, the launch's own child/*.meta.json, its RB-1 attempt record, driver-written raw).
PLANNED-BASIS REFUSAL iff the outcome is a planned basis outcome (driver-logic outcome as the rule set reads
RF-0 (b), acted on by a dependant's frozen logic or listed in RFR-2's enumeration) AND designed AND FAIL.
"""
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "<sys.executable>"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE_SET = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}          # RG-1 (c)
RENAMED = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
OUT = {}


def P(*a):
    print(*a)


# ============================================================================ LAYER 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 inputs / 251 report)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93 script)"
    return None


def attribute(rd, rels, dirs, records, specs, events, rule):
    """rels: paths relative to rd (files in the five directories); dirs: absolute directory paths present;
    records: dicts id, order, argv, stdout, stderr, child_end; specs: {absolute spec path: dict or None};
    events: dicts dir, tag, renamed_files. Returns {rel: [(record id, clause)]}."""
    names = {}
    for r in records:
        for a in set(r["argv"]):
            names[a] = names.get(a, 0) + 1
    res = {}
    for rel in rels:
        p = rd + "/" + rel
        hits = []
        for r in records:
            if p == r["stdout"] or p == r["stderr"]:
                hits.append((r["id"], "(i)" if rule != "RG4" else "stdout/stderr"))
            if p in r["argv"]:
                hits.append((r["id"], "(ii)" if rule != "RG4" else "argv exact"))
            if rule in ("RH1", "RH1w"):
                for a in r["argv"]:
                    if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                        hits.append((r["id"], "(iii)"))
            for a in r["argv"]:
                if a in dirs and p.startswith(a.rstrip("/") + "/") and names.get(a, 0) == 1:
                    hits.append((r["id"], "(iv)" if rule != "RG4" else "argv directory"))
            if rule == "RH1" and r.get("child_end") == "exec" and r["argv"]:
                m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
                if m:
                    sp = specs.get(r["argv"][-1])
                    o = rd + "/child/" + m.group("tag")
                    if isinstance(sp, dict) and isinstance(sp.get("out"), str) and sp["out"] == o and p in (o + ".npz", o + ".meta.json"):
                        hits.append((r["id"], "(v)"))
        if rule == "RH1w" and rel.startswith("child/") and records:
            hits.append(("<some launch record>", "(v) weakened"))
        if rule == "RH1":
            d, _, name = rel.partition("/")
            m = RENAMED.fullmatch(name)
            if m and d in ("solver", "health"):
                tag, k = m.group("tag"), int(m.group("k"))
                ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
                same = sorted((r for r in records if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["order"])
                if ev and len(same) >= k:
                    hits.append((same[k - 1]["id"], "(vi) k=%d" % k))
        if not hits and nonlaunch(rel):
            hits.append(("-", nonlaunch(rel)))
        res[rel] = hits
    return res


# ============================================================================ LAYER 2: launches, files, packages
def L(lid, site, tag, **kw):
    d = dict(lid=lid, site=site, tag=tag, created=True, p227=True, exec_=True, report="OK", rc=0, pair=CP,
             raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False, foreign_write=None,
             recorded=True, callback="normal", fired=None, new_pids=None, opened=None, t_en=None, value=None,
             order=0, outcome="ok", job=None, cached=False, dirn=None, gb=False, cg_out_left=False,
             partial_npz=False, in_attempt_record=False, in_raw=False, retained=True, files_override=None)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["opened"] is None:
        d["opened"] = d["created"]
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if d["dirn"] is None:
        d["dirn"] = {"childjob": "child", "msolve": "solver", "callgrind": "solver", "comparator": "comparator",
                     "health": "health", "gp": "pari"}[site]
    return d


def launch_paths(l, rd):
    """argv, stdout_path, stderr_path exactly as the frozen call sites build them."""
    t, dn = l["tag"], rd + "/" + l["dirn"]
    s = l["site"]
    if s == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if s in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"]
                + (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if s == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2",
                 "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if s == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if s == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(s)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch (relative paths, truth writer)."""
    if l["files_override"] is not None:
        return list(l["files_override"])
    t, dn, s, me = l["tag"], l["dirn"], l["site"], l["lid"]
    f = []
    opened = l["created"] and l["report"] is not None       # the fork child opened stdout/stderr (188-189)
    if s == "childjob":
        f.append((dn + "/" + t + ".spec.json", ("driver", "v2_driver 98-99")))
        if opened:
            f += [(dn + "/" + t + ".stdout", (me, "")), (dn + "/" + t + ".stderr", (me, ""))]
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f += [(dn + "/" + t + ".npz", (me, "v2_child 38")), (dn + "/" + t + ".meta.json", (me, "v2_child 41"))]
                else:
                    f += [(dn + "/" + t + ".meta.json", (me, "v2_child 104; .npz removed v2_driver 144"))]
            elif l["outcome"] == "refused_meta":
                f += [(dn + "/" + t + ".meta.json", (me, "v2_child 68/80"))]
            elif l["partial_npz"]:
                f += [(dn + "/" + t + ".npz", (me, "partial, v2_child 38/100"))]
    elif s in ("msolve", "health"):
        if l["retained"]:
            f.append((dn + "/" + t + ".ms", ("driver", "v2_driver 162 / a1_health 143")))
        if opened:
            f += [(dn + "/" + t + ".ms.log", (me, "")), (dn + "/" + t + ".ms.err", (me, ""))]
        if l["exec_"] and l["outcome"] in ("ok", "ssf"):
            f.append((dn + "/" + t + ".ms.out", (me, "")))
    elif s == "callgrind":
        if opened:
            f += [(dn + "/" + t + ".callgrind.stdout", (me, "")), (dn + "/" + t + ".callgrind.stderr", (me, ""))]
        if l["cg_out_left"]:
            f.append((dn + "/" + t + ".callgrind.out", (me, "left by v2_solver 521-524")))
    elif s == "comparator":
        if opened:
            f += [(dn + "/stdout.log", (me, "")), (dn + "/stderr.log", (me, ""))]
        if l["exec_"] and l["outcome"] == "ok":
            f += [(dn + "/" + x, (me, "k4a 279-281, 318")) for x in ("anchor25_random.ms", "anchor25_planted.ms",
                                                                      "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json")]
    elif s == "gp":
        f.append((dn + "/" + t + ".gp", ("driver", "a1_pari 91-93")))
        if opened:
            f += [(dn + "/" + t + ".gp.stdout", (me, "")), (dn + "/" + t + ".gp.stderr", (me, ""))]
    return f


def resolve(kind, launches, raw="driver", gate=False, basis=None, row=None, designed=True, rd=None, resolves=(),
            raw_pairs=True, recording_failure=False, extra_files=()):
    """Build a package. resolves: (site_dir, tag, [launch ids in attempt order]) SE-3 / HR-3 re-solves: every
    attempt but the last has its .ms.out/.ms.log/.ms.err renamed to <name>.ssf-attempt<k> (r3_resolve 224-238)
    and listed under renamed_files["attempt<k>"] of the event (310)."""
    rd = rd or RUNS + "/RUN-X"
    files, events = {}, []
    for i, l in enumerate(launches):
        l["order"] = i
        for rel, w in files_of(l):
            files[rel] = w
    for dn, tag, ids in resolves:
        ev = {"dir": dn, "tag": tag, "renamed_files": {}}
        for k, lid in enumerate(ids[:-1], start=1):
            rn = {}
            for ext in (".ms.out", ".ms.log", ".ms.err"):
                src = dn + "/" + tag + ext
                if src in files:
                    w = files.pop(src)
                    files[src + ".ssf-attempt%d" % k] = (lid, "renamed, r3_resolve 234")
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"renamed": True}
                else:
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"absent": True}
            ev["renamed_files"]["attempt%d" % k] = rn
            # the next attempt rewrites the unrenamed names
            nxt = next(x for x in launches if x["lid"] == ids[k])
            for rel, w in files_of(nxt):
                files[rel] = w
        events.append(ev)
    for rel, w in extra_files:
        files[rel] = w
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, designed=designed, rd=rd,
                files=files, events=events, raw_pairs=raw_pairs, recording_failure=recording_failure)


# ---------------------------------------------------------------- recorded values
def rk1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def rf1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return l["pair"]


def child_end(l, rs):
    if rs in ("RH", "RHw") and l["callback"] == "caught":
        return "undetermined"
    cc = rf1(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["opened"] and l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE_SET:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):
    cc = rk1(l) if rs == "RK" else rf1(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


# ---------------------------------------------------------------- package-level rules
def records_for_layer1(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = launch_paths(l, pkg["rd"])
        out.append({"id": l["lid"], "order": l["order"], "argv": argv, "stdout": so, "stderr": se,
                    "child_end": child_end(l, rs) if rs in ("RG", "RH", "RHw") else None})
    return out


def specs_of(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["site"] == "childjob":
            path = pkg["rd"] + "/child/" + l["tag"] + ".spec.json"
            if ("child/" + l["tag"] + ".spec.json") in pkg["files"]:
                sp[path] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"], "to_cache": l["cached"]}
    return sp


def dirs_of(pkg):
    return {pkg["rd"] + "/" + d for d in FIVE}


def gaps(pkg, rs):
    rels = sorted(pkg["files"])
    if rs == "RK":
        return []
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob_hit = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            writer = w[0]
            if glob_hit and writer != "driver" and writer not in recorded:
                g.append(rel)
        return sorted(g)
    rule = {"RG": "RG4", "RH": "RH1", "RHw": "RH1w"}[rs]
    att = attribute(pkg["rd"], rels, dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    return sorted(r for r, h in att.items() if not h)


def pairs_collected(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(rec_pair(l))                                       # RL-3 (d)
        if l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"]:
            ps.append(l["pair"])                                         # RB-2 (b): the child's own getrlimit
        if l["in_attempt_record"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (c)
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (a)
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = pairs_collected(pkg)
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    five = bool(pkg["files"])
    r4ok = not pkg["recording_failure"]
    zl_kinds = ("cells_m5", "fixture4")
    if rs == "RK":
        if not items and r4ok:
            return "PASS"
        if not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(rf1(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs in ("RG", "RH", "RHw"):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    g = gaps(pkg, rs)
    if (not items and r4ok and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign
            and not g and not undet):
        return "PASS"
    if (not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok and rw == "driver"
            and pkg["kind"] in zl_kinds and not foreign):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    files = pkg["files"]
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (rk1(l) if rs == "RK" else rf1(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and l["pair"] == CP and (
                l["in_attempt_record"] or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in files and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            detected = (rs != "RK" and l["foreign_write"] == "ok") or (rs in ("RG", "RH", "RHw") and rec and child_end(l, rs) == "undetermined")
            if not detected:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs in ("RG", "RH", "RHw") and infra_stop(pkg):
        return False
    if rs in ("RH", "RHw") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (removed)"
    cc = rk1(l) if rs == "RK" else rf1(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs in ("RG", "RH", "RHw"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii) created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs in ("RG", "RH", "RHw") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant foreign-process record; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def evaluate(label, pkg, rule_sets=("RF", "RG", "RH"), ks=(0,), variants=("Mr", "Mc"), extra_b=None, key=None):
    P("\n### " + label)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-24s] %-3s %s" % (l["lid"][:24], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = pkg
            if k:
                other = [L("otherB%d" % j, "msolve", "otherB_t%d" % j, in_raw=True) for j in range(k)]
                q = resolve(pkg["kind"], [dict(x) for x in pkg["launches"]] + other, raw=pkg["raw"], gate=pkg["gate"],
                            basis=pkg["basis"], row=pkg["row"], designed=pkg["designed"], rd=pkg["rd"],
                            resolves=[(e["dir"], e["tag"], None) for e in []], raw_pairs=pkg["raw_pairs"],
                            recording_failure=pkg["recording_failure"])
                q["files"].update({r: w for r, w in pkg["files"].items()})
                q["events"] = pkg["events"]
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row " + str(q["row"]))))
            if rs in ("RG", "RH", "RHw") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RHw") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-18s defs %-24s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var),
                         "definitions": dfs, "fail_open": fo, "planned_basis_refusal": pb, "gaps": g})
    OUT[key or label] = rows
    return rows


# ============================================================================ helpers for objects
def ms(lid, tag, **kw):
    return L(lid, "msolve", tag, in_raw=True, **kw)


def cj(lid, tag, job="build", **kw):
    return L(lid, "childjob", tag, job=job, in_raw=True, **kw)


def cg(lid, tag, **kw):
    return L(lid, "callgrind", tag, in_raw=True, **kw)


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)"
BASIS_M4 = "X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003, 1068-1075)"


# ============================================================================ AJ-0 KNOWN-ANSWER CONTROL
P("=" * 110 + "\nAJ-0 KNOWN-ANSWER CONTROL (CRG-4 (a)-(e))")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK), RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False)
evaluate("KA-a1 P-16 (v2_solver 181 CALL then STORE_FAST pid; raise leaves the driver: raw wrapper-written)",
         resolve("cells_m5", [p16], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a1")
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False)
evaluate("KA-a2 P-F2 after P-14a (release raises in run_child's finally over a raise at 214)",
         resolve("cells_m5", [pf2], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a2")
evaluate("KA-a3 W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper 491-505)",
         resolve("cells_m5", [], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), key="KA-a3")

P("\n--- (b) failclosed AS WORDED (RF): FO-1, foreign-file write failed / interrupted")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (var_lab, wr, rc), "S5_t0", report=rep, rc=rc, pair=pr, p227=p227, exec_=False,
                    escaped=True, foreign_write=wr, outcome="refused_to_start" if var_lab == "C" else "crashed")
            evaluate("KA-b FO-1 variant %s, foreign write %s, escaped exit %d" % (var_lab, wr, rc),
                     resolve("cells_m5", [fo], basis=BASIS_M5, designed=False), ("RF", "RG", "RH"), ks=(0, 1),
                     key="KA-b-%s-%s-%d" % (var_lab, wr, rc))

P("\n--- (c) childend AS WORDED (RG): PB-2 and PB-3 (RF and RH for contrast)")
pb2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve raw_t0", "raw_t0"),
                           cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488)
evaluate("KA-c1 PB-2 cells m = 4, raw_grid child leaves child/grid_raw_t0.meta.json (v2_driver 1161 -> 133-147)", pb2, key="KA-c1")
a1 = ms("S5_t1 attempt 1 (SSF)", "S5_t1", outcome="ssf", in_attempt_record=True)
a2 = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
pb3 = resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1, a2], basis=BASIS_M5, row=485, resolves=[("solver", "S5_t1", [a1["lid"], a2["lid"]])])
evaluate("KA-c2 PB-3 cells m = 5 with one SE-3 re-solve at S-1 (r3_resolve 224-238, 310)", pb3, key="KA-c2")

# ---------------------------------------------------------------- (d) and AJ-2 (1): the listing check
listing = json.load(open(os.path.join(SCR, "listing.json")))
specout = json.load(open(os.path.join(SCR, "specout.json")))


def reconstruct(pk):
    """CRG-9 reconstruction by the frozen code's naming: child/<tag>.spec.json -> child job; solver/<tag>.ms.log ->
    msolve; solver/<tag>.callgrind.stdout -> callgrind; comparator/stdout.log -> comparator; health/<tag>.ms.log ->
    health msolve; pari/<tag>.gp.stdout -> gp. child_end "exec" is reconstructed for a child job whose <out>.meta.json
    or <out>.npz exists (only v2_child writes them, after exec) and for every launch whose output file exists."""
    rd = RUNS + "/" + pk
    ents = listing["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    dirs = {rd + "/" + e["path"].rstrip("/") for e in ents if e["type"] == "dir"}
    recs, order = [], 0
    specs = {}
    for rel, v in specout[pk]["specs"].items():
        specs[rd + "/" + rel] = {"out": v.get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = argv = so = se = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid = "childjob:" + t
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out", "<-P|-g>", "1"]
            so, se, ce, lid = rd + "/" + d + "/" + name, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v",
                    "2", "-t", "1", "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se, ce, lid = rd + "/solver/" + name, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t
        elif rel == "comparator/stdout.log":
            argv, so, se, ce, lid = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se, ce, lid = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/pari/" + name, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t
        if lid:
            recs.append({"id": lid, "order": order, "argv": argv, "stdout": so, "stderr": se, "child_end": ce})
            order += 1
    return rd, rels, dirs, recs, specs


def listing_check(rule, pkgs, drop=None, label=""):
    P("\n--- listing check under %s %s" % (rule, label))
    res = {}
    for pk in pkgs:
        rd, rels, dirs, recs, specs = reconstruct(pk)
        if drop:
            recs = [r for r in recs if r["id"] != drop]
        att = attribute(rd, rels, dirs, recs, specs, [], rule)
        g = [r for r in rels if not att[r]]
        by_clause = {}
        for r, h in att.items():
            for (_i, c) in (h[:1] if h else [("-", "NONE (gap)")]):
                by_clause[c] = by_clause.get(c, 0) + 1
        per_rec = {}
        for r, h in att.items():
            for (i, c) in h:
                per_rec.setdefault(i, []).append(c)
        meta_g = [x for x in g if x.endswith(".meta.json")]
        P("  %s: %d files in the five directories, %d reconstructed launch records (%s); files by first clause %s"
          % (pk, len(rels), len(recs), dict(sorted({k: sum(1 for r in recs if r["id"].startswith(k)) for k in ("childjob", "msolve", "callgrind", "comparator", "gp")}.items())),
             dict(sorted(by_clause.items()))))
        P("    unattributed: %d (child/*.meta.json %d; child/*.npz %d; other %d)" % (len(g), len(meta_g), sum(1 for x in g if x.endswith(".npz")),
                                                                                  len(g) - len(meta_g) - sum(1 for x in g if x.endswith(".npz"))))
        for x in g:
            P("      GAP " + x)
        res[pk] = {"n_files": len(rels), "n_records": len(recs), "gaps": g, "first_clause_counts": by_clause,
                   "attribution": {r: att[r] for r in rels}}
    OUT["listing_%s%s" % (rule, "_drop_" + drop if drop else "")] = res
    return res


GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
P("\n--- (d) LISTING CHECK under childend RG-4 (b) AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RG4", GATE, label="(childend)")

P("\n--- (e) gapattr with RH-1 (v) WEAKENED vs AS WORDED, one child-job launch record removed")
P("  (e0) file level on RUN-GFPN-bfe956 with the record of childjob:ctl_S3 removed:")
listing_check("RH1w", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(weakened)")
listing_check("RH1", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(worded)")
e1 = resolve("controls", [cj("ctl_identity_n3", "ctl_identity_n3", in_raw=False), cj("ctl_raw_random", "ctl_raw_random", job="grid", in_raw=False),
                          cj("ctl_S3", "ctl_S3", in_raw=False, recorded=False), ms("ctl_planted_S3", "ctl_planted_S3", in_raw=False)],
             gate=True, row=478, raw_pairs=False, rd=RUNS + "/RUN-G4-copy")
evaluate("KA-e1 controls (G4 shape, raw carries no pair), child-job record of ctl_S3 REMOVED (build ok: meta carries its pair)",
         e1, ("RH", "RHw"), key="KA-e1")
e2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid", outcome="crashed", partial_npz=True, recorded=False, in_raw=False),
                          ms("msolve S4_t0", "S4_t0"), cj("grid_raw_t1 child", "grid_raw_t1", job="grid"), ms("msolve raw_t1", "raw_t1")],
             basis=BASIS_M4, row=488)
evaluate("KA-e2 cells m = 4, raw_grid child of target 0 crashed after exec (partial .npz, no meta), its record REMOVED",
         e2, ("RH", "RHw"), key="KA-e2")

# ============================================================================ AJ-1 under gapattr
P("\n" + "=" * 110 + "\nAJ-1 FAIL-OPEN SEARCH UNDER GAPATTR (RH), RG for contrast")
P("\n--- (1) lost launch records whose files another record's positive source names")


def resolved_cell(drop=None, n=2, site="msolve", dn="solver", tag="S5_t1", kind="cells_m5", extra=()):
    atts = [L("%s attempt %d" % (tag, k), site, tag, outcome="ssf" if k < n else "ok", in_attempt_record=True, in_raw=(k == n),
              recorded=(drop is None or k not in drop)) for k in range(1, n + 1)]
    lau = [ms("S5_t0", "S5_t0")] + list(extra) + atts
    return resolve(kind, lau, basis=BASIS_M5 if kind == "cells_m5" else "X-02 / X-13 (controls_a1 image)", row=485 if kind == "cells_m5" else 480,
                   gate=kind == "controls_a1", resolves=[(dn, tag, [a["lid"] for a in atts])])


evaluate("LR-0 SE-3 re-solve at S-1 (2 attempts), every launch record present", resolved_cell(), ("RG", "RH"), key="LR-0")
evaluate("LR-1 SE-3 re-solve at S-1 (2 attempts), the FINAL attempt's launch record REMOVED", resolved_cell(drop={2}), ("RG", "RH"), key="LR-1")
evaluate("LR-2 SE-3 re-solve at S-1 (2 attempts), attempt 1's launch record REMOVED", resolved_cell(drop={1}), ("RG", "RH"), key="LR-2")
evaluate("LR-3 SE-3 re-solve at S-1 (3 attempts), attempt 2's launch record REMOVED", resolved_cell(drop={2}, n=3), ("RG", "RH"), key="LR-3")
evaluate("LR-4 SE-3 re-solve at S-1 (3 attempts), attempts 2 and 3 REMOVED", resolved_cell(drop={2, 3}, n=3), ("RG", "RH"), key="LR-4")
evaluate("LR-5 HR-3 re-solve at S-2 in controls_a1 (2 attempts), the final attempt's record REMOVED",
         resolved_cell(drop={2}, site="health", dn="health", tag="health_p1073741831_d222", kind="controls_a1",
                       extra=[L("gp", "gp", "controls_a1_pari"), L("health d444", "health", "health_p1073741831_d444")]),
         ("RG", "RH"), key="LR-5")
cgp = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve S4_t0 (callgrind tag)", "S4_t0", recorded=False),
                           cg("callgrind S4_t0", "S4_t0")], basis=BASIS_M4, row=488)
evaluate("LR-6 callgrind tag: the msolve record REMOVED, the callgrind record names <tag>.ms", cgp, ("RH",), key="LR-6")
cmp_ = resolve("anchor", [L("comparator", "comparator", "comparator", recorded=False), cj("anchor_S4", "anchor_S4"),
                          ms("anchor_comparator_random", "anchor_comparator_random", gb=True)], gate=True, row=478)
evaluate("LR-7 anchor-identity: the comparator record REMOVED", cmp_, ("RH",), key="LR-7")
bld = resolve("controls", [cj("ctl_S3", "ctl_S3", recorded=False), cj("ctl_raw_random", "ctl_raw_random", job="grid"), ms("ctl_planted_S3", "ctl_planted_S3")],
              gate=True, row=478)
evaluate("LR-8 a build child-job record REMOVED (the RH-6 (i) (22) shape)", bld, ("RH",), key="LR-8")

P("\n--- (2)-(3) FO-1 and RH-4 under gapattr")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("ok", "failed", "interrupted"):
        fo = ms("FO-1 %s %s" % (var_lab, wr), "S5_t0", report=rep, rc=1, pair=pr, p227=p227, exec_=False, escaped=True, foreign_write=wr,
                outcome="refused_to_start" if var_lab == "C" else "crashed")
        evaluate("FO-1 variant %s, foreign write %s" % (var_lab, wr), resolve("cells_m5", [fo], basis=BASIS_M5, designed=False),
                 ("RH",), ks=(1,), key="AJ1-FO1-%s-%s" % (var_lab, wr))
for lab, cb in (("H4-a a signal-raised exception caught by the callback's own try (RH-4 marks)", "caught"),
                ("H4-b an exception of the callback's own code, caught (RH-4 marks)", "caught"),
                ("H4-c a pending signal surfacing at the callback's entry, before its try: escapes, body not run", "escaped_before_body"),
                ("H4-d an exception escaping another after_in_parent callback, or the callback's epilogue after its body", "escaped_after_body")):
    evaluate(lab, resolve("cells_m5", [ms("msolve", "S5_t0", callback=cb)], basis=BASIS_M5, designed=False), ("RG", "RH"), ks=(1,), key=lab[:4])

P("\n--- (4) RG-1 residuals, HYPOTHETICAL supplying code (none found in the repository scan or the third-party text read)")
evaluate("X1 escaped child exits 99 by an unwinding-path SystemExit, variant C (empty report)",
         resolve("cells_m5", [ms("X1", "S5_t0", report="", rc=99, pair=None, p227=False, exec_=False, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X1")
evaluate("X10 escaped child itself execs, variant B",
         resolve("cells_m5", [ms("X10", "S5_t0", report="OK", rc=0, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X10")
evaluate("X6b counter on a second live child that execs while the real child escaped (variant B)",
         resolve("cells_m5", [ms("X6b", "S5_t0", report="OK", rc=1, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X6b")

P("\n--- census paths under gapattr (RH), each in a cells m = 5 package with one other class (B) launch")
census = [
    ("P-1..P-4 refused before fork (153-169)", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start")),
    ("P-6 ERR setrlimit 97", dict(report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-7 empty report 99", dict(report="", rc=99, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-8 soft != cap (98; return 232)", dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")),
    ("P-9 hard-only mismatch (98)", dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")),
    ("P-10..P-13 exec; ok / crashed / memory / timeout", dict()),
    ("exec raised after OK (99)", dict(report="OK", rc=99, exec_=False, outcome="crashed")),
    ("P-5a raise before fork", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, raised="MemoryError", tb=[(152, False)], rec_key=False)),
    ("P-16 raise at 181", dict(raised="KeyboardInterrupt", p227=False, exec_=False, report=None, rc=None, pair=None, tb=[(181, False)], rec_key=False)),
    ("P-14c raise after 227", dict(raised="KeyboardInterrupt", tb=[(244, True)], rec_key=True)),
]
for lab, kw in census:
    raw = "wrapper" if kw.get("raised") else "driver"
    evaluate("census " + lab, resolve("cells_m5", [ms("path", "S5_t0", **kw)], raw=raw, basis=BASIS_M5, designed=kw.get("raised") is None),
             ("RH",), ks=(1,), variants=("Mc",), key="census " + lab)

# ============================================================================ AJ-2 normal outcomes under gapattr
P("\n" + "=" * 110 + "\nAJ-2 NORMAL OUTCOMES OF EVERY LAUNCH KIND UNDER GAPATTR (RH): files written and their attribution")


def show_attr(label, pkg, rs="RH"):
    rule = {"RG": "RG4", "RH": "RH1"}[rs]
    att = attribute(pkg["rd"], sorted(pkg["files"]), dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    P("\n### " + label)
    for rel in sorted(att):
        h = att[rel]
        P("  %-52s writer %-44s -> %s" % (rel, ("%s %s" % pkg["files"][rel])[:44], "; ".join("%s %s" % (c, i) for i, c in h) if h else "GAP"))
    OUT.setdefault("AJ2_attr", {})[label] = {r: att[r] for r in att}
    return evaluate(label + " [verdict]", pkg, ("RG", "RH"), variants=("Mr",), key="AJ2 " + label)


show_attr("N-1 cells m = 5 measured (S5 t0 retained, t1 not retained)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), ms("S5_t1", "S5_t1", retained=False)], basis=BASIS_M5, row=485))
show_attr("N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out)", resolve(
    "cells_m5", [ms("S5_t0 timeout", "S5_t0", rc=-9, outcome="timeout"), ms("S5_t1 memory", "S5_t1", rc=-11, outcome="memory_exhausted")], basis=BASIS_M5, row=485))
show_attr("N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488))
show_attr("N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="crashed", rc=1, partial_npz=True), cj("grid_raw_t1", "grid_raw_t1", job="grid"),
                 ms("raw_t1", "raw_t1")], basis=BASIS_M4, row=488))
a1_ = ms("S5_t1 attempt 1", "S5_t1", outcome="ssf", in_attempt_record=True)
a2_ = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
show_attr("N-5 SE-3 re-solve at S-1 (2 attempts)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1_, a2_], basis=BASIS_M5, row=485,
                                                         resolves=[("solver", "S5_t1", [a1_["lid"], a2_["lid"]])]))
h1 = L("health d222 attempt 1", "health", "health_p1073741831_d222", outcome="ssf", in_attempt_record=True)
h2 = L("health d222 attempt 2", "health", "health_p1073741831_d222", in_attempt_record=True)
show_attr("N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves", resolve(
    "controls_a1", [L("gp", "gp", "controls_a1_pari"), h1, h2, L("health d444", "health", "health_p1073741831_d444"),
                    cj("ctl_a1_torsion_S3_rq", "ctl_a1_torsion_S3_rq"), ms("ctl_a1_planted_torsion_S3_rq", "ctl_a1_planted_torsion_S3_rq")],
    gate=True, row=480, resolves=[("health", "health_p1073741831_d222", [h1["lid"], h2["lid"]])],
    extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))]))
show_attr("N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)],
    basis=BASIS_M4, row=488))
show_attr("N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=-9, outcome="timeout")],
    basis=BASIS_M4, row=488))
show_attr("N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962)", resolve(
    "build", [cj("build_4111_S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True), cj("build_4111_S4", "build_4111_ecgfp5_shaped_S4_m4", cached=True)],
    basis=BASIS_BUILD, row=483))
show_attr("N-10 fixture4: uncached builds and solves", resolve(
    "fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481))
show_attr("N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C)", resolve(
    "cells_m4", [cj("grid_raw_t0 refused meta", "grid_raw_t0", job="grid", outcome="refused_meta"),
                 cj("grid_raw_t1 refused before fork", "grid_raw_t1", job="grid", created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start"),
                 cj("grid_raw_t2 ERR", "grid_raw_t2", job="grid", report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start"),
                 ms("raw_t3", "raw_t3")], basis=BASIS_M4, row=488))
show_attr("N-12 anchor-identity: comparator, uncached build, gb_only solves", resolve(
    "anchor", [L("comparator", "comparator", "comparator"), cj("anchor_S4", "anchor_S4"), ms("anchor_v2_t0", "anchor_v2_t0", gb=True),
               ms("anchor_comparator_system", "anchor_comparator_system", gb=True)], gate=True, row=478))
show_attr("N-13 Z-C5 (no launch; directories only)", resolve("cells_m5", [], basis=BASIS_M5, row=486))

P("\n--- AJ-2 (1) LISTING CHECK under gapattr RH-1 AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RH1", GATE, label="(gapattr)")

# ============================================================================ AJ-3 cap-mismatch outcomes and RKR-4 (b) rows
P("\n" + "=" * 110 + "\nAJ-3 CAP-MISMATCH OUTCOMES (RH-2) AND THE RKR-4 (b) PASS / PASS_ZL ROWS: RF vs RG vs RH")
p8 = dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")
p9 = dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")
for kind, basis in (("cells_m5", BASIS_M5), ("cells_m4", BASIS_M4), ("build", BASIS_BUILD)):
    evaluate("CM %s: every launch P-8" % kind, resolve(kind, [ms("P-8 a", "t0", **p8), ms("P-8 b", "t1", **p8)], basis=basis), variants=("Mr",), key="CM %s P8" % kind)
    evaluate("CM %s: every launch P-9" % kind, resolve(kind, [ms("P-9 a", "t0", **p9), ms("P-9 b", "t1", **p9)], basis=basis), variants=("Mr",), key="CM %s P9" % kind)
    evaluate("CM %s: mixture, one P-9 launch and one measured launch (pair = cap, exec)" % kind,
             resolve(kind, [ms("P-9", "t0", **p9), ms("measured", "t1")], basis=basis), variants=("Mr",), key="CM %s mix" % kind)
evaluate("CM controls (gate): one P-9 build child", resolve("controls", [cj("P-9 build", "ctl_S3", **p9), ms("ok", "ctl_planted_S3")], gate=True, row=478),
         variants=("Mr",), key="CM controls")
rows = [
    ("478 G1..G4 completed_valid (fixture shape: uncached builds, raw grids, solves, callgrind)", resolve(
        "fixture", [cj("fixture_S3", "fixture_S3"), cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid"), ms("fx_reg0_raw_x", "fx_reg0_raw_x"),
                    cg("cg fx_reg0_raw_x", "fx_reg0_raw_x"), ms("fx_reg0_S3", "fx_reg0_S3"), cg("cg fx_reg0_S3", "fx_reg0_S3")], gate=True, row=478)),
    ("480 controls_a1 image", resolve("controls_a1", [L("gp", "gp", "controls_a1_pari"), L("health", "health", "health_p1073741831_d222"),
                                                      cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")], gate=True, row=480,
                                      extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])),
    ("481 fixture4 launched", resolve("fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481)),
    ("482 Z-F4 (zero call)", resolve("fixture4", [], row=482)),
    ("483 build (cached)", resolve("build", [cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True)], basis=BASIS_BUILD, row=483)),
    ("485 cells m = 5 measured", resolve("cells_m5", [ms("S5_t0", "S5_t0")], basis=BASIS_M5, row=485)),
    ("485 cells m = 5 measured, one SE-3 re-solve", pb3),
    ("486 Z-C5", resolve("cells_m5", [], basis=BASIS_M5, row=486)),
    ("488 cells m = 4", pb2),
    ("488 cells m = 4, callgrind child failed", resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"),
                                                                     cg("cg raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)], basis=BASIS_M4, row=488)),
    ("489 aggregate v2", resolve("aggregate", [], basis="X-10 aggregate_a1", row=489)),
]
for lab, pkg in rows:
    evaluate("RKR-4 (b) row " + lab, pkg, ("RF", "RG", "RH"), variants=("Mr",), key="row " + lab)

with open(os.path.join(SCR, "rt_eval.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rt_eval.json with %d keys" % len(OUT))
````

### `rt_eval.v3.py`

- sha256: `1f60cdc492e74a280e791bf04c8ab719cd9d2b8ef185251c1151ee17ee8f4dc3`
- bytes: 49517; lines: 838
- argv: `ran once; argv form as for v2; outputs kept as rt_eval.v3.out and rt_eval.v3.json`
- role: Third version. Superseded: record-removed constructions were tagged PLANNED-BASIS REFUSAL because resolve() defaulted designed=True.

````text
#!/usr/bin/env python3
"""TASK-20260924-94cc33 rule evaluator (scratch; zero runs). One method for AJ-0..AJ-3, unchanged across objects.

It imports only json, os, re and itertools. It reads two scratch files written earlier by this review
(listing.json: the directory listings of the four archived r3 gate packages; specout.json: the "out" value of
each child/*.spec.json). It imports no module of any scanned tree and no third-party module.

LAYER 1 (file level) - attribution of every file under child/, solver/, health/, comparator/, pari/ to launch
records, under three encodings of the attribution text:
  RG4   childend RG-4 (b) AS WORDED: stdout_path / stderr_path; a path the argv names exactly; a file under a
        directory the argv names and no other record's argv names; the non-launch list.
  RH1   gapattr RH-1 (i)-(vi) AS WORDED, with the same non-launch list.
  RH1w  RH1 with clause (v) WEAKENED to "every file under child/ is attributed to some launch record" (CRG-4 (e)).
A file with no attribution and not on the non-launch list is a RECORDER GAP.

LAYER 2 (package level) - verdicts under the rule texts, encoded as functions:
  RK   readbackclose RK-1 (a)/(b) and RK-3 (b) AS WORDED (RL-3 gaps gate nothing).
  RF   failclosed AS WORDED: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 gap = a file of the RL-3 globs whose
       writing launch (truth) has no launch record.
  RG   childend: RF with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b) (layer 1 RG4; a gap makes the verdict FAIL).
  RH   gapattr: RG with RH-1 (layer 1 RH1), RH-2 (a)/(b) and RH-4.
  RHw  RH with RH-1 (v) weakened (layer 1 RH1w).
Each package is read under two manifest variants of the requested cap (v2_check_run.py 64):
  Mr = r3 base (r3_run_wrapper.py 550: raw-result.json envelope; None when the wrapper wrote raw-result.json);
  Mc = an r4 wrapper recording the requested cap independently of raw-result.json.
Definitions (failclosed 604-621), evaluated on TRUTH facts: FAIL-OPEN iff the verdict is PASS or PASS_ZL while one
of (i)..(v) holds. (ii) is evaluated under two readings of "recorded pair": LR = in a launch record; ANY = in any
RB-2 source (launch record, the launch's own child/*.meta.json, its RB-1 attempt record, driver-written raw).
PLANNED-BASIS REFUSAL iff the outcome is a planned basis outcome (driver-logic outcome as the rule set reads
RF-0 (b), acted on by a dependant's frozen logic or listed in RFR-2's enumeration) AND designed AND FAIL.
"""
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "<sys.executable>"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE_SET = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}          # RG-1 (c)
RENAMED = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
OUT = {}


def P(*a):
    print(*a)


# ============================================================================ LAYER 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 inputs / 251 report)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93 script)"
    return None


def attribute(rd, rels, dirs, records, specs, events, rule):
    """rels: paths relative to rd (files in the five directories); dirs: absolute directory paths present;
    records: dicts id, order, argv, stdout, stderr, child_end; specs: {absolute spec path: dict or None};
    events: dicts dir, tag, renamed_files. Returns {rel: [(record id, clause)]}."""
    names = {}
    for r in records:
        for a in set(r["argv"]):
            names[a] = names.get(a, 0) + 1
    res = {}
    for rel in rels:
        p = rd + "/" + rel
        hits = []
        for r in records:
            if p == r["stdout"] or p == r["stderr"]:
                hits.append((r["id"], "(i)" if rule != "RG4" else "stdout/stderr"))
            if p in r["argv"]:
                hits.append((r["id"], "(ii)" if rule != "RG4" else "argv exact"))
            if rule in ("RH1", "RH1w"):
                for a in r["argv"]:
                    if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                        hits.append((r["id"], "(iii)"))
            for a in r["argv"]:
                if a in dirs and p.startswith(a.rstrip("/") + "/") and names.get(a, 0) == 1:
                    hits.append((r["id"], "(iv)" if rule != "RG4" else "argv directory"))
            if rule == "RH1" and r.get("child_end") == "exec" and r["argv"]:
                m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
                if m:
                    sp = specs.get(r["argv"][-1])
                    o = rd + "/child/" + m.group("tag")
                    if isinstance(sp, dict) and isinstance(sp.get("out"), str) and sp["out"] == o and p in (o + ".npz", o + ".meta.json"):
                        hits.append((r["id"], "(v)"))
        if rule == "RH1w" and rel.startswith("child/") and records:
            hits.append(("<some launch record>", "(v) weakened"))
        if rule == "RH1":
            d, _, name = rel.partition("/")
            m = RENAMED.fullmatch(name)
            if m and d in ("solver", "health"):
                tag, k = m.group("tag"), int(m.group("k"))
                ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
                same = sorted((r for r in records if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["order"])
                if ev and len(same) >= k:
                    hits.append((same[k - 1]["id"], "(vi) k=%d" % k))
        if not hits and nonlaunch(rel):
            hits.append(("-", nonlaunch(rel)))
        res[rel] = hits
    return res


# ============================================================================ LAYER 2: launches, files, packages
def L(lid, site, tag, **kw):
    d = dict(lid=lid, site=site, tag=tag, created=True, p227=True, exec_=True, report="OK", rc=0, pair=CP,
             raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False, foreign_write=None,
             recorded=True, callback="normal", fired=None, new_pids=None, opened=None, t_en=None, value=None,
             order=0, outcome="ok", job=None, cached=False, dirn=None, gb=False, cg_out_left=False,
             partial_npz=False, in_attempt_record=False, in_raw=False, retained=True, files_override=None)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["opened"] is None:
        d["opened"] = d["created"]
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if d["dirn"] is None:
        d["dirn"] = {"childjob": "child", "msolve": "solver", "callgrind": "solver", "comparator": "comparator",
                     "health": "health", "gp": "pari"}[site]
    return d


def launch_paths(l, rd):
    """argv, stdout_path, stderr_path exactly as the frozen call sites build them."""
    t, dn = l["tag"], rd + "/" + l["dirn"]
    s = l["site"]
    if s == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if s in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"]
                + (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if s == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2",
                 "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if s == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if s == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(s)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch (relative paths, truth writer)."""
    if l["files_override"] is not None:
        return list(l["files_override"])
    t, dn, s, me = l["tag"], l["dirn"], l["site"], l["lid"]
    f = []
    opened = l["created"] and l["report"] is not None       # the fork child opened stdout/stderr (188-189)
    if s == "childjob":
        f.append((dn + "/" + t + ".spec.json", ("driver", "v2_driver 98-99")))
        if opened:
            f += [(dn + "/" + t + ".stdout", (me, "")), (dn + "/" + t + ".stderr", (me, ""))]
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f += [(dn + "/" + t + ".npz", (me, "v2_child 38")), (dn + "/" + t + ".meta.json", (me, "v2_child 41"))]
                else:
                    f += [(dn + "/" + t + ".meta.json", (me, "v2_child 104; .npz removed v2_driver 144"))]
            elif l["outcome"] == "refused_meta":
                f += [(dn + "/" + t + ".meta.json", (me, "v2_child 68/80"))]
            elif l["partial_npz"]:
                f += [(dn + "/" + t + ".npz", (me, "partial, v2_child 38/100"))]
    elif s in ("msolve", "health"):
        if l["retained"]:
            f.append((dn + "/" + t + ".ms", ("driver", "v2_driver 162 / a1_health 143")))
        if opened:
            f += [(dn + "/" + t + ".ms.log", (me, "")), (dn + "/" + t + ".ms.err", (me, ""))]
        if l["exec_"] and l["outcome"] in ("ok", "ssf"):
            f.append((dn + "/" + t + ".ms.out", (me, "")))
    elif s == "callgrind":
        if opened:
            f += [(dn + "/" + t + ".callgrind.stdout", (me, "")), (dn + "/" + t + ".callgrind.stderr", (me, ""))]
        if l["cg_out_left"]:
            f.append((dn + "/" + t + ".callgrind.out", (me, "left by v2_solver 521-524")))
    elif s == "comparator":
        if opened:
            f += [(dn + "/stdout.log", (me, "")), (dn + "/stderr.log", (me, ""))]
        if l["exec_"] and l["outcome"] == "ok":
            f += [(dn + "/" + x, (me, "k4a 279-281, 318")) for x in ("anchor25_random.ms", "anchor25_planted.ms",
                                                                      "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json")]
    elif s == "gp":
        f.append((dn + "/" + t + ".gp", ("driver", "a1_pari 91-93")))
        if opened:
            f += [(dn + "/" + t + ".gp.stdout", (me, "")), (dn + "/" + t + ".gp.stderr", (me, ""))]
    return f


def resolve(kind, launches, raw="driver", gate=False, basis=None, row=None, designed=True, rd=None, resolves=(),
            raw_pairs=True, recording_failure=False, extra_files=()):
    """Build a package. resolves: (site_dir, tag, [launch ids in attempt order]) SE-3 / HR-3 re-solves: every
    attempt but the last has its .ms.out/.ms.log/.ms.err renamed to <name>.ssf-attempt<k> (r3_resolve 224-238)
    and listed under renamed_files["attempt<k>"] of the event (310)."""
    rd = rd or RUNS + "/RUN-X"
    files, events = {}, []
    for i, l in enumerate(launches):
        l["order"] = i
        for rel, w in files_of(l):
            files[rel] = w
    for dn, tag, ids in resolves:
        ev = {"dir": dn, "tag": tag, "renamed_files": {}}
        for k, lid in enumerate(ids[:-1], start=1):
            rn = {}
            for ext in (".ms.out", ".ms.log", ".ms.err"):
                src = dn + "/" + tag + ext
                if src in files:
                    w = files.pop(src)
                    files[src + ".ssf-attempt%d" % k] = (lid, "renamed, r3_resolve 234")
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"renamed": True}
                else:
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"absent": True}
            ev["renamed_files"]["attempt%d" % k] = rn
            # the next attempt rewrites the unrenamed names
            nxt = next(x for x in launches if x["lid"] == ids[k])
            for rel, w in files_of(nxt):
                files[rel] = w
        events.append(ev)
    for rel, w in extra_files:
        files[rel] = w
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, designed=designed, rd=rd,
                files=files, events=events, raw_pairs=raw_pairs, recording_failure=recording_failure)


# ---------------------------------------------------------------- recorded values
def rk1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def rf1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return l["pair"]


def child_end(l, rs):
    if rs in ("RH", "RHw") and l["callback"] == "caught":
        return "undetermined"
    cc = rf1(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["opened"] and l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE_SET:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):
    cc = rk1(l) if rs == "RK" else rf1(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


# ---------------------------------------------------------------- package-level rules
def records_for_layer1(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = launch_paths(l, pkg["rd"])
        out.append({"id": l["lid"], "order": l["order"], "argv": argv, "stdout": so, "stderr": se,
                    "child_end": child_end(l, rs) if rs in ("RG", "RH", "RHw") else None})
    return out


def specs_of(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["site"] == "childjob":
            path = pkg["rd"] + "/child/" + l["tag"] + ".spec.json"
            if ("child/" + l["tag"] + ".spec.json") in pkg["files"]:
                sp[path] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"], "to_cache": l["cached"]}
    return sp


def dirs_of(pkg):
    return {pkg["rd"] + "/" + d for d in FIVE}


def gaps(pkg, rs):
    rels = sorted(pkg["files"])
    if rs == "RK":
        return []
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob_hit = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            writer = w[0]
            if glob_hit and writer != "driver" and writer not in recorded:
                g.append(rel)
        return sorted(g)
    rule = {"RG": "RG4", "RH": "RH1", "RHw": "RH1w"}[rs]
    att = attribute(pkg["rd"], rels, dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    return sorted(r for r, h in att.items() if not h)


def pairs_collected(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(rec_pair(l))                                       # RL-3 (d)
        if l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"]:
            ps.append(l["pair"])                                         # RB-2 (b): the child's own getrlimit
        if l["in_attempt_record"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (c)
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (a)
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = pairs_collected(pkg)
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    five = bool(pkg["files"])
    r4ok = not pkg["recording_failure"]
    zl_kinds = ("cells_m5", "fixture4")
    if rs == "RK":
        if not items and r4ok:
            return "PASS"
        if not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(rf1(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs in ("RG", "RH", "RHw"):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    g = gaps(pkg, rs)
    if (not items and r4ok and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign
            and not g and not undet):
        return "PASS"
    if (not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok and rw == "driver"
            and pkg["kind"] in zl_kinds and not foreign):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    files = pkg["files"]
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (rk1(l) if rs == "RK" else rf1(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and l["pair"] == CP and (
                l["in_attempt_record"] or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in files and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            detected = (rs != "RK" and l["foreign_write"] == "ok") or (rs in ("RG", "RH", "RHw") and rec and child_end(l, rs) == "undetermined")
            if not detected:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs in ("RG", "RH", "RHw") and infra_stop(pkg):
        return False
    if rs in ("RH", "RHw") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (removed)"
    cc = rk1(l) if rs == "RK" else rf1(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs in ("RG", "RH", "RHw"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii) created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs in ("RG", "RH", "RHw") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant foreign-process record; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def evaluate(label, pkg, rule_sets=("RF", "RG", "RH"), ks=(0,), variants=("Mr", "Mc"), extra_b=None, key=None):
    P("\n### " + label)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-24s] %-3s %s" % (l["lid"][:24], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = pkg
            if k:
                other = [L("otherB%d" % j, "msolve", "otherB_t%d" % j, in_raw=True) for j in range(k)]
                q = resolve(pkg["kind"], [dict(x) for x in pkg["launches"]] + other, raw=pkg["raw"], gate=pkg["gate"],
                            basis=pkg["basis"], row=pkg["row"], designed=pkg["designed"], rd=pkg["rd"],
                            resolves=[(e["dir"], e["tag"], None) for e in []], raw_pairs=pkg["raw_pairs"],
                            recording_failure=pkg["recording_failure"])
                q["files"].update({r: w for r, w in pkg["files"].items()})
                q["events"] = pkg["events"]
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row " + str(q["row"]))))
            if rs in ("RG", "RH", "RHw") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RHw") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-18s defs %-24s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var),
                         "definitions": dfs, "fail_open": fo, "planned_basis_refusal": pb, "gaps": g})
    OUT[key or label] = rows
    return rows


# ============================================================================ helpers for objects
def ms(lid, tag, **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "msolve", tag, **kw)


def cj(lid, tag, job="build", **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "childjob", tag, job=job, **kw)


def cg(lid, tag, **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "callgrind", tag, **kw)


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)"
BASIS_M4 = "X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003, 1068-1075)"


# ============================================================================ AJ-0 KNOWN-ANSWER CONTROL
P("=" * 110 + "\nAJ-0 KNOWN-ANSWER CONTROL (CRG-4 (a)-(e))")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK), RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False)
evaluate("KA-a1 P-16 (v2_solver 181 CALL then STORE_FAST pid; raise leaves the driver: raw wrapper-written)",
         resolve("cells_m5", [p16], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a1")
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False)
evaluate("KA-a2 P-F2 after P-14a (release raises in run_child's finally over a raise at 214)",
         resolve("cells_m5", [pf2], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a2")
evaluate("KA-a3 W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper 491-505)",
         resolve("cells_m5", [], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), key="KA-a3")

P("\n--- (b) failclosed AS WORDED (RF): FO-1, foreign-file write failed / interrupted")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (var_lab, wr, rc), "S5_t0", report=rep, rc=rc, pair=pr, p227=p227, exec_=False,
                    escaped=True, foreign_write=wr, outcome="refused_to_start" if var_lab == "C" else "crashed")
            evaluate("KA-b FO-1 variant %s, foreign write %s, escaped exit %d" % (var_lab, wr, rc),
                     resolve("cells_m5", [fo], basis=BASIS_M5, designed=False), ("RF", "RG", "RH"), ks=(0, 1),
                     key="KA-b-%s-%s-%d" % (var_lab, wr, rc))

P("\n--- (c) childend AS WORDED (RG): PB-2 and PB-3 (RF and RH for contrast)")
pb2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve raw_t0", "raw_t0"),
                           cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488)
evaluate("KA-c1 PB-2 cells m = 4, raw_grid child leaves child/grid_raw_t0.meta.json (v2_driver 1161 -> 133-147)", pb2, key="KA-c1")
a1 = ms("S5_t1 attempt 1 (SSF)", "S5_t1", outcome="ssf", in_attempt_record=True)
a2 = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
pb3 = resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1, a2], basis=BASIS_M5, row=485, resolves=[("solver", "S5_t1", [a1["lid"], a2["lid"]])])
evaluate("KA-c2 PB-3 cells m = 5 with one SE-3 re-solve at S-1 (r3_resolve 224-238, 310)", pb3, key="KA-c2")

# ---------------------------------------------------------------- (d) and AJ-2 (1): the listing check
listing = json.load(open(os.path.join(SCR, "listing.json")))
specout = json.load(open(os.path.join(SCR, "specout.json")))


def reconstruct(pk):
    """CRG-9 reconstruction by the frozen code's naming: child/<tag>.spec.json -> child job; solver/<tag>.ms.log ->
    msolve; solver/<tag>.callgrind.stdout -> callgrind; comparator/stdout.log -> comparator; health/<tag>.ms.log ->
    health msolve; pari/<tag>.gp.stdout -> gp. child_end "exec" is reconstructed for a child job whose <out>.meta.json
    or <out>.npz exists (only v2_child writes them, after exec) and for every launch whose output file exists."""
    rd = RUNS + "/" + pk
    ents = listing["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    dirs = {rd + "/" + e["path"].rstrip("/") for e in ents if e["type"] == "dir"}
    recs, order = [], 0
    specs = {}
    for rel, v in specout[pk]["specs"].items():
        specs[rd + "/" + rel] = {"out": v.get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = argv = so = se = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid = "childjob:" + t
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out", "<-P|-g>", "1"]
            so, se, ce, lid = rd + "/" + d + "/" + name, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v",
                    "2", "-t", "1", "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se, ce, lid = rd + "/solver/" + name, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t
        elif rel == "comparator/stdout.log":
            argv, so, se, ce, lid = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se, ce, lid = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/pari/" + name, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t
        if lid:
            recs.append({"id": lid, "order": order, "argv": argv, "stdout": so, "stderr": se, "child_end": ce})
            order += 1
    return rd, rels, dirs, recs, specs


def listing_check(rule, pkgs, drop=None, label=""):
    P("\n--- listing check under %s %s" % (rule, label))
    res = {}
    for pk in pkgs:
        rd, rels, dirs, recs, specs = reconstruct(pk)
        if drop:
            recs = [r for r in recs if r["id"] != drop]
        att = attribute(rd, rels, dirs, recs, specs, [], rule)
        g = [r for r in rels if not att[r]]
        by_clause = {}
        for r, h in att.items():
            for (_i, c) in (h[:1] if h else [("-", "NONE (gap)")]):
                by_clause[c] = by_clause.get(c, 0) + 1
        per_rec = {}
        for r, h in att.items():
            for (i, c) in h:
                per_rec.setdefault(i, []).append(c)
        meta_g = [x for x in g if x.endswith(".meta.json")]
        P("  %s: %d files in the five directories, %d reconstructed launch records (%s); files by first clause %s"
          % (pk, len(rels), len(recs), dict(sorted({k: sum(1 for r in recs if r["id"].startswith(k)) for k in ("childjob", "msolve", "callgrind", "comparator", "gp")}.items())),
             dict(sorted(by_clause.items()))))
        P("    unattributed: %d (child/*.meta.json %d; child/*.npz %d; other %d)" % (len(g), len(meta_g), sum(1 for x in g if x.endswith(".npz")),
                                                                                  len(g) - len(meta_g) - sum(1 for x in g if x.endswith(".npz"))))
        for x in g:
            P("      GAP " + x)
        res[pk] = {"n_files": len(rels), "n_records": len(recs), "gaps": g, "first_clause_counts": by_clause,
                   "attribution": {r: att[r] for r in rels}}
    OUT["listing_%s%s" % (rule, "_drop_" + drop if drop else "")] = res
    return res


GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
P("\n--- (d) LISTING CHECK under childend RG-4 (b) AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RG4", GATE, label="(childend)")

P("\n--- (e) gapattr with RH-1 (v) WEAKENED vs AS WORDED, one child-job launch record removed")
P("  (e0) file level on RUN-GFPN-bfe956 with the record of childjob:ctl_S3 removed:")
listing_check("RH1w", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(weakened)")
listing_check("RH1", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(worded)")
e1 = resolve("controls", [cj("ctl_identity_n3", "ctl_identity_n3", in_raw=False), cj("ctl_raw_random", "ctl_raw_random", job="grid", in_raw=False),
                          cj("ctl_S3", "ctl_S3", in_raw=False, recorded=False), ms("ctl_planted_S3", "ctl_planted_S3", in_raw=False)],
             gate=True, row=478, raw_pairs=False, rd=RUNS + "/RUN-G4-copy")
evaluate("KA-e1 controls (G4 shape, raw carries no pair), child-job record of ctl_S3 REMOVED (build ok: meta carries its pair)",
         e1, ("RH", "RHw"), key="KA-e1")
e2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid", outcome="crashed", partial_npz=True, recorded=False, in_raw=False),
                          ms("msolve S4_t0", "S4_t0"), cj("grid_raw_t1 child", "grid_raw_t1", job="grid"), ms("msolve raw_t1", "raw_t1")],
             basis=BASIS_M4, row=488)
evaluate("KA-e2 cells m = 4, raw_grid child of target 0 crashed after exec (partial .npz, no meta), its record REMOVED",
         e2, ("RH", "RHw"), key="KA-e2")

# ============================================================================ AJ-1 under gapattr
P("\n" + "=" * 110 + "\nAJ-1 FAIL-OPEN SEARCH UNDER GAPATTR (RH), RG for contrast")
P("\n--- (1) lost launch records whose files another record's positive source names")


def resolved_cell(drop=None, n=2, site="msolve", dn="solver", tag="S5_t1", kind="cells_m5", extra=()):
    atts = [L("%s attempt %d" % (tag, k), site, tag, outcome="ssf" if k < n else "ok", in_attempt_record=True, in_raw=(k == n),
              recorded=(drop is None or k not in drop)) for k in range(1, n + 1)]
    lau = [ms("S5_t0", "S5_t0")] + list(extra) + atts
    return resolve(kind, lau, basis=BASIS_M5 if kind == "cells_m5" else "X-02 / X-13 (controls_a1 image)", row=485 if kind == "cells_m5" else 480,
                   gate=kind == "controls_a1", resolves=[(dn, tag, [a["lid"] for a in atts])])


evaluate("LR-0 SE-3 re-solve at S-1 (2 attempts), every launch record present", resolved_cell(), ("RG", "RH"), key="LR-0")
evaluate("LR-1 SE-3 re-solve at S-1 (2 attempts), the FINAL attempt's launch record REMOVED", resolved_cell(drop={2}), ("RG", "RH"), key="LR-1")
evaluate("LR-2 SE-3 re-solve at S-1 (2 attempts), attempt 1's launch record REMOVED", resolved_cell(drop={1}), ("RG", "RH"), key="LR-2")
evaluate("LR-3 SE-3 re-solve at S-1 (3 attempts), attempt 2's launch record REMOVED", resolved_cell(drop={2}, n=3), ("RG", "RH"), key="LR-3")
evaluate("LR-4 SE-3 re-solve at S-1 (3 attempts), attempts 2 and 3 REMOVED", resolved_cell(drop={2, 3}, n=3), ("RG", "RH"), key="LR-4")
evaluate("LR-5 HR-3 re-solve at S-2 in controls_a1 (2 attempts), the final attempt's record REMOVED",
         resolved_cell(drop={2}, site="health", dn="health", tag="health_p1073741831_d222", kind="controls_a1",
                       extra=[L("gp", "gp", "controls_a1_pari"), L("health d444", "health", "health_p1073741831_d444")]),
         ("RG", "RH"), key="LR-5")
cgp = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve S4_t0 (callgrind tag)", "S4_t0", recorded=False),
                           cg("callgrind S4_t0", "S4_t0")], basis=BASIS_M4, row=488)
evaluate("LR-6 callgrind tag: the msolve record REMOVED, the callgrind record names <tag>.ms", cgp, ("RH",), key="LR-6")
cmp_ = resolve("anchor", [L("comparator", "comparator", "comparator", recorded=False), cj("anchor_S4", "anchor_S4"),
                          ms("anchor_comparator_random", "anchor_comparator_random", gb=True)], gate=True, row=478)
evaluate("LR-7 anchor-identity: the comparator record REMOVED", cmp_, ("RH",), key="LR-7")
bld = resolve("controls", [cj("ctl_S3", "ctl_S3", recorded=False), cj("ctl_raw_random", "ctl_raw_random", job="grid"), ms("ctl_planted_S3", "ctl_planted_S3")],
              gate=True, row=478)
evaluate("LR-8 a build child-job record REMOVED (the RH-6 (i) (22) shape)", bld, ("RH",), key="LR-8")

P("\n--- (2)-(3) FO-1 and RH-4 under gapattr")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("ok", "failed", "interrupted"):
        fo = ms("FO-1 %s %s" % (var_lab, wr), "S5_t0", report=rep, rc=1, pair=pr, p227=p227, exec_=False, escaped=True, foreign_write=wr,
                outcome="refused_to_start" if var_lab == "C" else "crashed")
        evaluate("FO-1 variant %s, foreign write %s" % (var_lab, wr), resolve("cells_m5", [fo], basis=BASIS_M5, designed=False),
                 ("RH",), ks=(1,), key="AJ1-FO1-%s-%s" % (var_lab, wr))
for lab, cb in (("H4-a a signal-raised exception caught by the callback's own try (RH-4 marks)", "caught"),
                ("H4-b an exception of the callback's own code, caught (RH-4 marks)", "caught"),
                ("H4-c a pending signal surfacing at the callback's entry, before its try: escapes, body not run", "escaped_before_body"),
                ("H4-d an exception escaping another after_in_parent callback, or the callback's epilogue after its body", "escaped_after_body")):
    evaluate(lab, resolve("cells_m5", [ms("msolve", "S5_t0", callback=cb)], basis=BASIS_M5, designed=False), ("RG", "RH"), ks=(1,), key=lab[:4])

P("\n--- (4) RG-1 residuals, HYPOTHETICAL supplying code (none found in the repository scan or the third-party text read)")
evaluate("X1 escaped child exits 99 by an unwinding-path SystemExit, variant C (empty report)",
         resolve("cells_m5", [ms("X1", "S5_t0", report="", rc=99, pair=None, p227=False, exec_=False, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X1")
evaluate("X10 escaped child itself execs, variant B",
         resolve("cells_m5", [ms("X10", "S5_t0", report="OK", rc=0, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X10")
evaluate("X6b counter on a second live child that execs while the real child escaped (variant B)",
         resolve("cells_m5", [ms("X6b", "S5_t0", report="OK", rc=1, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X6b")

P("\n--- census paths under gapattr (RH), each in a cells m = 5 package with one other class (B) launch")
census = [
    ("P-1..P-4 refused before fork (153-169)", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start")),
    ("P-6 ERR setrlimit 97", dict(report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-7 empty report 99", dict(report="", rc=99, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-8 soft != cap (98; return 232)", dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")),
    ("P-9 hard-only mismatch (98)", dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")),
    ("P-10..P-13 exec; ok / crashed / memory / timeout", dict()),
    ("exec raised after OK (99)", dict(report="OK", rc=99, exec_=False, outcome="crashed")),
    ("P-5a raise before fork", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, raised="MemoryError", tb=[(152, False)], rec_key=False)),
    ("P-16 raise at 181", dict(raised="KeyboardInterrupt", p227=False, exec_=False, report=None, rc=None, pair=None, tb=[(181, False)], rec_key=False)),
    ("P-14c raise after 227", dict(raised="KeyboardInterrupt", tb=[(244, True)], rec_key=True)),
]
for lab, kw in census:
    raw = "wrapper" if kw.get("raised") else "driver"
    evaluate("census " + lab, resolve("cells_m5", [ms("path", "S5_t0", **kw)], raw=raw, basis=BASIS_M5, designed=kw.get("raised") is None),
             ("RH",), ks=(1,), variants=("Mc",), key="census " + lab)

# ============================================================================ AJ-2 normal outcomes under gapattr
P("\n" + "=" * 110 + "\nAJ-2 NORMAL OUTCOMES OF EVERY LAUNCH KIND UNDER GAPATTR (RH): files written and their attribution")


def show_attr(label, pkg, rs="RH"):
    rule = {"RG": "RG4", "RH": "RH1"}[rs]
    att = attribute(pkg["rd"], sorted(pkg["files"]), dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    P("\n### " + label)
    for rel in sorted(att):
        h = att[rel]
        P("  %-52s writer %-44s -> %s" % (rel, ("%s %s" % pkg["files"][rel])[:44], "; ".join("%s %s" % (c, i) for i, c in h) if h else "GAP"))
    OUT.setdefault("AJ2_attr", {})[label] = {r: att[r] for r in att}
    return evaluate(label + " [verdict]", pkg, ("RG", "RH"), variants=("Mr",), key="AJ2 " + label)


show_attr("N-1 cells m = 5 measured (S5 t0 retained, t1 not retained)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), ms("S5_t1", "S5_t1", retained=False)], basis=BASIS_M5, row=485))
show_attr("N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out)", resolve(
    "cells_m5", [ms("S5_t0 timeout", "S5_t0", rc=-9, outcome="timeout"), ms("S5_t1 memory", "S5_t1", rc=-11, outcome="memory_exhausted")], basis=BASIS_M5, row=485))
show_attr("N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488))
show_attr("N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="crashed", rc=1, partial_npz=True), cj("grid_raw_t1", "grid_raw_t1", job="grid"),
                 ms("raw_t1", "raw_t1")], basis=BASIS_M4, row=488))
a1_ = ms("S5_t1 attempt 1", "S5_t1", outcome="ssf", in_attempt_record=True)
a2_ = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
show_attr("N-5 SE-3 re-solve at S-1 (2 attempts)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1_, a2_], basis=BASIS_M5, row=485,
                                                         resolves=[("solver", "S5_t1", [a1_["lid"], a2_["lid"]])]))
h1 = L("health d222 attempt 1", "health", "health_p1073741831_d222", outcome="ssf", in_attempt_record=True)
h2 = L("health d222 attempt 2", "health", "health_p1073741831_d222", in_attempt_record=True)
show_attr("N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves", resolve(
    "controls_a1", [L("gp", "gp", "controls_a1_pari"), h1, h2, L("health d444", "health", "health_p1073741831_d444"),
                    cj("ctl_a1_torsion_S3_rq", "ctl_a1_torsion_S3_rq"), ms("ctl_a1_planted_torsion_S3_rq", "ctl_a1_planted_torsion_S3_rq")],
    gate=True, row=480, resolves=[("health", "health_p1073741831_d222", [h1["lid"], h2["lid"]])],
    extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))]))
show_attr("N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)],
    basis=BASIS_M4, row=488))
show_attr("N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=-9, outcome="timeout")],
    basis=BASIS_M4, row=488))
show_attr("N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962)", resolve(
    "build", [cj("build_4111_S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True), cj("build_4111_S4", "build_4111_ecgfp5_shaped_S4_m4", cached=True)],
    basis=BASIS_BUILD, row=483))
show_attr("N-10 fixture4: uncached builds and solves", resolve(
    "fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481))
show_attr("N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C)", resolve(
    "cells_m4", [cj("grid_raw_t0 refused meta", "grid_raw_t0", job="grid", outcome="refused_meta"),
                 cj("grid_raw_t1 refused before fork", "grid_raw_t1", job="grid", created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start"),
                 cj("grid_raw_t2 ERR", "grid_raw_t2", job="grid", report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start"),
                 ms("raw_t3", "raw_t3")], basis=BASIS_M4, row=488))
show_attr("N-12 anchor-identity: comparator, uncached build, gb_only solves", resolve(
    "anchor", [L("comparator", "comparator", "comparator"), cj("anchor_S4", "anchor_S4"), ms("anchor_v2_t0", "anchor_v2_t0", gb=True),
               ms("anchor_comparator_system", "anchor_comparator_system", gb=True)], gate=True, row=478))
show_attr("N-13 Z-C5 (no launch; directories only)", resolve("cells_m5", [], basis=BASIS_M5, row=486))

P("\n--- AJ-2 (1) LISTING CHECK under gapattr RH-1 AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RH1", GATE, label="(gapattr)")

# ============================================================================ AJ-3 cap-mismatch outcomes and RKR-4 (b) rows
P("\n" + "=" * 110 + "\nAJ-3 CAP-MISMATCH OUTCOMES (RH-2) AND THE RKR-4 (b) PASS / PASS_ZL ROWS: RF vs RG vs RH")
p8 = dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")
p9 = dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")
for kind, basis in (("cells_m5", BASIS_M5), ("cells_m4", BASIS_M4), ("build", BASIS_BUILD)):
    evaluate("CM %s: every launch P-8" % kind, resolve(kind, [ms("P-8 a", "t0", **p8), ms("P-8 b", "t1", **p8)], basis=basis), variants=("Mr",), key="CM %s P8" % kind)
    evaluate("CM %s: every launch P-9" % kind, resolve(kind, [ms("P-9 a", "t0", **p9), ms("P-9 b", "t1", **p9)], basis=basis), variants=("Mr",), key="CM %s P9" % kind)
    evaluate("CM %s: mixture, one P-9 launch and one measured launch (pair = cap, exec)" % kind,
             resolve(kind, [ms("P-9", "t0", **p9), ms("measured", "t1")], basis=basis), variants=("Mr",), key="CM %s mix" % kind)
evaluate("CM controls (gate): one P-9 build child", resolve("controls", [cj("P-9 build", "ctl_S3", **p9), ms("ok", "ctl_planted_S3")], gate=True, row=478),
         variants=("Mr",), key="CM controls")
rows = [
    ("478 G1..G4 completed_valid (fixture shape: uncached builds, raw grids, solves, callgrind)", resolve(
        "fixture", [cj("fixture_S3", "fixture_S3"), cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid"), ms("fx_reg0_raw_x", "fx_reg0_raw_x"),
                    cg("cg fx_reg0_raw_x", "fx_reg0_raw_x"), ms("fx_reg0_S3", "fx_reg0_S3"), cg("cg fx_reg0_S3", "fx_reg0_S3")], gate=True, row=478)),
    ("480 controls_a1 image", resolve("controls_a1", [L("gp", "gp", "controls_a1_pari"), L("health", "health", "health_p1073741831_d222"),
                                                      cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")], gate=True, row=480,
                                      extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])),
    ("481 fixture4 launched", resolve("fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481)),
    ("482 Z-F4 (zero call)", resolve("fixture4", [], row=482)),
    ("483 build (cached)", resolve("build", [cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True)], basis=BASIS_BUILD, row=483)),
    ("485 cells m = 5 measured", resolve("cells_m5", [ms("S5_t0", "S5_t0")], basis=BASIS_M5, row=485)),
    ("485 cells m = 5 measured, one SE-3 re-solve", pb3),
    ("486 Z-C5", resolve("cells_m5", [], basis=BASIS_M5, row=486)),
    ("488 cells m = 4", pb2),
    ("488 cells m = 4, callgrind child failed", resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"),
                                                                     cg("cg raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)], basis=BASIS_M4, row=488)),
    ("489 aggregate v2", resolve("aggregate", [], basis="X-10 aggregate_a1", row=489)),
]
for lab, pkg in rows:
    evaluate("RKR-4 (b) row " + lab, pkg, ("RF", "RG", "RH"), variants=("Mr",), key="row " + lab)

with open(os.path.join(SCR, "rt_eval.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rt_eval.json with %d keys" % len(OUT))
````

### `rt_eval.py`

- sha256: `662e57565e314186a334173d0c4188acd7162bb21f9bce6196e69b2645ba893e`
- bytes: 51636; lines: 862
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B rt_eval.py > rt_eval.out   (cwd <scratch>/rt_94cc33)`
- role: FINAL evaluator: every verdict of AJ-0..AJ-3 in this report is read from its output rt_eval.out and rt_eval.json.

````text
#!/usr/bin/env python3
"""TASK-20260924-94cc33 rule evaluator (scratch; zero runs). One method for AJ-0..AJ-3, unchanged across objects.

It imports only json, os, re and itertools. It reads two scratch files written earlier by this review
(listing.json: the directory listings of the four archived r3 gate packages; specout.json: the "out" value of
each child/*.spec.json). It imports no module of any scanned tree and no third-party module.

LAYER 1 (file level) - attribution of every file under child/, solver/, health/, comparator/, pari/ to launch
records, under three encodings of the attribution text:
  RG4   childend RG-4 (b) AS WORDED: stdout_path / stderr_path; a path the argv names exactly; a file under a
        directory the argv names and no other record's argv names; the non-launch list.
  RH1   gapattr RH-1 (i)-(vi) AS WORDED, with the same non-launch list.
  RH1w  RH1 with clause (v) WEAKENED to "every file under child/ is attributed to some launch record" (CRG-4 (e)).
A file with no attribution and not on the non-launch list is a RECORDER GAP.

LAYER 2 (package level) - verdicts under the rule texts, encoded as functions:
  RK   readbackclose RK-1 (a)/(b) and RK-3 (b) AS WORDED (RL-3 gaps gate nothing).
  RF   failclosed AS WORDED: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 gap = a file of the RL-3 globs whose
       writing launch (truth) has no launch record.
  RG   childend: RF with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b) (layer 1 RG4; a gap makes the verdict FAIL).
  RH   gapattr: RG with RH-1 (layer 1 RH1), RH-2 (a)/(b) and RH-4.
  RHw  RH with RH-1 (v) weakened (layer 1 RH1w).
Each package is read under two manifest variants of the requested cap (v2_check_run.py 64):
  Mr = r3 base (r3_run_wrapper.py 550: raw-result.json envelope; None when the wrapper wrote raw-result.json);
  Mc = an r4 wrapper recording the requested cap independently of raw-result.json.
Definitions (failclosed 604-621), evaluated on TRUTH facts: FAIL-OPEN iff the verdict is PASS or PASS_ZL while one
of (i)..(v) holds. (ii) is evaluated under two readings of "recorded pair": LR = in a launch record; ANY = in any
RB-2 source (launch record, the launch's own child/*.meta.json, its RB-1 attempt record, driver-written raw).
PLANNED-BASIS REFUSAL iff the outcome is a planned basis outcome (driver-logic outcome as the rule set reads
RF-0 (b), acted on by a dependant's frozen logic or listed in RFR-2's enumeration) AND designed AND FAIL.
"""
import itertools
import json
import os
import re
import sys

SCR = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/crypto-autoresearcher"
EXP = REPO + "/experiments/EXP-GFPN-05ff43"
RUNS = EXP + "/runs"
V2CHILD = EXP + "/implementation-v2/v2_child.py"
PY = "<sys.executable>"
MSOLVE, VALGRIND, GP = "/usr/bin/msolve", "/usr/bin/valgrind", "/usr/bin/gp"
SAGE_PY = "/opt/conda-sage/envs/sage/bin/python"
COMPARATOR = REPO + "/coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py"
CACHE = "/tmp/gfpn05-v2-cache"
CAP = 10737418240
CP = (CAP, CAP)
FIVE = ("child", "solver", "health", "comparator", "pari")
FPE_SET = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}          # RG-1 (c)
RENAMED = re.compile(r"^(?P<tag>.+)(?P<ext>\.ms\.out|\.ms\.log|\.ms\.err)\.ssf-attempt(?P<k>[0-9]+)$")
OUT = {}


def P(*a):
    print(*a)


# ============================================================================ LAYER 1: attribution
def nonlaunch(rel):
    d, _, name = rel.partition("/")
    if d == "health" and (name.endswith(".ms") or re.fullmatch(r"health-[0-9]+\.json", name)):
        return "non-launch list (a1_health 141-143 inputs / 251 report)"
    if d == "pari" and name.endswith(".gp"):
        return "non-launch list (a1_pari 91-93 script)"
    return None


def attribute(rd, rels, dirs, records, specs, events, rule):
    """rels: paths relative to rd (files in the five directories); dirs: absolute directory paths present;
    records: dicts id, order, argv, stdout, stderr, child_end; specs: {absolute spec path: dict or None};
    events: dicts dir, tag, renamed_files. Returns {rel: [(record id, clause)]}."""
    names = {}
    for r in records:
        for a in set(r["argv"]):
            names[a] = names.get(a, 0) + 1
    res = {}
    for rel in rels:
        p = rd + "/" + rel
        hits = []
        for r in records:
            if p == r["stdout"] or p == r["stderr"]:
                hits.append((r["id"], "(i)" if rule != "RG4" else "stdout/stderr"))
            if p in r["argv"]:
                hits.append((r["id"], "(ii)" if rule != "RG4" else "argv exact"))
            if rule in ("RH1", "RH1w"):
                for a in r["argv"]:
                    if a.startswith("--callgrind-out-file=") and a[len("--callgrind-out-file="):] == p:
                        hits.append((r["id"], "(iii)"))
            for a in r["argv"]:
                if a in dirs and p.startswith(a.rstrip("/") + "/") and names.get(a, 0) == 1:
                    hits.append((r["id"], "(iv)" if rule != "RG4" else "argv directory"))
            if rule == "RH1" and r.get("child_end") == "exec" and r["argv"]:
                m = re.fullmatch(re.escape(rd + "/child/") + r"(?P<tag>[^/]+)\.spec\.json", r["argv"][-1])
                if m:
                    sp = specs.get(r["argv"][-1])
                    o = rd + "/child/" + m.group("tag")
                    if isinstance(sp, dict) and isinstance(sp.get("out"), str) and sp["out"] == o and p in (o + ".npz", o + ".meta.json"):
                        hits.append((r["id"], "(v)"))
        if rule == "RH1w" and rel.startswith("child/") and records:
            hits.append(("<some launch record>", "(v) weakened"))
        if rule == "RH1":
            d, _, name = rel.partition("/")
            m = RENAMED.fullmatch(name)
            if m and d in ("solver", "health"):
                tag, k = m.group("tag"), int(m.group("k"))
                ev = any(e["dir"] == d and e["tag"] == tag and name in (e["renamed_files"].get("attempt%d" % k) or {}) for e in events)
                same = sorted((r for r in records if r["stdout"] == rd + "/" + d + "/" + tag + ".ms.log"), key=lambda r: r["order"])
                if ev and len(same) >= k:
                    hits.append((same[k - 1]["id"], "(vi) k=%d" % k))
        if not hits and nonlaunch(rel):
            hits.append(("-", nonlaunch(rel)))
        res[rel] = hits
    return res


# ============================================================================ LAYER 2: launches, files, packages
def L(lid, site, tag, **kw):
    d = dict(lid=lid, site=site, tag=tag, created=True, p227=True, exec_=True, report="OK", rc=0, pair=CP,
             raised=None, tb=[], chain=None, rec_bound=True, rec_key=None, escaped=False, foreign_write=None,
             recorded=True, callback="normal", fired=None, new_pids=None, opened=None, t_en=None, value=None,
             order=0, outcome="ok", job=None, cached=False, dirn=None, gb=False, cg_out_left=False,
             partial_npz=False, in_attempt_record=False, in_raw=False, retained=True, files_override=None)
    d.update(kw)
    if d["chain"] is None:
        d["chain"] = list(d["tb"])
    if d["rec_key"] is None:
        d["rec_key"] = d["created"] and d["raised"] is None
    if d["fired"] is None:
        d["fired"] = d["created"]
    if d["new_pids"] is None:
        d["new_pids"] = 1 if d["created"] else 0
    if d["opened"] is None:
        d["opened"] = d["created"]
    if d["t_en"] is None:
        d["t_en"] = 1 if d["exec_"] else 0
    if d["value"] is None:
        d["value"] = d["t_en"]
    if d["dirn"] is None:
        d["dirn"] = {"childjob": "child", "msolve": "solver", "callgrind": "solver", "comparator": "comparator",
                     "health": "health", "gp": "pari"}[site]
    return d


def launch_paths(l, rd):
    """argv, stdout_path, stderr_path exactly as the frozen call sites build them."""
    t, dn = l["tag"], rd + "/" + l["dirn"]
    s = l["site"]
    if s == "childjob":
        return [PY, "-B", V2CHILD, dn + "/" + t + ".spec.json"], dn + "/" + t + ".stdout", dn + "/" + t + ".stderr"
    if s in ("msolve", "health"):
        return ([MSOLVE, "-v", "2", "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".ms.out"]
                + (["-g", "1"] if l["gb"] else ["-P", "1"]), dn + "/" + t + ".ms.log", dn + "/" + t + ".ms.err")
    if s == "callgrind":
        return ([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + dn + "/" + t + ".callgrind.out", MSOLVE, "-v", "2",
                 "-t", "1", "-f", dn + "/" + t + ".ms", "-o", dn + "/" + t + ".cg.ms.out", "-P", "1"],
                dn + "/" + t + ".callgrind.stdout", dn + "/" + t + ".callgrind.stderr")
    if s == "comparator":
        return [SAGE_PY, COMPARATOR, dn], dn + "/stdout.log", dn + "/stderr.log"
    if s == "gp":
        return [GP, "-q", "-f", "--default", "nbthreads=1", dn + "/" + t + ".gp"], dn + "/" + t + ".gp.stdout", dn + "/" + t + ".gp.stderr"
    raise ValueError(s)


def files_of(l):
    """Files the frozen code leaves in the five directories for one launch (relative paths, truth writer)."""
    if l["files_override"] is not None:
        return list(l["files_override"])
    t, dn, s, me = l["tag"], l["dirn"], l["site"], l["lid"]
    f = []
    opened = l["created"] and l["report"] is not None       # the fork child opened stdout/stderr (188-189)
    if s == "childjob":
        f.append((dn + "/" + t + ".spec.json", ("driver", "v2_driver 98-99")))
        if opened:
            f += [(dn + "/" + t + ".stdout", (me, "")), (dn + "/" + t + ".stderr", (me, ""))]
        if l["exec_"] and not l["cached"]:
            if l["outcome"] == "ok":
                if l["job"] == "build":
                    f += [(dn + "/" + t + ".npz", (me, "v2_child 38")), (dn + "/" + t + ".meta.json", (me, "v2_child 41"))]
                else:
                    f += [(dn + "/" + t + ".meta.json", (me, "v2_child 104; .npz removed v2_driver 144"))]
            elif l["outcome"] == "refused_meta":
                f += [(dn + "/" + t + ".meta.json", (me, "v2_child 68/80"))]
            elif l["partial_npz"]:
                f += [(dn + "/" + t + ".npz", (me, "partial, v2_child 38/100"))]
    elif s in ("msolve", "health"):
        if l["retained"]:
            f.append((dn + "/" + t + ".ms", ("driver", "v2_driver 162 / a1_health 143")))
        if opened:
            f += [(dn + "/" + t + ".ms.log", (me, "")), (dn + "/" + t + ".ms.err", (me, ""))]
        if l["exec_"] and l["outcome"] in ("ok", "ssf"):
            f.append((dn + "/" + t + ".ms.out", (me, "")))
    elif s == "callgrind":
        if opened:
            f += [(dn + "/" + t + ".callgrind.stdout", (me, "")), (dn + "/" + t + ".callgrind.stderr", (me, ""))]
        if l["cg_out_left"]:
            f.append((dn + "/" + t + ".callgrind.out", (me, "left by v2_solver 521-524")))
    elif s == "comparator":
        if opened:
            f += [(dn + "/stdout.log", (me, "")), (dn + "/stderr.log", (me, ""))]
        if l["exec_"] and l["outcome"] == "ok":
            f += [(dn + "/" + x, (me, "k4a 279-281, 318")) for x in ("anchor25_random.ms", "anchor25_planted.ms",
                                                                      "anchor17_random.ms", "anchor17_planted.ms", "k4a_results.json")]
    elif s == "gp":
        f.append((dn + "/" + t + ".gp", ("driver", "a1_pari 91-93")))
        if opened:
            f += [(dn + "/" + t + ".gp.stdout", (me, "")), (dn + "/" + t + ".gp.stderr", (me, ""))]
    return f


def resolve(kind, launches, raw="driver", gate=False, basis=None, row=None, designed=True, rd=None, resolves=(),
            raw_pairs=True, recording_failure=False, extra_files=()):
    """Build a package. resolves: (site_dir, tag, [launch ids in attempt order]) SE-3 / HR-3 re-solves: every
    attempt but the last has its .ms.out/.ms.log/.ms.err renamed to <name>.ssf-attempt<k> (r3_resolve 224-238)
    and listed under renamed_files["attempt<k>"] of the event (310)."""
    rd = rd or RUNS + "/RUN-X"
    files, events = {}, []
    for i, l in enumerate(launches):
        l["order"] = i
        for rel, w in files_of(l):
            files[rel] = w
    for dn, tag, ids in resolves:
        ev = {"dir": dn, "tag": tag, "renamed_files": {}}
        for k, lid in enumerate(ids[:-1], start=1):
            rn = {}
            for ext in (".ms.out", ".ms.log", ".ms.err"):
                src = dn + "/" + tag + ext
                if src in files:
                    w = files.pop(src)
                    files[src + ".ssf-attempt%d" % k] = (lid, "renamed, r3_resolve 234")
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"renamed": True}
                else:
                    rn[os.path.basename(src) + ".ssf-attempt%d" % k] = {"absent": True}
            ev["renamed_files"]["attempt%d" % k] = rn
            # the next attempt rewrites the unrenamed names
            nxt = next(x for x in launches if x["lid"] == ids[k])
            for rel, w in files_of(nxt):
                files[rel] = w
        events.append(ev)
    for rel, w in extra_files:
        files[rel] = w
    designed = designed and all(l["recorded"] for l in launches)      # a removed record is a construction
    return dict(kind=kind, launches=launches, raw=raw, gate=gate, basis=basis, row=row, designed=designed, rd=rd,
                files=files, events=events, raw_pairs=raw_pairs, recording_failure=recording_failure)


# ---------------------------------------------------------------- recorded values
def rk1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if l["rec_bound"] and l["rec_key"]:
        return True
    return any(pid for (_ln, pid) in l["tb"])


def rf1(l):
    if l["raised"] is None:
        return l["rec_key"]
    if len(l["chain"]) > 16:
        return "undetermined"
    if (l["rec_bound"] and l["rec_key"]) or any(pid for (_ln, pid) in l["chain"]):
        return True
    if all(ln < 181 and not pid for (ln, pid) in l["chain"]):
        return False
    return "undetermined"


def rec_pair(l):
    if not l["p227"]:
        return None
    if l["raised"] is not None and not l["rec_bound"]:
        return None
    return l["pair"]


def child_end(l, rs):
    if rs in ("RH", "RHw") and l["callback"] == "caught":
        return "undetermined"
    cc = rf1(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if l["callback"] == "escaped_before_body":
        return "undetermined"
    if not (l["opened"] and l["new_pids"] == 1):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0 and (l["report"], l["rc"]) in FPE_SET:
        return "frozen_pre_exec_exit"
    return "undetermined"


def klass(l, rs):
    cc = rk1(l) if rs == "RK" else rf1(l)
    pr = rec_pair(l) is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("RK", "RF") or base is None:
        return base
    ce = child_end(l, rs)
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    return "C" if ce == "frozen_pre_exec_exit" else None


# ---------------------------------------------------------------- package-level rules
def records_for_layer1(pkg, rs):
    out = []
    for l in pkg["launches"]:
        if not l["recorded"]:
            continue
        argv, so, se = launch_paths(l, pkg["rd"])
        out.append({"id": l["lid"], "order": l["order"], "argv": argv, "stdout": so, "stderr": se,
                    "child_end": child_end(l, rs) if rs in ("RG", "RH", "RHw") else None})
    return out


def specs_of(pkg):
    sp = {}
    for l in pkg["launches"]:
        if l["site"] == "childjob":
            path = pkg["rd"] + "/child/" + l["tag"] + ".spec.json"
            if ("child/" + l["tag"] + ".spec.json") in pkg["files"]:
                sp[path] = {"out": (CACHE if l["cached"] else pkg["rd"] + "/child") + "/" + l["tag"], "to_cache": l["cached"]}
    return sp


def dirs_of(pkg):
    return {pkg["rd"] + "/" + d for d in FIVE}


def gaps(pkg, rs):
    rels = sorted(pkg["files"])
    if rs == "RK":
        return []
    if rs == "RF":
        recorded = {l["lid"] for l in pkg["launches"] if l["recorded"]}
        g = []
        for rel, w in pkg["files"].items():
            glob_hit = (rel.startswith("child/") and rel.endswith(".meta.json")) or (rel.startswith("solver/") and rel.endswith(".ms.log")) \
                or rel.split("/")[0] in ("health", "comparator", "pari")
            writer = w[0]
            if glob_hit and writer != "driver" and writer not in recorded:
                g.append(rel)
        return sorted(g)
    rule = {"RG": "RG4", "RH": "RH1", "RHw": "RH1w"}[rs]
    rdc = pkg.get("rd_check", pkg["rd"])
    att = attribute(rdc, rels, {rdc + "/" + d for d in FIVE}, records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    return sorted(r for r, h in att.items() if not h)


def pairs_collected(pkg):
    ps = []
    for l in pkg["launches"]:
        if l["recorded"] and rec_pair(l):
            ps.append(rec_pair(l))                                       # RL-3 (d)
        if l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in pkg["files"] and l["outcome"] == "ok" and l["exec_"]:
            ps.append(l["pair"])                                         # RB-2 (b): the child's own getrlimit
        if l["in_attempt_record"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (c)
        if pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"] and l["p227"]:
            ps.append(l["pair"])                                         # RB-2 (a)
    return ps


def frozen_items(pkg, var):
    if pkg["kind"] == "aggregate":
        return []
    ps = pairs_collected(pkg)
    req = CAP if (var == "Mc" or pkg["raw"] == "driver") else None
    it = []
    if not ps:
        it.append("66-67")
    if any(p != (req, req) for p in ps):
        it.append("68-70")
    return it


def verdict(pkg, rs, var):
    items = frozen_items(pkg, var)
    recs = [l for l in pkg["launches"] if l["recorded"]]
    five = bool(pkg["files"])
    r4ok = not pkg["recording_failure"]
    zl_kinds = ("cells_m5", "fixture4")
    if rs == "RK":
        if not items and r4ok:
            return "PASS"
        if not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok:
            return "PASS_ZL"
        return "FAIL"
    rw = pkg["raw"]
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in pkg["launches"])
    undet = any(rf1(l) == "undetermined" for l in recs) or rw == "undetermined"
    if rs in ("RG", "RH", "RHw"):
        undet = undet or any(child_end(l, rs) == "undetermined" for l in recs)
    g = gaps(pkg, rs)
    if (not items and r4ok and all(klass(l, rs) in ("A", "B", "C") for l in recs) and rw == "driver" and not foreign
            and not g and not undet):
        return "PASS"
    if (not pkg["gate"] and not recs and not five and items == ["66-67"] and r4ok and rw == "driver"
            and pkg["kind"] in zl_kinds and not foreign):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    d = set()
    files = pkg["files"]
    for l in pkg["launches"]:
        rec = l["recorded"]
        pr = rec_pair(l) if rec else None
        if l["p227"] and pr is None:
            d.add("(i)")
        cc = (rk1(l) if rs == "RK" else rf1(l)) if rec else None
        k = klass(l, rs) if rec else None
        if (l["created"] or cc == "undetermined") and k not in ("A", "C"):
            if pr != CP:
                d.add("(ii-LR)")
            anysrc = pr == CP or (l["p227"] and l["pair"] == CP and (
                l["in_attempt_record"] or (pkg["raw"] == "driver" and pkg["raw_pairs"] and l["in_raw"])
                or (l["site"] == "childjob" and ("child/" + l["tag"] + ".meta.json") in files and l["outcome"] == "ok")))
            if not anysrc:
                d.add("(ii-ANY)")
        if rec and l["created"] and cc is False:
            d.add("(iii)")
        if l["escaped"]:
            detected = (rs != "RK" and l["foreign_write"] == "ok") or (rs in ("RG", "RH", "RHw") and rec and child_end(l, rs) == "undetermined")
            if not detected:
                d.add("(iv)")
    if pkg["raw"] == "wrapper":
        d.add("(v)")
    return sorted(d)


def infra_stop(pkg):
    recs = [l for l in pkg["launches"] if l["recorded"]]
    return pkg["raw"] == "driver" and bool(recs) and not any(rec_pair(l) for l in recs)


def cap_mismatch(pkg, var):
    return pkg["raw"] == "driver" and "68-70" in frozen_items(pkg, var)


def planned(pkg, rs, var):
    if pkg["raw"] != "driver":
        return False
    if rs in ("RG", "RH", "RHw") and infra_stop(pkg):
        return False
    if rs in ("RH", "RHw") and cap_mismatch(pkg, var):
        return False
    return bool(pkg["basis"] or pkg["row"])


def record_level(l, rs):
    if not l["recorded"]:
        return "NO LAUNCH RECORD (removed)"
    cc = rk1(l) if rs == "RK" else rf1(l)
    s = "child_created=%s class=%s" % (cc, klass(l, rs))
    if rs in ("RG", "RH", "RHw"):
        s += " child_end=%s" % child_end(l, rs)
    fl = []
    if l["created"] and cc is False:
        fl.append("(iii) created child recorded child_created false")
    if l["escaped"]:
        det = []
        if rs != "RK" and l["foreign_write"] == "ok":
            det.append("recorder-foreign file")
        if rs in ("RG", "RH", "RHw") and child_end(l, rs) == "undetermined":
            det.append("child_end undetermined")
        fl.append("(iv)-relevant foreign-process record; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + (" | " + "; ".join(fl) if fl else "")


def evaluate(label, pkg, rule_sets=("RF", "RG", "RH"), ks=(0,), variants=("Mr", "Mc"), extra_b=None, key=None):
    P("\n### " + label)
    for l in pkg["launches"]:
        for rs in rule_sets:
            P("  record[%-24s] %-3s %s" % (l["lid"][:24], rs, record_level(l, rs)))
    rows = []
    for rs in rule_sets:
        for k, var in itertools.product(ks, variants):
            q = pkg
            if k:
                other = [L("otherB%d" % j, "msolve", "otherB_t%d" % j, in_raw=True) for j in range(k)]
                q = resolve(pkg["kind"], [dict(x) for x in pkg["launches"]] + other, raw=pkg["raw"], gate=pkg["gate"],
                            basis=pkg["basis"], row=pkg["row"], designed=pkg["designed"], rd=pkg["rd"],
                            resolves=[(e["dir"], e["tag"], None) for e in []], raw_pairs=pkg["raw_pairs"],
                            recording_failure=pkg["recording_failure"])
                q["files"].update({r: w for r, w in pkg["files"].items()})
                q["events"] = pkg["events"]
            v = verdict(q, rs, var)
            dfs = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(dfs)
            pb = planned(q, rs, var) and q["designed"] and v == "FAIL"
            g = gaps(q, rs)
            tags = []
            if fo:
                tags.append("FAIL-OPEN %s" % dfs)
            if pb:
                tags.append("PLANNED-BASIS REFUSAL (basis %s)" % (q["basis"] or ("RKR-4 (b) row " + str(q["row"]))))
            if rs in ("RG", "RH", "RHw") and infra_stop(q):
                tags.append("infrastructure-stop (RG-2)")
            if rs in ("RH", "RHw") and cap_mismatch(q, var):
                tags.append("cap-mismatch stop (RH-2)")
            if g:
                tags.append("gaps %s" % g)
            P("  package %-3s k=%d %-2s verdict %-7s items %-18s defs %-24s %s" % (rs, k, var, v, frozen_items(q, var), dfs, "; ".join(tags)))
            rows.append({"rule_set": rs, "k": k, "variant": var, "verdict": v, "items": frozen_items(q, var),
                         "definitions": dfs, "fail_open": fo, "planned_basis_refusal": pb, "gaps": g})
    OUT[key or label] = rows
    return rows


# ============================================================================ helpers for objects
def ms(lid, tag, **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "msolve", tag, **kw)


def cj(lid, tag, job="build", **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "childjob", tag, job=job, **kw)


def cg(lid, tag, **kw):
    kw.setdefault("in_raw", True)
    return L(lid, "callgrind", tag, **kw)


BASIS_M5 = "X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)"
BASIS_M4 = "X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)"
BASIS_BUILD = "X-07 _load_build (v2_driver 989-1003, 1068-1075)"


# ============================================================================ AJ-0 KNOWN-ANSWER CONTROL
P("=" * 110 + "\nAJ-0 KNOWN-ANSWER CONTROL (CRG-4 (a)-(e))")
P("\n--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK), RF for contrast")
p16 = ms("P-16 raise at 181", "S5_t0", raised="KeyboardInterrupt", p227=False, report=None, rc=None, exec_=False,
         tb=[(181, False)], rec_key=False)
evaluate("KA-a1 P-16 (v2_solver 181 CALL then STORE_FAST pid; raise leaves the driver: raw wrapper-written)",
         resolve("cells_m5", [p16], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a1")
pf2 = ms("P-F2 after P-14a", "S5_t0", raised="OSError", p227=False, report=None, rc=None, exec_=False, tb=[],
         chain=[(214, True)], rec_key=False)
evaluate("KA-a2 P-F2 after P-14a (release raises in run_child's finally over a raise at 214)",
         resolve("cells_m5", [pf2], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), ks=(0, 1), key="KA-a2")
evaluate("KA-a3 W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper 491-505)",
         resolve("cells_m5", [], raw="wrapper", basis=BASIS_M5, designed=False), ("RK", "RF"), key="KA-a3")

P("\n--- (b) failclosed AS WORDED (RF): FO-1, foreign-file write failed / interrupted")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("failed", "interrupted"):
        for rc in (1, -2):
            fo = ms("FO-1 %s %s rc%d" % (var_lab, wr, rc), "S5_t0", report=rep, rc=rc, pair=pr, p227=p227, exec_=False,
                    escaped=True, foreign_write=wr, outcome="refused_to_start" if var_lab == "C" else "crashed")
            evaluate("KA-b FO-1 variant %s, foreign write %s, escaped exit %d" % (var_lab, wr, rc),
                     resolve("cells_m5", [fo], basis=BASIS_M5, designed=False), ("RF", "RG", "RH"), ks=(0, 1),
                     key="KA-b-%s-%s-%d" % (var_lab, wr, rc))

P("\n--- (c) childend AS WORDED (RG): PB-2 and PB-3 (RF and RH for contrast)")
pb2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve raw_t0", "raw_t0"),
                           cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488)
evaluate("KA-c1 PB-2 cells m = 4, raw_grid child leaves child/grid_raw_t0.meta.json (v2_driver 1161 -> 133-147)", pb2, key="KA-c1")
a1 = ms("S5_t1 attempt 1 (SSF)", "S5_t1", outcome="ssf", in_attempt_record=True)
a2 = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
pb3 = resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1, a2], basis=BASIS_M5, row=485, resolves=[("solver", "S5_t1", [a1["lid"], a2["lid"]])])
evaluate("KA-c2 PB-3 cells m = 5 with one SE-3 re-solve at S-1 (r3_resolve 224-238, 310)", pb3, key="KA-c2")

# ---------------------------------------------------------------- (d) and AJ-2 (1): the listing check
listing = json.load(open(os.path.join(SCR, "listing.json")))
specout = json.load(open(os.path.join(SCR, "specout.json")))


def reconstruct(pk):
    """CRG-9 reconstruction by the frozen code's naming: child/<tag>.spec.json -> child job; solver/<tag>.ms.log ->
    msolve; solver/<tag>.callgrind.stdout -> callgrind; comparator/stdout.log -> comparator; health/<tag>.ms.log ->
    health msolve; pari/<tag>.gp.stdout -> gp. child_end "exec" is reconstructed for a child job whose <out>.meta.json
    or <out>.npz exists (only v2_child writes them, after exec) and for every launch whose output file exists."""
    rd = RUNS + "/" + pk
    ents = listing["packages"][pk]["entries"]
    rels = sorted(e["path"] for e in ents if e["type"] == "file" and e["path"].split("/")[0] in FIVE)
    dirs = {rd + "/" + e["path"].rstrip("/") for e in ents if e["type"] == "dir"}
    recs, order = [], 0
    specs = {}
    for rel, v in specout[pk]["specs"].items():
        specs[rd + "/" + rel] = {"out": v.get("out")} if v.get("parses") else None
    for rel in rels:
        d, _, name = rel.partition("/")
        lid = argv = so = se = None
        if d == "child" and name.endswith(".spec.json"):
            t = name[:-len(".spec.json")]
            argv, so, se = [PY, "-B", V2CHILD, rd + "/child/" + name], rd + "/child/" + t + ".stdout", rd + "/child/" + t + ".stderr"
            ce = "exec" if ("child/" + t + ".meta.json" in rels or "child/" + t + ".npz" in rels) else "unknown"
            lid = "childjob:" + t
        elif d in ("solver", "health") and name.endswith(".ms.log"):
            t = name[:-len(".ms.log")]
            argv = [MSOLVE, "-v", "2", "-t", "1", "-f", rd + "/" + d + "/" + t + ".ms", "-o", rd + "/" + d + "/" + t + ".ms.out", "<-P|-g>", "1"]
            so, se, ce, lid = rd + "/" + d + "/" + name, rd + "/" + d + "/" + t + ".ms.err", "exec", "msolve:" + d + "/" + t
        elif d == "solver" and name.endswith(".callgrind.stdout"):
            t = name[:-len(".callgrind.stdout")]
            argv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + rd + "/solver/" + t + ".callgrind.out", MSOLVE, "-v",
                    "2", "-t", "1", "-f", rd + "/solver/" + t + ".ms", "-o", rd + "/solver/" + t + ".cg.ms.out", "-P", "1"]
            so, se, ce, lid = rd + "/solver/" + name, rd + "/solver/" + t + ".callgrind.stderr", "exec", "callgrind:" + t
        elif rel == "comparator/stdout.log":
            argv, so, se, ce, lid = [SAGE_PY, COMPARATOR, rd + "/comparator"], rd + "/comparator/stdout.log", rd + "/comparator/stderr.log", "exec", "comparator"
        elif d == "pari" and name.endswith(".gp.stdout"):
            t = name[:-len(".gp.stdout")]
            argv, so, se, ce, lid = [GP, "-q", "-f", "--default", "nbthreads=1", rd + "/pari/" + t + ".gp"], rd + "/pari/" + name, rd + "/pari/" + t + ".gp.stderr", "exec", "gp:" + t
        if lid:
            recs.append({"id": lid, "order": order, "argv": argv, "stdout": so, "stderr": se, "child_end": ce})
            order += 1
    return rd, rels, dirs, recs, specs


def listing_check(rule, pkgs, drop=None, label=""):
    P("\n--- listing check under %s %s" % (rule, label))
    res = {}
    for pk in pkgs:
        rd, rels, dirs, recs, specs = reconstruct(pk)
        if drop:
            recs = [r for r in recs if r["id"] != drop]
        att = attribute(rd, rels, dirs, recs, specs, [], rule)
        g = [r for r in rels if not att[r]]
        by_clause = {}
        for r, h in att.items():
            for (_i, c) in (h[:1] if h else [("-", "NONE (gap)")]):
                by_clause[c] = by_clause.get(c, 0) + 1
        per_rec = {}
        for r, h in att.items():
            for (i, c) in h:
                per_rec.setdefault(i, []).append(c)
        meta_g = [x for x in g if x.endswith(".meta.json")]
        P("  %s: %d files in the five directories, %d reconstructed launch records (%s); files by first clause %s"
          % (pk, len(rels), len(recs), dict(sorted({k: sum(1 for r in recs if r["id"].startswith(k)) for k in ("childjob", "msolve", "callgrind", "comparator", "gp")}.items())),
             dict(sorted(by_clause.items()))))
        P("    unattributed: %d (child/*.meta.json %d; child/*.npz %d; other %d)" % (len(g), len(meta_g), sum(1 for x in g if x.endswith(".npz")),
                                                                                  len(g) - len(meta_g) - sum(1 for x in g if x.endswith(".npz"))))
        for x in g:
            P("      GAP " + x)
        res[pk] = {"n_files": len(rels), "n_records": len(recs), "gaps": g, "first_clause_counts": by_clause,
                   "attribution": {r: att[r] for r in rels}}
    OUT["listing_%s%s" % (rule, "_drop_" + drop if drop else "")] = res
    return res


GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
P("\n--- (d) LISTING CHECK under childend RG-4 (b) AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RG4", GATE, label="(childend)")

P("\n--- (e) gapattr with RH-1 (v) WEAKENED vs AS WORDED, one child-job launch record removed")
P("  (e0) file level on RUN-GFPN-bfe956 with the record of childjob:ctl_S3 removed:")
listing_check("RH1w", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(weakened)")
listing_check("RH1", ["RUN-GFPN-bfe956"], drop="childjob:ctl_S3", label="(worded)")
e1 = resolve("controls", [cj("ctl_identity_n3", "ctl_identity_n3", in_raw=False), cj("ctl_raw_random", "ctl_raw_random", job="grid", in_raw=False),
                          cj("ctl_S3", "ctl_S3", in_raw=False, recorded=False), ms("ctl_planted_S3", "ctl_planted_S3", in_raw=False)],
             gate=True, row=478, raw_pairs=False, rd=RUNS + "/RUN-G4-copy")
evaluate("KA-e1 controls (G4 shape, raw carries no pair), child-job record of ctl_S3 REMOVED (build ok: meta carries its pair)",
         e1, ("RH", "RHw"), key="KA-e1")
e2 = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid", outcome="crashed", partial_npz=True, recorded=False, in_raw=False),
                          ms("msolve S4_t0", "S4_t0"), cj("grid_raw_t1 child", "grid_raw_t1", job="grid"), ms("msolve raw_t1", "raw_t1")],
             basis=BASIS_M4, row=488)
evaluate("KA-e2 cells m = 4, raw_grid child of target 0 crashed after exec (partial .npz, no meta), its record REMOVED",
         e2, ("RH", "RHw"), key="KA-e2")

# ============================================================================ AJ-1 under gapattr
P("\n" + "=" * 110 + "\nAJ-1 FAIL-OPEN SEARCH UNDER GAPATTR (RH), RG for contrast")
P("\n--- (1) lost launch records whose files another record's positive source names")


def resolved_cell(drop=None, n=2, site="msolve", dn="solver", tag="S5_t1", kind="cells_m5", extra=()):
    atts = [L("%s attempt %d" % (tag, k), site, tag, outcome="ssf" if k < n else "ok", in_attempt_record=True, in_raw=(k == n),
              recorded=(drop is None or k not in drop)) for k in range(1, n + 1)]
    lau = [ms("S5_t0", "S5_t0")] + list(extra) + atts
    return resolve(kind, lau, basis=BASIS_M5 if kind == "cells_m5" else "X-02 / X-13 (controls_a1 image)", row=485 if kind == "cells_m5" else 480,
                   gate=kind == "controls_a1", resolves=[(dn, tag, [a["lid"] for a in atts])])


evaluate("LR-0 SE-3 re-solve at S-1 (2 attempts), every launch record present", resolved_cell(), ("RG", "RH"), key="LR-0")
evaluate("LR-1 SE-3 re-solve at S-1 (2 attempts), the FINAL attempt's launch record REMOVED", resolved_cell(drop={2}), ("RG", "RH"), key="LR-1")
evaluate("LR-2 SE-3 re-solve at S-1 (2 attempts), attempt 1's launch record REMOVED", resolved_cell(drop={1}), ("RG", "RH"), key="LR-2")
evaluate("LR-3 SE-3 re-solve at S-1 (3 attempts), attempt 2's launch record REMOVED", resolved_cell(drop={2}, n=3), ("RG", "RH"), key="LR-3")
evaluate("LR-4 SE-3 re-solve at S-1 (3 attempts), attempts 2 and 3 REMOVED", resolved_cell(drop={2, 3}, n=3), ("RG", "RH"), key="LR-4")
evaluate("LR-5 HR-3 re-solve at S-2 in controls_a1 (2 attempts), the final attempt's record REMOVED",
         resolved_cell(drop={2}, site="health", dn="health", tag="health_p1073741831_d222", kind="controls_a1",
                       extra=[L("gp", "gp", "controls_a1_pari"), L("health d444", "health", "health_p1073741831_d444")]),
         ("RG", "RH"), key="LR-5")
cgp = resolve("cells_m4", [cj("grid_raw_t0 child", "grid_raw_t0", job="grid"), ms("msolve S4_t0 (callgrind tag)", "S4_t0", recorded=False),
                           cg("callgrind S4_t0", "S4_t0")], basis=BASIS_M4, row=488)
evaluate("LR-6 callgrind tag: the msolve record REMOVED, the callgrind record names <tag>.ms", cgp, ("RH",), key="LR-6")
cmp_ = resolve("anchor", [L("comparator", "comparator", "comparator", recorded=False), cj("anchor_S4", "anchor_S4"),
                          ms("anchor_comparator_random", "anchor_comparator_random", gb=True)], gate=True, row=478)
evaluate("LR-7 anchor-identity: the comparator record REMOVED", cmp_, ("RH",), key="LR-7")
bld = resolve("controls", [cj("ctl_S3", "ctl_S3", recorded=False), cj("ctl_raw_random", "ctl_raw_random", job="grid"), ms("ctl_planted_S3", "ctl_planted_S3")],
              gate=True, row=478)
evaluate("LR-8 a build child-job record REMOVED (the RH-6 (i) (22) shape)", bld, ("RH",), key="LR-8")

P("\n--- (2)-(3) FO-1 and RH-4 under gapattr")
for var_lab, rep, pr, p227 in (("C", "", None, False), ("B", "OK", CP, True)):
    for wr in ("ok", "failed", "interrupted"):
        fo = ms("FO-1 %s %s" % (var_lab, wr), "S5_t0", report=rep, rc=1, pair=pr, p227=p227, exec_=False, escaped=True, foreign_write=wr,
                outcome="refused_to_start" if var_lab == "C" else "crashed")
        evaluate("FO-1 variant %s, foreign write %s" % (var_lab, wr), resolve("cells_m5", [fo], basis=BASIS_M5, designed=False),
                 ("RH",), ks=(1,), key="AJ1-FO1-%s-%s" % (var_lab, wr))
for lab, cb in (("H4-a a signal-raised exception caught by the callback's own try (RH-4 marks)", "caught"),
                ("H4-b an exception of the callback's own code, caught (RH-4 marks)", "caught"),
                ("H4-c a pending signal surfacing at the callback's entry, before its try: escapes, body not run", "escaped_before_body"),
                ("H4-d an exception escaping another after_in_parent callback, or the callback's epilogue after its body", "escaped_after_body")):
    evaluate(lab, resolve("cells_m5", [ms("msolve", "S5_t0", callback=cb)], basis=BASIS_M5, designed=False), ("RG", "RH"), ks=(1,), key=lab[:4])

P("\n--- (4) RG-1 residuals, HYPOTHETICAL supplying code (none found in the repository scan or the third-party text read)")
evaluate("X1 escaped child exits 99 by an unwinding-path SystemExit, variant C (empty report)",
         resolve("cells_m5", [ms("X1", "S5_t0", report="", rc=99, pair=None, p227=False, exec_=False, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X1")
evaluate("X10 escaped child itself execs, variant B",
         resolve("cells_m5", [ms("X10", "S5_t0", report="OK", rc=0, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X10")
evaluate("X6b counter on a second live child that execs while the real child escaped (variant B)",
         resolve("cells_m5", [ms("X6b", "S5_t0", report="OK", rc=1, exec_=False, t_en=1, value=1, escaped=True, foreign_write="failed")],
                 basis=BASIS_M5, designed=False), ("RH",), ks=(1,), key="X6b")

P("\n--- census paths under gapattr (RH), each in a cells m = 5 package with one other class (B) launch")
census = [
    ("P-1..P-4 refused before fork (153-169)", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start")),
    ("P-6 ERR setrlimit 97", dict(report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-7 empty report 99", dict(report="", rc=99, p227=False, pair=None, exec_=False, outcome="refused_to_start")),
    ("P-8 soft != cap (98; return 232)", dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")),
    ("P-9 hard-only mismatch (98)", dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")),
    ("P-10..P-13 exec; ok / crashed / memory / timeout", dict()),
    ("exec raised after OK (99)", dict(report="OK", rc=99, exec_=False, outcome="crashed")),
    ("P-5a raise before fork", dict(created=False, p227=False, exec_=False, report=None, rc=None, pair=None, raised="MemoryError", tb=[(152, False)], rec_key=False)),
    ("P-16 raise at 181", dict(raised="KeyboardInterrupt", p227=False, exec_=False, report=None, rc=None, pair=None, tb=[(181, False)], rec_key=False)),
    ("P-14c raise after 227", dict(raised="KeyboardInterrupt", tb=[(244, True)], rec_key=True)),
]
for lab, kw in census:
    raw = "wrapper" if kw.get("raised") else "driver"
    evaluate("census " + lab, resolve("cells_m5", [ms("path", "S5_t0", **kw)], raw=raw, basis=BASIS_M5, designed=kw.get("raised") is None),
             ("RH",), ks=(1,), variants=("Mc",), key="census " + lab)

# ============================================================================ AJ-2 normal outcomes under gapattr
P("\n" + "=" * 110 + "\nAJ-2 NORMAL OUTCOMES OF EVERY LAUNCH KIND UNDER GAPATTR (RH): files written and their attribution")


def show_attr(label, pkg, rs="RH"):
    rule = {"RG": "RG4", "RH": "RH1"}[rs]
    att = attribute(pkg["rd"], sorted(pkg["files"]), dirs_of(pkg), records_for_layer1(pkg, rs), specs_of(pkg), pkg["events"], rule)
    P("\n### " + label)
    for rel in sorted(att):
        h = att[rel]
        P("  %-52s writer %-44s -> %s" % (rel, ("%s %s" % pkg["files"][rel])[:44], "; ".join("%s %s" % (c, i) for i, c in h) if h else "GAP"))
    OUT.setdefault("AJ2_attr", {})[label] = {r: att[r] for r in att}
    return evaluate(label + " [verdict]", pkg, ("RG", "RH"), variants=("Mr",), key="AJ2 " + label)


show_attr("N-1 cells m = 5 measured (S5 t0 retained, t1 not retained)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), ms("S5_t1", "S5_t1", retained=False)], basis=BASIS_M5, row=485))
show_attr("N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out)", resolve(
    "cells_m5", [ms("S5_t0 timeout", "S5_t0", rc=-9, outcome="timeout"), ms("S5_t1 memory", "S5_t1", rc=-11, outcome="memory_exhausted")], basis=BASIS_M5, row=485))
show_attr("N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0")], basis=BASIS_M4, row=488))
show_attr("N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid", outcome="crashed", rc=1, partial_npz=True), cj("grid_raw_t1", "grid_raw_t1", job="grid"),
                 ms("raw_t1", "raw_t1")], basis=BASIS_M4, row=488))
a1_ = ms("S5_t1 attempt 1", "S5_t1", outcome="ssf", in_attempt_record=True)
a2_ = ms("S5_t1 attempt 2", "S5_t1", in_attempt_record=True)
show_attr("N-5 SE-3 re-solve at S-1 (2 attempts)", resolve("cells_m5", [ms("S5_t0", "S5_t0"), a1_, a2_], basis=BASIS_M5, row=485,
                                                         resolves=[("solver", "S5_t1", [a1_["lid"], a2_["lid"]])]))
h1 = L("health d222 attempt 1", "health", "health_p1073741831_d222", outcome="ssf", in_attempt_record=True)
h2 = L("health d222 attempt 2", "health", "health_p1073741831_d222", in_attempt_record=True)
show_attr("N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves", resolve(
    "controls_a1", [L("gp", "gp", "controls_a1_pari"), h1, h2, L("health d444", "health", "health_p1073741831_d444"),
                    cj("ctl_a1_torsion_S3_rq", "ctl_a1_torsion_S3_rq"), ms("ctl_a1_planted_torsion_S3_rq", "ctl_a1_planted_torsion_S3_rq")],
    gate=True, row=480, resolves=[("health", "health_p1073741831_d222", [h1["lid"], h2["lid"]])],
    extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))]))
show_attr("N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)],
    basis=BASIS_M4, row=488))
show_attr("N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211)", resolve(
    "cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"), cg("callgrind raw_t0", "raw_t0", rc=-9, outcome="timeout")],
    basis=BASIS_M4, row=488))
show_attr("N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962)", resolve(
    "build", [cj("build_4111_S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True), cj("build_4111_S4", "build_4111_ecgfp5_shaped_S4_m4", cached=True)],
    basis=BASIS_BUILD, row=483))
show_attr("N-10 fixture4: uncached builds and solves", resolve(
    "fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481))
show_attr("N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C)", resolve(
    "cells_m4", [cj("grid_raw_t0 refused meta", "grid_raw_t0", job="grid", outcome="refused_meta"),
                 cj("grid_raw_t1 refused before fork", "grid_raw_t1", job="grid", created=False, p227=False, exec_=False, report=None, rc=None, pair=None, outcome="refused_to_start"),
                 cj("grid_raw_t2 ERR", "grid_raw_t2", job="grid", report="ERR", rc=97, p227=False, pair=None, exec_=False, outcome="refused_to_start"),
                 ms("raw_t3", "raw_t3")], basis=BASIS_M4, row=488))
show_attr("N-12 anchor-identity: comparator, uncached build, gb_only solves", resolve(
    "anchor", [L("comparator", "comparator", "comparator"), cj("anchor_S4", "anchor_S4"), ms("anchor_v2_t0", "anchor_v2_t0", gb=True),
               ms("anchor_comparator_system", "anchor_comparator_system", gb=True)], gate=True, row=478))
show_attr("N-13 Z-C5 (no launch; directories only)", resolve("cells_m5", [], basis=BASIS_M5, row=486))

P("\n--- AJ-2 (1) LISTING CHECK under gapattr RH-1 AS WORDED (launch sets RECONSTRUCTED, CRG-9)")
listing_check("RH1", GATE, label="(gapattr)")

# ============================================================================ AJ-3 cap-mismatch outcomes and RKR-4 (b) rows
P("\n" + "=" * 110 + "\nAJ-3 CAP-MISMATCH OUTCOMES (RH-2) AND THE RKR-4 (b) PASS / PASS_ZL ROWS: RF vs RG vs RH")
p8 = dict(report="OK", rc=98, pair=(CAP - 1, CAP - 1), exec_=False, outcome="refused_to_start")
p9 = dict(report="OK", rc=98, pair=(CAP, CAP - 1), exec_=False, outcome="crashed")
for kind, basis in (("cells_m5", BASIS_M5), ("cells_m4", BASIS_M4), ("build", BASIS_BUILD)):
    evaluate("CM %s: every launch P-8" % kind, resolve(kind, [ms("P-8 a", "t0", **p8), ms("P-8 b", "t1", **p8)], basis=basis), variants=("Mr",), key="CM %s P8" % kind)
    evaluate("CM %s: every launch P-9" % kind, resolve(kind, [ms("P-9 a", "t0", **p9), ms("P-9 b", "t1", **p9)], basis=basis), variants=("Mr",), key="CM %s P9" % kind)
    evaluate("CM %s: mixture, one P-9 launch and one measured launch (pair = cap, exec)" % kind,
             resolve(kind, [ms("P-9", "t0", **p9), ms("measured", "t1")], basis=basis), variants=("Mr",), key="CM %s mix" % kind)
evaluate("CM controls (gate): one P-9 build child", resolve("controls", [cj("P-9 build", "ctl_S3", **p9), ms("ok", "ctl_planted_S3")], gate=True, row=478),
         variants=("Mr",), key="CM controls")
rows = [
    ("478 G1..G4 completed_valid (fixture shape: uncached builds, raw grids, solves, callgrind)", resolve(
        "fixture", [cj("fixture_S3", "fixture_S3"), cj("fx_reg0_raw_x", "fx_reg0_raw_x", job="grid"), ms("fx_reg0_raw_x", "fx_reg0_raw_x"),
                    cg("cg fx_reg0_raw_x", "fx_reg0_raw_x"), ms("fx_reg0_S3", "fx_reg0_S3"), cg("cg fx_reg0_S3", "fx_reg0_S3")], gate=True, row=478)),
    ("480 controls_a1 image", resolve("controls_a1", [L("gp", "gp", "controls_a1_pari"), L("health", "health", "health_p1073741831_d222"),
                                                      cj("ctl_a1_S3_rescaled", "ctl_a1_S3_rescaled")], gate=True, row=480,
                                      extra_files=[("health/health-1073741831.json", ("driver", "a1_health 251"))])),
    ("481 fixture4 launched", resolve("fixture4", [cj("f4_S4", "f4_S4"), ms("f4_t0_S4", "f4_t0_S4")], row=481)),
    ("482 Z-F4 (zero call)", resolve("fixture4", [], row=482)),
    ("483 build (cached)", resolve("build", [cj("build S5", "build_4111_ecgfp5_shaped_S5_m5", cached=True)], basis=BASIS_BUILD, row=483)),
    ("485 cells m = 5 measured", resolve("cells_m5", [ms("S5_t0", "S5_t0")], basis=BASIS_M5, row=485)),
    ("485 cells m = 5 measured, one SE-3 re-solve", pb3),
    ("486 Z-C5", resolve("cells_m5", [], basis=BASIS_M5, row=486)),
    ("488 cells m = 4", pb2),
    ("488 cells m = 4, callgrind child failed", resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0"),
                                                                     cg("cg raw_t0", "raw_t0", rc=1, outcome="crashed", cg_out_left=True)], basis=BASIS_M4, row=488)),
    ("489 aggregate v2", resolve("aggregate", [], basis="X-10 aggregate_a1", row=489)),
]
for lab, pkg in rows:
    evaluate("RKR-4 (b) row " + lab, pkg, ("RF", "RG", "RH"), variants=("Mr",), key="row " + lab)

# ============================================================================ added in the final version
P("\n" + "=" * 110 + "\nADDED OBJECTS (final version)")
P("\n--- RH-6 (i) (19) third case as worded: 'one launch record of the tag removed yields a recorder gap and FAIL'")
for n in (2, 3, 6):
    for k in range(1, n + 1):
        q = resolved_cell(drop={k}, n=n)
        P("  %d attempts, record of attempt %d removed: RH-1 gaps %s; RH verdict %s (Mr)" % (n, k, gaps(q, "RH"), verdict(q, "RH", "Mr")))
        OUT.setdefault("RH6_19_single_removal", []).append({"attempts": n, "removed": k, "gaps": gaps(q, "RH"), "verdict": verdict(q, "RH", "Mr")})
P("\n--- RH-6 (i) (22) with a raw_grid child job (its .npz removed at v2_driver 144)")
g22 = resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid", recorded=False), ms("raw_t0", "raw_t0"),
                           cj("grid_raw_t1", "grid_raw_t1", job="grid"), ms("raw_t1", "raw_t1")], basis=BASIS_M4, row=488)
P("  gaps %s; the expected list '.spec.json, .stdout, .stderr, .npz and .meta.json' contains .npz: %s"
  % (gaps(g22, "RH"), "child/grid_raw_t0.npz" in gaps(g22, "RH")))
OUT["RH6_22_raw_grid"] = gaps(g22, "RH")
iv1 = resolve("anchor", [L("comparator", "comparator", "comparator"), cj("anchor_S4", "anchor_S4")], gate=True, row=478,
              extra_files=[("comparator/unknown-writer.dat", ("process-not-known-to-the-rules", "e.g. a grandchild (RFL-1)"))])
show_attr("IV-1 comparator/ holds a file written by a process no rule knows: RH-1 (iv) attributes it by its directory", iv1)
rel1 = resolve("cells_m4", [cj("grid_raw_t0", "grid_raw_t0", job="grid"), ms("raw_t0", "raw_t0")], basis=BASIS_M4, row=488,
               rd=RUNS + "/RUN-X")
rel1["rd_check"] = "/elsewhere/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/runs/RUN-X"
evaluate("REL-1 the same package read at another absolute root (recorded paths from run time)", rel1, ("RH",), variants=("Mr",), key="REL-1")

with open(os.path.join(SCR, "rt_eval.json"), "w") as fh:
    json.dump(OUT, fh, indent=1, default=str)
P("\nWROTE rt_eval.json with %d keys" % len(OUT))
````

### `tables.py`

- sha256: `7c731da6d2e440eb0660439d7a95032287ca7a65d6a148f85fcc9d6d710653f0`
- bytes: 7937; lines: 124
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B tables.py   (cwd <scratch>/rt_94cc33)`
- role: Writes the listing tables (tables.yaml.part, tables.md.part) by copying attributions from rt_eval.json; computes none.

````text
#!/usr/bin/env python3
# TASK-20260924-94cc33 listing-table writer (scratch). Reads rt_eval.json (the evaluator's recorded attributions)
# and listing.json (the O_NOATIME listings) from this directory and writes two text parts for the deliverables:
#   tables.yaml.part  (a top-level YAML key listing_tables:, every scalar JSON-quoted)
#   tables.md.part    (the same tables as markdown)
# It computes no attribution itself: every clause shown is copied from rt_eval.json. Imports nothing from the
# repository and no third-party module.
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
R = json.load(open(os.path.join(HERE, "rt_eval.json")))
LST = json.load(open(os.path.join(HERE, "listing.json")))
GATE = ["RUN-GFPN-f6a21a", "RUN-GFPN-902222", "RUN-GFPN-f5412a", "RUN-GFPN-bfe956"]
FIVE = ("child/", "solver/", "health/", "comparator/", "pari/")
q = json.dumps


def cell(hits):
    if not hits:
        return "NONE (recorder gap)"
    return "; ".join("%s %s" % (c, i) if i != "-" else c for i, c in hits)


def outside(pk):
    return sorted(x["path"] for x in LST["packages"][pk]["entries"] if x["type"] != "dir" and not x["path"].startswith(FIVE))


tables = [
    ("childend_RG4_as_worded", "listing_RG4", GATE,
     "AJ-0 (d): childend RG-4 (b) as worded; clause names: stdout/stderr, argv exact, argv directory"),
    ("gapattr_RH1_as_worded", "listing_RH1", GATE,
     "AJ-2 (1): gapattr RH-1 (i)-(vi) as worded with the non-launch list"),
    ("gapattr_RH1_weakened_v_ctl_S3_record_removed", "listing_RH1w_drop_childjob:ctl_S3", ["RUN-GFPN-bfe956"],
     "AJ-0 (e0): RH-1 with (v) weakened to 'every file under child/ is attributed to some launch record', record childjob:ctl_S3 removed"),
    ("gapattr_RH1_as_worded_ctl_S3_record_removed", "listing_RH1_drop_childjob:ctl_S3", ["RUN-GFPN-bfe956"],
     "AJ-0 (e0): RH-1 as worded, record childjob:ctl_S3 removed"),
]

y = []
y.append("listing_tables:")
y.append("  source: %s" % q("rt_eval.json (sha256 %s) written by rt_eval.py; listing.json (sha256 %s)" % (
    hashlib.sha256(open(os.path.join(HERE, "rt_eval.json"), "rb").read()).hexdigest(),
    hashlib.sha256(open(os.path.join(HERE, "listing.json"), "rb").read()).hexdigest())))
y.append("  reconstruction_rule: %s" % q(
    "CRG-9: launch sets RECONSTRUCTED from the files by the frozen naming: child/<tag>.spec.json -> one child-job record "
    "(argv [<python>, -B, implementation-v2/v2_child.py, <rd>/child/<tag>.spec.json], stdout/stderr child/<tag>.stdout/.stderr; "
    "v2_driver.py 92-102); solver/<tag>.ms.log or health/<tag>.ms.log -> one msolve record (argv -f <dir>/<tag>.ms -o <dir>/<tag>.ms.out; "
    "stdout/stderr <tag>.ms.log/.ms.err; v2_driver.py 161-166, a1_health.py 141-147); solver/<tag>.callgrind.stdout -> one callgrind record "
    "(argv valgrind --tool=callgrind --callgrind-out-file=<dir>/<tag>.callgrind.out msolve ... -f <tag>.ms -o <tag>.cg.ms.out; "
    "v2_solver.py 515-518, v2_driver.py 208-209); comparator/stdout.log -> one comparator record (argv [<comparator python>, "
    "k4a_anchor_system.py, <rd>/comparator]; v2_driver.py 647-651); pari/<tag>.gp.stdout -> one gp record (a1_pari.py 91-96). "
    "child_end exec for a child job whose .meta.json or .npz exists (only v2_child writes them, after exec) and for every other "
    "reconstructed launch. Spec 'out' values read from the archived spec files (specout.json). Paths compared as absolute paths "
    "under the package's recorded GFPN_RUN_DIR, which equals its current path for all four packages (command.txt). A listing "
    "check is a reading of r3 artifacts under r4 rule text, never a result about any package's verdict and never evidence about D."))
md = []
md.append("## Listing tables (every file of the five directories of the four archived r3 gate packages)\n")
md.append("Launch sets are RECONSTRUCTED (CRG-9); the rule is stated in section 3 and in the YAML "
          "`listing_tables.reconstruction_rule`. Each cell names the clause and the reconstructed record that attributes "
          "the file, every clause that applies, in record order. `NONE (recorder gap)` means no clause attributes it and it "
          "is not on the non-launch list. These are readings of r3 artifacts under r4 rule text, never results about any "
          "package's verdict and never evidence about D.\n")
for key, src, pkgs, note in tables:
    y.append("  %s:" % key)
    y.append("    rule: %s" % q(note))
    for pk in pkgs:
        t = R[src][pk]
        y.append("    %s:" % pk)
        y.append("      files_in_the_five_directories: %d" % t["n_files"])
        y.append("      reconstructed_launch_records: %d" % t["n_records"])
        y.append("      files_by_first_clause: {%s}" % ", ".join("%s: %d" % (q(k), v) for k, v in sorted(t["first_clause_counts"].items())))
        y.append("      unattributed_count: %d" % len(t["gaps"]))
        if t["gaps"]:
            y.append("      unattributed:")
            for g in t["gaps"]:
                y.append("        - %s" % q(g))
        else:
            y.append("      unattributed: []")
        y.append("      files:")
        for f in sorted(t["attribution"]):
            y.append("        %s: %s" % (q(f), q(cell(t["attribution"][f]))))
y.append("  files_outside_the_five_directories:")
y.append("    note: %s" % q("Outside RH-1's and RG-4 (b)'s scope (the five directories); listed for completeness, not attributed."))
for pk in GATE:
    o = outside(pk)
    y.append("    %s:" % pk)
    y.append("      count: %d" % len(o))
    y.append("      files: [%s]" % ", ".join(q(x) for x in o))

# markdown: one combined table per package (childend RG-4 (b) and gapattr RH-1), then the ctl_S3-removed tables
for pk in GATE:
    a = R["listing_RG4"][pk]
    b = R["listing_RH1"][pk]
    md.append("### %s: %d files in the five directories, %d reconstructed launch records\n" % (pk, a["n_files"], a["n_records"]))
    md.append("- childend RG-4 (b) as worded: first-clause counts %s; unattributed %d." % (
        ", ".join("%s %d" % (k, v) for k, v in sorted(a["first_clause_counts"].items())), len(a["gaps"])))
    md.append("- gapattr RH-1 as worded: first-clause counts %s; unattributed %d.\n" % (
        ", ".join("%s %d" % (k, v) for k, v in sorted(b["first_clause_counts"].items())), len(b["gaps"])))
    md.append("| # | file | childend RG-4 (b) as worded | gapattr RH-1 as worded |")
    md.append("|---|---|---|---|")
    for n, f in enumerate(sorted(a["attribution"]), start=1):
        md.append("| %d | `%s` | %s | %s |" % (n, f, cell(a["attribution"][f]), cell(b["attribution"][f])))
    md.append("")
    o = outside(pk)
    md.append("Files outside the five directories (%d; outside the attribution rules' scope): %s\n" % (len(o), ", ".join("`%s`" % x for x in o)))
a = R["listing_RH1w_drop_childjob:ctl_S3"]["RUN-GFPN-bfe956"]
b = R["listing_RH1_drop_childjob:ctl_S3"]["RUN-GFPN-bfe956"]
md.append("### RUN-GFPN-bfe956 with the reconstructed record childjob:ctl_S3 removed (AJ-0 (e0))\n")
md.append("- RH-1 with (v) weakened: first-clause counts %s; unattributed %d." % (
    ", ".join("%s %d" % (k, v) for k, v in sorted(a["first_clause_counts"].items())), len(a["gaps"])))
md.append("- RH-1 as worded: first-clause counts %s; unattributed %d: %s.\n" % (
    ", ".join("%s %d" % (k, v) for k, v in sorted(b["first_clause_counts"].items())), len(b["gaps"]), ", ".join("`%s`" % g for g in b["gaps"])))
md.append("| # | file | RH-1, (v) weakened | RH-1 as worded |")
md.append("|---|---|---|---|")
for n, f in enumerate(sorted(a["attribution"]), start=1):
    md.append("| %d | `%s` | %s | %s |" % (n, f, cell(a["attribution"][f]), cell(b["attribution"][f])))
md.append("")

open(os.path.join(HERE, "tables.yaml.part"), "w").write("\n".join(y) + "\n")
open(os.path.join(HERE, "tables.md.part"), "w").write("\n".join(md) + "\n")
print("yaml lines %d, md lines %d" % (len(y), len(md)))
````

### `selfcheck.py`

- sha256: `434c5a252bacd7c5603c37266db9c9bdb875a687338d09bbcc206eef02c100b8`
- bytes: 1291; lines: 27
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B selfcheck.py <files>   (cwd <scratch>/rt_94cc33)`
- role: CRG-7 name self-check: reads words.txt at run time; prints only that file's sha256, the word count, and hit counts / line numbers.

````text
#!/usr/bin/env python3
# CRG-7 name self-check (scratch). Reads its word list AT RUN TIME from words.txt next to this script (a file the
# dispatching session placed outside write_scope; one word per line), and counts case-insensitive occurrences of
# each listed word in each file named on the command line. Prints ONLY: the sha256 of words.txt, the number of
# words, and per file the number of hits and the line numbers holding a hit. It never prints a listed word.
# Imports nothing from the repository.
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
raw = open(os.path.join(HERE, "words.txt"), "rb").read()
words = [w.strip().lower() for w in raw.decode("utf-8", "replace").splitlines() if w.strip()]
print("words.txt sha256 %s; %d words" % (hashlib.sha256(raw).hexdigest(), len(words)))
total = 0
for path in sys.argv[1:]:
    hits, lines = 0, []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh, start=1):
            low = line.lower()
            n = sum(low.count(w) for w in words)
            if n:
                hits += n
                lines.append(i)
    total += hits
    print("%s: %d hits; lines %s" % (os.path.basename(path), hits, lines[:50]))
print("TOTAL HITS %d" % total)
````

### `appendix.py`

- sha256: `c59102ca35a20b7ef84330120b32f25a643b450ceecad94bef5647340644df8c`
- bytes: 4348; lines: 53
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 60 python3 -B appendix.py   (cwd <scratch>/rt_94cc33)`
- role: Writes this appendix (appendix.md.part).

````text
#!/usr/bin/env python3
# TASK-20260924-94cc33 appendix writer (scratch). Reproduces each computation script of this review VERBATIM
# (and the final outputs named below), each with its sha256, size and the argv it ran under, into
# appendix.md.part in this directory. Reads only files in this directory. Imports nothing from the repository.
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
ENV = "PYTHONDONTWRITEBYTECODE=1"
ITEMS = [
    ("integrity.py", "python3 -B integrity.py | tee integrity.out   (cwd <scratch>/rt_94cc33)",
     "CRG-2 (c): compares the path_sha256 field of five archive receipts with on-disk bytes. Output: integrity.out."),
    ("listing.py", ENV + " timeout 120 python3 -B listing.py listing.json   (cwd <scratch>/rt_94cc33)",
     "O_NOATIME directory listing of the four archived r3 gate packages; lstat of every directory before and after. Output: listing.json."),
    ("specout.py", ENV + " timeout 120 python3 -B specout.py listing.json specout.json   (cwd <scratch>/rt_94cc33)",
     "O_NOATIME read of every child/*.spec.json 'out' value and the '# GFPN_RUN_DIR=' line of command.txt. Output: specout.json."),
    ("scan.py", ENV + " timeout 300 python3 -B scan.py /home/user/crypto-autoresearcher > scan.out   (cwd <scratch>/rt_94cc33)",
     "ast / dis static scan of the three implementation trees' source text, under an audit-hook guard refusing imports of scanned modules and every process launch. Output: scan.out."),
    ("rt_eval.v1.py", "NEVER RUN",
     "First evaluator version. Superseded before any run: writers were stored as space-joined strings although launch ids contain spaces."),
    ("rt_eval.v2.py", "ran once; the argv form retained is " + ENV + " timeout 300 python3 -B rt_eval.py > rt_eval.out (cwd <scratch>/rt_94cc33), the file then being the current rt_eval.py; its output is kept as rt_eval.v2.run1.out",
     "Second version. The run failed with TypeError (L() got multiple values for keyword argument 'in_raw'); no JSON was written."),
    ("rt_eval.v3.py", "ran once; argv form as for v2; outputs kept as rt_eval.v3.out and rt_eval.v3.json",
     "Third version. Superseded: record-removed constructions were tagged PLANNED-BASIS REFUSAL because resolve() defaulted designed=True."),
    ("rt_eval.py", ENV + " timeout 300 python3 -B rt_eval.py > rt_eval.out   (cwd <scratch>/rt_94cc33)",
     "FINAL evaluator: every verdict of AJ-0..AJ-3 in this report is read from its output rt_eval.out and rt_eval.json."),
    ("tables.py", ENV + " timeout 120 python3 -B tables.py   (cwd <scratch>/rt_94cc33)",
     "Writes the listing tables (tables.yaml.part, tables.md.part) by copying attributions from rt_eval.json; computes none."),
    ("selfcheck.py", ENV + " timeout 60 python3 -B selfcheck.py <files>   (cwd <scratch>/rt_94cc33)",
     "CRG-7 name self-check: reads words.txt at run time; prints only that file's sha256, the word count, and hit counts / line numbers."),
    ("appendix.py", ENV + " timeout 60 python3 -B appendix.py   (cwd <scratch>/rt_94cc33)",
     "Writes this appendix (appendix.md.part)."),
    ("integrity.out", "(output of integrity.py)", "Reproduced verbatim."),
    ("scan.out", "(output of scan.py)", "Reproduced verbatim."),
    ("rt_eval.out", "(output of the final rt_eval.py)", "Reproduced verbatim; 1141 lines."),
]
out = ["## Appendix: computation scripts and outputs, verbatim\n",
       "Every file below is in the reviewer's transient scratch directory `<scratch>/rt_94cc33/` (outside the repository; "
       "the literal scratch path is not written into this report). Each is reproduced byte for byte between the fences; the "
       "sha256 is of the file's bytes. No listed word required masking (the self-check found 0 hits in every file reproduced).\n"]
for name, argv, note in ITEMS:
    b = open(os.path.join(HERE, name), "rb").read()
    out.append("### `%s`\n" % name)
    out.append("- sha256: `%s`" % hashlib.sha256(b).hexdigest())
    out.append("- bytes: %d; lines: %d" % (len(b), b.count(b"\n")))
    out.append("- argv: `%s`" % argv)
    out.append("- role: %s\n" % note)
    out.append("````text")
    out.append(b.decode("utf-8").rstrip("\n"))
    out.append("````\n")
open(os.path.join(HERE, "appendix.md.part"), "w").write("\n".join(out) + "\n")
print("appendix items %d" % len(ITEMS))
````

### `integrity.out`

- sha256: `beefb79963a06053f4c28785afce7ad226e2d2f9a996a29b100d4b1cfcdd8476`
- bytes: 3393; lines: 45
- argv: `(output of integrity.py)`
- role: Reproduced verbatim.

````text
RECEIPT TASK-20260924-0c2fdc/snapshot-receipt.json
  OK  coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md
    receipt 0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8
    disk    0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8
  OK  coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml
    receipt b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f
    disk    b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f
RECEIPT TASK-20260924-7e8a5d/snapshot-receipt.json
  OK  coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md
    receipt 97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055
    disk    97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055
  OK  coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml
    receipt 139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4
    disk    139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4
RECEIPT TASK-20260924-71d070/snapshot-receipt.json
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json
    receipt 9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa
    disk    9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md
    receipt ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838
    disk    ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py
    receipt 00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c
    disk    00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c
RECEIPT TASK-20260924-ddfb69/snapshot-receipt.json
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json
    receipt 36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158
    disk    36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md
    receipt 5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7
    disk    5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py
    receipt ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558
    disk    ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558
RECEIPT TASK-20260924-a01341/snapshot-receipt.json
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py
    receipt 3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64
    disk    3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json
    receipt 49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4
    disk    49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4
  OK  experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md
    receipt 2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3
    disk    2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3
ALL_OK True
````

### `scan.out`

- sha256: `cde64163b4067793bdd6ce3264592302320b0ac77e5184389e1f33e73d6603fd`
- bytes: 9846; lines: 136
- argv: `(output of scan.py)`
- role: Reproduced verbatim.

````text
== guard: 256 refused names, sha256(sorted) 4200f056c940e60770363c6079cb9cac458676e2cf8cc35604f59dd186d012ef; stdlib/loaded collisions []; self-test [('import', 'refused'), ('os.fork', 'refused')]

== (exit_calls) 26
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py:114 sys.exit(main(sys.argv[1]))
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:60 sys.exit(96)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:69 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:81 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:54 sys.exit(2)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:243 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:208 os._exit(99)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:201 os._exit(98)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:266 os.kill(pid)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:196 os._exit(97)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py:280 sys.exit(1 if bad else 0)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py:145 sys.exit(main(sys.argv[1]))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py:439 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py:297 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py:148 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:378 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:417 sys.exit(main(args[0], aj))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:406 sys.exit(r3_reg1.main(sys.argv[2:]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:408 sys.exit(frozen_v2(sys.argv[2]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:410 sys.exit(frozen_a1(sys.argv[2]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks.py:298 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:115 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:84 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:333 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_reg1.py:352 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:583 sys.exit(main())

== (systemexit_raises) 17
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py:100 SystemExit('GFPN_RUN_DIR not set: launch through v2_run_wrapp)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py:433 SystemExit('REFUSING: development outputs never go under expe)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:52 SystemExit("REFUSING: --p %s does not match the plan package')
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:224 SystemExit("REFUSING: --p %s does not match the plan package')
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:233 SystemExit('REFUSING: arguments do not match the plan package)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_make_trial_plan.py:69 SystemExit('only the 31-bit plan is implemented as a writer; )
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv12.py:131 SystemExit('REFUSING: %s exists (a case is run once; a re-run)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:434 SystemExit('REFUSING: %s exists (DV-7 runs once; a re-run nee)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:141 SystemExit('REFUSING: expected 42 distinct minted ids, 31 v2 )
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:152 SystemExit('REFUSING: M is not a bijection from the 42 frozen)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:154 SystemExit('REFUSING: the r1 / r2 plan ids differ from the re)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:157 SystemExit('REFUSING: retirement lists differ from the parist)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:135 SystemExit('REFUSING: %s sha256 %s != bound %s' % (path, got,)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:295 SystemExit('REFUSING: %s fails the RC-4 (c) equality (%s != %)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:297 SystemExit('REFUSING: %s watchdogs differ from trial-plan-v2.)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:299 SystemExit('REFUSING: %s carries a forbidden task id' % name)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:318 SystemExit('REFUSING: %s exists; plans are written once' % pa)

== (exec_fork_spawn) 26
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py:59 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:182 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:49 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:181 os.fork
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:205 os.execv
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:533 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:204 os.execve
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py:121 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:303 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:61 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:372 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_toy.py:334 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:372 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks.py:205 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:278 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:93 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:538 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:100 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:492 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:502 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:96 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:99 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv6.py:324 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:477 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:73 subprocess.run
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:341 subprocess.run

== (hooks) 0

== (broad_handlers) 5
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:206 except BaseException (raise inside: False)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:100 except SystemExit (raise inside: False)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:103 except BaseException (raise inside: False)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:69 except SystemExit (raise inside: False)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:72 except BaseException (raise inside: False)

== (run_child_refs) 9
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py:101 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py:166 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py:650 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:517 run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:171 _run_child_locked [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py:147 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py:96 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks.py:190 V.run_child [Load]
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:80 V.run_child [Load]

== (from_v2_solver_import) 0

== (defs) 2
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:149 def run_child
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:177 def _run_child_locked

== (dis) v2_solver.py sha256 0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d, compiled from text with 3.11.15; _run_child_locked first line 177; lines 178-183:
  178 LOAD_GLOBAL            NULL + os
  178 LOAD_ATTR              pipe
  178 PRECALL                
  178 CALL                   
  178 UNPACK_SEQUENCE        
  178 STORE_FAST             rep_r
  178 STORE_FAST             rep_w
  179 LOAD_GLOBAL            NULL + os
  179 LOAD_ATTR              pipe
  179 PRECALL                
  179 CALL                   
  179 UNPACK_SEQUENCE        
  179 STORE_FAST             go_r
  179 STORE_FAST             go_w
  180 LOAD_GLOBAL            NULL + time
  180 LOAD_ATTR              time
  180 PRECALL                
  180 CALL                   
  180 STORE_FAST             t0
  181 LOAD_GLOBAL            NULL + os
  181 LOAD_ATTR              fork
  181 PRECALL                
  181 CALL                   
  181 STORE_FAST             pid
  182 LOAD_FAST              pid
  182 LOAD_CONST             0
  182 COMPARE_OP             ==
  182 EXTENDED_ARG           
  182 POP_JUMP_FORWARD_IF_FALSE to 1350
  183 NOP                    

== guard attempt counts: import 0, launch 0
````

### `rt_eval.out`

- sha256: `1c88d680bff71dbcc94039890726928b433bc6e9841df1e821a32900898e1290`
- bytes: 104926; lines: 1141
- argv: `(output of the final rt_eval.py)`
- role: Reproduced verbatim; 1141 lines.

````text
==============================================================================================================
AJ-0 KNOWN-ANSWER CONTROL (CRG-4 (a)-(e))

--- (a) readbackclose RK-1 / RK-3 AS WORDED (RK), RF for contrast

### KA-a1 P-16 (v2_solver 181 CALL then STORE_FAST pid; raise leaves the driver: raw wrapper-written)
  record[P-16 raise at 181       ] RK  child_created=False class=None | (iii) created child recorded child_created false
  record[P-16 raise at 181       ] RF  child_created=undetermined class=None
  package RK  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mc verdict PASS    items []                 defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] FAIL-OPEN ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)', '(v)'] 

### KA-a2 P-F2 after P-14a (release raises in run_child's finally over a raise at 214)
  record[P-F2 after P-14a        ] RK  child_created=False class=None | (iii) created child recorded child_created false
  record[P-F2 after P-14a        ] RF  child_created=True class=None
  package RK  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] 
  package RK  k=1 Mc verdict PASS    items []                 defs ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)'] FAIL-OPEN ['(ii-ANY)', '(ii-LR)', '(iii)', '(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)', '(v)'] 
  package RF  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)', '(v)'] 

### KA-a3 W-1 (driver exits before any launch; wrapper writes raw-result.json, r3_run_wrapper 491-505)
  package RK  k=0 Mr verdict PASS_ZL items ['66-67']          defs ['(v)']                  FAIL-OPEN ['(v)']
  package RK  k=0 Mc verdict PASS_ZL items ['66-67']          defs ['(v)']                  FAIL-OPEN ['(v)']
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(v)']                  
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(v)']                  

--- (b) failclosed AS WORDED (RF): FO-1, foreign-file write failed / interrupted

### KA-b FO-1 variant C, foreign write failed, escaped exit 1
  record[FO-1 C failed rc1       ] RF  child_created=True class=C | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 C failed rc1       ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 C failed rc1       ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RG  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### KA-b FO-1 variant C, foreign write failed, escaped exit -2
  record[FO-1 C failed rc-2      ] RF  child_created=True class=C | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 C failed rc-2      ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 C failed rc-2      ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RG  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### KA-b FO-1 variant C, foreign write interrupted, escaped exit 1
  record[FO-1 C interrupted rc1  ] RF  child_created=True class=C | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 C interrupted rc1  ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 C interrupted rc1  ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RG  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### KA-b FO-1 variant C, foreign write interrupted, escaped exit -2
  record[FO-1 C interrupted rc-2 ] RF  child_created=True class=C | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 C interrupted rc-2 ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 C interrupted rc-2 ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=0 Mc verdict FAIL    items ['66-67']          defs ['(iv)']                 
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RG  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RG  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=0 Mr verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=0 Mc verdict FAIL    items ['66-67']          defs ['(ii-ANY)', '(ii-LR)']  infrastructure-stop (RG-2)
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### KA-b FO-1 variant B, foreign write failed, escaped exit 1
  record[FO-1 B failed rc1       ] RF  child_created=True class=B | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 B failed rc1       ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 B failed rc1       ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       
  package RG  k=1 Mr verdict FAIL    items []                 defs []                       
  package RG  k=1 Mc verdict FAIL    items []                 defs []                       
  package RH  k=0 Mr verdict FAIL    items []                 defs []                       
  package RH  k=0 Mc verdict FAIL    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### KA-b FO-1 variant B, foreign write failed, escaped exit -2
  record[FO-1 B failed rc-2      ] RF  child_created=True class=B | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 B failed rc-2      ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 B failed rc-2      ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       
  package RG  k=1 Mr verdict FAIL    items []                 defs []                       
  package RG  k=1 Mc verdict FAIL    items []                 defs []                       
  package RH  k=0 Mr verdict FAIL    items []                 defs []                       
  package RH  k=0 Mc verdict FAIL    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### KA-b FO-1 variant B, foreign write interrupted, escaped exit 1
  record[FO-1 B interrupted rc1  ] RF  child_created=True class=B | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 B interrupted rc1  ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 B interrupted rc1  ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       
  package RG  k=1 Mr verdict FAIL    items []                 defs []                       
  package RG  k=1 Mc verdict FAIL    items []                 defs []                       
  package RH  k=0 Mr verdict FAIL    items []                 defs []                       
  package RH  k=0 Mc verdict FAIL    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### KA-b FO-1 variant B, foreign write interrupted, escaped exit -2
  record[FO-1 B interrupted rc-2 ] RF  child_created=True class=B | (iv)-relevant foreign-process record; detected by: NOTHING
  record[FO-1 B interrupted rc-2 ] RG  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  record[FO-1 B interrupted rc-2 ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RF  k=0 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=0 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RF  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       
  package RG  k=1 Mr verdict FAIL    items []                 defs []                       
  package RG  k=1 Mc verdict FAIL    items []                 defs []                       
  package RH  k=0 Mr verdict FAIL    items []                 defs []                       
  package RH  k=0 Mc verdict FAIL    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

--- (c) childend AS WORDED (RG): PB-2 and PB-3 (RF and RH for contrast)

### KA-c1 PB-2 cells m = 4, raw_grid child leaves child/grid_raw_t0.meta.json (v2_driver 1161 -> 133-147)
  record[grid_raw_t0 child       ] RF  child_created=True class=B
  record[grid_raw_t0 child       ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0 child       ] RH  child_created=True class=B child_end=exec
  record[msolve raw_t0           ] RF  child_created=True class=B
  record[msolve raw_t0           ] RG  child_created=True class=B child_end=exec
  record[msolve raw_t0           ] RH  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RF  child_created=True class=B
  record[callgrind raw_t0        ] RG  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RF  k=0 Mc verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mc verdict PASS    items []                 defs []                       

### KA-c2 PB-3 cells m = 5 with one SE-3 re-solve at S-1 (r3_resolve 224-238, 310)
  record[S5_t0                   ] RF  child_created=True class=B
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1 (SSF)   ] RF  child_created=True class=B
  record[S5_t1 attempt 1 (SSF)   ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1 (SSF)   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RF  child_created=True class=B
  record[S5_t1 attempt 2         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RF  k=0 Mc verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mc verdict PASS    items []                 defs []                       

--- (d) LISTING CHECK under childend RG-4 (b) AS WORDED (launch sets RECONSTRUCTED, CRG-9)

--- listing check under RG4 (childend)
  RUN-GFPN-f6a21a: 284 files in the five directories, 88 reconstructed launch records ({'callgrind': 36, 'childjob': 16, 'comparator': 0, 'gp': 0, 'msolve': 36}); files by first clause {'NONE (gap)': 20, 'argv exact': 88, 'stdout/stderr': 176}
    unattributed: 20 (child/*.meta.json 16; child/*.npz 4; other 0)
      GAP child/fixture_S3.meta.json
      GAP child/fixture_S3.npz
      GAP child/fixture_S3_rescaled.meta.json
      GAP child/fixture_S3_rescaled.npz
      GAP child/fixture_torsion_S3_norm.meta.json
      GAP child/fixture_torsion_S3_norm.npz
      GAP child/fixture_torsion_S3_rq.meta.json
      GAP child/fixture_torsion_S3_rq.npz
      GAP child/fx_fresh1_raw_u.meta.json
      GAP child/fx_fresh1_raw_x.meta.json
      GAP child/fx_fresh2_raw_u.meta.json
      GAP child/fx_fresh2_raw_x.meta.json
      GAP child/fx_planted0_raw_u.meta.json
      GAP child/fx_planted0_raw_x.meta.json
      GAP child/fx_planted1_raw_u.meta.json
      GAP child/fx_planted1_raw_x.meta.json
      GAP child/fx_reg0_raw_u.meta.json
      GAP child/fx_reg0_raw_x.meta.json
      GAP child/fx_reg1_raw_u.meta.json
      GAP child/fx_reg1_raw_x.meta.json
  RUN-GFPN-902222: 284 files in the five directories, 88 reconstructed launch records ({'callgrind': 36, 'childjob': 16, 'comparator': 0, 'gp': 0, 'msolve': 36}); files by first clause {'NONE (gap)': 20, 'argv exact': 88, 'stdout/stderr': 176}
    unattributed: 20 (child/*.meta.json 16; child/*.npz 4; other 0)
      GAP child/fixture_S3.meta.json
      GAP child/fixture_S3.npz
      GAP child/fixture_S3_rescaled.meta.json
      GAP child/fixture_S3_rescaled.npz
      GAP child/fixture_torsion_S3_norm.meta.json
      GAP child/fixture_torsion_S3_norm.npz
      GAP child/fixture_torsion_S3_rq.meta.json
      GAP child/fixture_torsion_S3_rq.npz
      GAP child/fx_fresh1_raw_u.meta.json
      GAP child/fx_fresh1_raw_x.meta.json
      GAP child/fx_fresh2_raw_u.meta.json
      GAP child/fx_fresh2_raw_x.meta.json
      GAP child/fx_planted0_raw_u.meta.json
      GAP child/fx_planted0_raw_x.meta.json
      GAP child/fx_planted1_raw_u.meta.json
      GAP child/fx_planted1_raw_x.meta.json
      GAP child/fx_reg0_raw_u.meta.json
      GAP child/fx_reg0_raw_x.meta.json
      GAP child/fx_reg1_raw_u.meta.json
      GAP child/fx_reg1_raw_x.meta.json
  RUN-GFPN-f5412a: 32 files in the five directories, 7 reconstructed launch records ({'callgrind': 0, 'childjob': 1, 'comparator': 1, 'gp': 0, 'msolve': 5}); files by first clause {'NONE (gap)': 2, 'argv directory': 5, 'argv exact': 11, 'stdout/stderr': 14}
    unattributed: 2 (child/*.meta.json 1; child/*.npz 1; other 0)
      GAP child/anchor_S4.meta.json
      GAP child/anchor_S4.npz
  RUN-GFPN-bfe956: 83 files in the five directories, 19 reconstructed launch records ({'callgrind': 0, 'childjob': 11, 'comparator': 0, 'gp': 0, 'msolve': 8}); files by first clause {'NONE (gap)': 18, 'argv exact': 27, 'stdout/stderr': 38}
    unattributed: 18 (child/*.meta.json 11; child/*.npz 7; other 0)
      GAP child/ctl_S3.meta.json
      GAP child/ctl_S3.npz
      GAP child/ctl_S3_rescaled.meta.json
      GAP child/ctl_S3_rescaled.npz
      GAP child/ctl_identity_n3.meta.json
      GAP child/ctl_identity_n3.npz
      GAP child/ctl_identity_n5_m3.meta.json
      GAP child/ctl_identity_n5_m3.npz
      GAP child/ctl_identity_n5_m4.meta.json
      GAP child/ctl_identity_n5_m4.npz
      GAP child/ctl_raw_n5_m3.meta.json
      GAP child/ctl_raw_n5_m4.meta.json
      GAP child/ctl_raw_planted.meta.json
      GAP child/ctl_raw_random.meta.json
      GAP child/ctl_torsion_S3_norm.meta.json
      GAP child/ctl_torsion_S3_norm.npz
      GAP child/ctl_torsion_S3_rq.meta.json
      GAP child/ctl_torsion_S3_rq.npz

--- (e) gapattr with RH-1 (v) WEAKENED vs AS WORDED, one child-job launch record removed
  (e0) file level on RUN-GFPN-bfe956 with the record of childjob:ctl_S3 removed:

--- listing check under RH1w (weakened)
  RUN-GFPN-bfe956: 83 files in the five directories, 18 reconstructed launch records ({'callgrind': 0, 'childjob': 10, 'comparator': 0, 'gp': 0, 'msolve': 8}); files by first clause {'(i)': 36, '(ii)': 26, '(v) weakened': 21}
    unattributed: 0 (child/*.meta.json 0; child/*.npz 0; other 0)

--- listing check under RH1 (worded)
  RUN-GFPN-bfe956: 83 files in the five directories, 18 reconstructed launch records ({'callgrind': 0, 'childjob': 10, 'comparator': 0, 'gp': 0, 'msolve': 8}); files by first clause {'(i)': 36, '(ii)': 26, '(v)': 16, 'NONE (gap)': 5}
    unattributed: 5 (child/*.meta.json 1; child/*.npz 1; other 3)
      GAP child/ctl_S3.meta.json
      GAP child/ctl_S3.npz
      GAP child/ctl_S3.spec.json
      GAP child/ctl_S3.stderr
      GAP child/ctl_S3.stdout

### KA-e1 controls (G4 shape, raw carries no pair), child-job record of ctl_S3 REMOVED (build ok: meta carries its pair)
  record[ctl_identity_n3         ] RH  child_created=True class=B child_end=exec
  record[ctl_identity_n3         ] RHw child_created=True class=B child_end=exec
  record[ctl_raw_random          ] RH  child_created=True class=B child_end=exec
  record[ctl_raw_random          ] RHw child_created=True class=B child_end=exec
  record[ctl_S3                  ] RH  NO LAUNCH RECORD (removed)
  record[ctl_S3                  ] RHw NO LAUNCH RECORD (removed)
  record[ctl_planted_S3          ] RH  child_created=True class=B child_end=exec
  record[ctl_planted_S3          ] RHw child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3.spec.json', 'child/ctl_S3.stderr', 'child/ctl_S3.stdout']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3.spec.json', 'child/ctl_S3.stderr', 'child/ctl_S3.stdout']
  package RHw k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']
  package RHw k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']

### KA-e2 cells m = 4, raw_grid child of target 0 crashed after exec (partial .npz, no meta), its record REMOVED
  record[grid_raw_t0 child       ] RH  NO LAUNCH RECORD (removed)
  record[grid_raw_t0 child       ] RHw NO LAUNCH RECORD (removed)
  record[msolve S4_t0            ] RH  child_created=True class=B child_end=exec
  record[msolve S4_t0            ] RHw child_created=True class=B child_end=exec
  record[grid_raw_t1 child       ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t1 child       ] RHw child_created=True class=B child_end=exec
  record[msolve raw_t1           ] RH  child_created=True class=B child_end=exec
  record[msolve raw_t1           ] RHw child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] gaps ['child/grid_raw_t0.npz', 'child/grid_raw_t0.spec.json', 'child/grid_raw_t0.stderr', 'child/grid_raw_t0.stdout']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] gaps ['child/grid_raw_t0.npz', 'child/grid_raw_t0.spec.json', 'child/grid_raw_t0.stderr', 'child/grid_raw_t0.stdout']
  package RHw k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] FAIL-OPEN ['(i)', '(ii-ANY)', '(ii-LR)']
  package RHw k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] FAIL-OPEN ['(i)', '(ii-ANY)', '(ii-LR)']

==============================================================================================================
AJ-1 FAIL-OPEN SEARCH UNDER GAPATTR (RH), RG for contrast

--- (1) lost launch records whose files another record's positive source names

### LR-0 SE-3 re-solve at S-1 (2 attempts), every launch record present
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mc verdict PASS    items []                 defs []                       

### LR-1 SE-3 re-solve at S-1 (2 attempts), the FINAL attempt's launch record REMOVED
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RG  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 2         ] RH  NO LAUNCH RECORD (removed)
  package RG  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']

### LR-2 SE-3 re-solve at S-1 (2 attempts), attempt 1's launch record REMOVED
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 1         ] RH  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 2         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']

### LR-3 SE-3 re-solve at S-1 (3 attempts), attempt 2's launch record REMOVED
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RG  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 2         ] RH  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 3         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 3         ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RG  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RH  k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']

### LR-4 SE-3 re-solve at S-1 (3 attempts), attempts 2 and 3 REMOVED
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RG  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 2         ] RH  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 3         ] RG  NO LAUNCH RECORD (removed)
  record[S5_t1 attempt 3         ] RH  NO LAUNCH RECORD (removed)
  package RG  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RG  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S5_t1.ms.err.ssf-attempt2', 'solver/S5_t1.ms.log.ssf-attempt2', 'solver/S5_t1.ms.out.ssf-attempt2']

### LR-5 HR-3 re-solve at S-2 in controls_a1 (2 attempts), the final attempt's record REMOVED
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[gp                      ] RG  child_created=True class=B child_end=exec
  record[gp                      ] RH  child_created=True class=B child_end=exec
  record[health d444             ] RG  child_created=True class=B child_end=exec
  record[health d444             ] RH  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 ] RG  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 ] RH  child_created=True class=B child_end=exec
  record[health_p1073741831_d222 ] RG  NO LAUNCH RECORD (removed)
  record[health_p1073741831_d222 ] RH  NO LAUNCH RECORD (removed)
  package RG  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
  package RG  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']
  package RH  k=0 Mc verdict PASS    items []                 defs ['(i)', '(ii-LR)']       FAIL-OPEN ['(i)', '(ii-LR)']

### LR-6 callgrind tag: the msolve record REMOVED, the callgrind record names <tag>.ms
  record[grid_raw_t0 child       ] RH  child_created=True class=B child_end=exec
  record[msolve S4_t0 (callgrind ] RH  NO LAUNCH RECORD (removed)
  record[callgrind S4_t0         ] RH  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['solver/S4_t0.ms.err', 'solver/S4_t0.ms.log', 'solver/S4_t0.ms.out']

### LR-7 anchor-identity: the comparator record REMOVED
  record[comparator              ] RH  NO LAUNCH RECORD (removed)
  record[anchor_S4               ] RH  child_created=True class=B child_end=exec
  record[anchor_comparator_random] RH  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] gaps ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-ANY)', '(ii-LR)'] gaps ['comparator/anchor17_planted.ms', 'comparator/anchor17_random.ms', 'comparator/anchor25_planted.ms', 'comparator/anchor25_random.ms', 'comparator/k4a_results.json', 'comparator/stderr.log', 'comparator/stdout.log']

### LR-8 a build child-job record REMOVED (the RH-6 (i) (22) shape)
  record[ctl_S3                  ] RH  NO LAUNCH RECORD (removed)
  record[ctl_raw_random          ] RH  child_created=True class=B child_end=exec
  record[ctl_planted_S3          ] RH  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3.spec.json', 'child/ctl_S3.stderr', 'child/ctl_S3.stdout']
  package RH  k=0 Mc verdict FAIL    items []                 defs ['(i)', '(ii-LR)']       gaps ['child/ctl_S3.meta.json', 'child/ctl_S3.npz', 'child/ctl_S3.spec.json', 'child/ctl_S3.stderr', 'child/ctl_S3.stdout']

--- (2)-(3) FO-1 and RH-4 under gapattr

### FO-1 variant C, foreign write ok
  record[FO-1 C ok               ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: recorder-foreign file, child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### FO-1 variant C, foreign write failed
  record[FO-1 C failed           ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### FO-1 variant C, foreign write interrupted
  record[FO-1 C interrupted      ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)']  

### FO-1 variant B, foreign write ok
  record[FO-1 B ok               ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: recorder-foreign file, child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### FO-1 variant B, foreign write failed
  record[FO-1 B failed           ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### FO-1 variant B, foreign write interrupted
  record[FO-1 B interrupted      ] RH  child_created=True class=None child_end=undetermined | (iv)-relevant foreign-process record; detected by: child_end undetermined
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### H4-a a signal-raised exception caught by the callback's own try (RH-4 marks)
  record[msolve                  ] RG  child_created=True class=B child_end=exec
  record[msolve                  ] RH  child_created=True class=None child_end=undetermined
  package RG  k=1 Mr verdict PASS    items []                 defs []                       
  package RG  k=1 Mc verdict PASS    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### H4-b an exception of the callback's own code, caught (RH-4 marks)
  record[msolve                  ] RG  child_created=True class=B child_end=exec
  record[msolve                  ] RH  child_created=True class=None child_end=undetermined
  package RG  k=1 Mr verdict PASS    items []                 defs []                       
  package RG  k=1 Mc verdict PASS    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### H4-c a pending signal surfacing at the callback's entry, before its try: escapes, body not run
  record[msolve                  ] RG  child_created=True class=None child_end=undetermined
  record[msolve                  ] RH  child_created=True class=None child_end=undetermined
  package RG  k=1 Mr verdict FAIL    items []                 defs []                       
  package RG  k=1 Mc verdict FAIL    items []                 defs []                       
  package RH  k=1 Mr verdict FAIL    items []                 defs []                       
  package RH  k=1 Mc verdict FAIL    items []                 defs []                       

### H4-d an exception escaping another after_in_parent callback, or the callback's epilogue after its body
  record[msolve                  ] RG  child_created=True class=B child_end=exec
  record[msolve                  ] RH  child_created=True class=B child_end=exec
  package RG  k=1 Mr verdict PASS    items []                 defs []                       
  package RG  k=1 Mc verdict PASS    items []                 defs []                       
  package RH  k=1 Mr verdict PASS    items []                 defs []                       
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

--- (4) RG-1 residuals, HYPOTHETICAL supplying code (none found in the repository scan or the third-party text read)

### X1 escaped child exits 99 by an unwinding-path SystemExit, variant C (empty report)
  record[X1                      ] RH  child_created=True class=C child_end=frozen_pre_exec_exit | (iv)-relevant foreign-process record; detected by: NOTHING
  package RH  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RH  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']

### X10 escaped child itself execs, variant B
  record[X10                     ] RH  child_created=True class=B child_end=exec | (iv)-relevant foreign-process record; detected by: NOTHING
  package RH  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RH  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']

### X6b counter on a second live child that execs while the real child escaped (variant B)
  record[X6b                     ] RH  child_created=True class=B child_end=exec | (iv)-relevant foreign-process record; detected by: NOTHING
  package RH  k=1 Mr verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']
  package RH  k=1 Mc verdict PASS    items []                 defs ['(iv)']                 FAIL-OPEN ['(iv)']

--- census paths under gapattr (RH), each in a cells m = 5 package with one other class (B) launch

### census P-1..P-4 refused before fork (153-169)
  record[path                    ] RH  child_created=False class=A child_end=no_child
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

### census P-6 ERR setrlimit 97
  record[path                    ] RH  child_created=True class=C child_end=frozen_pre_exec_exit
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

### census P-7 empty report 99
  record[path                    ] RH  child_created=True class=C child_end=frozen_pre_exec_exit
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

### census P-8 soft != cap (98; return 232)
  record[path                    ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RH  k=1 Mc verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### census P-9 hard-only mismatch (98)
  record[path                    ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RH  k=1 Mc verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### census P-10..P-13 exec; ok / crashed / memory / timeout
  record[path                    ] RH  child_created=True class=B child_end=exec
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

### census exec raised after OK (99)
  record[path                    ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RH  k=1 Mc verdict PASS    items []                 defs []                       

### census P-5a raise before fork
  record[path                    ] RH  child_created=False class=None child_end=no_child
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(v)']                  

### census P-16 raise at 181
  record[path                    ] RH  child_created=undetermined class=None child_end=undetermined
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(ii-ANY)', '(ii-LR)', '(v)'] 

### census P-14c raise after 227
  record[path                    ] RH  child_created=True class=None child_end=undetermined
  package RH  k=1 Mc verdict FAIL    items []                 defs ['(v)']                  

==============================================================================================================
AJ-2 NORMAL OUTCOMES OF EVERY LAUNCH KIND UNDER GAPATTR (RH): files written and their attribution

### N-1 cells m = 5 measured (S5 t0 retained, t1 not retained)
  solver/S5_t0.ms                                      writer driver v2_driver 162 / a1_health 143         -> (ii) S5_t0
  solver/S5_t0.ms.err                                  writer S5_t0                                        -> (i) S5_t0
  solver/S5_t0.ms.log                                  writer S5_t0                                        -> (i) S5_t0
  solver/S5_t0.ms.out                                  writer S5_t0                                        -> (ii) S5_t0
  solver/S5_t1.ms.err                                  writer S5_t1                                        -> (i) S5_t1
  solver/S5_t1.ms.log                                  writer S5_t1                                        -> (i) S5_t1
  solver/S5_t1.ms.out                                  writer S5_t1                                        -> (ii) S5_t1

### N-1 cells m = 5 measured (S5 t0 retained, t1 not retained) [verdict]
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1                   ] RG  child_created=True class=B child_end=exec
  record[S5_t1                   ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out)
  solver/S5_t0.ms                                      writer driver v2_driver 162 / a1_health 143         -> (ii) S5_t0 timeout
  solver/S5_t0.ms.err                                  writer S5_t0 timeout                                -> (i) S5_t0 timeout
  solver/S5_t0.ms.log                                  writer S5_t0 timeout                                -> (i) S5_t0 timeout
  solver/S5_t1.ms                                      writer driver v2_driver 162 / a1_health 143         -> (ii) S5_t1 memory
  solver/S5_t1.ms.err                                  writer S5_t1 memory                                 -> (i) S5_t1 memory
  solver/S5_t1.ms.log                                  writer S5_t1 memory                                 -> (i) S5_t1 memory

### N-2 cells m = 5 not_measured (timeout / memory_exhausted after exec; no .ms.out) [verdict]
  record[S5_t0 timeout           ] RG  child_created=True class=B child_end=exec
  record[S5_t0 timeout           ] RH  child_created=True class=B child_end=exec
  record[S5_t1 memory            ] RG  child_created=True class=B child_end=exec
  record[S5_t1 memory            ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549)
  child/grid_raw_t0.meta.json                          writer grid_raw_t0 v2_child 104; .npz removed v2_dr -> (v) grid_raw_t0
  child/grid_raw_t0.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t0
  child/grid_raw_t0.stderr                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  child/grid_raw_t0.stdout                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  solver/raw_t0.callgrind.stderr                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.callgrind.stdout                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.ms                                     writer driver v2_driver 162 / a1_health 143         -> (ii) raw_t0; (ii) callgrind raw_t0
  solver/raw_t0.ms.err                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.log                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.out                                 writer raw_t0                                       -> (ii) raw_t0

### N-3 cells m = 4: raw_grid measured, callgrind ok at target 0 (.callgrind.out removed at 549) [verdict]
  record[grid_raw_t0             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[raw_t0                  ] RG  child_created=True class=B child_end=exec
  record[raw_t0                  ] RH  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RG  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal)
  child/grid_raw_t0.npz                                writer grid_raw_t0 partial, v2_child 38/100         -> (v) grid_raw_t0
  child/grid_raw_t0.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t0
  child/grid_raw_t0.stderr                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  child/grid_raw_t0.stdout                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  child/grid_raw_t1.meta.json                          writer grid_raw_t1 v2_child 104; .npz removed v2_dr -> (v) grid_raw_t1
  child/grid_raw_t1.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t1
  child/grid_raw_t1.stderr                             writer grid_raw_t1                                  -> (i) grid_raw_t1
  child/grid_raw_t1.stdout                             writer grid_raw_t1                                  -> (i) grid_raw_t1
  solver/raw_t1.ms                                     writer driver v2_driver 162 / a1_health 143         -> (ii) raw_t1
  solver/raw_t1.ms.err                                 writer raw_t1                                       -> (i) raw_t1
  solver/raw_t1.ms.log                                 writer raw_t1                                       -> (i) raw_t1
  solver/raw_t1.ms.out                                 writer raw_t1                                       -> (ii) raw_t1

### N-4 cells m = 4: raw_grid child crashed after exec (partial .npz kept: v2_driver 137-139 returns before removal) [verdict]
  record[grid_raw_t0             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[grid_raw_t1             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t1             ] RH  child_created=True class=B child_end=exec
  record[raw_t1                  ] RG  child_created=True class=B child_end=exec
  record[raw_t1                  ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.npz', 'child/grid_raw_t1.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-5 SE-3 re-solve at S-1 (2 attempts)
  solver/S5_t0.ms                                      writer driver v2_driver 162 / a1_health 143         -> (ii) S5_t0
  solver/S5_t0.ms.err                                  writer S5_t0                                        -> (i) S5_t0
  solver/S5_t0.ms.log                                  writer S5_t0                                        -> (i) S5_t0
  solver/S5_t0.ms.out                                  writer S5_t0                                        -> (ii) S5_t0
  solver/S5_t1.ms                                      writer driver v2_driver 162 / a1_health 143         -> (ii) S5_t1 attempt 1; (ii) S5_t1 attempt 2
  solver/S5_t1.ms.err                                  writer S5_t1 attempt 2                              -> (i) S5_t1 attempt 1; (i) S5_t1 attempt 2
  solver/S5_t1.ms.err.ssf-attempt1                     writer S5_t1 attempt 1 renamed, r3_resolve 234      -> (vi) k=1 S5_t1 attempt 1
  solver/S5_t1.ms.log                                  writer S5_t1 attempt 2                              -> (i) S5_t1 attempt 1; (i) S5_t1 attempt 2
  solver/S5_t1.ms.log.ssf-attempt1                     writer S5_t1 attempt 1 renamed, r3_resolve 234      -> (vi) k=1 S5_t1 attempt 1
  solver/S5_t1.ms.out                                  writer S5_t1 attempt 2                              -> (ii) S5_t1 attempt 1; (ii) S5_t1 attempt 2
  solver/S5_t1.ms.out.ssf-attempt1                     writer S5_t1 attempt 1 renamed, r3_resolve 234      -> (vi) k=1 S5_t1 attempt 1

### N-5 SE-3 re-solve at S-1 (2 attempts) [verdict]
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1         ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves
  child/ctl_a1_torsion_S3_rq.meta.json                 writer ctl_a1_torsion_S3_rq v2_child 41             -> (v) ctl_a1_torsion_S3_rq
  child/ctl_a1_torsion_S3_rq.npz                       writer ctl_a1_torsion_S3_rq v2_child 38             -> (v) ctl_a1_torsion_S3_rq
  child/ctl_a1_torsion_S3_rq.spec.json                 writer driver v2_driver 98-99                       -> (ii) ctl_a1_torsion_S3_rq
  child/ctl_a1_torsion_S3_rq.stderr                    writer ctl_a1_torsion_S3_rq                         -> (i) ctl_a1_torsion_S3_rq
  child/ctl_a1_torsion_S3_rq.stdout                    writer ctl_a1_torsion_S3_rq                         -> (i) ctl_a1_torsion_S3_rq
  health/health-1073741831.json                        writer driver a1_health 251                         -> non-launch list (a1_health 141-143 inputs / 251 report) -
  health/health_p1073741831_d222.ms                    writer driver v2_driver 162 / a1_health 143         -> (ii) health d222 attempt 1; (ii) health d222 attempt 2
  health/health_p1073741831_d222.ms.err                writer health d222 attempt 2                        -> (i) health d222 attempt 1; (i) health d222 attempt 2
  health/health_p1073741831_d222.ms.err.ssf-attempt1   writer health d222 attempt 1 renamed, r3_resolve 23 -> (vi) k=1 health d222 attempt 1
  health/health_p1073741831_d222.ms.log                writer health d222 attempt 2                        -> (i) health d222 attempt 1; (i) health d222 attempt 2
  health/health_p1073741831_d222.ms.log.ssf-attempt1   writer health d222 attempt 1 renamed, r3_resolve 23 -> (vi) k=1 health d222 attempt 1
  health/health_p1073741831_d222.ms.out                writer health d222 attempt 2                        -> (ii) health d222 attempt 1; (ii) health d222 attempt 2
  health/health_p1073741831_d222.ms.out.ssf-attempt1   writer health d222 attempt 1 renamed, r3_resolve 23 -> (vi) k=1 health d222 attempt 1
  health/health_p1073741831_d444.ms                    writer driver v2_driver 162 / a1_health 143         -> (ii) health d444
  health/health_p1073741831_d444.ms.err                writer health d444                                  -> (i) health d444
  health/health_p1073741831_d444.ms.log                writer health d444                                  -> (i) health d444
  health/health_p1073741831_d444.ms.out                writer health d444                                  -> (ii) health d444
  pari/controls_a1_pari.gp                             writer driver a1_pari 91-93                         -> (ii) gp
  pari/controls_a1_pari.gp.stderr                      writer gp                                           -> (i) gp
  pari/controls_a1_pari.gp.stdout                      writer gp                                           -> (i) gp
  solver/ctl_a1_planted_torsion_S3_rq.ms               writer driver v2_driver 162 / a1_health 143         -> (ii) ctl_a1_planted_torsion_S3_rq
  solver/ctl_a1_planted_torsion_S3_rq.ms.err           writer ctl_a1_planted_torsion_S3_rq                 -> (i) ctl_a1_planted_torsion_S3_rq
  solver/ctl_a1_planted_torsion_S3_rq.ms.log           writer ctl_a1_planted_torsion_S3_rq                 -> (i) ctl_a1_planted_torsion_S3_rq
  solver/ctl_a1_planted_torsion_S3_rq.ms.out           writer ctl_a1_planted_torsion_S3_rq                 -> (ii) ctl_a1_planted_torsion_S3_rq

### N-6 controls_a1 with an HR-3 re-solve at S-2, gp child, health d444, builds, S-1 solves [verdict]
  record[gp                      ] RG  child_created=True class=B child_end=exec
  record[gp                      ] RH  child_created=True class=B child_end=exec
  record[health d222 attempt 1   ] RG  child_created=True class=B child_end=exec
  record[health d222 attempt 1   ] RH  child_created=True class=B child_end=exec
  record[health d222 attempt 2   ] RG  child_created=True class=B child_end=exec
  record[health d222 attempt 2   ] RH  child_created=True class=B child_end=exec
  record[health d444             ] RG  child_created=True class=B child_end=exec
  record[health d444             ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_torsion_S3_rq    ] RG  child_created=True class=B child_end=exec
  record[ctl_a1_torsion_S3_rq    ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_planted_torsion_S] RG  child_created=True class=B child_end=exec
  record[ctl_a1_planted_torsion_S] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 480); gaps ['child/ctl_a1_torsion_S3_rq.meta.json', 'child/ctl_a1_torsion_S3_rq.npz', 'health/health_p1073741831_d222.ms.err.ssf-attempt1', 'health/health_p1073741831_d222.ms.log.ssf-attempt1', 'health/health_p1073741831_d222.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524)
  child/grid_raw_t0.meta.json                          writer grid_raw_t0 v2_child 104; .npz removed v2_dr -> (v) grid_raw_t0
  child/grid_raw_t0.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t0
  child/grid_raw_t0.stderr                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  child/grid_raw_t0.stdout                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  solver/raw_t0.callgrind.out                          writer callgrind raw_t0 left by v2_solver 521-524   -> (iii) callgrind raw_t0
  solver/raw_t0.callgrind.stderr                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.callgrind.stdout                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.ms                                     writer driver v2_driver 162 / a1_health 143         -> (ii) raw_t0; (ii) callgrind raw_t0
  solver/raw_t0.ms.err                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.log                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.out                                 writer raw_t0                                       -> (ii) raw_t0

### N-7 failing callgrind child (valgrind exits nonzero after writing its out file: v2_solver 521-524) [verdict]
  record[grid_raw_t0             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[raw_t0                  ] RG  child_created=True class=B child_end=exec
  record[raw_t0                  ] RH  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RG  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json', 'solver/raw_t0.callgrind.out']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211)
  child/grid_raw_t0.meta.json                          writer grid_raw_t0 v2_child 104; .npz removed v2_dr -> (v) grid_raw_t0
  child/grid_raw_t0.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t0
  child/grid_raw_t0.stderr                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  child/grid_raw_t0.stdout                             writer grid_raw_t0                                  -> (i) grid_raw_t0
  solver/raw_t0.callgrind.stderr                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.callgrind.stdout                       writer callgrind raw_t0                             -> (i) callgrind raw_t0
  solver/raw_t0.ms                                     writer driver v2_driver 162 / a1_health 143         -> (ii) raw_t0; (ii) callgrind raw_t0
  solver/raw_t0.ms.err                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.log                                 writer raw_t0                                       -> (i) raw_t0
  solver/raw_t0.ms.out                                 writer raw_t0                                       -> (ii) raw_t0

### N-8 timed-out callgrind child (SIGKILL; no out file; .cg.ms.out removed at v2_driver 211) [verdict]
  record[grid_raw_t0             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[raw_t0                  ] RG  child_created=True class=B child_end=exec
  record[raw_t0                  ] RH  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RG  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962)
  child/build_4111_ecgfp5_shaped_S4_m4.spec.json       writer driver v2_driver 98-99                       -> (ii) build_4111_S4
  child/build_4111_ecgfp5_shaped_S4_m4.stderr          writer build_4111_S4                                -> (i) build_4111_S4
  child/build_4111_ecgfp5_shaped_S4_m4.stdout          writer build_4111_S4                                -> (i) build_4111_S4
  child/build_4111_ecgfp5_shaped_S5_m5.spec.json       writer driver v2_driver 98-99                       -> (ii) build_4111_S5
  child/build_4111_ecgfp5_shaped_S5_m5.stderr          writer build_4111_S5                                -> (i) build_4111_S5
  child/build_4111_ecgfp5_shaped_S5_m5.stdout          writer build_4111_S5                                -> (i) build_4111_S5

### N-9 build package: cached builds (out under the cache dir, v2_driver 96, 961-962) [verdict]
  record[build_4111_S5           ] RG  child_created=True class=B child_end=exec
  record[build_4111_S5           ] RH  child_created=True class=B child_end=exec
  record[build_4111_S4           ] RG  child_created=True class=B child_end=exec
  record[build_4111_S4           ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-10 fixture4: uncached builds and solves
  child/f4_S4.meta.json                                writer f4_S4 v2_child 41                            -> (v) f4_S4
  child/f4_S4.npz                                      writer f4_S4 v2_child 38                            -> (v) f4_S4
  child/f4_S4.spec.json                                writer driver v2_driver 98-99                       -> (ii) f4_S4
  child/f4_S4.stderr                                   writer f4_S4                                        -> (i) f4_S4
  child/f4_S4.stdout                                   writer f4_S4                                        -> (i) f4_S4
  solver/f4_t0_S4.ms                                   writer driver v2_driver 162 / a1_health 143         -> (ii) f4_t0_S4
  solver/f4_t0_S4.ms.err                               writer f4_t0_S4                                     -> (i) f4_t0_S4
  solver/f4_t0_S4.ms.log                               writer f4_t0_S4                                     -> (i) f4_t0_S4
  solver/f4_t0_S4.ms.out                               writer f4_t0_S4                                     -> (ii) f4_t0_S4

### N-10 fixture4: uncached builds and solves [verdict]
  record[f4_S4                   ] RG  child_created=True class=B child_end=exec
  record[f4_S4                   ] RH  child_created=True class=B child_end=exec
  record[f4_t0_S4                ] RG  child_created=True class=B child_end=exec
  record[f4_t0_S4                ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 481); gaps ['child/f4_S4.meta.json', 'child/f4_S4.npz']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C)
  child/grid_raw_t0.meta.json                          writer grid_raw_t0 refused meta v2_child 68/80      -> (v) grid_raw_t0 refused meta
  child/grid_raw_t0.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t0 refused meta
  child/grid_raw_t0.stderr                             writer grid_raw_t0 refused meta                     -> (i) grid_raw_t0 refused meta
  child/grid_raw_t0.stdout                             writer grid_raw_t0 refused meta                     -> (i) grid_raw_t0 refused meta
  child/grid_raw_t1.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t1 refused before fork
  child/grid_raw_t2.spec.json                          writer driver v2_driver 98-99                       -> (ii) grid_raw_t2 ERR
  child/grid_raw_t2.stderr                             writer grid_raw_t2 ERR                              -> (i) grid_raw_t2 ERR
  child/grid_raw_t2.stdout                             writer grid_raw_t2 ERR                              -> (i) grid_raw_t2 ERR
  solver/raw_t3.ms                                     writer driver v2_driver 162 / a1_health 143         -> (ii) raw_t3
  solver/raw_t3.ms.err                                 writer raw_t3                                       -> (i) raw_t3
  solver/raw_t3.ms.log                                 writer raw_t3                                       -> (i) raw_t3
  solver/raw_t3.ms.out                                 writer raw_t3                                       -> (ii) raw_t3

### N-11 child jobs on refusal paths: refused meta (v2_child 68), refused before fork (class A), ERR setrlimit (class C) [verdict]
  record[grid_raw_t0 refused meta] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0 refused meta] RH  child_created=True class=B child_end=exec
  record[grid_raw_t1 refused befo] RG  child_created=False class=A child_end=no_child
  record[grid_raw_t1 refused befo] RH  child_created=False class=A child_end=no_child
  record[grid_raw_t2 ERR         ] RG  child_created=True class=C child_end=frozen_pre_exec_exit
  record[grid_raw_t2 ERR         ] RH  child_created=True class=C child_end=frozen_pre_exec_exit
  record[raw_t3                  ] RG  child_created=True class=B child_end=exec
  record[raw_t3                  ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-12 anchor-identity: comparator, uncached build, gb_only solves
  child/anchor_S4.meta.json                            writer anchor_S4 v2_child 41                        -> (v) anchor_S4
  child/anchor_S4.npz                                  writer anchor_S4 v2_child 38                        -> (v) anchor_S4
  child/anchor_S4.spec.json                            writer driver v2_driver 98-99                       -> (ii) anchor_S4
  child/anchor_S4.stderr                               writer anchor_S4                                    -> (i) anchor_S4
  child/anchor_S4.stdout                               writer anchor_S4                                    -> (i) anchor_S4
  comparator/anchor17_planted.ms                       writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor17_random.ms                        writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor25_planted.ms                       writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor25_random.ms                        writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/k4a_results.json                          writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/stderr.log                                writer comparator                                   -> (i) comparator; (iv) comparator
  comparator/stdout.log                                writer comparator                                   -> (i) comparator; (iv) comparator
  solver/anchor_comparator_system.ms                   writer driver v2_driver 162 / a1_health 143         -> (ii) anchor_comparator_system
  solver/anchor_comparator_system.ms.err               writer anchor_comparator_system                     -> (i) anchor_comparator_system
  solver/anchor_comparator_system.ms.log               writer anchor_comparator_system                     -> (i) anchor_comparator_system
  solver/anchor_comparator_system.ms.out               writer anchor_comparator_system                     -> (ii) anchor_comparator_system
  solver/anchor_v2_t0.ms                               writer driver v2_driver 162 / a1_health 143         -> (ii) anchor_v2_t0
  solver/anchor_v2_t0.ms.err                           writer anchor_v2_t0                                 -> (i) anchor_v2_t0
  solver/anchor_v2_t0.ms.log                           writer anchor_v2_t0                                 -> (i) anchor_v2_t0
  solver/anchor_v2_t0.ms.out                           writer anchor_v2_t0                                 -> (ii) anchor_v2_t0

### N-12 anchor-identity: comparator, uncached build, gb_only solves [verdict]
  record[comparator              ] RG  child_created=True class=B child_end=exec
  record[comparator              ] RH  child_created=True class=B child_end=exec
  record[anchor_S4               ] RG  child_created=True class=B child_end=exec
  record[anchor_S4               ] RH  child_created=True class=B child_end=exec
  record[anchor_v2_t0            ] RG  child_created=True class=B child_end=exec
  record[anchor_v2_t0            ] RH  child_created=True class=B child_end=exec
  record[anchor_comparator_system] RG  child_created=True class=B child_end=exec
  record[anchor_comparator_system] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478); gaps ['child/anchor_S4.meta.json', 'child/anchor_S4.npz']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### N-13 Z-C5 (no launch; directories only)

### N-13 Z-C5 (no launch; directories only) [verdict]
  package RG  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       

--- AJ-2 (1) LISTING CHECK under gapattr RH-1 AS WORDED (launch sets RECONSTRUCTED, CRG-9)

--- listing check under RH1 (gapattr)
  RUN-GFPN-f6a21a: 284 files in the five directories, 88 reconstructed launch records ({'callgrind': 36, 'childjob': 16, 'comparator': 0, 'gp': 0, 'msolve': 36}); files by first clause {'(i)': 176, '(ii)': 88, '(v)': 20}
    unattributed: 0 (child/*.meta.json 0; child/*.npz 0; other 0)
  RUN-GFPN-902222: 284 files in the five directories, 88 reconstructed launch records ({'callgrind': 36, 'childjob': 16, 'comparator': 0, 'gp': 0, 'msolve': 36}); files by first clause {'(i)': 176, '(ii)': 88, '(v)': 20}
    unattributed: 0 (child/*.meta.json 0; child/*.npz 0; other 0)
  RUN-GFPN-f5412a: 32 files in the five directories, 7 reconstructed launch records ({'callgrind': 0, 'childjob': 1, 'comparator': 1, 'gp': 0, 'msolve': 5}); files by first clause {'(i)': 14, '(ii)': 11, '(iv)': 5, '(v)': 2}
    unattributed: 0 (child/*.meta.json 0; child/*.npz 0; other 0)
  RUN-GFPN-bfe956: 83 files in the five directories, 19 reconstructed launch records ({'callgrind': 0, 'childjob': 11, 'comparator': 0, 'gp': 0, 'msolve': 8}); files by first clause {'(i)': 38, '(ii)': 27, '(v)': 18}
    unattributed: 0 (child/*.meta.json 0; child/*.npz 0; other 0)

==============================================================================================================
AJ-3 CAP-MISMATCH OUTCOMES (RH-2) AND THE RKR-4 (b) PASS / PASS_ZL ROWS: RF vs RG vs RH

### CM cells_m5: every launch P-8
  record[P-8 a                   ] RF  child_created=True class=B
  record[P-8 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RF  child_created=True class=B
  record[P-8 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM cells_m5: every launch P-9
  record[P-9 a                   ] RF  child_created=True class=B
  record[P-9 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RF  child_created=True class=B
  record[P-9 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM cells_m5: mixture, one P-9 launch and one measured launch (pair = cap, exec)
  record[P-9                     ] RF  child_created=True class=B
  record[P-9                     ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9                     ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[measured                ] RF  child_created=True class=B
  record[measured                ] RG  child_created=True class=B child_end=exec
  record[measured                ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM cells_m4: every launch P-8
  record[P-8 a                   ] RF  child_created=True class=B
  record[P-8 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RF  child_created=True class=B
  record[P-8 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM cells_m4: every launch P-9
  record[P-9 a                   ] RF  child_created=True class=B
  record[P-9 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RF  child_created=True class=B
  record[P-9 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM cells_m4: mixture, one P-9 launch and one measured launch (pair = cap, exec)
  record[P-9                     ] RF  child_created=True class=B
  record[P-9                     ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9                     ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[measured                ] RF  child_created=True class=B
  record[measured                ] RG  child_created=True class=B child_end=exec
  record[measured                ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM build: every launch P-8
  record[P-8 a                   ] RF  child_created=True class=B
  record[P-8 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RF  child_created=True class=B
  record[P-8 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-8 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM build: every launch P-9
  record[P-9 a                   ] RF  child_created=True class=B
  record[P-9 a                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 a                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RF  child_created=True class=B
  record[P-9 b                   ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 b                   ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM build: mixture, one P-9 launch and one measured launch (pair = cap, exec)
  record[P-9                     ] RF  child_created=True class=B
  record[P-9                     ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9                     ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[measured                ] RF  child_created=True class=B
  record[measured                ] RG  child_created=True class=B child_end=exec
  record[measured                ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis X-07 _load_build (v2_driver 989-1003, 1068-1075))
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### CM controls (gate): one P-9 build child
  record[P-9 build               ] RF  child_created=True class=B
  record[P-9 build               ] RG  child_created=True class=B child_end=frozen_pre_exec_exit
  record[P-9 build               ] RH  child_created=True class=B child_end=frozen_pre_exec_exit
  record[ok                      ] RF  child_created=True class=B
  record[ok                      ] RG  child_created=True class=B child_end=exec
  record[ok                      ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478)
  package RG  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478)
  package RH  k=0 Mr verdict FAIL    items ['68-70']          defs ['(ii-ANY)', '(ii-LR)']  cap-mismatch stop (RH-2)

### RKR-4 (b) row 478 G1..G4 completed_valid (fixture shape: uncached builds, raw grids, solves, callgrind)
  record[fixture_S3              ] RF  child_created=True class=B
  record[fixture_S3              ] RG  child_created=True class=B child_end=exec
  record[fixture_S3              ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x           ] RF  child_created=True class=B
  record[fx_reg0_raw_x           ] RG  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x           ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x           ] RF  child_created=True class=B
  record[fx_reg0_raw_x           ] RG  child_created=True class=B child_end=exec
  record[fx_reg0_raw_x           ] RH  child_created=True class=B child_end=exec
  record[cg fx_reg0_raw_x        ] RF  child_created=True class=B
  record[cg fx_reg0_raw_x        ] RG  child_created=True class=B child_end=exec
  record[cg fx_reg0_raw_x        ] RH  child_created=True class=B child_end=exec
  record[fx_reg0_S3              ] RF  child_created=True class=B
  record[fx_reg0_S3              ] RG  child_created=True class=B child_end=exec
  record[fx_reg0_S3              ] RH  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3           ] RF  child_created=True class=B
  record[cg fx_reg0_S3           ] RG  child_created=True class=B child_end=exec
  record[cg fx_reg0_S3           ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478); gaps ['child/fixture_S3.meta.json', 'child/fixture_S3.npz', 'child/fx_reg0_raw_x.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 480 controls_a1 image
  record[gp                      ] RF  child_created=True class=B
  record[gp                      ] RG  child_created=True class=B child_end=exec
  record[gp                      ] RH  child_created=True class=B child_end=exec
  record[health                  ] RF  child_created=True class=B
  record[health                  ] RG  child_created=True class=B child_end=exec
  record[health                  ] RH  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled      ] RF  child_created=True class=B
  record[ctl_a1_S3_rescaled      ] RG  child_created=True class=B child_end=exec
  record[ctl_a1_S3_rescaled      ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 480); gaps ['child/ctl_a1_S3_rescaled.meta.json', 'child/ctl_a1_S3_rescaled.npz']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 481 fixture4 launched
  record[f4_S4                   ] RF  child_created=True class=B
  record[f4_S4                   ] RG  child_created=True class=B child_end=exec
  record[f4_S4                   ] RH  child_created=True class=B child_end=exec
  record[f4_t0_S4                ] RF  child_created=True class=B
  record[f4_t0_S4                ] RG  child_created=True class=B child_end=exec
  record[f4_t0_S4                ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 481); gaps ['child/f4_S4.meta.json', 'child/f4_S4.npz']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 482 Z-F4 (zero call)
  package RF  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       
  package RG  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       

### RKR-4 (b) row 483 build (cached)
  record[build S5                ] RF  child_created=True class=B
  record[build S5                ] RG  child_created=True class=B child_end=exec
  record[build S5                ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 485 cells m = 5 measured
  record[S5_t0                   ] RF  child_created=True class=B
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 485 cells m = 5 measured, one SE-3 re-solve
  record[S5_t0                   ] RF  child_created=True class=B
  record[S5_t0                   ] RG  child_created=True class=B child_end=exec
  record[S5_t0                   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1 (SSF)   ] RF  child_created=True class=B
  record[S5_t1 attempt 1 (SSF)   ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 1 (SSF)   ] RH  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RF  child_created=True class=B
  record[S5_t1 attempt 2         ] RG  child_created=True class=B child_end=exec
  record[S5_t1 attempt 2         ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-08 m = 4 _condition_met (v2_driver 1110-1127); X-09/X-10 aggregates (1259-1267; a1_driver 301-310)); gaps ['solver/S5_t1.ms.err.ssf-attempt1', 'solver/S5_t1.ms.log.ssf-attempt1', 'solver/S5_t1.ms.out.ssf-attempt1']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 486 Z-C5
  package RF  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       
  package RG  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       
  package RH  k=0 Mr verdict PASS_ZL items ['66-67']          defs []                       

### RKR-4 (b) row 488 cells m = 4
  record[grid_raw_t0 child       ] RF  child_created=True class=B
  record[grid_raw_t0 child       ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0 child       ] RH  child_created=True class=B child_end=exec
  record[msolve raw_t0           ] RF  child_created=True class=B
  record[msolve raw_t0           ] RG  child_created=True class=B child_end=exec
  record[msolve raw_t0           ] RH  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RF  child_created=True class=B
  record[callgrind raw_t0        ] RG  child_created=True class=B child_end=exec
  record[callgrind raw_t0        ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 488 cells m = 4, callgrind child failed
  record[grid_raw_t0             ] RF  child_created=True class=B
  record[grid_raw_t0             ] RG  child_created=True class=B child_end=exec
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[raw_t0                  ] RF  child_created=True class=B
  record[raw_t0                  ] RG  child_created=True class=B child_end=exec
  record[raw_t0                  ] RH  child_created=True class=B child_end=exec
  record[cg raw_t0               ] RF  child_created=True class=B
  record[cg raw_t0               ] RG  child_created=True class=B child_end=exec
  record[cg raw_t0               ] RH  child_created=True class=B child_end=exec
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json', 'solver/raw_t0.callgrind.out']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### RKR-4 (b) row 489 aggregate v2
  package RF  k=0 Mr verdict PASS    items []                 defs []                       
  package RG  k=0 Mr verdict PASS    items []                 defs []                       
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

==============================================================================================================
ADDED OBJECTS (final version)

--- RH-6 (i) (19) third case as worded: 'one launch record of the tag removed yields a recorder gap and FAIL'
  2 attempts, record of attempt 1 removed: RH-1 gaps []; RH verdict PASS (Mr)
  2 attempts, record of attempt 2 removed: RH-1 gaps []; RH verdict PASS (Mr)
  3 attempts, record of attempt 1 removed: RH-1 gaps []; RH verdict PASS (Mr)
  3 attempts, record of attempt 2 removed: RH-1 gaps []; RH verdict PASS (Mr)
  3 attempts, record of attempt 3 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 1 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 2 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 3 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 4 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 5 removed: RH-1 gaps []; RH verdict PASS (Mr)
  6 attempts, record of attempt 6 removed: RH-1 gaps []; RH verdict PASS (Mr)

--- RH-6 (i) (22) with a raw_grid child job (its .npz removed at v2_driver 144)
  gaps ['child/grid_raw_t0.meta.json', 'child/grid_raw_t0.spec.json', 'child/grid_raw_t0.stderr', 'child/grid_raw_t0.stdout']; the expected list '.spec.json, .stdout, .stderr, .npz and .meta.json' contains .npz: False

### IV-1 comparator/ holds a file written by a process no rule knows: RH-1 (iv) attributes it by its directory
  child/anchor_S4.meta.json                            writer anchor_S4 v2_child 41                        -> (v) anchor_S4
  child/anchor_S4.npz                                  writer anchor_S4 v2_child 38                        -> (v) anchor_S4
  child/anchor_S4.spec.json                            writer driver v2_driver 98-99                       -> (ii) anchor_S4
  child/anchor_S4.stderr                               writer anchor_S4                                    -> (i) anchor_S4
  child/anchor_S4.stdout                               writer anchor_S4                                    -> (i) anchor_S4
  comparator/anchor17_planted.ms                       writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor17_random.ms                        writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor25_planted.ms                       writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/anchor25_random.ms                        writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/k4a_results.json                          writer comparator k4a 279-281, 318                  -> (iv) comparator
  comparator/stderr.log                                writer comparator                                   -> (i) comparator; (iv) comparator
  comparator/stdout.log                                writer comparator                                   -> (i) comparator; (iv) comparator
  comparator/unknown-writer.dat                        writer process-not-known-to-the-rules e.g. a grandc -> (iv) comparator

### IV-1 comparator/ holds a file written by a process no rule knows: RH-1 (iv) attributes it by its directory [verdict]
  record[comparator              ] RG  child_created=True class=B child_end=exec
  record[comparator              ] RH  child_created=True class=B child_end=exec
  record[anchor_S4               ] RG  child_created=True class=B child_end=exec
  record[anchor_S4               ] RH  child_created=True class=B child_end=exec
  package RG  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis RKR-4 (b) row 478); gaps ['child/anchor_S4.meta.json', 'child/anchor_S4.npz']
  package RH  k=0 Mr verdict PASS    items []                 defs []                       

### REL-1 the same package read at another absolute root (recorded paths from run time)
  record[grid_raw_t0             ] RH  child_created=True class=B child_end=exec
  record[raw_t0                  ] RH  child_created=True class=B child_end=exec
  package RH  k=0 Mr verdict FAIL    items []                 defs []                       PLANNED-BASIS REFUSAL (basis X-09/X-10 aggregates (v2_driver 1259-1267; a1_driver 301-310)); gaps ['child/grid_raw_t0.meta.json', 'child/grid_raw_t0.spec.json', 'child/grid_raw_t0.stderr', 'child/grid_raw_t0.stdout', 'solver/raw_t0.ms', 'solver/raw_t0.ms.err', 'solver/raw_t0.ms.log', 'solver/raw_t0.ms.out']

WROTE rt_eval.json with 90 keys
````

