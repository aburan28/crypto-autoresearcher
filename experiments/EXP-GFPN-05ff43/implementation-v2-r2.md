# EXP-GFPN-05ff43 — implementation note, protocols 2-r2 and 2-a1-r2 (successor stage, TASK-20260923-de3a7d)

> **STAGE OUTCOME: STOP at DV-11 (solverevent SE-3 / SE-9 as incorporated; card ST-8), recorded at 2026-09-24T02:10:05Z.**
> `implementation-v2-a1/a1_health.py` `run_system` launches msolve and classifies its output (lines 144, 147, 182)
> outside `v2_driver.solve`. It is reached from `controls-a1` (RUN-GFPN-599b87, package 1 of trial-plan-v2-a1-r2.json), so
> the SE-3 wrapper cannot reach it. **Neither r2 plan is treated as final.** No run package exists. No frozen byte changed
> (DV-9). This is an impediment for a new Coordinator decision. It is never evidence about D, H-GFPN-9a29be or
> HEUR-GFPN-DFLAT. Sections 1 and 12 have the details. (This banner was added at the end of the stage. The section below it
> was written first, as it states.)

(Section written first, at 2026-09-24T01:48:08Z. At that time neither `trial-plan-v2-r2.json` nor `trial-plan-v2-a1-r2.json`
existed. This satisfies DEC-20260923-80e280 RC-4 (b), re-pointed to r2 (card ST-5). The rest of this note follows below this
section.)

## RC-4 (b): declared metadata key paths (JSON pointer), recorded before either plan was written

`trial-plan-v2-r2.json` (11 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed (2 → "2-r2") | protocol label |
| `/task_id` | changed (→ TASK-20260924-946010) | task ids |
| `/written_by_task` | added (TASK-20260923-de3a7d) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-689d2f phase A (Coordinator)") | archived_by |
| `/repair` | added (SC-1 content) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed) | gate.regression |
| `/id_map` | added (31 entries, v2 → r2) | id map |
| `/v2_ids_never_reused` | added (the 31 frozen v2 ids) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids) | never-reused lists |
| `/retired_ids` | added (used v2 ids kept as records; the 82 retired ids: 29 v2, 11 v2-a1, 42 r1) | retired id lists |
| `/ceiling_note` | added (2 existing + 31 + 11 = 44 of 48) | ceiling note |

`trial-plan-v2-a1-r2.json` (12 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed ("2-a1" → "2-a1-r2") | protocol label |
| `/task_id` | changed (→ TASK-20260924-9490b1) | task ids |
| `/written_by_task` | changed (TASK-20260923-4c64b5 → TASK-20260923-de3a7d) | task ids |
| `/archived_by` | changed (→ "TASK-20260924-689d2f phase A (Coordinator)") | archived_by |
| `/repair` | added (SC-1 content) | the `repair` block |
| `/gate/regression` | added (REG-1, d-parsed) | gate.regression |
| `/id_map` | added (11 entries, v2-a1 → r2) | id maps |
| `/id_map_v2` | added (31 entries, v2 → r2) | id maps |
| `/frozen_v2_ids_never_reused` | added (the 31 frozen v2 ids; RC-4 (d)) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids; RC-4 (d)) | never-reused lists |
| `/retired_ids` | added (as in the v2-r2 plan) | retired id lists |
| `/ceiling_note` | added | ceiling note |

In `trial-plan-v2-a1-r2.json` the pre-existing `/v2_ids_never_reused` is NOT a declared key. It is mapped like every other
field, so its image lists the 31 r2 v2 ids (RC-4 (d)). The frozen v2 and v2-a1 ids are carried under the added keys
`/frozen_v2_ids_never_reused` and `/a1_ids_never_reused`; the 42 r1 ids under `/retired_ids`. `/gate/v2_blocking_packages`,
`/gate/addendum_blocking_package` and aggregate_a1's `driver_args` are not declared keys; they are mapped through M.
The derivation source is the FROZEN plans (trial-plan-v2.json sha256 16f33e39...4e16; trial-plan-v2-a1.json sha256
2a788720...5ac6), not the r1 plans (card ST-5).

## RC-4 (a): the union map M (42 entries), recorded before either plan was written

Assignment rule (as stage R1): ids are taken in minting order (`implementation-v2-r2/minted-run-ids.txt`, section 15). The first
31 go to the packages of `trial-plan-v2.json` in plan order; the next 11 to the packages of `trial-plan-v2-a1.json` in plan
order. The r1 id of the same frozen package is shown for reference only; every r1 id is retired.

id_map_v2 (31):

| order | frozen v2 id | r2 id | (retired r1 id) | label |
| --- | --- | --- | --- | --- |
| 1 | RUN-GFPN-ac4487 | RUN-GFPN-a09162 | RUN-GFPN-a61a10 | F-1..F-3 fixture, n = m = 3, p' = 4111 |
| 2 | RUN-GFPN-3377f1 | RUN-GFPN-0dca26 | RUN-GFPN-30d3ee | F-1..F-3 fixture, n = m = 3, p' = 16777291 |
| 3 | RUN-GFPN-76420e | RUN-GFPN-b69444 | RUN-GFPN-b0993b | jv_anchor_system_trace_identity, p' = 16777291, n = 5, m = 4 (rulings.DC-5) |
| 4 | RUN-GFPN-b231c1 | RUN-GFPN-22ee49 | RUN-GFPN-3e521f | frozen controls: degenerate_symmetrization_identity, orbit_lifting_verifier, known_scalar_instances |
| 5 | RUN-GFPN-a07776 | RUN-GFPN-bf833b | RUN-GFPN-4fc824 | F-4 secondary fixture, n = m = 4, GF(4111^4), b a square (NOT blocking) |
| 6 | RUN-GFPN-1ad09b | RUN-GFPN-4bafcf | RUN-GFPN-27c136 | build p' = 4111 (m = 5 and m = 4; all shapes; refusal rows) |
| 7 | RUN-GFPN-0c7483 | RUN-GFPN-93607c | RUN-GFPN-fc29b6 | cells p' = 4111, ecgfp5_shaped, m = 5 |
| 8 | RUN-GFPN-4abae0 | RUN-GFPN-3a01f3 | RUN-GFPN-072f55 | cells p' = 4111, random_2torsion, m = 5 |
| 9 | RUN-GFPN-9e4212 | RUN-GFPN-4ea41a | RUN-GFPN-a6ac23 | cells p' = 4111, random_no2torsion, m = 5 |
| 10 | RUN-GFPN-bbbbe3 | RUN-GFPN-b9059b | RUN-GFPN-d48e01 | cells p' = 4111, ecgfp5_shaped, m = 4 |
| 11 | RUN-GFPN-a521dd | RUN-GFPN-bebfc0 | RUN-GFPN-9696d7 | cells p' = 4111, random_2torsion, m = 4 |
| 12 | RUN-GFPN-a07b6d | RUN-GFPN-48c73f | RUN-GFPN-d6468a | cells p' = 4111, random_no2torsion, m = 4 |
| 13 | RUN-GFPN-dc1d4e | RUN-GFPN-724745 | RUN-GFPN-98d454 | build p' = 262151 (m = 5 and m = 4; all shapes; refusal rows) |
| 14 | RUN-GFPN-b9207c | RUN-GFPN-477ae1 | RUN-GFPN-bda7a9 | cells p' = 262151, ecgfp5_shaped, m = 5 |
| 15 | RUN-GFPN-aa56bd | RUN-GFPN-479e05 | RUN-GFPN-1bcead | cells p' = 262151, random_2torsion, m = 5 |
| 16 | RUN-GFPN-e5b90d | RUN-GFPN-c3fb79 | RUN-GFPN-b76390 | cells p' = 262151, random_no2torsion, m = 5 |
| 17 | RUN-GFPN-d2f759 | RUN-GFPN-ecefab | RUN-GFPN-aad5a9 | cells p' = 262151, ecgfp5_shaped, m = 4 |
| 18 | RUN-GFPN-745cad | RUN-GFPN-4189b4 | RUN-GFPN-286cdb | cells p' = 262151, random_2torsion, m = 4 |
| 19 | RUN-GFPN-aeff00 | RUN-GFPN-ff8c15 | RUN-GFPN-4e37c2 | cells p' = 262151, random_no2torsion, m = 4 |
| 20 | RUN-GFPN-3db273 | RUN-GFPN-6c464c | RUN-GFPN-5cb274 | build p' = 16777291 (m = 5 and m = 4; all shapes; refusal rows) |
| 21 | RUN-GFPN-3be8a4 | RUN-GFPN-0bb551 | RUN-GFPN-1626b4 | cells p' = 16777291, ecgfp5_shaped, m = 5 |
| 22 | RUN-GFPN-00e64b | RUN-GFPN-f78382 | RUN-GFPN-2d52fc | cells p' = 16777291, random_2torsion, m = 5 |
| 23 | RUN-GFPN-c5294d | RUN-GFPN-f4302b | RUN-GFPN-f917a8 | cells p' = 16777291, random_no2torsion, m = 5 |
| 24 | RUN-GFPN-36cad2 | RUN-GFPN-beac9f | RUN-GFPN-5fc8d7 | cells p' = 16777291, ecgfp5_shaped, m = 4 |
| 25 | RUN-GFPN-11d2ad | RUN-GFPN-d9f68f | RUN-GFPN-8b0643 | cells p' = 16777291, random_2torsion, m = 4 |
| 26 | RUN-GFPN-fc5d58 | RUN-GFPN-c8be8b | RUN-GFPN-e2a2a5 | cells p' = 16777291, random_no2torsion, m = 4 |
| 27 | RUN-GFPN-8f86cc | RUN-GFPN-2f3442 | RUN-GFPN-3e568b | aggregate: ladder table, like-for-like scoring, HEUR-GFPN-DFLAT, F4, band (B-3) |
| 28 | RUN-GFPN-e26e4b | RUN-GFPN-9e266d | RUN-GFPN-25adbd | contingency 1 |
| 29 | RUN-GFPN-9da048 | RUN-GFPN-c3062b | RUN-GFPN-a3773d | contingency 2 |
| 30 | RUN-GFPN-59320d | RUN-GFPN-cfe871 | RUN-GFPN-cb9dff | contingency 3 |
| 31 | RUN-GFPN-1596f6 | RUN-GFPN-c8c1f8 | RUN-GFPN-3868df | contingency 4 |

id_map_a1 (11):

| order | frozen v2-a1 id | r2 id | (retired r1 id) | label |
| --- | --- | --- | --- | --- |
| 1 | RUN-GFPN-0d91bf | RUN-GFPN-599b87 | RUN-GFPN-14cfa2 | controls_a1, p' = 1073741831 (BLOCKING for the addendum) |
| 2 | RUN-GFPN-8c772a | RUN-GFPN-af4935 | RUN-GFPN-dd64d4 | build p' = 1073741831 (m = 5 and m = 4; all shapes; refusal rows) |
| 3 | RUN-GFPN-569fd7 | RUN-GFPN-ad6372 | RUN-GFPN-097656 | cells p' = 1073741831, ecgfp5_shaped, m = 5 |
| 4 | RUN-GFPN-086463 | RUN-GFPN-b0bfca | RUN-GFPN-8fd922 | cells p' = 1073741831, random_2torsion, m = 5 |
| 5 | RUN-GFPN-bab146 | RUN-GFPN-a11a01 | RUN-GFPN-a901d9 | cells p' = 1073741831, random_no2torsion, m = 5 |
| 6 | RUN-GFPN-7dd55d | RUN-GFPN-585023 | RUN-GFPN-6435b2 | cells p' = 1073741831, ecgfp5_shaped, m = 4 |
| 7 | RUN-GFPN-47aa51 | RUN-GFPN-411471 | RUN-GFPN-f7733e | cells p' = 1073741831, random_2torsion, m = 4 |
| 8 | RUN-GFPN-3a70f1 | RUN-GFPN-09fbad | RUN-GFPN-3a1c9f | cells p' = 1073741831, random_no2torsion, m = 4 |
| 9 | RUN-GFPN-ae4918 | RUN-GFPN-20faaa | RUN-GFPN-c8870b | aggregate_a1 (A1-5 (i)-(v); A1-3; A1-4; DEC-20260923-8b2dbf AA-4) |
| 10 | RUN-GFPN-8cfac3 | RUN-GFPN-dc7e11 | RUN-GFPN-8e4d7d | contingency a1-1 |
| 11 | RUN-GFPN-6a7f35 | RUN-GFPN-0fa6cd | RUN-GFPN-51e56b | contingency a1-2 |

