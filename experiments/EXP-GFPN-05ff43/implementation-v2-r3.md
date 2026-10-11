# EXP-GFPN-05ff43 — implementation note, protocols 2-r3 and 2-a1-r3 (r3 successor stage, TASK-20260924-ed17fe)

Stage note of the r3 successor stage (maximum_runs 0; no run package). Scratch outputs live in the session scratchpad, referred to
only as `<scratchpad>`. Section 0 is the running progress log, and sections 1-16 follow the two RC-4 sections.

## 0. Progress log (UTC)

- 10:42:19Z stage start. The nine amendment files hashed before any write; all nine equal the card's `nine_hashes`
  (DEC-20260924-e52eec VA-1). 0 mismatches.
- 10:47:35Z DV-9 baseline taken before any write (454 files under the frozen roots; 5 pre-existing byte-code files;
  `runs/` 51 entries = 50 run directories + `.gitkeep`; HEAD 5505464a92ed6c78e8155615cb6cde00d3ee49ae; `git status
  --porcelain --untracked-files=all` empty). Record: `<scratchpad>/r3/dv9/baseline.json`.
- 10:48:46Z 42 run ids minted and each BARE id checked with `--check` (rc 0, 0 occurrences, 42 distinct) before any
  file named it. Logs: `<scratchpad>/r3/ids/`.
- 10:50Z the preserved r2 files re-hashed: all 15 equal the TASK-20260924-5ca2a5 preservation receipt.
- 10:50Z first repository write: `implementation-v2-r3/` created; this note opened.
- 10:59:13Z-10:59:17Z DV-3, the RC-2 semantics probe and DV-2 / DV-4 run on the delivered r3 configuration code (all
  pass; section 4). PS-1 branch: P-A.
- 11:01:16Z both r3 plans written once by `r3_make_plans.py --write` (RC-4 (c) equality asserted in the writer).
- 11:09Z DV-5 PASS; DV-10 PASS. 11:10Z DV-8 PASS.
- 11:12Z DV-6 attempt 1 FAIL (implementation defect in `r3_run_wrapper.py` R-13: it read the amendment ids at
  `repair.<key>`; the plans nest them at `repair.amendments.<key>`). Attempt 1 preserved in
  `<scratchpad>/r3/dv_attempts/dv6_attempt1_implementation_defect/`. Fix: one key path in R-13. 11:13Z DV-6 attempt 2
  PASS (deviation RD-3).
- 11:14:46Z DV-1 static, attempt 1: a harness fault only (callgrind_annotate prints its version on stderr; the probe
  captured stdout). Preserved in `<scratchpad>/r3/dv_attempts/dv1_attempt1_harness_version_on_stderr/`. 11:15:01Z
  attempt 2 complete (deviation RD-4).
- 11:18Z DV-7 attempt 1: harness fault, no SE-5 verdict. Development files were added to `implementation-v2-r3/`
  while the lineage ran. The synthetic f1fb0e phase-A receipt built at the lineage start then no longer bound the
  tree, and R-6 correctly refused world B's toy G1 before anything was written. The harness then failed while comparing
  a world-B result that did not exist. Preserved in
  `<scratchpad>/r3/dv_attempts/dv7_attempt1_harness_layer_extended_during_run/`. Fix (harness only): DV-7 stops cleanly
  when a toy G1 is refused, and DV-12 / DV-16 bind their own synthetic receipt at their start. Rule adopted from here
  on: no file of the layer and not this note is edited while a lineage check runs (deviation RD-5).
- **DV-16 toy prime, declared here before DV-16 runs (HR-9; VA-4): p' = 1021**, the DV-7 addendum-role toy rung. It is
  none of 4111, 262151, 16777291 or 1073741831. The declared forced system is the first draw of pattern (2, 2, 2),
  `run_system` tag `health_p1021_d222`, in the toy `controls-a1 --p 1021` package.
- 11:23:10Z DV-7 attempt 2 (full harness `r3_devchecks.py dv7`). Steps (1)-(2) complete. The SE-5 probe was run ONCE:
  toy G1 (fixture --p 1033) was completed_valid in world A (PYTHONHASHSEED "0") and in world B ("12345"). The **SE-5 verdict
  was PASS** (no REG-1-compared field differs), and REG-1 on a perturbed copy returned FAIL, as it must. Step (3): the toy G2
  (fixture --p 1039) ended `failed` / `implementation_error` (the frozen driver's AC-5 reading). In it, the toy raw_u and
  S3_rescaled systems kept the SSF signature (clause ii) on all six SE-3 attempts (K = 5; counters: 36 wrapped calls, 47
  attempts, 11 re-solves, 3 calls with an SSF attempt, 2 still SSF after the last attempt). R-7 then refused every later
  package, writing nothing. Step (4) crashed: the harness passed the checker an accounting path in a directory it had never
  created. Both are harness reasons (deviation RD-6). Preserved:
  `<scratchpad>/r3/dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/`.
- 11:28:50Z a stray `implementation-v2-r3/__pycache__/r3_common.cpython-311.pyc` was written by an executor inspection
  command that imported `r3_common` without `-B` (the module disables byte-code writing only after its own import). It was
  found at 11:35Z and removed (sha256 99ef27a4…3eb0d). From then on, every inspection command uses `-B` (deviation RD-7).
- 11:33:57Z DV-7 attempt 3 was a continuation harness **outside the layer** (`<scratchpad>/r3/dev/dv7_resume.py`). It
  reused the RECORDED SE-5 packages and did not re-run the probe. The toy G2 prime was declared before launch by the rule
  "smallest prime p >= 2^16 with p = 1 (mod 3)" = 65539, with no further prime to be tried. R-6 refused every launch on the
  stray pyc, writing nothing, and the continuation then crashed on an import-path defect. Preserved:
  `<scratchpad>/r3/dv_attempts/dv7_attempt3_resume_R6_refused_stray_pyc_and_a1_toy_import/`.
- 11:35:36Z DV-7 attempt 4 (the same continuation, with the path fix). Toy G2 at 65539: `failed` /
  `infrastructure_error`. Every msolve child exited with returncode -11 (SIGSEGV) on the toy systems at p = 65539, with 0
  SSF attempts. A crash is never evidence. R-7 refused the rest (38 refusals, nothing written). The checker passed on
  world A G1 and on the toy G2; on world B G1 it failed only on the declared SE-6 override. Preserved:
  `<scratchpad>/r3/dv_attempts/dv7_attempt4_resume_toyG2_65539_msolve_segv/`.
- 11:48:34Z-11:53:48Z DV-7 attempt 5 (`<scratchpad>/r3/dev/dv7_resume5.py`). This is the continuation with a
  **SYNTHETIC toy G2 gate row**, treated as G3 and G4 already are, because the real toy G2 failed at both declared toy
  primes (deviation RD-8). 20 toy packages ran through the delivered wrapper and entries:
  - world A G1 and world B G1 (recorded in attempt 2), F-4, the v2 build, six cells and the v2 aggregate;
  - controls-a1 at 1021 through the r3 a1 entry, the addendum build, six cells and the a1 aggregate.

  All 20 were completed_valid. The checker returned rc 0 on every world-A package, and on world B G1 it failed only on
  the declared SE-6 override. RC-8 phase B: verified. DV-13 PASS over all 20 packages. getrlimit read 10737418240 in
  every child, threads were 1, and the PARI stack status was command_returned. **DV-7: PASS** (section 9).
- 11:54:17Z-12:03:57Z DV-12 (cases U, a..g, through the delivered wrapper and entry with a development forcing shim):
  **PASS (a)-(g)**.
- 12:04:05Z DV-16 attempt 1: a harness defect. The shared case runner never set the in-process REG-1 reference id, so
  REG-1 looked for RUN-GFPN-ac4487 in the toy world, and the run crashed before any child. Preserved:
  `<scratchpad>/r3/dv_attempts/dv16_attempt1_harness_reg1_reference_not_set_in_process/`. Fix in `r3_dv16.py` only
  (deviation RD-10). 12:04:54Z-12:05:46Z DV-16 attempt 2 at the declared toy prime 1021: **PASS (a)-(e)**.
- 12:06Z `r3_inventory.py` (the R3S-10 consumer inventory) was copied into the layer from `<scratchpad>/r3/dev/`, where
  it had been developed and tested read-only. 12:06:01Z DV-15: **PASS** (set O 75, toy lineage 596 rows, 0
  violations). A supplementary DV-15 (b) over the 14 DV-12 / DV-16 case packages found 0 violations (report only).
- 12:07:11Z DV-11: **PASS**. Static launch list = S-1, S-2, S-3, with 0 r3 launch sites. Dynamic counts were all equal.
  R3S-10 inventory: 199 listed functions, 0 stops.
- 12:08:08Z DV-17 attempt 1: a harness defect (wrong receipt path) at start-up, before any child. Preserved (deviation
  RD-11). 12:08:42Z-12:31:47Z DV-17 attempt 2 (detached, quiet machine; 0 other
  solver processes before every launch): **PASS**. 360 calls, 0 compared-field differences, every getrlimit
  10737418240 / 10737418240, minimum spacing 2.006 s, 0 log-visible SSF indicators.
- 12:33:09Z DV-9: **PASS** (section 15). 12:33:31Z the VA-5 bundle was written and then verified (section 15). This
  note was completed afterwards. Every written file was then searched for the model, vendor and runtime names, the
  branch name and the scratch path.

## RC-4 (b): declared metadata key paths (JSON pointer), recorded before either plan was written

(Written at 10:59:57Z. At this time neither `trial-plan-v2-r3.json` nor `trial-plan-v2-a1-r3.json` exists. This
satisfies DEC-20260923-80e280 RC-4 (b), re-pointed to r3 by DEC-20260924-e52eec VA-3 and card R3S-7.)

`trial-plan-v2-r3.json` (11 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed (2 → "2-r3") | protocol label |
| `/task_id` | changed (→ TASK-20260924-4351ac) | task ids |
| `/written_by_task` | added (TASK-20260924-ed17fe) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-f1fb0e phase A (Coordinator)") | archived_by |
| `/repair` | added (the VA-1 content) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed, with the exclusion list's sha256) | gate.regression |
| `/id_map` | added (31 entries, v2 → r3) | id map |
| `/v2_ids_never_reused` | added (the 31 frozen v2 ids) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids) | never-reused lists |
| `/retired_ids` | added (used v2 ids kept as records; the 124 retired ids: 29 v2, 11 v2-a1, 42 r1, 42 r2) | retired id lists |
| `/ceiling_note` | added (2 existing + 31 + 11 = 44 of 48, over eight plans) | ceiling note |

`trial-plan-v2-a1-r3.json` (12 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed ("2-a1" → "2-a1-r3") | protocol label |
| `/task_id` | changed (→ TASK-20260924-b3e690) | task ids |
| `/written_by_task` | changed (→ TASK-20260924-ed17fe) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-f1fb0e phase A (Coordinator)") | archived_by |
| `/repair` | added (the VA-1 content, with the a1 gate re-pointing and the phase-B receipt re-pointed to TASK-20260924-f1fb0e, VC-6 (c)) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed) | gate.regression |
| `/id_map` | added (11 entries, v2-a1 → r3) | id maps |
| `/id_map_v2` | added (31 entries, v2 → r3) | id maps |
| `/frozen_v2_ids_never_reused` | added (the 31 frozen v2 ids; RC-4 (d)) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids; RC-4 (d)) | never-reused lists |
| `/retired_ids` | added (as in the v2-r3 plan) | retired id lists |
| `/ceiling_note` | added | ceiling note |

In `trial-plan-v2-a1-r3.json` the pre-existing `/v2_ids_never_reused` is NOT a declared key: it is mapped like every
other field, so its image lists the 31 r3 v2 ids (RC-4 (d)). `/gate/v2_blocking_packages`,
`/gate/addendum_blocking_package` and aggregate_a1's `driver_args` are not declared keys; they are mapped through M.
The derivation source is the FROZEN plans (trial-plan-v2.json sha256 16f33e39...4e16; trial-plan-v2-a1.json sha256
2a788720...5ac6), never the r1 or r2 plans (R3S-7).

