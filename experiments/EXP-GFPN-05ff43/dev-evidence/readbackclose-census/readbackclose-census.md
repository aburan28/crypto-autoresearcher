# Close census: EXP-GFPN-05ff43, TASK-20260924-e8da78

This is the zero-run, zero-solve close census for the DRAFT
AMD-EXP-GFPN-05ff43-20260924-readbackclose. The draft is not approved. The census was
ordered by DEC-20260924-a789e1. Its card is `ledger/handoffs/TASK-20260924-e8da78.yaml`
(RKQ-1..RKQ-9). It is archived by TASK-20260924-71d070.

**What the census does.** It computes the draft's `pre_approval_readings` in the draft's
order: RKR-5, RKR-1, RKR-2, RKR-3, RKR-4, RKR-6 and RKR-7.

**What the census is not.**
- These are observations only.
- Nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
- No D or degree is reported as a result.
- Nothing here is an approval recommendation. For each reading, the census states the
  draft's condition and what it found. The approval act applies the reading.

**Files.**
- Machine-readable record: `readbackclose-census.json`.
- Check script, exactly as run: `rk_check.py`.
- Every value below comes from `readbackclose-census.json` or from a cited line.
- The method reuses the two earlier censuses:
  - the successor census, TASK-20260924-cab04e, archived by TASK-20260924-ddfb69;
  - the archived census, TASK-20260924-bf5724, archived by TASK-20260924-a01341.
  - What it reuses: their integrity pattern, their guard, their line-citation check, and
    their hand-read path tables, which the script then checks.
- Carried by hash, not recomputed: the RLR-2 finding and the X-01..X-12 table.

## 0. Run record

| item | value |
|---|---|
| task / card | TASK-20260924-e8da78 / `ledger/handoffs/TASK-20260924-e8da78.yaml` |
| dispatch | `/run EXP-GFPN-05ff43 under TASK-20260924-e8da78`. Lane claim `coordination/goals/GOAL-GFPN-380702/batches/BATCH-e409ca/claims/TASK-20260924-e8da78.1.claim.json` (owner executor, epoch 1, ttl 600 min, expires 2026-09-25T02:25:36Z). The dispatcher holds the claim and releases it; this task did not touch it, the queue or any ledger file |
| repository HEAD | 7996eda2819a09c6e3a32fcdcc18dd443dd71fd4 (the claim commit). The tree was clean at dispatch. At the final script run the only status line was `?? experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py` |
| DP-1 (as dispatched) | Ledger archive TASK-20260924-1ae107 committed as 2abe574332e79f8912a3c5adaaee7286f5860ce3 (receipt backfill a4cb7b74d); the post-commit verifier accepted it; pushed; PR #1422 open. The addendum_sha256 was read from `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-1ae107/ledger-receipt.json` (section 1 (a)), not from the dispatch prompt |
| DP-2 (as dispatched) | BATCH-e409ca revision 5e8f2cf6e appended this task (queued); `tools/research_dispatch.py --claims refs` and `tools/validate_dispatch_reference.py` both exit 0 |
| DP-5, re-checked before any write | `runs/` holds 54 run directories plus the file `.gitkeep`. There is no `dev-evidence/readbackclose-census/` (before this task wrote it), no `implementation-v2-r4*`, no `trial-plan-v2-r4.json` and no `trial-plan-v2-a1-r4.json`. The script re-checks at run time (`dp5_recheck`): 54 directories, no r4 path, and the census directory held only `rk_check.py` |
| final script run | 2026-09-24T16:51:12Z to 16:51:14Z UTC (1.418 s). Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py --out .../readbackclose-census.json --scratch-root <scratchpad> --name-words <scratchpad>/rkcensus/name_words.txt`, cwd `/tmp`, Python 3.11.15 |
| run packages created | 0 |
| msolve, valgrind, callgrind_annotate, gp, Sage or builder children | 0 |
| scanned-tree modules imported | 0 |
| network | not used |
| files read by the final run | 66, each with sha256 in `files_read_sha256`. Also a text scan of 251 files under `tools/`, `harness/` and the three implementation trees (RKR-7), recorded as one combined digest |
| wall_clock_seconds 21600 (advisory) | not reached. The script's final run took 1.418 s; the task's total elapsed time was not instrumented |

**Inference block (RKQ-9).**
- requested_policy: executor-implementation
- resolved_model_id: null. The dispatching session supplied none, and none is invented.
- fallback_used: false
- bedrock_used: false

This is not a security statement.

**Dispatcher memory guard (DP-4), verbatim as dispatched:** pid 875, a bash loop
(scratchpad memguard.sh) that kills the largest-RSS msolve/gp/python3 process when
MemAvailable < 2621440 kB (about 14.2 GB in use on this 16481980 kB host, swap 0, 4
CPUs). The task needs little memory and runs no solver.

**Child processes started by this task.** No msolve, valgrind, callgrind_annotate, gp,
Sage or builder child was started.

The git children were all read-only:
- In the shell, before any bound input was read:
  - `git rev-parse HEAD`
  - `git status --porcelain --untracked-files=all`
  - `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'` (empty output)
  - `git check-ignore -q orchestration/__pycache__`
- Phase 1 of each of the three `rk_check.py` runs made these four calls:
  1. `git -C /home/user/crypto-autoresearcher diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
     (exit 0, empty)
  2. `git -C /home/user/crypto-autoresearcher ls-files -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
     (a pathspec sanity check; 92 files)
  3. `git -C /home/user/crypto-autoresearcher rev-parse HEAD`
  4. `git -C /home/user/crypto-autoresearcher status --porcelain --untracked-files=all`
- In the shell:
  - `git -C /home/user/crypto-autoresearcher status --porcelain --untracked-files=all`,
    once before the final run and once as the final check reported in the executor's
    return.

Other shell children were read-only utilities or scratch writers:
- `ls`, `find`, `grep`, `sed`, `cat`, `wc`, `cut`, `head`, `diff`, `sha256sum`,
  `date`, `mkdir`, `printf`, `mv`;
- `python3 --version`.
- `python3 -B` readers of JSON and YAML data, plus:
  - one ast / dis inspection of `v2_solver.py`, compiled from source text in that
    process;
  - two ast enumerations: the checker items, and the r3 attribute assignments;
  - the scratch integrity pre-check `<scratchpad>/rkcensus/pre_integrity.py`.
- None of these imported a module of a scanned tree.

**The in-process guard (RKQ-1).**
- It is installed after phase 1 with `sys.addaudithook`.
- It refuses:
  - the launch events `subprocess.Popen`, `os.system`, `os.exec`, `os.posix_spawn`,
    `os.spawn`, `os.fork`, `os.forkpty`, `pty.spawn` and `os.startfile`;
  - any import of 259 module names. These are every `.py` file of the implementation
    trees, `tools/`, `harness/`, the k5k7 scratch and the comparator scratch. The sha256
    of the sorted name list is
    `1b6b56e1ba7afa2c9467bf239d44b5415f3c53ac3e4636dea0fb1333e90458e0`.
- No name collides with a standard-library module, and none was already imported
  before the guard was installed.
- A self-test with `sys.audit` refused `subprocess.Popen` and `v2_solver`. Self-test
  events are not counted.
- **Attempt counts in the final run: launch 0, import 0.** Both development runs also
  counted 0 and 0.

## 1. RKR-5: integrity (RKQ-2), applied first

Every check passed before any bound input was read, and again as phase 1 of each script
run. The full per-path hashes are in the JSON under `phase_1_integrity_RKR-5`.

