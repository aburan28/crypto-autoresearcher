# EXP-GFPN-05ff43 — implementation note, protocols 2-r1 and 2-a1-r1 (stage R1)

> **STAGE R1 OUTCOME: STOP (card R1-7; DEC-20260923-80e280 RC-6), recorded at 2026-09-23T21:55Z.**
> The RC-6 determinism probe in DV-7 found fields that REG-1 compares, including D and the arm outcome,
> differing between two toy runs of the same toy package. The runs were in separate processes, with
> PYTHONHASHSEED 0 and 12345. The solver inputs were byte-identical in both runs. The difference is
> inside msolve 0.6.5 (section 12). Under RC-6, stage R1 stops and returns. **Neither r1 plan is
> treated as final.** No run package exists. No frozen byte changed (DV-9). This is an impediment for
> a new Coordinator decision. It is never evidence about D, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
> (This banner was added at the end of stage R1. The section below it was written first, as it states.)

(Section written first, at 2026-09-23T21:33:43Z. At that time neither `trial-plan-v2-r1.json` nor
`trial-plan-v2-a1-r1.json` existed (`ls` returned "No such file or directory"). This satisfies
DEC-20260923-80e280 RC-4 (b). The rest of this note follows below this section.)

## RC-4 (b): declared metadata key paths (JSON pointer), recorded before either plan was written

`trial-plan-v2-r1.json` (11 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed (2 → "2-r1") | protocol label |
| `/task_id` | changed (→ TASK-20260923-3aa31e) | task ids |
| `/written_by_task` | added (TASK-20260923-a681f9) | task ids |
| `/archived_by` | changed (→ "TASK-20260923-b53550 phase A (Coordinator)") | archived_by |
| `/repair` | added | the `repair` block |
| `/gate/regression` | added (REG-1) | gate.regression |
| `/id_map` | added (31 entries, v2 → r1) | id map |
| `/v2_ids_never_reused` | added (the 31 frozen v2 ids) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids) | never-reused lists |
| `/retired_ids` | added | retired id lists |
| `/ceiling_note` | added | ceiling note |

`trial-plan-v2-a1-r1.json` (12 paths):

| path | added / changed | PS-3 category |
| --- | --- | --- |
| `/protocol_version` | changed ("2-a1" → "2-a1-r1") | protocol label |
| `/task_id` | changed (→ TASK-20260923-292052) | task ids |
| `/written_by_task` | changed (TASK-20260923-4c64b5 → TASK-20260923-a681f9) | task ids |
| `/archived_by` | changed (→ "TASK-20260923-b53550 phase A (Coordinator)") | archived_by |
| `/repair` | added | the `repair` block |
| `/gate/regression` | added (REG-1) | gate.regression |
| `/id_map` | added (11 entries, v2-a1 → r1) | id maps |
| `/id_map_v2` | added (31 entries, v2 → r1) | id maps |
| `/frozen_v2_ids_never_reused` | added (the 31 frozen v2 ids; RC-4 (d)) | never-reused lists |
| `/a1_ids_never_reused` | added (the 11 frozen v2-a1 ids; RC-4 (d)) | never-reused lists |
| `/retired_ids` | added | retired id lists |
| `/ceiling_note` | added | ceiling note |

In `trial-plan-v2-a1-r1.json` the pre-existing `/v2_ids_never_reused` is NOT a declared key. It is
mapped like every other field, so its image lists the 31 r1 v2 ids (RC-4 (d)). The frozen v2 and
v2-a1 ids are carried under the added keys `/frozen_v2_ids_never_reused` and `/a1_ids_never_reused`.
`/gate/v2_blocking_packages`, `/gate/addendum_blocking_package` and aggregate_a1's `driver_args` are
not declared keys either. They are mapped through M.

## RC-4 (a): the union map M (42 entries), recorded before either plan was written

Assignment rule: ids are taken in minting order (`implementation-v2-r1/minted-run-ids.txt`). The
first 31 go to the packages of `trial-plan-v2.json` in plan order, and the next 11 go to the packages
of `trial-plan-v2-a1.json` in plan order.

id_map_v2 (31):

| order | frozen v2 id | r1 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-ac4487 | RUN-GFPN-a61a10 | G1: F-1..F-3 fixture, n = m = 3, p' = 4111 |
| 2 | RUN-GFPN-3377f1 | RUN-GFPN-30d3ee | G2: F-1..F-3 fixture, n = m = 3, p' = 16777291 |
| 3 | RUN-GFPN-76420e | RUN-GFPN-b0993b | G3: jv_anchor_system_trace_identity, p' = 16777291 |
| 4 | RUN-GFPN-b231c1 | RUN-GFPN-3e521f | G4: frozen controls |
| 5 | RUN-GFPN-a07776 | RUN-GFPN-4fc824 | F-4 secondary fixture, n = m = 4 |
| 6 | RUN-GFPN-1ad09b | RUN-GFPN-27c136 | build p' = 4111 |
| 7 | RUN-GFPN-0c7483 | RUN-GFPN-fc29b6 | cells 4111 ecgfp5_shaped m = 5 |
| 8 | RUN-GFPN-4abae0 | RUN-GFPN-072f55 | cells 4111 random_2torsion m = 5 |
| 9 | RUN-GFPN-9e4212 | RUN-GFPN-a6ac23 | cells 4111 random_no2torsion m = 5 |
| 10 | RUN-GFPN-bbbbe3 | RUN-GFPN-d48e01 | cells 4111 ecgfp5_shaped m = 4 |
| 11 | RUN-GFPN-a521dd | RUN-GFPN-9696d7 | cells 4111 random_2torsion m = 4 |
| 12 | RUN-GFPN-a07b6d | RUN-GFPN-d6468a | cells 4111 random_no2torsion m = 4 |
| 13 | RUN-GFPN-dc1d4e | RUN-GFPN-98d454 | build p' = 262151 |
| 14 | RUN-GFPN-b9207c | RUN-GFPN-bda7a9 | cells 262151 ecgfp5_shaped m = 5 |
| 15 | RUN-GFPN-aa56bd | RUN-GFPN-1bcead | cells 262151 random_2torsion m = 5 |
| 16 | RUN-GFPN-e5b90d | RUN-GFPN-b76390 | cells 262151 random_no2torsion m = 5 |
| 17 | RUN-GFPN-d2f759 | RUN-GFPN-aad5a9 | cells 262151 ecgfp5_shaped m = 4 |
| 18 | RUN-GFPN-745cad | RUN-GFPN-286cdb | cells 262151 random_2torsion m = 4 |
| 19 | RUN-GFPN-aeff00 | RUN-GFPN-4e37c2 | cells 262151 random_no2torsion m = 4 |
| 20 | RUN-GFPN-3db273 | RUN-GFPN-5cb274 | build p' = 16777291 |
| 21 | RUN-GFPN-3be8a4 | RUN-GFPN-1626b4 | cells 16777291 ecgfp5_shaped m = 5 |
| 22 | RUN-GFPN-00e64b | RUN-GFPN-2d52fc | cells 16777291 random_2torsion m = 5 |
| 23 | RUN-GFPN-c5294d | RUN-GFPN-f917a8 | cells 16777291 random_no2torsion m = 5 |
| 24 | RUN-GFPN-36cad2 | RUN-GFPN-5fc8d7 | cells 16777291 ecgfp5_shaped m = 4 |
| 25 | RUN-GFPN-11d2ad | RUN-GFPN-8b0643 | cells 16777291 random_2torsion m = 4 |
| 26 | RUN-GFPN-fc5d58 | RUN-GFPN-e2a2a5 | cells 16777291 random_no2torsion m = 4 |
| 27 | RUN-GFPN-8f86cc | RUN-GFPN-3e568b | aggregate |
| 28 | RUN-GFPN-e26e4b | RUN-GFPN-25adbd | contingency 1 |
| 29 | RUN-GFPN-9da048 | RUN-GFPN-a3773d | contingency 2 |
| 30 | RUN-GFPN-59320d | RUN-GFPN-cb9dff | contingency 3 |
| 31 | RUN-GFPN-1596f6 | RUN-GFPN-3868df | contingency 4 |

