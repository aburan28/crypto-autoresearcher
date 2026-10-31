# Validation report: EXP-SEMAEV-93d5cc matched legacy/repaired S4 rerun (TASK-20261018-83a561)

- Report id: VAL-20261024-c8a775
- Task: TASK-20261018-83a561 (role: validator; review plan EXP-SEMAEV-93d5cc-matched-rerun-review)
- Joint owned: `run_integrity_and_controls`, plus the plan's proves-too-much control and its blind re-derivation
- Validated at: 2026-10-24, HEAD `361f7b32f222bb5b2df0dda3f41dcc285633483d`, branch `claude/s4-matched-rerun-20261018`. The tracked tree was clean when work started. Three untracked paths appeared while I was working; none was written by me (see Attestation).
- Joint verdict: **holds** on all 7 validated cells, with the caveats in Limitations.
- Validation verdict: **passed**. The 7 output-validated run records are admissible receipts for the per-cell table. This says nothing about H-SEMAEV-94dab2 or any archived conclusion, and it authorizes no promotion.

Every check below was run on committed bytes. Archives were extracted into a session scratch directory under `/tmp/claude-0/.../scratchpad/x/<RUN-ID>/` (one new empty directory per run), and Python was run with `-I`. When the producer's `compare.py` or `check.py` was executed (check 5 and the CTRL-REEXTRACT re-run only), Python ran with `-I -B` so that no bytecode was written into the repository. The exact scripts are in the Appendix.

## Runs in scope

| Cell | Run | Experiment | Receipt status |
|---|---|---|---|
| icinv-m4 | RUN-SEMAEV-9cab7b | EXP-SEMAEV-93d5cc | output_validated |
| fib-004 | RUN-SEMAEV-3e69b6 | EXP-SEMAEV-93d5cc | output_validated |
| fib-005 | RUN-SEMAEV-4be606 | EXP-SEMAEV-93d5cc | output_validated |
| fib-decision | RUN-SEMAEV-894e27 | EXP-SEMAEV-93d5cc | output_validated |
| mtic-007 | RUN-SEMAEV-2a8498 | EXP-SEMAEV-93d5cc | output_validated |
| mtic-008 | RUN-SEMAEV-fcd67c | EXP-SEMAEV-93d5cc | output_validated |
| mtic-010b | RUN-SEMAEV-0e5876 | EXP-SEMAEV-6e9dcf (2nd successor) | output_validated |
| mtic-010b | RUN-SEMAEV-500a81 | EXP-SEMAEV-93d5cc | interrupted (no receipt) |
| mtic-010b | RUN-SEMAEV-980e8c | EXP-SEMAEV-88c46c (1st successor) | interrupted (no receipt) |

---

## Check 0: snapshot, frozen bindings, revision, dirty state, environment

**What I did**
- `git status --short` at start: empty (tracked tree clean). `git ls-files` lists every file of all 9 run directories, so every byte validated is committed. The run commits are a34afc78bb, ef0b7a8319, c418440b90, fec8cb0bb8, f1bf275a7a and 5dcd02c6ef (93d5cc), 93280014b7 (6e9dcf), and 74fc2154dc / a934929fde (interrupted attempts preserved).
- `sha256sum` of the three trial plans against the approval decisions: 93d5cc `2842d7b3...` = DEC-20261018-a7a0fd; 88c46c `670ad0cf...` = DEC-20261019-5b9240; 6e9dcf `6fe1fc2c...` = DEC-20261019-ebf1dc. The specifications hash to `19072698...`, `7b45ae4c...` and `57658efd...`, matching each decision and each run's environment.json.
- Every entry in each trial plan's `input_sha256` and `source_sha256` (44, 40 and 40 entries) re-hashed on the current tree: 0 mismatches. Pinned S4 sources: vendor legacy file `53a23952420f8ee7...` and `harness/semaev.py` `c417f1948d7df7bb...`, both equal to the specification's `arms` block.
- `manifests.py` (Appendix A2). For each run's `code.commit` and its environment.json start commit, I ran `git show <commit>:<path>` for every pinned source and found 0 drifts at either commit. `dirty: false` in all 7 manifests. The manifest command equals the plan argv in 6 of 7 runs; RUN-SEMAEV-0e5876 is the exception (see Limitations L2). Environment in all 7 runs: Python 3.13.16, Linux x86_64, 4 CPUs, sympy 1.14.0; icinv-m4 also records Singular 4.4.1. These are the values the specification declares.
- The review plan (`b267d4f0...`) has been byte-identical since commit 28789aca0c (2026-10-18 22:03:07Z), which is before the first trial finished (22:31:34Z). Its source_snapshot c0b5dded is an ancestor of HEAD and carries the same spec, trial plan, hypothesis and decision bytes as HEAD.
- Invalidation rule "no archived experiment directory written": `git log --since 2026-10-18T21:00Z` and `git status --untracked-files=all` on experiments/EXP-MTIC-001, EXP-FIB-001 and EXP-ICINV-e0cd8f show 0 commits and 0 changes.
- Pairing: in every run both arms started within 0.05 s of each other, and their execution intervals overlap for the full duration of the shorter arm (`started_unix`/`finished_unix` in arm-result.json).

**Result: PASS.** The record limitations are L1, L2 and L8.

## Check 8: receipts (artifact_sha256 against the files on disk)

**What I did** (`receipts.py`, Appendix A1). For each validated run I compared every `execution-receipt.json` `artifact_sha256` entry with both the on-disk sha256 and the sha256 of the committed blob (`git show HEAD:<path>`). I also checked plan_sha256, trial_id/run_id, status, returncode and check_returncode, that no file in the run directory is unhashed, that every plan-required artifact is present, and that no empty file falls outside `allow_empty_artifacts`.

**Result**

| Run | hashed | mismatched | unhashed files | plan sha | status | rc / check rc |
|---|---|---|---|---|---|---|
| RUN-SEMAEV-9cab7b | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-3e69b6 | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-4be606 | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-894e27 | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-2a8498 | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-fcd67c | 15 | 0 | 0 | ok | output_validated | 0 / 0 |
| RUN-SEMAEV-0e5876 | 15 | 0 | 0 | ok | output_validated | 0 / 0 |

I also checked the archive contents (`extract.py`, Appendix A3). Each `arms.tar.gz` was extracted with `tarfile` `filter="data"` into a fresh scratch directory. The member sets equal the `arms-manifest.json` keys (4, 16, 16, 30, 26, 26 and 50 members), every member sha256 matches, there are no non-file members, and each archive's `raw-result.json.arms_archive_members` count agrees. The only empty members are program stderr files.

I re-ran the recorded checker as a CTRL-REEXTRACT replay, using the producer's code: `python3 -I -B experiments/EXP-SEMAEV-93d5cc/implementation/check.py <run_dir> <plan>` for all 7 runs, with TMPDIR set to the scratchpad. Every run gave rc 0, `pass: true`, `failures: []`, and stdout byte-equal to the committed `check.stdout.log`.

**Result: PASS.**

## Check 1: arm swap (did an arm run the other arm's S4?)

**What I did** (`armswap.py`, Appendix A4). For each run and arm I read the archived `arms/<arm>/arm-result.json` and checked that it is byte-equal (as JSON) to `raw-result.json.arm_results[arm]`. I then checked its `arm`, `provenance.arm`, `s4_source`, `s4_source_sha256`, `installed_into`, `installed_function_module` and `installed_fingerprint`, and the pre-install `s4_fingerprint`. For fib-004 and fib-005 I tallied every `fib_child` line in `arm-<arm>.stderr.log` with `grep '^fib_child ' | sort | uniq -c`.

**Result**
- icinv-m4, mtic-007, mtic-008, mtic-010b: legacy has sha `53a23952...` and module `harness._semaev_legacy_53a23952`, and its installed fingerprint has free symbols {x1,x2,x4}, 227 terms over Z, total degree 16, witness residue 47. Repaired has sha `c417f194...` and module `harness.semaev`, with free symbols {x1,x2,x3,x4}, 439 terms, total degree 12, residue 0. The installed fingerprint equals the pre-install self-test in every arm.
- fib-004 and fib-005 install inside the spawn child, so they have no `installed_fingerprint`. Provenance sha and self-test are as above. The child lines are uniform per arm:
  - RUN-SEMAEV-3e69b6: legacy has 275 lines, all `fib_child arm=legacy module=harness._semaev_legacy_53a23952 sha256=53a23952420f`. Repaired has 231 lines, all `arm=repaired module=harness.semaev sha256=c417f1948d7d`. The only other stderr line in each log is the run-status line.
  - RUN-SEMAEV-4be606: 90 legacy lines and 90 repaired lines, each uniform in the same way.
  - The line counts equal the number of solves each arm measured: fib-004 legacy 200 + 75 = 275 and repaired 200 + 31 = 231; fib-005 75 + 15 = 90 in each arm.
- fib-decision: `s4_used: false` (the arm only selects its upstream input; see check 4). The self-test fingerprints match the arm labels.
- Bypass check: the three consumers call `s4_expr(a, b)` through the module-global name that `arms.install` rebinds (`run_mtic.py:663`, `driver/decompcost.py:29`, `harness/exp_icinv_e0cd8f_m3class.py:57,67`; each imports it with `from ... import s4_expr`). So the installed binding is the one called.
- Output-level corroboration, independent of provenance:
  - ICINV: the legacy arm reproduces the archived 227/225/210 supports, and the repaired arm gives 439/391. Both sets match my blind exact/sequential-substitution counts for the same curves (check 6).
  - fib-004 C16-1: per-target basis sizes are 3/4 in legacy and the archive, and 14 to 19 in repaired.
  - MTIC: `setup.s4_resultant_seconds` is about 0.21 s in legacy and 0.59 to 0.71 s in repaired, in 007 and 008 at every size.

**Result: PASS.** No arm ran the other arm's S4 (attack `arm_swap` failed to break).

## Check 2: extraction (re-extract one value per cell by hand and compare with `comparison`)

I wrote my own extraction scripts and did not import `compare.py` for this check. I read compare.py only afterwards (see Attestation for one earlier `rg median` hit). Scripts: Appendix A5 to A8.

- **icinv-m4 (RUN-SEMAEV-9cab7b)**: `icinv_extract.py`.
  - Records keyed (set, index, role) from the archived control-set-invariants.json and per-curve-invariants.json (base m4 and gauge.m4) and from each arm's `m4-records.json`.
  - My summaries (s4_support counts per set, singular-locus dim/degree counts, unit-ideal counts, n_error, gauge agreement, class-vs-control tuple-set equality, max wall) equal `comparison.archived/legacy/repaired` field by field, and the four conclusion fields equal `conclusion_fields`.
  - Hand row, first control curve (3603, 2402) base: archived (227, 2, 60, False), legacy (227, 2, 60, False), repaired (439, 2, 39, False). Its gauge twin (370, 3784) gives repaired (439, 2, 39, False).
  - s4_support values: archived = legacy = {210, 225, 227}, repaired {391, 439}. Singular locus: archived = legacy {2/60}, repaired {2/39}. Records differing repaired vs legacy: 552 of 552, equal to the recorded value.
- **fib-004 (RUN-SEMAEV-3e69b6)**: `fib_extract.py`.
  - From the archived `EXP-FIB-001/runs/RUN-FIB-004/raw.json` and each arm's `runs/RUN-FIB-004/raw.json`, every count equals `comparison` (n_measured, n_capped, n_solved, n_trivial_ideal, basis-size counts, basis-max-degree counts, resource_exhaustion, stop_reason). Header n_measured and n_capped agree with the measurement lists, and worker_error is null on every solve.
  - C16-1 hand rows for targets 0 to 4 (capped, basis size, max degree, trivial): archived = legacy = (F,4,5,F), (F,3,5,F), (F,4,5,F), (F,4,5,F), (F,4,5,F); repaired (F,16,6,F), (F,18,5,F), (F,19,5,F), (F,14,6,F), (F,17,5,F). Repaired basis-size counts {14:61, 16:28, 17:36, 18:16, 19:59} equal the recorded counts.
  - C16-2 n_measured: archived 75, legacy 75, repaired 31, matching the recorded values.
  - The one difference is `median_cost_seconds` on C16-1: my conventional median is 0.0279151, the recorded value 0.0279397. The recorded value is the upper median `sorted(costs)[n//2]`, which reproduces exactly in all three sources. The archived driver uses the same convention (`orchestrate.compute_predictor_cost_ratio`). This is a convention, not a misread (L5).
