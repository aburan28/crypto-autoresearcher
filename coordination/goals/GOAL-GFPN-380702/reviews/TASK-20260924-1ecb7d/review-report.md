# TASK-20260924-1ecb7d: red-team review of the childend draft's difference from failclosed

Zero runs, static only. **Observations only.** This report makes no approval
recommendation. It makes no statement about D, the quotient, H-GFPN-9a29be or
HEUR-GFPN-DFLAT. The machine-readable twin is `review-report.yaml` in this
directory. The three helper scripts are reproduced verbatim in appendices A-C, with
sha256 and argv.

| item | value |
|---|---|
| draft under review | AMD-EXP-GFPN-05ff43-20260924-childend, `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml`, sha256 `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b` |
| compared against | AMD-EXP-GFPN-05ff43-20260924-failclosed, `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml`, sha256 `1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c` |
| repository HEAD read | `2f7edb36fe705ea87673760ffe9d521ca0dcaca8` |
| goal / question / experiment / batch | GOAL-GFPN-380702 / RQ-GFPN-c01af8 / EXP-GFPN-05ff43 / BATCH-e409ca |
| archived by | TASK-20260924-7e8a5d |

**Scope.** This is a static reading of RG-1..RG-9 and RGL-1..RGL-5, together with:
- the incorporated rules: failclosed RF-0..RF-8, readbackclose RK-1..RK-7,
  readbackfull RL-1..RL-8 and readbackcover RB-2;
- the frozen implementation-v2 and implementation-v2-a1 trees;
- the r3 base (implementation-v2-r3) and both r3 plans;
- the three archived censuses and the archived review TASK-20260924-f5631b (an input).

The r4 layer does not exist. Every statement about r4 behaviour applies the rules to
the frozen code and the r3 base. FAIL-OPEN, PLANNED-BASIS REFUSAL, PLANNED BASIS
OUTCOME and FAIL-CLOSED FINDING are failclosed's definitions (lines 604-621), which
childend incorporates unchanged (childend 582-612).

## Summary of verdicts

| joint | verdict | one line |
|---|---|---|
| CJ-0 known-answer control | **holds** | The method flags P-16, P-F2 after P-14a, W-1, FO-1 (C and B), PB-1 and the weakened-RG-1 (c) mutation, each at record level and package level. |
| CJ-1 child-end evidence, no fail-open | **holds** | Under RG-1 no path reachable through repository code is FAIL-OPEN. Both FO-1 variants become FAIL. Residual dependence is on unread third-party and interpreter behaviour and on recalled kernel semantics. |
| CJ-2 child-end evidence, no planned-basis refusal | **holds** | Every normal launch at the six call sites is recorded "exec", "frozen_pre_exec_exit" or "no_child" as RG-1 (c) words it. This depends on a host that meets RGL-1 (FC-B). |
| CJ-3 infrastructure-stop scope | **holds** | RG-2 changes no verdict and closes PB-1 definitionally. PB-4 is pre-existing and outside RG-2's class. |
| CJ-4 development harness | **breaks (fail-closed only)** | RG-3's clauses hold on the r3 base, but DV-18 (a), (b) and (e) still STOP by construction through RG-4 (b) (FC-A). |
| CJ-5 readers of the difference | **breaks (PLANNED-BASIS REFUSAL)** | RG-4 (b)'s attribution turns cells m = 4 packages, and any package with an SE-3 / HR-3 re-solve, into FAIL by design (PB-2, PB-3). |
| CJ-6 value classes and neutrality | **holds** | Observations: wall time includes the callback, asynchronous exceptions are consumed in the callback window, and the callback is a registration only by the attribute-level reading of HR-3. |

## 1. Integrity (CRT-2), applied first: PASS

| check | path | computed sha256 | bound / receipt | result |
|---|---|---|---|---|
| (a) childend | `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_childend.yaml` | `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b` | `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b` (from the dispatching session's message, which gives TASK-20260924-5816cd's receipt value `addendum_sha256`; **the receipt was not opened**, not even its one permitted field) | PASS; in file: status draft, approved_by null, approval_decision null (lines 166-168) |
| (b) failclosed | `.../amendments/v2_addendum_failclosed.yaml` | `1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c` | same | PASS |
| (b) readbackclose | `.../amendments/v2_addendum_readbackclose.yaml` | `f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c` | same | PASS |
| (b) readbackfull | `.../amendments/v2_addendum_readbackfull.yaml` | `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1` | same | PASS |
| (b) readbackcover | `.../amendments/v2_addendum_readbackcover.yaml` | `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e` | same | PASS |
| (c) f5631b review yaml | `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml` | `b12600aa82c907471f04e1d42882fbd644b67e0be019ec5c423be12227f34c2f` | TASK-20260924-0c2fdc receipt: same | PASS |
| (c) f5631b review md | `.../reviews/TASK-20260924-f5631b/review-report.md` | `0d368a821368189f3b952ce165a49448e942d9c29c780619028574d2a73967b8` | same | PASS |
| (c) close census md | `experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/readbackclose-census.md` | `ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838` | TASK-20260924-71d070: same | PASS |
| (c) close census json | `.../readbackclose-census/readbackclose-census.json` | `9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa` | same | PASS |
| (c) close census script | `.../readbackclose-census/rk_check.py` | `00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c` | same | PASS |
| (c) successor census md | `.../readbackfull-census/readbackfull-census.md` | `5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7` | TASK-20260924-ddfb69: same | PASS |
| (c) successor census json | `.../readbackfull-census/readbackfull-census.json` | `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158` | same | PASS |
| (c) successor census script | `.../readbackfull-census/rf_check.py` | `ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558` | same | PASS |
| (c) read-back census md | `.../readback-census/readback-census.md` | `2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3` | TASK-20260924-a01341: same | PASS |
| (c) read-back census json | `.../readback-census/readback-census.json` | `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4` | same | PASS |
| (c) read-back census script | `.../readback-census/rb_check.py` | `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64` | same | PASS |
| (d) frozen diff | `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json` | empty output, exit 0, with the pathspecs quoted (git-side globs) and unquoted (shell globs). `git status --porcelain=v1 -- experiments/EXP-GFPN-05ff43/` also printed nothing. | - | PASS |

DP-5 as observed: the write-scope directory did not exist before this task created it.

## 2. CJ-0: known-answer control, reported first. Verdict: holds

**Method.** One method serves CJ-0, CJ-1, CJ-2, CJ-3 and CJ-5, unchanged across
objects: the scratch rule evaluator `rule_eval.py` (appendix B; sha256
`9e8357c6aeba518120d68c5002f5c8e86a5f6f9210b1c48dc03d24be0eb337d7`; output
`rule_eval.out` sha256
`e954d28751b0a47cf73be8744c2b2f9883a6932e1338409ad1448b5fc851ca91`). It reads no file
and imports only `itertools`.

Hand-read path objects, each cited to frozen lines, are evaluated under five encodings
of the rule texts:

| rule set | encodes |
|---|---|
| R0 | readbackclose RK-1 (a)/(b) and RK-3 (b) as worded; RL-3 gaps gate nothing |
| R1 | failclosed as worded: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 as readbackfull 279-282 words it |
| R2 | childend: R1 with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b) |
| R2x | R2 with the RG-4 (b) gap rule switched off; isolates RG-1 and RG-2 |
| R2w | R2 with RG-1 (c) weakened as CJ-0 names |

Each object is placed in a package with k = 0 or 1 other class (B) launch. It is read
under two manifest variants of the requested cap at v2_check_run 64:
- Mr3: r3_run_wrapper 550, which gives None when the wrapper wrote raw-result.json;
- Mc: the cap recorded independently.

The method reports at two levels:
- **Record level.** The recorded child_created, the class, the child_end (under R2,
  R2x and R2w), whether (iii) holds, and whether a record written in another process
  is detected.
- **Package level.** The frozen checker items that fail and the verdict.
  - FAIL-OPEN: one of (i)-(v) holds while the verdict is PASS or PASS_ZL.
  - PLANNED-BASIS REFUSAL: a designed driver-logic outcome gets FAIL, where a
    dependant's frozen logic acts on that outcome or RFR-2 lists its row.

Escapes, raises and hypotheticals are marked not designed.

| object (CRT-4) | record level | package level | flagged |
|---|---|---|---|
| (a) P-16 on readbackclose RK-1/RK-3 as worded (v2_solver 181: `CALL` then `STORE_FAST pid`; census md 200) | R0: child_created **false** for a created child, (iii). R1: undetermined | R0 k = 1 Mc: PASS, **FAIL-OPEN [(ii), (iii), (v)]**. R0 Mr3: FAIL (68-70; the requested cap is None because the wrapper wrote raw). R0 k = 0: FAIL (66-67). R1: FAIL in every variant | yes |
| (a) P-F2 after P-14a (census md 205) | R0: child_created **false**, (iii); the release exception's traceback holds no `_run_child_locked` frame. R1: true (pid at 214 on `__context__`) | R0 k = 1 Mc: **FAIL-OPEN [(ii), (iii), (v)]**; FAIL otherwise. R1: FAIL | yes |
| (a) W-1 (the driver exits before any launch; r3_run_wrapper 491-505) | no launch record | R0: **PASS_ZL with (v)**, both variants, FAIL-OPEN. R1: FAIL (RF-2 (vi)) | yes |
| (b) FO-1 variant C on failclosed (escape before 183; the parent sees the P-7 shape) | R1: class (C), report empty, returncode 1 or -2. The child's pari-stack.json write (r3_entry_v2 75-77) is **detected by nothing** when the recorder-foreign write fails or is interrupted | k = 1: PASS, **FAIL-OPEN [(iv)]**, both variants. k = 0: FAIL (66-67) | yes |
| (b) FO-1 variant B on failclosed (OK at 198; a first exception at 202 caught at 206, a second at 207-208) | R1: class (B), OK, pair read, returncode 1 or -2; detected by nothing | **FAIL-OPEN [(iv)]** at k = 0 and k = 1, both variants | yes |
| (c) PB-1 on failclosed: cells m = 5, every launch refused before fork (v2_solver 166-169), or every created child ERR 97 / empty 99 | every launch class (A), or every launch class (C) | FAIL (66-67) on a driver-written package acted on by the m = 4 `_condition_met` (X-08): **PLANNED-BASIS REFUSAL** for both objects | yes |
| mutation: FO-1 C under childend, R2 unmutated vs R2w (RG-1 (c) accepts any returncode without exec) | R2: child_end **undetermined** (empty report with returncode 1 is not in the set), so the escape is detected. R2w: frozen_pre_exec_exit, class (C), detected by nothing | R2: FAIL in every variant. R2w k = 1: PASS, **FAIL-OPEN [(iv)] again** | yes |

**Result: holds.** The method, unchanged, flags every object CRT-4 names, on its named
condition, and it separates the two levels:
- P-16 and P-F2 after P-14a are record-level (iii) defects. They become package-level
  FAIL-OPEN under readbackclose only with another collected pair and a requested cap
  recorded independently of raw-result.json.
- W-1 is a package-level FAIL-OPEN (v).
- FO-1 C and B are package-level FAIL-OPEN (iv) under failclosed.
- PB-1 is a PLANNED-BASIS REFUSAL under failclosed.
- The weakened RG-1 (c) reopens FO-1 C. The worded RG-1 (c) closes it.

CJ-1 and CJ-3 may therefore be reported as holding where the method finds no break.
The relevant output is appendix D.1.

## 3. CJ-1: child-end evidence, no fail-open. Verdict: holds

**Reading.** failclosed RFR-1 with definitions (i)-(v), applied to RG-1 and RG-4 and
to their interaction with RF-0..RF-3.

Definition (iv) is read as FO-1 read it: a record written by recorder, entry or frozen
caller code in a process other than the installing one. Read literally, it would also
cover the r3 wrapper's own designed records (manifest.yaml, environment.json, a
fallback raw-result.json; r3_run_wrapper 466-505, 567). The wrapper writes those in
its own process by design.

**FO-1 under RG-1.** Both variants were evaluated:
- the recorder-foreign write ok, failed or interrupted;
- the escaped exit status 1 or -2.

The parent's record is child_end **undetermined**. There is no exec, so time_enabled
is 0 and value is 0. The (report, returncode) pair is ('', 1), ('', -2), ('OK', 1) or
('OK', -2), none of them in RG-1 (c)'s set. The record has no class, and the verdict
is FAIL. Under R1 the same rows, with the write failed or interrupted, are FAIL-OPEN
(iv).

**Census paths.** None is FAIL-OPEN under R2.
- PASS: P-1..P-4 (class A); P-6 (ERR 97, C); P-7 (empty 99, C); P-10..P-13 (exec, B);
  an exec that raised after OK (OK 99, B).
- FAIL by 68-70: P-8 and P-9 (OK 98 with a pair not equal to the cap; see PB-4).
- FAIL: P-5a, P-5b, P-16, P-14a/b/c, P-F1 and P-F2 raise, so raw is wrapper-written
  and the record is raised non-null.
- P-C is FO-1.

**Constructed objects.**

| id | object | R2 result | classification / reachability |
|---|---|---|---|
| X1 | an escaped child exits with 99 (variant C) or 98 / 99 (variant B) | frozen_pre_exec_exit, PASS: FAIL-OPEN (iv) in the evaluator | HYPOTHETICAL; not reachable through repository code. See the scan below |
| X2 | a second fork in one recorder call | undetermined, FAIL | fail-closed; the frozen function forks once (181) |
| X3 | the child is gone before the callback reads the list | undetermined, FAIL | fail-closed. It is either not listed, or it is exiting and the counter open fails (recalled) |
| X4 | the callback fires outside a recorder call | returns at once | no record effect |
| X5 | the callback fires in a call recorded child_created false | undetermined, FAIL | fail-closed |
| X6a | the counter is on the wrong pid; the real child exec'd | time_enabled 0 with ('OK', 0): undetermined, FAIL | fail-closed |
| X6b | the counter is on the wrong pid, which execs, while the real child escaped (B) | "exec", class (B), PASS: FAIL-OPEN (iv) in the evaluator | HYPOTHETICAL; needs a live, unreaped non-frozen child of the installing thread during a recorder call. No repository code leaves one: every post-fork return reaps (v2_solver 223, 230, 243-271), and the other launches are synchronous `subprocess.run` calls (v2_common 59; v2_solver 533; a1_pari 121). A child left waiting after a parent-side raise belongs to a package that already FAILs |
| X7 | a pid reused between fork and reap | no effect | the counter binds the task and is read by descriptor (recalled) |
| X8 | exec by a grandchild | the counter is not inherited, so time_enabled is 0: undetermined, FAIL | fail-closed; the non-inheritance is protective |
| X9 | an exec'd Python image (build / raw-grid child, v2_driver 100; comparator, 650) | "exec", class (B) | not FAIL-OPEN. v2_child imports only v2_field and v2_arms (plus numpy, flint), reads only its spec and argv, and runs no recorder, entry or run_child-calling code. Its outputs are detected: an RB-2 (b) read-back source under failclosed, a recorder gap under childend (PB-2). The comparator writes under its argv-named directory. Its script lies under a withheld path and was not read |
| X10 | the escaped process itself execs something | "exec", class (B) in variant B, PASS: FAIL-OPEN (iv) in the evaluator | HYPOTHETICAL. The only `os.exec*` calls in the three trees are v2_solver 204-205 (child path); `subprocess` execs in a grandchild. RG-1 (e) asserts "Such a child neither execs"; RGL-2 names only the exit-code half as a DV-18 (h) item (OB-F) |
| X12 | a timeout SIGKILL between the go byte and exec | ('OK', -9) with no exec: undetermined, FAIL | fail-closed (FC-C); needs a stall of the smallest watchdog, 1800 s |
| X13 | an out-of-memory kill before exec (RGL-4) | undetermined, FAIL | fail-closed (FC-C) |
| X14 | a host without RGL-1's behaviour | undetermined for every created child, FAIL | fail-closed (FC-B) |

