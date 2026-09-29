# Red-team review report: TASK-20260924-f5631b

This is the zero-run, static red-team review of the DRAFT
AMD-EXP-GFPN-05ff43-20260924-failclosed
(`experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml`, sha256
`1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c`), under the card
`ledger/handoffs/TASK-20260924-f5631b.yaml`. It is archived by TASK-20260924-0c2fdc. The
machine-readable report is `review-report.yaml` in this directory.

**What this is not.**
- It is observations only. It makes no approval recommendation.
- It makes no statement about D, the quotient, H-GFPN-9a29be or HEUR-GFPN-DFLAT. Nothing here is
  evidence about them.
- FAIL-OPEN, PLANNED-BASIS REFUSAL and FAIL-CLOSED are the draft's definitions
  (`pre_approval_readings.definitions`, draft lines 604-621). Where a verdict turns on how a
  definition is read, both readings are stated. The approval act rules on them.

**Summary of verdicts (J-5 first, as RTR-4 requires).**

| joint | verdict | classification |
|---|---|---|
| J-5 known-answer control | **holds** | The method flags every named object. One deviation (DV-1): under RF-2 / RF-3, the weakened RF-1 on P-16 is reported as a record-level defect, not as a package-level fail-open. |
| J-1 recording rule | **breaks** | FO-1. It is a FAIL-OPEN under definition (iv) as literally worded. It is reachable only through documented interpreter behaviour. No argv is executed. |
| J-2 verdict rules | **holds** | No counterexample under (ii) or (v). F-4's carve-out is recorded as OB-4. |
| J-3 planned basis outcomes | **breaks** | PB-1. It is a PLANNED-BASIS REFUSAL by the draft's definitions. The break is definitional: the verdict is unchanged from readbackclose. |
| J-4 development harness | **breaks** | FC-1 and FC-2. RF-4 as worded makes DV-18 STOP by construction. This is fail-closed. |
| J-6 reads, reach, readers | **holds** | Informational. |

## 0. Run record

| item | value |
|---|---|
| repository HEAD read | `f8858be35eead85e3c966677bc33701d843f10d5` |
| lane | Claimed by the dispatching session on BATCH-e409ca (owner red-team, epoch 1). This review did not touch it. |
| git writes | none of any kind |
| run packages, solver / valgrind / callgrind_annotate / gp / Sage / builder children | 0 |
| scanned-tree modules imported, executed or run | 0. The `ast_scan.py` audit-hook guard counted 0 import attempts and 0 launch attempts. |
| interpreter used for ast / dis | 3.11.15. The census run record gives the same version. |
| network | not used; no web search, no web fetch |
| wall clock | not instrumented; well inside the advisory 43200 s |

**Inference block (RTR-7), as the dispatching session specified.**
- requested_policy: review-adversarial
- agent_binding: red-team, at the policy's default reasoning effort, as the dispatching session arranged
- resolved_model_id: null ("none supplied by the dispatching session; none invented")
- model_verified: false
- fallback_used: false
- bedrock_used: false

## 1. RTR-2 integrity (applied first): PASS

| check | computed | bound | result |
|---|---|---|---|
| (a) failclosed draft | `1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c` | Two sources, which agree: the dispatching session's message, and a one-field print of `["addendum_sha256"]` from `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-eb2540/ledger-receipt.json`. Its sha256 member equals the computed value and its path member names this file. The file itself reads `status: draft`, `approved_by: null`, `approval_decision: null` (lines 177-179). | PASS |
| (b) readbackclose | `f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c` | same | PASS |
| (b) readbackfull | `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1` | same | PASS |
| (b) readbackcover | `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e` | same | PASS |
| (c) readbackclose-census.md | `ed9817daf9d0bb2ba131b62f90ae0206ee0757f518fa2eb36ed7ad59ccdbd838` | TASK-20260924-71d070 path_sha256: same | PASS |
| (c) readbackclose-census.json | `9c87067cbb3118e642b1bf1df89f2ae93bddbbc24e012865025a9c3e0379adaa` | same | PASS |
| (c) rk_check.py | `00a04a0e5bac1362c041bbf32d2b8a9db0289857afb637575647b018631d667c` | same | PASS |
| (c) readbackfull-census.md | `5f36e962421596b696b824fd3ac4d11f5166ed37365a812309a3bb11d864ebe7` | TASK-20260924-ddfb69: same | PASS |
| (c) readbackfull-census.json | `36d79fe5d34726ebf6beda900fa553e4c40de9ae7833d27a30c6320dfc8f1158` | same | PASS |
| (c) rf_check.py | `ac64b01e346c5cd1b1ec634488408c49932eed3c2a1054156fa6e46092f75558` | same | PASS |
| (c) readback-census.md | `2e0e05259dc4a030907ae5cf9bafa931be52883bd3d7adcf51f7922e9417a5c3` | TASK-20260924-a01341: same | PASS |
| (c) readback-census.json | `49232738d576b0352f709fc84f368c7d7a1dd8c56fd52d2d9aa4d161ae73eea4` | same | PASS |
| (c) rb_check.py | `3d7f82b054793d53eaf4062418078c5691bbf08422ee7b8d4e39e206b4371a64` | same | PASS |
| (d) `git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json` | empty, exit 0 | must be empty | PASS |

The following were also checked, and all are consistent:
- the same diff with git-side pathspec globs: empty;
- the diff from dd103455 to HEAD: empty;
- `git status --porcelain --untracked-files=all` on the same pathspecs: empty;
- `git cat-file -t dd103455...`: `commit`;
- the scan's own sha256 of v2_solver.py (`0a3bdb9c...ac9d`), v2_driver.py (`0d22a082...0098`) and
  a1_driver.py (`0ec607c7...acde`), which equal the values at close census md 122;
- before any write, `test -e` on this review directory printed ABSENT.

## 2. J-5: the known-answer control (reported first)

**Method.** One method is used, unchanged, for J-5, J-1, J-2 and J-3. It is the scratch rule
evaluator `rule_eval.py`, reproduced verbatim in appendix B (sha256
`5a8bec2aac61b59deac15d7c122bd4490994ca4eed93661d6134bf0d328e4f86`).

The evaluator combines two parts:
- **Path and outcome facts.** These are read by hand from the frozen code, with lines cited per
  object, and follow the close census's tables (md 190-206, 377-383, 476-492).
- **The rule texts, encoded as functions.** There are four rule sets:
  - **R0**: readbackclose RK-1 and RK-3 (b), as worded;
  - **R1**: the failclosed draft (RF-0 (b), RF-1, RF-2, RF-3 (a));
  - **R1w**: R1 with RF-1 weakened to "false whenever no pid is found";
  - **R1m**: R1 with the class (C) returncode mutation of FO-1.

Each launch path is placed in a cells package with k = 0 or 1 other class (B) launch. Each package
is evaluated under two manifest variants of the requested cap, which v2_check_run.py reads at 64
and compares at 68-70:
- **Mr3** is the r3 base. r3_run_wrapper.py 550 takes the requested cap from raw-result.json's
  `envelope.cap_bytes`. A wrapper-written raw-result.json (r3_run_wrapper.py 500) has no envelope,
  so the requested cap is None.
- **Mc** is an r4 wrapper that records the requested cap independently of raw-result.json.

For each object the method reports:
- the recorded child_created;
- the verdict;
- which of definitions (i)-(v) hold on the truth facts;
- **FAIL-OPEN** if and only if some definition holds while the verdict is PASS or PASS_ZL.

**What the method did on each named object** (rule_eval.out, "KNOWN-ANSWER CONTROL"):

| object | rule set | Mr3 | Mc |
|---|---|---|---|
| P-16 (k = 1) | R0 as worded | child_created **false** for a created child ((iii)). FAIL: item 68-70 compares the other pair with requested None, so the defect is record-level only. | child_created **false** ((iii)). **PASS, so FAIL-OPEN** ((ii), (iii), (v)). |
| P-16 (k = 0) | R0 | false ((iii)). FAIL: item 66-67 fails and launch_records is non-empty. | same |
| P-F2 after P-14a (k = 1) | R0 | child_created **false** ((iii)). FAIL, record-level. | **PASS, so FAIL-OPEN** ((ii), (iii), (v)). |
| W-1 | R0 | **PASS_ZL** with (v): **FAIL-OPEN** | **PASS_ZL**: **FAIL-OPEN** |
| P-16 (k = 1) | R1w (weakened RF-1) | false ((iii)). FAIL (RF-3 (a): raised non-null; RF-0 (b): wrapper-recorded). Record-level. | same |
| P-16 | R1 (the draft) | undetermined. FAIL. | undetermined. FAIL. |

**Result: J-5 holds.**
- The method, unchanged, flags P-16 and P-F2 (after P-14a) as child_created false for a created
  child, and W-1 as PASS_ZL for a wrapper-recorded outcome. RTR-4's condition is met as worded.
- It also separates record-level defects from package-level ones. Under RK-3 (b) as worded, P-16
  and P-F2 are package-level FAIL-OPEN only when the requested cap is recorded independently of
  raw-result.json (Mc). On the r3-base manifest their packages FAIL.
- **Deviation DV-1.** The card expects the weakened RF-1 to be reported "as fail-open" on P-16. The
  method reports that only in combination with RK-3 (b) as worded; the R0/Mc row applies, because
  RK-1 (b) and the weakened rule coincide on P-16. In combination with RF-2 / RF-3, no raise path
  reaches PASS: the raise ends the frozen driver, so the outcome is wrapper-recorded, and the
  launch record has raised non-null. The draft's FAIL-OPEN precondition (PASS or PASS_ZL) is
  therefore not met. This also shows that RF-1's three-valued precision does not bear on any
  verdict, given that no handler catches a raise from run_child (J-2).

## 3. J-1: the recording rule: **breaks** (FO-1)

**Claim under attack.** RF-1 with RK-1 (a), (c), (d) and RL-1:
- never records child_created false for a created or possibly created child;
- never loses a pair the parent read at v2_solver.py 227;
- detects every record that ends in a process other than the installing one.

**What holds.**
- **(iii)** RF-1 (a) assigns `false` only when both of these hold:
  - `rec` is unbound, or lacks `child_rlimit_report`;
  - every `_run_child_locked` frame on the chain has tb_lineno below 181 and no `pid`.

  Fork is at 181, and `pid` is bound only there. Compiling the source text and disassembling it
  gives, at line 181, `LOAD_GLOBAL os`, `LOAD_ATTR fork`, `PRECALL`, `CALL`, `STORE_FAST pid`; line
  183 is `NOP` (the try). The following all give `undetermined`: P-16, P-F2 after P-16, a failing
  fork at 181, chains longer than 16, and cycles.

  On the return path, key presence is exact. The key is set at 220, before the post-fork returns
  (225, 232, 308) and before none of the pre-fork returns (155, 160, 165, 169). The evaluator
  finds no path on which R1 records false for a created child.
- **(i)** The pair is copied on every path on which 227 executed: from the returned record, or,
  on a raise, from `rec` in the outermost run_child frame. It is lost only when the recorder fails
  in the installing process. That failure ends the frozen driver (no handler; scan (3)), so the
  package FAILs (RF-0 (b), RF-3 (a)).

**Paths evaluated (R1).** Every census row, and every constructed variant, gives the same result:
- every **raise** path is FAIL (wrapper-recorded, raised non-null);
- every **return** path is recorded exactly.

The rows evaluated were:
- P-1..P-4, P-5a (rec bound and unbound), P-5b (178-180, and a failing fork at 181);
- P-6, P-7, P-8, P-9, P-10..P-13;
- P-14a, P-14b, P-14c, P-16, P-F1;
- P-F2 after each of P-5b, P-16, P-14a, P-14b and P-14c;
- chains longer than 16.

The only FAIL-OPEN rows under R1 are the two foreign-process rows of FO-1.

**Constructed paths (card J-1 (2)).**
- **A raise inside the recorder after the frozen call returned** (in the event-file write or the
  chain walk), in the installing process. The exception leaves the recorder and no frozen or r3
  handler catches it, so the driver ends and raw-result.json is wrapper-written. Result: FAIL.
  This is fail-closed; record exactness is best effort (RF-0 (e)).
- **An asynchronous exception in the recorder, before the durable write.**
  - In the installing process: the same as above, so FAIL.
  - In a foreign process: this is step 4 of FO-1.