- **fib-005 (RUN-SEMAEV-4be606)**: same script. All fields equal `comparison`. C20-1 has n_measured 75 with all 75 capped, and C20-2 has 15 with all 15 capped, in all three sources. Stop reasons are per_curve_cumulative_cap_1500s and per_run_wall_cap_1800s in all three. Hand rows for targets 0 to 4 are (T, None, None, F) in every source.
- **fib-decision (RUN-SEMAEV-894e27)**: `fibdec_extract.py`.
  - I recomputed Spearman rho_s for C16-1 myself (average ranks, then Pearson) from the archived RUN-FIB-002 `n_R_per_target` and each source's own RUN-FIB-004 `cost_seconds`. Results: archived -0.023615555909563, legacy -0.096911244251097, repaired -0.365603791488796. These equal the recorded values to the last printed digit (|diff| = 0).
  - Recomputed by the archived rules, all equal to the recorded values: per-curve status (measured if at least 100 measured, otherwise resource_exhaustion); predictor cost ratios (RUN-FIB-007 amortized seconds per target divided by the upper-median cost); the cost gate (ratio <= 0.1 on at least 3 curves); the correlation gate (|rho_s| >= 0.4 and p < 0.01 on a measured curve, with at least 3 such curves needed overall); gate_pass; and the RUN-FIB-008 outcome. The gate rule was read from `orchestrate.py:378-396, 442-455`.
  - The archived side of `comparison` equals RUN-FIB-006C raw.json and summary.json, and its ratios equal the RUN-FIB-008 summary's reason string. Each arm's `decision.json` and `runs/RUN-FIB-006C` agree with `comparison`.
  - The p-values come from the producer's permutation test. I did not recompute them; I only read them.
- **mtic-007 (RUN-SEMAEV-2a8498)** and **mtic-008 (RUN-SEMAEV-fcd67c)**: `mtic_extract.py`.
  - From `raw.per_target`, I computed n_attempted, n_capped, n_uncapped, n_trivial, n_aux and n_cancelled myself, and the median from `charged_seconds`. All equal `comparison`, and the conclusion fields equal `conclusion_fields`.
  - 007, 16-bit: 25 attempted, all 25 capped, median 60.0. Hand row index 0, (a, b) = (3257, 11262): capped, basis (0, 0), trivial None in all three sources.
  - 008: 20-bit has 13 attempted, all capped; 24-bit has 12 attempted, all capped; medians 60.0. The attempted index sets and per-index (a, b) are identical across archive, legacy and repaired (25/25, 13/13, 12/12).
- **mtic-010b (RUN-SEMAEV-0e5876)**: `mtic010b_extract.py`.
  - From `metrics.decision_matrix[bits].accountings[*].K_star`, `regime_per_accounting`, `n_uncensored_solves` and the ablation blocks, all values equal `comparison` and `conclusion_fields`. K* is infinite in all 3 accountings at 16, 20 and 24 bits, the regime is "(i) K* infinite", and n_uncensored is 0, in all three sources. Ablation B = 52 (cbrt) gives 13 of 13 capped and B = 115 (2_5) gives 12 of 12 capped, with K* infinite.
  - I re-derived "K* infinite iff T_desc >= sqrt_n" in every accounting. For example, at 16 bits in the rho accounting, T_desc is 9.85e7 group-op equivalents against sqrt_n 132.8.
  - `upstream_missing_or_invalid = []` and validity is valid in all three sources.

**Result: PASS.** compare.extract reads every checked archived and arm field correctly (attack 2 failed to break). The `median` label is the upper median, the archived convention.

## Check 3: vacuous control (does CTRL-LEGACY-REPRO compare non-empty sets?)

**What I did.** I rebuilt CTRL-LEGACY-REPRO with my own code, per the specification's per-cell rules, in the check-2 scripts, and compared the result with `comparison.ctrl_legacy_repro`. Afterwards I read `compare.legacy_control` and `_prefix_equal` to look for an emptiness guard.

**Result**

| Cell | Compared population (legacy vs archive) | My control | Recorded |
|---|---|---|---|
| icinv-m4 | 552 of 552 records, identical keys and (a, b) in all three sources, 552 non-null archived tuples, 552 equal | pass | pass, `records_equal: 552/552` |
| fib-004 | C16-1 n_common 200, C16-2 n_common 75; per-target equal; n_measured diff 0 | pass | pass |
| fib-005 | C20-1 n_common 75, C20-2 n_common 15 | pass | pass |
| fib-decision | correlation_gate_pass_overall, curves_passing, per_curve_status equal | pass | pass |
| mtic-007 | 16-bit n_common 25 | pass | pass |
| mtic-008 | 20-bit n_common 13, 24-bit n_common 12 | pass | pass |
| mtic-010b | decision matrix 16/20/24 (regime, K*, n_uncensored) and 2 ablation bases | pass | pass |

No control passes on an empty common set or zero records (attack `empty_common_prefix` failed to break). Two qualifications:
- **Latent guard gap.** The frozen rule has no non-emptiness guard. `_prefix_equal` returns `all([]) == True` with `n_common = 0`, the FIB and MTIC pass conditions do not require `n_common > 0`, and icinv passes if `0 == 0 == 0`. The guard was not needed here, as the counts above show.
- **Saturation (discriminating power).** In fib-005, mtic-007, mtic-008 and mtic-010b, every compared solve is capped in all three sources, so the compared per-target tuples are constant (capped, None/0, None/0, ...). fib-decision's frozen fields are fixed by resource_exhaustion on 3 of 4 curves. Check 5's SWAP object shows that the control in these 5 cells passes even with the repaired arm in the legacy slot. There, the control tests reproduction of the cap pattern and attempted-target set, not of S4-sensitive output (L3).

**Result: PASS** (non-vacuous), with the saturation caveat.

## Check 4: wrong dependency arm

**What I did** (`deps_check.py`, Appendix A9). For fib-decision (RUN-SEMAEV-894e27) and mtic-010b (RUN-SEMAEV-0e5876) I read each arm's archived `inputs.json`. I compared each recorded sha256 with three things: the dependency run's `arms-manifest.json` members for the same arm and for the other arm; the trial-plan pin, for archived S4-independent inputs; and the bytes actually present in this run's archive. I also confirmed that `run_mtic.py` reads upstream runs from `--out-root` (`READ_EXP_DIR = out_root`, lines 1246 and 2309-2311), and that the arm's 010b decision-matrix counts equal its own upstream copies.

**Result**
- fib-decision legacy: `inputs/RUN-FIB-004/raw.json` and `RUN-FIB-005/raw.json` match RUN-SEMAEV-3e69b6 and RUN-SEMAEV-4be606 `arms/legacy/...` and do not match `arms/repaired/...`. The legacy and repaired members differ (89493 vs 75278 bytes for FIB-004). The repaired arm is the mirror image. RUN-FIB-002, -003 and -007 equal their trial-plan pins and the archived bytes.
- mtic-010b legacy: `out-root/runs/RUN-MTIC-007/raw.json` and `RUN-MTIC-008/raw.json` match RUN-SEMAEV-2a8498 and RUN-SEMAEV-fcd67c `arms/legacy/...` and do not match the repaired members (11171 vs 11175 and 12992 vs 12995 bytes). The repaired arm is the mirror image. RUN-MTIC-002 to -006, -009 and frozen-instances.yaml equal their pins.
- The tar bytes equal the inputs.json hashes for every input.
- Both arms of 010b report `upstream_missing_or_invalid = []`, and their decision-matrix attempted/capped counts equal their own upstream copies.

**Result: PASS.** Each dependency cell consumed its own arm's upstream outputs (attack `wrong_dependency_arm` failed to break). The check discriminates, because the two arms' upstream files differ. The 010b outputs alone could not have shown this, since both upstream arms are all-capped with equal counts.

## Check 5: proves-too-much (legacy compared with itself)

**What I did** (`ptm.py`, Appendix A10). For each of the 7 runs I built scratch run directories from the extracted arms and ran the producer's `compare.compare(cell, dir)` on them, using `python3 -I -B` and reading the archive in place. I built four objects:
- **LL**: legacy bytes in both slots. This is the plan's object.
- **RR**: repaired bytes in both slots.
- **SWAP**: repaired bytes in the legacy slot, legacy bytes in the repaired slot. This is a sensitivity probe of CTRL-LEGACY-REPRO.
- **REAL**: legacy and repaired in their own slots. This is a CTRL-REEXTRACT replay.

With my own extraction, the corresponding A/A (legacy against archive) already holds at conclusion level: in check 2, legacy conclusion fields equal archived ones in every cell.

**Result**

| Cell | LL: changed vs legacy | LL: changed vs archive | LL ctrl | RR: changed vs legacy | SWAP ctrl | REAL == recorded |
|---|---|---|---|---|---|---|
| icinv-m4 | none (0 records differ) | none | pass | none | **fail** | yes |
| fib-004 | none | none | pass | none | **fail** | yes |
| fib-005 | none | none | pass | none | pass | yes |
| fib-decision | none | none | pass | none | pass | yes |
| mtic-007 | none | none | pass | none | pass | yes |
| mtic-008 | none | none | pass | none | pass | yes |
| mtic-010b | none | none | pass | none | pass | yes |

The failure signature ("any conclusion field reported changed between legacy and legacy") does not occur. The extraction does not invent changes, and it does report changes where they exist: REAL shows icinv `m4_s4_support_values` and `m4_singular_locus_dim_degree_values` changed. SWAP shows the control is discriminating in icinv-m4 and fib-004 and saturated in the other five cells (check 3, L3).

**Result: PASS.**

## Check 6: blind re-derivation (S4 term count mod p; free symbols of the legacy substitution)

**Blindness.** I ran the first computation, (a, b) = (3603, 2402) at p = 4001, before opening `arms.py` or any arm output. I never opened `harness/semaev.py` or the vendored legacy file; I only hashed them. The script uses sympy and nothing from the repository. I knew the target numbers 439 and 227 beforehand from the review plan's prior, the specification and the archived JSON. The derivation is code-blind, not number-blind. I computed the additional curves and the fixture later with the same unchanged script, after seeing arm values.

**Statement implemented.** S3(u,v,w) = (u-v)^2 w^2 - 2((u+v)(uv+a)+2b) w + ((uv-a)^2 - 4b(u+v)), and S4(x1,x2,x3,x4) = Res_t(S3(x1,x2,t), S3(x3,x4,t)). I computed the resultant generically over Z[A,B] and specialized it mod p. As a cross-check I also computed it directly over GF(p) and checked symmetry and vanishing. Script: `blind_s4.py` (Appendix B1). Command: `python3 -I scripts/blind_s4.py 3603 2402 4001`.

**Result**, first control curve, p = 4001:
- Generic S4 has 540 terms over Z[A,B]. Mod 4001 at (3603, 2402) it has **439 terms**, total degree 12, degree list (4,4,4,4), free symbols {x1,x2,x3,x4}. The direct GF(p) resultant is identical.
- S4 is symmetric under x1<->x2, x3<->x4 and (x1,x2)<->(x3,x4), and it vanishes on 12 of 12 quadruples of x-coordinates of points with P1+P2+P3+P4 = O on the curve.
- This equals the repaired arm's `s4_support` for this record, 439 (record ('control', 0, 'base')), and for its gauge twin (370, 3784), also 439.
- Sequential substitution {x1->x3, x2->x4, x3->t}, applied one at a time to S3(x1,x2,x3), gives S3(t,x4,t). Its free symbols are {t, x4}, so **x3 is dropped**. The simultaneous substitution gives S3(x3,x4,t) with {t, x3, x4}. sympy's default `subs(dict)` equals the sequential result.
- Res_t(S3(x1,x2,t), S3(t,x4,t)) mod 4001 has **227 terms**, total degree 16, degree list (8,8,0,2), and free symbols **{x1, x2, x4}**. This is the archived and legacy `s4_support` 227 for the record and the pinned legacy fingerprint.