| check | result |
|---|---|
| (a) readbackclose draft | computed `f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c`, equal to `addendum_sha256.sha256` in `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-1ae107/ledger-receipt.json`, whose `path` field names the same file. In-file `status: draft`, `approved_by: null`, `approval_decision: null`: PASS |
| (b) readbackfull | computed `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1`, equal to the card value: PASS |
| (b) readbackcover | computed `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e`, equal to the card value: PASS |
| (c) nine VA-1 files vs DEC-20260924-e52eec `bound_hashes` | 9 / 9 equal: v1_to_v2_reanchor_and_arm_iii `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3`; v2_addendum_rung31 `2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c`; paristack `856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7`; seedresolve `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81`; solverevent `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f`; healthresolve `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d`; launchcover `c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447`; consumercover `a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0`; valueclose `877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1`: PASS |
| (d) archived census vs the TASK-20260924-a01341 receipt | readback-census.md `2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3`; readback-census.json `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4`; rb_check.py `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64`: 3 / 3 equal: PASS |
| (d) successor census vs the TASK-20260924-ddfb69 receipt | readbackfull-census.md `5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7`; readbackfull-census.json `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158`; rf_check.py `ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558`: 3 / 3 equal: PASS |
| (e) TASK-20260924-f1fb0e | snapshot receipt 22 / 22 paths equal (each hash in the JSON; for example r3_run_wrapper.py `dd52a4bfad9c4bfb0e4e37ee8a24951e8992edf8d2f1dfcc112e9bcdbabb9c19`, r3_check_run.py `939d7d7e5bc8a8c64f15df188f98f13b22ef7a9d696680f8e47854c2dbdcd14d`, trial-plan-v2-r3.json `77cd52d15c66e6a3729b1fdb313ff1b6c8a6d58096055403cc69986b1f4ce7cf`, trial-plan-v2-a1-r3.json `fbc9df3b94dcc302c7e53f5cf21ee53649dad4bec536d3115a2684f0af52042e`); post-run receipt 801 / 801 equal (combined digest of the sorted path-hash lines `3208cffc407a1c2c6b89dc094391ee9c14e2a3367a28a09e670f353e69b02fe1`): PASS |
| (f) implementation-v2/ vs TASK-20260923-0fa03f; implementation-v2-a1/ vs TASK-20260923-4ff597 | 14 / 14 and 12 / 12 bound paths equal (each hash in the JSON; for example v2_solver.py `0a3bdb9cc7f59f9029f677113f634ba7abf11a241c35e5e073099c2bd970ac9d`, v2_driver.py `0d22a082c967500f28d0aabdce1b0cdf125cf5a3109727045e6cf55407a20098`, v2_check_run.py `ed813df7760be9d9289a6643ba7be95cf9be905e6ba0835d476b56ea551d2e25`, a1_check_run.py `516d913687c31ef9fdfebb25c0f1b89e733237a57f8e3ad721388987130d229f`, a1_driver.py `0ec607c75feb5908b71613f6a0d2d1418ba8e7902919b71231bcc8be3381acde`); no file in either tree outside its receipt: PASS |
| (g) `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- .../implementation* .../trial-plan-*.json` | exit 0, empty output: PASS |

**Scope of (f).** Every bound path was checked, which covers every implementation file
read:
- the r3 files, both r3 plans and the r3 development-check files (`r3_dv7.py`,
  `r3_dv12.py` and the others) are bound by the f1fb0e snapshot receipt (e);
- the v1 `implementation/ladder.json`, read as data, is covered by (g).

## 2. RKR-1 (RKQ-3): every path, and what RK-1 as worded records

### Mechanical facts (script, from ast and from bytecode compiled from source text here)

- **Return statements.** `run_child` returns at 155, 160, 165, 169 and 171.
  `_run_child_locked` returns at 225, 232 and 308. Every return value is `rec`, except
  171, which returns what `_run_child_locked(..., rec)` returns.
- **Explicit `raise`.** None, in `run_child`, `_run_child_locked` or any `v2_solver`
  function they reach.
- **Functions reached.** `self_rss_bytes`, `other_solver_processes`,
  `SolverLock.__init__`, `SolverLock.acquire`, `SolverLock.release`,
  `_run_child_locked`, `_perf_open_instructions`, `_perf_read` and `_decode_status`.
  No other `v2_solver` function is reached.
- **Bindings.**
  - `rec` is bound in `run_child` only at 152.
  - `rec` is never rebound in `_run_child_locked`: it is the 9th parameter, and every
    store is a subscript or `update` on the same object.
  - `pid` is bound only at 181.
  - All three are fast locals (not cell variables) of one code object each:
    `run_child` (first line 149) and `_run_child_locked` (first line 177).
- **Bytecode.**
  - Line 181 is `LOAD_GLOBAL os`, `LOAD_ATTR fork`, `PRECALL`, `CALL`, `STORE_FAST pid`.
  - Line 220 and line 227 each end in `STORE_SUBSCR`. Line 227 first calls `int` twice
    and builds the dict.
  - Lines 173-174 appear twice: once on the normal exit (`RETURN_VALUE`) and once on the
    exception exit (`RERAISE`).
- **Handlers.**
  - `other_solver_processes` 82: `OSError`, then `continue`.
  - `SolverLock.acquire` 107: `OSError`; after the wait it closes the file and returns
    `False` inside `acquire`, and run_child then returns `rec` at 169.
  - `_run_child_locked`, child side 194 (`Exception`) and 206 (`BaseException`, `pass`).
  - `_run_child_locked`, parent side 261 (`(OSError, ValueError, IndexError)`), 267
    (`ProcessLookupError`) and 301 (`OSError`), each `pass`.
  - Finally blocks: `_perf_read` 142-143 and run_child 172-174.
  - **No frozen handler returns an object other than the 152 record from run_child.**
- **Other facts.**
  - No call site in the scanned trees passes `lock=`, so the finally at 172-174 always
    calls `SolverLock.release()`.
  - No signal handler, `register_at_fork` or audit hook is installed in the closure. The
    only asynchronous exception source is the default SIGINT handler
    (`KeyboardInterrupt`).
- 88 cited lines in this section were checked against the file text, with 0 failures.

### Per-path table

The columns follow the RKR-1 definition:
- **child**: a child is created (os.fork returned a positive pid in the parent).
- **227**: line 227 executed.
- **fate**: run_child returns or raises.
- **frames**: frozen frames on the traceback of the raise that leaves run_child.
- **pid**: `pid` is bound in the `_run_child_locked` frame.
- **RK-1 as worded records**: readback_from / child_created / pair / pair_read_by_parent.
- **(a)** and **(b)**: RKR-1 (a) and (b).

The object identity column is not repeated in each row:
- on every return, the returned object IS the object built at 152;
- on every raise that leaves run_child, `rec` in the outermost frozen run_child frame IS
  that object, with the one exception noted at P-5a.