- **Exception chaining.**
  - `__suppress_context__` does not clear `__context__`, and RF-1 walks both `__context__` and
    `__cause__`.
  - The frozen functions reached contain no explicit `raise` (census md 138-139).
  - A chain longer than 16, or a cycle, gives `undetermined`.
  - A 181 frame reached only through `__cause__` also gives `undetermined`; the frozen code never
    sets `__cause__`.
- **Signal handlers.** No file of the three trees calls any of the following: `signal.signal`,
  `setitimer`, `alarm`, `faulthandler`, `atexit`, `threading`, `_thread`, `register_at_fork`,
  `addaudithook`, `settrace`, `setprofile` or `excepthook` (scan (4)). The only hits are
  `import signal` at v2_solver.py 35 and `os.kill` at 266. Handlers installed by third-party
  libraries the entries load were not read, being outside the repository (OB-8).

**The break: FO-1** (section 8). RF-1 (b) detects a foreign-process recorder call only through a
write made by that process. When that write fails or is interrupted:
- the entry's `finally` still writes pari-stack.json in the foreign process;
- that record goes undetected;
- the parent's class (C) or (B) record admits PASS.

This is a FAIL-OPEN under (iv) as literally worded. It is reachable only through documented
interpreter behaviour. The foreign process executes no argv and creates no capped child. If (iv) is
read as covering only records the recorder writes, FO-1 is not a FAIL-OPEN, but J-1's third claim
is still unmet on that sequence.

**Files and lines read:**
- v2_solver.py 1-553;
- r3_entry_v2.py 36-80; r3_entry_a1.py 47-111;
- r3_resolve.py 1-514; r3_common.py 405-417;
- readbackclose RK-1 and RK-2 (245-306);
- readbackfull RL-1, RL-3 and RL-5 (209-333);
- failclosed RF-0, RF-1 and RF-3 (279-418);
- close census md 131-268.

**What would change the verdict:**
- a ruling that (iv) covers only recorder-written records;
- or a rule that makes the foreign-process fact positive evidence: the class (C) returncode
  mutation for variant C, and a rule that no r4 writer writes outside the installing process for
  variant B.

## 4. J-2: the verdict rules: **holds**

**Claim under attack.** Under RF-0 (b), RF-2 and RF-3, no package receives PASS or PASS_ZL, and no
dependant is admitted, while either:
- a child that may have executed argv lacks a recorded pair equal to the cap; or
- the outcome is wrapper-recorded.

**(1) Layers and handlers.** Scan (3) enumerates every call edge from the six run_child call sites
up to the entries. The six sites are v2_driver 101, 166 and 650, v2_solver 517, a1_health 147 and
a1_pari 96. The edges pass through:
- child_job, build_poly and raw_grid;
- the frozen solve, reached through the SE-3 wrapper: r3_resolve.solve 373-390, then `_bounded`
  248-319 or the pass-through at 382-387, then `_call_original` 117-118;
- a1_health.run_system, reached through the HR-3 wrapper (397-409), and a1_health.run;
- a1_pari.curve_facts and callgrind_instructions;
- fixture_core.run_target, _run_cell and the cmd_* functions;
- v2_driver.main 1329-1348 and a1_driver.main 445-462.

No call edge lies inside a try body with a handler, except the entries' `main`:
- r3_entry_v2 67-79 and r3_entry_a1 98-110 record SystemExit and BaseException;
- their `finally` writes pari-stack.json;
- they then re-raise at 78-79 and 109-110.

P-B (v2_common.curve_order_pari) launches no child. Scan (3) marks three edges (a1_pari 121,
v2_common 59, v2_solver 533). These are `subprocess.run` calls matched by name, not on a run_child
path. On every raise, the RF-3 verdict is FAIL.

**(2) "driver" for a raw-result.json that finish() did not write.** No route was found.
- The writers of raw-result.json are:
  - `finish` (v2_driver 84);
  - the two aggregates' direct writes (v2_driver 1322, a1_driver 388; OB-2).
- R-3, and `os.makedirs` at r3_run_wrapper 435, exclude a pre-existing file.
- No launch follows any raw-result write. Each `finish` is the command's last statement or is
  followed by `return`: v2_driver 280, 540-541, 578, 658-659, 667-668, 676-677, 748, 931, 984-985
  and 1107; a1_driver 215.
- The escaped fork child cannot reach `finish`.

**(3) The route "driver died after 227".**
- Under RK-3 (b) as worded, it is PASS only in Mc. On the r3 base, item 68-70 fails because the
  requested cap is None (OB-1).
- Under RF-3 it is FAIL in both variants (raised non-null; wrapper-recorded).

**(4) A class (C) child cannot reach exec.**
- A report that is empty, or that starts with `ERR setrlimit`, means the child never executed 198,
  the only `OK` write.
- Exec at 203-205 is reached only after 198-202.
- An `execv` that raises after `OK` leaves an `OK` report and a read pair. That is class (B), with
  exit 99 via 206-208.
- A report of under PIPE_BUF bytes is written atomically.
- The only non-exec continuation is the P-C escape, which executes no argv (FO-1).

**(5) Every class (B) pair reaches item 68-70.** RL-3 (d) adds every launch-record pair to the
RB-2 union. v2_check_run 63 reads the union, and 68-70 compare soft and hard with the requested cap.
The only exemption is kind `aggregate` (65), and the aggregate commands reach no run_child.

**Observation OB-4 (F-4).** Build 4111 is admitted whatever F-4's verdict (RK-3 (d), RF-0 (d),
RF-3 (b)). This is not read as a match of the admission clause:
- build is admitted by R-8's existence test, not by F-4's outcome;
- cmd_build (v2_driver 935-985) reads no run directory.

**What would change the verdict:**
- a handler in the r4 entries or the r4 recorder that catches a raise and continues;
- an r4 raw_result_writer test that accepts a raw-result.json the driver process did not write;
- a reading of the admission clause that counts F-4.

## 5. J-3: planned basis outcomes: **breaks** (PB-1, definitional)

| kind (both r3 plans) | driver-logic outcome | verdict under RF-2 / RF-3 | read by a dependant's frozen logic? |
|---|---|---|---|
| fixture G1, G2; anchor G3; controls G4 | completed_valid, gate_pass true | PASS | no. The wrapper reads it (R-7 / RB-4); any other outcome is a gate stop. |
| fixture4 F-4 | launched, with a pair | PASS | no |
| fixture4 F-4 | Z-F4 (538-541) | PASS_ZL (RF-2 (vii) fixture4; (vi) via `finish` at 540) | no |
| build | rows ok / refused / failed with at least one pair, class (A) or (C) launches included | PASS | yes: cells' `_load_build` (989-1003) |
| build | every launch refused before fork, or no pair | **FAIL (PB-1)** | yes: cells read it as "polynomial unavailable" (1068-1075) |
| cells m = 5 | Z-C5 completed_valid | PASS_ZL | yes: `_condition_met` (1119-1126) |
| cells m = 5 | Z-C5 failed / resource_exhaustion (invalid cell; 1101-1102) | PASS_ZL (RF-2 reads no run_status) | yes |
| cells m = 5 | measured or not_measured, with a pair; class (A) / (C) included | PASS | yes |
| cells m = 5 | at least one launch and no pair | **FAIL (PB-1)** | yes: `m5_not_measured` is met (terminal not_measured, 0 measured) |
| cells m = 4 | with a pair (the raw arm always launches) | PASS | yes: the aggregates (1259-1267; a1_driver 301-310) |
| cells m = 4 | launches and no pair | **FAIL (PB-1)** | yes |
| aggregate, aggregate_a1 | their figures (no launch; kind exempt at 65) | PASS | aggregate: yes, by aggregate_a1 (X-10) |
| controls_a1 | completed_valid, gate_pass true | PASS | no (X-02 is the wrapper; X-13 is the checker) |
| contingency | as the kind it replaces | as that kind | as that kind |
| every kind | W-1, W-2 (wrapper-recorded) | FAIL | not planned basis outcomes (RF-0 (b)) |

**PB-1.** The draft defines a PLANNED BASIS OUTCOME as "a driver-logic outcome (RF-0 (b)) that a
dependant's frozen logic acts on". Outcomes that have launch records but no collected pair meet
both prongs, and RF-2 / RF-3 FAIL them by design:
- RF-3 (a) keeps RK-3 (b)'s requirement that the frozen checker exit 0, and item 66-67 denies it;
- RF-2 keeps RK-3 (b) (ii), empty launch_records.

The sequence, with file and line at each step, is in section 8. The break is **definitional**.
These rows were FAIL, with "yes: designed stop", in the census's RKR-4 (b) table under
readbackclose (md 484, 487). RF-3 (b) replaced RK-3 (c), and RK-3 (c) was the text that excluded
them from planned basis outcomes. RF-3 (b) still names "an infrastructure launch (as RK-3 (c)
defines it)" as a designed-stop class. No census row that is PASS or PASS_ZL is turned to FAIL by
RF-2's or RF-3's added conditions.

**Files read:**
- both r3 plans (a JSON read of the gate blocks, package kinds, cells arms and conditions);
- v2_driver 935-1237;
- census md 326-492;
- readbackclose RK-3 (307-373);
- failclosed RF-0 (b), RF-2, RF-3 (b) and the definitions (604-621).

**What would change the verdict:**
- a reading that RF-3 (b)'s designed-stop class carries RK-3 (c)'s exclusion;
- or a definition that excludes outcomes with launch records and no collected pair.

## 6. J-4: the development harness: **breaks** (fail-closed; FC-1, FC-2)

**(1) The replacements exist.** Each is at the lines the census lists (md 612-631):

| replacement | declared at | redirected at |
|---|---|---|
| r3_run_wrapper `RUNS` | 68 | r3_dv7 481; r3_dv12 156 |
| r3_common `RUNS_DIR` | 31 | r3_dv7 480; r3_dv12 153 |
| r3_common `PLAN_V2_R3`, `PLAN_A1_R3`, `PLAN_V2`, `RECEIPT_R3_PHASE_A`, `RECEIPT_R3_PHASE_B`, `REG1_REFERENCE_RUN` | 112, 113, 104, 131, 132, 174 | r3_dv7 470-473; r3_dv12 121-122, 155 |
| r3_common `RECEIPT_V2_PHASE_B` | 129 | r3_dv7 480; r3_dv12 154 |
| v2_common `LADDER_PATH` | 35 | r3_dv7 174 (restored at 180) |
| child-side shim | - | r3_dv7 230-231, 299-300, `cfg_for` 393-404; r3_dv12 139-149 |
| `W.ENTRY_V2` / `W.ENTRY_A1` | - | r3_dv7 469; r3_dv12 113 |
| `K.FROZEN_LAUNCHER` | - | r3_dv7 570 |
| `W.git_tree_state` | - | r3_dv7 468; r3_dv12 111 |
| synthetic phase-A receipt | - | r3_dv12 118-122 (it carries a `commit_sha`, 119) |

OB-9 records a note on "the ladder path".

**(2) Frozen reads.**
- **Seeds and streams.** Every `random.Random` in the command modules is keyed by constants, p,
  shape, arm, m or a target label: v2_common 163 and 172; v2_driver 309, 347, 372, 392, 543-544,
  770-772, 781, 803-804, 818 and 1160; a1_driver 148; v2_child 72, 88 and 94 (from the constant
  `spec["sample_seed"]`). None is keyed by the run id or a path.