**Extra points**, same script (`blind_s4_multi.py`, Appendix B2):

| (a, b, p) | exact S4 terms mod p | sequential-substitution terms | arm values (repaired / legacy = archived) |
|---|---|---|---|
| (3603, 2402, 4001) control[0] base | 439, deg 12 | 227, deg 16, {x1,x2,x4} | 439 / 227 |
| (370, 3784, 4001) control[0] gauge | 439 | 227 | 439 / 227 |
| (441, 294, 4001) class[77] base | **391** | **210** | 391 / 210 |
| (1506, 3218, 4001) class[77] gauge | **391** | **210** | 391 / 210 |
| (1509, 1006, 4001) class[34] base | 439 | **225** | 439 / 225 |
| (2, 3, 101) a097b5 fixture | 439 terms over Z, deg 12, residue 0 at (1,3,5,41) | 227 over Z, deg 16, residue 47 | the fingerprints recorded in every arm |

The 391 has a mechanical explanation (`blind_vanish.py`, Appendix B3). At (441, 294), a^3 / b^2 ≡ -8 (mod 4001), so a^3 + 8b^2 ≡ 0. That zeroes 48 of the 439 generic coefficients (the four largest families, 40 coefficients, all carry the factor A^3 + 8B^2), leaving 439 - 48 = 391. The gauge map preserves a^3/b^2, so the twin is also 391. So the two 391 records are a property of the curve, not of the instrument. This is relevant to P1 of H-SEMAEV-94dab2, which predicts 439 on every record. Interpreting P1 is not part of my joint.

**FIB/MTIC solver tuple.** The handoff objective also mentions a blind re-derivation of "one FIB/MTIC solver tuple"; the review plan's `blind_rederivation` does not. I did not perform it. The parameters do not determine such a tuple: `EXP-FIB-001/frozen-instances.yaml` gives (p, a, b, B, N, seed) per curve, but the target abscissa x_R, the factor base V, the generator set and the Groebner monomial order are fixed only in the producer's driver (`instances.py`, `decompcost.py`). Basis size and maximum degree depend on the order. Per agents/validator.md I am reporting this underspecification rather than reading the solver to fill it in.

**Result: PASS** for the plan's blind quantity (exact S4 term count mod p for one ICINV curve; free-symbol set of the legacy S4). **Not derivable (finding)** for the handoff's additional FIB/MTIC solver tuple.

## Check 7: interrupted runs (nothing readable as a result)

**What I did** (`interrupted.py`, Appendix A11, plus `ls` and `find`).
- RUN-SEMAEV-500a81 and RUN-SEMAEV-980e8c have no execution-receipt.json, raw-result.json, manifest.yaml, arms.tar.gz, arms-manifest.json or check.stdout.log at the top level. `stdout.log` holds only the two "started <arm>: pid" lines.
- Each run does contain `deps/mtic-007/` and `deps/mtic-008/` trees that include raw-result.json, arm-result.json, manifest.yaml and summary.json files. These are the unpacked dependency archives: 26 files each, with the file set and bytes identical to the RUN-SEMAEV-2a8498 and RUN-SEMAEV-fcd67c `arms-manifest.json` members. They are copies of validated inputs, not results of the interrupted attempt.
- `arms/` holds 26 files per run: the copied archived inputs (frozen-instances.yaml, RUN-MTIC-002 to -009 raw/relations) and inputs.json. There is no RUN-MTIC-010b path and no arm-result.json.
- The arm stdout logs end mid-ablation:
  - 500a81: legacy ends at `[ablation-ablation_cbrt] target 6 ... capped=True`, repaired at `[ablation-ablation_2_5] target 5 ... capped=True`. This matches AMD-EXP-SEMAEV-93d5cc-20261019-mtic010b-successor.
  - 980e8c: both arms end at `[ablation-ablation_2_5] target 6`.
  - No aggregation (K* or regime) appears in either run.

**Result: PASS.** Nothing in either interrupted run can be read as a result. Both are correctly preserved as non-evidence, and they are infrastructure losses, not negative evidence.

---

## Per-cell table

| Cell | Run | Joint holds | Defect / caveat |
|---|---|---|---|
| icinv-m4 | RUN-SEMAEV-9cab7b | yes | None in the joint. Control discriminating (SWAP fails). Manifest commit is the end-of-run HEAD (L1). |
| fib-004 | RUN-SEMAEV-3e69b6 | yes | None in the joint. Control discriminating. `median_cost_seconds` is the upper median (L5). The repaired C16-2 was truncated by the shared 1800 s per-run cap after 31 targets, not the per-curve cap (L4). Manifest commit as L1. |
| fib-005 | RUN-SEMAEV-4be606 | yes | None in the joint. Saturated: every solve is capped in all sources, and the control and conclusion fields cannot distinguish the two S4s (L3). Manifest commit as L1. |
| fib-decision | RUN-SEMAEV-894e27 | yes | None in the joint. Gate fields are fixed by resource_exhaustion on 3 of 4 curves (the overall correlation gate needs 3 measured curves), so they are saturated (L3). rho_s recomputed exactly. |
| mtic-007 | RUN-SEMAEV-2a8498 | yes | None in the joint. Saturated: 25 of 25 capped in every source (L3). Manifest commit as L1. |
| mtic-008 | RUN-SEMAEV-fcd67c | yes | None in the joint. Saturated: 13 of 13 and 12 of 12 capped (L3). Manifest commit as L1. |
| mtic-010b | RUN-SEMAEV-0e5876 (EXP-SEMAEV-6e9dcf) | yes | None in the joint. Saturated: K* infinite and regime (i) from 60 s-capped T_desc in every source (L3). The manifest `code.command` names the parent launch.py, not launch_successor.py (L2). |
| mtic-010b | RUN-SEMAEV-500a81 (interrupted) | n/a | No result. Correctly non-evidence. |
| mtic-010b | RUN-SEMAEV-980e8c (interrupted) | n/a | No result. Correctly non-evidence. |

No cell is returned to the executor. None of the caveats breaks the joint, and none requires a repair of producer artifacts.

## Limitations and observations (for the Coordinator; none changes the joint verdict)

- **L1 (record).** In RUN-SEMAEV-9cab7b, -3e69b6, -4be606, -2a8498 and -fcd67c, `manifest.yaml code.commit` is the HEAD at the end of the run, because the executor committed the previous run, and once the review plan, while the trial ran. The start revision is in environment.json and launch.json `authority.commit`. No pinned source or implementation file differs between the two commits, so there is no code drift. But the manifest field does not name the revision the trial started from.
- **L2 (record).** In RUN-SEMAEV-0e5876, `manifest.yaml code.command` records `/usr/bin/python3 experiments/EXP-SEMAEV-93d5cc/implementation/launch.py ...`. The parent launcher builds this string itself. The actual entry point, `experiments/EXP-SEMAEV-6e9dcf/implementation/launch_successor.py`, is recorded correctly in launch.json and command.txt.
- **L3 (discriminating power).** In fib-005, fib-decision, mtic-007, mtic-008 and mtic-010b, every S4-dependent solve is capped (20 s FIB, 60 s MTIC) in the archive and in both arms, or the gate is structurally fixed. In these cells CTRL-LEGACY-REPRO and the conclusion fields cannot distinguish the legacy and repaired S4s (SWAP passes). "Conclusion unchanged" there means "no change observable under the archived caps". It is not evidence that the solves behave the same below the cap. The one S4 marker visible in MTIC is setup time (about 3x slower with the repaired S4).
- **L4 (coupling).** In fib-004, the repaired C16-1 took 1189 s of wall time (sum of costs 931 s, against 12 s in legacy). The repaired C16-2 therefore ran only about 621 s before the 1800 s per-run cap, giving 31 measurements, against legacy's 75 under the 1500 s per-curve cap. Its conclusion fields (all capped, resource_exhaustion) are equal, but they come from a smaller sample with a different stop reason. The archived protocol couples the curves through the shared run cap. The 2026-10-18 timing drift is also visible in legacy vs archive: C16-1 upper-median cost is 0.058 s vs 0.028 s, and fib-decision rho_s is -0.097 vs -0.024 (p 0.17 vs 0.74). This is the A/A floor that the frozen gate-level control does not test.
- **L5 (label).** `median_cost_seconds` (compare.py:79) is the upper median `sorted[n//2]`, the archived driver's convention, not the conventional even-n median. It differs at the 4th significant figure on C16-1 and is not a conclusion field.
- **L6 (frozen-rule guard).** The CTRL-LEGACY-REPRO code has no `n_common > 0` or `n_records > 0` guard (check 3). It was not triggered here.
- **L7 (blind tuple).** The handoff's "one FIB/MTIC solver tuple" blind re-derivation is not derivable from the statement and parameters (check 6). The review plan does not require it. If the Coordinator wants it, the statement needs to fix x_R, V, the generator set and the monomial order.
- **L8 (resources).** The trial-level manifests record wall time but not peak memory. The 8 GB budget is machine protection, so this is a record gap, not an invalidation.
- **L9 (prediction context).** The repaired s4_support is 439 on 550 of 552 records and 391 on 2 (class curve 77 and its gauge twin). The blind derivation confirms 391 as the exact count mod 4001 there.
- **L10 (procedure).** The review plan's `written_at: 2026-10-18T22:10:00Z` is later than its own commit time (22:03:07Z). The `written_before` claim holds by the commit timestamp.
- **Out of scope by blindness.** I did not check the specification's required `reports/run-*` artifacts or the CTRL-IMMUNE-BY-IMPORT restatement, which lives in the report.