| id | path (lines) | child | 227 | fate | frames | pid | RK-1 as worded records | (a) | (b) |
|---|---|---|---|---|---|---|---|---|---|
| P-1..P-4 | refused before fork: invalid cap (153-155); driver RSS (156-160); other solver process (161-165); lock held (166-169) | no | no | returns | n/a | n/a | returned_record / false / absent / false | n/a | holds (no child) |
| P-6 | ERR setrlimit: the child writes `ERR setrlimit ...` and exits 97 (193-196; 220-225) | yes | no | returns | n/a | n/a | returned_record / **true** (key) / absent / false; report `ERR setrlimit ...` | n/a | holds |
| P-7 | pre-setrlimit child failure (186-191), swallowed at 206, exit 99; empty report (220-225) | yes | no | returns | n/a | n/a | returned_record / **true** (key presence, "the empty string included") / absent / false; report `''` | n/a | holds |
| P-8 | soft read-back != cap (226-232) | yes | yes | returns | n/a | n/a | returned_record / true / copied / true | holds | holds |
| P-9 | hard-only mismatch: the child exits 98 (200-201); the parent tests soft only (228). A race: it returns via P-12 or raises at 236 (P-14c) | yes | yes | returns or raises | on the raise: run_child, _run_child_locked | yes | returned_record or raise_frame_record / true / copied / true | holds | holds |
| P-10..P-13 | ok without perf (284-285, 308); ok with perf (280-282, 308); memory_exhausted / crashed / non-zero exit (290-308); timeout (263-270, 287, 308) | yes | yes | returns | n/a | n/a | returned_record / true / copied / true | holds | holds |
| P-5a | raise in run_child before 171: 152 (`list(argv)`, dict build); `self_rss_bytes` 51-56; `other_solver_processes` 69-90; `SolverLock()` 96-98; `acquire` 101-112; the refusal formatting; or an asynchronous exception at any of these | no | no | RAISES | run_child (+ callee) | n/a | raise_frame_record / false / absent / false | n/a | holds (no child) |
| P-5b | raise in `_run_child_locked` before a child exists: `os.pipe` 178 / 179, `time.time` 180, `os.fork` 181 failing | no | no | RAISES | run_child, _run_child_locked | no | raise_frame_record / false / absent / false | n/a | holds (no child) |
| **P-16** | raise AT 181 AFTER fork() created the child and BEFORE `pid` is bound. Line 181 is `CALL` then `STORE_FAST pid`. The raise is a MemoryError while the C function converts the new pid to a Python int, or an asynchronous exception (the default SIGINT handler's `KeyboardInterrupt`) delivered at the bytecode boundary after the CALL returns | **yes** | no | RAISES | run_child, _run_child_locked | **NO** | raise_frame_record / **false** / absent / false. `rec` lacks `child_rlimit_report` (220 not reached) and the frame holds no `pid` | n/a | **FAILS** |
| P-14a | raise after `pid` is bound and before 220 completes: 182 (asynchronous), `os.close` 210 / 211, `os.read` 214, 217, `os.close` 218, 219, 220 | yes | no | RAISES | run_child, _run_child_locked | yes (> 0) | raise_frame_record / **true** (pid) / absent / false; report key missing | n/a | holds |
| P-14b | raise after 220 and before 227 completes: 221; `os.close` 222; `os.wait4` 223; 224 (formatting; `_decode_status` 311-318); 226 (split / unpack); 227 (`int()` or the store) | yes | no | RAISES | run_child, _run_child_locked (+ _decode_status) | yes | raise_frame_record / true (key) / absent / false. The report as carried: `ERR ...` or `''` on 222-224; `OK <soft> <hard>` on 226-227 | n/a | holds |
| P-14c | raise after 227 completed, in `_run_child_locked` or a callee: 229, 230, 231; `_perf_open_instructions` 235 (126-136); `os.write` 236 (BrokenPipeError); 237; `os.wait4` 244; 249-260 (exceptions other than OSError / ValueError / IndexError escape 261); 263; `os.kill` 266 (other than ProcessLookupError); `os.wait4` 269; `time.sleep` 271; 272-279; `_perf_read` 281 (141; `os.close` 143 in its finally); 284-307 | yes | yes | RAISES | run_child, _run_child_locked (+ callee) | yes | raise_frame_record / true / **copied** / true | holds | holds |
| P-F1 | run_child raises AFTER `_run_child_locked` returned: an asynchronous exception at 171 after the CALL returns, or `lk.release()` raising in the finally (115-117: `fcntl.flock(LOCK_UN)`, `self.fh.close()`, or asynchronous). The returned record is discarded | yes | as the return path (yes on 232 / 308, no on 225) | RAISES | run_child (+ SolverLock.release). `_run_child_locked` is NOT on the traceback | n/a (frame gone) | raise_frame_record / true (key: 220 precedes 225, 232, 308) / copied where 227 executed / accordingly | holds | holds |
| **P-F2** | `_run_child_locked` raises AND `lk.release()` then raises in run_child's finally (172-174). The exception that leaves run_child is release's; the first is its `__context__`. Its traceback holds run_child (174) and SolverLock.release, and NOT `_run_child_locked` | as the first raise | as the first raise | RAISES | run_child, SolverLock.release | **NO frame of _run_child_locked** | after P-5b: false (correct, no child); **after P-16: false**; **after P-14a: false** (no key, no pid frame); after P-14b: true / absent; after P-14c: true / copied | holds (after P-14c the pair is copied from `rec`) | **FAILS after P-14a and after P-16** |
| P-C | CHILD-PROCESS side. In the fork child (os.fork returned 0), an asynchronous exception delivered before the try at 183 (at the bytecode boundary after 181, or at 182) leaves `_run_child_locked` and run_child IN THE CHILD PROCESS. run_child's finally calls `lk.release()` in the child (flock `LOCK_UN` on the open file description the parent shares), and the child then continues in the caller's frames without RLIMIT_AS (193 never ran). In the parent this is P-7: it reads `''` once the child exits and returns at 225 | per the definition, a parent fact: yes (P-7) | no | parent: returns | n/a | n/a | parent: returned_record / true (key) / absent / false. A recorder inherited by the fork child would record child_created false (no key; pid 0) | n/a | holds on the parent |

Notes to the table:
- **P-5a** (O-1). A raise at 152 itself comes before `STORE_FAST rec`, so the run_child
  frame is found but `rec` is unbound. RK-1 (b) does not say what is recorded in that
  case. No child exists.
- **P-5a** (O-2). An asynchronous raise after `acquire()` returned True at 167 and before
  the `try` at 170 leaves the host lock file locked until the SolverLock object is
  collected. No child exists.
- **P-14a, P-14b.** A raise before 227 is NOT A BAR as RKR-1 words it: the pair is
  "absent" with the report as carried.
- **P-14b** (O-3). At 226-227 the report is `OK <soft> <hard>` and the parent did not read
  the pair.
  - RK-1 (c)'s examples do not name this report class ("an ERR setrlimit report, the
    empty report, or the key missing when the raise preceded line 220").
  - Neither do RK-2 (ii)'s classes ("ERR setrlimit report; empty report; report not
    read").
  - From the frozen child, 226-227 can raise only asynchronously or by MemoryError. The
    child writes exactly `OK %d %d` (198).
- **P-14c** contains the successor census's P-14 at 230, 236 and 244, and its P-15 at 281.
- **P-16.**
  - The child reports OK and waits at 202 for the go byte. The parent never closes `go_w`
    on this path, so the child is released when the parent process exits (RKL-2).
  - Reachability is a run-time fact (RKL-3). The interpreter behaviour relied on is L-11.
- **P-F2** needs two raises:
  1. one in `_run_child_locked` after fork and before 220;
  2. then one from `release`: an OSError from `flock` or `close`, or an asynchronous
     exception (for example a second KeyboardInterrupt) while the finally runs.
- **P-C** (O-4) is not traced beyond run_child (L-12). The definitions state CHILD
  CREATED on the parent. RK-1 does not name records written by a recorder that a fork
  child inherited.

### RKR-1 reading, as the draft words it

The draft's condition, verbatim: "(a) on EVERY path on which line 227 executed, RK-1 (a)
or (b) as worded copies the pair; AND (b) on EVERY path on which a child is created, RK-1
as worded records child_created true. A path on which (a) or (b) fails makes the draft NOT
approvable as written."

It names as NOT A BAR: "a created child whose parent never read a pair (the ERR setrlimit
report, the empty report, a raise before 227; recorded "absent" with its report under
RK-1 (c) and named under RK-2); grandchildren (RKL-1); a child left waiting for the go
byte (RKL-2); refusals and raises before fork (no child); a child found in two sources."

Census finding:
- **(a):** the census names no path on which (a) fails. On every path on which 227
  completed:
  - either run_child returns the 152 object, which carries the pair;
  - or the exception leaving run_child has the run_child frame on its traceback, and
    `rec` there is the 152 object, which carries the pair (P-8..P-14c, P-F1, and P-F2
    after P-14c).
- **(b): the census names paths on which (b) fails as worded:**
  1. **P-16.** A raise at 181 after the child is created and before `pid` is bound. `rec`
     has no `child_rlimit_report`, and no `_run_child_locked` frame holds a `pid`, so RK-1
     (b) records child_created false.
  2. **P-F2 after P-14a (or after P-16).** A raise in `_run_child_locked` after fork and
     before 220, followed by a raise from `lk.release()` in run_child's finally. The
     exception that leaves run_child carries a traceback without the `_run_child_locked`
     frame. The first exception, whose traceback holds it, is only its `__context__`. RK-1
     (b) then records child_created false.
- Neither failing path is among the NOT A BAR classes as the draft words them. "a child
  left waiting for the go byte (RKL-2)" names the unrecorded run of the child, not the
  value of child_created.

## 3. RKR-2 (RKQ-4): reach and frame identity