- **Unchanged values.** Targets, the cap (v2_driver 43; a1_common 64), the watchdogs (the plan
  copy's values) and the thread count (`-t 1`, `nbthreads=1`) do not change.
- **Argv differs.** Every capped child's argv embeds a path derived from GFPN_RUN_DIR
  (v2_common 97-105, then Ctx 55):
  - v2_driver 98-101 (the spec path);
  - v2_driver 160-166 (msolve `-f` / `-o`);
  - v2_driver 647-650 (the comparator directory);
  - a1_driver 86-89, then a1_pari 91-96 (the script path);
  - a1_driver 129, then a1_health 141-147.

  Each such argv therefore carries the redirected RUNS parent and the label (FC-2).
- **Label reads.** The label also reaches the certificate `run_id` (v2_driver 252, then v2_lift
  220) and the package that `finish` copies (78), both as RF-4 (d) lists. v2_verify_independent
  contains no `run_id`.
- **The archived anchor run.** anchor-identity reads `C.ARCHIVED_ANCHOR_RUN`, which is fixed when
  v2_common is imported (41), so a later EXP_DIR redirection does not move it.

**(3) Launch, sweeps and other items.**
- **Receipt reads at launch.** r3_run_wrapper 437-440 do not raise without a receipt:
  `phase_a_commit` 88-89 returns None with "receipt absent". The stage's phase-A commit is then
  recorded as None, and r3_check_run 255-256 fails, unless the RF-4 (a) (3) synthetic receipt
  carries a `commit_sha` (FC-3).
- **Forbidden-id sweeps.** r3_check_run 189-224 and a1_check_run 51-58 react to the label only if
  the label, or a development path in the swept files, contains one of the forbidden task ids
  (r3_common 123-124 with RB-6 (d); a1_common 57).
- **Three REG-1 items, not one (FC-1).** On a development package, the r3-base checker fails
  **three** REG-1 items:
  - r3_check_run 329-330: NOT_EVALUABLE;
  - 331-332: `d_branch` None against `d-parsed`;
  - 333-334: `exclusion_list_sha256` None against the plan's
    `4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c`.

  The NOT_EVALUABLE block (r3_run_wrapper 158, recorded at 565-566) carries neither key.
- **Preflight refusals** are as the census lists (md 578-594), with two additions:
  - R-6 at stage time, handled by RF-4 (a) (3);
  - R-10, handled by RF-4 (b).

**Files read:**
- r3_run_wrapper.py 1-584; r3_check_run.py 1-418; r3_common.py 1-418; r3_reg1.py 1-353;
- r3_dv7.py at the ranges listed in section 11; r3_dv12.py 95-174;
- v2_driver 53-107 and 628-931; a1_driver 50-215; a1_common 1-123; v2_common; v2_child;
- census md 552-692;
- RF-4 and RF-6.

**What would change the verdict:**
- an r4 REG-1 item that records the NOT_EVALUABLE block as one item, or an RF-4 (c) that lists
  331-334;
- an RF-4 (d) that compares argv after substituting the run-directory path.

## 7. J-6: reads, reach and readers: **holds** (informational)

- **X-13 and X-02 read the same fields.**
  - X-13 (a1_check_run 79-84) reads `run_status` and `gate_pass` of the controls_a1 image. It
    finds the image id at the a1 plan's `gate.addendum_blocking_package`, under the root
    `C.EXP_DIR/runs`.
  - X-02 (r3_run_wrapper 190-196, called at 288-289) reads the same two fields of the same package
    under the root `RUNS`.
  - They differ in the root attribute, and in how they treat an unparseable file. X-02 reads it as
    `unparseable` (103-104); X-13 raises, so its checker exits non-zero. Both refuse.
- **The RLR-2 / RKR-2 findings stand.**
  - The RTR-2 (d) diff is empty.
  - Scan (1) re-derives the six call sites, each with no enclosing try or with.
  - There is one definition each, at 149 and 177.
  - There are zero `from v2_solver import` statements in the three trees.
  - A text listing of both names in the entries' closure shows no rebinding.
- **Readers in the r3 base.** None. None of `raw_result_writer`, `recorder-foreign`,
  `undetermined`, `launch_records`, `child_created`, `pair_read_by_parent` or `frame_inspection`
  occurs in any file of the three trees (scan (6)).
- **Readers in the draft's rules.**
  - `raw_result_writer`:
    - It is defined by RF-0 (b), read by RF-2 (vi) and RF-3 (a), and named as a stop class by
      RF-3 (b).
    - It is written to every manifest (RF-7).
    - The frozen checkers do not read it. Neither does r3_check_run, whose sweeps use constant
      keys and five named files. Neither does REG-1, which compares solver inputs, outputs,
      certificates and raw-result items, but not the manifest.
    - The a1 byte sweep reads manifest bytes, with no effect.
  - The recorder-foreign file:
    - It is read by RF-2 (viii), RF-3 (a) and RF-3 (b).
    - It lies in the run root, so it is not in RL-3's gap list.
    - REG-1 does not compare it, and r3_check_run does not sweep it.
    - The a1 byte sweep scans it, with no effect: it holds only pids and a type name.
  - `undetermined`:
    - It is read by RF-0 (c), RF-2, RF-3 (a) and RK-2 (iv).
    - RL-3's count of "evidenced" children counts only `child_created` true. That accounting
      changes, but it gates nothing by itself.
    - REG-1's SE-4 (e) test reads only the top-level flag and the S-1 / S-2 event consistency
      records.

## 8. Counterexamples

### FO-1 (J-1): a foreign-process record goes undetected

**Classification.**
- It is a FAIL-OPEN under definition (iv) as literally worded.
- Under a reading of (iv) limited to records written by the recorder, it is not a FAIL-OPEN, but
  J-1's third claim is unmet.

**Reachability.**
- It is reachable only through documented interpreter behaviour: asynchronous exceptions at
  bytecode boundaries in the fork child, the census's L-11 class.
- That must combine with one of:
  - a further asynchronous exception, or a kill, during the recorder's foreign-file write;
  - an operating-system error confined to that write, since the entry's later write must succeed.

**Sequence.**
1. **v2_solver.py 181.** `os.fork()` creates the child. The parent holds `pid > 0`.
2. **v2_solver.py 181-183.** In the **child**, an asynchronous exception is delivered at a
   bytecode boundary before the try at 183. An example is KeyboardInterrupt from SIGINT sent to
   the child's pid. The disassembly of these lines is: 181 `CALL`, `STORE_FAST pid`; 182
   `LOAD_FAST`, `COMPARE_OP`, `POP_JUMP`; 183 `NOP`.

   *Variant B:* the child has written `OK` at 198 and closed `rep_w` at 199. A first exception at
   202 is caught at 206, and a second is delivered at 207-208, before `os._exit(99)`.
3. **v2_solver.py 172-174 and 114-118.** The exception leaves `_run_child_locked` in the child.
   run_child's `finally` then calls `lk.release()` there: `flock LOCK_UN` on the open file
   description the parent shares, followed by `close`.
4. **failclosed RF-1 (b); readbackfull RL-1 (d).**
   - The r4 recorder sees the call end outside the installing process. It starts writing
     `recorder-foreign-<pid>.json` in the run root.
   - A further asynchronous exception is delivered before the file is durable. Alternatively, the
     write fails with an error confined to it.
   - RF-1 (b) specifies no failure path in the foreign process ("It takes no other action there:
     it does not exit, signal or wait").
   - RL-1 (d) says "a recording failure ... package failed", but there is no channel from that
     process.
5. **Scan (3); r3_entry_v2.py 67-79 (r3_entry_a1.py 98-110); r3_common.py 405-417.**
   - The exception crosses the frozen callers; none has a handler.
   - It reaches the entry's try, which records the status.
   - The entry's `finally` writes **pari-stack.json in the child**.
   - The entry then re-raises, and the child exits (status 1, or by SIGINT).
6. **v2_solver.py 213-225 (variant C) or 227-308 (variant B).**
   - *Variant C:* the parent is blocked at 214 until EOF, because the child held `rep_w`. It reads
     the empty report, sets the key at 220, closes `go_w`, and reaps the child at 223. It returns
     `refused_to_start` with report `''` and a returncode other than 99.
   - *Variant B:* the parent read `OK` and the pair at 227, and wrote the go byte at 236. It reaped
     the child in the 243-271 loop. The outcome is `crashed`, with the pair equal to the cap.
7. **failclosed RF-3 (a).** The recorder in the installing process writes a class (C) launch
   record (variant C) or a class (B) one (variant B).
8. **v2_driver.py 77-88.** The frozen driver treats `refused_to_start` or `crashed` as a value and
   continues. `finish` writes raw-result.json, so raw_result_writer is `driver` (RF-0 (b)).
9. **r3_entry_v2.py 75-77.** When the parent exits, its entry rewrites pari-stack.json. This
   overwrites the child's record.
10. **RF-3 (a); RL-4.** The package now has all of the following:
    - every launch record is class (A), (B) or (C);
    - it is driver-written;
    - there is no recorder-foreign file, no recorder gap and nothing undetermined;
    - with another collected pair, the frozen checker exits 0.

    The verdict is **PASS**, and dependants are admitted. Definition (iv) holds on the child's
    pari-stack.json write.

**Evaluator.**
- "P-C before 183, foreign-file write FAILED/interrupted; ...": R1 gives PASS with (iv) in Mr3 and
  in Mc. **R1m gives FAIL.**
- "P-C after OK (206-208), foreign-file write FAILED/interrupted; ...": R1 and R1m both give PASS
  with (iv).
- Controls:
  - "foreign file WRITTEN": R1 gives FAIL.
  - "child killed before any write": R1 gives PASS with no definition holding; R1m gives FAIL for
    variant C.

**Substance.**
- The foreign process executes no argv and creates no capped child. No frozen or r3 handler lets it
  continue (scans (2)-(3)).
- No capped child lacks a recorded cap, so the AC-1 property of options_weighed FB is not
  violated.
- The child's traceback on the package's stderr.log is also written there and goes undetected.
- The child's `LOCK_UN` at step 3 releases the parent's host lock during the call.

**Cheapest mutation.**
- *Variant C:* require the class (C) returncode to be 97 with an `ERR setrlimit` report, or 99
  with the empty report. These are the frozen child's own pre-exec exits (v2_solver.py 196, 208),
  so the parent-side record becomes positive evidence. R1m shows the effect.
- *Variant B:* no parent-side positive evidence was found. A rule that no r4 writer writes outside
  the installing process removes the undetected record.

### PB-1 (J-3): an outcome with launch records and no pair

**Classification.** It is a PLANNED-BASIS REFUSAL as the draft's definitions word it. It is
definitional, because the verdict was already FAIL, as a designed stop, under readbackclose
RK-3 (c).

**Sequence.**
1. **trial-plan-v2-r3.json, cells RUN-GFPN-0983ac (p 4111, ecgfp5_shaped, m 5).** The package
   runs, and one of the following happens:
   - every solve launch is refused before fork (v2_solver.py 161-169: another solver-like process,
     or the host lock held); or
   - every created child reports `''` or `ERR setrlimit` (P-6, P-7).
2. **v2_driver.py 1174-1204, 1235-1236, 1101-1102 and 1107.** The driver records the targets and
   the cell terminal as not_measured, sets run_status to `failed` / `resource_exhaustion`, and
   writes raw-result.json. This is a driver-logic outcome.
3. **v2_check_run.py 65-67; RK-3 (b) (ii); RF-2; RF-3 (a).**
   - No pair is collected, so item 66-67 fails and PASS is unavailable.
   - launch_records is non-empty, so PASS_ZL is unavailable.
   - The verdict is FAIL.
4. **RF-3 (b), RF-0 (d); RL-4.** The m = 4 dependant RUN-GFPN-5bf619 is refused. It follows
   through the `requires` chain, with `--prior-run RUN-GFPN-0983ac`. This is a designed stop.
5. **v2_driver.py 1006-1013 and 1110-1127.** That dependant's frozen logic acts on exactly this
   outcome:
   - `_prior_cells` reads the m = 5 cells;
   - `_condition_met` finds `m5_not_measured` met (terminal not_measured, 0 measured);
   - that decides whether its conditional arms run.

   By the definitions, the outcome is therefore a PLANNED BASIS OUTCOME that receives FAIL by
   design.

**Other outcomes of the same kind:**
- build packages with no pair, which cells read through `_load_build` (989-1003, 1068-1075);
- cells m = 4 packages with launches and no pair, which the aggregates read;
- contingencies of either.

**Evaluator.** Every rule set gives FAIL on:
- "cells, every launch refused before fork (class A only)";
- "class C only";
- P-1..P-4, P-6 and P-7 with k_other 0.

## 9. Fail-closed findings (never a bar; each with its cost)

| id | joint | finding | cost (which package or stage would stop) |
|---|---|---|---|
| FC-1 | J-4 | RF-4 (c) expects one failing checker item on a development package. The r3-base checker fails three: r3_check_run 329-330, 331-332 and 333-334. The NOT_EVALUABLE block (r3_run_wrapper 158, recorded at 565-566) has no `d_branch` and no `exclusion_list_sha256`. | DV-18 (a) controls, (b) anchor-identity and (e) controls-a1 STOP as worded. The r4 stage stops for a new decision, and no r4 package runs. |
| FC-2 | J-4 | RF-4 (d) makes any argv difference a STOP. Every capped child's argv embeds a path under GFPN_RUN_DIR (v2_driver 98-101, 160-166, 647-650; a1_pari 91-96; a1_health 141-147), so the argv always differs in its path components. Flags, binary and threads are equal. | DV-18 (a), (b) and (e) STOP, unless argv is compared after substituting the run-directory path. The draft does not state that. |
| FC-3 | J-4 | Without a `commit_sha` in the RF-4 (a) (3) synthetic receipt, launch (r3_run_wrapper 440) records the stage's phase-A commit as None, and r3_check_run 255-256 fails. r3_dv12 119 wrote one; RF-4 (a) (3) cites that method but does not state it. | A further DV-18 STOP. |
| FC-4 | J-4 | The r3 child-side shim also wrapped v2_solver.run_child with a tracer (r3_dv7 301-314). Carried over, it would make the RL-5 install read-back refuse, giving a W-2 outcome. RF-4 (a) (2)'s "only actions" excludes it. | A DV-18 STOP if it is copied. |
| FC-5 | J-3 | RF-0 (d) says a designed stop "may rule an R-12 contingency". R-12 (r3_run_wrapper 206-228, the frozen contingency_rule) replaces only `infrastructure_error`. A cells package with no measured target is `resource_exhaustion` (v2_driver 1101-1102). An RF-3 FAIL on a completed_valid raw (foreign file, gap, undetermined) has failure_class None. | The linear `requires` chain of either plan stops at that package with no in-protocol contingency. Continuing needs a Coordinator decision beyond R-12. |
| FC-6 | J-1 / J-2 | Every raise leaving run_child ends the frozen driver and FAILs the package. This includes a failing fork at 181 with no child (RF-1: undetermined). RF-1's values bear on record exactness only (RF-0 (e)). | That package fails, and its dependants stop. |
| FC-7 | J-3 / J-4 (conditional) | RL-3 names directories (health/, comparator/, pari/) that also hold files that no launch writes under its own tag: a1_health 141-143 and 251, a1_pari 91-93, and the comparator's outputs. A gap test that maps files by tag would report gaps on controls_a1 and G3. | controls_a1 or G3 FAIL, which is a gate stop; or DV-18 (e) / (c') STOP. |

## 10. Observations outside the definitions

- **OB-1.** RF-3 (a)'s parenthetical and RFF-3's last sentence say that under RK-3 (b) as worded,
  "driver died after 227" gets PASS. On the r3 base it does not:
  - v2_check_run 68-70 compares the pair with `child_rlimit_as_requested_bytes`;
  - r3_run_wrapper 550 takes that value from raw-result.json's envelope;
  - the wrapper-written raw (500) has no envelope, so the value is None and the item fails.

  The statement holds only with an r4 wrapper that records the requested cap independently of
  raw-result.json (evaluator DIED227: R0 Mr3 FAIL, R0 Mc PASS). RF-3 FAILs the route either way.
- **OB-2.** RF-0 (b)'s "(written by the frozen command's finish())" is inexact for aggregate and
  aggregate_a1, which write raw-result.json directly (v2_driver 1322; a1_driver 388). The
  normative test still reads `driver`, and neither command launches anything.
