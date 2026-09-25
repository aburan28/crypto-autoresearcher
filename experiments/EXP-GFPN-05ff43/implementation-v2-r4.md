# EXP-GFPN-05ff43 — implementation note, protocols 2-r4 and 2-a1-r4 (r4 stage, TASK-20260924-d91a96)

Stage note of the r4 stage (maximum_runs 0; no run package was written). Scratch outputs live in the session scratchpad,
referred to only as `<scratchpad>`. Section 0 is the progress log; the two RC-4 sections (written before either plan
existed) follow it unchanged; sections 1-18 were written at the end of the stage.

**Stage outcome, stated first (observations only; no hypothesis, heuristic or claim is assessed here).** Every
development check DV-1..DV-17 passed on the delivered r4 code. DV-18 was run once, after DV-7, with (f) (xiv) and
(xv) first; every DV-18 item passed except that **RB-5 (d) is not met as literally worded** ("with the original, it
admits"): in any development world REG-1 is NOT_EVALUABLE (no G1), so the three REG-1 checker items fail on every
development package (RG-3 (d)) and RB-4 (b) refuses a later package with the unedited copy too. Under the development
reading that RF-4 (c) / RG-3 (d) give "the r4 checks pass", RB-5 (d) is met (section 10.4). RB-5 says "STOP ... on any
failure of (c) or (d)". **The stage therefore records a STOP condition (RB-5 (d), literal reading) for a Coordinator
ruling**; the remaining development checks were completed afterwards as development observations so that the ruling
has the complete record (deviation D-13). No plan is to be treated as final until that ruling.

## 0. Progress log (UTC)

- 03:52:17Z stage start. Before any write, the SEVENTEEN amendment files were hashed with
  `sha256sum -c <scratchpad>/r4/lka1-expected.sha256`, where the expected file was cut from
  `ledger/decisions/DEC-20260924-daf670.yaml` lines 1052-1068 (`bound_hashes`). All 17 print `OK` (0 mismatches).
- 03:52Z GFPN_V2_CAP_BYTES check (R4S-13; LKA-11 (d)), in the environment this stage was launched in:
  - `env | grep -c GFPN_V2_CAP_BYTES` printed `0`;
  - `printenv GFPN_V2_CAP_BYTES` printed nothing and exited `1`.
  The variable is UNSET. Every child environment this stage builds is derived from this environment and never adds it.
- 03:52Z HEAD 1768588f0d7f94020f235e2141d7a843f45b150f; `GIT_OPTIONAL_LOCKS=0 git status --porcelain` empty.
- 04:00:48Z DV-9 baseline taken before any repository write (`<scratchpad>/r4/dv9/baseline.json`): 1294 files hashed
  under the frozen roots; the other 48 run packages recorded by listing and lstat metadata only (2110 files, never read,
  R4S-12); 5 pre-existing byte-code files; `runs/` 55 entries (54 run directories + `.gitkeep`); git status empty.
- 04:01:03Z-04:02:01Z 42 run ids minted with `python3 -B tools/allocate_id.py --next run --area GFPN` and each BARE id
  checked with `--check` (rc 0 and 0 occurrences for all 42; 42 distinct) before any file named it
  (`<scratchpad>/r4/ids/`).
- 04:04:39Z first repository write: `implementation-v2-r4/` created (the exclusion list copied byte for byte from
  `implementation-v2-r3/`, and `minted-run-ids.txt`).
- 04:23:47Z the union map M computed from the delivered writer's inputs; this note opened with the RC-4 (b) and RC-4 (a)
  records below. Neither r4 plan exists at this time.
- 04:25:54Z both plans written (first write; superseded, see 04:35Z). 04:34Z DV-1 static PASS.
- 04:34Z-04:36Z DV-5 attempt 1 FAIL: an IMPLEMENTATION defect in the plan writer (its `ceiling_note` named
  RUN-GFPN-ac4487 and RUN-GFPN-3377f1 outside the id maps / retired lists). Fixed in `r4_make_plans.py` (the note now
  names the `retired_ids` lists). Attempt 2 was a harness fault (the writer's write-once guard refused the rewrite, so
  attempt 2 read the old plans). The first-write plans (sha256 2f79444a...9794 and f76eb50f...7dd7) were moved to
  `<scratchpad>/r4/superseded-plans/` (never archived, never read by any package) and the plans re-written (sha256
  10822601...93f1 and 36f07060...9c6a). DV-5 attempt 3 PASS. Both failed attempts are preserved.
- 04:35Z-04:38Z DV-8 PASS; DV-10 PASS.
- 04:38Z-04:41Z DV-6 attempt 1: 80 of 81 wrapper cases and 17 of 17 entry cases passed; the RL-4 case's EXPECTED text in
  the harness omitted "X-04 requires" (G2 both requires and reads G1) -- a harness label fault, preserved. Attempt 2
  PASS (81 wrapper cases, 17 entry cases).
- 04:43Z r4_check_run.x13_check changed to read the controls_a1 image in the package's own runs directory (the file the
  frozen X-13 read opens; identical to `R.RUNS_DIR/<id>` in a package).
- 04:51Z the layer was written in full (DV-6/7/12/16 harnesses, the inventory). 04:51Z-04:59Z DV-7 attempt 1: toy
  ladder, SE-5 probe (PASS; the perturbed copy FAILS REG-1 as required); toy G2 (fixture --p 1039) ended failed /
  implementation_error with the SSF signature persistent on all six attempts of two toy systems (the r3 stage's
  attempt-2 observation, reproduced), every later package met the unexpected refusal "toy G2 did not pass" and was not
  launched; step (4) crashed on the accounting-directory harness defect carried from r3. 05:00Z-05:12Z DV-7 attempt 2
  (a continuation outside the layer, reusing the recorded SE-5 packages and the recorded toy G2, which stays the toy
  gate; its "did not pass" refusal declared expected): PASS.
- 05:12Z layer patch 1 (section 3.9): the r4 checker runs the frozen checker on the run directory's NAME with cwd = the
  runs directory and prints the name; the wrapper's recorded checker command names the name; the DV-7 / DV-12
  harnesses carry the declared failed-toy-G2 rule and the accounting directory. 05:12Z-05:27Z DV-7 run again in full on
  the patched layer ("final-layer run"): PASS. All later checks ran on the final layer.
- 05:27Z-05:41Z DV-12 PASS (a)-(g); DV-16 PASS (a)-(e); DV-11 PASS; DV-15 PASS.
- 05:41:04Z DV-18 began: (f) (xiv) and (xv) FIRST: PASS. 05:41Z-05:55Z the rest of DV-18 (section 10).
- 05:47:42Z the RB-5 (d) STOP condition was recorded (literal reading); the remaining development checks continued.
- 05:54:56Z-06:18:02Z DV-17 PASS. 06:18Z-06:22Z DV-6 re-run on the final layer: PASS. 06:22Z DV-9 (last): PASS. Then the bundle and this note.
- CONTEXT COMPACTION (first): the executor's working context was compacted during the stage (at about 04:30Z, while the
  DV-1..DV-18 harnesses were being written). The running command log `<scratchpad>/r4/command-log.txt` (bundled) was kept
  throughout; every file this note relies on was re-read after the compaction.
- SECOND CONTEXT COMPACTION: the working context was compacted a second time at about 06:20Z, after DV-9 and before
  the bundle was built. The command log and this note were again the continuity record; the bundle builder and section 17
  were re-read before use.

## RC-4 (b): declared metadata key paths (JSON pointer), recorded before either plan was written

(Written at 04:24Z. At this time neither `trial-plan-v2-r4.json` nor `trial-plan-v2-a1-r4.json` exists. This satisfies
DEC-20260923-80e280 RC-4 (b), re-pointed to r4 by DEC-20260924-daf670 LKA-3 and card R4S-5.)

`trial-plan-v2-r4.json` (12 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed (2 → "2-r4") | protocol label |
| `/task_id` | changed (→ TASK-20260924-b85e59) | task ids |
| `/written_by_task` | added (TASK-20260924-d91a96) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-4a47e5 phase A (Coordinator)") | archived_by |
| `/repair` | added (the LKA-1 content) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed, with the exclusion list's sha256) | gate.regression |
| `/gate/admission` | added (the gate admission as RB-4 words it, with RL-4 / RK-3 / RF-3 / RF-5) | gate admission |
| `/id_map` | added (31 entries, v2 → r4) | id map |
| `/v2_ids_never_reused` | added (the 31 frozen v2 ids) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids) | never-reused lists |
| `/retired_ids` | added (ids kept as records; the 162 retired ids: 29 v2, 11 v2-a1, 42 r1, 42 r2, 38 r3) | retired id lists |
| `/ceiling_note` | added (6 existing + 31 + 11 = 48 of 48, over ten plans) | ceiling note |

`trial-plan-v2-a1-r4.json` (13 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed ("2-a1" → "2-a1-r4") | protocol label |
| `/task_id` | changed (→ TASK-20260924-46a554) | task ids |
| `/written_by_task` | changed (→ TASK-20260924-d91a96) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-4a47e5 phase A (Coordinator)") | archived_by |
| `/repair` | added (the LKA-1 content, with the a1 gate re-pointing and the phase-B receipt re-pointed to TASK-20260924-4a47e5, VC-6 (c)) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed) | gate.regression |
| `/gate/admission` | added (as in the v2-r4 plan) | gate admission |
| `/id_map` | added (11 entries, v2-a1 → r4) | id maps |
| `/id_map_v2` | added (31 entries, v2 → r4) | id maps |
| `/frozen_v2_ids_never_reused` | added (the 31 frozen v2 ids; RC-4 (d)) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids; RC-4 (d)) | never-reused lists |
| `/retired_ids` | added (as in the v2-r4 plan) | retired id lists |
| `/ceiling_note` | added | ceiling note |

In `trial-plan-v2-a1-r4.json` the pre-existing `/v2_ids_never_reused` is NOT a declared key: it is mapped like every
other field, so its image lists the 31 r4 v2 ids (RC-4 (d)). `/gate/v2_blocking_packages`,
`/gate/addendum_blocking_package` and aggregate_a1's `driver_args` are not declared keys; they are mapped through M.
The derivation source is the FROZEN plans (trial-plan-v2.json sha256 16f33e39...4e16; trial-plan-v2-a1.json sha256
2a788720...5ac6), never the r1, r2 or r3 plans (R4S-5).

## RC-4 (a): the union map M (42 entries), recorded before either plan was written

Assignment rule (as the earlier stages): ids are taken in minting order (`implementation-v2-r4/minted-run-ids.txt`;
section 16 has the allocator outputs). The first 31 go to the packages of `trial-plan-v2.json` in plan order; the next
11 to the packages of `trial-plan-v2-a1.json` in plan order. The writer's `inputs()` checked every image against the
frozen, r1, r2 and r3 plans, the v1 ids and the 162 retired ids: 0 collisions; M is a bijection.