**(a) Carried by hash.**
- Source: the successor census's RLR-2 block, in `readbackfull-census.json` (file sha256
  `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158`; canonical sha256
  of the RLR-2 block `b934feed9e87c829446a0f482d9e009a6ed8e53a6c3165799ef8eeaeebfbd667`).
  It is also in `readbackfull-census.md` 294-387 (sha256
  `5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7`).
- What it states:
  - six reachable call sites: v2_driver 101, 166, 650; v2_solver 517; a1_health 147;
    a1_pari 96;
  - none of them not intercepted;
  - no `from v2_solver import`;
  - no capped launch reachable from module-level code.
- **Change since dd1034553:** the RKQ-2 (g) diff is empty, so no call site has been added
  in the implementation trees or plans.

**(b) Definitions and rebinding.**
- `implementation-v2/v2_solver.py` has exactly one definition of `run_child` (line 149)
  and exactly one of `_run_child_locked` (line 177). Both are at module level.
- Compiling the source text gives exactly one code object each, with `co_firstlineno` 149
  and 177. These are the first lines RL-1 (a) and RK-1 (b) name.
- The scan covered every module of either r3 entry's import closure, as the successor
  census lists it: a1_common, a1_driver, a1_health, a1_pari, a1_reading, r3_common,
  r3_entry_a1, r3_entry_v2, r3_resolve, v2_arms, v2_child, v2_common, v2_driver,
  v2_field, v2_lift, v2_scoring, v2_solver and v2_verify_independent. It looked for any
  of these, naming either function:
  - assignment, augmented assignment or annotated assignment;
  - deletion;
  - loop, with or except target;
  - `global` or `nonlocal`;
  - an import binding;
  - a def or class of that name;
  - `setattr` or `delattr`;
  - a namespace-subscript write (`globals()`, `vars()`, `sys.modules`, `__dict__`);
  - a `__code__` write.
- **Result: no hit.**
- One `setattr` with a non-constant name was found and resolved. It is `v2_field.py:55`
  (`OpCount.merge`), whose name runs over the literal tuple `("fq_mul", "fq_inv",
  "fq_add", "fp_mul", "fp_inv")` on an OpCount instance. It is not either function.
- The r3 wrapper, `r3_check_run.py`, `r3_reg1.py`, `a1_check_run.py` and
  `v2_check_run.py` were also scanned. There was no hit.