- **OB-3.** Infrastructure-caused driver-logic outcomes pass. Two routes:
  - A class (A) host-state refusal (v2_solver 161-169) of a build child gives a build row
    `refused_to_start`. Cells then read it as "polynomial unavailable" (v2_driver 1068-1075).
  - A missing or changed cached polynomial gives `not_attempted ... infrastructure_error`
    (1076-1081). The cache is under TMPDIR (v2_common 42), outside the package.

  Both can yield Z-C5 with PASS_ZL, and both steer the m = 4 conditional rule (1119-1126). That is
  the effect RFF-3 cites against admitting W-1. It is not a FAIL-OPEN under (i)-(v), and RF-3 (a)
  admits class (A) by design.
- **OB-4.** F-4's carve-out (section 4).
- **OB-5.** Some children are launched outside run_child, uncapped, and so fall outside "capped
  child":
  - a1_driver 90, then a1_pari 118-123: the gp version query;
  - v2_solver 531-533: callgrind_annotate;
  - v2_common 57-61: shell utilities for host facts.

  RF-1 and RF-3 do not cover them.
- **OB-6.** RL-3's gap list omits the callgrind child's files: `solver/<tag>.callgrind.stdout` and
  `.stderr` (v2_solver 515-518). A lost S-3 launch record would be caught only by RL-1 (d)'s own
  failure path. The CG-3 record (r3_resolve 323-369) carries that child's read-back, but the draft
  does not name it as a cross-check.
- **OB-7.** RF-0 (a) says no favourable value may be inferred from the absence of a record. RF-2
  (viii) and RF-3 (a) nevertheless read "no recorder-foreign file" as "no foreign-process call".
  This is the basis of FO-1.
- **OB-8.** No file of the three trees installs a signal handler (scan (4)). Third-party libraries
  that the entries load were not read, being outside the repository. The verdicts depend only on
  asynchronous exceptions being deliverable at bytecode boundaries.
- **OB-9.** Two points about the ladder:
  - The wrapper reads `r3_common.LADDER_PATH` (r3_run_wrapper 464, a sha256 record only). The
    census table (md 615-622) does not list it.
  - RF-4 (a) (2) does not state that the development ladder and fixture files must be
    byte-identical to the real ones. Only RF-4 (d)'s STOP catches a difference.

**Interpreter semantics relied on.** All three rules are stated from documentation that was not
opened (provenance: recalled; no web access):
- **Python signal handlers** run in the main thread between bytecode instructions, not inside the
  C handler (the signal module documentation). FO-1 steps 2 and 4 depend on this; no other verdict
  does.
- **Exception context.** An exception raised in a `finally` clause, or while another is being
  handled, gets that earlier exception as `__context__`. `raise ... from` sets `__cause__` and
  `__suppress_context__`, but does not clear `__context__` (the language reference: the raise and
  try statements). J-1 (iii) on P-F2 depends on this. A deviation from it yields `undetermined`
  (RFL-4).
- **Tracebacks** keep their frames, and those frames' locals, reachable until released (the data
  model). J-1 (iii) depends on this. A deviation from it yields `undetermined`.

## 11. Attestation details: commands, paths read, scratch, blindness, deviations

**Commands.** Every shell child is listed in order. `<scratch>` is the session scratch directory
the dispatching session assigned, outside the repository; its literal path contains a word covered
by the RTR-7 list, so it is not written here. `<repo>` is `/home/user/crypto-autoresearcher`. All
children are read-only, except `mkdir` of the scratch directory and the scratch outputs noted. No
git write of any kind was made.

1. `wc -l <repo>/AGENTS.md; mkdir -p <scratch>/rt_f5631b && ls -la <scratch>/rt_f5631b`
2. `cd <repo> && git rev-parse HEAD && git status --porcelain=v1 -- experiments/EXP-GFPN-05ff43 coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b | head -50; test -e coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b && echo EXISTS || echo ABSENT`
3. `cd <repo> && sha256sum experiments/EXP-GFPN-05ff43/amendments/v2_addendum_failclosed.yaml experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackclose.yaml experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackfull.yaml experiments/EXP-GFPN-05ff43/amendments/v2_addendum_readbackcover.yaml && ls -la experiments/EXP-GFPN-05ff43/amendments/ experiments/EXP-GFPN-05ff43/dev-evidence/ experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census experiments/EXP-GFPN-05ff43/dev-evidence/readback-census && ls coordination/goals/GOAL-GFPN-380702/archives/`
4. `cd <repo> && ls -la coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-71d070 coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-ddfb69 coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-a01341 coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-0fa03f coordination/goals/GOAL-GFPN-380702/archives/TASK-20260923-4ff597 coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-f1fb0e; sha256sum experiments/EXP-GFPN-05ff43/dev-evidence/readbackclose-census/* experiments/EXP-GFPN-05ff43/dev-evidence/readbackfull-census/* experiments/EXP-GFPN-05ff43/dev-evidence/readback-census/*`
5. `cd <repo> && python3 -B -c '<script 5>' coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-71d070/snapshot-receipt.json coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-ddfb69/snapshot-receipt.json coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-a01341/snapshot-receipt.json`. Script 5 printed only the `path_sha256` maps:
   ```
   import json,sys
   for p in sys.argv[1:]:
       d=json.load(open(p))
       def find(o,path=""):
           if isinstance(o,dict):
               for k,v in o.items():
                   if k=="path_sha256":
                       print(p, path+"/"+k)
                       for kk,vv in (v.items() if isinstance(v,dict) else []):
                           print("   ",vv,kk)
                   else:
                       find(v,path+"/"+k)
           elif isinstance(o,list):
               for i,x in enumerate(o): find(x,path+"[%d]"%i)
       find(d)
   ```
6. `cd <repo> && git cat-file -t dd103455380238ec2f20d17414de687acdcc822a; git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json; git diff --stat dd103455380238ec2f20d17414de687acdcc822a -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'; git diff --stat dd103455380238ec2f20d17414de687acdcc822a HEAD -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'; git status --porcelain=v1 --untracked-files=all -- 'experiments/EXP-GFPN-05ff43/implementation*' 'experiments/EXP-GFPN-05ff43/trial-plan-*.json'; ls -d experiments/EXP-GFPN-05ff43/implementation* experiments/EXP-GFPN-05ff43/trial-plan-*.json`. The `echo` separators and `rc=$?` echoes are omitted here.
7. `cd <repo>/experiments/EXP-GFPN-05ff43 && ls -la implementation-v2 implementation-v2-a1 implementation-v2-r3 && wc -l implementation-v2/*.py implementation-v2-a1/*.py implementation-v2-r3/*.py implementation-v2-r3.md`
8. `cd <repo>/experiments/EXP-GFPN-05ff43 && grep -n "except\|finally:\|signal\.\|atexit\|faulthandler\|threading\|register_at_fork\|excepthook\|addaudithook"` over v2_driver, v2_common, v2_lift, v2_arms, v2_child, v2_scoring, v2_field, v2_verify_independent, a1_driver, a1_health, a1_pari, a1_common, a1_reading, r3_common, r3_run_wrapper, r3_check_run, r3_reg1 and r3_accounting (explicit file paths).
9. `cd <repo>/experiments/EXP-GFPN-05ff43 && grep -n "raw-result.json\|def finish\|finish(ctx\|finish(\b" implementation-v2/*.py implementation-v2-a1/*.py implementation-v2-r3/r3_entry_v2.py implementation-v2-r3/r3_entry_a1.py implementation-v2-r3/r3_resolve.py implementation-v2-r3/r3_common.py implementation-v2-r3/r3_run_wrapper.py | grep -v "^implementation-v2/v2_run_wrapper.py\|^implementation-v2-a1/a1_run_wrapper.py\|a1_devchecks\|a1_toy\|make_trial_plan"`
10. `cd <repo>/experiments/EXP-GFPN-05ff43 && python3 -B -c '<script 10>'`. Script 10 is a plan reader:
    ```
    import json,collections
    for f in ("trial-plan-v2-r3.json","trial-plan-v2-a1-r3.json"):
        d=json.load(open(f))
        print("==",f)
        g=d.get("gate",{})
        print(" gate keys:",sorted(g.keys()))
        print(" gate.regression:",json.dumps(g.get("regression"))[:400])
        print(" blocking_packages:",g.get("blocking_packages"), " addendum_blocking_package:",g.get("addendum_blocking_package"), " v2_blocking_packages:", g.get("v2_blocking_packages"))
        print(" package kinds:",collections.Counter(p["kind"] for p in d["packages"]))
        for p in d["packages"]:
            if p["kind"]=="cells":
                arms=[(c["arm"],c.get("disposition"),c.get("condition")) for c in p["cells"]]
                print("  cells",p["run_id"],"p",p.get("p"),"shape",p.get("shape"),"m",p.get("m"),"requires",p.get("requires"),"prior",[a for a in p.get("driver_args",[]) if "RUN" in a],"arms",arms)
            else:
                print("  ",p["kind"],p["run_id"],"blocking",p.get("blocking"),"gate_required",p.get("gate_required"),"ca1",p.get("controls_a1_gate_required"),"requires",p.get("requires"),"args",p.get("driver_args"))
    ```