**The RGL-2 premise, checked by the scan (appendix A, D.2).**
- The only calls producing exit status 97, 98 or 99 are `os._exit` at v2_solver 196,
  201 and 208, all on the child path.
- Every `SystemExit` raised in the three trees carries a string (exit status 1):
  v2_common 100; a1_driver 52, 224, 233.
- `sys.exit(96)`, `sys.exit(0)` and `sys.exit(0)` at v2_child 60, 69 and 81 run only
  in the exec'd build child.
- The entries re-raise the caught exception unchanged (r3_entry_v2 69-79; r3_entry_a1
  100-110). They call `sys.exit(main())` only on a normal return (84; 115).
- r3_resolve and r3_common hold no handler or `finally` on the unwinding path.
- No signal handler, `register_at_fork`, `atexit`, `faulthandler` or thread is
  installed in the three trees: scan (hooks) finds 0.

Residual dependence: third-party code on the unwinding path (flint, numpy, cypari2 and
its signal layer, yaml) and interpreter shutdown were not read.

**RG-4, lost launch record: holds.** Directory attribution (RG-4 (b)'s last clause)
needs an argv that names a directory.
- The only such launch is the comparator (v2_driver 650, argv names
  `<run dir>/comparator`). It runs once per anchor-identity package, and no other
  launch writes into comparator/.
- A launch record lost in the installing process is a recording failure: RL-1 (d)
  fails the package.
- A recorder call that ends in another process writes no launch record by design
  (RF-1 (b)), and its parent's record is child_end undetermined.

**Files and lines read.**
- The drafts: childend 1-719 and failclosed 1-809.
- The frozen and r3 code: v2_solver.py 1-552 (dis of 181-208), r3_entry_v2.py 1-84,
  r3_entry_a1.py 1-115, r3_resolve.py 1-513, r3_common.py 88-90 and 330-417,
  v2_child.py 1-111, v2_common.py 1-261, v2_driver.py 1-1352, r3_run_wrapper.py 1-583.
- Archived text: census md 100-279 and the f5631b review-report.yaml.
- Scratch output: scan.out.

**What would change the verdict.**
- Code on an escaped child's unwinding path (in the r4 layer or third-party) that ends
  the process with 97, 98 or 99, or that calls an exec function.
- An r4 recorder that leaves a live non-frozen child of the installing thread during a
  later recorder call.
- A kernel or pid-namespace arrangement in which `/proc/self/task/<tid>/children`
  lists pids other than os.fork's.

## 4. CJ-2: child-end evidence, no planned-basis refusal. Verdict: holds

This holds conditionally on the host behaviour RGL-1 states (FC-B).

**Per site and outcome.** The result is identical at all six call sites:
- v2_driver 101 (child job), 166 (msolve, count_instructions true) and 650
  (comparator);
- v2_solver 517 (callgrind);
- a1_health 147 (msolve);
- a1_pari 96 (gp).

child_end depends only on exec and on the (report, returncode) pair. See appendix D.3.

| frozen outcome | lines | child_end | class |
|---|---|---|---|
| ok / crashed / memory_exhausted / timeout after exec | 243-308 | exec | B |
| refused_to_start before fork: invalid cap, driver RSS, other solver, lock | 153-169 | no_child | A |
| refused_to_start, ERR setrlimit with 97 (or 99) | 193-196, 206-208 | frozen_pre_exec_exit | C |
| refused_to_start, empty report with 99 | 186-191, 206-208 | frozen_pre_exec_exit | C |
| refused_to_start, soft read-back mismatch (OK, 98), return at 232 | 200-201, 226-232 | frozen_pre_exec_exit | B (then 68-70 fails; PB-4) |
| crashed, hard-only mismatch (OK, 98) | 200-201 | frozen_pre_exec_exit | B (then 68-70 fails; PB-4) |
| crashed, exec raised (OK, 99) | 204-208 | frozen_pre_exec_exit | B |

The frozen hardware counter opened at 235 (count_instructions true) is a separate
event and changes nothing here.

**Where it may break.**
- *An exec'd child reading time_enabled 0.* This happens only if the counter is not on
  the task that exec'd (X6a) or the host deviates from RGL-1. Both give undetermined
  and FAIL.
- *A timeout kill between the go byte and exec.*
  - t0 is taken at 180, before fork, and the first timeout test (263) runs in the
    first loop pass after 236.
  - A kill before exec needs a stall of the smallest watchdog: 1800 s (builder m3,
    per-target 1800, a1_health DEV_TIMEOUT_S 1800; a1_pari 7200).
  - This is not a normal path. It gives FAIL (FC-C).

**Counter semantics and provenance.** RGL-1 relies on four behaviours:
1. enable_on_exec enables the counter at the monitored task's exec, and time_enabled
   then grows;
2. a counter that is never enabled reads 0 and 0;
3. `/proc/self/task/<tid>/children` lists the calling thread's live children;
4. the after-fork-in-parent callback runs in the parent after fork() returns and
   before os.fork() returns.

These are *recalled* from the perf_event_open and proc manual pages and from CPython's
posix module. They were not opened: documentation is outside the permitted read set,
and the web was not used.

*Internal* provenance:
- the frozen code's own perf_event_attr layout (v2_solver 129-131: disabled bit 0,
  inherit bit 1, exclude_kernel bit 5, exclude_hv bit 6, enable_on_exec bit 12,
  read_format 3) and its read (141-145);
- the stage host's ENOENT for the hardware event (implementation-v2.md 132-135, 395).

The verdict depends on these behaviours holding on the r4 host. DV-18 (f) (xiv)-(xx)
tests them on the delivered code (RGL-5).

**What would change the verdict.** A normal launch path that ends, without exec, with
a (report, returncode) pair outside RG-1 (c)'s set; or an exec that the kernel does not
count as enabling the counter.

## 5. CJ-3: infrastructure-stop scope. Verdict: holds

**Per kind.** The kinds are build, cells m = 5, cells m = 4, fixture4, the fixture /
anchor / controls gates and controls_a1, in both r3 plans. For each, take any outcome
with at least one launch record and no collected pair:
- every launch refused before fork, for host state, the host lock, or driver RSS above
  1 GiB (v2_solver 153-169);
- every created child ERR setrlimit or empty;
- or a mixture of the two.

Such an outcome is FAIL by v2_check_run 66-67 in failclosed and in childend alike, and
RG-2 (a) classes it infrastructure-stop. A mixture with at least one class (B) launch
is not infrastructure-stop and is PASS in both. The evaluator (section CJ-3)
reproduces PB-1 under R1 and shows no planned-basis refusal under R2x for these
objects.

**Frozen sequencing.** The frozen code *does* read these outcomes:
- cells' `_load_build` turns a non-ok build row into "polynomial unavailable"
  (v2_driver 1068-1075);
- an m = 5 cell whose every target was refused ends terminal not_measured (1235-1236)
  and so meets the m = 4 condition `m5_not_measured` (1119-1126);
- the aggregates read cells rows (1259-1267).

The design basis stated in frozen text is narrower:
- the m = 4 conditional cells are the "stopping rule 3 fallback"
  (trial-plan-v2-r3.json 1065; v1->v2 amendment DC-3 m4_fallback 581-587);
- stopping rule 3 names timeout, OOM and crash;
- the frozen driver classes refused_to_start rows `infrastructure_error` (v2_driver
  1186-1188).

In every protocol version the frozen item 66-67 FAILs such a package, so no version
has admitted it as a basis. The driver-RSS refusal (the AC-1 envelope, v2_solver
156-160) is named by RG-2 (d) as a stop for a Coordinator decision.

**RKR-4 (b) rows.** RG-2 changes no verdict. R1 and R2x give the same verdict for
every PASS / PASS_ZL row of the close census's RKR-4 (b) table (md 478, 480, 481, 483,
485, 486, 488). The effect of RG-4 on those rows is under CJ-5 (appendix D.4).

**Narrowest statement.** RG-2 closes PB-1 definitionally. It narrows RF-0 (b), the
rule that the readings' definition of PLANNED BASIS OUTCOME references, so that
infrastructure-stop outcomes are not driver-logic outcomes (OB-B). It changes no
verdict. A planned-basis refusal of a different shape, pre-existing and outside RG-2's
class, is recorded as PB-4.

**What would change the verdict.**
- A frozen text that designates an all-refused m = 5 cell as the m = 4 fallback
  trigger (in particular the driver-RSS refusal).
- A reading that the readings' definitions refer to failclosed's RF-0 (b) as
  failclosed worded it, not as RG-2 (b) re-reads it. Then PB-1 stands as before.

## 6. CJ-4: development harness. Verdict: breaks (fail-closed only)

This is not a FAIL-OPEN and not a planned-basis refusal. RFR-3's conditions hold (the
replacements exist, and no other frozen read changes the computation), with one
sub-item inconclusive.

- **Checker items on NOT_EVALUABLE.** Exactly three items of `r3_checks` depend on the
  REG-1 block: r3_check_run 329-330 (verdict), 331-332 (d_branch) and 333-334
  (exclusion_list_sha256). They are guarded by rid != G1 (327), which holds for a
  development label. The NOT_EVALUABLE block (r3_run_wrapper 158, recorded at 565-566)
  carries neither d_branch nor exclusion_list_sha256. RG-3 (d) matches.
- **argv substitution.** In every argv element of the three commands' launches, the run
  directory appears only as a path prefix of a whole element:
  - child job: `[sys.executable, "-B", implementation-v2/v2_child.py, <rd>/child/<tag>.spec.json]` (v2_driver 98-100);
  - msolve: `-f <rd>/solver/<tag>.ms -o <rd>/solver/<tag>.ms.out` (160-166; v2_solver 331-334);
  - comparator: `[SAGE_PYTHON, COMPARATOR, <rd>/comparator]` (647-650). COMPARATOR lies under the repository and is not redirected;
  - gp: `[..., <rd>/pari/<tag>.gp]` (a1_pari 91-96);
  - health msolve: `-f <rd>/health/<tag>.ms -o ...` (a1_health 141-147).

  After substitution none carries the label or the scratch root. The three commands run
  no callgrind child, so the `--callgrind-out-file=<rd>/...` element (v2_solver 516) is
  not reached (FC-F).
- **Other label- or path-bearing reads.**
  - The child-job spec files carry `"out": <rd>/child/<tag>` (v2_driver 96-99). The
    child reads them (v2_child 56, 68, 80, 95, 100, 104) to place its outputs, and its
    computation does not depend on the value. RG-3 (e) substitutes argv only.
    RF-4 (d)'s "the run directory's name" plausibly covers a path under that directory;
    read literally, it gives a STOP (FC-E).
  - The children inherit GFPN_RUN_DIR and GFPN_V2_PACKAGE (r3_run_wrapper 472). v2_child
    reads no environment variable. msolve, gp and valgrind are not known to read them
    (recalled).
  - The gp script (a1_pari 36-53) and the msolve inputs carry no path.
  - **Inconclusive sub-item.** The comparator script
    (`coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/scratch/k4a_anchor_system.py`,
    v2_common 39) lies under a withheld reviews directory and was not read, so its
    environment reads are unknown.
- **RG-3 (a)-(c) against the r3 base.**
  - (a) r3_run_wrapper 464 reads `r3_common.LADDER_PATH` (r3_common 114) for a sha256
    record only.
  - (b) r3_dv7 301-314 is a `run_child` tracer, which is not carried.
  - (c) r3_run_wrapper 437-440 read the receipts. **But r3_dv12 119 writes commit_sha
    `"dev-synthetic-not-a-commit"`, not HEAD**, so "as r3_dv12.py 119 does" is inexact
    as to the value. r3_check_run 255-256 tests presence only (OB-A).
- **DV-18 STOP through RG-4.** The development packages all leave `child/<tag>.meta.json`
  and `child/<tag>.npz` files that RG-4 (b) attributes to no launch record:
  - controls: build_poly at v2_driver 768, 801, 816; raw_grid at 782, 805;
  - anchor-identity: build_poly at 671;
  - controls-a1: build_poly at a1_driver 146.

  RL-6 (c') ("RL-3 lists no recorder gap"), RG-7 (i) (17) and RG-3 (d) ("Any other
  failing item ... is a STOP") then STOP DV-18 (a), (b) and (e). The archived r3 G3 and
  G4 packages carry exactly these files (readback census md 433-434, 444-451).

**What would change the verdict.** An RG-4 attribution that attributes the child-job
outputs, and the SE-3 / HR-3 renamed files, to their launch records.

## 7. CJ-5: readers of the difference. Verdict: breaks (PLANNED-BASIS REFUSAL)

The break is found while listing the readers of the RG-4 attribution. CRT-3 names CJ-2
and CJ-3 as the planned-basis joints; this refusal comes from RG-4, which neither CJ-2
(RG-1) nor CJ-3 (RG-2) covers. It is reachable in ordinary operation, and no
interpreter or operating-system behaviour is needed.

**Readers in the r3 base.** None reads child_end, child_end_observer, the
infrastructure-stop class or the RG-4 attribution. From scan (names):
- stdout_path and stderr_path occur only as run_child's parameters (v2_solver 149, 171,
  177, 188-189, 299);
- "child_end" occurs only as the event name of the r3 development tracer (r3_dv7 308,
  616-618; r3_devchecks_more 668);
- "time_enabled_ns" occurs as a key of the frozen hardware counter's returned block
  (v2_solver 144; OB-E).

**Readers in the rules.**