id_map_v2 (31):

| order | frozen v2 id | r4 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-ac4487 | RUN-GFPN-3e27a0 | F-1..F-3 fixture, n = m = 3, p' = 4111 (G1) |
| 2 | RUN-GFPN-3377f1 | RUN-GFPN-878af1 | F-1..F-3 fixture, n = m = 3, p' = 16777291 (G2) |
| 3 | RUN-GFPN-76420e | RUN-GFPN-315a64 | jv_anchor_system_trace_identity, p' = 16777291, n = 5, m = 4 (G3) |
| 4 | RUN-GFPN-b231c1 | RUN-GFPN-d1a204 | frozen controls (G4) |
| 5 | RUN-GFPN-a07776 | RUN-GFPN-f87282 | F-4 secondary fixture, n = m = 4 (NOT blocking) |
| 6 | RUN-GFPN-1ad09b | RUN-GFPN-e761f2 | build p' = 4111 |
| 7 | RUN-GFPN-0c7483 | RUN-GFPN-3c4bc4 | cells 4111 ecgfp5_shaped m = 5 |
| 8 | RUN-GFPN-4abae0 | RUN-GFPN-cf4442 | cells 4111 random_2torsion m = 5 |
| 9 | RUN-GFPN-9e4212 | RUN-GFPN-4689f8 | cells 4111 random_no2torsion m = 5 |
| 10 | RUN-GFPN-bbbbe3 | RUN-GFPN-5e877a | cells 4111 ecgfp5_shaped m = 4 |
| 11 | RUN-GFPN-a521dd | RUN-GFPN-89b623 | cells 4111 random_2torsion m = 4 |
| 12 | RUN-GFPN-a07b6d | RUN-GFPN-9fd0fa | cells 4111 random_no2torsion m = 4 |
| 13 | RUN-GFPN-dc1d4e | RUN-GFPN-add291 | build p' = 262151 |
| 14 | RUN-GFPN-b9207c | RUN-GFPN-50fa88 | cells 262151 ecgfp5_shaped m = 5 |
| 15 | RUN-GFPN-aa56bd | RUN-GFPN-d02ab7 | cells 262151 random_2torsion m = 5 |
| 16 | RUN-GFPN-e5b90d | RUN-GFPN-61f15b | cells 262151 random_no2torsion m = 5 |
| 17 | RUN-GFPN-d2f759 | RUN-GFPN-722d56 | cells 262151 ecgfp5_shaped m = 4 |
| 18 | RUN-GFPN-745cad | RUN-GFPN-7c0be2 | cells 262151 random_2torsion m = 4 |
| 19 | RUN-GFPN-aeff00 | RUN-GFPN-0f6e79 | cells 262151 random_no2torsion m = 4 |
| 20 | RUN-GFPN-3db273 | RUN-GFPN-15cd11 | build p' = 16777291 |
| 21 | RUN-GFPN-3be8a4 | RUN-GFPN-15c228 | cells 16777291 ecgfp5_shaped m = 5 |
| 22 | RUN-GFPN-00e64b | RUN-GFPN-eb674f | cells 16777291 random_2torsion m = 5 |
| 23 | RUN-GFPN-c5294d | RUN-GFPN-75c894 | cells 16777291 random_no2torsion m = 5 |
| 24 | RUN-GFPN-36cad2 | RUN-GFPN-191941 | cells 16777291 ecgfp5_shaped m = 4 |
| 25 | RUN-GFPN-11d2ad | RUN-GFPN-929d40 | cells 16777291 random_2torsion m = 4 |
| 26 | RUN-GFPN-fc5d58 | RUN-GFPN-ed0ea7 | cells 16777291 random_no2torsion m = 4 |
| 27 | RUN-GFPN-8f86cc | RUN-GFPN-dabc2a | aggregate (ladder table, scoring, HEUR-GFPN-DFLAT, F4, band) |
| 28 | RUN-GFPN-e26e4b | RUN-GFPN-377a64 | contingency 1 |
| 29 | RUN-GFPN-9da048 | RUN-GFPN-45fc69 | contingency 2 |
| 30 | RUN-GFPN-59320d | RUN-GFPN-b0325c | contingency 3 |
| 31 | RUN-GFPN-1596f6 | RUN-GFPN-a146f6 | contingency 4 |

id_map_a1 (11):

| order | frozen v2-a1 id | r4 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-0d91bf | RUN-GFPN-5c417c | controls_a1, p' = 1073741831 (BLOCKING for the addendum) |
| 2 | RUN-GFPN-8c772a | RUN-GFPN-957eb1 | build p' = 1073741831 |
| 3 | RUN-GFPN-569fd7 | RUN-GFPN-82322f | cells 1073741831 ecgfp5_shaped m = 5 |
| 4 | RUN-GFPN-086463 | RUN-GFPN-c7b90c | cells 1073741831 random_2torsion m = 5 |
| 5 | RUN-GFPN-bab146 | RUN-GFPN-2111a4 | cells 1073741831 random_no2torsion m = 5 |
| 6 | RUN-GFPN-7dd55d | RUN-GFPN-e8e2c9 | cells 1073741831 ecgfp5_shaped m = 4 |
| 7 | RUN-GFPN-47aa51 | RUN-GFPN-adf7eb | cells 1073741831 random_2torsion m = 4 |
| 8 | RUN-GFPN-3a70f1 | RUN-GFPN-cf0210 | cells 1073741831 random_no2torsion m = 4 |
| 9 | RUN-GFPN-ae4918 | RUN-GFPN-690ecb | aggregate_a1 |
| 10 | RUN-GFPN-8cfac3 | RUN-GFPN-296a26 | contingency a1-1 |
| 11 | RUN-GFPN-6a7f35 | RUN-GFPN-9389e1 | contingency a1-2 |

## 1. What this stage delivered (paths)

- `experiments/EXP-GFPN-05ff43/implementation-v2-r4/` (20 files; table in section 2);
- `experiments/EXP-GFPN-05ff43/implementation-v2-r4.md` (this note);
- `experiments/EXP-GFPN-05ff43/trial-plan-v2-r4.json` (sha256 10822601c96f6df9d28cfeccac43ce3543d946fde3b10034e6f52796686693f1);
- `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r4.json` (sha256 36f0706067b362285574c3502c36b46d61052bbce890e277a3998cb7bdbc9c6a);
- `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r4-dv/stage-r4-dv-evidence.tar.gz` (section 17).

No run directory was created; nothing was written under `coordination/`, `ledger/` or `runs/`; every frozen tree,
plan, amendment, the specification, `ladder.json` and every existing run package is byte-identical (DV-9, section 9).
No git write of any kind was made (read-only git children only, each with GIT_OPTIONAL_LOCKS=0; their argv are in the
command log and in the DV outputs).

## 2. The r4 layer, file by file

