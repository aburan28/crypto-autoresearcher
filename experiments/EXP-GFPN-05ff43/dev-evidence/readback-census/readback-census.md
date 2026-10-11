# Read-back census: EXP-GFPN-05ff43, TASK-20260924-bf5724

This is the zero-run, zero-solve read-back census for the DRAFT
AMD-EXP-GFPN-05ff43-20260924-readbackcover. The draft is not approved. The census
was ordered by DEC-20260924-1ce186 R-7, and its card is
`ledger/handoffs/TASK-20260924-bf5724.yaml` (RBQ-1..RBQ-8).

**What the census does.** It computes the draft's pre-approval readings RBR-5,
RBR-1, RBR-2, RBR-3 and RBR-4, in that order, exactly as the draft and the card
word them.

**What the census is not.**
- These are observations only.
- Nothing here is evidence about D, the quotient, H-GFPN-9a29be or
  HEUR-GFPN-DFLAT.
- Nothing here is an approval recommendation. The approval act applies the
  readings; this census reports what they read.

Machine-readable record: `readback-census.json`. Check script, exactly as run:
`rb_check.py`. Every number below is copied from `readback-census.json`.

## 0. Run record

| item | value |
|---|---|
| task / card | TASK-20260924-bf5724 / ledger/handoffs/TASK-20260924-bf5724.yaml |
| dispatch | /run EXP-GFPN-05ff43 under TASK-20260924-bf5724; lane claim `coordination/goals/GOAL-GFPN-380702/batches/BATCH-e409ca/claims/TASK-20260924-bf5724.1.claim.json` (owner executor, epoch 1), held by the dispatcher |
| repository HEAD | 50ba9e7ee2900d696f793fd3fe6aa914040434eb; at the final run the only status line was `?? experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py` |
| final script run | 2026-09-24T14:18:45Z to 14:18:48Z UTC (2.971 s), `PYTHONDONTWRITEBYTECODE=1 python3 -B rb_check.py --out readback-census.json`, cwd `/tmp`, Python 3.11.15 |
| run packages created | 0 |
| solver, valgrind, callgrind_annotate, gp, Sage or builder children | 0 |
| scanned-tree modules imported | 0 |
| network | not used |
| files read by the final run | 192, each with sha256 in `files_read_sha256` |

**Inference block (RBQ-8).**
- requested_policy: executor-implementation
- resolved_model_id: null. None was supplied, and none is invented.
- fallback_used: false
- bedrock_used: false. Amazon Bedrock is prohibited.

This is not a security statement.

**Dispatcher memory guard (DP-4), verbatim as dispatched:** pid 875, a bash loop
that kills the largest-RSS msolve/gp/python3 process when MemAvailable <
2621440 kB (about 14.2 GB in use on this 16481980 kB host, swap 0, 4 CPUs). The
task needs little memory and runs no solver.

**Child processes started by this task.**

All of them are read-only git children, launched in the integrity phase:
- Before the integrity pre-check (initial state): `git rev-parse HEAD` and
  `git status --porcelain`, run in the shell, twice.
- The scratch pre-check `<scratchpad>/rbcensus/integrity_precheck.py`, run once:
  `git -C /home/user/crypto-autoresearcher diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'`
- Each of the four runs of `rb_check.py` (see section 7):
  1. `git -C /home/user/crypto-autoresearcher diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`
  2. `git -C /home/user/crypto-autoresearcher ls-files -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`, a pathspec sanity check that matched 92 files
  3. `git -C /home/user/crypto-autoresearcher rev-parse HEAD`
  4. `git -C /home/user/crypto-autoresearcher status --porcelain --untracked-files=all`

**The in-process guard (RBQ-1).**
- It is installed after the integrity phase with `sys.addaudithook`.
- It refuses:
  - the launch events `subprocess.Popen`, `os.system`, `os.exec`,
    `os.posix_spawn`, `os.spawn`, `os.fork`, `os.forkpty`, `pty.spawn` and
    `os.startfile`;
  - any import of the 74 module names of the scanned trees.
- It was self-tested with `sys.audit`, which launches and imports nothing. The
  self-test refused `subprocess.Popen` and `v2_driver`.
- **Attempt counts in the final run: launch 0, import 0.** The two earlier
  complete development runs also counted 0 and 0. The first development run
  stopped before installing the guard.

## 1. RBR-5: integrity (RBQ-2), applied first

All checks passed before any reading. They passed twice: once in the scratch
pre-check, and again as phase 1 of the final `rb_check.py` run.