| value | readers | changes what is computed? |
|---|---|---|
| child_end | RG-1 (d) classes, feeding the RF-3 (a) verdict; RF-0 (c); RF-3 (b) ("an undetermined value"); RG-7 (f) (xiv)-(xx), (i) (14); RG-8 | narrows PASS by design; no change on normal paths (CJ-2) |
| child_end_observer | RG-1 (c) derivation only; epsilon (RG-8) | no |
| stdout_path, stderr_path | RG-4 (b) attribution, then the RL-3 gap list, then the RF-3 (a) verdict; RL-6 (c'); RG-7 (i) (17) | **YES: PB-2, PB-3, FC-A** |
| infrastructure-stop class | RF-0 (b) driver-logic scope; RF-3 (b) stop record | no verdict (CJ-3) |
| RG-4 attribution | RF-3 (a) ("no RL-3 recorder gap", failclosed 389-391, with RG-4 (b) "a recorder gap makes the verdict FAIL"); RK-3 (b) (iii) (zero-launch packages hold no such file); RL-6 (c'); RG-7 (i) (17) | **YES** |
| REG-1 | solver-events.json outside the compared sets by the globs (RL-7); the SE-4 (e) test reads the top-level flag and the S-1 / S-2 events | no; the verbatim quote grows |
| key and byte sweeps | r3_check_run 189-211 (top-level keys), 214-224 (five files, not solver-events.json); a1_check_run 51-58 (every .json/.yaml/.txt/.log, for `a1_common.FORBIDDEN_TASK_ID`, a1_common 57) | no; the new values do not carry that id |
| frozen checkers | v2_check_run and a1_check_run read the manifest's resources, raw-result.json and certificates | no |

**What would change the verdict.** An RG-4 (b) that attributes three kinds of file:
1. `<out>.npz` and `<out>.meta.json`, where out is the value in the spec file that the
   launch's argv names exactly (v2_driver 96-100);
2. the files an SE-3 / HR-3 event records under renamed_files (r3_resolve 235), to the
   attempt whose files they were;
3. the value of an argv element `--callgrind-out-file=<path>` (v2_solver 516).

## 8. CJ-6: value classes and neutrality. Verdict: holds

**Values recorded by the frozen parent.**
- argv, env, cwd, cap, timeout, lock and count_instructions are unchanged, and so is
  the order of 210-236. The callback completes inside os.fork before 182 runs in the
  parent.
- The frozen hardware counter (v2_solver 126-136, 233-235, 280-282) is a separate
  event. A software task-clock event occupies no hardware counter, so the multiplexed
  flag is unaffected (recalled).
- **wall_seconds (272-274) does include the callback's duration**, because t0 is taken
  at 180, before fork. The same interval counts against timeout_s (263). Transfer
  assumption (3) discloses the added work, and REG-1 excludes wall-clock fields
  (reg1-exclusion-list.json X2, X3).

**Asynchronous exceptions (OB-C).** A Python-level signal handler that runs while the
callback's bytecode executes raises inside the callback. Two things then stop it:
- the callback "catches every exception its own code raises";
- CPython discards an exception escaping an at-fork callback as unraisable (recalled).

So a KeyboardInterrupt that, without the callback, would surface at line 181 in the
parent (P-16: a raise, wrapper-recorded, FAIL) is consumed, and the parent continues.
This is not a FAIL-OPEN under (i)-(v): the child is recorded and its pair read. It is a
change in the frozen parent's control flow under a signal, and RG-1 (f)'s list does not
name it.

**Function replacement.** By the letter of HR-3 / RL-5, the registration replaces
nothing: HR-3 is a closed list of in-process replacements of module attributes, read
back by attribute at install. The callback is, however, code that runs inside the
frozen call, between fork() and the return of os.fork(). RG-8's "a registration, not a
function replacement" therefore rests on the attribute-level reading of HR-3.

## 9. Counterexamples

### PB-2: RG-4 (b) and the child-job outputs (joint CJ-5; also FC-A)

**PLANNED-BASIS REFUSAL** as failclosed's definitions word it, **by design of RG-4 (b)**.
The difference introduced it: under failclosed as worded the same outcomes PASS
(evaluator R1 and R2x). It is reachable on every normal path of the kinds named, and
needs no interpreter or operating-system behaviour.

| step | where | what |
|---|---|---|
| 1 | trial-plan-v2-r3.json 1054-1059 (RUN-GFPN-5bf619, order 10) | A cells m = 4 package lists arm raw, disposition run, no condition. So does every cells m = 4 package of both r3 plans: v2-r3 orders 10-12, 17-19 and 24-26; a1-r3 orders 6-8. |
| 2 | v2_driver.py 1016-1092, 1130-1161; census md 357-359 | cmd_cells runs `_run_cell` for the raw arm. Target 0 always runs: there is no early stop, and the 86400 s per-cell watchdog cannot fire first. It calls `raw_grid(..., "grid_" + tag, ...)` at 1161. |
| 3 | v2_driver.py 133-136, then 92-102 | child_job sets `spec["out"] = <run dir>/child/grid_raw_t<i>` (96; no to_cache). It writes the spec to `<run dir>/child/grid_raw_t<i>.spec.json` (98-99) and builds argv `[sys.executable, "-B", implementation-v2/v2_child.py, <spec path>]` (100). It calls run_child with stdout_path `.../grid_raw_t<i>.stdout` and stderr_path `.../grid_raw_t<i>.stderr` (101). |
| 4 | v2_child.py 96-104 | The exec'd capped child writes `<out>.npz` (100) and `<out>.meta.json` (104). The meta carries the child's own getrlimit pair (103). Under RG-1 the launch record is child_end "exec", class (B). |
| 5 | v2_driver.py 140-146 | The driver loads and removes the .npz (144). `child/grid_raw_t<i>.meta.json` stays. The archived r3 G1 package holds 16 such files (readback census md 431: 12 from raw_grid, 4 from uncached builds). |
| 6 | childend 423-434 (RG-4 (b)) | The meta file is not the record's stdout_path or stderr_path. It is not a path the argv names exactly (the argv names the .spec.json), it is not under a directory the argv names, and it is not a listed non-launch write. **It is a RECORDER GAP.** Yet readbackcover 230-231 makes every `child/*.meta.json` a designed RB-2 (b) read-back source. |
| 7 | failclosed 389-391 (RF-3 (a)) with childend 432-434 | "a recorder gap makes the verdict FAIL": **FAIL**. This holds although every launch record is class (A), (B) or (C), the frozen checker exits 0, and raw-result.json is driver-written. |
| 8 | failclosed RF-0 (d), RF-3 (b); readbackfull 286-306 (RL-4) | Two things are refused, a designed stop: the next package (RUN-GFPN-7fc9a4 requires RUN-GFPN-5bf619), and the aggregates that read the package (RUN-GFPN-cfe003; RUN-GFPN-9bf947; v2_driver 1252-1267, a1_driver 276-393; X-09, X-10). |
| 9 | census md 488; failclosed 616-617; childend 349-353 | The outcome is the close census's RKR-4 (b) row 488 (cells m = 4 with a collected pair, "the raw cell always launches", PASS there). It has collected pairs, so it is not an infrastructure-stop outcome and stays a driver-logic outcome. The aggregates' frozen logic acts on it, so it is **a planned basis outcome that receives FAIL by design.** |

**The same file class elsewhere.**
- G1 / G2 fixture: build_poly without to_cache at v2_driver 317; raw_grid at 348.
  RKR-4 (b) row 478.
- G3 anchor-identity: 671. Row 478.
- G4 controls: 768, 782, 801, 805, 816. Row 478.
- controls_a1: a1_driver 146. Row 480; read by the frozen a1 checker of packages 2-9
  (X-13).
- fixture4: 548. Row 481.

Uncached builds also leave `child/<tag>.npz` (v2_child 38), and no rule removes it.

For G1..G4 and F-4, the planned-basis status rests on RFR-2's enumeration of the
RKR-4 (b) rows: the wrapper (R-7) reads their outcomes, not frozen driver logic. Their
FAIL is at least a fail-closed finding, and its cost is every r4 package, through the
R-7 gate.

The archived r3 packages carry these files: G1 and G2 16 each, G3 1, G4 11 (readback
census md 431-434, 444-451).

**Cheapest mutation.** Attribute to a launch record the files `<out>.npz` and
`<out>.meta.json`, where out is the value carried by the spec file that the record's
argv names exactly (v2_driver 96-100). That spec file is a positive record, consistent
with RF-0 (a).

### PB-3: RG-4 (b) and the SE-3 / HR-3 renamed files (joint CJ-5)

**PLANNED-BASIS REFUSAL** by design of RG-4 (b), on every package in which the approved
re-solve rule re-solves at least once. The difference introduced it: R1 and R2x give
PASS. No interpreter or operating-system behaviour is needed.

| step | where | what |
|---|---|---|
| 1 | r3_resolve.py 373-390, then 248-319; 397-409 (a1 entry) | An S-1 solve (not gb_only), or an S-2 health system, has an attempt carrying the SSF signature (61-74). Fewer than K + 1 = 6 attempts were made (r3_common 88), so the loop reaches `_rename` at 310. |
| 2 | r3_resolve.py 224-238; r3_common.py 90 | `<tag>.ms.out`, `.ms.log` and `.ms.err` are renamed to `<name>.ssf-attempt<k>` inside solver/ (S-1) or health/ (S-2). They are listed in the event's renamed_files (235). |
| 3 | r3_resolve.py 258-263 | The frozen solve is called again. The new attempt's launch writes `<tag>.ms.*` afresh, and the renamed files remain. |
| 4 | childend 423-434 | No launch record names a renamed file as stdout_path or stderr_path, no argv names it, and no argv names its directory. The renamed files are **RECORDER GAPS**, so the verdict is FAIL (RF-3 (a)). |
| 5 | census md 485, 488; v2_driver 1119-1126, 1259-1267 | A cells package (m = 5 or 4) with one re-solve and otherwise measured targets is a driver-logic outcome with collected pairs. The m = 4 package's `_condition_met` (X-08) and the aggregates (X-09, X-10) read it, so it is **a planned basis outcome that receives FAIL by design.** controls_a1's health check (S-2) is affected the same way. |

**Cheapest mutation.** Attribute each file that an SE-3 / HR-3 event records under
renamed_files (r3_resolve 235, a positive record) to the attempt whose files they were.

### PB-4: a collected pair different from the cap (outside RG-2; pre-existing)

This is a **PLANNED-BASIS REFUSAL** as the definitions word it.
- **Definitional and pre-existing.** It is identical under failclosed, the difference
  did not introduce it, and it lies outside RG-2's class because a pair is collected.
- **Not on a normal path.** It is reachable only if the child's getrlimit read-back
  differs from the value it set at v2_solver 193. That needs an external prlimit on the
  child between 193 and 197, or a non-conforming kernel (recalled).

| step | where | what |
|---|---|---|
| 1 | v2_solver.py 193, 197-198, 200-201 | setrlimit(cap, cap) succeeds. getrlimit reads soft != cap (P-8) or hard != cap (P-9). The child writes "OK soft hard" and exits 98. |
| 2 | v2_solver.py 226-232 (P-8) or 236-308 (P-9) | The parent reads the pair at 227 and returns refused_to_start (P-8), or crashed with returncode 98 (P-9). |
| 3 | childend 283-314 (RG-1 (c), (d)) | child_end is "frozen_pre_exec_exit" (OK, 98) and the class is (B). RG-2 (a) does not apply, because a pair is collected. |
| 4 | v2_driver 184-186, 150-154; readbackcover 221-240; readbackfull 272-274; v2_check_run 68-70 | The pair reaches the manifest list. The frozen item compares it with the requested cap and FAILs. |
| 5 | v2_driver 1119-1126; census md 485 | On a driver-written cells m = 5 package, this is a driver-logic outcome that the m = 4 `_condition_met` reads: a planned basis outcome that receives FAIL by design. The design intends that FAIL, because the recorded cap differs from the requested one. |

## 10. Fail-closed findings (never a bar; each with its cost)

| id | joint | finding | cost |
|---|---|---|---|
| FC-A | CJ-4 / CJ-5 | RG-4 (b) makes DV-18 (a) controls, (b) anchor-identity and (e) controls-a1 STOP by construction. Their child-job outputs are recorder gaps (v2_driver 768, 782, 801, 805, 816, 671; a1_driver 146), and RL-6 (c'), RG-7 (i) (17) and RG-3 (d) require none. | The r4 stage STOPs at DV-18; no r4 package runs. |
| FC-B | CJ-2 | Suppose the r4 host's kernel lacks `/proc/<pid>/task/<tid>/children` (built without CONFIG_PROC_CHILDREN; recalled), or refuses perf_event_open for a per-task software counter on the child (paranoid policy, missing capability or seccomp; recalled). Then every created child is child_end undetermined, and every package with a created child FAILs. DV-18 (f) (xiv) STOPs first. This is host-conditional and not testable here. | The r4 stage STOPs at DV-18 on such a host. |
| FC-C | CJ-2 | A created child killed before exec is ('OK', -9) with no exec: child_end undetermined, FAIL. The kill is either a timeout SIGKILL after the go byte (which needs a stall of at least 1800 s) or the out-of-memory killer (RGL-4). | That package FAILs and its dependants stop. |
| FC-D | CJ-5 | When a callgrind child's outcome is not ok, the function returns before removing `<rd>/solver/<tag>.callgrind.out` (v2_solver 521-524; removal only at 549). The file is attributed only if the argv element `--callgrind-out-file=<path>` (516) counts as the argv naming the path exactly; otherwise it is a recorder gap. G1/G2 and cells m <= 4 target 0 run callgrind. | That package FAILs (depends on the reading). |
| FC-E | CJ-4 | RG-3 (e) substitutes argv only. The child-job spec files carry out = `<development run dir>/child/<tag>` (v2_driver 96-99), and the child reads them (v2_child 56-104). Accepted if RF-4 (d)'s "the run directory's name" covers paths under that directory. | A DV-18 STOP under the literal reading ("any other frozen read of the label ... is a STOP"). |
| FC-F | CJ-4 | Latent. RG-3 (e) STOPs on "any occurrence of the development run directory in argv other than as a path prefix", and `--callgrind-out-file=<rd>/...` (v2_solver 516) is such an occurrence. DV-18's three commands run no callgrind child. | None now. |

## 11. Observations outside the definitions

- **OB-A.** RG-3 (c) requires commit_sha equal to HEAD "as r3_dv12.py 119 does", but
  r3_dv12 119 writes `"dev-synthetic-not-a-commit"`. Both values pass, because
  r3_check_run 255-256 tests presence only.
- **OB-B.** RG-2 re-reads RF-0 (b), which the incorporated definition of PLANNED BASIS
  OUTCOME references. childend 611-612 states that no definition is reworded: the
  definition's words are unchanged, but its referent is narrowed. Whether that is
  within "these readings, unchanged" (failclosed 705-708) is for the approval act. This
  review makes no ruling.
- **OB-C.** Asynchronous exceptions are consumed in the callback window (section 8).
- **OB-D.** RG-1 records no binding between the counter's pid and the pid that the
  frozen function reaped. The returned record carries no pid, and RK-1 (b) records a
  pid only on raise. The binding rests on the /proc children diff (X6).
- **OB-E.** Two name collisions. "time_enabled_ns" is already a key of the frozen
  returned record's instructions block (v2_solver 144), from the hardware counter
  opened with inherit (129). "child_end" is a development tracer's event name (r3_dv7
  308). A recorder that read the frozen block would read the wrong event, and
  DV-18 (f) (xiv) would STOP.
- **OB-F.** RGL-2 names only the exit-code half of RG-1 (e)'s premise as a DV-18 (h)
  closure item. The "neither execs" half is not named.
- **OB-G.** The comparator script and the fixture JSON files that v2_common 36-39
  names lie under withheld reviews directories. They were not read.

## 12. Interpreter and operating-system behaviours relied on (CRT-6)

| behaviour | provenance | verdict dependence |
|---|---|---|
| CPython runs Python-level signal handlers in the main thread at bytecode check points (after a CALL completes, at function entry, on backward jumps), and the handler's exception appears there. PyOS_AfterFork_Child clears pending signals in the child. | recalled | FO-1 reachability (CJ-0 (b); CJ-1 FO-1 rows); OB-C |
| An uncaught exception gives exit status 1. An uncaught KeyboardInterrupt re-raises SIGINT (wait status -2). SystemExit(code) exits with code (a string gives 1, None gives 0). A failed flush at shutdown gives 120. | recalled | CJ-1: the RGL-2 premise that no escaped exit status is in {97, 98, 99}. CJ-1 holds only with it. |
| os.fork runs after_in_parent callbacks in the parent after fork() returns and before os.fork() returns, also when fork() fails. An exception escaping a callback is discarded as unraisable. subprocess without preexec_fn runs no at-fork callback. | recalled (CPython posix, _posixsubprocess) | CJ-1 (P-5b row; no callback from subprocess.run); CJ-6 (OB-C); RG-1 itself (RGL-1) |
| perf_event_open: a counter opened disabled with enable_on_exec is enabled at the monitored task's exec (after the point of no return), and time_enabled then grows. A counter never enabled reads 0 and 0. The descriptor stays readable after the task is reaped. Without inherit, the counter is not copied to the task's children. Opening on an exiting task fails. A software task-clock event uses no hardware counter. | recalled; internal for the frozen attr layout (v2_solver 129-131) and read (141-145) | CJ-1 (X3, X7, X8); CJ-2 (every "exec" and "frozen_pre_exec_exit" row); CJ-6 |
| `/proc/<pid>/task/<tid>/children` (Linux 3.5+; CONFIG_PROC_CHILDREN since 4.2) lists the thread's children, including exited unreaped ones, in the reader's pid namespace. It is unreliable if children exit during the read. | recalled; this host's /proc was not read (outside the permitted read set) | CJ-1 (X3, X6); CJ-2 (FC-B) |
| Per-task user-only counting on one's own child is permitted at perf_event_paranoid <= 2 upstream. It is refused at stricter distribution levels without a capability, or under seccomp. ENOENT for a hardware event means the call reached event initialisation. | recalled; internal for the stage host's ENOENT (implementation-v2.md 132-135, 395) | FC-B only |
| The kernel stores RLIMIT_AS as set, and getrlimit returns it unless another process changes it. | recalled | PB-4 reachability only |
| The signal layer loaded with cypari2 converts SIGINT / SIGHUP / SIGALRM outside its protected blocks into Python's SIGINT handling, and error signals into a diagnostic and signal death. It raises SystemExit only inside protected blocks, without a code. | recalled (third-party, not read) | CJ-1 residual dependence |

## 13. red_team_report

- **id / task_id:** TASK-20260924-1ecb7d / TASK-20260924-1ecb7d
- **claim_under_review:** the DRAFT AMD-EXP-GFPN-05ff43-20260924-childend (sha256
  `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b`): its difference
  from failclosed (RG-1..RG-9), read with everything incorporated, on joints
  CJ-0..CJ-6.
- **objections:**
  1. PB-2. RG-4 (b) attributes no child-job output to any launch record. As a result,
     every cells m = 4 package FAILs by design, and so do every r4 gate package,
     controls_a1 and F-4. The same meta files are a designed RB-2 (b) read-back source.
  2. PB-3. RG-4 (b) makes the files that the SE-3 / HR-3 rule renames into recorder
     gaps, so any package with one re-solve FAILs by design.
  3. FC-A. DV-18 (a), (b) and (e) STOP by construction, before any package.
  4. PB-4 (definitional, pre-existing). A collected pair different from the cap is a
     planned basis outcome FAILed by 68-70. RG-2 does not reach it, and it is not on a
     normal path.
  5. RG-1 holds on repository code, but two of its premises rest on unread third-party
     and interpreter behaviour: that an escaped child never execs, and that it never
     exits with 97, 98 or 99. RGL-2 names only the exit-code half (OB-F).
  6. RG-2 closes PB-1 definitionally, through RF-0 (b) (OB-B).
- **required_controls:**
  1. A zero-run listing check. Apply RG-4 (b), exactly as worded, to the file listings
     of RUN-GFPN-f6a21a, RUN-GFPN-902222, RUN-GFPN-f5412a and RUN-GFPN-bfe956 (bound by
     the TASK-20260924-f1fb0e post-run receipt). The prediction is 16, 16, 1 and 11
     unattributed `child/*.meta.json` files, plus the uncached builders' .npz files.
  2. A development check of RG-4 on a package with an SE-3 re-solve and with a failing
     callgrind child. RG-7 lists neither.
  3. Run DV-18 (f) (xiv) first on the r4 host, with a negative control: a child that
     never execs must read time_enabled 0 and value 0.
  4. Extend the RGL-2 DV-18 (h) scan to exec calls on every unwinding path of the r4
     closure.
- **counterexample_or_mutation:** PB-2 (cells m = 4, RUN-GFPN-5bf619 first). The
  cheapest mutation that removes PB-2 and PB-3 extends RG-4 (b)'s attribution with
  three kinds of file:
  1. `<out>.npz` and `<out>.meta.json` from the argv-named spec file (v2_driver 96-100);
  2. the files recorded under renamed_files (r3_resolve 235);
  3. the value of `--callgrind-out-file=<path>` (v2_solver 516).

  The known-answer mutation of RG-1 (c) reopens FO-1 C.
- **baseline_comparison:** not applicable. The object is a recording, verdict and
  development-harness protocol.
- **heuristic_challenges:** none in scope (CRT-6). **cost_model_challenges:** none in
  scope; the stage costs are listed with FC-A..FC-F.
- **reduction_and_scope_challenges:**
  1. Definition (iv), read literally, covers the wrapper's own designed records. It is
     read here as FO-1 read it.
  2. PB-2's gate and F-4 cases rest on RFR-2's enumeration of RKR-4 (b) rows. Its
     cells m = 4 and controls_a1 cases do not.
- **proof_architecture_challenges:** a compositional attack on the difference.
  - Switching RG-4 (b) off (R2x) leaves every RKR-4 (b) row's verdict equal to
    failclosed's.
  - Keeping it turns rows 478, 480, 481, 485 (after a re-solve) and 488 to FAIL.
  - Weakening RG-1 (c)'s returncode set reopens FO-1 C, so that set carries the
    variant-C closure.
- **narrowest_supported_statement:** on the r3 base and the drafts' text, with zero
  runs:
  - RG-1 closes FO-1 in both variants and yields no FAIL-OPEN on any path reachable
    through repository code (CJ-1). The residual dependence is on unread third-party and
    interpreter behaviour and on recalled kernel semantics.
  - RG-1 records every normal launch at the six sites as its rule words it (CJ-2), on a
    host meeting RGL-1.
  - RG-2 changes no verdict and closes PB-1 definitionally (CJ-3).
  - RG-3's clauses hold, but DV-18 still STOPs by construction (CJ-4, fail-closed).
  - RG-4 (b) introduces planned-basis refusals on cells m = 4 packages and on any
    package with a re-solve (CJ-5; PB-2, PB-3).
  - CJ-6 holds, with observations.
  - PB-4 is definitional and pre-existing.
  - The known-answer control holds.
- **next_concrete_action:** run the zero-run listing check (required control 1). List
  the child/, solver/, health/, comparator/ and pari/ files of the four archived r3
  gate packages. Apply RG-4 (b)'s three attribution clauses and its non-launch list as
  worded, and record every file attributed to no launch record.
- **artifact_paths:** `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.yaml`,
  `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d/review-report.md`

## 14. Review attestation

- **task_id / role:** TASK-20260924-1ecb7d / red-team
- **joints_owned:** CJ-0, CJ-1, CJ-2, CJ-3, CJ-4, CJ-5, CJ-6
- **verdicts:** CJ-0 holds; CJ-1 holds; CJ-2 holds; CJ-3 holds; CJ-4 breaks; CJ-5
  breaks; CJ-6 holds
- **read_sibling_reports:** none
- **blind_from_not_opened:**
  - `ledger/decisions/DEC-20260924-844896.yaml`
  - `ledger/corrections/CORR-20260924-862f7d.yaml`
  - `ledger/handoffs/TASK-20260924-64c8fe.yaml`
  - `ledger/handoffs/TASK-20260924-5816cd.yaml`
  - `ledger/goals/GOAL-GFPN-380702/goal.yaml`
  - `knowledge/techniques/KN-TECH-79d6b9.md`
  - `ledger/decisions/DEC-20260924-8fa3d4.yaml`
  - `ledger/corrections/CORR-20260924-7fcbd2.yaml`
  - `ledger/handoffs/TASK-20260924-7e9d3e.yaml`
  - `ledger/handoffs/TASK-20260924-eb2540.yaml`
- **dispatcher_withheld_not_opened:**
  - `ledger/handoffs/TASK-20260924-7e8a5d.yaml`
  - everything under `coordination/goals/GOAL-GFPN-380702/batches/`
  - `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-5816cd/`, not even the
    one permitted field: the value came from the dispatching session
  - `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-eb2540/`
  - `coordination/bus/` and `coordination/events/`
  - every directory under `coordination/goals/*/reviews/` other than
    `reviews/TASK-20260924-f5631b/`
  - git commit messages, pull requests and the web
- **blindness_disclosures:**
  1. The draft itself summarizes DEC-20260924-844896's rulings and plans (childend 4-26,
     64-67, 613-622, 644-648, 694-696) and names CORR-20260924-862f7d's role (245-247).
     Those were read as part of the draft.
  2. The f5631b review (an input) records its own read of the TASK-20260924-eb2540
     receipt field and the member names it saw (its yaml 40-47, 883-889). That was read
     as part of the input.
  3. v2_common.py 36-39 names paths under two withheld reviews directories
     (TASK-20260923-404bf9, TASK-20260923-58953e). The path strings were seen; the
     directories were not opened.
  4. One git child, `git status --porcelain=v1` with no pathspec, traversed the whole
     worktree without printing content: it printed nothing.
  5. The scan walked tools/ and harness/ for .py file names only.
- **paths_read:** as listed in `review-report.yaml`
  (`review_attestation.paths_read`: full, partial, grep scopes, hashed only, counts and
  listings, not read).
- **commands (argv):** in order below. `<repo>` is the repository root, and
  `<scratch>` is the session scratch directory outside the repository.
  - git children:
    1. `git rev-parse HEAD`
    2. `git status --porcelain=v1`
    3. `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'`
    4. the same diff with shell-expanded globs
    5. `git status --porcelain=v1 -- experiments/EXP-GFPN-05ff43/`
    6. `git status --porcelain=v1 --untracked-files=all -- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-1ecb7d experiments/EXP-GFPN-05ff43` (final check)

    No git write of any kind.
  - shell children: `sha256sum`, `ls`, `ls -d`, `ls -la`, `wc -l`, `wc -c`, and
    `mkdir -p` (for `<scratch>/rt_1ecb7d` and the write-scope directory). Also
    `cat -n`, `sed -n`, `awk`, `head`, `cut`, `grep -n` and `grep -c`, and
    `python3 --version`.
  - python3 children:
    - `python3 -B` one-line readers (receipt key names and path_sha256; childend status
      by yaml; both r3 plans; watchdogs; reg1-exclusion-list.json);
    - `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B <scratch>/rt_1ecb7d/scan.py <repo>`;
    - `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B <scratch>/rt_1ecb7d/rule_eval.py`, two runs;
    - two python3 heredoc edits of rule_eval.py;
    - `python3 -B <scratch>/rt_1ecb7d/name_check.py`: first on the two deliverables;
      then, after its rewrite (DV-7), on its own source, scan.py, rule_eval.py and the
      template, and again on the two deliverables;
    - one `python3 -B` one-liner that printed md lines 1390-1394 with every listed word
      masked (DV-7);
    - `python3 -B` yaml.safe_load parse checks of review-report.yaml;
    - one python3 heredoc that assembled this file from `<scratch>/rt_1ecb7d/md_template.md`
      and the scratch scripts and outputs.
- **guard and import attestation.** No module of
  `experiments/EXP-GFPN-05ff43/implementation*/`, `tools/` or `harness/` was imported,
  executed or run.
  - scan.py's audit hook refused imports of 256 scanned module names (sha256 of the
    sorted list `4200f056c940e60770363c6079cb9cac458676e2cf8cc35604f59dd186d012ef`; no
    collision with a standard-library or loaded module). It also refused every
    process-launch event. Its self-test refused both, and the attempt counts were
    import 0, launch 0.
  - rule_eval.py reads no file.
  - There was no msolve, valgrind, callgrind_annotate, gp, Sage or builder child, no
    perf_event_open call, and no run package.