**RKR-2 reading, as the draft words it.** The condition: "(a) the successor census's
RLR-2 finding stands ... and no call site has been added since (RKR-5's diff); AND (b) the
close census finds EXACTLY ONE definition each of run_child and _run_child_locked in
implementation-v2/v2_solver.py, with the first lines RK-1 names, and no rebinding of
either name anywhere in either entry's closure, so that the two code objects RK-1
captures are well defined."

Census finding:
- (a) The RLR-2 finding is carried unchanged, and the diff is empty.
- (b) There is exactly one definition each (149, 177), and no rebinding of either name in
  either closure.
- The r4 closure does not exist; the draft leaves it to DV-18 (h) (L-8).

## 4. RKR-3 (RKQ-5): zero-launch exactness

**Package kinds.**
- trial-plan-v2-r3.json: fixture (G1, G2), anchor (G3), controls (G4), fixture4 (F-4),
  build (3), cells m = 5 (9), cells m = 4 (9), aggregate (1), contingency (4).
- trial-plan-v2-a1-r3.json: controls_a1 (1), build (1), cells m = 5 (3), cells m = 4 (3),
  aggregate_a1 (1), contingency (2).

**Checker items.**
- The script lists every item mechanically (every `errs.append`, `errs +=` or
  `fails.append`):
  - v2_check_run 18;
  - a1_check_run 21;
  - r3_check_run 39;
  - r3_reg1 10.
- The non-append exits are:
  - r3_check_run 369 (no r3 plan reserves the id), 56 and 75 (redirection read-backs,
    exit 2), 400;
  - a1_check_run 141;
  - v2_check_run 110.
- Each item has a disposition per outcome in the JSON (`RKR-3.zero_call_outcomes.*.every_item`).
- r3_reg1's items are not applied to the package itself. REG-1 compares G1 with
  RUN-GFPN-ac4487 at the admission of later packages (r3_run_wrapper 285-287), and
  r3_check_run 327-334 reads the recorded verdict.

**Kinds with no zero-call outcome from the frozen driver's own logic** (a correctly
recorded outcome with no run_child call cannot come from the driver's result logic):
- **anchor (G3):** the comparator `run_child` at 650 is its first launch, unconditional.
- **controls (G4):** `build_poly` at 768 is its first action, and reaches run_child at 101.
- **build:** every plan build list holds S5 and S4 rows for every shape. Kind S takes no
  refusal branch (947) and reaches `build_poly` at 961.
- **cells m = 4:** the raw arm is disposition `run`, with no condition and no build
  needed. The first target runs `raw_grid` (1161), because `early_stop` is None and the
  per-cell watchdog (86400 s for raw|m4, checked at 1149) cannot fire before it.
- **controls_a1:** the gp child is unconditional (a1_driver 89 → a1_pari 96).
- **aggregate / aggregate_a1:** they never call run_child. Their raw kind is `aggregate`
  (v2_driver 1314; a1_driver 374), which v2_check_run exempts at 65, so no item fails by
  design. Their verdict is PASS.
- **contingency:** it runs as the kind it replaces.

**Zero-call outcomes, and every item that exits non-zero on them.**

The checker output shape on the ZL item is:
- a v2-r3 package prints the header `<rd>: FAIL; [<notes>]` and the item line
  `  - no child RLIMIT_AS read-back recorded`;
- an a1-r3 package prints `v2_check_run (unchanged, plan redirected): FAIL`, the same two
  lines, then `<rd>: addendum checks PASS`.
- The archived instance is RUN-GFPN-bfe956 (f1fb0e post-run receipt). Its frozen checker
  printed FAIL rc=1 with that single item line, under the header `... FAIL; ['7/7
  certificates re-verify independently']`, and its r3 checks were PASS.

| id | kind | outcome (frozen lines) | recorded as | items that exit non-zero |
|---|---|---|---|---|
| Z-C5 | cells m = 5 (both r3 plans) | No runnable cell reaches `_run_cell` (1090). Each ends earlier as one of: not_attempted by disposition (1037-1041); refused (rescaling 1044-1050; norm without 2-torsion 1052-1058); condition not met (1059-1067); polynomial unavailable (1068-1075); cached polynomial missing or sha256 mismatch (1076-1081); invalid (1083-1086) | completed_valid when every terminal is refused / not_attempted (1101). **failed / resource_exhaustion when any cell is `invalid`** (1101-1102). Certificate kind none (1105) | **exactly v2_check_run.py 66-67** |
| Z-F4 | fixture4 (F-4) | the data file's curve refuses the rescaling before any build (538-541) | failed / specification_error | **exactly v2_check_run.py 66-67** |
| Z-G12 | fixture (G1, G2) | the fixture curve refuses the DC-3 rescaling before any build (298-307; finish 280) | failed / specification_error, gate_pass false | **exactly v2_check_run.py 66-67** (a gate package: PASS_ZL never applies) |
| W-1 | every kind (recorded by the WRAPPER) | the driver exits or raises before any run_child call without writing raw-result.json. Examples: a1_driver `_check_package_p` 50-52; the SystemExit refusals at 223-224 and 232-233; an exception in `Ctx()`. The entry still wrote solver-events.json (`begin()`, r3_entry_v2 65) and pari-stack.json (77) | failed / infrastructure_error; raw and the three yaml files written by the wrapper (491-505) | **exactly v2_check_run.py 66-67**. For an aggregate the wrapper's raw has no `kind`, so 65 does not exempt it |
| W-2 | every kind (recorded by the WRAPPER) | the r3 entry refuses before any command (r3_entry_v2 60-64; r3_entry_a1 92). No `begin()`; pari-stack status `refused_before_any_command` with no exit read-back | failed / infrastructure_error (494-495) | v2_check_run 66-67; **r3_check_run 167** (solver-events.json missing), **279** (pari_stack status), **305** and **308** (no exit read-back; r3_common.write_pari_stack_json 405-417); and at least one of 283, 288, 293, 297, 302, 317, whichever read-back refused |

Every other item on Z-C5, Z-F4, Z-G12 and W-1 does not fail by design. The reasons are
recorded per item in the JSON:
- Artifacts: finish() writes the three yaml files (v2_driver 84-87), and the wrapper
  writes the rest (435 and on).
- Status agreement: the wrapper copies run_status, with the 508-509 exception that 53
  allows.
- Threads: `[]` is falsy at 72.
- Certificates: none exist, and the kind is none.
- F3: the strings are `undecidable ...` (v2_scoring 23, 257).
- torsion_S5_norm group order: 3840 (v2_arms 71-72).
- The launch-independent a1 and r3 items: every r3 item passed on the archived r3 gate
  packages G1..G4.

**Sufficient conditions for Z-C5** (static; which occurs is a run-time fact):
- **random_no2torsion.** torsion_S5_rq, S5_rescaled and torsion_S5_norm are refused (no
  rational 2-torsion; the plans record these as expected refusals), and raw is
  not_attempted by disposition. **One non-ok S5 m = 5 build row suffices.**
- **ecgfp5_shaped at 16777291.** The ladder data record `b_is_square_in_Fq: true`, the
  only rung and shape with true. The rescaling tests `F.is_square(b)` itself
  (v2_arms 165). Where that agrees with the record, it refuses torsion_S5_rq and
  S5_rescaled ("b-square class mismatch", 173-174). **One non-ok S5 row then suffices**,
  and torsion_S5_norm's condition `measured_in_this_package:S5` is not met.
- **Other (shape, p).** S5, torsion_S5_rq and S5_rescaled each end without an ok build
  row, or with a cache mismatch, or invalid.

**RKR-3 reading, as the draft words it.** The condition: "approvable as written ONLY IF
the close census, per package kind of either plan, states whether a correctly recorded
outcome with NO call of run_child can occur (with the frozen lines), and, for each such
outcome, ... lists EVERY item that exits non-zero, verbatim; AND that list is, for every
such outcome, EXACTLY the one item RK-3 (b) (iv) names. Another item failing by design on
a zero-launch outcome makes the draft NOT approvable as written."

Census finding:
- **Z-C5, Z-F4, Z-G12 and W-1:** the failing list is exactly the one item
  `v2_check_run.py` 66-67 ("no child RLIMIT_AS read-back recorded"), verbatim.
- **W-2** is an entry refusal before any command, recorded by the wrapper. On it, other
  items fail: r3_check_run 167, 279, 305, 308, and at least one read-back item.
- Whether W-1 and W-2 are "correctly recorded outcomes" in the draft's sense is not
  decided here (L-13).
- Also recorded:
  - A Z-C5 package with an `invalid` cell is recorded **failed / resource_exhaustion**
    with zero calls. RK-3 (b) reads no run_status, so its verdict is PASS_ZL.
  - RK-3 (b) (iv) says the output lists "EXACTLY ONE failing item ... and nothing else".
    The frozen output also always prints a header line (`<rd>: FAIL; [...]`), and the a1
    checker adds its own summary lines (see the output shape above).

## 5. RKR-4 (RKQ-6): admission coverage, outcomes, F-4

### (a) Reads of another package's recorded result

**Carried by hash.**
- The X-01..X-12 table of the successor census: canonical sha256
  `091c6891b6ebf2c0ca98480e5142c8448ff9e0dbb2dbbd546c1fac61e71031db`.
- Its outside-scope list: canonical sha256
  `c94ebbb4a2ec2462619342d91a76be10fc8ec196b498c8bca630d1013c2d9d59`.
- Its archived-package bindings: canonical sha256
  `79b8b27a2b6939b9bb0740571fdb208a084c0bae90c0308cba38283ef206f62c`.
- All three are in readbackfull-census.json; the md has them at 436-468.

**Change.** The RKQ-2 (g) diff is empty.

**Scan.** The script scanned every run-directory read pattern in these files: the
command modules (v2_driver, v2_common, v2_lift, v2_solver, v2_child, v2_scoring,
a1_driver, a1_health, a1_pari, a1_reading, a1_common), the r3 entries, r3_resolve,
r3_common and r3_run_wrapper.
- Every hit maps to X-01..X-12, or is not a read: v2_driver 1314 and a1_driver 375 write
  the list of run ids, and r3_run_wrapper 433 is the package's own directory.
- **0 unmapped lines.**

| id | reader | covered BY NAME, or named not covered by design |
|---|---|---|
| X-01 | r3_run_wrapper 176-181 (G1..G4 run_status, gate_pass) | RB-4 |
| X-02 | r3_run_wrapper 190-196 (the controls_a1 image) | RB-4 |
| X-03 | r3_run_wrapper 153-162, 285 (REG-1 on G1) | RK-3 (a) by name: "G1 read by REG-1 at the admission of every package after G1, G3 and G4 included". The X-03 reference (RUN-GFPN-ac4487) is named not covered by design |
| X-04 | r3_run_wrapper 199-203 (`requires`, existence) | RK-3 (a) by name: "every `requires` entry, subject to (d)" |
| X-05 | r3_run_wrapper 206-228 (R-12 failure_class) | named not covered by design |
| X-06 | r3_run_wrapper 273-274, 300, 305 (existence / count) | named not covered by design |
| X-07 | v2_driver `_load_build` 989-1003 | RK-3 (a) by name |
| X-08 | v2_driver `_prior_cells` 1006-1013, `_condition_met` 1110-1127 | RK-3 (a) by name |
| X-09 | v2_driver `cmd_aggregate` 1248-1326 | RK-3 (a) by name |
| X-10 | a1_driver `cmd_aggregate_a1` 276-393 | RK-3 (a) by name |
| X-11 | v2_common.resolve_replacement 76-86; a1_driver._resolve 243-254 | RK-3 (a) by name |
| X-12 | v2_driver `cmd_anchor_identity` 642, 683-686, 700 (RUN-GFPN-61bba9) | named not covered by design |
| **X-13 (further read found)** | **a1_check_run 79-84**, a CHECKER item: the controls_a1 image's run_status and gate_pass | covered by name by **neither** RB-4 nor RK-3 (a). RB-4 names the package it reads (X-02). The successor census listed it as outside its card's scope. RKR-4 (a) covers reads "by any command of either plan or by the r3 wrapper", and this reader is neither |

### (b) Per package kind so read and per correctly recorded outcome: the RK-3 (b) verdict

This is read from the frozen and r3 checker items. The r4 checks are taken as passing
except where the draft makes them fail: RL-3 "gating nothing by itself" and RL-5's
consistency tests failing only on a recording failure.

| kind (reads) | outcome | verdict | infrastructure launch (RK-3 (c)) |
|---|---|---|---|
| G1..G4 (X-01, X-03, X-04) | completed_valid, gate_pass true, frozen checker exit 0, r4 checks pass | PASS | - |
| G1..G4 | any other, including Z-G12 | FAIL: RK-3 (b) (i) never gives PASS_ZL to G1..G4, so the gate stops the lineage by design (RB-4) | not the basis |
| controls_a1 image (X-02) | as G1..G4 | PASS, or FAIL (never PASS_ZL); a failure ends the addendum by design | not the basis |
| fixture4 F-4 (X-04 only) | launched, >= 1 pair collected | PASS if the other items pass | - |
| fixture4 F-4 | Z-F4 (failed / specification_error; zero call) | PASS_ZL | no |
| build (X-07, X-04) | rows ok / refused / failed with >= 1 created child whose pair is collected (completed_valid or failed) | PASS (53 accepts failed; 66-70 pass) | may be present; PASS does not read it |
| build | every launch refused before fork, or every created child without a pair | FAIL (launch_records non-empty, so not PASS_ZL) | **yes: designed stop** |
| cells m = 5 (X-08, X-09, X-10, X-04) | measured / not_measured with >= 1 pair | PASS | may be present |
| cells m = 5 | Z-C5 (completed_valid, or failed / resource_exhaustion with an invalid cell) | PASS_ZL | no |
| cells m = 5 and m = 4 | every target refused before fork, or no created child with a pair | FAIL | **yes: designed stop** |
| cells m = 4 (X-09, X-10, X-04) | measured / not_measured / not_attempted / refused with >= 1 pair (the raw cell always launches) | PASS | may be present |
| aggregate v2 (X-10) | its figures (zero call; exempt at 65) | PASS | no |
| contingency (X-11) | as the kind replaced | as the kind replaced | as the kind replaced |
| every kind read | W-1 | PASS_ZL (RK-3 (b) reads no run_status or failure_class) | no |
| every kind read | **W-2** | **FAIL (several items)** | **no**. RK-3 (c) does not apply; RL-4 refuses the dependant, a stop RK-3 (c) does not name as designed |

### (c) Non-blocking declarations and F-4's `requires`

- **By gate rule and by label text**, F-4 is the only package declared not blocking:
  - the gate rule "F-4": "package 5 runs after the gate and is NOT blocking"
    (trial-plan-v2.json 78; trial-plan-v2-r3.json 506);
  - the label "F-4 secondary fixture, n = m = 4, GF(4111^4), b a square (NOT blocking)"
    (trial-plan-v2.json 263; trial-plan-v2-r3.json 712);
  - the two a1 plans declare no package not blocking.
- **One further text matches the search.** The `content` field of package 3 (G3,
  anchor-identity, `blocking: true`) in trial-plan-v2.json (239) and
  trial-plan-v2-r3.json (688) ends "wall-clock ratio vs 17.01 s reported NON-BLOCKING".
  It declares a reported figure non-blocking, not a package.
- **The boolean field `blocking`** is false on 27 of the 31 packages of each v2-lineage
  plan (every package except G1..G4), and on 10 of the 11 packages of each a1 plan
  (every package except controls_a1).
  - The r3 wrapper reads that field only as "is a gate package" (R-12, 216) and copies it
    into manifest.package (529).
  - The frozen F-4 driver also writes `"blocking": False` into its own raw (v2_driver
    532).
- **The package that names F-4 in `requires`** is build 4111: RUN-GFPN-1ad09b in
  trial-plan-v2.json and RUN-GFPN-c8f179 in trial-plan-v2-r3.json.
  - `cmd_build` and its static callees (`build_poly`, `child_job`, `field_spec`,
    `curve_spec`, `finish`, `_slim`, `Ctx`) contain no reference to a run directory,
    `EXP_DIR`, `ARCHIVED_ANCHOR_RUN`, `resolve_replacement` or a run id.
  - Its builders write to `C.CACHE_DIR` (96), while F-4's builds are not `to_cache`
    (548).
  - **It reads none of F-4's recorded content.**

### RKR-4 reading, as the draft words it

The condition: "(a) every read ... is covered BY NAME by RB-4 or RK-3 (a), or is one RK-3
(a) names as not covered by design; AND (b) for every package kind so read and every
correctly recorded outcome a dependant's frozen logic acts on, the verdict RK-3 (b)
defines is PASS or PASS_ZL, OR the outcome contains an infrastructure launch (RK-3 (c), a
designed stop); AND (c) F-4 is the ONLY package ... that a gate rule or label declares
non-blocking, and the package that names F-4 in `requires` reads none of F-4's recorded
content." NOT A BAR: "X-05, X-06, X-12 and the X-03 reference, as RK-3 (a) names them."

Census finding:
- **(a)**
  - Every read by a command or by the r3 wrapper is covered by name, or is named not
    covered by design.
  - One further read was found, X-13. It is a checker read (a1_check_run 79-84) that
    neither RB-4 nor RK-3 (a) names; it lies outside the reading's worded scope.
- **(b)**
  - Every listed outcome is PASS or PASS_ZL, or is FAIL with an infrastructure launch.
    **The exception is W-2**: an entry refusal before any command, which is FAIL without
    an infrastructure launch.
  - Gate and controls_a1 failures are outside PASS and PASS_ZL by RK-3 (b) (i), and stop
    at RB-4.
  - Whether W-2 is a "correctly recorded outcome a dependant's frozen logic acts on" is
    not decided here (L-13). If W-2 were admitted, the m = 4 package's `_prior_cells`
    would read it as having no m = 5 cell (1013, 1122).
- **(c)**
  - By gate rule and label text, F-4 is the only package declared not blocking.
  - The boolean field `blocking` is false on every non-gate package, as listed above.
  - Build 4111 reads none of F-4's recorded content.

## 6. RKR-6 (RKQ-7): the development world

**(a) preflight, launch and `info`.**
- `preflight` (231-324) and `launch` (423-570) are separate module functions. `main`
  (403-420) calls `launch` only when `preflight` returns no refusal (412-420).
- `launch` reads these values from `info`:
  - `plans`, `plan`, `pk` and `plan_key` (424);
  - `amendment_sha256` (462);
  - `reg1` (565-566).
- `preflight` sets every one of them before it returns, whether or not it recorded
  refusals:
  - `amendment_sha256` at 235-240;
  - `plans` at 245;
  - `plan_key` at 253;
  - `reg1` at 279 (None), and at 286 when the package is not G1;
  - `pk` and `plan` at 323.
- The one exception is the early return at 244 (a plan unreadable), after which `plans`,
  `plan_key`, `pk` and `plan` are unset.
- In the development world, `info['reg1']` is the NOT_EVALUABLE block (158), and
  `launch` writes it into the manifest (565-566). r3_check_run 327-330 then fails on a
  non-G1 development package ("gate.regression_REG-1 not recorded PASS").

**(b) Refusals preflight records in a development world as RK-4 (a) words it.** The
world: redirected RUNS and plan paths, and development plan copies that change only the
package's run id.

| predicate (lines) | controls (G4) | anchor-identity (G3) | controls-a1 |
|---|---|---|---|
| R-1 (234-240) | none | none | none |
| R-2 (257-271) | none (the label is reserved in the copy the redirected plan path names) | none | none |
| R-3 (273-274) | none | none | none |
| R-4, R-5 (276-277) | none | none | none |
| R-6 (278) | none for the r3 wrapper as written (see N-2) | none | none |
| R-7 gate packages (282-284) | none (need_gate false: v2r3, gate_required false) | none (same) | **4 × "R-7 repaired gate package <G> has not run"**: expected |
| R-7 REG-1 (285-287; reg1 153-162) | **"R-7 REG-1 did not pass (NOT_EVALUABLE)"**: expected | same: expected | same: expected |
| R-7 controls_a1 image (288-289) | n/a | n/a | none (the package's own `controls_a1_gate_required` is false) |
| R-8 (290; 199-203) | **requires RUN-GFPN-f5412a: no manifest**: expected | **requires RUN-GFPN-902222: no manifest**: expected | none (`requires` empty) |
| R-9 (292-293) | none | none | none |
| R-10 (295-297) | only if another solver-like process runs: **not in RK-4 (a)'s list** | same | same |
| R-11 (299-307) | none | none | none |
| R-12 (309-312) | none | none | none |
| R-13 (314-322) | none | none | none |
| RB-4 / RL-4 / RK-3 (r4 only) | RL-4 on the `requires` entry: expected | same: expected | RB-4 (b) on G1..G4: expected |

**(c) Reads of the run id by the three frozen commands.**
- **Ctx.__init__ (v2_driver 55-58)** looks up the package and names the directory, in
  controls, anchor-identity and controls-a1 (a1_driver 57).
  - `run_dir()` is GFPN_RUN_DIR (v2_common 97-101).
  - `run_id()` is its basename (104-105).
  - `plan_package(plan, rid)` looks it up in `v2_common.PLAN_PATH`'s plan.
- **v2_driver 59-62** handles contingency runs only.
- **v2_driver 78 (`finish`)** copies the looked-up package, whose `run_id` is the label,
  into raw-result.json.
- **v2_driver 252 → v2_lift 220** writes `"run_id": <label>` into every certificate. It
  is reached by controls (842) and controls-a1 (a1_driver 167). This is neither a lookup
  nor the directory name. v2_verify_independent does not read it.
- The run id reaches the frozen command only as the basename of GFPN_RUN_DIR. The plan it
  is looked up in is the ENTRY process's `v2_common.PLAN_PATH` (r3_entry_v2 45;
  r3_entry_a1 58 via a1_common), not the wrapper process's.

**(d) Redirections the r3 development checks made.** Each is listed by ast in the JSON;
the main ones are these.

| attribute | declared at | redirected at |
|---|---|---|
| r3_run_wrapper `RUNS` | r3_run_wrapper 68 | r3_dv7 481; r3_dv12 156 |
| r3_common `RUNS_DIR` | r3_common 31 | r3_dv7 480; r3_dv12 153 |
| r3_common `PLAN_V2_R3`, `PLAN_A1_R3`, `PLAN_V2`, `RECEIPT_R3_PHASE_A`, `RECEIPT_R3_PHASE_B`, `REG1_REFERENCE_RUN` | r3_common 112-113 and following | r3_dv7 470-473 (setattr at 473); r3_dv12 121-122; r3_dv12 155; r3_dv16 142 |
| r3_common `RECEIPT_V2_PHASE_B` | r3_common 129 | r3_dv7 480; r3_dv12 154 |
| v2_common `LADDER_PATH` | v2_common 35 | r3_dv7 174 (restored at 180), in the toy-ladder builder |
| in the CHILD processes: r3_common `R.*`; v2_common `EXP_DIR`, `LADDER_PATH`, `FIXTURE_N3_JSON`, `FIXTURE_N4_JSON`; a1_common `EXP_DIR`, `RUNS_DIR`, `LADDER_PATH` | - | the shim code r3_dv7 230-231 and 299-300, configured by `R3_TOY_CFG` (cfg_for 393-404; r3_dv12 139-149) |

Replacements the r3 checks also made:
- `W.ENTRY_V2` / `W.ENTRY_A1` → the shim entry (r3_dv7 469; r3_dv12 113);
- `K.FROZEN_LAUNCHER` → the shim checker (r3_dv7 570);
- `W.git_tree_state` → a lambda (r3_dv7 468; r3_dv12 111);
- `W.DRIVER_PYTHONHASHSEED` (r3_dv7 482; r3_dv12 157);
- a tracing wrapper over `v2_solver.run_child` in the child (r3_dv7 301-314).
- They invoked the whole wrapper through `W.main([rid])` (r3_dv7 486; r3_dv12 161).

Notes:
- **N-1.** Redirection inside the wrapper process does not reach the entry child, which is
  a new interpreter (r3_run_wrapper 434, 477). Without a child-side redirection:
  - the entry loads the real plan (r3_entry_v2 45);
  - `Ctx`'s `plan_package` raises KeyError on the label (v2_common 69-73);
  - the outcome is of class W-1.
- **N-2.** DV-18 runs during the r4 stage "before the stage writes its bundle"
  (readbackcover RB-5), that is, before the r4 phase-A archive.
  - The r3 wrapper's R-6 compares its own tree with its phase-A receipt (276-278;
    tree_check 114-139).
  - An r4 analogue would find no receipt and untracked files at that time.
  - The r3 checks handled their own R-6 with a synthetic receipt and a replaced
    `git_tree_state` (r3_dv12 111, 118-122).
  - This is an inference about unwritten r4 code from the r3 base (L-14).
