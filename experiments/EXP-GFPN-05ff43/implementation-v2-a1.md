# EXP-GFPN-05ff43 — implementation note, protocol v2-a1 (stage 1b)

Executor card **TASK-20260923-4c64b5**, stage 1b: implement, do not run. Zero run packages
(`maximum_runs: 0`).

Protocol v2-a1 has four parts, read together:
- protocol v2: the frozen specification plus AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii, with
  DEC-20260923-e788a1 AC-1 to AC-6;
- the additive addendum **AMD-EXP-GFPN-05ff43-20260923-rung31**;
- its approval, **DEC-20260923-8b2dbf**, with conditions AA-1 to AA-8.

The addendum's in-file `status: draft` is expected (DEC-20260923-8b2dbf `in_file_status_note`).

- **Binding check (step 0).** Both amendment hashes were computed before any file was written. Both
  matched the bound values:
  - `amendments/v1_to_v2_reanchor_and_arm_iii.yaml`:
    `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3`;
  - `amendments/v2_addendum_rung31.yaml`:
    `2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c`.
- **Preconditions checked by the executor.**
  - The 14 paths bound by the TASK-20260923-0fa03f phase-A receipt hash to the receipt's values.
  - None of the 31 ids reserved in `trial-plan-v2.json` has a directory under `runs/` (DP-7).
    Only the top level of `runs/` was listed. Nothing inside any run directory was read (S1B-8).
  - Source revision: HEAD `230991159906b317a9eb9e1ad4216dbe88383e53`, branch
    `claude/pollard-rho-speedup-hypotheses-yu8qwp`. The worktree was clean at start.
- **Edits to frozen material.** None. These are byte-identical before and after stage 1b (sha256
  checked against a baseline taken at 19:06Z, before any write):
  - `implementation-v2/`, `implementation-v2.md`, `trial-plan-v2.json`;
  - `implementation/` (including `ladder.json`), `implementation.md`, `trial-plan.json`;
  - the specification and both amendments.

  No byte was written under `implementation-v2/`: every interpreter ran with `-B` and
  `PYTHONDONTWRITEBYTECODE=1`, and each addendum module sets `sys.dont_write_bytecode` before
  importing a v2 module. The pre-existing, git-ignored `implementation/__pycache__/` is v1's. It is
  untouched and in the baseline.
- **End state.**
  - No run package exists, and nothing was created under `runs/`.
  - Nothing outside the three write-scope paths was written.
  - Nothing was committed, staged or pushed. Phase A of TASK-20260923-4ff597 commits this tree.
- **Plan branch: 31-bit** (11 packages). FB-1 did not fire (section 9, AA-3).

This note reports observations only. No number in it is a result. It contains no security
statement and no conclusion about H-GFPN-9a29be or HEUR-GFPN-DFLAT.

## 1. Files (the exact list phase A binds)

`experiments/EXP-GFPN-05ff43/implementation-v2-a1/` has 10 files. There is no `ladder-a1.json`,
because FB-1 did not fire.

| file | role |
|---|---|
| `a1_common.py` | Paths, ids, hashes and constants. `redirect_v2()` sets v2 module-level constants in-process only. It also provides the inference block and the receipt reader. |
| `a1_health.py` | msolve characteristic check on synthetic systems of known degree: A1-7 (b), AA-3, controls_a1 (d). `fb1_trigger()` is the AA-3 (b) criterion. |
| `a1_pari.py` | PARI/gp in a capped child: `ellcard`, `N mod 4`, rational 2-torsion, `isprime(N/h)`, and the norm class of b, cross-checked in pure Python. `fb1_curve_search()` (A1-9) is used only if FB-1 fires. |
| `a1_reading.py` | Reading rules as pure functions: the A1-3 sets and triple accounting, the A1-4 label, and the AA-4 matched-triple figure. |
| `a1_driver.py` | Addendum driver: `controls-a1` (its own entry point), `build` and `cells` (v2 `cmd_build` / `cmd_cells` on the addendum plan), and `aggregate-a1` (A1-5 (i)-(v)). |
| `a1_run_wrapper.py` | Addendum wrapper: refusals A-1 to A-12 (section 5), then the A1-7 (3) manifest. |
| `a1_check_run.py` | Addendum completion-gate checker: v2_check_run's checks unchanged, plus the addendum checks (A1-7 (4)). |
| `a1_make_trial_plan.py` | Writes `trial-plan-v2-a1.json` from the minted ids. |
| `a1_devchecks.py` | Stage-1b development checks (a), (c), (d), (e), (f). Output goes to scratch only. |
| `a1_toy.py` | Development check (a): the toy-ladder integration. |

The other two deliverables are `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json` and this note.

sha256 of the delivered code at the final development-check run:

- `a1_check_run.py` 516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f
- `a1_common.py` f347eebafa51eace211012f780c8425a2f4d6917f61370c7c2f20a1c62a9185b
- `a1_devchecks.py` d008405054f1afb1ff7b885e03bbcac3aec0878e0877bc46d4229e426a72edd6
- `a1_driver.py` 0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde
- `a1_health.py` 749237a6cfc15eeb235824dcf5e28e6733ee099df56daad3f996ae028650e5b7
- `a1_make_trial_plan.py` dc1c14110a015a278d71f06fb4593e13a7ca06c79746cb5ff30c5bf702933104
- `a1_pari.py` dafe748d9a1e923c106a5fa0cfcdd7d622fbb80cb23e1099d5fc6064be4e7293
- `a1_reading.py` b968838ef59035d15d9d71e74ac9e4dae8f903e0780737f04fb3497bc5a71ada
- `a1_run_wrapper.py` 03bd5c59ebbe27b6b6831ac1da9552b9a7d075fd68c472ae153eaa60a02ac81c
- `a1_toy.py` 58afe374d4ecd84b2f5e731a5f71ebbea7fb940728805354d128db7336b516d7
- `trial-plan-v2-a1.json` 2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6

## 2. Additive reuse of v2 (A1-7 (1); DEC-20260923-8b2dbf AA-5)

The addendum imports v2 modules read-only. It changes only module-level constants, and only inside
its own processes. No v2 function is replaced. No v2 file had to be edited, so there was no STOP
(S1B-1).

- **AA-5 (a): task id.** `v2_common.py` line 46 hard-codes the v2 stage-1 task id.
  - `redirect_v2()` sets `v2_common.TASK_ID = TASK-20260923-6c7f55` in-process.
  - The addendum wrapper writes `task_id: TASK-20260923-6c7f55` into every addendum manifest. It
    never reads `v2_common.TASK_ID`.
  - `a1_check_run.py` fails any package in which any file carries the old id.
  - The plan writer asserts that the plan text does not contain it.
  - The string occurs in the addendum tree only as the guard constant `FORBIDDEN_TASK_ID`
    (`a1_common.py` line 57) and in that module's docstring (line 10). It is never used as a task id.
  - These development notes record TASK-20260923-4c64b5.
- **AA-5 (b): wrapper.** `a1_run_wrapper.py` is a separate wrapper. It reserves ids from
  `trial-plan-v2-a1.json` and refuses v1 and v2 ids.
- **AA-5 (c): v2 entry points.**
  - `build` and `cells` call `v2_driver.cmd_build` / `cmd_cells` unchanged after
    `v2_common.PLAN_PATH` is redirected to `trial-plan-v2-a1.json`. Those functions then read the
    addendum package, its `builds` and `cells` lists and its watchdogs.
  - The driver first refuses if `--p/--shape/--m` differ from the plan package.
  - `cmd_controls`, which hard-codes the three v2 primes, is never called. controls_a1 is
    `a1_driver.cmd_controls_a1`.
- **AA-5 (d).** No v2 byte was written (see step 0).
- **AA-5 (e): shared ceiling.** Enforced as wrapper check A-10 (section 5).

## 3. The plan: `trial-plan-v2-a1.json` (A1-2; S1B-4)

- **Branch.** `plan_branch: "31-bit"`, with its evidence recorded (section 9, AA-3).
- **Recorded metadata.** The plan records:
  - `protocol_version: "2-a1"`;
  - the addendum id and sha256, and the approval DEC-20260923-8b2dbf;
  - the v2 amendment id and sha256;
  - `task_id: TASK-20260923-6c7f55` (the task that runs it) and `written_by_task:
    TASK-20260923-4c64b5`;
  - `v1_ids_never_reused` (49 ids, copied from trial-plan-v2.json) and `v2_ids_never_reused` (the 31
    v2 ids).
- **Count.** 11 packages: 9 planned plus 2 contingency. With v2's 31 that makes 42, within the shared
  ceiling of 48.
- **Ids.** Each id was minted with `python3 tools/allocate_id.py --next run --area GFPN` and confirmed
  with `--check <id>`. Each check returned 0 occurrences across 26314 identifier-bearing paths (see
  deviation X-1). None is a v1 or v2 id; the plan writer asserts both.

| order | run id | package | driver args | requires |
|---|---|---|---|---|
| 1 | RUN-GFPN-0d91bf | controls_a1 (blocking; checks (a)-(f)) | `controls-a1 --p 1073741831` | — |
| 2 | RUN-GFPN-8c772a | build p' = 1073741831 (m = 5 and m = 4; all shapes; refusal rows) | `build --p 1073741831` | 0d91bf |
| 3 | RUN-GFPN-569fd7 | cells, ecgfp5_shaped, m = 5 | `cells --p 1073741831 --shape ecgfp5_shaped --m 5` | 8c772a |
| 4 | RUN-GFPN-086463 | cells, random_2torsion, m = 5 | `cells … --shape random_2torsion --m 5` | 569fd7 |
| 5 | RUN-GFPN-bab146 | cells, random_no2torsion, m = 5 | `cells … --shape random_no2torsion --m 5` | 086463 |
| 6 | RUN-GFPN-7dd55d | cells, ecgfp5_shaped, m = 4 | `cells … --m 4 --prior-run RUN-GFPN-569fd7` | bab146 |
| 7 | RUN-GFPN-47aa51 | cells, random_2torsion, m = 4 | `cells … --m 4 --prior-run RUN-GFPN-086463` | 7dd55d |
| 8 | RUN-GFPN-3a70f1 | cells, random_no2torsion, m = 4 | `cells … --m 4 --prior-run RUN-GFPN-bab146` | 47aa51 |
| 9 | RUN-GFPN-ae4918 | aggregate_a1 | `aggregate-a1 --a1-runs <3-8> --v2-runs <the 18 v2 cell ids> --v2-aggregate RUN-GFPN-8f86cc` | 3a70f1 |
| 10 | RUN-GFPN-8cfac3 | contingency a1-1 | — | — |
| 11 | RUN-GFPN-6a7f35 | contingency a1-2 | — | — |