- **scratch files** (`<scratch>/rt_1ecb7d/`; the literal path contains a word the CRT-7
  list covers):

  | file | purpose | sha256 |
  |---|---|---|
  | words.txt | CRT-7 word list, placed by the dispatching session; read at run time only; words never printed | `c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268` |
  | scan.py | static scan with guard (appendix A) | `5548e783ec9a9a2e520f3836491cc83dabe5adbdf89e2b2437db04f0caa642e3` |
  | scan.out | its output | `80cd213c7c12ab63930c6c85d5be6c36a55a396d27e7eba4ef89092c73c5246a` |
  | rule_eval.py | rule evaluator (appendix B) | `9e8357c6aeba518120d68c5002f5c8e86a5f6f9210b1c48dc03d24be0eb337d7` |
  | rule_eval.out | its output | `e954d28751b0a47cf73be8744c2b2f9883a6932e1338409ad1448b5fc851ca91` |
  | name_check.py | CRT-7 self-check (appendix C) | `0eebe3a8c287ec55adae2d6310e6bbf20aaae57549be1eb6cdfdcfc3e613f273` |
  | name_check.out | its output on the two deliverables | (listed in the return) |
  | md_template.md | the prose of this file before the appendices were inserted | (listed in the return) |

  Nothing was written outside the repository and the scratch directory by a command of
  this review.
- **inference:**

```yaml
requested_policy: review-adversarial
agent_binding: red-team, at the policy's default reasoning effort, as the dispatching session arranged
resolved_model_id: null   # none supplied by the dispatching session; none invented
model_verified: false
fallback_used: false
bedrock_used: false
```