```yaml
validation_report:
  id: VAL-20261024-c8a775
  task_id: TASK-20261018-83a561
  run_ids: [RUN-SEMAEV-9cab7b, RUN-SEMAEV-3e69b6, RUN-SEMAEV-4be606, RUN-SEMAEV-894e27, RUN-SEMAEV-2a8498, RUN-SEMAEV-fcd67c, RUN-SEMAEV-0e5876, RUN-SEMAEV-500a81, RUN-SEMAEV-980e8c]
  artifact_checks:
    - "receipts: 7/7 runs, 15/15 artifact_sha256 each equal to disk and to HEAD blobs; plan sha256 ok; status output_validated; rc 0; check rc 0"
    - "arms.tar.gz: 7/7 member sets equal arms-manifest.json; all member sha256 match"
    - "trial plans and specs hash-equal to DEC-20261018-a7a0fd, DEC-20261019-5b9240, DEC-20261019-ebf1dc; all pinned inputs and sources unchanged; dirty false; no drift at start or end commits"
    - "interrupted RUN-SEMAEV-500a81, RUN-SEMAEV-980e8c: no receipt, raw-result, manifest or archive; deps/ are byte copies of validated dependencies; no 010b output"
    - "archived experiment directories not written (no commits, no working-tree changes)"
  metric_recomputations:
    - "icinv-m4: s4_support / singular-locus / gauge / tuple-set summaries from archived JSON and m4-records.json equal comparison; 552/552 legacy==archive; 552 repaired!=legacy"
    - "fib-004/005: n_measured, n_capped, n_solved, basis-size and degree counts, resource_exhaustion, stop_reason equal; median is the upper median (archived convention)"
    - "fib-decision: Spearman rho_s(C16-1) recomputed exactly (-0.0236 / -0.0969 / -0.3656); cost ratios, statuses, gates, RUN-FIB-008 outcome equal"
    - "mtic-007/008: counts and medians from per_target equal; mtic-010b: K*, regime, n_uncensored, ablation K* equal; K* infinite re-derived from T_desc >= sqrt_n"
  control_checks:
    - "CTRL-ARM-FINGERPRINT: legacy 53a23952 {x1,x2,x4} deg16 res47; repaired c417f194 {x1,x2,x3,x4} deg12 res0, every arm; fib_child lines uniform per arm and equal to solve counts (275/231, 90/90)"
    - "CTRL-REEXTRACT: check.py re-run passes 7/7 with byte-equal stdout; compare REAL object equals recorded comparison 7/7"
    - "CTRL-LEGACY-REPRO: non-empty in every cell (552 records; n_common 200/75, 75/15, 25, 13/12; 010b 3 sizes and 2 bases); discriminating in icinv-m4 and fib-004, saturated in fib-005, fib-decision, mtic-007/008/010b"
    - "proves-too-much (legacy vs legacy): no conclusion field changed in any cell"
    - "wrong dependency arm: fib-decision and mtic-010b each consumed its own arm's upstream bytes (own-arm member match, other-arm mismatch)"
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  blind_rederivation:
    quantity: "exact S4 = Res_t(S3(x1,x2,t), S3(x3,x4,t)) term count mod 4001 at (a,b) = (3603,2402); free symbols of the sequential-substitution S4"
    value: "439 terms, total degree 12, free {x1,x2,x3,x4}; sequential {x1->x3,x2->x4,x3->t} gives S3(t,x4,t), so Res has 227 terms, deg 16, free {x1,x2,x4}"
    agrees_with_producer: true
    fib_mtic_solver_tuple: "not derivable from statement and parameters (x_R, V, generators, monomial order unspecified); not attempted"
  verdict: passed
  limitations: [L1 manifest commit is end-of-run HEAD, L2 successor manifest command names parent launcher, L3 saturation in five cells, L4 fib-004 C16-2 run-cap coupling, L5 upper-median label, L6 no non-emptiness guard in control code, L7 blind solver tuple underspecified, L8 no trial-level peak memory, L9 two 391 records explained, L10 review-plan written_at after its commit]
  artifact_paths:
    - experiments/EXP-SEMAEV-93d5cc/reviews/TASK-20261018-83a561/validation-report.md
review_attestation:
  task_id: TASK-20261018-83a561
  joints_owned: [run_integrity_and_controls, proves_too_much (legacy vs legacy), blind_rederivation (S4 term count, legacy free symbols)]
  sources_read:
    - docs/agent-runtime-core.md
    - agents/validator.md
    - AGENTS.md (heading list; section "Review architecture", lines 362-375)
    - ledger/handoffs/TASK-20261018-83a561.yaml
    - experiments/EXP-SEMAEV-93d5cc/reviews/review-plan.yaml
    - experiments/EXP-SEMAEV-93d5cc/specification.yaml
    - experiments/EXP-SEMAEV-93d5cc/trial-plan.json
    - experiments/EXP-SEMAEV-88c46c/trial-plan.json (trials, hashes)
    - experiments/EXP-SEMAEV-6e9dcf/trial-plan.json (trials, hashes)
    - experiments/EXP-SEMAEV-88c46c/specification.yaml and experiments/EXP-SEMAEV-6e9dcf/specification.yaml (sha256 only)
    - experiments/EXP-SEMAEV-93d5cc/amendments/AMD-EXP-SEMAEV-93d5cc-20261019-mtic010b-successor.yaml
    - experiments/EXP-SEMAEV-88c46c/amendments/AMD-EXP-SEMAEV-88c46c-20261019-successor.yaml
    - experiments/EXP-SEMAEV-93d5cc/implementation/{arms.py, fib_child.py, check.py, worker.py, launch.py} (read after the blind computation)
    - experiments/EXP-SEMAEV-93d5cc/implementation/compare.py (an rg for "median" after the FIB extraction, then lines 16-30, 31-168 and 170-300 after all independent extractions)
    - experiments/EXP-SEMAEV-93d5cc/implementation/vendor/semaev_legacy_53a23952.py and harness/semaev.py (sha256 only, never opened)
    - experiments/EXP-SEMAEV-6e9dcf/implementation/launch_successor.py; experiments/EXP-SEMAEV-88c46c/implementation/launch_successor.py (diff)
    - ledger/hypotheses/H-SEMAEV-94dab2.yaml (predictions block, lines 105-120)
    - ledger/decisions/DEC-20261018-a7a0fd.yaml, DEC-20261019-5b9240.yaml, DEC-20261019-ebf1dc.yaml
    - the 7 validated run directories (all supervisor files; arm stderr logs of fib-004/005 by grep) and their extracted arms.tar.gz members, by key (not opened: arms/*/out-root/analysis.md in RUN-SEMAEV-0e5876)
    - experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-500a81 and experiments/EXP-SEMAEV-88c46c/runs/RUN-SEMAEV-980e8c (listing, stdout.log, arm stdout last lines, deps hashes, inputs.json presence)
    - experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class/{control-set-invariants.json, per-curve-invariants.json}
    - experiments/EXP-FIB-001/runs/{RUN-FIB-002,003,004,005,007}/raw.json, RUN-FIB-006C/{raw.json, summary.json}, RUN-FIB-008/summary.json, frozen-instances.yaml (C16-1 block)
    - experiments/EXP-FIB-001/driver/orchestrate.py (lines 311-330, 378-386, 442-470); driver/decompcost.py, harness/exp_icinv_e0cd8f_m3class.py, experiments/EXP-MTIC-001/code/run_mtic.py (rg for s4_expr and input paths only)
    - experiments/EXP-MTIC-001/runs/{RUN-MTIC-007, RUN-MTIC-008, RUN-MTIC-010b}/raw.json
    - tools/experiment_execution.py (lines 770-790), tools/allocate_id.py (header), templates/research-records.md (review_attestation block)
    - git metadata (log, show, ls-files, status)
  not_read:
    - experiments/*/reports/ (forbidden)
    - experiments/EXP-SEMAEV-93d5cc/analysis.md (untracked; appeared at 2026-10-24T19:23:31Z during this session; 6370 bytes; not written by me; not opened)
    - ledger/corrections/CORR-20261018-d51221.yaml (untracked; appeared at 2026-10-24T19:33:51Z during this session; 6762 bytes; not written by me; not opened)
    - experiments/EXP-SEMAEV-93d5cc/reports/review-DEC-20261018-3b4a32/ (untracked; directory mtime 2026-10-24T19:44:02Z, during this session, after my checks were complete; under reports/, forbidden; not opened)
    - session scratchpad smoke/ (2026-10-18) and gen/ (2026-10-19) directories predating this task (not opened)
  read_sibling_reports: false
  blind_from_respected: true
  verdict: holds
  procedure_deviations_disclosed:
    - "This validator ran as a subagent of the Claude session whose scratchpad holds design-time smoke/ and gen/ outputs, plausibly the session that designed and executed the runs. My context excluded the producer's, and I opened none of those files. Whether this satisfies the handoff's independent_session_required: true is for the Coordinator to decide."
    - "Three untracked paths (above) appeared in the shared worktree while I worked: a draft analysis, a draft correction and a reports/review-DEC-* directory. Their contents are unknown to me, and I make no claim about how they relate to this validation."
    - "The blind derivation was code-blind but not number-blind: the expected 439 and 227 appear in the review plan's prior, the specification and the archived JSON."
```

---

## Appendix: exact scripts run

The scripts were run from the session scratchpad: `/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/scripts/`. Archives were extracted into `.../scratchpad/x/<RUN-ID>/` and the proves-too-much objects built in `.../scratchpad/ptm/`. The listings below are the exact bytes executed.

### A1 `receipts.py` (sha256 847c81b9b4bfc768)

```python
import hashlib, json, subprocess, sys, os
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
RUNS = {
 'EXP-SEMAEV-93d5cc': ['RUN-SEMAEV-9cab7b','RUN-SEMAEV-3e69b6','RUN-SEMAEV-4be606','RUN-SEMAEV-894e27','RUN-SEMAEV-2a8498','RUN-SEMAEV-fcd67c'],
 'EXP-SEMAEV-6e9dcf': ['RUN-SEMAEV-0e5876'],
}
PLAN = {e: hashlib.sha256((REPO/'experiments'/e/'trial-plan.json').read_bytes()).hexdigest() for e in RUNS}
for exp, rids in RUNS.items():
    plan = json.loads((REPO/'experiments'/exp/'trial-plan.json').read_text())
    trials = {t['run_id']: t for t in plan['trials']}
    for rid in rids:
        d = REPO/'experiments'/exp/'runs'/rid
        r = json.loads((d/'execution-receipt.json').read_text())
        files = sorted(p.name for p in d.iterdir() if p.is_file())
        bad = []
        for name, h in r['artifact_sha256'].items():
            disk = hashlib.sha256((d/name).read_bytes()).hexdigest()
            blob = hashlib.sha256(subprocess.run(['git','show',f'HEAD:{(d/name).relative_to(REPO)}'],cwd=REPO,capture_output=True).stdout).hexdigest()
            if disk != h or blob != h: bad.append(name)
        extra = sorted(set(files) - set(r['artifact_sha256']) - {'execution-receipt.json'})
        missing_required = [a for a in trials[rid]['artifacts'] if a not in r['artifact_sha256']]
        empty_not_allowed = [n for n in trials[rid]['artifacts'] if (d/n).stat().st_size == 0 and n not in trials[rid].get('allow_empty_artifacts', [])]
        print(f"{rid} trial={r['trial_id']}({trials[rid]['id']}) status={r['status']} rc={r['returncode']} check_rc={r['check_returncode']} "
              f"plan_sha_ok={r['plan_sha256']==PLAN[exp]} n_hashed={len(r['artifact_sha256'])} mismatched={bad} unhashed_files={extra} "
              f"required_missing={missing_required} empty_disallowed={empty_not_allowed} published={r['published']} sci={r['scientific_conclusion']} "
              f"commit={r['authority']['commit'][:10]} started={r['started_at']} finished={r['finished_at']}")
```

### A2 `manifests.py` (sha256 7475b25e9bdf1ac3)

```python
import hashlib, json, subprocess, yaml
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
RUNS = {'EXP-SEMAEV-93d5cc': ['RUN-SEMAEV-9cab7b','RUN-SEMAEV-3e69b6','RUN-SEMAEV-4be606','RUN-SEMAEV-894e27','RUN-SEMAEV-2a8498','RUN-SEMAEV-fcd67c'],
        'EXP-SEMAEV-6e9dcf': ['RUN-SEMAEV-0e5876']}
def blob_sha(commit, path):
    r = subprocess.run(['git','show',f'{commit}:{path}'],cwd=REPO,capture_output=True)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 else None
for exp, rids in RUNS.items():
    plan = json.loads((REPO/'experiments'/exp/'trial-plan.json').read_text())
    trials = {t['run_id']: t for t in plan['trials']}
    for rid in rids:
        d = REPO/'experiments'/exp/'runs'/rid
        m = yaml.safe_load((d/'manifest.yaml').read_text())['run']
        env = json.loads((d/'environment.json').read_text())
        launch = json.loads((d/'launch.json').read_text())
        raw = json.loads((d/'raw-result.json').read_text())
        c = m['code']['commit']
        drift = [k for k, v in plan['source_sha256'].items() if blob_sha(c, k) != v]
        # successor launcher bytes at the commit
        extra = {}
        if exp != 'EXP-SEMAEV-93d5cc':
            for k, v in env['source_sha256'].items():
                if k not in plan['source_sha256']:
                    extra[k] = (blob_sha(c, k) == v)
        argv_plan = [a.replace('{run_dir}', str(d)) for a in trials[rid]['argv']]
        cmd_ok = m['code']['command'][1:] == argv_plan[1:] and launch['argv'] == argv_plan
        print(rid, 'exp', m['experiment_id'], 'status', m['status'], 'commit', c[:10], 'dirty', m['code']['dirty'],
              'pinned_src_drift_at_commit', drift, 'extra_src_ok', extra,
              'cmd_matches_plan', cmd_ok, 'env.commit==manifest', env['commit'] == c,
              'spec_sha_env', env['specification_sha256'][:8], 'py', m['environment']['python'], m['environment']['machine'],
              'cpu', m['environment']['cpu_count'], 'sympy', m['environment']['sympy'], 'singular', m['environment']['singular'],
              'ctrl', m['result']['ctrl_legacy_repro_pass'], 'valid', m['validity'], 'wall', round(m['timing']['wall_seconds'],1),
              'raw.run_id', raw['run_id'], 'raw.cell', raw['cell'], 'arm_rc', raw['arm_returncodes'], 'raw.error', raw['error'],
              'members', raw['arms_archive_members'], 'sci', raw['scientific_conclusion'])
```