| check | result |
|---|---|
| (a) draft `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml` | computed `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e` = card value = `addendum_sha256.sha256` of `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-9c617a/ledger-receipt.json` (whose `path` field names the same file): PASS |
| (b) nine VA-1 files vs DEC-20260924-e52eec `bound_hashes` | 9 / 9 equal: v1_to_v2_reanchor_and_arm_iii `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3`; v2_addendum_rung31 `2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c`; paristack `856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7`; seedresolve `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81`; solverevent `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f`; healthresolve `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d`; launchcover `c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447`; consumercover `a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0`; valueclose `877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1`: PASS |
| (c) TASK-20260924-f1fb0e snapshot receipt | 22 / 22 paths hash to their recorded values: PASS |
| (c) TASK-20260924-f1fb0e post-run receipt | 801 / 801 paths hash to their recorded values: PASS |
| (d) implementation-v2/ vs TASK-20260923-0fa03f phase-A receipt | 14 / 14 bound paths equal; no unbound .py file in the tree: PASS |
| (d) implementation-v2-a1/ vs TASK-20260923-4ff597 phase-A receipt | 12 / 12 bound paths equal; no unbound .py file in the tree: PASS |
| (e) `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- .../implementation* .../trial-plan-*.json` | exit 0, empty output: PASS |

**Scope of (d).** Every bound path was checked, which is a superset of the files
this census read.

**Other files read, hashed for the record.** These are not RBQ-2 checks. Their
hashes are in `files_read_sha256`:
- the Sage comparator `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py`,
  sha256 `3ce24822d4af1de3d3a2c6aecb7eaeddb8d78486ea20163903a4fd84dcc8260b`;
- the k5k7 scratch `.py` files.

The stage-r3-dv tarball was hash-checked by (c) and not opened.

## 2. RBR-1 (RBQ-3): every reachable capped child, and its read-back sources

### Definitions and method

**Definitions, as the draft words them.**
- A *capped child* is a process launched through `v2_solver.run_child`.
- A *read-back source* is one of:
  - RB-2 (a): `raw-result.json`, by the r3 key-name collection of
    `rlimit_as_child_getrlimit` (r3_run_wrapper.py 510);
  - RB-2 (b): `child/*.meta.json`;
  - RB-1 / RB-2 (c): a `solver-events.json` attempt record that RB-1 writes from
    the result the frozen function RETURNED.

**Launch scan of every scanned tree** (v1, v2, v2-a1, r1, r2, r3, the Sage
comparator, k5k7):
- **12 `run_child` call sites.**
  - The 6 reachable ones are v2_driver.py 101, 166 and 650, v2_solver.py 517,
    a1_health.py 147 and a1_pari.py 96.
  - The other 6 are in r1/r2/r3 development checks and are reachable from no
    command.
- **2 `setrlimit(RLIMIT_AS)` sites.**
  - `v2_solver.py:193`, inside run_child.
  - `implementation/symmetrize.py:396`, in v1 `run_msolve._limit`. No runtime
    module imports v1, so it is not reachable.
- So `run_child` is the only frozen function reachable from the plans that sets
  RLIMIT_AS in a child.

**Reachability.** A static call graph was built with `ast` over:
- the runtime modules: implementation-v2/, implementation-v2-a1/;
- r3_entry_v2, r3_entry_a1, r3_resolve and r3_common.

How the graph was built:
- **Commands:** taken from the dispatch dicts of `v2_driver.main` and
  `a1_driver.main`.
- **Runtime rebinding:** SE-3 applies in both entries (calls to `v2_driver.solve`
  go to `r3_resolve.solve`, then to the original). HR-3 applies in the a1 entry
  (`a1_health.run_system` goes to `r3_resolve.run_system`, then to the original).
- **Paths:** every path from a command to a `run_child` call was enumerated.

**Dispositions.** They were read by hand from the cited lines and put into an
instance table. The script requires two things:
- every path is covered by an instance, and every instance lies on a path.
  Result: 0 uncovered paths and 0 unmatched instances.
- every cited line is re-checked against the file text. Result: 288 citations,
  0 failures.

It also ran 17 AST checks, all of which pass:
- `info`, `ginfo` and `_i` are never read in `cmd_controls`.
- The `rc` result at v2_driver.py 711 is read only for `f4_rounds`, `outcome`
  and `input`.
- 7 callers pass no `callgrind_timeout`.
- `H.run` at a1_driver.py 129 passes no `reinvoke_on_fail`.

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

### Branches

A launched child can end in one of these branches:
- **ok:** the child exits ok, and `<out>.meta.json` carries the pair
  (v2_child.py 90/95 or 101-104).
- **refused_meta:** the child exits ok but writes a refusal meta WITHOUT the pair
  (v2_child.py 68, 80).
- **no_meta:** timeout, memory_exhausted, crash, nonzero exit, or a pre-exec
  mismatch. No meta.json exists. The `run_child` record still carries the pair
  (v2_solver.py 227).
- **recorded:** the attempt whose result the frozen function returned to its
  caller.
- **ssf_earlier:** an SSF attempt that the r3 bounded rule renamed and re-solved.

### Instances

Columns:
- **raw-result.json write path** is the key `rlimit_as_child_getrlimit`.
- **Returned to wrapper** is the field path of the pair in the result the frozen
  function returns to the S-1 / S-2 wrapper.
- **Sources per branch** are under RB-1 and RB-2 as worded.