- **deviations:**
  - **DV-1.** The first git child was `git status --porcelain=v1` with no pathspec. It
    traversed the whole worktree and printed nothing.
  - **DV-2.** Five archive receipts (0c2fdc, 71d070, ddfb69, a01341, f1fb0e) were read
    for their key names as well as path_sha256. None of them is withheld.
  - **DV-3.** rule_eval.py was edited once before its first run and once after it.
    - Before: the class under R0 was taken on R0's own record, and R2x was added for
      the constructed objects.
    - After: the planned-basis flag was gated on designed outcomes.

    The first output was overwritten. The FAIL-OPEN and PB-1 known-answer flags were the
    same in both runs.
  - **DV-4.** Not every input was read in full. No verdict rests on an unread part,
    except the CJ-4 comparator sub-item, which is marked inconclusive.
  - **DV-5.** Interpreter, library and kernel behaviour is recalled (section 12).
  - **DV-6.** implementation-v2.md (128-137, 393-399) and reg1-exclusion-list.json were
    read. Both are frozen, hash-bound files that the card's input list names only
    through their directories.
  - **DV-7.** The first version of name_check.py spelled out the permitted prohibition
    flag's key inside a regex. Once reproduced in appendix C, that put a listed word
    into a pattern, and the first run flagged it (md line 1393). The script was
    rewritten to recognise the flag line structurally after masking, and this file was
    reassembled and re-checked. To locate the hit, one python3 one-liner printed md
    lines 1390-1394 with every listed word masked. The first version and its output are
    superseded.
- **wall clock:** not instrumented.

## Appendix A: scan.py (verbatim)

sha256 `5548e783ec9a9a2e520f3836491cc83dabe5adbdf89e2b2437db04f0caa642e3`; argv
`PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B <scratch>/rt_1ecb7d/scan.py <repo>`;
output scan.out (sha256 `80cd213c7c12ab63930c6c85d5be6c36a55a396d27e7eba4ef89092c73c5246a`).

```python
#!/usr/bin/env python3
"""Static scan for red-team review TASK-20260924-1ecb7d. Zero runs.

Reads source TEXT only: ast.parse and compile() of text read from disk, dis of the
compiled code object. Never imports, execs or evals a scanned module. An audit hook
refuses (and counts) any import of a scanned module name and every process-launch
event. Usage: python3 -B scan.py <repo-root>
"""
import ast
import dis
import hashlib
import os
import sys

REPO = os.path.abspath(sys.argv[1])
EXP = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43")
TREES = ["implementation-v2", "implementation-v2-a1", "implementation-v2-r3"]

# ---------------------------------------------------------------- guard (names only)
scanned_names = set()
for d in sorted(os.listdir(EXP)):
    p = os.path.join(EXP, d)
    if d.startswith("implementation") and os.path.isdir(p):
        for f in os.listdir(p):
            if f.endswith(".py"):
                scanned_names.add(f[:-3])
for d in ("tools", "harness"):
    for dp, _dn, fn in os.walk(os.path.join(REPO, d)):
        for f in fn:
            if f.endswith(".py"):
                scanned_names.add(f[:-3])
collide = sorted(n for n in scanned_names if n in sys.stdlib_module_names or n in sys.modules)
LAUNCH_EVENTS = ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn",
                 "os.fork", "os.forkpty", "pty.spawn", "os.startfile")
COUNT = {"import": 0, "launch": 0, "selftest_import_refused": False, "selftest_launch_refused": False}
SELFTEST = [False]


def hook(event, args):
    if event == "import" and args and str(args[0]).split(".")[0] in scanned_names:
        if not SELFTEST[0]:
            COUNT["import"] += 1
        raise RuntimeError("guard: import of scanned module %s refused" % args[0])
    if event in LAUNCH_EVENTS:
        if not SELFTEST[0]:
            COUNT["launch"] += 1
        raise RuntimeError("guard: process launch %s refused" % event)


sys.addaudithook(hook)
SELFTEST[0] = True
try:
    sys.audit("import", "v2_solver", None, [], [], [])
except RuntimeError:
    COUNT["selftest_import_refused"] = True
try:
    sys.audit("subprocess.Popen", "true", ["true"], None, None)
except RuntimeError:
    COUNT["selftest_launch_refused"] = True
SELFTEST[0] = False
print("== guard: %d scanned module names (sha256 of sorted list %s); stdlib/loaded collisions %s; self-test import refused %s, launch refused %s"
      % (len(scanned_names), hashlib.sha256("\n".join(sorted(scanned_names)).encode()).hexdigest(), collide,
         COUNT["selftest_import_refused"], COUNT["selftest_launch_refused"]))


# ---------------------------------------------------------------- helpers
def files():
    out = []
    for t in TREES:
        base = os.path.join(EXP, t)
        for f in sorted(os.listdir(base)):
            if f.endswith(".py"):
                out.append(os.path.join(base, f))
    return out


def rel(p):
    return os.path.relpath(p, REPO)


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        d = dotted(node.value)
        return (d + "." + node.attr) if d else node.attr
    return None


def seg(src, node, limit=110):
    s = ast.get_source_segment(src, node) or "?"
    s = " ".join(s.split())
    return s if len(s) <= limit else s[:limit] + "..."


EXIT_FUNCS = {"sys.exit", "exit", "quit", "os._exit", "os.abort", "os.kill", "os.killpg", "signal.raise_signal"}
EXEC_PREFIX = ("os.exec", "os.posix_spawn", "os.spawn", "subprocess.", "pty.", "multiprocessing.")
EXEC_EXACT = {"os.system", "os.popen", "os.fork", "os.forkpty", "os.fexecve"}
HOOKS = {"os.register_at_fork", "signal.signal", "signal.setitimer", "signal.alarm", "signal.pthread_kill",
         "atexit.register", "faulthandler.enable", "faulthandler.register", "sys.settrace", "sys.setprofile",
         "sys.addaudithook", "threading.Thread", "threading.Timer", "_thread.start_new_thread"}
WRITE_FUNCS = {"np.savez", "np.savez_compressed", "numpy.savez", "os.rename", "os.replace", "shutil.copy",
               "shutil.copyfile", "shutil.move", "json.dump", "C.write_json", "C.write_yaml", "write_json",
               "write_yaml", "A.write_msolve_input", "write_msolve_input", "T.dump", "yaml.safe_dump"}
FIELD_NAMES = ("child_end", "child_end_observer", "stdout_path", "stderr_path", "infrastructure_stop",
               "infrastructure-stop", "recorder-foreign", "raw_result_writer", "launch_records", "undetermined",
               "time_enabled", "register_at_fork", "/children")

sec = {k: [] for k in ("exit", "raise_systemexit", "exec", "hooks", "handlers", "finally", "writes")}
names_hits = []
for path in files():
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src, filename=path)
    r = rel(path)
    for i, line in enumerate(src.splitlines(), 1):
        for nm in FIELD_NAMES:
            if nm in line:
                names_hits.append("%s:%d [%s] %s" % (r, i, nm, " ".join(line.split())[:100]))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = dotted(node.func)
            if fn in EXIT_FUNCS or (fn and fn.endswith("SystemExit")):
                sec["exit"].append("%s:%d %s" % (r, node.lineno, seg(src, node)))
            if fn and (fn in EXEC_EXACT or fn.startswith(EXEC_PREFIX)):
                sec["exec"].append("%s:%d %s" % (r, node.lineno, seg(src, node)))
            if fn in HOOKS:
                sec["hooks"].append("%s:%d %s" % (r, node.lineno, seg(src, node)))
            if fn == "open" and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                    and any(c in str(node.args[1].value) for c in "wax"):
                sec["writes"].append("%s:%d open(%s, %r)" % (r, node.lineno, seg(src, node.args[0], 90), node.args[1].value))
            elif fn in WRITE_FUNCS:
                sec["writes"].append("%s:%d %s" % (r, node.lineno, seg(src, node, 130)))
        if isinstance(node, ast.Raise) and node.exc is not None:
            e = node.exc
            nm = dotted(e.func) if isinstance(e, ast.Call) else dotted(e)
            if nm and nm.endswith("SystemExit"):
                sec["raise_systemexit"].append("%s:%d %s" % (r, node.lineno, seg(src, node)))
        if isinstance(node, ast.Try):
            for h in node.handlers:
                tn = "bare" if h.type is None else seg(src, h.type, 60)
                if h.type is None or any(x in tn for x in ("BaseException", "SystemExit", "KeyboardInterrupt")):
                    body_kinds = sorted({type(b).__name__ for b in h.body})
                    reraises = any(isinstance(b, ast.Raise) for b in ast.walk(ast.Module(body=h.body, type_ignores=[])))
                    sec["handlers"].append("%s:%d except %s -> body %s; contains raise: %s" % (r, h.lineno, tn, body_kinds, reraises))
            if node.finalbody:
                sec["finally"].append("%s:%d finally (first stmt line %d)" % (r, node.lineno, node.finalbody[0].lineno))

for k in ("exit", "raise_systemexit", "exec", "hooks", "handlers", "finally", "writes"):
    print("\n== (%s) %d" % (k, len(sec[k])))
    for x in sec[k]:
        print("  " + x)
print("\n== (names) occurrences of the difference's field names and RG-1 mechanism words in the three trees: %d" % len(names_hits))
for x in names_hits:
    print("  " + x)

# ---------------------------------------------------------------- dis of v2_solver._run_child_locked 181-208
vp = os.path.join(EXP, "implementation-v2", "v2_solver.py")
vsrc = open(vp, encoding="utf-8").read()
print("\n== (dis) v2_solver.py sha256 %s; compiled from source text with %s" % (hashlib.sha256(vsrc.encode()).hexdigest(), sys.version.split()[0]))
mod = compile(vsrc, vp, "exec")
target = None
for c in mod.co_consts:
    if hasattr(c, "co_name") and c.co_name == "_run_child_locked":
        target = c
for ins in dis.get_instructions(target):
    ln = ins.positions.lineno if ins.positions else None
    if ln is not None and 181 <= ln <= 208:
        print("  %3d %-22s %s" % (ln, ins.opname, ins.argrepr))
print("  exception table entries covering lines 183-208 (start,end,target,depth):")
for line in dis.Bytecode(target).dis().splitlines():
    if line.strip().startswith("ExceptionTable") or " to " in line and "->" in line:
        print("   ", line.strip())

print("\n== guard attempt counts: import %d, launch %d" % (COUNT["import"], COUNT["launch"]))
```

## Appendix B: rule_eval.py (verbatim, final version)

sha256 `9e8357c6aeba518120d68c5002f5c8e86a5f6f9210b1c48dc03d24be0eb337d7`; argv
`PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B <scratch>/rt_1ecb7d/rule_eval.py`;
output rule_eval.out (sha256 `e954d28751b0a47cf73be8744c2b2f9883a6932e1338409ad1448b5fc851ca91`).