### A3 `extract.py` (sha256 559bb2d9b9a21640)

```python
import hashlib, json, tarfile, sys
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
RUNS = {'RUN-SEMAEV-9cab7b':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-3e69b6':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-4be606':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-894e27':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-2a8498':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-fcd67c':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-0e5876':'EXP-SEMAEV-6e9dcf'}
for rid, exp in RUNS.items():
    d = REPO/'experiments'/exp/'runs'/rid
    out = X/rid
    out.mkdir(parents=True, exist_ok=False)
    man = json.loads((d/'arms-manifest.json').read_text())
    with tarfile.open(d/'arms.tar.gz', 'r:gz') as tar:
        mem = tar.getmembers()
        names = sorted(m.name for m in mem if m.isfile())
        nonfile = [m.name for m in mem if not m.isfile()]
        tar.extractall(out, filter='data')
    bad = [k for k, v in man['members'].items() if hashlib.sha256((out/k).read_bytes()).hexdigest() != v]
    sizes = {k: (out/k).stat().st_size for k in names}
    print(rid, 'members', len(names), 'manifest', len(man['members']), 'same_set', names == sorted(man['members']),
          'hash_mismatch', bad, 'nonfile', nonfile, 'empty', [k for k, s in sizes.items() if s == 0])
    for k in names: print('   ', k, sizes[k])
```

### A4 `armswap.py` (sha256 03f91e3f40ef5d7d)

```python
import json, re
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
RUNS = {'RUN-SEMAEV-9cab7b':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-3e69b6':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-4be606':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-894e27':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-2a8498':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-fcd67c':'EXP-SEMAEV-93d5cc','RUN-SEMAEV-0e5876':'EXP-SEMAEV-6e9dcf'}
LEG = '53a23952420f8ee724b70746eb7c872e54cbb33dc4cb24be1e88dcdcbef4817e'
REP = 'c417f1948d7df7bb1864726e169d885e4d3163cb62036393f2616ef71c630de6'
PIN = {'legacy': LEG, 'repaired': REP}
MOD = {'legacy': 'harness._semaev_legacy_53a23952', 'repaired': 'harness.semaev'}
for rid, exp in RUNS.items():
    d = REPO/'experiments'/exp/'runs'/rid
    raw = json.loads((d/'raw-result.json').read_text())
    for arm in ('legacy', 'repaired'):
        ar = json.loads((X/rid/'arms'/arm/'arm-result.json').read_text())
        same_as_raw = ar == raw['arm_results'][arm]
        pv = ar['provenance']; fp = ar['s4_fingerprint']; ifp = pv.get('installed_fingerprint')
        print(f"{rid} {raw['cell']:12s} {arm:8s} arm={ar['arm']} prov.arm={pv.get('arm')} src={pv.get('s4_source')} "
              f"sha_ok={pv.get('s4_source_sha256')==PIN[arm] if 's4_source_sha256' in pv else 'n/a(s4_used=%s)'%pv.get('s4_used')} "
              f"into={pv.get('installed_into')} fnmod={pv.get('installed_function_module')} fnmod_ok={pv.get('installed_function_module')==MOD[arm] if 'installed_function_module' in pv else 'n/a'} "
              f"selftest={fp} installed_fp={ifp} raw==tar:{same_as_raw}")
```

### A5 `icinv_extract.py` (sha256 b23d330c977f2a82)

```python
import json
from collections import Counter
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x/RUN-SEMAEV-9cab7b/arms')
ARCH = REPO/'experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-m3class'
raw = json.loads((REPO/'experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-9cab7b/raw-result.json').read_text())['comparison']
def tup(m):
    return (m.get('s4_support'), m.get('singular_locus_dim'), m.get('singular_locus_degree'), m.get('singular_locus_is_unit_ideal'))
# archived records keyed (set, index, role)
arch = {}
for set_name, fname in (('control', 'control-set-invariants.json'), ('class', 'per-curve-invariants.json')):
    doc = json.loads((ARCH/fname).read_text())
    assert doc['p'] == 4001
    for i, c in enumerate(doc['curves']):
        arch[(set_name, i, 'base')] = ((c['a'], c['b']), c['m4'])
        arch[(set_name, i, 'gauge')] = ((c['gauge']['a2'], c['gauge']['b2']), c['gauge']['m4'])
arms = {}
for arm in ('legacy', 'repaired'):
    recs = json.loads((X/arm/'m4-records.json').read_text())
    assert recs['p'] == 4001
    arms[arm] = {(r['set'], r['index'], r['role']): ((r['a'], r['b']), r['m4']) for r in recs['records']}
def summarize(R):
    out = {'n_records': len(R)}
    for s in ('control', 'class'):
        sub = {k: v for k, v in R.items() if k[0] == s}
        out[f'{s}_s4_support_counts'] = dict(sorted(Counter(str(m['s4_support']) for _, m in sub.values()).items()))
        out[f'{s}_singular_locus_dim_degree_counts'] = dict(Counter(f"{m['singular_locus_dim']}/{m['singular_locus_degree']}" for _, m in sub.values()))
        out[f'{s}_unit_ideal_count'] = sum(bool(m['singular_locus_is_unit_ideal']) for _, m in sub.values())
    out['n_error'] = sum(1 for _, m in R.values() if m.get('returncode') != 0 or m.get('timeout'))
    pairs = [(R[(s, i, 'base')][1], R[(s, i, 'gauge')][1]) for (s, i, r) in R if r == 'base']
    out['gauge_m4_pairs'] = len(pairs); out['gauge_m4_agree'] = sum(tup(b) == tup(g) for b, g in pairs)
    tc = {tup(m) for (s, _, _), (_, m) in R.items() if s == 'class'}
    tk = {tup(m) for (s, _, _), (_, m) in R.items() if s == 'control'}
    out['class_m4_tuple_distinct'] = len(tc)
    out['class_and_control_m4_tuple_sets_equal'] = tc == tk
    out['_s4_values'] = sorted({m['s4_support'] for _, m in R.values()})
    out['_sl_values'] = sorted({f"{m['singular_locus_dim']}/{m['singular_locus_degree']}" for _, m in R.values()})
    out['max_wall_seconds'] = max(m['wall_seconds'] for _, m in R.values())
    return out
S = {'archived': summarize(arch), 'legacy': summarize(arms['legacy']), 'repaired': summarize(arms['repaired'])}
for k, v in S.items():
    mismatch = {f: (v[f], raw[k][f]) for f in raw[k] if v.get(f) != raw[k][f]}
    print(k, 'my summary == raw-result comparison[%s]:' % k, not mismatch, mismatch if mismatch else '', 's4 values', v['_s4_values'], 'SL', v['_sl_values'])
    cf = raw['conclusion_fields'][k]
    print('   conclusion_fields match:', cf['m4_s4_support_values'] == v['_s4_values'], cf['m4_singular_locus_dim_degree_values'] == v['_sl_values'],
          cf['gauge_m4_all_agree'] == (v['gauge_m4_agree'] == v['gauge_m4_pairs']), cf['class_and_control_m4_tuple_sets_equal'] == v['class_and_control_m4_tuple_sets_equal'])
# CTRL-LEGACY-REPRO, independently: same keys, same (a,b), equal tuples
keys_same = set(arch) == set(arms['legacy']) == set(arms['repaired'])
ab_same = all(arch[k][0] == arms['legacy'][k][0] == arms['repaired'][k][0] for k in arch)
eq = sum(tup(arch[k][1]) == tup(arms['legacy'][k][1]) for k in arch)
diff_rl = sum(tup(arms['repaired'][k][1]) != tup(arms['legacy'][k][1]) for k in arch)
nonnull = sum(all(x is not None for x in tup(arch[k][1])) for k in arch)
print('keys identical', keys_same, 'curves identical', ab_same, 'legacy==archive tuples', f'{eq}/{len(arch)}', 'non-null archived tuples', nonnull,
      'raw says', raw['ctrl_legacy_repro'], '| repaired!=legacy records', diff_rl, 'raw says', raw['records_differing_repaired_vs_legacy'])
k0 = ('control', 0, 'base')
print('first control curve', arch[k0][0], 'archived', tup(arch[k0][1]), 'legacy', tup(arms['legacy'][k0][1]), 'repaired', tup(arms['repaired'][k0][1]))
k1 = ('control', 0, 'gauge'); print('its gauge twin', arch[k1][0], 'repaired', tup(arms['repaired'][k1][1]))
for want in (391, 210, 225):
    for k, (ab, m) in sorted(arms['repaired' if want == 391 else 'legacy'].items()):
        if m['s4_support'] == want:
            print(f'first record with {"repaired" if want==391 else "legacy"} s4_support={want}:', k, ab, 'archived', tup(arch[k][1]), 'legacy', tup(arms['legacy'][k][1]), 'repaired', tup(arms['repaired'][k][1])); break
```

### A6 `fib_extract.py` (sha256 f56aba9c50b51fe2)

```python
import json, statistics, sys
from collections import Counter
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
CELLS = {'fib-004': ('RUN-SEMAEV-3e69b6', 'RUN-FIB-004'), 'fib-005': ('RUN-SEMAEV-4be606', 'RUN-FIB-005')}
def load(path): return json.loads(Path(path).read_text())['per_curve']
def summ(pc):
    ms = pc['measurements']
    ok = [m for m in ms if not m['capped'] and m['worker_error'] is None]
    return {'n_measured': len(ms), 'n_capped': sum(bool(m['capped']) for m in ms), 'n_solved': len(ok),
            'n_trivial_ideal': sum(bool(m['is_trivial_ideal']) for m in ms),
            'basis_size_counts': dict(sorted(Counter(str(m['groebner_basis_size']) for m in ok).items())),
            'basis_max_degree_counts': dict(sorted(Counter(str(m['groebner_basis_max_degree']) for m in ok).items())),
            'median_cost_seconds': statistics.median(m['cost_seconds'] for m in ms) if ms else None,
            'resource_exhaustion': pc['resource_exhaustion'], 'stop_reason': pc['stop_reason'],
            '_header_n_measured': pc['n_measured'], '_header_n_capped': pc['n_capped'],
            '_worker_errors': sum(m['worker_error'] is not None for m in ms)}
pt = lambda m: (bool(m['capped']), m['groebner_basis_size'], m['groebner_basis_max_degree'], bool(m['is_trivial_ideal']))
for cell, (rid, frun) in CELLS.items():
    raw = json.loads((REPO/'experiments/EXP-SEMAEV-93d5cc/runs'/rid/'raw-result.json').read_text())['comparison']
    src = {'archived': load(REPO/'experiments/EXP-FIB-001/runs'/frun/'raw.json'),
           'legacy': load(X/rid/'arms/legacy/runs'/frun/'raw.json'),
           'repaired': load(X/rid/'arms/repaired/runs'/frun/'raw.json')}
    for k, pcs in src.items():
        for cid, pc in pcs.items():
            s = summ(pc); r = raw[k][cid]
            mism = {f: (s[f], r[f]) for f in r if (abs(s[f] - r[f]) > 1e-12 if isinstance(r[f], float) else s[f] != r[f])}
            allcap = s['n_measured'] > 0 and s['n_capped'] == s['n_measured']
            cf = raw['conclusion_fields'][k][cid]
            print(f"{cell} {k:8s} {cid}: mine==raw {not mism} {mism if mism else ''} header_consistent={s['_header_n_measured']==s['n_measured'] and s['_header_n_capped']==s['n_capped']} worker_errors={s['_worker_errors']} "
                  f"n_meas={s['n_measured']} n_cap={s['n_capped']} | conclusion all_capped={allcap} RE={s['resource_exhaustion']} raw_cf={cf} match={cf=={'all_measured_capped': allcap, 'resource_exhaustion': s['resource_exhaustion']}}")
    # legacy control rebuilt per target
    for cid in src['archived']:
        A = {m['target_index']: m for m in src['archived'][cid]['measurements']}
        L = {m['target_index']: m for m in src['legacy'][cid]['measurements']}
        common = sorted(set(A) & set(L))
        neq = [t for t in common if pt(A[t]) != pt(L[t])]
        allcapA = all(m['capped'] for m in A.values()); allcapL = all(m['capped'] for m in L.values())
        chk = {'n_common': len(common), 'per_target_equal_on_common': not neq, 'n_measured_diff': len(L) - len(A),
               'resource_exhaustion_equal': src['archived'][cid]['resource_exhaustion'] == src['legacy'][cid]['resource_exhaustion'],
               'all_capped_pattern_equal': allcapA == allcapL}
        chk['pass'] = chk['per_target_equal_on_common'] and abs(chk['n_measured_diff']) <= 2 and chk['resource_exhaustion_equal'] and chk['all_capped_pattern_equal'] and chk['n_common'] > 0
        r = raw['ctrl_legacy_repro']['checks'][cid]
        print(f"{cell} CTRL {cid}: mine={chk} raw==mine {all(r[k]==v for k,v in chk.items())} common targets {common[:3]}..{common[-3:]}")
    print(f"{cell} CTRL overall raw pass={raw['ctrl_legacy_repro']['pass']}")
    # hand sample: first 5 C16-1 / C20-1 targets, archived vs legacy vs repaired (capped, size, maxdeg, trivial)
    cid = sorted(src['archived'])[0]
    for t in range(5):
        row = [pt({m['target_index']: m for m in src[k][cid]['measurements']}[t]) for k in ('archived', 'legacy', 'repaired')]
        print(f"   {cid} target {t}: archived {row[0]} legacy {row[1]} repaired {row[2]}")
```