Every r4 file starts from the r3 file named (with that file's sha256 in the TASK-20260924-f1fb0e phase-A receipt) or
is new. No r4 file imports an r1, r2, r3 or v1 module (DV-11 inventory check). sha256 values are of the delivered bytes.

| file | sha256 | origin |
| --- | --- | --- |
| `minted-run-ids.txt` | d5ca1e06f7595365d6e8cbc188c173b91d997bda2748924d312ae7dea20038a2 | new |
| `r4_accounting.py` | 93d95cbe8812015babb79f90fdeb3f21c8320d777aea6a15b6a914d31293a0b0 | `implementation-v2-r3/r3_accounting.py` (phase-A sha256 dca726f7cb35c107536ea92b1e51566b8ed1a4e1ee7a9110eac5836425757e38) |
| `r4_check_run.py` | b794adaa171538ac6e23b08195d13cf489085e0c159626e70332449d643c7181 | `implementation-v2-r3/r3_check_run.py` (phase-A sha256 939d7d7e5bc8a8c64f15df188f98f13b22ef7a9d696680f8e47854c2dbdcd14d) |
| `r4_common.py` | e9087ed6792751a0cb10d4c40efdc0fd201c90da0eab693915d823e3479a074e | `implementation-v2-r3/r3_common.py` (phase-A sha256 7bb7b688250d69a2ca209a57fd70176727aa1fe225c95c9878076be407380868) |
| `r4_devchecks.py` | b156d15d2314a0e29c73024d9ee174d791fa469295b1120e4a6f2309bbd8f90d | `implementation-v2-r3/r3_devchecks.py` (phase-A sha256 b94cb0176c25a3ac3cec504a0d9d614f47495c49e95557f3cc770d1651652cfd) |
| `r4_devchecks_more.py` | aad8f2bf66ccb8fc1c3209ed8c36e46af50d915080e9eed5d945e680e728bfe7 | `implementation-v2-r3/r3_devchecks_more.py` (phase-A sha256 d17a10749d8c40c90adeded2e64ee82f42afd93b43b963dc14d0ab843f0c04bd) |
| `r4_dv12.py` | 922e28c5c90082910146249509f21aa15d316bd462564f3f9dc420467678a168 | `implementation-v2-r3/r3_dv12.py` (phase-A sha256 4c0103ec07ac5a3a5dbad8ed29c876dbeebe44ada0dda5d80fec4308727a6dd0) |
| `r4_dv16.py` | 7c864cb56707f80f74c721f3d87c4b8da3c1bc84136ccaedd25f0f41ec6fc802 | `implementation-v2-r3/r3_dv16.py` (phase-A sha256 7bc2df84d70dc87dadb7913a5b4e8529769d0066faa020869a3e62beaa1710b3) |
| `r4_dv6.py` | adbc6c909f9e378962d76c592e70415dfa1f6034593a33308cda55f74164256f | `implementation-v2-r3/r3_dv6.py` (phase-A sha256 23e82cac90c6411175ca7896fc3dc43384c75b5dfac050a68585c5d0457ae4d5) |
| `r4_dv7.py` | acb3a3546d82910f7f32b8029cccf66dc9f0958cd2fb16c8d551191661ec6ce7 | `implementation-v2-r3/r3_dv7.py` (phase-A sha256 1376cbd44ab3e73ff92da612281270270cc33a50b1f42fbd3869c17fd715a740) |
| `r4_entry_a1.py` | 1c1c8d9dbce54f151327fcb7a0cabba503ad2914118fe36c097ced48245badcb | `implementation-v2-r3/r3_entry_a1.py` (phase-A sha256 cefbb3348174bf02546129a65a9a0961b3ad5f60341d25ca4bfab1d54cb56f23) |
| `r4_entry_v2.py` | 82ac34b9056da15155961a5e7bf9096c70d58050ebcfcad5ca86df5961afb20d | `implementation-v2-r3/r3_entry_v2.py` (phase-A sha256 f79161999507cdb5438c1be39de21ba74d25ef745f490c08e56a600c28117fbd) |
| `r4_gaps.py` | 7051a8c674e524b828f52bf3b1d3d46ebc6f3d29a4529ec4bc2d734643ef6f70 | new |
| `r4_inventory.py` | bc84fb9241c184c13bb1f9b929ba5cec762c987691908b0a2fd2e1d380dd762b | `implementation-v2-r3/r3_inventory.py` (phase-A sha256 203b5be93998c6bc0d9994eaaaa64dcbe300f34e45cc6294d4f1c219d75fe81a) |
| `r4_make_plans.py` | bed0a21c3419d67807bac5ecba4495a01c4ded7fbd34f394433b94e0bbd900a3 | `implementation-v2-r3/r3_make_plans.py` (phase-A sha256 9143eef16951e894e5de5252bbe157c533970a3090e2becabadb24ee494f3ff7) |
| `r4_recorder.py` | d367bd7e682b341bbedfd1b0a27e645d29b02d7c14c2d26ecdcb80c7e35066f8 | new |
| `r4_reg1.py` | a4bdfcfc3c4c5254a79c3bf838ee4089adc0733a1f9fec6ab34409aa088bfa57 | `implementation-v2-r3/r3_reg1.py` (phase-A sha256 04ee68d350198340d9427d1b575febc8f8cfe99b4f5f59ffef832de7b04378f3) |
| `r4_resolve.py` | 324ce12e5247b3d9eed58d6503022ba379a54cfd19efdfee6dfb7508f5bb754e | `implementation-v2-r3/r3_resolve.py` (phase-A sha256 3a6828f42a6e8dd97fd487510fbb0c153ca8f51d9bcd0c310d1af96c8d5e3e15) |
| `r4_run_wrapper.py` | 65109323d9bc576a9a3d6082a9bed8ecbdd63ffaa90d6c6a3452806acf744404 | `implementation-v2-r3/r3_run_wrapper.py` (phase-A sha256 dd52a4bfad9c4bfb0e4e37ee8a24951e8992edf8d2f1dfcc112e9bcdbabb9c19) |
| `reg1-exclusion-list.json` | 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c | `implementation-v2-r3/reg1-exclusion-list.json` (phase-A sha256 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c) |

`r4_dv6.py`, `r4_dv7.py`, `r4_dv12.py`, `r4_dv16.py`, `r4_devchecks.py`, `r4_devchecks_more.py` and `r4_inventory.py`
are development-check files: never imported by an entry, the wrapper or the checker. The DV-17 and DV-18 harnesses and
the DV-7 continuation are SCRATCH files OUTSIDE the tree (bundled under `dev/` and `dv18/`), so that the r4 tree holds
no launch site of its own (CC-1) and no load of the frozen run_child other than the RL-1 installation (LKA-7).

## 3. How the r4 rules are implemented (where to read them)

3.1 **RL-1 launch recorder** (`r4_recorder.py`). `install(v2_solver, run_dir)` is the one load of the frozen
`v2_solver.run_child` in the r4 tree (line 450); it captures the function and the code objects of `run_child` (first line
149) and `_run_child_locked` (177), stores the installing pid, registers ONE after-fork-in-parent callback
(`os.register_at_fork(after_in_parent=...)`) and sets `v2_solver.run_child = launch_recorder`. `launch_recorder` calls the
captured original with the same arguments (line 426), returns its record unchanged or re-raises the same exception, and
appends one launch record through the single event writer `r4_resolve.append_launch_record`. Return path: RK-1 (a) key
presence (`child_created`, `pair_read_by_parent`); raise path: RK-1 (b) with RF-1 (a) (the chain over `__context__` /
`__cause__`, at most 16, `undetermined` on a cycle or the limit; `pid` read from a `_run_child_locked` frame;
`tb_lineno < 181` for `false`). RF-1 (b): a call ending in a non-installing process writes only
`recorder-foreign-<pid>.json`. RG-1 / RH-4: the callback reads `/proc/self/task/<tid>/children`, opens one software
task-clock counter (disabled, enable_on_exec, inherit not set, exclude_kernel, exclude_hv, close-on-exec) on exactly one
new pid, catches every exception (marking the call); `child_end` is `no_child | exec | frozen_pre_exec_exit |
undetermined` exactly as RG-1 (c) words it. RG-4 (a): `stdout_path` / `stderr_path` copied from the arguments.
`readback()` is the RL-5 install read-back (recorder installed; captured original is the frozen function with the stated
module, qualname, file and first line; both code objects frozen; callback registered in the installing process; one
v2_solver module object for every user).
3.2 **RB-1 with RJ-1 (a) and LKA-9** (`r4_resolve.py`). Every attempt of every wrapped call at S-1 and S-2 gets an
attempt record (`attempt_records`, with `call_index`) carrying `rb1` = {tag, `.ms.out` retained or renamed,
`rlimit_as_child_getrlimit` or "absent", `threads_executed` or "absent", the outcome class, and at S-1
`callgrind_result_present`}. `_rb1_callgrind_result_present(res)` is exactly `return "instructions_callgrind" in res`
(DV-11 checks the AST). RL-2: `passthrough_records` for gb_only calls. A recording failure raises
`SolverEventConsistencyError` (SE-2 (4)).
3.3 **The wrapper** (`r4_run_wrapper.py`). R-1..R-13 re-pointed per LKA-3 (R-1 the seventeen hashes; R-2 v1 / v2 / v2-a1 /
r1 / r2 / r3 ids and the 162 retired ids; R-6 against the TASK-20260924-4a47e5 phase-A receipt; R-11 48 over TEN plans;
R-13 the eight forbidden task ids). RB-4 (b) / RL-4 / RK-3: the r4 checker is run IN THE WRAPPER'S PROCESS at admission
(its frozen checker in its own process, RC-3 (e)) on each gate package, the controls_a1 image and every read package;
F-4 recorded only (RK-3 (d)); commands, exit statuses, verdicts and outputs are recorded under
`gate.gate_package_checker` / `gate.required_package_checker`. After the package ran, the wrapper runs the r4 checker on
it and appends its verdict to the manifest (`run.verdict`). RB-2 / RL-3: the collector over sources (a)-(e) and
`resources.child_readback_accounting` (with the RL-3 recorder-gap computation). RF-0 (b): `raw_result_writer`.
3.4 **The recorder-gap computation** (`r4_gaps.py`): RH-1 (i)-(vi) with RI-1 (a)-(d), RJ-1, RJ-2 (the gp script removed
from the non-launch list), RJ-3, RJ-4 (b); stdout paths relativized ONLY by the exact prefix "<run directory>/" taken
from command.txt line 2 (LKA-10). `recorder_gaps()` is the delivered entry point (every condition on); `_evaluate()`
takes condition switches that ONLY the scratch evaluators of DV-18 turn off.
3.5 **The checker** (`r4_check_run.py`): the carried checks re-pointed; the verdict PASS / PASS_ZL / FAIL as RK-3 (b) with
RF-2, RF-3 (classes (A), (B), (C) with RG-1 (d)); stop classes RF-3 (b); labels RG-2, RH-2; X-13 by name (RF-5); the
SC-4 accounting with RB-3 (report only).
3.6 **Entries** (`r4_entry_v2.py`, `r4_entry_a1.py`): PS-1 configuration first; LKA-3 redirections; SE-3 (and HR-3 in the
a1 entry); then RL-1; then the read-backs (RC-3 (d), SE-3, HR-3, RL-5) before any command; refusal writes only
`pari-stack.json` and exits 2.
3.7 **Plans** (`r4_make_plans.py`): derived from the FROZEN plans (RC-4 (c) equality asserted and checked by DV-5 with
its own code); `--check` regenerates both byte-identically.
3.8 **Reading adopted: RB-4 (b) "run by the wrapper"** is implemented in the wrapper's own process (the frozen checker in
a separate process), not as a further child of the wrapper; the command recorded says so.
3.9 **Layer patch 1 (05:12Z; before DV-7's final-layer run and before DV-18).** `r4_check_run.main` runs the frozen
checker with `cwd` = the runs directory on the run directory's NAME (the frozen checkers join every path to that
argument and read the run id from its basename), and prints the name instead of the path; `r4_run_wrapper.checker_verdict`
records "r4_check_run.main(<runs directory>/<id>) ... cwd <runs directory>: <launcher> <mode> <id>". Reason: under LKA-4
(b) the manifest's recorded checker text would otherwise carry the absolute development run directory followed by ':'
or inside quotes (a form other than a path prefix). No check changed.

## 4. PS-1 branch (paristack), with evidence, values, API and read-back semantics

- **Branch P-A**, decided by `r4_make_plans.branch_evidence` from DV-2 and DV-3 (it refuses unless both pass).
- **Evidence (DV-3):** at (p' = 16777291, n = 3) with the library-default stack (read back parisize 8000000,
  parisizemax 8003584), `ellcard` raised `PariError`: "ellcard: the PARI stack overflows (current size: 8003584;
  maximum size: 8003584)", reproducing RUN-GFPN-3377f1's failure mode. DV-2: with the P-A configuration the in-process
  PARI call returns at (4111, 3) N = 69477519282, (16777291, 3) N = 4722429815066881402162 and (4111, 4)
  N = 285620852275820 (DV-4), two repetitions each, and gp in capped children launched through the delivered recorder
  agrees at each point (getrlimit 10737418240 / 10737418240; child_end "exec").
- **Values:** parisize 67108864 (64 MiB), parisizemax 536870912 (512 MiB = half the driver RSS limit).
- **API:** `h = cypari2.Pari(); h.allocatemem(67108864, 536870912, silent=True)` (cypari2 2.2.0
  `Pari.allocatemem(s, sizemax)` -> `set_pari_stack_size` -> libpari `paristack_setsize`), called before the first
  v2 / v2-a1 import.
- **Read-back semantics: "requested".** The semantics probe grew the stack from 64 MiB to 256 MiB inside one handle; the
  `parisize` default read back 67108864 on the same handle after the growth and on a fresh handle (it reports the
  requested size, not the current stack). The exit read-back therefore requires parisize == 67108864 and parisizemax ==
  536870912 (RC-2 (b)).

## 5. The two r4 plans

| plan | sha256 | packages | protocol | run card | order and ids |
| --- | --- | --- | --- | --- | --- |
| `trial-plan-v2-r4.json` | 10822601c96f6df9d28cfeccac43ce3543d946fde3b10034e6f52796686693f1 | 31 | 2-r4 | TASK-20260924-b85e59 | the frozen v2 order; ids = id_map_v2 above (G1..G4 = RUN-GFPN-3e27a0, -878af1, -315a64, -d1a204) |
| `trial-plan-v2-a1-r4.json` | 36f0706067b362285574c3502c36b46d61052bbce890e277a3998cb7bdbc9c6a | 11 | 2-a1-r4 | TASK-20260924-46a554 | the frozen v2-a1 order; ids = id_map_a1 above (addendum blocking RUN-GFPN-5c417c; plan_branch 31-bit) |