```python
#!/usr/bin/env python3
"""Rule evaluator for red-team review TASK-20260924-1ecb7d. Reads no file; imports nothing
from a scanned tree. Every object below is a hand-read path of the frozen code (lines cited
in its label); the rule sets are the drafts' texts encoded as functions:
  R0   readbackclose RK-1 (a)/(b) and RK-3 (b) AS WORDED (RL-3 gaps gate nothing)
  R1   failclosed AS WORDED: RF-0 (b), RF-1 (a)/(b), RF-2, RF-3 (a); RL-3 as readbackfull words it
  R2   childend: R1 with RG-1 (c)/(d), RG-2 (a)/(b) and RG-4 (b)
  R2x  R2 with the RG-4 (b) gap rule switched off (isolates RG-1 and RG-2)
  R2w  R2 with RG-1 (c) weakened: "frozen_pre_exec_exit" accepts ANY returncode when no exec is seen
Definitions (failclosed pre_approval_readings): FAIL-OPEN iff the verdict is PASS or PASS_ZL while
(i)..(v) holds; PLANNED-BASIS REFUSAL iff a planned basis outcome gets FAIL by design.
Manifest variants of the requested cap read at v2_check_run 64: Mr3 = r3 base (r3_run_wrapper 550:
from raw-result.json's envelope, None when the wrapper wrote raw) and Mc = recorded independently.
"""
import itertools

CAP = "cap"
FPE_SET = {("ERR", 97), ("ERR", 99), ("", 99), ("OK", 98), ("OK", 99)}          # RG-1 (c)


def L(name, created, raised=None, key=True, report=None, rc=None, pair=None, rec_bound=True,
      tb_lcl=(), chain_lcl=None, exec_=False, escaped=False, foreign_write=None, foreign_records=False,
      fired=None, new_pids=None, opened=True, read=True, t_en=None, value=None, second=False, files=()):
    """One launch. tb_lcl: _run_child_locked frames (tb_lineno, has_pid) on the traceback of the
    exception that leaves run_child; chain_lcl: the same over the whole __context__/__cause__ chain."""
    fired = created if fired is None else fired
    new_pids = (1 if created else 0) if new_pids is None else new_pids
    t_en = (1 if exec_ else 0) if t_en is None else t_en
    value = (1 if exec_ else 0) if value is None else value
    return dict(name=name, created=created, raised=raised, key=key, report=report, rc=rc, pair=pair,
                rec_bound=rec_bound, tb_lcl=list(tb_lcl), chain_lcl=list(tb_lcl if chain_lcl is None else chain_lcl),
                exec_=exec_, escaped=escaped, foreign_write=foreign_write, foreign_records=foreign_records,
                fired=fired, new_pids=new_pids, opened=opened and created, read=read and created,
                t_en=t_en, value=value, second=second, files=list(files))


NORMAL_FILES = ("stdout_stderr", "argv_exact")


def B_ok(name="other B (msolve ok, P-10)"):
    return L(name, True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)


# ---------------------------------------------------------------- recorded values
def cc_rk1(l):
    if l["raised"] is None:
        return l["key"]
    if l["rec_bound"] and l["key"]:
        return True
    return any(p for (_ln, p) in l["tb_lcl"])


def cc_rf1(l):
    if l["raised"] is None:
        return l["key"]
    if (l["rec_bound"] and l["key"]) or any(p for (_ln, p) in l["chain_lcl"]):
        return True
    if all(ln < 181 and not p for (ln, p) in l["chain_lcl"]):
        return False
    return "undetermined"


def child_end(l, weakened=False):
    cc = cc_rf1(l)
    if cc is False:
        return "no_child" if not l["fired"] else "undetermined"
    if l["raised"] is not None or cc is not True:
        return "undetermined"
    if not (l["opened"] and l["read"] and l["new_pids"] == 1 and not l["second"]):
        return "undetermined"
    if l["t_en"] > 0:
        return "exec"
    if l["t_en"] == 0 and l["value"] == 0:
        if weakened and l["report"] in ("", "ERR", "OK"):
            return "frozen_pre_exec_exit"
        if (l["report"], l["rc"]) in FPE_SET:
            return "frozen_pre_exec_exit"
    return "undetermined"


def cls(l, rs):
    """RF-3 (a) classes; for R2/R2x/R2w narrowed by RG-1 (d). Under R0 the class is taken on R0's own record."""
    cc = cc_rk1(l) if rs == "R0" else cc_rf1(l)
    pr = l["pair"] is not None
    base = None
    if cc is False and l["raised"] is None:
        base = "A"
    elif cc is True and l["raised"] is None and pr:
        base = "B"
    elif cc is True and l["raised"] is None and not pr and l["report"] in ("", "ERR") and l["rc"] is not None:
        base = "C"
    if rs in ("R0", "R1") or base is None:
        return base
    ce = child_end(l, weakened=(rs == "R2w"))
    if base == "A":
        return "A" if ce == "no_child" else None
    if base == "B":
        return "B" if (ce == "exec" or (ce == "frozen_pre_exec_exit" and l["rc"] in (98, 99))) else None
    if base == "C":
        return "C" if ce == "frozen_pre_exec_exit" else None


GAP_R1 = {"child_output_meta": False, "child_output_npz": False, "ssf_renamed_solver": False,
          "ssf_renamed_health": "conditional", "callgrind_out_prefixed": False, "nonlaunch_listed": "conditional (FC-7)",
          "stdout_stderr": False, "argv_exact": False, "argv_dir": False}
GAP_R2 = {"child_output_meta": True, "child_output_npz": True, "ssf_renamed_solver": True, "ssf_renamed_health": True,
          "callgrind_out_prefixed": "conditional", "nonlaunch_listed": False, "stdout_stderr": False,
          "argv_exact": False, "argv_dir": False}


def gaps(pkg, rs):
    tab = {"R1": GAP_R1, "R2": GAP_R2, "R2w": GAP_R2}.get(rs)
    if tab is None:                                     # R0 (gates nothing) and R2x (RG-4 switched off: RL-3 as R1)
        tab = GAP_R1 if rs == "R2x" else {}
    hard, cond = [], []
    for l in pkg["launches"]:
        for f in l["files"]:
            g = tab.get(f, False)
            if g is True:
                hard.append(f)
            elif g:
                cond.append(f)
    return hard, cond


def frozen_checker(pkg, variant):
    caps = [l["pair"] for l in pkg["launches"] if l["pair"] is not None]
    req = CAP if (variant == "Mc" or pkg["raw_writer"] == "driver") else None
    items = []
    if pkg["kind"] != "aggregate":
        if not caps:
            items.append("66-67")
        if any(c != req for c in caps):
            items.append("68-70")
    return items


def infra_stop(pkg):                                    # RG-2 (a)
    return pkg["raw_writer"] == "driver" and pkg["launches"] and all(l["pair"] is None for l in pkg["launches"])


def verdict(pkg, rs, variant):
    items = frozen_checker(pkg, variant)
    ls = pkg["launches"]
    files_present = any(l["files"] for l in ls)
    zl_shape = items == ["66-67"]
    if rs == "R0":
        if not items:
            return "PASS"
        if (not pkg["gate"]) and not ls and not files_present and zl_shape:
            return "PASS_ZL"
        return "FAIL"
    foreign = any(l["escaped"] and l["foreign_write"] == "ok" for l in ls)
    hard, _cond = gaps(pkg, rs)
    classes = [cls(l, rs) for l in ls]
    undet = any(cc_rf1(l) == "undetermined" for l in ls)
    if rs in ("R2", "R2x", "R2w"):
        undet = undet or any(child_end(l, rs == "R2w") == "undetermined" for l in ls)
    if (not items and all(c in ("A", "B", "C") for c in classes) and pkg["raw_writer"] == "driver"
            and not foreign and not hard and not undet):
        return "PASS"
    if ((not pkg["gate"]) and not ls and not files_present and zl_shape and pkg["raw_writer"] == "driver"
            and pkg["kind"] in ("cells_m5", "fixture4") and not foreign):
        return "PASS_ZL"
    return "FAIL"


def definitions(pkg, rs):
    out = []
    for l in pkg["launches"]:
        c = cc_rk1(l) if rs == "R0" else cc_rf1(l)
        k = cls(l, rs)
        if l["pair"] is None and l.get("pair_read_truth"):
            out.append("(i)")
        if l["created"] and k not in ("A", "C") and l["pair"] != CAP:
            out.append("(ii)")
        if l["created"] and c is False:
            out.append("(iii)")
        if l["foreign_records"]:
            out.append("(iv)")
    if pkg["raw_writer"] == "wrapper":
        out.append("(v)")
    return sorted(set(out))


def record_level(l, rs):
    c = cc_rk1(l) if rs == "R0" else cc_rf1(l)
    s = "child_created=%s class=%s" % (c, cls(l, rs))
    if rs in ("R2", "R2x", "R2w"):
        s += " child_end=%s" % child_end(l, rs == "R2w")
    flags = []
    if l["created"] and c is False:
        flags.append("(iii) created child recorded child_created false")
    if l["foreign_records"]:
        det = []
        if l["escaped"] and l["foreign_write"] == "ok" and rs != "R0":
            det.append("recorder-foreign file")
        if rs in ("R2", "R2x", "R2w") and child_end(l, rs == "R2w") == "undetermined":
            det.append("child_end undetermined")
        flags.append("(iv) foreign-process record; detected by: %s" % (", ".join(det) or "NOTHING"))
    return s + ((" | " + "; ".join(flags)) if flags else "")


def P(name, kind, launches, raw="driver", gate=False, basis=None, row=None, designed=True):
    """designed: the outcome is a designed branch of the frozen code (a refusal, an exit class, a
    normal completion); False for escapes, raises and constructed hypotheticals."""
    return dict(name=name, kind=kind, launches=launches, raw_writer=raw, gate=gate, basis=basis, row=row,
                designed=designed)


def planned_basis(pkg, rs):
    if pkg["raw_writer"] != "driver":
        return False
    if rs in ("R2", "R2x", "R2w") and infra_stop(pkg):
        return False
    return bool(pkg["basis"] or pkg["row"])


def evaluate(obj_label, pkg, rule_sets=("R0", "R1", "R2x", "R2", "R2w"), ks=(0, 1)):
    print("\n### %s" % obj_label)
    for l in pkg["launches"]:
        if l["name"].startswith("other B"):
            continue
        for rs in rule_sets:
            print("  record[%s] %-4s %s" % (l["name"][:38], rs, record_level(l, rs)))
    for rs in rule_sets:
        for k, var in itertools.product(ks, ("Mr3", "Mc")):
            q = dict(pkg, launches=pkg["launches"] + [B_ok() for _ in range(k)])
            v = verdict(q, rs, var)
            d = definitions(q, rs)
            fo = v in ("PASS", "PASS_ZL") and bool(d)
            pb = planned_basis(q, rs) and v == "FAIL" and q["designed"]
            hard, cond = gaps(q, rs)
            tag = []
            if fo:
                tag.append("FAIL-OPEN %s" % d)
            if pb:
                tag.append("PLANNED-BASIS REFUSAL (basis: %s)" % (q["basis"] or ("RFR-2 row " + str(q["row"]))))
            if rs in ("R2", "R2x", "R2w") and infra_stop(q):
                tag.append("RG-2 infrastructure-stop")
            if hard:
                tag.append("RG-4/RL-3 gaps %s" % sorted(set(hard)))
            if cond:
                tag.append("conditional gaps %s" % sorted(set(cond)))
            print("  package %-4s k=%d %-3s verdict %-7s items %-14s %s" % (rs, k, var, v, frozen_checker(q, var), "; ".join(tag)))


# ================================================================ CJ-0 known-answer objects
print("=" * 100 + "\nCJ-0 KNOWN-ANSWER CONTROL")
p16 = L("P-16 (v2_solver 181; census md 200)", True, raised="KeyboardInterrupt", key=False, tb_lcl=[(181, False)])
evaluate("KA-a1 P-16 on readbackclose RK-1/RK-3 as worded (raw wrapper-written: the raise ends the driver)",
         P("P-16", "cells_m5", [p16], raw="wrapper"), rule_sets=("R0", "R1"))
pf2 = L("P-F2 after P-14a (174 over 214; md 205)", True, raised="OSError", key=False, tb_lcl=[], chain_lcl=[(214, True)])
evaluate("KA-a2 P-F2 after P-14a on readbackclose as worded", P("P-F2", "cells_m5", [pf2], raw="wrapper"), rule_sets=("R0", "R1"))
evaluate("KA-a3 W-1 (driver exits before any launch; wrapper writes raw, r3_run_wrapper 491-505)",
         P("W-1", "cells_m5", [], raw="wrapper"), rule_sets=("R0", "R1"), ks=(0,))
foC = L("FO-1 C, foreign write FAILED", True, report="", rc=1, pair=None, escaped=True,
        foreign_write="failed", foreign_records=True, files=NORMAL_FILES)
foB = L("FO-1 B, foreign write FAILED", True, report="OK", rc=1, pair=CAP, escaped=True,
        foreign_write="failed", foreign_records=True, files=NORMAL_FILES)
evaluate("KA-b1 FO-1 variant C (escape before 183; P-7 shape in the parent) on failclosed as worded",
         P("FO-1C", "cells_m5", [foC], basis="X-08 _condition_met", designed=False), rule_sets=("R1",))
evaluate("KA-b2 FO-1 variant B (OK at 198; escape at 207-208) on failclosed as worded",
         P("FO-1B", "cells_m5", [foB], basis="X-08 _condition_met", designed=False), rule_sets=("R1",))
refA = L("refused before fork (lock 166-169)", False, key=False, fired=False)
evaluate("KA-c1 PB-1: cells m=5, every launch refused before fork (class A only) on failclosed",
         P("PB-1a", "cells_m5", [refA, refA], basis="X-08 _condition_met (m4), X-09/X-10"), rule_sets=("R1",), ks=(0,))
errC = L("ERR setrlimit, exit 97 (P-6)", True, report="ERR", rc=97, files=NORMAL_FILES)
empC = L("empty report, exit 99 (P-7)", True, report="", rc=99, files=NORMAL_FILES)
evaluate("KA-c2 PB-1: cells m=5, every created child ERR / empty (class C only) on failclosed",
         P("PB-1c", "cells_m5", [errC, empC], basis="X-08 _condition_met (m4), X-09/X-10"), rule_sets=("R1",), ks=(0,))
evaluate("KA-d  MUTATION: childend with RG-1 (c) weakened, FO-1 variant C (R2w must flag; R2 must not)",
         P("FO-1C", "cells_m5", [foC], basis="X-08", designed=False), rule_sets=("R2", "R2w"))

# ================================================================ CJ-1 under childend
print("\n" + "=" * 100 + "\nCJ-1 FAIL-OPEN SEARCH UNDER CHILDEND")
for wr in ("ok", "failed", "interrupted"):
    c = dict(foC, foreign_write=wr, name="FO-1 C, foreign write %s" % wr)
    b = dict(foB, foreign_write=wr, name="FO-1 B, foreign write %s" % wr)
    for lab, l in (("C", c), ("B", b)):
        for rc in (1, -2):
            evaluate("FO-1 variant %s, foreign write %s, escaped exit status %d" % (lab, wr, rc),
                     P("FO", "cells_m5", [dict(l, rc=rc)], basis="X-08", designed=False), rule_sets=("R1", "R2"), ks=(1,))
census = [
    ("P-1..P-4 refused before fork (153-169)", L("P-1..4", False, key=False, fired=False)),
    ("P-6 ERR setrlimit 97 (193-196; 220-225)", errC),
    ("P-7 empty report 99 (186-191, 206-208)", empC),
    ("P-8 soft != cap (226-232; child exit 98 at 201)", L("P-8", True, report="OK", rc=98, pair="other", files=NORMAL_FILES)),
    ("P-9 hard-only mismatch (200-201; loop 243-271)", L("P-9", True, report="OK", rc=98, pair="other", files=NORMAL_FILES)),
    ("P-10..P-13 ok / crashed / memory / timeout after exec", L("P-10", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)),
    ("exec raised after OK (204-205 -> 206 -> 208 exit 99)", L("execfail", True, report="OK", rc=99, pair=CAP, files=NORMAL_FILES)),
    ("P-5a raise before 171, no child", L("P-5a", False, raised="MemoryError", key=False, fired=False)),
    ("P-5b fork failing at 181 (callback fires, no new pid)", L("P-5b", False, raised="OSError", key=False, tb_lcl=[(181, False)], fired=True, new_pids=0)),
    ("P-16 raise at 181 after fork", p16),
    ("P-14a raise after pid, before 220", L("P-14a", True, raised="KeyboardInterrupt", key=False, tb_lcl=[(214, True)])),
    ("P-14b raise after 220 before 227", L("P-14b", True, raised="KeyboardInterrupt", key=True, report="OK", tb_lcl=[(226, True)])),
    ("P-14c raise after 227", L("P-14c", True, raised="KeyboardInterrupt", key=True, report="OK", pair=CAP, tb_lcl=[(244, True)])),
    ("P-F1 raise after _run_child_locked returned", L("P-F1", True, raised="OSError", key=True, report="OK", rc=0, pair=CAP, exec_=True)),
    ("P-F2 after P-16", L("P-F2/16", True, raised="OSError", key=False, tb_lcl=[], chain_lcl=[(181, False)])),
    ("P-F2 after P-14a", pf2),
]
for lab, l in census:
    raw = "wrapper" if l["raised"] else "driver"
    evaluate("census %s" % lab, P(lab, "cells_m5", [l], raw=raw, basis="X-08", designed=l["raised"] is None),
             rule_sets=("R1", "R2"), ks=(1,))
cons = [
    ("X1 escaped child exits by SystemExit(99), variant C (HYPOTHETICAL: no repository code raises it; scan)",
     dict(foC, rc=99, foreign_write="failed")),
    ("X1b escaped child exits by SystemExit(99), variant B (HYPOTHETICAL)", dict(foB, rc=99, foreign_write="failed")),
    ("X1c escaped child exits by SystemExit(98), variant B (HYPOTHETICAL)", dict(foB, rc=98, foreign_write="failed")),
    ("X2 second fork within one recorder call (hypothetical; frozen forks once, 181)",
     L("X2", True, report="OK", rc=0, pair=CAP, exec_=True, second=True, files=NORMAL_FILES)),
    ("X3a child gone before the callback reads (not listed -> no new pid)",
     L("X3a", True, report="", rc=1, new_pids=0, opened=False, files=NORMAL_FILES)),
    ("X3b child exiting when read (listed; counter open fails on an exiting task)",
     L("X3b", True, report="", rc=1, opened=False, files=NORMAL_FILES)),
    ("X5 callback fired in a call recorded child_created false (hypothetical)",
     L("X5", False, key=False, fired=True)),
    ("X6a wrong pid; the real child exec'd, the wrong process did not",
     L("X6a", True, report="OK", rc=0, pair=CAP, exec_=True, t_en=0, value=0, files=NORMAL_FILES)),
    ("X6b wrong pid execs while the real child escaped (variant B) (needs a live non-frozen child; none created)",
     dict(foB, foreign_write="failed", t_en=1, value=1)),
    ("X8 escaped child's grandchild execs (counter not inherited)", dict(foB, foreign_write="failed", t_en=0, value=0)),
    ("X9 exec'd Python image (build child v2_child.py; comparator)",
     L("X9", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta"))),
    ("X10 escaped process itself execs something (HYPOTHETICAL: no os.exec* on unwinding paths; scan)",
     dict(foB, foreign_write="failed", t_en=1, value=1)),
    ("X12 timeout SIGKILL between go byte and exec (needs a stall >= the 1800 s minimum watchdog)",
     L("X12", True, report="OK", rc=-9, pair=CAP, exec_=False, files=NORMAL_FILES)),
    ("X13 OOM-killer SIGKILL before exec (RGL-4)", L("X13", True, report="OK", rc=-9, pair=CAP, files=NORMAL_FILES)),
    ("X14 host: children file absent or perf_event_open refused (RGL-1 not met)",
     L("X14", True, report="OK", rc=0, pair=CAP, exec_=True, opened=False, files=NORMAL_FILES)),
]
for lab, l in cons:
    evaluate(lab, P(lab, "cells_m5", [l], basis="X-08", designed=lab.startswith("X9")), rule_sets=("R2x", "R2"), ks=(1,))

# ================================================================ CJ-2 normal launches, six sites
print("\n" + "=" * 100 + "\nCJ-2 NORMAL LAUNCHES (RG-1 only: R2x; host behaviour as RGL-1 states it)")
sites = ["v2_driver 101 child job", "v2_driver 166 msolve (count_instructions true)", "v2_driver 650 comparator",
         "v2_solver 517 callgrind", "a1_health 147 msolve", "a1_pari 96 gp"]
outs = [("ok", L("ok", True, report="OK", rc=0, pair=CAP, exec_=True)),
        ("crashed (signal)", L("crashed", True, report="OK", rc=-11, pair=CAP, exec_=True)),
        ("memory_exhausted", L("mem", True, report="OK", rc=-9, pair=CAP, exec_=True)),
        ("timeout (killed after exec)", L("timeout", True, report="OK", rc=-9, pair=CAP, exec_=True)),
        ("refused before fork (invalid cap, driver RSS, other solver, lock)", L("ref", False, key=False, fired=False)),
        ("refused: ERR setrlimit 97", errC), ("refused: empty report 99", empC),
        ("refused: soft read-back != cap (OK, 98; returns at 232)", L("soft", True, report="OK", rc=98, pair="other")),
        ("crashed: hard-only mismatch (OK, 98)", L("hard", True, report="OK", rc=98, pair="other")),
        ("crashed: exec raised (OK, 99)", L("execfail", True, report="OK", rc=99, pair=CAP))]
for s in sites:
    row = []
    for o, l in outs:
        row.append("%s -> %s/%s" % (o.split(" (")[0], child_end(l), cls(l, "R2x")))
    print("  %-48s %s" % (s, " | ".join(row)))

# ================================================================ CJ-3 infrastructure-stop scope
print("\n" + "=" * 100 + "\nCJ-3 OUTCOMES WITH >= 1 LAUNCH RECORD AND NO COLLECTED PAIR, per kind (R1 vs R2x; RG-2)")
for kind, basis, gate in (("build", "X-07 _load_build", False), ("cells_m5", "X-08 _condition_met; X-09/X-10", False),
                          ("cells_m4", "X-09/X-10 aggregates", False), ("fixture4", None, False),
                          ("fixture", None, True), ("controls_a1", "X-13 a1_check_run 79-84", True)):
    for lab, ls in (("all refused before fork (incl. driver RSS 156-160)", [refA, refA]),
                    ("all created children ERR / empty", [errC, empC]),
                    ("mixture refused + ERR", [refA, errC])):
        evaluate("CJ-3 %s: %s" % (kind, lab), P(kind, kind, ls, gate=gate, basis=basis), rule_sets=("R1", "R2x"), ks=(0,))
    evaluate("CJ-3 %s: mixture refused + one B (not infra-stop)" % kind,
             P(kind, kind, [refA, B_ok("B in pkg")], gate=gate, basis=basis), rule_sets=("R1", "R2x"), ks=(0,))
print("\n-- RKR-4 (b) PASS / PASS_ZL rows (census md 476-492), R1 vs R2x (RG-2 alone) vs R2 (with RG-4):")
rows = [
    ("478 G1..G4 completed_valid (fixture: 4 uncached builds + raw grids; census md 431)", "fixture", True, None,
     [L("build", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta", "child_output_npz")),
      L("grid", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta")),
      L("msolve", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)]),
    ("478 G3 anchor-identity (comparator + uncached anchor_S4 build, v2_driver 671)", "anchor", True, None,
     [L("comparator", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_dir")),
      L("build", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta", "child_output_npz"))]),
    ("480 controls_a1 image (gp + health + uncached builds, a1_driver 89, 129, 146)", "controls_a1", True, "X-13 a1_check_run 79-84",
     [L("gp", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "nonlaunch_listed")),
      L("health", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "nonlaunch_listed")),
      L("build", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta", "child_output_npz"))]),
    ("481 fixture4 launched (uncached builds, v2_driver 548)", "fixture4", False, None,
     [L("build", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta", "child_output_npz"))]),
    ("483 build (cached builds, to_cache true, v2_driver 961-962)", "build", False, "X-07 _load_build",
     [L("build", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)]),
    ("485 cells m=5 measured, no SSF re-solve", "cells_m5", False, "X-08; X-09/X-10",
     [L("msolve", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)]),
    ("485 cells m=5 measured, one SSF re-solve at S-1 (r3_resolve 224-238, 310)", "cells_m5", False, "X-08; X-09/X-10",
     [L("msolve#1", True, report="OK", rc=0, pair=CAP, exec_=True, files=("ssf_renamed_solver",)),
      L("msolve#2", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)]),
    ("486 cells m=5 Z-C5 (no launch)", "cells_m5", False, "X-08; X-09/X-10", []),
    ("488 cells m=4 (raw cell always launches: raw_grid, v2_driver 1161 -> 133-147)", "cells_m4", False, "X-09/X-10 aggregates",
     [L("grid", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta")),
      L("msolve", True, report="OK", rc=0, pair=CAP, exec_=True, files=NORMAL_FILES)]),
    ("488 cells m=4, callgrind child failed on target 0 (v2_solver 521-524 leaves .callgrind.out)", "cells_m4", False, "X-09/X-10 aggregates",
     [L("grid", True, report="OK", rc=0, pair=CAP, exec_=True, files=("stdout_stderr", "argv_exact", "child_output_meta")),
      L("callgrind", True, report="OK", rc=-9, pair=CAP, exec_=True, files=("stdout_stderr", "callgrind_out_prefixed"))]),
]
for lab, kind, gate, basis, ls in rows:
    evaluate("RKR-4 (b) row %s" % lab, P(lab, kind, ls, gate=gate, basis=basis, row=lab.split()[0]),
             rule_sets=("R1", "R2x", "R2"), ks=(0,))
```