### A7 `fibdec_extract.py` (sha256 3394ffadb11d6277)

```python
import json, math
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
FIB = REPO/'experiments/EXP-FIB-001/runs'
raw = json.loads((REPO/'experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-894e27/raw-result.json').read_text())['comparison']
def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j+1]] == v[o[i]]: j += 1
        for k in range(i, j+1): r[o[k]] = (i + j)/2 + 1
        i = j + 1
    return r
def pearson(a, b):
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    num = sum((x-ma)*(y-mb) for x, y in zip(a, b)); den = math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    return num/den
r2 = json.loads((FIB/'RUN-FIB-002/raw.json').read_text())['per_curve']
r3 = json.loads((FIB/'RUN-FIB-003/raw.json').read_text())['per_curve']
r7 = json.loads((FIB/'RUN-FIB-007/raw.json').read_text())['per_curve']
nR = {**{c: d['n_R_per_target'] for c, d in r2.items()}, **{c: [round(e['estimate']) for e in d['n_R_estimates']] for c, d in r3.items()}}
src = {'archived': (FIB/'RUN-FIB-004/raw.json', FIB/'RUN-FIB-005/raw.json'),
       'legacy': (X/'RUN-SEMAEV-3e69b6/arms/legacy/runs/RUN-FIB-004/raw.json', X/'RUN-SEMAEV-4be606/arms/legacy/runs/RUN-FIB-005/raw.json'),
       'repaired': (X/'RUN-SEMAEV-3e69b6/arms/repaired/runs/RUN-FIB-004/raw.json', X/'RUN-SEMAEV-4be606/arms/repaired/runs/RUN-FIB-005/raw.json')}
for k, (p4, p5) in src.items():
    pc = {**json.loads(p4.read_text())['per_curve'], **json.loads(p5.read_text())['per_curve']}
    status = {c: ('measured' if len(d['measurements']) >= 100 else 'resource_exhaustion') for c, d in pc.items()}
    ms = pc['C16-1']['measurements']
    rho = pearson(ranks([nR['C16-1'][m['target_index']] for m in ms]), ranks([m['cost_seconds'] for m in ms]))
    ratios = {}
    for c, d in r7.items():
        cs = sorted(m['cost_seconds'] for m in pc[c]['measurements']); ratios[c] = d['amortized_predictor_seconds_per_target'] / cs[len(cs)//2]
    rec = raw[k]; arm_rho = rec['per_curve_correlation']['C16-1']['rho_s']; arm_p = rec['per_curve_correlation']['C16-1']['p_value']
    gate_curves = [c for c in pc if status[c] == 'measured' and abs(rec['per_curve_correlation'].get(c, {}).get('rho_s', 0)) >= 0.4 and rec['per_curve_correlation'].get(c, {}).get('p_value', 1) < 0.01]
    cost_gate = [c for c, r in ratios.items() if r <= 0.1]
    corr_overall = len(gate_curves) >= 3; cost_pass = len(cost_gate) >= 3; gate = corr_overall and cost_pass
    print(f"{k:8s} my rho_s(C16-1)={rho:.15f} recorded={arm_rho:.15f} |diff|={abs(rho-arm_rho):.1e} p_recorded={arm_p} "
          f"status_ok={status==rec['per_curve_status']} ratios_ok={all(abs(ratios[c]-rec['predictor_cost_ratios'][c])<1e-18 for c in ratios)} "
          f"gate_curves={gate_curves} (rec {rec['correlation_gate_curves_passing']}) corr_overall={corr_overall} (rec {rec['correlation_gate_pass_overall']}) "
          f"cost_gate={cost_gate==rec['cost_gate_curves']} cost_pass={cost_pass} (rec {rec['predictor_cost_gate_pass']}) gate={gate} (rec {rec['gate_pass']}) "
          f"fib008={'would_run' if gate else 'cancelled_by_gate'} (rec {rec['run_fib_008_outcome']})")
# archived values in compare 'archived' vs the archived RUN-FIB-006C / 008 files directly
a6 = json.loads((FIB/'RUN-FIB-006C/raw.json').read_text())['per_curve']; s6 = json.loads((FIB/'RUN-FIB-006C/summary.json').read_text())
s8 = json.loads((FIB/'RUN-FIB-008/summary.json').read_text())
A = raw['archived']
print('archived from RUN-FIB-006C: rho_s', a6['C16-1']['correlation']['rho_s'] == A['per_curve_correlation']['C16-1']['rho_s'],
      'p', a6['C16-1']['correlation']['p_value'] == A['per_curve_correlation']['C16-1']['p_value'],
      'curves_passing', s6['correlation_gate_curves_passing'] == A['correlation_gate_curves_passing'],
      'overall', s6['correlation_gate_pass_overall'] == A['correlation_gate_pass_overall'], 'status', s6['per_curve_status'] == A['per_curve_status'],
      'label_shuffle', s6['CTRL-LABEL-SHUFFLE_pass'] == A['CTRL-LABEL-SHUFFLE_pass'])
print('RUN-FIB-008 summary:', s8)
# arm decision.json vs comparison and vs arm's own RUN-FIB-006C summary
for arm in ('legacy', 'repaired'):
    dj = json.loads((X/'RUN-SEMAEV-894e27/arms'/arm/'decision.json').read_text())
    s = json.loads((X/'RUN-SEMAEV-894e27/arms'/arm/'runs/RUN-FIB-006C/summary.json').read_text())
    r6 = json.loads((X/'RUN-SEMAEV-894e27/arms'/arm/'runs/RUN-FIB-006C/raw.json').read_text())['per_curve']
    print(arm, 'decision.json fields == comparison:', all(dj[f] == raw[arm][f] for f in dj), '| 006C summary status/curves/overall ==', s['per_curve_status'] == raw[arm]['per_curve_status'],
          s['correlation_gate_curves_passing'] == raw[arm]['correlation_gate_curves_passing'], s['correlation_gate_pass_overall'] == raw[arm]['correlation_gate_pass_overall'],
          '| arm 006C rho_s == comparison', r6['C16-1']['correlation']['rho_s'] == raw[arm]['per_curve_correlation']['C16-1']['rho_s'])
```

### A8 `mtic_extract.py` (sha256 aef2204925e92f2a)

```python
import json, statistics
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
CELLS = {'mtic-007': ('RUN-SEMAEV-2a8498', 'RUN-MTIC-007'), 'mtic-008': ('RUN-SEMAEV-fcd67c', 'RUN-MTIC-008')}
tup = lambda r: (r['a'], r['b'], bool(r['capped']), r['basis_size'], r['basis_max_degree'], r['trivial_ideal'], r['aux_decomposition_found'])
for cell, (rid, mrun) in CELLS.items():
    raw = json.loads((REPO/'experiments/EXP-SEMAEV-93d5cc/runs'/rid/'raw-result.json').read_text())['comparison']
    src = {'archived': REPO/'experiments/EXP-MTIC-001/runs'/mrun/'raw.json',
           'legacy': X/rid/'arms/legacy/out-root/runs'/mrun/'raw.json', 'repaired': X/rid/'arms/repaired/out-root/runs'/mrun/'raw.json'}
    D = {k: json.loads(p.read_text()) for k, p in src.items()}
    for k, d in D.items():
        for bits, pts in d['raw']['per_target'].items():
            inst = d['metrics']['instances'][bits]
            charged = [r['charged_seconds'] for r in pts]; unc = [r['charged_seconds'] for r in pts if not r['capped']]
            mine = {'n_targets': inst['n_targets'], 'n_attempted': len(pts), 'n_capped': sum(r['capped'] for r in pts),
                    'n_uncapped': sum(not r['capped'] for r in pts), 'n_trivial_ideal': sum(r['trivial_ideal'] is True for r in pts),
                    'n_aux_decomposition_found': sum(bool(r['aux_decomposition_found']) for r in pts),
                    'n_cancelled_by_budget': inst['n_targets'] - len(pts),
                    'ideal_enumeration_disagreements': inst['ideal_enumeration_disagreements'],
                    't_desc_median_seconds': statistics.median(charged) if charged else None,
                    't_desc_uncapped_median_seconds': statistics.median(unc) if unc else None}
            r = raw[k][bits]
            mism = {f: (mine[f], r[f]) for f in r if mine[f] != r[f]}
            hdr = (inst['n_attempted'] == len(pts), inst['n_capped'] == mine['n_capped'], inst['n_cancelled_by_budget'] == mine['n_cancelled_by_budget'], len(inst['cancelled_indices']) == mine['n_cancelled_by_budget'])
            cf = {'all_attempted_capped': mine['n_attempted'] > 0 and mine['n_capped'] == mine['n_attempted'], 't_desc_median_at_cap': mine['t_desc_median_seconds'] == 60.0}
            print(f"{cell} {k:8s} {bits}b: mine==raw {not mism} {mism or ''} header_consistent={all(hdr)} conclusion {cf} == raw {cf == raw['conclusion_fields'][k][bits]} "
                  f"max_seconds_observed={max(r_['seconds'] for r_ in pts):.2f} charged_set={sorted(set(charged))}")
    for bits in D['archived']['raw']['per_target']:
        A = {r['index']: r for r in D['archived']['raw']['per_target'][bits]}; L = {r['index']: r for r in D['legacy']['raw']['per_target'][bits]}
        P = {r['index']: r for r in D['repaired']['raw']['per_target'][bits]}
        common = sorted(set(A) & set(L)); neq = [i for i in common if tup(A[i]) != tup(L[i])]
        chk = {'n_common': len(common), 'per_target_equal_on_common': not neq, 'n_attempted_diff': len(L) - len(A),
               'uncapped_equal': sum(not r['capped'] for r in A.values()) == sum(not r['capped'] for r in L.values())}
        chk['pass'] = chk['per_target_equal_on_common'] and abs(chk['n_attempted_diff']) <= 2 and chk['uncapped_equal'] and chk['n_common'] > 0
        rr = raw['ctrl_legacy_repro']['checks'][bits]
        same_targets = [i for i in common if (A[i]['a'], A[i]['b']) == (L[i]['a'], L[i]['b']) == (P[i]['a'], P[i]['b'])]
        print(f"{cell} CTRL {bits}b: mine {chk} == raw {all(rr[f] == v for f, v in chk.items())}; attempted index sets equal (arch/leg/rep) {set(A)==set(L)==set(P)}; same (a,b) per index {len(same_targets)}/{len(common)}; "
              f"basis fields on capped targets: {sorted({(r['basis_size'], r['basis_max_degree'], r['trivial_ideal']) for r in list(A.values())+list(L.values())+list(P.values())})}")
        i0 = common[0]
        print(f"   hand row index {i0}: archived {tup(A[i0])} legacy {tup(L[i0])} repaired {tup(P[i0])}")
```