## 1. STAGE OUTCOME: STOP at DV-11 (solverevent SE-3 and SE-9 as incorporated; card ST-8)

> **STOP, recorded at 2026-09-24T02:10:05Z.** DV-11 found a CLASSIFIED msolve launch OUTSIDE the SE-3 wrapper:
> `implementation-v2-a1/a1_health.py` `run_system` launches `/usr/bin/msolve` (`V.msolve_argv`, line 144; `V.run_child`,
> line 147) and passes the output to `V.classify_solve` (line 182). The run never passes through `v2_driver.solve`.
> It is reached from `a1_driver.cmd_controls_a1` check (d) (`H.run(p, ...)`, a1_driver.py line 129), that is, from
> `controls-a1 --p 1073741831`, package order 1 of `trial-plan-v2-a1-r2.json` (RUN-GFPN-599b87, the addendum's
> blocking package, the image of controls_a1). The r2 layer cannot route it through the wrapper without replacing a
> function other than `v2_driver.solve`, which ST-1 forbids. Under ST-8 the stage STOPS and returns. **Neither r2
> plan is treated as final.** No run package exists. No frozen byte changed (DV-9). The stop is an impediment for a
> new Coordinator decision. It is never evidence about D, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
> The Executor's code reading PREDICTED this before any check ran, and it was reported to the dispatcher at the
> time. The dispatcher's reply left the stop binding and accepted the check order below. DV-11 was then run as the
> card defines it. Its result is the evidence of the stop (section 12). The prediction is not.

## 2. Binding, scope and sequencing checks

- **SC-1.** Checked at 2026-09-24T01:32Z, before any file was written. All five sha256 values equal the bound values:
  - `v2_addendum_paristack.yaml`: 856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7;
  - `v2_addendum_rung31.yaml`: 2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c;
  - `v1_to_v2_reanchor_and_arm_iii.yaml`: e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3;
  - `v2_addendum_seedresolve.yaml`: dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81;
  - `v2_addendum_solverevent.yaml`: 011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f;
  - The in-file `status: draft` / `approved_by: null` of the paristack, seedresolve and solverevent files is expected (SC-1).
- **Repository state at start.** HEAD was 0b90f70b30f2b39d7342fd4a1d7027ca085faf8d, the claim commit of this card.
  `git status --porcelain --untracked-files=all` was empty.
- **DV-9 baseline.** Taken at 2026-09-24T01:32:51.885287Z (the stage start), before any write. It covers 420 files under the
  frozen paths: the specification, all amendments, implementation/, implementation.md, trial-plan.json, implementation-v2/,
  implementation-v2.md, trial-plan-v2.json, implementation-v2-a1/, implementation-v2-a1.md, trial-plan-v2-a1.json,
  implementation-v2-r1/, implementation-v2-r1.md, both r1 plans, dev-evidence/{seedresolve-premise,
  solver-characterization, stageR1-dv7}, both run packages and execution-report-v2.yaml.
- **SC-6.** The pre-existing, gitignored `implementation/__pycache__/` (v1 tree) was listed before any write and again by DV-9.
  It is neither deleted nor staged. Its contents, unchanged:
  - `__pycache__/` 4096 2026-09-23T03:17:31.750504Z;
  - `gfpn5_core.cpython-311.pyc` 25364 2026-09-21T16:07:21.278154Z;
  - `pdp_cell.cpython-311.pyc` 100532 2026-09-23T03:17:31.750504Z;
  - `pdp_common.cpython-311.pyc` 18825 2026-09-22T00:10:07.959907Z;
  - `symmetrize.cpython-311.pyc` 52075 2026-09-22T00:10:07.952871Z;
  - `verify_independent.cpython-311.pyc` 14617 2026-09-22T00:10:07.964654Z.
- **Sequencing (ST-11; DP-7).**
  - `runs/` held 50 directories (the 48 v1 packages, RUN-GFPN-ac4487 and RUN-GFPN-3377f1) and `.gitkeep`.
  - No directory exists for any of the 42 new ids or any of the 82 retired ids (DV-10).
  - Nothing under `runs/` was read except RUN-GFPN-ac4487 (REG-1 reference, DV-8, DV-15) and RUN-GFPN-3377f1. Of
    RUN-GFPN-3377f1 only the failure text quoted in the paristack addendum was used, as DV-3's reference string.
- **Host.** MemTotal 16481980 kB, SwapTotal 0, 4 CPUs, Python 3.11.15, cypari2 2.2.0 (PARI 2.15.4), gp 2.15.4,
  msolve 0.6.5-1build2 at /usr/bin/msolve, always `-t 1` (argv unchanged).
- **Memory guard (DP-4; AC-1; SC-8).**
  - The dispatcher's guard is `scratchpad/memguard.sh`, pid 875 (seen running at 01:44Z).
  - Its threshold is MemAvailable < 2621440 kB, about 13.2 GiB in use on this host. That is above 12.0 GB, so the child
    cap stays **RLIMIT_AS 10737418240**. It is set in each child and read back with getrlimit (section 11).
- **Machine quiet.** At 01:44Z and again before DV-12 no msolve, gp, sage or valgrind process was running. Every
  development process ran alone, in sequence.
- **No outer guard.** No development process was wrapped in `timeout` or any other guard. The only child timeouts in
  use are:
  - the frozen code's own per-target timeouts;
  - `run_child` timeouts in the checks: 7200 s for the RC-5 gp cross-check (as a1_pari) and 3600 s for the Sage
    start-up probe;
  - the SF-2 (c) cap, exercised in DV-12 (f).
- **Byte code.** Every Python process ran with `-B` and PYTHONDONTWRITEBYTECODE=1. DV-9 found no byte code newer than
  the stage start under any frozen tree.
- **PYTHONHASHSEED (CORR-20260923-111265; SE-6).** The r2 wrapper sets "0" in the driver child's environment.
  - DV-12's eight packages read back "0" inside the driver process (section 10, DV-13 partial).
  - The SC-11 (f) world-B override, a development-only in-process change of `r2_run_wrapper.DRIVER_PYTHONHASHSEED`, was
    NOT used, because the SE-5 probe did not run (STOP).

## 3. Files written (the exact list; for each r2 file, the r1 file and sha256 it started from, or "new")

`experiments/EXP-GFPN-05ff43/implementation-v2-r2/` (15 files; sha256 of the final bytes):

| file | role | started from (r1 file, sha256) | sha256 |
| --- | --- | --- | --- |
| `r2_common.py` | shared context; five bound hashes; ids and retirement lists; PS-1 P-A configuration; RC-2 read-backs; RC-3 read-back helper; SE-6 hash-seed read-back; pari-stack.json | `implementation-v2-r1/r1_common.py` ea3ea5da076a544cca3b4c4fe1fbc72da129ed734d405336b871879a6ee107c0 | 6b34cf03bb90d9d96d795f9530f9b28b53e29abbcf472e9fed3d85aa34647872 |
| `r2_resolve.py` | the SE-3 re-solve wrapper of v2_driver.solve (SE-2 with SF-1, SF-2, SF-3; SC-11); install / SE-3 read-back / begin; solver-events.json | new | ee2b755c242cb681e03f8f69ea94389dcb97977459d7da2783bad872e9107438 |
| `r2_entry_v2.py` | entry point, v2 driver commands (PS-2 (a)); RC-3 (a), SE-3, read-backs | `implementation-v2-r1/r1_entry_v2.py` 82594a7b3830e79acc83514966b87525e1777a0bbf690b2748b5499901e907b4 | ea157d9479f8e6968116abd09326274d62cbfa6eedcf1a40b49e3aa5552c08a7 |
| `r2_entry_a1.py` | entry point, v2-a1 driver commands (PS-2 (a)); RC-3 (b), SE-3, read-backs | `implementation-v2-r1/r1_entry_a1.py` f404a2d96985b84dda78340f29d5792c97499217acf28d65d3424b3864c971fd | 5d2c6d93f3b56eaaf788149f8671407ebcf6d4a483247b9447f91a50b0e058c7 |
| `r2_run_wrapper.py` | r2 run wrapper, R-1..R-13 re-pointed, --dry-run, PYTHONHASHSEED "0", manifest incl. `solver_events` (PS-2 (b)) | `implementation-v2-r1/r1_run_wrapper.py` b3d00e1ada7af2e39331bab0013f564be591bda2228b7ebe51944436734fb9d6 | bccf6b2fff50aa8d24899d0899a8c009f9c20104562152eb1c08d16b0f3bfb47 |
| `r2_check_run.py` | r2 completion-gate checker incl. SC-4 accounting (PS-2 (c)) | `implementation-v2-r1/r1_check_run.py` 87d23924a3f1c317eaf1773683b365631a538d22836da698829a6517052812d6 | 2fc5c141b18e8150654fb1ad018da0014c9b91a9883a6c3a76f845df3f665b9c |
| `r2_reg1.py` | REG-1 comparator, (d) branch d-parsed, SE-4 solver-events conditions (PS-2 (c)) | `implementation-v2-r1/r1_reg1.py` 1b4e4c880f829e8f04915c6a55b9274c9391c6dea701880f63671963db7d1d26 | 2bf7f5d6108b7965b747e0de015e1a5fcab76888ea0b9c0415522d49a8d7bd3d |
| `r2_accounting.py` | SC-3 / SC-4 parametrisation accounting (frozen v2_solver read-only; no child) | new | 4f8c3a72dcf602bd79a5bf1283bf970a3c6c56511cc6f086fff25f60c1416378 |
| `reg1-exclusion-list.json` | REG-1 exclusion list X1..X17, byte-identical copy of the r1 list (SE-4 (e)) | byte-identical copy of `implementation-v2-r1/reg1-exclusion-list.json` 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c | 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c |
| `r2_make_plans.py` | plan writer (PS-2 (d)) | `implementation-v2-r1/r1_make_plans.py` e58720cd1ee8f876fd97a5e19bcb49dab4cbac30f6bb31eb37fcf7fbf73f2e0e | 78c6d85c6be925fbf32f5da9a53a2df671ac4d3139caa779b84225f9f2bfb17a |
| `minted-run-ids.txt` | the 42 ids in minting order (plan-writer input) | new | 5ddf35148a3dfa73dc82bde80f6cb0c6dd114ea22751c42d19af6436156ff1a0 |
| `r2_devchecks.py` | development checks: DV-2, DV-3, DV-4, RC-2 semantics probe, dispatcher (PS-2 (e)) | `implementation-v2-r1/r1_devchecks.py` b777a27b139ff6059be7bd01987638765799e3ecd5f8b1601428f60c480789f4 | f16470ead2437e60107b4fe70b29f2e67b635c7cd557ab21712474ea74d916bc |
| `r2_devchecks_more.py` | development checks: DV-1 static + Sage probe, DV-5, DV-8, DV-9, DV-10, DV-11, DV-15 (a), DV-15 (b) | `implementation-v2-r1/r1_devchecks_more.py` 99e1f144adb95a30d8290065a948200f90864263916db76f1c6a1ccb843b8c00 | be7b332df0fbcd881846ff03bf6ae27c3f248db855ced0db88b119bab7e59bab |
| `r2_dv6.py` | development check DV-6 | `implementation-v2-r1/r1_dv6.py` d3eac6bfa5a13a1e4beb62ec2246766d09790d6ef8962a6e39d9748d734c4507 | 8ed298d5303169c506acd6eebdf18fdf30ba82beb04df3293e442e25c4cf19dc |
| `r2_dv12.py` | development check DV-12 (a)-(g) harness and its development-only shim (scratch toy copy) | new (its `toy_fixture_n3` reproduces r1_toy.py lines 56-75, from `implementation-v2-r1/r1_toy.py` e72582251725b9dcc355264521903b2ded2a2884d8c4b73a5243c29834fafc82; no r1 module is imported) | a0888082cb6bc98cf84b859b51d0cf84ea09919ed11d6e9affff45e0674a6d91 |

The other paths written:

- `experiments/EXP-GFPN-05ff43/trial-plan-v2-r2.json`: sha256 d3bf5d74884c870c1d4996085651c3057322d6153875246bedd96c2f542b75ff;
- `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r2.json`: sha256 121202cb9ba971218d5491c4553f29fb872dfa225903dad620e3db29e27cb1e5;
- `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r2-dv/stage-r2-dv-evidence.tar.gz`: sha256 307c98f98505094b2073bdc7090b68d21eafa9f6bd3060dcb2cec2d75127b508, 1688182 bytes (section 14);
- this note.