11. `cd <repo>/experiments/EXP-GFPN-05ff43 && python3 -B -c '<script 11>'`. Script 11 read the keys of `gate.regression`:
    ```
    import json
    for f in ("trial-plan-v2-r3.json","trial-plan-v2-a1-r3.json"):
        r=json.load(open(f))["gate"]["regression"]
        print(f, sorted(r.keys()))
        print("  exclusion_list_sha256 =", r.get("exclusion_list_sha256"), " candidate_run =", r.get("candidate_run"), " reference_run =", r.get("reference_run"))
    ```
12. `cd <repo>/experiments/EXP-GFPN-05ff43/implementation-v2-r3 && for r in "165,185" "222,240" "292,318" "388,410" "460,492" "562,575"; do echo "=== r3_dv7.py $r"; sed -n "${r}p" r3_dv7.py | cat -n | sed "s/^ *\([0-9]*\)/\1+$(echo $r|cut -d, -f1)-1:/" ; done 2>/dev/null | head -200`
13. `cd <repo>/experiments/EXP-GFPN-05ff43 && grep -n "ctx\.rid\|run_id()\|\.run_dir()\|GFPN_RUN_DIR\|GFPN_V2_PACKAGE\|GFPN_V2_REPLACES\|GFPN_V2_CAP\|GFPN_V2_CACHE\|os\.environ\|EXP_DIR\|RUNS_DIR\|LADDER_PATH\|FIXTURE_N3_JSON\|FIXTURE_N4_JSON\|ARCHIVED_ANCHOR_RUN\|COMPARATOR\|RECEIPT"` over the thirteen command modules; then `grep -n "run_id" implementation-v2/v2_lift.py implementation-v2/v2_verify_independent.py`
14. `python3 --version; sha256sum <scratch>/rt_f5631b/words.txt | cut -d' ' -f1; wc -l < <scratch>/rt_f5631b/words.txt`
15. `cd <scratch>/rt_f5631b && PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B ast_scan.py /home/user/crypto-autoresearcher > ast_scan.out 2>&1; echo "rc=$?"; wc -l ast_scan.out; sed -n '1,80p' ast_scan.out` (rc=0)
16. `sed -n '80,260p' <scratch>/rt_f5631b/ast_scan.out`; then `sed -n '260,412p' <scratch>/rt_f5631b/ast_scan.out`
17. `cd <scratch>/rt_f5631b && PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B rule_eval.py > rule_eval.out 2>&1; echo "rc=$?"; wc -l rule_eval.out; grep -n "FAIL-OPEN" rule_eval.out | head -80` (rc=0)
18. `cd <scratch>/rt_f5631b && grep -n "^## \|R1  Mr3\|R1  Mc \|R1m Mr3" rule_eval.out | sed -n '1,400p' | awk 'length($0)<260' | head -260`. The tool harness persisted this long output to a file in its own session directory outside the repository; that file was not opened (DV-6).
19. `cd <scratch>/rt_f5631b && awk '<summary program>' rule_eval.out | sort > summary.txt; wc -c summary.txt; cut -c1-400 summary.txt | head -30`; then `cut -c1-330 summary.txt | sed -n '31,70p'; sed -n '/KNOWN-ANSWER/,$p' rule_eval.out | cut -c1-230`. The awk program builds one line per `## ` object, of the form `rs/var=verdict[defs]!FO`.
20. `cd <repo> && python3 -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["addendum_sha256"])' coordination/goals/GOAL-GFPN-380702/archives/TASK-20260924-eb2540/ledger-receipt.json`
21. `cd <repo> && wc -l ledger/decisions/DEC-20260924-a789e1.yaml ledger/decisions/DEC-20260924-650068.yaml ledger/decisions/DEC-20260924-1ce186.yaml ledger/corrections/CORR-20260924-217903.yaml ledger/corrections/CORR-20260924-80009d.yaml ledger/corrections/CORR-20260924-b3cd63.yaml`
22. `cd <repo>/experiments/EXP-GFPN-05ff43 && grep -n "run_child\|_run_child_locked"` over the eighteen closure modules `| grep -v '^\S*:[0-9]*:\s*#' | cut -c1-170`
23. `cd <repo>/experiments/EXP-GFPN-05ff43 && grep -n "random\.Random(\|Random("` over v2_driver, v2_common, v2_child, v2_arms, v2_lift, a1_driver, a1_health and a1_pari `| cut -c1-175`
24. `cd <scratch>/rt_f5631b && sha256sum ast_scan.py ast_scan.out rule_eval.py rule_eval.out summary.txt words.txt && wc -l ast_scan.py rule_eval.py && ls -la`
25. `cd <scratch>/rt_f5631b && PYTHONDONTWRITEBYTECODE=1 python3 -B name_check.py words.txt ast_scan.py rule_eval.py name_check.py` (0 hits)
26. `cd <repo> && python3 -B -c '<yaml.safe_load of review-report.yaml; print its keys, verdicts and ids>'`
27. `python3 -B name_check.py words.txt <review-report.yaml>`. It was followed by `grep -n -c` for the inference flag and by a `grep -n -E` for the eight RTR-8 task ids, built from the card's list. The ids are not reproduced here. The count was 0.
28. `sed -n '<two line numbers>p' <review-report.yaml>`. This viewed the two self-check hit lines of this review's own text. One was the scratch path, since replaced by `<scratch>`; the other was the inference flag.
29. `cd <scratch>/rt_f5631b && sha256sum name_check.py && sed -n '/^(1) run_child/,/^(2)/p' ast_scan.out | head -12`
30. Final checks, whose results are given in the return rather than in this file:
    - the appendix append: `cat` of the three scratch scripts into this file;
    - `yaml.safe_load` of review-report.yaml;
    - `name_check.py words.txt` on both deliverables;
    - the RTR-8 id grep on both deliverables;
    - `sha256sum` of both deliverables;
    - `git status --porcelain=v1 --untracked-files=all -- coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b experiments/EXP-GFPN-05ff43`.