id_map_a1 (11):

| order | frozen v2-a1 id | r1 id | label |
| --- | --- | --- | --- |
| 1 | RUN-GFPN-0d91bf | RUN-GFPN-14cfa2 | controls_a1, p' = 1073741831 (the addendum's blocking package) |
| 2 | RUN-GFPN-8c772a | RUN-GFPN-dd64d4 | build p' = 1073741831 |
| 3 | RUN-GFPN-569fd7 | RUN-GFPN-097656 | cells 1073741831 ecgfp5_shaped m = 5 |
| 4 | RUN-GFPN-086463 | RUN-GFPN-8fd922 | cells 1073741831 random_2torsion m = 5 |
| 5 | RUN-GFPN-bab146 | RUN-GFPN-a901d9 | cells 1073741831 random_no2torsion m = 5 |
| 6 | RUN-GFPN-7dd55d | RUN-GFPN-6435b2 | cells 1073741831 ecgfp5_shaped m = 4 |
| 7 | RUN-GFPN-47aa51 | RUN-GFPN-f7733e | cells 1073741831 random_2torsion m = 4 |
| 8 | RUN-GFPN-3a70f1 | RUN-GFPN-3a1c9f | cells 1073741831 random_no2torsion m = 4 |
| 9 | RUN-GFPN-ae4918 | RUN-GFPN-c8870b | aggregate_a1 |
| 10 | RUN-GFPN-8cfac3 | RUN-GFPN-8e4d7d | contingency a1-1 |
| 11 | RUN-GFPN-6a7f35 | RUN-GFPN-51e56b | contingency a1-2 |

## 1. Binding, scope and sequencing checks

- **RC-1.** Checked before any file was written, at 2026-09-23T21:17Z. All three sha256 values equal
  the bound values:
  - `v2_addendum_paristack.yaml`: 856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7;
  - `v2_addendum_rung31.yaml`: 2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c;
  - `v1_to_v2_reanchor_and_arm_iii.yaml`: e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3.
- **Repository state at start.** HEAD was ce34983dfa2798f4bfc418fa89cc4c8e5dd4f8f8, the claim commit of
  this card. `git status --porcelain --untracked-files=all` was empty.
- **DV-9 baseline.** Taken at 21:17:28Z, before any write: 393 files under the frozen paths, hashed with
  sha256.
  - Pre-existing byte code: `implementation/__pycache__/` (v1, gitignored) held 5 `.pyc` files, dated
    2026-09-21 to 2026-09-23T03:17. It was recorded in the baseline. Nothing was added.
- **R1-9 sequencing.** `runs/` held 50 directories (the 48 v1 packages, RUN-GFPN-ac4487 and
  RUN-GFPN-3377f1) and `.gitkeep`. No directory exists for any of the 42 new ids or the 40 retired ids
  (DV-10, which lists them). Nothing under `runs/` was read except RUN-GFPN-ac4487 (REG-1 reference,
  DV-8) and RUN-GFPN-3377f1 (the DV-3 reference: only the failure text quoted in the addendum).
- **Host.** MemTotal 16481980 kB, SwapTotal 0, 4 CPUs, Python 3.11.15, cypari2 2.2.0 (PARI 2.15.4),
  gp 2.15.4, msolve 0.6.5-1build2. The dispatcher reported its guard (`scratchpad/memguard.sh`,
  pid 875) with threshold MemAvailable < 2621440 kB, which is above 12.0 GB. So the child cap stays
  10737418240 (AC-1).
- **Machine quiet.** No msolve, gp, sage or valgrind process was running at the start of DV-3. Every
  development process ran alone, in sequence.
- **No outer guard.** No development process was wrapped in `timeout` or any other guard. The only
  child timeouts are the ones in the frozen code and in `run_child` calls (7200 s for the gp
  cross-check, as a1_pari; 1800 or 3600 s for the scratch probes).

## 2. Files written (the exact stage-R1 list)

`experiments/EXP-GFPN-05ff43/implementation-v2-r1/` (13 files; sha256 of the final bytes):

| file | role (addendum PS-2) | sha256 |
| --- | --- | --- |
| `r1_common.py` | shared context; PS-1 P-A configuration; RC-2 read-backs; RC-3 read-back helper; pari-stack.json | ea3ea5da076a544cca3b4c4fe1fbc72da129ed734d405336b871879a6ee107c0 |
| `r1_entry_v2.py` | entry point, v2 driver commands (a) | 82594a7b3830e79acc83514966b87525e1777a0bbf690b2748b5499901e907b4 |
| `r1_entry_a1.py` | entry point, v2-a1 driver commands (a) | f404a2d96985b84dda78340f29d5792c97499217acf28d65d3424b3864c971fd |
| `r1_run_wrapper.py` | r1 run wrapper, R-1..R-13, --dry-run (b) | b3d00e1ada7af2e39331bab0013f564be591bda2228b7ebe51944436734fb9d6 |
| `r1_check_run.py` | r1 completion-gate checker (c) | 87d23924a3f1c317eaf1773683b365631a538d22836da698829a6517052812d6 |
| `r1_reg1.py` | REG-1 comparator (c) | 1b4e4c880f829e8f04915c6a55b9274c9391c6dea701880f63671963db7d1d26 |
| `reg1-exclusion-list.json` | REG-1 exclusion list, PS-4 (e) (c) | 4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c |
| `r1_make_plans.py` | plan writer (d) | e58720cd1ee8f876fd97a5e19bcb49dab4cbac30f6bb31eb37fcf7fbf73f2e0e |
| `minted-run-ids.txt` | the 42 ids in minting order (plan-writer input) | b065914e5120def71c8f112d0b1eb35d869a6f23a33ef2635f40ca436bbb7b28 |
| `r1_devchecks.py` | development checks: DV-2, DV-3, DV-4, RC-2 semantics probe, dispatcher (e) | b777a27b139ff6059be7bd01987638765799e3ecd5f8b1601428f60c480789f4 |
| `r1_devchecks_more.py` | development checks: DV-1 static, DV-5, DV-8, DV-9, DV-10 (e) | 99e1f144adb95a30d8290065a948200f90864263916db76f1c6a1ccb843b8c00 |
| `r1_dv6.py` | development check DV-6 (e) | d3eac6bfa5a13a1e4beb62ec2246766d09790d6ef8962a6e39d9748d734c4507 |
| `r1_toy.py` | development check DV-7, and the DV-1 dynamic trace (e) | e72582251725b9dcc355264521903b2ded2a2884d8c4b73a5243c29834fafc82 |

The other three paths written:

- `experiments/EXP-GFPN-05ff43/trial-plan-v2-r1.json`: sha256
  14ca7bb5cfdcb031496b1fdbd272fb40f2b27b6f0621de037190e8c7a6586ec8;
- `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r1.json`: sha256
  c9f3c08e8a0b3dec4ae190bbcdd1f50985eaba9c61cbae1bfebbb84ad3f9efb4;
- this note.

Nothing else was written in the repository. Development outputs are in
`/tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/stageR1/` (below, `$S`).

## 3. PS-1: the branch, the values, the API and the RC-2 read-back semantics