- **N-3.** `reg1()` reads the REG-1 reference through `R.RUNS_DIR` (159), not `RUNS`. The
  candidate G1 is looked up under `RUNS` (156).
- **N-4.** The development package's own frozen checker runs in r3_check_run's child
  (37, 372). It looks the label up in the real r3 plan unless that child is redirected
  too, and would then fail at v2_check_run 45.

**RKR-6 reading, as the draft words it.** The condition: "(a) preflight and launch are
separate functions such that launch can be invoked in a development process after a
recorded preflight, and lists every value launch reads from preflight's `info` and where
each comes from when preflight recorded refusals; (b) in a development world as RK-4 (a)
words it, for `controls`, `anchor-identity` and `controls-a1`, every refusal preflight
records is one of the admission predicates RK-4 (a) lists as expected; (c) the
development label is the ONLY plan value the development copy changes, and no frozen
command reads the run id other than to look up its package and name its directory; and
(d) every in-process redirection RK-4 (a) needs (RUNS, the plan paths, the ladder path)
exists as a module attribute the r3 development checks already redirected, with lines. A
failure of (a)-(d) makes DV-18 infeasible as worded and the draft NOT approvable as
written."

Census finding:
- **(a)**
  - The functions are separate, and launch can be called after a recorded preflight.
  - The values launch reads, and where each is set, are listed above.
  - The recorded REG-1 block in a development world makes r3_check_run 327-330 fail on
    the development package.