The tool reads (Read, and the tool's search) are listed under paths read.

**Paths read in full:**
- `ledger/handoffs/TASK-20260924-f5631b.yaml`
- `agents/red-team.md`
- `AGENTS.md`
- the failclosed and readbackclose drafts
- `readbackclose-census.md`
- implementation-v2: `v2_solver.py`, `v2_check_run.py`, `v2_driver.py`, `v2_common.py`, `v2_child.py`
- implementation-v2-a1: `a1_pari.py`, `a1_health.py`, `a1_driver.py`, `a1_check_run.py`, `a1_common.py`
- implementation-v2-r3: `r3_entry_v2.py`, `r3_entry_a1.py`, `r3_resolve.py`, `r3_run_wrapper.py`,
  `r3_check_run.py`, `r3_common.py`, `r3_reg1.py`
- `ledger/corrections/CORR-20260924-b3cd63.yaml`

**Paths read in part:**
- readbackfull, lines 1-420;
- readbackcover, a heading search and lines 195-394;
- r3_dv7.py and r3_dv12.py, at the ranges above;
- v2_lift.py, via grep;
- both r3 plans, through the JSON reads above;
- DEC-20260924-1ce186, a search and lines 236-285;
- the path_sha256 maps of the 71d070, ddfb69 and a01341 snapshot receipts;
- the single field `addendum_sha256` of the eb2540 ledger receipt.

**Other access:**
- **Parsed by the scan:** every `.py` file of the three trees (ast), and every file of the three
  trees text-searched for the new field names. The eighteen closure modules were parsed in full;
  `v2_solver.py` was also compiled from its source text for `dis`.
- **tools/ and harness/:** file names only, for the guard list.
- **Hashed only:** the drafts and census files of section 1.
- **Line counts only:** DEC-20260924-a789e1, DEC-20260924-650068, CORR-20260924-217903,
  CORR-20260924-80009d and implementation-v2-r3.md.
- **Provided in context by the harness, not opened by a tool call:** the repository's top-level
  session-instructions file.

**Not read:**
- the other amendments;
- trial-plan-v2.json and trial-plan-v2-a1.json;
- the census JSON and script contents;
- the remainder of the decisions and corrections above.

No verdict rests on an unread part (DV-3).

**Scratch files**, all in `<scratch>/rt_f5631b/`, outside the repository:

| file | purpose | sha256 |
|---|---|---|
| `words.txt` | The RTR-7 word list, placed by the dispatching session. It was hashed and read only at run time; its words were never printed. | `c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268` |
| `ast_scan.py` | static ast / dis scan with a guard (appendix A) | `67d10a430ea6791c0555c452bb4a765ccc99f6881c38bde38ddf9afc0aca4fff` |
| `ast_scan.out` | its output | `40969d00c6f8f665549a8d9d6898a2a2ad8193c8e1c7814504fbd00a4a0db405` |
| `rule_eval.py` | the rule evaluator (appendix B) | `5a8bec2aac61b59deac15d7c122bd4490994ca4eed93661d6134bf0d328e4f86` |
| `rule_eval.out` | its output | `a7c19ca91b4d4ddd3a632e2b0d2db09d634dbd6012ff9ba5a00de7c11bdc763a` |
| `summary.txt` | one line per object of `rule_eval.out` | `6ee6df925f7b55c85db8f2cba5b07411357a3d60ddb795876d647bf066db7eed` |
| `name_check.py` | the RTR-7 self-check (appendix C) | `9d0b6e1980f4348528cd6e444ab4cef7f170a69ca0e7a114a378bf77004c7bf6` |
| `name_check.out` | its output on the deliverables | given in the return |

**Blindness.**
- **Not opened (blind_from):** the five blind_from files. These are DEC-20260924-8fa3d4,
  CORR-20260924-7fcbd2, the handoffs TASK-20260924-7e9d3e and TASK-20260924-eb2540, and the
  GOAL-GFPN-380702 goal head.
- **Not opened (withheld by the dispatcher):** TASK-20260924-0c2fdc's card; `batches/`; the eb2540
  archive directory, apart from the one field; `coordination/bus/`; `coordination/events/`; every
  other review directory; commit messages; pull requests and the web.
- **Disclosures:**
  1. The permitted field was seen in full. It has the members `id`, `path`, `sha256`, `status`
     (draft), `approved_by` (None) and `approval_decision` (None), and a note saying that this
     review's RTR-2 (a), the archive's check (1) and the approval act (reserved
     TASK-20260924-64c8fe; RFR-5) read that value.
  2. An `ls` of `coordination/goals/GOAL-GFPN-380702/archives/` listed its task-directory names,
     the eb2540 directory among them. That directory's contents were not listed.
  3. No search traversed a withheld path.
- **Sibling reports read:** none.

**Deviations.**
- **DV-1.** The known-answer control's weakened-RF-1 object (section 2).
- **DV-2.** RTR-2 (a) used two sources, as the dispatching session permitted.
- **DV-3.** Partial reads, listed above.
- **DV-4.** The call graph is name-based. Three `subprocess.run` edges were marked and discounted,
  and two dynamic edges were added by hand: `r3_resolve._call_original` to the frozen solve and
  run_system, captured at install (434-437, 446-449).
- **DV-5.** Interpreter semantics are stated with recalled provenance.
- **DV-6.** The harness persisted one tool output outside the repository and outside scratch. It
  was not opened.

## 12. red_team_report

```yaml
red_team_report:
  id: TASK-20260924-f5631b
  task_id: TASK-20260924-f5631b
  claim_under_review: >-
    The DRAFT AMD-EXP-GFPN-05ff43-20260924-failclosed (sha256 1dec09a9...834c): its fail-closed
    recording, verdict and development-harness rules, on joints J-1..J-6.
  objections: [FO-1 (J-1, (iv) as worded), PB-1 (J-3, definitional), FC-1 and FC-2 (J-4 STOP by construction), OB-1 (premise about RK-3 (b) holds only under Mc), FC-5 (no R-12 route for non-infrastructure FAILs)]
  required_controls: [scratch check of a failing / interrupted recorder-foreign write, r4 REG-1 items on the NOT_EVALUABLE block, evaluator re-run with the r4 source of the requested cap]
  counterexample_or_mutation: FO-1; for variant C, class (C) returncode 97 / 99 (v2_solver.py 196, 208), evaluator R1m
  baseline_comparison: not applicable (a recording / verdict protocol; no algorithmic, cost or success claim)
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges: [uncapped children outside run_child (OB-5), readings of (iv) and PLANNED BASIS OUTCOME left open]
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    On the r3 base and the draft's text, with zero runs: no FAIL-OPEN under (i), (ii), (iii) or (v);
    FO-1 meets (iv) as literally worded, reachable only through documented interpreter behaviour,
    with no argv executed; J-3 breaks only definitionally (PB-1); RF-4 as worded stops DV-18 by
    construction (FC-1, FC-2); J-5 and J-6 hold.
  next_concrete_action: >-
    Run, as a scratch development check with no package, the FO-1 falsification case: install the
    recorder in a scratch process that forks, make the child's recorder-foreign write fail and,
    separately, interrupt it, and record whether any r4 artifact reveals the escaped child and which
    verdict the r4 rules give.
  artifact_paths:
    - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.yaml
    - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260924-f5631b/review-report.md
```

**Review attestation.**
- task_id TASK-20260924-f5631b; role red-team
- joints_owned: J-1, J-2, J-3, J-4, J-5, J-6
- verdicts: J-1 breaks, J-2 holds, J-3 breaks, J-4 breaks, J-5 holds, J-6 holds
- read_sibling_reports: none
- blind_from_not_opened and dispatcher_withheld_not_opened: as above
- paths_read, commands, scratch_files, inference and deviations: as above, and in
  `review-report.yaml`

## Appendix: key scan output (from ast_scan.out)

- **(1) run_child call sites.** The six sites are a1_health:147, a1_pari:96, v2_driver:101,
  v2_driver:166, v2_driver:650 and v2_solver:517. None has an enclosing try or with. The defs are
  at v2_solver:149 and v2_solver:177. There are zero `from v2_solver import` statements.
- **(2) Broad handlers.** a1_pari:122 is in gp_version and r3_common:371/376 are in versions.
  r3_entry_a1:103 and r3_entry_v2:72 are BaseException handlers in main; they re-raise after
  their finally. v2_common:60 is in sh. v2_solver:423, 435 and 450 are in the parsers.
  v2_solver:545 is callgrind_annotate, after 517. v2_solver:206 and 194 are child-side. None
  encloses a run_child call edge.
- **(4) Hook scan.** There are 2 hits: `v2_solver.py:35 import ['signal']` and
  `v2_solver.py:266 os.kill`.
- **(5) dis.** Line 181 is `LOAD_GLOBAL os`, `LOAD_ATTR fork`, `PRECALL`, `CALL`, `STORE_FAST pid`.
  Line 182 is `LOAD_FAST pid`, `LOAD_CONST 0`, `COMPARE_OP ==`, `POP_JUMP_FORWARD_IF_FALSE`.
  Line 183 is `NOP`. run_child 171 is a `CALL`, and its 173-174 finally appears on both exits
  (`RETURN_VALUE` and `RERAISE`).
- **(6) raw-result.json writers.** They are v2_driver:84 (finish), v2_driver:1322 and
  a1_driver:388. None of the new field names appears in the three trees.
- **Guard.** The guard refused 223 names, with no collisions. Its self-test refused an import and
  a launch. The attempt counts were import 0 and launch 0.

## Appendix A: ast_scan.py (verbatim)

- sha256: `67d10a430ea6791c0555c452bb4a765ccc99f6881c38bde38ddf9afc0aca4fff`
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 300 python3 -B ast_scan.py /home/user/crypto-autoresearcher`
- cwd: `<scratch>/rt_f5631b`
- output sha256: `40969d00c6f8f665549a8d9d6898a2a2ad8193c8e1c7814504fbd00a4a0db405`

It reads committed bytes only, so its output can be re-derived.

```python
#!/usr/bin/env python3
"""TASK-20260924-f5631b red-team static scan (scratch; never delivered as code).
Reads source TEXT of the frozen and r3 trees, parses it with ast, compiles v2_solver's text in this process for dis.
Imports NO module of the scanned trees: an audit hook refuses any import whose top-level name is a .py stem of the
scanned trees, tools/ or harness/, and every process-launch event. Writes nothing.
usage: python3 -B ast_scan.py <repo-root>
"""
import ast
import dis
import hashlib
import os
import sys

REPO = os.path.abspath(sys.argv[1])
EXP = os.path.join(REPO, "experiments", "EXP-GFPN-05ff43")
TREES = ["implementation-v2", "implementation-v2-a1", "implementation-v2-r3"]

# ---------------------------------------------------------------- guard (installed before any scanned file is read)
stems = set()
for base in [os.path.join(EXP, t) for t in TREES] + [os.path.join(REPO, "tools"), os.path.join(REPO, "harness")]:
    for dp, _dn, fn in os.walk(base):
        for f in fn:
            if f.endswith(".py"):
                stems.add(f[:-3])
collide = sorted(s for s in stems if s in sys.stdlib_module_names or s in sys.modules)
REFUSE_IMPORT = stems - set(collide)
LAUNCH = ("subprocess.Popen", "os.system", "os.exec", "os.posix_spawn", "os.spawn", "os.fork", "os.forkpty", "pty.spawn",
          "os.startfile")
COUNT = {"import": 0, "launch": 0}
SELFTEST = [True]


def hook(event, args):
    if event == "import":
        top = str(args[0]).split(".")[0]
        if top in REFUSE_IMPORT:
            if not SELFTEST[0]:
                COUNT["import"] += 1
            raise ImportError("guard: refused import of scanned module %s" % top)
    elif event in LAUNCH:
        if not SELFTEST[0]:
            COUNT["launch"] += 1
        raise RuntimeError("guard: refused %s" % event)


sys.addaudithook(hook)
selftest = []
for ev, a in (("import", ("v2_solver", None, None, None, None)), ("subprocess.Popen", ("x", [], None, None))):
    try:
        sys.audit(ev, *a)
        selftest.append((ev, "NOT refused"))
    except (ImportError, RuntimeError):
        selftest.append((ev, "refused"))
SELFTEST[0] = False
print("GUARD refused-import names:", len(REFUSE_IMPORT), "sha256(sorted names):",
      hashlib.sha256("\n".join(sorted(REFUSE_IMPORT)).encode()).hexdigest(), "stdlib/loaded collisions (not refused):", collide)
print("GUARD self-test:", selftest)

CLOSURE = {  # the r3 entries' import closure as the successor/close census list it
    "implementation-v2-a1": ["a1_common", "a1_driver", "a1_health", "a1_pari", "a1_reading"],
    "implementation-v2-r3": ["r3_common", "r3_entry_a1", "r3_entry_v2", "r3_resolve"],
    "implementation-v2": ["v2_arms", "v2_child", "v2_common", "v2_driver", "v2_field", "v2_lift", "v2_scoring", "v2_solver",
                          "v2_verify_independent"],
}
SRC, TREE, SHA = {}, {}, {}
for t, mods in CLOSURE.items():
    for m in mods:
        p = os.path.join(EXP, t, m + ".py")
        b = open(p, "rb").read()
        SHA[m] = hashlib.sha256(b).hexdigest()
        SRC[m] = b.decode("utf-8")
        tr = ast.parse(SRC[m], filename=p)
        for node in ast.walk(tr):
            for ch in ast.iter_child_nodes(node):
                ch._parent = node
        TREE[m] = tr
print("\nCLOSURE files sha256:")
for m in sorted(SHA):
    print("  %-24s %s" % (m, SHA[m]))

FUNC_T = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)


def encl_func(node):
    n = getattr(node, "_parent", None)
    names = []
    while n is not None:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(n.name)
        n = getattr(n, "_parent", None)
    return ".".join(reversed(names)) or "<module>"


def handler_desc(h):
    t = "bare" if h.type is None else ast.unparse(h.type)
    rer = any(isinstance(x, ast.Raise) for x in ast.walk(h))
    return "%s@%d%s" % (t, h.lineno, " (re-raises)" if rer else " (no raise in handler)")


def try_context(node):
    """Try/With nodes enclosing node inside its function, with the region node lies in."""
    out = []
    child, n = node, getattr(node, "_parent", None)
    while n is not None and not isinstance(n, FUNC_T) and not isinstance(n, ast.Module):
        if isinstance(n, ast.Try):
            if any(child is x for x in n.body):
                reg = "body"
            elif any(child is x for x in n.handlers):
                reg = "handler"
            elif any(child is x for x in n.orelse):
                reg = "else"
            else:
                reg = "finally"
            out.append("try@%d[%s] handlers=%s finally=%s" % (n.lineno, reg, [handler_desc(h) for h in n.handlers],
                                                              bool(n.finalbody)))
        if isinstance(n, (ast.With, ast.AsyncWith)):
            out.append("with@%d items=%s" % (n.lineno, [ast.unparse(i.context_expr)[:60] for i in n.items]))
        child, n = n, getattr(n, "_parent", None)
    return out


def call_name(c):
    f = c.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


# ---------------------------------------------------------------- (1) run_child call sites, defs, from-imports
print("\n(1) run_child call sites in the closure (Call with func Name/Attribute 'run_child'):")
for m, tr in sorted(TREE.items()):
    for c in ast.walk(tr):
        if isinstance(c, ast.Call) and call_name(c) == "run_child":
            print("  %s:%d in %s via %s ; context %s" % (m, c.lineno, encl_func(c), ast.unparse(c.func), try_context(c) or "none"))
print("defs named run_child / _run_child_locked (all closure files):")
for m, tr in sorted(TREE.items()):
    for d in ast.walk(tr):
        if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)) and d.name in ("run_child", "_run_child_locked"):
            print("  %s:%d def %s (enclosing %s)" % (m, d.lineno, d.name, encl_func(d)))
print("`from v2_solver import` anywhere in the three trees:")
hits = 0
for t in TREES:
    for dp, _dn, fn in os.walk(os.path.join(EXP, t)):
        for f in sorted(fn):
            if f.endswith(".py"):
                tr = ast.parse(open(os.path.join(dp, f), encoding="utf-8").read())
                for n in ast.walk(tr):
                    if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "v2_solver":
                        hits += 1
                        print("  %s/%s:%d" % (t, f, n.lineno))
print("  total:", hits)

# ---------------------------------------------------------------- (2) every exception handler in the closure
print("\n(2) every try/except handler in the closure (file:line, enclosing function, handlers):")
broad = []
for m, tr in sorted(TREE.items()):
    for n in ast.walk(tr):
        if isinstance(n, ast.Try) and n.handlers:
            hd = [handler_desc(h) for h in n.handlers]
            print("  %s:%d in %s: %s" % (m, n.lineno, encl_func(n), hd))
            for h in n.handlers:
                t = "bare" if h.type is None else ast.unparse(h.type)
                if t in ("bare", "BaseException", "Exception") or "BaseException" in t or "KeyboardInterrupt" in t:
                    broad.append("%s:%d %s in %s" % (m, h.lineno, handler_desc(h), encl_func(n)))
print("broad handlers (bare / BaseException / Exception / KeyboardInterrupt):")
for b in broad:
    print("  ", b)

# ---------------------------------------------------------------- (3) upward call paths from run_child (name-based, conservative)
defs = {}   # name -> list of (module, qualname, node)
for m, tr in TREE.items():
    for d in ast.walk(tr):
        if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.setdefault(d.name, []).append((m, encl_func(d) + ("." if encl_func(d) != "<module>" else "") + d.name, d))
callers = {}  # callee name -> list of (module, caller qualname, lineno, context)
for m, tr in TREE.items():
    for c in ast.walk(tr):
        if isinstance(c, ast.Call):
            nm = call_name(c)
            if nm:
                callers.setdefault(nm, []).append((m, encl_func(c), c.lineno, try_context(c)))
# dynamic edge recorded by hand: r3_resolve._call_original calls `original`, which is v2_driver.solve (S-1) or
# a1_health.run_system (S-2) captured at install (r3_resolve.py 117-118, 429-450).
DYN = {"solve": [("r3_resolve", "_call_original", 118, ["dynamic: original(*args) captured at install 434-437"])],
       "run_system": [("r3_resolve", "_call_original", 118, ["dynamic: original(*args) captured at install 446-449"])]}
print("\n(3) upward call paths from run_child (name-based; every call edge with its try/with context):")
seen, frontier = set(), ["run_child"]
edge_ctx = []
while frontier:
    name = frontier.pop(0)
    if name in seen:
        continue
    seen.add(name)
    for (m, q, ln, ctx) in callers.get(name, []) + DYN.get(name, []):
        leaf = q.split(".")[-1]
        edge_ctx.append((name, m, q, ln, ctx))
        if leaf not in seen and leaf != "<module>":
            frontier.append(leaf)