### A8b `mtic010b_extract.py` (sha256 16e20a77a142d3d9)

```python
import json
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x/RUN-SEMAEV-0e5876/arms')
raw = json.loads((REPO/'experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876/raw-result.json').read_text())['comparison']
src = {'archived': REPO/'experiments/EXP-MTIC-001/runs/RUN-MTIC-010b/raw.json',
       'legacy': X/'legacy/out-root/runs/RUN-MTIC-010b/raw.json', 'repaired': X/'repaired/out-root/runs/RUN-MTIC-010b/raw.json'}
for k, p in src.items():
    d = json.loads(p.read_text()); m = d['metrics']
    bad = []
    print(f"{k}: status={d['status']} valid={d['validity']} upstream_missing_or_invalid={m['upstream_missing_or_invalid']} deviations={len(d['protocol_deviations'])} anomalies={len(d['anomalies'])}")
    for bits, dm in m['decision_matrix'].items():
        K = {a: dm['accountings'][a]['K_star'] for a in ('group_ops_rho', 'group_ops_bsgs', 'wall_seconds')}
        reg = dm['regime_per_accounting']
        # independent re-derivation: K* infinite iff T_desc >= sqrt_n in that accounting (regime (i))
        rederive = {a: (dm['accountings'][a]['T_desc'] >= dm['accountings'][a]['sqrt_n']) == (K[a] == 'infinite') == dm['accountings'][a]['regime_i_t_desc_geq_sqrt_n'] for a in K}
        r = raw[k]['decision_matrix'][bits]
        mine = {'K_star_per_accounting': K, 'regime_per_accounting': reg, 'n_uncensored_solves': dm['n_uncensored_solves'],
                't_desc_n_attempted': dm['t_desc_n_attempted'], 't_desc_n_capped': dm['t_desc_n_capped'], 't_desc_seconds_median': dm['t_desc_seconds_median'],
                'below_frontier_observed_any_accounting': dm['below_frontier_observed_any_accounting']}
        ok = all(mine[f] == r[f] for f in r)
        cf = raw['conclusion_fields'][k]
        print(f"   {bits}b K*={K} regime={sorted(set(reg.values()))} n_unc={dm['n_uncensored_solves']} att/cap={dm['t_desc_n_attempted']}/{dm['t_desc_n_capped']} "
              f"T_desc/sqrt_n(rho)={dm['accountings']['group_ops_rho']['T_desc']:.3g}/{dm['accountings']['group_ops_rho']['sqrt_n']:.4g} rederive_ok={all(rederive.values())} "
              f"mine==raw {ok} conclusion K*,regime match {cf['K_star.'+bits] == K and cf['regime.'+bits] == reg}")
    for name, ab in m['ablation'].items():
        r = raw[k]['ablation'][name]
        mine = {f: ab[f] for f in ('B', 'K_star_per_accounting', 't_desc_median_seconds', 't_desc_n_attempted', 't_desc_n_capped')}
        print(f"   ablation {name}: B={ab['B']} K*={ab['K_star_per_accounting']} att/cap={ab['t_desc_n_attempted']}/{ab['t_desc_n_capped']} mine==raw {mine == r} "
              f"conclusion match {raw['conclusion_fields'][k]['ablation_K_star.'+name] == ab['K_star_per_accounting']}")
# upstream consumed by each arm: does the arm's 010b decision matrix T_desc counts equal its own 007/008 raw?
for arm in ('legacy', 'repaired'):
    d = json.loads((X/arm/'out-root/runs/RUN-MTIC-010b/raw.json').read_text())['metrics']['decision_matrix']
    u7 = json.loads((X/arm/'out-root/runs/RUN-MTIC-007/raw.json').read_text())['metrics']['instances']
    u8 = json.loads((X/arm/'out-root/runs/RUN-MTIC-008/raw.json').read_text())['metrics']['instances']
    print(arm, 'decision_matrix counts == own upstream copies:', all(d[b]['t_desc_n_attempted'] == u[b]['n_attempted'] and d[b]['t_desc_n_capped'] == u[b]['n_capped'] for b, u in (('16', u7), ('20', u8), ('24', u8))))
```

### A9 `deps_check.py` (sha256 4cdc1d00e41c613a)

```python
import json, hashlib
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
R93 = REPO/'experiments/EXP-SEMAEV-93d5cc/runs'
def members(rid): return json.loads((R93/rid/'arms-manifest.json').read_text())['members']
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan_in = json.loads((REPO/'experiments/EXP-SEMAEV-93d5cc/trial-plan.json').read_text())['input_sha256']
CASES = {
 'fib-decision RUN-SEMAEV-894e27': ('RUN-SEMAEV-894e27', {'RUN-FIB-004': ('RUN-SEMAEV-3e69b6', 'arms/{arm}/runs/RUN-FIB-004/raw.json'),
                                                          'RUN-FIB-005': ('RUN-SEMAEV-4be606', 'arms/{arm}/runs/RUN-FIB-005/raw.json')}),
 'mtic-010b RUN-SEMAEV-0e5876': ('RUN-SEMAEV-0e5876', {'RUN-MTIC-007': ('RUN-SEMAEV-2a8498', 'arms/{arm}/out-root/runs/RUN-MTIC-007/raw.json'),
                                                     'RUN-MTIC-008': ('RUN-SEMAEV-fcd67c', 'arms/{arm}/out-root/runs/RUN-MTIC-008/raw.json')}),
}
for label, (rid, deps) in CASES.items():
    print('==', label)
    for arm in ('legacy', 'repaired'):
        other = 'repaired' if arm == 'legacy' else 'legacy'
        ledger = json.loads((X/rid/'arms'/arm/'inputs.json').read_text())
        for dst, rec in sorted(ledger.items()):
            src = rec['source']; h = rec['sha256']
            hit = None
            for drun_id, (drid, pat) in deps.items():
                if drun_id in dst:
                    own = members(drid)[pat.format(arm=arm)]; oth = members(drid)[pat.format(arm=other)]
                    hit = f"dep {drid}: own-arm member match={h==own} other-arm member match={h==oth} (own!=other: {own!=oth})"
            if hit is None:
                rel = src.split('crypto-autoresearcher/')[-1]
                pin = plan_in.get(rel)
                hit = f"archived input: plan pin match={h==pin if pin else 'unpinned'} disk match={h==sha(REPO/rel)}"
            # also verify the bytes actually in this run's archive
            member = 'arms/' + arm + dst.split('/arms/' + arm, 1)[1]
            in_tar = sha(X/rid/member) == h if (X/rid/member).exists() else 'not archived'
            print(f"  {arm:8s} {member}  src={src.split('crypto-autoresearcher/')[-1]}  {hit}  tar-bytes match={in_tar}")
```

### A10 `ptm.py` (sha256 0a5b65e3d29b611b)

```python
import json, shutil, sys
from pathlib import Path
IMPL = '/home/user/crypto-autoresearcher/experiments/EXP-SEMAEV-93d5cc/implementation'
sys.path.insert(0, IMPL)
import compare  # producer's extraction, used only for the proves-too-much object (read-only)
X = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/x')
P = Path('/tmp/claude-0/-home-user-crypto-autoresearcher/09f358a3-30a1-54bd-aad0-b5484a52918d/scratchpad/ptm')
RUNS = {'RUN-SEMAEV-9cab7b': 'icinv-m4', 'RUN-SEMAEV-3e69b6': 'fib-004', 'RUN-SEMAEV-4be606': 'fib-005', 'RUN-SEMAEV-894e27': 'fib-decision',
        'RUN-SEMAEV-2a8498': 'mtic-007', 'RUN-SEMAEV-fcd67c': 'mtic-008', 'RUN-SEMAEV-0e5876': 'mtic-010b'}
OBJ = {'LL': ('legacy', 'legacy'), 'RR': ('repaired', 'repaired'), 'SWAP': ('repaired', 'legacy'), 'REAL': ('legacy', 'repaired')}
REPO = Path('/home/user/crypto-autoresearcher')
for rid, cell in RUNS.items():
    exp = 'EXP-SEMAEV-6e9dcf' if rid == 'RUN-SEMAEV-0e5876' else 'EXP-SEMAEV-93d5cc'
    recorded = json.loads((REPO/'experiments'/exp/'runs'/rid/'raw-result.json').read_text())['comparison']
    for name, (in_leg_slot, in_rep_slot) in OBJ.items():
        d = P/name/rid
        shutil.copytree(X/rid/'arms'/in_leg_slot, d/'arms'/'legacy')
        shutil.copytree(X/rid/'arms'/in_rep_slot, d/'arms'/'repaired')
        c = json.loads(json.dumps(compare.compare(cell, d), sort_keys=True, default=str))
        ch_l = sorted(k for k, v in c['conclusion_changed_repaired_vs_legacy'].items() if v)
        ch_a = sorted(k for k, v in c['conclusion_changed_repaired_vs_archived'].items() if v)
        extra = f" records_differing={c['records_differing_repaired_vs_legacy']}" if cell == 'icinv-m4' else ''
        same = (c == recorded) if name == 'REAL' else ''
        print(f"{cell:12s} {name:4s} slots(leg<-{in_leg_slot}, rep<-{in_rep_slot}) changed_rep_vs_leg={ch_l or 'none'} changed_rep_vs_arch={ch_a or 'none'} "
              f"ctrl_pass={c['ctrl_legacy_repro']['pass']}{extra}{' REAL==recorded: '+str(same) if name=='REAL' else ''}")
```

### A11 `interrupted.py` (sha256 33595d2ef90a38d8)

```python
import json, hashlib
from pathlib import Path
REPO = Path('/home/user/crypto-autoresearcher')
R93 = REPO/'experiments/EXP-SEMAEV-93d5cc/runs'
DEP = {'mtic-007': 'RUN-SEMAEV-2a8498', 'mtic-008': 'RUN-SEMAEV-fcd67c'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for d in (R93/'RUN-SEMAEV-500a81', REPO/'experiments/EXP-SEMAEV-88c46c/runs/RUN-SEMAEV-980e8c'):
    print('==', d.relative_to(REPO))
    for cell, rid in DEP.items():
        man = json.loads((R93/rid/'arms-manifest.json').read_text())['members']
        root = d/'deps'/cell
        files = sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
        same = files == sorted(man) and all(sha(root/k) == v for k, v in man.items())
        print(f'  deps/{cell}: {len(files)} files, identical set+bytes to {rid} arms-manifest: {same}')
    arms_files = sorted(str(p.relative_to(d)) for p in (d/'arms').rglob('*') if p.is_file())
    print('  arms/ files:', len(arms_files), '| any RUN-MTIC-010b path:', [f for f in arms_files if '010b' in f], '| any arm-result.json:', [f for f in arms_files if f.endswith('arm-result.json')])
    print('  arms/ file names (dedup):', sorted({'/'.join(Path(f).parts[3:]) for f in arms_files}))
    for arm in ('legacy', 'repaired'):
        led = json.loads((d/'arms'/arm/'inputs.json').read_text()) if (d/'arms'/arm/'inputs.json').exists() else None
        print(f'  arms/{arm}/inputs.json present: {led is not None}')
    for arm in ('legacy', 'repaired'):
        log = (d/f'arm-{arm}.stdout.log').read_text().splitlines()
        print(f'  arm-{arm}.stdout.log: {len(log)} lines; last line: {log[-1][:150] if log else None}')
```

### B1 `blind_s4.py` (sha256 2fc0e1204f7ce2fc)