Nothing else was written in the repository. No r2 file imports an r1 module. Development outputs are in
`/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/stageR2/` (below, `$S`) and in the bundle.

## 4. PS-1: the branch, the values, the API and the RC-2 read-back semantics

- **Branch: P-A.** No P-B trigger condition occurred.
  - DV-2 passed at every point with no overflow, no VmHWM excess and no read-back mismatch.
  - `v2_common.curve_order_pari` is not replaced, and no P-B code exists in the layer.
  - `pari_child_timeout_s` is absent from both plans (it is P-B only).
  - Both r2 plans record `repair.ps1_branch: "P-A"` with `repair.ps1_branch_evidence`.
  - Because the stage STOPPED, the plans are not final (ST-8).
- **Values.** parisize 67108864 and parisizemax 536870912. No other value is used anywhere.
- **API.** In each entry process, `r2_common.PariStack.configure()` runs
  `h = cypari2.Pari(); h.allocatemem(67108864, 536870912, silent=True)`.
  - In cypari2 2.2.0 this calls `set_pari_stack_size`, which calls libpari `paristack_setsize`.
  - The call is made BEFORE the entry imports any v2 or v2-a1 module. The entry imports only `r2_common` and
    `r2_resolve`, and neither imports a v2 or v2-a1 module.
  - `pari-stack.json` records `configured_before_first_v2_or_a1_import` (true in every entry run), the cypari2 version
    (importlib.metadata) and the PARI library version (RC-2 (c)).
- **Why a fresh handle keeps the configuration.** As established in stage R1, cypari2 2.2.0 `Pari.__init__` never lowers
  the configured sizes. The RC-2 read-backs confirm it in every r2 entry run of this stage (DV-2 workers; the eight DV-12
  packages).
- **RC-2 (a) start read-back.** After all imports and immediately before dispatch, the entry reads `default(parisize)` and
  `default(parisizemax)` through a fresh `cypari2.Pari()`, then again through a second fresh handle. It exits 2 before
  any command unless all four readings are exact.
- **RC-2 (b) exit read-back.** At exit (normal or exception) the entry reads both through the RETAINED second handle, plus
  `/proc/self/status` VmHWM / VmRSS / VmPeak / VmSize. Everything goes into `pari-stack.json`, and the wrapper copies it
  to `resources.pari_stack`.
- **RC-2 (b) semantics: established as "requested" in THIS stage.** Semantics probe, 01:46:15Z:
  - `my(v = vector(4000000, i, i^2 + 2^70)); #v` grew the stack to 134217728 and then to 268435456 (stderr warnings).
  - After the growth, `default(parisize)` still read 67108864 and `default(parisizemax)` read 536870912, while
    `stacksize()` read 268435456.
  - A fresh handle constructed afterwards reset the current size to 67108864.
  - So on this host `default(parisize)` reports the requested size, and the exit rule is exact equality: 67108864 and
    536870912 (`r2_common.PARISIZE_EXIT_SEMANTICS = "requested"`, applied by `r2_check_run`).
  - Record: `$S/semantics/semantics.json`.

## 5. RC-3 redirections and the SE-3 replacement (in-process only)