- **Branch: P-A.** No P-B trigger condition occurred. DV-2 passed at every point, and no overflow,
  VmHWM excess or read-back mismatch appeared. `v2_common.curve_order_pari` is not replaced. No P-B
  code exists in the layer. `pari_child_timeout_s` is absent from both plans (P-B only). The r1 plans
  record `repair.ps1_branch: "P-A"`. Because stage R1 stopped, that value is not final (R1-7).
- **Values.** parisize 67108864 and parisizemax 536870912. No other value is used anywhere.
- **API.** In each entry process, `r1_common.PariStack.configure()` runs
  `h = cypari2.Pari(); h.allocatemem(67108864, 536870912, silent=True)`.
  - This happens BEFORE the entry imports any v2 or v2-a1 module. The entry imports only
    `r1_common`, which imports no v2 or v2-a1 module.
  - In cypari2 2.2.0 `Pari.allocatemem(s, sizemax)` calls `set_pari_stack_size` → libpari
    `paristack_setsize`.
  - `pari-stack.json` records `configured_before_first_v2_or_a1_import` (true in every recorded
    entry run), the cypari2 version (importlib.metadata) and the PARI library version (RC-2 (c)).
- **Why a fresh handle keeps the configuration.** cypari2 2.2.0 `Pari.__init__`
  (`pari_instance.pyx` lines 613-617) sets `size = max(8000000, rsize)` and
  `sizemax = max(size, vsize, 0)`. So each fresh `cypari2.Pari()` (as v2_common.py line 253 constructs)
  re-applies the larger configured values and never lowers them. The RC-2 read-backs confirm this in
  every run.
- **RC-2 (a) start read-back.** After all imports and immediately before dispatch, the entry constructs
  a fresh `cypari2.Pari()`, reads `default(parisize)` and `default(parisizemax)`, then does the same
  through a second fresh handle. It exits with code 2 before any command unless all four readings are
  exact.
- **RC-2 (b) exit read-back.** At exit, normal or by exception, the entry reads both defaults through
  the retained second handle. It does not construct a new handle, because construction would re-size
  the stack. It also reads `/proc/self/status` VmHWM, VmRSS, VmPeak and VmSize. Everything goes into
  `pari-stack.json`, and the r1 wrapper copies that file into manifest `resources.pari_stack`.