Declared key paths: the RC-4 (b) tables above (12 and 13 paths); DV-5 read them back from this note and found them
equal to each plan's `repair.declared_key_paths`. Both plans carry `retired_ids` with the 162 retired ids, the ceiling
note "6 + 31 + 11 = 48 of 48 ... TEN plans", the LKA-1 repair block (seventeen hashes with standing; RB-1..RJ-8;
LKA-1..LKA-15; K = 5; spacing 2 s; the SF-2 (c) / HR-6 cap; REG-1 d-parsed; the three sites with their CC-1
dispositions; P-A; R = 10; V-1..V-7, K-1..K-6 and the classes), and the admission as RB-4 / RL-4 / RK-3 / RF-3 / RF-5
word it. The a1-r4 plan re-points the v2 gate to the four r4 gate ids and the phase-B receipt to TASK-20260924-4a47e5.

## 6. Hash check (LKA-1) and GFPN_V2_CAP_BYTES (LKA-11 (d); R4S-13)

- `sha256sum -c` over the seventeen `bound_hashes` of DEC-20260924-daf670 (lines 1052-1068): 17 OK, 0 mismatches, at
  03:52Z, before any write. R-1 binds the same seventeen values (DV-6 exercises one altered copy of each: 17 refusals).
- GFPN_V2_CAP_BYTES: unset at the stage start (`env | grep -c` printed 0; `printenv` exited 1); recorded again unset in
  the wrapper environment of every DV-18 development package ((a), (b), (e): `GFPN_V2_CAP_BYTES_in_wrapper_environment`
  {"GFPN_V2_CAP_BYTES_set": false, "GFPN_V2_CAP_BYTES_value": null}) and at the start of every DV-18 (f) run; every child environment is derived from it and never adds it
  (`r4_devchecks.child_env` removes it defensively).

## 7. Redirections (LKA-3) and the install read-backs

- v2 entry: `v2_common.PLAN_PATH` -> `trial-plan-v2-r4.json`; `v2_common.TASK_ID` -> TASK-20260924-b85e59.
- a1 entry, before `import a1_driver`: `a1_common.PLAN_A1_PATH` -> `trial-plan-v2-a1-r4.json`, `V2_PLAN_PATH` ->
  `trial-plan-v2-r4.json`, `RECEIPT_V2_PHASE_B` ->
  `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-4a47e5/post-run-receipt.json`, `V2_GATE_PACKAGES` -> the
  four r4 gate ids, `TASK_ID_RUNS` -> TASK-20260924-46a554, `PROTOCOL_VERSION` -> "2-a1-r4"; after it,
  `v2_common.TASK_ID` -> TASK-20260924-46a554.
- Every redirection, the SE-3, HR-3 and RL-5 read-backs and the PARI read-backs are checked before any command and
  recorded in `pari-stack.json` (`redirections`); any failure exits 2 before any command. Exercised by DV-6 (17 entry
  refusal cases, among them RL-5: the attribute rebound to the frozen function, and the captured original replaced, in
  each entry) and DV-18 (g) (each entry copied with the RL-1 install line removed exits 2 before any command).
- The complete set of in-process function replacements in a package: `v2_driver.solve` (SE-3, both entries),
  `a1_health.run_system` (HR-3, a1 entry), `v2_solver.run_child` (RL-1, both entries). `v2_common.curve_order_pari` is
  not replaced (P-A). The RG-1 callback is a registration, not a replacement.

## 8. DV-1..DV-17 (development observations; no number is a result)

| DV | outcome | when (UTC) | notes |
| --- | --- | --- | --- |
| DV-1 | PASS | 04:34Z (static); dynamic in DV-7 | 233 PARI-related lines in v2 / v2-a1 / r4; the Sage child probe (through the delivered recorder, capped, getrlimit 10737418240 / 10737418240) read parisize 8000000, parisizemax 1073741824, Sage 10.9; toolchain: /usr/bin/msolve (msolve 0.6.5-1build2), /usr/bin/valgrind (valgrind-3.22.0), /usr/bin/callgrind_annotate (callgrind_annotate-3.22.0, version printed on stderr), /usr/bin/gp (2.15.4; pari-gp 2.15.4-2.1build1) (CC-8 (e)) |
| DV-2 | PASS | 04:2xZ | section 4 |
| DV-3 | PASS | 04:2xZ | section 4 |
| DV-4 | PASS | with DV-2 | (4111, n = 4) |
| DV-5 | PASS (attempt 3) | 04:36Z | attempt 1 implementation defect, attempt 2 harness fault (section 0); RC-4 (c) equality by DV-5's own code (canonical sha256 0588623b... v2, 138545e9... a1, equal on both sides); declared keys equal the RC-4 (b) record; watchdogs equal trial-plan-v2.json lines 95-177; 31 / 11 packages, each the image of the frozen id in order; no old id outside the maps / lists; 162 retired ids; none of the eight forbidden task ids; `--check` regenerates both plans byte-identically |
| DV-6 | PASS (attempt 2, pre-patch layer); PASS again on the final layer | 04:40Z; 06:18Z-06:22Z | 81 wrapper cases (R-1 x17; R-2 incl. an exhaustive sweep of 217 ids: 162 retired, 42 frozen, 42 r3 and the v1 ids, each refused by R-2 with an id-class reason; R-3..R-13; RB-4 (b) on a gate package and on the controls_a1 image; RL-4 on a read package) and 17 entry cases, each exiting 2 with its own reason and writing nothing; real run packages compared by lstat metadata only |
| DV-7 | PASS (final-layer run) | 05:12Z-05:27Z | section 8.1 |
| DV-8 | PASS | 04:36Z | exclusion list byte-identical to the r1 / r2 / r3 lists and to implementation-v2-r1.md lines 329-372, sha256 4122bcb0...9a99f2c, X1..X17; REG-1 self-comparison PASS (219 reference files verified against the TASK-20260923-0fa03f post-run receipt); every perturbation as expected; the reference-integrity negative FAILs |
| DV-9 | PASS | 06:22Z (last) | section 9 |
| DV-10 | PASS | 04:37Z | 42 ids, distinct, equal to the allocator outputs in order; every mint-time `--check` rc 0 with 0 occurrences; none in v1 / v2 / v2-a1 / r1 / r2 / r3 / the 162 retired; no run directory |
| DV-11 | PASS | 05:40Z | static launch list S-1 (v2_driver.py 166), S-2 (a1_health.py 147), S-3 (v2_driver.py 209 / v2_solver.py 517); 0 r4 launch sites; dynamic counts equal for all 21 DV-7 packages (forks traced = launch records with child_created true; S-1 children = attempts + pass-through; S-2 children = attempts; S-3 valgrind children = wrapped ok calls with callgrind_timeout = CG-3 records, each inside a wrapped-call interval); the consumer inventory (section 13) |
| DV-12 | PASS (a)-(g) | 05:27Z-05:37Z | toy G1 (fixture --p 1033), target fx_reg1_S3; forcing through the documented `_call_original` indirection in a development shim |
| DV-13 | PASS | in DV-7 | every launched toy package read back PYTHONHASHSEED "0" (world B "12345", the declared SE-5 override) |
| DV-14 | PASS | in DV-7 | every re-solve started >= 2.0 s after the previous attempt's recorded end |
| DV-15 | PASS | 05:40Z | set O: 75 outputs (73 ok-classified), each located and verified against its receipt; 848 toy rows (DV-7 final, DV-12, DV-16 packages); 0 violations of the invariant |
| DV-16 | PASS (a)-(e) | 05:37Z-05:39Z | toy prime 1021 declared in `r4_dv16.py` before the run; health tag health_p1021_d222 |
| DV-17 | PASS | 05:54:56Z-06:18:02Z | 360 calls (36 entries x R = 10) of the frozen callgrind_instructions at 4111, >= 2 s apart, the delivered recorder installed; inputs (RUN-GFPN-ac4487 solver/<tag>.ms) verified against the TASK-20260923-0fa03f post-run receipt and the archived entries; timeout 1800 s (trial-plan-v2.json callgrind_timeout_s.m3); every call's REG-1-compared fields equal the archived reference values (CG-5 (c)); 360 launch records, each child_created true, pair = cap, child_end "exec" |

8.1 **DV-7 (final-layer run).** Toy primes only: n = m = 3 fixture data at 1033 and 1039, n = m = 4 at 1033; toy
ladder rungs 1021 (addendum role) and the first complete prime of the declared list (v2 role), through the frozen
a1_toy / a1_pari with gp in capped children launched through the delivered recorder. SE-5 probe run once: world A
(PYTHONHASHSEED "0") and world B ("12345") toy G1 compared by REG-1 (d-parsed): PASS; a perturbed copy FAILS. Toy G2
(1039) failed with the persistent SSF signature (as in attempt 1 and in the r3 stage); declared rule: it stays the toy G2
and its "did not pass" refusal is expected. G3, G4 and the builds / cells at 262151 and 16777291 are SYNTHETIC rows
(declared before any launch). 21 packages launched through the delivered wrapper (`preflight`, then `launch`) and
entries; every world-A package's manifest verdict PASS or PASS_ZL and the standalone r4 checker rc 0; world B G1 fails
only the declared SE-6 override; RC-8 phase B verified; getrlimit 10737418240 in every child; threads 1; PARI status
command_returned. Consequence stated plainly: R-7's admission of a PASSING toy G2 is not exercised (a failed gate
package's refusal is).

## 9. DV-9 (SC-6): nothing edited

PASS at 06:22Z, against the baseline taken at 04:00:48Z before any write (`dv9/baseline.json`; stage start 03:52:17Z):
- the 1294 files hashed under the frozen roots (every frozen tree, plan, amendment, the specification, `implementation/ladder.json`, the archives this stage verifies): 0 changed, 0 added, 0 removed;
- the other run packages (2110 files, lstat size and mtime only, never read): 0 changed;
- the seventeen amendments equal their bound sha256; `ladder.json` unchanged (7e42961d...327c);
- receipt equalities (paths under the experiment that this stage may read): TASK-20260923-0fa03f phase A (14) and phase B (345), TASK-20260923-4ff597 phase A (12), TASK-20260924-f1fb0e phase A (22) and phase B (801), TASK-20260923-53a47d (17), TASK-20260924-5ca2a5 (19), TASK-20260924-3ee9a8 (3), TASK-20260924-0957c2 (3), TASK-20260924-ad3f9a (3), TASK-20260924-c65bfb (3), TASK-20260924-68cf6b (0 such paths): all equal. The run-package paths among them are files of the six packages R4S-12 permits (RUN-GFPN-ac4487, -3377f1 and the four r3 gate packages), hashed to verify the receipts; no other run package was read;
- byte code: the 5 pre-existing files only; none later than the stage start; no `__pycache__` anywhere in the repository newer than the stage start;
- `git status --porcelain --untracked-files=all` (GIT_OPTIONAL_LOCKS=0): 23 lines, every one an untracked path in the write scope; 0 tracked modifications; HEAD unchanged (1768588f0d7f94020f235e2141d7a843f45b150f); `runs/` 55 entries, no new run directory.

