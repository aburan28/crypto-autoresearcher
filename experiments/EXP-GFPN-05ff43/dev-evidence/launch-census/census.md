# Launch-path census: EXP-GFPN-05ff43, TASK-20260924-1039eb

This is a zero-run, zero-solve static census. It computes the pre-declared readings CN-5, CN-1, CN-2 (i)-(ix), CN-3 and CN-4 of the DRAFT AMD-EXP-GFPN-05ff43-20260924-healthresolve (`pre_approval_readings`, draft lines 451-566).

**It records observations only.** It decides nothing and makes no approval recommendation. Nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT. Nothing here is a security statement.

- **Card:** `ledger/handoffs/TASK-20260924-1039eb.yaml`
- **Ordered by:** DEC-20260924-bea197 R-4.
- **Read with:** CORR-20260924-5b83a1 and CORR-20260924-36ce25.
- **Archival task:** TASK-20260924-c65bfb (snapshot, content_first).

## 0. Run record

**Machine-readable record:** `experiments/EXP-GFPN-05ff43/dev-evidence/launch-census/census.json`. It holds every site, call chain, citation, hash and the full launch-call list, 149 calls in all.

**Script:** `experiments/EXP-GFPN-05ff43/dev-evidence/launch-census/census_scan.py`, as run.

**Command (as run)**, from the repository root at 2026-09-24T03:19:31.19Z to 03:19:34.76Z, exit 0:

```
PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-GFPN-05ff43/dev-evidence/launch-census/census_scan.py \
  --out-dir experiments/EXP-GFPN-05ff43/dev-evidence/launch-census \
  --scratch /tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/census1039eb/run
```

- **Wall time:** about 3.6 s, from the two UTC stamps around the command. No resource meter was attached (deviation D-1).
- **stdout:**
  - `census.json written: .../launch-census/census.json`
  - `integrity pass: True; msolve sites: 7; citation failures: 0; guard blocks: 0; children at end: []`
- **stderr:** empty.

**Revision:** HEAD `bd66eb454ddc70fa51d0a130c6c48622d663928b`, the dispatcher's claim commit, on a clean tree. At the script's integrity phase, `git status --porcelain` listed only the untracked script itself. census.json records this.

**Environment:**
- Python 3.11.15, python-flint 0.9.0, numpy 2.4.6, PyYAML 6.0.1.
- Linux 6.18.44.
- The dispatcher's memory guard (DP-5) was not touched.

**Randomness:** none of its own. The only random streams exercised are the frozen `a1_health.draw` streams `random.Random('2026092001:v2a1:health:1073741831')` and `...:2` (CN-2 (vi)).

**Scratch outputs** (scratchpad only, not deliverables):
- `.../census1039eb/run/health-systems/`: the four .ms files and their round-trip copies.
- `.../census1039eb/run/stage-r2-bundle/`: the extracted dv1 members and MEMBERS.sha256.

### Inference

- requested_policy: `executor-implementation`
- resolved_model_id: `null`. None is invented. The dispatching session supplied no resolved binding.
- fallback_used: `false`
- bedrock_used: `false`
- Network: not used.

### Child processes started by this census

- **24 read-only `git` invocations**, all in the integrity phase: `rev-parse HEAD`, `status --porcelain`, `ls-files`, and `show HEAD:<path>` for the 10 tracked v1 files and the 11 tracked coordination scratch files. census.json lists every argv (`closing_checks.census_children_started`).
- **After the integrity phase**, an in-process guard replaced `os.fork`, `os.posix_spawn*`, `os.exec*`, `os.spawn*`, `os.system`, `os.popen` and `subprocess.Popen` with functions that raise. The guard recorded 0 attempts.
- **Child pids:**
  - before the permitted CN-2 (vi) imports: none;
  - after them: none;
  - at the end: none.
- **No msolve, gp, Sage, valgrind, builder or other solver child was started, not even `-h` or `-V`.** No run package was created. `runs/` still holds 50 directories.
- **Byte code:** no `.pyc` exists under implementation-v2/, -a1/, -r1/ or -r2/ (checked at the end).
- **Frozen files:** every file bound in the integrity phase was re-hashed at the end, and none had changed.

## 1. CN-5: integrity (LC-2), applied first

**Result: PASS.** All 64 checks are equal. The script checked integrity before reading anything else. After LC-2 (d) passed, it extracted the stage-r2 bundle members, and only into the scratchpad.

- (a) The healthresolve draft is `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d`. This equals `addendum_sha256.sha256`, and the path_sha256 entry, of the TASK-20260924-bc10a8 receipt.
- (b) The seedresolve draft is `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` and the solverevent draft is `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f`. Both match.
- (c) and (d): every file on disk under implementation-v2/ (12), -a1/ (10), -r1/ (13) and -r2/ (15) equals its receipt, file by file. No file is on disk without being bound, and no bound file is missing. The r2 note, both r2 plans, the stage-r2 bundle and both frozen plans also match.

Receipts used:

| receipt | sha256 | commit_sha | binding_mode | paths bound |
|---|---|---|---|---|
| `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-bc10a8/snapshot-receipt.json` | `5916bc5aada9d8fe684c97dc16593dbc1dda8f185b2596bff014ada387d03b43` | `a947b079f224956611811fbf4452ce2c2e7c92b9` | content_at_commit | 9 |
| `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-0fa03f/snapshot-receipt.json` | `ef5a0239d0171eaddf4c4720ea105010ad9c0617bb9f72bba199d232161b64b9` | `fb4597b2014b44a0c9528d48d3ab9997b46f038c` | phase A | 14 |
| `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-4ff597/snapshot-receipt.json` | `400d04e5ee89a685df02e4349d09712aa20b1466e5db05365d11bc58434267f3` | `36c3b0d2e05878a8df1209b5048f8ce14515c27f` | phase A | 12 |
| `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-53a47d/preservation-receipt.json` | `cc5d5f9e1df1b9086e94cfa920cc8c3b81bd7e8d9d51b61f4a7433433aaf5adc` | `02d7e6ce40faf2426f92b252bfe637bdb755340e` | content_first | 17 |
| `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-5ca2a5/preservation-receipt.json` | `a19825c8efa744ba04caffd9701d094508e064ed8bd0e0f4e4ac82cbae038bf8` | `22d0085aaee61c7c32a075a78bd46221f606f72e` | content_first | 20 |

All checks with full hashes:

| # | check | path | expected sha256 (source) | actual sha256 | equal |
|---|---|---|---|---|---|
| 1 | (a) healthresolve draft == TASK-20260924-bc10a8 addendum_sha256 | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_healthresolve.yaml` | `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d` (TASK-20260924-bc10a8) | `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d` | True |
| 2 | (a') healthresolve draft == TASK-20260924-bc10a8 path_sha256 | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_healthresolve.yaml` | `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d` (TASK-20260924-bc10a8) | `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d` | True |
| 3 | (b) seedresolve draft | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_seedresolve.yaml` | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` (card LC-2 (b)) | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` | True |
| 4 | (b) solverevent draft | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_solverevent.yaml` | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` (card LC-2 (b)) | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` | True |
| 5 | (c) experiments/EXP-GFPN-05ff43/implementation-v2/ file list equals the 0fa03f_phaseA receipt | `experiments/EXP-GFPN-05ff43/implementation-v2/` | file list: 12 bound | 12 on disk; not bound none; missing none | True |
| 6 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_arms.py` | `b703159955765811f51b08d0e1a677f47907b2d4e655f4821a78da03be665049` (TASK-20260923-0fa03f) | `b703159955765811f51b08d0e1a677f47907b2d4e655f4821a78da03be665049` | True |
| 7 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py` | `ed813df7760be9d9289a6643ba7be95cf9be905e6ba0835d476b56ea551d2e25` (TASK-20260923-0fa03f) | `ed813df7760be9d9289a6643ba7be95cf9be905e6ba0835d476b56ea551d2e25` | True |
| 8 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py` | `6ff43cae46e2ea200e1765974daa316bd0b75719169189c5c584bd8576557bf9` (TASK-20260923-0fa03f) | `6ff43cae46e2ea200e1765974daa316bd0b75719169189c5c584bd8576557bf9` | True |
| 9 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py` | `c064144c7d70d84727cd286baf34df8160eca2b3b5e469ea29556446289b6592` (TASK-20260923-0fa03f) | `c064144c7d70d84727cd286baf34df8160eca2b3b5e469ea29556446289b6592` | True |
| 10 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_driver.py` | `0d22a082c967500f28d0aabdce1b0cdf125cf5a3109727045e6cf55407a20098` (TASK-20260923-0fa03f) | `0d22a082c967500f28d0aabdce1b0cdf125cf5a3109727045e6cf55407a20098` | True |
| 11 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_field.py` | `056f4ebbcc2c96176fde2c29e56cf8e8b69fa75749f437d05a958d8873be114f` (TASK-20260923-0fa03f) | `056f4ebbcc2c96176fde2c29e56cf8e8b69fa75749f437d05a958d8873be114f` | True |
| 12 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_lift.py` | `6a9a43a1ee00394db34d0ecec16a3a3a75a6d71bfe88c2f6028638c01a3993f3` (TASK-20260923-0fa03f) | `6a9a43a1ee00394db34d0ecec16a3a3a75a6d71bfe88c2f6028638c01a3993f3` | True |
| 13 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_make_trial_plan.py` | `b1ea52c51314ce7b64a6d26291f338a0ed7cae85ff608f9b34b04a1bcc9b20d8` (TASK-20260923-0fa03f) | `b1ea52c51314ce7b64a6d26291f338a0ed7cae85ff608f9b34b04a1bcc9b20d8` | True |
| 14 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py` | `115008eb91b3bf4b5f6577d671ea3af612c6ecbe1388d41e269af069bfc368ab` (TASK-20260923-0fa03f) | `115008eb91b3bf4b5f6577d671ea3af612c6ecbe1388d41e269af069bfc368ab` | True |
| 15 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_scoring.py` | `3142c154cf1263d12c18fdf87b72d15b229a52c6b355983a432a0cb500c85e59` (TASK-20260923-0fa03f) | `3142c154cf1263d12c18fdf87b72d15b229a52c6b355983a432a0cb500c85e59` | True |
| 16 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py` | `0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d` (TASK-20260923-0fa03f) | `0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d` | True |
| 17 | (c) v2 | `experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py` | `b5dcd80a74354708ce131bc83ef30b84c21481ad9831f18da70aad0c12856712` (TASK-20260923-0fa03f) | `b5dcd80a74354708ce131bc83ef30b84c21481ad9831f18da70aad0c12856712` | True |
| 18 | (c) experiments/EXP-GFPN-05ff43/implementation-v2-a1/ file list equals the 4ff597_phaseA receipt | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/` | file list: 10 bound | 10 on disk; not bound none; missing none | True |
| 19 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py` | `516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f` (TASK-20260923-4ff597) | `516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f` | True |
| 20 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_common.py` | `f347eebafa51eace211012f780c8425a2f4d6917f61370c7c2f20a1c62a9185b` (TASK-20260923-4ff597) | `f347eebafa51eace211012f780c8425a2f4d6917f61370c7c2f20a1c62a9185b` | True |
| 21 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py` | `d008405054f1afb1ff7b885e03bbcac3aec0878e0877bc46d4229e426a72edd6` (TASK-20260923-4ff597) | `d008405054f1afb1ff7b885e03bbcac3aec0878e0877bc46d4229e426a72edd6` | True |
| 22 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py` | `0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde` (TASK-20260923-4ff597) | `0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde` | True |
| 23 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py` | `749237a6cfc15eeb235824dcf5e28e6733ee099df56daad3f996ae028650e5b7` (TASK-20260923-4ff597) | `749237a6cfc15eeb235824dcf5e28e6733ee099df56daad3f996ae028650e5b7` | True |
| 24 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_make_trial_plan.py` | `dc1c14110a015a278d71f06fb4593e13a7ca06c79746cb5ff30c5bf702933104` (TASK-20260923-4ff597) | `dc1c14110a015a278d71f06fb4593e13a7ca06c79746cb5ff30c5bf702933104` | True |
| 25 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py` | `dafe748d9a1e923c106a5fa0cfcdd7d622fbb80cb23e1099d5fc6064be4e7293` (TASK-20260923-4ff597) | `dafe748d9a1e923c106a5fa0cfcdd7d622fbb80cb23e1099d5fc6064be4e7293` | True |
| 26 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_reading.py` | `b968838ef59035d15d9d71e74ac9e4dae8f903e0780737f04fb3497bc5a71ada` (TASK-20260923-4ff597) | `b968838ef59035d15d9d71e74ac9e4dae8f903e0780737f04fb3497bc5a71ada` | True |
| 27 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py` | `03bd5c59ebbe27b6b6831ac1da9552b9a7d075fd68c472ae153eaa60a02ac81c` (TASK-20260923-4ff597) | `03bd5c59ebbe27b6b6831ac1da9552b9a7d075fd68c472ae153eaa60a02ac81c` | True |
| 28 | (c) a1 | `experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_toy.py` | `58afe374d4ecd84b2f5e731a5f71ebbea7fb940728805354d128db7336b516d7` (TASK-20260923-4ff597) | `58afe374d4ecd84b2f5e731a5f71ebbea7fb940728805354d128db7336b516d7` | True |
| 29 | (c) experiments/EXP-GFPN-05ff43/implementation-v2-r1/ file list equals the 53a47d receipt | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/` | file list: 13 bound | 13 on disk; not bound none; missing none | True |
| 30 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/minted-run-ids.txt` | `b065914e5120def71c8f112d0b1eb35d869a6f23a33ef2635f40ca436bbb7b28` (TASK-20260923-53a47d) | `b065914e5120def71c8f112d0b1eb35d869a6f23a33ef2635f40ca436bbb7b28` | True |
| 31 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_check_run.py` | `87d23924a3f1c317eaf1773683b365631a538d22836da698829a6517052812d6` (TASK-20260923-53a47d) | `87d23924a3f1c317eaf1773683b365631a538d22836da698829a6517052812d6` | True |
| 32 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_common.py` | `ea3ea5da076a544cca3b4c4fe1fbc72da129ed734d405336b871879a6ee107c0` (TASK-20260923-53a47d) | `ea3ea5da076a544cca3b4c4fe1fbc72da129ed734d405336b871879a6ee107c0` | True |
| 33 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_devchecks.py` | `b777a27b139ff6059be7bd01987638765799e3ecd5f8b1601428f60c480789f4` (TASK-20260923-53a47d) | `b777a27b139ff6059be7bd01987638765799e3ecd5f8b1601428f60c480789f4` | True |
| 34 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_devchecks_more.py` | `99e1f144adb95a30d8290065a948200f90864263916db76f1c6a1ccb843b8c00` (TASK-20260923-53a47d) | `99e1f144adb95a30d8290065a948200f90864263916db76f1c6a1ccb843b8c00` | True |
| 35 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_dv6.py` | `d3eac6bfa5a13a1e4beb62ec2246766d09790d6ef8962a6e39d9748d734c4507` (TASK-20260923-53a47d) | `d3eac6bfa5a13a1e4beb62ec2246766d09790d6ef8962a6e39d9748d734c4507` | True |
| 36 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_entry_a1.py` | `f404a2d96985b84dda78340f29d5792c97499217acf28d65d3424b3864c971fd` (TASK-20260923-53a47d) | `f404a2d96985b84dda78340f29d5792c97499217acf28d65d3424b3864c971fd` | True |
| 37 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_entry_v2.py` | `82594a7b3830e79acc83514966b87525e1777a0bbf690b2748b5499901e907b4` (TASK-20260923-53a47d) | `82594a7b3830e79acc83514966b87525e1777a0bbf690b2748b5499901e907b4` | True |
| 38 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_make_plans.py` | `e58720cd1ee8f876fd97a5e19bcb49dab4cbac30f6bb31eb37fcf7fbf73f2e0e` (TASK-20260923-53a47d) | `e58720cd1ee8f876fd97a5e19bcb49dab4cbac30f6bb31eb37fcf7fbf73f2e0e` | True |
| 39 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_reg1.py` | `1b4e4c880f829e8f04915c6a55b9274c9391c6dea701880f63671963db7d1d26` (TASK-20260923-53a47d) | `1b4e4c880f829e8f04915c6a55b9274c9391c6dea701880f63671963db7d1d26` | True |
| 40 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_run_wrapper.py` | `b3d00e1ada7af2e39331bab0013f564be591bda2228b7ebe51944436734fb9d6` (TASK-20260923-53a47d) | `b3d00e1ada7af2e39331bab0013f564be591bda2228b7ebe51944436734fb9d6` | True |
| 41 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/r1_toy.py` | `e72582251725b9dcc355264521903b2ded2a2884d8c4b73a5243c29834fafc82` (TASK-20260923-53a47d) | `e72582251725b9dcc355264521903b2ded2a2884d8c4b73a5243c29834fafc82` | True |
| 42 | (c) r1 | `experiments/EXP-GFPN-05ff43/implementation-v2-r1/reg1-exclusion-list.json` | `4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c` (TASK-20260923-53a47d) | `4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c` | True |
| 43 | (d) experiments/EXP-GFPN-05ff43/implementation-v2-r2/ file list equals the 5ca2a5 receipt | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/` | file list: 15 bound | 15 on disk; not bound none; missing none | True |
| 44 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/minted-run-ids.txt` | `5ddf35148a3dfa73dc82bde80f6cb0c6dd114ea22751c42d19af6436156ff1a0` (TASK-20260924-5ca2a5) | `5ddf35148a3dfa73dc82bde80f6cb0c6dd114ea22751c42d19af6436156ff1a0` | True |
| 45 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_accounting.py` | `4f8c3a72dcf602bd79a5bf1283bf970a3c6c56511cc6f086fff25f60c1416378` (TASK-20260924-5ca2a5) | `4f8c3a72dcf602bd79a5bf1283bf970a3c6c56511cc6f086fff25f60c1416378` | True |
| 46 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_check_run.py` | `2fc5c141b18e8150654fb1ad018da0014c9b91a9883a6c3a76f845df3f665b9c` (TASK-20260924-5ca2a5) | `2fc5c141b18e8150654fb1ad018da0014c9b91a9883a6c3a76f845df3f665b9c` | True |
| 47 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_common.py` | `6b34cf03bb90d9d96d795f9530f9b28b53e29abbcf472e9fed3d85aa34647872` (TASK-20260924-5ca2a5) | `6b34cf03bb90d9d96d795f9530f9b28b53e29abbcf472e9fed3d85aa34647872` | True |
| 48 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_devchecks.py` | `f16470ead2437e60107b4fe70b29f2e67b635c7cd557ab21712474ea74d916bc` (TASK-20260924-5ca2a5) | `f16470ead2437e60107b4fe70b29f2e67b635c7cd557ab21712474ea74d916bc` | True |
| 49 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_devchecks_more.py` | `be7b332df0fbcd881846ff03bf6ae27c3f248db855ced0db88b119bab7e59bab` (TASK-20260924-5ca2a5) | `be7b332df0fbcd881846ff03bf6ae27c3f248db855ced0db88b119bab7e59bab` | True |
| 50 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_dv12.py` | `a0888082cb6bc98cf84b859b51d0cf84ea09919ed11d6e9affff45e0674a6d91` (TASK-20260924-5ca2a5) | `a0888082cb6bc98cf84b859b51d0cf84ea09919ed11d6e9affff45e0674a6d91` | True |
| 51 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_dv6.py` | `8ed298d5303169c506acd6eebdf18fdf30ba82beb04df3293e442e25c4cf19dc` (TASK-20260924-5ca2a5) | `8ed298d5303169c506acd6eebdf18fdf30ba82beb04df3293e442e25c4cf19dc` | True |
| 52 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_entry_a1.py` | `5d2c6d93f3b56eaaf788149f8671407ebcf6d4a483247b9447f91a50b0e058c7` (TASK-20260924-5ca2a5) | `5d2c6d93f3b56eaaf788149f8671407ebcf6d4a483247b9447f91a50b0e058c7` | True |
| 53 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_entry_v2.py` | `ea157d9479f8e6968116abd09326274d62cbfa6eedcf1a40b49e3aa5552c08a7` (TASK-20260924-5ca2a5) | `ea157d9479f8e6968116abd09326274d62cbfa6eedcf1a40b49e3aa5552c08a7` | True |
| 54 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_make_plans.py` | `78c6d85c6be925fbf32f5da9a53a2df671ac4d3139caa779b84225f9f2bfb17a` (TASK-20260924-5ca2a5) | `78c6d85c6be925fbf32f5da9a53a2df671ac4d3139caa779b84225f9f2bfb17a` | True |
| 55 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_reg1.py` | `2bf7f5d6108b7965b747e0de015e1a5fcab76888ea0b9c0415522d49a8d7bd3d` (TASK-20260924-5ca2a5) | `2bf7f5d6108b7965b747e0de015e1a5fcab76888ea0b9c0415522d49a8d7bd3d` | True |
| 56 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_resolve.py` | `ee2b755c242cb681e03f8f69ea94389dcb97977459d7da2783bad872e9107438` (TASK-20260924-5ca2a5) | `ee2b755c242cb681e03f8f69ea94389dcb97977459d7da2783bad872e9107438` | True |
| 57 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/r2_run_wrapper.py` | `bccf6b2fff50aa8d24899d0899a8c009f9c20104562152eb1c08d16b0f3bfb47` (TASK-20260924-5ca2a5) | `bccf6b2fff50aa8d24899d0899a8c009f9c20104562152eb1c08d16b0f3bfb47` | True |
| 58 | (d) r2 | `experiments/EXP-GFPN-05ff43/implementation-v2-r2/reg1-exclusion-list.json` | `4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c` (TASK-20260924-5ca2a5) | `4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c` | True |
| 59 | (d) r2 output | `experiments/EXP-GFPN-05ff43/implementation-v2-r2.md` | `d17f9abf9fc7ea05ffcb9112af0af6cfd9a56fe931449a9632a4a1e8f3293184` (TASK-20260924-5ca2a5) | `d17f9abf9fc7ea05ffcb9112af0af6cfd9a56fe931449a9632a4a1e8f3293184` | True |
| 60 | (d) r2 output | `experiments/EXP-GFPN-05ff43/trial-plan-v2-r2.json` | `d3bf5d74884c870c1d4996085651c3057322d6153875246bedd96c2f542b75ff` (TASK-20260924-5ca2a5) | `d3bf5d74884c870c1d4996085651c3057322d6153875246bedd96c2f542b75ff` | True |
| 61 | (d) r2 output | `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r2.json` | `121202cb9ba971218d5491c4553f29fb872dfa225903dad620e3db29e27cb1e5` (TASK-20260924-5ca2a5) | `121202cb9ba971218d5491c4553f29fb872dfa225903dad620e3db29e27cb1e5` | True |
| 62 | (d) r2 output | `experiments/EXP-GFPN-05ff43/dev-evidence/stage-r2-dv/stage-r2-dv-evidence.tar.gz` | `307c98f98505094b2073bdc7090b68d21eafa9f6bd3060dcb2cec2d75127b508` (TASK-20260924-5ca2a5) | `307c98f98505094b2073bdc7090b68d21eafa9f6bd3060dcb2cec2d75127b508` | True |
| 63 | (c) frozen plan | `experiments/EXP-GFPN-05ff43/trial-plan-v2.json` | `16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16` (TASK-20260923-0fa03f) | `16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16` | True |
| 64 | (c) frozen plan | `experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json` | `2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6` (TASK-20260923-4ff597) | `2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6` | True |

The following inputs are not bound by the four receipts. They are recorded with their sha256 at HEAD and every archive under `coordination/goals/GOAL-GFPN-380702/archives/` that binds them.

| path | sha256 on disk | tracked | sha256 at HEAD equal | archive(s) binding it |
|---|---|---|---|---|
| `experiments/EXP-GFPN-05ff43/implementation/__pycache__/gfpn5_core.cpython-311.pyc` | `6d2510b9bedf7f051e4a0bd66ec2e583f90b426864b9a658984ef0f15fa3a367` | False | None | none |
| `experiments/EXP-GFPN-05ff43/implementation/__pycache__/pdp_cell.cpython-311.pyc` | `cc9aefc2b24308472c638ee430a53717dac669f9faad0aaa89bb0abe0ea56576` | False | None | none |
| `experiments/EXP-GFPN-05ff43/implementation/__pycache__/pdp_common.cpython-311.pyc` | `6ad18e0f39463342e1545171e114e8e5eef343b142ec1644884999c296a49b61` | False | None | none |
| `experiments/EXP-GFPN-05ff43/implementation/__pycache__/symmetrize.cpython-311.pyc` | `c7d22de8c9069def87a3ea1bbc8e62249a0fdaa72bf2db0aaca84ba02e2e5f64` | False | None | none |
| `experiments/EXP-GFPN-05ff43/implementation/__pycache__/verify_independent.cpython-311.pyc` | `3ee027b5d4e69b943db01092c427c88bfbe2ef4e5eb65f8812929f4f101d75bb` | False | None | none |
| `experiments/EXP-GFPN-05ff43/implementation/check_run.py` | `db2f6d93918ad03d10d16d3835294ce38afbeb70a8a84e188dc3716d4f10aea8` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/close_terminated_run.py` | `38433f238f5b64671c88147bf5d597d7deeb737a902ea6d484707e6d87f1578c` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/gfpn5_core.py` | `4523d05fbbbb95ca844cc8d1888300d91d2ad4a8e1f4bce5d36a76694faae1ed` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/ladder.json` | `7e42961d5bd3de9c5833c0cf5bbb53120c113a4ee2d55371e6eec84379cb327c` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/ladder_select.py` | `fb2fc3f46d8adf97220b7601ce853eab9e3b127af5c4736167e8cc3f7f8c0f73` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/pdp_cell.py` | `ffc8d9f3a8a2afda28bcfa14555074414b4473e8650fa8669ea4e16c21e4cd6f` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/pdp_common.py` | `f3afa290c468a6ed1d795085e763c5066177745c768b58c7b6b773bd1c1e8b21` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/run_wrapper.py` | `5938941d7a0e4f76e19933e85818799185fdf1f687378b33f8dfd8347dd95c70` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/symmetrize.py` | `b71daad03aa8cbf9586aebdc6ce19cb8ed338f380345bdb29084e0473729b309` | True | True | TASK-20260921-98561a (equal) |
| `experiments/EXP-GFPN-05ff43/implementation/verify_independent.py` | `bb8310c68afe271ca1e9f0357a185c2b293398e914267aac00565243f21d1267` | True | True | TASK-20260921-98561a (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py` | `3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv4_failed_launch.log` | `044ef208214d6e847b277f45745bede5fa3386d5572d29a3f09ae13b3bcd387a` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv5_stdout.log` | `61e7f9cc21dfc5f71c4da338ff88a14acf6ae5e832d23433348cc9fbb40ca95b` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv7_failed_stderr.log` | `e66bf32d680f3609808df1a88048071a8d2bfcf3d83137ef4e27e62783f3aa2a` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv7_failed_stdout.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv8_stderr.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/inv8_stdout.log` | `5faf1f46534e94f4f16d7b279eae764246f6c2749abedcce000ed7bc99016372` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue.py` | `1776b20d994231a030ebe35b197256eecf81b0a69df4e69cf01a86079d004b64` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_m4.py` | `b253a973aa97140923705cec43ba752aa7c0216f1d06e9315b75b372c7288498` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n3.json` | `22550c2f4ede32a41d7b8134f2c72c04121d20065eacd6604640b0ef0e8a81ba` | True | True | TASK-20260923-3b12c2 (equal) |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/scratch/k5k7/square_analogue_n4.json` | `e3bc6d120a52a898fd84e47efe54f727f20e2013c906522cd41a73303ae595a2` | True | True | TASK-20260923-3b12c2 (equal) |

**Pre-existing byte code in v1.** `implementation/__pycache__/` holds five git-ignored `.pyc` files, dated 2026-09-21 and 2026-09-23. They were not written by this census. No archive binds them. Their mtimes are recorded in census.json and were unchanged at the end.

**Stage-r2 bundle.**
- It has 2304 members; MEMBERS.sha256 is `a785b5e45312c5eec9b84683bac969b6c99262b6ed30d3487b8285ffe7c68675`.
- The census extracted only the 4 dv1 members and MEMBERS.sha256.
- Each dv1 member's sha256 equals its MEMBERS.sha256 entry:
  - `dv1_static.json`: `62d0664ff40fb11b18089bca7d177f5b3208e68ac88c7098eea667a4f7697edb`
  - `sage_pari_probe.py`: `4cda650b5587d56b17c68858fd2e146853507c4c43f84c57f61fa45761c7cb13`
  - `sage_pari_probe.stdout`: `a38e8466471394c7b5ef68b4bfe4eb2b9aa67793eed2f0b2c2913c1161518b88`
  - `sage_pari_probe.stderr`: empty, `e3b0c442...b855`

## 2. CN-1: msolve launch census

### Method

**Scope.** The census parsed every `.py` file with `ast`: 58 modules and 831 functions in total. That covers the five trees plus every file they execute or import from outside them:
- `k4a_anchor_system.py`, the Sage comparator, which `v2_driver.cmd_anchor_identity` executes at line 650;
- the `k5k7/` scratch, whose two `.py` files are scanned. v2_common reads only the two JSON files there, as data.

**Imports that resolve outside the trees** are stdlib and third-party only: flint, numpy, yaml, cypari2, sage.all, cysignals, scipy.stats. **No v2, a1, r1 or r2 module imports a v1 module.** v1 contributes `ladder.json` as data only.

**Launch primitives** detected: `os.fork`/`exec*`/`spawn*`/`system`/`popen`/`posix_spawn`, `subprocess.*`, `pty.spawn`, `multiprocessing.Process` and `asyncio` subprocess calls. Launcher functions that forward a whole argv or shell string were then inferred to a fixpoint: `run_child`, `_run_child_locked`, `callgrind_instructions` (with a valgrind prefix), `sh`, `git`, and v1 `run_msolve` (with an msolve prefix).

**Commands.** The driver_args commands of both r2 plans equal the frozen plans' commands package by package, as census.json `commands` shows:
- 31 packages for v2: `fixture`, `anchor-identity`, `controls`, `fixture4`, `build`, `cells`, `aggregate`;
- 11 packages for a1: `controls-a1`, `build`, `cells`, `aggregate-a1`.

Differences sit only in run ids inside `--prior-run`, `--runs`, `--a1-runs`, `--v2-runs` and `--v2-aggregate`. The contingency packages replay these same commands (r2_run_wrapper.py 387-391).

**Reachability** follows the static call graph from each command's dispatch function, under the r2 entries' import order. The roots are the entry's `<module>` and `main`, plus the dispatch function; the edge into the driver's `main()` is cut.

The graph follows calls through:
- module attributes (`H.run`, `D.solve`, `V.run_child`, `P.curve_facts`, `C.host_record`);
- `from X import`, including `*`;
- module-level aliases (`log = D.log`) and `self.` methods;
- function references (the dict dispatch);
- import-time code of every imported module. `if __name__ == "__main__":` blocks are excluded, because they do not run on import.

**SE-3 binding.** SE-3's in-process binding is added explicitly (`r2_resolve.install`, r2_resolve.py 298; r2_entry_v2.py 46; r2_entry_a1.py 64). Every call of `v2_driver.solve` goes to `r2_resolve.solve`, which reaches the original through `_call_original` (line 224).

**Conservative edges.**
- An unresolved `obj.method()` is linked to every class method of that name in the caller's module or its imports. This over-includes; census.json lists those edges.
- A name used only as an attribute base, as an `is`/`==` operand, as the first argument of `getattr`/`hasattr`, or as the value of an attribute assignment is not a call edge.
- The only callable rebound in reachable code is `v2_driver.solve` (r2_resolve.py 298). `getattr` is used only for identity read-backs, at r2_resolve.py 294-326 and r2_common.py 310.

**Generated-code strings.** String literals that contain generated Python (the development shims) were parsed too:
- r1_toy.py 218 and 280;
- r2_dv12.py 81.

Their only launch-like calls wrap the frozen `run_child` (`rc(argv, ...)`) or run an entry via `runpy`. They live in development harnesses that no delivered entry reaches.

### Every msolve launch site (definition: argv contains `v2_solver.MSOLVE`, `/usr/bin/msolve` or a `msolve_argv` argv, directly or under valgrind)

| # | site (file:line) | enclosing function | argv construction | program launched | launch chain to exec | reachable | commands reaching it (static) |
|---|---|---|---|---|---|---|---|
| 1 | `implementation/run_wrapper.py:36` | `environment` | `'msolve -h 2>&1 / head -1'` | shell: msolve / head | run_wrapper.py:36 -> run_wrapper.py:23 | False | none |
| 2 | `implementation/symmetrize.py:399` | `run_msolve` | `cmd` | /usr/bin/msolve (fixed here; arguments forwarded from parameter extra) | symmetrize.py:399 | False | none |
| 3 | `implementation-v2/v2_driver.py:209` | `solve` | `V.msolve_argv(inp, cg_out, threads=1, gb_only=gb_only)` | valgrind (callgrind) -> /usr/bin/msolve (v2_solver.msolve_argv) | v2_driver.py:209 -> v2_solver.py:517 -> v2_solver.py:171 -> v2_solver.py:205 | True | v2-r2 `anchor-identity`, v2-r2 `cells`, v2-r2 `controls`, v2-r2 `fixture`, v2-r2 `fixture4`, v2-a1-r2 `cells`, v2-a1-r2 `controls-a1` |
| 4 | `implementation-v2/v2_driver.py:166` | `solve` | `argv` | /usr/bin/msolve (v2_solver.msolve_argv) | v2_driver.py:166 -> v2_solver.py:171 -> v2_solver.py:205 | True | v2-r2 `anchor-identity`, v2-r2 `cells`, v2-r2 `controls`, v2-r2 `fixture`, v2-r2 `fixture4`, v2-a1-r2 `cells`, v2-a1-r2 `controls-a1` |
| 5 | `implementation-v2-a1/a1_health.py:147` | `run_system` | `argv` | /usr/bin/msolve (v2_solver.msolve_argv) | a1_health.py:147 -> v2_solver.py:171 -> v2_solver.py:205 | True | v2-a1-r2 `controls-a1` |
| 6 | `TASK-20260923-404bf9/scratch/k5k7/square_analogue.py:157` | `ideal_degree` | `['/usr/bin/msolve', '-v', '2', '-t', '1', '-f', fn, '-o', fn + '.out']` | /usr/bin/msolve | square_analogue.py:157 | False | none |
| 7 | `TASK-20260923-404bf9/scratch/k5k7/square_analogue_m4.py:26` | `ideal_degree` | `['/usr/bin/msolve', '-v', '2', '-t', '4', '-f', fn, '-o', fn + '.out']` | /usr/bin/msolve | square_analogue_m4.py:26 | False | none |

Call chains for the reachable sites (static; `@n` is the line of the edge):

- `v2_driver.py:209`:
  - v2-r2 anchor-identity: v2_driver:cmd_anchor_identity > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @711] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 cells: v2_driver:cmd_cells > v2_driver:_run_cell [call @1090] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @1174] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 controls: v2_driver:cmd_controls > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @841] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 fixture: v2_driver:cmd_fixture > v2_driver:fixture_core [call @279] > v2_driver:fixture_core.run_target [call @411] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @358] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 fixture4: v2_driver:cmd_fixture4 > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @565] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-a1-r2 cells: a1_driver:cmd_cells > v2_driver:cmd_cells [call @234] > v2_driver:_run_cell [call @1090] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @1174] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-a1-r2 controls-a1: a1_driver:cmd_controls_a1 > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @166] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
- `v2_driver.py:166`:
  - v2-r2 anchor-identity: v2_driver:cmd_anchor_identity > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @711] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 cells: v2_driver:cmd_cells > v2_driver:_run_cell [call @1090] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @1174] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 controls: v2_driver:cmd_controls > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @841] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 fixture: v2_driver:cmd_fixture > v2_driver:fixture_core [call @279] > v2_driver:fixture_core.run_target [call @411] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @358] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-r2 fixture4: v2_driver:cmd_fixture4 > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @565] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-a1-r2 cells: a1_driver:cmd_cells > v2_driver:cmd_cells [call @234] > v2_driver:_run_cell [call @1090] > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @1174] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
  - v2-a1-r2 controls-a1: a1_driver:cmd_controls_a1 > r2_resolve:solve [runtime binding (SE-3: v2_driver.solve is the r2 wrapper) @166] > r2_resolve:_call_original [call @224] > v2_driver:solve [runtime binding @None]
- `a1_health.py:147`:
  - v2-a1-r2 controls-a1: a1_driver:cmd_controls_a1 > a1_health:run [call @129] > a1_health:run_system [call @244]

Callers of each launch function:

- `run_wrapper.py:36` callers: run_wrapper.py:88 (`run_wrapper:main`)
- `symmetrize.py:399` callers: pdp_cell.py:135 (`pdp_cell:cmd_validate`), pdp_cell.py:113 (`pdp_cell:cmd_validate`), pdp_cell.py:112 (`pdp_cell:cmd_validate`), pdp_cell.py:233 (`pdp_cell:cmd_anchor`), pdp_cell.py:355 (`pdp_cell:cmd_cell`), pdp_cell.py:517 (`pdp_cell:cmd_raw`)
- `v2_driver.py:209` callers: v2_driver.py:358 (`v2_driver:fixture_core.run_target`), v2_driver.py:565 (`v2_driver:cmd_fixture4`), v2_driver.py:711 (`v2_driver:cmd_anchor_identity`), v2_driver.py:693 (`v2_driver:cmd_anchor_identity`), v2_driver.py:841 (`v2_driver:cmd_controls`), v2_driver.py:787 (`v2_driver:cmd_controls`), v2_driver.py:786 (`v2_driver:cmd_controls`), v2_driver.py:1174 (`v2_driver:_run_cell`), a1_driver.py:166 (`a1_driver:cmd_controls_a1`)
- `v2_driver.py:166` callers: v2_driver.py:358 (`v2_driver:fixture_core.run_target`), v2_driver.py:565 (`v2_driver:cmd_fixture4`), v2_driver.py:711 (`v2_driver:cmd_anchor_identity`), v2_driver.py:693 (`v2_driver:cmd_anchor_identity`), v2_driver.py:841 (`v2_driver:cmd_controls`), v2_driver.py:787 (`v2_driver:cmd_controls`), v2_driver.py:786 (`v2_driver:cmd_controls`), v2_driver.py:1174 (`v2_driver:_run_cell`), a1_driver.py:166 (`a1_driver:cmd_controls_a1`)
- `a1_health.py:147` callers: a1_health.py:244 (`a1_health:run`), a1_health.py:241 (`a1_health:run`), a1_health.py:237 (`a1_health:run`), a1_health.py:234 (`a1_health:run`)
- `square_analogue.py:157` callers: square_analogue.py:249 (`square_analogue:run_prime`), square_analogue.py:221 (`square_analogue:run_prime`), square_analogue.py:210 (`square_analogue:run_prime`), square_analogue.py:205 (`square_analogue:run_prime`)
- `square_analogue_m4.py:26` callers: square_analogue_m4.py:120 (`square_analogue_m4:run`), square_analogue_m4.py:96 (`square_analogue_m4:run`), square_analogue_m4.py:87 (`square_analogue_m4:run`)

**Unresolved argv (manual reading).**
- `implementation/run_wrapper.py:98` runs the operator's command after `--` (`cmd = argv[3:]`, line 82). Whether that command is msolve cannot be determined statically. It is v1 and not reachable.
- No other launch call has an unresolved program.

**Argument-level note.** This is not the definition; it is recorded to support the reading.
- Static reachability counts the callgrind child wherever `solve()` is reachable.
- Only two call sites pass a `callgrind_timeout`:
  - `fixture_core` line 358, with `callgrind_timeout_s.m3`;
  - `_run_cell` lines 1174-1175, on target 0 of an m <= 4 cell.
- It runs only after an ok outcome (line 207).
- So the callgrind child actually runs in `fixture` and in `cells` with m = 4, in both plans. `anchor-identity`, `controls`, `fixture4` and `controls-a1` pass no callgrind_timeout.

### Classification of each site (recorded readings; every cited line re-checked by the script, 152 citations, 0 failures)

1. **`v2_driver.py:165-166` (solve): CLASSIFIED.**
   - Its output enters:
     - `parse_msolve_log` (176);
     - `parse_msolve_param` (193);
     - `V.classify_solve` (197);
     - the recorded outcome and reason (198);
     - D and solutions (204).
   - The `gb_only=True` calls in anchor-identity (693, 711) return at line 188, but their F4 trace, recorded at line 177, feeds the anchor trace-identity gate.
   - Under both r2 entries it runs only inside `r2_resolve.solve` (SE-3). gb_only is passed straight through (r2_resolve.py 208-212).
2. **`a1_health.py:144/147` (run_system): CLASSIFIED.**
   - Its output enters:
     - `parse_msolve_log` (163);
     - `parse_msolve_param` (168);
     - `V.classify_solve` (182);
     - `v2_outcome_class` and `v2_outcome_reason` (185-186);
     - `checks` and `pass` (188-199);
     - `pattern_pass` (245);
     - a1_driver check (d) (130), and so controls_a1 `gate_pass` (187, 208).
   - The r2 layer does not wrap it: r2_entry_a1.py replaces only `v2_driver.solve` (lines 24, 64).
3. **`v2_driver.py:209` -> `v2_solver.py:516-517` (callgrind: valgrind running the same msolve argv): see the observation below.**
   - It enters neither `classify_solve`, the target's outcome, reason, D or solutions (all set before line 207), nor any frozen v2 or v2-a1 check or gate.
   - Its record `res["instructions_callgrind"]` holds:
     - cost fields: `instructions_user`, `f4_core_inclusive_Ir` and `child.wall_seconds`;
     - non-cost fields: `child.outcome`, `child.returncode`, `child.rlimit_as_child_getrlimit`, `child.peak_vm_bytes` (a host reading), `method`, `label`, `f4_core_function`, `f4_core_note`, and `reason` when the child is not ok (v2_solver.py 519-547).
   - Those are copied into the fixture and cell target rows (v2_driver.py 360, 1180).
4. **v1 `symmetrize.py:392/399` (run_msolve): CLASSIFIED within v1.** Its output enters `parse_msolve_log` (435) and `outcome` (448). Callers are listed above, all in v1 `pdp_cell.py`. It is **not reachable.**
5. **v1 `run_wrapper.py:36`, `sh("msolve -h 2>&1 | head -1")`.** It is a version-string launch. Its stdout enters the recorded field `environment.json` `software.msolve`, which is not a cost measurement. It enters no classifier, check, gate or outcome class. It is **not reachable.**
6. **`k5k7/square_analogue.py:157` and `k5k7/square_analogue_m4.py:26`.** These are red-team scratch msolve launches. Their outputs enter the scripts' own `D_msolve` fields. No scanned tree executes or imports them. They are **not reachable.**

### OBSERVATION: the callgrind child and the literal CN-1 definition

The draft defines CLASSIFIED to include output entering "any pass / fail check, a gate, ... or any recorded result field other than a cost measurement (wall, cpu or instruction counts)". Measured against that definition:

**(a) Recorded non-cost fields.** The callgrind child's record carries non-cost fields: `child.outcome`, `child.returncode`, `f4_core_function`, `f4_core_note` and `reason`.

**(b) REG-1 compares them.** REG-1 is the r2 regression comparator, `r2_reg1.compare`:
- Item (b) compares every fixture target entry whole, minus the exclusion list X1..X17 (r2_reg1.py 260).
- For `instructions_callgrind`, X14-X17 exclude only `child.wall_seconds`, `child.peak_vm_bytes`, `instructions_user` and `f4_core_inclusive_Ir` (`implementation-v2-r2/reg1-exclusion-list.json`).
- So these fields are compared: `instructions_callgrind.method`, `.label`, `.child.outcome`, `.child.returncode`, `.child.rlimit_as_child_getrlimit`, `.f4_core_function`, `.f4_core_note`, and `.reason` when present.
- A difference in any of them fails REG-1.

**(c) REG-1 gates later packages.** The wrapper's preflight R-7 refuses every package after G1 unless REG-1 passes (r2_run_wrapper.py 22-23, 222-225).
- REG-1 compares the G1 package (`fixture --p 4111`) with RUN-GFPN-ac4487.
- `fixture_core` passes a callgrind_timeout on every fixture solve (358).

**Applying the definition literally**, the callgrind launch is therefore CLASSIFIED. The draft's CN-1 reading instead states that the callgrind child "is expected" among the unclassified reachable launches. The census reports this difference and does not resolve it; the approval act rules on it.

The census also notes, without drawing any conclusion from them:
- The check that consumes these fields is REG-1, in the r2 layer. It runs in the wrapper process, not in a driver command.
- `f4_core_function` comes from `callgrind_annotate`, an uncapped `subprocess.run` with a 600 s timeout (v2_solver.py 533). A timeout or error there becomes `f4_core_note` (547), which is a compared field.
- The r2 stage's own static list described the callgrind site as "output never classified" (`r2_devchecks_more.py` 530).

### CN-1 reading, as the draft words it

The draft says it is "approvable as written ONLY IF the reachable classified msolve launch sites are exactly two ... and every other reachable msolve launch is unclassified (the callgrind child ... is expected). If any other reachable classified site exists, this draft is NOT approvable as written ... An unreachable site is listed and is not a bar."

**Census values:**
- **Reachable msolve launch sites: 3.**
  - `v2_driver.py:165-166` (classified);
  - `a1_health.py:144/147` (classified);
  - `v2_driver.py:209` -> `v2_solver.py:517`, the callgrind child. It is classified under the literal definition through the fields and REG-1 comparison above. The draft expected it to be unclassified.
- **Other reachable msolve launch sites: none.** No other classified reachable site exists, and no unclassified one either.
- **Unreachable msolve launch sites: 4**, all listed above: v1 `run_wrapper.py:36`, v1 `symmetrize.py:399`, `k5k7/square_analogue.py:157` and `k5k7/square_analogue_m4.py:26`.
- **The census makes no approvability judgement.**

## 3. CN-2: health-path facts (i)-(ix)

**(i) CONFIRMED.**
- `run_system` builds the log text as the `.ms.log` text + `"\n"` + the `.ms.err` text + `"\n"`: `logp`/`errp` at line 145, the loop at 157-162. This matches `v2_driver.py` 170-175 (`for ext in (".ms.log", ".ms.err")`).
- It classifies with `V.classify_solve` (182) only when the child outcome is ok (167). Otherwise it takes `outcome, reason = rec.outcome, rec.refusal_reason` (183-184).
- `a1_health.py` removes no file, so `.ms.log` and `.ms.err` persist after `run_system` returns.
- Differences, none of which is an SSF class:
  - a1_health passes `nfail or 0` where v2_driver passes 0-initialised `nfail`; the value is the same.
  - On a non-ok child, a1_health records `reason = refusal_reason`, where v2_driver records None, except for refused_to_start.

**(ii) CONFIRMED.**
- `classify_solve` returns (v2_solver.py 491-508):
  - 491: `(rec.outcome, None)`;
  - 493 and 495: `positive_dimensional`;
  - 498: `degenerate_parametrisation`, "eliminating polynomial is not square-free" (SF-1 (i), exact);
  - 501: "eliminating polynomial degree %s != quotient dimension %s (...)" (SF-1 (ii), prefix);
  - 505: "msolve reports square-free part degree %s != quotient dimension %s" (SF-1 (iii), prefix);
  - 507: "%d parsed solution(s) fail substitution into the descended system" (SF-1 (iv), suffix);
  - 508: `ok`.
- `run_system` stores these unmodified in `v2_outcome_class` and `v2_outcome_reason` (185-186). Those are the only assignments to those keys in any scanned file.
- `r2_resolve.ssf_clause` (62-68) matches the same strings.

**(iii) CONFIRMED.**
- The bytecode of `a1_health.run` was compiled in memory; no file was written. Its four `run_system` loads are all `LOAD_GLOBAL`, at lines 234, 237, 241 and 244, so the name resolves through a1_health's module globals at call time.
- `run`'s defaults do not capture `run_system`.
- No `from a1_health import` exists in any scanned file.
- The only textual occurrences of `run_system` are a1_health.py 140, 234, 237, 241 and 244, plus a string in `r2_devchecks_more.py` 534, which is not code.
- The only module that calls `run_system` is `a1_health`.
- `a1_driver.H` is `import a1_health as H` (a1_driver.py 38).

**(iv) Callers.**
- `a1_health.run` has two callers:
  - `a1_driver.py:129` in `cmd_controls_a1`. It passes no `reinvoke_on_fail`, and the default is False (a1_health.py 223). It is reached by trial-plan-v2-a1-r2 `controls-a1` only.
  - `a1_health.py:287`, the file's own CLI `main`, which takes `--reinvoke-on-fail` from the command line. It is reached by no plan command, because it sits inside `if __name__ == "__main__"`.
- `a1_health.run_system` is called only from `a1_health.run`, at 234, 237, 241 and 244.
- Commands reaching `run_system`: trial-plan-v2-a1-r2 `controls-a1` only, by the chain `cmd_controls_a1 -> a1_health.run (129) -> run_system`.
- No trial-plan-v2-r2 command reaches it.

**(v) CONFIRMED.**
- `DEV_TIMEOUT_S = 1800` (line 53). It is passed as `timeout_s=DEV_TIMEOUT_S` at line 147, which is a `LOAD_GLOBAL` in the `run_system` bytecode, so it is read at call time.
- Its only occurrences in any scanned file are lines 53 and 147. Nothing rebinds it.
- `run_system` has no timeout parameter.

**(vi) CONFIRMED; round trip 4/4 byte-identical, no solver run.**
- `run_system` writes the `.ms` from `(NAMES, p, eqs)` with `A.write_msolve_input` (143). It substitutes into the same `eqs` at 172 (`V.substitute`) and 178 (`param_substitution`).
- `dense_system` draws each coefficient as `rng.randrange(1, p)` (59).
- `_parse_ms_file` spans 582-608. The coefficient `% p` is at 606 and the return at 608. `write_msolve_input` is at 691, skips zero coefficients at 698 and writes terms at 701. This matches CORR-20260924-36ce25.
- **Imports.** The four permitted names were imported: `v2_arms.write_msolve_input`, `v2_driver._parse_ms_file`, `a1_health.draw` and `a1_common.HEALTH_SEED`.
  - Before importing, the script listed the module-level statements of every module those imports load. They are path constants, `sys.path` inserts, `flint.ctx.threads = 1`, `ctypes.CDLL(None)` and a regex compile. None is a computation or a child launch.
  - Child pids before and after the import: none. Guard blocks: 0.
- **Round trip.** The four systems `a1_health.draw` produces at p' = 1073741831 were written with `write_msolve_input` to the scratchpad. Then `write_msolve_input(tmp, *_parse_ms_file(f))` was compared with `f`:

| system (tag) | seed | pattern | .ms sha256 | bytes | round-trip sha256 | bytes | byte-identical | first differing offset | coefficients in [1, p-1] |
|---|---|---|---|---|---|---|---|---|---|
| `health_p1073741831_d222` | `2026092001:v2a1:health:1073741831` | (2, 2, 2) | `ad2fd42b8706514ce4059e9d01d03ffb6a6df6d94fb24caf4c484bdacbf606a9` | 454 | `ad2fd42b8706514ce4059e9d01d03ffb6a6df6d94fb24caf4c484bdacbf606a9` | 454 | True | None | True (min 83742761, max 1049688468) |
| `health_p1073741831_d444` | `2026092001:v2a1:health:1073741831` | (4, 4, 4) | `fd41e8c8f19a9e276d68d3a3ee0b5fed200417dadd5741d1d3fb9afd5e996c7b` | 1789 | `fd41e8c8f19a9e276d68d3a3ee0b5fed200417dadd5741d1d3fb9afd5e996c7b` | 1789 | True | None | True (min 4452700, max 1043428588) |
| `health_p1073741831_d222_seed2` | `2026092001:v2a1:health:1073741831:2` | (2, 2, 2) | `486e453e0dcc5651ae8b8638df0e49742b63eba0377a497b0468aa17bf8681bb` | 448 | `486e453e0dcc5651ae8b8638df0e49742b63eba0377a497b0468aa17bf8681bb` | 448 | True | None | True (min 32053202, max 1061006686) |
| `health_p1073741831_d444_seed2` | `2026092001:v2a1:health:1073741831:2` | (4, 4, 4) | `76b51809a762c9cbb02071fe516878b3ca7ddcd92018a0962fb28510890d3107` | 1787 | `76b51809a762c9cbb02071fe516878b3ca7ddcd92018a0962fb28510890d3107` | 1787 | True | None | True (min 9966784, max 1057667721) |

- For each system, the parsed `(names, p, eqs)` equals the drawn system. Each (2,2,2) system has 3 equations and 30 terms, and each (4,4,4) system has 3 equations and 105 terms. No equation was dropped.

**(vii) How the frozen code records a failing run_system result.**
- `res["checks"]` (188-198) holds eight booleans: `exit_0`, `zero_dimensional_parametrisation`, `quotient_dimension_equals_expected`, `elim_degree_equals_expected`, `elim_squarefree`, `rational_solutions_substitute`, `parametrisation_substitutes` and `threads_executed_1`.
- `res["pass"] = all(checks)` (199).
- On failure only, `solver_side_signal` is set (200-218) to one of `harness_refused_to_start`, `crash_or_signal`, `refused_characteristic`, `unparseable_output`, `degree_mismatch` or `substitution_failure`.
- In `run` (232-247):
  - The first draw is `entry["first"]`.
  - If it fails, `retry = draw(seed + ":2", p)` is drawn once, lazily: both patterns come from ONE `Random(seed + ':2')` stream in PATTERNS order. `run_system` then runs on `retry[degs]` and the result is stored as `entry["retry_seed2"]` (238-242).
  - Reinvocations happen only with `reinvoke_on_fail` (236-237, 243-244).
  - `pattern_pass = first.pass or retry_seed2.pass` (245), and `report["pass"] = all(pattern_pass)` (247).
  - The report is written to `health-<p>.json` (251).
- `a1_driver`'s check (d) records `hr["pass"]` plus, per pattern, `pattern_pass` and the FIRST draw's D and getrlimit (130-133).
- A failed check (d) makes controls_a1 `gate_pass` false (187, 208). The check's detail dict carries no `outcome` key and no dict-valued entries at the keys `a1_driver` inspects (188-205). So a failure of check (d) alone is classed `implementation_error` by those lines. It is classed `infrastructure_error` only if another failed check carries an infrastructure outcome class.

**(viii) Maximum classified msolve launches per controls-a1 command, frozen code: 6. This confirms CORR-20260924-5b83a1 item 2 (6).**
- **Planted-arm solves: at most 2.** There is 1 `D.solve` (a1_driver.py 166) per arm, inside a loop over 2 arms (143). No `callgrind_timeout` or `gb_only` is passed, so no callgrind child runs.
- **Health launches: at most 4.** There are 2 patterns, each with a first draw (234) and at most one seed-':2' re-draw (241). The reinvocations at 237 and 244 need `reinvoke_on_fail`, which is False here.
- **No other msolve launch site** is reachable from controls-a1. Static reachability also lists the callgrind site inside `solve()`, but controls-a1 passes no callgrind_timeout, so it is never launched.
- **Derived bounds (derived from code and draft text; not measured):**
  - With the r2 layer as delivered, where only solve() is wrapped with K + 1 = 6 attempts: at most 2 x 6 + 4 = 16.
  - With HR-3 as drafted: at most 2 x 6 + 4 x 6 = 36.
  - Both are further bounded by the SF-2 (c) and HR-6 caps.

**(ix) Watchdogs or timeouts spanning more than one run_system call in the controls_a1 package: none found in code.**
- Only per-child timeouts exist:
  - `DEV_TIMEOUT_S` for each `run_system` (147);
  - the per-target watchdog `*|m3` for each planted solve (166);
  - `builder_timeout_s.m3` for each build child (146);
  - `PARI_TIMEOUT_S = 7200` for the gp child (a1_pari.py 28).
- `a1_health.run` (223-253) reads no clock and has no deadline.
- `cmd_controls_a1` reads the clock only at line 59, `t0`, which feeds `metrics.wall_seconds` (210).
- `r2_entry_a1` has no alarm or timer.
- `r2_run_wrapper` launches the driver with `subprocess.run` and no timeout (437; "no outer guard", line 36).
- **Plan watchdogs:**
  - The package's `watchdogs` field reads "per_arm_m keys *|m3 and builder_timeout_s m3 (uniform with v2)".
  - `per_cell_no_measurement_watchdog` is evaluated only in `v2_driver._run_cell` (cells).
- **Not in scanned code:** dispatcher lane-claim TTLs and run-card wall-clock budgets. The successor R2b'' card does not exist yet.
- **Derived, not measured:** the 4 health launches are each capped at 1800 s, which is at most 4 x 1800 s of child wall time, plus launch overhead.

### CN-2 reading, as the draft words it

The draft says: "a discrepancy in (i), (ii), (iii) or (vi) makes this draft NOT approvable as written ...; a discrepancy in (iv), (v), (vii), (viii) or (ix) is ruled on by the approval act".

**Census values:**
- **(i), (ii), (iii), (vi):** no discrepancy found. The (i) differences listed above involve no SSF class.
- **(iv):** as the draft states: `a1_driver.py` 129 with `reinvoke_on_fail` false, reached by `controls-a1` only. There is one further caller, the file's own CLI `main` at `a1_health.py:287`, which no plan command reaches.
- **(v):** confirmed.
- **(vii):** recorded above, including the lazy one-stream ':2' re-draw and how a failure of check (d) alone is classed.
- **(viii):** 6. This equals CORR-20260924-5b83a1 item 2.
- **(ix):** no spanning watchdog in code.
- **The census makes no approvability judgement.**

## 4. CN-3: PARI inventory

### In-process cypari2 entries

Only one in-process PARI entry computes on a field: `v2_common.curve_order_pari` (v2_common.py 249-261; `import cypari2` 252; handle `cypari2.Pari()` 253; `pari(expr)` 261).

**Stack:** PS-1 branch P-A, `parisize 67108864`, `parisizemax 536870912`, configured by `r2_common.PariStack.configure` (239) at entry step 1, before any v2 import (r2_entry_v2.py 36; r2_entry_a1.py 45).

**Call sites:** v2_driver.py 308 (`fixture_core`), 542 (`cmd_fixture4`) and 771 (`cmd_controls`). The r1 and r2 dev-check workers also call it; no delivered entry reaches those.

**Where the plans reach it:** trial-plan-v2-r2 `fixture`, `fixture4` and `controls`. No trial-plan-v2-a1-r2 command reaches it.

| command | (p', field degree) | curve | covered by DV-2's three points of paristack PS-6 |
|---|---|---|---|
| fixture --p 4111 | (4111, 3), F_4111[z]/(z^3 - 2) | fixture_n3(4111) | yes (paristack line 661) |
| fixture --p 16777291 | (16777291, 3), F_16777291[z]/(z^3 - 2) | fixture_n3(16777291) | yes (line 662) |
| fixture4 | (4111, 4), GF(4111^4) modulus x^4 + 5x^2 + 3586x + 12 | fixture_n4() | yes (line 663) |
| controls | (4111, 3) | fixture_n3(4111) (v2_driver.py 764, 771) | yes (line 661) |

The plans reach no in-process PARI entry at a ladder prime at n = 5.

**Other in-process cypari2 uses reached by every command of both plans.** They do not compute on a field. They all come from `r2_common` in the entry process:
- `PariStack.configure` (237-239), which calls `allocatemem`;
- `start_readback` (250-262), which uses two fresh handles and reads `default(parisize)` and `default(parisizemax)`;
- `exit_readback` (265-284);
- `versions` (295-296: `import cypari2`, `cypari2.Pari.pari_version()`).

**Unreachable entries:**
- v1 `ladder_select.py` 23;
- `r1_common` PariStack and `versions`;
- the r1 and r2 dev-check workers `worker_dv2`, `worker_dv3` and `worker_semantics`.

### Children that run PARI

**gp, `a1_pari.curve_facts`** (a1_pari.py 94-96):
- It runs as a capped child under `run_child`: `/usr/bin/gp -q -f --default nbthreads=1 <script.gp>`.
- The script's first two lines set the stack: `default(parisize, 256000000); default(parisizemax, 4000000000);` (a1_pari.py 38).
- It is reached by trial-plan-v2-a1-r2 `controls-a1` only (a1_driver.py 89), at (1073741831, 5) on the three ladder curves of that rung. The field is `Fq.binomial(p, 5, cmod)`, v2_common.py 154.
- `fb1_curve_search` is not reachable.

**gp version probes.** They do no computation and set no stack:
- `a1_pari.gp_version`, line 121: an uncapped `subprocess.run`, 30 s timeout, reached by `controls-a1`;
- `r2_run_wrapper` `sh("gp --version-short 2>&1 | head -1")`, line 412: an uncapped shell child in the wrapper process, run for every package.

**Sage comparator** (v2_driver.py 650):
- `/opt/conda-sage/envs/sage/bin/python k4a_anchor_system.py <cdir>` runs as a capped child, with `comparator_timeout_s` 3600.
- It is reached by trial-plan-v2-r2 `anchor-identity` only.
- Its PARI use is `E.order()`, PARI SEA via Sage (k4a line 158, inside `alarm(240)`, line 156).
- It loops over both CURVES (309), so it reaches **(16777291, 5)**, RUN-GFPN-61bba9 "anchor25" (line 72), and **(65551, 5)**, RUN-GFPN-bbed6f "anchor17" (line 77). The modulus is `Zv^5 - cmod` (135).
- Other Sage field arithmetic in the script: `GF`, `PolynomialRing`, `is_irreducible`, `resultant`, and matrix `rank`/`solve_right`. Which backend each uses was not determined statically, and no Sage process was started.
- **Stack:** the code sets none. The start-up probe values, read from the stage-r2 bundle member `dv1/sage_pari_probe.stdout` (`a38e8466...8b88`), are:
  - `parisize 8000000`
  - `parisizemax 1073741824`
  - `stacksize 8000000`
  - `stacksizemax 1073741824`
  - `sage_version 10.9`

  These equal the values DEC-20260924-bea197 R-5 quotes.

### CN-3 reading (informational)

- Every in-process PARI entry that the plans reach at a (p', degree) is covered by DV-2's three points: (4111, 3), (16777291, 3), (4111, 4). No uncovered point was found.
- Two child-side uses are recorded:
  - the Sage comparator, at the library default stack, at (16777291, 5) and (65551, 5);
  - gp, at 256000000/4000000000, at (1073741831, 5).

## 5. CN-4: other child launches

### Driver process, reachable from the plans' commands

These are all the child launches in the driver process that are not listed under CN-1 (static reachability; "classified" is read from the code):

| site | child | commands reaching it (static) | output classified? | clock | seed | environment |
|---|---|---|---|---|---|---|
| `v2_common.py:132` | shell: dpkg-query libmsolve-* (package query) | aggregate, aggregate-a1, anchor-identity, build, cells, controls, controls-a1, fixture, fixture4 | no: host block only | no | no | yes: installed package database |
| `v2_common.py:131` | shell: dpkg-query -W -f='${Version}' msolve (package query; msolve is NOT executed) | aggregate, aggregate-a1, anchor-identity, build, cells, controls, controls-a1, fixture, fixture4 | no: host block only | no | no | yes: installed package database |
| `v2_common.py:129` | shell: grep -m1 'model name' /proc/cpuinfo / cut -d: -f2 (host scan) | aggregate, aggregate-a1, anchor-identity, build, cells, controls, controls-a1, fixture, fixture4 | no: recorded in raw-result host block (v2_driver.finish line 79); not compared by REG-1 (not in its compared items) | no (60 s subprocess timeout only) | no | yes: host CPU |
| `v2_common.py:136` | shell: dpkg-query -W -f='${Version}' msolve (package query) | aggregate, aggregate-a1, anchor-identity, build, cells, controls, controls-a1, fixture, fixture4 | no classifier; recorded as envelope.msolve_version and, in anchor-identity, raw['msolve_version'] (line 639) and in envelope tuples | no | no | yes: installed package database |
| `v2_driver.py:101` | python3 -B implementation-v2/v2_child.py <spec.json> (builder: build_poly / raw_grid); sys.executable | anchor-identity, build, cells, controls, controls-a1, fixture, fixture4 | yes: the built polynomial / grid defines the systems solved; build outcome and meta (single-flip, held-out) enter checks (e.g. a1_driver check (f) lines 179-186; fixture F-checks) | timeout_s (builder_timeout_s) -> outcome timeout; meta seconds_total recorded | yes, declared: random.Random(spec['sample_seed']) and ':flip' / ':releq' streams (v2_child.py 72, 88, 94); seeds are deterministic strings from the driver | inherits the driver env; output path under C.CACHE_DIR when to_cache (GFPN_V2_CACHE_DIR / TMPDIR; v2_common.py 42) |
| `v2_driver.py:650` | Sage python /opt/conda-sage/envs/sage/bin/python k4a_anchor_system.py <cdir> (comparator) | anchor-identity | yes: its random target x_R and anchor25_random.ms feed the anchor trace-identity gate (v2_driver.py 659-669, 704-720); failure -> infrastructure_error, gate_pass false (655-658) | comparator_timeout_s (run_child); inside the script alarm(240) around E.order() (k4a 156) -> order not computed if it fires | yes, declared in the script: random.Random('TASK-20260923-58953e:K4a:%d' % p), set_random_seed(20260923 + p) (k4a 198-199) | inherits the driver env; the Sage installation at a fixed path |
| `v2_solver.py:533` | callgrind_annotate --inclusive=yes <out> (UNCAPPED subprocess.run, not run_child; PATH lookup) | anchor-identity, cells, controls, controls-a1, fixture, fixture4 | its output sets f4_core_function / f4_core_note (compared by REG-1 (b); not excluded) and f4_core_inclusive_Ir (excluded, X17) | timeout 600 s -> exception -> f4_core_note 'callgrind_annotate failed: ...' (a compared field) | no | yes: PATH resolution of callgrind_annotate |
| `v2_solver.py:517` | valgrind --tool=callgrind <msolve argv> (see CN-1) | anchor-identity, cells, controls, controls-a1, fixture, fixture4 | see CN-1 site v2_driver.py:209 | callgrind_timeout_s | the msolve child it runs is the same argv as the solve (FGLM clock seed) | valgrind at /usr/bin/valgrind |
| `a1_pari.py:96` | /usr/bin/gp -q -f --default nbthreads=1 <script.gp> (capped) | controls-a1 | yes: controls_a1 check (b) (a1_driver.py 92-112) | PARI_TIMEOUT_S 7200 (a1_pari.py 28) | none set by the script (no setrand) | gp binary at /usr/bin/gp; -f skips gprc |
| `a1_pari.py:121` | /usr/bin/gp --version-short (UNCAPPED subprocess.run, timeout 30) | controls-a1 | no: recorded as detail_b.pari.gp_version inside check (b)'s detail | timeout 30 s -> 'ERROR ...' string recorded | no | yes: installed gp |

### Per-package harness processes

These run outside the driver command:
- **the wrapper** `r2_run_wrapper`, for every package of both plans;
- **the post-run checker** `r2_check_run`, named `checker` by both plans.

Their child launches:

| site | group | program | process |
|---|---|---|---|
| `v2_common.py:132` | sh | shell: dpkg-query | r2_run_wrapper |
| `v2_common.py:131` | sh | shell: dpkg-query | r2_run_wrapper |
| `v2_common.py:129` | sh | shell: grep / cut | r2_run_wrapper |
| `r2_check_run.py:254` | check_run | <sys.executable: python3> | r2_check_run |
| `r2_run_wrapper.py:73` | git | git (fixed here; arguments forwarded from parameter args) | r2_run_wrapper |
| `r2_run_wrapper.py:78` | git | git (fixed here; arguments forwarded from parameter paths_rel) | r2_run_wrapper |
| `r2_run_wrapper.py:78` | git | git (fixed here; arguments forwarded from parameter paths_rel) | r2_run_wrapper |
| `r2_run_wrapper.py:93` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:116` | git | git (fixed here; arguments forwarded from parameter paths_rel) | r2_run_wrapper |
| `r2_run_wrapper.py:208` | git | git (fixed in r2_run_wrapper:tree_check) | r2_run_wrapper |
| `r2_run_wrapper.py:207` | git | git (fixed in r2_run_wrapper:tree_check) | r2_run_wrapper |
| `r2_run_wrapper.py:206` | git | git (fixed in r2_run_wrapper:tree_check) | r2_run_wrapper |
| `r2_run_wrapper.py:437` | driver | <sys.executable: python3> | r2_run_wrapper |
| `r2_run_wrapper.py:420` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:419` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:418` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:417` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:416` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:416` | git | git (fixed in r2_run_wrapper:git) | r2_run_wrapper |
| `r2_run_wrapper.py:414` | sh | shell: valgrind | r2_run_wrapper |
| `r2_run_wrapper.py:413` | sh | shell: python3 / print(m.version("cypari2"))' | r2_run_wrapper |
| `r2_run_wrapper.py:412` | sh | shell: gp / head | r2_run_wrapper |
| `r2_run_wrapper.py:411` | sh | shell: python3 / print(yaml.__version__)' | r2_run_wrapper |
| `r2_run_wrapper.py:411` | sh | shell: python3 / print(numpy.__version__)' | r2_run_wrapper |
| `r2_run_wrapper.py:410` | sh | shell: python3 / print(flint.__version__)' | r2_run_wrapper |
| `r2_run_wrapper.py:410` | sh | shell: dpkg-query | r2_run_wrapper |
| `r2_run_wrapper.py:398` | git | git (fixed in r2_run_wrapper:git_tree_state) | r2_run_wrapper |

Readings for the harness groups:
- **git.** This covers `rev-parse HEAD`, `branch --show-current`, `log -1` for the three trees and the receipts, `status --porcelain`, `ls-files` and `status --porcelain --untracked-files=all` per tree.
  - Outputs enter the R-4..R-6 preflight refusals (a gate) and the environment.json `git` block.
  - Dependence: repository state; no clock or seed.
- **sh.** This covers `dpkg-query` msolve, four `python3 -c` version probes (PATH `python3`, not `sys.executable`), `gp --version-short | head -1` and `valgrind --version`. They are uncapped and have a 60 s timeout. The v2_common host-scan commands (`grep` on /proc/cpuinfo and `dpkg-query`) also run in the wrapper, through `C.host_record()`.
  - Outputs: environment.json only.
  - Dependence: environment (PATH and installed packages).
- **driver (line 437).** This is `python3 -B r2_entry_{v2,a1}.py <driver_args>`, run with `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1` and `GFPN_RUN_DIR`. It has no timeout. This is the command itself.
- **check_run (line 254).** This is `python3 -B r2_check_run.py frozen-v2|frozen-a1 <run dir>`, which runs the frozen `v2_check_run` or `a1_check_run`. Its output is the checker verdict.

None of these starts msolve. `dpkg-query ... msolve` queries the package database; it does not execute msolve.

### CN-4 reading (informational)

The rows above are the complete list for the approval act. Children whose output can depend on:
- **the clock:**
  - every capped child, through its timeout;
  - the Sage comparator's `alarm(240)`;
  - `callgrind_annotate`'s 600 s timeout, whose error text is a REG-1-compared field.
- **a seed:**
  - the builder, through declared `sample_seed` strings;
  - the Sage comparator, through `random.Random('TASK-20260923-58953e:K4a:%d' % p)` and `set_random_seed(20260923 + p)` (k4a 198-199);
  - the valgrind child, which runs msolve's clock-seeded FGLM.
- **the environment:** host scans, PATH-resolved tools, and `GFPN_V2_CACHE_DIR`/`TMPDIR` for the builder cache.

## 6. Deviations and disclosures

- **D-1.** The first invocation, at 2026-09-24T03:19:20Z, was wrapped in `/usr/bin/time -v`. That binary does not exist on this host: bash reported "No such file or directory" with exit 127, and the census script never started. It wrote nothing and created no scratch directory; census_scan.py was already in place. The second invocation, at 03:19:31Z, is the one recorded above as run. Wall time comes from the UTC stamps around it; the census records no peak-memory measurement.
- **D-2.** Before the as-run execution, 13 development invocations of pre-final versions of the scanner ran from the session scratchpad. They wrote output only there, not in write_scope. Each started only the same read-only `git` children, ran under the same in-process child-launch guard, and (in the later iterations) made the same permitted CN-2 (vi) imports. None started a solver, gp, Sage or valgrind child. Their outputs are superseded development artifacts and are not evidence.
- **D-3.** The card orders reading the draft, decision, corrections and card before writing anything, so those were read before their hashes were checked.
  - The first executable integrity comparison was a manual `sha256sum` of all five trees and all six amendment drafts against the receipts. It was made before any frozen source file was read.
  - The stage-r2 bundle's hash was compared before its member list was read.
  - The script then repeated the full check (section 1) before computing any reading.
- **D-4.** The census itself started 24 read-only `git` children (section 0). They are not solver children, and census.json records every argv.
- **D-5.** Static-analysis limits:
  - Method-name edges are approximate and over-inclusive.
  - Launches inside third-party libraries are not traced: Sage, PARI, python-flint, numpy.
  - Reachability is static; the call-graph rules are listed in section 2. It is not a dynamic trace, and DV-11 and DV-1 of the r3 stage remain the dynamic checks.
- **D-6.** Pre-existing, git-ignored v1 byte code (section 1) was left untouched.
- **D-7.** The Sage PARI stack values come from the archived r2 probe output only. No Sage process was started.
- **D-8.** No stop condition fired. The LC-2 integrity checks and the LC-1 scope rules both held.
- **D-9.** At the dispatcher's request, after the run of record, one bullet was removed from the Inference section. It recorded the runtime's self-reported model name, which may not appear in a committed research artifact. No reading, value or other line changed. census.json and census_scan.py contain no model name and were not changed; census.json's only matches on the search were the scratchpad path component `claude-0`, which is a directory name.