## Appendix C: name_check.py (verbatim)

sha256 `0eebe3a8c287ec55adae2d6310e6bbf20aaae57549be1eb6cdfdcfc3e613f273`; argv
`python3 -B <scratch>/rt_1ecb7d/name_check.py <review-report.yaml> <review-report.md>`.
It reads its word list at run time from words.txt, next to the script, and prints only
counts and line numbers.

```python
#!/usr/bin/env python3
"""CRT-7 self-check for TASK-20260924-1ecb7d. Reads the word list at run time from words.txt next
to this script and prints ONLY the list's sha256, counts and line numbers, never a word.
A hit is counted as permitted only on a line which, after every listed word is masked, is exactly
the inference block's prohibition flag line "<masked>_used: false" (the one permitted exception).
Usage: python3 -B name_check.py FILE [FILE ...]"""
import hashlib
import os
import re
import sys

here = os.path.dirname(os.path.abspath(__file__))
wp = os.path.join(here, "words.txt")
raw = open(wp, "rb").read()
words = [w.strip() for w in raw.decode("utf-8").splitlines() if w.strip()]
print("word list sha256 %s; %d entries" % (hashlib.sha256(raw).hexdigest(), len(words)))
MASK = "\x00"
flag = re.compile(r"\s*(-\s*)?" + MASK + r"_used:\s*false\s*")
for path in sys.argv[1:]:
    lines = open(path, encoding="utf-8").read().splitlines()
    permitted, other = 0, []
    for i, line in enumerate(lines, 1):
        masked = line
        n = 0
        for w in words:
            masked, k = re.subn(re.escape(w), MASK, masked, flags=re.I)
            n += k
        if not n:
            continue
        if flag.fullmatch(masked):
            permitted += n
        else:
            other.append(i)
    print("%s: permitted-flag hits %d; other hits on %d line(s): %s" % (os.path.basename(path), permitted, len(other), other))
```

## Appendix D: output excerpts (verbatim)

### D.1 rule_eval.out, CJ-0 known-answer control

```text
CJ-0 KNOWN-ANSWER CONTROL

### KA-a1 P-16 on readbackclose RK-1/RK-3 as worded (raw wrapper-written: the raise ends the driver)
  record[P-16 (v2_solver 181; census md 200)] R0   child_created=False class=None | (iii) created child recorded child_created false
  record[P-16 (v2_solver 181; census md 200)] R1   child_created=undetermined class=None
  package R0   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R0   k=0 Mc  verdict FAIL    items ['66-67']      
  package R0   k=1 Mr3 verdict FAIL    items ['68-70']      
  package R0   k=1 Mc  verdict PASS    items []             FAIL-OPEN ['(ii)', '(iii)', '(v)']
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      
  package R1   k=1 Mr3 verdict FAIL    items ['68-70']      
  package R1   k=1 Mc  verdict FAIL    items []             

### KA-a2 P-F2 after P-14a on readbackclose as worded
  record[P-F2 after P-14a (174 over 214; md 205] R0   child_created=False class=None | (iii) created child recorded child_created false
  record[P-F2 after P-14a (174 over 214; md 205] R1   child_created=True class=None
  package R0   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R0   k=0 Mc  verdict FAIL    items ['66-67']      
  package R0   k=1 Mr3 verdict FAIL    items ['68-70']      
  package R0   k=1 Mc  verdict PASS    items []             FAIL-OPEN ['(ii)', '(iii)', '(v)']
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      
  package R1   k=1 Mr3 verdict FAIL    items ['68-70']      
  package R1   k=1 Mc  verdict FAIL    items []             

### KA-a3 W-1 (driver exits before any launch; wrapper writes raw, r3_run_wrapper 491-505)
  package R0   k=0 Mr3 verdict PASS_ZL items ['66-67']      FAIL-OPEN ['(v)']
  package R0   k=0 Mc  verdict PASS_ZL items ['66-67']      FAIL-OPEN ['(v)']
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      

### KA-b1 FO-1 variant C (escape before 183; P-7 shape in the parent) on failclosed as worded
  record[FO-1 C, foreign write FAILED] R1   child_created=True class=C | (iv) foreign-process record; detected by: NOTHING
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      
  package R1   k=1 Mr3 verdict PASS    items []             FAIL-OPEN ['(iv)']
  package R1   k=1 Mc  verdict PASS    items []             FAIL-OPEN ['(iv)']

### KA-b2 FO-1 variant B (OK at 198; escape at 207-208) on failclosed as worded
  record[FO-1 B, foreign write FAILED] R1   child_created=True class=B | (iv) foreign-process record; detected by: NOTHING
  package R1   k=0 Mr3 verdict PASS    items []             FAIL-OPEN ['(iv)']
  package R1   k=0 Mc  verdict PASS    items []             FAIL-OPEN ['(iv)']
  package R1   k=1 Mr3 verdict PASS    items []             FAIL-OPEN ['(iv)']
  package R1   k=1 Mc  verdict PASS    items []             FAIL-OPEN ['(iv)']

### KA-c1 PB-1: cells m=5, every launch refused before fork (class A only) on failclosed
  record[refused before fork (lock 166-169)] R1   child_created=False class=A
  record[refused before fork (lock 166-169)] R1   child_created=False class=A
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      PLANNED-BASIS REFUSAL (basis: X-08 _condition_met (m4), X-09/X-10)
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      PLANNED-BASIS REFUSAL (basis: X-08 _condition_met (m4), X-09/X-10)

### KA-c2 PB-1: cells m=5, every created child ERR / empty (class C only) on failclosed
  record[ERR setrlimit, exit 97 (P-6)] R1   child_created=True class=C
  record[empty report, exit 99 (P-7)] R1   child_created=True class=C
  package R1   k=0 Mr3 verdict FAIL    items ['66-67']      PLANNED-BASIS REFUSAL (basis: X-08 _condition_met (m4), X-09/X-10)
  package R1   k=0 Mc  verdict FAIL    items ['66-67']      PLANNED-BASIS REFUSAL (basis: X-08 _condition_met (m4), X-09/X-10)

### KA-d  MUTATION: childend with RG-1 (c) weakened, FO-1 variant C (R2w must flag; R2 must not)
  record[FO-1 C, foreign write FAILED] R2   child_created=True class=None child_end=undetermined | (iv) foreign-process record; detected by: child_end undetermined
  record[FO-1 C, foreign write FAILED] R2w  child_created=True class=C child_end=frozen_pre_exec_exit | (iv) foreign-process record; detected by: NOTHING
  package R2   k=0 Mr3 verdict FAIL    items ['66-67']      RG-2 infrastructure-stop
  package R2   k=0 Mc  verdict FAIL    items ['66-67']      RG-2 infrastructure-stop
  package R2   k=1 Mr3 verdict FAIL    items []             
  package R2   k=1 Mc  verdict FAIL    items []             
  package R2w  k=0 Mr3 verdict FAIL    items ['66-67']      RG-2 infrastructure-stop
  package R2w  k=0 Mc  verdict FAIL    items ['66-67']      RG-2 infrastructure-stop
  package R2w  k=1 Mr3 verdict PASS    items []             FAIL-OPEN ['(iv)']
  package R2w  k=1 Mc  verdict PASS    items []             FAIL-OPEN ['(iv)']
```

### D.2 scan.out, guard, exits, SystemExit, exec, hooks, handlers, names and guard counts