## RC-4 (a): the union map M (42 entries), recorded before either plan was written

Assignment rule (as stages R1 and r2): ids are taken in minting order (`implementation-v2-r3/minted-run-ids.txt`;
section 16 has the allocator outputs). The first 31 go to the packages of `trial-plan-v2.json` in plan order; the next
11 to the packages of `trial-plan-v2-a1.json` in plan order. Every image was checked against all six existing plans
(frozen, r1, r2) before this table was written: 0 collisions.

id_map_v2 (31):

| order | frozen v2 id | r3 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-ac4487 | RUN-GFPN-f6a21a | F-1..F-3 fixture, n = m = 3, p' = 4111 (G1) |
| 2 | RUN-GFPN-3377f1 | RUN-GFPN-902222 | F-1..F-3 fixture, n = m = 3, p' = 16777291 (G2) |
| 3 | RUN-GFPN-76420e | RUN-GFPN-f5412a | jv_anchor_system_trace_identity, p' = 16777291, n = 5, m = 4 (G3) |
| 4 | RUN-GFPN-b231c1 | RUN-GFPN-bfe956 | frozen controls (G4) |
| 5 | RUN-GFPN-a07776 | RUN-GFPN-596fb2 | F-4 secondary fixture, n = m = 4 (NOT blocking) |
| 6 | RUN-GFPN-1ad09b | RUN-GFPN-c8f179 | build p' = 4111 |
| 7 | RUN-GFPN-0c7483 | RUN-GFPN-0983ac | cells 4111 ecgfp5_shaped m = 5 |
| 8 | RUN-GFPN-4abae0 | RUN-GFPN-0be651 | cells 4111 random_2torsion m = 5 |
| 9 | RUN-GFPN-9e4212 | RUN-GFPN-716bdf | cells 4111 random_no2torsion m = 5 |
| 10 | RUN-GFPN-bbbbe3 | RUN-GFPN-5bf619 | cells 4111 ecgfp5_shaped m = 4 |
| 11 | RUN-GFPN-a521dd | RUN-GFPN-7fc9a4 | cells 4111 random_2torsion m = 4 |
| 12 | RUN-GFPN-a07b6d | RUN-GFPN-dfe748 | cells 4111 random_no2torsion m = 4 |
| 13 | RUN-GFPN-dc1d4e | RUN-GFPN-aeccf2 | build p' = 262151 |
| 14 | RUN-GFPN-b9207c | RUN-GFPN-272a09 | cells 262151 ecgfp5_shaped m = 5 |
| 15 | RUN-GFPN-aa56bd | RUN-GFPN-2b8290 | cells 262151 random_2torsion m = 5 |
| 16 | RUN-GFPN-e5b90d | RUN-GFPN-fbbf4e | cells 262151 random_no2torsion m = 5 |
| 17 | RUN-GFPN-d2f759 | RUN-GFPN-143714 | cells 262151 ecgfp5_shaped m = 4 |
| 18 | RUN-GFPN-745cad | RUN-GFPN-671e62 | cells 262151 random_2torsion m = 4 |
| 19 | RUN-GFPN-aeff00 | RUN-GFPN-d06833 | cells 262151 random_no2torsion m = 4 |
| 20 | RUN-GFPN-3db273 | RUN-GFPN-b56ad4 | build p' = 16777291 |
| 21 | RUN-GFPN-3be8a4 | RUN-GFPN-b6b9d8 | cells 16777291 ecgfp5_shaped m = 5 |
| 22 | RUN-GFPN-00e64b | RUN-GFPN-835b83 | cells 16777291 random_2torsion m = 5 |
| 23 | RUN-GFPN-c5294d | RUN-GFPN-af5d67 | cells 16777291 random_no2torsion m = 5 |
| 24 | RUN-GFPN-36cad2 | RUN-GFPN-ef6c66 | cells 16777291 ecgfp5_shaped m = 4 |
| 25 | RUN-GFPN-11d2ad | RUN-GFPN-48ee63 | cells 16777291 random_2torsion m = 4 |
| 26 | RUN-GFPN-fc5d58 | RUN-GFPN-1280cc | cells 16777291 random_no2torsion m = 4 |
| 27 | RUN-GFPN-8f86cc | RUN-GFPN-cfe003 | aggregate (ladder table, scoring, HEUR-GFPN-DFLAT, F4, band) |
| 28 | RUN-GFPN-e26e4b | RUN-GFPN-ee0e68 | contingency 1 |
| 29 | RUN-GFPN-9da048 | RUN-GFPN-ad17db | contingency 2 |
| 30 | RUN-GFPN-59320d | RUN-GFPN-c1178d | contingency 3 |
| 31 | RUN-GFPN-1596f6 | RUN-GFPN-a6b204 | contingency 4 |

id_map_a1 (11):

| order | frozen v2-a1 id | r3 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-0d91bf | RUN-GFPN-2c4862 | controls_a1, p' = 1073741831 (BLOCKING for the addendum) |
| 2 | RUN-GFPN-8c772a | RUN-GFPN-67cdf5 | build p' = 1073741831 |
| 3 | RUN-GFPN-569fd7 | RUN-GFPN-8816e9 | cells 1073741831 ecgfp5_shaped m = 5 |
| 4 | RUN-GFPN-086463 | RUN-GFPN-8b0636 | cells 1073741831 random_2torsion m = 5 |
| 5 | RUN-GFPN-bab146 | RUN-GFPN-5e9b88 | cells 1073741831 random_no2torsion m = 5 |
| 6 | RUN-GFPN-7dd55d | RUN-GFPN-bf7c41 | cells 1073741831 ecgfp5_shaped m = 4 |
| 7 | RUN-GFPN-47aa51 | RUN-GFPN-0bc236 | cells 1073741831 random_2torsion m = 4 |
| 8 | RUN-GFPN-3a70f1 | RUN-GFPN-a379b4 | cells 1073741831 random_no2torsion m = 4 |
| 9 | RUN-GFPN-ae4918 | RUN-GFPN-9bf947 | aggregate_a1 |
| 10 | RUN-GFPN-8cfac3 | RUN-GFPN-a5e22b | contingency a1-1 |
| 11 | RUN-GFPN-6a7f35 | RUN-GFPN-3b498c | contingency a1-2 |

## 1. Stage outcome, scope and binding

- **Outcome.** Every check DV-1..DV-17 ran and is recorded. Outcomes are in section 9. No STOP condition of R3S-11 fired. **No run package
  was created** (`maximum_runs: 0`). Nothing under `runs/` was written. No tracked file was modified. No git write
  was made. A development check reports no number as a result: every D, degree and count in the scratch outputs is a
  harness value.
- **Binding.** The nine amendment files were hashed at stage start (10:42:19Z). All nine equal the card's
  `nine_hashes` (DEC-20260924-e52eec VA-1), and `r3_common.BOUND_HASHES` carries the same nine values (R-1):
  - `v1_to_v2_reanchor_and_arm_iii.yaml` e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3
  - `v2_addendum_rung31.yaml` 2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c
  - `v2_addendum_paristack.yaml` 856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7
  - `v2_addendum_seedresolve.yaml` dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81
  - `v2_addendum_solverevent.yaml` 011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f
  - `v2_addendum_healthresolve.yaml` ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d
  - `v2_addendum_launchcover.yaml` c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447
  - `v2_addendum_consumercover.yaml` a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0
  - `v2_addendum_valueclose.yaml` 877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1
- **Dispatch preconditions as found (cited, not re-derived):**
  - DP-1: HEAD 5505464a9.
  - DP-2: memory guard pid 875, kills at MemAvailable < 2,621,440 kB (above 12.0 GB), so the child cap stays at
    10737418240.
  - DP-3: lane held by the dispatcher (claim at 5505464a9, epoch 1, expiring 2026-09-25T10:41:20Z).
  - DP-4/DP-5: toolchain msolve 0.6.5-1build2, valgrind 3.22.0, callgrind_annotate-3.22.0 at /usr/bin, gp 2.15.4
    (pari-gp 2.15.4-2.1build1).
  - DP-6/DP-7: machine quiet at dispatch. It was also quiet at the DV-17 launch (12:08Z): no other msolve, valgrind,
    gp or Sage process ran, and MemAvailable was 15623272 kB.
- **Read, and nothing else under `runs/`:** RUN-GFPN-ac4487 (REG-1 reference; DV-8, DV-15, DV-17) and
  RUN-GFPN-3377f1 (the DV-3 reproduction reference).
- **Read-only inputs:**
  - the frozen trees `implementation-v2/` and `implementation-v2-a1/`;
  - the r2 files (templates only, never imported) and `implementation-v2-r1/r1_toy.py` (template for the DV-7 toy
    constructions, never imported);
  - `dev-evidence/launch-census/`, `dev-evidence/launchcover-premise/`, `dev-evidence/seedresolve-premise/`,
    `dev-evidence/solver-characterization/` and `dev-evidence/stageR1-dv7/`;
  - the goal archives' receipts.
- **Inference.**
  - `requested_policy: executor-implementation`
  - `resolved_model_id: null` (none was supplied; none is invented)
  - `fallback_used: false`
  - `bedrock_used: false`
  - Network: not used.

## 2. Files written (the exact list; for each r3 file, the r2 file and sha256 it started from, or "new")