- **(b)**
  - Every refusal preflight records for the three commands is one RK-4 (a) lists as
    expected: REG-1, R-8, and the R-7 gate packages.
  - Two predicates can refuse outside that list:
    - R-10, a host-state predicate;
    - the r4 analogue of R-6 at stage time (N-2; inferred, L-14).
- **(c)**
  - As RK-4 (a) words the copy, the development label is the only plan value it changes.
  - The frozen commands read the run id to look up the package and to name the
    directory.
  - **Controls and controls-a1 also write it into every certificate** (v2_driver 252 →
    v2_lift 220).
  - `finish` copies the looked-up package into raw-result.json (78).
- **(d)**
  - RUNS, the plan paths and the ladder path exist as module attributes, and the r3
    development checks redirected them (lines above).
  - The frozen command runs in the entry child process, and the frozen checker in its
    own child. The r3 checks reached both only by replacing `W.ENTRY_V2` / `W.ENTRY_A1`
    and `K.FROZEN_LAUNCHER` with shims that re-apply the redirections from `R3_TOY_CFG`,
    and by replacing `W.git_tree_state`.
  - RK-4 (a) names in-process redirection only. It names neither the child-process
    redirection nor these replacements.

## 7. RKR-7 (informational): readers of the fields RK-1 and RK-2 add

The text scan covered 251 files under `tools/`, `harness/` and the three implementation
trees (combined digest
`e6f55653a95b2f61fbb7ac9ef53a970c825fbdc051a8c356524f4fecaac7b8ca`). It searched for the
names `launch_records`, `child_readback_accounting`, `pair_read_by_parent`,
`readback_from`, `frame_inspection`, `raise_site` and `child_created`. **None of these
names occurs** in any existing file. Every reader below is therefore either unwritten r4
code or reads the file or manifest in general.

| reader | reads | changes what it computes? |
|---|---|---|
| RL-3 collector (r4; not written) | launch records: child_created and the pair; RK-2 adds readback_from and the named lists | YES, by design. RK-1 (a) makes child_created true on P-7; RK-1 (b) adds raise-path records whose pair is copied (P-14c, P-F1) to source (d); "capped children evidenced" counts child_created true |
| frozen v2_check_run 62-70, via `child_rlimit_as_read_back_by_getrlimit` (the RB-2 union with RL-3 (d)) | the de-duplicated pairs | YES where a raise-path pair is the only source: 66-67 then passes and 68-70 compares it (RK-2: "applies to every source, the raise-frame records included") |
| r4 checks: RK-3 (b) (ii), (iii) and RK-3 (c) | whether launch_records is empty; child_created, raised, pair_read_by_parent; RL-3 recorder gaps | new readers, by design (the verdict) |
| REG-1 SE-4 (e): r3_reg1.solver_events_check 171-199, render 321-333 | exists / parses; the top-level flag; S-1 / S-2 events' consistency.ok and counters, by constant key; the whole file quoted | no for the verdict. The verbatim quote grows. RK-1 (b)'s `frame_inspection "not_found"` is an SE-2 (4) violation and would set the flag (a recording failure; RK-6) |
| a1_check_run byte sweep 51-58 | every .json / .yaml / .txt / .log, solver-events.json and manifest.yaml included | no, unless a copied string (refusal_reason with the lock path, v2_solver 168; child_rlimit_report) contains the forbidden id. A hit fails the package |
| r3_check_run.events_file_integrity 153-158 | whole-file sha256 on both sides | no |
| r3_check_run.events_file_epsilon 161-185 | constant keys | no |
| r3_check_run.forbidden_id_keys 189-211 | top-level keys only | no (the new fields are nested) |
| r3_check_run.forbidden_id_sweep 214-224 | five files; neither solver-events.json nor manifest.yaml | no |
| r3_check_run.sc4_accounting 128-150 | raw-result.json and health reports | no |
| r3_run_wrapper.solver_events_block 381-400; consistency_flag 573-579 | constant keys; whole-file sha256 | no (the recorded sha256 changes with the bytes) |
| frozen commands, aggregates, a1 phase_b_check | none (successor census RLR-6) | n/a |