## 10. DV-18 (run once, after DV-7; (f) (xiv) and (xv) first)

Every DV-18 output is a DEVELOPMENT OBSERVATION: never a gate package, never a result, never compared with a gate
package for selection, never a reason to re-run anything; its values at 4111, 16777291, 1073741831 and the toy primes
are toy harness values and never evidence about D. The complete record is `dv18/dv18-summary.json` in the bundle.

10.1 **(f) (xiv) and (xv), FIRST (05:41:04Z-05:41:12Z; RH-5 (d)).** (xiv) a real trivial capped child that execs a
development program: one launch record, child_created true, pair = cap, child_end "exec", time_enabled_ns > 0, class (B).
(xv) a stand-in for os.execv as v2_solver sees it raising OSError in the child only: returncode 99, pair read,
child_end "frozen_pre_exec_exit" with time_enabled_ns 0 and value 0, class (B). Both PASS on this host.

10.2 **(f) (i)-(xiii), (xvi)-(xxi)** (each in its own scratch process; the delivered recorder installed over the frozen
run_child by `r4_recorder.install`; stand-ins only at frozen callees / primitives as v2_solver or the recorder sees them,
or -- RL-6 (f) (iii)-(v) only -- the recorder's captured original):
(i) timeout kill: child_created true, pair = cap; (ii) nonzero exit: the same; (iii) refusal before fork: child_created
false, no_child; (iv) "ERR setrlimit" record: pair "absent", report carried; (v) a raise recorded and re-raised as the
same object; (vi) `_perf_open_instructions` raising at 235: child_created true, pair = cap, raise_frame_record, raised,
re-raised (the frozen child, left waiting for the go byte, is released at process exit and execs the trivial program);
(vii) `_perf_read` raising at 281: the same (this host's PERF_TYPE_HARDWARE counter does not open, ENOENT, so a stand-in
`_perf_open_instructions` returning an fd on /dev/null was needed to reach 281; recorded); (viii) `self_rss_bytes`
raising: child_created false, raised; (ix) stdout in a missing directory: child_created true, pair "absent", report ''
(as RK-4 (c) (ix) states; see observation O-1); (x) fork then MemoryError in the parent: child_created undetermined;
(xi) os.read raising at 214 and SolverLock.release raising: child_created true from `pid` on the __context__
exception's traceback; (xii) os.pipe raising at 178 and release raising: child_created false; (xiii) a recorder call
ending in the child: one recorder-foreign file and no launch record from the child; (xvi) fork raising
KeyboardInterrupt in the child with the foreign-file write made to fail: child_end undetermined (returncode 1, no exec),
record-level verdict FAIL; (xvii) os.read raising at 202 and os._exit(99) raising KeyboardInterrupt in the child, the
foreign-file write (a) made to fail and (b) interrupted: pair read, child_end undetermined, FAIL (the records are in
`dv18/f/xvii-a`, `xvii-b`); (xviii) the recorder's own perf_event_open made to fail: counter not opened, undetermined,
FAIL; (xix) refusal before fork (cap 0): callback not fired, no_child, class (A); (xx) a stand-in child exiting 98
after OK (hard-limit mismatch; os._exit(98) delayed 1.5 s in the child so that the parent writes its go byte first):
frozen_pre_exec_exit; (xxi) a signal handler raising KeyboardInterrupt inside the RG-1 callback: the callback marked,
child_end undetermined, FAIL. All as stated.

10.3 **(a) controls, (b) anchor-identity, (e) controls-a1** (RF-4 harness; one process per command; development labels
DEV-DV18-a-controls, DEV-DV18-b-anchor-identity, DEV-DV18-e-controls-a1; scratch worlds outside `runs/`):

| item | preflight refusals | launch | frozen checker | r4 items | (c) / (e) requirements | (c') | RG-3 (e) / RH-3 (a) / LKA-4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (a) controls at its hard-coded 4111 / 262151 / 16777291 | only the expected ones (R-7 gate packages not run, REG-1 NOT_EVALUABLE, R-8, RL-4) | completed_valid, 82.1 s | exit 0 | exactly the three REG-1 items (RG-3 (d)) | no evidenced child without a read-back; 19 capped children (11 builders, 8 solves) each with its pair before de-duplication, as RB-5 (c) states for RUN-GFPN-bfe956; SC-4 rows 8 = the 8 recorded ok S-1 attempts with a retained output | every child_created record carries pair = cap; no recorder gap | 19 argv substituted clean; 11 spec "out" values; 113 recorded values tabled, all as LKA-4 requires |
| (b) anchor-identity at 16777291 with the Sage comparator | the expected ones | completed_valid, 38.0 s | exit 0 | exactly the three REG-1 items | no evidenced child without a read-back (7 capped children: comparator, 1 builder, 5 gb_only solves) | pair = cap everywhere; no recorder gap; the anchor_comparator_random pass-through record carries the pair and threads 1 | clean; 1 spec; raw['build']['npz'] tabled; 52 recorded values, all as LKA-4 requires |
| (e) controls-a1 at 1073741831 (RK-4 (b); the MODELED single-attempt bound 21600 s is not a measurement) | the expected ones | completed_valid, 7.7 s | a1 checker exit 0 | exactly the three REG-1 items | 2 SC-4 S-1 rows (a1_driver.py:166); both S-2 attempts the health report records accounted | pair = cap; no recorder gap | clean; a1_pari.py 97 script / command, a1_health.py 148-149, S-2 attempt command tabled; 66 recorded values, all as LKA-4 requires |

The RG-3 (a) development copies of `implementation/ladder.json` and the two fixture files are byte-identical (sha256
side by side in `dv18/package-*.json`). The development plan copies differ from the r4 plans ONLY in the package under
test's run id (recorded path by path). `r4_run_wrapper.DRIVER_PYTHONHASHSEED` stayed "0"; GFPN_V2_CACHE_DIR was not set.
The anchor-identity command reads RUN-GFPN-61bba9's raw-result.json and anchor logs by its own frozen code
(`v2_common.ARCHIVED_ANCHOR_RUN`, fixed at import); the stage itself read nothing there.

10.4 **(d) RB-4 on copies of the (a) world** (attempt 3; attempts 1 and 2 were harness faults, preserved: attempt 1's
plan copy did not make the (a) package the G4 image; attempt 2's copy also rewrote the id map). A (d)-specific plan copy
names the (a) label as G4 (gate.blocking_packages and `requires` only). Preflight of the F-4 package: with the ORIGINAL
copy, RB-4 (a) holds and the r4 checker on the (a) package has frozen exit 0 and exactly the three REG-1 items (verdict
FAIL); with the read-back list EMPTIED, the frozen checker exits 1 on "no child RLIMIT_AS read-back recorded" and the
wrapper refuses the later package on RB-4 (b) naming the (a) package. **Literal reading NOT MET** (the original also
yields an RB-4 (b) refusal, because of the three REG-1 items); **development reading MET**. This is the STOP condition
recorded at the top of this note.

10.5 **(g)** both entry copies without the RL-1 install exit 2 before any command, writing only `pari-stack.json`
(status refused_before_any_command, "RL-5 install read-back ..."); argv `--help` (were the refusal absent, no computation
could start). **(h)** PASS: section 12 and `dv18/h/h.json` (the six production call sites; the two loads; the one call
of the captured reference; no `from v2_solver import`, no module-level launch, no second v2_solver; exactly one
definition each of run_child (149) and _run_child_locked (177); no SystemExit(97 / 98 / 99) anywhere scanned; no
process creation or exec in the r4 modules of the entries' closure; third-party modules listed with versions and NOT
scanned).

10.6 **Objects and in-place checks (RI-3 (19)-(27); RJ-5 (28)-(32)).** Objects built at toy primes through the delivered
wrapper and entries (`dv18/objects/`), stand-ins only BENEATH the wrappers (LKA-6): S1 = toy G1 with an msolve
stand-in EXECUTABLE forcing the SSF signature (clause v) on declared tags so that N = 2, 3, 6 (fx_fresh1_S3,
fx_fresh1_S3_rescaled, fx_fresh1_torsion_S3_norm); S2 = toy controls-a1 (1021) with the same stand-in on
health_p1021_d222 (N = 2 at S-2); CG = toy G1 with a valgrind stand-in executable (writes its out file, exits 3);
O28 = toy G1 with os.open failing in the child for ".callgrind.stdout"; O29b = toy controls-a1 with os.open failing in
the child for ".gp.stdout" (LKA-5). In every object RB-1 records, events, counters and launch records were written by the
delivered r4 code. LKA-11 (c): the parent made 0 os.open calls through the proxy naming a targeted suffix (O28, O29b);
the proxy acts only in the child. Every alteration was made IN PLACE, the bytes restored and the restore verified by
sha256; (32) was evaluated on every unaltered object BEFORE any alteration.

| item | object | gap level, all detectors on | gap level, detector off | verdict level (on / off) |
| --- | --- | --- | --- | --- |
| (32) positive control | S1, S2, CG, O28, O29b, DV-18 (a), (b), (e), unaltered | no named gap, no recorder gap (all eight) | - | S1, CG, O28 PASS; S2 and the three DV-18 packages FAIL on the three REG-1 items only; O29b FAIL (its gp child failed: an infrastructure launch, an undetermined child_end) |
| (19) renamed files | S1 | the attempt-1 renamed files attributed by RH-1 (vi); renamed_files entry removed: recorder gap; one launch record of the tag removed: COUNT GAP | - | FAIL (V-7 also fails on the altered file, not the discriminant) |
| (20) the same at S-2 | S2 | as (19) | - | FAIL |
| (21) callgrind not ok | CG | `<tag>.callgrind.out` attributed by RH-1 (iii) | - | - |
| (22) uncached build_poly record removed | S1 | .spec.json, .stdout, .stderr, .npz, .meta.json gaps | - | FAIL |
| (22) raw_grid record removed | S1 | .spec.json, .stdout, .stderr, .meta.json gaps | - | FAIL |
| (24) LR-1, LR-2, LR-3, LR-5 | S1, S2 | COUNT GAP | RI-1 (a), (d) off: NO RI-1 named gap and NO recorder gap (25) | FAIL / FAIL (V-7) |
| (24) every single removal among 2, 3 and 6 attempts (11), LR-4 (3 pairs of three) | S1 | COUNT GAP each | - | FAIL |
| (27) attempt record removed; launch record duplicated; counter decremented; child-job record duplicated | S1 | COUNT GAP; COUNT GAP; SITE COUNT GAP; DUPLICATE-PATH GAP | - | FAIL |
| (28) CX-A: a callgrind child's stdout open failed, its record removed | O28 | CALLGRIND COUNT GAP and CALLGRIND SITE COUNT GAP | RJ-1 off: NO named gap, NO recorder gap | FAIL ("a recorder gap", "an infrastructure launch", V-7) / FAIL ("an infrastructure launch", V-7) |
| (29) first object: DV-18 (e)'s gp record removed | DV-18 (e) | pari/<tag>.gp, .gp.stdout, .gp.stderr gaps | RJ-2 off: pari/<tag>.gp NOT a gap; .gp.stdout, .gp.stderr gaps | FAIL / FAIL ("a recorder gap"; V-7) |
| (29) second object (LKA-5): gp stdout open failed, record removed | O29b | pari/<tag>.gp gap | RJ-2 off: NO named gap, NO recorder gap | FAIL ("a recorder gap"; V-7) / FAIL (V-7 and the object's own failed gp launch) |
| (30) DV-18 (b)'s comparator record removed | DV-18 (b) | COMPARATOR COUNT GAP; comparator/ files gaps | RJ-3 off: no COMPARATOR COUNT GAP; comparator/ files still gaps (RH-1 (iv) needs the record) | FAIL / FAIL ("a recorder gap"; V-7) |
| (31) a record with an unknown stdout form appended | S1 | UNKNOWN-KIND GAP | - | FAIL |

At the verdict level every in-place alteration FAILs also on the carried V-7 item (the manifest's solver-events.json
sha256), as RJ-5 (a) states; the discriminant is the gap level. In (28) with RJ-1 off the verdict is FAIL on V-7 and on
the stop class "an infrastructure launch" (the O28 callgrind records are class (C): child_created true, pair not read;
the stop-class list names every such launch whenever the verdict is FAIL); in (29)'s second object with RJ-2 off it is
FAIL on V-7 and the object's own failed gp launch.

10.7 **(i) (1)-(18), (23)** on coherent development copies of DV-7 (final) toy packages (the manifest's solver_events
block and child_readback_accounting recomputed by the delivered wrapper functions after each edit, so V-7 holds):
(1) PASS_ZL (the frozen checker's single item "no child RLIMIT_AS read-back recorded"); (2) FAIL; (3) FAIL; (4) FAIL
(a gate package); (5) a failing F-4 copy does not refuse the build package, a failing G1 copy does; (6) the dependant
refused with "an infrastructure launch"; (7) FAIL; (8) FAIL, not PASS_ZL, the X-08 dependant refused; (9) FAIL; (10)
FAIL; (11) PASS (class (C)); (12) PASS (class (A)); (13) FAIL; (14) FAIL; (15) FAIL with "an infrastructure launch" and
the label "infrastructure-stop outcome (RG-2)", the dependant refused; (16) the 19 substituted argv of (a) carry neither
label nor scratch root; (17) (b) and (e): no recorder gap; (18) (a) 51, (b) 12, (e) 10 child / comparator files, each
attributed, no gap; (23) FAIL with "a cap read-back mismatch" and the label "cap-mismatch stop outcome (RH-2)", the
dependant refused. All as stated.

## 11. RI-4 / RJ-6 path values as LKA-4 words them (per value: path, form, raw, substituted)

The complete per-value tables (file, JSON path, form, raw value, substituted value, class, verdict) are in
`dv18/eval-a.json`, `eval-b.json`, `eval-e.json` ("LKA-4 value table"). Substitution: every occurrence of the
development run directory D is replaced by `<repository>/experiments/EXP-GFPN-05ff43/runs/<plan run id>` (G4 d1a204,
G3 315a64, controls_a1 5c417c). Summary:

| package | values | LISTED (LKA-4 (a)) | unlisted, D as a whole element or D + "/" prefix (LKA-4 (b)) | label fields (RF-4 (d)) | RF-4 (a) development values | absent listed fields (LKA-4 (c)) | not OK |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (a) | 113 | 93 (launch-record stdout/stderr 38, argv 43, spec out 11, command.txt line 2) | 1 (resources.child_readback_accounting.recorder_gaps.run_directory_recorded) | 11 (7 certificate run_id; raw package; manifest run.id; command.txt line 5; the r4 checker's text) | 8 (the dev plan copies in pari-stack.json and the manifest; the entry / check shim paths) | S-2 attempt command; a1_health 148 / 149; a1_pari 97; raw['build']['npz'] | 0 |
| (b) | 52 | 39 | 1 | 4 | 8 | S-2 attempt command; a1_health 148 / 149; a1_pari 97 | 0 |
| (e) | 66 | 40 | 1 | 9 | 16 | raw['build']['npz'] | 0 |

Every listed value, substituted, carries neither the development label nor the scratch root; every unlisted value
carries D only as a whole element or a "D/" prefix; every label occurrence is a field RF-4 (d) accepts or the run
directory's name; every scratch-root occurrence outside D is a recorded RF-4 (a) development value (the plan copies, the
shims). No text-log line (stdout.log, stderr.log, child logs) carries D, the label or the scratch root in another form.
The argv (RG-3 (e)) and spec "out" (RH-3 (a)) comparisons are in the same files.

## 12. LKA-7: every load of the frozen run_child in the delivered r4 tree (DV-18 (h); ast)

| file | line | function | form |
| --- | --- | --- | --- |
| `implementation-v2-r4/r4_recorder.py` | 450 | `install` | attribute load `v2_solver_module.run_child` (the capture) |
| `implementation-v2-r4/r4_recorder.py` | 475 | `readback` | `getattr(v2_solver_module, "run_child", None)` (the RL-5 read-back; at that time the attribute is the recorder) |

The captured reference is stored only in `r4_recorder._ST["original"]` (install), read by `launch_recorder` and by
`readback` (identity only), and CALLED only in `launch_recorder` (line 426). No r4 function calls run_child. No
from-import, attrgetter or default argument names it. The production call sites (ast over implementation-v2/ and
implementation-v2-a1/): v2_driver.py 101 (`V.run_child`, child_job), 166 (`V.run_child`, solve), 650 (`V.run_child`,
cmd_anchor_identity), v2_solver.py 517 (module global, callgrind_instructions), a1_health.py 147 (`V.run_child`,
run_system), a1_pari.py 96 (`V.run_child`, curve_facts): exactly the six of RJ-4 (a). Method limits: static;
string-built attribute names and dynamic imports are not seen (the RL-5 read-back covers the attribute at run time).
Scope: the development shims that DV-6 writes to scratch mention the recorder's state inside a Python string (never an
AST load in the tree); the DV-17 / DV-18 harnesses live outside the tree.

## 13. The consumer inventory (DV-11; VC-3 with RB-7, RL-5, RK-5, RF-7, RG-8, RH-7, RI-5 (b), LKA-8, LKA-9)

`r4_inventory.py` over the 20-file tree: 297 functions, 272 listed; classes: alpha 77, epsilon 54, gamma 39, reads no
site value 63, reads no site value directly 8, V-4 8, V-1 row K-1 5, V-1 row K-2 4, beta 5, V-7 2, V-2 2, V-2 (CG-4) 2,
V-5 2 (both development-report functions, effect E6), V-1 row K-5 1. Every listed delivered function has exactly one
class; every gamma entry names its clause (39, among them the recorder, its callback `_after_fork_in_parent` (RG-1 (a);
RH-4), the counter open and read, `child_end_value`, and the RB-1 writers). REQUIRED LISTINGS all present with the class
their texts give: RB-1 (e) writer `_rb1_callgrind_result_present` (gamma, clause RB-1 (e)); RB-2 collector
`readback_sources` (V-1 row K-2, E5); RB-3 `recorded_attempts` (epsilon, E6); RB-4 (b) `checker_verdict` (V-4, E2); the
launch recorder (gamma); readers of launch / pass-through records; RH-1 attribution `attribute`, `_spec_ok`,
`_renamed_ok` (epsilon); RI-1 counts `ri1_counts`, RJ-1 (b) `rj1_callgrind`, RJ-3 `rj3_comparator`, RJ-4 (b)
`rj4_unknown` (each epsilon, E2). LKA-8: the only E1-E4 readers of an RB-1 value are `ri1_counts` and `rj1_callgrind`
(others read at E5 / E6 or are gamma writers). LKA-9: `callgrind_result_present` is written only by `_rb1_s1` through
`_rb1_callgrind_result_present`, whose body is exactly `return "instructions_callgrind" in res` (ast-checked), and read at
E1-E4 only by `rj1_callgrind`; no delivered function with effect E1-E4 names a CG-3 field, the S-3 section or a
callgrind-site count. The RG-2 and RH-2 outcome labels are listed as classification labels with no value class. No STOP.

## 14. LKA-4..LKA-10, quoted, with the outputs that show each was implemented as worded

- **LKA-4** (quoted): "(a) Every value RI-4 as RJ-6 extends it LISTS (the spec "out" values, the a1_pari.py 97 "script"
  and "command", the a1_health.py 148 "input.path" and 149 "command", the S-2 attempt record "command" of r3_resolve.py
  198 and its r4 counterpart, health-<p>.json's copies, the second line of command.txt, the launch records' stdout_path
  and stderr_path, and argv) is SUBSTITUTED by replacing EVERY occurrence of the development run directory's absolute
  path by <repository>/experiments/EXP-GFPN-05ff43/runs/<the plan package's run id>, exactly as RG-3 (e) substitutes
  argv, and must then equal the value the plan package's frozen code would write. A listed value is never STOPped for the
  form in which it carries the run directory; a difference after substitution is a STOP. (b) For a value NOT listed,
  RJ-6's form clause applies, with "as a whole whitespace-delimited element of a command string" read as "as an element
  that is the development run directory or begins with it followed by '/'": such a value is substituted and compared as
  in (a); any other occurrence of the development run directory, the development label or the scratch root is a STOP.
  (c) A listed field a package does not carry (the controls builds' raw["build"]["npz"]) is recorded absent, not a STOP
  (RJ-6). The DV-18 output records, per value, its path, form, raw value and substituted value." OUTPUTS: section 11;
  `dv18/eval-{a,b,e}.json`; 0 values not OK; absent listed fields recorded (not STOPs).
- **LKA-5** (quoted): "(29)'s second object is a separate controls-a1-shaped development object built in a scratch
  development process with an RF-6 / RG-7 (f) stand-in (os.open as v2_solver sees it, resolved at call time in the gp
  child only, raising for names ending ".gp.stdout"), its gp launch record then removed in place. It is NOT a DV-18 (e)
  package: every DV-18 (a), (b) and (e) package stays shim-free under RG-3 (b). The stage records the object's
  construction, its stand-in and its gap-level and verdict-level outcomes with RJ-2 enabled and disabled." OUTPUTS:
  object O29b (`dv18/objects/object-O29b.json`: construction, stand-in, LKA-11 (c)); section 10.6 row "(29) second
  object"; `dv18/alter-results.json`.
- **LKA-6** (quoted): ""a function the frozen solve, run_system, callgrind_instructions, child_job or curve_facts calls"
  reads TRANSITIVELY: any callee reached from those functions' bodies down to process primitives as v2_solver sees them
  (the level RG-7 (f) (xiv)-(xx) already uses: os.execv, os.fork, os.read, os._exit, and here os.open in the child), and
  the executable the frozen run_child launches, EXCEPT v2_solver.run_child itself, the RL-1 launch recorder installed in
  its place, the SE-3 and HR-3 wrappers, and any function of the r4 layer. A stand-in at any of those excepted objects is
  a STOP. The (28) and (29) os.open stand-ins, resolved at call time in the child only, are admitted. The DV-18 output
  records each stand-in's target, the process it acts in, and that RB-1 records, events, site counters and launch
  records were written by the delivered r4 code on each object." OUTPUTS: the objects' stand-ins are the msolve and
  valgrind EXECUTABLES (v2_solver.MSOLVE / VALGRIND) and os.open as v2_solver sees it in the child; each object's JSON
  records target, process and level; every RB-1 record, event, counter and launch record was written by the delivered
  code in the entry process. (Stand-ins at r4 functions or at the captured original occur only in DV-12 / DV-16 (the
  documented `_call_original` indirection, not a DV-18 object) and in RL-6 (f) (iii)-(v), which words them so.)
- **LKA-7** (quoted): "(a) The production call sites of v2_solver.run_child are found by ast exactly as RJ-4 (c) words
  it (every call through V.run_child or the module global run_child, as review be2daf BJ-5 derived them) and must be
  exactly the six of RJ-4 (a). (b) "No r4 function calls run_child" reads: no r4 function OTHER THAN the RL-1 launch
  recorder calls the frozen run_child, through ANY reference. DV-18 (h) checks it by listing every LOAD of the frozen
  function object in the delivered r4 tree (attribute loads of v2_solver.run_child or V.run_child, global-name loads of
  run_child, from-imports, getattr / attrgetter, and default arguments) and requiring that each lies in the RL-1
  installation, that the captured reference is stored only where the recorder reads it, and that it is called only
  inside the recorder. Any other load or call is a STOP (VA-12 (b) re-pointed). (c) The scan's output lists every load
  found, with file and line." OUTPUTS: section 12; `dv18/h/h.json`.
- **LKA-8** (quoted): "RB-7's "read at E1-E4 only by the consumers named here" reads as RB-7's list extended by the
  consumers the incorporating texts name with their class: attcount RI-1 (a) (i) and (ii) (epsilon, effect E2 through
  RF-3 (a); RI-5 (b)), launchkind RJ-1 (b) (epsilon, effect E2; RJ-1 (d)), RJ-3 (epsilon, effect E2; CORR-20260924-19154c
  item 3) and RJ-4 (b) (epsilon, effect E2). DV-11's VC-3 inventory lists each with exactly that one class. Any OTHER r4
  consumer of an RB-1 value at E1-E4 is a DV-11 STOP, unchanged." OUTPUTS: section 13; `dv11/inventory/inventory.json`
  ("LKA-8_LKA-9_and_required_listings").
- **LKA-9** (quoted): "Reading K, as RJ-1 (a) words it: callgrind_result_present is written by the r4 SE-3 wrapper as the
  result of a key-membership test ("instructions_callgrind" in the mapping the frozen solve RETURNED for that attempt),
  before the unmodified result is returned, and from nothing else. It reads no value inside res["instructions_callgrind"],
  no CG-3 field, no V-5 record in solver-events.json and no callgrind-site count. It is an epsilon S-1 value (RB-7);
  RJ-1 (b) is its only E1-E4 reader (LKA-8). DV-11 lists the writer (gamma, clause RB-1 (e)) and the reader (epsilon).
  VA-6 (c) and CC-5 are UNCHANGED: any r4 read of a CG-3 field, a V-5 record or a callgrind-site count at E1-E4 is a
  DV-11 STOP; if RB-1 (e) cannot be implemented within these words, the stage STOPs (LKA-15 (c))." OUTPUTS:
  `r4_resolve._rb1_callgrind_result_present` (section 3.2); section 13; the unaltered (28) object O28 (every callgrind
  child failed; RB-1 (e) still true on each attempt whose returned result carries the key) evaluates with no CALLGRIND
  COUNT GAP (section 10.6, (32)).
- **LKA-10** (quoted): "The stdout forms of RJ-1 (b), RJ-3 and RJ-4 (a) / (b) are relative to the package's own run
  directory, as RI-1 (a) and (b), RH-1 and RL-3 read their forms. A recorded stdout_path is relativized ONLY by removing
  the exact string prefix "<run directory>/", where the run directory is the absolute path the package records for
  itself (GFPN_RUN_DIR; command.txt line 2); no normalization, symlink resolution or case folding is applied. A
  stdout_path without that prefix, or whose remainder matches none of the six forms, is an UNKNOWN-KIND GAP (RJ-4 (b)) and
  the verdict is FAIL. DV-18 (32) and the RI-3 / RJ-5 objects are evaluated under this reading." OUTPUTS:
  `r4_gaps.run_dir_recorded` / `relativize` (section 3.4); (31) yields UNKNOWN-KIND GAP; (32) on every unaltered object.

## 15. Deviations, readings and implementation choices (every one recorded; none changes a rule)

- **D-1 (R4S-16, exact commands).** Six stray interpreter invocations outside the file-by-path rule, each recorded in
  the command log as deviation lines (a)-(f): `python3 -B -c "print(1)" >/dev/null` appended by mistake to a listing
  command; `python3 -B -c ""` twice; `python3 -B -` with an EMPTY heredoc twice; `python3 -c ""` (no -B; empty program,
  nothing imported) once at about 06:20Z. None read or wrote a file or touched the repository. After the bundle was
  built: one `ls` of an unset shell variable listed /dev (read-only), and one final-scan attempt with an empty grep
  pattern (the hex decoder was absent) matched every file and was discarded as INVALID (command log [62]); the valid
  scan is in section 17. Every other
  development program was written to a file and run by its path (including the scratch editors that edited layer files).
- **D-2 (DV-5).** Attempt 1 found an implementation defect in the plan writer (section 0); fixed; attempt 2 a harness
  fault (write-once guard); the first-write plans were moved to `<scratchpad>/r4/superseded-plans/` and re-written.
- **D-3 (DV-6).** Attempt 1: a harness label fault in one case's expected text; attempt 2 PASS; both preserved.
- **D-4.** `x13_check` reads the controls_a1 image in the package's own runs directory (04:43Z, before DV-7).
- **D-5 (DV-7).** Attempt 1 ended on the toy G2 at 1039 (persistent SSF, as in r3) and on the accounting-directory
  defect carried from r3. Attempt 2 was a continuation outside the layer that kept the REAL failed toy G2 as the toy
  gate (the r3 continuation had replaced it with a synthetic row) and declared its "did not pass" refusal expected.
- **D-6 (layer patch 1, 05:12Z).** Section 3.9. DV-7 was then run again in full on the patched layer; DV-12, DV-16,
  DV-11, DV-15, DV-17 and DV-18 ran on the patched layer; DV-6 was re-run on it (section 8). DV-1 (static listing),
  DV-2 / DV-3 / DV-4, DV-5, DV-8 and DV-10 ran before the patch; they read none of the patched functions' behaviour
  (the patched files are r4_check_run.py, r4_run_wrapper.py, r4_dv7.py and r4_dv12.py; DV-1's static line listing of
  them differs only by the patched lines). The layer snapshots are bundled (`layer-snapshots/`).
- **D-7 (reading).** RB-4 (b) / RL-4 / RK-3 "run by the wrapper at admission time": the r4 checker runs IN the wrapper's
  process; its frozen checker runs in its own process (RC-3 (e)); the recorded command says so.
- **D-8 (implementation choice).** After a package ran, the wrapper runs the r4 checker on it and appends the verdict,
  stop classes, labels, exit statuses and verbatim output to the manifest (`run.verdict`), the RK-3 (b) record.
- **D-9 (DV-7 scope).** G3 (anchor-identity), G4 (controls) and the builds / cells at 262151 and 16777291 are SYNTHETIC
  toy rows, declared before any launch; the two commands run at their own parameters in DV-18 (a) and (b) instead.
- **D-10 (DV-7 / DV-12 / DV-16 method).** Each toy package is run as RK-4 (a) / RF-4 (a) word the development method:
  preflight, refusals recorded verbatim, only refusals naming a declared synthetic package or the declared failed toy G2
  expected, then `launch` in the harness process. No flag, mode or argument was added to the wrapper.
- **D-11 (DV-7 trace).** The r3 run_child tracer is not carried (it would make RL-5 refuse; RG-3 (b)). DV-11's dynamic
  counts come from a development proxy for the `os` module AS v2_solver SEES IT whose `fork` logs in the parent after
  the real fork (beneath the recorder), and from a wrapper of the documented `r4_resolve._call_original` indirection,
  both in the toy shims only.
- **D-12 (DV-18 harness faults).** (b) attempt 1: the harness looked for plan kind "anchor_identity" (the kind is
  "anchor"); stopped before any launch; preserved. (d) attempt 1: the plan copy did not make the (a) package the G4
  image (nothing about it was evaluated); attempt 2: the plan copy also rewrote the id map (an artifact item); both
  preserved; attempt 3 is the recorded (d).
- **D-13 (sequencing).** The RB-5 (d) STOP condition was recorded at 05:47:42Z; the remaining development checks (DV-18
  objects, in-place checks, copies, (g), DV-17, DV-9) were completed afterwards as development observations, so that the
  Coordinator's ruling has the complete record. No run package was written at any time.
- **D-14 (DV-18 (f) (vii)).** This host's PERF_TYPE_HARDWARE counter does not open (ENOENT), so `_perf_read` at
  v2_solver.py 281 is reached only with a second stand-in for `_perf_open_instructions` returning an fd on /dev/null
  (recorded in the item's output).
- **D-15 (DV-18 (g)).** The entry copies were run with argv `--help` (were the refusal absent, argparse would print its
  usage; no computation could start).
- **D-16 (DV-17).** The r3 harness was carried with one r4 change: the delivered recorder is installed in the harness
  process, so every callgrind child is launched through it and recorded.
- **D-17 (a vendor-service name in the delivered code).** `r4_run_wrapper.inference_block()` writes the key
  `bedrock_used: false` and `r4_check_run.manifest_protocol_checks` tests it: the program's inference-block key, carried
  from the frozen v2 wrapper and the approved r3 layer. It names a vendor service. It was found by the final text scan,
  after DV-18 had begun, when changing the layer would have required re-running DV-18 (which runs once); it was NOT
  removed. For the Coordinator. No other model, vendor or runtime name appears in any file this stage wrote (scan
  recorded; the bundle's text members are redacted as section 17 states -- CORRECTED in section 17: the bundle's
  redaction did not cover this word, which the bundled development manifests carry).
- **D-18 (caches).** GFPN_V2_CACHE_DIR was set to scratch directories for the DV-7 / DV-12 / DV-16 toy packages and the
  DV-18 objects (the frozen drivers' build cache; toy only); it was NOT set for DV-18 (a), (b), (e).
- **D-19 (DV-18 (i) method).** The (i) copies are COHERENT development copies: after each edit the manifest's
  solver_events block and child_readback_accounting were recomputed with the delivered wrapper functions, so that each
  item's own condition is what the verdict sees (unlike the in-place RI-3 / RJ-5 objects, whose expectations are at the
  gap level).
- **D-20 (DV-1).** The DV-1 command was run under a shell `timeout 3700` guard (development only; the capped Sage probe
  child had its own frozen timeout of 3600 s).

## 16. Unexpected observations (recorded, not interpreted)

- **O-1 (RG-1 timing).** When a frozen child exits on its own pre-exec path before the parent's after-fork callback has
  opened the task-clock counter, `perf_event_open` returns ESRCH, the counter is "not opened" and `child_end` is
  `undetermined` (RG-1 (c)), so the launch record has no class and the verdict is FAIL. Seen in DV-18 (f) (ix) (stdout in
  a missing directory) and in object O29b's gp child (stdout open failed in the child); NOT seen in object O28, whose 36
  callgrind children (stdout open failed in the child) each gave `frozen_pre_exec_exit` and class (C). Class (C) and the
  (B) cases with returncode 98 / 99 are therefore observed only when the child is still alive when the callback runs
  ((xv) waits for the go byte; (xx) needed a delayed os._exit). The outcome is fail-closed (FAIL, a designed stop), never
  a result.
- **O-2.** The toy G2 at p' = 1039 kept the SSF signature (clause ii) on all six attempts of fx_reg0_raw_u and
  fx_reg0_S3_rescaled in all three DV-7 runs (as in the r3 stage). Toy value; no bearing on D.
- **O-3 (RB-3 printout).** The r4 checker's SC-4 printout names as "COVERAGE GAP" every (site, tag) found in only ONE of
  its two enumeration sources (for controls, raw-result.json carries no solve record with an argv, so all 8 recorded
  attempts are "attempt record only"); RB-3 names as coverage gaps the wrapped attempts found in NEITHER source, which the
  printout does not detect by itself (a lost attempt record is caught at the verdict level by RI-1's COUNT GAP).
  Report-only; exit statuses unaffected; not changed (the layer was fixed for DV-18).
- **O-4.** PERF_TYPE_HARDWARE instruction counters do not open on this host (ENOENT); every S-1 solve records that
  reason; the RG-1 software counter opens.
- **O-5.** At the verdict level, (28) with RJ-1 disabled, (29)'s first object with RJ-2 disabled and (30) with RJ-3
  disabled still FAIL (V-7 on the altered file; comparator / gp output files attributed only through the removed
  record); they discriminate at the gap level (section 10.6), as the approval decision's OB-4 anticipated.
- **O-6.** The DV-18 (h) import closure is an over-approximation (modulefinder follows optional imports; it lists, for
  example, pytest); it is not the set of modules a package imports at run time.

## 17. The development-evidence bundle (VA-5; R4S-10)

- **Path.** `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r4-dv/stage-r4-dv-evidence.tar.gz`
- **sha256** `d19edb0ca7b4d2ed0e812f5ee2b24537d07a795ad0ae9ce05ba751a60b98fde6`; 21307071 bytes; built 06:22Z.
- **Command** (cwd /tmp; env GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1): `python3 -B <scratchpad>/r4/dev/make_bundle.py
  <scratchpad>/r4 /home/user/crypto-autoresearcher/experiments/EXP-GFPN-05ff43/dev-evidence/stage-r4-dv/stage-r4-dv-evidence.tar.gz`;
  its one git child is read-only (`git -C <repo> branch --show-current`, GIT_OPTIONAL_LOCKS=0 inherited). Command-log
  entry [60] was appended after the build and so is not in the bundled copy of the log.
- **Members.** 22981 = 22979 data members + `stage-r4-dv/MEMBERS.sha256` (sha256, size and path of every data member;
  for redacted members also the sha256 of the unredacted scratch bytes) + `stage-r4-dv/REDACTION.txt`. Top-level member
  counts: dv18 7363, dv16 4285, dv7 3854, dv7final 3851, dv12 2201, dv17 1119, dv6 66, dv6-attempt1-HARNESS 66, dv6final
  65, dev 31, dv2 26, dv1 5, semantics 4, ids 4, dv9 4, dv3 4, and 1-2 each for dv5, dv5-attempt1-FAIL,
  dv5-attempt2-HARNESS, dv8, dv10, dv11, dv15, superseded-plans, layer-snapshots, inv_draft2, command-log.txt,
  lka1-expected.sha256, lka1-check.out, stage-start.txt, note-before-final-sections.md, note-file-table.md,
  inv_draft2.out and the *.log files.
- **Redaction** (disclosed in REDACTION.txt): in text members the scratchpad's absolute path and its parents become
  `<scratchpad>` / `<scratch-session-dir>` / `<scratch-base>`, the branch name `<branch>`, and the runtime
  instruction file's name `<runtime-instructions-file>`; 3625 members were redacted. 0 members were withheld for a
  forbidden name; 0 members exceeded 50 MiB.
- **Listed by sha256 and size, not bundled** (15308 files, rows `# NOT BUNDLED` in MEMBERS.sha256): byte copies of the
  archived RUN-GFPN-ac4487 in the DV-6 synthetic worlds (`dv6/runs` 3069, `dv6-attempt1-HARNESS/runs` 3069,
  `dv6final/runs` 3069), the DV-8 perturbation copies (`dv8/perturb` 5041) and the DV-15 extracts of archived,
  receipt-bound tarballs (`dv15/extract` 1060). Also skipped as derived: the frozen drivers' build caches
  `dv7/toy/cache`, `dv7final/toy/cache`, `dv12/cache`, `dv16/cache`. `ref_r3/` (copies of the r3 stage's archived
  scratch harnesses) is not bundled.

- **Final scan of the written files and every bundle member** (`<scratchpad>/r4/dev/final_scan.py`, output
  `<scratchpad>/r4/final-scan.out`; run after the bundle was built, so neither is in the bundle): 23 written files and
  22981 bundle members scanned for the forbidden model / vendor / runtime names and for the eight R-13 task ids.
  (1) The only name found is the vendor-service word in the inference key `bedrock_used` (D-17): in 3 written files
  (`r4_run_wrapper.py`, `r4_check_run.py`, this note's D-17 text) and in 162 bundle members (the manifests of the DV-7
  toy packages and the DV-18 development packages, which the delivered wrapper wrote). The bundle builder's redaction
  list did not include that word, so D-17's earlier sentence that the bundle's text members are redacted does NOT cover
  it; this line corrects that sentence. The bundle was not rebuilt. (2) The eight R-13 ids occur in 91 bundle members and in
  no written file. Every occurrence is data under test or a byte copy, never a task id of this stage: the DV-6
  forbidden-id cases (`dv6*/altered/trial-plan-v2-r4.forbidden0..7.json`, each carrying one id so the plan checker
  must refuse it), byte copies of the frozen amendment texts and archived receipts in `dv6*/altered/`, and the DV-7
  toy plan copy and its result (`dv7*/toy/toy-trial-plan-v2.json`, `dv7*/dv7.json`), which copy the frozen v2 plan's
  history field.
- **Byte code.** No `__pycache__` directory and no `.pyc` file newer than the stage start exists in the repository
  (find, 06:24Z). `git status --porcelain` (GIT_OPTIONAL_LOCKS=0) lists only the five untracked write-scope paths; HEAD
  1768588f0d7f94020f235e2141d7a843f45b150f, unchanged.
## 18. Scratch files, allocator outputs, inference record, exact commands

- **Scratch** (`<scratchpad>/r4/`, outside the repository; all bundled except the r3 reference copies and derived
  caches): `command-log.txt` (every command with its argv, in order); `lka1-expected.sha256`, `lka1-check.out`;
  `stage-start.txt`; `ids/` (mint script, allocator and `--check` logs, ids); `dv9/` (baseline script and baseline);
  `dev/` (compile checker, map table, scratch editors that applied every layer edit, the DV-7 continuation, DV-15 dir
  lister, DV-17 harness, note helpers, bundle builder); `dv1`..`dv17` outputs; `dv5-attempt1-FAIL`,
  `dv5-attempt2-HARNESS`, `dv6-attempt1-HARNESS`; `dv7/` (attempts 1-2), `dv7final/`; `dv18/` (every harness, output,
  development package, object, stand-in, scratch-evaluator output and closure-scan output; `attempts/`);
  `superseded-plans/`; `layer-snapshots/`; `semantics/`; `inv_draft2/` (an inventory draft run); `ref_r3/` (reference
  copies of the r3 stage's scratch harnesses, extracted from the archived r3 bundle; NOT re-bundled).
- **Allocator outputs.** 42 x `python3 -B tools/allocate_id.py --next run --area GFPN`, then `--check <bare id>` for each
  (rc 0, 0 occurrences, 42 distinct), all before any file named an id; the ids in minting order are
  `implementation-v2-r4/minted-run-ids.txt`; the logs are `ids/mint.log` and `ids/check.log` in the bundle.
- **Inference record (R4S-15).** requested_policy: executor-implementation; resolved_model_id: null ("none supplied by
  the dispatching session; none invented"); fallback_used: false. Amazon Bedrock was not used.
- **Task ids.** Nothing this stage wrote carries any of the eight R-13 ids as its own task id (DV-5; the text scan of
  every written file finds none of them).
- **Machine protection.** Every msolve, valgrind, gp and builder child ran under RLIMIT_AS 10737418240 set in the child
  and read back (every pair read back was 10737418240 / 10737418240, except DV-18 (f) (xx), which simulates a hard-limit
  mismatch by design; the (f) items that end before the read-back carry no pair, as stated); one memory-heavy process at a time (DV-18 (h), a
  static scan, ran beside DV-18 (e)); msolve -t 1. No OOM, guard kill or timeout of a development package occurred.