- **Gates.** Every package has `gate_required: true`: all four v2 gate packages must be completed_valid
  with gate_pass true. Packages 2-11 also have `controls_a1_gate_required: true`.
  `gate.addendum_blocking_package` is RUN-GFPN-0d91bf.
- **Cells.** The build list and cell lists come from `v2_make_trial_plan.builds / cells_m5 / cells_m4`,
  imported read-only. They are therefore exactly v2's cell set and dispositions (A1-1). At p' =
  1073741831 there is no KI-1 refusal. 30 cells are enumerated in `cells_enumeration`.
- **Watchdogs.** The `watchdogs` object is copied verbatim from trial-plan-v2.json's object (its lines
  95-177). The plan writer asserts equality, and the wrapper re-checks it (A-8). Canonical-JSON
  sha256: `watchdogs_canonical_sha256`. The declared values:
  - per target, with per-cell watchdog "none": every m = 3 arm (raw_x, raw_u, S3, S3_rescaled,
    torsion_S3_norm, torsion_S3_rq, identity) 1800 s;
  - raw, S4, S4_rescaled, torsion_S4_rq and torsion_S4_norm at m = 4: 7200 s per target, 86400 s per
    cell;
  - S5, S5_rescaled, torsion_S5_rq and torsion_S5_norm at m = 5: 43200 s per target, 172800 s per
    cell;
  - raw at m = 5: none (not_attempted by design, A-6);
  - builder timeouts: m3 1800 s, m4 7200 s, m5 86400 s;
  - callgrind timeouts: m3 1800 s, m4 14400 s;
  - comparator: 3600 s.

  The per-cell watchdog applies only while a cell has no measured target. `instruction_measurement`
  and `early_stop` are v2's, copied.
- **Target streams (A1-1).** `random.Random('2026092001:v2:targets:1073741831:<shape>')`. The three
  expanded strings are in `target_stream_strings`. Basepoint, build and grid streams follow v2's
  pattern at p' = 1073741831. controls_a1 streams carry `:v2a1:` (`other_streams`).