```text
== guard: 256 scanned module names (sha256 of sorted list 4200f056c940e60770363c6079cb9cac458676e2cf8cc35604f59dd186d012ef); stdlib/loaded collisions []; self-test import refused True, launch refused True

== (exit) 43
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_check_run.py:114 sys.exit(main(sys.argv[1]))
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:60 sys.exit(96)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:69 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_child.py:81 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py:100 SystemExit("GFPN_RUN_DIR not set: launch through v2_run_wrapper.py")
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:54 sys.exit(2)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:243 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:208 os._exit(99)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:201 os._exit(98)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:266 os.kill(pid, signal.SIGKILL)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:196 os._exit(97)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_verify_independent.py:280 sys.exit(1 if bad else 0)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_check_run.py:145 sys.exit(main(sys.argv[1]))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py:439 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py:433 SystemExit("REFUSING: development outputs never go under experiments/")
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:52 SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (p, ctx.pkg.get("p")))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:224 SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (args.p, ctx_pkg.get("p")))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:233 SystemExit("REFUSING: arguments do not match the plan package")
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_health.py:297 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_make_trial_plan.py:69 SystemExit("only the 31-bit plan is implemented as a writer; the FB-1 plan is written only if AA-3 fires " "(i...
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py:148 sys.exit(0)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:378 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:417 sys.exit(main(args[0], aj))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:406 sys.exit(r3_reg1.main(sys.argv[2:]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:408 sys.exit(frozen_v2(sys.argv[2]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:410 sys.exit(frozen_a1(sys.argv[2]))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks.py:298 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv12.py:131 SystemExit("REFUSING: %s exists (a case is run once; a re-run needs a recorded harness reason)" % cd)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:434 SystemExit("REFUSING: %s exists (DV-7 runs once; a re-run needs a recorded harness reason)" % tdir)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:115 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:84 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:333 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:141 SystemExit("REFUSING: expected 42 distinct minted ids, 31 v2 and 11 v2-a1 packages")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:152 SystemExit("REFUSING: M is not a bijection from the 42 frozen ids onto 42 fresh ids (RC-4 (a); R3S-7)")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:154 SystemExit("REFUSING: the r1 / r2 plan ids differ from the retirement lists")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:157 SystemExit("REFUSING: retirement lists differ from the paristack PS-3 enumeration")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:135 SystemExit("REFUSING: %s sha256 %s != bound %s" % (path, got, want))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:295 SystemExit("REFUSING: %s fails the RC-4 (c) equality (%s != %s)" % (name, h1, h2))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:297 SystemExit("REFUSING: %s watchdogs differ from trial-plan-v2.json" % name)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:299 SystemExit("REFUSING: %s carries a forbidden task id" % name)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:318 SystemExit("REFUSING: %s exists; plans are written once" % path)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_reg1.py:352 sys.exit(main())
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:583 sys.exit(main())

== (raise_systemexit) 17
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py:100 raise SystemExit("GFPN_RUN_DIR not set: launch through v2_run_wrapper.py")
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_devchecks.py:433 raise SystemExit("REFUSING: development outputs never go under experiments/")
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:52 raise SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (p, ctx.pkg.get("p")))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:224 raise SystemExit("REFUSING: --p %s does not match the plan package's p %s" % (args.p, ctx_pkg.get("p")))
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_driver.py:233 raise SystemExit("REFUSING: arguments do not match the plan package")
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_make_trial_plan.py:69 raise SystemExit("only the 31-bit plan is implemented as a writer; the FB-1 plan is written only if AA-3 fires...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv12.py:131 raise SystemExit("REFUSING: %s exists (a case is run once; a re-run needs a recorded harness reason)" % cd)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:434 raise SystemExit("REFUSING: %s exists (DV-7 runs once; a re-run needs a recorded harness reason)" % tdir)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:141 raise SystemExit("REFUSING: expected 42 distinct minted ids, 31 v2 and 11 v2-a1 packages")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:152 raise SystemExit("REFUSING: M is not a bijection from the 42 frozen ids onto 42 fresh ids (RC-4 (a); R3S-7)")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:154 raise SystemExit("REFUSING: the r1 / r2 plan ids differ from the retirement lists")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:157 raise SystemExit("REFUSING: retirement lists differ from the paristack PS-3 enumeration")
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:135 raise SystemExit("REFUSING: %s sha256 %s != bound %s" % (path, got, want))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:295 raise SystemExit("REFUSING: %s fails the RC-4 (c) equality (%s != %s)" % (name, h1, h2))
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:297 raise SystemExit("REFUSING: %s watchdogs differ from trial-plan-v2.json" % name)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:299 raise SystemExit("REFUSING: %s carries a forbidden task id" % name)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_make_plans.py:318 raise SystemExit("REFUSING: %s exists; plans are written once" % path)

== (exec) 26
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_common.py:59 subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:182 subprocess.run(cmd, cwd=C.REPO, env=child_env, stdout=so, stderr=se)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_run_wrapper.py:49 subprocess.run(["git", "-C", C.REPO] + list(args), capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:181 os.fork()
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:205 os.execv(argv[0], argv)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:533 subprocess.run(["callgrind_annotate", "--inclusive=yes", out], capture_output=True, text=True, timeout=600)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:204 os.execve(argv[0], argv, env)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_pari.py:121 subprocess.run([GP, "--version-short"], capture_output=True, text=True, timeout=30)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:303 subprocess.run(cmd, cwd=REPO, env=child_env, stdout=so, stderr=se)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:61 subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_run_wrapper.py:372 subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
  experiments/EXP-GFPN-05ff43/implementation-v2-a1/a1_toy.py:334 subprocess.run([sys.executable, "-B", shim], env=env, capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_check_run.py:372 subprocess.run(FROZEN_LAUNCHER + [mode, rd], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWR...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks.py:205 subprocess.run(cmd, env=child_env(), stdout=so, stderr=se)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:278 subprocess.run([sys.executable, "-B", os.path.join(HERE, "r3_make_plans.py"), "--check"], capture_output=True,...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:93 subprocess.run(["callgrind_annotate", "--version"], capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:538 subprocess.run([sys.executable, "-B", os.path.join(R.REPO, "tools", "allocate_id.py"), "--check", i], capture_...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:100 subprocess.run(["dpkg-query", "-W", "-f=${Package} ${Version}\n", "msolve", "valgrind", "pari-gp"], capture_ou...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:492 subprocess.run(["git", "-C", R.REPO, "status", "--porcelain", "--untracked-files=all"], capture_output=True, t...
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:502 subprocess.run(["git", "-C", R.REPO, "rev-parse", "HEAD"], capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:96 subprocess.run(["valgrind", "--version"], capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:99 subprocess.run(["gp", "--version-short"], capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv6.py:324 subprocess.run([sys.executable, "-B", shim] + args, env=env, capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:477 subprocess.run(cmd, cwd=R.REPO, env=child_env, stdout=so, stderr=se)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:73 subprocess.run(["git", "-C", R.REPO] + list(args), capture_output=True, text=True)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_run_wrapper.py:341 subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)

== (hooks) 0

== (handlers) 5
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:206 except BaseException -> body ['Pass']; contains raise: False
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:100 except SystemExit -> body ['Assign']; contains raise: False
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:103 except BaseException -> body ['Assign']; contains raise: False
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:69 except SystemExit -> body ['Assign']; contains raise: False
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:72 except BaseException -> body ['Assign']; contains raise: False

== (finally) 10
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_arms.py:741 finally (first stmt line 754)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_lift.py:52 finally (first stmt line 75)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_lift.py:82 finally (first stmt line 91)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:140 finally (first stmt line 143)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:170 finally (first stmt line 173)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv6.py:58 finally (first stmt line 61)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:175 finally (first stmt line 180)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_a1.py:98 finally (first stmt line 107)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_entry_v2.py:67 finally (first stmt line 76)
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_reg1.py:151 finally (first stmt line 154)


== (names) occurrences of the difference's field names and RG-1 mechanism words in the three trees: 14
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:144 [time_enabled] return {"instructions_user": v, "time_enabled_ns": enabled, "time_running_ns": running,
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:149 [stdout_path] def run_child(argv, stdout_path, stderr_path, cap_bytes=CAP_BYTES_DEFAULT, timeout_s=None,
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:149 [stderr_path] def run_child(argv, stdout_path, stderr_path, cap_bytes=CAP_BYTES_DEFAULT, timeout_s=None,
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:171 [stdout_path] return _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, c
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:171 [stderr_path] return _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, c
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:177 [stdout_path] def _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, cwd,
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:177 [stderr_path] def _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, cwd,
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:188 [stdout_path] fo = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:189 [stderr_path] fe = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
  experiments/EXP-GFPN-05ff43/implementation-v2/v2_solver.py:299 [stderr_path] with open(stderr_path, errors="replace") as fh:
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_devchecks_more.py:668 [child_end] ch = [t for t in ev if t.get("event") == "child_end"]
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:308 [child_end] _log("child_end", {"child_argv0": os.path.basename(argv[0]), "child_flags": [x for x in argv if x in
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:616 [child_end] "children_by_launcher": sorted({json.dumps([t.get("launcher"), t.get("child_argv0")]) for t in tr if
  experiments/EXP-GFPN-05ff43/implementation-v2-r3/r3_dv7.py:618 [child_end] if t["event"] == "child_end" and t.get("child_argv0") == "gp"],

== guard attempt counts: import 0, launch 0
```

### D.3 rule_eval.out, CJ-2 normal launches (each line is one call site)

```text
CJ-2 NORMAL LAUNCHES (RG-1 only: R2x; host behaviour as RGL-1 states it)
  v2_driver 101 child job                          ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
  v2_driver 166 msolve (count_instructions true)   ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
  v2_driver 650 comparator                         ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
  v2_solver 517 callgrind                          ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
  a1_health 147 msolve                             ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
  a1_pari 96 gp                                    ok -> exec/B | crashed -> exec/B | memory_exhausted -> exec/B | timeout -> exec/B | refused before fork -> no_child/A | refused: ERR setrlimit 97 -> frozen_pre_exec_exit/C | refused: empty report 99 -> frozen_pre_exec_exit/C | refused: soft read-back != cap -> frozen_pre_exec_exit/B | crashed: hard-only mismatch -> frozen_pre_exec_exit/B | crashed: exec raised -> frozen_pre_exec_exit/B
```

### D.4 rule_eval.out, RKR-4 (b) rows (R1 vs R2x vs R2; the Mr3 lines)

```text
-- RKR-4 (b) PASS / PASS_ZL rows (census md 476-492), R1 vs R2x (RG-2 alone) vs R2 (with RG-4):

### RKR-4 (b) row 478 G1..G4 completed_valid (fixture: 4 uncached builds + raw grids; census md 431)
  record[build] R1   child_created=True class=B
  record[build] R2x  child_created=True class=B child_end=exec
  record[build] R2   child_created=True class=B child_end=exec
  record[grid] R1   child_created=True class=B
  record[grid] R2x  child_created=True class=B child_end=exec
  record[grid] R2   child_created=True class=B child_end=exec
  record[msolve] R1   child_created=True class=B
  record[msolve] R2x  child_created=True class=B child_end=exec
  record[msolve] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: RFR-2 row 478); RG-4/RL-3 gaps ['child_output_meta', 'child_output_npz']

### RKR-4 (b) row 478 G3 anchor-identity (comparator + uncached anchor_S4 build, v2_driver 671)
  record[comparator] R1   child_created=True class=B
  record[comparator] R2x  child_created=True class=B child_end=exec
  record[comparator] R2   child_created=True class=B child_end=exec
  record[build] R1   child_created=True class=B
  record[build] R2x  child_created=True class=B child_end=exec
  record[build] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: RFR-2 row 478); RG-4/RL-3 gaps ['child_output_meta', 'child_output_npz']

### RKR-4 (b) row 480 controls_a1 image (gp + health + uncached builds, a1_driver 89, 129, 146)
  record[gp] R1   child_created=True class=B
  record[gp] R2x  child_created=True class=B child_end=exec
  record[gp] R2   child_created=True class=B child_end=exec
  record[health] R1   child_created=True class=B
  record[health] R2x  child_created=True class=B child_end=exec
  record[health] R2   child_created=True class=B child_end=exec
  record[build] R1   child_created=True class=B
  record[build] R2x  child_created=True class=B child_end=exec
  record[build] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             conditional gaps ['nonlaunch_listed']
  package R2x  k=0 Mr3 verdict PASS    items []             conditional gaps ['nonlaunch_listed']
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: X-13 a1_check_run 79-84); RG-4/RL-3 gaps ['child_output_meta', 'child_output_npz']

### RKR-4 (b) row 481 fixture4 launched (uncached builds, v2_driver 548)
  record[build] R1   child_created=True class=B
  record[build] R2x  child_created=True class=B child_end=exec
  record[build] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: RFR-2 row 481); RG-4/RL-3 gaps ['child_output_meta', 'child_output_npz']

### RKR-4 (b) row 483 build (cached builds, to_cache true, v2_driver 961-962)
  record[build] R1   child_created=True class=B
  record[build] R2x  child_created=True class=B child_end=exec
  record[build] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict PASS    items []             

### RKR-4 (b) row 485 cells m=5 measured, no SSF re-solve
  record[msolve] R1   child_created=True class=B
  record[msolve] R2x  child_created=True class=B child_end=exec
  record[msolve] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict PASS    items []             

### RKR-4 (b) row 485 cells m=5 measured, one SSF re-solve at S-1 (r3_resolve 224-238, 310)
  record[msolve#1] R1   child_created=True class=B
  record[msolve#1] R2x  child_created=True class=B child_end=exec
  record[msolve#1] R2   child_created=True class=B child_end=exec
  record[msolve#2] R1   child_created=True class=B
  record[msolve#2] R2x  child_created=True class=B child_end=exec
  record[msolve#2] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: X-08; X-09/X-10); RG-4/RL-3 gaps ['ssf_renamed_solver']

### RKR-4 (b) row 486 cells m=5 Z-C5 (no launch)
  package R1   k=0 Mr3 verdict PASS_ZL items ['66-67']      
  package R2x  k=0 Mr3 verdict PASS_ZL items ['66-67']      
  package R2   k=0 Mr3 verdict PASS_ZL items ['66-67']      

### RKR-4 (b) row 488 cells m=4 (raw cell always launches: raw_grid, v2_driver 1161 -> 133-147)
  record[grid] R1   child_created=True class=B
  record[grid] R2x  child_created=True class=B child_end=exec
  record[grid] R2   child_created=True class=B child_end=exec
  record[msolve] R1   child_created=True class=B
  record[msolve] R2x  child_created=True class=B child_end=exec
  record[msolve] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: X-09/X-10 aggregates); RG-4/RL-3 gaps ['child_output_meta']

### RKR-4 (b) row 488 cells m=4, callgrind child failed on target 0 (v2_solver 521-524 leaves .callgrind.out)
  record[grid] R1   child_created=True class=B
  record[grid] R2x  child_created=True class=B child_end=exec
  record[grid] R2   child_created=True class=B child_end=exec
  record[callgrind] R1   child_created=True class=B
  record[callgrind] R2x  child_created=True class=B child_end=exec
  record[callgrind] R2   child_created=True class=B child_end=exec
  package R1   k=0 Mr3 verdict PASS    items []             
  package R2x  k=0 Mr3 verdict PASS    items []             
  package R2   k=0 Mr3 verdict FAIL    items []             PLANNED-BASIS REFUSAL (basis: X-09/X-10 aggregates); RG-4/RL-3 gaps ['child_output_meta']; conditional gaps ['callgrind_out_prefixed']
```
