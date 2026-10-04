# Successor census: EXP-GFPN-05ff43, TASK-20260924-cab04e

This is the zero-run, zero-solve successor census for the DRAFT
AMD-EXP-GFPN-05ff43-20260924-readbackfull. The draft is not approved. The census was
ordered by DEC-20260924-650068. Its card is
`ledger/handoffs/TASK-20260924-cab04e.yaml` (RFQ-1..RFQ-9), and it is archived by
TASK-20260924-ddfb69.

**What the census does.** It computes the draft's `pre_approval_readings`, in the
draft's order: RLR-5, RLR-1, RLR-2, RLR-3, RLR-4, RLR-7 and RLR-6.

**What the census is not.**
- These are observations only.
- Nothing here is evidence about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT.
- No D or degree is reported as a result.
- Nothing here is an approval recommendation. For each reading, the census states the
  draft's condition and what it found. The approval act applies the reading.

**Files.**
- Machine-readable record: `readbackfull-census.json`.
- Check script, exactly as run: `rf_check.py`.
- Every number below is copied from `readbackfull-census.json`.
- The method reuses the archived census (TASK-20260924-bf5724, archived by
  TASK-20260924-a01341):
  - its static call graph;
  - its capped-child instance table I-01..I-26, with every cited line re-checked;
  - its guard;
  - its integrity pattern.

## 0. Run record

| item | value |
|---|---|
| task / card | TASK-20260924-cab04e / `ledger/handoffs/TASK-20260924-cab04e.yaml` |
| dispatch | `/run EXP-GFPN-05ff43 under TASK-20260924-cab04e`. Lane claim `coordination/goals/GOAL-GFPN-380702/batches/BATCH-e409ca/claims/TASK-20260924-cab04e.1.claim.json` (owner executor, epoch 1, ttl 600 min, expires 2026-09-25T01:11:44Z). The dispatcher holds the claim and releases it; this task did not touch it |
| repository HEAD | 6f526762189108b13b459195960bf616ebf2723b (the claim commit). The tree was clean at dispatch. At the final run the only status line was `?? experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py` |
| DP-1 (as dispatched) | Ledger archive TASK-20260924-833cde committed as ee749081e56eea6e7fa3841ad90e2dc1d61fd341 (receipt backfill 47393b511); the post-commit verifier accepted it; pushed; PR #1419 open. The addendum_sha256 was read from `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-833cde/ledger-receipt.json` (section 1 (a)) |
| DP-2 (as dispatched) | BATCH-e409ca revision 310246170 appended this task (queued); `tools/research_dispatch.py --claims refs` and `tools/validate_dispatch_reference.py` both exit 0 |
| DP-5, re-checked before any write | `runs/` holds 54 run directories plus the file `.gitkeep`. There is no `dev-evidence/readbackfull-census/`, no `implementation-v2-r4*`, no `trial-plan-v2-r4.json` and no `trial-plan-v2-a1-r4.json`. The script re-checks this at run time (`dp5_recheck`): 54 directories, no r4 path |
| final script run | 2026-09-24T15:34:48Z to 15:34:53Z UTC (4.775 s). Command: `PYTHONDONTWRITEBYTECODE=1 python3 -B rf_check.py --out readbackfull-census.json`, cwd `/tmp`, Python 3.11.15 |
| run packages created | 0 |
| msolve, valgrind, callgrind_annotate, gp, Sage or builder children | 0 |
| scanned-tree modules imported | 0 |
| network | not used |
| files read by the final run | 109, each with sha256 in `files_read_sha256`. Also a text scan of 215 files under `tools/` and `harness/`, recorded as one combined digest in `RLR-6.tools_and_harness_scan` |
| wall_clock_seconds 21600 (advisory) | not reached |

**Inference block (RFQ-9).**
- requested_policy: executor-implementation
- resolved_model_id: null. None was supplied by the dispatching session, and none is
  invented.
- fallback_used: false
- bedrock_used: false. Amazon Bedrock is prohibited.

This is not a security statement. The JSON's `output_self_check` finds none of the
eight forbidden task ids and no model, runtime or vendor word.

**Dispatcher memory guard (DP-4), verbatim as dispatched:** pid 875, a bash loop
(scratchpad memguard.sh) that kills the largest-RSS msolve/gp/python3 process when
MemAvailable < 2621440 kB (about 14.2 GB in use on this 16481980 kB host, swap 0, 4
CPUs). The task needs little memory and runs no solver.

**Child processes started by this task.** No solver, valgrind, callgrind_annotate, gp,
Sage or builder child was started.

The git children, all read-only:
- In the shell, before the pre-check:
  - `git rev-parse HEAD`
  - `git status --porcelain --untracked-files=all`