- **(beta, lam)** is fixed per (curve, p') by v2's rule (`v2_arms.rescaling`) and recorded in
  `rescaling_parameters` before any target is drawn. Stage 1b drew no target at 1073741831.
  - ecgfp5_shaped: beta = 7, lam = [0, 0, 0, 208737419, 0].
  - random_2torsion: beta = 7, lam = [218405532, 161868101, 510615659, 659400181, 689310716].
  - random_no2torsion: recorded refusal, "no rational 2-torsion".
  - These are parameters, not results.
- **Contingency.** `contingency_rule` is trial-plan-v2.json's text, verbatim. `contingency_rule_scope`
  restricts it to ADDENDUM packages. controls_a1 is never replaced.
- **Reading rules.** `reading_rules` records the A1-4 label, the A1-3 sets, and the AA-4 triple and
  label, all as declared before any value exists.
- **Reproducibility.** `a1_make_trial_plan.py` regenerates the file byte-identically from the id list
  (checked: `cmp` identical).

## 4. controls_a1 (A1-2 (a)-(f); `a1_driver.cmd_controls_a1`)

controls_a1 runs at the plan's p' only. The six checks, all required for `gate_pass: true`:

- **(a)** Independent known-scalar recheck on all three shapes, in pure Python (`v2_verify_independent`):
  - G and [n]G = O;
  - R = [k]G for the first 3 targets of the cell target stream.
- **(b)** A PARI capped child checks, for each shape:
  - `ellcard` equals the ladder.json order;
  - N/h equals the ladder subgroup prime, and PARI `isprime` proves it prime.

  For ecgfp5_shaped and random_2torsion it also checks the double-odd facts: N mod 4 = 2, cofactor 2,
  and b a non-square by the norm criterion. The norm is computed by PARI and again in pure Python, and
  the two must agree. For random_no2torsion it checks that there is no rational 2-torsion.
- **(c)** (beta, lam) is recomputed and must equal the plan for both 2-torsion shapes. The rq
  rescaling must refuse on random_no2torsion with "no rational 2-torsion".
- **(d)** `a1_health.run` at p' (section 9 (b)). Its output goes to `health/`.
- **(e)** Planted m = 3 < n = 5 instrument checks of the lifting path for torsion_S3_rq and
  S3_rescaled on the ecgfp5_shaped curve:
  - build (m3 builder timeout), a planted sum in the prime-order subgroup, a solve (m3 per-target
    watchdog), then lifting;
  - every certificate must pass `v2_verify_independent`;
  - the certificates carry the instrument-check label and `a1_protocol_version` / `a1_addendum_*`
    fields;
  - never degree evidence.
- **(f)** Single-flip and held-out checks on every polynomial built in (e).

Status follows v2's `cmd_controls` rules:
- a failed check is failed, as `infrastructure_error` if its child outcome is an infrastructure
  class and otherwise `implementation_error`;
- any certificate that fails re-verification makes the package invalid / `invalid_measurement`.

## 5. Addendum wrapper `a1_run_wrapper.py` (S1B-3; A1-7 (2))

The wrapper evaluates every check before any directory is created. It prints every failing reason
and exits 2 having written nothing. `--dry-run` evaluates the checks only.

| check | S1B-3 clause |
|---|---|
| A-1 | both amendment hashes |
| A-2 | id reserved in trial-plan-v2-a1.json; not a v1 id (v1 lists of both plans); not a v2 id (any id reserved in trial-plan-v2.json) |
| A-3 | run directory does not exist |
| A-4 | implementation-v2/, implementation-v2.md, trial-plan-v2.json: every path of the TASK-20260923-0fa03f phase-A receipt hash-matches; tracked; clean; no unbound file under implementation-v2/ |
| A-5 | implementation-v2-a1/, implementation-v2-a1.md, trial-plan-v2-a1.json: tracked; clean (`--untracked-files=all`); the TASK-20260923-4ff597 phase-A receipt exists at `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-4ff597/snapshot-receipt.json`; every bound path hash-matches; its implementation-v2-a1/ file list equals git's; the note and plan are bound |
| A-6 | the A1-2 gates: the four v2 gate packages completed_valid with gate_pass true; controls_a1 completed_valid with gate_pass true for packages 2-11 |
| A-7 | every `requires` predecessor has a manifest |
| A-8 | plan watchdogs == trial-plan-v2.json watchdogs (the whole object) |
| A-9 | no other solver-like process (v2_solver.other_solver_processes) |
| A-10 | shared ceiling: existing v2 dirs + existing addendum dirs + 1 ≤ 48; the addendum's own count ≤ package_count |
| A-11 | contingency_rule verbatim, addendum packages only. The replaced package must be planned, non-contingency and non-blocking, and must have a manifest with failure_class infrastructure_error. It may be replaced at most once. `--replaces` is refused on a non-contingency id and for a v2 package. |
| A-12 | the plan records protocol_version 2-a1, the addendum id and sha256, and TASK-20260923-6c7f55; it carries no forbidden task id |

**Manifest (A1-7 (3)).** Each manifest records:
- `task_id: TASK-20260923-6c7f55`, `protocol_version: "2-a1"`, and the addendum id, sha256 and
  conditions;
- the v2 amendment block;
- `code.phase_a_commits` for TASK-20260923-0fa03f and TASK-20260923-4ff597, each with its source. The
  source is the receipt's backfilled `commit_sha` if present, else `git log -1` of the receipt file;
- `implementation_v2_clean` and `implementation_v2_a1_clean`;
- `resources.child_rlimit_as_read_back_by_getrlimit`, collected from the children's own read-backs;
- `msolve_threads_executed`, taken from the argv actually executed;
- host RAM and swap;
- the watchdogs, and whether they equal v2's;
- the inference block (section 12).

A driver that exits without `raw-result.json` is recorded failed / `infrastructure_error`. The wrapper
never invents a status.

## 6. aggregate_a1 (A1-5; A1-3; A1-4; AA-4; `a1_driver.cmd_aggregate_a1`, `a1_reading.py`)

- **Inputs.** It reads the 18 v2 cell packages and RUN-GFPN-8f86cc, with v2 contingency replacements
  resolved against trial-plan-v2.json, and the 6 addendum cell packages.
- **v2 bytes are verified.** Every v2 `raw-result.json` read must hash-match
  `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-0fa03f/post-run-receipt.json`:
  - receipt absent, or a path not bound by it: failed / `infrastructure_error`;
  - a hash mismatch: invalid / `invalid_measurement`.
- **A1-4.** Every row carries `reading_label`: rows at (16777291, ecgfp5_shaped) read
  `off_shape_non_double_odd`, and `read_as_primary_shape` is false on them. No v2 byte is changed.
- **(i) Primary-shape reading.** For each arm, over {4111, 262151, 1073741831}:
  - the cell D per rung;
  - `score_like_for_like` (T-1/T-2/T-3, F1/F1') for the on-shape ecgfp5 groups only;
  - HEUR-GFPN-DFLAT per A1-3;
  - the B-3 band via `v2_scoring.band_for_arm`, unchanged. It is fed the A1-3 block (so it is emitted
    only when A1-3 is TRUE) and only primary-shape m = 5 rows of S.
- **(ii) Control reading.**
  - A1-3 for random_2torsion (4 arms, 4 rungs) and random_no2torsion (S5; the other arms are
    not_applicable refusals).
  - The F4 matched comparisons at 4111, 262151 and 1073741831.
  - The AA-4 matched-triple figure on {4111, 262151, 1073741831}, labelled "matched-triple figure (same
    rungs as the primary set); descriptive; not a verdict". It carries no pass/fail key, and it is
    not_applicable unless all three rungs have a D.
- **(iii) Off-shape section.** It holds exactly the off-shape rows, under the title "EcGFp5-model curve
  with b a square, not double-odd; nearby object; no verdict".
- **(iv) Reconciliation.** Every figure of RUN-GFPN-8f86cc is reproduced and labelled "as-planned (v2)".
  - These figures are marked "includes off-shape rung; not read for the primary shape": the heur_dflat
    figures that use the 16777291 ecgfp5 rung, the like-for-like groups there, the F4 entries at
    16777291, and the band arms derived from an off-shape DFLAT figure.
  - Control figures record whether v2's triple is one of the A1-3 eligible triples.
- **(v)** Every planned v2 and addendum cell without a row is recorded not_attempted with its reason.
- **A1-3 rule** (`a1_3_verdict`). Eligible triple: three rungs of S with a bit-length span ≥ 12.
  - TRUE iff at least one eligible triple has D at all three rungs and every such triple is below 0.10.
  - FALSE iff any such triple fails.
  - not_applicable iff none has D at all three rungs.
  - Each triple is scored by `v2_scoring.heur_dflat`, unchanged. The output lists the triples
    evaluated and not evaluable, and the "all-points figure, descriptive".
  - With exactly three rungs the verdict equals `heur_dflat`'s (tested, section 9 (a)).
- **Raw kind.** The package's raw `kind` is `aggregate`, with `aggregate_variant: aggregate_a1`, so
  that v2_check_run's aggregate branch applies unchanged.

## 7. Completion-gate checker `a1_check_run.py` (A1-7 (4))

1. It runs `v2_check_run.main` unchanged, with `PLAN_PATH` redirected in-process.
2. It adds these checks:
   - the manifest's protocol_version, addendum id and sha256, and task id;
   - no package file carries the forbidden id;
   - both phase-A commits are recorded, and both clean flags are true;
   - the watchdogs are recorded equal to v2's;
   - controls_a1 has all six checks and a boolean gate_pass;
   - for packages 2-11, controls_a1 passed;
   - for aggregate_a1:
     - the A1-4 label is on every off-shape row, and on no other row;
     - no off-shape group is in the primary scoring;
     - the off-shape section holds exactly the off-shape rows;
     - every v2 figure that uses the off-shape rung is marked;
     - the A1-3 accounting and the AA-4 figures recompute from the rows.

## 8. Envelope and machine protection (AC-1; AA-6; S1B-7)

- **Child cap.** Every msolve, PARI (`gp`), builder or valgrind child runs through
  `v2_solver.run_child`:
  - RLIMIT_AS = 10737418240 B is set in the child and read back with getrlimit before exec;
  - a child that cannot set the cap, or reads back a different value, refuses to start;
  - `/proc/<pid>/limits` is also read.
- **Why the cap stays 10 GiB.** DP-4 reports a dispatcher memory guard at MemAvailable < 2621440 kB
  (about 13.2 GB in use). That is above 12.0 GB, so the cap is not lowered.
- **Other limits.** Driver RSS at most 1 GiB, checked before each launch. One memory-heavy child at a
  time: a host lock plus a scan for other solver processes. msolve always runs with `-t 1`.
- **Host.** Intel Xeon @ 2.10 GHz, 4 cores; MemTotal 16481980 kB; SwapTotal 0; kernel 6.18.44-fc-v37;
  no cgroup memory limit.
- **Tools.** msolve 0.6.5-1build2; PARI/gp 2.15.4; cypari2 2.2.0; python-flint 0.9.0; Python 3.11.
- **Scans.** A host scan before each development-check batch found no solver-like process.
- **getrlimit read-back.** Every child launched by the development checks read back `{"soft":
  10737418240, "hard": 10737418240}`, and `/proc` reported `10737418240`. This covers 256 JSON output
  files of the final run; no other value occurs.

## 9. Development notes (no run package; no number reported as a result)

Task TASK-20260923-4c64b5.
- **Outputs.**
  - Final outputs:
    `/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/stage1b/` (below,
    `$S`).
  - Earlier attempts are preserved in `$S/prior_attempts/` (deviation X-2).
- **Timing.** The final run went from 19:36:13Z to 19:38:26Z on the delivered bytes. The hashes in
  section 1 were verified unchanged after the run.
- **Scope.** No ladder curve, cell system or fixture system was solved at any prime.
- **Commands.** Run from `experiments/EXP-GFPN-05ff43/implementation-v2-a1/`, with
  `PYTHONDONTWRITEBYTECODE=1`.

- **(b) msolve characteristic check at p' = 1073741831.**
  - Command: `python3 -B a1_health.py --p 1073741831 --out $S/devcheck_b_health_1073741831
    --reinvoke-on-fail`.
  - Systems: dense 3-variable systems (every monomial of total degree ≤ d_i, coefficients
    `rng.randrange(1, p)`), drawn in order (2,2,2) then (4,4,4) from
    `random.Random('2026092001:v2a1:health:1073741831')`.
  - Flags: the v2 cell flags, `msolve -v 2 -t 1 -f IN -o OUT -P 1`.
  - Outcome: PASS on both systems.
    - Each exited 0 with no signal.
    - The output parsed as a zero-dimensional parametrisation.
    - The quotient dimension and eliminating-polynomial degree equal the expected 8 and 64, and the
      eliminating polynomial is square-free.
    - Every rational solution substitutes. The parametrisation substitutes modulo the eliminating
      polynomial, which covers all D solutions over the closure.
  - No retry on ':2' and no re-invocation were needed.
  - Report: `$S/devcheck_b_health_1073741831/health-1073741831.json` (sha256 082d1ecd…c107). msolve
    inputs, outputs and logs are alongside it.
- **AA-3: the identical harness at p' = 16777291.**
  - Command: `python3 -B a1_health.py --p 16777291 --out $S/devcheck_b_health_16777291
    --reinvoke-on-fail`.
  - It used the same seed strings, taken literally (deviation X-5), and the same flags.
  - Outcome: PASS on both systems (exit 0, no signal, expected degree, all substitutions).
  - Report: `$S/devcheck_b_health_16777291/health-16777291.json` (fb4acb5e…e4f2).
  - The harness was debugged first at the non-ladder prime 10007. A negative test confirmed that a
    perturbed equation fails the parametrisation substitution (`$S/health_debug_10007/`).
- **AA-3 attribution record.** `a1_health.fb1_trigger` returned `p16777291_pass: true` and
  `fb1_triggers: false` (`$S/aa3_fb1_trigger_evaluation.json`, cabd8252…a786).
  - FB-1 requires both 1073741831 systems to FAIL with an A1-9 solver-side signal that reproduces on
    re-invocation. Neither failed.
  - The branch is therefore the 31-bit plan, and it is final for this protocol version (AA-3 (e)).
  - No FB-1 artifact exists: no `ladder-a1.json`, no FB-1 plan, no curve search.
  - The same outcome held at every earlier run of this check in this session.
- **(c) PARI ellcard recheck of the three 31-bit orders.**
  - Command: `python3 -B a1_devchecks.py c --out $S/devcheck_c`. PARI/gp 2.15.4 ran as a capped child.
  - Outcome: PASS.
    - For all three shapes, `ellcard` equals the ladder.json order, and N/cofactor equals the recorded
      subgroup prime and is proved prime by `isprime`.
    - ecgfp5_shaped (c = 372) and random_2torsion: N mod 4 = 2, cofactor 2, one rational 2-torsion
      point, and b a non-square by the norm criterion. The PARI norm equals the pure-Python norm,
      which agrees with ladder.json `b_is_square_in_Fq: false`.
    - random_no2torsion: no rational 2-torsion, cofactor 3.
  - Report: `$S/devcheck_c/devcheck_c.json` (1689370b…107f).
- **(d) Verifier arithmetic at p' = 1073741831.**
  - Command: `python3 -B a1_devchecks.py d --out $S/devcheck_d`. No solver was used.
  - Outcome: PASS, 76/76.
  - flint (`v2_field`) and pure-Python (`v2_verify_independent`) agree on add, double and scalar
    multiplication, and [N]P = O, on all three 31-bit curves. The flint `is_square(b)` equals the
    pure-Python norm criterion.
  - Rescaling: λ²β = b in pure Python.
  - Synthetic planted relations on ecgfp5_shaped and random_2torsion were checked for all four
    factor-base kinds (S3, S3_rescaled, torsion_S3_rq, torsion_S3_norm). Every certificate verifies.
  - relation_mod_T was checked on the T-quotient arms: accepted with the flag, and rejected without it.
  - Every negative case is rejected: wrong k, flipped signs, missing relation_mod_T, missing
    beta/lam/u_values, square beta at odd n, wrong lam, a torsion certificate on a curve without
    2-torsion, and relation_mod_T on a non-T arm.
  - rq refuses random_no2torsion.
  - Report: `$S/devcheck_d/devcheck_d.json` (d3e31edd…5147).
- **(e) Wrapper refusal dry-runs.**
  - Command: `python3 -B a1_devchecks.py e --out $S/devcheck_e`.
  - Outcome: PASS, 27/27. Every case was refused with its expected reason, exit 2, and nothing
    written. Checked: no new entry in `runs/` (top-level names only) and no change to any addendum
    file.
  - Cases:
    - A-2: an unreserved id; v1 ids RUN-GFPN-61bba9 and RUN-GFPN-bb78e5; v2 ids RUN-GFPN-ac4487 and
      RUN-GFPN-e26e4b.
    - A-5, uncommitted addendum tree and absent 4ff597 receipt: the real current state.
    - A-8: watchdog mismatch, using a scratch plan copy with one value changed.
    - A-10: the shared 48 ceiling, using a scratch plan and runs directory with 31 v2 + 17 addendum
      dirs.
    - A-1: altered addendum copy.
    - A-3: run directory exists.
    - A-4: altered 0fa03f receipt copy; dirty v2 tree (simulated git state).
    - A-5: 4ff597 receipt hash mismatch.
    - A-6: v2 gate not run (real) and failed; controls_a1 not run and failed.
    - A-7: predecessor without manifest.
    - A-9: other solver process (simulated scan result).
    - A-11: six contingency misuses.
    - A-12: wrong plan metadata.
  - Report: `$S/devcheck_e/devcheck_e.json` (161ae6da…fc66).
- **(f) Stream disjointness.**
  - Command: `python3 -B a1_devchecks.py f --out $S/devcheck_f`.
  - Outcome: PASS.
  - No v2 source or plan contains 1073741831. Every v2 stream is keyed by a prime from
    trial-plan-v2.json or by a literal in {4111, 262151, 16777291}.
  - v1 code contains no literal 1073741831.
  - The only v1 stream string with that prime is the v1 curve-selection stream
    `random.Random('2026092002:ladder:1073741831')`, recorded in ladder.json line 444, which selected
    the three frozen curves. v1 trial-plan.json lists the rung as `selected_unused`.
  - No v2-a1 stream string equals any v1 or v2 stream: all carry `:v2:` or `:v2a1:`, and each was
    searched for in the v1 and v2 sources.
  - v1 run packages were not read (S1B-8).
  - Report: `$S/devcheck_f/devcheck_f.json` (ac781bfc…b459).
- **(a) Toy-ladder integration.**
  - Command: `python3 -B a1_devchecks.py a --out $S/devcheck_a`. Outcome: PASS.
  - Report: `$S/devcheck_a/devcheck_a.json` (8946a9bf…83d8). The toy tree is in
    `$S/devcheck_a/toy/`.
  - **Reading-rule tests: 19/19 pass.**
    - 3-rung S: flat is TRUE; 20% is FALSE; D undefined at 31 bits is not_applicable, never FALSE; A1-3
      equals `heur_dflat` in four cases.
    - 4-rung S: 4 eligible triples, spanning 12, 18, 18 and 12 bits. The FALSE, missing-rung and
      not_applicable cases all behave as specified.
    - The AA-4 figure is emitted or not_applicable as required, and never carries a pass key.
    - The A1-4 label is applied to off-shape rows and not to on-shape rows.
    - `evaluate_all` marks the off-shape set NOT EVALUATED.
  - **Toy ladder.**
    - Field: p = 1021 over F_p[z]/(z^5 - 2). This is not a ladder prime.
    - Curves chosen by PARI in a capped child: ecgfp5-model c = 80 with N = 2q and b a non-square; a
      random 2-torsion curve with N = 2q and b a non-square; a random curve without 2-torsion, cofactor
      15.
  - **Toy plan.** It has the addendum's 11-package layout, with the m = 5 and m = 4 roles played by
    m = 3 and m = 2 (as v2 DN-8).
  - **Synthetic v2 packages.** The four gates, and the 18 cells at the real v2 primes with synthetic
    per-target D, labelled synthetic and honouring each planned disposition and refusal. RUN-GFPN-8f86cc
    was produced by `v2_driver.cmd_aggregate` itself on those rows. A synthetic phase-B receipt binds
    them.
  - **Packages 1-9 through `a1_run_wrapper.main()`.**
    - All nine ended completed_valid.
    - Every child read back 10737418240, and msolve threads executed = {1}.
    - `a1_check_run` passed on all nine: v2 checks plus addendum checks. The five controls_a1
      certificates re-verify.
  - **Toy aggregate_a1 readings of the synthetic inputs.**
    - Phase-B check verified.
    - Every primary-set arm is not_applicable: the 31-bit rung is absent in the toy, and the synthetic
      off-shape D at 16777291 did not enter.
    - random_2torsion torsion_S5_rq is FALSE (a synthetic 30% variation). random_2torsion S5 and
      random_no2torsion S5 are TRUE.
    - 10 off-shape rows sit in section (iii). No 16777291 group is in the primary scoring.
    - Three v2 ecgfp5 DFLAT figures are marked "includes off-shape rung".
    - No planned cell is without a row.
    - A contingency attempt on a completed_valid toy package was refused (A-11).
  - **Toy rows at p = 1021.** They have undefined D, because m < n makes the systems overdetermined, as
    in v2 DN-8. They belong to no A1-3 set. The A1-3 verdict logic is exercised by the synthetic tests
    above.

## 10. Deviations and implementation readings (disclosed; none changes a threshold, control, set or branch)

- **X-1: minting.** The first `--check` pass received the allocator's whole multi-line output instead of
  the bare id, so it checked nothing.
  - It was repeated on each bare id: 11 × "OK: well-formed and free across the union", 0 occurrences
    in 26314 paths.
  - Logs: `$S/minted_ids.log` (first pass, void), `$S/minted_ids_check.log` (valid pass),
    `$S/minted_ids.txt`.
- **X-2: development-check attempts, all preserved in `$S/prior_attempts/`.**
  - (e) attempt 1 scored 26/27 because of a harness fault, not a wrapper fault. The pass condition
    treated the pre-existing v1 directory RUN-GFPN-61bba9 as "written". The wrapper refused correctly.
    The harness was fixed to "not created by this case".
  - (a) attempt 1 stopped at toy-ladder selection: the search range c ≤ 60 was too small at p = 1021.
    It was widened to 400.
  - `final_run_1` and `final_run_2` passed in full. They were superseded after two small code fixes,
    and everything was re-run on the delivered bytes:
    - the wrapper's cypari2 version probe used `cypari2.__version__`, which does not exist, and now uses
      `importlib.metadata`;
    - the phase-A commit fallback (X-8) was added.
  - Unused imports were removed after a pyflakes pass. pyflakes was already installed per v2 DN-10;
    nothing was installed here.
- **X-3: toy harness (A1-7 (a)).** The toy runs addendum code on redirected paths.
  - Redirected: module constants in-process, and in a scratch shim that launches `a1_driver.py`.
  - One in-process stub: `a1_run_wrapper.git_tree_state` reports the uncommitted addendum files as
    tracked and clean, because stage 1b cannot commit. The real git refusals are exercised in (e).
  - The toy v2 plan copy and the toy addendum plan both carry toy-only m = 2 watchdog keys (and
    `raw|m3`, builder m2). These exist only in the scratch toy files. The delivered plan's watchdogs
    equal trial-plan-v2.json's exactly.
  - The toy uses synthetic receipts and ids (`RUN-TOYA1-*`), in scratch only.
- **X-4: simulated states in (e).** "Dirty v2 tree" and "another solver process" were simulated
  in-process (stubbed git status and scan result). Creating either for real would edit a v2 file or
  start a solver-named process.
- **X-5: AA-3 seed reading.** "The same harness, flags and seed strings" was read literally. The
  16777291 run uses the seed string `'2026092001:v2a1:health:1073741831'` unchanged. Coefficients are
  drawn with `randrange(1, p)` at that p. The ':2' retry re-draws the same degree pattern from
  `'<seed>:2'`.
- **X-6: development timeouts that are not per-(arm, m) watchdogs.**
  - The synthetic msolve check has 1800 s per system (the m = 3 per-target value).
  - PARI children have 7200 s (the m = 4 builder value).
  - They apply to non-arm, non-cell children in controls_a1 (b) and (d) and in the development checks.
    They do not alter the plan's watchdogs.
- **X-7: certificate bodies.** `v2_lift.make_certificate` hard-codes `protocol_version: 2` inside each
  certificate. It is not replaced (A1-7 (1)).
  - Addendum cell certificates therefore carry 2 in their body, while the manifest and raw-result carry
    "2-a1".
  - controls_a1 certificates also carry `a1_protocol_version: "2-a1"` through v2's own `extra`
    argument.
  - The verifier does not read the field.
- **X-8: phase-A commit recording.** The 4ff597 card says its receipt never carries its own commit's
  sha. The manifest therefore takes the receipt's backfilled `commit_sha` if present, else `git log -1`
  of the receipt file, and records which source was used.
  - The wrapper requires that receipt at the card's path, with path_sha256 covering every
    implementation-v2-a1/ file, this note and the plan.
- **X-9: aggregate_a1 bytes.** aggregate_a1 needs the TASK-20260923-0fa03f post-run receipt at
  `…/TASK-20260923-0fa03f/post-run-receipt.json` (the path in TASK-20260923-6c7f55's bound_protocol),
  and every v2 raw-result it reads must be bound by it. Otherwise the package ends failed or invalid
  (section 6). That is never a result.
- **X-10: FB-1 plan writer.** It is not implemented: `a1_make_trial_plan.py --branch FB-1` refuses,
  because FB-1 did not fire.
  - `a1_health.fb1_trigger` and `a1_pari.fb1_curve_search` exist for the record.
  - Changing branch after phase A needs a new Coordinator decision (AA-3 (e)).
- **X-11: dense-system definition.** "Dense" means every monomial of total degree ≤ d_i with a nonzero
  coefficient. The pass criterion adds parametrisation-level substitution to the rational-solution
  substitution.
- **X-12: first 3 targets in controls_a1 (a).** controls_a1 (a) reads the first 3 targets of the cell
  target stream, as v2 `cmd_controls` does. They are the same R that cell target indices 0-2 will use.
  (beta, lam) was fixed in the plan first.
- **X-13: v1 selection stream.** Development check (f) records the observation that the only v1 stream
  with the 31-bit prime is the v1 curve-selection stream (section 9 (f)).

## 11. What could block or limit stage 2b (for the Coordinator; not results)

- **Receipts.** The wrapper refuses until phase A of TASK-20260923-4ff597 has committed these three
  paths with its receipt at the card's path. aggregate_a1 needs the 0fa03f post-run receipt.
- **31-bit m = 5 build.** The S5, S5_rescaled and norm interpolations are the same size as at the
  other rungs: N = 20349 dense, about 3.3 GB (v2 amendment A-2). Under the 10 GiB cap a build may
  exhaust memory. It is then recorded, and its cells are not_attempted with that reason.
- **31-bit m = 5 cells.** They may end not_measured (timeout or OOM). The primary-shape verdict is then
  not_applicable, never FALSE (S2B-5).
- **G-2.** Small synthetic systems cannot certify msolve at large D (DEC-20260923-8b2dbf G-2). This is a
  review joint (AA-7 (4)).

## 12. Inference

- requested_policy: `executor-implementation`
- resolved_model_id: null (this runtime supplies no model id for artifacts; none is written anywhere)
- fallback_used: false
- bedrock_used: false

Every addendum manifest records the same block, and `a1_check_run.py` / `v2_check_run.py` require it.