- **RC-2 (b) semantics: established as "requested".** Semantics probe, `$S/semantics/semantics_probe.json`,
  under the layer's configuration:
  - `my(v = vector(4000000, i, i^2 + 2^70)); #v` grew the stack twice ("increasing stack size to
    134217728", then "to 268435456").
  - After the growth, `default(parisize)` still read 67108864 and `default(parisizemax)` read
    536870912. `stacksize()` read 268435456, the grown current size. A fresh handle constructed
    afterwards reset the current size to 67108864.
  - So on this host `default(parisize)` reports the requested size. The exit rule is exact equality,
    67108864 and 536870912 (`r1_common.PARISIZE_EXIT_SEMANTICS = "requested"`; r1_check_run applies
    it).
  - In DV-2 no call needed growth: the current size stayed 67108864.

## 4. RC-3: the redirection list (in-process only; no function, class or computation replaced)

| entry | attribute | frozen value | r1 value | set when | reason |
| --- | --- | --- | --- | --- | --- |
| r1_entry_v2 | `v2_common.PLAN_PATH` | `experiments/EXP-GFPN-05ff43/trial-plan-v2.json` | `experiments/EXP-GFPN-05ff43/trial-plan-v2-r1.json` | after `import v2_common`, before `import v2_driver` | PS-2 list; RC-3 (a) |
| r1_entry_v2 | `v2_common.TASK_ID` | TASK-20260923-cd932c | TASK-20260923-3aa31e | same | PS-2 list; RC-3 (a) |
| r1_entry_a1 | `a1_common.PLAN_A1_PATH` | `.../trial-plan-v2-a1.json` | `.../trial-plan-v2-a1-r1.json` | before `import a1_driver` | PS-2 list; RC-3 (b) |
| r1_entry_a1 | `a1_common.V2_PLAN_PATH` | `.../trial-plan-v2.json` | `.../trial-plan-v2-r1.json` | before `import a1_driver` | PS-2 list |
| r1_entry_a1 | `a1_common.RECEIPT_V2_PHASE_B` | `coordination/.../TASK-20260923-0fa03f/post-run-receipt.json` | `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-b53550/post-run-receipt.json` | before `import a1_driver` | PS-2 list; RC-8 |
| r1_entry_a1 | `a1_common.V2_GATE_PACKAGES` | (RUN-GFPN-ac4487, RUN-GFPN-3377f1, RUN-GFPN-76420e, RUN-GFPN-b231c1) | (RUN-GFPN-a61a10, RUN-GFPN-30d3ee, RUN-GFPN-b0993b, RUN-GFPN-3e521f), read from trial-plan-v2-r1.json `gate.blocking_packages` | before `import a1_driver` | PS-2 list |
| r1_entry_a1 | `a1_common.TASK_ID_RUNS` | TASK-20260923-6c7f55 | TASK-20260923-292052 | before `import a1_driver` | PS-2 list |
| r1_entry_a1 | `a1_common.PROTOCOL_VERSION` | "2-a1" | "2-a1-r1" | before `import a1_driver` | PS-2 list |
| r1_entry_a1 | `v2_common.PLAN_PATH` | set by `a1_common.redirect_v2()` at a1_driver import | = the redirected PLAN_A1_PATH (`trial-plan-v2-a1-r1.json`); never set to trial-plan-v2-r1.json | by redirect_v2 (a1_driver.py line 30) | RC-3 (b) |
| r1_entry_a1 | `v2_common.TASK_ID` | TASK-20260923-6c7f55 (redirect_v2's definition-time default, a1_common.py line 90) | TASK-20260923-292052 | AFTER `import a1_driver` | RC-3 (b), the catch-all of PS-2 (addendum lines 387-391) |

Notes on the redirections:

- **RC-3 (d).** Each entry reads every redirected attribute back from its module after all imports and
  immediately before dispatch. It exits with code 2 before any command unless each equals its r1 value.
  - The a1 entry additionally checks two things: `a1_driver.C is v2_common`, and that the r1 gate ids
    of trial-plan-v2-r1.json equal trial-plan-v2-a1-r1.json `gate.v2_blocking_packages`.
  - The read-back goes into `pari-stack.json` under `redirections` and from there into the manifest.
  - It records the r1 values only. A frozen task id is never written into a run artifact.
- **RC-3 (e).** `r1_check_run.py` runs `v2_check_run.main` or `a1_check_run.main` in a SEPARATE
  process, with only the redirections above applied (the a1 constants before `a1_check_run` is
  imported). The checker process imports neither checker.
  - The REG-1 comparator imports no v2 or v2-a1 module.
- **An observation, not a defect.** `v2_common.TASK_ID` is read by no frozen v2 function; it is only a
  constant. It is redirected and read back anyway, as RC-3 requires.

## 5. The plans (PS-3; RC-4)

- **Counts.**
  - trial-plan-v2-r1.json: 31 packages (27 planned + 4 contingency), protocol_version "2-r1", task_id
    TASK-20260923-3aa31e, written_by_task TASK-20260923-a681f9, archived_by "TASK-20260923-b53550
    phase A (Coordinator)".
  - trial-plan-v2-a1-r1.json: 11 packages (9 planned + 2 contingency), protocol_version "2-a1-r1",
    task_id TASK-20260923-292052, written_by_task TASK-20260923-a681f9, the same archived_by, and
    plan_branch "31-bit" unchanged.
- **Order and ids.** These are the id_map tables above. Package order equals the frozen plan order, and
  every package id is the image of the frozen id at the same order (DV-5).
- **Gate.**
  - The r1 gate is (RUN-GFPN-a61a10, RUN-GFPN-30d3ee, RUN-GFPN-b0993b, RUN-GFPN-3e521f), the images of
    the four v2 gate packages.
  - The a1-r1 plan's `gate.v2_blocking_packages` holds the same four ids, and
    `gate.addendum_blocking_package` is RUN-GFPN-14cfa2, the image of controls_a1.
  - `gate.regression` (REG-1) is in both plans, with exclusion_list_sha256
    4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c.
- **aggregate_a1 driver_args.** `--a1-runs` RUN-GFPN-097656,8fd922,a901d9,6435b2,f7733e,3a1c9f.
  `--v2-runs` holds the 18 r1 v2 cell ids. `--v2-aggregate` is RUN-GFPN-3e568b.
- **Retirement (`retired_ids`, both plans).**
  - Used v2 ids, kept as records and never re-run: RUN-GFPN-ac4487 and RUN-GFPN-3377f1.
  - 29 unused v2 ids and 11 unused v2-a1 ids, exactly the addendum's PS-3 enumeration (the writer
    asserts this).
- **Ceiling note.** 2 + 31 + 11 = 44 of 48, with 4 unreserved.
- **`watchdogs`.** Identical to trial-plan-v2.json's in both plans (writer and DV-5).
- **RC-4 (c) reading (disclosed).** Several declared paths are CHANGED keys that the frozen plan also
  holds: `/protocol_version`, `/task_id`, `/archived_by`, and `/written_by_task` in the a1 plan.
  - Deleting them from the r1 side only could never produce equality. So both the writer and DV-5
    delete every declared path from BOTH sides (a no-op where the frozen plan lacks the key).
  - Then they apply the inverse of M and compare canonical JSON.
  - The canonical sha256 of both sides is recorded in DV-5.
- **Plan history (disclosed).**
  - The plans were first written at 21:34:14Z.
  - At 21:40Z they were regenerated with one change: prose inside two declared keys
    (`/ceiling_note` and `/gate/regression/rule`) no longer spells the used v2 ids.
  - The declared key paths did not change. No plan was treated as final at any time.
- **Stale prose kept unchanged, because the RC-4 (c) equality requires it (noted for the Coordinator).**
  - `trial-plan-v2-a1-r1.json` `/task_id_note` still reads "written by stage 1b under
    TASK-20260923-4c64b5".
  - Its aggregate_a1 package `content` still names "TASK-20260923-0fa03f post-run receipt". The r1
    rule is the b53550 phase-B receipt (RC-8), stated in `repair.v2_gate_repointed_to`.
  - The frozen `written_at`, `written_in`, `package_count_note` and `id_minting` strings are unchanged.
- **Observation: the cited watchdogs line range.** The `watchdogs` object of trial-plan-v2.json starts
  at line 95 and its last member is at line 177. Its closing brace ` },` is at line 178. DV-5 parses
  lines 95-178 and checks that lines 95-177 are its content.

## 6. REG-1 (PS-4; RC-6; RC-7): comparator and exclusion list

- **Comparator.** `r1_reg1.py` (also `r1_check_run.py reg1 ...`) compares a candidate with the reference
  RUN-GFPN-ac4487.
  - It first verifies every reference file it reads against the TASK-20260923-0fa03f post-run receipt
    `path_sha256`. That is 111 files: 36 `.ms`, 36 `.ms.out`, 38 certificates and `raw-result.json`.
    A mismatch, or a file the receipt does not bind, is fatal.
  - (a) `solver/*.ms`: the file sets must be equal and every file byte-identical.
  - (b) raw-result.json: run_status / failure_class / gate_pass; every entry of `targets`,
    `planted_targets` and `replaced_fresh_targets`, whole, minus the exclusions; the D table derived
    from them; `structure_checks`; `fixture_F1` (added, stricter); `fixture_F2a`; `fixture_F2b`;
    `fixture_F3`; `group` (order_pari_ellcard 69477519282, N_times_G_is_O); `rescaling` (beta, lam,
    b_is_square_in_Fq, ...); `curve_checks`; every fresh target's k (read from its certificates) and
    x_R; the `certificate` block (kind, verified, count); `metrics` minus `wall_seconds`.
  - (c) `certificates/*.json`: the file sets must be equal, and every file equal as JSON after the
    exclusions.
  - (d) `solver/*.ms.out`: byte-identical. No exclusion is declared for msolve output.
- **Output.** Deterministic text: per file and field, the exclusion list's sha256, the failures and
  `REG-1 VERDICT: PASS|FAIL`. It is designed to be quoted verbatim (RC-7). The wrapper evaluates REG-1
  before G2 and before every later package of either plan, and records `gate.regression_REG-1`
  (verdict, sha256, failures, full output) in the manifest.
- **Exclusion list.** Declared by reading RUN-GFPN-ac4487's archived bytes and the v2 code.
  - Certificates differ only in `run_id`: it is the only certificate field that names the package, in
    all 38.
  - No `.ms` or `.ms.out` file contains a path, an id or a timestamp.
  - The list never names k, x_R, relation, beta, lam, u_values, relation_mod_T, D, solutions, verified
    or lifted_points. Every entry is confined to a PS-4 (e) category, and the comparator refuses a list
    that breaks either rule.
- **READINGS FOR RJ-2 REVIEW.**
  - X16 and X17 exclude the callgrind instruction counts (`instructions_user`,
    `f4_core_inclusive_Ir`). They are classified under "wall and cpu seconds" as the cpu-cost
    measurement of the execution. They include dynamic-loader and libc start-up work, which depends on
    the environment and argv.
  - PS-4 (e) does not name instruction counts. This classification is a judgment.

The exclusion list, verbatim (`implementation-v2-r1/reg1-exclusion-list.json`, sha256
4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c):

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

## 7. The r1 wrapper (PS-5) and the r1 checker

- **Refusals.** `r1_run_wrapper.py RUN-ID [--replaces RUN-ID] [--dry-run]` implements R-1..R-13 as the
  addendum states them (lines 546-576). It evaluates every check before creating any directory, and on
  refusal it prints every failing reason and exits 2.
  - R-4, R-5 and R-6 compare each tree with its receipt file by file, and check that it is tracked
    and clean (untracked files count as dirty).
  - They also require that no file under the tree is left unbound, on disk as well as in git. This
    catches byte code.
  - R-5 is applied to every package, v2 packages too. That is stricter than applying it to addendum
    packages only.
- **Launch rule.** The package is launched directly: the command is
  `[python3, -B, r1_entry_v2.py | r1_entry_a1.py] + driver_args`, read from the plan.
  - There is no outer guard, and `command.txt` states this.
  - The child environment adds GFPN_RUN_DIR, GFPN_V2_PACKAGE, GFPN_V2_REPLACES, PYTHONUNBUFFERED=1 and
    PYTHONDONTWRITEBYTECODE=1.
- **Manifest fields (PS-5 manifest).** Every v2 / v2-a1 field, plus:
  - `protocol_version`; the `amendment`, `addendum` (addendum packages) and `repair` blocks;
    `task_id` from the plan's run card; `derived_from` (the retired id).
  - `code.phase_a_commits` LITERALLY: TASK-20260923-0fa03f fb4597b2014b44a0c9528d48d3ab9997b46f038c;
    TASK-20260923-b53550 read from its phase-A receipt at run time (receipt commit_sha, else
    `git log -1` of the receipt); on addendum packages TASK-20260923-4ff597
    36c3b0d2e05878a8df1209b5048f8ce14515c27f. Each has a `sources` entry, which also carries the
    receipt-derived reading.
  - Clean flags for all three implementation trees.
  - `resources.pari_stack`: the whole pari-stack.json.
  - `gate.regression_REG-1` from G2 on.
  - The child getrlimit read-backs, threads executed, host RAM and swap, and watchdogs with
    `equal_to_trial_plan_v2`.
  - Dependency versions, with cypari2 read through importlib.metadata.
  - `environment.PYTHONHASHSEED_inherited`, and the inference block.
- **PYTHONHASHSEED (RC-6; DISCREPANCY FLAGGED, deviation RD-1).** The r1 wrapper does NOT set
  PYTHONHASHSEED, as RC-6 states literally. But RC-6's stated premise, "RUN-GFPN-ac4487 ran without
  it", does not match the frozen code.
  - `v2_run_wrapper.py` line 178 sets `PYTHONHASHSEED="0"` for the driver, so RUN-GFPN-ac4487 ran with
    PYTHONHASHSEED=0. `a1_run_wrapper.py` line 299 does the same.
  - Following RC-6 literally therefore gives G1 a different condition from the reference: unset
    (Python randomizes per process) versus "0". Following its purpose ("G1 inherits the same condition
    as the reference") would mean setting "0".
  - The wrapper follows the literal text and records the inherited value, or "unset".
  - This needs a Coordinator ruling before any plan is final. The DV-7 msolve probes (section 12)
    showed no dependence of msolve output on PYTHONHASHSEED.
- **Checker.** `r1_check_run.py RUN_DIR` runs the frozen checker, unchanged, in a separate process, then
  the r1 checks:
  - the labels, blocks, run card and derived_from;
  - the literal phase-A commits;
  - the three clean flags;
  - pari_stack: status not refused; every redirection equal; both start handles exact; exit exact;
    configured before the first v2 import; branch P-A; cypari2 version recorded;
  - REG-1 PASS with the plan's exclusion sha from G2 on;
  - no file of the package carrying either forbidden task id (a byte scan of every file);
  - watchdogs equal; the inference block; status agreement.

## 8. DV-1: inventory of every PARI use

Static search: `r1_devchecks_more.dv1_static` (defined, NOT run because of the STOP). The search below
was made by hand at the start of stage R1, with `grep -n -i "cypari2|pari|ellcard|allocatemem|parisize|/usr/bin/gp|sage"`
over implementation-v2/ and implementation-v2-a1/, plus the call graph read from the code.

| command (plan) | PARI use | file:line | process | (p', field degree, curve) reached by the r1 plans |
| --- | --- | --- | --- | --- |
| v2 `fixture --p 4111` (G1) | `C.curve_order_pari` → `cypari2.Pari()` + ellcard | v2_driver.py 279 → 308; v2_common.py 253, 261 | driver, IN-PROCESS | (4111, 3, fixture_n3(4111)) |
| v2 `fixture --p 16777291` (G2) | same | same | driver, IN-PROCESS | (16777291, 3, fixture_n3(16777291)) |
| v2 `controls` (G4) | same, on fixture_n3(4111) | v2_driver.py 764, 771; v2_common.py 253, 261 | driver, IN-PROCESS | (4111, 3, fixture_n3(4111)) |
| v2 `fixture4` (F-4) | same, on fixture_n4 | v2_driver.py 542; v2_common.py 253, 261 | driver, IN-PROCESS | (4111, 4, fixture_n4) |
| v2 `anchor-identity` (G3) | Sage comparator k4a_anchor_system.py: `GF(p ** 5, "z", modulus=...)` (comparator line 137) | v2_driver.py 650 (`V.run_child(SAGE_PYTHON, COMPARATOR)`) | capped CHILD (Sage) | GF(16777291^5) in Sage |
| a1 `controls-a1 --p 1073741831` | `/usr/bin/gp` ellcard, isprime, norm | a1_driver.py 89 → a1_pari.py 36-39, 94-96 | capped CHILD (gp) | (1073741831, 5, the three 31-bit curves) |
| v2 build / cells / aggregate; a1 build / cells / aggregate-a1 | none (orders from ladder.json; builders in v2_child.py children use flint and numpy) | — | — | — |

- **No in-process PARI call is reached at a ladder prime** (262151, 16777291 or 1073741831 at n = 5).
  The only in-process call site is `v2_common.curve_order_pari`, reached at exactly the three DV-2
  points. This is the same set as the addendum's three call sites; nothing was added.
- **The layer's own PARI uses.** `r1_common.PariStack` constructs `cypari2.Pari()` handles
  (configuration and read-backs) and calls allocatemem and default. It performs no computation.
- **Dynamic trace (partial; DV-7 stopped after the two toy G1 runs).** Source:
  `$S/dv7/toy/pari-trace.jsonl`, sha256 0999bcb5e023ae3b045a05e8487032cfe7e97fe13ee2556f7cc6305d59658ffb,
  187 events.
  - `cypari2.Pari.__call__` occurred twice, both from `v2_driver.py:279 → :308 → v2_common.py:261`, at
    p = 1033 with field degree 3 (toy G1, both worlds).
  - `cypari2.Pari()` constructions came from `r1_common.py:181/194/196` and `v2_common.py:253` only.
  - Children: msolve 72, valgrind 71, python3 builders 32. No gp or sage child was reached on this path.
  - The rest of the toy lineage (fixture4, build, cells, aggregate, all v2-a1 commands) was not traced,
    because of the STOP.
- **FLAGGED TO THE COORDINATOR (child-side PARI at a library default; not fixed, out of scope).**
  - The anchor-identity Sage comparator configures no PARI stack. A search of k4a_anchor_system.py
    finds no `pari`, `allocatemem` or `parisize`.
  - At GF(16777291^5) it therefore runs at Sage's default PARI stack.
  - The no-computation start-up probe of that default (`dv1_static`: a capped Sage child reading
    `pari.default('parisize' / 'parisizemax')`) was not run, because of the STOP. The value is
    unmeasured.
  - The gp child of controls-a1 runs with explicit `default(parisize, 256000000);
    default(parisizemax, 4000000000)` (a1_pari.py line 38). It is not at a library default.

## 9. Development notes DV-2..DV-10 (no run package; no number is a result)

Every note below is a development note of TASK-20260923-a681f9. The group orders are parameters.
Commands were run from `implementation-v2-r1/` with `PYTHONDONTWRITEBYTECODE=1 python3 -B`.

- **DV-3, negative control: PASS (the overflow was reproduced).** 21:28:01Z.
  `r1_devchecks.py dv3 --out $S/dv3`.
  - In a fresh process WITHOUT the configuration, the unchanged `v2_common.curve_order_pari` on
    `fixture_n3(16777291)` raised `PariError: ellcard: the PARI stack overflows (current size: 8003584;
    maximum size: 8003584)`.
  - The read-backs before the call were parisize 8000000 and parisizemax 8003584. stderr shows
    "Warning: increasing stack size to 8003584."
  - Record: `$S/dv3/dv3_16777291_n3.json`.
- **RC-2 semantics probe: "requested"** (section 3). Record: `$S/semantics/semantics_probe.json`.
- **DV-2 and DV-4: PASS under P-A at all three points, two fresh processes each.** 21:28:15Z.
  `r1_devchecks.py dv2 --out $S/dv2`. Report: `$S/dv2/dv2.json`.
  - Each worker runs the entry's code exactly up to dispatch: configure, `import v2_common`, the two
    redirections, `import v2_driver`, RC-3 read-back, RC-2 start read-back. It then calls the unchanged
    `curve_order_pari` on the unchanged `fixture_n3` / `fixture_n4` objects.
  - (4111, n = 3): N = 69477519282 in both repetitions, equal to RUN-GFPN-ac4487. Hasse holds:
    N - q - 1 = 299650 with q = 69477219631. [N]G = O for the basepoint stream
    `2026092002:v2:fixture:4111:basepoint`. [N]P = O for the RC-5 second point stream
    `2026092002:v2r1:dv2:4111:3`, and P ≠ G. The call took 0.003 s. VmHWM after: 66007040 and 66002944
    B. The v2_solver.self_rss_bytes reading equalled the VmRSS reading.
  - (16777291, n = 3): N = 4722429815066881402162 in both. Hasse holds: N - q - 1 = 44360348990. [N]G
    and [N]P = O. 0.317 and 0.301 s. VmHWM 88014848 and 88141824 B. RC-5 gp cross-check: N =
    4722429815066881402162, agrees. gp child outcome ok; getrlimit read back soft = hard =
    10737418240; `/proc` limits 10737418240.
  - (4111, n = 4): N = 285620852275820 in both. Hasse holds: N - q - 1 = 2372778. [N]G (stream
    `2026092002:v2:fixture4:4111:basepoint`) and [N]P = O. 0.008 s. VmHWM 67612672 and 67653632 B.
    RC-5 gp cross-check agrees, getrlimit 10737418240.
  - Read-backs:
    - start, both fresh handles, in every run: 67108864 / 536870912;
    - before and after each call: the same;
    - exit, through the retained handle: 67108864 / 536870912;
    - the current stack size stayed 67108864, with no growth.
  - VmHWM ≤ 805306368 at every point (maximum 88141824). DV-4: the driver RSS read with
    `v2_solver.self_rss_bytes` was below 1073741824 at every point (maximum 88039424).
  - `configured_before_first_v2_or_a1_import`: true. Versions: cypari2 2.2.0; PARI "GP/PARI CALCULATOR
    Version 2.15.4 (released)".
- **DV-5, plan derivation with its own code path: PASS.** `r1_devchecks.py dv5 --out $S/dv5`. Report:
  `$S/dv5/dv5.json`.
  - M has 42 entries, is a bijection and maps onto fresh ids. `id_map_v2` of the a1 plan equals the
    v2-r1 `id_map`.
  - RC-4 (c) equality, computed by DV-5's own implementation (path walking and a character scanner, not
    the writer's functions): TRUE for both plans. The canonical sha256 of both sides is
    0588623b9fe8eec632a5be376f87f018acc3fcbdf589bd98b33b7f2002d63252 for the v2-r1 plan and
    138545e96baf2811681d3f42e552679ffd529d8fba4bf66148fb273cc31f2537 for the a1-r1 plan.
  - The declared keys equal the RC-4 (b) record read back from this note. Watchdogs are identical. The
    plans hold 31 and 11 packages, in order, as images.
  - No old id appears outside the maps, the never-reused lists and retired_ids, with ONE disclosed
    exception: `/gate/regression/reference_run` names RUN-GFPN-ac4487 in both plans, because REG-1 must
    name its reference.
  - No forbidden task id. The a1 plan's `v2_ids_never_reused` is mapped.
  - The writer's own `--check` regenerated both files byte-identically. Its output: "regenerated
    byte-identically: True" for both.
- **DV-6, refusals: PASS.** 33 wrapper dry-run cases and 4 entry cases. `r1_devchecks.py dv6 --out
  $S/dv6`. Report: `$S/dv6/dv6.json`.
  - Baseline: G1 --dry-run with the two declared stubs printed "DRY RUN: every R-1..R-13 check passes".
    The stubs are: r1 tree reported tracked and clean, and a synthetic b53550 phase-A receipt in
    scratch.
  - Each case below exited 2, printed its expected reason, and wrote nothing. Before and after each
    case the real runs directory, the scratch runs directory and implementation-v2-r1/ were identical.
  - R-1: three altered amendment copies.
  - R-2: RUN-GFPN-ac4487, RUN-GFPN-3377f1, RUN-GFPN-76420e (retired planned v2), RUN-GFPN-e26e4b
    (retired v2 contingency), RUN-GFPN-0d91bf (v2-a1), RUN-GFPN-61bba9 (v1), and the unreserved
    RUN-GFPN-0f0f0f.
  - R-3.
  - R-4 and R-5: altered receipt copy; dirty tree through a simulated git state.
  - R-6: the REAL state (not tracked, `??` dirty, b53550 phase-A receipt absent); a synthetic receipt
    mismatch.
  - R-7: gate not run (the real state, for the F-4 image); G2 failed while REG-1 passed; REG-1 failed on
    a synthetic pair (a G1 copy with one D perturbed); controls_a1 image not passed.
  - R-8. R-9 (a plan copy with one watchdog value changed). R-10 (a simulated scan). R-11 (48 synthetic
    directories under the four plans' ids; and a plan copy with package_count 1).
  - R-12: a contingency on a gate package; across plans; on implementation_error; twice; `--replaces`
    on a non-contingency id.
  - R-13: a wrong label; a forbidden task id in a plan copy.
  - Entries, each in a fresh process through a development shim, exited 2 and wrote nothing but the
    refusal record `pari-stack.json` (status `refused_before_any_command`):
    - PARI read-back: the configuring call made not to reach PARI; both entries. Start read-back
      8000000 / 8003584.
    - RC-3 (f) redirection read-back: a hook re-redirects a constant at driver import; both entries.
  - **DV-6 disclosure.**
    - The a1 "redirect" case, as run, hooked the nested `v2_driver` import as well as `a1_driver`. It
      therefore simulated two faults, and both read-backs refused.
    - After the run, the shim in `r1_dv6.py` was narrowed to one fault per entry. That is a one-line
      change to development code only. The delivered `r1_dv6.py` is that later version, and DV-6 was
      not re-run on it, because of the STOP.
- **DV-8, REG-1 exclusion list and comparator: PASS.** `r1_devchecks.py dv8 --out $S/dv8`. Report:
  `$S/dv8/dv8.json`; verbatim self output in `$S/dv8/dv8_self_output.txt`.
  - The entries are confined to the permitted categories, and none names a never-excludable field.
  - RUN-GFPN-ac4487 against itself: PASS, with 111 reference files verified against the receipt.
  - Perturbed scratch copies FAIL, one per item:
    - (a) one byte of `solver/fx_reg0_S3.ms`;
    - (b) `targets[2].arms.S3.D + 1`;
    - (c) `factor_base.u_values[0] + 1` in one certificate;
    - (d) one byte of `solver/fx_fresh2_raw_u.ms.out`.
  - A control copy that differs only in excluded fields PASSES.
  - An altered receipt, which makes the reference bytes mismatch, gives FAIL (integrity is fatal).
- **DV-9, no edit: PASS.** 21:57Z. `r1_devchecks.py dv9 --out $S/dv9 $S/dv9-baseline-before.sha256
  $S/dv9-pycache-before.txt`.
  - All 393 baseline files are byte-identical: no change, no addition, no removal. The files covered:
    implementation/ (v1, including ladder.json), implementation-v2/, implementation-v2-a1/, the three
    implementation notes, trial-plan.json, trial-plan-v2.json, trial-plan-v2-a1.json, the
    specification, all amendments, both run packages and execution-report-v2.yaml.
  - They equal the 0fa03f phase-A, 4ff597 phase-A and 0fa03f phase-B receipts, and all three amendment
    hashes are the bound values.
  - No new byte code exists anywhere under the experiment.
- **DV-10, ids: PASS.** `r1_devchecks.py dv10 --out $S/dv10 $S/check-outputs.txt`.
  - 42 ids, all distinct. Each BARE id was checked with `--check` at minting time, before any stage-R1
    file named it: rc 0, "occurrences across the union (26353 identifier-bearing paths scanned): 0",
    "OK: well-formed and free across the union."
  - None is in the v1 (49), v2 (31) or v2-a1 (11) lists. No run directory exists for any of the 42 or
    for any of the 40 retired ids.
  - Observation: a re-check at DV-10 time also reported 0 occurrences, although the ids now occur in
    stage-R1 files. The allocator apparently does not scan untracked working-tree files.
  - Every allocator output and every `--check` output is in section 14.
- **DV-7: STOP** (section 12).

## 10. getrlimit read-backs (every capped child of stage R1)

- DV-2 RC-5 gp children (2): soft = hard = 10737418240; `/proc/<pid>/limits` 10737418240.
- DV-7 toy G1, world A and world B: every msolve, valgrind and builder child read back soft = hard =
  10737418240 (manifest `child_rlimit_as_read_back_by_getrlimit`). msolve threads executed: [1].
- DV-7 toy ladder selection: gp children through the frozen `a1_toy.toy_ladder` / `a1_pari.curve_facts`
  (records in `$S/dv7/toy/ladder_*/`; attempt 1 in `$S/dv7_attempts/attempt1_ladder_incomplete/`).
- STOP diagnosis probes: 50 msolve children, every one soft = hard = 10737418240.
- No child failed to set the cap.

## 11. DV-7 as run (before the STOP)

- **Attempt 1 (21:4xZ): FAIL, harness parameter.** The toy ladder was incomplete. At the v2-role toy
  prime 1031, the frozen a1_toy rule found no ecgfp5-model curve (c in 1..400) with N = 2q, q prime and
  b a non-square. The attempt is preserved in `$S/dv7_attempts/attempt1_ladder_incomplete/`.
- **The change.** `r1_toy.py` now tries a declared candidate list (1031, 1051, 1061, 1091, 1151, 1171,
  1181, 1201) and records the trail. This changes no pipeline code.
- **Attempt 2 (21:51:45Z).**
  - Toy ladder: 1021 complete (a1 role); 1031 incomplete; 1051 complete (v2 role).
  - Toy n = 3 fixture data at 1033 and 1039. Toy n = 4 data at 1033.
  - Toy copies of both r1 plans (section 1 of `r1_toy.py`).
  - World A ran G1 (RUN-GFPN-a61a10 = `fixture --p 1033`) through the r1 wrapper and the v2 entry, with
    PYTHONHASHSEED 0. World B ran the same toy package with PYTHONHASHSEED 12345.
  - Both manifests passed every r1 read-back:
    - start and exit 67108864 / 536870912;
    - VmHWM 68468736 and 68501504 B;
    - redirections equal; configured before the first v2 import;
    - getrlimit 10737418240; threads [1];
    - phase_a_commits 0fa03f literal, plus the synthetic b53550 value;
    - protocol_version "2-r1"; task_id TASK-20260923-3aa31e; derived_from RUN-GFPN-ac4487.
  - No forbidden task id occurs in any toy artifact (a byte scan of both worlds).
  - REG-1 of world B against world A (toy receipt): **FAIL** → RC-6 STOP. The remaining toy lineage
    (G2, F-4, build, cells, aggregate, controls-a1, a1 build and cells, aggregate-a1, the RC-8 receipt
    check, the checker on every package, the REG-1 perturbation) was not run.
  - Report: `$S/dv7/dv7.json`, sha256 9491829e1d45f4b07e719af4241b7240420eff2e61ebb98387360ac799b98e78.

## 12. THE STOP: evidence (RC-6; card R1-7)

REG-1 failures between the two toy runs (verbatim from the comparator):

```
(d) solver/fx_reg0_torsion_S3_norm.ms.out differs
(b) run_status/failure_class/gate_pass differs
(b) D_table differs
(b) targets[0] (reg0) differs
(b) fixture_F1 differs
(b) metrics (minus X2) differs
```

- **(a) passed.** All 36 `solver/*.ms` inputs were byte-identical between the worlds, including
  `fx_reg0_torsion_S3_norm.ms`, sha256 541b57b904e0c16956f9ea4615a32f1aaaae1cdfe7ca9c3b767f3b5f22d537c8.
- **Only one system differed:** target reg0, arm torsion_S3_norm, at the toy prime 1033. Both worlds
  ran the same argv shape, `msolve -v 2 -t 1 -f IN -o OUT -P 1`, under the same cap.
  - World A: msolve stderr "Degree of the square-free part: 63", "[64, 63, 63]" and "Elimination
    polynomial is not squarefree". Its output parametrization has an eliminating polynomial of degree
    63 against a quotient dimension of 64. The v2 driver classified the arm
    `degenerate_parametrisation` (D undefined). F-1 therefore failed on reg0, and the package ended
    `failed` / `implementation_error` with gate_pass false.
  - World B: "Elimination polynomial has degree 64". D = 64; completed_valid, gate_pass true.
  - The two `.ms.out` files differ (sha256 prefixes d2878f4f2b276162 in A and 201812d43b7c7a9d in B).
- **Diagnosis probes, scratch and development only** (`$S/stop_probe/`): the identical input solved in
  capped children through the frozen `v2_solver.run_child`, with `v2_solver.msolve_argv(threads=1)`.
  - 20 runs in the probe's environment: all identical (201812d4…), all squarefree degree 64, all ok.
  - 10 runs each in a reconstruction of world A's msolve environment (PYTHONHASHSEED=0), world B's
    (12345), and one without PYTHONHASHSEED: all 30 identical to world B's output.
  - World A's output was not reproduced in 50 runs. PYTHONHASHSEED does not explain it.
  - Records: `probe.json` (b10ae3e7…301b) and `probe_env.json` (180bd31e…7646).
- **Observation.** With byte-identical input and flags, msolve 0.6.5 produced two different results in
  two processes, one of them not square-free. The world-A outcome did not recur in 50 further runs, so
  it is rare and non-reproducing. RC-6's rule is literal: a difference in any field REG-1 compares
  STOPS R1. The differing fields include D and the arm outcome, which the exclusion list may never
  absorb.
- **Not established (stated so that nothing is read into it).**
  - The mechanism inside msolve (for example a randomized sequence or projection step in its
    parametrization), and the rate of such events.
  - Whether such an event can occur at 4111, 16777291 or 1073741831. All 36 RUN-GFPN-ac4487 solves at
    4111 returned `ok` with the eliminating degree equal to D.
- **Reading, as RC-6 states it.** "The pipeline is not deterministic at toy scale; REG-1 could not be
  read; fixing it is out of this repair's scope." It is an impediment for a new Coordinator decision.
  - It is not a P-B trigger.
  - It is not a result about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
  - The toy D values are never measurements.
- **Not done, in accordance with the stop.**
  - DV-7 was not re-run to obtain a passing probe. That would be rerunning until a favourable result.
  - The DV-1 static start-up probe of the Sage child was not run.
  - DV-6 was not re-run on the narrowed shim.

## 13. Deviations and implementation readings (disclosed)

- **RD-1: PYTHONHASHSEED.** RC-6 is followed literally, and its premise conflicts with the frozen code
  (section 7). A Coordinator ruling is needed.
- **RD-2: RC-4 (c).** Declared CHANGED keys are deleted from both sides before the comparison
  (section 5).
- **RD-3: DV-5.** One disclosed old-id location, `/gate/regression/reference_run`.
- **RD-4: entry refusals.** "Nothing written" is read as "no command output". The entry still writes
  its refusal record `pari-stack.json`, because RC-2 (a) says the refusal is recorded. A refused entry
  leaves only that file. The wrapper then records the package failed / infrastructure_error, with the
  refusal reasons.
- **RD-5: REG-1 (b).** It compares whole target entries minus declared exclusions, and it adds
  `fixture_F1` and `curve_checks` (stricter than listed). Callgrind instruction counts are excluded as
  cpu measurements (X16, X17; for RJ-2 review).
- **RD-6: R-5 applies to v2 packages too** (stricter).
- **RD-7: the plans were regenerated once** at 21:40Z (prose only; section 5).
- **RD-8: DV-6's shim was narrowed after the run** (section 9).
- **RD-9: DV-7 attempt 1** failed on a toy-parameter choice and was preserved; the toy prime list was
  added (section 11).
- **RD-10: DV-1 is incomplete** (static search by hand only; Sage start-up probe not run; dynamic trace
  partial). DV-7 is incomplete, because of the STOP.
- **RD-11: observations for the Coordinator.**
  - The cited watchdogs line range (95-177 against 95-178).
  - Stale prose in the a1-r1 plan (section 5).
  - The allocator's re-check does not see untracked files.

## 14. Allocator and --check outputs, verbatim (DV-10)

Allocator outputs (42 mints). Mint 1 was the first call, and its output was captured to a file before
the loop ran.

```
### mint 1 (command: python3 -B tools/allocate_id.py --next run --area GFPN; rc=0)
free run id for 'GFPN': RUN-GFPN-a61a10
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a61a10
### mint 2 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-30d3ee
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-30d3ee
rc=0
### mint 3 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-b0993b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-b0993b
rc=0
### mint 4 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-3e521f
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-3e521f
rc=0
### mint 5 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-4fc824
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-4fc824
rc=0
### mint 6 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-27c136
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-27c136
rc=0
### mint 7 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-fc29b6
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-fc29b6
rc=0
### mint 8 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-072f55
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-072f55
rc=0
### mint 9 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-a6ac23
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a6ac23
rc=0
### mint 10 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-d48e01
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-d48e01
rc=0
### mint 11 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-9696d7
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-9696d7
rc=0
### mint 12 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-d6468a
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-d6468a
rc=0
### mint 13 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-98d454
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-98d454
rc=0
### mint 14 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-bda7a9
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-bda7a9
rc=0
### mint 15 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-1bcead
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-1bcead
rc=0
### mint 16 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-b76390
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-b76390
rc=0
### mint 17 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-aad5a9
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-aad5a9
rc=0
### mint 18 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-286cdb
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-286cdb
rc=0
### mint 19 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-4e37c2
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-4e37c2
rc=0
### mint 20 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-5cb274
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-5cb274
rc=0
### mint 21 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-1626b4
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-1626b4
rc=0
### mint 22 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-2d52fc
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-2d52fc
rc=0
### mint 23 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-f917a8
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-f917a8
rc=0
### mint 24 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-5fc8d7
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-5fc8d7
rc=0
### mint 25 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-8b0643
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-8b0643
rc=0
### mint 26 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-e2a2a5
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-e2a2a5
rc=0
### mint 27 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-3e568b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-3e568b
rc=0
### mint 28 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-25adbd
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-25adbd
rc=0
### mint 29 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-a3773d
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a3773d
rc=0
### mint 30 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-cb9dff
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-cb9dff
rc=0
### mint 31 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-3868df
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-3868df
rc=0
### mint 32 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-14cfa2
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-14cfa2
rc=0
### mint 33 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-dd64d4
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-dd64d4
rc=0
### mint 34 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-097656
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-097656
rc=0
### mint 35 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-8fd922
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-8fd922
rc=0
### mint 36 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-a901d9
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-a901d9
rc=0
### mint 37 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-6435b2
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-6435b2
rc=0
### mint 38 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-f7733e
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-f7733e
rc=0
### mint 39 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-3a1c9f
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-3a1c9f
rc=0
### mint 40 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-c8870b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-c8870b
rc=0
### mint 41 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-8e4d7d
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-8e4d7d
rc=0
### mint 42 (command: python3 -B tools/allocate_id.py --next run --area GFPN)
free run id for 'GFPN': RUN-GFPN-51e56b
  allocation: random 6-hex token (1 of 16,777,216 per namespace; no state scanned)
  VERIFY BEFORE USE: python3 tools/allocate_id.py --check RUN-GFPN-51e56b
rc=0
```

`--check` outputs, one per BARE id, at minting time:

```
### python3 -B tools/allocate_id.py --check RUN-GFPN-a61a10
identifier: RUN-GFPN-a61a10
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-30d3ee
identifier: RUN-GFPN-30d3ee
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-b0993b
identifier: RUN-GFPN-b0993b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-3e521f
identifier: RUN-GFPN-3e521f
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-4fc824
identifier: RUN-GFPN-4fc824
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-27c136
identifier: RUN-GFPN-27c136
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-fc29b6
identifier: RUN-GFPN-fc29b6
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-072f55
identifier: RUN-GFPN-072f55
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-a6ac23
identifier: RUN-GFPN-a6ac23
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-d48e01
identifier: RUN-GFPN-d48e01
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-9696d7
identifier: RUN-GFPN-9696d7
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-d6468a
identifier: RUN-GFPN-d6468a
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-98d454
identifier: RUN-GFPN-98d454
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-bda7a9
identifier: RUN-GFPN-bda7a9
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-1bcead
identifier: RUN-GFPN-1bcead
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-b76390
identifier: RUN-GFPN-b76390
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-aad5a9
identifier: RUN-GFPN-aad5a9
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-286cdb
identifier: RUN-GFPN-286cdb
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-4e37c2
identifier: RUN-GFPN-4e37c2
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-5cb274
identifier: RUN-GFPN-5cb274
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-1626b4
identifier: RUN-GFPN-1626b4
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-2d52fc
identifier: RUN-GFPN-2d52fc
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-f917a8
identifier: RUN-GFPN-f917a8
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-5fc8d7
identifier: RUN-GFPN-5fc8d7
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-8b0643
identifier: RUN-GFPN-8b0643
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-e2a2a5
identifier: RUN-GFPN-e2a2a5
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-3e568b
identifier: RUN-GFPN-3e568b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-25adbd
identifier: RUN-GFPN-25adbd
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-a3773d
identifier: RUN-GFPN-a3773d
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-cb9dff
identifier: RUN-GFPN-cb9dff
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-3868df
identifier: RUN-GFPN-3868df
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-14cfa2
identifier: RUN-GFPN-14cfa2
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-dd64d4
identifier: RUN-GFPN-dd64d4
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-097656
identifier: RUN-GFPN-097656
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-8fd922
identifier: RUN-GFPN-8fd922
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-a901d9
identifier: RUN-GFPN-a901d9
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-6435b2
identifier: RUN-GFPN-6435b2
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-f7733e
identifier: RUN-GFPN-f7733e
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-3a1c9f
identifier: RUN-GFPN-3a1c9f
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-c8870b
identifier: RUN-GFPN-c8870b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-8e4d7d
identifier: RUN-GFPN-8e4d7d
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
### python3 -B tools/allocate_id.py --check RUN-GFPN-51e56b
identifier: RUN-GFPN-51e56b
  well-formed: YES -- matches run pattern ^RUN-[A-Za-z0-9._-]+$
  occurrences across the union (26353 identifier-bearing paths scanned): 0

OK: well-formed and free across the union.
rc=0
```

## 15. Inference

- requested_policy: `executor-implementation`
- resolved_model_id: null (the dispatching session supplied none; none is invented)
- fallback_used: false
- bedrock_used: false
- The development notes record TASK-20260923-a681f9. No stage-R1 artifact carries TASK-20260923-cd932c
  or TASK-20260923-6c7f55 as its own task id. Those strings appear in this note only as the frozen
  values in sections 4 and 7. In the layer they appear only in the guard constant `FORBIDDEN_TASK_IDS`
  (`r1_common.py` line 69, split so the full string never occurs), and in the docstring (line 17) and
  one comment (line 61) of `r1_check_run.py`, which describe the rule.