| path | sha256 | started from |
| --- | --- | --- |
| `implementation-v2-r3/minted-run-ids.txt` | f916c8a5fb842bd9c4851409e7056bce0d8bde275b1202da87aa06e21e4312a3 | new (the 42 r3 ids, minting order) |
| `implementation-v2-r3/r3_accounting.py` | dca726f7cb35c107536ea92b1e51566b8ed1a4e1ee7a9110eac5836425757e38 | `implementation-v2-r2/r2_accounting.py` 4f8c3a72dcf602bd79a5bf1283bf970a3c6c56511cc6f086fff25f60c1416378 |
| `implementation-v2-r3/r3_check_run.py` | 939d7d7e5bc8a8c64f15df188f98f13b22ef7a9d696680f8e47854c2dbdcd14d | `implementation-v2-r2/r2_check_run.py` 2fc5c141b18e8150654fb1ad018da0014c9b91a9883a6c3a76f845df3f665b9c |
| `implementation-v2-r3/r3_common.py` | 7bb7b688250d69a2ca209a57fd70176727aa1fe225c95c9878076be407380868 | `implementation-v2-r2/r2_common.py` 6b34cf03bb90d9d96d795f9530f9b28b53e29abbcf472e9fed3d85aa34647872 |
| `implementation-v2-r3/r3_devchecks.py` | b94cb0176c25a3ac3cec504a0d9d614f47495c49e95557f3cc770d1651652cfd | `implementation-v2-r2/r2_devchecks.py` f16470ead2437e60107b4fe70b29f2e67b635c7cd557ab21712474ea74d916bc |
| `implementation-v2-r3/r3_devchecks_more.py` | d17a10749d8c40c90adeded2e64ee82f42afd93b43b963dc14d0ab843f0c04bd | `implementation-v2-r2/r2_devchecks_more.py` be7b332df0fbcd881846ff03bf6ae27c3f248db855ced0db88b119bab7e59bab |
| `implementation-v2-r3/r3_dv12.py` | 4c0103ec07ac5a3a5dbad8ed29c876dbeebe44ada0dda5d80fec4308727a6dd0 | `implementation-v2-r2/r2_dv12.py` a0888082cb6bc98cf84b859b51d0cf84ea09919ed11d6e9affff45e0674a6d91 |
| `implementation-v2-r3/r3_dv16.py` | 7bc2df84d70dc87dadb7913a5b4e8529769d0066faa020869a3e62beaa1710b3 | new (uses r3_dv12's case runner); changed once after DV-16 attempt 1 (RD-10; before: b9b9667ab4e1c8c642fba76708d9748a259353f1bfd112142ed5cc415f860e39) |
| `implementation-v2-r3/r3_dv6.py` | 23e82cac90c6411175ca7896fc3dc43384c75b5dfac050a68585c5d0457ae4d5 | `implementation-v2-r2/r2_dv6.py` 8ed298d5303169c506acd6eebdf18fdf30ba82beb04df3293e442e25c4cf19dc |
| `implementation-v2-r3/r3_dv7.py` | 1376cbd44ab3e73ff92da612281270270cc33a50b1f42fbd3869c17fd715a740 | new (its toy constructions follow `implementation-v2-r1/r1_toy.py`, sha256 e72582251725b9dcc355264521903b2ded2a2884d8c4b73a5243c29834fafc82, which is not imported) |
| `implementation-v2-r3/r3_entry_a1.py` | cefbb3348174bf02546129a65a9a0961b3ad5f60341d25ca4bfab1d54cb56f23 | `implementation-v2-r2/r2_entry_a1.py` 5d2c6d93f3b56eaaf788149f8671407ebcf6d4a483247b9447f91a50b0e058c7 |
| `implementation-v2-r3/r3_entry_v2.py` | f79161999507cdb5438c1be39de21ba74d25ef745f490c08e56a600c28117fbd | `implementation-v2-r2/r2_entry_v2.py` ea157d9479f8e6968116abd09326274d62cbfa6eedcf1a40b49e3aa5552c08a7 |
| `implementation-v2-r3/r3_inventory.py` | 203b5be93998c6bc0d9994eaaaa64dcbe300f34e45cc6294d4f1c219d75fe81a | new (developed in `<scratchpad>/r3/dev/`, copied into the layer at 12:06Z, before DV-11) |
| `implementation-v2-r3/r3_make_plans.py` | 9143eef16951e894e5de5252bbe157c533970a3090e2becabadb24ee494f3ff7 | `implementation-v2-r2/r2_make_plans.py` 78c6d85c6be925fbf32f5da9a53a2df671ac4d3139caa779b84225f9f2bfb17a |
| `implementation-v2-r3/r3_reg1.py` | 04ee68d350198340d9427d1b575febc8f8cfe99b4f5f59ffef832de7b04378f3 | `implementation-v2-r2/r2_reg1.py` 2bf7f5d6108b7965b747e0de015e1a5fcab76888ea0b9c0415522d49a8d7bd3d |
| `implementation-v2-r3/r3_resolve.py` | 3a6828f42a6e8dd97fd487510fbb0c153ca8f51d9bcd0c310d1af96c8d5e3e15 | `implementation-v2-r2/r2_resolve.py` ee2b755c242cb681e03f8f69ea94389dcb97977459d7da2783bad872e9107438 |
| `implementation-v2-r3/r3_run_wrapper.py` | dd52a4bfad9c4bfb0e4e37ee8a24951e8992edf8d2f1dfcc112e9bcdbabb9c19 | `implementation-v2-r2/r2_run_wrapper.py` bccf6b2fff50aa8d24899d0899a8c009f9c20104562152eb1c08d16b0f3bfb47 |
| `implementation-v2-r3/reg1-exclusion-list.json` | 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c | `implementation-v2-r2/reg1-exclusion-list.json (byte copy)` 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c |
| `trial-plan-v2-r3.json` | 77cd52d15c66e6a3729b1fdb313ff1b6c8a6d58096055403cc69986b1f4ce7cf | written by `r3_make_plans.py --write` from the FROZEN `trial-plan-v2.json` |
| `trial-plan-v2-a1-r3.json` | fbc9df3b94dcc302c7e53f5cf21ee53649dad4bec536d3115a2684f0af52042e | written by `r3_make_plans.py --write` from the FROZEN `trial-plan-v2-a1.json` |
| `implementation-v2-r3.md` | (this file) | the stage note |
| `dev-evidence/stage-r3-dv/stage-r3-dv-evidence.tar.gz` | b1100521dd2ceb5df5a6afbd4db79c9883db6f0330d4e681bc7eeab3ea7cd07d | new (VA-5; section 15) |

No other path inside the repository was written. Every scratch output is under `<scratchpad>/r3/` (section 15).

## 3. PS-1: the branch, the values, the API and the RC-2 read-back semantics

- **Branch.** PS-1 branch **P-A**: parisize 67108864 and parisizemax 536870912. Both entries configure cypari2's
  process-wide PARI stack in `r3_common.PariStack.configure` before any v2 or v2-a1 module is imported (RC-2 (c)).
  The P-B trigger did not fire, so `v2_common.curve_order_pari` is not replaced.
- **API.** `cypari2.Pari()` construction with the requested sizes, followed by `allocatemem`. Read-backs use
  `default(parisize)`, `default(parisizemax)`, `stacksize()` and `stacksizemax()` on a fresh handle.
- **RC-2 (a) start read-back.** This runs immediately before dispatch. The entry exits 2 before any command unless the
  handle reads 67108864 / 536870912.
- **RC-2 (b) exit read-back.** This goes to `pari-stack.json`, with VmHWM / VmRSS. The exit semantics are
  **"requested"** (semantics probe, 10:59Z):
  - after growth of the stack on the same handle (to 268435456, within 536870912), `default(parisize)` still reads
    the requested 67108864;
  - a fresh handle reads 67108864 / 536870912.

## 4. DV-2, DV-3, DV-4 and the semantics probe (10:59:13Z-10:59:17Z; no number is a result)

- **DV-3 PASS.** Without the layer's configuration, the in-process `ellcard` at (16777291, n = 3) overflowed. The
  read-back before the call was 8000000 / 8003584, and the exception was "ellcard: the PARI stack overflows
  (current size: 8003584; maximum size: 8003584)". This reproduces RUN-GFPN-3377f1.
- **DV-2 / DV-4 PASS** at (4111, 3), (16777291, 3) and (4111, 4), two repetitions each, through the delivered r3
  configuration code: every start read-back exact, the call returned, and every exit read-back is "requested".
- **RC-5 cross-checks** at (16777291, 3) and (4111, 4). The in-process order agrees with a gp child:
  `gp -q -f --default nbthreads=1`, RLIMIT_AS 10737418240 set in the child, and getrlimit read back
  {10737418240, 10737418240}. These orders are fixture parameters, not results; the values are in the bundle
  (`dv2/dv2.json`).

## 5. RC-3 redirections, the SE-3 and HR-3 replacements (in-process only), and the read-backs

| entry | attribute | frozen value | r3 value | set when |
| --- | --- | --- | --- | --- |
| r3_entry_v2 | `v2_common.PLAN_PATH` | `experiments/EXP-GFPN-05ff43/trial-plan-v2.json` | `experiments/EXP-GFPN-05ff43/trial-plan-v2-r3.json` | after `import v2_common`, before `import v2_driver` |
| r3_entry_v2 | `v2_common.TASK_ID` | the frozen v2 task id (a forbidden id; `FORBIDDEN_TASK_IDS`) | TASK-20260924-4351ac | same |
| r3_entry_v2 | `v2_driver.solve` (SE-3) | the frozen function (v2_driver.py line 158) | `r3_resolve.solve`, which calls the recorded ORIGINAL | after `import v2_driver`, before dispatch |
| r3_entry_a1 | `a1_common.PLAN_A1_PATH` | `.../trial-plan-v2-a1.json` | `.../trial-plan-v2-a1-r3.json` | before `import a1_driver` |
| r3_entry_a1 | `a1_common.V2_PLAN_PATH` | `.../trial-plan-v2.json` | `.../trial-plan-v2-r3.json` | before `import a1_driver` |
| r3_entry_a1 | `a1_common.RECEIPT_V2_PHASE_B` | the TASK-20260923-0fa03f post-run receipt | `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-f1fb0e/post-run-receipt.json` (RC-8; VC-6 (c)) | before `import a1_driver` |
| r3_entry_a1 | `a1_common.V2_GATE_PACKAGES` | (RUN-GFPN-ac4487, RUN-GFPN-3377f1, RUN-GFPN-76420e, RUN-GFPN-b231c1) | (RUN-GFPN-f6a21a, RUN-GFPN-902222, RUN-GFPN-f5412a, RUN-GFPN-bfe956), read from `trial-plan-v2-r3.json` `gate.blocking_packages` | before `import a1_driver` |
| r3_entry_a1 | `a1_common.TASK_ID_RUNS` | the frozen v2-a1 task id (a forbidden id) | TASK-20260924-b3e690 | before `import a1_driver` |
| r3_entry_a1 | `a1_common.PROTOCOL_VERSION` | "2-a1" | "2-a1-r3" | before `import a1_driver` |
| r3_entry_a1 | `v2_common.PLAN_PATH` | set by `a1_common.redirect_v2()` at a1_driver import | = the redirected PLAN_A1_PATH; never set to trial-plan-v2-r3.json | by redirect_v2 (a1_driver.py line 30) |
| r3_entry_a1 | `v2_common.TASK_ID` | redirect_v2's definition-time default (a forbidden id) | TASK-20260924-b3e690 | AFTER `import a1_driver` |
| r3_entry_a1 | `v2_driver.solve` (SE-3; a1_driver's `D`) | the frozen function | `r3_resolve.solve` | after `import a1_driver`, before dispatch |
| r3_entry_a1 | `a1_health.run_system` (HR-3) | the frozen function (a1_health.py; argv line 144, launch line 147) | `r3_resolve.run_system`, which calls the recorded ORIGINAL | after `import a1_driver` (a1_driver imports a1_health at its line 38), before dispatch |

- **Read-back.** It runs after all imports, immediately before dispatch, and goes into `pari-stack.json` under
  `redirections`. It includes the replacement keys:
  - "v2_driver.solve (SE-3 replacement)" (both entries);
  - "a1_health.run_system (HR-3 replacement)" (a1 entry);
  - "a1_health (HR-3: not imported in the v2 entry)" (v2 entry; the v2 entry refuses if a module named a1_health is
    loaded).
- **Refusal.** Each replacement is refused (exit 2, before any command) if the attribute was rebound after install,
  or if the recorded original is not the frozen function. For HR-3 it is also refused if `a1_driver`'s `H` is not
  the frozen `a1_health` module.
- **VA-7 (a).** A redirected value equal to, or containing, one of the six forbidden task ids is refused
  (`r3_common.check_redirections`).
- **Checker isolation.** `r3_check_run.py` runs the frozen `v2_check_run.main` / `a1_check_run.main` in a SEPARATE
  process, with only the redirections applied.

## 6. The two re-solve wrappers and the callgrind-site recording (`r3_resolve.py`)

- **SE-3 at S-1 (`v2_driver.solve`)** and **HR-3 at S-2 (`a1_health.run_system`)** share one bounded loop, `_bounded`.
  - The SSF signature is SF-1 clauses (i)-(v).
  - K = 5 re-solves, so at most six attempts.
  - Each attempt starts at least 2.0 s after the previous attempt's recorded end.
  - Before each re-solve, the attempt's output and log files are renamed with the suffix `.ssf-attempt<k>`.
  - Every attempt has the same cap and timeout as attempt 1.
  - The re-solve cap is SF-2 (c) at S-1 (the call's `timeout_s`) and HR-6 at S-2 (`a1_health.DEV_TIMEOUT_S`, read at
    call time; 1800).
  - SE-2 (4) / HR-5 consistency: a violation raises `SolverEventConsistencyError`, the package ends `failed` /
    `implementation_error`, and the violation is recorded.
  - At S-1, `gb_only=True` calls pass through unwrapped and are counted (`passthrough_calls_gb_only_true`).
- **CG-3 with CC-4 at S-3 (the callgrind child).** S-3 is NOT re-solved (CG-2).
  - After each ORIGINAL S-1 call whose result carries `instructions_callgrind`, the wrapper records the CG-3 fields
    under site "v2_driver.solve/callgrind":
    - `tag` and `attempt_recorded_by_the_wrapper`;
    - the log files' sha256 and size, or "absent";
    - `dimension_of_quotient`;
    - `fglm_squarefree_degree`, which is "absent" when the key is absent (CC-4; CC-8 (a));
    - `positive_dimension_reported`, `random_linear_form_string_in_log` and `log_visible_ssf_indicator`;
    - `printed_quotient_dimension_equals_recorded_attempt`, `reg1_compared_fields_verbatim` and
      `child_readback_equals_requested_cap`.
  - It also keeps the counts `callgrind_children_observed`, `with_log_visible_ssf_indicator`,
    `with_quotient_dimension_mismatch` and `with_readback_differing_from_requested_cap`.
  - No field is added to `raw-result.json`, and nothing reads these values to decide anything (VA-6 (c)).
- **The record.** `solver-events.json` at the run root has:
  - `sites`, with one entry per site: disposition, counters, and events or records;
  - a top-level `consistency_violation`.

  The manifest's `solver_events` block is per site. The event-record writer `_write` has no guard (VA-7).
- **VA-6.**
  - The whole-file sha256 of `solver-events.json` is V-7.
  - Exists, parses, the flag, and the S-1 / S-2 counters are epsilon.
  - V-5 (the CG-3 records and counts) is recorded and reported only.
- **VA-7.**
  - Task-id keys are checked by constant key (`r3_check_run.forbidden_id_keys`).
  - The byte sweep (`forbidden_id_sweep`) reads only `command.txt`, `stdout.log`, `stderr.log`, `environment.json`
    and `pari-stack.json`.
- **VA-8 (b).** Each guard is a separate function with its own class.
- **Readings adopted (disclosed; section 14):**
  - RD-1: the VA-7 "site value" is a site-record field (census M-3: "a key the site record does not carry cannot read
    site data").
  - Derived tokens can therefore appear in the swept files without being site values: PASS / FAIL in `stdout.log`,
    the `pari-stack.json` status, and a `SolverEventConsistencyError` traceback in `stderr.log`.
  - This reading is disclosed, not a STOP.

## 7. The r3 run wrapper, the r3 checker, the plans and REG-1

- **`r3_run_wrapper.py` (R-1..R-13).** Before ANY directory is created, the wrapper evaluates every check and
  refuses (exit 2, nothing written, every failing reason printed) unless all hold:
  - R-1: the nine hashes above.
  - R-2: the RUN-ID is reserved in its r3 plan, and is not a v1, v2, v2-a1, r1 or r2 id, nor any of the 124 retired
    ids.
  - R-3: `runs/RUN-ID` does not exist.
  - R-4: `implementation-v2/`, its note and its plan match the TASK-20260923-0fa03f phase-A receipt, and are tracked
    and clean.
  - R-5: the same for `implementation-v2-a1/`, against the TASK-20260923-4ff597 phase-A receipt.
  - R-6: the same for the r3 layer, this note and both r3 plans, against the TASK-20260924-f1fb0e phase-A receipt.
  - R-7: the PS-4 gate rule:
    - G1..G4 `completed_valid` with `gate_pass` true, and REG-1 (d-parsed) passed;
    - REG-1 is evaluated before G2 and before every later package;
    - addendum packages 2-11 also need the controls_a1 image passed.
  - R-8: every required package has a manifest.
  - R-9: the plan's watchdogs equal `trial-plan-v2.json`'s.
  - R-10: no other solver-like process.
  - R-11: the ceiling over the EIGHT plans (existing + 1 <= 48; currently 2 + 31 + 11 = 44), and the plan's own
    count.
  - R-12: the contingency rule verbatim.
  - R-13: the plan records its label, the ids and sha256 of the seven repair amendments (`repair.amendments.<key>`)
    and its run card. None of the six forbidden task ids appears in the plan, and no r3 constant or redirected value
    carries one (VA-7 (a)).

  Other properties:
  - The preflight is split into single-class helpers (`r7_gate_packages`, `r7_reg1_verdict`, `r7_controls_a1_image`,
    `r8_requires`, `r12_contingency`).
  - The driver child runs with PYTHONHASHSEED "0" (SE-6), read back inside the driver process into the manifest.
  - `environment.json` records the toolchain including `callgrind_annotate`.
  - Launch rule: no outer guard around the wrapper.
- **`r3_check_run.py`.**
  - It runs the frozen checkers in a separate process (section 5).
  - It adds the r3 checks, one class per function: `manifest_protocol_checks`, `pari_stack_checks`,
    `events_file_epsilon`, `events_file_integrity`, `reg1_recorded_check`, `forbidden_id_keys`, `forbidden_id_sweep`
    and `status_agreement`.
  - It adds the SC-4 accounting at BOTH sites: S-1 attempts, and S-2 through `health/health-<p>.json`. The accounting
    is reported only.
- **Plans.** Both plans were written once by `r3_make_plans.py --write` at 11:01:16Z (RC-4 (c) equality asserted in
  the writer). They hold 31 and 11 packages; the branch P-A; the VA-1 repair block; the 124 retired ids; and the
  ceiling note. RC-4 is covered in the two sections at the top of this note; the sha256 values are in section 2.
- **REG-1.**
  - `r3_reg1.py` is the r2 comparator (d-parsed; exclusion list X1..X17), unchanged except `solver_events_check`,
    which reads the S-1 / S-2 events and the flag by constant key.
  - `reg1-exclusion-list.json` is a byte copy (sha256 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c;
    DV-8).
  - Every reference file read is verified against the TASK-20260923-0fa03f post-run receipt first.

## 8. DV-1 inventory, the HR-11 / CC-1 site concordance and the R3S-10 consumer inventory

**DV-1 (static; 11:15:01Z; flags from the frozen code):**

- **v2 fixture:** `v2_driver.main -> cmd_fixture (275) -> fixture_core (284) -> C.curve_order_pari (308)`. IN-PROCESS
  cypari2, at (4111, n = 3) and (16777291, n = 3). Covered by P-A (DV-2).
- **v2 controls:** `cmd_controls (752) -> C.fixture_n3(4111) (764) -> C.curve_order_pari (771)`. IN-PROCESS, at
  (4111, n = 3). Covered by DV-2.
- **v2 fixture4:** `cmd_fixture4 (526) -> C.fixture_n4 -> C.curve_order_pari (542)`. IN-PROCESS, at (4111, n = 4).
  Covered by DV-4.
- **v2 anchor-identity:** `cmd_anchor_identity (628) -> V.run_child(SAGE_PYTHON, COMPARATOR) (650)`. **FLAGGED**: a
  Sage child with a PARI-backed GF(p^5) and a library-default stack (DEC-20260924-bea197 R-5).
  - The Sage probe child (RLIMIT_AS set in the child; getrlimit read back {10737418240, 10737418240}) reads parisize
    8000000, parisizemax 1073741824, Sage 10.9.
- **v2 build / cells / aggregate:** builders in capped `v2_child.py` children, msolve children, and file reads. No
  PARI.
- **a1 controls-a1:** `cmd_controls_a1 (56) -> P.curve_facts (89) -> V.run_child(/usr/bin/gp)`. A gp CHILD, with
  parisize 256000000 / parisizemax 4000000000 set in its script (a1_pari.py line 38), and no random seed set
  (CG-9 (f)).
- **a1 build / cells / aggregate-a1:** these delegate to the v2 commands or read files. No PARI.
- **r3 layer:** `PariStack` constructions, `allocatemem` and default read-backs only. No computation.
- **callgrind_annotate (S-3):** `v2_solver.callgrind_instructions` line 533 runs `subprocess.run(["callgrind_annotate",
  ...])`. It uses a PATH lookup, a 600 s timeout, and is uncapped in the frozen code. It is not an msolve, valgrind, gp
  or builder child, and is recorded as an observation.
- 235 static PARI / Sage / gp mentions in the frozen trees are listed in `dv1/dv1_static.json` (bundle).

**DV-1 dynamic (DV-7 trace, 1499 events):**
- In-process PARI calls occur only in `curve_order_pari`: for toy G1 (both worlds) at (1033, degree 3), and for F-4
  at (1033, degree 4).
- `cypari2.Pari()` constructions come only from `r3_common` (configure, start_readback) and `curve_order_pari`.
- Children by launcher:
  - `v2_driver.solve` -> msolve;
  - `a1_health.run_system` -> msolve;
  - `v2_solver.callgrind_instructions` -> valgrind;
  - `a1_pari.curve_facts` -> gp;
  - `v2_driver.child_job` -> python3 builders.

**DV-11 (12:07:11Z; PASS; no STOP):**
- **STATIC.** The msolve launch list over `implementation-v2/`, `implementation-v2-a1/` and the r3 layer EQUALS the
  CC-1 sites:
  - S-1 at v2_driver.py 166;
  - S-2 at a1_health.py 147;
  - S-3 at v2_driver.py 209 (argv) and v2_solver.py 517 (launch).

  There are 0 unexpected launch calls and **0 r3-layer launch sites** (HR-11 / CC-1 concordance: no r3 file adds a
  launch site). The census sites of CN-1 outside the two frozen trees are "unreachable (U-1..U-5 of CC-1)".
- **Scope disclosure.** The development harnesses that call the frozen launch functions, namely DV-17's
  `callgrind_instructions` calls and the DV-7 continuations' wrapper calls, live OUTSIDE the layer in
  `<scratchpad>/r3/dev/` (RD-2). No delivered entry can reach them.
- **DYNAMIC** (over the 20 DV-7 attempt-5 toy packages; every per-package count equal):
  - 562 S-1 msolve children = 562 wrapper attempts (+ 0 pass-through);
  - 2 S-2 msolve children = 2 wrapper attempts;
  - 90 S-3 valgrind children = 90 wrapped ok calls with a callgrind timeout = 90 CG-3 records. Every S-3 child lies
    inside a wrapped-call interval and every one has a CG-3 record;
  - 0 classified launches outside both wrappers; 0 other msolve children.
- **Supplementary (report only):** the same count logic applied to the two preserved real toy G2 packages.
  - p = 1039: 47 msolve children = 47 wrapper attempts, including 11 real SSF re-solves; 34 valgrind children = 34
    CG-3 records.
  - p = 65539: 36 = 36; 0 valgrind children.
  - Both are equal (`dv11_extra/`).
- **R3S-10 consumer inventory** (`implementation-v2-r3/r3_inventory.py`; `dv11/inventory/inventory.json` in the
  bundle): 222 functions parsed and 199 listed, each with exactly one class. Counts:

  | class | functions |
  | --- | --- |
  | alpha | 73 |
  | reads no site value | 53 |
  | epsilon | 27 |
  | gamma | 17 (each naming its clause) |
  | reads no site value directly | 6 |
  | beta | 5 |
  | V-1 row K-1 (CG-4) | 5 |
  | V-4 | 3 |
  | V-7 | 2 |
  | V-2 | 2 |
  | V-2 (CG-4) | 2 |
  | V-5 | 2 |
  | V-1 row K-5 | 1 |
  | V-1 row K-2 | 1 |

  The results:
  - 0 unclassified functions;
  - 0 imports from `implementation-v2-r1/`, `implementation-v2-r2/` or `implementation/`;
  - 0 consumers of a V-5 value at E1-E4;
  - 0 consumers using an epsilon value to choose a recorded result;
  - **stops: none**.
- **Class rule (declared).** A function's class is that of the site values it reads DIRECTLY. Orchestrators are
  "reads no site value directly". Development-check functions carry effect E6 under DEV_RULE.

## 9. DV-1..DV-17 outcomes (development observations; no number is a result)

| check | outcome | when (UTC) | notes |
| --- | --- | --- | --- |
| DV-1 | complete | 11:15:01Z static (attempt 2); dynamic from DV-7 | section 8; attempt 1 harness fault (RD-4) |
| DV-2 | PASS | 10:59Z | section 4 |
| DV-3 | PASS | 10:59Z | overflow reproduced without the layer's configuration |
| DV-4 | PASS | 10:59Z | (4111, n = 4) |
| DV-5 | PASS | 11:09Z | plans: M a bijection onto the 42 minted ids; images disjoint from the frozen, r1, r2 and 124 retired ids; the writer regenerates byte-identically |
| DV-6 | PASS (attempt 2) | 11:13Z | 57 wrapper cases (R-1..R-13 incl. the nine hashes, a 175-id R-2 sweep, all seven repair amendments, the six forbidden ids, VA-7 (a)), 13 entry cases (PARI, RC-3, SE-3 (a)/(b), HR-3 attribute / original / `H`, v2 entry with a1_health imported, VA-7 redirection); attempt 1 an implementation defect in R-13 (RD-3) |
| DV-7 | PASS (attempt 5) | 11:23:10Z-11:53:48Z | SE-5 probe run ONCE (attempt 2): PASS; REG-1 on a perturbed copy FAIL (as required); RC-8 phase-B check verified; controls-a1 at 1021 through the r3 a1 entry; checker on every toy package; attempts 1-4 preserved (RD-5..RD-9) |
| DV-8 | PASS | 11:10Z | exclusion list byte-identical to X1..X17 (sha256 4122bcb0…94a99f2c); self-comparison PASS; every perturbation FAIL; reference-integrity negative FAIL as required; 219 reference files verified |
| DV-9 | PASS | 12:33:09Z (last check before the bundle) | section 15 |
| DV-10 | PASS | 11:09Z | 42 distinct ids, equal to the allocator outputs in order; none in any existing plan or retired list; no run directory |
| DV-11 | PASS | 12:07:11Z | section 8 |
| DV-12 | PASS (a)-(g) | 11:54:17Z-12:03:57Z | section 10 |
| DV-13 | PASS | DV-7 attempt 5 | the driver child's PYTHONHASHSEED read back "0" in every world-A toy package (19) and "12345" in world B's G1 (the declared SE-5 override); also "0" in the preserved toy G2 packages |
| DV-14 | PASS | DV-7, DV-12, DV-16 | every re-solve attempt started >= 2.0 s after the previous attempt's end: the toy lineage's 11 real re-solves (preserved attempt-2 toy G2; minimum gap 2.010 s), and every forced re-solve of the DV-12 / DV-16 cases that check spacing ((a)-(d) and (a)-(b); all `spacing_ge_2s` true); DV-7 attempt 5 had 0 re-solves |
| DV-15 | PASS | 12:06:01Z | set O 75 outputs (73 ok-classified), 596 toy-lineage rows, invariant holds on every applicable output, 0 violations; section 11 |
| DV-16 | PASS (a)-(e) (attempt 2) | 12:04:54Z-12:05:46Z | toy prime 1021 declared before the check; attempt 1 a harness defect (RD-10) |
| DV-17 | PASS | 12:08:42Z - 12:31:47Z | section 12 |

**DV-7 details.**
- **Toy objects.** Toy primes only; no ladder or fixture prime was solved except DV-17's calls at 4111.
  - n = m = 3 fixture data at 1033 and 1039, plus 65539 for the attempt-4 continuation.
  - n = m = 4 data at 1033.
  - Toy ladder rungs chosen by the frozen `a1_toy.toy_ladder` through capped gp children: 1021 (addendum role), and
    1051 (v2 role; 1031 was incomplete, as recorded in the selection trail).
- **Not exercisable at toy scale (recorded, not run):**
  - `anchor-identity`: it hard-codes p' = 16777291 and the Sage anchor system.
  - `controls`: it hard-codes the fixture field at 4111 and ladder primes 4111, 262151 and 16777291.
  - Their gate roles G3 and G4 are SYNTHETIC rows.
  - The v2 builds and cells at 262151 and 16777291 are SYNTHETIC rows.
  - Contingency launches are covered by DV-6's R-12 refusals.
- **Toy G2 (RD-6, RD-8).** The real toy G2 ran twice and failed at both declared toy primes:
  - p = 1039: persistent SSF signature on all six attempts of two calls;
  - p = 65539: msolve SIGSEGV on every child, classified `crashed` / infrastructure_error, never evidence.

  Both packages are preserved, and the checker passed on the 65539 package. Attempt 5 exercised the lineage past
  the gate on a SYNTHETIC toy G2 row. **Consequence, stated plainly:** R-7's REG-1 comparison for a real, passing
  toy G2 was not exercised. R-7's refusal of a failed G2 WAS exercised, in attempts 2 and 4: 38 correct refusals
  each, nothing written.
- **The 20 packages run through the delivered wrapper and entries in attempt 5:**
  - world A: G1, F-4, the v2 build, six cells, the v2 aggregate, controls-a1, the addendum build, six addendum cells
    and aggregate_a1;
  - world B: G1.

  All are `completed_valid`. Every child read getrlimit 10737418240 / 10737418240, msolve threads were 1, and the
  PARI stack status was `command_returned`. The checker returned rc 0 on every world-A package; on world B's G1 it
  failed only on "SE-6: the driver process read back PYTHONHASHSEED '12345', not '0'" (the declared override).
- **Forbidden task ids in toy artifacts (report only).** One occurrence, in the toy COPY of the frozen
  `trial-plan-v2.json`, which carries its own frozen task id.

## 10. DV-12 (a)-(g) and DV-16 (a)-(e) (forced cases through the delivered wrapper; development shims)

**DV-12 (seedresolve SF-6; S-1; toy G1 at 1033; target `fx_reg1_S3`):** all cases pass: True; STOP: None.

| case | package status | failure class | pass | checks (all true unless listed) |
| --- | --- | --- | --- | --- |
| U | completed_valid | None | reference (U) | the unforced reference |
| a | completed_valid | None | True | attempt1_ssf_clause, package_completed, re_solved, recorded_target_equals_U, reg1_d_parsed_vs_U_pass, renamed_attempt1_files, spacing_ge_2s |
| b | completed_valid | None | True | attempt1_ssf_clause, package_completed, re_solved, recorded_target_equals_U, reg1_d_parsed_vs_U_pass, renamed_attempt1_files, spacing_ge_2s |
| c | completed_valid | None | True | attempt1_ssf_clause, package_completed, re_solved, recorded_target_equals_U, reg1_d_parsed_vs_U_pass, renamed_attempt1_files, spacing_ge_2s |
| d | failed | implementation_error | True | all_clause_ii, no_resolve_cap, recorded_degenerate_D_undefined, renamed_attempts_1_to_5, six_attempts, spacing_ge_2s, still_ssf_after_last_attempt |
| e | failed | implementation_error | True | implementation_error, manifest_block_records_violation, package_failed, violation_recorded |
| f | failed | implementation_error | True | manifest_block_counts_cap, recorded_is_attempt2_class, resolve_cap_reached, two_attempts |
| g | failed | implementation_error | True | implementation_error, manifest_block_records_violation, package_failed, violation_recorded |

**DV-16 (healthresolve HR-9; S-2; toy prime 1021 declared in section 0; target `health_p1021_d222`):** all cases pass: True; STOP: None.

| case | package status | failure class | pass | checks (all true unless listed) |
| --- | --- | --- | --- | --- |
| U | completed_valid | None | reference (U) | the unforced reference |
| a | completed_valid | None | True | attempt1_ssf_clause_ii, no_seed2_redraw, package_completed_as_U, re_solved, recorded_equals_U_pass_checks_D, renamed_attempt1_files, spacing_ge_2s |
| b | completed_valid | None | True | all_clause_ii, frozen_seed2_redraw_ran, recorded_is_the_6th_forced_result, renamed_attempts_1_to_5, seed2_redraw_itself_wrapped, six_attempts, spacing_ge_2s, still_ssf_after_last_attempt |
| c | failed | implementation_error | True | implementation_error, manifest_block_records_violation, package_failed, violation_recorded |
| d | completed_valid | None | True | cap_compared_with_DEV_TIMEOUT_S_1800, manifest_block_counts_cap, recorded_is_attempt2, resolve_cap_reached, two_attempts |
| e | failed | implementation_error | True | implementation_error, manifest_block_records_violation, package_failed, violation_recorded |


## 11. DV-15 per-output table (SC-3; frozen v2_solver imported read-only; no solver child)

- The invariant, checked on every ok-classified parametrised output: n_den_zero = n_arity = 0 and n_distinct =
  n_points = n_roots.
- The integrity inputs were each verified against their receipts first:
  - the characterization archive `distinct-outputs.tar.gz`;
  - the stage-R1 DV-7 bundle;
  - the seedresolve premise check;
  - RUN-GFPN-ac4487 `solver/`.
- Table (b) covers the 22 non-synthetic toy-lineage package directories: the 20 of DV-7 attempt 5 and the two
  preserved real toy G2 packages. It includes both sites.
- Rows with parse kind "none" are not parametrisations; the invariant does not apply to them, and they are listed.
- Degree columns are omitted here and kept in the bundle (`dv15/dv15.json`) as harness values.
- Supplementary (report only): the same accounting over the 14 DV-12 / DV-16 case packages gives 222 rows, 222
  applicable, 0 violations (`dv15_supp_dv12_dv16/`).

**(a) Set O (75 outputs).**

| # | input key | output sha256 (first 12) | p | nvars | classifier outcome | parse | applicable | n_roots | n_den_zero | n_arity | n_points | n_distinct | invariant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `event/fx_reg0_torsion_S3_norm` | 201812d43b7c | 1033 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 2 | `event/fx_reg0_torsion_S3_norm` | d2878f4f2b27 | 1033 | 3 | degenerate_parametrisation | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 3 | `ac4487/fx_fresh1_S3` | 60a4cd6e4607 | 4111 | 3 | ok | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 4 | `ac4487/fx_fresh1_S3_rescaled` | efb50e2ef8c6 | 4111 | 3 | ok | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 5 | `ac4487/fx_fresh1_raw_u` | 913635c67f3d | 4111 | 3 | ok | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 6 | `ac4487/fx_fresh1_raw_x` | 7dc2c544bc5d | 4111 | 3 | ok | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 7 | `ac4487/fx_fresh1_torsion_S3_norm` | efb572acc1a0 | 4111 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 8 | `ac4487/fx_fresh1_torsion_S3_rq` | 7a89173a15d1 | 4111 | 4 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 9 | `ac4487/fx_fresh2_S3` | eca772970934 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 10 | `ac4487/fx_fresh2_S3_rescaled` | ac26fa0bd1d1 | 4111 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 11 | `ac4487/fx_fresh2_raw_u` | 12c4b747e3b2 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 12 | `ac4487/fx_fresh2_raw_x` | 7a3c217d2f43 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 13 | `ac4487/fx_fresh2_torsion_S3_norm` | 2ebac156e566 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 14 | `ac4487/fx_fresh2_torsion_S3_rq` | b564bab4afdf | 4111 | 4 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 15 | `ac4487/fx_planted0_S3` | 5a5c3ade3fad | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 16 | `ac4487/fx_planted0_S3_rescaled` | e0b8706cb485 | 4111 | 3 | ok | param | True | 8 | 0 | 0 | 8 | 8 | True |
| 17 | `ac4487/fx_planted0_raw_u` | fa43416ce9f9 | 4111 | 3 | ok | param | True | 48 | 0 | 0 | 48 | 48 | True |
| 18 | `ac4487/fx_planted0_raw_x` | 4979535ed24c | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 19 | `ac4487/fx_planted0_torsion_S3_norm` | 4b64be0be57b | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 20 | `ac4487/fx_planted0_torsion_S3_rq` | 88f25f454f52 | 4111 | 4 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 21 | `ac4487/fx_planted1_S3` | d697a8abefa7 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 22 | `ac4487/fx_planted1_S3_rescaled` | 811679d46e3b | 4111 | 3 | ok | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 23 | `ac4487/fx_planted1_raw_u` | e2560125e6aa | 4111 | 3 | ok | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 24 | `ac4487/fx_planted1_raw_x` | a8d0557e35dd | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 25 | `ac4487/fx_planted1_torsion_S3_norm` | aaadd08c36eb | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 26 | `ac4487/fx_planted1_torsion_S3_rq` | 4a2ffb7100cc | 4111 | 4 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 27 | `ac4487/fx_reg0_S3` | 53293037cd73 | 4111 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 28 | `ac4487/fx_reg0_S3_rescaled` | 6ea8b0e8d7fc | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 29 | `ac4487/fx_reg0_raw_u` | 728ecf36505e | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 30 | `ac4487/fx_reg0_raw_x` | a87355d97a2f | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 31 | `ac4487/fx_reg0_torsion_S3_norm` | 606fc541d777 | 4111 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 32 | `ac4487/fx_reg0_torsion_S3_rq` | 43b940e70603 | 4111 | 4 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 33 | `ac4487/fx_reg1_S3` | 1f2628d960a8 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 34 | `ac4487/fx_reg1_S3_rescaled` | 3b232b2b6557 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 35 | `ac4487/fx_reg1_S3_rescaled` | 7e283c2834f0 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 36 | `ac4487/fx_reg1_raw_u` | e57c788f1f63 | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 37 | `ac4487/fx_reg1_raw_x` | 5f44e62678ce | 4111 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 38 | `ac4487/fx_reg1_torsion_S3_norm` | efc903550623 | 4111 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 39 | `ac4487/fx_reg1_torsion_S3_rq` | 840f544d9da3 | 4111 | 4 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 40 | `event/fx_reg0_torsion_S3_norm` | ec54fd1520ea | 1033 | 3 | degenerate_parametrisation | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 41 | `toy35/fx_fresh1_S3` | 0b826a955bf8 | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 42 | `toy35/fx_fresh1_S3_rescaled` | cd0ea21d0d43 | 1033 | 3 | ok | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 43 | `toy35/fx_fresh1_raw_u` | a260a14727f5 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 44 | `toy35/fx_fresh1_raw_x` | 441286fd1641 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 45 | `toy35/fx_fresh1_torsion_S3_norm` | b9d29cb8c0e3 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 46 | `toy35/fx_fresh1_torsion_S3_rq` | d4b7d575a576 | 1033 | 4 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 47 | `toy35/fx_fresh2_S3` | c64559085efb | 1033 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 48 | `toy35/fx_fresh2_S3_rescaled` | 92fae5959205 | 1033 | 3 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 49 | `toy35/fx_fresh2_raw_u` | 658094488ecd | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 50 | `toy35/fx_fresh2_raw_x` | 8ff2d23f552c | 1033 | 3 | ok | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 51 | `toy35/fx_fresh2_torsion_S3_norm` | 474178c25c83 | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 52 | `toy35/fx_fresh2_torsion_S3_rq` | 332ee8496348 | 1033 | 4 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 53 | `toy35/fx_planted0_S3` | 12337eae1056 | 1033 | 3 | ok | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 54 | `toy35/fx_planted0_S3_rescaled` | 5ade3f32ffa1 | 1033 | 3 | ok | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 55 | `toy35/fx_planted0_raw_u` | 7b2d971242c2 | 1033 | 3 | ok | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 56 | `toy35/fx_planted0_raw_x` | 3c9855ee4ad2 | 1033 | 3 | ok | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 57 | `toy35/fx_planted0_torsion_S3_norm` | 4a2734dc2c2f | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 58 | `toy35/fx_planted0_torsion_S3_rq` | 49eb0b2170e7 | 1033 | 4 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 59 | `toy35/fx_planted1_S3` | 9d782351728a | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 60 | `toy35/fx_planted1_S3_rescaled` | bc2f6065bfc1 | 1033 | 3 | ok | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 61 | `toy35/fx_planted1_raw_u` | a58b0f283ef5 | 1033 | 3 | ok | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 62 | `toy35/fx_planted1_raw_x` | b9bc99f4a96c | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 63 | `toy35/fx_planted1_torsion_S3_norm` | b6a14a7a31ce | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 64 | `toy35/fx_planted1_torsion_S3_rq` | 1f2b7f6c1bd9 | 1033 | 4 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 65 | `toy35/fx_reg0_S3` | b7c2aec257a4 | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 66 | `toy35/fx_reg0_S3_rescaled` | ade0308b662b | 1033 | 3 | ok | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 67 | `toy35/fx_reg0_raw_u` | 78ce47f76a78 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 68 | `toy35/fx_reg0_raw_x` | 84c80057e514 | 1033 | 3 | ok | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 69 | `toy35/fx_reg0_torsion_S3_rq` | 4baa667bbef5 | 1033 | 4 | ok | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 70 | `toy35/fx_reg1_S3` | c6ffbdf11462 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 71 | `toy35/fx_reg1_S3_rescaled` | 6e005f1b4b37 | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 72 | `toy35/fx_reg1_raw_u` | 4a0aacd842bd | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 73 | `toy35/fx_reg1_raw_x` | a6187802ea6f | 1033 | 3 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 74 | `toy35/fx_reg1_torsion_S3_norm` | 64f7fe95d895 | 1033 | 3 | ok | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 75 | `toy35/fx_reg1_torsion_S3_rq` | 4bdba858f220 | 1033 | 4 | ok | param | True | 0 | 0 | 0 | 0 | 0 | True |

**(b) Toy lineage (596 ok-classified attempts; 22 package directories).**

| # | package | site | tag | output sha256 (first 12) | parse | applicable | n_roots | n_den_zero | n_arity | n_points | n_distinct | invariant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 2 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 3 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 4 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 5 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 6 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 7 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 8 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 9 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 10 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 11 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 12 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 13 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 14 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 15 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 16 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 17 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 18 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 19 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 20 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_rq_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 21 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 22 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 23 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 24 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 25 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 26 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 27 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 28 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 29 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 30 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 31 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 32 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 33 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 34 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 35 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 36 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 37 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 38 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 39 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 40 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 41 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 42 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 43 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 44 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 45 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 46 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 47 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 48 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 49 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 50 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 51 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 52 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 53 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 54 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 55 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 56 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 57 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 58 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 59 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 60 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `S3_rescaled_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 61 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 62 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 63 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 64 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 65 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 66 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 67 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 68 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 69 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 70 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 71 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 72 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 73 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 74 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 75 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 76 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 77 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 78 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 79 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 80 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0983ac` | v2_driver.solve | `torsion_S3_norm_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 81 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 82 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 83 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 84 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 85 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 86 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 87 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 88 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 89 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 90 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 91 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 92 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 93 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 94 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 95 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 96 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 97 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 98 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 99 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 100 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0bc236` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 101 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 102 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 103 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 104 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 105 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 106 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 107 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 108 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 109 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 110 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 111 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 112 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 113 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 114 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 115 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 116 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 117 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 118 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 119 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 120 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_rq_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 121 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 122 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 123 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 124 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 125 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 126 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 127 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 128 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 129 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 130 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 131 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 132 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 133 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 134 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 135 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 136 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 137 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 138 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 139 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 140 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 141 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 142 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 143 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 144 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 145 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 146 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 147 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 148 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 149 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 150 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 151 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 152 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 153 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 154 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 155 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 156 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 157 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 158 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 159 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 160 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `S3_rescaled_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 161 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 162 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 163 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 164 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 165 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 166 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 167 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 168 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 169 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 170 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 171 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 172 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 173 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 174 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 175 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 176 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 177 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 178 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 179 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 180 | `dv7/toy/world_A/exp/runs/RUN-GFPN-0be651` | v2_driver.solve | `torsion_S3_norm_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 181 | `dv7/toy/world_A/exp/runs/RUN-GFPN-2c4862` | a1_health.run_system | `health_p1021_d222` | e5a58fc75292 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 182 | `dv7/toy/world_A/exp/runs/RUN-GFPN-2c4862` | a1_health.run_system | `health_p1021_d444` | c69bdf3a1d84 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 183 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t0_S4` | 9d186a537062 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 184 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t0_S4_rescaled` | f9c83b9b633f | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 185 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t0_torsion_S4_norm` | 343b90928bfe | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 186 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t0_torsion_S4_rq` | 94c67bd223b5 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 187 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t1_S4` | c4175cd6ad7c | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 188 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t1_S4_rescaled` | 47466d984228 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 189 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t1_torsion_S4_norm` | 77060b5798c2 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 190 | `dv7/toy/world_A/exp/runs/RUN-GFPN-596fb2` | v2_driver.solve | `f4_t1_torsion_S4_rq` | 35d9f77efb09 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 191 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 192 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 193 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 194 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 195 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 196 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 197 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 198 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 199 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 200 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 201 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 202 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 203 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 204 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 205 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 206 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 207 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 208 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 209 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 210 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5bf619` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 211 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 212 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 213 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 214 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 215 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 216 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 217 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 218 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 219 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 220 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 221 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 222 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 223 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 224 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 225 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 226 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 227 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 228 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 229 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 230 | `dv7/toy/world_A/exp/runs/RUN-GFPN-5e9b88` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 231 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 232 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 233 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 234 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 235 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 236 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 237 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 238 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 239 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 240 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 241 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 242 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 243 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 244 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 245 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 246 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 247 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 248 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 249 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 250 | `dv7/toy/world_A/exp/runs/RUN-GFPN-716bdf` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 251 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 252 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 253 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 254 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 255 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 256 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 257 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 258 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 259 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 260 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 261 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 262 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 263 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 264 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 265 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 266 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 267 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 268 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 269 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 270 | `dv7/toy/world_A/exp/runs/RUN-GFPN-7fc9a4` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 271 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 272 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 273 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 274 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 275 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 276 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 277 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 278 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 279 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 280 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 281 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 282 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 283 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 284 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 285 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 286 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 287 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 288 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 289 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 290 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_rq_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 291 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 292 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 293 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 294 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 295 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 296 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 297 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 298 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 299 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 300 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 301 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 302 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 303 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 304 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 305 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 306 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 307 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 308 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 309 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 310 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 311 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 312 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 313 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 314 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 315 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 316 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 317 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 318 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 319 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 320 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 321 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 322 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 323 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 324 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 325 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 326 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 327 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 328 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 329 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 330 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `S3_rescaled_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 331 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 332 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 333 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 334 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 335 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 336 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 337 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 338 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 339 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 340 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 341 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 342 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 343 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 344 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 345 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 346 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 347 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 348 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 349 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 350 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8816e9` | v2_driver.solve | `torsion_S3_norm_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 351 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 352 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 353 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 354 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 355 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 356 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 357 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 358 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 359 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 360 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 361 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 362 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 363 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 364 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 365 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 366 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 367 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 368 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 369 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 370 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_rq_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 371 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 372 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 373 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 374 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 375 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 376 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 377 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 378 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 379 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 380 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 381 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 382 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 383 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 384 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 385 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 386 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 387 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 388 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 389 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 390 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 391 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 392 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 393 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 394 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 395 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 396 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 397 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 398 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 399 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 400 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 401 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 402 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 403 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 404 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 405 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 406 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 407 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 408 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 409 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 410 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `S3_rescaled_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 411 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 412 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 413 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 414 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 415 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 416 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 417 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 418 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 419 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 420 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 421 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 422 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 423 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 424 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 425 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 426 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 427 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 428 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 429 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 430 | `dv7/toy/world_A/exp/runs/RUN-GFPN-8b0636` | v2_driver.solve | `torsion_S3_norm_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 431 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 432 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 433 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 434 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 435 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 436 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 437 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 438 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 439 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 440 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 441 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 442 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 443 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 444 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 445 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 446 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 447 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 448 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 449 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 450 | `dv7/toy/world_A/exp/runs/RUN-GFPN-a379b4` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 451 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 452 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 453 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 454 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 455 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 456 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 457 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 458 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 459 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 460 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 461 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 462 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 463 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 464 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 465 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 466 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 467 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 468 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 469 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 470 | `dv7/toy/world_A/exp/runs/RUN-GFPN-bf7c41` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 471 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t0` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 472 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t1` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 473 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t2` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 474 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t3` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 475 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t4` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 476 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t5` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 477 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t6` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 478 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t7` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 479 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t8` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 480 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t9` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 481 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t10` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 482 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t11` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 483 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t12` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 484 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t13` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 485 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t14` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 486 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t15` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 487 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t16` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 488 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t17` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 489 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t18` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 490 | `dv7/toy/world_A/exp/runs/RUN-GFPN-dfe748` | v2_driver.solve | `raw_t19` | 0333251e6ebb | none | False | n/a | n/a | n/a | n/a | n/a | n/a |
| 491 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_raw_x` | 84c80057e514 | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 492 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_raw_u` | 78ce47f76a78 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 493 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_S3` | b7c2aec257a4 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 494 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_S3_rescaled` | ade0308b662b | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 495 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_torsion_S3_norm` | 201812d43b7c | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 496 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_torsion_S3_rq` | 4baa667bbef5 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 497 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_raw_x` | a6187802ea6f | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 498 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_raw_u` | 4a0aacd842bd | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 499 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_S3` | c6ffbdf11462 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 500 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_S3_rescaled` | 6e005f1b4b37 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 501 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_torsion_S3_norm` | 64f7fe95d895 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 502 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_torsion_S3_rq` | 4bdba858f220 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 503 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_raw_x` | 441286fd1641 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 504 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_raw_u` | a260a14727f5 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 505 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_S3` | 0b826a955bf8 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 506 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_S3_rescaled` | cd0ea21d0d43 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 507 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_torsion_S3_norm` | b9d29cb8c0e3 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 508 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_torsion_S3_rq` | d4b7d575a576 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 509 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_raw_x` | 8ff2d23f552c | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 510 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_raw_u` | 658094488ecd | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 511 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_S3` | c64559085efb | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 512 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_S3_rescaled` | 92fae5959205 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 513 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_torsion_S3_norm` | 474178c25c83 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 514 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_torsion_S3_rq` | 332ee8496348 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 515 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_raw_x` | 3c9855ee4ad2 | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 516 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_raw_u` | 7b2d971242c2 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 517 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_S3` | 12337eae1056 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 518 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_S3_rescaled` | 5ade3f32ffa1 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 519 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_torsion_S3_norm` | 4a2734dc2c2f | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 520 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_torsion_S3_rq` | 49eb0b2170e7 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 521 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_raw_x` | b9bc99f4a96c | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 522 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_raw_u` | a58b0f283ef5 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 523 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_S3` | 9d782351728a | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 524 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_S3_rescaled` | bc2f6065bfc1 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 525 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_torsion_S3_norm` | b6a14a7a31ce | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 526 | `dv7/toy/world_A/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_torsion_S3_rq` | 1f2b7f6c1bd9 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 527 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_raw_x` | 84c80057e514 | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 528 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_raw_u` | 78ce47f76a78 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 529 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_S3` | b7c2aec257a4 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 530 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_S3_rescaled` | ade0308b662b | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 531 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_torsion_S3_norm` | 201812d43b7c | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 532 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg0_torsion_S3_rq` | 4baa667bbef5 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 533 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_raw_x` | a6187802ea6f | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 534 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_raw_u` | 4a0aacd842bd | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 535 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_S3` | c6ffbdf11462 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 536 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_S3_rescaled` | 6e005f1b4b37 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 537 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_torsion_S3_norm` | 64f7fe95d895 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 538 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_reg1_torsion_S3_rq` | 4bdba858f220 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 539 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_raw_x` | 441286fd1641 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 540 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_raw_u` | a260a14727f5 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 541 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_S3` | 0b826a955bf8 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 542 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_S3_rescaled` | cd0ea21d0d43 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 543 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_torsion_S3_norm` | b9d29cb8c0e3 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 544 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh1_torsion_S3_rq` | d4b7d575a576 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 545 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_raw_x` | 8ff2d23f552c | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 546 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_raw_u` | 658094488ecd | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 547 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_S3` | c64559085efb | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 548 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_S3_rescaled` | 92fae5959205 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 549 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_torsion_S3_norm` | 474178c25c83 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 550 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_fresh2_torsion_S3_rq` | 332ee8496348 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 551 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_raw_x` | 3c9855ee4ad2 | param | True | 6 | 0 | 0 | 6 | 6 | True |
| 552 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_raw_u` | 7b2d971242c2 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 553 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_S3` | 12337eae1056 | param | True | 3 | 0 | 0 | 3 | 3 | True |
| 554 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_S3_rescaled` | 5ade3f32ffa1 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 555 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_torsion_S3_norm` | 4a2734dc2c2f | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 556 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted0_torsion_S3_rq` | 49eb0b2170e7 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 557 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_raw_x` | b9bc99f4a96c | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 558 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_raw_u` | a58b0f283ef5 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 559 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_S3` | 9d782351728a | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 560 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_S3_rescaled` | bc2f6065bfc1 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 561 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_torsion_S3_norm` | b6a14a7a31ce | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 562 | `dv7/toy/world_B/exp/runs/RUN-GFPN-f6a21a` | v2_driver.solve | `fx_planted1_torsion_S3_rq` | 1f2b7f6c1bd9 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 563 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg0_raw_x` | c398cc583a85 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 564 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg0_S3` | 9722975bcce1 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 565 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg0_torsion_S3_norm` | 995cf3b337f7 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 566 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg0_torsion_S3_rq` | 7985f9bab2b1 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 567 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_raw_x` | 8d8354c437ba | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 568 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_raw_u` | 86eb395f84e1 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 569 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_S3` | a4b67f5e8ed5 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 570 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_S3_rescaled` | 64514c378473 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 571 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_torsion_S3_norm` | 795f92987565 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 572 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_reg1_torsion_S3_rq` | 87e8f1d37a33 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 573 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_raw_x` | b0f8eee7e2ba | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 574 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_raw_u` | 8c357c580370 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 575 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_S3` | f9bb0fc730f4 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 576 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_S3_rescaled` | 68f34cc356a4 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 577 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_torsion_S3_norm` | 0ad66a633a2c | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 578 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh1_torsion_S3_rq` | 52994942fe8c | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 579 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_raw_x` | 35f61d5c8b36 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 580 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_raw_u` | 1bc6c7d36724 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 581 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_S3` | 0f6e48b9fd47 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 582 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_S3_rescaled` | 65564c251973 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 583 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_torsion_S3_norm` | 706fcfab9de8 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 584 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_fresh2_torsion_S3_rq` | 76453ecb9124 | param | True | 1 | 0 | 0 | 1 | 1 | True |
| 585 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_raw_x` | ed3ebbb7b600 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 586 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_raw_u` | e079c6498a30 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 587 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_S3` | c395b4ffabf5 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 588 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_S3_rescaled` | 379c7c0908c4 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 589 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_torsion_S3_norm` | a5b24e334e28 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 590 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted0_torsion_S3_rq` | 5d522ff750ff | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 591 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_raw_x` | 7a6743455955 | param | True | 0 | 0 | 0 | 0 | 0 | True |
| 592 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_raw_u` | c10873c36461 | param | True | 24 | 0 | 0 | 24 | 24 | True |
| 593 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_S3` | 799c3c50a117 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 594 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_S3_rescaled` | e11dc62c49f9 | param | True | 4 | 0 | 0 | 4 | 4 | True |
| 595 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_torsion_S3_norm` | 7661c8ecb6d1 | param | True | 2 | 0 | 0 | 2 | 2 | True |
| 596 | `dv_attempts/dv7_attempt2_toyG2_persistent_ssf_at_1039_and_accounting_dir_crash/dv7/toy/world_A/exp/runs/RUN-GFPN-902222` | v2_driver.solve | `fx_planted1_torsion_S3_rq` | 791468e5c9b6 | param | True | 2 | 0 | 0 | 2 | 2 | True |

Violations: 0. Integrity / location / classification agreement: all true (`dv15/dv15.json`).

## 12. DV-17 (launchcover CG-5 (a)-(g); CC-8 (b), (d))

- **Harness.** `<scratchpad>/r3/dev/dv17.py`, outside the layer (RD-2); attempt 1 was a harness defect before any child (RD-11).
- **Settings (declared before any callgrind child).** R = 10 (declared); cap 10737418240; timeout 1800 s (`trial-plan-v2.json watchdogs.callgrind_timeout_s.m3`); calls spaced at least 2.0 s apart; one call at a time on a quiet machine.
- **Inputs.** 36 inputs verified against the TASK-20260923-0fa03f post-run receipt and the archived entries, then copied to scratch. Prime(s): [4111] (the REG-1 reference prime; CG-5 (f)).
- **Run.** Started 2026-09-24T12:08:42.682262Z; finished 2026-09-24T12:31:47.146284Z; 360 calls.
- **Result.** Compared-field differences: none. **DV-17: PASS.**
- **Bounds (CC-8 (d), derived and never measured).** Bound 1 is 1334.4 s; bound 2 is 648000 s. The measured wall span is in `dv17/dv17.json`.

| # | entry tag | reference: method / label / child outcome / returncode / getrlimit / reason / f4_core_function / f4_core_note | calls | calls equal on every compared field | child outcomes | getrlimit read-backs | log-visible SSF indicator (CG-3) | scratch output byte-equal to archived ac4487 output (calls) | classification (development observation) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | `fx_reg0_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 1 | `fx_reg0_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 2 | `fx_reg0_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 3 | `fx_reg0_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 4 | `fx_reg0_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 5 | `fx_reg0_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 6 | `fx_reg1_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 7 | `fx_reg1_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 8 | `fx_reg1_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 9 | `fx_reg1_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 10 | `fx_reg1_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 11 | `fx_reg1_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 12 | `fx_fresh1_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 13 | `fx_fresh1_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 14 | `fx_fresh1_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 15 | `fx_fresh1_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 16 | `fx_fresh1_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 17 | `fx_fresh1_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 18 | `fx_fresh2_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 19 | `fx_fresh2_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 20 | `fx_fresh2_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 21 | `fx_fresh2_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 22 | `fx_fresh2_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 23 | `fx_fresh2_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 24 | `fx_planted0_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 25 | `fx_planted0_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 26 | `fx_planted0_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 27 | `fx_planted0_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 28 | `fx_planted0_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 29 | `fx_planted0_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 30 | `fx_planted1_raw_x` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 31 | `fx_planted1_raw_u` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 9 | ok |
| 32 | `fx_planted1_S3` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 33 | `fx_planted1_S3_rescaled` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 34 | `fx_planted1_torsion_S3_norm` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |
| 35 | `fx_planted1_torsion_S3_rq` | valgrind callgrind (Ir) / measured work proxy (instructions) / ok / 0 / {"soft": 10737418240, "hard": 10737418240} / (absent) / ???:core_f4 [/usr/lib/x86_64-linux-gnu/libneogb-0.6.5.so] / (absent) | 10 | 10 | ok | {"soft": 10737418240, "hard": 10737418240} | False | 10 | ok |

- **Over all 360 calls:**
  - 0 other solver processes were seen before any launch;
  - the minimum spacing between one call's end and the next call's start was 2.006 s;
  - the total child wall time was 623.0 s (measured, a harness value);
  - the CG-3 log-visible SSF indicator was false in all 360;
  - 359 of 360 scratch outputs were byte-equal to the archived output (section 14).
- **Disclosed limit (CG-5 (e)).** A PASS says nothing about SSF events in callgrind children.

## 13. Child launches and their RLIMIT_AS read-backs (every capped child of this stage)

- Every msolve, valgrind, gp, builder and Sage child of this stage was launched by frozen code (`v2_solver.run_child`)
  or by the layer's configuration code. RLIMIT_AS 10737418240 was set in the child and read back with getrlimit.
- The table counts read-back RECORDS per scratch output directory (a child can be recorded in more than one file) and
  lists every distinct value seen.
- msolve always ran with `-t 1`. One memory-heavy process ran at a time, and every check ran detached or in sequence.
- Records under `dv6/` and `dv8/` are mostly byte copies of RUN-GFPN-ac4487's archived records, used by the R-2 /
  REG-1 cases; those children ran in the frozen v2 stage, not in this one.
- `dv11_extra/` and `dv15/` re-read package records.
- A null row is the row of a refused launch, which started no child.
- Every non-null value found is {soft 10737418240, hard 10737418240}.
- This stage's own capped children:
  - DV-1: one Sage probe child;
  - DV-2: two gp children (RC-5);
  - DV-7: the toy ladder gp children and the lineage children (562 + 2 msolve, 90 valgrind, 1 gp and 194 builders in
    attempt 5; section 8);
  - DV-12 and DV-16: the case children;
  - DV-17: 360 valgrind children.

  Each of them read back 10737418240 / 10737418240.

| scratch directory | read-back records | distinct values |
| --- | --- | --- |
| `dv1/` | 1 | {"hard": 10737418240, "soft": 10737418240} x1 |
| `dv11_extra/` | 149 | {"hard": 10737418240, "soft": 10737418240} x149 |
| `dv12/` | 1511 | {"hard": 10737418240, "soft": 10737418240} x1511 |
| `dv15/` | 249 | {"hard": 10737418240, "soft": 10737418240} x249 |
| `dv16/` | 925 | {"hard": 10737418240, "soft": 10737418240} x925 |
| `dv17/` | 360 | {"hard": 10737418240, "soft": 10737418240} x360 |
| `dv2/` | 2 | {"hard": 10737418240, "soft": 10737418240} x2 |
| `dv6/` | 576 | {"hard": 10737418240, "soft": 10737418240} x576 |
| `dv7/` | 2099 | null (a refused launch: no child) x18; {"hard": 10737418240, "soft": 10737418240} x2081 |
| `dv8/` | 1261 | {"hard": 10737418240, "soft": 10737418240} x1261 |
| `dv_attempts/` | 1947 | null (a refused launch: no child) x64; {"hard": 10737418240, "soft": 10737418240} x1883 |

## 14. Deviations and implementation readings (disclosed)

RD-1 and RD-2 are written here for the first time. They were not written to this note before this section.

- **RD-1 (reading, VA-7).** The "site value" of VA-7 is a site-record field (census M-3). Derived tokens are
  disclosed, not treated as a STOP (section 6).
- **RD-2 (placement).** The development harnesses that must launch through frozen code live OUTSIDE
  `implementation-v2-r3/`, in `<scratchpad>/r3/dev/`, and are bundled. This keeps the r3 layer free of launch sites
  (CC-1 / DV-11). They are:
  - DV-17 (`dv17.py`);
  - the DV-7 continuations (`dv7_resume.py`, `dv7_resume5.py`);
  - the supplementary helpers `dv11_extra_g2.py` and `readbacks.py`;
  - the bundle builder `make_bundle.py`.
- **RD-3 (DV-6 attempt 1; implementation defect).** R-13 read `repair.<key>`, but the plans nest the ids at
  `repair.amendments.<key>`. Fixed; attempt 1 preserved.
- **RD-4 (DV-1 static attempt 1; harness).** `callgrind_annotate` prints its version on stderr. Preserved.
- **RD-5 (DV-7 attempt 1; harness).** Layer files were added during the lineage, and R-6 correctly refused. Preserved.
- **RD-6 (DV-7 attempt 2; harness reasons).** Two reasons: the toy G2 at 1039 was persistently SSF, which blocked the
  lineage at R-7; and a missing accounting directory crashed step (4).
  - The continuation reuses the RECORDED SE-5 packages; the probe was not re-run.
  - The live trace keeps attempt 2's steps (1)-(2) records only; its step-(3) records are in the preserved copy.
  - Toy G2 prime for the continuation, declared before launch: 65539 (the smallest prime >= 2^16 that is 1 mod 3).
- **RD-7 (stray byte-code; executor error).** An inspection command imported `r3_common` without `-B` and wrote
  `implementation-v2-r3/__pycache__/r3_common.cpython-311.pyc` at 11:28:50Z. It was inside the write scope and
  untracked.
  - R-6 correctly refused every launch of DV-7 attempt 3 because of it.
  - Removed at 11:35Z; every later inspection command uses `-B`.
  - Attempt 3 also crashed on a harness import-path defect.
- **RD-8 (DV-7 attempts 4-5).** At the declared 65539, every toy G2 msolve child crashed (SIGSEGV). By the declared
  rule, no further prime was tried. Attempt 5 continued the lineage on a SYNTHETIC toy G2 gate row (consequence in
  section 9).
- **RD-9 (DV-13 evaluation).** Attempt 4's raw `dv13_pass` counted refused launches, which have no driver and no
  package. Attempt 5 evaluates DV-13 over every toy package with a manifest, which is the text of DV-13 ("in every
  toy package").
- **RD-10 (DV-16 attempt 1; harness defect).** The shared case runner set the REG-1 reference id only in the child
  configuration; DV-12's G1 packages never evaluate REG-1.
  - The fix is in `r3_dv16.py` only, from sha256 b9b9667a…860e39 to the value in section 2.
  - `r3_dv12.py` is byte-unchanged, so DV-12's bound bytes stand. Attempt 1 preserved.
- **RD-11 (DV-17 attempt 1; harness defect).** The receipt path was wrong. The run stopped at start-up, before any
  child. Preserved.
- **RD-12 (DV-17 classification record).** DV-17 records the characterization classification of each scratch output
  as outcome, SSF flag, parse kind and byte-equality with the archived ac4487 output. It records no D, no degree and
  no count (outcome blindness).
- **RD-13 (bundle redaction; section 15).** In text members, three strings are replaced:
  - the scratchpad's absolute path -> `<scratchpad>`;
  - the git branch name -> `<branch>`;
  - the runtime-instructions filename that appears in byte copies of the frozen amendment texts ->
    `<runtime-instructions-file>`.

  Each redacted member's row carries both sha256 values. Binary members containing any of the three strings, and the
  frozen drivers' build caches, are not bundled; they are listed.
- **RD-14 (DV-15 table).** Degree columns are omitted from the note and kept in the bundle.
- **Observations (recorded, never evidence):**
  - msolve 0.6.5 crashed (SIGSEGV) on the toy fixture systems at p = 65539.
  - At p = 1039, the toy raw_u / S3_rescaled systems kept the SSF signature through K = 5.
  - The frozen `a1_check_run.py` lines 51-57 byte-sweep for the frozen v2 task id (frozen, V-4).
  - The DV-12 log prints toy D values; they are harness values of toy packages.
  - In DV-17, 359 of the 360 scratch outputs are byte-equal to the archived RUN-GFPN-ac4487 output. One is not: entry
    31 `fx_planted1_raw_u`, call 4. It was classified ok with no NSP signature. It is not a REG-1-compared field of
    DV-17, and CG-5 (e) anticipates ordinary clock-seed variation. It is recorded as a development observation.

## 15. Scratch files, DV-9 and the evidence bundle

**Scratch files** (all under `<scratchpad>/r3/`; nothing else outside the repository was written):

| path | content |
| --- | --- |
| `dv1/`, `dv2/`, `dv3/`, `semantics/`, `dv5/`, `dv6/`, `dv8/`, `dv9/`, `dv10/`, `dv11/`, `dv12/`, `dv15/`, `dv16/`, `dv17/` | the raw outputs of each check (JSON records, worker stdout / stderr, toy and case package directories) |
| `dv7/` | the DV-7 toy environment: both SE-5 worlds with every `solver-events.json`, the attempt-5 lineage, the trace, the resumed toy plan and fixture data, and `dv14_attempt2_toyG2_gaps.json` |
| `dv11_extra/`, `dv15_supp_dv12_dv16/` | the supplementary (report-only) count and accounting outputs |
| `dv_attempts/` | every failed or superseded attempt, preserved with a `REASON.txt`: `dv1_attempt1_*`, `dv6_attempt1_*`, `dv7_attempt1_*` .. `dv7_attempt4_*`, `dv16_attempt1_*`, `dv17_attempt1_*` |
| `ids/` | `mint.log`, `check.log`, `ids.txt` (DV-10) |
| `dev/` | the development harnesses outside the layer (RD-2), the inventory's development copy, the read-back aggregator, the bundle builder, and this note's assembly script and drafts |
| `*.log` | the detached checks' console logs |

**DV-9 (SC-6; 12:33:09Z; PASS)** against the baseline taken at 10:47:35Z, before any write, with stage start
10:42:19Z:
- 454 baseline files under 31 frozen roots: 0 changed, 0 added, 0 removed.
- Receipt equalities all equal: TASK-20260923-0fa03f phase A (14 paths) and phase B (345), TASK-20260923-4ff597 phase
  A (12), the stage-R1 and stage-r2 preservation receipts (17, 19), the seedresolve and launchcover premise checks, the
  consumer census and the launch census (3 each).
- The nine amendment hashes are equal.
- `implementation/ladder.json` is unchanged (7e42961d…cb327c).
- Byte-code: the 5 pre-existing files are unchanged, and none is later than the stage start. The stray file of RD-7
  was removed before this check.
- `git status`: no path outside the write scope, and no tracked modification.
- `runs/`: 51 entries, no new run directory.
- HEAD 5505464a92ed6c78e8155615cb6cde00d3ee49ae (unchanged).

After DV-9, the only writes were the bundle and this note (both inside the write scope).

**Evidence bundle (VA-5; R3S-12):** `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r3-dv/stage-r3-dv-evidence.tar.gz`.
- sha256 b1100521dd2ceb5df5a6afbd4db79c9883db6f0330d4e681bc7eeab3ea7cd07d; 14739055 bytes.
- 21133 members: 21131 data members, `stage-r3-dv/MEMBERS.sha256` (member list with each member's sha256 and size)
  and `stage-r3-dv/REDACTION.txt`.
- It holds the raw outputs of every check:
  - DV-1;
  - DV-7 (both SE-5 worlds, with every `solver-events.json`);
  - DV-11 (launch list, counts and the R3S-10 inventory);
  - DV-12 (a)-(g), DV-13, DV-14, DV-15 and DV-16 (a)-(e);
  - DV-17 under `dv17/`;
  - every preserved attempt.
- It was built deterministically: sorted names, mtime 0, uid / gid 0, gzip mtime 0.
- 0 members over 50 MiB, so nothing is kept back for size.
- 0 members left out for containing a redacted string.
- The frozen drivers' derived build caches (7 `cache/` directories) are not bundled; they are rebuilt by the commands.
- **Redaction (RD-13).** In 2186 text members, the scratchpad path, the git branch name and the runtime-instructions
  filename were replaced by placeholders. Each such member's row also gives the scratch (unredacted) sha256.
- Verified after writing: every member's sha256 equals its MEMBERS.sha256 row (0 mismatches), and a case-insensitive
  search of the extracted bundle for the model, vendor and runtime names, the branch name and `/tmp/` finds 0 files.


## 16. Allocator and --check outputs (DV-10)

- The 42 ids were minted at 10:48:46Z with `tools/allocate_id.py --next run --area GFPN`, and each BARE id was checked
  with `--check` (rc 0, 0 occurrences) before any file named it.
- The verbatim outputs are in `<scratchpad>/r3/ids/` (`mint.log`, `check.log`, `ids.txt`) and in the bundle under
  `ids/`.
- The ids, in minting order, are `implementation-v2-r3/minted-run-ids.txt`.
- The retirement lists (124 = 29 v2 + 11 v2-a1 + 42 r1 + 42 r2) are in both plans' `retired_ids` and in
  `r3_common.RETIRED_ALL`.