- The scratch pre-check `<scratchpad>/rfcensus/integrity_precheck.py`, run once:
  `git -C /home/user/crypto-autoresearcher diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
- Each of the four runs of `rf_check.py` (phase 1 only):
  1. `git -C /home/user/crypto-autoresearcher diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
     (exit 0, empty)
  2. `git -C /home/user/crypto-autoresearcher ls-files -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
     (a pathspec sanity check; 92 files)
  3. `git -C /home/user/crypto-autoresearcher rev-parse HEAD`
  4. `git -C /home/user/crypto-autoresearcher status --porcelain --untracked-files=all`
- In the shell, `git -C /home/user/crypto-autoresearcher status --porcelain --untracked-files=all`:
  - twice during the work;
  - once as the final check, reported in the executor's return.

Other shell children were read-only utilities:
- `ls`, `find`, `grep`, `sed`, `cat`, `wc`, `awk`, `head`, `diff`, `sha256sum`, `date`;
- `python3 --version`;
- short `python3 -B -c` readers of JSON and YAML data (plans, receipts, `ladder.json`,
  the census JSON). None of them imported a module of a scanned tree.

**The in-process guard (RFQ-1).**
- It is installed after the integrity phase with `sys.addaudithook`.
- It refuses:
  - the launch events `subprocess.Popen`, `os.system`, `os.exec`, `os.posix_spawn`,
    `os.spawn`, `os.fork`, `os.forkpty`, `pty.spawn` and `os.startfile`;
  - any import of 258 module names: every `.py` file of the six implementation trees,
    the Sage comparator, the k5k7 scratch, `tools/` and `harness/`.
- No name collides with a standard-library module (checked before the first run).
- It was self-tested with `sys.audit`. The self-test refused `subprocess.Popen` and
  `v2_solver`.
- **Attempt counts in the final run: launch 0, import 0.** The three development runs
  also counted 0 and 0.

## 1. RLR-5: integrity (RFQ-2), applied first

All checks passed before any reading. They passed twice: once in the scratch
pre-check, and again as phase 1 of every `rf_check.py` run.

| check | result |
|---|---|
| (a) readbackfull draft | computed `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1`, equal to `addendum_sha256.sha256` of `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-833cde/ledger-receipt.json`, whose `path` field names the same file. In-file `status: draft`, `approved_by: null`, `approval_decision: null`: PASS |
| (b) readbackcover | computed `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e`, equal to the card value: PASS |
| (c) nine VA-1 files vs DEC-20260924-e52eec `bound_hashes` | 9 / 9 equal: v1_to_v2_reanchor_and_arm_iii `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3`; v2_addendum_rung31 `2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c`; paristack `856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7`; seedresolve `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81`; solverevent `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f`; healthresolve `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d`; launchcover `c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447`; consumercover `a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0`; valueclose `877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1`: PASS |
| (d) archived census vs the TASK-20260924-a01341 receipt | readback-census.md `2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3`; readback-census.json `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4`; rb_check.py `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64`: 3 / 3 equal: PASS |
| (e) TASK-20260924-f1fb0e | snapshot receipt 22 / 22 and post-run receipt 801 / 801 paths hash to their recorded values: PASS |
| (f) implementation-v2/ vs TASK-20260923-0fa03f; implementation-v2-a1/ vs TASK-20260923-4ff597 | 14 / 14 and 12 / 12 bound paths equal; no unbound `.py` file in either tree: PASS |
| (g) `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- .../implementation* .../trial-plan-*.json` | exit 0, empty output: PASS |

**Scope of (f).** Every bound path was checked, which is a superset of the files read.
Of the 65 implementation and plan files the final run read:
- every file bound by the 0fa03f, 4ff597 or f1fb0e phase-A receipts equals its recorded
  hash;
- the r1 / r2 development files, which those receipts do not bind, are covered by (g).

## 2. RLR-1 (RFQ-3): every capped child, on every branch, and its sources

### (a) `v2_solver.run_child` and `_run_child_locked`: every path

The script checks two facts:
- **Return statements found by ast:** `run_child` 155, 160, 165, 169, 171;
  `_run_child_locked` 225, 232, 308. These equal the table.
- **Explicit `raise` statements:** none.
- The child process never returns to Python: it ends in `exec` or `os._exit` (208).

The docstring says "never raises for child failures" (151). The pair is set at 227.

| id | branch | child created | returns or raises | returned record carries `rlimit_as_child_getrlimit` | lines |
|---|---|---|---|---|---|
| P-1..P-4 | refused_before_fork: invalid cap; driver RSS > 1 GiB; another solver-like process; lock held | no | returns (refused_to_start) | no | 153-155, 158-160, 162-165, 167-169 |
| P-5 | raised, before fork: `open(/proc/self/status)`, `os.listdir(/proc)`, `open(LOCK_PATH, "a+")`, `os.pipe`, `os.fork` | no | RAISES | no record | 156, 161, 101, 178, 181 |
| P-6 | ERR setrlimit: the child writes `ERR setrlimit ...` and exits 97 | yes | returns (refused_to_start; `child_rlimit_report`) | **no** | 193, 195, 220-225 |
| P-7 | pre-setrlimit child failure: `os.chdir`, `os.open(stdout/stderr)` or `os.dup2` raises in the child; the except at 206 swallows it; exit 99; the parent reads an **empty** report | yes | returns (refused_to_start `child could not set RLIMIT_AS: `; `child_rlimit_report ''`) | **no** | 188, 206, 208, 224 |
| P-8 | no_meta: pre-exec read-back mismatch (soft != cap) | yes | returns | yes (227 precedes 228-232) | 227, 228, 232 |
| P-9 | no_meta: hard-only mismatch (see below) | yes | returns (via P-12) or RAISES (P-14): a race | yes / not returned | 200, 228, 236 |
| P-10 | ok, without perf | yes | returns | yes | 284, 288, 308 |
| P-11 | ok, with perf | yes | returns unless `_perf_read` raises (P-15) | yes | 280, 281, 308 |
| P-12 | no_meta: memory_exhausted / crash / nonzero exit (includes an exec failure, exit 99) | yes | returns | yes | 304, 308 |
| P-13 | no_meta: timeout | yes | returns | yes | 263, 287, 308 |
| P-14 | raised, after fork: `os.write(go_w)` raises BrokenPipeError when the child exited after reporting OK and before the go byte (P-9, or a signal in that window). Also raise points: `os.read` 214; `os.wait4` 223, 230, 244 | yes | **RAISES**: the record, with the pair already set at 227, is not returned | not returned | 236, 214, 244 |
| P-15 | raised, after the child is reaped: `_perf_read` (`os.read` / `struct.unpack`), only with `count_instructions` true and an opened counter | yes | **RAISES** | not returned | 141, 281 |

**P-9 in detail.** The case is soft == cap and hard != cap:
- The child exits 98, because line 200 tests both soft and hard.
- The parent tests soft only (228) and continues.

**Which launch sites can reach P-15.** Only `v2_driver.py:166`, which omits
`count_instructions` (default true, v2_solver.py 150). The other five reachable launch
sites pass `count_instructions=False`.

### (b) Static call graph and instance coverage

The call graph is the archived census's: runtime modules parsed with ast; SE-3 in both
entries; HR-3 in the a1 entry. It is re-run on the same bytes, with RL-1 placed over
`run_child` as a recording pass-through.

Paths to a capped launch, per command:

| command | paths |
|---|---|
| fixture | 16 |
| anchor-identity | 10 |
| controls | 17 |
| fixture4 | 5 |
| build | 1 |
| cells | 5 |
| aggregate | 0 |
| controls-a1 | 10 |
| build (a1) | 1 |
| cells (a1) | 5 |
| aggregate-a1 | 0 |

- **Coverage:** 0 paths not covered by an instance, and 0 instances without a path.
- **No further capped launch was found.** The launch scan of every scanned tree finds 12
  `run_child` call sites. The 6 reachable ones:
  - v2_driver.py 101, 166 and 650;
  - v2_solver.py 517;
  - a1_health.py 147;
  - a1_pari.py 96.
- The other 6 are in development checks and are reachable from no command:
  - r1_devchecks 177 and r1_devchecks_more 75;
  - r2_devchecks 186 and r2_devchecks_more 75;
  - r3_devchecks 190 and r3_devchecks_more 80.
- `_run_child_locked` is called only at v2_solver.py 171, inside `run_child`.
- The 7 statically reachable, never-launched callgrind paths are carried unchanged:
  v2_driver 565, 693, 711, 786, 787, 841 and a1_driver 166. In each the caller passes
  no `callgrind_timeout`.

### (c) Sources per instance and branch, under RB-1, RB-2, RL-1, RL-2 and RL-3 as worded

**Columns.**
- `RL-1` means an RL-1 launch record, which is the RL-3 (d) source.
- `RL-2` means an RL-2 pass-through record, which is the RL-3 (e) source.
- RL-1 counts only where RLR-2 finds the call site intercepted. It finds all 6
  reachable sites intercepted (section 3).

**Carried branches.** A branch "carried" from the archived census is one on which a
child is created and `run_child` returns a record carrying the pair (P-8, P-10..P-13).
The census's ok, refused_meta, no_meta, recorded, ssf_earlier, passthrough and
any_outcome branches are all of this kind.

| id | launch | carried branches, with sources |
|---|---|---|
| I-01 fixture builders | v2_driver:101 | ok: RB-2(a), RB-2(b), RL-1; refused_meta: RB-2(a), RL-1; no_meta: RB-2(a), RL-1 |
| I-02 fixture raw_grid | :101 | ok: RB-2(b), RL-1; refused_meta: RB-2(a), RL-1; no_meta: RB-2(a), RL-1 |
| I-03 fixture S-1 | :166 | recorded: RB-2(a), RB-1, RL-1; ssf_earlier: RB-1, RL-1 |
| I-04 fixture S-3 | v2_solver:517 | ok solve with callgrind_timeout: RB-2(a), RL-1 |
| I-05 fixture4 builders | :101 | ok: RB-2(a), RB-2(b), RL-1; refused_meta / no_meta: RB-2(a), RL-1 |
| I-06 fixture4 S-1 | :166 | recorded: RB-2(a), RB-1, RL-1; ssf_earlier: RB-1, RL-1 |
| I-07 Sage comparator | :650 | any outcome: RB-2(a), RL-1 |
| I-08 anchor_S4 builder | :101 | ok: RB-2(a), RB-2(b), RL-1; no_meta: RB-2(a), RL-1 |
| I-09 anchor gb_only (4) | :166 | passthrough: RB-2(a), RL-1, **RL-2** |
| **I-10 anchor_comparator_system** | :166 | passthrough: **RL-1, RL-2** (no RB source) |
| I-11..I-14 controls builders | :101 | ok: RB-2(b), RL-1; **no_meta: RL-1** |
| I-15 controls builders | :101 | ok: RB-2(b), RL-1; **refused_meta: RL-1; no_meta: RL-1** |
| I-16..I-18 controls S-1 | :166 | recorded: RB-1, RL-1; ssf_earlier: RB-1, RL-1 |
| I-19 build | :101 | ok / refused_meta / no_meta: RB-2(a), RL-1 |
| I-20 cells raw_grid | :101 | ok: RB-2(b), RL-1; **refused_meta: RL-1; no_meta: RL-1** |
| I-21 cells S-1 | :166 | recorded: RB-2(a), RB-1, RL-1; ssf_earlier: RB-1, RL-1 |
| I-22 cells S-3 | v2_solver:517 | ok solve with callgrind_timeout: RB-2(a), RL-1 |
| I-23 gp | a1_pari:96 | any outcome: RB-2(a), RL-1 |
| I-24 (first, retry_seed2; reinvocation variants not executed) | a1_health:147 | recorded: RB-1, RL-1; ssf_earlier: RB-1, RL-1 |
| I-25 controls-a1 builders | :101 | ok: RB-2(b), RL-1; **refused_meta: RL-1; no_meta: RL-1** |
| I-26 controls-a1 S-1 | :166 | recorded: RB-1, RL-1; ssf_earlier: RB-1, RL-1 |

**What changed from the archived census.** Eleven carried branch rows had no source
under RB-1 and RB-2 as worded:
- I-10 passthrough;
- I-11..I-14 no_meta;
- I-15, I-20 and I-25, each on refused_meta and no_meta.

Each now has RL-1 (and I-10 also has RL-2).

**Run_child-level branches added for every instance** (P-rows of (a)):

| branch | child created | sources | what RL-1 as worded records |
|---|---|---|---|
| refused_before_fork (P-1..P-4) | no | no child (NOT A BAR) | child_created false; pair "absent" with refusal_reason |
| raised before fork (P-5) | no | no child | raised: <type>; child_created false |
| ERR setrlimit (P-6) | yes | **NONE**; no pair is ever taken; NOT A BAR as the draft words it | pair "absent" with `child_rlimit_report` and refusal_reason; child_created true |
| pre-setrlimit child failure (P-7) | yes | **NONE**; no pair is ever taken | pair "absent"; `child_rlimit_report` is present with the value `''`; child_created true only if RL-1 (c)'s "carries" is a key-presence test (L-7) |
| raised after fork (P-14; and P-15 at v2_driver:166) | yes | **NONE** | raised: <type>; pair "absent"; **child_created false**, because RL-1 (c) tests the RETURNED record and there is none (L-6) |
| raised in the frozen caller after `run_child` returned (archived L-1) | yes | RL-1 | the launch record is appended before the return reaches the caller |

### RLR-1 reading, as the draft words it

The draft's condition: "approvable as written ONLY IF, for every capped-child instance
of the archived census's RBR-1 table (I-01..I-26 with the I-24 variants) and every
further capped launch the successor census finds, and for EVERY branch on which a
child is created, at least one read-back source exists under RB-1, RB-2 (as
incorporated), RL-1, RL-2 and RL-3 as worded. ... A created child with NO source on
some branch makes the draft NOT approvable as written. NOT A BAR: the ERR setrlimit
branch (no pair is ever taken; RL-1 records "absent" and RL-3 names it);
grandchildren; refused_before_fork (no child); a child found in two sources."

Census findings, per reachable run_child call site and per branch:
- **Sites and branches with a source.** All six reachable call sites are intercepted.
  On every branch on which a child is created and `run_child` returns, the returned
  record carries the pair (P-8, P-10..P-13), and every instance has at least RL-1 /
  RL-3 (d) there.
- **Created-child branches with NO source under RB-1, RB-2, RL-1, RL-2 and RL-3 as
  worded:**
  1. **ERR setrlimit (P-6).** This applies to every launched instance: I-01..I-23,
     I-24-first, I-24-retry_seed2, I-25 and I-26. The two I-24 reinvocation variants
     carry the same row and are not executed. The draft names this branch NOT A BAR.
  2. **Pre-setrlimit child failure (P-7).** Every launched instance, as in item 1.
     - A child is created.
     - `run_child` returns a record with an empty `child_rlimit_report` and no pair.
     - The draft's NOT A BAR names "the ERR setrlimit branch"; this branch is a
       different report ('' rather than 'ERR setrlimit ...').
  3. **Raised after fork (P-14).** Every launched instance. P-15 applies in addition at
     the S-1 instances I-03, I-06, I-09, I-10, I-16, I-17, I-18, I-21 and I-26.
     - A child is created.
     - `run_child` raises, and no record reaches RL-1.
     - RL-1 as worded records it with pair "absent" and child_created false.
     - The draft's NOT A BAR does not name a raise after fork.
- **How reachable these three are.** The approval act rules on them; the census states
  the conditions, all static (L-3):
  - P-7 needs a child-side `os.open`, `os.chdir` or `os.dup2` failure.
  - P-14 needs the child to exit between its OK report and the go byte. That happens
    either with getrlimit returning a hard value different from the one setrlimit just
    set (P-9), or with a signal in that window.
  - P-15 needs an opened perf counter.
- **Not bars as worded:** refused_before_fork and raised before fork create no child.
  Grandchildren (L-4) were not examined.

## 3. RLR-2 (RFQ-4): how each call site resolves `run_child`

| file:line | enclosing function | expression | resolution form | binding of the base name | intercepted by RL-1 |
|---|---|---|---|---|---|
| v2_driver.py:101 | child_job | `V.run_child` | module-attribute lookup at call time | `V` bound only by `import v2_solver as V`, module level, line 38 | yes |
| v2_driver.py:166 | solve | `V.run_child` | module-attribute lookup at call time | same (38) | yes |
| v2_driver.py:650 | cmd_anchor_identity | `V.run_child` | module-attribute lookup at call time | same (38) | yes |
| v2_solver.py:517 | callgrind_instructions | `run_child` | module-global lookup inside v2_solver | no local, argument or module-level rebinding of `run_child` | yes |
| a1_health.py:147 | run_system | `V.run_child` | module-attribute lookup at call time | `import v2_solver as V`, line 48, only binding | yes |
| a1_pari.py:96 | curve_facts | `V.run_child` | module-attribute lookup at call time | `import v2_solver as V`, line 24, only binding | yes |

The 6 development-check sites (section 2 (b)) use `V.run_child`, with `V` bound by
function-level `import v2_solver as V`. None is reachable from a command.

**Import-time captures.** The capture search looks for every non-call reference to
`run_child` or `_run_child_locked` in every scanned tree: Attribute, Name or string
constant. It finds 2, both string constants in development checks:
- `r2_devchecks_more.py:506`, a regex-pattern key in `dv11`;
- `r3_devchecks_more.py:564`, the `LAUNCH_CALLEES` tuple.

Neither module is in either entry's import closure. There is:
- no binding of the frozen function to another name;
- no default argument, container, closure or class attribute holding it;
- no `functools.partial` over it.

**`from v2_solver import` statements:** none, in any scanned tree. Every
`import v2_solver` is `as V`:
- at module level in v2_driver 38, a1_health 48 and a1_pari 24;
- at module level in the wrappers' own processes: v2_run_wrapper 40, a1_run_wrapper 52,
  and the r1 / r2 / r3 run wrappers;
- at function level in development checks.

**Import closure of the r3 entries** (the r4 entries do not exist; L-8):

| entry | modules |
|---|---|
| `r3_entry_v2` | r3_common, r3_resolve, v2_common, v2_driver, v2_arms, v2_child, v2_field, v2_lift, v2_scoring, v2_solver, v2_verify_independent |
| `r3_entry_a1` | the same, plus a1_common, a1_driver, a1_health, a1_pari, a1_reading |

External imports are the standard library, flint, numpy, yaml and cypari2.

**Dynamic-import words in the closure:** only `r3_common.py:367`,
`import importlib.metadata as md`, used for version lookup. Every other hit is:
- in a development check;
- or in a shell-command string of a wrapper process (a1_run_wrapper 281,
  r3_run_wrapper 452).

**Module identity.** The entries' `sys.path` directories hold exactly one
`v2_solver.py` (implementation-v2/):
- implementation-v2-r3 is inserted at r3_entry_v2 27;
- implementation-v2 at r3_entry_v2 43, r3_entry_a1 55 and a1_common 25;
- implementation-v2-a1 at r3_entry_a1 56 and a1_common 27.

The a1 entry refuses unless `a1_driver.C` and `a1_driver.D` are the imported module
objects (r3_entry_a1 76-79). `r3_resolve` stores the `v2_solver` MODULE object
(`_STATE["v2_solver"]`, 435) and uses it only for `parse_msolve_log` (340).

**Launches before install.** No capped launch is reachable from module-level code at
import. The one module-level path, `a1_health.main` at 297, sits under
`if __name__ == "__main__":` and does not run when the file is imported.

**Other launches that set RLIMIT_AS.** The setrlimit sites in the scanned trees are:
- `v2_solver.py:193`, inside `run_child`;
- `implementation/symmetrize.py:396`, in v1 `run_msolve._limit`. It is not in either
  closure.

Under `tools/` and `harness/` the text scan finds:
- `tools/audit_process.py` 33-36;
- `tools/experiment_execution.py` 347;
- `harness/ctrl_valueshuffle.py` 841;
- `harness/run_blocknull.py` 2457;
- `harness/run_fullgroup.py` 1920.

No `tools/` or `harness/` module is in either entry's closure. The r3 run wrapper
launches the entry with `subprocess.run` (r3_run_wrapper 477) and sets no RLIMIT_AS.

**RLR-2 reading, as the draft words it.** The draft's condition: "approvable as written
ONLY IF every reachable run_child call site (the archived census's six ... and any
further one the successor census finds) resolves run_child at CALL time through the
module attribute v2_solver.run_child (an attribute lookup on the module object, or a
global-name lookup inside module v2_solver), so that RL-1's replacement intercepts it;
AND no module either r4 entry imports binds the frozen run_child object to another
name, default argument, container, closure or class attribute before the entries
install RL-1 (an import-time capture). A call site that is not intercepted makes the
draft NOT approvable as written."

Census finding:
- The six reachable call sites are the only ones. Five use an attribute lookup on the
  module object bound only by `import v2_solver as V`. One uses a global-name lookup
  inside `v2_solver`.
- The census names **no call site that is not intercepted** and **no import-time
  capture** in any module the r3 entries import.
- The finding is scoped to the r3 entries and their closure. The r4 entries do not
  exist (L-8).

## 4. RLR-3 (RFQ-5): pass-through calls and the SC-4 `-g` exclusion

**gb_only S-1 calls any command reaches.** Two, both in `anchor-identity`:
- `v2_driver.py:693`, 4 calls (anchor_comparator_random, anchor_v2_t0..t2);
- `v2_driver.py:711`, 1 call (anchor_comparator_system).

No other call carries a `gb_only` keyword except `V.msolve_argv(..., gb_only=gb_only)`
at 165 and 209 inside `solve`.

**Fields returned at each pass-through call.** `v2_driver.solve` sets two fields before
every return (the return statements are at 186, 189 and 214):
- `res["solver"] = _slim(rec)` at 167. `_slim` copies `rlimit_as_child_getrlimit` when
  the record carries it (150-154).
- `res["threads_executed"]` at 169.

The gb_only return is at 187-189, after the refused_to_start return at 184-186. The r3
pass-through (`r3_resolve.py` 382-387) counts the call, calls the captured original and
returns the same object unchanged.

So at each of the 5 calls:
- `result["solver"]["rlimit_as_child_getrlimit"]` is present whenever `run_child`'s
  record carries the pair (P-8..P-13). It is absent on P-1..P-4, P-6 and P-7, where RL-2
  records "absent".
- `result["threads_executed"]` is always present.

**SC-4 `-g` exclusion.**
- `msolve_argv` appends `["-g", "1"]` when gb_only (v2_solver.py 333).
- The carried SC-4 selection skips every raw solve record whose argv contains `-g`
  (r3_check_run.py 136, inside the loop at 134).
- S-2 argv is never gb_only (a1_health.py 144).
- RL-2's own text cites the exclusion (draft 268).

**RLR-3 reading, as the draft words it.** The draft's condition: "approvable as written
ONLY IF (a) every gb_only S-1 call any command reaches returns to the SE-3 entry a
result carrying result["solver"] with the pair and result["threads_executed"] ..., and
(b) the carried SC-4 selection excludes every `-g` argv, so that no pass-through record
can become an SC-4 row, and RL-1..RL-3 change no wrapped call's enumeration (archived
census RBR-2 carries over)."

Census finding:
- (a) holds from code at the 5 calls on every branch on which the child's record
  carries the pair. On P-1..P-4, P-6 and P-7 the frozen record carries none, and RL-2
  records "absent".
- (b) holds: the exclusion is at r3_check_run.py 136.
- Launch and pass-through records are held under their own keys. They are not among
  RB-3's worded sources (attempt records, raw solve records, health reports).

## 5. RLR-4 (RFQ-6): cross-package reads and planned outcomes

### (a) Every read of another package's recorded result

The reads are by a command of either r3 plan or by `r3_run_wrapper.py`.

| id | reader: file, lines, function | package kind read | file and field | covered by |
|---|---|---|---|---|
| X-01 | r3_run_wrapper 176-181, r7_gate_packages (via _raw 97-104) | G1..G4 | raw-result.json run_status, gate_pass | RB-4 (G1..G4 (a) and (b)) |
| X-02 | r3_run_wrapper 190-196, 288, r7_controls_a1_image | the controls_a1 image | raw-result.json run_status, gate_pass | RB-4 (addendum packages 2-11) |
| X-03 | r3_run_wrapper 153-162, 285, reg1 -> r3_reg1.compare (175) | G1, as REG-1 candidate, for every package after G1; RUN-GFPN-ac4487 as reference | solver/*.ms, *.ms.out (+ .ms.log, .ms.err), certificates/*.json, raw-result.json, solver-events.json | G1: RB-4 for post-gate packages; RL-4 `requires` for G2; for G3 and G4 (whose `requires` name G2 and G3) **only RL-4's clause "every further cross-package read of an r4-lineage package that the successor census lists"**. ac4487: outside the r4 lineage, bound by hash (NOT A BAR) |
| X-04 | r3_run_wrapper 199-203, r8_requires | each `requires` entry (the previous package in plan order) | existence of manifest.yaml (no field) | RL-4 (`requires`, existence test kept) |
| X-05 | r3_run_wrapper 206-228, r12_contingency | the replaced package; other contingency packages | manifest.yaml failure_class; package.replaces | NOT A BAR (R-12's failure_class read; DEC-20260924-650068 R-RB3-R-12 stands) |
| X-06 | r3_run_wrapper 273, 300 | run directories | existence / count only | not a read of a recorded result |
| X-07 | v2_driver 1070 -> _load_build 989-1003 (995, 999, 1071, 1077, 1083) | build | raw-result.json polynomials[] shape, arm, m, outcome, reason, info.npz, npz_sha256, meta.support_nonzero_monomials, rescaling beta / lam; the cached .npz under C.CACHE_DIR (outside the package), sha256-compared | RL-4 (`_load_build`) |
| X-08 | v2_driver 1028 -> _prior_cells 1006-1013; _condition_met 1110-1127 | the prior m = 5 cells package | raw-result.json cells[].arm, terminal.status, metrics.targets_measured | RL-4 (`_prior_cells`, `_condition_met`) |
| X-09 | v2_driver cmd_aggregate 1248-1326 (1253, 1256, 1262, 1307) | the 18 cells packages of --runs | raw-result.json kind, curve_shape, m, cells[] (terminal, metrics D, D_per_target, targets_measured, outcome_counts, targets_with_verified_relation, ...) | RL-4 (aggregate) |
| X-10 | a1_driver cmd_aggregate_a1 276-393 (286, 294, 295, 298; _load_raw 238-240) | 6 a1 cells, 18 v2 cells, the v2 aggregate | cells as X-09; v2 aggregate raw-result.json heur_dflat, like_for_like_scoring, matched_control_check_F4, cost_band, ladder_rows, planned_cells_without_row, metrics; the v2 paths hashed against AC.RECEIPT_V2_PHASE_B | RL-4 (aggregate_a1) |
| X-11 | v2_common.resolve_replacement 76-86 (called at v2_driver 993, 1009, 1253, 1269); a1_driver._resolve 243-254 (called at 283, 291, 321) | every contingency package of the plan with a manifest | manifest.yaml run.package.replaces | **only RL-4's clause "every further cross-package read ... that the successor census lists"**; the ids read are the plan's contingency ids |
| X-12 | v2_driver cmd_anchor_identity 642, 683-686, 700 | archived RUN-GFPN-61bba9 (v1) | raw-result.json parameters a4, a6, p; anchor_t0..t4.ms.log | NOT A BAR (archived, outside the r4 lineage; binding below) |

**Outside the card's scope, listed for completeness:**
- `a1_check_run.py` 79-84, a checker item rather than a command or the wrapper, reads
  the controls_a1 image's run_status and gate_pass.
- `r3_check_run.reg1_recorded_check` reads the package's OWN manifest.

**Bindings of the archived reads.** Each file's sha256 was compared at read time:
- RUN-GFPN-61bba9 `raw-result.json` and `anchor_t0..t4.ms.log`, 6 / 6 equal to the
  TASK-20260921-98561a snapshot receipt (commit 520e7fea5). `cmd_anchor_identity`
  records the logs' sha256 (684) and checks no receipt itself.
- RUN-GFPN-ac4487 `raw-result.json` equals the TASK-20260923-0fa03f post-run receipt
  (commit f9188ae34). `r3_reg1` checks the reference's integrity itself (285).

### (b) Per package kind so read: outcomes a dependent package acts on, and checker items

**Checker items read.**
- `v2_check_run`:
  - run id reserved (43);
  - status agreement (53);
  - **read-back list non-empty for every kind except `aggregate`, and each entry equal
    to the cap (65-70)**;
  - certificates re-verify on completed_valid (90).
- `a1_check_run`:
  - controls_a1 checks present (72);
  - image passed for controls_a1_gate_required packages (79);
  - v2_check_run applied unchanged (133).
- `r3_check_run`:
  - the frozen checker's exit status (400);
  - the consistency flag (174);
  - REG-1 recorded PASS from G2 on (329);
  - status agreement (341);
  - SC-4 does not change the exit status (396).
- The r4 checks as specified:
  - RB-3 SC-4 changes no exit status.
  - RL-3 gates "nothing by itself".
  - RL-5's consistency tests fail only on a recording failure.

**Plan `requires` chains** (JSON `plan_requires_chains`). Each package requires the
previous one:
- v2-r3: G1 → G2 → G3 → G4 → F-4 → build 4111 → m = 5 cells (ecgfp5_shaped,
  random_2torsion, random_no2torsion) → m = 4 cells (same order) → build 262151 → ...
  → m = 4 random_no2torsion 16777291 → aggregate.
- v2-a1-r3: controls_a1 → build → m = 5 × 3 → m = 4 × 3 → aggregate_a1.

The v2-r3 plan's gate rule states "package 5 runs after the gate and is NOT blocking"
(F-4).

| kind (read by) | correctly recorded outcome a dependent's frozen logic acts on | does a checker item exit non-zero on it by design? |
|---|---|---|
| cells m = 5 (X-08, X-09, X-10, X-04) | **The draft's example:** a cell recorded not_measured, with its targets' children created (timeout, memory_exhausted, crash, non-generic). `_condition_met` reads it (1125-1126; terminal 1235); the package records failed / resource_exhaustion (1101-1102) | **No.** Status agrees with the manifest (53); the created children's pairs are collected (raw `cells[].targets[].solver`, and RL-1 launch records), so the list is non-empty and equal to the cap |
| cells m = 5 | **A package in which no capped child is created.** Every runnable cell is not_attempted "polynomial unavailable" (the build row for (shape, arm, 5) is not ok: 1071-1075). Every other cell is refused or not_attempted by design: raw not_attempted; torsion_S5_norm conditional on S5 measured. For random_no2torsion only S5 is runnable (rq and S_rescaled refused "no rational 2-torsion", 1044-1050; norm refused 1052-1058), so one failed build row suffices. The package records completed_valid (1101). The m = 4 package's `_condition_met` acts on the S5 cell's terminal not_attempted (1122-1126); the aggregates act on the rows | **Yes: `v2_check_run.py` 65-67 "no child RLIMIT_AS read-back recorded"** (kind `cells` is not exempt; zero launches give an empty list under RB-2 and RL-3 alike). Under RL-4 this refuses the dependent package, and through `requires` the rest of the chain |
| cells m = 5 | Every target of every runnable cell refused_to_start before fork (P-1..P-4). The cells are recorded not_measured with class infrastructure_error (1184-1188, 1235), and `_condition_met` treats them as not_measured (condition met) | **Yes: 65-67** (no child was created, so there is no pair) |
| cells m = 4 (X-09, X-10, X-04) | measured / not_measured / not_attempted (condition not met) / refused. The unconditional raw cell creates raw_grid children and solves (I-20, I-21) | **No.** RL-1 records the pair of every created child. The only exception is every launch refused before fork (65-67) |
| build (X-07, X-04) | rows ok / refused / failed; the package records failed with class resource_exhaustion or infrastructure_error (976-978). Cells act on `outcome != "ok"` (1071) | **No.** Every created builder child's pair is in `polynomials[].info.child` and in RL-1. The only exception is every launch refused before fork |
| fixture4 F-4 (X-04: build 4111 requires F-4) | the plan calls F-4 "NOT blocking"; build reads none of F-4's content | only on the generic items (e.g. no pair recorded). **Observation:** RL-4 through `requires` makes build's admission depend on F-4's r4 checker exit status, which the frozen plan's F-4 rule does not |
| gate packages G1..G4 (X-01, X-03, X-04) | completed_valid with gate_pass true admits; anything else refuses | a failed gate stops the lineage by design (RB-4) |
| controls_a1 image (X-02; a1_check_run 79-84) | the same | the same; a failed controls_a1 ends the addendum at its gate by design |
| aggregate (v2), read by aggregate-a1 (X-10) | its figures | **No.** Kind `aggregate` is exempt from 65 (aggregate_a1 also writes kind `aggregate`, a1_driver 374); run_status is always completed_valid (v2_driver 1314) |
| contingency packages (X-11) | `package.replaces` redirects the read | as for the kind replaced |

**RLR-4 reading, as the draft words it.** The draft's condition: "approvable as written
ONLY IF (a) every read, by any command of either plan or by the r4 wrapper, of the
recorded result of another package of the r4 lineage ... is covered by RB-4 or RL-4 as
worded; AND (b) for each kind of package so read, no correctly recorded outcome that a
dependent package's frozen logic is designed to act on (for example an m = 5 cell
recorded not_measured, read by "m5_not_measured", v2_driver.py 1119-1126) is one on
which the frozen checker or an r4 check as specified exits non-zero by design. ...
NOT A BAR: reads of archived packages outside the r4 lineage bound by hash
(RUN-GFPN-61bba9, RUN-GFPN-ac4487), named with their binding; R-12's failure_class
read."

Census findings, reported, not decided:

(a) Coverage of the reads:
- RB-4 covers X-01 and X-02.
- RL-4 covers these by name: X-04 (`requires`), X-07, X-08, X-09 and X-10.
- RL-4 covers these only through the clause that covers the reads "the successor census
  lists":
  - X-03, G1 read by REG-1 at the admission of G3 and G4;
  - X-11, the contingency manifests read by `resolve_replacement` and `_resolve`.
- NOT A BAR as worded: X-05 (R-12), X-12 and the X-03 reference (archived; bound by the
  receipts above).
- X-06 reads no recorded result.

(b) Checker exits on planned outcomes:
- For the draft's own example (an m = 5 cell recorded not_measured with children
  created), no frozen checker item or specified r4 check exits non-zero.
- The census does name **correctly recorded outcomes on which `v2_check_run.py` 65-67
  exits 1 by design while a dependent package's frozen logic acts on them**:
  - an m = 5 cells package in which no capped child is created. This follows from the
    frozen logic when the build rows its runnable cells need are not ok; for
    random_no2torsion one failed S5 m = 5 build row suffices.
  - any package kind whose every launch was refused before fork.
- F-4's checker verdict gates build through `requires` under RL-4, although the frozen
  plan's rule calls F-4 not blocking.

## 6. RLR-7 (RFQ-7): controls-a1 in a development world

**What the frozen `controls-a1` command reads, and where each input comes from.**

| input | lines | supplied by |
|---|---|---|
| the plan package of the run id, with p == `--p` (`--p` is `type=int, required=True`) | v2_driver 58; a1_driver 51, 449 | the plan (the package whose run_id is the basename of GFPN_RUN_DIR) |
| the ladder entry `C.ladder_entry(p)` | a1_driver 68; v2_common 35; `C = AC.redirect_v2()` at a1_driver 30 (no ladder_path; a1_common 95) | v1 `implementation/ladder.json`, not the plan |
| `rescaling_parameters.per_shape` (check (c)) | a1_driver 114, 120 | the plan |
| watchdogs `builder_timeout_s.m3` (check (e) builds) and `per_arm_m "<arm>\|m3".per_target_timeout_s` (check (e) solves) | a1_driver 146, 166 | the plan. The r3 wrapper's R-9 requires the plan's watchdogs to equal trial-plan-v2.json's (r3_run_wrapper 292) |
| gp `/usr/bin/gp`, capped, `PARI_TIMEOUT_S` 7200; plus an uncapped `gp --version-short` (timeout 30) | a1_pari 27, 28, 121 | host binary and module constants |
| the health check: PATTERNS (2,2,2), (4,4,4); `DEV_TIMEOUT_S` 1800; seed `AC.HEALTH_SEED`; retry `:2` when the first system fails; no reinvocation | a1_health 51, 53, 223; a1_driver 129 | module constants |
| the cap | v2_driver 43, 65 | `v2_driver.CAP` (env `GFPN_V2_CAP_BYTES`, default 10737418240) |

**How a development plan derived "as RB-6 (a) derives plans" supplies these.**
- The draft's words (readbackcover 315): "Plans are derived from the FROZEN plans, as
  r3's were."
- The r3 a1 plan equals the frozen a1 plan in every plan-read field:
  - controls_a1 p 1073741831 in both;
  - driver_args `controls-a1 --p 1073741831` in both;
  - rescaling_parameters equal (its `p` is 1073741831);
  - watchdogs equal, and equal to trial-plan-v2.json's.
- RB-5's development world requires "no reserved id, a development label" (readbackcover
  287). `Ctx` resolves `plan_package(plan, run_id())`, so the label must be a package id
  of the plan the process reads.
- The r3 DV-7 precedent (r3_dv7.py 11, 47, 160, 174) differs:
  - it ran controls-a1 at the toy prime 1021;
  - it used toy plan copies, with `p`, `driver_args` and watchdogs changed, and the
    toy-only keys also added to the toy trial-plan-v2.json copy so that R-9 held;
  - it redirected `v2_common.LADDER_PATH` and `EXP_DIR` in-process;
  - it solved at no ladder or fixture prime (R3S-9).

**Per ladder prime.** All data comes from `ladder.json`, read as data:

| p | role | ladder facts (ecgfp5_shaped; random_2torsion; random_no2torsion) | ladder records check (b)'s facts | ecgfp5_shaped rescaling refused (b a square) | every plan-read input supplied without changing a frozen plan value |
|---|---|---|---|---|---|
| 4111 | ladder | order ≡ 2 (mod 4), h 2, b non-square; same; order ≡ 1, h 1, no 2-torsion | yes | no | **no**: needs the package's p / driver_args set to 4111 and rescaling_parameters recomputed (else check (c) records equals_plan false) |
| 262151 | ladder | as 4111 | yes | no | **no** (as 4111) |
| 65551 | "anchor_only (16-bit rung: msolve 0.6.5 segfaults in its parametrization step for 16-17-bit primes, so this rung serves the JV 16-bit timing anchor with -g only)" | as 4111 | yes | no | **no** (as 4111); the rung's recorded role concerns the `-P 1` solves of checks (d) and (e) |
| 16777291 | ladder | **order ≡ 0 (mod 4), h 4, b a square**; order ≡ 2, h 2, b non-square; order ≡ 3, h 1 | **no** | **yes** (checks (c), (e), (f) depend on that rescaling) | **no** (as 4111) |
| 1073741831 | ladder | order ≡ 2, h 2, b non-square; same; order ≡ 1, h 3, no 2-torsion | yes | no | **yes** (the plan's own controls_a1 prime; only a development label replaces the run id) |

**The frozen plan's watchdogs for this command at 1073741831.**
- The package field: "per_arm_m keys *|m3 and builder_timeout_s m3 (uniform with v2)".
- `builder_timeout_s.m3` 1800, for 2 builders.
- `torsion_S3_rq|m3` and `S3_rescaled|m3` `per_target_timeout_s` 1800, for 2 S-1
  solves.
- Module constants, not plan values:
  - `DEV_TIMEOUT_S` 1800, for 2 first S-2 systems plus up to 2 retry_seed2 systems;
  - `PARI_TIMEOUT_S` 7200, for 1 gp child.

**MODELED, not measured:** the sum of those single-attempt timeouts is 21600 s
(2 × 1800 + 2 × 1800 + 4 × 1800 + 7200). Three things fall outside that sum:
- The r3 bounded re-solve rule may add attempts 2..k at S-1 / S-2 until their summed
  wall seconds reach the call's timeout (r3_resolve.py 241-244, 301-309).
- In-process work (checks (a), (c), (e) point sampling, lifting) is bounded by no
  watchdog.
- So are the uncapped host scans.

**RLR-7 reading, as the draft words it.** The draft's condition: "approvable as written
ONLY IF the successor census names at least one ladder prime at which the frozen
controls-a1 command can run in a development world through the r4 a1 entry WITHOUT a
frozen-byte edit, stating what the command reads there (the ladder entry, the plan's
rescaling_parameters and watchdogs, gp, the health patterns and cap) and where a
development plan derived as RB-6 (a) derives plans supplies each, and the frozen plan's
watchdogs that bound its cost. If none exists, DV-18 (e) is infeasible as worded and
the draft is NOT approvable as written."

Census finding:
- **Frozen plan values unchanged.** The smallest ladder prime at which a plan derived
  from the frozen plans, as the r3 plans were, supplies every plan-read input without
  changing a frozen plan value is **1073741831**. It is the only such prime. It needs
  only a development label as the package's run id, and no frozen byte changes.
- **Plan values re-derived per prime.** If the derived plan may also set the
  controls_a1 package's p / driver_args and recompute rescaling_parameters at the
  prime, as the r3 DV-7 toy copies did, the command reads every input at every ladder
  prime. The ladder entry is present for all five. The smallest is then **4111**.
  - At 16777291 the ladder data record ecgfp5_shaped as b-square, order ≡ 0 (mod 4),
    h 4.
  - At 65551 the ladder records msolve 0.6.5 segfaulting in its parametrization step.
- Which derivation RB-6 (a) permits for DV-18 (e) is not decided here (L-9). Neither is
  the wrapper-level admission of a development controls-a1 package (R-7 gate packages,
  REG-1, R-9).

## 7. RLR-6 (RFQ-7, informational): readers of `solver-events.json`

| reader | lines | reads | does a new top-level key (launch_records, passthrough_records) change what it computes? |
|---|---|---|---|
| r3_resolve (the writer) | 154, 167 | never reads the file: it rewrites its in-memory document | n/a |
| r3_run_wrapper.solver_events_block | 391, 395 | sites, K, spacing_s, cap_rule, consistency_violation by constant key; S-1 / S-2 counters and events; S-3 counters; whole-file sha256 | no, except the recorded whole-file sha256 (the bytes change) |
| r3_run_wrapper.consistency_flag | 577 | top-level consistency_violation | no |
| r3_check_run.events_file_integrity (VA-6 (a)) | 157 | whole-file sha256 vs the manifest's recorded sha256 | no (both sides are the same bytes) |
| r3_check_run.events_file_epsilon (VA-6 (b)) | 174, 179 | exists / parses; flag; K, spacing; S-1 / S-2 counters | no |
| r3_check_run.forbidden_id_keys (VA-7 (b)) | 195, 209 | top-level task_id, run_card, written_by_task, archived_by only | no |
| r3_reg1.solver_events_check / compare (REG-1 SE-4 (e)) | 175, 194, 282 | candidate only: exists / parses; flag; S-1 / S-2 events' consistency.ok; counters copied; file quoted verbatim | no for the verdict; the verbatim quote grows (report only); a recording failure is one more cause of the flag (RL-7) |
| a1_check_run addendum_checks, forbidden-id byte sweep | 51, 53 | the bytes of every `.json` of the package, solver-events.json included, for `a1_common.FORBIDDEN_TASK_ID` | no, unless a record's copied strings (argv, tag, calling-frame file) contain that id; the added bytes are scanned |
| frozen commands, v2_check_run, the aggregates, a1 phase_b_check | a1_driver 298 | none: no file of implementation-v2/ or implementation-v2-a1/ names the file; phase_b_check hashes only the raw-result.json paths read | n/a |
| tools/ and harness/ | - | none (text scan of 215 files) | n/a |

Development checks also name the file, but none is invoked by an entry, the wrapper or
the checker:
- r3_devchecks_more, r3_dv6, r3_dv7, r3_dv12, r3_dv16 and r3_inventory;
- the retired r2 layer.

## 8. Method limits

**Carried from the archived census, where they still apply:**
- **L-1.** It closes for a raise in the CALLER after `run_child` returned: RL-1 has
  already appended the launch record. It remains for a raise INSIDE `run_child` after
  fork; see L-6.
- **L-2.** The ERR setrlimit branch (P-6) takes no pair; RL-1 records "absent".
- **L-3.** Which branch occurs is a run-time fact. Every branch here is static.
- **L-4.** Grandchildren were not examined.
- **L-5.** controls-a1, fixture4, build, cells and aggregate(-a1) have never run under
  r3, so their dispositions are static. No r4 code exists: RL-1..RL-3 are read as
  worded, not as implemented.

**New limits:**
- **L-6.** RL-1 (c) derives every recorded field from the RETURNED record. On P-14 and
  P-15 no record is returned, so RL-1 as worded records child_created false and pair
  "absent" for a created child.
- **L-7.** P-7 is a created-child branch with no pair, and it is not literally "the ERR
  setrlimit branch". The draft does not say whether RL-1 (c)'s "carries
  child_rlimit_report" is a key-presence test; the key's value on P-7 is `''`.
- **L-8.** RLR-2 is read on the r3 entries and their import closure. The r4 entries do
  not exist. A module the r4 layer adds, or a `v2_solver.py` placed on the r4 entries'
  `sys.path`, is outside this reading.
- **L-9.** RLR-7 does not decide:
  - whether a derived plan may change the controls_a1 package's p and
    rescaling_parameters;
  - the wrapper-level admission of a development controls-a1 package (R-7 gate
    packages, REG-1, R-9).
- **L-10.** RLR-4 (b) is a static reading of the checkers and drivers. No package was
  run to confirm any checker exit status.

## 9. Completion gate

- **RFQ-2 integrity** passed before any reading and is recorded with full hashes
  (section 1).
- **RLR-1** is reported per run_child path (P-1..P-15) and per instance and branch, each
  with its sources or NONE, and the reading is stated as the draft words it.
- **RLR-2** is reported per call site with its resolution form, with the capture search,
  the from-imports, the closure and the other RLIMIT_AS launches, and the reading is
  stated.
- **RLR-3** is reported per gb_only call, with the `-g` exclusion lines, and the reading
  is stated.
- **RLR-4** (a) and (b) are reported per read and per package kind, and the reading is
  stated.
- **RLR-7** is reported per ladder prime, with the smallest prime under each stated
  derivation, and the reading is stated. **RLR-6** is reported.
- **Scope (RFQ-1):**
  - no solver, valgrind, callgrind_annotate, gp, Sage or builder child;
  - no import of a scanned-tree module (guard 0 / 0);
  - no run package;
  - nothing written outside `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/`,
    apart from disclosed transient scratch under `<scratchpad>/rfcensus/`;
  - no frozen, preserved or archived byte changed: (g) is empty; 60 pre-existing `.pyc`
    files and the pre-existing `__pycache__` directories are unchanged, and none was
    added.
- **Citations:** 480 checked against the file text, with 0 failures (RLR-1 321, RLR-2
  18, RLR-3 18, RLR-4 79, RLR-6 16, RLR-7 28).
- No D or degree is reported as a result, and no approval recommendation is made.

## 10. Deviations and disclosures

1. **Reading before integrity.** The card, the executor contract, the runtime core, the
   draft, DEC-20260924-650068, CORR-20260924-80009d, and the archived census's md and
   rb_check.py were read before the integrity checks, as the dispatch ordered ("READ
   FIRST, IN FULL").
   - The archived census files were therefore read before check (d) confirmed their
     hashes. Check (d) then passed.
   - No bound source code, plan or run package was read before the scratch pre-check
     passed.
2. **Integrity ran more than once.** It ran as the scratch pre-check
   (`<scratchpad>/rfcensus/integrity_precheck.py`), and again as phase 1 of each of the
   four `rf_check.py` runs. Every run passed.
3. **`rf_check.py` ran four times.** Development runs 1-3 wrote to
   `<scratchpad>/rfcensus/`; the fourth run wrote `readbackfull-census.json`. Every run
   was complete with guard 0 / 0 and 480 citations with 0 failures.
   - After run 1:
     - DP-5's count now counts directories only. Run 1 counted 55 entries because
       `runs/.gitkeep` is a file; there are 54 directories.
     - The module-level launch scan now separates calls under
       `if __name__ == "__main__":`. Run 1 listed `a1_health.main` (297) among
       import-time launches.
   - After run 2: the plan `requires` chains block was added to RLR-4 (b).
   - Before run 1, three edits were made:
     - one cited line was corrected (r3_resolve `os.replace` is at 167);
     - the per-reading citation tally was fixed;
     - the caller-raise row was extended to every instance.
   - The final file is byte-identical before and after the run that produced the JSON
     (sha256 below).
4. **Dispositions were read by hand**, as in the archived census (DEC-20260924-650068
   D-4). These are the run_child path table P-1..P-15, the RLR-4 read and outcome
   tables, and the RLR-7 inputs. The script:
   - re-checks every cited line;
   - ties the instance table to the call graph in both directions;
   - verifies the run_child return statements by ast.
5. **`tools/` and `harness/` were read as text only.** Their 258 module names (with the
   implementation trees) are in the guard's refused set.
6. **Shell utilities.** Uncapped, read-only shell utilities and short `python3 -B -c`
   data readers were used (section 0). None is a solver, valgrind, gp, Sage or builder
   child.
7. **This file** was written by the executor from `readbackfull-census.json`. It is not
   generated by the script.

## 11. Deliverables

- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/rf_check.py`, sha256
  `ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.json`,
  sha256 `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/readbackfull-census.md`,
  this file. Its sha256 is given in the executor's return.