| id | command(s) | caller (function) | launch | kind / tags | raw-result.json write path | child/*.meta.json | returned to wrapper | sources per branch |
|---|---|---|---|---|---|---|---|---|
| I-01 | fixture | v2_driver.py:317 (fixture_core) | v2_driver.py:101 | builder build_poly, fixture_<arm> (4) | builds.<arm>.child (+ .meta on ok) | ok only | n/a | ok: RB-2(a),(b); refused_meta: RB-2(a); no_meta: RB-2(a) |
| I-02 | fixture | v2_driver.py:348 (fixture_core.run_target) | :101 | builder raw_grid, fx_<target>_<raw_x/raw_u> | failure only: targets[].arms.<arm>.reason.child (350); ok keeps construction_ops only (353) | ok | n/a | ok: RB-2(b); refused_meta: RB-2(a); no_meta: RB-2(a) |
| I-03 | fixture | v2_driver.py:358 (run_target) | :166 | S-1 msolve, fx_<target>_<arm> | targets[] / replaced_fresh_targets[] / planted_targets[] .arms.<arm>.solver | none | result['solver']['rlimit_as_child_getrlimit'] (167) | recorded: RB-2(a), RB-1; ssf_earlier: RB-1 |
| I-04 | fixture | v2_driver.py:358 via :209 | v2_solver.py:517 | S-3 callgrind | ...arms.<arm>.instructions_callgrind.child | none | inside the S-1 result: result['instructions_callgrind']['child'][...] (RB-1 (b) as worded copies result['solver'] only) | RB-2(a) |
| I-05 | fixture4 | v2_driver.py:548 (cmd_fixture4) | :101 | builder build_poly, f4_<arm> (4) | builds.<arm>.child | ok | n/a | every branch: RB-2(a) (+(b) on ok) |
| I-06 | fixture4 | v2_driver.py:565 | :166 | S-1 msolve, f4_t<i>_<arm> | targets[].arms.<arm>.solver | none | result['solver'][...] | recorded: RB-2(a), RB-1; ssf_earlier: RB-1 |
| I-07 | anchor-identity | v2_driver.py:650 (cmd_anchor_identity) | :650 | Sage comparator (1) | comparator.child (652, 655; every outcome) | none | n/a | RB-2(a) |
| I-08 | anchor-identity | v2_driver.py:671 | :101 | builder build_poly, anchor_S4 (1) | build.child (673) | ok | n/a | RB-2(a) (+(b) on ok) |
| I-09 | anchor-identity | v2_driver.py:693 (gb_only=True) | :166 | S-1 msolve -g 1, pass-through, anchor_<comparator_random, v2_t0..t2> (4) | targets[].solver (699) | none | result['solver'][...] through the r3 pass-through (r3_resolve.py 382-387) | RB-2(a) |
| **I-10** | anchor-identity | v2_driver.py:711 (gb_only=True) | :166 | S-1 msolve -g 1, pass-through, **anchor_comparator_system (1)** | **NONE**: row['comparator_system'] keeps outcome, input and trace only (713-716) | none | result['solver'][...] through the pass-through | **only RB-1, and only if RB-1 is read to cover pass-through calls** |
| I-11 | controls | v2_driver.py:768 (cmd_controls) | :101 | builder build_poly, ctl_identity_n3 (1) | **NONE**: `info` never read | ok | n/a | ok: RB-2(b); **no_meta: NONE** |
| I-12 | controls | v2_driver.py:782 | :101 | builder raw_grid, ctl_raw_random, ctl_raw_planted (2) | **NONE**: `ginfo` never read | ok | n/a | ok: RB-2(b); **no_meta: NONE** |
| I-13 | controls | v2_driver.py:801 | :101 | builder build_poly, ctl_identity_n5_m3/m4 (2) | **NONE**: bound to `_` | ok | n/a | ok: RB-2(b); **no_meta: NONE** |
| I-14 | controls | v2_driver.py:805 | :101 | builder raw_grid, ctl_raw_n5_m3/m4 (2) | **NONE**: bound to `_i` | ok | n/a | ok: RB-2(b); **no_meta: NONE** |
| I-15 | controls | v2_driver.py:816 | :101 | builder build_poly, ctl_S3, ctl_S3_rescaled, ctl_torsion_S3_rq, ctl_torsion_S3_norm (4) | **NONE**: bound to `_` | ok | n/a | ok: RB-2(b); **refused_meta: NONE; no_meta: NONE** |
| I-16 | controls | v2_driver.py:786 | :166 | S-1 msolve, ctl_identity_random/planted (2) | **NONE** (detail keeps D, outcome; 792-795) | none | result['solver'][...] | recorded: RB-1 only; ssf_earlier: RB-1 |
| I-17 | controls | v2_driver.py:787 | :166 | S-1 msolve, ctl_rawx_random/planted (2) | **NONE** | none | result['solver'][...] | RB-1 only |
| I-18 | controls | v2_driver.py:841 | :166 | S-1 msolve, ctl_planted_<arm> (4) | **NONE** (845-846) | none | result['solver'][...] | RB-1 only |
| I-19 | build, build (a1) | v2_driver.py:961 (cmd_build; a1 via a1_driver.py:225) | :101 | builder build_poly, to_cache | polynomials[].info.child (963, 979), every branch | none under child/: meta goes to C.CACHE_DIR outside the package (96); retained copies go to polynomials/*.meta.json (969-970) | n/a | every branch: RB-2(a) |
| I-20 | cells, cells (a1) | v2_driver.py:1161 (_run_cell) | :101 | builder raw_grid, grid_<arm>_t<i> (raw arms, m <= 4) | **NONE**: ok keeps construction_ops (1168); failure keeps a reason STRING (1163) | ok | n/a | ok: RB-2(b); **refused_meta: NONE; no_meta: NONE** |
| I-21 | cells, cells (a1) | v2_driver.py:1174 | :166 | S-1 msolve, <arm>_t<i> | cells[].targets[].solver (1179) | none | result['solver'][...] | recorded: RB-2(a), RB-1; ssf_earlier: RB-1 |
| I-22 | cells, cells (a1) | v2_driver.py:1174 via :209 | v2_solver.py:517 | S-3 callgrind, <arm>_t0 of m <= 4 cells | cells[].targets[].instructions_callgrind.child | none | inside the S-1 result | RB-2(a) |
| I-23 | controls-a1 | a1_driver.py:89 (cmd_controls_a1) | a1_pari.py:96 | gp, controls_a1_pari (1) | checks[b].detail.pari.child (a1_pari 98; a1_driver 91, 112) | none | n/a | RB-2(a) |
| I-24-first | controls-a1 | a1_health.py:234 (run), entry a1_driver.py:129 | a1_health.py:147 | S-2 health msolve, health_p<p>_d<pattern> | **NONE under the collected key**: first-system pair at checks[d].detail.per_pattern[].**getrlimit** (a1_driver.py 133) | none | result['child']['rlimit_as_child_getrlimit'] (a1_health.py 150) | recorded: RB-1 only; ssf_earlier: RB-1 |
| I-24-retry_seed2 | controls-a1 | a1_health.py:241 | :147 | S-2, _seed2 (only when the first system fails) | **NONE** (retries are not in raw-result.json) | none | same | RB-1 only |
| I-24-reinvocation / -retry_seed2_reinvocation | controls-a1 | a1_health.py:237, 244 | :147 | S-2 (not executed: `H.run` is called without `reinvoke_on_fail`, default False) | NONE | none | same | RB-1 only |
| I-25 | controls-a1 | a1_driver.py:146 | v2_driver.py:101 | builder build_poly, ctl_a1_torsion_S3_rq, ctl_a1_S3_rescaled (2) | **NONE under the collected key**: pair at checks[f].detail.<arm>.**build_getrlimit** (184); the failure detail of (e) keeps outcome and reason only (163) | ok | n/a | ok: RB-2(b); **refused_meta: NONE; no_meta: NONE** |
| I-26 | controls-a1 | a1_driver.py:166 | v2_driver.py:166 | S-1 msolve, ctl_a1_planted_<arm> (2) | **NONE under the collected key**: pair at checks[e].detail.**solver_getrlimit** (174) | none | result['solver'][...] | recorded: RB-1 only; ssf_earlier: RB-1 |

**Other package files carrying the pair.** None of these is an RB-2 source.
- **Builders:** the text line `child RLIMIT_AS read back: soft=... hard=...` in
  `child/<tag>.stdout` (v2_child.py 61), for every branch in which the child
  started its job.
- **S-2:** `health/health-<p>.json` (systems[].<first|retry_seed2|...>.child, and
  getrlimit_read_backs; a1_health.py 248-252).
- **S-3:** the r3 `solver-events.json` S-3 record (r3_resolve.py 348-361). It is
  not an attempt record.
- **SSF attempts at S-1 / S-2 in r3:** event attempt records
  `child_rlimit_as_getrlimit` (r3_resolve.py 185, 199). They are persisted only
  when an SSF event or a consistency violation exists, and no r3 collector reads
  them.

**Statically reachable but never launched (7 paths).** In each case the
callgrind child is reachable through `solve()`, but the caller passes no
`callgrind_timeout` (default None, and v2_driver.py 207 requires it):
- v2_driver.py 565, 693, 711, 786, 787 and 841;
- a1_driver.py 166.

**Uncapped children reachable from the commands.** These are not capped children
and are recorded for completeness:
- `v2_common.py:59` (sh: host scans, dpkg-query), reached by every command;
- `v2_solver.py:533` (`callgrind_annotate`), reached by fixture and cells, and
  statically by the other solving commands;
- `a1_pari.py:121` (`gp --version-short`), reached by controls-a1.

### Threads-executed

| child | raw-result.json | returned field | RB-1 | other |
|---|---|---|---|---|
| S-1 in fixture, fixture4, anchor gb_only targets, cells | yes (`threads_executed` in rows) | result['threads_executed'] (v2_driver.py 169) | yes (not for pass-through, unless RB-1 is read to cover it) | none |
| S-1 in controls | NONE | same | yes | none |
| S-1 in controls-a1 | yes (checks[e].detail.threads_executed, a1_driver.py 173) | same | yes | none |
| S-1 anchor_comparator_system | NONE | same | reading-dependent | none |
| S-2 health | NONE | result['threads_executed'] (a1_health.py 149) | yes | health/health-<p>.json |
| S-3 callgrind | NONE | none: the frozen record carries no threads value (v2_solver.py 519-520) | none | none |
| builder, Sage, gp | n/a: no msolve threads value is produced | | | |

### RBR-1 reading, as the draft words it

The draft's condition: the draft is "approvable as written ONLY IF, for EVERY
capped child the census finds reachable from ANY command of either r3 plan, at
least one read-back source exists under RB-1 and RB-2 as worded."

The census's findings against that condition, naming every child with NO source
under RB-1 and RB-2 as worded:

1. **A child whose source depends on how RB-1 is read.** This one is launched in
   every anchor-identity run.
   - **I-10 `anchor_comparator_system`** (anchor-identity, v2_driver.py:711;
     evidenced in RUN-GFPN-f5412a).
   - It is a gb_only call. In the r3 layer's vocabulary it is not a "wrapped
     call": `wrapped_calls` is counted only in `_bounded` (r3_resolve.py 253),
     and pass-through calls are counted apart (382-387). RUN-GFPN-f5412a records
     wrapped_calls 0 and passthrough 5.
   - The draft does not say whether RB-1's "EVERY attempt of EVERY wrapped call
     at S-1" covers pass-through calls. If it does not, this child has NO source.
2. **Children with NO source on a failure or refusal branch.** For these the pair
   exists only in the `run_child` record, which the caller discards or stores
   under a key the collection does not read:
   - **controls:** I-11 ctl_identity_n3, I-12 ctl_raw_random / ctl_raw_planted,
     I-13 ctl_identity_n5_m3 / m4 and I-14 ctl_raw_n5_m3 / m4, each on no_meta;
     I-15 ctl_S3, ctl_S3_rescaled, ctl_torsion_S3_rq and ctl_torsion_S3_norm, on
     refused_meta and no_meta.
   - **cells (both plans):** I-20 grid_<arm>_t<i>, on refused_meta and no_meta.
   - **controls-a1:** I-25 ctl_a1_torsion_S3_rq / ctl_a1_S3_rescaled, on
     refused_meta and no_meta.
3. **On the ok branch,** every reachable capped child other than I-10 has at
   least one source under RB-1 and RB-2 as worded.

For some children the ok-branch source exists only under RB-1:
- I-16, I-17 and I-18 (the 8 controls solves);
- I-24 (S-2 health);
- I-26 (the 2 controls-a1 solves).

For others the source exists only under RB-2 (b) (meta):
- I-02 on ok, I-11..I-15, I-20 and I-25.

**Static-method limits** (the draft names such limits "NOT A BAR"):
- **L-1:** a frozen function that raises after its child ran returns no result.
  For example, a parse error in `v2_driver.solve` after line 166 means RB-1 has
  nothing to copy.
- **L-2:** on the `run_child` "ERR setrlimit" branch (v2_solver.py 194-196), no
  getrlimit pair is ever taken.
- **L-3:** which branch occurs is a run-time fact. The refused_meta branches of
  I-20 and I-25 are not expected, because the same deterministic rescaling
  already passed in the parent (v2_driver.py 1044-1050; a1_driver.py 139). They
  are static branches.
- **L-4:** grandchildren (inside msolve, valgrind, Sage or gp) inherit RLIMIT_AS
  and were not examined. The comparator script launches no process.
- **L-5:** controls-a1, fixture4, build, cells and aggregate(-a1) have never run
  under r3, so their dispositions are static only. fixture, anchor-identity and
  controls are corroborated by the gate packages (section 5).

Whether the failure and refusal branches and the pass-through question fall
under the condition, or under the NOT-A-BAR limits, is for the approval act.

## 3. RBR-2 (RBQ-4): SC-4 enumerability of every wrapped S-1 / S-2 call

The wrapped call sites were found on the same call graph: edges into
`r3_resolve.solve` or `r3_resolve.run_system` from outside r3_resolve.
Today's SC-4 source is `r3_check_run.sc4_accounting`:
- S-1 from raw-result.json dicts carrying a `solver` record with argv and
  outcome ok, and without `-g` (r3_check_run.py 89-99, 134-140);
- S-2 from `health/health-<p>.json` (111-125).

The table has 14 citations, 0 failures.

| command | call site | site | wrapped? | enumerated by today's r3 SC-4 source | under RB-1 + RB-3 as worded |
|---|---|---|---|---|---|
| fixture | v2_driver.py:358 | S-1 | yes | yes (raw solve record) | yes |
| fixture4 | v2_driver.py:565 | S-1 | yes | yes | yes |
| cells, cells (a1) | v2_driver.py:1174 | S-1 | yes | yes | yes |
| **controls** | v2_driver.py:786, 787, 841 | S-1 | yes | **NO** (no `solver` record in raw-result.json) | yes |
| **controls-a1** | **a1_driver.py:166** | S-1 | yes | **NO**: check (e) detail carries `solver_getrlimit` and `threads_executed`, but no `solver` record | yes |
| controls-a1 | a1_health.py:234, 237, 241, 244 | S-2 | yes | yes (health report: first, reinvocation, retry_seed2, retry_seed2_reinvocation) | yes |
| anchor-identity | v2_driver.py:693, 711 | S-1 | no (gb_only pass-through) | excluded: `-g` argv (r3_check_run.py 136); 711 is not in raw-result.json | not a wrapped call; excluded from SC-4 by `-g` |

**RBR-2 reading, as the draft words it.** The draft's condition: "approvable as
written ONLY IF every wrapped S-1 and S-2 call the census finds reachable from any
command is enumerable by RB-3 as worded."

Census finding: every wrapped S-1 and S-2 call site found (the 11 wrapped sites
in the table) is enumerable under RB-1 + RB-3 as worded. RB-1 writes every
attempt with its tag, retained-output flag and outcome class to a
`solver-events.json` attempt record, and RB-3 enumerates from those records. The
census names no wrapped call whose attempts no source would enumerate.

**Finding on today's gap: it is NOT confined to `controls`.** The frozen
`controls-a1` command (a1_driver.py:166; 2 calls, ctl_a1_planted_torsion_S3_rq
and ctl_a1_planted_S3_rescaled) has the same gap under the r3 enumeration. It has
never run.

**Limit.** An attempt whose frozen function raises returns no result for RB-1 to
copy. Such an attempt has no ok class, so it cannot be a recorded ok attempt
with a retained output.

## 4. RBR-3 (RBQ-5): admission predicates of `r3_run_wrapper.py`

**Method.** Every `ref.append("R-n ...")` was mapped with ast to its function.
R-4..R-6 are attributed through `tree_check`, which formats its tag at run time.
What each predicate reads was read at the cited lines (11 citations, 0 failures).
The preflight predicate calls are at lines 276-278, 284, 286, 287, 289, 290 and
310.

| id | refusal lines (function, def lines) | reads | admits on ANOTHER package's record? | can a completion-gate checker contradict what it reads? |
|---|---|---|---|---|
| R-1 | 240 (preflight 231-324) | amendment bytes vs the nine bound hashes | no | n/a |
| R-2 | 259-271 (preflight) | plans' id lists, the retired ids | no | n/a |
| R-3 | 274 | existence of its own runs/<RUN-ID> | no | n/a |
| R-4 / R-5 / R-6 | tree_check 114-139 (119, 121, 123, 129, 132, 135, 138); calls 276 / 277 / 278 | implementation trees and plans vs their phase-A receipts (git ls-files, git status, sha256) | no | n/a |
| **R-7** | r7_gate_packages 173-181 (179, 181); reg1 153-162 + r7_reg1_verdict 184-187 (187); r7_controls_a1_image 190-196 (194, 196) | (i) raw-result run_status and gate_pass of G1..G4; (ii) REG-1 of G1 (solver/*.ms, *.ms.out/.ms.log/.ms.err, certificates, raw-result.json, solver-events.json) vs RUN-GFPN-ac4487; (iii) raw-result run_status and gate_pass of RUN-GFPN-2c4862 | **yes** | **yes** for (i) and (iii): RUN-GFPN-bfe956 records completed_valid and gate_pass true, and its r3 checker exits 1. (ii) is a comparison separate from G1's checker verdict. All three are what RB-4 replaces (gate packages; the controls_a1 image; REG-1 kept unchanged) |
| R-8 | 203 (r8_requires 199-203) | existence of runs/<req>/manifest.yaml; no field read | yes (existence of a record) | no field is read. Every checker opens manifest.yaml; none disputes that it exists. R-8 admits regardless of the required package's status |
| R-9 | 293 | plan watchdogs vs trial-plan-v2.json | no | n/a |
| R-10 | 297 | host process table | no | n/a |
| R-11 | 303, 307 | count of existing run directories | no (existence only) | n/a |
| **R-12** | r12_contingency 206-228 (209-228); 312 | the replaced package's manifest.yaml `failure_class` (must be infrastructure_error) and its plan entry; every other contingency manifest's `package.replaces` | **yes** (failure_class) | **no checker item reads `failure_class`.** Token counts: v2_check_run 0, a1_check_run 0, r3_check_run 0 (for comparison, run_status 3 / 1 / 3 and gate_pass 0 / 5 / 0). The checker's exit status on the replaced package is a verdict on that package, not on its failure_class. R-12 admits a replacement run of the replaced package, not a package that relies on its result |
| R-13 | 168, 170 (refuse_forbidden_ids 165-170); 320 | plan labels, repair block, task id, forbidden ids, r3 constants | no | n/a |

**Additional facts.**
- **Gate packages G2..G4.** Each has `gate_required: false`, so R-7 (i) does not
  apply to them. Each is admitted on R-8 (the previous gate package's manifest
  exists) and REG-1 (r3_run_wrapper.py 282-287).
- **A checker item, not an admission predicate.** The frozen `a1_check_run.py`
  79-84 reads the controls_a1 image's run_status and gate_pass for every package
  with `controls_a1_gate_required`.
- **Driver-level reads of another package's record.** These are outside RBR-3's
  scope as worded:
  - `_load_build` (v2_driver.py 989-1003): build outcome and npz sha256;
  - `_prior_cells` / `_condition_met` (1006-1013, 1110-1127);
  - `cmd_aggregate` (1248-1326) and `cmd_aggregate_a1` (a1_driver.py 276-393);
  - `resolve_replacement` / `_resolve` (a1_driver.py 243-254);
  - the archived RUN-GFPN-61bba9 parameters (v2_driver.py 642).

**RBR-3 reading, as the draft words it.** The draft's condition: "approvable as
written ONLY IF ... every predicate that admits a package on the recorded result
of ANOTHER package is either RB-4 (gate packages; the controls_a1 image) or reads
no recorded result that a completion-gate checker can contradict."

Census finding:
- The predicates that read another package's record are R-7 (three parts, all
  within RB-4's scope), R-8 (existence only) and R-12 (`failure_class`).
- No predicate other than R-7 admits on another package's recorded run_status or
  gate_pass.
- No checker item reads the field R-12 reads.

Whether R-8's existence test and R-12's `failure_class` count as "a recorded
result that a completion-gate checker can contradict" is for the approval act.

## 5. RBR-4 (RBQ-6), informational

### (a) The four r3 gate packages, from their phase-B-bound bytes

**How the bytes were read.** Every file was read and its sha256 compared with the
TASK-20260924-f1fb0e post-run receipt at read time. Each package's file set on
disk equals its receipt-bound set.

**How children were counted:**
- builder: child/<tag>.spec.json, by job;
- S-1: solver/<tag>.ms.log;
- S-3: solver/<tag>.callgrind.stdout;
- Sage: comparator/stdout.log.

**How SC-4 rows were counted.** The rows were re-derived with the r3 selection
rule, re-implemented rather than imported.

| package (command) | capped children evidenced, by kind | of those, read-back reaches the manifest list through raw-result.json | manifest read-back list / threads list | SC-4 rows (r3 rule) / recorded checker output | wrapped attempts (solver-events.json) |
|---|---|---|---|---|---|
| RUN-GFPN-f6a21a (fixture --p 4111) | 88: build_poly 4, raw_grid 12, S-1 36, S-3 36 | 76: builders 4, S-1 36, S-3 36. The 12 raw_grid read-backs are in child/*.meta.json only (16 metas carry the pair, all equal to the cap) | [{soft 10737418240, hard 10737418240}] / [1] | 36 (36 with retained output) / 36 | S-1 wrapped_calls 36, attempts_total 36, re_solves 0; S-2 0; S-3 callgrind_children_observed 36 |
| RUN-GFPN-902222 (fixture --p 16777291) | 88: build_poly 4, raw_grid 12, S-1 36, S-3 36 | 76 (as above; 12 raw_grid via meta only) | [{soft 10737418240, hard 10737418240}] / [1] | 36 (36) / 36 | S-1 36 / 36; S-2 0; S-3 36 |
| RUN-GFPN-f5412a (anchor-identity) | 7: build_poly 1, S-1 5 (gb_only), Sage 1 | 6: Sage 1, builder 1, S-1 4. **Missing: anchor_comparator_system** (I-10) | [{soft 10737418240, hard 10737418240}] / [1] | 0 (all S-1 records carry `-g`) / 0 | S-1 wrapped_calls 0, attempts_total 0, passthrough_calls_gb_only_true 5; S-2 0; S-3 0 |
| RUN-GFPN-bfe956 (controls) | 19: build_poly 7, raw_grid 4, S-1 8 | **0** | **[] / []** (requested 10737418240) | **0** (8 S-1 outputs retained on disk) / 0 | S-1 wrapped_calls 8, attempts_total 8, re_solves 0; S-2 0; S-3 0 |

For RUN-GFPN-bfe956, RBR-4's expected triple (19, 0, 0) is reproduced.

**Comparison with CORR-20260924-ec044e.** Every statement it makes about
RUN-GFPN-bfe956 is reproduced from the bytes:
- manifest lines 176-183: the lists are [] and [], and the requested cap is
  10737418240;
- raw-result.json has 0 `rlimit_as_child_getrlimit` keys;
- it has one `"threads"` key, at line 516: `"threads": 1,`;
- `child/ctl_S3.meta.json` lines 83-86 carry the pair {10737418240,
  10737418240};
- `solver/ctl_planted_S3.ms.err` line 15 reads `#threads                         1`;
- solver/ holds 32 files for 8 tags;
- `solver-events.json` records wrapped_calls 8 and attempts_total 8.

**No difference in any value.** Two precisions:
- The census read all 11 builder `.meta.json` files, and all 11 carry a pair equal
  to the cap. CORR read one directly and took the other ten from the report.
- The census splits the 11 builder children into 7 `build_poly` and 4 `raw_grid`
  children (ctl_raw_*). CORR calls all of them builder children.

### (b) REG-1 field scope against RB-1..RB-3

`r3_reg1.compare` reads the following (ast list; 6 citations, 0 failures):
- the exclusion list;
- from the reference and the candidate: solver/*.ms, solver/*.ms.out (plus .ms,
  .ms.log and .ms.err), certificates/*.json and raw-result.json;
- from the candidate only: `solver-events.json` (175-197, 282).

It reads no manifest.yaml and no SC-4 output.

| change | does REG-1 (a)-(d), or an X1..X17 exclusion, read a field it changes or adds? |
|---|---|
| RB-1 (solver-events.json attempt records; a recording failure becomes an SE-2 (4) consistency violation) | **Yes.** REG-1's SE-4 (e) test reads the candidate's `solver-events.json`: it must exist and parse; the top-level `consistency_violation` flag and the S-1 / S-2 events' `consistency.ok` decide a FAIL (r3_reg1.py 193-197); the counters are copied (198); the file is quoted verbatim (282). RB-1 adds attempt records to that file and a new cause for the consistency flag. The reference RUN-GFPN-ac4487's solver-events.json is not read |
| RB-2 (manifest resources) | No. REG-1 reads no manifest.yaml |
| RB-3 (SC-4 output) | No. r3_reg1 imports r3_accounting only for the frozen parse functions and EXTRA_VAR_LINE (r3_reg1.py 140, 162) |
| X1..X17 | No exclusion names solver-events.json, the manifest or SC-4 (the scopes are certificate run_id, raw-result metrics.wall_seconds, and target-entry solver / timings / last_f4_round / instructions_callgrind). RB-1 copies (reads) arms.*.solver.rlimit_as_child_getrlimit and threads_executed from the returned result; it changes no raw-result.json field. REG-1 (b) compares those two fields without exclusion |

Whether REG-1 of an r4 G1 against RUN-GFPN-ac4487 remains well defined is for the
approval act (RBR-4 (b)).

## 6. Completion gate

**Integrity (RBR-5).** Passed before any reading, recorded above with full
hashes.

**RBR-1..RBR-4.** Reported with every instance, the method and the readings. The
census states each reading's condition and what it found. It decides nothing.

**Scope (RBQ-1):**
- no solver, valgrind, callgrind_annotate, gp, Sage or builder child;
- no import of a scanned-tree module;
- no run package;
- nothing written outside
  `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/`;
- no frozen, preserved or archived byte changed: the git diff (e) is empty, and
  every read of a bound file was hash-checked.

No D or degree is reported as a result, and no approval recommendation is made.

## 7. Deviations and disclosures

1. **Integrity was run twice.** It ran first as a separate scratch script
   (`<scratchpad>/rbcensus/integrity_precheck.py`, before any census reading),
   then again as phase 1 of `rb_check.py`. Both passed. The card, the executor
   contract, the decision, the two corrections and the draft were read before
   the integrity checks, as the dispatch ordered ("READ FIRST, IN FULL").
2. **`rb_check.py` ran four times.** Three development runs wrote to
   `<scratchpad>/rbcensus/`, and the fourth wrote `readback-census.json`.
   - **Development run 1 stopped at its integrity phase on a SCRIPT defect, not
     a hash mismatch.** The script looked for `bound_hashes` under a top-level
     key `decision`. DEC-20260924-e52eec's top-level key is
     `coordinator_decision`, so the script found 0 of 9 hashes. The scratch
     pre-check, which compared by text, had matched all 9. The script was
     corrected, and every later run matched all 9.
   - That run wrote only a failure JSON to scratch and made no reading.
   - The census readings made by hand had begun after the scratch pre-check
     passed. They did not begin after this failed run.
   - Recorded as an integrity-tool false negative for the Coordinator's review.
3. **Runs 2 and 3 were complete, both with guard counts 0 / 0.** Between runs 3
   and 4, `rb_check.py` changed only to attribute the R-4..R-6 lines to
   `tree_check`. The final file (sha256 below) is byte-identical before and after
   the run that produced `readback-census.json`.
4. **Dispositions were read by hand.** Which field a caller stores, and under
   which key, is data flow. It was read by the executor at the cited lines. It
   is not derived by the script. The script ties the table to the call graph in
   both directions and re-checks every cited line (288 + 14 + 11 + 6 citations,
   0 failures).
5. **Existing census read for cross-reference.** The existing launch census
   (`dev-evidence/launch-census/census.md`, sections CN-1 and CN-4, written for
   r2) was read for cross-reference only. Every result here is re-derived.
6. **Uncapped shell children.** Outside `rb_check.py`, the executor's shell ran
   these read-only utilities: `sha256sum` on the comparator and k5k7 files and on
   the amendment files, `ls`, `find`, `grep`, `ps` and `wc`. None is a solver,
   valgrind, gp, Sage or builder child.
7. **Pre-existing bytecode.** `.pyc` files existed before this task under the
   v1 tree `experiments/EXP-GFPN-05ff43/implementation/__pycache__/`, with mtimes
   before this task. They were recorded in a baseline, and this task added none
   (checked after the final run).
8. **This file** was written by the executor from `readback-census.json`. It is
   not generated by the script.

## 8. Deliverables

- `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/rb_check.py`, sha256
  `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.json`,
  sha256 `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4`
- `experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/readback-census.md`,
  this file; its sha256 is given in the executor's return.