for (callee, m, q, ln, ctx) in edge_ctx:
    mark = ""
    if any("try@" in x and "[body]" in x and "no raise in handler" in x for x in ctx):
        mark = "  <== inside a try BODY with a non-raising handler"
    print("  %-18s <- %s:%d %s ; %s%s" % (callee, m, ln, q, ctx or "no try/with", mark))
print("functions reached upward:", sorted(seen))

# ---------------------------------------------------------------- (4) asynchronous-exception and process-hook installers
print("\n(4) signal / faulthandler / atexit / threading / at-fork / audit / trace hooks in the three trees:")
ATTRS = {("signal", a) for a in ("signal", "setitimer", "alarm", "set_wakeup_fd", "pthread_kill", "siginterrupt", "raise_signal")}
ATTRS |= {("faulthandler", a) for a in ("enable", "register", "dump_traceback_later")}
ATTRS |= {("atexit", "register"), ("threading", "Thread"), ("threading", "Timer"), ("_thread", "start_new_thread"),
          ("os", "register_at_fork"), ("os", "kill"), ("os", "killpg"), ("sys", "addaudithook"), ("sys", "settrace"),
          ("sys", "setprofile"), ("threading", "excepthook"), ("sys", "excepthook"), ("signal", "SIGINT")}
MODS = {"signal", "faulthandler", "atexit", "threading", "_thread", "multiprocessing", "concurrent"}
nh = 0
for t in TREES:
    for dp, _dn, fn in os.walk(os.path.join(EXP, t)):
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            tr = ast.parse(open(os.path.join(dp, f), encoding="utf-8").read())
            for n in ast.walk(tr):
                hit = None
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    names = [a.name for a in n.names] if isinstance(n, ast.Import) else [n.module or ""]
                    if any(x.split(".")[0] in MODS for x in names):
                        hit = "import %s" % names
                elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and (n.value.id, n.attr) in ATTRS:
                    hit = "%s.%s" % (n.value.id, n.attr)
                if hit:
                    nh += 1
                    print("  %s/%s:%d %s" % (t, f, n.lineno, hit))
print("  total hits:", nh)

# ---------------------------------------------------------------- (5) bytecode of the frozen run_child / _run_child_locked
print("\n(5) dis of v2_solver.run_child (lines 149-175) and _run_child_locked (lines 177-183, 219-237), compiled from source text:")
code = compile(SRC["v2_solver"], os.path.join(EXP, "implementation-v2", "v2_solver.py"), "exec")
objs = {c.co_name: c for c in code.co_consts if hasattr(c, "co_code")}
for name, rng in (("run_child", (166, 175)), ("_run_child_locked", (177, 183)), ("_run_child_locked", (219, 237))):
    c = objs[name]
    print("  %s co_firstlineno=%d nlocals=%d varnames=%s cellvars=%s" % (name, c.co_firstlineno, c.co_nlocals, c.co_varnames[:12],
                                                                      c.co_cellvars))
    for ins in dis.get_instructions(c):
        ln = ins.positions.lineno if ins.positions else None
        if ln is not None and rng[0] <= ln <= rng[1]:
            print("    L%-4s %-24s %s" % (ln, ins.opname, "" if ins.argrepr is None else ins.argrepr))
    et = getattr(c, "co_exceptiontable", b"")
    print("    exception table bytes:", len(et))

# ---------------------------------------------------------------- (6) raw-result.json writers and new-field names
print("\n(6) string constant 'raw-result.json' in the closure, with the enclosing function (writers and readers):")
for m, tr in sorted(TREE.items()):
    for n in ast.walk(tr):
        if isinstance(n, ast.Constant) and n.value == "raw-result.json":
            par = getattr(n, "_parent", None)
            while par is not None and not isinstance(par, ast.Call):
                par = getattr(par, "_parent", None)
            outer = par
            while outer is not None and isinstance(getattr(outer, "_parent", None), ast.Call):
                outer = outer._parent
            print("  %s:%d in %s: %s" % (m, n.lineno, encl_func(n), ast.unparse(outer)[:110] if outer is not None else "?"))
print("\nnames raw_result_writer / recorder-foreign / recorder_foreign / undetermined / launch_records / child_created / "
      "pair_read_by_parent / frame_inspection in the three trees (text):")
for t in TREES:
    for dp, _dn, fn in os.walk(os.path.join(EXP, t)):
        for f in sorted(fn):
            p = os.path.join(dp, f)
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            for w in ("raw_result_writer", "recorder-foreign", "recorder_foreign", "undetermined", "launch_records",
                      "child_created", "pair_read_by_parent", "frame_inspection"):
                k = txt.count(w)
                if k:
                    print("  %s/%s: %s x%d" % (t, f, w, k))
print("\nGUARD attempt counts in this run: import %d launch %d" % (COUNT["import"], COUNT["launch"]))
```

## Appendix B: rule_eval.py (verbatim)

- sha256: `5a8bec2aac61b59deac15d7c122bd4490994ca4eed93661d6134bf0d328e4f86`
- argv: `PYTHONDONTWRITEBYTECODE=1 timeout 120 python3 -B rule_eval.py`
- cwd: `<scratch>/rt_f5631b`
- output sha256 (`rule_eval.out`): `a7c19ca91b4d4ddd3a632e2b0d2db09d634dbd6012ff9ba5a00de7c11bdc763a`

The script reads no file and imports only `itertools`. Its output therefore depends only on its own
text, and re-running it reproduces `rule_eval.out`. The path and outcome facts are hand-read, with
the frozen lines cited in the dictionary keys. The rule functions encode the texts under test.

```python
#!/usr/bin/env python3
"""TASK-20260924-f5631b red-team fail-open method (scratch). Pure data + rule functions: it reads no file and imports
no module of any scanned tree. The PATH FACTS below are hand-read from the frozen code (lines cited per object) and
from the close census path table (readbackclose-census.md 190-206, 377-383, 476-492). The RULE FUNCTIONS encode the
texts under test:
  R0  = readbackclose AS WORDED: RK-1 (a)/(b) child_created; RK-3 (b) PASS / PASS_ZL.
  R1  = failclosed draft: RF-1 (a) three-valued child_created; RF-0 (b) raw_result_writer; RF-2 PASS_ZL; RF-3 (a) PASS.
  R1w = R1 with RF-1 WEAKENED to "false whenever no pid is found" (the J-5 mutation).
  R1m = R1 with class (C) additionally requiring returncode 97 ('ERR setrlimit' report) or 99 ('' report), the frozen
        child's own pre-exec exits (v2_solver.py 196, 208): the cheapest mutation examined for FO-1.
Each rule set is evaluated under two manifest variants of the requested cap read by v2_check_run.py 64, 68-70:
  Mr3  = the r3 base: child_rlimit_as_requested_bytes = raw-result.json envelope.cap_bytes (r3_run_wrapper.py 550);
         a wrapper-written raw-result.json (r3_run_wrapper.py 500) has no envelope, so the requested cap is None.
  Mc   = an r4 wrapper that records the plan cap independently of raw-result.json.
FAIL-OPEN = verdict PASS or PASS_ZL while any of the draft's definitions (i)-(v) holds on the TRUTH facts.
"""
import itertools

CAP = 10737418240
OTHER = {"name": "B-other", "child": True, "p227": True, "fate": "return", "key": True, "report": "OK", "rc": 0,
         "pair": (CAP, CAP), "frames": [], "ctx_frames": [], "rec_bound": True}


def L(**kw):
    d = {"child": False, "p227": False, "fate": "return", "key": False, "report": None, "rc": None, "pair": None,
         "frames": [], "ctx_frames": [], "rec_bound": True, "chain_len": 1}
    d.update(kw)
    return d


# ---------------------------------------------------------------- launch paths (v2_solver.py lines; census md 190-206)
# frames: (_run_child_locked tb_lineno, pid bound?) on the traceback of the exception LEAVING run_child;
# ctx_frames: the same on its __context__ exception (P-F2).
PATHS = {
    "P-1..4 refusal before fork (153-169)": L(),
    "P-5a raise before 171 (rec bound)": L(fate="raise"),
    "P-5a' raise at 152 (rec unbound; O-1)": L(fate="raise", rec_bound=False),
    "P-5b raise at 178/179/180": L(fate="raise", frames=[(178, False)]),
    "P-5b' os.fork failing at 181 (no child)": L(fate="raise", frames=[(181, False)]),
    "P-6 ERR setrlimit (193-196; 220-225)": L(child=True, key=True, report="ERR", rc=97),
    "P-7 empty report (186-191, 206-208; 220-225)": L(child=True, key=True, report="", rc=99),
    "P-8 soft != cap (226-232)": L(child=True, p227=True, key=True, report="OK", rc=98, pair=(CAP - 1, CAP - 1)),
    "P-9 hard-only mismatch, return via 308": L(child=True, p227=True, key=True, report="OK", rc=98, pair=(CAP, CAP - 1)),
    "P-10..13 normal (284-308)": L(child=True, p227=True, key=True, report="OK", rc=0, pair=(CAP, CAP)),
    "P-14a raise 182-220 (pid bound, key missing)": L(child=True, fate="raise", frames=[(214, True)]),
    "P-14b raise 221-227 before the pair": L(child=True, fate="raise", key=True, report="OK", frames=[(226, True)]),
    "P-14c raise after 227 (230/236/244/281)": L(child=True, p227=True, fate="raise", key=True, report="OK",
                                                pair=(CAP, CAP), frames=[(236, True)]),
    "P-16 raise AT 181 after fork, pid unbound": L(child=True, fate="raise", frames=[(181, False)]),
    "P-F1 raise in run_child after _run_child_locked returned (171/174)": L(child=True, p227=True, fate="raise", key=True,
                                                                          report="OK", pair=(CAP, CAP), frames=[]),
    "P-F2 after P-5b": L(fate="raise", frames=[], ctx_frames=[(178, False)], chain_len=2),
    "P-F2 after P-16": L(child=True, fate="raise", frames=[], ctx_frames=[(181, False)], chain_len=2),
    "P-F2 after P-14a": L(child=True, fate="raise", frames=[], ctx_frames=[(214, True)], chain_len=2),
    "P-F2 after P-14b": L(child=True, fate="raise", key=True, report="OK", frames=[], ctx_frames=[(226, True)], chain_len=2),
    "P-F2 after P-14c": L(child=True, p227=True, fate="raise", key=True, report="OK", pair=(CAP, CAP), frames=[],
                          ctx_frames=[(236, True)], chain_len=2),
    "chain longer than 16 (any raise after fork)": L(child=True, fate="raise", frames=[], ctx_frames=[], chain_len=17),
}


# ---------------------------------------------------------------- rules: child_created
def rk1_as_worded(l):
    """RK-1 (a) on return: key presence. RK-1 (b) on raise: rec key OR a _run_child_locked frame ON THE TRACEBACK
    (of the raised exception) holding pid > 0; false otherwise; no chain walk."""
    if l["fate"] == "return":
        return l["key"]
    return bool(l["key"] and l["rec_bound"]) or any(pid for (_ln, pid) in l["frames"])


def rf1(l):
    """RF-1 (a): chain walk over __context__/__cause__ (<= 16), three-valued."""
    if l["fate"] == "return":
        return l["key"]                                  # RK-1 (a) unchanged
    if l["chain_len"] > 16:
        return "undetermined"
    allf = l["frames"] + l["ctx_frames"]
    if (l["key"] and l["rec_bound"]) or any(pid for (_ln, pid) in allf):
        return True
    if (not l["rec_bound"] or not l["key"]) and all(ln < 181 and not pid for (ln, pid) in allf):
        return False
    return "undetermined"


def rf1_weak(l):
    """J-5 mutation: 'false whenever no pid is found' (no undetermined)."""
    if l["fate"] == "return":
        return l["key"]
    allf = l["frames"] + l["ctx_frames"]
    if (l["key"] and l["rec_bound"]) or any(pid for (_ln, pid) in allf):
        return True
    return False