| entry | attribute | frozen value | r2 value | set when | reason |
| --- | --- | --- | --- | --- | --- |
| r2_entry_v2 | `v2_common.PLAN_PATH` | `experiments/EXP-GFPN-05ff43/trial-plan-v2.json` | `experiments/EXP-GFPN-05ff43/trial-plan-v2-r2.json` | after `import v2_common`, before `import v2_driver` | PS-2 list; RC-3 (a); ST-3 (a) |
| r2_entry_v2 | `v2_common.TASK_ID` | TASK-20260923-cd932c | TASK-20260924-946010 | same | ST-3 (a) |
| r2_entry_v2 | `v2_driver.solve` (SE-3 replacement) | the frozen function `v2_driver.solve` (v2_driver.py line 158) | `r2_resolve.solve`, which calls the recorded ORIGINAL | after `import v2_driver`, before dispatch | SE-3; ST-3 (c) |
| r2_entry_a1 | `a1_common.PLAN_A1_PATH` | `.../trial-plan-v2-a1.json` | `.../trial-plan-v2-a1-r2.json` | before `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `a1_common.V2_PLAN_PATH` | `.../trial-plan-v2.json` | `.../trial-plan-v2-r2.json` | before `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `a1_common.RECEIPT_V2_PHASE_B` | `coordination/.../TASK-20260923-0fa03f/post-run-receipt.json` | `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-689d2f/post-run-receipt.json` | before `import a1_driver` | ST-3 (b); RC-8 |
| r2_entry_a1 | `a1_common.V2_GATE_PACKAGES` | (RUN-GFPN-ac4487, RUN-GFPN-3377f1, RUN-GFPN-76420e, RUN-GFPN-b231c1) | (RUN-GFPN-a09162, RUN-GFPN-0dca26, RUN-GFPN-b69444, RUN-GFPN-22ee49), read from trial-plan-v2-r2.json `gate.blocking_packages` | before `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `a1_common.TASK_ID_RUNS` | TASK-20260923-6c7f55 | TASK-20260924-9490b1 | before `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `a1_common.PROTOCOL_VERSION` | "2-a1" | "2-a1-r2" | before `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `v2_common.PLAN_PATH` | set by `a1_common.redirect_v2()` at a1_driver import | = the redirected PLAN_A1_PATH (`trial-plan-v2-a1-r2.json`); never set to trial-plan-v2-r2.json | by redirect_v2 (a1_driver.py line 30) | RC-3 (b); ST-3 (b) |
| r2_entry_a1 | `v2_common.TASK_ID` | TASK-20260923-6c7f55 (redirect_v2's definition-time default) | TASK-20260924-9490b1 | AFTER `import a1_driver` | ST-3 (b) |
| r2_entry_a1 | `v2_driver.solve` (SE-3 replacement; a1_driver's `D`) | the frozen function | `r2_resolve.solve` | after `import a1_driver`, before dispatch | SE-3; ST-3 (c) |

- **Read-back (ST-3 (d)).** Each entry reads every redirected attribute and the SE-3 replacement back after all imports
  and immediately before dispatch. It exits 2 before any command unless all hold.
  - The SE-3 read-back (`r2_resolve.readback`) requires two things. First, `v2_driver.solve is r2_resolve.solve`.
    Second, the wrapper's recorded original is the frozen function object: module `v2_driver`, qualname `solve`, code
    file `implementation-v2/v2_driver.py`, first line 158, identical to the object captured at install.
  - The a1 entry also requires `a1_driver.C is v2_common` and `a1_driver.D is v2_driver`, and that the r2 gate ids equal
    `trial-plan-v2-a1-r2.json` `gate.v2_blocking_packages`.
  - The read-back goes into `pari-stack.json` under `redirections` (key `v2_driver.solve (SE-3 replacement)` for SE-3)
    and from there into the manifest. It records r2 values only.
- **Isolation (RC-3 (e); ST-3 (e)).**
  - `r2_check_run.py` runs `v2_check_run.main` or `a1_check_run.main` in a SEPARATE process, with only the redirections
    above applied.
  - The REG-1 comparator imports no v2_common, v2_driver or v2-a1 module. It imports the frozen `v2_solver` read-only,
    for the SF-4 parse functions only.
- **No further replacement.** No other function, class or computation is replaced. The P-A branch replaces nothing else.

## 6. The SE-3 re-solve wrapper (`r2_resolve.py`): SE-2 with SF-1, SF-2, SF-3 and SC-11

- **SSF signature (SF-1).** An attempt has the signature iff one of these holds:
  - outcome `degenerate_parametrisation` with reason:
    - (i) equal to "eliminating polynomial is not square-free";
    - (ii) beginning "eliminating polynomial degree ";
    - (iii) beginning "msolve reports square-free part degree ";
    - (iv) ending "parsed solution(s) fail substitution into the descended system";
  - (v) outcome `positive_dimensional` where the log text contains the exact string
    "[coefficients of linear form are randomly chosen]".
  - The log text is `.ms.log` + "\n" + `.ms.err` + "\n", read exactly as v2_driver.py lines 170-175 build it. The
    wrapper reads it after the frozen solve() returns; the frozen retention rule keeps both files (PR-3 (v)).
- **Attempts.** Attempt 1 is the frozen solve(), with the same arguments and argv.
  - On an SSF attempt k, while k < K + 1 = 6 (SF-3), the layer does four things:
    - records the attempt: outcome, reason, `dimension_of_quotient_printed`, `solution_info`, input sha256, output
      sha256, argv, the child's getrlimit read-back, start and end UTC with microseconds, wall seconds, the clause, and
      whether the random-form string was in the log;
    - renames `solver/<tag>.ms.out`, `.ms.log` and `.ms.err` by appending `.ssf-attempt<k>` to the full name (SC-11
      (a)), and records each renamed file's sha256 and size;
    - waits until at least 2.0 s after the attempt's recorded end (SC-11 (d));
    - calls the frozen solve() again with identical arguments.
  - The recorded result is the last attempt's result object, returned UNMODIFIED to the frozen caller. raw-result.json
    is written by the frozen driver from it, and the layer adds no field.
- **Cap (SF-2 (c); SC-11 (c), (e)).**
  - Attempt 2 always starts on an SSF attempt 1.
  - Attempt k + 1 (k >= 2) starts only if the summed wall seconds of attempts 2..k are below the `timeout_s` argument
    actually passed to that call. Each attempt's wall seconds are its recorded end UTC minus its recorded start UTC.
  - Otherwise the recorded result is attempt k's, and the event records `resolve_cap_reached` with the sums.
- **Consistency (SE-2 (4); SF-2 (b)), checked after every attempt.** Three conditions:
  - every attempt's input sha256 equals attempt 1's;
  - every printed quotient dimension is the same;
  - each attempt k >= 2 started at least 2.0 s after attempt k - 1's recorded end.
  - On a violation the layer writes the records and raises `SolverEventConsistencyError`. The entry records
    `command_raised_SolverEventConsistencyError`. The wrapper sees solver-events.json `consistency_violation: true` and
    no raw-result.json, and records the package failed / implementation_error (DV-12 (e), (g)).
- **Never (SE-2 (6)).**
  - gb_only calls pass straight through (counted).
  - The callgrind child runs only inside the frozen solve() after an ok outcome, so never on an SSF attempt.
  - Package re-runs, discretion, and changed flags, inputs or caps are all excluded.
- **Recording (SE-2 (5); SC-11 (b)).** Run-root `solver-events.json`, schema `crypto.autoresearch.gfpn05.r2.solver_events.v1`.
  - It is written atomically (temporary file, fsync, `os.replace`) after every wrapped call and every re-solve.
  - `r2_resolve.begin()` writes the initial file only after all entry read-backs pass, so it exists and parses even if
    no solve() runs.
  - It carries: K, the spacing, the cap rule; counters (wrapped calls, pass-through gb_only calls, attempts, SSF attempts
    per clause (i)-(v), re-solves, solves with an SSF attempt, solves still SSF after the last attempt,
    resolve_cap_reached, consistency violations); and one event per solve with at least one SSF attempt (or a
    consistency violation).
  - Disclosed addition: the counters are rewritten after every wrapped call, including calls without an event. SE-2 (5)
    names the events and the manifest block. The counters support the DV-11 dynamic count and the manifest block.
- **Manifest block `solver_events` (SC-11 (b)).** It is recomputed by `r2_run_wrapper` from solver-events.json and holds:
  K, the spacing, SSF attempts per clause, re-solves, solves still SSF after the last attempt, resolve_cap_reached (count
  and tags), `watchdog_after_resolve` (SF-2 (d): cells whose per-cell watchdog fired after a target with a re-solve), the
  file's sha256 and the consistency flag.
- **SE-6.** The wrapper sets PYTHONHASHSEED="0" in the driver child's environment (`r2_run_wrapper.DRIVER_PYTHONHASHSEED`).
  - The entry reads `os.environ["PYTHONHASHSEED"]`, `sys.flags.hash_randomization` and `hash("r2-hashseed-probe")`
    inside the driver process. They go into `pari-stack.json` `python_hash_seed_driver_readback` and the manifest
    `environment.PYTHONHASHSEED_driver_readback`.
  - The checker fails a package whose driver read-back is not "0".
  - No delivered entry reads any override. The world-B value "12345" (SC-11 (f)) can be set only by a development
    harness changing the module constant in its own process. It was not used, because DV-7 did not run.

## 7. The plans (PS-3; RC-4; SE-7; SF-7; SC-1)

- **Counts, labels and task ids.**
  - `trial-plan-v2-r2.json`: 31 packages (27 planned + 4 contingency), protocol_version "2-r2", task_id
    TASK-20260924-946010, written_by_task TASK-20260923-de3a7d, archived_by "TASK-20260924-689d2f phase A (Coordinator)".
  - `trial-plan-v2-a1-r2.json`: 11 packages (9 planned + 2 contingency), protocol_version "2-a1-r2", task_id
    TASK-20260924-9490b1, written_by_task TASK-20260923-de3a7d, the same archived_by, and plan_branch "31-bit",
    unchanged.
- **Order and ids.** These are the id_map tables in the RC-4 (a) section above. Package order equals the frozen order, and
  each id is the image of the frozen id at the same order (DV-5).
- **Gate.**
  - The r2 gate is (RUN-GFPN-a09162, RUN-GFPN-0dca26, RUN-GFPN-b69444, RUN-GFPN-22ee49).
  - The a1-r2 `gate.v2_blocking_packages` holds the same four ids, and `gate.addendum_blocking_package` is RUN-GFPN-599b87
    (the image of controls_a1).
  - `gate.regression` (REG-1, `d_branch: "d-parsed"`) is in both plans, with exclusion_list_sha256
    4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c.
- **aggregate_a1 driver_args.**
  - `--a1-runs` RUN-GFPN-ad6372,b0bfca,a11a01,585023,411471,09fbad;
  - `--v2-runs` holds the 18 r2 v2 cell ids (93607c ... c8be8b, frozen order);
  - `--v2-aggregate` is RUN-GFPN-2f3442.
- **`repair` block (SC-1).** It names:
  - paristack (id, path, sha256 856fdc1d...c7, DEC-20260923-80e280, RC-1..RC-13);
  - seedresolve (id, path, sha256 dc714a44...81, DEC-20260924-15a77a, SC-1..SC-11, CORR-20260924-36ce25);
  - solverevent (id, path, sha256 011d4b2c...7f, "incorporated by reference, never approved").
  - It also records K 5, max attempts 6, spacing_s 2.0, the SF-2 (c) cap rule, the SF-1 signature, reg1_d_branch
    "d-parsed", driver_pythonhashseed "0", the PS-1 branch, values, API and evidence, the RC-2 exit semantics, the entry
    point, resolve wrapper, run wrapper and checker paths, derived_from (the frozen plan and its sha256) and the declared
    key paths. DV-5 checks this content.
- **Retirement (`retired_ids`, both plans).**
  - Used v2 ids, kept as records and never re-run: RUN-GFPN-ac4487 and RUN-GFPN-3377f1.
  - 29 unused v2 ids and 11 unused v2-a1 ids (the paristack PS-3 enumeration).
  - The 42 r1 ids (`r1_ids_retired_unused`, in r1 minting order; equal to the ids of both r1 plans).
  - `n_retired` 82.
- **Ceiling note.** 2 existing + 31 + 11 = 44 of 48, with 4 unreserved. The 82 retired ids never produce a package.
- **`watchdogs`.** Identical to trial-plan-v2.json lines 95-177 in both plans (writer and DV-5). As observed in stage R1,
  the object's closing brace is on line 178.
- **RC-4 (c) reading, as in stage R1 (RD-2 there).** Declared CHANGED keys are deleted from BOTH sides before comparing.
  The canonical sha256 of both sides is 0588623b...3252 (v2) and 138545e9...2537 (a1). These equal stage R1's values,
  as expected, because the frozen sources are the same.
- **Stale prose kept unchanged, because the RC-4 (c) equality requires it (noted for the Coordinator, as in stage R1).**
  - The a1-r2 plan's `/task_id_note` still reads "written by stage 1b under TASK-20260923-4c64b5".
  - Its aggregate_a1 `content` still names "TASK-20260923-0fa03f post-run receipt". The r2 rule is the 689d2f phase-B
    receipt (RC-8), stated in `repair.v2_gate_repointed_to`.
- **Plan history.** The plans were written once, at 01:49:08Z, and never regenerated. `r2_make_plans.py --write` refuses
  to overwrite an existing plan.

## 8. REG-1 (PS-4 as amended by SE-4 with SF-4 d-parsed; RC-6 with CORR-20260923-111265; RC-7)

- **Comparator.** `r2_reg1.py` (also `r2_check_run.py reg1 ...`).
  - It first verifies every reference file it reads against the TASK-20260923-0fa03f post-run receipt. That is 219 files
    for RUN-GFPN-ac4487 in DV-8: the .ms, .ms.out, .ms.log and .ms.err of all 36 tags, 38 certificates and
    raw-result.json. A mismatch, or a file the receipt does not bind, is fatal.
  - (a) `solver/*.ms`: equal file sets, byte-identical.
  - (b) raw-result.json: exactly the r1 list (RD-5 of stage R1 carried).
  - (c) `certificates/*.json`: equal after the exclusions.
  - (d) **d-parsed**. For every `solver/*.ms.out` of the recorded attempts (renamed attempt files do not match the glob),
    the comparator checks equal parse kind, header degree, eliminating-polynomial degree, square-free flag, F_p-rational
    solution set as a set (`v2_solver.rational_solutions`, with p and nvars taken from the `.ms` header), and D (the
    quotient dimension printed in the recorded attempt's `.ms.log`). No tolerance.
  - SE-4: the candidate's `solver-events.json` must exist, parse, and record no consistency violation. It is quoted in
    full, and the `*.ssf-attempt<k>` files are listed with sha256. They are outside the compared sets, not exclusions.
- **Output.** Deterministic text ending "REG-1 VERDICT: PASS|FAIL", to be quoted verbatim (RC-7). The wrapper records it
  in `gate.regression_REG-1` from G2 on, together with `d_branch`.
- **Exclusion list (SE-4 (e): nothing added).** It is the r1 list X1..X17, byte-identical
  (`implementation-v2-r2/reg1-exclusion-list.json`, sha256 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c;
  equal to implementation-v2-r1.md lines 329-372, checked by DV-8).
  - X16 and X17 (callgrind instruction counts, classified as cpu measurements) remain open review items (RJ-2).
  - Verbatim:

```json
{
 "schema": "crypto.autoresearch.gfpn05.r1.reg1_exclusion_list.v1",
 "id": "REG-1 exclusion list (AMD-EXP-GFPN-05ff43-20260923-paristack PS-4 (e); DEC-20260923-80e280 RC-6, RC-7)",
 "declared_in": "stage R1 (TASK-20260923-a681f9), before any repaired run, by reading RUN-GFPN-ac4487's archived bytes and the v2 code; reproduced verbatim in implementation-v2-r1.md",
 "reference_run": "RUN-GFPN-ac4487",
 "permitted_categories": ["timestamps", "wall and cpu seconds", "rusage", "pids", "absolute paths", "host readings", "run-id, task-id and protocol-version labels"],
 "never_excludable": ["k", "x_R", "relation", "beta", "lam", "u_values", "relation_mod_T", "D", "solutions", "verified", "lifted_points"],
 "entries": [
  {"id": "X1", "item": "c", "scope": "certificate", "path": ["run_id"], "category": "run-id, task-id and protocol-version labels",
   "reason": "v2_lift.make_certificate writes the id of the package that produced the certificate; a repaired package carries a new id by construction (PS-3). The only field of the 38 archived certificates that names the package."},
  {"id": "X2", "item": "b", "scope": "raw-result", "path": ["metrics", "wall_seconds"], "category": "wall and cpu seconds",
   "reason": "wall-clock time of the fixture package (v2_driver.fixture_core)."},
  {"id": "X3", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "wall_seconds"], "category": "wall and cpu seconds",
   "reason": "wall-clock time of the msolve child (v2_solver.run_child)."},
  {"id": "X4", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "rusage"], "category": "rusage",
   "reason": "wait4 rusage of the msolve child (maxrss, utime, stime)."},
  {"id": "X5", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "peak_rss_bytes"], "category": "host readings",
   "reason": "sampled /proc/<pid>/status VmHWM of the child; a polling reading of the host, not a computed value."},
  {"id": "X6", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "peak_vm_bytes"], "category": "host readings",
   "reason": "sampled /proc/<pid>/status VmPeak of the child; a polling reading of the host."},
  {"id": "X7", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "driver_rss_bytes_before_launch"], "category": "host readings",
   "reason": "the driver's own VmRSS read before each launch (v2_solver.self_rss_bytes); it depends on the driver process's allocation history."},
  {"id": "X8", "item": "b", "scope": "target-entry", "path": ["arms", "*", "solver", "argv"], "category": "absolute paths",
   "reason": "the msolve argv carries the absolute input and output paths under runs/<run id>/solver/."},
  {"id": "X9", "item": "b", "scope": "target-entry", "path": ["arms", "*", "timings", "overall_cpu"], "category": "wall and cpu seconds",
   "reason": "msolve's own reported cpu seconds (parsed from its log)."},
  {"id": "X10", "item": "b", "scope": "target-entry", "path": ["arms", "*", "timings", "overall_elapsed"], "category": "wall and cpu seconds",
   "reason": "msolve's own reported elapsed seconds."},
  {"id": "X11", "item": "b", "scope": "target-entry", "path": ["arms", "*", "timings", "linear_algebra_sec"], "category": "wall and cpu seconds",
   "reason": "msolve's own reported linear-algebra seconds."},
  {"id": "X12", "item": "b", "scope": "target-entry", "path": ["arms", "*", "last_f4_round", "sec_real"], "category": "wall and cpu seconds",
   "reason": "real seconds of msolve's last F4 round (log column time(rd) real)."},
  {"id": "X13", "item": "b", "scope": "target-entry", "path": ["arms", "*", "last_f4_round", "sec_cpu"], "category": "wall and cpu seconds",
   "reason": "cpu seconds of msolve's last F4 round (log column time(rd) cpu)."},
  {"id": "X14", "item": "b", "scope": "target-entry", "path": ["arms", "*", "instructions_callgrind", "child", "wall_seconds"], "category": "wall and cpu seconds",
   "reason": "wall-clock time of the valgrind child."},
  {"id": "X15", "item": "b", "scope": "target-entry", "path": ["arms", "*", "instructions_callgrind", "child", "peak_vm_bytes"], "category": "host readings",
   "reason": "sampled VmPeak of the valgrind child."},
  {"id": "X16", "item": "b", "scope": "target-entry", "path": ["arms", "*", "instructions_callgrind", "instructions_user"], "category": "wall and cpu seconds",
   "reason": "callgrind Ir of the whole msolve process: the DC-4 C-1 'measured work proxy (instructions)', a cpu-cost measurement of the execution that also counts dynamic-loader and libc start-up work, which depends on the process environment and argv (the r1 wrapper's environment differs from the frozen wrapper's: RC-6). READING FOR RJ-2 REVIEW: classified as a cpu measurement, not as computed content."},
  {"id": "X17", "item": "b", "scope": "target-entry", "path": ["arms", "*", "instructions_callgrind", "f4_core_inclusive_Ir"], "category": "wall and cpu seconds",
   "reason": "callgrind inclusive Ir of msolve's core_f4: the same cpu-cost measurement restricted to the F4 core. READING FOR RJ-2 REVIEW, as X16."}
 ]
}
```

## 9. The r2 wrapper (PS-5 re-pointed) and the r2 checker

- **Refusals.** `r2_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]` evaluates every check before creating any
  directory. On refusal it prints every failing reason and exits 2.
  - R-1: the FIVE SC-1 hashes.
  - R-2: the id must be reserved in an r2 plan, and it must be none of the following: a v1 id; a v2 or v2-a1 id; an r1
    id (both r1 plans); an id on the 82-id retired list.
  - R-3: the run directory must not exist.
  - R-4 and R-5: the v2 and v2-a1 trees match their phase-A receipts file by file, are tracked and clean, and have no
    unbound file on disk.
  - R-6: `implementation-v2-r2/`, `implementation-v2-r2.md` and both r2 plans are checked against the
    TASK-20260924-689d2f phase-A receipt (`snapshot-receipt.json`).
  - R-7: the gate rule, with REG-1 (d-parsed) before G2 and every later package.
  - R-8: every package this one `requires` has a manifest.
  - R-9: the plan's watchdogs equal trial-plan-v2.json's.
  - R-10: no other solver-like process is running.
  - R-11: the 48 ceiling over the run directories of the SIX plans (frozen v2 and v2-a1, both r1, both r2).
  - R-12: the contingency rule, within one r2 plan.
  - R-13: the plan's label, the seedresolve and paristack ids and sha256, and the run card; none of the four forbidden
    task ids.
- **Launch.** The command is `[python3, -B, r2_entry_v2.py | r2_entry_a1.py] + driver_args`, read from the plan.
  - There is no outer guard, and `command.txt` says so.
  - The child environment adds GFPN_RUN_DIR, GFPN_V2_PACKAGE, GFPN_V2_REPLACES, PYTHONHASHSEED="0", PYTHONUNBUFFERED=1
    and PYTHONDONTWRITEBYTECODE=1.
- **Manifest (PS-5 fields).** Every v2 / v2-a1 field, plus:
  - `protocol_version`; the `amendment` and `addendum` blocks (the latter on addendum packages); the `repair` block
    (paristack, seedresolve, solverevent); `task_id` (the plan's run card); `derived_from` (the frozen id).
  - `code.phase_a_commits`, LITERALLY:
    - TASK-20260923-0fa03f fb4597b2014b44a0c9528d48d3ab9997b46f038c;
    - TASK-20260924-689d2f read from its phase-A receipt at run time (receipt `commit_sha`, else `git log -1` of the
      receipt);
    - on addendum packages, TASK-20260923-4ff597 36c3b0d2e05878a8df1209b5048f8ce14515c27f.
  - Clean flags for the v2, v2-a1 and r2 trees.
  - `resources.pari_stack` (the whole of pari-stack.json, with the read-backs); child getrlimit read-backs; threads
    executed; host RAM and swap; watchdogs with `equal_to_trial_plan_v2`.
  - The `solver_events` block; `environment.PYTHONHASHSEED_set_for_driver` and `PYTHONHASHSEED_driver_readback`.
  - `gate.regression_REG-1` (from G2 on); dependency versions (cypari2 through importlib.metadata); the inference block.
- **Failure class.** A package with no raw-result.json is recorded infrastructure_error, unless the entry refused (the
  refusal reasons are recorded) or solver-events.json records a consistency violation. In the latter case it is
  implementation_error (SF-2 (b)).
- **Checker.** `r2_check_run.py RUN_DIR [--accounting-json OUT]` runs the frozen checker, unchanged, in a separate
  process, then the r2 checks:
  - labels, the three repair blocks, the amendment and addendum blocks, run card, derived_from;
  - the phase-A commits and the three clean flags;
  - pari_stack: not refused; every RC-3 redirection and the SE-3 replacement read back as required; start handles exact;
    exit exact ("requested"); configured before the first v2 import; branch P-A; cypari2 version;
  - SE-6: the driver read back "0";
  - `solver_events`: present, K 5 and spacing 2.0, counts equal to solver-events.json, sha256 equal, no consistency
    violation, `watchdog_after_resolve` recorded;
  - REG-1 PASS with `d_branch` "d-parsed" and the plan's exclusion sha256 from G2 on;
  - no file of the package carrying any of the four forbidden task ids (a byte scan);
  - watchdogs equal; the inference block; status agreement.
- **SC-4 accounting.** For every recorded ok attempt with a retained `.ms.out`, the checker prints n_roots, n_den_zero,
  n_arity, n_points, n_distinct and the invariant (`--accounting-json` writes it OUTSIDE the run directory).
  - A violation is printed verbatim and routed to SJ-5. It never changes the exit status, a field or a class.
  - A tag whose output was not retained is listed as such.
  - Source of nvars and p: the retained `.ms` header. Otherwise the msolve output header, minus msolve's added
    linear-form variable when the log records "Adding a linear form with an extra variable". The source is labelled per
    row.
- **Not exercised end to end in this stage.** Because of the STOP (DV-7 not run), the checker ran on no toy package. Its
  SC-4 accounting function did run: it was used by DV-15 (b) on the eight DV-12 packages. The wrapper ran end to end in
  DV-12 (eight launches through the delivered wrapper and the delivered v2 entry) and in DV-6 (dry-runs).

## 10. Development notes DV-1..DV-15 (no run package; no number is a result)

Every note is a development note of TASK-20260923-de3a7d. Group orders are parameters. Commands ran from
`implementation-v2-r2/` with `PYTHONDONTWRITEBYTECODE=1 python3 -B`, one process at a time.

**Order in which the checks ran, and why (dispatcher's reply: "a legitimate choice"; ST-7 fixes no order).**

1. DV-3 (01:46:14Z), then the RC-2 semantics probe, then DV-2 / DV-4 (01:46:21Z). These fix the PS-1 branch, which the
   plans record.
2. The 42 mints and `--check`s (01:47Z). Then this note's RC-4 (b) section. Then the plans (01:49:08Z).
3. DV-5 and DV-10 (01:52Z).
4. DV-8 (01:53Z; attempt 1 harness fault, attempt 2 01:53:54Z).
5. DV-6 (01:56Z).
6. DV-1 (01:56:49Z).
7. DV-15 (a) (01:57:47Z).
8. DV-12 (01:59Z-02:09Z).
9. DV-15 (b) (02:09Z).
10. DV-11 (02:10:05Z): STOP.
11. DV-9 (02:11Z; attempt 1 harness fault, attempt 2 02:11:23Z).
12. The SC-5 bundle.

Reason: the Executor's reading of the frozen code predicted a DV-11 stop (section 1). DV-11 was therefore run BEFORE
DV-7, so that the one-shot SE-5 probe stays unspent if DV-11 stops. On the dispatcher's suggestion, DV-12 and DV-15 (a)
were run before DV-11, because neither depends on the DV-7 lineage. A DV-12 or DV-15 failure would itself have been a
stop, and whichever stop fired first would have ended the stage.

- **DV-3, negative control: PASS (the overflow was reproduced).** `r2_devchecks.py dv3 --out $S/dv3`.
  - In a fresh process WITHOUT the configuration, the unchanged `v2_common.curve_order_pari` on `fixture_n3(16777291)`
    raised `PariError: ellcard: the PARI stack overflows (current size: 8003584; maximum size: 8003584)`.
  - The read-backs before the call were parisize 8000000 and parisizemax 8003584.
- **RC-2 semantics probe: "requested"** (section 4).
- **DV-2 and DV-4: PASS under P-A at all three points, in two fresh processes each.** `r2_devchecks.py dv2 --out $S/dv2`.
  - Each worker runs the r2 entry's code up to dispatch: configure, `import v2_common`, the two redirections,
    `import v2_driver`, the SE-3 install and read-back (true), the RC-3 read-back and the RC-2 start read-back. It then
    calls the unchanged `curve_order_pari` on the unchanged `fixture_n3` / `fixture_n4` objects.
  - (4111, n = 3): N = 69477519282 in both repetitions, equal to RUN-GFPN-ac4487. Hasse: N - q - 1 = 299650. [N]G = O
    (stream `2026092002:v2:fixture:4111:basepoint`). [N]P = O (RC-5 stream `2026092002:v2r2:dv2:4111:3`), and P != G.
    The call took 0.004 s and 0.003 s. VmHWM after: 65880064 and 66027520 B.
  - (16777291, n = 3): N = 4722429815066881402162 in both. Hasse: N - q - 1 = 44360348990. [N]G = O and [N]P = O. The
    call took 0.292 s and 0.310 s. VmHWM: 87953408 and 88170496 B. RC-5 gp cross-check: N = 4722429815066881402162,
    which agrees. The gp child's outcome was ok, and getrlimit read back soft = hard = 10737418240.
  - (4111, n = 4): N = 285620852275820 in both. Hasse: N - q - 1 = 2372778. [N]G = O (stream
    `2026092002:v2:fixture4:4111:basepoint`) and [N]P = O. The call took 0.009 s and 0.008 s. VmHWM: 67559424 and
    67723264 B. The RC-5 gp cross-check agrees, with getrlimit 10737418240.
  - Read-backs in every run:
    - start, through both fresh handles: 67108864 / 536870912;
    - before and after each call: the same;
    - exit, through the retained handle: the same;
    - the current stack size stayed 67108864.
  - VmHWM <= 805306368 at every point (maximum 88170496). The DV-4 reading with `v2_solver.self_rss_bytes` was below
    1073741824 at every point (maximum 88170496). `configured_before_first_v2_or_a1_import` was true.
- **DV-5, plan derivation with its own code path: PASS.** `$S/dv5/dv5.json`.
  - M has 42 entries, is a bijection, and its images are fresh: disjoint from the v1, v2, v2-a1, r1 and 82 retired ids,
    and equal to the minted list. The a1-r2 `id_map_v2` equals the v2-r2 `id_map`.
  - RC-4 (c) holds by DV-5's own implementation for both plans. The canonical sha256 values are in section 7.
  - The declared keys equal the RC-4 (b) record read back from this note. The watchdogs are identical to lines 95-177.
    The plans hold 31 and 11 packages, in order, as images.
  - No frozen or r1 id appears outside the maps, never-reused lists and `retired_ids`, except the one disclosed location
    `/gate/regression/reference_run` (RUN-GFPN-ac4487), as in stage R1.
  - `retired_ids` carries the 82. There is no forbidden task id. Labels, task ids, written_by_task, archived_by and the
    d-parsed `gate.regression` are as required. The repair block carries the SC-1 content.
  - For the a1 plan: the four r2 gate ids, the controls_a1 image, plan_branch "31-bit", the mapped
    `v2_ids_never_reused` and the mapped aggregate_a1 arguments.
  - The writer's `--check` regenerated both files byte-identically.
- **DV-6, refusals: PASS.** 42 wrapper dry-run cases and 8 entry cases. `$S/dv6/dv6.json`.
  - Baseline: a G1 dry-run with the two declared stubs printed "DRY RUN: every R-1..R-13 check passes". The stubs are
    the r2 tree reported tracked and clean, and a synthetic 689d2f phase-A receipt.
  - Every case below exited 2 with its expected reason and wrote nothing. The real runs directory, the scratch runs
    directory and `implementation-v2-r2/` were identical before and after each case.
  - R-1: altered copies of each of the five files.
  - R-2: RUN-GFPN-ac4487; RUN-GFPN-3377f1; RUN-GFPN-76420e and RUN-GFPN-e26e4b (retired v2); RUN-GFPN-0d91bf (v2-a1);
    RUN-GFPN-61bba9 (v1); RUN-GFPN-a61a10 and RUN-GFPN-51e56b (r1); RUN-GFPN-3868df (on the retired list); the
    unreserved RUN-GFPN-0f0f0f.
  - R-3. R-4 and R-5: an altered receipt; a simulated dirty tree. R-6: the REAL state (tree uncommitted, 689d2f receipt
    absent) and a synthetic receipt mismatch.
  - R-7: gate not run; G2 failed; REG-1 failed on a synthetic pair; controls_a1 image not passed. R-8. R-9. R-10
    (simulated scan).
  - R-11: 48 synthetic directories (the 42 frozen ids plus 6 r1 ids, which exercises the six-plan count); the plan's own
    package_count.
  - R-12: a gate package; across plans; a non-infrastructure class; twice; `--replaces` on a non-contingency id.
  - R-13: a wrong label; a wrong seedresolve sha256 in the repair block; each of the four forbidden task ids.
  - Entries, each in a fresh process through a development shim, exited 2 and wrote only the refusal record
    `pari-stack.json` (status `refused_before_any_command`):
    - PARI read-back, both entries: start read-back 8000000 / 8003584.
    - RC-3 redirection read-back, both entries.
    - **SE-3 read-back (a): `v2_driver.solve` rebound after install**, both entries: "SE-3 read-back: v2_driver.solve is
      not the r2 re-solve wrapper".
    - **SE-3 read-back (b): the wrapper's recorded original replaced by a non-frozen function**, both entries: "SE-3
      read-back: the wrapper's recorded original is not the frozen v2_driver.solve".
  - **Disclosure (not re-run).** Three cases use a synthetic G1 that is a byte copy of RUN-GFPN-ac4487 without a
    `solver-events.json`: "R-7 gate failed (G2 failed; REG-1 passes)", "R-7 controls_a1 image not passed" and "R-12
    contingency on a gate package".
    - In all three, REG-1 ALSO failed, on "(SE-4) candidate solver-events.json is missing". The label "REG-1 passes" is
      inaccurate under r2.
    - Each case still showed its own expected reason.
- **DV-7: NOT RUN (STOP at DV-11).** Consequently none of the following ran:
  - the toy lineage;
  - the SE-5 probe (worlds A "0" and B "12345"), which remains unspent;
  - the RC-8 synthetic phase-B receipt check of aggregate_a1;
  - the checker on toy packages;
  - REG-1 within the lineage.
  - No DV-7 output exists.
- **DV-8, REG-1 exclusion list and d-parsed comparator: PASS (attempt 2).** `$S/dv8/dv8.json`; verbatim self output in
  `$S/dv8/dv8_self_output.txt`.
  - The list is X1..X17, byte-identical to the r1 list and to implementation-v2-r1.md lines 329-372. Every entry is
    within the permitted categories, and none names a never-excludable field.
  - Self: RUN-GFPN-ac4487 against a byte copy of itself carrying a structurally valid no-event solver-events.json gives
    PASS, with 219 reference files verified against the receipt. (SE-4 makes solver-events.json mandatory for a
    candidate, so a bare self-comparison would fail by design.)
  - These cases FAIL, as expected: (a) one byte of `fx_reg0_S3.ms`; (b) `targets[2].arms.S3.D + 1`; (c)
    `u_values[0] + 1` in one certificate; (d) the constant coefficient of the first parametrisation polynomial of
    `fx_fresh1_S3.ms.out` + 1 (only `rational_solution_set` differs); solver-events.json missing; unparseable; recording
    a consistency violation.
  - These controls PASS, as expected: a trailing newline added to `fx_fresh1_S3.ms.out` (bytes differ, parsed fields
    equal); excluded fields only; a renamed `.ssf-attempt1` file (outside the sets, listed with sha256).
  - An altered receipt gives FAIL (integrity is fatal).
  - **Attempt 1 (preserved in `$S/dv_attempts/dv8_attempt1_harness_fault/`) FAILED on the trailing-newline control only.**
    Recorded harness reason: the control's construction `open(p, "w").write(open(p).read()...)` truncated the file
    before reading it, so the candidate became an empty-content file. The fix (read first, then write) touched the check
    code only. DV-8 was re-run once (ST-8 re-run rule).
- **DV-9, no edit (SC-6): PASS (attempt 2).** `$S/dv9/result/dv9.json`.
  - All 420 baseline files are byte-identical: nothing changed, added or removed.
  - They equal the 0fa03f phase-A, 4ff597 phase-A, 0fa03f phase-B and 53a47d preservation receipts. The five amendment
    hashes are the bound values.
  - No byte code is newer than the stage start. The only byte code is the pre-existing v1 `__pycache__` (section 2).
  - `git status` shows nothing outside the write scope and no tracked modification.
  - `runs/` holds the same 50 non-hidden entries, plus the pre-existing `.gitkeep`.
  - **Attempt 1 (preserved in `$S/dv_attempts/dv9_attempt1_harness_fault/`) FAILED only on `no_new_run_directory`.**
    Recorded harness reason: the baseline listing was taken with `ls` (which hides `.gitkeep`) and compared with
    `os.listdir` (51 entries). `.gitkeep` is pre-existing: committed in fcd91a1, mtime 2026-09-20. The fix compares with
    `ls` semantics and lists hidden entries separately. DV-9 was re-run once.
- **DV-10, ids: PASS.** `$S/dv10/dv10.json`.
  - 42 ids, all distinct, equal to the allocator outputs in order.
  - Each BARE id was checked with `--check` at minting time, before any stage file named it: rc 0, "occurrences across
    the union (26444 identifier-bearing paths scanned): 0", "OK: well-formed and free across the union."
  - None is a v1, v2, v2-a1, r1 or retired id. No run directory exists for any of the 42 or for any of the 82 retired
    ids.
  - The re-check at DV-10 time also reported 0 occurrences, although the ids now occur in stage files. As observed in
    stage R1, the allocator apparently does not scan untracked files.
  - Section 16 has every output.
- **DV-11, msolve call paths: STOP.** Section 12.
  - Static part: 65 hits for MSOLVE, msolve_argv, run_child, classify_solve, solve( and callgrind in implementation-v2/,
    implementation-v2-a1/ and the layer. `$S/dv11/dv11.json`.
  - The frozen solve() call sites are v2_driver.py 358, 565, 693 (gb_only), 711 (gb_only), 786, 787, 841 and 1174, and
    a1_driver.py 166. These equal the characterization's list. The layer's only call of the frozen function is
    `r2_resolve._call_original`.
  - Dynamic part, available without DV-7: the traced unforced DV-12 package U (fixture command). It had 37 classified
    msolve children (`-P`) against 37 wrapper attempts, which are equal, and 0 classified children outside the wrapper.
    It also had 36 callgrind (valgrind) children, all inside the wrapper after ok outcomes, 0 gb_only children, and 16
    python3 builder children.
- **DV-12, forced re-solve path: PASS, (a)-(g).**
  - `$S/dv12/dv12.json` covers the scratch toy copy: the toy G1 `fixture --p 1033` (stage R1's toy fixture data), run
    through the delivered r2 wrapper and v2 entry with a development shim. The declared target is `fx_reg1_S3`
    (timeout_s 1800).
  - U (unforced): completed_valid, gate_pass true; the target was ok with D 64.
  - (a) Attempt 1 was forced to clause (ii). It was renamed (.ms.out / .ms.log / .ms.err.ssf-attempt1), the gap was
    2.010 s, and attempt 2 was ok. The recorded target equals U's, and REG-1 (d-parsed) against U passes.
  - (b) Clause (iv), with the same results.
  - (c) Clause (v) via a shimmed `.ms.log` line carrying the random-form string, with the same results.
  - (d) All six attempts were forced to (ii), each gap 2.010 s. The recorded result was degenerate_parametrisation with
    D undefined and still_ssf. Renamed files attempt1..5 exist, and attempt 6 is at the normal names. No cap applied.
    The package was failed / implementation_error with gate_pass false (F-1 on the forced target), as frozen handling
    gives.
  - (e) Attempt 2's input sha256 was forced to 0...0. The violation was recorded verbatim ("attempt 2 input sha256 0000...
    != attempt 1's e6f463b4...9062 (SE-2 (4))"), and the package ended failed / implementation_error.
  - (f) All attempts forced; the clock was shimmed so that attempt 2's wall time was 1801.917 s against timeout_s 1800.
    `resolve_cap_reached` was recorded (summed 1801.916863 s against 1800, k = 2). The recorded result is attempt 2's
    (degenerate_parametrisation), and the manifest counts the cap.
  - (g) The 2 s wait was shimmed away. The recorded violation was "attempt 2 started 0.001888 s after attempt 1's
    recorded end, < 2.0 s (SF-2 (b); SC-11 (d))", and the package ended failed / implementation_error.
  - **Unforced, natural SSF events in the DV-12 toy packages** (observations only, at toy prime 1033):
    - U: `fx_planted1_raw_u` attempt 1, clause (iii) ("square-free part degree 382 != quotient dimension 384"), re-solved
      2.010 s later to ok, D 384. Attempt 2's output sha256 is a58b0f28...; the characterization's toy35 distinct outputs
      contain it for this tag.
    - (d): `fx_reg0_raw_x` attempt 1, clause (iii) (383 vs 384), re-solved to ok, D 384.
    - (f): `fx_planted0_S3_rescaled` attempt 1, clause (ii) (63 vs 64), re-solved to ok, D 64.
    - None was seen in (a), (b), (c), (e) or (g) before each package ended.
  - Forced attempts are real frozen solves whose returned dict the shim rewrote after the call. In forced attempts whose
    real outcome was ok, the frozen solve() had already run its callgrind child before the rewrite; that is disclosed and
    applies to development only.
- **DV-13: NOT RUN as defined (it applies to the DV-7 lineage).** Partial observation from the DV-12 packages
  (`$S/dv13_dv14_partial/`): the driver read back PYTHONHASHSEED "0" in all 8 packages.
- **DV-14: NOT RUN as defined (the DV-7 lineage).** Partial observation from the DV-12 packages: every re-solve attempt
  started 2.010 s after the previous recorded end. The exception is case (g), where the wait was deliberately shimmed
  away (0.002 s) and the violation was detected.
- **DV-15 (SC-3): PASS on everything that ran.** Section 13 has the tables.
  - (a) The 75 outputs of set O were re-extracted from the hash-verified archives and RUN-GFPN-ac4487/solver/:
    - `distinct-outputs.tar.gz` 05a08171...4994 equals the 683f34 receipt;
    - the stage-R1 DV-7 bundle 70b83d61...bd14 equals the 53a47d receipt;
    - `premise-check.json` 16924318...6e67 equals the 3ee9a8 receipt;
    - 216 ac4487 solver files equal the 0fa03f post-run receipt.
    - Every output, input and log was located by sha256 and classified by the frozen code path.
    - 73 are ok-classified, and every classification agrees with the premise check.
    - The invariant holds on all 73: n_den_zero = n_arity = 0, n_distinct = n_points = n_roots.
    - The two degenerate outputs (modes A and B) are listed and are not subject to the invariant.
  - (b) The 214 ok-classified recorded outputs of the DV-12 packages (U, a, b, c, d, f) show no violation.
    - Packages (e) and (g) aborted by design before raw-result.json existed, so no recorded ok classification exists
      there.
    - The SE-5 worlds and the rest of the lineage did not run.
  - No solver child was launched by DV-15.

## 11. getrlimit read-backs (every capped child of this stage)

- DV-2 RC-5 gp children (2): soft = hard = 10737418240.
- DV-1 Sage start-up probe child: soft = hard = 10737418240.
- DV-12, eight packages: every msolve, valgrind and builder child read back soft = hard = 10737418240 (manifest
  `child_rlimit_as_read_back_by_getrlimit`). msolve threads executed: [1].
- No child failed to set the cap. No child was started outside `v2_solver.run_child`.

## 12. THE STOP: DV-11 evidence (SE-3; SE-9 as incorporated; card ST-8)

- **The launch outside the wrapper.** `implementation-v2-a1/a1_health.py` (frozen; bound by the 4ff597 phase-A receipt),
  `run_system`:
  - line 144: `argv = V.msolve_argv(inp, out, threads=1)`;
  - line 147: `rec = V.run_child(argv, logp, errp, cap_bytes=cap, timeout_s=DEV_TIMEOUT_S, count_instructions=False)`;
  - lines 168-172: `V.parse_msolve_param`, `V.rational_solutions`, `V.substitute` (`run_system` is defined at line 140; `run` at line 223);
  - line 182: `outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail or 0)`.
- **How the plans reach it.** `a1_driver.py` line 38 imports `a1_health as H`, and line 129 runs
  `hr = H.run(p, os.path.join(ctx.rd, "health"), cap=ctx.cap)` inside `cmd_controls_a1`. Lines 130-131 record the result
  as controls_a1 check (d) `d_msolve_characteristic_check_synthetic`.
  - `controls-a1 --p 1073741831` is package order 1 of `trial-plan-v2-a1-r2.json`: RUN-GFPN-599b87, the addendum's
    blocking package (`gate.addendum_blocking_package`), whose pass gates the other addendum packages (`controls_a1_gate_required`).
  - The msolve children of `a1_health.run_system` are classified by the frozen classifier, and their classification
    feeds a gate check. They never pass through `v2_driver.solve`, so the SE-3 wrapper cannot apply SE-2 to them.
  - `a1_health.run` has its own pre-declared re-draw / re-invocation logic (A1-7 (b); AA-3 (b)). That is not SE-2, and
    this stage does not change or read it.
- **Why the layer cannot remove it.** Routing these children through the wrapper would mean replacing
  `a1_health.run_system` or `v2_solver.run_child`. ST-1 and SE-3 permit only `v2_driver.solve` (and
  `v2_common.curve_order_pari` under P-B). Treating the launches as out of SE-2's scope would contradict SE-3's DV-11
  requirement. Neither is the Executor's call.
- **Not covered by the prior records.** The characterization's per-kind count (`summary.json`, "controls_a1": "2 planted
  arms (a1_driver.py lines 142-166)") and the premise check's PR-3 (iii) list cover solve() call sites only. Neither names
  `a1_health`.
- **What was not run because of the stop.** DV-7 (the toy lineage, the SE-5 probe, the RC-8 check, the checker on toy
  packages, REG-1 in the lineage), and with it DV-13 and DV-14 as defined and the DV-11 dynamic count on
  `controls-a1`. No check was re-run to change an outcome.
- **Reading.** This is an impediment for a new Coordinator decision, not a mathematical or solver result. It says
  nothing about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT. At toy prime 1021, the controls-a1 health check was
  never executed in this stage.

## 13. DV-15 per-output table (SC-3)

Columns: n_roots, n_den_zero, n_arity, n_points, n_distinct, and whether the invariant holds. "ok" is the frozen
classifier's outcome, recomputed; it agrees with the premise check in every row.

(a) Set O, 75 outputs (p = 1033 for event/toy35, 4111 for ac4487):

| # | input key | output sha256 (16) | classifier | roots | den0 | arity | points | distinct | invariant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | event/fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 2 | event/fx_reg0_torsion_S3_norm | d2878f4f2b276162 | degenerate_parametrisation | 1 | 0 | 0 | 1 | 1 | holds |
| 3 | ac4487/fx_fresh1_S3 | 60a4cd6e46072593 | ok | 3 | 0 | 0 | 3 | 3 | holds |
| 4 | ac4487/fx_fresh1_S3_rescaled | efb50e2ef8c6553e | ok | 6 | 0 | 0 | 6 | 6 | holds |
| 5 | ac4487/fx_fresh1_raw_u | 913635c67f3d3d1a | ok | 24 | 0 | 0 | 24 | 24 | holds |
| 6 | ac4487/fx_fresh1_raw_x | 7dc2c544bc5d015f | ok | 6 | 0 | 0 | 6 | 6 | holds |
| 7 | ac4487/fx_fresh1_torsion_S3_norm | efb572acc1a06f1f | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 8 | ac4487/fx_fresh1_torsion_S3_rq | 7a89173a15d12c5b | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 9 | ac4487/fx_fresh2_S3 | eca772970934e5a5 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 10 | ac4487/fx_fresh2_S3_rescaled | ac26fa0bd1d18e17 | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 11 | ac4487/fx_fresh2_raw_u | 12c4b747e3b2a426 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 12 | ac4487/fx_fresh2_raw_x | 7a3c217d2f436c65 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 13 | ac4487/fx_fresh2_torsion_S3_norm | 2ebac156e566bc1d | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 14 | ac4487/fx_fresh2_torsion_S3_rq | b564bab4afdff3fc | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 15 | ac4487/fx_planted0_S3 | 5a5c3ade3fade8ac | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 16 | ac4487/fx_planted0_S3_rescaled | e0b8706cb48594fa | ok | 8 | 0 | 0 | 8 | 8 | holds |
| 17 | ac4487/fx_planted0_raw_u | fa43416ce9f92ff8 | ok | 48 | 0 | 0 | 48 | 48 | holds |
| 18 | ac4487/fx_planted0_raw_x | 4979535ed24c467a | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 19 | ac4487/fx_planted0_torsion_S3_norm | 4b64be0be57b1998 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 20 | ac4487/fx_planted0_torsion_S3_rq | 88f25f454f5270af | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 21 | ac4487/fx_planted1_S3 | d697a8abefa77325 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 22 | ac4487/fx_planted1_S3_rescaled | 811679d46e3b0ff1 | ok | 4 | 0 | 0 | 4 | 4 | holds |
| 23 | ac4487/fx_planted1_raw_u | e2560125e6aaabe2 | ok | 24 | 0 | 0 | 24 | 24 | holds |
| 24 | ac4487/fx_planted1_raw_x | a8d0557e35dd8e65 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 25 | ac4487/fx_planted1_torsion_S3_norm | aaadd08c36eb7f57 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 26 | ac4487/fx_planted1_torsion_S3_rq | 4a2ffb7100cc81cd | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 27 | ac4487/fx_reg0_S3 | 53293037cd7354f9 | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 28 | ac4487/fx_reg0_S3_rescaled | 6ea8b0e8d7fc75a2 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 29 | ac4487/fx_reg0_raw_u | 728ecf36505ecee0 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 30 | ac4487/fx_reg0_raw_x | a87355d97a2f4870 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 31 | ac4487/fx_reg0_torsion_S3_norm | 606fc541d777720d | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 32 | ac4487/fx_reg0_torsion_S3_rq | 43b940e706031a9c | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 33 | ac4487/fx_reg1_S3 | 1f2628d960a8e77c | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 34 | ac4487/fx_reg1_S3_rescaled | 3b232b2b6557c13f | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 35 | ac4487/fx_reg1_S3_rescaled | 7e283c2834f02442 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 36 | ac4487/fx_reg1_raw_u | e57c788f1f63c4ca | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 37 | ac4487/fx_reg1_raw_x | 5f44e62678ce8769 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 38 | ac4487/fx_reg1_torsion_S3_norm | efc90355062318d5 | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 39 | ac4487/fx_reg1_torsion_S3_rq | 840f544d9da36243 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 40 | event/fx_reg0_torsion_S3_norm | ec54fd1520eafb22 | degenerate_parametrisation | 2 | 0 | 0 | 2 | 2 | holds |
| 41 | toy35/fx_fresh1_S3 | 0b826a955bf88e8b | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 42 | toy35/fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | ok | 3 | 0 | 0 | 3 | 3 | holds |
| 43 | toy35/fx_fresh1_raw_u | a260a14727f5fb0a | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 44 | toy35/fx_fresh1_raw_x | 441286fd1641a103 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 45 | toy35/fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 46 | toy35/fx_fresh1_torsion_S3_rq | d4b7d575a576020e | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 47 | toy35/fx_fresh2_S3 | c64559085efbb499 | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 48 | toy35/fx_fresh2_S3_rescaled | 92fae59592050289 | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 49 | toy35/fx_fresh2_raw_u | 658094488ecd881e | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 50 | toy35/fx_fresh2_raw_x | 8ff2d23f552c3b08 | ok | 6 | 0 | 0 | 6 | 6 | holds |
| 51 | toy35/fx_fresh2_torsion_S3_norm | 474178c25c8394eb | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 52 | toy35/fx_fresh2_torsion_S3_rq | 332ee8496348c73f | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 53 | toy35/fx_planted0_S3 | 12337eae105636c6 | ok | 3 | 0 | 0 | 3 | 3 | holds |
| 54 | toy35/fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | ok | 4 | 0 | 0 | 4 | 4 | holds |
| 55 | toy35/fx_planted0_raw_u | 7b2d971242c22d94 | ok | 24 | 0 | 0 | 24 | 24 | holds |
| 56 | toy35/fx_planted0_raw_x | 3c9855ee4ad2ec8e | ok | 6 | 0 | 0 | 6 | 6 | holds |
| 57 | toy35/fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 58 | toy35/fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 59 | toy35/fx_planted1_S3 | 9d782351728a9c70 | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 60 | toy35/fx_planted1_S3_rescaled | bc2f6065bfc15581 | ok | 4 | 0 | 0 | 4 | 4 | holds |
| 61 | toy35/fx_planted1_raw_u | a58b0f283ef5a1ce | ok | 24 | 0 | 0 | 24 | 24 | holds |
| 62 | toy35/fx_planted1_raw_x | b9bc99f4a96c79d4 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 63 | toy35/fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 64 | toy35/fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 65 | toy35/fx_reg0_S3 | b7c2aec257a4fffd | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 66 | toy35/fx_reg0_S3_rescaled | ade0308b662b0dda | ok | 3 | 0 | 0 | 3 | 3 | holds |
| 67 | toy35/fx_reg0_raw_u | 78ce47f76a789d2c | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 68 | toy35/fx_reg0_raw_x | 84c80057e5146ce4 | ok | 6 | 0 | 0 | 6 | 6 | holds |
| 69 | toy35/fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | ok | 2 | 0 | 0 | 2 | 2 | holds |
| 70 | toy35/fx_reg1_S3 | c6ffbdf114623841 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 71 | toy35/fx_reg1_S3_rescaled | 6e005f1b4b378e02 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 72 | toy35/fx_reg1_raw_u | 4a0aacd842bdc525 | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 73 | toy35/fx_reg1_raw_x | a6187802ea6fed6d | ok | 0 | 0 | 0 | 0 | 0 | holds |
| 74 | toy35/fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | ok | 1 | 0 | 0 | 1 | 1 | holds |
| 75 | toy35/fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | ok | 0 | 0 | 0 | 0 | 0 | holds |

Summary (a): 75 outputs; 73 ok-classified, invariant holds on 73; 2 not ok (the event input's mode A d2878f4f... clause (ii) and mode B ec54fd15... clause (iv)); 0 violations.

(b) DV-12 toy packages, recorded ok attempts (p = 1033), 214 rows:

| package | tag | output sha256 (16) | roots | den0 | arity | points | distinct | invariant |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DV-12 U | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 U | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 U | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 U | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 U | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_reg1_S3 | c6ffbdf114623841 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 U | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 U | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 U | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 U | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 U | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 U | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 U | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 U | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 U | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 U | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 U | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 U | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 U | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 a | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 a | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 a | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 a | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_reg1_S3 | c6ffbdf114623841 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 a | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 a | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 a | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 a | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 a | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 a | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 a | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 a | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 a | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 a | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 a | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 a | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 a | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 b | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 b | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 b | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 b | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_reg1_S3 | c6ffbdf114623841 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 b | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 b | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 b | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 b | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 b | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 b | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 b | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 b | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 b | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 b | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 b | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 b | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 b | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 c | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 c | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 c | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 c | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_reg1_S3 | c6ffbdf114623841 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 c | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 c | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 c | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 c | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 c | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 c | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 c | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 c | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 c | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 c | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 c | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 c | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 c | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 d | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 d | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 d | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 d | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 d | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 d | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 d | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 d | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 d | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 d | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 d | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 d | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 d | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 d | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 d | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 d | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 d | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_reg0_raw_x | 84c80057e5146ce4 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 f | fx_reg0_raw_u | 78ce47f76a789d2c | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_reg0_S3 | b7c2aec257a4fffd | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_reg0_S3_rescaled | ade0308b662b0dda | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 f | fx_reg0_torsion_S3_norm | 201812d43b7c7a9d | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 f | fx_reg0_torsion_S3_rq | 4baa667bbef5d9f6 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 f | fx_reg1_raw_x | a6187802ea6fed6d | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_reg1_raw_u | 4a0aacd842bdc525 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_reg1_S3_rescaled | 6e005f1b4b378e02 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_reg1_torsion_S3_norm | 64f7fe95d895cd7d | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_reg1_torsion_S3_rq | 4bdba858f22099c3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_fresh1_raw_x | 441286fd1641a103 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_fresh1_raw_u | a260a14727f5fb0a | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_fresh1_S3 | 0b826a955bf88e8b | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_fresh1_S3_rescaled | cd0ea21d0d43a66c | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 f | fx_fresh1_torsion_S3_norm | b9d29cb8c0e323c8 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_fresh1_torsion_S3_rq | d4b7d575a576020e | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 f | fx_fresh2_raw_x | 8ff2d23f552c3b08 | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 f | fx_fresh2_raw_u | 658094488ecd881e | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_fresh2_S3 | c64559085efbb499 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 f | fx_fresh2_S3_rescaled | 92fae59592050289 | 2 | 0 | 0 | 2 | 2 | holds |
| DV-12 f | fx_fresh2_torsion_S3_norm | 474178c25c8394eb | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_fresh2_torsion_S3_rq | 332ee8496348c73f | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_planted0_raw_x | 3c9855ee4ad2ec8e | 6 | 0 | 0 | 6 | 6 | holds |
| DV-12 f | fx_planted0_raw_u | 7b2d971242c22d94 | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 f | fx_planted0_S3 | 12337eae105636c6 | 3 | 0 | 0 | 3 | 3 | holds |
| DV-12 f | fx_planted0_S3_rescaled | 5ade3f32ffa1eadf | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 f | fx_planted0_torsion_S3_norm | 4a2734dc2c2f335c | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_planted0_torsion_S3_rq | 49eb0b2170e78082 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_planted1_raw_x | b9bc99f4a96c79d4 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_planted1_raw_u | a58b0f283ef5a1ce | 24 | 0 | 0 | 24 | 24 | holds |
| DV-12 f | fx_planted1_S3 | 9d782351728a9c70 | 1 | 0 | 0 | 1 | 1 | holds |
| DV-12 f | fx_planted1_S3_rescaled | bc2f6065bfc15581 | 4 | 0 | 0 | 4 | 4 | holds |
| DV-12 f | fx_planted1_torsion_S3_norm | b6a14a7a31ce7fd3 | 0 | 0 | 0 | 0 | 0 | holds |
| DV-12 f | fx_planted1_torsion_S3_rq | 1f2b7f6c1bd94f01 | 1 | 0 | 0 | 1 | 1 | holds |

Summary (b): U: 36, a: 36, b: 36, c: 36, d: 35, f: 35; 0 violations. DV-12 (e) and (g) contribute no rows (aborted before raw-result.json by design).

## 14. SC-5 evidence bundle

- Path: `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r2-dv/stage-r2-dv-evidence.tar.gz`, sha256 307c98f98505094b2073bdc7090b68d21eafa9f6bd3060dcb2cec2d75127b508, 1688182 bytes.
- Written by the scratch script `make_bundle.py` (sha256 517762224fafe6f71fe99510597ff7d5f26e7fc79096381adf2440141b86d367; a member of the bundle).
- 2304 members: `stage-r2-dv/MEMBERS.sha256` (sha256, bytes and path of each of the 2302 files), `stage-r2-dv/EXCLUDED.json`, and the files.
  No member exceeds 50 MiB. MEMBERS.sha256 has sha256 a785b5e45312c5eec9b84683bac969b6c99262b6ed30d3487b8285ffe7c68675.
- Files by top-level directory: dv1 4, dv10 1, dv11 1, dv12 2209, dv12.log 1, dv12.start 1, dv13_dv14_partial 1, dv15a 1, dv15b 1, dv2 31, dv3 4, dv5 1, dv6 27, dv8 2, dv9 6, dv_attempts 3, ids 3, make_bundle.py 1, semantics 4.
- It holds the raw outputs of DV-11, DV-12 (a)-(g) with U, every solver-events.json, the shim logs and traces, the DV-13 / DV-14 partial observations and DV-15 (a) and (b).
  It also holds DV-1, DV-2, DV-3, the semantics probe, DV-5, DV-6, DV-8 (both attempts), DV-9 (baseline, both attempts), DV-10 and the allocator logs.
- It holds no DV-7 output, because DV-7 did not run: there are no SE-5 world outputs.
- Excluded and left in the scratchpad (EXCLUDED.json): byte copies of RUN-GFPN-ac4487 used as perturbation or synthetic-package scratch, and DV-15's re-extraction of the hash-bound archives:
  - `$S/dv15a/extract`: 1060 files, 10135565 bytes, tree sha256 8f6f3326706cc25ea4fd13f7f6cd4d01cac0b4b67947cd6e08c14183230aa261;
  - `$S/dv6/runs`: 2041 files, 9199267 bytes, tree sha256 941a8de1e9e731b1e1c4299edf35afb66a49c05a9104bc860faf73163ed721de;
  - `$S/dv8/perturb`: 3697 files, 17014604 bytes, tree sha256 638677d6dd5772ad19a1d7bfc9032f601c7ad49bf4d4fccd6514921d4c9d2114;
  - `$S/dv_attempts/dv8_attempt1_harness_fault/perturb`: 3697 files, 17013390 bytes, tree sha256 bce72190dd651a20bd961048eefa07717539698bb8a99d6644133466aa248205;
- The bundle was written on the STOP, as ST-9 requires.

## 15. Deviations and implementation readings (disclosed)

- **SD-1: order of the checks.** DV-11 ran before DV-7, and DV-12 and DV-15 (a) ran before DV-11 (section 10; the dispatcher's reply accepted the order). The STOP at DV-11 left DV-7, DV-13 and DV-14 (as defined) unrun.
- **SD-2: code changed after some checks ran, all before the check it affects or with no bearing on earlier checks.**
  - (i) At 01:54Z, after DV-2 (01:46Z), `r2_resolve.install` stopped writing the initial solver-events.json. The write moved to `r2_resolve.begin()`, which the entries call after all read-backs pass, so that a refused entry leaves only `pari-stack.json`. DV-2's workers ran with the earlier `install`, which wrote an initial file into each worker's scratch run directory. The PARI readings DV-2 checks are unaffected, and DV-2 was not re-run.
  - (ii) `r2_devchecks_more.py` changed three times: the DV-8 harness fix (01:53Z), the DV-9 harness fix (02:11Z), and a new `dv15b` entry (02:09Z; DV-15 (a) was not re-run). DV-1, DV-5, DV-10, DV-11 and DV-15 (a) code is unchanged by these edits.
  - DV-6, DV-12, DV-11, DV-15 (b) and DV-9 ran on the final `r2_resolve.py`, entries and wrapper.
- **SD-3: two development checks re-run once after a failure with a recorded harness reason**, with the failed attempt preserved: DV-8 (the trailing-newline control's file was truncated before it was read) and DV-9 (`.gitkeep` compared against an `ls` listing). Section 10.
- **SD-4: DV-6 disclosure.** Three R-7 / R-12 cases also failed REG-1 through the SE-4 solver-events requirement. The case label "REG-1 passes" is inaccurate under r2 (section 10).
- **SD-5: DV-8 self-comparison.** The candidate is a byte copy of RUN-GFPN-ac4487 plus a no-event solver-events.json, because SE-4 makes the file mandatory for a candidate.
- **SD-6: solver-events.json counters.** The counters are rewritten after every wrapped call, including calls without an event. This is an addition beyond the SE-2 (5) events (section 6).
- **SD-7: SC-4 nvars fallback.** When the `.ms` is not retained, nvars comes from the msolve output header minus msolve's added variable, as its log records it. The source is labelled per row. In this stage every accounted output had its `.ms`.
- **SD-8: DV-11 report prose.** The hard-coded site description in `dv11.json` (in the bundle) says `run_system (lines 139-230)` and `a1_health.run (lines 232-)`. The definitions are at lines 140 and 223. The launch and classify lines (144, 147, 182) and the quoted source lines are correct. Section 12 gives the correct ranges.
- **SD-9: stage-R1 readings carried unchanged.** RC-4 (c) deletes declared changed keys from both sides (R1 RD-2). `/gate/regression/reference_run` is the one disclosed old-id location (R1 RD-3). REG-1 (b) compares whole target entries minus exclusions (R1 RD-5). R-5 applies to v2 packages too (R1 RD-6). An entry's refusal writes `pari-stack.json` only (R1 RD-4).
- **SD-10: observations for the Coordinator.**
  - The Sage comparator child starts at Sage's library-default PARI stack: parisize 8000000, parisizemax 1073741824 (DV-1 probe; Sage 10.9). This is FLAGGED (PS-6 DV-1) and not fixed.
  - The a1-r2 plan keeps the stale prose noted in section 7.
  - The allocator's re-check does not see untracked files.
  - Natural SSF events occurred in 3 of the 8 DV-12 toy packages at p = 1033 (section 10). They are observations only.
- **SD-11: the DV-12 toy data** reuse stage R1's DV-7 toy fixture construction and stream label (`r1-dv7:toy-fixture-n3:1033:regression`), so the toy inputs equal the stage-R1 toy inputs. The label string is data, not an import.

## 16. Allocator and --check outputs, verbatim (DV-10)

Allocator outputs (42 mints; `$S/ids/mint.log`):

```
### mint 1 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-a09162
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a09162
rc=0
### mint 2 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-0dca26
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-0dca26
rc=0
### mint 3 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-b69444
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-b69444
rc=0
### mint 4 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-22ee49
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-22ee49
rc=0
### mint 5 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-bf833b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-bf833b
rc=0
### mint 6 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-4bafcf
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-4bafcf
rc=0
### mint 7 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-93607c
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-93607c
rc=0
### mint 8 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-3a01f3
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-3a01f3
rc=0
### mint 9 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-4ea41a
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-4ea41a
rc=0
### mint 10 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-b9059b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-b9059b
rc=0
### mint 11 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-bebfc0
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-bebfc0
rc=0
### mint 12 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-48c73f
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-48c73f
rc=0
### mint 13 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-724745
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-724745
rc=0
### mint 14 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-477ae1
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-477ae1
rc=0
### mint 15 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-479e05
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-479e05
rc=0
### mint 16 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-c3fb79
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-c3fb79
rc=0
### mint 17 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-ecefab
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-ecefab
rc=0
### mint 18 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-4189b4
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-4189b4
rc=0
### mint 19 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-ff8c15
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-ff8c15
rc=0
### mint 20 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-6c464c
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-6c464c
rc=0
### mint 21 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-0bb551
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-0bb551
rc=0
### mint 22 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-f78382
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-f78382
rc=0
### mint 23 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-f4302b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-f4302b
rc=0
### mint 24 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-beac9f
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-beac9f
rc=0
### mint 25 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-d9f68f
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-d9f68f
rc=0
### mint 26 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-c8be8b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-c8be8b
rc=0
### mint 27 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-2f3442
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-2f3442
rc=0
### mint 28 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-9e266d
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-9e266d
rc=0
### mint 29 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-c3062b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-c3062b
rc=0
### mint 30 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-cfe871
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-cfe871
rc=0
### mint 31 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-c8c1f8
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-c8c1f8
rc=0
### mint 32 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-599b87
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-599b87
rc=0
### mint 33 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-af4935
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-af4935
rc=0
### mint 34 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-ad6372
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-ad6372
rc=0
### mint 35 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-b0bfca
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-b0bfca
rc=0
### mint 36 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-a11a01
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a11a01
rc=0
### mint 37 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-585023
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-585023
rc=0
### mint 38 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-411471
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-411471
rc=0
### mint 39 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-09fbad
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-09fbad
rc=0
### mint 40 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-20faaa
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-20faaa
rc=0
### mint 41 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-dc7e11
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-dc7e11
rc=0
### mint 42 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-0fa6cd
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-0fa6cd
rc=0
```

`--check` outputs, one per BARE id, at minting time and before any stage file named the id (`$S/ids/check.log`):

```
### python3 -B tools/allocate_id.py --check RUN-GFPN-a09162
identifier: RUN-GFPN-a09162
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-0dca26
identifier: RUN-GFPN-0dca26
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-b69444
identifier: RUN-GFPN-b69444
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-22ee49
identifier: RUN-GFPN-22ee49
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-bf833b
identifier: RUN-GFPN-bf833b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-4bafcf
identifier: RUN-GFPN-4bafcf
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-93607c
identifier: RUN-GFPN-93607c
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-3a01f3
identifier: RUN-GFPN-3a01f3
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-4ea41a
identifier: RUN-GFPN-4ea41a
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-b9059b
identifier: RUN-GFPN-b9059b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-bebfc0
identifier: RUN-GFPN-bebfc0
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-48c73f
identifier: RUN-GFPN-48c73f
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-724745
identifier: RUN-GFPN-724745
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-477ae1
identifier: RUN-GFPN-477ae1
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-479e05
identifier: RUN-GFPN-479e05
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-c3fb79
identifier: RUN-GFPN-c3fb79
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-ecefab
identifier: RUN-GFPN-ecefab
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-4189b4
identifier: RUN-GFPN-4189b4
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-ff8c15
identifier: RUN-GFPN-ff8c15
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-6c464c
identifier: RUN-GFPN-6c464c
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-0bb551
identifier: RUN-GFPN-0bb551
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-f78382
identifier: RUN-GFPN-f78382
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-f4302b
identifier: RUN-GFPN-f4302b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-beac9f
identifier: RUN-GFPN-beac9f
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-d9f68f
identifier: RUN-GFPN-d9f68f
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-c8be8b
identifier: RUN-GFPN-c8be8b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-2f3442
identifier: RUN-GFPN-2f3442
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-9e266d
identifier: RUN-GFPN-9e266d
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-c3062b
identifier: RUN-GFPN-c3062b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-cfe871
identifier: RUN-GFPN-cfe871
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-c8c1f8
identifier: RUN-GFPN-c8c1f8
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-599b87
identifier: RUN-GFPN-599b87
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-af4935
identifier: RUN-GFPN-af4935
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-ad6372
identifier: RUN-GFPN-ad6372
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-b0bfca
identifier: RUN-GFPN-b0bfca
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-a11a01
identifier: RUN-GFPN-a11a01
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-585023
identifier: RUN-GFPN-585023
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-411471
identifier: RUN-GFPN-411471
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-09fbad
identifier: RUN-GFPN-09fbad
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-20faaa
identifier: RUN-GFPN-20faaa
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-dc7e11
identifier: RUN-GFPN-dc7e11
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-0fa6cd
identifier: RUN-GFPN-0fa6cd
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26444 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
```

## 17. Inference

- requested_policy: `executor-implementation`
- resolved_model_id: null (the dispatching session supplied none; none is invented)
- fallback_used: false
- bedrock_used: false
- The development notes record TASK-20260923-de3a7d.
- No r2 artifact carries TASK-20260923-cd932c, TASK-20260923-6c7f55, TASK-20260923-3aa31e or TASK-20260923-292052 as its own task id.
  - Those strings appear in this note only as frozen values (section 5) and as the names of the forbidden ids.
  - In the layer they appear only in the guard constant `FORBIDDEN_TASK_IDS` (`r2_common.py`, built from split strings) and in docstrings that describe the rule.