## 8. Method limits

**Carried from the earlier censuses, where they still apply:**
- **L-1.** RL-1 still covers a raise in the CALLER after run_child returned. A raise INSIDE
  run_child is now read under RK-1 (b), in the RKR-1 table.
- **L-2.** The ERR setrlimit branch takes no pair. It is now a NOT A BAR class of RKR-1.
- **L-3.** Which path occurs is a run-time fact (RKL-3).
- **L-4.** Grandchildren were not examined (RKL-1).
- **L-5.** controls-a1, fixture4, build, cells and aggregate(-a1) never ran under r3. No
  r4 code exists, so RK-1..RK-4 are read as worded.
- **L-6.** Superseded, as a reading of RL-1, by RK-1. RK-1 as worded still records
  child_created false on P-16, and on P-F2 after P-14a or P-16.
- **L-7.** Closed as worded: RK-1 (a) defines key presence.
- **L-8.** RKR-2 is read on the r3 entries' closure. The r4 closure is checked by DV-18 (h)
  at stage time.
- **L-9.** RK-4 (b) names 1073741831. Development admission is read under RKR-6 on the r3
  base.
- **L-10.** RKR-3 and RKR-4 (b) are static readings of the checkers. No package was run.

**New limits:**
- **L-11.** Interpreter behaviour is taken from the language's documented behaviour and
  from bytecode compiled here from source text, not from interpreter source. This covers
  a C-level call raising after its side effect (MemoryError converting a new pid), and
  asynchronous exceptions delivered at bytecode boundaries.
- **L-12.** The fork-child path P-C is not traced beyond run_child.
- **L-13.** Whether the wrapper-recorded outcomes W-1 and W-2 are "correctly recorded
  outcomes" in the draft's sense is not decided. They are listed with their items and
  verdicts.
- **L-14.** RKR-6 reads the r3 wrapper as the base of the r4 wrapper. Predicates the r4
  wrapper adds or re-points, such as its R-6 at stage time, are inferred, not read.

## 9. Completion gate

- **RKQ-2 integrity** passed before any reading of a bound input, and is recorded with
  full hashes (section 1 and the JSON).
- **RKR-1** is reported per path, covering every return and every explicit or implicit
  raise point. It states what RK-1 records on each, and states the reading as the draft
  words it.
- **RKR-2** is reported with the definition count, the first lines, the rebinding scan,
  and the reading.
- **RKR-3** is reported per package kind and per zero-call outcome, with every failing
  item verbatim, and the reading.
- **RKR-4 (a), (b) and (c)** are reported per read, per package kind and outcome, and per
  non-blocking declaration, with the reading.
- **RKR-6 (a)-(d)** are reported with lines, with the reading. **RKR-7** is reported.
- **Scope (RKQ-1):**
  - no solver, valgrind, callgrind_annotate, gp, Sage or builder child;
  - no import of a scanned-tree module (guard 0 / 0);
  - no run package;
  - nothing written outside
    `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/`, apart from
    disclosed transient scratch under `<scratchpad>/rkcensus/`;
  - no frozen, preserved or archived byte changed: (g) is empty.
  - 16 pre-existing `__pycache__` directories, all ignored by git, are unchanged. Two of
    them are under the v1 trees `experiments/EXP-GFPN-05ff43/implementation/` and
    `experiments/EXP-GFPN-726eb2/implementation/`, dated 2026-09-21..23. None was
    added, and no `.pyc` is newer than the card.
- **Citations:** 282 checked against the file text, with 0 failures (RKR-1 88, RKR-2 2,
  RKR-3 71, RKR-4 16, RKR-6 95, RKR-7 10).
- **Output self-check:**
  - the JSON carries none of the eight forbidden task ids, which are read at run time
    from the card's RKQ-9 text and not embedded;
  - the JSON does not carry the scratch path.
- **Name check (RKQ-9):**
  - Word list: a scratch file outside the repository, sha256
    `9ef26729cba8985d231fe45f67dc609ec8562d872f7e4b65188306bc5ee0b136`.
  - Script self-check over the JSON and `rk_check.py`: 2 hits.
  - Shell check with the same word list over all three deliverables, this file included:
    5 hits.
  - **Every hit is the dispatcher-specified inference-block key `bedrock_used`**: once in
    the JSON, once in `rk_check.py`, and three times in this file (the inference block in
    section 0, this line, and deviation 5). There is no other hit.
- No D or degree is reported as a result, and no approval recommendation is made.

## 10. Deviations and disclosures

1. **Reading before integrity.** These were read before the integrity checks, as the card
   allows ("may be read first, as definitions"):
   - the card, the executor contract, the runtime core;
   - the draft, DEC-20260924-a789e1, CORR-20260924-217903 and CORR-20260924-b3cd63.

   The archive receipts and DEC-20260924-e52eec's `bound_hashes` were also read, to
   perform the checks; they are the binding records, not bound inputs. No bound source
   code, plan, package or earlier-census file was read before the scratch pre-check
   passed.
2. **Integrity ran four times**: as the scratch pre-check
   (`<scratchpad>/rkcensus/pre_integrity.py`, 858 hashes plus (g)), and as phase 1 of
   each of the three `rk_check.py` runs. Every run passed.
3. **`rk_check.py` ran three times.**
   - Development runs 1 and 2 wrote to `<scratchpad>/rkcensus/`; the third run wrote
     `readbackclose-census.json`. Every run completed every reading, with guard 0 / 0 and
     0 citation failures.
   - Before run 1, two no-op fragments were removed and one disposition text was
     reworded.
   - After run 1:
     - the binding helper counted subscript stores (`rec[...] = ...`) as bindings of
       `rec`; it now counts name bindings only;
     - a non-constant `setattr` name is now resolved from an enclosing loop over a
       literal (v2_field 55);
     - four scan lines that are not reads of another package were mapped;
     - the ladder b-square read and the G3 `content` text were added.
   - The final script is byte-identical before and after the run that wrote the JSON
     (sha256 below).
4. **Dispositions were read by hand**, as in both earlier censuses. This covers:
   - the path table;
   - the zero-call outcome catalogue and the per-item disposition texts;
   - the development-world predicates;
   - the reader table.

   The script re-checks every cited line (282 checks) and derives these mechanically:
   returns, raises, handlers, bindings, bytecode, the closure rebinding scan, the checker
   item inventory, the plan text scan, the run-directory read scan and the redirection
   inventory.
5. **Name words.** The dispatcher specified the inference-block field key `bedrock_used`
   (RKQ-9 dispatch facts), and it is recorded as specified. It contains a service-product
   word that the scratch word list includes, so the checks count its occurrences: 2 in
   the script's own scan of the JSON and the script, and 5 across the three deliverables
   (section 9). The word list is held only in scratch; the deliverables carry only its
   sha256 and the hit counts.
6. **`tools/` and `harness/` were read as text only.** Their module names are in the
   guard's refused set.
7. **Shell utilities and scratch.** Uncapped, read-only shell utilities and short
   `python3 -B` data and ast readers were used (section 0). None is a solver, valgrind,
   gp, Sage or builder child. All scratch is under `<scratchpad>/rkcensus/`: the
   pre-check, the word list, two development JSONs and two `__pycache__` listings.
8. **This file** was written by the executor from `readbackclose-census.json`. It is not
   generated by the script.

## 11. Deliverables

- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/rk_check.py`, sha256
  `00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.json`,
  sha256 `9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md`,
  this file. Its sha256 is given in the executor's return.