def record(l, cc_rule):
    pair = l["pair"] if (l["p227"] and l["rec_bound"]) else None      # pair copied from rec (RK-1 (a)/(b), RK-1 (c))
    return {"child_created": cc_rule(l), "raised": l["fate"] == "raise", "pair": pair, "pair_read": pair is not None,
            "report": l["report"], "rc": l["rc"]}


# ---------------------------------------------------------------- package model
def package(kind, launches, raw_writer, zero_launch_ok=True, gate=False, foreign_file=False, foreign_record=False,
            other_frozen_items=(), r4_items=(), recorder_gap=False, missing_records=()):
    """missing_records: launches that happened (truth) but have NO launch record (recording failure)."""
    return {"kind": kind, "launches": launches, "raw_writer": raw_writer, "gate": gate, "foreign_file": foreign_file,
            "foreign_record": foreign_record, "other_frozen_items": list(other_frozen_items), "r4_items": list(r4_items),
            "recorder_gap": recorder_gap, "missing": list(missing_records)}


def frozen_items(pkg, recs, variant):
    """v2_check_run.py 62-70 as the manifest the wrapper builds would feed it."""
    items = list(pkg["other_frozen_items"])
    if pkg["kind"] == "aggregate":
        return items                                      # 65: exempt
    pairs = [r["pair"] for r in recs if r["pair"] is not None]
    if pkg["raw_writer"] == "driver":                     # RB-2 (a): a lost launch's pair survives only in driver raw
        pairs += [l["pair"] for l in pkg["missing"] if l["pair"]]
    req = CAP if (variant == "Mc" or pkg["raw_writer"] == "driver") else None
    if not pairs:
        items.append("66-67 no child RLIMIT_AS read-back recorded")
    for p in sorted(set(pairs)):
        if p[0] != req or p[1] != req:
            items.append("68-70 read-back %s != requested %s" % (p, req))
    return items


def rk3b(pkg, recs, variant):
    fi = frozen_items(pkg, recs, variant)
    r4ok = not pkg["r4_items"]
    if not fi and r4ok:
        return "PASS", fi
    if (not pkg["gate"] and pkg["kind"] != "controls_a1" and not recs and not pkg["missing"] and not pkg["recorder_gap"]
            and fi == ["66-67 no child RLIMIT_AS read-back recorded"] and r4ok):
        return "PASS_ZL", fi
    return "FAIL", fi


def positive_class(r, mut_rc=False):
    if r["child_created"] is False and not r["raised"]:
        return "A"
    if r["child_created"] is True and not r["raised"] and r["pair_read"]:
        return "B"
    if (r["child_created"] is True and not r["raised"] and not r["pair_read"] and r["report"] in ("", "ERR")
            and r["rc"] is not None):
        if mut_rc and not ((r["report"] == "ERR" and r["rc"] == 97) or (r["report"] == "" and r["rc"] == 99)):
            return None
        return "C"
    return None


def verdict(ruleset, pkg, variant):
    cc = {"R0": rk1_as_worded, "R1": rf1, "R1w": rf1_weak, "R1m": rf1}[ruleset]
    recs = [record(l, cc) for l in pkg["launches"]]
    base, fi = rk3b(pkg, recs, variant)
    if ruleset == "R0":
        return base, recs, fi
    rrw = pkg["raw_writer"]
    undet = any(r["child_created"] == "undetermined" for r in recs) or rrw == "undetermined"
    if base == "PASS":
        ok = (all(positive_class(r, ruleset == "R1m") for r in recs) and rrw == "driver" and not pkg["foreign_file"]
              and not pkg["recorder_gap"] and not undet)
        return ("PASS" if ok else "FAIL"), recs, fi
    if base == "PASS_ZL":
        ok = rrw == "driver" and pkg["kind"] in ("cells", "fixture4") and not pkg["foreign_file"]
        return ("PASS_ZL" if ok else "FAIL"), recs, fi
    return "FAIL", recs, fi


def definitions(pkg, recs):
    """The draft's FAIL-OPEN conditions (i)-(v), on TRUTH facts."""
    hit = []
    for l, r in zip(pkg["launches"], recs):
        if l["p227"] and r["pair"] is None:
            hit.append("(i)")
        may_exec = (l["child"] or r["child_created"] == "undetermined") and positive_class(r) not in ("A", "C")
        if may_exec and r["pair"] != (CAP, CAP):
            hit.append("(ii)")
        if l["child"] and r["child_created"] is False:
            hit.append("(iii)")
    for l in pkg["missing"]:
        if l["p227"]:
            hit.append("(i)")
        if pkg["raw_writer"] != "driver":
            hit.append("(ii)")
    if pkg["foreign_record"] and not pkg["foreign_file"]:
        hit.append("(iv)")
    if pkg["raw_writer"] == "wrapper":
        hit.append("(v)")
    return sorted(set(hit))


def evaluate(name, pkg, rulesets=("R0", "R1", "R1w", "R1m")):
    rows = []
    for rs, var in itertools.product(rulesets, ("Mr3", "Mc")):
        v, recs, fi = verdict(rs, pkg, var)
        d = definitions(pkg, recs)
        fo = v in ("PASS", "PASS_ZL") and bool(d)
        cc = [r["child_created"] for r in recs]
        rows.append((rs, var, v, cc, d, "FAIL-OPEN" if fo else ("record-level only (verdict FAIL)" if d else "-"), fi))
    print("\n## %s" % name)
    for rs, var, v, cc, d, fo, fi in rows:
        print("  %-3s %-3s verdict=%-7s child_created=%s defs=%s -> %s ; frozen items=%s" % (rs, var, v, cc, d, fo, fi))
    return rows


def raise_pkg(path, k_other):
    """A launch that RAISES out of run_child ends the frozen driver (no frozen handler; the r3/r4 entry re-raises):
    raw-result.json is wrapper-written (r3_run_wrapper.py 491-505)."""
    ls = [OTHER] * k_other + [path]
    return package("cells", ls, "wrapper" if path["fate"] == "raise" else "driver")


RESULTS = {}
print("RULE EVALUATION -- every launch path embedded in a cells package, with k other class-(B) launches (pair = cap)")
for name, path in PATHS.items():
    for k in (0, 1):
        RESULTS[(name, k)] = evaluate("%s | k_other=%d" % (name, k), raise_pkg(path, k))

print("\n\nPACKAGE-LEVEL OUTCOMES")
W1 = package("cells", [], "wrapper")
RESULTS["W-1"] = evaluate("W-1 driver exits before any launch; wrapper-written raw (482-509)", W1)
W2 = package("cells", [], "wrapper", r4_items=["r3_check_run 167", "279", "305", "308"])
RESULTS["W-2"] = evaluate("W-2 entry refuses before any command", W2)
RESULTS["Z-C5"] = evaluate("Z-C5 cells m=5, zero launch, completed_valid or failed/resource_exhaustion (1101-1102)",
                           package("cells", [], "driver"))
RESULTS["Z-F4"] = evaluate("Z-F4 fixture4 refused before any build (538-541)", package("fixture4", [], "driver"))
RESULTS["Z-G12"] = evaluate("Z-G12 fixture gate refused (298-307)", package("fixture", [], "driver", gate=True))
RESULTS["AGG"] = evaluate("aggregate (no launch; kind exempt at 65)", package("aggregate", [], "driver"))
A_ = L()
C_ = L(child=True, key=True, report="ERR", rc=97)
C0 = L(child=True, key=True, report="", rc=99)
RESULTS["ALL-A"] = evaluate("cells, every launch refused before fork (class A only; driver raw)",
                            package("cells", [A_, A_], "driver"))
RESULTS["ALL-C"] = evaluate("cells/build, every created child without a pair (class C only; driver raw)",
                            package("cells", [C_, C0], "driver"))
RESULTS["A+B"] = evaluate("normal outcome with a class (A) refusal and a class (B) child", package("cells", [A_, OTHER], "driver"))
RESULTS["C+B"] = evaluate("normal outcome with a class (C) child and a class (B) child", package("cells", [C0, OTHER], "driver"))
P14C = PATHS["P-14c raise after 227 (230/236/244/281)"]
RESULTS["DIED227"] = evaluate("driver died after 227 (P-14c at 236 / 281), its only launch, raise-frame record carries the pair",
                              package("cells", [P14C], "wrapper"))
print("\n\nFOREIGN-PROCESS (P-C) OBJECTS: parent-side record + foreign-process facts")
PC_C = L(child=True, key=True, report="", rc=-2)          # escape before 183: parent reads '' at EOF; child exits by SIGINT
PC_B = L(child=True, p227=True, key=True, report="OK", rc=-2, pair=(CAP, CAP))   # escape at 207-208 after OK at 198-199
for nm, lp in (("P-C before 183", PC_C), ("P-C after OK (206-208)", PC_B)):
    RESULTS[nm + " foreign file written"] = evaluate(nm + ", foreign file WRITTEN (RF-1 (b))",
                                                     package("cells", [OTHER, lp], "driver", foreign_file=True, foreign_record=True))
    RESULTS[nm + " foreign write failed, entry record written"] = evaluate(
        nm + ", foreign-file write FAILED/interrupted; the entry's finally wrote pari-stack.json in the child (r3_entry 75-77)",
        package("cells", [OTHER, lp], "driver", foreign_file=False, foreign_record=True))
    RESULTS[nm + " killed before any write"] = evaluate(nm + ", child killed before any write (nothing written)",
                                                        package("cells", [OTHER, lp], "driver", foreign_file=False,
                                                                foreign_record=False))
print("\n\nRECORDER FAILURE IN THE INSTALLING PROCESS")
RESULTS["RECFAIL raised"] = evaluate("recorder write raises after the frozen call returned (class B call lost); exception ends the driver",
                                     package("cells", [OTHER], "wrapper", missing_records=[OTHER]))
RESULTS["RECFAIL flagged"] = evaluate("recording failure flagged SE-2 (4) and persisted; driver finished",
                                      package("cells", [OTHER], "driver", r4_items=["consistency flag (RL-1 (d))"],
                                              missing_records=[OTHER]))

# ---------------------------------------------------------------- known-answer control summary (J-5)
print("\n\nKNOWN-ANSWER CONTROL (J-5) -- what the method reports on the named objects")
def flags(key, rs, var):
    for row in RESULTS[key]:
        if row[0] == rs and row[1] == var:
            return row
for key in (("P-16 raise AT 181 after fork, pid unbound", 1), ("P-F2 after P-14a", 1), ("P-16 raise AT 181 after fork, pid unbound", 0),
            ("P-F2 after P-14a", 0), "W-1"):
    for rs in ("R0", "R1w", "R1"):
        for var in ("Mr3", "Mc"):
            r = flags(key, rs, var)
            print("  %-55s %-3s %-3s verdict=%-7s child_created=%s defs=%s -> %s" % (str(key), rs, var, r[2], r[3], r[4], r[5]))
```

## Appendix C: name_check.py (verbatim; the RTR-7 self-check)

- sha256: `9d0b6e1980f4348528cd6e444ab4cef7f170a69ca0e7a114a378bf77004c7bf6`
- argv: `PYTHONDONTWRITEBYTECODE=1 python3 -B name_check.py words.txt <file> ...`
- cwd: `<scratch>/rt_f5631b`
- The word list's sha256 is
  `c78adb55d1f7061c477d022b8a62c01ebda242aa9a883f1ddba08bb7fc18a268`, with 16 entries. Its words
  are never printed or recorded.
- The hit counts on the two deliverables are given in the return. Every hit in each file is
  intended to be the inference block's prohibition flag.

```python
#!/usr/bin/env python3
"""TASK-20260924-f5631b RTR-7 self-check (scratch). Reads the word list at run time from argv[1] and reports, per file,
the number of case-insensitive substring hits and the line numbers that carry one. It never prints a word.
usage: python3 -B name_check.py <word-list> <file> [<file> ...]
"""
import hashlib
import sys

wl = open(sys.argv[1], "rb").read()
words = [w.strip().lower() for w in wl.decode("utf-8", "replace").splitlines() if w.strip()]
print("word list sha256 %s ; %d entries" % (hashlib.sha256(wl).hexdigest(), len(words)))
total = 0
for path in sys.argv[2:]:
    n, lines = 0, []
    for i, line in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        low = line.lower()
        k = sum(low.count(w) for w in words)
        if k:
            n += k
            lines.append(i)
    total += n
    print("%s: hits %d ; lines %s" % (path, n, lines))
print("total hits %d" % total)
```