```python
# Blind re-derivation: S4 = Res_t(S3(x1,x2,t), S3(x3,x4,t)) for y^2 = x^3 + a x + b.
# Written from the statement only; imports nothing from the repository.
import sys, time
import sympy as sp
from sympy import Poly, GF, resultant, symbols

a_int, b_int, p = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
x1, x2, x3, x4, t, A, B = symbols('x1 x2 x3 x4 t A B')

def S3(u, v, w, a, b):
    return ((u - v)**2 * w**2
            - 2*((u + v)*(u*v + a) + 2*b)*w
            + ((u*v - a)**2 - 4*b*(u + v)))

print('sympy', sp.__version__)
# (i) generic S4 over Z[A,B], then specialise and reduce mod p
t0 = time.time()
S4gen = sp.expand(resultant(S3(x1, x2, t, A, B), S3(x3, x4, t, A, B), t))
print('generic S4: terms over Z[A,B] =', len(sp.Add.make_args(S4gen)),
      'free =', sorted(map(str, S4gen.free_symbols)), 'secs %.1f' % (time.time() - t0))
S4num = sp.expand(S4gen.subs({A: a_int, B: b_int}, simultaneous=True))
P = Poly(S4num, x1, x2, x3, x4, modulus=p)
print('exact S4 mod p: nterms =', len(P.terms()), 'total_degree =', P.total_degree(),
      'free =', sorted(str(g) for g in P.free_symbols_in_domain | P.free_symbols) if False else sorted(str(g) for g, d in zip(P.gens, P.degree_list()) if d > 0),
      'degree_list =', P.degree_list())
# (ii) resultant computed directly over GF(p) as a cross-check
Pa = Poly(S3(x1, x2, t, a_int, b_int), t, x1, x2, x3, x4, modulus=p)
Pb = Poly(S3(x3, x4, t, a_int, b_int), t, x1, x2, x3, x4, modulus=p)
R = Poly(resultant(Pa.as_expr(), Pb.as_expr(), t), x1, x2, x3, x4, modulus=p)
print('direct GF(p) resultant: nterms =', len(R.terms()), 'equal to (i):', R == P)
# symmetry sanity: S4 symmetric under x1<->x2, x3<->x4, (x1,x2)<->(x3,x4)
sw = lambda e, m: sp.expand(e.subs(m, simultaneous=True))
e = P.as_expr()
for m in [{x1: x2, x2: x1}, {x3: x4, x4: x3}, {x1: x3, x3: x1, x2: x4, x4: x2}]:
    print('symmetric under', m, Poly(sw(e, m), x1, x2, x3, x4, modulus=p) == P)
# vanishing check: S4(P1,P2,P3,P4)=0 when P1+P2+P3+P4=O; find points on the curve mod p
pts = []
for X in range(p):
    r = (X**3 + a_int*X + b_int) % p
    if r == 0:
        pts.append((X, 0)); continue
    if pow(r, (p - 1)//2, p) == 1:
        Y = sp.sqrt_mod(r, p); pts.append((X, Y))
    if len(pts) > 40: break
def add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    (X1, Y1), (X2, Y2) = P1, P2
    if X1 == X2 and (Y1 + Y2) % p == 0: return None
    if P1 == P2: l = (3*X1*X1 + a_int) * pow(2*Y1, -1, p) % p
    else: l = (Y2 - Y1) * pow(X2 - X1, -1, p) % p
    X3 = (l*l - X1 - X2) % p
    return (X3, (l*(X1 - X3) - Y1) % p)
neg = lambda Q: (Q[0], (-Q[1]) % p)
ok = 0; tried = 0
for i in range(0, 12):
    Pp, Qq, Rr = pts[i], pts[i + 13], pts[i + 26]
    S = add(add(Pp, Qq), Rr)
    if S is None: continue
    Ww = neg(S); tried += 1
    v = P.eval({x1: Pp[0], x2: Qq[0], x3: Rr[0], x4: Ww[0]}) % p
    ok += (v == 0)
print('S4 vanishes on P1+P2+P3+P4=O for', ok, 'of', tried, 'quadruples')
# (iii) the sequential substitution defect: from S3(x1,x2,x3) map x1->x3, x2->x4, x3->t one at a time
base = S3(x1, x2, x3, a_int, b_int)
seq = base
for old, new in [(x1, x3), (x2, x4), (x3, t)]:
    seq = seq.subs(old, new)
sim = base.subs({x1: x3, x2: x4, x3: t}, simultaneous=True)
dict_default = base.subs({x1: x3, x2: x4, x3: t})
print('sequential  S3 image:', sp.factor(sp.expand(seq - S3(t, x4, t, a_int, b_int))) == 0 and 'equals S3(t,x4,t)', 'free =', sorted(map(str, seq.free_symbols)))
print('simultaneous S3 image equals S3(x3,x4,t):', sp.expand(sim - S3(x3, x4, t, a_int, b_int)) == 0, 'free =', sorted(map(str, sim.free_symbols)))
print('sympy subs(dict) default equals sequential:', sp.expand(dict_default - seq) == 0)
L = Poly(resultant(S3(x1, x2, t, a_int, b_int), seq, t), x1, x2, x3, x4, modulus=p)
print('legacy-shaped Res_t(S3(x1,x2,t), S3(t,x4,t)) mod p: nterms =', len(L.terms()),
      'total_degree =', L.total_degree(), 'degree_list =', L.degree_list(),
      'free =', sorted(str(g) for g, d in zip(L.gens, L.degree_list()) if d > 0))
```

### B2 `blind_s4_multi.py` (sha256 60511fe75ad21384)

```python
# Blind S4 term counts for several (a,b,p); repository-independent.
import sys
import sympy as sp
from sympy import Poly, resultant, symbols
x1, x2, x3, x4, t, A, B = symbols('x1 x2 x3 x4 t A B')
def S3(u, v, w, a, b):
    return (u - v)**2*w**2 - 2*((u + v)*(u*v + a) + 2*b)*w + ((u*v - a)**2 - 4*b*(u + v))
G = sp.expand(resultant(S3(x1, x2, t, A, B), S3(x3, x4, t, A, B), t))
seq = S3(x1, x2, x3, A, B)
for old, new in [(x1, x3), (x2, x4), (x3, t)]:
    seq = seq.subs(old, new)
L = sp.expand(resultant(S3(x1, x2, t, A, B), seq, t))
over_Z = lambda e, a, b: Poly(sp.expand(e.subs({A: a, B: b})), x1, x2, x3, x4)
for spec in sys.argv[1:]:
    a, b, p = map(int, spec.split(','))
    E = Poly(sp.expand(G.subs({A: a, B: b})), x1, x2, x3, x4, modulus=p)
    Lg = Poly(sp.expand(L.subs({A: a, B: b})), x1, x2, x3, x4, modulus=p)
    fs = lambda P: sorted(str(g) for g, d in zip(P.gens, P.degree_list()) if d > 0)
    line = f'(a,b,p)=({a},{b},{p}) exact: nterms_mod_p={len(E.terms())} deg={E.total_degree()} free={fs(E)} | sequential-subst: nterms_mod_p={len(Lg.terms())} deg={Lg.total_degree()} free={fs(Lg)}'
    if p == 101:
        EZ, LZ = over_Z(G, a, b), over_Z(L, a, b)
        pt = {x1: 1, x2: 3, x3: 5, x4: 41}
        line += f' | over Z: exact terms={len(EZ.terms())} deg={EZ.total_degree()} residue@(1,3,5,41)={int(EZ.eval(pt)) % 101}; sequential terms={len(LZ.terms())} deg={LZ.total_degree()} residue={int(LZ.eval(pt)) % 101}'
    print(line)
```

### B3 `blind_vanish.py` (sha256 68bffdf686644d20)

```python
import sympy as sp
from sympy import Poly, resultant, symbols, factor
x1, x2, x3, x4, t, A, B = symbols('x1 x2 x3 x4 t A B')
S3 = lambda u, v, w: (u - v)**2*w**2 - 2*((u + v)*(u*v + A) + 2*B)*w + ((u*v - A)**2 - 4*B*(u + v))
G = Poly(sp.expand(resultant(S3(x1, x2, t), S3(x3, x4, t), t)), x1, x2, x3, x4)
p = 4001
for a, b in ((441, 294), (3603, 2402)):
    vanish = [(mon, c) for mon, c in G.terms() if int(c.subs({A: a, B: b})) % p == 0]
    print(f'(a,b)=({a},{b}): {len(G.terms())} generic monomials, {len(vanish)} with coefficient = 0 mod {p}')
    facs = {}
    for mon, c in vanish:
        f = str(factor(c)); facs[f] = facs.get(f, 0) + 1
    for f, n in sorted(facs.items(), key=lambda kv: -kv[1])[:4]: print('   ', n, 'monomials with coefficient', f)
print('2*441^3 mod p =', (2*441**3) % p, '; 3*294^2 ... a^3 / b^2 mod p:', (441**3 * pow(294**2, -1, p)) % p)
```

### Inline shell commands

```bash
# check 1: fib_child tally per arm
cd experiments/EXP-SEMAEV-93d5cc/runs && for r in RUN-SEMAEV-3e69b6 RUN-SEMAEV-4be606; do for arm in legacy repaired; do
  f=$r/arm-$arm.stderr.log; grep -c '^fib_child ' $f; grep '^fib_child ' $f | sort | uniq -c; grep -v '^fib_child ' $f; done; done
# check 1: s4_expr call sites in the consumers
rg -n 's4_expr' experiments/EXP-MTIC-001/code/run_mtic.py experiments/EXP-FIB-001/driver/decompcost.py harness/exp_icinv_e0cd8f_m3class.py
# check 0: trial-plan / spec hashes against the decisions; pinned sources
sha256sum experiments/EXP-SEMAEV-{93d5cc,88c46c,6e9dcf}/trial-plan.json experiments/EXP-SEMAEV-{93d5cc,88c46c,6e9dcf}/specification.yaml \
  experiments/EXP-SEMAEV-93d5cc/implementation/vendor/semaev_legacy_53a23952.py harness/semaev.py
# check 0: archived experiment directories untouched
for p in experiments/EXP-MTIC-001 experiments/EXP-FIB-001 experiments/EXP-ICINV-e0cd8f; do
  git log --since='2026-10-18T21:00:00Z' --format='%h %ad %s' -- $p; git status --porcelain --untracked-files=all -- $p | wc -l; done
# check 0: environment.json start commit vs manifest end commit -- for each run, git show <commit>:<pinned path> | sha256sum
#   at both commits, git merge-base --is-ancestor, git diff --name-only <start> <end> restricted to pinned/implementation paths
# CTRL-REEXTRACT replay with the producer's checker (no bytecode written)
for r in experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-{9cab7b,3e69b6,4be606,894e27,2a8498,fcd67c} experiments/EXP-SEMAEV-6e9dcf/runs/RUN-SEMAEV-0e5876; do
  plan=$(echo $r | sed 's|/runs/.*|/trial-plan.json|')
  out=$(TMPDIR=<scratchpad> python3 -I -B experiments/EXP-SEMAEV-93d5cc/implementation/check.py $r $plan); echo $?
  [ "$out" = "$(cat $r/check.stdout.log)" ] && echo equal; done
# check 7: top-level artifacts of the interrupted runs
for d in experiments/EXP-SEMAEV-93d5cc/runs/RUN-SEMAEV-500a81 experiments/EXP-SEMAEV-88c46c/runs/RUN-SEMAEV-980e8c; do
  for f in execution-receipt.json raw-result.json manifest.yaml arms.tar.gz arms-manifest.json check.stdout.log; do [ -e $d/$f ] && echo PRESENT $f || echo absent $f; done; done
# blind derivation
python3 -I scripts/blind_s4.py 3603 2402 4001
python3 -I scripts/blind_s4_multi.py 3603,2402,4001 370,3784,4001 441,294,4001 1509,1006,4001 2,3,101
python3 -I scripts/blind_s4_multi.py 1506,3218,4001
python3 -I scripts/blind_vanish.py
```
